---
id: FEA-D06-GAP
title: D06 四项缺口补齐（C-08 UNFREEZE）
kind: docs
governance_version: 3
status: done
approval: user_ruling_2026-11-01_activate_d06
suggested_owner: dsh
owner: dsh-lead
reviewer: c01b-reviewer
depends_on:
  - FEA-D07-UNBLOCK
base_commit: 1e0a98734
branch: null
worktree: null
integration_commit: 1027de616
delivery_head: 0119a8014
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-D06-GAP
allowed_paths:
  - doc/tasks/FEA-D06-GAP.md
  - doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md
  - doc/plan/FEA-CONTRACT-FROZEN-C08.md
  - doc/reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md
  - doc/reviews/FEA-D06-*.md
  - doc/checkpoints/**
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-D06-GAP/**
---

# FEA-D06-GAP：D06 四项缺口补齐

## 来源

用户 2026-11-01 裁决：**激活 FEA-D06-GAP，走 C-08 的 UNFREEZE 流程补齐四项，仅修改契约文档**。

背景：[FEA-GATE-READINESS-review](../reviews/FEA-GATE-READINESS-review.md) P1-1 指出 D06（Run 快照）六项声明范围中**四项无任何冻结契约承载**，导致 `G-DELETE-CONTRACT` 的 D06 条件不满足。迁延至今，D04/D05/D07 均已覆盖，**D06 是唯一剩余缺口**。

## 四项缺口与用户的起草要点

| # | 缺口 | 用户给的既有语义约束 |
|---|---|---|
| 1 | **控制 pending 状态** | 区分「控制请求已持久化」与「状态已改变」。pause/stop 已受理时，Run 仍可为 `running`，**不能提前显示暂停或结束**（M2-C1 `:203` 的 Running 行：pause 先持久化请求，当前不可安全中断的 Step 可完成，到安全边界后不再开始下一步） |
| 2 | **真实完成口径** | 明确**权威持久状态**、目标结果与统计的对应关系；**接受响应和事件均不能单独证明完成** |
| 3 | **retry** | 区分「**同键重放**」（M2-C1 `:200`，返回原 Run、不重取快照）与「**新建失败目标重试 Run**」（M2-C1 `:206`，`RetryFailedTargets` 新 Run + `source_run_id`）；**后者的快照来源仍须明确回答**，并对照 P11 |
| 4 | **断线 receipt** | 已有基础：M2-C1 `:200`「提交后响应丢失时，同键重放须找回原 Run」。须在此之上补**覆盖范围、查询方式与生命周期**；**`request_id` 不能充当去重键** |

## 验收标准

- [x] **AC1 控制 pending 条款**：定义「控制受理」与「状态变更」的区分；给出 Run 侧的 UI 不变量（不得因受理而显示暂停/结束）；引用 M2-C1 `:203` 不复写。 <<MET>>
- [x] **AC2 真实完成口径条款**：定义权威持久状态来源、完成判定（状态 + 目标结果 + 统计一致）、明确「`RunAccepted` 不证明完成」「事件不是状态真值」；引用 M2-C1 `:137`/`:902`/`:1060`。 <<MET>>
- [x] **AC3 retry 快照来源条款**：明确回答「`RetryFailedTargets` 的新 Run 是否复用源 Run 的快照」——分「目标集合」与「冻结上下文」两部分答；对照 P11 §3.3。 <<MET>>
- [x] **AC4 断线 receipt 条款**：覆盖范围（哪些命令）、查询方式（同键重放为主）、生命周期（随 Run History 保留）、**`request_id` 不作去重键**的明文禁止。 <<MET>>
- [x] **AC5 UNFREEZE 载体**：`doc/reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md` 登记四项补充、依据、复核状态。 <<MET>>
- [x] **AC6 独立复核** `approved`（P0/P1 = 0）。 <<MET>>
- [x] **AC7 C-08 重新冻结**：新 pin + 冻结记录 §1A/§1B 更新；`verify_pins.ps1` PASS。 <<MET>>
- [x] **AC8 D04–D07 完整覆盖检查**（表已建，待独立复核）：四项补齐后重跑完整覆盖核对（不是只看 D06），确认无其它缺口。 <<MET>>
- [x] **AC9 重新判定 `G-DELETE-CONTRACT`**：AC8 通过后才可关闭；**不引入「部分关闭」**。 <<MET>>

## 禁止范围

- **不改 M2-C1 字节**（只引用其既有冻结语义）。
- 不改 C-01b/C-04b/C-06/C-09/C-13/C-14 的冻结字节。
- 不改代码、不动用户数据、不 push。
- **不得在 AC8 完成前声称 D06 已覆盖**。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 条款 vs M2-C1 `:203` Running 行 | 文档 | NOT_RUN（本收口不重跑条款级对照） | `doc/reviews/FEA-C08-r12.md`（条款链 r9→r10→r12） |
| AC2 | 条款 vs M2-C1 `:137`/`:902`/`:1060` | 文档 | NOT_RUN（本收口不重跑条款级对照） | 同上 |
| AC3 | 条款 vs M2-C1 `:200`/`:206` + P11 §3.3 | 文档 | NOT_RUN（本收口不重跑条款级对照） | 同上 |
| AC4 | 条款 vs M2-C1 `:200` | 文档 | NOT_RUN（本收口不重跑条款级对照） | 同上 |
| AC5 | UNFREEZE 载体登记四项 + 依据 | 只读 | PASS | `doc/reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md`（sha256 `99c07fae…` @ `90e81f5cb`） |
| AC6 | 独立复核 `approved`（P0/P1 = 0） | 只读 | PASS | `doc/reviews/FEA-C08-r12.md` frontmatter：`approved` / 0 / 0 |
| AC7 | 重新冻结 + pin 校验 | 只读 | PASS | `verify_pins.ps1` 13/13；C-08 pin `453f993c…` |
| AC8 | D04–D07 完整覆盖表 | 文档 | PASS | `FEA-D04D07-COVERAGE-r3` approved |
| AC9 | `G-DELETE-CONTRACT` 判定 | 文档 | PASS | `doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md` |

> AC1–AC4 的**条款级语义验证**由 C-08 的既有复核链（r9 提 2 P1 → v6；r10/r11 记录同步；r12 `approved`）完成，属本轮之前的历史证据；**本收口没有重跑这些文档对照**，故按红线保留 `NOT_RUN`，不把未执行写成 `PASS`。本收口实际执行的是 AC5–AC9 的收口核对、证据复算与治理检查。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| E-C08-R12 | AC1–AC7 | `doc/reviews/FEA-C08-r12.md` | `44667d836` | `4d2053abe707dc886426379eed4b91d231abe51f231122b2261e2dce73a740ed` | CANONICAL |
| E-UNFREEZE | AC5 | `doc/reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md` | `90e81f5cb` | `99c07fae5a7e8060fa4fdc4c7da1a3f4220b25078491fbb64758bf992fa81114` | CANONICAL |
| E-D04D07-R3 | AC8 | `doc/reviews/FEA-D04D07-COVERAGE-r3.md` | `2ed4ed91a` | `7baba5491fc1e37b60255976094cd281a57c9fe5d87b06ac55291c7697de7fac` | CANONICAL |
| E-GATE-R3 | AC9 | `doc/reviews/GATE-DELETE-CONTRACT-CLOSURE-r3.md` | `0119a8014` | `f894839fb35151901d79a9011abbe9a1fd7ddc66e80cbaa5509c91f60f03b313` | CANONICAL |
| E-RES | Resource | `verification/FEA-D06-GAP/workspace-tmp-manifest.md` | `-` | `ebc8d80d23d13c8b7bff90c0d6bc39f6ae09f4ece2078683166a2decaf646b2d` | CANONICAL |

## Resource Manifest

文档 Task：仓库内无 worktree、无 task-env、无构建产物；**仓库外临时脚本确实存在**——`G:\CODEX\New Manga.workspace\tmp\` 有 32 个 2026-11-01 契约线一次性脚本/日志/截图，已逐项登记到 `verification/FEA-D06-GAP/workspace-tmp-manifest.md`（每项 sha256 + 关联 + 引用检查）。处置 `PRESERVE_UNKNOWN`：**不删除、不移动**（`add_c08_d06.py` 等生成了被冻结契约字节，删除会破坏其可复现性）。

**偏离登记（用户口径 vs 检查器约束）**：用户口头要求「Resource Manifest 用纯文本、不建表（参考 FEA-GOV-11）」。但 `check.ps1` 对 `done` Task 的 Resource Manifest 只接受**非空 6 列表**或 `verification/**` 下的单个 JSON 引用（`resourceRows.Count -eq 0` 即报 `DONE 必须逐项填写 Resource Manifest`；JSON 路线同样要求 `resources` 非空与 `process_check` 非空）。**「纯文本无表」在现行检查器下不可满足**，故保留纯文本说明并附真实表格（不虚构任何路径或哈希）。如需纯文本口径，须另立 governance Task 修改 `tools/governance/check.ps1`（`tools/**` 不在本 Task 范围）。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| doc-task | - | NOT_APPLICABLE | - | - | 仓库内无 worktree/task-env/artifact/build/temp；未访问用户数据 |
| temp-scripts | ..\New Manga.workspace\tmp | PRESERVE_UNKNOWN | ..\New Manga.workspace\tmp | verification/FEA-D06-GAP/workspace-tmp-manifest.md | 32 项逐条 sha256 见清单；无进程占用、不在 git 跟踪内、非用户数据；delete/move/migrate/archive 均为 0 |

## Closeout Record

- 2026-11-01 / DSH：AC1–AC9 全部 MET。C-08 v7 冻结 pin `453f993c…`；AC8 覆盖检查 r3 `approved`；AC9 关闭裁定 r3 `approved`（两 Gate 均 CLOSED）。
- 收口（R1 复核后修订，2026-11-01）：`doc/reviews/FEA-D06-CLOSEOUT-r1.md` 判 `changes_requested`（P1×3 / P2×5），本版逐项处置——R-001 证据覆盖改为 `AC1–AC7` 并补 `E-UNFREEZE`/`E-RES`；R-002 仓外 32 个临时脚本登记为 `PRESERVE_UNKNOWN` + 清单（含 sha256）；R-003 checkpoint 位置按用户指令保留 `doc/checkpoints/`，增列 `allowed_paths: doc/checkpoints/**` 并在 STATUS 登记为当前恢复点；R-004 三处指针同步为 `in_review`；R-005 `evidence_dir` 已实际创建；R-006 AC5/AC6/AC7 拆行；R-007 偏离已登记；R-008 checkpoint 头部加「计划记录非释放」声明。
- `delivery_head` = `0119a8014`（AC1–AC9 交付落盘提交）；`integration_commit` 与 `resource_closeout_status: complete` 在复核 `approved` 后的 `done` 提交回填。
- 证据口径：4 条 commit 型 evidence 的 path/commit/sha256 已逐项实核（worktree 与对应 commit blob 同 hash）；第 5 条 `E-RES` 为仓内清单文件，按 worktree sha256 校验（`-` commit，符合 check.ps1 规则）。
- 冻结字节：13 个受 pin 契约文件（12 份 `FEA-C*_DRAFT.md` + `FEA-C07_API_INVENTORY.md`）字节未动，`verify_pins.ps1` 13/13；`git diff` 的 `doc/plan/` 为空。
- 未跑项：AC1–AC4 的条款级对照本收口未重跑（见测试要求注），保持 `NOT_RUN`；未运行任何程序测试（纯文档 Task）。
- 资源：仓库内无 worktree/临时/构建产物；仓库外 32 项 `PRESERVE_UNKNOWN`（清单见 `verification/FEA-D06-GAP/workspace-tmp-manifest.md`）；未访问用户数据。
- 边界：不构成实现授权；不构成远端 push 授权；不改变任何冻结契约字节。
- 收口（2026-11-01）：R2 [approved](../reviews/FEA-D06-CLOSEOUT-r2.md)（P0/P1 = 0；P2×6 非阻断）；`status: done`、`integration_commit: 1027de616`、`resource_closeout_status: complete` 为**纯元数据回填**（未改 AC / 证据表 / 资源清单正文）；P2 技术债登记于 `doc/checkpoints/AUTONOMOUS-2026-11-01.md`。
