"""Serial module implementation and isolated candidate assembly from one architecture.

This stage never treats generated code as compiled or runtime-verified. All model
invocations use the existing bounded worker through the module API.
"""
from __future__ import annotations

import fcntl
from pathlib import Path
import time

from . import code_architecture_modules as modules
from . import code_postprocess as worker
from .io import encoded, inside, read, safe, sha
from .output_limits import copy_verified
from .sources.compiled import fail


def module_order(plan):
    """Prefer implemented dependencies; retain cycles as explicit contract edges."""
    classes={row['id']:row for row in plan['classes']}
    dependencies={row['id']:set() for row in plan['modules']}
    for row in classes.values():
        dependencies[row['module']].update(classes[cid]['module'] for cid in row.get('typeDependencies',[])
                                           if classes[cid]['module']!=row['module'])
    remaining=set(dependencies);order=[];cycles=[]
    while remaining:
        ready=sorted(mid for mid in remaining if not dependencies[mid]&remaining)
        if not ready:
            # A cycle requires the shared typed architecture contract, not fake
            # dependency implementations or a permanently blocked queue.
            selected=min(remaining,key=lambda mid:(-sum(mid in dependencies[other]for other in remaining),len(dependencies[mid]&remaining),mid))
            cycles.append(dict(moduleId=selected,pendingTypeModules=sorted(dependencies[selected]&remaining)))
            ready=[selected]
        order.extend(ready);remaining.difference_update(ready)
    return order,cycles


def prepare(architecture_stage,output,*,codex=worker.DEFAULT_CODEX,timeout_seconds=3600,idle_seconds=900,external_references=None,retained_support_paths=()):
    stage=modules._pin_stage(architecture_stage)
    root=safe(output)
    if root.exists():fail('CODE_NATIVE_OUTPUT',str(root),'Require a new independent pipeline directory')
    for source in (stage['root'],safe(stage['request']['sourceRoot'])):
        if root==source or root.is_relative_to(source) or source.is_relative_to(root):
            fail('CODE_NATIVE_OUTPUT',str(root),'Pipeline must not overlap the architecture or frozen source')
    if type(timeout_seconds)is not int or not 1<=timeout_seconds<=3600 or type(idle_seconds)is not int or not 1<=idle_seconds<=timeout_seconds:
        fail('CODE_NATIVE_BUDGET',str(root),'Each module needs finite total/idle budgets within 3600 seconds')
    order,cycles=module_order(stage['plan']);root.mkdir(parents=True)
    modules._save(root/'request.json',dict(schemaVersion=1,architectureStage=str(stage['root']),**stage['pins'],
        codex=str(codex),timeoutSeconds=timeout_seconds,idleSeconds=idle_seconds,externalReferences=external_references or {},retainedSupportPaths=list(retained_support_paths),
        moduleOrder=order,contractCycleEdges=cycles,createdAt=time.time()))
    modules._save(root/'state.json',dict(status='prepared',modules=[dict(id=mid,status='pending',task=f'Modules/{i+1:04d}')for i,mid in enumerate(order)],
        implementation='not_started',compilation='not_run',runtime='not_run'))
    return status(root)


def _stage(root,request):
    stage=modules._pin_stage(request['architectureStage'])
    if stage['pins']!={key:request.get(key)for key in stage['pins']}:
        fail('CODE_NATIVE_SOURCE',str(root),'Global architecture or frozen source identity changed')
    return stage


def _collect(root,stage,state):
    """Pin model outputs into a fresh aggregate; unreviewed bodies remain partial."""
    aggregate=root/'Implementation'
    if aggregate.exists():fail('CODE_NATIVE_AGGREGATE',str(aggregate),'Existing aggregate may contain manual changes; never overwrite')
    aggregate.mkdir()
    files=[];classes={row['id']:row for row in stage['plan']['classes']};seen=set();module_rows=[]
    for item in state['modules']:
        module_rows.append(dict(id=item['id'],status='partial' if item['status']!='evidence_only' else 'evidence_only'))
        if item['status']=='evidence_only':continue
        task=inside(root,item['task']);report=modules.status(task)
        if report['manifestSha256']!=item['manifestSha256']:
            fail('CODE_NATIVE_MODULE',str(task),'Module receipt changed after generation')
        manifest=modules._json(task/modules.MANIFEST)
        records={row['classId']:row for row in manifest['classes']}
        for row in manifest['files']:
            path=row['targetPath']
            record=next((v for v in records.values()if v['path']==path),None)
            if record is None or stage['validation']['classPaths'].get(record['classId'])!=path or path in seen:
                fail('CODE_NATIVE_MODULE',path,'Module output violates global class ownership')
            seen.add(path)
            if row['status']!='generated_unreviewed':continue
            raw=read(inside(task,row['artifactPath']),max_bytes=worker.FILE_BYTES)
            if sha(raw)!=row['sha256'] or len(raw)!=row['bytes']:
                fail('CODE_NATIVE_MODULE',path,'Module implementation differs from its pinned receipt')
            planned=classes[record['classId']]
            members=sorted({sid for kind in ('fields','methods')for member in planned.get(kind,[])for sid in member.get('sourceMemberIds',[])})
            copy_verified(inside(task,row['artifactPath']),inside(aggregate,path),row['sha256'],row['bytes'],atomic=False)
            files.append(dict(path=path,sha256=row['sha256'],bytes=row['bytes'],owner='generated',classId=record['classId'],
                              sourceUnitIds=sorted(planned['sourceUnitIds']),sourceMemberIds=members,status='partial'))
    raw=encoded(dict(schemaVersion=1,sourceManifestSha256=stage['pins']['sourceManifestSha256'],architectureSha256=stage['pins']['architectureSha256'],
        files=files,modules=module_rows,compilation='not_run',runtime='not_run',acceptance='model_outputs_unreviewed'))
    worker._atomic(aggregate/'manifest.json',raw)
    return aggregate,sha(raw)


def run(output):
    root=safe(output);request=modules._json(root/'request.json')
    with (root/'pipeline.lock').open('a+b')as lock:
        try:fcntl.flock(lock.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:fail('CODE_NATIVE_BUSY',str(root),'Another supervisor owns this pipeline')
        state=modules._json(root/'state.json');stage=_stage(root,request)
        if state['status']=='candidate_assembled_unvalidated':return status(root)
        module_table={row['id']:row for row in stage['plan']['modules']}
        state.update(status='running',implementation='in_progress');modules._save(root/'state.json',state)
        for item in state['modules']:
            if item['status']in ('generated_unreviewed','partial_unimplemented_seed','evidence_only'):continue
            task=inside(root,item['task'])
            if not module_table[item['id']]['classIds']:
                item.update(status='evidence_only');modules._save(root/'state.json',state);continue
            try:
                if not task.exists():
                    dependencies=[str(inside(root,prior['task']))for prior in state['modules']if prior['status']in ('generated_unreviewed','partial_unimplemented_seed')]
                    modules.prepare(stage['root'],item['id'],task,dependency_roots=dependencies,codex=request['codex'],
                        timeout_seconds=request['timeoutSeconds'],idle_seconds=request['idleSeconds'])
                current=modules.status(task)
                item.update(status=current['status']);state['activeModule']=item['id'];modules._save(root/'state.json',state)
                while current['status']in ('prepared','checkpoint'):
                    current=modules.run(task,session_id=current.get('sessionId')if current['status']=='checkpoint' else None)
                    item.update(status=current['status']);modules._save(root/'state.json',state)
            except (ValueError,OSError) as error:
                state.update(status='blocked',blocker=getattr(error,'code','module-execution-error'))
                item.update(status='blocked');state['activeModule']=item['id']
                modules._save(root/'state.json',state);raise
            if current['status']not in ('generated_unreviewed','partial_unimplemented_seed'):
                state.update(status='blocked',blocker=current.get('blocker')or current.get('reason')or current['status'])
                modules._save(root/'state.json',state);return status(root)
            item.update(status=current['status'],manifestSha256=current['manifestSha256']);modules._save(root/'state.json',state)
        aggregate,pin=_collect(root,stage,state)
        from .code_architecture_candidate import assemble_native_candidate
        assembled=assemble_native_candidate(stage['request']['sourceRoot'],request['sourceManifestSha256'],stage['root']/'architecture.json',
            request['architectureSha256'],stage['root']/'validation.json',request['validationSha256'],aggregate,pin,root/'UnityProject',
            external_references=request['externalReferences'],retained_support_paths=request.get('retainedSupportPaths',()),allow_partial=True)
        state.update(status='candidate_assembled_unvalidated',implementation='model_outputs_unreviewed',candidate=str(root/'UnityProject'),
            candidateManifestSha256=sha(read(root/'UnityProject/manifest.json',max_bytes=128*1024*1024)),assemblyStatus=assembled['status'])
        state.pop('activeModule',None);modules._save(root/'state.json',state)
        return status(root)


def status(output):
    root=safe(output);state=modules._json(root/'state.json')
    if state['status']=='running' and state.get('activeModule'):
        active=next((row for row in state['modules']if row['id']==state['activeModule']),None)
        process=inside(root,active['task'])/'Task/process.json' if active else None
        if process and process.is_file():
            child=modules._json(process)
            state.update(childState=child.get('state'),childPid=child.get('pid'))
            if child.get('state')in ('starting','running'):active['status']='running'
    counts={}
    for row in state['modules']:counts[row['status']]=counts.get(row['status'],0)+1
    return {**state,'moduleCounts':counts,'report':str(root/'state.json')}
