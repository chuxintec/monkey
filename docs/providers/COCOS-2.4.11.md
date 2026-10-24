# Cocos Creator 2.4.11 发布包子集

公开 package-convert 自动识别本次输入中原始 `cc.ENGINE_VERSION = "2.4.11"` AST 赋值；也接受显式 profile 与相符的原配置版本。注释、字符串内代码和其他对象的属性不作为版本证明，声明冲突拒绝，不自动就近套 2.4.15。静态解析使用固定 Acorn，不执行源 JS；记录原文件 SHA、UTF-8 范围及字节 SHA。上限 32MiB/300万节点/512层，隔离 Node 环境并有时间/堆预算。

## 真实《冲关小队》

10 个已解密原 wxapkg，经 Research manifest 哈希核对；容器 8325914B，881 个展开输入 8247168B。原版本赋值范围 1365303..1365329，整文件 SHA `c8a077e5008f28e4138afa667edf25ca4f595d59a8afb12a0ab0b7dc9d703c8b`，范围 SHA `d7be7a5f825da8ad2191579af1968446e30adf1831e8789bd17b2c29f40c0351`。采用已核对的 2.x 编译资源结构子集，未知字段、组件及缺引用继续列缺口。

`outputs/cocos2411-chongguan-package-03` 公开单命令 both 输出：451 个源 SpriteFrame/360 纹理依赖/33 native 载荷/91 个节点图；42 个 Spine 文件闭包仅资源闭合，播放未验。170 源码模块是源映射草稿，9 个源码来源和20个资源引用未闭合。

第一原生02在 Unity 因字体 atlas 容量失败，364 严格差异，Creator 未启动；失败保留。原 TTF 字形存在，1024 atlas 无法装下完整请求。新导入器按唯一字符数为固定 90pt/16 padding 请求选择1024/2048/4096的有界 atlas，仍要求 TryAddCharacters 全部成功并严格核真实字形，不替代字体或容差。

新鲜03：Unity90592于22:02:20.273789Z→22:02:43.754387Z exit0/reaped；Creator91386于22:02:45.141184Z→22:03:15.442065Z正常TERM/reaped。双端 strict0，Unity editor partial / Creator pass。Unity1550节点/902 Sprite变体/89独立Prefab/177标签和2字体保存重载；原资源、节点几何及View引用按计划强核。视觉/输入/完整玩法仍not_run。

Unity manifest `c81aac4b36e3b06a17945a20326c721fb4f14bf4f1ac71ac3001cc54fcdcd348`；Creator `1465091db38fbe92ede45b2ad4e5bc845d415cbfc0b2fffb3003a3f3c3edd90d`。所有样本、原件和产物均私有隔离；本支持不等于所有2.x版本或全部业务恢复。
