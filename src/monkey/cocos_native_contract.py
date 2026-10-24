"""Read existing native Sprite identities/importers/references without an Editor."""
import re
from pathlib import Path
from .io import safe,inside,read,load,sha,new_output,write_json
from .sources.compiled import fail


def number(meta,key):
    matches=re.findall(rb'^\s*'+key.encode()+rb':\s*(-?[0-9.eE+]+)\s*$',meta,re.M)
    if len(matches)!=1:return None
    value=float(matches[0]);return int(value)if value.is_integer()else value


def vector(meta,key):
    match=re.search(rb'^\s*'+key.encode()+rb':\s*\{([^\r\n}]+)\}',meta,re.M)
    if not match:return None
    return {k.decode():float(v)for k,v in re.findall(rb'([xyzw]):\s*(-?[0-9.eE+]+)',match[1])}


def export(candidate,output):
    root=safe(candidate);manifest_raw=read(root/'manifest.json',max_bytes=128*1024**2);manifest=load(manifest_raw,max_nodes=16_000_000,max_depth=128)
    raw=read(root/'Analysis/editor-readback.json',max_bytes=128*1024**2);rb=load(raw,max_nodes=16_000_000,max_depth=128)
    source=load(read(root/'Analysis/source-map.json',max_bytes=128*1024**2),max_nodes=16_000_000,max_depth=128)
    locations=load(read(root/'Analysis/output-paths.json'));plan_path=inside(root,locations['plan']);plan=load(read(plan_path,max_bytes=128*1024**2),max_nodes=16_000_000,max_depth=128)
    if rb.get('status')not in ('partial','passed')or not rb.get('sceneReopened'):fail('NATIVE_CONTRACT_READBACK',str(root),'Existing saved/reopened native readback required')
    by_id={r['sourceId']:r for r in source['assets']};specs={r['id']:r for r in plan['textures']};old_hashes={f['path']:f['sha256']for f in rb['nativeFiles']};sprites=[];by_guid={}
    for native in rb['sprites']:
        asset=by_id[native['id']];path=asset['path'];meta_path=inside(root,path+'.meta');meta=read(meta_path)
        if old_hashes.get(path+'.meta')!=sha(meta):fail('NATIVE_CONTRACT_META_CHANGED',path,'Importer metadata differs from actual readback snapshot')
        guid=re.findall(rb'^guid: ([0-9a-f]{32})\r?$',meta,re.M)
        if guid!=[native['guid'].encode()]or native['fileId']==0:fail('NATIVE_CONTRACT_IDENTITY',path,'Actual Sprite GUID/localID differs')
        importer=dict(type=number(meta,'textureType'),spriteMode=number(meta,'spriteMode'),pixelsPerUnit=number(meta,'spritePixelsToUnits'),configuredPivot=vector(meta,'spritePivot'),configuredBorder=vector(meta,'spriteBorder'))
        if importer['type']!=8 or importer['spriteMode']!=1:fail('NATIVE_CONTRACT_IMPORTER',path,'Expected actual single-Sprite importer semantics')
        row=dict(sourceId=native['id'],path=path,guid=native['guid'],nativeType='Sprite',actualSpriteFileId=str(native['fileId']),
                 actualSize=native['size'],actualBorder=native['border'],importer=importer,importerMetaSha256=sha(meta),
                 sourceGeometry={k:specs[native['id']].get(k)for k in ('size','originalSize','offset','border')},
                 pivotEvidence='Importer metadata matched to previous native snapshot; Sprite.pivot was not separately captured')
        sprites.append(row);by_guid.setdefault(row['guid'],[]).append(row)
    prefabs=[]
    for prefab in rb['sourcePrefabs']:
        path=inside(root,prefab['path']);body=read(path,max_bytes=128*1024**2)
        if old_hashes.get(prefab['path'])!=sha(body):fail('NATIVE_CONTRACT_PREFAB_CHANGED',prefab['path'],'Prefab differs from saved native snapshot')
        refs=[]
        for fid,guid in re.findall(rb'^\s*m_Sprite:\s*\{fileID:\s*(-?[0-9]+),\s*guid:\s*([0-9a-f]{32}),\s*type:\s*[0-9]+\}',body,re.M):
            key=guid.decode();candidates=by_guid.get(key,[])
            if not candidates or any(c['actualSpriteFileId']!=fid.decode()for c in candidates):fail('NATIVE_CONTRACT_SPRITE_PPTR',prefab['path'],'Prefab Sprite pointer not in actual native Sprite identity set')
            refs.append(dict(guid=key,fileId=fid.decode(),sourceSpriteIds=[c['sourceId']for c in candidates]))
        prefabs.append(dict(sourceId=prefab['sourceId'],path=prefab['path'],guid=prefab['guid'],sha256=sha(body),savedReloaded=prefab['savedReloaded'],referencesVerified=prefab['referencesVerified'],spriteReferences=refs))
    out=new_output(output,[root]);report=dict(schemaVersion=1,sourceManifestSha256=sha(manifest_raw),nativeReadbackSha256=sha(raw),
        sprites=sprites,prefabs=prefabs,counts=dict(sprites=len(sprites),sourceFrames=len({r['sourceId'].removesuffix('@original')for r in sprites}),sourcePrefabs=len(prefabs),prefabSpritePointers=sum(len(p['spriteReferences'])for p in prefabs)),
        mergePolicy=dict(hashOnlyReuse=False,guidOnlyReuse=False,requires=['nativeType','importer semantics','geometry','actual Sprite local fileID','Prefab PPtr mapping'],preserveTargetManualBorderAndGeometry=True),
        sceneRecovery='Source SceneAsset identities require separate source scene handoff; auxiliary Candidate/ImportBootstrap not counted as source scenes',newEditorRun=False)
    write_json(out/'native-contract.json',report);return dict(status='contracted',counts=report['counts'],report=str(out/'native-contract.json'))
