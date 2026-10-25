# monkey 目标工程规范（monkey-project/1）

状态：**已确认**（2026-10-25，用户在本聊天确认 D1–D6 全部采用推荐项；实施分支 `monkey`，起点 eb91533）。本文件是 monkey 生成 Unity6 / Creator3.8.8 工程目录、文件命名、配置表与交接文件的唯一规范；`targets/layout.py`、`names.py` 及各 emitter 中现有的路径常量都按本文重构。版本号 `monkey-project/1.0.0`，破坏性修改升主版本，兼容新增升次版本。

参照工程：
- 肥鹅美食街 `projects/20-肥鹅美食街/FoodStreet`（Cocos 2.4.15 → Unity6，已采用 dev3 全量初版）。
- 向僵尸开炮 `projects/21-向僵尸开炮/Unity`（Unity 2021.3 IL2CPP → Unity6，已采用 AssetRipper 全量初版）。
- 工作区规范：GREA `grea-unity-standard` STR/ARC 规则、`grea-native-port` 原生转换规范、Manager `COCOS-FIVE-LAYER.md`、`UNITY-CONFIGURATION.md`。本文与它们一致；不同之处在第 9 节列出。

---

## 1. 为什么要改：两款游戏里看到的问题

| # | 现状（实际路径） | 问题 |
|---|---|---|
| 1 | `Assets/Game/Content/Images/Sprites/remoteAsset/Texture/Element/Fish_3/1005302.original.png` | 来源分包名 `remoteAsset`、源类型目录 `Texture`、派生后缀 `.original` 全部进了生产路径 |
| 2 | `Content/Images/Sprites/gameAsset/Audio/BGM/bgm_Intro.mp3`（共 356 个 mp3） | 音频按“图片”归类，类型判断错误 |
| 3 | `Content/Config/Recovered/zh-tw/Config/label.json` | 语言分包当目录、`Recovered` 来源词、`Config` 重复；实为本地化字符串表 |
| 4 | `Content/Materials/002aba30c8bc53ce83ca705ea6b1b7fb.mat`、`Animations/Controllers/c0e7…5.controller`（776 个） | 以 GUID 命名，无法阅读 |
| 5 | `Animations/gameAsset/Anim/BigDay/PlayerGroup/appear4.animationclip.anim` | 双扩展名；分包＋源类型目录 |
| 6 | `Content/Prefabs/Recovery/Sources/remoteAsset/Prefab/House/Adorns/Room7/10070600.prefab` | 6 层来源嵌套（Recovery/Sources/包/Prefab） |
| 7 | `Assets/Generated/`、`Assets/Monkey/`、`Assets/Manual/`、`Assets/Game/` 四个并列根 | 同一工程四套归属根；转换胶水散在 3 处 |
| 8 | `SourceRecovery/CodeDrafts/NamedCSharp/AutoSeriesBoxElement-5983162.cs`，`namespace Recovered.Gameplay`；另有 `CSharp/snapshot/` 同名第二份 | 文件名带哈希；命名空间是来源词；两套草稿 |
| 9 | 向僵尸 `Assets/Texture2D/`、`MonoBehaviour/`、`AnimationClip/`、`Sprite/`、`TextAsset/` 与 `uiraw/`、`effect/`、`actormodel/` 并列；`Font/`+`fonts/`、`Material/`+`materials/` 重复 | 直接沿用 AssetRipper 类型根和源工程小写目录 |
| 10 | 向僵尸 `Assets/Resources/config/` 27,740 个原始 `.bytes` 表在生产 Assets | 原始二进制表混入运行资产；正式配置真源不清 |

两款游戏为了弥补，自己又建了 `Art/Original/<批次>`、`Content/BulkInitial/`、`Product/`、`Original*`/`Source*` 类名前缀、`*.UIRecovery.unity`——说明工具输出无法直接当作日常工程。本规范要让生成工程**打开即是按模块组织的普通工程**，来源信息全部留在 `Analysis/` 和 `SourceRecovery/`。

## 2. 原则

1. **按目标职责＋游戏模块组织，不按来源打包组织**。分包/bundle、语言包、AssetBundle、AssetRipper 类型根、源类型目录（`Texture/`、`Prefab/`、`Anim/`…）只作为元数据记录，不作为目录。
2. **身份与路径解耦**。Unity GUID / Creator UUID 继续由 `sourceId` 确定性派生，与路径无关；布局变化不改身份。旧布局→新布局的同 GUID 迁移表随输出提供。
3. **只做有依据的规范化**。工具负责：去打包层、去源类型层、去来源词、统一大小写和字符集、按真实导入类型归类。**工具不臆造语义名**（如把 `a2_saodiji3` 改成 `Sweeper`）；语义改名只来自游戏级覆盖表 `layout.json`（第 7 节），可由人或 AI 填写后确定性重生成。
4. **每项资产一个规范位置**。派生变体只在被引用时生成，后缀有固定含义；源证据留在 `SourceRecovery/`，不进 `Assets/`、`assets/`。
5. **生产区无来源痕迹**。`Assets/`、`assets/` 下禁止第 8 节列出的目录名、文件名和类名模式。转换胶水只放在一个可整体删除的目录里。
6. **可重复、可迭代**。同输入＋同工具版本＋同 `layout.json` → 路径逐字节相同；冲突消解与输入顺序无关；每次重生成可预览差异，人工修改不被覆盖（沿用现有 manifest 所有权规则）。
7. **模块分区明确**。主线、独立小游戏、SDK、测试内容分区；被排除的内容保留但不进入 Build 列表。

## 3. 输出根目录

```text
<out>/
  README.md                  # 新增：本次输入、目标、各工程入口、状态一页说明
  conversion-result.json     # 不变（外部合同）
  UnityProject/              # 不改名（下游采用脚本已依赖）
  CocosProject/
  InputCache/                # 仅转换期使用，两工程不依赖
```

## 4. Unity6 工程（逐文件）

### 4.1 目录树

```text
UnityProject/
  AGENTS.md                         # 生成：AI 接手规则（一页，链接 Docs/START-HERE.md）
  README.md                         # 生成：打开方式与目录速览
  manifest.json                     # 生成：逐文件 owner/hash（现有合同）
  Packages/manifest.json            # 生成：仅实际需要的官方包（uGUI、TMP 等）
  Packages/packages-lock.json
  ProjectSettings/*.asset           # 生成：Unity 默认 + 必要项；EditorBuildSettings 只含 Boot
  Assets/
    Game/
      Bootstrap/                    # 有可编译入口时才建
      Domain/<Module>/              # 可编译纯数据/规则（含配置 DTO）
      Gameplay/<Module>/
      Presentation/<Module>/        # View 组件
      Presentation/Common/Layout/   # monkey 提供的少量原生布局组件
      Presentation/Preview/         # 预览场景用组件（可删）
      Services/<Capability>/
      Scripts/<Assembly>/           # 仅 Unity 来源：原程序集类型壳（见 4.6）
      Content/                      # 全部资产，见 4.2
      Scenes/                       # 见 4.4
      Editor/
        Conversion/                 # monkey 胶水，整目录可删（见 4.5）
    Plugins/<Vendor>/               # 第三方二进制（如 Spine38 dll）
    ThirdParty/<Vendor>/            # 必须留在 Assets 的供应方源码/资源
    TextMesh Pro/                   # Unity 官方 TMP Essential，保持官方默认路径
  Docs/                             # 见 6.1
  Analysis/                         # 见 6.2
  SourceRecovery/                   # 见 6.3
```

只创建有内容的目录；不建空层。`Assets/Generated`、`Assets/Monkey`、`Assets/Manual`、`Assets/Editor/Monkey`、`Assets/MonkeyRecoveryVerification` 全部取消（见第 10 节迁移表）。人工区不再用 `Assets/Manual/`，而由 manifest `owner=manual` 判定：manifest 外或 owner≠generated 的文件一律视为人工。

### 4.2 `Assets/Game/Content/` 类型目录

路径形式：`Content/<Type>/<Module>/<Sub…>/<file>`。`<Type>` 按**实际导入类型**决定，不按扩展名或来源目录名。

| `<Type>` | 放什么 | 判定依据 |
|---|---|---|
| `Sprites/` | 导入为 Sprite 的图片（UI/2D 显示） | Cocos SpriteFrame 主图；Unity 来源 Texture2D 有 Sprite 子资源或被 Image/SpriteRenderer 引用 |
| `Textures/` | 非 Sprite 图片（材质、特效、模型贴图） | 被 Material/Mesh/粒子引用，或无 Sprite 用途 |
| `Atlases/` | SpriteAtlas v2 | 生成或来源已有图集 |
| `Prefabs/` | Prefab / Prefab Variant | cc.Prefab；Unity 来源 Prefab（非特效） |
| `Effects/` | 粒子与特效 Prefab | 根含 ParticleSystem / cc.ParticleSystem |
| `Animations/` | `.anim`、`.controller`、`.overrideController` | 同模块的 clip 与 controller 放一起 |
| `Spine/` | 每个骨骼一个子目录：数据、atlas、页图、SkeletonData/Atlas/Material 资产 | spine 闭包；运行包未安装时整闭包进 `SourceRecovery/Unconverted/Spine/` 同路径 |
| `Fonts/` | 每个字族一个子目录：ttf/otf、TMP FontAsset、位图字体及其页图 | cc.TTFFont / cc.BitmapFont / TMP_FontAsset |
| `Audio/Music/`、`Audio/Sfx/`、`Audio/Voice/` | 音频 | 来源路径或名含 bgm/music→Music；voice/vo→Voice；其余 Sfx |
| `Materials/` | Material | |
| `Shaders/` | Shader/HLSL/ShaderGraph | 不因名字含 Spine 归到 Spine |
| `Models/` | Mesh、FBX 及模型组 | |
| `Config/` | 正式 UTF-8 JSON 配置 | 见 4.3 |
| `Data/` | 非配置的 ScriptableObject 资产（Unity 来源） | MonoBehaviour `.asset` 且不属于字体/Spine/图集 |
| `Localization/<locale>/…` | 语言覆盖资源与字符串表 | 见 5.3 |
| `MiniGames/<Name>/<Type>/…` | 独立小游戏/活动玩法的全部资产，内部同样按类型 | `layout.json` 或分包规则标记为 minigame |

### 4.3 配置表

- 源 JSON 表（cc.JsonAsset 等）：**内容逐字节保留**，只改位置与文件名 → `Content/Config/<Module>/<Name>.json`，`<Name>` 为 PascalCase，去掉 `Cfg/Config/Conf/Data` 尾词后加 `Table`（`AudioCfg`→`AudioTable`，`decor-config`→`DecorTable`）。关卡/逐条数据文件不加 `Table`（`level_2`→`Level2`）。
- 字段名、数值、ID 不改。字段语义改名只在有明确 table adapter 或 `layout.json` 字段映射时生成新的规范化表；原表仍保留在 `SourceRecovery/Config/`。
- 无法解析的原始表（二进制 `.bytes`、resbin 等）不进 Assets，进 `SourceRecovery/Config/<Module>/<原文件名>`，台账状态 `needs_adapter`。
- 配置 DTO/校验代码（有据生成时）放 `Domain/<Module>/Config/<Name>Row.cs`、`<Name>.cs`；读取 I/O 放 `Services/Config/`。不生成重复的 SO 数值表。
- 来源、原路径、hash 写 `Analysis/Mappings/config.json`，**不写进生产 JSON**。

### 4.4 场景

| 场景 | 位置 | Build |
|---|---|---|
| 导入引导（原 `ImportBootstrap.unity`） | `Assets/Game/Scenes/Boot.unity` | 是（唯一） |
| 内容预览（原 `Candidate.unity`） | `Assets/Game/Scenes/Preview/ContentPreview.unity` | 否，可删 |
| 恢复的源场景 | `Assets/Game/Scenes/<SceneName>.unity`（`main`→`Main.unity`） | 否，待确认后加入 |
| 源测试场景（名含 test） | `Assets/Game/Scenes/Tests/<SceneName>.unity`（`room16_test`→`Room16Test.unity`） | 否 |
| 小游戏场景 | `Content/MiniGames/<Name>/Scenes/` | 否 |
| 场景附属（Lighting 等） | 与场景同名的同级目录 | — |

### 4.5 转换胶水 `Assets/Game/Editor/Conversion/`

monkey 写入的全部 Editor 代码与计划集中于此，删除整个目录后工程仍能编译、打开和运行已生成部分。

| 现文件 | 新文件 |
|---|---|
| `Assets/Monkey/Editor/MonkeyImporter.cs`、`Assets/Game/Editor/Conversion/MonkeyImporter.cs` | `Editor/Conversion/MonkeyImporter.cs` |
| `Assets/Monkey/Editor/import-plan.json` | `Editor/Conversion/import-plan.json` |
| `Assets/Monkey/Editor/MonkeyNumericCode.cs` | `Editor/Conversion/MonkeyNumericCode.cs` |
| `Assets/Monkey/Editor/MonkeyPrefabInstances.cs` | `Editor/Conversion/MonkeyPrefabInstances.cs` |
| `Assets/Monkey/Editor/UnityDynamicUi.cs` | `Editor/Conversion/MonkeyDynamicUi.cs` |
| `UnityBulkFinish.cs`、`UnityLayoutPatch.cs`、`UnityNumericCodeVerifier.cs` | `Editor/Conversion/MonkeyBulkFinish.cs` 等（统一 `Monkey` 前缀） |
| `Assets/Editor/Monkey/UnitySourceVerifier.cs`、`Assets/MonkeyRecoveryVerification/` | `Editor/Conversion/MonkeySourceVerifier.cs`、`Editor/Conversion/Verification/` |

`Monkey` 前缀**只允许出现在本目录**。胶水使用独立 asmdef `Monkey.Conversion.Editor`（Editor only）。

### 4.6 代码

**Cocos 等非 Unity 来源**：可编译代码进五层 `Assets/Game/<Layer>/<Module>/<Class>.cs`；不可编译初稿进 `SourceRecovery/Code/Drafts/CSharp/<Layer>/<Module>/<Class>.cs`（与将来目标位置一一对应，可直接搬入）。

- 文件名＝类名，一文件一个公开类型，**不带哈希**；同模块同名冲突在 `Analysis/Mappings/code.json` 登记，按第 5.4 节消解。
- 命名空间 `<RootNamespace>.<Layer>.<Module>`；`RootNamespace` 来自 `layout.json`（如 `FoodStreet`、`ZombieShooter`），未设置时为 `Game`。不再使用 `Recovered.*`。
- 层/模块推断（结果与理由写 `code.json`）：①被 Prefab/Scene 组件绑定 → `Presentation/<该 Prefab 的模块>`；②类名后缀 `Window|View|Panel|Hud|Item|Cell|Button|Btn|Comp` → Presentation，`Manager|Mgr|System|Controller|Ctrl|Logic` → Gameplay，`Config|Cfg|Data|Model|Info|Vo|Def` → Domain，`Net|Http|Socket|Sdk|Storage|Platform|Ad|Ads` → Services；③模块取绑定 Prefab 模块或类名前缀匹配的已知模块；④仍不确定 → `Gameplay/Unclassified/`。`layout.json` 可逐类覆盖。
- 取消 `CSharp/snapshot/` 与 `NamedCSharp/` 两套并存，只保留具名初稿一套。

**Unity 来源**：原程序集的类型壳（为保持序列化字段与 MonoScript 身份）放 `Assets/Game/Scripts/<AssemblyName>/<命名空间转目录>/<Class>.cs`，每个程序集一个 asmdef，**类名与命名空间保持原样**（它们是序列化类型身份）。第三方/引擎程序集（`UnityEngine.UI`、`Unity.TextMeshPro`、`Spine`、`YooAsset`、`HybridCLR.Runtime`、`wx-*` 等）不作为游戏代码输出：有官方包的改用包，SDK 进 `SourceRecovery/Code/ThirdParty/<Assembly>/` 并在台账标 `excluded-sdk`。

**monkey 提供的运行时组件**（原 `Assets/Generated/Views/`、`Assets/Game/Presentation/Recovery/`）：

| 组件 | 新位置 | 命名空间 |
|---|---|---|
| `NativeLinearLayoutGroup`、`NativeChildLayoutGroup`、`NativeRectConstraints`、`NativeTextLineBox`、`IntrinsicGridLayoutGroup` | `Assets/Game/Presentation/Common/Layout/<Class>.cs` | `<Root>.Presentation.Common` |
| `MonkeyCandidateView` | `Assets/Game/Presentation/Preview/ContentPreviewView.cs` | `<Root>.Presentation.Preview` |

布局组件保持类名（肥鹅已按 GUID 采用，避免无谓改名），脚本 GUID 不变；退役的 `NativeFlowLayoutGroup` 不再输出。

## 5. 命名规则

### 5.1 大小写与字符

分词：按 `_ - . 空格` 切分，再在“小写/数字→大写”“缩写→单词”处切分；字母与数字不切开（`Room7`、`Area01` 各为一个词）。已知缩写 `UI HUD BGM SFX VFX FX NPC AI ID VIP PVP PVE SDK 2D 3D` 在 PascalCase 中保持全大写。非 ASCII（中文等）保留 NFC，不音译。

| 对象 | Unity | Creator | 例 |
|---|---|---|---|
| 固定结构目录 | PascalCase（本文所列名） | 小写（本文所列名） | `Content/Sprites` / `assets/art/sprites` |
| 模块及子目录 | PascalCase | kebab-case | `CardSeason` / `card-season`；`Fish_3`→`Fish3`/`fish3` |
| 代码文件、类 | PascalCase＝类名 | PascalCase＝`@ccclass` 名 | `ElementDetailWindow.cs` / `.ts` |
| Prefab、Scene、Controller、SO、配置 JSON | PascalCase | PascalCase | `DigGamePriceEndWindow.prefab`、`AudioTable.json` |
| 媒体（图片、音频、clip、模型、材质） | snake_case 小写 | snake_case 小写 | `bgm_Intro`→`bgm_intro.mp3`；`CookGo`→`cook_go.png` |
| 纯数字或 ID 名 | 保持 | 保持 | `10070600.prefab`、`1005302.png` |

非法字符替换为 `_`；Windows 保留名加 `_`；单段 ≤64 字节，`Assets/` 下全路径 ≤180 字节，超出时截断并加 `_<hash6>`（台账记理由）。

### 5.2 引用闭包内文件名保持原样

被数据文件按名字引用的文件，**只规范目录、不改文件名**，避免改写二进制/文本内部引用：Spine 的 `.atlas` 页图、BMFont `.fnt` 页图、plist 帧表页图、Unity 来源 Spine `_Atlas/_SkeletonData/_Material` 三件套。

### 5.3 本地化

- 语言分包识别：`en zh zh-cn zh-tw tw jp ja kr ko` 等，规范为 BCP 47：`zh→zh-Hans`，`zh-tw/tw→zh-Hant`，`jp→ja`，`kr→ko`。
- 默认语言（`layout.json` `defaultLocale`，默认 `zh-Hans`）的资源放普通类型目录；其他语言的覆盖资源放 `Content/Localization/<locale>/<Type>/<Module>/…`，文件名与默认语言资源相同。
- 字符串表（扁平 key→string，或名为 `label/lang/i18n/text`）放 `Content/Localization/<locale>/Strings/<Name>.json`，内容逐字节保留。

### 5.4 派生变体与冲突

- 变体后缀只有两种：`_untrimmed`（Cocos 裁切帧的原尺寸填充图，原 `.original`）、`_page<N>`（拆出的字体/图集页）。只在 Prefab/Scene/字体实际引用时生成；主资产是被引用的那份。
- 不再使用 `.<kind>` 扩展式消歧（如 `.animationclip.anim`）。
- 冲突（大小写不敏感、NFC 后同名）：按 `sourceId` 排序，第一个保留名称，其余加 `_<sha6(sourceId)>`。结果只取决于参与冲突的源身份，与输入顺序无关。全部写入 `Analysis/Mappings/names.json`。

### 5.5 GUID 命名对象

无源名的 Material/Controller 不再用 GUID 作文件名：Material 取主贴图名，否则取首个引用 Prefab 名；Controller 取所属 Prefab 名，否则取其 clip 所在目录名；仍无依据时 `<type>_<sha6>`（如 `material_3f2a1c.mat`）并标 `no-safe-source-name`。

## 6. 工程内非 Assets 目录

### 6.1 `Docs/`

| 文件 | 内容 |
|---|---|
| `START-HERE.md` | 唯一 AI/人工入口（合并原 `AI-ENTRY.md`）：打开方式、状态、下一步、禁止事项 |
| `PROJECT-STRUCTURE.md` | 引用本规范版本；实际模块表（模块→Unity/Creator 目录→文件数）；本工程例外 |
| `CONTENT-INDEX.md` | 模块 × 类型数量表；被排除/待转内容数量 |
| `CODE-STATUS.md` | 代码：可编译 / 初稿 / 未分类 / SDK 排除数量与位置 |
| `HANDOFF.md` | 原 `BULK-INITIAL-HANDOFF.md`：本次交付的验证层级与限制 |
| `DEPENDENCIES.md` | 包、插件、版本与许可 |

### 6.2 `Analysis/`

```text
Analysis/
  README.md                 # 本目录文件索引
  Mappings/                 # 源 ↔ 目标映射（AI 日常最常读）
    assets.json             # sourceId → 目标路径、GUID/UUID、原包、原逻辑路径、类型、模块、命名理由
    modules.json            # 模块表与来源规则
    names.json              # 规范化/冲突/覆盖记录（合并原 name-map、package-name-map、module-name-map、decoded-name-map）
    dynamic-keys.json       # 原动态加载键 (bundle,key,type) → 新资产
    locales.json
    code.json               # 源类 → 层/模块/草稿路径/理由
    config.json             # 源表 → 正式 JSON / 原件位置
    layout-migration.json   # 上一布局路径 → 新路径（同 GUID），供已采用工程迁移
  Ledger/                   # resources.json（原 resource-ledger）、inputs.json（原 all-inputs）、coverage.json
  Code/                     # code-index、component-code-bindings、named-code-handoff、unity-code-model…
  Readback/                 # editor-readback、native-identity-contract、initial-editor-verification、bulk-finish-readback…
  Tasks/                    # agent-work.json、agent-work-details.json
  Evidence/                 # Decoded/、structured-objects、typed-objects、dependency-typed-*：证据区，保持源布局
```

`dependency-typed-0..600.json` 这类分片收进 `Evidence/Dependencies/`，不再平铺在 `Analysis/` 根。

### 6.3 `SourceRecovery/`（不编译，不进 Assets）

```text
SourceRecovery/
  Original/<container>/…                  # 原件逐字节，保持源布局
  Code/Modules/<Module>/<Class>.js        # 源模块切片（按 code.json 的模块）
  Code/Drafts/CSharp/<Layer>/<Module>/<Class>.cs
  Code/Drafts/TypeScript/<layer>/<module>/<Class>.ts
  Code/Source/…                           # 完整源脚本（原 SourceCode/）
  Code/ThirdParty/<Assembly>/…            # Unity 来源的 SDK/引擎程序集
  Config/<Module>/<原文件名>               # 原表与无法解析的表
  Unconverted/<Type>/<Module>/…           # 原格式待转（astc、未接 Spine 等），镜像将来的 Content 位置
```

除 `Original/` 与 `Code/Source/` 保持源布局作证据外，其余子目录一律镜像目标布局，转换后可原样搬入 `Content/`。

## 7. 游戏级覆盖表 `layout.json`

放在 `--input-set` 同目录或 `--layout PATH` 指定；纳入输入快照与续跑校验。全部字段可选。

```json
{
  "schemaVersion": 1,
  "rootNamespace": "FoodStreet",
  "defaultLocale": "zh-Hans",
  "bundles": {
    "miniGameRes": {"role": "minigame"},
    "spineAsset": {"role": "packaging"}
  },
  "stripSegments": ["uiraw", "SpineCook"],
  "modules": [
    {"match": "uiraw/icon_*", "module": "Icons/{1}"},
    {"match": "Texture/UI/Disco/**", "module": "Disco"}
  ],
  "renames": {
    "remoteAsset:<uuid>": "street_sweeper"
  },
  "code": {
    "AutoSeriesBoxElement": {"layer": "Presentation", "module": "Board"}
  }
}
```

- `match` 使用原 `bundle/logicalPath` 的 glob；第一条命中生效；`{1}` 取第一个 `*`。
- 新命令 `monkey layout-preview --input-set … --layout layout.json --out preview/` 只输出 `Mappings/*.json` 和目录树统计，不写工程；用于人或 AI 审阅后补充覆盖表。
- 覆盖表只能改路径和名字，不能改身份、内容、数值或动态键本身。

### 7.1 内置规则（无覆盖时）

| 规则 | Cocos 来源 | Unity 来源 |
|---|---|---|
| 打包层（直接去掉，记为元数据） | `main resources internal start-scene gameAsset remoteAsset spineAsset` 及 subpackage 名 | AssetRipper 类型根 `Texture2D Sprite Material MonoBehaviour TextAsset AnimationClip AnimatorController Shader Font Mesh AudioClip`；`Assets/` |
| 源类型词（仅首段，大小写不敏感） | `Texture(s) Image(s) Prefab(s) Anim Animation(s) Spine SpineCook UiSpine Audio Sound(s) Music Font(s) Config Data Material(s) Shader(s) MovieClip` | `uiraw textures materials fonts spine prefabs scenes` |
| 类别词（音频） | `BGM Music`→Music、`Voice`→Voice、`SFX Sound`→Sfx，去掉该段 | 同左 |
| 小游戏 | `miniGameRes` 分包 | `layout.json` 指定 |
| 本地化 | 语言分包名 | 路径段 `zh/en/…` 或 `layout.json` |
| 无模块段 | `Common` | `Common` |
| 无源逻辑路径 | `Content/<Type>/Unsorted/` | 同左（如 AssetRipper 无容器名对象） |

## 8. 生产区禁止项（静态检查）

`Assets/`（除 `Editor/Conversion/`、`Plugins/`、`ThirdParty/`、`TextMesh Pro/`）及 Creator `assets/` 内：

1. 目录名：`Original Recovered Recovery Source Sources Generated Monkey Manual BulkInitial Imported SourceMedia Unformatted` 及第 7.1 节全部打包层名、源类型词、语言分包名（`Localization/` 之下除外）。
2. 文件名：32 位十六进制主干（`[0-9a-f]{32}`）、`-<hash>.cs`、双扩展（`.animationclip.anim`、`.original.png`）、`unknown--*`。
3. 类名/命名空间前缀：`Original Source Recovered Monkey Generated`（Unity 来源原类型名本身例外）。
4. 原始二进制配置（`.bytes` 源表）、未编译初稿、源 JS。

检查实现为 `monkey verify --layout` 的一部分，生成后自动执行；命中即 `LAYOUT_FORBIDDEN_NAME`，状态不得为 pass。

## 9. Creator 3.8.8 工程（逐文件）

与 Manager `COCOS-FIVE-LAYER.md` 一致；目录全部小写，模块目录 kebab-case（与肥鹅现有 `goose-handbook`、`street-locks` 一致）。

```text
CocosProject/
  AGENTS.md  README.md  manifest.json  package.json  tsconfig.json
  extensions/monkey-import/         # 转换胶水，整目录可删（原位置不变）
  assets/
    scripts/
      bootstrap/
      domain/<module>/  gameplay/<module>/  gameplay/ports/
      presentation/<module>/  presentation/common/layout/
      services/{config,resources,network,storage,platform}/
    scenes/<SceneName>.scene  scenes/tests/  scenes/preview/ContentPreview.scene
    prefabs/<module>/<sub…>/<Name>.prefab
    effects/<module>/
    animations/<module>/
    art/sprites/<module>/…   art/textures/<module>/…   art/atlases/   art/spine/<module>/<skeleton>/
    art/materials/<module>/  art/shaders/  art/models/<module>/
    audio/{music,sfx,voice}/<module>/
    fonts/<family>/
    config/<module>/<Name>.json
    localization/<locale>/…
    mini-games/<name>/…
    resources/…                     # 仅动态加载证据要求的资产，内部同上分类
  Docs/  Analysis/  SourceRecovery/  # 同第 6 节
```

- 被源代码按动态键加载的资产（`Analysis/Mappings/dynamic-keys.json` 有证据）放 `assets/resources/<同分类路径>`，其余放静态目录。
- 现 `assets/art/images/Original/<包>/…`、`assets/audio/Original/…`、`assets/fonts/Original/…`、`assets/generated/{art,views,prefabs,animations}`、`assets/manual/` 全部取消。
- TS 初稿：`SourceRecovery/Code/Drafts/TypeScript/<layer>/<module>/<Class>.ts`；可接线的有据代码进 `assets/scripts/<layer>/<module>/`。

### 与工作区规范的差异

| 项 | GREA / Manager | 本规范 | 理由 |
|---|---|---|---|
| 图片类型目录 | `Images/` `Sprites/` 并列 | `Sprites/`（Sprite 导入）与 `Textures/`（非 Sprite） | 按导入类型二分，名称是 Unity 通用术语；`Images` 含义与 `Sprites` 重叠 |
| Unity 来源代码 | 五层 | `Scripts/<Assembly>/` 保留原程序集与类型名 | 原类型名是序列化身份，未经语义分析不能拆层 |
| 媒体文件命名 | 无证据保留原名 | snake_case 规范化原名，闭包内保持原名 | 统一风格且不改语义；闭包内引用不改写 |

## 10. 旧布局 → 新布局迁移表

| 旧（dev3 / none / grea） | 新 |
|---|---|
| `Assets/Generated/Art/<包>/<逻辑路径>`、`Content/Images/Sprites/<包>/Texture/…` | `Content/Sprites/<Module>/…` 或 `Content/Textures/<Module>/…` |
| `…/<name>.original.png` | `…/<name>_untrimmed.png`（仅被引用时） |
| `Content/Images/…/*.mp3` | `Content/Audio/{Music,Sfx,Voice}/<Module>/…` |
| `Assets/Generated/Animations/<包>/Anim/…`、`Content/Animations/<包>/…` | `Content/Animations/<Module>/…` |
| `Content/Animations/Controllers/<guid>.controller` | `Content/Animations/<Module>/<Owner>.controller` |
| `Assets/Generated/Views/Sources/<包>/Prefab/…`、`Content/Prefabs/Recovery/Sources/<包>/Prefab/…` | `Content/Prefabs/<Module>/…` |
| `Content/Config/Recovered/<包>/…` | `Content/Config/<Module>/<Name>Table.json` 或 `Content/Localization/<locale>/Strings/…` |
| `Content/Fonts/<包>/Font|Texture/…`、`Content/Fonts/Original/…` | `Content/Fonts/<Family>/…` |
| `Content/Materials/<guid>.mat` | `Content/Materials/<Module>/<name>.mat` |
| `Assets/Game/Scenes/Sources/main/main.unity` | `Assets/Game/Scenes/Main.unity` |
| `Assets/Generated/Scenes/ImportBootstrap.unity`、`Candidate.unity` | `Scenes/Boot.unity`、`Scenes/Preview/ContentPreview.unity` |
| `Assets/Monkey/Editor/*`、`Assets/Editor/Monkey/*` | `Assets/Game/Editor/Conversion/*` |
| `Assets/Generated/Views/Native*.cs`、`Presentation/Recovery/*.cs` | `Presentation/Common/Layout/*.cs`、`Presentation/Preview/ContentPreviewView.cs` |
| `SourceRecovery/CodeDrafts/{CSharp/snapshot,NamedCSharp}/*` | `SourceRecovery/Code/Drafts/CSharp/<Layer>/<Module>/<Class>.cs` |
| `SourceRecovery/Modules/<包>/*.js` | `SourceRecovery/Code/Modules/<Module>/<Class>.js` |
| `SourceRecovery/Spine/<包>/…` | `Content/Spine/<Module>/<skeleton>/`（有运行包）或 `SourceRecovery/Unconverted/Spine/<Module>/<skeleton>/` |
| Unity 来源 `Assets/Texture2D|Sprite|Material|…/*`、`Assets/uiraw|effect|actormodel/…` | `Content/<Type>/<Module>/…` |
| Unity 来源 `Assets/Resources/config/*.bytes` | `SourceRecovery/Config/<Module>/…` |
| Unity 来源 `Assets/Scripts/<Assembly>/…` | `Assets/Game/Scripts/<Assembly>/…`（游戏程序集）或 `SourceRecovery/Code/ThirdParty/…` |
| `Analysis/*.json` 平铺 | `Analysis/{Mappings,Ledger,Code,Readback,Tasks,Evidence}/…`（第 6.2 节） |

已冻结的 dev3 候选和两款游戏工程**不被修改**；新输出附 `Analysis/Mappings/layout-migration.json`（同 GUID 的旧路径→新路径），游戏工程可自行决定是否用 `AssetDatabase.MoveAsset` 迁移。

## 11. monkey 代码重构（文件级）

新增 `src/monkey/layout/`，是唯一决定输出路径和名字的地方；其他模块不得再写 `'Assets/…'`、`'assets/…'`、`'Analysis/…'`、`'SourceRecovery/…'` 字面量（测试静态扫描）。

| 文件 | 职责 |
|---|---|
| `layout/__init__.py` | 公开 `LayoutPlanner`、`LAYOUT_VERSION='monkey-project/1.0.0'` |
| `layout/standard.py` | Unity/Creator 全部固定目录和文件常量（第 4、6、9 节） |
| `layout/classify.py` | 源类型/导入类型 → `<Type>`；音频 Music/Sfx/Voice；JSON → Config/Strings/原件 |
| `layout/semantic.py` | 打包层、源类型词、语言、小游戏、模块推断（第 7.1 节） |
| `layout/casing.py` | 分词、PascalCase/kebab/snake、缩写、非法字符、长度 |
| `layout/allocate.py` | 大小写不敏感占用、冲突消解、闭包内保名（替代 `names.py` 的 `Names`） |
| `layout/overrides.py` | 读取并校验 `layout.json` |
| `layout/code.py` | 层/模块/命名空间推断（第 4.6 节） |
| `layout/records.py` | 写 `Analysis/Mappings/*.json` 与 `layout-migration.json` |
| `layout/verify.py` | 第 8 节禁止项检查 |

修改：
- `names.py`：保留为旧 manifest 读取兼容，新输出不再调用；`targets/layout.py` 同理（只读旧路径）。
- `targets/unity.py`、`targets/cocos.py`、`targets/prefabs.py`、`targets/common.py`：资源/Prefab/Scene/胶水路径改由 `LayoutPlanner` 提供。
- `package.py`、`package_code.py`、`code_emit.py`、`cocos_code_handoff.py`、`unity_code_handoff.py`、`handoff_package.py`、`resource_package.py`：SourceRecovery/Analysis/Docs 路径与代码草稿命名。
- `recover_unity.py`、`unity_bulk_prepare.py`、`unity_native.py`、`unity_handoff.py`、`bulk_handoff.py`、`providers/assetripper.py`：AssetRipper 导出后做一次带 `.meta` 的重定位（GUID 不变），再执行后续阶段。
- `formatting.py`、`formatting_unity.py`、`post_format.py`：新输出直接产生规范布局，`--format` 改为兼容参数（`none`/`grea` 都输出本规范并提示弃用）；旧候选的 resume/diff 仍可读取。
- `cli.py`：新增 `--layout PATH`、`layout-preview` 子命令；`verify` 增加布局检查。
- `targets/*.cs`、`targets/*.js`：胶水与组件的路径常量、`Monkey` 前缀统一、命名空间改为 `<Root>.Presentation.Common`。
- `scripts/demo.py`、`docs/ARCHITECTURE.md`（“建议目录”改为引用本文）、`docs/USAGE.md`、`docs/SUPPORT-MATRIX.md`、`README.md`。

测试（语义反例，不镜像实现）：分包/语言/源类型词剥离；同名不同包冲突与顺序无关；大小写冲突；闭包内保名；`layout.json` 覆盖与非法覆盖拒绝；禁止项扫描能抓到旧布局样本；同 sourceId 新旧布局 GUID 相等；配置 JSON 字节不变；mp3 不再进 Sprites。现有依赖旧路径的测试按迁移表更新。

## 12. 验收

1. 静态：两款游戏的完整输入各生成一次，第 8 节禁止项 0 命中；每个 Content 文件的类型目录与导入类型一致；同输入两次运行 `Mappings/assets.json` 字节相同。
2. 身份：与冻结 dev3（肥鹅 manifest `b8dde1e1…`、向僵尸 `f2410ed9…`）比较，共有 sourceId 的 GUID 全部相等；`layout-migration.json` 覆盖全部移动项。
3. 原生：在自有副本按既有原生窗口规则做一次 Unity 导入回读（代表子集：肥鹅 MainUi 与 1 个含 Spine/字体的窗口，向僵尸 1 个 UI 场景），Missing Script 0、引用回读一致。Creator 用 3.8.7 下方了样本做一次。
4. 文档：生成工程 `Docs/PROJECT-STRUCTURE.md` 引用 `monkey-project/1.0.0` 并列出实际模块表。
5. 状态分别报告：静态通过、Editor 导入通过、画面/业务未验证——布局整理不等于还原完成。

## 13. 实施顺序

1. `layout/` 核心 + 测试（不接 emitter）。
2. Cocos→Unity6、Cocos→Creator 资源/Prefab/Scene/胶水接入；`layout-preview`。
3. 代码草稿与 SourceRecovery 重排。
4. Unity 来源重定位。
5. `Analysis/`、`Docs/` 重排与旧候选兼容读取。
6. 两款游戏完整输入静态验收 + 原生代表样本；版本 `0.3.0.dev1`，更新 `docs/PLAN.md`。

## 14. 已确认决定

2026-10-25 用户确认全部采用“推荐”列。

| # | 问题 | 推荐（已采用） | 备选 |
|---|---|---|---|
| D1 | 媒体文件名风格 | snake_case 规范化原名，闭包内保原名 | 完全保留原名；全部 PascalCase |
| D2 | 语义改名方式 | 工具只做有据规范化，语义名走 `layout.json` + `layout-preview` | 工具内置启发式语义改名 |
| D3 | 重构范围 | 只重构目标工程布局及其生成代码 | 同时把 monkey 自身 `src/monkey/` 按 sources/targets/unity 子包重排 |
| D4 | `monkey` 分支起点 | 当前 `codex/native-layout-production-fix`（eb91533） | `main`（v0.2.0.dev1） |
| D5 | `--format none/grea` | 新输出统一本规范，参数保留为弃用别名 | 保留三种布局并存 |
| D6 | 向僵尸原始 `.bytes` 表 | 移出 Assets 到 `SourceRecovery/Config/` | 保留在 `Content/Data/<Module>/` |

## 变更记录

- 2026-10-25 初稿；同日确认 D1–D6，进入 `monkey` 分支实施。
