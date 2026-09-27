---
task_id: M2-C1
reviewer: Qoder (non-author independent Reviewer, Reviewer B)
author: ZCode (Owner)
base_commit: 7478f72fe6f9872cae29f4fa12888b5e1f2380f1
delivery_commit: 7de1cd27e22037d4b76b235c9f11399b0cea9463
handoff_commit: b2377288680569dbee4e2299fd7dfae4de067c54
reviewed_head: b2377288680569dbee4e2299fd7dfae4de067c54
review_branch: review/qoder/M2-C1-zcode-7de1cd2
review_worktree: G:/CODEX/New Manga.worktrees/M2-C1-qoder-review-7de1cd2
session: 31a451ce-4440-47f4-9794-48550a1bc0ba (UNVERIFIED - reported by user, not independently provable by Reviewer)
web_visibility: not-applicable
case: A (OWNER_ADOPTED_WITHOUT_SEMANTIC_CHANGE)
decision: approved
---

# Review：M2-C1 — Typed IPC Contract（Qoder Reviewer B / ZCode Owner Delivery）

Reviewer 非作者（Owner=ZCode，Reviewer B=Qoder）。本轮为 ZCode Owner Delivery=`7de1cd2`、`reviewed_head=b237728` 的正式独立复审，在 Codex 授权的专属 Review worktree 内执行。

**Case A 等价性复验**：Owner disposition 为 `OWNER_ADOPTED_WITHOUT_SEMANTIC_CHANGE`（Case A），adopted source head 为 `ac38dede84ff22290c9b9d579c1372c8184a7bd5`（Qoder R3 的 `reviewed_head`）。本 Review 独立验证 Contract blob 为 `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`，与 Owner 声明完全一致，确认 Case A 等价性成立。因此本轮采用 **equivalence re-validation** 路径：独立复验 R3 证据对当前语义 Contract 的覆盖，并对 R-001…R-008 给出本轮独立处置。

**授权来源**：本 worktree 固定在 `reviewed_head=b237728`，branch=`review/qoder/M2-C1-zcode-7de1cd2`。授权范围依据 Owner Handoff `doc/handoffs/M2-C1-zcode-7de1cd2.md` 与 Task 指令：`doc/reviews/M2-C1-zcode-7de1cd2-qoder.md` 与 `verification/M2-C1/review-qoder-zcode-7de1cd2/**` 授权给 Qoder Reviewer B。

## 范围与依据

- **被审对象**：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（276 行，blob `4b503a17…`）、`doc/handoffs/M2-C1-zcode-7de1cd2.md`、`verification/M2-C1/zcode-owner/**`（6 件 Owner 验证文件）。
- **对照来源**：固定 base `7478f72` 的 `src/application/editing/{ports,service,region_canvas}.py`、`src/application/tasks/{projection,service}.py`、`src/domain/tasks/models.py`、`doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`、`doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md`。
- **R3 证据复验**：`1950a23:doc/reviews/M2-C1-4d66523-r3.md` 与 R3 evidence 03-delivery-scope.log、04-link-integrity.log、05-r008-source-ownership.log、06-r001-r006-regression.log（从共享 Git 对象库只读解析）。
- **未覆盖**：产品 pytest / GUI / IPC runtime / 序列化 / 大媒体通道（全部 NOT_RUN，文档-only Task 范围要求）。

## 独立验证结果

### 1. Case A 等价性确认

| 验证项 | 命令 | 观察值 | 结果 |
|---|---|---|---|
| Contract blob SHA-1 | `git rev-parse HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` | **PASS**：与 Owner 声明、R3 被审 blob 完全一致 |
| Contract 行数 | `wc -l doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | 276 | **PASS**：与 R3 被审 Contract 行数一致 |
| Diff scope | `git diff --name-status 7478f72..HEAD` | 8 个 A（Contract ×1 + Handoff ×1 + zcode-owner ×6） | **PASS**：全部落在允许路径 |
| Whitespace | `git diff --check 7478f72 HEAD` | 无输出，exit 0 | **PASS** |
| Dependency ancestry | 5 × `git merge-base --is-ancestor <dep> 7478f72` | D1/I1/I2/R1/UI1 全 exit 0 | **PASS**：复现 Owner `00-environment.md` |

**结论**：Contract blob `4b503a17…` 是 byte-identical 的精确证据，Case A 等价性独立确认成立。R3 对语义 Contract 的审查结论可直接作为本轮 Review 的输入，但 R-001…R-008 的处置由本 Review 独立给出。

### 2. Diff scope 与允许路径

`base..reviewed_head` 全部 8 个新增路径：

| 路径 | 允许？ |
|---|---|
| `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | YES — 唯一 Owner Contract |
| `doc/handoffs/M2-C1-zcode-7de1cd2.md` | YES — Owner Handoff |
| `verification/M2-C1/zcode-owner/00-environment.md` | YES — `zcode-owner/**` |
| `verification/M2-C1/zcode-owner/01-source-trace-owner-base.md` | YES |
| `verification/M2-C1/zcode-owner/02-decision-log.md` | YES |
| `verification/M2-C1/zcode-owner/03-blob-equivalence.md` | YES |
| `verification/M2-C1/zcode-owner/04-git-scope-check.md` | YES |
| `verification/M2-C1/zcode-owner/05-drift-and-links.md` | YES |

禁止路径探针（`src/**`、`tests/**`、`packaging/**`、`src-tauri/**`、`*.qml`、`*.jsx/*.tsx`、Schema/migration、依赖/锁文件、bootstrap、Domain Contract、Task/Plan/Status/Index、历史 Review/evidence）：**全部为空，未违反禁止范围**。

### 3. R-001…R-008 独立处置

本 Review 独立重读 R3 报告与 R3 evidence 03/04/05/06，并在 fixed base `7478f72` 上独立验证每个 Contract 点的源码证据。

| ID | 级别 | Contract 位置 | R3 处置 | 本 Review 独立验证 | 本轮处置 |
|---|---|---|---|---|---|
| R-001 | P2 | §6.1 ↔ `projection.py:95-119` | closed | `TaskProjection` 字段计数 = 23；映射表 7 行覆盖 6+1+1+7+1+6+1=23；`:143` 首句含 `PROPOSAL — wire DTO`；`PageProjectionRow:82-92` 七个行字段与 `:166` 逐项一致 | **closed** |
| R-002 | P3 | `source-trace.md:26` → `AD-001:33` | closed | `AD-001:33` 原文即 `4. **Large binary boundary.** …must not traverse ordinary JSON IPC or Base64 IPC.`；引用行在 Owner base 未变 | **closed** |
| R-003 | P3 | §2 `:34` | closed | `AD-001:15`=`## TARGET_INTENT and decision`（表 `:19-24`）、`:28`=`## Migration constraints`、第 6 项 `**SQLite authority.**` 在 `:35`；契约引「17–25」含前言与表、「第 6 项（第 35 行）」精确 | **closed** |
| R-004 | P3 | §7.1 `:197-203` ↔ `service.py:829-884` | closed | `control_run` 逐条比对：pause 门控 PENDING/RUNNING 且先置 `pause_requested=True`（`:832-837`）；stop 拒绝终态（`:841`）、PENDING/PAUSED 立即取消（`:844-846`）；continue 覆盖 paused→pending 与 interrupted 重规划（`:850-861`）；restart/abandon 仅 interrupted（`:863-882`）；`retry_failed_targets:903` 无失败页抛 `TARGET_NOT_FOUND:913`；`recover_running_runs:886` 存在。`PipelineRunStatus` 九值（`models.py:91-99`）与契约 `:193` 枚举**逐字一致** | **closed** |
| R-005 | P3 | §5 `:114` | closed | `git grep 'CredentialRef' 7478f72 -- src/` → exit 1（零命中）；契约标 `UNKNOWN / DEFERRED`，措辞与实际相符 | **closed** |
| R-006 | P3 | §9 `:75`、`:243` ↔ `region_canvas.py:40-41,67-99` | closed | `_to_pixels = min(size, max(0, math.floor(axis*size + 0.5)))`：像素空间 half-up 后 clamp 到 `[0,size]`；`normalized_to_page_geometry` 仅校验 `page_w/h>0` 与点数≥2，无 `[0,1]` 预 clamp | **closed** |
| R-007 | P3 | `doc/tasks/README.md:7` | closed | `git grep 'M2-S1\.md' 7478f72 -- doc/tasks/README.md` → exit 1；`git ls-tree -r | grep -i M2-S1` → exit 1（全树无该文件）；正文含 `M2-S1 remains unreleased.` | **closed** |
| R-008 | P3 | §5 `:112` | closed | `ports.py:30` `RegionRepository.list_revisions` 定义计数 = 1；`service.py` 内 `def list_revisions` = exit 1（零定义）；service 提供 `restore_revision:550`、`set_revision_pinned:574`（计数 = 2）；`:131` 经 `self._repo.list_revisions(...)` 委托 | **closed** |

**回归判定**：R3 报告引用的 Contract 行在 adopted head `ac38ded` 与 Owner base `7478f72` 之间**逐字节 IDENTICAL**（Owner `01-source-trace-owner-base.md` section A 已证明 9 个被引用文件 blob 完全一致），且总行数 276 未变，故 R3 的全部 `:行号` 引用在本 head 仍然有效。R-001…R-008 无回归。

### 4. Contract §1 相对链接限制评估

Contract §1 第 16 行的相对链接 `../../verification/M2-C1/source-trace.md` 在 Owner branch 树内无目标（Owner 允许路径不含 `zcode-owner/` 之外的 verification 文件）。

**评估**：
- 该链接指向的 draft evidence 文件可从固定历史对象 `ac38dede…` 只读解析（`git show ac38dede:verification/M2-C1/source-trace.md`）。
- Owner 提供了等效的 Owner-base-anchored trace：`verification/M2-C1/zcode-owner/01-source-trace-owner-base.md`，覆盖了 Contract 所有 AS-IS 证据引用在 `7478f72` 的 blob 一致性与抽查。
- 该链接是 Case A byte-identical 保留的产物，不是语义缺陷；不改变任何 normative clause。
- **可用性判断**：对于后续实现者，Contract 内的相对链接在 Owner tree 内是断链，但 (1) Contract 正文已完整包含所有 AS-IS 证据声明，不依赖外部文件才能理解契约条款；(2) 历史 trace 可通过固定对象解析；(3) Owner 等效 trace 已提供。**不构成阻塞**。

**结论**：该链接限制是已解释的非语义治理面限制，**不阻塞可用性，不 merit finding**。若 Codex 集成时希望消除该树内断链，属集成面的治理导航决定，需相应 Case 语义评估，不属本 Review 授权。

### 5. 架构立场独立确认

本 Review 独立对照 Contract 的架构立场与 `AD-001` 及 fixed base 源码：

- **单一写入权威**：§2/§10 复述 AD-001:19-24 边界表及 :35 第 6 项；§2:37 的 Qt-free seam import 约束可检（`projection.py`/`region_canvas.py` 无 PySide6/`src.ui` import，已承认的例外 `application/export/pdf_qt.py` 与文本一致）。
- **现状与目标分离**：§1 否认既有 IPC runtime；§3/§4/§6/§8 全标 PROPOSAL；§7.2 握手标 UNVERIFIED；§11 保留六项未决。
- **数据安全不变式**：§10 保源文件、Managed Copy、人工编辑、Lock、current/pinned Revision 与 recovery；大图片/Webtoon/模型权重禁止进 JSON/Base64 IPC。
- **状态域未被混用**：§7.1 把 Run `blocked` 与 Page 状态分域（实测 `PipelineRunStatus` 九值与投影值域确为两套）；§11 把 glyph/文案/行为与 React UI Owner 留作用户裁决。
- **发布边界明确**：§12 只冻结设计，不授权 runtime、M2-S1、Schema、集成。

**Architecture 面：可以交给 Codex 集成。** 无 P0/P1/P2，无未声明的实现假设。

### 6. React consumer 可用性评估

从 React UI 消费者视角评估 Contract 的可用性：

- **Library / Workspace / Reader / Settings 需求**：§5 的 command catalog 覆盖四个一级页面的核心操作（ListBooks/CreateBook/DeleteBook、ListChapters/ImportPages、StartRun/GetTaskProjection/ControlRun、CreateRegion/DeleteRegion/SaveManualTranslation、GetReaderProjection/SaveReadingProgress、GetSettings/SaveSettings、StartExport/CancelExport）。每个 command 有 typed payload → result 定义。
- **Loading / error / progress / cancel 状态**：§4 定义 request/response 语义；§6.2 定义 RunStatusChanged/RunProgressChanged/RunFinished/RunCrashed 事件；§7 定义 lifecycle 与断线恢复（snapshot resync 为安全 proposal）；§8 定义 typed error envelope（保留源 code，category 为粗分类）。
- **Domain logic 是否推到前端**：§2 明确 Python Core 是业务校验与持久化权威；§5.2 明确 UI-local actions 只改变前端状态，不成为 Core command；§5 前言声明"UI enablement 只用于体验，不代替校验"。**Domain logic 未被推到前端**。
- **Command / query / event / resource mapping**：§5 定义 typed command catalog；§4 定义 request/response 互斥不变量；§6 定义 typed projections 与 events；§6.1 定义 TaskProjection wire DTO 与 AS-IS 字段映射。**映射清晰**。
- **M2-UI1 parity contract 一致性**：Contract §5 的 command catalog 与 `doc/design/M2-UI1_REACT_FEATURE_PARITY_VISUAL_CONTRACT.md` 的功能覆盖一致（Owner `01-source-trace-owner-base.md` section B 已验证 UI1 设计文档引用可解析）。
- **Unknown / Unverified / Deferred / user-decision 边界**：§11 明确列出六项 DEFERRED / UNKNOWN / USER_DECISION_REQUIRED（page-level blocked UI、React UI Owner、large-media transport、runtime serialization、event ordering/replay、lock/conflict policy）。**边界清晰**。

**结论**：Contract 对 React consumer 的可用性充分，所有需求面有对应 typed 定义，所有未决项有明确标注。

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| Review 环境与 worktree 绑定 | `rev-parse --show-toplevel`、`branch --show-current`、`rev-parse HEAD`、`status` | Git Bash；git 2.52.0.windows.1；在授权 Review worktree 内 | **PASS**：root / branch / HEAD=`b237728` / status clean | `00-review-environment.log` |
| Case A blob 等价 | `git rev-parse HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`；`wc -l` | 同上 | **PASS**：blob=`4b503a17…`，276 行 | `01-blob-equivalence.log` |
| Diff scope 与允许路径 | `git diff --name-status 7478f72..HEAD`；禁止路径探针 | 同上 | **PASS**：8 个 A 全在允许路径；禁止路径探针为空 | `02-diff-scope.log` |
| Whitespace | `git diff --check 7478f72 HEAD` | 同上 | **PASS**：无输出，exit 0 | `02` |
| Dependency ancestry | 5 × `git merge-base --is-ancestor <dep> 7478f72` | 同上 | **PASS**：D1/I1/I2/R1/UI1 全 exit 0 | `03-ancestry.log` |
| R-001…R-008 独立重跑 | 各 Contract 点的源码证据在 `7478f72` 的独立验证 | 固定 base `7478f72` | **PASS**：全部复现 R3 结论 | `04-r001-r008-verification.log` |
| §1 相对链接限制 | `git show HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md | grep source-trace`；Owner `01-source-trace-owner-base.md` 覆盖检查 | 同上 | **PASS**：链接在 Owner tree 内无目标，但历史对象可解析，Owner 等效 trace 已提供 | `05-link-limitation.log` |
| 产品 pytest / GUI / IPC runtime | 未运行 | 文档-only Task | **NOT_RUN** | `06-notrun-register.log` |

**执行环境偏差（如实记录）**：prescribed 命令块以 Windows PowerShell 书写，本会话在 **Git Bash** 下执行同一组命令；命令、参数与 exit code 语义一致，故 scope / diff-check / ancestry / blob 四项结论不受影响。本会话未遇到任何 ACL 或权限错误。

**覆盖范围**：Case A 等价性独立确认 + diff scope 与允许路径 + dependency ancestry + R-001…R-008 逐条独立重跑 + §1 相对链接限制评估 + 架构立场独立确认 + React consumer 可用性评估。

**未覆盖 / 超出本 Review 触达**：未运行任何 runtime 语义（见 NOT_RUN 登记）；Owner verification 00-05 的结论经本 Review 阅读确认并复验关键命令，但未从第一性原理重推其全部论证；四个依赖 Task（D1/I1/I2/R1/UI1）仅经 ancestry 确认，未重审其内部结论；AD-001 的产品意图按用户已批准记录采信；页级 `blocked` 的 UI 语义与 React UI Owner 属 `USER_DECISION_REQUIRED`，本 Review 明确不决定。

## 结论与复审

**decision = `APPROVED`**（针对 `reviewed_head=b2377288680569dbee4e2299fd7dfae4de067c54`）。

理由：
1. Case A 等价性独立确认：Contract blob `4b503a17…` 与 R3 被审 blob byte-identical。
2. R-001…R-008 全部由本 Review 在 fixed base `7478f72` 上独立重跑并关闭，无回归。
3. Diff scope 全部落在允许路径，禁止路径零命中，whitespace/ancestry 四道硬门全 exit 0。
4. §1 相对链接限制是已解释的非语义治理面限制，不阻塞可用性，不 merit finding。
5. 架构立场经独立对照成立，React consumer 可用性充分，所有未决项有明确标注。
6. 未发现新的设计性错误、边界越权或未声明的运行时假设。

批准的有效边界：

- 本 Review **不**进入 Integration Gate、**不**集成、**不**启动 M2-S1，也不授权任何 React/Tauri/Python IPC 实现。完成 Review 即停止，交回 Codex。
- 「APPROVED」只覆盖**文档契约本身**，不覆盖产品行为：本 Review 未运行任何产品测试（全部 NOT_RUN），runtime 语义（版本握手、事件投递/重放/幂等、错误映射落地、大媒体通道容量与安全）仍为契约自述的 PROPOSAL/UNKNOWN。任何后续实现 Task 必须自行验证这些语义，不得把本批准复制为实现 PASS。
- 页级 `blocked` 的 UI 语义与 React UI Owner 仍待用户裁决，本 Review 未代答。

**剩余风险**：集成时若把 §5 的 As-Is 单元再压缩（例如把 port 与 service 合并叙述），会重新引入 R-008 类错位；若后续 Task 直接按 §6.1 wire DTO 生成 schema 而未回填 §11 的未决项，会把 PROPOSAL 固化成既成契约。两者都属实现期风险，不阻塞本文档批准。

**非阻塞项**：§1 相对链接限制（已评估，不阻塞）；Owner Handoff 记录的三条 R3 非阻塞说明（被删 ACL 链接、`source-trace.md:28` 引用格式、`531647e` Task 措辞残留）保持原状，均不影响契约条款，不要求返修或再复审。
