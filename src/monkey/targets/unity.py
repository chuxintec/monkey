"""Python plans and assembles a native Unity Editor import candidate."""
from importlib.resources import files
from pathlib import Path
import uuid
from .. import __version__
from ..io import safe, inside, read, load, sha, encoded, new_output, finish, write_json, diagnostic
from ..sources.compiled import fail

PROFILE = 'unity-6000.6.2f1-ugui'


def guid(namespace, identity):
    return uuid.uuid5(uuid.NAMESPACE_URL, 'monkey/'+namespace+'/'+identity).hex


def plan(ir_path, namespace, output):
    ir_path = safe(ir_path)
    ir = load(read(ir_path))
    if ir.get('schemaVersion') != 1 or ir.get('sourceProfile') not in ('cocos-2.4.15-bundle','cocos-2.4.15-project'):
        fail('UNSUPPORTED_IR', '$', 'Expected normalize schema 1')
    source_files = load(read(ir_path.parent/'manifest.json'))['files']
    expected = {f['path']: f['sha256'] for f in source_files}
    diagnostics = list(ir['diagnostics'])
    textures, copies = [], []
    def resource(relative, identity, role):
        source = inside(ir_path.parent, relative)
        if relative not in expected or sha(read(source)) != expected[relative]:
            fail('SOURCE_CHANGED', relative, 'Normalized asset differs from output manifest')
        target = 'Assets/Generated/Art/'+guid(namespace,identity)+source.suffix.lower()
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
        assets.append(dict(id=asset['sourceId'],kind=asset['kind'],path=resource(asset['path'],asset['sourceId'],'native')))
    resource_ids = {a['id'] for a in assets}
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
    components=[]
    for c in ir['components']:
        entry=dict(c)
        for field in ('spriteFrame','font'):
            value=entry.get(field);seen=set()
            while value in ir.get('aliases',{}):
                if value in seen:fail('REDIRECT_CYCLE',value,'IR alias cycle')
                seen.add(value);value=ir['aliases'][value]
            if field in entry:entry[field]=value
        c=entry
        entry['convertible']=c['type'] in ('cc.Sprite','cc.Label') and c['node'] in node_ids
        if c['type']=='cc.Sprite':
            if c.get('spriteFrame') not in sprite_ids or c['mode'] not in (0,1):
                entry['convertible']=False
                diagnostics.append(diagnostic('SPRITE_NOT_CONVERTIBLE',c['sourceId'],'Missing frame or unsupported mode',c['sourceId']))
            if not c.get('trim',True) and c['mode']==1:
                entry['convertible']=False
                diagnostics.append(diagnostic('SLICED_UNTRIMMED_UNSUPPORTED',c['sourceId'],'Needs Cocos size-mode evidence',c['sourceId']))
        elif c['type']=='cc.Label':
            if c.get('font') not in resource_ids:
                entry['convertible']=False
                diagnostics.append(diagnostic('FONT_NOT_CONVERTIBLE',c['sourceId'],'No imported matching font; no fallback text',c['sourceId']))
            if c.get('overflow') != 0:
                entry['convertible']=False
            diagnostics.append(diagnostic('LABEL_METRICS_NOT_VERIFIED',c['sourceId'],'TMP line metrics need engine/reference comparison',c['sourceId']))
        if not entry['convertible']:
            diagnostics.append(diagnostic('COMPONENT_HANDOFF',c['sourceId'],'Native mapping unavailable for '+str(c['type']),c['sourceId']))
        components.append(entry)
    out = new_output(output,[ir_path.parent])
    (out/'resources').mkdir()
    for copy in copies:
        target = out/'resources'/Path(copy['target']).name
        target.write_bytes(read(inside(ir_path.parent,copy['source'])))
        copy['source']='resources/'+target.name
    result=dict(schemaVersion=1,toolVersion=__version__,targetProfile=PROFILE,namespace=namespace,
                sourceIrSha256=sha(read(ir_path)),designSize=[750,1334],pixelsPerUnit=100,
                textures=textures,assets=assets,nodes=nodes,components=components,copies=copies,
                diagnostics=diagnostics,galleryOnly=not bool(nodes),editorValidation='not_run')
    write_json(out/'plan.json',result)
    return finish(out,result)


def export(plan_path, output):
    plan_path=safe(plan_path);p=load(read(plan_path))
    if p.get('targetProfile')!=PROFILE or p.get('schemaVersion')!=1:
        fail('UNSUPPORTED_PLAN','$','Expected Unity plan schema 1')
    # Plan JSON itself must match its create-only manifest, not just copied images.
    pm=load(read(plan_path.parent/'manifest.json'))
    expected={f['path']:f['sha256'] for f in pm['files']}
    if expected.get(plan_path.name)!=sha(read(plan_path)):
        fail('PLAN_CHANGED',str(plan_path),'Plan differs from manifest')
    for c in p['copies']:
        if sha(read(inside(plan_path.parent,c['source'])))!=c['sha256']:
            fail('SOURCE_CHANGED',c['source'],'Plan resource differs')
        if not c['target'].startswith('Assets/Generated/Art/'):
            fail('UNSAFE_TARGET',c['target'],'Unexpected target root')
    out=new_output(output,[plan_path.parent])
    for folder in ['Assets/Generated/Art','Assets/Generated/Views','Assets/Generated/Scenes',
                   'Assets/Monkey/Editor','Assets/Manual','Packages','ProjectSettings','Analysis']:
        (out/folder).mkdir(parents=True,exist_ok=True)
    ownership=[]
    for c in p['copies']:
        target=inside(out,c['target']);target.write_bytes(read(inside(plan_path.parent,c['source'])))
        Path(str(target)+'.meta').write_text('fileFormatVersion: 2\nguid: '+c['guid']+'\n',encoding='utf-8')
        ownership.append(dict(path=c['target'],sourceId=c['sourceId'],guid=c['guid']))
    view_path=out/'Assets/Generated/Views/MonkeyCandidateView.cs'
    view_path.write_bytes(files('monkey.targets').joinpath('MonkeyCandidateView.cs').read_bytes())
    Path(str(view_path)+'.meta').write_text('fileFormatVersion: 2\nguid: '+guid(p['namespace'],'native-view-script')+'\n')
    adapter=files('monkey.targets').joinpath('UnityImporter.cs').read_bytes()
    adapter_path=out/'Assets/Monkey/Editor/MonkeyImporter.cs';adapter_path.write_bytes(adapter)
    Path(str(adapter_path)+'.meta').write_text('fileFormatVersion: 2\nguid: '+guid(p['namespace'],'editor-adapter')+'\n')
    # Only the typed, finite import instruction subset is sent to the Editor.
    instruction={key:p[key] for key in ('designSize','pixelsPerUnit','textures','assets','nodes','components','galleryOnly')}
    instruction['sourceDiagnosticCount']=len(p['diagnostics'])
    instruction['prefabGuid']=guid(p['namespace'],'native-prefab')
    instruction['sceneGuid']=guid(p['namespace'],'native-scene')
    write_json(out/'Assets/Monkey/Editor/import-plan.json',instruction)
    write_json(out/'Packages/manifest.json',dict(dependencies={'com.unity.ugui':'2.0.0',
               'com.unity.modules.ui':'1.0.0','com.unity.modules.imgui':'1.0.0'}))
    (out/'ProjectSettings/ProjectVersion.txt').write_text('m_EditorVersion: 6000.6.2f1\n')
    (out/'Assets/Manual/README.md').write_text('AI/人工业务代码区。生成区默认不覆盖；缺口见工程根 Analysis/handoff.json。\n')
    (out/'README.md').write_text('Unity 原生资源/UI候选，非可玩游戏。\n\n打开后执行 Tools > Monkey > Import Candidate。\n'
        '仅首次导入新候选；已生成 Prefab/Scene 存在时拒绝覆盖。\n'
        '或用独立 batchmode -projectPath 此目录 -executeMethod MonkeyImporter.ImportBatch。\n'
        '导入成功后删除 Assets/Monkey 仍保留原生可编辑资产；Player 不读取转换 JSON。\n'
        '真实编辑器/画面对照/业务尚未验证，见 Analysis。\n')
    tasks=[]
    for i,d in enumerate(p['diagnostics']):
        tasks.append(dict(taskId=f'gap-{i+1:04d}',sourceRefs=[d.get('sourceId'),d.get('location')],
                          gaps=[d],generatedTargets=['Assets/Generated/Views/Candidate.prefab'],
                          allowedPaths=['Assets/Manual/'],dependencies=['matching original evidence'],
                          verificationScope=['affected UI in real Editor','source reference comparison']))
    write_json(out/'Analysis/handoff.json',dict(schemaVersion=1,tasks=tasks,
               verification=dict(static='pending',editor='not_run',visual='not_run',business='not_run')))
    write_json(out/'Analysis/source-map.json',dict(assets=ownership,
        nodes=[dict(sourceId=n['sourceId'],target='Assets/Generated/Views/Candidate.prefab',name=n['name']) for n in p['nodes']]))
    report=dict(schemaVersion=1,toolVersion=__version__,targetProfile=PROFILE,namespace=p['namespace'],
                planSha256=sha(read(plan_path)),diagnostics=p['diagnostics'],editorValidation='not_run',
                visualValidation='not_run',businessValidation='not_run',galleryOnly=p['galleryOnly'])
    write_json(out/'Analysis/candidate.json',report)
    return finish(out,report)


def verify(candidate, output, level='static'):
    root=safe(candidate);m=load(read(root/'manifest.json'));diagnostics=[]
    native={};editor='not_run'
    if level=='editor':
        readback_path=root/'Analysis/editor-readback.json'
        if not readback_path.is_file():
            diagnostics.append(diagnostic('EDITOR_NOT_RUN','Analysis/editor-readback.json','Run native import in the declared Editor first'))
        else:
            rb=load(read(readback_path))
            native={f['path']:f['sha256'] for f in rb.get('nativeFiles',[])}
            if rb.get('unityVersion')!='6000.6.2f1' or rb.get('missingScripts')!=0:
                diagnostics.append(diagnostic('EDITOR_READBACK_FAILED',str(readback_path),'Version/missing-script check failed'))
            for relative,expected in native.items():
                file=inside(root,relative)
                if not file.is_file() or sha(read(file))!=expected:
                    diagnostics.append(diagnostic('NATIVE_FILE_CHANGED',relative,'Native file differs from saved readback'))
            instruction=load(read(root/'Assets/Monkey/Editor/import-plan.json'))
            by_id={s['id']:s for s in rb.get('sprites',[])}
            for spec in instruction['textures']:
                actual=by_id.get(spec['id'])
                meta=(root/(spec['path']+'.meta')).read_text() if (root/(spec['path']+'.meta')).is_file() else ''
                if not actual or actual.get('size')!=spec['size'] or actual.get('border')!=spec['border'] or actual.get('guid','') not in meta or not actual.get('fileId'):
                    diagnostics.append(diagnostic('SPRITE_READBACK_MISMATCH',spec['path'],'Native sprite size/border/GUID/fileID mismatch'))
            by_node={n['sourceId']:n for n in rb.get('nodes',[])}
            for spec in instruction['nodes']:
                actual=by_node.get(spec['sourceId'])
                if not actual or any(actual.get(k)!=spec[v] for k,v in [('size','size'),('pivot','anchor'),('position','position'),('active','active')]):
                    diagnostics.append(diagnostic('NODE_READBACK_MISMATCH',spec['sourceId'],'Saved RectTransform differs from plan'))
            for required in ('Assets/Generated/Views/Candidate.prefab','Assets/Generated/Scenes/Candidate.unity'):
                if required not in native:
                    diagnostics.append(diagnostic('NATIVE_ARTIFACT_MISSING',required,'No saved native artifact hash'))
            editor='partial' if rb.get('diagnostics') else 'pass'
    for item in m['files']:
        path=inside(root,item['path'])
        expected=native.get(item['path']) if level=='editor' and item['path'].endswith('.meta') else item['sha256']
        if expected is None: expected=item['sha256']
        if not path.is_file() or sha(read(path))!=expected:
            diagnostics.append(diagnostic('GENERATED_FILE_CHANGED',item['path'],'Missing or modified generated file'))
    guids={}
    for path in (root/'Assets').rglob('*.meta'):
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.startswith('guid: '):
                value=line[6:]
                if value in guids:
                    diagnostics.append(diagnostic('DUPLICATE_TARGET_GUID',str(path.relative_to(root)),'GUID duplicates '+guids[value]))
                guids[value]=str(path.relative_to(root))
    instruction=load(read(root/'Assets/Monkey/Editor/import-plan.json'))
    for item in instruction['textures']+instruction['assets']:
        if not inside(root,item['path']).is_file():
            diagnostics.append(diagnostic('TARGET_REFERENCE_MISSING',item['path'],'Import resource does not exist'))
    adapter=root/'Assets/Monkey/Editor/MonkeyImporter.cs'
    if not adapter.is_file() or list((root/'Assets').rglob('ir.json')):
        diagnostics.append(diagnostic('TARGET_LAYOUT_INVALID','Assets','Missing Editor adapter or runtime IR found'))
    out=new_output(output,[root])
    result=dict(schemaVersion=1,toolVersion=__version__,candidateManifestSha256=sha(read(root/'manifest.json')),
                diagnostics=diagnostics,staticValidation='pass' if not diagnostics else 'conflict',
                editorValidation=editor,visualValidation='not_run',businessValidation='not_run')
    write_json(out/'verification.json',result)
    return finish(out,result)


def handoff(candidate, output):
    root=safe(candidate)
    package=load(read(root/'Analysis/handoff.json'))
    out=new_output(output,[root])
    package['candidateManifestSha256']=sha(read(root/'manifest.json'))
    write_json(out/'handoff.json',package)
    lines=['# AI接续工作包','', '这是候选工程，Editor/原版画面对照/业务分别按验证记录处理。',
           '仅修改 Assets/Manual；生成区需要明确解除所有权后才可手改。','']
    for task in package['tasks']:
        lines.extend(['## '+task['taskId'],'',
                      '来源：'+str(task['sourceRefs']),
                      '目标：'+', '.join(task['generatedTargets']),
                      '缺口：'+'; '.join(g['code']+': '+g['message'] for g in task['gaps']),
                      '验证：'+', '.join(task['verificationScope']),''])
    (out/'HANDOFF.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    return finish(out,dict(schemaVersion=1,diagnostics=[],tasks=len(package['tasks']),toolVersion=__version__))
