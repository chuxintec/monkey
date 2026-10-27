"""Architecture-first recovery stages over frozen source evidence, not old draft files."""
from __future__ import annotations
import collections
import json
from pathlib import Path
import re
import time
from .candidate_snapshot import snapshot
from .io import inside,read,load,sha,encoded,safe
from .sources.compiled import fail
from . import code_postprocess as worker

SCHEMA='monkey-native-code-architecture/1'
PLAN_PATH='Analysis/Architecture/architecture.json'
LAYERS={
    'Domain':[], 'Gameplay':['Domain'], 'Presentation':['Domain','Gameplay'],
    'Services':['Domain','Gameplay'], 'Bootstrap':['Domain','Gameplay','Presentation','Services'],
}


def _json(path):
    return load(read(safe(path),max_bytes=128*1024*1024),max_nodes=8_000_000)


def _save(path,value):
    worker._atomic(Path(path),encoded(value))


def _shard_members(catalog,contexts):
    """Keep a whole-project catalog bounded without dropping indexed member evidence."""
    pending=[];size=0;parts=[]
    def flush():
        nonlocal pending,size
        if not pending:return
        path=f'MemberCatalog/Part{len(parts)+1:04d}.json'
        raw=json.dumps(dict(schemaVersion=1,units=pending),ensure_ascii=False,separators=(',',':')).encode()
        contexts[path]=raw;parts.append(dict(path=path,sha256=sha(raw),bytes=len(raw)))
        ids={r['sourceUnitId']for r in pending}
        for unit in catalog['sourceUnits']:
            if unit['id']in ids:unit['memberCatalogPaths']=['__Context/'+path]
        pending=[];size=0
    for unit in catalog['sourceUnits']:
        members=unit.pop('members',[]);unit['memberCount']=len(members)
        bindings=unit.pop('bindings',[])
        if bindings:unit['bindingCount']=len(bindings)
        if not members:continue
        row=dict(sourceUnitId=unit['id'],members=members)
        amount=len(json.dumps(row,ensure_ascii=False,separators=(',',':')).encode())
        if pending and size+amount>2*1024*1024:flush()
        if amount>worker.FILE_BYTES-1024:fail('CODE_ARCHITECTURE_BUDGET',unit['id'],'One owner member catalog exceeds its bounded context')
        pending.append(row);size+=amount
    flush();catalog['memberShards']=parts


def _catalog_for_validation(root,request):
    raw=read(root/'Evidence/source-catalog.json',max_bytes=worker.FILE_BYTES)
    if sha(raw)!=request['catalogSha256']:fail('CODE_ARCHITECTURE_SOURCE',str(root),'Architecture catalog changed after preparation')
    catalog=load(raw,max_nodes=8_000_000);units={u['id']:u for u in catalog['sourceUnits']};seen=set()
    for part in catalog.get('memberShards',[]):
        raw=read(inside(root/'Evidence',part['path']),max_bytes=worker.FILE_BYTES)
        if sha(raw)!=part['sha256']or len(raw)!=part['bytes']:fail('CODE_ARCHITECTURE_SOURCE',part['path'],'Member shard changed after preparation')
        for row in load(raw,max_nodes=1_000_000)['units']:
            identity=row['sourceUnitId']
            if identity not in units or identity in seen:fail('CODE_ARCHITECTURE_SOURCE',identity,'Unknown or duplicate source owner in member shards')
            seen.add(identity);units[identity]['members']=row['members']
    for unit in units.values():
        if len(unit.get('members',[]))!=unit['memberCount']:fail('CODE_ARCHITECTURE_SOURCE',unit['id'],'Member shard coverage differs')
    return catalog


def build_catalog(candidate,expected_manifest):
    """Read the existing whole-source index once; retain all registered and residual bytes."""
    root,manifest,owned,pin=snapshot(candidate)
    if pin!=expected_manifest:fail('CODE_ARCHITECTURE_SOURCE',str(root),'Frozen source manifest pin differs')
    inputs={};contexts={}
    def owned_bytes(path,maximum=64*1024*1024):
        if path in inputs:return inputs[path]
        row=owned.get(path)
        if not row:fail('CODE_ARCHITECTURE_SOURCE',path,'Required evidence is outside the owning inventory')
        raw=read(inside(root,path),max_bytes=maximum)
        if sha(raw)!=row['sha256'] or len(raw)!=row['bytes']:
            fail('CODE_ARCHITECTURE_SOURCE',path,'Frozen evidence bytes differ from their owning inventory')
        inputs[path]=raw;return raw
    package=load(owned_bytes('Analysis/Code/package-csharp-drafts.json'),max_nodes=500_000)
    index=load(owned_bytes('Analysis/Code/code-index.json'),max_nodes=8_000_000)
    sources=[];by_snapshot={};source_raw={}
    for item in package.get('sources',[]):
        identity=item['source']['sha256'];candidates=item.get('sourceMembers',[])
        path=next((p for p in candidates if p in owned),None)
        if path is None:fail('CODE_ARCHITECTURE_SOURCE',identity,'Pinned original source member is unavailable')
        raw=owned_bytes(path,worker.FILE_BYTES)
        if sha(raw)!=identity:fail('CODE_ARCHITECTURE_SOURCE',path,'Original source SHA differs from package index')
        context='Sources/'+identity[:12]+'.js';contexts[context]=raw;source_raw[identity]=raw
        snapshots=[p.removeprefix('SourceRecovery/Code/Source/') for p in candidates]
        for name in snapshots:by_snapshot[name]=identity
        sources.append(dict(sha256=identity,bytes=len(raw),sourcePath=path,contextPath='__Context/'+context,snapshotPaths=snapshots))
    if not sources:fail('CODE_ARCHITECTURE_SOURCE',str(root),'No complete indexed original source was supplied')
    units={};intervals=collections.defaultdict(list);member_count=0
    for item in index.get('modules',[]):
        if item.get('entryType')!='module_candidate':continue
        source_name=item.get('sourceSnapshotPath') or item.get('sourceFile')
        identity=by_snapshot.get(source_name);span=item.get('source_bytes',{})
        a,b=span.get('start'),span.get('end')
        if identity is None or type(a)is not int or type(b)is not int or not 0<=a<b<=len(source_raw[identity]):
            fail('CODE_ARCHITECTURE_SOURCE',str(item.get('sourceId')),'Registered module lacks an exact complete-source span')
        raw=source_raw[identity];digest=sha(raw[a:b])
        if digest!=item.get('sha256'):fail('CODE_ARCHITECTURE_SOURCE',str(item.get('sourceId')),'Registered module slice SHA differs')
        unit_id=f'module:{identity[:12]}:{a}:{b}'
        if unit_id in units:
            units[unit_id]['sourceNames'].append(item['name']);units[unit_id]['sourceIds'].append(item['sourceId']);continue
        members=[]
        for kind,rows in item.get('syntax',{}).get('members',{}).items():
            if kind not in ('functions','methods','fields') or not isinstance(rows,list):continue
            for member in rows:
                ms=member.get('sourceBytes')or{};lo,hi=ms.get('start'),ms.get('end')
                if type(lo)is not int or type(hi)is not int or not a<=lo<hi<=b:continue
                md=sha(raw[lo:hi])
                if md!=member.get('sourceSha256'):fail('CODE_ARCHITECTURE_SOURCE',unit_id,'Indexed member span SHA differs')
                members.append(dict(id=f'{identity[:12]}:{kind}@{lo}:{hi}',kind=kind,name=member.get('name'),
                    sourceBytes=dict(start=lo,end=hi),sourceSha256=md,parameters=member.get('parameters',[]),
                    sourceType=member.get('sourceType')or member.get('returnType'),static=member.get('static',False)))
        member_count+=len(members);intervals[identity].append((a,b))
        units[unit_id]=dict(id=unit_id,kind='registered-source-module',sourceNames=[item['name']],sourceIds=[item['sourceId']],
            sourceSha256=identity,sourceBytes=dict(start=a,end=b),spanSha256=digest,
            priorLayerHint=item.get('layer'),priorModuleHint=item.get('codeModule'),hintsAreNotArchitecture=True,
            members=members,dependencies=item.get('dependencies',[]),bindings=item.get('targetBindings',[]),
            syntaxTruncated=bool(item.get('syntax',{}).get('truncated')))
    for source in sources:
        identity=source['sha256'];raw=source_raw[identity];cursor=0;merged=[]
        for a,b in sorted(intervals[identity]):
            if merged and a<=merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
            else:merged.append((a,b))
        for a,b in merged+[(len(raw),len(raw))]:
            if cursor<a:
                unit_id=f'residual:{identity[:12]}:{cursor}:{a}'
                units[unit_id]=dict(id=unit_id,kind='unregistered-source-range',sourceNames=[],sourceIds=[],
                    sourceSha256=identity,sourceBytes=dict(start=cursor,end=a),spanSha256=sha(raw[cursor:a]),members=[],
                    classification='unknown; inspect native-replacement/SDK/helper/business ownership, do not omit')
            cursor=max(cursor,b)
    configs=[];assets=[]
    for path,row in owned.items():
        if path.startswith('Assets/Game/Content/Config/') and path.endswith('.json'):
            configs.append(dict(path=path,sha256=row['sha256'],bytes=row['bytes']))
        elif path.startswith('Assets/Game/Content/') and path.endswith(('.prefab','.unity')):
            assets.append(dict(path=path,sha256=row['sha256'],bytes=row['bytes']))
    bindings_path='Analysis/Code/component-code-bindings.json'
    if bindings_path in owned:contexts['component-code-bindings.json']=owned_bytes(bindings_path,worker.FILE_BYTES)
    config_budget=min(24*1024*1024,worker.INPUT_BYTES-sum(map(len,contexts.values()))-worker.FILE_BYTES)
    for i,config in enumerate(sorted(configs,key=lambda r:r['bytes'])):
        if config['bytes']>worker.FILE_BYTES or config['bytes']>config_budget:
            config['contextOmitted']='bounded global-design context; exact owning identity retained for module-stage input'
            continue
        raw=owned_bytes(config['path'],worker.FILE_BYTES)
        context='Config/'+str(i)+'.json';contexts[context]=raw;config['contextPath']='__Context/'+context
        config_budget-=len(raw)
    catalog=dict(schemaVersion=1,sourceManifestSha256=pin,sourceRoot=str(root),sourceManifestName=manifest['_manifestName'],
        sourceUnits=list(units.values()),sources=sources,configurations=configs,assets=assets,registeredMemberCount=member_count,
        sourceExecuted=False,scope='Complete registered source regions plus every complementary original-source byte range; old draft filenames are not implementation units')
    return catalog,contexts


def _contract(namespace):
    return dict(schemaVersion=SCHEMA,rootNamespace=namespace,layerDependencies=LAYERS,
        requiredPlanKeys=['schemaVersion','sourceManifestSha256','rootNamespace','modules','classes','sourceCoverage','entryPoint','integrationChains','limitations'],
        moduleShape=dict(id='SemanticModule',responsibility='specific source feature',sourceUnitIds=[],classIds=[]),
        classShape=dict(id='stable-target-id',name='SemanticClass',layer='Domain',module='SemanticModule',kind='class',
            responsibility='actual function',stateOwnership='single writer and state boundary',lifecycle='creation/init/use/dispose owner',
            dependsOn=['Domain'],typeDependencies=[],sourceUnitIds=[],fields=[dict(name='Value',type='int',role='source-backed state')],
            methods=[dict(name='Apply',returnType='void',parameters=[],sourceMemberIds=[])]),
        coverageShape=dict(sourceUnitId='exact catalog id',disposition='planned|native-replacement|existing-implementation|evidence-only|blocked',classIds=[],reason='specific evidence and target/adaptation/unknown'),
        entryPointShape=dict(classId='Bootstrap target class ID',initializationOrder=[]),
        integrationChainShape=dict(id='core-chain',classIds=[],configPaths=[],assetPaths=[],behavior='real input through all layers',sourceUnitIds=[]),
        constraints=['dependsOn contains layer names; typeDependencies contains exact target class IDs, including ports and shared state',
            'sourceMemberIds must name actual catalog member IDs from the class sourceUnitIds; no invented source identities',
            'Domain and Gameplay have no Unity dependency','Presentation calls Gameplay; Services implement Gameplay ports; Bootstrap composes',
            'Every catalog source unit appears exactly once in sourceCoverage; do not reduce scope to samples',
            'Semantic types and meaningful fields/method signatures; no Function_x/Unresolved_x folders or giant dynamic object core',
            'Native Unity components, explicit typed state/ports and real JSON resource associations; no source-engine runtime or fake backend',
            'Unknown SDK/backend/source behavior is explicit evidence-only/blocked/native-replacement, not invented successful behavior',
            'This architecture design is an executable generation contract, not a compilation or recovery completion claim'])


def prepare(candidate,expected_manifest,output,*,namespace='Game',codex=worker.DEFAULT_CODEX,timeout_seconds=3600,idle_seconds=900):
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*(?:\.[A-Za-z_][A-Za-z0-9_]*)*',namespace):fail('CODE_ARCHITECTURE_NAMESPACE',namespace,'Expected an ASCII C# root namespace')
    root=safe(output)
    if root.exists():fail('CODE_ARCHITECTURE_OUTPUT',str(root),'Require a new independent stage directory')
    catalog,contexts=build_catalog(candidate,expected_manifest)
    source=safe(candidate)
    if root.is_relative_to(source)or source.is_relative_to(root):fail('CODE_ARCHITECTURE_OUTPUT',str(root),'Stage must not overlap original candidate')
    root.mkdir(parents=True);context=root/'Evidence';context.mkdir();seed=root/'Seed';seed.mkdir()
    _shard_members(catalog,contexts)
    contexts.update({'source-catalog.json':encoded(catalog),'architecture-contract.json':encoded(_contract(namespace))})
    for relative,raw in contexts.items():
        target=inside(context,relative);target.parent.mkdir(parents=True,exist_ok=True);worker._atomic(target,raw)
    initial=encoded(dict(schemaVersion=SCHEMA,sourceManifestSha256=expected_manifest,rootNamespace=namespace,
        modules=[],classes=[],sourceCoverage=[],entryPoint={},integrationChains=[],limitations=['Architecture not designed yet']))
    target=inside(seed,PLAN_PATH);target.parent.mkdir(parents=True);worker._atomic(target,initial)
    manifest=encoded(dict(schemaVersion=1,identity='native-architecture-seed',files=[dict(path=PLAN_PATH,owner='generated',sha256=sha(initial),bytes=len(initial))]))
    worker._atomic(seed/'manifest.json',manifest)
    task='''Design the whole project native Unity code architecture once, using ALL source units in source-catalog.json and exact original JS context as data. Read the global module/field/method relationships and original bodies where needed; do not walk old generated draft filenames. Rewrite the sole selected architecture.json to satisfy architecture-contract.json. Determine actual feature modules, core semantic classes, typed fields/method signatures, state owners, ports, lifecycles and layer dependencies BEFORE implementation. Cover every source unit, including unregistered ranges, SDK/platform and unknown backend with a concrete disposition. Do not claim unresolved dynamic factories are native classes. Do not blindly preserve prior name-suffix layer hints. Design complete feature classes across layers, not a two-method sample or generic empty framework. Plan source-to-target ownership via sourceUnitIds and method sourceMemberIds; body implementation is the next module stage. Domain/Gameplay must be engine-free; Services implement ports; Bootstrap composes real config/resource-to-input-to-rule-to-view chains. No JS/Cocos interpreter, all-dynamic object system, fake success backend or copying the formal game. Use concise source-specific reasons and shared limitations, not repetitive long proofs. Do not execute original source, engines, compilers, network, other agents/CLIs, or change model/config. Only rewrite the selected JSON; report complete means architecture plan designed, never implementation/compilation/gameplay complete.'''
    prepared=worker.prepare(seed,[PLAN_PATH],sha(manifest),root/'Task',task,context_root=context,context_files=list(contexts),
        architecture_stage=True,codex=codex,timeout_seconds=timeout_seconds,no_progress_seconds=idle_seconds,max_resumes=2)
    _save(root/'request.json',dict(schemaVersion=1,stage='global-architecture',sourceRoot=str(source),sourceManifestSha256=expected_manifest,
        catalogSha256=sha(contexts['source-catalog.json']),planPath=PLAN_PATH,task=str(prepared.output),namespace=namespace,createdAt=time.time()))
    _save(root/'state.json',dict(status='prepared',stage='global-architecture',sourceUnits=len(catalog['sourceUnits']),implementation='not_started',compilation='not_run',runtime='not_run'))
    return status(root)


def run(output,*,session_id=None):
    root=safe(output);request=_json(root/'request.json');result=worker.run(root/'Task',session_id=session_id)
    if result.get('blockingCondition'):
        _save(root/'state.json',dict(status='blocked',stage=request['stage'],blocker=result['blockingCondition'],implementation='not_started',compilation='not_run',runtime='not_run'))
        return status(root)
    if _json(root/'Task/request.json').get('state')=='checkpoint':
        _save(root/'state.json',dict(status='checkpoint',stage=request['stage'],sessionId=result.get('sessionId'),implementation='not_started',compilation='not_run',runtime='not_run'))
        return status(root)
    if result.get('unexpectedPaths') or result.get('workspaceIntegrityErrors') or result.get('sourceVerificationErrors') or not result.get('gitBoundary',{}).get('valid'):
        fail('CODE_ARCHITECTURE_BOUNDARY',str(root),'Stage write or source boundary failed; preserve the task evidence')
    if result.get('stopReason') or result.get('status')=='failed':
        _save(root/'state.json',dict(status='stage_incomplete',stage=request['stage'],reason=result.get('stopReason'),implementation='not_started',compilation='not_run',runtime='not_run'))
        return status(root)
    actual={r['path']:r for r in result.get('actualChanges',[])}
    if set(actual)!=set(result.get('declaredChangedPaths',[])):
        fail('CODE_ARCHITECTURE_BOUNDARY',str(root),'Declared paths differ from the actual stage patch')
    payload=read(root/'Task/workspace'/request['planPath'],max_bytes=worker.FILE_BYTES)
    if request['planPath']not in actual or sha(payload)!=actual[request['planPath']].get('afterSha256'):
        fail('CODE_ARCHITECTURE_BOUNDARY',str(root),'Architecture payload differs from its recorded stage patch')
    from .code_architecture_contract import validate_architecture
    catalog=_catalog_for_validation(root,request);plan=_json(root/'Task/workspace'/request['planPath'])
    try:validation=validate_architecture(plan,catalog)
    except ValueError as error:
        _save(root/'state.json',dict(status='invalid_architecture',stage=request['stage'],error=str(error),implementation='not_started',compilation='not_run',runtime='not_run'));raise
    _save(root/'architecture.json',plan);_save(root/'validation.json',validation)
    _save(root/'state.json',dict(status='architecture_designed',stage=request['stage'],sourceUnits=len(catalog['sourceUnits']),classes=len(plan['classes']),modules=len(plan['modules']),architectureSha256=sha(read(root/'architecture.json',max_bytes=worker.FILE_BYTES)),validationSha256=sha(read(root/'validation.json',max_bytes=worker.FILE_BYTES)),modelStatus=result['status'],unresolved=result.get('unresolved',[]),implementation='not_started',compilation='not_run',runtime='not_run'))
    return status(root)


def status(output):
    root=safe(output);state=_json(root/'state.json');process=root/'Task/process.json'
    if process.is_file():
        child=_json(process);state={**state,'childState':child.get('state'),'childPid':child.get('pid')}
        if child.get('state')in ('starting','running') and state['status'] in ('prepared','checkpoint'):
            state['status']='running'
    return {**state,'report':str(root/'state.json'),'workspace':str(root/'Task/workspace')}
