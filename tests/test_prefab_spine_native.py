import copy
import hashlib
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from monkey.prefab_spine_native import SpineNativePlanError, build_unity_native_binding_plan


def fixture():
    source_sha = "a" * 64
    ir_sha = "b" * 64
    runtime_manifest = "c" * 64
    skeleton_sha = "d" * 64
    atlas_sha = "e" * 64
    texture_sha = "f" * 64
    shader_sha = hashlib.sha256(Path("src/monkey/targets/materials/spine/UnitySpineSourceProfile.shader").read_bytes()).hexdigest()
    ids = ["gameAsset:prefab#1/components/0", "gameAsset:prefab#2/components/0"]
    data_id = "spineAsset:data"
    source_material_ref = "gameAsset:material"
    material_target = "internal:material"
    components = []
    for index, source_id in enumerate(ids):
        components.append({
            "sourceComponentId": source_id,
            "sourcePrefabId": "gameAsset:prefab",
            "sourceNodeId": str(index + 1),
            "sourceNodePath": f"Root/Spine{index}",
            "sourceDataAssetId": data_id if index == 0 else None,
            "sourceSerializedFields": {"_materials": [{"__uuid__": "material"}]},
            "unity": {"fields": {"animation": {"status": "explicit", "sourceValue": "idle"},
                                   "skin": {"status": "explicit", "sourceValue": "default"}}},
        })
    material_rows = [{"sourceComponentId": sid,
                      "sourceMaterialReferenceSourceId": source_material_ref,
                      "sourceMaterialSourceId": material_target} for sid in ids]
    page = {"pageIndex": 0, "pageName": "source-page.png", "sourceTextureSourceId": "gameAsset:texture",
            "materialIdentitySeeds": {"normal": "seed/normal"}}
    unity_material_rows = [
        {"sourceComponentId": ids[0], "status": "profile-materials-defined", "pmaVertexColors": False,
         "sourceAtlasPages": [page], "variants": [{"blendMode": "normal", "sourceSlotCount": 3}]},
        {"sourceComponentId": ids[1], "status": "no-serialized-skeleton-data-no-render-material-closure"},
    ]
    emission = {
        "contract": "monkey-spine-emission/1", "sourceVersion": "2.4.15", "sourceComponentCount": 2,
        "pins": {"sourceManifestSha256": source_sha, "normalizedIrSha256": ir_sha},
        "components": components,
        "assets": [{"sourceId": data_id, "sourceSkeletonSha256": skeleton_sha,
                    "sourceSpineVersion": "3.8.99", "unity": {
                        "candidateInputPath": "Assets/Game/Spine/rig.skel.bytes",
                        "atlasPath": "Assets/Game/Spine/rig.atlas.txt"}}],
        "copies": [
            {"sourceId": data_id, "path": "Assets/Game/Spine/rig.skel.bytes", "sha256": skeleton_sha, "target": "unity"},
            {"sourceId": data_id, "path": "Assets/Game/Spine/rig.atlas.txt", "sha256": atlas_sha, "target": "unity"},
            {"sourceId": data_id, "path": "Assets/Game/Spine/renamed-page.png", "sha256": texture_sha, "target": "unity"},
        ],
    }
    material_contract = {
        "schema": "monkey-spine-material-contract/1", "profile": "cocos24-builtin-spine-material-v1",
        "creatorBindingStatus": "source-semantics-exact-builtin-spine",
        "pins": {"sourceManifestSha256": source_sha, "normalizedIrSha256": ir_sha,
                 "materialReferenceSourceId": source_material_ref, "materialSourceId": material_target},
        "spec": {"creator38": {"targetMaterialUuid": "default-spine-material", "perComponent": material_rows},
                 "unity": {"shaderSourceSha256": shader_sha, "perComponent": unity_material_rows}},
    }
    closure = {"skeletons": [{"sourceId": data_id, "status": "closure_recovered",
        "skeletonPath": "Assets/Game/Spine/rig.skel.bytes", "atlasPath": "Assets/Game/Spine/rig.atlas.txt",
        "sourceSkeletonSha256": skeleton_sha, "sourceAtlasSha256": atlas_sha,
        "dependencies": [{"page": "source-page.png", "sourceId": "gameAsset:texture", "sourceSha256": texture_sha,
                          "targetPage": "renamed-page.png"}]}]}
    file_names = ["spine-csharp.dll", "spine-unity.dll", "Shaders/Spine-SkeletonGraphic.shader", "LICENSE"]
    checks = {name: {"verified": True, "expectedSha256": hashlib} for name, hashlib in
              zip(file_names, ("2" * 64, "3" * 64, "4" * 64, "5" * 64))}
    runtime_evidence = {"unity": {"spinePlugin": {"compiledAgainst": "Unity6000.6.2f1",
        "sourceVersion": "3.8.99", "upstreamCommit": "commit", "manifestSha256": runtime_manifest,
        "fileChecks": checks}}}
    stage = {"verified": True, "destination": "/private/UnityRuntimeStage/Assets/Plugins/Spine38",
             "sourceManifestSha256": runtime_manifest,
             "copiedFiles": {name: {"verified": True, "sha256": data["expectedSha256"]}
                             for name, data in checks.items()}}
    target_unit_evidence = {"status": "verified_unit_mapping", "targetUnitsPerSourcePixel": 1.0,
                           "worldSpaceCanvasScale": 1.0, "pixelsPerUnitConversion": None,
                           "evidenceSource": "neutral fixture"}
    return emission, material_contract, closure, runtime_evidence, stage, target_unit_evidence


class PrefabSpineNativePlanTests(unittest.TestCase):
    def test_join_preserves_bound_and_unbound_components_and_material_source_identity(self):
        plan = build_unity_native_binding_plan(*fixture())
        self.assertEqual(plan["componentCount"], 2)
        self.assertEqual(plan["sourceStaticDataBoundCount"], 1)
        self.assertEqual(plan["sourceStaticDataUnboundCount"], 1)
        self.assertEqual(plan["dataAssetCount"], 1)
        self.assertEqual(plan["components"][1]["staticDataState"], "source_uuid_absent_component_preserved_unbound")
        self.assertEqual(plan["components"][0]["creatorMaterialBinding"]["targetMaterialUuid"], "default-spine-material")
        self.assertEqual(plan["dataAssets"][0]["pages"][0]["nativeAtlasPage"], "renamed-page.png")
        self.assertEqual(plan["dataAssets"][0]["scale"], 1.0)
        self.assertEqual(plan["scaleEvidence"]["status"], "verified_source_scale_and_target_unit_mapping")
        self.assertEqual(plan["dataAssets"][0]["factoryInput"]["scale"], 1.0)

    def test_changed_nonempty_source_material_ref_is_rejected(self):
        values = list(fixture())
        values[0] = copy.deepcopy(values[0])
        values[0]["components"][0]["sourceSerializedFields"]["_materials"][0]["__uuid__"] = "wrong"
        with self.assertRaisesRegex(SpineNativePlanError, "serialized material references"):
            build_unity_native_binding_plan(*values)

    def test_runtime_license_or_dll_hash_mismatch_is_rejected(self):
        values = list(fixture())
        values[4] = copy.deepcopy(values[4])
        values[4]["copiedFiles"]["LICENSE"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(SpineNativePlanError, "runtime copy differs"):
            build_unity_native_binding_plan(*values)

    def test_missing_target_unit_evidence_does_not_use_unity_scale_fallback(self):
        values = list(fixture())
        values[5] = None
        plan = build_unity_native_binding_plan(*values)
        self.assertIsNone(plan["dataAssets"][0]["factoryInput"]["scale"])
        self.assertEqual(plan["scaleEvidence"]["status"], "target_unit_evidence_missing")
        self.assertIn("UNITY_SPINE_SCALE_EVIDENCE_MISSING", {row["code"] for row in plan["diagnostics"]})

    def test_persistent_visible_pose_is_pinned_to_actual_spine_38_renderer_lifecycle(self):
        workspace = Path(__file__).resolve().parents[3]
        runtime = workspace / "projects/18-灵境守卫/LingJing/Assets/ThirdParty/Spine38/Unity/Components"
        graphic = (runtime / "SkeletonGraphic.cs").read_bytes()
        animation = (runtime / "SkeletonAnimation.cs").read_bytes()
        renderer = (runtime / "SkeletonRenderer.cs").read_bytes()
        self.assertEqual(hashlib.sha256(graphic).hexdigest(),
                         "ce83a9686b6d79f94ad7bc4ff06c6d732dbca194ae921abfd0a69bc28df7afb4")
        self.assertEqual(hashlib.sha256(animation).hexdigest(),
                         "91674944a815287a9f7ef4f242d9f748db71d5585f2d36bce7559208948b1339")
        self.assertEqual(hashlib.sha256(renderer).hexdigest(),
                         "a56bc75ccd170f3cbb6523e318e02a99fb0af41713836cbd12df3b10e0971525")
        self.assertIn(b"canvasRenderer.Clear();", graphic)
        self.assertIn(b"deltaTime *= timeScale;", graphic)
        self.assertIn(b"UpdateMesh(keepRendererCount : true)", graphic)
        self.assertIn(b"deltaTime *= timeScale;", animation)



if __name__ == "__main__":
    unittest.main()
