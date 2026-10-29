const cc=require('cc');
/** Static import adapter only. Source event arrays are retained in the spec and never invoked. */
class CreatorStaticToggle {
    static Apply(spec, resolveNode, resolveComponent) {
        const gaps = [];
        if (!spec || !Array.isArray(spec.bindings)) return ['missing_toggle_spec'];
        for (const row of spec.bindings) {
            try {
                const node = resolveNode && resolveNode(row.nodeSourceId);
                if (!(node instanceof cc.Node)) { gaps.push(`${row.sourceId}:node_unresolved`); continue; }
                if (row.kind === 'cc.Toggle') {
                    let toggle = node.getComponent(cc.Toggle);
                    if (!toggle) toggle = node.addComponent(cc.Toggle);
                    toggle.enabled = false;
                    if (row.checkedPresent || row.checkedSourceDefaultVerified) {
                        // Creator 3.8.8 public API updates the actual serialized _isChecked field without events.
                        toggle.setIsCheckedWithoutNotify(!!row.checkedValue);
                        if (toggle.checkMark && toggle.checkMark.node) toggle.checkMark.node.active = !!row.checkedValue;
                    }
                    if (row.interactablePresent || row.interactableSourceDefaultVerified) toggle.interactable = !!row.interactableValue;
                    if (row.checkMarkPresent || row.checkMarkSourceDefaultVerified) {
                        if (!row.checkMarkSourceId) toggle.checkMark = null;
                        else { const mark = resolveComponent && resolveComponent(row.checkMarkSourceId);
                            if (mark instanceof cc.Sprite) toggle.checkMark = mark;
                            else gaps.push(`${row.sourceId}:checkmark_unresolved`); }
                    }
                    if ((row.checkedPresent || row.checkedSourceDefaultVerified) && toggle.checkMark && toggle.checkMark.node)
                        toggle.checkMark.node.active = !!row.checkedValue;
                    if (row.targetPresent || row.targetSourceDefaultVerified) {
                        if (!row.targetSourceId) toggle.target = null;
                        else { const target = resolveNode && resolveNode(row.targetSourceId);
                            if (target instanceof cc.Node) toggle.target = target;
                            else gaps.push(`${row.sourceId}:target_unresolved`); }
                    }
                    if (row.normalColorValue && (row.normalColorPresent || row.normalColorSourceDefaultVerified)) {
                        const c = row.normalColorValue;
                        toggle.normalColor = new cc.Color(c.r, c.g, c.b, c.a);
                    }
                    if (row.transitionPresent || row.transitionSourceDefaultVerified) toggle.transition = row.transitionValue;
                    if (row.groupSourceId) {
                        const groupNode = resolveNode && resolveNode(row.groupNodeSourceId);
                        const group = groupNode instanceof cc.Node ? groupNode.getComponent(cc.ToggleContainer) : null;
                        if (group) group.enabled = false;
                        else gaps.push(`${row.sourceId}:toggle_group_unresolved`);
                    }
                } else if (row.kind === 'cc.ToggleContainer') {
                    let group = node.getComponent(cc.ToggleContainer);
                    if (!group) group = node.addComponent(cc.ToggleContainer);
                    group.enabled = false;
                    if (row.allowSwitchOffPresent || row.allowSwitchOffSourceDefaultVerified) group.allowSwitchOff = !!row.allowSwitchOffValue;
                } else gaps.push(`${row.sourceId}:unsupported_toggle_kind`);
            } catch (error) { gaps.push(`${row.sourceId}:apply_failed:${error && error.name || 'Error'}`); }
        }
        return gaps;
    }

    static Create(spec, resolveNode, resolveComponent) { return this.Apply(spec, resolveNode, resolveComponent); }

    static Read(spec, resolveNode, resolveComponent) {
        const fields = [];
        if (!spec || !Array.isArray(spec.bindings)) return { dynamicBehaviorComplete: false, fields };
        for (const row of spec.bindings) {
            const result = { sourceId: row.sourceId, kind: row.kind, verified: false, gaps: [...(row.gaps || [])] };
            try {
                const node = resolveNode && resolveNode(row.nodeSourceId);
                if (!(node instanceof cc.Node)) result.gaps.push('node_unresolved');
                else if (row.kind === 'cc.Toggle') {
                    const toggle = node.getComponent(cc.Toggle);
                    if (!toggle || toggle.enabled) result.gaps.push('toggle_missing_or_enabled');
                    else {
                        result.checkedValue = toggle.isChecked;
                        result.interactableValue = toggle.interactable;
                        result.checkMarkSourceId = row.checkMarkPresent ? row.checkMarkSourceId : null;
                        result.targetSourceId = row.targetPresent ? row.targetSourceId : null;
                        result.groupSourceId = row.groupSourceId || null;
                        let ok = (!(row.checkedPresent || row.checkedSourceDefaultVerified) || toggle.isChecked === row.checkedValue)
                            && (!(row.interactablePresent || row.interactableSourceDefaultVerified) || toggle.interactable === row.interactableValue);
                        if (row.checkMarkPresent || row.checkMarkSourceDefaultVerified)
                            ok = ok && (row.checkMarkSourceId ? toggle.checkMark === (resolveComponent && resolveComponent(row.checkMarkSourceId)) : toggle.checkMark === null);
                        if (row.targetPresent || row.targetSourceDefaultVerified)
                            ok = ok && (row.targetSourceId ? toggle.target === (resolveNode && resolveNode(row.targetSourceId)) : toggle.target === null);
                        if (row.normalColorValue && (row.normalColorPresent || row.normalColorSourceDefaultVerified)) {
                            const c = toggle.normalColor, e = row.normalColorValue;
                            ok = ok && c.r === e.r && c.g === e.g && c.b === e.b && c.a === e.a;
                        }
                        result.transitionValue = toggle.transition;
                        if (row.transitionPresent || row.transitionSourceDefaultVerified) ok = ok && toggle.transition === row.transitionValue;
                        result.normalColorValue = toggle.normalColor ? { r: toggle.normalColor.r, g: toggle.normalColor.g,
                            b: toggle.normalColor.b, a: toggle.normalColor.a } : null;
                        result.verified = !!ok;
                        if (!ok) result.gaps.push('toggle_fields_mismatch');
                    }
                } else {
                    const group = node.getComponent(cc.ToggleContainer);
                    result.allowSwitchOffValue = !!(group && group.allowSwitchOff);
                    result.verified = !!group && !group.enabled
                        && (!(row.allowSwitchOffPresent || row.allowSwitchOffSourceDefaultVerified) || group.allowSwitchOff === row.allowSwitchOffValue);
                    if (!result.verified) result.gaps.push('toggle_container_mismatch');
                }
            } catch (error) { result.gaps.push(`read_failed:${error && error.name || 'Error'}`); }
            fields.push(result);
        }
        return { dynamicBehaviorComplete: false, fields };
    }
}

module.exports = CreatorStaticToggle;
