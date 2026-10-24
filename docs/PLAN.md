# monkey 项目计划与执行进度

完工/阻塞/交付与续推按[DIRECTOR-CONTINUATION](/Users/wangmeng/Documents/Manager/standards/DIRECTOR-CONTINUATION.md)执行；本聊天已原生核验人类授权`01a166b4-5c18-78f3-8cc2-c0d07dd46a20`，总监路由`01a14c8c-6402-7d03-bab8-ec7ea8051abf`。更新本PLAN后以稳定事件ID报告，已批准就绪下一包连续推进，不因报告或普通ACK停下。

## 当前：NativeFlow原生替换及局部增量已完成（2026-10-25）

依据总监`monkey-native-layout-production-fix-20261025-01`，沿已核验通用脚本修复与全量初版人类授权，只修复冻结肥鹅dev3的布局转换/引用子集，不写游戏工程，不原地修改dev3、不重导全量或AssetRipper、不发布。单主开发，无新增Agent。规范为grea-native-port原生转换规范与Unity官方uGUI技能。

已实核48独立源Prefab/63个NativeFlow组件，另2汇总Prefab各63引用；63处均水平起排、无缩放参与/无固定行列。62处当前子尺寸一致，1处问卷异尺寸单行；另有2处卡季零尺寸模板，源码用途正在逐项核对。NativeChildLayoutGroup是共享的子Rect/scale/pivot变动通知基类，Flow移除后仍有其他Linear调用，既有Linear不在本次整体重写范围。

已通过公开CLI完成48项处置表、独立暖缓存候选`outputs/native-layout-fix-01/UnityProject`及原生替换计划（50 Prefab/189组件槽，3384节点身份/几何绑定）。58处原生内容网格、4处固定单元格网格、1处原生异尺寸单行；禁用项保持禁用，卡季零尺寸模板通过确切嵌套Prefab根尺寸核验，5处`_N$cellSize`读取缺口修正。原算法与许可证移至SourceRecovery/冻结历史；新运行时代码不再导出NativeFlow。小型原生Grid子类只处理Image优先级及空容器高度，无源布局递推。

28项定向测试（含导出回归）及候选实际C#离线编译通过；公开`native-layout-audit / native-layout-prepare / native-layout-patch`计划调用成功，真实Editor仍not_run。patch计划SHA `77c73cab78081ead4c88c80b5d51724f4dda2f28f2efecdcd32bc8a0682c64bd`，helper SHA `36318fef0f715e3fa69666382b2d89f244a9226e185ea89e9276d5e9de727eaf`。已获`monkey-native-layout-window-20261025-01`新窗UTC18:10–18:35，并于18:10:14启动自有Unity PID86605；许可证启动返回缺少`com.unity.editor.headless`权益，增量方法未进入、0目标Prefab被保存、无原生读回。首新失败后仅终止自有child，18:12:26已exit -15/reaped，冻结源104份保护文件哈希不变；同窗不重试。执行现场`outputs/native-layout-execution-01`保留，Editor保存/动态回读仍not_run；原生身份映射和最终可采用增量包待新的可用许可/独立窗口。冻结dev3/游戏工程不写、不全量重导或发布。最终原生组件fileID映射、48项资产增量及代表动态验证在原生完成后冻结供游戏主开发采用。

启动归因追加核对：本次Unity是默认use_default沙盒；同版本成功肥鹅调用`call_1409892a7ac94fde8cfc4ae4c03ed90f`明确require_escalated并含batchmode+nographics。失败日志另有2次readonly database、LSModifyNotification和hiservices-XPC错误，两个成功日志均无这些错误且实际解析权益。已证实启动权限/参数边界不同，不能认定用户许可不可用；沙盒影响是有依据推断，尚待新窗正常审批启动验证。下一次同一有界任务经require_escalated常规审批、使用-nographics和新候选；不改许可/协议/全环境，不同窗探测。只读比较回执`.private/native-layout-production-fix-01/startup-cause-review.json`。 新候选`outputs/native-layout-fix-02/UnityProject`已准备，patch/helper与已核身份完全相同；启动器仅补-nographics，第二独立窗口`monkey-native-layout-window-20261025-02`已于18:20:23以require_escalated及-nographics启动PID88949；许可实际解析成功，方法进入。前14源Prefab/18组件完成替换、保存重开及几何/身份核验；问卷探针错误假定直接子节点存在已恢复TMP Label，实际既有基线只含RectTransform，因First无匹配而停止。18:21:12进程exit1/reaped，同窗不重试；冻结源104保护哈希不变。失败层`outputs/native-layout-execution-02`保留。 已在独立COW `outputs/native-layout-fix-03/UnityProject`精确承接14份已验资产（按执行计划/读回/文件SHA与未变公共映射代码绑定），仅剩36资产/171槽需要替换；14份只复用证据，不重新保存，问卷新探针按真实子Rect测试且text-not_run。其余探针的组件存在性和宽度输入假设已成组核对；新helper离线C#编译、29定向/导出/CLI拒绝回归通过。公开patch规划调用已核续接输入；第三新窗`monkey-native-layout-window-20261025-03`中18:32:29启动PID90784，18:33:37 exit0/reaped。实际新增36资产并复用14已验结果，50资产/189组件映射、6代表探针全部完成，sourceRuntimeTypeAbsent及legacyReferencesAbsent均true，冻结源保护哈希不变。问卷按真实子Rect高度变化验证，原Label/text动态继续not_run且写入limitations。已通过公开finish完成全对象身份闭包及冻结：新候选manifest `824f9dd8bdc9efe850333d00696034ec898b18967ebec8690b1ca2eb5eb32c16`，73项全工程差异；原冻结92434份文件逐项哈希全部未变。3384个绑定节点几何/身份及其余全部序列化对象类型/脚本/owner/local ID保留，189项新组件映射（168 IntrinsicGrid、18 stock Grid、3 Horizontal）。局部交接包`outputs/native-layout-adoption-01/monkey-native-layout-delta.zip`为8824625字节/SHA `32badbf655308a236dd4deefa6a79c319c877cd7d73525591f98121ff8a26829`，53资产操作（50 Prefab+1运行时适配+2旧源/Meta删除指令），111载荷ZIP逐项哈希复核；adoption-manifest SHA `fb9201bb2ade10356a4a69bc4915195385ad4f919e6c8507674d8f5fd71e9d50`，附实际GUID/fileID与旧hash保护。未写游戏、未发布；准备向总监交接精确范围，Player/业务/视觉和原问卷text仍not_run。启动边界修正有效，问卷原Label未恢复是既有独立缺口；离线改探针为精确绑定的既有子Rect高度变化并明确text-not_run，不补假Label或扩大业务恢复。

## 历史：两份批量完整初版及dev3工具已本地交付（2026-10-25）

依据用户全量先行纠正`01a16e53-16d8-7351-b6e3-981caef2ceb5`及重启续推`01a16e87-16ec-7111-9d25-967b392eed98`：先批量导出已取得全集与具名代码证据，再由游戏Agent继续开发。分支`codex/full-project-handoff`，本地工具0.2.0.dev3；无远端发布。grea实际MCP已核2026.10.24rc1；两个游戏工程保持只读。

- 肥鹅：同一自包含`outputs/bulk-foodstreet-native-01/UnityProject`已冻结，manifest `b8dde1e12d87a0ff059f46a230bfbec039bb4afefa026e7d3dd35b3d31f5e387`，92434文件/3486088823字节。1694源Prefab/24480节点、2源Scene/300节点、16934 Sprite及7756 Sprite PPtr实际身份合同；main/room16_test保持原名，测试场景不称完整主线玩法，小游戏4节点排除。914具名模块、10607方法/10391字段声明，0方法实现。SHRINK严格配置与缩放几何复核后，冻结工程独立editor verify零诊断；原5fail、两次增量失败/partial、16630来源限制全部保留。入口`Docs/BULK-INITIAL-HANDOFF.md`。
- 向僵尸：`outputs/bulk-zombie-handoff-03/UnityProject`已冻结，recovery manifest `f2410ed90d038867dca6b6093e7927fe1c516c408dacf471a1da83242a623752`，163473文件/3252286957字节。887原始文件逐项原字节保留，7595已取得纹理（含13未引用原件）齐；7626纹理对象水合、426对象对应425确切404键隔离、不造像素。一次AssetRipper导出601输入，65362资源文件、65309唯一GUID、64476唯一内容hash，53新媒体GUID待Editor，0重复GUID。原路径精确映射57346/63302，5956未映射、975未解析、1992 provider占位引用显式保留。13有据字段类/57字段，20181元数据类型/20129具名声明初稿、138243方法签名，0方法实现；Editor/Player/业务not_run。入口同名初版文档。
- 工具：已有可恢复检查点`09b026c`；增量原生、源Scene/实际fileID、具名代码、固定CDN补取、601 typed复用、可续接纹理准备、独立限时provider、全量组装/冻结均经公开CLI实际执行。跨Bundle同名脚本仅在MonoScript原字节及有据字段完全一致时合并，保留全部源身份；不按名称猜合并。代码生成输入只取必需字段，完整745576030字节typed分片保留。

三次肥鹅增量和一次AssetRipper原生child均已退出回收，无新引擎运行；工具分发已从不可变源码`f7015311b0641ec4daea9fa36bb3ff86156d972f`构建，wheel453353字节/SHA `9b52c3419ba731def190b141ea040be1a36f2f219335fbb5256108eaae83f3c4`，sdist610970字节/SHA `3bcfb4f99ee7d15ce547b73cce4f90062eb9e15f638595c20af1c0b7933c3e95`。wheel/sdist的123产品文件字节一致；隔离离开checkout安装后6命令帮助/能力回读、13字段类重新生成逐字节一致、163473份Unity来源冻结文件哈希复核通过；末次53项定向检查及13类离线C#编译通过。分发与总回执在`.private/full-project-handoff-01/package`和`delivery.json`，公开命令见`docs/BULK-INITIAL-DEV3.md`。此处交付的是可接续初版，完整玩法/全像素一致性/所有源版本支持均不扩大宣称。完整失败层及过程见`docs/validation/2026-10-25-bulk-development-notes.md`；机器回执在`.private/full-project-handoff-01`和上述outputs。清理维护已完成，不再扩清理。

## 历史：dev2语义校验与身份保护已接收

## 完成记录：游戏回流脚本修复，本地候选 0.2.0.dev2（2026-10-24）

v0.2.0.dev1 已发布并冻结（发布提交528b762）；当前独立本地分支`codex/game-adoption-fixes`。用户新增授权经总监原生turn01a16d5b-bb87-7013-af20-8b3fc6be7ab5/message01a16d5b-bd05-7ee1-999d-88320434dc3f核验，依据Manager/decisions/20261024-monkey-release-game-adoption/TOOL-FEEDBACK.md补齐通用语义校验、失败隔离和稳定对象身份保护。仅monkey工具侧开发，两个游戏只读；不启动Editor、不重导600Bundle、不推送或发布。游戏继续采用冻结旧包，新候选需明确采用。

第五轮最新证据：106对象严格读取成功，70既有对象字段/引用交叉核对一致；01–04错误不追认为正确。当前将可信头部、字段/数组/PPtr校验提炼至读取层，并提供冻结证据与精确目标身份的离线字段计划入口；全量读取不等于可写回，缺可信对照/目标映射时禁止生成写回载荷。实现与必要负例已完成：242项工具测试通过；新增读取层由1个精确冻结Bundle的17个真实借取对象验证。原对象70份重新哈希并独立读取头部，01阻止70/70、03/04各阻止2/70、05通过70/70。`unity-field-plan`以冻结可信对照、完整字段校验及源file/pathID→目标GUID/localId保护离线计划；任何失败整组无写回载荷。CLI和接入限制见`docs/UNITY-FIELD-PLAN.md`；独立dev2候选包与隔离安装回执位于`.private/game-adoption-fixes-01/`，以实际回执为准。未运行Editor或接管两个游戏的写回器。

## 历史：v0.2 声明范围本地交付与 dev1 发布准备

以下为发布前阶段记录；“未发布”和当时不唤醒肥鹅等约束只说明该阶段，不覆盖当前两个游戏回流修复授权。

## 发布前记录：v0.2 声明范围本地交付已验收，预发布 v0.2.0.dev1（2026-10-24）

v0.1 已发布冻结；当前本地 `codex/v0.2`，本次按直接用户授权发布v0.2.0.dev1预发布。用户持续推进授权及本轮进度核查已原生核验：总监 turn01a16bea-fe5f-7082-9583-f3a7f0292b56 / human01a16beb-0267-79b1-9472-e1ced602d6ba。原生验证仍限自有独立副本与单次≤30分钟；单主开发，不唤醒肥鹅。

- 已实现：公共CLI统一输入/精确远端获取、按资源与版本隔离、具名有据C#/TS/JS数值子集、ProjectModel typed引用与可选none/grea格式、Unity来源受限原生恢复、Cocos2.1.1/2.1.2/3.4.1/3.8.7资源及部分图、Egret5.2.32自定义资源/图集。Research最新重扫仍11例，10例不同范围输出、1例未导出、完整游戏0，详见validation/research-v02-status.json；候选数量不代表完整兼容。
- 补源：机智147的13091份精确远端文件已取得，19298项声明资源missing0，双端最新07静态零诊断（完整新版Editor/玩法not_run）；天命当前3包336缓存与Cocos3.4.1来源已冻结，11618确切下载项齐，版本专用资源/节点/实例reader及公开双目标05导出已完成。灵画师核实Egret5.2.32，不记作Laya。
- 原生结构已验证：Creator3.8.7开发期模板DAG/局部ID/覆盖解析已接公共IR/Unity计划；114/119图可结构解析，5图缺6个精确模板；以Prefab.data闭包修正PveFightUI的3个游离记录后114图父子均闭合，其他图hash不变。Unity真实4Prefab/104节点/5关系及合成双实例/三层嵌套/Variant均完成保存重开、对应节点/模板未污染读回；Creator3.8.8同真实4Prefab/104节点/5关系及合成三层嵌套也已通过原生保存重开/UUID-fileID/模板SHA校验，严格0诊断。尚未恢复源脚本的partial与结构检查分开，详见validation/2026-10-24-native-prefab-relations.md。
- 动态UI已落地：同一真实SysDialogPop/StarGroup（16节点/2Prefab），Unity05与Creator05均严格0诊断，NONE/RESIZE_HEIGHT改字与隐藏恢复、Widget父尺寸变化、线性布局子节点增隐显删均通过；跨目标各阶段≤0.05px，TTF高度已对齐。Creator1972帧原生RECT网格也已逐项读回；详见validation/2026-10-24-dynamic-ui.md。
- 代表集成已过：同源4Prefab/104节点/5关系与新动态组件，Unity01严格0诊断、Creator04严格0诊断/editor pass；两端各2组动态探针。Creator子资源按原生SpriteFrame UUID保存/重导入并核对真实library，修复父meta已改而子资产仍旧；序列化后恢复自有活对象ID，避免Scheduler销毁异常。Creator04全部1972帧读回通过且无该生命周期错误，own75174已回收。01–03失败保留，详见validation/2026-10-24-prefab-dynamic-integration.md。
- 天命3.4.1资源公共双目标已过：11618已确认远端项齐（含4668备选编码）、11962文件/1011728200字节全入账；7071Frame/每端14142变体、1TTF/13JSON，04双端静态0诊断。真实5Frame/10变体两端原生0诊断，own82339/82795均回收。源码/Spine/未知后缀与原版UI未恢复独立列限，详见validation/2026-10-24-tianming341-resources.md。
- 天命图/追加结构已过：856/857图、22503节点、24511组件、52实例关系接公共05双目标；15位图字体恢复，1份原图四个null旋转值精确隔离。真实6Prefab/331节点/8关系/7新增节点/1新增Widget，两端原生严格0诊断，Unity04 editor partial（源业务缺口）、Creator10 editor pass；源Prefab及Unity最终Candidate证明独立核对。详见validation/2026-10-24-tianming341-graphs.md。Creator根继承、移除组件与任意新增类型不外推已支持。
- 本地交付已验收：总监事件monkey-v02-director-local-acceptance-20261024-01确认本轮声明支持范围通过，依据[总监本地验收决定](/Users/wangmeng/Documents/Manager/decisions/20261024-monkey-v01-v02/LOCAL-ACCEPTANCE.md)。分发02源码快照0a523d5、实现df68c59；两包大小/SHA、4份回执SHA及106包文件等于源码已由总监独立核验。隔离安装8条CLI、none/grea双端4份静态verify及232工具测试沿用既有证据，不再重跑。版本仍0.2.0.dev1，未正式发布；详情见LOCAL-v0.2.md。
- 版本出口：本地声明范围已验收，用户现已明确授权本次GitHub预发布。47份其他guard、缺模板、Spine/Egret源UI、未知方法/组件等逐case限制和Player/视觉not_run继续保留。此次仅发布现有已验制品及同一产品源码；不改变功能、不重测引擎，v0.1冻结。

## v0.2.0.dev1 发布

用户已授权推送GitHub并创建Release（总监原生用户turn01a16d40-0f79-7a52-9121-745c27b6565d/message01a16d40-1113-73a2-9d11-7085346ee514）。目标为私有chuxintec/monkey，固定tag v0.2.0.dev1、GitHub prerelease；v0.1冻结。使用已验分发02，不重打包或运行引擎。包源码快照0a523d5与tag发布提交的产品源码逐字节相同，后者另含最新发布文档与精简验收摘要。

开发历史及逐节点验收载荷在本地保留，不纳入远端发布历史；本发布提交由原main产生，正常快进，无强推。逐case限制、47布局guard及Player/视觉not_run保持原结论。详细能力、安装、命令和包身份见RELEASE-v0.2.0.dev1.md。

## 输出空间维护（2026-10-25 追加）

按用户本聊天最新清理要求，进一步核对并删除已标记废弃的 full-foodstreet-06-creator、10/11 Unity/Creator 及 structured-foodstreet-03–08 中的生成资源副本，共25个目录、330060份文件（占用20.31 GiB）；磁盘可用空间观测增加15.26 GiB。删除前逐文件核对生成所有权、字节数与SHA256，删除后276份源码、清单、原生读回和冻结包哈希一致。原始输入、SourceRecovery、验收记录、full14、所有bulk输出与当前增量验证所需Library保留。精确回执：`.private/cleanup-20261025-output-02/receipt.json`。未改功能、未运行引擎或发布；上方原生布局修复WIP保持。

## 输出空间维护（2026-10-25）

按用户本聊天再次提出的清理要求，删除肥鹅已标记废弃的03、04、05、07、08、09、12、13轮Structured生成资源副本，以及历史Unity/Creator可重建缓存，共90个目录、535052份文件（占用约38.67 GiB）；本次观测磁盘可用空间实际增加26.70 GiB。删除前旧资源逐项核对生成所有权、字节数和SHA256，删除后215份源码、清单、原生读回与冻结分发文件哈希一致。所有当前bulk输出（含后续增量验证所需Library）、full14最新基线、原始InputTree/InputCache、SourceRecovery和独立验收记录保留；历史目录补充不完整说明。精确清单及回执：`.private/cleanup-20261025-output-01/receipt.json`。此次不改功能、不运行引擎、不发布；批量初版主线仍按上方WIP记录推进。

## 输出空间维护（2026-10-24）

按用户直接要求清理7组已被新轮次替代的机智逃脱04–06／天命01–04输出，仅删除24个生成资源目录（du约21.83 GiB），本次观测磁盘可用空间增加19.07 GiB。InputTree/InputCache、SourceRecovery、原始获取目录、最新机智07／天命05、肥鹅14、验收集及冻结发布包保留；372148份保留记录与发布包哈希复核一致。旧目录已添加不再完整的说明，精确清单及回执位于`.private/cleanup-20261024-output-02/`。此次无功能改动、引擎运行或发布。
