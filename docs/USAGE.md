# 一键工程转换

产品目标规则：Cocos全部版本原包可选Unity6/Cocos3.8.8/both；Unity、Laya/LayaAir、Egret、自研与其他引擎全部版本原包仅以Unity6为目标。当前实际解析子集见[支持矩阵](SUPPORT-MATRIX.md)，未接入来源不能据以下命令视为已还原。

在monkey根目录运行，无须逐阶段调用reader或export：

```sh
bin/monkey convert --source /path/to/game.wxapkg --target unity6 --out outputs/game-unity
bin/monkey convert --source /path/to/game.apk --target both --out outputs/game-both
bin/monkey convert --source /path/to/cocos-project --target cocos38 --out outputs/game-creator
```

`UnityProject/`、`CocosProject/`为独立目标工程，`conversion-result.json`说明候选状态和缺口。
结构化支持范围为声明的2.4.15格式；其他格式保留文件证据，不能视为原生还原成功。
输入原件不修改，输出目录必须新建。生成代码合同放在编译排除区，不生成假业务。

多目录使用明确清单，路径相对于该JSON所在目录：

```json
{
  "schemaVersion": 1,
  "sourceProfile": "cocos-2.4.15-bundle",
  "game": {"gameId": "my-game", "engineVersion": "2.4.15"},
  "inputs": [
    {"id": "main", "path": "source/main", "config": "config.json"},
    {"id": "remote", "path": "source/remote", "config": "config.hash.json"}
  ]
}
```

```sh
bin/monkey convert --input-set inputs.json --target both --out outputs/game
bin/monkey convert --resume outputs/game --input-set inputs.json
```

仅扫描列出的本地根。未知appId/version保持未知；已知冲突拒绝。可选`cacheList`与`cacheKind: cache|temp`
读取本地缓存映射，URL仅作身份键，不请求网络。原列表保留，wxfile与物理文件必须在声明根内。
续跑验证清单身份、输入快照和已有工程哈希，拒绝未知/缺失/人工修改文件；原候选归档到`Previous/`。
可校验恢复已有备份的中断运行；没有可信清单的半成品不自动覆盖。结构阶段复用不等于编辑器验收。

静态检查不会启动引擎：

```sh
bin/monkey verify --candidate outputs/game/UnityProject --out outputs/game-unity-check
bin/monkey verify --candidate outputs/game/CocosProject --out outputs/game-creator-check
```

默认`needs_action`与退出码1表示候选生成后仍有待验项；`--offline`显式限定离线候选。
Editor导入、编译、保存重开、画面和业务验收分开记录，目前整包真实Editor验收未完成。

# 当前使用与支持矩阵

结构化对象reader当前声明两种 Cocos **2.4.15 子集**；新增包级全文件盘点与静态代码恢复见下文。不是所有 Cocos 格式的通用原生导入器。

## 发布资源

```sh
.venv/bin/monkey inspect --source /path/to/bundle/config.hash.json \
  --source-profile cocos-2.4.15-bundle --asset-index 123 \
  --dependency-source /path/to/main/config.hash.json --out outputs/inspect-new
.venv/bin/monkey normalize --manifest outputs/inspect-new/source-manifest.json --out outputs/ir-new
.venv/bin/monkey plan --ir outputs/ir-new/ir.json --namespace my-game \
  --target-profile unity-6000.6.2f1-ugui --out outputs/plan-new
.venv/bin/monkey export --plan outputs/plan-new/plan.json --out outputs/unity-new
.venv/bin/monkey verify --candidate outputs/unity-new --level static --out outputs/static-new
.venv/bin/monkey handoff --candidate outputs/unity-new --out outputs/handoff-new
```

`--asset-index` 可重复。索引来自精确版本的 config UUID 表。只读取选择项及引用闭包；共享 pack 只解码选择的 section。依赖 bundle 必须显式提供已有本地 config，不联网找资源。根据版本表读取确切 import/native 文件，不选 glob 第一个。没有版本时只接受确切未版本化文件。

版本依据是用户显式 profile 声明、存在时的 engineVersion 字段、编译 header/shape 校验；发布 config 本身没有完整 Editor 版本证据时不宣称自动识别了版本。未知 header 不猜测升级。

## 可编辑源工程

```sh
.venv/bin/monkey catalog --source /path/to/project \
  --source-profile cocos-2.4.15-project --out outputs/catalog-new
.venv/bin/monkey inspect --source /path/to/project \
  --source-profile cocos-2.4.15-project --asset-index 0 --out outputs/project-inspect-new
```

选择 catalog.json 的 index，后续 normalize/plan/export 相同。要求 project.json/version 严格为 2.4.15，项目有稳定 id 或 name。读取 assets 下 meta 索引、纹理的 sprite-frame subMeta、`.prefab`/`.fire` 对象数组及明确的 native 文件。没有把 compiled reader 套在源工程上。源工程路径仅以合成夹具验证，尚未验真实源工程。

## Unity 导入

用独立、获准资源窗口打开生成候选，执行 `Tools > Monkey > Import Candidate`。独立 batchmode 入口为 `MonkeyImporter.ImportBatch`。工具不会自行启动 Editor；不得拿肥鹅正式 Editor 执行。首次导入使用 AssetDatabase/TextureImporter/PrefabUtility 保存原生资产，不调用全局 SaveAssets；已有生成 Prefab/Scene 则拒绝重复导入。

导入指令和源身份只在 `Assets/Monkey/Editor`。原生 Prefab 位于 `Assets/Generated/Views`，Scene 位于 `Assets/Generated/Scenes`，普通 View 组件仅保留 Image/TMP/Button 引用，不带源节点 ID、业务回调或运行时解释器。导入后移除 Assets/Monkey 仍应可编辑/编译；这项真正 Editor 脱离测试尚未执行。

```sh
.venv/bin/monkey verify --candidate outputs/unity-new --level editor --out outputs/editor-check-new
```

该命令读取导入器保存的 `Analysis/editor-readback.json`，不会启动 Editor。没有回读文件则明确 `EDITOR_NOT_RUN`、退出 1；检查 Sprite border/尺寸/GUID/fileID、节点尺寸/锚点/位置、字体GUID/覆盖、Bitmap字形四角、序列化View引用/fileID、原生编辑/保存/重开克隆、缺脚本及保存文件hash。画面对照和业务仍另行验收。Editor 首次保存的 Prefab/Scene GUID 以真实回读为准，**目前仅资源与脚本 GUID 确定性通过静态验证**。

## 支持边界

| 项目 | 当前结果 |
|---|---|
| UUID/压缩 UUID、短十六进制纹理 key | 已实现，畸形身份诊断、不修补猜测 |
| pack ordinal、import/native 版本、redirect | 已实现；未提供依赖 bundle 记 REDIRECT_UNRESOLVED |
| PNG/JPEG、ASTC 2D | 已实现；ASTC 校验 header、block、长度、像素预算，只有固定可选 provider |
| 旋转/trim/offset/originalSize/capInsets | PNG 语义反例及真实切片已验证；亚像素留白不能无损栅格化则记 SUBPIXEL_TRIM |
| TTF/MP3/WAV/OGG | 资源拷贝路径；TTF 的 TMP 字体创建未实测，不静默替换字体 |
| Node/RectTransform、simple/sliced/tiled Sprite | 已实现 typed IR 与原生 adapter，真实 Editor 未验 |
| Label/BitmapFont | 原RGBA图集、glyph/offset/advance/kerning生成静态TMP字体；目前单行，缩放时存在非零源未缩放kerning则显式拒绝。TTF先做cmap4/12覆盖检查，再为已知文字生成静态TMP；字体度量/描边仍需实际对照 |
| 有限UI子集 | 父级绝对全拉伸Widget；容器resize H/V及均匀水平Grid；矩形非反转Mask；双轴禁用ScrollView；自目标none/scale Button。使用原生组/Animator，不写源布局运行时。复杂/动态子集仍handoff |
| 原空Sprite/点击回调 | 空frame生成禁用Image并保留待绑定项，防止Unity默认白框；原handler只记录，Button没有假回调或默认成功 |
| Animation/Spine、自定义脚本、事件 | 不生成空回调或假业务；交 AI 包 |
| Cocos 3.8.8 输出 | 离线 candidate；Creator 原生导入/画面对照 not_run |
| diff/register/apply | 已实现；默认dry-run，expected-manifest与预览收据保护写入 |

`candidate` 表示本命令的离线范围完成，不表示游戏可玩；`partial` 表示已出报告但存在诊断。退出码 0/1/2 分别为声明范围完成、有待处理诊断、参数/IO/协议错误。所有阶段创建新目录，不覆盖输入、旧候选或人工文件。

计划资源、源文件及候选清单均带 hash。静态 verify 会检测包清单等生成文件的修改；Editor verify 允许引擎生成的 meta，只接受与保存回读匹配的 hash。现有受控apply见下文；仍不支持任意目录同步、自动删除或自动合并人工代码。

## 带依据的动态字体绑定

源Prefab中无Font引用的Label可能由原脚本在加载时选择字体。monkey不执行JS、不自动猜字体。可以显式把已人工核对的冻结脚本作为只读证据，inspect增加`--evidence-source /path/to/frozen/game.js`，并选择实际字体asset索引。plan增加`--bindings /path/to/bindings.json`。

绑定JSON包含`sourceManifestSha256`、已登记的`evidenceSha256`、`offset`/`bytes`及`labelFonts`数组；每项为`component`、`font`稳定sourceId和布尔`syntheticBold`。工具核验文件hash、范围、组件和manifest，但原脚本的选择语义由提供绑定的开发者负责核对。禁止覆盖原来已有的明确Font引用。绑定回执写`Analysis/font-bindings.json`；源manifest和IR若被改动会报STAGE_DOCUMENT_CHANGED，不能直接改中间文件绕过来源。

CONTINUE-01只给原奖励页zh场景的3个系统Label绑定了已取得的zh-bold文件，另2个数量文本使用原BitmapFont。没有绑定时仍报缺口，不换系统字体。Bitmap图集包含原彩色描边，采用TMP Bitmap Custom Atlas材质；TTF描边和垂直度量仍等待真正画面对照。

隔离Unity第一次导入需要TMP资源时，adapter只在该候选工程通过已注册包的`resolvedPath`定位UGUI 2.6.0必需资源，导入Essential archive后同步刷新并核验原名shader/settings；不弹交互窗口、不导入Examples、不修改引擎或肥鹅。未生成或未就绪会明确失败，不用其他shader替代。新Scene包含固定750×1334设计坐标框、原生Canvas/EventSystem，Editor导入后会尝试离屏捕获`Analysis/native-page.png`；只有文件和真实回读存在才是Unity画面。`scripts/probe_bitmap.py`产物明确标OFFLINE，不是Unity预览。

机器交接包按模块/根因聚合并保留全部明细。真实View数组索引和Prefab component fileID必须读Editor回执；在此之前只提供字段/目标路径，不猜fileID。

## Creator 3.8.8 候选

`plan --target-profile cocos-3.8.8`读取同一schema 1 IR；可用同一`--bindings`证据收据。`export`按plan目标选择emitter。输出`assets/generated/art`的PNG/原TTF/标准BMFont及根meta、`extensions/monkey-import`的Editor-only薄扩展、Analysis映射与AI包；人工业务放`assets/manual`。不随Player解释IR。

资源窗口明确授权后才打开隔离工程，在资产导入就绪后执行`Monkey / Import isolated candidate`一次。扩展检查项目UUID、3.8.8版本和生成内容hash，查询原生SpriteFrame/Texture UUID，保留原生subMeta并设置尺寸/trim/九宫格；创建独立原生节点树并经Creator serializer保存Scene、重新加载回读。已有Scene或回执即拒绝覆盖。未执行时不含实际Scene，不声称真实显示通过。

当前支持Node/UITransform/UIOpacity、simple/sliced/tiled Sprite、原BitmapFont/TTF Label、Label原生描边、必要Widget/Layout/Button/矩形Mask/静止ScrollView子集。未知脚本、动态滚动和事件业务留handoff；字体度量、布局行为与同状态画面仍需真实比较。根UUID按namespace/source ID稳定产生；子资源UUID不在Python拼接猜测。

CONTINUE-02明确允许v0.1待验时推进v0.2/v0.3离线工作，两目标的Editor/视觉状态分别记录。

## v0.3 登记、差异与受控应用

当前CLI JSON合同schemaVersion=1，IR仍为schema 1。`capabilities --json`分别列源profile、两个目标profile及各目标真实验证状态。文件逻辑身份由目标profile/namespace/路径与source-map来源ID表达，内容SHA-256另列；不能把内容变更当成来源身份变更。

输出只在当前工作区的`outputs/<candidate>`登记，状态保存在`.monkey/outputs.json`，绑定绝对根、profile/namespace、来源根与manifest hash。CLI在该目录export后自动登记；其他目录可生成候选，但不能作为apply目标。旧候选或移位后未经登记的候选可用`register --candidate ... --out ...`验证并登记；不通过手改registry更新基线。原Unity10冻结候选保持原位不登记改写。

```sh
monkey diff --before outputs/base --after outputs/next --out outputs/change-report
monkey register --candidate outputs/base --out outputs/registration-report
monkey apply --target outputs/base --candidate outputs/next \
  --expected-manifest <base-manifest-sha256> --out outputs/apply-preview
monkey apply --target outputs/base --candidate outputs/next \
  --expected-manifest <same-base-manifest-sha256> --write \
  --preview outputs/apply-preview/application.json --out outputs/apply-result
```

默认apply只预览；写入必须有先前stage-hash保护的dry-run收据，且预览、当前内容、目标manifest与登记hash一致。路径必须规范化且不能包含符号链接或穿越片段，profile/namespace不能跨线合并。diff分别列added/changed/removed/unchanged/manual及manualConflicts；修改、缺失、目标占位、未知生成区文件、输入候选篡改或保留项被重引入都会拒绝相关写入。

生成区由manifest登记，`Assets/Manual/`和`assets/manual/`属于人工区。工具可初始化README脚手架但登记为manual，后续apply不覆盖、创建或删除人工区文件；人工文件hash仅作初始记录，静态verify与apply不据此覆盖人工内容；人工修改的生成文件作为冲突处理。Editor重写meta及新增原生输出尚不支持自动收编，必须停下处理，不把引擎生成和人工修改混为可覆盖文件。

removed文件保留在原路径，合并后的manifest将其标记retained，记录desired/applied-from manifest及retainedRemovedPaths；不会宣称目标逐字等于新候选。retained文件再次生成且内容变化时拒绝覆盖，目前没有自动所有权释放或垃圾清理命令。

写入前在`.monkey/transactions/<id>/`保存旧文件、manifest、registry和事务journal；同工作区使用更新锁。普通写盘失败会回滚自身已写文件；发现外部并发修改则保留该修改并标记recovery-required，不能承诺任意断电场景自动恢复。遗留update.lock需先检查对应journal，不自动删锁。该能力只处理登记生成文件，不是通用目录同步器，不写源工程。

## 两目标能力矩阵（当前开发候选）

| 能力 | Unity 6000.6.2f1/uGUI | Creator 3.8.8 |
|---|---|---|
| 同一2.4.15 IR、图像/原字体 | 离线支持既有子集 | 离线支持既有子集 |
| 原生节点/UI、必要布局/按钮/遮罩 | Editor-only C#候选 | Editor-only JS薄扩展候选 |
| 静态依赖/hash/AI包 | 通过代表切片 | 通过同源代表切片 |
| 源数值/业务脚本 | 正式JSON/业务待原生实现 | 正式JSON/业务待原生实现 |
| 登记、diff、受控apply | 定向人工区用例通过 | 定向用例及真实候选副本通过 |
| 实际导入/保存/重开、画面对照/输入 | not_run | not_run |
| 动态滚动、未知脚本/事件、Spine | unsupported/handoff | unsupported/handoff |

最低Python3.11与Windows运行环境尚未实测；当前验证环境为macOS arm64/Python3.14.7。开发wheel不是正式发行，不含原素材或测试样本。

## 有限 AnimationClip（CONTINUE-03）

新normalize输出可选的`animationSchemaVersion=1`、`animationClips`及cc.Animation的clip/root绑定。原IR schema仍为1，旧IR缺该字段等价于无动画；未知animation schema明确拒绝。计划可用`--animation <source-clip-id>`选一份来源剪辑，不另建reader；未选择时分析IR内的剪辑。

```sh
monkey plan --ir <normalized>/ir.json --namespace <stable-namespace> \
  --target-profile unity-6000.6.2f1-ugui --animation <source-clip-id> --out <new-plan>
# target-profile cocos-3.8.8 使用同一IR/clip选择；export/verify/handoff沿用现有命令。
```

支持局部x/y/z或position向量、scale向量/scaleX/Y/Z、0..255透明度；严格递增、从0起、在duration内的有限键序列，末键后恒定延至duration。仅linear（含省略/null）和constant阶跃；Normal/Loop、speed=1。其他easing/Bezier/循环、active和组件曲线不默认为线性。路径按源Animation所属节点的子层级唯一解析，缺失/重名、重复通道或Layout/Widget持有位置时明确留缺口。

Python生成六类数据：源位置、目标身份/相对路径、有限键、原生绑定/单位、中点验证探针、事件合同。Unity使用原生AnimationUtility，Creator按同一节点/向量分组为VectorTrack、透明度为RealTrack/UIOpacity；IR和创作脚本仅在Editor，Player不解释源对象图。原生.anim由Editor创建/保存/回读，离线没有实际曲线资产。`Analysis/animation-module.json`和单一AI模块任务聚合部分轨道及事件。

部分映射不会自动播放、附加业务Animator或回调。事件只记录source位置、时间、函数名与JSON参数及manual-only状态，Native事件数组为空；真实采样/播放和可编辑重开未验证。首个真实`CellBoxClicked`为0.5秒/6标量轨道，另两条active未支持，不能标作完整动画还原。详见[动画验收](validation/2026-10-23-animation.md)。
# 一键转换入口（2026-10-23）

```sh
bin/monkey convert --source /path/to/creator-2.4.15-project --target unity --out outputs/new-unity
bin/monkey convert --source /path/to/creator-2.4.15-project --target cocos --out outputs/new-creator
bin/monkey convert --recipe /path/to/recipe.json --out outputs/new-candidate
bin/monkey convert --resume outputs/new-candidate
```

`--output` 是 `--out` 的别名；目标也可用完整 profile。源目录须含 project.json 或 config.json，带 hash 的 bundle config 可直接传文件。可编辑工程默认选择全部 metadata 资产并保留未知类型诊断；发布 bundle 需 `--asset-index N`（可重复）或显式 `--all-assets`。无 engineVersion 的 bundle 必须声明 `--source-profile cocos-2.4.15-bundle`，不靠文件名猜源版本。既有 2048 资产闭包、字节预算仍适用。

recipe 为 UTF-8 JSON，可复用范围与依赖，路径相对 recipe 文件解析，不写输出路径：

```json
{
  "source": "source/config.json",
  "target": "cocos",
  "source_profile": "cocos-2.4.15-bundle",
  "namespace": "example-ui",
  "selection": [2],
  "dependencies": [],
  "evidence": []
}
```

也支持 `bindings`、`animations`、`all_assets`；未知字段/错误类型拒绝。recipe 不可混用显式输入选项；输出由 `--out` 指定。

一次调用串联 inspect/normalize/plan/export/verify/handoff，原生候选在 `project/`，各阶段 manifest 独立保留，`conversion.json` 与顶层 `manifest.json` 汇总。失败保留阶段和 `failedStage`，不覆盖原件/旧输出、不删除证据。默认 `status=needs_action`、`resultKind=candidate`，明确原生导入待处理；显式 `--offline` 为 `partial`。当前尚无命令行自动启动编辑器/调用原生导入的实现，不把待处理项当自动化完成；外部编辑器仍需真实可用版本、登录/许可与窗口条件。

`completed=true` 仅表示六个离线阶段执行完毕，不表示原生/视觉/业务完成。退出码沿用：0 无缺口，1 部分/需行动，2 输入/冲突/执行失败；当前 convert 因原生或后续验收未闭合返回 1。未支持的组件和业务在 handoff 内保留。

`--resume` 校验工具版本、原始 conversion 收据、来源/证据 SHA、候选 manifest SHA 后复用工程，仅做原生回读验证；新检查写入独立 `checks/<id>/`。没有回读仍为 needs_action；实际原生引用与文件通过才为 resultKind=native，视觉/业务仍单列待验。引擎生成的 meta 通过原生回读合同校验，人工内容改动仍由 hash 检出。当前仅续验已完成候选；失败的中间生成阶段保留证据但尚不能自动续跑。登记增量仍使用既有 register/apply 合同。

## 包级默认入口与双目标（2026-10-23）

```sh
bin/monkey convert --source GAME.wxapkg --target both --out outputs/new-game
bin/monkey convert --source GAME.apk --target unity6 --out outputs/new-game-unity
bin/monkey convert --source /path/to/obtained-resources --target cocos38 --out outputs/new-game-cocos
```

支持明文wxapkg的BE/ED头、索引和连续不重叠payload，APK ZIP及明确Cocos资源目录。资源目录默认全文件，保留`--package`强制全文件入口；旧asset-index/recipe只用于切片诊断。全量指本次明确输入内的全部可枚举文件；多输入根通过schema 1 input-set校验身份并合并。存在同名不同配置bundle时拒绝混拼。源Cocos版本无法确定时记录unknown，不伪称对象reader支持。非Cocos或未知加密容器明确报错。

边界：最多50,000文件/目录、每文件32MiB、展开512MiB、容器1GiB、目录深64。拒绝穿越、绝对路径、反斜线、symlink/特殊项、大小/哈希变化、同名及Unicode/casefold路径别名、wxapkg重叠或漏计payload。仅一层枚举，不递归解包内部容器；嵌套包原样待转。APK内动态库/dex及平台文件保留证据并排除目标运行时，不执行、不安装。

输出分别为UnityProject/CocosProject；移走其中一个工程不依赖另一个或InputCache。每个工程包含resource-ledger、cocos-assets、code-index、dynamic-keys、agent-work、生成文件hash/所有权，以及AGENTS、START-HERE、PROJECT-STRUCTURE和DEPENDENCIES。已识别PNG/JPEG、TTF/OTF、Ogg/MP3/WAV复制到规范内容目录（仍需引擎导入）；所有未知原件/序列化对象/配置/Spine等留SourceRecovery。数值未判明前不假造正式配置；JSON不是一律当数值表。

AST解析只读源代码，固定Acorn8.15.0；Node堆上限512MiB、单次30秒、AST3百万节点/深512。literal loader/System.register能恢复相应factory；动态/拼表模块仍为候选。RF fallback仅配对同一词法块的静态push/pop，保存精确UTF-8字节范围、hash、类/身份、可读片段；外围import/模块边界未知，未匹配位置另列缺口，不能当完整模块语义证明。每模块生成SourceRecovery内TS/C#初稿、实际依赖/导出/事件/资源键证据；调用抛明确未实现，不接原服、不假奖励。编译/行为均false，未启用业务。

当前返回needs_action/candidate，`completed`只表示留存/工作区生成已执行完毕；nativeObjects=pending_adapter、editor/visual/business=not_run。`--offline`返回partial。包级原生对象恢复、原生导入编排、失败阶段续跑、包级resume/register/apply待接入；目录生成不能代表产品目标已完成。资源覆盖以输入文件/字节为分母，缺失引用另计，去重保留每个来源ID。

## 原生启动预检与阶段续跑身份

```sh
bin/monkey preflight --candidate outputs/game/UnityProject \
  --log /path/to/previous-import.log --out outputs/startup-check
```

该命令只检查冻结文件、目标版本、已安装引擎/CLI和已有Editor标记，并对已有日志作分类；不启动Editor、写全局缓存、删除锁、修改安全设置或自动重试。readonly database/系统IPC警告且未初始化引擎时标记`HOST_CACHE_OR_IPC_ACCESS_SUSPECTED`，这是定位推断；许可entitlement已解析时，不仅凭token更新失败就断言许可无效。

新候选记录包级源码恢复、inspect、normalize、目标plan和emit的源码阶段签名。包级续跑在归档/改动候选前拒绝缺失或变化的缓存算法签名。旧开发候选（如932220d）没有这份签名，应保留并用新输出目录重新转换，不能给旧缓存补写当前签名后冒充兼容。

Unity新导入计划另列每个独立源Prefab的根、节点集合和目标路径，跨源节点引用/多根图明确拒绝；Editor薄层保存后加载内容核对，回执缺失时不声称原生Prefab已完成。源Scene不按Prefab冒名输出。Spine闭包输出在`SourceRecovery/Spine/`，保存真实bin、原atlas文本和按显式引用解码的PNG页面；`Analysis/spine-closures.json`区分缺失和未支持。闭包恢复不等于安装兼容且有许可的Spine runtime或动画通过。

原生薄层按128张纹理分批设置与同步加载，避免每张重复刷新。执行层可显式设置`MONKEY_NATIVE_BUDGET_SECONDS=600`或`MONKEY_NATIVE_DEADLINE_UTC`为本次授权窗口的UTC截止；预算在批次/阶段安全点生效，不能硬抢占阻塞的引擎调用，外层仍需核对进程真实退出。停止会写`Analysis/native-progress.json`，已有原生Scene/Prefab保持create-only，暂不支持凭进度原地续跑。

```sh
bin/monkey preflight --candidate outputs/game/UnityProject \
  --progress /path/to/Analysis/native-progress.json --out outputs/progress-check
```

进度必须匹配该候选import-plan SHA；`completed`也不代表编辑器验收通过，仍须`verify --level editor`真实回读。nativeResumeSupported=false不能当作自动重跑授权。

## 受控异步原生导入

`native-import`默认仅生成计划。实际执行必须显式加`--execute`，并由操作者保证本轮独立Editor/资源已获准。不会从历史窗口推导新许可。

```sh
bin/monkey native-import --candidate outputs/game/UnityProject \
  --out outputs/acceptance/my-new-run \
  --editor-path /Applications/Unity/Hub/Editor/6000.6.2f1/Unity.app/Contents/MacOS/Unity \
  --expected-manifest "候选manifest的SHA256" --budget-seconds 600 \
  --deadline-utc "YYYY-MM-DDTHH:MM:SSZ" --window-end-utc "YYYY-MM-DDTHH:MM:SSZ"
```

替换SHA和本轮UTC时间。内部截止至少比外层截止早30秒，当前外层窗口上限1小时；共享验证按实际批准的更短窗口。确认计划后同参数添加`--execute`可执行规划目录；参数/代码或输入变化需新目录，已有部分工程不覆盖。

宿主新建副本后直接启动已指定Editor的batchmode，固定`ImportBatchAsync`且不带`-quit`，等待包完成事件继续。`unity run`固定带`-quit`，不能用于这一异步入口。成功/失败/预算结束由薄层退出，宿主保存真实PID与退出状态，外层必要时仅普通terminate自己的child，无hard kill；未退出明确报attention。`execution-result.json`和`Verification/`分开记录启动、资源、原生回读和来源缺口。

这是生成工程的可选原生验收阶段；没有--execute时不会启动引擎。新执行路径尚待实际窗口验证，进度或模拟测试不构成引擎通过。

## 原名恢复与受校验重新规划

可恢复的config.paths优先，源_name其次，均无可靠名称才用unknown短ID。目标保留bundle和相对目录；原尺寸/字库atlas等派生资源有语义后缀，真实冲突才消歧。Analysis/name-map.json、package-name-map.json、decoded-name-map.json、module-name-map.json以及spine-closures.json记录映射与原因；中间缓存可以继续哈希命名。

名称规则更新可从明确支持的旧阶段生成新候选，无需重新执行未变化的reader/像素/AST解析：

```sh
bin/monkey convert --input-set inputs.json --target both --namespace SAME_NAMESPACE --reuse-source-stages outputs/FROZEN_OLD --out outputs/FRESH_NEW
```

只接受完全相同的输入路径/字节/SHA及namespace；阶段owner清单和实际文件需全部一致，且算法为当前或明确支持的names-v1元数据迁移（838d05b）。旧候选只读，新的SourceRecovery初稿按RF/模块原名重新组织，不合并旧候选中的人工业务修改。像素缓存只作不可改写的数据复用；引用、meta、manifest和handoff随新路径重新生成。任一身份/算法/文件漂移直接拒绝，不静默跳过。原生回读仍需实际新窗口。

## Creator原生CLI执行

新生成的Creator候选可复用同一`native-import`入口，Editor按显式路径选择；计划默认不启动，实际执行须`--execute`：

```sh
bin/monkey native-import --candidate outputs/game/CocosProject --out outputs/acceptance/game-creator-new \
  --editor-path /Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/MacOS/CocosCreator \
  --expected-manifest MANIFEST_SHA256 --budget-seconds 1200 \
  --deadline-utc INTERNAL_UTC --window-end-utc OUTER_UTC --execute
```

严格核验源候选后复制到全新CocosProject，仅本次child收到绑定路径/manifest的执行标志；等资产库和Scene就绪后调用一次原生导入。普通打开工程不自动执行。进度/首错/执行结果在acceptance目录，保存后核实际文件SHA和原生回读；退出0不等于原生通过。旧候选没有新执行入口时明确拒绝，应重新生成，不能借用其他已打开工程。当前实现已离线定向验证，真实端到端自动执行仍待验收。
