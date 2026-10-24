# 天命行者 3.4.1 资源与公共双目标导出

当前微信缓存修订12、资源版本1.2.67、原始 settings.CocosEngine=3.4.1。独立 profile 为 `cocos-3.4.1-bundle`，目标为 Unity6 / Creator3.8.8 / both，不将来源伪装成3.8.7。3包及336缓存原件保留不动。

公开命令 `bin/monkey convert --input-set .private/tianming-cache12-intake-01/inputs-all-declared-formats.json --target both --out outputs/tianming341-full-package-04 --offline` 已完成：14个显式根、11962文件、1011728200字节全部入账；19960声明对象，7071源SpriteFrame→每目标14142变体、1 TTF、13 JSON。两端静态verify均0诊断。此轮资源profile不恢复原版UI图，不能把空源图或派生gallery称为原版界面。

## 格式与远端证据

3.4.1 Texture2D 使用命名 `base/mipmaps`，SpriteFrame 尚无后期pivot/meshType/pixelsToUnit字段；分别依据[3.4.1 Texture2D](https://github.com/cocos/cocos-engine/blob/v3.4.1/cocos/core/assets/texture-2d.ts)、[SpriteFrame](https://github.com/cocos/cocos-engine/blob/v3.4.1/cocos/2d/assets/sprite-frame.ts)、[ImageAsset](https://github.com/cocos/cocos-engine/blob/v3.4.1/cocos/core/assets/image-asset.ts)实现。只支持有据的单图2D纹理、矩形帧与明确图像编码；多mipmap、自定义polygon不猜。原始采样信息保留，运行时采样语义仍列限。

配置版本表、原始资产 `_native` 和 fmt 扩展索引共同声明11618项下载：12 import、6938首选原生资源、4668声明备选图像编码，全部取得；11289实际下载、329本地SHA复用，合计926342475字节。ASTC与PNG/JPG均保留，转换选择第一个已声明、受支持、实际可得的编码并记录选择。另162个SpriteAtlas声明有native版本但未取得可确认后缀，未猜路径。并非已枚举整个CDN。

新增跨显式输入根的精确资源解析，保留实际快照路径和来源台账；相同版本同路径不同字节明确冲突。没有拷入/覆盖原包目录，没有用下载文件数代替实际资源入IR。3.4.1字符串pack成员索引和包容器身份单独处理；包容器不再作为额外普通对象解码。底层选择按不可变输入缓存，避免为每个pack成员重复哈希整份pack。

## 原生代表与必要剩余

真实5个源SpriteFrame、10变体覆盖旋转、trim/offset、九宫格、原矩形、奇数尺寸。Unity own82339（05:33:01–05:33:12 UTC）exit0/reaped，Creator own82795（05:33:34–05:33:53 UTC）TERM/reaped；两端严格0诊断/editor pass。机器回执见[tianming341-native-resources.json](tianming341-native-resources.json)。只验证资源，原版UI/玩法/视觉及整包native均not_run。

45项受影响检查通过。来源尚有203内置/外部redirect、162未知native后缀、6独立import形状及部分源脚本解析缺口；738 Spine闭包未恢复。下一必修组为已发现的3.4.1源图和mounted结构：857原图初审848可结构试读，4图实际含mounted（1个Widget组及7个子节点组），不能将其永久改为handoff。SDK/default版本核对和原生实例新增对象关系仍在推进，本组不是v0.2结项。

## 后续结构集成

full04资源候选保持冻结。后续公开同一命令输出full05，新增856份源图/22503节点/24511组件/52实例关系和15位图字库，双端静态0诊断。6Prefab/331节点真实追加结构两端原生闭环见[图与追加关系](2026-10-24-tianming341-graphs.md)；不把资源组早期原图未恢复描述当作当前状态。隔离对象总数包括Spine/自定义资产等，不是1683份失败图；图实际仅1份null旋转值未恢复。
