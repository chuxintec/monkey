"""Validate native static-carrier field evidence without declaring source completeness."""
from .io import diagnostic


def verify(components, rows, asset_identity, target, owner):
    expected = {c['sourceId']: c['staticFieldBinding'] for c in components if c.get('staticFieldBinding')}
    if not expected and rows in (None, []): return []
    def gap(message): return [diagnostic('STATIC_FIELD_NATIVE_MISMATCH', owner, message, owner)]
    if not isinstance(rows, list) or any(not isinstance(r, dict) or not isinstance(r.get('binding'), dict) for r in rows):
        return gap('Static field readback is absent')
    actual = {r['binding'].get('sourceId'): r for r in rows}
    if len(actual) != len(rows) or set(actual) != set(expected): return gap('Static component identities differ')
    identities = set()
    for sid, spec in expected.items():
        row = actual[sid]; b = row['binding']
        identity = row.get('localFileId') if target == 'unity' else row.get('componentUuid')
        valid = type(identity) is int and identity != 0 if target == 'unity' else isinstance(identity, str) and bool(identity)
        if not valid or identity in identities: return gap('Missing or duplicate persistent component identity: '+sid)
        identities.add(identity)
        if row.get('assetGuid' if target == 'unity' else 'assetUuid') != asset_identity or not asset_identity:
            return gap('Carrier belongs to a different asset: '+sid)
        if (b.get('typeName') != spec['typeName'] or b.get('nativeScriptGuid') != spec['scriptGuid'] or
            b.get('nativeSourceId') != sid or b.get('nativeIdentityVerified') is not True or
            b.get('enabled') is not False or b.get('fieldsVerified') is not True):
            return gap('Saved carrier identity, disabled policy or fields differ: '+sid)
        fields = b.get('fields')
        if not isinstance(fields,list) or any(not isinstance(f,dict) for f in fields):return gap('Missing fields: '+sid)
        by_name={f.get('fieldName'):f for f in fields}
        if len(by_name)!=len(fields) or set(by_name)!={f['fieldName']for f in spec['fields']}:return gap('Field coverage differs: '+sid)
        for f in spec['fields']:
            a=by_name[f['fieldName']]
            if any(a.get(k)!=f.get(k)for k in ('kind','storageType','sourceFieldName')):return gap('Field schema differs: '+sid)
            key={'bool':'boolValue','double':'numberValue','string':'stringValue','bool[]':'boolValues','double[]':'numberValues','string[]':'stringValues','UnityEngine.Object':'refValue','UnityEngine.Object[]':'refValues'}[f['storageType']]
            if a.get(key)!=f.get(key):return gap('Field value differs: '+sid+'/'+f['sourceFieldName'])
            if f['storageType']=='UnityEngine.Object' and a.get('referenceVerified') is not True:return gap('Reference differs: '+sid)
            if f['storageType']=='UnityEngine.Object[]' and a.get('referencesVerified') is not True:return gap('Reference array differs: '+sid)
        if target=='unity':
            refs=row.get('references')
            count=sum(1 if f['storageType']=='UnityEngine.Object' and not f.get('nullExpected') else len(f.get('refValues',[]))if f['storageType']=='UnityEngine.Object[]' else 0 for f in spec['fields'])
            if not isinstance(refs,list) or len(refs)!=count or any(r.get('persistent') is not True or not r.get('guid') or not r.get('localFileId')for r in refs):return gap('Persistent reference identities missing: '+sid)
    return []
