# monkey v0.7.0 — complete core Prefab recovery

Development version: **0.7.0.dev1**. Formal 0.6.0 and fixed local consumer packages remain unchanged. This is the active plan; the prior status below is historical.

## Acceptance and current work

Freeze all 13 proposed core Prefabs against original source identities, resources and code. At least 10 distinct core Prefabs must pass both Creator 3.8.8 and Unity 6000.6.2f1: source-to-IR completeness, target native hierarchy/components/fields/references, static images/text/materials/layout in a source-evidenced fixed state, save/reopen and deterministic regeneration. Business scripts may be disabled, not run or partial, with all source fields and references retained. Dynamic behavior and physical input are a separate second phase. Unknown components remain in the source denominator. No acceptance by file counts or zero MissingScript alone.

A is original source/version evidence; B is the frozen pre-v0.7 pure monkey output; C is v0.7 pure output; D is the manually repaired game, used only for locating differences. Game repair scripts must not participate in B/C. Original server gaps remain explicit in the dynamic phase; they do not block independently proven static acceptance. Private source and sample receipts stay outside public artifacts.

Execution order: freeze source identities and baseline; implement independent component/field/reference/event accounting; fix shared source and target semantics; close static component/field/resource bindings; run isolated native/static-render/save-reopen/regeneration checks for each sample. Then extend dynamic scripts/events and input independently. Shared IR and targets have one primary writer. Reuse beaver for applicable native operations; coordinate Editor ownership before execution.

Current: all 13 source anchors are mapped; one instance variant retains an explicit base/override distinction. Original package bytes independently confirm the recovered code bundle and its version literal. Independent node/component/field accounting is integrated into normalization. The initial eleven-core baseline contains 627 nodes, 935 components and 181 custom occurrences (51 classes); these are not the larger dependency-closure totals.

Native subset import/save/reopen has run in both editors. Eleven Creator and four Unity source-bound local behavior components are emitted with unresolved semantics retained. Sixteen selected Spine resources pass Creator resource-reference and observed bone-motion probes; this is not yet Prefab component or visual acceptance. Unity native save/reopen now verifies 928 source nodes across 22 closure Prefabs, separately accounting for 68 TMP-generated nonpersistent submeshes. Source-pinned static fallback and DynamicOS fonts survive Editor exit with zero file-hash diagnostics; this is native subset evidence, not full core acceptance. Exact UI-color material references pass Creator native readback. User-provided visual references cover order states, shop scroll positions, avatar, handbook, goose details and construction; the user explicitly permits cross-version references, with versions recorded separately. Static component/field/resource binding and visual comparison remain incomplete. Static accepted samples: 0/13 on each target; dynamic accepted samples: 0/13; versionComplete=false. Source-family/CDN expansion including 3.8.5 is deferred. Only the explicitly authorized development-branch push is permitted; no formal release, global install or game writes.

## Static-first convergence

First-phase exit: at least ten of the existing thirteen core Prefabs pass on both targets. Record source_identity, hierarchy, components_fields, asset_references, static_render, save_reopen and regenerate independently for every sample and target. All seven must pass; dynamic_behavior and physical_input remain separate. Never replace the core denominator with dependency closure counts.

Preserve all source components through native mappings or generated typed serializable field/reference carriers with business behavior disabled. Empty fieldless shells and zero MissingScript counts do not prove completeness. Carriers must be derived from source declarations, not game-specific templates. Distinguish serialized defaults from source-evidenced display states; missing display evidence remains unverified for the affected sample.

Reuse unchanged source freeze, font/material and 928-node native evidence. GuideTalk asynchronous typing, animation and close lifecycle no longer block the first static result. Select representative cores by available static evidence and close their real graphics render, save/reopen and regeneration gaps in bounded groups.

Visual collection previously used Unity Null graphics, producing invalid gray PNGs. Native import has an explicit `--render-preview` option; capture rejects Null devices. Isolated previews activate only the root on a disposable clone and disclose that scope. Actual rendering is evidence to compare, not automatic visual acceptance. Reference versions remain explicit; cross-version screenshots are not same-version pixel proof.

## Generality requirement

The production recovery path must derive business behavior from source parsing and AST/IR lowering, not select handwritten game-specific templates by source hash, UUID or class name. Source hashes bind evidence and reuse; they are not business implementation selectors. Project-specific WeekTask and Goose WIP has been preserved privately and removed from the production package and public test suite. It is reference analysis only and contributes no complete acceptance.

The same production entry point must be tested with renamed symbols/UUIDs/paths, changed sorting and thresholds, and an independent neutral source example. Generated behavior must follow the changed source. Unsupported semantics remain partial. Existing finite known-behavior adapters require a separate scope audit and must not be reported as general JavaScript conversion. Native font/layout/material/resource fixes continue independently; the ten-core dual-target goal is unchanged.

## Historical pre-v0.7 status

# monkey release and implementation status

Current version: **0.6.0**. This release consolidates the native recovery branch and the source-toolkit branch on `main`; older implementation branches are preserved in history. Retired formatting/engine-emulation code is not revived by consolidation.

## Implemented scope

- Source-format parsing, resource acquisition with exact identities, project manifests and ownership-aware candidate export.
- Large-project parse budgets, stage reuse and explicit missing-source classification.
- Complete-source C# draft emission, source-linked diagnostics, optional bounded postprocessing, and a five-layer native architecture workflow.
- Serial module execution, exact checkpoint recovery, inherited-member evidence, immutable reassembly and pinned candidate revisions.
- Seven received source-side toolkit commands with compatible IDs, arguments, reports and exit codes.

## Evidence boundaries

A representative private candidate with 1,555 C# files compiled across all five actual assemblies with no errors and 3,249 warnings. An affected native core integration passed source-coordinate, 24 Sprite identity, 348-cell rendering, production/persistence/reopen and out-of-viewport rejection checks. Private source material and raw identity logs are excluded from public Git and distribution artifacts. These are historical scoped observations, not a publicly reproduced full-game acceptance.

Partial/unreviewed logic, unavailable original-server behavior and source gaps remain explicit. Physical input, original visual comparison, complete gameplay and Player builds are not implied. Two Editor Search startup exceptions remain recorded in the private evidence.

## Formal release

- Package, CLI and public metadata use 0.6.0.
- Preserve MIT and required third-party attribution, stable compatibility/API identifiers and public download URLs.
- Review the exact staged tree and distributions for private material before publishing `v0.6.0`.
- Verify remote main/tag/Release state and downloaded artifact hashes.
- Coordinate global installation through the designated integration owner; repository release work does not concurrently uninstall or replace shared installations.

Detailed public contracts remain in the adjacent documentation. Private coordination, source evidence and pre-redaction originals are retained outside the release tree.

## Bounded local maintenance

The active local branch addresses one received Unity 2021.3 SpriteAtlas resource subset: exact packing-bit interpretation, original float geometry and UVs, explicit DDS/DXT5 cache hydration, and ordered native Sprite identity readback. Original inputs remain immutable; candidate assets and raw evidence stay outside Git. The formal 0.6.0 release and global installation are not modified. Completion requires the affected source-to-native mapping and precise unsupported-case diagnostics, not another full-game export.

The affected resource subset passed Unity 6000.6.2f1 import/save/reopen: 29 ordered Sprite references, original float32 vertices and triangle topology, actual GUID/localFileID readback and exact native texture pixels. A separately bound source SpriteAtlas confirmed the packing/UV interpretation. A minimal native-asset closure and frame mapping are retained privately for consumer adoption. Game runtime wiring, visual parity and gameplay remain unverified by this maintenance. See [bounded atlas contract](providers/UNITY-ATLAS-SUBSET.md) for limits and importer policy.

A follow-up local resource request found two additional frozen leaf-Prefab closures outside the supplied dependency pool. Their bound source atlases contain 35 and 34 frames and require the narrow FlipHorizontal/Rotate180 settings (69/77), now interpreted as reflections about the serialized atlas rectangle. Source-control vertex/topology checks are exact; the existing UV arithmetic tolerance is unchanged. Independent candidate generation reuses the same DDS/profile chain without repeating the full input pool. Both candidates passed native import/save/reopen, all 69 ordered Sprite identities and exact texture pixel readback; the 38 focused tests also passed. The minimal consumer closure has 69 Sprites, two textures and their metadata, with original field order and per-frame mappings. Native consumer handoff remains separate from game runtime integration and publication.

Another local hydration extension accepts frozen literal cache buckets and an optional source-SHA/file/pathID/raw-SHA/logical-path selection manifest. It atomically hydrates a bounded explicit Texture2D set while retaining all unselected bytes and reporting unprocessed textures as deferred. A partial derivative remains nonzero CLI status and cannot imply whole-container success. Private synthetic two-texture UnityFS cases exercise the real pinned UnityPy/ASTC/DDS workers with 256x512 pixels in bucket 256; consumer source/native acceptance is still separate. See [exact texture selection](providers/UNITY-TEXTURE-SELECTION.md). No formal release or shared installation is replaced.

The follow-up selected PNG outlet now bypasses the whole-container exporter entirely: it binds the original, selected derivative, selector and externally pinned hydration receipt, independently checks unselected bytes and selected RGBA pixels, and emits only PNG candidates with provenance/importer-intent metadata. Partial container state is retained, no native GUID/import is claimed, and the consumer owns controlled adoption. A synthetic 225-texture case covers one exported texture with 224 deferred keys without deleting or decoding those unrelated objects.

## Local P0 Shader evidence handoff

The approved P0 adds a content-first Shader classifier and `classify-unity-shaders` for existing frozen candidates. `monkey-shader-handoff/1` separates recognizable source candidates, platform-compiled data, recovered binary evidence, unknown content and unsupported asset kinds. Native compilation remains `not_run`; source-text only requests source review. New recovery inventories carry explicit Shader hold/review dispositions, without removing referenced evidence or changing legacy exported-file counts into runtime approval.

The bounded existing-candidate check classified 126 serialized platform-compiled Shaders and one unsupported variant collection, hashing about 5.5 MB of Shader/meta content rather than rerunning the full pool. All 127 target identities are serialized declarations, not native readback. The old source map lacks original object associations for the 126 Shaders; these remain explicitly unmapped, with no name-based ID or raw hash inference. A neutral consumer-contract check is accepted by beaver's read-only planner and remains blocked for unproven dynamic runtime use; it is not Editor or isolation-execution evidence.

The fixed candidate, game project, shared installation and formal release are unchanged. beaver owns actual build target/pipeline, dependency coverage, native identities/compilation and any reversible filtering; game-directory migration remains with its owner. No P1 parser/recovery expansion is included. Public schema/example/CLI and limitations are in [Shader handoff](providers/UNITY-SHADER-HANDOFF.md).
