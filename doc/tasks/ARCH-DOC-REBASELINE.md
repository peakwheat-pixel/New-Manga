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

**结构依 `codex-adjudicate-archdoc-closeout-r37.md` 的裁定：7 条 Gate + 1 条消费处置汇总。**
**本 Task 只对「映射是否确立」与「交接是否处置」负责，不替消费者判定其自身技术结果。**

- [x] AC1-GATE：逐份核验 01–08 的覆盖；为新技术架构、权限边界和 UI 映射指定正式来源；
  明确 Legacy/Historical 内容、范围边界及其与目标架构的对应关系，并提供可复核引用。
  **该项验收规范与映射是否确立，不验收具体 React 组件渲染或 Tauri IPC 编译。**
- [x] AC2-GATE：对领域模型、Pipeline、版本/Revision、受控来源、持久化及错误语义提供
  逐项跨文档一致性对照；记录新栈 IPC/领域服务集成验证的消费者、Gate 和证据要求。
  **该项不要求消费者集成测试已通过。**
- [x] AC3-GATE：正式确立四个一级页面、默认书架、基础 Reader 与延期项，并证明其与 01/04/05/08 一致；
  明确 React 视觉/交互设计须由 ZCode 的独立设计 Gate 审查，**文档映射不能代替设计审查。**
- [x] AC4-GATE：将 P18 的 JA/KO、无字页及质量验收项映射到新链；定义真实样本、真值、阈值及
  `version/device/model/endpoint` 的证据责任，并明确旧结果不继承、消费者实测由 P18 或其经授权的后续 Task 出具。
- [x] AC5-GATE：逐项映射 P20 的 Tauri/WebView2/Python sidecar/Windows/UI/可选模型 NFR，
  **原要求及阈值不得降低**；明确各项测量方法、环境矩阵、证据字段和消费者 Gate。
- [x] AC6-GATE：建立 P08-FMT PNG/ZIP/CBZ/PDF/文本格式的长期追踪表；为导入/导出契约、
  `SEC-FMT-001..005`、外部阅读器互操作验证逐项指定责任 Task/Owner、前置关系、证据
  和未满足时可用的限制处置。**仅在这些责任均有活动 Task 或经授权的 limitation 接收路径后才算达成。**
  → **已由 [SEC-FMT-IMPL-1](SEC-FMT-IMPL-1.md) `closed_with_limitations` 承接**（r37 判定的唯一缺口）。
- [x] AC7-GATE：对固定交付 head 完成非作者 Review 与 Codex 集成核验，并对每个消费者给出
  「映射已就位/未就位、消费者须自证事项、接受/附条件/拒绝」的逐项裁决；**不替消费者判定其自身技术结果。**
- [ ] AC-CONSUMPTION-DISPOSITION：对 AC1–AC6 所列每个消费者逐项登记消费状态、证据引用、
  负责的消费者 Task/Owner，以及未完成项的后续路径或经授权接受的 limitation；
  AC7 登记各消费者是否已作出 Gate 裁决。**状态可以是 `MET`、`PARTIAL`、`BLOCKED` 或
  `NOT_APPLICABLE`；不得因未完成而虚报 `MET`。**

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

### 2026-10-18 AC7 逐消费者 Gate 裁决完成（Coordinator/Reviewer dsh, epoch 7）

- 授权：用户 2026-10-18 裁决"授权 dsh 直接完成 DOC AC7 并激活 P20"。
- 被审固定 head：`integration_commit 4227e8b509e3a42736229b93df4bd9eec548153d`（本轮实测 `git merge-base --is-ancestor … HEAD` exit 0）。
- 裁决证据：[`verification/ARCH-DOC-REBASELINE/ac7-per-consumer-gate-ruling.md`](../../verification/ARCH-DOC-REBASELINE/ac7-per-consumer-gate-ruling.md)。
- 结论：AC7 三项构成全部达成（固定 head 非作者 Review 已于 `dsh-review-r1.md` 完成；Codex 集成为 main 祖先；逐消费者裁决见证据文件）——P09（AC1–3）**接受附条件**、P18（AC4）**接受**、P20（AC5）**接受**（阈值未放宽，P20 须自证 NFR 实测）、P16/P17（AC6）**接受附条件**。
- **本 Task 不标 `done`**：AC1–AC3 仍 PARTIAL（未决项已逐条列出）、AC4–AC6 实测部分属消费者责任，按 AC7 原文"某项未完成不标整 Task done"。保持 `ready`，其映射交付可被消费者引用。

## 2026-10-20 逐项复核与 Codex r33 裁定

Coordinator 在 2026-10-20 对 AC4–AC6 逐项溯源（三轮：`ac5-measured-baseline-20261020.md`、
`ac6-measured-run-20261020.md`、`ac4-blocking-chain-20261020.md`），
Codex r33 据此作出裁定。

### 结论：AC4 / AC5 / AC6 均判 `PARTIAL`

| AC | r33 判定 | 缺口 |
|---|---|---|
| **AC4** | **`PARTIAL`** | 消费者实测只部分存在：**修复后新链路未重跑** |
| **AC5** | **`PARTIAL`** | NFR 实测覆盖绝大多数项且阈值未降，但**只有一台 Win11 + RTX 5070 Ti**；`CUDA_VISIBLE_DEVICES` 屏蔽**不等同**实际无独显硬件档 |
| **AC6** | **`PARTIAL`** | 五格式往返通过；**`SEC-FMT-001..005` 与 CBZ/PDF 外部阅读器验证缺失** |

### r33 对各问题的具体裁定

**1. AC5 不能判 `MET`** —— 单机环境无法替代原 Gate 要求的
「Win11 + Win10 22H2 + Intel i5/8GB 无独显档」三档。

**2. AC6 的结构校验不能替代外部阅读器验证** ——
「结构合法性校验可补充格式内部一致性证据，**不能代替独立阅读器互操作验证**，
也不能替代恶意输入安全测试」。

**3. P16/P17 的前置 Gate 曾被违反，但不自动撤销其 `done`** ——
> AC6 报告 §4 明确要求安全测试及外部阅读器验证在消费前完成，而 P16 的
> `P16-FMT-PIN` 引用了该报告、P16/P17 随后完成。应把这是次序/前置 Gate 偏差
> **登记为遗留**，并由新 Task 完成尚缺的验收。

**4. P18 不自动重开** ——
> `ImportPages` 实现及其测试**只解除一个技术前置**，不代表 P18 的端到端实验已重跑。
> 原 AC 明确不重新获取 Manga109；真实素材、真值与模型端点及另外两项运行缺口仍需确认。

**5. AC4 判 `PARTIAL` 而非 NOT_RUN，且措辞更正了交付方的一处不准确** ——
> 已确认旧阻塞后来解除，但没有修复后重跑的证据。原 P18 运行**确实执行过**但失败在
> 导入/检测前置，故「完全没有任何运行」不准确；「修复后新链路未验证」是未运行部分。
> 若要按限制终止，必须保留未完成状态并由有权者明确接受限制，**不能把 limitation
> 改写成 PASS 或补勾**。

**6. 跨 Task 等待需要登记，但不直接改协作协议** ——
> 建议未来治理 Task 以 Plan 的 DAG 为索引、Task 的依赖/阻塞段为事实详情。

### 当前阻塞（r33 §7 推荐下一步）

> **先由用户裁决 P18 AC2 的 JA/KO 发布门槛。**

`P18` 的 `experiments/P18/qualification-plan.md` L5 记载：

> **产品质量门槛**：未冻结。检测、OCR、翻译、无字页与复杂背景修复的产品发布判定
> 保持 `BLOCKED_WAITING_EXTERNAL_DECISION`。

**5 个维度的发布门槛均需用户裁决，这是产品取舍，不在 Agent 权限内。**

### 本 Task 因此的处置

- **AC4 / AC5 / AC6 记为 `PARTIAL`**（不勾选）。
- AC1 / AC2 / AC3 / AC7 本轮未复核，维持原 `PARTIAL` / 待做。
- **不因上述判 `done` 或 `closed_with_limitations`**——r33 明确：
  「不能把 limitation 改写成 PASS 或补勾」。
- 下一步取决于用户对 P18 AC2 门槛的裁决。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EVID-DOC-PIN | AC1/SourcePin | verification/ARCH-DOC-REBASELINE/source-pins.json | 702081442d44f74310f7ae9ae7cc412479f0766a | 75f7622d3fd946689746bbe71ff4f63a284c800f69d4eca5d32a761bba60c230 | SOURCE_PIN |
| EVID-DOC-AC1 | AC1 | verification/ARCH-DOC-REBASELINE/ac1-coverage-and-sources.md | 702081442d44f74310f7ae9ae7cc412479f0766a | e767e5a8f7558d3657b1840ce8bac21e2f23bf1eb56ed7be39c4a07e4085d88e | CANONICAL |
| EVID-DOC-AC2 | AC2 | verification/ARCH-DOC-REBASELINE/ac2-cross-document-consistency.md | 702081442d44f74310f7ae9ae7cc412479f0766a | 1b69f0836fed9f3c7cdcb0bb21bd95d441898a256cbd171eab069d29994cde21 | CANONICAL |
| EVID-DOC-AC3 | AC3 | verification/ARCH-DOC-REBASELINE/ac3-four-pages-and-deferred.md | 702081442d44f74310f7ae9ae7cc412479f0766a | 4453f4ef27b08a13df518c714effc6b6efee6801e8240ab44b27ecb9a6e57ea6 | CANONICAL |
| EVID-DOC-AC4 | AC4 | verification/ARCH-DOC-REBASELINE/ac4-p18-quality-and-responsibility.md | 702081442d44f74310f7ae9ae7cc412479f0766a | 28b356628d8a086bf44a0f1a6fb0316ad52084d432e233436d827484b6dbf962 | CANONICAL |
| EVID-DOC-AC5 | AC5 | verification/ARCH-DOC-REBASELINE/ac5-p20-nfr-stack-rebaseline.md | 702081442d44f74310f7ae9ae7cc412479f0766a | a103c84746c722cd2041fbf4ec1bbaace4d4b6f57c3e1693abdcae188128343c | CANONICAL |
| EVID-DOC-AC6 | AC6 | verification/ARCH-DOC-REBASELINE/ac6-p08-fmt-traceability.md | 702081442d44f74310f7ae9ae7cc412479f0766a | 48156cc15757d41d6edf419cd83c9228055a4152a98f0b92f25a212822b607a6 | CANONICAL |
| EVID-DOC-SUM | AC1-6/Summary | verification/ARCH-DOC-REBASELINE/rebaseline-summary.md | 702081442d44f74310f7ae9ae7cc412479f0766a | 6f93cd89ad212504682023694200765e08a6c3446f0aaec09472e4ea81c6c620 | CANONICAL |
| EVID-DOC-REVIEW | AC7 | verification/ARCH-DOC-REBASELINE/dsh-review-r1.md | 79ed01fd | （Review 文件，未自算入库 pin；复核见 Recovery 证据） | SOURCE_PIN |
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

### 2026-10-17 AC7 逐消费者裁决补记（Coordinator dsh, epoch 6）

- **触发**：唯一 READY 节点复查（设置面 Core+host 双链已于本日全部完成，`3cee3e29a`）。
- **消费者现状**（以 `doc/tasks/**` 权威状态为准）：**P09 = `closed_with_limitations`**（AC1–AC3）、**P16 = `done`**、**P17 = `done`**（AC6）、**P18 = `closed_with_limitations`**（AC4）、**P20 = 无任务文件**（AC5）。
- **裁决**：AC5 的消费者 **P20 尚不存在**，故**按 AC7"某项未完成不标整 Task done"**，本 Task **保持 `status: ready`**，**不**标 done；AC1–AC3（P09）、AC4（P18）、AC6（P16/P17）对应的消费者**均已关闭**，其证据形态与范围已由 R1 非作者 Review（`verification/ARCH-DOC-REBASELINE/dsh-review-r1.md`：architecture_axis **PASS** / verification_axis **PASS**，`approved_with_conditions`）覆盖，**无需重做**。
- **不做的**：不重跑已 PASS 的核验、不迁移历史 PASS、不新增产品范围、不改阈值；**未**为 AC5 预写结论（P20 未释放，预写即越权）。
- **解除条件**：**P20 释放并关闭**后，本 Task 方可做 AC5 裁决并整体 closeout（或按 AC7 另行冻结 consumer-scoped 交付）。**P20 又依赖 P19 的验收方式（用户裁决硬门）** → 本节点实质由该裁决解锁。

### 2026-10-20 按 r37 裁定实施 7+1 结构（Coordinator dsh, epoch 8）

**依据**：`verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-archdoc-closeout-r37.md`

**r37 的判定**：7 条 Gate 中 **AC1–AC5、AC7 已达成，AC6 部分达成**——
「格式追踪表、前置要求和 `SEC-FMT` 定义存在；但 `SEC-FMT-001..004` 及外部阅读器验证
没有活动承接 Task/Owner」。**这是唯一的 Gate 责任缺口。**

**该缺口已关闭**：r37 判定的下一步是「为 AC6 未承接项明确后续 Task/Owner 或经授权接受的
limitation」。已完成：

- **[SEC-FMT-IMPL-1](./SEC-FMT-IMPL-1.md)** 建立并收口为 `closed_with_limitations`
  （5 MET + AC5 `PARTIAL`），29 个测试覆盖 `SEC-FMT-001..004`。
- **由它发现并驱动修复了一个 P1 缺陷**
  [PDF-STREAM-FIX-1](./PDF-STREAM-FIX-1.md)（`closed_with_limitations`）：
  `QtFreePdfComposer` 的 content stream 声明了 FlateDecode 但未压缩，
  **导致所有导出 PDF 渲染空白**。

**所以 7 条 Gate 现已全部达成**（AC6 的责任缺口由活动 Task 承接并关闭）。

**剩余 1 条 `AC-CONSUMPTION-DISPOSITION` 未完成**：它要求逐消费者登记消费状态。
**这依赖 P09 / P18 / P20 / P16 / P17 / ZCode 设计 Gate / 第二环境 / 真实阅读器各自的执行结果。**

**这不是本 Task 能自己完成的**——**它是「向消费者要结果」的登记，不是「本 Task 交东西」。**

**所以本 Task 现在的形态是**：**7 Gate 全达成 + 1 消费处置汇总待消费者**。

**按 r37 的措辞**：关闭候选为 **`closed_with_limitations`，不是 `done`**——
前提是 AC6 的未承接项已被明确派发或经授权接受 limitation。**该前提现已满足。**

