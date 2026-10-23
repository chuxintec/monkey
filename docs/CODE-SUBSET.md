# 可接续代码子集（v0.2开发中）

```sh
monkey code-model --source original-module.js --module-name NumberLabel --out fresh-facts
monkey code-emit --source original-module.js --code-model fresh-facts/code-model.json \
  --numeric-field value --namespace my-game --cocos-code-language ts --out fresh-code
```

默认TypeScript；JS为显式次选。只生成可证实的普通同步实例字段setter/getter，arrow/async/generator不误判this。渲染前重新静态解析并核全部事实，篡改模型/源/重复owner与危险目标名拒绝；原JS从不执行。

`--numeric-field`明确限定number调用子域，不是断言所有JS动态值都是数字。C#double?未初始化没有值，对应TS undefined；负零/NaN/Infinity在该子域内保持，JS null/string/object/省略参数仍在合同外。未知方法原文/范围/哈希和具体待补状态留SourceRecovery及code-contract，不能用空成功替代。无源级Label声明的普通类只发状态类，不能凭名字生成引擎组件。

只有RF原名/身份、IIFE cc.Label参数、构造别名和方法作用域吻合时，才生成显式Label/TMP表现适配。原继承/decorator helper并未执行或恢复；有限Label字段projection拒绝丢弃未知序列化业务字段。原`_N$overflow`精确读取，冲突拒绝；数字小样的SHRINK用明确baked静态呈现，动态缩字不算恢复。

`code-emit`可以单独输出代码子集；包级`convert --numeric-code-contract numeric.json`已接入相同发现/生成/组件投射/双目标导出链。它不自动补齐所有方法。Unity脚本GUID和默认TS脚本UUID由namespace+源身份确定、独立于目标路径；Creator TS meta4.0.24来自实际3.8.8导入回读。固定meta的新输出仍须真实验证；JS importer metadata尚未实证，包级绑定明确拒绝js选项，独立code-emit仍可生成次选JS证据。

## 包级单命令

```sh
monkey convert --input-set inputs.json --target both --out fresh \
  --numeric-code-contract numeric.json --cocos-code-language ts --format grea
```

`numeric.json`为明确调用子域声明，字段如下（moduleSha256替换为静态恢复模块原始字节的完整SHA256）：

```json
{
  "schemaVersion": 1,
  "kind": "numeric-call-subdomain-v1",
  "moduleName": "Meter",
  "registrationId": "original-rf-identity",
  "moduleSha256": "exact-module-sha256",
  "numericField": "value"
}
```

当前一次声明一个源级Label类/数值字段与唯一setter/getter。CLI自动在本次原包静态恢复结果中唯一匹配RF身份/原名，重核模块SHA/方法事实，生成C#/默认TS，按全部原组件身份建立绑定；未知序列化业务字段、重复模块/owner、非Label继承或缺失getter/setter会停止声明分支，不退成“声明成功”的基线工程。原始声明/模块/待补方法均保留工程内部。`--format grea`只移动明确脚本路径和报告槽，GUID/UUID保持；已有代码投射包的resume/reuse暂拒绝，保留旧候选。可加`--native`及编辑器参数顺序实导。

公开单命令合成native01完成7输入/1原组件：Unity own78528于2026-10-23T20:57:53.848046Z→20:58:04.054183Z exit0/reaped；Creator own78894于20:58:04.082896Z→20:58:20.932724Z正常TERM exit-15/reaped。两端严格回读0差异、生成类实际注册/原组件绑定、负零/NaN/Infinity/未初始化、文本引用、Scene+独立Prefab保存重开通过；Unity editor partial保留未实现方法，Creator资源editor pass。它验证自动包级链，不能替代下方真实5组件分母，也不代表业务完成。

## 实际NumberLabel证据

源及5原组件映射见V0.2-EXAMPLES.md；6方法中2个实现、4个pending。C#真实编译通过；TS5.8.2+Creator3.8.8公开SDK对target启用strict，错误字符串调用TS2345拒绝。上游SDK本身82项full-strict声明错误单列，skipLibCheck只隔离这些声明，不放宽target。

- Unity probe05：own70833，2026-10-23T19:23:17.534061Z→19:23:27.140130Z exit0/reaped。MainUi129节点/原Prefab GUID不变，MissingScript0；5实际TMP/原字体/字串引用、数字边界/实例隔离、未初始化态、保存重载及全部节点几何保持。原件SHA保持；初始3轮失败因缺TMP投射、TMP Settings隐式资源和无Canvas字形测量分别保留。字形在隔离active Canvas clone验证，不改原树。
- Creator TS native01：candidate03 SHA804703d0010a88fc25608e2fa519b3d94e7785e1a391cef3ba7c2a544685cd7c。own71766，19:28:21Z→19:28:41Z正常TERM exit-15/reaped，editor pass/诊断0。实际注册NumberLabel，Scene和独立Prefab共129源节点/同5原组件，原字串/字体引用/完整geometry与数字边界/状态隔离保持；重载5个getter为undefined，4未知方法未绑定。
- Creator实际初始自动分配脚本UUID86325443-58b5-4b92-b0e4-bc27ec362d46、classId86325RDWLVLkrDkvCfsNi1G，TypeScript meta4.0.24。此自动分配结果不能作为跨新工程/格式恒定身份承诺；后续固定meta用明确新输出验证，不追改该冻结结果。

以上是原生资源接线与数字方法子集，不代表数字动画/SHRINK动态行为/原版视觉/输入/可玩已通过。
