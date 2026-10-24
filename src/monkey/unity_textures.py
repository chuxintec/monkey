"""Exact cached texture-key hydration to an isolated Unity bundle derivative."""
import re,subprocess
from pathlib import Path
from .io import safe,read,load,sha,new_output,write_json
from .sources.compiled import fail
from .sources.containers import relative


def hydrate(source,cache_manifest,provider_python,output,budget_seconds=120):
    source=safe(source);manifest=safe(cache_manifest);raw=read(source,max_bytes=128*1024*1024);cache=load(read(manifest))
    if cache.get('schemaVersion')!=1 or not isinstance(cache.get('files'),list) or not 1<=len(cache['files'])<=2000:
        fail('UNITY_TEXTURE_CACHE_SCHEMA',str(manifest),'Expected explicit bounded cache pool manifest')
    if not 1<=budget_seconds<=1200:fail('UNITY_TEXTURE_BUDGET','$','Expected1..1200 seconds')
    requested=Path(provider_python).absolute();safe(requested.parent);python=safe(requested.resolve(strict=True));rows=[];seen=set()
    for x in cache['files']:
        logical=relative(x['logicalPath']);path=safe(manifest.parent/x['path'])
        if not isinstance(logical,str)or not logical.startswith('Assets/Textures/astc/') or any(p in ('','.','..')for p in logical.split('/'))or logical in seen:
            fail('UNITY_TEXTURE_CACHE_PATH',str(logical),'Expected unique explicit ASTC logical path')
        if type(x.get('bytes'))is not int or not 0<x['bytes']<=128*1024*1024 or not re.fullmatch('[0-9a-f]{64}',x.get('sha256','')):
            fail('UNITY_TEXTURE_CACHE_IDENTITY',logical,'Expected exact byte count and SHA256')
        seen.add(logical);rows.append(dict(path=str(path),logicalPath=logical,bytes=x['bytes'],sha256=x['sha256']))
    out=new_output(output,[source,manifest,python.parent,*[r['path']for r in rows]])
    write_json(out/'hydrate-job.json',dict(schemaVersion=1,source=str(source),sourceSha256=sha(raw),cache=rows))
    receipt=dict(schemaVersion=1,status='started',processExited=False,sourceSha256=sha(raw),cacheManifestSha256=sha(read(manifest)))
    with (out/'provider.log').open('wb')as log:
        (out/'provider.log').chmod(0o600)
        p=subprocess.Popen([str(requested),'-I','-B',str(Path(__file__).parent/'sources/unity_worker.py'),'--hydrate',str(out/'hydrate-job.json'),str(out/'hydration.json')],cwd=out,stdout=log,stderr=subprocess.STDOUT)
        receipt['pid']=p.pid;write_json(out/'execution.json',receipt)
        try:p.wait(timeout=budget_seconds)
        except subprocess.TimeoutExpired:
            p.terminate()
            try:p.wait(timeout=10)
            except subprocess.TimeoutExpired:pass
        receipt.update(processExited=p.poll()is not None,exitCode=p.poll())
    if p.poll()==0:
        body=load(read(out/'hydration.json'));receipt.update(status=body['status'],resolved=len(body['resolved']),missing=len(body['missing']))
        if body['status']=='hydrated':
            derived=read(out/'hydrated.bundle',max_bytes=128*1024*1024)
            if sha(derived)!=body.get('derivedBundleSha256'):fail('UNITY_DERIVED_CHANGED',str(out),'Derived bundle differs')
            receipt['derivedBundleSha256']=sha(derived);receipt['derivedBundle']=str(out/'hydrated.bundle')
    else:receipt['status']='failed'if receipt['processExited']else'pending_child_exit'
    write_json(out/'execution.json',receipt)
    return dict(receipt,report=str(out/'hydration.json'))
