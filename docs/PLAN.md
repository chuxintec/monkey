# monkey 项目计划与执行进度

完工/阻塞/交付与续推按[DIRECTOR-CONTINUATION](/Users/wangmeng/Documents/Manager/standards/DIRECTOR-CONTINUATION.md)执行；本聊天已原生核验人类授权`01a166b4-5c18-78f3-8cc2-c0d07dd46a20`，总监路由`01a14c8c-6402-7d03-bab8-ec7ea8051abf`。更新本PLAN后以稳定事件ID报告，已批准就绪下一包连续推进，不因报告或普通ACK停下。

## 当前：v0.2 声明范围本地交付已验收，预发布 v0.2.0.dev1（2026-10-24）

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
