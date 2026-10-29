using System;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

/// <summary>Applies source-evidenced Toggle state only. No source event is invoked; components stay disabled.</summary>
public static class UnityStaticToggle
{
    [Serializable] public sealed class Binding
    {
        public string kind, sourceId, nodeSourceId, checkMarkSourceId, targetSourceId, groupSourceId, groupNodeSourceId;
        public bool checkedPresent, checkedValue, interactablePresent, interactableValue;
        public bool checkMarkPresent, targetPresent, allowSwitchOffPresent, allowSwitchOffValue;
        public bool transitionPresent, normalColorPresent, allowSwitchOffSourceDefaultVerified;
        public bool checkedSourceDefaultVerified, interactableSourceDefaultVerified, checkMarkSourceDefaultVerified;
        public bool targetSourceDefaultVerified, transitionSourceDefaultVerified, normalColorSourceDefaultVerified;
        public int transitionValue;
        public string unityTransition;
        public ColorValue normalColorValue;
        public string[] gaps;
    }
    [Serializable] public sealed class ColorValue { public float r, g, b, a; }
    [Serializable] public sealed class Spec { public Binding[] bindings; }
    [Serializable] public sealed class FieldRead
    {
        public string sourceId, kind, checkMarkSourceId, targetSourceId, groupSourceId;
        public bool verified, checkedValue, interactableValue, allowSwitchOffValue;
        public int transitionValue;
        public string unityTransition;
        public ColorValue normalColorValue;
        public string[] gaps;
    }
    [Serializable] public sealed class Readback { public bool dynamicBehaviorComplete; public FieldRead[] fields; }

    public static string[] Apply(Spec spec, Func<string, GameObject> resolveNode, Func<string, UnityEngine.Object> resolveComponent)
    {
        var gaps = new List<string>();
        if (spec == null || spec.bindings == null) return new[] { "missing_toggle_spec" };
        foreach (var row in spec.bindings)
        {
            try
            {
                var go = resolveNode?.Invoke(row.nodeSourceId);
                if (!go) { gaps.Add(row.sourceId + ":node_unresolved"); continue; }
                if (row.kind == "cc.Toggle")
                {
                    var toggle = go.GetComponent<Toggle>();
                    if (!toggle) toggle = go.AddComponent<Toggle>();
                    toggle.enabled = false;
                    if (row.interactablePresent || row.interactableSourceDefaultVerified) toggle.interactable = row.interactableValue;
                    if (row.checkMarkPresent || row.checkMarkSourceDefaultVerified)
                    {
                        if (String.IsNullOrEmpty(row.checkMarkSourceId)) toggle.graphic = null;
                        else { var image = resolveComponent?.Invoke(row.checkMarkSourceId) as Graphic;
                            if (image) toggle.graphic = image; else gaps.Add(row.sourceId + ":checkmark_unresolved"); }
                    }
                    if (row.targetPresent || row.targetSourceDefaultVerified)
                    {
                        if (String.IsNullOrEmpty(row.targetSourceId)) toggle.targetGraphic = null;
                        else { var targetNode = resolveNode?.Invoke(row.targetSourceId);
                            var graphic = targetNode ? targetNode.GetComponent<Graphic>() : null;
                            if (graphic) toggle.targetGraphic = graphic;
                            else if (targetNode && targetNode == go && String.Equals(row.targetSourceId, row.nodeSourceId, StringComparison.Ordinal)) toggle.targetGraphic = null;
                            else gaps.Add(row.sourceId + ":target_graphic_unresolved"); }
                    }
                    if (row.normalColorValue != null && (row.normalColorPresent || row.normalColorSourceDefaultVerified))
                    {
                        var colors = toggle.colors;
                        colors.normalColor = new Color(row.normalColorValue.r / 255f, row.normalColorValue.g / 255f,
                            row.normalColorValue.b / 255f, row.normalColorValue.a / 255f);
                        toggle.colors = colors;
                    }
                    var nativeTransition = row.unityTransition;
                    if (!String.IsNullOrEmpty(nativeTransition))
                    {
                        if (nativeTransition == "ColorTint") toggle.transition = Selectable.Transition.ColorTint;
                        else if (nativeTransition == "SpriteSwap") toggle.transition = Selectable.Transition.SpriteSwap;
                        else toggle.transition = Selectable.Transition.None;
                    }
                    if (!String.IsNullOrEmpty(row.groupSourceId))
                    {
                        var groupNode = resolveNode?.Invoke(row.groupNodeSourceId);
                        var group = groupNode ? groupNode.GetComponent<ToggleGroup>() : null;
                        if (group) { group.enabled = false; toggle.group = group; }
                        else gaps.Add(row.sourceId + ":toggle_group_unresolved");
                    }
                    if (row.checkedPresent || row.checkedSourceDefaultVerified)
                    {
                        if (toggle.graphic)
                        {
                            if (toggle.graphic.gameObject == go) toggle.graphic.enabled = row.checkedValue;
                            else toggle.graphic.gameObject.SetActive(row.checkedValue);
                        }
                        toggle.SetIsOnWithoutNotify(row.checkedValue);
                        // Toggle.PlayEffect also updates the live preview alpha. That alpha is transient,
                        // so Read verifies the persisted GameObject/component visibility above instead.
                        if (toggle.graphic) toggle.graphic.canvasRenderer.SetAlpha(row.checkedValue ? 1f : 0f);
                    }
                }
                else if (row.kind == "cc.ToggleContainer")
                {
                    var group = go.GetComponent<ToggleGroup>();
                    if (!group) group = go.AddComponent<ToggleGroup>();
                    group.enabled = false;
                    if (row.allowSwitchOffPresent || row.allowSwitchOffSourceDefaultVerified) group.allowSwitchOff = row.allowSwitchOffValue;
                }
                else gaps.Add(row.sourceId + ":unsupported_toggle_kind");
            }
            catch (Exception e) { gaps.Add(row.sourceId + ":apply_failed:" + e.GetType().Name); }
        }
        return gaps.ToArray();
    }

    public static string[] Create(Spec spec, Func<string, GameObject> resolveNode, Func<string, UnityEngine.Object> resolveComponent)
        => Apply(spec, resolveNode, resolveComponent);

    public static Readback Read(Spec spec, Func<string, GameObject> resolveNode, Func<string, UnityEngine.Object> resolveComponent)
    {
        var rows = new List<FieldRead>();
        if (spec?.bindings == null) return new Readback { dynamicBehaviorComplete = false, fields = rows.ToArray() };
        foreach (var row in spec.bindings)
        {
            var result = new FieldRead { sourceId = row.sourceId, kind = row.kind, gaps = row.gaps ?? Array.Empty<string>() };
            try
            {
                var go = resolveNode?.Invoke(row.nodeSourceId);
                if (!go) { result.gaps = Append(result.gaps, "node_unresolved"); rows.Add(result); continue; }
                if (row.kind == "cc.Toggle")
                {
                    var toggle = go.GetComponent<Toggle>();
                    if (!toggle || toggle.enabled) { result.gaps = Append(result.gaps, "toggle_missing_or_enabled"); }
                    else
                    {
                        result.checkedValue = toggle.isOn; result.interactableValue = toggle.interactable;
                        result.checkMarkSourceId = row.checkMarkPresent ? row.checkMarkSourceId : null;
                        result.targetSourceId = row.targetPresent ? row.targetSourceId : null;
                        result.groupSourceId = row.groupSourceId;
                        bool ok = (!(row.checkedPresent || row.checkedSourceDefaultVerified) || toggle.isOn == row.checkedValue)
                            && (!(row.interactablePresent || row.interactableSourceDefaultVerified) || toggle.interactable == row.interactableValue);
                        if (row.checkMarkPresent || row.checkMarkSourceDefaultVerified)
                            ok &= String.IsNullOrEmpty(row.checkMarkSourceId) ? toggle.graphic == null : ReferenceEquals(toggle.graphic, resolveComponent?.Invoke(row.checkMarkSourceId));
                        if (toggle.graphic && (row.checkedPresent || row.checkedSourceDefaultVerified))
                        {
                            bool persistedVisible = toggle.graphic.gameObject == go
                                ? toggle.graphic.enabled : toggle.graphic.gameObject.activeSelf;
                            ok &= persistedVisible == row.checkedValue;
                        }
                        if ((row.targetPresent || row.targetSourceDefaultVerified) && String.IsNullOrEmpty(row.targetSourceId)) ok &= toggle.targetGraphic == null;
                        else if (row.targetPresent || row.targetSourceDefaultVerified)
                        {
                            var targetNode = resolveNode?.Invoke(row.targetSourceId);
                            var targetGraphic = targetNode ? targetNode.GetComponent<Graphic>() : null;
                            if (String.Equals(row.targetSourceId, row.nodeSourceId, StringComparison.Ordinal) && targetNode == go && !targetGraphic)
                                ok &= toggle.targetGraphic == null;
                            else ok &= targetGraphic && toggle.targetGraphic == targetGraphic;
                        }
                        result.transitionValue = row.transitionValue;
                        result.unityTransition = toggle.transition.ToString();
                        var normalColor = toggle.colors.normalColor;
                        result.normalColorValue = new ColorValue { r = normalColor.r * 255f, g = normalColor.g * 255f,
                            b = normalColor.b * 255f, a = normalColor.a * 255f };
                        if (row.normalColorValue != null && (row.normalColorPresent || row.normalColorSourceDefaultVerified))
                        {
                            var expected = row.normalColorValue;
                            ok &= Math.Abs(result.normalColorValue.r - expected.r) < 0.01f
                                && Math.Abs(result.normalColorValue.g - expected.g) < 0.01f
                                && Math.Abs(result.normalColorValue.b - expected.b) < 0.01f
                                && Math.Abs(result.normalColorValue.a - expected.a) < 0.01f;
                        }
                        string expectedTransition = row.unityTransition;
                        if (row.transitionPresent || row.transitionSourceDefaultVerified)
                            ok &= String.IsNullOrEmpty(expectedTransition) || result.unityTransition == expectedTransition;
                        result.verified = ok;
                        if (!ok) result.gaps = Append(result.gaps, "toggle_fields_mismatch");
                    }
                }
                else
                {
                    var group = go.GetComponent<ToggleGroup>();
                    result.allowSwitchOffValue = group && group.allowSwitchOff;
                    result.verified = group && !group.enabled && (!(row.allowSwitchOffPresent || row.allowSwitchOffSourceDefaultVerified) || group.allowSwitchOff == row.allowSwitchOffValue);
                    if (!result.verified) result.gaps = Append(result.gaps, "toggle_group_mismatch");
                }
            }
            catch (Exception e) { result.gaps = Append(result.gaps, "read_failed:" + e.GetType().Name); }
            rows.Add(result);
        }
        return new Readback { dynamicBehaviorComplete = false, fields = rows.ToArray() };
    }
    static string[] Append(string[] source, string item) { var list = new List<string>(source ?? Array.Empty<string>()); list.Add(item); return list.ToArray(); }
}
