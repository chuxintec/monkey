# Typed GREA格式化首个子集（v0.2开发中）

```sh
monkey format-project --project unimported-creator-candidate --profile grea --preview --out fresh-preview
monkey format-project --project unimported-creator-candidate --plan fresh-preview/format-plan.json --out fresh-formatted
```

当前只有未导入、归属明确、使用新typed output-path导入器的Creator候选。默认未格式化导出、Unity格式器、公开convert的`--format none|grea`编排及已导入资产的native move adapter仍在开发，不能声称整组v0.2格式要求已完成。legacy game-standard-v1、Library/已导入、未知文件/人工漂移拒绝；不在原工程就地移动。

按真实类型将资源放assets/content/images/sprites、fonts、config/recovered、animations、prefabs，Scene放assets/scenes，已证明的Label脚本放assets/scripts/presentation/ui、状态类放domain/state。不创造没有职责的空框架。只改ProjectModel资产路径槽、明确代码artifact/meta、source-map/name-map目标字段、handoff生成目标与导入器outputPaths；SourceId/UUID/原名/正文/逻辑key/数值资源原字节保持。BMFont只从明确font→atlas关系重发单page字段，不重写glyph数值。

Preview包含input manifest/各文件hash/owner、typed路径、资源身份、物理移动和编辑字段。Apply重新生成计划并逐项比较，算法/输入/所有权不同即stale；再次核源文件，输出到fresh目录。大小写/Unicode/路径冲突、人工meta/资源改动、JS脚本meta尚未验证等不静默跳过。纯数值JSON测试保留1.2500、-0.0和恰含旧路径的加载字符串原字节，不做任意JSON/代码全局prefix替换。

## 真实MainUi none/grea对照

- none candidate05：SHA71a110e66437afc0c69b844be0b5d11ba70b3a8ae04afb83fee74fcc8cd7f896；grea01：SHAdcfc2a92581c5fa2298a33b98e79ff6e53186e65dce704979c4ec2ffaee300e2。94目标路径变化、184物理文件移动。
- none native02 own72833：2026-10-23T19:42:33.598898Z→19:42:51.032834Z；grea native01 own73175：19:43:25.973864Z→19:43:43.423979Z。两者正常TERM/reaped、Creator3.8.8 editor pass/0诊断。
- 91资源UUID及75 SpriteFrame身份、原字体页、129源节点几何、同5原NumberLabel组件/数值子集/Scene及独立Prefab保存重载全部保持。脚本固定UUIDd70c6943-490a-5b7b-bf8a-ca7b490ad126、实际classId d70c6lDSQpbe7+KyntJCtEm两模式相同。
- 输入没有物化Prefab/节点的native身份，本次仅此前已分配的资源/脚本ID纳入身份保持。fresh导入MainUi Prefab UUID分别09ecace9-6934-4d09-bc3d-956794e27e9d和1f486368-acee-4b13-a702-7a636cbd5310；不能写成全GUID/局部ID保持。已有native对象迁移仍需要asset database move机制后另验。

原SHRINK动态行为、4个复杂代码方法、原版视觉/输入/玩法均没有因此晋级。实际比较在outputs/number-label-format-comparison-01/comparison.json（私有、不发行）。
