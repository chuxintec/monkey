import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from importlib.resources import files

from monkey.code_profiles import load_profile
from monkey.io import encoded
from monkey.sources.compiled import ParseError


ROOT = Path(__file__).resolve().parents[1]
PROFILE_NAME = 'foodstreet-demand-health-v1'
SOURCE = ROOT / 'outputs/foodstreet-unified-textures/UnityProject/SourceRecovery/Code/Source/snapshot/_subpackages_main_/subpackages/main/game.js'


class BuiltInCodeProfileTests(unittest.TestCase):
    def test_packaged_profile_is_canonical_and_contains_no_source_or_private_path(self):
        resource = files('monkey').joinpath('code_profiles', PROFILE_NAME + '.json')
        raw = resource.read_bytes()
        profile = json.loads(raw)
        self.assertEqual(encoded(profile), raw)
        self.assertEqual(profile['profileName'], PROFILE_NAME)
        self.assertEqual(profile['sourceSha256'], '21af08e48846f6ad1a2e0673b0c945358136723b1664f0cd1f6ec9b3df6c5cb5')
        self.assertEqual(profile['sourceBytes'], 7147892)
        text = raw.decode('utf-8')
        for forbidden in ('.private', '/Users/', 'Kp=function', 'game.js', 'SourceRecovery'):
            self.assertNotIn(forbidden, text)
        self.assertEqual(len(profile['records']), 3)
        self.assertEqual(sum(len(module['methods']) for module in profile['modules']), 12)

    def test_motion_profile_is_packaged_canonical_and_source_bound(self):
        name='foodstreet-motion-math-v1';raw=files('monkey').joinpath('code_profiles',name+'.json').read_bytes();profile=json.loads(raw)
        self.assertEqual(raw,encoded(profile));self.assertEqual(profile['profileName'],name)
        self.assertEqual(profile['sourceSha256'],'21af08e48846f6ad1a2e0673b0c945358136723b1664f0cd1f6ec9b3df6c5cb5')
        self.assertEqual(len(profile['modules']),1);self.assertEqual(len(profile['modules'][0]['methods']),4)
        for forbidden in ('.private','/Users/','game.js','SourceRecovery'): self.assertNotIn(forbidden,raw.decode())

    def test_unknown_profile_is_rejected_before_reading_source(self):
        with self.assertRaises(ParseError) as caught:
            load_profile('foodstreet-demand-health-v2', '/does/not/exist.js')
        self.assertEqual(caught.exception.code, 'CODE_PROFILE_UNKNOWN')

    def test_source_sha_or_size_mismatch_is_rejected(self):
        private = ROOT / '.private/v060-csharp-20261026/profile-tests'
        private.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=private) as directory:
            source = Path(directory) / 'wrong.js'
            source.write_bytes(b'not the pinned source')
            with self.assertRaises(ParseError) as caught:
                load_profile(PROFILE_NAME, source)
            self.assertEqual(caught.exception.code, 'CODE_PROFILE_SOURCE_IDENTITY')

    def test_current_frozen_source_matches_profile_identity(self):
        if not SOURCE.is_file():
            self.skipTest('Frozen FoodStreet source is not present in this checkout')
        profile = json.loads(load_profile(PROFILE_NAME, SOURCE))
        raw = SOURCE.read_bytes()
        self.assertEqual(len(raw), profile['sourceBytes'])
        self.assertEqual(hashlib.sha256(raw).hexdigest(), profile['sourceSha256'])


if __name__ == '__main__':
    unittest.main()
