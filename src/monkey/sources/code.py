"""Static source recovery via vendored, pinned AST parser. Never execute input JS."""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from ..io import sha


def modules(raw, source_path=None):
    node = shutil.which('node')
    if not node:
        return [], dict(code='DEPENDENCY_MISSING',message='Node is required for static module AST recovery')
    adapter = 'system-register-v1' if b'System.register' in raw else 'define-browserify-v1' if b'define(' in raw else 'browserify-table-v1'
    env = {k:v for k,v in os.environ.items() if k not in ('NODE_OPTIONS','NODE_PATH')}
    parser = Path(__file__).with_name('index-modules.cjs')
    attempts=[adapter]
    if adapter=='define-browserify-v1': attempts+=['define-factory-candidates-v1','define-multi-factory-candidates-v1']
    if b'cc._RF.push' in raw: attempts+=['rf-regions-v1']
    for attempt in attempts:
        try:
            # A regular stdin file avoids host Node pipe-read failures on large inputs.
            with open(source_path,'rb') if source_path else tempfile.TemporaryFile() as stream:
                if not source_path: stream.write(raw);stream.seek(0)
                run = subprocess.run([node,'--max-old-space-size=512',str(parser),attempt],stdin=stream,
                                     capture_output=True,timeout=30,env=env)
            if not run.stdout:
                oom=b'heap out of memory' in run.stderr
                return [],dict(code='AST_MEMORY_BUDGET' if oom else 'AST_PROCESS_FAILED',
                               message='Static parser exceeded the 512 MiB heap budget' if oom else 'Static parser exited without JSON',returncode=run.returncode)
            report = json.loads(run.stdout)
        except (OSError,ValueError,subprocess.TimeoutExpired) as error:
            return [],dict(code='AST_UNAVAILABLE',message=str(error))
        if 'error' in report:
            if report['error']['code'] in ('UNSUPPORTED_WRAPPER','EMPTY_INPUT','AMBIGUOUS_WRAPPER'): continue
            return [],report['error']
        if run.returncode:
            return [],dict(code='AST_FAILED',message='Static parser exited without a usable result')
        for module in report['modules']:
            start,end=module['source_bytes']['start'],module['source_bytes']['end']
            if not 0<=start<end<=len(raw) or sha(raw[start:end])!=module['sha256']:
                return [],dict(code='SOURCE_IDENTITY_MISMATCH',message='AST module byte-range/hash mismatch')
        partial = report.get('issues') or any(m.get('unresolved') for m in report['modules'])
        return report['modules'], (dict(code='MODULE_RECOVERY_PARTIAL',
            message='Static candidates require enclosing context/module identity recovery',
            issues=report.get('issues',[]),sourceFormat=report.get('source_format')) if partial else None)
    return [],dict(code='UNSUPPORTED_WRAPPER',message='No supported literal module table; complete source retained')


def drafts(module, module_id):
    """Contracts retain source identity/dependencies; no fabricated business implementation."""
    token='M'+sha(module_id.encode())[:20]
    deps=[str(d.get('module')) for d in module.get('dependencies',[])]
    facts=module.get('syntax',{})
    exports=facts.get('exports',[]);events=facts.get('events',[]);keys=facts.get('dynamicKeys',[])
    array=lambda values: 'new string[] { '+', '.join(json.dumps(v) for v in values)+' }'
    # These drafts remain outside all engine compilation roots until an Agent implements them.
    cs=('// SourceRecovery draft: not compiled, behavior unresolved.\n'
        'namespace Recovered.Gameplay {\n'
        f'  public sealed class {token} {{\n'
        f'    public const string SourceModule = {json.dumps(module_id)};\n'
        f'    public static readonly string[] SourceDependencies = {array(deps)};\n'
        f'    public static readonly string[] SourceExports = {array(exports)};\n'
        f'    public static readonly string[] SourceEvents = {array(events)};\n'
        f'    public static readonly string[] SourceResourceKeys = {array(keys)};\n'
        '    public object Invoke(string sourceExport, params object[] arguments) {\n'
        '      throw new System.NotImplementedException("Restore source module behavior before enabling");\n'
        '    }\n  }\n}\n')
    ts=('// SourceRecovery draft: not compiled, behavior unresolved.\n'
        f'export const sourceModule = {json.dumps(module_id)};\n'
        f'export const sourceDependencies: readonly string[] = {json.dumps(deps)};\n'
        f'export const sourceExports: readonly string[] = {json.dumps(exports)};\n'
        f'export const sourceEvents: readonly string[] = {json.dumps(events)};\n'
        f'export const sourceResourceKeys: readonly string[] = {json.dumps(keys)};\n'
        'export function invoke(sourceExport: string, ...args: unknown[]): never {\n'
        '  throw new Error("Restore source module behavior before enabling");\n}\n')
    return token,cs,ts
