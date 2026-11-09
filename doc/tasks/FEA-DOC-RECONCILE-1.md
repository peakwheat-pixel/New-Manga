---
id: FEA-DOC-RECONCILE-1
title: FEA 线文档对账（STATUS 四表 DDL 口径、C11-PREREQ-1 DAG 行、GOV-11/D07 关闭、BRIDGE 裁决、卡级注记）
kind: governance
governance_version: 3
status: done
approval: 用户 2026-11-09 指令「做文档对账」（承接 `FEA-STATUS-2026-11-09` 检查发现的 1/2/4 项，并入 3/5/6 项）；DSH 范围冻结：只改文档与卡级状态，0 源码、0 契约字节、0 pin 重算、0 push
suggested_owner: dsh
owner: dsh-lead
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审；指派于交付后，session 记入 `doc/reviews/FEA-DOC-RECONCILE-1-r1.md`）
depends_on: []
base_commit: 9b0683822
branch: null
worktree: null
integration_commit: c22aea60c
delivery_head: c22aea60c
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-DOC-RECONCILE-1
allowed_paths:
  - doc/tasks/FEA-DOC-RECONCILE-1.md
  - doc/tasks/FEA-C11-PREREQ-1.md
  - doc/tasks/FEA-GOV-11.md
  - doc/tasks/FEA-D07-UNBLOCK.md
  - doc/tasks/FEA-07-IMMERSIVE-F11-1.md
  - doc/tasks/FEA-11-RUN-GRANT-2.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/00_INDEX.md
  - doc/handoffs/FEA-DOC-RECONCILE-1-*.md
  - doc/reviews/FEA-DOC-RECONCILE-1-*.md
  - verification/FEA-DOC-RECONCILE-1/**
out_of_scope:
  - 不改任何 `doc/plan/FEA-CONTRACT-FROZEN-*`、`doc/contracts/**`、18 pins（只引用，不重算）
  - 不改任何 `doc/reviews/**` 与 `verification/**` 既有字节（append-only 关闭记录只写本 Task 与新卡内）
  - 不改源码、测试、构建产物；不 push
---

# FEA-DOC-RECONCILE-1：FEA 线文档对账

## 来源

`FEA-STATUS-2026-11-09` 状态检查（产物在仓外 `G:\CODEX\New Manga.workspace\agent-output\fea-status-2026-11-09\FEA-STATUS-2026-11-09.md`）发现 6 项文档口径问题。用户 2026-11-09 指令「做文档对账」。

检查事实基线：HEAD `9b0683822`（`main` 干净）；`verify_pins` 18/18 PASS；`check.ps1` PASS（3 warnings）；pytest 3395/10、.NET 1794/0/107。

## 对账清单（范围冻结）

| # | 问题 | 处置 | 事实依据 |
|---|---|---|---|
| 1 | `STATUS:11` 写「FEA-12 四表 DDL 未冻」 | 改为「四表 DDL 已冻 = L-1 前置已满足（C-15 schema v7：`source_entries`/`page_bindings`；C-17 v1.1 schema v8：`source_sync_plans`/`source_operations`，并增 `source_binding_publications`/`source_revision_lineage`）」 | `FEA-CONTRACT-FROZEN-C15.md:43,50`；`FEA-CONTRACT-FROZEN-C17.md:20`；`FEA-11-PREREQ-1.md:45,65`；`tests/fea11/test_v8_migration.py`；`src/infrastructure/sqlite/schema.py:757-871` |
| 2 | `FEA-C11-PREREQ-1` 卡 done、DAG 行仍 `approved（待集成收口）` | PLAN 行翻 `done`（集成 `b7018e19b`） | 卡 Closeout 2026-11-02：交付 `b7018e19b` 已在 main，证据 sha256 一致 |
| 3 | `FEA-GOV-11` 长期 `in_progress`（等 4 项裁决） | AC1–AC3 标 `<<MET>>` + 关闭记录 + `done` | `ADJ-2026-11-01-FEA-DECISIONS.md`：R=C1=D/C3=是、U-04 批准、U-05a 纳入、U-05b 保留；C-01b/C-02/C-03/C-11 已 FROZEN；首个实现候选 `FEA-02-CORE` done（集成 `135479270`） |
| 4 | `FEA-D07-UNBLOCK` AC8 为 `[ ] <<MET>>`（矛盾），状态 `in_progress` | AC8 改 `[x] <<MET>>` + 证据 + `done`（Closeout 披露 D07 行 7 为 L-5 认定的「部分」） | `GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md:14,30,39-40`（2026-11-01 CLOSED；L-5 认定） |
| 5 | `FEA-07-IMMERSIVE-F11-1` limitation「默认 v2 壳无 F11 入口」已由 `FEA-07-V2-F11-1` 收口，卡未记录 | append-only 关闭该条 limitation；status 保持 `closed_with_limitations`；补「本卡 legacy 壳」限定 | `FEA-07-V2-F11-1` done（`9b0683822` 链，AOC 2560×1440 `EV-V2F-05`） |
| 6 | `FEA-11-RUN-GRANT-2` title 仍带「proposed，待依赖」而 status=done | 追加对账注记（不改 title 字节） | 卡 front matter `status: done` |
| 7 | `FEA-02-BRIDGE` 无卡、无 DAG 行 | PLAN 记结论「不独立释放」；**依据登记在本卡**：退出协调由 `FEA-07` 已交付的 `ExitCoordinator`（AC2 `FEA-07.md:298`）与 `FEA-07-RESIDUAL-2` AC-R4a-2（`:50`）覆盖；残余风险另卡 | 方案 §15.6 `:922`；`FEA-04.md:46`（原文为「Host 生命周期/`ExitCoordinator` 部分未实施」，仅支持本卡不依赖）；`git grep 生命周期断言 -- doc/tasks` 仅命中 FEA-07 两卡 |

## Acceptance Criteria

- [x] **AC1 STATUS 四表 DDL 口径**：`STATUS:11` 不再声称未冻，且四个表名/版本可追溯。 <<MET>>
- [x] **AC2 C11-PREREQ-1 DAG 行**：`REBASELINE_PLAN` 该行 `done` + 集成 `b7018e19b`，与卡 Closeout 一致。 <<MET>>
- [x] **AC3 GOV-11 收口**：AC1–AC3 标 `<<MET>>` 并引裁决记录；`status: done`；测试表 `NOT_RUN` 原样保留（append-only，不据此判 PASS）。 <<MET>>
- [x] **AC4 D07-UNBLOCK 收口**：AC8 一致性修复（`[x] <<MET>>`）+ Gate 关闭证据（含 D07 行 7「部分」的 L-5 口径）；`status: done`。 <<MET>>
- [x] **AC5 IMMERSIVE limitation 关闭记录**：追加一节记录「v2 壳入口」limitation 由 V2-F11-1 关闭（补 legacy 壳限定）；status 保持 `closed_with_limitations`（其余 limitation 不动）。 <<MET>>
- [x] **AC6 RUN-GRANT-2 注记**：卡内追加 title 历史描述说明。 <<MET>>
- [x] **AC7 BRIDGE 裁决**：PLAN 记结论（不独立释放），依据（`FEA-07` `ExitCoordinator` AC2 + `FEA-07-RESIDUAL-2` AC-R4a-2）登记于本卡 §对账清单 #7，不留悬空节点。 <<MET>>
- [x] **AC8 门禁不降**：`verify_pins` 18/18、`check.ps1` PASS、ledger 重生成、STATUS/PLAN 未超防膨胀预算、0 源码/契约字节改动。 <<MET>>
- [x] **AC9 独立 Review**：非本会话的独立上下文审查交付 head；r1/第二审查者 = changes_requested（均处置），r2/r3 复审 = approved。 <<MET>>

## 禁止范围

- 不改 `doc/plan/FEA-CONTRACT-FROZEN-*` / `doc/contracts/**` / 18 pins 的任何字节。
- 不改任何既有 `doc/reviews/**`、`verification/**` 字节；不改 `FEA-07-AC5-NATIVE-1`（用户动作未复位）与 `FEA-06-RESIDUAL-1`（残余承接未变）。
- 不把「done」写成「可发布」；本轮不推进 S5、不释放 FEA-13/14/15。
- 不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC7 | 逐项 diff 对照上表事实依据 | 只读 + 文档 | PASS | 本卡 §对账清单 |
| AC8 | `pwsh -NoProfile -File tools/governance/check.ps1` | 仓库根 | PASS（3 warnings，预算内） | `verification/FEA-DOC-RECONCILE-1/gates-3.log`（当前入口） |
| AC8 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 仓库根 | PASS 18/18 | 同上 |
| AC8 | `python tools/governance/task_ledger.py --write`（**提交后**重跑；修 REC-02） | Python 3.14 | PASS（分项与 HEAD 一致） | `doc/TASK_LEDGER.md` |
| AC9 | Review r1（fresh subagent） | head `4d64bfdcb` | changes_requested（P0=0/P1=1/P2=4/P3=8） | `doc/reviews/FEA-DOC-RECONCILE-1-r1.md` |
| AC9 | 第二独立审查者 | head `4d64bfdcb` | changes_requested（P0=0/P1=2/P2=4/P3=3） | `doc/reviews/FEA-DOC-RECONCILE-1-review.md` |
| AC9 | r2 复审（处置后） | head `b6ada81e8` | **approved**（11 FIXED / 2 PARTIAL / 0 OPEN） | `doc/reviews/FEA-DOC-RECONCILE-1-r2.md` |
| AC9 | r3 复审（P1-01/P2-02 处置后） | head `c22aea60c` | **approved**（22 FIXED / 0 OPEN；新增 P3×5 非阻断） | `doc/reviews/FEA-DOC-RECONCILE-1-r3.md` |

## 残余 / 未闭环（登记，不在本轮范围）

| # | 项 | 状态 | 处置建议 |
|---|---|---|---|
| R-1 | `doc/AD-003_REFERENCED_SOURCE_ARCHITECTURE.md:128` 仍写「四表 DDL 仍未冻结」 | **过期口径**（C-15/C-17 已冻） | 不在本卡 allowed_paths；需 AD-003 errata 专项（下次对账或 AD 文档维护卡） |
| R-2 | `doc/plan/FEA-C11_IMPL_PREREQS.md:24` L-1 仍写「DDL 未冻结」 | **过期口径**（L-1 前置已满足） | 需 L-1 解除记录或 errata；本卡只登记不改契约前置文档 |
| R-3 | `doc/REBASELINE_PLAN.md:12` 写「C-17 v1.0 FROZEN」（现状 v1.1） | 既有文本，改动前已存在 | 下次 PLAN 变更时一并更正 |
| R-4 | PLAN 预算仅剩 6 B / 1 行（6994/7000，63/64 行） | 结构性风险 | 释放下一 Task 前把「完成：」长段迁至 checkpoint/TASK_LEDGER |
| R-5 | `FEA-07-AC5-NATIVE-1` 用户显示设置未复位；`FEA-06-RESIDUAL-1` 残余承接未变 | 明确不处理 | 维持原状，用户动作与后续 residual 卡承接 |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-RECON-STATUS | AC1,AC3,AC4,AC5,AC6 | `doc/STATUS.md` | `-` | `59e7bb9f6ddef77419471cc700cfd0e8d8ea9a95ece0d4581c1ebe2be5d5eb44` | CANONICAL |
| EV-RECON-PLAN | AC2,AC7 | `doc/REBASELINE_PLAN.md` | `-` | `a2d9c7fda96eb733503cc2f1d07ff5e93c2b8855e8cc7b9496ce98ec30048f8c` | CANONICAL |
| EV-RECON-GOV11 | AC3 | `doc/tasks/FEA-GOV-11.md` | `-` | `b340cbbd43fc4b7a102cf6232692a6db6c8ba31f496f89f7bfed870338deac73` | CANONICAL |
| EV-RECON-D07 | AC4 | `doc/tasks/FEA-D07-UNBLOCK.md` | `-` | `946ad2bd9b51fe8bcba988303336fcf45bb4c371524066415e463dd2d4ca2745` | CANONICAL |
| EV-RECON-IMMERSIVE | AC5 | `doc/tasks/FEA-07-IMMERSIVE-F11-1.md` | `-` | `4ea62822594e29c479f304d3fab4893811da569b8e573ee999ca838d685db1b2` | CANONICAL |
| EV-RECON-RG2 | AC6 | `doc/tasks/FEA-11-RUN-GRANT-2.md` | `-` | `83d15cbd086ae30323aff8cde51c25186dbba42377a5ffeaf9f7de6739b9dfd3` | CANONICAL |
| EV-RECON-GATE | AC8 | `verification/FEA-DOC-RECONCILE-1/gates-3.log` | `-` | `79fa4682c747f8f2386d2b376f36e9bb1fab78d7de3f98e8a11e61c7a4c80e75` | CANONICAL |
| EV-RECON-GATE-R2 | AC8（历史） | `verification/FEA-DOC-RECONCILE-1/gates-2.log` | `b6ada81e8` | `d6626c58c4a23cc312542836fccde0df07fa4845e131044d5655ec52d14767e3` | HISTORICAL |
| EV-RECON-GATE-R1 | AC8（历史） | `verification/FEA-DOC-RECONCILE-1/gates.log` | `d91dbe444` | `c5fcd1f78fdf233503acd2562ca093a5cb5a87cc03eaecba4dcd78ef9b579d7a` | HISTORICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `9b0683822`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| agent-output | `G:\CODEX\New Manga.workspace\agent-output\fea-status-2026-11-09\` | PRESERVE_REFERENCED | 原位 | 图/报告 6 文件 | 被本卡 §来源引用，保留 |
| temp | `%TEMP%\fea-shots`、`%TEMP%\chrome-prof-fea*` | NOT_APPLICABLE | — | — | 截图用临时 profile，OS 清理 |
| build/artifact | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 本轮无构建 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问用户数据 |

## Closeout Record

- **2026-11-09 / DSH（关账）**：7 项对账全部落地；AC1–AC9 MET。
- **Review 链（上下文独立，均非本会话）**：r1 `FEA-DOC-RECONCILE-1-r1.md` = changes_requested（P0=0/P1=1/P2=4/P3=8）→ 处置；第二审查者 `FEA-DOC-RECONCILE-1-review.md` = changes_requested（P0=0/P1=2/P2=4/P3=3）→ 处置；r2 `-r2.md` = **approved**（11 FIXED / 2 PARTIAL / 0 OPEN）；r3 `-r3.md` = **approved**（22 FIXED / 0 OPEN，新增 P3×5 非阻断：reviewer 引用、AC8 证据入口、gates-3 提交前标注、两卡 delivery_head 时点、`doc/reviews` 写域，除写域外均为表述性）。
- **门禁**：`check.ps1` PASS（3 warnings）EXIT=0；`check.ps1 -TaskPath` PASS EXIT=0；`verify_pins` 18/18 PASS EXIT=0；ledger 559 tracked / 0 untracked / 13 非终态（本卡关闭后重生成）；STATUS 3026 B/28 行、PLAN 6994 B/63 行（均在预算内）。
- **0 源码 / 0 契约字节 / 0 pin 重算**：diff 仅 `doc/**` 与 `verification/**`；`FEA-CONTRACT-FROZEN-*`、`doc/contracts/**`、18 pins 零改动。
- **append-only**：r1/第二审查者报告字节未改写；GOV-11/D07 只改 AC 勾选与标记（原 AC 文本逐字保留）、测试表 `NOT_RUN` 保留；IMMERSIVE/RUN-GRANT-2 为纯追加。
- **残余**：R-1…R-5 见 §残余，均不在本轮范围且已登记；PLAN 预算余 6 B/1 行为下一 Task 释放前的硬约束。
- **交付/集成**：`delivery_head` = `c22aea60c`（r3 复审 head，含全部对账内容）；本收口提交仅翻转状态与指针。


