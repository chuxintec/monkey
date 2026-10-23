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
        match=re.fullmatch(r'([^/\\\x00]{1,240}\.[0-9a-f]{8})(?:_([0-9]+)###)?',key)
        if match:
            return dict(kind='external-key-token-candidate',key=match[1],wireKey=key,
                        blockSizeHint=int(match[2]) if match[2] else None,bytes=len(payload),sha256=digest(payload),
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


def astc_header(raw,width,height,hint=None):
    if len(raw)<16 or raw[:4]!=b'\x13\xab\xa1\x5c':raise ValueError('Exact cached payload is not ASTC')
    bx,by,bz=raw[4:7];w=int.from_bytes(raw[7:10],'little');h=int.from_bytes(raw[10:13],'little');d=int.from_bytes(raw[13:16],'little')
    if bx!=by or bx not in (4,5,6,8,10,12) or bz!=1 or d!=1 or w!=width or h!=height or w*h>16_777_216:
        raise ValueError('ASTC block/dimension profile mismatch')
    if hint is not None and hint!=bx:raise ValueError('Wire texture format hint differs from cached ASTC header')
    required=((w+bx-1)//bx)*((h+by-1)//by)*16
    if len(raw)!=required+16:raise ValueError('ASTC payload byte size mismatch')
    return dict(block=bx,width=w,height=h,payloadBytes=required)


def hydrate_manifest(job_path,output):
    import UnityPy
    if UnityPy.__version__!=PROVIDER_VERSION:raise RuntimeError('Expected UnityPy '+PROVIDER_VERSION)
    job=json.loads(job_path.read_text());source=Path(job['source']);raw=source.read_bytes()
    if len(raw)>MAX_BYTES or digest(raw)!=job['sourceSha256']:raise ValueError('Source changed')
    env=UnityPy.load(raw);before={(a.name,identifier(o.path_id)):(o.type.name,digest(o.get_raw_data())) for a in env.assets for o in a.objects.values()}
    pool={x['logicalPath']:x for x in job['cache']};resolved=[];missing=[];modified=set()
    for asset in env.assets:
        if not asset.unity_version.startswith('2021.3.'):raise ValueError('Texture token hydration currently verified for Unity2021.3 profile only')
        for obj in asset.objects.values():
            if obj.type.name!='Texture2D':continue
            typed=obj.read_typetree(check_read=True);token=texture_payload(typed)
            if token['kind']!='external-key-token-candidate':continue
            if typed.get('m_MipCount')!=1 or typed.get('m_ImageCount')!=1:raise ValueError('Only original single-mip 2D texture hydration supported')
            logical='Assets/Textures/astc/'+str(max(typed['m_Width'],typed['m_Height']))+'/'+token['key']+'.txt'
            item=pool.get(logical)
            if item is None:
                missing.append(dict(file=asset.name,pathId=identifier(obj.path_id),key=token['wireKey'],logicalPath=logical,reason='exact-cache-key-missing'));continue
            with Path(item['path']).open('rb') as stream:cached=stream.read(MAX_BYTES+1)
            if len(cached)!=item['bytes'] or digest(cached)!=item['sha256']:raise ValueError('Texture cache identity changed')
            header=astc_header(cached,typed['m_Width'],typed['m_Height'],token.get('blockSizeHint'))
            # Normalize once with the same pinned decoder as monkey's Cocos ASTC path.
            # Raw BGRA -> RGBA channel mapping only; no vertical flip, rounding tolerance or invented pixels.
            from importlib.metadata import version
            import texture2ddecoder
            if version('texture2ddecoder')!='1.0.6':raise ValueError('Expected texture2ddecoder1.0.6')
            decoded=texture2ddecoder.decode_astc(cached[16:],header['width'],header['height'],header['block'],header['block'])
            if len(decoded)!=header['width']*header['height']*4:raise ValueError('Decoded texture byte budget/size differs')
            rgba=bytearray(len(decoded));rgba[0::4]=decoded[2::4];rgba[1::4]=decoded[1::4];rgba[2::4]=decoded[0::4];rgba[3::4]=decoded[3::4]
            fmt=4
            typed['image data']=bytes(rgba);typed['m_CompleteImageSize']=len(rgba);typed['m_TextureFormat']=fmt
            obj.save_typetree(typed);modified.add((asset.name,identifier(obj.path_id)))
            resolved.append(dict(file=asset.name,pathId=identifier(obj.path_id),key=token['wireKey'],logicalPath=logical,
                                 cacheSha256=digest(cached),cacheBytes=len(cached),textureFormat=fmt,astc=header,rgbaRawSha256=digest(rgba),decoder='texture2ddecoder1.0.6',normalization='BGRA-to-RGBA-no-flip-v1'))
    report=dict(schemaVersion=1,provider=dict(name='UnityPy',version=PROVIDER_VERSION),sourceSha256=digest(raw),
                status='blocked' if missing else 'hydrated',resolved=resolved,missing=missing,originalSourceWritten=False,
                sourceCodeExecuted=False,pixelsDecoded=bool(resolved),canonicalPixelDecoder='texture2ddecoder1.0.6')
    if not missing:
        encoded=env.file.save(packer='lz4')
        if len(encoded)>MAX_BYTES:raise ValueError('Derived bundle byte budget')
        check=UnityPy.load(encoded);after={(a.name,identifier(o.path_id)):(o.type.name,digest(o.get_raw_data())) for a in check.assets for o in a.objects.values()}
        if before.keys()!=after.keys() or any(before[k]!=after[k] for k in before if k not in modified):
            raise ValueError('Non-texture source object changed during serialization')
        for asset in check.assets:
            for obj in asset.objects.values():
                if (asset.name,identifier(obj.path_id))in modified:
                    d=obj.read_typetree(check_read=True)
                    if texture_payload(d)['kind']!='inline-payload':raise ValueError('Texture hydration did not roundtrip')
        (output.parent/'hydrated.bundle').write_bytes(encoded)
        report.update(derivedBundleSha256=digest(encoded),derivedBundleBytes=len(encoded),nonTextureObjectsUnchanged=True,modifiedTextures=len(modified))
    if digest(source.read_bytes())!=job['sourceSha256']:raise ValueError('Original changed during hydration')
    output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')


def index_manifest(manifest_path,output):
    import UnityPy
    if UnityPy.__version__!=PROVIDER_VERSION:raise RuntimeError('Expected UnityPy '+PROVIDER_VERSION)
    job=json.loads(manifest_path.read_text());rows=[];total=0;object_count=0
    for i,item in enumerate(job['files']):
        source=Path(item['path'])
        with source.open('rb') as stream:raw=stream.read(MAX_BYTES+1)
        if len(raw)!=item['bytes'] or len(raw)>MAX_BYTES or digest(raw)!=item['sha256']:raise ValueError('Source identity changed before indexing')
        total+=len(raw)
        if total>1024*1024*1024:raise ValueError('Aggregate input budget')
        row=dict(id=item['id'],source=dict(sha256=digest(raw),bytes=len(raw)),status='indexed',files=[])
        try:
            env=UnityPy.load(raw)
            for asset in env.assets:
                objects=[dict(pathId=identifier(o.path_id),type=o.type.name,classId=int(o.type)) for o in asset.objects.values()]
                object_count+=len(objects)
                if object_count>1_000_000:raise ValueError('Aggregate object budget')
                row['files'].append(dict(name=asset.name,unityVersion=asset.unity_version,
                    key=row['source']['sha256']+':'+asset.name,sourceTypeTreeEnabled=asset._enable_type_tree,
                    externals=[dict(fileId=str(j+1),path=e.path,guid=e.guid.hex()) for j,e in enumerate(asset.externals)],objects=objects))
            if not row['files']:raise ValueError('No serialized files')
        except Exception as error:
            row.update(status='failed',error=dict(type=type(error).__name__,message=str(error).splitlines()[0][:200]))
        with source.open('rb') as stream:after=stream.read(MAX_BYTES+1)
        if digest(after)!=item['sha256']:raise ValueError('Source changed while indexing')
        rows.append(row)
        if i%16==0:(output.parent/'index-progress.json').write_text(json.dumps(dict(processed=i+1,total=len(job['files']))))
    report=dict(schemaVersion=1,provider=dict(name='UnityPy',version=PROVIDER_VERSION),containers=rows,
        sourceManifestSha256=job['sourceManifestSha256'],identifierEncoding='signed-int64-decimal-string-v1',
        summary=dict(containers=len(rows),indexed=sum(r['status']=='indexed' for r in rows),failed=sum(r['status']=='failed' for r in rows),objects=object_count,inputBytes=total),
        objectBodiesParsed=False,pixelsDecoded=False,sourceCodeExecuted=False,sourceUnchanged=True)
    encoded=json.dumps(report,ensure_ascii=False,separators=(',',':')).encode()
    if len(encoded)>MAX_BYTES:raise ValueError('Index output budget')
    output.write_bytes(encoded)


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
    if len(sys.argv)==4 and sys.argv[1]=='--hydrate':hydrate_manifest(Path(sys.argv[2]),Path(sys.argv[3]))
    elif len(sys.argv)==4 and sys.argv[1]=='--index':index_manifest(Path(sys.argv[2]),Path(sys.argv[3]))
    else:main()
