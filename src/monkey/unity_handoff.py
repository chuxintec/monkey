"""Count actual native files separately from source objects and retained evidence."""
import collections
import re
from pathlib import Path
from .io import read,load,sha,write_json


def inventory(project,inspections,exported):
    native=[];by_path={};guids=collections.defaultdict(list)
    for p in sorted((project/'Assets').rglob('*')):
        if not p.is_file()or p.suffix.lower()in ('.meta','.cs','.dll','.asmdef','.asmref','.js','.wasm'):continue
        rel=p.relative_to(project).as_posix();meta=p.with_suffix(p.suffix+'.meta')
        guid=None
        if meta.is_file():
            found=re.findall(rb'^guid: ([0-9a-f]{32})\r?$',read(meta),re.M)
            if len(found)==1:guid=found[0].decode()
        row=dict(path=rel,bytes=p.stat().st_size,sha256=sha(read(p,max_bytes=128*1024**2)),guid=guid,kind=p.suffix.lower()or'extensionless',nativeImport='not_run')
        native.append(row);by_path.setdefault(rel.casefold(),[]).append(row)
        if guid:guids[guid].append(row)
    roots=[];objects=0;unparsed=0;containers=[]
    for index,(source,receipt)in enumerate(inspections):
        stage=project.parent/('SourceInspection'if index==0 else'DependencyInspection-'+str(index-1));d=load(read(stage/'typed-objects.json',max_bytes=128*1024**2),max_nodes=16_000_000,max_depth=128)
        files={f['id']:f for f in d['files']};objects+=len(d['objects']);unparsed+=sum(o['status']!='parsed'for o in d['objects'])
        containers.append(dict(source=receipt['source'],disposition='submitted-to-native-provider',nativeProviderStatus=exported['status']))
        for o in d['objects']:
            if o['type']!='AssetBundle'or o['status']!='parsed':continue
            for entry in o['data'].get('m_Container',[]):
                if not isinstance(entry,list)or len(entry)!=2 or not isinstance(entry[0],str):continue
                logical,value=entry;ptr=value.get('asset',{})if isinstance(value,dict)else{}
                original=dict(containerSha256=receipt['source']['sha256'],file=files[o['file']]['name'],pathId=ptr.get('pathId'),fileId=ptr.get('fileId'),logicalPath=logical)
                matches=by_path.get(logical.casefold(),[])
                roots.append(dict(source=original,status='exact-original-container-path-candidate'if len(matches)==1 and matches[0]['guid']else'unmapped-original-asset-path',
                                  target=matches[0]if len(matches)==1 and matches[0]['guid']else None))
    unique_roots={(r['source']['file'],r['source']['fileId'],r['source']['pathId'])for r in roots}
    counts=dict(collections.Counter(r['kind']for r in native));duplicates=[dict(guid=g,paths=[r['path']for r in rows])for g,rows in guids.items()if len(rows)>1]
    report=dict(schemaVersion=1,containers=containers,sourceObjects=objects,unparsedSourceObjects=unparsed,
                originalContainerEntries=len(roots),uniqueOriginalContainerReferences=len(unique_roots),sourceToTarget=roots,
                nativeFiles=native,uniqueNativeGuids=len(guids),nativeFilesWithoutGuid=sum(r['guid']is None for r in native),
                duplicateNativeGuids=duplicates,counts=counts,native='not_run',business='not_run',
                mappingScope='Only unique exact original AssetBundle container path -> exported Assets path; no name-only fallback',
                sourceObjectCountIsNotNativeAssetCount=True)
    write_json(project/'Analysis/full-resource-handoff.json',report)
    start=project/'Docs/START-HERE.md'
    start.write_text('''# AI development handoff

This is a bulk Unity 6 editable resource candidate. Open ProjectSettings/ProjectVersion.txt's exact Editor version.
Read Analysis/full-resource-handoff.json first: actual native files/GUIDs, original logical assets and unmapped items are separate.
SourceRecovery/Original retains every unique explicitly supplied container. Lookup/schema copies are evidence, not extra native assets.
Analysis/all-typed-objects.json (when present) preserves exact source file/pathID, references and parsed fields across the full input set.
Analysis/unity-code-model.json contains proven named field classes; SourceRecovery/OriginalCode and CodeDrafts retain original code and metadata signatures/TODOs.
Metadata-only declarations do not contain recovered business logic; uncompiled drafts remain outside Assets. Do not count empty or unsupported methods as working behavior.
Repair missing script/package/Shader/Spine dependencies using their exact source identities. Never resolve collisions by first matching name or replace unknown logic with fake rewards.
Native import/compile, Editor save/reload, Player and gameplay are separate gates; current native state is not_run unless an independent receipt says otherwise.
''')
    return dict(nativeFiles=len(native),uniqueNativeGuids=len(guids),nativeCounts=counts,sourceObjects=objects,
                originalContainerEntries=len(roots),uniqueOriginalContainerReferences=len(unique_roots),mappedOriginalEntries=sum(r['target']is not None for r in roots),
                duplicateNativeGuids=len(duplicates),report='Analysis/full-resource-handoff.json',native='not_run')
