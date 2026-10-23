---
task_id: GUI-PLUGIN-SANDBOX-SMOKE-1
kind: verification
status: blocked
blocked_reason: 手工 GUI 冒烟成本过高（慢/占鼠标/token），用户 2026-10-23 指示暂停；等待工具化检查方案
owner: dsh（本会话 Lead）
reviewer: （暂停，未进入 Review）
created: 2026-10-23
base_commit: d79e1a48063d66e43febe1df693bb83466dcbbdf
depends_on: PLUGIN-RUNTIME-PACKAGED-PYTHON-1
authorization: 用户 2026-10-23「1234都授权」（本 Task = 候选 1）
allowed_paths:
  - verification/GUI-SANDBOX-SMOKE-1/**
  - doc/tasks/GUI-PLUGIN-SANDBOX-SMOKE-1.md
  - doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/TASK_LEDGER.md（Lead 集成登记）
---

# GUI-PLUGIN-SANDBOX-SMOKE-1 — GUI 端到端插件沙箱冒烟（手工，暂停）

## 目标

在真实 Tauri dev 窗口中：启用真实插件（无权限 / network）→ 触发 `after_detect` Hook → 观察根外读/联网被拒与审计事件 → 截图。

## 已完成（evidence）

- [plugins-page-2.png](../../verification/GUI-SANDBOX-SMOKE-1/plugins-page-2.png)：设置 → Plugin/Hooks 的加载/拒绝/权限徽标/审计/安全说明。
- [workbench-run.png](../../verification/GUI-SANDBOX-SMOKE-1/workbench-run.png)：真实导入页面并启动 Run（检测 failed：dev 数据根无模型权重）。
- 详情：[smoke-notes.md](../../verification/GUI-SANDBOX-SMOKE-1/smoke-notes.md)。

## 未完成

- GUI 内真实触发插件 Hook 并观察沙箱拒绝 + 审计（需要检测模型权重，dev 环境未配置）。
- 安装包（NSIS/Tauri）内联冒烟。

## 暂停原因（用户 2026-10-23）

手工 GUI 检查太慢、占用鼠标、消耗 token；用户计划后续写一个软件检查工具替代手工 GUI 操作。本 Task 暂停，已获得的证据与复现步骤保存在 `verification/GUI-SANDBOX-SMOKE-1/`。

## 替代证据（沙箱行为已被真实测试覆盖）

- `verification/PLUGIN-RUNTIME-SANDBOX-1/probe-appcontainer.log`（`fs=BLOCKED, net=NET_BLOCKED`）、定向 pytest 10 例；
- `verification/PLUGIN-RUNTIME-PACKAGED-PYTHON-1/real-bundle-verify.log`（真实 bundle 解释器 + AppContainer Hook `real-bundle-sandbox-hook-ok`）。

## Closeout Record

- 未 closeout：`paused`（等待工具化检查方案）。
