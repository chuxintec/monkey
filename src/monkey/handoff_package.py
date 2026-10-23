"""Join recovered code to literal component identities; aggregate work, retain detail."""
import re
from pathlib import Path
from .io import stage_document,read,load,write_json,sha


def script_identity(value):
    if not isinstance(value,str):return None
    if re.fullmatch('[0-9a-fA-F-]{36}',value):return value.lower()
    prefix=2 if len(value)==22 else 5 if len(value)==23 else None
    alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
    if prefix and re.fullmatch('[0-9a-fA-F]{'+str(prefix)+'}[A-Za-z0-9+/]+',value):
        digits=value[:prefix]
        for i in range(prefix,len(value),2):
            a,b=alphabet.index(value[i]),alphabet.index(value[i+1])
            digits+=f'{a>>2:x}{((a&3)<<2)|(b>>4):x}{b&15:x}'
        return '-'.join((digits[:8],digits[8:12],digits[12:16],digits[16:20],digits[20:])).lower()
    return value


def enrich(project,out,rows,code_index,tasks):
    project=Path(project).resolve();out=Path(out).resolve()
    stage=out/'Structured'
    normalized=stage/'validated-ir' if (stage/'validated-ir/manifest.json').exists() else stage/'normalize'
    ir=stage_document(normalized/'ir.json') if (normalized/'manifest.json').exists() else None
    inspected=stage_document(stage/'inspect/source-manifest.json') if (stage/'inspect/manifest.json').exists() else None
    lookup={};by_code={m['sourceId']:m for m in code_index if m.get('entryType')=='module_candidate'}
    for mod in by_code.values():
        for rf in mod.get('rf',[]):lookup.setdefault(script_identity(rf.get('identity')),[]).append(mod['sourceId'])
    bindings=[];groups={};assigned=set()
    if ir:
        for c in ir['components']:
            matches=sorted(set(lookup.get(script_identity(c['type']),[])))
            if len(matches)!=1:continue
            module=matches[0];page=c['sourceId'].split('#')[0];assigned.add(module)
            binding=dict(sourceComponent=c['sourceId'],sourceNode=c.get('node'),sourceAsset=page,
                         codeRegion=module,evidence='exact_literal_script_identity',nativeComponent='not_implemented')
            bindings.append(binding);groups.setdefault(page,[]).append(binding)
        for mod in by_code.values():mod['targetBindings']=[b for b in bindings if b['codeRegion']==mod['sourceId']]
    aggregates=[]
    for page,links in sorted(groups.items()):
        regions=sorted({b['codeRegion'] for b in links})
        aggregates.append(dict(taskId='view-'+sha(page.encode())[:16],module=page,rootCause='source-component-behavior',
                               sourceRefs=regions,bindings=links,codeState='draft_generated',nativeValidation='not_run',
                               nextAction='Restore this source view/module using its exact decoded objects and source regions; resolve shared dependencies before enabling behavior',
                               allowedPaths=['Assets/Game/','assets/scripts/'],
                               verification=['native references/compile','affected view input','failure/unavailable behavior']))
    pool=sorted(set(by_code)-assigned)
    if pool:
        aggregates.append(dict(taskId='code-unclassified-pool',module='unclassified-source-context',sourceRefs=pool,
                               eligibleForDispatch=False,nextAction='Classify a coherent subset from dependency/resource evidence; this pool is not one Agent task per region',
                               allowedPaths=['SourceRecovery/CodeDrafts/'],verification=['module ownership and external wrapper context']))
    aggregates.extend(t for t in tasks if t['taskId'].startswith('resources-'))
    write_json(project/'Analysis/agent-work-details.json',dict(schemaVersion=1,tasks=tasks))
    write_json(project/'Analysis/agent-work.json',dict(schemaVersion=1,tasks=aggregates,
               detailIndex='Analysis/agent-work-details.json',dispatchPolicy='coherent_module_batches_no_automatic_agents'))
    write_json(project/'Analysis/code-index.json',dict(schemaVersion=1,modules=code_index))
    write_json(project/'Analysis/component-code-bindings.json',dict(schemaVersion=1,bindings=bindings))
    objects=[];by_tree={r['inputRoot']+'/'+r['localPath']:r for r in rows}
    frames={a['sourceId'] for a in ir['spriteFrames']} if ir else set()
    texture_sources={a['textureRef'] for a in ir['spriteFrames']} if ir else set()
    native={a['sourceId'] for a in ir['assets']} if ir else set()
    node_assets={n['sourceId'].split('#')[0] for n in ir['nodes']} if ir else set()
    quarantined={a['sourceId'] for a in ir.get('quarantinedAssets',[])} if ir else set()
    if inspected:
        for asset in inspected['assets']:
            source_root=Path(inspected['sourceRoots'][asset.get('bundle',inspected['bundle'])])
            prefix=source_root.relative_to(out/'InputTree').as_posix()
            file_rows=[by_tree.get(prefix+'/'+asset[k]) for k in ('importPath','native') if asset.get(k)]
            source_ids=[r['sourceId'] for r in file_rows if r]
            record=dict(sourceId=asset['sourceId'],kind=asset.get('kind'),sourceInputs=source_ids,logicalPath=asset.get('logicalPath'),
                        state='decoded_only' if asset.get('document') else 'unresolved',nativeValidation='not_run')
            if asset.get('document'):
                relative='Analysis/Decoded/'+sha(asset['sourceId'].encode())[:24]+'.json'
                dest=project/relative;dest.parent.mkdir(parents=True,exist_ok=True)
                write_json(dest,dict(schemaVersion=1,sourceId=asset['sourceId'],kind=asset.get('kind'),document=asset['document']))
                record['decodedEvidence']=relative
            if ir:
                if asset['sourceId'] in frames:record['state']='normalized_sprite_frame'
                if asset['sourceId'] in texture_sources:record['state']='normalized_texture_dependency'
                if asset['sourceId'] in native:record['state']='normalized_native_payload'
                if asset['sourceId'] in node_assets:record['state']='normalized_node_graph'
                if asset['sourceId'] in quarantined:record['state']='quarantined_graph'
            objects.append(record)
    write_json(project/'Analysis/structured-objects.json',dict(schemaVersion=1,objects=objects))
    return dict(codeRegionDetails=len(by_code),componentBindings=len(bindings),viewBatches=len(groups),unclassifiedRegions=len(pool),
                aggregateTasks=len(aggregates),structuredObjects=len(objects))
