# 肥鹅资源重新导出 — 2026-10-25

用户删除全部旧 outputs 后，使用 monkey 当前工作树从三处显式输入全新导出。目标 Unity 6000.6.2f1，布局 monkey-project/1.0.0；未改肥鹅游戏工程。

## 本次交付

- 原生工程：`outputs/foodstreet-unity6-native-02/UnityProject`。
- 转换候选与输入台账：`outputs/foodstreet-unity6`。
- 17,201 项原始输入、884,709,704 字节逐项与原件及保留文件比对通过；8,952 张图片尺寸和格式验证通过。
- 914 份唯一代码草稿均存在；它们不是已恢复业务实现。
- Unity 原生回读：24,784 节点、8,952 Sprite、1,694 源 Prefab、416 项支持的源动画；其余动画声明与缺口仍保留。
- Missing Script 0，场景重开与编辑保存回读为 true；子进程退出码 0，静态验证 pass，Editor partial，验证器诊断 0。

## 修复与边界

首轮原生导入在 MiniGames 动画路径守卫处失败：C# 默认支持 Content 根，但 Python 输出配置仍缩窄到 Content/Animations。已修复源工具与本次候选唯一生成配置，27 项定向检查和完整生成文件核验通过后，在新的隔离副本成功完成。配置变更前后清单和失败回执保留在 `.private/foodstreet-reexport-20261025/`。

原台账仍有 1,521 项缺失引用和 16,630 条源限制；Spine 1,776 个文件闭包保留，但原生 Spine 未验。未实现业务、Player 与视觉保真不宣称完成。Missing Script 0 仅指已生成原生对象，不表示未知源组件或方法已恢复。

执行/核验机器回执：`.private/foodstreet-reexport-20261025/delivery.json`、`resource-verification.json`；原生详细回读与核验见原生输出的 `Analysis/Readback` 和上级 `Verification/verification.json`。
