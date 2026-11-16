---
id: GOV-EVIDENCE-PIN-REPAIR-1
title: "Canonical Evidence pin 失效巡检与 append-only 修复（含 EV-11）"
kind: governance
governance_version: 3
status: in_progress
approval: dsh_lead_release_2026-11-16_by_codex_ruling_q1_d
suggested_owner: DSH
owner: DSH
reviewer: 独立上下文子 agent（未参与实施）
depends_on: [GOV-DECLARATION-SCAN-CLEANUP-1]
base_commit: 9f2db6463
branch: main
worktree: main
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GOV-EVIDENCE-PIN-REPAIR-1
allowed_paths:
  - doc/tasks/GOV-EVIDENCE-PIN-REPAIR-1.md
  - tools/governance/audit_evidence_pins.py
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

- [x] **AC1 巡检工具**：`tools/governance/audit_evidence_pins.py` 只读、无副作用；
  自证：对 `GOV-DECLARATION-SCAN-CLEANUP-1`（全 BLOB 基准）报 0 FAIL，对 `FEA-11-HOST-AUTH-2` 能报出失效行；
  支持 `--json`、`--cards`；记录耗时。 <<MET>>
- [x] **AC2 全仓基线**：给出 canonical 行数、FAIL 分类计数、受影响卡数，并**逐类抽样复核**至少 3 条
  （确认真实失效 vs 工具误报）。 <<MET>>
- [ ] **AC3 EV-11 修复**（裁定 Q1/Q2）：append-only 追加 `EV-11-supersede`（有效 commit + 64 位 sha256 且等于
  `git cat-file blob <commit>:<path>`）+ 表下说明「旧值在本仓无任何字节表示可复现，已被取代」；
  原行字节逐字不变；`check.ps1` 对该卡 PASS。
  <<PARTIAL: 前四款已完成（EV-11/12/13 三条 supersede 行 + 说明、0 删除、工具复核 SUPERSEDED=3）；
  唯「check.ps1 对该卡 PASS」不可达——该卡在单卡校验下**改动前就已 7 errors**（5 条 SHA 不匹配 + 2 条 Resource manifest 为「—」），
  append-only 不会让逐行校验转绿。可选路径：①改写原始行（裁定禁止）②让 check.ps1 支持 supersession（门禁变更，需另行裁定）。>>
- [ ] **AC4 逐条判定**：445 条失败逐条归类（真实失效 ⇒ supersede；历史形态 ⇒ 记录可接受依据），
  每批后 FAIL 数单调不增；判定表与巡检 JSON 一一对应。 <<PARTIAL: 未开始>>
- [ ] **AC5 独立复核**：上下文独立 Reviewer（未参与实施）复核；`check.ps1` 与 `-TaskPath` 均 PASS。 <<PARTIAL: 未开始>>
- [ ] **AC6 门禁决策**：按实测耗时决定是否并入 `check.ps1`（默认不并入），并记录理由。 <<PARTIAL: 未开始>>

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
