# 来源与依赖

- 编译格式解析核心改编自 GREA `src/grea/tools/cocos_assets.py`，本次只读快照 SHA-256 `ca0a2858d964f43f2423b309b3a89f14ef5bd84ad80afc2d68424e50f061c9d1`。当时 HEAD `48debf7cece25803a06cc3002ae73970a7773ddc`；这不证明工作树无增量。许可为 MIT，全文随源码和 wheel 保存在 [GREA-MIT.txt](../src/monkey/licenses/GREA-MIT.txt)。monkey 不在运行时 import GREA。
- SpriteFrame rotated rect、capInsets 顺序参考肥鹅保留的 2.4.15 `CCSpriteFrame.js`；旋转方向与冻结提取器交叉核对，使用不对称合成彩色块和中心偏移反例验证。未复制肥鹅专用 Tools 或私有图像进公开源码。
- 发布图标和奖励窗口样本只读取肥鹅已冻结 package/CDN 文件；每次 inspect 保留来源路径、版本选择、字节数、SHA-256，normalize 再核验。真实清单位于本项目 `.private/`，原件未写。
- [Pillow](https://pypi.org/project/pillow/12.2.0/) 固定 12.2.0。[texture2ddecoder](https://pypi.org/project/texture2ddecoder/1.0.6/) 固定 1.0.6 可选，仅使用 ASTC decode；BGRA→RGBA 按[作者文档](https://github.com/K0lb3/texture2ddecoder)处理。来源为 PyPI 官方索引，依赖安装只在本项目 `.venv`。未启用 PVRTC 等其他 codec。
- Unity profile 来自只读核对现有 6000.6.2f1 与 uGUI 2.0.0 清单。编译校验使用现有 Unity 引擎/Editor DLL 和现有 uGUI/TMP DLL，不复制这些 DLL 到产品，不运行原游戏或 Editor。此证据仅证明 adapter API/类型可编译。
- 本轮无远端仓库、推送、发布、全局安装、引擎安装或付费生成。Python 最低 3.11 的跨版本实测仍未执行；当前宿主为 3.14.7。

CONTINUE-01新增依据：冻结主包game.js的zh字体选择经人工只读核对，绑定JSON带整文件hash、字节范围及匹配source-manifest hash；没有执行或复制业务JS到产品。原TTF的字形覆盖由本项目标准库SFNT cmap4/12预检，渲染仍交给Unity原生字体接口。BitmapFont的逻辑字框及未缩放字距差异通过原字段和独立反例核对，转换器不嵌入Cocos运行时。

字段/default与字形坐标语义核对了Cocos官方明确tag的 [Widget](https://github.com/cocos/cocos-engine/blob/v2.4.15/cocos2d/core/components/CCWidget.js)、[Bitmap label](https://github.com/cocos/cocos-engine/blob/v2.4.15/cocos2d/core/renderer/utils/label/bmfont.js)；仅作格式/可观察语义参考，未复制源引擎实现到产品。TMP接口/序列化字段与RGBA bitmap材质行为只读核对现有uGUI包源码，并通过当前Unity程序集窄编译。

Creator 3.8.8新增目标按本机已安装3.8.8的`cc.d.ts`、引擎公开组件属性、app.asar内Editor/asset-db声明及肥鹅Cocos已有meta做只读格式核对；没有复制其游戏脚本或导入器实现。参考的image 1.0.27、ttf-font 1.0.1、bitmap-font 1.0.6仅用于对应profile的根meta，subMeta由原生importer创建并回读。Scene脚本入口遵循[官方扩展文档](https://docs.cocos.com/creator/3.8/manual/en/editor/extension/scene-script)，序列化调用核对本机EditorExtends声明；未启动Editor。

开发wheel构建使用固定`setuptools==84.2.1`（与上一候选构建器一致）在临时隔离构建环境执行，不修改全局Python。运行时仍为既有固定Pillow及可选ASTC provider。

有限动画子集只读核对官方2.4.15 [AnimationClip](https://github.com/cocos/cocos-engine/blob/v2.4.15/cocos2d/animation/animation-clip.js)、[曲线](https://github.com/cocos/cocos-engine/blob/v2.4.15/cocos2d/animation/animation-curves.js)、[easing](https://github.com/cocos/cocos-engine/blob/v2.4.15/cocos2d/animation/easing.js)、[WrapMode](https://github.com/cocos/cocos-engine/blob/v2.4.15/cocos2d/animation/types.js)的公开格式/语义：省略curve为linear，constant持有左键，默认Normal=1、Loop=2；未复制引擎实现。Creator当前TrackPath/VectorTrack/RealTrack/RealCurve/序列化接口核对本机3.8.8 cc.d.ts，Unity AnimationUtility对现有6000.6.2f1程序集编译核验；这不等于原生执行。私有真实Prefab/Clip与来源hash仅保存在.private/outputs，测试使用自造无美术fixture，无原游戏内容纳入Git。

包级增量：明文wxapkg头/索引算法参考GREA `src/grea/tools/unpack_wxapkg.py`（MIT），monkey独立实现额外连续区间、字节/数量预算与路径别名检查；APK用Python标准库zipfile，不执行原程序。不在运行时import GREA。

AST模块框架改编自GREA `tools/cocos/index-modules.cjs`，来源SHA256 `462ef1dcac57831c6f430bb86e46b5034405d1b5bedb2a6ddcf0eeafa5feea97`；monkey新增语法事实、显式多表候选和词法RF区域候选，非原运行时注册证明。固定vendored Acorn8.15.0 `dist/acorn.js` 原文件SHA256 `fdb08546776ec6228b03e8d02b40d4ab3255bae5f401adba7ff5dad927ac5c9c`；MIT许可随`licenses/ACORN-MIT.txt`和既有GREA-MIT保留。仅宿主Node解析，无在线依赖安装，目标工程不携带解析器。


## 2026-10-23 用户自有旧工具行为迁移

经授权只读核对AssetDeoce `ae49cdaa372f27a79776bace9c07a25478a4c489`中的
`pkg/bundle/file.go`、`pkg/decoder/config.go`、`pkg/asset/cc_asset.go`、`pkg/asset/cc_spine.go`。
本次Python独立实现本地cache/temp列表映射、精确版本与显式跨bundle依赖解析、JsonAsset真实payload保留。
未复制整个私有仓库或对其宣称MIT许可；未引入Go依赖、CDN请求、猜测音频/Spine扩展名或吞掉失败。
Spine原生闭包适配尚未实现。原始PSD等文件留存上限128MiB，不代表结构解析或图像像素预算放宽。
生成的受控阶段文档读取上限128MiB/800万值，原始普通JSON保持独立预算。

## 原始命名恢复（2026-10-23）

只读参考用户自有AssetDeoce/pkg/decoder/decoder.go的Config.Paths[index][0]→assetPath/末段name逻辑（Manager/.runtime/vendor-reviews/AssetDeoce）；未运行Go或复制私有实现。monkey自己的bundle reader已读取logicalPath，本次独立Python共享Names分配器将它贯穿IR、target plans和native保存路径。中文保留，路径穿越拒绝用于输出并给明确unknown回退，真实大小写/Unicode/同类型冲突按语义类型再短ID消歧；原始JSON数值和源字节不改。GUID/UUID计算不依赖显示路径。
