import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from monkey.prefab_spine_native_stage import (
    SpineNativeStageError,
    attach_unity_stage,
    creator_profile_handoff,
    emit_unity_stage,
    prepare_unity_stage,
)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True) + "\n", encoding="utf-8")
    return path


class SpineNativeStageTests(unittest.TestCase):
    def make_fixture(self, root):
        source_manifest = root / "frozen" / "source-manifest.json"
        manifest_bytes = b'{"assets":[]}\n'
        source_manifest.parent.mkdir(parents=True)
        source_manifest.write_bytes(manifest_bytes)
        manifest_sha = digest(manifest_bytes)
        source_ir = root / "frozen" / "ir.json"
        source_ir.write_bytes(b'{"components":[]}\n')
        ir_sha = digest(source_ir.read_bytes())

        closure = root / "closure"
        closure_file = closure / "Assets/Game/Content/Spine/Test/test.skel.bytes"
        closure_file.parent.mkdir(parents=True)
        closure_file.write_bytes(b"spine skeleton bytes")
        closure_meta = Path(str(closure_file) + ".meta")
        closure_meta.write_text("fileFormatVersion: 2\nguid: 12345678901234567890123456789012\n")

        closure_report = write_json(closure / "Analysis/Evidence/spine-closures.json", {"skeletons": []})
        closure_freeze = {
            "schemaVersion": 1, "sourceManifestSha256": manifest_sha,
            "candidatePath": str(closure.resolve()), "closureReportSha256": digest(closure_report.read_bytes()),
            "files": [
                {"path": "Analysis/Evidence/spine-closures.json", "sha256": digest(closure_report.read_bytes()),
                 "bytes": closure_report.stat().st_size},
                {"path": "Assets/Game/Content/Spine/Test/test.skel.bytes", "sha256": digest(closure_file.read_bytes()),
                 "bytes": closure_file.stat().st_size},
                {"path": "Assets/Game/Content/Spine/Test/test.skel.bytes.meta", "sha256": digest(closure_meta.read_bytes()),
                 "bytes": closure_meta.stat().st_size},
            ],
        }
        closure_freeze_path = write_json(root / "closure-freeze.json", closure_freeze)

        emission = {
            "schemaVersion": 1, "contract": "monkey-spine-emission/1",
            "pins": {"sourceManifestSha256": manifest_sha, "normalizedIrSha256": ir_sha,
                     "unityClosureReceiptSha256": digest(closure_freeze_path.read_bytes())},
            "copies": [
                {"target": "unity", "path": "Assets/Game/Content/Spine/Test/test.skel.bytes",
                 "sha256": digest(closure_file.read_bytes()), "bytes": closure_file.stat().st_size,
                 "sourceId": "asset:test"},
                {"target": "unity", "path": "Assets/Game/Content/Spine/Test/test.skel.bytes.meta",
                 "sha256": digest(closure_meta.read_bytes()), "bytes": closure_meta.stat().st_size,
                 "sourceId": "asset:test"},
            ],
        }
        emission_path = write_json(root / "emission.json", emission)

        runtime_root = root / "runtime-stage"
        runtime_root.mkdir()
        runtime_manifest = b'{"version":"3.8.99"}\n'
        (runtime_root / "manifest.json").write_bytes(runtime_manifest)
        files = {
            "spine-csharp.dll": b"csharp-runtime",
            "spine-unity.dll": b"unity-runtime",
            "Shaders/Spine-SkeletonGraphic.shader": b"graphic-shader",
            "LICENSE": b"license text",
        }
        checks = {}
        for relative, data in files.items():
            path = runtime_root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            value = digest(data)
            checks[relative] = {"expectedSha256": value, "observedSha256": value, "verified": True}
        runtime_evidence = {
            "unity": {"spinePlugin": {"manifestSha256": digest(runtime_manifest), "path": str(root / "runtime-source" / "manifest.json"),
                                       "compiledAgainst": "Unity6000.6.2f1",
                                       "fileChecks": checks}},
        }
        runtime_source_manifest = Path(runtime_evidence["unity"]["spinePlugin"]["path"])
        runtime_source_manifest.parent.mkdir(parents=True)
        runtime_source_manifest.write_bytes(runtime_manifest)
        runtime_evidence_path = write_json(root / "runtime-evidence.json", runtime_evidence)
        stage_evidence = {
            "verified": True, "sourceManifestSha256": digest(runtime_manifest),
            "copiedFiles": {name: {"sha256": checks[name]["expectedSha256"], "verified": True} for name in checks},
        }
        stage_evidence_path = write_json(root / "runtime-stage-evidence.json", stage_evidence)

        repo_root = Path(__file__).resolve().parents[1]
        shader_path = repo_root / "src/monkey/targets/materials/spine/UnitySpineSourceProfile.shader"
        native_plan = {
            "schemaVersion": 1, "contract": "monkey-spine-native-binding/1",
            "sourceManifestSha256": manifest_sha, "normalizedIrSha256": ir_sha,
            "sourceMaterialProfile": {
                "creatorMappingStatus": "exact_source_builtin_profile_mapping",
                "sourceReferenceSourceId": "bundle:source-material-ref",
                "resolvedSourceMaterialId": "bundle:source-material",
                "creatorTargetMaterialUuid": "default-spine-material",
            },
            "scaleEvidence": {"status": "verified_source_scale_and_target_unit_mapping"},
            "persistentVisiblePose": True,
            "visualPolicy": "native_renderer_enabled_timeScale_zero_source_timeScale_retained",
            "persistentVisiblePoseEvidence": {"status": "verified_pinned_spine_unity_3_8_runtime_source",
                "upstreamCommit": "8b4844bd4b193ba9e54487ed397a777993cbad56",
                "runtimeVersion": "3.8.99",
                "targetPolicy": "keep_native_renderer_enabled_and_set_timeScale_zero; preserve verified sourceTimeScale in identity/readback; no recovered game behavior"},
            "componentCount": 1, "sourceStaticDataBoundCount": 1, "sourceStaticDataUnboundCount": 0,
            "components": [{"sourceComponentId": "asset:test#0/components/0", "sourcePrefabId": "asset:test",
                            "behavior": "disabled", "sourceCallbacksExecuted": False,
                            "persistentVisiblePose": True, "sourceTimeScale": 1.0, "sourceTimeScaleVerified": True}],
            "dataAssetCount": 1,
            "dataAssets": [{"scale": 1.0,
                             "scaleEvidence": {"status": "verified_source_scale_and_target_unit_mapping"}}],
            "unityShader": {"sourcePath": str(shader_path),
                            "targetPath": "Assets/Game/Content/Shaders/UnitySpineSourceProfile.shader",
                            "sha256": digest(shader_path.read_bytes())},
        }
        native_path = write_json(root / "native-plan.json", native_plan)
        target_plan = {
            "schemaVersion": 1, "targetProfile": "unity-6000.6.2f1-ugui", "namespace": "Recovered.Tests",
            "sourceManifestSha256": manifest_sha, "sourceManifestPath": str(source_manifest),
            "sourceIrSha256": ir_sha,
            "sourcePrefabs": [{"sourceId": "asset:test"}],
            "components": [{"sourceId": "asset:test#0/components/0"}],
        }
        output = root / "target-plan"
        output.mkdir()
        return (target_plan, native_path, emission_path, source_ir, closure, closure_freeze_path, runtime_evidence_path,
                stage_evidence_path, runtime_root, output, native_plan)

    def test_attach_emit_includes_real_closure_runtime_helpers_and_plan(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp:
            args = self.make_fixture(Path(temp))
            target, native, emission, source_ir, closure, closure_freeze, runtime, stage_evidence, runtime_root, plan_root, native_doc = args
            stage = prepare_unity_stage(target, native, emission, source_ir, closure, closure_freeze, runtime, stage_evidence, runtime_root, plan_root)
            attached = attach_unity_stage(target, stage)
            self.assertIs(attached["spineNativeStage"], stage)
            self.assertEqual(stage["componentCount"], 1)
            self.assertEqual(stage["dataAssetCount"], 1)
            self.assertEqual(stage["resolvedSkeletonDataScale"], 1.0)
            self.assertTrue(stage["runtimeLicenseIncluded"])
            self.assertTrue(any(row["target"].endswith("spine-native-binding-plan.json") for row in stage["copies"]))
            self.assertTrue(any(row["target"].endswith("UnitySpineNativeStage.cs") for row in stage["copies"]))
            self.assertTrue(any(row["target"].endswith("UnitySpineImporterIntegration.cs") for row in stage["copies"]))
            self.assertTrue(any(row["target"].endswith("UnitySpineSourceIdentity.cs") for row in stage["copies"]))
            plugin_meta = next(row for row in stage["copies"] if row["target"].endswith("spine-unity.dll.meta"))
            self.assertNotIn(b"platformData: []", (plan_root / plugin_meta["source"]).read_bytes())
            unity = Path(temp) / "unity-candidate"
            report = emit_unity_stage(stage, plan_root, unity)
            self.assertEqual(report["componentCount"], 1)
            self.assertEqual(report["dataAssetCount"], 1)
            self.assertEqual((unity / "Assets/Plugins/Spine38/LICENSE").read_bytes(), b"license text")
            self.assertTrue((unity / "Assets/Game/Content/Spine/Test/test.skel.bytes").is_file())
            self.assertTrue((unity / "Assets/Game/Editor/Conversion/spine-native-binding-plan.json").is_file())

    def test_emit_rejects_changed_payload_and_conflicting_target(self):
        with tempfile.TemporaryDirectory(dir="/private/tmp") as temp:
            args = self.make_fixture(Path(temp))
            target, native, emission, source_ir, closure, closure_freeze, runtime, stage_evidence, runtime_root, plan_root, _ = args
            stage = prepare_unity_stage(target, native, emission, source_ir, closure, closure_freeze, runtime, stage_evidence, runtime_root, plan_root)
            first = stage["copies"][0]
            (plan_root / first["source"]).write_bytes(b"changed")
            with self.assertRaises(SpineNativeStageError):
                emit_unity_stage(stage, plan_root, Path(temp) / "unity")

    def test_creator_handoff_requires_exact_source_material_identity(self):
        profile = {"creatorMappingStatus": "exact_source_builtin_profile_mapping",
                   "sourceReferenceSourceId": "bundle:ref", "resolvedSourceMaterialId": "bundle:material",
                   "creatorTargetMaterialUuid": "default-spine-material"}
        contract = creator_profile_handoff({"sourceMaterialProfile": profile})
        self.assertEqual(contract["profile"], "cocos24-builtin-spine-material-v1")
        self.assertEqual(contract["targetMaterialUuid"], "default-spine-material")
        profile["creatorMappingStatus"] = "unresolved"
        with self.assertRaises(SpineNativeStageError):
            creator_profile_handoff({"sourceMaterialProfile": profile})

    def test_unity_domain_reload_read_paths_reload_frozen_plan_without_creating_native_objects(self):
        integration = (Path(__file__).resolve().parents[1] /
                       "src/monkey/targets/spine/UnitySpineImporterIntegration.cs").read_text()
        self.assertIn("static UnitySpineNativeStage.Plan LoadFrozenStaticSpinePlan()", integration)
        self.assertIn("UnitySpineNativeStage.Parse(File.ReadAllText(StaticSpinePlanPath))", integration)
        resolver = integration.split("static partial void ResolveStaticSpineReference", 1)[1].split("static partial void ReadSavedStaticSpine", 1)[0]
        readback = integration.split("static partial void ReadSavedStaticSpine", 1)[1].split("static string ResolveSpineNodeId", 1)[0]
        self.assertIn("LoadFrozenStaticSpinePlan()", resolver)
        self.assertIn("LoadFrozenStaticSpinePlan()", readback)
        self.assertNotIn("CreateDataAssets", resolver + readback)
        self.assertNotIn("CreateComponents", resolver + readback)
        self.assertIn("AssetDatabase.LoadAssetAtPath<SkeletonDataAsset>", resolver)
        self.assertIn("marker.sourceComponentId == id", resolver)

    def test_unity_spine_graphic_color_uses_source_node_rgba_and_readback_does_not_repair(self):
        integration = (Path(__file__).resolve().parents[1] /
                       "src/monkey/targets/spine/UnitySpineImporterIntegration.cs").read_text()
        prepare = integration.split("static partial void PrepareStaticSpine", 1)[1].split("LoadFrozenStaticSpinePlan()", 1)[0]
        readback = integration.split("static partial void ReadSavedStaticSpine", 1)[1].split("static string ResolveSpineNodeId", 1)[0]
        self.assertIn("SourceSpineNodeColor(sourceNode, row.sourceComponentId)", prepare)
        self.assertIn("graphic.color = expectedColor", prepare)
        self.assertIn("channels[0] / 255f", integration)
        self.assertIn("channels[3] / 255f", integration)
        self.assertIn("CanvasGroup", integration)
        self.assertIn("saved_spine_graphic_color_mismatch", readback)
        self.assertIn("SpineGraphicColorMatches(graphic, sourceNodeSpec", readback)
        self.assertNotIn("graphic.color =", readback)


if __name__ == "__main__":
    unittest.main()
