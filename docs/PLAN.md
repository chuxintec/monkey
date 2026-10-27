# monkey 项目计划与执行进度

## 最新集成状态（2026-10-27，覆盖下方早期在途计数）

**本轮最终候选已可交付核查（不等于原版完整恢复）**：同源全部1555 C#五程序集0 error已通过，NativeFinalRuntime01在全部源码启用的独立完整副本中通过Board6/348格/24Sprite实际读回、GraphicRaycaster+EventSystem生产→revision0到2→201401精确Sprite→退出Play重开新协调器恢复，以及m4越界拒绝；Scene重开Missing Script0。正常exit0/reaped pid88827，report SHA `2e6a4eef637545ac37082193c1e3fd1fb311cf09b998ba0d47f914d859904cfb`；51083输入未变/声明MergeCell改动1/未声明0。首次sandbox licensing启动失败已正常回收，放开本轮系统访问后通过；两条QuickSearch启动异常仍保留，非零Editor诊断。完整玩法、原厂远端、视觉/物理/Player未验，模块代码仍partial/unreviewed。公开复现路径、唯一候选、包及限制见V0.6-FINAL-INTEGRATION。

本地工具包来自产品源码c8842d0（200文件），wheel889881字节/SHA3fbff8ba…877a，sdist1366344字节/SHAd710fb18…e2f4，均与源码字节一致。独立venv安装/跨cwd命令及35合成测试通过，2私有审计按合同skip；未全局安装或推送发布。当前阶段`local_final_candidate_ready_for_review`，不是`full_original_game_restoration_complete`；不再为旧警告/QuickSearch/音频/公式重开验证。保留局部不可恢复及未知原服边界，下一步由本版本审阅决定，不另起版本或默认扩范围。

**最终集中编译已通过**：公开CLI再合并6个API/坐标/Bootstrap修订，附加3份明确自编local-test JSON，稳定候选 `outputs/v060-foodstreet-architecture-01/UnityProject`，manifest `f843c056e8670fc35d756eca896d194a8013cbb5b614e9c0d25685420409c982`，51,082文件/1,555 C#。NativeCompileFullLayers01按实际Game.* asmdef名称分别编译全部Domain563/Gameplay70/Presentation882/Services38/Bootstrap2，**0 error / 3,249 warning**，Domain/Gameplay零Unity引用，无源码排除或假API。JSON前manifest `9d093b83f2a1ade2b2e90969b699df6e1f32e07d08d9af087cc7070293f1bf6d`与最终候选的全部C# path/hash相等。不是整版业务/原生Editor验收。最新入口与限制见 `docs/V0.6-FINAL-INTEGRATION.md`。

原生最终影响验证已准备完整副本NativeFinalRuntime01，51,082份来源文件及新增Editor脚本有ownership核验；全部1,555份代码保持启用。按既有人类授权及总监资源交接事件`monkey-final-native-resource-20261027-01`执行，启动前实际ps无其他Unity Editor/自有项目无锁；不依赖不完整的unity status证明空闲。核心检查仅限Board6源坐标/24 Sprite/生产触控→存储→Play退出重开/m4拒绝；结果待本轮实际回执。不追加全玩法/音频/进度条验证。

公开 `code-native-revise` 已将54项修订合入 `NativeFullCoreIntegration03`（根即工程，manifest `06abc50b9eec1793864b1fdfb792606ddb42314e8ea8745e656203ab03d74c31`）：51,076文件、1,555 C#。四组配置解析移入Services并保留Domain强类型，19个Tutorial/Narrative文件由实际来源及基类哈希证明继承API，不造方法。对应公开分类器修订只去除已证实的planned-member-missing，保留其他架构guard，条件编译/源漂移/私有成员/不明继承不放行。已通过9 inheritance、27 module、11 reassembly、10 pipeline、17 revision定向测试。

`NativeCompileSurvey08` 已实际编译全部1,555源、305真实引用，**23 error / 3,243 warning**：22处为SessionController的缺少enum alias/对immutable GameSnapshot使用with赋值，1处为GuideController调用已退休FromJson；相关模块正在有界修复。不是旧Survey07的326缺类型诊断，也不能把警告计入错误宣称回退。原始模型代码仍unreviewed；五层独立全编译和最终原生接线仍待完成。

剩余两个planned missing分类：PayTiersBasic原JSON仅3字节`{}\n`，已由EmptyTableDescriptor+严格reader承接，旧空行class不补造（原classPath仍保留缺失，API退休有证据）；UnityAudioService的原候选显式Unavailable，缺少pinned Audio模块和typed native引用，不补假播放。两项均不等于全工程/全部业务正确。资源47956份冻结path/size/hash一致的既有证据复用，不重复全导。

坐标核查发现Presentation01对Board2/Board6上下翻转，生成格子不在会滚动的Layers下。`NativeCoreBoardCoordinatesAudit02`已据源字节定位；Presentation04按源坐标保留全部348格，index335在m0 mask-local(250,-150)、m4(250,-550)。输入router旧翻转同时待改，Bootstrap07已准备显式viewport/mask/fog注入；尚未做新的Editor/真实触控/画面对照。RuntimeProbe03原事务与重开证据保留，其视觉一直not_run。

本轮集中最终集成，不增加旁路平台或下一版本；按总监 `monkey-v06-final-integration-focus-20261027-01` 汇合公开工具路径、完整候选、全源码编译与受影响核心原生验证。无发布/推送/安装/正式游戏写入。

## 早期核心接续记录（保留历史状态）

2026-10-27 核心联合编译：NativeCoreBootstrapRevision01真实Content/Session/Presentation/Bootstrap窄链共66源码、183Unity managed refs，以netstandard2.1/C#9编译0警告/0错误；含明确compiler shim而非游戏DTO替身，整47仍未过编译。34终态1159源文件早期全编译72条均为未来模块namespace缺失（NativeCompileSurvey04，不外推其他错误不会显现）。公共candidate按实际record/init需求生成唯一Domain公共IsExternalInit及稳定meta/ownership；真实无shim复现CS0518，有shim通过，48组装/reassembly/revision定向检查通过。Session02已在真实28格Board2保持初态的独立local policy下完成normal→同IDweb merge、升级消网/原子存储/重开并标remote-unreconciled，正在接五层编译与自有PlayMode探针；非原厂角色/远端成功，物理输入/视觉/完整游戏未验。

2026-10-27 核心接续实绩：Orders34 已通过公开 module-recover 离线物化64类，worker receipt 明确 partial / exit-not-recorded，事件SHA ce4917e326cfeb8af4876bdb6dbe6b759367c688a3e808e6538b5dbb047945f3；公开只读 recheck 64类通过。没有伪造OS退出0或重跑模型。当前唯一串行 supervisor 接续 NativeCorePriority03，34终态、Street35在途（以run状态为准）。恢复、module/revision/pipeline与JSON producer共102定向测试通过；新JSON producer只附加明确自编local-test资产，未补音频。五层词法守卫禁止Gameplay反向Services等依赖；未完成类型不会生成空壳。启动helper已写WIP，核心View拆纯core helper以切断legacy GameSnapshot44活动依赖，完整旧API与全量类型继续保留。整候选编译/真实启动未完成。

2026-10-27 中断接续：NativeCorePriority03 的 Content32、Production33 已终态；Orders34 模型事件已含最终JSON及turn.completed，但父supervisor中断，未记录OS退出码。未重跑模型；先补严格离线恢复，共用普通worker校验，明确exitCode/returnCode=null并保留原request/process/event SHA，随后继续Street/Tutorial/Bootstrap。当前核心整合：Content08真实11 JSON helper已交付；CoreSession typed role JSON/事务存储与源Board28格、CorePresentation旧API兼容及真实输入/metadata、父CoreBoardBootstrap正在统一编译。Bootstrap新WIP保留旧全量root、显式Editor candidate-local-test，无原版认证/远端成功声明。全47范围继续，所有活动aggregate尚未闭合，整工程与运行仍未验收。不新增音频/进度条证明。
## 2026-10-27 当前目标：整体原生Unity架构恢复

用户新要求已本聊天原生核验：总监turn `01a17b0d-59e9-7d63-81fa-329046f0007c` / human `01a17b0d-5a06-7f73-8d96-4057429299ba`；事件`monkey-v06-architecture-first-stop-old-20261027-01`。**旧逐文件修补方向被替代，不再以6445旧文件逐个审过为出口。** 目标为Bootstrap/Domain/Gameplay/Presentation/Services五层架构，先确定全项目模块、核心类及功能类，再把来源代码段和字段依赖归入语义化类，编译及代表业务链拉通。不能只改名/搬目录，不能复刻JS/Cocos运行时或用空壳补业务。新独立候选按版本化架构/符号/所有权计划生成，旧“本批不可增删文件/不可改类名”限制不再用于新架构；正式游戏与原始证据不变。

旧队列已在第46批合作式自然收尾，3476/6445已处理，2969未处理原样保留，子进程已退出，第47批未启动。旧结果是可复用原材料，不是有效原生架构交付；不补跑剩余40批、不默认深修全部partial。未启用的5C效率WIP九文件与tracked patch已逐字节副本封存`.private/v060-architecture-first-20261027/StoppedEfficiencyWip01/receipt.json`，产品代码恢复4ed6f6c基线，不再推进该优化。项目继续开发；已完成全局架构验收，正按完整功能模块生成与原生资源接线实施。无新的模型/上下文/CLI并发、依赖、发布/推送/安装或正式工程写入。

### 当前执行记录（2026-10-27 架构阶段）

**最新统一候选（全47资源 + 核心修订）**：公开只读reassemble已产`NativeFullIntegrationBase01/UnityProject`，manifest `a85f070569609e2cf1162b1b0124c4526ac054d7925b4aa59bbc7a8373b36a0e`，50,792文件/1413 C#/1408实现类path/76缺失。再公开code-native-revise应用100项（7 replace/93 helper）生成`NativeFullCoreIntegration01/UnityProject`，manifest `79b8f27df093fea2bebdddbb89c11c3c9a1df35634f0ac736294ef821977da0e`，50,978文件/1506 C#/37缺失。此处“实现path”仅指有归属源文件，不证明功能恢复。NativeCompileSurvey07编译全部1506源、无排除/假API，共326诊断（CS0234=53/CS0246=273）；比37模块旧254增多是加入余10模块暴露新类型依赖，不能称回退/已过全编译。主要缺UpgradeRace State/Command、CookfishController、FoodDelivery State/Command及三untyped definitions。源/原候选/失败收据均保留。

**真实核心内容扩展**：ProgressionContent01通过4个真实TextAsset调用封存Orders03/Street02 reader，只有两边全部成功才发布，否则清旧catalog并失败关闭。Bootstrap05已接这四表与Session04，137实际源按Domain89/Gameplay17/Presentation5/Services25/Bootstrap1五个独立assembly编译通过，0 error/33 CS0649序列化字段警告；非全候选、非Editor。Presentation02曾反向引用Bootstrap，未采用；03改typed delegate+clock注入并独立Presentation→Domain/Gameplay编译通过。父正在Bootstrap06接线，Board6可视/滚动及201401精确Sprite缺口仍在，不能称真实生产触控/画面通过。

**47模块生成终态与组装修复**：NativeRemainder04 已取得全部47份终态收据（具体generated/partial计数见CoreIntegrationExecution02/pipeline-assembly-failure.json），单一真实CLI supervisor exit2/reaped；失败在自动aggregate将所有完整source-ID映射代码标partial却缺少具体未审阅原因，严格assembler按合同拒绝IGameCommandPort。原state仍保留running属于失败前旧状态，不能据此称模型还在运行；不改旧manifest/收据。公共修复`fe1ebe9`保持partial并写明确semantic-unreviewed原因，且未来收集/组装异常持久blocked并清activeModule；21项pipeline/reassembly定向测试通过，回归测试先复现缺失原因。当前使用公开code-native-reassemble新输出重核47终态，不重跑模型、不放宽assembler。

**核心接续（Session04 / Bootstrap03，待全量候选整合）**：真实11表与Board6（58×6）生产源201801/index335→201401/index334，已进入唯一CoreSession coordinator与v4原子快照，新协调器重开保持生产计数、seed、HP/timer、metadata和单一RoleRuntime能量；失败写入/旧revision不发布。源码GetClosestBlankCell仅排除occupied/locked，旧Production01额外排除空UnderBox导致错误选格；04已按字节pin纠正，旧候选保留。政策为明确自编session-policy/3及production-policy/2，不代表远端状态。原policy/1候选Integration03保持不变，下一候选必须从无JSON新基线附加新政策。

Bootstrap03实际83源码/6项目/183 Unity refs联合netstandard2.1/C#9编译0警告/0错误（MSBuild求值后的receipt `38957b0ba8ccfe6db0286cd9be1cd83d949ddc4be17b6daee0d28b5ad7d2251b`；旧清单脚本忽略Exclude误报88，旧receipt保留，5个排除项与errata已记录）；只证明核心闭包，不替代完整47编译或Editor。Session04的7/7 UTF8 byte spans、31/31源码、11/11表hash复核通过；Production01的三条误将字符串偏移标为byte的来源引用已在04 errata记录，旧证据不改。当前Presentation仍只把同格点击发为SelectCell，生产点击与Board6完整视口尚未接通，core_presentation在独立Presentation02查源接线。

**Orders/Street依赖审计**：Orders02 harness曾有手写OrdersDefinitions/NamespaceMarker，其编译证据无效，保留原件与errata；Orders03改为真实Module0034及Integration03依赖后，3432行原Order JSON严格reader/构造编译通过。43项Compile pin核验通过，无替身，19项Link虚拟显示路径仍旧名不影响实际Include。Street01 typed proposal与Street02真实Build954/Area26/Adron409 reader使用真实依赖通过，复核无fake API；Street02 parser两处引用行号不完整记录于follow-up audit，实际严格实现/反例存在。Orders/Street目前仅定义读取与Pending proposal，不声称Session原子消费、RPC或奖励成功。

**最新可核查候选**：`NativeCoreIntegration03/UnityProject`已通过公共`code-native-add-json`附加显式candidate-local-test policy/1，manifest `428bbbff87daa0dc9716bfeb25d0473c8fbe1456961d92f5ad66e0a4b1de9dba`，50,516 files/1,274 C#，1269 implementedClassPaths/247 missing。C#全清单与下述Integration02逐path/SHA完全一致（inventory digest `bdceeae63b09bb288cea1ef57a4a2e50191037731e909a6548e5c5fbaedbbb58`），因此仍保留254静态诊断，不宣称已编译/运行全工程。JSON首次自拟声明不等于严格合同固定文字，在输出前拒绝；失败spec/receipt保留，新的JsonPlan02按明确“Self-authored test data; not recovered from the original game.”声明成功，未放宽validator或改旧输入。完整操作回执在`CoreIntegrationExecution01/result.json`。其后的Session04/Orders03/Street02成果见上方；下一主链为全47重新组装、统一源修订与整工程编译。父仍单写公共契约/候选与唯一实际模型队列。

**公开整合更新**：公共`code-native-revise`已实际将核心69-row计划与strict record39-row计划合并（ShopColumn只保留有双来源pin的record+关键词修复版本），一次应用107项修改；`NativeCoreIntegration02/UnityProject` manifest `2c5d2e358c4f88614a47fb0ccccfc161a942480a165f3d064e7a0f0dac2ce33a`，50,514 files，1,274 C#。完整未排除静态编译`NativeCompileSurvey06`为254诊断（CS0234=103/CS0246=151），相同基线Survey05为615，预留缺失类型247；仍未编译通过，不隐藏Cookfish事务所有者/缺失FoodDelivery等类型以凑成功。record39项经实际Unity Roslyn C#9/netstandard2.1闭包编译通过，另7项明确保留拒绝。公共revision单次root namespace扫描实际2.778s，已按单次调用复用验证结果以避免71 helper重复扫描，所有文件hash仍在copy前检查，17 revision+10 JSON unittest通过，源码d6ac314。

历史检查点：Production01已交付真实11表/Board6的201801→201401候选规则与typed port harness，远端仍Pending；其后Session04已接真实CoreSession原子store（见上方）。core_session继续独立Session04补唯一写者、完整runtime与versioned codec/真实重开，不写02/03；worker_recovery继续独立Orders01来源规则。其余模块NativeRemainder04继续同一真实CLI串行，版本未完；不追加组件旁路验证。


**最新已实测核心链（本段覆盖下方在途历史）**：`NativeCoreRuntimeProbe03` 使用 Unity6000.6.2f1，真实11份JSON/TextAsset→Board2的28格/15占格/10种原生Sprite→源MergeScreen/Cell Prefab→EventSystem点击与16→17带Web合并→原子本地JSON→退出Play后第二次新coordinator从盘恢复，报告passed；revision0→2，BoardCommitted与ViewRender各2，source清空/target升级9001102并清Web，身份/状态文件哈希保持，Prefab保存重开引用和无MissingScript检查通过。own native child exit0/reaped，458 owned文件未变，仅2个声明可变源Prefab在独立工程挂接后变化，核心C#没有手改。`Evidence/core-runtime-probe-report.json` SHA `3f075848a8fe16f6d59597389b12406b47be1fc3a9bab2309b1a90e3f2a5ca7a`。这是实际核心闭包而非全47工程；physicalInput/visualComparison not_run、remoteAuthority not_connected/RemoteReconciliationPending=true、whole47 not_verified。Editor日志含2次Unity QuickSearch启动索引异常（栈无游戏代码），保留原文，不能称零诊断。

原生前两次记录保留于Probe02：01在Play前因私有authoring plan误用Single Sprite的旧切片internalID拒绝，冻结native readback实际fileID21300000用于校正，未证明公共exporter缺陷；02原生挂接完成但CLI自动`-quit`提前退出，报告停留running不算运行成功。Probe03在同一既定窗口使用同一已安装Editor原生batchmode入口，无`-quit/-nographics`，由终态hook退出，不改引擎/许可证/全局安装。

`NativeCorePriority03`自然完成37份终态并返回integration_checkpoint；公开`code-native-continue`启动`NativeRemainder04`原位复用37份，余10模块继续，实际只一条模型执行。首完整资源整合候选已公开reassemble：实际路径`NativeCoreIntegration01/UnityProject/UnityProject`（重复一级是输出契约结果），manifest `3cc924310c1b5839dd669c3cc8f56ba3914b5a96388597f295bc63e12f73c68c`，50,372 files/1198 implemented class paths/286 missing，尚未纳入人工核心修订，不可称全工程编译通过。父接续公开hash-pinned revision/JSON和主工程集成；worker_recovery仅准备闭合核心revision-plan，core_session独立落实真实Production功能，Session03移动/交换规则离线通过而原生尚未运行。版本继续，不增加音频/进度条/公式旁路工作。


当前主链运行以`NativeCorePriority03`为准：02在模型初始化前受沙箱app-server/readonly database限制，0模型session/0代码变更，失败完整保留；新03固定02/01 lineage和31模块原始pins，正常用户运行时权限已获执行层批准。Content四类已实际生成，Production运行中；下方02描述保留交接历史，不代表当前活动目录。补充native implementation context已可通过公开module prepare的hash-pinned `--supplemental-csharp-spec`传递给后续Bootstrap：只读C#实际API、非原来源归属，缺pin/篡改/重复输入拒绝。19项module检查与9项pipeline检查通过；不重跑旧组件/原生验收。

**当前主链（§7纠偏）**：已核验总监人类turn `01a17c1d-92eb-7df2-9a66-3b03bf87c8ce` / human `01a17c1d-9448-7822-903e-d4fe113396ab`及Manager计划§7。NativeProject01在31份终态结果后安全收尾：当前模型自然退出，父取得既有worker互斥锁阻止下一模型启动，supervisor因`POSTPROCESS_BUSY`退出；Production仅prepared，无进程被杀、旧request/终态模块未改。新公开`code-native-continue`生成`.private/v060-architecture-first-20261027/NativeCorePriority02`，以旧request/state与31模块manifest pins原位复用，不复制私有context、不重跑31模型；优先Content→Production→Orders→Street→Tutorial→Bootstrap，在Bootstrap自然结束后返回integration_checkpoint供集成。剩余ProgressBoard/Settings/SmileBuff/Social/SurpriseBox/UpgradeRace/WeekTask/WeightRace/WoodGame/GooseSimulation全部保留，下一次run继续，不缩范围。当前Content模型实际运行；旧47终态后才集成的安排被覆盖。

当前完整可编译候选**尚未产生**：冻结资源基线为`.private/v060-draft-quality-20261026/FullDraftCandidate07/UnityProject`；新完整架构实现在上述NativeCorePriority02加只读复用的NativeProject01模块；首个核心整合目标为`.private/v060-architecture-first-20261027/NativeCoreIntegration01/UnityProject`（待主链模块/修订到齐创建，不宣称目录已存在）。`code-native-reassemble --allow-incomplete`现可在停止的集成检查点生成含全资源/全classPaths且明确missing的候选，不伪造未生成类型；普通reassemble仍要求全部终态。50项candidate/revision/pipeline/reassembly定向检查通过。

首条链仍具体缺：Content实际TextAsset端口/配置聚合，Board.element源冒号格式→真实CellState初值，Session核心唯一写者/本地文件恢复与MergeBoardController有效提交，原生Toucher与Render真实绑定/刷新，以及Bootstrap装配。已实现可复用部分为严格JSON reader与Session/Audio/Inventory等表工厂、MergeBoard的Select/BeginDrag/Move/Cancel规则及PointerRouter、string AccountId/long RoleId分离的版本化本地store；现Controller仍整体Unavailable、原View.Render仅保存Snapshot，不能报主链通过。会话/配置/Presentation三个模块正协同补这些缺口；Production/Orders/Street在新优先队列生成，不能因未知原服把本地交互全部禁用。合法测试角色须显式candidate-local-test且不冒充远端认证/奖励；合成2×2只能单测，不能代替真实配置主链。完整工程编译/运行仍not_run。

非主链专项暂停新增：音频Integration03未写入；派生资源producer两文件未验证WIP完整封存在`CorePriorityHandoff01/DeferredResourceProducerWip01`，未接CLI。已完成音频/进度条/公式/绑定证据保留并复用，不继续扩向量或重验。Unity授权分流已成功且窗口结束，不需用户重新登录；不再为同一问题重启Editor。

NativeAudioNativeProbe01实际原生验收通过：Unity6000.6.2f1导入357路径（356冻结Content+1有receipt的派生WAV），0失败；67 cue、31个独立AudioSource的序列化引用、Prefab保存重开及service可用性通过。方法16秒、own launcher退出0且回收，窗口结束后无Editor残留。633源音频行重新哈希全一致、冻结07 manifest不变。首轮沙箱因授权数据库只读在方法前退出198，保留失败记录；只读核实既有Unity Personal有效后，正常用户运行时权限复测通过，无激活/安装。隔离probe锁文件仅内置audio依赖depth从1变0，版本仍1.0.0；记录差异，不篡改原ownership。`Evidence/latest-editor-probe.json` SHA `5edafc7e35691fa3a200f294dd3081ac224288ecf2daacc9bd04e17110abe985`，postrun回执固定输入与输出。没有调用Play，声音播放/游戏触发/整工程仍未验收。

当前29/47终态、Playable运行中（实时以run为准）。AudioControllerRevision02显式JSON初值及74组件断言通过，legacy Session测试替身明确排除候选；继续NativeAudioIntegration03修正本地播放/停播与cue前缀，不能以gain0冒充停播。NativeServicesContent06接实际Inventory聚合/singleton与reader，不发明配置键。通用新增资源producer开发中，仅向fresh candidate新增有pin的JSON/WAV及派生meta，不借C# revision偷写资源或修改旧07。

新组装器补齐manifest-owned `.cs.meta`/`.asmdef.meta`：Script GUID按project namespace/root namespace/classId派生，不因方法正文或输出目录变动；冲突中止，全部路径与输出预算核对。`scriptIdentities`记录实际C#/meta SHA，后续revision保留旧GUID并刷新新C#哈希。绑定planner可验证完整新candidate manifest pin、原架构/来源、未变的模块class字节、owned meta与GUID/index关系，取得后生成authoring意图，不改旧module receipt；修改过C#仍须新receipt。62项相关定向检查通过。当前在途supervisor使用旧导入代码，47模块终态后以新reassemble组装才会采用，不热改已完成产物；整工程/Editor脚本挂接仍待验。

音频实际漏导已定位并补通用normalizer：633条扩展名文件记录=356 Content路径+277 SourceRecovery原件，276原件与Content同字节，另1份fireworks.m4a（46,239B）此前`UNSUPPORTED_NATIVE`而未生成Content。新增可选本地ffmpeg有界解码，固定provider版本/二进制SHA、输入/输出SHA及PCM形状；8MiB输入/16MiB输出、超时/child回收/截断或无效WAV均明确失败，不造音频，原件保留。实际公共normalize→Unity plan→export得到483,590B、44.1kHz立体声WAV，SHA `6e088bebda4142fb535d12244e36dd2ef89c609b0f38d3c8149d3e0c56f8dbe8`，目标`Assets/Game/Content/Audio/Sfx/MiniGames/Garden/Common/fireworks.wav`；原件哈希不变，10项decoder/6项progress/4项原target回归通过。NativeAudioNativeProbe01正在接收该派生资源，356+1导入与67 cue/31 sources原生保存重开尚未运行；不是冻结07已被修改。

当前队列检查点28/47、Platform运行中，原顺序和请求未动；Street/Orders/Tutorial在实际前置到齐后用新prepare补齐输入，仍0额外模型调用，GooseSimulation待Street真实实现。NativeCompileSurvey03/Revision02固定24终态模块825 C#（排除prepared seeds），复用显式ShopColumn补丁后84项错误全部是未来模块namespace；新增11模块442文件无直接诊断，闭合Domain303文件编译通过，完整工程不称通过。NativeSnapshotRevision04保留string AccountId与long RoleId独立，自有文件存储/20状态codec组件78断言通过，GameSnapshot aggregate仍pending。NativeServicesContent05读10份实际JSON、Inventory的60/32/8行与Launcher单对象已核，聚合schema仍需修正，不能冒造singleton字典键。Audio本地偏好controller正在新02移除C#默认音量并改为显式JSON初值注入；独立音频开关的停播/恢复及PlayCue仍pending，使用legacy依赖测试替身的组件检查不当整工程验收。

原生进度条已从私有验证提炼到公共`normalize/plan/export/native-import`流程：精确横向正向Tiled子集以非交互Slider+序列化宽度driver保留原节点和360完整长度，不拿380父宽替代。真实CardSeasonMainWindow独立42节点候选完成保存前/重开后8次值变更/几何检查、0 Missing Script、引用及源58文件哈希不变；另生产CLI两节点合成来源全链实际导入Unity6000.6.2f1，编译/保存重开/引用及静态验证0诊断，own child退出。竖向/反向/竞争控制者或无方向几何证明仍handoff。公开inspect入口的局部import遮蔽故障已由实际CLI复现并修复。组件与流程验证不代表完整游戏/物理输入/视觉验收。记录`NativeProgressBinding01/`、`NativeProgressProduct01/`；23项相关定向检查通过。

公共Prefab authoring planner进一步要求精确class↔script证明：固定的架构bindingEvidence、源码RF字面量注册/字节offset/UUID、模块所有权、唯一目标MonoBehaviour类及source component type同时一致；共享sourceUnit不能代替身份。缺旧证据保留unresolved/0操作，矛盾或歧义拒绝；C#注释/各种字符串假声明不能通过。父复跑19项通过；实际CardSeasonMainWindow新Revision03身份成立，但Script meta与其他字段仍未齐，计划0操作，不把原生进度条组件验证当成整窗挂接。NativeBindingInventory02在21终态模块快照中固定302 View、193精确身份/638未证、102计划0操作。

NativeProject01继续同一47模块实际串行队列，检查点22份终态输出、Inventory运行中（实时以run为准），不改旧request/state/manifest/顺序。NativeSnapshotRevision03固定当前44状态/29模块输入，18个codec形状闭合、26个具体pending，75份真实/生成C#以C#9/.NETStandard2.1编译、66断言与再生签名通过；完整GameSnapshot仍未生成。02存储long account与实际Session string AccountId不兼容，正在新04单独修订，RoleId不互换。NativeServicesContent04与AudioRules已通过实际6 JSON/27音频行及C#9/.NETStandard2.1检查，尚待真实IGameContentPort。NativeAudioCatalogFix01修复校验失败后发布半成索引，75断言通过且原版本同用例复现失败；未接原生AudioClip播放。各组件仍需统一candidate revision与整工程/跨层集成，不作整版完成。

2026-10-27 Interface准备预算已实修：完整10,397,795B绑定上下文（1,997 bindings、1,997 unresolved、284 sourceOwners）按无截断index+5片输出，最大片<8MiB，重建SHA `0eadd326c47b39553c13067fcc21df57c4199644516583ea0b49154484c59a23`与完整原文一致；含其他worker context共23,674,228B/64MiB。小context格式兼容，新增loader在只读recheck中重建后继续核查原件/目标资产pin，prompt要求读取每片；7项asset-context和17项module定向检查通过。只为尚未开始、且所有较早声明类型依赖均已终结的8模块（Interface/Inventory/MergeBoard/Narrative/Platform/PlayerProfile/Social/WoodGame）调用prepare，保留原排序、run request、已终结module manifest，0额外模型调用；Interface实际230类/48配置输入及所有context pin已复核，旧supervisor可按原序消费新prepared任务。Orders/Street/Tutorial/GooseSimulation等待更早实际依赖实现到齐后再准备，不提前省略依赖。

Audio/配置组件进一步交付：独立NativeAudioRevision01有67条实际clip路径/meta/GUID证据（全候选633份音频中的相关子集），UnityAudioService/V2接口编译通过，尚无Editor绑线/播放；NativeAudioRevision02更正“无配置”为“原表均存在但未接reader/aggregate/clip”。NativeAudioFixes01对原AudioDefinitions无参空表壳作显式old/new SHA修订；新三表constructor实际校验27行/74字段，TryGetPropSound(17)、click cue→Common/sfx_ButtonClick通过。NativeServicesContent03四helper精确五层namespace与架构校验、.NET8编译及6个真实TextAsset读取通过，整体Loaded仍false、尚未接真实Content接口；AudioRules对已加载Definitions的空UnavailableReason兼容修订继续。

NativeSnapshotRevision02为自有候选本地存储，11份C#通过实际path/type/namespace校验、C#9/.NET Standard2.1编译与51断言文件重开验证（两种真实State、旧revision拒写、同revision冲突/幂等、损坏不覆盖、取消与分区）；不处理原厂存档/远端成功，单进程writer条件明确。ownership SHA `71621ed3350b02ca6e3c1e013a7c46ffda53bb5f6fccb4b31189a7bdbda7f1c5`，01字节保留。GameSnapshot实际44种唯一状态仍有缺源及身份/接口接线缺口，不填空默认冒充完整存档；上述均为待整合组件，不是整工程或玩法验收。

2026-10-27 新prepare边界实测：主队列已保存16/47首轮模块，Flower运行中。在不改变既有输入/状态/排序前提下，尝试为尚未启动且无缺失前置实现的Interface预置class+chain配置context；模型调用前发现完整module-asset-bindings.json超过8MiB，尚未成为prepared任务。完整失败Evidence已移入NativeFutureContextPreparation01/InterfaceFailedPreparation01，0022槽恢复不存在，未调用额外模型。正在按每片/整组双预算实现无截断绑定上下文分片，完成后才准备新任务供既有supervisor按原序消费。

同一真实失败暴露prepare异常会遗留无request/state的输出目录、阻碍后续续跑。现仅对本次调用成功独占新建的目录，失败时整目录移至同级.prepare-failed-唯一ID并写明确未调用模型/不可续跑回执；原已存在目录绝不移动。17项模块检查通过，含完整Evidence保留、槽位恢复、拒绝接管既有目录；不删除失败证据，不改既有运行模块。

2026-10-27 配置上下文根因补修：实际Audio旧manifest configPaths=[]，但Global05三Definition的configPaths/fieldKeyMap及冻结CookSound/PropSound/SFX完整存在。producer此前只取integrationChains.configPaths，现取所选classes.configPaths与相关chain并集，继续验证catalog/完整字节/SHA/预算；15项模块定向检查通过（新增类独有配置/篡改反例）。NativeConfigurationContext01实际只读重建AudioContext02并完整携带三表；静态影响18模块、180个模块内遗漏路径引用，非180份唯一文件。既有运行supervisor已加载旧函数，不热改当前队列或旧context；完整实现经独立版本化修订消费真实证据后再集成，未据此自动宣称旧输出恢复完成。

BigDaySourceBehavior01以146份Domain编译产物实际读取原BigDay/BigDayRaceStage JSON，对四段精确源公式独立Python binary64转写的1,005分数/阶段/进度向量及9毫秒时钟边界执行通过，.NET8编译0警告/错误。原JS未执行，仅实际JSON、安全整数及秒→毫秒合同子集；活动启动/奖励/结算/服务端、Unity与整工程仍未验收。

2026-10-27 原生引用接线前置核验：bindings模块已从原始Cocos2.4 pack/config准确恢复CardSeasonMainWindow 16个序列化属性，UUID index3137、pack0621940b9 section2640；42源节点与冻结Prefab child-index路径/名称逐项同构，既有保存重开readback确认42身份。12个显式字段映射均有真实源引用及目标路径，其中10个类型兼容；progressBar目标只有Image而C#要求Slider，label_title缺TMP文本，另4源属性缺新C#字段。NativeBindingPlan04 SHA `05e94087f9a55a02f58b8b7d887979562407a5073063ddf9b5d56f4e2be721bb`保留具体缺口；新Script GUID/MonoScript未固定，0个Prefab写入操作，不宣称已挂接。12项定向测试及py_compile通过，后续批量所有已终结View的真实盘点继续。

NativeDomainCompile01完成13模块中146份无外部待生成类型依赖Domain源码的实际C#9/.NET Standard2.1编译，0诊断、无Unity引用；仅使用上述ShopColumn显式语法修订。GameSnapshot/RemoteReply依赖未生成功能状态，明确排除并保留分母；没有假类型或空壳补依赖，不代表Gameplay/Presentation/整工程编译、原生运行或业务等价已过。

2026-10-27 最新接续检查点（非整版交付）：NativeProject01已保存前13/47模块首轮输出，FireRank实际运行中；实时状态以原run为准，不改其旧清单/输出或重启旧6445队列。新增`code-native-revise`按base manifest、修订计划、旧/新C#哈希和类/layer/module归属生成新候选，完整保留资源/JSON/包/设置及已有meta；新助手生成独立meta。16项定向检查、实际CLI合成候选烟测和源哈希不变通过。类归属与implemented/missing必须一致，普通/已采用工程拒绝；compile/runtime仍not_run，不把构造候选当验收。

NativeContentRevision01在55个direct schema、56个实际JSON路径执行1,584行解码及13,334字段回投，失败路径0，8项组件测试通过；45个Content port方法仍39 pending，未与完整真实接口编译。NativeRandomRevision01已实现两种独立原生随机流和显式单位区间/范围接口：.NET8组件编译0警告/错误，4,292源公式向量及1,000状态续跑步骤通过；没有执行原JS，尚未接真实Merge/Foodom调用或Unity。ownership和原source/hash各自固定于私有工作区，后续统一revision-plan后整合。

NativeCompileSurvey01只读固定13模块/383份实际C#，用已装Roslyn C#9、.NET Standard2.1及Unity6000.6.2f1引用检查；首轮确认Commerce.ShopColumnDefinition构造参数`event`的语法错误。NativeCompileFixes01仅在独立修订artifact改为`@event`并保留旧/新SHA及模块pin；Survey02该语法错误消除，仍128项CS0234对应尚未生成的模块。未添加假类型、未改运行队列，非Unity/整工程编译通过。后续完整47模块、核心业务补全、真实Editor序列化接线与主业务跨层链继续；音频实际实现与原包Prefab引用→原生组件计划并行实施，不能以工具/组件交付结束版本。

2026-10-27 后续检查点：前6模块首轮已保存，CardSeason实际运行中，后续40模块待处理。重组回执及新候选manifest现已保留各模块准确Task status/outcome/responseSummary/unresolved及Task SHA，结束前复核漂移；8项重组检查通过，包括具体缺口保留、Task回执篡改和大于8MiB标准manifest。冻结来源47,954条资源/设置清单序列化已达9,450,616B，不能套用单源码8MiB边界；新候选清单沿既有128MiB候选边界读取。

RuntimeSourceReview01完成两随机流的只读调用核查，9份切片与冻结源逐字节匹配，review SHA `8494b0a30bb026853a4db0acd5df4aacfa14ba83bae45c515000a038b11066a6`。eh合并路径每次抽样写回remoteData/board seed；WX按channel缓存或临时洗牌，不能共用一个全局随机源。当前IRandomSequence不含单位区间/范围语义且Merge/Foodom尚无显式消费者，需要后续有据版本化接线。报告另发现FoodomRules.StartLevel的两个member ID来自Screen/Preview入口；这些只能作为责任来源，不能当Domain方法已恢复的证明，修订前须核正方法归属。来源residual没有精确member索引时继续明确unit级边界，不编造method身份。

2026-10-27 接续：NativeProject01已保存Session、Runtime、Audio三个完整模块的首轮实现，BigDay正在实际运行，其余43个模块待处理。旧进程仍沿已固定合同串行执行，不修改其清单或源文件。Session的4个有效声明因用户提示字符串中的`not implemented`被误判为种子残留；已修复词法检测并新增只读`code-architecture-module-recheck`。实际复核Session为21/21 generated_unreviewed，Audio为15 generated_unreviewed / 1 incomplete_contract，旧request/state/manifest哈希均未改变。回执保存在`ModuleRecheck01/`；分类通过仍不代表语义/编译/运行验收。模块定向13项通过（新增3项，其他既有检查不重跑）。

Audio的UnityAudioService确实缺少设计的AudioSource字段和播放实现，不能通过放宽检测消除。本机6000.6.2f1已有com.unity.modules.audio 1.0.0，但冻结候选未声明；已只读固定其package.json身份，没有安装或修改包。另从原始main/game.js发现两种不同种子随机算法：合并棋盘eh（9301/49297/233280及22643→22646特例）、Cookfish WX（1664525/1013904223/uint32）。原始正文、字节区间、SHA及所属sourceUnit保存在`IntegrationFindings01/`，WX窄范围见`rng-narrowing.json`；尚未集成，不能继续把“算法未知”当作永久适配理由，也不能将两算法全局互换。后续按来源调用点补齐真实核心实现和候选包/序列化引用，再做整工程编译及业务链。

当前父单写CLI与集成；code_regeneration已交付检测/recheck并停止写入；codex_postprocess正在实现只读重分类后的新版本汇总。新汇总必须保留旧模块manifest SHA和逐文件新诊断，只接受精确已保存输出，不重跑AI、不覆盖正在运行的队列或旧候选。整版与原生验收仍未完成。

已实现 whole-source 架构准备/执行/状态三命令及结构合同，源目录不重导；1831个完整注册区间和补充区间、21999个成员、548份实际JSON、1698个Prefab/Scene身份作为规划输入。成员索引按SHA分片，不因单文件8MiB边界删减。GlobalArchitecture02因CLI自身状态库/app-server沙箱权限在模型启动前失败，原回执保留；新独立GlobalArchitecture03沿现有Codex配置经正常权限启动，其原始分析已结束，后续修订验收见下。此阶段只形成架构合同，不能称原生实现/编译/运行已完成。

主开发持有唯一真实CLI和共享架构/CLI/集成写权；复用code_regeneration实现按完整功能模块prepare/run/status（精确来源、预规划目标、全局合同及依赖实现、模块回执），复用codex_postprocess实现冻结资源+五层实现的独立候选组装（清除生产路径旧草稿、所有权与source→target映射、手改保护）。仅模块接口和私有隔离测试，不执行源代码/不写正式游戏；shader_profile空闲。下一步架构验收后顺序生成实际模块，组装新候选并做整工程及跨层业务验证，不恢复旧3476队列。

2026-10-27 接续实际结果：GlobalArchitecture03 单次全局分析已输出47模块/1484目标类型/27链，原始9,261,012B模型payload保留。16MiB原有worker输出边界接收、recheck和模块架构分片已实现；首次验收严格发现3489项来源归属反向缺失，未把静态设计认作通过或业务恢复。GlobalArchitecture04已沿原payload及精确诊断修正3489项归属，GlobalArchitecture05又保留原初始化说明并补正实际类ID；不重做整套旧草稿分析。record属于可接受设计类型、null base表示无基类；实际Unity兼容仍待整工程编译。

完整模块API、串行pipeline与候选assembler已接CLI；当前48项新增/定向用例通过（含大plan/分片/精确续跑/权限阻塞/篡改/来源和meta绑定）。候选保留4个冻结原生Layout助手及meta以保护既有Prefab GUID引用；本机Unity6000.6.2f1内置uGUI2.6.0的UnityEngine.UI/TMP程序集名和SHA已实际只读核验，无安装。仍未产生新的完整模块实现或新Unity候选，编译/运行not_run；下一步是修订架构验收后连续实现全部模块，而非以工具小包停工。

2026-10-27 当前架构出口：GlobalArchitecture05 `architecture_designed`，47模块/1484类型/1831来源单元/27链；architecture SHA `89343c3edb3ccb39cd0fe5495096b38972288e6a8c2609b0733ba91e4f6fe25e`，validation SHA `179e7e41ce44f437f90e030080aa3bccebc271c2e36c1abee987fd05e6b721c7`。117个JSON路径及230个Prefab/Scene路径均属冻结清单，routing-check.json保留原生未运行边界。第一条链严格要求JSON，独立接触/Prefab调参链不强造不存在的JSON；实际运行仍执行正式JSON约定。

NativeProject01已通过真实CLI准备47模块串行计划（当前0实现），最大模块230类，小于256选择边界。开始完整模块实现前补齐原脚本注册→组件→原生资源/只读Editor读回的精确上下文；已有120MB editor-readback是原生身份子集，不能把源mapping缺localID外推为全部缺失，也不能冒称已给新类完成序列化。之后持续单CLI全模块生成、候选组装、必要整工程和跨层业务验证；架构完成不代表实现/编译/运行完成。

2026-10-27 实际实现已启动：NativeProject01的单CLI串行supervisor正在Session模块（21目标类）；完整47模块自动接续，pending不等于完成。模块输入约17.8MB/220份只读context，含完整架构分片、所需源码/JSON、真实资源身份及冻结Unity包版本；不发源UUID runtime lookup，不装额外包。原生身份helper在真实Orders只读检查中核实95/95目标Prefab路径/GUID，但没有精确component localID，明确待Editor接线。新candidate manifest已与现有candidate_snapshot.snapshot/verify标准接通；48项当前定向测试通过，非整工程编译/运行证明。

## 历史：2026-10-26 全量逐文件Codex后处理（已被上方替代）

事件 `monkey-v06-full-project-postprocess-20261026-01`；本聊天已原生回读总监 turn `01a178b1-2519-7ef3-a8e7-39951dffe754` / human `01a178b1-2548-7db3-b13e-818e583fb769`。用户明确要求全量资源/代码项目恢复，Codex也必须实际批量处理全量，可以有错误，不能以少量测试结束。执行权威计划 §5B 最新全文。先前两方法调用只证明封装可用；5A、3a0391a、ca0350a及07证据保留，**全量后处理未完成，v0.6继续开发/实际跑全队列**。

以manifest自动发现完整6,445 C#（新初稿5,522、旧具名草稿914、原生辅助9）、19,571索引方法、47,384函数映射；按源/模块/依赖分批，实际分析/修订每个文件并记录具体保留或修改理由、未决项。项目prepare/run/status/resume、失败隔离/精确session、多批连续串行；旧全任务一次session/resume及一次模块调用上限被覆盖，单批预算/有限重试仍保护空转。继承模型/上下文/登录配置，不降级；额度/认证/权限真实阻塞保留pending并如实报，不换通道。独立完整AI修订工程含资源、Scene/Prefab、JSON和源映射，07/冻结资源/正式游戏/GREA/beaver只读，无发布/推送/全局安装。

主体为真实全量处理；复用61检查/资源证据，不重跑旧原生套件。所有就绪批连续执行，不能以调度器或新小样完成而停工；版本或严重问题反馈，不等逐批ACK。

2026-10-27 §5C执行提效（未启用、已封存）：事件`monkey-v06-fullqueue-efficiency-20261027-01`的人类turn `01a17b04-b0ea-75d1-bcff-0eff1266fcf3`已核验；随后被上方整体架构人类要求覆盖。机械预处理/源分析复用/简化逐文件任务WIP仅完成定向模块检查，未用于真实批次；副本和patch保留，不继续开发或部署。保留无新增信号不做重复人工审计/旧测试的效率原则，不能继续旧流水线。

2026-10-27 全量检查点2960（非整版完成）：前40批2960/6445实际审阅集成，2899 partial /49 processed /12 unchanged，2323文件实际改动，17754项必需源函数映射逐文件覆盖；3份额外未知ID的元数据问题仍保留且不计覆盖。第41批68文件继续执行。增量内容复核06仅新增429文件，源/当前hash全匹配，无55%以下收缩或新增映射空方法；额外未映射空方法检查04同429文件亦无新信号。2份异常计数告警逐一回读精确原文，对应NarrativeItem的onRender/onSkip/onAnimate与ActivityEntranceBase.onEnter共4个原本显式抛错钩子，当前保留原消息，generic Exception改为NotImplementedException；未用异常替换既有业务正文，CLR异常类型语义仍未验证，文件保持partial。回执`ContentAudit06/accepted-code-audit.json`、`manual-signal-review.json`、`checkpoint-metrics.json`与`UnmappedEmptyAudit04/signals.json`；原告警不抹除。2960份摘要无空摘要、5组精确重复文本最多7份，文本信号不能证明语义等价或替代源码核验。仅静态内容/身份/覆盖检查，非整版编译、Player或运行证明；全部就绪批继续，不停在本检查点。

2026-10-27 字段映射边界核对：第41批观测大小写差异后复用renderer实例，授权样本Function_b6facd65dd为owner_unresolved、无classId/ownerBindingId及对应PascalCase字段声明，不据此认定renderer造成同一字段错名。合成AST确认独立render_field只见targetName，跨render_method须显式_draftMember身份注解；无映射维持源名和诊断。未增加全局大小写猜测或修改renderer逻辑，仅补文档与映射/未映射边界用例，父复跑34项、py_compile及diff检查通过；不是已修复所有动态字段或全工程编译的声明，实际串行队列继续。

2026-10-27 命令记录增量检查02：仅前轮25批之外已完成26–43批的18份尝试归档，614条去重命令项；560段Python AST可解析，13个敏感compile命中均re.compile，os仅观测创建允许的__Reviews目录，random用于自有4096组低/高字乘法公式核对，不执行原JS/WASM/DLL或C#候选。51条引用/转义文本shell解析缺口及3条脱敏Python解析缺口保留，不重构脱敏内容；4条pwd复合命令含可解析Python静态变换。所见无原程序、引擎、联网或第二Codex启动，限定证据`EventAudit02/command-launch-signals.json`、`python-static-signals.json`、`manual-review.json`，不能作为每个操作的绝对证明。实际3221/6445，第44批96文件继续；未重跑旧引擎/资源或原生套件。


2026-10-27 生成器控制流补修：新鲜discard局部声明自带block，避免无花括号if/else、while、for中CS1023；保留真实`_`赋值及Sequence求值顺序。renderer模块23项通过，独立.NET8反例先用022fc8c复现3处CS1023，再以修复版编译零警告/错误并得到`embedded=7,7`；回执`.private/v060-full-postprocess-20261026/RendererEmbeddedBehavior02/receipt.json`。仅合成代码执行，不是游戏全量编译。修复影响未来生成，冻结07与实际串行队列不改；检查点1294/6445，第20批实际审阅中，全量未完成。

2026-10-27 增量内容复核03：前20批1400/6445实际审阅集成，第21批90文件继续执行。新增321文件（前两轮已核1079之外）源/当前哈希全部匹配、无55%以下体积收缩；4个新增空/null-only方法信号逐一回读精确原文均为空函数。另1处新增NotSupportedException经差异/原文复核是原空壳XHR类新增部分方法后的未知事件分支，未用异常替换既有正文；任意事件名/this绑定/send及WeakMap等仍明确未恢复、originalLogicPreserved=false。回执`ContentAudit03/accepted-code-audit.json`与`manual-signal-review.json`保留原信号及人工判断；不是全语义/编译/运行证明，不外推后续未审文件。

2026-10-27 生成器绑定命名根因补修：已观测奖励动画`$`/`_`碰撞后，renderer仅依据明确bindingId为冲突局部分配稳定无碰撞名称，参数/局部/闭包/循环/catch/嵌套函数共用映射，公开成员和已有显式目标保持。无binding/目标冲突/预算截断具体诊断；截断不自动改名。根命名函数按可证公开签名保护，避免把递归引用改成不存在局部函数。31项renderer检查通过；独立.NET8用例03旧版CS0100、修复版零错误并得到`distinct=27,72`，用例04旧版虽编译成功但递归调用RuntimeBinderException，修复版得`recursive=15,0`。证据`RendererBindingBehavior03/receipt.json`与`RendererRecursiveBindingBehavior04/receipt.json`；仅合成代码执行，未来生成生效，冻结07/真实批处理候选不重导不改。全量实际进度1490/6445，第22批继续；无整版完成/编译或运行声明。

2026-10-27 字面量除法根因及静态复核补充：renderer只在两端均普通int32数字Literal且无BigInt/正则标记的`/`中使用double；变量/动态/布尔/字符串/越界/其他运算符保持。32项模块检查通过；独立.NET8用例05复现旧版1/60=0与零除CS0020，修复后1/60=0.016666666666666666、0/0=NaN、1/0=正无穷、8/4=2，编译零警告/错误。证据`RendererLiteralDivisionBehavior05/receipt.json`，仅合成代码，不改冻结候选。另对1779份已接受代码补查未映射新增空方法29信号：9份精确原版空函数、20份新增discard辅助方法，回执`UnmappedEmptyAudit01/manual-source-review.json`；不外推语义。前25批28份尝试归档912个命令项静态记录复核，886段Python AST可解析，74个compile命中均re.compile；8份脱敏导致的解析缺口保留、3份原命令语法错误exit1、1份组合heredoc，不重建脱敏内容。所见无原JS/WASM/DLL/编译器/引擎/网络启动，限定日志信号证据`EventAudit01/manual-review.json`，不作为所有操作的绝对证明。全量实际1870/6445，第27批继续，全版未完成。

2026-10-27 全量检查点1924（非整版完成）：前27批1924/6445实际审阅集成，1884 partial /32 processed /8 unchanged，1476文件实际改动，14847项必需源函数映射逐文件覆盖。第28批19文件（含大型配置模块集合）继续。增量内容复核04仅新增524文件：源/当前hash全匹配、无55%以下收缩、占位异常增加或新增映射空方法信号；`ContentAudit04/accepted-code-audit.json`及`checkpoint-metrics.json`留存。另前1779之外新增145文件发现1个未映射新增空方法信号：原prototype.OnUpdate空回调被转为具名StateDraft.OnUpdate，精确原文确认仍为空，非新业务占位；`UnmappedEmptyAudit02/signals.json`和`manual-source-review.json`。上一条本地记录将信号数提前写为0，现按实际结果更正。前轮已知XHR未知事件分支等partial限制保留，不因本轮无新信号消除。仅静态内容/身份/覆盖检查，不是全语义、整版编译、Player或运行证明。

2026-10-27 全量检查点2531（非整版完成）：前35批2531/6445实际审阅集成，2471 partial /49 processed /11 unchanged，1975文件改动，16779必需源函数映射覆盖；3文件额外review-ID限制保留，不计未知ID为已验证覆盖。第36批90文件继续。内容复核05新增607文件hash匹配，无55%以下收缩/新增映射空方法；新增未映射空方法信号亦0。3处异常计数增加经精确原文复核：配置10个delete占位变为字典删除+未知接收者NotSupported分支、movieClip属性删除同类限制、原版明确抛Error的待覆写钩子改为NotImplementedException（异常类型近似仍非等价证明）。均非把原业务正文新改成占位，全部originalLogicPreserved=false/partial保留；回执`ContentAudit05/{accepted-code-audit,manual-signal-review,checkpoint-metrics}.json`和`UnmappedEmptyAudit03/signals.json`。不外推全语义/整版编译/运行/资源实际加载。

2026-10-27 生成器布尔常量窄补修：仅普通数字Literal 0/1的Unary !分别转true/false；其他数字/类型/标记/运算符维持原输出及诊断，不猜动态truthiness。33项renderer检查通过；独立.NET8用例06先复现旧版方法/字段CS0023三处，再以修复版零警告/错误编译并运行得`not=True,False;field=True`。`RendererBooleanLiteralBehavior06/receipt.json`保存源码与日志hash，仅合成代码。未来生成生效，冻结07和实际串行候选不改、不重导；全量继续。

## 全量执行入口（本轮进行中）

首轮全manifest实际为 **6,445份C# / 40,574,177字节 / 86批**：5,522份新初稿、914份旧具名草稿（原JS模块SHA全部精确匹配）、9份原生工程辅助代码；47,384函数/19,571索引方法和3,706字段映射另作分母。各弱标签均未过滤，唯一725,535字节文件保持完整。`ProjectRun01` 以0模型调用/0处理状态升级旧未运行5522清单，ScopeHistory保留原plan/request/state；完整资源工程复用原已拷贝清单，未重导资源。

实际队列 `.private/v060-full-postprocess-20261026/ProjectRun01/`；`code-project-run` 连续处理全部就绪批，`code-project-status`给已处理/partial/失败/阻塞/未处理真实分母，`code-project-resume`恢复；不是一个批次结束后停工。低层支持每batch文件结果/精确session/只读源context，父按完整函数ID与声明/marker守卫串行集成。首批104文件已实际读取/修订，但旧1200s/无事件180s预算未等到完整逐文件JSON即中断，已进入第二次尝试；补合作式pause与停机预算调整，默认后续3600s/900s，累计耗时/次数不重置。监督器在既有子进程自然保存检查点后安全交接。有限重试2不是项目总量上限，实际完成数以状态文件为准；**全量后处理仍未完成**。实现/用法见[项目批处理](CODEX-PROJECT-POSTPROCESS.md)；旧局部测试沿用，只做新边界必要检查，主体为实际执行。

新进程/项目控制集成检查27项通过（7项目场景+20进程模块）；86批真实源context预算预检全部通过，最大单context 847,073字节，回执在 `ProjectRun01/context-budget-preflight.json`。这些是继续全量运行的保障，不计为文件已处理。

2026-10-27 首批真实结果：104/6445已处理，101 partial、3 processed，全部104有不同具体审核摘要；首轮21项因字段/同源嵌套函数ID被过窄校验误拒绝，经源SHA+完整包含字节区间校正后从已保存真实结果重检接受，未重跑模型。完整函数覆盖仍必需，越界/异源ID仍拒绝；新增结果hash防篡改及无模型recheck，10项项目定向检查通过。第二批116文件合作式暂停检查点已确认子进程退出，随后恢复同一session继续。完整资源/正式游戏边界不变，全量队列未完成。

2026-10-27 后续推进：当前实际219/6445已审阅集成，第二批唯一TimSort已完整审阅但旧验证仍以语义确认布尔和额外ID拒绝。修正“审阅完成≠等价证明”：False+具体差异保留原值记partial；额外未知ID仅作为metadata未决项保留、不加入已验证覆盖，必要函数缺失/blocked/代码hash或边界错误仍不接受。准备交接后从保存结果重检，不重跑排序模块。新增fixed JSON ledger通道减少最终回复重复ID，原数组协议兼容；artifact路径/引用/结构错误另作批级阻断，逐行问题继续隔离。当前第三批旧inline仍真实执行，已请求本次尝试自然结束再升级监督器，后续实际采用ledger后才记入运行证据。父15项与低层26项相关检查通过；不是全量完成声明。

2026-10-27 安全交接完成：前三批271/6445实际审阅并集成，265 partial / 4 processed / 2 unchanged，83批待实际执行。TimSort与第三批已从真实完成记录重检，False原值/具体差异保留；未启动的新尝试暂停不能遮蔽上一份完整审核，recheck已补倒序实际结果回放并通过专测（父16项、低层26项）；不新增模型调用。当前新监督器将从第4批采用fixed JSON ledger，旧inline已接受记录不重跑。全量仍进行中，源码语义/编译/完整游戏/发布未因此完成。

2026-10-27 Ledger兼容纠正：第4批Box2D单文件（207映射函数、1515源标记）实际完成审核，归档JSON采用`{"fileResults":[...]}`包装，现与直接数组同等支持；固定路径、原始SHA/字节数、逐文件必需ID和最终代码哈希守卫继续执行。原始225,716字节审核归档保持不变，重检复用真实记录，不增加模型调用。累计272/6445已审阅（266 partial /4 processed /2 unchanged），82批待执行；该模块originalLogicPreserved=false及具体限制保留，全量未完成。父/worker定向回归合计45项。

2026-10-27 审核损坏行边界：单行必需字段/类型不合法时一律blocked，不再用partial占位，避免无函数ID辅助文件被误计。合法已分析且有具体限制的partial保持；新增反例与worker 28项通过，父18项（含导入plan夹具共26）通过。只读回查已接受的13份无函数ID记录，未发现该格式损坏情形。实际队列当前批自然结束后加载本修复，不中断模型。

2026-10-27 全量运行检查点（非整版完成）：前9批472/6445实际审阅并集成，5982必需源函数映射覆盖、379文件实际改动；状态{'partial': 461, 'processed': 9, 'unchanged': 2}。第5–9批均在首次实际调用后通过逐文件覆盖/原代码与资源身份/最终工作区哈希/写入边界检查；固定ledger两种JSON格式已真实通过，无格式返工重跑。第7批Spine移位/图集换行/浮点通道、第8批真实下划线变量覆盖、第9批Zlib跳转/Widget递归/物理步长等已形成具体修订与未决项。当前第10批120文件执行中，剩余队列连续串行；后续动态进度以`monkey code-project-status --run .private/v060-full-postprocess-20261026/ProjectRun01`与该目录state/progress为准，不把本检查点当最终数。原07/完整资源/正式游戏/GREA/beaver不改，无编译/Player/全语义等价/发布宣称。

2026-10-27 内容复核与连续第10批：完整接受592/6445，必需函数映射6929；第11批已自动开始。新增`.private/v060-full-postprocess-20261026/ContentAudit01/`只读审计前472份实际接受代码：全部源/当前哈希匹配，无占位异常计数增加；唯一55%以下体积收缩经原文/差异确认是数组/List原生操作替换冗余生成器表达式，方法保留，未证全语义。新增空/null-only方法13份信号逐一回读精确源字节，13/13原版函数体为空，无此项业务正文删除；回执保留逐文件哈希、源范围及判断。后续增量代码仍须同等复核，不把该472快照外推到未处理代码。当前无额度/认证/权限阻塞，监督器持续串行，未完成整版。

2026-10-27 已观测生成器根因闭环：复用renderer模块修复精确源空体误抛异常与生成丢弃赋值覆盖真实`_`变量；仅有界AST证明空的体发空结果，缺失/未知/超预算保留诊断；临时名避开当前/嵌套AST及参数/capture元数据，原业务赋值保留。受影响renderer 22项通过，独立.NET8合成C#两方法0错误0警告，实际输出`underscore=6;empty=null`，证据`.private/v060-full-postprocess-20261026/RendererBehavior01/`。producer签名本来包含renderer源码SHA，未来导出缓存会失效；未重导/改写07或当前AI队列，不重跑已有审阅/旧原生套件。第11批真实调用持续，整版全量后处理仍未完成，无正式游戏/引擎/原始脚本执行或发布。

2026-10-27 千份代码连续检查点：前14批1079/6445实际审阅并集成，10146必需函数映射、800文件实际改动，状态{'partial': 1049, 'processed': 26, 'unchanged': 4}。第15批连续执行中，无额度/认证/权限阻塞；全量仍未完成。新增ContentAudit02只查未覆盖的607份接受代码，全部源/当前哈希匹配、无新增占位异常计数/显著体积收缩；58份新空/null-only方法信号回读精确源，58/58原版确为空。结合Audit01已覆盖全部1079接受文件，71份空体信号均有原文依据，首份数组/List压缩已手工核对；这是有界内容信号复核，不是全语义等价或完整编译/运行验收。原07与资源身份保持，动态实时数继续用code-project-status/state。

## 当前执行：v0.6.0 / 全量 C# 初稿与完整候选组装（2026-10-26）

**5A/5B继续开发（最新授权）**：原生已核验总监human `01a17878-8321-74c3-bea3-bac188c57398`“按方案执行”与`01a1787c-c602-77e0-93c1-6c610ebaaeac`“允许monkey导出C#后启动codex cli进行代码处理”。保留d3f22ab/ed8323d/FullDraftCandidate03，先通用集合参数、符号声明-引用、闭包归属整改，再确定性全量导出→可选既有Codex CLI→独立AI修订代码候选。基础导出不依赖AI/登录/编译；一组有界肥鹅模块将实际调用一次，原候选/manifest/资源/正式游戏不改。单CLI串行/精确session/预算/差异与用量回执，不递归、不扩至其他AI服务/无关资料。5A/5B现已完成本地下述实际验证；未知业务与动态语义继续保留，正式版本裁定不由旧候选反推。依据权威计划5A/5B，完成或严重问题成组回报。

**5A/5B本地组已实际验证**：见[本组验收](validation/2026-10-26-v060-draft-quality-codex.md)。三源19,571索引方法/47,384函数映射不减，23,535辅助函数内嵌，物理方法23,849、C#文件5,522；3,706字段/3,528声明和全部资源身份不变。最终07候选94,127文件、manifest `7febffc663f08e035befaf98b6307308d66d6e79a5823e4789a4a631945d6c7e`，beaver独立全清单hash通过。11样例检查、46 draft +9 postprocess +6 package定向测试通过；暖阶段禁parser/render复用5,632文件。可选公开Codex CLI已实际一次有界配方模块调用，61.405秒、只改2方法、其余字节/原候选不变，真实patch与精确session保存；修订为partial，4项getter/动态/集合语义限制保留。两个实际修订方法体在限定.NET8夹具编译及受限行为检查通过，不外推完整游戏/原UI/Player/视觉。下方03基线证据继续冻结，代码文件下降是闭包去重，新增未知成员诊断不冒充清零。无推送/Release/全局安装/正式游戏写入。

**本组源码/分发已固定**：源码 `3a0391a`，分发04的184产品文件与源码/wheel/sdist/隔离安装一致；只测新增postprocess三条安装CLI，无额外模型或旧整套重跑。wheel `bc89d6468fb9434c9eba1c96ba9cb624bf61433462b500212f81d642365c4cfd`；总回执 `.private/v060-draft-quality-20261026/delivery.json` SHA `394d28bbb8637346836fd210d99b63aee8ea278fc409bc5b28be40205246af1b`。本轮04–06中间输出留清单后清理10.42GB逻辑体积，保留07/03/冻结资源。日常0.4、发布状态和旧未验项不变。本版按已声明初稿及可选有界修订能力交付，AI结果partial不标作生产工程完成。

**最新全量裁定（覆盖下方历史门槛）**：本聊天已原生核验总监turn `01a17807-bfde-7210-ac1a-06412c7f108f` / human `01a17807-bffc-72c3-af7b-6551a18f424f`：“monkey 是工具，不是 agent，它的目标应该是全量导出 C#，哪怕存在一些语法问题也是可以接受的”。执行已重写权威计划：默认完整输入业务/框架/SDK方法批量输出实际C#初稿；未知类型、API/语法/依赖不阻止导出，局部失败其余继续。严格16方法/profile/显式类型只作增强；全量初稿/语法诊断/编译/行为分别记录。包级convert统一资源/Scene/Prefab/JSON/代码，资源native清单按已有hash新封存，无需重跑引擎。

**当前本地完整初稿主链已固定**：公开包级 `convert` 默认不需要类型合同，完整肥鹅3份JS→19,571/19,571索引方法 +27,813辅助函数，实际24,153份C#初稿；1,157源类与辅助容器分开计数。3,706字段记录→3,528独立声明、1,440初始化、2,266运行时写入，方法内写入不被提升到类头，跨字段初始化保留源顺序。统一候选112,758文件/3,484,952,335字节含2 Scene/1696 Prefab、JSON和原键/身份映射；beaver只读snapshot+逐文件hash通过。完整源/方法/字段位置和输出映射均核验，0未导出索引方法。近似/未支持局部及556,272诊断如实保留，1254函数有局部未支持/无可转写语句等标记，绝不外推全部方法可运行。101份完整详情分片最大4,363,623字节，最大主索引32,699,305字节；旧450MB重复报告已替换。暖阶段禁用parser/render，实际复用24,263文件/328,742,065字节，原候选不变。资源按原nativeFiles哈希新封存，未重新启动Editor。完整记录见[全量主链验收](validation/2026-10-26-v060-full-source-mainflow.md)。 源码 `d3f22ab`；分发03的182产品文件与冻结提交/wheel/sdist/隔离安装逐字节一致，新入口4条实际调用通过。wheel SHA `59335598b8153988dfc9eafc5d5b733ef293a29bb32094ab005cd570d0d75d02`；sdist SHA `23231fda81199cb16b8e891378c71ff89f2e4a5adf9dbb770656f73043aaa5de`。总回执 `.private/v060-package-mainflow-20261026/delivery.json`，未重复旧引擎/安装整套验收。

**方向补正后继续实现**：事件 `monkey-v06-direction-mainflow-20261026-01`，按 Manager/reviews/20261026-grea-responsibility-review/MONKEY-BEAVER-DIRECTION.md 补包级主链。此前16方法/8WASM/6CUA与分发02为已验模块成果，不能代表整版“一键可开发候选”闭合；不重复验证。当前新增公开 `convert` 接 typed模块与冻结资源候选组装，通用AST/已有资料类型提取、同一配置/资源/Scene-Prefab映射及beaver消费合同。只验证新增主链，不恢复全部16k/原UI/未知动态语义，不动36schema，不新增发布或平台。


人类授权已原生核验：turn `01a17751-6597-7d01-ae5b-13c670fb3d3c` / human `01a17751-65b2-76c2-bf0d-df22da2b6204`。执行 [总监完整计划](/Users/wangmeng/Documents/Manager/decisions/20261026-grea-monkey-beaver/MONKEY-V06-CSHARP-PLAN.md)，原06/07及后续C#相关能力合入一版 `0.6.0.dev1`；不是只做盘点。分支 `codex/v0.6-csharp-recovery`，基线 `36e9d6d`。v0.5源码71c177d/受限制品冻结、原全范围未完保留，日常安装0.4不动。

| 工作组 | 当前完整初稿主链与既有增强 | 当前状态 |
|---|---|---|
| C1 来源/符号 | 3源1,157类/19,571索引方法，全部源跨度/hash及目标文件核验 | 本地样本通过；SDK/业务标签仅弱线索，未过滤；非全平台/全引擎声明 |
| C2 类型初稿 | 默认dynamic与逐位置近似诊断；通用可证明类型提取、具名fillable合同仅作增强 | 未知类型不挡默认导出；严格16方法增强的既有类型证据保留 |
| C3 方法体批量转写 | 47,384函数记录实际C#，控制流/字段写/调用/集合/回调尽力保留；局部未知保留源定位 | 0整函数AST/renderer失败回退；1,254函数存在局部未支持或无可转写语句，不称语义全还原 |
| C4 模块及依赖 | namespace、稳定分类候选路径、原函数/字段/依赖与输出映射；调用环作为诊断 | 24,153文件包括辅助函数容器，不等于24,153原业务类 |
| C5 Unity适配 | 常见cc API近似；原16方法/9方法原生链/6次CUA保持冻结证据 | 全量草稿未绑定/未编译；旧有限探针不外推全游戏 |
| C6 资源/配置关联 | 88,493资源基线完整复用，2Scene/1696Prefab与JSON/逻辑键/GUID/localID同一清单 | 原资产hash未变；36schema精确写回限制、缺原Label/未知语义保留 |
| C7 实际源码候选 | 默认convert统一资源和SourceRecovery/CSharp实际初稿，类型合同可选；freeze-resource-candidate支持旧native清单补封存 | 自有新候选已核；编译排除安排不冒充已编译工程 |
| C8 复用与所有权 | 完整生成签名/源hash/所有文件hash；24,263文件实际暖阶段复用；dirty/manual拒绝；大工程500k/8GiB有界 | 21项新增主链定向检查通过；人工工程采用继续归beaver |
| C9 接续诊断 | 101详情分片、全部源位置/字段/方法映射、分类不确定性、局部缺口；beaver独立只读全清单通过 | 当前本地主链出口；Mono真实样本、WASM状态方法与完整游戏/原UI/Player/视觉仍未验 |


**首个本地限定候选已交付，合并大版本继续开发**：源码 `8a536d31cab8722c392e1003761002ea50897419`，50项定向测试无skip通过，完整[验收记录](validation/2026-10-26-v060-csharp-modules.md)。该候选贯通已声明语义/profile，不能据此认定原C1–C9大版本完成；16,372项是未选，不能统称不支持或无源。证据 `.private/v060-csharp-20261026/delivery.json`；日常0.4不动。

续推按 [交付审阅](/Users/wangmeng/Documents/Manager/decisions/20261026-grea-monkey-beaver/MONKEY-V06-DELIVERY-REVIEW.md)、事件`monkey-v06-delivery-gap-correction-20261026-01`继续：模块选择/类型依赖预检与裁剪发射、已存在僵尸segment/map的同源核验和有据body恢复、Unity实际按钮可操作有限流程。僵尸已有完整segment和selected-method-map-07，先前仅核压缩来源的结论不能外推为全部材料缺失。


**上一组模块成果已验，整版包级主链未闭合，按上方继续**：三项审阅差额均有实际出口，见[续推验收](validation/2026-10-26-v060-continuation.md)。通用 `code-select` 支持有界入口/类型依赖/实际lowering与裁剪发射；合并4模块16方法编译通过（新4数学方法+原12字节保持），16,368未选择不标不可恢复。Unity独立窗口6次CUA系统指针流程/JSON/事件/销毁解绑/保存重开通过、exit0/reaped。僵尸两压缩源→精确segment/map/body已核，8纯i64方法生成片段并编译/行为通过；13波次/触发方法保留精确布局/调用缺口，caller-map关联假设不冒充独立证明。26不同定向用例通过，首50测试/旧自动原生链沿用。源码 `5a2ce31c517e1ada130ecaddf651903290859d86`；隔离分发02的178产品文件与源码/wheel/sdist/安装副本完全一致，24CLI烟测与4条真实安装版命令通过。首候选包hash未变。总回执 `.private/v060-csharp-continuation-20261026/delivery.json` SHA `6af5eca03c06d4a964a6ba29450e97375a9f442487c53d91602ba5bbeef8a873`。C1–C9本地候选和交接按声明子集收口，完整游戏、原UI/生命周期、Player/视觉、无真实Mono/其他平台未验；正式总监裁定另列。

Unity Mono/IL2CPP-WASM来源独立模块按不同证据等级推进，缺真实Mono用自有合法夹具验证接口，不外推真实游戏；原方法/映射/元数据不互相冒充。泛新引擎/CDN能力后移，不再另排C# v0.7出口。正式游戏/账号/服务/GREA/beaver不写，无推送/Release/全局安装。模块登记见 [TEAM-STATE](TEAM-STATE.md)。持续实现整版，不逐包报告或等待ACK。

## 历史基线：v0.5 受限本地候选；原范围精确来源阻塞（2026-10-26）

本地开发版本 **0.5.0.dev1**；已安装仍为 **0.4.0**，无推送/Release/全局安装。

总监事件 `monkey-v05-local-restricted-delivery-20261026-01` 已按 [本地出口裁定](/Users/wangmeng/Documents/Manager/decisions/20261026-grea-monkey-beaver/MONKEY-V05-LOCAL-EXIT.md) 接受已声明子集：`acceptedDelivery=local_declared_subset`；原全范围 `versionComplete=false`、`originalScopeComplete=false` 保留。沿用源码 `71c177d` 和原 0.5.0.dev1 制品，不因状态文字重打包。

按续推事件 `monkey-v05-existing-plan-resume-20261026-01` 完成可独立推进的资源及使用基础，未把子集通过报成整版完成。正式肥鹅/GREA/beaver 只读，向僵尸保持暂停；本轮仅使用 monkey 自有资源探针和已冻结来源。

| 工作包 | 已验证 | 当前出口 |
|---|---|---|
| 05-A 大工程预算与阶段复用 | 肥鹅 Unity 75,710 文件 / 2,834,639,181 字节，Creator 74,694 / 2,789,086,480；僵尸 164,599 / 3,267,184,074；暖阶段禁止原包读/解码/worker 时实际复用，漂移/篡改拒绝 | 完成既定本地子集，复用 [预算验收](validation/2026-10-26-v050-budget-reuse-handoff.md)，未重导全量 |
| 05-B adopt 移交 | 冻结采用实现已由 beaver 接收并完成其本地 0.1.0 验收；只读复核固定回执/wheel | 采用归 beaver；旧 monkey CLI 明确 deprecated compatibility，消费者切换/退休另列，不重复采用测试 |
| 05-C 原生资源与引用 | 第一组 72 头引用、2 动画长名、21 Tiled、3 紧密 Sprite 几何/UV；新增 Spine 二进制/JSON 各 1 份原生引用/页图/时间/姿态保存重开；精确 Shader 的材质保存重导、编译/Metal 像素通过 | **仍阻断**：36 正文无可信精确 schema，字段写回不放行。8 非标准 Spine、其他 37 Effect、Unity Spine runtime 等继续隔离；[新验收](validation/2026-10-26-v050-operations-resources.md) |
| 05-D 诊断与使用基础 | acquire-resources 的有限重试/已结束部分层续接；diagnose 的源身份/目标映射/动作；doctor、space-preview 无安装/删除；公开 CLI 与相关回归通过 | macOS 隔离 wheel/sdist 159 产品文件逐字节一致、13 CLI 烟测通过；Linux/Windows CI 矩阵已写但未远端运行，不能声称跨平台已通过 |

**实际阻断**：19 Image、10 Text、3 TMP、4 自定义组件的精确 Unity `2021.3.30f1` / platform `20` / scriptId / typeHash 正文 schema 或相应可信原程序集未取得。逐对象原 hash、类型和动作已写 `.private/v050-continuation-20261026/source-schema-blockers.json`。独立参考与目标 GUID/localId/hash 写回门继续有效；不按通用类名套近似布局，不补默认值。已批准的独立工作已继续做到分发收口，v0.5 当前不能宣称完整验收。

执行方式按 [模块登记](TEAM-STATE.md)；仅一个 Shader 完整模块开发者，公共接口/窗口/集成由主开发负责。Shader 已交付，受限本地候选已按裁定收口；当前等待具体可信输入、获准的新恢复方法或后续版本指令，不循环尝试或自动启动 v0.6。裁定无需确认/重复报告。范围和后续版本见 [ENGINE-ROADMAP](ENGINE-ROADMAP.md)，操作见 [V0.5-OPERATIONS](V0.5-OPERATIONS.md)。

### 继续恢复所需输入

- 逐对象取 `.private/v050-continuation-20261026/source-schema-blockers.json` 的 Unity版本 / platform / scriptId / typeHash / 原对象SHA；提供与其精确匹配的可信 schema 或原程序集及匹配依据。
- 字段写回还需独立可信的原字段值对照，以及目标 GUID/localId/hash；程序集/解析成功本身不放行写回。
- 不同版本同事包、Unity6/同名类或近似树不能替代；36 正文、8 非标准 Spine、Unity Spine runtime、其他37 Effect和未运行CI继续按真实状态保留。无新输入不重试、不重导、不构建/启动引擎。

## 本轮完成：资源与引用第一组（2026-10-26）

续推已原生核验：总监 turn `01a176aa-5d5a-7d10-9a1b-d67ebc7052ea` / human `01a176aa-5d78-7421-a5db-d4c06b216750`，事件 `monkey-resource-reference-continuation-20261026-01`。本组复用冻结来源和 beaver 已验结果，没有重跑 601 容器/全量导出/采用矩阵。原生段仅 monkey 自有副本，所有自有 Unity/Creator child 已退出；正式肥鹅/GREA/beaver/僵尸只读。

- 36 失败对象的基础头恢复 72 处 PPtr（69 非空、3 空引用），与原字节独立核对；1567 成功对象字段及全部原对象 hash 不变。失败正文与字段写回继续严格拒绝，不把引用保留称正文恢复。
- 肥鹅 776 控制器 / 1552 派生片段只改两个超长文件名；真实路径 Unity 6 创建/独立重开、GUID/曲线/状态引用通过。统一分配器和命名预览重放均包含派生片段。
- 肥鹅 1053 Tiled 中 21 个超过默认 4096 顶点，最大 59892。局部 2106 KiB / 59904 容量保留原几何/UV/边框；21 Sprite / 13 Frame 的 Creator 3.8.8 原生保存重开、分配/拓扑/UUID 复核零诊断。候选元数据/设置/说明记录该宏，**资源采用不会自动带入项目设置**。
- 僵尸原叶 Prefab 的 3 紧密 Sprite / 271 顶点 / 336 三角形和 UV 原生读回通过；1 Prefab / 16 字段 / 3 Sprite 引用保存重载及原 GUID 通过。仅精确版本/平面浮点/无旋转等子集，未知布局仍阻断。
- 定向 72 测试与 JS 语法通过。Spine/Shader 只核已有清单与 48 份代表文件 hash：1768 标准 3.8.99、8 非标准版本，38 Effect / 214 源文件；播放/目标编译仍未闭合。beaver 0.1.0 本地验收回执/wheel 身份已复核，未重复测试，不退休旧兼容入口。

公开证据 [资源引用验收](validation/2026-10-26-resource-reference-correctness.md)，完整私有回执 `.private/v050-resources-20261026/`。下一组继续精确 schema/字段、Spine 代表播放和 Shader profile；v0.5 仍未完成，安装 v0.4.0 不动。

## 本轮完成：同事交接的通用证据能力实际并入（2026-10-26）

人类授权已原生核验：总监turn `01a17684-3487-7890-a76a-33bc95bf9f91` / human `01a17684-35f6-7ed2-a252-2f7f73d2898a`；事件 `monkey-colleague-recovery-intake-20261026-01`。完整读取指定3脚本与对应manifest/方法映射格式，独立实现并接入现有CLI/inspection，未复制游戏实现：`query-methods`流式方法定位及完整SHA，`query-tables`带hash的嵌套归档/单表提取，`inspect-aliases`精确URL→内容身份与选中载荷核验；既有Unity代码证据清单增加method-map/table-manifest/alias-index及独立adapted-binary角色。

真实交接ZIP中174,526映射行/49MB流式查询通过；27,454表变体清单/59MB内层ZIP及选中表核验通过；69,463 URL映射为34,003内容身份，选中别名载荷SHA通过。3个公开开发CLI入口均实调成功；原主WASM与适配主WASM分别完整核hash，按不同内容身份保留。全套349测试通过，最终身份回执字段补充后的定向验证也通过；旧inspect/normalize签名未改变，可继续原缓存复用。

机制与边界见 [EVIDENCE-QUERIES](EVIDENCE-QUERIES.md)、[验收记录](validation/2026-10-26-colleague-evidence-intake.md)。私有证据`.private/colleague-intake-20261026/`；大包完整验收由僵尸接收者集中做，本工具只核选定成员，不重解7GB。方法体恢复仍0；不采用WebView宿主、改造WASM运行层、经济/存档政策，游戏资料不进入公开包。当前0.5.0.dev1本地开发，安装0.4.0不动，无发布/推送；本项属于05-D证据定位增量，不替代05-C剩余36对象/资源阻断或整版完成。

## 本轮补充：GREA 七项恢复工具归属已评审（2026-10-26）

按总监事件 `monkey-grea-recovery-handoff-scope-20261026-01` 核对固定清单/来源SHA，只审7项恢复侧条目。Cocos结构/模块/转换3项复用monkey现有核心或明确子集、兼容替代仍需消费者核验；APK复用现有reader但XAPK嵌套/OBB只保留参考；ELF、Laya合同、Shader探针3项当前无等价能力，冻结参考而不扩profile。共保留23份必要源/依赖/许可身份，没有复制903文件或并入新实现。compiled代表/两个拒绝、三类AST源范围、APK/XAPK与可编辑版本差异得到实际回执，6项定向测试通过；原生/Player/消费方切换未验。七项均不归beaver，旧实现仍由GREA在替代/消费核验后退休。

详情 [归属评审](GREA-RECOVERY-HANDOFF.md) 与 [机器清单](validation/2026-10-26-grea-recovery-handoff.json)。仅修改monkey文档和自有私有证据；db253cb的beaver采用冻结归档不变，05-C/05-D保持实施主线，不将归属评审算作资源问题修复或版本完成。

## 历史：v0.5 – v0.7 统一版本规划（2026-10-26，已由本页 v0.6 合并计划覆盖）

完整范围和出口见 [ENGINE-ROADMAP](ENGINE-ROADMAP.md)。制作目录沿用 `monkey-project/2.0.0`，不因产品拆分重排目录或改资产身份。

| 版本 | monkey 的结果 | 工作包 | 状态 |
|---|---|---|---|
| v0.5.0 | 可复用、可追溯的大工程恢复候选与资源阻断治理 | 05-A 预算/复用；05-B 冻结移交；05-C 资源/引用；05-D 诊断/使用基础 | 开发中，05-A 本轮子集通过 |
| v0.6.0 | 有据恢复源方法、字段、事件和原配置 | 06-A 大 JS/有限转写；06-B 源字段/事件/组件绑定；06-C 原配置角色/类型证据与保真 JSON；06-D 原动态键映射/效果子集 | 待实施 |
| v0.7.0 | 明确 source profile 和原版远端资源闭包 | 07-A 精确 CDN 清单/缓存/续取；07-B 明确来源扩展；07-C 按恢复语义深化覆盖；07-D 候选交接验收 | 待实施 |

开发工程 DTO/配置制作、运行时框架/UI 生成、AssetBundle/Addressables/Creator Bundle 构建、微信打包、内容更新回退归 beaver；GREA 维护方法与调用路由。monkey 不引入第二套人工工程修改器。57 缺失 GUID/17,495 引用与待核“87 缺失脚本”口径不混用，528 JSON 先分类；不靠空壳清缺脚本，不承诺找回 404。原始脚本不执行，未知业务持续隔离。

## 已完成：MIT 开源（2026-10-26）

用户明确要求 monkey 开源并选定 MIT。检查 GitHub main/全部发布 tag 可达历史及 Release 附件，补齐根 LICENSE、README 和后续包许可元数据。现有 v0.4.0 tag/包保持原 SHA，Release 单独附 MIT LICENSE；正常推送后将仓库设为 public，并通过未认证访问核验。已完成：许可提交 6af9928，仓库 public；未认证 GitHub API 返回 private=false、MIT，未认证 LICENSE Release 附件下载逐字节一致。main/全部旧发布 tag 可达 867 个文件对象与 14 份原附件检查未发现私有目录、二进制游戏素材或常见凭据特征；第三方声明保留。后续 wheel 构建已验证 License-Expression: MIT 和 LICENSE，未替换既有 v0.4.0 附件/安装。回执 .private/release-v0.4.0/public-readback.json。

## 已完成：v0.4.0 正式发布与本地安装（2026-10-26）

用户本聊天直接要求提交当前版本至 GitHub、发布 v0.4.0 并安装本地。将已验 0.3.0.dev2 功能提升为 0.4.0；当前只改版本和发布说明，不扩大转换能力。执行测试、wheel/sdist 分发内容核验、精确暂存清单、main 正常快进和不可变 tag/Release；从 GitHub 下载正式附件、核对 SHA 后安装并验证唯一日常 CLI。旧版本保留回滚，原包、outputs、私有证据不上传。发布与安装已完成：源码/tag 提交 `7f602cbfa6542d124f2d36cfd3e5d35451b92a9b`，GitHub 正式 Release v0.4.0（非 prerelease）；API 与 ls-remote 回读一致。318 测试通过；wheel/sdist 140 产品文件与提交快照一致，4 份 GitHub 附件重新下载 SHA/字节一致。本地唯一 PATH 入口 ~/.local/bin/monkey → releases/0.4.0，实际版本和 140 安装文件已核验；独立目录双端合成样本导出/静态 verify 通过（convert 明确返回 partial/1，保留未知输入），未运行引擎。详情见 docs/validation/2026-10-26-v0.4.0-release.md，机器回执 .private/release-v0.4.0/delivery.json。

## 已完成：解析预算优化与向僵尸开炮复测（2026-10-26）

用户直接要求按优化方案修改并复测。开发候选 0.3.0.dev2；已安装 0.3.0.dev1 Release 保持冻结，开发显式使用 .venv/bin/python -m monkey.cli。本轮不覆盖旧 tag/包，不自动发布新版。新增类型树精确绑定的字体字节 / AssetBundle 预加载引用表流式块读取与哈希闭包；单对象及单包预算显式可配置，统计用量，所有权与复用绑定覆盖参数、读取器合同及块文件。先回归，再独立重读 601 原容器，比较原 939 预算缺口，并检验新导出的块闭包和内容；另 36 类型不匹配与 CDN 404 分开记录。原游戏 / GREA 只读，输出在 monkey 内。


本轮已完成：318 项回归通过，601 原容器 / 81,580 对象完整复测，未解析由 975 降至 36，939 个预算缺口全部恢复（933 MonoBehaviour、4 Font、2 AssetBundle）。既有 80,605 个已解析对象字段值等价，75,244 个生产资产/代码/meta 文件与旧候选逐字节相同。8 个重点大数组 38,465,356 字节通过独立原包读取对比；完整工程 25 个大字段 / 1,116 块 / 49,480,972 字节自包含。技能表现包实际内联值 5,725,048；严格结构检查与所有原始 SHA 保留。

新全量工程 `outputs/zombie-parser-optimized/UnityProject`，164,599 文件 / 3,267,184,074 字节，manifest `631e0e39edf2e6f941c2b21a4e3daed70a3d0824eef76f17ae5b9fc4af440cd2` 已最终全文件核验；887 原件及 7,595 纹理留存完整。生产资源保持 37,635；源目录条目新增 2,177，但不算新原生资产。剩余 36 个结构不匹配和既有 CDN/业务/原生缺口单列。验收 `docs/validation/2026-10-26-unity-parser-budget.md`，机器回执 `.private/zombie-parser-20261026/delivery.json`。开发候选 0.3.0.dev2 未发布，正常安装入口仍为冻结 Release 0.3.0.dev1。

## 已完成：向僵尸开炮全量导出核验、GitHub Release 与唯一安装入口（2026-10-25）

本聊天用户直接授权：使用 monkey 测试向僵尸开炮、核验导出文件内容，随后提交 GitHub 并发布 Release，安装该 Release 作为本地唯一常规调用程序。发布版本沿用 PROJECT-SPEC 的 0.3.0.dev1（GitHub prerelease）；本条覆盖此前未获新版发布/安装授权的限制。原游戏/Sources/GREA只读；私有游戏原件、outputs、缓存与完整日志不入 GitHub。先完成原输入/目标文件字节、类型、GUID/引用、命名、可解析内容与代表样本原生核验，再制作分发、精确暂存、正常推送与 tag/release 回读，最后从 Release 附件安装并验证标准入口。工具已知范围与源缺口明确写发布说明，不声明完整游戏已还原。

当前：源 Unity 2021.3.30f1 → Unity 6000.6.2f1；601 容器重新解析，887 原件 / 7,595 已取得纹理留存校验通过。425 精确 CDN 键仍 404，975 对象未解析（后续分类为 939 预算限制、36 结构读取不匹配），17,495 处未闭合引用已完整记账。发现并修复 JPEG 重编码造成的纹理像素差异，以精确水合源生成 PNG 并保留 GUID。312 项回归通过。最终候选 `outputs/zombie-release-lossless/UnityProject`，全量 Editor/Player/视觉/业务未验；叶 Prefab 原生入口因紧密图集不支持在启动前阻断。详细验收 `docs/validation/2026-10-25-zombie-release.md`，机器回执 `.private/zombie-release-20261025/`。已完成发行与本地安装：GitHub 私有仓库正常快进 main，tag / prerelease `v0.3.0.dev1` 固定产品提交 `3d0915b676e12927f532636f713bdf72659f6344`；wheel SHA256 `16f4b62c9759b36628403eb489168806439ddc4c53b709600d1adab91f37f9ab`。GitHub API、ls-remote、附件重新下载均核对一致。`~/.local/bin/monkey` 是 PATH 中唯一入口，仓库 bin/monkey 转发到同一安装版；138 产品文件与 wheel 一致，无 editable 安装。实际安装版已重新解析向僵尸代表原包，并在源码目录外完成双目标转换与静态 pass。最终候选 163,483 文件 / 3,307,505,149 字节，manifest `ab8c00b29dd8a894ca6ba5e9af9df4b60c1be6fbc70ab06c5a6e1d4fa6862143`；7,727 图片全部有像素、Alpha8 或原件字节证明，0 无据图片、0 搬移/meta 错误。已归档回执并删除两份旧测试导出约 8.22 GB。


## 当前结果：统一类型目录与 Textures 合并已完成（2026-10-25）

用户确认 Unity `Assets/Game/Content/<Type>/<Module>/`、Creator `assets/resources/<Type>/<Module>/`。两端统一只生成 Textures 类型目录；保持原 Sprite GUID/UUID 与裁切/边框信息，仅复用字节完全一致的附加完整纹理。Unity 去除 5,391 份、Creator 去除 5,415 份重复 PNG，合计减少 563,105,516 字节。17,201 输入逐项保留，两个目标各 356 音频、528 JSON、1,776 Spine 闭包及 214 Shader 来源文件齐全；1,694 源 Prefab 相对路径与名称一致。

最终 Unity 自有副本验证器 0 诊断、保存重开通过（Editor partial 保留源缺口）；Creator 第五轮 editor pass/0 诊断，1,694 Prefab/24,784 节点/416 动画/356 正时长音频及八组动态探针完成回读。两端 528 JSON 实际导入类型、7,587 纹理映射与原字节已核对。Creator 1,768 SkeletonData 原生导入，另 8 套保留原始文本。所有本轮已知自有 Editor 进程已退出。

本轮同时修复 Boot 父目录、全树 UI 探针开销、AudioClip 时长 API、源几何初始化/Prefab 再激活，以及 Creator 手动对齐递归更新禁用 Widget 的校验器问题。当前 308 项测试通过；失败版本与完整证据保留在 .private/unified-textures-20261025/。最新原生目录为 outputs/foodstreet-unified-textures-unity-native、outputs/foodstreet-unified-textures-creator-native-05；离线源为 outputs/foodstreet-unified-textures。旧导出清理完成：删除 12 个过时/失败导出目录及 5 份中间候选备份（17 个受控根），清理前目录占用约 193.34 GiB，文件逻辑字节 203,142,619,438。仅保留本轮离线双目标、Unity 原生、Creator 原生三个阶段；失败回执、manifest、关键助手源码与日志摘要已归档于 .private/unified-textures-20261025/retired-receipts/。

未闭合：Creator 有 19 次 Tiled Sprite 渲染缓冲区分配错误；Unity 两个派生状态动画名超过 64 字节。结构/引用通过不等于视觉/业务/Player 完成；Shader 仍为来源代码、Unity Spine 播放及微信远端打包未验。工具未提交/发布，原游戏与 GREA 未修改；更大版本的其他门槛按后续计划继续，不能用本轮目录结果替代。详情见 [本轮核验](validation/2026-10-25-unified-textures.md)。

## 历史：资源缺失与分区目录修复（2026-10-25）

本聊天用户明确要求执行双端方案。已修 Creator AudioClip emit/目标覆盖判定；新增完整纹理与 Effect/GLSL 源文件目录、Spine 正式资源闭包；共享分区器与 PascalCase 路径、资源地址清单、Creator Bundle meta 已实现。双端新候选 outputs/foodstreet-resource-layout 导出完成；17,201 输入逐文件保留一致，356 音频/276 独立内容双端一致、原 Creator 少导的 259 种已补齐。各 7,587 完整纹理、1,776 Spine 闭包、38 Effect/214 源文件、528 JSON；静态 pass/0 诊断。12,164 共有资源文件名一致，中文路径及超长正式资源文件名均 0。1,517 跨包 redirect 已改为已解析，4 个未知索引单列。

300 项全套通过；后续静态 Shader 名 MovieClip 误报修正与合成 WAV 双端测试共 18 布局 + 6 专项通过。Unity 6 自有副本正在执行原生导入，之后顺序 Creator 3.8.8；新工程通过前保留旧输出。微信分包/Player 未验证，Unity Addressables/AssetBundle 后端仅输出分组方案，未配置构建。验收 docs/validation/2026-10-25-resource-layout.md，机器证据 .private/resource-layout-20261025/。

## 当前审计：Cocos / Unity 完整性与命名（2026-10-25）

用户要求对比目录/文件、命名及原版漏导。本轮只读核验，未改工具/输出、未启动 Editor。独立遍历 17,201 源文件并核对两个候选及 Unity 原生副本保留字节：0 漏存、0 哈希错误。528 JSON/1,776 Spine 闭包一致；2,617 个不同 PNG 按声明裁切后像素全部一致。11,808 共有资源映射及 914 草稿主名一致，43 个模块目录差异均为 Creator 大小写/长度截断规则。

发现待修复：Creator assets 仅 17 种音频，Unity 276 种；259 种内容只保留于 SourceRecovery。根因是 consumed_inputs 不区分目标能力而 Creator 无 AudioClip emit。另有实际文件名超 64 字节：Unity 候选 22、Creator 18、Unity 原生 36；两端各 18 草稿非 PascalCase。旧 1,521 missing_reference 实为 1,517 已解析跨包 redirect + 4 个未知 main UUID，不能当作 1,521 文件丢失。冻结输出与旧记录未改写；以后以此分类解读。

完整报告 docs/validation/2026-10-25-export-parity-audit.md，机器证据 .private/export-parity-audit-20261025/summary.json。优先修 Creator 音频及目标覆盖状态、最终名称长度、缺失引用统计；本轮为审计交付，修复尚未实施。

## 本轮完成：仅 monkey 导出 Cocos 3.8.8（2026-10-25）

用户本聊天最初要求导出/导入，随后明确收窄为“仅使用 monkey 做导出 Cocos 3.8.8 测试”。已仅用 monkey convert --target cocos38 --offline 导出 outputs/foodstreet-creator388/CocosProject，并由 monkey verify --level static 验证通过、0 诊断。17,201 输入/884,709,704 字节均计入台账，528 配置 JSON，63,896 清单文件中文路径为 0；导入计划含 8,511 资产（8,472 SpriteFrame）、24,784 节点、1,694 源 Prefab 计划。导出 completed=true/status=partial，4 项已知源恢复警告保留；不将离线候选或计划计数称为实际原生还原。

未启动 Creator、未执行导入/编译/运行、未使用其他转换器、未恢复肥鹅 Cocos 产品开发。原生脚本仅准备未执行；按用户最新范围记 not_run_by_user_scope。15 项相关离线测试通过。验收 docs/validation/2026-10-25-creator388-export.md；证据 .private/creator388-export-20261025/delivery.json。现有 Unity 最新输出保持。

## 当前：中文路径拼音化与配置表补全（2026-10-25）

用户本聊天直接要求修改中文命名文件并解决 JSON 配置表缺失。已在共享命名器、原始证据路径及 Spine 页图闭包实现拼音命名/同音冲突消歧；骨骼区域标识、源 JSON 键和值不改。新增带静态格式证据、完整字节消费和预算限制的 BON 解码/逐表 JSON 导出，覆盖原配置 10 包、528 个顶层值（含 236 张主表），主表/地区覆盖/语言数据独立保存。

296 项测试通过，17,201 输入逐字节核验、528 JSON 与独立 BON Reader 重建对象完全一致；目标工程中文路径 0、1,776 Spine 页图闭包有效。旧候选 GUID 对比：600 路径迁移、8,775 保持、0 丢失、528 新配置。新输出 `outputs/foodstreet-unity6-pinyin` 与 `outputs/foodstreet-unity6-pinyin-native/UnityProject` 已完成 Unity 6000.6.2f1 原生验证：1,694 源 Prefab / 24,784 节点 / 8,952 Sprite，Missing Script 0、保存重开通过、验证器 0 诊断；528 配置 TextScriptImporter 实际导入并保留字节。静态 pass、Editor partial（既有源限制），配置运行时业务绑定/Player/视觉仍未验收。详情 [本轮验收](validation/2026-10-25-pinyin-config.md)，证据 `.private/pinyin-config-20261025/`。本地开发功能，未发布；不宣称所有引擎身份约束均可自动改名。旧两个输出已核验后清理，保留关键回执，实际释放 15.26 GiB；outputs 仅保留本轮两个阶段。

## 上次交付：肥鹅资源重新导出完成（2026-10-25）

用户自行删除全部旧 outputs 后要求全新导出。三处原始输入仍在，旧清理计划未执行。已使用当前 monkey 工作树生成 `outputs/foodstreet-unity6`，并在 `outputs/foodstreet-unity6-native-02/UnityProject` 完成 Unity 6000.6.2f1 全量原生导入。详情见 [重新导出验收](validation/2026-10-25-foodstreet-reexport.md)。

17,201 项输入逐字节核验、8,952 张图片检查、914 份唯一草稿检查通过；实际 1,694 源 Prefab / 24,784 节点 / 8,952 Sprite，Missing Script 0，保存重开通过。子进程 exit 0，静态 pass，Editor partial，验证器 0 诊断。首轮 MiniGames 动画 allow-root 失败已修复，27 项定向测试通过；失败证据另存私有目录。原 1,521 缺失引用、16,630 源限制与业务/Player/视觉 not_run 继续保留。游戏工程未改，工具未发布。

机器回执 `.private/foodstreet-reexport-20261025/delivery.json`；旧 outputs 历史路径已失效，不视为当前交付。版本整体尚未收口，不用本次肥鹅导出覆盖向僵尸缺脚本等未完成门槛。


## 当前：0.3.0.dev1 工程布局重构接手（2026-10-25）

用户直接要求接手 Claude 未完成开发。当前分支 `monkey`，基线 `2d4f528`；实施合同见 [PROJECT-SPEC](PROJECT-SPEC.md)，D1–D6 已记录确认。Claude 的六个提交及全部未提交改动保留，未重置或覆盖工作树。此节覆盖下面旧版本“当前/完成”措辞；旧证据继续归属原候选。

- 已提交：布局规划器、Unity/Creator emitter 接入、代码草稿/Spine 闭包重排、Unity 来源同 GUID 重定位、真实输入命名规则修正。
- 接手时未提交：Analysis 分组及兼容读取、工程文档/模块索引、layout-preview/layout-migration CLI 和多处 writer/test 接入。该组现已通过离线测试，但未作新版原生验证。
- 本次修复：macOS Assets/assets 同目录重复扫描导致迁移清单重复和大小写错误；重复 GUID/UUID 显式拒绝；Creator 目录 meta 不当资产；仅新候选存在的资产增加逐项清单。README/USAGE/ARCHITECTURE 同步。
- 验证：首次 284 项中 1 项失败；修复及增加反例后 286 项通过（12.207 秒），git diff --check 通过。日志 `.private/takeover-20261025/unittest.log`。这是工具离线测试，不是游戏或 Editor 验收。
- 待完成：两款游戏完整输入重新生成/静态布局检查及确定性核验；与冻结 dev3 按身份比较 GUID/UUID 和移动覆盖；Unity/Creator 代表样本原生回读；按结果收口 SUPPORT-MATRIX/验收报告并更新版本号和本地分发。
- 版本仍为 0.2.0.dev3，目标 0.3.0.dev1 尚未交付/发布。本次未启动 Editor、未修改肥鹅或冻结候选、未再次清理 output。


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
