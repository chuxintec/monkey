# 同事交接中的通用证据能力接入

2026-10-26；monkey 0.5.0.dev1，本地开发。本轮在人类授权范围内只写monkey，原包、游戏与其他工具工作树只读。原生核验总监turn `01a17684-3487-7890-a76a-33bc95bf9f91` / human `01a17684-35f6-7ed2-a252-2f7f73d2898a`；事件 `monkey-colleague-recovery-intake-20261026-01`。

## 来源与实际差异

完整读取以下三个小脚本及对应manifest/方法映射格式，保留原件到本项目.private，没有导入执行：

| 包内源 | 字节 | SHA256 |
|---|---:|---|
| Tools/Query-Methods.py | 928 | `4877d5f51387548d7830b2ab2c86ef783fcd6e93aa1b9b3a05d85c99aa712e64` |
| Tools/Query-Tables.py | 1,146 | `4b653bc08389e62645b0ece30bed8a90b4b6165a2b9d4825870e9c5db3c57fff` |
| SourceEvidence/AdapterSources/iter_original_methods.py | 567 | `df1dab33b477f602df6115c6cf33deb06a6d9dd1d23f802a54b6474e1850d295` |

接收来源ZIP的交接声明SHA为 `f3387ecedb9820ae664a731644cc2a427da86ba5b464bef9f165333c455d2a9c`、2,287,341,755字节。完整大包核验由僵尸接收者集中执行，本consumer未重复哈希/解压整包；直接ZIP读取自己所需条目并核CRC、内清单所声明的完整SHA。包内Manifests/files.json本轮读取SHA `e3e246a598913d516736eb25a757b08b1eed0113b88e21d981a5a77503607734`，不把内清单未自列的文件视为已被其认证。

实现是基于机制的独立增量，不按对方项目源码许可直接复制：

- `evidence_stream.py`：复用safe、RootReader、严格load和预算；64KiB流式UTF-8/BOM JSON数组/信封读取，补完整定界、重复键/截断/尾随数据拒绝；逐字节SHA校验到EOF，结果limit不绕过尾部验证。
- `evidence_queries.py`：`query-methods`保留原module/function/token/slot与字段，只读定位；`query-tables`核整个选定嵌套ZIP、清单完整条目身份和单表字节；`inspect-aliases`保留精确URL与内容SHA/大小，只核显式选择的内容，拒绝近似/版本猜测及身份冲突。
- `unity_code_handoff.py`：既有schema1/SourceRecovery流程新增method-map、decoded-table-manifest、resource-alias-index、adapted-binary角色；适配模块必须声明同清单中不同哈希的原source-binary。原始/适配字节分开，manifest派生关系不升级成方法行为或二进制等价证明。
- CLI/capabilities/用法实际接通；没有新增Unity/Cocos/Laya等引擎profile，没有生成产品运行框架或启动工程。

## 真实包验证

3个公开开发CLI入口均直接从本包验证通过，输出都在monkey自有.private：

| 验证对象 | 实际结果 |
|---|---|
| 方法映射 | 49,026,542字节、174,526映射行完整流式扫描/哈希通过；精确module+function查询命中1行；methodBodiesRecovered=0 |
| 嵌套表 | 6,361,390字节清单含27,454变体；58,865,851字节内层ZIP完整SHA/CRC通过；查询保留display/fp等变体，提取一份44,686字节原表并核SHA；未展开整个表目录 |
| URL别名 | 22,020,748字节路由清单，69,463精确URL→34,003内容身份、33,968共享别名组；选中内容有2个别名，512字节实际载荷SHA通过 |
| 原主模块 | 本包SourceEvidence下40,314,476字节，完整成员SHA `80a22c512328fe647f8a8e65f6616bc5efb5c590cf39c75bf2e9f40e0e640ce2` |
| 适配主模块 | RuntimeAuthoring下40,309,128字节，完整成员SHA `e1d3418251a64ec3ed5d5a5f6872e29ffeca6380300ca24dd5ba678ed543eb8e`，不同于原模块；名字含original不作为原版证明 |

两个WASM仅核文件头及完整内容身份，未执行、未反编译晋升C#、未声称规则等价。方法/反编译格式与原程序集签名分别保留，没有把174,526映射行算已恢复方法，也没有把27,454变体算独立业务表。

`selection.kind=zip-member` 的verified只指所选成员字节，明确containerHashVerified=false；外层包完整验收应引用独立回执。角色/哈希不同、缺失清单和错误别名不以“已有路径”或近似哈希跳过。

## 测试、分发与限制

- 全套349项测试通过（14.741秒）；新增10项覆盖UTF-8/分块/严格JSON、尾部SHA、module身份/大整数、嵌套ZIP与表变体、篡改/路径/链接/冲突、精确别名、适配来源关系、CLI。最终成员验证层字段补充后，相关14项定向测试再通过。
- 原inspect/normalize源合同SHA保持不变；这组查询/证据角色没有触发已有原包解析缓存失效。
- 用本项目已有固定setuptools84.2.1后端离线构建wheel（开发venv本身没有build/setuptools，前两次准备失败日志保留；未安装新依赖）。wheel共156文件，544,200字节，SHA `46ca2e1a21386c6660e0d339a4327821ccb37d80bdd6a4692fa18b69cdf712a4`；独立目录从解包wheel导入并实际query-methods成功。wheel不含.private、交接工具、游戏源码/素材/WASM。日常PATH仍monkey0.4.0。
- 未采用WebView2/C++宿主、原WASM运行层、307/309启动构建、赠钻/体力/掉落/本地存档与经济政策；其职责/来源与原生Unity恢复不同，不作为通用inspection。未发布/推送/全局安装，未开启Editor或运行原游戏。静态通过不等于可玩/视觉/Player通过。
- 05-C剩余36对象/图集/Tiled/动画名/Spine/Shader、05-D其他统一诊断仍待实施；本批是有界证据定位增量，不代表v0.5完成。beaver采用快照db253cb及其源归档未改写。

完整私有回执在 `.private/colleague-intake-20261026/`：input-identities.json、real-validation.json、cli-validation.json、source-contracts.json、tests-final.log、tests-targeted-final.log、distribution-final.json及源脚本/表清单/单表。原包未全量复制，也没有将真实数据作为公开fixture。
