"""Pinned Creator Spine component/resource stage; source assignments stay explicit."""
from pathlib import Path
from .io import read,load,sha,safe,inside,stage_manifest
from .sources.compiled import fail


def load_binding(ir,ir_path,receipt_path,expected_sha,resources):
    if not any((receipt_path,expected_sha,resources)):return None
    if not all((receipt_path,expected_sha,resources)):fail('SPINE_BINDING_ARGUMENTS','spine','Receipt, SHA and frozen resource root are required together')
    raw=read(safe(receipt_path));record=load(raw)
    if sha(raw)!=expected_sha or record.get('contract')!='monkey-spine-emission/1':fail('SPINE_BINDING_CHANGED','spine','Emission receipt differs')
    pins=record.get('pins',{})
    if pins.get('normalizedIrSha256')!=sha(read(ir_path)) or pins.get('sourceManifestSha256')!=ir['sourceManifestSha256']:
        fail('SPINE_BINDING_SOURCE_MISMATCH','spine','Source manifest or current IR pin differs')
    root=safe(resources);manifest=stage_manifest(root)
    if sha(read(root/'manifest.json'))!=pins.get('creatorClosureReceiptSha256'):
        fail('SPINE_CLOSURE_CHANGED','spine','Frozen resource manifest differs')
    files={x['path']:x for x in manifest['files']};components={x['sourceId']:x for x in ir['components']}
    seen=set()
    for row in record['components']:
        sid=row['sourceComponentId'];c=components.get(sid)
        source_node=row['sourceNodeId']
        numeric_node=type(source_node)is int or (isinstance(source_node,str)and source_node.isascii()and source_node.isdigit())
        node_id=row['sourcePrefabId']+'#'+str(source_node) if numeric_node else source_node
        if sid in seen or not c or c['type']!='sp.Skeleton' or c['node']!=node_id:
            fail('SPINE_COMPONENT_IDENTITY',sid,'Source component or node differs')
        seen.add(sid)
    if len(seen)!=record['sourceComponentCount']:fail('SPINE_COMPONENT_COUNT','spine','Component denominator differs')
    for row in record['copies']:
        if row['target']!='creator':continue
        if not row['path'].startswith('assets/resources/Spine/') or files.get(row['path'],{}).get('sha256')!=row['sha256']:
            fail('SPINE_RESOURCE_IDENTITY',row['path'],'Resource is not owned by the pinned closure')
        raw=read(inside(root,row['path']))
        if sha(raw)!=row['sha256'] or len(raw)!=row['bytes']:fail('SPINE_RESOURCE_CHANGED',row['path'],'Source closure bytes differ')
    return dict(record=record,root=root,receiptSha256=expected_sha)


def prepare(binding,output):
    if not binding:return None
    record=binding['record'];copies=[]
    for row in record['copies']:
        if row['target']!='creator':continue
        source='spine-payloads/'+sha(row['path'].encode())+Path(row['path']).suffix
        raw=read(inside(binding['root'],row['path']));dest=inside(output,source);dest.parent.mkdir(exist_ok=True);dest.write_bytes(raw)
        copies.append(dict(source=source,target=row['path'],sha256=row['sha256']))
    return dict(components=record['components'],assets=record['assets'],copies=copies,
                emissionReceiptSha256=binding['receiptSha256'],sourceComponentCount=record['sourceComponentCount'])


def emit(binding,plan_root,output):
    if not binding:return
    for row in binding['copies']:
        raw=read(inside(plan_root,row['source']))
        if sha(raw)!=row['sha256']:fail('SPINE_RESOURCE_CHANGED',row['source'],'Plan-owned bytes differ')
        dest=inside(output,row['target'])
        if dest.exists():fail('SPINE_RESOURCE_COLLISION',row['target'],'Refuse to replace an existing asset')
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)


def verify(components,rows,owner):
    from .io import diagnostic
    expected={c['sourceId'] for c in components if c.get('convertible') and c.get('spineBinding')}
    if not expected and rows in (None,[]):return []
    if not isinstance(rows,list) or any(not isinstance(row,dict)for row in rows):
        return [diagnostic('SPINE_NATIVE_READBACK_MISSING',owner,'Source component readback absent')]
    actual={r.get('sourceComponentId'):r for r in rows}
    if len(actual)!=len(rows) or set(actual)!=expected:
        return [diagnostic('SPINE_NATIVE_IDENTITY_MISMATCH',owner,'Source component denominator differs')]
    gaps=[]
    for sid,row in actual.items():
        if row.get('status')!='verified' or row.get('failures'):
            gaps.append(diagnostic('SPINE_NATIVE_COMPONENT_INCOMPLETE',sid,str(row.get('status'))+': '+str(row.get('failures',[])),sid))
    return gaps
