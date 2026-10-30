"""Independent verifier for saved Unity static sort-queue evidence."""

from __future__ import annotations

import math
import hashlib
import json
import re

from .io import diagnostic


_SHA = re.compile(r"^[0-9a-f]{64}$")
_GUID = re.compile(r"^[0-9a-f]{32}$")


def _diag(owner, message):
    return diagnostic("STATIC_SORT_QUEUE_NATIVE_MISMATCH", owner, message, owner)


def _same(actual, expected, keys):
    return all(actual.get(key) == expected.get(key) for key in keys)


def _field_rows(specs, rows, owner, *, sort_root=False):
    key = "sourceSortRoots" if sort_root else "sourceFields"
    if not isinstance(rows, list) or len(rows) != len(specs):
        return [f"{key} actual row count differs"]
    failures = []
    fields = ("sourceId", "nativeId", "node")
    actual_ids = []
    for index, (expected, actual) in enumerate(zip(specs, rows)):
        if not isinstance(actual, dict):
            failures.append(f"{key}[{index}] is malformed")
            continue
        actual_ids.append(actual.get("sourceId"))
        source_values_match = _same(actual, expected, fields)
        if sort_root:
            source_values_match = source_values_match and actual.get("enabledInSource") == expected.get("enabled")
        else:
            source_values_match = (source_values_match and actual.get("enabledInSource") == expected.get("enabled") and
                                   actual.get("sourceSortOrder") == expected.get("sortOrder"))
        if not source_values_match:
            failures.append(f"{key}[{index}] source value differs")
        if (actual.get("identityPresent") is not True or actual.get("verified") is not True or
                actual.get("identityComponentEnabled") is not False or
                actual.get("actualSourceId") != expected.get("sourceId") or
                actual.get("actualNativeId") != expected.get("nativeId") or
                actual.get("actualEnabledInSource") is not expected.get("enabled")):
            failures.append(f"{key}[{index}] persistent typed identity readback differs")
        if not sort_root and actual.get("actualSortOrder") != expected.get("sortOrder"):
            failures.append(f"sourceFields[{index}] actual sort order differs")
    if len(actual_ids) != len(set(actual_ids)):
        failures.append(f"{key} contains duplicate source identities")
    return failures


def _check_graphics(spec, queue_readback, owner, mode):
    failures = []
    expected = spec.get("renderers")
    rows = queue_readback.get("graphics")
    empty_rows = queue_readback.get("emptyRenderers")
    if not isinstance(expected, list) or not isinstance(rows, list) or not isinstance(empty_rows, list):
        return [f"{mode} graphics evidence is absent"]
    expected_by_id = {row.get("sourceComponentId"): row for row in expected if isinstance(row, dict)}
    empty_by_id = {row.get("sourceComponentId"): row for row in empty_rows
                   if isinstance(row, dict) and row.get("actualQueueIndex", -1) >= 0}
    non_draw = spec.get("nonDrawRenderers") or []
    retained_by_id = {row.get("sourceComponentId"): row for row in empty_rows
                      if isinstance(row, dict) and row.get("actualQueueIndex") == -1}
    expected_non_draw = {row.get("sourceComponentId"): row for row in non_draw if isinstance(row, dict)}
    if set(retained_by_id) != set(expected_non_draw):
        failures.append(f"{mode} disabled source renderer denominator differs")
    for sid, row in retained_by_id.items():
        source = expected_non_draw.get(sid)
        if source is None or not _empty_renderer_matches(source, row, mode):
            failures.append(f"{mode} disabled renderer typed evidence differs: {sid}")
    for sid, row in empty_by_id.items():
        source = expected_by_id.get(sid)
        if source is None or not _empty_renderer_matches(source, row, mode):
            failures.append(f"{mode} empty renderer typed evidence differs: {sid}")
    drawable_expected = {sid: row for sid, row in expected_by_id.items() if sid not in empty_by_id}
    seen = set()
    actual_order = []
    for row in rows:
        if not isinstance(row, dict):
            failures.append(f"{mode} graphic row is malformed")
            continue
        sid = row.get("sourceComponentId")
        source = drawable_expected.get(sid)
        if source is None:
            failures.append(f"{mode} graphic source identity is unexpected")
            continue
        seen.add(sid)
        actual_order.append((row.get("sourceQueueIndex"), sid))
        if row.get("sourceNode") != source.get("node"):
            failures.append(f"{mode} graphic source node differs: {sid}")
        if not isinstance(row.get("sourceQueueIndex"), int) or row.get("sourceQueueIndex") < 0:
            failures.append(f"{mode} graphic actual generated queue index is invalid: {sid}")
        if row.get("staticSnapshotVerified") is not True or row.get("verified") is not True:
            failures.append(f"{mode} graphic snapshot is not verified: {sid}")
        if row.get("sourceGraphicEnabled") is not True or row.get("vertexCount", 0) <= 0:
            failures.append(f"{mode} graphic has no enabled source geometry: {sid}")
        if not _GUID.fullmatch(row.get("meshAssetGuid") or ""):
            failures.append(f"{mode} graphic mesh asset identity is missing: {sid}")
        for key in ("capturedSourceMeshSha256", "meshContentSha256", "proxyMeshSha256"):
            if not _SHA.fullmatch(row.get(key) or ""):
                failures.append(f"{mode} graphic {key} evidence is missing: {sid}")
        if row.get("meshContentSha256") != row.get("proxyMeshSha256"):
            failures.append(f"{mode} persisted mesh content hash differs: {sid}")
        alpha_pairs = (("sourceRendererAlpha", "proxyRendererAlpha"),
                       ("sourceInheritedAlpha", "proxyInheritedAlpha"),
                       ("sourceEffectiveAlpha", "proxyEffectiveAlpha"))
        alpha_values_valid = True
        for source_key, proxy_key in alpha_pairs:
            source_alpha, proxy_alpha = row.get(source_key), row.get(proxy_key)
            if (type(source_alpha) not in (int, float) or type(proxy_alpha) not in (int, float) or
                    not math.isfinite(source_alpha) or not math.isfinite(proxy_alpha) or
                    abs(source_alpha - proxy_alpha) > 1e-4):
                alpha_values_valid = False
        if row.get("opacityVerified") is not True or not alpha_values_valid:
            failures.append(f"{mode} CanvasGroup/CanvasRenderer alpha evidence differs: {sid}")
        counts = row.get("sourceUvChannelVertexCounts")
        proxy_counts = row.get("proxyUvChannelVertexCounts")
        dimensions = row.get("sourceUvChannelDimensions")
        proxy_dimensions = row.get("proxyUvChannelDimensions")
        if (not isinstance(counts, list) or len(counts) != 8 or
                not isinstance(proxy_counts, list) or len(proxy_counts) != 8 or
                counts != proxy_counts or not isinstance(dimensions, list) or len(dimensions) != 8 or
                not isinstance(proxy_dimensions, list) or len(proxy_dimensions) != 8 or
                dimensions != proxy_dimensions):
            failures.append(f"{mode} UV channels 0–7 do not match source evidence: {sid}")
        if mode == "loaded":
            if (row.get("runtimeMeshVerified") is not True or
                    row.get("transformedGeometryVerified") is not True or
                    row.get("sourceCulled") is not True or row.get("proxyVisible") is not True):
                failures.append(f"loaded graphic presentation evidence is incomplete: {sid}")
            if row.get("sourceMeshSha256") != row.get("capturedSourceMeshSha256"):
                failures.append(f"loaded source mesh differs from its persisted capture: {sid}")
            if row.get("renderedMeshSha256") != row.get("proxyMeshSha256"):
                failures.append(f"loaded CanvasRenderer mesh differs from persisted proxy: {sid}")
            if (row.get("renderedUvChannelVertexCounts") != proxy_counts or
                    row.get("renderedUvChannelDimensions") != proxy_dimensions):
                failures.append(f"loaded CanvasRenderer UV channels differ from proxy: {sid}")
            metrics = ("transformedTopologyMatches", "transformedUvMatches", "transformedColorsMatch",
                       "transformedNormalsMatch", "transformedTangentsMatch")
            max_error = row.get("maxWorldVertexError")
            if (type(max_error) not in (int, float) or not math.isfinite(max_error) or
                    max_error < 0 or max_error > 0.001 or
                    row.get("sourceVertexCount") != row.get("persistedProxyVertexCount") or
                    any(row.get(key) is not True for key in metrics)):
                failures.append(
                    f"loaded transformed mesh diagnostics differ: {sid} "
                    f"worldVertexError={max_error} topology={row.get('transformedTopologyMatches')} "
                    f"uv={row.get('transformedUvMatches')} colors={row.get('transformedColorsMatch')} "
                    f"normals={row.get('transformedNormalsMatch')} tangents={row.get('transformedTangentsMatch')}"
                )
        else:
            if row.get("renderedUvChannelVertexCounts") not in ([], None):
                failures.append(f"persistent readback claims initialized renderer channels: {sid}")
    if set(drawable_expected) != seen:
        failures.append(f"{mode} graphic source denominator differs")
    events = spec.get("drawEvents") or []
    expected_order = [event.get("sourceComponentId") for event in events
                      if isinstance(event, dict) and event.get("kind") == "renderer"]
    if not events:
        expected_order = [row.get("sourceComponentId") for row in expected if isinstance(row, dict)]
    observed_order = []
    queue_events = actual_order + [(row.get("actualQueueIndex"), sid) for sid, row in empty_by_id.items()]
    for _, sid in sorted(queue_events, key=lambda item: item[0] if isinstance(item[0], int) else -1):
        if not observed_order or observed_order[-1] != sid:
            observed_order.append(sid)
    if observed_order != expected_order:
        failures.append(f"{mode} renderer ordering differs from source queue")
    return failures


def _check_text_sources(spec, queue_readback, mode):
    failures = []
    non_draw_ids = {row.get("sourceComponentId") for row in spec.get("nonDrawRenderers", []) if isinstance(row, dict)}
    graphic_rows = queue_readback.get("graphics") or []
    drawable_ids = {row.get("sourceComponentId") for row in graphic_rows if isinstance(row, dict)}
    text_specs = {row.get("sourceComponentId"): row for row in spec.get("renderers", [])
                    if isinstance(row, dict) and row.get("sourceType") in ("cc.Label", "cc.RichText") and
                    row.get("sourceComponentId") not in non_draw_ids and row.get("sourceComponentId") in drawable_ids}
    expected_ids = set(text_specs)
    actual = queue_readback.get("textSources")
    if not isinstance(actual, list):
        return [f"{mode} TMP typed source readback is absent"]
    actual_ids = set()
    actual_slots = set()
    slot_enumerations = {}
    graphics = graphic_rows
    by_graphic_identity = {}
    for graphic in graphics:
        if isinstance(graphic, dict):
            by_graphic_identity.setdefault((graphic.get("sourceComponentId"), graphic.get("textMaterialSlot")), []).append(graphic)
    for row in actual:
        if (not isinstance(row, dict) or not isinstance(row.get("sourceComponentId"), str) or
                not isinstance(row.get("evidence"), dict)):
            failures.append(f"{mode} TMP source row is malformed")
            continue
        source_id = row["sourceComponentId"]
        slot = row.get("materialSlot")
        evidence = row["evidence"]
        actual_ids.add(source_id)
        key = (source_id, slot)
        if type(slot) is not int or slot < 0 or key in actual_slots:
            failures.append(f"{mode} TMP material slot is invalid or duplicated: {source_id}")
        actual_slots.add(key)
        enumeration = evidence.get("textSlotEnumeration")
        if not isinstance(enumeration, dict):
            failures.append(f"{mode} TMP slot enumeration evidence is absent: {source_id}")
        else:
            rows = enumeration.get("rows")
            rows = rows if isinstance(rows, list) else []
            row_slots = [entry.get("slot") for entry in rows if isinstance(entry, dict)]
            if (enumeration.get("verified") is not True or enumeration.get("sourceComponentId") != source_id or
                    type(enumeration.get("slotCount")) is not int or enumeration.get("slotCount") != len(rows) or
                    len(row_slots) != len(rows) or any(type(value) is not int for value in row_slots) or
                    sorted(row_slots) != list(range(len(rows))) or
                    not _SHA.fullmatch(enumeration.get("sourceTextSha256") or "") or
                    not _SHA.fullmatch(enumeration.get("evidenceSha256") or "") or
                    any(not _SHA.fullmatch(entry.get("evidenceSha256") or "") for entry in rows if isinstance(entry, dict))):
                failures.append(f"{mode} TMP slot enumeration identity or denominator differs: {source_id}")
            else:
                previous = slot_enumerations.get(source_id)
                if previous is not None and previous.get("evidenceSha256") != enumeration.get("evidenceSha256"):
                    failures.append(f"{mode} TMP slot enumeration differs across proxy identities: {source_id}")
                slot_enumerations[source_id] = enumeration
                placeholders = [entry for entry in rows if entry.get("disposition") == "empty-placeholder"]
                unknown = [entry for entry in rows if entry.get("disposition") not in ("drawable", "empty-placeholder")]
                for entry in placeholders:
                    if (entry.get("slot") != 0 or entry.get("characterReferences") != 0 or
                            entry.get("visibleCharacterReferences") != 0 or
                            entry.get("textInfoNondegenerateTriangleCount") != 0 or
                            entry.get("canvasNondegenerateTriangleCount") != 0 or
                            not _SHA.fullmatch(entry.get("evidenceSha256") or "")):
                        failures.append(f"{mode} TMP placeholder lacks exact slot-0 zero-draw proof: {source_id}")
                if unknown or len(placeholders) > 1:
                    failures.append(f"{mode} TMP slot disposition is invalid: {source_id}")
        if source_id not in expected_ids:
            failures.append(f"{mode} TMP row has an extra source component: {source_id}")
        expected_node = text_specs.get(source_id, {}).get("node")
        if (row.get("sourceNode") != expected_node or row.get("readbackMode") != mode or
                evidence.get("sourceComponentId") != source_id or evidence.get("materialSlot") != slot):
            failures.append(f"{mode} TMP owner source-node/material-slot mapping differs: {source_id}")
        for key_name in ("proxyMaterialGuid", "shaderGuid", "textureGuid", "proxyMeshGuid", "ownerFontMaterialGuid"):
            if not _GUID.fullmatch(evidence.get(key_name) or ""):
                failures.append(f"{mode} TMP {key_name} identity is missing: {source_id}")
        source_material_guid = evidence.get("materialGuid")
        if source_material_guid and not _GUID.fullmatch(source_material_guid):
            failures.append(f"{mode} TMP source material GUID is malformed: {source_id}")
        if mode == "persistent":
            if (not _GUID.fullmatch(evidence.get("ownerGuid") or "") or
                    type(evidence.get("ownerLocalFileId")) is not int or evidence["ownerLocalFileId"] == 0 or
                    evidence.get("ownerScopeVerified") is not True):
                failures.append(f"persistent TMP mapped owner GUID/local ID differs: {source_id}")
        elif (evidence.get("ownerGuid") not in (None, "") or evidence.get("ownerLocalFileId") not in (None, 0) or
              evidence.get("ownerScopeVerified") is not True):
            failures.append(f"loaded TMP owner does not match the transient loaded source map: {source_id}")
        for optional_guid in ("fontAssetGuid", "spriteAssetGuid"):
            value = evidence.get(optional_guid)
            if value and not _GUID.fullmatch(value):
                failures.append(f"{mode} TMP {optional_guid} is malformed: {source_id}")
        local_keys = ("proxyMaterialLocalFileId", "ownerFontMaterialLocalFileId", "shaderLocalFileId",
                      "textureLocalFileId", "proxyMeshLocalFileId")
        for local_key in local_keys:
            if type(evidence.get(local_key)) is not int or evidence[local_key] == 0:
                failures.append(f"{mode} TMP {local_key} is missing: {source_id}")
        if source_material_guid and (type(evidence.get("materialLocalFileId")) is not int or evidence["materialLocalFileId"] == 0):
            failures.append(f"{mode} TMP source material local ID is missing: {source_id}")
        if evidence.get("fontAssetGuid") and (type(evidence.get("fontAssetLocalFileId")) is not int or evidence["fontAssetLocalFileId"] == 0):
            failures.append(f"{mode} TMP font asset local ID is missing: {source_id}")
        if evidence.get("spriteAssetGuid") and (type(evidence.get("spriteAssetLocalFileId")) is not int or evidence["spriteAssetLocalFileId"] == 0):
            failures.append(f"{mode} TMP sprite asset local ID is missing: {source_id}")
        fallback_algorithm = evidence.get("tmpFallbackAlgorithm")
        if fallback_algorithm:
            if (fallback_algorithm not in ("tmpro-fallback-font-material-v1",
                                           "tmpro-fallback-font-material-v1+tmpro-multi-atlas-v1",
                                           "tmpro-multi-atlas-v1") or
                    not _GUID.fullmatch(evidence.get("fallbackFontAssetGuid") or "") or
                    not _GUID.fullmatch(evidence.get("fallbackFontMaterialGuid") or "") or
                    not _GUID.fullmatch(evidence.get("fallbackAtlasGuid") or "") or
                    any(type(evidence.get(key)) is not int or evidence[key] == 0 for key in
                        ("fallbackFontAssetLocalFileId", "fallbackFontMaterialLocalFileId", "fallbackAtlasLocalFileId")) or
                    not _SHA.fullmatch(evidence.get("transientFallbackFingerprint") or "") or
                    not _SHA.fullmatch(evidence.get("bakedProxyMaterialFingerprint") or "") or
                    evidence.get("transientFallbackFingerprint") != evidence.get("bakedProxyMaterialFingerprint")):
                failures.append(f"{mode} TMP SDK fallback descriptor or baked material proof differs: {source_id}")
        else:
            if source_material_guid is None or not _SHA.fullmatch(evidence.get("sourceMaterialFingerprint") or "") or \
                    evidence.get("bakedProxyMaterialFingerprint") != evidence.get("sourceMaterialFingerprint"):
                failures.append(f"{mode} TMP direct source material proof is incomplete: {source_id}")
        for fingerprint_key in ("sourceMaterialFingerprint", "ownerFontMaterialFingerprint",
                                "fallbackFontMaterialFingerprint", "bakedProxyMaterialFingerprint"):
            value = evidence.get(fingerprint_key)
            if value and not _SHA.fullmatch(value):
                failures.append(f"{mode} TMP {fingerprint_key} is malformed: {source_id}")
        if (bool(evidence.get("fontAssetGuid")) == bool(evidence.get("spriteAssetGuid")) or
                evidence.get("persistentReferencesVerified") is not True or
                evidence.get("fontAssetVerified") is not True or evidence.get("spriteAssetVerified") is not True or
                evidence.get("materialVerified") is not True or evidence.get("shaderVerified") is not True or
                evidence.get("textureVerified") is not True or evidence.get("proxyMaterialVerified") is not True or
                evidence.get("tmpFallbackDescriptorVerified") is not True or
                evidence.get("transientFallbackVerified") is not True or
                evidence.get("ownerFontMaterialVerified") is not True or
                evidence.get("fallbackFontAssetVerified") is not True or
                evidence.get("fallbackFontMaterialVerified") is not True or
                evidence.get("fallbackAtlasVerified") is not True or
                evidence.get("bakedProxyMeshVerified") is not True or
                evidence.get("verified") is not True):
            failures.append(f"{mode} TMP persistent owner/font/material/atlas proof differs: {source_id}")
        if not _SHA.fullmatch(evidence.get("sourceMeshSha256") or "") or not _SHA.fullmatch(evidence.get("proxyMeshSha256") or ""):
            failures.append(f"{mode} TMP source/proxy mesh hashes are missing: {source_id}")
        linked = by_graphic_identity.get((source_id, slot), [])
        if len(linked) != 1 or linked[0].get("meshAssetGuid") != evidence.get("proxyMeshGuid") or \
                linked[0].get("proxyMeshSha256") != evidence.get("proxyMeshSha256") or \
                linked[0].get("materialGuid") != evidence.get("proxyMaterialGuid") or linked[0].get("textureGuid") != evidence.get("textureGuid"):
            failures.append(f"{mode} TMP typed assets do not match exactly one proxy graphic: {source_id}")
        if mode == "loaded" and (evidence.get("generatedSlotResolved") is not True or
                                  evidence.get("sourceStateVerified") is not True or evidence.get("sourceMeshVerified") is not True):
            failures.append(f"loaded TMP source slot state or mesh differs: {source_id}")
        if mode == "persistent" and evidence.get("generatedSlotResolved") is True:
            failures.append(f"persistent TMP readback claims a loaded generated slot: {source_id}")
    for source_id, enumeration in slot_enumerations.items():
        expected_drawable_slots = {entry.get("slot") for entry in enumeration.get("rows", [])
                                   if entry.get("disposition") == "drawable"}
        observed_slots = {slot for sid, slot in actual_slots if sid == source_id}
        if expected_drawable_slots != observed_slots:
            failures.append(f"{mode} TMP drawable slots differ from native proxy identities: {source_id}")
        if not expected_drawable_slots:
            failures.append(f"{mode} TMP owner has no drawable slot identity: {source_id}")
    if actual_ids != expected_ids:
        failures.append(f"{mode} TMP source component denominator differs")
    if queue_readback.get("textSourcesVerified") is not True:
        failures.append(f"{mode} TMP aggregate typed source verification is false")
    return failures


def _check_spine_owner_delegations(spec, queue_readback, mode, plan=None):
    failures = []
    renderers = spec.get("renderers")
    proof_rows = queue_readback.get("spineOwnerDelegations")
    source_spines = {row.get("sourceComponentId"): row for row in renderers or []
                     if isinstance(row, dict) and row.get("sourceType") == "sp.Skeleton"}
    if proof_rows is None and not source_spines:
        return failures
    if not isinstance(proof_rows, list):
        return [f"{mode} Spine owner delegation evidence is absent"]
    proof_by_id = {}
    for proof in proof_rows:
        if not isinstance(proof, dict) or not isinstance(proof.get("sourceComponentId"), str):
            failures.append(f"{mode} Spine owner delegation row is malformed")
            continue
        source_id = proof["sourceComponentId"]
        if source_id in proof_by_id:
            failures.append(f"{mode} Spine owner delegation source ID repeats: {source_id}")
        if source_id not in source_spines:
            failures.append(f"{mode} Spine owner delegation has an extra source ID: {source_id}")
        proof_by_id[source_id] = proof
    graphics = queue_readback.get("graphics") or []
    graphics_by_id = {}
    for graphic in graphics:
        if isinstance(graphic, dict) and isinstance(graphic.get("sourceComponentId"), str):
            graphics_by_id.setdefault(graphic["sourceComponentId"], []).append(graphic)
    for source_id, source in source_spines.items():
        rows = graphics_by_id.get(source_id, [])
        proof = proof_by_id.get(source_id)
        generated_children = [row for row in rows if row.get("generatedSourceChild") is True]
        if proof is None:
            if generated_children and len(generated_children) == len(rows):
                failures.append(f"{mode} Spine generated-child-only draw lacks owner delegation proof: {source_id}")
            continue
        child_paths = proof.get("delegatedChildPaths")
        child_types = proof.get("delegatedChildGraphicTypes")
        child_vertices = proof.get("childMeshVertexCounts")
        child_submeshes = proof.get("childMeshSubmeshCounts")
        child_materials = proof.get("childCanvasMaterialCounts")
        child_texture_guids = proof.get("delegatedChildTextureGuids")
        child_material_guids = proof.get("delegatedChildMaterialGuids")
        count = len(child_paths) if isinstance(child_paths, list) else -1
        spine_stage = (plan or {}).get("spineNativeStage") or {}
        expected_components = [entry for entry in spine_stage.get("components", [])
                              if isinstance(entry, dict) and entry.get("sourceComponentId") == source_id]
        expected_data = []
        if len(expected_components) == 1 and expected_components[0].get("sourceDataAssetId"):
            expected_data = [entry for entry in spine_stage.get("dataAssets", [])
                             if isinstance(entry, dict) and entry.get("sourceAssetId") == expected_components[0].get("sourceDataAssetId")]
        stage_mapping_matches = (len(expected_components) == 1 and len(expected_data) == 1 and
            expected_components[0].get("sourceHasStaticDataReference") is True and
            proof.get("sourceDataAssetId") == expected_components[0].get("sourceDataAssetId") and
            proof.get("sourceDataAssetPath") == expected_data[0].get("skeletonDataAssetPath") and
            proof.get("sourceManifestSha256") == spine_stage.get("sourceManifestSha256"))
        if (proof.get("sourceNode") != source.get("node") or
                proof.get("sourceGraphicType") != "Spine.Unity.SkeletonGraphic" or
                proof.get("sourceIdentityComponentId") != source_id or
                not isinstance(proof.get("sourceDataAssetId"), str) or
                not proof["sourceDataAssetId"].startswith("spineAsset:") or
                not isinstance(proof.get("sourceDataAssetPath"), str) or
                not proof["sourceDataAssetPath"].startswith("Assets/") or
                not _GUID.fullmatch(proof.get("sourceDataAssetGuid") or "") or
                proof.get("sourceBindingPlanPath") != "Assets/Game/Editor/Conversion/spine-native-binding-plan.json" or
                not _SHA.fullmatch(proof.get("sourceBindingPlanSha256") or "") or
                not _SHA.fullmatch(proof.get("sourceManifestSha256") or "") or
                (spine_stage and not stage_mapping_matches) or
                proof.get("rootMeshVertexCount") != 0 or proof.get("rootMeshDelegated") is not True or
                proof.get("sourceIdentityVerified") is not True or
                proof.get("sourceDataReferenceVerified") is not True or
                proof.get("childRendererListVerified") is not True or
                proof.get("childReferencesPersistent") is not True or
                proof.get("verified") is not True or count <= 0 or
                not all(isinstance(values, list) and len(values) == count for values in
                        (child_types, child_vertices, child_submeshes, child_materials,
                         child_texture_guids, child_material_guids))):
            failures.append(f"{mode} Spine owner/registered-renderer typed proof differs: {source_id}")
            continue
        if (any(value != "UnityEngine.UI.RawImage" for value in child_types) or
                any(type(value) is not int or value <= 0 for value in child_vertices) or
                any(value != 1 for value in child_submeshes) or any(value != 1 for value in child_materials) or
                any(not _GUID.fullmatch(value or "") for value in child_material_guids) or
                any(not _GUID.fullmatch(value or "") for value in child_texture_guids)):
            failures.append(f"{mode} Spine delegated child mesh/resource proof differs: {source_id}")
        if (len(rows) != count or len(generated_children) != count or
                any(row.get("generatedSourceChild") is not True or
                    row.get("nativeGraphicType") != "UnityEngine.UI.RawImage" or
                    row.get("sourceNode") != source.get("node") for row in rows) or
                [row.get("vertexCount") for row in rows] != child_vertices):
            failures.append(f"{mode} Spine child proxy rows do not cover delegated native renderers: {source_id}")
        if (type(proof.get("rootCanvasMaterialCount")) is not int or proof["rootCanvasMaterialCount"] < 0 or
                (proof.get("rootMeshWasMissing") is True and proof.get("rootMeshSubmeshCount") != -1) or
                (proof.get("rootMeshWasMissing") is False and type(proof.get("rootMeshSubmeshCount")) is not int)):
            failures.append(f"{mode} Spine owner root mesh/material diagnostics are malformed: {source_id}")
    return failures


def _check_spine_non_draw_children(spec, queue_readback, mode):
    failures = []
    expected_rows = [row for row in spec.get("nonDrawRenderers", [])
                     if isinstance(row, dict) and row.get("sourceType") == "sp.Skeleton"]
    actual_rows = queue_readback.get("spineNonDrawChildren")
    if not expected_rows and actual_rows is None:
        return failures
    if not isinstance(actual_rows, list):
        return [f"{mode} Spine non-draw child evidence is absent"]
    expected_by_id = {row.get("sourceComponentId"): row for row in expected_rows}
    if len(expected_by_id) != len(expected_rows):
        failures.append(f"{mode} Spine non-draw spec identities repeat")
    actual_by_id = {}
    child_keys = set()
    for row in actual_rows:
        if not isinstance(row, dict) or not isinstance(row.get("sourceComponentId"), str):
            failures.append(f"{mode} Spine non-draw child row is malformed")
            continue
        sid = row["sourceComponentId"]
        actual_by_id.setdefault(sid, []).append(row)
        key = (sid, row.get("childPath"))
        if key in child_keys:
            failures.append(f"{mode} Spine non-draw child identity repeats: {sid}")
        child_keys.add(key)
        expected = expected_by_id.get(sid)
        if expected is None:
            failures.append(f"{mode} Spine non-draw child has an extra source ID: {sid}")
            continue
        reason = "inactive-source" if expected.get("sourceActive") is False else "disabled-source"
        identity_ok = (row.get("sourceNode") == expected.get("node") and row.get("noDrawReason") == reason and
            row.get("sourceOwnerEnabled") is expected.get("sourceEnabled") and
            row.get("sourceNodeActive") is expected.get("sourceActive") and
            row.get("sourceIdentityComponentId") == sid and
            isinstance(row.get("sourceDataAssetId"), str) and row["sourceDataAssetId"].startswith("spineAsset:") and
            isinstance(row.get("sourceDataAssetPath"), str) and row["sourceDataAssetPath"].startswith("Assets/") and
            bool(_GUID.fullmatch(row.get("sourceDataAssetGuid") or "")) and
            isinstance(row.get("childPath"), str) and bool(row["childPath"]) and
            row.get("childGraphicType") == "UnityEngine.UI.RawImage" and
            bool(_GUID.fullmatch(row.get("childMaterialGuid") or "")) and
            bool(_GUID.fullmatch(row.get("childTextureGuid") or "")) and
            row.get("sourceIdentityVerified") is True and row.get("sourceDataReferenceVerified") is True and
            row.get("registeredChildVerified") is True and row.get("childReferencePersistent") is True and
            row.get("verified") is True)
        if not identity_ok:
            failures.append(f"{mode} Spine non-draw owner/child source identity or resource proof differs: {sid}")
        source_enabled, source_active, source_active_self = (row.get("sourceChildEnabled"),
            row.get("sourceChildActiveInHierarchy"), row.get("sourceChildActiveSelf"))
        if (type(source_enabled) is not bool or type(source_active) is not bool or
                type(source_active_self) is not bool or row.get("targetChildEnabled") is not source_enabled or
                row.get("targetChildActiveInHierarchy") is not source_active):
            failures.append(f"{mode} Spine child target state differs from its typed source state: {sid}")
        safe_state = source_active is False if expected.get("sourceActive") is False else source_active is False or source_enabled is False
        if row.get("childNoDrawVerified") is not True or not safe_state:
            failures.append(f"{mode} Spine registered child can still draw under a no-draw owner: {sid}")
        if any(type(row.get(key)) is not int or row.get(key) < -1 for key in
               ("sourceChildMeshVertexCount", "sourceChildMeshSubmeshCount", "sourceChildMaterialCount")):
            failures.append(f"{mode} Spine non-draw child mesh/material diagnostics are malformed: {sid}")
    if set(actual_by_id) != set(expected_by_id):
        failures.append(f"{mode} Spine non-draw child owner denominator differs")
    if any(not rows for rows in actual_by_id.values()):
        failures.append(f"{mode} Spine non-draw child mapping is empty")
    return failures


def _empty_renderer_matches(expected, actual, mode):
    if (not isinstance(actual, dict) or actual.get("sourceNode") != expected.get("node") or
            actual.get("sourceType") != expected.get("sourceType") or
            actual.get("sourceComponentType") != expected.get("expectedGraphicType") or
            actual.get("sourceEnabled") is not expected.get("sourceEnabled") or
            actual.get("sourceActive") is not expected.get("sourceActive") or
            actual.get("sourceActiveInHierarchy") is not expected.get("sourceActive") or
            actual.get("sourceTextureBound") is not expected.get("sourceTextureBound", False) or
            actual.get("sourceText", "") != expected.get("sourceText", "") or
            actual.get("nativeTextExpectation", "") != expected.get("nativeTextExpectation", "") or
            actual.get("sourceTextEmpty") is not expected.get("sourceTextEmpty", False) or
            actual.get("sourceFontMissing") is not expected.get("sourceFontMissing", False) or
            actual.get("sourceReferenceVerified") is not True or actual.get("typedFieldsVerified") is not True or
            actual.get("carrierPresent") is not True or actual.get("verified") is not True or
            not _GUID.fullmatch(actual.get("carrierGuid") or "") or
            type(actual.get("carrierLocalFileId")) is not int or actual.get("carrierLocalFileId") == 0):
        return False
    source_type = expected.get("sourceType")
    if expected.get("sourceActive") is False:
        if actual.get("noDrawReason") != "source-node-inactive":
            return False
        if source_type == "cc.Sprite":
            return (actual.get("nativeTextureBound") is expected.get("sourceTextureBound") and
                    actual.get("nativeGraphicEnabled") is (expected.get("sourceEnabled") is True and
                                                            expected.get("sourceTextureBound") is True))
        if source_type in ("cc.Label", "cc.RichText"):
            return (actual.get("nativeGraphicEnabled") is expected.get("sourceEnabled") and
                    actual.get("nativeText") == expected.get("nativeTextExpectation") and
                    actual.get("nativeFontMissing") is expected.get("sourceFontMissing"))
        if source_type == "cc.Graphics":
            return (actual.get("sourceCommandsEmpty") is True and actual.get("nativeCommandsEmpty") is True and
                    actual.get("sourceFieldsSha256") == expected.get("sourceFieldsSha256") and
                    actual.get("sourceDrawingCommands") == expected.get("sourceDrawingCommands") and
                    actual.get("sourceMaterialGuids") == expected.get("sourceMaterialGuids") and
                    actual.get("actualSourceMaterialGuids") == expected.get("sourceMaterialGuids"))
        return actual.get("nativeComponentEnabled") is expected.get("sourceEnabled")
    if expected.get("sourceEnabled") is False:
        if source_type in ("cc.Label", "cc.RichText"):
            return (actual.get("nativeComponentEnabled") is False and
                    actual.get("nativeText") == expected.get("nativeTextExpectation") and
                    actual.get("nativeFontMissing") is expected.get("sourceFontMissing") and
                    actual.get("noDrawReason") == "source-renderer-disabled")
        return actual.get("nativeComponentEnabled") is False and actual.get("noDrawReason") == "source-renderer-disabled"
    if source_type == "cc.Sprite":
        return (expected.get("sourceEnabled") is True and expected.get("sourceTextureBound") is False and
                actual.get("nativeGraphicEnabled") is False and actual.get("nativeTextureBound") is False and
                actual.get("sourceMeshPresent") is False and actual.get("sourceMeshVertexCount") == 0 and
                actual.get("noDrawReason") == "source-sprite-frame-null-native-image-disabled-zero-mesh")
    if source_type in ("cc.Label", "cc.RichText") and expected.get("sourceEnabled") is True:
        return (expected.get("sourceTextEmpty") is True and actual.get("nativeTextEmpty") is True and
                actual.get("nativeText") == expected.get("nativeTextExpectation") and
                actual.get("nativeGraphicEnabled") is True and actual.get("sourceMeshPresent") is False and
                actual.get("sourceMeshVertexCount") == 0 and actual.get("nativeFontMissing") is expected.get("sourceFontMissing") and
                actual.get("noDrawReason") == "source-text-empty-zero-mesh")
    if source_type == "cc.Graphics":
        expected_materials = expected.get("sourceMaterialGuids") or []
        return (expected.get("sourceCommandsEmpty") is True and actual.get("sourceCommandsEmpty") is True and
                actual.get("nativeCommandsEmpty") is True and actual.get("nativeComponentEnabled") is False and
                actual.get("sourceFieldsSha256") == expected.get("sourceFieldsSha256") and
                actual.get("sourceDrawingCommands") == expected.get("sourceDrawingCommands") and
                actual.get("sourceMaterialGuids") == expected_materials and
                actual.get("actualSourceMaterialGuids") == expected_materials and
                actual.get("noDrawReason") == "source-graphics-command-stream-proven-empty")
    return expected.get("sourceEnabled") is False and actual.get("nativeComponentEnabled") is False and actual.get("noDrawReason") == "source-renderer-disabled"


def _check_queue(spec, row, owner, mode, plan=None):
    failures = []
    if not isinstance(row, dict):
        return [f"{mode} queue readback is absent"]
    if row.get("rootScope") != spec.get("rootScope"):
        failures.append(f"{mode} queue root identity differs")
    if mode == "persistent":
        if (row.get("readbackMode") != "persistent" or row.get("provisional") is not False or
                row.get("verified") is not True or row.get("persistentSnapshotVerified") is not True or
                row.get("runtimeGeometryDeferred") is not True or
                row.get("initializedPresentationVerified") is not False):
            failures.append("saved Prefab queue lacks a persistent, runtime-deferred readback")
    else:
        if (row.get("readbackMode") != "initialized" or row.get("provisional") is not False or
                row.get("verified") is not True or row.get("persistentSnapshotVerified") is not True or
                row.get("initializedPresentationVerified") is not True or
                row.get("runtimeGeometryDeferred") is not False):
            failures.append("loaded Prefab queue lacks initialized presentation evidence")
    if row.get("sourceTreePreserved") is not True or row.get("drawSequenceVerified") is not True:
        failures.append(f"{mode} source tree or draw sequence is not verified")
    structural = row.get("structuralDiagnostics")
    if not isinstance(structural, list) or structural:
        failures.append(f"{mode} native readback reports structural failures: {structural}")
    if row.get("sourceGraphicsCovered") is not True:
        failures.append(f"{mode} source Graphic suppression coverage is incomplete")
    if row.get("layoutIgnored") is not True:
        failures.append(f"{mode} generated proxy root participates in source layout")
    if row.get("sourceFieldsPreserved") is not True:
        failures.append(f"{mode} source SortOrder fields are not preserved")
    if row.get("sourceSortRootsPreserved") is not True:
        failures.append(f"{mode} source SortRoot fields are not preserved")
    if row.get("sourceMaskReferencesVerified") is not True:
        failures.append(f"{mode} source mask component references are not verified")
    failures.extend(_field_rows(spec.get("sourceFields", []), row.get("sourceFields"), owner))
    failures.extend(_field_rows(spec.get("sourceSortRoots", []), row.get("sourceSortRoots"), owner, sort_root=True))
    failures.extend(_check_graphics(spec, row, owner, "loaded" if mode == "loaded" else "persistent"))
    failures.extend(_check_text_sources(spec, row, "loaded" if mode == "loaded" else "persistent"))
    failures.extend(_check_spine_owner_delegations(spec, row, "loaded" if mode == "loaded" else "persistent", plan))
    failures.extend(_check_spine_non_draw_children(spec, row, "loaded" if mode == "loaded" else "persistent"))
    expected_masks = [mask.get("sourceId") for mask in spec.get("masks", []) if isinstance(mask, dict)]
    masks = row.get("masks")
    if (not isinstance(masks, list) or
            [mask.get("sourceId") for mask in masks if isinstance(mask, dict)] != expected_masks or
            row.get("maskSourceIds") != expected_masks or
            any(not isinstance(mask, dict) or mask.get("verified") is not True for mask in masks or [])):
        failures.append(f"{mode} mask event identities or native fields differ: " +
                        repr([mask.get("failedChecks") for mask in masks if isinstance(mask, dict)] if isinstance(masks, list) else masks))
    return failures


def _creator_non_draw_errors(spec, actual, creator_assets=None):
    expected_rows = spec.get("nonDrawRenderers")
    actual_rows = actual.get("sourceNonDrawRenderers")
    if not isinstance(expected_rows, list) or not isinstance(actual_rows, list):
        return ["Creator typed non-draw renderer readback is absent"]
    errors = []
    expected_by_id = {}
    for row in expected_rows:
        if not isinstance(row, dict) or not isinstance(row.get("sourceId"), str) or row["sourceId"] in expected_by_id:
            errors.append("Creator non-draw renderer spec identities are malformed or duplicated")
            continue
        expected_by_id[row["sourceId"]] = row
    actual_by_id = {}
    for row in actual_rows:
        if not isinstance(row, dict) or not isinstance(row.get("sourceId"), str) or row["sourceId"] in actual_by_id:
            errors.append("Creator native non-draw renderer rows are malformed or duplicated")
            continue
        actual_by_id[row["sourceId"]] = row
    if set(actual_by_id) != set(expected_by_id):
        errors.append("Creator native non-draw renderer source IDs differ")

    component_ids = set()
    source_nodes = spec.get("sourceNodeActive") or {}
    for sid, expected in expected_by_id.items():
        row = actual_by_id.get(sid)
        if row is None:
            continue
        expected_enabled = expected.get("nativeEnabledExpected")
        expected_needs_binding = expected.get("sourceNeedsSpriteBinding")
        source_frame_asset_id = expected.get("sourceSpriteFrameAssetId")
        native_image_uuid = expected.get("nativeSpriteImageUuidExpected")
        expected_native_frame = None
        source_type = expected.get("sourceType")
        if source_type == "cc.Sprite":
            if type(expected_needs_binding) is not bool:
                errors.append(f"Creator Sprite no-draw binding policy is missing: {sid}")
            elif expected_enabled is not (expected.get("sourceEnabled") is True and not expected_needs_binding):
                errors.append(f"Creator Sprite native enabled expectation conflicts with binding policy: {sid}")
            elif expected.get("sourceSpriteFrameUuid") is None and not expected_needs_binding:
                errors.append(f"Creator Sprite has null source frame without binding-needed proof: {sid}")
            elif expected_needs_binding and expected.get("sourceSpriteFrameUuid") is not None:
                errors.append(f"Creator Sprite has unresolved nonempty source SpriteFrame reference: {sid}")
            if expected.get("sourceTextureBound") is not (expected.get("sourceSpriteFrameUuid") is not None):
                errors.append(f"Creator Sprite source texture identity/bound flag differs: {sid}")
            if expected.get("sourceActive") is True and expected.get("sourceEnabled") is True:
                expected_reason = "null-sprite-frame" if expected_needs_binding else None
                if expected_reason is None or expected.get("noDrawReason") != expected_reason:
                    errors.append(f"Creator active no-draw Sprite reason conflicts with binding policy: {sid}")
            elif expected.get("sourceActive") is False and expected.get("noDrawReason") != "inactive-source":
                errors.append(f"Creator inactive Sprite no-draw reason differs: {sid}")
            elif expected.get("sourceActive") is True and expected.get("sourceEnabled") is False and expected.get("noDrawReason") != "disabled-source":
                errors.append(f"Creator disabled Sprite no-draw reason differs: {sid}")
            if expected_needs_binding:
                if source_frame_asset_id is not None or native_image_uuid is not None:
                    errors.append(f"Creator null-frame Sprite carries a nonnull target asset identity: {sid}")
            else:
                if not isinstance(source_frame_asset_id, str) or not source_frame_asset_id or not isinstance(native_image_uuid, str) or not native_image_uuid:
                    errors.append(f"Creator bound Sprite image asset identity is missing: {sid}")
                else:
                    matches = [asset for asset in creator_assets or [] if isinstance(asset, dict) and asset.get("sourceId") == source_frame_asset_id]
                    if (len(matches) != 1 or matches[0].get("kind") != "sprite" or
                            matches[0].get("uuid") != native_image_uuid or
                            not isinstance(matches[0].get("spriteFrameUuid"), str) or
                            re.fullmatch(r"[a-f0-9-]{36}@[a-f0-9]+", matches[0].get("spriteFrameUuid", "")) is None):
                        errors.append(f"Creator saved ImageAsset/SpriteFrame identity mapping differs: {sid}")
                    else:
                        expected_native_frame = matches[0]["spriteFrameUuid"]
        elif expected_needs_binding is not False:
            errors.append(f"Creator non-Sprite carries a Sprite binding policy: {sid}")
        elif source_frame_asset_id is not None or native_image_uuid is not None:
            errors.append(f"Creator non-Sprite carries a native SpriteFrame expectation: {sid}")
        if (row.get("sourceId") != sid or row.get("nativeId") != expected.get("nativeId") or
                row.get("node") != expected.get("node") or row.get("sourceType") != expected.get("sourceType") or
                row.get("expectedNativeType") != expected.get("expectedNativeType") or
                row.get("actualNativeType") != expected.get("expectedNativeType") or
                row.get("sourceEnabled") is not expected.get("sourceEnabled") or
                row.get("sourceActive") is not expected.get("sourceActive") or
                row.get("sourceNeedsSpriteBinding") is not expected_needs_binding or
                row.get("sourceSpriteFrameAssetId") != source_frame_asset_id or
                row.get("nativeSpriteImageUuidExpected") != native_image_uuid or
                row.get("nativeSpriteFrameUuidExpected") != expected_native_frame or
                row.get("nativeEnabledExpected") is not expected_enabled or
                row.get("componentEnabled") is not expected_enabled or
                row.get("nodeActive") is not source_nodes.get(expected.get("node")) or
                row.get("effectiveActive") is not expected.get("sourceActive") or
                row.get("noDrawReason") != expected.get("noDrawReason") or row.get("verified") is not True):
            errors.append(f"Creator non-draw source identity/activity/reason differs: {sid}")
        component_uuid = row.get("componentUuid")
        if not isinstance(component_uuid, str) or not component_uuid or component_uuid in component_ids:
            errors.append(f"Creator non-draw native component UUID missing or duplicated: {sid}")
        else:
            component_ids.add(component_uuid)
        fields_json = expected.get("sourceFieldsJson")
        fields_hash = expected.get("sourceFieldsSha256")
        try:
            parsed_fields = json.loads(fields_json) if isinstance(fields_json, str) else None
            canonical = json.dumps(parsed_fields, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        except (ValueError, TypeError):
            parsed_fields, canonical = None, None
        if (not isinstance(parsed_fields, dict) or parsed_fields != expected.get("sourceFields") or
                canonical != fields_json or not isinstance(fields_hash, str) or
                hashlib.sha256(fields_json.encode("utf-8")).hexdigest() != fields_hash or
                row.get("sourceFieldsJson") != fields_json or row.get("sourceFieldsSha256") != fields_hash):
            errors.append(f"Creator non-draw serialized source fields/hash differ: {sid}")
        if (row.get("sourceSpriteFrameUuid") != expected.get("sourceSpriteFrameUuid") or
                row.get("sourceNeedsSpriteBinding") is not expected_needs_binding or
                row.get("sourceText") != expected.get("sourceText") or
                row.get("nativeTextExpectation") != expected.get("nativeTextExpectation") or
                row.get("sourceTextEmpty") != expected.get("sourceTextEmpty") or
                row.get("sourceFontId") != expected.get("sourceFontId") or
                row.get("nativeFontAssetId") != expected.get("nativeFontAssetId") or
                row.get("nativeFallbackAssetIds") != expected.get("nativeFallbackAssetIds") or
                row.get("targetSystemFontFamily") != expected.get("targetSystemFontFamily") or
                row.get("creatorMarkup") != expected.get("creatorMarkup")):
            errors.append(f"Creator non-draw source/target text or font contract differs: {sid}")
        if source_type == "cc.Sprite":
            frame = row.get("nativeSpriteFrameUuid")
            if expected_needs_binding and frame is not None:
                errors.append(f"Creator Sprite needing source binding gained a native SpriteFrame: {sid}")
            if not expected_needs_binding and frame != expected_native_frame:
                errors.append(f"Creator native SpriteFrame does not match exact resolved source asset: {sid}")
        if expected.get("sourceType") in ("cc.Label", "cc.RichText"):
            if row.get("actualText") != expected.get("nativeTextExpectation", expected.get("sourceText")):
                errors.append(f"Creator non-draw actual text differs from native projection: {sid}")
            if expected.get("noDrawReason") == "empty-text" and expected.get("sourceTextEmpty") is not True:
                errors.append(f"Creator empty-text reason has nonempty source proof: {sid}")
        if expected.get("sourceType") == "cc.Graphics":
            if (expected.get("initialCommandStreamEmpty") is not True or row.get("initialCommandStreamEmpty") is not True or
                    expected.get("sourceDrawingCommands") != "not-serialized-empty-in-fixed-state" or
                    row.get("sourceDrawingCommands") != expected.get("sourceDrawingCommands") or
                    row.get("sourceMaterialIds") != expected.get("sourceMaterialIds") or
                    row.get("graphicsPathCount") != 0 or row.get("nativeMaterialVerified") is not True or
                    row.get("nativeMaterialUuid") != "f0416e68-0200-4b77-a926-4f9d16e494da" or
                    row.get("nativeEffectUuid") != "1c02ae6f-4492-4915-b8f8-7492a3b1e4cd"):
                errors.append(f"Creator empty Graphics material/command proof differs: {sid}")
    return errors


def _creator_projection_errors(spec, actual, creator_assets=None):
    errors = []
    original = spec.get("sourceOriginalDrawEvents")
    proxy_events = spec.get("sourceDrawEvents")
    renderer_rows = spec.get("renderers")
    non_draw_rows = spec.get("nonDrawRenderers")
    mapping_rows = spec.get("sourceNonDrawRenderers")
    if not all(isinstance(value, list) for value in (original, proxy_events, renderer_rows, non_draw_rows, mapping_rows)):
        return ["Creator source queue projection contract is incomplete"]
    if actual.get("sourceOriginalDrawEvents") != original:
        errors.append("Creator actual original source event sequence differs")
    if actual.get("sourceQueueProjectionVerified") is not True:
        errors.append("Creator source queue projection flag is false")

    drawable = {}
    for row in renderer_rows:
        if not isinstance(row, dict) or not isinstance(row.get("sourceComponentId"), str):
            errors.append("Creator drawable renderer spec is malformed")
            continue
        sid = row["sourceComponentId"]
        if sid in drawable:
            errors.append(f"Creator drawable renderer source ID repeats: {sid}")
        drawable[sid] = row
    non_draw = {}
    for row in non_draw_rows:
        if not isinstance(row, dict) or not isinstance(row.get("sourceId"), str):
            errors.append("Creator non-draw renderer spec is malformed")
            continue
        sid = row["sourceId"]
        if sid in non_draw or sid in drawable:
            errors.append(f"Creator draw/non-draw source ID repeats: {sid}")
        non_draw[sid] = row

    event_indices = {}
    for index, event in enumerate(original):
        if (not isinstance(event, dict) or event.get("kind") not in ("renderer", "maskEnter", "maskExit") or
                not isinstance(event.get("node"), str)):
            errors.append(f"Creator original source event is malformed at {index}")
            continue
        if event["kind"] != "renderer":
            continue
        sid = event.get("sourceComponentId")
        if not isinstance(sid, str) or sid in event_indices:
            errors.append(f"Creator original renderer event source ID is missing/duplicated at {index}")
            continue
        event_indices[sid] = (index, event["node"])
        drawable_row, non_draw_row = drawable.get(sid), non_draw.get(sid)
        if (drawable_row is None) == (non_draw_row is None):
            errors.append(f"Creator original renderer event is not mapped exactly once: {sid}")
        elif drawable_row is not None and drawable_row.get("node") != event["node"]:
            errors.append(f"Creator drawable renderer event node differs: {sid}")
        elif non_draw_row is not None and non_draw_row.get("node") != event["node"]:
            errors.append(f"Creator non-draw renderer event node differs: {sid}")
    for sid, row in drawable.items():
        if sid not in event_indices:
            errors.append(f"Creator drawable renderer is absent from original queue: {sid}")

    expected_proxy_events = [event for event in original if not (
        isinstance(event, dict) and event.get("kind") == "renderer" and event.get("sourceComponentId") in non_draw)]
    if proxy_events != expected_proxy_events:
        errors.append("Creator proxy event stream is not the exact original drawable projection")

    expected_mappings = {}
    for sid, row in non_draw.items():
        source_event = event_indices.get(sid)
        expected_mappings[sid] = {"sourceComponentId": sid, "node": row.get("node"),
            "disposition": "source-render-event" if source_event else "source-component-only",
            "sourceEventIndex": source_event[0] if source_event else None,
            "noDrawReason": row.get("noDrawReason")}
    planned_mappings = {}
    for mapping in mapping_rows:
        if not isinstance(mapping, dict) or not isinstance(mapping.get("sourceComponentId"), str):
            errors.append("Creator source non-draw mapping is malformed")
            continue
        sid = mapping["sourceComponentId"]
        if sid in planned_mappings:
            errors.append(f"Creator source non-draw mapping repeats source ID: {sid}")
        planned_mappings[sid] = mapping
    if set(planned_mappings) != set(non_draw):
        errors.append("Creator planned non-draw mapping denominator differs")
    for sid, expected in expected_mappings.items():
        row = planned_mappings.get(sid)
        if (not isinstance(row, dict) or any(row.get(key) != value for key, value in expected.items())):
            errors.append(f"Creator planned non-draw index/node/reason differs: {sid}")

    actual_mappings = actual.get("sourceNonDrawSourceMappings")
    if not isinstance(actual_mappings, list) or len(actual_mappings) != len(expected_mappings):
        errors.append("Creator actual non-draw mapping count differs")
    else:
        observed = {}
        for row in actual_mappings:
            if not isinstance(row, dict) or not isinstance(row.get("sourceComponentId"), str):
                errors.append("Creator actual non-draw mapping row is malformed")
                continue
            sid = row["sourceComponentId"]
            if sid in observed:
                errors.append(f"Creator actual non-draw mapping repeats source ID: {sid}")
            observed[sid] = row
        if set(observed) != set(expected_mappings):
            errors.append("Creator actual non-draw mapping denominator differs")
        for sid, expected in expected_mappings.items():
            row = observed.get(sid)
            if (not isinstance(row, dict) or any(row.get(key) != value for key, value in expected.items()) or
                    row.get("verified") is not True):
                errors.append(f"Creator actual non-draw index/node/reason differs: {sid}")
    errors.extend(_creator_non_draw_errors(spec, actual, creator_assets))
    return errors


def verify(plan: dict, result: dict):
    """Return diagnostics from actual persistent and initialized queue rows.

    ``plan`` is the frozen Unity import plan. ``result`` is the Editor
    readback object (or its decoded JSON mapping); truthy aggregate flags are
    never sufficient without typed per-source rows.
    """
    queues = plan.get("staticSortQueue") or []
    if not queues:
        return []
    owner_by_id = {prefab.get("sourceId"): prefab for prefab in plan.get("sourcePrefabs", [])
                   if isinstance(prefab, dict)}
    rows = result.get("sourcePrefabs") if isinstance(result, dict) else None
    actual_by_id = {row.get("sourceId"): row for row in rows or [] if isinstance(row, dict)}
    diagnostics = []
    if len(actual_by_id) != len(rows or []):
        return [_diag("staticSortQueue", "Source Prefab rows are malformed or duplicated")]
    queue_by_prefab = {}
    for spec in queues:
        if not isinstance(spec, dict):
            diagnostics.append(_diag("staticSortQueue", "Queue specification is malformed"))
            continue
        owner = spec.get("sourcePrefabId")
        queue_by_prefab.setdefault(owner, []).append(spec)
    for source_id, specs in queue_by_prefab.items():
        prefab = owner_by_id.get(source_id)
        if prefab is None:
            diagnostics.append(_diag(str(source_id), "Queue references unknown source Prefab"))
            continue
        observed = actual_by_id.get(source_id)
        if observed is None:
            diagnostics.append(_diag(source_id, "Source Prefab queue readback is absent"))
            continue
        binding = observed.get("staticSortFields")
        if not isinstance(binding, dict) or binding.get("sourcePrefabId") != source_id or binding.get("prefabPath") != prefab.get("path"):
            diagnostics.append(_diag(source_id, "Static sort Prefab binding identity differs"))
            continue
        if binding.get("verified") is not True:
            diagnostics.append(_diag(source_id, "Static sort aggregate verification failed"))
        for mode, key in (("persistent", "persistentAsset"), ("loaded", "loadedInstance")):
            actual = binding.get(key)
            if not isinstance(actual, list) or len(actual) != len(specs):
                diagnostics.append(_diag(source_id, f"{mode} queue scope count differs"))
                continue
            by_root = {row.get("rootScope"): row for row in actual if isinstance(row, dict)}
            expected_roots = {spec.get("rootScope") for spec in specs}
            if len(by_root) != len(actual) or set(by_root) != expected_roots:
                diagnostics.append(_diag(source_id, f"{mode} queue scopes are missing, extra, or duplicated"))
                continue
            for spec in specs:
                root = spec.get("rootScope")
                errors = _check_queue(spec, by_root[root], source_id, mode, plan)
                diagnostics.extend(_diag(source_id, f"{root}: {message}") for message in errors)
    return diagnostics


def verify_creator(plan: dict, saved: dict):
    """Verify Creator persistent/initialized static sort rows when wired by the Editor bridge."""
    queues = plan.get("staticSortQueue") or []
    if not queues:
        return []
    prefabs = {row.get("sourceId"): row for row in plan.get("sourcePrefabs", []) if isinstance(row, dict)}
    actual_rows = saved.get("sourcePrefabs") if isinstance(saved, dict) else None
    actual_prefabs = {row.get("sourceId"): row for row in actual_rows or [] if isinstance(row, dict)}
    diagnostics = []
    creator_assets = saved.get("assets") if isinstance(saved, dict) else None
    if creator_assets is not None:
        if not isinstance(creator_assets, list) or any(not isinstance(asset, dict) for asset in creator_assets):
            diagnostics.append(_diag("staticSortQueue", "Creator saved asset identity rows are malformed"))
            creator_assets = []
        elif len({asset.get("sourceId") for asset in creator_assets}) != len(creator_assets):
            diagnostics.append(_diag("staticSortQueue", "Creator saved asset source IDs are duplicated"))
    if len(actual_prefabs) != len(actual_rows or []):
        return [_diag("staticSortQueue", "Creator source Prefab rows are malformed or duplicated")]
    for spec in queues:
        owner = spec.get("sourcePrefabId") if isinstance(spec, dict) else None
        source_prefab = prefabs.get(owner)
        observed = actual_prefabs.get(owner)
        if source_prefab is None or observed is None:
            diagnostics.append(_diag(str(owner), "Creator sort queue source Prefab is missing"))
            continue
        binding = observed.get("staticSortQueue") or observed.get("staticSortFields")
        if not isinstance(binding, dict):
            diagnostics.append(_diag(owner, "Creator static sort Prefab binding identity differs"))
            continue
        if observed.get("path") != source_prefab.get("path") and binding.get("prefabPath") != source_prefab.get("path"):
            diagnostics.append(_diag(owner, "Creator static sort Prefab path differs"))
            continue
        if "persistent" in binding or "initialized" in binding:
            mode_rows = (("persistent", [binding.get("persistent")]),
                         ("loaded", [binding.get("initialized")]))
        else:
            mode_rows = (("persistent", binding.get("persistentAsset")),
                         ("loaded", binding.get("loadedInstance")))
        expected_root_scope = spec.get("rootScope")
        for mode, rows in mode_rows:
            presentation = "persistent" if mode == "persistent" else "initialized"
            if not isinstance(rows, list) or len(rows) != 1:
                diagnostics.append(_diag(owner, f"Creator {mode} queue scope count differs"))
                continue
            row = rows[0]
            if (not isinstance(row, dict) or row.get("rootScope") != expected_root_scope or
                    row.get("presentationMode") != presentation or row.get("verified") is not True):
                diagnostics.append(_diag(owner, f"Creator {mode} queue readback identity or mode differs"))
                continue
            if row.get("sourceTreePreserved") is not True or row.get("sourceFieldsPreserved") is not True or row.get("sourceSortRootsPreserved") is not True:
                diagnostics.append(_diag(owner, f"Creator {mode} source tree/fields are not verified"))
            if row.get("rootScope") != spec.get("rootScope"):
                diagnostics.append(_diag(owner, f"Creator {mode} queue identity differs"))
            diagnostics.extend(_diag(owner, f"Creator {mode}: {error}")
                               for error in _creator_projection_errors(spec, row, creator_assets))
            expected_orders = spec.get("sourceSortOrderFields", [])
            actual_orders = row.get("sourceSortOrderFields")
            if not isinstance(actual_orders, list) or len(actual_orders) != len(expected_orders):
                diagnostics.append(_diag(owner, f"Creator {mode} SortOrder row count differs"))
            else:
                for expected, actual in zip(expected_orders, actual_orders):
                    if (not isinstance(actual, dict) or actual.get("expectedSourceId") != expected.get("sourceId") or
                            actual.get("sourceId") != expected.get("sourceId") or
                            actual.get("expectedNativeId") != expected.get("nativeId") or
                            actual.get("nativeId") != expected.get("nativeId") or actual.get("node") != expected.get("node") or
                            actual.get("sourceSortOrder") != expected.get("sortOrder") or
                            actual.get("effectiveSourceSortOrder") != (expected.get("sortOrder") if expected.get("enabled") else 0) or
                            actual.get("enabledInSource") is not expected.get("enabled") or
                            actual.get("renderedOnNode") is not False or actual.get("verified") is not True or
                            actual.get("nativeClass") != "MonkeyStaticSortOrderField" or
                            not isinstance(actual.get("componentUuid"), str) or not actual.get("componentUuid")):
                        diagnostics.append(_diag(owner, f"Creator {mode} SortOrder typed field differs"))
            expected_sort_roots = spec.get("sourceSortRoots", [])
            actual_roots = row.get("sourceSortRoots")
            if not isinstance(actual_roots, list) or len(actual_roots) != len(expected_sort_roots):
                diagnostics.append(_diag(owner, f"Creator {mode} SortRoot row count differs"))
            else:
                for expected, actual in zip(expected_sort_roots, actual_roots):
                    if (not isinstance(actual, dict) or actual.get("expectedSourceId") != expected.get("sourceId") or
                            actual.get("sourceId") != expected.get("sourceId") or
                            actual.get("expectedNativeId") != expected.get("nativeId") or
                            actual.get("nativeId") != expected.get("nativeId") or actual.get("node") != expected.get("node") or
                            actual.get("enabledInSource") is not expected.get("enabled") or
                            actual.get("verified") is not True or actual.get("nativeClass") != "CreatorStaticSortRootField" or
                            not isinstance(actual.get("componentUuid"), str) or not actual.get("componentUuid")):
                        diagnostics.append(_diag(owner, f"Creator {mode} SortRoot typed field differs"))
            expected_graphics = spec.get("renderers", [])
            actual_graphics = row.get("graphics")
            if not isinstance(actual_graphics, list) or len(actual_graphics) != len(expected_graphics):
                diagnostics.append(_diag(owner, f"Creator {mode} renderer evidence count differs"))
            else:
                for expected, actual in zip(expected_graphics, actual_graphics):
                    if (not isinstance(actual, dict) or actual.get("sourceComponentId") != expected.get("sourceComponentId") or
                            actual.get("sourceNode") != expected.get("node") or actual.get("verified") is not True or
                            not actual.get("sourceFingerprint") or actual.get("sourceFingerprint") != actual.get("proxyFingerprint") or
                            actual.get("opacityVerified") is not True or actual.get("originalLayer") != actual.get("proxyLayer")):
                        diagnostics.append(_diag(owner, f"Creator {mode} renderer evidence differs"))
            expected_masks = spec.get("masks", [])
            actual_masks = row.get("masks")
            if not isinstance(actual_masks, list) or len(actual_masks) != len(expected_masks):
                diagnostics.append(_diag(owner, f"Creator {mode} mask evidence count differs"))
            else:
                for expected, actual in zip(expected_masks, actual_masks):
                    if (not isinstance(actual, dict) or actual.get("sourceId") != expected.get("sourceId") or
                            actual.get("sourceNode") != expected.get("node") or
                            actual.get("sourceMaskType") != expected.get("maskType") or
                            actual.get("inverted") is not expected.get("inverted") or
                            actual.get("enabled") is not expected.get("enabled") or
                            actual.get("alphaThreshold") != expected.get("alphaThreshold") or
                            actual.get("transformVerified") is not True or actual.get("opacityVerified") is not True or
                            actual.get("verified") is not True):
                        diagnostics.append(_diag(owner, f"Creator {mode} mask evidence differs"))
            if presentation == "persistent" and row.get("sourceLayersPreserved") is not True:
                diagnostics.append(_diag(owner, "Creator persistent source layer snapshot differs"))
            if presentation == "initialized" and (row.get("sourceSuppressed") is not True or row.get("nestedProxyRootsDisabled") is not True):
                diagnostics.append(_diag(owner, "Creator initialized source suppression evidence differs"))
            if row.get("drawSequenceVerified") is not True:
                diagnostics.append(_diag(owner, f"Creator {mode} draw sequence is not verified"))
    return diagnostics
