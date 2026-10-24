# monkey 项目计划与执行进度

完工/阻塞/交付与续推按[DIRECTOR-CONTINUATION](/Users/wangmeng/Documents/Manager/standards/DIRECTOR-CONTINUATION.md)执行；本聊天已原生核验人类授权`01a166b4-5c18-78f3-8cc2-c0d07dd46a20`，总监路由`01a14c8c-6402-7d03-bab8-ec7ea8051abf`。更新本PLAN后以稳定事件ID报告，已批准就绪下一包连续推进，不因报告或普通ACK停下。

## 当前：v0.2 实际实现与必要剩余（2026-10-24）

v0.1 已发布冻结；当前本地 `codex/v0.2`，未推送/发布。用户持续推进授权及本轮进度核查已原生核验：总监 turn01a16bea-fe5f-7082-9583-f3a7f0292b56 / human01a16beb-0267-79b1-9472-e1ced602d6ba。原生验证仍限自有独立副本与单次≤30分钟；单主开发，不唤醒肥鹅。

- 已实现：公共CLI统一输入/精确远端获取、按资源与版本隔离、具名有据C#/TS/JS数值子集、ProjectModel typed引用与可选none/grea格式、Unity来源受限原生恢复、Cocos2.1.1/2.1.2/3.8.7资源及部分图、Egret5.2.32自定义资源/图集。Research 11例尝试、9例不同范围输出、2例未导出、完整游戏0，详见validation/research-v02-status.json；候选数量不代表完整兼容。
- 补源：机智147的13091份精确远端文件已取得，19298项声明资源missing0，双端最新07静态零诊断（完整新版Editor/玩法not_run）；天命当前3包336缓存与Cocos3.4.1来源已冻结，旧archives缺源阻塞解除，版本专用reader/export待完成。灵画师核实Egret5.2.32，不记作Laya。
- 结构在途：Creator3.8.7开发期模板DAG/局部ID/覆盖解析已接公共IR/Unity计划；114/119图可结构解析，5图缺6个精确模板。Unity真实4Prefab/104节点/5关系及合成双实例/三层嵌套/Variant均完成保存重开、对应节点/模板未污染读回；Creator3.8.8同真实4Prefab/104节点/5关系及合成三层嵌套也已通过原生保存重开/UUID-fileID/模板SHA校验，严格0诊断。尚未恢复源脚本的partial与结构检查分开，详见validation/2026-10-24-native-prefab-relations.md。
- 当前下一包：动态Layout/Widget/Label状态变化、天命3.4.1公共双目标导出及真实输入集成。Creator仅根继承仍需专用资产合同，普通嵌套不再guard；真实代表中未出现根继承。真实mounted/removed出现时按具体结构解决；缺模板只接精确声明补源。
- 版本出口：上述必修结构/动态行为落地，逐case支持矩阵与limitations、CLI本地分发/安装和必要代表验证收口。未知受保护方法/不可支持引擎允许明确限制，不要求全游戏全业务恢复；不得把必修能力降为handoff结项。旧证据及旧未实现状态按下方历史读取。

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

当前顺序：P1统一CLI与原生导入问题收口 → P2安全包级入口、全资源台账和标准化导出 → P3源模块/导出/依赖索引、双目标代码初稿 → P4真实打开编辑与AI接续核对。既有v0.1–v0.3作为历史切片验证，不替代该总目标。显式原生编排已实现；失败的原生中间阶段自动续跑未实现，须保留失败副本并用新候选验证。

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

Unity10全量生成emitter a0fd18b，完整输入与源阶段/Spine页图复用；static/name/routing均pass，无身份或原名漂移。Creator新增有界批处理只改编辑期流程，已有小探针02冻结；历史Creator03 manifesta4908311bc31d68dfa414189d6c7c40cce93dd38894c337c8a57e1759864bf26，static pass，待有界实证，不无依据直接启动全量。

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

Unity布局稳定探针05新登记：锚点14:07:45Z，内部14:35:45Z/外层14:37:45Z，方法1200秒；ps未见引擎冲突。只新acceptance/native-font-geometry-probe-05，固定manifest73aab725465ae1e80e4d47f3b70f1c9f1481b8b995b2769c064911d16c7d57aa，首新错误停止保存，不顺延。

Unity探针05 own19228已exit0/reap，方法2.607秒；7 Prefab/413节点严格新增回读得到Scene NODE5、独立Prefab几何9，7份字体/Sprite/内部组件引用全部通过。实际UI稳定过程解决所选nested父size/childposition主差额，不追认全量243已解决。剩下source Banner无活动孩子319→0、空负spacing content145→153；根Widget隔离Prefab缺父尺寸→0；inactive Upon缓存1334被native anchor即时拉伸1440。

这些区别并非放宽比较：新增EMPTY_LAYOUT_HANDOFF保留空布局几何待动态内容adapter；全拉伸Widget必须有源父级且烘焙几何与源父/边距一致，缺父级/停用缓存差异分别显式WIDGET_PARENT_CONTEXT_REQUIRED/WIDGET_CACHED_GEOMETRY_HANDOFF。已有转换组件减少会单独报告，不把handoff算行为恢复。Probe06仍7图413节点，manifestd203d620ef86980569c239e843a719806ef351da9a00e08535b3b8e4642ff2f3，static pass，9项相关检查通过；C#未再改、沿用已核compile。宿主进度同时补已有components显式阶段，未知阶段仍拒绝。Creator10 static/name/routing已全部pass、身份稳定、源非命名IR不变。

Unity边界探针06新登记：锚点14:12:09Z，内部14:40:09Z/外层14:42:09Z，方法1200秒；ps无主引擎冲突，仅新acceptance/native-font-geometry-probe-06，固定manifestd203d620ef86980569c239e843a719806ef351da9a00e08535b3b8e4642ff2f3，不顺延。

Unity06 own19932已exit0/reap，7原图413节点的root Widget隔离上下文、空布局和inactive Widget反例按明示handoff闭合；剩仅OrderDrawerWindow一图Scene3/Prefab3。实际Banner的唯一活动孩子bigday.banner尺寸0x0，而父缓存319高（待原生广告内容填充），不是source child缺失。新增LAYOUT_CACHED_CONTAINER_HANDOFF：源线性容器缓存extent不等于明确活动子尺寸/边距/间距时保留源几何，待动态内容/lifecycle适配，不能用0高fitter覆盖。6项相关语义检查通过。下一集中Unity11应用，不为单字段再次冷跑小探针。Creator10三项离线核对通过，准备已批准全量独立窗口。

Creator10全量新登记：锚点14:15:31Z，内部14:43:31Z/外层14:45:31Z，方法1200秒；ps无引擎主进程，固定manifest7fb3a4b7f996da9402ae1ecc9f9b921ab874e49046b63ea86938d143e08c770c，新acceptance/full10-creator-window-01。仅自有新副本，metadata有界+原生reimport屏障，首错保留停止，不顺延截止。

下一Unity11在已有Scene/独立Prefab几何门基础上补原生localScale/Quaternion实际读数；新transformReadback=full-local-v1强制存在并核验，q与-q只作同一旋转精确等价，不改原.001容差；旧冻结候选无新标志保持原对账口径。7项几何/引用/批处理/占位语义检查及4 structured检查通过，.private/full-local-transform-compile-01 C#编译pass。新增只读回执不另冷跑一字段小样，随本次成组全量11验证。

## 2026-10-23 Creator全量RPC边界与新任务接口

full10 own20570于14:16:33Z启动、14:18:41Z normal TERM exit-15/reap；方法87.821秒，16978资产metadata/重导入/原生身份阶段完成后assemble触发SceneFacadeManager.executeSceneScriptMethod timeout（约30秒RPC上限）。实际独立Prefab/Scene0。API计数与耗时保存，错误保留；没有重跑原失败工程、没有顺延窗口或修改引擎。

新增CreatorJobs编辑期任务合同：beginJob只白名单assemble/readSaved，立即返回jobId；jobStatus短调用读进度；takeJob只消费完成结果一次。所有任务仍绑定nativeDeadlineMs，过期/首错停止、foreign ID/重入/未知方法拒绝；每256节点/组件及16 Prefab协作yield，Renderer资产加载不再占据一次长RPC。只把可转换组件/动画送原生任务，未转换数据仍完整留在冻结plan/SourceRecovery与handoff，不改分母。接口错误只记首行，避免SceneFacade把全plan参数灌入错误回执。19项定向检查和4 JS语法检查通过；新3图76节点Creator任务小探针01 manifest55a58f191c323c1e2ab7f620aa0809a86b0666fced709563f098b246b3f40270，static pass，真实新接口尚待验，不能把小样性能推成全量通过。

Creator短调用job探针01新登记：锚点14:28:00Z，内部14:56:00Z/外层14:58:00Z，方法1200秒；ps无冲突主进程，只新acceptance/creator-job-probe-01，manifest55a58f191c323c1e2ab7f620aa0809a86b0666fced709563f098b246b3f40270，首错停、不顺延。

Creator job小探针01 own23510已正常TERM exit-15/reap，方法1.811秒；真实beginJob/jobStatus/takeJob贯通assemble及readSaved，16原字体/3 Prefab/76节点/Scene实际保存重载，editor/static pass零诊断；新增合同不等于全量超过30秒场景已通过。Unity11三项离线核对全部pass，完整输入/非名称IR/17329身份/1776Spine复用不变，准备顺序全量新原生段。

Unity11全量新登记：锚点14:29:57Z，内部14:57:57Z/外层14:59:57Z，方法1200秒；ps无主引擎冲突。manifest a4e286808cae2d8b758a6fd9968d2542e05f5f6066276a78ff6b45d05ffaa9db，新acceptance/full11-unity-window-01，严格Scene/独立Prefab几何、localScale/Quaternion和引用核对，首新错停，不顺延。Creator11只离线生成，不并发引擎。

Unity11 actual own24527已exit0/reap，方法445.702秒，1694独立Prefab/24784节点/16934 Sprite/16原字体/Scene重开与editable roundtrip完成。新增独立Prefab引用门无错，Scale/Quaternion回读无新增错；仅剩同12节点的SOURCE_PREFAB_GEOMETRY12+NODE12，全为Grid相关。严格验证口径更强，不能把新增独立Prefab计为新源节点分母；原243→12 SourceNode差异，旧候选不改。类型为Grid方向对齐、scaled child、缓存容器与graphic布局最小尺寸，下一成组修复；不为单字段重冷全库。Creator11 manifest6ec3ea8804cc10415b22b021b990756dcbf94ba307a033a570b4a427d8f34f65 static/name/routing全pass，准备顺序新原生段。

Creator11全量job段新登记：锚点14:50:29Z，内部15:18:29Z/外层15:20:29Z，方法1200秒；ps未见引擎冲突，新acceptance/full11-creator-window-01，固定manifest6ec3ea8804cc10415b22b021b990756dcbf94ba307a033a570b4a427d8f34f65。短调用job已小样实证、全量仍未验；首新错误停/正常回收自有child，不顺延。

CDN通用CLI增量已接入：convert --input-set --remote-manifest（可带cache-root/native），原输入匹配SHA只读复用且不重复复制，新文件在独立acquisition根有界获取并派生输入集；失败/404/身份冲突单列、原件不动；签名URL只留哈希及origin。4路、128MiB单文件/1GiB总量、明确origin跳转及30..3600秒预算；--offline只核缓存。每个新候选原生manifest最终封存前追加Analysis/acquisition证据并回写最终身份，不修改已有冻结候选、不改package/reader算法或绕过源阶段校验。6获取+5顺序编排定向检查通过，含模拟下载→实际合成转换→模拟native的完整单命令；真实通用网络传输待单独核验，原先肥鹅手工实际GET事实不借作该实现实证。

Creator11全量own28471于14:51:30Z启动、14:57:44Z normal TERM exit-15/reap，方法333.375秒；已完成1694独立Prefab和1 Scene实际保存，新的job架构已越过30秒RPC限制。readSaved首个层级差异为SourceRoot ProgressBoardHomeEntrance、原资产HomeEntrance.prefab被原生Importer规范为HomeEntrance（257份源根名与原文件名不同）；原生文件节点数/子级与UITransform存在，非丢节点。当前先核对全部原生文件的asset-basename规范，再显式定义根名policy/sourceRootName映射，不宽松跳过子级或几何。冻结失败副本不改。

Unity最后12节点Grid成组：childAlignment须随startCorner方向，Grid fitter使用MinSize防止图片preferred尺寸干扰；scaled child、缓存height与实际cell extent不符、sliced/tiled graphic minHeight大于网格extent分别handoff保留源几何。布局helper移回unity.py使现有target-plan算法指纹完整覆盖，不改source/signatures、不设绕过白名单。12项定向检查与C# compile .private/grid-direction-minfit-compile-01通过；9原图397节点的GridProbe07 manifest14ccc41556f06060db9f828ff889f7ca483da854bfc0fcc578121b29eddc931b，未重读源/解码像素/AST，待实际原生验证。

Creator11原生已保存1694 Prefab逐文件只读对账：1694/1694根名均严格等于原资产文件basename，其中257与源Root.name不同，未见其他命名值。新增creator-asset-basename-v1在plan冻结时给出sourceRootName/nativeRootName，序列化显式采用原生名；Scene源根名与全部子级仍保持源值，回读只在根应用精确规则，层级/几何/引用仍严检。新增单个成组handoff审查依赖Root.name的业务代码；不改文件原路径/UUID，也不隐去源原名。8 geometry/5 Cocos/3 Jobs/4 native-host/6 preflight与获取定向检查通过；native/foreign-child-name反例不会被根名规则掩盖。

通用获取层真实网络探针已执行：从已有明确Femsj配置URL实际GET 347021字节，SHA与原下载清单一致，downloaded1/missing0/无本地缓存复用；只写monkey/.private/remote-network-probe-01及回执，未改肥鹅原件。该结果独立于先前肥鹅19 GET/16627本地SHA，不借用旧事实；通用自动发现未知CDN地址仍未实现。

Unity Grid探针07新登记：锚点15:08:54Z，内部15:36:54Z/外层15:38:54Z，方法1200秒；ps无主引擎冲突，固定manifest14ccc41556f06060db9f828ff889f7ca483da854bfc0fcc578121b29eddc931b，新acceptance/native-font-geometry-probe-07，9原图397节点，首错保留/正常回收自有child，不顺延。其后顺序Creator根名4图85节点小探针，未盲跑全库。

Unity GridProbe07实际own29881已exit0/reap，9原图397节点、全部16字体、Scene及独立Prefab的几何/scale/quaternion/引用严格回读零诊断，整体partial保留未转换业务/源组件；最后Grid组修复由真实Editor证明，但全量12仍待集中验证，不追认full11原12已消失。随后顺序Creator RootName四图85节点小探针，不并发Editor。

Creator根名Probe01新登记：锚点15:11:56Z，内部15:39:56Z/外层15:41:56Z，方法1200秒；ps无主引擎冲突，固定manifest7b054a5efe2635bdd7f4750f0c8ccfe9a56f05f10f4049a3537753d631d482cd，新acceptance/creator-prefab-name-probe-01。4原图85节点、16字体、含原生规范根名反例，严格子级/几何/引用不变；首错停/正常回收自有child，不顺延。

## 2026-10-23 full12单命令端到端验证登记

Unity GridProbe07实际397节点/9独立Prefab、16字体、Scene保存重开、完整位置/大小/pivot/active/scale/quaternion/引用回读零诊断，own29881 exit0/reap；Creator根名Probe01实际85节点/4 Prefab/16字体/Scene、sourceRootName→nativeRootName规则及子级/几何/引用回读editor/static pass零诊断，own30462 normal TERM exit-15/reap。两端均释放。

新获取层另核肥鹅16627声明文件/799052150字节，SHA全部匹配、networkAttempts0、不重复复制，input-set原路径/SHA保持。加上真实347021字节的已声明配置GET/SHA证明，获取实现与模拟编排、真实底层两端样本分别记录，不宣称未知URL自动发现。

现在用公开单条convert --remote-manifest --native生成全新outputs/full-foodstreet-12，然后在full-foodstreet-12-native的顺序新副本执行Unity→Creator；获取在full-foodstreet-12-acquired，均不覆盖旧候选或原件。起步ps未见引擎主进程。每个原生段由orchestration在真正开始时固定UTC锚点、内部+28分钟/外部+30分钟、方法1200秒，写native-orchestration.json；不复用旧grant时钟、不顺延当前段，首错/未退出/非零回读差异停止下一端。生成期间持续只读资源状态，原生前复制阶段再次确认冲突。冻结候选/实际原生副本/获取证据分开；全量12当前未生成/未验，不将小样推成全量通过。

full12单命令生成在acquisition.attach读取已生成Unity manifest（63668683字节）时误用原始输入32MiB预算而安全停止，两个原生段均未启动；保留full12候选及获取回执，不追认端到端通过。修复只在acquisition采用既有stage_manifest的128MiB/8m节点上限，原始输入预算及source算法不改；新增33MiB生成manifest且owned文件篡改仍拒绝的反例，7项获取定向检查通过。下一次全新full13重跑公开单命令，不修改失败候选。

full13单命令继续生成中（acquisition 16627/799052150B全缓存SHA匹配）；自然安全点只读U样本：本机UnityPy1.25.3对Research同源data.unity3d的1603对象成功枚举，1326所选对象有严格TypeTree正文，包括76GO/76 Transform类；106 MonoBehaviour均因类型正文不足长度校验失败，未用宽松读取掩盖。私有typed-inspection-01含身份/正文/逐对象错误；现有AssetRipper2.0.0仅核--help，无独立export CLI，尚未启动服务或导出工程。此为后续reader探查，不抢当前全量验收、不冒称Unity来源已支持。

full13公开单命令已完成获取→双端生成→acquisition封存：每端17201文件/884709704B，Unity manifest80484c192bee73c172673fc3d0dfa87906d242149d061afaad3ed2dd6a8e02bb，Creator a840b6d50dc08ec198bf24dd05e7efbabcd4fe6d9f652eb165e77ce11acec58c。开始原生前再核ps无主Editor冲突；Unity段锚点15:40:33.784088Z，内部16:08:33.784088Z/外层16:10:33.784088Z，方法1200秒，不顺延。static/name/routing集中只读核对在途；获取清单零缺失不覆盖此前7个HTTP404/未知URL。

全量覆盖口径另核：节点24784/组件28514保持。Unity可转换组件11995→11988，新增7个明确Grid handoff：graphic最小尺寸4、scaled child2、缓存extent1；其余方向对齐/MinSize等仍由原生Grid实现。不能把这7项写成行为已转换。Creator可转换12568。双端1694独立Prefab计划、16原字体保持；静态verify、name与routing均零问题（full13-unity-static/full13-creator-static/full13-name-audit/full13-routing-audit）。Unity已实际进入texture-settings方法，own35982，后续回读待验。

full13 Unity实际own35982 exit0/reap、方法441.597秒；1694独立Prefab/24784节点/16934Sprites/16字体/Scene+editable保存重开，MissingScript0。强回读新发现同20个源节点Scene与独立Prefab各20几何诊断（合40），其余字体/字形/scale/quaternion/引用/版本零新增错误；旧full11的12节点不可追认已解决。编排按合同stopped，Creator未启动，ps无遗留主Editor。新增差异集中Grid的MinSize对子布局/多行容器的计算；先离线定位共同原因，再一组成对探针，不能盲重全库。完整失败副本及.private/full13-geometry-differences.json保留。

总监续派monkey-full13-independent-target-closeout-20261023-01：保留单命令失败即停合同；Unity已reap安全退出，可对冻结Creator13独立native-import关闭既有出口，不反复为Unity改动重生双端。Creator13新登记锚点15:54:00Z，内部16:22:00Z/外层16:24:00Z，方法1200秒；ps无主Editor冲突，新acceptance/full13-creator-window-01，manifest a840b6d50dc08ec198bf24dd05e7efbabcd4fe6d9f652eb165e77ce11acec58c。首新错停、自有child正常TERM/reap，不顺延、不并发Unity。后台仅Unity离线共因修复。

Grid共因已对照实际UGUI2.6源码：Flexible最小尺寸固定单行、preferred才依容器宽度计算行数；原生Image与Grid同priority0时LayoutUtility会混用图片尺寸。改为正常uGUI子类IntrinsicGridLayoutGroup，仅override layoutPriority=1，继续使用原生Flexible行列/方向/动态尺寸算法及ContentSizeFitter PreferredSize；无源图/IR解释器、不固定行数或写常量高度。4个Graphic metrics handoff改由明确原生适配覆盖，scaled/cached差异仍handoff。新增运行脚本跟随生成/标准路径/GUID及emit指纹，C#独立compile和8 geometry+4 structured定向检查通过；13原图成组探针生成，覆盖多行/嵌套/Graphic及此前9图反例，真实运行需Creator退出后顺序新段。

Creator13独立actual own38754 15:55:02Z启动、16:02:37Z normal TERM exit-15/reap；方法379.596秒，真实1694 Prefab+Scene保存/全量重载已完成，根名不再首错，强verify editor fail841：492 Sprite裁切差异、270 Prefab源节点几何（78份Prefab）、78份不verified及1聚合失败；不能把completed进度当验收通过。私有full13-creator-prefab-differences.json保留。Unity13失败20源节点与Creator270节点分别计；此后顺序Unity08成组探针、后台仅Creator离线归类。
Unity08新登记锚点16:03:00Z，内部16:31:00Z/外层16:33:00Z，方法1200秒；冻结manifest31b49cb02301eb989ee874f683580e3fb2d2d8af7c38fb4c8b212f1de03557bb，新acceptance/native-font-geometry-probe-08，13图646节点多行/嵌套/Graphic，已核Creator退出且无主Editor，首新错停、不顺延。

Unity成组Probe08 own42078 16:03:47Z启动、16:04:10Z exit0/reap，方法4.093秒，13图646节点/13独立Prefab/16字体，Scene+editable与完整几何/scale/quaternion/字体Sprite/internal引用零诊断，editor partial保留源行为缺口。IntrinsicGrid修复经多行/嵌套/Graphic实际证明，不能追认全量通过；后续等Creator共因处理后集中必要全量。
Creator差异离线归类：248个Label overflow0（既有baked尺寸与3.8自动测量不一致，含显著缓存差异，不能放宽容差）；18个纯Sprite尺寸，4个位置节点都为ScrollView content；492帧meta trim自定义字段正确但computed vertices仍旧自动裁切2px，需区分重导计算缓存与Scene资源缓存。将测实际固件，Label/Sprite无法等价自动尺寸行为需明确待适配，不把保留烘焙geometry称行为修复。

Creator共因修复候选：Sprite meta改custom矩形时移除旧computed vertices，由原生Importer重算，仍严格核rect/原尺寸/offset/border。ScrollView先设置enabled/axes再绑定content，避免默认双轴初始化改变位置（官方3.8.8 content setter会立即calculateBoundary）。Label新增显式source-baked-clamp-v1、原overflow0保留并列LABEL_AUTOSIZE_SEMANTICS_HANDOFF；缓存Sprite原sizeMode与帧尺寸不符时source-baked-custom-v1及SPRITE_CACHED_SIZE_HANDOFF，均是静态显示尺寸保留，自动尺寸行为未修复。新增Scene完整geometry/Scale/Quaternion/active回读marker，仅新候选要求，不追认旧Cocos Scene强验。7 Cocos+8 geometry、3份JS语法检查通过。
15图577节点/810组件/267资产/16字体/15Prefab sizingProbe01 manifest3875ceb47786522d75383de6d42a9d706e6cdc528297d1bf6c6d6534a23fabc6 static pass；含额外2个未使用alpha裁切Spine frame、原根名、4个ScrollView位置、TTF/bitmap/缓存尺寸。61 Label静态尺寸handoff/3 Sprite缓存handoff明确计，不算行为转换。新登记锚点16:14:15Z，内部16:42:15Z/外层16:44:15Z，方法1200秒，ps无Editor冲突，新的acceptance/creator-native-sizing-probe-01，首错停、自有正常TERM/reap、不顺延。

Creator sizingProbe01 actual own45954 normal TERM exit-15/reap，方法3.679秒，15Prefab/577节点独立+新增Scene完整geometry/scale/quat均零差异；原双alpha帧通过，61 Label/3 Sprite source-baked政策为明确行为handoff。仅剩miniGame bitmap atlas SpriteFrame矩形1项+聚合1项，字体JSON实际依赖SpriteFrame，不采用纯Texture替代。原生meta fullrect且无vertices，但library仍旧裁切；新增仅font-page的实际subresource UUID reimport（UUID来自native meta，不合成），并新增BitmapFont自身页的SpriteFrame/Texture/矩形独立回读。
新的15图相同分母Probe02 manifest92bec56220b96eff7c159c97f764a12ad6a4dccca2b4c3fb80ec7af4891cd7b4 static pass，7 Cocos定向检查通过；ps无主Editor冲突，登记16:22:45Z锚点/16:50:45Z内部/16:52:45Z外层，方法1200秒，新acceptance/creator-native-sizing-probe-02。首错停，不延长旧段、不变旧证据。

Creator sizingProbe02 own48074已normal TERM exit-15/reap，方法3.753秒；15Prefab/577节点Scene及独立完整geometry仍零差异，bitmap页新增强回读揭示3页与3个Frame裁切不符（+聚合=7），子资源直接reimport无效且已移除。字体本身确需SpriteFrame，未采用错误纯Texture路线、未发起该假设的原生段。新修正对完整图片矩形明确trimType=none（原零origin/零offset/size=originalSize），真实裁片保留custom；native页几何仍强检，不能靠meta字段正确冒称library更新。
Probe03仍15图577节点/16字体/额外alpha帧，重新冻结、static pass；锚点16:26:15Z/内部16:54:15Z/外部16:56:15Z，方法1200秒，已核无主Editor冲突，新acceptance/creator-native-sizing-probe-03，首错停、不顺延。

Creator sizingProbe03 actual own49235 16:26:47Z启动、16:27:07Z normal TERM exit-15/reap，方法3.772秒，editor/static pass零诊断：15图577节点/15Prefab/Scene强geometry/16原字体/5位图页引用与矩形、额外两个alpha原帧均通过。子资源直接重导路线已移除；完整图片明确none关闭裁切是有据原生策略，真实裁片custom不改。Creator clamp/custom只保留静态显示geometry，61+3 probe或预估全量1006+18 auto-size行为handoff不能记已恢复。两端成组出口就绪，将集中full14一次完整公开单命令验证。

full14公开单命令已完成16627声明CDN缓存SHA→双端生成→获取证据封存：每端17201文件/884709704B，Unity manifest65e59177410266aa075b13d58ac4991715e19cefa1d198821ed1b72d70b43a74，Creator eacbf1bfff274f9abb2d7dc64abc4b9537ca9863e32eaa26a060608e2f485cf6。原生前新ps无冲突；Unity段实际锚点16:35:20.404958Z，内部17:03:20.404958Z/外层17:05:20.404958Z、方法1200秒，不顺延。四项static/name/routing集中只读审计在途；完整原生尚未通过，不覆盖full13失败。

full14双端static/name/routing四项集中审计全部pass零问题，非名称IR保持/17329资源身份保持/1776Spine闭包及原图复用，reader/像素/AST未重跑。实际Unity own53301，16:35:36Z启动，固定内部17:03:20Z/外层17:05:20Z，不顺延；原生结果待验。U自然安全点只读600个明确.ab缓存128字节header，全部UnityFS/2021.3.30f1；仅header证据，不是600包对象解析/业务恢复，记录current-bundle-headers.json。

full14 Unity actual own53301 exit0/reap/方法475.455秒/强verify零诊断；之前full13同20源节点以及full11同12源节点差异已在本次新完整输入回读中闭合，旧失败副本仍原样，不追认。Source-prefab逐节点/Scene完整geometry、scale/quaternion、字体/图片/内部引用、字形/bitmap atlas/material、10508 View引用及版本门保留；业务/画面/Spine播放不晋级。当前公开单命令顺序Creator16:46:24Z新段，不改失败即停合同。


## 2026-10-24 v0.2 U精确依赖资源子集闭合

事件monkey-v02-unity-exact-dependency-20261024-01。当前codex/v0.2本地继续，不推送/Release；v0.1发布身份不变。600明确Bundle索引600/600、79977对象表项，不冒充正文全解析。FrameSpritePool三个外部Sprite依同文件external表和精确CAB/pathID唯一匹配；原型16个Sprite[]字段，原方法实现0。

显式依赖/本地精确缓存已进入公开convert：--dependency-source可重复、--unity-texture-cache指定冻结池。3纹理用固定texture2ddecoder1.0.6一次解码到RGBA32，无翻转，原始hash和非纹理对象raw hash保持。3 PNG像素hash精确一致；先前隐式ASTC最大1LSB失败比较独立保留，不放宽比较。新outputs/unity-source-with-dependency-02输入5文件529624B，候选manifest96226025fd017ea4728f245c0a2cfcfaca71843e5b143a6c653bc6c2bda9b695，deadbeef引用0。

原生probe03自有child67435、锚点2026-10-23T18:40:58.386769Z、内部19:08:58.386769Z/外层19:10:58.386769Z、方法1200秒，实际18:41:04.978708Z exit0/reap；16严格门通过：类注册、16字段/几何/GUID与十进制fileID、MissingScript0、3真实Sprite引用，独立editable copy保存/重导/重载引用保持。仅resource_subset_verified，原方法/视觉/玩法未验；公开Unity--native尚未整合。probe01/02冻结结果不变。

启动Bundle精确纹理仅3/4，缺Assets/Textures/astc/512/pangzhijiangsi.a976bf1d.txt（sharedassets1.assets/pathID4），另hashf656c6db不是替代证据。本轮hydration blocked，不写派生包/启动Provider或Editor。另106MB缺TypeTree、CODEPHPY保护方法仍在；向总监报告具体原件条件，同时继续v0.2具名C#/TS和typed格式化，不等待ACK。15项定向检查通过（首次命令缺PYTHONPATH后按src:tests正确重跑），不代替上述实际Editor结果。


总监source-assistance事件monkey-zombie-exact-texture-found-20261024-01后，核原包DATA_CDN明示URL与新增精确原件65552B/SHA6c11b424ba429c442664e0fc4eb212030fad8255800755bd894b3c96596fa018，ASTC8x8/512x512及长度匹配，复制到monkey私有池。104项新pool SHA887c4c3dc35d1f96dcfb9472c01827a46274232ae207f6e8b2ae26207319dcfb；startup hydrate02四键齐全、非纹理raw hash不变。公开startup convert02完成5输入3554576B候选、2484 Provider文件11019493B，自有child退出、原件不变，1173代码隔离/schema0/原生not_run；106MB和受保护方法仍不恢复。旧缺件状态保持。

代码具名输出第一组：code-emit --source --code-model --numeric-field value --cocos-code-language ts|js（默认ts）。重新静态解析核源/hash/方法语义，拒绝篡改模型；仅显式number调用子域的字段setter/getter生成非空实现，C#double?未初始化与TS undefined分别明示。NumberLabel真实6方法→2实现/4pending，待补不放空成功函数。箭头/async/generator函数不误判普通this方法。4定向反例通过，含仅运行生成JS验证undefined/负零/NaN/Infinity/独立实例/原Label字符串不变。真实输出C#compile通过，TS5.8.2/Creator3.8.8公开SDK target strict通过、错误字符串调用TS2345拒绝；官方SDK自身82项full-strict声明诊断独立记录，skipLibCheck只隔离上游声明，不放宽生成target。Creator原生注册/5引用与Unity5引用尚not_run，未并入convert，当前继续下一组。


NumberLabel Unity代表接线段登记：outputs/number-label-unity-bind-probe-02，MainUi129节点/5原脚本引用，实际资源GUID闭包132文件3297014B（其余7个GUID为包/内置或待原生解析，不假称全内闭合），生成方法+通用Editor验证器已编译。启动器先查ps无主Editor、仅自有最小副本；真实锚点启动前固定在native-plan，内部+28/外层+30分钟/方法1200秒，首新失败停止，不延长、不改full14或原源码。将验证数字边界/实例隔离、5 TMP引用/文字字体/全部节点几何及保存重载；当前尚not_run。


NumberLabel接线probe02 own69237于19:12:28.284136Z→19:12:36.937026Z exit1/reaped、saved=false：129节点/根GUID正确，但原五自定义脚本从未映射TMP组件，严格绑定前置失败。旧full14真实1006 Label不包含这5个，不能把不存在的目标文字组件当已有。源RF+IIFE cc.Label参数/构造别名/方法作用域现已静态绑定，原helper仍不执行；增加有限Label字段projection，非Label业务序列化字段出现即拒绝，原5组件身份/未知4方法保留。

同时核出Label序列化_N$overflow别名被旧normalizer漏读；已修精确别名/冲突拒绝，未重写旧IR/候选。原NumberLabel实际overflow2（SHRINK）保持，不能说原源模式0。新native03明确仅baked文本/数值读写：按原字串/原位图字体/颜色/对齐投射TMP，原SHRINK动态行为待补，不宣称视觉通过；位图bold沿既有源字形规则避免二次加粗。补齐实际字体/着色器include依赖，186文件4744978B。修正后新段仍先ps无冲突、独立新副本、实际锚点+28/+30/方法1200秒，首次新失败停；不会重跑旧失败副本。


接线probe03 own69932于19:18:52.806299Z→19:19:01.434561Z exit1/reaped、saved=false，原件不变；创建TMP阶段空引用。离线核精确UGUI TMP_Settings源码：AddComponent初始化必需Resources/TMP Settings资源，前一最小闭包漏掉该隐式入口。新probe04在显式原资源闭包加入原TMP Settings及其GUID递归依赖，新增强前置TMP_Settings.instance/阶段与完整异常回执；不以加判空跳过Glyph门。不改旧副本，ps无冲突后新+28/+30/1200段，首次新错停。Label SHIRNK动态行为仍handoff，数字方法与静态文字/字体/几何分别验。


probe04 own70396于19:20:54.346031Z→19:21:03.474011Z exit1/reaped、saved=false：TMP Settings前置已过，首个glyph门失败；保存副本与原件均未改。原Prefab没有Canvas，沿既有已实证ReadSavedLabel的隔离active Canvas clone测量策略修正新验证器，全部源树保持inactive/几何不动；不删glyph门、不增容差。新probe05已独立复制并编译，仍相同显式5字串/原字体/129节点，新的有界段，不在失败工程重试。

离线source字段审计另证：full14原生1006个converted Label中89个有未读到的_N$overflow非零（85为SHRINK2、4为RESIZE_HEIGHT3），原native几何/引用通过事实保留，但源overflow=0说法对这89个不成立；动态behavior原就not_run/handoff，不因此晋级。旧v0.1/IR/候选不改，v0.2新reader已精确读别名，需按真实模式重建后验证。


NumberLabel Unity probe05 own70833于19:23:17.534061Z→19:23:27.140130Z exit0/reaped；129节点、根GUID0eaedff19bd76487f9f32a796d094f94保持，MissingScript0，5个真实源脚本→NumberLabel+原字体TMP引用绑定/独立状态/数字边界/未初始化状态通过，保存重载5处绑定全在、全部节点几何保持、源full14 Prefab SHA不变。原script四未知方法、SHRINK动态字体行为、原版视觉/交互仍未恢复。glyph采用隔离active Canvas clone强验，不改原树。probe02–04失败均冻结，不追认。继续Creator TS真实注册/5处原生绑定；未并入公开convert。


Creator NumberLabel TS原生段准备：candidate03仅MainUi129节点、同5原RF组件，重新投射原Label序列化字段；明确native CLAMP静态几何策略，原SHRINK2及4业务方法仍handoff。有限code adapter以注册类实例/原字体/字串绑定，不执行源JS/helper。通用Editor模块先检实际class注册/数字边界/实例隔离，再保存Scene+独立Prefab、重载核实际classId/原组件映射/未初始化态；未导入TS meta标native_assignment_pending，读回真实ID，不捏造稳定UUID。25定向检查通过（新增可选模块依赖已在旧非code几何路径按需加载，未削弱几何反例）。只新outputs/number-label-creator-native-01，先ps无引擎冲突、启动锚点+28/+30/方法1200秒，首错停/正常回收，不改Unity结果或原件。


Creator TS native01 own71766于19:28:21.200824Z→19:28:41.202280Z正常TERM exit-15/reaped，editor pass/0诊断，候选804703d0010a88fc25608e2fa519b3d94e7785e1a391cef3ba7c2a544685cd7c。真实注册NumberLabel、MainUi129节点，Scene与独立Prefab5原脚本接线/实际classId/字串字体/完整几何、数字边界/实例隔离、保存重载未初始化态通过。首次实际自动UUID86325443-58b5-4b92-b0e4-bc27ec362d46、classId86325RDWLVLkrDkvCfsNi1G；原TS meta ver4.0.24已读。未冒称这个自动ID跨fresh项目恒定；后续code-emit新增namespace+源RF稳定meta，新的固定meta模式需格式阶段再验。JS importer metadata仍待实证，不捏造模板。

成组状态见docs/CODE-SUBSET.md。具名C#/TS原生代表已从facts/candidate推进到5绑定数值子集；公开convert集成、第二来源模块、typed none/grea格式化及全Research逐case仍未闭合，继续开发、不推送v0.2。


Typed格式化首个实现进入公开format-project：当前仅未导入Creator候选，preview→冻结plan→新输出apply；Unity与native已导入移动adapter仍明确pending。94个typed目标路径变化/184物理文件移动，SourceName/逻辑key/节点/组件/资产UUID/meta/原数值资源不全局替换，BMFont只重发显式page引用。全部owned文件、owner、算法、case/Unicode冲突与stale plan强检，Library/已导入拒绝。3语义反例通过，含文字/逻辑key恰含旧路径也不改、篡改owned/stale/人工所有权/已导入保护。

真实MainUi seeded-none candidate05 manifest71a110e66437afc0c69b844be0b5d11ba70b3a8ae04afb83fee74fcc8cd7f896，typed grea01 manifestdcfc2a92581c5fa2298a33b98e79ff6e53186e65dce704979c4ec2ffaee300e2；均未原生验。固定namespace/RF脚本meta已加入，两模式同seed。只有已分配resource/script UUID纳入保持门，未物化Prefab/节点native IDs仍pending，不能承诺fresh导入会自行分配相同ID。

下一先none native02、通过并退出后才grea native01，各实际锚点内部+28/外层+30/方法1200秒，ps无资源冲突、自有新副本、首错停；本轮检查新固定脚本meta/typed路径/字体页/5个注册组件及资源引用/完整几何保存重载，不重跑完整full14，不改原件。


固定meta none native02 own72833于19:42:33.598898Z→19:42:51.032834Z正常TERM/reaped，editor pass/0诊断，5类绑定/数值及129节点/字体页/引用/几何通过。typed grea01静态verify零诊断；离线逐项核91资产，nodes/components完全一致、resource UUID/meta原字节/非FNT资源字节保持。现在资源已释放，顺序grea native01新段同+28/+30/1200合同，验证同固定脚本UUID、typed目录/原字体页与资源绑定；未物化Prefab/局部节点ID不声称跨fresh相同。


Typed grea native01 own73175于19:43:25.973864Z→19:43:43.423979Z正常TERM/reaped，Creator3.8.8 editor pass/0诊断。对照none/grea：91资源UUID及75SpriteFrame身份、脚本UUIDd70c6943-490a-5b7b-bf8a-ca7b490ad126/classIdd70c6lDSQpbe7+KyntJCtEm、5代码组件/数字边界/原字体页/129节点几何/Scene与独立Prefab保存重载保持，比较7门全true。初始未物化Prefab的fresh UUID不同（none09ecace9-6934-4d09-bc3d-956794e27e9d/grea1f486368-acee-4b13-a702-7a636cbd5310），明确不计已保持；已有native迁移仍pending。4格式化语义反例含数值JSON原字节，相关23定向检查通过；Creator verify摘要原先0资产改为实际candidate plan91/75，非native数量推断。详见FORMATTING.md。继续Unity typed格式器/公开编排、native对象身份迁移及其余源用例，不结束v0.2。


总监event monkey-v02-format-identity-scope-20261024-01已明确审阅V0.2-PLAN首期范围：已存在native ID须保持；未物化Prefab首次生成ID与来源映射如实记录，fresh自动UUID不同不等于破坏旧身份。已导入/人工修改工程首期拒绝即可，完整native move不升级为本版前置。不重复已过探针；按本机支持接口尽量控制Prefab初始身份，无可核接口时记录实际ID/source映射而不虚构。优先Unity格式器、公开convert默认none/显式grea、生成接线、全Research真实导出。继续开发不等ACK；先前native-move pending为未支持范围，不是阻断本版的必做框架。


Unity typed格式器首个生成工程profile已实现：113路径变化/183物理文件移动，Editor host保持原字节、通过Analysis/output-paths.json明确plan/Scene/Prefab/Material/Animation/Editor输出，数据/代码文本不全局替换。原meta GUID保持；20个待首次生成位置（字体SO/Prefab/Scene等）标首次分配，不假装旧ID。非已导入候选、ownership/stale/native ID字符串保护有反例。通用UnityImporter现直接绑定生成C#脚本到TMP，要求精确脚本GUID/普通数值方法签名并读回数字边界/独立实例/重载态及文件ID。原Lifecycle候选方法保留pending不编进Label组件，避免被引擎自动调用。新C#host/helper独立compile通过，相关32检查通过。

真实MainUi129节点/5 C#绑定/80可转换组件，none01 manifest8b9a1a40dfdcadc45f31f2e7d4291aeb77b9a321cc93d45843cb16a7d7bfea21；grea01 manifestd8ea7bb144c24c847c12b46d18c8bbf6acbf316382baa38a0c12f1ad8528a248，两者尚未native。先none新段输出number-label-unity-format-native-none-01，实际锚点启动时+28/+30/方法1200秒，ps无主Editor冲突；仅自有copy/child，首新增严格失败停止，已知source行为partial不晋级玩法；前端独立格式器不含原生已导入移动，不作为本版前置。


Unity格式none native01 own74623于20:17:39.052866Z→20:17:58.020921Z exit0/reaped，方法2.039秒，严格verify0诊断/editor partial（已知源未知组件，不作为玩法完成）。通用生产导入器已实际生成5 C#绑定/数字边界，Scene和独立Prefab都读回5绑定/十进制身份/未初始化态；129节点及原字体/引用/保存重开门保持。资源已释放，顺序启动grea01独立新段，实际锚点内部+28/外层+30/1200秒，不重跑none、不改冻结候选，首新增严格失败停。


公开convert --format none|grea已接入，默认none；structured不再调用旧standardize，任意字符串/JSON/代码全局替换写入器已移除，只留旧manifest物理路径只读前缀lookup。grea在完整未格式化导出后两端全部prepared才晋升canonical；未格式化项目保留Unformatted，格式失败completed=false并阻止native。resume格式化工程首期拒绝、未知/直接Unity恢复profile的grea明确拒绝，不静默忽略。真实合成CLI none/grea各执行一次，none not_requested/grea applied，双端原件保留；17相关语义检查通过，含第二端格式失败两原candidate不晋升/native not_run。

公开单条convert --target both --format grea --native现用同一合成输入新outputs/format-cli-native-package-01→独立native目录执行，源/生成/格式/Engine分层。orchestration在实际启动每段前自动写不可顺延+28/+30锚点、方法1200秒，ps资源检查，自有child顺序Unity→Creator，第一新增严格失败停，当前未宣称端到端完成；不会借合成验证当游戏恢复通过。


单命令synthetic native01实际stopped：Unity own76092 exit0/reaped、strict0/editor partial；Creator own76364正常TERM/reaped，Scene/Prefab1节点几何/引用保存重载通过，但strict1 GENERATED_FILE_CHANGED。根因是package原始图assets/art/images/Original/...的合法Importer meta扩写未被新分目录nativeRoots收进回执；没有重跑失败副本。修正Creator回执覆盖自有assets根，并在导出manifest封存全部预先分配的资源/脚本GUID/UUID、原生verify逐项强核ID不变，既不跳过未记录meta也不放宽资产内容hash。新的无native ID首次分配继续单列来源映射。修正有定向检查后将新完整输出公开单条命令重跑，旧失败保持。


单命令synthetic native02完成：orchestration completed_native_stages，Unity76820 exit0/reaped/strict0/editor partial、Creator77095正常TERM/reaped/strict0/editor pass。首轮缺meta回执失败不改；新修捕获全部自有assets并封存/复验所有此前已分配资源/脚本GUID/UUID，Importer扩写允许、ID重换即使重记native hash仍拒绝。相关30检查+身份变更反例通过。真实Unity129节点 none/grea比较6门全true，91既有meta GUID保持、5代码绑定/数值边界/Scene与独立Prefab保存重载通过；首次Prefab GUID 3e4eb429eb2f3409e99e030c7ab2721a/92ba4d626843745b18205e873c7b5e04按来源映射记录，不当旧ID。当前生成式Unity/Creator格式与公开fresh编排已实证，直接Unity provider格式、自动代码发现/接线、Research扩展仍未闭合，继续开发。

U独立离线metadata-only新线索：启动40条Mono类型表对应27唯一script_id+old_type_hash身份，冻结600包含744嵌入Mono类型，其中18类可精确匹配。只做表/类型树匹配，未解析额外对象正文/解码纹理/执行源代码，不视为106MB已恢复。下一按版本/平台/精确哈希借取类型树并严格read校验，不放松字段/长度；原CODEPHPY方法仍未知。

事件monkey-v02-unity-schema-borrow-20261024-01：公开inspect-unity新增显式--schema-manifest，固定池≤2000文件/1GiB、逐包SHA；版本/平台/script_id/old_type_hash全相同才借TypeTree，布局旗标全哈希，歧义即拒绝。严格check_read=True真实70MB成功，启动总1567/1603、36未解析；原始SHA不变，worker77699 exit0/reaped，补充schema/provenance与embedded分列。13定向检查通过；此包仅正文解析，导出器/代码生成尚未消费借取结构，旧startup02/schema0不追认。下一继续自动源码接线与Research来源适配，不因受保护方法/未匹配36结构停全部开发。

事件monkey-v02-package-code-native-20261024-01：包级convert --numeric-code-contract已自动唯一发现RF原名/身份/模块SHA→重核语义→C#/默认TS→全部对应组件投射→双端导出→none/grea→原生编排。当前显式一个Label类/数值字段/唯一setter/getter，非number调用不假推类型、未知方法保留；自定义序列化业务字段拒绝，投射失败不报baseline成功；原始声明和源码留工程内部。JS包级绑定/投射包resume/reuse尚拒绝。格式化同步typed scriptPath到manifest/code-index，既有ID不改。26定向检查和证据留存后11关联检查通过。

公开合成7输入native01：Unity78528于20:57:53.848046Z→20:58:04.054183Z exit0/reaped、strict0/editor partial；Creator78894于20:58:04.082896Z→20:58:20.932724Z正常TERM/reaped、strict0/editor pass。1实际生成类/原组件绑定、数值边界/文本保持/Scene+独立Prefab保存重开通过；真实NumberLabel5组件旧证据分列。当前outputs/number-label-full-package-01正在新鲜全量原输入离线单命令运行，不复用旧89overflow有误IR，不改肥鹅工程。另U借取schema已接入字段模型试跑得2类11字段/12实例，尚在源基类/外部表规则收口及消费导出中，不能提前报原生恢复。

事件monkey-v02-unity-schema-consumed-20261024-01：公开convert新增--unity-schema-manifest，结构读取→精确MonoScript跨serialized-file外部表→具名C#→Provider输出真实接通。新startup-schema-convert03（资源/纹理5输入3554576B，另schema池600输入53730632B）实际生成GradientColor7字段/4实例、UIButtonScale4字段/8实例，对应脚本meta保持；2源码用Unity6 SDK编译通过。原有Unity包类型36实例单列不造同名类；22已读未知基类/字段与36未解析继续缺口。结构池600原件自包含留SourceRecovery并有metadata-only用途分母。Provider81142 exit0/reaped、原件不变；最终manifest802275864fe99b0a743b2c4de9aeca0b60104a25ea704b9b999427cb38e09a02。借取字段值尚未进Scene，明确pending诊断，原方法0、原生not_run；不改Unity场景YAML或空类补成功。下一优先C3/其他Research真实case，字段值按其依赖分支继续。

NumberLabel包级全量已收口：outputs/number-label-full-package-01新鲜17201输入884709704B，每端全账；24784节点/28514组件，5原RF组件在双端全部唯一可绑定；C#/TS与此前真实原生验证代码/脚本meta逐字节相同。Unity manifest7f654e6b928ff78d65ef7a95ca50a395ab64b58c22ad66117834bbf75777773f，Creator9deadb2235fe43ae2d5767f4665fe33afbf63260a193e2c6718c95724b69b821。none基线完整保留、grea双端已应用。当前严格可转换组件Unity11896/Creator12472，未知与overflow修正后的缺口未强行晋级；本次全量native not_run，复用前述5接线/数值/几何证据，不重开整游戏行为验收。四未知方法、1521缺引用、Spine播放/视觉/业务继续待补。

事件monkey-v02-cocos387-resource-native-20261024-01：新增严格Cocos3.8.7资源profile，package必须有本次输入settings.CocosEngine=3.8.7证明；@子资产身份不剥离（含原短hash基名）、新Texture2D数组pack、数字字符串redirect、UUID表索引pack版本及重复pack内容一致性已实现。相同源资产多pack仅选择已提供且完整解码等价的候选，冲突拒绝；单个未知纹理section不抹掉其他有效section。源图全隔离，不套2.4默认identity变换。首批01/02/03配置失败、04未闭合纹理链、05 gallery根读回失败全部冻结。

下方了原Research474缓存声明472存在、2zip缺件（excel/res.80d2b.zip、proto/res.ba762.zip）；加3个已解密原wxapkg共496输入38081754B。公开convert生成4804严格对象正文，986源Frame/80用到的ImageAsset与17本机载荷，3124代码模块仅源合同草稿、119源图及35图像依赖缺口保持。06复用签名/hash不变读取与像素，自有Unity86098于21:33:54.879791Z→21:34:19.498246Z exit0/reaped、strict0/editor partial；Creator86578于21:34:25.003724Z→21:35:09.391120Z正常TERM/reaped、strict0/editor pass。1972trim/full Sprite变体双端强尺寸/引用回读，Unity986 gallery还核GUID/rect并明确sourceGraphVerification=not_run。候选manifest60b77ba6d53d8f19268da44c981c97f1f0d964da2850900eb763a9b97663cabe/82033bb8ac1abddeed7a68b7fcebbf5a40edde81136d1ed9e6e7d6ddb776b5fb。仅资源子集原生通过，源图/采样/Spine/视觉/玩法未完成。gallery分支与非空图严格检查分开，C#离线编译及14关联检查通过；继续其余Research案例。


事件monkey-v02-cocos2411-native-20261024-01：Cocos2.4.11新增逐原件版本证明AST，不执行JS；10容器经Research manifest逐SHA，881展开输入8247168B、451源Frame/360纹理依赖/33载荷/91图，42Spine文件闭包仅资源。native02因1024字体atlas容量丢失167标签而364严格差异，Creator未启动；失败冻结。新导入器按完整请求选择有界1024/2048/4096 atlas，保留实际全部glyph/GUID/引用强门；C#本机SDK编译通过、21相关检查通过。新03 Unity90592于22:02:20.273789Z→22:02:43.754387Z exit0/reaped，Creator91386于22:02:45.141184Z→22:03:15.442065Z正常TERM/reaped，双端严格0，Unitypartial/Creatorpass；Unity1550节点/902Sprite变体/89独立Prefab/177标签/2字体保存重载。manifest c81aac4b36e3b06a17945a20326c721fb4f14bf4f1ac71ac3001cc54fcdcd348 /1465091db38fbe92ede45b2ad4e5bc845d415cbfc0b2fffb3003a3f3c3edd90d。170代码模块仍草稿、20缺引用/Spine播放/视觉/玩法未补。Research当前4/11实际候选、7未导出，不用识别代替通过。继续Unity2022 WebData与其余case。


事件monkey-v02-unity2022-webdata-20261024-01：公开convert新增精确UnityWebData1.0识别，固定provider直接读取，各serialized原版本独立保留。勇者乱斗2022.3.16f1实际3799对象3338parsed/461未知，首01因45个ETC1仅1byte导致decoder失败冻结；手机反恐2022.3.34f1c1实际9675对象9598parsed/77未知。新增ETC1最小block字节强分类，默认blocked；显式--unity-quarantine-invalid-textures才移除自有派生中的坏对象，其余对象逐rawSHA保存重读相同，完整原件保留，引用不假补。新勇者02隔离45/保留3754，Provider92149 exit0/reaped、4303文件9229669B，recovery59ad197e2ee5d692fdd161df931acf8b2e4f96cbf3ad35763c5de821fd07ad81；手机01隔离40/保留9635，Provider92301 exit0/reaped、18066文件35824738B，recoveryc3de2369343bd1f5a04751dea21c7933551f0e1df736f231e9c287b94071c031。0字段类，2029/8913原代码隔离，7/4缺引用，原方法/原生/玩法未验；10定向检查通过，Provider失败现进入公开诊断。Research6/11实际候选，其余5继续。

Unity typed值预算新增逐对象250000/全请求4000000强限；超大对象单列unparsed保留rawSHA，后续小对象继续，避免团结大型ComputeShader展开使整份已读结果无法载入。未放宽core上限或源schema；16相关反例检查通过，团结新inspection/导出另行记录。


事件monkey-v02-research-expanded-20261024-01：Research动态11例全部进入定位/读取/导出/核对矩阵，9例实际不同范围导出、2例blocked、完整游戏0，fullCompatibilityComplete=false。新增2.1.2原engine/settings AST证明及109项legacy-flat缓存：129展开输入26806035B，211Frame/38纹理依赖/81隔离图/956源码草稿，19298声明身份中18955未提供，完整声明分母与现有引用缺口0分列。02 Unity93877于22:20:45.832681Z→22:21:03.159315Z exit0/reaped、Creator94149于22:21:04.060650Z→22:21:26.613506Z正常TERM/reaped，双端strict0；422变体/211gallery强核，sourceGraphs0。03仅补声明分母，不重复已过原生段。详见COCOS-LEGACY.md。

新增显式non-Cocos family原图出口，Laya/LayaAir/Egret/Eraget/custom/other只允许Unity6，低层Creator plan也强拒绝。当前只源PNG/JPEG→派生gallery，原版本unknown、sourceSpriteFrames/graphs/methods全0；完整原件outside Assets、未知二进制不猜解析，图片/总像素预算和失败回执已实现。灵画师4包40文件19112966B/16原图，公开grea native03 Unity94895于22:24:49.703592Z→22:24:58.927183Z exit0/reaped、strict0；32变体/16gallery refs强核，manifest d83a54ee0c1fa1d985770366b678c8dd83cd2b29c84ce537e2273cc6c90028ce。原图集/界面/方法/远程清单adapter未实现，未冒充Egret全版本恢复。早期01接线错误冻结，Laya/custom仅自造反例，无额外真实样本。

武侠启动1468/1559正文，6纹理键3缓存匹配/3精确缺件，启动blocked保留；独立4272B配置Bundle实际导出SpriteSaveInfo一类/一个Sprite[]字段、meta保持且Unity6 SDK编译通过。Provider95567 exit0/reaped，9文件16555B、131Sprite引用待补，recovery cb80fa0e7aa18e58a0ded0e6118faa62053200983aca39f3bb74bffdf75e437e。原生not_run。团结原始t9保留、2888/3042正文，Provider实际3042不可读对象/0原生资源；新门exported_evidence_only→blocked、无候选晋升，旧误分类01冻结。新02 Provider93252 exit0/reaped；Lua/资源专用adapter仍缺。天命Research/Manager指向的archives目录当前不存在，明确源定位blocked，不扫描玩家档或恢复项目。

本组35定向检查通过；新增literal settings函数调用拒绝、evidence-only不得晋升两反例另9项通过。样本/输出均私有，工具源码与证据说明留本仓；继续资源闭包、Unity原生消费/格式与未支持adapter，不宣称v0.2已完成，不推送发布。


事件monkey-v02-js-and-dependency-closure-20261024-01：JS次选先实际native01失败/TERM reaped，观察javascript importer4.0.24与ESM文件被默认CommonJS解析。按官方模块规范新增assets/package.json局部ESM边界和固定脚本meta，新MainUi129节点/5绑定native02 own96527于22:41:40.702916Z→22:41:58.153501Z正常TERM/reaped、strict0/editorpass；Scene+独立Prefab5绑定/数字/未初始化/文字/几何/UUID→实际classId六门只读审计全true。原4方法/动态SHRINK未恢复。公开JS选项与grea已接通，installer不把package.json当scriptPath，代码注册/回读强核压缩脚本UUID；public合成02 own97084于22:47:18.787472Z→22:47:35.091237Z正常TERM/reaped、strict0，manifest d200ccbdca2a9185fb209dc0b5df281666ec3716bbb319f9c747e06f53131bed。旧public01格式hash变量错误冻结/native未启动；修正未放宽保护。

新增公开--unity-dependency-manifest：完整冻结元数据池内按原external表/精确serialized-file身份递归闭包，环/返回主包/字节相同别名处理，冲突拒绝、缺件列明。武侠212查找包33404614B/49314对象全部索引，自动找到1依赖+3精确ASTC缓存，实际资源5输入2271482B，Provider97219 exit0/reaped、277文件12586350B/135原生资源/0unreadable，131缺引用占位降0；recovery bd757d050d3afb12567d850d674f3fb125dd74215244e10470984a9beef3b81a。查找分母/实际导出分开，全部冻结池原件及索引闭包保留SourceRecovery，SourceC#与已编译代码相同但fresh meta不同、不混旧GUID。原方法0/native尚未跑。23相关检查通过，含脚本UUID反例、精确依赖名/歧义/环/失败索引，不重跑完整full14。

总监event monkey-v02-research-gap-coordination-20261024-01已确认天命源目录缺失并向用户询问新路径；本聊天不再重复扫旧址、不等待该项而停止其他能力。9输出不是v0.2完成，图片gallery不冒充源UI/代码；继续有成果的源atlas/图适配、公开Unity native/格式及代码接续。武侠启动3精确缺纹理的逻辑路径/预期属性/原DATA_CDN静态声明已形成.private/unity-wuxia-current-01/source-assist-request.json，下一成组报告交总监协助；不自行猜别的hash或复制认证。

事件monkey-v02-public-unity-native-wuxia-20261024-01：Unity来源公开convert现支持显式--native与受限--format grea（须native），profile为单原叶Prefab/单字段类/嵌入Sprite[]/精确水合非变体图集。原PPtr按container+原external表+decimal pathID解析，唯一源名映射后核目标GUID/localID/顺序/图集rect/纹理GUID，固定纵向像素转换对源RGBA SHA。oneclass来源C#之外代码/未知包/场景/借取实例值未闭合等启动前拒绝；null数组/空数组/缺slot区分。脚本/程序集名保持，全部原meta GUID封存；资源动态寻址固定，不手改YAML。21定向检查通过，C#helper编译通过。

首公开native01 own98320于23:26:03.217619Z→23:26:09.804296Z exit1/reaped：131非空引用/源descriptor已读，保存副本名Roundtrip导致重开根名变化，旧失败冻结。改独立目录内沿用原Prefab文件名，不放宽名称/几何校验；新02 own98633于23:27:07.437151Z→23:27:14.025354Z exit0/reaped，20项checks全true，131引用/一个字段/3张纹理/136既有meta GUID/保存重开通过。grea实际0移动、134项因Resources或bundle名固定；正向真实资源搬移尚未验证，不能泛称通用native格式迁移。none manifest f967d290e262112ee5b41c4abd304d7b292442670367b969aecd72b593c2aa6c；受限grea 92c54ce70a6b0f01e420ea38bcd041c0922a9a411f68ccf0798a091fa97c1819。canonical不带helper/probe/enginecache，原none保留Unformatted；未来晋升START-HERE已补实际资源验证层级，02冻结的旧模板native未跑文字以外部readback为准，不回写旧证据。

总监event monkey-wuxia-exact-textures-found-20261024-01给出的3精确HTTP200/ASTC原件已按回执SHA/块长/尺寸再核并复制私有池，新显式117纹理清单sha2efdbaedd87d35976312307cf2ef19b252add1e0afcb98d03a4696dbd40d7f13；无重复GET、不改WeChat/Research。启动6键全部水合。旧startup02普通沙箱loopback启动60秒超时，Provider98919正常TERM/reaped；新允许loopback环境startup03 Provider99060 exit0/reaped、0.648秒，7实际输入6442729B、2408文件12417811B/44原生资源/0unreadable/0缺引用占位。1142原代码隔离/0字段类/91对象缺结构，native整包/方法/视觉/玩法未验；manifest e06d27982539d72b1e2f7ebd4f14fc72b6771ab343055c9ce3e739819623cd4a。

下一接现有acquisition到Unity输入闭包，精确声明URL可由统一CLI消费，不依赖总监手取；不扩未知URL扫描。继续源atlas/图与代码接续，不重跑已过代表小样、不为gallery扩大完整兼容口径。Research11attempted/9不同范围输出/2blocked/完整游戏0不变，v0.2仍未完成、不推送发布。

事件monkey-v02-unity-acquisition-cli-20261024-01：Unity来源复用既有acquisition到公开convert，支持显式remote-manifest/remote-cache-root/acquisition-out/offline，不再只接受手工合并纹理表。ASTC精确逻辑路径入纹理池，真实Unity容器入显式依赖或冻结精确查找池；未知文件只在SourceRecovery/Acquired保留并diagnostic，不导入Assets。缓存同逻辑键异字节拒绝，实际source尺寸/mip仍由既有水合器强核；不猜URL/hash/版本，不执行下载代码。全可用原件+脱敏回执在native封存前附加，暂存完成再晋升，源变化保留原owned基线。

公开真实offline04使用114原缓存表+3显式精确URL/SHA，localVerified3/110848B、0GET/0missing，6键齐；Provider99626 exit0/reaped、0.655秒，44原生资源/2408文件/0占位，candidate owned全核。recovery bd3caf0ed9e2f8e2487b39282fd6fcf006bc3b4cfc434f362045c560ac38caa2，acquisition receipt15820ec524708207ca6186bb3cce52475e2297750a5d24fbba2ac37d4151ff80。34定向检查通过；未重跑已过Editor。继续源atlas/图适配与代码接续，v0.2未完成，不推送发布。

事件monkey-v02-cocos387-source-graphs-20261024-01：3.8.7新增真实静态源图adapter，读取_lpos/_lrot/_lscale、UITransform、UIOpacity及renderer颜色，省略默认值依据官方v3.8.7固定9文件SHA（docs/validation/cocos387-engine-baseline.json），不套2.4 identity。吸收几何组件时保留sourceGeometryComponents；错tag/owner/重复UI组件/未归一化Quaternion/disabled UITransform阻断，PrefabInstance/非空nested/override整图隔离。未知组件原名/数据留handoff且supported=false，不能靠同名2.4缺省意外原生化。共享目标规划显式尊重unsupported。Scene/Prefab新增opacity/已发renderer颜色强核；Creator保留并强核layer，Unity原layer作为provenance及camera/layer待办。

实际119原图→83静态图/810节点/81 Prefab/908组件，36嵌套图隔离；35源Image边、sampler、Spine和方法/视觉/交互仍缺，986Frame/1972变体不变。118节点非白色、2非255opacity；Unity363/Creator380发出renderer节点做颜色强核，95Label/1源字体。当前源策略与冻结08候选810节点/908组件逐项完全一致，审计保留outputs/cocos38-xiafangle-graphs-08-current-policy-audit。

07 Unity own1431于23:50:14.643489Z→23:50:42.606725Z exit0/reaped，方法6.82秒、strict0/editorpartial，源图/资源/保存重开通过。07 Creator导出source-map漏unsupported.nativeType，structured失败而文件记账fallback完成，入口缺失因此Creator未启动；该失败冻结。补nativeType=None、两个真实反例，并在全组Editor启动前预检所有请求目标的owned入口，避免第一引擎先跑、第二才发现缺发出。此前未先检查structured.status是本轮一次可避免调度错误，后续已补门。

08仅重建Creator；own2304于23:53:25.726798Z→23:54:10.873039Z正常TERM/reaped，方法21.22秒、strict0/editorpass，810节点/81Prefab/95Label源几何/引用/颜色/透明度/层/保存重开通过。Python后补layer强核editor级只读复验pass/0诊断，无新Editor；一次误用static层级看到importer meta变化的冲突结果保留，改用正确editor层级核对，没有降低meta校验或改旧证据。Unity07 manifest ba63a4652259a04bfcb368e3e694f8c1a898df0c3053dbf360099ada41bb6153；Creator08 7983feacd55006b06aa94f7aca2aa2cbc5dca635e187346e1963a6a00ae7a10c。

34定向检查在本项目.venv全过（含可选ASTC），host C#与两个JS语法检查过；篡改Unityplan的早期stage hash错误现保留既有PLAN_CHANGED代码，不放宽内容保护。未重跑已过Unity、未全库测试/发布。Research仍11/9不同范围输出/2blocked/完整游戏0，更新当前case ledger而保留旧gallery/失败记录。继续代码接续与专用来源缺口，v0.2尚未完成。

事件monkey-v02-new-source-number-code-20261024-01：新增static-number-methods-v1公开convert合同，从真实下方了ParabolaUtils951B/8方法中静态恢复3个Number算术方法；保留原名/范围/SHA/原文，5向量方法继续待补。literal模块setup/import setter/RF/export/constructor scope/createClass descriptor逐项绑定；精确helper SHA及其自由e从原main/game.js追到../../@babel/runtime/helpers/typeof和唯一声明callback SHA，不执行原源/constructor/helper。首次context worker保留逐节点parent数组导致256MiB OOM，改scope-only栈/有界索引后同预算真实验证通过，没有抬高限制。后补Math遮蔽、descriptor歧义、别名update/解构重赋值、require遮蔽和动态scope拒绝反例。

双目标生成静态C#/TS（可选JS），不伪造原组件接线；Number/double显式参数子域包含-0/NaN/Infinity，排除非number/constructor/未知向量/可变intrinsics。C#用NoInlining独立binary64运算保持源序，特别保留unclamped lerp和先乘后除溢出。grea Unity归Domain/Math，Creator归domain/math；09旧Creator目录state冻结，10修正。工程START-HERE连到可调用签名/源证据/5待补方法/实际scriptPath指针及一个聚合任务，不靠大量同构空桩。

公开新10：496输入38081754B、83图/810节点/81Prefab/986Frame不变，双端格式成功；Unity manifest d7a6c143a5db8d3e73a847bec6c1d7dbe307942d47fa66bd2c207ea8acdfc56b，Creator 0ac57d3e28988db54508811333c531ad8095b0db9bbcf8b6080826690e8a20d1。当前源码重解析model与冻结完全相等，helper context也相等；30974个owned文件全核。C#SHA e95db24463f04ebd4b6d7cdced345c8dd99f6270699088ca01b586dfa8e43d10，TS SHA9d481af7ddcdf49ae7b08958f8cba9e45690b5f9da483b91bd78eec9ad415955。Unity6 SDK编译及TS5.8.2 strict过，C#/.NET8.0.21、TS编译产物/Node、JS次选/Node各13实际边界调用过（负零位、NaN/Inf、外插、mul-add舍入与大数运算序）。仅运行受控生成代码。26定向检查全过，包括TS/JS包级both+grea及未知helper/模型篡改反例。

审计outputs/parabola-math-audit-10的audit.json/runtime-receipt.json封存输入/代码/编译产物/检查hash；没有新Editor/Player，资源Editor沿此前07/08，不据此晋级视觉/业务。Research仍11attempted/9不同范围导出/2blocked/完整游戏0。继续专用来源atlas/图等有据缺口与v0.2出口整理，不推送/Release、不以此检查点结束版本。

事件monkey-v02-egret-binary-atlas-20261024-01：新增可复用egret-custom-resource-plist-v1，静态核9类已审阅callback及BinJson helper词法绑定，解析resource prefixes/types/URLs/groups、Plist trim/body边界、VERSION2 Skin typed JSON。源代码/原配置不执行，不把Skin解码等同原生UI。初始全9.9MiB AST触及256MiB后改整体tokenize+≤64KiB候选/≤2MiB lexical AST，原预算不抬高；截断/多余尾/变长整数/索引/大小/路径冲突明确拒绝。config.bin与Skin格式不同，保持隔离，不用错误全包同格式推断。

旧4包40文件19112966B读出3清单48252声明、53图集1920切片、3026 Skin；最初28声明可得/53纹理页缺失。基于原默认inChina=true、testMode=false及生产CDN literal，只取清单精确hash文件名。先单页1GET取得Emoji1537x509/290374B/SHA61142f5aabd84a130c11505855b6fc0e2efee703a57baa5859d638279fe8d104；完整53页52GET+1缓存共7975531B，全部可用，未猜不同hash/地区。冻结SHA后公开convert复用统一remote/cache/offline/acquisition→独立源root→同reader/像素→grea/native，原件只读。未扩至其余48171声明载荷，缺数保留。

实际公开09：41输入19403340B、132真实源切片+17整图预览（两类分母不混）、298Sprite变体，manifest229847969e423e63de80ace23bba5121b437cbdeeae0c74ccae3900abaea7607。自登记≤30min段，ps确认无主Editor后own Unity8815于01:07:12.912716Z→01:07:24.952861Z exit0/reaped，方法1.18秒，strict0/editorpartial；GUID/rect/尺寸/引用与保存重开通过。源节点0、sourceGraphVerification=not_run，视觉/玩法未跑。原始一页的132 trim/full及264目标PNG逐RGBA核过。

完整53页offline10：93输入27088497B、1920源切片、69独立整图预览，53页全闭合、81声明已提供/48171缺件；sourceSkins仍3026、nativeSourceGraphs0。1920源切片和3840目标trim/full变体逐像素完全一致（outputs/egret-linghuashi-atlas-pixel-audit-10），manifest47277e354e8674ad02570cb152369e8c78adc835386ad1d9d1112a4ba64e1a62。全10 Editor尚not_run，不把09代表结果写成全量通过。27资源/缓存/编排检查及35关联格式检查通过，聚合AI任务/START-HERE/来源表自包含，所有JS/BIN/解码Skin在编译根外。

当前灵画师引擎已按最新human要求独立确认Egret5.2.32，而非先前初步Laya：本机wxcbc1fc07fb13d667/166主包2857006B，实际64字符SHA256为2e200f176380470eff845c868d1b96391b93261e375a23997697c6eb29886de1，与Research完全一致；入口bootstrap9a27...8193直接egret.runEgret，原runtime版本literal5.2.32及RenderNode实现。公共精确span/hash见egret5232-source-baseline.json。总监来源材料的主包SHA有误拼接，以上为本聊天实际重算值；不照抄长于64字符的字段。未据此声称Laya已支持，广义Laya仍等待真实样本。

最新取舍已同步AGENTS/方案/支持矩阵与case：不可逆源引擎/方法保留limitations，不强求全游戏；嵌套Prefab/override/动态布局仍必须解决。当前转入天命/机智微信缓存补源：已只读定位目标applet packages/local，机智146/147可见、灵画师165/166可见，未读usrmmkv玩家档。天命需定位AppID；applet元数据库不是明文SQLite，仅探header/只读schema失败，未取凭据或绕解。下一先冻结机智147当前包/资源索引并有据补取，同时以允许标题/AppID元数据定位天命，之后解决下方了36嵌套图及真实动态布局，不等旧归档答复、不新增团队/安装/发布。

事件monkey-output-cleanup-20261024-01：本聊天用户直接要求适当清理monkey输出。清理前outputs约560GiB，其中历史acceptance约294GiB；已删除full-foodstreet01–13及structured-foodstreet01–08的重复输入、派生资源/SourceRecovery和旧工程资产载荷，保留原manifest、Analysis、Docs、日志与独立验收报告，并为23个旧轮次增加CLEANUP-NOTICE（不再是完整可打开候选）。full13失败原生副本保留失败日志/回读，载荷清理；所有可识别生成工程仅另清可重建Unity Library/Temp/obj及Creator library/temp。

实际删除246个目录；macOS大小写路径别名36项按冻结清单去重，首遍遇Assets/assets同目录已删后恢复原计划，没有扩大范围。保留full14及其native、NumberLabel full package、下方了graphs07/08与Parabola10、Egret最新候选、所有远端acquisition和.private来源/开发资料；79份保留manifest及在途源码SHA复核相同。物理可用空间增加428851200000B（399.40GiB），卷可用从约291GiB至690GiB。删除计划、逐目录日志、原候选hash和完成回执在.private/cleanup-20261024-output-01/{plan.json,deleted.jsonl,receipt.json}。仅历史已执行的Editor证据有效，重新打开保留候选会重建缓存；未启动引擎重跑、不改变验收层级、不提交推送。本次维护不代表v0.2完成；嵌套Prefab/override、动态布局与当前补源集成仍按既有授权继续。

清理后du实际分配统计：outputs 166190656KiB，即158.49GiB（清理前约560GiB）；人读回执.private/cleanup-20261024-output-01/README.md。

事件monkey-v02-jizhi147-full-resource-20261024-01：清理后按原授权恢复开发，机智wxc9ca302d7fa972f2/147当前5原包7740297B、解密展开19文件7739181B及原109项缓存冻结。按原Cocos2.1.2 settings/packedAssets/md5AssetsMap及wxDownloader微信生产CDN literal补7676 import+5415 native，全部13091精确文件1201902615B逐SHA核验；metadata和两张图片的URLError各有界重试成功，不扫URL、不读玩家档、不混版本。原TextureUnpacker的5159段格式确认4699PNG/460JPG；MP3/粒子/字体用原_native和MD5Pipe规则，不猜扩展或font目录URL。

新实现支持JSON/TextureUnpacker两个pack、原res/import目录、等字节native aliases、sampler/alpha来源保留；不支持的图/Spine等正文保留在原packed载荷和成员/原文及解码SHA，避免生成约900MB单JSON（04失败冻结）。BitmapFont资源profile被postpass错误消费导致05规范化失败，已加严格source-only跳过及Spine/source映射实质反例，旧失败不改。input-set允许显式严格整数limits.maxInputBytes（默认1GiB、硬上限8GiB），单根1GiB/单文件128MiB/计数/每轮远端1GiB不变，派生输入集保留预算。旧缓存有3个非settings版本项，结构索引拒绝后工程也过滤至SourceRecovery，避免旧PNG进入Assets或与正常资源按SHA去重。

公开06全源步骤成功；07在相同输入/hash及完全相同inspect/normalize算法下复用受验来源/像素，不重解码。07实际13220输入1228708650B、19298声明身份缺0、7343源Frame/每端14686变体、249音频/1字体、956模块草稿/5未知wrapper，6546源图/Spine/动画等继续隔离。Unity manifest93502f5cfd2e0a1ba9a65608221e77621b8cf69e8b11698e81843388d4c3f0d3，Creator872235edc8036c39f824efbceadd47eeabf926f1993c8f1d1d6d121dd3978304。双端static pass/0诊断，35关联检查通过。7343全几何/纹理身份核过、48代表源Frame/96trim-full像素覆盖13组合RGBA相等，双端29372 PNG载荷与源规范化语义相符；Creator正确使用完整图+trim元数据。审计outputs/cocos212-jizhi147-resource-audit-07/audit.json；全07 Editor/视觉/玩法not_run，旧211代表原生证据不追认当前全量。

天命已定位当前wxbdf25cb34ce9bf6e/12并冻结3包13675974B、7展开文件13675688B及336缓存71617967B，原索引无缺项；原game_name天命行者经Acorn8.15 tokenize绑定精确字节，settings.CocosEngine=3.4.1，资源URL版本1.2.67一致。仅1个缺bundle条目按原remoteBundles与完整URL段生成有证派生索引，不改原件；原始缺archives不再是当前阻塞。docs/validation/tianming-source-intake.json记录身份/哈希，3.4.1专用reader/公开导出仍pending，不套3.8.7。下一主优先仍是下方了嵌套Prefab/override及动态布局，已有development-only解析储备，尚未计原生能力；v0.2不结项、不推送发布。

## 2026-10-24 Creator 原生嵌套与实例覆盖

event monkey-v02-native-prefab-creator-20261024-01：Creator3.8.8后端已接公共IR/plan的精确模板DAG，按依赖顺序保存真实Prefab后原生instantiate，差异写目标SDK的PrefabInstance/propertyOverrides，Editor serializer/checkAndStripNode保存。SceneAsset读回显式初始化自有inactive Scene使原生占位展开；不激活Director当前场景或执行原脚本。源实例/模板节点按native fileID+asset UUID读回；共享模板磁盘SHA保持不变。

合成02：13节点/3Prefab/5关系，双实例不同覆盖/三层嵌套/Scene与Prefab保存重开通过，own49700、03:29:51Z–03:30:10Z、按正常TERM退出/reaped，严格0诊断；真实01：104节点/4Prefab/5关系/1972帧，own49926、03:30:57Z–03:31:39Z，TERM/reaped，严格0诊断/editor pass。失败01的缺少Scene._load初始化记录保留，离线修复后使用新候选02；不覆盖旧证据。Creator根继承专用asset合同尚待实现，计划阶段显式拒绝（Unity原生Variant已通过），真实选定样本没有该类型。21项相关测试通过；动态布局及天命接续，不计视觉或玩法完成。
