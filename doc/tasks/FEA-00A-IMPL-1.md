---
id: FEA-00A-IMPL-1
title: FEA-00a 数据安全修复（prepare 与 seam 分离 / 三处零变化）· 范围冻结候选
kind: implementation
governance_version: 3
status: proposed
approval: pending_user_decision_D1_D4_and_scope_freeze
suggested_owner: codex
owner: codex
reviewer: c01b-reviewer
depends_on:
  - FEA-00A-PREP-1
blocked_by:
  - FEA-00A-PREP-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-00A-IMPL-1
allowed_paths:
  - doc/tasks/FEA-00A-IMPL-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/reviews/FEA-00A-IMPL-*.md
  - src/infrastructure/providers/**
  - src/infrastructure/sqlite/pipeline.py
  - tests/**
  - verification/FEA-00A-IMPL-1/**
---

# FEA-00a 数据安全修复（候选卡，`proposed`，未释放）

## 来源

用户 2026-11-01 授权 `FEA-00A-PREP-1`（只读评估）；评估文档 [`doc/plan/FEA-00A_PREP.md`](../plan/FEA-00A_PREP.md) 已落盘并经独立复核 `approved`（[`FEA-00A-PREP-r1`](../reviews/FEA-00A-PREP-r1.md)，P0/P1 = 0，P2×6 已处置）。

本卡是**范围冻结候选**：`proposed`，未 `ready`、未释放。**必须用户先拍板评估文档 §7 的 D1–D4**，再由 DSH 完成范围冻结与独立复核后才可 `ready`。

## 待用户拍板的决策（评估 §7）

| # | 决策 | 推荐 |
|---|---|---|
| D1 | 是否同时覆盖 artifact 指针（含 `publish` 的 `artifact_revisions` 行/文件） | ② 覆盖（同类缺陷一并修） |
| D2 | 是否允许改 `src/application/tasks/service.py` | ① 不允许（token 契约可避免） |
| D3 | 候选承载：复用 `step_result_candidates` / 新 staging 表 / 文件 staging | ① 复用（无迁移，需清理归属） |
| D4 | 验证等级 | L2 + 真实生产 assembly |

## 范围（待 D1–D4 定稿后冻结）

- **写域**：`src/infrastructure/providers/**`、`src/infrastructure/sqlite/pipeline.py`、`tests/**`（+ D1=② 时 `handlers.py:962` 的 `adopt_current` 调用点，仍在 `providers/**` 内）；**不改** `src/application/**`、不改 schema（前提 D3=①）、不改 App/CoreClient/Python 其它面。
- **禁止**：改冻结契约字节（15 份 pin）、`G-DELETE-IMPL` 状态、用户数据；不 push。

## 验收标准（草案，随 D1–D4 定稿）

- [ ] **AC1 三处零变化**：revision 冲突 / Lock 冲突 / `STALE_RUN_SNAPSHOT` / DB 失败 / pause / cancel / prepare 后崩溃重启 7 类注入下，`regions.text_json`、`regions.current_revision_id`、`region_revisions` 行数与 prepare 前完全相同（A1）。
- [ ] **AC2 候选可诊断**：失败候选可在 `step_result_candidates` 查询（reason/status/base_revision_id/payload 正确），staged 失败行的清理归属按 §4.2 落实（A2）。
- [ ] **AC3 成功同事务**：revision 行 + text + 指针 + 候选 resolved 同事务；无「text 已变而指针未变」中间态（A3）。
- [ ] **AC4 prepare 不触 live**：结构/grep 断言 `step_writes.py` prepare 路径无 `UPDATE regions`/`media_artifacts`；token = 预生成真实 revision id（§4.1）。
- [ ] **AC5 重启可判定**：重启后三处不变、候选可识别/清理/重试（A5）。
- [ ] **AC6（D1=②）artifact**：`media_artifacts.current_revision_id` 与 `publish` 的 `artifact_revisions` 行/文件同样 staging，成功时同事务 adopt（A6）。
- [ ] **AC7 §15.6 出口**：关闭新写入入口；旧库只读核验、保留备份与候选（A7）。
- [ ] **AC8 回归**：8 个 blast-radius 测试文件（评估 G7）的 outcome 对照；生产 assembly 执行 prepare。
- [ ] **AC9 独立复核**：`doc/reviews/FEA-00A-IMPL-r1.md` 判 `approved`（P0/P1 = 0）。

## L 前置判定（预估）

`L-1`：**N/A**（不迁 schema、不触 Source 四表 DDL；若 D3 改为新表则触发）；`L-2`：**N/A**（不新增 wire 码/白名单；若引入错误码则触发）；`L-5`：**N/A**（不触备份/恢复）。

## 禁止范围

- 不改任何冻结契约字节；不释放其它实现 Task；不动用户数据；不 push；不顺手修 FEA-03/FEA-10。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

实现 Task（未开始）：仓库内无 worktree/构建产物；开始后按 `Workspace Governance` 在 `G:\CODEX\New Manga.workspace\` 建 task-env。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 尚未开始实现；未访问用户数据 |
| build/temp（未来） | - | PENDING | ..\New Manga.workspace\ | - | 实现开始前补齐具体路径与处置 |

## Closeout Record

- 2026-11-01：`proposed`；等用户拍板 D1–D4 后由 DSH 冻结范围并安排独立复核。
