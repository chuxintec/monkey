"""Create-only output and bounded immutable source reads."""
import hashlib
import json
from pathlib import Path
from .sources.compiled import budget, fail

MAX_BYTES = 32 * 1024 * 1024


def sha(data):
    return hashlib.sha256(data).hexdigest()


def safe(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in (path, *path.parents)):
        fail('SYMLINK_PATH', str(path), 'Symbolic links are not accepted')
    return path.resolve()


def inside(root, relative):
    if not isinstance(relative, str) or Path(relative).is_absolute():
        fail('UNSAFE_PATH', str(relative), 'Expected relative path')
    path = safe(root / relative)
    if not path.is_relative_to(root):
        fail('UNSAFE_PATH', relative, 'Path escapes root')
    return path


def read(path):
    path = safe(path)
    with path.open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        fail('BYTE_BUDGET', str(path), 'Input exceeds 32 MiB')
    return raw


def load(raw):
    def pairs(items):
        out = {}
        for key, value in items:
            if key in out:
                fail('DUPLICATE_KEY', '$', key)
            out[key] = value
        return out
    result = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=pairs,
                        parse_constant=lambda x: fail('NONFINITE_NUMBER', '$', x))
    budget(result, max_nodes=3_000_000)
    return result


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + '\n').encode('utf-8')


def write_json(path, value):
    path.write_bytes(encoded(value))


def stage_document(path):
    """Verify the generated document against its owning stage manifest."""
    path=safe(path);raw=read(path)
    manifest=load(read(path.parent/'manifest.json'))
    expected=next((f['sha256'] for f in manifest.get('files',[]) if f['path']==path.name),None)
    if expected!=sha(raw):fail('STAGE_DOCUMENT_CHANGED',str(path),'Document differs from its owning stage manifest')
    return load(raw)


def new_output(path, inputs=()):
    path = safe(path)
    for item in inputs:
        item = safe(item)
        if path == item or path.is_relative_to(item) or item.is_relative_to(path):
            fail('OUTPUT_OVERLAP', str(path), 'Output overlaps an input')
    if path.exists():
        fail('OUTPUT_EXISTS', str(path), 'Use a fresh candidate directory')
    path.mkdir(parents=True, exist_ok=False)
    return path


def diagnostic(code, location, message, source_id=None):
    severe = any(token in code for token in ('MISSING','INVALID','CYCLE','BOUNDS','EXCEEDED','CHANGED'))
    return dict(code=code, location=location, message=message, sourceId=source_id,
                severity='error' if severe else 'warning', affectedScope=source_id or 'selection')


def finish(out, report):
    report['files'] = [dict(path=p.relative_to(out).as_posix(), sha256=sha(p.read_bytes()),
                            bytes=p.stat().st_size, owner='generated')
                       for p in sorted(out.rglob('*')) if p.is_file() and p != out / 'manifest.json']
    if sum(f['bytes'] for f in report['files']) > 256*1024*1024:
        fail('OUTPUT_BUDGET',str(out),'Candidate exceeds 256 MiB output budget')
    report['status'] = 'partial' if report.get('diagnostics') else 'candidate'
    write_json(out / 'manifest.json', report)
    return report
