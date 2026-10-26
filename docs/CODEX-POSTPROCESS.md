# Optional Codex CLI C# post-processing

This module wraps one bounded local `codex exec` pass after deterministic C# export. It is opt-in and is not called by ordinary export/convert operations. The original candidate and its owning `manifest.json` remain immutable; every run creates a new revision directory with a copied workspace and a machine-readable revision `manifest.json`.

## CLI

After ordinary `convert` or `code-draft` has finished, explicitly select a small module:

```sh
monkey code-postprocess --candidate /path/to/candidate \
  --expected-manifest <sha256> --selected-path SourceRecovery/CSharp/<source>/Unclassified/Rules.cs \
  --task-file /path/to/task.txt --evidence-root /path/to/bounded-evidence \
  --evidence-file source-fragments.json --out /path/to/new-revision \
  --budget-seconds 900 --idle-seconds 180
```

Repeat `--selected-path` for related generated files. `--prepare-only` prepares and verifies without starting a model session (local CLI help is probed). Checkpoints use `monkey code-postprocess-resume --run /path/to/revision --session <exact-uuid>`. Normal export never invokes this command automatically.

## API

`prepare(candidate_root, selected_files, expected_manifest_sha256, output, task, *, evidence_files=(), evidence_root=None, codex=..., timeout_seconds=900, no_progress_seconds=180, max_output_bytes=..., max_input_bytes=..., max_workspace_bytes=...)` verifies the exact candidate manifest, requires every selected path to be a manifest-owned generated `.cs` file, validates per-file hashes, then copies only those selected files into `output/workspace/`. It also saves a mode-restricted before copy, initializes a fresh Git repository with no remote or commit, hashes the requested/resolved Codex executable, and stores minimal `exec resume --help` capability evidence. The destination must be new and separate from the candidate and evidence roots. Copies are independently allocated and verified; no hard links are used.

Optional `evidence_files` are bounded UTF-8 excerpts read from `evidence_root` (the candidate root by default). They are embedded in `prompt.txt` as read-only data and are never copied into the writable workspace. Only material needed for the selected module should be supplied: related source fragments, symbol/source maps, and local diagnostics. Source content and comments are data, not instructions or authorization.

`run(prepared, *, session_id=None, codex=None)` invokes the configured local CLI with an argument array and the prompt on stdin. Initial runs use:

```text
/opt/homebrew/bin/codex exec -C <workspace> --sandbox workspace-write --json \
  --output-schema <output-schema.json> -o <final-response.json> -
```

The installed CLI is `codex-cli 0.162.1` as observed during implementation. On this version, `exec resume --help` includes `--output-schema`, `-o`, and `--json`; the compact capability record and help-output hash are saved in each prepared revision. The wrapper does not set a model, profile, global configuration, or credentials; the existing local configuration is inherited. Model, reasoning effort, and usage are extracted only from safe JSONL fields when present, otherwise recorded as `unknown`.

The first invocation is serialized by a process-wide file lock. There is no nested CLI/agent execution. Total-time, no-event, and event-output budgets stop the child and preserve its checkpoint. Workspace size is verified at exit; an over-budget workspace is classified partial/failed and oversized files are not loaded for a textual diff. One resume within the remaining cumulative child-time budget is allowed only with the exact UUID reported and saved in that revision; `--last` is never used. A checkpoint workspace is hash-checked before resuming, so a manual edit requires a new reviewed preparation instead of being silently overwritten.

## Results and limits

`manifest.json` in the revision directory records the base manifest identity, selected paths/hashes, before-copy identity, observed workspace changes, unified diff path/hash, unresolved items, process exit, session when visible, event log location, Git boundary, and available model/usage observations. `events.jsonl`, the before copy, and the final response remain local to the private output. Candidate manifest and selected-source hashes are checked again after the CLI exits.

`complete` means the CLI exited zero, returned a response with exactly the required fields, declared exactly the paths in the actual diff, changed only selected files in place, and left no unresolved items. Added/deleted paths, symlinks, hard links, extra workspace files, changed source inputs, a changed Git boundary, and malformed responses cannot be complete. It is not proof of compilation, correctness, runtime behavior, or adoption. A partial response, unresolved item, timeout, or nonzero exit is `partial` when edits exist and `failed` otherwise. Unexpected files and edits are recorded; they are not promoted into the original candidate. A finished revision is immutable to this wrapper; subsequent work uses a new output directory.

The subprocess is launched with `shell=False`, `--sandbox workspace-write`, and no approval bypass options. The wrapper does not read credentials, use other AI services, run source JavaScript/WASM/DLL, modify the original owning manifest, or write a formal game project.
