---
id: E7-CONCURRENCY-STATUS-2
title: E-7 并发安全状态更新（五项终态 + 可信表述 + 残余清单）
kind: governance
governance_version: 3
status: done
suggested_owner: DSH
owner: DSH
reviewer: （见 r1）
integration_commit: PENDING
canonical_evidence_status: complete
resource_closeout_status: complete
depends_on:
  - E7-1-UNIFY-LEASE-1
  - E7-2-DYNAMIC-EVIDENCE-1
  - BRIDGE-FAKE-HARNESS-1
  - R002-RESYNC-1
  - E7-5-SHUTDOWN-RACE-1
approval: 用户 2026-11-15「全部授权」；E-7 五项已全部处置，需更新权威状态表述
base_commit: dd5dc1519
branch: main
worktree: G:/CODEX/New Manga
evidence_dir: verification/E7-CONCURRENCY-STATUS-2
allowed_paths:
  - doc/tasks/E7-CONCURRENCY-STATUS-2.md
  - doc/reviews/E7-CONCURRENCY-STATUS-2026-11-16.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/E7-CONCURRENCY-STATUS-2/**
---

# E7-CONCURRENCY-STATUS-2：状态更新（第 2 版）

## 为什么需要

`doc/reviews/E7-CONCURRENCY-STATUS-2026-11-16.md` 第 1 版写于 E-7 五项**全部仍开**时，
标题就是「权威 5 项的逐项核实（**全部仍开**）」。

此后陆续完成：

| 卡 | 处置的项 |
|---|---|
| `E7-1-UNIFY-LEASE-1` | 第 1 项（`_pipeGate` → 传输层租约；两个 `ExchangeAsync` 重载降 `internal`） |
| `R002-RESYNC-1` | 第 3 项（R-002 有界重同步） |
| `R005-CANCEL-POISON-1` | 第 4 项（R-005 取消 poison） |
| `E7-5-SHUTDOWN-RACE-1` | 第 5 项（核证，不改代码） |
| `E7-2-FAILCLOSED-1` + `E7-2-DYNAMIC-EVIDENCE-1` | 第 2a 项（core 侧 fail-open） |
| `BRIDGE-ID-FAILCLOSED-1` + `BRIDGE-FAKE-HARNESS-1` | 第 2b 项（bridge 侧 fail-open） |

⇒ 第 1 版报告**已经过期且会误导读者**。本卡更新它。

## 做了什么

重写 `doc/reviews/E7-CONCURRENCY-STATUS-2026-11-16.md` 为第 2 版，结构：

1. **五项逐项终态表**（每项标注：处置 / 卡 / 动态证据）；
2. **判定依据的强度分级**（「已修」= 有会变红的测试；「已核证」= 未改代码但行为被钉住）；
3. **「并发安全」现在可以怎么表述** —— 分「可以说的」与「不能说的」两栏；
4. **残余清单 6 项**（按风险排序：`AcquireExchangeLeaseAsync` 仍 public、tools/perf 过期说明、
   **真实 sidecar 长稳压测未做**、bridge 其余边界、场景编码约定、`_stopping` 守卫）；
5. **方法学教训 6 条**（变异测试是判据 / `--no-incremental` 不传子项目 / evidence 登记 /
   否定式约束读法 / 改 A 回头看 B / 对不稳定测试先说"我不确定"）。

## 核实（本卡的核心验收）

报告里的每条引用都必须真实：

- 12 项证据文件全部存在（0 缺失）；
- 7 张 E-7 相关卡全部 `status=done`、AC **6/6**；
- 三处 poison 接线测试都在（`FakeCore` 2 处、`FakeBridge` 2 处）。

## 目标（一个可观察结果）

第 2 版报告落盘，且其引用的每条证据都可 `Test-Path` 验证；读者不必重走这十几轮即可了解 E-7 终态。

## Acceptance Criteria

- [x] **AC1 五项终态表**：每项都有「处置 / 卡 / 动态证据」三列，且卡名与证据路径真实存在。 <<MET>>
- [x] **AC2 表述分级**：明确区分「可以说的」与「不能说的」，不把残余淡化。 <<MET>>
- [x] **AC3 残余清单**：至少包含「真实 sidecar 长稳压测未做」这一项。 <<MET>>
- [x] **AC4 不越权**：明确写「不关闭 E-7」「不改变 Release Gate」。 <<MET>>
- [x] **AC5 引用核实**：报告引用的证据文件全部存在；相关卡全部 done 且 AC 全达成。 <<MET>>
- [x] **AC6 独立复核**：固定 head 交独立上下文 Review。 <<MET>>

## 允许修改范围

见 frontmatter `allowed_paths`：只改状态报告 + 新建本卡。

## 禁止范围

- 不得据此关闭 `E-7` 或 `PIPE-EXCLUSIVE-TRANSPORT-1`；
- 不得把「单测通过」写成「真实 sidecar 下安全」；
- 不得删除第 1 版已记录的教训（可改写结构，不可抹掉内容）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class | sha256_basis |
|---|---|---|---|---|---|---|
| EV-ECS2-01 | AC5 引用核实（12 项存在性 + 7 张卡状态） | verification/E7-CONCURRENCY-STATUS-2/citation-check.log | dd5dc1519 | PIN_PENDING | CANONICAL | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | verification/E7-CONCURRENCY-STATUS-2/ | NOT_APPLICABLE | — | — | 新增证据，无迁移/归档 |

## Closeout Record

- Closeout：2026-11-16，DSH。
- **成果**：`doc/reviews/E7-CONCURRENCY-STATUS-2026-11-16.md` 重写为第 2 版。第 1 版标题是
  「权威 5 项的逐项核实（**全部仍开**）」，在六张卡完成后已**过期且会误导读者**。
- **第 2 版内容**：
  1. 五项终态表（处置 / 卡 / 动态证据）；
  2. 判定强度分级：「已修」= 有会变红的测试（多数经变异验证）；「已核证」= 未改代码但行为被钉住；
  3. **「可以说的」与「不能说的」两栏**，明确不宣称「并发安全已完全达成」「E-7 可关闭」
     「单测通过 ⇒ 真实 sidecar 下安全」；
  4. **残余 6 项**（含最高风险项：**真实 sidecar 下的长稳压测未做**）；
  5. 方法学教训 6 条。
- **核实（AC5）**：`citation-check.log` 记录 12 项证据文件全部存在（缺失 0）、
  7 张 E-7 相关卡全部 `status=done` 且 AC **6/6**。
- **门禁**：`check.ps1` PASS (3 warnings)｜`verify_pins` 18/18｜`api_inventory` 1/80/6=87。
- **未关闭项（不淡化）**：
  1. **本卡不关闭 `E-7`**，也不改变 Release Gate —— 报告只是状态更新，`E-7` 本项由
     `PIPE-EXCLUSIVE-TRANSPORT-1` 的限定条承接；
  2. 报告 §3 的**残余 6 项**仍需后续处置，其中「真实 sidecar 长稳压测未做」需要真实夹具与更长运行时间；
  3. 第 2 版报告的「动态证据」列举的是**能变红的测试**，不等于**真实产品场景全覆盖**。

