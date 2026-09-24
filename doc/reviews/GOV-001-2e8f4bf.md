---
task_id: GOV-001
reviewer: DeepSeek Harness（独立非作者 Review）
author: Codex
base_commit: 1e8cb1157c987945316351728f725073b8b109f9
reviewed_head: 2e8f4bf951ad8a16af50300463f990d325b768e6
handoff_commit: 5a16d8aaa0a9a9362cef6bd2e96d0dbd79e63c62
handoff_doc: doc/handoffs/GOV-001-2e8f4bf.md
decision: approved
---

# Review：GOV-001 — Architecture Decision Registration Gate（Delivery `2e8f4bf` / Handoff tip `5a16d8a`）

本报告由 **DeepSeek Harness** 独立作出，非本登记的作者，依据
[09 协作协议](../09_COLLABORATION.md) §6 与 [Review 模板](../templates/REVIEW.md) 编写。
所有结论均在本报告列出的命令、于独立 Reviewer worktree
`G:/CODEX/New Manga.worktrees/GOV-001-deepseek-review`（分支
`agent/deepseek/GOV-001-review-5a16d8a`，检出 Handoff tip `5a16d8a`）中现场得出，
未采信交付方 Handoff 与 Task 运行记录的自述。本次 Review 不修改作者分支
`codex/architecture-decision-registration`、不改写任何交付物或历史证据、不合并 `master`、
不修改 Task / STATUS / Plan，也不实施或集成 GOV-001。

## 范围与依据

| 项 | 值 |
|---|---|
| 本 Task | [GOV-001](../tasks/GOV-001.md)（`kind: governance`，`status: in_review`） |
| 固定 Base | `1e8cb1157c987945316351728f725073b8b109f9`（`master` / `origin/main`，2026-09-25） |
| 固定 Reviewed Head | `2e8f4bf951ad8a16af50300463f990d325b768e6`（`docs(architecture): register accepted desktop target and planned migration gate`） |
| 固定 Handoff Commit / 分支 tip | `5a16d8aaa0a9a9362cef6bd2e96d0dbd79e63c62`（`docs(governance): hand off architecture registration for independent review`；相对 `2e8f4bf` 仅追加 `doc/handoffs/GOV-001-2e8f4bf.md` 并回填 `doc/tasks/GOV-001.md`） |
| 作者分支 / worktree | `codex/architecture-decision-registration` / `G:/CODEX/New Manga.worktrees/architecture-decision-registration`（审查时 status 空、HEAD=`5a16d8a`） |
| 被审要求来源 | 用户 2026-09-25 批准的 `React + TypeScript + Tauri + Python Core` 目标；用户裁决 A（Legacy Production Baseline Closure）与裁决 B（Qoder = Frontend/UI Owner） |
| 覆盖文件 | `AGENTS.md`、`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/GOV-001.md`、`doc/handoffs/GOV-001-2e8f4bf.md` |

**未审到的部分**（明确记录）：① 未独立复算 `verification/T3.2.1/**` 底层证据（本次变更未触碰）；
② 未运行产品测试（交付为纯文档登记，无代码/测试/Schema/依赖改动，按 §6 元数据提交口径免跑）；
③ 未 `fetch`，不主张远端服务器状态，仅核对本地 `origin/main` ref。

## 固定点与范围核验

```text
git rev-parse --show-toplevel            → G:/CODEX/New Manga.worktrees/GOV-001-deepseek-review
git branch --show-current                → agent/deepseek/GOV-001-review-5a16d8a
git rev-parse HEAD                       → 5a16d8aaa0a9a9362cef6bd2e96d0dbd79e63c62
git merge-base --is-ancestor 1e8cb11 5a16d8a → exit 0
git rev-list --count 1e8cb11..5a16d8a    → 2（无夹带提交）
git diff --check 1e8cb11..5a16d8a        → exit 0（无空白错误）
```

`git diff --name-status 1e8cb11..5a16d8a`（8 路径，无 `D`/`R`）：

```text
M AGENTS.md   M doc/00_INDEX.md   M doc/12_ROADMAP.md   A doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md
M doc/REBASELINE_PLAN.md   M doc/STATUS.md   A doc/handoffs/GOV-001-2e8f4bf.md   A doc/tasks/GOV-001.md
```

受保护路径过滤（`doc/tasks doc/handoffs doc/reviews verification src tests packaging requirements*`）
仅得到两条 `A`：`doc/tasks/GOV-001.md`、`doc/handoffs/GOV-001-2e8f4bf.md`。
即：`src/**`、`tests/**`、`packaging/**`、`requirements*`、`verification/**`
及全部历史 Task / Handoff / Review 证据 **零修改、零删除**。全部 8 个路径均落在
[GOV-001](../tasks/GOV-001.md) `:36-40` 自声明的允许范围内（`AGENTS.md` 于 `:38` 明确列出）。
被审分支树中 `frontend/`、`src-tauri/`、`package.json`、`Cargo.toml`、`tauri.conf.json` 命中数为 **0**。

## Standards（可选视角 · executed）

依据本仓库记录在案的标准核对：

- [09 协作协议](../09_COLLABORATION.md) §4 `:65` 的状态机 `proposed → ready → in_progress → in_review → approved → done` 中 `in_review` 合法；GOV-001 `status: in_review` 合规，且最后一条 AC（`:32`）保持未勾选，未自宣 `done` → **符合**。
- §3 `:54` 允许 Codex 维护 `doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/STATUS.md` 的**状态、Task 导航与链接**：本次对三者的改动正是导航登记，未改需求、契约或代码范围 → **符合**。
- §5 `:82-88` Handoff 命名与字段、在 delivery head 之后以文档提交追加、不要求文件包含自身 hash → **符合**。
- §5.1 `:96-114` 下一任务建议七要素（Task / Agent / Recovery point / Scope / Deliverables / Verification / Forwardable instruction）齐备，且 Owner 与 Reviewer 不同、未臆造 worktree/branch（写明"待 Codex 创建"）、明写"不等于任务释放" → **符合**。
- §6 `:153,:170` Review 固定 base 与 reviewed_head、findings 带级别/文件/行/复现/建议 → 本报告执行。
- §6 `:177` 纯元数据归档提交无需重跑产品测试 → 适用。
- 仓库未记录标准的方面（本交付为治理文档，主要是措辞与导航完整性），适用判断项而非硬性违规，见 Findings 中 F-001～F-006，均已标注为 MINOR/NOTE。

## Spec（可选视角 · executed）

来源为 [GOV-001](../tasks/GOV-001.md) `:28-32` 的 AC 与用户批准的架构目标：

| AC | 要求 | 实测证据 | 结果 |
|---|---|---|---|
| AC1 `:28` | AD-001 准确记录四层职责、强制边界、Current/Target、增量迁移与 parity、Qt headless 审计、SQLite 单一写者、大二进制 IPC 边界 | `AD-001:19-24`（四层权威表）、`:28-36`（七条约束）、`:11-17`（Current/Target 分节）、`:40-42`（审计矩阵 `KEEP/DECOUPLE/REPLACE/LEGACY/UNVERIFIED`） | PASS |
| AC2 `:29` | Plan 登记 M2 `PLANNED / NOT_RELEASED`，只提一个研究/审计 successor；STATUS 与索引可导航，不改唯一 Active Task | `REBASELINE_PLAN:22-28`；`STATUS:38-40`；`00_INDEX:7`；`12_ROADMAP:8-10`；`STATUS:16` 仍为唯一 Active Task | PASS |
| AC3 `:30` | T3.2.1 Gate、REPAIR-13 与历史证据保持原状态；无代码/测试/打包/依赖/Schema/React-Tauri 初始化改动 | 见「T3.2.1 保护」与上方范围核验 | PASS |
| AC4 `:31` | 待裁决的 Legacy Closure 范围与 React UI Owner 明列；remote 漂移只记录 | `AD-001:44`、`AD-001:45`、`AD-001:46`；`REBASELINE_PLAN:28` | PASS |
| AC5 `:32` | 固定交付、Handoff、diff 检查、路径核对与非作者 Review | 本报告 + `review_report_commit` 构成本项证据；Task 状态保持 `in_review` 未提前收敛 | PASS（本报告） |

未发现 scope creep：diff 中不存在来源未要求的行为改动。

## Architecture 面结论

**PASS。** 用户批准的 `React + TypeScript + Tauri + Python Core` 被忠实登记，且目标与现实的边界清晰：

- 四层权威与职责（`AD-001:19-24`）：React/TS=Presentation（禁直接 SQLite/OCR/Domain）、Tauri/Rust=Desktop shell 与 system bridge（**明写 "Rust carries no domain business logic and is not a DB writer"**，`:22`）、Python Core=业务/持久化权威（**"Core must ultimately run headless"**，`:23`、`:34`）、SQLite=Persistent source of truth（React 与 Rust 不得成为独立 DB writer，`:24`）。
- 强制约束齐备（`:28-36`）：**No big bang rewrite** / Incremental Strangler（`:30`）；**Feature Parity 后才可删除 Legacy QML**（`:30`、`:32`，并要求 Implementation+Tests+Visual/Behaviour Verification+Parity Evidence+授权发布决定）；**Large binary 不进入普通 JSON/Base64 IPC**（`:33`，要求后续 spike 选定传输并验证容量/生命周期/安全）；Packaging 证据基线绑定（`:36`）。
- Python Core 保留策略正确（用户检查 7）：`AD-001:31` 明确"**不为替换 UI 而重写** `src/domain/**`、`src/application/**`、`src/ports/**`；`src/infrastructure/**` 仅在审计确认适用处复用"，`:34` 将既有 Qt 影像/渲染依赖标为 `MIGRATION_AUDIT_REQUIRED` 且**不预先判定全部不适合**，`:40-42` 给出 Audit → Decouple → Reuse 路径。**未要求**重写 Domain / Application / Ports / SQLite。
- 事实性抽验：`src/` 下 **22** 个 `.py` 文件 import `PySide6`；`src/ui/viewmodels/**`（QObject）、`src/application/export/pdf_qt.py`（QPdfWriter）、`src/infrastructure/rendering/qt_compositor.py`、`src/bootstrap/app.py` 真实存在；`AD-001:42` 的六个审计目录 `src/{domain,application,ports,infrastructure,bootstrap,ui}` 全部存在。**无臆造路径。**
- CURRENT_REALITY / TARGET_INTENT 分离：`AD-001:11-13` 明确当前生产与 T3.2.1 candidate 为 **Python + PySide6/QML + SQLite**，`:15-17` 才是 React/Tauri。全文无任何把 React/Tauri 写成"当前实现"的句子；`AGENTS.md:35` 同口径并注明旧技术栈表述待独立 Rebaseline。
- SoT 关系未出现第二套体系：`AD-001:9` 自我从属（Plan 为唯一规划源、STATUS 为实时执行源，D02/QML 映射/NFR/AC 仍描述 legacy 基线直至另行释放的 Rebaseline Task），`REBASELINE_PLAN:17-20` 原文未变。唯一登记缺口见 F-001（MINOR）。

## Verification 面结论

**PASS。** 本节各命令均在 Reviewer worktree 内实际执行（见「验证」表）。关键结论：
Scope 与受保护路径、commit 拓扑、空白检查、React/Tauri 初始化缺失、历史证据只读性、
M2 未释放性、T3.2.1 保护、152 条本地链接全部可解析 —— 均为 PASS。
产品测试按纯文档登记口径记为 **NOT_RUN（不适用，见 §6 `:177`）**，不冒充 PASS。

### T3.2.1 保护（逐点）

| 检查点 | 证据（文件:行） | 结果 |
|---|---|---|
| Full Release Gate 仍 OPEN | `AD-001:13`；`REBASELINE_PLAN:28`、`:137`；`GOV-001:63` | 未改动 |
| AC3 `BLOCKED` 未被偷改 PASS | `AD-001:13`（"AC3 is BLOCKED at image import"）；`STATUS:23` 该行在本次 diff 中未被修改 | PASS |
| REPAIR-13 未被取消/改写 | `AD-001:13`；`REBASELINE_PLAN:28`；`STATUS:16`；`doc/tasks/T3.2.1-REPAIR-13.md` 未被修改 | PASS |
| GOV-001 未自行裁决 Closure | `AD-001:13`（"neither closes, narrows, cancels nor redefines that Gate"）、`:44`；`REBASELINE_PLAN:28`（"until then the original Gate applies"） | PASS |
| PyInstaller/QML Evidence 未被外推为 Tauri Evidence | `AD-001:36`；`REBASELINE_PLAN:28` | PASS |

### M2 治理

`REBASELINE_PLAN:26` 与 `AD-001:40` 均为 `M2 — Desktop Architecture Migration: PLANNED / NOT_RELEASED`；
`REBASELINE_PLAN:26` 明写"**does not release any React, Tauri, IPC or Python migration implementation**"、
"**not ready or authorized to start**"。`STATUS:40`、`00_INDEX:7`、`12_ROADMAP:10` 同口径。
无 React/Tauri 初始化，无 Migration implementation authorization，
无任何把 M2 写成 `READY` / `IN_PROGRESS` 的位置（全量关键词扫描 0 命中）。
唯一 successor 为 `research / audit` 型 Headless & Qt Coupling Audit，且标注未授权启动。

### 用户裁决 A / B 的登记余量（只核查，不改 GOV-001）

- **裁决 A（Legacy Production Baseline Closure）**：现有 GOV-001 **允许**后续安全登记。
  `AD-001:44` 将其保留为 `USER_DECISION_REQUIRED`，给出"完整跑完原 Gate"或"重定义 Legacy Closure 边界"两个选项，
  并附"**Until the user decides otherwise through a separate authorized governance change, the original Gate remains in force**"；
  `REBASELINE_PLAN:28` 同口径。用户数据/源文件安全边界在 `AD-001:35`（source-file safety、Managed Copy、
  human edits、Lock、current/pinned Revision、recoverable task state）保留；Legacy 基线可复现性由
  `AD-001:36`（QML/PyInstaller 证据仅适用于 legacy closure）+ 既有 Release Gate 记录支撑。
  **哪些旧 Gate 可 defer 未被 GOV-001 自行裁决**，交由后续 Governance Task —— 满足用户"不能由 Reviewer 私自改 Gate"的约束（本 Review 亦未改）。
- **裁决 B（Qoder = Frontend/UI Owner）**：GOV-001 **未错误提前裁决角色**。
  `AD-001:45` 把 React UI ownership 列为 `USER_DECISION_REQUIRED`（"Qoder, Zcode or feature-based allocation … The user chooses in a later release decision"），
  `REBASELINE_PLAN:28` 复述"existing roles remain unchanged"，`GOV-001:57` 同样标注待用户裁决；
  `AGENTS.md` 角色段未被修改，Codex 仍保留 Architecture / Shared Contract / Integration。
  仅候选清单未列 Antigravity，见 F-004（NOTE）。

## Findings

无 P0/P1（BLOCKING/MAJOR）。以下 1 项 MINOR（≈P2）与 5 项 NOTE 均不阻塞集成。

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| F-001 | MINOR（≈P2） | `doc/00_INDEX.md:62`（"Source of Truth 按问题区分"表 `架构及数据怎么约束` 行） | AD-001 未进入本仓库唯一的 SoT 映射表；该行仍只指向 D02/D03/D06，未声明 AD-001 是 TARGET_INTENT 的权威位置。影响：只查该表的 Agent 可能把 D02 当作未来目标架构的权威，或误判存在两套架构权威。`00_INDEX:7` 指针块与 `AD-001:9` 的自我从属已大幅缓解，故不构成第二套体系 | `git show 2e8f4bf:doc/00_INDEX.md` 第 62 行原文 | 追加一句：`未来目标架构见 AD-001（TARGET_INTENT / 未释放实现）；D02 仍描述当前基线`。**建议并入** `REBASELINE_PLAN:28` 已提议的 Architecture Documentation Rebaseline Task，从而无需对已批准 head 做增量复审 | open（deferred 建议） |
| F-002 | NOTE | `doc/tasks/README.md:7`（"Current Codex-owned closeout" 导航行） | 该文件属 Codex 默认元数据维护范围（§3 `:54`），其导航行仍只提 T3.2.1/REPAIR-13，未提 GOV-001。因 `GOV-001:36-40` 冻结的 allowed paths 未含此文件，不改属范围合规选择，非越界 | `Select-String -Path doc/tasks/README.md -Pattern 'GOV'` → 0 命中 | 后续元数据提交补 1 行导航 | open |
| F-003 | NOTE | `doc/REBASELINE_PLAN.md:3`（Status 头行） | 头行仍为 `T3.1.1 VERIFIED_COMPLETE; T3.2.1 IMPLEMENTATION RELEASED, FULL RELEASE GATE OPEN`，未提 M2。只扫头行可能漏读 `:22-28` 的新登记（内容本身未错，T3.2.1 仍是当前基线） | `git show 5a16d8a:doc/REBASELINE_PLAN.md` 第 3 行 | 后续维护时在头行补 `M2 PLANNED/NOT_RELEASED` | open |
| F-004 | NOTE | `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md:45`（React UI ownership 选项） | 候选实现者仅列 Qoder / Zcode / feature-based allocation，未含 Antigravity；相对用户随后给出的裁决 B（Qoder = Frontend/UI Owner，Zcode/Antigravity 可依正式 Task 实现 React Feature）清单不完整。**未提前裁决**，属完整性不足 | `git show 2e8f4bf:doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` 第 45 行 | 由后续 Governance Task 正式登记裁决 B：Qoder 负责 UI/UX、Design System、Visual Contract、React Component Boundary、Visual Acceptance；Codex 保留 Architecture / Shared Contract / Integration | open |
| F-005 | NOTE | `doc/REBASELINE_PLAN.md:28`（未来 Rebaseline Task 范围句） | 该句列出 `D02/D05/D07/D08` 与 `09_COLLABORATION` remote 漂移，但未列本次实际被改的 `AGENTS.md:35` 产品边界段与 `00_INDEX:62` SoT 表；两者都带有旧/新技术栈并存措辞 | `git show 5a16d8a:doc/REBASELINE_PLAN.md` 第 28 行 | 将 `AGENTS.md` 产品边界段与 `00_INDEX` SoT 表加入该未来 Task 的协调清单 | open |
| F-006 | NOTE | `doc/tasks/GOV-001.md:51` / `doc/handoffs/GOV-001-2e8f4bf.md:25`（"六个被改 Markdown 文件"） | 交付 `2e8f4bf` 实际改动 **7** 个 Markdown 文件（含带 AD-001 链接的 `AGENTS.md`），表述为"六个"少计 1 个。**结论仍正确**：本次独立解析 8 个文件全部链接，152 条 0 断链 | `git diff --name-only 1e8cb11..2e8f4bf` 计数 = 7 | 后续如有修订，改为"全部被改 Markdown 文件"或列全 7 个 | open |

**未发现**：伪造实现状态、提前释放 Migration Implementation、破坏 T3.2.1、重写历史 Evidence、
混淆 CURRENT_REALITY 与 TARGET_INTENT 的任何情形。

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 范围与受保护路径 | `git diff --name-status 1e8cb11..5a16d8a`；再按 `doc/tasks doc/handoffs doc/reviews verification src tests packaging requirements*` 过滤 | Reviewer worktree，`5a16d8a` | PASS（8 路径全在 allowed paths；受保护目录仅 2 条 `A`；无 `D`/`R`） | 本报告「固定点与范围核验」 |
| 固定点拓扑 | `git merge-base --is-ancestor 1e8cb11 5a16d8a`（exit 0）；`git rev-list --count 1e8cb11..5a16d8a` = 2 | 同上 | PASS | 命令输出 |
| 空白/格式 | `git diff --check 1e8cb11..5a16d8a` | 同上 | PASS，exit 0 | 命令输出 |
| 交付路径 vs 自述 | `git diff --name-only 1e8cb11..2e8f4bf` 计数 = 7；handoff `:14` 列出 7 条 | 同上 | PASS（仅 F-006 计数措辞问题） | 命令输出 |
| 禁止初始化 Artifact | `git ls-tree -r --name-only 5a16d8a` 匹配 `^(frontend/\|src-tauri/\|package\.json\|Cargo\.toml\|.*tauri\.conf\.json)` | 同上 | PASS（命中 0） | 命令输出 |
| 文档链接完整性 | 正则抽取 8 个被审文件的 Markdown 本地相对链接，按被审分支树归一化解析（`..` 栈式）后逐一比对 | 同上，比对集合 = `git ls-tree -r 5a16d8a` | PASS（**152 条解析成功，0 断链**；含 `12_ROADMAP:10` 锚点标题匹配） | 命令输出 |
| Handoff 事实性抽查 | `git status --porcelain` 计数；`git rev-parse origin/main`；`git remote -v`；`Test-Path` worktree 路径；比对 `09_COLLABORATION.md:24` | 主仓库 `1e8cb11` | PASS（1 tracked dirty + 35 untracked；`origin/main`=`1e8cb11`；worktree 路径存在；"无 remote"漂移属实） | 命令输出 |
| ADR 事实抽验 | `Select-String -Path src/**/*.py -Pattern 'PySide6' -List` 计数；六个审计目录 `Test-Path` | 同上 | PASS（22 个文件；6/6 目录存在） | 命令输出 |
| 作者分支未被触碰 | `git -C <author worktree> status --porcelain`；`rev-parse HEAD`；`branch --show-current` | 作者 worktree | PASS（status 空；HEAD=`5a16d8a`；分支不变） | 命令输出 |
| 产品测试 | — | — | NOT_RUN（不适用：纯文档登记，无代码/测试/Schema/依赖变化，§6 `:177`） | — |
| DSH Web 可见性（§6.1） | 本 Review 由用户在 DSH Web 会话内直接派发并产出 | 本次会话 | N/A（非 CLI headless 派发，无 session ID 口径；本报告本身即 Web 会话产物） | 本报告 |

**证据纪律说明**：上表每条命令均记录执行环境与 commit；无仅以"N passed"代替证据的条目；
无判别力 artefact 被记为 PASS；未跑项明确记 `NOT_RUN` / `N/A`。

## 结论与复审

**decision: approved**（Architecture 面 PASS，Verification 面 PASS，无 P0/P1，关键验证无缺失）。

> GOV-001 Architecture Decision Registration Gate 可由 Codex 集成；该批准不代表 M2 Implementation 已获授权，也不代表 T3.2.1 已关闭。

集成前置条件与剩余风险：

1. 本批准只绑定 reviewed_head = `2e8f4bf951ad8a16af50300463f990d325b768e6`（文档 tip `5a16d8a` 仅追加 Handoff 与 Task 状态回填）。该 head 之后再有任何内容改动，本批准失效，须就新增切片重新 Review（§6 `:172`）。
2. 本报告与 `review_report_commit` 构成 `GOV-001:32` 的非作者 Review 证据；Codex 须核对本报告与当前 head 后再串行集成，并将 GOV-001 推进 `approved → done`。
3. F-001～F-006 均为 MINOR/NOTE，**不阻塞集成**；建议整体并入 `REBASELINE_PLAN:28` 已提议的后续 Architecture Documentation Rebaseline Task，以避免触发对已批准 head 的增量复审。
4. **状态保持原样**：T3.2.1 Full Release Gate 保持 `OPEN`、AC3 保持 `BLOCKED`、REPAIR-13 保持 `ready`；M2 保持 `PLANNED / NOT_RELEASED`；Headless & Qt Coupling Audit 仍只是后继建议，未释放、未授权启动。
5. 用户裁决 A 与裁决 B **均未**由 GOV-001 或本 Review 落地实施；二者仍需独立的、范围冻结的 Governance 变更才能登记。
6. 本 Review 未修改作者分支、未修复任何问题、未合并、未改 Task / STATUS / Plan。
