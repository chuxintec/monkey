'use strict';

// Independent adapter for Creator's native sp.Skeleton component. The main
// prefab importer owns component construction and must call this after mapping
// each sourceComponentId to the created component and each source asset ID to
// a loaded sp.SkeletonData instance.
function explicitField(fields, name, target) {
    const row = fields && fields[name] && fields[name][target];
    return row && (row.status === 'explicit' || row.status === 'resolved_source_engine_default') && typeof row.member === 'string'
        ? { member: row.member, value: row.value }
        : null;
}

function assign(component, row) {
    if (!row) return;
    if (!(row.member in component)) throw new Error('Missing Creator Spine member: ' + row.member);
    component[row.member] = row.value;
}

function applyCreatorSpineBinding(binding, resolveComponent, resolveSkeletonData) {
    if (!binding || !binding.sourceComponentId || !binding.creator || !binding.creator.fields)
        throw new Error('Invalid source-exact Spine component binding');
    const component = resolveComponent(binding.sourceComponentId);
    if (!component) throw new Error('No native component for source ID: ' + binding.sourceComponentId);

    const data = binding.creator.fields.skeletonData;
    if (data && data.sourceAssetId) {
        const asset = resolveSkeletonData(data.sourceAssetId);
        if (!asset) throw new Error('No exact Creator SkeletonData for source asset: ' + data.sourceAssetId);
        component.skeletonData = asset;
    }
    // An absent source UUID intentionally leaves skeletonData untouched. This
    // preserves room for source code to assign it later without inventing one.
    const fields = binding.creator.fields;
    for (const name of ['skin', 'animation', 'loop', 'timeScale', 'premultipliedAlpha',
        'tint', 'debugSlots', 'debugBones', 'debugMesh', 'enableBatch', 'caching'])
        assign(component, explicitField(fields, name, 'creator'));

    return {
        sourceComponentId: binding.sourceComponentId,
        staticDataBound: !!(data && data.sourceAssetId),
        unresolvedDynamicAssignment: !(data && data.sourceAssetId),
        appliedFields: ['skin', 'animation', 'loop', 'timeScale', 'premultipliedAlpha',
            'tint', 'debugSlots', 'debugBones', 'debugMesh', 'enableBatch', 'caching']
            .filter(name => !!explicitField(fields, name, 'creator')),
        sourceCallbacksExecuted: false,
    };
}

function applyCreatorSpineBindings(bindings, resolvers) {
    if (!Array.isArray(bindings) || !resolvers || typeof resolvers.resolveComponent !== 'function' ||
        typeof resolvers.resolveSkeletonData !== 'function')
        throw new Error('Creator Spine binding resolvers are required');
    return bindings.map(binding => applyCreatorSpineBinding(
        binding, resolvers.resolveComponent, resolvers.resolveSkeletonData));
}

function readCreatorSpineBinding(binding, resolveComponent) {
    if (!binding || !binding.sourceComponentId || !binding.creator || !binding.creator.fields)
        throw new Error('Invalid source-exact Spine component binding');
    const resolved = resolveComponent(binding.sourceComponentId);
    const component = Array.isArray(resolved)
        ? (resolved.length === 1 ? resolved[0] : null)
        : resolved;
    if (!component) throw new Error('Expected exactly one saved native sp.Skeleton for source ID: ' + binding.sourceComponentId);

    const fields = binding.creator.fields;
    const sourceData = fields.skeletonData || {};
    const hasStaticSourceData = typeof sourceData.sourceAssetId === 'string' && sourceData.sourceAssetId.length > 0;
    const expectedData = sourceData.creator && sourceData.creator.nativeUuid;
    const skeletonData = component.skeletonData || null;
    const actualDataUuid = skeletonData && skeletonData.uuid || null;
    const runtimeData = skeletonData && typeof skeletonData.getRuntimeData === 'function'
        ? skeletonData.getRuntimeData(true)
        : null;
    const requestedAnimationRow = explicitField(fields, 'animation', 'creator');
    const requestedSkinRow = explicitField(fields, 'skin', 'creator');
    const requestedAnimation = requestedAnimationRow && requestedAnimationRow.value ? requestedAnimationRow.value : null;
    const requestedSkin = requestedSkinRow && requestedSkinRow.value ? requestedSkinRow.value : null;
    const animations = runtimeData && Array.isArray(runtimeData.animations) ? runtimeData.animations : [];
    const skins = runtimeData && Array.isArray(runtimeData.skins) ? runtimeData.skins : [];
    const animationExists = requestedAnimation === null || !hasStaticSourceData || !runtimeData ? null
        : (typeof component.findAnimation === 'function'
            ? !!component.findAnimation(requestedAnimation)
            : animations.some(row => row && row.name === requestedAnimation));
    const skinExists = requestedSkin === null || !hasStaticSourceData || !runtimeData ? null
        : skins.some(row => row && row.name === requestedSkin);
    const isCached = typeof component.isAnimationCached === 'function' && component.isAnimationCached();
    const currentEntry = !isCached && typeof component.getCurrent === 'function' ? component.getCurrent(0) : null;
    const actualAnimation = isCached
        ? (component._animationName || null)
        : (currentEntry && currentEntry.animation && currentEntry.animation.name) || component.animation || null;
    const actualSkin = (component._skeleton && component._skeleton.skin && component._skeleton.skin.name)
        || component._skinName || null;

    const actual = {
        nativeComponentUuid: component.uuid || null,
        skeletonDataUuid: actualDataUuid,
        defaultSkin: component.defaultSkin,
        currentSkin: actualSkin,
        defaultAnimation: component.defaultAnimation,
        currentAnimation: actualAnimation,
        loop: component.loop,
        timeScale: component.timeScale,
        premultipliedAlpha: component.premultipliedAlpha,
        useTint: component.useTint,
        debugBones: component.debugBones,
        debugSlots: component.debugSlots,
        debugMesh: component.debugMesh,
        enableBatch: component.enableBatch,
        defaultCacheMode: typeof component.defaultCacheMode === 'number' ? component.defaultCacheMode : null,
        runtimeAnimationNames: animations.map(row => row && row.name).filter(name => typeof name === 'string'),
        runtimeSkinNames: skins.map(row => row && row.name).filter(name => typeof name === 'string'),
    };
    const checks = {
        exactSkeletonDataUuid: hasStaticSourceData ? !!expectedData && actualDataUuid === expectedData : null,
        requestedAnimationExists: requestedAnimation === null ? null : animationExists,
        requestedSkinExists: requestedSkin === null ? null : skinExists,
        requestedAnimationActive: requestedAnimation === null || !runtimeData ? null : actualAnimation === requestedAnimation,
        requestedSkinActive: requestedSkin === null || !runtimeData ? null : actualSkin === requestedSkin,
    };
    for (const key of ['skin', 'animation', 'loop', 'timeScale', 'premultipliedAlpha',
        'tint', 'debugSlots', 'debugBones', 'debugMesh', 'enableBatch', 'caching']) {
        const row = explicitField(fields, key, 'creator');
        if (!row) continue;
        const actualValue = key === 'skin' ? actual.defaultSkin
            : key === 'animation' ? actual.defaultAnimation
                : key === 'caching' ? actual.defaultCacheMode
                    : key === 'tint' ? actual.useTint : actual[key];
        checks[key + 'FieldMatchesSource'] = Object.is(actualValue, row.value);
    }
    const failures = Object.entries(checks).filter(([, value]) => value === false).map(([name]) => name);
    return {
        sourceComponentId: binding.sourceComponentId,
        nativeComponentType: component.constructor && component.constructor.name || 'sp.Skeleton',
        status: !hasStaticSourceData ? 'incomplete_dynamic_assignment'
            : !runtimeData ? 'incomplete_runtime_data'
                : failures.length ? 'mismatch' : 'verified',
        staticDataBoundBySource: hasStaticSourceData,
        expectedTargetDataUuidAvailable: !!expectedData,
        runtimeDataAvailable: !!runtimeData,
        dynamicAssignmentUnverified: !hasStaticSourceData,
        observedDataWithoutStaticSourceReference: !hasStaticSourceData && !!actualDataUuid,
        requestedAnimation,
        requestedSkin,
        actual,
        checks,
        failures,
        sourceCodeExecuted: false,
    };
}

// Read-only data catalog helper for Creator's isolated SkeletonData resource
// probe. The primary importer can use this in its Spine resource readback to
// publish the complete native name lists without selecting an animation.
function readCreatorSpineDataCatalog(sourceId, skeletonData, expected) {
    if (!sourceId || !skeletonData) throw new Error('Source ID and loaded sp.SkeletonData are required');
    const runtimeData = typeof skeletonData.getRuntimeData === 'function'
        ? skeletonData.getRuntimeData(true)
        : null;
    if (!runtimeData) {
        return { sourceId, status: 'runtime_data_unavailable', uuid: skeletonData.uuid || null,
            animationNames: [], skinNames: [], diagnostics: ['getRuntimeData(true) returned no SkeletonData'] };
    }
    const animationNames = Array.isArray(runtimeData.animations)
        ? runtimeData.animations.map(row => row && row.name).filter(name => typeof name === 'string')
        : [];
    const skinNames = Array.isArray(runtimeData.skins)
        ? runtimeData.skins.map(row => row && row.name).filter(name => typeof name === 'string')
        : [];
    const diagnostics = [];
    if (expected && expected.nativeUuid && skeletonData.uuid !== expected.nativeUuid)
        diagnostics.push('SkeletonData UUID differs from expected native readback UUID');
    if (expected && expected.animationName && !animationNames.includes(expected.animationName))
        diagnostics.push('Requested animation name is absent from SkeletonData runtime data');
    if (expected && expected.skinName && !skinNames.includes(expected.skinName))
        diagnostics.push('Requested skin name is absent from SkeletonData runtime data');
    return {
        sourceId,
        status: diagnostics.length ? 'mismatch' : 'verified',
        uuid: skeletonData.uuid || null,
        animationNames,
        skinNames,
        boneCount: Array.isArray(runtimeData.bones) ? runtimeData.bones.length : null,
        slotCount: Array.isArray(runtimeData.slots) ? runtimeData.slots.length : null,
        sourceCodeExecuted: false,
        diagnostics,
    };
}

function readCreatorSpineBindings(bindings, resolveComponent) {
    if (!Array.isArray(bindings) || typeof resolveComponent !== 'function')
        throw new Error('Creator Spine readback requires bindings and an exact component resolver');
    return bindings.map(binding => readCreatorSpineBinding(binding, resolveComponent));
}

module.exports = {
    applyCreatorSpineBinding,
    applyCreatorSpineBindings,
    readCreatorSpineBinding,
    readCreatorSpineBindings,
    readCreatorSpineDataCatalog,
};
