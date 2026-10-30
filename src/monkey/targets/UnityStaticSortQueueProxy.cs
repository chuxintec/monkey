using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.UI;
using Monkey.StaticMaskSort;
using Monkey.StaticSortQueue;

namespace Monkey.StaticSortQueueProxy
{
    [Serializable] public sealed class ProxyRendererSpec
    {
        public string node, sourceComponentId, sourceType, expectedGraphicType;
        public float sourceSortOrder;
        public int sourceQueueIndex;
        public bool sourceEnabled, sourceActive, sourceTextureBound, sourceTextEmpty, sourceFontMissing;
        public string sourceText, nativeTextExpectation, sourceFieldsJson, sourceFieldsSha256, sourceDrawingCommands;
        public string[] sourceMaterialGuids;
        public bool sourceCommandsEmpty;
    }
    [Serializable] public sealed class ProxyMaskSpec
    {
        public string node, sourceId, nativeId, spriteFrameUuid, sourceFieldsJson;
        public int maskType;
        public bool inverted, enabled, convertible;
        public float alphaThreshold;
        public string sourceMaterialId, resolvedSourceMaterialId, sourceEffectId, sourceEffectName,
            sourceEffectDocumentSha256, unityMaskShaderPath, unityMaskShaderSha256,
            unityMaskMaterialGuid, unityMaskMaterialPath;
    }
    [Serializable] public sealed class ProxyDrawEventSpec
    {
        public string kind, node, sourceComponentId;
    }
    [Serializable] public sealed class ProxySortRootFieldSpec
    {
        public string sourceId, nativeId, node;
        public bool enabled;
    }
    [Serializable] public sealed class ProxySourceChildrenSpec
    {
        public string node;
        public string[] children;
    }
    [Serializable] public sealed class ProxySourceActiveSpec
    {
        public string node;
        public bool active;
    }
    [Serializable] public sealed class ProxyQueueSpec
    {
        public string rootScope, sourcePrefabId, prefabPath, meshAssetFolder, sourceManifestSha256;
        public ProxyRendererSpec[] renderers;
        public ProxyMaskSpec[] masks;
        public ProxyDrawEventSpec[] drawEvents;
        public QueueSortFieldSpec[] sourceFields;
        public ProxySortRootFieldSpec[] sourceSortRoots;
        public ProxySourceChildrenSpec[] sourceChildOrder;
        public ProxySourceActiveSpec[] sourceNodeActive;
        public ProxyRendererSpec[] nonDrawRenderers;
    }
    [Serializable] public sealed class ProxyPresenterReadback
    {
        public string sourceComponentId, sourceNode, nativeGraphicType, sourceMeshSha256, proxyMeshSha256, renderedMeshSha256,
            capturedSourceMeshSha256, meshContentSha256, meshAssetGuid, materialGuid, textureGuid;
        public int submeshIndex, vertexCount, sourceQueueIndex, textMaterialSlot;
        public int sourceVertexCount, persistedProxyVertexCount;
        public int[] sourceUvChannelVertexCounts, proxyUvChannelVertexCounts, renderedUvChannelVertexCounts;
        public int[] sourceUvChannelDimensions, proxyUvChannelDimensions, renderedUvChannelDimensions;
        public float sourceRendererAlpha, proxyRendererAlpha, sourceInheritedAlpha, proxyInheritedAlpha,
            sourceEffectiveAlpha, proxyEffectiveAlpha, maxWorldVertexError, maxWorldNormalError, maxWorldTangentError;
        public bool sourceGraphicEnabled, sourceCulled, proxyVisible, generatedSourceChild,
            staticSnapshotVerified, transformedGeometryVerified, runtimeMeshVerified, opacityVerified, verified,
            transformedTopologyMatches, transformedUvMatches, transformedColorsMatch, transformedNormalsMatch,
            transformedTangentsMatch;
    }
    [Serializable] public sealed class ProxySpineOwnerDelegationReadback
    {
        public string sourceComponentId, sourceNode, sourceGraphicType, sourceIdentityComponentId, sourceDataAssetId,
            sourceDataAssetPath, sourceDataAssetGuid, sourceBindingPlanPath,
            sourceBindingPlanSha256, sourceManifestSha256;
        public int rootMeshVertexCount, rootMeshSubmeshCount, rootCanvasMaterialCount;
        public string[] delegatedChildPaths, delegatedChildGraphicTypes, delegatedChildTextureGuids,
            delegatedChildMaterialGuids;
        public int[] childMeshVertexCounts, childMeshSubmeshCounts, childCanvasMaterialCounts;
        public bool rootMeshWasMissing, sourceIdentityVerified, sourceDataReferenceVerified, rootMeshDelegated,
            childRendererListVerified, childReferencesPersistent, verified;
    }
    [Serializable] public sealed class ProxySpineNonDrawChildReadback
    {
        public string sourceComponentId, sourceNode, noDrawReason, sourceIdentityComponentId, sourceDataAssetId,
            sourceDataAssetPath, sourceDataAssetGuid, childPath, childGraphicType, childMaterialGuid, childTextureGuid;
        public bool sourceOwnerEnabled, sourceNodeActive, sourceChildEnabled, sourceChildActiveSelf,
            sourceChildActiveInHierarchy, targetChildEnabled, targetChildActiveInHierarchy,
            sourceIdentityVerified, sourceDataReferenceVerified, registeredChildVerified,
            childReferencePersistent, childNoDrawVerified, verified;
        public int sourceChildMeshVertexCount, sourceChildMeshSubmeshCount, sourceChildMaterialCount;
    }
    [Serializable] public sealed class ProxyQueueReadback
    {
        public string rootScope, proxyRootName;
        public bool sourceTreePreserved, sourceFieldsPreserved, sourceSortRootsPreserved, nestedProxyRootsDisabled,
            drawSequenceVerified, verified;
        public string diagnostic, readbackMode;
        public string[] spineDelegationDiagnostics, spineNonDrawChildDiagnostics;
        public bool provisional, persistentSnapshotVerified, initializedPresentationVerified, runtimeGeometryDeferred;
        public bool sourceGraphicsCovered, layoutIgnored, spineDelegationsVerified, spineNonDrawChildrenVerified;
        public bool textSourcesVerified;
        public bool sourceMaskReferencesVerified;
        public string[] structuralDiagnostics;
        public ProxyPresenterReadback[] graphics;
        public ProxyTextSourceReadback[] textSources;
        public ProxySpineOwnerDelegationReadback[] spineOwnerDelegations;
        public ProxySpineNonDrawChildReadback[] spineNonDrawChildren;
        public ProxyEmptyRendererReadback[] emptyRenderers;
        public ProxyMaskReadback[] masks;
        public ProxySortFieldReadback[] sourceFields;
        public ProxySortRootValueReadback[] sourceSortRoots;
        public string[] maskSourceIds;
    }
    [Serializable] public sealed class ProxyTextSourceReadback
    {
        public string sourceNode, readbackMode, sourceComponentId;
        public int materialSlot;
        public TextSourceReadback evidence;
    }
    [Serializable] public sealed class ProxyEmptyRendererReadback
    {
        public string sourceComponentId, sourceNode, sourceType, noDrawReason, carrierGuid;
        public string sourceComponentType, sourceFieldsSha256, sourceDrawingCommands, sourceText, nativeTextExpectation, nativeText;
        public string[] sourceMaterialGuids, actualSourceMaterialGuids;
        public long carrierLocalFileId;
        public bool sourceEnabled, sourceActive, nativeGraphicEnabled, nativeComponentEnabled, sourceActiveInHierarchy,
            sourceTextureBound, nativeTextureBound, sourceTextEmpty, nativeTextEmpty,
            sourceFontMissing, nativeFontMissing, sourceMeshPresent, carrierPresent,
            sourceReferenceVerified, typedFieldsVerified, sourceCommandsEmpty, nativeCommandsEmpty, verified;
        public int sourceMeshVertexCount, sourceCanvasMaterialCount, actualQueueIndex;
    }
    [Serializable] public sealed class ProxySortFieldReadback
    {
        public string sourceId, node, nativeId, actualSourceId, actualNativeId;
        public float sourceSortOrder, actualSortOrder;
        public bool enabledInSource, actualEnabledInSource, identityPresent, identityComponentEnabled, verified;
    }
    [Serializable] public sealed class ProxySortRootValueReadback
    {
        public string sourceId, node, nativeId, actualSourceId, actualNativeId;
        public bool enabledInSource, actualEnabledInSource, identityPresent, identityComponentEnabled, verified;
    }
    [Serializable] public sealed class ProxyMaskReadback
    {
        public string sourceId, sourceNode, nativeMaskType;
        public int sourceMaskType;
        public bool inverted, enabled, sourceTransformVerified, verified;
        public bool maskPresent, identityPresent, graphicPresent, graphicTypeMatches, sourceIdentityMatches,
            sourceFieldsMatches, maskEnabledMatches, maskGraphicHidden, graphicEnabledMatches, graphicRaycastDisabled,
            sourceMaterialMatches, resolvedSourceMaterialMatches, sourceEffectMatches, alphaThresholdMatches,
            invertedCanvasMatches;
        public string[] failedChecks;
        public float alphaThreshold;
    }

    public static class UnityStaticSortQueueProxy
    {
        static string HashBytes(byte[] bytes)
        {
            using (var sha = SHA256.Create())
                return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant();
        }
        static string HashText(string value) => HashBytes(Encoding.UTF8.GetBytes(value ?? ""));

        static string MaterialFingerprint(Material material)
        {
            if (material == null) return null;
            var shader = material.shader;
            if (shader == null || !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(shader, out var shaderGuid, out long shaderFileId) ||
                string.IsNullOrEmpty(shaderGuid))
                throw new InvalidOperationException("STATIC_SORT_PROXY_SHADER_GUID_MISSING: " + material.name);
            var sb = new StringBuilder();
            sb.Append("shader=").Append(shaderGuid).Append(':').Append(shaderFileId)
              .Append("|queue=").Append(material.renderQueue)
              .Append("|instancing=").Append(material.enableInstancing)
              .Append("|doubleSidedGI=").Append(material.doubleSidedGI)
              .Append("|giFlags=").Append((int)material.globalIlluminationFlags)
              .Append("|keywords=").Append(string.Join(",", material.shaderKeywords.OrderBy(x => x, StringComparer.Ordinal)));
            for (var index = 0; index < shader.GetPropertyCount(); index++)
            {
                var name = shader.GetPropertyName(index);
                var type = shader.GetPropertyType(index);
                sb.Append("|p=").Append(name).Append(':').Append(type).Append('=');
                if (type == UnityEngine.Rendering.ShaderPropertyType.Color)
                {
                    var value = material.GetColor(name);
                    sb.Append(value.r.ToString("R", CultureInfo.InvariantCulture)).Append(',')
                      .Append(value.g.ToString("R", CultureInfo.InvariantCulture)).Append(',')
                      .Append(value.b.ToString("R", CultureInfo.InvariantCulture)).Append(',')
                      .Append(value.a.ToString("R", CultureInfo.InvariantCulture));
                }
                else if (type == UnityEngine.Rendering.ShaderPropertyType.Vector)
                    AppendVector(sb, material.GetVector(name));
                else if (type == UnityEngine.Rendering.ShaderPropertyType.Texture)
                {
                    var texture = material.GetTexture(name);
                    if (texture == null) sb.Append("null");
                    else if (texture == Texture2D.whiteTexture) sb.Append("builtin:white");
                    else
                    {
                        if (!AssetDatabase.TryGetGUIDAndLocalFileIdentifier(texture, out var textureGuid, out long textureFileId) ||
                            string.IsNullOrEmpty(textureGuid))
                            throw new InvalidOperationException("STATIC_SORT_PROXY_MATERIAL_TEXTURE_GUID_MISSING: " + name);
                        sb.Append(textureGuid).Append(':').Append(textureFileId);
                    }
                    var scale = material.GetTextureScale(name); var offset = material.GetTextureOffset(name);
                    sb.Append(";scale=").Append(scale.x.ToString("R", CultureInfo.InvariantCulture)).Append(',')
                      .Append(scale.y.ToString("R", CultureInfo.InvariantCulture))
                      .Append(";offset=").Append(offset.x.ToString("R", CultureInfo.InvariantCulture)).Append(',')
                      .Append(offset.y.ToString("R", CultureInfo.InvariantCulture));
                }
                else if (type == UnityEngine.Rendering.ShaderPropertyType.Int)
                    sb.Append(material.GetInt(name));
                else
                    sb.Append(material.GetFloat(name).ToString("R", CultureInfo.InvariantCulture));
            }
            return HashText(sb.ToString());
        }

        static void AppendVector(StringBuilder sb, Vector4 value)
        {
            sb.Append(value.x.ToString("R", CultureInfo.InvariantCulture)).Append(',')
              .Append(value.y.ToString("R", CultureInfo.InvariantCulture)).Append(',')
              .Append(value.z.ToString("R", CultureInfo.InvariantCulture)).Append(',')
              .Append(value.w.ToString("R", CultureInfo.InvariantCulture)).Append(';');
        }

        static int UvDimension(Mesh mesh, int channel)
        {
            if (mesh == null || channel < 0 || channel > 7) return 0;
            var attribute = (VertexAttribute)((int)VertexAttribute.TexCoord0 + channel);
            return mesh.HasVertexAttribute(attribute) ? mesh.GetVertexAttributeDimension(attribute) : 0;
        }

        static int[] UvChannelVertexCounts(Mesh mesh)
        {
            var result = new int[8];
            if (mesh == null) return result;
            for (var channel = 0; channel < result.Length; channel++)
            {
                var values = new List<Vector4>(); mesh.GetUVs(channel, values);
                result[channel] = values.Count;
            }
            return result;
        }

        static int[] UvChannelDimensions(Mesh mesh)
        {
            var result = new int[8];
            if (mesh == null) return result;
            for (var channel = 0; channel < result.Length; channel++) result[channel] = UvDimension(mesh, channel);
            return result;
        }

        static bool HasMalformedUvChannels(Mesh mesh)
        {
            if (mesh == null) return true;
            var counts = UvChannelVertexCounts(mesh);
            var dimensions = UvChannelDimensions(mesh);
            for (var channel = 0; channel < counts.Length; channel++)
            {
                if (counts[channel] != 0 && counts[channel] != mesh.vertexCount) return true;
                if (counts[channel] != 0 && (dimensions[channel] < 2 || dimensions[channel] > 4)) return true;
            }
            return false;
        }

        static void CopyUvChannels(Mesh source, Mesh target)
        {
            for (var channel = 0; channel < 8; channel++)
            {
                switch (UvDimension(source, channel))
                {
                    case 0: break;
                    case 2:
                    {
                        var values = new List<Vector2>(); source.GetUVs(channel, values);
                        if (values.Count != source.vertexCount) throw new InvalidOperationException("STATIC_SORT_PROXY_UV_CHANNEL_VERTEX_COUNT_MISMATCH:" + channel);
                        target.SetUVs(channel, values); break;
                    }
                    case 3:
                    {
                        var values = new List<Vector3>(); source.GetUVs(channel, values);
                        if (values.Count != source.vertexCount) throw new InvalidOperationException("STATIC_SORT_PROXY_UV_CHANNEL_VERTEX_COUNT_MISMATCH:" + channel);
                        target.SetUVs(channel, values); break;
                    }
                    case 4:
                    {
                        var values = new List<Vector4>(); source.GetUVs(channel, values);
                        if (values.Count != source.vertexCount) throw new InvalidOperationException("STATIC_SORT_PROXY_UV_CHANNEL_VERTEX_COUNT_MISMATCH:" + channel);
                        target.SetUVs(channel, values); break;
                    }
                    default: throw new InvalidOperationException("STATIC_SORT_PROXY_UV_DIMENSION_UNSUPPORTED:" + channel);
                }
            }
        }

        static string MeshFingerprint(Mesh mesh, int submesh)
        {
            var sb = new StringBuilder();
            sb.Append(mesh.vertexCount).Append('|').Append(mesh.subMeshCount).Append('|').Append(submesh).Append('|');
            foreach (var p in mesh.vertices) AppendVector(sb, p);
            foreach (var c in mesh.colors32) sb.Append(c.r).Append(',').Append(c.g).Append(',').Append(c.b).Append(',').Append(c.a).Append(';');
            for (var channel = 0; channel < 8; channel++)
            {
                var values = new List<Vector4>(); mesh.GetUVs(channel, values);
                sb.Append('#').Append(channel).Append('/').Append(UvDimension(mesh, channel)).Append(':');
                foreach (var uv in values) AppendVector(sb, uv);
            }
            foreach (var n in mesh.normals) AppendVector(sb, n);
            foreach (var t in mesh.tangents) AppendVector(sb, t);
            foreach (var index in mesh.GetTriangles(submesh)) sb.Append(index).Append(',');
            return HashText(sb.ToString());
        }

        static bool TransformedMeshMatches(Mesh source, int submesh, Transform sourceTransform,
            Transform proxyTransform, Mesh persistedProxy)
        {
            if (source == null || sourceTransform == null || proxyTransform == null || persistedProxy == null) return false;
            var expected = SnapshotSubmesh(source, submesh, sourceTransform, proxyTransform);
            var matches = MeshFingerprint(expected, 0) == MeshFingerprint(persistedProxy, 0);
            UnityEngine.Object.DestroyImmediate(expected);
            return matches;
        }

        sealed class TransformedMeshDiagnostics
        {
            public float maxWorldVertexError, maxWorldNormalError, maxWorldTangentError;
            public bool topologyMatches, uvMatches, colorsMatch, normalsMatch, tangentsMatch;
        }

        static TransformedMeshDiagnostics MeasureTransformedMesh(Mesh source, int submesh, Transform sourceTransform,
            Transform proxyTransform, Mesh persistedProxy)
        {
            var result = new TransformedMeshDiagnostics();
            if (source == null || persistedProxy == null || sourceTransform == null || proxyTransform == null ||
                submesh < 0 || submesh >= source.subMeshCount) return result;
            var sourceVertices = source.vertices; var proxyVertices = persistedProxy.vertices;
            if (sourceVertices.Length == proxyVertices.Length)
            {
                result.maxWorldVertexError = 0f;
                for (var index = 0; index < sourceVertices.Length; index++)
                    result.maxWorldVertexError = Mathf.Max(result.maxWorldVertexError,
                        Vector3.Distance(sourceTransform.TransformPoint(sourceVertices[index]),
                            proxyTransform.TransformPoint(proxyVertices[index])));
            }
            result.topologyMatches = sourceVertices.Length == proxyVertices.Length && persistedProxy.subMeshCount == 1 &&
                source.GetTriangles(submesh).SequenceEqual(persistedProxy.GetTriangles(0));
            result.uvMatches = true;
            for (var channel = 0; channel < 8; channel++)
            {
                if (UvDimension(source, channel) != UvDimension(persistedProxy, channel))
                { result.uvMatches = false; break; }
                var sourceUvs = new List<Vector4>(); var proxyUvs = new List<Vector4>();
                source.GetUVs(channel, sourceUvs); persistedProxy.GetUVs(channel, proxyUvs);
                if (!sourceUvs.SequenceEqual(proxyUvs)) { result.uvMatches = false; break; }
            }
            var sourceColors = source.colors32; var proxyColors = persistedProxy.colors32;
            result.colorsMatch = sourceColors.SequenceEqual(proxyColors);
            var sourceNormals = source.normals; var proxyNormals = persistedProxy.normals;
            result.normalsMatch = sourceNormals.Length == proxyNormals.Length;
            if (result.normalsMatch && sourceNormals.Length == sourceVertices.Length)
            {
                result.maxWorldNormalError = 0f;
                var sourceMatrix = sourceTransform.localToWorldMatrix;
                var proxyMatrix = proxyTransform.localToWorldMatrix;
                var sourceNormalMatrix = Mathf.Abs(sourceMatrix.determinant) > 1e-8f ? sourceMatrix.inverse.transpose : Matrix4x4.identity;
                var proxyNormalMatrix = Mathf.Abs(proxyMatrix.determinant) > 1e-8f ? proxyMatrix.inverse.transpose : Matrix4x4.identity;
                for (var index = 0; index < sourceNormals.Length; index++)
                {
                    var sourceWorld = sourceNormalMatrix.MultiplyVector(sourceNormals[index]).normalized;
                    var proxyWorld = proxyNormalMatrix.MultiplyVector(proxyNormals[index]).normalized;
                    result.maxWorldNormalError = Mathf.Max(result.maxWorldNormalError, Vector3.Distance(sourceWorld, proxyWorld));
                }
                result.normalsMatch &= result.maxWorldNormalError <= 1e-5f;
            }
            var sourceTangents = source.tangents; var proxyTangents = persistedProxy.tangents;
            result.tangentsMatch = sourceTangents.Length == proxyTangents.Length;
            if (result.tangentsMatch && sourceTangents.Length == sourceVertices.Length)
            {
                result.maxWorldTangentError = 0f;
                var sourceMatrix = sourceTransform.localToWorldMatrix;
                var proxyMatrix = proxyTransform.localToWorldMatrix;
                for (var index = 0; index < sourceTangents.Length; index++)
                {
                    var sourceTangent = sourceTangents[index]; var proxyTangent = proxyTangents[index];
                    var sourceWorld = sourceMatrix.MultiplyVector(new Vector3(sourceTangent.x, sourceTangent.y, sourceTangent.z)).normalized;
                    var proxyWorld = proxyMatrix.MultiplyVector(new Vector3(proxyTangent.x, proxyTangent.y, proxyTangent.z)).normalized;
                    result.maxWorldTangentError = Mathf.Max(result.maxWorldTangentError, Vector3.Distance(sourceWorld, proxyWorld));
                    var sourceHand = sourceTangent.w * Math.Sign(sourceMatrix.determinant);
                    var proxyHand = proxyTangent.w * Math.Sign(proxyMatrix.determinant);
                    if (sourceHand != proxyHand) result.tangentsMatch = false;
                }
                result.tangentsMatch &= result.maxWorldTangentError <= 1e-5f;
            }
            return result;
        }

        static string AssetGuid(UnityEngine.Object value, out long fileId)
        {
            string guid;
            return AssetDatabase.TryGetGUIDAndLocalFileIdentifier(value, out guid, out fileId) ? guid : null;
        }
        static string TextureAssetGuid(Texture value)
        {
            if (value == null) return null;
            if (value == Texture2D.whiteTexture) return "builtin:white";
            long fileId; return AssetGuid(value, out fileId);
        }

        /// <summary>True only for the generated proxy root owned by this exact source root.</summary>
        public static bool IsGeneratedSortProxyRoot(Transform child)
        {
            if (child == null || child.parent == null) return false;
            var marker = child.GetComponent<NativeStaticSortQueueProxyMarker>();
            if (marker == null || marker.kind != "root" || marker.sourceRootOwner == null ||
                marker.sourceRootOwner.transform != child.parent) return false;
            var presenter = child.GetComponent<NativeStaticSortQueueProxyPresenter>();
            return presenter != null && presenter.sourceRoot == marker.sourceRootOwner &&
                presenter.proxyRoot == child.gameObject && presenter.sourceRootId == marker.sourceNode;
        }

        static List<GameObject> NestedProxyRoots(GameObject sourceRoot)
        {
            var roots = new List<GameObject>();
            foreach (var marker in sourceRoot.GetComponentsInChildren<NativeStaticSortQueueProxyMarker>(true))
            {
                if (marker == null || marker.kind != "root" || marker.sourceRootOwner == sourceRoot) continue;
                if (!IsGeneratedSortProxyRoot(marker.transform)) continue;
                if (marker.sourceRootOwner == null || !marker.sourceRootOwner.transform.IsChildOf(sourceRoot.transform))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_NESTED_ROOT_OWNER_OUTSIDE_SOURCE_SCOPE: " + marker.sourceNode);
                roots.Add(marker.gameObject);
            }
            return roots.Distinct().ToList();
        }

        /// <summary>
        /// Temporarily removes nested presenters from the mesh capture path.
        /// Their OnDisable restores the source CanvasRenderer cull values; the
        /// generated proxy roots are then hidden while source geometry is
        /// rebuilt and copied by the outer queue.
        /// </summary>
        sealed class NestedProxyCaptureScope : IDisposable
        {
            readonly GameObject[] roots;
            readonly NativeStaticSortQueueProxyPresenter[] presenters;
            readonly bool[] rootActiveBefore, presenterEnabledBefore;
            bool committed, disposed;

            public NestedProxyCaptureScope(IReadOnlyList<GameObject> nestedRoots)
            {
                roots = (nestedRoots ?? Array.Empty<GameObject>()).ToArray();
                presenters = roots.Select(root => root == null ? null : root.GetComponent<NativeStaticSortQueueProxyPresenter>()).ToArray();
                rootActiveBefore = roots.Select(root => root != null && root.activeSelf).ToArray();
                presenterEnabledBefore = presenters.Select(presenter => presenter != null && presenter.enabled).ToArray();
                for (var i = 0; i < roots.Length; i++)
                    if (roots[i] == null || presenters[i] == null || !IsGeneratedSortProxyRoot(roots[i].transform))
                        throw new InvalidOperationException("STATIC_SORT_PROXY_NESTED_CAPTURE_IDENTITY_INVALID: " + i);

                // Disable presenters first so their source cull state is restored
                // before any source Graphic mesh is rebuilt.
                for (var i = 0; i < presenters.Length; i++)
                    if (presenters[i].enabled) presenters[i].enabled = false;
                for (var i = 0; i < roots.Length; i++)
                    if (roots[i].activeSelf) roots[i].SetActive(false);
            }

            public void Commit()
            {
                if (disposed) throw new ObjectDisposedException(nameof(NestedProxyCaptureScope));
                committed = true;
                // Preserve the authored component enabled state while leaving
                // each generated nested branch inactive under the outer queue.
                for (var i = 0; i < presenters.Length; i++)
                    if (presenters[i] != null) presenters[i].enabled = presenterEnabledBefore[i];
            }

            public void Dispose()
            {
                if (disposed) return;
                disposed = true;
                if (committed) return;
                // On failure, restore the exact pre-capture active/enabled
                // state. Enabling a presenter after its root is active restores
                // its normal source suppression behavior.
                for (var i = 0; i < roots.Length; i++)
                    if (roots[i] != null) roots[i].SetActive(rootActiveBefore[i]);
                for (var i = 0; i < presenters.Length; i++)
                    if (presenters[i] != null) presenters[i].enabled = presenterEnabledBefore[i];
            }
        }

        static void EnsureSourceGraphicMeshReady(Graphic graphic)
        {
            if (graphic == null || graphic.canvasRenderer == null) return;
            // Spine's registered RawImage children carry a custom mesh emitted
            // by SkeletonGraphic. Rebuilding them as ordinary RawImages would
            // replace that mesh with a quad, so only the SDK static-pose path
            // may prepare those renderers.
            var parentGraphic = graphic.transform.parent == null ? null : graphic.transform.parent.GetComponent<Graphic>();
            if (parentGraphic != null && IsSpineCanvasSubmesh(graphic.gameObject, parentGraphic)) return;
            // TMP generated submesh objects are emitted by the owning text
            // component's ForceMeshUpdate and likewise must keep that mesh.
            if (parentGraphic != null && parentGraphic.GetType().FullName == "TMPro.TextMeshProUGUI" &&
                IsGeneratedTextSubmesh(graphic.gameObject)) return;
            if (graphic.GetType().FullName == "Spine.Unity.SkeletonGraphic") return;
            if (graphic is TMPro.TMP_Text tmp)
            {
                tmp.ForceMeshUpdate(true, false);
                return;
            }
            graphic.SetAllDirty();
            graphic.Rebuild(CanvasUpdate.PreRender);
        }

        static Dictionary<string, OwnerFontStyleDescriptor> PrepareSourceGeometryForCapture(ProxyQueueSpec spec,
            IDictionary<string, GameObject> sourceNodes,
            GameObject sourceRoot)
        {
            var ownerStyles = new Dictionary<string, OwnerFontStyleDescriptor>(StringComparer.Ordinal);
            if ((spec.renderers ?? Array.Empty<ProxyRendererSpec>()).Any(row => row != null && row.sourceType == "sp.Skeleton"))
                InitializeSourceSpineStaticPose(sourceRoot);
            Canvas.ForceUpdateCanvases();
            foreach (var row in spec.renderers ?? Array.Empty<ProxyRendererSpec>())
            {
                if (row == null || !String.Equals(row.sourceType, "cc.Sprite", StringComparison.Ordinal) &&
                    !String.Equals(row.sourceType, "cc.Label", StringComparison.Ordinal) &&
                    !String.Equals(row.sourceType, "cc.RichText", StringComparison.Ordinal)) continue;
                if (!sourceNodes.TryGetValue(row.node, out var sourceNode) || sourceNode == null) continue;
                var graphic = sourceNode.GetComponent<Graphic>();
                if (graphic == null || graphic.GetType().FullName != row.expectedGraphicType)
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_GRAPHIC_MISMATCH_DURING_CAPTURE_PREPARE: " +
                        row.sourceComponentId + ";node=" + row.node);
                if (row.sourceType == "cc.Label" || row.sourceType == "cc.RichText")
                {
                    if (!row.sourceEnabled || !row.sourceActive || row.sourceTextEmpty) continue;
                    var textOwner = sourceNode.GetComponent<TMPro.TMP_Text>();
                    if (textOwner == null)
                        throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SOURCE_OWNER_MISSING: " + row.sourceComponentId);
                    if (!UnityStaticSortTextSource.PrepareSource(textOwner, row.sourceComponentId, out var textDiagnostic))
                        throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SOURCE_PREPARE_FAILED: " + row.sourceComponentId +
                            ";diagnostic=" + textDiagnostic);
                    var outline = sourceNode.GetComponent<NativeStaticTextOutline>();
                    if (outline != null)
                    {
                        var ownerStylePath = OwnerFontMaterialPath(spec.meshAssetFolder, row.sourceComponentId,
                            textOwner, outline);
                        if (!UnityStaticSortTextSource.CaptureOwnerFontMaterial(textOwner, row.sourceComponentId,
                                ownerStylePath, out var persistentOwnerMaterial, out var ownerStyle, out var ownerStyleDiagnostic) ||
                            persistentOwnerMaterial == null || ownerStyle == null)
                            throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_OWNER_STYLE_CAPTURE_FAILED: " +
                                row.sourceComponentId + ";diagnostic=" + ownerStyleDiagnostic);
                        ownerStyles.Add(row.sourceComponentId, ownerStyle);
                        if (!UnityStaticSortTextSource.PrepareSource(textOwner, row.sourceComponentId, out textDiagnostic))
                            throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_OWNER_STYLE_REPREPARE_FAILED: " +
                                row.sourceComponentId + ";diagnostic=" + textDiagnostic);
                    }
                }
                else EnsureSourceGraphicMeshReady(graphic);
            }
            Canvas.ForceUpdateCanvases();
            return ownerStyles;
        }

        static List<TextSlotBinding> CaptureAndRebindTextSlots(ProxyQueueSpec spec, ProxyRendererSpec row,
            TMPro.TMP_Text owner, OwnerFontStyleDescriptor ownerStyle,
            out NativeStaticSortTextSlotEnumeration slotEnumeration)
        {
            slotEnumeration = null;
            if (owner == null) throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_OWNER_MISSING: " + row.sourceComponentId);
            if (!UnityStaticSortTextSource.GetCurrentSlots(owner, row.sourceComponentId, out var initialSlots,
                    out slotEnumeration, out var initialDiagnostic))
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_CAPTURE_FAILED: " + row.sourceComponentId +
                    ";diagnostic=" + initialDiagnostic);
            ValidateTextSlotEnumeration(slotEnumeration, row.sourceComponentId);
            if (initialSlots.Count == 0)
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_DENOMINATOR_EMPTY: " + row.sourceComponentId +
                    ";enumeration=" + slotEnumeration.evidenceSha256);
            var slotIds = initialSlots.Select(binding => binding.materialSlot).OrderBy(slot => slot).ToArray();
            if (slotIds.Distinct().Count() != slotIds.Length)
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_DENOMINATOR_DUPLICATED: " + row.sourceComponentId);
            var captureProofs = new Dictionary<int, TextSlotBinding>();
            foreach (var slot in slotIds)
            {
                if (!UnityStaticSortTextSource.GetCurrentSlots(owner, row.sourceComponentId, out var liveSlots,
                        out var liveEnumeration, out var liveDiagnostic))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_REFRESH_FAILED: " + row.sourceComponentId +
                        ";slot=" + slot + ";diagnostic=" + liveDiagnostic);
                if (!SameTextSlotEnumeration(slotEnumeration, liveEnumeration))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_EVIDENCE_CHANGED_DURING_CAPTURE: " +
                        row.sourceComponentId + ";slot=" + slot);
                var live = liveSlots.SingleOrDefault(binding => binding.materialSlot == slot);
                if (live == null)
                    throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_DISAPPEARED_DURING_CAPTURE: " + row.sourceComponentId +
                        ";slot=" + slot);
                live.ownerStyle = ownerStyle;
                var materialPath = spec.meshAssetFolder.TrimEnd('/') + "/TMPTextMaterial_" +
                    HashText(row.sourceComponentId + "|" + slot + "|" +
                        (live.transientFallbackFingerprint ?? live.sourceMaterialFingerprint ?? String.Empty)).Substring(0, 24) + ".mat";
                if (!UnityStaticSortTextSource.CaptureFallbackMaterial(live, materialPath, out var captureDiagnostic))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_FALLBACK_MATERIAL_CAPTURE_FAILED: " + row.sourceComponentId +
                        ";slot=" + slot + ";diagnostic=" + captureDiagnostic);
                captureProofs.Add(slot, live);
                // The registered primary/fallback material must take effect in
                // TMP's current mesh before another slot is resolved.
                if (!UnityStaticSortTextSource.PrepareSource(owner, row.sourceComponentId, out var prepareDiagnostic))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_REPREPARE_FAILED: " + row.sourceComponentId +
                        ";slot=" + slot + ";diagnostic=" + prepareDiagnostic);
                Canvas.ForceUpdateCanvases();
            }

            if (!UnityStaticSortTextSource.PrepareSource(owner, row.sourceComponentId, out var finalPrepareDiagnostic))
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_FINAL_REPREPARE_FAILED: " + row.sourceComponentId +
                    ";diagnostic=" + finalPrepareDiagnostic);
            Canvas.ForceUpdateCanvases();
            if (!UnityStaticSortTextSource.GetCurrentSlots(owner, row.sourceComponentId, out var finalSlots,
                    out var finalEnumeration, out var finalDiagnostic))
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_FINAL_SLOTS_FAILED: " + row.sourceComponentId +
                    ";diagnostic=" + finalDiagnostic);
            if (!SameTextSlotEnumeration(slotEnumeration, finalEnumeration))
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_EVIDENCE_CHANGED_AFTER_REGISTRATION: " + row.sourceComponentId);
            if (!slotIds.SequenceEqual(finalSlots.Select(binding => binding.materialSlot).OrderBy(slot => slot)))
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_DENOMINATOR_CHANGED_AFTER_REGISTRATION: " + row.sourceComponentId);
            var result = new List<TextSlotBinding>();
            foreach (var slot in slotIds)
            {
                var current = finalSlots.Single(binding => binding.materialSlot == slot);
                if (!UnityStaticSortTextSource.RebindCapturedSlot(captureProofs[slot], owner, current.sourceGraphic,
                        out var rebound, out var rebindDiagnostic))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_REBIND_FAILED: " + row.sourceComponentId +
                        ";slot=" + slot + ";diagnostic=" + rebindDiagnostic);
                rebound.ownerStyle = ownerStyle;
                result.Add(rebound);
            }
            return result;
        }

        static void ValidateTextSlotEnumeration(NativeStaticSortTextSlotEnumeration enumeration, string sourceComponentId)
        {
            if (enumeration == null || enumeration.verified != true || enumeration.sourceComponentId != sourceComponentId ||
                String.IsNullOrEmpty(enumeration.sourceTextSha256) || String.IsNullOrEmpty(enumeration.evidenceSha256) ||
                enumeration.slotCount < 1 || enumeration.rows == null || enumeration.rows.Length != enumeration.slotCount ||
                enumeration.rows.Select(row => row == null ? -1 : row.slot).Distinct().Count() != enumeration.slotCount ||
                !enumeration.rows.Select(row => row.slot).OrderBy(slot => slot).SequenceEqual(Enumerable.Range(0, enumeration.slotCount)))
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_ENUMERATION_INVALID: " + sourceComponentId);
            foreach (var row in enumeration.rows)
            {
                if (row == null || String.IsNullOrEmpty(row.evidenceSha256) ||
                    (row.disposition != "drawable" && row.disposition != "empty-placeholder"))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_EVIDENCE_ROW_INVALID: " + sourceComponentId);
                if (row.disposition == "empty-placeholder" &&
                    (row.characterReferences != 0 || row.visibleCharacterReferences != 0 ||
                     row.textInfoNondegenerateTriangleCount != 0 || row.canvasNondegenerateTriangleCount != 0))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_PLACEHOLDER_HAS_DRAWABLE_EVIDENCE: " +
                        sourceComponentId + ";slot=" + row.slot);
            }
            if (enumeration.rows.Any(row => row.disposition == "empty-placeholder" && row.slot != 0) ||
                enumeration.rows.Count(row => row.disposition == "empty-placeholder") > 1)
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_PLACEHOLDER_SLOT_NOT_OWNER_SLOT0: " + sourceComponentId);
        }

        static bool SameTextSlotEnumeration(NativeStaticSortTextSlotEnumeration left,
            NativeStaticSortTextSlotEnumeration right)
        {
            return left != null && right != null && left.sourceComponentId == right.sourceComponentId &&
                left.sourceTextSha256 == right.sourceTextSha256 && left.slotCount == right.slotCount &&
                left.evidenceSha256 == right.evidenceSha256;
        }

        static string OwnerFontMaterialPath(string folder, string sourceComponentId, TMPro.TMP_Text owner,
            NativeStaticTextOutline outline)
        {
            if (String.IsNullOrWhiteSpace(folder) || owner == null || owner.font == null || outline == null ||
                !AssetDatabase.TryGetGUIDAndLocalFileIdentifier(owner.font, out var fontGuid, out long fontLocalId) ||
                String.IsNullOrWhiteSpace(fontGuid) || fontLocalId == 0)
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_OWNER_STYLE_PATH_INPUT_INVALID: " + sourceComponentId);
            var color = outline.SourceOutlineColor;
            var profile = sourceComponentId + "|" + fontGuid + ":" + fontLocalId + "|" +
                owner.fontSize.ToString("R", CultureInfo.InvariantCulture) + "|" +
                outline.SourceOutlineWidth.ToString("R", CultureInfo.InvariantCulture) + "|" +
                color.r.ToString("R", CultureInfo.InvariantCulture) + "," + color.g.ToString("R", CultureInfo.InvariantCulture) + "," +
                color.b.ToString("R", CultureInfo.InvariantCulture) + "," + color.a.ToString("R", CultureInfo.InvariantCulture);
            return folder.TrimEnd('/') + "/TMPOwnerMaterial_" + HashText(profile).Substring(0, 24) + ".mat";
        }

        static void InitializeSourceSpineStaticPose(GameObject sourceRoot)
        {
            // The hook is emitted only when the pinned Spine integration is
            // part of this target. Reflection keeps the optional non-Spine
            // Editor assembly compilable without adding a hard SDK dependency.
            var initialize = typeof(MonkeyImporter).GetMethod("InitializeSavedStaticSpine",
                BindingFlags.Static | BindingFlags.NonPublic);
            if (initialize == null)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_STATIC_POSE_INITIALIZER_MISSING");
            try { initialize.Invoke(null, new object[] { sourceRoot }); }
            catch (TargetInvocationException error)
            {
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_STATIC_POSE_INITIALIZATION_FAILED",
                    error.InnerException ?? error);
            }
        }

        static bool SourceTreeMatchesProxy(ProxyQueueSpec spec, IDictionary<string, GameObject> nodes)
        {
            var rows = spec.sourceChildOrder ?? Array.Empty<ProxySourceChildrenSpec>();
            var active = spec.sourceNodeActive ?? Array.Empty<ProxySourceActiveSpec>();
            if (rows.Length == 0 || rows.Any(row => row == null || string.IsNullOrEmpty(row.node)) ||
                rows.Select(row => row.node).Distinct().Count() != rows.Length ||
                active.Any(row => row == null || string.IsNullOrEmpty(row.node)) ||
                active.Select(row => row.node).Distinct().Count() != active.Length ||
                active.Length != rows.Length || !active.Select(row => row.node).ToHashSet().SetEquals(rows.Select(row => row.node)) ||
                !rows.Any(row => row.node == spec.rootScope)) return false;
            var sourceIds = new HashSet<string>(rows.Select(row => row.node));
            foreach (var row in rows)
            {
                if (!nodes.TryGetValue(row.node, out var parent) || parent == null) return false;
                var expected = row.children ?? Array.Empty<string>();
                if (expected.Any(string.IsNullOrEmpty) || expected.Distinct().Count() != expected.Length ||
                    expected.Any(id => !sourceIds.Contains(id))) return false;
                var observed = new List<string>();
                foreach (Transform child in parent.transform)
                {
                    if (IsGeneratedSortProxyRoot(child)) continue;
                    var sourceChild = nodes.FirstOrDefault(entry => entry.Value != null && entry.Value.transform == child).Key;
                    if (sourceChild != null) observed.Add(sourceChild);
                    else if (!IsGeneratedTextSubmesh(child.gameObject)) return false;
                }
                if (!observed.SequenceEqual(expected)) return false;
            }
            return true;
        }

        static Mesh SnapshotSubmesh(Mesh source, int submesh, Transform sourceTransform, Transform proxyTransform)
        {
            var copy = new Mesh { name = source.name + "_StaticQueue" };
            if (source.vertexCount > 65535) copy.indexFormat = UnityEngine.Rendering.IndexFormat.UInt32;
            var singularPlane = Mathf.Abs(sourceTransform.localToWorldMatrix.determinant) <= 1e-8f ||
                Mathf.Abs(proxyTransform.localToWorldMatrix.determinant) <= 1e-8f;
            var positions = source.vertices.Select(vertex => InverseTransformPointForUiPlane(proxyTransform,
                sourceTransform.TransformPoint(vertex), source.name)).ToArray();
            copy.vertices = positions;
            if (source.colors32.Length == source.vertexCount) copy.colors32 = source.colors32;
            CopyUvChannels(source, copy);
            var normals = source.normals;
            if (normals.Length == source.vertexCount)
            {
                if (singularPlane) copy.normals = normals;
                else
                {
                    var sourceNormalMatrix = sourceTransform.localToWorldMatrix.inverse.transpose;
                    var proxyNormalMatrix = proxyTransform.localToWorldMatrix.transpose;
                    copy.normals = normals.Select(n => proxyNormalMatrix.MultiplyVector(sourceNormalMatrix.MultiplyVector(n)).normalized).ToArray();
                }
            }
            var tangents = source.tangents;
            if (tangents.Length == source.vertexCount)
            {
                if (singularPlane) copy.tangents = tangents;
                else
                {
                    var sourceMatrix = sourceTransform.localToWorldMatrix;
                    var proxyInverse = proxyTransform.worldToLocalMatrix;
                    copy.tangents = tangents.Select(t => {
                        var direction = proxyInverse.MultiplyVector(sourceMatrix.MultiplyVector(new Vector3(t.x, t.y, t.z))).normalized;
                        var handedness = Mathf.Sign((proxyInverse * sourceMatrix).determinant);
                        return new Vector4(direction.x, direction.y, direction.z, t.w * handedness);
                    }).ToArray();
                }
            }
            copy.subMeshCount = 1;
            copy.SetTriangles(source.GetTriangles(submesh), 0, false);
            copy.RecalculateBounds();
            return copy;
        }

        static Mesh PersistMesh(Mesh source, int submesh, Transform sourceTransform, Transform proxyTransform,
            string sourceComponentId, int submeshIndex, string folder, out string sourceSha,
            out string contentSha, out string guid)
        {
            sourceSha = MeshFingerprint(source, submesh);
            var snapshot = SnapshotSubmesh(source, submesh, sourceTransform, proxyTransform);
            contentSha = MeshFingerprint(snapshot, 0);
            var key = HashText(sourceComponentId + "|" + submeshIndex + "|" + sourceSha + "|" + contentSha).Substring(0, 24);
            var path = folder.TrimEnd('/') + "/QueueMesh_" + key + ".asset";
            var existing = AssetDatabase.LoadAssetAtPath<Mesh>(path);
            if (existing != null)
            {
                // Existing generated assets are immutable unless byte-level
                // vertex/channel/index data matches this source snapshot.
                var existingHash = MeshFingerprint(existing, 0);
                if (existingHash != contentSha)
                    throw new InvalidOperationException("STATIC_SORT_PROXY_MESH_ASSET_COLLISION: " + path);
                long existingId; guid = AssetGuid(existing, out existingId);
                return existing;
            }
            Directory.CreateDirectory(Path.GetDirectoryName(path));
            AssetDatabase.CreateAsset(snapshot, path);
            long local; guid = AssetGuid(snapshot, out local);
            if (guid == null) throw new InvalidOperationException("STATIC_SORT_PROXY_MESH_NOT_PERSISTENT: " + sourceComponentId);
            return snapshot;
        }

        static bool WorldRectMatches(RectTransform source, RectTransform proxy, float tolerance = .001f)
        {
            var a = new Vector3[4]; var b = new Vector3[4];
            source.GetWorldCorners(a); proxy.GetWorldCorners(b);
            for (var i = 0; i < 4; i++) if ((a[i] - b[i]).sqrMagnitude > tolerance * tolerance) return false;
            return true;
        }

        static string WorldCornerEvidence(RectTransform source, RectTransform proxy)
        {
            var sourceCorners = new Vector3[4]; var proxyCorners = new Vector3[4];
            source.GetWorldCorners(sourceCorners); proxy.GetWorldCorners(proxyCorners);
            return "sourceCorners=[" + string.Join(";", sourceCorners.Select(value => value.ToString("R"))) +"];proxyCorners=[" +
                string.Join(";", proxyCorners.Select(value => value.ToString("R"))) + "]";
        }

        static bool MatrixNear(Matrix4x4 a, Matrix4x4 b, float tolerance)
        {
            for (var row = 0; row < 4; row++)
                for (var column = 0; column < 4; column++)
                    if (Mathf.Abs(a[row, column] - b[row, column]) > tolerance) return false;
            return true;
        }

        static bool TrySolvePlaneCoordinates(Transform plane, Vector3 worldPoint, out Vector2 coordinates,
            out Vector3 reconstructed)
        {
            coordinates = Vector2.zero; reconstructed = Vector3.zero;
            if (plane == null) return false;
            var matrix = plane.localToWorldMatrix;
            var origin = matrix.GetColumn(3);
            var axisX = (Vector3)matrix.GetColumn(0); var axisY = (Vector3)matrix.GetColumn(1);
            var delta = worldPoint - (Vector3)origin;
            var xx = Vector3.Dot(axisX, axisX); var xy = Vector3.Dot(axisX, axisY); var yy = Vector3.Dot(axisY, axisY);
            var determinant = xx * yy - xy * xy;
            if (determinant <= 1e-12f) return false;
            var dx = Vector3.Dot(axisX, delta); var dy = Vector3.Dot(axisY, delta);
            coordinates.x = (dx * yy - dy * xy) / determinant;
            coordinates.y = (dy * xx - dx * xy) / determinant;
            reconstructed = (Vector3)origin + axisX * coordinates.x + axisY * coordinates.y;
            return true;
        }

        static bool TrySolvePlaneVector(Transform plane, Vector3 worldVector, out Vector2 coordinates,
            out Vector3 reconstructed)
        {
            coordinates = Vector2.zero; reconstructed = Vector3.zero;
            if (plane == null) return false;
            var matrix = plane.localToWorldMatrix;
            var axisX = (Vector3)matrix.GetColumn(0); var axisY = (Vector3)matrix.GetColumn(1);
            var xx = Vector3.Dot(axisX, axisX); var xy = Vector3.Dot(axisX, axisY); var yy = Vector3.Dot(axisY, axisY);
            var determinant = xx * yy - xy * xy;
            if (determinant <= 1e-12f) return false;
            var dx = Vector3.Dot(axisX, worldVector); var dy = Vector3.Dot(axisY, worldVector);
            coordinates.x = (dx * yy - dy * xy) / determinant;
            coordinates.y = (dy * xx - dx * xy) / determinant;
            reconstructed = axisX * coordinates.x + axisY * coordinates.y;
            return true;
        }

        static Vector3 InverseTransformPointForUiPlane(Transform target, Vector3 worldPoint, string sourceId)
        {
            if (Mathf.Abs(target.localToWorldMatrix.determinant) > 1e-8f) return target.InverseTransformPoint(worldPoint);
            if (!TrySolvePlaneCoordinates(target, worldPoint, out var coordinates, out var reconstructed) ||
                (reconstructed - worldPoint).sqrMagnitude > 1e-6f)
                throw new InvalidOperationException("STATIC_SORT_PROXY_VERTEX_OUTSIDE_SINGULAR_UI_PLANE: " + sourceId);
            // Local Z is unobservable when the native parent has a zero depth
            // scale. Preserve exact world positions in its invertible UI plane.
            return new Vector3(coordinates.x, coordinates.y, 0f);
        }

        static void CopyWorldRectOnSingularPlane(RectTransform source, RectTransform proxy, Transform parent, string sourceId)
        {
            if (!TrySolvePlaneCoordinates(parent, source.position, out var position, out var reconstructedPosition) ||
                (reconstructedPosition - source.position).sqrMagnitude > 1e-6f)
                throw new InvalidOperationException("STATIC_SORT_PROXY_PIVOT_OUTSIDE_SINGULAR_UI_PLANE: " + sourceId);
            var sourceRight = source.TransformVector(Vector3.right);
            var sourceUp = source.TransformVector(Vector3.up);
            if (!TrySolvePlaneVector(parent, sourceRight, out var right, out var reconstructedRight) ||
                !TrySolvePlaneVector(parent, sourceUp, out var up, out var reconstructedUp) ||
                (reconstructedRight - sourceRight).sqrMagnitude > 1e-8f ||
                (reconstructedUp - sourceUp).sqrMagnitude > 1e-8f)
                throw new InvalidOperationException("STATIC_SORT_PROXY_BASIS_OUTSIDE_SINGULAR_UI_PLANE: " + sourceId);
            var sx = right.magnitude; var upLength = up.magnitude;
            if (sx <= 1e-8f || upLength <= 1e-8f)
                throw new InvalidOperationException("STATIC_SORT_PROXY_TRANSFORM_DEGENERATE: " + sourceId);
            var angle = Mathf.Atan2(right.y, right.x);
            var rotation = Quaternion.Euler(0f, 0f, angle * Mathf.Rad2Deg);
            var rotatedUp = (Vector2)(rotation * Vector3.up);
            var signedY = Vector2.Dot(up, rotatedUp);
            if (Mathf.Abs(signedY) <= 1e-8f || (up - rotatedUp * signedY).sqrMagnitude > 1e-8f)
                throw new InvalidOperationException("STATIC_SORT_PROXY_2D_SHEAR_UNREPRESENTABLE: " + sourceId);
            proxy.localPosition = new Vector3(position.x, position.y, 0f);
            proxy.localRotation = rotation;
            proxy.localScale = new Vector3(sx, signedY, 1f);
            var matrix = parent.localToWorldMatrix * Matrix4x4.TRS(proxy.localPosition, proxy.localRotation, proxy.localScale);
            var reconstructedProxyRight = matrix.MultiplyVector(Vector3.right);
            var reconstructedProxyUp = matrix.MultiplyVector(Vector3.up);
            if ((reconstructedProxyRight - sourceRight).sqrMagnitude > 1e-8f ||
                (reconstructedProxyUp - sourceUp).sqrMagnitude > 1e-8f ||
                ((Vector3)matrix.GetColumn(3) - source.position).sqrMagnitude > 1e-6f)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SINGULAR_2D_TRS_NOT_EXACT: " + sourceId);
            if (!WorldRectMatches(source, proxy))
                throw new InvalidOperationException("STATIC_SORT_PROXY_TRANSFORM_NOT_EXACT: " + sourceId + " (" + WorldCornerEvidence(source, proxy) + ")");
        }

        static void CopyWorldRect(RectTransform source, RectTransform proxy, Transform parent, string sourceId)
        {
            proxy.SetParent(parent, false);
            proxy.anchorMin = new Vector2(.5f, .5f); proxy.anchorMax = new Vector2(.5f, .5f);
            proxy.pivot = source.pivot; proxy.sizeDelta = source.rect.size;
            if (Mathf.Abs(parent.localToWorldMatrix.determinant) <= 1e-8f)
            {
                CopyWorldRectOnSingularPlane(source, proxy, parent, sourceId);
                return;
            }
            var local = parent.worldToLocalMatrix * source.localToWorldMatrix;
            var x = (Vector3)local.GetColumn(0); var y = (Vector3)local.GetColumn(1); var z = (Vector3)local.GetColumn(2);
            var sx = x.magnitude; var sy = y.magnitude;
            if (sx <= 1e-8f || sy <= 1e-8f)
                throw new InvalidOperationException("STATIC_SORT_PROXY_TRANSFORM_DEGENERATE: " + sourceId);
            var right = x / sx; var up = y / sy;
            if (Mathf.Abs(Vector3.Dot(right, up)) > 1e-5f ||
                Mathf.Abs(Vector3.Dot(right, z.normalized)) > 1e-5f ||
                Mathf.Abs(Vector3.Dot(up, z.normalized)) > 1e-5f)
                throw new InvalidOperationException("STATIC_SORT_PROXY_TRANSFORM_SHEAR_UNREPRESENTABLE: " + sourceId);
            var forward = Vector3.Cross(right, up).normalized;
            var rotation = Quaternion.LookRotation(forward, up);
            var signedZ = z.sqrMagnitude <= 1e-16f ? 0f : Vector3.Dot(z, forward);
            proxy.localPosition = local.GetColumn(3);
            proxy.localRotation = rotation;
            // Derive orientation from the actual X/Y basis, then preserve a
            // reflection on the depth axis explicitly. Matrix4x4.rotation and
            // lossyScale can redistribute a reflection (notably local Z=-1)
            // across X/Y, changing RectTransform corners.
            proxy.localScale = new Vector3(sx, sy, signedZ);
            var reconstructed = Matrix4x4.TRS(proxy.localPosition, proxy.localRotation, proxy.localScale);
            if (!MatrixNear(local, reconstructed, 1e-4f))
                throw new InvalidOperationException("STATIC_SORT_PROXY_TRANSFORM_TRS_NOT_EXACT: " + sourceId + " (" + WorldCornerEvidence(source, proxy) + ")");
            if (!WorldRectMatches(source, proxy))
                throw new InvalidOperationException("STATIC_SORT_PROXY_TRANSFORM_NOT_EXACT: " + sourceId + " (" + WorldCornerEvidence(source, proxy) + ")");
        }

        static bool IsGeneratedTextSubmesh(GameObject gameObject)
        {
            if (gameObject == null || gameObject.transform.parent == null || gameObject.transform.childCount != 0 ||
                !(gameObject.transform is RectTransform) || (gameObject.hideFlags & HideFlags.DontSave) != HideFlags.DontSave) return false;
            var components = gameObject.GetComponents<Component>();
            var sub = components.FirstOrDefault(component => component != null && component.GetType().FullName == "TMPro.TMP_SubMeshUI");
            var owner = gameObject.transform.parent.GetComponents<Component>().FirstOrDefault(component => component != null &&
                component.GetType().FullName == "TMPro.TextMeshProUGUI");
            var layout = gameObject.GetComponent<LayoutElement>();
            if (sub == null || owner == null || layout == null || !layout.ignoreLayout) return false;
            var textComponent = sub.GetType().GetProperty("textComponent", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)?.GetValue(sub, null);
            var fontAsset = sub.GetType().GetProperty("fontAsset", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)?.GetValue(sub, null);
            return textComponent == (object)owner && fontAsset != null && components.All(component => component == null ||
                component is RectTransform || component is CanvasRenderer || component == sub || component is LayoutElement);
        }

        static bool IsSpineCanvasSubmesh(GameObject gameObject, Graphic sourceGraphic)
        {
            if (gameObject == null || sourceGraphic == null || sourceGraphic.GetType().FullName != "Spine.Unity.SkeletonGraphic" ||
                gameObject.transform.parent != sourceGraphic.transform || gameObject.transform.childCount != 0 ||
                !(gameObject.transform is RectTransform) || gameObject.GetComponent<RawImage>() == null ||
                gameObject.GetComponent<CanvasRenderer>() == null) return false;
            if (gameObject.GetComponents<Component>().Any(component => component != null &&
                !(component is RectTransform) && !(component is CanvasRenderer) && !(component is RawImage))) return false;
            var rendererListMember = (MemberInfo)sourceGraphic.GetType().GetProperty("canvasRenderers", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic) ??
                                     sourceGraphic.GetType().GetField("canvasRenderers", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic);
            var rendererList = rendererListMember is PropertyInfo property ? property.GetValue(sourceGraphic, null) :
                rendererListMember is FieldInfo field ? field.GetValue(sourceGraphic) : null;
            if (!(rendererList is IEnumerable enumerable)) return false;
            var target = gameObject.GetComponent<CanvasRenderer>(); var exactCount = 0;
            foreach (var item in enumerable) if (item is CanvasRenderer renderer && renderer == target && renderer.gameObject == gameObject) exactCount++;
            return exactCount == 1;
        }

        static string TransformPath(Transform node)
        {
            var names = new Stack<string>();
            for (var cursor = node; cursor != null; cursor = cursor.parent) names.Push(cursor.name);
            return String.Join("/", names.ToArray());
        }

        static string SpineChildPath(Transform root, Transform child)
        {
            if (root == null || child == null || child == root || !child.IsChildOf(root)) return null;
            var segments = new Stack<string>();
            for (var cursor = child; cursor != null && cursor != root; cursor = cursor.parent)
                segments.Push(cursor.name + "[" + cursor.GetSiblingIndex() + "]");
            return String.Join("/", segments.ToArray());
        }

        static bool TryReadSpineMember(object target, string name, out object value)
        {
            for (var type = target == null ? null : target.GetType(); type != null; type = type.BaseType)
            {
                var flags = BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.DeclaredOnly;
                var property = type.GetProperty(name, flags);
                if (property != null && property.CanRead) { value = property.GetValue(target, null); return true; }
                var field = type.GetField(name, flags);
                if (field != null) { value = field.GetValue(target); return true; }
            }
            value = null; return false;
        }

        static bool TryReadSpineRendererList(Graphic owner, out List<CanvasRenderer> renderers)
        {
            renderers = new List<CanvasRenderer>();
            if (owner == null || owner.GetType().FullName != "Spine.Unity.SkeletonGraphic") return false;
            if (!TryReadSpineMember(owner, "canvasRenderers", out var value) || !(value is IEnumerable enumerable)) return false;
            foreach (var item in enumerable)
            {
                if (!(item is CanvasRenderer renderer) || renderer == null) return false;
                renderers.Add(renderer);
            }
            return true;
        }

        static bool TryReadSpineDataAsset(Graphic owner, out UnityEngine.Object dataAsset)
        {
            dataAsset = null;
            if (owner == null || owner.GetType().FullName != "Spine.Unity.SkeletonGraphic") return false;
            if (!TryReadSpineMember(owner, "SkeletonDataAsset", out var value) &&
                !TryReadSpineMember(owner, "skeletonDataAsset", out value)) return false;
            dataAsset = value as UnityEngine.Object;
            return dataAsset != null;
        }

        [Serializable] sealed class SpineSourceBindingPlan
        {
            public string sourceManifestSha256;
            public SpineSourceBindingComponent[] components;
            public SpineSourceBindingAsset[] dataAssets;
        }
        [Serializable] sealed class SpineSourceBindingComponent
        {
            public string sourceComponentId, sourceDataAssetId;
            public bool sourceHasStaticDataReference;
        }
        [Serializable] sealed class SpineSourceBindingAsset
        {
            public string sourceAssetId, skeletonDataAssetPath, skeletonSha256;
        }
        [Serializable] sealed class SpineDataCreateAttempt
        {
            public string sourceManifestSha256;
            public SpineDataAssetReadback[] readback;
        }
        [Serializable] sealed class SpineDataAssetReadback
        {
            public string sourceAssetId, skeletonDataAssetPath, skeletonDataAssetGuid, skeletonSha256;
            public bool nativeAssetIdentityVerified, savedSourceReferencesVerified, sourceProfileMaterialsVerified, staticDataVerified;
        }
        sealed class SpineDataIdentityEvidence
        {
            public string sourceDataAssetId, dataAssetPath, dataAssetGuid, bindingPlanPath, bindingPlanSha256,
                sourceManifestSha256;
        }

        static bool TryReadSpineDataIdentity(ProxyQueueSpec spec, string sourceComponentId,
            UnityEngine.Object actualDataAsset, out SpineDataIdentityEvidence evidence, out string diagnostic)
        {
            evidence = null; diagnostic = null;
            const string bindingPlanPath = "Assets/Game/Editor/Conversion/spine-native-binding-plan.json";
            if (spec == null || actualDataAsset == null || !File.Exists(bindingPlanPath))
            { diagnostic = "source-binding-plan-or-data-asset-missing"; return false; }
            var planBytes = File.ReadAllBytes(bindingPlanPath);
            var planHash = HashBytes(planBytes);
            var bindingPlan = JsonUtility.FromJson<SpineSourceBindingPlan>(Encoding.UTF8.GetString(planBytes));
            if (bindingPlan == null || String.IsNullOrWhiteSpace(bindingPlan.sourceManifestSha256) ||
                bindingPlan.sourceManifestSha256 != spec.sourceManifestSha256)
            { diagnostic = "source-binding-plan-manifest-hash-differs"; return false; }
            var componentRows = (bindingPlan.components ?? Array.Empty<SpineSourceBindingComponent>())
                .Where(row => row != null && row.sourceComponentId == sourceComponentId).ToArray();
            if (componentRows.Length != 1 || !componentRows[0].sourceHasStaticDataReference ||
                String.IsNullOrWhiteSpace(componentRows[0].sourceDataAssetId))
            { diagnostic = "source-component-data-asset-mapping-missing-or-ambiguous"; return false; }
            var sourceDataAssetId = componentRows[0].sourceDataAssetId;
            var dataRows = (bindingPlan.dataAssets ?? Array.Empty<SpineSourceBindingAsset>())
                .Where(row => row != null && row.sourceAssetId == sourceDataAssetId).ToArray();
            if (dataRows.Length != 1 || String.IsNullOrWhiteSpace(dataRows[0].skeletonDataAssetPath) ||
                String.IsNullOrWhiteSpace(dataRows[0].skeletonSha256))
            { diagnostic = "source-data-asset-plan-row-missing-or-ambiguous"; return false; }
            var attemptPath = Path.Combine(Directory.GetParent(Application.dataPath).FullName,
                "Analysis/Readback/Spine/create-attempt.json");
            if (!File.Exists(attemptPath))
            { diagnostic = "spine-data-asset-native-readback-missing"; return false; }
            var attempt = JsonUtility.FromJson<SpineDataCreateAttempt>(File.ReadAllText(attemptPath, Encoding.UTF8));
            if (attempt == null || attempt.sourceManifestSha256 != bindingPlan.sourceManifestSha256)
            { diagnostic = "spine-data-asset-readback-manifest-hash-differs"; return false; }
            var readbackRows = (attempt.readback ?? Array.Empty<SpineDataAssetReadback>())
                .Where(row => row != null && row.sourceAssetId == sourceDataAssetId).ToArray();
            if (readbackRows.Length != 1)
            { diagnostic = "spine-data-asset-native-readback-row-missing-or-ambiguous"; return false; }
            var readback = readbackRows[0];
            if (!readback.nativeAssetIdentityVerified || !readback.savedSourceReferencesVerified ||
                !readback.sourceProfileMaterialsVerified || !readback.staticDataVerified ||
                readback.skeletonDataAssetPath != dataRows[0].skeletonDataAssetPath ||
                readback.skeletonSha256 != dataRows[0].skeletonSha256)
            { diagnostic = "spine-data-asset-native-readback-content-or-path-differs"; return false; }
            var actualPath = AssetDatabase.GetAssetPath(actualDataAsset);
            var actualGuid = String.IsNullOrWhiteSpace(actualPath) ? null : AssetDatabase.AssetPathToGUID(actualPath);
            if (actualPath != readback.skeletonDataAssetPath || String.IsNullOrWhiteSpace(actualGuid) ||
                actualGuid != readback.skeletonDataAssetGuid || AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(actualPath) != actualDataAsset)
            { diagnostic = "component-data-asset-reference-does-not-match-exact-readback-guid"; return false; }
            evidence = new SpineDataIdentityEvidence { sourceDataAssetId = sourceDataAssetId, dataAssetPath = actualPath,
                dataAssetGuid = actualGuid, bindingPlanPath = bindingPlanPath, bindingPlanSha256 = planHash,
                sourceManifestSha256 = bindingPlan.sourceManifestSha256 };
            return true;
        }

        static ProxySpineNonDrawChild[] CaptureSpineNonDrawChildren(ProxyQueueSpec spec, ProxyRendererSpec row,
            GameObject sourceNode, IDictionary<string, GameObject> sourceNodes)
        {
            if (spec == null || row == null || sourceNode == null || sourceNodes == null ||
                row.sourceType != "sp.Skeleton" || row.sourceActive && row.sourceEnabled ||
                sourceNode.activeInHierarchy != row.sourceActive)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_NONDRAW_OWNER_SPEC_INVALID: " +
                    (row == null ? "null" : row.sourceComponentId));
            var owner = sourceNode.GetComponent<Graphic>();
            if (owner == null || owner.GetType().FullName != "Spine.Unity.SkeletonGraphic" || owner.enabled != row.sourceEnabled)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_NONDRAW_OWNER_COMPONENT_MISMATCH: " + row.sourceComponentId);
            if (!TryReadSpineIdentity(owner, row.sourceComponentId, out _))
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_NONDRAW_OWNER_IDENTITY_MISMATCH: " + row.sourceComponentId);
            UnityEngine.Object dataAsset = null;
            if (!TryReadSpineDataAsset(owner, out dataAsset))
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_NONDRAW_DATA_ASSET_NOT_BOUND: " + row.sourceComponentId +
                    ";dataGuid=<null>;binding=skeletonDataAsset-reference-missing");
            if (!TryReadSpineDataIdentity(spec, row.sourceComponentId, dataAsset, out var dataEvidence, out var dataGap))
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_NONDRAW_DATA_ASSET_NOT_BOUND: " + row.sourceComponentId +
                    ";dataGuid=" + AssetDatabase.AssetPathToGUID(AssetDatabase.GetAssetPath(dataAsset)) + ";binding=" + dataGap);
            var registered = new List<CanvasRenderer>();
            if (!TryReadSpineRendererList(owner, out registered) || registered.Count == 0 ||
                registered.Distinct().Count() != registered.Count)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_NONDRAW_REGISTERED_CHILD_LIST_INVALID: source=" +
                    row.sourceComponentId + ";owner=" + SpineMeshDiagnostic(row.sourceComponentId, owner,
                    owner.canvasRenderer == null ? null : owner.canvasRenderer.GetMesh()) + ";registered=" + registered.Count +
                    ";dataGuid=" + dataEvidence.dataAssetGuid);
            var childGraphics = new List<Graphic>();
            foreach (var renderer in registered)
            {
                var child = renderer == null ? null : renderer.GetComponent<Graphic>();
                if (child == null || renderer.gameObject != child.gameObject ||
                    !IsSpineCanvasSubmesh(child.gameObject, owner) || childGraphics.Contains(child))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_NONDRAW_REGISTERED_CHILD_NOT_EXACT: source=" +
                        row.sourceComponentId + ";child=" + (renderer == null ? "<null>" : TransformPath(renderer.transform)) +
                        ";type=" + (child == null ? "<null>" : child.GetType().FullName) + ";dataGuid=" + dataEvidence.dataAssetGuid);
                if (row.sourceActive && row.sourceEnabled == false && child.gameObject.activeInHierarchy && child.enabled)
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_NONDRAW_ACTIVE_CHILD_GRAPHIC_STILL_ENABLED: source=" +
                        row.sourceComponentId + ";child=" + TransformPath(child.transform) + ";type=" + child.GetType().FullName +
                        ";enabled=" + child.enabled + ";activeSelf=" + child.gameObject.activeSelf +
                        ";activeInHierarchy=" + child.gameObject.activeInHierarchy + ";dataGuid=" + dataEvidence.dataAssetGuid);
                if (!row.sourceActive && child.gameObject.activeInHierarchy)
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_NONDRAW_INACTIVE_OWNER_CHILD_IS_EFFECTIVE_ACTIVE: source=" +
                        row.sourceComponentId + ";child=" + TransformPath(child.transform) + ";type=" + child.GetType().FullName +
                        ";enabled=" + child.enabled + ";activeSelf=" + child.gameObject.activeSelf +
                        ";dataGuid=" + dataEvidence.dataAssetGuid);
                childGraphics.Add(child);
            }

            var sourceNodeTransforms = new HashSet<Transform>(sourceNodes.Values.Where(node => node != null)
                .Select(node => node.transform));
            foreach (var childGraphic in sourceNode.GetComponentsInChildren<Graphic>(true))
            {
                if (childGraphic == null || childGraphic == owner) continue;
                var cursor = childGraphic.transform.parent;
                var independentlyMapped = false;
                while (cursor != null && cursor != sourceNode.transform)
                {
                    if (sourceNodeTransforms.Contains(cursor)) { independentlyMapped = true; break; }
                    cursor = cursor.parent;
                }
                if (independentlyMapped) continue;
                if (!childGraphics.Contains(childGraphic) || !IsSpineCanvasSubmesh(childGraphic.gameObject, owner))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_NONDRAW_UNCLASSIFIED_DESCENDANT_GRAPHIC: source=" +
                        row.sourceComponentId + ";child=" + TransformPath(childGraphic.transform) +
                        ";type=" + childGraphic.GetType().FullName + ";dataGuid=" + dataEvidence.dataAssetGuid);
            }

            var readbacks = new List<ProxySpineNonDrawChild>();
            foreach (var child in childGraphics)
            {
                var renderer = child.canvasRenderer;
                var mesh = renderer == null ? null : renderer.GetMesh();
                var material = child.material;
                var texture = material == null || material.mainTexture == null ? child.mainTexture : material.mainTexture;
                long materialLocal;
                var materialGuid = material == null ? null : AssetGuid(material, out materialLocal);
                var textureGuid = TextureAssetGuid(texture);
                if (String.IsNullOrWhiteSpace(materialGuid) || String.IsNullOrWhiteSpace(textureGuid) ||
                    String.IsNullOrWhiteSpace(AssetDatabase.GetAssetPath(material)))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_NONDRAW_CHILD_RESOURCE_NOT_PERSISTENT: source=" +
                        row.sourceComponentId + ";child=" + TransformPath(child.transform) + ";vertices=" +
                        (mesh == null ? -1 : mesh.vertexCount) + ";submeshes=" + (mesh == null ? -1 : mesh.subMeshCount) +
                        ";materials=" + (renderer == null ? -1 : renderer.materialCount) + ";dataGuid=" + dataEvidence.dataAssetGuid);
                readbacks.Add(new ProxySpineNonDrawChild { sourceComponentId = row.sourceComponentId, sourceNode = row.node,
                    noDrawReason = !row.sourceActive ? "inactive-source" : "disabled-source",
                    sourceDataAssetId = dataEvidence.sourceDataAssetId, sourceDataAssetPath = dataEvidence.dataAssetPath,
                    sourceDataAssetGuid = dataEvidence.dataAssetGuid, childPath = SpineChildPath(sourceNode.transform, child.transform),
                    childMaterialGuid = materialGuid, childTextureGuid = textureGuid,
                    sourceOwnerGraphic = owner, sourceChildGraphic = child, sourceChildCanvasRenderer = renderer,
                    sourceDataAssetReference = dataAsset, sourceOwnerEnabled = owner.enabled, sourceNodeActive = row.sourceActive,
                    sourceChildEnabled = child.enabled, sourceChildActiveSelf = child.gameObject.activeSelf,
                    sourceChildActiveInHierarchy = child.gameObject.activeInHierarchy,
                    targetChildEnabled = child.enabled, targetChildActiveInHierarchy = child.gameObject.activeInHierarchy,
                    sourceChildMeshVertexCount = mesh == null ? -1 : mesh.vertexCount,
                    sourceChildMeshSubmeshCount = mesh == null ? -1 : mesh.subMeshCount,
                    sourceChildMaterialCount = renderer == null ? -1 : renderer.materialCount });
            }
            return readbacks.ToArray();
        }

        static bool TryReadSpineIdentity(Graphic owner, string sourceComponentId, out string actualSourceId)
        {
            actualSourceId = null;
            if (owner == null || owner.GetType().FullName != "Spine.Unity.SkeletonGraphic") return false;
            var candidates = owner.GetComponents<Component>().Where(component => component != null &&
                component.GetType().FullName == "UnitySpineSourceIdentity").ToArray();
            if (candidates.Length != 1) return false;
            var marker = candidates[0];
            if (!TryReadSpineMember(marker, "instanceSourceComponentId", out var sourceIdValue) ||
                !TryReadSpineMember(marker, "renderer", out var rendererValue)) return false;
            actualSourceId = sourceIdValue as string;
            return actualSourceId == sourceComponentId && rendererValue as Component == owner;
        }

        static string SpineMeshDiagnostic(string sourceComponentId, Graphic graphic, Mesh mesh)
        {
            var canvas = graphic == null ? null : graphic.canvasRenderer;
            return "source=" + sourceComponentId + ";child=" + (graphic == null ? "<null>" : TransformPath(graphic.transform)) +
                ";vertices=" + (mesh == null ? -1 : mesh.vertexCount) + ";submeshes=" + (mesh == null ? -1 : mesh.subMeshCount) +
                ";materials=" + (canvas == null ? -1 : canvas.materialCount);
        }

        static ProxySpineOwnerDelegation CreateSpineOwnerDelegation(ProxyRendererSpec row,
            Graphic rootGraphic, Mesh rootMesh, List<Graphic> delegatedGraphics,
            SpineDataIdentityEvidence dataEvidence, UnityEngine.Object dataAsset)
        {
            var sourceDataAssetPath = dataEvidence == null ? null : dataEvidence.dataAssetPath;
            var sourceDataAssetGuid = dataEvidence == null ? null : dataEvidence.dataAssetGuid;
            var rootMaterialCount = rootGraphic.canvasRenderer == null ? -1 : rootGraphic.canvasRenderer.materialCount;
            if (!row.sourceEnabled || !row.sourceActive || !rootGraphic.enabled ||
                !rootGraphic.gameObject.activeInHierarchy)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_OWNER_DELEGATION_SOURCE_INACTIVE: " +
                    SpineMeshDiagnostic(row.sourceComponentId, rootGraphic, rootMesh) + ";dataGuid=" + sourceDataAssetGuid);
            if (dataAsset == null || String.IsNullOrWhiteSpace(sourceDataAssetPath) ||
                !sourceDataAssetPath.StartsWith("Assets/", StringComparison.Ordinal) ||
                String.IsNullOrWhiteSpace(sourceDataAssetGuid) ||
                AssetDatabase.LoadAssetAtPath<UnityEngine.Object>(sourceDataAssetPath) != dataAsset)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_OWNER_DELEGATION_DATA_REFERENCE_NOT_PERSISTENT: " +
                    SpineMeshDiagnostic(row.sourceComponentId, rootGraphic, rootMesh) + ";dataPath=" + sourceDataAssetPath +
                    ";dataGuid=" + sourceDataAssetGuid);
            if (!TryReadSpineIdentity(rootGraphic, row.sourceComponentId, out _))
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_OWNER_DELEGATION_SOURCE_IDENTITY_MISMATCH: " +
                    SpineMeshDiagnostic(row.sourceComponentId, rootGraphic, rootMesh) + ";dataGuid=" + sourceDataAssetGuid);
            var registered = new List<CanvasRenderer>();
            if (!TryReadSpineRendererList(rootGraphic, out registered) || registered.Count == 0 ||
                registered.Distinct().Count() != registered.Count)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_OWNER_DELEGATION_REGISTERED_RENDERERS_MISSING: " +
                    SpineMeshDiagnostic(row.sourceComponentId, rootGraphic, rootMesh) + ";registered=" + registered.Count +
                    ";dataGuid=" + sourceDataAssetGuid);
            if (delegatedGraphics == null || delegatedGraphics.Count != registered.Count ||
                delegatedGraphics.Distinct().Count() != delegatedGraphics.Count)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_OWNER_DELEGATION_CHILD_DENOMINATOR_DIFFERS: " +
                    SpineMeshDiagnostic(row.sourceComponentId, rootGraphic, rootMesh) + ";registered=" + registered.Count +
                    ";collected=" + (delegatedGraphics == null ? -1 : delegatedGraphics.Count) + ";dataGuid=" + sourceDataAssetGuid);

            var vertices = new List<int>(); var submeshes = new List<int>(); var materials = new List<int>();
            var renderers = new List<CanvasRenderer>(); var paths = new List<string>();
            var materialGuids = new List<string>(); var textureGuids = new List<string>();
            foreach (var childGraphic in delegatedGraphics)
            {
                var childRenderer = childGraphic == null ? null : childGraphic.canvasRenderer;
                var childMesh = childRenderer == null ? null : childRenderer.GetMesh();
                var materialCount = childRenderer == null ? -1 : childRenderer.materialCount;
                if (childGraphic == null || !IsSpineCanvasSubmesh(childGraphic.gameObject, rootGraphic) ||
                    childRenderer == null || !registered.Contains(childRenderer) || childMesh == null ||
                    childMesh.vertexCount <= 0 || childMesh.subMeshCount <= 0 || materialCount != childMesh.subMeshCount ||
                    materialCount != 1)
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_OWNER_DELEGATION_CHILD_MESH_INVALID: " +
                        SpineMeshDiagnostic(row.sourceComponentId, childGraphic, childMesh) + ";root=" +
                        SpineMeshDiagnostic(row.sourceComponentId, rootGraphic, rootMesh) + ";dataGuid=" + sourceDataAssetGuid);
                var sourceMaterial = childGraphic.material;
                var sourceTexture = sourceMaterial == null || sourceMaterial.mainTexture == null ? childGraphic.mainTexture : sourceMaterial.mainTexture;
                long materialLocal;
                var materialGuid = sourceMaterial == null ? null : AssetGuid(sourceMaterial, out materialLocal);
                var textureGuid = TextureAssetGuid(sourceTexture);
                if (String.IsNullOrWhiteSpace(materialGuid) ||
                    String.IsNullOrWhiteSpace(AssetDatabase.GetAssetPath(sourceMaterial)) ||
                    String.IsNullOrWhiteSpace(textureGuid))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_OWNER_DELEGATION_CHILD_RESOURCE_NOT_PERSISTENT: " +
                        SpineMeshDiagnostic(row.sourceComponentId, childGraphic, childMesh) + ";materialGuid=" + materialGuid +
                        ";textureGuid=" + textureGuid + ";dataGuid=" + sourceDataAssetGuid);
                vertices.Add(childMesh.vertexCount); submeshes.Add(childMesh.subMeshCount); materials.Add(materialCount);
                renderers.Add(childRenderer); paths.Add(SpineChildPath(rootGraphic.transform, childGraphic.transform));
                materialGuids.Add(materialGuid); textureGuids.Add(textureGuid);
            }
            return new ProxySpineOwnerDelegation { sourceComponentId = row.sourceComponentId, sourceNode = row.node,
                sourceDataAssetId = dataEvidence.sourceDataAssetId,
                sourceOwnerGraphic = rootGraphic, sourceDataAssetReference = dataAsset,
                sourceDataAssetPath = sourceDataAssetPath, sourceDataAssetGuid = sourceDataAssetGuid,
                sourceBindingPlanPath = dataEvidence.bindingPlanPath,
                sourceBindingPlanSha256 = dataEvidence.bindingPlanSha256,
                sourceManifestSha256 = dataEvidence.sourceManifestSha256,
                delegatedSourceGraphics = delegatedGraphics.ToArray(), delegatedCanvasRenderers = renderers.ToArray(),
                delegatedChildPaths = paths.ToArray(), delegatedChildMaterialGuids = materialGuids.ToArray(),
                delegatedChildTextureGuids = textureGuids.ToArray(), rootMeshVertexCount = rootMesh == null ? 0 : rootMesh.vertexCount,
                rootMeshSubmeshCount = rootMesh == null ? -1 : rootMesh.subMeshCount, rootCanvasMaterialCount = rootMaterialCount,
                rootMeshWasMissing = rootMesh == null,
                childMeshVertexCounts = vertices.ToArray(), childMeshSubmeshCounts = submeshes.ToArray(),
                childCanvasMaterialCounts = materials.ToArray() };
        }

        static List<Graphic> CollectEventGraphics(ProxyQueueSpec queue, ProxyRendererSpec row, IDictionary<string, GameObject> nodes,
            out ProxySpineOwnerDelegation spineDelegation)
        {
            spineDelegation = null;
            var root = nodes[row.node];
            var result = new List<Graphic>();
            var rootGraphic = root.GetComponent<Graphic>();
            if (rootGraphic == null || rootGraphic.GetType().FullName != row.expectedGraphicType)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_GRAPHIC_MISMATCH: " + row.node + ";source=" + row.sourceComponentId);
            var rootMesh = rootGraphic.canvasRenderer == null ? null : rootGraphic.canvasRenderer.GetMesh();
            var delegateEmptySpineOwner = row.sourceType == "sp.Skeleton" &&
                rootGraphic.GetType().FullName == "Spine.Unity.SkeletonGraphic" && (rootMesh == null || rootMesh.vertexCount == 0);
            if (!delegateEmptySpineOwner) result.Add(rootGraphic);
            void Visit(Transform parent)
            {
                foreach (Transform child in parent)
                {
                    if (IsGeneratedSortProxyRoot(child)) continue;
                    var sourceNode = nodes.FirstOrDefault(pair => pair.Value != null && pair.Value.transform == child).Key;
                    // Every mapped source child is an independent render
                    // boundary, even when that child is inactive, disabled,
                    // or has no current draw event. Its typed renderer row is
                    // handled by its own draw/non-draw contract.
                    if (sourceNode != null && sourceNode != row.node) continue;
                    var graphics = child.GetComponents<Graphic>();
                    if (graphics.Length > 0)
                    {
                        var allowed = row.sourceType == "cc.Label" || row.sourceType == "cc.RichText" ? IsGeneratedTextSubmesh(child.gameObject) :
                            row.sourceType == "sp.Skeleton" && IsSpineCanvasSubmesh(child.gameObject, root.GetComponent<Graphic>());
                        if (!allowed)
                        {
                            var graphicTypes = String.Join(",", graphics.Select(graphic => graphic == null ? "<missing>" : graphic.GetType().FullName).ToArray());
                            throw new InvalidOperationException("STATIC_SORT_PROXY_UNCLASSIFIED_DESCENDANT_GRAPHIC: sourceNode=" + row.node +
                                ";sourceComponent=" + row.sourceComponentId + ";childPath=" + TransformPath(child) +
                                ";graphicTypes=" + graphicTypes);
                        }
                        foreach (var graphic in graphics) result.Add(graphic);
                    }
                    Visit(child);
                }
            }
            Visit(root.transform);
            if (delegateEmptySpineOwner)
            {
                if (!TryReadSpineDataAsset(rootGraphic, out var dataAsset))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_OWNER_DELEGATION_DATA_REFERENCE_MISSING: " +
                        SpineMeshDiagnostic(row.sourceComponentId, rootGraphic, rootMesh));
                if (!TryReadSpineDataIdentity(queue, row.sourceComponentId, dataAsset, out var dataEvidence, out var dataDiagnostic))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SPINE_OWNER_DELEGATION_DATA_REFERENCE_NOT_PERSISTENT: " +
                        SpineMeshDiagnostic(row.sourceComponentId, rootGraphic, rootMesh) + ";sourceDataGuid=" +
                        (dataEvidence == null ? "<unresolved>" : dataEvidence.dataAssetGuid) + ";sourceDataBinding=" + dataDiagnostic);
                spineDelegation = CreateSpineOwnerDelegation(row, rootGraphic, rootMesh, result, dataEvidence, dataAsset);
            }
            return result;
        }

        static bool MeshHasNoVertices(Mesh mesh) => mesh == null || mesh.vertexCount == 0;

        static bool TryCreateEmptyRendererCarrier(ProxyRendererSpec spec, GameObject sourceNode,
            Transform parent, int queueIndex, out NativeStaticSortQueueProxyMarker marker)
        {
            marker = null;
            if (spec == null || sourceNode == null || sourceNode.activeInHierarchy != spec.sourceActive) return false;
            var source = sourceNode.GetComponent<Graphic>();
            Component sourceComponent = source;
            string reason = null;
            var sprite = source as Image;
            var text = source as TMPro.TMP_Text;
            var spriteFrameBound = sprite != null && sprite.sprite != null;
            var textIsEmpty = text != null && String.IsNullOrEmpty(text.GetParsedText());
            var fontMissing = text != null && text.font == null;
            var sourceMesh = source == null || source.canvasRenderer == null ? null : source.canvasRenderer.GetMesh();
            if (!spec.sourceActive)
            {
                if (spec.sourceType == "cc.Graphics")
                {
                    var graphics = sourceNode.GetComponent<NativeStaticGraphics>();
                    sourceComponent = graphics;
                    if (source != null || graphics == null || graphics.enabled || graphics.sourceId != spec.sourceComponentId ||
                        graphics.sourceDrawingCommands != spec.sourceDrawingCommands || !spec.sourceCommandsEmpty ||
                        !GraphicsMaterialGuidsMatch(spec.sourceMaterialGuids, graphics.sourceMaterials)) return false;
                }
                else if (source == null || source.GetType().FullName != spec.expectedGraphicType)
                    return false;
                else if (spec.sourceType == "cc.Sprite" && (sprite == null || spriteFrameBound != spec.sourceTextureBound ||
                    source.enabled != (spec.sourceEnabled && spec.sourceTextureBound))) return false;
                else if ((spec.sourceType == "cc.Label" || spec.sourceType == "cc.RichText") &&
                    (text == null || text.enabled != spec.sourceEnabled ||
                     !String.Equals(text.text ?? String.Empty, spec.nativeTextExpectation ?? String.Empty, StringComparison.Ordinal) ||
                     fontMissing != spec.sourceFontMissing)) return false;
                else if (spec.sourceType != "cc.Sprite" && spec.sourceType != "cc.Label" && spec.sourceType != "cc.RichText" &&
                    source.enabled != spec.sourceEnabled) return false;
                reason = "source-node-inactive";
            }
            else if (!spec.sourceEnabled && source != null && !source.enabled)
                reason = "source-renderer-disabled";
            else if (spec.sourceType == "cc.Sprite")
            {
                // UnityImporter deliberately disables Image when the source
                // Sprite has no frame. Keep that distinction from the source
                // component's authored enabled bit.
                if (!spec.sourceEnabled || spec.sourceTextureBound || sprite == null || spriteFrameBound || source.enabled ||
                    !MeshHasNoVertices(sourceMesh))
                    return false;
                reason = "source-sprite-frame-null-native-image-disabled-zero-mesh";
            }
            else if (spec.sourceType == "cc.Label" || spec.sourceType == "cc.RichText")
            {
                if (!spec.sourceEnabled || !spec.sourceTextEmpty || !textIsEmpty || source.enabled != spec.sourceEnabled ||
                    !String.Equals(text.text ?? String.Empty, spec.nativeTextExpectation ?? String.Empty, StringComparison.Ordinal) ||
                    fontMissing != spec.sourceFontMissing || !MeshHasNoVertices(sourceMesh)) return false;
                reason = "source-text-empty-zero-mesh";
            }
            else if (spec.sourceType == "cc.Graphics")
            {
                var graphics = sourceNode.GetComponent<NativeStaticGraphics>();
                sourceComponent = graphics;
                if (source != null || graphics == null || graphics.enabled || !spec.sourceCommandsEmpty ||
                    spec.sourceDrawingCommands != "not-serialized-empty-in-fixed-state" ||
                    graphics.sourceId != spec.sourceComponentId || graphics.sourceDrawingCommands != spec.sourceDrawingCommands ||
                    !GraphicsMaterialGuidsMatch(spec.sourceMaterialGuids, graphics.sourceMaterials)) return false;
                reason = spec.sourceEnabled ? "source-graphics-command-stream-proven-empty" : "source-renderer-disabled";
            }
            else return false;

            var go = new GameObject("__sort_empty_source_" + queueIndex, typeof(RectTransform),
                typeof(NativeStaticSortQueueProxyMarker));
            go.transform.SetParent(parent, false);
            marker = go.GetComponent<NativeStaticSortQueueProxyMarker>();
            marker.kind = queueIndex >= 0 ? "emptyRenderer" : "retainedNonDraw"; marker.sourceNode = spec.node;
            marker.sourceComponentId = spec.sourceComponentId; marker.sourceType = spec.sourceType;
            marker.queueIndex = queueIndex; marker.sourceGraphic = source; marker.sourceComponent = sourceComponent;
            marker.sourceEnabled = spec.sourceEnabled; marker.sourceActive = spec.sourceActive;
            marker.sourceTextureBound = spec.sourceTextureBound; marker.sourceTextEmpty = spec.sourceTextEmpty;
            marker.sourceFontMissing = spec.sourceFontMissing; marker.sourceText = spec.sourceText ?? String.Empty;
            marker.nativeTextExpectation = spec.nativeTextExpectation ?? String.Empty;
            marker.sourceFieldsJson = spec.sourceFieldsJson ?? String.Empty;
            marker.sourceFieldsSha256 = spec.sourceFieldsSha256 ?? String.Empty;
            marker.sourceDrawingCommands = spec.sourceDrawingCommands ?? String.Empty;
            marker.sourceMaterialGuids = spec.sourceMaterialGuids ?? Array.Empty<string>();
            marker.sourceCommandsEmpty = spec.sourceCommandsEmpty;
            marker.noDrawReason = reason; marker.enabled = false;
            return true;
        }

        static bool GraphicsMaterialGuidsMatch(string[] expected, Material[] actual)
        {
            expected = expected ?? Array.Empty<string>(); actual = actual ?? Array.Empty<Material>();
            return expected.Length == actual.Length && expected.Select((guid, index) =>
            {
                long localId; return !String.IsNullOrWhiteSpace(guid) && actual[index] != null && AssetGuid(actual[index], out localId) == guid;
            }).All(value => value);
        }

        static bool ValidateSourceGraphicCoverage(ProxyQueueSpec spec, IDictionary<string, GameObject> sourceNodes,
            Transform proxyRoot, IList<ProxyGraphicBinding> bindings,
            IEnumerable<ProxySpineOwnerDelegation> spineDelegations,
            IEnumerable<ProxySpineNonDrawChild> spineNonDrawChildren, bool requireGeneratedTextSlots,
            out string missingSourceNode)
        {
            missingSourceNode = null;
            var root = sourceNodes.TryGetValue(spec.rootScope, out var rootObject) ? rootObject : null;
            if (root == null || proxyRoot == null) return false;
            var boundGraphics = new HashSet<Graphic>((bindings ?? Array.Empty<ProxyGraphicBinding>())
                .Where(binding => binding != null && binding.sourceGraphic != null).Select(binding => binding.sourceGraphic));
            foreach (var delegation in spineDelegations ?? Array.Empty<ProxySpineOwnerDelegation>())
                if (delegation != null && delegation.sourceOwnerGraphic != null &&
                    delegation.rootMeshVertexCount == 0 && delegation.delegatedSourceGraphics != null &&
                    delegation.delegatedSourceGraphics.Length > 0)
                    boundGraphics.Add(delegation.sourceOwnerGraphic);
            foreach (var child in spineNonDrawChildren ?? Array.Empty<ProxySpineNonDrawChild>())
                if (child != null && child.sourceChildGraphic != null && child.sourceOwnerGraphic != null &&
                    child.sourceChildCanvasRenderer == child.sourceChildGraphic.canvasRenderer)
                    boundGraphics.Add(child.sourceChildGraphic);
            var textOwners = new HashSet<TMPro.TMP_Text>();
            var textIdentities = proxyRoot.GetComponentsInChildren<NativeStaticSortTextSource>(true)
                .Where(identity => identity != null).ToArray();
            foreach (var identityGroup in textIdentities.GroupBy(identity => identity.sourceComponentId, StringComparer.Ordinal))
            {
                var sourceComponentId = identityGroup.Key;
                if (String.IsNullOrEmpty(sourceComponentId))
                {
                    missingSourceNode = "TMP identity has an empty source component ID";
                    return false;
                }
                var textSpec = (spec.renderers ?? Array.Empty<ProxyRendererSpec>())
                    .SingleOrDefault(row => row != null && row.sourceComponentId == sourceComponentId);
                var expectedTextOwner = textSpec != null && sourceNodes.TryGetValue(textSpec.node, out var textNode) && textNode != null ?
                    textNode.GetComponent<TMPro.TMP_Text>() : null;
                if (expectedTextOwner == null || identityGroup.Any(identity => identity.sourceOwner != expectedTextOwner))
                {
                    missingSourceNode = sourceComponentId + ";expectedOwner=" + (expectedTextOwner != null) +
                        ";identityOwnerMismatch=" + identityGroup.Any(identity => identity.sourceOwner != expectedTextOwner);
                    return false;
                }
                textOwners.Add(expectedTextOwner);
                var identities = identityGroup.ToArray();
                var enumeration = identities[0].textSlotEnumeration;
                try { ValidateTextSlotEnumeration(enumeration, sourceComponentId); }
                catch (Exception error)
                {
                    missingSourceNode = sourceComponentId + ";slotEnumeration=" + error.Message;
                    return false;
                }
                if (identities.Any(identity => !SameTextSlotEnumeration(enumeration, identity.textSlotEnumeration)))
                {
                    missingSourceNode = sourceComponentId + ";slotEnumerationDiffersAcrossIdentities";
                    return false;
                }
                var expectedDrawableSlots = enumeration.rows.Where(row => row.disposition == "drawable")
                    .Select(row => row.slot).OrderBy(slot => slot).ToArray();
                var actualSlots = identities.Select(identity => identity.materialSlot).OrderBy(slot => slot).ToArray();
                if (!expectedDrawableSlots.SequenceEqual(actualSlots) ||
                    actualSlots.Distinct().Count() != actualSlots.Length)
                {
                    missingSourceNode = sourceComponentId + ";drawableSlots=" + String.Join(",", expectedDrawableSlots) +
                        ";identitySlots=" + String.Join(",", actualSlots);
                    return false;
                }
                foreach (var textIdentity in identities)
                {
                    if (!textIdentity.generatedSubmesh)
                    {
                        if (textIdentity.materialSlot != 0 || textIdentity.GetComponent<Graphic>() != (expectedTextOwner as Graphic))
                        {
                            missingSourceNode = sourceComponentId + ";ownerSlotIdentityInvalid=" + textIdentity.materialSlot;
                            return false;
                        }
                        boundGraphics.Add(expectedTextOwner as Graphic);
                        continue;
                    }
                    if (UnityStaticSortTextSource.ResolveGeneratedSlot(textIdentity, expectedTextOwner,
                            textIdentity.sourceComponentId, out var slotBinding, out var slotDiagnostic) &&
                        slotBinding != null && slotBinding.sourceGraphic != null)
                        boundGraphics.Add(slotBinding.sourceGraphic);
                    else if (requireGeneratedTextSlots)
                    {
                        missingSourceNode = textIdentity.sourceComponentId + ";textSlot=" + textIdentity.materialSlot +
                            ";diagnostic=" + slotDiagnostic;
                        return false;
                    }
                }
                var placeholder = enumeration.rows.SingleOrDefault(row => row.disposition == "empty-placeholder");
                if (placeholder != null)
                {
                    var ownerGraphic = expectedTextOwner as Graphic;
                    if (placeholder.slot != 0 || ownerGraphic == null || placeholder.characterReferences != 0 ||
                        placeholder.visibleCharacterReferences != 0 || placeholder.textInfoNondegenerateTriangleCount != 0 ||
                        placeholder.canvasNondegenerateTriangleCount != 0)
                    {
                        missingSourceNode = sourceComponentId + ";placeholderEvidenceInvalid";
                        return false;
                    }
                    // This is the only non-proxied TMP source Graphic accepted:
                    // typed enumeration proves owner slot 0 is zero-area while
                    // every drawable material slot has a proxy identity above.
                    boundGraphics.Add(ownerGraphic);
                }
            }
            foreach (var marker in proxyRoot.GetComponentsInChildren<NativeStaticSortQueueProxyMarker>(true)
                .Where(marker => marker != null && (marker.kind == "emptyRenderer" || marker.kind == "retainedNonDraw") && marker.sourceGraphic != null))
                boundGraphics.Add(marker.sourceGraphic);
            var allowedMaskGraphics = new HashSet<Graphic>();
            foreach (var nodeId in (spec.masks ?? Array.Empty<ProxyMaskSpec>()).Select(mask => mask.node).Distinct(StringComparer.Ordinal))
                if (sourceNodes.TryGetValue(nodeId, out var maskNode) && maskNode != null)
                {
                    var graphic = maskNode.GetComponent<Graphic>();
                    if (graphic != null) allowedMaskGraphics.Add(graphic);
                }
            var nodeIds = sourceNodes.ToDictionary(pair => pair.Value.transform, pair => pair.Key);
            foreach (var graphic in root.GetComponentsInChildren<Graphic>(true))
            {
                if (graphic == null) continue;
                if (!requireGeneratedTextSlots && graphic is TMPro.TMP_SubMeshUI generatedText &&
                    generatedText.textComponent != null && textOwners.Contains(generatedText.textComponent) &&
                    IsGeneratedTextSubmesh(generatedText.gameObject)) continue;
                var cursor = graphic.transform;
                var generatedProxy = false;
                while (cursor != null && cursor != root.transform)
                {
                    if (IsGeneratedSortProxyRoot(cursor)) { generatedProxy = true; break; }
                    cursor = cursor.parent;
                }
                if (generatedProxy || boundGraphics.Contains(graphic) || allowedMaskGraphics.Contains(graphic)) continue;
                var owner = graphic.transform;
                string sourceId = null;
                while (owner != null && owner != root.transform)
                {
                    if (nodeIds.TryGetValue(owner, out sourceId)) break;
                    owner = owner.parent;
                }
                missingSourceNode = sourceId ?? spec.rootScope;
                return false;
            }
            return true;
        }

        static ProxyEmptyRendererReadback ReadEmptyRenderer(ProxyRendererSpec spec,
            IDictionary<string, GameObject> sourceNodes, NativeStaticSortQueueProxyMarker marker)
        {
            var node = sourceNodes.TryGetValue(spec.node, out var sourceNode) ? sourceNode : null;
            var graphic = node == null ? null : node.GetComponent<Graphic>();
            Component sourceComponent = graphic;
            var staticGraphics = node == null ? null : node.GetComponent<NativeStaticGraphics>();
            if (spec.sourceType == "cc.Graphics") sourceComponent = staticGraphics;
            var image = graphic as Image; var text = graphic as TMPro.TMP_Text;
            var mesh = graphic == null || graphic.canvasRenderer == null ? null : graphic.canvasRenderer.GetMesh();
            var sourceTextureBound = image != null && image.sprite != null;
            var sourceTextEmpty = spec.sourceTextEmpty;
            var sourceFontMissing = text != null && text.font == null;
            var sourceText = text == null ? String.Empty : text.text ?? String.Empty;
            var nativeTextEmpty = text != null && String.IsNullOrEmpty(text.GetParsedText());
            var sourceGraphicTypeMatches = spec.sourceType == "cc.Graphics" ? staticGraphics != null &&
                staticGraphics.GetType().FullName == spec.expectedGraphicType : graphic != null && graphic.GetType().FullName == spec.expectedGraphicType;
            var sourceActive = node != null && node.activeInHierarchy;
            var sourceGraphicStateMatches = sourceGraphicTypeMatches && sourceActive == spec.sourceActive &&
                (!spec.sourceActive ? spec.sourceType == "cc.Graphics" ? staticGraphics != null && !staticGraphics.enabled &&
                    staticGraphics.sourceId == spec.sourceComponentId && staticGraphics.sourceDrawingCommands == spec.sourceDrawingCommands &&
                    spec.sourceCommandsEmpty && GraphicsMaterialGuidsMatch(spec.sourceMaterialGuids, staticGraphics.sourceMaterials) :
                    graphic != null && graphic.enabled == spec.sourceEnabled &&
                    (spec.sourceType == "cc.Sprite" ? image != null && (image.sprite != null) == spec.sourceTextureBound &&
                        image.enabled == (spec.sourceEnabled && spec.sourceTextureBound) :
                     spec.sourceType == "cc.Label" || spec.sourceType == "cc.RichText" ? text != null &&
                        String.Equals(sourceText, spec.nativeTextExpectation ?? String.Empty, StringComparison.Ordinal) &&
                        sourceFontMissing == spec.sourceFontMissing : true) :
                 !spec.sourceEnabled ? spec.sourceType == "cc.Graphics" ? staticGraphics != null && !staticGraphics.enabled &&
                    staticGraphics.sourceId == spec.sourceComponentId && staticGraphics.sourceDrawingCommands == spec.sourceDrawingCommands &&
                    spec.sourceCommandsEmpty && GraphicsMaterialGuidsMatch(spec.sourceMaterialGuids, staticGraphics.sourceMaterials) :
                    sourceComponent is Behaviour disabledBehaviour && !disabledBehaviour.enabled :
                 spec.sourceType == "cc.Graphics" ? staticGraphics != null && !staticGraphics.enabled &&
                    staticGraphics.sourceId == spec.sourceComponentId && staticGraphics.sourceDrawingCommands == spec.sourceDrawingCommands &&
                    spec.sourceCommandsEmpty && GraphicsMaterialGuidsMatch(spec.sourceMaterialGuids, staticGraphics.sourceMaterials) :
                 spec.sourceType == "cc.Sprite" ? image != null && !image.enabled && image.sprite == null &&
                    spec.sourceEnabled && !spec.sourceTextureBound :
                 spec.sourceType == "cc.Label" || spec.sourceType == "cc.RichText" ? text != null &&
                    text.enabled == spec.sourceEnabled && nativeTextEmpty == spec.sourceTextEmpty &&
                    String.Equals(sourceText, spec.nativeTextExpectation ?? String.Empty, StringComparison.Ordinal) &&
                    sourceFontMissing == spec.sourceFontMissing : !spec.sourceEnabled && graphic != null && !graphic.enabled);
            var noMesh = spec.sourceType == "cc.Graphics" ? spec.sourceCommandsEmpty : MeshHasNoVertices(mesh);
            var markerExpected = marker != null && (marker.kind == "emptyRenderer" || marker.kind == "retainedNonDraw") && marker.sourceNode == spec.node &&
                marker.sourceComponentId == spec.sourceComponentId && marker.sourceType == spec.sourceType &&
                (marker.kind == "emptyRenderer" ? marker.queueIndex >= 0 : marker.queueIndex == -1) && marker.noDrawReason != null && !marker.enabled;
            var expectedSourceFieldsJson = spec.sourceFieldsJson ?? String.Empty;
            var expectedSourceFieldsSha256 = spec.sourceFieldsSha256 ?? String.Empty;
            var expectedSourceDrawingCommands = spec.sourceDrawingCommands ?? String.Empty;
            var fieldsJsonVerified = String.IsNullOrEmpty(expectedSourceFieldsJson) ? String.IsNullOrEmpty(expectedSourceFieldsSha256) :
                HashText(expectedSourceFieldsJson) == expectedSourceFieldsSha256;
            var typedFieldsVerified = markerExpected && marker.sourceGraphic == graphic && marker.sourceComponent == sourceComponent &&
                marker.sourceEnabled == spec.sourceEnabled && marker.sourceActive == spec.sourceActive &&
                marker.sourceTextureBound == spec.sourceTextureBound && marker.sourceTextEmpty == spec.sourceTextEmpty &&
                marker.sourceFontMissing == spec.sourceFontMissing &&
                String.Equals(marker.sourceText ?? String.Empty, spec.sourceText ?? String.Empty, StringComparison.Ordinal) &&
                String.Equals(marker.nativeTextExpectation ?? String.Empty, spec.nativeTextExpectation ?? String.Empty, StringComparison.Ordinal) &&
                String.Equals(marker.sourceFieldsJson ?? String.Empty, expectedSourceFieldsJson, StringComparison.Ordinal) &&
                String.Equals(marker.sourceFieldsSha256 ?? String.Empty, expectedSourceFieldsSha256, StringComparison.Ordinal) &&
                marker.sourceCommandsEmpty == spec.sourceCommandsEmpty &&
                String.Equals(marker.sourceDrawingCommands ?? String.Empty, expectedSourceDrawingCommands, StringComparison.Ordinal) &&
                (marker.sourceMaterialGuids ?? Array.Empty<string>()).SequenceEqual(spec.sourceMaterialGuids ?? Array.Empty<string>()) &&
                fieldsJsonVerified;
            string carrierGuid = null; long carrierLocalId = 0;
            var carrierPersistent = marker != null && AssetDatabase.TryGetGUIDAndLocalFileIdentifier(marker, out carrierGuid, out carrierLocalId) &&
                !String.IsNullOrWhiteSpace(carrierGuid) && carrierLocalId != 0;
            var materialCount = graphic == null || graphic.canvasRenderer == null ? -1 : graphic.canvasRenderer.materialCount;
            var actualMaterialGuids = staticGraphics == null ? Array.Empty<string>() :
                (staticGraphics.sourceMaterials ?? Array.Empty<Material>()).Select(material =>
                { long id; return material == null ? null : AssetGuid(material, out id); }).ToArray();
            var expectedReason = !spec.sourceActive ? "source-node-inactive" : !spec.sourceEnabled ? "source-renderer-disabled" :
                spec.sourceType == "cc.Sprite" ? "source-sprite-frame-null-native-image-disabled-zero-mesh" :
                spec.sourceType == "cc.Label" || spec.sourceType == "cc.RichText" ? "source-text-empty-zero-mesh" :
                spec.sourceType == "cc.Graphics" ? "source-graphics-command-stream-proven-empty" : "source-renderer-disabled";
            var markerReasonVerified = marker != null && marker.noDrawReason == expectedReason;
            var verified = sourceGraphicStateMatches && (noMesh || !spec.sourceActive || (!spec.sourceEnabled && graphic != null && !graphic.enabled)) &&
                typedFieldsVerified && carrierPersistent && markerReasonVerified &&
                (spec.sourceType != "cc.Graphics" || actualMaterialGuids.SequenceEqual(spec.sourceMaterialGuids ?? Array.Empty<string>()));
            return new ProxyEmptyRendererReadback { sourceComponentId = spec.sourceComponentId, sourceNode = spec.node,
                sourceType = spec.sourceType, noDrawReason = marker == null ? null : marker.noDrawReason,
                sourceComponentType = sourceComponent == null ? null : sourceComponent.GetType().FullName,
                sourceFieldsSha256 = marker == null ? null : marker.sourceFieldsSha256,
                sourceDrawingCommands = marker == null ? null : marker.sourceDrawingCommands,
                sourceText = marker == null ? null : marker.sourceText,
                nativeTextExpectation = spec.nativeTextExpectation,
                nativeText = text == null ? String.Empty : text.text ?? String.Empty,
                sourceMaterialGuids = marker == null ? null : marker.sourceMaterialGuids,
                actualSourceMaterialGuids = actualMaterialGuids,
                carrierGuid = carrierGuid, carrierLocalFileId = carrierLocalId,
                sourceEnabled = spec.sourceEnabled, sourceActive = spec.sourceActive,
                nativeGraphicEnabled = graphic != null && graphic.enabled,
                nativeComponentEnabled = sourceComponent is Behaviour behaviour && behaviour.enabled,
                sourceActiveInHierarchy = sourceActive,
                sourceTextureBound = spec.sourceTextureBound, nativeTextureBound = sourceTextureBound,
                sourceTextEmpty = spec.sourceTextEmpty, nativeTextEmpty = nativeTextEmpty,
                sourceFontMissing = spec.sourceFontMissing, nativeFontMissing = sourceFontMissing,
                sourceMeshPresent = mesh != null && mesh.vertexCount > 0, sourceMeshVertexCount = mesh == null ? 0 : mesh.vertexCount,
                sourceCanvasMaterialCount = materialCount, actualQueueIndex = marker == null ? -1 : marker.queueIndex,
                carrierPresent = carrierPersistent, sourceReferenceVerified = marker != null && marker.sourceComponent == sourceComponent,
                typedFieldsVerified = typedFieldsVerified, sourceCommandsEmpty = spec.sourceCommandsEmpty,
                nativeCommandsEmpty = spec.sourceType == "cc.Graphics" && staticGraphics != null &&
                    staticGraphics.sourceDrawingCommands == "not-serialized-empty-in-fixed-state", verified = verified };
        }

        static NativeStaticSortQueueProxyGraphic CreateProxyGraphic(Graphic source, Graphic sourceOwnerGraphic, string sourceNodeId,
            string sourceComponentId, string sourceType, int queueIndex, int submeshIndex,
            string expectedGraphicType, bool generatedSourceChild, Transform parent, string meshFolder,
            TextSlotBinding textBinding, out ProxyGraphicBinding binding)
        {
            if (textBinding == null) Canvas.ForceUpdateCanvases();
            var stableSourceGraphic = textBinding == null ? source : (Graphic)textBinding.owner;
            var sourceCanvasRenderer = source.canvasRenderer;
            var sourceMesh = textBinding != null ? textBinding.sourceMesh : sourceCanvasRenderer == null ? null : sourceCanvasRenderer.GetMesh();
            if (sourceMesh == null || sourceMesh.vertexCount == 0)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_MESH_EMPTY: " + sourceComponentId);
            if (HasMalformedUvChannels(sourceMesh))
                throw new InvalidOperationException("STATIC_SORT_PROXY_MALFORMED_UV_CHANNELS: " + sourceComponentId);
            var materialCount = Math.Max(1, sourceCanvasRenderer.materialCount);
            if (sourceMesh.subMeshCount != materialCount)
                throw new InvalidOperationException("STATIC_SORT_PROXY_MATERIAL_MESH_SUBMESH_MISMATCH: " + sourceComponentId);
            var rt = source.transform as RectTransform;
            if (rt == null) throw new InvalidOperationException("STATIC_SORT_PROXY_RECTTRANSFORM_MISSING: " + sourceComponentId);
            var proxyObject = new GameObject("__sort_proxy_" + queueIndex + "_" + submeshIndex,
                typeof(RectTransform), typeof(CanvasRenderer), typeof(NativeStaticSortQueueProxyGraphic),
                typeof(NativeStaticSortQueueProxyMarker), typeof(CanvasGroup));
            var proxyRect = proxyObject.GetComponent<RectTransform>();
            CopyWorldRect(rt, proxyRect, parent, sourceNodeId);
            // Graphic.material is the authored base material. CanvasRenderer's
            // installed material may already include an ancestor Mask stencil
            // modifier, so it must never seed the proxy material.
            var sourceMaterial = textBinding != null ? textBinding.sourceMaterial : source.material;
            if (textBinding != null && sourceMaterial == null)
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SOURCE_MATERIAL_MISSING: " + sourceComponentId);
            if (sourceMaterial == null) sourceMaterial = Canvas.GetDefaultCanvasMaterial();
            if (sourceMaterial == null) throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_MATERIAL_MISSING: " + sourceComponentId);
            var sourceMaterialFingerprint = MaterialFingerprint(sourceMaterial);
            var texture = textBinding != null ? textBinding.sourceTexture : sourceMaterial.mainTexture ?? source.mainTexture;
            if (textBinding != null && texture == null)
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SOURCE_TEXTURE_MISSING: " + sourceComponentId);
            var mesh = PersistMesh(sourceMesh, submeshIndex, source.transform, proxyRect,
                sourceComponentId, submeshIndex, meshFolder, out var sourceMeshSha, out var meshSha, out var meshGuid);
            var material = textBinding != null ? textBinding.proxyMaterial : sourceMaterial;
            if (textBinding != null && material == null)
                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_PROXY_MATERIAL_MISSING: " + sourceComponentId);
            if (string.IsNullOrEmpty(AssetDatabase.GetAssetPath(material)) ||
                !AssetDatabase.GetAssetPath(material).StartsWith("Assets/", StringComparison.Ordinal))
            {
                if (textBinding != null)
                    throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_PROXY_MATERIAL_NOT_PERSISTENT: " + sourceComponentId);
                var materialPath = meshFolder.TrimEnd('/') + "/QueueMaterial_" + HashText(sourceComponentId + sourceMaterialFingerprint).Substring(0, 20) + ".mat";
                var persisted = AssetDatabase.LoadAssetAtPath<Material>(materialPath);
                if (persisted == null)
                {
                    Directory.CreateDirectory(Path.GetDirectoryName(materialPath));
                    persisted = new Material(material) { name = material.name };
                    AssetDatabase.CreateAsset(persisted, materialPath);
                }
                material = persisted;
            }
            var materialGuid = AssetGuid(material, out var materialLocal);
            var textureGuid = TextureAssetGuid(texture);
            if (materialGuid == null || textureGuid == null)
                throw new InvalidOperationException("STATIC_SORT_PROXY_RESOURCE_NOT_PERSISTENT: " + sourceComponentId);
            var proxy = proxyObject.GetComponent<NativeStaticSortQueueProxyGraphic>();
            proxy.sourceGraphic = stableSourceGraphic; proxy.sourceOwnerGraphic = sourceOwnerGraphic;
            proxy.sourceNodeId = sourceNodeId; proxy.sourceComponentId = sourceComponentId;
            proxy.sourceType = sourceType; proxy.queueIndex = queueIndex; proxy.submeshIndex = submeshIndex;
            proxy.expectedSourceGraphicType = expectedGraphicType; proxy.generatedSourceChild = generatedSourceChild;
            proxy.sourceRendererAlpha = sourceCanvasRenderer.GetAlpha();
            proxy.sourceInheritedAlpha = sourceCanvasRenderer.GetInheritedAlpha();
            proxy.sourceOpacityCaptured = true;
            proxy.proxyMesh = mesh; proxy.proxyTexture = texture; proxy.proxyBaseMaterial = material;
            proxy.sourceMeshSha256 = sourceMeshSha; proxy.meshContentSha256 = meshSha; proxy.meshAssetGuid = meshGuid;
            proxy.sourceUvChannelVertexCounts = UvChannelVertexCounts(sourceMesh);
            proxy.sourceUvChannelDimensions = UvChannelDimensions(sourceMesh);
            proxy.sourceMaterialGuid = materialGuid; proxy.sourceTextureGuid = textureGuid;
            proxy.sourceBaseTexture = texture; proxy.sourceMaterialFingerprint = sourceMaterialFingerprint;
            proxy.raycastTarget = false; proxy.color = Color.white;
            var opacity = proxyObject.GetComponent<CanvasGroup>();
            opacity.ignoreParentGroups = true;
            opacity.alpha = proxy.sourceInheritedAlpha;
            proxyObject.GetComponent<CanvasRenderer>().SetAlpha(proxy.sourceRendererAlpha);
            var marker = proxyObject.GetComponent<NativeStaticSortQueueProxyMarker>();
            marker.kind = "renderer"; marker.sourceNode = sourceNodeId; marker.sourceComponentId = sourceComponentId;
            marker.sourceType = sourceType; marker.queueIndex = queueIndex;
            if (textBinding != null) UnityStaticSortTextSource.Attach(proxyObject, textBinding, mesh, meshSha);
            binding = new ProxyGraphicBinding { sourceGraphic = stableSourceGraphic,
                sourceCanvasRenderer = stableSourceGraphic == null ? null : stableSourceGraphic.canvasRenderer,
                proxyGraphics = new[] { proxy }, sourceGraphicEnabled = stableSourceGraphic != null && stableSourceGraphic.enabled,
                sourceCanvasCullBefore = stableSourceGraphic != null && stableSourceGraphic.canvasRenderer != null &&
                    stableSourceGraphic.canvasRenderer.cull };
            return proxy;
        }

        public static ProxyQueueReadback CreateStaticSortQueueProxy(ProxyQueueSpec spec,
            IDictionary<string, GameObject> sourceNodes, Func<string, Sprite> resolveSprite,
            Func<MaskSpec, Material> resolveMaskMaterial)
        {
            if (spec == null || sourceNodes == null || !sourceNodes.TryGetValue(spec.rootScope, out var sourceRoot) || sourceRoot == null)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_ROOT_MISSING");
            using (var capture = new NestedProxyCaptureScope(NestedProxyRoots(sourceRoot)))
                return CreateStaticSortQueueProxyCore(spec, sourceNodes, resolveSprite, resolveMaskMaterial, capture);
        }

        static ProxyQueueReadback CreateStaticSortQueueProxyCore(ProxyQueueSpec spec,
            IDictionary<string, GameObject> sourceNodes, Func<string, Sprite> resolveSprite,
            Func<MaskSpec, Material> resolveMaskMaterial, NestedProxyCaptureScope nestedCapture)
        {
            if (spec == null || sourceNodes == null || string.IsNullOrEmpty(spec.rootScope))
                throw new InvalidOperationException("STATIC_SORT_PROXY_PLAN_INVALID");
            if (string.IsNullOrEmpty(spec.meshAssetFolder) || !spec.meshAssetFolder.StartsWith("Assets/", StringComparison.Ordinal))
                throw new InvalidOperationException("STATIC_SORT_PROXY_ASSET_FOLDER_INVALID");
            if (!sourceNodes.TryGetValue(spec.rootScope, out var sourceRoot) || sourceRoot == null)
                throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_ROOT_MISSING");
            if (sourceRoot.GetComponentsInChildren<NativeStaticSortQueueProxyMarker>(true).Any(marker => marker != null &&
                marker.kind == "root" && marker.sourceRootOwner == sourceRoot && IsGeneratedSortProxyRoot(marker.transform)))
                throw new InvalidOperationException("STATIC_SORT_PROXY_ROOT_ALREADY_EXISTS: " + spec.rootScope);
            Canvas.ForceUpdateCanvases();
            if (!AssetDatabase.IsValidFolder(spec.meshAssetFolder))
            {
                var parent = Path.GetDirectoryName(spec.meshAssetFolder).Replace("\\", "/");
                var leaf = Path.GetFileName(spec.meshAssetFolder);
                if (!AssetDatabase.IsValidFolder(parent)) throw new InvalidOperationException("STATIC_SORT_PROXY_PARENT_ASSET_FOLDER_MISSING: " + parent);
                AssetDatabase.CreateFolder(parent, leaf);
            }
            var ownerTextStyles = PrepareSourceGeometryForCapture(spec, sourceNodes, sourceRoot);

            var sourceRendererByComponent = (spec.renderers ?? Array.Empty<ProxyRendererSpec>()).ToDictionary(row => row.sourceComponentId);
            var maskByNode = (spec.masks ?? Array.Empty<ProxyMaskSpec>()).ToDictionary(row => row.node);
            var sourceParent = sourceRoot.transform;
            var proxyRootObject = new GameObject("__NativeStaticSortQueueProxy_" + HashText(spec.rootScope).Substring(0, 12),
                typeof(RectTransform), typeof(LayoutElement));
            proxyRootObject.GetComponent<LayoutElement>().ignoreLayout = true;
            var proxyRoot = proxyRootObject.GetComponent<RectTransform>();
            var sourceRootRect = sourceRoot.transform as RectTransform;
            if (sourceRootRect == null) throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_ROOT_RECTTRANSFORM_REQUIRED");
            CopyWorldRect(sourceRootRect, proxyRoot, sourceParent, spec.rootScope);
            var rootMarker = proxyRootObject.AddComponent<NativeStaticSortQueueProxyMarker>();
            rootMarker.kind = "root"; rootMarker.sourceNode = spec.rootScope; rootMarker.sourceRootOwner = sourceRoot;
            var bindings = new List<ProxyGraphicBinding>();
            var spineOwnerDelegations = new List<ProxySpineOwnerDelegation>();
            var spineNonDrawChildren = new List<ProxySpineNonDrawChild>();
            var maskBindings = new List<ProxyMaskBinding>();
            var nestedProxyRoots = NestedProxyRoots(sourceRoot);
            var nestedProxyActiveBefore = nestedProxyRoots.Select(root =>
            {
                var marker = root.GetComponent<NativeStaticSortQueueProxyMarker>();
                return marker != null && marker.generatedRootActiveBefore;
            }).ToArray();
            var maskProxyIds = new List<string>();
            var containerStack = new Stack<Transform>(); containerStack.Push(proxyRoot);
            var maskNodeStack = new Stack<string>();
            var queueIndex = 0;
            foreach (var item in spec.drawEvents ?? Array.Empty<ProxyDrawEventSpec>())
            {
                if (item.kind == "maskEnter")
                {
                    if (!maskByNode.TryGetValue(item.node, out var maskSpec) || !sourceNodes.TryGetValue(item.node, out var sourceMaskNode))
                        throw new InvalidOperationException("STATIC_SORT_PROXY_MASK_SOURCE_MISSING: " + item.node);
                    var maskObject = new GameObject("__sort_mask_" + queueIndex++, typeof(RectTransform), typeof(CanvasRenderer),
                        typeof(NativeStaticSortQueueProxyMarker));
                    var maskRect = maskObject.GetComponent<RectTransform>();
                    var sourceMaskRect = sourceMaskNode.transform as RectTransform;
                    if (sourceMaskRect == null) throw new InvalidOperationException("STATIC_SORT_PROXY_MASK_RECTTRANSFORM_MISSING: " + item.node);
                    CopyWorldRect(sourceMaskRect, maskRect, containerStack.Peek(), item.node);
                    var marker = maskObject.GetComponent<NativeStaticSortQueueProxyMarker>();
                    marker.kind = "mask"; marker.sourceNode = item.node; marker.sourceType = "cc.Mask";
                    marker.maskType = maskSpec.maskType; marker.sourceInverted = maskSpec.inverted;
                    var nativeMask = new MaskSpec { sourceId = maskSpec.sourceId, nativeId = maskSpec.nativeId,
                        node = "proxy:" + item.node, enabled = maskSpec.enabled, maskType = maskSpec.maskType,
                        inverted = maskSpec.inverted, alphaThreshold = maskSpec.alphaThreshold,
                        spriteFrameUuid = maskSpec.spriteFrameUuid, sourceFieldsJson = maskSpec.sourceFieldsJson,
                        sourceMaterialId = maskSpec.sourceMaterialId ?? String.Empty,
                        resolvedSourceMaterialId = maskSpec.resolvedSourceMaterialId ?? String.Empty,
                        sourceEffectId = maskSpec.sourceEffectId ?? String.Empty,
                        sourceEffectName = maskSpec.sourceEffectName ?? String.Empty,
                        sourceEffectDocumentSha256 = maskSpec.sourceEffectDocumentSha256 ?? String.Empty,
                        unityMaskShaderPath = maskSpec.unityMaskShaderPath, unityMaskShaderSha256 = maskSpec.unityMaskShaderSha256,
                        unityMaskMaterialGuid = maskSpec.unityMaskMaterialGuid, unityMaskMaterialPath = maskSpec.unityMaskMaterialPath };
                    // Always use stencil Mask on the render proxy. RectMask2D
                    // uses an axis-aligned clip rect and cannot represent a
                    // rotated source mask shape exactly.
                    UnityStaticMaskSort.CreateStaticMasks(new[] { nativeMask },
                        new Dictionary<string, GameObject> { [nativeMask.node] = maskObject }, resolveSprite, resolveMaskMaterial);
                    var sourceMaskComponent = (Component)sourceMaskNode.GetComponent<Mask>() ?? sourceMaskNode.GetComponent<RectMask2D>();
                    var proxyMaskComponent = maskObject.GetComponent<Mask>();
                    if (sourceMaskComponent == null || proxyMaskComponent == null)
                        throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_OR_PROXY_MASK_REFERENCE_MISSING: " + maskSpec.sourceId);
                    maskBindings.Add(new ProxyMaskBinding { sourceId = maskSpec.sourceId, sourceNode = item.node,
                        sourceMask = sourceMaskComponent, proxyMask = proxyMaskComponent });
                    containerStack.Peek().gameObject.GetComponent<NativeStaticSortQueueProxyMarker>();
                    containerStack.Push(maskRect); maskNodeStack.Push(item.node); maskProxyIds.Add(item.node);
                }
                else if (item.kind == "maskExit")
                {
                    if (containerStack.Count <= 1 || maskNodeStack.Count == 0 || maskNodeStack.Pop() != item.node)
                        throw new InvalidOperationException("STATIC_SORT_PROXY_MASK_EVENT_STACK_MISMATCH: " + item.node);
                    containerStack.Pop();
                }
                else if (item.kind == "renderer")
                {
                    if (!sourceRendererByComponent.TryGetValue(item.sourceComponentId, out var row) ||
                        !sourceNodes.TryGetValue(row.node, out var sourceNode))
                        throw new InvalidOperationException("STATIC_SORT_PROXY_RENDERER_SOURCE_MISSING: " + item.sourceComponentId);
                    if (row.sourceType == "cc.Graphics")
                    {
                        if (!TryCreateEmptyRendererCarrier(row, sourceNode, containerStack.Peek(), queueIndex++, out var graphicsCarrier))
                            throw new InvalidOperationException("STATIC_SORT_PROXY_GRAPHICS_EMPTY_SOURCE_PROOF_FAILED: " + item.sourceComponentId);
                        continue;
                    }
                    var graphics = CollectEventGraphics(spec, row, sourceNodes, out var spineDelegation);
                    if (spineDelegation != null) spineOwnerDelegations.Add(spineDelegation);
                    if (row.sourceType == "cc.Label" || row.sourceType == "cc.RichText")
                    {
                        var textOwner = sourceNode.GetComponent<TMPro.TMP_Text>();
                        if (textOwner == null)
                            throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_OWNER_MISSING: " + item.sourceComponentId);
                        var textInfo = textOwner.textInfo;
                        var hasTextGeometry = textInfo != null && textInfo.meshInfo != null &&
                            Enumerable.Range(0, Mathf.Min(textInfo.materialCount, textInfo.meshInfo.Length))
                                .Any(index => textInfo.meshInfo[index].mesh != null && textInfo.meshInfo[index].mesh.vertexCount > 0);
                        if (!hasTextGeometry)
                        {
                            if (!TryCreateEmptyRendererCarrier(row, sourceNode, containerStack.Peek(), queueIndex++, out var emptyTextCarrier))
                                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_EMPTY_SOURCE_PROOF_FAILED: " + item.sourceComponentId);
                            continue;
                        }
                        ownerTextStyles.TryGetValue(row.sourceComponentId, out var ownerStyle);
                        var textSlots = CaptureAndRebindTextSlots(spec, row, textOwner, ownerStyle, out var textSlotEnumeration);
                        var expectedGraphics = textSlots.Select(binding => binding.sourceGraphic).ToHashSet();
                        var placeholder = textSlotEnumeration.rows.SingleOrDefault(slot => slot.disposition == "empty-placeholder");
                        if (placeholder != null)
                        {
                            if (placeholder.slot != 0 || !expectedGraphics.Add(textOwner as Graphic))
                                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_PLACEHOLDER_OWNER_GRAPHIC_INVALID: " +
                                    item.sourceComponentId + ";slot=" + placeholder.slot);
                        }
                        var collectedGraphics = graphics.ToHashSet();
                        if (expectedGraphics.Contains(null) || expectedGraphics.Count != graphics.Count ||
                            !expectedGraphics.SetEquals(collectedGraphics))
                            throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_GRAPHIC_DENOMINATOR_DIFFERS: " +
                                item.sourceComponentId + ";drawableSlots=" + textSlots.Count + ";placeholder=" +
                                (placeholder == null ? "none" : placeholder.slot.ToString()) + ";graphics=" +
                                String.Join(",", graphics.Select(graphic => graphic == null ? "null" : graphic.GetType().Name + ":" + graphic.name)));
                        foreach (var textBinding in textSlots)
                        {
                            var sourceGraphic = textBinding.sourceGraphic;
                            var canvasRenderer = sourceGraphic == null ? null : sourceGraphic.canvasRenderer;
                            var sourceMesh = textBinding.sourceMesh;
                            var materialCount = canvasRenderer == null ? -1 : Math.Max(1, canvasRenderer.materialCount);
                            if (sourceGraphic == null || canvasRenderer == null || sourceMesh == null || sourceMesh.vertexCount == 0)
                                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_FINAL_MESH_EMPTY: " +
                                    item.sourceComponentId + ";slot=" + textBinding.materialSlot);
                            if (materialCount != sourceMesh.subMeshCount || materialCount != 1)
                                throw new InvalidOperationException("STATIC_SORT_PROXY_TEXT_SLOT_SUBMESH_DENOMINATOR_UNPROVEN: " +
                                    item.sourceComponentId + ";slot=" + textBinding.materialSlot +
                                    ";materials=" + materialCount + ";submeshes=" + sourceMesh.subMeshCount);
                            CreateProxyGraphic(sourceGraphic, sourceNode.GetComponent<Graphic>(), row.node, item.sourceComponentId,
                                row.sourceType, queueIndex++, 0, row.expectedGraphicType, sourceGraphic.gameObject != sourceNode,
                                containerStack.Peek(), spec.meshAssetFolder, textBinding, out var textProxyBinding);
                            bindings.Add(textProxyBinding);
                        }
                        continue;
                    }
                    foreach (var sourceGraphic in graphics)
                    {
                        var canvasRenderer = sourceGraphic.canvasRenderer;
                        EnsureSourceGraphicMeshReady(sourceGraphic);
                        var sourceMesh = canvasRenderer.GetMesh();
                        var materialCount = Math.Max(1, canvasRenderer.materialCount);
                        if (sourceMesh == null || sourceMesh.vertexCount == 0)
                        {
                            if (!TryCreateEmptyRendererCarrier(row, sourceNode, containerStack.Peek(), queueIndex++, out var emptyCarrier))
                                throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_MESH_MATERIAL_COUNT_MISMATCH: " +
                                    SpineMeshDiagnostic(item.sourceComponentId, sourceGraphic, sourceMesh));
                            continue;
                        }
                        if (materialCount != sourceMesh.subMeshCount)
                            throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_MESH_MATERIAL_COUNT_MISMATCH: " +
                                SpineMeshDiagnostic(item.sourceComponentId, sourceGraphic, sourceMesh));
                        if (materialCount != 1)
                            throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_BASE_MATERIAL_PER_SUBMESH_UNPROVEN: " + item.sourceComponentId);
                        for (var submesh = 0; submesh < materialCount; submesh++)
                        {
                            CreateProxyGraphic(sourceGraphic, sourceNode.GetComponent<Graphic>(), row.node, item.sourceComponentId, row.sourceType,
                                queueIndex++, submesh, row.expectedGraphicType, sourceGraphic.gameObject != sourceNode,
                                containerStack.Peek(), spec.meshAssetFolder, null, out var binding);
                            bindings.Add(binding);
                        }
                    }
                }
                else throw new InvalidOperationException("STATIC_SORT_PROXY_DRAW_EVENT_UNKNOWN: " + item.kind);
            }
            foreach (var row in spec.nonDrawRenderers ?? Array.Empty<ProxyRendererSpec>())
            {
                if (row == null || !sourceNodes.TryGetValue(row.node, out var disabledNode) ||
                    row.sourceEnabled && row.sourceActive)
                    throw new InvalidOperationException("STATIC_SORT_PROXY_NON_DRAW_SPEC_INVALID: " + (row == null ? "null" : row.sourceComponentId));
                if (!TryCreateEmptyRendererCarrier(row, disabledNode, proxyRoot, -1, out var carrier))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_NON_DRAW_SOURCE_PROOF_FAILED: " + row.sourceComponentId);
                if (row.sourceType == "sp.Skeleton")
                    spineNonDrawChildren.AddRange(CaptureSpineNonDrawChildren(spec, row, disabledNode, sourceNodes));
            }
            if (containerStack.Count != 1 || maskNodeStack.Count != 0)
                throw new InvalidOperationException("STATIC_SORT_PROXY_UNCLOSED_MASK_SCOPE");
            var presenter = proxyRootObject.AddComponent<NativeStaticSortQueueProxyPresenter>();
            presenter.sourceRootId = spec.rootScope; presenter.sourcePrefabId = spec.sourcePrefabId;
            presenter.prefabPath = spec.prefabPath; presenter.sourceRoot = sourceRoot; presenter.proxyRoot = proxyRootObject;
            presenter.queueSha256 = HashText(string.Join("|", (spec.drawEvents ?? Array.Empty<ProxyDrawEventSpec>())
                .Select(row => row.kind + ":" + row.node + ":" + row.sourceComponentId)));
            presenter.bindings = bindings.ToArray();
            presenter.maskBindings = maskBindings.ToArray();
            presenter.spineOwnerDelegations = spineOwnerDelegations.ToArray();
            presenter.spineNonDrawChildren = spineNonDrawChildren.ToArray();
            presenter.nestedProxyRoots = nestedProxyRoots.ToArray();
            presenter.nestedProxyRootActiveBefore = nestedProxyActiveBefore;
            presenter.nestedProxyPresenters = nestedProxyRoots.Select(root =>
                root.GetComponent<NativeStaticSortQueueProxyPresenter>()).ToArray();
            if (!ValidateSourceGraphicCoverage(spec, sourceNodes, proxyRootObject.transform, bindings,
                    spineOwnerDelegations, spineNonDrawChildren, true, out var uncoveredSourceNode))
                throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_GRAPHIC_UNCOVERED: " + uncoveredSourceNode);
            presenter.InitializePresentation();
            nestedCapture.Commit();
            var sourceFields = spec.sourceFields ?? Array.Empty<QueueSortFieldSpec>();
            foreach (var field in sourceFields)
            {
                if (!sourceNodes.TryGetValue(field.node, out var fieldNode))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_FIELD_NODE_MISSING: " + field.sourceId);
                var identity = fieldNode.GetComponent<NativeStaticSortOrderIdentity>();
                if (identity == null || identity.sourceId != field.sourceId || identity.nativeId != field.nativeId ||
                    identity.sourceSortOrder != field.sortOrder || identity.enabledInSource != field.enabled)
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_SORTORDER_IDENTITY_MISSING_OR_DIFFERS: " + field.sourceId);
            }
            foreach (var field in spec.sourceSortRoots ?? Array.Empty<ProxySortRootFieldSpec>())
            {
                if (!sourceNodes.TryGetValue(field.node, out var fieldNode))
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_SORTROOT_NODE_MISSING: " + field.sourceId);
                var identity = fieldNode.GetComponent<NativeStaticSortRootIdentity>();
                if (identity == null || identity.sourceId != field.sourceId || identity.nativeId != field.nativeId ||
                    identity.enabledInSource != field.enabled)
                    throw new InvalidOperationException("STATIC_SORT_PROXY_SOURCE_SORTROOT_IDENTITY_MISSING_OR_DIFFERS: " + field.sourceId);
            }
            AssetDatabase.SaveAssets();
            return ReadProxy(spec, sourceNodes, proxyRootObject, presenter, resolveSprite, resolveMaskMaterial,
                verifyRuntimeGeometry: true, requireSavedPrefabAsset: false, provisional: true);
        }

        public static ProxyQueueReadback ReadStaticSortQueueProxy(ProxyQueueSpec spec,
            IDictionary<string, GameObject> sourceNodes, GameObject proxyRoot, NativeStaticSortQueueProxyPresenter presenter,
            Func<string, Sprite> resolveSprite = null, Func<MaskSpec, Material> resolveMaskMaterial = null)
        {
            return ReadProxy(spec, sourceNodes, proxyRoot, presenter, resolveSprite, resolveMaskMaterial,
                verifyRuntimeGeometry: true, requireSavedPrefabAsset: true, provisional: false);
        }

        public static ProxyQueueReadback ReadPersistentSortQueueProxy(ProxyQueueSpec spec,
            IDictionary<string, GameObject> sourceNodes, GameObject proxyRoot, NativeStaticSortQueueProxyPresenter presenter,
            Func<string, Sprite> resolveSprite = null, Func<MaskSpec, Material> resolveMaskMaterial = null)
        {
            return ReadProxy(spec, sourceNodes, proxyRoot, presenter, resolveSprite, resolveMaskMaterial,
                verifyRuntimeGeometry: false, requireSavedPrefabAsset: true, provisional: false);
        }

        static ProxySpineOwnerDelegationReadback[] ReadSpineOwnerDelegations(ProxyQueueSpec spec,
            IDictionary<string, GameObject> sourceNodes, NativeStaticSortQueueProxyPresenter presenter,
            bool requireRuntimeMeshes, out bool allVerified, out string[] diagnostics)
        {
            var rows = new List<ProxySpineOwnerDelegationReadback>();
            var gaps = new List<string>();
            var specs = (spec.renderers ?? Array.Empty<ProxyRendererSpec>())
                .Where(row => row != null && row.sourceType == "sp.Skeleton")
                .ToDictionary(row => row.sourceComponentId, StringComparer.Ordinal);
            var proofs = presenter == null ? Array.Empty<ProxySpineOwnerDelegation>() :
                presenter.spineOwnerDelegations ?? Array.Empty<ProxySpineOwnerDelegation>();
            var seen = new HashSet<string>(StringComparer.Ordinal);
            foreach (var proof in proofs)
            {
                if (proof == null || String.IsNullOrWhiteSpace(proof.sourceComponentId) || !seen.Add(proof.sourceComponentId))
                {
                    gaps.Add("STATIC_SORT_PROXY_SPINE_DELEGATION_PROOF_MISSING_OR_DUPLICATE");
                    continue;
                }
                specs.TryGetValue(proof.sourceComponentId, out var rendererSpec);
                sourceNodes.TryGetValue(proof.sourceNode, out var node);
                var owner = node == null ? null : node.GetComponent<Graphic>();
                var rootMesh = owner == null || owner.canvasRenderer == null ? null : owner.canvasRenderer.GetMesh();
                var rootVertices = rootMesh == null ? 0 : rootMesh.vertexCount;
                var rootSubmeshes = rootMesh == null ? -1 : rootMesh.subMeshCount;
                var rootMaterials = owner == null || owner.canvasRenderer == null ? -1 : owner.canvasRenderer.materialCount;
                var sourceIdentityVerified = rendererSpec != null && rendererSpec.node == proof.sourceNode &&
                    proof.sourceOwnerGraphic == owner && owner != null &&
                    TryReadSpineIdentity(owner, proof.sourceComponentId, out var actualSourceId);
                UnityEngine.Object actualData = null;
                var hasActualData = owner != null && TryReadSpineDataAsset(owner, out actualData);
                SpineDataIdentityEvidence dataEvidence = null; string dataDiagnostic = null;
                var sourceDataReferenceVerified = hasActualData && actualData != null &&
                    actualData == proof.sourceDataAssetReference &&
                    TryReadSpineDataIdentity(spec, proof.sourceComponentId, actualData, out dataEvidence, out dataDiagnostic) &&
                    dataEvidence.sourceDataAssetId == proof.sourceDataAssetId &&
                    dataEvidence.dataAssetPath == proof.sourceDataAssetPath &&
                    dataEvidence.dataAssetGuid == proof.sourceDataAssetGuid &&
                    dataEvidence.bindingPlanPath == proof.sourceBindingPlanPath &&
                    dataEvidence.bindingPlanSha256 == proof.sourceBindingPlanSha256 &&
                    dataEvidence.sourceManifestSha256 == proof.sourceManifestSha256;
                var registered = new List<CanvasRenderer>();
                var listReadable = owner != null && TryReadSpineRendererList(owner, out registered);
                var sourceGraphics = proof.delegatedSourceGraphics ?? Array.Empty<Graphic>();
                var renderers = proof.delegatedCanvasRenderers ?? Array.Empty<CanvasRenderer>();
                var paths = proof.delegatedChildPaths ?? Array.Empty<string>();
                var materialGuids = proof.delegatedChildMaterialGuids ?? Array.Empty<string>();
                var textureGuids = proof.delegatedChildTextureGuids ?? Array.Empty<string>();
                var vertexCounts = proof.childMeshVertexCounts ?? Array.Empty<int>();
                var submeshCounts = proof.childMeshSubmeshCounts ?? Array.Empty<int>();
                var materialCounts = proof.childCanvasMaterialCounts ?? Array.Empty<int>();
                var count = sourceGraphics.Length;
                var childPaths = new List<string>(); var childTypes = new List<string>();
                var childMaterialGuids = new List<string>(); var childTextureGuids = new List<string>();
                var childRendererListVerified = listReadable && count > 0 &&
                    count == renderers.Length && count == paths.Length && count == materialGuids.Length &&
                    count == textureGuids.Length && count == vertexCounts.Length && count == submeshCounts.Length &&
                    count == materialCounts.Length && registered.Count == count &&
                    registered.SequenceEqual(renderers) && sourceGraphics.Distinct().Count() == count &&
                    renderers.Distinct().Count() == count;
                var childReferencesPersistent = childRendererListVerified;
                for (var index = 0; index < count; index++)
                {
                    var child = sourceGraphics[index];
                    var renderer = child == null ? null : child.canvasRenderer;
                    var mesh = requireRuntimeMeshes && renderer != null ? renderer.GetMesh() : null;
                    var sourceMaterial = child == null ? null : child.material;
                    var sourceTexture = sourceMaterial == null || sourceMaterial.mainTexture == null ?
                        child == null ? null : child.mainTexture : sourceMaterial.mainTexture;
                    long materialLocal; var actualMaterialGuid = sourceMaterial == null ? null : AssetGuid(sourceMaterial, out materialLocal);
                    var actualTextureGuid = TextureAssetGuid(sourceTexture);
                    var childOK = child != null && renderer != null && renderer == renderers.ElementAtOrDefault(index) &&
                        IsSpineCanvasSubmesh(child.gameObject, owner) && paths.ElementAtOrDefault(index) == SpineChildPath(owner.transform, child.transform) &&
                        !String.IsNullOrWhiteSpace(actualMaterialGuid) && actualMaterialGuid == materialGuids.ElementAtOrDefault(index) &&
                        !String.IsNullOrWhiteSpace(AssetDatabase.GetAssetPath(sourceMaterial)) &&
                        !String.IsNullOrWhiteSpace(actualTextureGuid) && actualTextureGuid == textureGuids.ElementAtOrDefault(index);
                    if (requireRuntimeMeshes)
                        childOK = childOK && mesh != null && mesh.vertexCount == vertexCounts.ElementAtOrDefault(index) &&
                            mesh.subMeshCount == submeshCounts.ElementAtOrDefault(index) &&
                            renderer.materialCount == materialCounts.ElementAtOrDefault(index) && mesh.vertexCount > 0 &&
                            mesh.subMeshCount > 0 && renderer.materialCount == mesh.subMeshCount;
                    childRendererListVerified &= childOK;
                    childReferencesPersistent &= childOK;
                    childPaths.Add(child == null ? null : SpineChildPath(owner.transform, child.transform));
                    childTypes.Add(child == null ? null : child.GetType().FullName);
                    childMaterialGuids.Add(actualMaterialGuid); childTextureGuids.Add(actualTextureGuid);
                }
                var childProxyBindings = (presenter == null ? Array.Empty<ProxyGraphicBinding>() : presenter.bindings ?? Array.Empty<ProxyGraphicBinding>())
                    .Where(binding => binding != null && binding.sourceGraphic != null && sourceGraphics.Contains(binding.sourceGraphic)).ToArray();
                var boundChildren = childProxyBindings.Select(binding => binding.sourceGraphic).ToArray();
                var childProxyRefsVerified = boundChildren.Length == count && boundChildren.Distinct().Count() == count &&
                    sourceGraphics.All(child => childProxyBindings.Count(binding => binding.sourceGraphic == child &&
                        (binding.proxyGraphics ?? Array.Empty<NativeStaticSortQueueProxyGraphic>()).Length == 1 &&
                        binding.proxyGraphics[0] != null && binding.proxyGraphics[0].sourceComponentId == proof.sourceComponentId &&
                        binding.proxyGraphics[0].sourceNodeId == proof.sourceNode && binding.proxyGraphics[0].generatedSourceChild &&
                        binding.proxyGraphics[0].sourceOwnerGraphic == owner) == 1);
                var rootMeshDelegated = proof.rootMeshVertexCount == 0 && rootVertices == 0 &&
                    proof.rootMeshWasMissing == (proof.rootMeshSubmeshCount == -1) && proof.rootCanvasMaterialCount >= 0 &&
                    (!requireRuntimeMeshes && rootMesh == null || rootSubmeshes == proof.rootMeshSubmeshCount) &&
                    (!requireRuntimeMeshes || rootMaterials == proof.rootCanvasMaterialCount);
                var verified = sourceIdentityVerified && sourceDataReferenceVerified && rootMeshDelegated &&
                    childRendererListVerified && childReferencesPersistent && childProxyRefsVerified;
                if (!verified)
                    gaps.Add("STATIC_SORT_PROXY_SPINE_OWNER_DELEGATION_READBACK_INVALID: source=" + proof.sourceComponentId +
                        ";rootVertices=" + rootVertices + ";rootSubmeshes=" + rootSubmeshes + ";rootMaterials=" + rootMaterials +
                        ";proofRootVertices=" + proof.rootMeshVertexCount + ";proofRootSubmeshes=" + proof.rootMeshSubmeshCount +
                        ";proofRootMaterials=" + proof.rootCanvasMaterialCount + ";dataGuid=" + proof.sourceDataAssetGuid +
                        ";registeredChildren=" + registered.Count + ";proofChildren=" + count +
                        ";boundChildren=" + boundChildren.Length);
                TryReadSpineIdentity(owner, proof.sourceComponentId, out var actualIdentityId);
                rows.Add(new ProxySpineOwnerDelegationReadback { sourceComponentId = proof.sourceComponentId,
                    sourceNode = proof.sourceNode, sourceGraphicType = owner == null ? null : owner.GetType().FullName,
                    sourceIdentityComponentId = actualIdentityId, sourceDataAssetPath = proof.sourceDataAssetPath,
                    sourceDataAssetId = proof.sourceDataAssetId, sourceBindingPlanPath = proof.sourceBindingPlanPath,
                    sourceBindingPlanSha256 = proof.sourceBindingPlanSha256, sourceManifestSha256 = proof.sourceManifestSha256,
                    sourceDataAssetGuid = proof.sourceDataAssetGuid, rootMeshVertexCount = rootVertices,
                    rootMeshSubmeshCount = rootSubmeshes, rootCanvasMaterialCount = rootMaterials,
                    delegatedChildPaths = childPaths.ToArray(), delegatedChildGraphicTypes = childTypes.ToArray(),
                    delegatedChildTextureGuids = childTextureGuids.ToArray(), delegatedChildMaterialGuids = childMaterialGuids.ToArray(),
                    childMeshVertexCounts = vertexCounts, childMeshSubmeshCounts = submeshCounts,
                    childCanvasMaterialCounts = materialCounts, rootMeshWasMissing = proof.rootMeshWasMissing,
                    sourceIdentityVerified = sourceIdentityVerified, sourceDataReferenceVerified = sourceDataReferenceVerified,
                    rootMeshDelegated = rootMeshDelegated, childRendererListVerified = childRendererListVerified,
                    childReferencesPersistent = childReferencesPersistent, verified = verified });
            }
            allVerified = gaps.Count == 0;
            diagnostics = gaps.ToArray();
            return rows.ToArray();
        }

        static ProxySpineNonDrawChildReadback[] ReadSpineNonDrawChildren(ProxyQueueSpec spec,
            IDictionary<string, GameObject> sourceNodes, NativeStaticSortQueueProxyPresenter presenter,
            out bool allVerified, out string[] diagnostics)
        {
            var rows = new List<ProxySpineNonDrawChildReadback>();
            var gaps = new List<string>();
            var expectedOwners = (spec.nonDrawRenderers ?? Array.Empty<ProxyRendererSpec>())
                .Where(row => row != null && row.sourceType == "sp.Skeleton").ToDictionary(row => row.sourceComponentId, StringComparer.Ordinal);
            var proofs = presenter == null ? Array.Empty<ProxySpineNonDrawChild>() :
                presenter.spineNonDrawChildren ?? Array.Empty<ProxySpineNonDrawChild>();
            var proofOwners = proofs.Where(proof => proof != null).Select(proof => proof.sourceComponentId)
                .Distinct(StringComparer.Ordinal).ToArray();
            if (!new HashSet<string>(proofOwners, StringComparer.Ordinal).SetEquals(expectedOwners.Keys))
                gaps.Add("STATIC_SORT_PROXY_SPINE_NONDRAW_OWNER_DENOMINATOR_DIFFERS: expected=" + expectedOwners.Count +
                    ";observed=" + proofOwners.Length);

            var globalChildRefs = new HashSet<Graphic>();
            foreach (var pair in expectedOwners)
            {
                var sourceId = pair.Key; var expected = pair.Value;
                sourceNodes.TryGetValue(expected.node, out var node);
                var owner = node == null ? null : node.GetComponent<Graphic>();
                if (owner == null || owner.GetType().FullName != "Spine.Unity.SkeletonGraphic")
                {
                    gaps.Add("STATIC_SORT_PROXY_SPINE_NONDRAW_OWNER_MISSING: " + sourceId + ";node=" + expected.node);
                    continue;
                }
                UnityEngine.Object dataAsset = null;
                var hasDataAsset = TryReadSpineDataAsset(owner, out dataAsset);
                SpineDataIdentityEvidence dataEvidence = null; string dataDiagnostic = null;
                var dataOK = hasDataAsset && TryReadSpineDataIdentity(spec, sourceId, dataAsset, out dataEvidence, out dataDiagnostic);
                var sourceIdentityOK = TryReadSpineIdentity(owner, sourceId, out var actualSourceIdentity);
                var registered = new List<CanvasRenderer>();
                var listReadable = TryReadSpineRendererList(owner, out registered);
                var ownerProofs = proofs.Where(proof => proof != null && proof.sourceComponentId == sourceId).ToArray();
                var ownerGraphicOK = owner.enabled == expected.sourceEnabled && node.activeInHierarchy == expected.sourceActive &&
                    ownerProofs.Length > 0;
                if (!dataOK || !sourceIdentityOK || !listReadable || registered.Count != ownerProofs.Length ||
                    registered.Count == 0 || !registered.SequenceEqual(ownerProofs.Select(proof => proof.sourceChildCanvasRenderer)))
                    gaps.Add("STATIC_SORT_PROXY_SPINE_NONDRAW_OWNER_TYPED_IDENTITY_OR_RENDERER_LIST_DIFFERS: source=" + sourceId +
                        ";node=" + expected.node + ";children=" + registered.Count + ";proofs=" + ownerProofs.Length +
                        ";dataGuid=" + (dataEvidence == null ? "<unresolved>" : dataEvidence.dataAssetGuid) +
                        ";dataBinding=" + (dataDiagnostic ?? "none"));

                for (var index = 0; index < ownerProofs.Length; index++)
                {
                    var proof = ownerProofs[index];
                    var child = proof.sourceChildGraphic;
                    var renderer = child == null ? null : child.canvasRenderer;
                    var mesh = renderer == null ? null : renderer.GetMesh();
                    var material = child == null ? null : child.material;
                    var texture = material == null || material.mainTexture == null ?
                        child == null ? null : child.mainTexture : material.mainTexture;
                    long materialLocal; var materialGuid = material == null ? null : AssetGuid(material, out materialLocal);
                    var textureGuid = TextureAssetGuid(texture);
                    var registeredOK = index < registered.Count && renderer != null && renderer == registered[index] &&
                        proof.sourceChildCanvasRenderer == renderer && IsSpineCanvasSubmesh(child.gameObject, owner) &&
                        proof.childPath == SpineChildPath(node.transform, child.transform) && globalChildRefs.Add(child);
                    var childRefOK = registeredOK && materialGuid == proof.childMaterialGuid &&
                        textureGuid == proof.childTextureGuid && !String.IsNullOrWhiteSpace(AssetDatabase.GetAssetPath(material)) &&
                        proof.sourceOwnerGraphic == owner && proof.sourceDataAssetReference == dataAsset &&
                        proof.sourceDataAssetId == (dataEvidence == null ? null : dataEvidence.sourceDataAssetId) &&
                        proof.sourceDataAssetPath == (dataEvidence == null ? null : dataEvidence.dataAssetPath) &&
                        proof.sourceDataAssetGuid == (dataEvidence == null ? null : dataEvidence.dataAssetGuid);
                    var sourceChildStateOK = proof.sourceOwnerEnabled == expected.sourceEnabled &&
                        proof.sourceNodeActive == expected.sourceActive && proof.sourceChildEnabled == child.enabled &&
                        proof.sourceChildActiveSelf == child.gameObject.activeSelf &&
                        proof.sourceChildActiveInHierarchy == child.gameObject.activeInHierarchy &&
                        proof.targetChildEnabled == child.enabled && proof.targetChildActiveInHierarchy == child.gameObject.activeInHierarchy;
                    var childNoDraw = expected.sourceActive
                        ? (!child.gameObject.activeInHierarchy || !child.enabled)
                        : !child.gameObject.activeInHierarchy;
                    var verified = ownerGraphicOK && dataOK && sourceIdentityOK && registeredOK && childRefOK &&
                        sourceChildStateOK && childNoDraw;
                    if (!verified)
                        gaps.Add("STATIC_SORT_PROXY_SPINE_NONDRAW_CHILD_READBACK_INVALID: source=" + sourceId +
                            ";child=" + (child == null ? "<null>" : SpineChildPath(node.transform, child.transform)) +
                            ";type=" + (child == null ? "<null>" : child.GetType().FullName) +
                            ";sourceEnabled=" + expected.sourceEnabled + ";sourceActive=" + expected.sourceActive +
                            ";childEnabled=" + (child != null && child.enabled) +
                            ";childActiveSelf=" + (child != null && child.gameObject.activeSelf) +
                            ";childActiveInHierarchy=" + (child != null && child.gameObject.activeInHierarchy) +
                            ";meshVertices=" + (mesh == null ? -1 : mesh.vertexCount) +
                            ";meshSubmeshes=" + (mesh == null ? -1 : mesh.subMeshCount) +
                            ";materialCount=" + (renderer == null ? -1 : renderer.materialCount) +
                            ";dataGuid=" + (dataEvidence == null ? proof.sourceDataAssetGuid : dataEvidence.dataAssetGuid));
                    rows.Add(new ProxySpineNonDrawChildReadback { sourceComponentId = sourceId,
                        sourceNode = expected.node, noDrawReason = expected.sourceActive ? "disabled-source" : "inactive-source",
                        sourceIdentityComponentId = actualSourceIdentity, sourceDataAssetId = proof.sourceDataAssetId,
                        sourceDataAssetPath = proof.sourceDataAssetPath, sourceDataAssetGuid = proof.sourceDataAssetGuid,
                        childPath = child == null ? null : SpineChildPath(node.transform, child.transform),
                        childGraphicType = child == null ? null : child.GetType().FullName,
                        childMaterialGuid = materialGuid, childTextureGuid = textureGuid,
                        sourceOwnerEnabled = proof.sourceOwnerEnabled, sourceNodeActive = proof.sourceNodeActive,
                        sourceChildEnabled = proof.sourceChildEnabled, sourceChildActiveSelf = proof.sourceChildActiveSelf,
                        sourceChildActiveInHierarchy = proof.sourceChildActiveInHierarchy,
                        targetChildEnabled = child != null && child.enabled,
                        targetChildActiveInHierarchy = child != null && child.gameObject.activeInHierarchy,
                        sourceIdentityVerified = sourceIdentityOK, sourceDataReferenceVerified = dataOK,
                        registeredChildVerified = registeredOK, childReferencePersistent = childRefOK,
                        childNoDrawVerified = childNoDraw, sourceChildMeshVertexCount = mesh == null ? -1 : mesh.vertexCount,
                        sourceChildMeshSubmeshCount = mesh == null ? -1 : mesh.subMeshCount,
                        sourceChildMaterialCount = renderer == null ? -1 : renderer.materialCount,
                        verified = verified });
                }
            }
            allVerified = gaps.Count == 0;
            diagnostics = gaps.ToArray();
            return rows.ToArray();
        }

        static ProxyQueueReadback ReadProxy(ProxyQueueSpec spec,
            IDictionary<string, GameObject> sourceNodes, GameObject proxyRoot, NativeStaticSortQueueProxyPresenter presenter,
            Func<string, Sprite> resolveSprite, Func<MaskSpec, Material> resolveMaskMaterial,
            bool verifyRuntimeGeometry, bool requireSavedPrefabAsset, bool provisional)
        {
            var expected = (spec.drawEvents ?? Array.Empty<ProxyDrawEventSpec>()).Select(row => row.kind + ":" + row.node + ":" + row.sourceComponentId).ToArray();
            var observed = new List<string>(); var graphics = new List<ProxyPresenterReadback>();
            var emptyGraphics = new List<ProxyEmptyRendererReadback>();
            var proxyMasks = new Dictionary<string, GameObject>();
            var structuralDiagnostics = new List<string>();
            var textSourceReadbacks = new List<ProxyTextSourceReadback>();
            var textSourceBindings = new Dictionary<NativeStaticSortTextSource, TextSlotBinding>();
            var textSourceVerified = new Dictionary<NativeStaticSortTextSource, bool>();
            foreach (var identity in proxyRoot == null ? Array.Empty<NativeStaticSortTextSource>() :
                proxyRoot.GetComponentsInChildren<NativeStaticSortTextSource>(true))
            {
                if (identity == null) continue;
                var proxyGraphic = identity.GetComponent<NativeStaticSortQueueProxyGraphic>();
                var textMesh = proxyGraphic == null ? null : proxyGraphic.proxyMesh;
                var sourceTextSpec = (spec.renderers ?? Array.Empty<ProxyRendererSpec>())
                    .SingleOrDefault(row => row != null && row.sourceComponentId == identity.sourceComponentId);
                var expectedTextOwner = sourceTextSpec != null && sourceNodes.TryGetValue(sourceTextSpec.node, out var sourceTextNode) &&
                    sourceTextNode != null ? sourceTextNode.GetComponent<TMPro.TMP_Text>() : null;
                TextSourceReadback textReadback;
                bool textVerified;
                if (expectedTextOwner == null || identity.sourceOwner != expectedTextOwner)
                {
                    textReadback = new TextSourceReadback { sourceComponentId = identity.sourceComponentId,
                        materialSlot = identity.materialSlot, diagnostic = "TMP_SORT_EXPECTED_SOURCE_NODE_OWNER_MISSING_OR_DIFFERS" };
                    textVerified = false;
                }
                else if (verifyRuntimeGeometry)
                {
                    textVerified = UnityStaticSortTextSource.ReadInitialized(identity, textMesh, expectedTextOwner,
                        identity.sourceComponentId, out textReadback);
                }
                else if (AssetDatabase.TryGetGUIDAndLocalFileIdentifier(expectedTextOwner, out var expectedOwnerGuid, out long expectedOwnerLocalId) &&
                    !String.IsNullOrWhiteSpace(expectedOwnerGuid) && expectedOwnerLocalId != 0)
                {
                    textVerified = UnityStaticSortTextSource.ReadPersistent(identity, textMesh, expectedTextOwner,
                        identity.sourceComponentId, expectedOwnerGuid, expectedOwnerLocalId, out textReadback);
                }
                else
                {
                    textReadback = new TextSourceReadback { sourceComponentId = identity.sourceComponentId,
                        materialSlot = identity.materialSlot, diagnostic = "TMP_SORT_PERSISTENT_MAP_OWNER_ASSET_GUID_OR_LOCAL_ID_MISSING" };
                    textVerified = false;
                }
                textSourceReadbacks.Add(new ProxyTextSourceReadback { sourceNode = sourceTextSpec == null ? null : sourceTextSpec.node,
                    readbackMode = verifyRuntimeGeometry ? "loaded" : "persistent",
                    sourceComponentId = textReadback.sourceComponentId, materialSlot = textReadback.materialSlot,
                    evidence = textReadback });
                textSourceVerified[identity] = textVerified;
                if (textVerified && verifyRuntimeGeometry)
                {
                    if (UnityStaticSortTextSource.ResolveGeneratedSlot(identity, expectedTextOwner,
                            identity.sourceComponentId, out var textBinding, out var resolveDiagnostic))
                        textSourceBindings[identity] = textBinding;
                    else
                    {
                        textReadback.verified = false;
                        textReadback.diagnostic = resolveDiagnostic;
                        textVerified = false;
                        textSourceVerified[identity] = false;
                    }
                }
                if (!textVerified)
                    structuralDiagnostics.Add("STATIC_SORT_PROXY_TEXT_SOURCE_READBACK_INVALID: source=" + identity.sourceComponentId +
                        ";slot=" + identity.materialSlot + ";mode=" + (verifyRuntimeGeometry ? "initialized" : "persistent") +
                        ";diagnostic=" + textReadback.diagnostic);
            }
            if (verifyRuntimeGeometry && presenter != null)
            {
                Canvas.ForceUpdateCanvases();
                presenter.RefreshSourceSuppression();
            }
            var textSourcesVerified = textSourceReadbacks.All(readback => readback != null && readback.evidence != null &&
                readback.evidence.verified);
            bool Visit(Transform node)
            {
                var marker = node.GetComponent<NativeStaticSortQueueProxyMarker>();
                if (marker != null && (marker.kind == "emptyRenderer" || marker.kind == "retainedNonDraw"))
                {
                    var rendererSpec = (spec.renderers ?? Array.Empty<ProxyRendererSpec>())
                        .Concat(spec.nonDrawRenderers ?? Array.Empty<ProxyRendererSpec>())
                        .SingleOrDefault(row => row != null && row.sourceComponentId == marker.sourceComponentId);
                    var nodeOK = rendererSpec != null;
                    if (rendererSpec == null)
                        structuralDiagnostics.Add("STATIC_SORT_PROXY_EMPTY_RENDERER_SPEC_MISSING: source=" +
                            marker.sourceComponentId + ";node=" + marker.sourceNode + ";kind=" + marker.kind);
                    else
                    {
                        var empty = ReadEmptyRenderer(rendererSpec, sourceNodes, marker);
                        if (empty != null) emptyGraphics.Add(empty);
                        nodeOK = empty != null && empty.verified;
                        if (!nodeOK)
                            structuralDiagnostics.Add("STATIC_SORT_PROXY_EMPTY_RENDERER_READBACK_INVALID: source=" +
                                marker.sourceComponentId + ";node=" + marker.sourceNode + ";kind=" + marker.kind +
                                ";reason=" + (empty == null ? "readback-null" : empty.noDrawReason) +
                                ";sourceMeshVertices=" + (empty == null ? -1 : empty.sourceMeshVertexCount) +
                                ";sourceMaterials=" + (empty == null ? -1 : empty.sourceCanvasMaterialCount) +
                                ";sourceEnabled=" + (empty != null && empty.sourceEnabled) +
                                ";sourceActive=" + (empty != null && empty.sourceActive) +
                                ";fields=" + (empty != null && empty.typedFieldsVerified) +
                                ";sourceRef=" + (empty != null && empty.sourceReferenceVerified));
                        if (marker.kind == "emptyRenderer")
                        {
                            var eventKey = "renderer:" + marker.sourceNode + ":" + marker.sourceComponentId;
                            if (observed.Count == 0 || observed[observed.Count - 1] != eventKey) observed.Add(eventKey);
                        }
                    }
                    var childrenOK = true;
                    foreach (Transform child in node) if (!Visit(child)) childrenOK = false;
                    return nodeOK && childrenOK;
                }
                if (marker != null && marker.kind == "mask")
                {
                    var nodeOK = proxyMasks.TryAdd(marker.sourceNode, node.gameObject);
                    if (!nodeOK) structuralDiagnostics.Add("STATIC_SORT_PROXY_DUPLICATE_MASK_PROXY: node=" + marker.sourceNode +
                        ";path=" + TransformPath(node));
                    observed.Add("maskEnter:" + marker.sourceNode + ":");
                    var childrenOK = true;
                    foreach (Transform child in node) if (!Visit(child)) childrenOK = false;
                    observed.Add("maskExit:" + marker.sourceNode + ":");
                    return nodeOK && childrenOK;
                }
                var proxy = node.GetComponent<NativeStaticSortQueueProxyGraphic>();
                if (proxy != null)
                {
                    var eventKey = "renderer:" + proxy.sourceNodeId + ":" + proxy.sourceComponentId;
                    // One source renderer can produce several real native
                    // CanvasRenderer materials/submeshes. Keep each proxy
                    // leaf inspectable while comparing the source event once.
                    if (observed.Count == 0 || observed[observed.Count - 1] != eventKey) observed.Add(eventKey);
                    var textIdentity = proxy.GetComponent<NativeStaticSortTextSource>();
                    var textBinding = textIdentity != null && textSourceBindings.TryGetValue(textIdentity, out var resolvedTextBinding) ?
                        resolvedTextBinding : null;
                    var source = textIdentity == null ? proxy.sourceGraphic :
                        textBinding != null ? textBinding.sourceGraphic : textIdentity.sourceOwner as Graphic;
                    var sourceMesh = textIdentity != null ? textBinding == null ? null : textBinding.sourceMesh :
                        !verifyRuntimeGeometry || source == null || source.canvasRenderer == null ? null : source.canvasRenderer.GetMesh();
                    var currentHash = textIdentity != null ? textBinding == null ? textIdentity.sourceMeshSha256 : textBinding.sourceMeshSha256 :
                        sourceMesh == null ? null : MeshFingerprint(sourceMesh, proxy.submeshIndex);
                    var proxyHash = proxy.proxyMesh == null ? null : MeshFingerprint(proxy.proxyMesh, 0);
                    var renderedMesh = !verifyRuntimeGeometry ? null : proxy.GetComponent<CanvasRenderer>()?.GetMesh();
                    var renderedHash = renderedMesh == null ? null : MeshFingerprint(renderedMesh, 0);
                    var sourceUvCounts = sourceMesh == null ? proxy.sourceUvChannelVertexCounts : UvChannelVertexCounts(sourceMesh);
                    var sourceUvDimensions = sourceMesh == null ? proxy.sourceUvChannelDimensions : UvChannelDimensions(sourceMesh);
                    var proxyUvCounts = UvChannelVertexCounts(proxy.proxyMesh);
                    var proxyUvDimensions = UvChannelDimensions(proxy.proxyMesh);
                    var renderedUvCounts = renderedMesh == null ? Array.Empty<int>() : UvChannelVertexCounts(renderedMesh);
                    var renderedUvDimensions = renderedMesh == null ? Array.Empty<int>() : UvChannelDimensions(renderedMesh);
                    var sourceProxyUvVerified = sourceUvCounts != null && sourceUvDimensions != null &&
                        sourceUvCounts.SequenceEqual(proxyUvCounts) && sourceUvDimensions.SequenceEqual(proxyUvDimensions);
                    var renderedProxyUvVerified = !verifyRuntimeGeometry || renderedMesh != null &&
                        renderedUvCounts.SequenceEqual(proxyUvCounts) && renderedUvDimensions.SequenceEqual(proxyUvDimensions);
                    var currentSourceMaterial = textIdentity != null ?
                        (textBinding == null ? textIdentity.sourceMaterial : textBinding.sourceMaterial) :
                        source == null ? null : (source.material ?? Canvas.GetDefaultCanvasMaterial());
                    var currentSourceTexture = textIdentity != null ?
                        (textBinding == null ? textIdentity.sourceTexture : textBinding.sourceTexture) :
                        currentSourceMaterial != null && currentSourceMaterial.mainTexture != null ?
                            currentSourceMaterial.mainTexture : source == null ? null : source.mainTexture;
                    var sourceGraphicNode = source == null ? null : source.transform as RectTransform;
                    var proxyRt = node as RectTransform;
                    var transformed = verifyRuntimeGeometry && sourceGraphicNode != null && proxyRt != null &&
                        WorldRectMatches(sourceGraphicNode, proxyRt) &&
                        TransformedMeshMatches(sourceMesh, proxy.submeshIndex, source.transform, proxyRt, proxy.proxyMesh);
                    var transformDiagnostics = verifyRuntimeGeometry ? MeasureTransformedMesh(sourceMesh, proxy.submeshIndex,
                        source == null ? null : source.transform, proxyRt, proxy.proxyMesh) : new TransformedMeshDiagnostics();
                    var sourceReferenceValid = source != null && sourceNodes.TryGetValue(proxy.sourceNodeId, out var sourceNode) &&
                        (textIdentity != null ?
                            textIdentity.sourceComponentId == proxy.sourceComponentId &&
                            textIdentity.sourceOwner != null &&
                            textIdentity.sourceOwner == sourceNode.GetComponent<TMPro.TMP_Text>() &&
                            proxy.sourceOwnerGraphic == (Graphic)textIdentity.sourceOwner &&
                            textIdentity.sourceOwner.GetType().FullName == proxy.expectedSourceGraphicType &&
                            proxy.sourceGraphic == (Graphic)textIdentity.sourceOwner &&
                            textIdentity.generatedSubmesh == proxy.generatedSourceChild &&
                            textSourceVerified.TryGetValue(textIdentity, out var textProofVerified) && textProofVerified &&
                            (!verifyRuntimeGeometry || textBinding != null && textBinding.sourceGraphic == source &&
                                (source.GetType().FullName == "TMPro.TMP_SubMeshUI") == proxy.generatedSourceChild) :
                            (source.transform == sourceNode.transform || source.transform.IsChildOf(sourceNode.transform)) &&
                            (proxy.generatedSourceChild ? (proxy.sourceType == "cc.Label" || proxy.sourceType == "cc.RichText" ? IsGeneratedTextSubmesh(source.gameObject) :
                                proxy.sourceType == "sp.Skeleton" && source != null && IsSpineCanvasSubmesh(source.gameObject, proxy.sourceOwnerGraphic)) :
                                source.GetType().FullName == proxy.expectedSourceGraphicType));
                    var canvasCull = source != null && source.canvasRenderer.cull;
                    long meshLocal; var meshGuid = proxy.proxyMesh == null ? null : AssetGuid(proxy.proxyMesh, out meshLocal);
                    long materialLocal; var actualMaterialGuid = proxy.proxyBaseMaterial == null ? null : AssetGuid(proxy.proxyBaseMaterial, out materialLocal);
                    var actualTextureGuid = TextureAssetGuid(proxy.proxyTexture);
                    var proxyMeshPersistent = proxy.proxyMesh != null && !string.IsNullOrEmpty(AssetDatabase.GetAssetPath(proxy.proxyMesh)) &&
                        AssetDatabase.GetAssetPath(proxy.proxyMesh).StartsWith("Assets/", StringComparison.Ordinal) &&
                        AssetGuid(proxy.proxyMesh, out meshLocal) == proxy.meshAssetGuid;
                    var proxyResourcesPersistent = proxy.proxyBaseMaterial != null &&
                        AssetDatabase.GetAssetPath(proxy.proxyBaseMaterial).StartsWith("Assets/", StringComparison.Ordinal) &&
                        actualMaterialGuid == proxy.sourceMaterialGuid && actualTextureGuid == proxy.sourceTextureGuid;
                    var renderer = proxy.GetComponent<CanvasRenderer>();
                    var sourceGraphicEnabled = textIdentity != null ?
                        (textBinding == null ? textIdentity.sourceGraphicEnabled : textBinding.sourceGraphicEnabled) :
                        source != null && source.enabled;
                    var sourceRendererAlpha = textIdentity != null && !verifyRuntimeGeometry ? proxy.sourceRendererAlpha :
                        source == null || source.canvasRenderer == null ? 0f : source.canvasRenderer.GetAlpha();
                    var sourceInheritedAlpha = textIdentity != null && !verifyRuntimeGeometry ? proxy.sourceInheritedAlpha :
                        source == null || source.canvasRenderer == null ? 0f : source.canvasRenderer.GetInheritedAlpha();
                    var proxyRendererAlpha = renderer == null ? 0f : renderer.GetAlpha();
                    var proxyInheritedAlpha = renderer == null ? 0f : renderer.GetInheritedAlpha();
                    var opacityCarrier = proxy.GetComponent<CanvasGroup>();
                    var sourceEffectiveAlpha = sourceRendererAlpha * sourceInheritedAlpha;
                    var proxyEffectiveAlpha = proxyRendererAlpha * proxyInheritedAlpha;
                    var opacityVerified = source != null && proxy.sourceOpacityCaptured && opacityCarrier != null &&
                        opacityCarrier.ignoreParentGroups && Mathf.Abs(opacityCarrier.alpha - sourceInheritedAlpha) <= 1e-4f &&
                        Mathf.Abs(proxy.sourceRendererAlpha - sourceRendererAlpha) <= 1e-4f &&
                        Mathf.Abs(proxy.sourceInheritedAlpha - sourceInheritedAlpha) <= 1e-4f &&
                        Mathf.Abs(proxyRendererAlpha - sourceRendererAlpha) <= 1e-4f &&
                        Mathf.Abs(proxyInheritedAlpha - sourceInheritedAlpha) <= 1e-4f &&
                        Mathf.Abs(proxyEffectiveAlpha - sourceEffectiveAlpha) <= 1e-4f;
                    var currentMaterialFingerprint = source == null ? null : MaterialFingerprint(currentSourceMaterial);
                    var proxyMaterialFingerprint = MaterialFingerprint(proxy.proxyBaseMaterial);
                    var sourceMaterialMatches = source != null && currentMaterialFingerprint == proxy.sourceMaterialFingerprint &&
                        proxyMaterialFingerprint == proxy.sourceMaterialFingerprint && proxy.proxyTexture == currentSourceTexture &&
                        (textIdentity == null || textSourceVerified.TryGetValue(textIdentity, out var verifiedTextMaterial) && verifiedTextMaterial);
                    var staticSnapshotVerified = sourceReferenceValid && source != null && sourceGraphicEnabled && sourceProxyUvVerified && opacityVerified &&
                        proxyMeshPersistent && proxy.meshContentSha256 == proxyHash && meshGuid == proxy.meshAssetGuid &&
                        proxyResourcesPersistent && sourceMaterialMatches;
                    var runtimeMeshVerified = staticSnapshotVerified && renderedProxyUvVerified && canvasCull && renderer != null && !renderer.cull &&
                        proxy.sourceMeshSha256 == currentHash && renderedHash == proxyHash && transformed;
                    graphics.Add(new ProxyPresenterReadback { sourceComponentId = proxy.sourceComponentId,
                        sourceNode = proxy.sourceNodeId, nativeGraphicType = source == null ? null : source.GetType().FullName,
                        sourceMeshSha256 = currentHash, capturedSourceMeshSha256 = proxy.sourceMeshSha256,
                        meshContentSha256 = proxy.meshContentSha256, proxyMeshSha256 = proxyHash, renderedMeshSha256 = renderedHash,
                        meshAssetGuid = meshGuid, materialGuid = actualMaterialGuid,
                        textureGuid = actualTextureGuid, submeshIndex = proxy.submeshIndex,
                        sourceVertexCount = sourceMesh == null ? -1 : sourceMesh.vertexCount,
                        persistedProxyVertexCount = proxy.proxyMesh == null ? -1 : proxy.proxyMesh.vertexCount,
                        sourceUvChannelVertexCounts = sourceUvCounts,
                        proxyUvChannelVertexCounts = proxyUvCounts,
                        renderedUvChannelVertexCounts = renderedUvCounts,
                        sourceUvChannelDimensions = sourceUvDimensions,
                        proxyUvChannelDimensions = proxyUvDimensions,
                        renderedUvChannelDimensions = renderedUvDimensions,
                        sourceRendererAlpha = sourceRendererAlpha, proxyRendererAlpha = proxyRendererAlpha,
                        sourceInheritedAlpha = sourceInheritedAlpha, proxyInheritedAlpha = proxyInheritedAlpha,
                        sourceEffectiveAlpha = sourceEffectiveAlpha, proxyEffectiveAlpha = proxyEffectiveAlpha,
                        vertexCount = proxy.proxyMesh == null ? 0 : proxy.proxyMesh.vertexCount,
                        sourceQueueIndex = proxy.queueIndex, textMaterialSlot = textIdentity == null ? -1 : textIdentity.materialSlot,
                        sourceGraphicEnabled = sourceGraphicEnabled,
                        sourceCulled = canvasCull, proxyVisible = renderer != null && !renderer.cull,
                        generatedSourceChild = proxy.generatedSourceChild,
                        staticSnapshotVerified = staticSnapshotVerified, runtimeMeshVerified = runtimeMeshVerified,
                        transformedGeometryVerified = transformed, opacityVerified = opacityVerified,
                        maxWorldVertexError = transformDiagnostics.maxWorldVertexError,
                        maxWorldNormalError = transformDiagnostics.maxWorldNormalError,
                        maxWorldTangentError = transformDiagnostics.maxWorldTangentError,
                        transformedTopologyMatches = transformDiagnostics.topologyMatches,
                        transformedUvMatches = transformDiagnostics.uvMatches,
                        transformedColorsMatch = transformDiagnostics.colorsMatch,
                        transformedNormalsMatch = transformDiagnostics.normalsMatch,
                        transformedTangentsMatch = transformDiagnostics.tangentsMatch,
                        verified = verifyRuntimeGeometry ? runtimeMeshVerified : staticSnapshotVerified });
                    var graphicReadback = graphics[graphics.Count - 1];
                    if (!graphicReadback.verified)
                        structuralDiagnostics.Add("STATIC_SORT_PROXY_GRAPHIC_READBACK_INVALID: source=" + proxy.sourceComponentId +
                            ";node=" + proxy.sourceNodeId + ";type=" + graphicReadback.nativeGraphicType +
                            ";sourceMesh=" + graphicReadback.sourceMeshSha256 + ";proxyMesh=" + graphicReadback.proxyMeshSha256 +
                            ";renderedMesh=" + graphicReadback.renderedMeshSha256 +
                            ";worldVertexError=" + graphicReadback.maxWorldVertexError.ToString("R", CultureInfo.InvariantCulture) +
                            ";topology=" + graphicReadback.transformedTopologyMatches + ";uv=" + graphicReadback.transformedUvMatches +
                            ";colors=" + graphicReadback.transformedColorsMatch + ";normals=" + graphicReadback.transformedNormalsMatch +
                            ";tangents=" + graphicReadback.transformedTangentsMatch +
                            ";transformed=" + graphicReadback.transformedGeometryVerified +
                            ";static=" + graphicReadback.staticSnapshotVerified + ";runtime=" + graphicReadback.runtimeMeshVerified);
                }
                var descendantsOK = true;
                foreach (Transform child in node) if (!Visit(child)) descendantsOK = false;
                return descendantsOK;
            }
            var rootMarker = proxyRoot == null ? null : proxyRoot.GetComponent<NativeStaticSortQueueProxyMarker>();
            var root = proxyRoot == null ? null : proxyRoot.transform;
            var traversalOk = root != null;
            if (traversalOk) foreach (Transform child in root) if (!Visit(child)) traversalOk = false;
            var observedArray = observed.ToArray();
            var textSourceSlots = textSourceReadbacks.Where(readback => readback != null)
                .Select(readback => readback.sourceComponentId + "\n" + readback.materialSlot).ToArray();
            var actualEmptyDrawIds = new HashSet<string>(emptyGraphics.Where(row => row != null && row.actualQueueIndex >= 0)
                .Select(row => row.sourceComponentId), StringComparer.Ordinal);
            var expectedTextIds = new HashSet<string>((spec.renderers ?? Array.Empty<ProxyRendererSpec>())
                .Where(row => row != null && (row.sourceType == "cc.Label" || row.sourceType == "cc.RichText") &&
                    !actualEmptyDrawIds.Contains(row.sourceComponentId) &&
                    (spec.drawEvents ?? Array.Empty<ProxyDrawEventSpec>()).Any(draw => draw != null && draw.kind == "renderer" &&
                        draw.sourceComponentId == row.sourceComponentId))
                .Select(row => row.sourceComponentId), StringComparer.Ordinal);
            var actualTextIds = new HashSet<string>(textSourceReadbacks.Where(row => row != null)
                .Select(row => row.sourceComponentId), StringComparer.Ordinal);
            textSourcesVerified &= textSourceSlots.Length == textSourceSlots.Distinct(StringComparer.Ordinal).Count() &&
                expectedTextIds.SetEquals(actualTextIds);
            if (!textSourcesVerified)
                structuralDiagnostics.Add("STATIC_SORT_PROXY_TEXT_SOURCE_DENOMINATOR_OR_IDENTITY_INVALID: expected=" +
                    String.Join(",", expectedTextIds.OrderBy(value => value, StringComparer.Ordinal)) + ";actual=" +
                    String.Join(",", actualTextIds.OrderBy(value => value, StringComparer.Ordinal)));
            var sourceTreePreserved = SourceTreeMatchesProxy(spec, sourceNodes);
            var sourceActivePreserved = (spec.sourceNodeActive ?? Array.Empty<ProxySourceActiveSpec>()).Length > 0 &&
                (spec.sourceNodeActive ?? Array.Empty<ProxySourceActiveSpec>()).All(row =>
                    row != null && sourceNodes.TryGetValue(row.node, out var go) && go != null && go.activeSelf == row.active);
            var sourceRoot = sourceNodes.TryGetValue(spec.rootScope, out var sourceRootGo) ? sourceRootGo : null;
            var expectedQueueSha = HashText(string.Join("|", (spec.drawEvents ?? Array.Empty<ProxyDrawEventSpec>())
                .Select(row => row.kind + ":" + row.node + ":" + row.sourceComponentId)));
            var presenterRefsOK = presenter != null && presenter.sourceRootId == spec.rootScope &&
                presenter.sourcePrefabId == spec.sourcePrefabId && presenter.prefabPath == spec.prefabPath &&
                presenter.sourceRoot == sourceRoot && presenter.proxyRoot == proxyRoot &&
                presenter.queueSha256 == expectedQueueSha && presenter.sourceTreeStayedUnmodified &&
                (presenter.sourceGraphics ?? Array.Empty<Graphic>()).All(graphic => graphic != null && graphic.canvasRenderer != null && graphic.canvasRenderer.cull);
            var nestedProxyRootsDisabled = presenter != null &&
                presenter.nestedProxyRoots.Length == presenter.nestedProxyRootActiveBefore.Length &&
                presenter.nestedProxyRoots.Length == presenter.nestedProxyPresenters.Length &&
                presenter.nestedProxyRoots.Select((nestedRoot, index) => nestedRoot != null &&
                    IsGeneratedSortProxyRoot(nestedRoot.transform) && !nestedRoot.activeSelf &&
                    nestedRoot.GetComponent<NativeStaticSortQueueProxyPresenter>() == presenter.nestedProxyPresenters[index]).All(value => value);
            var sourceMaskRefsOK = true;
            foreach (var mask in spec.masks ?? Array.Empty<ProxyMaskSpec>())
            {
                var matches = (presenter == null ? Array.Empty<ProxyMaskBinding>() : presenter.maskBindings ?? Array.Empty<ProxyMaskBinding>())
                    .Where(item => item != null && item.sourceId == mask.sourceId).ToArray();
                var binding = matches.Length == 1 ? matches[0] : null;
                var sourceNode = sourceNodes.TryGetValue(mask.node, out var sourceMaskNode) ? sourceMaskNode : null;
                var proxyNode = proxyMasks.TryGetValue(mask.node, out var proxyMaskNode) ? proxyMaskNode : null;
                var expectedSourceMask = sourceNode == null ? null : (Component)sourceNode.GetComponent<Mask>() ?? sourceNode.GetComponent<RectMask2D>();
                var sourceReferenceOK = binding != null && sourceNode != null && proxyNode != null &&
                    binding.sourceNode == mask.node && binding.sourceMask == expectedSourceMask &&
                    binding.proxyMask == proxyNode.GetComponent<Mask>();
                if (!sourceReferenceOK)
                {
                    sourceMaskRefsOK = false;
                    structuralDiagnostics.Add("STATIC_SORT_PROXY_MASK_SOURCE_REFERENCE_INVALID: source=" + mask.sourceId +
                        ";node=" + mask.node + ";bindings=" + matches.Length + ";sourceNode=" + (sourceNode != null) +
                        ";sourceComponent=" + (expectedSourceMask == null ? "missing" : expectedSourceMask.GetType().FullName) +
                        ";proxyNode=" + (proxyNode != null) + ";proxyMask=" + (proxyNode == null ? "missing" :
                            (proxyNode.GetComponent<Mask>() == null ? "missing" : proxyNode.GetComponent<Mask>().GetType().FullName)));
                }
            }
            var prefabPathOK = !requireSavedPrefabAsset || (sourceRoot != null && !string.IsNullOrEmpty(spec.prefabPath) &&
                AssetDatabase.LoadAssetAtPath<GameObject>(spec.prefabPath) != null &&
                PrefabUtility.GetPrefabAssetPathOfNearestInstanceRoot(sourceRoot) == spec.prefabPath);
            var spineDelegationRows = ReadSpineOwnerDelegations(spec, sourceNodes, presenter, verifyRuntimeGeometry,
                out var spineDelegationsVerified, out var spineDelegationDiagnostics);
            var spineNonDrawChildRows = ReadSpineNonDrawChildren(spec, sourceNodes, presenter,
                out var spineNonDrawChildrenVerified, out var spineNonDrawChildDiagnostics);
            var verifiedSpineIds = new HashSet<string>(spineDelegationRows.Where(row => row.verified)
                .Select(row => row.sourceComponentId), StringComparer.Ordinal);
            var validSpineDelegations = (presenter == null ? Array.Empty<ProxySpineOwnerDelegation>() :
                presenter.spineOwnerDelegations ?? Array.Empty<ProxySpineOwnerDelegation>())
                .Where(row => row != null && verifiedSpineIds.Contains(row.sourceComponentId)).ToArray();
            var validSpineNonDrawChildKeys = new HashSet<string>(spineNonDrawChildRows.Where(row => row.verified)
                .Select(row => row.sourceComponentId + "\n" + row.childPath), StringComparer.Ordinal);
            var validSpineNonDrawChildren = (presenter == null ? Array.Empty<ProxySpineNonDrawChild>() :
                presenter.spineNonDrawChildren ?? Array.Empty<ProxySpineNonDrawChild>())
                .Where(row => row != null && validSpineNonDrawChildKeys.Contains(row.sourceComponentId + "\n" + row.childPath))
                .ToArray();
            var sourceGraphicsCovered = ValidateSourceGraphicCoverage(spec, sourceNodes, root, presenter == null ?
                Array.Empty<ProxyGraphicBinding>() : presenter.bindings ?? Array.Empty<ProxyGraphicBinding>(),
                validSpineDelegations, validSpineNonDrawChildren, verifyRuntimeGeometry, out var uncoveredGraphicNode);
            var layoutElement = proxyRoot == null ? null : proxyRoot.GetComponent<LayoutElement>();
            var layoutIgnored = layoutElement != null && layoutElement.ignoreLayout;
            var expectedRendererIds = (spec.drawEvents ?? Array.Empty<ProxyDrawEventSpec>())
                .Where(row => row.kind == "renderer").Select(row => row.sourceComponentId).ToArray();
            var actualRendererIds = graphics.Select(row => row.sourceComponentId)
                .Concat(emptyGraphics.Where(row => row.actualQueueIndex >= 0).Select(row => row.sourceComponentId))
                .Distinct(StringComparer.Ordinal).ToArray();
            var nonDrawIds = (spec.nonDrawRenderers ?? Array.Empty<ProxyRendererSpec>()).Select(row => row.sourceComponentId).ToArray();
            var actualNonDrawIds = emptyGraphics.Where(row => row.actualQueueIndex < 0).Select(row => row.sourceComponentId).ToArray();
            var rendererDenominatorOK = expectedRendererIds.Distinct(StringComparer.Ordinal).Count() == expectedRendererIds.Length &&
                expectedRendererIds.OrderBy(id => id, StringComparer.Ordinal).SequenceEqual(actualRendererIds.OrderBy(id => id, StringComparer.Ordinal)) &&
                nonDrawIds.Distinct(StringComparer.Ordinal).Count() == nonDrawIds.Length &&
                nonDrawIds.OrderBy(id => id, StringComparer.Ordinal).SequenceEqual(actualNonDrawIds.OrderBy(id => id, StringComparer.Ordinal));
            var sourceFieldRows = (spec.sourceFields ?? Array.Empty<QueueSortFieldSpec>()).Select(field =>
            {
                var node = field != null && sourceNodes.TryGetValue(field.node, out var value) ? value : null;
                var identity = node == null ? null : node.GetComponent<NativeStaticSortOrderIdentity>();
                return new ProxySortFieldReadback { sourceId = field == null ? null : field.sourceId,
                    node = field == null ? null : field.node, nativeId = field == null ? null : field.nativeId,
                    sourceSortOrder = field == null ? 0f : field.sortOrder,
                    enabledInSource = field != null && field.enabled, identityPresent = identity != null,
                    actualSourceId = identity == null ? null : identity.sourceId,
                    actualNativeId = identity == null ? null : identity.nativeId,
                    actualSortOrder = identity == null ? 0f : identity.sourceSortOrder,
                    actualEnabledInSource = identity != null && identity.enabledInSource,
                    identityComponentEnabled = identity != null && identity.enabled,
                    verified = identity != null && identity.sourceId == field.sourceId && identity.nativeId == field.nativeId &&
                        identity.sourceSortOrder == field.sortOrder && identity.enabledInSource == field.enabled && !identity.enabled };
            }).ToArray();
            var sourceSortRootRows = (spec.sourceSortRoots ?? Array.Empty<ProxySortRootFieldSpec>()).Select(field =>
            {
                var node = field != null && sourceNodes.TryGetValue(field.node, out var value) ? value : null;
                var identity = node == null ? null : node.GetComponent<NativeStaticSortRootIdentity>();
                return new ProxySortRootValueReadback { sourceId = field == null ? null : field.sourceId,
                    node = field == null ? null : field.node, nativeId = field == null ? null : field.nativeId,
                    enabledInSource = field != null && field.enabled, identityPresent = identity != null,
                    actualSourceId = identity == null ? null : identity.sourceId,
                    actualNativeId = identity == null ? null : identity.nativeId,
                    actualEnabledInSource = identity != null && identity.enabledInSource,
                    identityComponentEnabled = identity != null && identity.enabled,
                    verified = identity != null && identity.sourceId == field.sourceId && identity.nativeId == field.nativeId &&
                        identity.enabledInSource == field.enabled && !identity.enabled };
            }).ToArray();
            var fieldsOK = sourceFieldRows.All(row => row != null && row.verified);
            var sortRootsOK = sourceSortRootRows.All(row => row != null && row.verified);
            var expectedSequence = expected;
            var sequenceOK = traversalOk && observedArray.SequenceEqual(expectedSequence);
            var maskReadbacks = new List<ProxyMaskReadback>();
            foreach (var sourceMask in spec.masks ?? Array.Empty<ProxyMaskSpec>())
            {
                if (!proxyMasks.TryGetValue(sourceMask.node, out var maskObject))
                {
                    maskReadbacks.Add(new ProxyMaskReadback { sourceId = sourceMask.sourceId,
                        sourceNode = sourceMask.node, sourceMaskType = sourceMask.maskType, verified = false });
                    continue;
                }
                {
                    var nativeSpec = new MaskSpec { sourceId = sourceMask.sourceId, nativeId = sourceMask.nativeId,
                        node = "proxy:" + sourceMask.node, enabled = sourceMask.enabled, maskType = sourceMask.maskType,
                        inverted = sourceMask.inverted, alphaThreshold = sourceMask.alphaThreshold,
                        spriteFrameUuid = sourceMask.spriteFrameUuid, sourceFieldsJson = sourceMask.sourceFieldsJson,
                        sourceMaterialId = sourceMask.sourceMaterialId ?? String.Empty,
                        resolvedSourceMaterialId = sourceMask.resolvedSourceMaterialId ?? String.Empty,
                        sourceEffectId = sourceMask.sourceEffectId ?? String.Empty,
                        sourceEffectName = sourceMask.sourceEffectName ?? String.Empty,
                        sourceEffectDocumentSha256 = sourceMask.sourceEffectDocumentSha256 ?? String.Empty,
                        unityMaskShaderPath = sourceMask.unityMaskShaderPath, unityMaskShaderSha256 = sourceMask.unityMaskShaderSha256,
                        unityMaskMaterialGuid = sourceMask.unityMaskMaterialGuid, unityMaskMaterialPath = sourceMask.unityMaskMaterialPath };
                    var native = UnityStaticMaskSort.ReadStaticMask(nativeSpec, maskObject, resolveSprite);
                    // For readback, verify the exact generated material asset too.
                    if (sourceMask.maskType == 2)
                    {
                        var image = maskObject.GetComponent<Image>();
                        var material = resolveMaskMaterial == null ? null : resolveMaskMaterial(nativeSpec);
                        native.verified = native.verified && image != null && material != null && image.material == material;
                    }
                    var sourceTransformVerified = sourceNodes.TryGetValue(sourceMask.node, out var sourceMaskNode) &&
                        sourceMaskNode.transform is RectTransform sourceMaskRect &&
                        maskObject.transform is RectTransform proxyMaskRect && WorldRectMatches(sourceMaskRect, proxyMaskRect);
                    var maskComponent = maskObject.GetComponent<Mask>();
                    var maskIdentity = maskObject.GetComponent<NativeStaticMaskIdentity>();
                    var maskGraphic = maskObject.GetComponent<Graphic>();
                    var expectedGraphicType = sourceMask.maskType == 0 ? sourceMask.inverted ?
                        maskGraphic is NativeStaticInvertedMaskGraphic : maskGraphic is Image :
                        sourceMask.maskType == 1 ? maskGraphic is NativeStaticEllipseMaskGraphic : maskGraphic is Image;
                    var checks = new List<string>();
                    if (maskComponent == null) checks.Add("mask-present");
                    if (maskIdentity == null) checks.Add("typed-identity-present");
                    if (maskGraphic == null) checks.Add("graphic-present");
                    if (!expectedGraphicType) checks.Add("mask-graphic-type");
                    var sourceIdentityMatches = maskIdentity != null && maskIdentity.sourceId == sourceMask.sourceId &&
                        maskIdentity.nativeId == sourceMask.nativeId && maskIdentity.sourceMaskType == sourceMask.maskType &&
                        maskIdentity.sourceInverted == sourceMask.inverted;
                    if (!sourceIdentityMatches) checks.Add("source-identity");
                    var sourceFieldsMatches = maskIdentity != null && maskIdentity.sourceFieldsJson == sourceMask.sourceFieldsJson;
                    if (!sourceFieldsMatches) checks.Add("source-fields");
                    var maskEnabledMatches = maskComponent != null && maskComponent.enabled == sourceMask.enabled;
                    if (!maskEnabledMatches) checks.Add("mask-enabled");
                    var maskGraphicHidden = maskComponent != null && !maskComponent.showMaskGraphic;
                    if (!maskGraphicHidden) checks.Add("show-mask-graphic");
                    var graphicEnabledMatches = maskGraphic != null && maskGraphic.enabled == sourceMask.enabled;
                    if (!graphicEnabledMatches) checks.Add("graphic-enabled");
                    var graphicRaycastDisabled = maskGraphic != null && !maskGraphic.raycastTarget;
                    if (!graphicRaycastDisabled) checks.Add("graphic-raycast-target");
                    var sourceMaterialMatches = maskIdentity != null && maskIdentity.sourceMaterialId == sourceMask.sourceMaterialId;
                    if (!sourceMaterialMatches) checks.Add("source-material-id");
                    var resolvedSourceMaterialMatches = maskIdentity != null && maskIdentity.resolvedSourceMaterialId == sourceMask.resolvedSourceMaterialId;
                    if (!resolvedSourceMaterialMatches) checks.Add("resolved-source-material-id");
                    var sourceEffectMatches = maskIdentity != null && maskIdentity.sourceEffectId == sourceMask.sourceEffectId &&
                        maskIdentity.sourceEffectName == sourceMask.sourceEffectName &&
                        maskIdentity.sourceEffectDocumentSha256 == sourceMask.sourceEffectDocumentSha256;
                    if (!sourceEffectMatches) checks.Add("source-effect-proof");
                    var alphaThresholdMatches = maskIdentity != null && maskIdentity.sourceAlphaThreshold == sourceMask.alphaThreshold;
                    if (!alphaThresholdMatches) checks.Add("alpha-threshold");
                    var invertedCanvasMatches = !sourceMask.inverted || maskGraphic is NativeStaticInvertedMaskGraphic &&
                        maskGraphic.GetComponentInParent<Canvas>() != null;
                    if (!invertedCanvasMatches) checks.Add("inverted-canvas");
                    maskReadbacks.Add(new ProxyMaskReadback { sourceId = sourceMask.sourceId,
                        sourceNode = sourceMask.node, nativeMaskType = native.nativeType,
                        sourceMaskType = native.maskType, inverted = native.inverted, enabled = native.enabled,
                        alphaThreshold = native.alphaThreshold, sourceTransformVerified = sourceTransformVerified,
                        maskPresent = maskComponent != null, identityPresent = maskIdentity != null, graphicPresent = maskGraphic != null,
                        graphicTypeMatches = expectedGraphicType, sourceIdentityMatches = sourceIdentityMatches,
                        sourceFieldsMatches = sourceFieldsMatches, maskEnabledMatches = maskEnabledMatches,
                        maskGraphicHidden = maskGraphicHidden, graphicEnabledMatches = graphicEnabledMatches,
                        graphicRaycastDisabled = graphicRaycastDisabled, sourceMaterialMatches = sourceMaterialMatches,
                        resolvedSourceMaterialMatches = resolvedSourceMaterialMatches, sourceEffectMatches = sourceEffectMatches,
                        alphaThresholdMatches = alphaThresholdMatches, invertedCanvasMatches = invertedCanvasMatches,
                        failedChecks = checks.ToArray(),
                        verified = native.verified && sourceTransformVerified });
                    var maskReadback = maskReadbacks[maskReadbacks.Count - 1];
                    if (!maskReadback.verified)
                        structuralDiagnostics.Add("STATIC_SORT_PROXY_MASK_READBACK_INVALID: source=" + maskReadback.sourceId +
                            ";node=" + maskReadback.sourceNode + ";nativeType=" + maskReadback.nativeMaskType +
                            ";maskType=" + maskReadback.sourceMaskType + ";inverted=" + maskReadback.inverted +
                            ";enabled=" + maskReadback.enabled + ";alphaThreshold=" +
                            maskReadback.alphaThreshold.ToString("R", CultureInfo.InvariantCulture) +
                            ";sourceTransform=" + maskReadback.sourceTransformVerified +
                            ";failedChecks=" + String.Join(",", maskReadback.failedChecks ?? Array.Empty<string>()));
                }
            }
            var nativeStructureOK = rootMarker != null && rootMarker.kind == "root" && rootMarker.sourceNode == spec.rootScope &&
                sourceTreePreserved && sourceActivePreserved && fieldsOK && sortRootsOK && sequenceOK && rendererDenominatorOK &&
                sourceGraphicsCovered && layoutIgnored && spineDelegationsVerified && spineNonDrawChildrenVerified && textSourcesVerified &&
                maskReadbacks.Count == (spec.masks ?? Array.Empty<ProxyMaskSpec>()).Length && maskReadbacks.All(mask => mask.verified) &&
                sourceMaskRefsOK && nestedProxyRootsDisabled && presenterRefsOK && presenter.enabled;
            var persistentSnapshotVerified = !provisional && requireSavedPrefabAsset && prefabPathOK && nativeStructureOK &&
                graphics.All(graphic => graphic.staticSnapshotVerified);
            var initializedPresentationVerified = persistentSnapshotVerified && verifyRuntimeGeometry &&
                graphics.All(graphic => graphic.runtimeMeshVerified);
            var passed = !provisional && (verifyRuntimeGeometry ? initializedPresentationVerified : persistentSnapshotVerified);
            return new ProxyQueueReadback { rootScope = spec.rootScope,
                proxyRootName = proxyRoot == null ? null : proxyRoot.name,
                sourceTreePreserved = sourceTreePreserved, sourceFieldsPreserved = fieldsOK,
                sourceSortRootsPreserved = sortRootsOK,
                sourceGraphicsCovered = sourceGraphicsCovered, layoutIgnored = layoutIgnored,
                nestedProxyRootsDisabled = nestedProxyRootsDisabled,
                drawSequenceVerified = sequenceOK, persistentSnapshotVerified = persistentSnapshotVerified,
                initializedPresentationVerified = initializedPresentationVerified,
                runtimeGeometryDeferred = !verifyRuntimeGeometry && !provisional, provisional = provisional,
                readbackMode = provisional ? "pre-save-provisional" : verifyRuntimeGeometry ? "initialized" : "persistent",
                spineDelegationsVerified = spineDelegationsVerified,
                spineDelegationDiagnostics = spineDelegationDiagnostics,
                textSourcesVerified = textSourcesVerified,
                sourceMaskReferencesVerified = sourceMaskRefsOK,
                spineNonDrawChildrenVerified = spineNonDrawChildrenVerified,
                spineNonDrawChildDiagnostics = spineNonDrawChildDiagnostics,
                verified = passed,
                diagnostic = provisional ? "STATIC_SORT_PROXY_PRE_SAVE_PROVISIONAL" : !passed ?
                    "STATIC_SORT_PROXY_NATIVE_MESH_MASK_OR_TREE_READBACK_FAILED" : !verifyRuntimeGeometry ?
                    "STATIC_SORT_PROXY_RUNTIME_GEOMETRY_DEFERRED" : null,
                structuralDiagnostics = structuralDiagnostics.ToArray(),
                graphics = graphics.ToArray(), spineOwnerDelegations = spineDelegationRows,
                spineNonDrawChildren = spineNonDrawChildRows,
                textSources = textSourceReadbacks.ToArray(),
                emptyRenderers = emptyGraphics.ToArray(), masks = maskReadbacks.ToArray(),
                sourceFields = sourceFieldRows, sourceSortRoots = sourceSortRootRows,
                maskSourceIds = (spec.masks ?? Array.Empty<ProxyMaskSpec>()).Select(mask => mask.sourceId).ToArray() };
        }
    }

}
