# Project Rebaseline Plan

## 2026-10-12 当前任务 DAG：H1 P2-1 保持 OPEN；ZCode 证据追溯已完成但阻塞

当前阻塞中的 H1 Task=`P02PRE-R1H-R6-ZCODE-H1`，状态=`in_review / DSH_REVIEW_CHANGES_REQUESTED`；Owner/Coordinator=Codex /root；final pre-run author=`agent_25b6e51e-a4ed-4bf0-be14-372029dfc4c0`；独立 Reviewer=DeepSeek Harness，session=`session-2e6e238c-1814-40b9-b0c6-b253f102296a`，verdict=`CHANGES_REQUESTED`（P0/P1/P2/P3=`0/0/1/6`）；非作者 Integrator/Adjudicator=Codex /root。ZCode 的 P2-1 evidence closure Task=`P02PRE-R1H-P2-1-EVIDENCE-CLOSURE` 已执行并标记 `blocked / EXECUTED_20261012 / BLOCKED_P2_1_OPEN`；ZCode CLI session=`sess_c297a288-813f-4dfa-92f1-bae7d37d05b8`，内置 Agent session=`agent_8886fd38-6ba0-41d4-a084-6ee8cf40dc8d`。H1 acceptance 与 X6 eligibility 仍 blocked。

P2-1 结论=`BLOCKED / P2-1 OPEN`：15 项中 2 项 status spans（`e-root-status`、`e-agy-status`）已由 Codex 逐 pin 核对并 byte-exact 重建；13 项没有可接受的 item-level raw source。报告=`C:\Users\49745\.codex\worktrees\p2-p2-1-zcode\New Manga\verification\P02\zcode-p02pre-r1h-p2-1-evidence-closure-report-20261012.md`（27065 / `DA3C419658AE6FD8FB42A93488666A622FF80DAAD5A565A5E92E0B2615C6AE43`）；Handoff 同目录，5733 / `456CD1E8B33B4DF1E3ECADB5BECF9D23AF613E83AB0A7B780514B3610ECA98DF`。13 项缺口使 DSH focused Review 条件不满足；两项 span 只作为部分候选，不关闭 P2-1。当前没有 READY 子 Task；如需继续查找 attempt1 stderr 提及的仓库外 CLI harness forensic 输出，须先由用户授权扩大只读范围。ZCode worktree 交付保持未集成、未提交。

H1 恢复点=`verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt6-zcode-handoff-20261012.md`。

Live Root=`G:\CODEX\New Manga`，`main@343895fb5f0329c0c07a7104ec321b698f967607` / tree=`e12bd627c307d4bf3c851dc09d0b82f97c86ec63`，`.git/index` SHA-256=`C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68`。固定 Git=`C:\Program Files\Git\cmd\git.exe` (`2.52.0.windows.1`)；受控 `--no-optional-locks status --porcelain=v1 -z --untracked-files=all -- . :(exclude).tmp.driveupload` 于 `2026-10-12T13:31:59Z` exit=0 / 1237 NUL / 85373 bytes / SHA-256 `D3042D8DE60C33C23B950ABB8B8FD26E6CF8F2A5AAFBF76E0EE12B0793026100` / stderr=0；末尾排除 path 未访问。相较上一份 Codex 快照 `1227 / 84670 / EC915022…`，新增 10 个 ZCode CLI probe/task dispatch 日志文件；更早历史 status 无逐路径基线，仍 `UNKNOWN / NOT_VERIFIED`，不归因给执行 Agent。PowerShell=`7.6.6`；Git 实测 `2.52.0.windows.1`，与 A6 Handoff 声称的 `2.48.1` 记录为版本差异，不宣称一致。

attempt1=`PRE_RUN_BLOCKED`，保留其四份原始证据；v2 四文件稳定两次读取，`PRE_RUN_PASS`，24 checks=`23 PASS / 0 FAIL / 1 NOT_VERIFIED`（`.tmp.driveupload` scope 按设计保持 `NOT_VERIFIED`），四个 attempt1 引用 pins 均逐项匹配实测。受保护文件前后均为 `57648 / 977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA`。dynamic process closure=`REQUIRES_ACTIVE_TEST / NOT_RUN`。Agy worktree 的 protocol/executor/Handoff pins 与给定值一致；Root 中三路径仍不存在，executor 未运行。

DSH=`0.2.0-rc.2`；无附件连通性探测回答“收到”、exit=0。正式 Review session 已完成，shell exit=0；response/stdout=`14078 / 6AAD7750AFABCCD5B159C69F40EF49149E3D3EBB1CA6613CD0FD91FDCB960C19`；Codex pre/post verification=`13/13 pins match`；Codex adjudication 接受 P2-1 为有效且未闭合，P3-1/P3-5 部分接受，其余 P3 findings 接受。ZCode P2-1 closure 报告与 Codex 非作者核验已完成；13 项 source 缺失，整体 P2-1 维持 OPEN，DSH focused Review 与 X6 均不派发。当前没有 READY 子 Task；若继续查找仓库外 CLI harness forensic 输出，须先获用户授权扩大只读范围。既有 Review 证据见 `verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.response.md`、`verification/P02/codex-p02pre-r1h-attempt6-zcode-h1-review-input-verification-20261012.json` 与 `verification/P02/codex-p02pre-r1h-attempt6-zcode-h1-review-adjudication-20261012.md`。X6 仍 `BLOCKED / NOT_RUN`。

Gate 原值不变：`private_registry_absence=UNPROVABLE`；Technical Gate=`NOT_SATISFIED`；Owner Risk Acceptance=`APPROVED`；Gate Disposition=`WAIVED_BY_OWNER`；Build Authorization=`AUTHORIZED_WITH_EXCEPTION`；`technical condition unmet; user explicitly accepted residual risk`。Build Gate=`BLOCKED`；Hard Build Barrier=`EFFECTIVE`；Build/Cargo=`NOT_RUN`；AC1–AC7=`BLOCKED / NOT_RUN`。

~~~mermaid
flowchart TD
  AUTH["Owner risk acceptance / waiver · recorded; not a technical PASS"]
  A4["A4 integration + Parser/selfcheck · DONE"]
  A5["A5 final pre-run · PRE_RUN_BLOCKED; executor NOT_RUN"]
  A6["A6 delivery · DONE_WITH_LIMITATIONS"]
  R6["DSH R2 Review + Codex adjudication · accepted with limitations"]
  V6["Codex Parser/selfcheck · PASS_WITH_EVIDENCE"]
  H1["H1 v2 final pre-run · PRE_RUN_PASS"]
  RV["H1 independent DSH Review · CHANGES_REQUESTED; P2-1 open"]
  ADJ["Codex input verification PASS; adjudication complete; H1 acceptance blocked"]
  PC["P2-1 evidence provenance · BLOCKED / 2 spans verified, 13 sources missing"]
  FR["Focused independent Review + Codex adjudication · NOT DISPATCHED; requires 15/15 closure candidate"]
  X6["One-shot executor + dynamic closure · BLOCKED / NOT_RUN; separate Task required"]
  POST["Post-run Review/adjudication · BLOCKED"]
  BG["Build Gate · BLOCKED"]
  BUILD["Build/Cargo · BLOCKED / NOT_RUN"]
  AC["AC1–AC7 · BLOCKED / NOT_RUN"]
  AUTH --> A4 --> A5 --> A6 --> R6 --> V6 --> H1 --> RV --> ADJ --> PC --> FR --> X6 --> POST --> BG --> BUILD --> AC
~~~
## 历史锚点与快照（ARCHIVE）

压缩前的完整唯一计划源保存在 [2026-10-12 REBASELINE_PLAN 快照](../archive/history/2026-10-12/REBASELINE_PLAN.md)。该历史副本不再授予当前排期或实现权限；当前 DAG 以上方为准。

### Architecture decision and future migration registration

历史注册正文见[归档快照](../archive/history/2026-10-12/REBASELINE_PLAN.md#architecture-decision-and-future-migration-registration)。当前目标架构唯一依据仍是 [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md)。

### 2026-09-28 任务盘点（当日快照；当前执行状态见 STATUS）

历史任务盘点见[归档快照](../archive/history/2026-10-12/REBASELINE_PLAN.md#2026-09-28-任务盘点当日快照当前执行状态见-status)。该快照不参与当前 READY DAG。

### M2 Acceptance Backlog (planning rows and explicit releases)

历史 backlog 见[归档快照](../archive/history/2026-10-12/REBASELINE_PLAN.md#m2-acceptance-backlog-planning-rows-and-explicit-releases)。当前状态以本文件上方 DAG 和 STATUS.md 为准。