> 当前开发0.6.0.dev1为合并的C#恢复/模块构建版，C1–C9见[PLAN](PLAN.md)。肥鹅大JS整源词法索引16,384方法，3源模块12方法自动转写/离线编译/独立行为通过，2模块9方法/原JSON在Unity原生有限流程通过；其余方法未生成。Mono仅合法夹具，向僵尸IL2CPP/WASM仍metadata_only，不提前记家族supported。v0.5受限交付及36精确正文缺口原样保留。

> v0.5 受限本地出口已接受：`acceptedDelivery=local_declared_subset`；原范围 `versionComplete=false` / `originalScopeComplete=false`。依据 [总监裁定](/Users/wangmeng/Documents/Manager/decisions/20261026-grea-monkey-beaver/MONKEY-V05-LOCAL-EXIT.md)，沿用 71c177d 和既有 0.5.0.dev1 制品，所有 partial/unsupported、36正文及字段写回阻断保持。后续只由精确可信输入/获准新方法/下一版指令触发，当前等待，不重测或重打包。

> 本地 v0.5 新增的标准 3.8.99 Spine 二进制/JSON 两份时间/姿态代表、精确单 Shader 材质/编译/Metal 像素结果及 36 正文 schema 阻断见 [本轮验收](validation/2026-10-26-v050-operations-resources.md)。仅声明代表子集，不外推全资源/全宏/全版本。

> 当前开发分支的原生 Flow 替换及限制见 [原生布局增量修复](NATIVE-LAYOUT-PATCH.md)。旧版本动态布局读回为历史证据；新实现按候选另验，不继承旧算法的全子集宣称。

# 来源与目标支持矩阵

2026-10-23用户批准产品目标，原生验证按独立资源窗口执行。planned/supported_static/partial/native_verified/unsupported必须按具体profile和样本记录，不把一个样本推成整个家族兼容。用户本聊天最新目标规则：Cocos所有版本原包→Unity6/Cocos3.8.8/both；Unity、Laya/LayaAir、Egret（用户写作Eraget）、自研及其他引擎所有版本原包→Unity6。此为产品范围，不是全格式已支持。目标当前精确版本为Unity6000.6.2f1/Creator3.8.8，不更改已安装引擎。用户最新补充：所有Unity来源版本一律以Unity6为目标，源版本解析能力逐profile验收。

|来源|目标|当前实际状态|后续批准顺序|
|---|---|---|---|
|Cocos Creator2.4.15发布bundle|Unity6 / Cocos3.8.8 / both|partial：full14双端各1694 Prefab/24784节点保存重开与完整几何/引用回读零诊断；Unity资源partial/Creator资源pass，业务/视觉/交互未验收|先收拢肥鹅当前包|
|Cocos Creator2.4.11发布bundle|Unity6 / Cocos3.8.8 / both|partial：冲关小队881明确输入；451源Frame、91节点图，两端资源/节点/引用保存重载0严格差异，170源码模块仍草稿|持续逐case|
|Cocos Creator2.1.2旧发布资源|Unity6 / Cocos3.8.8 / both|partial：当前147完整13091远端文件可得、19298声明身份缺0；7343Frame/14686变体每端静态通过，3旧版本缓存排除；旧211代表双端原生证据独立保留|当前全包Editor未跑；4406Prefab/3Scene及Spine等旧结构待适配|
|Cocos Creator2.4.15可编辑工程子集|Unity6 / Cocos3.8.8 / both|supported_static有限子集，非全版本/全组件承诺|按新增真实输入反例扩展|
|Unity2021.3.30f1 IL2CPP-Wasm|Unity6|partial：显式Bundle及依赖→Unity6候选已实现；代表1 Prefab/16字段/3 Sprite引用保存重载通过；2026-10-26补充3紧密Sprite的271顶点/336三角形及UV原生逐项核验，限精确2021.3.30f1/platform20/无旋转平面子集。启动4精确纹理已齐；显式冻结类型树池严格读到1567/1603对象，仍36个MonoBehaviour缺正文结构（已独立恢复72基础头PPtr）；补充类型树已消费生成2字段类/11字段，但实例值尚未回写Scene，整包及业务未完成|U，用户最新打开《向僵尸开炮》优先|
|Unity2022.3.16f1 / 2022.3.34f1c1 WebData|Unity6|partial：两实际候选已导出；45/40坏ETC1显式隔离，其余对象hash逐项保持；461/77对象缺结构，原生/方法未恢复|逐case补齐|
|Unity2021.3.18f1|Unity6|partial：SpriteSaveInfo配置Prefab/一个Sprite[]字段、131引用公开native保存重开已验；grea固定134动态寻址资源，实际移动0。启动6纹理已齐并导出44原生资源；91对象/原方法及整包原生待补|按独立分支补闭包|
|团结2022.3.61t9|Unity6|blocked：typed2888/3042读取，固定Provider仅3042不可读证据、0原生资源；未晋升候选|专用来源adapter待实现|
|Unity任意版本其他Mono/IL2CPP来源|Unity6|planned，逐serializedFile/AssetBundle/provider/profile增加|U|
|Unity6来源|Unity6|planned，需明确版本真实样本|U|
|Cocos Creator3.8.7发布资源|Unity6 / Cocos3.8.8 / both|partial：下方了496明确输入/38081754B，4804对象正文；986源Frame→1972变体，83源图/810节点/81 Prefab双端原生0严格差异。ParabolaUtils的3个静态Number方法生成C#/TS/JS并各13边界调用通过，无组件绑定；真实4Prefab/5原生嵌套关系双端已验证，动态16节点代表双端状态≤0.05px；114图静态闭合（5图缺6模板），其余5向量方法/未覆盖布局/采样/Spine/业务待补，两zip缺失|C，持续逐case|
|Cocos Creator3.x其他格式|Unity6 / Cocos3.8.8 / both|planned，不能套2.4 reader|C|
|Cocos Creator3.4.1发布资源|Unity6 / Cocos3.8.8 / both|partial：天命11962输入/约1.01GB入账，11618确切下载齐；7071Frame/15位图字体/856源图/22503节点/52实例关系公共双目标输出。5Frame资源及6Prefab/331节点/8关系/7新增节点/1Widget双端原生严格0；Unity业务partial、Creator结构pass|1份null旋转图隔离；162未知native后缀、redirect/源码/Spine与全包原生/玩法明确列限|
|Cocos Creator2.4.x以下/1.x旧格式|Unity6 / Cocos3.8.8 / both|planned，逐格式/版本反例，不能笼统已支持|C|
|Cocos2d-x及其他Cocos分支原包|Unity6 / Cocos3.8.8 / both|planned，独立识别和适配，不能套Creator序列化|逐来源样本|
|Unity任意来源|Cocos / both|unsupported，不在本次批准矩阵|明确拒绝，不产假工程|
|Laya / LayaAir 所有版本原包|Unity6|planned专用adapter；显式图片gallery fallback仅自造反例验证，没有真实Laya案例|持续逐来源|
|Egret5.2.32/custom binary（灵画师166）|Unity6|partial：当前缓存原件同SHA并核启动/版本；48252声明/53图集1920切片/3024 EUI皮肤类（3026包根记录含2元数据键，非界面数），53精确CDN页闭合、1920切片像素核；132代表源切片Unity原生通过。原生EUI布局/方法/动画未恢复|源UI专用适配与AI接续|
|其他Egret / 自研 / 其他引擎原包|Unity6|planned专用adapter，custom只有自造通用图片反例|持续逐真实来源|

2026-10-24用户新取舍：不可逆方法/缺类型或确实不可支持的引擎可保留limitations，不再以全部游戏完整还原阻断版本；实际嵌套Prefab、override与动态布局仍须解决。天命/机智按微信目标缓存/有据远端补源，灵画师已纠正短暂Laya判断。

上述范围是支持目标，未知UnityTypeTree/压缩/未来格式/团结等分支单列provider或诊断，不因有版本字符串就近套解析器。资源、元数据、Mono实现、IL2CPP/Wasm方法体、DummyDLL/签名桩、编译、原生保存重开、视觉、可玩分别报告。

人类依据已原生核验：总监turn01a167c9-388f-7920-80b6-961ab237c0d7，message01a167c9-38cf-7a21-8ae8-83a8bf19d8c0及01a167cb-ba50-73a3-8dbf-4a8bd7f56115。产品路线见ENGINE-ROADMAP.md；仅选择转换样本，不在projects立项复刻游戏。


2026-10-24动态布局有限续修：19个缩放Grid、13个child-resize配置解除旧guard；实际6组/54态两端Editor保存重开与子节点几何通过，最大差0.000074px，详见validation/2026-10-24-layout-followup.md。该代表覆盖不替代全量原生/Player或所有组合；负缩放线性、NONE及浮点padding等guard继续列限。
