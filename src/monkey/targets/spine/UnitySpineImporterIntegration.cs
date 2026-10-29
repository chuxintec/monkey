// Optional Editor hook emitted only with a Spine native stage. The base
// MonkeyImporter stays free of a hard dependency on the Spine runtime.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEngine;
using Spine.Unity;
using Monkey.Targets.Spine;

public static partial class MonkeyImporter
{
    [Serializable] public sealed class StaticSpineSavedReadback
    {
        public int schemaVersion = 1;
        public string sourcePrefabId;
        public string sourceManifestSha256;
        public string normalizedIrSha256;
        public bool staticNativeVerified;
        public bool dynamicBehaviorComplete;
        public string visualPolicy;
        public int componentCount;
        public int dataAssetCount;
        public UnitySpineNativeFactory.DataAssetReadback[] dataAssets;
        public UnitySpineNativeFactory.ComponentReadback[] components;
        public StaticSpineVisualIdentity[] visualComponents;
        public UnitySpineNativeStage.StageGap[] stageGaps;
        public string[] failures;
    }
    [Serializable] public sealed class StaticSpineVisualIdentity
    {
        public string sourceComponentId;
        public string rendererKind;
        public float sourceTimeScale;
        public float nativeTimeScale;
        public bool sourceTimeScaleVerified;
        public bool rendererEnabled;
        public bool persistentVisiblePose;
        public float[] sourceColor;
        public float[] nativeColor;
        public bool sourceColorVerified;
        public bool nativeColorVerified;
    }

    const string StaticSpinePlanPath = "Assets/Game/Editor/Conversion/spine-native-binding-plan.json";
    const string StaticSpineReadbackRoot = "Analysis/Readback/Spine";
    static UnitySpineNativeStage.Plan staticSpinePlan;
    static UnitySpineNativeStage.CreateResult staticSpineAssets;
    static readonly Dictionary<string, string> staticSpineNodeSourceIdsByComponent = new Dictionary<string, string>(StringComparer.Ordinal);

    // Base importer declares these optional partial methods and calls them only
    // at the matching stage boundaries. No stage file means no generated helper
    // and no Spine runtime assembly dependency for ordinary candidates.
    static partial void PrepareStaticSpine(Plan plan, Dictionary<string, GameObject> nodes)
    {
        if (!File.Exists(StaticSpinePlanPath)) return;
        if (plan == null || plan.nodes == null || plan.components == null || plan.sourcePrefabs == null || nodes == null)
            throw new InvalidOperationException("SPINE_IMPORTER_PLAN_GRAPH_MISSING");

        var parsed = UnitySpineNativeStage.Parse(File.ReadAllText(StaticSpinePlanPath));
        var componentById = plan.components.ToDictionary(row => row.sourceId, StringComparer.Ordinal);
        var prefabById = plan.sourcePrefabs.ToDictionary(row => row.sourceId, StringComparer.Ordinal);
        foreach (var row in parsed.components)
        {
            if (row == null || !componentById.ContainsKey(row.sourceComponentId) || !prefabById.ContainsKey(row.sourcePrefabId))
                throw new InvalidOperationException("SPINE_STAGE_SOURCE_COMPONENT_NOT_IN_TARGET_PLAN:" + (row == null ? "null" : row.sourceComponentId));
            var nodeId = ResolveSpineNodeId(prefabById[row.sourcePrefabId], row.sourceNodeId);
            if (nodeId == null || !nodes.ContainsKey(nodeId))
                throw new InvalidOperationException("SPINE_STAGE_SOURCE_NODE_NOT_IN_TARGET_PLAN:" + row.sourceComponentId);
        }
        if (parsed.dataAssets.Any(row => row.factoryInput == null || row.factoryInput.scale != 1f ||
                                         row.factoryInput.sourceAssetId != row.sourceAssetId))
            throw new InvalidOperationException("SPINE_STAGE_DATA_ASSET_SCALE_OR_IDENTITY_MISMATCH");

        staticSpinePlan = parsed;
        staticSpineNodeSourceIdsByComponent.Clear();
        foreach (var row in parsed.components)
            staticSpineNodeSourceIdsByComponent.Add(row.sourceComponentId,
                ResolveSpineNodeId(prefabById[row.sourcePrefabId], row.sourceNodeId));
        staticSpineAssets = UnitySpineNativeStage.CreateDataAssets(staticSpinePlan);
        if (staticSpineAssets.gaps.Count != 0 || staticSpineAssets.dataAssets.Count != staticSpinePlan.dataAssets.Length)
            throw new InvalidOperationException("SPINE_DATA_ASSET_CREATE_FAILED: " + JsonUtility.ToJson(staticSpineAssets.gaps.ToArray()));

        var all = UnitySpineNativeStage.CreateComponents(staticSpinePlan, staticSpineAssets,
            (prefabId, sourceNodeId) => {
                if (!prefabById.TryGetValue(prefabId, out var prefab)) return null;
                var nodeId = ResolveSpineNodeId(prefab, sourceNodeId);
                return nodeId != null && nodes.TryGetValue(nodeId, out var node) ? node : null;
            });
        foreach (var row in staticSpinePlan.components)
        {
            if (!all.components.TryGetValue(row.sourceComponentId, out var component))
                throw new InvalidOperationException("SPINE_COMPONENT_CREATE_FAILED:" + row.sourceComponentId);
            var node = component.gameObject;
            if (component.GetType() == typeof(SkeletonGraphic))
            {
                var nodeId = staticSpineNodeSourceIdsByComponent[row.sourceComponentId];
                var sourceNode = plan.nodes.SingleOrDefault(candidate => candidate.sourceId == nodeId);
                if (sourceNode == null)
                    throw new InvalidOperationException("SPINE_SOURCE_NODE_COLOR_IDENTITY_MISSING:" + row.sourceComponentId);
                var expectedColor = SourceSpineNodeColor(sourceNode, row.sourceComponentId);
                var graphic = (SkeletonGraphic)component;
                graphic.color = expectedColor;
                if (!SpineGraphicColorMatches(graphic, sourceNode, row.sourceComponentId))
                    throw new InvalidOperationException("SPINE_GRAPHIC_COLOR_ASSIGNMENT_MISMATCH:" + row.sourceComponentId);
            }
            if (node.GetComponents<UnitySpineSourceIdentity>().Any(marker => marker.sourceComponentId == row.sourceComponentId))
                throw new InvalidOperationException("SPINE_SOURCE_IDENTITY_ALREADY_EXISTS:" + row.sourceComponentId);
            var identity = node.AddComponent<UnitySpineSourceIdentity>();
            identity.sourceComponentId = row.sourceComponentId;
            identity.rendererKind = component.GetType().FullName;
            identity.renderer = component as Behaviour;
            identity.sourceTimeScale = (float)row.sourceTimeScale;
            identity.nativeTimeScale = ReadSpineTimeScale(component);
            identity.sourceTimeScaleVerified = row.sourceTimeScaleVerified;
            identity.persistentVisiblePose = row.persistentVisiblePose;
            identity.enabled = false;
        }
        var expectedIds = new HashSet<string>(staticSpinePlan.components.Select(row => row.sourceComponentId), StringComparer.Ordinal);
        var applyById = all.componentReadbacks.ToDictionary(row => row.sourceComponentId, StringComparer.Ordinal);
        var readIds = new HashSet<string>(applyById.Keys, StringComparer.Ordinal);
        if (!expectedIds.SetEquals(readIds) || all.gaps.Any(gap => gap.code == "SPINE_COMPONENT_CREATE_FAILED"))
            throw new InvalidOperationException("SPINE_COMPONENT_CREATE_DENOMINATOR_MISMATCH: " + JsonUtility.ToJson(all.gaps.ToArray()));
        foreach (var row in staticSpinePlan.components)
        {
            var readback = applyById[row.sourceComponentId];
            if (!readback.componentTypeVerified || !readback.dataReferenceVerified || !readback.fieldsVerified || !readback.enabled ||
                row.sourceHasStaticDataReference && (!readback.staticDataBound || !readback.dataAssetContentVerified) ||
                !row.sourceHasStaticDataReference && !readback.sourceDataUnbound)
                throw new InvalidOperationException("SPINE_COMPONENT_CREATE_READBACK_FAILED:" + row.sourceComponentId + ":" + JsonUtility.ToJson(readback));
        }
    }

    // Domain reload clears these fields. Resolve/readback may run during the
    // saved-Prefab verification pass, so reload only the frozen stage JSON;
    // never call CreateDataAssets/CreateComponents from this path.
    static UnitySpineNativeStage.Plan LoadFrozenStaticSpinePlan()
    {
        if (staticSpinePlan != null) return staticSpinePlan;
        if (!File.Exists(StaticSpinePlanPath)) return null;
        var parsed = UnitySpineNativeStage.Parse(File.ReadAllText(StaticSpinePlanPath));
        staticSpineNodeSourceIdsByComponent.Clear();
        foreach (var row in parsed.components)
        {
            var nodeId = ResolveNativeSpineNodeId(row.sourcePrefabId, row.sourceNodeId);
            if (String.IsNullOrWhiteSpace(row.sourceComponentId) || String.IsNullOrWhiteSpace(nodeId) ||
                staticSpineNodeSourceIdsByComponent.ContainsKey(row.sourceComponentId))
                throw new InvalidOperationException("SPINE_FROZEN_PLAN_COMPONENT_NODE_IDENTITY_INVALID:" + (row.sourceComponentId ?? "null"));
            staticSpineNodeSourceIdsByComponent.Add(row.sourceComponentId, nodeId);
        }
        staticSpinePlan = parsed;
        return staticSpinePlan;
    }

    static string ResolveNativeSpineNodeId(string prefabId, string sourceNodeId)
    {
        if (String.IsNullOrWhiteSpace(prefabId) || String.IsNullOrWhiteSpace(sourceNodeId)) return null;
        if (sourceNodeId.StartsWith(prefabId + "#", StringComparison.Ordinal)) return sourceNodeId;
        return sourceNodeId.All(Char.IsDigit) ? prefabId + "#" + sourceNodeId : sourceNodeId;
    }

    // Called by the main target's exact sourceId resolver after its normal
    // node/component/asset maps. Unknown IDs are left untouched for the caller
    // to report as unresolved instead of being guessed by name.
    static partial void ResolveStaticSpineReference(string id, Dictionary<string, GameObject> nodes, ref UnityEngine.Object value)
    {
        if (String.IsNullOrWhiteSpace(id)) return;
        var frozen = LoadFrozenStaticSpinePlan();
        if (frozen == null) return;
        if (nodes == null) return;
        if (nodes.TryGetValue(id, out var node)) { value = node; return; }
        if (staticSpineNodeSourceIdsByComponent.TryGetValue(id, out var nodeId) && nodes.TryGetValue(nodeId, out node))
        {
            var identities = node.GetComponents<UnitySpineSourceIdentity>()
                .Where(marker => marker != null && marker.sourceComponentId == id).ToArray();
            if (identities.Length == 1 && !identities[0].enabled && identities[0].renderer != null &&
                identities[0].renderer.gameObject == node && identities[0].rendererKind == identities[0].renderer.GetType().FullName)
                value = identities[0].renderer;
            return;
        }
        var asset = frozen.dataAssets.SingleOrDefault(row => row.sourceAssetId == id);
        if (asset != null)
        {
            var exact = AssetDatabase.LoadAssetAtPath<SkeletonDataAsset>(asset.skeletonDataAssetPath);
            if (exact != null) value = exact;
        }
    }

    static partial void ReadSavedStaticSpine(Dictionary<string, GameObject> nodes, string prefabId)
    {
        if (String.IsNullOrWhiteSpace(prefabId)) return;
        var frozen = LoadFrozenStaticSpinePlan();
        if (frozen == null) return;
        var prefab = frozen.components.Where(row => row.sourcePrefabId == prefabId).ToArray();
        if (prefab.Length == 0) return;
        if (nodes == null) throw new InvalidOperationException("SPINE_SAVED_NODE_MAP_MISSING:" + prefabId);

        var plan = JsonUtility.FromJson<Plan>(File.ReadAllText(Paths.plan));
        var sourcePrefab = (plan.sourcePrefabs ?? Array.Empty<SourcePrefabSpec>()).SingleOrDefault(row => row.sourceId == prefabId);
        if (sourcePrefab == null) throw new InvalidOperationException("SPINE_SAVED_SOURCE_PREFAB_MISSING:" + prefabId);
        var nodeSpecs = (plan.nodes ?? Array.Empty<NodeSpec>()).ToDictionary(row => row.sourceId, StringComparer.Ordinal);
        var savedComponents = new Dictionary<string, Component>(StringComparer.Ordinal);
        var visualIdentities = new Dictionary<string, StaticSpineVisualIdentity>(StringComparer.Ordinal);
        var failures = new List<string>();

        foreach (var group in prefab.GroupBy(row => ResolveSpineNodeId(sourcePrefab, row.sourceNodeId), StringComparer.Ordinal))
        {
            if (group.Key == null || !nodes.TryGetValue(group.Key, out var node) || node == null)
            { failures.Add("saved_source_node_missing:" + group.Key); continue; }
            foreach (var row in group)
            {
                var identities = node.GetComponents<UnitySpineSourceIdentity>()
                    .Where(marker => marker != null && marker.sourceComponentId == row.sourceComponentId).ToArray();
            if (identities.Length != 1 || identities[0].enabled || identities[0].renderer == null ||
                    identities[0].renderer.gameObject != node ||
                    identities[0].rendererKind != identities[0].renderer.GetType().FullName ||
                !identities[0].persistentVisiblePose || !identities[0].sourceTimeScaleVerified ||
                Mathf.Abs(identities[0].sourceTimeScale - (float)row.sourceTimeScale) > 0.000001f ||
                Mathf.Abs(identities[0].nativeTimeScale) > 0.000001f ||
                !((Behaviour)identities[0].renderer).enabled || Mathf.Abs(ReadSpineTimeScale(identities[0].renderer)) > 0.000001f ||
                    identities[0].renderer.GetType() != typeof(SkeletonGraphic) &&
                    identities[0].renderer.GetType() != typeof(SkeletonAnimation))
                { failures.Add("saved_source_component_identity_mismatch:" + row.sourceComponentId); continue; }
                savedComponents.Add(row.sourceComponentId, identities[0].renderer);
                var sourceNodeSpec = nodeSpecs.TryGetValue(group.Key, out var exactNodeSpec) ? exactNodeSpec : null;
                var sourceColor = new float[0];
                var nativeColor = new float[0];
                var sourceColorVerified = false;
                var nativeColorVerified = false;
                if (identities[0].renderer.GetType() == typeof(SkeletonGraphic))
                {
                    if (sourceNodeSpec == null)
                    { failures.Add("saved_spine_graphic_source_node_missing:" + row.sourceComponentId); }
                    else
                    {
                        SourceSpineNodeColor(sourceNodeSpec, row.sourceComponentId);
                        sourceColor = sourceNodeSpec.color.ToArray();
                        var graphic = (SkeletonGraphic)identities[0].renderer;
                        nativeColor = SpineGraphicColorChannels(graphic);
                        sourceColorVerified = true;
                        nativeColorVerified = SpineGraphicColorMatches(graphic, sourceNodeSpec, row.sourceComponentId);
                        if (!nativeColorVerified) failures.Add("saved_spine_graphic_color_mismatch:" + row.sourceComponentId);
                    }
                }
                visualIdentities.Add(row.sourceComponentId, new StaticSpineVisualIdentity {
                    sourceComponentId = row.sourceComponentId,
                    rendererKind = identities[0].rendererKind,
                    sourceTimeScale = identities[0].sourceTimeScale,
                    nativeTimeScale = ReadSpineTimeScale(identities[0].renderer),
                    sourceTimeScaleVerified = identities[0].sourceTimeScaleVerified,
                    rendererEnabled = ((Behaviour)identities[0].renderer).enabled,
                    persistentVisiblePose = identities[0].persistentVisiblePose,
                    sourceColor = sourceColor,
                    nativeColor = nativeColor,
                    sourceColorVerified = sourceColorVerified,
                    nativeColorVerified = nativeColorVerified,
                });
            }
        }

        var saved = UnitySpineNativeStage.ReadSaved(frozen,
            sourceId => savedComponents.TryGetValue(sourceId, out var component) ? component : null, prefabId);
        var expected = prefab.ToDictionary(row => row.sourceComponentId, StringComparer.Ordinal);
        var actual = saved.components.ToDictionary(row => row.sourceComponentId, StringComparer.Ordinal);
        if (actual.Count != expected.Count || expected.Keys.Any(id => !actual.ContainsKey(id)))
            failures.Add("saved_component_denominator_mismatch");
        foreach (var pair in actual)
        {
            var row = expected[pair.Key]; var readback = pair.Value;
            if (!readback.componentTypeVerified || !readback.dataReferenceVerified || !readback.fieldsVerified || !readback.enabled)
                failures.Add("saved_native_component_identity_or_fields_mismatch:" + pair.Key);
            if (row.sourceHasStaticDataReference && (!readback.staticDataBound || !readback.dataAssetContentVerified))
                failures.Add("saved_native_data_asset_binding_mismatch:" + pair.Key);
            if (!row.sourceHasStaticDataReference && !readback.sourceDataUnbound)
                failures.Add("saved_source_unbound_component_not_preserved:" + pair.Key);
        }
        var expectedAssetIds = new HashSet<string>(prefab.Where(row => row.sourceHasStaticDataReference &&
            !String.IsNullOrEmpty(row.sourceDataAssetId)).Select(row => row.sourceDataAssetId), StringComparer.Ordinal);
        var actualAssets = saved.dataAssets.ToDictionary(row => row.sourceAssetId, StringComparer.Ordinal);
        if (actualAssets.Count != expectedAssetIds.Count || expectedAssetIds.Any(id => !actualAssets.ContainsKey(id)))
            failures.Add("saved_data_asset_denominator_mismatch");
        foreach (var pair in actualAssets)
        {
            var asset = pair.Value;
            if (!asset.nativeAssetIdentityVerified || !asset.savedSourceReferencesVerified || !asset.scaleVerified ||
                !asset.sourceProfileMaterialsVerified || !asset.staticDataVerified || Mathf.Abs(asset.scale - 1f) > 0.000001f)
                failures.Add("saved_native_data_asset_identity_scale_or_material_profile_mismatch:" + pair.Key);
        }
        if (saved.gaps.Any(gap => gap.code.Contains("READBACK_FAILED") || gap.code.Contains("IDENTITY_MISMATCH")))
            failures.AddRange(saved.gaps.Select(gap => gap.code + ":" + gap.sourceId + ":" + gap.message));

        Directory.CreateDirectory(StaticSpineReadbackRoot);
        var destination = Path.Combine(StaticSpineReadbackRoot, AssetDatabase.AssetPathToGUID(sourcePrefab.path) + ".json");
        var result = new StaticSpineSavedReadback {
            sourcePrefabId = prefabId,
            sourceManifestSha256 = frozen.sourceManifestSha256,
            normalizedIrSha256 = frozen.normalizedIrSha256,
            visualPolicy = frozen.visualPolicy,
            staticNativeVerified = failures.Count == 0,
            dynamicBehaviorComplete = false,
            componentCount = saved.components.Count,
            dataAssetCount = saved.dataAssets.Count,
            components = saved.components.ToArray(), dataAssets = saved.dataAssets.ToArray(),
            visualComponents = visualIdentities.Values.OrderBy(row => row.sourceComponentId, StringComparer.Ordinal).ToArray(),
            stageGaps = saved.gaps.ToArray(), failures = failures.ToArray(),
        };
        File.WriteAllText(destination, JsonUtility.ToJson(result, true));
        if (failures.Count != 0)
            throw new InvalidOperationException("SPINE_SAVED_READBACK_FAILED:" + prefabId + ":" + String.Join(",", failures));
    }

    static string ResolveSpineNodeId(SourcePrefabSpec prefab, string sourceNodeId)
    {
        if (prefab == null || String.IsNullOrWhiteSpace(sourceNodeId)) return null;
        var candidate = sourceNodeId.StartsWith(prefab.sourceId + "#", StringComparison.Ordinal)
            ? sourceNodeId
            : sourceNodeId.All(Char.IsDigit) ? prefab.sourceId + "#" + sourceNodeId : sourceNodeId;
        return (prefab.nodes ?? Array.Empty<string>()).Contains(candidate, StringComparer.Ordinal) ? candidate : null;
    }

    static float ReadSpineTimeScale(Component component)
    {
        if (component != null && component.GetType() == typeof(SkeletonGraphic)) return ((SkeletonGraphic)component).timeScale;
        if (component != null && component.GetType() == typeof(SkeletonAnimation)) return ((SkeletonAnimation)component).timeScale;
        return Single.NaN;
    }

    static Color SourceSpineNodeColor(NodeSpec source, string sourceComponentId)
    {
        var channels = source == null ? null : source.color;
        if (channels == null || channels.Length != 4 || channels.Any(value => Single.IsNaN(value) || Single.IsInfinity(value) || value < 0f || value > 255f))
            throw new InvalidOperationException("SPINE_SOURCE_NODE_RGBA_INVALID:" + sourceComponentId);
        // NodeSpec.color stores source RGBA channels as bytes. CanvasGroup
        // opacity is emitted separately by the primary importer.
        return new Color(channels[0] / 255f, channels[1] / 255f, channels[2] / 255f, channels[3] / 255f);
    }

    static float[] SpineGraphicColorChannels(SkeletonGraphic graphic)
    {
        var color = graphic.color;
        return new[] { color.r * 255f, color.g * 255f, color.b * 255f, color.a * 255f };
    }

    static bool SpineGraphicColorMatches(SkeletonGraphic graphic, NodeSpec source, string sourceComponentId)
    {
        SourceSpineNodeColor(source, sourceComponentId);
        var actual = SpineGraphicColorChannels(graphic);
        return Enumerable.Range(0, 4).All(index => Math.Abs(actual[index] - source.color[index]) <= 0.001f);
    }
}
