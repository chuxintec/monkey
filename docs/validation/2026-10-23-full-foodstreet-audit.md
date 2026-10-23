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
