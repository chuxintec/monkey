using System;
using TMPro;
using UnityEngine;

namespace Monkey.StaticSortQueueProxy
{
    [Serializable]
    public sealed class NativeStaticSortTextSlotEvidence
    {
        public int slot;
        public int characterReferences;
        public int visibleCharacterReferences;
        public bool textInfoMaterialMissing;
        public int textInfoVertexCount;
        public uint textInfoTriangleIndexCount;
        public int textInfoNondegenerateTriangleCount;
        public int canvasVertexCount;
        public uint canvasTriangleIndexCount;
        public int canvasNondegenerateTriangleCount;
        public string disposition;
        public string sourceAssetKind;
        public string sourceAssetGuid;
        public long sourceAssetLocalFileId;
        public string atlasGuid;
        public long atlasLocalFileId;
        public string textInfoMaterialFingerprint;
        public string sourceGraphicMaterialFingerprint;
        public string characterEvidenceSha256;
        public string evidenceSha256;
    }

    [Serializable]
    public sealed class NativeStaticSortTextSlotEnumeration
    {
        public string sourceComponentId;
        public string sourceTextSha256;
        public int slotCount;
        public bool verified;
        public string evidenceSha256;
        public NativeStaticSortTextSlotEvidence[] rows;
    }

    /// <summary>
    /// Persistent identity for one TextMeshPro material/mesh slot used by a
    /// static sort-queue proxy. Generated TMP_SubMeshUI objects are deliberately
    /// not serialized here: TMP creates them from the persistent owner.
    /// </summary>
    [AddComponentMenu("")]
    [DisallowMultipleComponent]
    public sealed class NativeStaticSortTextSource : MonoBehaviour
    {
        public string sourceComponentId;
        public TMP_Text sourceOwner;
        public int materialSlot;
        public bool generatedSubmesh;
        public bool sourceGraphicEnabled;
        public bool sourceGraphicActiveSelf;
        public NativeStaticSortTextSlotEnumeration textSlotEnumeration;
        public bool textInfoMaterialMissing;
        public bool textInfoCharacterSlotVerified;
        public bool textInfoCharacterMaterialVerified;
        public bool textInfoFontAssetVerified;
        public bool textInfoAtlasVerified;
        public int textInfoCharacterCount;
        public int textInfoVisibleCharacterCount;
        public string sourceTextSha256;
        public string textInfoCharacterEvidenceSha256;
        public string textInfoCharacterMaterialFingerprint;

        public TMP_FontAsset fontAsset;
        public TMP_SpriteAsset spriteAsset;
        public Material ownerFontSharedMaterial;
        public TMP_FontAsset fallbackFontAsset;
        public Material fallbackFontMaterial;
        public Material sourceMaterial;
        public Material proxyMaterial;
        public Texture sourceTexture;

        public bool tmpFallbackMaterialBaked;
        public bool persistentFallbackVariantRegistered;
        public string tmpFallbackAlgorithm;
        public int tmpFallbackAtlasIndex;
        public string ownerFontMaterialGuid;
        public long ownerFontMaterialLocalFileId;
        public string ownerFontMaterialFingerprint;
        public string ownerStyleProfile;
        public string ownerStyleSourceComponentId;
        public float ownerStyleOutlineWidth;
        public Color ownerStyleOutlineColor;
        public TMP_FontAsset ownerStyleSourceFontAsset;
        public string ownerStyleSourceFontAssetGuid;
        public long ownerStyleSourceFontAssetLocalFileId;
        public Material ownerStyleSourceFontMaterial;
        public string ownerStyleSourceFontMaterialGuid;
        public long ownerStyleSourceFontMaterialLocalFileId;
        public string ownerStyleSourceFontMaterialFingerprint;
        public string fallbackFontAssetGuid;
        public long fallbackFontAssetLocalFileId;
        public string fallbackFontMaterialGuid;
        public long fallbackFontMaterialLocalFileId;
        public string fallbackFontMaterialFingerprint;
        public string fallbackAtlasGuid;
        public long fallbackAtlasLocalFileId;
        public string transientFallbackFingerprint;
        public string bakedProxyMaterialFingerprint;
        public string bakedProxyMaterialGuid;
        public long bakedProxyMaterialLocalFileId;

        public string fontAssetGuid;
        public long fontAssetLocalFileId;
        public string spriteAssetGuid;
        public long spriteAssetLocalFileId;
        public string sourceMaterialGuid;
        public long sourceMaterialLocalFileId;
        public string sourceMaterialFingerprint;
        public string sourceShaderGuid;
        public long sourceShaderLocalFileId;
        public string sourceTextureGuid;
        public long sourceTextureLocalFileId;

        public string sourceMeshSha256;
        public string proxyMeshGuid;
        public long proxyMeshLocalFileId;
        public string proxyMeshSha256;
    }

    /// <summary>Typed owner-level TMP slot evidence for text whose complete material-slot set draws no proxy geometry.</summary>
    [AddComponentMenu("")]
    [DisallowMultipleComponent]
    public sealed class NativeStaticSortTextSlotEnumerationIdentity : MonoBehaviour
    {
        public TMP_Text sourceOwner;
        public string sourceComponentId;
        public NativeStaticSortTextSlotEnumeration slotEnumeration;
    }
}
