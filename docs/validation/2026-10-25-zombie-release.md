# 向僵尸开炮导出核验与 0.3.0.dev1 发行

用户直接授权 monkey 测试、GitHub 发布和本地唯一 Release 入口。源项目只读，所有新导出和验证副本位于 monkey outputs；原件、私有证据和缓存不随发行包上传。

## 输入与实际导出

源为 Unity 2021.3.30f1 IL2CPP/Wasm，目标 Unity 6000.6.2f1。由公开 monkey CLI 重新解析启动包及 600 个冻结依赖，共 601 容器、81,580 对象，80,605 个可解析，975 个当时未解析（后续核查为 939 预算限制、36 结构读取失败）。7,595 份纹理原件及 248 份代码证据重新校验 SHA256。按原 game.js 的 DATA_CDN 和精确键补查，425 键仍返回 HTTP 404；7,626 纹理对象成功水合，426 缺失对象隔离且保留原件，不伪造像素。

固定 UnityPy 1.25.3 / AssetRipper 2.0.0，禁用源脚本执行。首次 provider 沙箱未启动本机接口，正常终止自有进程；第二次允许 loopback，exit 0 且已回收。实际输出 133,003 文件，随后由 monkey 组装统一布局、代码隔离和原输入留存。

最终 Assets 资源 37,635 个，37,582 个已有资源 GUID，53 份原始媒体等待 Editor 建立 GUID。包含 505 Prefab、3 Scene、1,566 AnimationClip、1,113 Controller、14,974 Material、7,554 PNG、172 TGA、9 MP3、14 JSON；Spine 651 个闭包成员，Shader 类型 124 个文件（保留 provider 序列化描述，不表示目标 Shader 编译通过）。27,727 份无序列化引用的原始二进制表等从生产 Assets 移至 SourceRecovery，不能把它们计作丢失，也不能宣称已全部转成正式 JSON。

## 内容核验

- 887 个冻结源文件及 7,595 份取得的纹理均逐字节留存，包括 13 份未引用纹理。
- 65,307 个非代码搬移文件与 provider 输出字节一致，meta 字节一致；14 个源字段代码/程序集定义单独核验。
- 4,179 个 Resources 路径保持原加载键。重复 GUID 和 YAML 文件内重复 local ID 均为 0。
- 7,727 个图片均能完整解码：7,602 个原导出图与外置 ASTC 规范解码像素 SHA 一致，74 个与源内置 ASTC 像素一致，5 个字体图的 Alpha8 通道字节一致，44 个原始媒体字节一致。另发现两张 provider JPEG 重编码差异（最大通道差 4 / 87），已在 monkey 中新增按精确 CAB/pathID 和水合 SHA 生成无损 PNG 的流程，保持 meta/GUID，并记录转换前后路径、字节和像素身份。JPEG 不能直接转存 PNG 冒充原图修复；只使用已验证源 ASTC。
- 14 个生产 JSON 均可解析；原始二进制表仍是恢复证据，未知格式未猜测转换。

312 项回归测试通过，包括缺失脚本引用统计、原始纹理漂移拒绝、PNG 目标冲突拒绝及无损像素/GUID 保持。

## 修正与限制

本次发现旧报告只计 provider 特殊占位引用。现新增对所有 YAML 资产 GUID 的核对：57 个缺失 GUID / 17,495 处引用，其中 55 个 GUID 来自隔离的 provider 脚本，其余是源缺件或待接入包；1,992 处特殊占位是上述总量的子集。完整路径、次数和保留的脚本 meta 写入 `Analysis/Tasks/full-resource-handoff.json`，`UNITY_ASSET_REFERENCES_PENDING` 会在转换结果明确提示。

代表 FrameSpritePool 叶 Prefab 已重新导出，16 个 Sprite[] 字段及依赖保留；原生验证在启动 Editor 前拒绝 settingsRaw=65 的紧密网格图集（现有 profile 只支持矩形图集）。没有降低检查条件：该样本原生保存重开、全量 Editor、Player、视觉、游戏业务均未验收。13 个具名字段类 / 57 字段及 20,129 份元数据声明初稿不包含原方法实现。

此版本作为恢复工具 prerelease 发布；资源候选不等于可运行完整游戏。肥鹅此前 Creator Tiled Sprite buffer 错误和少量 Unity 派生动画文件名长度问题也仍是已知限制。

## 分发与安装

版本 `0.3.0.dev1`，tag `v0.3.0.dev1`。仅工具产品源码、测试、文档、wheel/sdist 和安装脚本发布。安装脚本要求精确 wheel SHA256，将版本隔离到用户目录，校验成功后切换 current。唯一日常入口 `~/.local/bin/monkey`；仓库 `bin/monkey` 转发到相同 Release，显式源码开发使用 `.venv/bin/python -m monkey.cli`。

最终全量候选入口为 `outputs/zombie-release-lossless/UnityProject`。

完整机器证据在本地 `.private/zombie-release-20261025/`；发行身份和安装验收见其中 release/install 回执。完整原包和日志不进入发行包。

## 发布及安装实际回读

GitHub prerelease: https://github.com/chuxintec/monkey/releases/tag/v0.3.0.dev1 。发布产品提交 `3d0915b676e12927f532636f713bdf72659f6344`，源码 tree `037669123b2ff6b5efda8f57e41332b3c1f2cee4`。本节为发布后文档回执，不移动 tag 或替换附件。wheel SHA256 `16f4b62c9759b36628403eb489168806439ddc4c53b709600d1adab91f37f9ab`；138 产品文件在提交、wheel、sdist 与实际安装中一致。GitHub API / ls-remote 和实际下载附件已读回一致。

最终 frozen candidate：163,483 文件，3,307,505,149 字节；manifest SHA256 `ab8c00b29dd8a894ca6ba5e9af9df4b60c1be6fbc70ab06c5a6e1d4fa6862143`。全部清单文件重新计算哈希通过。7,727 图片分类核验为：7,604 外置 ASTC 精确 RGBA（含 2 个修复 PNG），74 内置 ASTC 精确 RGBA，5 字体 Alpha8 通道，44 原件字节；无未证明图片。五张字体图不以未定义 RGB 通道代替 Alpha8 原语义，仍不宣称材质/字体运行画面已验。

实际安装路径 `~/.local/share/monkey/releases/0.3.0.dev1`，PATH 唯一 `~/.local/bin/monkey`；仓库 bin/monkey 同样读取安装版。实际 Release 安装程序已从 GitHub 下载且校验 SHA；无 editable path。安装版在源码目录外的合成来源完成 Unity / Creator 两端转换和静态验证，并实际重新解析向僵尸 3,122 字节原包。

两份已被无损候选替代的全量导出在确认完整所有权与哈希后清理，删除逻辑大小 8,223,964,242 字节；manifest、转换结果与冻结回执留在 `.private/zombie-release-20261025/superseded/`。保留最终全量候选及当前可复验来源阶段，不触碰原游戏项目。
