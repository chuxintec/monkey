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
