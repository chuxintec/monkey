# v0.5 模块执行登记

执行 [通用模块开发规范](/Users/wangmeng/Documents/Manager/standards/MODULE-DEVELOPERS.md)；主开发持有唯一 PLAN、CLI/manifest/依赖及 Editor 资源调度权。当前实际平台总容量为 6，按就绪模块调度，不按授权上限满编。

| 模块 / 实例 | 目标 / 观测模型 | 基线与可写区 | 依赖 / 状态 |
|---|---|---|---|
| 全版关键路径 / `/root` | 保持当前主模型 / 不在本表推断运行时模型名 | e93de8d；05-D、Spine、共享接线、PLAN/验收/本地集成 | 05-D 本地分发收尾；05-C 精确 schema 阻断；正式游戏/GREA/beaver 只读 |
| Shader 资源子集 / `/root/shader_profile` | gpt-6-luna/high（spawn 指定）/ 运行时未单独回读 | e93de8d；shader_profiles.py、RecoveredSprite.shader、UnityShaderProbe.cs、test_shader_profiles.py、SHADER-PROFILES.md、私有 shader-module 证据 | 完整精确源 Effect→原生资源→代表编译/固定视图；已交付：4 unittest、SDK 编译、Unity Metal 原生材质/像素通过；窗口已回收，停止产品文件写入；未直接比较源 Cocos 帧 |

首个独立模块，没有可复用实例。源产物与窗口回执留本项目 `.private/v050-continuation-20261026/`；模块交付后及时集成，仅版本出口/严重问题回报总监。
