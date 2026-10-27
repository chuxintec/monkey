# Native M4A AudioClip support

`normalize()` has an opt-in-by-input, optional-provider adapter for the narrow Cocos case `cc.AudioClip` with an exact native `.m4a` path. It decodes to PCM16 WAV during conversion; it does not add an audio runtime or change the target Player. Other audio formats retain their previous byte-copy behavior. Other native kinds and unsupported extensions remain unsupported.

The decoder is in `monkey.assets.audio.decode_m4a(raw, provider=None, ...)`. With no explicit executable it discovers `ffmpeg` from `PATH`; `normalize()` accepts the same optional override as `audio_provider`. The resolved executable path, version line, byte count, and SHA-256 are pinned in each normalized asset record. The decoder passes file paths as argv elements without a shell, limits ffmpeg input protocols to local `file`, and never interprets or executes source JavaScript.

The bounded contract is: input at most 8 MiB (callers cannot raise this hard limit), WAV output at most 16 MiB, decode timeout at most 120 seconds (30 seconds by default), version probe at most 5 seconds, and provider executable at most 256 MiB. A child file-size limit plus ffmpeg's `-fs` output cap and a parent-side size monitor stop oversized output, including on hosts without `RLIMIT_FSIZE`. Reaching the cap is an error; a truncated or partial WAV is never accepted. The decoder pins the input demuxer to `mov` for this M4A-only path. The returned bytes must be a structurally complete RIFF/WAVE PCM16 stream with consistent chunk sizes, channel/rate/alignment values, and non-empty frames. The owned ffmpeg child is killed and reaped in a `finally` path on timeout, I/O failure, or interruption. Invalid input, missing ffmpeg, failed decode, timeout, output limit, invalid WAV, or invalid provider remain diagnostics; no WAV asset is emitted on those paths, and the source remains in `SourceRecovery`.

Successful normalizer records include the source bundle/path, logical key, source byte count and SHA, provider identity, output byte count and SHA, container/codec, channel count, sample rate, bit depth, frame count, and measured duration. The generated `cc.AudioClip` asset has a `.wav` suffix, so the existing Unity planner and exporter allocate and copy it as an audio asset.

## Frozen07 evidence

The actual pinned source is `FullDraftCandidate07/UnityProject/SourceRecovery/Original/original/cdn/remote/miniGameRes/native/63/63310199-382b-5e30-b8da-9ba0daf2d48a.f8696.m4a`, 46,239 bytes, SHA-256 `7b3a20a92bec17f6652289c60820ef03d2cdecd6517bf841331d4d03bbc76cec`. The frozen source maps identify `miniGameRes:63310199-382b-5e30-b8da-9ba0daf2d48a` as `cc.AudioClip`, logical key `Texture/garden/resources/audio/fireworks`, and the exact importer/native files. Their mapping pins and source row are recorded in `.private/v060-architecture-first-20261027/NativeM4aDecode01/Revision04/receipt.json`.

On the installed provider `/opt/homebrew/Cellar/ffmpeg/9.0.1_1/bin/ffmpeg`, version `9.0.1`, SHA-256 `9f5ddd4f8b36eb07b0c5d60ab6ea1e618bedd70bc45feab82b4dc23be1596ad1`, public `normalize → Unity plan → export` produced `Assets/Game/Content/Audio/Sfx/MiniGames/Garden/Common/fireworks.wav`. The WAV is PCM16, stereo, 44,100 Hz, 120,878 frames / 2.7409977 seconds, 483,590 bytes, SHA-256 `6e088bebda4142fb535d12244e36dd2ef89c609b0f38d3c8149d3e0c56f8dbe8`. The same bytes are preserved as the independent derived file `NativeM4aDecode01/Revision04/derived/fireworks.wav`.

The public pipeline and provider were exercised without launching Unity. This proves the static resource conversion and export path only; Unity import, playback, audible quality, looping, and runtime references remain unverified. The original frozen input was hash-checked after conversion and remains untouched.

## Tests

`tests/test_audio_decode.py` covers missing provider, hard input-budget rejection, decode failure, output truncation with `resource` unavailable, invalid WAV, timeout and keyboard-interrupt child cleanup, normalizer source retention, and generated M4A flowing through public normalize/plan/export. The generated test audio is an independent fixture, not game code.
