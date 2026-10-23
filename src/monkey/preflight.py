"""Read-only native-startup checks. Never launches an Editor or changes host settings."""
from pathlib import Path
import shutil
from .io import safe,stage_manifest,new_output,finish,write_json,read,sha,diagnostic,inside
from .sources.containers import fingerprint


def classify_log(text):
    initialized='Initialize engine version:' in text
    readonly='attempt to write a readonly database' in text
    ipc=any(s in text for s in ('Connection invalid','Connection Invalid','_LSModifyNotification'))
    entitlement='Successfully resolved entitlement details' in text
    token='Access token is unavailable' in text
    findings=[]
    if not initialized and (readonly or ipc):
        findings.append(dict(code='HOST_CACHE_OR_IPC_ACCESS_SUSPECTED',confidence='inference',
            message='Startup stopped before engine initialization with host database/IPC warnings; review sandbox/cache access before requesting another bounded run'))
    if token and not entitlement:findings.append(dict(code='LICENSE_ENTITLEMENT_NOT_CONFIRMED',confidence='observed',message='Token update failed and no entitlement resolution is recorded'))
    if token and entitlement:findings.append(dict(code='LICENSE_TOKEN_UPDATE_WARNING',confidence='observed',message='Entitlement resolution is recorded despite failed token update; this alone does not prove a license failure'))
    if any(s in text for s in ('error CS','Scripts have compiler errors')):findings.append(dict(code='NATIVE_SCRIPT_COMPILE_FAILED',confidence='observed',message='Editor recorded script compiler errors'))
    return dict(engineInitialized=initialized,readonlyDatabaseWarning=readonly,ipcWarning=ipc,
                entitlementResolved=entitlement,tokenUpdateWarning=token,findings=findings)


def preflight(candidate,output,log=None):
    root=safe(candidate);manifest=stage_manifest(root);diagnostics=[]
    for row in manifest['files']:
        p=inside(root,row['path'])
        if not p.is_file() or fingerprint(p)!=row['sha256']:
            diagnostics.append(diagnostic('GENERATED_FILE_CHANGED',row['path'],'Candidate differs from frozen ownership manifest'))
    profile=manifest.get('targetProfile');unity=profile=='unity-6000.6.2f1-ugui'
    version=root/'ProjectSettings/ProjectVersion.txt'
    editor=Path('/Applications/Unity/Hub/Editor/6000.6.2f1/Unity.app/Contents/MacOS/Unity')
    if not unity:diagnostics.append(diagnostic('PREFLIGHT_TARGET_UNSUPPORTED',str(profile),'This preflight currently checks only the declared Unity profile'))
    if not version.exists() or '6000.6.2f1' not in version.read_text():diagnostics.append(diagnostic('EDITOR_VERSION_MISMATCH','ProjectVersion.txt','Expected Unity 6000.6.2f1'))
    if not editor.is_file():diagnostics.append(diagnostic('EDITOR_NOT_INSTALLED','Unity6000.6.2f1','Required local Editor absent; no installation attempted'))
    cli=shutil.which('unity')
    if not cli:diagnostics.append(diagnostic('UNITY_CLI_NOT_FOUND','PATH','Local Unity CLI absent; no installation attempted'))
    locks=[str(p.relative_to(root)) for p in (root/'Temp/UnityLockfile',root/'Library/EditorInstance.json') if p.exists()]
    if locks:diagnostics.append(diagnostic('EDITOR_OWNERSHIP_REQUIRES_CHECK',','.join(locks),'Existing Editor state; check exact project/process before a new invocation, never delete locks'))
    observation=None
    if log:
        raw=read(safe(log),max_bytes=32*1024*1024);observation=classify_log(raw.decode('utf-8',errors='replace'))
        observation['sha256']=sha(raw)
        diagnostics.extend(diagnostic(f['code'],'native-startup-log',f['message']) for f in observation['findings'])
    out=new_output(output,[root]);report=dict(schemaVersion=1,candidateManifestSha256=fingerprint(root/'manifest.json'),
        targetProfile=profile,editorExecutablePresent=editor.is_file(),unityCliPresent=bool(cli),existingEditorMarkers=locks,
        hostWriteAccess='not_probed',hostIpcAccess='not_probed',nativeExecution='not_run',startupObservation=observation,
        nextAction='Use an isolated acceptance copy and request a fresh bounded window; if host access is restricted, use the normal execution approval flow. No automatic retries or security-setting changes.',diagnostics=diagnostics)
    write_json(out/'preflight.json',report);return finish(out,report)
