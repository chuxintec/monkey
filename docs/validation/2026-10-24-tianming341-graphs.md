# 天命 3.4.1 原图与原生追加关系

在资源组的同一修订12/资源1.2.67输入上，实现独立的 `cocos-3.4.1-node-ui-v1`，不将源版本伪装为3.8.7。已逐项核对官方 v3.4.1 Node/UITransform/UIOpacity/Renderable2D/Sprite/Label/Widget/Layout、BitmapFont、PrefabInfo 与 prefab utils；共享实现只覆盖已核对一致的字段和默认值。SDK原文及SHA在私有 `cocos341-sdk-01/graph-sdk-complete.json`。

857份源图中856份可解析，22503节点、24511组件、52实例关系。另1份源图的实际旋转字段为四个null，保留 `INVALID_GEOMETRY`，不猜单位四元数。内嵌子节点建立稳定来源身份；重复局部ID按3.4.1 SDK遍历最后写入规则解析并保留碰撞记录，3.8.7严格保护不因此放宽。禁用UITransform仍保留尺寸/锚点与状态，Creator直接设置原生enabled=false；Unity没有可禁用的RectTransform，明确报告其父变化监听生命周期待人工复核。3.4.1命名fntConfig接位图字库，不改原件。

## 真实追加结构双端闭环

4个实际owner包含1个追加Widget组和7个追加子节点组；加入精确模板闭包后共6份Prefab、331节点、44源SpriteFrame、1位图字体、8实例关系。原版SDK的处理顺序为追加子节点→移除组件→追加组件→属性override；当前实际没有移除案例，移除组件仍明确拒绝，没有宣称已实现。

- Unity `tianming341-mounted-integration-04-unity-native` own95278，06:11:10–06:11:21 UTC，exit0/reaped，严格0诊断。源Prefab、最终Candidate.prefab分别重开校验原生追加记录；Scene再核对它实际继承的Candidate资产及对应对象与SHA，避免把Scene继承的组件错误当成Scene自己新增。8条Scene证明和8条Candidate证明，7新增根/7节点/1组件，模板未污染。原业务缺口使editor层仍为partial。
- Creator `tianming341-mounted-integration-10-cocos-native` own3121，06:30:09–06:30:31 UTC，正常TERM/reaped，严格0诊断/editor pass。使用原生MountedChildrenInfo/MountedComponentsInfo、编辑器mountedRoot及组件fileID；SDK默认序列化会丢弃可同步实例下被追加表引用的组件，因此仅有追加组件时启用其 `reserveContentsForSyncablePrefab` 选项。原生PrefabInfo/实例记录保留，重开展开后精确UUID/fileID、追加表实际对象、父子关系及模板SHA均通过；不修补序列化JSON，不运行原版JS。

机器回执：[tianming341-native-mounted.json](tianming341-native-mounted.json)。Creator04类型前缀错误、05–08保存后缺Widget、09保存前null保护失败及Unity02/03错误验收层级均保留，未当成功。源脚本/未知组件、完整游戏交互、视觉和整包原生未验。49项受影响检查通过；真实追加类型只验证本组Widget和单节点子树，不外推所有组件/任意嵌套追加。
