# Unity来源首个Provider合同（v0.2开发中）

目前仅明确本地UnityFS/UnityRaw/UnityWeb主文件及显式Bundle依赖→Unity6候选，不代表wxapkg整包、APK、serializedFile及全部源版本已支持。`inspect-unity`可单独检查UnityPy能读取的显式文件；转换只接受已验证bundle签名。Unity来源请求Creator/both或尚未实现的native/remote/input-set选项会先拒绝，不能静默忽略。

```sh
monkey convert --source /path/to/file.ab --target unity6 --out /path/to/new-candidate \
  --provider-python /path/to/existing/python --asset-ripper /path/to/existing/AssetRipper.GUI.Free \
  --dependency-source /path/to/exact-dependency.ab --unity-texture-cache /path/to/cache-pool.json
```

自动按bundle签名识别Unity，或明确`--source-family unity`。Provider不自动安装：现有Python须UnityPy1.25.3；AssetRipper精确2.0.0+1ac666f47d8e9dedf96afb0b914c70d7656151ea，实际首行产品前缀一起核对。Core不import GREA。独立worker只读源bytes，不跟随源目录的DLL/缓存/外部PPtr；TypeTree严格check_read，不使用宽松长度模式。ID为signed64十进制字符串，未解析对象/原始bytes hash保留；嵌入MonoBehaviour schema可恢复具名C#字段，但不包含原方法体。

AssetRipper只复制精确现有可执行文件和固定capstone伴随库到自有目录，版本/二进制SHA留收据；只绑定127.0.0.1随机端口，代理/跨域redirect关闭，不打开浏览器。使用公开Settings/LoadFile/Export/UnityProject接口，先回读TargetVersion6000.6.2f1、Level0、原Shader YAML、TextAsset bytes。设置文件和日志仅自有runtime；命令成功必须302完成redirect，HTTP200错误页不算成功，实际项目/版本/文件hash还需核对。固定总预算和正常TERM/reap，无SIGKILL。

公开接口依据（非代码复制）：AssetRipper2.0.0官方`GUI.Web/Pages/Commands.cs`、`Pages/Settings/SettingsPage.cs`、`WebApplicationLauncher.cs`与`Export/Configuration/SerializedSettings.cs`。运行副本避免默认settings路径写入GREA安装目录。不执行原DLL/JS/Wasm或原游戏方法。

目标工程把原始/Provider空壳源码隔离SourceRecovery；只有已证明字段结构的C#能替换对应Provider空壳，保留脚本meta GUID。未支持类型不生成any/object替身空壳；没有字段/方法的类不另发相同模板。旧VR模块在精确目标内不存在，明确移除并保留原包清单和迁移收据；未知功能不宣称恢复。Provider的deadbeef缺依赖GUID保留诊断，不能当有效引用。恢复manifest与原件hash独立。

## 首批实际证据

- 向僵尸开炮启动UnityFS2637008B：1603对象/1497严格parsed/106MB类型缺失；4个Texture2D只有外部资源键令牌，公开convert实际blocked、Provider未启动。原始全资料尚未转换完成。
- 3个带TypeTree远程Bundle严格读到1947对象。独立3122B代表Bundle经公开convert生成Unity6候选，原Prefab1、FrameSpritePool具名16个Sprite数组字段；原空壳隔离，3个外部Sprite引用仍缺。C#只程序集编译通过，方法实现0，不能当业务恢复。
- outputs/unity-source-convert-02/UnityProject/recovery-manifest.json SHA0adf7fe360c1942fc1a92e418125b6b1a6018ca81800be1832a2aa1a6fd680d6。
- 原生只读probe01 own65810 17:59:26Z→17:59:33Z exit1/reaped；Prefab几何/根GUID可读，MissingScript计数0但预期schema组件未识别，严格失败，未保存/集成。编译通过不追认为组件注册通过。

## 显式依赖和缓存（新增实证）

`index-unity --manifest frozen.json --provider-python PY --out fresh`只从schemaVersion=1/files[{path,bytes,sha256}]清单读对象表/外部表，最多2000文件、合计1GiB；不是对象正文解析或全盘发现。PPtr按当前serialized文件的外部表与精确CAB/pathID匹配，重复CAB歧义不猜。

`hydrate-unity --source file.ab --texture-cache pool.json --provider-python PY --out fresh`接受schemaVersion=1/files[{logicalPath,path,bytes,sha256}]。当前仅Unity2021.3、单mip、单2D图的明确外部键；从`Assets/Textures/astc/<max-dimension>/<exact-key>.txt`精确读取ASTC，无网络发现或近似同名替换。验证原始hash、ASTC块/尺寸/长度，固定texture2ddecoder1.0.6一次解码BGRA→RGBA（不翻转），派生bundle写RGBA32。原CAB/pathID和全部非纹理对象raw hash保持；任何缺失阻止派生输出与后续Provider。

convert可重复`--dependency-source`，仅依赖清单及实际消费的缓存计入输入，复制原始证据至SourceRecovery。未知原程序集仍隔离，不因依赖齐全执行原方法。

- 冻结600个Bundle：600/600索引、79977对象表项、0失败；没有宣称79977对象正文已解析。
- 代表Prefab的3个Sprite PPtr从精确CAB找到，同依赖Bundle内3个纹理键在冻结103文件池中精确匹配。输出候选02实际输入5文件/529624B，deadbeef占位0；manifest SHA `96226025fd017ea4728f245c0a2cfcfaca71843e5b143a6c653bc6c2bda9b695`。
- 固定RGBA32策略导出3 PNG与规范解码像素hash全部精确一致。早期隐式ASTC解码比较有最大1 LSB差异，失败收据保留；没有放宽容差或追认旧输出。
- probe02普通C#标识符修正后，类实际注册、16 Sprite[]字段/几何/身份读回通过，3个源依赖尚空，saved=false；旧probe01失败保留。
- probe03独立Unity6副本own67435于2026-10-23T18:40:58.386769Z启动、18:41:04.978708Z exit0/reaped；16项严格检查通过，3个真实Sprite引用、MissingScript0、独立editable Prefab保存/重导/重载及引用身份保持，status=resource_subset_verified。公开convert本身仍只生成候选，此原生段为独立受控验证，不能声称公开`--native`已接通Unity来源。

完整启动Bundle缓存仅3/4匹配：`sharedassets1.assets`/pathID `4`需要`Assets/Textures/astc/512/pangzhijiangsi.a976bf1d.txt`，现有另hash同名不能代用。该轮blocked且未写派生bundle/启动Provider或Editor。启动106MB缺TypeTree、CODEPHPY保护方法、完整场景/视觉/业务及全Research逐项目输出仍未闭合。
