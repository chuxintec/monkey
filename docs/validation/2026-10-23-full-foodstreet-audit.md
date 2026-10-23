# 肥鹅全部资料转换与集中核对

用户授权原生核验：总监turn01a16781-e3f9-78d1-9fcd-001f73f41486 / human message01a16781-e596-7581-9fd9-76378aef0afb。本次独立执行，原件只读、无网络补取、无人工客户端或服务实现混入。

## 来源分母

|口径|文件|字节|用途|
|---|---:|---:|---|
|Evidence既有总清单|17216|905618352|逐项SHA和长度均verified，覆盖源/冻结目录无多出或缺失|
|Evidence/source|17097|856102708|上项子集，包含CDN16627项、缓存、原包和公开配置|
|本轮明确转换输入|17201|884709704|source全部＋snapshot101＋两个plain包和decoded-config三个衍生原件|
|仅核对参考|15|20908648|7个引擎参考文件＋8个获取清单/证据，排除目标Assets|
|此前四根候选|5097|243799340|仅局部，不能作为全部资料分母|

总清单内容哈希唯一16161份/806404759字节；转换输入唯一16147份。逐路径重复映射见.private/full-foodstreet-audit-01/source-audit.json，去重不是文件漏失。两个plain包27/72条均逐项SHA匹配冻结展开文件；各snapshot多一份展开回执，未冒称额外游戏资源。

源内9个远程bundle全部纳入：gameAsset、remoteAsset、spineAsset、miniGameRes、zh、zh-tw、en、jp、kr；冻结主包含internal/resources/main。历史清单明确miniGame代码分包未取得，只有miniGameRes美术；不把获取0失败或CDN已全下载当缺包不存在。

## 固定执行

输入.private/full-foodstreet-audit-01/inputs.json，SHA 1fef746ef5f4483aa9605da81aef4a8ed6cea736834b2024169a00c6aa60fff2。其三个根分别是原source、原snapshot、monkey私有派生原件最小副本。所有副本SHA与原件一致，完整原路径账保留，源游戏版本1.9.1为来源声明，不冒充独立运行验证。

```sh
bin/monkey convert --input-set .private/full-foodstreet-audit-01/inputs.json --target both --namespace foodstreet-full --out outputs/full-foodstreet-01
```

工具固定64b7c51。针对实际884709704字节、约24k bundle UUID上限，将全输入总预算从512MiB增至1GiB、结构化资产上限从20k增至50k；单文件128MiB和默认原始解析32MiB保持。package/structured九项定向检查通过。旧候选均保留；本轮还没有启动Engine，窗口08申请不作为授权。

当前转换正在执行，结果与P0/P1集中核对待补。原生保存重开、字体/Spine runtime/代表视觉均未验；不把计划和源码初稿当实际对象/玩法恢复。

## 首轮实际排查：P1 等价缓存索引

full-foodstreet-01完成17201项双端文件台账，但Structured/recovery.json为DUPLICATE_BUNDLE失败，nativeObjects=pending_adapter，不是结构化成功。原缓存gameAsset时间戳JSON与CDN索引等价，被reader按重复bundle拒绝。修复选择前验证整份索引语义哈希一致，仅在等价组选择实际具备import/native树的根，所有别名/原件留存；索引冲突仍拒绝。缓存裸索引先出现且缺载荷的反例已通过，四项structured检查通过；阶段签名纳入structured.py。新02输出重跑实际失败路径，旧01保持证据，不当Native通过。

人类当前monkey聊天追加批准下载CDN/远程包并补充肥鹅；已实际GET19个已知端点，12响应同原件、7HTTP404，原16627 CDN文件全部本地SHA/长度verified，无新增文件。9远程bundle均isZip=false，脚本原包内嵌；miniGame微信代码分包缺少可下载URL仍缺。肥鹅Analysis/acquisition/monkey-full-20261023-01及Evidence/README已补回执，不改产品/角色/服务。缓存462个wxfile原ID因冻结目录移除usr/gamecaches前缀，按明确前缀重定位全与CDN同hash，原manifest未改。当前full02正在normalize，资源窗口尚未申请/执行。

全量02已解析23955源对象，包含1776 Spine、8467 SpriteFrame、1696 Prefab、358 AudioClip、23 JsonAsset；四个等价缓存索引已正确映射CDN。归一化实际输出约1.6GiB触发旧1GiB owned-output上限，阶段失败且保持证据；这是实际解码膨胀预算而不是漏源。仅whole-input输出上限有界增至4GiB，保留切片256MiB/原始解析32MiB/单文件128MiB/生成文档128MiB限制；生成IR70MiB在已声明128MiB元数据预算内。下一全新03继续，02不原地修改。

全量03实际生成双目标原生计划：23955源对象→24784节点/28514组件/8467帧/11字体/23JsonAsset；Unity13550、Creator12588组件可转换，仍为计划而非原生对象。二进制Spine1762闭包，14项实际是内嵌JSON而非缺源。已补JSON骨骼原样语义导出、atlas/纹理闭包，精确保留含3.8-from-4.0-from-4.1-from-4.2.43等源版本标签，不推断兼容runtime；真实14项定向复验14/14闭合。修正相同缓存索引导致逻辑资源重复/假缺失计数，按(bundle,index)合并定位证据，原件账不去项。14项定向检查通过；03冻结不改，按新实现生成04最终核对候选。

## 最终离线候选04与集中核对

实现固定838d05b，公开CLI完整执行完成，exit1按needs_action合同返回，不冒称原生完成。输入未因CDN补核发生变化；实际新增的是肥鹅获取回执/说明，3份材料在Analysis/acquisition/monkey-full-20261023-01，未混入游戏资源。

|项|Unity6|Creator3.8|
|---|---|---|
|工程|outputs/full-foodstreet-04/UnityProject|outputs/full-foodstreet-04/CocosProject|
|manifest SHA|c084c8c6bbf472b17f65057dfaf26a35138477b06056053b4b7685b5490ff630|ab1673be10093857b4c1489a934cd96074a733ff4df0b6271fdc0ea4b88e799a|
|文件/字节入账|17201/884709704|17201/884709704|
|静态verify|exit0/零诊断|exit0/零诊断|
|源路径→保留字节对账|pass/零问题|pass/零问题|
|共享计划节点/组件|24784/28514|24784/28514|
|可转换组件计划|13550|12588|
|独立源Prefab计划|1694|尚无该适配；现有Scene聚合流程，不当作独立Prefab已恢复|
|TTF/位图字库计划|11/5|11/5|
|JsonAsset计划|23|23|
|Spine数据闭包|1776/1776|1776/1776|
|原生保存重开/代表画面/业务|not_run|not_run|

源类型含1696 Prefab和3 Scene，源图1项隔离，原生计划不等于已保存。8467 SpriteFrame产生16934个trim/original纹理变体；Creator另有5个位图字库纹理Sprite，不能算新增原版SpriteFrame。Unity Assets实际约1510157092字节。源AudioClip358，Unity原生资源计划356；373个原始音频文件（含缓存/重复）全部有字节去向，Creator目前按音频原件复制/meta导入，未生成同等AudioClip行为计划。未转换能力与文件丢失分别记录。

源RF区域914，每目标914初稿、3个源包装上下文未闭合；5773组件→代码绑定、742视图批＋资源/未分类池共749批，259区未分类。未启动Agent；初稿全部在SourceRecovery编译排除区，业务not_implemented。

粗索引missingReferences=1521中，1517是声明redirect、不拥有独立文件；非redirect未定位4项：main:2fe916b2-a259-47da-98a6-4377b9feb162、main:3057bf89-567c-48bc-8463-91d22afdf6a6、main:3cd60781-3b8d-4c98-b86f-1c1b16e8909c、main:957bd1fa-ddd8-40e7-b414-9fda8572f4d1。不能当1521个CDN漏下载。结构reader原版非法UUID/相关文档unsupported共3项诊断，精确保留原字节和ID；不猜改原件。原miniGame代码包和7个HTTP404公开配置仍缺，不把未提供内容算已恢复。

## P0/P1结果与原生资源申请

- 本次文件去向/内容SHA核对未发现P0丢失/错配，不代表未执行引擎阶段也无P0。
- 已修P1：等价缓存索引阻断结构化读取、逻辑资源重复/假缺失计数、实际全量输入/解码输出预算不足、14个内嵌JSON Spine假缺源。14项定向检查pass、真实14 JSON闭包复验全闭合，04双端最终闭包全闭合。
- 待实际复验P1：窗口07的Unity字体材质/无名场景修复已进入04；SDK窄编译可复用，未宣称原生闭合。
- 能力差额：Creator独立Prefab原生适配、音频/未知组件/动画与业务绑定、非标准源身份及非法源图、Spine runtime导入/兼容播放均未完成。Spine回执runtime字段描述候选整合状态，不断言Creator安装包缺少内置Spine模块；含转换来源的版本标签原样保留。
- 外部/原件缺口：miniGame wxapkg没有明确公开地址，7个配置地址HTTP404；不猜包地址，不联网扫目录或操作微信账号。

只读preflight零诊断、Editor可执行文件存在，host IPC/写权限未探测，nativeExecution=not_run，不能当实际启动许可。拟申请独立Unity6000.6.2f1新窗口：外层30分钟、方法20分钟、内部UTC总截止早于外层2分钟；依据为1.51GB Assets、16934纹理、1694 Prefab计划及旧10358纹理49秒到fonts的实测，Prefab保存吞吐仍未知，不保证估时。首新错误停止并释放，只持有自身PID；正常exec审批，不复用窗口08。Creator3.8.8另开顺序窗口，先确认能绑定工程窗口/菜单，不能绑定立即释放，不重演Dashboard盲重启。

## 可复跑与证据入口

```sh
# 用全新输出目录复跑，输入清单不变；不能覆盖04。
bin/monkey convert --input-set .private/full-foodstreet-audit-01/inputs.json --target both --namespace foodstreet-full --out outputs/full-foodstreet-next
bin/monkey verify --candidate outputs/full-foodstreet-next/UnityProject --out outputs/full-foodstreet-next-unity-check
bin/monkey verify --candidate outputs/full-foodstreet-next/CocosProject --out outputs/full-foodstreet-next-creator-check
.venv/bin/python scripts/audit_conversion.py --candidate outputs/full-foodstreet-next --source-audit .private/full-foodstreet-audit-01/source-audit.json --out outputs/full-foodstreet-next-routing-audit
```

本轮结果：outputs/full-foodstreet-04-routing-audit-02/audit.json、outputs/full-foodstreet-04-unity-check、outputs/full-foodstreet-04-creator-check、outputs/full-foodstreet-04-preflight。静态verify核对实际生成文件，routing audit将原始来源路由/字节/哈希绑定到这些已核验生成清单；不重复把manifest自洽当作原生成功。原源审计与网络收据在.private/full-foodstreet-audit-01，肥鹅本轮获取收据也已补至其项目。
