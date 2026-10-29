# Source-bound Prefab recovery (development)

The v0.7 development pipeline preserves original node and component identities and reports unsupported fields and behaviors. An exported project or successful native import does not mean complete Prefab recovery.

## Independent accounting

`normalize --manifest <source-manifest.json> --out <fresh-stage>` writes `prefab-completeness.json`. It compares selected source declarations with the IR, including inline components. Missing identities, mismatched fields, unsupported semantics and unverified fields are separate outcomes. The dependency closure can be larger than the selected core set; its counts must not replace the core denominator.

## Serialized custom fields

Normalization also writes `prefab-static-fields.json` for supported source graphs. Each custom component retains its exact serialized fields and source node/component/asset references in `staticFieldSnapshot`. Invalid or ambiguous references remain explicit diagnostics. This record is conversion-time evidence, not a runtime source-engine interpreter or a native component binding.

For an existing frozen normalized stage, use:

```sh
monkey prefab-static-fields --manifest <inspect/source-manifest.json> --ir <normalize/ir.json> --out <fresh-stage>
```

The command verifies both stage owners and their source-manifest identity, copies unchanged resources with hash checks, and writes a new IR. It does not re-extract the original package or run source scripts. Both target planners retain these records; native convertibility is unchanged. Script declaration defaults, target field carriers, native reference assignment and persistence still require separate verification. `behaviorPolicy=disabled` describes the intended static carrier policy, not evidence that an existing native script has been disabled.

`prefab_static_acceptance.evaluate_static_acceptance` evaluates a supplied fixed sample matrix, with configurable sample count and threshold. A pass requires seven explicit criterion statuses and evidence IDs; rendering also requires source/reference versions and a declared scope/difference list for cross-version comparisons. It validates the evidence declarations, not the referenced artifacts themselves. Dynamic behavior is recorded independently.

## Reviewed local behaviors

`prefab-behavior-ir --manifest <source-manifest.json> --ir <ir.json> --source-bundle <original.js> --expected-source-bundle <sha256> --out <fresh-stage>` creates an independent derived IR stage. Source JavaScript is parsed, never executed. Reviewed templates require exact code-region identities, serialized field validation and any enclosing-scope proof required by their rule. Unrecognized code remains unsupported.

Pass the derived `ir.json` to the ordinary `plan` command, then pass `plan.json` to `export`. Unity scripts are emitted under `Assets/Game/Scripts/Presentation/Recovered/`; Creator scripts under `assets/Game/Scripts/Presentation/Recovered/`. Hash changes, path collisions and missing providers block the affected binding. Native components retain source IDs and typed field specifications. A `lowered_with_gaps` component is never promoted to complete runtime recovery by import success.

## System fonts

Creator preserves an original system-font request separately from an explicit Font asset reference. Unity may consume an explicitly pinned local resolution receipt using `plan --system-font-resolution <receipt.json> --expected-system-font-resolution <sha256>`. Both arguments are required together; they apply only to Unity. The receipt must match the current IR and source identity, requested family, label text and observed glyph coverage.

The Editor must actually resolve each declared native face, create and persist the TMP assets and verify required glyphs. Platform font resolution does not prove original-platform typography or future dynamic text coverage. A missing face blocks that binding; the importer must not silently replace it with a default font. Source font bytes are not bundled by this option.

## Acceptance

For every core Prefab and target, independently record source identity, hierarchy, component/field preservation, resource readback, source-evidenced fixed-state rendering, save/reopen and regeneration. All seven must pass for static acceptance. Business behavior may be disabled, not run or partial; fields and references must still be preserved. Dynamic events, animation, changing layouts and physical input are a separate second phase. Resource-only probes prove only their stated resource scope. Partial code, unavailable server behavior and missing original-state evidence remain explicit. No publication or game-project adoption is performed by these stages.

## Native diagnostic rendering

`native-import --render-preview` enables a real Unity graphics device in the bounded independent copy. Default headless import keeps graphics disabled; screenshot capture explicitly reports unavailable on a Null device. Per-source Prefab diagnostic images use disposable isolated clones with only root visibility enabled. Source child states and business behavior are not repaired or executed by this preview, so rendering is separate from runtime and visual acceptance.
