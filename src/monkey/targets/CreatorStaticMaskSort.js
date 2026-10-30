'use strict';

const cc = require('cc');
function resolveSprite(plan, assets, uuid) {
    const ids=(plan.assets||[]).filter(a=>a.kind==='sprite'&&a.sourceId.endsWith(':'+uuid));
    if(ids.length!==1||!assets.has(ids[0].sourceId))throw Error('STATIC_MASK_FRAME_IDENTITY_AMBIGUOUS:'+uuid);
    const asset=assets.get(ids[0].sourceId);
    if(!(asset instanceof cc.SpriteFrame))throw Error('STATIC_MASK_FRAME_NATIVE_TYPE_DIFFERS:'+uuid);
    return asset;
}

function createStaticMasks(specs, nodes, resolveSprite) {
    if (!Array.isArray(specs)) throw Error('STATIC_MASK_PLAN_INVALID');
    const rows = [];
    for (const spec of specs) {
        if (!spec || !spec.sourceFields || typeof spec.sourceFields !== 'object' || Array.isArray(spec.sourceFields))
            throw Error('STATIC_MASK_SOURCE_FIELDS_MISSING');
        const sourceFieldsJson = typeof spec.sourceFieldsJson === 'string' ? spec.sourceFieldsJson : JSON.stringify(spec.sourceFields);
        if (typeof sourceFieldsJson !== 'string') throw Error('STATIC_MASK_SOURCE_FIELDS_JSON_INVALID: ' + spec.sourceId);
        const node = nodes.get(spec.node);
        if (!node) throw Error('STATIC_MASK_NODE_MISSING: ' + spec.sourceId);
        let sprite = null;
        let spriteFrame = null;
        if (spec.maskType === 2) {
            spriteFrame = resolveSprite && resolveSprite(spec.spriteFrameUuid);
            if (!spriteFrame) throw Error('STATIC_MASK_SPRITE_FRAME_MISSING: ' + spec.sourceId);
            // A source image Mask owns a native Sprite backing even when the
            // source node has no standalone Sprite component. Create it before
            // assigning a frame so CUSTOM sizing applies to the first assignment.
            sprite = node.getComponent(cc.Sprite) || node.addComponent(cc.Sprite);
            if (!(sprite instanceof cc.Sprite)) throw Error('STATIC_MASK_NATIVE_SPRITE_MISSING: ' + spec.sourceId);
            if (!cc.Sprite.SizeMode || cc.Sprite.SizeMode.CUSTOM === undefined)
                throw Error('STATIC_MASK_SPRITE_CUSTOM_SIZE_MODE_UNAVAILABLE: ' + spec.sourceId);
            // Mask.type creates its renderer from the existing Sprite. Set the
            // persisted Sprite's size mode before assigning its frame so Creator
            // cannot resize source UITransform from the frame's trimmed rect.
            sprite.sizeMode = cc.Sprite.SizeMode.CUSTOM;
        }
        if (node.getComponent(cc.Mask)) throw Error('STATIC_MASK_ALREADY_EXISTS: ' + spec.sourceId);
        const mask = node.addComponent(cc.Mask);
        if (!(mask instanceof cc.Mask)) throw Error('STATIC_MASK_CREATE_FAILED: ' + spec.sourceId);
        const type = spec.maskType === 0 ? cc.Mask.Type.GRAPHICS_RECT :
            spec.maskType === 1 ? cc.Mask.Type.GRAPHICS_ELLIPSE :
            spec.maskType === 2 ? cc.Mask.Type.SPRITE_STENCIL : null;
        if (type === null) throw Error('STATIC_MASK_TYPE_UNSUPPORTED: ' + spec.sourceId);
        mask.type = type;
        // Creator creates its stencil renderer in Mask.onLoad/onEnable. A
        // newly-added component on an inactive prefab node has not reached
        // that lifecycle yet; initialize the same native backing explicitly
        // before setters such as inverted access subComp.
        if (!mask.subComp && typeof mask.onLoad === 'function') mask.onLoad();
        if (!mask.subComp) throw Error('STATIC_MASK_NATIVE_BACKING_MISSING: ' + spec.sourceId);
        if (spec.maskType === 2) {
            if (mask.subComp !== sprite) throw Error('STATIC_MASK_NATIVE_SPRITE_BACKING_MISMATCH: ' + spec.sourceId);
            sprite.spriteFrame = spriteFrame;
        }
        mask.inverted = spec.inverted;
        mask.alphaThreshold = spec.alphaThreshold;
        mask.enabled = spec.enabled;
        const IdentityType = cc.js && cc.js.getClassByName && cc.js.getClassByName('MonkeyStaticMaskIdentity');
        if (!IdentityType) throw Error('STATIC_MASK_IDENTITY_TYPE_MISSING: ' + spec.sourceId);
        const identity = node.addComponent(IdentityType);
        if (!(identity instanceof IdentityType)) throw Error('STATIC_MASK_IDENTITY_CREATE_FAILED: ' + spec.sourceId);
        identity.sourceId = spec.sourceId;
        identity.nativeId = spec.nativeId;
        identity.sourceMaskType = spec.maskType;
        identity.sourceInverted = spec.inverted;
        identity.sourceAlphaThreshold = spec.alphaThreshold;
        identity.sourceFieldsJson = sourceFieldsJson;
        identity.sourceSpriteFrameUuid = spec.spriteFrameUuid || '';
        identity.sourceSpriteFrame = spec.maskType === 2 ? mask.spriteFrame : null;
        identity.nativeMask = mask;
        identity.enabled = false;
        rows.push(readStaticMasks([spec], nodes, resolveSprite, {initialized: true})[0]);
    }
    return rows;
}

function readStaticMasks(specs, nodes, resolveSprite, options = {}) {
    const initialized = options === true || (options && options.initialized === true);
    return specs.map(spec => {
        const node = nodes.get(spec.node);
        const components = node && node.getComponents(cc.Mask);
        if (!components || components.length !== 1)
            throw Error('STATIC_MASK_NATIVE_COMPONENT_COUNT_MISMATCH: ' + spec.sourceId);
        const mask = components[0];
        const IdentityType = cc.js && cc.js.getClassByName && cc.js.getClassByName('MonkeyStaticMaskIdentity');
        const identities = node && IdentityType ? node.getComponents(IdentityType) : [];
        if (!IdentityType || !identities || identities.length !== 1)
            throw Error('STATIC_MASK_IDENTITY_COMPONENT_COUNT_MISMATCH: ' + spec.sourceId);
        const identity = identities[0];
        const expectedType = spec.maskType === 0 ? cc.Mask.Type.GRAPHICS_RECT :
            spec.maskType === 1 ? cc.Mask.Type.GRAPHICS_ELLIPSE : cc.Mask.Type.SPRITE_STENCIL;
        const expectedSpriteFrame = spec.maskType === 2 && resolveSprite ? resolveSprite(spec.spriteFrameUuid) : null;
        const sprite = spec.maskType === 2 ? node.getComponent(cc.Sprite) : null;
        const nativeSpriteFrame = sprite ? sprite.spriteFrame : null;
        const spriteOK = spec.maskType !== 2 || (sprite && expectedSpriteFrame &&
            nativeSpriteFrame === expectedSpriteFrame && identity.sourceSpriteFrame === expectedSpriteFrame);
        const initializedBackingOK = !initialized || spec.maskType !== 2 || (mask.subComp === sprite && mask.spriteFrame === nativeSpriteFrame);
        const dependencyOK = spec.maskType === 2 ? !!node.getComponent(cc.Sprite) :
            !!node.getComponent(cc.Graphics) && !node.getComponent(cc.Sprite);
        const sourceFieldsJson = typeof spec.sourceFieldsJson === 'string' ? spec.sourceFieldsJson : JSON.stringify(spec.sourceFields);
        let sourceFields = null;
        try { sourceFields = JSON.parse(identity.sourceFieldsJson); } catch (_) { /* validation below fails closed */ }
        const identityOK = identity.enabled === false && identity.sourceId === spec.sourceId &&
            identity.nativeMask === mask &&
            identity.nativeId === spec.nativeId && identity.sourceMaskType === spec.maskType &&
            identity.sourceInverted === spec.inverted && identity.sourceAlphaThreshold === spec.alphaThreshold &&
            identity.sourceFieldsJson === sourceFieldsJson && identity.sourceSpriteFrameUuid === (spec.spriteFrameUuid || '') &&
            (spec.maskType === 2 ? identity.sourceSpriteFrame === expectedSpriteFrame : identity.sourceSpriteFrame === null) &&
            initializedBackingOK;
        const verified = mask.node === node && mask.type === expectedType && mask.enabled === spec.enabled &&
            mask.inverted === spec.inverted && mask.alphaThreshold === spec.alphaThreshold && spriteOK && dependencyOK &&
            identityOK && !!sourceFields && typeof mask.uuid === 'string' && mask.uuid.length > 0;
        const nativeSpriteFrameUuid = spec.maskType === 2 && nativeSpriteFrame ?
            (nativeSpriteFrame._uuid || nativeSpriteFrame.uuid || null) : null;
        return {sourceId: spec.sourceId, node: spec.node, nativeType: mask.constructor.name,
            componentUuid: mask.uuid, enabled: mask.enabled, maskType: spec.maskType,
            nativeMaskType: mask.type, inverted: mask.inverted, alphaThreshold: mask.alphaThreshold,
            sourceSpriteFrameUuid: spec.maskType === 2 ? spec.spriteFrameUuid : null,
            nativeSpriteFrameUuid, maskSpriteFrameUuid: initialized && mask.spriteFrame ?
                (mask.spriteFrame._uuid || mask.spriteFrame.uuid || null) : null,
            initialized, initializedBackingVerified: initialized ? !!initializedBackingOK : null,
            sourceFieldsJson: identity.sourceFieldsJson,
            sourceFields, identitySourceId: identity.sourceId, identityNativeId: identity.nativeId,
            verified: !!verified};
    });
}

function createStaticSort(sortOrders, sortRoots, sortGroups, nodes) {
    if (!Array.isArray(sortOrders) || !Array.isArray(sortRoots) || !Array.isArray(sortGroups)) throw Error('STATIC_SORT_PLAN_INVALID');
    return readStaticSort(sortOrders, sortRoots, sortGroups, nodes);
}

function readStaticSort(sortOrders, sortRoots, sortGroups, nodes) {
    const groupByParent = new Map(sortGroups.map(group => [group.parent, group]));
    const nodeIdByNode = new Map(Array.from(nodes.entries(), ([id, node]) => [node, id]));
    const orders = sortOrders.map(spec => {
        const node = nodes.get(spec.node);
        const group = node && groupByParent.get(nodeIdByNode.get(node.parent));
        return {sourceId: spec.sourceId, node: spec.node, nativeType: null, sortOrder: spec.sortOrder,
            enabled: spec.enabled, siblingIndex: node && node.getSiblingIndex(),
            sourceGroupRepresentable: !!group && group.representableBySiblingOrder,
            sourceQueueMapped: false, diagnostic: 'STATIC_SORT_GLOBAL_QUEUE_ADAPTER_REQUIRED', verified: false};
    });
    const roots = sortRoots.map(spec => {
        const node = nodes.get(spec.node);
        return {sourceId: spec.sourceId, node: spec.node, nativeType: null, enabled: spec.enabled,
            childCount: node ? node.children.length : -1,
            sourceQueueMapped: false, diagnostic: 'STATIC_SORT_GLOBAL_QUEUE_ADAPTER_REQUIRED', verified: false};
    });
    return {sortOrders: orders, sortRoots: roots};
}

module.exports = {createStaticMasks, readStaticMasks, createStaticSort, readStaticSort,resolveSprite};
