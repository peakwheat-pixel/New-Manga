---
id: FEA-12-CORE-C04B-RESIDUAL-1
title: C-04b v1.1 residual 8 项记录收口（docs-only，0 pin；契约字节不动）
kind: documentation
governance_version: 3
status: ready
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（fresh subagent session `0fc94b7f…`；verdict **recommended**：docs-only 记录卡 0 pin，**不建议现在 UNFREEZE**；8 项分类 docs-only 1 / 契约措辞 6 / 代码+契约 1；精确 pin 口径 = C-04b 1/18 + M2-C1 仅记录型冻结契约而非 2/18）；**DSH 裁决（2026-11-07）**：采纳 A 方案（docs-only），不现在做 B/C/D；本卡只登记 residual、不改任何契约字节、不做 ① 代码修复
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（docs-only 窄面；未参与本卡起草；session 见 `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-1-r1.md`）
depends_on:
  - FEA-12-CORE
base_commit: 28a2826af
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-12-CORE-C04B-RESIDUAL-1
allowed_paths:
  - doc/tasks/FEA-12-CORE-C04B-RESIDUAL-1.md
  - doc/plan/FEA-CONTRACT-FROZEN-C04b.md
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md
  - doc/reviews/FEA-12-CORE-C04B-RESIDUAL-1-*.md
  - verification/FEA-12-CORE-C04B-RESIDUAL-1/**
out_of_scope:
  - C-04b/M2-C1 契约字节（任何 UNFREEZE；§1 表/§2.0/§2.1/§2.2/§5.11.1a/§5.13/banner/history）
  - 删除协议重写、ADJ-001/Gate 语义、错误码/行为变更
  - `src/**`、`apps/**`、`tests/**`（含 ① artifact 成员谓词代码修复 —— 另立实现卡）
  - FEA-12-CORE 实现/测试/证据返修；STATUS/PLAN/LEDGER（Lead 维护）；push（Lead 统一）
---

# FEA-12-CORE-C04B-RESIDUAL-1：C-04b v1.1 residual 8 项记录收口（docs-only，0 pin）

> **状态：`ready`（DSH 裁决 docs-only；`base_commit=28a2826af`；Owner=`dsh`）。**
> 依据：`doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（recommended；8 项逐项定位与性质判定）+
> `doc/tasks/FEA-12-CORE.md:284` ②（8 项转后续文档卡）+ `doc/reviews/CONTRACT-UNFREEZE-2026-11-05.md` §5E
> （r6 复核 0×P0 + 1×P1 + 8×P2；路径 A：字节不动、如实登记 residual）。
> **本卡不修契约字节**：C-04b 仍 `acc8f0e0…`、M2-C1 仍 `701093b5…`；`verify_pins.ps1` 必须仍 18/18。

## 目标

把 C-04b v1.1 的 8 项 P2 residual **如实、可审计地**收口到冻结记录与载体（**不改 C-04b/M2-C1 任何字节**）：
① 冻结记录 §4A 一行 residual 扩成 `R-1…R-8` 逐项表；② 补 r1–r3 复核报告 sha（⑥ 完全闭合）；③ 载体 §5F
追加 errata（③④ 的 0 pin 收口）；④ 登记 **L-3**（① artifact 成员谓词代码偏差，**未修**）；⑤ 登记 ②⑤⑦⑧ 的
「权威读法 + 契约字节未改 + 规范修复待 UNFREEZE」；⑥ 零字节/零代码门禁与不夸大。

## Acceptance Criteria

- [ ] **AC-1 8 项逐项表**：冻结记录 §4A 扩成 `R-1…R-8` 表，逐项给「位置（节名 + 行号，行号以 `28a2826af` 为准）、
  当前文本摘录、问题、性质（docs/契约措辞/代码）、影响、当前权威读法、是否需 UNFREEZE」；与释放时字节一致；
  不得改 C-04b/M2-C1 字节。 <<PENDING>>
- [ ] **AC-2 ⑥ 完全闭合**：§1B 补 r1–r3 复核报告的绝对路径 + 完整 sha256 + reviewer/session（不可得时如实注明）；
  r4–r7 注明前缀口径或补全；用 `Get-FileHash` 复核并记录实测值。 <<PENDING>>
- [ ] **AC-3 ③④ 的 0 pin 收口**：载体 §5F（**追加**，不改已批准正文）写明：`separate/detached` 无定义、现行
  representative 规则（字典序最小 artifact revision id，仅展示、不进 digest）、C-04b §1 表行号是 v1.0 时点
  且现行以节名为准；日期/来源可追溯。 <<PENDING>>
- [ ] **AC-4 ① 的 limitation**：冻结记录 §4A 新增 **L-3**：`src/infrastructure/sqlite/library.py:1178-1190`
  的 page/chapter join 取 artifact vs 删除路径 `:1926` 的 `media_artifacts.book_id = 本书`；正常数据无影响、
  损坏行可能多绑定/少绑定；**未修**，修复需独立实现卡；**不得**写「已对齐/已修复」。 <<PENDING>>
- [ ] **AC-5 ②⑤⑦⑧ 权威读法登记**：逐项写明「契约字节未改；现行读法/实现取值如下；规范修复待 UNFREEZE」，
  至少覆盖：`:44` 以 §2.2 为准、首确认=**请求** `book_ids`（预览不缓存）、单条取 `inventoryDigests[bookId]`、
  banner/history 仅**批量**、单条 manifest 取值 `batch_id`=uuidv4/`original_book_ids=[book_id]`/集合级值且
  retry 只校验逐书 digest。 <<PENDING>>
- [ ] **AC-6 零字节/零代码门禁与不夸大**：`git diff --name-only` 仅命中 `allowed_paths`；C-04b sha256 仍
  `acc8f0e03d42fd574837cc556e9fa546ba355d7f45a5eefc7bd7b9fe8c16968f`、M2-C1 仍
  `701093b5282228fdc791843146bf9459338e6ac1829ce3a801c72470fc938b7f`；`verify_pins.ps1` **18/18**、
  `check.ps1` PASS；独立 docs-only review **approved（P0/P1=0）**；closeout 明确「8 项中仅 ⑥ 完全闭合；
  ③/④ 的 0 pin 部分已登记；其余契约文本未改」。 <<PENDING>>

## Out

C-04b/M2-C1 字节、任何 UNFREEZE、`src/**`/`apps/**`/`tests/**`、删除协议/ADJ-001/Gate 语义、FEA-12-CORE 返修、
STATUS/PLAN/LEDGER、push。

## 门禁

`verify_pins.ps1` 18/18；`check.ps1`（默认 + `-TaskPath`）PASS；C-04b/M2-C1 sha256 与冻结记录一致（不变）；
`git diff --name-only` ⊆ allowed_paths；独立 docs-only fresh subagent review approved（P0/P1=0）。

## 依赖与下一步

- 依赖：`FEA-12-CORE`（done；residual 来源）。
- 完成后：若 DSH 决定改契约措辞 → 另立 `FEA-12-CORE-C04B-RESIDUAL-2`（UNFREEZE，C-04b 1/18 + M2-C1 记录型 rev）；
  若决定修 ① 代码 → 另立 `FEA-12-CORE-C04B-RESIDUAL-3`（implementation，0 pin）。
  本卡**不承诺**这些后续卡已建立。
