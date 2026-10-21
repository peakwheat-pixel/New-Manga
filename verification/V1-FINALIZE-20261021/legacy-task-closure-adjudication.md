# 非 v1 遗留 Task 收口裁定（2026-10-21）

**授权**：用户 2026-10-21 goal「以完成本项目为目标……全部授权 dsh……尽量减少增加额外任务，尽量收口任务，完成第一版软件」。
**执行者**：dsh（Coordinator）。**性质**：收口裁定与状态记录，不是 Review，不改变历史证据、不删除文件、不改写旧 Review/pin。

## 1. 原则

1. 只改变 `doc/tasks/<id>.md` 的 frontmatter `status`（以及终态 Task 必需的 closeout 字段），并在文末追加「历史收口」说明；不删正文、不改历史结论。
2. 状态语义：
   - `cancelled`：从未交付/未集成，且已被架构或 Plan 取代（旧栈、早期草案、非 v1 范围）。
   - `superseded`：已有替代 Task 或已限定关闭的上游，遗留链不再需要。
   - `closed_with_limitations`：本 Task 有真实交付/证据，但 AC 未全部达成，限制如实保留。
3. 不把「未运行/未集成」写成 PASS；不把遗留 Task 的 AC 勾选补成已完成。
4. 每个终态化 Task 若 `governance_version: 2`，同时满足治理检查器的终态要求（`resource_closeout_status: complete`；Resource Manifest 机械校验可执行）。旧 lifecycle v1 Task 只改状态并留说明。

## 2. 旧架构遗留（AD-001 冻结，`cancelled`）

AD-001 规定：PySide6/QML 旧栈仅保留为历史证据，不再释放 Legacy 实现、诊断或修复 Task；父 Task `T3.2.1` 已 `closed_with_limitations`（`SUPERSEDED_BY_M2`）。以下 13 项均为旧栈修复/证据整理，从未进入 v1 交付：

`T3.2.1-REPAIR-3`、`-4`、`-5`、`-6`、`-7`、`-8`、`-9`、`-10`、`-11`、`-12`、
`-15-reader-export-lineage`、`-16-bookshelf-page-count`、`-17-mock-local-pipeline-smoke`。

## 3. 早期规划草案（`cancelled`）

以下草案从未授权/认领/实施（`approval: pending_user_review`，owner 多为 Qoder——已于 2026-10-08 退出项目），范围已被 Rebaseline Plan 与 M2 架构取代：

`TASK-022`、`TASK-025`、`TASK-026`、`TASK-027`。

## 4. P02 取证链（`superseded`）

`P02` 已 `closed_with_limitations`（Plan 行「P02 WebView / P08 / 限定关闭」）。其后继 forensic capture 链（R0/R1H/Round6）不再作为 v1 发布门禁；未交付/未集成的部分保持原样，证据保留在 workspace 与 Git 历史：

`P02PRE-R0S2`、`R0S4`、`R0S5`、`R0S6`、`P02PRE-R1H`、`P02PRE-R1H-P2-1-EVIDENCE-CLOSURE`、
`P02PRE-R1H-R6-EXEC-A4`、`-A5`、`-A6`、`P02PRE-R1H-R6-ZCODE-H1`。

## 5. 已被替代的交付 Task（`superseded`）

| Task | 替代/依据 | 说明 |
|---|---|---|
| `P22` | `P22-REBASE-1`（`done`，已集成） | 原 P22 交付 `92093792` 未合并；`verification/PROJECT-ROADMAP-RELEASE/REPORT.md` 裁定按当前 main 最小移植，P22-REBASE-1 已完成该角色。原交付保留为历史，不声称已集成 |
| `P19-UI-FIX-3` | `FEAT-CREATE-1`–`FEAT-CREATE-4`（均 `done`） | 空书架新建作品/章节的能力已由 FEAT-CREATE 链交付：前端 `BookshelfPage` 通过 `library_create_book` 创建并有测试；本 Task 未执行但目标已被覆盖 |
| `GOV-DEBT-CLEANUP-1` | `GOV-DEBT-CLEANUP-2`、`GOV-UNTRACKED-BACKLOG-1`、`GOV-PIN-LINEAGE-1`（均已终态） | 历史 pin 失效/未入库证据的清理已被后续治理 Task 部分承接；剩余为历史证据，不阻塞 v1；Plan 行同步更新 |

## 6. 本 Task 完成后关闭（`closed_with_limitations`）

| Task | 交付 | 保留限制 |
|---|---|---|
| `P19-AC3-1` | 全域安全边界扫描（AC3/AC5/AC6/AC7 PASS；矩阵与 17 项证据；已集成 `7b1fcc45a`） | AC1 请求侧（58/58 未知 key 被接受）、AC2 返回侧（`settings_*` 回显绝对路径）、AC4 错误侧（21/51 闭合投影）为扫描发现的**产品缺陷**，本 Task 按边界只报告不修复；后续由 SEC/P15-HOST 等 Task 处理。保留 `PARTIAL` 语义，不声称 AC 全 PASS |
| `RUST-ENV-BASELINE-1` | 环境基线修复与实测：M2RC1_PYTHON 固定、source 套件 150 passed/0 failed/1 ignored、packaged 套件 12 passed/0 failed（exit 0）；并发现/修复真实缺陷（recycle-bin 命令 ACL 缺失，已提交） | AC2 基线 `8bf3ae30` 本轮未重跑（历史基线不重写）；AC1 的「缺配置自检」未改测试代码，仅记录运行口径。详见 `v1-verification-20261021.md` |

## 7. 仍未收口（下一轮处理，不伪装已完成）

- `P02-NEW-TIME-X6`、`-BUILD-CARGO`、`-POSTRUN-REVIEW`：`approved`，P02 遗留观测/构建链；其 Resource Manifest 存在大量历史 `same/pending` 值，需按当前实际资源重写后才能终态化。
- `P09-MANAGED-READ-ROOT-TRUST-1`：`proposed`，真实安全加固（读路径 root 信任）；未进入 v1 范围，保留为 backlog。
- `WORKSPACE-CLEANUP-TOOL-HARDENING-1`：`proposed`，P1 安全根因修复；需 Codex 冻结范围后释放。

## 8. 验证方式

1. 每个 Task 改动可用 `git diff` 逐项复核：仅 frontmatter `status`/终态字段 + 文末说明。
2. `doc/TASK_LEDGER.md` 由 `tools/governance/task_ledger.py --write` 重生成；治理检查须 PASS。
3. 任何被关闭 Task 的原始正文、证据路径、历史 Review 与 pin 均未删除或改写。


## 9. r1 修正（2026-10-21，dsh）

- **P15-CORE-1**：原写 `cancelled`/"未交付"不准确。其范围已拆分为 `P15-CORE-1A/1B/1C`（均 `done`，commit `9232802c0`/`6cf3c8209`/`52b0974ad`），Core 命令已实现并接线；Task 已改为 `superseded`，并指向真实 `verification/P15-CORE-1/resource-manifest.json`。
- **P19-AC3-1**：限制说明精确到 successor —— 仅 AC2 由 `SEC-FIX-PATH-ECHO-1`（`done`）修复；AC1/AC4 未修复、无专项承接 Task。
- **P19-UI-FIX-3**：补充 `FEAT-CREATE-4` AC6 真实 GUI/UIA 证据覆盖其 AC1–AC5 目标；本 Task 自身未执行。
- **GOV-DEBT-CLEANUP-1**：明确 AC1 完成、AC2/AC3/AC4/AC6 未全部完成；`superseded` 仅表示不再作为 v1 门禁，不表示完成。
- **RUST-ENV-BASELINE-1**：AC4 分类修正为 12+7+2+1=22；证据 EOL 统一为 LF 并重算 pin（旧 CRLF hash 见 rework 对照）。
- 上文原始裁定文本保留，不回写。
