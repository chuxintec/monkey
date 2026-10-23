# Creator 2.1.2 资源子集

`cocos-2.1.2-resource` 从本次输入的原 JS 静态解析 `cc.ENGINE_VERSION="2.1.2"` 及唯一 `window._CCSettings={...}`。固定 Acorn 仅读 literal object/array/string/number/boolean/null 和数字 !/-/+；函数调用、计算属性、重复属性、spread及多份settings拒绝，不执行原JS或源模块factory。记录整个输入和原赋值字节范围SHA。原始13206项UUID表、packedAssets成员及md5AssetsMap版本用于精确定位，不能用缓存中另一版本代替。

旧缓存是文件名→时间戳的109项声明，`cacheKind=legacy-flat`只读取这些声明的确切文件；时间戳不是内容身份，实际SHA另冻结。导入pack按原顺序/成员数解包；不同pack同身份正文冲突拒绝。SpriteFrame content明确投射rect/offset/originalSize/rotation/insets，未知几何字段拒绝；纹理身份、版本与文件必须匹配。Prefab/Scene、AnimationClip、材质和方法只保留证据，不套2.4节点解释。

实际《机智逃脱》5个已解密原包+109缓存：129展开输入26806035B；211源Frame/38纹理依赖/81隔离图/1原生音频，956模块草稿、5源码来源待补、9Spine闭包待补。settings完整声明资产身份并集19298，本次未提供18955；这与当前已解析引用缺口0分开统计，不能称为全部资源已取得。

公开单命令02双端原生：Unity93877于22:20:45.832681Z→22:21:03.159315Z exit0/reaped；Creator94149于22:21:04.060650Z→22:21:26.613506Z正常TERM/reaped。两端strict0，Unitypartial/Creatorpass。Unity422Sprite变体、211gallery引用逐GUID/geometry核验，源nodes0/sourceGraphVerification=not_run；未恢复原界面或玩法。02 manifest `e0b7822699f9dc27e7e1be39ac114c7e2235146ec66ad6097848a9b26c5e70bf` / `a4290b400360b9b2c7d661400603db448be6abc12daafe22df4fa53e4ab5140a`。

后续03只补充完整声明资产分母及缺源计数，不重复已通过的像素/原生段；211实际Frame及其资源投射范围相同。03 Unity `5b179d80df29160f7895f0e1e8476cf95bb50db58521ceab1cc965f3c880be7c` / Creator `abc3984fe81dfd8d0faef05fcdf3edece9dcd0d3a2fdcc8f447e3baf68f85678`。未知旧格式与其他1.x/2.x仍需独立adapter。
