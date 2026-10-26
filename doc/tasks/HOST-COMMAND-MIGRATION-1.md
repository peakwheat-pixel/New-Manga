---
id: HOST-COMMAND-MIGRATION-1
title: S2 命令迁移——生产命令面 parity 快照 + 6 个 domain service + 双 sidecar 覆盖
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [HOST-CORECLIENT-1]
base_commit: 45841d218
branch: task/HOST-COMMAND-MIGRATION-1
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-COMMAND-MIGRATION-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/HOST-COMMAND-MIGRATION-1
allowed_paths:
  - doc/tasks/HOST-COMMAND-MIGRATION-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/HOST-COMMAND-MIGRATION-1/**
  - G:/CODEX/New Manga.workspace/task-envs/HOST-COMMAND-MIGRATION-1/**
  - G:/CODEX/New Manga.workspace/worktrees/HOST-COMMAND-MIGRATION-1/**
---

# HOST-COMMAND-MIGRATION-1：S2 命令迁移

## 来源与目标

依据 [AD-002](../AD-002_TARGET_DESKTOP_ARCHITECTURE.md)、[EXECUTION_DIRECTIVE_AD002_V2](../design/EXECUTION_DIRECTIVE_AD002_V2.md) §5.4、S1 交付（`HOST-CORECLIENT-1` done，集成 `45841d218`）。

目标：把旧壳 Rust host 的**生产命令面**完整迁移到 C# `CoreClient`/`Host`，用机器可校验的 parity 快照保证语义不漂移；按 6 个 domain service 组织（settings 36 / library 14 / region 7 / reader 4 / resource 2 / workbench 1 生产调用），双 sidecar 全覆盖。

## Acceptance Criteria

- [ ] **AC1 parity 快照生成**：写脚本从 Rust 源码提取**运行时生产命令面**（`PRODUCTION_COMMANDS`，当前 66 条；不含 probe 4 / ac1 3），输出快照：命令名 + 参数 schema + 返回 schema + 错误码清单 → `verification/HOST-COMMAND-MIGRATION-1/parity/production-commands.json`。
- [ ] **AC2 C# 侧映射**：6 个 domain service（Settings/Library/Region/Reader/Resource/Workbench）逐条实现，映射表覆盖快照 100%；未实现项必须显式 `NOT_SUPPORTED` 并登记原因。
- [ ] **AC3 parity 测试**：对每条命令跑「旧壳行为 vs 新 C# 行为」对照（同输入、同 sidecar 副本），结果一致；无旧壳可跑的用契约快照断言。
- [ ] **AC4 双 sidecar 覆盖**：`core_service`（protocol 2.3）与 `host_bridge`（wire v1）两条通道各自的命令都覆盖；中文经 IPC 零乱码（复用 S1 证据方法）。
- [ ] **AC5 回归**：`dotnet build -warnaserror` + `dotnet test` 绿；旧壳 `npx vitest run` 仍 60/60 文件 567/567；`python -m pytest` 相对基线无新增失败（基线见 `prereq/BASELINE.md`）。
- [ ] **AC6 门禁与交接**：`check.ps1 -TaskPath` PASS；lifecycle v3 AC 标记 + Canonical Evidence pin；Handoff（`doc/handoffs/HOST-COMMAND-MIGRATION-1-handoff.md`）；不修改旧壳 `apps/desktop/**`、不改 Python Core、不 push。

## 允许修改范围

- `apps/desktop-avalonia/**`、本 Task 卡、STATUS/PLAN/LEDGER 指针、`verification/HOST-COMMAND-MIGRATION-1/**`、workspace task-env/worktree。
- 只读引用：`apps/desktop/src-tauri/src/**`（命令面与协议）、`verification/HOST-CORECLIENT-1/**`、`doc/design/ADR-0002*`。

## 禁止范围

- 不得修改旧壳、Python Core、依赖清单、AD/ADR；不得 push；不得动受保护资源。
- 不得为对齐而改变既有命令语义（grant 三件套、错误码含义、SQLite 单写）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 快照脚本 + 人工核对条目数 | 仓库源码只读 | NOT_RUN | 待填 |
| AC2/AC3 | C# 集成测试逐命令对照 | sidecar 无标签副本 | NOT_RUN | 待填 |
| AC4 | 中文往返 + wire hex | 同上 | NOT_RUN | 待填 |
| AC5/AC6 | 全量门禁 | 全量 | NOT_RUN | 待填 |

## 依赖、风险与阻塞

- 依赖：HOST-CORECLIENT-1（done）。
- 风险 1：命令面统计口径（66 生产面 vs 57 宏）→ 以 AC1 脚本输出为准，人工复核。
- 风险 2：部分命令只在旧壳 Tauri 侧有薄封装，实际语义在 Core → 对照以 Core 响应为准。
- 风险 3：错误码映射遗漏 → 快照须包含错误码清单。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/HOST-COMMAND-MIGRATION-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/HOST-COMMAND-MIGRATION-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。

