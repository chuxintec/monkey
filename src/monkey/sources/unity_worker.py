"""Isolated fixed UnityPy provider protocol; never resolves/executes source scripts."""
import base64
import hashlib
import json
import math
import re
import sys
import time
from collections import Counter
from pathlib import Path

# -I worker imports only its installed tool code, never source-side Python.
if not __package__:
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from monkey.unity_semantics import validate_component
from monkey.unity_parse_limits import parse_limits as resolve_limits,reader_fingerprint
from monkey.unity_payloads import StreamedArray,PayloadWriter,read_streamed,write_document

PROVIDER_VERSION = '1.25.3'
MAX_BYTES = 128 * 1024 * 1024
MAX_OBJECTS = 250_000
MAX_VALUES = 250_000
MAX_TYPED_VALUES = 8_000_000


def runtime_stats(start):
    try:
        import resource
        peak=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        if sys.platform!='darwin':peak*=1024
    except ImportError:peak=None
    return dict(elapsedSeconds=round(time.monotonic()-start,3),peakRssBytes=peak,peakScope='worker-lifetime')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def identifier(value):
    if type(value) is not int or not -(1 << 63) <= value < (1 << 63):
        raise ValueError('Expected signed 64-bit Unity identifier')
    return str(value)


def portable(value, refs, location='$', depth=0, counter=None, max_values=None):
    """PPtr fields are typed strings; arbitrary large integers are lossless tagged values."""
    if counter is None:
        counter = [0]
    counter[0] += 1
    if counter[0] > (MAX_VALUES if max_values is None else max_values) or depth > 96:
        raise ValueError('Typed value budget exceeded')
    if isinstance(value, StreamedArray):return value.descriptor
    if isinstance(value, dict):
        if set(value) == {'m_FileID', 'm_PathID'}:
            file_id, path_id = identifier(value['m_FileID']), identifier(value['m_PathID'])
            refs.append(dict(location=location, fileId=file_id, pathId=path_id))
            return {'$type': 'UnityPPtr', 'fileId': file_id, 'pathId': path_id}
        return {str(k): portable(v, refs, location + '/' + str(k), depth+1, counter, max_values) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [portable(v, refs, location + '/' + str(i), depth+1, counter, max_values) for i, v in enumerate(value)]
    if isinstance(value, bytes):
        return {'$type': 'bytes', 'base64': base64.b64encode(value).decode(), 'sha256': digest(value), 'bytes': len(value)}
    if isinstance(value, str):
        try:
            value.encode('utf-8')
            return value
        except UnicodeEncodeError:
            # UnityPy uses surrogateescape for arbitrary binary TextAsset bodies.
            return portable(value.encode('utf-8', errors='surrogateescape'), refs, location, depth+1, counter, max_values)
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
    # ETC1 requires at least one 8-byte block, even for a 1x1 texture.
    # Missing mip levels are not inferred, and streamed/token payloads were
    # handled above. This identifies invalid bytes without decoding pixels.
    width,height=typed.get('m_Width'),typed.get('m_Height')
    stream=typed.get('m_StreamData',{})
    if typed.get('m_TextureFormat')==34 and type(width)is int and type(height)is int and width>0 and height>0 and isinstance(stream,dict) and not stream.get('size') and not stream.get('path'):
        minimum=((width+3)//4)*((height+3)//4)*8
        if len(payload)<minimum:
            return dict(kind='invalid-inline-etc1',bytes=len(payload),sha256=digest(payload),minimumBaseLevelBytes=minimum,nativePixelsVerified=False,resourceResolution='source-payload-missing')
    return dict(kind='inline-payload',bytes=len(payload),sha256=digest(payload),nativePixelsVerified=False)


def schema_node(node,depth=0):
    if depth>64:raise ValueError('Embedded schema depth budget')
    result = dict(name=node.m_Name,type=node.m_Type,children=[schema_node(n,depth+1) for n in node.m_Children])
    for source, target in [('m_MetaFlag','metaFlag'),('m_Version','version'),('m_ByteSize','byteSize')]:
        if hasattr(node, source): result[target] = getattr(node, source)
    return result


def type_identity(asset, serialized_type):
    if serialized_type is None or serialized_type.class_id != 114:
        return None
    script_id, old_hash = serialized_type.script_id, serialized_type.old_type_hash
    if len(script_id) != 16 or len(old_hash) != 16 or not any(script_id) or not any(old_hash):
        return None
    return (asset.unity_version, str(asset.target_platform), script_id.hex(), old_hash.hex())


def full_schema(node):
    # Include layout/alignment/version flags, not just field names and types.
    return [{k:v for k,v in n.items() if k != 'm_Children'} for n in node.to_dict_list()]


def component_prefix(obj):
    """Keep independently decoded native PPtrs when a component body is unknown."""
    head=obj.parse_monobehaviour_head();refs=[];values={}
    for name in ('m_GameObject','m_Script'):
        ptr=getattr(head,name)
        values[name]=portable(dict(m_FileID=ptr.m_FileID,m_PathID=ptr.m_PathID),refs,'$/'+name)
    return dict(status='prefix-only',body='unparsed',fields=values),refs


def schema_pool(assets, job, all_schemas=False):
    import UnityPy
    wanted = {type_identity(a, o.serialized_type) for a in assets for o in a.objects.values()
              if o.type.name == 'MonoBehaviour' and not (o.serialized_type and o.serialized_type.node)} - {None}
    matches, total = {}, 0
    for row in job['files']:
        source = Path(row['path'])
        with source.open('rb') as stream: raw = stream.read(MAX_BYTES+1)
        total += len(raw)
        if len(raw) != row['bytes'] or len(raw) > MAX_BYTES or digest(raw) != row['sha256'] or total > 1024*1024*1024:
            raise ValueError('Frozen schema pool identity or budget changed')
        env = UnityPy.load(raw)
        for asset in env.assets:
            for typ in asset.types:
                key = type_identity(asset, typ)
                if key is None or (not all_schemas and key not in wanted) or typ.node is None: continue
                encoded = json.dumps(full_schema(typ.node), sort_keys=True, separators=(',',':')).encode()
                schema_hash = digest(encoded)
                if key in matches and matches[key]['sha256'] != schema_hash:
                    raise ValueError('Ambiguous exact-identity TypeTree in frozen pool')
                record = matches.setdefault(key, dict(node=typ.node, sha256=schema_hash, sources=[]))
                provenance = dict(bundleSha256=digest(raw), file=asset.name)
                if provenance not in record['sources']: record['sources'].append(provenance)
        with source.open('rb') as stream: after = stream.read(MAX_BYTES+1)
        if digest(after) != row['sha256']: raise ValueError('Schema source changed while reading')
    return matches


def inspect_bytes(raw, schema_job=None, schema_cache=None, parse_limits=None, payload_root=None):
    import UnityPy
    if UnityPy.__version__ != PROVIDER_VERSION:
        raise RuntimeError('Expected UnityPy ' + PROVIDER_VERSION)
    limits=resolve_limits(parse_limits or dict(objectValues=MAX_VALUES,containerValues=MAX_TYPED_VALUES))
    writer=PayloadWriter(payload_root,digest(raw)) if payload_root else None
    env = UnityPy.load(raw)  # bytes only: no source-side sibling or cache discovery
    assets = env.assets
    if not assets:
        raise ValueError('No serialized files found')
    if sum(len(f.objects) for f in assets) > MAX_OBJECTS:
        raise ValueError('Object budget exceeded')
    borrowed = schema_cache if schema_cache is not None else (schema_pool(assets, schema_job) if schema_job else {})
    files, objects, schemas, borrowed_schemas = [], [], {}, {};typed_values=0
    for index, asset in enumerate(assets):
        file_id = str(index)
        externals = [dict(fileId=str(i+1), path=e.path, guid=e.guid.hex()) for i, e in enumerate(asset.externals)]
        files.append(dict(id=file_id, name=asset.name, unityVersion=asset.unity_version,
                          targetPlatform=str(asset.target_platform), sourceTypeTreeEnabled=asset._enable_type_tree, externals=externals, objects=len(asset.objects)))
        if hasattr(asset, 'reader'):
            files[-1]['serializedFileSha256'] = digest(bytes(asset.reader.bytes))
        for obj in asset.objects.values():
            row = dict(file=file_id, pathId=identifier(obj.path_id), classId=int(obj.type), type=obj.type.name,
                       bytes=obj.byte_size, rawSha256=digest(obj.get_raw_data()), references=[],
                       typeTreeSource='embedded' if asset._enable_type_tree and obj.serialized_type and obj.serialized_type.node else 'provider-version-schema')
            if obj.type.name=='MonoBehaviour' and asset._enable_type_tree and obj.serialized_type and obj.serialized_type.node:
                shape=schema_node(obj.serialized_type.node)
                shape_id=digest(json.dumps(shape,sort_keys=True,separators=(',',':')).encode())
                schemas[shape_id]=shape;row['embeddedSchemaId']=shape_id
            exact = borrowed.get(type_identity(asset, obj.serialized_type)) if obj.type.name == 'MonoBehaviour' and not (obj.serialized_type and obj.serialized_type.node) else None
            if exact:
                shape = schema_node(exact['node'])
                shape_id = digest(json.dumps(shape,sort_keys=True,separators=(',',':')).encode())
                borrowed_schemas[shape_id] = shape
                row.update(typeTreeSource='exact-frozen-bundle', borrowedSchemaId=shape_id,
                    schemaProvenance=dict(identity=list(type_identity(asset,obj.serialized_type)), layoutSha256=exact['sha256'],
                        sourceManifestSha256=schema_job['sourceManifestSha256'], sources=exact['sources']))
            counter=[0];mark=len(writer.files) if writer else 0;blocks=[]
            row['parseMetrics']=dict(containerValuesBefore=typed_values)
            try:
                streamed=read_streamed(obj,writer,file_id)
                if streamed is not None:typed,blocks=streamed
                else:typed = obj.read_typetree(nodes=exact['node'], check_read=True) if exact else obj.read_typetree(check_read=True)
                if obj.type.name == 'MonoBehaviour':
                    node = exact['node'] if exact else (obj.serialized_type.node if obj.serialized_type else None)
                    if node is None:
                        raise ValueError('No proven MonoBehaviour schema for semantic validation')
                    head = obj.parse_monobehaviour_head()
                    header = {name: {'m_FileID': getattr(head, name).m_FileID,
                                     'm_PathID': getattr(head, name).m_PathID}
                              for name in ('m_Script', 'm_GameObject')}
                    validate_component(schema_node(node), typed, header)
                    row['semanticValidation'] = dict(status='passed', header='independent-native-prefix',
                                                      fields='schema-shape', fieldValues='not-cross-checked', writable=False)
                converted=portable(typed,row['references'],counter=counter,max_values=limits['objectValues'])
                typed_values+=counter[0]
                if typed_values>limits['containerValues']:
                    typed_values-=counter[0]
                    raise ValueError('Aggregate portable value budget exceeded; original object hash retained')
                row['data']=converted
                if blocks:row['payloads']=blocks
                if obj.type.name=='Texture2D' and isinstance(typed,dict):row['texturePayload']=texture_payload(typed)
                name = typed.get('m_Name') if isinstance(typed,dict) else None
                row['name'] = name if isinstance(name,str) and not any(0xd800 <= ord(c) <= 0xdfff for c in name) else None
                row['status'] = 'parsed'
            except Exception as error:
                # No relaxed read, zero-fill, guessed schema or source assembly execution.
                if writer:writer.rollback(mark)
                row['status'] = 'unparsed'
                row.pop('payloads',None)
                row.pop('data', None)
                row.pop('semanticValidation', None)
                row['references'] = []
                row['error'] = dict(type=type(error).__name__, message=str(error).splitlines()[0][:240])
                if obj.type.name=='MonoBehaviour':
                    try:
                        prefix,refs=component_prefix(obj)
                        row['nativePrefix']=prefix;row['references']=refs
                        row['referenceCoverage']='native-prefix-only;unknown-body-references-not-enumerated'
                        row['error']['code']='MONOBEHAVIOUR_BODY_UNPARSED'
                        if not exact and not (obj.serialized_type and obj.serialized_type.node):
                            row['error']['code']='MISSING_EXACT_MONOBEHAVIOUR_SCHEMA'
                            row['requiredSchemaIdentity']=type_identity(asset,obj.serialized_type)
                    except Exception as prefix_error:
                        row['nativePrefix']=dict(status='unreadable',error=str(prefix_error)[:240])
            row['parseMetrics'].update(inlineValues=counter[0],streamedValues=sum(b['length']for b in blocks)if row['status']=='parsed'else 0)
            objects.append(row)
    return dict(schemaVersion=1, sourceFamily='unity', provider=dict(name='UnityPy',version=PROVIDER_VERSION),
                parseLimits=limits,parseUsage=dict(inlineValues=typed_values,payloadBytes=writer.total if writer else 0,payloadChunks=len(writer.files)if writer else 0),
                payloadFiles=writer.files if writer else [],identifierEncoding='signed-int64-decimal-string-v1', files=files, objects=objects, embeddedSchemas=schemas, borrowedSchemas=borrowed_schemas,
                summary=dict(serializedFiles=len(files), objects=len(objects),
                             parsed=sum(o['status']=='parsed' for o in objects),
                             unparsed=sum(o['status']=='unparsed' for o in objects), borrowedSchemaParsed=sum(o['status']=='parsed' and o['typeTreeSource']=='exact-frozen-bundle' for o in objects), externalTextureTokens=sum(o.get('texturePayload',{}).get('kind')=='external-key-token-candidate' for o in objects), invalidInlineTextures=sum(o.get('texturePayload',{}).get('kind')=='invalid-inline-etc1' for o in objects), types=dict(Counter(o['type'] for o in objects))),
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



def quarantine_invalid_textures(job_path,output):
    import UnityPy
    if UnityPy.__version__!=PROVIDER_VERSION:raise RuntimeError('Expected UnityPy '+PROVIDER_VERSION)
    job=json.loads(job_path.read_text());source=Path(job['source']);raw=source.read_bytes()
    if len(raw)>MAX_BYTES or digest(raw)!=job['sourceSha256']:raise ValueError('Source changed')
    env=UnityPy.load(raw);before={};removed=[]
    for asset in env.assets:
        for obj in list(asset.objects.values()):
            key=(asset.name,identifier(obj.path_id))
            if key in before:raise ValueError('Ambiguous serialized file identity')
            before[key]=(obj.type.name,digest(obj.get_raw_data()))
            if obj.type.name!='Texture2D':continue
            typed=obj.read_typetree(check_read=True);payload=texture_payload(typed)
            if payload['kind']!='invalid-inline-etc1':continue
            removed.append(dict(file=asset.name,pathId=identifier(obj.path_id),name=typed.get('m_Name'),rawSha256=before[key][1],payload=payload))
            del asset.objects[obj.path_id]
    if not removed:raise ValueError('No exact invalid ETC1 payload to quarantine')
    encoded=env.file.save(packer='none' if raw.startswith(b'UnityWebData1.0\0') else 'lz4')
    if len(encoded)>MAX_BYTES:raise ValueError('Derived container byte budget')
    check=UnityPy.load(encoded);after={(a.name,identifier(o.path_id)):(o.type.name,digest(o.get_raw_data()))for a in check.assets for o in a.objects.values()}
    excluded={(r['file'],r['pathId'])for r in removed}
    expected={k:v for k,v in before.items()if k not in excluded}
    if after!=expected:raise ValueError('A retained object changed during quarantine')
    if digest(source.read_bytes())!=job['sourceSha256']:raise ValueError('Original changed')
    (output.parent/'derived.container').write_bytes(encoded)
    report=dict(schemaVersion=1,status='quarantined',sourceSha256=digest(raw),removed=removed,
        derivedSha256=digest(encoded),derivedBytes=len(encoded),retainedObjects=len(after),retainedObjectsUnchanged=True,
        sourceCodeExecuted=False,pixelsFabricated=False,referencesToRemovedObjects='unresolved-not-replaced',originalRetainedByConversion=True)
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


def inspect_batch(job_path, output):
    """Read each frozen schema bundle once, then inspect every explicit container."""
    import UnityPy
    if UnityPy.__version__ != PROVIDER_VERSION: raise RuntimeError('Expected UnityPy '+PROVIDER_VERSION)
    job=json.loads(job_path.read_text());pool=job.get('schemaPool');rows=job['files'];limits=resolve_limits(job.get('parseLimits'))
    if job.get('readerContractSha256')!=reader_fingerprint():raise ValueError('Reader contract changed before execution')
    if not 1 <= len(rows) <= 2001: raise ValueError('Batch container budget')
    cache=schema_pool([],pool,all_schemas=True) if pool else {}
    reports=[];total=0
    for index,row in enumerate(rows):
        source=Path(row['path']);raw=source.read_bytes();total+=len(raw)
        if len(raw)>MAX_BYTES or total>1024**3 or len(raw)!=row['bytes'] or digest(raw)!=row['sha256']:
            raise ValueError('Batch input identity or budget changed')
        dest=Path(row['inspection']);dest.mkdir(exist_ok=False)
        receipt=dict(schemaVersion=1,status='started',source=dict(path=str(source),bytes=len(raw),sha256=digest(raw)),
                     processExited=True,sourceCodeExecuted=False)
        started=time.monotonic()
        try:
            typed=inspect_bytes(raw,pool,schema_cache=cache,parse_limits=limits,payload_root=dest)
            typed['source']={k:receipt['source'][k] for k in ('bytes','sha256')}
            typed_hash=write_document(dest/'typed-objects.json',typed)
            receipt.update(status='partial' if typed['summary']['unparsed'] else 'inspected',
                           summary=typed['summary'],provider=typed['provider'],typedObjectsSha256=typed_hash,parseLimits=limits,parseUsage=typed['parseUsage'],readerContractSha256=reader_fingerprint())
        except Exception as error:
            receipt.update(status='failed',error=dict(type=type(error).__name__,message=str(error)[:300]))
        receipt['performance']=runtime_stats(started)
        receipt['sourceUnchanged']=digest(source.read_bytes())==row['sha256']
        (dest/'inspection.json').write_text(json.dumps(receipt,indent=2)+'\n')
        reports.append(dict(path=str(source),inspection=str(dest),receipt=receipt))
        (output.parent/'batch-progress.json').write_text(json.dumps(dict(processed=index+1,total=len(rows)))+'\n')
    output.write_text(json.dumps(dict(schemaVersion=1,files=reports,schemaBundlesRead=len(pool['files'])if pool else 0,
                                     containersInspected=len(rows),sourceCodeExecuted=False),separators=(',',':'))+'\n')


def main():
    schema_job = None;limits=None
    if sys.argv[1] == '--inspect-with-schemas':
        job = json.loads(Path(sys.argv[2]).read_text())
        source, output = Path(job['source']), Path(sys.argv[3])
        schema_job = job['schemaPool'];limits=resolve_limits(job.get('parseLimits'))
        if job.get('readerContractSha256')!=reader_fingerprint():raise ValueError('Reader contract changed before execution')
    else: source, output = map(Path, sys.argv[1:])
    with source.open('rb') as stream:
        raw = stream.read(MAX_BYTES+1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Input byte budget exceeded')
    started=time.monotonic()
    data = inspect_bytes(raw, schema_job,parse_limits=limits,payload_root=output.parent)
    data['source'] = dict(bytes=len(raw), sha256=digest(raw))
    write_document(output,data)
    (output.parent/'reader-runtime.json').write_text(json.dumps(runtime_stats(started)))


if __name__ == '__main__':
    if len(sys.argv)==4 and sys.argv[1]=='--inspect-batch':inspect_batch(Path(sys.argv[2]),Path(sys.argv[3]))
    elif len(sys.argv)==4 and sys.argv[1]=='--hydrate':hydrate_manifest(Path(sys.argv[2]),Path(sys.argv[3]))
    elif len(sys.argv)==4 and sys.argv[1]=='--quarantine-invalid-textures':quarantine_invalid_textures(Path(sys.argv[2]),Path(sys.argv[3]))
    elif len(sys.argv)==4 and sys.argv[1]=='--index':index_manifest(Path(sys.argv[2]),Path(sys.argv[3]))
    else:main()
