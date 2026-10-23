---
task_id: PLUGIN-RUNTIME-SANDBOX-2
kind: implementation
status: in_review
owner: dsh（本会话 Lead 兼任 Owner）
reviewer: reviewer-settings-a（非实现者）
created: 2026-10-23
base_commit: acc1e36a7dc9f333c41f8131ff1b4d0b0bcd3423
depends_on: PLUGIN-RUNTIME-SANDBOX-1
authorization: 用户 2026-10-23「1234都授权」（本 Task = 候选 2：per-plugin AppContainer profile）
allowed_paths:
  - src/infrastructure/plugins/**
  - tests/**
  - doc/tasks/PLUGIN-RUNTIME-SANDBOX-2.md
  - doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/TASK_LEDGER.md（Lead 集成登记）
  - doc/handoffs/**
  - verification/PLUGIN-RUNTIME-SANDBOX-2/**
---

# PLUGIN-RUNTIME-SANDBOX-2 — per-plugin AppContainer profile

## 背景

SANDBOX-1 为性能使用**共享容器**（所有插件同一 AppContainer SID），插件目录 ACL 只授予当前插件，但历史上已授目录对共享 SID 保留 → 跨插件目录读不在 v1 威胁模型（Task/UI 已注明）。本 Task 改为 **每插件独立 profile**，使插件只能读自己的目录与 Python 运行时。

## 范围

- `sandbox.py`：`_profile_name` 按 `plugin_id` 生成（`NewMangaPlugin-<sha256前12>`）；`_ensure_profile` per-plugin 缓存；解释器 ACL 按 SID 只授一次（缓存已授 SID 集合，避免每插件重复递归授予）；保留共享容器作为**显式 opt-in**（`shared_profile=True`，仅供测试/低开销场景），生产默认 per-plugin。
- `PluginService`/`core_assembly`：生产装配使用 per-plugin 模式。
- 测试：
  - 插件 A 读取插件 B 目录（`plugin.py`/`manifest.json`）→ `BLOCKED`；
  - 插件 A 仍能正常执行自己的 Hook；
  - 解释器 ACL 每 SID 只授一次（计数断言）；
  - 生产装配 `core.plugins._sandbox.shared_profile is False`。

## 验收

- [x] **AC1** 插件 A 在容器内读取插件 B 目录失败（`BLOCKED`，不泄露内容）。
- [x] **AC2** 插件 A 自己的 Hook 正常执行（per-plugin profile 不破坏沙箱启动）。
- [x] **AC3** 生产装配使用 per-plugin profile（非共享）。
- [x] **AC4** 解释器 ACL 按 SID 缓存（同一插件多次 Hook 不重复授予；不同插件各授一次）。
- [x] **AC5** 全量测试无回归；文档（UI/Task/Handoff）更新为「每插件独立容器」。

## Closeout Record

## 测试与证据

| AC | 命令/证据 | 结果 |
|---|---|---|
| AC1 | `tests/infrastructure/test_plugin_sandbox.py::test_plugin_cannot_read_another_plugins_directory` | PASS：插件 A 读 B 目录 → `BLOCKED`，无内容泄露 |
| AC2 | `test_sandbox_still_runs_a_benign_hook` / `test_production_assembly_wires_the_sandbox` | PASS：per-plugin 容器内 Hook 正常执行 |
| AC3 | `test_production_assembly_wires_the_sandbox`（`shared_profile is False`） | PASS：生产默认 per-plugin |
| AC4 | `test_interpreter_acl_is_granted_once_per_profile_sid` | PASS：同一 SID 只授一次（缓存） |
| AC5 | `python -m pytest tests -q` + `npx vitest run` + `tsc --noEmit` | 见 `verification/PLUGIN-RUNTIME-SANDBOX-2/*.log` |
| 定向 | sandbox + runtime + wire + assembly | 52 passed |

## Closeout Record

- Closeout：待 Review approved 后 closeout。

## Canonical Evidence

|Evidence ID|AC|Path|Commit|SHA-256|Class|
|---|---|---|---|---|---|
|EV-SANDBOX-2-CORE-PYTEST-TARGETED|AC1-AC5|verification/PLUGIN-RUNTIME-SANDBOX-2/core-pytest-targeted.log|9ab2748d6325e8e817537fed40cd9269edc0d1ea|b2faaf1e293cbda8094f4088639ae10c019a5df4cef35b4fc75e78aaf9c423ae|CANONICAL|
|EV-SANDBOX-2-CORE-PYTEST|AC1-AC5|verification/PLUGIN-RUNTIME-SANDBOX-2/core-pytest.log|9ab2748d6325e8e817537fed40cd9269edc0d1ea|7fa94623f790fcc12f1dd8ef31dec40bcd352f189ba619ae77be7d37ff8b11aa|CANONICAL|
