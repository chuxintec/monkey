# 已批准后续来源扩展

本路线沿唯一PLAN执行，不另建任务表。用户原生授权见SUPPORT-MATRIX.md；工作版本U/C不是预先声明发布号或已支持状态。

## 顺序与架构

先完成肥鹅全资料/原名恢复05及必要核对，原生窗口协调继续；自然安全点可只读核样本/依赖，不抛弃当前成果。之后推进U（Unity来源→Unity6），再C（Cocos3和旧格式扩展），同一立项不重复询问。不新增Agent、不改模型/上下文、不改GREA、不全局安装或下载引擎，不发布/推送，不恢复暂停游戏开发。

Python核心保留统一输入/容器安全、来源身份、资源全账、可读命名、阶段签名与可控接续、目标计划、诊断和AI接续。Unity来源采用自己的typed对象/PPtr/GUID/fileID/pathID契约，不强塞成Cocos节点图；Cocos2/3的序列化适配独立，仅共享证明可等价的UI/资源语义。目标只使用原生对象/组件，Unity Player不嵌源引擎解释器。原名映射对两源家族统一适用。

CLI继续convert --source/--input-set --target unity6|cocos38|both。加入真实source-family/version探测及有依据的显式profile；用户2026-10-23补充：Unity来源无论版本，目标一律Unity6，不保留旧目标版本分支；此目标规则不等于各版本解析已支持。Unity来源选择cocos38/both必须拒绝。能力检测、工具可调用、真实解析、Editor导入、业务分别报告。unknown不伪造工程版本或默认最近reader。

## U：指定Unity来源样本

用户指定最新打开《向僵尸开炮》。旧Research身份wx31a9c726536cdacc/本地修订273/Unity2021.3.30f1 IL2CPP-Wasm仅作线索。2026-10-23本轮只读检查已知对应账号的当前可见包目录，仅发现修订273，内有__WITHOUT_MULTI_PLUGINCODE__.wxapkg、_wasmcode_.wxapkg、_wasmcode1_.wxapkg；这还不是当前Unity版本/后端正文核验，不能只凭旧记录或mtime宣称已验证最新运行内容。本轮已通过固定本机grea:wxapkg-decrypt在monkey私有目录重新解密这3个当前包，明文SHA全部与冻结证据一致；分别3/2/48条目，game.js实际出现2021.3.30f1版本字符串，Wasm条目可枚举。这里只是当前包体静态证据，serializedFile/TypeTree正文仍待解析，不把版本字符串当完整原生恢复。原件/玩家档不写。

先发现本机可用且版本固定的AssetRipper/UnityPy/提取provider和GREA既有合同，只读复用、固定参数/输出schema，不重写Unity二进制生态。缺工具/TypeTree/元数据列条件，不自动安装。未知DLL/JS/Wasm从不执行。枚举Unity数据目录/AssetBundle/serializedFile及显式容器解包关系，保留GUID/fileID/PPtr、原名/路径、Prefab/Scene、Transform/材质/Shader/字体/模型/音频/配置。

Mono托管实现与IL2CPP/Wasm元数据/方法体分别分层；只有签名/空壳时进入SourceRecovery编译排除区，不声称业务恢复或编译通过。跨版本兼容在隔离候选与目标Editor原生API内有据处理，不靠改ProjectVersion或重做UI伪造恢复。保留对象引用SO；正式数值JSON遵既有约定，不破坏性机械转SO。

出口为真实已取得资源得到可追溯Unity6候选，代表原Prefab/Scene实际导入/引用回读/缺脚本报告/保存重开与显示；整个游戏可玩另验。Unity6和其他旧版本各需要有据样本，不能以该例泛化全家族。

## C：Cocos3和旧格式

首样《下方了》：Research/games/下方了/Analysis/source-work-20261021/__WITHOUT_MULTI_PLUGINCODE__/app-config.json的gamePlugins.cocos.version实际为3.8.7。该字段是插件引擎声明；正文、UUID/pack/CCON/import/native可用性仍需核。旧身份wx8310ec5d413eee82/修订70，不保证最新或完整资源。

reader按3.x真实序列化、UUID子资源、redirect/bundle/pack、System/JS模块和依赖；新增UITransform/UIOpacity/Canvas/层/坐标差异，unsupported明确隔离。输出Creator3.8尽量保留同源结构/身份；输出Unity6复用原生目标薄层，不能用2.4 parser猜3.x。2.1/1.x等按已取得样本逐profile扩展，不把Cocos2d-x与Creator混同。

出口为《下方了》明确输入→两套独立候选、Creator真实导入/保存重开/代表UI引用回读；Unity只对本轮新增语义作必要验证，不做无关全平台/逐场景矩阵。Research只读选样，不新建游戏开发项目。

## 后续来源家族

用户本聊天补充范围：Cocos所有版本原包输出Unity6/Cocos3.8.8或both；Unity所有版本、Laya/LayaAir、Egret（用户写作Eraget）、自研及其他引擎原包统一输出Unity6。后续扩展不改变当前肥鹅、U、C顺序；按取得样本逐来源识别和独立reader适配，未知不套用Cocos图或假称已支持。非Cocos来源请求cocos38/both一律拒绝。

## 原包与远程资源闭包

沿本聊天CDN/远程包补充授权，一键入口需覆盖原包明确声明的远程资源：已有本地缓存先核SHA复用，有据URL有界获取并记实际HTTP/哈希/缺失收据，未知miniGame地址不猜。肥鹅19次GET/16627本地文件核对已经完成；通用CLI自动获取编排尚未接入，不以本次人工收据冒充已实现。
