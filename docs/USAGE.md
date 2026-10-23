# 当前使用与支持矩阵

当前实现只声明两种 Cocos **2.4.15 子集**，不是所有 Cocos 格式的通用导入器。

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

隔离Unity第一次导入需要TMP资源时，adapter只在该候选工程使用官方`TMP_PackageResourceImporter.ImportResources(true,false,false)`，不弹交互窗口、不导入Examples、不修改引擎或肥鹅。新Scene包含固定750×1334设计坐标框、原生Canvas/EventSystem，Editor导入后会尝试离屏捕获`Analysis/native-page.png`；只有文件和真实回读存在才是Unity画面。`scripts/probe_bitmap.py`产物明确标OFFLINE，不是Unity预览。

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
