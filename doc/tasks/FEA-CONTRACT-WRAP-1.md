---
id: FEA-CONTRACT-WRAP-1
title: 契约线收尾（L-3 Errata + PLAN 预算卫生）
kind: governance
governance_version: 3
status: in_review
approval: user_instruction_2026-11-01_autonomous_closeout
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-C14-DRAFT
base_commit: ff432e97c
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/FEA-CONTRACT-WRAP-1
allowed_paths:
  - doc/tasks/FEA-CONTRACT-WRAP-1.md
  - doc/plan/GATE-CLOSURE-RULING-2026-11-01.md
  - doc/plan/FEA-CONTRACT-FROZEN-C04b.md
  - doc/plan/FEA-CONTRACT-FROZEN-C08.md
  - doc/plan/FEA-CONTRACT-FROZEN-C09.md
  - doc/plan/FEA-CONTRACT-FROZEN-C13.md
  - doc/REBASELINE_PLAN.md
  - doc/PLAN-HISTORY.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/**
  - doc/reviews/FEA-WRAP-*.md
  - verification/FEA-CONTRACT-WRAP-1/**
---

# FEA-CONTRACT-WRAP-1：契约线收尾（L-3 Errata + PLAN 预算卫生）

## 来源

用户 2026-11-01 指令：契约线最后两项收尾——**L-3 Errata**（依据 [GATE-DELETE-CONTRACT-CLOSURE-2026-11-01](../plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md) §4 的 Errata 表）与**文档预算卫生**（`doc/REBASELINE_PLAN.md` 触发 80% 预算告警）。

边界：**不 push、不改任何已冻结契约字节、不改 Gate 状态、不删改用户数据**。Errata 的处置方式是「**只追加注记、不删原文**」，冻结契约正文一律不动。

## 验收标准

- [x] **AC1 L-3 Errata**：`doc/plan/GATE-CLOSURE-RULING-2026-11-01.md` 的 `:63`/`:111` 与三份冻结记录（`FEA-CONTRACT-FROZEN-C04b.md` / `-C08.md` / `-C13.md`）的旧「D07 缺多项 / Gate 保持 OPEN / C-09 仍 blocked」口径均**追加 errata 注记、保留原文**；`FEA-CONTRACT-FROZEN-C09.md` 的 L-1 残留项追加处置注记；13 份冻结契约 DRAFT 字节 **0 改动**（`verify_pins.ps1` 13/13 且 pin 值不变）；**C-13 草案 `:203` 保持原字节**。增补判据（R1 复核建议）：**新增/改动的相对链接按所在目录可解析（0 死链）** + **注记中的 `:行号`/`§小节` 与现行文件一致** + **注记与裁定 §4 逐行对齐并给出「该表述是否真的存在」核对结论**（C-08 属「表里有、文件里没有」，已在注记写明）。 <<MET>>
- [x] **AC2 PLAN 预算**：`doc/REBASELINE_PLAN.md` 压缩到 **< 5600 B 且 ≤ 50 行**（实测 **2257 B / 32 行**）；历史终态节点**原样迁入** `doc/PLAN-HISTORY.md`（31 行，`git diff --numstat` = `38 0` 纯新增）；**不删仍被引用的当前状态**（活动程序、READY 行、当前 DAG、终态约束段全部保留）；压缩后 `check.ps1` PASS。 <<MET>>
- [x] **AC3 指针与治理检查**：`doc/STATUS.md` / `doc/REBASELINE_PLAN.md` / `doc/TASK_LEDGER.md` 指向真实状态；`check.ps1`（默认 + `-TaskPath`）PASS、`verify_pins.ps1` 13/13；`doc/checkpoints/AUTONOMOUS-2026-11-01.md` 含每项一行、待裁决与收尾（`done` 提交同批更新第 5 行结果）。 <<MET>>

## 禁止范围

- **不改 13 份冻结契约草案字节**（改则须 UNFREEZE + 重算 pin，本 Task 无此授权）。
- 不改 Gate 状态（`G-CONTRACT` / `G-DELETE-CONTRACT` 已 CLOSED，`G-DELETE-IMPL` 仍 OPEN，不自我放宽）。
- 不改代码、不动用户数据、不 push、不改其它 Task 的既有证据正文（只追加本 Task 的注记）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 5 文件 diff 只含 `+` 行、旧文原样保留 | 只读 | PASS | `git diff 593141773..14e6e6a3c`：49 插入 / 0 删除；R1 复核复算一致 |
| AC1 | 相对链接按所在目录解析 | 只读 | PASS | 死链 0（`500aa6b27` 修 2 处 D07 解环链接后复跑） |
| AC1 | 注记行号与现行文件一致 | 只读 | PASS | `:63`/`:111`/`:112`、C04b §3/§4、C08 `:55`/`:65`、C13 `:62-63`/`:74`、C09 `:68`/`:74` 逐条核对 |
| AC1 | 13 份 pin 契约字节 0 改动 | 只读 | PASS | `verify_pins.ps1` 13/13；`doc/plan/` 受 pin 文件 diff 空 |
| AC2 | PLAN 字节/行数实测 | 只读 | PASS | 6777 B/57 行 → **2257 B/32 行**（< 5600 B / ≤ 51 行） |
| AC2 | 历史节点原样迁入 | 只读 | PASS | `doc/PLAN-HISTORY.md` 新增 38 行、删除 0 行；31 行取自 `HEAD:doc/REBASELINE_PLAN.md` 原行 |
| AC2 | 压缩后 `check.ps1` | 只读 | PASS | PASS (2 warnings)，PLAN 预算 WARN 消失 |
| AC3 | 指针一致性 + 两命令 | 只读 | PASS | 见 `verification/FEA-CONTRACT-WRAP-1/closeout-check.md` |

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-WRAP-ERRATA-R1 | AC1 | `doc/reviews/FEA-WRAP-ERRATA-r1.md` | `500aa6b27` | `0d183364c0f885985f9a83a94245a856c98f02ce9fa1f356c53178b19fc26adb` | CANONICAL |
| E-ERRATA-DOC | AC1 | `doc/plan/GATE-CLOSURE-RULING-2026-11-01.md` | `500aa6b27` | `ae4a432b72fd17b370a1d8bb509a33498f1d07d7782ebbd28d4b1f4d01500c89` | CANONICAL |
| E-PLAN-HISTORY | AC2 | `doc/PLAN-HISTORY.md` | `-` | `8e292d43c4c30584bca76d3aa3c4127e1cb551ae6535c6ecba6ce3e05b87efaf` | CANONICAL |
| E-WRAP-CHECK | AC2,AC3 | `verification/FEA-CONTRACT-WRAP-1/closeout-check.md` | `-` | `6aeaf45e7e52c8d55e07841c3ac02874feac183cbaf53ea72d894b7d13691087` | CANONICAL |

## Resource Manifest

文档 Task：仓库内无 worktree、无 task-env、无构建产物。仓外一次性脚本与 2026-11-01 契约线共用同一批残留（`G:\CODEX\New Manga.workspace\tmp\`），逐项 sha256 见共享清单 `verification/FEA-D06-GAP/workspace-tmp-manifest.md`，处置 `PRESERVE_UNKNOWN`（不删除，保留冻结字节可复现性）。

**偏离登记**：用户口头要求「Resource Manifest 用纯文本、不建表」；但 `check.ps1` 对 `done` Task 只接受非空 6 列表或 `verification/**` 单个 JSON，「纯文本无表」不可满足。故保留纯文本说明 + 真实表格（不虚构路径/哈希）。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 仓库内无 worktree/task-env/artifact/build/temp；未访问用户数据 |
| temp-scripts | ..\New Manga.workspace\tmp | PRESERVE_UNKNOWN | ..\New Manga.workspace\tmp | verification/FEA-D06-GAP/workspace-tmp-manifest.md | 共享清单 32 项；无进程占用、不在 git 跟踪内；delete/move/migrate/archive 均为 0 |
| verification-log | - | PRESERVE | - | verification/FEA-CONTRACT-WRAP-1/closeout-check.md | 只读命令实跑记录已入库；无待清理资源 |

## Closeout Record

- 2026-11-01 / DSH：AC1–AC3 MET。AC1 由 `14e6e6a3c` 执行、`500aa6b27` 修 P2；AC2 压缩见 `closeout-check.md`；AC3 指针与检查见同文件。
- 收口（2026-11-01）：`status: in_review` → 待独立复核 `doc/reviews/FEA-WRAP-CLOSEOUT-r1.md`；`delivery_head` 与 `integration_commit` 按复核结论回填（`done` 提交为纯元数据 + 指针/checkpoint 回填）。
- 边界：不构成 Gate 变更；不构成实现授权；不构成远端 push 授权；冻结契约字节 0 改动（13/13）。
