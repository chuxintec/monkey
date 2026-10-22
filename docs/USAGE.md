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

该命令读取导入器保存的 `Analysis/editor-readback.json`，不会启动 Editor。没有回读文件则明确 `EDITOR_NOT_RUN`、退出 1；检查 Sprite border/尺寸/GUID/fileID、节点尺寸/锚点/位置、缺脚本及保存文件 hash。画面对照和业务仍另行验收。Editor 首次保存的 Prefab/Scene GUID 以真实回读为准，**目前仅资源与脚本 GUID 确定性通过静态验证**。

## 支持边界

| 项目 | 当前结果 |
|---|---|
| UUID/压缩 UUID、短十六进制纹理 key | 已实现，畸形身份诊断、不修补猜测 |
| pack ordinal、import/native 版本、redirect | 已实现；未提供依赖 bundle 记 REDIRECT_UNRESOLVED |
| PNG/JPEG、ASTC 2D | 已实现；ASTC 校验 header、block、长度、像素预算，只有固定可选 provider |
| 旋转/trim/offset/originalSize/capInsets | PNG 语义反例及真实切片已验证；亚像素留白不能无损栅格化则记 SUBPIXEL_TRIM |
| TTF/MP3/WAV/OGG | 资源拷贝路径；TTF 的 TMP 字体创建未实测，不静默替换字体 |
| Node/RectTransform、simple/sliced Sprite | 已实现 typed IR 与原生 adapter，真实 Editor 未验 |
| Label | 显式匹配 TTF 时生成 TMP；缺字体不造替代文字，行高/度量仍需对照 |
| BitmapFont、富文本、Button、Mask、ScrollView、Widget/Layout | 保留定位和缺口，尚无原生映射 |
| Animation/Spine、自定义脚本、事件 | 不生成空回调或假业务；交 AI 包 |
| Cocos 3.8.8 输出、diff/apply | planned，CLI 不伪装提供 |

`candidate` 表示本命令的离线范围完成，不表示游戏可玩；`partial` 表示已出报告但存在诊断。退出码 0/1/2 分别为声明范围完成、有待处理诊断、参数/IO/协议错误。所有阶段创建新目录，不覆盖输入、旧候选或人工文件。

计划资源、源文件及候选清单均带 hash。静态 verify 会检测包清单等生成文件的修改；Editor verify 允许引擎生成的 meta，只接受与保存回读匹配的 hash。当前不提供 apply，不能宣称已有完整增量合并能力。
