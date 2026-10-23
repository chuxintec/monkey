"""Creator 3.8.8 candidate asset emitter; native objects are saved only by its Editor."""
from importlib.resources import files
from pathlib import Path
import uuid
from .. import __version__
from ..io import safe, inside, read, load, sha, write_json, new_output, finish, diagnostic, stage_document, stage_bytes,stage_manifest
from ..sources.compiled import fail
from .common import input_ir, tasks

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


def plan(ir_path,namespace,output,bindings_path=None,animation_selection=None):
    path,ir,bindings,receipt,resource,resolve=input_ir(ir_path,bindings_path)
    from ..names import Names
    naming=Names(ir.get('sourceNames'))
    diagnostics=list(ir['diagnostics']);assets=[];copies=[]
    def add(sid,relative,kind,suffix,**fields):
        raw=resource(relative);uid=identity(namespace,sid);target=naming.path(sid,suffix,'assets/generated/art')
        item=dict(sourceId=sid,uuid=uid,path=target,kind=kind,sha256=sha(raw),**fields)
        assets.append(item);copies.append(dict(source=relative,target=target,sha256=sha(raw)))
        return item
    for f in ir['spriteFrames']:
        # Already physically unrotated pixels; no raw atlas rotation is guessed in target metadata.
        add(f['sourceId'],f['originalImage'],'sprite','.png',size=f['rect'][2:4],trimOrigin=f['trimOrigin'],originalSize=f['originalSize'],
            offset=f['offset'],border=f['capInsets'],subresource='spriteFrame')
        add(f['sourceId']+'@original',f['originalImage'],'sprite','.png',size=f['originalSize'],
            originalSize=f['originalSize'],offset=[0,0],border=[0,0,0,0],subresource='spriteFrame')
    for a in ir['assets']:
        if a['kind']=='cc.TTFFont':add(a['sourceId'],a['path'],'ttf','.ttf',fontCoverage=a.get('fontCoverage'))
        elif a['kind']=='cc.JsonAsset':add(a['sourceId'],a['path'],'json','.json')
        else:diagnostics.append(diagnostic('ASSET_HANDOFF',a['sourceId'],'Creator native subset has no mapping for '+a['kind'],a['sourceId']))
    font_by_id={}
    for f in ir.get('bitmapFonts',[]):
        atlas=add(f['sourceId']+'@atlas',f['atlasImage'],'sprite','.png',size=f['atlasSize'],originalSize=f['atlasSize'],
                  offset=[0,0],border=[0,0,0,0],subresource='spriteFrame')
        uid=identity(namespace,f['sourceId']);target=naming.path(f['sourceId'],'.fnt','assets/generated/art')
        raw=bitmap_text(f,Path(atlas['path']).name,Path(target).stem)
        assets.append(dict(sourceId=f['sourceId'],uuid=uid,path=target,kind='bitmap',sha256=sha(raw),
                           atlas=atlas['sourceId'],pointSize=f['pointSize'],glyphCount=len(f['glyphs']),kerningCount=len(f['kernings'])))
        copies.append(dict(source=None,target=target,sha256=sha(raw),text=raw.decode()))
        font_by_id[f['sourceId']]=f
    asset_by_id={a['sourceId']:a for a in assets};components=[]
    supported={'cc.Sprite','cc.Label','cc.Widget','cc.Mask','cc.ScrollView','cc.Layout','cc.Button','cc.LabelOutline'}
    materials={m['sourceId'] for m in ir.get('materials',[]) if m['nativeRole']=='standard-ugui'}
    node_ids={n['sourceId'] for n in ir['nodes']}
    for src in ir['components']:
        c=dict(src);sid=c['sourceId'];c['convertible']=c['type'] in supported and c.get('node') in node_ids
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
            if c['overflow']!=0 or c.get('italic') or c.get('underline'):gap('LABEL_SUBSET_UNSUPPORTED','First subset: no overflow/style synthesis')
            diagnostics.append(diagnostic('CREATOR_TEXT_METRICS_NOT_VERIFIED',sid,'Original font selected; 2.4 vs 3.8 glyph layout needs real comparison',sid))
        elif c['type']=='cc.Widget':
            if c['flags'] not in (0,45) or c['target'] is not None or not all(c['absolute']):gap('WIDGET_SUBSET_UNSUPPORTED','Only parent absolute disabled/full stretch')
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
            if c['layoutType'] not in (1,2,3) or c['resize']!=1 or c['affectedByScale']:gap('LAYOUT_SUBSET_UNSUPPORTED','Only unscaled container resize')
        if not c['convertible']:diagnostics.append(diagnostic('COMPONENT_HANDOFF',sid,'Unsupported native mapping: '+c['type'],sid))
        c['nativeType']=('cc.Label' if c['type']=='cc.LabelOutline' else c['type']) if c['convertible'] else None;components.append(c)
    for c in components:
        if c['type']=='cc.LabelOutline' and c['convertible'] and not any(x['type']=='cc.Label' and x['node']==c['node'] and x['convertible'] for x in components):
            c['convertible']=False;c['nativeType']=None
            diagnostics.append(diagnostic('MISSING_OUTLINE_LABEL',c['sourceId'],'Label dependency could not be converted',c['sourceId']))
    from .prefabs import plan_prefabs
    prefabs,prefab_gaps=plan_prefabs(ir,components)
    diagnostics.extend(prefab_gaps)
    for prefab in prefabs:
        prefab['path']=naming.path(prefab['sourceId'],'.prefab','assets/generated/prefabs')
    from .common import reject_layout_conflicts
    diagnostics.extend(reject_layout_conflicts(components))
    from ..assets.animation import plan_clips
    animations,animation_gaps=plan_clips(ir,namespace,PROFILE,animation_selection)
    naming.records.extend(a['nameEvidence'] for a in animations)
    if animation_selection:
        unselected={c['sourceId'] for c in ir.get('animationClips',[]) if c['sourceId'] not in animation_selection}
        diagnostics=[d for d in diagnostics if d.get('sourceId') not in unselected]
    diagnostics.extend(animation_gaps)
    out=new_output(output,[path.parent]);(out/'resources').mkdir()
    for i,c in enumerate(copies):
        raw=c.pop('text',None)
        raw=raw.encode() if raw is not None else resource(c['source'])
        dest=f'resources/{i:04d}'+Path(c['target']).suffix;(out/dest).write_bytes(raw);c['source']=dest
    result=dict(schemaVersion=1,toolVersion=__version__,targetProfile=PROFILE,namespace=namespace,
        scopeMode=ir.get('scopeMode','asset-selection'),
        sourceIrSha256=sha(stage_bytes(path)),sourceManifestSha256=ir['sourceManifestSha256'],sourceManifestPath=ir.get('sourceManifestPath'),
        sourceRoots=ir.get('sourceRoots',{}),sourceLocations=ir.get('sourceLocations',{}),bindings=receipt,
        designSize=[750,1334],assets=assets,copies=copies,animations=animations,sourcePrefabs=prefabs,naming=naming.report(),nodes=ir['nodes'],components=components,
        diagnostics=diagnostics,editorValidation='not_run',subresourceValidation='pending-native-import')
    write_json(out/'plan.json',result);return finish(out,result)


def export(plan_path,output):
    path=safe(plan_path);p=stage_document(path)
    if p.get('targetProfile')!=PROFILE or p.get('schemaVersion')!=1:fail('UNSUPPORTED_PLAN',str(path),'Expected Creator schema 1')
    # Preflight everything before output creation.
    for c in p['copies']:
        if not c['target'].startswith('assets/generated/art/') or sha(read(inside(path.parent,c['source'])))!=c['sha256']:
            fail('SOURCE_CHANGED',c['target'],'Invalid plan resource')
    out=new_output(output,[path.parent,*p.get('sourceRoots',{}).values()])
    for folder in ['assets/generated/art','assets/generated/animations','assets/generated/views','assets/generated/prefabs','assets/manual','extensions/monkey-import','Analysis']:
        (out/folder).mkdir(parents=True,exist_ok=True)
    by_path={a['path']:a for a in p['assets']};by_id={a['sourceId']:a for a in p['assets']}
    for c in p['copies']:
        target=inside(out,c['target']);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(read(inside(path.parent,c['source'])))
        a=by_path[c['target']]
        if a['kind']=='sprite':m=meta(a['uuid'],'image','1.0.27',dict(type='sprite-frame',fixAlphaTransparencyArtifacts=False,hasAlpha=True))
        elif a['kind']=='ttf':m=meta(a['uuid'],'ttf-font','1.0.1')
        elif a['kind']=='json':m=meta(a['uuid'],'json','2.0.1')
        else:m=meta(a['uuid'],'bitmap-font','1.0.6',dict(fontSize=a['pointSize'],textureUuid=by_id[a['atlas']]['uuid']))
        write_json(Path(str(target)+'.meta'),m)
    project_id=identity(p['namespace'],'project')
    write_json(out/'package.json',dict(name='monkey-native-candidate',version='3.8.8',uuid=project_id,creator=dict(version='3.8.8')))
    ext=out/'extensions/monkey-import'
    for name in ['main.js','scene.js']:(ext/name).write_bytes(files('monkey.targets').joinpath('Creator'+('Main.js' if name=='main.js' else 'Scene.js')).read_bytes())
    (ext/'prefab.js').write_bytes(files('monkey.targets').joinpath('CreatorPrefab.js').read_bytes())
    (ext/'animation.js').write_bytes(files('monkey.targets').joinpath('CreatorAnimation.js').read_bytes())
    write_json(ext/'package.json',dict(package_version=2,version='0.2.0',name='monkey-import',main='./main.js',
        contributions=dict(scene=dict(script='./scene.js'),menu=[dict(path='Monkey',label='Import isolated candidate',message='import-candidate')],
                           messages={'import-candidate':dict(methods=['importCandidate'])})))
    write_json(ext/'import-plan.json',{k:p[k] for k in ['schemaVersion','targetProfile','designSize','assets','nodes','components'] }|dict(projectUuid=project_id,animations=p.get('animations',[]),sourcePrefabs=p.get('sourcePrefabs',[])))
    from ..assets.animation import module_report
    write_json(out/'Analysis/animation-module.json',module_report(p.get('animations',[])))
    write_json(out/'Analysis/source-map.json',dict(assets=p['assets'],sourcePrefabs=p.get('sourcePrefabs',[]),nodes=[dict(sourceId=n['sourceId'],target='assets/generated/views/Candidate.scene') for n in p['nodes']],
        components=[dict(sourceId=c['sourceId'],node=c['node'],nativeType=c['nativeType']) for c in p['components']],
        sourceRoots=p['sourceRoots'],sourceLocations=p['sourceLocations'],subresources='actual UUIDs require native importer readback'))
    handoff_tasks=tasks(p['components'],[d for d in p['diagnostics'] if not d['code'].startswith('ANIMATION_')],'assets/generated/views/Candidate.scene','assets/manual/')
    if p.get('animations') or any(d['code'].startswith('ANIMATION_') for d in p['diagnostics']):
        from ..assets.animation import handoff_task
        handoff_tasks.append(handoff_task(p['animations'],p['diagnostics']))
    write_json(out/'Analysis/handoff.json',dict(schemaVersion=1,tasks=handoff_tasks,
        verification=dict(static='pending',editor='not_run',visual='not_run',business='not_run')))
    if p['bindings']:write_json(out/'Analysis/font-bindings.json',p['bindings'])
    (out/'README.md').write_text('Creator 3.8.8 isolated candidate. Open only in an authorized resource window.\nRun Monkey/Import isolated candidate once after assets import. Existing outputs are refused.\nNative scene and child UUIDs require Editor; no source engine interpreter ships.\n')
    write_json(out/'Analysis/name-map.json',p.get('naming',{}))
    report=dict(schemaVersion=1,toolVersion=__version__,targetProfile=PROFILE,namespace=p['namespace'],projectUuid=project_id,
        scopeMode=p.get('scopeMode','asset-selection'),
        sourceManifestSha256=p['sourceManifestSha256'],sourceRoots=p['sourceRoots'],planSha256=sha(stage_bytes(path)),diagnostics=p['diagnostics'],
        editorValidation='not_run',visualValidation='not_run',businessValidation='not_run',subresourceValidation='pending-native-import')
    write_json(out/'Analysis/candidate.json',report);return finish(out,report)


def verify(candidate,output,level='static'):
    root=safe(candidate);m=stage_manifest(root);diagnostics=[]
    from .layout import translate
    from ..sources.containers import fingerprint
    path_for=lambda p:translate(p,m.get('pathMap',{}))
    if m.get('targetProfile')!=PROFILE:fail('UNSUPPORTED_CANDIDATE',str(root),'Expected Creator profile')
    native={};editor='not_run'
    if level=='editor':
        rb_path=root/'Analysis/editor-readback.json'
        if not rb_path.exists():diagnostics.append(diagnostic('EDITOR_NOT_RUN',str(rb_path),'Run native importer in declared Creator first'))
        else:
            rb=load(read(rb_path));native={f['path']:f['sha256'] for f in rb.get('nativeFiles',[])}
            plan=load(read(root/'extensions/monkey-import/import-plan.json',max_bytes=128*1024*1024),max_nodes=8_000_000)
            expected_assets={a['sourceId']:a for a in plan['assets']}
            actual_assets={a['sourceId']:a for a in rb.get('assets',[])}
            json_assets={a['sourceId']:a for a in rb.get('jsonAssets',[])}
            good=rb.get('creatorVersion')=='3.8.8' and rb.get('projectUuid')==m['projectUuid'] and rb.get('manifestSha256')==fingerprint(root/'manifest.json')
            good=good and set(expected_assets)==set(actual_assets) and rb.get('nodeCount')==len(plan['nodes'])
            for sid,a in expected_assets.items():
                actual=actual_assets.get(sid,{})
                good=good and actual.get('uuid')==a['uuid'] and (a['kind']!='sprite' or bool(actual.get('spriteFrameUuid')))
                if a['kind']=='json':
                    actual_json=json_assets.get(sid,{})
                    good=good and actual_json.get('uuid')==a['uuid'] and 'value' in actual_json and actual_json['value']==load(read(root/a['path']))
            labels={v['sourceId']:v for v in rb.get('labels',[])}
            for c in plan['components']:
                if c['convertible'] and c['type']=='cc.Label':
                    actual=labels.get(c['sourceId'],{})
                    good=good and actual.get('text')==c['text'] and actual.get('fontUuid')==expected_assets[c['font']]['uuid']
            expected_components={c['sourceId'] for c in plan['components'] if c['convertible']}
            good=good and {c['sourceId'] for c in rb.get('components',[])}==expected_components
            good=good and {n['sourceId'] for n in rb.get('nodes',[])}=={n['sourceId'] for n in plan['nodes']}
            def near(actual,expected):
                return isinstance(actual,list) and len(actual)==len(expected) and all(type(x) in (int,float) and abs(x-y)<.001 for x,y in zip(actual,expected))
            frames={f['sourceId']:f for f in rb.get('frames',[])}
            for sid,a in expected_assets.items():
                if a['kind']=='sprite':
                    f=frames.get(sid,{})
                    good=good and f.get('uuid')==actual_assets.get(sid,{}).get('spriteFrameUuid')
                    good=good and f.get('textureUuid')==actual_assets.get(sid,{}).get('textureUuid')
                    good=good and near(f.get('rect'),a.get('trimOrigin',[0,0])+a['size']) and near(f.get('originalSize'),a['originalSize'])
                    good=good and near(f.get('offset'),a['offset']) and near(f.get('border'),a['border'])
            good=good and all(isinstance(n.get('nodeUuid'),str) and n['nodeUuid'] for n in rb.get('nodes',[]))
            good=good and all(isinstance(c.get('componentUuid'),str) and c['componentUuid'] for c in rb.get('components',[]))
            good=good and path_for('assets/generated/views/Candidate.scene') in native and bool(rb.get('sceneUuid'))
            actual_prefabs={v['sourceId']:v for v in rb.get('sourcePrefabs',[])}
            expected_prefabs={v['sourceId']:v for v in plan.get('sourcePrefabs',[])}
            if set(actual_prefabs)!=set(expected_prefabs):good=False
            for sid,spec in expected_prefabs.items():
                actual=actual_prefabs.get(sid,{})
                expected_components={c['sourceId'] for c in plan['components'] if c['convertible'] and c['node'] in set(spec['nodes'])}
                valid=(set(actual.get('components',[]))==expected_components and actual.get('path')==spec['path'] and bool(actual.get('uuid')) and
                       actual.get('nodeCount')==spec['nodeCount'] and actual.get('savedReloaded') is True and
                       actual.get('geometryVerified') is True and actual.get('referencesVerified') is True and spec['path'] in native)
                if not valid:
                    good=False;diagnostics.append(diagnostic('SOURCE_PREFAB_NOT_VERIFIED',sid,'Independent Creator prefab save/reload evidence absent or inconsistent'))
            from ..assets.animation import verify_native
            motion_gaps=verify_native(plan.get('animations',[]),rb.get('animations',[]),native);diagnostics.extend(motion_gaps);good=good and not motion_gaps
            if not good:diagnostics.append(diagnostic('EDITOR_READBACK_FAILED',str(rb_path),'Native identities/counts/version differ'))
            editor='pass' if good else 'fail'
    for f in m['files']:
        if f.get('owner')=='manual':continue
        target=inside(root,f['path']);expected=native.get(f['path'],f['sha256'])
        if not target.is_file() or fingerprint(target)!=expected:diagnostics.append(diagnostic('GENERATED_FILE_CHANGED',f['path'],'Generated file differs'))
    for relative,h in native.items():
        prefixes=('assets/','Analysis/') if m.get('layout')=='game-standard-v1' else ('assets/generated/','Analysis/')
        if not relative.startswith(prefixes):fail('UNSAFE_NATIVE_FILE',relative,'Unexpected native output')
        p=inside(root,relative)
        if not p.is_file() or sha(read(p))!=h:diagnostics.append(diagnostic('NATIVE_FILE_CHANGED',relative,'Saved native hash differs'))
    # Static asset references are logical, not asserted native subresource UUIDs.
    plan=load(read(root/'extensions/monkey-import/import-plan.json',max_bytes=128*1024*1024),max_nodes=8_000_000);ids={a['sourceId'] for a in plan['assets']}
    for a in plan['assets']:
        if a.get('atlas') and a['atlas'] not in ids:diagnostics.append(diagnostic('MISSING_ATLAS',a['path'],'Bitmap atlas absent'))
    for c in plan['components']:
        if c['convertible']:
            for field in ['font','spriteFrame']:
                if c.get(field) is not None and c[field] not in ids:diagnostics.append(diagnostic('MISSING_REFERENCE',c['sourceId'],'Missing '+field))
    if any(d['code'] in ('GENERATED_FILE_CHANGED','NATIVE_FILE_CHANGED') for d in diagnostics) and editor=='pass':editor='fail'
    out=new_output(output,[root]);report=dict(schemaVersion=1,toolVersion=__version__,diagnostics=diagnostics,
        staticValidation='conflict' if any(d['code']!='EDITOR_NOT_RUN' for d in diagnostics) else 'pass',editorValidation=editor)
    write_json(out/'verification.json',report);return finish(out,report)
