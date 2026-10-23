"""Target-independent validation of the existing normalize schema and evidence bindings."""
from ..io import safe, stage_document, stage_manifest, read, load, sha, inside
from ..sources.compiled import fail


def input_ir(path, bindings_path=None):
    path=safe(path);ir=stage_document(path)
    if ir.get('schemaVersion')!=1 or ir.get('sourceProfile') not in ('cocos-2.4.15-bundle','cocos-2.4.15-project'):
        fail('UNSUPPORTED_IR',str(path),'Expected supported normalize schema 1')
    expected={f['path']:f['sha256'] for f in stage_manifest(path.parent)['files']}
    bindings={};receipt=None
    if bindings_path:
        raw=read(bindings_path);receipt=load(raw)
        if receipt.get('sourceManifestSha256')!=ir['sourceManifestSha256']:
            fail('BINDING_SOURCE_MISMATCH',str(bindings_path),'Binding source differs')
        evidence=next((e for e in ir.get('evidenceFiles',[]) if e['sha256']==receipt.get('evidenceSha256')),None)
        offset,length=receipt.get('offset'),receipt.get('bytes')
        if evidence is None:fail('BINDING_EVIDENCE_MISSING',str(bindings_path),'Missing explicit evidence')
        if type(offset) is not int or type(length) is not int or offset<0 or length<=0 or offset+length>evidence['bytes']:
            fail('BINDING_EVIDENCE_RANGE',str(bindings_path),'Invalid evidence range')
        labels={c['sourceId']:c for c in ir['components'] if c['type']=='cc.Label'}
        for b in receipt.get('labelFonts',[]):
            sid=b['component']
            if sid not in labels:fail('UNKNOWN_BINDING_COMPONENT',sid,'Not a Label')
            if sid in bindings:fail('DUPLICATE_BINDING',sid,'Duplicate font binding')
            if labels[sid].get('font') is not None:fail('BINDING_REPLACES_EXPLICIT_FONT',sid,'Only absent source fonts may be bound')
            if not isinstance(b.get('font'),str) or type(b.get('syntheticBold',False)) is not bool:
                fail('INVALID_FONT_BINDING',sid,'Expected typed font and syntheticBold')
            bindings[sid]=b
        receipt=dict(receipt,sha256=sha(raw))
    nodes={n['sourceId']:n for n in ir['nodes']}
    if len(nodes)!=len(ir['nodes']):fail('DUPLICATE_NODE',str(path),'Duplicate source node')
    for sid,n in nodes.items():
        if n['parent'] is not None and n['parent'] not in nodes:fail('MISSING_PARENT',sid,'Parent absent')
        if len(n['children'])!=len(set(n['children'])):fail('INVALID_NODE_GRAPH',sid,'Duplicate child')
        for child in n['children']:
            if child not in nodes or nodes[child]['parent']!=sid:fail('INVALID_NODE_GRAPH',sid,'Inconsistent child')
        if n['parent'] and sid not in nodes[n['parent']]['children']:fail('INVALID_NODE_GRAPH',sid,'Parent lacks child')
        cursor=sid;seen=set()
        while cursor is not None:
            if cursor in seen:fail('NODE_CYCLE',sid,'Parent cycle')
            seen.add(cursor);cursor=nodes[cursor]['parent']
    def resource(relative):
        raw=read(inside(path.parent,relative))
        if expected.get(relative)!=sha(raw):fail('SOURCE_CHANGED',relative,'Normalized resource changed')
        return raw
    def resolve(value):
        seen=set()
        while value in ir.get('aliases',{}):
            if value in seen:fail('REDIRECT_CYCLE',str(value),'Alias cycle')
            seen.add(value);value=ir['aliases'][value]
        return value
    return path,ir,bindings,receipt,resource,resolve


def tasks(components, diagnostics, target, manual):
    types={c['sourceId']:c['type'] for c in components};groups={}
    for d in diagnostics:
        sid=d.get('sourceId') or 'resources';module=sid.split('#')[0] if '#' in sid else 'resources'
        kind=types.get(sid,'source');code=d['code']
        if 'BUSINESS' in code:cause='button-business'
        elif kind in ('cc.Label','cc.LabelOutline') or any(t in code for t in ['FONT','LABEL','BITMAP']):cause='text-and-font'
        elif kind in ('cc.SortRoot','cc.SortOrder'):cause='render-order'
        elif kind in ('cc.Widget','cc.Layout','cc.ScrollView','cc.Mask'):cause='native-layout'
        elif any(t in code for t in ['ASSET','SPRITE','TEXTURE','NATIVE','REFERENCE']):cause='asset-binding'
        elif any(t in code for t in ['CONFIG','IDENTITY']):cause='source-format'
        else:cause='unknown-components-and-behavior'
        groups.setdefault((module,cause),[]).append(d)
    return [dict(taskId='module-'+sha((m+'/'+c).encode())[:12],module=m,moduleName=m,rootCause=c,
                 sourceRefs=sorted({str(d.get('sourceId') or d['location']) for d in gaps}),gaps=gaps,
                 generatedTargets=[target],allowedPaths=[manual],verificationScope=['native import/readback','source comparison'])
            for (m,c),gaps in sorted(groups.items())]
