import json
import os
from pathlib import Path
import tempfile
import unittest

from monkey.code_postprocess import prepare, run
from monkey.io import sha, encoded
from monkey.sources.compiled import ParseError


SESSION = '123e4567-e89b-42d3-a456-426614174000'


class CodePostprocessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir='/private/tmp')
        self.root = Path(self.temp.name)
        self.candidate = self.root / 'candidate'
        self.candidate.mkdir()
        code = b'public class Example { public int Value = 1; }\n'
        (self.candidate / 'Assets').mkdir()
        (self.candidate / 'Assets' / 'Example.cs').write_bytes(code)
        self.manifest = {
            'schemaVersion': 1, 'candidateId': 'synthetic-candidate',
            'files': [{'path': 'Assets/Example.cs', 'owner': 'generated',
                       'sha256': sha(code), 'bytes': len(code)}],
        }
        (self.candidate / 'manifest.json').write_bytes(encoded(self.manifest))
        self.manifest_hash = sha((self.candidate / 'manifest.json').read_bytes())
        self.codex = self.root / 'codex'
        self.output = self.root / 'revision'
        self.fake_cli('import sys\nsys.stdin.read()\n')

    def tearDown(self):
        before = self.root / 'revision' / 'before'
        if before.exists():
            for path in before.rglob('*'):
                if path.is_dir(): path.chmod(0o700)
                elif path.is_file(): path.chmod(0o600)
            before.chmod(0o700)
        self.temp.cleanup()

    def fake_cli(self, body):
        script = '''#!/usr/bin/env python3
import sys
if '--version' in sys.argv:
    print('codex-cli synthetic-1')
    raise SystemExit(0)
''' + body
        self.codex.write_text(script, encoding='utf-8')
        self.codex.chmod(0o755)

    def make_prepared(self, **kwargs):
        return prepare(self.candidate, ['Assets/Example.cs'], self.manifest_hash,
                       self.output, 'Fix only mechanically clear C# issues.',
                       codex=self.codex, **kwargs)

    def test_prepare_copies_only_selected_generated_cs_and_keeps_source_immutable(self):
        evidence = self.candidate / 'map.json'
        evidence.write_text('{"note":"context"}', encoding='utf-8')
        prepared = self.make_prepared(evidence_files=['map.json'])
        copied = prepared.workspace / 'Assets/Example.cs'
        self.assertEqual(copied.read_bytes(), (self.candidate / 'Assets/Example.cs').read_bytes())
        self.assertNotEqual(copied.stat().st_ino, (self.candidate / 'Assets/Example.cs').stat().st_ino)
        self.assertFalse((prepared.workspace / 'map.json').exists())
        self.assertEqual(sha((self.candidate / 'manifest.json').read_bytes()), self.manifest_hash)
        self.assertFalse(os.access(prepared.output / 'before/Assets/Example.cs', os.W_OK))
        self.assertTrue((prepared.workspace / '.git').is_dir())

    def test_rejects_manifest_drift_paths_and_non_generated_files(self):
        (self.candidate / 'manifest.json').write_bytes(encoded({**self.manifest, 'candidateId': 'changed'}))
        with self.assertRaises(ParseError):
            self.make_prepared()
        self.output = self.root / 'revision2'
        (self.candidate / 'manifest.json').write_bytes(encoded(self.manifest))
        self.manifest_hash = sha((self.candidate / 'manifest.json').read_bytes())
        with self.assertRaises(ParseError):
            prepare(self.candidate, ['../outside.cs'], self.manifest_hash,
                    self.root / 'revision2', 'task', codex=self.codex)
        with self.assertRaises(ParseError):
            prepare(self.candidate, ['manifest.json'], self.manifest_hash,
                    self.root / 'revision2', 'task', codex=self.codex)

    def test_cli_complete_records_real_diff_and_limits_scope(self):
        self.fake_cli(f'''import json, pathlib, sys
prompt = sys.stdin.read()
path = pathlib.Path('Assets/Example.cs')
path.write_text(path.read_text().replace('Value = 1', 'Value = 2'))
print(json.dumps({{"type":"thread.started","thread_id":"{SESSION}"}}), flush=True)
print(json.dumps({{"type":"turn.completed","model":"gpt-6-luna","reasoning_effort":"high","usage":{{"input_tokens":12,"output_tokens":3}}}}), flush=True)
response = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])
response.write_text(json.dumps({{"status":"complete","changedPaths":["Assets/Example.cs"],"unresolved":[],"summary":"synthetic"}}))
''')
        prepared = self.make_prepared()
        revision = run(prepared)
        self.assertEqual(revision['status'], 'complete')
        self.assertEqual(revision['sessionId'], SESSION)
        self.assertEqual(revision['actualChanges'][0]['path'], 'Assets/Example.cs')
        self.assertIn('Value = 1', (self.output / 'changes.patch').read_text())
        self.assertEqual(revision['diffSha256'], sha((self.output / 'changes.patch').read_bytes()))
        self.assertTrue(revision['gitBoundary']['valid'])
        self.assertEqual(revision['model'], 'gpt-6-luna')
        self.assertEqual(revision['reasoningEffort'], 'high')
        self.assertEqual(revision['usage'], {'input_tokens': 12, 'output_tokens': 3})
        self.assertEqual((self.candidate / 'Assets/Example.cs').read_text(), 'public class Example { public int Value = 1; }\n')
        invocation = json.loads((self.output / 'invocation.json').read_text())
        args = invocation['command']
        self.assertIn('--sandbox', args)
        self.assertIn('workspace-write', args)
        self.assertNotIn('--dangerously-bypass-approvals-and-sandbox', args)

    def test_extra_file_turns_success_into_partial_and_is_recorded(self):
        self.fake_cli(f'''import json, pathlib, sys
pathlib.Path('extra.txt').write_text('unexpected')
response = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])
response.write_text(json.dumps({{"status":"complete","changedPaths":[],"unresolved":[],"summary":"synthetic"}}))
''')
        revision = run(self.make_prepared())
        self.assertEqual(revision['status'], 'partial')
        self.assertEqual(revision['unexpectedPaths'], ['extra.txt'])

    def test_source_hash_is_rechecked_after_cli(self):
        source = self.candidate / 'Assets/Example.cs'
        self.fake_cli(f'''import pathlib, sys
sys.stdin.read()
pathlib.Path({str(source)!r}).write_text('tampered')
''')
        revision = run(self.make_prepared())
        self.assertEqual(revision['status'], 'failed')
        self.assertEqual(revision['stopReason'], 'source-identity-changed')
        self.assertTrue(revision['sourceVerificationErrors'])

    def test_hardlink_is_not_accepted_as_a_revision(self):
        source = self.candidate / 'Assets/Example.cs'
        self.fake_cli(f'''import os, pathlib, sys
sys.stdin.read()
path = pathlib.Path('Assets/Example.cs')
path.unlink()
os.link({str(source)!r}, path)
''')
        revision = run(self.make_prepared())
        self.assertNotEqual(revision['status'], 'complete')
        self.assertTrue(any('hard link' in item for item in revision['workspaceIntegrityErrors']))

    def test_custom_codex_symlink_is_rejected(self):
        link = self.root / 'codex-link'
        link.symlink_to(self.codex)
        with self.assertRaises(ParseError):
            prepare(self.candidate, ['Assets/Example.cs'], self.manifest_hash,
                    self.root / 'linked-revision', 'task', codex=link)

    def test_resume_requires_exact_recorded_session(self):
        self.fake_cli(f'''import json, pathlib, sys, time
if 'resume' in sys.argv:
    response = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])
    response.write_text(json.dumps({{"status":"partial","changedPaths":[],"unresolved":["synthetic"],"summary":"partial"}}))
else:
    print(json.dumps({{"type":"thread.started","thread_id":"{SESSION}"}}), flush=True)
    time.sleep(3)
''')
        prepared = self.make_prepared(timeout_seconds=4, no_progress_seconds=1)
        revision = run(prepared)
        self.assertEqual(revision['stopReason'], 'no-progress')
        self.assertEqual(json.loads((self.output / 'request.json').read_text())['state'], 'checkpoint')
        with self.assertRaises(ParseError):
            run(prepared, session_id='223e4567-e89b-42d3-a456-426614174000')
        resumed = run(prepared, session_id=SESSION)
        self.assertEqual(resumed['status'], 'partial')
        self.assertEqual(json.loads((self.output / 'invocation.json').read_text())['command'][2], 'resume')

    def test_exhausted_total_budget_keeps_checkpoint_but_cannot_resume(self):
        self.fake_cli(f'''import json,sys,time
print(json.dumps({{"type":"thread.started","thread_id":"{SESSION}"}}),flush=True)
time.sleep(3)
''')
        prepared=self.make_prepared(timeout_seconds=1,no_progress_seconds=1)
        revision=run(prepared)
        self.assertEqual(revision['stopReason'],'timeout')
        with self.assertRaises(ParseError) as error:
            run(prepared,session_id=SESSION)
        self.assertEqual(error.exception.code,'POSTPROCESS_TOTAL_BUDGET')
        self.assertEqual(json.loads((self.output/'request.json').read_text())['state'],'checkpoint')


if __name__ == '__main__':
    unittest.main()
