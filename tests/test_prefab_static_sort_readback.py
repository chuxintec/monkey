import copy
import math
import unittest
from pathlib import Path

from src.monkey.prefab_static_sort_readback import _check_text_sources, _empty_renderer_matches, verify, verify_creator


def slot_enumeration(source_id, rows):
    return {"sourceComponentId": source_id, "sourceTextSha256": "a" * 64,
            "slotCount": len(rows), "verified": True, "evidenceSha256": "b" * 64, "rows": rows}


def slot_row(slot, disposition):
    placeholder = disposition == "empty-placeholder"
    return {"slot": slot, "characterReferences": 0 if placeholder else 1,
            "visibleCharacterReferences": 0 if placeholder else 1,
            "textInfoNondegenerateTriangleCount": 0 if placeholder else 2,
            "canvasNondegenerateTriangleCount": 0 if placeholder else 2,
            "disposition": disposition, "evidenceSha256": f"{slot + 1:064x}"}


def fixture():
    queue = {
        "rootScope": "root", "sourcePrefabId": "prefab-a", "prefabPath": "Assets/Game/Prefabs/A.prefab",
        "renderers": [{"node": "icon", "sourceComponentId": "sprite-a", "sourceQueueIndex": 0}],
        "drawEvents": [{"kind": "renderer", "node": "icon", "sourceComponentId": "sprite-a"}],
        "masks": [], "sourceFields": [{"sourceId": "sort-a", "nativeId": "sort-native-a", "node": "icon",
                                          "sortOrder": 7, "enabled": True}],
        "sourceSortRoots": [{"sourceId": "scope-a", "nativeId": "scope-native-a", "node": "icon", "enabled": False}],
    }
    plan = {"staticSortQueue": [queue], "sourcePrefabs": [{"sourceId": "prefab-a", "path": queue["prefabPath"]}]}
    graphic = {
        "sourceComponentId": "sprite-a", "sourceNode": "icon", "sourceQueueIndex": 0,
        "staticSnapshotVerified": True, "verified": True, "sourceGraphicEnabled": True, "vertexCount": 4,
        "meshAssetGuid": "a" * 32, "sourceMeshSha256": "1" * 64, "proxyMeshSha256": "2" * 64,
        "capturedSourceMeshSha256": "1" * 64, "meshContentSha256": "2" * 64,
        "sourceRendererAlpha": 0.8, "proxyRendererAlpha": 0.8,
        "sourceInheritedAlpha": 0.5, "proxyInheritedAlpha": 0.5,
        "sourceEffectiveAlpha": 0.4, "proxyEffectiveAlpha": 0.4, "opacityVerified": True,
        "renderedMeshSha256": None, "sourceCulled": True, "proxyVisible": False,
        "runtimeMeshVerified": False, "transformedGeometryVerified": False,
        "sourceVertexCount": 4, "persistedProxyVertexCount": 4,
        "maxWorldVertexError": 0.0, "maxWorldNormalError": 0.0, "maxWorldTangentError": 0.0,
        "transformedTopologyMatches": True, "transformedUvMatches": True,
        "transformedColorsMatch": True, "transformedNormalsMatch": True, "transformedTangentsMatch": True,
        "sourceUvChannelVertexCounts": [4, 0, 0, 0, 4, 0, 0, 4],
        "proxyUvChannelVertexCounts": [4, 0, 0, 0, 4, 0, 0, 4],
        "renderedUvChannelVertexCounts": [],
        "sourceUvChannelDimensions": [2, 0, 0, 0, 2, 0, 0, 3],
        "proxyUvChannelDimensions": [2, 0, 0, 0, 2, 0, 0, 3],
        "renderedUvChannelDimensions": [],
    }
    order = {"sourceId": "sort-a", "node": "icon", "nativeId": "sort-native-a", "sourceSortOrder": 7,
             "enabledInSource": True, "actualSourceId": "sort-a", "actualNativeId": "sort-native-a",
             "actualSortOrder": 7, "actualEnabledInSource": True, "identityPresent": True,
             "identityComponentEnabled": False, "verified": True}
    root = {"sourceId": "scope-a", "node": "icon", "nativeId": "scope-native-a", "enabledInSource": False,
            "actualSourceId": "scope-a", "actualNativeId": "scope-native-a", "actualEnabledInSource": False,
            "identityPresent": True, "identityComponentEnabled": False, "verified": True}
    persistent = {"rootScope": "root", "readbackMode": "persistent", "provisional": False, "verified": True,
                  "persistentSnapshotVerified": True, "runtimeGeometryDeferred": True,
                  "initializedPresentationVerified": False, "sourceTreePreserved": True,
                  "structuralDiagnostics": [], "textSourcesVerified": True, "textSources": [],
                  "sourceMaskReferencesVerified": True,
                  "sourceGraphicsCovered": True, "layoutIgnored": True, "emptyRenderers": [],
                  "sourceFieldsPreserved": True, "sourceSortRootsPreserved": True,
                  "drawSequenceVerified": True, "graphics": [copy.deepcopy(graphic)], "masks": [],
                  "maskSourceIds": [], "sourceFields": [copy.deepcopy(order)], "sourceSortRoots": [copy.deepcopy(root)]}
    loaded = copy.deepcopy(persistent)
    loaded.update({"readbackMode": "initialized", "runtimeGeometryDeferred": False,
                   "initializedPresentationVerified": True})
    loaded["graphics"][0].update({"renderedMeshSha256": "2" * 64, "renderedUvChannelVertexCounts": [4, 0, 0, 0, 4, 0, 0, 4],
                                  "renderedUvChannelDimensions": [2, 0, 0, 0, 2, 0, 0, 3],
                                  "runtimeMeshVerified": True, "transformedGeometryVerified": True,
                                  "proxyVisible": True})
    result = {"sourcePrefabs": [{"sourceId": "prefab-a", "staticSortFields": {
        "sourcePrefabId": "prefab-a", "prefabPath": plan["sourcePrefabs"][0]["path"],
        "verified": True, "persistentAsset": [persistent], "loadedInstance": [loaded]}}]}
    return plan, result


class StaticSortReadbackTests(unittest.TestCase):
    def test_accepts_persistent_fields_and_all_eight_loaded_uv_channels(self):
        plan, result = fixture()
        self.assertEqual([], verify(plan, result))

    def test_rejects_source_and_native_sort_order_disagreement(self):
        plan, result = fixture()
        result["sourcePrefabs"][0]["staticSortFields"]["loadedInstance"][0]["sourceFields"][0]["actualSortOrder"] = 8
        self.assertTrue(any("actual sort order differs" in row["message"] for row in verify(plan, result)))

    def test_rejects_proxy_that_loses_inherited_canvas_group_alpha(self):
        plan, result = fixture()
        result["sourcePrefabs"][0]["staticSortFields"]["loadedInstance"][0]["graphics"][0]["proxyInheritedAlpha"] = 1.0
        self.assertTrue(any("CanvasGroup/CanvasRenderer alpha evidence differs" in row["message"] for row in verify(plan, result)))

    def test_rejects_identity_carrier_enabled_on_source_tree(self):
        plan, result = fixture()
        result["sourcePrefabs"][0]["staticSortFields"]["persistentAsset"][0]["sourceSortRoots"][0]["identityComponentEnabled"] = True
        self.assertTrue(any("persistent typed identity readback differs" in row["message"] for row in verify(plan, result)))

    def test_rejects_world_vertex_error_even_when_rendered_mesh_matches_proxy(self):
        plan, result = fixture()
        result["sourcePrefabs"][0]["staticSortFields"]["loadedInstance"][0]["graphics"][0]["maxWorldVertexError"] = 0.002
        self.assertTrue(any("transformed mesh diagnostics differ" in row["message"] for row in verify(plan, result)))

    def test_rejects_collected_native_structural_diagnostic(self):
        plan, result = fixture()
        result["sourcePrefabs"][0]["staticSortFields"]["persistentAsset"][0]["structuralDiagnostics"] = [
            "STATIC_SORT_PROXY_EMPTY_RENDERER_READBACK_INVALID: source=fixture"
        ]
        self.assertTrue(any("native readback reports structural failures" in row["message"] for row in verify(plan, result)))

    def test_text_slot_readback_matches_exact_persistent_assets_and_proxy(self):
        spec = {"renderers": [{"sourceComponentId": "label-a", "sourceType": "cc.Label"}]}
        text = {"sourceComponentId": "label-a", "materialSlot": 1, "ownerGuid": "a" * 32,
                "ownerScopeVerified": True,
                "fontAssetGuid": "b" * 32, "fontAssetLocalFileId": 11, "spriteAssetGuid": None,
                "spriteAssetLocalFileId": 0, "materialGuid": "c" * 32, "materialLocalFileId": 13,
                "proxyMaterialGuid": "c" * 32, "proxyMaterialLocalFileId": 13,
                "ownerFontMaterialGuid": "8" * 32, "ownerFontMaterialLocalFileId": 18,
                "ownerFontMaterialFingerprint": "3" * 64, "sourceMaterialFingerprint": "4" * 64,
                "bakedProxyMaterialFingerprint": "4" * 64, "shaderGuid": "d" * 32,
                "textureGuid": "e" * 32, "proxyMeshGuid": "f" * 32,
                "ownerLocalFileId": 12, "materialLocalFileId": 13, "shaderLocalFileId": 14,
                "textureLocalFileId": 15, "proxyMeshLocalFileId": 16,
                "sourceMeshSha256": "1" * 64, "proxyMeshSha256": "2" * 64,
                "textSlotEnumeration": slot_enumeration("label-a", [slot_row(0, "empty-placeholder"), slot_row(1, "drawable")]),
                "persistentReferencesVerified": True, "fontAssetVerified": True, "spriteAssetVerified": True,
                "ownerFontMaterialVerified": True, "fallbackFontAssetVerified": True,
                "fallbackFontMaterialVerified": True, "fallbackAtlasVerified": True,
                "tmpFallbackDescriptorVerified": True, "transientFallbackVerified": True,
                "proxyMaterialVerified": True,
                "materialVerified": True, "shaderVerified": True, "textureVerified": True,
                "bakedProxyMeshVerified": True, "verified": True, "generatedSlotResolved": False}
        graphic = {"sourceComponentId": "label-a", "textMaterialSlot": 1, "meshAssetGuid": "f" * 32,
                   "proxyMeshSha256": "2" * 64, "materialGuid": "c" * 32, "textureGuid": "e" * 32}
        readback = {"textSources": [{"sourceNode": "label-node", "readbackMode": "persistent",
                                     "sourceComponentId": "label-a", "materialSlot": 1, "evidence": text}],
                    "textSourcesVerified": True, "graphics": [graphic]}
        spec["renderers"][0]["node"] = "label-node"
        self.assertEqual([], _check_text_sources(spec, readback, "persistent"))
        readback["textSources"][0]["evidence"]["textureGuid"] = "0" * 32
        self.assertTrue(any("do not match exactly one proxy graphic" in error
                            for error in _check_text_sources(spec, readback, "persistent")))
        readback["textSources"][0]["evidence"]["textureGuid"] = "e" * 32
        readback["textSources"][0]["evidence"]["textSlotEnumeration"]["rows"][0]["canvasNondegenerateTriangleCount"] = 1
        self.assertTrue(any("placeholder lacks exact slot-0 zero-draw proof" in error
                            for error in _check_text_sources(spec, readback, "persistent")))
        readback["textSources"][0]["evidence"]["textSlotEnumeration"]["rows"][0]["canvasNondegenerateTriangleCount"] = 0
        readback["textSources"].clear()
        self.assertTrue(any("TMP source component denominator differs" in error
                            for error in _check_text_sources(spec, readback, "persistent")))

    def test_loaded_text_slot_uses_exact_source_map_without_assetdb_owner_id(self):
        spec = {"renderers": [{"sourceComponentId": "label-a", "sourceType": "cc.RichText", "node": "label-node"}]}
        evidence = {"sourceComponentId": "label-a", "materialSlot": 0, "ownerGuid": None, "ownerLocalFileId": 0,
                    "ownerScopeVerified": True, "fontAssetGuid": "b" * 32, "fontAssetLocalFileId": 11,
                    "spriteAssetGuid": None, "spriteAssetLocalFileId": 0, "materialGuid": "c" * 32,
                    "proxyMaterialGuid": "c" * 32, "proxyMaterialLocalFileId": 13,
                    "ownerFontMaterialGuid": "8" * 32, "ownerFontMaterialLocalFileId": 18,
                    "ownerFontMaterialFingerprint": "3" * 64, "sourceMaterialFingerprint": "4" * 64,
                    "bakedProxyMaterialFingerprint": "4" * 64,
                    "shaderGuid": "d" * 32, "textureGuid": "e" * 32, "proxyMeshGuid": "f" * 32,
                    "materialLocalFileId": 13, "shaderLocalFileId": 14, "textureLocalFileId": 15,
                    "proxyMeshLocalFileId": 16, "sourceMeshSha256": "1" * 64, "proxyMeshSha256": "2" * 64,
                    "textSlotEnumeration": slot_enumeration("label-a", [slot_row(0, "drawable")]),
                    "persistentReferencesVerified": True, "fontAssetVerified": True, "spriteAssetVerified": True,
                    "ownerFontMaterialVerified": True, "fallbackFontAssetVerified": True,
                    "fallbackFontMaterialVerified": True, "fallbackAtlasVerified": True,
                    "tmpFallbackDescriptorVerified": True, "transientFallbackVerified": True,
                    "proxyMaterialVerified": True,
                    "materialVerified": True, "shaderVerified": True, "textureVerified": True,
                    "bakedProxyMeshVerified": True, "verified": True, "generatedSlotResolved": True,
                    "sourceStateVerified": True, "sourceMeshVerified": True}
        graphic = {"sourceComponentId": "label-a", "textMaterialSlot": 0, "meshAssetGuid": "f" * 32,
                   "proxyMeshSha256": "2" * 64, "materialGuid": "c" * 32, "textureGuid": "e" * 32}
        result = {"textSources": [{"sourceNode": "label-node", "readbackMode": "loaded",
                                    "sourceComponentId": "label-a", "materialSlot": 0, "evidence": evidence}],
                  "textSourcesVerified": True, "graphics": [graphic]}
        self.assertEqual([], _check_text_sources(spec, result, "loaded"))
        evidence["ownerScopeVerified"] = False
        self.assertTrue(any("loaded TMP owner does not match" in error for error in _check_text_sources(spec, result, "loaded")))

    def test_tmp_fallback_bake_requires_exact_sdk_descriptor_and_asset_provenance(self):
        spec = {"renderers": [{"sourceComponentId": "label-cjk", "sourceType": "cc.Label", "node": "label-node"}]}
        evidence = {"sourceComponentId": "label-cjk", "materialSlot": 1, "ownerGuid": None, "ownerLocalFileId": 0,
                    "ownerScopeVerified": True, "fontAssetGuid": "b" * 32, "fontAssetLocalFileId": 11,
                    "spriteAssetGuid": None, "spriteAssetLocalFileId": 0, "materialGuid": None,
                    "materialLocalFileId": 0, "proxyMaterialGuid": "c" * 32, "proxyMaterialLocalFileId": 13,
                    "ownerFontMaterialGuid": "8" * 32, "ownerFontMaterialLocalFileId": 18,
                    "fallbackFontAssetGuid": "6" * 32, "fallbackFontAssetLocalFileId": 20,
                    "fallbackFontMaterialGuid": "7" * 32, "fallbackFontMaterialLocalFileId": 21,
                    "fallbackAtlasGuid": "5" * 32, "fallbackAtlasLocalFileId": 22,
                    "tmpFallbackAlgorithm": "tmpro-fallback-font-material-v1",
                    "ownerFontMaterialFingerprint": "3" * 64, "fallbackFontMaterialFingerprint": "4" * 64,
                    "sourceMaterialFingerprint": "9" * 64, "transientFallbackFingerprint": "9" * 64,
                    "bakedProxyMaterialFingerprint": "9" * 64, "shaderGuid": "d" * 32,
                    "textureGuid": "e" * 32, "proxyMeshGuid": "f" * 32,
                    "ownerLocalFileId": 0, "shaderLocalFileId": 14, "textureLocalFileId": 15,
                    "proxyMeshLocalFileId": 16, "sourceMeshSha256": "1" * 64, "proxyMeshSha256": "2" * 64,
                    "textSlotEnumeration": slot_enumeration("label-cjk", [slot_row(0, "empty-placeholder"), slot_row(1, "drawable")]),
                    "persistentReferencesVerified": True, "ownerFontMaterialVerified": True,
                    "fallbackFontAssetVerified": True, "fallbackFontMaterialVerified": True,
                    "fallbackAtlasVerified": True, "tmpFallbackDescriptorVerified": True,
                    "transientFallbackVerified": True, "proxyMaterialVerified": True,
                    "fontAssetVerified": True, "spriteAssetVerified": True, "materialVerified": True,
                    "shaderVerified": True, "textureVerified": True, "bakedProxyMeshVerified": True,
                    "verified": True, "generatedSlotResolved": True, "sourceStateVerified": True,
                    "sourceMeshVerified": True}
        graphic = {"sourceComponentId": "label-cjk", "textMaterialSlot": 1, "meshAssetGuid": "f" * 32,
                   "proxyMeshSha256": "2" * 64, "materialGuid": "c" * 32, "textureGuid": "e" * 32}
        result = {"textSources": [{"sourceNode": "label-node", "readbackMode": "loaded",
                                    "sourceComponentId": "label-cjk", "materialSlot": 1, "evidence": evidence}],
                  "textSourcesVerified": True, "graphics": [graphic]}
        self.assertEqual([], _check_text_sources(spec, result, "loaded"))
        evidence["transientFallbackFingerprint"] = "0" * 64
        self.assertTrue(any("SDK fallback descriptor" in error for error in _check_text_sources(spec, result, "loaded")))

    def test_rejects_loss_of_uv4_uv7_or_native_canvas_mesh_channels(self):
        plan, result = fixture()
        result["sourcePrefabs"][0]["staticSortFields"]["persistentAsset"][0]["graphics"][0]["proxyUvChannelVertexCounts"][4] = 0
        self.assertTrue(any("UV channels 0–7" in row["message"] for row in verify(plan, result)))
        plan, result = fixture()
        result["sourcePrefabs"][0]["staticSortFields"]["loadedInstance"][0]["graphics"][0]["renderedUvChannelDimensions"][7] = 2
        self.assertTrue(any("CanvasRenderer UV channels" in row["message"] for row in verify(plan, result)))

    def test_null_sprite_uses_a_persistent_no_draw_carrier_not_a_fabricated_mesh(self):
        plan, result = fixture()
        spec = plan["staticSortQueue"][0]
        empty_spec = {"node": "newicon", "sourceComponentId": "sprite-empty", "sourceType": "cc.Sprite",
                      "expectedGraphicType": "UnityEngine.UI.Image", "sourceEnabled": True, "sourceActive": True,
                      "sourceTextureBound": False, "sourceTextEmpty": False, "sourceFontMissing": False}
        spec["renderers"].append(empty_spec)
        spec["drawEvents"].append({"kind": "renderer", "node": "newicon", "sourceComponentId": "sprite-empty"})
        empty = {"sourceComponentId": "sprite-empty", "sourceNode": "newicon", "sourceType": "cc.Sprite",
                 "sourceComponentType": "UnityEngine.UI.Image", "noDrawReason": "source-sprite-frame-null-native-image-disabled-zero-mesh",
                 "carrierGuid": "b" * 32, "carrierLocalFileId": 124, "sourceEnabled": True, "sourceActive": True,
                 "sourceActiveInHierarchy": True, "nativeGraphicEnabled": False, "nativeComponentEnabled": False,
                 "sourceTextureBound": False, "nativeTextureBound": False, "sourceTextEmpty": False,
                 "nativeTextEmpty": False, "sourceFontMissing": False, "nativeFontMissing": False,
                 "sourceMeshPresent": False, "sourceMeshVertexCount": 0, "sourceCanvasMaterialCount": 1,
                 "actualQueueIndex": 1, "carrierPresent": True, "sourceReferenceVerified": True,
                 "typedFieldsVerified": True, "sourceCommandsEmpty": False, "nativeCommandsEmpty": False,
                 "verified": True}
        binding = result["sourcePrefabs"][0]["staticSortFields"]
        for key in ("persistentAsset", "loadedInstance"):
            binding[key][0]["emptyRenderers"] = [copy.deepcopy(empty)]
        self.assertEqual([], verify(plan, result))
        binding["loadedInstance"][0]["emptyRenderers"][0]["nativeGraphicEnabled"] = True
        self.assertTrue(any("empty renderer typed evidence differs" in row["message"] for row in verify(plan, result)))

    def test_empty_text_graphics_and_disabled_sources_keep_typed_field_evidence(self):
        plan, result = fixture()
        spec = plan["staticSortQueue"][0]
        label = {"node": "empty-label", "sourceComponentId": "label-empty", "sourceType": "cc.Label",
                 "expectedGraphicType": "TMPro.TextMeshProUGUI", "sourceEnabled": True, "sourceActive": True,
                 "sourceTextureBound": False, "sourceText": "", "nativeTextExpectation": "",
                 "sourceTextEmpty": True, "sourceFontMissing": False}
        graphics_fields = '{"__type__":"cc.Graphics","_materials":[{"__uuid__":"material-id"}]}'
        import hashlib
        fields_sha = hashlib.sha256(graphics_fields.encode("utf-8")).hexdigest()
        native_graphics = {"node": "graphics", "sourceComponentId": "graphics-empty", "sourceType": "cc.Graphics",
                           "expectedGraphicType": "NativeStaticGraphics", "sourceEnabled": True, "sourceActive": True,
                           "sourceCommandsEmpty": True, "sourceDrawingCommands": "not-serialized-empty-in-fixed-state",
                           "sourceFieldsJson": graphics_fields, "sourceFieldsSha256": fields_sha,
                           "sourceMaterialGuids": ["c" * 32]}
        spec["renderers"].extend([label, native_graphics])
        disabled = {"node": "disabled", "sourceComponentId": "sprite-disabled", "sourceType": "cc.Sprite",
                    "expectedGraphicType": "UnityEngine.UI.Image", "sourceEnabled": False, "sourceActive": True,
                    "sourceTextureBound": True, "sourceTextEmpty": False, "sourceFontMissing": False}
        spec["nonDrawRenderers"] = [disabled]
        spec["drawEvents"].extend([
            {"kind": "renderer", "node": label["node"], "sourceComponentId": label["sourceComponentId"]},
            {"kind": "renderer", "node": native_graphics["node"], "sourceComponentId": native_graphics["sourceComponentId"]},
        ])

        def carrier(sid, node, native_type, reason, queue, **extra):
            return {"sourceComponentId": sid, "sourceNode": node, "sourceType": extra.pop("sourceType"),
                    "sourceComponentType": native_type, "noDrawReason": reason, "carrierGuid": "d" * 32,
                    "carrierLocalFileId": 125, "sourceEnabled": extra.pop("sourceEnabled"),
                    "sourceActive": True, "sourceActiveInHierarchy": True, "carrierPresent": True,
                    "sourceReferenceVerified": True, "typedFieldsVerified": True, "verified": True,
                    "actualQueueIndex": queue, "sourceMeshPresent": False, "sourceMeshVertexCount": 0,
                    "nativeGraphicEnabled": False, "nativeComponentEnabled": False,
                    "sourceTextureBound": False, "nativeTextureBound": False,
                    "sourceTextEmpty": True, "nativeTextEmpty": True,
                    "sourceFontMissing": False, "nativeFontMissing": False,
                    "sourceCommandsEmpty": False, "nativeCommandsEmpty": False, **extra}

        label_row = carrier("label-empty", "empty-label", "TMPro.TextMeshProUGUI", "source-text-empty-zero-mesh", 2,
                            sourceType="cc.Label", sourceEnabled=True, sourceText="", nativeText="",
                            sourceTextureBound=False, sourceTextEmpty=True, nativeTextEmpty=True,
                            nativeGraphicEnabled=True)
        graphics_row = carrier("graphics-empty", "graphics", "NativeStaticGraphics",
                               "source-graphics-command-stream-proven-empty", 3,
                               sourceType="cc.Graphics", sourceEnabled=True, sourceCommandsEmpty=True,
                               nativeCommandsEmpty=True, sourceDrawingCommands="not-serialized-empty-in-fixed-state",
                               sourceFieldsSha256=fields_sha, sourceMaterialGuids=["c" * 32],
                               actualSourceMaterialGuids=["c" * 32], nativeComponentEnabled=False,
                               sourceTextEmpty=False, nativeTextEmpty=False)
        disabled_row = carrier("sprite-disabled", "disabled", "UnityEngine.UI.Image", "source-renderer-disabled", -1,
                               sourceType="cc.Sprite", sourceEnabled=False, sourceTextureBound=True, nativeTextureBound=True,
                               sourceTextEmpty=False, nativeTextEmpty=False)
        binding = result["sourcePrefabs"][0]["staticSortFields"]
        for key in ("persistentAsset", "loadedInstance"):
            read = binding[key][0]
            read["emptyRenderers"] = [copy.deepcopy(label_row), copy.deepcopy(graphics_row), copy.deepcopy(disabled_row)]
        self.assertEqual([], verify(plan, result))
        binding["persistentAsset"][0]["emptyRenderers"][1]["actualSourceMaterialGuids"] = []
        self.assertTrue(any("empty renderer typed evidence differs" in row["message"] for row in verify(plan, result)))

    def test_rejects_incomplete_or_duplicate_persistent_queue_rows(self):
        plan, result = fixture()
        binding = result["sourcePrefabs"][0]["staticSortFields"]
        binding["persistentAsset"] = []
        self.assertTrue(any("persistent queue scope count differs" in row["message"] for row in verify(plan, result)))
        plan, result = fixture()
        binding = result["sourcePrefabs"][0]["staticSortFields"]
        binding["loadedInstance"].append(copy.deepcopy(binding["loadedInstance"][0]))
        self.assertTrue(any("loaded queue scope count differs" in row["message"] for row in verify(plan, result)))

    def test_creator_verifies_persistent_and_initialized_source_sort_fields(self):
        spec = {"rootScope": "root", "sourcePrefabId": "prefab-c", "prefabPath": "db://assets/A.prefab",
                "sourceOriginalDrawEvents": [{"kind": "renderer", "node": "icon", "sourceComponentId": "sprite"}],
                "sourceDrawEvents": [{"kind": "renderer", "node": "icon", "sourceComponentId": "sprite"}],
                "sourceSortOrderFields": [{"sourceId": "order", "nativeId": "native-order", "node": "icon",
                                            "sortOrder": 4, "enabled": False}],
                "sourceSortRoots": [{"sourceId": "sortroot", "nativeId": "native-root", "node": "root", "enabled": True}],
                "renderers": [{"sourceComponentId": "sprite", "node": "icon"}], "masks": [],
                "nonDrawRenderers": [], "sourceNonDrawRenderers": []}
        plan = {"staticSortQueue": [spec], "sourcePrefabs": [{"sourceId": "prefab-c", "path": spec["prefabPath"]}]}
        order = {"sourceId": "order", "expectedSourceId": "order", "nativeId": "native-order",
                 "expectedNativeId": "native-order", "node": "icon", "sourceSortOrder": 4,
                 "effectiveSourceSortOrder": 0, "enabledInSource": False, "renderedOnNode": False,
                 "componentUuid": "component-uuid-order", "nativeClass": "MonkeyStaticSortOrderField", "verified": True}
        sortroot = {"sourceId": "sortroot", "expectedSourceId": "sortroot", "nativeId": "native-root",
                    "expectedNativeId": "native-root", "node": "root", "enabledInSource": True,
                    "componentUuid": "component-uuid-root", "nativeClass": "CreatorStaticSortRootField", "verified": True}
        graphic = {"sourceComponentId": "sprite", "sourceNode": "icon", "sourceFingerprint": "fingerprint",
                   "proxyFingerprint": "fingerprint", "originalLayer": 8, "proxyLayer": 8,
                   "opacityVerified": True, "verified": True}
        persistent = {"rootScope": "root", "presentationMode": "persistent", "verified": True,
                      "sourceTreePreserved": True, "sourceFieldsPreserved": True, "sourceSortRootsPreserved": True,
                      "sourceLayersPreserved": True, "drawSequenceVerified": True,
                      "sourceQueueProjectionVerified": True,
                      "sourceOriginalDrawEvents": copy.deepcopy(spec["sourceOriginalDrawEvents"]),
                      "sourceNonDrawSourceMappings": [], "sourceNonDrawRenderers": [],
                      "sourceSortOrderFields": [order], "sourceSortRoots": [sortroot], "graphics": [graphic], "masks": []}
        initialized = copy.deepcopy(persistent)
        initialized.update({"presentationMode": "initialized", "sourceSuppressed": True,
                            "nestedProxyRootsDisabled": True})
        result = {"sourcePrefabs": [{"sourceId": "prefab-c", "path": spec["prefabPath"],
                                     "staticSortQueue": {"persistent": persistent, "initialized": initialized}}]}
        self.assertEqual([], verify_creator(plan, result))
        result["sourcePrefabs"][0]["staticSortQueue"]["persistent"]["sourceSortOrderFields"][0]["componentUuid"] = ""
        self.assertTrue(any("SortOrder typed field differs" in row["message"] for row in verify_creator(plan, result)))

    def test_creator_projection_validates_original_empty_graphics_event_and_mapping(self):
        import hashlib
        raw = {"__type__": "cc.Graphics", "_materials": [{"__uuid__": "source-material"}]}
        fields_json = '{"__type__":"cc.Graphics","_materials":[{"__uuid__":"source-material"}]}'
        fields_sha = hashlib.sha256(fields_json.encode("utf-8")).hexdigest()
        event = {"kind": "renderer", "node": "graphics-node", "sourceComponentId": "graphics-source"}
        spec = {"rootScope": "root", "sourcePrefabId": "prefab-g", "prefabPath": "db://assets/G.prefab",
                "sourceOriginalDrawEvents": [event], "sourceDrawEvents": [], "renderers": [],
                "sourceSortOrderFields": [], "sourceSortRoots": [], "masks": [],
                "sourceNodeActive": {"graphics-node": True},
                "nonDrawRenderers": [{"sourceId": "graphics-source", "nativeId": "native-graphics", "node": "graphics-node",
                    "sourceType": "cc.Graphics", "expectedNativeType": "Graphics", "sourceEnabled": True,
                    "sourceActive": True, "sourceFields": raw, "sourceFieldsJson": fields_json,
                    "sourceFieldsSha256": fields_sha, "sourceSpriteFrameUuid": None, "sourceText": None,
                    "sourceNeedsSpriteBinding": False,
                    "nativeTextExpectation": None, "sourceTextEmpty": False, "sourceFontId": None,
                    "creatorMarkup": None, "nativeFontAssetId": None, "nativeFallbackAssetIds": [],
                    "targetSystemFontFamily": None, "noDrawReason": "empty-command-stream",
                    "nativeEnabledExpected": False, "initialCommandStreamEmpty": True,
                    "sourceDrawingCommands": "not-serialized-empty-in-fixed-state", "sourceMaterialIds": ["source-material"]}],
                "sourceNonDrawRenderers": [{"sourceComponentId": "graphics-source", "node": "graphics-node",
                    "disposition": "source-render-event", "sourceEventIndex": 0,
                    "noDrawReason": "empty-command-stream"}]}
        native = {"sourceId": "graphics-source", "nativeId": "native-graphics", "node": "graphics-node",
            "sourceType": "cc.Graphics", "expectedNativeType": "Graphics", "actualNativeType": "Graphics",
            "componentUuid": "component-uuid-graphics", "sourceEnabled": True, "sourceActive": True,
            "componentEnabled": False, "nativeEnabledExpected": False, "nodeActive": True, "effectiveActive": True,
            "sourceFieldsJson": fields_json, "sourceFieldsSha256": fields_sha,
            "sourceSpriteFrameUuid": None, "nativeSpriteFrameUuid": None, "sourceText": None,
            "sourceNeedsSpriteBinding": False,
            "actualText": None, "sourceFontId": None, "nativeFontAssetId": None, "nativeFallbackAssetIds": [],
            "targetSystemFontFamily": None, "creatorMarkup": None, "noDrawReason": "empty-command-stream",
            "sourceTextEmpty": False, "nativeTextExpectation": None, "initialCommandStreamEmpty": True,
            "sourceDrawingCommands": "not-serialized-empty-in-fixed-state", "sourceMaterialIds": ["source-material"],
            "graphicsPathCount": 0, "nativeMaterialUuid": "f0416e68-0200-4b77-a926-4f9d16e494da",
            "nativeEffectUuid": "1c02ae6f-4492-4915-b8f8-7492a3b1e4cd", "nativeMaterialVerified": True,
            "verified": True}
        persistent = {"rootScope": "root", "presentationMode": "persistent", "verified": True,
                      "sourceTreePreserved": True, "sourceFieldsPreserved": True, "sourceSortRootsPreserved": True,
                      "sourceLayersPreserved": True, "drawSequenceVerified": True,
                      "sourceQueueProjectionVerified": True, "sourceOriginalDrawEvents": [copy.deepcopy(event)],
                      "sourceNonDrawSourceMappings": [{**copy.deepcopy(spec["sourceNonDrawRenderers"][0]), "verified": True}],
                      "sourceNonDrawRenderers": [copy.deepcopy(native)], "sourceSortOrderFields": [],
                      "sourceSortRoots": [], "graphics": [], "masks": []}
        initialized = copy.deepcopy(persistent)
        initialized.update({"presentationMode": "initialized", "sourceSuppressed": True,
                            "nestedProxyRootsDisabled": True})
        plan = {"staticSortQueue": [spec], "sourcePrefabs": [{"sourceId": "prefab-g", "path": spec["prefabPath"]}]}
        result = {"sourcePrefabs": [{"sourceId": "prefab-g", "path": spec["prefabPath"],
                                     "staticSortQueue": {"persistent": persistent, "initialized": initialized}}]}
        self.assertEqual([], verify_creator(plan, result))
        persistent["sourceNonDrawSourceMappings"][0]["sourceEventIndex"] = 4
        self.assertTrue(any("index/node/reason differs" in row["message"] for row in verify_creator(plan, result)))
        persistent["sourceNonDrawSourceMappings"][0]["sourceEventIndex"] = 0
        persistent["sourceNonDrawSourceMappings"].append(copy.deepcopy(persistent["sourceNonDrawSourceMappings"][0]))
        self.assertTrue(any("mapping count differs" in row["message"] or "duplicates source ID" in row["message"]
                            for row in verify_creator(plan, result)))
        persistent["sourceNonDrawSourceMappings"] = [copy.deepcopy(spec["sourceNonDrawRenderers"][0] | {"verified": True})]
        persistent["sourceNonDrawRenderers"] = []
        self.assertTrue(any("native non-draw renderer source IDs differ" in row["message"]
                            for row in verify_creator(plan, result)))

    def test_spine_empty_owner_delegation_requires_typed_child_renderers(self):
        from src.monkey.prefab_static_sort_readback import _check_spine_owner_delegations
        source_id = "source-spine"
        spec = {"renderers": [{"sourceComponentId": source_id, "node": "spine-node", "sourceType": "sp.Skeleton"}]}
        graphics = [
            {"sourceComponentId": source_id, "sourceNode": "spine-node", "nativeGraphicType": "UnityEngine.UI.RawImage",
             "generatedSourceChild": True, "vertexCount": 18, "submeshIndex": 0},
            {"sourceComponentId": source_id, "sourceNode": "spine-node", "nativeGraphicType": "UnityEngine.UI.RawImage",
             "generatedSourceChild": True, "vertexCount": 6, "submeshIndex": 0},
        ]
        proof = {"sourceComponentId": source_id, "sourceNode": "spine-node",
            "sourceGraphicType": "Spine.Unity.SkeletonGraphic", "sourceIdentityComponentId": source_id,
            "sourceDataAssetId": "spineAsset:test-source",
            "sourceDataAssetPath": "Assets/Game/Content/Spine/Test/Test_SkeletonData.asset",
            "sourceBindingPlanPath": "Assets/Game/Editor/Conversion/spine-native-binding-plan.json",
            "sourceBindingPlanSha256": "f" * 64, "sourceManifestSha256": "1" * 64,
            "sourceDataAssetGuid": "a" * 32, "rootMeshVertexCount": 0, "rootMeshSubmeshCount": -1,
            "rootCanvasMaterialCount": 0, "rootMeshWasMissing": True, "rootMeshDelegated": True,
            "sourceIdentityVerified": True, "sourceDataReferenceVerified": True,
            "childRendererListVerified": True, "childReferencesPersistent": True, "verified": True,
            "delegatedChildPaths": ["root/spine/segment-0", "root/spine/segment-1"],
            "delegatedChildGraphicTypes": ["UnityEngine.UI.RawImage"] * 2,
            "childMeshVertexCounts": [18, 6], "childMeshSubmeshCounts": [1, 1],
            "childCanvasMaterialCounts": [1, 1], "delegatedChildTextureGuids": ["b" * 32, "c" * 32],
            "delegatedChildMaterialGuids": ["d" * 32, "e" * 32]}
        row = {"graphics": graphics, "spineOwnerDelegations": [copy.deepcopy(proof)]}
        spine_plan = {"spineNativeStage": {"sourceManifestSha256": proof["sourceManifestSha256"],
            "components": [{"sourceComponentId": source_id, "sourceHasStaticDataReference": True,
                            "sourceDataAssetId": proof["sourceDataAssetId"]}],
            "dataAssets": [{"sourceAssetId": proof["sourceDataAssetId"],
                            "skeletonDataAssetPath": proof["sourceDataAssetPath"]}]}}
        self.assertEqual([], _check_spine_owner_delegations(spec, row, "persistent", spine_plan))
        wrong_binding = copy.deepcopy(row)
        wrong_binding["spineOwnerDelegations"][0]["sourceDataAssetId"] = "spineAsset:other"
        self.assertTrue(any("owner/registered-renderer typed proof" in message
                            for message in _check_spine_owner_delegations(spec, wrong_binding, "persistent", spine_plan)))
        row["spineOwnerDelegations"][0]["sourceDataReferenceVerified"] = False
        self.assertTrue(any("owner/registered-renderer typed proof" in message
                            for message in _check_spine_owner_delegations(spec, row, "persistent", spine_plan)))
        row["spineOwnerDelegations"] = [copy.deepcopy(proof), copy.deepcopy(proof)]
        self.assertTrue(any("source ID repeats" in message
                            for message in _check_spine_owner_delegations(spec, row, "persistent", spine_plan)))
        row["spineOwnerDelegations"] = [copy.deepcopy(proof)]
        row["graphics"] = graphics[:1]
        self.assertTrue(any("do not cover delegated native renderers" in message
                            for message in _check_spine_owner_delegations(spec, row, "loaded", spine_plan)))
        row["graphics"] = graphics
        row["spineOwnerDelegations"] = []
        self.assertTrue(any("lacks owner delegation proof" in message
                            for message in _check_spine_owner_delegations(spec, row, "persistent", spine_plan)))

    def test_spine_nondraw_owner_requires_exact_inactive_registered_children(self):
        from src.monkey.prefab_static_sort_readback import _check_spine_non_draw_children
        source_id = "source-spine-inactive"
        spec = {"nonDrawRenderers": [{"sourceComponentId": source_id, "node": "spine-node",
                                      "sourceType": "sp.Skeleton", "sourceEnabled": True,
                                      "sourceActive": False}]}
        child = {"sourceComponentId": source_id, "sourceNode": "spine-node", "noDrawReason": "inactive-source",
            "sourceIdentityComponentId": source_id, "sourceDataAssetId": "spineAsset:fixture",
            "sourceDataAssetPath": "Assets/Game/Content/Spine/Fixture.asset", "sourceDataAssetGuid": "a" * 32,
            "childPath": "3/0", "childGraphicType": "UnityEngine.UI.RawImage",
            "childMaterialGuid": "b" * 32, "childTextureGuid": "c" * 32,
            "sourceOwnerEnabled": True, "sourceNodeActive": False,
            "sourceChildEnabled": True, "sourceChildActiveSelf": True, "sourceChildActiveInHierarchy": False,
            "targetChildEnabled": True, "targetChildActiveInHierarchy": False,
            "sourceIdentityVerified": True, "sourceDataReferenceVerified": True,
            "registeredChildVerified": True, "childReferencePersistent": True,
            "childNoDrawVerified": True, "sourceChildMeshVertexCount": 12,
            "sourceChildMeshSubmeshCount": 1, "sourceChildMaterialCount": 1, "verified": True}
        row = {"spineNonDrawChildren": [copy.deepcopy(child)]}
        self.assertEqual([], _check_spine_non_draw_children(spec, row, "persistent"))
        row["spineNonDrawChildren"][0]["sourceChildActiveInHierarchy"] = True
        row["spineNonDrawChildren"][0]["targetChildActiveInHierarchy"] = True
        self.assertTrue(any("can still draw" in message
                            for message in _check_spine_non_draw_children(spec, row, "loaded")))
        row["spineNonDrawChildren"] = [copy.deepcopy(child)]
        row["spineNonDrawChildren"][0]["registeredChildVerified"] = False
        self.assertTrue(any("owner/child source identity or resource proof differs" in message
                            for message in _check_spine_non_draw_children(spec, row, "persistent")))

    def test_creator_nondraw_sprite_requires_exact_binding_policy_and_native_frame(self):
        from src.monkey.prefab_static_sort_readback import _creator_non_draw_errors
        def case(source_frame, needs_binding, source_asset_id, image_uuid, resolved_frame,
                 enabled, source_enabled=True, actual_frame="__expected__", saved_image_uuid=None,
                 saved_frame_uuid=None):
            fields = {"__type__": "cc.Sprite"}
            if source_frame is not None:
                fields["_spriteFrame"] = {"__uuid__": source_frame}
            fields_json = __import__("json").dumps(fields, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            fields_hash = __import__("hashlib").sha256(fields_json.encode("utf-8")).hexdigest()
            expected = {"sourceId": "sprite-id", "nativeId": "sprite-native", "node": "sprite-node",
                "sourceType": "cc.Sprite", "expectedNativeType": "Sprite", "sourceEnabled": source_enabled,
                "sourceActive": True, "nativeEnabledExpected": enabled, "sourceNeedsSpriteBinding": needs_binding,
                "sourceFields": fields, "sourceFieldsJson": fields_json, "sourceFieldsSha256": fields_hash,
                "sourceSpriteFrameUuid": source_frame, "sourceTextureBound": source_frame is not None,
                "sourceSpriteFrameAssetId": source_asset_id, "nativeSpriteImageUuidExpected": image_uuid,
                "sourceText": None, "sourceTextEmpty": False,
                "nativeTextExpectation": None, "sourceFontId": None, "nativeFontAssetId": None,
                "nativeFallbackAssetIds": [], "targetSystemFontFamily": None, "creatorMarkup": None,
                "noDrawReason": "null-sprite-frame" if needs_binding else "disabled-source" if not source_enabled else "invalid-active-draw"}
            actual = {"sourceId": "sprite-id", "nativeId": "sprite-native", "node": "sprite-node",
                "sourceType": "cc.Sprite", "expectedNativeType": "Sprite", "actualNativeType": "Sprite",
                "componentUuid": "native-component-sprite", "sourceEnabled": source_enabled, "sourceActive": True,
                "componentEnabled": enabled, "nativeEnabledExpected": enabled, "sourceNeedsSpriteBinding": needs_binding,
                "nodeActive": True, "effectiveActive": True, "noDrawReason": expected["noDrawReason"],
                "sourceFieldsJson": fields_json, "sourceFieldsSha256": fields_hash,
                "sourceSpriteFrameUuid": source_frame,
                "sourceSpriteFrameAssetId": source_asset_id, "nativeSpriteImageUuidExpected": image_uuid,
                "nativeSpriteFrameUuid": resolved_frame if actual_frame == "__expected__" else actual_frame,
                "nativeSpriteFrameUuidExpected": resolved_frame, "sourceText": None, "actualText": None,
                "sourceTextEmpty": False, "nativeTextExpectation": None, "sourceFontId": None,
                "nativeFontAssetId": None, "nativeFallbackAssetIds": [], "targetSystemFontFamily": None,
                "creatorMarkup": None, "verified": True}
            spec = {"nonDrawRenderers": [expected], "sourceNodeActive": {"sprite-node": True}}
            assets = [] if source_asset_id is None else [{"sourceId": source_asset_id, "kind": "sprite",
                "uuid": image_uuid if saved_image_uuid is None else saved_image_uuid,
                "spriteFrameUuid": resolved_frame if saved_frame_uuid is None else saved_frame_uuid}]
            return _creator_non_draw_errors(spec, {"sourceNonDrawRenderers": [actual]}, assets)

        image_uuid = "12345678-1234-4234-8234-1234567890ab"
        sprite_frame_uuid = "12345678-1234-4234-8234-1234567890ab@f9941"
        self.assertEqual([], case(None, True, None, None, None, False))
        self.assertEqual([], case("source-frame", False, "fixture:frame", image_uuid, sprite_frame_uuid,
                                  False, source_enabled=False))
        self.assertTrue(case(None, True, "fixture:frame", image_uuid, sprite_frame_uuid, False))
        self.assertTrue(case("source-frame", False, "fixture:frame", image_uuid, sprite_frame_uuid, False,
                             source_enabled=False, actual_frame="wrong-native-frame"))
        self.assertTrue(case("source-frame", False, "fixture:frame", image_uuid, sprite_frame_uuid, False,
                             source_enabled=False, saved_image_uuid="ffffffff-ffff-4fff-8fff-ffffffffffff"))
        self.assertTrue(case("source-frame", False, "fixture:frame", image_uuid, sprite_frame_uuid, False,
                             source_enabled=False, saved_frame_uuid="12345678-1234-4234-8234-1234567890ab@other"))
        self.assertTrue(case("source-frame", True, None, None, None, False))

    def test_creator_verifier_resolves_native_frame_through_saved_image_asset_rows(self):
        import hashlib
        import json
        source_id = "fixture:prefab#1/components/0"
        source_event = {"kind": "renderer", "node": "sprite-node", "sourceComponentId": source_id}
        source_frame = "fixture-source-frame"
        asset_id = "fixture:frame-asset"
        image_uuid = "12345678-1234-4234-8234-1234567890ab"
        frame_uuid = "12345678-1234-4234-8234-1234567890ab@f9941"
        source_fields = {"__type__": "cc.Sprite", "_spriteFrame": {"__uuid__": source_frame}}
        fields_json = json.dumps(source_fields, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        fields_hash = hashlib.sha256(fields_json.encode("utf-8")).hexdigest()
        nondraw = {"sourceId": source_id, "nativeId": "native-sprite", "node": "sprite-node",
            "sourceType": "cc.Sprite", "expectedNativeType": "Sprite", "sourceEnabled": False,
            "sourceActive": True, "sourceNeedsSpriteBinding": False, "nativeEnabledExpected": False,
            "sourceFields": source_fields, "sourceFieldsJson": fields_json, "sourceFieldsSha256": fields_hash,
            "sourceSpriteFrameUuid": source_frame, "sourceTextureBound": True,
            "sourceSpriteFrameAssetId": asset_id, "nativeSpriteImageUuidExpected": image_uuid,
            "sourceText": None, "sourceTextEmpty": False, "nativeTextExpectation": None,
            "sourceFontId": None, "nativeFontAssetId": None, "nativeFallbackAssetIds": [],
            "targetSystemFontFamily": None, "creatorMarkup": None, "noDrawReason": "disabled-source"}
        mapping = {"sourceComponentId": source_id, "node": "sprite-node", "disposition": "source-render-event",
                   "sourceEventIndex": 0, "noDrawReason": "disabled-source"}
        spec = {"rootScope": "root", "sourcePrefabId": "fixture:prefab", "prefabPath": "db://assets/Fixture.prefab",
            "sourceOriginalDrawEvents": [source_event], "sourceDrawEvents": [], "renderers": [], "masks": [],
            "sourceSortOrderFields": [], "sourceSortRoots": [], "nonDrawRenderers": [nondraw],
            "sourceNonDrawRenderers": [mapping], "sourceNodeActive": {"sprite-node": True}}
        plan = {"staticSortQueue": [spec], "sourcePrefabs": [{"sourceId": spec["sourcePrefabId"], "path": spec["prefabPath"]}]}
        native = {"sourceId": source_id, "nativeId": "native-sprite", "node": "sprite-node",
            "sourceType": "cc.Sprite", "expectedNativeType": "Sprite", "actualNativeType": "Sprite",
            "componentUuid": "native-component-sprite", "sourceEnabled": False, "sourceActive": True,
            "componentEnabled": False, "nativeEnabledExpected": False, "sourceNeedsSpriteBinding": False,
            "nodeActive": True, "effectiveActive": True, "noDrawReason": "disabled-source",
            "sourceFieldsJson": fields_json, "sourceFieldsSha256": fields_hash,
            "sourceSpriteFrameUuid": source_frame, "nativeSpriteFrameUuid": frame_uuid,
            "sourceSpriteFrameAssetId": asset_id, "nativeSpriteImageUuidExpected": image_uuid,
            "nativeSpriteFrameUuidExpected": frame_uuid, "sourceText": None, "actualText": None,
            "sourceTextEmpty": False, "nativeTextExpectation": None, "sourceFontId": None,
            "nativeFontAssetId": None, "nativeFallbackAssetIds": [], "targetSystemFontFamily": None,
            "creatorMarkup": None, "verified": True}
        asset = {"sourceId": asset_id, "kind": "sprite", "uuid": image_uuid, "spriteFrameUuid": frame_uuid}
        persistent = {"rootScope": "root", "presentationMode": "persistent", "verified": True,
            "sourceTreePreserved": True, "sourceFieldsPreserved": True, "sourceSortRootsPreserved": True,
            "sourceLayersPreserved": True, "drawSequenceVerified": True, "sourceQueueProjectionVerified": True,
            "sourceOriginalDrawEvents": [source_event], "sourceNonDrawSourceMappings": [{**mapping, "verified": True}],
            "sourceNonDrawRenderers": [native], "sourceSortOrderFields": [], "sourceSortRoots": [],
            "graphics": [], "masks": []}
        initialized = {**persistent, "presentationMode": "initialized", "sourceSuppressed": True,
                       "nestedProxyRootsDisabled": True}
        saved = {"assets": [asset], "sourcePrefabs": [{"sourceId": spec["sourcePrefabId"], "path": spec["prefabPath"],
            "staticSortQueue": {"persistent": persistent, "initialized": initialized}}]}
        self.assertEqual([], verify_creator(plan, saved))
        saved["assets"][0]["uuid"] = "ffffffff-ffff-4fff-8fff-ffffffffffff"
        self.assertTrue(any("saved ImageAsset/SpriteFrame identity mapping differs" in row["message"]
                            for row in verify_creator(plan, saved)))

    def test_negative_z_reflection_keeps_rect_axes_and_depth_vertices(self):
        # Neutral matrix proof for the Unity decomposition used by
        # CopyWorldRect: source basis (X,Y,-Z) must stay (X,Y,-Z), rather than
        # Matrix4x4.rotation/lossyScale redistributing reflection into X/Y.
        source_basis = ((1, 0, 0), (0, 1, 0), (0, 0, -1))
        signed_scale = (1, 1, -1)
        reconstructed_basis = ((1 * signed_scale[0], 0, 0),
                               (0, 1 * signed_scale[1], 0),
                               (0, 0, 1 * signed_scale[2]))
        self.assertEqual(source_basis, reconstructed_basis)
        rect_corners = [(-55, -55, 0), (55, -55, 0), (55, 55, 0), (-55, 55, 0)]
        source_world = [(x, y, -z) for x, y, z in rect_corners]
        proxy_world = [(x * signed_scale[0], y * signed_scale[1], z * signed_scale[2])
                       for x, y, z in rect_corners]
        self.assertEqual(source_world, proxy_world)
        source_depth_vertex = (0.25, -0.5, 2.0)
        proxy_depth_vertex = (source_depth_vertex[0] * signed_scale[0],
                              source_depth_vertex[1] * signed_scale[1],
                              source_depth_vertex[2] * signed_scale[2])
        self.assertEqual((0.25, -0.5, -2.0), proxy_depth_vertex)
        helper = Path(__file__).parents[1] / "src/monkey/targets/UnityStaticSortQueueProxy.cs"
        text = helper.read_text(encoding="utf-8")
        self.assertIn("Vector3.Dot(z, forward)", text)
        self.assertIn("MatrixNear(local, reconstructed, 1e-4f)", text)
        zero_depth_source = ((1, 0, 0), (0, 1, 0), (0, 0, 0))
        zero_depth_proxy = ((1, 0, 0), (0, 1, 0), (0, 0, 0))
        self.assertEqual(zero_depth_source, zero_depth_proxy)
        self.assertIn("z.sqrMagnitude <= 1e-16f ? 0f", text)
        self.assertNotIn("z.magnitude <= 1e-8f", text)

    def test_zero_depth_parent_uses_invertible_ui_plane_for_position_and_mesh(self):
        # A parent scaled to Z=0 has a singular 4x4 inverse but retains a
        # perfectly usable two-axis UI plane. Reconstruct a rotated/scaled
        # child through the same Gram-system plane map.
        px = (0.8660254, 0.5, 0.0)
        py = (-1.5, 2.5980762, 0.0)
        origin = (11.0, -4.0, 0.0)

        def dot(a, b):
            return sum(x * y for x, y in zip(a, b))

        def add(a, b):
            return tuple(x + y for x, y in zip(a, b))

        def scale(a, factor):
            return tuple(x * factor for x in a)

        def solve_plane(vector):
            xx, xy, yy = dot(px, px), dot(px, py), dot(py, py)
            determinant = xx * yy - xy * xy
            dx, dy = dot(px, vector), dot(py, vector)
            u = (dx * yy - dy * xy) / determinant
            v = (dy * xx - dx * xy) / determinant
            reconstructed = add(scale(px, u), scale(py, v))
            return (u, v), reconstructed

        local_position = (5.0, -7.0)
        world_position = add(origin, add(scale(px, local_position[0]), scale(py, local_position[1])))
        found_position, reconstructed_position = solve_plane(tuple(a - b for a, b in zip(world_position, origin)))
        self.assertAlmostEqual(local_position[0], found_position[0], places=5)
        self.assertAlmostEqual(local_position[1], found_position[1], places=5)
        self.assertAlmostEqual(0.0, math.dist(world_position, add(origin, reconstructed_position)), places=5)

        angle = math.radians(31.0)
        relative_right = (1.2 * math.cos(angle), 1.2 * math.sin(angle))
        relative_up = (-0.7 * math.sin(angle), 0.7 * math.cos(angle))
        source_right = add(scale(px, relative_right[0]), scale(py, relative_right[1]))
        source_up = add(scale(px, relative_up[0]), scale(py, relative_up[1]))
        mapped_right, rebuilt_right = solve_plane(source_right)
        mapped_up, rebuilt_up = solve_plane(source_up)
        self.assertAlmostEqual(relative_right[0], mapped_right[0], places=5)
        self.assertAlmostEqual(relative_right[1], mapped_right[1], places=5)
        self.assertAlmostEqual(relative_up[0], mapped_up[0], places=5)
        self.assertAlmostEqual(relative_up[1], mapped_up[1], places=5)
        self.assertAlmostEqual(0.0, math.dist(source_right, rebuilt_right), places=5)
        self.assertAlmostEqual(0.0, math.dist(source_up, rebuilt_up), places=5)
        helper = Path(__file__).parents[1] / "src/monkey/targets/UnityStaticSortQueueProxy.cs"
        text = helper.read_text(encoding="utf-8")
        self.assertIn("TrySolvePlaneCoordinates", text)
        self.assertIn("CopyWorldRectOnSingularPlane", text)
        self.assertIn("InverseTransformPointForUiPlane", text)

    def test_graphic_collection_stops_at_every_source_node_boundary(self):
        # Neutral traversal fixture: a disabled/inactive source child owns its
        # own non-draw row and must not be absorbed into the parent's TMP mesh.
        source_child_nodes = {"inactive_sprite", "disabled_label"}
        owner_children = ["inactive_sprite", "disabled_label", "generated_tmp_segment"]

        def collect(children):
            collected = []
            for child in children:
                if child in source_child_nodes:
                    continue
                if child == "generated_tmp_segment":
                    collected.append(child)
                    continue
                raise ValueError("unclassified child graphic: " + child)
            return collected

        self.assertEqual(["generated_tmp_segment"], collect(owner_children))
        with self.assertRaisesRegex(ValueError, "unclassified child graphic: foreign_image"):
            collect(owner_children + ["foreign_image"])
        helper = Path(__file__).parents[1] / "src/monkey/targets/UnityStaticSortQueueProxy.cs"
        text = helper.read_text(encoding="utf-8")
        self.assertIn("if (sourceNode != null && sourceNode != row.node) continue;", text)
        self.assertIn(";childPath=", text)
        self.assertIn(";graphicTypes=", text)

    def test_non_draw_carrier_accepts_inactive_but_enabled_and_rejects_active_enabled(self):
        valid_non_draw = {"sourceEnabled": True, "sourceActive": False}
        invalid_non_draw = {"sourceEnabled": True, "sourceActive": True}
        should_reject = lambda spec: spec["sourceEnabled"] and spec["sourceActive"]
        self.assertFalse(should_reject(valid_non_draw))
        self.assertTrue(should_reject(invalid_non_draw))
        helper = Path(__file__).parents[1] / "src/monkey/targets/UnityStaticSortQueueProxy.cs"
        text = helper.read_text(encoding="utf-8")
        self.assertIn("row.sourceEnabled && row.sourceActive", text)

    def test_richtext_source_markup_and_native_projection_are_separate(self):
        expected = {"sourceComponentId": "rich-empty", "node": "rich-node", "sourceType": "cc.RichText",
                    "expectedGraphicType": "TMPro.TextMeshProUGUI", "sourceEnabled": True,
                    "sourceActive": False, "sourceText": "<color=#fff></color>",
                    "nativeTextExpectation": "<color=#fff></color>", "sourceTextEmpty": True,
                    "sourceFontMissing": False, "sourceTextureBound": False}
        actual = {"sourceNode": "rich-node", "sourceType": "cc.RichText",
                  "sourceComponentType": "TMPro.TextMeshProUGUI", "sourceEnabled": True,
                  "sourceActive": False, "sourceActiveInHierarchy": False,
                  "sourceText": "<color=#fff></color>", "nativeTextExpectation": "<color=#fff></color>",
                  "nativeText": "<color=#fff></color>", "sourceTextEmpty": True, "nativeTextEmpty": True,
                  "nativeGraphicEnabled": True,
                  "sourceFontMissing": False, "nativeFontMissing": False,
                  "sourceTextureBound": False, "sourceReferenceVerified": True,
                  "typedFieldsVerified": True, "carrierPresent": True, "verified": True,
                  "carrierGuid": "e" * 32, "carrierLocalFileId": 126,
                  "carrierLocalFileId": 126, "noDrawReason": "source-node-inactive"}
        self.assertTrue(_empty_renderer_matches(expected, actual, "persistent"))
        expected["sourceText"] = "<color=#fff>source</color>"
        expected["nativeTextExpectation"] = "<color=#0f0>target</color>"
        actual["sourceText"] = expected["sourceText"]
        actual["nativeTextExpectation"] = expected["nativeTextExpectation"]
        actual["nativeText"] = expected["nativeTextExpectation"]
        self.assertTrue(_empty_renderer_matches(expected, actual, "persistent"))
        actual["nativeText"] = actual["sourceText"]
        self.assertFalse(_empty_renderer_matches(expected, actual, "persistent"))


if __name__ == "__main__":
    unittest.main()
