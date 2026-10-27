---
id: NS-WIRE-A1
title: NS 命令接线第一批（settings/plugins/backup/cleanup）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups_batch_a1
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 230164c5c
branch: task/NS-WIRE-A1
worktree: G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-A1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/NS-WIRE-A1
allowed_paths:
  - doc/tasks/NS-WIRE-A1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/NS-WIRE-A1/**
  - G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-A1/**
  - G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-A1/**
---

# NS-WIRE-A1：设置/插件/备份/清理类 NOT_SUPPORTED 接线（第一批）

## 背景

S2 交付时 66 条生产命令中 16 条已实现、50 条显式 NOT_SUPPORTED；S3/S4 已登记 18 条计划批次（S3-A/B/C 8 条、S4-A/B/C 10 条）。本任务做 **A 组第一批 = S3-A/B/C 类（settings / plugins / backup / cleanup 语义）** 的命令接线。

## Acceptance Criteria

- [x] **AC1 清单**：从 `doc/handoffs/HOST-COMMAND-MIGRATION-1-handoff.md` 与 `verification/HOST-COMMAND-MIGRATION-1/parity/` 列出 S3-A/B/C 对应命令（预期 8 条），逐条标注 Core 路由/参数/返回。→ **MET**：8 条全部列出（旧壳 handler/参数/返回/错误类型 + Core 路由 + minor + probe 实测）：`verification/NS-WIRE-A1/command-list.json`。
- [x] **AC2 实现**：在 C# `HostCommandRegistry`/dispatcher 与 domain service 中接线；每条命令对冻结 sidecar 真实执行，参数/返回/错误码与旧壳 parity 一致。→ **MET**：registry 8 条 Core 绑定（P15 三条 minor=7，其余 minor=3）；dispatcher 复刻旧壳签名做参数边界校验/负载翻译；集成测试 24 implemented 真实执行 + `probe-results.json` 8 路由实测（含 reader projection 在 BOOK-FIXTURE-1 上 8 页成功路径；P15 错 minor/空 chapter 两类负例）。
- [x] **AC3 parity 更新**：`extract-command-surface.py --check` 零漂移；parity 快照中这些命令从 NOT_SUPPORTED → IMPLEMENTED，证据 JSON 落 `verification/NS-WIRE-A1/`。→ **MET**：`--check` PASS（66 命令零漂移，快照 sha `4c6a4da0…` 未变）；registry 16→24 IMPLEMENTED / 50→42 NOT_SUPPORTED（8 条变更）：`parity-update.json` + `evidence/parity-contract.json`。
- [x] **AC4 回归**：`scripts/test.ps1` 全绿（新增命令测试）；旧壳 vitest 60/567；pytest 基线 3F/2739P/9S 无新增失败。→ **MET**：test.ps1 **110/110 passed, 0 skipped**；vitest **60/60 文件、567/567 用例**；pytest **3F/2739P/9S（0 新增）**。
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。→ **MET**：check.ps1 PASS；pin 见下；`doc/handoffs/NS-WIRE-A1-handoff.md`。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/NS-WIRE-A1/**`、workspace。只读参考：旧 Rust host 命令面、S2 Handoff。

## 禁止范围

不改 Python Core 语义、不改 Host 契约（如确需，先回报 DSH）、不改旧壳、不 push、不 gc/prune；不得把未验证命令标 IMPLEMENTED。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | `verification/NS-WIRE-A1/tools/probe-ns-a1.ps1`（8 路由直连）+ `scripts/test.ps1` 集成测试 | 无标签 sidecar 副本 + 隔离 data root（+ BOOK-FIXTURE-1 数据根） | **PASS**：8/8 路由实测；24 implemented 真实执行；P15 错 minor/空 chapter 负例按预期 typed error | `probe-results.json`、`evidence/integration-results.json` |
| AC3 | `extract-command-surface.py --check` + registry 前后对比 | Rust 源只读 | **PASS**：66 命令零漂移、快照 sha 未变；16→24 / 50→42 | `parity-update.json`、`parity-check.log` |
| AC4/AC5 | test.ps1 / vitest / pytest / check.ps1 | 全量 | **PASS**：110/110、60/567、3F/2739P/9S、治理 PASS | `dotnet-all.log`、`vitest.log`、`pytest.log` |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-A1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/NS-WIRE-A1 | 本轮 probe 临时根已清理；证据副本在 `verification/NS-WIRE-A1/` | 无残留进程；task-env 仅脚本副本 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
