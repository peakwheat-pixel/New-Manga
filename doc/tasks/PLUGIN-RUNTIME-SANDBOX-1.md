---
task_id: PLUGIN-RUNTIME-SANDBOX-1
kind: implementation
status: proposed
owner: 待指派
reviewer: reviewer-settings-a（非实现者）
created: 2026-10-23
base_commit: d603fd518065e933117a6b5ce9a4122093369ebc
depends_on: PLUGIN-RUNTIME-1
authorization: 待用户/Codex 明确授权（本文件仅提案，未授权前不实施）
allowed_paths:
  - src/infrastructure/plugins/**
  - tests/**
  - doc/tasks/PLUGIN-RUNTIME-SANDBOX-1.md
  - doc/handoffs/**
  - verification/PLUGIN-RUNTIME-SANDBOX-1/**
---

# PLUGIN-RUNTIME-SANDBOX-1 — 插件 OS 级沙箱（提案，未授权）

## 背景

PLUGIN-RUNTIME-1 review r1 P1-1 指出：`permissions: []` 目前只保证「Core 不授予能力句柄」，插件子进程仍以用户 OS 权限运行（恶意插件可自行读写文件/联网）。该边界已在 v1 诚实降级为「受信任的本地代码」并在 UI/文档说明。本 Task 是实现真正的 **OS 级隔离**，把 `permissions` 从声明式词表升级为可强制执行的能力边界。

## 候选方案（实施前需裁决）

| 方案 | 说明 | 代价 |
|---|---|---|
| A. Windows AppContainer + 能力 SID | 子进程放入 AppContainer，仅授予 manifest 声明的 capability（files_read/network 等） | 需要 Win32 API 绑定、ACL 配置、调试复杂 |
| B. Job Object + 受限令牌 | 低完整性级别/受限令牌，限制写路径与网络 | 粒度较粗，读权限仍受用户令牌影响 |
| C. 独立 helper 进程（Rust）+ 权限声明 | Hook 调用经 Rust 侧沙箱代理，Python 插件只接收已筛选数据 | 需重构 D1 隔离模型 |
| D. 维持 trusted-code + 仅在 manifest 声明权限时拒绝 | 无新实现，只强化文档 | 不满足设计 §4.3 的"无文件/网络/模型访问" |

## 验收（授权后填写）

- [ ] AC1 沙箱内读取插件根外文件失败；AC2 沙箱内联网失败（在声明 `permissions: []` 时）；AC3 声明权限的插件只有对应能力可用；AC4 崩溃/超时仍隔离；AC5 审计记录沙箱拒绝；AC6 UI 显示实际能力边界。

## Closeout Record

- Closeout：未开始（proposed，待授权）。
