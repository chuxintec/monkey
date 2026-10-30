import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EDITOR_SOURCE = ROOT / "src/monkey/targets/UnityStaticSortTextSource.cs"
RUNTIME_SOURCE = ROOT / "src/monkey/targets/NativeStaticSortTextSource.cs"


def _body(source, signature):
    start = source.find(signature)
    if start < 0:
        raise AssertionError(f"missing source API: {signature}")
    opening = source.find("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[opening + 1:index]
    raise AssertionError(f"unclosed C# method body: {signature}")


class UnityStaticSortTextSourceContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.editor = EDITOR_SOURCE.read_text(encoding="utf-8")
        cls.runtime = RUNTIME_SOURCE.read_text(encoding="utf-8")

    def test_runtime_identity_keeps_owner_and_asset_refs_without_transient_child(self):
        self.assertIn("public TMP_Text sourceOwner;", self.runtime)
        self.assertIn("public TMP_FontAsset fontAsset;", self.runtime)
        self.assertIn("public TMP_SpriteAsset spriteAsset;", self.runtime)
        self.assertIn("public Material sourceMaterial;", self.runtime)
        self.assertIn("public Material proxyMaterial;", self.runtime)
        self.assertIn("public Material ownerFontSharedMaterial;", self.runtime)
        self.assertIn("public TMP_FontAsset fallbackFontAsset;", self.runtime)
        self.assertIn("public Texture sourceTexture;", self.runtime)
        self.assertNotRegex(self.runtime, r"public\s+string\s+ownerGuid")
        self.assertNotRegex(self.runtime, r"public\s+long\s+ownerLocalFileId")
        self.assertNotRegex(self.runtime, r"public\s+TMP_SubMeshUI\s+\w+")

    def test_main_and_generated_slots_use_typed_tmp_material_and_atlas(self):
        slot = _body(self.editor, "string sourceComponentId, out TextSlotBinding binding")
        self.assertIn("owner.fontSharedMaterial", slot)
        self.assertIn("generated.sharedMaterial", slot)
        self.assertIn("sourceMaterial.GetTexture(MainTex)", slot)
        self.assertNotIn("sourceGraphic.material;", slot)
        self.assertNotIn("sourceGraphic.mainTexture", slot)
        self.assertIn("TryMaterialSlot(generated", slot)
        self.assertIn("ReadTextInfoSlotEvidence(owner, expectedSlot", slot)
        self.assertIn("characterMaterialMatchesSlotInfo", slot)
        self.assertIn("slotInfo.material == null", slot)
        self.assertIn("rendererMaterialMatches", slot)
        self.assertIn("TextureBelongsToSourceAsset", slot)
        self.assertNotIn("AssetIdentity(owner", slot)

    def test_persistent_read_requires_real_asset_identity_and_baked_mesh_hash(self):
        persistent = _body(self.editor, "public static bool ReadPersistent(")
        self.assertIn("TMP_Text expectedOwner", self.editor)
        self.assertIn("string expectedSourceComponentId", self.editor)
        self.assertIn("expectedOwnerGuid", persistent)
        self.assertIn("expectedOwnerLocalFileId", persistent)
        self.assertIn("identity.sourceOwner == expectedOwner", persistent)
        resources = _body(self.editor, "static bool ReadAssetsAndMesh(")
        self.assertIn("SameIdentity(identity.sourceTexture", resources)
        self.assertIn("identity.proxyMaterial.shader", resources)
        self.assertIn("SameIdentity(identity.proxyMaterial", resources)
        self.assertIn("MeshFingerprint(bakedProxyMesh) == identity.proxyMeshSha256", resources)
        self.assertIn("readback.textureVerified", resources)
        self.assertIn("readback.bakedProxyMeshVerified", resources)
        self.assertIn("readback.bakedProxyMaterialFingerprint", resources)
        self.assertIn("readback.ownerFontMaterialVerified", resources)
        self.assertIn("readback.fallbackFontMaterialVerified", resources)

    def test_initialized_read_re_resolves_unique_owner_slot_and_checks_source_mesh(self):
        resolve = _body(self.editor, "TMP_Text expectedOwner,\n            string expectedSourceComponentId, out TextSlotBinding binding")
        initialized = _body(self.editor, "TMP_Text expectedOwner, string expectedSourceComponentId, out TextSourceReadback")
        self.assertIn("GetCurrentSlots(expectedOwner, expectedSourceComponentId", resolve)
        self.assertIn("out var currentEnumeration", resolve)
        self.assertIn("currentEnumeration.evidenceSha256 != binding.textSlotEnumeration.evidenceSha256", resolve)
        self.assertIn("identity.sourceOwner != expectedOwner", resolve)
        self.assertIn("identity.sourceComponentId != expectedSourceComponentId", resolve)
        self.assertIn("currentSlots.SingleOrDefault(candidate => candidate.materialSlot == identity.materialSlot)", resolve)
        self.assertIn("TMP_SORT_GENERATED_SLOT_NOT_UNIQUE", resolve)
        self.assertIn("BindingMatchesIdentity", resolve)
        self.assertIn("identity.sourceOwner == expectedOwner", initialized)
        self.assertIn("identity.sourceComponentId == expectedSourceComponentId", initialized)
        self.assertNotIn("AssetIdentity(expectedOwner", initialized)
        self.assertIn("PrepareSource(expectedOwner", initialized)
        self.assertIn("binding.sourceMeshSha256 == identity.sourceMeshSha256", initialized)

    def test_capture_does_not_pin_scene_owner_as_asset_but_persistent_read_requires_caller_pin(self):
        capture = _body(self.editor, "string sourceComponentId, out TextSlotBinding binding")
        attach = _body(self.editor, "public static NativeStaticSortTextSource Attach(")
        persistent = _body(self.editor, "public static bool ReadPersistent(")
        self.assertNotIn("AssetIdentity(owner", capture)
        self.assertNotIn("ownerGuid", attach)
        self.assertIn("AssetIdentity(expectedOwner", persistent)
        self.assertIn("expectedOwnerGuid", persistent)
        self.assertIn("expectedOwnerLocalFileId", persistent)

    def test_owner_outline_material_is_persisted_only_from_exact_font_asset_derived_style(self):
        capture = _body(self.editor, "public static bool CaptureOwnerFontMaterial(")
        self.assertIn("NativeStaticTextOutline", capture)
        self.assertIn("outline.LastReadback", capture)
        self.assertIn("styleReadback.sourceLabelId != sourceComponentId", capture)
        self.assertNotIn("SerializedObject", capture)
        self.assertIn("outline.Target != owner", capture)
        self.assertIn("sourceFont.material", capture)
        self.assertIn("SourceOutlineWidth", capture)
        self.assertIn("SourceOutlineColor", capture)
        self.assertIn("_GradientScale", capture)
        self.assertIn("expectedFingerprint != liveFingerprint", capture)
        self.assertIn("outline.ConfigureCaptureCandidate(expected, sourceFont, owner.fontSize", capture)
        self.assertIn("TMPro.ShaderUtilities.GetPadding(expected, owner.extraPadding, owner.isUsingBold)", capture)
        self.assertIn("MaterialFingerprintDelta(expected, liveMaterial)", capture)
        self.assertIn(";delta=", capture)
        self.assertIn("AssetDatabase.CreateAsset(expected, persistentAssetPath)", capture)
        self.assertIn("owner.fontSharedMaterial = saved", capture)
        self.assertIn("native-static-text-outline-font-material-v1", capture)
        delta = _body(self.editor, "static string MaterialFingerprintDelta(")
        self.assertIn("GetPropertyType", delta)
        self.assertIn("MaterialPropertyValue", delta)
        self.assertIn("details.Count >= 16", delta)
        self.assertIn("details.Count == 0", delta)
        self.assertIn("MaterialFingerprint(expected)", self.editor)
        self.assertIn("expectedFingerprint != liveFingerprint", capture)
        self.assertNotIn("AssetDatabase.CreateAsset", _body(self.editor, "static bool ReadAssetsAndMesh("))
        self.assertIn("ownerStyleVerified", self.editor)
        self.assertIn("identity.ownerStyleSourceComponentId == identity.sourceComponentId", self.editor)
        self.assertIn("MaterialFingerprint(styleBase) == identity.ownerStyleSourceFontMaterialFingerprint", self.editor)
        self.assertIn("identity.sourceOwner.fontSharedMaterial == identity.ownerFontSharedMaterial", self.editor)
        self.assertIn("public string ownerStyleProfile;", self.runtime)
        self.assertIn("public TMP_FontAsset ownerStyleSourceFontAsset;", self.runtime)
        self.assertIn("public Material ownerStyleSourceFontMaterial;", self.runtime)

    def test_transient_fallback_material_requires_sdk_provenance_and_owned_bake(self):
        capture = _body(self.editor, "public static bool CaptureFallbackMaterial(")
        self.assertIn("TMP_SORT_SLOT_FONT_OR_SPRITE_ASSET_MISSING", self.editor)
        self.assertIn("TMP_SORT_SLOT_ATLAS_DOES_NOT_MATCH_SOURCE_ASSET", self.editor)
        self.assertIn("PersistentAsset(sourceBase", capture)
        self.assertIn("PersistentAsset(fallbackBase", capture)
        self.assertIn("TMP_MaterialManager.GetFallbackMaterial(sourceBase, fallbackBase)", capture)
        self.assertIn("transientFingerprint != sdkFingerprint", capture)
        self.assertIn("MaterialFingerprint(clone) != transientFingerprint", capture)
        self.assertIn("AssetDatabase.CreateAsset(clone, persistentAssetPath)", capture)
        self.assertIn("TMP_SORT_TRANSIENT_MATERIAL_IS_NOT_A_SUPPORTED_TMP_FALLBACK", capture)
        self.assertIn("binding.ownerFontSharedMaterial", capture)
        self.assertIn("binding.fallbackFontMaterial", capture)
        self.assertIn("GetFallbackMaterial", capture)
        self.assertIn("MaterialFingerprint(binding.sourceMaterial)", capture)
        self.assertIn("TMP_SORT_TRANSIENT_FALLBACK_DIFFERS_FROM_PINNED_SDK_OUTPUT", capture)
        self.assertIn("identity.bakedProxyMaterialFingerprint", self.editor)
        persistent = _body(self.editor, "public static bool ReadPersistent(")
        initialized = _body(self.editor, "TMP_Text expectedOwner, string expectedSourceComponentId, out TextSourceReadback")
        self.assertNotIn("AssetDatabase.CreateAsset", persistent)
        self.assertNotIn("AssetDatabase.CreateAsset", initialized)
        self.assertIn("readback.actualTransientMaterialFingerprint == identity.transientFallbackFingerprint", initialized)
        self.assertIn("TMP_SORT_GENERATED_SLOT_NOT_UNIQUE", self.editor)

    def test_registered_fallback_capture_rebind_uses_fresh_slot_and_exact_baked_asset(self):
        enumerate_slots = _body(self.editor, "out List<TextSlotBinding> slots, out NativeStaticSortTextSlotEnumeration enumeration,")
        self.assertIn("owner.GetComponentsInChildren<TMP_SubMeshUI>(true)", enumerate_slots)
        self.assertIn("matches.Length != 1", enumerate_slots)
        self.assertIn("TryResolveSlot(owner, generated, slot", enumerate_slots)
        self.assertIn('"empty-placeholder"', enumerate_slots)
        self.assertIn('"drawable"', enumerate_slots)
        self.assertIn("TextSlotEnumerationHash(enumeration)", enumerate_slots)
        self.assertIn("binding.textSlotEnumeration = enumeration", enumerate_slots)
        rebind = _body(self.editor, "public static bool RebindCapturedSlot(")
        self.assertIn("TryResolveSlot(currentOwner", rebind)
        self.assertIn("current.sourceMeshSha256 != capturedProof.sourceMeshSha256", rebind)
        self.assertIn("current.sourceMaterial != capturedProof.proxyMaterial", rebind)
        self.assertIn("currentGuid != capturedProof.bakedProxyMaterialGuid", rebind)
        self.assertIn("current.tmpFallbackMaterialBaked = capturedProof.tmpFallbackMaterialBaked", rebind)
        self.assertIn("current.sourceMaterialGuid = null", rebind)
        self.assertIn("capturedProof.persistentFallbackVariantRegistered", rebind)
        self.assertIn("TMP_SORT_CAPTURE_REBIND_REGISTERED_FALLBACK_VARIANT_MISMATCH", rebind)
        self.assertIn("TMP_SORT_CAPTURE_REBIND_SDK_TRANSIENT_FALLBACK_PROFILE_MISMATCH", rebind)
        self.assertIn("current.sourceMaterialFingerprint != capturedProof.transientFallbackFingerprint", rebind)
        slot = _body(self.editor, "public static bool TryResolveSlot(")
        self.assertIn(";materialRefEqual=", slot)
        self.assertIn(";rendererMaterial=", slot)
        self.assertIn("ReadTextInfoSlotEvidence(owner, expectedSlot", slot)
        proof = _body(self.editor, "static bool ReadTextInfoSlotEvidence(")
        self.assertIn("character.materialReferenceIndex != materialSlot", proof)
        self.assertIn("character.fontAsset == fontAsset", proof)
        self.assertIn("character.textElement.textAsset", proof)
        self.assertIn("character.alternativeGlyph", proof)
        self.assertIn("fontAsset.atlasTextures[atlasIndex]", proof)
        self.assertIn("spriteAsset.spriteSheet", proof)
        self.assertIn("character.material.GetTexture(MainTex)", proof)
        self.assertIn("character.isVisible", proof)
        persistent = _body(self.editor, "public static bool ReadPersistent(")
        self.assertIn("GetCurrentSlots(expectedOwner", persistent)
        self.assertIn("BindingMatchesIdentity(current, identity)", persistent)
        slots = _body(self.editor, "out List<TextSlotBinding> slots, out NativeStaticSortTextSlotEnumeration enumeration,")
        self.assertIn("visibleTextInfoReferences == 0", slots)
        self.assertIn("MeshHasDrawTriangles(slotMesh)", slots)
        self.assertIn("MeshHasDrawTriangles(rendererMesh)", slots)
        self.assertIn("MeshNonDegenerateTriangleCount", self.editor)
        self.assertIn("MeshGeometryDiagnostic(slotMesh)", slots)
        self.assertIn("MeshGeometryDiagnostic(rendererMesh)", slots)
        self.assertIn("TMP_SORT_UNREFERENCED_TEXTINFO_SLOT_HAS_RENDERED_MESH", slots)
        self.assertIn("HashText(owner.text ?? String.Empty)", slot)
        self.assertIn("HashText(identity.sourceOwner.text ?? String.Empty) == identity.sourceTextSha256", self.editor)
        matches = _body(self.editor, "static bool BindingMatchesIdentity(")
        self.assertIn("identity.tmpFallbackMaterialBaked", matches)
        self.assertIn("identity.persistentFallbackVariantRegistered", matches)
        self.assertIn("binding.sourceMaterial == identity.proxyMaterial", matches)
        self.assertIn("currentSourceGuid == identity.bakedProxyMaterialGuid", matches)
        self.assertIn("binding.sourceMaterialFingerprint == identity.transientFallbackFingerprint", matches)
        self.assertIn("!PersistentAsset(binding.sourceMaterial", matches)
        self.assertIn("identity.persistentFallbackVariantRegistered == hasOutlineSuffix", self.editor)

    def test_empty_owner_enumeration_has_typed_persistent_identity_and_recomputed_readback(self):
        attach = _body(self.editor, "public static bool AttachEmptyTextSlotEnumeration(")
        read = _body(self.editor, "public static bool ReadEmptyTextSlotEnumerationIdentity(")
        self.assertIn("EnumerationIsPlaceholderOnly(enumeration)", attach)
        self.assertIn("NativeStaticSortTextSlotEnumerationIdentity", attach)
        self.assertIn("identity.sourceOwner == expectedOwner", read)
        self.assertIn("identity.sourceComponentId == expectedSourceComponentId", read)
        self.assertIn("!readback.ownerScopeVerified", read)
        self.assertIn("GetCurrentSlots(expectedOwner", read)
        self.assertIn("currentEnumeration.evidenceSha256 == identity.slotEnumeration.evidenceSha256", read)
        self.assertIn("EnumerationIsPlaceholderOnly(currentEnumeration)", read)

    def test_public_module_is_neutral_and_has_the_requested_capture_contract(self):
        all_source = self.editor + self.runtime
        self.assertIn("TryGetMaterialSlot(", self.editor)
        self.assertIn("PrepareSource(", self.editor)
        self.assertIn("Attach(", self.editor)
        self.assertIn("ReadPersistent(", self.editor)
        self.assertIn("ResolveGeneratedSlot(", self.editor)
        self.assertIn("ReadInitialized(", self.editor)
        self.assertNotRegex(all_source, r"\.private/|ThirtySamples|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}")


if __name__ == "__main__":
    unittest.main()
