"""Isolated fixed UnityPy provider protocol; never resolves/executes source scripts."""
import base64
import hashlib
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

PROVIDER_VERSION = '1.25.3'
MAX_BYTES = 128 * 1024 * 1024
MAX_OBJECTS = 250_000
MAX_VALUES = 4_000_000


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def identifier(value):
    if type(value) is not int or not -(1 << 63) <= value < (1 << 63):
        raise ValueError('Expected signed 64-bit Unity identifier')
    return str(value)


def portable(value, refs, location='$', depth=0, counter=None):
    """PPtr fields are typed strings; arbitrary large integers are lossless tagged values."""
    if counter is None:
        counter = [0]
    counter[0] += 1
    if counter[0] > MAX_VALUES or depth > 96:
        raise ValueError('Typed value budget exceeded')
    if isinstance(value, dict):
        if set(value) == {'m_FileID', 'm_PathID'}:
            file_id, path_id = identifier(value['m_FileID']), identifier(value['m_PathID'])
            refs.append(dict(location=location, fileId=file_id, pathId=path_id))
            return {'$type': 'UnityPPtr', 'fileId': file_id, 'pathId': path_id}
        return {str(k): portable(v, refs, location + '/' + str(k), depth+1, counter) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [portable(v, refs, location + '/' + str(i), depth+1, counter) for i, v in enumerate(value)]
    if isinstance(value, bytes):
        return {'$type': 'bytes', 'base64': base64.b64encode(value).decode(), 'sha256': digest(value), 'bytes': len(value)}
    if isinstance(value, str):
        try:
            value.encode('utf-8')
            return value
        except UnicodeEncodeError:
            # UnityPy uses surrogateescape for arbitrary binary TextAsset bodies.
            return portable(value.encode('utf-8', errors='surrogateescape'), refs, location, depth+1, counter)
    if type(value) is int:
        return {'$type': 'integer', 'decimal': str(value)} if abs(value) > (1 << 53)-1 else value
    if isinstance(value, float) and not math.isfinite(value):
        return {'$type': 'nonfinite', 'value': repr(value)}
    if value is None or isinstance(value, (bool, float)):
        return value
    raise ValueError('Unsupported typed value ' + type(value).__name__)


def texture_payload(typed):
    payload=typed.get('image data')
    if not isinstance(payload,bytes) or not payload:
        return dict(kind='empty-or-streamed',resourceResolution='not_evaluated')
    if len(payload)<256 and payload[0]==len(payload)-1:
        try:key=payload[1:].decode('ascii')
        except UnicodeDecodeError:key=''
        if re.fullmatch(r'[^/\\\x00]{1,240}\.[0-9a-f]{8}',key):
            return dict(kind='external-key-token-candidate',key=key,bytes=len(payload),sha256=digest(payload),
                        resourceResolution='required',nativePixelsVerified=False)
    return dict(kind='inline-payload',bytes=len(payload),sha256=digest(payload),nativePixelsVerified=False)


def schema_node(node,depth=0):
    if depth>64:raise ValueError('Embedded schema depth budget')
    return dict(name=node.m_Name,type=node.m_Type,children=[schema_node(n,depth+1) for n in node.m_Children])


def inspect_bytes(raw):
    import UnityPy
    if UnityPy.__version__ != PROVIDER_VERSION:
        raise RuntimeError('Expected UnityPy ' + PROVIDER_VERSION)
    env = UnityPy.load(raw)  # bytes only: no source-side sibling or cache discovery
    assets = env.assets
    if not assets:
        raise ValueError('No serialized files found')
    if sum(len(f.objects) for f in assets) > MAX_OBJECTS:
        raise ValueError('Object budget exceeded')
    files, objects, schemas = [], [], {}
    for index, asset in enumerate(assets):
        file_id = str(index)
        externals = [dict(fileId=str(i+1), path=e.path, guid=e.guid.hex()) for i, e in enumerate(asset.externals)]
        files.append(dict(id=file_id, name=asset.name, unityVersion=asset.unity_version,
                          sourceTypeTreeEnabled=asset._enable_type_tree, externals=externals, objects=len(asset.objects)))
        for obj in asset.objects.values():
            row = dict(file=file_id, pathId=identifier(obj.path_id), classId=int(obj.type), type=obj.type.name,
                       bytes=obj.byte_size, rawSha256=digest(obj.get_raw_data()), references=[],
                       typeTreeSource='embedded' if asset._enable_type_tree and obj.serialized_type and obj.serialized_type.node else 'provider-version-schema')
            if obj.type.name=='MonoBehaviour' and asset._enable_type_tree and obj.serialized_type and obj.serialized_type.node:
                shape=schema_node(obj.serialized_type.node)
                shape_id=digest(json.dumps(shape,sort_keys=True,separators=(',',':')).encode())
                schemas[shape_id]=shape;row['embeddedSchemaId']=shape_id
            try:
                typed = obj.read_typetree(check_read=True)
                row['data'] = portable(typed, row['references'])
                if obj.type.name=='Texture2D' and isinstance(typed,dict):row['texturePayload']=texture_payload(typed)
                name = typed.get('m_Name') if isinstance(typed,dict) else None
                row['name'] = name if isinstance(name,str) and not any(0xd800 <= ord(c) <= 0xdfff for c in name) else None
                row['status'] = 'parsed'
            except Exception as error:
                # No relaxed read, zero-fill, guessed schema or source assembly execution.
                row['status'] = 'unparsed'
                row['references'] = []
                row['error'] = dict(type=type(error).__name__, message=str(error).splitlines()[0][:240])
            objects.append(row)
    return dict(schemaVersion=1, sourceFamily='unity', provider=dict(name='UnityPy',version=PROVIDER_VERSION),
                identifierEncoding='signed-int64-decimal-string-v1', files=files, objects=objects, embeddedSchemas=schemas,
                summary=dict(serializedFiles=len(files), objects=len(objects),
                             parsed=sum(o['status']=='parsed' for o in objects),
                             unparsed=sum(o['status']=='unparsed' for o in objects), externalTextureTokens=sum(o.get('texturePayload',{}).get('kind')=='external-key-token-candidate' for o in objects), types=dict(Counter(o['type'] for o in objects))),
                sourceCodeExecuted=False, externalFilesResolved=False, nativeExport='not_run')


def main():
    source, output = map(Path, sys.argv[1:])
    with source.open('rb') as stream:
        raw = stream.read(MAX_BYTES+1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Input byte budget exceeded')
    data = inspect_bytes(raw)
    data['source'] = dict(bytes=len(raw), sha256=digest(raw))
    encoded = (json.dumps(data,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n').encode()
    if len(encoded) > MAX_BYTES:
        raise ValueError('Typed output byte budget exceeded')
    output.write_bytes(encoded)


if __name__ == '__main__':
    main()
