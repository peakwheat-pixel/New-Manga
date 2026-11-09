---
id: FEA-DOC-RECONCILE-1
title: FEA 线文档对账（STATUS 四表 DDL 口径、C11-PREREQ-1 DAG 行、GOV-11/D07 关闭、BRIDGE 裁决、卡级注记）
kind: governance
governance_version: 3
status: in_progress
approval: 用户 2026-11-09 指令「做文档对账」（承接 `FEA-STATUS-2026-11-09` 检查发现的 1/2/4 项，并入 3/5/6 项）；DSH 范围冻结：只改文档与卡级状态，0 源码、0 契约字节、0 pin 重算、0 push
suggested_owner: dsh
owner: dsh-lead
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审；指派于交付后，session 记入 `doc/reviews/FEA-DOC-RECONCILE-1-r1.md`）
depends_on: []
base_commit: 9b0683822
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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
| 1 | `STATUS:11` 写「FEA-12 四表 DDL 未冻」 | 改为「四表 DDL 已冻（C-15 v7 + FEA-11-PREREQ-1 v8+）」 | `FEA-CONTRACT-FROZEN-C15.md:43,50`；`FEA-11-PREREQ-1.md:45,65`；`tests/fea11/test_v8_migration.py` |
| 2 | `FEA-C11-PREREQ-1` 卡 done、DAG 行仍 `approved（待集成收口）` | PLAN 行翻 `done`（集成 `b7018e19b`） | 卡 Closeout 2026-11-02：交付 `b7018e19b` 已在 main，证据 sha256 一致 |
| 3 | `FEA-GOV-11` 长期 `in_progress`（等 4 项裁决） | AC1–AC3 标 `<<MET>>` + 关闭记录 + `done` | `ADJ-2026-11-01-FEA-DECISIONS.md`：R=C1=D/C3=是、U-04 批准、U-05a 纳入、U-05b 保留；C-01b/C-02/C-03/C-11 已 FROZEN；FEA-01-FREEZE-1 done |
| 4 | `FEA-D07-UNBLOCK` AC8 为 `[ ] <<MET>>`（矛盾），状态 `in_progress` | AC8 改 `[x] <<MET>>` + 证据 + `done` | `GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md`（2026-11-01 CLOSED） |
| 5 | `FEA-07-IMMERSIVE-F11-1` limitation「默认 v2 壳无 F11 入口」已由 `FEA-07-V2-F11-1` 收口，卡未记录 | append-only 关闭该条 limitation；status 保持 `closed_with_limitations` | `FEA-07-V2-F11-1` done（`9b0683822` 链，2K 复验） |
| 6 | `FEA-11-RUN-GRANT-2` title 仍带「proposed，待依赖」而 status=done | 追加对账注记（不改 title 字节） | 卡 front matter `status: done` |
| 7 | `FEA-02-BRIDGE` 无卡、无 DAG 行 | PLAN 明确裁决：不独立释放（由现有装配与 FEA-05/06/07 生命周期断言覆盖），无缺口 | 方案 §15.6；`FEA-04.md:46`；`FEA-07-RESIDUAL-2` 标题含生命周期断言 |

## Acceptance Criteria

- [x] **AC1 STATUS 四表 DDL 口径**：`STATUS:11` 不再声称未冻，且四个表名/版本可追溯。 <<MET>>
- [x] **AC2 C11-PREREQ-1 DAG 行**：`REBASELINE_PLAN` 该行 `done` + 集成 `b7018e19b`，与卡 Closeout 一致。 <<MET>>
- [x] **AC3 GOV-11 收口**：AC1–AC3 标 `<<MET>>` 并引裁决记录；`status: done`；测试表不再 `NOT_RUN`。 <<MET>>
- [x] **AC4 D07-UNBLOCK 收口**：AC8 一致性修复（`[x] <<MET>>`）+ Gate 关闭证据；`status: done`。 <<MET>>
- [x] **AC5 IMMERSIVE limitation 关闭记录**：追加一节记录「v2 壳入口」limitation 由 V2-F11-1 关闭；status 保持 `closed_with_limitations`（其余 limitation 不动）。 <<MET>>
- [x] **AC6 RUN-GRANT-2 注记**：卡内追加 title 历史描述说明。 <<MET>>
- [x] **AC7 BRIDGE 裁决**：PLAN 写明不独立释放及依据，不留悬空节点。 <<MET>>
- [x] **AC8 门禁不降**：`verify_pins` 18/18、`check.ps1` PASS、ledger 重生成、STATUS/PLAN 未超防膨胀预算、0 源码/契约字节改动。 <<MET>>
- [ ] **AC9 独立 Review**：非本会话的独立上下文审查交付 head。 <<PARTIAL: 待指派>>

## 禁止范围

- 不改 `doc/plan/FEA-CONTRACT-FROZEN-*` / `doc/contracts/**` / 18 pins 的任何字节。
- 不改任何既有 `doc/reviews/**`、`verification/**` 字节；不改 `FEA-07-AC5-NATIVE-1`（用户动作未复位）与 `FEA-06-RESIDUAL-1`（残余承接未变）。
- 不把「done」写成「可发布」；本轮不推进 S5、不释放 FEA-13/14/15。
- 不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1–AC7 | 逐项 diff 对照上表事实依据 | 只读 + 文档 | PASS | 本卡 §对账清单 |
| AC8 | `pwsh -NoProfile -File tools/governance/check.ps1` | 仓库根 | PASS（3 warnings，预算内） | `verification/FEA-DOC-RECONCILE-1/gates.log` |
| AC8 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | 仓库根 | PASS 18/18 | 同上 |
| AC8 | `python tools/governance/task_ledger.py --write` | Python 3.14 | PASS（ledger 重生成） | `doc/TASK_LEDGER.md` |
| AC9 | 独立 Review（fresh subagent，只读） | 交付 head | NOT_RUN | `doc/reviews/FEA-DOC-RECONCILE-1-r1.md` |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-RECON-STATUS | AC1,AC3,AC4,AC5,AC6 | `doc/STATUS.md` | `-` | `db73b5236301591fd51e67a0d740a2db4a3966498040c3512c340003a35dcfe2` | CANONICAL |
| EV-RECON-PLAN | AC2,AC7 | `doc/REBASELINE_PLAN.md` | `-` | `816e6e1d8df512eff27293a27479408709a5966ad4e9374424007bb26a196891` | CANONICAL |
| EV-RECON-GOV11 | AC3 | `doc/tasks/FEA-GOV-11.md` | `-` | `ace803570181ca8502286ec5d70cf1c676d2662dd372a55de72ccd2af86b9fa7` | CANONICAL |
| EV-RECON-D07 | AC4 | `doc/tasks/FEA-D07-UNBLOCK.md` | `-` | `32386b2c998fff325e573b2d5640a9c877a20ceb77b09858c48d868ebca7c181` | CANONICAL |
| EV-RECON-IMMERSIVE | AC5 | `doc/tasks/FEA-07-IMMERSIVE-F11-1.md` | `-` | `3fa51eadbe0c9ec6ab93d87d2b00ce3dc1fe0a0dc063d435585426a7a60bf59d` | CANONICAL |
| EV-RECON-RG2 | AC6 | `doc/tasks/FEA-11-RUN-GRANT-2.md` | `-` | `83d15cbd086ae30323aff8cde51c25186dbba42377a5ffeaf9f7de6739b9dfd3` | CANONICAL |
| EV-RECON-GATE | AC8 | `verification/FEA-DOC-RECONCILE-1/gates.log` | `-` | `c5fcd1f78fdf233503acd2562ca093a5cb5a87cc03eaecba4dcd78ef9b579d7a` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `9b0683822`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| agent-output | `G:\CODEX\New Manga.workspace\agent-output\fea-status-2026-11-09\` | PRESERVE_REFERENCED | 原位 | 图/报告 6 文件 | 被本卡 §来源引用，保留 |
| temp | `%TEMP%\fea-shots`、`%TEMP%\chrome-prof-fea*` | NOT_APPLICABLE | — | — | 截图用临时 profile，OS 清理 |
| build/artifact | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 本轮无构建 |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问用户数据 |

## Closeout Record

- 待关闭时填写。
