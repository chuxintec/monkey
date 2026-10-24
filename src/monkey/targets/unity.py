"""Python plans and assembles a native Unity Editor import candidate."""
from importlib.resources import files
from pathlib import Path
import uuid
from .. import __version__
from ..io import safe, inside, read, load, sha, encoded, new_output, finish, write_json, diagnostic, stage_document, stage_bytes, stage_manifest
from ..sources.compiled import fail

PROFILE = 'unity-6000.6.2f1-ugui'


def guid(namespace, identity):
    return uuid.uuid5(uuid.NAMESPACE_URL, 'monkey/'+namespace+'/'+identity).hex


def widget_geometry_matches(widget, node, parent):
    if parent is None:
        return False
    left,bottom,right,top=widget['margins']
    size=[parent['size'][0]-left-right,parent['size'][1]-bottom-top]
    position=[left+node['anchor'][0]*size[0]-parent['anchor'][0]*parent['size'][0],
              bottom+node['anchor'][1]*size[1]-parent['anchor'][1]*parent['size'][1]]
    return (all(abs(a-b)<.001 for a,b in zip(size,node['size'])) and
            all(abs(a-b)<.001 for a,b in zip(position,node['position'])))


def layout_issues(layout,children):
    issues=[]
    if layout['layoutType']not in(1,2,3)or layout['resize']not in(0,1,2)or any(v!=int(v)for v in layout['padding']):
        issues.append(('LAYOUT_SUBSET_UNSUPPORTED','Native linear/flow layout requires known modes and integer padding'))
    if layout['layoutType']in(1,2)and any(any(v<0 for v in n['scale'][:2])for n in children):
        issues.append(('LAYOUT_NEGATIVE_SCALE_PENDING','Negative-scale linear pivots need a separate native bounds contract'))
    if layout['layoutType']==3 and(layout['startAxis']not in(0,1)or layout.get('constraint',0)not in(0,1,2)or type(layout.get('constraintCount',2))is not int or layout.get('constraintCount',2)<1):
        issues.append(('GRID_SUBSET_UNSUPPORTED','Unknown flow axis or row/column constraint'))
    if layout['resize']==2 and layout.get('affectedByScale')and any(0 in n['scale'][:2]for n in children):
        issues.append(('LAYOUT_ZERO_SCALE_PENDING','Child resizing cannot divide by a zero effective scale'))
    return issues


def grid_native_extent(layout,parent,children):
    import math
    children=[n for n in children if n['active']]
    if not children:return None,'EMPTY_LAYOUT_HANDOFF'
    if any(n['scale'][:2]!=[1,1] for n in children):return None,'GRID_SCALED_CHILD_HANDOFF'
    width,height=children[0]['size'];spacing_x,spacing_y=layout['spacingXY']
    if width<=0 or height<=0 or width+spacing_x<=0:return None,'GRID_CELL_GEOMETRY_HANDOFF'
    left,bottom,right,top=layout['padding']
    columns=max(1,math.floor((parent['size'][0]-left-right+spacing_x+.001)/(width+spacing_x)))
    rows=math.ceil(len(children)/columns)
    extent=bottom+top+height*rows+spacing_y*(rows-1)
    if abs(extent-parent['size'][1])>.001:return None,'GRID_CACHED_CONTAINER_HANDOFF'
    return extent,None


def linear_container_matches(layout, parent, children):
    axis=0 if layout['layoutType']==1 else 1
    children=[child for child in children if child['active']]
    before,after=((layout['padding'][0],layout['padding'][2]) if axis==0 else (layout['padding'][1],layout['padding'][3]))
    extent=before+after+sum(child['size'][axis] for child in children)+max(0,len(children)-1)*layout['spacingXY'][axis]
    return abs(extent-parent['size'][axis])<.001


def cross_axis_mapping(layout, parent, children):
    # Creator linear layouts leave the other axis untouched. uGUI drives both axes;
    # only a shared, representable alignment is safe to emit as a standard group.
    axis = 1 if layout['layoutType'] == 1 else 0
    children = [child for child in children if child['active']]
    before, after = ((layout['padding'][1], layout['padding'][3]) if axis == 1
                     else (layout['padding'][0], layout['padding'][2]))
    extent = parent['size'][axis]
    for scaled in (False, True):
        if scaled and any(child['scale'][axis] <= 0 for child in children):
            continue
        for alignment in (.5, 0., 1.):
            def matches(child):
                size = child['size'][axis] * (child['scale'][axis] if scaled else 1.)
                position = (-parent['anchor'][axis] * extent + before
                            + (extent - before - after - size) * alignment
                            + child['anchor'][axis] * size)
                return abs(position - child['position'][axis]) < .001
            if all(matches(child) for child in children):
                return dict(crossAxisScale=scaled, crossAxisAlignment=alignment)
    return None


def plan(ir_path, namespace, output, bindings_path=None,animation_selection=None):
    ir_path = safe(ir_path)
    ir = stage_document(ir_path)
    if ir.get('schemaVersion') != 1 or ir.get('sourceProfile') not in ('cocos-2.4.15-bundle','cocos-2.4.15-project','cocos-3.8.7-bundle','cocos-3.4.1-bundle','cocos-2.4.11-bundle','cocos-2.1.2-resource','generic-image-resources-v1','egret-custom-resource-plist-v1'):
        fail('UNSUPPORTED_IR', '$', 'Expected normalize schema 1')
    source_files = stage_manifest(ir_path.parent)['files']
    expected = {f['path']: f['sha256'] for f in source_files}
    diagnostics = list(ir['diagnostics'])
    for node in ir['nodes']:
        if node.get('sourceUITransformEnabled')is False:
            diagnostics.append(dict(code='SOURCE_UI_TRANSFORM_LIFECYCLE_UNSUPPORTED',sourceId=node['sourceId'],severity='warning',message='Source disabled UITransform geometry is retained; Unity RectTransform has no enabled state and source parent-change listener lifecycle needs manual review'))
    binding_receipt=None;label_bindings={}
    if bindings_path:
        raw=read(bindings_path);binding=load(raw)
        if binding.get('sourceManifestSha256')!=ir['sourceManifestSha256']:
            fail('BINDING_SOURCE_MISMATCH',str(bindings_path),'Binding targets a different source manifest')
        evidence={x['sha256']:x for x in ir.get('evidenceFiles',[])}
        if binding.get('evidenceSha256') not in evidence:
            fail('BINDING_EVIDENCE_MISSING',str(bindings_path),'Explicit inspect evidence hash is required')
        offset,length=binding.get('offset'),binding.get('bytes')
        if type(offset) is not int or type(length) is not int or offset<0 or length<=0 or offset+length>evidence[binding['evidenceSha256']]['bytes']:
            fail('BINDING_EVIDENCE_RANGE',str(bindings_path),'Evidence byte range is invalid')
        for item in binding.get('labelFonts',[]):
            if type(item.get('syntheticBold',False)) is not bool or not isinstance(item.get('font'),str):
                fail('INVALID_FONT_BINDING',str(bindings_path),'Font identity and syntheticBold must be typed')
            if item['component'] in label_bindings:fail('DUPLICATE_BINDING',item['component'],'Duplicate component binding')
            label_bindings[item['component']]=item
        known_ids={c['sourceId'] for c in ir['components'] if c['type']=='cc.Label'}
        if set(label_bindings)-known_ids:fail('UNKNOWN_BINDING_COMPONENT',str(bindings_path),'Binding references unknown Label')
        binding_receipt=dict(sha256=sha(raw),**binding)
        diagnostics=[d for d in diagnostics if not (d.get('sourceId') in label_bindings and d['message'].startswith('system font requires'))]
    from ..names import Names
    naming=Names(ir.get('sourceNames'))
    textures, copies = [], []
    def resource(relative, identity, role):
        source = inside(ir_path.parent, relative)
        if relative not in expected or sha(read(source)) != expected[relative]:
            fail('SOURCE_CHANGED', relative, 'Normalized asset differs from output manifest')
        target = naming.path(identity,source.suffix.lower(),'Assets/Generated/Art')
        copies.append(dict(source=relative,target=target,sha256=expected[relative],sourceId=identity,role=role,
                           guid=guid(namespace,identity)))
        return target
    for frame in ir['spriteFrames']:
        sid = frame['sourceId']
        left,top,right,bottom = frame['capInsets']
        textures.append(dict(id=sid, path=resource(frame['image'],sid,'sprite'),
                             border=[left,bottom,right,top], size=frame['rect'][2:4],
                             originalSize=frame['originalSize'],offset=frame['offset']))
        textures.append(dict(id=sid+'@original',path=resource(frame['originalImage'],sid+'@original','sprite'),
                             border=[0,0,0,0],size=frame['originalSize'],originalSize=frame['originalSize'],offset=[0,0]))
    assets=[]
    for asset in ir['assets']:
        item=dict(id=asset['sourceId'],kind=asset['kind'],path=resource(asset['path'],asset['sourceId'],'native'),fontCoverage=asset.get('fontCoverage'))
        if asset['kind']=='cc.TTFFont':item['fontAssetPath']=naming.path(asset['sourceId'],'.asset','Assets/Generated/Art')
        assets.append(item)
    bitmap_fonts=[]
    for font in ir.get('bitmapFonts',[]):
        item={k:v for k,v in font.items() if k!='atlasImage'}
        item['id']=font['sourceId']
        item['atlasGuid']=guid(namespace,font['sourceId']+'@atlas')
        item['path']=resource(font['atlasImage'],font['sourceId']+'@atlas','bitmap-atlas')
        item['fontPath']=naming.path(font['sourceId'],'.asset','Assets/Generated/Art')
        bitmap_fonts.append(item)
    resource_ids = {a['id'] for a in assets if a['kind']=='cc.TTFFont'}|{f['id'] for f in bitmap_fonts}
    sprite_ids = {s['id'] for s in textures}
    nodes = ir['nodes']
    node_ids = {n['sourceId'] for n in nodes}
    if len(node_ids) != len(nodes):
        fail('DUPLICATE_NODE','$','Duplicate node identities')
    by_node={n['sourceId']:n for n in nodes}
    for n in nodes:
        if len(n['children'])!=len(set(n['children'])):
            fail('INVALID_NODE_GRAPH',n['sourceId'],'Duplicate child reference')
        for child in n['children']:
            if child not in by_node or by_node[child]['parent']!=n['sourceId']:
                fail('INVALID_NODE_GRAPH',n['sourceId'],'Child missing or parent does not agree')
        if n['parent'] in by_node and n['sourceId'] not in by_node[n['parent']]['children']:
            fail('INVALID_NODE_GRAPH',n['sourceId'],'Parent does not list child')
        if n['parent'] and n['parent'] not in node_ids:
            diagnostics.append(diagnostic('MISSING_PARENT',n['sourceId'],'Parent not present in IR',n['sourceId']))
        if n['size'][0] <= 0 or n['size'][1] <= 0:
            diagnostics.append(diagnostic('ZERO_SIZE_NODE',n['sourceId'],'Node needs visibility/layout review',n['sourceId']))
        seen=set();cursor=n
        while cursor.get('parent') in node_ids:
            if cursor['sourceId'] in seen:
                fail('NODE_CYCLE',n['sourceId'],'Parent cycle')
            seen.add(cursor['sourceId']);cursor=next(v for v in nodes if v['sourceId']==cursor['parent'])
    native_types={'cc.Sprite','cc.Label','cc.Widget','cc.Mask','cc.ScrollView','cc.Layout','cc.Button','cc.LabelOutline'}
    native_materials={f['sourceId'] for f in ir.get('materials',[]) if f['nativeRole']=='standard-ugui'}
    def resolve_id(value):
        seen=set()
        while value in ir.get('aliases',{}):
            if value in seen:fail('REDIRECT_CYCLE',value,'IR alias cycle')
            seen.add(value);value=ir['aliases'][value]
        return value
    components=[]
    for c in ir['components']:
        entry=dict(c)
        if c['sourceId'] in label_bindings:
            bind=label_bindings[c['sourceId']]
            if c.get('font') is not None:fail('BINDING_REPLACES_EXPLICIT_FONT',c['sourceId'],'Only absent system-font references may be source-bound')
            entry['font']=bind['font']
            entry['bold']=bind.get('syntheticBold',False)
        for field in ('spriteFrame','font'):
            value=entry.get(field);seen=set()
            while value in ir.get('aliases',{}):
                if value in seen:fail('REDIRECT_CYCLE',value,'IR alias cycle')
                seen.add(value);value=ir['aliases'][value]
            if field in entry:entry[field]=value
        c=entry
        entry['convertible']=c['type'] in native_types and c['node'] in node_ids
        entry['nativeId']=guid(namespace,c['sourceId'])
        if c.get('supported') is False:
            entry['convertible']=False
            diagnostics.append(diagnostic('SOURCE_COMPONENT_PROFILE_HANDOFF',c['sourceId'],'Source component semantics are not implemented for this profile',c['sourceId']))
            components.append(entry);continue

        if any(resolve_id(mat) not in native_materials for mat in c.get('materials',[])):
            entry['convertible']=False
            diagnostics.append(diagnostic('CUSTOM_MATERIAL_HANDOFF',c['sourceId'],'Material is not recognized standard UI texture',c['sourceId']))
        if c['type']=='cc.Sprite':
            if c.get('spriteFrame') is not None and c.get('spriteFrame') not in sprite_ids or c['mode'] not in (0,1,2):
                entry['convertible']=False
                diagnostics.append(diagnostic('SPRITE_NOT_CONVERTIBLE',c['sourceId'],'Missing frame or unsupported mode',c['sourceId']))
            if c.get('spriteFrame') is None:
                entry['needsSpriteBinding']=True
                diagnostics.append(diagnostic('SOURCE_SPRITE_UNBOUND',c['sourceId'],'Source Sprite has no frame; native Image is disabled until AI binds an actual Sprite and enables it',c['sourceId']))
            if not c.get('trim',True) and c['mode'] in (1,2):
                entry['convertible']=False
                diagnostics.append(diagnostic('SLICED_UNTRIMMED_UNSUPPORTED',c['sourceId'],'Needs Cocos size-mode evidence',c['sourceId']))
        elif c['type']=='cc.Label':
            if c.get('italic') or c.get('underline'):
                entry['convertible']=False
                diagnostics.append(diagnostic('LABEL_STYLE_UNSUPPORTED',c['sourceId'],'Italic/underline require explicit native style mapping',c['sourceId']))
            if c.get('font') not in resource_ids:
                entry['convertible']=False
                diagnostics.append(diagnostic('FONT_NOT_CONVERTIBLE',c['sourceId'],'No imported matching font; no fallback text',c['sourceId']))
            ttf=next((a for a in assets if a['id']==c.get('font') and a.get('fontCoverage')),None)
            if ttf:
                from ..assets.ttf import missing
                absent=missing(ttf['fontCoverage'],c['text'])
                if absent:
                    entry['convertible']=False
                    diagnostics.append(diagnostic('SOURCE_FONT_GLYPHS_MISSING',c['sourceId'],'Original TTF lacks codepoints: '+str(absent),c['sourceId']))
            font=next((f for f in bitmap_fonts if f['id']==c.get('font')),None)
            if font:
                from ..assets.bitmap import single_line
                try:
                    entry['sourceBold']=entry.get('bold',False)
                    entry['bold']=False
                    entry['bitmapProbe']=single_line(font,c['text'],c['fontSize'],c.get('spacing',0))
                    codepoints=list(map(ord,c['text']))
                    actual_pairs={(codepoints[i],codepoints[i+1]) for i in range(len(codepoints)-1)}
                    if c['fontSize']!=font['pointSize'] and any((k['first'],k['second']) in actual_pairs and k['advance'] for k in font['kernings']):
                        fail('BITMAP_KERNING_SCALE_UNSUPPORTED',c['sourceId'],'Source pair offsets are unscaled, native TMP scales font features; this text needs a reviewed font variant')
                except ValueError as error:
                    entry['convertible']=False
                    diagnostics.append(diagnostic(getattr(error,'code','BITMAP_LAYOUT_UNSUPPORTED'),c['sourceId'],str(error),c['sourceId']))
            if c.get('overflow')not in(0,1,2,3):entry['convertible']=False
            entry['presentationPolicy']='native-tmp-sizing-v1'
            diagnostics.append(diagnostic('LABEL_METRICS_NOT_VERIFIED',c['sourceId'],'TMP line metrics need engine/reference comparison',c['sourceId']))
        elif c['type']=='cc.Widget':
            node=by_node.get(c['node'],{})
            entry.setdefault('center',[0,0]);entry.setdefault('centerAbsolute',[True,True])
            flags=c['flags'];horizontal=flags&56;vertical=flags&7
            invalid=(flags&~63 or horizontal in(24,48,56)or vertical in(3,6,7)or c.get('alignMode',1)not in(0,1,2))
            if invalid or c.get('target')not in(None,node.get('parent'))or node.get('scale',[1,1])[:2]!=[1,1]or node.get('rotation')!=[0,0,0,1]:
                entry['convertible']=False
                diagnostics.append(diagnostic('WIDGET_CONTEXT_UNSUPPORTED',c['sourceId'],'Requires parent-relative target, valid edge/center flags and unrotated unit-scale node',c['sourceId']))
            if flags and node.get('parent')not in by_node:
                entry['externalParentContext']='candidate-design-root'
                diagnostics.append(diagnostic('WIDGET_EXTERNAL_PARENT_CONTEXT',c['sourceId'],'Prefab root keeps native constraints for its future parent; the candidate Scene uses its declared design root, not a recovered original game viewport',c['sourceId']))
            entry['presentationPolicy']='native-rect-constraints-v1'
        elif c['type']=='cc.Mask':
            if c['maskType']!=0 or c['inverted']:
                entry['convertible']=False
                diagnostics.append(diagnostic('MASK_SUBSET_UNSUPPORTED',c['sourceId'],'Only non-inverted rectangular mask supported',c['sourceId']))
        elif c['type']=='cc.ScrollView':
            if c['horizontal'] or c['vertical'] or c['content'] not in node_ids:
                entry['convertible']=False
                diagnostics.append(diagnostic('SCROLL_SUBSET_UNSUPPORTED',c['sourceId'],'First subset preserves disabled axes and native content/viewport references',c['sourceId']))
        elif c['type']=='cc.Layout':
            children=[by_node[k]for k in by_node[c['node']]['children']]
            for code,message in layout_issues(c,children):
                entry['convertible']=False;diagnostics.append(diagnostic(code,c['sourceId'],message,c['sourceId']))
            entry.setdefault('alignCross',False);entry.setdefault('affectedByScale',False)
            entry['presentationPolicy']='native-flow-layout-v1'if c['layoutType']==3 else'native-linear-layout-v1'
            if c['layoutType']==3:entry['effectiveCellSize']=list(c['cellSize'])
        elif c['type']=='cc.Button':
            if c['transition'] not in (0,3) or c['target'] not in (None,c['node']):
                entry['convertible']=False
                diagnostics.append(diagnostic('BUTTON_SUBSET_UNSUPPORTED',c['sourceId'],'Only self-targeted none/scale transitions supported',c['sourceId']))
            if c['events']:
                diagnostics.append(diagnostic('BUTTON_BUSINESS_UNBOUND',c['sourceId'],'Native Button generated; original handlers remain AI work: '+','.join(e.get('handler') or '?' for e in c['events']),c['sourceId']))
        elif c['type']=='cc.LabelOutline':
            label=next((x for x in ir['components'] if x['node']==c['node'] and x['type']=='cc.Label'),None)
            if not label:entry['convertible']=False
            diagnostics.append(diagnostic('OUTLINE_METRICS_NOT_VERIFIED',c['sourceId'],'Bitmap outline is baked; TTF outline width needs actual pixel comparison',c['sourceId']))
        if not entry['convertible']:
            diagnostics.append(diagnostic('COMPONENT_HANDOFF',c['sourceId'],'Native mapping unavailable for '+str(c['type']),c['sourceId']))
        components.append(entry)
    for c in components:
        if c['type']=='cc.LabelOutline' and c['convertible'] and not any(x['type']=='cc.Label' and x['node']==c['node'] and x['convertible'] for x in components):
            c['convertible']=False
            diagnostics.append(diagnostic('MISSING_OUTLINE_LABEL',c['sourceId'],'Label dependency could not be converted',c['sourceId']))
    from .common import reject_layout_conflicts
    diagnostics.extend(reject_layout_conflicts(components))
    from ..assets.animation import plan_clips
    animations,animation_gaps=plan_clips(ir,namespace,PROFILE,animation_selection)
    naming.records.extend(a['nameEvidence'] for a in animations)
    if animation_selection:
        unselected={c['sourceId'] for c in ir.get('animationClips',[]) if c['sourceId'] not in animation_selection}
        diagnostics=[d for d in diagnostics if d.get('sourceId') not in unselected]
    diagnostics.extend(animation_gaps)
    from .prefabs import plan_prefabs
    source_prefabs,prefab_gaps=plan_prefabs(ir,components)
    from .prefabs import native_relationships
    source_prefabs,prefab_instances=native_relationships(ir,source_prefabs,components)
    for prefab in source_prefabs:prefab['path']=naming.path(prefab['sourceId'],'.prefab','Assets/Generated/Views/Sources')
    diagnostics.extend(prefab_gaps)
    out = new_output(output,[ir_path.parent])
    (out/'resources').mkdir()
    for copy in copies:
        target = out/'resources'/(sha(copy['target'].encode())[:24]+Path(copy['target']).suffix)
        target.write_bytes(read(inside(ir_path.parent,copy['source'])))
        copy['source']='resources/'+target.name
    from .common import native_color_nodes
    nodes=native_color_nodes(nodes,components)
    for node in nodes:
        if node.get('sourceGeometryProfile'):
            diagnostics.append(diagnostic('COCOS3_UNITY_LAYER_HANDOFF',node['sourceId'],'Original layer bits retained as provenance; native uGUI uses target UI layer 5, source camera visibility is pending',node['sourceId']))
    result=dict(schemaVersion=1,toolVersion=__version__,targetProfile=PROFILE,namespace=namespace,
                sourcePrefabs=source_prefabs,prefabInstances=prefab_instances,naming=naming.report(),
                scopeMode=ir.get('scopeMode','asset-selection'),
                sourceIrSha256=sha(stage_bytes(ir_path)),sourceManifestPath=ir.get('sourceManifestPath'),sourceManifestSha256=ir['sourceManifestSha256'],
                sourceRoots=ir.get('sourceRoots',{}),sourceLocations=ir.get('sourceLocations',{}),designSize=[750,1334],pixelsPerUnit=100,
                textures=textures,assets=assets,bitmapFonts=bitmap_fonts,animations=animations,bindings=binding_receipt,nodes=nodes,components=components,copies=copies,
                diagnostics=diagnostics,galleryOnly=not bool(nodes),editorValidation='not_run')
    write_json(out/'plan.json',result)
    return finish(out,result)


def export(plan_path, output):
    plan_path=safe(plan_path)
    from ..sources.compiled import ParseError
    try:p=stage_document(plan_path)
    except ParseError as error:
        if error.code=='STAGE_DOCUMENT_CHANGED':fail('PLAN_CHANGED',str(plan_path),'Plan differs from manifest')
        raise
    if p.get('targetProfile')!=PROFILE or p.get('schemaVersion')!=1:
        fail('UNSUPPORTED_PLAN','$','Expected Unity plan schema 1')
    # Plan JSON itself must match its create-only manifest, not just copied images.
    pm=stage_manifest(plan_path.parent)
    expected={f['path']:f['sha256'] for f in pm['files']}
    if expected.get(plan_path.name)!=sha(stage_bytes(plan_path)):
        fail('PLAN_CHANGED',str(plan_path),'Plan differs from manifest')
    for c in p['copies']:
        if sha(read(inside(plan_path.parent,c['source'])))!=c['sha256']:
            fail('SOURCE_CHANGED',c['source'],'Plan resource differs')
        if not c['target'].startswith('Assets/Generated/Art/'):
            fail('UNSAFE_TARGET',c['target'],'Unexpected target root')
    out=new_output(output,[plan_path.parent])
    for folder in ['Assets/Generated/Art','Assets/Generated/Animations','Assets/Generated/Controllers','Assets/Generated/Views','Assets/Generated/Scenes',
                   'Assets/Monkey/Editor','Assets/Manual','Packages','ProjectSettings','Analysis']:
        (out/folder).mkdir(parents=True,exist_ok=True)
    ownership=[]
    for c in p['copies']:
        target=inside(out,c['target']);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(read(inside(plan_path.parent,c['source'])))
        metadata='fileFormatVersion: 2\nguid: '+c['guid']+'\n'
        if c['role'] in ('sprite','bitmap-atlas'):
            metadata+='TextureImporter:\n  serializedVersion: 13\n  externalObjects: {}\n  textureType: 0\n  textureShape: 1\n  alphaSource: 0\n  alphaIsTransparency: 1\n'
        Path(str(target)+'.meta').write_text(metadata,encoding='utf-8')
        ownership.append(dict(path=c['target'],sourceId=c['sourceId'],guid=c['guid']))
    view_path=out/'Assets/Generated/Views/MonkeyCandidateView.cs'
    view_path.write_bytes(files('monkey.targets').joinpath('MonkeyCandidateView.cs').read_bytes())
    Path(str(view_path)+'.meta').write_text('fileFormatVersion: 2\nguid: '+guid(p['namespace'],'native-view-script')+'\n')
    grid_path=out/'Assets/Generated/Views/IntrinsicGridLayoutGroup.cs'
    grid_path.write_bytes(files('monkey.targets').joinpath('IntrinsicGridLayoutGroup.cs').read_bytes())
    Path(str(grid_path)+'.meta').write_text('fileFormatVersion: 2\nguid: '+guid(p['namespace'],'intrinsic-grid-script')+'\n')
    numeric_path=out/'Assets/Monkey/Editor/MonkeyNumericCode.cs'
    numeric_path.write_bytes(files('monkey.targets').joinpath('UnityNumericCode.cs').read_bytes())
    Path(str(numeric_path)+'.meta').write_text('fileFormatVersion: 2\nguid: '+guid(p['namespace'],'numeric-code-editor')+'\n')
    instances_path=out/'Assets/Monkey/Editor/MonkeyPrefabInstances.cs'
    instances_path.write_bytes(files('monkey.targets').joinpath('UnityPrefabInstances.cs').read_bytes())
    Path(str(instances_path)+'.meta').write_text('fileFormatVersion: 2\nguid: '+guid(p['namespace'],'prefab-instances-editor')+'\n')
    for filename,relative in [('NativeFlowLayoutGroup.cs','Assets/Generated/Views/'),('NativeLinearLayoutGroup.cs','Assets/Generated/Views/'),('NativeRectConstraints.cs','Assets/Generated/Views/'),('NativeTextLineBox.cs','Assets/Generated/Views/'),('UnityDynamicUi.cs','Assets/Monkey/Editor/')]:
        dest=out/relative/filename;dest.write_bytes(files('monkey.targets').joinpath(filename).read_bytes())
        Path(str(dest)+'.meta').write_text('fileFormatVersion: 2\nguid: '+guid(p['namespace'],'native-ui/'+filename)+'\n')
    adapter=files('monkey.targets').joinpath('UnityImporter.cs').read_bytes()
    adapter_path=out/'Assets/Monkey/Editor/MonkeyImporter.cs';adapter_path.write_bytes(adapter)
    Path(str(adapter_path)+'.meta').write_text('fileFormatVersion: 2\nguid: '+guid(p['namespace'],'editor-adapter')+'\n')
    # Only the typed, finite import instruction subset is sent to the Editor.
    instruction={key:p.get(key,[]) for key in ('designSize','pixelsPerUnit','textures','assets','bitmapFonts','nodes','components','galleryOnly','animations','sourcePrefabs','prefabInstances')}
    instruction['tmpResources']=dict(packageName='com.unity.ugui',packageVersion='2.6.0',resource='Package Resources/TMP Essential Resources.unitypackage',importMode='package-completion-callback')
    instruction['glyphReadback']='native-quad-padding-v1'
    instruction['sceneRoundtrip']=True
    instruction['sourcePrefabReadback']='native-layout-settled-v1'
    instruction['transformReadback']='full-local-v1'
    instruction['sourceDiagnosticCount']=len(p['diagnostics'])
    instruction['prefabGuid']=guid(p['namespace'],'native-prefab')
    instruction['prefabRelationshipReadback']='native-source-correspondence-v1'
    instruction['uiGeometryReadback']='native-ui-layout-roundtrip-v1'
    from .dynamic_ui import probe_sources
    instruction['uiStateProbeVersion']=2;instruction['uiProbeSources']=probe_sources(instruction)
    instruction['textLineBoxReadback']='native-cocos-ttf-line-box-v1'
    instruction['sceneGuid']=guid(p['namespace'],'native-scene')
    if p['galleryOnly']:
        instruction['galleryReadback']='exact-sprite-and-rect-v1'
        instruction['textures']=[dict(t,guid=guid(p['namespace'],t['id']))for t in instruction['textures']]
    write_json(out/'Assets/Monkey/Editor/import-plan.json',instruction)
    write_json(out/'Packages/manifest.json',dict(dependencies={'com.unity.ugui':'2.6.0',
               'com.unity.modules.ui':'1.0.0','com.unity.modules.imgui':'1.0.0','com.unity.modules.animation':'1.0.0'}))
    (out/'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 6000.6.2f1\n')
    (out/'Assets/Manual/README.md').write_text('AI/人工业务代码区。生成区默认不覆盖；缺口见工程根 Analysis/handoff.json。\n')
    (out/'README.md').write_text('Unity 原生资源/UI候选，非可玩游戏。\n\n打开后执行 Tools > Monkey > Import Candidate。\n'
        '仅首次导入新候选；已生成 Prefab/Scene 存在时拒绝覆盖。\n'
        '或用独立 batchmode -projectPath 此目录 -executeMethod MonkeyImporter.ImportBatch。\n'
        '导入成功后删除 Assets/Monkey 仍保留原生可编辑资产；Player 不读取转换 JSON。\n'
        '真实编辑器/画面对照/业务尚未验证，见 Analysis。\n')
    from ..assets.animation import module_report
    write_json(out/'Analysis/animation-module.json',module_report(p.get('animations',[])))
    groups={}
    module_names={n['sourceId'].split('#')[0]:n['name'] for n in p['nodes'] if n['parent'] is None}
    component_types={c['sourceId']:c['type'] for c in p['components']}
    def cause(d):
        code=d['code'];message=d['message'].lower()
        if component_types.get(d.get('sourceId')) in ('cc.SortOrder','cc.SortRoot'):return 'render-order'
        if any(term in code for term in ('FONT','LABEL','BITMAP','OUTLINE')):return 'text-and-font-metrics'
        if any(term in code for term in ('SPRITE','TEXTURE','NATIVE','REFERENCE','REDIRECT')):return 'asset-binding'
        if any(term in code for term in ('NODE','WIDGET','LAYOUT','GRID','SCROLL','MASK')):return 'native-layout'
        if code=='BUTTON_BUSINESS_UNBOUND':return 'button-business-handlers'
        if any(term in code for term in ('IDENTITY','CONFIG')):return 'source-format'
        if any(term in message for term in ('cc.sortorder','cc.sortroot')):return 'render-order'
        return 'unknown-components-and-behavior'
    for d in p['diagnostics']:
        if d['code'].startswith('ANIMATION_'):continue
        sid=d.get('sourceId') or 'source-config';module=sid.split('#',1)[0] if '#' in sid else 'resources'
        key=(module,cause(d));groups.setdefault(key,[]).append(d)
    tasks=[]
    for (module,root_cause),gaps in sorted(groups.items()):
        task_id='module-'+sha((module+'/'+root_cause).encode())[:12]
        tasks.append(dict(taskId=task_id,module=module,moduleName=module_names.get(module,'Resources'),rootCause=root_cause,
            sourceRefs=sorted({str(d.get('sourceId') or d.get('location')) for d in gaps}),
            sourceManifest=dict(path=p.get('sourceManifestPath'),sha256=p.get('sourceManifestSha256')),
            sourceLocations=[dict(location=d.get('location'),sourceId=d.get('sourceId')) for d in gaps],
            gaps=gaps,generatedTargets=['Assets/Generated/Views/Candidate.prefab'],
            allowedPaths=['Assets/Manual/'],dependencies=['matching original evidence'],
            verificationScope=['affected UI module in real Editor','source reference comparison']))
    if p.get('animations') or any(d['code'].startswith('ANIMATION_') for d in p['diagnostics']):
        from ..assets.animation import handoff_task
        tasks.append(handoff_task(p['animations'],p['diagnostics']))
    write_json(out/'Analysis/handoff.json',dict(schemaVersion=1,tasks=tasks,
               verification=dict(static='pending',editor='not_run',visual='not_run',business='not_run')))
    write_json(out/'Analysis/source-map.json',dict(assets=ownership,sourceRoots=p.get('sourceRoots',{}),sourceLocations=p.get('sourceLocations',{}),
        fonts=[dict(sourceId=f['id'],target=f['fontPath'],atlas=f['path']) for f in p.get('bitmapFonts',[])]+[dict(sourceId=a['id'],target=str(Path(a['path']).with_suffix('.asset'))) for a in p['assets'] if a['kind']=='cc.TTFFont'],
        nodes=[dict(sourceId=n['sourceId'],target='Assets/Generated/Views/Candidate.prefab',name=n['name']) for n in p['nodes']],
        components=[dict(sourceId=c['sourceId'],node=c['node'],type=c['type'],convertible=c['convertible'],
            target='Assets/Generated/Views/Candidate.prefab',viewField={'cc.Sprite':'Images','cc.Label':'Labels','cc.Button':'Buttons'}.get(c['type']),
            bindingEvidence='Actual indices and native fileIDs require Analysis/editor-readback.json') for c in p['components']]))
    if p.get('bindings'):write_json(out/'Analysis/font-bindings.json',p['bindings'])
    write_json(out/'Analysis/name-map.json',p.get('naming',{}))
    report=dict(schemaVersion=1,toolVersion=__version__,targetProfile=PROFILE,namespace=p['namespace'],
                scopeMode=p.get('scopeMode','asset-selection'),
                planSha256=sha(stage_bytes(plan_path)),sourceRoots=p.get('sourceRoots',{}),sourceManifestSha256=p.get('sourceManifestSha256'),diagnostics=p['diagnostics'],editorValidation='not_run',
                visualValidation='not_run',businessValidation='not_run',galleryOnly=p['galleryOnly'])
    write_json(out/'Analysis/candidate.json',report)
    return finish(out,report)


def close(actual,expected,tolerance=.001):
    if isinstance(expected,list):
        return isinstance(actual,list) and len(actual)==len(expected) and all(close(a,b,tolerance) for a,b in zip(actual,expected))
    return type(actual) in (int,float) and abs(actual-expected)<=tolerance


def label_font_matches(spec,actual,font,evidence=None):
    """SHRINK sizes may vary only with explicit native auto-size/bounds proof."""
    import math
    if not actual or not font or not font.get('guid') or actual.get('fontGuid')!=font['guid'] or actual.get('text')!=spec['text'] or actual.get('allCharactersPresent')is not True:return False
    if close(actual.get('fontSize'),spec['fontSize']) and not actual.get('autoSizeReadback'):return True
    if spec.get('overflow')!=2:return close(actual.get('fontSize'),spec['fontSize'])
    proof=evidence or actual
    config=proof.get('autoSizing')is True and (not evidence or proof.get('prefabUnchanged')is True)
    measured=proof.get('actualFontSize',proof.get('fontSize'));low=proof.get('fontSizeMin');high=proof.get('fontSizeMax')
    if not all(type(v)in(int,float)and math.isfinite(v)for v in (measured,low,high)):return False
    if evidence and (proof.get('fontGuid')!=font['guid'] or proof.get('text')!=spec['text']or proof.get('allCharactersPresent')is not True or not close(proof.get('requestedFontSize'),spec['fontSize'])):return False
    return bool(config and close(high,spec['fontSize'])and 0<low<=high and low-.001<=measured<=high+.001)


def node_geometry_matches(actual,source,full=False):
    if not actual or actual.get('active')!=source['active']:
        return False
    if any(not close(actual.get(key),source[field]) for key,field in [('size','size'),('pivot','anchor'),('position','position')]):
        return False
    if source.get('sourceGeometryProfile'):
        if not close(actual.get('opacity'),source['opacity']):return False
        if source.get('verifyUiColor') and not close(actual.get('color'),source['color']):return False
    if full:
        rotation=actual.get('rotation');expected=source['rotation']
        # q and -q describe the same native rotation. No angular tolerance change.
        if not close(actual.get('scale'),source['scale']) or not (close(rotation,expected) or close(rotation,[-v for v in expected])):
            return False
    return True


def gallery_readback(instruction,readback):
    if instruction.get('galleryReadback')!='exact-sprite-and-rect-v1':return []
    expected={t['id']:t for t in instruction['textures']if not t['id'].endswith('@original')}
    rows=readback.get('gallery')
    actual={r.get('id'):r for r in rows}if isinstance(rows,list)and all(isinstance(r,dict)for r in rows)else{}
    valid=instruction.get('galleryOnly')is True and not instruction.get('nodes')and not instruction.get('components')and not instruction.get('sourcePrefabs')and readback.get('nativeScope')=='resources-and-gallery-only'and readback.get('sourceGraphVerification')=='not_run'
    valid=valid and isinstance(rows,list)and len(actual)==len(rows)and set(actual)==set(expected)
    if valid:valid=all(actual[key].get('spriteGuid')==spec['guid']and actual[key].get('geometryVerified')is True for key,spec in expected.items())
    return []if valid else[diagnostic('NATIVE_GALLERY_READBACK','Analysis/editor-readback.json','Resource-only preview must prove exact sprite identities/rects without claiming source graph restoration')]


def verify(candidate, output, level='static'):
    root=safe(candidate);m=stage_manifest(root);diagnostics=[]
    from .layout import lookup
    from ..sources.containers import fingerprint
    path_for=lambda p:lookup(p,m)
    native={};editor='not_run'
    if level=='editor':
        readback_path=root/'Analysis/editor-readback.json'
        if not readback_path.is_file():
            diagnostics.append(diagnostic('EDITOR_NOT_RUN','Analysis/editor-readback.json','Run native import in the declared Editor first'))
        else:
            rb=load(read(readback_path,max_bytes=128*1024*1024),max_nodes=8_000_000)
            native={f['path']:f['sha256'] for f in rb.get('nativeFiles',[])}
            if rb.get('unityVersion')!='6000.6.2f1' or rb.get('missingScripts')!=0:
                diagnostics.append(diagnostic('EDITOR_READBACK_FAILED',str(readback_path),'Version/missing-script check failed'))
            for relative,expected in native.items():
                file=inside(root,relative)
                if not file.is_file() or fingerprint(file)!=expected:
                    diagnostics.append(diagnostic('NATIVE_FILE_CHANGED',relative,'Native file differs from saved readback'))
            instruction=load(read(root/path_for('Assets/Monkey/Editor/import-plan.json'),max_bytes=128*1024*1024),max_nodes=8_000_000)
            diagnostics.extend(gallery_readback(instruction,rb))
            from ..code_validation import numeric as verify_numeric
            diagnostics.extend(verify_numeric(instruction['components'],rb.get('numericCodeBindings'),'unity','scene',rb.get('numericCodeExercise',[])))
            if instruction.get('bitmapFonts') or any(a['path'].lower().endswith('.ttf') for a in instruction['assets']):
                resources=rb.get('tmpResources') or {}
                expected_resources=instruction.get('tmpResources',{})
                if resources.get('status')!='ready' or resources.get('completionProof') not in ('package-completed-event','preexisting-files') or any(resources.get(k)!=expected_resources.get(k) for k in ('packageName','packageVersion','resource')) or not all(resources.get(k) for k in ('archiveSha256','bitmapGuid','distanceGuid','mobileGuid','settingsGuid')):
                    diagnostics.append(diagnostic('TMP_RESOURCES_NOT_VERIFIED','Analysis/tmp-resources.json','Exact installed package, essential resource import and native shader/settings identities are unverified'))
            if instruction.get('sceneRoundtrip') and rb.get('sceneReopened') is not True:
                diagnostics.append(diagnostic('SCENE_ROUNDTRIP_NOT_VERIFIED','Candidate.unity','Saved scene was not normally closed/reopened before native readback'))
            json_assets={a['id']:a for a in rb.get('jsonAssets',[])}
            actual_prefabs={a['sourceId']:a for a in rb.get('sourcePrefabs',[])}
            from .prefabs import verify_native_relationships
            template_guids={sid:row.get('guid')for sid,row in actual_prefabs.items()}
            diagnostics.extend(verify_native_relationships(instruction.get('prefabInstances',[]),instruction.get('sourcePrefabs',[]),rb.get('prefabInstances'),'scene',template_guids))
            if any(x.get('mountedChildren')or x.get('mountedComponents')for x in instruction.get('prefabInstances',[])):
                diagnostics.extend(verify_native_relationships(instruction['prefabInstances'],instruction.get('sourcePrefabs',[]),rb.get('candidatePrefabInstances'),'candidate-prefab',template_guids))
            from .dynamic_ui import expectations,verify_probes
            diagnostics.extend(verify_probes(instruction,rb.get('dynamicUiProbes')))
            scene_expected,ui_gaps=expectations(instruction,rb.get('nativeInitialNodes'),'UnityScene');diagnostics.extend(ui_gaps)
            expected_nodes={n['sourceId']:n for n in instruction['nodes']}
            for spec in instruction.get('sourcePrefabs',[]):
                actual=actual_prefabs.get(spec['sourceId'],{})
                diagnostics.extend(verify_native_relationships([x for x in instruction.get('prefabInstances',[])if x['owner']==spec['sourceId']],instruction.get('sourcePrefabs',[]),actual.get('prefabInstances'),spec['sourceId'],template_guids))
                target=spec['path']
                if not actual.get('guid') or actual.get('nodeCount')!=spec['nodeCount'] or actual.get('missingScripts')!=0 or actual.get('path')!=target or target not in native:
                    diagnostics.append(diagnostic('SOURCE_PREFAB_NOT_VERIFIED',spec['sourceId'],'Independent native prefab save/reopen evidence is absent or inconsistent'))
                if instruction.get('prefabRelationshipReadback')=='native-source-correspondence-v1':
                    root_variant=any(x['owner']==spec['sourceId']and x['root']==spec['root']for x in instruction.get('prefabInstances',[]))
                    if actual.get('nativePrefabType')!=('Variant'if root_variant else'Regular'):
                        diagnostics.append(diagnostic('NATIVE_PREFAB_ASSET_TYPE',spec['sourceId'],'Native Prefab/Variant asset type differs from the source relation'))
                if instruction.get('sourcePrefabReadback')=='native-layout-settled-v1':
                    saved_nodes={n['sourceId']:n for n in actual.get('nodes',[])}
                    if actual.get('savedReloaded') is not True or actual.get('geometryPhase')!='native-layout-settled-v1' or set(saved_nodes)!=set(spec['nodes']):
                        diagnostics.append(diagnostic('SOURCE_PREFAB_GEOMETRY_NOT_VERIFIED',spec['sourceId'],'Saved native hierarchy geometry evidence is absent'))
                    prefab_expected,ui_gaps=expectations(instruction,actual.get('nativeInitialNodes'),spec['sourceId'],[expected_nodes[sid]for sid in spec['nodes']]);diagnostics.extend(ui_gaps)
                    prefab_expected={n['sourceId']:n for n in prefab_expected}
                    for sid in spec['nodes']:
                        source=prefab_expected[sid];saved=saved_nodes.get(sid,{})
                        if not node_geometry_matches(saved,source,instruction.get('transformReadback')=='full-local-v1'):
                            diagnostics.append(diagnostic('SOURCE_PREFAB_GEOMETRY_MISMATCH',sid,'Independent saved prefab differs: '+target))
                    if actual.get('referencesVerified') is not True or actual.get('referenceFailures'):
                        diagnostics.append(diagnostic('SOURCE_PREFAB_REFERENCE_MISMATCH',spec['sourceId'],'Saved component references differ: '+str(actual.get('referenceFailures'))))
            for prefab in instruction.get('sourcePrefabs',[]):
                source_nodes=set(prefab['nodes']);specs=[c for c in instruction['components']if c.get('node')in source_nodes]
                diagnostics.extend(verify_numeric(specs,actual_prefabs.get(prefab['sourceId'],{}).get('numericCodeBindings'),'unity',prefab['sourceId']))
            for spec in instruction['assets']:
                if spec['kind']=='cc.JsonAsset':
                    actual=json_assets.get(spec['id'],{})
                    if actual.get('textSha256')!=fingerprint(root/spec['path']) or not actual.get('guid'):
                        diagnostics.append(diagnostic('JSON_READBACK_MISMATCH',spec['path'],'Native TextAsset text/identity differs or is absent'))
            by_id={s['id']:s for s in rb.get('sprites',[])}
            for spec in instruction['textures']:
                actual=by_id.get(spec['id'])
                meta=(root/(spec['path']+'.meta')).read_text() if (root/(spec['path']+'.meta')).is_file() else ''
                if not actual or actual.get('size')!=spec['size'] or actual.get('border')!=spec['border'] or actual.get('guid','') not in meta or not actual.get('fileId'):
                    diagnostics.append(diagnostic('SPRITE_READBACK_MISMATCH',spec['path'],'Native sprite size/border/GUID/fileID mismatch'))
            by_node={n['sourceId']:n for n in rb.get('nodes',[])}
            for spec in scene_expected:
                actual=by_node.get(spec['sourceId'])
                if not node_geometry_matches(actual,spec,instruction.get('transformReadback')=='full-local-v1'):
                    diagnostics.append(diagnostic('NODE_READBACK_MISMATCH',spec['sourceId'],'Saved RectTransform differs from plan'))
            if not rb.get('editableRoundtrip'):
                diagnostics.append(diagnostic('EDITABLE_ROUNDTRIP_NOT_VERIFIED','Assets/Generated/Views/EditableProbe.prefab','Native edit/save/reopen proof is absent or failed'))
            by_font={f['id']:f for f in rb.get('fonts',[])}
            for spec in instruction.get('bitmapFonts',[]):
                actual=by_font.get(spec['id'])
                if not actual or actual.get('glyphCount',0)<len(spec['glyphs']) or not close(actual.get('pointSize'),spec['pointSize']) or not close(actual.get('lineHeight'),spec['lineHeight']):
                    diagnostics.append(diagnostic('BITMAP_FONT_READBACK_MISMATCH',spec['id'],'Saved static font glyph count or metrics differ'))
                if spec.get('atlasGuid') and (not actual or actual.get('atlasGuid')!=spec['atlasGuid'] or actual.get('materialAtlasGuid')!=spec['atlasGuid']):
                    diagnostics.append(diagnostic('BITMAP_ATLAS_READBACK_MISMATCH',spec['id'],'Saved font and material must reference the original atlas GUID'))
            by_label={l['sourceId']:l for l in rb.get('labels',[])}
            from ..cocos_native_finish import font_evidence
            extra_fonts=font_evidence(root,instruction,readback_path)
            node_specs={n['sourceId']:n for n in instruction['nodes']}
            for spec in instruction['components']:
                if spec['type']!='cc.Label' or not spec['convertible']:continue
                actual=by_label.get(spec['sourceId']);font=by_font.get(spec.get('font'))
                if not label_font_matches(spec,actual,font,extra_fonts.get(spec['sourceId'])):
                    diagnostics.append(diagnostic('LABEL_FONT_READBACK_MISMATCH',spec['sourceId'],'Saved text/font/GUID/glyph coverage differs; no fallback accepted'))
                    continue
                if spec.get('bitmapProbe'):
                    geometry=by_node.get(spec['node'],{});node=node_specs[spec['node']]
                    size=geometry.get('size',node['size']);pivot=geometry.get('pivot',node['anchor'])
                    probe=spec['bitmapProbe'];glyphs=actual.get('glyphBounds',[])
                    if instruction.get('glyphReadback')=='native-quad-padding-v1':
                        from .common import native_ink_box
                        try:
                            if actual.get('geometryProbe') not in ('saved-node','isolated-active-clone'):raise ValueError('No native geometry probe')
                            glyphs=[native_ink_box(g) for g in glyphs]
                        except (ValueError,KeyError):
                            diagnostics.append(diagnostic('BITMAP_INK_PROOF_MISSING',spec['sourceId'],'Native quad padding/geometry proof absent or invalid'))
                            continue
                    expected=[b for b in probe['boxes'] if b['width']>0 and b['height']>0]
                    if len(glyphs)!=len(expected):
                        diagnostics.append(diagnostic('BITMAP_QUAD_READBACK_MISMATCH',spec['sourceId'],'Visible glyph count differs'))
                        continue
                    origin_x=-pivot[0]*size[0]+spec['horizontalAlign']*.5*(size[0]-probe['inkRight'])
                    origin_top=(1-pivot[1])*size[1]-spec['verticalAlign']*.5*(size[1]-spec['fontSize'])
                    for actual_glyph,box in zip(glyphs,expected):
                        intended=dict(left=origin_x+box['x'],top=origin_top-box['top'],width=box['width'],height=box['height'])
                        if actual_glyph.get('unicode')!=box['unicode'] or any(not close(actual_glyph.get(key),value,.03) for key,value in intended.items()):
                            diagnostics.append(diagnostic('BITMAP_QUAD_READBACK_MISMATCH',spec['sourceId'],'Glyph origin/size differs from source metric probe'))
                            break
            if instruction.get('textLineBoxReadback')=='native-cocos-ttf-line-box-v1':
                label_rows={r['sourceId']:r for r in rb.get('labels',[])};bitmap_ids={f['id']for f in instruction.get('bitmapFonts',[])}
                for c in instruction['components']:
                    if not(c.get('convertible')and c['type']=='cc.Label'and c['overflow']in(0,3)and c['font']not in bitmap_ids):continue
                    row=label_rows.get(c['sourceId'],{});node=by_node.get(c['node'],{});line_height=c['lineHeight']or c['fontSize']
                    if (row.get('lineBoxPresent')is not True or 'NativeTextLineBox'not in node.get('componentTypes',[])or
                        not close(row.get('lineBoxLineHeight'),line_height)or not close(row.get('lineBoxExtra'),.26)):
                        diagnostics.append(diagnostic('NATIVE_TTF_LINEBOX_MISSING',c['sourceId'],'Saved native TTF line box/leading differs'))
                    current=c['node'];active=c['enabled']
                    while current is not None:
                        n=expected_nodes[current];active=active and n['active'];current=n['parent']
                    if active and(row.get('lineBoxActive')is not True or not close((node.get('size')or[0,0])[1],row.get('lineBoxHeight'),.05)):
                        diagnostics.append(diagnostic('NATIVE_TTF_LINEBOX_HEIGHT',c['sourceId'],'Active native text height differs from its measured typographic line box'))
            view_refs={v['sourceId']:v for v in rb.get('viewReferences',[])}
            for spec in instruction['components']:
                if spec['convertible'] and spec['type'] in ('cc.Sprite','cc.Label','cc.Button'):
                    binding=view_refs.get(spec['sourceId'])
                    if not binding or not binding.get('bound') or binding.get('index',-1)<0 or not binding.get('prefabFileId'):
                        diagnostics.append(diagnostic('VIEW_REFERENCE_READBACK_MISMATCH',spec['sourceId'],'Serialized native View reference or fileID is missing'))
            for required in ('Assets/Generated/Views/Candidate.prefab','Assets/Generated/Scenes/Candidate.unity'):
                required=path_for(required)
                if required not in native:
                    diagnostics.append(diagnostic('NATIVE_ARTIFACT_MISSING',required,'No saved native artifact hash'))
            from ..assets.animation import verify_native
            diagnostics.extend(verify_native(instruction.get('animations',[]),rb.get('animations',[]),native))
            editor='partial' if rb.get('diagnostics') else 'pass'
            if any(d['code']!='EDITOR_NOT_RUN' for d in diagnostics):editor='fail'
    for item in m['files']:
        path=inside(root,item['path'])
        expected=native.get(item['path']) if level=='editor' and item['path'].endswith('.meta') else item['sha256']
        if expected is None: expected=item['sha256']
        changed=not path.is_file() or fingerprint(path)!=expected
        if changed and level=='editor' and item['path']=='ProjectSettings/ProjectVersion.txt' and path.is_file():
            from .common import normalized_unity_version
            changed=not normalized_unity_version(read(path),'6000.6.2f1')
        if changed:
            diagnostics.append(diagnostic('GENERATED_FILE_CHANGED',item['path'],'Missing or modified generated file'))
    from ..identities import verify as verify_assigned
    identity_gaps=verify_assigned(root,m);diagnostics.extend(identity_gaps)
    if identity_gaps and editor in ('pass','partial'):editor='fail'
    guids={}
    for path in (root/'Assets').rglob('*.meta'):
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.startswith('guid: '):
                value=line[6:]
                if value in guids:
                    diagnostics.append(diagnostic('DUPLICATE_TARGET_GUID',str(path.relative_to(root)),'GUID duplicates '+guids[value]))
                guids[value]=str(path.relative_to(root))
    instruction=load(read(root/path_for('Assets/Monkey/Editor/import-plan.json'),max_bytes=128*1024*1024),max_nodes=8_000_000)
    for item in instruction['textures']+instruction['assets']:
        if not inside(root,item['path']).is_file():
            diagnostics.append(diagnostic('TARGET_REFERENCE_MISSING',item['path'],'Import resource does not exist'))
    adapter=root/path_for('Assets/Monkey/Editor/MonkeyImporter.cs')
    if not adapter.is_file() or list((root/'Assets').rglob('ir.json')):
        diagnostics.append(diagnostic('TARGET_LAYOUT_INVALID','Assets','Missing Editor adapter or runtime IR found'))
    out=new_output(output,[root])
    result=dict(schemaVersion=1,toolVersion=__version__,candidateManifestSha256=fingerprint(root/'manifest.json'),
                diagnostics=diagnostics,staticValidation='conflict' if any(d['code'] in ('GENERATED_FILE_CHANGED','DUPLICATE_TARGET_GUID','TARGET_REFERENCE_MISSING','TARGET_LAYOUT_INVALID','NATIVE_FILE_CHANGED','ASSIGNED_NATIVE_IDENTITY_CHANGED') for d in diagnostics) else 'pass',
                editorValidation=editor,visualValidation='not_run',businessValidation='not_run')
    write_json(out/'verification.json',result)
    return finish(out,result)


def handoff(candidate, output):
    from ..sources.containers import fingerprint
    root=safe(candidate)
    package=load(read(root/'Analysis/handoff.json'))
    out=new_output(output,[root])
    package['candidateManifestSha256']=fingerprint(root/'manifest.json')
    write_json(out/'handoff.json',package)
    lines=['# AI接续工作包','', '这是候选工程，Editor/原版画面对照/业务分别按验证记录处理。',
           '仅修改目标的 Manual/manual 区；生成区需要明确解除所有权后才可手改。','']
    for task in package['tasks']:
        lines.extend(['## '+task.get('moduleName',task.get('module','Module'))+' / '+task.get('rootCause',task['taskId']),'',
                      '任务：'+task['taskId'],
                      '来源：'+str(task['sourceRefs']),
                      '目标：'+', '.join(task['generatedTargets']),
                      '根因：'+task.get('rootCause','unknown')+'；详细诊断 '+str(len(task['gaps']))+' 条，见同目录 handoff.json。',
                      '摘要：'+'; '.join(dict.fromkeys(g['code'] for g in task['gaps'])),
                      '验证：'+', '.join(task['verificationScope']),''])
    (out/'HANDOFF.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return finish(out,dict(schemaVersion=1,diagnostics=[],tasks=len(package['tasks']),toolVersion=__version__))
