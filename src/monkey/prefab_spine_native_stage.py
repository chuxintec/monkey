"""Attach and emit the evidence-pinned Unity Spine native stage.

The ordinary target planner remains engine-agnostic.  This module adds the
already-validated Spine native factory payload to a completed Unity target
plan and materializes it beside the target's normal export files.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .io import inside, read, sha, write_json
from .sources.compiled import fail


CONTRACT = "monkey-spine-native-stage/1"
NATIVE_CONTRACT = "monkey-spine-native-binding/1"
EMISSION_CONTRACT = "monkey-spine-emission/1"
MATERIAL_PROFILE = "cocos24-builtin-spine-material-v1"
_HELPERS = (
    ("targets/spine/UnitySpineBinding.cs", "Assets/Game/Editor/Conversion/Spine/UnitySpineBinding.cs"),
    ("targets/materials/spine/UnitySpineMaterialBindings.cs", "Assets/Game/Editor/Conversion/Spine/UnitySpineMaterialBindings.cs"),
    ("targets/spine/UnitySpineNativeFactory.cs", "Assets/Game/Editor/Conversion/Spine/UnitySpineNativeFactory.cs"),
    ("targets/spine/UnitySpineNativeStage.cs", "Assets/Game/Editor/Conversion/Spine/UnitySpineNativeStage.cs"),
    ("targets/spine/UnitySpineImporterIntegration.cs", "Assets/Game/Editor/Conversion/Spine/UnitySpineImporterIntegration.cs"),
    ("targets/spine/UnitySpineSourceIdentity.cs", "Assets/Game/Scripts/Presentation/Recovered/Spine/UnitySpineSourceIdentity.cs"),
)


class SpineNativeStageError(ValueError):
    """A frozen input does not satisfy the native Spine stage contract."""


def _document(path: str | Path) -> tuple[dict, bytes]:
    path = Path(path).resolve(strict=True)
    raw = read(path, max_bytes=128 * 1024 * 1024)
    try:
        result = json.loads(raw.decode("utf-8-sig"), parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    except (UnicodeError, ValueError, json.JSONDecodeError) as error:
        raise SpineNativeStageError(f"invalid JSON document {path}: {error}") from error
    if not isinstance(result, dict):
        raise SpineNativeStageError(f"expected JSON object: {path}")
    return result, raw


def _record(output: Path, source: str | Path, target: str, role: str,
            expected_sha256: str | None = None, expected_bytes: int | None = None) -> dict:
    source_path = Path(source)
    raw = read(source_path, max_bytes=128 * 1024 * 1024)
    digest = sha(raw)
    if expected_sha256 is not None and digest != expected_sha256:
        raise SpineNativeStageError(f"source hash changed for {source_path}")
    if expected_bytes is not None and len(raw) != expected_bytes:
        raise SpineNativeStageError(f"source size changed for {source_path}")
    if not target.startswith("Assets/") or ".." in Path(target).parts:
        raise SpineNativeStageError(f"invalid Unity target path {target!r}")
    relative = f"spine-native-stage-payloads/{digest}/{Path(target).name}"
    payload = inside(output, relative)
    payload.parent.mkdir(parents=True, exist_ok=True)
    if payload.exists():
        if read(payload, max_bytes=128 * 1024 * 1024) != raw:
            raise SpineNativeStageError(f"payload collision at {relative}")
    else:
        payload.write_bytes(raw)
    return {"source": relative, "target": target, "sha256": digest, "bytes": len(raw), "role": role}


def _unity_guid(namespace: str, identity: str) -> str:
    return uuid5_hex(f"monkey/{namespace}/{identity}")


def uuid5_hex(name: str) -> str:
    import uuid
    return uuid.uuid5(uuid.NAMESPACE_URL, name).hex


def _meta_payload(namespace: str, target: str, output: Path, kind: str) -> dict:
    target_meta = target + ".meta"
    guid = _unity_guid(namespace, "spine-native-stage/" + target)
    if kind == "plugin":
        # Match Unity's minimal managed-plugin metadata. An empty platformData
        # list would explicitly disable the DLL on every platform.
        body = "fileFormatVersion: 2\n" + f"guid: {guid}\n"
    elif kind == "shader":
        body = ("fileFormatVersion: 2\n" + f"guid: {guid}\n" +
                "ShaderImporter:\n  externalObjects: {}\n  defaultTextures: []\n"
                "  nonModifiableTextures: []\n  preprocessorOverride: 0\n"
                "  userData: \n  assetBundleName: \n  assetBundleVariant: \n")
    else:
        body = ("fileFormatVersion: 2\n" + f"guid: {guid}\n" +
                "MonoImporter:\n  externalObjects: {}\n  serializedVersion: 2\n"
                "  defaultReferences: []\n  executionOrder: 0\n  icon: {instanceID: 0}\n"
                "  userData: \n  assetBundleName: \n  assetBundleVariant: \n")
    relative = f"spine-native-stage-payloads/generated/{hashlib.sha256(target_meta.encode()).hexdigest()[:16]}.meta"
    payload = inside(output, relative)
    payload.parent.mkdir(parents=True, exist_ok=True)
    raw = body.encode("utf-8")
    payload.write_bytes(raw)
    return {"source": relative, "target": target_meta, "sha256": sha(raw), "bytes": len(raw), "role": "unity-meta"}


def prepare_unity_stage(target_plan: dict, native_plan_path: str | Path,
                        emission_path: str | Path, source_ir_path: str | Path,
                        closure_root: str | Path,
                        closure_freeze_path: str | Path,
                        runtime_evidence_path: str | Path,
                        runtime_stage_evidence_path: str | Path,
                        runtime_stage_root: str | Path, output: str | Path) -> dict:
    """Prepare an attachable stage and its payloads from pinned frozen inputs.

    `output` is the existing target plan directory. The function writes only a
    new `spine-native-stage-payloads/` subdirectory there.
    """
    if not isinstance(target_plan, dict) or target_plan.get("targetProfile") != "unity-6000.6.2f1-ugui":
        raise SpineNativeStageError("a completed Unity target plan is required")
    plan_path = Path(output).resolve()
    if not isinstance(target_plan.get("namespace"), str) or not target_plan["namespace"]:
        raise SpineNativeStageError("target plan namespace is missing")
    native_plan, native_raw = _document(native_plan_path)
    emission, _ = _document(emission_path)
    closure_freeze, closure_freeze_raw = _document(closure_freeze_path)
    runtime_evidence, _ = _document(runtime_evidence_path)
    runtime_stage, _ = _document(runtime_stage_evidence_path)

    if native_plan.get("contract") != NATIVE_CONTRACT or native_plan.get("schemaVersion") != 1:
        raise SpineNativeStageError("unsupported native Spine binding plan")
    if emission.get("contract") != EMISSION_CONTRACT or emission.get("schemaVersion") != 1:
        raise SpineNativeStageError("unsupported Spine emission receipt")
    pins = emission.get("pins", {})
    for key, plan_key in (("sourceManifestSha256", "sourceManifestSha256"), ("normalizedIrSha256", "sourceIrSha256")):
        expected = target_plan.get(plan_key)
        if not isinstance(expected, str) or pins.get(key) != expected or native_plan.get(key) != expected:
            raise SpineNativeStageError(f"target plan/emission/native plan source pin mismatch: {key}")
    if sha(closure_freeze_raw) != pins.get("unityClosureReceiptSha256"):
        raise SpineNativeStageError("Unity closure freeze receipt differs from Spine emission pin")
    manifest_path = target_plan.get("sourceManifestPath")
    if not isinstance(manifest_path, str) or sha(read(Path(manifest_path), max_bytes=128 * 1024 * 1024)) != target_plan["sourceManifestSha256"]:
        raise SpineNativeStageError("source manifest is missing or does not match target plan pin")
    if sha(read(Path(source_ir_path), max_bytes=128 * 1024 * 1024)) != target_plan["sourceIrSha256"]:
        raise SpineNativeStageError("source IR is missing or does not match target plan pin")

    components = native_plan.get("components")
    data_assets = native_plan.get("dataAssets")
    if not isinstance(components, list) or not isinstance(data_assets, list):
        raise SpineNativeStageError("native Spine plan lacks component or data asset arrays")
    target_component_ids = {row.get("sourceId") for row in target_plan.get("components", []) if isinstance(row, dict)}
    target_prefab_ids = {row.get("sourceId") for row in target_plan.get("sourcePrefabs", []) if isinstance(row, dict)}
    for row in components:
        if not isinstance(row, dict) or row.get("sourceComponentId") not in target_component_ids:
            raise SpineNativeStageError("native Spine component is absent from the existing target plan")
        if row.get("sourcePrefabId") not in target_prefab_ids:
            raise SpineNativeStageError("native Spine component source prefab is absent from the target plan")
        if row.get("behavior") != "disabled" or row.get("sourceCallbacksExecuted") is not False:
            raise SpineNativeStageError("Spine source behavior must remain disabled")
    if any(row.get("scale") != 1.0 or row.get("scaleEvidence", {}).get("status") != "verified_source_scale_and_target_unit_mapping"
           for row in data_assets):
        raise SpineNativeStageError("all planned Spine assets need verified scale=1 evidence")
    if len(data_assets) != native_plan.get("dataAssetCount") or len(components) != native_plan.get("componentCount"):
        raise SpineNativeStageError("native Spine plan counts do not match its rows")
    if (native_plan.get("persistentVisiblePose") is not True or
        native_plan.get("visualPolicy") != "native_renderer_enabled_timeScale_zero_source_timeScale_retained" or
        native_plan.get("persistentVisiblePoseEvidence", {}).get("status") != "verified_pinned_spine_unity_3_8_runtime_source" or
        native_plan.get("persistentVisiblePoseEvidence", {}).get("upstreamCommit") != "8b4844bd4b193ba9e54487ed397a777993cbad56" or
        any(row.get("persistentVisiblePose") is not True or row.get("sourceTimeScaleVerified") is not True
            for row in components)):
        raise SpineNativeStageError("persistent visible native pose or original timeScale is not proven")

    if (native_plan.get("sourceMaterialProfile", {}).get("creatorMappingStatus") != "exact_source_builtin_profile_mapping" or
        not native_plan.get("sourceMaterialProfile", {}).get("creatorTargetMaterialUuid")):
        raise SpineNativeStageError("Creator exact built-in Spine material mapping is not proven")

    runtime_profile = runtime_evidence.get("unity", {}).get("spinePlugin", {})
    copied_files = runtime_stage.get("copiedFiles", {})
    if (not runtime_stage.get("verified") or runtime_profile.get("manifestSha256") != runtime_stage.get("sourceManifestSha256") or
        runtime_profile.get("compiledAgainst") != "Unity6000.6.2f1"):
        raise SpineNativeStageError("Unity Spine runtime/license stage is not verified")
    for relative, proof in runtime_profile.get("fileChecks", {}).items():
        staged = copied_files.get(relative, {})
        if not proof.get("verified") or staged.get("verified") is not True or staged.get("sha256") != proof.get("expectedSha256"):
            raise SpineNativeStageError(f"runtime stage file is not hash-verified: {relative}")
    required_runtime = {"spine-csharp.dll", "spine-unity.dll", "Shaders/Spine-SkeletonGraphic.shader", "LICENSE"}
    if not required_runtime.issubset(copied_files):
        raise SpineNativeStageError("runtime stage lacks required DLL/shader/license files")

    closure = Path(closure_root).resolve(strict=True)
    runtime_root = Path(runtime_stage_root).resolve(strict=True)
    if Path(closure_freeze.get("candidatePath", "")).resolve() != closure:
        raise SpineNativeStageError("Unity closure freeze candidate path differs")
    closure_files = {row.get("path"): row for row in closure_freeze.get("files", []) if isinstance(row, dict)}
    closure_report_path = inside(closure, "Analysis/Evidence/spine-closures.json")
    closure_report_pin = closure_files.get("Analysis/Evidence/spine-closures.json", {})
    if sha(read(closure_report_path, max_bytes=128 * 1024 * 1024)) != closure_report_pin.get("sha256"):
        raise SpineNativeStageError("Unity closure report differs from frozen receipt")
    payload_root = inside(plan_path, "spine-native-stage-payloads")
    if payload_root.exists():
        raise SpineNativeStageError("Spine payload staging directory already exists; use a fresh target plan")
    payload_root.mkdir(parents=True)
    copies = []
    seen_targets = set()
    for row in emission.get("copies", []):
        if row.get("target") != "unity":
            continue
        target = row.get("path")
        if target in seen_targets:
            raise SpineNativeStageError(f"duplicate Unity closure target {target}")
        seen_targets.add(target)
        frozen_file = closure_files.get(target)
        if not frozen_file or frozen_file.get("sha256") != row.get("sha256") or frozen_file.get("bytes") != row.get("bytes"):
            raise SpineNativeStageError(f"Unity closure copy is not covered by frozen receipt: {target}")
        copies.append(_record(plan_path, inside(closure, target), target,
                              "source-spine-closure", row.get("sha256"), row.get("bytes")))

    runtime_manifest = runtime_profile.get("path")
    if not isinstance(runtime_manifest, str):
        raise SpineNativeStageError("verified runtime manifest path is missing")
    runtime_manifest_path = Path(runtime_manifest).resolve(strict=True)
    runtime_manifest_raw = read(runtime_manifest_path, max_bytes=128 * 1024 * 1024)
    if sha(runtime_manifest_raw) != runtime_profile.get("manifestSha256"):
        raise SpineNativeStageError("runtime manifest source hash changed")
    stage_manifest_path = inside(runtime_root, "manifest.json")
    if read(stage_manifest_path, max_bytes=128 * 1024 * 1024) != runtime_manifest_raw:
        raise SpineNativeStageError("isolated runtime manifest does not match verified source manifest")
    runtime_target_root = "Assets/Plugins/Spine38"
    copies.append(_record(plan_path, stage_manifest_path, runtime_target_root + "/manifest.json", "runtime-manifest",
                          runtime_profile["manifestSha256"], len(runtime_manifest_raw)))
    for relative, expected in runtime_profile.get("fileChecks", {}).items():
        source = inside(runtime_root, relative)
        target = runtime_target_root + "/" + relative
        record = _record(plan_path, source, target, "verified-runtime-license-or-shader",
                         expected.get("expectedSha256"), expected.get("expectedBytes"))
        copies.append(record)
        if target.endswith(".dll"):
            copies.append(_meta_payload(target_plan["namespace"], target, plan_path, "plugin"))

    native_plan_rel = "Assets/Game/Editor/Conversion/spine-native-binding-plan.json"
    copies.append(_record(plan_path, native_plan_path, native_plan_rel, "native-binding-plan", sha(native_raw), len(native_raw)))
    source_root = Path(__file__).resolve().parent
    for relative, target in _HELPERS:
        source = source_root / relative
        copies.append(_record(plan_path, source, target, "unity-native-spine-helper"))
        copies.append(_meta_payload(target_plan["namespace"], target, plan_path, "script"))

    shader = native_plan.get("unityShader", {})
    shader_source = Path(shader.get("sourcePath", ""))
    if shader.get("sha256") != sha(read(shader_source)):
        raise SpineNativeStageError("Unity source profile shader hash differs from native plan")
    copies.append(_record(plan_path, shader_source, shader.get("targetPath"), "source-profile-shader", shader["sha256"]))
    copies.append(_meta_payload(target_plan["namespace"], shader["targetPath"], plan_path, "shader"))

    # The native-plan file, helpers, DLLs and closure are all explicit in the
    # export plan; callers can attach this object and call emit_unity_stage.
    stage = {
        "schemaVersion": 1,
        "contract": CONTRACT,
        "target": "unity",
        "sourceManifestSha256": native_plan["sourceManifestSha256"],
        "sourceIrSha256": native_plan["normalizedIrSha256"],
        "emissionReceiptSha256": sha(read(Path(emission_path), max_bytes=128 * 1024 * 1024)),
        "nativeBindingPlanSha256": sha(native_raw),
        "nativeBindingPlanPath": native_plan_rel,
        "runtimeManifestSha256": runtime_profile["manifestSha256"],
        "runtimeFilesVerified": len(required_runtime),
        "runtimeLicenseIncluded": True,
        "resolvedSkeletonDataScale": 1.0,
        "persistentVisiblePose": True,
        "visualPolicy": native_plan["visualPolicy"],
        "persistentVisiblePoseEvidence": native_plan["persistentVisiblePoseEvidence"],
        "scaleEvidenceStatus": native_plan["scaleEvidence"]["status"],
        "rendererSelection": "actual target node RectTransform => SkeletonGraphic; otherwise SkeletonAnimation",
        "componentCount": len(components),
        "boundComponentCount": native_plan.get("sourceStaticDataBoundCount"),
        "unboundComponentCount": native_plan.get("sourceStaticDataUnboundCount"),
        "dataAssetCount": len(data_assets),
        "creatorMaterialProfile": native_plan["sourceMaterialProfile"],
        "importHook": [
            "var spinePlan = UnitySpineNativeStage.Parse(File.ReadAllText(\"Assets/Game/Editor/Conversion/spine-native-binding-plan.json\"));",
            "var spineAssets = UnitySpineNativeStage.CreateDataAssets(spinePlan);",
            "var spineComponents = UnitySpineNativeStage.CreateComponents(spinePlan, spineAssets, ResolveSourceNode, currentSourcePrefabId);",
            "SavePrefabAndReopen();",
            "var spineReadback = UnitySpineNativeStage.ReadSaved(spinePlan, ResolveSavedSpineComponent, currentSourcePrefabId);",
        ],
        "copies": copies,
        "nativeImport": "not_run",
        "sourceBehaviorExecuted": False,
    }
    write_json(plan_path / "spine-native-stage.json", stage)
    return stage


def attach_unity_stage(target_plan: dict, stage: dict) -> dict:
    """Attach stage metadata to a completed Unity target plan in memory."""
    if not isinstance(target_plan, dict) or not isinstance(stage, dict) or stage.get("contract") != CONTRACT:
        raise SpineNativeStageError("invalid target plan or Spine native stage")
    if target_plan.get("sourceManifestSha256") != stage.get("sourceManifestSha256") or target_plan.get("sourceIrSha256") != stage.get("sourceIrSha256"):
        raise SpineNativeStageError("stage source pins differ from Unity target plan")
    if target_plan.get("spineNativeStage") is not None:
        raise SpineNativeStageError("Unity target plan already has a Spine native stage")
    target_plan["spineNativeStage"] = stage
    return target_plan


def emit_unity_stage(stage: dict, plan_root: str | Path, output: str | Path) -> dict:
    """Emit verified payload files into a fresh or partially assembled Unity candidate."""
    if not isinstance(stage, dict) or stage.get("contract") != CONTRACT or stage.get("target") != "unity":
        raise SpineNativeStageError("invalid Unity Spine native stage")
    plan_root, output = Path(plan_root).resolve(), Path(output).resolve()
    emitted = []
    seen = set()
    for row in stage.get("copies", []):
        target = row.get("target")
        if target in seen:
            raise SpineNativeStageError(f"duplicate emitted target path {target}")
        seen.add(target)
        raw = read(inside(plan_root, row["source"]), max_bytes=128 * 1024 * 1024)
        if sha(raw) != row.get("sha256") or len(raw) != row.get("bytes"):
            raise SpineNativeStageError(f"staged payload changed: {row.get('source')}")
        dest = inside(output, target)
        if dest.exists():
            if read(dest, max_bytes=128 * 1024 * 1024) != raw:
                raise SpineNativeStageError(f"refuse to replace different existing target file: {target}")
            status = "already_present_identical"
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
            status = "emitted"
        emitted.append({"target": target, "sha256": row["sha256"], "bytes": len(raw), "status": status})
    return {"contract": "monkey-spine-native-stage-emission/1", "fileCount": len(emitted),
            "files": emitted, "componentCount": stage["componentCount"], "dataAssetCount": stage["dataAssetCount"],
            "nativeImport": "not_run"}


def creator_profile_handoff(native_plan: dict) -> dict:
    """Return the exact material-profile assertion consumed by Creator planning.

    Creator assets/components remain emitted by `prefab_spine_pipeline`; this
    helper makes the profile condition explicit to callers sharing the stage.
    """
    profile = native_plan.get("sourceMaterialProfile", {}) if isinstance(native_plan, dict) else {}
    if (profile.get("creatorMappingStatus") != "exact_source_builtin_profile_mapping" or
        not profile.get("sourceReferenceSourceId") or not profile.get("resolvedSourceMaterialId") or
        not profile.get("creatorTargetMaterialUuid")):
        raise SpineNativeStageError("Creator source material does not have an exact built-in profile mapping")
    return {"profile": MATERIAL_PROFILE, "status": profile["creatorMappingStatus"],
            "sourceReferenceSourceId": profile["sourceReferenceSourceId"],
            "resolvedSourceMaterialId": profile["resolvedSourceMaterialId"],
            "targetMaterialUuid": profile["creatorTargetMaterialUuid"],
            "pipeline": "prefab_spine_pipeline.prepare/emit", "sourceScriptsExecuted": False}
