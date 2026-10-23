"""Typed formatting of unimported generated Unity candidates; no Scene/Prefab text edits."""
import copy,re,unicodedata
from pathlib import Path
from .io import safe,read,load,sha,encoded,inside,stage_manifest,new_output,write_json,finish
from .sources.compiled import fail
from .project_model import import_plan_model,replace_slots,asset_path
from .targets import unity

PLAN_PATH='Assets/Monkey/Editor/import-plan.json'
PATHS=dict(plan='Assets/Game/Editor/Conversion/import-plan.json',prefab='Assets/Game/Content/Prefabs/Recovery/Candidate.prefab',
    scene='Assets/Game/Scenes/Candidate.unity',bootstrap='Assets/Game/Scenes/ImportBootstrap.unity',
    artRoot='Assets/Game/Content/Images/Sprites',controllersRoot='Assets/Game/Content/Animations/Controllers',
    materialsRoot='Assets/Game/Content/Materials',animationsRoot='Assets/Game/Content/Animations',
    sourcePrefabsRoot='Assets/Game/Content/Prefabs/Recovery/Sources',editableProbe='Assets/Game/Content/Prefabs/Recovery/EditableProbe.prefab',
    nativeRoots=['Assets/Game/Content','Assets/Game/Scenes','Assets/Game/Presentation','Assets/Game/Domain','Assets/TextMesh Pro'],metaRoots=['Assets/Game/Editor/Conversion'])


def owned(project):
    root=safe(project);raw=read(root/'manifest.json',max_bytes=128*1024*1024);manifest=stage_manifest(root)
    if manifest.get('targetProfile')!=unity.PROFILE:fail('FORMAT_PROFILE',str(root),'Expected generated Unity target; direct Unity recovery profile pending')
    if manifest.get('layout')or manifest.get('format',{}).get('profile','none')!='none':fail('FORMAT_BASELINE',str(root),'Expected unformatted fresh export')
    if any((root/path).exists()for path in ['Library','Temp','Analysis/editor-readback.json']):fail('FORMAT_NATIVE_REQUIRED',str(root),'Native/materialized assets are outside this first formatting profile')
    files={f['path']:f for f in manifest['files']}
    if {p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}!=set(files)|{'manifest.json'}:fail('FORMAT_NATIVE_OR_UNKNOWN_FILES',str(root),'Unknown or missing project files')
    for path,row in files.items():
        data=read(inside(root,path),max_bytes=128*1024*1024)
        if sha(data)!=row['sha256']or len(data)!=row['bytes']:fail('FORMAT_OWNERSHIP_DRIFT',path,'Owned file differs from frozen receipt')
    adapter=root/'Assets/Monkey/Editor/MonkeyImporter.cs'
    if read(adapter)!=read(Path(__file__).parent/'targets/UnityImporter.cs'):fail('FORMAT_HOST_VERSION',str(adapter),'Fresh typed output-path Editor host required')
    plan=load(read(root/PLAN_PATH,max_bytes=128*1024*1024),max_nodes=8_000_000)
    if any((root/p['path']).exists()for p in plan.get('sourcePrefabs',[]))or any((root/path).exists()for path in ['Assets/Generated/Views/Candidate.prefab','Assets/Generated/Scenes/Candidate.unity']):fail('FORMAT_NATIVE_REQUIRED',str(root),'Native/materialized assets require native move support')
    return root,raw,manifest,plan


def build(project):
    root,raw,manifest,document=owned(project);model=import_plan_model(document,unity.PROFILE);changes={};files={f['path']:f for f in manifest['files']}
    fonts={a['path']for a in document['assets']if a['kind']=='cc.TTFFont'}|{a['fontAssetPath']for a in document['assets']if a.get('fontAssetPath')}|{f[k]for f in document.get('bitmapFonts',[])for k in ('path','fontPath')}
    jsons={a['path']for a in document['assets']if a['kind']=='cc.JsonAsset'}
    def change(old,new):
        asset_path(old,unity.PROFILE);asset_path(new,unity.PROFILE)
        if old in changes and changes[old]!=new:fail('FORMAT_PATH_CONFLICT',old,'Two typed destinations')
        changes[old]=new
    for slot in model['pathSlots']:
        old=slot['path']
        if old.startswith('Assets/Generated/Art/'):
            kind='Fonts'if old in fonts else'Config/Recovered'if old in jsons else'Images/Sprites'
            new='Assets/Game/Content/'+kind+'/'+old.removeprefix('Assets/Generated/Art/')
        elif old.startswith('Assets/Generated/Animations/'):new=PATHS['animationsRoot']+'/'+old.removeprefix('Assets/Generated/Animations/')
        elif old.startswith('Assets/Generated/Views/Sources/'):new=PATHS['sourcePrefabsRoot']+'/'+old.removeprefix('Assets/Generated/Views/Sources/')
        else:fail('FORMAT_ASSET_BASELINE',old,'Unknown typed generated path')
        change(old,new)
    for old,new in {
        'Assets/Monkey/Editor/MonkeyNumericCode.cs':'Assets/Game/Editor/Conversion/MonkeyNumericCode.cs',
        PLAN_PATH:PATHS['plan'],'Assets/Monkey/Editor/MonkeyImporter.cs':'Assets/Game/Editor/Conversion/MonkeyImporter.cs',
        'Assets/Generated/Views/MonkeyCandidateView.cs':'Assets/Game/Presentation/Recovery/MonkeyCandidateView.cs',
        'Assets/Generated/Views/IntrinsicGridLayoutGroup.cs':'Assets/Game/Presentation/Recovery/IntrinsicGridLayoutGroup.cs',
        'Assets/Generated/Views/Candidate.prefab':PATHS['prefab'],'Assets/Generated/Scenes/Candidate.unity':PATHS['scene'],
        'Assets/Generated/Scenes/ImportBootstrap.unity':PATHS['bootstrap'],'Assets/Generated/Views/EditableProbe.prefab':PATHS['editableProbe']}.items():change(old,new)
    contract_path=root/'Analysis/code-contract.json'
    if contract_path.exists():
        contract=load(read(contract_path));layer='Presentation/UI'if contract.get('presentation',{}).get('kind')=='label-adapter'else'Domain/State'
        for entry in contract['files']:
            if not entry['path'].startswith('Unity/Assets/Generated/Code/')or entry['path'].endswith('.meta'):continue
            old=entry['path'].removeprefix('Unity/');meta=inside(root,old+'.meta')
            if sha(read(root/old))!=entry['sha256']or not meta.exists():fail('FORMAT_CODE_DRIFT',old,'Code contract/meta differs')
            guid=contract.get('nativeIdentity',{}).get('unityScriptGuid')
            if not guid or ('guid: '+guid+'\n').encode()not in read(meta):fail('FORMAT_SCRIPT_IDENTITY',old,'Script GUID differs')
            change(old,'Assets/Game/'+layer+'/'+Path(old).name)
    physical={};identities=[]
    for old,new in changes.items():
        if old in files:
            if files[old].get('owner')!='generated':fail('FORMAT_HUMAN_OWNERSHIP',old,'Affected asset is not generated')
            physical[old]=new
            if old+'.meta'in files:
                if files[old+'.meta'].get('owner')!='generated':fail('FORMAT_HUMAN_OWNERSHIP',old+'.meta','Meta is not generated')
                physical[old+'.meta']=new+'.meta'
    for path,row in files.items():
        if not path.endswith('.meta'):continue
        matches=re.findall(rb'^guid: ([0-9a-f]{32})$',read(root/path),re.M)
        if len(matches)!=1:fail('FORMAT_META_IDENTITY',path,'Expected one declared Unity GUID')
        identities.append(dict(path=path[:-5],guid=matches[0].decode(),state='assigned_before_import'))
    targets={}
    for old in [*files,*changes]:
        new=physical.get(old,changes.get(old,old));key=unicodedata.normalize('NFC',new).casefold()
        if key in targets and targets[key]!=old:fail('FORMAT_COLLISION',new,'Case/Unicode/destination conflict')
        targets[key]=old
    document2=replace_slots(document,model['pathSlots'],changes)
    edits={PLAN_PATH:encoded(document2),'Analysis/output-paths.json':encoded(PATHS)}
    def report(data):
        result=replace_slots(data,import_plan_model(data,unity.PROFILE)['pathSlots'],changes)
        for collection in ['nodes','components','fonts']:
            for item in result.get(collection,[]):
                for key in ['target','atlas']:
                    if item.get(key)in changes:item[key]=changes[item[key]]
        return result
    for path in ['Analysis/source-map.json','Analysis/candidate.json']:
        if path in files:edits[path]=encoded(report(load(read(root/path,max_bytes=128*1024*1024),max_nodes=8_000_000)))
    for path in ['Analysis/name-map.json','Analysis/handoff.json']:
        if path not in files:continue
        data=load(read(root/path,max_bytes=128*1024*1024),max_nodes=8_000_000)
        for record in data.get('records',[]):
            if record.get('target')in changes:record['target']=changes[record['target']]
        for task in data.get('tasks',[]):task['generatedTargets']=[changes.get(value,value)for value in task.get('generatedTargets',[])]
        edits[path]=encoded(data)
    algorithm=sha(read(Path(__file__))+read(Path(__file__).with_name('project_model.py'))+read(Path(__file__).with_name('io.py')))
    future=sorted({slot['path']for slot in model['pathSlots']if slot['path']not in files}|{old for old in ['Assets/Generated/Views/Candidate.prefab','Assets/Generated/Scenes/Candidate.unity','Assets/Generated/Scenes/ImportBootstrap.unity']if old not in files})
    plan=dict(schemaVersion=1,profile='grea',targetProfile=unity.PROFILE,algorithmSha256=algorithm,candidateManifestSha256=sha(raw),sourceFiles=manifest['files'],
        pathChanges=[dict(old=old,new=new,materialized=old in files)for old,new in sorted(changes.items())],
        physicalMoves=[dict(old=old,new=new,sha256=files[old]['sha256'],owner=files[old]['owner'])for old,new in sorted(physical.items())],
        typedPathSlots=model['pathSlots'],identities=identities,nativeAssignmentPending=len(future),firstGenerationPaths=future,
        fileEdits=[dict(path=path,beforeSha256=files[path]['sha256']if path in files else None,afterSha256=sha(content))for path,content in sorted(edits.items())if path not in files or sha(content)!=files[path]['sha256']],
        sourceNamesAndLogicalKeysRewritten=False,numericPayloadsRewritten=False,nativeValidation='not_run')
    return root,manifest,plan,physical,edits,report,changes


def preview(project,output):
    root,_,plan,*_=build(project);out=new_output(output,[root]);write_json(out/'format-plan.json',plan)
    return dict(status='preview',physicalMoves=len(plan['physicalMoves']),typedPathChanges=len(plan['pathChanges']),nativeAssignmentPending=plan['nativeAssignmentPending'],report=str(out/'format-plan.json'))


def apply(project,plan_path,output):
    plan_path=safe(plan_path);root,manifest,plan,moves,edits,report,changes=build(project)
    if load(read(plan_path,max_bytes=128*1024*1024),max_nodes=8_000_000)!=plan:fail('FORMAT_STALE_PLAN',str(plan_path),'Source/ownership/algorithm changed')
    out=new_output(output,[root,plan_path.parent])
    for row in manifest['files']:
        old=row['path'];data=read(inside(root,old),max_bytes=128*1024*1024)
        if sha(data)!=row['sha256']:fail('FORMAT_SOURCE_CHANGED',old,'Source changed during apply')
        dest=inside(out,moves.get(old,old));dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(edits.get(old,data))
    for path,data in edits.items():
        if path not in {row['path']for row in manifest['files']}:
            dest=inside(out,path);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
    for path in [PATHS['artRoot'],PATHS['controllersRoot'],PATHS['materialsRoot'],PATHS['animationsRoot'],PATHS['sourcePrefabsRoot'],str(Path(PATHS['scene']).parent)]:(out/path).mkdir(parents=True,exist_ok=True)
    updated=report(manifest);updated.update(layout='grea-typed-v1',pathMappingMode='exact',pathMap=changes,format=dict(profile='grea',applied=True,inputManifestSha256=plan['candidateManifestSha256'],nativeValidation='not_run'))
    _,raw,_,_=owned(root)
    if sha(raw)!=plan['candidateManifestSha256']:fail('FORMAT_SOURCE_CHANGED',str(root),'Source manifest changed')
    write_json(out/'Analysis/formatting.json',plan);finish(out,updated)
    return dict(status='formatted_partial',project=str(out),physicalMoves=len(plan['physicalMoves']),nativeAssignmentPending=plan['nativeAssignmentPending'],manifestSha256=sha(read(out/'manifest.json',max_bytes=128*1024*1024)),nativeValidation='not_run')
