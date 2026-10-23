import contextlib,io,tempfile,unittest
from pathlib import Path
from monkey.cli import main
from monkey.providers.assetripper import Form


class UnityRouteTests(unittest.TestCase):
    def test_non_cocos_targets_and_unsupported_native_options_reject_before_output(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t).resolve();source=root/'game.ab';source.write_bytes(b'UnityFS\0dummy')
            for args in [ ['--target','both'], ['--target','unity6','--provider-python','missing','--asset-ripper','missing','--native'] ]:
                with contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit)as e:
                    main(['convert','--source',str(source),'--out',str(root/'out'),*args])
                self.assertEqual(e.exception.code,2);self.assertFalse((root/'out').exists())

    def test_public_settings_form_distinguishes_disabled_and_disk_save_flags(self):
        p=Form();p.feed('<input name="TargetVersion" value="6000.6.2f1"><input type="checkbox" name="Premium" checked disabled><input type="checkbox" name="SaveSettingsToDisk"><select name="ScriptContentLevel"><option value="Level2">x</option><option value="Level0" selected>y</option></select>')
        self.assertEqual(p.values,{'TargetVersion':'6000.6.2f1','ScriptContentLevel':'Level0'})


if __name__=='__main__':unittest.main()
