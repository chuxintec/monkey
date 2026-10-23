import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from fixtures import fixture
from monkey.package import convert_package
from monkey.io import read,load,sha
from monkey.orchestration import run as native_run

class PostFormatTests(unittest.TestCase):
    def test_default_none_and_explicit_grea_preserve_baseline_and_format_both_targets(self):
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();source=fixture(root/'source').parent
            none=convert_package(source,'both',root/'none');grea=convert_package(source,'both',root/'grea',format_profile='grea')
            self.assertEqual(none['format']['status'],'not_requested');self.assertTrue(grea['completed']);self.assertEqual(grea['format']['status'],'applied')
            for name in ['UnityProject','CocosProject']:
                plain=load(read(root/'none'/name/'manifest.json'));formatted=load(read(root/'grea'/name/'manifest.json'));backup=load(read(root/'grea/Unformatted'/name/'manifest.json'))
                self.assertNotIn('layout',plain);self.assertEqual(formatted['layout'],'grea-typed-v1');self.assertEqual(backup['format']['profile'],'none')
                self.assertEqual(formatted['format']['inputManifestSha256'],sha(read(root/'grea/Unformatted'/name/'manifest.json')))

    def test_second_format_failure_retains_both_unformatted_projects_and_blocks_native(self):
        from monkey.formatting import apply
        with tempfile.TemporaryDirectory()as temp:
            root=Path(temp).resolve();source=fixture(root/'source').parent;calls=[]
            def fail_second(*args):
                calls.append(args)
                if len(calls)==2:raise ValueError('format dependency unresolved')
                return apply(*args)
            with patch('monkey.formatting.apply',side_effect=fail_second):result=convert_package(source,'both',root/'out',format_profile='grea')
            self.assertFalse(result['completed']);self.assertEqual(result['format']['status'],'failed');self.assertTrue(result['format']['unformattedExportPreserved'])
            for name in ['UnityProject','CocosProject']:
                manifest=load(read(root/'out'/name/'manifest.json'));self.assertEqual(manifest['format']['profile'],'none');self.assertNotIn('layout',manifest)
            self.assertEqual(native_run(result,{}),dict(status='not_run',reason='CONVERSION_INCOMPLETE'));self.assertFalse((root/'out/Unformatted').exists())

if __name__=='__main__':unittest.main()
