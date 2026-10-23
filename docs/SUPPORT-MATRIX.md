# 来源与目标支持矩阵

2026-10-23用户批准产品目标，原生验证按独立资源窗口执行。planned/supported_static/partial/native_verified/unsupported必须按具体profile和样本记录，不把一个样本推成整个家族兼容。用户本聊天最新目标规则：Cocos所有版本原包→Unity6/Cocos3.8.8/both；Unity、Laya/LayaAir、Egret（用户写作Eraget）、自研及其他引擎所有版本原包→Unity6。此为产品范围，不是全格式已支持。目标当前精确版本为Unity6000.6.2f1/Creator3.8.8，不更改已安装引擎。用户最新补充：所有Unity来源版本一律以Unity6为目标，源版本解析能力逐profile验收。

|来源|目标|当前实际状态|后续批准顺序|
|---|---|---|---|
|Cocos Creator2.4.15发布bundle|Unity6 / Cocos3.8.8 / both|partial：肥鹅全资料静态计划/资源账已验证，原名整改05离线验证通过；原生/业务未通过|先收拢肥鹅当前包|
|Cocos Creator2.4.15可编辑工程子集|Unity6 / Cocos3.8.8 / both|supported_static有限子集，非全版本/全组件承诺|按新增真实输入反例扩展|
|Unity2021.3.30f1 IL2CPP-Wasm|Unity6|planned：当前273包SHA/2021.3.30f1正文已核，1603对象枚举/1326所选typed读数；106 MonoBehaviour类型不足，通用reader/Unity6输出未实现|U，用户最新打开《向僵尸开炮》优先|
|Unity任意版本其他Mono/IL2CPP来源|Unity6|planned，逐serializedFile/AssetBundle/provider/profile增加|U|
|Unity6来源|Unity6|planned，需明确版本真实样本|U|
|Cocos Creator3.8.7发布资源|Unity6 / Cocos3.8.8 / both|planned，《下方了》真实app-config插件声明3.8.7已读，资源正文待核|C，U后|
|Cocos Creator3.x其他格式|Unity6 / Cocos3.8.8 / both|planned，不能套2.4 reader|C|
|Cocos Creator2.4.x以下/1.x旧格式|Unity6 / Cocos3.8.8 / both|planned，逐格式/版本反例，不能笼统已支持|C|
|Cocos2d-x及其他Cocos分支原包|Unity6 / Cocos3.8.8 / both|planned，独立识别和适配，不能套Creator序列化|逐来源样本|
|Unity任意来源|Cocos / both|unsupported，不在本次批准矩阵|明确拒绝，不产假工程|

|Laya / LayaAir 所有版本原包|Unity6|planned，需真实样本和独立来源profile|当前肥鹅及U/C收拢后|
|Egret / 自研 / 其他引擎原包|Unity6|planned，逐引擎识别，未知格式明确拒绝或隔离|同上|

上述范围是支持目标，未知UnityTypeTree/压缩/未来格式/团结等分支单列provider或诊断，不因有版本字符串就近套解析器。资源、元数据、Mono实现、IL2CPP/Wasm方法体、DummyDLL/签名桩、编译、原生保存重开、视觉、可玩分别报告。

人类依据已原生核验：总监turn01a167c9-388f-7920-80b6-961ab237c0d7，message01a167c9-38cf-7a21-8ae8-83a8bf19d8c0及01a167cb-ba50-73a3-8dbf-4a8bd7f56115。产品路线见ENGINE-ROADMAP.md；仅选择转换样本，不在projects立项复刻游戏。
