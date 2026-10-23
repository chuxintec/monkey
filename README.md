# monkey

Python 驱动的 Cocos 资源解析与原生工程候选命令行工具。当前为 **0.3.0.dev1 本地开发候选**，没有发布。

## 一条命令转换

```sh
bin/monkey convert --source /path/to/cocos-project --target unity --out outputs/my-unity
bin/monkey convert --source /path/to/cocos-project --target cocos --out outputs/my-creator
```

源工程目前限 Creator 2.4.15；目标为 Unity 6000.6.2f1/uGUI 或 Creator 3.8.8。自动串联检查、解析、规范化、计划、生成、静态验证和交接；工程在输出的 `project/`，总报告为 `manifest.json`。既有目录拒绝覆盖。发布 bundle 需明确选择 `--asset-index` 或 `--all-assets`，可将范围与依赖写入可复用 recipe，详见 [命令说明](docs/USAGE.md)。

**当前单命令自动化完成到候选生成。原生编辑器启动/导入尚未自动编排**；默认返回 `needs_action` 和具体下一动作，退出码 1，不能作为完整转换成功。显式 `--offline` 返回 `partial`。引擎完成原生保存回读后，用同一入口 `bin/monkey convert --resume outputs/my-creator` 校验身份并续验，无需重新解析资源。真实编辑器导入、视觉和业务分别报告。

已实现两条明确的 2.4.15 输入路径：编辑器工程 JSON/meta，以及发布 bundle 的 compiled-v1/pack-v1/texture-pack-v1。工具不执行源脚本，不自动翻译业务、不恢复服务器、不模拟源引擎运行时。

当前可运行 `convert / catalog / inspect / normalize / plan / export / verify / handoff / diff / register / apply`。可生成 Unity 6000.6.2f1、uGUI 2.0.0 的图像、原BitmapFont/源TTF文字、有限布局/按钮/遮罩、Editor 导入指令和原生 View 引用脚本；Unity 实际导入和画面对照尚未执行。Creator 3.8.8 实导已进入资产阶段并发现 package 版本与 Mask 默认赋值问题，修复尚待原生复验；Scene/字体/页面验收未完成。已实现登记生成区的差异预览和 expected-manifest 受控 apply，人工区保持独立，移除项保留而不自动删除。

## 本地使用

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --index-url https://pypi.org/simple -e '.[astc]'
.venv/bin/monkey capabilities --json
.venv/bin/python scripts/demo.py --out outputs/demo-new
.venv/bin/python -m unittest discover -s tests -v
```

Python 最低 3.11，本次实际验证为 macOS arm64 / Python 3.14.7。Pillow 固定 12.2.0；ASTC 是可选、固定版本的 texture2ddecoder 1.0.6，不安装该 extra 时会输出 dependency_missing。没有全局安装、模型调用或网络服务。

合成 demo 会创建图集、来源索引、规范化图像、Unity 候选和静态报告，不含原游戏文件。`--ui` 另演示缺失字体和待处理组件，结果应为 partial。已有目录一律拒绝覆盖。

- [实际进度与下一步](docs/PLAN.md)
- [命令、支持矩阵与边界](docs/USAGE.md)
- [首批离线验证](docs/validation/2026-10-22-offline.md)、[首屏字体/UI续包](docs/validation/2026-10-22-reward-font-ui.md)
- [架构合同](docs/ARCHITECTURE.md)、[原实施方案](docs/IMPLEMENTATION.md)
- [算法与依赖来源](docs/PROVENANCE.md)

私有真实输入和样本只在 `.private/`，候选在 `outputs/`，均被 Git 忽略；GREA 和肥鹅工程保持只读。源身份与转换 IR 仅存在离线 Analysis/Editor 指令中，Player 只使用原生 Unity 对象和 UI 引用。
