---
id: FEA-C14-DRAFT
title: C-14 起草（D05 剩余范围：重定位/同步 + 容器页映射 + 缓存边界缺失子面）
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
| 5 | 缓存边界 / 资源上限 | **部分**（逐条见下） | ⚠ **部分** |

**第 5 项逐条证明**（用户 2026-11-01 要求：不能只写「留给 C-09」——C-09 自身要求两 Gate 先关闭，会形成循环）：

| 子面 | 承载条款 | 状态 |
|---|---|---|
| **单次读取预算**（字节/解码尺寸上限，超限拒绝不截断） | **C-06 `:64`** 第 7 条 `budget{maxBytes,maxDecodeBytes}` | ✅ 已冻结 |
| **可再生产物定义 + cache key**（含 `SourceVersion`/entry/decoder 版本/参数） | **C-01b SC-02** | ✅ 已冻结 |
| **缓存 vs 非缓存边界**（处理结果/人工版本/恢复文件不得按缓存清理） | **C-01b SC-03** | ✅ 已冻结 |
| **两通道隔离**（`user-source` 不得进 derived-cache grant） | **C-01b SC-20** + **C-06 `:65`** | ✅ 已冻结 |
| **淘汰策略**（何时清、清多少、顺序、LRU 还是别的） | 无 | ❌ **C-14 覆盖** |
| **持久化**（缓存是否跨会话保留、存放位置、崩溃后一致性） | 无 | ❌ **C-14 覆盖** |
| **全局资源上限**（总缓存字节上限、并发解码数、与其它任务的配额关系） | 无 | ❌ **C-14 覆盖** |

**因此 C-14 覆盖第 3、4 项 + 第 5 项的三个缺失子面**；第 1/2 项与第 5 项已承载的四个子面**引用 C-06/C-01b，不复写**（避免双权威）。

## 验收标准

- [ ] **AC1 覆盖矩阵**：`doc/plan/FEA-C14_SOURCE_RELOCATION_DRAFT.md` 的首节含上表（D05 原始要求 → 已有条款 → 缺失条款 → 验收方式），并与 C-06 冻结记录的「D05 授权面子集」表述**无冲突**。 <<PARTIAL: 待实现>>
- [ ] **AC2 重定位/同步条款**：定义 relink（改名/移动）与 repoint（改引用目标）两种操作、`source_sync_plans` 的 diff → 预览 → 确认 → 应用语义、`page_bindings` 的 generation 与 `acceptedSourceVersion`、失败/冲突路径（方案 `:432`/`:459`/`:461`）。 <<PARTIAL: 待实现>>
- [ ] **AC3 容器页映射条款**：定义 `source_entries` 的 locator（PDF 页码 / ZIP 成员名）与**永久身份**的区分、稳定排序键、encoded/pixel digest、容器内容变更时的健康判定（方案 `:419`/`:461`）。 <<PARTIAL: 待实现>>
- [ ] **AC4 跨契约一致性**：与 C-01b（SC-21/22 源表、**SC-02/SC-03/SC-20 缓存条款**）、C-06（grant scope + per-request 预算）、C-04b（删除 preflight 的源引用）逐条对表，无冲突。 <<PARTIAL: 待实现>>
- [ ] **AC5 缓存边界条款**：定义淘汰策略（触发条件/清理顺序/上限）、持久化（跨会话/位置/崩溃一致性）、全局资源上限（总字节/并发解码数）；**不得与 C-01b SC-02/SC-03/SC-20 冲突**。 <<PARTIAL: 待实现>>\n- [ ] **AC6 独立复核**：`doc/reviews/FEA-C14-r1.md`（`approved`，P0/P1 = 0）后由 DSH 冻结。 <<PARTIAL: 待实现>>

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
| AC5 | 缓存边界条款 vs C-01b SC-02/03/20 | 文档 | NOT_RUN | 待补 |
| AC6 | 独立复核 | 只读 | NOT_RUN | 待补 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| - | - | - | `-` | `-` | CANONICAL |

## Resource Manifest

无 worktree、无临时产物。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
