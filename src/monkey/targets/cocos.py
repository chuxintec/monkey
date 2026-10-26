"""Creator 3.8.8 candidate asset emitter; native objects are saved only by its Editor."""
from importlib.resources import files
from pathlib import Path
import uuid
from .. import __version__
from ..io import safe, inside, read, load, sha, write_json, new_output, finish, diagnostic, stage_document, stage_bytes,stage_manifest
from ..sources.compiled import fail
from .common import input_ir, tasks,native_color_nodes
from ..layout import standard
from ..layout.standard import VERSION
from ..layout.standard import find_analysis

PROFILE='cocos-3.8.8'


def identity(namespace,sid):
    return str(uuid.uuid5(uuid.NAMESPACE_URL,'monkey/'+namespace+'/creator-3.8.8/'+sid))


def meta(uid,importer,version,user=None):
    return dict(ver=version,uuid=uid,importer=importer,imported=False,files=[],subMetas={},userData=user or {})


def bitmap_text(font,atlas_name,face="MonkeySourceBitmap"):
    # Normalized sourceRect is top-origin; metrics stores the logical point-size bearing.
    lines=[f'info face="{face}" size={font["pointSize"]} bold=0 italic=0 unicode=1',
           f'common lineHeight={font["lineHeight"]} base={font["pointSize"]} scaleW={font["atlasSize"][0]} scaleH={font["atlasSize"][1]} pages=1 packed=0',
           f'page id=0 file="{atlas_name}"',f'chars count={len(font["glyphs"])}']
    for g in font['glyphs']:
        x,y,w,h=g['sourceRect'];_,_,bearing_x,bearing_y,advance=g['metrics']
        lines.append(f'char id={g["unicode"]} x={x} y={y} width={w} height={h} xoffset={bearing_x} yoffset={font["pointSize"]-bearing_y} xadvance={advance} page=0 chnl=15')
    lines.append(f'kernings count={len(font["kernings"])}')
    lines += [f'kerning first={k["first"]} second={k["second"]} amount={k["advance"]}' for k in font['kernings']]
    return ('\n'.join(lines)+'\n').encode()


def plan(ir_path,namespace,output,bindings_path=None,animation_selection=None,layout=None):
    path,ir,bindings,receipt,resource,resolve=input_ir(ir_path,bindings_path)
    if ir.get('sourceProfile')in ('generic-image-resources-v1','egret-custom-resource-plist-v1'):fail('SOURCE_TARGET_UNSUPPORTED',str(ir_path),'Non-Cocos sources target Unity 6 only')
    from ..layout import LayoutPlanner
    overrides,overrides_sha=layout or ({},None)
    naming=LayoutPlanner('creator',ir.get('sourceNames'),overrides)
    planned={'sprite':'sprite','ttf':'cc.TTFFont','json':'cc.JsonAsset','audio':'cc.AudioClip'}
    # Creator trims natively from the original image, so no untrimmed duplicate is emitted (PROJECT-SPEC 5.4).
    naming.reserve([(f['sourceId'],'sprite','.png','',None,None) for f in ir['spriteFrames']]
        +[(a['sourceId'],a['kind'],Path(a['path']).suffix if a['kind']=='cc.AudioClip' else {'cc.TTFFont':'.ttf','cc.JsonAsset':'.json'}[a['kind']],'',None,None) for a in ir['assets'] if a['kind'] in ('cc.TTFFont','cc.JsonAsset','cc.AudioClip')]
        +[r for f in ir.get('bitmapFonts',[]) for r in ((f['sourceId']+'@atlas','bitmap-atlas','.png','',None,None),(f['sourceId'],'bitmap','.fnt','',None,None))])
    diagnostics=list(ir['diagnostics']);assets=[];copies=[]
    def add(sid,relative,kind,suffix,**fields):
        raw=resource(relative);uid=identity(namespace,sid);target=naming.path(sid,fields.get('role')=='bitmap-atlas-page' and 'bitmap-atlas' or planned[kind],suffix)
        item=dict(sourceId=sid,uuid=uid,path=target,kind=kind,sha256=sha(raw),**fields)
        assets.append(item);copies.append(dict(source=relative,target=target,sha256=sha(raw)))
        return item
    for f in ir['spriteFrames']:
        # Already physically unrotated pixels; no raw atlas rotation is guessed in target metadata.
        add(f['sourceId'],f['originalImage'],'sprite','.png',size=f['rect'][2:4],trimOrigin=f['trimOrigin'],originalSize=f['originalSize'],
            offset=f['offset'],border=f['capInsets'],subresource='spriteFrame')
    for a in ir['assets']:
        if a['kind']=='cc.TTFFont':add(a['sourceId'],a['path'],'ttf','.ttf',fontCoverage=a.get('fontCoverage'))
        elif a['kind']=='cc.JsonAsset':add(a['sourceId'],a['path'],'json','.json')
        elif a['kind']=='cc.AudioClip':add(a['sourceId'],a['path'],'audio',Path(a['path']).suffix)
        else:diagnostics.append(diagnostic('ASSET_HANDOFF',a['sourceId'],'Creator native subset has no mapping for '+a['kind'],a['sourceId']))
    font_by_id={}
    for f in ir.get('bitmapFonts',[]):
        atlas=add(f['sourceId']+'@atlas',f['atlasImage'],'sprite','.png',size=f['atlasSize'],originalSize=f['atlasSize'],
                  offset=[0,0],border=[0,0,0,0],subresource='spriteFrame',role='bitmap-atlas-page')
        uid=identity(namespace,f['sourceId']);target=naming.path(f['sourceId'],'bitmap','.fnt')
        raw=bitmap_text(f,Path(atlas['path']).name,Path(target).stem)
        assets.append(dict(sourceId=f['sourceId'],uuid=uid,path=target,kind='bitmap',sha256=sha(raw),
                           atlas=atlas['sourceId'],pointSize=f['pointSize'],glyphCount=len(f['glyphs']),kerningCount=len(f['kernings'])))
        copies.append(dict(source=None,target=target,sha256=sha(raw),text=raw.decode()))
        font_by_id[f['sourceId']]=f
    asset_by_id={a['sourceId']:a for a in assets};components=[]
    supported={'cc.Sprite','cc.Label','cc.Widget','cc.Mask','cc.ScrollView','cc.Layout','cc.Button','cc.LabelOutline'}
    materials={m['sourceId'] for m in ir.get('materials',[]) if m['nativeRole']=='standard-ugui'}
    node_ids={n['sourceId'] for n in ir['nodes']};source_nodes={n['sourceId']:n for n in ir['nodes']}
    for src in ir['components']:
        c=dict(src);sid=c['sourceId'];c['convertible']=c['type'] in supported and c.get('node') in node_ids
        if c.get('supported') is False:
            c['convertible']=False;c['nativeType']=None
            diagnostics.append(diagnostic('SOURCE_COMPONENT_PROFILE_HANDOFF',c['sourceId'],'Source component semantics are not implemented for this profile',c['sourceId']))
            components.append(c);continue
        if sid in bindings:c.update(font=bindings[sid]['font'],bold=bindings[sid].get('syntheticBold',False))
        for field in ['font','spriteFrame']:
            if field in c:c[field]=resolve(c[field])
        def gap(code,message):
            c['convertible']=False;diagnostics.append(diagnostic(code,sid,message,sid))
        if any(resolve(m) not in materials for m in c.get('materials',[])):gap('CUSTOM_MATERIAL_HANDOFF','Unrecognized source material')
        if c['type']=='cc.Sprite':
            if c['mode'] not in (0,1,2) or c['sizeMode'] not in (0,1,2):gap('SPRITE_SUBSET_UNSUPPORTED','Unknown mode')
            if c.get('spriteFrame') is not None and c['spriteFrame'] not in asset_by_id:gap('MISSING_SPRITE','SpriteFrame absent')
            if c.get('spriteFrame') is None:
                c['needsSpriteBinding']=True;diagnostics.append(diagnostic('SOURCE_SPRITE_UNBOUND',sid,'Keep native Sprite disabled pending real binding',sid))
            frame=asset_by_id.get(c.get('spriteFrame'))
            if c['convertible']:c.update(nativeSizeMode=c['sizeMode'],sizingPolicy='native-sprite-sizing-v1')
        elif c['type']=='cc.Label':
            font=asset_by_id.get(c.get('font'))
            if not font or font['kind'] not in ('ttf','bitmap'):gap('FONT_NOT_CONVERTIBLE','No matching original font; no system fallback')
            elif font['kind']=='ttf':
                from ..assets.ttf import missing
                if missing(font['fontCoverage'],c['text']):gap('SOURCE_FONT_GLYPHS_MISSING','Missing original font glyphs')
            else:
                available={g['unicode'] for g in font_by_id[c['font']]['glyphs']}
                if any(ord(ch) not in available for ch in c['text'] if ch not in '\r\n'):gap('SOURCE_FONT_GLYPHS_MISSING','Bitmap lacks glyphs')
                c['bold']=False
            if c['overflow']not in(0,1,2,3):gap('LABEL_SUBSET_UNSUPPORTED','Unknown overflow mode')
            if c['convertible']:c.update(nativeOverflow=c['overflow'],sizingPolicy='native-label-sizing-v1')
            diagnostics.append(diagnostic('CREATOR_TEXT_METRICS_NOT_VERIFIED',sid,'Original font selected; cross-version glyph layout needs real source comparison',sid))
        elif c['type']=='cc.Widget':
            if c['flags']&~63 or c.get('alignMode',1)not in(0,1,2):gap('WIDGET_SUBSET_UNSUPPORTED','Unknown flags or align policy')
            c.setdefault('center',[0,0]);c.setdefault('centerAbsolute',[True,True])
        elif c['type']=='cc.Mask':
            if c['maskType']!=0 or c['inverted']:gap('MASK_SUBSET_UNSUPPORTED','Only plain rectangle')
        elif c['type']=='cc.ScrollView':
            if c.get('content') not in {n['sourceId'] for n in ir['nodes']}:gap('MISSING_SCROLL_CONTENT','Scroll content absent')
            if c['horizontal'] or c['vertical']:gap('SCROLL_SUBSET_UNSUPPORTED','Dynamic scrolling physics not yet verified')
        elif c['type']=='cc.Button':
            if c['transition'] not in (0,3) or c['target'] not in (None,c['node']):gap('BUTTON_SUBSET_UNSUPPORTED','Only none/scale self-target')
            if c['events']:diagnostics.append(diagnostic('BUTTON_BUSINESS_UNBOUND',sid,'Original click handlers remain native AI work',sid))
        elif c['type']=='cc.LabelOutline':
            if not any(x['type']=='cc.Label' and x['node']==c['node'] for x in ir['components']):gap('MISSING_OUTLINE_LABEL','Outline has no Label')
        elif c['type']=='cc.Layout':
            if c['layoutType']not in(0,1,2,3)or c['resize']not in(0,1,2)or c.get('constraint',0)not in(0,1,2):gap('LAYOUT_SUBSET_UNSUPPORTED','Unknown native Layout mode')
        if not c['convertible']:diagnostics.append(diagnostic('COMPONENT_HANDOFF',sid,'Unsupported native mapping: '+c['type'],sid))
        c['nativeType']=('cc.Label' if c['type']=='cc.LabelOutline' else c['type']) if c['convertible'] else None;components.append(c)
    for c in components:
        if c['type']=='cc.LabelOutline' and c['convertible'] and not any(x['type']=='cc.Label' and x['node']==c['node'] and x['convertible'] for x in components):
            c['convertible']=False;c['nativeType']=None
            diagnostics.append(diagnostic('MISSING_OUTLINE_LABEL',c['sourceId'],'Label dependency could not be converted',c['sourceId']))
    from .prefabs import plan_prefabs,native_relationships
    prefabs,prefab_gaps=plan_prefabs(ir,components)
    diagnostics.extend(prefab_gaps)
    prefabs,instances=native_relationships(ir,prefabs,components)
    roots={p['sourceId']:p['root']for p in prefabs}
    for link in instances:
        if roots.get(link['owner'])==link['root']:
            fail('CREATOR_ROOT_PREFAB_INHERITANCE_PENDING',link['root'],'Root inheritance needs a dedicated Creator asset contract; nested instances are supported, Unity emits a native Variant')
    by_node={n['sourceId']:n for n in ir['nodes']}
    naming.reserve([(prefab['sourceId'],'prefab','.prefab','',None,None) for prefab in prefabs])
    for prefab in prefabs:
        prefab['path']=naming.path(prefab['sourceId'],'prefab','.prefab')
        prefab['rootNamePolicy']='creator-asset-basename-v1'
        prefab['sourceRootName']=by_node[prefab['root']]['name']
        prefab['nativeRootName']=Path(prefab['path']).stem
    from .common import reject_layout_conflicts
    diagnostics.extend(reject_layout_conflicts(components))
    from ..assets.animation import plan_clips
    animations,animation_gaps=plan_clips(ir,namespace,PROFILE,animation_selection,naming)
    if animation_selection:
        unselected={c['sourceId'] for c in ir.get('animationClips',[]) if c['sourceId'] not in animation_selection}
        diagnostics=[d for d in diagnostics if d.get('sourceId') not in unselected]
    diagnostics.extend(animation_gaps)
    out=new_output(output,[path.parent]);(out/'resources').mkdir()
    for i,c in enumerate(copies):
        raw=c.pop('text',None)
        raw=raw.encode() if raw is not None else resource(c['source'])
        dest=f'resources/{i:04d}'+Path(c['target']).suffix;(out/dest).write_bytes(raw);c['source']=dest
    from ..creator_geometry import renderer_budget
    render_budget,tile_gaps=renderer_budget(ir['nodes'],components,assets)
    diagnostics.extend(diagnostic('TILED_GEOMETRY_UNSUPPORTED',sid,message,sid) for sid,message in tile_gaps)
    result=dict(schemaVersion=1,toolVersion=__version__,targetProfile=PROFILE,namespace=namespace,projectLayout=VERSION,layoutOverridesSha256=overrides_sha,
        scopeMode=ir.get('scopeMode','asset-selection'),
        sourceIrSha256=sha(stage_bytes(path)),sourceManifestSha256=ir['sourceManifestSha256'],sourceManifestPath=ir.get('sourceManifestPath'),
        sourceRoots=ir.get('sourceRoots',{}),sourceLocations=ir.get('sourceLocations',{}),bindings=receipt,
        designSize=[750,1334],rendererBudget=render_budget,assets=assets,copies=copies,animations=animations,sourcePrefabs=prefabs,prefabInstances=instances,naming=naming.report(),nodes=native_color_nodes(ir['nodes'],components),components=components,
        diagnostics=diagnostics,editorValidation='not_run',subresourceValidation='pending-native-import')
    write_json(out/'plan.json',result);return finish(out,result)


def export(plan_path,output):
    path=safe(plan_path);p=stage_document(path)
    if p.get('targetProfile')!=PROFILE or p.get('schemaVersion')!=1:fail('UNSUPPORTED_PLAN',str(path),'Expected Creator schema 1')
    # Preflight everything before output creation.
    for c in p['copies']:
        if not c['target'].startswith(standard.ROOTS['creator']['content']+'/') or sha(read(inside(path.parent,c['source'])))!=c['sha256']:
            fail('SOURCE_CHANGED',c['target'],'Invalid plan resource')
    out=new_output(output,[path.parent,*p.get('sourceRoots',{}).values()])
    for folder in ['assets',standard.ROOTS['creator']['conversion'],'Analysis']:
        (out/folder).mkdir(parents=True,exist_ok=True)
    by_path={a['path']:a for a in p['assets']};by_id={a['sourceId']:a for a in p['assets']}
    for c in p['copies']:
        target=inside(out,c['target']);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(read(inside(path.parent,c['source'])))
        a=by_path[c['target']]
        if a['kind']=='sprite':m=meta(a['uuid'],'image','1.0.27',dict(type='sprite-frame',fixAlphaTransparencyArtifacts=False,hasAlpha=True))
        elif a['kind']=='ttf':m=meta(a['uuid'],'ttf-font','1.0.1')
        elif a['kind']=='json':m=meta(a['uuid'],'json','2.0.1')
        elif a['kind']=='audio':m=meta(a['uuid'],'audio-clip','1.0.0',dict(downloadMode=0))
        else:m=meta(a['uuid'],'bitmap-font','1.0.6',dict(fontSize=a['pointSize'],textureUuid=by_id[a['atlas']]['uuid']))
        write_json(Path(str(target)+'.meta'),m)
    project_id=identity(p['namespace'],'project')
    write_json(out/'package.json',dict(name='monkey-native-candidate',version='3.8.8',uuid=project_id,creator=dict(version='3.8.8')))
    if p.get('rendererBudget',{}).get('macroConfig',{}).get('BATCHER2D_MEM_INCREMENT',144)>144:
        write_json(out/'settings/v2/packages/engine.json',dict(__version__='1.0.12',macroConfig=p['rendererBudget']['macroConfig']))
        (out/'Docs').mkdir(exist_ok=True)
        kib=p['rendererBudget']['macroConfig']['BATCHER2D_MEM_INCREMENT']
        (out/'Docs/RENDERER-REQUIREMENTS.md').write_text(
            '# Creator renderer requirements\n\nThis isolated 3.8.8 candidate requires '
            f'BATCHER2D_MEM_INCREMENT={kib} KiB for its original Tiled Sprite geometry. '
            'The candidate-local settings/v2/packages/engine.json records the requirement; '
            'the Editor importer also applies it in this owned Editor process.\n\n'
            'Copying assets alone does not transfer project settings. A development-project consumer must '
            'review and explicitly merge this requirement, preserving its other engine settings. '
            'Do not overwrite a development project settings file or assume asset adoption applies the macro. '
            'Preview/build/Player validation is separate from the Editor allocation proof.\n',encoding='utf-8')
    ext=out/'extensions/monkey-import'
    for name in ['main.js','scene.js']:(ext/name).write_bytes(files('monkey.targets').joinpath('Creator'+('Main.js' if name=='main.js' else 'Scene.js')).read_bytes())
    (ext/'execution.js').write_bytes(files('monkey.targets').joinpath('CreatorExecution.js').read_bytes())
    (ext/'numeric-code.js').write_bytes(files('monkey.targets').joinpath('CreatorNumericCode.js').read_bytes())
    (ext/'prefab.js').write_bytes(files('monkey.targets').joinpath('CreatorPrefab.js').read_bytes())
    (ext/'prefab-instances.js').write_bytes(files('monkey.targets').joinpath('CreatorPrefabInstances.js').read_bytes())
    (ext/'dynamic-ui.js').write_bytes(files('monkey.targets').joinpath('CreatorDynamicUi.js').read_bytes())
    (ext/'sprite-metadata.js').write_bytes(files('monkey.targets').joinpath('CreatorSpriteMetadata.js').read_bytes())
    (ext/'batch.js').write_bytes(files('monkey.targets').joinpath('CreatorBatch.js').read_bytes())
    (ext/'jobs.js').write_bytes(files('monkey.targets').joinpath('CreatorJobs.js').read_bytes())
    (ext/'animation.js').write_bytes(files('monkey.targets').joinpath('CreatorAnimation.js').read_bytes())
    write_json(ext/'package.json',dict(package_version=2,version='0.2.0',name='monkey-import',main='./main.js',
        contributions=dict(scene=dict(script='./scene.js'),menu=[dict(path='Monkey',label='Import isolated candidate',message='import-candidate')],
                           messages={'import-candidate':dict(methods=['importCandidate'])})))
    write_json(ext/'import-plan.json',{k:p[k] for k in ['schemaVersion','targetProfile','designSize','assets','nodes','components'] }|dict(rendererBudget=p.get('rendererBudget'),projectUuid=project_id,animations=p.get('animations',[]),sourcePrefabs=p.get('sourcePrefabs',[]),prefabInstances=p.get('prefabInstances',[]),prefabRelationshipReadback='creator-native-fileid-v1',uiGeometryReadback='native-ui-layout-roundtrip-v1',sceneGeometryReadback='full-local-v1',bitmapPageReadback='sprite-frame-v1',spriteMeshReadback='native-rect-mesh-v1',outputPaths=standard.creator_output_paths()))
    from .dynamic_ui import driven_fields
    instruction_path=ext/'import-plan.json';instruction=load(instruction_path.read_bytes())
    instruction['uiStateProbeVersion']=2
    from .dynamic_ui import probe_sources
    instruction['uiProbeSources']=probe_sources(instruction)
    instruction['uiDrivenFields']={sid:{key:sorted(axes)for key,axes in fields.items()}for sid,fields in driven_fields(instruction).items()}
    write_json(instruction_path,instruction)
    from ..assets.animation import module_report
    write_json(find_analysis(out,'animation-module.json'),module_report(p.get('animations',[])))
    write_json(find_analysis(out,'source-map.json'),dict(assets=p['assets'],sourcePrefabs=p.get('sourcePrefabs',[]),nodes=[dict(sourceId=n['sourceId'],target=standard.creator('previewScene')) for n in p['nodes']],
        components=[dict(sourceId=c['sourceId'],node=c['node'],nativeType=c['nativeType']) for c in p['components']],
        sourceRoots=p['sourceRoots'],sourceLocations=p['sourceLocations'],subresources='actual UUIDs require native importer readback'))
    handoff_tasks=tasks(p['components'],[d for d in p['diagnostics'] if not d['code'].startswith('ANIMATION_')],standard.creator('previewScene'),'assets/')
    normalized=[dict(sourceId=s['sourceId'],path=s['path'],sourceRootName=s['sourceRootName'],nativeRootName=s['nativeRootName'])
                for s in p.get('sourcePrefabs',[]) if s.get('rootNamePolicy')=='creator-asset-basename-v1' and s['sourceRootName']!=s['nativeRootName']]
    if normalized:
        handoff_tasks.append(dict(taskId='creator-prefab-root-names',module='creator-prefabs',rootCause='native-prefab-root-name-compatibility',
            sourceRefs=[s['sourceId'] for s in normalized],gaps=[dict(code='CREATOR_PREFAB_ROOT_NAME_POLICY',
                message='Creator normalizes root names to asset basenames. Source names remain in Scene/source-map; review name-dependent business code.')],
            generatedTargets=['Analysis/Mappings/source-map.json'],allowedPaths=['assets/'],verificationScope=['native root-name policy','name-dependent business code'],rootNames=normalized))
    if p.get('animations') or any(d['code'].startswith('ANIMATION_') for d in p['diagnostics']):
        from ..assets.animation import handoff_task
        handoff_tasks.append(handoff_task(p['animations'],p['diagnostics']))
    write_json(find_analysis(out,'handoff.json'),dict(schemaVersion=1,tasks=handoff_tasks,
        verification=dict(static='pending',editor='not_run',visual='not_run',business='not_run')))
    if p['bindings']:write_json(find_analysis(out,'font-bindings.json'),p['bindings'])
    (out/'README.md').write_text('Creator 3.8.8 isolated candidate. Layout '+VERSION+' (monkey docs/PROJECT-SPEC.md).\nOpen only in an authorized resource window.\nRun Monkey/Import isolated candidate once after assets import. Existing outputs are refused.\nNative scene and child UUIDs require Editor; no source engine interpreter ships.\n')
    write_json(find_analysis(out,'name-map.json'),p.get('naming',{}))
    report=dict(schemaVersion=1,toolVersion=__version__,targetProfile=PROFILE,namespace=p['namespace'],projectUuid=project_id,projectLayout=VERSION,
        scopeMode=p.get('scopeMode','asset-selection'),rendererBudget=p.get('rendererBudget'),
        sourceManifestSha256=p['sourceManifestSha256'],sourceRoots=p['sourceRoots'],planSha256=sha(stage_bytes(path)),diagnostics=p['diagnostics'],
        editorValidation='not_run',visualValidation='not_run',businessValidation='not_run',subresourceValidation='pending-native-import')
    write_json(find_analysis(out,'candidate.json'),report);return finish(out,report)


def verify(candidate,output,level='static'):
    root=safe(candidate);m=stage_manifest(root);diagnostics=[]
    from ..sources.containers import fingerprint
    if m.get('targetProfile')!=PROFILE:fail('UNSUPPORTED_CANDIDATE',str(root),'Expected Creator profile')
    native={};editor='not_run'
    if level=='editor':
        rb_path=find_analysis(root,'editor-readback.json')
        if not rb_path.exists():diagnostics.append(diagnostic('EDITOR_NOT_RUN',str(rb_path),'Run native importer in declared Creator first'))
        else:
            rb=load(read(rb_path,max_bytes=128*1024*1024),max_nodes=8_000_000);native={f['path']:f['sha256'] for f in rb.get('nativeFiles',[])}
            plan=load(read(root/'extensions/monkey-import/import-plan.json',max_bytes=128*1024*1024),max_nodes=8_000_000)
            expected_assets={a['sourceId']:a for a in plan['assets']}
            actual_assets={a['sourceId']:a for a in rb.get('assets',[])}
            json_assets={a['sourceId']:a for a in rb.get('jsonAssets',[])}
            audio_assets={a['sourceId']:a for a in rb.get('audioAssets',[])}
            good=rb.get('creatorVersion')=='3.8.8' and rb.get('projectUuid')==m['projectUuid'] and rb.get('manifestSha256')==fingerprint(root/'manifest.json')
            good=good and set(expected_assets)==set(actual_assets) and rb.get('nodeCount')==len(plan['nodes'])
            from ..creator_geometry import verify_tiled_readback
            if not verify_tiled_readback(plan,rb):
                good=False;diagnostics.append(diagnostic('TILED_NATIVE_READBACK_MISMATCH','CreatorScene','Tiled mesh allocation/budget/topology/identity readback differs'))
            for sid,a in expected_assets.items():
                actual=actual_assets.get(sid,{})
                good=good and actual.get('uuid')==a['uuid'] and (a['kind']!='sprite' or bool(actual.get('spriteFrameUuid')))
                if a['kind']=='json':
                    actual_json=json_assets.get(sid,{})
                    good=good and actual_json.get('uuid')==a['uuid'] and 'value' in actual_json and actual_json['value']==load(read(root/a['path']))
                if a['kind']=='audio':
                    audio=audio_assets.get(sid,{})
                    if audio.get('uuid')!=a['uuid'] or not isinstance(audio.get('duration'),(int,float)):
                        good=False;diagnostics.append(diagnostic('AUDIO_READBACK_MISMATCH',sid,'Expected a native AudioClip readback'))
            labels={v['sourceId']:v for v in rb.get('labels',[])}
            if plan.get('bitmapPageReadback')=='sprite-frame-v1':
                font_pages={f['sourceId']:f for f in rb.get('fontPages',[])}
                for font in (a for a in plan['assets'] if a['kind']=='bitmap'):
                    page=font_pages.get(font['sourceId'],{});atlas=expected_assets[font['atlas']];native_atlas=actual_assets.get(font['atlas'],{})
                    if (page.get('fontUuid')!=font['uuid'] or page.get('spriteFrameUuid')!=native_atlas.get('spriteFrameUuid') or
                            page.get('textureUuid')!=native_atlas.get('textureUuid') or page.get('rect')!=[0,0,*atlas['size']]):
                        good=False;diagnostics.append(diagnostic('BITMAP_PAGE_READBACK_MISMATCH',font['sourceId'],'Native BitmapFont page identity/texture/rect differs'))
            for c in plan['components']:
                if c['convertible'] and c['type']=='cc.Label':
                    actual=labels.get(c['sourceId'],{})
                    good=good and actual.get('text')==c['text'] and actual.get('fontUuid')==expected_assets[c['font']]['uuid']
            expected_components={c['sourceId'] for c in plan['components'] if c['convertible']}
            good=good and {c['sourceId'] for c in rb.get('components',[])}==expected_components
            good=good and {n['sourceId'] for n in rb.get('nodes',[])}=={n['sourceId'] for n in plan['nodes']}
            if plan.get('sceneGeometryReadback')=='full-local-v1':
                from .unity import node_geometry_matches
                saved_nodes={n['sourceId']:n for n in rb.get('nodes',[])}
                from .dynamic_ui import expectations,verify_probes
                probe_gaps=verify_probes(plan,rb.get('dynamicUiProbes'));diagnostics.extend(probe_gaps)
                if probe_gaps:good=False
                scene_expected,ui_gaps=expectations(plan,rb.get('nativeInitialNodes'),'CreatorScene');diagnostics.extend(ui_gaps)
                if ui_gaps:good=False
                for spec in scene_expected:
                    actual_node=saved_nodes.get(spec['sourceId'])
                    if not node_geometry_matches(actual_node,spec,True) or ('sourceLayer'in spec and actual_node.get('sourceLayer')!=spec['sourceLayer']):
                        good=False;diagnostics.append(diagnostic('SCENE_GEOMETRY_MISMATCH',spec['sourceId'],'Saved native Scene transform differs from the frozen source plan'))
            def near(actual,expected):
                return isinstance(actual,list) and len(actual)==len(expected) and all(type(x) in (int,float) and abs(x-y)<.001 for x,y in zip(actual,expected))
            frames={f['sourceId']:f for f in rb.get('frames',[])}
            for sid,a in expected_assets.items():
                if a['kind']=='sprite':
                    f=frames.get(sid,{})
                    expected=dict(uuid=actual_assets.get(sid,{}).get('spriteFrameUuid'),textureUuid=actual_assets.get(sid,{}).get('textureUuid'),
                                  rect=a.get('trimOrigin',[0,0])+a['size'],originalSize=a['originalSize'],offset=a['offset'],border=a['border'])
                    mismatches=[key for key,value in expected.items() if (f.get(key)!=value if key in ('uuid','textureUuid') else not near(f.get(key),value))]
                    if plan.get('spriteMeshReadback')=='native-rect-mesh-v1':
                        w,h=a['size'];tw,th=a['originalSize'];x,y=a.get('trimOrigin',[0,0]);mesh=f.get('mesh')or{}
                        expected_mesh=dict(rawPosition=[-w/2,-h/2,0,w/2,-h/2,0,-w/2,h/2,0,w/2,h/2,0],indexes=[0,1,2,2,1,3],
                            uv=[x,th-y,x+w,th-y,x,th-y-h,x+w,th-y-h],nuv=[x/tw,(th-y-h)/th,(x+w)/tw,(th-y-h)/th,x/tw,(th-y)/th,(x+w)/tw,(th-y)/th])
                        for key,value in expected_mesh.items():
                            actual=mesh.get(key)
                            if not isinstance(actual,list)or len(actual)!=len(value)or any(type(v)not in(int,float)or abs(v-e)>1e-6 for v,e in zip(actual,value)):
                                good=False;diagnostics.append(diagnostic('SPRITE_NATIVE_MESH_MISMATCH',sid,'Saved native RECT mesh '+key+' differs'))
                    if mismatches:
                        good=False;diagnostics.append(diagnostic('SPRITE_READBACK_MISMATCH',sid,
                            'Saved native sprite differs: '+str({key:dict(expected=expected[key],actual=f.get(key)) for key in mismatches})))
            good=good and all(isinstance(n.get('nodeUuid'),str) and n['nodeUuid'] for n in rb.get('nodes',[]))
            good=good and all(isinstance(c.get('componentUuid'),str) and c['componentUuid'] for c in rb.get('components',[]))
            from ..code_validation import numeric as verify_numeric
            code_gaps=verify_numeric(plan['components'],rb.get('numericCodeBindings'),'cocos','scene',rb.get('numericCodeExercise',[]))
            if code_gaps:good=False;diagnostics.extend(code_gaps)
            good=good and standard.locate(m,'previewScene','creator') in native and bool(rb.get('sceneUuid'))
            actual_prefabs={v['sourceId']:v for v in rb.get('sourcePrefabs',[])}
            expected_prefabs={v['sourceId']:v for v in plan.get('sourcePrefabs',[])}
            if set(actual_prefabs)!=set(expected_prefabs):good=False
            for sid,spec in expected_prefabs.items():
                actual=actual_prefabs.get(sid,{})
                source_nodes=set(spec['nodes']);code_specs=[c for c in plan['components']if c.get('node')in source_nodes]
                code_gaps=verify_numeric(code_specs,actual.get('numericCodeBindings'),'cocos',sid)
                if code_gaps:good=False;diagnostics.extend(code_gaps)
                if plan.get('uiGeometryReadback')=='native-ui-layout-roundtrip-v1':
                    from .dynamic_ui import expectations
                    _,ui_gaps=expectations(plan,actual.get('nativeInitialNodes'),sid,[n for n in plan['nodes']if n['sourceId']in source_nodes])
                    if ui_gaps:good=False;diagnostics.extend(ui_gaps)
                for mismatch in actual.get('geometryMismatches',[]):
                    good=False
                    diagnostics.append(diagnostic('PREFAB_GEOMETRY_MISMATCH',mismatch.get('sourceId',sid),
                        'Saved native geometry differs: '+str(mismatch)))
                expected_components={c['sourceId'] for c in plan['components'] if c['convertible'] and c['node'] in set(spec['nodes'])}
                valid=(set(actual.get('components',[]))==expected_components and actual.get('path')==spec['path'] and bool(actual.get('uuid')) and
                       actual.get('nodeCount')==spec['nodeCount'] and actual.get('savedReloaded') is True and
                       actual.get('geometryVerified') is True and actual.get('referencesVerified') is True and spec['path'] in native)
                if spec.get('rootNamePolicy')=='creator-asset-basename-v1':
                    valid=valid and all(actual.get(key)==spec[key] for key in ['rootNamePolicy','sourceRootName','nativeRootName'])
                if not valid:
                    good=False;diagnostics.append(diagnostic('SOURCE_PREFAB_NOT_VERIFIED',sid,'Independent Creator prefab save/reload evidence absent or inconsistent'))
            from .prefabs import verify_native_relationships
            native_ids={sid:a.get('uuid')for sid,a in actual_prefabs.items()}
            relation_gaps=verify_native_relationships(plan.get('prefabInstances',[]),plan.get('sourcePrefabs',[]),rb.get('prefabInstances',[]),'CreatorScene',native_ids,'uuid')
            for sid,a in actual_prefabs.items():
                relation_gaps.extend(verify_native_relationships([x for x in plan.get('prefabInstances',[])if x['owner']==sid],plan.get('sourcePrefabs',[]),a.get('prefabInstances',[]),sid,native_ids,'uuid'))
            if relation_gaps:good=False;diagnostics.extend(relation_gaps)
            from ..assets.animation import verify_native
            motion_gaps=verify_native(plan.get('animations',[]),rb.get('animations',[]),native);diagnostics.extend(motion_gaps);good=good and not motion_gaps
            if not good:diagnostics.append(diagnostic('EDITOR_READBACK_FAILED',str(rb_path),'Native identities/counts/version differ'))
            editor='pass' if good else 'fail'
    for f in m['files']:
        if f.get('owner')=='manual':continue
        target=inside(root,f['path']);expected=native.get(f['path'],f['sha256'])
        if not target.is_file() or fingerprint(target)!=expected:diagnostics.append(diagnostic('GENERATED_FILE_CHANGED',f['path'],'Generated file differs'))
    for relative,h in native.items():
        prefixes=('assets/','Analysis/')
        if not relative.startswith(prefixes):fail('UNSAFE_NATIVE_FILE',relative,'Unexpected native output')
        p=inside(root,relative)
        if not p.is_file() or fingerprint(p)!=h:diagnostics.append(diagnostic('NATIVE_FILE_CHANGED',relative,'Saved native hash differs'))
    from ..identities import verify as verify_assigned
    identity_gaps=verify_assigned(root,m);diagnostics.extend(identity_gaps)
    if identity_gaps and editor=='pass':editor='fail'
    # Static asset references are logical, not asserted native subresource UUIDs.
    plan=load(read(root/'extensions/monkey-import/import-plan.json',max_bytes=128*1024*1024),max_nodes=8_000_000);ids={a['sourceId'] for a in plan['assets']}
    for a in plan['assets']:
        if a.get('atlas') and a['atlas'] not in ids:diagnostics.append(diagnostic('MISSING_ATLAS',a['path'],'Bitmap atlas absent'))
    for c in plan['components']:
        if c['convertible']:
            for field in ['font','spriteFrame']:
                if c.get(field) is not None and c[field] not in ids:diagnostics.append(diagnostic('MISSING_REFERENCE',c['sourceId'],'Missing '+field))
    if standard.current(m):
        from ..layout.verify import scan
        diagnostics.extend(scan([f['path'] for f in m['files']]))
    if any(d['code'] in ('GENERATED_FILE_CHANGED','NATIVE_FILE_CHANGED') for d in diagnostics) and editor=='pass':editor='fail'
    out=new_output(output,[root]);report=dict(schemaVersion=1,toolVersion=__version__,diagnostics=diagnostics,
        staticValidation='conflict' if any(d['code']!='EDITOR_NOT_RUN' for d in diagnostics) else 'pass',editorValidation=editor,
        counts=dict(scope='candidate-import-plan',assets=len(plan['assets']),spriteFrames=sum(a['kind']=='sprite'for a in plan['assets']),nodes=len(plan['nodes']),plannedPrefabs=len(plan.get('sourcePrefabs',[]))))
    write_json(out/'verification.json',report);return finish(out,report)
