import tomllib
import unittest
from pathlib import Path

from monkey import __version__


class ReleaseVersionTests(unittest.TestCase):
    def test_package_metadata_and_runtime_version_match_v060_release(self):
        metadata_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
        metadata = tomllib.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["project"]["version"], "0.6.0")
        self.assertEqual(__version__, "0.6.0")


if __name__ == "__main__":
    unittest.main()
