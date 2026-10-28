# Exact Texture2D hydration scope

This is a local, unpublished extension of `hydrate-unity`; the formal 0.6.0 wheel and shared installations are unchanged. Consumers must bind the exact local artifact/implementation fingerprint and check capabilities instead of inferring this extension from `--version`.

## Literal frozen cache paths

Cache entries retain their existing `schemaVersion: 1`, `path`, `logicalPath`, `bytes` and `sha256` contract. `logicalPath` is `Assets/Textures/{astc,dds}/<literal-bucket>/<exact-source-token-key>.txt`. The bucket comes from the frozen source manifest; it is not inferred from `max(width,height)`. A 256×512 texture may therefore legitimately use bucket `256`. The decoder still verifies the actual header dimensions and encoding against the selected Texture2D.

Without selection, the whole-container mode matches exact token filenames within the supplied frozen manifest. Exactly one match is required. Multiple supplied buckets or encodings for one token require an explicit binding; no preferred directory, URL decoding, alias or encoding guess is introduced. A filename index keeps matching bounded by the supplied manifest rather than repeatedly scanning it per texture. Missing required textures continue to block whole-container serialization.

## Explicit selected objects

```sh
monkey hydrate-unity --source <frozen.bundle> \
  --texture-cache <frozen-cache.json> --selection-manifest <selection.json> \
  --provider-python <pinned-provider-python> --out <fresh-output>
```

`selection.json` pins the input bytes and selects 1–256 exact Texture2D objects:

```json
{
  "schemaVersion": 1,
  "sourceSha256": "<exact input SHA-256>",
  "objects": [
    {
      "file": "<exact serialized-file name>",
      "pathId": "<canonical signed-int64 decimal string>",
      "rawSha256": "<exact original object-byte SHA-256>",
      "logicalPath": "Assets/Textures/astc/256/<exact-source-token-key>.txt"
    }
  ]
}
```

The explicit path must appear in the frozen cache manifest, and its filename must equal the object's literal token key plus `.txt`. Object type, file/pathID, raw hash, input hash, cache byte count, cache hash, format/header dimensions and decoded pixel length are verified. A missing/mistyped/stale selected identity or missing/ambiguous binding produces diagnostics; it does not fall back to another object or path. Decoder dependency pins are unchanged.

Selection is an explicit texture set, not an automatic Sprite/Prefab reference graph or a full-project export. Callers obtain IDs from source inspection and supply every Texture2D needed for their intended set. Unselected objects are never deleted or parsed for hydration; each unselected Texture2D is marked `not-selected-not-evaluated`, without claiming it has valid pixels or a missing cache. All unselected and non-texture object bytes must survive serialization exactly. Selected pixel format, dimensions and RGBA SHA are read back from the serialized derivative.

The selected set is atomic: if any selected requirement fails, no derivative is committed. `resolved` may describe staged decoding in an unsuccessful report; `serializationCommitted` and `derivedBundleSha256` determine whether a derivative actually exists. Incomplete early inventories have `inventoryComplete: false`.

## Partial is not whole-container success

When the selected set succeeds but other Texture2D objects are deferred, the report has `status: partial`, `selectionComplete: true`, `wholeContainerComplete: false`, `serializationCommitted: true`, explicit `deferred` entries and a verified `derivedBundle`. CLI exit remains **1** for partial; full `hydrated` is the only exit-0 state. The derivative intentionally retains the unprocessed original objects and placeholders. Consumers may explicitly use the proven selected texture subset, but must not reinterpret this receipt as a complete container or feed it to an all-resources-success gate.

Missing selected data returns `needs_action`; missing required data in default whole-container mode remains `blocked`. Ambiguity and identity drift are diagnosed without writing a derivative. Originals are immutable in every mode. No network acquisition, global installation, native Editor import or original game method execution is performed by this operation.

## Validation boundary

Focused tests cover exact non-square bucket matching, unchanged unreadable neighbors, original/pixel identities, full-container blocking, ambiguous cache paths, explicit-path mismatch, stale selectors and serialization drift. A private synthetic two-Texture2D UnityFS fixture additionally exercises the real UnityPy 1.25.3 worker and pinned DDS/ASTC decoders for 256×512 pixels with a literal `256` bucket. This is provider/serialization evidence, not a claim that a consumer's undisclosed real source input, native project or gameplay has been validated.
