# v0.6 C# 合并版续推验收（本地）

2026-10-26。执行 C1–C9 和 `monkey-v06-delivery-gap-correction-20261026-01`。保留首候选源码 `8a536d3` / 验收 `de7c556` 及原包，不用续推结果重写旧验收。当前开发版本仍 `0.6.0.dev1`；新分发单独编号02。此文记录开发方本地验证，独立总监验收另列，不代表 GitHub Release、全版本引擎或完整游戏恢复。

## 三项审阅差额的实际结果

| 差额 | 实现和验证 | 保留边界 |
|---|---|---|
| 只有固定12方法profile | 新增 `code-select`：精确入口→已审类型/依赖闭包→真实 emitter lowering→裁剪合同→现有 `code-emit`。有界选择不执行源；区分缺源、缺类型/依赖合同、未支持语义。新数学profile3根自动加NormalizeAngle；原FindDish入口自动加IsDish/GetRecipeOf | 显式类型证据仍由开发者审阅；未选择方法不判为不支持。每次最多256方法含见证，不是恢复率配额 |
| 僵尸已有segment/map未消费 | 独立扫描WASM函数边界/类型签名，核metadata v29行/token与map、原body偏移/长度/hash；显式Brotli provider验证压缩包与现有segment逐字节相同。8个纯i64运算自动生成C#片段、已编译和自有fixture行为通过；公开CLI再次输出相同片段 | map的metadata方法→函数索引仍是caller-map，未解析codeRegistration/独立build ID；不称完整原FP/波次模块已恢复 |
| 缺Unity可操作出口 | 复用原12方法/JSON证据，新增独立Editor测试窗口。6次CUA系统指针MouseUp完成Start→Damage→Heal→Combo→Recipe→Stop/Reopen。回调、JSON9叶、销毁解绑及保存引用身份通过，Editor exit0/reaped | 新测试UI/adapter/lifecycle不称原版UI或原生命周期；无原游戏执行、真实账号/服务器、Player或视觉一致性声明 |

## 肥鹅：合同、生成和行为

完整源7,147,892字节，SHA `21af08e48846f6ad1a2e0673b0c945358136723b1664f0cd1f6ec9b3df6c5cb5`；静态图2,033,299 AST节点、928类、16,384方法（原有完整图证据沿用）。新 `foodstreet-motion-math-v1` 4方法是 NormalizeAngle、UnwrapAngle、Distance、Clamp；目标普通Number/Point2 C#，仅新增确切 `Math.sqrt` lowering，不含cc.v2或源引擎。

- 新4方法候选编译及独立预期行为通过：±180边界、多圈、跨零连续角、负零、NaN、3-4-5距离、同点、binary64溢出、正常及反向Clamp。
- FindDishOrderDemands裁剪3方法候选编译及已知/缺失recipe、原输入不变检查通过。Recipe.ingredients由同源 `method@621011` 的精确hash/AST见证，但该方法不计入这次生成；伪造/省略见证拒绝。
- 经 `code-select` 和 `code-emit` 实际组成4模块16方法/原JSON的同版本候选。整组再次编译；原OrderRules、RecipeCatalog、HealthState、CodeCollections、RecipeJsonConfiguration代码字节与首候选一致，沿用原12方法行为及原生证据。新数学入口在合并程序集再次通过。
- 分母：16/16,384已生成并编译，16,368未选择；16个方法的行为证据由旧12+新4组成，9个实际Unity绑定方法继续是独立子集。不能称全部可解析方法已经类型化/可转写。helpers、shape见证、3方法裁剪重复不刷新方法数。

源HealthState是原ECS模型，生成状态构造与Unity桥是显式适配。原 `onHpChange` consumer `method@3177644` 已有源码，SHA `198935ebd7d852ca7ae2495b17a0100eb4a6770f2ca8086daa1f3230cb1b7caf`，但decorated/inherited owner未解析，选择结果是 `CODE_SELECTION_CLASS_UNRESOLVED` / unsupported，不是missing_source；没有恢复其原hpBar/实体生命周期。

## Unity实际操作

独立 `UnityInteractive-04` 使用 Unity6000.6.2f1。6次系统指针操作后：Damage HP79/回调1，Heal HP89/回调2，Combo1/回调1，原JSON查询9叶顺序匹配；销毁adapter后两个源delegate均null。退出Play Mode后重开场景，脚本/UnityEvent/TextAsset GUID-localId等绑定串相同。原表仍732行、运行时JSON唯一数值真源。

receipt SHA `fcbe85ed1b37cdd5b958d810b15e6d6ebc0de779063fbc2700add229d024e265`；scene SHA `fcdf06619f67d4227b8e4d6239d6686a24bb268a0f5d1fd5959f431d0efca465`。失败01/02/03保留：domain reload状态、离线不可访问API、PlayMode过渡提前开场景分别修复；02未启动Editor。最终04正常退出，无重跑旧自动原生链。系统指针由CUA发出，不能写作人类物理输入或原游戏UI验收。

## 向僵尸开炮：补正来源结论

只读现有冻结材料，正式项目保持暂停。原报告仅核压缩文件所得metadata_only不能外推到所有可用输入。

| 来源 | 字节/SHA256 |
|---|---|
| segment0 | 31,328,237 / `81cebd06900cd8121387b5744e93f8ae9e59fc44029366704475d2a18a0bc1b9` |
| segment1 | 40,875,170 / `8e7ed54e1b47c2a525b214edb88d2bb57b8dfb205d189e51f010cba76bc742de` |
| selected-method-map-07 | 252,609 / `2ef178a04976d436a4442f7e3b45de6e2eedfe72fe3adb17407b03472cc4c71d` |
| 原metadata v29 | 20,251,452 / `44d6b987151c5d3ca6767221af4ec01b89ce03284dd5a048b961aa03dc20ae62` |

两压缩源SHA分别 `18d2865ee62aef660b34bcf2a63effdc4360fde6273329d7b01d7542f1ef4759`、`04f68ac1539ce483f99a7746e11fffd0e6d84742a2ddda1383b040efa7e6995d`，显式Brotli1.2.0静态解码逐字节对应上表。不同20,244,688字节同事metadata已排除。NORMAL-WAVE文档声明map07；WAVE-TRIGGER声明旧map hash，虽13行身份/body匹配，也不称文档map hash一致。

17个选定FP body中仅8个完整纯i64算术/有符号比较模式符合本版自动lift：加减unchecked环绕、==、!=、<、>、<=、>=。片段SHA `c803643e9c977cf6ec889289e3d6eb2a360c3db6a93cdd7affe598d215a2aa40`；自有raw-long宿主fixture编译/运行通过，保留CS0660/CS0661（Equals/GetHashCode没有伪造）。片段不能独立代替完整FP类型，宿主字段和caller-map绑定仍需采用者独立核验。

另13个波次/触发body均精确核验但0转写。例如 `NewMonsterRefresh.Start` 44B的load/store偏移56/8/40/24/16/32已有证据，缺逐字段layout map；Stop的9B写偏移24同理。更大方法含懒初始化、未具名直接/间接调用及内存操作，逐方法列bodyFeatures/unresolvedCallFunctions，禁止套手写移植或伪代码。跨segment函数索引不混作调用身份。

## 测试、分发与所有权

本轮26个不同定向用例通过（首轮24，后增混版本/重复报告与新profile2例；新守卫关联8例复测），另新候选离线编译/行为、真实CLI和Unity实际操作按上文分别记录。原50用例/旧自动窗口不重复跑。无全库/全资源重导。

新源码和不可变快照分发02的精确commit/文件清单、wheel/sdist及隔离安装hash写项目内 `.private/v060-csharp-continuation-20261026/distribution-02/` 与总 `delivery.json`，分发完成后在PLAN补记结果。首候选制品原样保留；日常0.4、v0.5、输入、正式游戏/GREA/beaver不改；无GitHub推送/Release/全局安装。此本地交付支持已声明的类型/语义子集，不承诺全部源方法、未知异步/继承/反射、36正文、完整玩法或其他未运行平台。
