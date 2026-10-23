# 全量工程原名恢复

用户原生授权已核验：总监turn01a167a4-ae5a-76c0-bafd-0db3f9dd141f / human message01a167a4-ae8e-7bb1-adea-6f17d9cf2a4d。参考用户自有AssetDeoce/pkg/decoder/decoder.go的Config.Paths[index][0]路径/末段name行为，旧Go只读。不是来源没名称，而是monkey之前主动使用身份作为文件名；本次修源实现，不事后裸rename。

## 实现与边界

sourceNames保留config.paths优先和源_name/name证据，进入IR；共享Names分配用于双端图片/派生original/atlas、字体及TMP资产、JSON/音频、Unity源Prefab、动画、Spine骨骼/atlas/原页图、decoded原图和有据RF模块初稿。类型目录＋bundle命名空间＋原相对目录保留，GUID/UUID函数不依赖路径且未改。生成Gallery Scene不是单个原版Scene，不伪装成原名恢复完成；Creator独立Prefab仍未支持，源图以同名JSON交接。

仅真实重名/大小写/Unicode冲突采用语义类型后缀再短ID；derived original/atlas使用语义后缀。中文保留，跨平台非法字符/保留设备名/尾点空格作最小处理，超长段/路径有显式理由。绝对/父级穿越路径拒绝用于输出，回退unknown稳定短ID并记录原值及拒绝原因。未有名称证据不猜名字。原格式证据可以保留输入原相对路径，中间缓存仍可hash命名，不算用户目标资源命名。

所有meta/typed plan、字库相对页图、native保存目录/字体材质名、manifest、decoded evidence和handoff同步。新路径下导出器建立父目录；临时资源不按basename摊平，避免跨bundle同名丢失。JSON数值及资源载荷不做字符串重写；Bitmap fnt页面引用变化后同步typed receipt SHA。

Analysis/name-map.json描述目标计划路径，包含尚待Editor生成的Prefab/FontAsset；package-name-map为输入文件去向，module-name-map为代码证据/初稿，decoded-name-map为源对象证据，Spine map为闭包目录；分母分别报告，不把计划数当磁盘原生对象。

## 实样命名预览

.private/full-foodstreet-audit-01/naming-preview.json为真实config.paths输入到同一分配器的预览；还不是最终生成结果。

|源路径|Unity目标|Creator目标|
|---|---|---|
|en:Texture/MiniGame/zd_txt_lose|Content/Images/en/Texture/MiniGame/zd_txt_lose.png|assets/art/images/en/Texture/MiniGame/zd_txt_lose.png|
|gameAsset:Audio/BGM/bgm_Intro|Content/Audio/gameAsset/Audio/BGM/bgm_Intro.mp3|assets/audio/Original/gameAsset/Audio/BGM/bgm_Intro.mp3|
|gameAsset:Common/Guide/GuideHand|Content/Prefabs/Recovery/Sources/gameAsset/Common/Guide/GuideHand.prefab|Analysis/Decoded/gameAsset/Common/Guide/GuideHand.json（源图证据）|
|gameAsset:Font/en|Content/Fonts/gameAsset/Font/en.ttf|assets/fonts/gameAsset/Font/en.ttf|
|gameAsset:Config/woodgame.debug|Content/Config/Recovered/gameAsset/Config/woodgame.debug.json|assets/config/recovered/gameAsset/Config/woodgame.debug.json|

Spine闭包按SourceRecovery/Spine/<bundle>/<原路径>/<原末段>.bin或.json、.atlas及原名PNG页图组织；具体源版本与runtime边界不变。

## 只重建受影响阶段

新增公开convert --reuse-source-stages：完全相同input-set/namespace和完整路径/字节/SHA，旧stage owner清单及每个文件实际SHA全部验证；仅接受当前算法或已审阅838d05b→source-name-metadata-v1迁移，写明父阶段算法/manifest身份。旧候选只读，新目录建立元数据、两端plan/emit及所有引用；源读取/归一化像素不重跑，已恢复源码也按原解析器算法/owner回执复用。Spine页图按骨骼/atlas/纹理来源SHA及旧目标owner实际SHA复用；不是不看签名直接复制旧输出。

16项相关检查通过，覆盖名称/中文/大小写/保留名/路径穿越/目录名/扩展名、JSON载荷与引用、相同源码证据复用、输入变化及stage手工漂移拒绝、Spine页图零重复解码。当前SDK C#离线编译02 pass且SHA对应当前导入器；无Editor执行。

当前全量04保持冻结（c084c8c6…/ab1673be…）；下一新命名全量05使用同一输入/namespace和公开CLI复用源阶段，最终原路径可恢复/仅名称/消歧/回退统计与实际工程路径待本轮生成核验补录。名称正确不当作原生保存重开或业务通过。

## 全量05实际结果

公开CLI于本轮实际完成：

```sh
bin/monkey convert --input-set .private/full-foodstreet-audit-01/inputs.json --target both --namespace foodstreet-full --reuse-source-stages outputs/full-foodstreet-04 --out outputs/full-foodstreet-05
```

冻结emitter c3e97a3；Unity manifest SHA 975a7e2ab2ea185fb02daf668aa6c0793c95af63aaf635e2b156eaae0961061c，Creator manifest SHA ebabd779a065fda0df872d800750cc187e79171726bc72a5e81d647f88ffe8d7。两端17201项/884709704字节全部有去向；双端静态verify exit0/零诊断，routing audit pass/零问题。

|命名分母|Unity|Creator|
|---|---:|---:|
|参与目标计划的逻辑资产|10962|8912|
|原config路径可恢复|10663|8618|
|仅源名称可恢复|38|33|
|无可靠名称回退|261|261|
|分配目标路径（含派生/待原生资产）|20100|18039|
|真实重名/派生绑定路径消歧|655|655|
|跨平台字符/长度处理路径|4|4|

该分母不是23955个全部源对象，也不是17201原始文件；未参与原生资源计划的源对象仍有decoded/原件账。Decoded证据22432项中原config路径22011、仅源名称52、回退369，11035处同逻辑名不同类型等真实冲突以语义类型后缀等消歧。914个RF代码区域全部有据源名，生成1828条模块证据/目标初稿路径，两端均零名称冲突；不是914个业务已实现。输入文件命名账17201条中9907映射config路径，7294保持输入原相对路径（含原本就编码的下载证据），不伪称这些都是作者可读逻辑名。

Unity17329条资源路径、Creator16978条资源路径均精确出现在最终owner清单；全部module/decoded/package路径及所有Spine文件精确匹配owner路径，未依赖macOS大小写宽容。全部目标文件无Windows保留名/非法路径、规范化全路径重复；计划目录大小写拼写冲突0。源图/原始JSON数值与所有非名称IR数据同04逐字段一致（仅排除sourceNames/来源路径与SHA/reuse元数据），name audit pass/零问题。

Unity17329个种子资源GUID、Creator16978个UUID与04逐sourceId完全相同。SourceReaderExecuted=false、pixelDecoderExecuted=false、sourceCodeParserExecuted=false；两端Spine1776/1776闭包、decodedPages=0/reusedPages=1776。没有重跑未变源读取/像素/AST，也没有启动Editor。

原名例已进入实际文件：Unity Assets/Game/Content/Audio/gameAsset/Audio/BGM/bgm_Intro.mp3；Creator assets/audio/Original/gameAsset/Audio/BGM/bgm_Intro.mp3。GuideHand.prefab是Unity独立原生保存计划，尚未落盘；两端实际decoded源图为Analysis/Decoded/gameAsset/Common/Guide/GuideHand.json。Spine骨骼/atlas和原名页图已按命名闭包落盘，不当runtime通过。

边界复测再补了CON.ttf等带扩展名保留名和大小写目录分配保护及c3元数据迁移白名单。05实际无这些边界冲突，保持c3冻结及其原算法身份，不为未触发边界重新全量导出；当前工具16项相关检查通过，C#SDK编译02对应当前导入器（无后续C#变化）。候选/当前实现身份分开，不篡改05签名。

证据：outputs/full-foodstreet-05-name-audit/audit.json，outputs/full-foodstreet-05-routing-audit/audit.json，双端*-check。可复跑审计：

```sh
.venv/bin/python scripts/audit_names.py --candidate outputs/full-foodstreet-05 --previous outputs/full-foodstreet-04 --out outputs/full-foodstreet-05-name-audit-new
```

整体仍needs_action/candidate：Unity字体/材质/1694独立Prefab保存/Scene重开和代表页须新窗口；Creator独立Prefab原生适配仍无，现有Scene链须实际验证；Spine runtime/动画/业务未通过。下一窗口以05冻结身份申请，旧窗口08及04不再启动。
