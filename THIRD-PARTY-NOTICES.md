# Third-party notices

monkey distributes independent Python implementations adapted from GREA and the vendored Acorn parser. Their MIT license texts are included in `src/monkey/licenses/` in the source distribution and `monkey/licenses/` in the wheel:

- GREA adaptations: `GREA-MIT.txt`.
- Acorn 8.15.0: `ACORN-MIT.txt`.

Pillow12.2.0 is an external runtime dependency; texture2ddecoder1.0.6 is optional. Their distributions supply their own license texts. Node.js, Unity and Cocos Creator are external tools and are not bundled.

No private game source/assets, editor binaries or AssetDeoce implementation are distributed. References to the user's AssetDeoce tool describe independently implemented behavior and do not assert that the private repository is MIT licensed. Exact algorithm origins, hashes and limitations are recorded in `docs/PROVENANCE.md`.


## Cocos engine Layout geometry reference

NativeFlowLayoutGroup uses the version-audited row-extent recurrence from Cocos engine v3.8.7 under its MIT license; no source runtime is embedded. Source: https://github.com/cocos/cocos-engine/blob/v3.8.7/cocos/ui/layout.ts . Copyright and license are preserved in src/monkey/licenses/cocos-layout-mit.txt. Older engine files are read-only behavioral references and are not bundled or executed.
