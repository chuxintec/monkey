import json
import tempfile
import unittest
from importlib.resources import files
from pathlib import Path

from monkey.code_profiles import load_profile
from monkey.io import encoded
from monkey.sources.compiled import ParseError


# Compatibility identifiers: public callers may already select these exact profiles.
COMPATIBILITY_PROFILE_IDS = (
    "foodstreet-demand-health-v1",
    "foodstreet-motion-math-v1",
)


class BuiltInCodeProfileTests(unittest.TestCase):
    def test_allowlisted_profiles_are_packaged_canonical_and_source_bound(self):
        for profile_name in COMPATIBILITY_PROFILE_IDS:
            with self.subTest(profile=profile_name):
                raw = files("monkey").joinpath("code_profiles", profile_name + ".json").read_bytes()
                profile = json.loads(raw)
                self.assertEqual(encoded(profile), raw)
                self.assertEqual(profile["profileName"], profile_name)
                self.assertRegex(profile["sourceSha256"], r"^[0-9a-f]{64}$")
                self.assertGreater(profile["sourceBytes"], 0)
                text = raw.decode("utf-8")
                for forbidden in (".private", "/Users/", "/private/", "game.js", "SourceRecovery"):
                    self.assertNotIn(forbidden, text)
        demand = json.loads(files("monkey").joinpath("code_profiles", COMPATIBILITY_PROFILE_IDS[0] + ".json").read_bytes())
        motion = json.loads(files("monkey").joinpath("code_profiles", COMPATIBILITY_PROFILE_IDS[1] + ".json").read_bytes())
        self.assertEqual(len(demand["records"]), 3)
        self.assertEqual(sum(len(module["methods"]) for module in demand["modules"]), 12)
        self.assertEqual(len(motion["modules"]), 1)
        self.assertEqual(len(motion["modules"][0]["methods"]), 4)

    def test_unknown_profile_is_rejected_before_reading_source(self):
        with self.assertRaises(ParseError) as caught:
            load_profile("demo-unknown-v2", "missing-source.js")
        self.assertEqual(caught.exception.code, "CODE_PROFILE_UNKNOWN")

    def test_source_sha_or_size_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=Path.cwd()) as directory:
            wrong = Path(directory) / "wrong.js"
            wrong.write_bytes(b"not the pinned source")
            with self.assertRaises(ParseError) as caught:
                load_profile(COMPATIBILITY_PROFILE_IDS[0], wrong)
            self.assertEqual(caught.exception.code, "CODE_PROFILE_SOURCE_IDENTITY")


if __name__ == "__main__":
    unittest.main()
