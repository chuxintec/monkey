# full07原生差异与成组修复

Unity实跑副本outputs/acceptance/full07-window-01/UnityProject，原生方法613.60秒、own86974正常exit0已回收。真实1694独立Prefab保存重载计数、24784节点、16934Sprite、Missing Script0、Scene重开和editable roundtrip完成；字体10/计划16，回读38,845,894字节，聚合Prefab42,815,767字节。旧32MiB回执/文件读取限制已分别改为128MiB/8m节点的生成回执预算与流式SHA；原始输入JSON预算不变。离线2005诊断是几何613、字形834、View557、ProjectVersion正规化1，未宣称还原通过。

## 根因与修正

- Creator首次导入5份fnt找不到邻接页图。own91737在09:43:08Z正常TERM exit-15已回收，未调用原生方法；副本full07-creator-window-01冻结。将bitmap atlas与对应fnt一同映射到assets/fonts，保持资产UUID和原名，fnt引用精确邻接basename；合成bundle→normalize→plan→export→standardize测试验证实际页图存在、SHA与静态检查。
- Unity557个SPRITE_MISSING全部对应源spriteFrame=null。JSON原生空串与null不同，改用IsNullOrEmpty生成禁用但可编辑的原生Image，仍不伪造图片绑定。
- 父pivot配置依赖源节点次序：例如BtnYellow的父#11晚于子#2，父源pivot[.5,0]，旧实现读到尚未配置的[.5,.5]，额外引入450坐标差。改从父NodeSpec直接读取pivot，不改变源数据；disabled Widget也不再套用stretch。剩余真实布局差异须复验，不提前归零。
- TMP GetPadding非SDF分支额外返回1个atlas像素。按已有回读与此原生实现离线计算，702个位图Label墨迹范围完全匹配，133个隐藏Label无可比网格（834错误含701个padding差异及133个无网格；另1个原通过）。新回读记录实际ShaderUtilities padding与character scale，严格从quad计算ink，不改容差；隐藏Label以独立激活clone测量，不激活保存树。新证据尚待Editor，旧回读不伪改通过。
- 6份未被页面使用的TTF给TMP传空字符集返回false。新适配跳过空字符请求，保留引用原字体的动态TMP资产；有字符的字体仍烘焙静态，均无系统fallback。
- 缺失可转换Label的Outline明确handoff；不能以源中有Label对象就宣称原生描边可应用。
- ProjectVersion只允许精确6000.6.2f1及合法同版本revision注释；未知字段、重复键和其他版本仍拒绝。
- 保存树回读一次建立源ID→真实RectTransform映射，避免每Label/View反复建立全量字典；组件构建每128项检查预算/引擎错误。

20项定向检查通过，3个Creator JS语法检查通过；修改后的C#原生API编译通过，均非Editor验证。计划生成全新full08并顺序原生核对，full07候选/实跑工程/截图保持冻结；20重复Layout继续明确待适配。
