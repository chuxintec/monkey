# monkey 项目计划与执行进度

## 2026-10-23 用户一键 CLI 收敛

用户直接要求命令行一键转换，当前统一入口为 `bin/monkey convert --source SOURCE --target unity|cocos --out NEW_OUTPUT`，复用六个既有阶段；支持私有可复用 recipe、候选身份校验和原生回读续验。双目标合成流程、拒绝覆盖/原件保护、失败收据、源版本证据和续验漂移检查定向通过。

真实肥鹅冻结奖励切片已通过一条 recipe 命令生成 `outputs/cli-reward-01/project`，25资产、48节点、82组件记录、156诊断，静态pass，原生/视觉/业务not_run；默认needs_action。它来自当前动画支持模板，和冻结creator-reward-04的155诊断不混作同一验收。原生自动启动/导入尚未实现；失败中间阶段自动续跑未实现，已完成候选可续验。故尚未实现完整“一键原生转换”，下一个实现包应补编辑器preflight与受支持原生导入编排，并在获独立窗口后复验。

第二轮Creator实导实际发现 package.version 被3.8.8规范化、Mask默认inverted赋值引发空renderer错误，已作最小产品修复且保留原始失败证据；23/23图像frame meta已更新trimType，原生Scene/回读仍不存在，原字体加载出现fallback警告。01:30:06 UTC后已向总监提前释放前台，不继续操作或重启引擎。修复不等于原生通过。详见[CLI及第二轮记录](validation/2026-10-23-cli.md)。

2026-10-22，批准本地开发。**当前：M01离线子集已实现；M02/M03已补字体和首屏必要原生UI映射，真实Editor/画面对照未验，v0.1尚未完成。** 主开发者更新本文件的当前状态及下一步，历史成组结果简记引用，不另建平行台账。

## 产品目标

输入已授权且实际取得的Cocos源工程/发布资源，输出原生可维护Unity或Cocos工程候选，让AI直接接续未知组件、业务接线和一致性修正。工具承担重复且可确定的解析/映射/生成，AI承担需要语义判断的部分。工具不承诺恢复服务器、不把可打开工程等同可玩游戏。

面向两类输入：
1. 完整Cocos工程：版本、编辑器资源、meta、脚本引用较完整；优先通过原生导入路径。
2. 发布资源：bundle/config、UUID/pack/import/native、压缩序列化、纹理/音频/字体/Spine、JS模块等；按明确版本与格式reader处理，缺少资源如实记录。

首期事实基线：肥鹅为Cocos Creator 2.4.15相关已冻结资源；现有Unity6000.6.2f1与Cocos3.8.8为可参考目标。发行许可是独立边界，monkey不购买/激活、不强制目标Unity6；输出profile必须声明实际可用版本，未验证2022/团结不得冒称兼容。

## 范围与非目标

覆盖：资源清单、引用闭包、SpriteFrame与图集语义、基本2D/UI节点/组件、有限原生动画与骨骼资源接入、工程模板、可查看预览、缺口/来源映射及AI工作包。

不包含：任意版本万能反序列化、运行未知原JS、自动全量业务转译、完整服务端恢复、原版账号/接口探测、破解新增加密格式、自动付费生图、自动发布；不新写Cocos运行时兼容层。现有安全解包工具可用于准备输入，但不把解密/抓包作为monkey首版主线。

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
