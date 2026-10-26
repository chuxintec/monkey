import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from monkey.code_native_probe import EXPECTED_SOURCE_SHA256, prepare
from monkey.sources.compiled import ParseError


CANDIDATE = Path(__file__).resolve().parents[1] / ".private/v060-csharp-20261026/foodstreet-code-candidate-05"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class CodeNativeProbeTests(unittest.TestCase):
    def test_exact_candidate_prepares_narrow_unity_project_without_starting_editor(self):
        manifest = CANDIDATE / "manifest.json"
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp).resolve()
            result = prepare(CANDIDATE, sha(manifest), root / "probe")
            plan = json.loads(Path(result["plan"]).read_text(encoding="utf-8"))
            root = Path(result["project"])
            self.assertEqual(result["status"], "prepared_not_run")
            self.assertEqual(plan["candidate"]["sourceSha256"], EXPECTED_SOURCE_SHA256)
            self.assertFalse(plan["project"]["editorAutoStarted"])
            self.assertEqual(plan["healthContract"]["methods"],
                             ["ComboDoDelta", "DoDelta", "MaxHpDoDelta", "SetProperty", "clearCombo", "getPercent"])
            self.assertEqual(set(plan["healthContract"]["fields"]),
                             {"atk", "combo", "currHp", "def", "delta", "maxHp", "onComboChange", "onHpChange"})
            self.assertEqual((root / "ProjectSettings/ProjectVersion.txt").read_text().strip(),
                             "m_EditorVersion: 6000.6.2f1")
            fixture = json.loads((root / "Assets/CodeModuleProbe/Data/InitialState.fixture.json").read_text())
            self.assertEqual(set(fixture), {"atk", "combo", "currHp", "def", "delta", "maxHp"})
            self.assertEqual(fixture["currHp"], 80.0)
            self.assertFalse((root / "Assets/CodeModuleProbe/Scenes/CodeModuleProbe.unity").exists())
            self.assertTrue((root / "Assets/Editor/CodeModuleProbeEditor.cs").is_file())
            runtime = (root / "Assets/CodeModuleProbe/Runtime/CodeModuleProbeRuntime.cs").read_text(encoding="utf-8")
            self.assertIn("JsonUtility.FromJsonOverwrite", runtime)
            self.assertIn("public double atk = double.NaN", runtime)
            self.assertIn("omitted a required numeric state field", runtime)
            self.assertIn("state.onHpChange += ForwardHpChange", runtime)
            self.assertIn("state.onHpChange -= ForwardHpChange", runtime)
            self.assertTrue((root / "Assets/CodeModuleProbe/Runtime/CodeModuleProbeReadout.cs").is_file())
            manifest = json.loads((root / "Packages/manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["dependencies"], {"com.unity.modules.imgui": "1.0.0", "com.unity.modules.jsonserialize": "1.0.0"})
            editor = (root / "Assets/Editor/CodeModuleProbeEditor.cs").read_text(encoding="utf-8")
            self.assertIn("state.currHp != 79d", editor)
            self.assertIn("state.currHp != 89d", editor)
            self.assertIn("state.currHp != 109d", editor)
            self.assertIn("109d / 120d", editor)
            self.assertNotIn("__RECIPE_", editor)
            self.assertTrue((root / "Assets/CodeModuleProbe/Runtime/CodeModuleProbeReadout.cs").is_file())

    def test_wrong_manifest_hash_and_non_health_contract_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            tmp_root = Path(temp).resolve()
            root = tmp_root / "candidate"
            root.mkdir()
            for relative in ("manifest.json", "Analysis/Code/code-modules.json",
                             "Assets/Game/Domain/Recovered/HealthState.cs",
                             "Assets/Game/Domain/Recovered/HealthState.cs.meta",
                             "Assets/Game/Domain/Recovered/CodeCollections.cs",
                             "Assets/Game/Domain/Recovered/CodeCollections.cs.meta"):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(CANDIDATE / relative, target)
            manifest_path = root / "manifest.json"
            with self.assertRaisesRegex(ParseError, "CODE_NATIVE_MANIFEST_HASH"):
                prepare(root, "0" * 64, tmp_root / "wrong-hash")
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            health_path = root / "Assets/Game/Domain/Recovered/HealthState.cs"
            health_bytes = health_path.read_bytes().replace(b"public double atk;", b"public float atk;")
            health_path.write_bytes(health_bytes)
            for row in manifest["files"]:
                if row["path"] == "Assets/Game/Domain/Recovered/HealthState.cs":
                    row["bytes"] = len(health_bytes)
                    row["sha256"] = hashlib.sha256(health_bytes).hexdigest()
            manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ParseError, "CODE_NATIVE_HEALTH_FIELDS"):
                prepare(root, sha(manifest_path), tmp_root / "bad-contract")

    def test_other_health_module_name_is_rejected(self):
        with self.assertRaisesRegex(ParseError, "CODE_NATIVE_MODULE_UNSUPPORTED"):
            prepare(CANDIDATE, sha(CANDIDATE / "manifest.json"), Path(tempfile.gettempdir()) / "never-used-probe",
                    health_module="AnythingElse")

    def test_owned_file_with_wrong_owner_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            tmp_root = Path(temp).resolve()
            root = tmp_root / "candidate"
            shutil.copytree(CANDIDATE, root)
            manifest_path = root / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            target = next(row for row in manifest["files"]
                          if row["path"] == "Assets/Game/Domain/Recovered/HealthState.cs")
            target["owner"] = "ManualOverride"
            manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ParseError, "CODE_NATIVE_OWNER_MISMATCH"):
                prepare(root, sha(manifest_path), tmp_root / "wrong-owner")

    def test_recipe_module_prepares_exact_json_and_probe_assertions(self):
        manifest_path = CANDIDATE / "manifest.json"
        with tempfile.TemporaryDirectory() as temp:
            result = prepare(CANDIDATE, sha(manifest_path), Path(temp).resolve() / "recipe-probe",
                             recipe_module=True)
            project = Path(result["project"])
            plan = json.loads(Path(result["plan"]).read_text(encoding="utf-8"))
            source_json = CANDIDATE / "Assets/Game/Content/Config/Base/ElementMultiOrderPool.json"
            copied_json = project / "Assets/Game/Content/Config/Base/ElementMultiOrderPool.json"
            self.assertEqual(sha(copied_json), sha(source_json))
            self.assertTrue(plan["recipeModule"]["enabled"])
            self.assertEqual(plan["recipeModule"]["contract"]["probeDishId"], 2015015)
            self.assertEqual(plan["recipeModule"]["contract"]["expectedFlattenedLeafIds"],
                             [1010204, 1005303, 1007206, 1002401, 1007204,
                              1010201, 1004302, 1005203, 1010303])
            runtime = (project / "Assets/CodeModuleProbe/Runtime/CodeModuleProbeRuntime.cs").read_text()
            editor = (project / "Assets/Editor/CodeModuleProbeEditor.cs").read_text()
            self.assertIn("RecipeCatalog._dishMap = RecipeJsonConfiguration.Load(recipeTable)", runtime)
            self.assertIn("Flatten probe dish 2015015", runtime)
            self.assertIn("RecipeJsonSha256", editor)
            self.assertIn("recipeTableRows", editor)
            self.assertIn("recipeFlatten2015015", editor)
            self.assertIn("AssetIdentity(runtime.RecipeTable)", editor)
            source_meta = (CANDIDATE / "Assets/Game/Content/Config/Base/ElementMultiOrderPool.json.meta").read_text()
            source_guid = next(line.split(":", 1)[1].strip() for line in source_meta.splitlines() if line.startswith("guid:"))
            self.assertIn('RecipeJsonGuid = "' + source_guid + '"', editor)
            self.assertIn("localId", editor)
            self.assertIn("localId <= 0", editor)
            self.assertNotIn("__RECIPE_", editor)


if __name__ == "__main__":
    unittest.main()
