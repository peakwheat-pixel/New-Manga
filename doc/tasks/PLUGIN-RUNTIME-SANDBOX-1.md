---
task_id: PLUGIN-RUNTIME-SANDBOX-1
kind: implementation
status: in_review
owner: dsh（本会话 Lead 兼任 Owner）
reviewer: reviewer-settings-a（非实现者）
created: 2026-10-23
base_commit: 1a17decf1
depends_on: PLUGIN-RUNTIME-1
authorization: 用户 2026-10-23「1」（选择候选 1 = 本 Task）
allowed_paths:
  - src/infrastructure/plugins/**
  - tests/**
  - doc/tasks/PLUGIN-RUNTIME-SANDBOX-1.md
  - doc/handoffs/**
  - verification/PLUGIN-RUNTIME-SANDBOX-1/**
---

# PLUGIN-RUNTIME-SANDBOX-1 — 插件 OS 级沙箱（AppContainer）

## 背景

PLUGIN-RUNTIME-1 review r1 P1-1 指出：`permissions: []` 目前只保证「Core 不授予能力句柄」，插件子进程仍以用户 OS 权限运行（恶意插件可自行读写文件/联网）。该边界已在 v1 诚实降级为「受信任的本地代码」并在 UI/文档说明。本 Task 是实现真正的 **OS 级隔离**，把 `permissions` 从声明式词表升级为可强制执行的能力边界。

## 裁决（2026-10-23）

采用 **方案 A：Windows AppContainer + Job Object**。可执行性探针（`verification/PLUGIN-RUNTIME-SANDBOX-1/probe-appcontainer.log`）证明：AppContainer 内 `python -I` 可正常执行，**读取插件根外文件被拒**（`BLOCKED`）、**联网被拒**（`NET_BLOCKED`）；给 Python 运行时（解释器根 / DLLs / Lib）一次性只读 ACL、插件目录 RX、数据根两级 traverse 后，合法 Hook 正常返回（prepare 2.0s 一次性，run 0.06s）。

实现要点：
- **共享容器**（`NewMangaPluginSandbox`）：解释器 ACL 只授一次；插件隔离靠目录 ACL（跨插件读不在 v1 威胁模型，后续可收紧）。
- **Job Object + KILL_ON_JOB_CLOSE**：进程树随 Job 关闭/超时全灭。
- **非阻塞管道泵**（PeekNamedPipe 轮询）：挂起插件永不会阻塞 Core 读取线程。
- **失败即 fail-closed**：`SandboxError` → `PLUGIN_HOOK_UNAVAILABLE` + `plugin_error` 审计，绝不同时回退到无沙箱执行。
- `permissions: []` 时容器**无任何 capability SID**（无网络）；带权限插件仍在 manifest 层拒绝（本轮不放开）。

## 候选方案（历史记录）

| 方案 | 说明 | 代价 |
|---|---|---|
| A. Windows AppContainer + 能力 SID | 子进程放入 AppContainer，仅授予 manifest 声明的 capability（files_read/network 等） | 需要 Win32 API 绑定、ACL 配置、调试复杂 |
| B. Job Object + 受限令牌 | 低完整性级别/受限令牌，限制写路径与网络 | 粒度较粗，读权限仍受用户令牌影响 |
| C. 独立 helper 进程（Rust）+ 权限声明 | Hook 调用经 Rust 侧沙箱代理，Python 插件只接收已筛选数据 | 需重构 D1 隔离模型 |
| D. 维持 trusted-code + 仅在 manifest 声明权限时拒绝 | 无新实现，只强化文档 | 不满足设计 §4.3 的"无文件/网络/模型访问" |

## 验收

- [x] **AC1** 沙箱内读取插件根外文件失败（真实 AppContainer 进程；插件捕获后返回 `BLOCKED`，不泄露内容）。
- [x] **AC2** 沙箱内联网失败（`permissions: []`，无 capability SID）。
- [x] **AC3** 能力映射存在但**不放开**：`CAPABILITY_SIDS` 支持 `network`（`S-1-15-3-1`），manifest 层仍拒绝非空 permissions（首发限制不变）；测试覆盖"带权限插件不可加载"。
- [x] **AC4** 崩溃/超时仍隔离：超时 kill 进程树（Job Object + PeekNamedPipe 泵），主链路不阻塞。
- [x] **AC5** 审计：沙箱拒绝/失败 → `plugin_error`（fail-closed 时 `PLUGIN_HOOK_UNAVAILABLE`）；成功 → `hook_invoked`。
- [x] **AC6** UI 文案与实际能力边界一致（AppContainer 沙箱已启用；无新增假控件）。

## Closeout Record

## 测试与证据

| AC | 命令/证据 | 结果 |
|---|---|---|
| AC1 | `python -m pytest tests/infrastructure/test_plugin_sandbox.py -q`（`test_sandbox_blocks_reading_files_outside_the_plugin_root`） | PASS：容器内读 `../top-secret.txt` → `BLOCKED`，`data` 不泄露 |
| AC2 | 同上（`test_sandbox_blocks_network_access`） | PASS：`socket.create_connection` → `NET_BLOCKED` |
| AC3 | 同上 + `test_core_plugin_wire`（带权限插件拒绝） | PASS：`CAPABILITY_SIDS` 就绪但未接线；manifest 仍拒绝非空 permissions |
| AC4 | 同上（`test_sandbox_kills_a_hanging_hook_within_the_timeout`） | PASS：1s 超时 kill 进程树，主链路不阻塞 |
| AC5 | 同上（`test_sandbox_failure_is_fail_closed_and_audited`） | PASS：`PLUGIN_HOOK_UNAVAILABLE` + `plugin_error`；正常路径 `hook_invoked` |
| AC6 | `npx vitest run src/settings/PluginSettingsPanel.test.tsx` | PASS：policy note 断言 AppContainer/fail-closed/permissions: [] |
| 全量 | `python -m pytest tests -q` | 结果见 `core-pytest.log` |
| 探针 | `verification/PLUGIN-RUNTIME-SANDBOX-1/probe-appcontainer.log` | AppContainer 内 `fs=BLOCKED, net=NET_BLOCKED` |

## Closeout Record

- Closeout：待 Review approved 后 closeout（当前 in_review；实现 commit 见 Handoff）。

## Canonical Evidence

|Evidence ID|AC|Path|Commit|SHA-256|Class|
|---|---|---|---|---|---|
|EV-SANDBOX-CORE-PYTEST-TARGETED|AC1-AC6|verification/PLUGIN-RUNTIME-SANDBOX-1/core-pytest-targeted.log|22f09e9056ad0c581db13eb61532035b032ba4b9|3bd5406385a4a496435d23f1daaf8eb1115b1df882728418637dad318b653c3c|CANONICAL|
|EV-SANDBOX-CORE-PYTEST|AC1-AC6|verification/PLUGIN-RUNTIME-SANDBOX-1/core-pytest.log|22f09e9056ad0c581db13eb61532035b032ba4b9|6bfa31ecc3d99331507ada14c764e03db09119c3ff4d29840c3a64f9f1be8134|CANONICAL|
|EV-SANDBOX-PROBE-APPCONTAINER|AC1-AC6|verification/PLUGIN-RUNTIME-SANDBOX-1/probe-appcontainer.log|22f09e9056ad0c581db13eb61532035b032ba4b9|e95d28b5c84081c470f5ab4cdb70f70bf66a43072e5ecff2b7e69fb769c99c21|CANONICAL|
