"""Build source-bound static Toggle/ToggleContainer native binding contracts."""
from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Mapping
from pathlib import Path

from . import io


_COMPONENT_ID = re.compile(r"^(?P<asset>[^#]+)#(?P<object>\d+)(?:/components/(?P<ordinal>\d+))?$")
_TYPES = {"cc.Toggle", "cc.ToggleContainer"}
_CHECKED_KEYS = ("_N$isChecked", "isChecked")
_INTERACTABLE_KEYS = ("_N$interactable", "interactable")
_TARGET_KEYS = ("_N$target", "target")
_TRANSITION_KEYS = ("_N$transition", "transition")
_NORMAL_COLOR_KEYS = ("_N$normalColor", "normalColor")
_EVENT_KEYS = {"cc.Toggle": ("checkEvents", "clickEvents", "_N$clickEvents"),
               "cc.ToggleContainer": ("checkEvents",)}
_TOGGLE_MAPPED = {"__type__", "node", "_enabled", "_id", "_objFlags", "_prefab", "_name",
                  "_N$isChecked", "isChecked", "_N$interactable", "interactable", "_N$target", "target",
                  "checkMark", "_N$transition", "transition", "_N$normalColor", "normalColor",
                  "checkEvents", "clickEvents", "_N$clickEvents"}
_CONTAINER_MAPPED = {"__type__", "node", "_enabled", "_id", "_objFlags", "_prefab", "_name",
                     "_allowSwitchOff", "allowSwitchOff", "checkEvents"}


class StaticToggleError(ValueError):
    """Malformed frozen source component or inconsistent target plan."""


def _pick(source, aliases, label):
    present = [key for key in aliases if key in source]
    if len(present) > 1 and any(source[present[0]] != source[key] for key in present[1:]):
        raise StaticToggleError(f"conflicting serialized aliases for {label}")
    return (bool(present), source[present[0]] if present else None, present[0] if present else None)


def _source_id(asset_id, index):
    return f"{asset_id}#{index}"


def _resolve_component(manifest, identity, expected_type):
    match = _COMPONENT_ID.fullmatch(identity or "")
    if not match:
        raise StaticToggleError(f"invalid source component identity: {identity!r}")
    asset_id = match.group("asset")
    asset = next((row for row in manifest.get("assets", [])
                  if isinstance(row, Mapping) and row.get("sourceId") == asset_id), None)
    document = asset.get("document") if asset else None
    objects = document.get("instances") if isinstance(document, Mapping) else None
    if not isinstance(objects, list):
        raise StaticToggleError(f"component owner has no document.instances: {identity}")
    node_index = int(match.group("object"))
    ordinal = match.group("ordinal")
    if ordinal is None:
        raw = objects[node_index] if node_index < len(objects) else None
        node_id = None
    else:
        node = objects[node_index] if node_index < len(objects) else None
        component_list = node.get("_components") if isinstance(node, Mapping) else None
        component_ordinal = int(ordinal)
        raw = component_list[component_ordinal] if isinstance(component_list, list) and component_ordinal < len(component_list) else None
        if isinstance(node, Mapping) and node.get("__type__") == "cc.Node":
            node_id = _source_id(asset_id, node_index)
        else:
            node_id = None
    if not isinstance(raw, Mapping) or raw.get("__type__") != expected_type:
        raise StaticToggleError(f"serialized source type does not match {expected_type}: {identity}")
    if node_id is None:
        node_ref = raw.get("node")
        node_index = node_ref.get("__id__") if isinstance(node_ref, Mapping) else None
        if type(node_index) is not int or node_index < 0 or node_index >= len(objects):
            raise StaticToggleError(f"serialized component node reference is invalid: {identity}")
        node = objects[node_index]
        if not isinstance(node, Mapping) or node.get("__type__") not in {"cc.Node", "cc.Scene"}:
            raise StaticToggleError(f"serialized component node target is not a node: {identity}")
        node_id = _source_id(asset_id, node_index)
    return raw, node_id, asset_id


def _node_ref(value, asset_id, objects, label):
    if value is None:
        return None
    if not isinstance(value, Mapping) or set(value) != {"__id__"} or type(value.get("__id__")) is not int:
        raise StaticToggleError(f"{label} must be null or an exact __id__ reference")
    index = value["__id__"]
    if index < 0 or index >= len(objects):
        raise StaticToggleError(f"{label} object-table index is out of range")
    obj = objects[index]
    if not isinstance(obj, Mapping) or obj.get("__type__") not in {"cc.Node", "cc.Scene"}:
        raise StaticToggleError(f"{label} target is not a source Node")
    return _source_id(asset_id, index)


def _component_ref(value, asset_id, objects, component_ids, expected_type, label):
    if value is None:
        return None
    if not isinstance(value, Mapping) or set(value) != {"__id__"} or type(value.get("__id__")) is not int:
        raise StaticToggleError(f"{label} must be null or an exact __id__ reference")
    index = value["__id__"]
    if index < 0 or index >= len(objects):
        raise StaticToggleError(f"{label} object-table index is out of range")
    obj = objects[index]
    identity = _source_id(asset_id, index)
    if not isinstance(obj, Mapping) or obj.get("__type__") != expected_type or identity not in component_ids:
        raise StaticToggleError(f"{label} target is not a mapped {expected_type}: {identity}")
    return identity


def _json(value):
    return json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def _color(value, label):
    """Decode the v2 Color ValueType packing: R in bits 0..7, then G/B/A."""
    if not isinstance(value, Mapping) or value.get("__value_type__") != 4:
        raise StaticToggleError(f"{label} must be a serialized Cocos v2 Color ValueType")
    values = value.get("values")
    if not isinstance(values, list) or len(values) != 1 or type(values[0]) is not int or not 0 <= values[0] <= 0xFFFFFFFF:
        raise StaticToggleError(f"{label} packed color must be one unsigned 32-bit integer")
    packed = values[0]
    return {"r": packed & 255, "g": (packed >> 8) & 255,
            "b": (packed >> 16) & 255, "a": (packed >> 24) & 255,
            "packed": packed}


def prepare(source_manifest_path, plan, target, output):
    """Create source-evidenced bindings for Toggle and ToggleContainer only."""
    if target not in {"unity", "creator"}:
        raise StaticToggleError(f"unsupported target: {target!r}")
    if not isinstance(plan, Mapping):
        raise StaticToggleError("plan must be a mapping")
    manifest_path = io.safe(source_manifest_path)
    try:
        manifest_raw = io.read(manifest_path)
        manifest = io.load(manifest_raw, max_nodes=8_000_000)
    except Exception as error:
        raise StaticToggleError(f"frozen source manifest is unreadable: {manifest_path}") from error
    manifest_sha = io.sha(manifest_raw)
    if manifest_sha != plan.get("sourceManifestSha256"):
        raise StaticToggleError("frozen source manifest hash differs from target plan")
    if not isinstance(manifest, Mapping) or not isinstance(manifest.get("assets"), list):
        raise StaticToggleError("frozen source manifest has no assets array")
    plan_nodes = plan.get("nodes")
    plan_components = plan.get("components")
    if not isinstance(plan_nodes, list) or not isinstance(plan_components, list):
        raise StaticToggleError("target plan nodes and components must be arrays")
    nodes = {row.get("sourceId"): row for row in plan_nodes
             if isinstance(row, Mapping) and isinstance(row.get("sourceId"), str)}
    components = {row.get("sourceId"): row for row in plan_components
                  if isinstance(row, Mapping) and isinstance(row.get("sourceId"), str)}
    if len(nodes) != len(plan_nodes) or len(components) != len(plan_components):
        raise StaticToggleError("target plan contains duplicate or missing source identities")
    component_ids = set(components)
    toggle_rows = []
    containers_by_node = defaultdict(list)
    toggles_by_node = defaultdict(list)
    source_cache = {}
    for source_id, component in components.items():
        typ = component.get("type")
        if typ not in _TYPES:
            continue
        raw, node_id, asset_id = _resolve_component(manifest, source_id, typ)
        if component.get("node") != node_id or node_id not in nodes:
            raise StaticToggleError(f"plan/source node identity differs: {source_id}")
        asset = next(row for row in manifest["assets"] if row.get("sourceId") == asset_id)
        objects = asset["document"]["instances"]
        if typ == "cc.Toggle":
            checked_present, checked, checked_key = _pick(raw, _CHECKED_KEYS, "Toggle.checked")
            interactable_present, interactable, interactable_key = _pick(raw, _INTERACTABLE_KEYS, "Toggle.interactable")
            if checked_present and type(checked) is not bool:
                raise StaticToggleError(f"Toggle checked field must be bool: {source_id}")
            if interactable_present and type(interactable) is not bool:
                raise StaticToggleError(f"Toggle interactable field must be bool: {source_id}")
            check_mark = _component_ref(raw.get("checkMark"), asset_id, objects, component_ids, "cc.Sprite", "Toggle.checkMark")
            target_present, target_value, _ = _pick(raw, _TARGET_KEYS, "Toggle.target")
            target_node_id = _node_ref(target_value, asset_id, objects, "Toggle.target") if target_present else None
            transition_present, transition, _ = _pick(raw, _TRANSITION_KEYS, "Toggle.transition")
            if transition_present and type(transition) is not int:
                raise StaticToggleError(f"Toggle transition must be an integer: {source_id}")
            color_present, color_raw, _ = _pick(raw, _NORMAL_COLOR_KEYS, "Toggle.normalColor")
            color_value = _color(color_raw, "Toggle.normalColor") if color_present else {"r": 255, "g": 255, "b": 255, "a": 255, "packed": 0xFFFFFFFF}
            event_keys = [key for key in _EVENT_KEYS[typ] if key in raw]
            dynamic_events = {key: raw[key] for key in event_keys}
            gaps = []
            if not transition_present:
                transition = 0
            if not checked_present:
                checked = True
            if not interactable_present:
                interactable = True
            if transition not in (0, 1, 2, 3):
                gaps.append("transition_value_unknown_to_cocos_2_4_15")
            if target_node_id is not None and target_node_id not in nodes:
                raise StaticToggleError(f"Toggle target is absent from plan nodes: {target_node_id}")
            if event_keys:
                gaps.append("dynamic_toggle_events_not_executed")
            unmapped = sorted(set(raw) - _TOGGLE_MAPPED)
            if unmapped:
                gaps.append("source_fields_preserved_not_native_mapped:" + ",".join(unmapped))
            binding = {"kind": typ, "sourceId": source_id, "nodeSourceId": node_id,
                       "checkedPresent": checked_present, "checkedValue": checked,
                       "checkedSourceDefaultVerified": not checked_present,
                       "interactablePresent": interactable_present,
                       "interactableValue": interactable,
                       "interactableSourceDefaultVerified": not interactable_present,
                       "checkMarkPresent": "checkMark" in raw, "checkMarkSourceId": check_mark,
                       "checkMarkSourceDefaultVerified": "checkMark" not in raw,
                       "targetPresent": target_present, "targetSourceId": target_node_id,
                       "targetSourceDefaultVerified": not target_present,
                       "transitionPresent": transition_present, "transitionValue": transition,
                       "transitionSourceDefaultVerified": not transition_present,
                       "unityTransition": {0: "None", 1: "ColorTint", 2: "SpriteSwap", 3: "None"}.get(transition),
                       "targetTransitionMapping": "Unity scale transition is inactive in this disabled static carrier; source enum/name remain in binding" if target == "unity" and transition == 3 else "native enum mapped",
                       "normalColorPresent": color_present, "normalColorValue": color_value,
                       "normalColorSourceDefaultVerified": not color_present,
                       "sourceTransitionName": {0: "NONE", 1: "COLOR", 2: "SPRITE", 3: "SCALE"}.get(transition),
                       "sourceDefaultsEvidence": {"version": "2.4.15", "CCToggle.js": "_N$isChecked default true",
                           "CCButton.js": "interactable default true; transition NONE; normalColor WHITE; target null",
                           "CCToggleContainer.js": "allowSwitchOff default false"},
                       "groupSourceId": None, "groupNodeSourceId": None, "dynamicEventsJson": _json(dynamic_events),
                       "sourceFieldsJson": _json(raw), "gaps": gaps,
                       "enabled": False, "dynamicBehaviorComplete": False}
            binding["staticGaps"] = [gap for gap in gaps if not gap.startswith("dynamic_")]
            binding["staticComplete"] = not binding["staticGaps"]
            toggle_rows.append(binding)
            toggles_by_node[node_id].append(binding)
        else:
            allow_present, allow_value, _ = _pick(raw, ("_allowSwitchOff", "allowSwitchOff"), "ToggleContainer.allowSwitchOff")
            if allow_present and type(allow_value) is not bool:
                raise StaticToggleError(f"ToggleContainer allowSwitchOff must be bool: {source_id}")
            event_keys = [key for key in _EVENT_KEYS[typ] if key in raw]
            dynamic_events = {key: raw[key] for key in event_keys}
            gaps = []
            if event_keys:
                gaps.append("dynamic_toggle_container_events_not_executed")
            unmapped = sorted(set(raw) - _CONTAINER_MAPPED)
            if unmapped:
                gaps.append("source_fields_preserved_not_native_mapped:" + ",".join(unmapped))
            binding = {"kind": typ, "sourceId": source_id, "nodeSourceId": node_id,
                       "allowSwitchOffPresent": allow_present, "allowSwitchOffValue": allow_value if allow_present else False,
                       "allowSwitchOffSourceDefaultVerified": not allow_present,
                       "memberToggleSourceIds": [], "dynamicEventsJson": _json(dynamic_events),
                       "sourceFieldsJson": _json(raw), "gaps": gaps,
                       "enabled": False, "dynamicBehaviorComplete": False}
            binding["staticGaps"] = [gap for gap in gaps if not gap.startswith("dynamic_")]
            binding["staticComplete"] = not binding["staticGaps"]
            toggle_rows.append(binding)
            containers_by_node[node_id].append(binding)

    parent = {sid: row.get("parent") for sid, row in nodes.items()}
    for toggle in (row for row in toggle_rows if row["kind"] == "cc.Toggle"):
        node_id = toggle["nodeSourceId"]
        ancestor = node_id
        found = []
        while ancestor is not None:
            found.extend(containers_by_node.get(ancestor, []))
            ancestor = parent.get(ancestor)
        if len(found) > 1:
            raise StaticToggleError(f"Toggle has multiple ToggleContainer ancestors: {toggle['sourceId']}")
        if found:
            container = found[0]
            if parent.get(node_id) != container["nodeSourceId"]:
                toggle["gaps"].append("toggle_container_not_direct_parent")
            else:
                toggle["groupSourceId"] = container["sourceId"]
                toggle["groupNodeSourceId"] = container["nodeSourceId"]
                container["memberToggleSourceIds"].append(toggle["sourceId"])
    for node_id, rows in toggles_by_node.items():
        if len(rows) > 1:
            raise StaticToggleError(f"multiple source Toggles on one node are ambiguous for native readback: {node_id}")

    bindings = {row["sourceId"]: row for row in toggle_rows}
    spec = {"schemaVersion": 1, "target": target, "sourceManifestSha256": manifest_sha,
            "sourceEngineContract": {"name": "Cocos Creator", "version": "2.4.15",
                "sources": {"toggle": "https://github.com/cocos/cocos-engine/blob/v2.4.15/cocos2d/core/components/CCToggle.js",
                            "button": "https://github.com/cocos/cocos-engine/blob/v2.4.15/cocos2d/core/components/CCButton.js",
                            "toggleContainer": "https://github.com/cocos/cocos-engine/blob/v2.4.15/cocos2d/core/components/CCToggleContainer.js",
                            "color": "https://github.com/cocos/cocos-engine/blob/v2.4.15/cocos2d/core/value-types/color.ts"}},
            "sourceProfile": manifest.get("sourceProfile"), "sourceVersion": manifest.get("sourceVersion"),
            "bindings": bindings, "diagnostics": [
                {"code": "DYNAMIC_TOGGLE_GAP" if gap.startswith("dynamic_") else "STATIC_TOGGLE_GAP",
                 "category": "dynamic" if gap.startswith("dynamic_") else "static",
                 "sourceId": row["sourceId"], "message": gap}
                for row in toggle_rows for gap in row["gaps"]]}
    output = io.new_output(output, [manifest_path])
    io.write_json(output / "toggle-bindings.json", spec)
    return spec
