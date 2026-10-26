# monkey 项目计划与执行进度

## 当前执行：v0.5.0 / 05-A 收口、05-B 冻结交接（2026-10-26）

用户直接批准先做大工程预算/阶段复用，再做 adopt 并验证肥鹅/向僵尸。开发版本 **0.5.0.dev1**。后续人类批准 GREA/monkey/beaver 职责整改：monkey 负责独立恢复候选，开发工程采用事务交 beaver；已原生核验总监 human `01a1764c-0246-7541-88e4-9a84d3556574`。依据 [三产品计划](/Users/wangmeng/Documents/Manager/decisions/20261026-grea-monkey-beaver/PLAN.md) 与 [交接合同](/Users/wangmeng/Documents/Manager/decisions/20261026-grea-monkey-beaver/CONTRACT.md)，保留在途实现和失败记录，冻结后供 beaver 接手，不重新实现或继续扩展 monkey 工程事务。

| 工作包 | 本轮结果 | 状态与下一步 |
|---|---|---|
| 05-A 大工程预算/阶段复用 | 全输入 8 GiB/50 万文件，选择集 256 MiB/2 万，单文件 512 MiB；流式哈希/复制、有界 no-follow 读取；精确 reader/schema/依赖合同替代仅靠版本号。肥鹅双端和僵尸共 315,003 个文件逐项核验通过；肥鹅 inspect/normalize 无重解析/图片解码，僵尸全部 601 容器无 worker 复用 | 本轮子集通过；仍复用原有检查点，未声称任意历史版本/所有阶段均可续跑 |
| 05-B adopt 在途实现 | 三方预览、身份/命名空间/依赖保护、Unity 原生移动与回滚。339 测试通过；肥鹅副本前一 WIP 原生移动/保存重开通过，并有真实失败后回滚证据；最新新增目录/资产仅离线编译与测试，未原生验证。僵尸全量预览通过，未启动其 Editor | **移交 beaver**；冻结文件/哈希、依赖、调用方、实际验证层和剩余项见 [交接清单](BEAVER-HANDOFF.md)。旧入口明确 deprecated compatibility，替代未就绪前不假转发/不删实现 |
| 05-C 资源/引用阻断 | 36 未解析对象、借用字段写回、紧密图集、Tiled、超长动画名、Spine/Shader 代表子集 | 待实施，仍属 monkey 候选正确性；不能用边界迁移抹除缺口 |
| 05-D 诊断与使用基础 | 本组补充能力/预算声明与验收摘要 | 其他统一诊断、显式补取续跑、环境/CI/空间预览待实施 |

证据 `.private/v050-adoption-20261026/`；公开摘要 [本轮核验](validation/2026-10-26-v050-budget-reuse-handoff.md)。v0.5 尚未完成；日常安装仍为 v0.4.0，无推送/Release/全局安装。正式肥鹅/GREA 只读，向僵尸继续暂停；当前冻结点没有存活的采用 Editor/CLI 进程。

## 当前：v0.5 – v0.7 统一版本规划（2026-10-26，职责整改后）

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
