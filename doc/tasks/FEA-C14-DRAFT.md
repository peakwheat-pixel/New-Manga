---
id: FEA-C14-DRAFT
title: C-14 起草（D05 剩余范围：重定位/同步 + 容器页映射）
kind: contract
governance_version: 3
status: in_progress
approval: user_ruling_2026-11-01_C14_new_contract
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-GOV-11
base_commit: 5add23956
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-C14
allowed_paths:
  - doc/tasks/FEA-C14-DRAFT.md
  - doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/reviews/FEA-C14-*.md
  - verification/FEA-C14/**
---

# FEA-C14-DRAFT：C-14 起草（D05 剩余范围）

## 来源

用户 2026-11-01 裁决：**新建 C-14 承载 D05 剩余范围，保留 C-06 的冻结字节**。

`G-CONTRACT` 的关闭条件 = D05 的**全部**「必须冻结」项都有承载契约。D05 共五项（FEA-00 §13.2 `:768`）：

| # | D05 必须冻结 | 已有承载 | 状态 |
|---|---|---|---|
| 1 | 持久身份与授权分离 | **C-06**（`identityFacts` + `grant`） | ✅ 已冻结 |
| 2 | scope / version / lease | **C-06**（grant `scope{sourceId,version,entry,rendition}`）+ **C-01b**（SC-25/29/31 的 lease） | ✅ 已冻结 |
| 3 | **重定位 / 同步** | **无** | ❌ **本 Task 目标** |
| 4 | **容器页映射** | **无**（C-06 只到 entry 授权，未定义容器内页 ↔ `PageId` 的映射与身份） | ❌ **本 Task 目标** |
| 5 | 缓存边界 / 资源上限 | **C-06**（`budget{maxBytes,maxDecodeBytes}`） | ✅ 已冻结 |

**因此 C-14 只需覆盖第 3、4 项**；第 1/2/5 项**引用 C-06 与 C-01b，不复写**（避免双权威）。

## 验收标准

- [ ] **AC1 覆盖矩阵**：`doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md` 的首节含上表（D05 原始要求 → 已有条款 → 缺失条款 → 验收方式），并与 C-06 冻结记录的「D05 授权面子集」表述**无冲突**。 <<PARTIAL: 待实现>>
- [ ] **AC2 重定位/同步条款**：定义 relink（改名/移动）与 repoint（改引用目标）两种操作、`source_sync_plans` 的 diff → 预览 → 确认 → 应用语义、`page_bindings` 的 generation 与 `acceptedSourceVersion`、失败/冲突路径（方案 `:432`/`:459`/`:461`）。 <<PARTIAL: 待实现>>
- [ ] **AC3 容器页映射条款**：定义 `source_entries` 的 locator（PDF 页码 / ZIP 成员名）与**永久身份**的区分、稳定排序键、encoded/pixel digest、容器内容变更时的健康判定（方案 `:419`/`:461`）。 <<PARTIAL: 待实现>>
- [ ] **AC4 跨契约一致性**：与 C-01b（SC-21/22 的 source 表）、C-06（grant scope）、C-04b（删除 preflight 的源引用）逐条对表，无冲突。 <<PARTIAL: 待实现>>
- [ ] **AC5 独立复核**：`doc/reviews/FEA-C14-r1.md`（`approved`，P0/P1 = 0）后由 DSH 冻结。 <<PARTIAL: 待实现>>

## 禁止范围

- **不改 C-06 冻结字节**（用户明确要求保留）；若发现 C-06 与本节冲突 → 走 `CONTRACT-UNFREEZE-C06-<DATE>.md`。
- 不改代码、不动用户数据、不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 覆盖矩阵 vs C-06 冻结记录对表 | 文档 | NOT_RUN | 待补 |
| AC2 | 条款 vs 方案 `:432`/`:459`/`:461` | 文档 | NOT_RUN | 待补 |
| AC3 | 条款 vs 方案 `:419` 与 `schema.py` source 表 | 文档 | NOT_RUN | 待补 |
| AC4 | 四契约交叉对表 | 文档 | NOT_RUN | 待补 |
| AC5 | 独立复核 | 只读 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree、无临时产物。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
