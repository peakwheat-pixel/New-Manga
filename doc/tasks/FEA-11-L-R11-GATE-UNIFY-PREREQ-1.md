---
id: FEA-11-L-R11-GATE-UNIFY-PREREQ-1
title: C-16 v1.7：§2.4「无 publication 行」口径澄清（legacy open / 新同步链缺行 fail-closed）
kind: contract
governance_version: 3
status: done
approval: 用户 2026-11-06「自动推进/全部授权/裁决交 Codex 或 DSH，无需用户介入」；独立 scope review `doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（fresh subagent session `5aa2c0cf…`；verdict **recommended**；方案 C：Core 单谓词 + 全链检测；**1/18 pin UNFREEZE**）；**DSH 裁决（2026-11-07）**：采纳 recommended，UNFREEZE 仅改 C-16 §2.4 `:90` 括注与 `:93` 过期陈述（同一 pin）；C-17 §3.3 `:171-173` 已冻结 fail-closed **零字节**；其余 17 pins 零改动；先契约后实现
suggested_owner: dsh
owner: dsh
reviewer: 独立上下文 fresh subagent（byte-level；不得参与本 UNFREEZE 起草；session 见 `doc/reviews/FEA-11-L-R11-GATE-UNIFY-PREREQ-1-r1.md`）
depends_on:
  - FEA-11-RENDITION-1
base_commit: 07a7d746a
branch: null
worktree: null
integration_commit: 2175238ab
delivery_head: 2175238ab
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1
allowed_paths:
  - doc/tasks/FEA-11-L-R11-GATE-UNIFY-PREREQ-1.md
  - doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-L-R11.md
  - doc/reviews/FEA-11-L-R11-GATE-UNIFY-PREREQ-1-*.md
  - doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C16.md
  - doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md
  - verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/**
out_of_scope:
  - 其它 17 份冻结契约字节（C-17/C-06/C-15/C-07/M2-C1 等零 diff）
  - wire 字段/命令集/能力/错误码/TTL/撤销语义/`PROTOCOL_MINOR=3`；schema/迁移/依赖
  - `src/**`、`apps/**`、`tests/**`（实现由 `FEA-11-L-R11-GATE-UNIFY-1` 负责）
  - L-R11 实现、`added` relation 缺行检测（plan receipt）、写面/章级面 gate 扩展
  - STATUS/PLAN/LEDGER（Lead 维护）；push（Lead 统一）
---

# FEA-11-L-R11-GATE-UNIFY-PREREQ-1：C-16 v1.7（§2.4 无 publication 行口径澄清）

> **状态：`ready`（DSH 已裁决 UNFREEZE 路径；本卡改 C-16 §2.4 两处行文（`:90` 口径 + `:93` 陈述）+ §0 版本面行
> + 头部状态/日期 + §10 条件 ⑨/变更记录（后三类为记录性），冻结记录/矩阵/载体，1/18 pin）。**
> `base_commit=07a7d746a`（本卡创建/释放时 HEAD；scope review 快照为 `3945e1f5c`）。
> 依据：`doc/reviews/L-R11-GATE-UNIFY-scope-r1.md`（独立 scope review，recommended）+ C-17 §3.3
> （`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:171-173`，已冻结「新同步 binding 缺 publication 行属于损坏，
> fail-closed，不能当作 legacy 放行」）+ RENDITION-1 L-R11（`doc/tasks/FEA-11-RENDITION-1.md:159`）。

## 目标

消除 **C-16 §2.4 规范句与 C-17 §3.3 的字面冲突**：C-16 `:90` 现写「无 publication 行按既有 open 处理」，
而 C-17 §3.3 要求「新同步 binding 缺行 fail-closed」。本卡把 `:90` 括注改为：

> 「沿用 Run 目标/commit guard 的**同一** gate 谓词，C-17 §3.3；**旧未参与同步且无 publication 行的 v7 binding
> 按既有 open 处理；新同步 binding 缺 publication 行属于损坏，fail-closed（C-17 §3.3），不得当作 legacy 放行**」

并同步修正 `:93` 的过期陈述（「publication gate 的两读面既有差异（L-R11）不属于本命令语义」→ 由 L-R11
统一；仍不引入第三套 gate 判定）。**不改任何 wire 字段/命令集/能力/错误闭集/TTL/撤销语义/`PROTOCOL_MINOR`/schema。**

## 范围（In / Out）

- **In**：`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`（v1.6 → **v1.7**：§2.4 `:90` 括注 + `:93` 陈述 +
  §0 版本面行 + 头部状态/日期 + §10 条件 ⑨/变更记录）；
  `doc/plan/FEA-CONTRACT-FROZEN-C16.md`（版本/pin/§1B/§11 记录）；`doc/plan/FEA-CONTRACT_FREEZE_MATRIX.md`（C-16 行）；
  载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-L-R11.md`；本卡/评审/证据。
- **Out**：其余 17 pins（C-17 §3.3 **零字节**——它已冻结正确语义）；`src/**`、`apps/**`、`tests/**`；实现
  （`added` relation 缺行检测需 plan receipt 或新持久标记，本卡不碰）；写面/章级面；STATUS/PLAN/LEDGER；push。

## Acceptance Criteria

- [x] **AC-T1 载体与最小 diff**：C-16 v1.7 变更范围 = §2.4 `:90` 括注 + `:93` 陈述 + §0 版本面行 + 头部状态/日期 + §10 条件 ⑨/变更记录（实测 1 file / 7 insertions / 6 deletions）；载体逐项落盘；C-16 新 sha256 `67286eec…` 与 frozen pin 一致。 <<MET>>
- [x] **AC-T2 独立 byte-level 复核**：fresh subagent（独立上下文、未参与起草）**r1 `approved`（P0=0/P1=0/P2=0/P3=7 非阻断）**；报告 `doc/reviews/FEA-11-L-R11-GATE-UNIFY-PREREQ-1-r1.md` 入库。 <<MET>>
- [x] **AC-T3 pins 18/18**：`verify_pins.ps1` **18/18 PASS**（C-16 新值 `67286eec…`，其余 **17 项 UNCHANGED** 实测）；`check.ps1`（默认 + `-TaskPath`）**PASS(3 warnings)**。 <<MET>>
- [x] **AC-T4 零漂移**：C-17/C-06/C-15/C-07/M2-C1 及其余契约 blob 零 diff（仅 C-16 变化）；`src/**`、`apps/**`、`tests/**`、schema/迁移/依赖零 diff；无新错误码/命令/能力/`PROTOCOL_MINOR`。 <<MET>>
- [x] **AC-T5 证据与不夸大**：EV（实跑数字）、Resource Manifest、卡面 closeout 完整；**未**宣称实现已完成/`L-R11` 已关闭/C-17 §3.3 已满足（本卡只是让契约文本与 C-17 一致）。 <<MET>>

## 依赖与下一步

- 依赖：`FEA-11-RENDITION-1`（done，L-R11 登记来源）。
- 完成后：释放 `FEA-11-L-R11-GATE-UNIFY-1`（Core 单谓词实现，0 pin；depends_on 本卡 + `FEA-11-RUN-GRANT-2C`）。
- 预登记 limitation（实现卡承担，本卡仅登记）：`L-R11-a`（`relation='added'` 缺行链检测不可见 → plan receipt 未实现）、
  `L-R11-b`（写面/章级面仍 pending-only）、`L-R11-c`（映射既有错误 family，无专用码）、`L-R11-d`（不自动修复损坏行）、
  `L-R11-e`（优先真实 v7→v8 fixture）。

## Canonical Evidence

| evidence_id | AC | 路径 | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-T1..T5 | verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/EV.md | 2175238ab | dd58c31ffabcd7a4b672e2d1f9a8dd1c35f2dbe8a872f4017ea865dfb7b35949 | CANONICAL |
| EV-02 | AC-T1..T5 | verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/logs/check-taskpath.log | 2175238ab | 3e42b0169ea993d0005f305e5f59639fade448ff31114179960be2fa7678d17f | CANONICAL |
| EV-03 | AC-T1..T5 | verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/logs/check.log | 2175238ab | 3e42b0169ea993d0005f305e5f59639fade448ff31114179960be2fa7678d17f | CANONICAL |
| EV-04 | AC-T3 | verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/logs/pins.log | 2175238ab | bbd82df4d119205b7198d08acac40ad87418d7b54dab5cd9142c02932cae7128 | CANONICAL |
| EV-05 | AC-T1/T4 | verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/logs/unfreeze-diffstat.log | 2175238ab | b1d21fec7430c9180c28afef4e7300e8ba2e02996ca5acad67678bffd6b22874 | CANONICAL |
| EV-06 | AC-T1 | verification/FEA-11-L-R11-GATE-UNIFY-PREREQ-1/unfreeze.diff | 2175238ab | 037ef4db95bb3cc392ed69dd59a3fcd9518915ce3d9e79b647fa52b832317db3 | CANONICAL |

## Resource Manifest

| resource_type | 资源 | disposition | 目标 | 完整性 | 引用/进程检查结果 |
|---|---|---|---|---|---|
| 无删除/移动/归档（仓内） | - | NOT_APPLICABLE | - | - | 本卡仓内 0 删除/0 移动/0 归档；仅改 C-16/冻结记录/矩阵/载体/卡/证据；工作区临时 diff 快照在 `.workspace\L-R11\unfreeze-review\`（无独有数据，保留）；无残留进程 |

## Closeout Record（2026-11-07；Lead）

- **状态**：`done`；`delivery_head`/`integration_commit` = **`2175238ab`**（C-16 v1.7 UNFREEZE 提交：C-16 字节 + FROZEN-C16 + 矩阵 + 载体 + r1 复核报告 + 证据 + 卡面 P3-05 修正）。
- **AC 判定**：AC-T1…T5 **全 MET**（无 PARTIAL/BLOCKED）。
- **Review 处置**：独立上下文 fresh subagent byte-level 复核 **r1 `approved`（P0=0/P1=0/P2=0/P3=7 非阻断；session `9bc4c117-…`；reviewed_head `07a7d746a`；worktree `67286eec…`）**；P3 处置：P3-01 提交隔离（本提交只 stage 包内文件，排除 `doc/STATUS.md`、`doc/handoffs/DSH-HANDOFF-2026-11-06.md`、并发 C-04b scope review）、P3-02 EV 措辞、P3-05 卡面元数据、P3-06 载体 §3 限定、P3-07 diff CRLF 归一化说明 —— 均已落地；**P3-03/P3-04（C-16 §0 `:17` 范围歧义、§10 ⑨ 完成式）保持现状**（改字节需新 pin/复核），登记后续 UNFREEZE 候选，不阻断本次冻结。
- **门禁数字**：pins **18/18 PASS**（C-16 `67286eec…`，其余 **17** 实测不变）；check（默认 + `-TaskPath`）**PASS(3 warnings)**；C-16 diff **1 file / 7 insertions / 6 deletions**；18 契约 blob 仅 C-16 变化（其余 17/17 与 HEAD 相同）；`src/**`/`apps/**`/`tests/**`/`tools/**`/`doc/contracts/**` 零 diff；`git diff --check` EXIT=0。全量 pytest/.NET **NOT_RUN**（契约-only；由实现卡门禁承担运行时回归）。
- **limitations / follow-up**：`L-R11-a…e` 由实现卡 `FEA-11-L-R11-GATE-UNIFY-1` 承担并登记；P3-03/P3-04 为后续 UNFREEZE 候选；**契约就绪 ≠ 实现/产品可用**，不得写成「L-R11 已修复 / C-17 §3.3 已实现」。
- **Resource Manifest**：仓内 0 删除/0 移动/0 归档；工作区临时 diff 快照保留（无独有数据）。
- **指针清理**：Lead 在后续 closeout 提交更新 STATUS/PLAN/TASK_LEDGER 并释放 `FEA-11-L-R11-GATE-UNIFY-1`（status proposed → ready）。
- **push**：随本轮 Lead 统一 push（PRE/POST hash、AHEAD 记录见 `doc/handoffs/DSH-HANDOFF-2026-11-06.md` §18/§19）。
