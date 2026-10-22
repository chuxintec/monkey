# monkey

Python 驱动的离线 Cocos 资源解析与原生工程候选工具。当前为 **0.1.0.dev1 本地开发候选**，没有发布。

已实现两条明确的 2.4.15 输入路径：编辑器工程 JSON/meta，以及发布 bundle 的 compiled-v1/pack-v1/texture-pack-v1。工具不执行源脚本，不自动翻译业务、不恢复服务器、不模拟源引擎运行时。

当前可运行 `catalog / inspect / normalize / plan / export / verify / handoff`。可生成 Unity 6000.6.2f1、uGUI 2.0.0 的资源、Editor 导入指令和原生 View 引用脚本；**实际 Editor 导入/保存回读、原版画面对照与业务均尚未执行**。Cocos 3.8.8 输出和增量 apply 仍为计划项。

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
- [首批离线验证](docs/validation/2026-10-22-offline.md)
- [架构合同](docs/ARCHITECTURE.md)、[原实施方案](docs/IMPLEMENTATION.md)
- [算法与依赖来源](docs/PROVENANCE.md)

私有真实输入和样本只在 `.private/`，候选在 `outputs/`，均被 Git 忽略；GREA 和肥鹅工程保持只读。源身份与转换 IR 仅存在离线 Analysis/Editor 指令中，Player 只使用原生 Unity 对象和 UI 引用。
