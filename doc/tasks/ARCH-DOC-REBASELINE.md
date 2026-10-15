---
id: ARCH-DOC-REBASELINE
title: 新架构需求、验收及输出格式映射Gate
kind: design
governance_version: 2
status: ready
approval: user_authorized_arch_doc_rebaseline_release_20261015
owner: Antigravity
reviewer: DeepSeek Harness
depends_on: [P08]
base_commit: 4ef92f3daa527adac752b8fc52d492176697a292
branch: codex/arch-doc-rebaseline
worktree: G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE
integration_commit: 4227e8b509e3a42736229b93df4bd9eec548153d
canonical_evidence_status: registered_blob_level
resource_closeout_status: registered
evidence_dir: verification/ARCH-DOC-REBASELINE
---

# ARCH-DOC-REBASELINE

## 来源与目标

来自P08 SCOPE_DRAFT §49/58/71及本轮路线恢复授权。目标是把既有产品要求映射至AD-001新栈，不降低P0/P1、不重写Schema、不新增产品范围。

## Acceptance Criteria

- [ ] AC1：AC-DOC-001逐份核验01–08覆盖，新技术架构/权限与UI映射具备正式来源，不只证明文件存在。
- [ ] AC2：AC-DOC-002领域/Pipeline/版本/受控来源/持久化与错误语义跨文档一致，有逐项对照证据。
- [ ] AC3：AC-DOC-003四一级页面/默认书架/基础Reader/延期项与01/04/05/08一致；四页设计独立释放，不以文档替代设计审查。
- [ ] AC4：P18的JA/KO、无字页、质量AC对应新链，明确真实样本/真值/阈值/version/device/model/endpoint证据责任；旧结果不继承。
- [ ] AC5：P20的Tauri/WebView2/Python sidecar/Windows/UI/可选模型对应旧stack-specific条目，逐项保留要求与新证据Gate。
- [ ] AC6：P08-FMT PNG/ZIP/CBZ/PDF/文本转录长期验收追踪；P16/P17在消费对应格式契约前须此项完成。
- [ ] AC7：固定head非作者Review、Codex集成与逐消费者Gate裁决；某项未完成不标整Task done，可按消费者拆独立已审交付但须另冻结。

## 允许修改范围（2026-10-15 冻结）

- `doc/02_TECHNICAL_ARCHITECTURE_.md`、`doc/05_UI_MAPPING.md`、`doc/07_NON_FUNCTIONAL_REQUIREMENTS.md`、`doc/08_ACCEPTANCE_CRITERIA.md`、`doc/13_ACCEPTANCE_TRACEABILITY.md`：仅做 AD-001 新栈映射与一致性对齐，不新增产品范围、不降低任何阈值。
- 本 Task（`doc/tasks/ARCH-DOC-REBASELINE.md`）、`doc/handoffs/ARCH-DOC-REBASELINE-*.md`、`verification/ARCH-DOC-REBASELINE/**`。
- 写入仅限本 Task 的 worktree（`G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE`）；**禁止原位覆盖主仓现有 dirty 文档**。
- `doc/01_FUNCTIONAL_ARCHITECTURE.md`、`doc/03_DATA_MODEL.md`、`doc/04_USER_FLOW.md`、`doc/06_TRANSLATION_PIPELINE.md`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md` 仍**不在** allowlist；确需调整须先由 Codex 单列允许路径并重新冻结。

## 禁止范围

不授权产品代码、Schema、依赖、模型、OS操作或旧QML实现；不降低阈值或作用户产品取舍。不合 main、不 push。

## 测试要求

planned：需求逐项映射/引用有效性/跨文档一致/193 AC及P08-FMT与AC-SMOKE覆盖/指定Task治理检查。当前全部NOT_RUN；不把历史PASS迁移到新栈。

## 依赖、风险与阻塞

P08已完成。Gate 消费者：P09（AC1–3）、P18（AC4）、P20（AC5）、P16/P17（AC6）。

## 交付与运行记录

- 2026-10-15 Owner 路由与认领：Antigravity 认领 Owner，在 worktree `G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE` 执行。
- 2026-10-15 来源 pin 锁定：扫描主仓 10 个未提交架构文档工作区内容，计算 SHA-256、字节数、mtime 并产出 `verification/ARCH-DOC-REBASELINE/source-pins.json`。
- 2026-10-15 AC1~AC6 逐项核验完成：产出 6 份专项证据报告与 1 份总览报告至 `verification/ARCH-DOC-REBASELINE/`。
- 2026-10-15 架构文档对齐：基于 worktree HEAD 版本在 allowlist 文档（`doc/02, 05, 07, 08, 13`）顶栏增加重基线与 AD-001 目标架构对齐说明，旧实现归为 LEGACY / HISTORICAL，不降阈值，不原位覆盖主仓。
- 2026-10-15 交付 Handoff：提交固定 commit，编写 Handoff 报告，移交 DeepSeek Harness 审查。

### 2026-10-15 冻结与释放（Coordinator dsh, epoch=5，guarded-write）

- 来源：用户 2026-10-15 在 P04 关闭后选定"冻结并释放 ARCH-DOC-REBASELINE"。
- 冻结执行坐标：base=`4ef92f3daa527adac752b8fc52d492176697a292`（main HEAD）；branch=`codex/arch-doc-rebaseline`；worktree=`G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE`（由 Owner 在认领时创建）。
- 逐文件 allowlist 见"允许修改范围（2026-10-15 冻结）"；主仓现有 dirty 架构文档须**先 pin 来源指纹（`verification/ARCH-DOC-REBASELINE/source-pins.json`）再在新 worktree 适配**，禁止原位覆盖。
- 角色：Owner=Codex、Reviewer=DeepSeek Harness（非 Owner、非 contributors/repair participants）、Integrator=Codex；权威参与状态见 `.orchestrator/tasks/ARCH-DOC-REBASELINE-role.json`。
- Gate 消费者：P09（AC1–3）、P18（AC4）、P20（AC5）、P16/P17（AC6）。AC7 要求固定 head 非作者 Review 与逐消费者裁决；可按消费者拆为独立已审交付，但须另行冻结。
- 仍未授权：产品代码、Schema、依赖、模型、OS 操作、旧 QML 实现；不改阈值、不作用户产品取舍；不 push。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EVID-DOC-PIN | AC1/SourcePin | verification/ARCH-DOC-REBASELINE/source-pins.json | 702081442d44f74310f7ae9ae7cc412479f0766a | 1200e967a03f7caad259244cc11e724b35f97e859120a4ef56dbfea54a01f977 | SOURCE_PIN |
| EVID-DOC-AC1 | AC1 | verification/ARCH-DOC-REBASELINE/ac1-coverage-and-sources.md | 702081442d44f74310f7ae9ae7cc412479f0766a | 577695c0ea10684def679a0bd76dc7553d89fe78837095e13208536a2eb5fb7b | CANONICAL |
| EVID-DOC-AC2 | AC2 | verification/ARCH-DOC-REBASELINE/ac2-cross-document-consistency.md | 702081442d44f74310f7ae9ae7cc412479f0766a | a28c60c5b1d2b8f6e8285c229c96269748fde08fa1905b61ebb6f6b6fe5d8778 | CANONICAL |
| EVID-DOC-AC3 | AC3 | verification/ARCH-DOC-REBASELINE/ac3-four-pages-and-deferred.md | 702081442d44f74310f7ae9ae7cc412479f0766a | 94bcd0722e820f1778cce2b943725fda8908df5e2f37242c01aa79caf8d9dc12 | CANONICAL |
| EVID-DOC-AC4 | AC4 | verification/ARCH-DOC-REBASELINE/ac4-p18-quality-and-responsibility.md | 702081442d44f74310f7ae9ae7cc412479f0766a | d8bb1a38af31c3ed76e5f081680b07515ad184aa307e3d87afc75776d71cc87d | CANONICAL |
| EVID-DOC-AC5 | AC5 | verification/ARCH-DOC-REBASELINE/ac5-p20-nfr-stack-rebaseline.md | 702081442d44f74310f7ae9ae7cc412479f0766a | bb29dc6fa2a154e8209987e7d4a6b2a259d081a0bb91147d36e62e64f4264044 | CANONICAL |
| EVID-DOC-AC6 | AC6 | verification/ARCH-DOC-REBASELINE/ac6-p08-fmt-traceability.md | 702081442d44f74310f7ae9ae7cc412479f0766a | b0276a9c78f217a2398e4367a83783345058bf2a70b89e23fad23af8d0d20ede | CANONICAL |
| EVID-DOC-SUM | AC1-6/Summary | verification/ARCH-DOC-REBASELINE/rebaseline-summary.md | 702081442d44f74310f7ae9ae7cc412479f0766a | 7703a92bea5cc55f516055ae29b66e8c1196533940e9dba6ea53cdd62614d4f5 | CANONICAL |
| EVID-DOC-REVIEW | AC7 | verification/ARCH-DOC-REBASELINE/dsh-review-r1.md | 79ed01fd | （Review 文件，未自算入库 pin；复核见 Recovery 证据） | REVIEW |
| EVID-DOC-RECOVERY | Recovery/R1–R6 | verification/ARCH-DOC-REBASELINE/recovery-r1-r6-20261015.md | 8db66b2489796f0e48ebcc01e327d9c3248c4187 | 8d04158e10b16989173a402c573c794a095c76af8fd56ebfa5bea32b78eaab5f | RECOVERY |

### Pin 语义（2026-10-15 R1–R6 恢复核验，blob 层零信任复核）

- 上表 `sha256` 为**冻结 git blob（LF 规范内容）**的 SHA-256；主仓 `core.autocrlf=true`，工作区
  checkout 为 CRLF，故对主仓磁盘文件直接 `Get-FileHash` 会得到不同值 —— 这是行尾转换，**不是内容漂移**。
- 复核方式（可重放）：`git cat-file blob HEAD:<path> | sha256`。2026-10-15 实测：上表 8 项证据
  **8/8 与磁盘 blob 完全一致**，`0 mismatch`。
- `source-pins.json` 内的 `sha256` 为**主仓未提交工作区（含 CRLF）**内容指纹，与本表 pin 语义不同，
  两者不可互相替代；10 个 pin 文件在恢复轮复算后 **10/10 与 pin 记录一致**（未被任何 Agent 覆盖）。
- 冻结 commit 取交付提交 `70208144`（该 8 个文件在 `HEAD` 中 blob 未变，见 Recovery 证据的
  `git diff --stat 70208144 HEAD`）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/ARCH-DOC-REBASELINE | worktree@70208144（分支 codex/arch-doc-rebaseline，HEAD 可达 70208144；内容 pin 见上表） | 任务交付分支 worktree，保留供 Review 与下游集成；**不删除、不 prune**。2026-10-15 R1–R6 核验：主仓工作区 10 个 pin 文件内容未被该 worktree 覆盖，worktree 未被清理 |

## Closeout Record
- 2026-10-15 Owner 路由：`route-agent.py --role owner --task-profile heavy --owner-policy AUTO_SELECT` 选中 **antigravity**（较 codex 同分时由 router tie-break 决定）；权威参与状态以 `.orchestrator/tasks/ARCH-DOC-REBASELINE-role.json` 为准（owner=antigravity，codex 保留为 contributor）。Reviewer 仍为 DeepSeek Harness（非 Owner、非参与者）。
- 2026-10-15 集成与审查：Owner 交付 `70208144` 经 R1 独立 Review（`approved_with_conditions；source-pins 10/10 复核一致）后合并入 main；AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN，按 AC7 由各消费者 Gate（P09/P18/P20/P16/P17）裁决后本 Task 方可 done。

- 2026-10-15 集成落库：合并 `codex/arch-doc-rebaseline` 入 main（merge=`4227e8b509e3a42736229b93df4bd9eec548153d`）。集成前按用户裁定先把主仓 5 个未提交文档固定为基线（`836a12c6`），再合并分支；5 个文档三方自动合并成功，`doc/tasks/ARCH-DOC-REBASELINE.md` 冲突按“双方记录并存”解决。本 Task 维持 `ready`（AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN），按 AC7 待 P09/P18/P20/P16/P17 消费者裁决后方可 done。

### 2026-10-15 AC7/C3 closeout 登记（Coordinator dsh, epoch=5）

- 来源：R1–R6 恢复轮（证据 `verification/ARCH-DOC-REBASELINE/recovery-r1-r6-20261015.md`），
  Coordinator 主控 dsh，lease `264c2000541748298000f93fb25a52de`（`assert` = `LEASE_VALID`）。
- **Canonical Evidence pin 已登记**：8 个证据的 `commit` 列由 `pending` 冻结为交付提交 `70208144`；
  `sha256` 经 blob 层零信任复核 **8/8 一致**。新增 `EVID-DOC-REVIEW`（`79ed01fd`）与
  `EVID-DOC-RECOVERY`（本轮恢复证据）两条登记；pin 语义与 `source-pins.json` 的差异见上节。
- **Resource Manifest 已登记**：交付 worktree `PRESERVE_REFERENCED`，`sha256/manifest` 由 `pending`
  更新为 `worktree@70208144`；未执行任何删除/prune。
- **集成语义取舍（F-2，Merge Conflict 规则）**：merge `4227e8b5` 对
  `doc/02_TECHNICAL_ARCHITECTURE_.md` 采用第一父（用户基线 `7af44a3c`）的标题
  「02 Legacy Production Technical Architecture（历史生产基线）」，分支 `70208144` 的标题
  「02 目标技术架构（Target Technical Architecture）」未进入 main；其余 4 个 allowlist 文档
  （`05/07/08/13`）分支与 `HEAD` **blob 完全一致**，无内容丢失。取舍依据：该文档正文首行分类即
  `LEGACY / HISTORICAL — 非当前目标架构`，分支标题「目标技术架构」与之自相矛盾；用户基线标题与
  正文分类一致，故**保留 HEAD 内容，不回改、不机械合并**。双方有效修改均已核验在库
  （用户基线 = `836a12c6`，分支交付 = `70208144` 且 4/5 文件同内容）。
- **AC7 剩余项**：逐消费者 Gate 裁决（P09/P18/P20/P16/P17）。消费者在 Plan 中均为 `proposed`，
  尚未冻结；释放任一消费者时须引用本 Task 证据作 Gate 输入（R1 review F3/C2）。
- 本 Task 维持 `ready`：AC1–AC3=PARTIAL、AC4–AC6=NOT_RUN；**不因 closeout 登记而标 done**。
- 本轮提交：`8db66b2489796f0e48ebcc01e327d9c3248c4187`（R1–R6 恢复证据 + AC7/C3 closeout pin + `STATUS`/`REBASELINE_PLAN` 指针刷新 + `.orchestrator` 运行日志设施）。
- **F-4（环境问题，非本 Task scope）**：`refs/codex/turn-diffs/checkpoints/2a21a8a6…/ba2cc422-…` 是 Codex CLI 遗留的 **broken ref**（指向不存在对象），使 `git gc --auto` 报 `fatal: bad object` 并失败；commit 本身不受影响。该 ref 归属 Codex 工具，按 External Change Protection **不擅自删除**，登记为 BACKLOG 交 Codex 处置。
