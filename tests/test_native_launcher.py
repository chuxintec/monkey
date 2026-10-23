import tempfile,unittest,json,io,contextlib
from pathlib import Path
from datetime import datetime,timezone,timedelta
from unittest.mock import patch
from fixtures import fixture
from monkey import native
from monkey.cli import main
from monkey.package import convert_package
from monkey.sources.containers import fingerprint
from monkey.sources.compiled import ParseError


class NativeLauncherTests(unittest.TestCase):
    def prepare(self,root):
        config=fixture(root/'source');convert_package(config.parent,'unity6',root/'candidate')
        candidate=root/'candidate/UnityProject';editor=root/'Unity';editor.write_text('#!/bin/sh\nexit 99\n');editor.chmod(0o700)
        instant=datetime.now(timezone.utc)
        return dict(candidate=candidate,editor=editor,expected_manifest=fingerprint(candidate/'manifest.json'),budget_seconds=600,
                    deadline_utc=native.stamp(instant+timedelta(minutes=10)),window_end_utc=native.stamp(instant+timedelta(minutes=12)))

    def test_plan_never_launches_and_source_drift_refuses_execution(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();options=self.prepare(root);out=root/'native'
            with patch.object(native.subprocess,'Popen',side_effect=AssertionError('No Editor in planning')):
                stdout=io.StringIO()
                args=['native-import','--candidate',str(options['candidate']),'--out',str(out),'--editor-path',str(options['editor']),
                      '--expected-manifest',options['expected_manifest'],'--deadline-utc',options['deadline_utc'],'--window-end-utc',options['window_end_utc']]
                with contextlib.redirect_stdout(stdout):code=main(args)
                self.assertEqual(code,0);result=json.loads(stdout.getvalue())
                self.assertEqual(result['status'],'planned');self.assertFalse((out/'UnityProject').exists())
                plan=json.loads((out/'native-plan.json').read_text());self.assertFalse(plan['quitFlag'])
                self.assertEqual(plan['method'],'MonkeyImporter.ImportBatchAsync')
                (options['candidate']/'Docs/START-HERE.md').write_text('manual edit')
                with self.assertRaises(ParseError) as error:native.native_import(output=out,execute=True,**options)
                self.assertEqual(error.exception.code,'NATIVE_SOURCE_DRIFT')
                self.assertFalse((out/'UnityProject').exists())

    def test_outer_deadline_terminates_only_owned_child_without_kill(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();options=self.prepare(root);out=root/'native';clock=[datetime.now(timezone.utc)]
            class Child:
                pid=31415
                returncode=None
                terminated=False
                def poll(self):return self.returncode
                def terminate(self):self.terminated=True;self.returncode=-15
                def wait(self,timeout):return self.returncode
                def kill(self):raise AssertionError('No hard kill')
            child=Child()
            def launch(args,**kwargs):
                self.assertNotIn('-quit',args);self.assertIn('-batchmode',args)
                self.assertEqual(args[0],str(options['editor']))
                self.assertEqual(kwargs['env']['MONKEY_NATIVE_BUDGET_SECONDS'],'600')
                clock[0]=native.utc(options['window_end_utc'])-timedelta(seconds=20)
                return child
            with patch.object(native,'now',side_effect=lambda:clock[0]),patch.object(native.subprocess,'Popen',side_effect=launch):
                result=native.native_import(output=out,execute=True,**options)
            self.assertTrue(child.terminated);self.assertTrue(result['processExited'])
            self.assertEqual(result['stopReason'],'outer_timebox');self.assertEqual(result['status'],'partial')
            self.assertEqual(fingerprint(options['candidate']/'manifest.json'),options['expected_manifest'])
            self.assertTrue((out/'UnityProject').exists())
            with self.assertRaises(ParseError) as existing:native.native_import(output=out,**options)
            self.assertEqual(existing.exception.code,'NATIVE_WORKSPACE_EXISTS')

    def test_host_journal_error_still_stops_its_child(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();options=self.prepare(root)
            class Child:
                pid=31416
                returncode=None
                terminated=False
                def poll(self):return self.returncode
                def terminate(self):self.terminated=True;self.returncode=-15
                def wait(self,timeout):return self.returncode
            child=Child();write=native.write_json
            def write_with_failure(path,value):
                if path.name=='execution-journal.json':raise OSError('simulated journal write failure')
                return write(path,value)
            with patch.object(native.subprocess,'Popen',return_value=child),patch.object(native,'write_json',side_effect=write_with_failure):
                result=native.native_import(output=root/'native',execute=True,**options)
            self.assertTrue(child.terminated);self.assertTrue(result['processExited'])
            self.assertEqual(result['reason'],'NATIVE_HOST_IO_FAILED')

    def test_invalid_time_contract_never_creates_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp).resolve();options=self.prepare(root)
            options['deadline_utc']=options['window_end_utc']
            with self.assertRaises(ValueError):native.native_import(output=root/'invalid',**options)
            self.assertFalse((root/'invalid').exists())


if __name__=='__main__':unittest.main()
