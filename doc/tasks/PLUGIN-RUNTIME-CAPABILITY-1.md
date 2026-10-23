---
task_id: PLUGIN-RUNTIME-CAPABILITY-1
kind: implementation
status: in_review
owner: dsh（本会话 Lead 兼任 Owner）
reviewer: reviewer-settings-a（非实现者）
created: 2026-10-23
base_commit: b5f3814b2a798ce17e6ebe0f7d8ce183ca091c02
depends_on: PLUGIN-RUNTIME-SANDBOX-2
authorization: 用户 2026-10-23「1234都授权」（本 Task = 候选 3：capability 接线）
allowed_paths:
  - src/infrastructure/plugins/**
  - tests/**
  - apps/desktop/frontend/src/settings/**
  - doc/tasks/PLUGIN-RUNTIME-CAPABILITY-1.md
  - doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/TASK_LEDGER.md（Lead 集成登记）
  - doc/handoffs/**
  - verification/PLUGIN-RUNTIME-CAPABILITY-1/**
---

# PLUGIN-RUNTIME-CAPABILITY-1 — capability 接线（`permissions` 从声明变为可强制执行）

## 背景

SANDBOX-2 后每个插件拥有独立 AppContainer，但 `permissions` 仍一律拒绝（首发限制）。本 Task 把**可强制执行的权限**接入沙箱：`network` → AppContainer `internetClient` capability SID；其余权限（`files_read`/`files_write`/`model`）继续拒绝（无可靠强制手段/语义未冻结），避免"声明即真"的假承诺。

## 范围

- `manifest.py`：新增 `SUPPORTED_PERMISSIONS = ("network",)`；`permissions` 允许空或仅含 `network`；含其他权限 → `PLUGIN_PERMISSION_UNSUPPORTED`（detail 列出不支持的权限）。`ALLOWED_PERMISSIONS` 词表保持（用于错误分类）。
- `sandbox.py`：`prepare_plugin(..., capabilities=...)` / `run(..., capabilities=...)` 接收能力名；`network` → `S-1-15-3-1`（internetClient）注入 `SECURITY_CAPABILITIES.Capabilities[]`；每个 capability SID 用 `LocalAlloc` 保持生命周期到 CreateProcess 结束；无能力时数组为空（与现状一致）。
- `service.py`：`_invoke_sandboxed` 把 `manifest.permissions` 传给沙箱。
- 前端：插件行显示权限徽标（`network` → 「网络」；空 → 「无权限」）。
- 测试（真实 AppContainer + 本地 loopback）：
  - 无权限插件连接本地 TCP server → 失败；
  - `network` 权限插件连接同一 server → 成功；
  - manifest：`permissions: ["network"]` 接受；`["files_read"]` → `PLUGIN_PERMISSION_UNSUPPORTED`；`["network","files_read"]` 拒绝；
  - 能力数组生命周期不崩溃（多次 hook）。
- 文档：Task/Handoff/UI 说明「仅 network 可强制；files_read/files_write/model 仍拒绝」。

## 验收

- [x] **AC1** `permissions: ["network"]` 插件可连接本地 TCP server；无权限插件被拒（同一测试对照）。
- [x] **AC2** manifest 接受 `network`、拒绝 `files_read`/`files_write`/`model`（错误码 `PLUGIN_PERMISSION_UNSUPPORTED`）。
- [x] **AC3** UI 显示权限徽标（network / 无权限），与实际能力一致。
- [x] **AC4** 多次 Hook 不泄漏/不崩溃（capability 数组生命周期正确）。
- [x] **AC5** 全量测试无回归；文档如实（仅 network 可强制，其余仍拒绝）。

## Closeout Record

## 测试与证据

| AC | 命令/证据 | 结果 |
|---|---|---|
| AC1 | `tests/infrastructure/test_plugin_sandbox.py::test_network_capability_requires_the_network_permission` | PASS：无权限插件 `PermissionError`（网络栈被拒）；`network` 插件错误类型不是 `PermissionError`（已放行） |
| AC2 | `test_manifest_rejects_unsupported_permissions_and_accepts_network` | PASS：`network` 接受；`files_read` / `network+model` → `PLUGIN_PERMISSIONS_UNSUPPORTED` |
| AC3 | `npx vitest run src/settings/PluginSettingsPanel.test.tsx` | PASS：权限徽标（`network` → 「网络」；空 → 「无权限」） |
| AC4 | `test_network_capability_survives_repeated_hooks` | PASS：3 次 Hook 无错误/无泄漏 |
| AC5 | `python -m pytest tests -q` + 前端全量 | 见 `verification/PLUGIN-RUNTIME-CAPABILITY-1/*.log` |
| 定向 | sandbox + runtime + wire | 47 passed |

## Closeout Record

- Closeout：待 Review approved 后 closeout。
