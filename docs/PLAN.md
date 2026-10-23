# monkey 项目计划与执行进度

完工/阻塞/交付与续推按[DIRECTOR-CONTINUATION](/Users/wangmeng/Documents/Manager/standards/DIRECTOR-CONTINUATION.md)执行；本聊天已原生核验人类授权`01a166b4-5c18-78f3-8cc2-c0d07dd46a20`，总监路由`01a14c8c-6402-7d03-bab8-ec7ea8051abf`。更新本PLAN后以稳定事件ID报告，已批准就绪下一包连续推进，不因报告或普通ACK停下。

## 当前：全量原生差异收口，代表探针后集中复验

最新全量实际依据为 `outputs/acceptance/full10-unity-window-01/UnityProject`：1694独立Prefab/24784节点/16934 Sprite/16原字体保存、Scene及editable roundtrip完成、Missing Script0。严格回读剩243项NODE几何差异，字形/字体atlas与material/10508 View引用/版本差异零；旧full07的2005项保留历史（613几何/834字形/557引用/1版本）。尚未几何/视觉/业务通过。冻结候选与acceptance实际工程、历史失败目录分开保留。

最新Unity探针04实际16原字体/3 Prefab/76节点、Scene重开/编辑重开完成，8 Label字形、5 atlas/material绑定及节点几何回读全部通过，零诊断；整体partial仍保留业务和源组件缺口。Creator探针02已通过显式CLI自动方法、16原字体/3 Prefab/76节点/Scene保存重载的几何及引用核对，editor/static pass、零诊断；没有原版画面对照或业务通过。所有本轮自有child已退出并回收。

全量新Unity10已生成：`outputs/full-foodstreet-10-unity/UnityProject`，manifest05c028933feb5329b41a6964f76b73d58edae1b6ffceb073706932e28418754a，static/name/routing零问题，17201文件/884709704字节全入账、17329种子身份稳定、1694 Prefab计划、1776 Spine闭包全复用，源reader/像素/AST不重跑。121份无法由单一标准uGUI横向对齐保留的源Layout明示handoff，20多Layout冲突继续保留，不能把保留几何称布局行为已恢复。

Creator02方法62.123秒处理67资产，逐图刷新/顺序保存不能直接假设满足全量窗口。当前批处理修复：去除就绪后逐图重复refresh、仅变更meta、8路有界提交/16路身份查询与原生load、Prefab父目录统一刷新及8路独立保存；仍使用原生分配subresource UUID、实际保存后严格回读，失败停止新调度并等待已开始项。新增API计数/耗时证据。12项定向检查及JS语法通过，小探针03已static pass，原生性能/语义待验。下一步Unity10全量→Creator03小探针顺序验证，再Creator全量候选；不放宽任何回读标准。

CLI通用CDN获取、更多来源profile及完整游戏业务仍未交付；肥鹅明确URL获取回执已补入原项目。用户目标矩阵为所有Cocos原包→Unity6/Creator3.8.8/both；所有Unity、Laya/LayaAir、Egret、自研/其他引擎→Unity6，按实际profile逐个实现，不以范围代替已支持能力。

## 历史依据与全量候选记录

用户原生授权已核验：总监turn01a16781-e3f9-78d1-9fcd-001f73f41486 / human message01a16781-e596-7581-9fd9-76378aef0afb，要求使用monkey完整转换肥鹅全部资料并核对排查。合同为Manager/decisions/20261022-monkey/FOODSTREET-FULL-CONVERSION-AUDIT.md。

此前四根5097文件仅为局部输入，不是全资料分母。当前对账Evidence清单17216项/905618352字节与source17097项、冻结package-snapshot、plain包、decoded-config、获取缺口和参考资料；原件只读。全新显式input-set经公开CLI生成Unity6/Creator3.8，逐项路由与重复映射、原生/代码/视觉分层核对。旧08/07保持冻结，不复用窗口08申请；实际全量候选就绪后重新报告资源需求。无新Agent，不改肥鹅产品/服务/GREA；联网仅限追加用户批准的明确CDN/配置地址，不扫描目录或装runtime。

用户原名授权已原生核验（总监turn01a167a4-ae5a-76c0-bafd-0db3f9dd141f / human01a167a4-ae8e-7bb1-adea-6f17d9cf2a4d）。当前新命名全量05已实际完成：冻结c3e97a3，Unity manifest975a7e2ab2ea185fb02daf668aa6c0793c95af63aaf635e2b156eaae0961061c、Creator ebabd779a065fda0df872d800750cc187e79171726bc72a5e81d647f88ffe8d7。双端17201文件/884709704字节入账、静态verify/routing/name audit均零问题，非名称IR完全同04；Unity17329种子GUID/Creator16978 UUID全不变，两端Spine1776闭合/零页图解码且全复用。原reader/像素/AST均未重跑。

目标计划逻辑资产Unity10962（原路径10663/仅名称38/回退261）、Creator8912（8618/33/261）；每端655处实际路径消歧，914 RF模块全有据名。全部资源/decoded/模块/原件/Spine引用精确匹配owner，源数字JSON不改。详情validation/2026-10-23-original-names.md。当前工具补边界保护并通过16项相关检查；05不触发这些边界，保持原c3身份不为之重导全库。原生窗口以05为准，旧04/窗口08不再启动。

当前全量04已完成双目标生成与一次集中离线核对：两端17201项/884709704字节全部入账、静态verify零诊断、来源路由/保留字节零问题；23955对象、24784节点/28514组件、1694 Unity独立Prefab计划、8467帧、11 TTF/5位图字库、23 JsonAsset、1776/1776 Spine闭包。代码实现838d05b，914 RF初稿/业务未实现。旧4根5097与全量01–03均保留历史，不能用于覆盖当前分母。

当前full05已取得独立Unity窗口：monkey-full05-native-grant-20261023-01，锚点16:42:23，内部17:10:23、外部17:12:23（北京时间）不顺延。08:47Z通过正常exec审批启动隔离 outputs/acceptance/full05-window-01，方法1200秒，实际PID/结果以journal为准。字体→1694Prefab保存→Scene重开→回读待实际执行。Creator独立Prefab适配已接入：复用源图边界→原名独立路径、Editor原生序列化保存→loadAsset/instantiate重载→层级/局部几何/组件/字体图片及内部节点引用核对；静态14项定向检查通过，原生尚not_run。下一步生成Creator-only全量新候选，不重导Unity05。用户追加所有Unity源版本一律目标Unity6，支持程度逐profile验收。

人类追加CDN/远程包下载已执行：原16627 CDN文件全本地SHA核对、19实际GET中12同原件/7HTTP404，无新增可用文件。9 bundle均散文件且脚本原包内嵌；miniGame代码原包缺URL仍缺。肥鹅获取回执/README已补充，未动产品/角色/服务。详见validation/2026-10-23-full-foodstreet-audit.md的当前最终核对、P0/P1与复跑命令；下面早期状态是历史，不表示本轮阶段未做。

用户本聊天最新范围：Cocos所有版本原包→Unity6/Cocos3.8.8/both；Unity所有版本及Laya/LayaAir、Egret、自研/其他引擎原包→Unity6。当前肥鹅→U→C先收拢，后续逐来源profile接入；未知格式不假称支持。

## 当前总目标与阶段

用户2026-10-23批准：一个命令将wxapkg/APK及明确提供的Cocos本地资源集合导出Creator3.8/Unity6独立恢复工程；包含全部已取得资源、恢复源码与目标TS/C#初稿，按五层/类型归类，提供AI接续入口。最终产品不止单奖励页、手选asset-index或缺口报告。实际可打开、资源覆盖、代码编译、行为保真分别验收。

当前顺序：P1统一CLI与原生导入问题收口 → P2安全包级入口、全资源台账和标准化导出 → P3源模块/导出/依赖索引、双目标代码初稿 → P4真实打开编辑与AI接续核对。既有v0.1–v0.3作为历史切片验证，不替代该总目标。原生自动编排与失败阶段续跑仍待实现。

所有输入文件有去向：原生转换、可复制、重复映射、原格式待转、缺失引用、明确过滤。未知/无法编译部分进入工程SourceRecovery编译排除区，不能整个原包换名当标准化。仅对已明确支持格式恢复；用户已追加CDN/远程包获取，肥鹅已完成明确URL的实际GET/本地SHA核对；通用CLI还需接入有界获取与缓存复用，未知地址不得臆造。禁止执行原JS/动态库、破解未知加密或安装APK。

有限静态模块恢复、支持语义转写与TS/C#初稿属于范围；不承诺无损全业务转换，不生成默认成功/假奖励/真实原服连接。正式数值JSON保持唯一制作源，Prefab/SO只管理引用；两目标可分别搬走，原件/GREA/肥鹅仍只读，不新增Agent/引擎/付费模型/推送。

## 已归档：早期切片与局部包状态

以下为历史执行记录，顶部旧not_run/未实现描述不代表当前能力。当前进展以上方全量任务与末尾最新窗口结果为准。

## 当前在途 CONTINUE-04

正在将包级inventory接现有reader/同一IR/标准目录双目标，新增显式input-set与来源关系核验，并吸收用户自有AssetDeoce（`ae49cda`）的本地缓存清单/资源版本定位/JsonAsset载荷与Spine关联经验，统一Python；旧Go不执行、私有源不假标开源。多根实样扩大后发现一份PSD超过旧32MiB留存上限，首轮安全停止并保留证据；原格式留存与结构化解析预算分开修正，未知PSD不冒充原生可用图片。当前native仍not_run，不启动/申请GUI。

## 2026-10-23 当前包级增量

P2/P3已接入明文wxapkg/APK/资源目录全文件台账与双目标标准目录、源码AST/RF区域候选、源/目标草稿映射和AI入口。真实冻结主分包73文件/8,166,145字节逐项有去向，914个RF区域候选和每目标914初稿；外围上下文未恢复、12个源引用缺失仍保留；该实样AST配对未报告未匹配项，字符串计数不当作模块分母。不是整游戏输入，也不是914个业务已还原。

Scene/Prefab/SpriteFrame/Spine/配置的全量原生还原、跨本地分包身份合并、编辑器preflight/自动导入、包级续接仍未完成。下一包应将全文件台账与既有结构化reader/标准目录原生emitter整合，不把大部分对象保留Unconverted作为最终资源恢复完成。真实引擎验证继续等待明确独立窗口，当前不启动新引擎。

## 2026-10-23 用户一键 CLI 收敛

用户直接要求命令行一键转换，当前统一入口为 `bin/monkey convert --source SOURCE --target unity|cocos --out NEW_OUTPUT`，复用六个既有阶段；支持私有可复用 recipe、候选身份校验和原生回读续验。双目标合成流程、拒绝覆盖/原件保护、失败收据、源版本证据和续验漂移检查定向通过。

真实肥鹅冻结奖励切片已通过一条 recipe 命令生成 `outputs/cli-reward-01/project`，25资产、48节点、82组件记录、156诊断，静态pass，原生/视觉/业务not_run；默认needs_action。它来自当前动画支持模板，和冻结creator-reward-04的155诊断不混作同一验收。原生自动启动/导入尚未实现；失败中间阶段自动续跑未实现，已完成候选可续验。故尚未实现完整“一键原生转换”，下一个实现包应补编辑器preflight与受支持原生导入编排，并在获独立窗口后复验。

第二轮Creator实导实际发现 package.version 被3.8.8规范化、Mask默认inverted赋值引发空renderer错误，已作最小产品修复且保留原始失败证据；23/23图像frame meta已更新trimType，原生Scene/回读仍不存在，原字体加载出现fallback警告。01:30:06 UTC后已向总监提前释放前台，不继续操作或重启引擎。修复不等于原生通过。详见[CLI及第二轮记录](validation/2026-10-23-cli.md)。

2026-10-22，批准本地开发。**当前：M01离线子集已实现；M02/M03已补字体和首屏必要原生UI映射，真实Editor/画面对照未验，v0.1尚未完成。** 主开发者更新本文件的当前状态及下一步，历史成组结果简记引用，不另建平行台账。

## 历史阶段与验收记录

下列v0.1–v0.3描述记录各时期切片与not_run，不作为缩小当前总目标的依据。

## v0.1：Unity原生资源与界面样板

成组成果：`inspect → normalize → plan → export unity → verify → handoff`可以处理一个已声明2.4.15数据子集；支持从干净目录生成可打开、可编辑、可预览的代表工程。catalog/inspect/normalize/plan/export/verify/handoff已可运行；具体子集和not_run见USAGE及首批验证。

### M01 数据读取与确定性资源恢复

- 建立Python包、CLI、版本/能力声明和合成fixtures；reader按源工程JSON与2.4发布bundle格式分开。
- 解析bundle标识、压缩/完整UUID、pack索引、路径/类型表及引用，不执行JS。建立稳定source ID和哈希，精确定位错误与缺口。
- 首批处理纹理/SpriteFrame、普通音频、TTF字体与基本资源引用；发布纹理压缩格式仅启用已验证可用解码器，无解码器则列缺口，不安装未知程序。
- SpriteFrame还原rotated、trim/offset、originalSize和capInsets，保存来源及规范化图。不得只按rect裁图忽略原尺寸和旋转。
- 交付能力清单、资产引用图和可检查的图片/资源输出；相同输入及参数的语义产物稳定，生成时间放报告不混入身份哈希。

### M02 Unity原生工程和UI生成

- Python生成候选计划、资源与Editor导入指令；Editor薄层使用AssetDatabase/PrefabUtility等原生API保存，不手写大型脆弱Unity YAML。
- 优先覆盖Node变换、Image/Sprite、Label、Canvas/RectTransform、常规Button、Mask/ScrollView、已明确的Widget/Layout子集；每项支持等级单独登记，未知字段/语义不默默丢弃。
- 保持源节点层级、锚点、颜色/透明、显示层级与合法布局关系；复杂动态布局由AI补实现。字体与位图字库分路，未支持位图字体不悄悄替换为系统字体。
- 生成序列化View引用和有限预览入口；业务回调只列待实现项，禁止按钮“默认成功”、发奖或伪造服务器结果。预览页面跳转仅用于查看，明确不是原游戏业务通过。
- 确定资源命名、GUID稳定性和人工维护边界；移除转换期IR与源reader后，生成工程仍可编辑、编译和预览。

### M03 肥鹅代表样本与AI交接

- 样本候选：主棋盘/HUD、订单区域、建造详情、料理面板、奖励/物品说明弹窗。先完成一个包含图片、文字、九宫格、按钮/遮罩的页面，再扩至这些代表页；按真实资源可得性选取，不为“凑五页”发明结构。
- 先比较单项语义（Sprite偏移/九宫格/锚点/文本），再做实际引擎页面回读与原版同状态画面对照。截图受账号状态影响的文字/数字必须解释，不设盲目像素全相等门。
- 原版新取证不由monkey抢桌面执行，引用肥鹅已保存证据；缺证据时标观察缺口，不阻断离线解析开发，也不冒称保真。
- 每页生成AI工作包：已转换部分、缺失资产/组件、源位置、目标文件、允许修改位置、依赖、需要的规则/真实证据和最小验证。AI可从具体缺口直接开发，不重新写提取器。

v0.1出口：原件未变；支持格式及资源闭包结果明确；代表性Unity工程可导入/编辑/预览；具体未知项留存；AI交接包可直接指向目标文件；输出只在monkey隔离目录。不是完整肥鹅游戏交付，不要求修完所有业务后才交工具。

## v0.2：Cocos Creator 3.8.8输出

- 复用M01中间描述，不重新实现另一套2.4解析器。
- 增加3.8纹理/SpriteFrame/meta/UUID子资源、UITransform/UIOpacity/Layer、常见UI组件的原生映射；按Creator版本原生导入/保存回读。
- 使用Creator扩展/编辑器接口处理必须由引擎维护的元数据，Python负责计划与制品；不从2.4复制字段后冒称3.8工程。
- 选同一代表切片比较Unity和Cocos输出的来源与语义，再扩已有支持矩阵。浏览器验证优先，Mac原生包不作本版前置。
- 官方2.x迁移器可作为受限provider评估，但其输入偏完整源工程、代码迁移有缺口；不能把它当作已编译缓存通用恢复器。
- Cocos结果也是独立monkey输出工程，不写肥鹅Cocos目录、不恢复肥鹅Cocos产品开发。

v0.2出口：同一normalize结果可选择生成两个目标之一；Cocos实际导入/保存回读与浏览器代表页通过；未知组件/脚本仍有准确handoff；Unity既有有效能力按受影响范围无回归。

## v0.3：可持续增量与AI接续

- 增量识别资源/节点/组件变更，输出added/changed/removed/conflict；稳定源映射与目标ID，不靠文件名猜身份。
- 区分工具生成区、AI/人工区；检测目标hash被改就报告冲突，默认不覆盖、不自动删除。每次生成先candidate，再显式apply到登记输出项目；不写输入工程。
- 按实际样本扩展有限AnimationClip与事件清单；Spine按真实数据版本使用兼容原生runtime，不能随意升级二进制骨骼。授权和依赖另记录。
- 输出完整CLI帮助、可安装本地Python包、source/target支持矩阵、使用教程、代表样本结果和缺口。不自动调用在线Agent；GREA后续只经版本化CLI/MCP薄适配接入，当前不改GREA。

## 工作组织与估算方式

首期一名主开发者顺序完成M01→M02→M03，不创建常驻岗位。预计主成本在发布格式reader、图集语义和原生UI映射，不把已有代码行数等同可复用完成度。开发者完成首个有图像/字体/九宫格的代表切片后，依据真实未支持组件给出剩余工作量；不先承诺无证据的天数或自动化比例。

先做离线任务与合成fixtures，不等待Editor窗口空闲才开工；需要Unity/Creator真实导入时向总监协调独立工程和有界时段。平台差异或许可证问题只阻塞相关实测，不扩展为修改系统/安装引擎的默认授权。

## 当前执行清单（开发者维护）

| 阶段 | 状态 | 下一步/证据 |
|---|---|---|
| 立项与方案 | 已具备 | README、AGENTS及三份设计文档 |
| M01 解析/IR/资源 | 离线子集 candidate | 两类2.4.15输入reader、pack/redirect/来源hash、旋转trim九宫格、PNG/JPEG/可选ASTC；真实11张SpriteFrame与原件hash核验。真实源工程/更多native格式待扩 |
| M02 Unity输出 | partial，Editor not_run | plan/export、原生Editor适配器/View引用脚本、静态verify、离线C#编译已通过；48个组件有原生结构候选（含13个源空Sprite保持禁用）；5处文字、必要布局/按钮/遮罩已补，需独立Editor窗口 |
| M03 代表页与AI交接 | 离线partial | 奖励窗口36来源资产/48节点/82组件，11张SpriteFrame、原字体及160条诊断已按8个模块根因组交接；真实同状态页面/输入/AI业务补全未验 |
| v0.2 Cocos输出 | 实际资产导入partial，工程窗口绑定blocked | 25项资产已导入/根UUID匹配；Scene、5Label、编辑重开、真实页面尚not_run；见首轮验收 |
| v0.3 增量/交付 | 离线增量已实现，正式交付待验 | diff/register/dry-run/apply、manual/retained边界、事务备份及可移位包；引擎门槛仍独立 |

新事实更新本表与简短变更记录，历史引用不抹除。不要生成与本表重复的每日任务库或为每次点击生成集成JSON。

## 2026-10-22 首批实现记录

实现与证据见 [使用矩阵](USAGE.md)、[首批离线验收](validation/2026-10-22-offline.md)、[来源/许可](PROVENANCE.md)。9组定向测试、真实来源hash不变、静态候选、C#程序集编译和本地wheel移位导入均有回执；不把测试数或候选文件数当可用工程验收。

下一步顺序：协调monkey隔离Unity6000.6.2f1工程资源窗口 → 执行首个代表候选导入/保存回读，修复真实API或引用问题 → 依据真实BitmapFont/布局/按钮缺口扩映射，完成一个真正图/字/九宫格页面及有依据的对照。未拿窗口时可以继续字体/组件的离线解析和合成反例；不能擅自占用肥鹅Editor。首次跨聊天申请曾被自动审批拒绝；用户现已直接授权发送，进展与窗口申请已成功送达总监并收到核对反馈。窗口本身尚未释放。

当时顺序为v0.1出口前不进v0.2；该顺序已被2026-10-22用户后续版本指令（CONTINUE-02）替代。v0.1出口仍未通过；不发布、不推送、不自动安装引擎。

## 2026-10-22 CONTINUE-01：首屏字体与原生UI

按总监续包 `monkey-v01-visible-page-20261022-01` 在原奖励窗口范围继续实现，未等待跨聊天反馈授权。已解析原BitmapFont的90字形/44组字距与彩色描边图集，补齐源TTF目录式native路径和cmap覆盖检查；人工核对冻结脚本的zh字体选择，3处中文有来源hash/字节范围约束的显式字体绑定，2处数量使用原BitmapFont。5处文本均进入原生TMP候选，尚非实际渲染通过。

必要simple/sliced/tiled Image、父级全拉伸Widget、容器resize布局/均匀Grid、矩形Mask、静止ScrollView、Button自目标缩放Animator和LabelOutline候选已接通；13个实际源空Sprite转为禁用的原生Image，保留业务绑定缺口，不填白框或替代图。旧版44份art/meta的hash/GUID不变。unknown脚本、SortOrder/SortRoot、原点击handler仍交AI，160条明细按8组根因组织，条数不是还原率。

最新候选：`outputs/unity-reward-10`，继承首批`unity-reward-04`同一页面/namespace。窄编译见`.runtime/adapter-compile-15`；资源/来源/字体详证与边界见 [续包验收](validation/2026-10-22-reward-font-ui.md)。本轮仅新增/受影响检查，不重跑无变化的9组基线，不扩Cocos/Spine或Player构建。

下一步：获得总监明确释放的最多12分钟独立Unity窗口后，首次导入10号候选，保存Prefab/Scene/字体，读回图像边距、字形四角/字体GUID、原生View引用；执行原生克隆的编辑/保存/重开探针并捕获真实Unity PNG。若发现问题只修该影响点。窗口由总监接手协调，向肥鹅的协调授权仍待用户处理；本执行已获直接授权向总监发送申请且送达，不代转肥鹅、不启动第二Editor或抢焦点。离线字体/映射/报告开发已持续推进到待实导候选，Editor、同状态原版画面对照及工具v0.1出口仍待验，不因业务未实现无限推迟工具阶段。

## 2026-10-22 CONTINUE-02：后续版本接续

用户已明确继续后续版本，覆盖先实导v0.1才进入v0.2的旧顺序；`9a86f03`与`unity-reward-10`保留。v0.1依然partial，Unity Editor/画面对照not_run。

v0.2已以同一`reward-ir-11`及字体证据输出`outputs/creator-reward-02`：25个图像/字体资产、48节点、48个组件候选，155诊断按模块/根因成组交接；Python不增加源reader。资产根UUID稳定，图像子资源由Creator importer决定，离线只校验逻辑闭包，实际UUID闭包待回读。3组Creator定向检查和两份JS语法检查通过；没有启动Creator，也没有写肥鹅Cocos。详见[续包02验收](validation/2026-10-22-creator.md)。

下一步不等普通ACK：执行v0.3 manifest diff、登记输出与expected-manifest约束的dry-run/apply、人工冲突保护。引擎窗口仍未释放，不启动第二Unity或Creator。

## 2026-10-22 CONTINUE-02：v0.3 登记输出增量

已实现schema 1的diff/register/apply。当前工作区outputs登记基线，默认dry-run，写入必须expected-manifest与同一预览收据一致；source ID、稳定逻辑身份与内容hash区分。保护人工区与生成区人工改动，拒绝缺失、symlink、非规范路径、输入篡改、目标占位、跨profile/namespace和陈旧预览。移除项保留并标记retained；写前备份，普通中途写盘失败回滚并留journal。

8组增量反例与受影响Creator/目标输出检查共15例通过。真实奖励页仅在`creator-incremental-base`隔离副本先执行版本元数据更新，再执行Creator薄扩展更新，两次登记基线→diff→dry-run→apply→静态验证通过；不是业务变化或引擎实测。原`unity-reward-10`、`creator-reward-02`冻结manifest不变；增量验证后的最新可实导候选为`outputs/creator-reward-04`，Unity新导出兼容候选为`outputs/unity-reward-v03-02`。详见[增量验收](validation/2026-10-22-incremental.md)。

本次可离线推进的两个续包均已落地；v0.1/v0.2的真实导入、可编辑重开、画面对照与v0.3正式交付尚未通过，不能标为工具发布。引擎资源窗口仍未释放。没有新增引擎、服务、项目、Agent、外发肥鹅协调、全局安装或远程推送。下一步按明确资源窗口实导冻结Unity/Creator候选，处理实际失败路径；未支持的原生对象和业务仍按8组AI包推进，不自行扩新产品范围。

## 2026-10-23 CONTINUE-03：有限动画模块

按用户继续推动指令，等待引擎资源期间接续既有v0.3动画项；Unity/Creator实导仍优先，尚未获资源释放。原页面候选不改；未启动Editor，不代转此前被拒的肥鹅协调。

新增可选animationSchemaVersion=1及源cc.Animation clip/root绑定；同一IR可选一份Clip，生成双目标原生曲线计划。真实奖励页Rewards_Show的sineOut保持unsupported；从已有冻结bundle选CellBoxReward（1504）原Animation #16实际引用的CellBoxClicked（3225），0.5秒，根x+item的y/scale三轴/opacity共6标量轨道；两条active明确未支持。原件只读，新闭包和候选均在monkey。事件只给source定位/参数/待接线合同，真样本事件0、合成合同1，不产原生回调、不自动播放。

`outputs/animation-unity-02`与`outputs/animation-creator-02`静态pass、部分动画候选；每目标一个动画AI模块。6组本增量定向检查pass，Unity薄层窄编译pass、Creator JS语法pass；没有重跑无变化15项基线、重复全库hash或制作新wheel。详情见[动画验收](validation/2026-10-23-animation.md)。原生曲线文件/实际采样/播放/可编辑重开/画面对照仍not_run。

下一步仍为获得明确资源窗口后，优先实导已有unity-reward-v03-02/creator-reward-04，修实际失败点；该动画离线包不替代页面和原生工程门槛，不扩Spine/服务/其他引擎或新版本线。

## 2026-10-23 v0.2 肥鹅样本实导验收准备

用户明确使用肥鹅项目验收v0.2，按V02-ACCEPTANCE合同执行。冻结creator-reward-04的manifest与60个生成文件已核对，原样复制到`outputs/acceptance/v02-reward-01`；输入身份/来源/5个字体Label清单见`.private/v02-acceptance-01/input-identity.json`。冻结目录不作为Editor工程使用。

当前仅完成副本与身份准备，等待总监明确资源接管；不因Creator未运行或开发者idle自行开始。收到接管消息后首轮最多12分钟，仅Creator3.8.8导入/Scene保存回读/编辑重开/浏览器真实页面PNG及必要UI命中，不启动Unity、不验证动画新包或改肥鹅工程/服务/档案。没有原版同状态截图时视觉对照准确partial。现有实导/编辑/视觉状态仍not_run；这段准备不是验收通过。

## 2026-10-23 v0.2 首轮实导结果与释放

总监确认肥鹅操作者明确释放后接管，窗口00:16:46–00:26:52 UTC（北京时间08:16:46–08:26:52），606秒，早于12分钟截止正常释放输入。仅操作monkey验收副本，未改肥鹅Unity/Player/Cocos/服务。

首次受限CLI启动在macOS _RegisterApplication阶段SIGABRT；改用官方3.8项目参数--project、正常桌面权限后，Creator3.8.8/monkey-import插件加载，资产库ready。实际Creator写出25/25 imported=true的资产meta，25根UUID全部匹配，46个Texture/SpriteFrame子资源记录；尚未执行导入扩展的trim/九宫格设置和Scene创建。

实际控制阻塞：CUA按bundle ID和已安装版本路径只能绑定无标题的推荐Dashboard启动提示；Window菜单没有工程可选窗口，无法安全绑定/操作已加载的monkey工程菜单。Dashboard显示登录界面，未登录/未输入凭据。按总监收敛指令停止同条件重试和源码排查，Dashboard正常退出；Creator仍报告running，工程startup记录PID41840，无法安全绑定主窗口故未强退，现无人输入；总监已收到释放消息。

Candidate.scene/editor-readback/真实PNG不存在，5Label绑定、原生Scene保存、编辑重开、浏览器及UI命中均not_run；v0.2未通过。详见[首轮验收](validation/2026-10-23-v02-acceptance-round1.md)。后续须先恢复可操作工程窗口/工具绑定，再在明确新窗口中继续；后台不追加离线功能或把资产ready当作页面验收。

## 2026-10-23 一键CLI与整包结构化成组结果

用户再次明确要求命令行一键转换，统一入口`bin/monkey convert`已落地；支持源目录/明文wxapkg/APK、显式多根input-set、unity6/cocos38/both，以及哈希保护的包级续跑（含可信备份的中断恢复）。旧候选归档，拒绝覆盖人工修改。CLI帮助、README、USAGE已同步。

真实四根输入5097文件/243799340字节已完成双目标离线候选，13994对象经同一IR生成标准目录原生计划。20605节点/23373组件/5179帧/8 JsonAsset，坏图1项隔离；914 RF证据与合同按714工作批交接。具体统计/清单SHA和各口径限制见`docs/validation/2026-10-23-structured-cli.md`。13项受影响测试与Unity薄层离线C#编译通过；Editor/Player/视觉/业务not_run。

当前成组工作包完成但工具版本未交付。必要剩余：独立源Prefab原生生成、Spine闭包、编辑器预检和有界导入编排、真实引擎验收及支持矩阵扩展；缓存映射缺失摘要的最终报告汇总、阶段算法签名尚待补强。按已批准范围继续离线开发；原生验收需总监协调独立Unity窗口。本组向总监报告事件`monkey-cli-structured-20261023-01`，不以报告或礼节ACK阻塞已就绪离线任务。

## 2026-10-23 窗口03与离线差额

已按总监实际grant在12:23:13–12:25:12完成独立首轮启动尝试并提前释放。冻结932220d逐项核验、acceptance副本建立；Unity在资源导入前停滞，readonly database/系统IPC与token更新警告，entitlement已解析；根因未证实。仅本次PID97901普通SIGTERM结束、ps无进程，未重试/未操作肥鹅；所有import/save/reopen/readback仍not_run，已向总监释放报告。详见`docs/validation/2026-10-23-native-startup-and-closures.md`。

继续离线完成独立源Prefab规划/原生保存回读适配（冻结IR1630份/20305节点，2源Scene排除）、Spine显式闭包（30/31闭合，1缺bin，未装runtime）、只读CLI preflight、包/阶段算法签名和缓存缺失汇总。新增3项语义边界反例、structured3及package6通过，C#离线编译通过；新整包/native尚未运行。准备成组上报`monkey-prefab-spine-preflight-20261023-01`并给出正常审批下缓存/IPC访问的安全续验方案；后续Editor须新的窗口许可，离线已批准范围持续有效。

新整包04与公开续跑已实际完成：5097文件留存、双端30/31 Spine闭包、Unity1630独立源Prefab指令进入真实输出，emit身份核对当前源码一致；克隆根局部变换补正并离线C#编译通过03。缓存缺失包级集成反例通过。新的原生验收仍需下一次许可窗口；原03/窗口03副本保持不变。
最新04双端静态verify均0诊断，03冻结manifest再次核对不变；成组证据可审查，工具整体仍candidate/native未验。

## 2026-10-23 窗口04与批量导入

已按新grant于12:42:12接管04独立副本，正常exec审批后Unity初始化/资产导入实跑，不再停于readonly DB/IPC。12:54:08截止前发送普通SIGTERM，12:54:24确认自身PID8690退出，期间未继续试验/强退他人，已报告总监释放。import partial，sourcePrefab0，save/reopen/readback not_run，04冻结SHA不变。

离线定位11552次刷新/报告Total累计673.36秒、同GUID重复导入，改128纹理批处理+同步加载验证，finally配对StopAssetEditing；源Prefab目录不逐项刷新。补schema1阶段进度、显式预算/截止安全点和preflight精确planSHA检查，明确未实现原生原地续跑。边界测试4项、新C#离线编译03通过；实际加速与原生通过未验。证据`docs/validation/2026-10-23-window04-batched-import.md`，按冻结新候选准备后上报下一必要原生gate，不复用窗口04。
修复05全新双端整包候选已完成，emit身份核对当前cf9c012源码，原04冻结SHA不变。Unity固定SHA为292255cee09a6940b222ff592afe560a83d08eb108764de0f6be433f253e6d5d；05没有启动Editor，下一原生gate仍需新实际许可。
05双端静态verify已零诊断，成组修复/制品准备完成；按事件monkey-window04-batch-fix-20261023-01-complete向总监报告固定身份和剩余原生gate，不把窗口04复用为05许可。

## 2026-10-23 窗口05与TMP闭包

13:14:28接管05独立副本，正常审批设置方法600秒/UTC内部13:24:28/外层13:26:28；纹理方法推进完成10358个双变体Sprite，方法49.08秒到fonts6/8，首个新失败为TMP Bitmap shader不可用。Unity自行exit1、包装CLI exit6，13:17:39确认PID17274退出并提前释放。sourcePrefab0、save/reopen/readback not_run，05冻结SHA不变，无窗口重启。

离线证据确认Essential archive存在且原名shader正确，失败工程未生成对应文件；现有辅助方法的物理Packages目录/后备位置均缺。改注册包resolvedPath+实际内置uGUI2.6.0合同，显式Essential导入、同步刷新、原名shader/settings加载/GUID回执与具体未完成诊断，不换字体/Shader；时序未证实已闭合，待新窗口。structured3/包级6/边界4通过，当前SDK C#编译02通过。详情`docs/validation/2026-10-23-window05-tmp-resources.md`。本组只准备新的Unity修复候选，不重复Creator旧矩阵或其他产品。
TMP修复06的Unity单目标已生成，固定实现4deb5ea，manifest a14f9648201fac01534a8037b3aeca29dd8772d6cd5998eacd2824e573cf14b1，实际依赖合同/emit身份一致，原05SHA不变。准备按事件monkey-tmp-fix-20261023-01-complete上报；没有新实际窗口不启动Editor。
06有变化的Unity静态verify已零诊断；本组离线修复与候选准备完成，资源导入/字体/原生保存重开仍未验，提交总监协调有依据的下一gate。

## 2026-10-23 窗口06与异步接续

06实跑验证注册包/Essential archive身份正确，但资源发起导入后仍未生成，方法44.53秒在tmp-resources首个错误退出；13:43:56确认自身PID25790退出、提前释放（原13:43:44误填已更正），原06SHA不变。Prefab/Scene/readback not_run。

已离线改为importPackageCompleted/failed/cancelled事件驱动，等待时返回Editor循环，不同步判断发起Import等于完成；新ImportBatchAsync拒绝-quit。增加native-import CLI默认规划、显式执行时校验冻结副本并直接持有无-quit Editor PID、预算/总截止/自身普通退出/未退出attention、结束editor verify。菜单入口异步但不退出用户Editor，batch完成自行退出。补正常Scene关闭重开后回读；原地native resume不支持。

launcher3/structured3/边界4及SDK C#离线编译05通过，新执行路径没有启动引擎。新候选准备后报告总监，不复用窗口06；证据docs/validation/2026-10-23-window06-async-import.md。此为实际时序失败后的必要执行层变化，不是扩大平台/安装/部署范围。
异步候选07已全新生成，emitter08d5e98，manifest bc3305c8a624fa03319c6280508c71738dee9a42a9f0604c06cb8474f55c77e3，Unity静态verify零诊断，原06SHA不变。实际native-import默认规划返回processStarted=false、无Project；规划时间不代表授权窗口。宿主IO失败清理补丁与第四项模拟反例通过。按事件monkey-tmp-async-20261023-01-complete报告固定候选/新执行路径与未验项；没有新实际许可不执行。

## 2026-10-23 窗口07与一键CLI收拢

用户再次明确产品形态为命令行一键工程转换，沿现有convert --source/--input-set --target --out入口继续，不要求逐阶段操作。窗口07异步TMP资源完成事件及原名资源加载实际通过；14:26:42自身PID36070 exit1回收并提前释放。实际新错误是bitmap字体材质初始化顺序与batch无名场景Additive限制；Prefab/Scene/readback仍未验。

离线修复材质先赋值、专属batch干净初始场景Single替换与正常重开、菜单场景保护、Unity记录错误后安全点停止及仅hash回执。SDK窄C#编译通过，详情validation/2026-10-23-window07-font-scene.md。下一步冻结Unity单目标08并静态验证，向总监成组报告/申请独立新窗口；不重复Creator/旧reader矩阵，不自行重启Editor。

08已通过真实CLI新生成Unity单目标：outputs/structured-foodstreet-08/UnityProject，emitter e1eeb74，manifest SHA 7ff13ed2870653db5bcf0d1491b38e9aba6d1efab6b7775b12afa3e44f6ede4b。5097/5097文件与243799340字节全部入账；状态needs_action/candidate，convert按合同exit1。Unity静态verify exit0/零诊断，11项受影响检查通过；SDK编译source SHA与当前C#一致，07冻结SHA不变。没有新Editor执行。准备按monkey-font-scene-fix-20261023-01报告成果并申请新独立窗口，原生修复效果/Prefab保存/Scene重开仍待验。

全量来源审计已完成：17216项SHA/字节全部verified，无覆盖目录外新增/缺失；17201项884709704字节入转换，15项20908648字节参考排除，两个plain包27/72条与snapshot匹配。input-set SHA 1fef746ef5f4483aa9605da81aef4a8ed6cea736834b2024169a00c6aa60fff2，64b7c51公开CLI正在生成outputs/full-foodstreet-01双目标。审计见validation/2026-10-23-full-foodstreet-audit.md。

全量01已实际完成17201项双目标台账，但结构化阶段因等价缓存bundle索引重复而失败，不能作为工程转换成功。P1已定位并修复：相同语义索引先核验一致再按实际import/native树选择，保留全部原件和别名回执；冲突索引仍拒绝。新增反例通过，四项structured检查通过；阶段签名纳入structured编排源码，避免复用改变前逻辑。接下来新建02重跑受影响全量结构化链，01失败候选保留。

人类当前monkey聊天追加批准下载CDN/远程包并补充肥鹅；已实际GET19个已知端点，12响应同原件、7HTTP404，原16627 CDN文件全部本地SHA/长度verified，无新增文件。9远程bundle均isZip=false，脚本原包内嵌；miniGame微信代码分包缺少可下载URL仍缺。肥鹅Analysis/acquisition/monkey-full-20261023-01及Evidence/README已补回执，不改产品/角色/服务。缓存462个wxfile原ID因冻结目录移除usr/gamecaches前缀，按明确前缀重定位全与CDN同hash，原manifest未改。当前full02正在normalize，资源窗口尚未申请/执行。

全量02已解析23955源对象，包含1776 Spine、8467 SpriteFrame、1696 Prefab、358 AudioClip、23 JsonAsset；四个等价缓存索引已正确映射CDN。归一化实际输出约1.6GiB触发旧1GiB owned-output上限，阶段失败且保持证据；这是实际解码膨胀预算而不是漏源。仅whole-input输出上限有界增至4GiB，保留切片256MiB/原始解析32MiB/单文件128MiB/生成文档128MiB限制；生成IR70MiB在已声明128MiB元数据预算内。下一全新03继续，02不原地修改。

全量03实际生成双目标原生计划：23955源对象→24784节点/28514组件/8467帧/11字体/23JsonAsset；Unity13550、Creator12588组件可转换，仍为计划而非原生对象。二进制Spine1762闭包，14项实际是内嵌JSON而非缺源。已补JSON骨骼原样语义导出、atlas/纹理闭包，精确保留含3.8-from-4.0-from-4.1-from-4.2.43等源版本标签，不推断兼容runtime；真实14项定向复验14/14闭合。修正相同缓存索引导致逻辑资源重复/假缺失计数，按(bundle,index)合并定位证据，原件账不去项。14项定向检查通过；03冻结不改，按新实现生成04最终核对候选。

全量04最终离线成果/资源申请报告准备事件monkey-foodstreet-full-candidate-20261023-01。后续只在实际grant后推进必要原生gate；没有当前前置满足的额外源码扩展包，不为等待制造测试或新版本。

原名整改实现/16项定向检查及当前SDK C#编译已通过，文档validation/2026-10-23-original-names.md。准备固定实现后用公开--reuse-source-stages从838d05b全量04新建05：校验完整输入、旧source stages、源码证据与Spine页图所有权/SHA，只重建名称元数据和两端目标，不重跑源reader/像素/AST。旧04及所有历史不改；新工程原名覆盖统计和身份完成后申请新原生窗口。

已原生核验后续来源扩展授权（总监turn01a167c9-388f-7920-80b6-961ab237c0d7两条human）：当前肥鹅全量05原名包优先，之后U（指定最新打开向僵尸开炮的Unity来源）再C（下方了3.8.7＋旧格式），无需重问立项。SUPPORT-MATRIX.md/ENGINE-ROADMAP.md与ARCHITECTURE已落地；只读当前已知账号的指定Unity AppID包目录仅见修订273，尚未用正文核Unity版本/后端；Cocos3插件3.8.7字段已真实读取，正文待核。后续实现已批准，未标现有支持，不建游戏开发项目。

命名成组与后续路线文档已就绪，准备报告monkey-original-names-complete-20261023-01；申请05新Unity有界窗口（外层30分钟/方法20分钟/内部留2分钟，首错退出）及顺序Creator窗口。后台按已批准U路线继续当前指定Unity样本身份/正文/provider只读核查，不等ACK；实际资源grant优先。

## 2026-10-23 full05真实Unity窗口结果

monkey-full05-native-grant-20261023-01按绝对截止执行，隔离outputs/acceptance/full05-window-01；controller606dde0、冻结emitter c3e97a3。实际自有PID74906，08:48:02Z起、08:54:46Z exit1已reap，窗口立即释放。16934纹理设置后进入hierarchy，方法192.56秒在MonkeyImporter.cs:562 NullReferenceException停止；实际独立Prefab0、Scene重开未执行。字体目录有10个.asset不等于16字体全部验证通过。首新异常不盲重试；下一步定位组件构建空引用并定向修复，原05冻结。Creator-only06正在以11ccef4通过公开CLI、复用05源阶段生成独立Prefab适配候选。

## 2026-10-23 Creator独立Prefab与全量06

11ccef4已通过公开CLI生成Creator-only outputs/full-foodstreet-06-creator，manifest7c47d0b55c1c2d4acf108281214f76956365d3c216f866977661a4d21e7b238a，1694独立Prefab原名保存计划。17201/884709704全入账，静态verify/name audit零问题，IR非命名数据完全同05，GUID/UUID不变；原生保存与重开not_run。

Unity真实窗口发现10源节点各两份Layout。当前补双目标逐组件MULTIPLE_LAYOUT_HANDOFF保留几何而不选方向；Unity原生防御检查与ownedScene唯一场景清理修复。15项定向检查、C#显式程序集compile pass（.private/full05-layout-compile-01）；不代替Editor。下一步以完整输入复用06已验源阶段生成full07双目标：Unity新候选只为本次实际根因修复，Creator同步相同来源冲突保护，不重新解图/解析源代码。再核对差额与申请必要新窗口。

## 2026-10-23 full07生成与待验

修复emitter53a7256，outputs/full-foodstreet-07双目标完整生成。Unity manifest dcd023012d2cc6e6a9b276c2391ceae7af738e169e725ac53a535deac530df67；Creator manifest61e7d81006580f6039572b2d9197d68bb65a91dffcbcbb5949553ec3e2c5aca6。两端各1694独立Prefab计划，20份冲突Layout明确handoff，转换组件Unity13530/Creator12568；1776Spine闭包全复用、零解码，原reader/像素/AST未重跑。最终双端static/name/routing核对全部通过，零问题，非名称IR同05、GUID/UUID不变；原生/视觉/业务未验。已申请下一独立Unity/Creator顺序窗口；没有新grant不启动引擎。Unity05失败副本与Creator06冻结保留。

## 2026-10-23 用户暂停肥鹅后的实际续推

总监turn01a1680e-4f9f-7ea0-bebe-fd7c7bb513b3、人类message01a16811-5561-7060-b381-bb89e4ee4e8f已原生回读核验，明确批准full07独立Unity/必要修复/后续顺序Creator，每次≤30分钟、仅monkey自有工程。肥鹅暂停，不再等其窗口。read-only ps/lsof显示已有肥鹅Unity57758、Creator42007低活动，不关闭或操作；前台osascript探测不可用，本次只batchmode。

full07新隔离outputs/acceptance/full07-window-01已经正常require_escalated审批启动；接管09:24:03Z，内部09:52:03Z、外部09:54:03Z，方法1200秒。controller8c1ad0384efa971e92f1cf1617fe67384c32628d、emitter53a7256，固定manifest dcd023012d2cc6e6a9b276c2391ceae7af738e169e725ac53a535deac530df67，当前执行中。字体/1694Prefab保存/Scene重开及引用按实际读回，20多Layout保持handoff；退出后顺序Creator，不并发抢前台、不改肥鹅/GREA/服务/存档。

## 2026-10-23 full07 Unity实际退出

own PID86974已09:38:17Z正常exit0且launcher回收；原生方法613.60秒completed_partial。实际1694独立Prefab保存、Scene重开、原生预览/回读文件已生成。launcher后续Python验证遇editor-readback.json BYTE_BUDGET，不能报原生全通过；先离线扩到与全量计划一致的有界128MiB/8m节点并重核，不重启引擎。资源已释放，随后顺序Creator。另已据TMP源码确认未使用TTF空字符集误判，后续代码已修并C#编译通过，未改变当前冻结07。

## 2026-10-23 full07离线复核与Creator释放

Unity回读38,845,894字节，原生Candidate.prefab42,815,767字节；已将生成回读读取上限单独设128MiB/8m节点、原生文件改流式SHA，不放宽原始输入解析上限。离线复核得到2005诊断：NODE613、BITMAP_QUAD834、VIEW_REFERENCE557、ProjectVersion正规化1。真实1694独立Prefab、24784节点、16934Sprites、Missing Script0、Scene重开和editable roundtrip通过，但几何/文字/引用未通过，不能当还原完成。

Creator新独立outputs/acceptance/full07-creator-window-01，接管09:40:41Z，内部10:08:41Z/外层10:10:41Z。own PID91737于09:41:58Z启动并实际绑定新路径，资产导入首次发现5份fnt页图缺失：原生按字体同目录basename查找，当前布局跨fonts/images。未调用importCandidate、独立Prefab/Scene实际0。按首失败停止，09:43:08Z正常TERM own child exit-15已reap，资源释放，未动旧Creator42007/肥鹅。下一必要修复字体页图同目录、Unity原始Sprite变体引用与几何/字体诊断；新候选后按已批准同规则验证，不借旧窗口无依据重启。

## 2026-10-23 full08 Creator与位图atlas补核

16dbbb7已生成full08双目标；Creator manifest eeb9718a6b828b3d7d30cbe2ef61275ef7c4bd93692d265730067cc59297965c，static/name/routing通过，IR非名称不变。当前Creator新窗口outputs/acceptance/full08-creator-window-01，接管10:10:08Z、内部10:38:08Z/外层10:40:08Z；无Unity主进程、旧Creator42007低活动，正常审批后启动自有child，先核实际导入再调用方法。

审阅full07真实native-page.png发现白色字块，5个保存的BitmapFont atlas及material主纹理引用为0；旧字形几何回读未覆盖纹理GUID。full08 Unity不启动，保留中间候选。新增强同步atlas导入、版本/material/atlas一起初始化、保存后GUID硬校验及回读验证；C#编译/负面引用测试已通过，需新Unity候选验证，不能只因702个ink几何匹配即称视觉正确。

## 2026-10-23 Creator CLI调用缺口

full08 own520已在10:15:39Z正常TERM exit-15/reap释放；5份font imported=true且有library UUID.json，缺页图根因已由原生证明解决。CUA只绑定旧42007，不调用错工程菜单；未生成Prefab/Scene。

新增CreatorExecution显式执行器与native_creator host：仅CLI --execute设置专属环境，严格绑定新副本路径/manifest，等待本机Creator3.8.8公开asset-db.query-ready与scene.query-is-ready；deadline/方法预算、结构化进度与首错回执、normal TERM own child、原生后离线验证。普通打开/手工工程不自动执行。API依据为本机app.asar的builtin/scene/package.json及asset-db/package.json公开消息，官方扩展load生命周期；未改引擎。定向测试涵盖默认不执行、错误工程拒绝、成功/失败/超时、源漂移拒绝、只结束自己child与journal失败回收；真实自动调用尚待full09。

## 2026-10-23 full09自动入口与小探针

full09已完成双目标生成，static/name/routing通过。Creator manifest6cfdf3b778d06872bf08d986bb456cf7fb8b294cf943ab89264c450e0c4ed27f首次通过公共CLI启动own8150，绑定正确副本；就绪查询返回类型触发NATIVE_READINESS_SCHEMA_INVALID，实际方法未执行。正常TERM后30秒仍pending，原回执保留；10:38:43Z ps查无8150、后续全引擎查询为空，release-followup.json另记退出已观察但exitCode未知，不伪称launcher回收。当前补缺省/未初始化响应等待与实际值记录，双true才执行，其他类型拒绝；Cocos正常退出等待使用现有窗口清理余量，最多120秒不强杀。

Unity代表探针outputs/acceptance/native-font-geometry-probe-01含3真实源图/76节点、11 TTF/5位图字体，own5893已10:30:40Z exit1/reap，字体阶段首份atlas检查拒绝。原始atlas meta textureShape=2（Cube），默认Texture2D加载为空；新增明确Texture2D及合法初始meta版本，GUID保持。全量Unity09不启动，先用同一小探针验证，避免为此再导1.5GB纹理。探针02描述字符串误写four但组列表实际3，未实跑；探针03描述/组列表一致，后续以03为准。

## 2026-10-23 代表探针实证

Unity探针03于13:15:36Z启动own9923，13:15:55Z exit0/reap，方法2.10秒。3真实图76节点、16原字体、3独立Prefab、Scene重开与editable roundtrip完成；8 Label包括隐藏clone的字形/原atlas与material GUID均通过，557空Sprite共因在选择内无View引用错。仅剩gameAsset:0004370a-24bc-402a-9d80-b0664a84df2b#18布局节点几何不符，保持未通过，不放宽容差。原生截图保留探针acceptance；不推成全量已验。

当前顺序运行Creator小探针outputs/acceptance/creator-font-geometry-probe-01，67资产/76节点/3Prefab计划，manifest6783ac2f1057de8c05ef33af9ad14a53cf00c7d1fc378a7415ece5616c31f8dd；内部13:45:15Z/外层13:47:15Z，方法1200秒，只自有child。确认就绪返回和实际调用后再集中全量复验。

## 2026-10-23 Creator探针01实际保存及下一组修复

own10498于13:18:29Z启动、13:19:49Z exit-15/reap。方法63.168秒，显式CLI实际完成67资产/76节点/3 Prefab与Scene保存，在Prefab几何回读首个descLabel尺寸错误停止。离线读取保存的Prefab发现8个Label均为默认85.63x40，源44.17x32等，字体/string/fontSize字段真实正确；隔离Scene未刷新渲染测量是当前待验共因。不是字体丢失或就绪失败。新实现最终统一updateRenderData(true)，逐Prefab完整收集差异、逐项仍拒绝通过，不让首个差异遮住后续证据。

Unity探针03唯一List节点#18位置-297→-270，直接父VerticalLayout驱动横向时未考虑scale1.1。原生标准uGUI可通过childScaleWidth恢复；新增按全部活动子节点检验的精确cross-axis映射，非共同对齐明确handoff，不伪造已转换。当前全量793份启用无scale expansion线性Layout中661中心不缩放/7边缘/4中心带cross-scale可表达、121需要handoff（含其他冲突/子集限制，最终分母以新计划为准）。C# compile .private/cross-axis-compile-01 pass；17项相关检查通过。小探针04 Unity manifest fdc0a10f0ab064d0640d7c4d80c6b72fe399bd8be1eb7f614bf7006965c9a1d4；Creator02 manifest8c954ab6f36e2fd9c7ae07e06a2dacc9affb6848e812e92551f5b94e03c6e5c5，两个static pass，原生待验。

Unity探针04新登记：13:29:00Z锚点，内部13:57:00Z/外层13:59:00Z，预算1200秒；只读ps未见Unity/Creator主进程，正常审批启动新acceptance副本。不得顺延截止或操作其他进程。

Unity04 own11411于13:29:12Z启动、13:29:31Z exit0/reap；回读零诊断，76节点几何/8 Label字形和资源引用核对通过，整体partial保留业务/源组件缺口。Creator02新登记锚点13:29:42Z，内部13:57:42Z/外层13:59:42Z，方法1200秒；ps未见冲突主进程，只启动新隔离副本。

## 2026-10-23 代表探针均零差异与全量10就绪

Unity04 own11411已13:29:31Z exit0/reap，76节点几何/8 Label字形及原字体引用零诊断，Scene及editable roundtrip完成。Creator02 own12108于13:30:01Z启动、13:31:19Z normal TERM exit-15/reap，方法62.123秒，16原字体/3独立Prefab/76节点/8 Label/Scene保存重载、几何及内部引用验证通过，editor/static pass。不能由此称全量/视觉/业务通过。

Unity10全量生成emitter a0fd18b，完整输入与源阶段/Spine页图复用；static/name/routing均pass，无身份或原名漂移。Creator新增有界批处理只改编辑期流程，已有小探针02冻结；新Creator03 manifesta4908311bc31d68dfa414189d6c7c40cce93dd38894c337c8a57e1759864bf26，static pass，待有界实证，不无依据直接启动全量。

Unity10全量原生新登记：锚点13:37:42Z，内部14:05:42Z/外层14:07:42Z，方法1200秒。只读ps未见Unity/Creator主进程，normal exec审批后只启动outputs/acceptance/full10-unity-window-01新副本；首新错误保存后停止，只正常回收自有child，不顺延截止。

单命令编排增量：convert --native已接续全新包级生成→Unity/Creator串行原生段；每段独立28/30分钟绝对截止、1200秒方法上限，默认不启动，支持独立--native-out。所有Editor参数/输出重叠/已有原生目录在转换前拒绝；manifest与生成回执绑定，未退出/原生错误/回读差异停止后续段。生成回执不改，native-orchestration.json另记实际阶段；源业务/视觉缺口不晋升。5项编排语义检查与4项既有convert检查通过；真实单命令双端整链尚未另跑，底层同一native-import已由代表样本实证，不为包装层无新语义重冷启动。README/USAGE/capabilities改为当前子集实证状态，不再保留TMP/Creator自动入口旧not_run作为当前事实。

Unity10实际own14717于13:38:24Z启动、13:48:28Z exit0/reap，方法437.966秒completed_partial；原生回读39,246,800字节、46038文件。1694独立Prefab/24784节点/16934 Sprite/16原字体、Scene与editable roundtrip完成；1006 Label中855直接测量/151隐藏active-clone测量，bitmap glyph/atlas/material回读零错，10508 View字段回读零错，版本正规化零错。严格剩NODE243（旧613），无其他诊断；不能把显式handoff布局算已恢复行为。实际native-page.png已查看，彩色BitmapFont文字可见；全独立页聚合重叠，不作为原版页面或游戏视觉验收。资源已释放，下一步Creator03批处理探针及243几何归类，不盲重导Unity全库。

Creator03批处理探针新登记：锚点13:49:23Z，内部14:17:23Z/外层14:19:23Z，方法1200秒；ps未见引擎冲突，只启动新outputs/acceptance/creator-font-geometry-probe-03，manifesta4908311bc31d68dfa414189d6c7c40cce93dd38894c337c8a57e1759864bf26。验证同源67资产/76节点/3 Prefab，严格geometry/reference不变；首错保存后停止，不顺延截止。

Creator03 own16625于13:49:50Z启动、13:50:08Z normal TERM exit-15/reap；实际texture-metadata 59/67在0.114秒，但宿主validate_progress阶段白名单未同步新texture-metadata，NATIVE_HOST_FAILED。新错已保留，未到Scene/Prefab。补显式phase及未知phase仍拒绝的定向测试，6项通过；只需修宿主，不重导同字节候选，下一新acceptance04验证同冻结Creator03。

Creator批处理重验04（候选仍03）新登记：锚点13:55:23Z，内部14:23:23Z/外层14:25:23Z，方法1200秒；ps未见引擎主进程，controller4f2c13a已同步texture-metadata合同，同manifesta4908311bc31d68dfa414189d6c7c40cce93dd38894c337c8a57e1759864bf26，新outputs/acceptance/creator-font-geometry-probe-04。只正常回收自有child，不顺延截止。

Creator批处理重验04 own17180于13:55:39Z启动、13:55:55Z normal TERM exit-15/reap；方法1.715秒completed，3 Prefab几何/字体及内部引用通过，但外层严格Sprite回读失败。归类11 SpriteFrame存在旧trim/border，API证据保存meta 51次total195ms、folder refresh524ms只扫目录，不能代替逐资产原生重导入。新补公共reimport-asset(uuid)等待屏障，仍8路有界，个别Sprite差异输出明确expected/actual；5定向检查及JS语法pass。新候选04 manifest5cfc0a2644d9a68c994dff40611f8a3d19a49857ddb51820ae0fef243fa6cb06，static pass，需新独立验证，不把1.7秒当性能通过。

Creator批处理/重导入探针05（候选04）新登记：锚点13:59:01Z，内部14:27:01Z/外层14:29:01Z，方法1200秒；ps未见冲突引擎，仅新acceptance/creator-font-geometry-probe-05。固定manifest5cfc0a2644d9a68c994dff40611f8a3d19a49857ddb51820ae0fef243fa6cb06，首新错停止保存，不顺延。

Creator05（候选04）原生结果：own17562已正常TERM exit-15/reap，Verification editor/static pass且零诊断；67资产/76节点/16原字体/3 Prefab/Scene严格几何/字体/边框与裁切/内部引用通过。原生reimport屏障已证明确保批处理后metadata生效；方法时长与API计数见execution-result及editor-readback，不再沿用1.715秒失败数据。开始生成Creator-only全量10，复用Unity10已核源阶段和1776 Spine页图，不重跑源reader/像素/AST。Unity243继续离线归类，发现nested Layout重载时序与SourcePrefab仅count/missing证据缺口，后续补正常UI稳定后几何/引用核对；尚未宣称独立Prefab几何全通过。

Unity剩余243离线分类：74仅size/无直接父Layout、132仅position/父Layout、4 size+position/父Layout、8仅size/父Layout，25带自身Widget（18 size/7 size+position）。这些是检查范围而非已证明独立根因；9个几何变更布局无活动孩子，root Widget设计父尺寸及缓存几何另待判断。现有Settle在无ILayoutController的DesignRoot上强刷实际跳过下树；新增只调用真正原生LayoutGroup的有界稳定过程，未稳定8轮即失败，不循环追逐源期望。独立Prefab改直接SaveAsPrefabAsset自有子树，避免活动Instantiate初始化缓存；正常保存重载后新增逐节点几何与字体/Sprite/内部组件引用证据，旧full07/10只有count/missing结论不追认。

新Unity小探针05复用原normalize，仅7原图/413节点/502组件/70帧及全部16字体；涵盖旧3图、nested/empty Layout及Widget实际反例。manifest73aab725465ae1e80e4d47f3b70f1c9f1481b8b995b2769c064911d16c7d57aa，static pass；.private/layout-settle-compile-01 C# pass，18项相关检查通过。源码/像素/AST未重跑。Creator-only全量10已生成manifest7fb3a4b7f996da9402ae1ecc9f9b921ab874e49046b63ea86938d143e08c770c，三项离线核对在途。
