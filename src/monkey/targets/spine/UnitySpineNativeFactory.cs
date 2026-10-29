// Unity Editor factory for source-exact, static Spine bindings.
// The factory invokes only Spine data parsing and component serialization; it
// never loads or executes recovered game scripts.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using Spine;
using Spine.Unity;
using UnityEditor;
using UnityEngine;
using UnityEngine.UI;

namespace Monkey.Targets.Spine
{
    public static class UnitySpineNativeFactory
    {
        public const string SourceProfile = "cocos24-builtin-spine-material-v1";
        public const string ShaderName = "Monkey/SpineSourceProfile/Colored";

        public enum RendererKind { SkeletonAnimation, SkeletonGraphic }

        [Serializable] public sealed class MaterialVariantSpec
        {
            public string blendMode;
            public string materialAssetPath;
            public int sourceSlotCountAcrossAsset;
            public string sourceSlotCountScope;
        }

        [Serializable] public sealed class AtlasPageSpec
        {
            public string sourceAtlasPage;
            public string nativeAtlasPage;
            public string sourceTextureSourceId;
            public string textureAssetPath;
            public string normalMaterialAssetPath;
            public MaterialVariantSpec[] variants;
        }

        [Serializable] public sealed class DataAssetSpec
        {
            public string sourceAssetId;
            public string skeletonTextAssetPath;
            public string skeletonSha256;
            public string atlasTextAssetPath;
            public string atlasSha256;
            public string atlasAssetPath;
            public string skeletonDataAssetPath;
            public string shaderAssetPath;
            public string shaderSha256;
            public string expectedSpineVersion;
            public float scale;
            public bool premultipliedAlpha;
            public AtlasPageSpec[] pages;
            public string[] requiredAnimations;
            public string[] requiredSkins;
        }

        [Serializable] public sealed class DataAssetReadback
        {
            public string sourceAssetId;
            public string skeletonDataAssetPath;
            public string skeletonDataAssetGuid;
            public string atlasAssetPath;
            public string atlasAssetGuid;
            public string skeletonSha256;
            public string atlasSha256;
            public string spineVersion;
            public string sourceMaterialProfile;
            public string profileShaderName;
            public string profileShaderSha256;
            public bool premultipliedAlpha;
            public float scale;
            public bool scaleVerified;
            public int boneCount;
            public int slotCount;
            public int skinCount;
            public int animationCount;
            public bool nativeAssetIdentityVerified;
            public bool savedSourceReferencesVerified;
            public bool sourceProfileMaterialsVerified;
            public bool staticDataVerified;
            public string[] animations;
            public string[] skins;
            public PageMaterialReadback[] pages;
            public string[] gaps;
        }

        [Serializable] public sealed class PageMaterialReadback
        {
            public string sourceAtlasPage;
            public string nativeAtlasPage;
            public string sourceTextureSourceId;
            public string textureGuid;
            public string normalMaterialGuid;
            public string[] variantModes;
            public string[] variantMaterialGuids;
            public bool referencesVerified;
        }

        [Serializable] public sealed class ComponentReadback
        {
            public string sourceComponentId;
            public string rendererKind;
            public string nativeComponentType;
            public string sourceDataAssetId;
            public string nativeDataAssetPath;
            public string nativeDataAssetGuid;
            public bool staticDataBound;
            public bool sourceDataUnbound;
            public bool enabled;
            public bool componentTypeVerified;
            public bool dataReferenceVerified;
            public bool dataAssetContentVerified;
            public bool fieldsVerified;
            public bool pmaMaterialProfileVerified;
            public bool nativeComplete;
            public bool dynamicAssignmentUnverified;
            public string[] gaps;
        }

        [Serializable] public sealed class StaticPoseReadback
        {
            public string sourceComponentId;
            public string sourceDataAssetId;
            public string nativeDataAssetGuid;
            public string rendererKind;
            public string requestedSkin;
            public string requestedAnimation;
            public string actualSkin;
            public string actualAnimation;
            public float trackTime;
            public bool loop;
            public bool componentEnabled;
            public bool poseVerified;
            public bool sourceCodeExecuted;
            public string timelineStatus;
            public string[] gaps;
        }

        /// <summary>Create the actual Unity Spine renderer selected from target-node evidence.</summary>
        public static Component CreateComponent(GameObject node, string sourceComponentId, RendererKind rendererKind)
        {
            if (node == null) throw new ArgumentNullException(nameof(node));
            if (String.IsNullOrWhiteSpace(sourceComponentId)) throw new ArgumentException("Source component identity is required.", nameof(sourceComponentId));
            Type type;
            if (rendererKind == RendererKind.SkeletonGraphic)
            {
                if (!(node.transform is RectTransform))
                    throw new InvalidOperationException("SkeletonGraphic requires a target RectTransform; importer must establish and verify UI node context first.");
                type = typeof(SkeletonGraphic);
            }
            else if (rendererKind == RendererKind.SkeletonAnimation)
                type = typeof(SkeletonAnimation);
            else throw new ArgumentOutOfRangeException(nameof(rendererKind));

            var component = node.AddComponent(type) as Component;
            if (component == null || component.GetType() != type)
                throw new InvalidOperationException("UNITY_SPINE_NATIVE_COMPONENT_CREATE_FAILED: " + sourceComponentId);
            var behaviour = component as Behaviour;
            if (behaviour != null) behaviour.enabled = false;
            return component;
        }

        /// <summary>
        /// Create and save a real SpineAtlasAsset/SkeletonDataAsset from exact
        /// imported Unity TextAssets, Texture2Ds and a source-pinned shader.
        /// Caller owns exact sourceId-to-path resolution and target scale.
        /// </summary>
        public static DataAssetReadback CreateDataAsset(DataAssetSpec spec)
        {
            ValidateSpec(spec);
            var existing = AssetDatabase.LoadAssetAtPath<SkeletonDataAsset>(spec.skeletonDataAssetPath);
            if (existing != null)
            {
                var existingReadback = ReadDataAssetAsset(spec);
                if (!existingReadback.nativeAssetIdentityVerified || !existingReadback.savedSourceReferencesVerified ||
                    !existingReadback.scaleVerified || !existingReadback.sourceProfileMaterialsVerified)
                    throw new InvalidOperationException("SPINE_EXISTING_NATIVE_ASSET_CONFLICT:" + String.Join(",", existingReadback.gaps));
                return existingReadback;
            }
            var createdPaths = new List<string>();
            try
            {
                var skeletonText = AssetDatabase.LoadAssetAtPath<TextAsset>(spec.skeletonTextAssetPath);
                var atlasText = AssetDatabase.LoadAssetAtPath<TextAsset>(spec.atlasTextAssetPath);
                var shader = AssetDatabase.LoadAssetAtPath<Shader>(spec.shaderAssetPath);
                if (skeletonText == null || atlasText == null)
                    throw new InvalidOperationException("SPINE_SOURCE_TEXT_ASSET_MISSING");
                if (shader == null || shader.name != ShaderName || HashAsset(spec.shaderAssetPath) != spec.shaderSha256)
                    throw new InvalidOperationException("SPINE_PROFILE_SHADER_IDENTITY_MISMATCH");
                if (!String.Equals(HashBytes(skeletonText.bytes), spec.skeletonSha256, StringComparison.OrdinalIgnoreCase) ||
                    !String.Equals(HashBytes(atlasText.bytes), spec.atlasSha256, StringComparison.OrdinalIgnoreCase))
                    throw new InvalidOperationException("SPINE_SOURCE_TEXT_ASSET_HASH_MISMATCH");
                if (String.IsNullOrEmpty(skeletonText.name) || !skeletonText.name.Contains(".skel"))
                    throw new InvalidOperationException("SPINE_BINARY_TEXT_ASSET_NAME_MUST_RETAIN_SKEL_EXTENSION");

                var pageNames = ReadAtlasPageNames(atlasText.text);
                if (!pageNames.SequenceEqual(spec.pages.Select(p => p.nativeAtlasPage), StringComparer.Ordinal))
                    throw new InvalidOperationException("SPINE_ATLAS_PAGE_ORDER_OR_IDENTITY_MISMATCH");

                var normalMaterials = new Material[spec.pages.Length];
                var variantMaterials = new Dictionary<string, Material>(StringComparer.Ordinal);
                for (int index = 0; index < spec.pages.Length; index++)
                {
                    var page = spec.pages[index];
                    var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(page.textureAssetPath);
                    if (texture == null) throw new InvalidOperationException("SPINE_PAGE_TEXTURE_MISSING: " + page.sourceTextureSourceId);
                    normalMaterials[index] = CreateProfileMaterial(spec, shader, texture, page,
                        "normal", page.normalMaterialAssetPath, createdPaths);
                    foreach (var variant in page.variants ?? Array.Empty<MaterialVariantSpec>())
                    {
                        if (variant.sourceSlotCountAcrossAsset <= 0) throw new InvalidOperationException("SPINE_EMPTY_BLEND_VARIANT: " + page.sourceAtlasPage);
                        var variantKey = page.sourceAtlasPage + "\n" + variant.blendMode;
                        if (variantMaterials.ContainsKey(variantKey))
                            throw new InvalidOperationException("SPINE_DUPLICATE_PAGE_BLEND_VARIANT: " + page.sourceAtlasPage + "/" + variant.blendMode);
                        var material = CreateProfileMaterial(spec, shader, texture, page,
                            variant.blendMode, variant.materialAssetPath, createdPaths);
                        variantMaterials.Add(variantKey, material);
                    }
                }

                var atlasAsset = ScriptableObject.CreateInstance<SpineAtlasAsset>();
                atlasAsset.name = Path.GetFileNameWithoutExtension(spec.atlasAssetPath);
                atlasAsset.atlasFile = atlasText;
                atlasAsset.materials = normalMaterials;
                CreateOwnedAsset(atlasAsset, spec.atlasAssetPath, createdPaths);
                AssetDatabase.SaveAssets();

                var savedAtlasAsset = AssetDatabase.LoadAssetAtPath<SpineAtlasAsset>(spec.atlasAssetPath);
                if (savedAtlasAsset == null || savedAtlasAsset.atlasFile != atlasText ||
                    savedAtlasAsset.materials == null || savedAtlasAsset.materials.Length != normalMaterials.Length)
                    throw new InvalidOperationException("SPINE_ATLAS_ASSET_SAVED_REFERENCE_MISMATCH");
                var parsedAtlas = savedAtlasAsset.GetAtlas();
                if (parsedAtlas == null || parsedAtlas.Pages == null || parsedAtlas.Pages.Count != spec.pages.Length)
                    throw new InvalidOperationException("SPINE_ATLAS_NATIVE_PARSE_FAILED");
                for (int index = 0; index < spec.pages.Length; index++)
                {
                    var page = parsedAtlas.Pages[index];
                    if (page.name != spec.pages[index].nativeAtlasPage || !ReferenceEquals(page.rendererObject, normalMaterials[index]))
                        throw new InvalidOperationException("SPINE_ATLAS_NATIVE_PAGE_READBACK_MISMATCH: " + spec.pages[index].sourceAtlasPage);
                }

                var dataAsset = SkeletonDataAsset.CreateRuntimeInstance(skeletonText,
                    new AtlasAssetBase[] { savedAtlasAsset }, false, spec.scale);
                dataAsset.name = Path.GetFileNameWithoutExtension(spec.skeletonDataAssetPath);
                ConfigureBlendMaterials(dataAsset, spec, variantMaterials);
                CreateOwnedAsset(dataAsset, spec.skeletonDataAssetPath, createdPaths);
                AssetDatabase.SaveAssets();
                AssetDatabase.ImportAsset(spec.skeletonDataAssetPath, ImportAssetOptions.ForceSynchronousImport);
                AssetDatabase.SaveAssets();

                var saved = AssetDatabase.LoadAssetAtPath<SkeletonDataAsset>(spec.skeletonDataAssetPath);
                var parsed = saved == null ? null : saved.GetSkeletonData(true);
                if (saved == null || parsed == null)
                    throw new InvalidOperationException("SPINE_SKELETON_DATA_NATIVE_PARSE_FAILED");
                return ReadDataAsset(spec, saved, parsed, variantMaterials);
            }
            catch
            {
                foreach (var path in createdPaths.AsEnumerable().Reverse()) AssetDatabase.DeleteAsset(path);
                AssetDatabase.SaveAssets();
                throw;
            }
        }

        /// <summary>Reopen and strictly re-read a previously created native asset from its exact plan paths.</summary>
        public static DataAssetReadback ReadDataAssetAsset(DataAssetSpec spec)
        {
            ValidateSpec(spec);
            var saved = AssetDatabase.LoadAssetAtPath<SkeletonDataAsset>(spec.skeletonDataAssetPath);
            if (saved == null) throw new InvalidOperationException("SPINE_SAVED_SKELETON_DATA_ASSET_MISSING");
            var parsed = saved.GetSkeletonData(true);
            if (parsed == null) throw new InvalidOperationException("SPINE_SAVED_SKELETON_DATA_PARSE_FAILED");
            var variants = new Dictionary<string, Material>(StringComparer.Ordinal);
            foreach (var page in spec.pages)
            foreach (var variant in page.variants ?? Array.Empty<MaterialVariantSpec>())
            {
                var material = AssetDatabase.LoadAssetAtPath<Material>(variant.materialAssetPath);
                if (material != null) variants[page.sourceAtlasPage + "\n" + variant.blendMode] = material;
            }
            return ReadDataAsset(spec, saved, parsed, variants);
        }

        /// <summary>Bind source settings without enabling the recovered component.</summary>
        public static ComponentReadback ApplyComponent(Component component, string sourceComponentId,
            string sourceDataAssetId, SkeletonDataAsset exactDataAsset,
            IDictionary<string, object> explicitTargetFields, bool sourceHasStaticDataReference,
            DataAssetReadback exactDataAssetReadback = null, bool persistentVisiblePose = false)
        {
            var gaps = new List<string>();
            if (component == null || String.IsNullOrWhiteSpace(sourceComponentId))
                return ComponentFailure(sourceComponentId, "carrier_missing");
            bool isGraphic = component.GetType() == typeof(SkeletonGraphic);
            bool isAnimation = component.GetType() == typeof(SkeletonAnimation);
            if (!isGraphic && !isAnimation) return ComponentFailure(sourceComponentId, "unsupported_native_spine_component_type");
            if (sourceHasStaticDataReference && exactDataAsset == null)
                gaps.Add("exact_skeleton_data_asset_unresolved:" + sourceDataAssetId);
            if (!sourceHasStaticDataReference && exactDataAsset != null)
                gaps.Add("unexpected_skeleton_data_asset_for_unbound_source");

            var fields = NormalizeTargetFields(component, explicitTargetFields);
            if (persistentVisiblePose) fields["timeScale"] = 0.0;
            bool pma = fields.ContainsKey("pmaVertexColors");
            if (isGraphic && pma)
            {
                // SkeletonGraphic has no pmaVertexColors member in this exact
                // runtime. PMA is represented by its per-page material factors.
                fields.Remove("pmaVertexColors");
            }
            UnitySpineBinding.Apply(component, sourceComponentId, exactDataAsset,
                sourceHasStaticDataReference && exactDataAsset != null, fields);
            if (isGraphic && pma) gaps.Add("pma_vertex_color_member_not_applicable_on_skeleton_graphic_material_profile_required");
            var behaviour = component as Behaviour;
            if (behaviour != null) behaviour.enabled = persistentVisiblePose;
            if (persistentVisiblePose && sourceHasStaticDataReference && exactDataAsset != null)
                BuildPersistentStaticPose(component);
            return ReadComponent(sourceComponentId, sourceDataAssetId, component, exactDataAsset,
                sourceHasStaticDataReference, fields, gaps, exactDataAssetReadback, persistentVisiblePose);
        }

        /// <summary>Read a saved/reopened component using the exact sourceId-to-data resolver result.</summary>
        public static ComponentReadback ReadComponent(string sourceComponentId, string sourceDataAssetId,
            Component component, SkeletonDataAsset exactDataAsset, bool sourceHasStaticDataReference,
            IDictionary<string, object> expectedTargetFields, IList<string> inheritedGaps = null,
            DataAssetReadback exactDataAssetReadback = null, bool persistentVisiblePose = false)
        {
            var gaps = new List<string>();
            if (inheritedGaps != null) foreach (var gap in inheritedGaps) AddGap(gaps, gap);
            if (component == null) return ComponentFailure(sourceComponentId, "saved_component_missing");
            var type = component.GetType();
            bool isGraphic = type == typeof(SkeletonGraphic);
            bool isAnimation = type == typeof(SkeletonAnimation);
            if (!isGraphic && !isAnimation) AddGap(gaps, "unsupported_native_spine_component_type");
            var behaviour = component as Behaviour;
            bool enabled = behaviour != null && behaviour.enabled;
            if (enabled != persistentVisiblePose)
                AddGap(gaps, persistentVisiblePose ? "persistent_spine_renderer_not_enabled" : "spine_component_enabled");

            var savedData = ReadDataReference(component);
            bool dataVerified = false;
            string dataPath = null, dataGuid = null;
            if (sourceHasStaticDataReference)
            {
                if (exactDataAsset == null) AddGap(gaps, "exact_skeleton_data_asset_unresolved:" + sourceDataAssetId);
                else
                {
                    dataPath = AssetDatabase.GetAssetPath(exactDataAsset);
                    dataGuid = String.IsNullOrEmpty(dataPath) ? null : AssetDatabase.AssetPathToGUID(dataPath);
                    dataVerified = savedData == exactDataAsset && !String.IsNullOrEmpty(dataGuid);
                    if (!dataVerified) AddGap(gaps, "skeleton_data_native_reference_mismatch:" + sourceDataAssetId);
                }
            }
            else
            {
                dataVerified = savedData == null;
                if (!dataVerified) AddGap(gaps, "source_unbound_component_has_native_data_asset");
                AddGap(gaps, "dynamic_skeleton_data_assignment_unverified");
            }

            bool fieldsVerified = VerifyFields(component, NormalizeTargetFields(component, expectedTargetFields), isGraphic, gaps);
            bool dataContentVerified = sourceHasStaticDataReference && exactDataAsset != null && exactDataAssetReadback != null &&
                exactDataAssetReadback.sourceAssetId == sourceDataAssetId &&
                exactDataAssetReadback.skeletonDataAssetGuid == dataGuid && exactDataAssetReadback.staticDataVerified;
            if (sourceHasStaticDataReference && !dataContentVerified)
                AddGap(gaps, "skeleton_data_asset_content_readback_missing_or_incomplete");
            bool pmaMaterialVerified = true;
            if (isGraphic && expectedTargetFields != null && expectedTargetFields.ContainsKey("pmaVertexColors"))
            {
                pmaMaterialVerified = sourceHasStaticDataReference && exactDataAsset != null && exactDataAssetReadback != null &&
                    exactDataAssetReadback.sourceAssetId == sourceDataAssetId &&
                    exactDataAssetReadback.skeletonDataAssetGuid == dataGuid &&
                    exactDataAssetReadback.sourceMaterialProfile == SourceProfile &&
                    exactDataAssetReadback.profileShaderName == ShaderName &&
                    exactDataAssetReadback.sourceProfileMaterialsVerified &&
                    exactDataAssetReadback.premultipliedAlpha == Convert.ToBoolean(expectedTargetFields["pmaVertexColors"]);
                if (!pmaMaterialVerified) AddGap(gaps, "skeleton_graphic_pma_material_profile_readback_missing_or_mismatched");
            }
            bool typeVerified = isGraphic || isAnimation;
            bool sourceUnbound = !sourceHasStaticDataReference && dataVerified;
            bool complete = typeVerified && dataVerified && dataContentVerified && fieldsVerified &&
                            enabled == persistentVisiblePose && gaps.Count == 0;
            return new ComponentReadback
            {
                sourceComponentId = sourceComponentId, rendererKind = isGraphic ? "SkeletonGraphic" : isAnimation ? "SkeletonAnimation" : "unknown",
                nativeComponentType = type.FullName, sourceDataAssetId = sourceDataAssetId,
                nativeDataAssetPath = dataPath, nativeDataAssetGuid = dataGuid,
                staticDataBound = sourceHasStaticDataReference && dataVerified, sourceDataUnbound = sourceUnbound,
                enabled = enabled, componentTypeVerified = typeVerified, dataReferenceVerified = dataVerified,
                dataAssetContentVerified = dataContentVerified,
                fieldsVerified = fieldsVerified, pmaMaterialProfileVerified = pmaMaterialVerified && isGraphic,
                nativeComplete = complete,
                dynamicAssignmentUnverified = sourceUnbound, gaps = gaps.ToArray(),
            };
        }

        /// <summary>
        /// Sample only the authored initial pose at t=0. This invokes the
        /// pinned native Spine data/runtime APIs, never source game callbacks,
        /// and leaves the component disabled. The resulting runtime skeleton
        /// is a preview readback; saved component fields remain the durable state.
        /// </summary>
        public static StaticPoseReadback SampleInitialPoseAtZero(Component component, string sourceComponentId,
            string sourceDataAssetId, SkeletonDataAsset exactDataAsset, DataAssetReadback dataAssetReadback,
            string requestedSkin, string requestedAnimation, bool loop)
        {
            var gaps = new List<string>();
            var result = new StaticPoseReadback
            {
                sourceComponentId = sourceComponentId, sourceDataAssetId = sourceDataAssetId,
                requestedSkin = requestedSkin, requestedAnimation = requestedAnimation, loop = loop,
                componentEnabled = false, sourceCodeExecuted = false,
                timelineStatus = "only_time_zero_pose_sampled",
            };
            if (component == null || String.IsNullOrWhiteSpace(sourceComponentId))
                return PoseFailure(result, "native_spine_component_missing");
            if (exactDataAsset == null || dataAssetReadback == null || !dataAssetReadback.staticDataVerified ||
                dataAssetReadback.sourceAssetId != sourceDataAssetId)
                return PoseFailure(result, "exact_verified_skeleton_data_asset_missing");
            var path = AssetDatabase.GetAssetPath(exactDataAsset);
            var guid = String.IsNullOrEmpty(path) ? null : AssetDatabase.AssetPathToGUID(path);
            if (String.IsNullOrEmpty(guid) || guid != dataAssetReadback.skeletonDataAssetGuid)
                return PoseFailure(result, "skeleton_data_asset_guid_mismatch");

            Skeleton skeleton;
            global::Spine.AnimationState state;
            try
            {
                if (component.GetType() == typeof(SkeletonAnimation))
                {
                    var renderer = (SkeletonAnimation)component;
                    renderer.Initialize(true, true);
                    skeleton = renderer.Skeleton; state = renderer.AnimationState;
                    result.rendererKind = "SkeletonAnimation";
                }
                else if (component.GetType() == typeof(SkeletonGraphic))
                {
                    var renderer = (SkeletonGraphic)component;
                    renderer.Initialize(true);
                    skeleton = renderer.Skeleton; state = renderer.AnimationState;
                    result.rendererKind = "SkeletonGraphic";
                }
                else return PoseFailure(result, "unsupported_native_spine_component_type");
            }
            catch (Exception error) { return PoseFailure(result, "native_pose_initialize_failed:" + error.GetType().Name); }

            if (skeleton == null || state == null) return PoseFailure(result, "native_skeleton_or_animation_state_missing");
            if (!String.IsNullOrEmpty(requestedSkin))
            {
                if (skeleton.Data.FindSkin(requestedSkin) == null) AddGap(gaps, "requested_skin_missing:" + requestedSkin);
                else { skeleton.SetSkin(requestedSkin); skeleton.SetSlotsToSetupPose(); }
            }
            else skeleton.SetToSetupPose();

            TrackEntry entry = null;
            if (!String.IsNullOrEmpty(requestedAnimation))
            {
                var animation = skeleton.Data.FindAnimation(requestedAnimation);
                if (animation == null) AddGap(gaps, "requested_animation_missing:" + requestedAnimation);
                else entry = state.SetAnimation(0, animation, loop);
            }
            if (entry != null) entry.TrackTime = 0f;
            // Applying an AnimationState does not advance track time; deliberately
            // do not call Update/Complete/event queue processing or any source code.
            state.Apply(skeleton);
            skeleton.UpdateWorldTransform();
            var current = state.GetCurrent(0);
            result.nativeDataAssetGuid = guid;
            result.actualSkin = skeleton.Skin == null ? null : skeleton.Skin.Name;
            result.actualAnimation = current == null || current.Animation == null ? null : current.Animation.Name;
            result.trackTime = current == null ? 0f : current.TrackTime;
            result.componentEnabled = ((Behaviour)component).enabled;
            if (!String.IsNullOrEmpty(requestedSkin) && result.actualSkin != requestedSkin)
                AddGap(gaps, "sampled_skin_mismatch:" + requestedSkin);
            if (!String.IsNullOrEmpty(requestedAnimation) && result.actualAnimation != requestedAnimation)
                AddGap(gaps, "sampled_animation_mismatch:" + requestedAnimation);
            if (Math.Abs(result.trackTime) > 0.000001f) AddGap(gaps, "sampled_track_time_not_zero");
            result.poseVerified = gaps.Count == 0;
            result.gaps = gaps.ToArray();
            return result;
        }

        static DataAssetReadback ReadDataAsset(DataAssetSpec spec, SkeletonDataAsset saved, SkeletonData parsed,
            IDictionary<string, Material> variantMaterials)
        {
            var gaps = new List<string>();
            var dataPath = AssetDatabase.GetAssetPath(saved);
            var atlas = saved.atlasAssets != null && saved.atlasAssets.Length == 1 ? saved.atlasAssets[0] as SpineAtlasAsset : null;
            var atlasPath = atlas == null ? null : AssetDatabase.GetAssetPath(atlas);
            bool identity = dataPath == spec.skeletonDataAssetPath && !String.IsNullOrEmpty(AssetDatabase.AssetPathToGUID(dataPath)) &&
                atlasPath == spec.atlasAssetPath && !String.IsNullOrEmpty(AssetDatabase.AssetPathToGUID(atlasPath));
            bool refs = saved.skeletonJSON != null && HashBytes(saved.skeletonJSON.bytes) == spec.skeletonSha256 &&
                atlas != null && atlas.atlasFile != null && HashBytes(atlas.atlasFile.bytes) == spec.atlasSha256;
            bool scaleVerified = Math.Abs(saved.scale - spec.scale) <= 0.000001f;
            if (!identity) AddGap(gaps, "native_data_asset_identity_unverified");
            if (!refs) AddGap(gaps, "saved_data_asset_source_reference_mismatch");
            if (!scaleVerified) AddGap(gaps, "saved_skeleton_data_scale_mismatch");

            bool materialReadback = true;
            var pinnedShader = AssetDatabase.LoadAssetAtPath<Shader>(spec.shaderAssetPath);
            if (pinnedShader == null || pinnedShader.name != ShaderName || HashAsset(spec.shaderAssetPath) != spec.shaderSha256)
                materialReadback = false;
            var parsedAtlas = atlas == null ? null : atlas.GetAtlas();
            if (parsedAtlas == null || parsedAtlas.Pages == null || parsedAtlas.Pages.Count != spec.pages.Length) materialReadback = false;
            else for (int index = 0; index < spec.pages.Length; index++)
            {
                var page = parsedAtlas.Pages[index];
                var expected = atlas.materials[index];
                if (page.name != spec.pages[index].nativeAtlasPage || !ReferenceEquals(page.rendererObject, expected) ||
                    expected == null || expected.mainTexture != AssetDatabase.LoadAssetAtPath<Texture2D>(spec.pages[index].textureAssetPath) ||
                    expected.shader != pinnedShader || !BlendMatches(expected, spec.premultipliedAlpha, "normal"))
                    materialReadback = false;
            }
            if (!VerifyBlendMaterials(saved, spec, variantMaterials)) materialReadback = false;
            if (!materialReadback) AddGap(gaps, "source_profile_native_material_readback_mismatch");

            var animationNames = parsed.Animations.Items.Select(item => item.Name).ToArray();
            var skinNames = parsed.Skins.Items.Select(item => item.Name).ToArray();
            bool catalogVerified = String.IsNullOrEmpty(spec.expectedSpineVersion) || parsed.Version == spec.expectedSpineVersion;
            if (!catalogVerified) AddGap(gaps, "native_spine_version_mismatch:" + parsed.Version);
            foreach (var name in spec.requiredAnimations ?? Array.Empty<string>())
                if (!animationNames.Contains(name, StringComparer.Ordinal)) AddGap(gaps, "requested_animation_missing:" + name);
            foreach (var name in spec.requiredSkins ?? Array.Empty<string>())
                if (!skinNames.Contains(name, StringComparer.Ordinal)) AddGap(gaps, "requested_skin_missing:" + name);

            var pageReadbacks = new List<PageMaterialReadback>();
            for (int index = 0; index < spec.pages.Length; index++)
            {
                var pageSpec = spec.pages[index];
                var texture = AssetDatabase.LoadAssetAtPath<Texture2D>(pageSpec.textureAssetPath);
                var normal = atlas != null && atlas.materials != null && index < atlas.materials.Length ? atlas.materials[index] : null;
                var variantGuids = new List<string>(); var variantModes = new List<string>();
                bool pageRefs = texture != null && normal != null && normal.mainTexture == texture && normal.shader == pinnedShader;
                foreach (var variant in pageSpec.variants ?? Array.Empty<MaterialVariantSpec>())
                {
                    var material = variantsOrNull(variantMaterials, pageSpec.sourceAtlasPage, variant.blendMode);
                    var materialPath = material == null ? null : AssetDatabase.GetAssetPath(material);
                    var materialGuid = String.IsNullOrEmpty(materialPath) ? null : AssetDatabase.AssetPathToGUID(materialPath);
                    variantModes.Add(variant.blendMode); variantGuids.Add(materialGuid);
                    pageRefs &= material != null && material.mainTexture == texture && material.shader == pinnedShader &&
                        BlendMatches(material, spec.premultipliedAlpha, variant.blendMode) && !String.IsNullOrEmpty(materialGuid);
                }
                var texturePath = texture == null ? null : AssetDatabase.GetAssetPath(texture);
                var normalPath = normal == null ? null : AssetDatabase.GetAssetPath(normal);
                var textureGuid = String.IsNullOrEmpty(texturePath) ? null : AssetDatabase.AssetPathToGUID(texturePath);
                var normalGuid = String.IsNullOrEmpty(normalPath) ? null : AssetDatabase.AssetPathToGUID(normalPath);
                pageRefs &= !String.IsNullOrEmpty(textureGuid) && !String.IsNullOrEmpty(normalGuid);
                if (!pageRefs) AddGap(gaps, "atlas_page_material_native_identity_unverified:" + pageSpec.sourceAtlasPage);
                pageReadbacks.Add(new PageMaterialReadback
                {
                    sourceAtlasPage = pageSpec.sourceAtlasPage, nativeAtlasPage = pageSpec.nativeAtlasPage,
                    sourceTextureSourceId = pageSpec.sourceTextureSourceId, textureGuid = textureGuid,
                    normalMaterialGuid = normalGuid, variantModes = variantModes.ToArray(),
                    variantMaterialGuids = variantGuids.ToArray(), referencesVerified = pageRefs,
                });
            }
            bool allPageReferencesVerified = pageReadbacks.Count == spec.pages.Length && pageReadbacks.All(page => page.referencesVerified);
            bool profileMaterialsVerified = materialReadback && allPageReferencesVerified;
            if (!allPageReferencesVerified) AddGap(gaps, "source_profile_material_native_guids_unverified");

            return new DataAssetReadback
            {
                sourceAssetId = spec.sourceAssetId, skeletonDataAssetPath = dataPath,
                skeletonDataAssetGuid = AssetDatabase.AssetPathToGUID(dataPath), atlasAssetPath = atlasPath,
                atlasAssetGuid = AssetDatabase.AssetPathToGUID(atlasPath), skeletonSha256 = HashBytes(saved.skeletonJSON.bytes),
                atlasSha256 = HashBytes(atlas.atlasFile.bytes), spineVersion = parsed.Version,
                sourceMaterialProfile = SourceProfile, profileShaderName = pinnedShader == null ? null : pinnedShader.name,
                profileShaderSha256 = pinnedShader == null ? null : HashAsset(spec.shaderAssetPath),
                premultipliedAlpha = spec.premultipliedAlpha, scale = saved.scale, scaleVerified = scaleVerified,
                boneCount = parsed.Bones.Count, slotCount = parsed.Slots.Count, skinCount = parsed.Skins.Count,
                animationCount = parsed.Animations.Count, nativeAssetIdentityVerified = identity,
                savedSourceReferencesVerified = refs, sourceProfileMaterialsVerified = profileMaterialsVerified,
                staticDataVerified = identity && refs && scaleVerified && profileMaterialsVerified && catalogVerified && parsed.Bones.Count > 0 &&
                    !gaps.Any(gap => gap.StartsWith("requested_animation_missing:", StringComparison.Ordinal) ||
                                     gap.StartsWith("requested_skin_missing:", StringComparison.Ordinal)),
                animations = animationNames, skins = skinNames, pages = pageReadbacks.ToArray(), gaps = gaps.ToArray(),
            };
        }

        static Material variantsOrNull(IDictionary<string, Material> variants, string sourcePage, string mode)
        {
            return variants.TryGetValue(sourcePage + "\n" + mode, out var material) ? material : null;
        }

        static bool VerifyBlendMaterials(SkeletonDataAsset asset, DataAssetSpec spec, IDictionary<string, Material> variants)
        {
            if (asset.blendModeMaterials == null) return variants.Count == 0;
            var blend = asset.blendModeMaterials;
            var fields = new Dictionary<string, List<BlendModeMaterials.ReplacementMaterial>>(StringComparer.Ordinal)
            {
                ["additive"] = blend.additiveMaterials,
                ["multiply"] = blend.multiplyMaterials,
                ["screen"] = blend.screenMaterials,
            };
            foreach (var page in spec.pages)
            foreach (var variant in page.variants ?? Array.Empty<MaterialVariantSpec>())
            {
                if (!fields.TryGetValue(variant.blendMode, out var rows)) return false;
                var item = rows.FirstOrDefault(row => row.pageName == page.nativeAtlasPage);
                if (item == null || !variants.TryGetValue(page.sourceAtlasPage + "\n" + variant.blendMode, out var expected) ||
                    item.material != expected || !BlendMatches(item.material, spec.premultipliedAlpha, variant.blendMode))
                    return false;
            }
            return true;
        }

        static void ConfigureBlendMaterials(SkeletonDataAsset asset, DataAssetSpec spec, IDictionary<string, Material> variants)
        {
            var blend = asset.blendModeMaterials ?? new BlendModeMaterials();
            blend.applyAdditiveMaterial = false;
            blend.additiveMaterials.Clear(); blend.multiplyMaterials.Clear(); blend.screenMaterials.Clear();
            foreach (var page in spec.pages)
            foreach (var variant in page.variants ?? Array.Empty<MaterialVariantSpec>())
            {
                var row = new BlendModeMaterials.ReplacementMaterial
                {
                    pageName = page.nativeAtlasPage,
                    material = variants[page.sourceAtlasPage + "\n" + variant.blendMode],
                };
                if (variant.blendMode == "additive") { blend.additiveMaterials.Add(row); blend.applyAdditiveMaterial = true; }
                else if (variant.blendMode == "multiply") blend.multiplyMaterials.Add(row);
                else if (variant.blendMode == "screen") blend.screenMaterials.Add(row);
            }
            asset.blendModeMaterials = blend;
        }

        static Material CreateProfileMaterial(DataAssetSpec spec, Shader shader, Texture2D texture,
            AtlasPageSpec page, string mode, string path, List<string> createdPaths)
        {
            if (String.IsNullOrWhiteSpace(path) || !path.StartsWith("Assets/", StringComparison.Ordinal))
                throw new InvalidOperationException("SPINE_MATERIAL_PATH_INVALID: " + mode);
            if (AssetDatabase.LoadAssetAtPath<Material>(path) != null || File.Exists(AbsoluteAssetPath(path)))
                throw new InvalidOperationException("SPINE_MATERIAL_ASSET_COLLISION: " + path);
            var material = new Material(shader) { name = Path.GetFileNameWithoutExtension(path), mainTexture = texture };
            if (!material.HasProperty("_SrcBlend") || !material.HasProperty("_DstBlend"))
            { UnityEngine.Object.DestroyImmediate(material); throw new InvalidOperationException("SPINE_PROFILE_SHADER_BLEND_PROPERTIES_MISSING"); }
            try { Monkey.Targets.SpineMaterials.UnitySpineMaterialBindings.ConfigureProfileMaterial(material, mode, spec.premultipliedAlpha); }
            catch { UnityEngine.Object.DestroyImmediate(material); throw; }
            AssetDatabase.CreateAsset(material, path); createdPaths.Add(path);
            var saved = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (saved == null || saved.shader != shader || saved.mainTexture != texture ||
                !Monkey.Targets.SpineMaterials.UnitySpineMaterialBindings.ProfileMaterialMatches(saved, mode, spec.premultipliedAlpha))
                throw new InvalidOperationException("SPINE_PROFILE_MATERIAL_SAVED_READBACK_MISMATCH: " + page.sourceAtlasPage + "/" + mode);
            return saved;
        }

        static bool BlendMatches(Material material, bool pma, string mode)
        {
            return Monkey.Targets.SpineMaterials.UnitySpineMaterialBindings.ProfileMaterialMatches(material, mode, pma);
        }

        static void CreateOwnedAsset(UnityEngine.Object asset, string path, List<string> createdPaths)
        {
            if (asset == null || String.IsNullOrWhiteSpace(path) || !path.StartsWith("Assets/", StringComparison.Ordinal))
                throw new InvalidOperationException("SPINE_NATIVE_ASSET_PATH_INVALID");
            if (AssetDatabase.LoadMainAssetAtPath(path) != null || File.Exists(AbsoluteAssetPath(path)))
                throw new InvalidOperationException("SPINE_NATIVE_ASSET_COLLISION: " + path);
            AssetDatabase.CreateAsset(asset, path); createdPaths.Add(path); EditorUtility.SetDirty(asset);
        }

        static bool VerifyFields(Component component, IDictionary<string, object> expected, bool isGraphic, List<string> gaps)
        {
            if (expected == null) return true;
            bool verified = true;
            foreach (var pair in expected)
            {
                if (isGraphic && pair.Key == "pmaVertexColors") continue;
                object actual;
                if (!TryReadMember(component, pair.Key, out actual) || !System.Object.Equals(actual, CoerceExpected(pair.Value, actual == null ? null : actual.GetType())))
                { AddGap(gaps, "native_field_readback_mismatch:" + pair.Key); verified = false; }
            }
            return verified;
        }

        static void BuildPersistentStaticPose(Component component)
        {
            if (component.GetType() == typeof(SkeletonGraphic))
            {
                var graphic = (SkeletonGraphic)component;
                graphic.freeze = false;
                graphic.Initialize(true);
                graphic.Update(0f);
                graphic.UpdateMesh(keepRendererCount: true);
                graphic.SetVerticesDirty();
                graphic.SetMaterialDirty();
                return;
            }
            if (component.GetType() == typeof(SkeletonAnimation))
            {
                var animation = (SkeletonAnimation)component;
                animation.Initialize(true, true);
                animation.Update(0f);
                animation.LateUpdate();
                return;
            }
            throw new InvalidOperationException("SPINE_PERSISTENT_POSE_UNSUPPORTED_RENDERER");
        }

        static Dictionary<string, object> NormalizeTargetFields(Component component, IDictionary<string, object> source)
        {
            var result = source == null
                ? new Dictionary<string, object>()
                : new Dictionary<string, object>(source);
            if (component != null && component.GetType() == typeof(SkeletonAnimation))
            {
                if (result.TryGetValue("startingAnimation", out var animation))
                { result.Remove("startingAnimation"); result["AnimationName"] = animation; }
                if (result.TryGetValue("startingLoop", out var loop))
                { result.Remove("startingLoop"); result["loop"] = loop; }
            }
            return result;
        }

        static UnityEngine.Object ReadDataReference(Component component)
        {
            for (var type = component.GetType(); type != null; type = type.BaseType)
            {
                var property = type.GetProperty("SkeletonDataAsset", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.DeclaredOnly);
                if (property != null && typeof(UnityEngine.Object).IsAssignableFrom(property.PropertyType)) return property.GetValue(component, null) as UnityEngine.Object;
                var field = type.GetField("skeletonDataAsset", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.DeclaredOnly);
                if (field != null && typeof(UnityEngine.Object).IsAssignableFrom(field.FieldType)) return field.GetValue(component) as UnityEngine.Object;
            }
            return null;
        }

        static bool TryReadMember(object target, string name, out object value)
        {
            for (var type = target.GetType(); type != null; type = type.BaseType)
            {
                var property = type.GetProperty(name, System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.DeclaredOnly);
                if (property != null && property.CanRead) { value = property.GetValue(target, null); return true; }
                var field = type.GetField(name, System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.Public | System.Reflection.BindingFlags.NonPublic | System.Reflection.BindingFlags.DeclaredOnly);
                if (field != null) { value = field.GetValue(target); return true; }
            }
            value = null; return false;
        }

        static object CoerceExpected(object value, Type type)
        {
            if (value == null || type == null || type.IsInstanceOfType(value)) return value;
            if (type.IsEnum) return value is string text ? Enum.Parse(type, text, false) : Enum.ToObject(type, value);
            return Convert.ChangeType(value, type);
        }

        static void ValidateSpec(DataAssetSpec spec)
        {
            if (spec == null || String.IsNullOrWhiteSpace(spec.sourceAssetId) ||
                !IsSha(spec.skeletonSha256) || !IsSha(spec.atlasSha256) || !IsSha(spec.shaderSha256) ||
                String.IsNullOrWhiteSpace(spec.skeletonDataAssetPath) || String.IsNullOrWhiteSpace(spec.atlasAssetPath) ||
                !IsFinite(spec.scale) || spec.scale <= 0f || spec.pages == null || spec.pages.Length == 0)
                throw new InvalidOperationException("SPINE_NATIVE_DATA_ASSET_SPEC_INVALID");
            if (spec.pages.Any(page => page == null || String.IsNullOrWhiteSpace(page.sourceAtlasPage) ||
                String.IsNullOrWhiteSpace(page.sourceTextureSourceId) || String.IsNullOrWhiteSpace(page.textureAssetPath) ||
                String.IsNullOrWhiteSpace(page.normalMaterialAssetPath)))
                throw new InvalidOperationException("SPINE_NATIVE_ATLAS_PAGE_SPEC_INVALID");
        }

        static string[] ReadAtlasPageNames(string atlas)
        {
            var lines = (atlas ?? String.Empty).Replace("\r\n", "\n").Replace('\r', '\n').Split('\n');
            var result = new List<string>();
            for (int i = 0; i + 1 < lines.Length; i++)
            {
                var line = lines[i];
                if (line.Length > 0 && !Char.IsWhiteSpace(line[0]) && !line.Contains(":") &&
                    (lines[i + 1].StartsWith("size:", StringComparison.Ordinal) || lines[i + 1].StartsWith("format:", StringComparison.Ordinal)))
                    result.Add(line);
            }
            if (result.Count == 0 || result.Distinct(StringComparer.Ordinal).Count() != result.Count)
                throw new InvalidOperationException("SPINE_ATLAS_PAGE_DECLARATIONS_INVALID");
            return result.ToArray();
        }

        static bool IsSha(string value) => value != null && value.Length == 64 && value.All(Uri.IsHexDigit);
        static bool IsFinite(float value) => !Single.IsNaN(value) && !Single.IsInfinity(value);
        static void AddGap(List<string> gaps, string value) { if (!gaps.Contains(value)) gaps.Add(value); }
        static ComponentReadback ComponentFailure(string sourceId, string gap) => new ComponentReadback
        {
            sourceComponentId = sourceId, componentTypeVerified = false, dataReferenceVerified = false,
            fieldsVerified = false, nativeComplete = false, enabled = false, gaps = new[] { gap },
        };
        static StaticPoseReadback PoseFailure(StaticPoseReadback result, string gap)
        {
            result.gaps = new[] { gap };
            result.poseVerified = false;
            return result;
        }
        static string HashBytes(byte[] bytes) { using (var sha = SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(bytes)).Replace("-", "").ToLowerInvariant(); }
        static string HashAsset(string assetPath) => HashBytes(File.ReadAllBytes(AbsoluteAssetPath(assetPath)));
        static string AbsoluteAssetPath(string assetPath) => Path.GetFullPath(Path.Combine(Directory.GetParent(Application.dataPath).FullName, assetPath));
    }
}
