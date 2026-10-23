# monkey

Python 驱动的原包恢复工程命令行工具。产品目标：Cocos各版本原包→Unity6/Cocos3.8.8/both；Unity、Laya/LayaAir、Egret、自研及其他引擎原包→Unity6。按来源逐步实现，当前结构化reader仍限已验证的Cocos2.4.15子集。wxapkg/APK/已取得资源集合一键生成独立工程，含全部输入资源、恢复源码与目标代码初稿，交给AI继续开发。当前为 **0.3.0.dev1 本地开发候选**，没有发布。

## 一条命令转换

```sh
bin/monkey convert --source /path/to/game.wxapkg --target both --out outputs/my-game
bin/monkey convert --source /path/to/game.apk --target unity6 --out outputs/my-unity
bin/monkey convert --source /path/to/cocos-resources --target cocos38 --out outputs/my-creator
```

包含原生导入的单命令（使用已安装的编辑器，默认仅转换时不启动）：

```sh
bin/monkey convert --source /path/to/game.wxapkg --target both --out outputs/my-game \
  --native --unity-editor /path/to/Unity --creator-editor /path/to/CocosCreator
```

按Unity→Creator顺序在`outputs/my-game-native/`的新副本中运行，每段最多30分钟、方法默认1200秒；未退出、原生错误或回读差异会停止后续段。单目标只提供对应编辑器参数。`--native-out`可指定另一个全新目录；不能与`--offline`混用。候选、原生核对与游戏业务分别记录，仍有源组件/业务缺口时退出码保持1。

已有明确CDN/远程包清单时，可将获取并入同一命令：

```sh
bin/monkey convert --input-set inputs.json --remote-manifest downloads.json \
  --remote-cache-root /path/to/read-only-cache --target both --out outputs/game
```

清单包含`url`、相对`path`及可选的`sha256`/`bytes`。匹配原输入的缓存只读复用，新文件在独立`outputs/game-acquired/`下载并接入输入；404、哈希冲突和预算结束各有回执。也可再加`--native`及对应Editor参数。当前按明确清单获取，尚未从所有原包自动发现全部CDN地址；未知地址仍列缺口。

当前已接入明文wxapkg、APK和资源目录的全文件盘点；输出`UnityProject/`、`CocosProject/`（单目标只生成对应项），两工程分别自包含。原包所有文件按原生可复制、去重映射、原格式待转、代码证据、明确运行时排除分类，报告为`conversion-result.json`。未知资源/不可编译初稿在`SourceRecovery/`，源UUID、逻辑键、代码候选和AI模块任务在`Analysis/`；每个工程含`AGENTS.md`与`Docs/START-HERE.md`。

可恢复资源优先保留原Cocos路径与名称，GUID/UUID只作身份；派生变体、真实冲突或无名回退另有明确映射。见`Analysis/*name-map.json`。

多个已取得的资源目录可在一个本地清单中声明，避免遗漏分包或混入其他版本：

```sh
bin/monkey convert --input-set inputs.json --target unity6 --out outputs/my-unity
bin/monkey convert --resume outputs/my-unity --input-set inputs.json
```

`inputs.json`指定`schemaVersion: 1`、`sourceProfile: "cocos-2.4.15-bundle"`和`inputs`数组，
每项包含`id`、本地`path`、相对`config`。可声明游戏身份与冻结来源回执；身份冲突在输出前拒绝。
续跑校验原输入快照、生成文件与阶段清单；旧工程归档在`Previous/`。实际原生Scene/Prefab仍需目标编辑器导入保存。

静态AST支持有限literal loader/System.register和RF区域候选；恢复的源代码＋TS/C#合同初稿不等于业务已转译。Node为静态解析所需宿主，Acorn8.15.0已固定并随包提供，不执行输入JS。没有Node或格式未支持时保留完整源文件并报告缺口。

**当前是全输入留存＋受支持对象的原生工程候选，尚未完成全对象及游戏业务转换**。已接入2.4.15共享IR：支持的节点图、SpriteFrame、字体及JsonAsset生成原生导入计划；未知组件及Spine运行时接入等保留证据和缺口。默认返回needs_action，`--offline`为partial，退出码1；不能当完整转换成功。CDN支持明确清单获取，未声明或获取失败的远程分包仍保留缺口。

已有2.4.15切片转换链继续可用：`--target unity|cocos`、`--asset-index`/recipe，结果在`project/`；其完成候选支持`--resume`身份续验。包级工程支持按哈希校验续跑并归档原候选；人工修改会阻止覆盖。`convert --native`接续原生阶段；已有冻结候选也可单独使用`native-import`，固定manifest/工程/期限，实际保存后回读。人工业务代码增量合并未实现。详见[命令说明](docs/USAGE.md)。

已实现两条明确的 2.4.15 输入路径：编辑器工程 JSON/meta，以及发布 bundle 的 compiled-v1/pack-v1/texture-pack-v1。工具不执行源脚本，代码初稿不代表业务语义已恢复，不伪造服务器、不模拟源引擎运行时。

当前可运行 `convert / catalog / inspect / normalize / plan / export / verify / handoff / diff / register / apply / preflight / native-import`。Unity 6000.6.2f1/uGUI 2.6.0与Creator 3.8.8均已用真实3源图/76节点代表样本完成原字体、3独立Prefab和Scene保存重载、几何与引用核对；Unity另有8个Label字形核对及编辑保存重开。全量Unity先前保存过1694 Prefab，仍有原生差异，新全量复验进行中；Creator全量尚未通过。代表样本不等于所有来源版本、原版画面或游戏业务通过。已实现登记生成区的差异预览和expected-manifest受控apply，人工区保持独立，移除项保留而不自动删除。

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
