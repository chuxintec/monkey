# v0.6 模块执行登记

沿通用 MODULE-DEVELOPERS；主开发保持模型、公共IR/Schema/CLI/manifest/注册/依赖/版本/Editor单写。真实容量6，不满编；2个独立模块实例均已完成、空闲，默认Luna High；不为等待或报告新开工作。

| 模块 / 实例 | 目标 / 观测模型 | 基线与可写区 | 依赖 / 状态 |
|---|---|---|---|
| C1–C7/C9核心 / `/root` | 主模型保持 / 不推断名称 | 36e9d6d；code graph/semantic IR/生成接线与共享文件 | 928类/16,384方法静态图，3真实模块12方法编译/独立行为、2模块9方法原生、原JSON及隔离分发通过；源码8a536d3，50定向测试/20CLI烟测；原生段父唯一启动 |
| Unity来源与C5探针 / `/root/shader_profile` | 复用gpt-6-luna/high / 实际运行时未知 | 36e9d6d；unity_code_sources.py、unity_code_il.py、unity_code_candidate.py、code_native_probe.py及专用测试/文档/证据 | Mono合法夹具闭环已交付；探针修复与原JSON可选接线已交付；父补齐JSONSerialize/持久阶段并在窗口04完成9方法/Scene/事件/原JSON/解绑，exit0/reaped。子Agent不启动Editor |
| C8/C6候选增量与JSON / `/root/code_regeneration` | gpt-6-luna/high / 实际运行时未知 | 36e9d6d；code_regeneration.py、code_configuration.py、RecipeJsonConfiguration.cs及专用测试/文档/证据 | 已交付：深链/依赖指纹/dirty保护，原732行JSON及meta原样、运行时reader真实9叶验证；父UnityTextAsset原生读回通过；不做beaver人工工程采用 |

源码/证据在 `.private/v060-csharp-20261026/`；只在接口变更、阻塞、交付或窗口交接时通信，主开发集成后成版报告。以下保留v0.5原登记。

# v0.5 模块执行登记

执行 [通用模块开发规范](/Users/wangmeng/Documents/Manager/standards/MODULE-DEVELOPERS.md)；主开发持有唯一 PLAN、CLI/manifest/依赖及 Editor 资源调度权。当前实际平台总容量为 6，按就绪模块调度，不按授权上限满编。

| 模块 / 实例 | 目标 / 观测模型 | 基线与可写区 | 依赖 / 状态 |
|---|---|---|---|
| 全版关键路径 / `/root` | 保持当前主模型 / 不在本表推断运行时模型名 | e93de8d；05-D、Spine、共享接线、PLAN/验收/本地集成 | 05-D macOS 本地分发/隔离烟测通过；05-C 精确 schema 阻断；正式游戏/GREA/beaver 只读 |
| Shader 资源子集 / `/root/shader_profile` | gpt-6-luna/high（spawn 指定）/ 运行时未单独回读 | e93de8d；shader_profiles.py、RecoveredSprite.shader、UnityShaderProbe.cs、test_shader_profiles.py、SHADER-PROFILES.md、私有 shader-module 证据 | 完整精确源 Effect→原生资源→代表编译/固定视图；已交付：4 unittest、SDK 编译、Unity Metal 原生材质/像素通过；窗口已回收，停止产品文件写入；未直接比较源 Cocos 帧 |

首个独立模块，没有可复用实例。源产物与窗口回执留本项目 `.private/v050-continuation-20261026/`；模块交付后及时集成，仅版本出口/严重问题回报总监。
