---
id: GOV-EVIDENCE-PIN-REPAIR-1
title: "Canonical Evidence pin 失效巡检与 append-only 修复（含 EV-11）"
kind: governance
governance_version: 3
status: done
approval: dsh_lead_release_2026-11-16_by_codex_ruling_q1_d
suggested_owner: DSH
owner: DSH
reviewer: 独立上下文子 agent（未参与实施）
depends_on: [GOV-DECLARATION-SCAN-CLEANUP-1]
base_commit: 9f2db6463
branch: main
worktree: main
integration_commit: 97ab23245
delivery_head: 97ab23245
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/GOV-EVIDENCE-PIN-REPAIR-1
allowed_paths:
  - doc/tasks/GOV-EVIDENCE-PIN-REPAIR-1.md
  - tools/governance/audit_evidence_pins.py
  - tools/governance/evidence-pin-exceptions.json
  - tools/governance/tests/test_evidence_exceptions.py
  - tools/governance/check.ps1   # 仅新增受控例外通道（不动其它门禁）
  - tools/governance/tests/test_audit_evidence_pins.py
  - doc/tasks/FEA-11-HOST-AUTH-2.md
  - doc/reviews/GOV-EVIDENCE-PIN-REPAIR-1-*.md
  - verification/GOV-EVIDENCE-PIN-REPAIR-1/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/NEXT-SESSION-STARTER.md
---

# GOV-EVIDENCE-PIN-REPAIR-1

## 来源与目标

2026-11-16 声明债务收口（`GOV-DECLARATION-SCAN-CLEANUP-1`）在关闭记录里登记了一条**未修缺陷**：
`doc/tasks/FEA-11-HOST-AUTH-2.md` 的 `EV-11` 证据行记录了一个在本仓**无法复现**的 sha256。

DSH 就此派 Codex 出书面裁定（`doc/reviews/GOV-EVIDENCE-PIN-REPAIR-1-CODEX-RULING-2026-11-16.md`），裁定为
`APPROVED_WITH_CONDITIONS`：**Q1=D（C→B）**——先由 DSH 释放并冻结一张独立治理修复卡，再对终态卡
**append-only 追加** `EV-11-supersede` 行与说明，原行逐字保留；**Q3** 要求提供只读巡检命令用于发现同类问题，
先作为独立命令纳入证据验收、**不并入 `check.ps1`**，除非基准测量证明耗时可接受。

DSH 按 Q3 实现巡检后发现这不是孤例，因此本卡目标定为：

1. 提供**只读**巡检工具并自证其准确性（已知良好卡全 PASS、已知坏卡能报出）；
2. 给出**全仓基线测量**（行数 / 失败分类 / 受影响卡数），作为后续逐条判定与验收的锚点；
3. 按裁定对确认失效的 pin 做 **append-only** 修复（原行不动，新增 supersede 行 + 表下说明）；
4. 逐条判定失败项，区分「真实失效」与「历史形态可接受」，每批后失败数**单调不增**；
5. 上下文独立复核 + 门禁通过；决定是否并入 `check.ps1`（默认不并入）。

## 范围冻结

- 只允许**追加**证据行与说明；**不得**修改任何既有证据行的字节、不得改历史计数、不得放宽 `check.ps1`。
- 不得批量重算 pin 覆盖旧值；每条 supersede 行必须附可机械复核的依据（commit 可解析 + 64 位 sha256 + 与 blob 相等）。
- 本卡不处理「产品代码/测试」；`test.ps1` 副作用等属另一张卡。

## Acceptance Criteria

- [x] **AC1 巡检工具**：`tools/governance/audit_evidence_pins.py` 只读、无副作用；支持 `--json`/`--cards`，逐卡与全仓巡检可用。 <<MET>>
- [x] **AC2 全仓基线**：给出 canonical 行数、FAIL 分类计数、受影响卡数，并逐类抽样复核（真实失效 vs 工具误报）。 <<MET>>
- [x] **AC3 EV-11 修复**：append-only 追加 EV-11/12/13-supersede 三行（commit `5cbec0e8` + 原行记录值），表下说明改写；原行字节逐字不变；该卡 `check.ps1` PASS。 <<MET>>
- [x] **AC4 逐条判定与例外登记**：445 条逐条归因并登记受控例外（一行为一指纹，无按类豁免）；实测真实失效 4 条，33 张有登记项的卡全部 PASS。 <<MET>>
- [x] **AC5 独立复核**：上下文独立 Reviewer 四轮复核（REJECTED ×3 → APPROVED）；`check.ps1` 与 `-TaskPath` 均 PASS。 <<MET>>
- [x] **AC6 例外通道落地**：版本化 allowlist + `check.ps1` 精确匹配降级；资格校验为 commit 逐字 + 摘要有序列表精确比较；Resource 不豁免。 <<MET>>
- [x] **AC7 门禁接受 blob 行尾形态**：六列历史行按「工作树原始 → blob 原始 → 行尾形态」判定；混合行尾不产生派生；七列显式 basis 不变；7 项测试。 <<MET>>

## 测试要求

- `tools/governance/tests/test_audit_evidence_pins.py`：至少覆盖
  ① 64 位合格 pin 判 PASS；② 多摘要单元格（同时列 blob 与 worktree）不误报；③ commit 列写 `pending` 时按无 commit 处理；
  ④ 内容改 1 字节 ⇒ FAIL；⑤ 混合换行/非登记表示 ⇒ FAIL；⑥ 路径缺失 ⇒ FAIL。
- 巡检工具不得修改工作树（跑完 `git status` 必须干净）。

## 允许修改范围

见 frontmatter `allowed_paths`。

## 禁止范围

- 不得修改既有证据行字节、不得重算覆盖历史 pin、不得放宽 `check.ps1`、不得删除或弱化任何测试。
- 不得把巡检并入强制门禁而未先测量耗时。

## 附带发现（本卡不处理，但必须登记，勿丢）

- `doc/tasks/FEA-11-HOST-AUTH-2.md` 同一张表里 `FEA-11-HOST-AUTH-4.md` / `FEA-11-HOST-AUTH-5.md` 两行同样不可复现
  （巡检 line 107/108）——并入 AC4 判定，不作为孤例。
- Codex 裁定所据的题述把 EV-11 的值写成「40 位十六进制」，实测为 **64 位**（`4a7e1ca8…`，长度 64）；
  即它是**合法长度的 sha256**，但当前与任何字节表示都不匹配。裁定其余条款不受影响，已在采纳记录里更正。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC1-AC7 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac1-ac2-baseline-2026-11-16.log | 8db997f94 | 52599f301c5a6a8f8c02ecef438fc1fdfd7cbeb1fc7eed2f60b6ad5ab21c01dc | CANONICAL |
| EV-02 | AC1-AC7 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac3-ev11-supersede-2026-11-16.log | 65d97a077 | 4e714ec104504257589b8b0ca83821506bead5116b3c49fc2af1d5ac5fc64d62 | CANONICAL |
| EV-03 | AC1-AC7 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac4-batch1-fea11-host-auth-2-2026-11-16.log | 94747c4ad | be700ca225df4438e8e7d16f09ac10e0795b5994c7c55b2853ce760b9fbde7bc | CANONICAL |
| EV-04 | AC1-AC7 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac4-batch2-2026-11-16.log | 34f6b3eae | 5e8a82aca794dc0eb7a4b247446787821fa0bd109ada4caf925cfefd2ab3c625 | CANONICAL |
| EV-05 | AC1-AC7 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac4-batch3-2026-11-17.log | ce66a0df1 | 2ab6af10365006a6bac87a62bc58d04861ebb1ce0fe4cd55d5c9cec10a65474e | CANONICAL |
| EV-06 | AC1-AC7 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac4-batch4-2026-11-17.log | f78c0f2b9 | 9779356f64e0e37eaa0888bd5088485a6068aa12417989042055f238251345a8 | CANONICAL |
| EV-07 | AC1-AC7 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac4-batch5-2026-11-17.log | 5f14f06b0 | 77a7f5e22d6e72d742ba6581a9d90df0f88aa4cd701b636199cd472496c41377 | CANONICAL |
| EV-08 | AC1-AC7 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac4-batch6-2026-11-17.log | c19b3f1bf | 4c1974c31d7ff8ca0444789e6c9cc5a3a420ce05a37803ba920f7846bb436268 | CANONICAL |
| EV-09 | AC1-AC7 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac4-triage-2026-11-16.json | 519acea7a | abef0b9633cd721df87ffad161f28eb41c2cb2707a2c95e42d3222d5363cc0a1 | CANONICAL |
| EV-10 | AC1-AC7 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac4-triage-2026-11-16.md | 519acea7a | 7da754f5d64b564edc4eaae32b7429c6334026700fdad18c4fba8518e3789432 | CANONICAL |
| EV-11 | AC1-AC7 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac6-exception-channel-2026-11-16.log | 8fe6b7ca8 | 8d8b036f6de43f0a9559edbde1157c6eaa08c406732fb5cce932d400018146bd | CANONICAL |
| EV-12 | AC1-AC7 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac7-gate-eol-forms-2026-11-16.log | 35f87d915 | 39610524ef1b6dd27b7e0164678c35c4bb7969d0a0ca41e85f3a4e29e2f0f105 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| evidence-dir | verification/GOV-EVIDENCE-PIN-REPAIR-1 | PRESERVE_REFERENCED | verification/GOV-EVIDENCE-PIN-REPAIR-1 | verification/GOV-EVIDENCE-PIN-REPAIR-1/ac4-batch6-2026-11-17.log | 证据目录随仓库保留；2026-11-17 收口登记 |
| doc-only | — | NOT_APPLICABLE | — | — | 本卡只改仓库内文档/工具，未创建仓外 worktree 或临时目录 |

## Closeout Record

- **收口时间**：2026-11-17。
- **AC 状态**：AC1–AC7 全部 `<<MET>>`。
- **实测**：全仓 `check.ps1` PASS；33 张有登记项的卡全部 PASS；例外通道 13 项 + 批量证据 8 项 + EOL 7 项测试全过。
- **关键更正（记录在案）**：本 Task 期间三次把「证据失效」判得过重（只 hash 原始 blob、不认 CRLF 形态、不认 commit-only 合法 pin），
  445 条里真实失效只有 4 条；每次更正都写进了证据日志与 STARTER。
- **独立复核**：`doc/reviews/GOV-EVIDENCE-PIN-REPAIR-1-AC5-REVIEW-2026-11-17.md`（REJECTED ×3 → APPROVED）。
- **遗留（不在本 Task 范围）**：2 条带 class 的占位行与 15 条 `superseded` 卡的巡检口径，另需裁定。
