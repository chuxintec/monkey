using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using TMPro;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace Monkey.StaticSortQueueProxy
{
    /// <summary>A live, non-serialized binding to one exact TMP material slot.</summary>
    public sealed class TextSlotBinding
    {
        public string sourceComponentId;
        public TMP_Text owner;
        public Graphic sourceGraphic;
        public Mesh sourceMesh;
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
        public string fontAssetGuid;
        public long fontAssetLocalFileId;
        public string spriteAssetGuid;
        public long spriteAssetLocalFileId;
        public string sourceMaterialGuid;
        public long sourceMaterialLocalFileId;
        public string sourceShaderGuid;
        public long sourceShaderLocalFileId;
        public string sourceTextureGuid;
        public long sourceTextureLocalFileId;
        public string sourceMeshSha256;
        public bool tmpFallbackMaterialBaked;
        public bool persistentFallbackVariantRegistered;
        public string tmpFallbackAlgorithm;
        public int tmpFallbackAtlasIndex;
        public string ownerFontMaterialGuid;
        public long ownerFontMaterialLocalFileId;
        public string ownerFontMaterialFingerprint;
        public OwnerFontStyleDescriptor ownerStyle;
        public string fallbackFontAssetGuid;
        public long fallbackFontAssetLocalFileId;
        public string fallbackFontMaterialGuid;
        public long fallbackFontMaterialLocalFileId;
        public string fallbackFontMaterialFingerprint;
        public string fallbackAtlasGuid;
        public long fallbackAtlasLocalFileId;
        public string transientFallbackFingerprint;
        public string sourceMaterialFingerprint;
        public string proxyMaterialFingerprint;
        public string proxyMaterialGuid;
        public long proxyMaterialLocalFileId;
        public string bakedProxyMaterialFingerprint;
        public string bakedProxyMaterialGuid;
        public long bakedProxyMaterialLocalFileId;
    }

    [Serializable]
    public sealed class TextSourceReadback
    {
        public string sourceComponentId, diagnostic;
        public int materialSlot;
        public bool ownerScopeVerified, persistentReferencesVerified, generatedSlotResolved, sourceStateVerified;
        public bool fontAssetVerified, spriteAssetVerified, materialVerified, shaderVerified, textureVerified;
        public bool tmpFallbackDescriptorVerified, ownerFontMaterialVerified, fallbackFontAssetVerified;
        public bool persistentFallbackVariantRegistered;
        public bool fallbackFontMaterialVerified, fallbackAtlasVerified, transientFallbackVerified, proxyMaterialVerified;
        public bool bakedProxyMeshVerified, sourceMeshVerified, verified;
        public NativeStaticSortTextSlotEnumeration textSlotEnumeration;
        public NativeStaticSortTextSlotEnumeration currentTextSlotEnumeration;
        public bool textInfoMaterialMissing, textInfoCharacterSlotVerified, textInfoCharacterMaterialVerified;
        public bool textInfoFontAssetVerified, textInfoAtlasVerified;
        public int textInfoCharacterCount, textInfoVisibleCharacterCount;
        public string sourceTextSha256;
        public string ownerGuid, fontAssetGuid, spriteAssetGuid, materialGuid, shaderGuid, textureGuid, proxyMaterialGuid,
            ownerFontMaterialGuid, fallbackFontAssetGuid, fallbackFontMaterialGuid, fallbackAtlasGuid;
        public long ownerLocalFileId, fontAssetLocalFileId, spriteAssetLocalFileId, materialLocalFileId,
            shaderLocalFileId, textureLocalFileId, proxyMeshLocalFileId, proxyMaterialLocalFileId,
            ownerFontMaterialLocalFileId, fallbackFontAssetLocalFileId, fallbackFontMaterialLocalFileId,
            fallbackAtlasLocalFileId;
        public string sourceMeshSha256, proxyMeshGuid, proxyMeshSha256, tmpFallbackAlgorithm,
            transientFallbackFingerprint, actualTransientMaterialFingerprint, sourceMaterialFingerprint,
            ownerFontMaterialFingerprint, fallbackFontMaterialFingerprint, bakedProxyMaterialFingerprint,
            textInfoCharacterEvidenceSha256, textInfoCharacterMaterialFingerprint,
            ownerStyleProfile, ownerStyleSourceComponentId, ownerStyleSourceFontAssetGuid,
            ownerStyleSourceFontMaterialGuid, ownerStyleSourceFontMaterialFingerprint;
        public long ownerStyleSourceFontAssetLocalFileId, ownerStyleSourceFontMaterialLocalFileId;
        public float ownerStyleOutlineWidth;
        public Color ownerStyleOutlineColor;
        public bool ownerStyleVerified;
    }

    [Serializable]
    public sealed class TextSlotEnumerationReadback
    {
        public string sourceComponentId, diagnostic;
        public bool ownerScopeVerified, persistentReferencesVerified, verified;
        public NativeStaticSortTextSlotEnumeration slotEnumeration;
        public NativeStaticSortTextSlotEnumeration currentSlotEnumeration;
    }

    [Serializable]
    public sealed class OwnerFontStyleDescriptor
    {
        public string profile;
        public string sourceComponentId;
        public float outlineWidth;
        public Color outlineColor;
        public TMP_FontAsset sourceFontAsset;
        public string sourceFontAssetGuid;
        public long sourceFontAssetLocalFileId;
        public Material sourceFontMaterial;
        public string sourceFontMaterialGuid;
        public long sourceFontMaterialLocalFileId;
        public string sourceFontMaterialFingerprint;
    }

    /// <summary>
    /// Exact TMP material/atlas capture and strict post-save resolution for
    /// static sort-queue proxies. This class never substitutes a white texture,
    /// manufactures a TMP material, or retains a generated submesh object in a
    /// serialized identity.
    /// </summary>
    public static class UnityStaticSortTextSource
    {
        const string MainTex = "_MainTex";
        static readonly FieldInfo MaterialSlotField = typeof(TMP_SubMeshUI).GetField(
            "m_materialReferenceIndex", BindingFlags.Instance | BindingFlags.NonPublic);
        static readonly MethodInfo MultiAtlasFallbackMethod = typeof(TMP_MaterialManager).GetMethod(
            "GetFallbackMaterial", BindingFlags.Static | BindingFlags.NonPublic, null,
            new[] { typeof(TMP_FontAsset), typeof(Material), typeof(int) }, null);

        static string HashText(string value)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(Encoding.UTF8.GetBytes(value ?? "")))
                    .Replace("-", "").ToLowerInvariant();
        }

        static string MaterialFingerprint(Material material)
        {
            if (material == null || material.shader == null) return null;
            if (!PersistentAsset(material.shader, out var shaderGuid, out var shaderFileId)) return null;
            var shader = material.shader;
            var sb = new StringBuilder();
            sb.Append("shader=").Append(shaderGuid).Append(':').Append(shaderFileId)
              .Append("|queue=").Append(material.renderQueue)
              .Append("|instancing=").Append(material.enableInstancing)
              .Append("|doubleSidedGI=").Append(material.doubleSidedGI)
              .Append("|giFlags=").Append((int)material.globalIlluminationFlags)
              .Append("|keywords=").Append(string.Join(",", material.shaderKeywords.OrderBy(value => value, StringComparer.Ordinal)));
            for (var index = 0; index < shader.GetPropertyCount(); index++)
            {
                var name = shader.GetPropertyName(index);
                var type = shader.GetPropertyType(index);
                sb.Append("|p=").Append(name).Append(':').Append(type).Append('=');
                if (type == UnityEngine.Rendering.ShaderPropertyType.Color)
                {
                    var value = material.GetColor(name);
                    sb.Append(value.r.ToString("R", System.Globalization.CultureInfo.InvariantCulture)).Append(',')
                      .Append(value.g.ToString("R", System.Globalization.CultureInfo.InvariantCulture)).Append(',')
                      .Append(value.b.ToString("R", System.Globalization.CultureInfo.InvariantCulture)).Append(',')
                      .Append(value.a.ToString("R", System.Globalization.CultureInfo.InvariantCulture));
                }
                else if (type == UnityEngine.Rendering.ShaderPropertyType.Vector)
                    AppendVector(sb, material.GetVector(name));
                else if (type == UnityEngine.Rendering.ShaderPropertyType.Texture)
                {
                    var texture = material.GetTexture(name);
                    if (texture == null) sb.Append("null");
                    else if (texture == Texture2D.whiteTexture) sb.Append("builtin:white");
                    else if (AssetIdentity(texture, out var textureGuid, out var textureFileId))
                        sb.Append(textureGuid).Append(':').Append(textureFileId);
                    else return null;
                    var scale = material.GetTextureScale(name); var offset = material.GetTextureOffset(name);
                    sb.Append(";scale=").Append(scale.x.ToString("R", System.Globalization.CultureInfo.InvariantCulture)).Append(',')
                      .Append(scale.y.ToString("R", System.Globalization.CultureInfo.InvariantCulture))
                      .Append(";offset=").Append(offset.x.ToString("R", System.Globalization.CultureInfo.InvariantCulture)).Append(',')
                      .Append(offset.y.ToString("R", System.Globalization.CultureInfo.InvariantCulture));
                }
                else if (type == UnityEngine.Rendering.ShaderPropertyType.Int)
                    sb.Append(material.GetInt(name));
                else
                    sb.Append(material.GetFloat(name).ToString("R", System.Globalization.CultureInfo.InvariantCulture));
            }
            return HashText(sb.ToString());
        }

        static string MaterialFingerprintDelta(Material expected, Material actual)
        {
            var details = new List<string>();
            if (expected == null || actual == null)
                return "expected=" + (expected == null ? "null" : "present") + ";actual=" + (actual == null ? "null" : "present");
            var expectedShader = expected.shader;
            var actualShader = actual.shader;
            if (expectedShader == null || actualShader == null || expectedShader != actualShader)
                details.Add("shader=" + ObjectIdentitySummary(expectedShader) + "->" + ObjectIdentitySummary(actualShader));
            if (expected.renderQueue != actual.renderQueue) details.Add("renderQueue=" + expected.renderQueue + "->" + actual.renderQueue);
            if (expected.enableInstancing != actual.enableInstancing) details.Add("instancing=" + expected.enableInstancing + "->" + actual.enableInstancing);
            if (expected.doubleSidedGI != actual.doubleSidedGI) details.Add("doubleSidedGI=" + expected.doubleSidedGI + "->" + actual.doubleSidedGI);
            if (expected.globalIlluminationFlags != actual.globalIlluminationFlags)
                details.Add("giFlags=" + expected.globalIlluminationFlags + "->" + actual.globalIlluminationFlags);
            var expectedKeywords = String.Join(",", expected.shaderKeywords.OrderBy(value => value, StringComparer.Ordinal));
            var actualKeywords = String.Join(",", actual.shaderKeywords.OrderBy(value => value, StringComparer.Ordinal));
            if (expectedKeywords != actualKeywords) details.Add("keywords=" + Clip(expectedKeywords) + "->" + Clip(actualKeywords));
            if (expectedShader != null && actualShader != null && expectedShader == actualShader)
            {
                var count = expectedShader.GetPropertyCount();
                for (var index = 0; index < count; index++)
                {
                    var name = expectedShader.GetPropertyName(index);
                    var type = expectedShader.GetPropertyType(index);
                    var left = MaterialPropertyValue(expected, name, type);
                    var right = MaterialPropertyValue(actual, name, type);
                    if (left == right) continue;
                    details.Add(name + "=" + Clip(left) + "->" + Clip(right));
                    if (details.Count >= 16) break;
                }
            }
            if (details.Count == 0) return "no-visible-property-delta;fingerprintNullExpected=" + (MaterialFingerprint(expected) == null) +
                ";fingerprintNullActual=" + (MaterialFingerprint(actual) == null);
            return String.Join("|", details) + (details.Count >= 16 ? "|truncated=true" : "");
        }

        static string MaterialPropertyValue(Material material, string name, UnityEngine.Rendering.ShaderPropertyType type)
        {
            if (type == UnityEngine.Rendering.ShaderPropertyType.Color)
            {
                var value = material.GetColor(name);
                return value.r.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "," +
                    value.g.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "," +
                    value.b.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "," +
                    value.a.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
            }
            if (type == UnityEngine.Rendering.ShaderPropertyType.Vector)
            {
                var value = material.GetVector(name);
                return value.x.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "," +
                    value.y.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "," +
                    value.z.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "," +
                    value.w.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
            }
            if (type == UnityEngine.Rendering.ShaderPropertyType.Texture)
            {
                var texture = material.GetTexture(name);
                var scale = material.GetTextureScale(name); var offset = material.GetTextureOffset(name);
                return ObjectIdentitySummary(texture) + ";scale=" + scale.x.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "," +
                    scale.y.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + ";offset=" +
                    offset.x.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "," +
                    offset.y.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
            }
            return type == UnityEngine.Rendering.ShaderPropertyType.Int
                ? material.GetInt(name).ToString(System.Globalization.CultureInfo.InvariantCulture)
                : material.GetFloat(name).ToString("R", System.Globalization.CultureInfo.InvariantCulture);
        }

        static string ObjectIdentitySummary(UnityEngine.Object value)
        {
            if (value == null) return "null";
            if (AssetIdentity(value, out var guid, out var fileId)) return guid + ":" + fileId;
            return "unpersisted:" + value.GetType().Name + ":" + Clip(value.name);
        }

        static string Clip(string value)
        {
            if (String.IsNullOrEmpty(value)) return value ?? "";
            return value.Length <= 96 ? value : value.Substring(0, 93) + "...";
        }

        static void AppendVector(StringBuilder sb, Vector4 value)
        {
            sb.Append(value.x.ToString("R", System.Globalization.CultureInfo.InvariantCulture)).Append(',')
              .Append(value.y.ToString("R", System.Globalization.CultureInfo.InvariantCulture)).Append(',')
              .Append(value.z.ToString("R", System.Globalization.CultureInfo.InvariantCulture)).Append(',')
              .Append(value.w.ToString("R", System.Globalization.CultureInfo.InvariantCulture)).Append(';');
        }

        static int UvDimension(Mesh mesh, int channel)
        {
            if (mesh == null || channel < 0 || channel > 7) return 0;
            var attribute = (UnityEngine.Rendering.VertexAttribute)((int)UnityEngine.Rendering.VertexAttribute.TexCoord0 + channel);
            return mesh.HasVertexAttribute(attribute) ? mesh.GetVertexAttributeDimension(attribute) : 0;
        }

        /// <summary>Fingerprint compatible with the sort-proxy source mesh contract.</summary>
        public static string MeshFingerprint(Mesh mesh, int submesh = 0)
        {
            if (mesh == null || submesh < 0 || submesh >= mesh.subMeshCount) return null;
            var sb = new StringBuilder();
            sb.Append(mesh.vertexCount).Append('|').Append(mesh.subMeshCount).Append('|').Append(submesh).Append('|');
            foreach (var point in mesh.vertices) AppendVector(sb, point);
            foreach (var color in mesh.colors32) sb.Append(color.r).Append(',').Append(color.g).Append(',')
                .Append(color.b).Append(',').Append(color.a).Append(';');
            for (var channel = 0; channel < 8; channel++)
            {
                var values = new List<Vector4>(); mesh.GetUVs(channel, values);
                sb.Append('#').Append(channel).Append('/').Append(UvDimension(mesh, channel)).Append(':');
                foreach (var uv in values) AppendVector(sb, uv);
            }
            foreach (var normal in mesh.normals) AppendVector(sb, normal);
            foreach (var tangent in mesh.tangents) AppendVector(sb, tangent);
            foreach (var index in mesh.GetTriangles(submesh)) sb.Append(index).Append(',');
            return HashText(sb.ToString());
        }

        static bool AssetIdentity(UnityEngine.Object value, out string guid, out long localFileId)
        {
            guid = null; localFileId = 0;
            return value != null && AssetDatabase.TryGetGUIDAndLocalFileIdentifier(value, out guid, out localFileId) &&
                !String.IsNullOrWhiteSpace(guid) && localFileId != 0;
        }

        static bool SameIdentity(UnityEngine.Object value, string expectedGuid, long expectedLocalFileId,
            out string actualGuid, out long actualLocalFileId)
        {
            return AssetIdentity(value, out actualGuid, out actualLocalFileId) &&
                actualGuid == expectedGuid && actualLocalFileId == expectedLocalFileId;
        }

        static bool TryMaterialSlot(TMP_SubMeshUI generated, out int slot)
        {
            slot = -1;
            if (generated == null || MaterialSlotField == null) return false;
            var value = MaterialSlotField.GetValue(generated);
            if (!(value is int index) || index <= 0) return false;
            slot = index;
            return true;
        }

        static int MeshNonDegenerateTriangleCount(Mesh mesh)
        {
            if (mesh == null) return 0;
            try
            {
                var vertices = mesh.vertices;
                var count = 0;
                for (var submesh = 0; submesh < mesh.subMeshCount; submesh++)
                {
                    var indices = mesh.GetTriangles(submesh);
                    for (var index = 0; index + 2 < indices.Length; index += 3)
                    {
                        var a = indices[index]; var b = indices[index + 1]; var c = indices[index + 2];
                        if (a < 0 || b < 0 || c < 0 || a >= vertices.Length || b >= vertices.Length || c >= vertices.Length)
                            return Int32.MaxValue;
                        if (Vector3.Cross(vertices[b] - vertices[a], vertices[c] - vertices[a]).sqrMagnitude > 1e-12f)
                            count++;
                    }
                }
                return count;
            }
            catch { return Int32.MaxValue; }
        }

        static uint MeshFirstSubmeshIndexCount(Mesh mesh)
        {
            return mesh != null && mesh.subMeshCount > 0 ? mesh.GetIndexCount(0) : 0;
        }

        static uint MeshTotalIndexCount(Mesh mesh)
        {
            if (mesh == null) return 0;
            ulong count = 0;
            for (var submesh = 0; submesh < mesh.subMeshCount; submesh++) count += mesh.GetIndexCount(submesh);
            return count > UInt32.MaxValue ? UInt32.MaxValue : (uint)count;
        }

        static bool MeshHasDrawTriangles(Mesh mesh)
        {
            return MeshNonDegenerateTriangleCount(mesh) > 0;
        }

        static string MeshGeometryDiagnostic(Mesh mesh)
        {
            if (mesh == null) return "null";
            try
            {
                var vertices = mesh.vertices;
                var indices = mesh.triangles;
                var colors = mesh.colors32;
                var vertexSummary = String.Join(",", Enumerable.Range(0, Math.Min(4, vertices.Length)).Select(index =>
                    vertices[index].x.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "/" +
                    vertices[index].y.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "/" +
                    vertices[index].z.ToString("R", System.Globalization.CultureInfo.InvariantCulture) +
                    (colors.Length == vertices.Length ? "/a" + colors[index].a : "")));
                var indexSummary = String.Join(",", indices.Take(6));
                return "vertices=" + mesh.vertexCount + ";indices=" + indices.Length +
                    ";nondegenerateTriangles=" + MeshNonDegenerateTriangleCount(mesh) +
                    ";bounds=" + mesh.bounds.size.x.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "/" +
                    mesh.bounds.size.y.ToString("R", System.Globalization.CultureInfo.InvariantCulture) + "/" +
                    mesh.bounds.size.z.ToString("R", System.Globalization.CultureInfo.InvariantCulture) +
                    ";firstVertices=" + vertexSummary + ";firstIndices=" + indexSummary;
            }
            catch (Exception error) { return "diagnostic_failed:" + error.GetType().Name; }
        }

        /// <summary>Resolve a Graphic captured by TMP owner to its owner-wide material slot.</summary>
        public static bool TryGetMaterialSlot(TMP_Text owner, Graphic sourceGraphic, out int materialSlot,
            out string diagnostic)
        {
            materialSlot = -1; diagnostic = null;
            if (owner == null || sourceGraphic == null) return Fail("TMP_SORT_GRAPHIC_SLOT_OWNER_MISSING", out diagnostic);
            if (sourceGraphic == (Graphic)owner)
            {
                materialSlot = 0;
                return true;
            }
            if (sourceGraphic is TMP_SubMeshUI generated && generated.textComponent == owner &&
                TryMaterialSlot(generated, out materialSlot)) return true;
            materialSlot = -1;
            return Fail("TMP_SORT_GRAPHIC_SLOT_IS_NOT_OWNED_BY_TEXT:" + sourceGraphic.GetType().FullName, out diagnostic);
        }

        static bool PersistentAsset(UnityEngine.Object value, out string guid, out long localFileId)
        {
            return AssetIdentity(value, out guid, out localFileId) &&
                !String.IsNullOrWhiteSpace(AssetDatabase.GetAssetPath(value));
        }

        static bool TextureBelongsToSourceAsset(TMP_FontAsset font, TMP_SpriteAsset sprite, Texture texture)
        {
            if (texture == null) return false;
            var fontOwnsTexture = font != null && font.atlasTextures != null && font.atlasTextures.Any(atlas => atlas == texture);
            var spriteOwnsTexture = sprite != null && sprite.spriteSheet == texture;
            return fontOwnsTexture || spriteOwnsTexture;
        }

        public static bool PrepareSource(TMP_Text owner, string sourceComponentId, out string diagnostic)
        {
            diagnostic = null;
            if (owner == null || String.IsNullOrWhiteSpace(sourceComponentId))
                return Fail("TMP_SORT_SOURCE_OWNER_OR_ID_MISSING", out diagnostic);
            if (!(owner is TextMeshProUGUI))
                return Fail("TMP_SORT_SOURCE_OWNER_TYPE_UNSUPPORTED", out diagnostic);
            try { owner.ForceMeshUpdate(true, true); }
            catch (Exception error) { return Fail("TMP_SORT_SOURCE_MESH_PREPARE_FAILED:" + error.GetType().Name, out diagnostic); }
            var info = owner.textInfo;
            if (info == null || info.materialCount <= 0 || info.meshInfo == null || info.meshInfo.Length < info.materialCount)
                return Fail("TMP_SORT_SOURCE_TEXTINFO_SLOTS_UNAVAILABLE", out diagnostic);
            for (var slot = 0; slot < info.materialCount; slot++)
                if (info.meshInfo[slot].mesh == null || info.meshInfo[slot].material == null)
                    return Fail("TMP_SORT_SOURCE_SLOT_INCOMPLETE:" + slot, out diagnostic);
            return true;
        }

        static bool ReadTextInfoSlotEvidence(TMP_Text owner, int materialSlot, TMP_FontAsset fontAsset,
            TMP_SpriteAsset spriteAsset, Material graphicMaterial, Material textInfoMaterial,
            out int characterCount, out int visibleCharacterCount, out string evidenceSha256,
            out string characterMaterialFingerprint, out string diagnostic)
        {
            characterCount = 0; visibleCharacterCount = 0; evidenceSha256 = null;
            characterMaterialFingerprint = null; diagnostic = null;
            var info = owner == null ? null : owner.textInfo;
            if (info == null || info.characterInfo == null || graphicMaterial == null)
                return Fail("TMP_SORT_TEXTINFO_SLOT_EVIDENCE_INPUT_MISSING", out diagnostic);
            var graphicTexture = graphicMaterial.GetTexture(MainTex);
            var graphicMaterialFingerprint = MaterialFingerprint(graphicMaterial);
            var evidence = new StringBuilder();
            var characterFingerprints = new SortedSet<string>(StringComparer.Ordinal);
            var firstCharacterMaterialFingerprint = (string)null;
            bool fontVerified = true, atlasVerified = true, materialVerified = true;
            int visible = 0;
            for (var index = 0; index < info.characterCount; index++)
            {
                var character = info.characterInfo[index];
                if (character.materialReferenceIndex != materialSlot) continue;
                characterCount++;
                var isSpriteCharacter = character.elementType == TMP_TextElementType.Sprite;
                var expectedAsset = isSpriteCharacter ? (UnityEngine.Object)spriteAsset : fontAsset;
                var characterAsset = character.textElement == null ? null : character.textElement.textAsset;
                var typedAssetMatches = expectedAsset != null && characterAsset == expectedAsset &&
                    (isSpriteCharacter ? spriteAsset != null : fontAsset != null && character.fontAsset == fontAsset);
                fontVerified &= typedAssetMatches;
                int atlasIndex = -1;
                Texture characterAtlas = null;
                if (character.textElement != null && character.textElement.glyph != null)
                    atlasIndex = character.alternativeGlyph != null
                        ? character.alternativeGlyph.atlasIndex : character.textElement.glyph.atlasIndex;
                if (isSpriteCharacter && spriteAsset != null)
                {
                    characterAtlas = spriteAsset.spriteSheet;
                    atlasIndex = 0;
                }
                else if (fontAsset != null && fontAsset.atlasTextures != null && atlasIndex >= 0 &&
                         atlasIndex < fontAsset.atlasTextures.Length)
                    characterAtlas = fontAsset.atlasTextures[atlasIndex];
                if (character.isVisible) atlasVerified &= characterAtlas != null && characterAtlas == graphicTexture;

                string perCharacterMaterialFingerprint = null;
                if (character.material != null)
                {
                    perCharacterMaterialFingerprint = MaterialFingerprint(character.material);
                    if (String.IsNullOrEmpty(perCharacterMaterialFingerprint) ||
                        character.material.shader != graphicMaterial.shader ||
                        character.isVisible && character.material.GetTexture(MainTex) != characterAtlas)
                        materialVerified = false;
                    if (owner.GetComponent<NativeStaticTextOutline>() == null &&
                        perCharacterMaterialFingerprint != graphicMaterialFingerprint)
                        materialVerified = false;
                    if (textInfoMaterial != null && MaterialFingerprint(textInfoMaterial) != perCharacterMaterialFingerprint)
                        materialVerified = false;
                    if (firstCharacterMaterialFingerprint == null) firstCharacterMaterialFingerprint = perCharacterMaterialFingerprint;
                    else if (firstCharacterMaterialFingerprint != perCharacterMaterialFingerprint) materialVerified = false;
                    if (!String.IsNullOrEmpty(perCharacterMaterialFingerprint)) characterFingerprints.Add(perCharacterMaterialFingerprint);
                }
                else if (character.isVisible) materialVerified = false;

                if (character.isVisible) visible++;
                uint unicode = character.textElement == null ? character.character : character.textElement.unicode;
                evidence.Append(index).Append(':').Append(unicode).Append(':').Append(character.materialReferenceIndex).Append(':')
                    .Append(isSpriteCharacter ? "sprite" : "font").Append(':')
                    .Append(AssetIdentity(expectedAsset, out var assetGuid, out var assetFileId) ? assetGuid + ":" + assetFileId : "missing-asset-id")
                    .Append(':').Append(atlasIndex).Append(':')
                    .Append(AssetIdentity(characterAtlas, out var atlasGuid, out var atlasFileId) ? atlasGuid + ":" + atlasFileId : "missing-atlas-id")
                    .Append(':').Append(perCharacterMaterialFingerprint ?? "missing-character-material").Append(';');
            }
            visibleCharacterCount = visible;
            if (characterCount == 0 || visibleCharacterCount == 0)
                return Fail("TMP_SORT_TEXTINFO_SLOT_HAS_NO_VISIBLE_CHARACTER_REFERENCES:" + materialSlot +
                    ":characters=" + characterCount + ":visible=" + visibleCharacterCount, out diagnostic);
            if (!fontVerified || !atlasVerified || !materialVerified || String.IsNullOrEmpty(graphicMaterialFingerprint))
                return Fail("TMP_SORT_TEXTINFO_SLOT_CHARACTER_ASSET_MATERIAL_OR_ATLAS_CONFLICT:" + materialSlot +
                    ":font=" + fontVerified + ":atlas=" + atlasVerified + ":characterMaterial=" + materialVerified +
                    ":sourceMaterial=" + (graphicMaterialFingerprint ?? "missing"), out diagnostic);
            characterMaterialFingerprint = firstCharacterMaterialFingerprint;
            evidenceSha256 = HashText(evidence.ToString());
            return !String.IsNullOrEmpty(evidenceSha256) || Fail("TMP_SORT_TEXTINFO_SLOT_EVIDENCE_HASH_MISSING", out diagnostic);
        }

        /// <summary>
        /// Capture-only persistence for the material instance produced by the
        /// pinned NativeStaticTextOutline/TMP path. The live material is accepted
        /// only when its complete shader/property fingerprint equals a fresh
        /// derivation from the owner's persistent FontAsset material and the
        /// exact serialized outline component bound to this source ID.
        /// </summary>
        public static bool CaptureOwnerFontMaterial(TMP_Text owner, string sourceComponentId,
            string persistentAssetPath, out Material persistentMaterial,
            out OwnerFontStyleDescriptor descriptor, out string diagnostic)
        {
            persistentMaterial = null; descriptor = null; diagnostic = null;
            if (owner == null || !(owner is TextMeshProUGUI) || String.IsNullOrWhiteSpace(sourceComponentId) || owner.font == null)
                return Fail("TMP_SORT_OWNER_STYLE_INPUT_INCOMPLETE", out diagnostic);
            var outline = owner.GetComponent<NativeStaticTextOutline>();
            if (outline == null || outline.Target != owner)
                return Fail("TMP_SORT_OWNER_STYLE_COMPONENT_NOT_BOUND", out diagnostic);
            // Capture-time only: bind the source-declared style result to the
            // caller's exact owner/source ID. diagnosticSourceLabelId is
            // intentionally nonserialized and is never used as saved readback
            // evidence; persistent/loaded checks bind Native identity through
            // the caller's sourceNodes map and expected sourceComponentId.
            var styleReadback = outline.LastReadback;
            if (styleReadback == null || styleReadback.sourceLabelId != sourceComponentId)
                return Fail("TMP_SORT_OWNER_STYLE_SOURCE_COMPONENT_ID_MISMATCH", out diagnostic);
            var sourceFont = owner.font;
            var sourceMaterial = sourceFont.material;
            if (!PersistentAsset(sourceFont, out var fontGuid, out var fontFileId) ||
                !PersistentAsset(sourceMaterial, out var sourceMaterialGuid, out var sourceMaterialFileId))
                return Fail("TMP_SORT_OWNER_STYLE_FONT_SOURCE_NOT_PERSISTENT", out diagnostic);
            var width = outline.SourceOutlineWidth;
            var color = outline.SourceOutlineColor;
            if (Single.IsNaN(width) || Single.IsInfinity(width) || width < 0f ||
                Single.IsNaN(owner.fontSize) || Single.IsInfinity(owner.fontSize) || owner.fontSize <= 0f ||
                !sourceMaterial.HasProperty("_GradientScale") || !sourceMaterial.HasProperty("_OutlineWidth") ||
                !sourceMaterial.HasProperty("_OutlineColor"))
                return Fail("TMP_SORT_OWNER_STYLE_SOURCE_METRICS_OR_SHADER_INVALID", out diagnostic);
            var gradient = sourceMaterial.GetFloat("_GradientScale");
            var pointSize = sourceFont.faceInfo.pointSize;
            if (Single.IsNaN(gradient) || Single.IsInfinity(gradient) || gradient <= 1f ||
                Single.IsNaN(pointSize) || Single.IsInfinity(pointSize) || pointSize <= 0f)
                return Fail("TMP_SORT_OWNER_STYLE_FONT_METRICS_INVALID", out diagnostic);
            var outlineWidth = width * pointSize / owner.fontSize / (gradient - 1f);
            if (Single.IsNaN(outlineWidth) || Single.IsInfinity(outlineWidth))
                return Fail("TMP_SORT_OWNER_STYLE_DERIVED_WIDTH_INVALID", out diagnostic);

            var expected = new Material(sourceMaterial) { hideFlags = HideFlags.HideAndDontSave };
            if (!outline.ConfigureCaptureCandidate(expected, sourceFont, owner.fontSize, out var derivationDiagnostic))
            {
                UnityEngine.Object.DestroyImmediate(expected);
                return Fail("TMP_SORT_OWNER_STYLE_FONT_ASSET_DERIVATION_FAILED:" + derivationDiagnostic, out diagnostic);
            }
            // The native driver calls UpdateMeshPadding after configuring a
            // material. TMP's padding calculation also updates _ScaleRatioA/B/C
            // from outline, softness, weight and shader keywords; reproduce that
            // SDK step on the temporary candidate before comparing fingerprints.
            TMPro.ShaderUtilities.GetPadding(expected, owner.extraPadding, owner.isUsingBold);
            var expectedFingerprint = MaterialFingerprint(expected);
            var liveMaterial = owner.fontSharedMaterial;
            var liveFingerprint = MaterialFingerprint(liveMaterial);
            if (String.IsNullOrEmpty(expectedFingerprint) || expectedFingerprint != liveFingerprint)
            {
                var delta = MaterialFingerprintDelta(expected, liveMaterial);
                var expectedHash = String.IsNullOrEmpty(expectedFingerprint) ? "unavailable" : expectedFingerprint.Substring(0, Math.Min(12, expectedFingerprint.Length));
                var liveHash = String.IsNullOrEmpty(liveFingerprint) ? "unavailable" : liveFingerprint.Substring(0, Math.Min(12, liveFingerprint.Length));
                UnityEngine.Object.DestroyImmediate(expected);
                return Fail("TMP_SORT_OWNER_STYLE_TRANSIENT_DIFFERS_FROM_FONT_ASSET_DERIVATION:expected=" + expectedHash +
                    ";actual=" + liveHash + ";delta=" + delta, out diagnostic);
            }

            if (!PersistentAssetPath(persistentAssetPath, out diagnostic))
            {
                UnityEngine.Object.DestroyImmediate(expected);
                return false;
            }
            var saved = AssetDatabase.LoadAssetAtPath<Material>(persistentAssetPath);
            if (saved == null)
            {
                if (File.Exists(persistentAssetPath))
                {
                    UnityEngine.Object.DestroyImmediate(expected);
                    return Fail("TMP_SORT_OWNER_STYLE_PATH_IS_OWNED_BY_NON_MATERIAL", out diagnostic);
                }
                expected.name = Path.GetFileNameWithoutExtension(persistentAssetPath);
                expected.hideFlags = HideFlags.None;
                try { AssetDatabase.CreateAsset(expected, persistentAssetPath); }
                catch (Exception error)
                {
                    UnityEngine.Object.DestroyImmediate(expected);
                    return Fail("TMP_SORT_OWNER_STYLE_CREATE_ASSET_FAILED:" + error.GetType().Name, out diagnostic);
                }
                saved = AssetDatabase.LoadAssetAtPath<Material>(persistentAssetPath);
            }
            else UnityEngine.Object.DestroyImmediate(expected);
            if (!PersistentAsset(saved, out _, out _) || MaterialFingerprint(saved) != expectedFingerprint)
                return Fail("TMP_SORT_OWNER_STYLE_PERSISTED_MATERIAL_MISMATCH", out diagnostic);

            owner.fontSharedMaterial = saved;
            owner.UpdateMeshPadding();
            EditorUtility.SetDirty(owner);
            PrefabUtility.RecordPrefabInstancePropertyModifications(owner);
            if (owner.fontSharedMaterial != saved || MaterialFingerprint(owner.fontSharedMaterial) != expectedFingerprint)
                return Fail("TMP_SORT_OWNER_STYLE_ASSIGNMENT_READBACK_MISMATCH", out diagnostic);
            var sourceAtlas = sourceMaterial.GetTexture(MainTex);
            string registerDiagnostic = null;
            if (!PersistentAsset(sourceAtlas, out _, out _))
                return Fail("TMP_SORT_OWNER_STYLE_PERSISTENT_VARIANT_ATLAS_NOT_PERSISTENT", out diagnostic);
            if (!outline.RegisterPersistentMaterialVariant(sourceFont, saved, null, owner.fontSize, sourceAtlas, out registerDiagnostic))
                return Fail("TMP_SORT_OWNER_STYLE_PERSISTENT_VARIANT_REGISTRATION_FAILED:" + registerDiagnostic, out diagnostic);
            EditorUtility.SetDirty(outline);
            PrefabUtility.RecordPrefabInstancePropertyModifications(outline);
            descriptor = new OwnerFontStyleDescriptor {
                profile = "native-static-text-outline-font-material-v1",
                sourceComponentId = sourceComponentId,
                outlineWidth = width,
                outlineColor = color,
                sourceFontAsset = sourceFont,
                sourceFontAssetGuid = fontGuid,
                sourceFontAssetLocalFileId = fontFileId,
                sourceFontMaterial = sourceMaterial,
                sourceFontMaterialGuid = sourceMaterialGuid,
                sourceFontMaterialLocalFileId = sourceMaterialFileId,
                sourceFontMaterialFingerprint = MaterialFingerprint(sourceMaterial),
            };
            persistentMaterial = saved;
            return true;
        }

        public static bool TryResolveSlot(TMP_Text owner, TMP_SubMeshUI generated, int expectedSlot,
            string sourceComponentId, out TextSlotBinding binding, out string diagnostic)
        {
            binding = null; diagnostic = null;
            if (owner == null || expectedSlot < 0 || !(owner is TextMeshProUGUI))
                return Fail("TMP_SORT_SLOT_OWNER_OR_INDEX_INVALID", out diagnostic);
            var info = owner.textInfo;
            if (info == null || info.meshInfo == null || expectedSlot >= info.materialCount || expectedSlot >= info.meshInfo.Length)
                return Fail("TMP_SORT_SLOT_OUT_OF_RANGE:" + expectedSlot, out diagnostic);

            Graphic sourceGraphic;
            Material sourceMaterial;
            TMP_FontAsset fontAsset;
            TMP_SpriteAsset spriteAsset;
            if (expectedSlot == 0)
            {
                if (generated != null) return Fail("TMP_SORT_MAIN_SLOT_HAS_GENERATED_CHILD", out diagnostic);
                sourceGraphic = owner as Graphic;
                sourceMaterial = owner.fontSharedMaterial;
                fontAsset = owner.font;
                spriteAsset = null;
            }
            else
            {
                if (generated == null || generated.textComponent != owner || generated.transform.parent != owner.transform ||
                    !TryMaterialSlot(generated, out var generatedSlot) || generatedSlot != expectedSlot)
                    return Fail("TMP_SORT_GENERATED_SLOT_OWNER_OR_INDEX_MISMATCH:" + expectedSlot, out diagnostic);
                sourceGraphic = generated;
                sourceMaterial = generated.sharedMaterial;
                spriteAsset = generated.spriteAsset;
                fontAsset = spriteAsset == null ? generated.fontAsset : null;
            }
            var slotInfo = info.meshInfo[expectedSlot];
            var sourceMesh = slotInfo.mesh;
            if (sourceGraphic == null || sourceMaterial == null || sourceMesh == null || sourceMesh.vertexCount <= 0)
            {
                var mismatchCanvasMesh = sourceGraphic == null || sourceGraphic.canvasRenderer == null ? null : sourceGraphic.canvasRenderer.GetMesh();
                return Fail("TMP_SORT_SLOT_SOURCE_MATERIAL_OR_MESH_MISMATCH:" + expectedSlot +
                    ";graphicNull=" + (sourceGraphic == null) +
                    ";sharedMaterialNull=" + (sourceMaterial == null) +
                    ";slotMaterialNull=" + (slotInfo.material == null) +
                    ";materialRefEqual=" + (slotInfo.material == sourceMaterial) +
                    ";slotMaterial=" + ObjectIdentitySummary(slotInfo.material) +
                    ";sharedMaterial=" + ObjectIdentitySummary(sourceMaterial) +
                    ";slotMeshNull=" + (sourceMesh == null) +
                    ";slotMeshVertices=" + (sourceMesh == null ? -1 : sourceMesh.vertexCount) +
                    ";canvasMeshNull=" + (mismatchCanvasMesh == null) +
                    ";canvasMeshVertices=" + (mismatchCanvasMesh == null ? -1 : mismatchCanvasMesh.vertexCount) +
                    ";meshFingerprintEqual=" + (mismatchCanvasMesh != null && sourceMesh != null && MeshFingerprint(mismatchCanvasMesh) == MeshFingerprint(sourceMesh)), out diagnostic);
            }
            var sourceTexture = sourceMaterial.GetTexture(MainTex);
            if (!ReadTextInfoSlotEvidence(owner, expectedSlot, fontAsset, spriteAsset, sourceMaterial, slotInfo.material,
                out var textInfoCharacterCount, out var textInfoVisibleCharacterCount,
                out var textInfoCharacterEvidenceSha256, out var textInfoCharacterMaterialFingerprint,
                out var textInfoEvidenceDiagnostic))
                return Fail("TMP_SORT_SLOT_TEXTINFO_CHARACTER_EVIDENCE_FAILED:" + expectedSlot + ";diagnostic=" +
                    textInfoEvidenceDiagnostic, out diagnostic);
            var slotMaterialFingerprint = slotInfo.material == null ? null : MaterialFingerprint(slotInfo.material);
            var characterMaterialMatchesSlotInfo = slotInfo.material == null ||
                !String.IsNullOrEmpty(slotMaterialFingerprint) && slotMaterialFingerprint == textInfoCharacterMaterialFingerprint;
            if (!characterMaterialMatchesSlotInfo)
                return Fail("TMP_SORT_SLOT_TEXTINFO_MATERIAL_DOES_NOT_MATCH_CHARACTER_REFERENCE:" + expectedSlot, out diagnostic);
            var canvasRenderer = sourceGraphic.canvasRenderer;
            var rendererMaterial = canvasRenderer == null || canvasRenderer.materialCount == 0 ? null : canvasRenderer.GetMaterial();
            var rendererMaterialMatches = rendererMaterial != null && (rendererMaterial == sourceMaterial ||
                MaterialFingerprint(rendererMaterial) == MaterialFingerprint(sourceMaterial));
            if (!rendererMaterialMatches)
            {
                var rendererDelta = "not_compared";
                try { rendererDelta = MaterialFingerprintDelta(rendererMaterial, sourceMaterial); }
                catch (Exception error) { rendererDelta = "diagnostic_failed:" + error.GetType().Name; }
                return Fail("TMP_SORT_SLOT_CANVAS_RENDERER_MATERIAL_MISMATCH:" + expectedSlot +
                    ";rendererMaterial=" + ObjectIdentitySummary(rendererMaterial) +
                    ";graphicSharedMaterial=" + ObjectIdentitySummary(sourceMaterial) +
                    ";rendererDelta=" + rendererDelta, out diagnostic);
            }
            if (fontAsset == null && spriteAsset == null)
                return Fail("TMP_SORT_SLOT_FONT_OR_SPRITE_ASSET_MISSING:" + expectedSlot, out diagnostic);
            if (!PersistentAsset(fontAsset != null ? (UnityEngine.Object)fontAsset : spriteAsset, out var assetGuid, out var assetFileId))
                return Fail("TMP_SORT_SLOT_FONT_OR_SPRITE_ASSET_NOT_PERSISTENT:" + expectedSlot, out diagnostic);
            if (!TextureBelongsToSourceAsset(fontAsset, spriteAsset, sourceTexture))
                return Fail("TMP_SORT_SLOT_ATLAS_DOES_NOT_MATCH_SOURCE_ASSET:" + expectedSlot, out diagnostic);
            if (!PersistentAsset(sourceMaterial.shader, out var shaderGuid, out var shaderFileId) ||
                !PersistentAsset(sourceTexture, out var textureGuid, out var textureFileId))
                return Fail("TMP_SORT_SLOT_SHADER_OR_ATLAS_NOT_PERSISTENT:" + expectedSlot, out diagnostic);
            var materialPersistent = PersistentAsset(sourceMaterial, out var materialGuid, out var materialFileId);
            if (!materialPersistent) { materialGuid = null; materialFileId = 0; }
            var ownerFontMaterial = owner.fontSharedMaterial;
            string ownerFontMaterialGuid = null; long ownerFontMaterialFileId = 0;
            if (ownerFontMaterial == null || !PersistentAsset(ownerFontMaterial, out ownerFontMaterialGuid, out ownerFontMaterialFileId))
                return Fail("TMP_SORT_OWNER_FONT_SHARED_MATERIAL_NOT_PERSISTENT:" + expectedSlot, out diagnostic);
            var fallbackFontAsset = generated != null ? fontAsset : null;
            var fallbackFontMaterial = fallbackFontAsset == null ? null : fallbackFontAsset.material;
            string fallbackFontAssetGuid = null; long fallbackFontAssetFileId = 0;
            string fallbackFontMaterialGuid = null; long fallbackFontMaterialFileId = 0;
            string fallbackFontMaterialFingerprint = null;
            if (fallbackFontAsset != null && (!PersistentAsset(fallbackFontAsset, out fallbackFontAssetGuid, out fallbackFontAssetFileId) ||
                !PersistentAsset(fallbackFontMaterial, out fallbackFontMaterialGuid, out fallbackFontMaterialFileId)))
                return Fail("TMP_SORT_FALLBACK_FONT_ASSET_OR_MATERIAL_NOT_PERSISTENT:" + expectedSlot, out diagnostic);
            if (fallbackFontMaterial != null)
            {
                fallbackFontMaterialFingerprint = MaterialFingerprint(fallbackFontMaterial);
                if (String.IsNullOrEmpty(fallbackFontMaterialFingerprint))
                    return Fail("TMP_SORT_FALLBACK_FONT_MATERIAL_FINGERPRINT_UNAVAILABLE:" + expectedSlot, out diagnostic);
            }
            var canvasMesh = sourceGraphic.canvasRenderer == null ? null : sourceGraphic.canvasRenderer.GetMesh();
            var sourceMeshSha = MeshFingerprint(sourceMesh);
            if (canvasMesh == null || MeshFingerprint(canvasMesh) != sourceMeshSha)
                return Fail("TMP_SORT_SLOT_CANVAS_MESH_DIFFERS_FROM_TEXTINFO:" + expectedSlot, out diagnostic);
            var sourceMaterialFingerprint = MaterialFingerprint(sourceMaterial);
            if (String.IsNullOrEmpty(sourceMaterialFingerprint))
                return Fail("TMP_SORT_SLOT_TRANSIENT_MATERIAL_FINGERPRINT_UNAVAILABLE:" + expectedSlot, out diagnostic);
            var ownerFontMaterialFingerprint = ownerFontMaterial == null ? null : MaterialFingerprint(ownerFontMaterial);
            if (ownerFontMaterial != null && String.IsNullOrEmpty(ownerFontMaterialFingerprint))
                return Fail("TMP_SORT_OWNER_FONT_SHARED_MATERIAL_FINGERPRINT_UNAVAILABLE:" + expectedSlot, out diagnostic);
            binding = new TextSlotBinding { sourceComponentId = sourceComponentId, owner = owner,
                sourceGraphic = sourceGraphic, sourceMesh = sourceMesh, materialSlot = expectedSlot,
                generatedSubmesh = generated != null, sourceGraphicEnabled = sourceGraphic.enabled,
                sourceGraphicActiveSelf = sourceGraphic.gameObject.activeSelf,
                textInfoMaterialMissing = slotInfo.material == null,
                textInfoCharacterSlotVerified = true,
                textInfoCharacterMaterialVerified = true,
                textInfoFontAssetVerified = true,
                textInfoAtlasVerified = true,
                textInfoCharacterCount = textInfoCharacterCount,
                textInfoVisibleCharacterCount = textInfoVisibleCharacterCount,
                sourceTextSha256 = HashText(owner.text ?? String.Empty),
                textInfoCharacterEvidenceSha256 = textInfoCharacterEvidenceSha256,
                textInfoCharacterMaterialFingerprint = textInfoCharacterMaterialFingerprint,
                fontAsset = fontAsset, spriteAsset = spriteAsset, sourceMaterial = sourceMaterial,
                ownerFontSharedMaterial = ownerFontMaterial, fallbackFontAsset = fallbackFontAsset,
                fallbackFontMaterial = fallbackFontMaterial, proxyMaterial = materialPersistent ? sourceMaterial : null,
                sourceTexture = sourceTexture,
                fontAssetGuid = fontAsset != null ? assetGuid : null,
                fontAssetLocalFileId = fontAsset != null ? assetFileId : 0,
                spriteAssetGuid = spriteAsset != null ? assetGuid : null,
                spriteAssetLocalFileId = spriteAsset != null ? assetFileId : 0,
                sourceMaterialGuid = materialGuid, sourceMaterialLocalFileId = materialFileId,
                sourceShaderGuid = shaderGuid, sourceShaderLocalFileId = shaderFileId,
                sourceTextureGuid = textureGuid, sourceTextureLocalFileId = textureFileId,
                sourceMeshSha256 = sourceMeshSha, sourceMaterialFingerprint = sourceMaterialFingerprint,
                ownerFontMaterialGuid = ownerFontMaterialGuid, ownerFontMaterialLocalFileId = ownerFontMaterialFileId,
                ownerFontMaterialFingerprint = ownerFontMaterialFingerprint,
                fallbackFontAssetGuid = fallbackFontAssetGuid, fallbackFontAssetLocalFileId = fallbackFontAssetFileId,
                fallbackFontMaterialGuid = fallbackFontMaterialGuid, fallbackFontMaterialLocalFileId = fallbackFontMaterialFileId,
                fallbackFontMaterialFingerprint = fallbackFontMaterialFingerprint };
            if (materialPersistent)
            {
                binding.proxyMaterial = sourceMaterial;
                binding.proxyMaterialFingerprint = sourceMaterialFingerprint;
                binding.proxyMaterialGuid = materialGuid;
                binding.proxyMaterialLocalFileId = materialFileId;
            }
            return true;
        }

        /// <summary>Enumerate fresh current TMP slots after ForceMeshUpdate; never retain generated child references.</summary>
        public static bool GetCurrentSlots(TMP_Text owner, string sourceComponentId,
            out List<TextSlotBinding> slots, out string diagnostic)
        {
            return GetCurrentSlots(owner, sourceComponentId, out slots, out _, out diagnostic);
        }

        public static bool GetCurrentSlots(TMP_Text owner, string sourceComponentId,
            out List<TextSlotBinding> slots, out NativeStaticSortTextSlotEnumeration enumeration,
            out string diagnostic)
        {
            slots = new List<TextSlotBinding>(); enumeration = null; diagnostic = null;
            if (owner == null || String.IsNullOrWhiteSpace(sourceComponentId))
                return Fail("TMP_SORT_CURRENT_SLOTS_OWNER_OR_ID_MISSING", out diagnostic);
            var info = owner.textInfo;
            if (info == null || info.materialCount <= 0 || info.meshInfo == null || info.meshInfo.Length < info.materialCount)
                return Fail("TMP_SORT_CURRENT_SLOTS_TEXTINFO_UNAVAILABLE", out diagnostic);
            var children = owner.GetComponentsInChildren<TMP_SubMeshUI>(true)
                .Where(child => IsGeneratedSubmesh(child, owner) && TryMaterialSlot(child, out _)).ToArray();
            var rows = new List<NativeStaticSortTextSlotEvidence>();
            for (var slot = 0; slot < info.materialCount; slot++)
            {
                var textInfoReferences = 0;
                var visibleTextInfoReferences = 0;
                for (var characterIndex = 0; characterIndex < info.characterCount; characterIndex++)
                {
                    var character = info.characterInfo[characterIndex];
                    if (character.materialReferenceIndex != slot) continue;
                    textInfoReferences++;
                    if (character.isVisible) visibleTextInfoReferences++;
                }
                TMP_SubMeshUI generated = null;
                if (slot > 0)
                {
                    var matches = children.Where(child => TryMaterialSlot(child, out var childSlot) && childSlot == slot).ToArray();
                    if (matches.Length > 1 || textInfoReferences > 0 && matches.Length != 1)
                        return Fail("TMP_SORT_CURRENT_SLOT_GENERATED_CHILD_NOT_UNIQUE:" + slot + ":" + matches.Length, out diagnostic);
                    if (matches.Length == 1) generated = matches[0];
                }
                var slotMesh = info.meshInfo[slot].mesh;
                var slotGraphic = slot == 0 ? owner as Graphic : generated as Graphic;
                var rendererMesh = slotGraphic == null || slotGraphic.canvasRenderer == null ? null : slotGraphic.canvasRenderer.GetMesh();
                if (textInfoReferences == 0 || visibleTextInfoReferences == 0)
                {
                    var slotHasTriangles = MeshHasDrawTriangles(slotMesh);
                    var rendererHasTriangles = MeshHasDrawTriangles(rendererMesh);
                    if (slotHasTriangles || rendererHasTriangles)
                        return Fail("TMP_SORT_UNREFERENCED_TEXTINFO_SLOT_HAS_RENDERED_MESH:" + slot +
                            ":references=" + textInfoReferences + ":visible=" + visibleTextInfoReferences +
                            ":slotVertices=" + (slotMesh == null ? -1 : slotMesh.vertexCount) +
                            ":slotTriangles=" + MeshFirstSubmeshIndexCount(slotMesh) +
                            ":canvasVertices=" + (rendererMesh == null ? -1 : rendererMesh.vertexCount) +
                            ":canvasTriangles=" + MeshFirstSubmeshIndexCount(rendererMesh) +
                            ":slotGeometry=" + MeshGeometryDiagnostic(slotMesh) +
                            ":canvasGeometry=" + MeshGeometryDiagnostic(rendererMesh), out diagnostic);
                    var placeholderGraphic = slotGraphic;
                    rows.Add(BuildTextInfoSlotEvidence(owner, slot, placeholderGraphic, generated, null,
                        textInfoReferences, visibleTextInfoReferences, "empty-placeholder"));
                    continue;
                }
                if (slotGraphic == null)
                    return Fail("TMP_SORT_CURRENT_SLOT_GRAPHIC_MISSING:" + slot, out diagnostic);
                if (!TryResolveSlot(owner, generated, slot, sourceComponentId, out var binding, out diagnostic))
                    return false;
                rows.Add(BuildTextInfoSlotEvidence(owner, slot, slotGraphic, generated, binding,
                    textInfoReferences, visibleTextInfoReferences, "drawable"));
                slots.Add(binding);
            }
            var sourceTextSha = HashText(owner.text ?? String.Empty);
            enumeration = new NativeStaticSortTextSlotEnumeration {
                sourceComponentId = sourceComponentId,
                sourceTextSha256 = sourceTextSha,
                slotCount = info.materialCount,
                verified = rows.Count == info.materialCount && rows.All(row => row != null && !String.IsNullOrEmpty(row.evidenceSha256)),
                rows = rows.ToArray(),
            };
            enumeration.evidenceSha256 = TextSlotEnumerationHash(enumeration);
            enumeration.verified = enumeration.verified && IsValidTextSlotEnumeration(enumeration);
            if (!enumeration.verified)
                return Fail("TMP_SORT_TEXTINFO_SLOT_ENUMERATION_INCOMPLETE:" + rows.Count + "/" + info.materialCount, out diagnostic);
            foreach (var binding in slots) binding.textSlotEnumeration = enumeration;
            return true;
        }

        static NativeStaticSortTextSlotEvidence BuildTextInfoSlotEvidence(TMP_Text owner, int slot,
            Graphic sourceGraphic, TMP_SubMeshUI generated, TextSlotBinding binding,
            int characterReferences, int visibleCharacterReferences, string disposition)
        {
            var info = owner.textInfo;
            var slotMesh = info.meshInfo[slot].mesh;
            var rendererMesh = sourceGraphic == null || sourceGraphic.canvasRenderer == null
                ? null : sourceGraphic.canvasRenderer.GetMesh();
            var sourceAsset = binding != null
                ? (UnityEngine.Object)(binding.spriteAsset != null ? (UnityEngine.Object)binding.spriteAsset : binding.fontAsset)
                : generated != null
                    ? (UnityEngine.Object)(generated.spriteAsset != null ? (UnityEngine.Object)generated.spriteAsset : generated.fontAsset)
                    : owner.font;
            var sourceAssetKind = sourceAsset is TMP_SpriteAsset ? "sprite" : sourceAsset is TMP_FontAsset ? "font" : "unresolved";
            var sourceGraphicMaterial = binding != null ? binding.sourceMaterial
                : slot == 0 ? owner.fontSharedMaterial
                : generated != null ? generated.sharedMaterial : null;
            Texture atlas = binding != null ? binding.sourceTexture
                : sourceGraphicMaterial == null ? null : sourceGraphicMaterial.GetTexture(MainTex);
            var textInfoMaterial = info.meshInfo[slot].material;
            AssetIdentity(sourceAsset, out var sourceAssetGuid, out var sourceAssetFileId);
            AssetIdentity(atlas, out var atlasGuid, out var atlasFileId);
            var textInfoMaterialFingerprint = MaterialFingerprint(textInfoMaterial);
            var graphicMaterialFingerprint = MaterialFingerprint(sourceGraphicMaterial);
            var characterProof = binding != null ? binding.textInfoCharacterEvidenceSha256
                : HashText(owner.text + "|slot=" + slot + "|characters=" + characterReferences + "|visible=" + visibleCharacterReferences);
            var row = new NativeStaticSortTextSlotEvidence {
                slot = slot,
                characterReferences = characterReferences,
                visibleCharacterReferences = visibleCharacterReferences,
                textInfoMaterialMissing = textInfoMaterial == null,
                textInfoVertexCount = slotMesh == null ? 0 : slotMesh.vertexCount,
                textInfoTriangleIndexCount = MeshTotalIndexCount(slotMesh),
                textInfoNondegenerateTriangleCount = MeshNonDegenerateTriangleCount(slotMesh),
                canvasVertexCount = rendererMesh == null ? 0 : rendererMesh.vertexCount,
                canvasTriangleIndexCount = MeshTotalIndexCount(rendererMesh),
                canvasNondegenerateTriangleCount = MeshNonDegenerateTriangleCount(rendererMesh),
                disposition = disposition,
                sourceAssetKind = sourceAssetKind,
                sourceAssetGuid = sourceAssetGuid,
                sourceAssetLocalFileId = sourceAssetFileId,
                atlasGuid = atlasGuid,
                atlasLocalFileId = atlasFileId,
                textInfoMaterialFingerprint = textInfoMaterialFingerprint,
                sourceGraphicMaterialFingerprint = graphicMaterialFingerprint,
                characterEvidenceSha256 = characterProof,
            };
            row.evidenceSha256 = TextSlotRowHash(row);
            return row;
        }

        static bool EnumerationIsPlaceholderOnly(NativeStaticSortTextSlotEnumeration enumeration)
        {
            return IsValidTextSlotEnumeration(enumeration) && enumeration.rows.All(row => row.disposition == "empty-placeholder");
        }

        /// <summary>Persist typed slot denominator evidence on an empty text renderer carrier.</summary>
        public static bool AttachEmptyTextSlotEnumeration(GameObject carrier, TMP_Text owner,
            string sourceComponentId, NativeStaticSortTextSlotEnumeration enumeration, out string diagnostic)
        {
            diagnostic = null;
            if (carrier == null || owner == null || String.IsNullOrWhiteSpace(sourceComponentId) ||
                !EnumerationIsPlaceholderOnly(enumeration) || enumeration.sourceComponentId != sourceComponentId ||
                enumeration.sourceTextSha256 != HashText(owner.text ?? String.Empty))
                return Fail("TMP_SORT_EMPTY_TEXT_SLOT_ENUMERATION_INPUT_INVALID", out diagnostic);
            var identity = carrier.GetComponent<NativeStaticSortTextSlotEnumerationIdentity>() ??
                carrier.AddComponent<NativeStaticSortTextSlotEnumerationIdentity>();
            identity.sourceOwner = owner;
            identity.sourceComponentId = sourceComponentId;
            identity.slotEnumeration = enumeration;
            EditorUtility.SetDirty(identity);
            PrefabUtility.RecordPrefabInstancePropertyModifications(identity);
            return true;
        }

        /// <summary>Read-only current-slot proof for a typed empty-text carrier.</summary>
        public static bool ReadEmptyTextSlotEnumerationIdentity(NativeStaticSortTextSlotEnumerationIdentity identity,
            TMP_Text expectedOwner, string expectedSourceComponentId, out TextSlotEnumerationReadback readback)
        {
            readback = new TextSlotEnumerationReadback { diagnostic = "TMP_SORT_EMPTY_TEXT_ENUMERATION_READBACK_FAILED" };
            if (identity == null || expectedOwner == null) return false;
            readback.sourceComponentId = identity.sourceComponentId;
            readback.slotEnumeration = identity.slotEnumeration;
            readback.ownerScopeVerified = identity.sourceOwner == expectedOwner &&
                identity.sourceComponentId == expectedSourceComponentId;
            readback.persistentReferencesVerified = readback.ownerScopeVerified;
            if (!readback.ownerScopeVerified || !EnumerationIsPlaceholderOnly(identity.slotEnumeration) ||
                identity.slotEnumeration.sourceTextSha256 != HashText(expectedOwner.text ?? String.Empty))
            {
                readback.diagnostic = "TMP_SORT_EMPTY_TEXT_ENUMERATION_SAVED_OWNER_OR_CONTRACT_MISMATCH";
                return false;
            }
            if (!PrepareSource(expectedOwner, expectedSourceComponentId, out var prepareDiagnostic))
            {
                readback.diagnostic = prepareDiagnostic;
                return false;
            }
            if (!GetCurrentSlots(expectedOwner, expectedSourceComponentId, out var slots,
                out var currentEnumeration, out var slotDiagnostic))
            {
                readback.diagnostic = slotDiagnostic;
                return false;
            }
            readback.currentSlotEnumeration = currentEnumeration;
            readback.verified = slots.Count == 0 && EnumerationIsPlaceholderOnly(currentEnumeration) &&
                currentEnumeration.sourceComponentId == identity.sourceComponentId &&
                currentEnumeration.evidenceSha256 == identity.slotEnumeration.evidenceSha256;
            readback.diagnostic = readback.verified ? null : "TMP_SORT_EMPTY_TEXT_ENUMERATION_CURRENT_SLOT_PROOF_CHANGED";
            return readback.verified;
        }

        static string TextSlotRowHash(NativeStaticSortTextSlotEvidence row)
        {
            if (row == null) return null;
            return HashText(row.slot + "|" + row.characterReferences + "|" + row.visibleCharacterReferences +
                "|" + row.textInfoMaterialMissing + "|" + row.textInfoVertexCount + "|" + row.textInfoTriangleIndexCount +
                "|" + row.textInfoNondegenerateTriangleCount + "|" + row.canvasVertexCount + "|" + row.canvasTriangleIndexCount +
                "|" + row.canvasNondegenerateTriangleCount + "|" + row.disposition + "|" + row.sourceAssetKind + "|" +
                row.sourceAssetGuid + ":" + row.sourceAssetLocalFileId + "|" + row.atlasGuid + ":" + row.atlasLocalFileId + "|" +
                row.textInfoMaterialFingerprint + "|" + row.sourceGraphicMaterialFingerprint + "|" + row.characterEvidenceSha256);
        }

        static string TextSlotEnumerationHash(NativeStaticSortTextSlotEnumeration enumeration)
        {
            if (enumeration == null) return null;
            var rowHashes = (enumeration.rows ?? Array.Empty<NativeStaticSortTextSlotEvidence>())
                .Select(row => row == null ? String.Empty : row.evidenceSha256 ?? String.Empty).ToArray();
            return HashText(enumeration.sourceComponentId + "|" + enumeration.sourceTextSha256 + "|" + enumeration.slotCount + "|" +
                String.Join("|", rowHashes));
        }

        static bool IsValidTextSlotEnumeration(NativeStaticSortTextSlotEnumeration enumeration)
        {
            if (enumeration == null || !enumeration.verified || String.IsNullOrWhiteSpace(enumeration.sourceComponentId) ||
                !IsSha256(enumeration.sourceTextSha256) || enumeration.slotCount <= 0 || enumeration.rows == null ||
                enumeration.rows.Length != enumeration.slotCount || !IsSha256(enumeration.evidenceSha256) ||
                TextSlotEnumerationHash(enumeration) != enumeration.evidenceSha256) return false;
            for (var index = 0; index < enumeration.rows.Length; index++)
            {
                var row = enumeration.rows[index];
                if (row == null || row.slot != index || !IsSha256(row.evidenceSha256) ||
                    TextSlotRowHash(row) != row.evidenceSha256 ||
                    (row.disposition != "drawable" && row.disposition != "empty-placeholder") ||
                    (row.sourceAssetKind != "font" && row.sourceAssetKind != "sprite") ||
                    String.IsNullOrWhiteSpace(row.sourceAssetGuid) || row.sourceAssetLocalFileId == 0 ||
                    String.IsNullOrWhiteSpace(row.atlasGuid) || row.atlasLocalFileId == 0 ||
                    !IsSha256(row.characterEvidenceSha256)) return false;
                if (row.disposition == "drawable" &&
                    (row.characterReferences <= 0 || row.visibleCharacterReferences <= 0 ||
                     row.textInfoNondegenerateTriangleCount <= 0 || row.canvasNondegenerateTriangleCount <= 0)) return false;
                if (row.disposition == "empty-placeholder" &&
                    (row.visibleCharacterReferences > 0 || row.textInfoNondegenerateTriangleCount > 0 ||
                     row.canvasNondegenerateTriangleCount > 0)) return false;
            }
            return true;
        }

        /// <summary>
        /// Carry a previously verified TMP SDK fallback proof onto the current
        /// mesh/Graphic after re-preparation. Current material must be the exact
        /// owned asset baked from that proof; generated child object identity is
        /// intentionally discarded.
        /// </summary>
        public static bool RebindCapturedSlot(TextSlotBinding capturedProof, TMP_Text currentOwner,
            Graphic currentGraphic, out TextSlotBinding rebound, out string diagnostic)
        {
            rebound = null; diagnostic = null;
            if (capturedProof == null || currentOwner == null || currentGraphic == null ||
                capturedProof.owner != currentOwner || capturedProof.sourceGraphic == null ||
                capturedProof.sourceComponentId == null)
                return Fail("TMP_SORT_CAPTURE_REBIND_INPUT_INVALID", out diagnostic);
            if (!TryResolveSlot(currentOwner, currentGraphic as TMP_SubMeshUI, capturedProof.materialSlot,
                capturedProof.sourceComponentId, out var current, out diagnostic)) return false;
            if (current.sourceGraphic != currentGraphic || current.generatedSubmesh != capturedProof.generatedSubmesh ||
                current.sourceMeshSha256 != capturedProof.sourceMeshSha256 || current.fontAsset != capturedProof.fontAsset ||
                current.spriteAsset != capturedProof.spriteAsset || current.ownerFontSharedMaterial != capturedProof.ownerFontSharedMaterial ||
                current.sourceTexture != capturedProof.sourceTexture || current.fallbackFontAsset != capturedProof.fallbackFontAsset ||
                current.fallbackFontMaterial != capturedProof.fallbackFontMaterial ||
                current.textInfoMaterialMissing != capturedProof.textInfoMaterialMissing ||
                current.textInfoCharacterEvidenceSha256 != capturedProof.textInfoCharacterEvidenceSha256 ||
                current.textInfoCharacterMaterialFingerprint != capturedProof.textInfoCharacterMaterialFingerprint ||
                current.textInfoCharacterCount != capturedProof.textInfoCharacterCount ||
                current.textInfoVisibleCharacterCount != capturedProof.textInfoVisibleCharacterCount ||
                current.sourceTextSha256 != capturedProof.sourceTextSha256 ||
                capturedProof.ownerStyle != null &&
                    (capturedProof.ownerStyle.sourceComponentId != capturedProof.sourceComponentId ||
                     capturedProof.ownerStyle.sourceFontAsset != currentOwner.font ||
                     capturedProof.ownerStyle.sourceFontMaterial != currentOwner.font.material ||
                     capturedProof.ownerStyle.profile != "native-static-text-outline-font-material-v1"))
                return Fail("TMP_SORT_CAPTURE_REBIND_SOURCE_IDENTITY_OR_MESH_CHANGED", out diagnostic);

            if (capturedProof.tmpFallbackMaterialBaked)
            {
                if (capturedProof.persistentFallbackVariantRegistered)
                {
                    if (!PersistentAsset(current.sourceMaterial, out var currentGuid, out var currentFileId) ||
                        current.sourceMaterial != capturedProof.proxyMaterial ||
                        current.sourceMaterialFingerprint != capturedProof.bakedProxyMaterialFingerprint ||
                        currentGuid != capturedProof.bakedProxyMaterialGuid || currentFileId != capturedProof.bakedProxyMaterialLocalFileId ||
                        capturedProof.bakedProxyMaterialFingerprint != capturedProof.transientFallbackFingerprint)
                        return Fail("TMP_SORT_CAPTURE_REBIND_REGISTERED_FALLBACK_VARIANT_MISMATCH", out diagnostic);
                }
                else if (PersistentAsset(current.sourceMaterial, out _, out _) || current.sourceMaterial == null ||
                    current.sourceMaterialFingerprint != capturedProof.transientFallbackFingerprint ||
                    capturedProof.bakedProxyMaterialFingerprint != capturedProof.transientFallbackFingerprint)
                    return Fail("TMP_SORT_CAPTURE_REBIND_SDK_TRANSIENT_FALLBACK_PROFILE_MISMATCH", out diagnostic);
            }
            else if (current.sourceMaterial != capturedProof.sourceMaterial ||
                current.sourceMaterialFingerprint != capturedProof.sourceMaterialFingerprint)
                return Fail("TMP_SORT_CAPTURE_REBIND_SOURCE_MATERIAL_CHANGED", out diagnostic);

            current.ownerStyle = capturedProof.ownerStyle;
            current.tmpFallbackMaterialBaked = capturedProof.tmpFallbackMaterialBaked;
            current.persistentFallbackVariantRegistered = capturedProof.persistentFallbackVariantRegistered;
            current.tmpFallbackAlgorithm = capturedProof.tmpFallbackAlgorithm;
            current.tmpFallbackAtlasIndex = capturedProof.tmpFallbackAtlasIndex;
            current.ownerFontMaterialGuid = capturedProof.ownerFontMaterialGuid;
            current.ownerFontMaterialLocalFileId = capturedProof.ownerFontMaterialLocalFileId;
            current.ownerFontMaterialFingerprint = capturedProof.ownerFontMaterialFingerprint;
            current.fallbackFontAssetGuid = capturedProof.fallbackFontAssetGuid;
            current.fallbackFontAssetLocalFileId = capturedProof.fallbackFontAssetLocalFileId;
            current.fallbackFontMaterialGuid = capturedProof.fallbackFontMaterialGuid;
            current.fallbackFontMaterialLocalFileId = capturedProof.fallbackFontMaterialLocalFileId;
            current.fallbackFontMaterialFingerprint = capturedProof.fallbackFontMaterialFingerprint;
            current.fallbackAtlasGuid = capturedProof.fallbackAtlasGuid;
            current.fallbackAtlasLocalFileId = capturedProof.fallbackAtlasLocalFileId;
            current.transientFallbackFingerprint = capturedProof.transientFallbackFingerprint;
            current.sourceMaterialFingerprint = capturedProof.sourceMaterialFingerprint;
            current.proxyMaterial = capturedProof.proxyMaterial;
            current.proxyMaterialFingerprint = capturedProof.proxyMaterialFingerprint;
            current.proxyMaterialGuid = capturedProof.proxyMaterialGuid;
            current.proxyMaterialLocalFileId = capturedProof.proxyMaterialLocalFileId;
            current.bakedProxyMaterialFingerprint = capturedProof.bakedProxyMaterialFingerprint;
            current.bakedProxyMaterialGuid = capturedProof.bakedProxyMaterialGuid;
            current.bakedProxyMaterialLocalFileId = capturedProof.bakedProxyMaterialLocalFileId;
            if (current.tmpFallbackMaterialBaked)
            {
                current.sourceMaterialGuid = null;
                current.sourceMaterialLocalFileId = 0;
            }
            rebound = current;
            return true;
        }

        /// <summary>
        /// Capture-only persistence step for TMP's hidden fallback material.
        /// It asks the pinned TMP SDK for the exact fallback result, compares
        /// every shader property to the transient submesh material, then saves
        /// that exact material profile as an owned .mat asset. Readback paths
        /// never call this method and never create or repair assets.
        /// </summary>
        public static bool CaptureFallbackMaterial(TextSlotBinding binding, string persistentAssetPath,
            out string diagnostic)
        {
            diagnostic = null;
            if (binding == null || binding.sourceMaterial == null || binding.sourceTexture == null)
                return Fail("TMP_SORT_FALLBACK_CAPTURE_BINDING_INCOMPLETE", out diagnostic);
            if (PersistentAsset(binding.sourceMaterial, out var directGuid, out var directFileId))
            {
                binding.persistentFallbackVariantRegistered = false;
                if (binding.generatedSubmesh && binding.owner != null && binding.fallbackFontAsset != null && binding.fallbackFontAsset != binding.owner.font)
                {
                    var outline = binding.owner.GetComponent<NativeStaticTextOutline>();
                    if (outline != null && !outline.RegisterPersistentMaterialVariant(binding.fallbackFontAsset,
                        binding.sourceMaterial, binding.ownerFontSharedMaterial, binding.owner.fontSize,
                        binding.sourceTexture, out var registerDiagnostic))
                        return Fail("TMP_SORT_PERSISTENT_FALLBACK_VARIANT_REGISTRATION_FAILED:" + registerDiagnostic, out diagnostic);
                    if (outline != null)
                    {
                        binding.persistentFallbackVariantRegistered = true;
                        EditorUtility.SetDirty(outline);
                        PrefabUtility.RecordPrefabInstancePropertyModifications(outline);
                    }
                }
                binding.proxyMaterial = binding.sourceMaterial;
                binding.proxyMaterialFingerprint = MaterialFingerprint(binding.sourceMaterial);
                binding.proxyMaterialGuid = directGuid;
                binding.proxyMaterialLocalFileId = directFileId;
                binding.bakedProxyMaterialFingerprint = binding.proxyMaterialFingerprint;
                binding.tmpFallbackMaterialBaked = false;
                return !String.IsNullOrEmpty(binding.proxyMaterialFingerprint) ||
                    Fail("TMP_SORT_SOURCE_MATERIAL_FINGERPRINT_UNAVAILABLE", out diagnostic);
            }

            var owner = binding.owner;
            var sourceBase = binding.ownerFontSharedMaterial;
            var fallbackFont = binding.fallbackFontAsset;
            var fallbackBase = binding.fallbackFontMaterial;
            if (owner == null || sourceBase == null || fallbackFont == null || fallbackBase == null)
                return Fail("TMP_SORT_TRANSIENT_MATERIAL_HAS_NO_EXACT_OWNER_FONT_PROVENANCE", out diagnostic);
            if (!PersistentAsset(sourceBase, out binding.ownerFontMaterialGuid, out binding.ownerFontMaterialLocalFileId) ||
                !PersistentAsset(fallbackFont, out binding.fallbackFontAssetGuid, out binding.fallbackFontAssetLocalFileId) ||
                !PersistentAsset(fallbackBase, out binding.fallbackFontMaterialGuid, out binding.fallbackFontMaterialLocalFileId) ||
                !PersistentAsset(binding.sourceTexture, out binding.fallbackAtlasGuid, out binding.fallbackAtlasLocalFileId))
                return Fail("TMP_SORT_TRANSIENT_FALLBACK_SOURCE_ASSET_NOT_PERSISTENT", out diagnostic);
            if (fallbackFont.atlasTextures == null)
                return Fail("TMP_SORT_FALLBACK_FONT_HAS_NO_ATLAS_ARRAY", out diagnostic);
            var atlasIndexes = Enumerable.Range(0, fallbackFont.atlasTextures.Length)
                .Where(index => fallbackFont.atlasTextures[index] == binding.sourceTexture).ToArray();
            if (atlasIndexes.Length != 1)
                return Fail("TMP_SORT_FALLBACK_ATLAS_IDENTITY_NOT_UNIQUE:" + atlasIndexes.Length, out diagnostic);
            var atlasIndex = atlasIndexes[0];
            binding.tmpFallbackAtlasIndex = atlasIndex;

            Material sdkOutput = null;
            var algorithm = "";
            try
            {
                if (fallbackFont != owner.font)
                {
                    // TMP_TextProcessing uses GetFallbackMaterial(currentMaterial, fallbackFont.material)
                    // when matchMaterialPreset is enabled. The source must be the exact persistent
                    // owner fontSharedMaterial; an alternate style/material chain is not inferred.
                    sdkOutput = TMP_MaterialManager.GetFallbackMaterial(sourceBase, fallbackBase);
                    algorithm = "tmpro-fallback-font-material-v1";
                    if (atlasIndex > 0)
                    {
                        if (MultiAtlasFallbackMethod == null)
                            return Fail("TMP_SORT_PINNED_MULTI_ATLAS_FALLBACK_API_UNAVAILABLE", out diagnostic);
                        sdkOutput = MultiAtlasFallbackMethod.Invoke(null, new object[] { fallbackFont, sdkOutput, atlasIndex }) as Material;
                        algorithm += "+tmpro-multi-atlas-v1";
                    }
                }
                else if (atlasIndex > 0)
                {
                    if (MultiAtlasFallbackMethod == null)
                        return Fail("TMP_SORT_PINNED_MULTI_ATLAS_FALLBACK_API_UNAVAILABLE", out diagnostic);
                    sdkOutput = MultiAtlasFallbackMethod.Invoke(null, new object[] { fallbackFont, sourceBase, atlasIndex }) as Material;
                    algorithm = "tmpro-multi-atlas-v1";
                }
                else
                    return Fail("TMP_SORT_TRANSIENT_MATERIAL_IS_NOT_A_SUPPORTED_TMP_FALLBACK", out diagnostic);
            }
            catch (Exception error)
            {
                return Fail("TMP_SORT_SDK_FALLBACK_EVALUATION_FAILED:" + error.GetType().Name, out diagnostic);
            }
            Material profileOutput = sdkOutput;
            bool ownsProfileOutput = false;
            var outlineDriver = owner.GetComponent<NativeStaticTextOutline>();
            if (outlineDriver != null && fallbackFont != owner.font)
            {
                profileOutput = new Material(sdkOutput) { hideFlags = HideFlags.HideAndDontSave };
                ownsProfileOutput = true;
                if (!outlineDriver.ConfigureCaptureCandidate(profileOutput, fallbackFont, owner.fontSize, out var styleDiagnostic))
                {
                    UnityEngine.Object.DestroyImmediate(profileOutput);
                    return Fail("TMP_SORT_FALLBACK_OUTLINE_STYLE_DERIVATION_FAILED:" + styleDiagnostic, out diagnostic);
                }
                // TextMeshProUGUI.UpdateMeshPadding also calls TMP_SubMeshUI.UpdateMeshPadding
                // for each generated face. That call runs this same shader-ratio update
                // on the fallback material before the rendered slot is read back.
                TMPro.ShaderUtilities.GetPadding(profileOutput, owner.extraPadding, owner.isUsingBold);
                algorithm += "+native-static-text-outline-v1";
            }
            var transientFingerprint = MaterialFingerprint(binding.sourceMaterial);
            var sdkFingerprint = MaterialFingerprint(profileOutput);
            if (sdkOutput == null || String.IsNullOrEmpty(transientFingerprint) ||
                transientFingerprint != sdkFingerprint || profileOutput.GetTexture(MainTex) != binding.sourceTexture)
            {
                if (ownsProfileOutput) UnityEngine.Object.DestroyImmediate(profileOutput);
                return Fail("TMP_SORT_TRANSIENT_FALLBACK_DIFFERS_FROM_PINNED_SDK_OUTPUT", out diagnostic);
            }

            if (!PersistentAssetPath(persistentAssetPath, out diagnostic))
            {
                if (ownsProfileOutput) UnityEngine.Object.DestroyImmediate(profileOutput);
                return false;
            }
            var ownerFingerprint = MaterialFingerprint(sourceBase);
            var fallbackFingerprint = MaterialFingerprint(fallbackBase);
            if (String.IsNullOrEmpty(ownerFingerprint) || String.IsNullOrEmpty(fallbackFingerprint))
                return Fail("TMP_SORT_FALLBACK_BASE_MATERIAL_FINGERPRINT_UNAVAILABLE", out diagnostic);
            var baked = AssetDatabase.LoadAssetAtPath<Material>(persistentAssetPath);
            if (baked == null)
            {
                if (File.Exists(persistentAssetPath))
                {
                    if (ownsProfileOutput) UnityEngine.Object.DestroyImmediate(profileOutput);
                    return Fail("TMP_SORT_FALLBACK_BAKE_PATH_IS_OWNED_BY_NON_MATERIAL", out diagnostic);
                }
                var clone = new Material(profileOutput) { name = Path.GetFileNameWithoutExtension(persistentAssetPath), hideFlags = HideFlags.None };
                if (MaterialFingerprint(clone) != transientFingerprint)
                {
                    UnityEngine.Object.DestroyImmediate(clone);
                    if (ownsProfileOutput) UnityEngine.Object.DestroyImmediate(profileOutput);
                    return Fail("TMP_SORT_FALLBACK_BAKE_CLONE_CHANGED_SHADER_PROPERTIES", out diagnostic);
                }
                try { AssetDatabase.CreateAsset(clone, persistentAssetPath); }
                catch (Exception error)
                {
                    UnityEngine.Object.DestroyImmediate(clone);
                    if (ownsProfileOutput) UnityEngine.Object.DestroyImmediate(profileOutput);
                    return Fail("TMP_SORT_FALLBACK_BAKE_CREATE_ASSET_FAILED:" + error.GetType().Name, out diagnostic);
                }
                baked = AssetDatabase.LoadAssetAtPath<Material>(persistentAssetPath);
            }
            if (ownsProfileOutput) UnityEngine.Object.DestroyImmediate(profileOutput);
            var bakedFingerprint = MaterialFingerprint(baked);
            if (!PersistentAsset(baked, out var bakedGuid, out var bakedFileId) ||
                String.IsNullOrEmpty(bakedFingerprint) || bakedFingerprint != transientFingerprint)
                return Fail("TMP_SORT_PERSISTENT_FALLBACK_BAKE_DIFFERS_FROM_TRANSIENT_SDK_OUTPUT", out diagnostic);

            binding.proxyMaterial = baked;
            binding.proxyMaterialFingerprint = bakedFingerprint;
            binding.proxyMaterialGuid = bakedGuid;
            binding.proxyMaterialLocalFileId = bakedFileId;
            binding.proxyMaterialFingerprint = bakedFingerprint;
            binding.tmpFallbackMaterialBaked = true;
            binding.persistentFallbackVariantRegistered = false;
            binding.tmpFallbackAlgorithm = algorithm;
            binding.ownerFontMaterialFingerprint = ownerFingerprint;
            binding.fallbackFontMaterialFingerprint = fallbackFingerprint;
            binding.transientFallbackFingerprint = transientFingerprint;
            binding.bakedProxyMaterialFingerprint = bakedFingerprint;
            if (outlineDriver != null && fallbackFont != owner.font &&
                !outlineDriver.RegisterPersistentMaterialVariant(fallbackFont, baked, sourceBase, owner.fontSize,
                    binding.sourceTexture, out var persistentVariantDiagnostic))
                return Fail("TMP_SORT_FALLBACK_PERSISTENT_VARIANT_REGISTRATION_FAILED:" + persistentVariantDiagnostic, out diagnostic);
            if (outlineDriver != null && fallbackFont != owner.font)
            {
                binding.persistentFallbackVariantRegistered = true;
                EditorUtility.SetDirty(outlineDriver);
                PrefabUtility.RecordPrefabInstancePropertyModifications(outlineDriver);
            }
            return true;
        }

        static bool PersistentAssetPath(string value, out string diagnostic)
        {
            diagnostic = null;
            if (String.IsNullOrWhiteSpace(value) || !value.StartsWith("Assets/", StringComparison.Ordinal) ||
                value.Contains("\\") || value.Split('/').Any(part => part == ".." || part == ".") ||
                !String.Equals(Path.GetExtension(value), ".mat", StringComparison.OrdinalIgnoreCase))
                return Fail("TMP_SORT_FALLBACK_BAKE_PATH_UNSAFE", out diagnostic);
            var folder = Path.GetDirectoryName(value)?.Replace("\\", "/");
            if (String.IsNullOrEmpty(folder) || !AssetDatabase.IsValidFolder(folder))
                return Fail("TMP_SORT_FALLBACK_BAKE_FOLDER_NOT_OWNED", out diagnostic);
            return true;
        }

        public static NativeStaticSortTextSource Attach(GameObject proxy, TextSlotBinding binding,
            Mesh bakedProxyMesh, string expectedProxyMeshSha256)
        {
            if (proxy == null || binding == null || bakedProxyMesh == null ||
                binding.proxyMaterial == null || String.IsNullOrWhiteSpace(binding.proxyMaterialGuid) ||
                String.IsNullOrWhiteSpace(expectedProxyMeshSha256) ||
                MeshFingerprint(bakedProxyMesh) != expectedProxyMeshSha256 ||
                !IsValidTextSlotEnumeration(binding.textSlotEnumeration) ||
                binding.textSlotEnumeration.sourceComponentId != binding.sourceComponentId ||
                binding.textSlotEnumeration.sourceTextSha256 != binding.sourceTextSha256 ||
                binding.materialSlot < 0 || binding.materialSlot >= binding.textSlotEnumeration.rows.Length ||
                binding.textSlotEnumeration.rows[binding.materialSlot].disposition != "drawable")
                throw new InvalidOperationException("TMP_SORT_SOURCE_ATTACH_INPUT_INVALID");
            var identity = proxy.GetComponent<NativeStaticSortTextSource>() ?? proxy.AddComponent<NativeStaticSortTextSource>();
            identity.sourceComponentId = binding.sourceComponentId;
            identity.sourceOwner = binding.owner;
            identity.materialSlot = binding.materialSlot;
            identity.generatedSubmesh = binding.generatedSubmesh;
            identity.sourceGraphicEnabled = binding.sourceGraphicEnabled;
            identity.sourceGraphicActiveSelf = binding.sourceGraphicActiveSelf;
            identity.textSlotEnumeration = binding.textSlotEnumeration;
            identity.textInfoMaterialMissing = binding.textInfoMaterialMissing;
            identity.textInfoCharacterSlotVerified = binding.textInfoCharacterSlotVerified;
            identity.textInfoCharacterMaterialVerified = binding.textInfoCharacterMaterialVerified;
            identity.textInfoFontAssetVerified = binding.textInfoFontAssetVerified;
            identity.textInfoAtlasVerified = binding.textInfoAtlasVerified;
            identity.textInfoCharacterCount = binding.textInfoCharacterCount;
            identity.textInfoVisibleCharacterCount = binding.textInfoVisibleCharacterCount;
            identity.sourceTextSha256 = binding.sourceTextSha256;
            identity.textInfoCharacterEvidenceSha256 = binding.textInfoCharacterEvidenceSha256;
            identity.textInfoCharacterMaterialFingerprint = binding.textInfoCharacterMaterialFingerprint;
            identity.fontAsset = binding.fontAsset;
            identity.spriteAsset = binding.spriteAsset;
            identity.ownerFontSharedMaterial = binding.ownerFontSharedMaterial;
            identity.fallbackFontAsset = binding.fallbackFontAsset;
            identity.fallbackFontMaterial = binding.fallbackFontMaterial;
            identity.sourceMaterial = binding.tmpFallbackMaterialBaked ? null : binding.sourceMaterial;
            identity.proxyMaterial = binding.proxyMaterial;
            identity.sourceTexture = binding.sourceTexture;
            identity.tmpFallbackMaterialBaked = binding.tmpFallbackMaterialBaked;
            identity.persistentFallbackVariantRegistered = binding.persistentFallbackVariantRegistered;
            identity.tmpFallbackAlgorithm = binding.tmpFallbackAlgorithm;
            identity.tmpFallbackAtlasIndex = binding.tmpFallbackAtlasIndex;
            identity.ownerFontMaterialGuid = binding.ownerFontMaterialGuid;
            identity.ownerFontMaterialLocalFileId = binding.ownerFontMaterialLocalFileId;
            identity.ownerFontMaterialFingerprint = binding.ownerFontMaterialFingerprint;
            if (binding.ownerStyle != null)
            {
                identity.ownerStyleProfile = binding.ownerStyle.profile;
                identity.ownerStyleSourceComponentId = binding.ownerStyle.sourceComponentId;
                identity.ownerStyleOutlineWidth = binding.ownerStyle.outlineWidth;
                identity.ownerStyleOutlineColor = binding.ownerStyle.outlineColor;
                identity.ownerStyleSourceFontAsset = binding.ownerStyle.sourceFontAsset;
                identity.ownerStyleSourceFontAssetGuid = binding.ownerStyle.sourceFontAssetGuid;
                identity.ownerStyleSourceFontAssetLocalFileId = binding.ownerStyle.sourceFontAssetLocalFileId;
                identity.ownerStyleSourceFontMaterial = binding.ownerStyle.sourceFontMaterial;
                identity.ownerStyleSourceFontMaterialGuid = binding.ownerStyle.sourceFontMaterialGuid;
                identity.ownerStyleSourceFontMaterialLocalFileId = binding.ownerStyle.sourceFontMaterialLocalFileId;
                identity.ownerStyleSourceFontMaterialFingerprint = binding.ownerStyle.sourceFontMaterialFingerprint;
            }
            identity.fallbackFontAssetGuid = binding.fallbackFontAssetGuid;
            identity.fallbackFontAssetLocalFileId = binding.fallbackFontAssetLocalFileId;
            identity.fallbackFontMaterialGuid = binding.fallbackFontMaterialGuid;
            identity.fallbackFontMaterialLocalFileId = binding.fallbackFontMaterialLocalFileId;
            identity.fallbackFontMaterialFingerprint = binding.fallbackFontMaterialFingerprint;
            identity.fallbackAtlasGuid = binding.fallbackAtlasGuid;
            identity.fallbackAtlasLocalFileId = binding.fallbackAtlasLocalFileId;
            identity.transientFallbackFingerprint = binding.transientFallbackFingerprint;
            identity.bakedProxyMaterialFingerprint = binding.bakedProxyMaterialFingerprint;
            identity.bakedProxyMaterialGuid = binding.proxyMaterialGuid;
            identity.bakedProxyMaterialLocalFileId = binding.proxyMaterialLocalFileId;
            identity.fontAssetGuid = binding.fontAssetGuid; identity.fontAssetLocalFileId = binding.fontAssetLocalFileId;
            identity.spriteAssetGuid = binding.spriteAssetGuid; identity.spriteAssetLocalFileId = binding.spriteAssetLocalFileId;
            identity.sourceMaterialGuid = binding.sourceMaterialGuid; identity.sourceMaterialLocalFileId = binding.sourceMaterialLocalFileId;
            identity.sourceShaderGuid = binding.sourceShaderGuid; identity.sourceShaderLocalFileId = binding.sourceShaderLocalFileId;
            identity.sourceTextureGuid = binding.sourceTextureGuid; identity.sourceTextureLocalFileId = binding.sourceTextureLocalFileId;
            identity.sourceMaterialFingerprint = binding.sourceMaterialFingerprint;
            identity.sourceMeshSha256 = binding.sourceMeshSha256;
            AssetIdentity(bakedProxyMesh, out identity.proxyMeshGuid, out identity.proxyMeshLocalFileId);
            identity.proxyMeshSha256 = expectedProxyMeshSha256;
            EditorUtility.SetDirty(identity);
            return identity;
        }

        static bool ReadAssetsAndMesh(NativeStaticSortTextSource identity, Mesh bakedProxyMesh,
            TextSourceReadback readback)
        {
            if (identity == null || bakedProxyMesh == null) return false;
            readback.materialGuid = identity.sourceMaterialGuid;
            readback.materialLocalFileId = identity.sourceMaterialLocalFileId;
            readback.proxyMaterialGuid = identity.bakedProxyMaterialGuid;
            readback.proxyMaterialLocalFileId = identity.bakedProxyMaterialLocalFileId;
            readback.ownerFontMaterialGuid = identity.ownerFontMaterialGuid;
            readback.ownerFontMaterialLocalFileId = identity.ownerFontMaterialLocalFileId;
            readback.ownerStyleProfile = identity.ownerStyleProfile;
            readback.ownerStyleSourceComponentId = identity.ownerStyleSourceComponentId;
            readback.ownerStyleOutlineWidth = identity.ownerStyleOutlineWidth;
            readback.ownerStyleOutlineColor = identity.ownerStyleOutlineColor;
            readback.ownerStyleSourceFontAssetGuid = identity.ownerStyleSourceFontAssetGuid;
            readback.ownerStyleSourceFontAssetLocalFileId = identity.ownerStyleSourceFontAssetLocalFileId;
            readback.ownerStyleSourceFontMaterialGuid = identity.ownerStyleSourceFontMaterialGuid;
            readback.ownerStyleSourceFontMaterialLocalFileId = identity.ownerStyleSourceFontMaterialLocalFileId;
            readback.ownerStyleSourceFontMaterialFingerprint = identity.ownerStyleSourceFontMaterialFingerprint;
            readback.fallbackFontAssetGuid = identity.fallbackFontAssetGuid;
            readback.fallbackFontAssetLocalFileId = identity.fallbackFontAssetLocalFileId;
            readback.fallbackFontMaterialGuid = identity.fallbackFontMaterialGuid;
            readback.fallbackFontMaterialLocalFileId = identity.fallbackFontMaterialLocalFileId;
            readback.fallbackAtlasGuid = identity.fallbackAtlasGuid;
            readback.fallbackAtlasLocalFileId = identity.fallbackAtlasLocalFileId;
            readback.tmpFallbackAlgorithm = identity.tmpFallbackAlgorithm;
            readback.persistentFallbackVariantRegistered = identity.persistentFallbackVariantRegistered;
            readback.textSlotEnumeration = identity.textSlotEnumeration;
            readback.transientFallbackFingerprint = identity.transientFallbackFingerprint;
            readback.sourceMaterialFingerprint = identity.sourceMaterialFingerprint;
            readback.textInfoMaterialMissing = identity.textInfoMaterialMissing;
            readback.textInfoCharacterSlotVerified = identity.textInfoCharacterSlotVerified;
            readback.textInfoCharacterMaterialVerified = identity.textInfoCharacterMaterialVerified;
            readback.textInfoFontAssetVerified = identity.textInfoFontAssetVerified;
            readback.textInfoAtlasVerified = identity.textInfoAtlasVerified;
            readback.textInfoCharacterCount = identity.textInfoCharacterCount;
            readback.textInfoVisibleCharacterCount = identity.textInfoVisibleCharacterCount;
            readback.sourceTextSha256 = identity.sourceTextSha256;
            readback.textInfoCharacterEvidenceSha256 = identity.textInfoCharacterEvidenceSha256;
            readback.textInfoCharacterMaterialFingerprint = identity.textInfoCharacterMaterialFingerprint;
            readback.ownerFontMaterialFingerprint = identity.ownerFontMaterialFingerprint;
            readback.fallbackFontMaterialFingerprint = identity.fallbackFontMaterialFingerprint;
            readback.bakedProxyMaterialFingerprint = identity.bakedProxyMaterialFingerprint;
            readback.fontAssetVerified = identity.fontAsset == null
                ? String.IsNullOrEmpty(identity.fontAssetGuid) && identity.fontAssetLocalFileId == 0
                : SameIdentity(identity.fontAsset, identity.fontAssetGuid, identity.fontAssetLocalFileId,
                    out readback.fontAssetGuid, out readback.fontAssetLocalFileId);
            readback.spriteAssetVerified = identity.spriteAsset == null
                ? String.IsNullOrEmpty(identity.spriteAssetGuid) && identity.spriteAssetLocalFileId == 0
                : SameIdentity(identity.spriteAsset, identity.spriteAssetGuid, identity.spriteAssetLocalFileId,
                    out readback.spriteAssetGuid, out readback.spriteAssetLocalFileId);
            readback.ownerFontMaterialVerified = identity.ownerFontSharedMaterial != null &&
                SameIdentity(identity.ownerFontSharedMaterial, identity.ownerFontMaterialGuid, identity.ownerFontMaterialLocalFileId,
                    out readback.ownerFontMaterialGuid, out readback.ownerFontMaterialLocalFileId) &&
                MaterialFingerprint(identity.ownerFontSharedMaterial) == identity.ownerFontMaterialFingerprint;
            var hasOwnerStyle = !String.IsNullOrEmpty(identity.ownerStyleProfile);
            var styleFont = identity.ownerStyleSourceFontAsset;
            var styleBase = identity.ownerStyleSourceFontMaterial;
            var expectedStyleWidth = styleFont != null && styleBase != null && styleBase.HasProperty("_GradientScale") &&
                styleBase.GetFloat("_GradientScale") > 1f && identity.sourceOwner != null && identity.sourceOwner.fontSize > 0f
                    ? identity.ownerStyleOutlineWidth * styleFont.faceInfo.pointSize / identity.sourceOwner.fontSize /
                      (styleBase.GetFloat("_GradientScale") - 1f) : Single.NaN;
            readback.ownerStyleVerified = !hasOwnerStyle
                ? identity.ownerStyleSourceComponentId == null && styleFont == null && styleBase == null
                : identity.ownerStyleProfile == "native-static-text-outline-font-material-v1" &&
                  identity.ownerStyleSourceComponentId == identity.sourceComponentId && identity.sourceOwner != null &&
                  identity.sourceOwner.font == styleFont && PersistentAsset(styleFont, out var styleFontGuid, out var styleFontFileId) &&
                  styleFontGuid == identity.ownerStyleSourceFontAssetGuid && styleFontFileId == identity.ownerStyleSourceFontAssetLocalFileId &&
                  styleFont.material == styleBase && SameIdentity(styleBase, identity.ownerStyleSourceFontMaterialGuid,
                      identity.ownerStyleSourceFontMaterialLocalFileId, out _, out _) &&
                  MaterialFingerprint(styleBase) == identity.ownerStyleSourceFontMaterialFingerprint &&
                  !Single.IsNaN(expectedStyleWidth) && !Single.IsInfinity(expectedStyleWidth) &&
                  identity.ownerFontSharedMaterial != null && identity.ownerFontSharedMaterial.HasProperty("_OutlineWidth") &&
                  identity.ownerFontSharedMaterial.HasProperty("_OutlineColor") &&
                  Mathf.Approximately(identity.ownerFontSharedMaterial.GetFloat("_OutlineWidth"), expectedStyleWidth) &&
                  identity.ownerFontSharedMaterial.GetColor("_OutlineColor") == identity.ownerStyleOutlineColor &&
                  identity.sourceOwner.fontSharedMaterial == identity.ownerFontSharedMaterial &&
                  (!identity.ownerFontSharedMaterial.HasProperty("_FaceDilate") || !styleBase.HasProperty("_FaceDilate") ||
                   Mathf.Approximately(identity.ownerFontSharedMaterial.GetFloat("_FaceDilate"), styleBase.GetFloat("_FaceDilate")));
            readback.fallbackFontAssetVerified = identity.fallbackFontAsset == null
                ? String.IsNullOrEmpty(identity.fallbackFontAssetGuid) && identity.fallbackFontAssetLocalFileId == 0
                : SameIdentity(identity.fallbackFontAsset, identity.fallbackFontAssetGuid, identity.fallbackFontAssetLocalFileId,
                    out readback.fallbackFontAssetGuid, out readback.fallbackFontAssetLocalFileId);
            readback.fallbackFontMaterialVerified = identity.fallbackFontMaterial == null
                ? String.IsNullOrEmpty(identity.fallbackFontMaterialGuid) && identity.fallbackFontMaterialLocalFileId == 0
                : SameIdentity(identity.fallbackFontMaterial, identity.fallbackFontMaterialGuid, identity.fallbackFontMaterialLocalFileId,
                    out readback.fallbackFontMaterialGuid, out readback.fallbackFontMaterialLocalFileId) &&
                  MaterialFingerprint(identity.fallbackFontMaterial) == identity.fallbackFontMaterialFingerprint;
            var fallbackAtlas = identity.fallbackFontAsset != null && identity.fallbackFontAsset.atlasTextures != null &&
                identity.tmpFallbackAtlasIndex >= 0 && identity.tmpFallbackAtlasIndex < identity.fallbackFontAsset.atlasTextures.Length
                    ? identity.fallbackFontAsset.atlasTextures[identity.tmpFallbackAtlasIndex] : null;
            readback.fallbackAtlasVerified = !identity.tmpFallbackMaterialBaked ||
                (fallbackAtlas != null && fallbackAtlas == identity.sourceTexture &&
                 SameIdentity(fallbackAtlas, identity.fallbackAtlasGuid, identity.fallbackAtlasLocalFileId,
                     out readback.fallbackAtlasGuid, out readback.fallbackAtlasLocalFileId));
            readback.materialVerified = identity.tmpFallbackMaterialBaked
                ? identity.sourceMaterial == null && String.IsNullOrEmpty(identity.sourceMaterialGuid) &&
                  identity.sourceMaterialLocalFileId == 0 && IsSha256(identity.sourceMaterialFingerprint) &&
                  identity.sourceMaterialFingerprint == identity.transientFallbackFingerprint
                : SameIdentity(identity.sourceMaterial, identity.sourceMaterialGuid, identity.sourceMaterialLocalFileId,
                    out readback.materialGuid, out readback.materialLocalFileId) &&
                  MaterialFingerprint(identity.sourceMaterial) == identity.sourceMaterialFingerprint;
            var sourceShader = identity.proxyMaterial == null ? null : identity.proxyMaterial.shader;
            readback.shaderVerified = sourceShader != null && SameIdentity(sourceShader,
                identity.sourceShaderGuid, identity.sourceShaderLocalFileId, out readback.shaderGuid, out readback.shaderLocalFileId);
            var textureFromMaterial = identity.proxyMaterial == null ? null : identity.proxyMaterial.GetTexture(MainTex);
            readback.textureVerified = textureFromMaterial != null && textureFromMaterial == identity.sourceTexture &&
                SameIdentity(identity.sourceTexture, identity.sourceTextureGuid, identity.sourceTextureLocalFileId,
                    out readback.textureGuid, out readback.textureLocalFileId) &&
                TextureBelongsToSourceAsset(identity.fontAsset, identity.spriteAsset, identity.sourceTexture);
            readback.proxyMaterialVerified = SameIdentity(identity.proxyMaterial, identity.bakedProxyMaterialGuid,
                identity.bakedProxyMaterialLocalFileId, out readback.proxyMaterialGuid, out readback.proxyMaterialLocalFileId) &&
                MaterialFingerprint(identity.proxyMaterial) == identity.bakedProxyMaterialFingerprint &&
                identity.proxyMaterial.GetTexture(MainTex) == identity.sourceTexture;
            if (identity.tmpFallbackMaterialBaked)
            {
                var outlineSuffix = "+native-static-text-outline-v1";
                var hasOutlineSuffix = identity.tmpFallbackAlgorithm != null && identity.tmpFallbackAlgorithm.EndsWith(outlineSuffix, StringComparison.Ordinal);
                var baseAlgorithm = hasOutlineSuffix
                    ? identity.tmpFallbackAlgorithm.Substring(0, identity.tmpFallbackAlgorithm.Length - outlineSuffix.Length)
                    : identity.tmpFallbackAlgorithm;
                var knownAlgorithm = baseAlgorithm == "tmpro-fallback-font-material-v1" ||
                    baseAlgorithm == "tmpro-fallback-font-material-v1+tmpro-multi-atlas-v1" ||
                    baseAlgorithm == "tmpro-multi-atlas-v1";
                var fallbackAssetDiffers = identity.sourceOwner != null && identity.fallbackFontAsset != null &&
                    identity.fallbackFontAsset != identity.sourceOwner.font;
                knownAlgorithm = knownAlgorithm &&
                    (baseAlgorithm == "tmpro-fallback-font-material-v1" && fallbackAssetDiffers && identity.tmpFallbackAtlasIndex == 0 ||
                     baseAlgorithm == "tmpro-fallback-font-material-v1+tmpro-multi-atlas-v1" && fallbackAssetDiffers && identity.tmpFallbackAtlasIndex > 0 ||
                     baseAlgorithm == "tmpro-multi-atlas-v1" && !fallbackAssetDiffers && identity.tmpFallbackAtlasIndex > 0) &&
                    (!hasOutlineSuffix || !String.IsNullOrEmpty(identity.ownerStyleProfile)) &&
                    identity.persistentFallbackVariantRegistered == hasOutlineSuffix;
                readback.tmpFallbackDescriptorVerified = knownAlgorithm && readback.ownerFontMaterialVerified &&
                    readback.fallbackFontAssetVerified && readback.fallbackFontMaterialVerified && readback.fallbackAtlasVerified &&
                    IsSha256(identity.transientFallbackFingerprint) &&
                    identity.bakedProxyMaterialFingerprint == identity.transientFallbackFingerprint &&
                    identity.sourceMaterialFingerprint == identity.transientFallbackFingerprint;
                readback.proxyMaterialVerified = readback.proxyMaterialVerified &&
                    identity.bakedProxyMaterialFingerprint == identity.transientFallbackFingerprint;
            }
            else
            {
                readback.tmpFallbackDescriptorVerified = !identity.tmpFallbackMaterialBaked &&
                    identity.proxyMaterial == identity.sourceMaterial &&
                    identity.bakedProxyMaterialFingerprint == identity.sourceMaterialFingerprint;
                readback.proxyMaterialVerified = readback.proxyMaterialVerified &&
                    identity.bakedProxyMaterialFingerprint == identity.sourceMaterialFingerprint;
            }
            readback.transientFallbackVerified = !identity.tmpFallbackMaterialBaked ||
                (readback.tmpFallbackDescriptorVerified && identity.transientFallbackFingerprint == identity.bakedProxyMaterialFingerprint);
            readback.bakedProxyMeshVerified = PersistentAsset(bakedProxyMesh, out readback.proxyMeshGuid,
                out readback.proxyMeshLocalFileId) && readback.proxyMeshGuid == identity.proxyMeshGuid &&
                readback.proxyMeshLocalFileId == identity.proxyMeshLocalFileId &&
                MeshFingerprint(bakedProxyMesh) == identity.proxyMeshSha256;
            var sourceHashOK = IsSha256(identity.sourceMeshSha256);
            return readback.fontAssetVerified && readback.spriteAssetVerified && readback.materialVerified &&
                identity.textInfoCharacterSlotVerified && identity.textInfoCharacterMaterialVerified &&
                identity.textInfoFontAssetVerified && identity.textInfoAtlasVerified &&
                identity.textInfoCharacterCount > 0 && identity.textInfoVisibleCharacterCount > 0 &&
                IsSha256(identity.sourceTextSha256) && identity.sourceOwner != null &&
                HashText(identity.sourceOwner.text ?? String.Empty) == identity.sourceTextSha256 &&
                IsSha256(identity.textInfoCharacterEvidenceSha256) && IsSha256(identity.textInfoCharacterMaterialFingerprint) &&
                readback.ownerStyleVerified &&
                IsValidTextSlotEnumeration(identity.textSlotEnumeration) &&
                identity.textSlotEnumeration.sourceComponentId == identity.sourceComponentId &&
                identity.textSlotEnumeration.sourceTextSha256 == identity.sourceTextSha256 &&
                identity.materialSlot >= 0 && identity.materialSlot < identity.textSlotEnumeration.rows.Length &&
                identity.textSlotEnumeration.rows[identity.materialSlot].disposition == "drawable" &&
                readback.ownerFontMaterialVerified && readback.fallbackFontAssetVerified && readback.fallbackFontMaterialVerified &&
                readback.fallbackAtlasVerified && readback.tmpFallbackDescriptorVerified && readback.proxyMaterialVerified &&
                readback.shaderVerified && readback.textureVerified && readback.bakedProxyMeshVerified && sourceHashOK;
        }

        static bool IsSha256(string value)
        {
            return value != null && value.Length == 64 && value.All(Uri.IsHexDigit);
        }

        public static bool ReadPersistent(NativeStaticSortTextSource identity, Mesh bakedProxyMesh,
            TMP_Text expectedOwner, string expectedSourceComponentId, string expectedOwnerGuid,
            long expectedOwnerLocalFileId, out TextSourceReadback readback)
        {
            readback = new TextSourceReadback { diagnostic = "TMP_SORT_PERSISTENT_READBACK_FAILED" };
            if (identity == null || bakedProxyMesh == null) return false;
            readback.sourceComponentId = identity.sourceComponentId;
            readback.materialSlot = identity.materialSlot;
            readback.sourceMeshSha256 = identity.sourceMeshSha256;
            var ownerRefMatches = expectedOwner != null && identity.sourceOwner == expectedOwner &&
                identity.sourceComponentId == expectedSourceComponentId;
            var ownerAssetMatches = ownerRefMatches && AssetIdentity(expectedOwner, out readback.ownerGuid, out readback.ownerLocalFileId) &&
                readback.ownerGuid == expectedOwnerGuid && readback.ownerLocalFileId == expectedOwnerLocalFileId;
            readback.ownerScopeVerified = ownerAssetMatches;
            readback.persistentReferencesVerified = ownerAssetMatches &&
                AssetIdentity(identity, out var identityGuid, out var identityFileId) && identityFileId != 0;
            var resourcesVerified = ReadAssetsAndMesh(identity, bakedProxyMesh, readback);
            bool textInfoScopeVerified = false;
            string textInfoDiagnostic = null;
            if (readback.ownerScopeVerified && resourcesVerified)
            {
                if (!PrepareSource(expectedOwner, expectedSourceComponentId, out var prepareDiagnostic))
                    textInfoDiagnostic = prepareDiagnostic;
                else if (!GetCurrentSlots(expectedOwner, expectedSourceComponentId, out var currentSlots,
                    out var currentEnumeration, out var slotDiagnostic))
                    textInfoDiagnostic = slotDiagnostic;
                else
                {
                    readback.currentTextSlotEnumeration = currentEnumeration;
                    var current = currentSlots.SingleOrDefault(row => row.materialSlot == identity.materialSlot);
                    if (current == null) textInfoDiagnostic = "TMP_SORT_PERSISTENT_TEXTINFO_SLOT_MISSING:" + identity.materialSlot;
                    else
                    {
                        current.ownerStyle = OwnerStyleFromIdentity(identity);
                        textInfoScopeVerified = BindingMatchesIdentity(current, identity);
                        if (!textInfoScopeVerified) textInfoDiagnostic = "TMP_SORT_PERSISTENT_TEXTINFO_SLOT_PROOF_MISMATCH:" + identity.materialSlot;
                    }
                }
            }
            readback.generatedSlotResolved = textInfoScopeVerified;
            readback.verified = readback.ownerScopeVerified && readback.persistentReferencesVerified && resourcesVerified && textInfoScopeVerified;
            readback.diagnostic = readback.verified ? null : "TMP_SORT_PERSISTENT_OWNER_SCOPE_OR_ASSET_MATERIAL_ATLAS_MESH_MISMATCH" +
                (String.IsNullOrEmpty(textInfoDiagnostic) ? "" : ";textInfo=" + textInfoDiagnostic);
            return readback.verified;
        }

        public static bool ResolveGeneratedSlot(NativeStaticSortTextSource identity, TMP_Text expectedOwner,
            string expectedSourceComponentId, out TextSlotBinding binding, out string diagnostic)
        {
            binding = null; diagnostic = null;
            if (identity == null || expectedOwner == null || identity.sourceOwner != expectedOwner ||
                identity.sourceComponentId != expectedSourceComponentId)
                return Fail("TMP_SORT_GENERATED_OWNER_SCOPE_MISMATCH", out diagnostic);
            if (!GetCurrentSlots(expectedOwner, expectedSourceComponentId, out var currentSlots,
                out var currentEnumeration, out diagnostic)) return false;
            binding = currentSlots.SingleOrDefault(candidate => candidate.materialSlot == identity.materialSlot);
            if (binding == null)
                return Fail("TMP_SORT_GENERATED_SLOT_NOT_UNIQUE:" + identity.materialSlot + ":0", out diagnostic);
            if (currentEnumeration == null || binding.textSlotEnumeration == null ||
                currentEnumeration.evidenceSha256 != binding.textSlotEnumeration.evidenceSha256)
                return Fail("TMP_SORT_GENERATED_SLOT_ENUMERATION_BINDING_MISMATCH:" + identity.materialSlot, out diagnostic);
            binding.ownerStyle = OwnerStyleFromIdentity(identity);
            if (!BindingMatchesIdentity(binding, identity))
            {
                binding = null;
                return Fail("TMP_SORT_GENERATED_SLOT_RESOURCE_IDENTITY_CHANGED:" + identity.materialSlot, out diagnostic);
            }
            return true;
        }

        public static bool ReadInitialized(NativeStaticSortTextSource identity, Mesh bakedProxyMesh,
            TMP_Text expectedOwner, string expectedSourceComponentId, out TextSourceReadback readback)
        {
            readback = new TextSourceReadback { diagnostic = "TMP_SORT_INITIALIZED_READBACK_FAILED" };
            if (identity == null || bakedProxyMesh == null || expectedOwner == null) return false;
            readback.sourceComponentId = identity.sourceComponentId;
            readback.materialSlot = identity.materialSlot;
            readback.sourceMeshSha256 = identity.sourceMeshSha256;
            readback.ownerScopeVerified = identity.sourceOwner == expectedOwner &&
                identity.sourceComponentId == expectedSourceComponentId;
            readback.persistentReferencesVerified = readback.ownerScopeVerified;
            var resourcesVerified = ReadAssetsAndMesh(identity, bakedProxyMesh, readback);
            if (!readback.ownerScopeVerified || !resourcesVerified)
            {
                readback.diagnostic = "TMP_SORT_INITIALIZED_OWNER_SCOPE_OR_ASSET_MATERIAL_ATLAS_MESH_MISMATCH";
                return false;
            }
            if (!PrepareSource(expectedOwner, expectedSourceComponentId, out var prepareDiagnostic))
            {
                readback.diagnostic = prepareDiagnostic;
                return false;
            }
            if (!ResolveGeneratedSlot(identity, expectedOwner, expectedSourceComponentId, out var binding, out var diagnostic))
            {
                readback.generatedSlotResolved = false;
                readback.diagnostic = diagnostic;
                return false;
            }
            readback.generatedSlotResolved = true;
            readback.currentTextSlotEnumeration = binding.textSlotEnumeration;
            readback.sourceStateVerified = binding.sourceGraphicEnabled == identity.sourceGraphicEnabled &&
                binding.sourceGraphicActiveSelf == identity.sourceGraphicActiveSelf;
            readback.sourceMeshVerified = binding.sourceMeshSha256 == identity.sourceMeshSha256;
            readback.actualTransientMaterialFingerprint = MaterialFingerprint(binding.sourceMaterial);
            readback.transientFallbackVerified = identity.tmpFallbackMaterialBaked
                ? readback.actualTransientMaterialFingerprint == identity.transientFallbackFingerprint &&
                  readback.tmpFallbackDescriptorVerified
                : readback.actualTransientMaterialFingerprint == identity.sourceMaterialFingerprint;
            readback.verified = readback.ownerScopeVerified && resourcesVerified && readback.generatedSlotResolved &&
                readback.sourceStateVerified && readback.sourceMeshVerified && readback.transientFallbackVerified;
            readback.diagnostic = readback.verified ? null : "TMP_SORT_INITIALIZED_SLOT_STATE_OR_MESH_CHANGED";
            return readback.verified;
        }

        static bool BindingMatchesIdentity(TextSlotBinding binding, NativeStaticSortTextSource identity)
        {
            var sourceMaterialMatches = binding != null && identity != null &&
                (identity.tmpFallbackMaterialBaked
                    ? identity.persistentFallbackVariantRegistered
                        ? binding.sourceMaterial != null && binding.sourceMaterial == identity.proxyMaterial &&
                          (binding.sourceMaterialGuid == null && binding.sourceMaterialLocalFileId == 0 ||
                           binding.sourceMaterialGuid == identity.bakedProxyMaterialGuid &&
                           binding.sourceMaterialLocalFileId == identity.bakedProxyMaterialLocalFileId) &&
                          binding.sourceMaterialFingerprint == identity.transientFallbackFingerprint &&
                          PersistentAsset(binding.sourceMaterial, out var currentSourceGuid, out var currentSourceFileId) &&
                          currentSourceGuid == identity.bakedProxyMaterialGuid && currentSourceFileId == identity.bakedProxyMaterialLocalFileId
                        : binding.sourceMaterial != null && !PersistentAsset(binding.sourceMaterial, out _, out _) &&
                          binding.sourceMaterialGuid == null && binding.sourceMaterialLocalFileId == 0 &&
                          binding.sourceMaterialFingerprint == identity.transientFallbackFingerprint
                    : binding.sourceMaterialGuid == identity.sourceMaterialGuid &&
                      binding.sourceMaterialLocalFileId == identity.sourceMaterialLocalFileId &&
                      binding.sourceMaterialFingerprint == identity.sourceMaterialFingerprint);
            return binding != null && identity != null && sourceMaterialMatches && binding.owner == identity.sourceOwner &&
                binding.sourceComponentId == identity.sourceComponentId && binding.materialSlot == identity.materialSlot &&
                binding.persistentFallbackVariantRegistered == identity.persistentFallbackVariantRegistered &&
                binding.generatedSubmesh == identity.generatedSubmesh &&
                binding.textInfoMaterialMissing == identity.textInfoMaterialMissing &&
                binding.textInfoCharacterSlotVerified == identity.textInfoCharacterSlotVerified &&
                binding.textInfoCharacterMaterialVerified == identity.textInfoCharacterMaterialVerified &&
                binding.textInfoFontAssetVerified == identity.textInfoFontAssetVerified &&
                binding.textInfoAtlasVerified == identity.textInfoAtlasVerified &&
                binding.textInfoCharacterCount == identity.textInfoCharacterCount &&
                binding.textInfoVisibleCharacterCount == identity.textInfoVisibleCharacterCount &&
                binding.sourceTextSha256 == identity.sourceTextSha256 &&
                binding.textSlotEnumeration != null && identity.textSlotEnumeration != null &&
                binding.textSlotEnumeration.sourceComponentId == identity.textSlotEnumeration.sourceComponentId &&
                binding.textSlotEnumeration.sourceTextSha256 == identity.textSlotEnumeration.sourceTextSha256 &&
                binding.textSlotEnumeration.slotCount == identity.textSlotEnumeration.slotCount &&
                binding.textSlotEnumeration.verified && identity.textSlotEnumeration.verified &&
                binding.textSlotEnumeration.evidenceSha256 == identity.textSlotEnumeration.evidenceSha256 &&
                binding.textInfoCharacterEvidenceSha256 == identity.textInfoCharacterEvidenceSha256 &&
                binding.textInfoCharacterMaterialFingerprint == identity.textInfoCharacterMaterialFingerprint &&
                binding.fontAssetGuid == identity.fontAssetGuid && binding.fontAssetLocalFileId == identity.fontAssetLocalFileId &&
                binding.spriteAssetGuid == identity.spriteAssetGuid && binding.spriteAssetLocalFileId == identity.spriteAssetLocalFileId &&
                binding.ownerFontMaterialGuid == identity.ownerFontMaterialGuid &&
                binding.ownerFontMaterialLocalFileId == identity.ownerFontMaterialLocalFileId &&
                binding.ownerFontMaterialFingerprint == identity.ownerFontMaterialFingerprint &&
                (identity.ownerStyleProfile == null ? binding.ownerStyle == null :
                 binding.ownerStyle != null && binding.ownerStyle.profile == identity.ownerStyleProfile &&
                 binding.ownerStyle.sourceComponentId == identity.ownerStyleSourceComponentId &&
                 binding.ownerStyle.sourceFontAssetGuid == identity.ownerStyleSourceFontAssetGuid &&
                 binding.ownerStyle.sourceFontMaterialGuid == identity.ownerStyleSourceFontMaterialGuid) &&
                binding.fallbackFontAssetGuid == identity.fallbackFontAssetGuid &&
                binding.fallbackFontAssetLocalFileId == identity.fallbackFontAssetLocalFileId &&
                binding.fallbackFontMaterialGuid == identity.fallbackFontMaterialGuid &&
                binding.fallbackFontMaterialLocalFileId == identity.fallbackFontMaterialLocalFileId &&
                binding.fallbackFontMaterialFingerprint == identity.fallbackFontMaterialFingerprint &&
                binding.sourceShaderGuid == identity.sourceShaderGuid && binding.sourceShaderLocalFileId == identity.sourceShaderLocalFileId &&
                binding.sourceTextureGuid == identity.sourceTextureGuid && binding.sourceTextureLocalFileId == identity.sourceTextureLocalFileId;
        }

        static OwnerFontStyleDescriptor OwnerStyleFromIdentity(NativeStaticSortTextSource identity)
        {
            if (identity == null || String.IsNullOrEmpty(identity.ownerStyleProfile)) return null;
            return new OwnerFontStyleDescriptor {
                profile = identity.ownerStyleProfile,
                sourceComponentId = identity.ownerStyleSourceComponentId,
                outlineWidth = identity.ownerStyleOutlineWidth,
                outlineColor = identity.ownerStyleOutlineColor,
                sourceFontAsset = identity.ownerStyleSourceFontAsset,
                sourceFontAssetGuid = identity.ownerStyleSourceFontAssetGuid,
                sourceFontAssetLocalFileId = identity.ownerStyleSourceFontAssetLocalFileId,
                sourceFontMaterial = identity.ownerStyleSourceFontMaterial,
                sourceFontMaterialGuid = identity.ownerStyleSourceFontMaterialGuid,
                sourceFontMaterialLocalFileId = identity.ownerStyleSourceFontMaterialLocalFileId,
                sourceFontMaterialFingerprint = identity.ownerStyleSourceFontMaterialFingerprint,
            };
        }

        static bool IsGeneratedSubmesh(TMP_SubMeshUI child, TMP_Text owner)
        {
            if (child == null || owner == null || child.transform.parent != owner.transform ||
                child.transform.childCount != 0 || !(child.transform is RectTransform) ||
                (child.gameObject.hideFlags & HideFlags.DontSave) != HideFlags.DontSave ||
                child.textComponent != owner) return false;
            if (child.GetComponent<LayoutElement>() is LayoutElement layout && !layout.ignoreLayout) return false;
            return true;
        }

        static bool Fail(string message, out string diagnostic)
        {
            diagnostic = message;
            return false;
        }
    }
}
