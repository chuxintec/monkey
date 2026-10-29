'use strict';
// Source-order marker and disabled cc.Animation binding for static native previews.
// The adapter never calls play(), sample(), or updates animation time.
const cc = require('cc');

const NativeStaticAnimationBinding = cc.Class({
    name: 'MonkeyNativeStaticAnimationBinding',
    extends: cc.Component,
    properties: {
        sourceComponentId: { default: '' },
        sourceNodeId: { default: '' },
        sourceEnabled: { default: false },
        sourceEnabledKnown: { default: false },
        sourcePlayOnLoad: { default: false },
        sourcePlayOnLoadKnown: { default: false },
        sourceDefaultClipId: { default: '' },
        sourceDefaultClipKnown: { default: false },
        hasSourceDefaultClip: { default: false },
        sourceClipOrderJson: { default: '[]' },
        clipBindingsJson: { default: '[]' },
        nativeClips: { default: [], type: [cc.AnimationClip] },
        nativeDefaultClip: { default: null, type: cc.AnimationClip },
    },
});

function attach(node, spec, resolveClip) {
    if (!node || !spec || spec.schema !== 'monkey-static-animation-bindings/1'
        || typeof resolveClip !== 'function') throw new Error('STATIC_ANIMATION_BINDING_INPUT_INVALID');
    let animation = node.getComponent(cc.Animation);
    if (!animation) animation = node.addComponent(cc.Animation);
    let marker = node.getComponent(NativeStaticAnimationBinding);
    if (!marker) marker = node.addComponent(NativeStaticAnimationBinding);

    const rows = [...(spec.clips || [])].sort((a, b) => a.order - b.order);
    const resolved = rows.map(row => ({ row, clip: row.status === 'native_clip_reference_resolved'
        ? resolveClip(row.nativeClipPath, row.nativeClipGuid, row.assetSha256) : null }));
    for (const pair of resolved) {
        if (pair.row.status === 'native_clip_reference_resolved' && !pair.clip)
            throw new Error(`STATIC_ANIMATION_CLIP_REFERENCE_MISSING:${pair.row.sourceClipId}`);
    }
    const sourceDefault = spec.hasSourceDefaultClip
        ? resolved.find(pair => pair.row.sourceClipId === spec.sourceDefaultClipId) : null;
    const defaultClip = sourceDefault && sourceDefault.clip ? sourceDefault.clip : null;

    // Preserve exact original ordering/status in a serializable marker, including
    // unavailable source clips. Standard cc.Animation receives the resolved assets
    // in that same relative order and remains disabled.
    animation.clips = resolved.filter(pair => pair.clip).map(pair => pair.clip);
    animation.defaultClip = defaultClip;
    animation.playOnLoad = !!spec.sourcePlayOnLoad;
    animation.enabled = false;
    marker.sourceComponentId = spec.sourceComponentId || '';
    marker.sourceNodeId = spec.sourceNodeId || '';
    marker.sourceEnabled = !!spec.sourceEnabled;
    marker.sourceEnabledKnown = !!spec.sourceEnabledKnown;
    marker.sourcePlayOnLoad = !!spec.sourcePlayOnLoad;
    marker.sourcePlayOnLoadKnown = !!spec.sourcePlayOnLoadKnown;
    marker.sourceDefaultClipId = spec.sourceDefaultClipId || '';
    marker.sourceDefaultClipKnown = !!spec.sourceDefaultClipKnown;
    marker.hasSourceDefaultClip = !!spec.hasSourceDefaultClip;
    marker.sourceClipOrderJson = JSON.stringify(spec.sourceClipOrder || []);
    marker.clipBindingsJson = JSON.stringify(rows.map(row => ({
        order: row.order,
        sourceClipId: row.sourceClipId,
        planAnimationId: row.planAnimationId,
        path: row.nativeClipPath || null,
        guid: row.nativeClipGuid || null,
        assetSha256: row.assetSha256 || null,
        status: row.status,
    })));
    marker.nativeClips = resolved.filter(pair => pair.clip).map(pair => pair.clip);
    marker.nativeDefaultClip = defaultClip;
    marker.enabled = false;

    return read(node, spec);
}

function read(node, spec) {
    if (!node || !spec) throw new Error('STATIC_ANIMATION_BINDING_INPUT_INVALID');
    const animation = node.getComponent(cc.Animation);
    const marker = node.getComponent(NativeStaticAnimationBinding);
    if (!animation || !marker) return { status: 'partial', diagnostics: ['native components missing'] };
    const rows = JSON.parse(marker.clipBindingsJson || '[]');
    const clips = [...(animation.clips || [])];
    const clipRefsMatch = rows.filter(row => row.status === 'native_clip_reference_resolved').length === clips.length
        && clips.every((clip, index) => marker.nativeClips[index] === clip);
    const fieldsMatch = marker.sourceComponentId === spec.sourceComponentId
        && marker.sourceNodeId === spec.sourceNodeId
        && marker.sourceEnabled === !!spec.sourceEnabled
        && marker.sourceEnabledKnown === !!spec.sourceEnabledKnown
        && marker.sourcePlayOnLoad === !!spec.sourcePlayOnLoad
        && marker.sourcePlayOnLoadKnown === !!spec.sourcePlayOnLoadKnown
        && marker.sourceDefaultClipId === (spec.sourceDefaultClipId || '')
        && marker.sourceDefaultClipKnown === !!spec.sourceDefaultClipKnown
        && marker.hasSourceDefaultClip === !!spec.hasSourceDefaultClip
        && marker.sourceClipOrderJson === JSON.stringify(spec.sourceClipOrder || [])
        && animation.enabled === false && marker.enabled === false
        && animation.defaultClip === marker.nativeDefaultClip;
    const matches = fieldsMatch && clipRefsMatch;
    return {
        status: matches ? (spec.status === 'resolved' ? 'reference_fields_verified' : 'partial') : 'mismatch',
        sourceComponentId: marker.sourceComponentId,
        sourceNodeId: marker.sourceNodeId,
        sourceEnabled: marker.sourceEnabled,
        sourcePlayOnLoad: marker.sourcePlayOnLoad,
        sourceDefaultClipId: marker.sourceDefaultClipId,
        sourceClipOrder: JSON.parse(marker.sourceClipOrderJson || '[]'),
        clipBindings: rows,
        nativeClipCount: clips.length,
        animationDisabled: !animation.enabled,
        markerDisabled: !marker.enabled,
        playbackExecuted: false,
        diagnostics: matches ? [] : ['serialized source animation fields or native clip references differ'],
    };
}

module.exports = { NativeStaticAnimationBinding, attach, read };
