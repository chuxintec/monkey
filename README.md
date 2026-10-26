# monkey

[MIT 开源许可](LICENSE) · [GitHub](https://github.com/chuxintec/monkey) · [v0.4.0 Release](https://github.com/chuxintec/monkey/releases/tag/v0.4.0)

当前版本为 **0.4.0**，采用 [monkey-project/1 工程规范](docs/PROJECT-SPEC.md)。新增 Unity 字体/引用表分块读取和可配置解析预算，详见 [解析预算](docs/providers/UNITY-PARSE-BUDGETS.md) 和 [v0.4.0 发布说明](docs/RELEASE-v0.4.0.md)。资源候选、原生导入、画面及业务验收分别记录。

新输出直接生成规范目录；`--format none|grea` 保留为弃用兼容参数。`convert --layout layout.json` 可使用游戏级命名覆盖；`layout-preview` 预览已完成转换的路径变化，`layout-migration` 按 GUID/UUID 生成旧候选到新候选的迁移清单。进度和未验证项见 [PLAN](docs/PLAN.md)，用法见 [USAGE](docs/USAGE.md)。

开发版现在默认将中文输出路径转为拼音，保留源名映射、同音消歧和资源 GUID；肥鹅 BON 配置自动逐表导出 JSON，入口为目标工程 `Docs/CONFIGURATION.md`。这些功能包含在本版 wheel 中。

开发版`convert --numeric-code-contract numeric.json`可在同一命令里发现精确源模块、生成有据C#/默认TypeScript，再格式化。现有Label数值调用子域支持原组件绑定；新增静态数值方法子集按调用合同生成独立工具类。声明格式和分层验证见[CODE-SUBSET](docs/CODE-SUBSET.md)，未知业务方法继续保留待补。

Python 驱动的原包恢复工程命令行工具。产品目标：Cocos各版本原包→Unity6/Cocos3.8.8/both；Unity、Laya/LayaAir、Egret、自研及其他引擎原包→Unity6。按来源逐步实现；结构化reader当前覆盖已验证的Cocos2.4.15子集，开发分支新增Cocos2.4.11、2.1.2/3.8.7资源子集、Unity显式Bundle/WebData来源，以及其他引擎原图gallery出口（原节点/方法范围见支持矩阵）。wxapkg/APK/已取得资源集合一键生成独立工程，含全部输入资源、恢复源码与目标代码初稿，交给AI继续开发。当前正式版本为 [`v0.4.0`](https://github.com/chuxintec/monkey/releases/tag/v0.4.0)，仍非所有引擎与版本全兼容。具体恢复范围见 [支持矩阵](docs/SUPPORT-MATRIX.md)。


本版完成向僵尸开炮 601 容器的全量导出与内容核查，补齐所有缺失 GUID 统计及精确纹理的无损 PNG 输出。核验范围和已知源缺件见 [本版验收](docs/validation/2026-10-25-zombie-release.md)。
## 安装与依赖

Python 3.11+。从 [GitHub Release](https://github.com/chuxintec/monkey/releases/tag/v0.4.0) 下载 wheel、`SHA256SUMS` 与安装脚本，核对哈希后安装：

```sh
python3 install_release.py --wheel monkey_native-0.4.0-py3-none-any.whl --sha256 <SHA256SUMS中的wheel哈希>
monkey --version
monkey capabilities --json
```

唯一日常入口为 `~/.local/bin/monkey`，需将 `~/.local/bin` 加入 PATH。版本隔离在 `~/.local/share/monkey/releases/`，`current` 只在安装校验成功后切换。仓库 `bin/monkey` 也转发到此 Release，不回退运行源码。显式开发使用 `.venv/bin/python -m monkey.cli`。

基础依赖固定 Pillow 12.2.0、pypinyin 0.55.0，安装脚本同时安装 ASTC extra（texture2ddecoder 1.0.6），不修改系统 Python。JS 静态解析需要已安装 Node.js；Acorn 和许可证随包提供。Unity 来源完整导出需已有 UnityPy 与 AssetRipper，使用明确 provider 路径；原生导入需 Unity 6000.6.2f1 或 Creator 3.8.8。编辑器、provider 和游戏原件不随工具发行。

## 一条命令转换

```sh
bin/monkey convert --source /path/to/game.wxapkg --target both --out outputs/my-game
bin/monkey convert --source /path/to/game.apk --target unity6 --out outputs/my-unity
bin/monkey convert --source /path/to/cocos-resources --target cocos38 --out outputs/my-creator
```

其他引擎的开发版原图出口（仅图片gallery，原节点/图集/方法待adapter）：

```sh
bin/monkey convert --source-family egret --source /path/to/decrypted.wxapkg --target unity6 --out outputs/images
```

具体范围见[支持矩阵](docs/SUPPORT-MATRIX.md)、[旧Cocos资源](docs/providers/COCOS-LEGACY.md)和[通用图片出口](docs/providers/GENERIC-IMAGES.md)。不能把资源候选或派生gallery当完整游戏转换成功。

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

Creator的静态显示尺寸策略会保留源节点烘焙尺寸：Label以原生CLAMP呈现，缓存尺寸与SpriteFrame不一致的Sprite使用CUSTOM；原overflow/sizeMode和自动尺寸行为待适配项同时保留。几何回读通过不等于源自动尺寸行为或原版文字画面通过。Unity的网格使用原生GridLayoutGroup的小型优先级扩展，仍由uGUI计算行列，Player不解释源节点图。

已有2.4.15切片转换链继续可用：`--target unity|cocos`、`--asset-index`/recipe，结果在`project/`；其完成候选支持`--resume`身份续验。包级工程支持按哈希校验续跑并归档原候选；人工修改会阻止覆盖。`convert --native`接续原生阶段；已有冻结候选也可单独使用`native-import`，固定manifest/工程/期限，实际保存后回读。人工业务代码增量合并未实现。详见[命令说明](docs/USAGE.md)。

已实现两条明确的 2.4.15 输入路径：编辑器工程 JSON/meta，以及发布 bundle 的 compiled-v1/pack-v1/texture-pack-v1。工具不执行源脚本，代码初稿不代表业务语义已恢复，不伪造服务器、不模拟源引擎运行时。

当前可运行 `convert / catalog / inspect / normalize / plan / export / verify / handoff / diff / register / apply / preflight / native-import`。Unity 6000.6.2f1/uGUI 2.6.0与Creator 3.8.8均已用真实3源图/76节点代表样本完成原字体、3独立Prefab和Scene保存重载、几何与引用核对；Unity另有8个Label字形核对及编辑保存重开。full14单命令已完成两端各1694独立Prefab、24784节点的保存重开及完整几何/引用强回读，差异诊断均为0；Unity保留源行为缺口为partial，Creator原生资源层pass。详见[全量实际回执](docs/validation/2026-10-24-full14-single-command.md)。代表样本不等于所有来源版本、原版画面或游戏业务通过。已实现登记生成区的差异预览和expected-manifest受控apply，人工区保持独立，移除项保留而不自动删除。

## 源码开发（显式使用开发环境）

```sh
python3 -m venv .venv
.venv/bin/python -m pip install --index-url https://pypi.org/simple -e '.[astc]'
.venv/bin/monkey capabilities --json
.venv/bin/python scripts/demo.py --out outputs/demo-new
.venv/bin/python -m unittest discover -s tests -v
```

Python 最低 3.11，本次实际验证为 macOS arm64 / Python 3.14.7。Pillow 固定 12.2.0，pypinyin 固定 0.55.0；ASTC 是可选、固定版本的 texture2ddecoder 1.0.6，不安装该 extra 时会输出 dependency_missing。不修改系统 Python，不调用模型服务。

合成 demo 会创建图集、来源索引、规范化图像、Unity 候选和静态报告，不含原游戏文件。`--ui` 另演示缺失字体和待处理组件，结果应为 partial。已有目录一律拒绝覆盖。

- [实际进度与下一步](docs/PLAN.md)
- [命令、支持矩阵与边界](docs/USAGE.md)
- [首批离线验证](docs/validation/2026-10-22-offline.md)、[首屏字体/UI续包](docs/validation/2026-10-22-reward-font-ui.md)
- [架构合同](docs/ARCHITECTURE.md)、[原实施方案](docs/IMPLEMENTATION.md)
- [算法与依赖来源](docs/PROVENANCE.md)

私有真实输入和样本只在 `.private/`，候选在 `outputs/`，均被 Git 忽略；GREA 和肥鹅工程保持只读。源身份与转换 IR 仅存在离线 Analysis/Editor 指令中，Player 只使用原生 Unity 对象和 UI 引用。

### 双端资源目录与完整性（2026-10-25）

`--target both` 共用 sourceId 与命名规则：Unity 为 `Assets/Game/Content/<Type>/<Module>/`，Creator 为 `assets/resources/<Type>/<Module>/`。目录统一 PascalCase，中文路径转拼音；源包与采集容器只留台账。详情见 [PROJECT-SPEC](docs/PROJECT-SPEC.md) 和 [USAGE](docs/USAGE.md)。

正式资源区包含已解析音频、完整纹理、SpriteFrame 图片、Spine 数据闭包与 Shader 来源代码，原件仍保留于 SourceRecovery。Scene/Prefab/Animation 由原生导入阶段生成。Shader 源文件、Spine 数据与原生渲染/播放分别验收；本轮不配置远端分组或构建。

图片统一使用 `Textures/<Module>/`，不再生成 Sprites 目录。保留 Sprite 导入设置与引用；仅合并字节一致且无独立绑定要求的附加完整纹理，尺寸/裁切不同的图片不强行删除。`resource-catalog.json` 记录纹理别名；Spine/字体页图仍留在对应闭包旁。

## 许可

monkey 自有代码采用 [MIT License](LICENSE)，适用于本仓库及已发布版本中的自有代码。第三方代码保留各自版权和许可，见 [THIRD-PARTY-NOTICES](THIRD-PARTY-NOTICES.md)。游戏原包、素材、引擎和第三方工具不属于本项目的开源授权内容，也不随发行包提供。v0.4.0 已发布包保持原哈希，MIT LICENSE 作为该 Release 的独立附件提供；后续构建自动携带根许可证及 MIT 包元数据。
