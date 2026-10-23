"""Bounded typed Unity source inspection through an explicitly selected provider."""
import subprocess
from pathlib import Path
from ..io import safe, read, sha, load, new_output, write_json
from .compiled import fail

PROFILE = 'unity-serialized-unitypy-1.25.3'
MAX_BYTES = 128 * 1024 * 1024


def inspect(source, provider_python, output, budget_seconds=120):
    if not 1 <= budget_seconds <= 1200:
        fail('UNITY_PROVIDER_BUDGET', '$', 'Expected 1..1200 seconds')
    source = safe(source)
    if not source.is_file():
        fail('UNITY_INPUT_FILE', str(source), 'Expected one explicit serialized file or AssetBundle')
    requested_python = Path(provider_python).absolute()
    safe(requested_python.parent)
    python = safe(requested_python.resolve(strict=True))
    if not python.is_file():
        fail('UNITY_PROVIDER_MISSING', str(python), 'Explicit provider Python is unavailable')
    raw = read(source, max_bytes=MAX_BYTES)
    out = new_output(output, [source, python.parent])
    receipt = dict(schemaVersion=1, sourceProfile=PROFILE, status='started', source=dict(path=str(source), bytes=len(raw), sha256=sha(raw)),
                   providerPythonSha256=sha(read(python,max_bytes=MAX_BYTES)), budgetSeconds=budget_seconds,
                   sourceCodeExecuted=False, editor='not_run', processExited=False)
    write_json(out/'inspection.json',receipt)
    with (out/'provider.log').open('wb') as log:
        process = subprocess.Popen([str(requested_python), '-I', '-B', str(Path(__file__).with_name('unity_worker.py')),str(source),str(out/'typed-objects.json')],
                                   cwd=out, stdout=log, stderr=subprocess.STDOUT)
        receipt['pid'] = process.pid
        try:
            receipt['exitCode'] = process.wait(timeout=budget_seconds)
        except subprocess.TimeoutExpired:
            receipt['status'] = 'timeout';process.terminate()
            try:
                receipt['exitCode'] = process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                receipt['status'] = 'pending_child_exit'
        receipt['processExited'] = process.poll() is not None
    if receipt.get('exitCode') == 0:
        typed_raw = read(out/'typed-objects.json', max_bytes=MAX_BYTES)
        typed = load(typed_raw,max_nodes=8_000_000)
        if typed.get('schemaVersion') != 1 or typed.get('source') != {k:receipt['source'][k] for k in ('bytes','sha256')}:
            fail('UNITY_PROVIDER_RECEIPT',str(out),'Provider source identity differs')
        receipt.update(status='partial' if typed['summary']['unparsed'] else 'inspected',
                       summary=typed['summary'], typedObjectsSha256=sha(typed_raw), provider=typed['provider'])
    elif receipt['status'] == 'started':
        receipt['status'] = 'provider_failed'
    receipt['sourceUnchanged'] = sha(read(source,max_bytes=MAX_BYTES)) == receipt['source']['sha256']
    if not receipt['sourceUnchanged']:
        receipt['status'] = 'source_changed'
    write_json(out/'inspection.json',receipt)
    return receipt
