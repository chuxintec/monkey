"""Typed, create-only offline formatting; never substitute arbitrary source/text strings."""
import copy,posixpath,re,unicodedata
from pathlib import Path
from .io import safe,inside,read,load,sha,encoded,new_output,write_json,stage_manifest,finish
from .sources.compiled import fail
from .project_model import import_plan_model,replace_slots,asset_path
from .targets import cocos

PLAN_PATH='extensions/monkey-import/import-plan.json'
OUTPUT_PATHS=dict(scene='assets/scenes/Candidate.scene',prefabs='assets/content/prefabs',animations='assets/content/animations',nativeRoots=['assets'])


def _owned(root):
    root=safe(root);raw=read(root/'manifest.json',max_bytes=128*1024*1024);manifest=stage_manifest(root)
    if manifest.get('targetProfile')!=cocos.PROFILE:fail('FORMAT_PROFILE',str(root),'First typed formatter supports Creator candidates; Unity formatter pending')
    if manifest.get('layout') or manifest.get('format',{}).get('profile','none')!='none':fail('FORMAT_BASELINE',str(root),'Expected an unformatted candidate, keep legacy/formatted artifacts unchanged')
    if any((root/name).exists()for name in ['Library','library','temp','profiles','Analysis/editor-readback.json']):fail('FORMAT_NATIVE_REQUIRED',str(root),'Imported/native candidates require the asset database move adapter')
    expected={f['path']for f in manifest['files']}|{'manifest.json'}
    actual={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()}
    if actual!=expected:fail('FORMAT_NATIVE_OR_UNKNOWN_FILES',str(root),'Only an unimported owned candidate is supported; native move adapter required otherwise')
    for f in manifest['files']:
        data=read(inside(root,f['path']),max_bytes=128*1024*1024)
        if len(data)!=f['bytes']or sha(data)!=f['sha256']:fail('FORMAT_OWNERSHIP_DRIFT',f['path'],'Generated or human file differs from frozen ownership receipt')
    if read(root/'extensions/monkey-import/main.js')!=read(Path(__file__).parent/'targets/CreatorMain.js'):
        fail('FORMAT_HOST_VERSION',PLAN_PATH,'Fresh export with the typed output-path host required')
    document=load(read(root/PLAN_PATH,max_bytes=128*1024*1024),max_nodes=8_000_000)
    if any((root/p['path']).exists()for p in document.get('sourcePrefabs',[]))or(root/'Analysis/editor-readback.json').exists():
        fail('FORMAT_NATIVE_REQUIRED',str(root),'Materialized assets must be moved with the native asset database')
    return root,raw,manifest,document


def _build(project):
    root,raw,manifest,document=_owned(project);model=import_plan_model(document,cocos.PROFILE);changes={};identities=[];rewrites={}
    def change(old,new):
        asset_path(old,cocos.PROFILE);asset_path(new,cocos.PROFILE)
        if old in changes and changes[old]!=new:fail('FORMAT_PATH_CONFLICT',old,'Two typed destinations')
        changes[old]=new
    for asset in document['assets']:
        old=asset['path'];prefix='assets/generated/art/'
        if not old.startswith(prefix):fail('FORMAT_ASSET_BASELINE',old,'Expected original native export asset root')
        folder={'ttf':'fonts','bitmap':'fonts','json':'config/recovered','sprite':'images/sprites'}.get(asset['kind'])
        if folder is None:fail('FORMAT_ASSET_KIND',asset['sourceId'],'Unknown kind cannot be guessed into Config')
        if asset.get('role')=='bitmap-atlas-page':folder='fonts'
        change(old,'assets/content/'+folder+'/'+old.removeprefix(prefix))
        identities.append(dict(sourceId=asset['sourceId'],uuid=asset['uuid'],kind=asset['kind']))
    for collection,prefix,target in [('animations','assets/generated/animations/','assets/content/animations/'),('sourcePrefabs','assets/generated/prefabs/','assets/content/prefabs/')]:
        for item in document.get(collection,[]):
            if not item['path'].startswith(prefix):fail('FORMAT_ASSET_BASELINE',item['path'],'Unexpected generated asset root')
            change(item['path'],target+item['path'].removeprefix(prefix))
    changes['assets/generated/views/Candidate.scene']=OUTPUT_PATHS['scene']
    contract_path=root/'Analysis/code-contract.json'
    if contract_path.exists():
        contract=load(read(contract_path));kind=contract.get('presentation',{}).get('kind')
        for entry in contract['files']:
            if not entry['path'].startswith('Cocos/assets/generated/scripts/')or entry['path'].endswith('.meta'):continue
            old=entry['path'].removeprefix('Cocos/')
            if sha(read(inside(root,old)))!=entry['sha256']:fail('FORMAT_CODE_DRIFT',old,'Code emission differs')
            meta=inside(root,old+'.meta')
            if not meta.exists():fail('FORMAT_SCRIPT_IDENTITY_PENDING',old,'An explicit verified importer meta is required before moving code')
            data=load(read(meta));uid=contract.get('nativeIdentity',{}).get('creatorScriptUuid')
            if not uid or data.get('uuid')!=uid:fail('FORMAT_SCRIPT_IDENTITY',old,'Code contract and meta identity differ')
            layer='presentation/ui'if kind=='label-adapter'else'domain/state'
            change(old,'assets/scripts/'+layer+'/'+Path(old).name);identities.append(dict(sourceId='code:'+contract['className'],uuid=uid,kind='script'))
    # Re-render only the declared page reference in generated BMFont text.
    assets={a['sourceId']:a for a in document['assets']}
    for font in document['assets']:
        if font['kind']!='bitmap':continue
        atlas=assets[font['atlas']];old_page=Path(atlas['path']).name;new_page=posixpath.relpath(changes[atlas['path']],posixpath.dirname(changes[font['path']]))
        content=read(root/font['path']);lines=content.decode('utf-8').splitlines(keepends=True);found=[]
        for index,line in enumerate(lines):
            match=re.fullmatch(r'page id=0 file="([^"\r\n]+)"(\r?\n)?',line)
            if match:found.append((index,match))
        if len(found)!=1 or found[0][1][1]!=old_page:fail('FORMAT_FONT_PAGE',font['path'],'Generated one-page font reference differs from the typed atlas')
        index,match=found[0];lines[index]='page id=0 file="'+new_page+'"'+(match[2]or'');rewrites[font['path']]=''.join(lines).encode()
    physical={};owners={f['path']:f for f in manifest['files']}
    for old,new in changes.items():
        if old in owners:
            if owners[old].get('owner')!='generated':fail('FORMAT_HUMAN_OWNERSHIP',old,'Affected file is not generated')
            physical[old]=new
            if old+'.meta'in owners:
                if owners[old+'.meta'].get('owner')!='generated':fail('FORMAT_HUMAN_OWNERSHIP',old+'.meta','Meta is not generated')
                physical[old+'.meta']=new+'.meta'
    targets={}
    for old in [*owners,*changes]:
        new=physical.get(old,changes.get(old,old));key=unicodedata.normalize('NFC',new).casefold()
        if key in targets and targets[key]!=old:fail('FORMAT_COLLISION',new,'Case/Unicode/destination conflict')
        targets[key]=old
    typed=replace_slots(document,model['pathSlots'],changes);typed['outputPaths']=copy.deepcopy(OUTPUT_PATHS)
    for asset in typed['assets']:
        original=assets[asset['sourceId']]
        if original['path']in rewrites:asset['sha256']=sha(rewrites[original['path']])
    edits={PLAN_PATH:encoded(typed)}
    def rewrite_report(data):
        updated=replace_slots(data,import_plan_model(data,cocos.PROFILE)['pathSlots'],changes)
        for item in updated.get('assets',[]):
            old=assets.get(item.get('sourceId'))
            if old and old['path']in rewrites and 'sha256'in item:item['sha256']=sha(rewrites[old['path']])
        emission=updated.get('codeEmission')
        if isinstance(emission,dict)and emission.get('scriptPath')in changes:emission['scriptPath']=changes[emission['scriptPath']]
        for collection in ['nodes','components']:
            for item in updated.get(collection,[]):
                if item.get('target')in changes:item['target']=changes[item['target']]
        return updated
    for path in ['Analysis/source-map.json','Analysis/candidate.json']:
        if path in owners:edits[path]=encoded(rewrite_report(load(read(root/path,max_bytes=128*1024*1024),max_nodes=8_000_000)))
    path='Analysis/name-map.json'
    if path in owners:
        data=load(read(root/path,max_bytes=128*1024*1024),max_nodes=8_000_000)
        for record in data.get('records',[]):
            if record.get('target')in changes:record['target']=changes[record['target']]
        edits[path]=encoded(data)
    path='Analysis/handoff.json'
    if path in owners:
        data=load(read(root/path,max_bytes=128*1024*1024),max_nodes=8_000_000)
        for task in data.get('tasks',[]):task['generatedTargets']=[changes.get(value,value)for value in task.get('generatedTargets',[])]
        edits[path]=encoded(data)
    edits.update(rewrites)
    algorithm=sha(read(Path(__file__))+read(Path(__file__).with_name('project_model.py'))+read(Path(__file__).with_name('io.py')))
    plan=dict(schemaVersion=1,profile='grea',targetProfile=cocos.PROFILE,algorithmSha256=algorithm,candidateManifestSha256=sha(raw),
              sourceFiles=manifest['files'],pathChanges=[dict(old=old,new=new,materialized=old in owners)for old,new in sorted(changes.items())],
              physicalMoves=[dict(old=old,new=new,sha256=owners[old]['sha256'],owner=owners[old]['owner'])for old,new in sorted(physical.items())],
              typedPathSlots=model['pathSlots'],identities=identities,nativePrefabIdentities='not_assigned_before_import',
              nativeAssignmentPending=sum(a['identityState']=='native_assignment_pending'for a in model['assets']),
              fileEdits=[dict(path=path,beforeSha256=owners[path]['sha256'],afterSha256=sha(content))for path,content in sorted(edits.items())if sha(content)!=owners[path]['sha256']],
              sourceNamesAndLogicalKeysRewritten=False,numericPayloadsRewritten=False,nativeValidation='not_run')
    return root,manifest,plan,physical,edits,rewrite_report,changes


def preview(project,output):
    from .targets import unity
    if stage_manifest(safe(project)).get('targetProfile')==unity.PROFILE:
        from .formatting_unity import preview as unity_preview
        return unity_preview(project,output)
    root,manifest,plan,*_=_build(project);out=new_output(output,[root]);write_json(out/'format-plan.json',plan)
    return dict(status='preview',physicalMoves=len(plan['physicalMoves']),typedPathChanges=len(plan['pathChanges']),nativeAssignmentPending=plan['nativeAssignmentPending'],report=str(out/'format-plan.json'))


def apply(project,plan_path,output):
    from .targets import unity
    if stage_manifest(safe(project)).get('targetProfile')==unity.PROFILE:
        from .formatting_unity import apply as unity_apply
        return unity_apply(project,plan_path,output)
    plan_path=safe(plan_path);root,manifest,plan,moves,edits,rewrite_report,changes=_build(project)
    if load(read(plan_path,max_bytes=128*1024*1024),max_nodes=8_000_000)!=plan:fail('FORMAT_STALE_PLAN',str(plan_path),'Source/ownership/algorithm/typed plan changed since preview')
    out=new_output(output,[root,plan_path.parent])
    for entry in manifest['files']:
        path=entry['path'];data=read(inside(root,path),max_bytes=128*1024*1024)
        if sha(data)!=entry['sha256']:fail('FORMAT_SOURCE_CHANGED',path,'Source changed during apply')
        dest=inside(out,moves.get(path,path));dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(edits.get(path,data))
    for folder in [OUTPUT_PATHS['prefabs'],OUTPUT_PATHS['animations'],posixpath.dirname(OUTPUT_PATHS['scene'])]:(out/folder).mkdir(parents=True,exist_ok=True)
    updated=rewrite_report(manifest);updated.update(layout='grea-typed-v1',pathMap=changes,pathMappingMode='exact',format=dict(profile='grea',applied=True,inputManifestSha256=plan['candidateManifestSha256'],nativeValidation='not_run'))
    _,source_manifest,_,_=_owned(root)
    if sha(source_manifest)!=plan['candidateManifestSha256']:fail('FORMAT_SOURCE_CHANGED',str(root),'Source manifest changed during apply')
    write_json(out/'Analysis/formatting.json',plan);finish(out,updated)
    return dict(status='formatted_partial',project=str(out),physicalMoves=len(plan['physicalMoves']),nativeAssignmentPending=plan['nativeAssignmentPending'],manifestSha256=sha(read(out/'manifest.json',max_bytes=128*1024*1024)),nativeValidation='not_run')
