# 来源与目标支持矩阵

2026-10-23用户批准产品目标，原生验证按独立资源窗口执行。planned/supported_static/partial/native_verified/unsupported必须按具体profile和样本记录，不把一个样本推成整个家族兼容。用户本聊天最新目标规则：Cocos所有版本原包→Unity6/Cocos3.8.8/both；Unity、Laya/LayaAir、Egret（用户写作Eraget）、自研及其他引擎所有版本原包→Unity6。此为产品范围，不是全格式已支持。目标当前精确版本为Unity6000.6.2f1/Creator3.8.8，不更改已安装引擎。用户最新补充：所有Unity来源版本一律以Unity6为目标，源版本解析能力逐profile验收。

|来源|目标|当前实际状态|后续批准顺序|
|---|---|---|---|
|Cocos Creator2.4.15发布bundle|Unity6 / Cocos3.8.8 / both|partial：full14双端各1694 Prefab/24784节点保存重开与完整几何/引用回读零诊断；Unity资源partial/Creator资源pass，业务/视觉/交互未验收|先收拢肥鹅当前包|
|Cocos Creator2.4.11发布bundle|Unity6 / Cocos3.8.8 / both|partial：冲关小队881明确输入；451源Frame、91节点图，两端资源/节点/引用保存重载0严格差异，170源码模块仍草稿|持续逐case|
|Cocos Creator2.1.2旧发布资源|Unity6 / Cocos3.8.8 / both|partial：211原Frame/422变体双端原生0严格差异；81源图隔离，19298声明身份中18955未提供|逐旧格式adapter|
|Cocos Creator2.4.15可编辑工程子集|Unity6 / Cocos3.8.8 / both|supported_static有限子集，非全版本/全组件承诺|按新增真实输入反例扩展|
|Unity2021.3.30f1 IL2CPP-Wasm|Unity6|partial：显式Bundle及依赖→Unity6候选已实现；代表1 Prefab/16字段/3 Sprite引用保存重载通过。启动4精确纹理已齐；显式冻结类型树池严格读到1567/1603对象，仍36MB缺结构；补充类型树已消费生成2字段类/11字段，但实例值尚未回写Scene，整包及业务未完成|U，用户最新打开《向僵尸开炮》优先|
|Unity2022.3.16f1 / 2022.3.34f1c1 WebData|Unity6|partial：两实际候选已导出；45/40坏ETC1显式隔离，其余对象hash逐项保持；461/77对象缺结构，原生/方法未恢复|逐case补齐|
|Unity2021.3.18f1|Unity6|partial：SpriteSaveInfo配置Prefab/一个Sprite[]字段实际导出并编译；自动闭包后131缺引用占位降0，原生待核。启动另缺3精确纹理而blocked|按独立分支补闭包|
|团结2022.3.61t9|Unity6|blocked：typed2888/3042读取，固定Provider仅3042不可读证据、0原生资源；未晋升候选|专用来源adapter待实现|
|Unity任意版本其他Mono/IL2CPP来源|Unity6|planned，逐serializedFile/AssetBundle/provider/profile增加|U|
|Unity6来源|Unity6|planned，需明确版本真实样本|U|
|Cocos Creator3.8.7发布资源|Unity6 / Cocos3.8.8 / both|partial：下方了496明确输入/38081754B，4804对象正文；986源Frame→1972变体双端原生强回读0差异。119源图/采样行为/Spine/业务待适配，Excel/Proto两zip缺失|C，持续逐case|
|Cocos Creator3.x其他格式|Unity6 / Cocos3.8.8 / both|planned，不能套2.4 reader|C|
|Cocos Creator2.4.x以下/1.x旧格式|Unity6 / Cocos3.8.8 / both|planned，逐格式/版本反例，不能笼统已支持|C|
|Cocos2d-x及其他Cocos分支原包|Unity6 / Cocos3.8.8 / both|planned，独立识别和适配，不能套Creator序列化|逐来源样本|
|Unity任意来源|Cocos / both|unsupported，不在本次批准矩阵|明确拒绝，不产假工程|
|Laya / LayaAir 所有版本原包|Unity6|planned专用adapter；显式图片gallery fallback仅自造反例验证，没有真实Laya案例|持续逐来源|
|Egret / 自研 / 其他引擎原包|Unity6|专用adapter planned；灵画师16张原图的派生gallery已原生验证，原图集/节点/方法均未恢复，custom仅自造反例|持续逐来源|

上述范围是支持目标，未知UnityTypeTree/压缩/未来格式/团结等分支单列provider或诊断，不因有版本字符串就近套解析器。资源、元数据、Mono实现、IL2CPP/Wasm方法体、DummyDLL/签名桩、编译、原生保存重开、视觉、可玩分别报告。

人类依据已原生核验：总监turn01a167c9-388f-7920-80b6-961ab237c0d7，message01a167c9-38cf-7a21-8ae8-83a8bf19d8c0及01a167cb-ba50-73a3-8dbf-4a8bd7f56115。产品路线见ENGINE-ROADMAP.md；仅选择转换样本，不在projects立项复刻游戏。
