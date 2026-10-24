# v0.2 本地候选与分发验收

第一轮分发01已获总监独立认可；整体仍待有限动态布局续修及新分发回执复核。Grid/child-resize/线性缩放的续修已通过，见[有限续修](validation/2026-10-24-layout-followup.md)。本页下方包SHA属于保留的分发01，最新续修包将另列回执，不覆盖01。版本仍为 `0.2.0.dev1`，未推送、未创建tag或Release。正式远端v0.1保持冻结。完成的是工具的声明子集及交接出口，各游戏仍有明确partial/blocked，不能宣称所有引擎版本或完整游戏自动转换。

## 一条命令

```sh
bin/monkey convert --input-set /path/to/inputs.json --target both --out /path/to/fresh-output --offline
```

Cocos目标可选unity/cocos/both，其他源引擎统一unity6；默认格式none，显式 `--format grea` 在新输出应用typed迁移。使用已登记精确URL/版本/哈希获取远程文件时，按USAGE的acquisition manifest接入并去掉offline；未知CDN地址不猜。原生导入需独立新副本、确切已安装Editor及明确执行授权；静态候选不等于已可玩。一般partial退出1，调用者读取conversion-result.json，不能把exit1一概视为没有输出。

当前可执行范围及必要依赖见[USAGE](USAGE.md)、[支持矩阵](SUPPORT-MATRIX.md)、[逐case机器状态](validation/research-v02-status.json)。ASTC需已声明的可选 `texture2ddecoder==1.0.6`；Unity专用来源需既有固定provider。安装包不包含引擎、第三方provider二进制、原包、CDN资源或验证输出。

## 已闭合的版本要求

- 统一原包/输入集获取、逐文件字节台账和来源隔离，未知格式/方法保留明确限制与接续入口。
- Cocos3.8.7模板DAG、嵌套实例、局部ID和override，以及真实动态Label/Widget/Layout状态变化，两端原生代表闭环；布局集成同时核对资源与生命周期。
- 天命3.4.1专用资源/节点/位图字库/实例reader接公开双目标：同11962文件输入，7071帧、15字库、856图、22503节点、52关系。1份null旋转图拒绝猜值。实际新增7节点/1Widget两端原生表、模板对应与保存重开均闭环。
- 有原文证据的NumberLabel C#/TS优先/JS次选代码及实际绑定、新来源Parabola数值方法；unknown/异步/受保护方法不伪造实现。
- 默认none及可选grea保留typed身份/引用/动态key与人工边界；受影响既有证明复用，不重开全部游戏。

## 第一轮分发01与安装结果（历史认可）

源码提交 `6deb03e`，从228个Git登记文件的独立新快照构建。wheel共109条目、源码包226条目；全部104个包载荷文件逐字节匹配源码，源码包解出后重建wheel载荷一致。两包无.private/outputs/游戏文件/引擎或原生DLL。机器回执：[v02-local-delivery.json](validation/v02-local-delivery.json)。

制品在 `.private/v02-delivery-01/dist/`：

|制品|字节|SHA-256|
|---|---:|---|
|monkey_native-0.2.0.dev1-py3-none-any.whl|393326|819ab94fdcf09b6a2512d41a11f0f32a6498fbad8e15a401ce367dc02a11110e|
|monkey_native-0.2.0.dev1.tar.gz|598875|995f4703146e04edbbe18b9bd33b63e2f32726d7dab7a846d8d8fd959e22d376|

在全新私有venv实际安装wheel及原固定Pillow12.2.0；离线缓存未命中后仅从官方PyPI获取该固定版本，没有全局安装。Python3.14.7，仓库src不在sys.path；从独立cwd运行安装后的8条CLI，none/grea各双目标，四份静态verify均通过，输入哈希不变。最低声明Python3.11未另装解释器验证。ASTC extra和Unity provider没有纳入本次最小安装smoke。

完整230项工具检查通过，受影响49项通过，另25项最终接口定向检查通过。已通过的真实Editor helpers与包内代码字节相同；未为打包重复启动引擎。Research重新发现仍11例、10例不同范围输出、1例团结blocked、完整游戏0。原版视觉/真实交互/存档/业务、未覆盖格式和方法各按机器状态保留，不能用这些测试数替代游戏验收。
