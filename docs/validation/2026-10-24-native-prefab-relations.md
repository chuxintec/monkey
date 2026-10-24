# Cocos 3.8.7 → Unity 6 原生 Prefab 关系

本组开发期解析精确模板 UUID、嵌套局部 ID、propertyOverrides、ValueType 子字段、数组及 targetOverrides，并记录无法从原包确定的脚本构造默认值。模板 DAG 和实例对象对应接入公共 normalize / plan；IR 不进入 Player。缺模板、环、预算及当前未覆盖的 mounted/removed 结构显式报错，不替换近似模板。

目标侧用 Unity PrefabUtility 实例化已保存模板、保存原生嵌套 Prefab 和 Variant；逐节点校验 GetCorrespondingObjectFromSourceAtPath，读回实际 GUID/fileID，保存前后模板 SHA 不变。原生引用在替换临时构造节点后重绑定；不复制 Transform 的内部层级数组。

- 合成候选 `outputs/cocos387-prefab-relations-fixture-03`，原生副本同名 `-native`：Unity 6000.6.2f1，own PID48567，2026-10-24T03:23:04Z–03:23:15Z，exit0/reaped。15节点、4Prefab、6原生关系；Regular×3、Variant×1，双实例不同覆盖、三层嵌套、源节点对应和模板未污染保存重开通过。
- 真实候选 `outputs/cocos387-prefab-relations-real-01`，原生副本同名 `-native`：own PID40110，02:52:51Z–02:53:11Z，exit0/reaped。CookSoupTaskItem、battleRewardItem、GoodsItem、starGroup，共104节点、4Prefab、5关系；Scene及独立Prefab保存重开对应和原资源引用通过。986源帧继续复用。当前全部Regular。
- 上述两次严格原生检查零诊断；Editor总体partial是原包未知脚本/有界转换范围，不等于玩法或视觉验证。动态Layout/Widget/Label与Creator原生关系仍待下一组实现。
- 首次合成失败01保留：内部Transform层级引用重映射造成重复链接；已停止并离线修复，新的02/03通过。没有改写失败记录或冷重复同一产物。
- 23项定向检查通过：`test_cocos38_prefabs test_cocos38_graphs test_structured test_prefab_spine_preflight test_unity_formatting`。C#同时以已安装Unity SDK编译通过；GUI/TMP引用来自安装模板libcache，不依赖其他项目或已清缓存。

完整119源图静态结构试读114图可解析，5图缺6个精确模板。未知构造字段/失效覆盖端点保留显式gap；不宣称所有组件或全部图原生验收。原件和共享模板不修改，Creator关系图暂显式阻止输出以免扁平化误报成功。

实现依据：原包元数据及官方 Cocos v3.8.7 `cocos/scene-graph/prefab/utils.ts` / `prefab-info.ts` 的序列化合同（MIT，Chukong / Xiamen Yaji），仅作行为研究，未复制引擎实现到目标Player。原出处及SHA在私有 `official-baseline/manifest.json`。Unity目标行为使用已安装6000.6.2f1官方API；独立生成代码不包含Cocos运行时。
