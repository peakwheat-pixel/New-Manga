---
id: FEA-12-CORE-C04B-RESIDUAL-1
title: C-04b v1.1 residual 8 项记录收口（docs-only，0 pin；契约字节不动）
kind: documentation
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-scope-r1.md`（fresh subagent session `0fc94b7f…`；verdict **recommended**：docs-only 记录卡 0 pin，**不建议现在 UNFREEZE**；8 项分类 docs-only 1 / 契约措辞 6 / 代码+契约 1；精确 pin 口径 = C-04b 1/18 + M2-C1 仅记录型冻结契约而非 2/18）；**DSH 裁决（2026-11-07）**：采纳 A 方案（docs-only），不现在做 B/C/D；本卡只登记 residual、不改任何契约字节、不做 ① 代码修复
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（docs-only 窄面；未参与本卡起草；session 见 `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-1-r1.md`）
depends_on:
  - FEA-12-CORE
base_commit: 28a2826af
branch: null
worktree: null
integration_commit: 698ac9524
delivery_head: 698ac9524
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC-1 8 项逐项表**：冻结记录 §4A 扩成 `R-1…R-8` 表（位置/当前文本/问题/性质/影响/权威读法/是否需 UNFREEZE，行号以 `28a2826af` 为准）；与释放时字节一致；C-04b/M2-C1 字节未改。 <<MET>>
- [x] **AC-2 ⑥ 完全闭合**：新增 §1C 补 r1–r7 报告绝对路径（仓外 `...\workspace\FEA-12\unfreeze-*`）+ 大小 + 完整 sha256 + session（r2 未暴露如实注明）；r4–r7 与 §1B 前缀一致；§1B 原文保留。 <<MET>>
- [x] **AC-3 ③④ 的 0 pin 收口**：载体 §5F 只追加（§1–§5E 未改）写明 `separate/detached` 无定义、representative=字典序最小 artifact revision id（仅展示、不进 digest）、§1 行号为 v1.0 时点且现行以节名为准。 <<MET>>
- [x] **AC-4 ① 的 limitation**：§4A 新增 **L-3**（`library.py:1178-1190` page/chapter join vs `:1920-1926`/`:1218-1225` 的 `book_id`；正常数据无影响、损坏行多/少绑定；**未修**；需 UNFREEZE+实现卡）；**无**「已对齐/已修复」断言。 <<MET>>
- [x] **AC-5 ②⑤⑦⑧ 权威读法登记**：§4A R-2/R-5/R-7/R-8 + 载体 §5F 逐项写「契约字节未改；现行读法；规范修复待 UNFREEZE」（`§2.2` 为准、请求 `book_ids`、单条 `inventoryDigests[bookId]`、banner/history 仅批量、单条 manifest 取值）。 <<MET>>
- [x] **AC-6 零字节/零代码门禁与不夸大**：本卡提交（显式 pathspec）仅 4 docs + 证据 + 评审，并发 L-R11 `src/**` 不属本卡（P3-7）；C-04b/M2-C1 sha 不变；pins 18/18；check PASS；r1 approved P0/P1/P2=0（P3：8 项总，open=6/fixed=1/mitigated=1）；closeout 明确「仅 ⑥ 完全闭合，其余契约文本未改」；相邻精度项已标注不计入 8 项 AC。 <<MET>>

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

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-1..AC-6 | verification/FEA-12-CORE-C04B-RESIDUAL-1/EV.md | 423efa200 | 488f3b521d805be420235d510649462fead0669633163bc8d4d3862c8833e908 | CANONICAL |
| EV-02 | AC-6 | verification/FEA-12-CORE-C04B-RESIDUAL-1/logs/check-taskpath.log | 698ac9524 | b6d8bf6f31850b15596ea074d123ede2eba50c433e0c732cca7d9d22a3124f68 | CANONICAL |
| EV-03 | AC-6 | verification/FEA-12-CORE-C04B-RESIDUAL-1/logs/check.log | 698ac9524 | 1d53f0d1dcad5c0d2e07eb74790114615a55cc23dc0fd3830b6ae5bec759ff00 | CANONICAL |
| EV-04 | AC-6 | verification/FEA-12-CORE-C04B-RESIDUAL-1/logs/pins.log | 698ac9524 | bbd82df4d119205b7198d08acac40ad87418d7b54dab5cd9142c02932cae7128 | CANONICAL |
| EV-05 | AC-6 | verification/FEA-12-CORE-C04B-RESIDUAL-1/logs/scope-changed.log | 698ac9524 | d1aa609ba11a08f28cbc5d7da7225903d1464f7e6ce1f9e644266dec2710c2bc | CANONICAL |
| EV-06 | AC-6 | verification/FEA-12-CORE-C04B-RESIDUAL-1/logs/scope-stat.log | 698ac9524 | fdd7231f5d56002251f45aa9fa378d861335e9f3e2011ffad752920ed66f2e48 | CANONICAL |
| EV-07 | AC-6 | verification/FEA-12-CORE-C04B-RESIDUAL-1/logs/sha-check.log | 698ac9524 | 2e8e4a75f641ce44168ba9c57e499728b8402fd1aa77c6e64391c7ea3c5effca | CANONICAL |

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档（仓内） | - | NOT_APPLICABLE | - | - | 本卡仓内 0 删除/0 移动/0 归档；仅改冻结记录/载体 + 卡/评审/证据；仓外 `unfreeze-*` 报告只读实测（未移动/未改）；无残留进程 |

## Closeout Record（2026-11-07；Lead）

- **状态**：`done`；`delivery_head`/`integration_commit` = **`698ac9524`**（docs-only 收口提交：FROZEN-C04b §4A/§1C/§4B/§5 + 载体 §5F + 卡 + r1 评审 + 证据）。
- **AC 判定**：AC-1…AC-6 **全 MET**（无 PARTIAL/BLOCKED）。
- **Review 处置**：独立上下文 fresh subagent docs-only 审查 **r1 `approved`（P0=0/P1=0/P2=0；P3 共 8 项：open=6 / fixed=1（P3-1）/ mitigated=1（P3-7），均非阻断）**；报告 `doc/reviews/FEA-12-CORE-C04B-RESIDUAL-1-r1.md`（session `c66cd50f-…`；`reviewed_head=28a2826af`）。P3 处置：① EV diff stat `+41/−2`→`+39/−2`（**fixed**）；② §1C 路径为 workspace 相对路径 + r4–r7 `...` 缩写（保留：完整路径可由 `G:\CODEX\New Manga.workspace\FEA-12\unfreeze-*` 直达，sha 已给全）；③ r4–r7 session 前缀（保留：报告内已有完整 id）；④ 卡面 AC-2 措辞改指 §1C（已修）；⑤ 相邻精度项已标注「不计入 8 项 AC」（已修）；⑥ EV AC-6 措辞改为「closeout 记录须明确」（已修）；⑦ 并发 L-R11 `src/**` 改动（本卡提交已用显式 pathspec 隔离，**mitigated**，工作树注记保留）；⑧ `698ac9524` 内卡仍 ready / EV「结论待回填」（由 closeout 提交闭合）。
- **门禁数字**：`verify_pins.ps1` **18/18 PASS**（C04b `acc8f0e0…` 仍命中）；`check.ps1`（默认 + `-TaskPath`）**PASS(3 warnings)**；C-04b sha256 `acc8f0e0…`、M2-C1 sha256 `701093b5…` **与冻结记录一致（零字节）**；本卡提交仅 4 个 docs 文件 + 证据 + 评审；`src/**`/`apps/**`/`tests/**` **不属本卡提交**（并发 L-R11）。全量 pytest/.NET **NOT_RUN**（docs-only）。
- **limitations / follow-up**：**8 项中仅 R-6（⑥）完全闭合**；R-3/R-4 的 0 pin 部分已在载体 §5F 登记；**R-1/R-2/R-5/R-7/R-8 的规范修复仍待 UNFREEZE（另卡，未建立）**；**L-3**：① artifact 成员谓词代码偏差**未修**（正常数据无影响、损坏行多/少绑定；修复需 C-04b+M2-C1 UNFREEZE + 独立实现卡）。**不得**写「8 项全部关闭 / 契约已修复」。
- **Resource Manifest**：仓内 0 删除/0 移动/0 归档；仓外复核报告只读实测未移动。
- **指针清理**：Lead 在本轮 closeout 更新 STATUS/PLAN/TASK_LEDGER。
- **push**：随本轮 Lead 统一 push（PRE/POST hash、AHEAD 记录见 `doc/handoffs/DSH-HANDOFF-2026-11-06.md` §20）。
