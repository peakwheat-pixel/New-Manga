---
task_id: M2-C1
reviewer: DeepSeek Harness (Reviewer A, non-author)
author: ZCode (Owner)
base_commit: 7478f72fe6f9872cae29f4fa12888b5e1f2380f1
delivery_commit: 7de1cd27e22037d4b76b235c9f11399b0cea9463
reviewed_head: b2377288680569dbee4e2299fd7dfae4de067c54
contract_blob: 4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3
case: A (OWNER_ADOPTED_WITHOUT_SEMANTIC_CHANGE)
review_branch: review/deepseek/M2-C1-zcode-7de1cd2-r3
session: session-5a2d596e-5db0-4651-b180-e45c1a8abedc
decision: approved
---

# Review：M2-C1 — Typed IPC Contract（DeepSeek Harness Reviewer A / ZCode Owner Delivery r3）

本报告是 M2-C1 ZCode Owner Delivery 的正式独立 Review（Reviewer A = DeepSeek Harness，非作者）。
被审对象固定为 `reviewed_head=b2377288680569dbee4e2299fd7dfae4de067c54`，
Owner Delivery 固定为 `7de1cd27e22037d4b76b235c9f11399b0cea9463`，
固定 base 为 `7478f72fe6f9872cae29f4fa12888b5e1f2380f1`。

**本轮为重新独立裁定。** 本 checkout 中不存在任何旧 r2 报告（`git ls-tree` 与本机文件系统均无），
未读取、未复制、未沿用 r2 的任何 finding、证据或结论。本报告所有事实均在本次 checkout 的
`review/deepseek/M2-C1-zcode-7de1cd2-r3`（独立 clone，`.`git` 即本 worktree 自身）中重新确认。
Qoder Reviewer B 的报告只作为被核查对象（`0d73983…`，**不在被审树内**），不作为批准依据。

## 范围与依据

- **被审路径（base..reviewed_head 全部 8 个 `A`）**：
  `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`（276 行）、`doc/handoffs/M2-C1-zcode-7de1cd2.md`、
  `verification/M2-C1/zcode-owner/00-environment.md` … `05-drift-and-links.md`。
- **对照来源**：固定 base `7478f72…` 的真实源码与文档（`src/application/tasks/{projection,service}.py`、
  `src/application/editing/{ports,service,region_canvas}.py`、`src/domain/tasks/models.py`、
  `src/ui/viewmodels/workbench/*`、`src/application/export/pdf_qt.py`、
  `doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`）；`origin/master` 上的 Codex 治理登记
  `doc/tasks/M2-C1.md` 与 `verification/M2-C1/scheduler-registration-7478f72.md`（仅只读解析，
  证明 Owner 授权来源；它们不在被审树内）。
- **协作协议**：`AGENTS.md`、`doc/09_COLLABORATION.md`（§3 任务释放与共享文件、§4 Task 状态机、
  §5 Handoff、§6 独立 Review 与集成）、`doc/templates/REVIEW.md`（批准门槛）。
- **未审到**：产品运行时语义（版本握手、事件投递/重放/幂等、错误映射落地、大媒体通道）——不存在
  运行时且本 Task 禁止实现；四个依赖 Task 的内部结论仅经 ancestry 确认；`ac38dede…` 草案树的
  链接计数未复跑。完整未跑清单见 [07-notrun-register](07-notrun-register.md)。

## 预检与工作区绑定

| 检查 | 观察值 | 结果 |
|---|---|---|
| `git rev-parse --show-toplevel` | `C:/Users/49745/.codex/worktrees/M2-C1-dsh-review-7de1cd2-r3` | PASS |
| `git branch --show-current` | `review/deepseek/M2-C1-zcode-7de1cd2-r3` | PASS |
| `git rev-parse HEAD` | `b2377288680569dbee4e2299fd7dfae4de067c54`（= reviewed_head） | PASS |
| `--path-format=absolute --git-dir` | `<root>/.git` | PASS |
| `--path-format=absolute --git-common-dir` | `<root>/.git`（独立 clone，非主仓 common dir） | PASS |
| 初始 `git status --short` | 0 行 | PASS |
| `git cat-file -t` ×4 | `7de1cd2`=commit、`b237728`=commit、`4b503a17`=blob、`0d73983`=commit | PASS |

四项预检条件全部符合，未触发 BLOCKED。原始命令与输出见
[00-review-environment](00-review-environment.md)。

## Standards 视角（executed）

- **Task 授权与允许范围**：被审树不含 `doc/tasks/M2-C1.md`（任务文件是 mainline 治理面产物），
  因此 Owner 树无法自证允许路径。本 Review 从 `origin/master` 独立读取该 Task：其允许范围含
  `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` 与 `verification/M2-C1/**`，禁止范围含
  `src/**`、`tests/**`、`packaging/**`、依赖清单、Schema/migration、Domain Contract、
  QML/React/Tauri/runtime、Task/Plan/Status/Index 与既有交付/Review/证据。被审的 8 个路径与
  `case A` 采用路径均落在允许范围内；禁止路径探针为空。见 F-002。
- **禁止越界**：`git diff --name-only 7478f72..b237728 -- src/** tests/** packaging/** src-tauri/** *.qml
  *.jsx *.tsx *.ts *.rs pyproject.toml requirements*.txt uv.lock package.json doc/STATUS.md
  doc/REBASELINE_PLAN.md doc/00_INDEX.md doc/tasks/**` → 空输出、exit 0。
- **证据纪律（§6 item 12）**：Owner 的 scope/whitespace/ancestry 结论由本 Review 逐条复跑
  （见下）；产品 pytest 明确记为 `NOT_RUN` 而非 PASS；Qoder 报告如实标注其 session
  `UNVERIFIED` 与 PowerShell→Git Bash 环境偏差。
- **Fowler baseline 判断项**：未发现重复代码、发散式变更或臆测性抽象类问题。契约内唯一可指摘处
  是 "possible Duplicated Data" 性质的投影字段映射（§6.1 的 23 字段 AS-IS→wire 映射表）——
  但它是有意的逐字段映射证据，不是冗余，不作为 finding。
- **未发现违反本仓库记录标准**的硬性项。

## Spec 视角（executed，可选视角）

来源顺序：`doc/tasks/M2-C1.md` 的 AC C1–C8 → 其引用的 AD-001 与既有 M2 交付 → STATUS/Plan 的
用户裁决。C1–C8 逐条对应情况：

| AC | 要求 | 本轮独立核验 | 结论 |
|---|---|---|---|
| C1 可追溯来源 | 来源表覆盖命令/事件/类型/错误/版本/生命周期，区分 AS-IS/TO-BE/PROPOSAL/UNKNOWN，固定基线与路径行号 | 9 个被引证据文件在三基线（`eec1aa4`/`7478f72`/`7de1cd2`）blob 全等；AD-001 `:15/:19-24/:28/:33/:35` 逐行原文核对；`CommandType` 18 值与 §5.1 枚举集合相等 | 满足 |
| C2 消息边界与版本 | transport-neutral envelope、版本兼容 Proposal、区分命令接受/长任务事件/快照恢复，未把未实现 runtime 写成现状 | §3/§3.2 全标 PROPOSAL 且显式声明 handshake `NOT_IMPLEMENTED`；§4 区分同步接受与长任务；§7.2 握手 `UNVERIFIED` | 满足 |
| C3 类型目录 | 候选命令/事件、payload/result DTO、对象/状态类型，分开 Core 操作与 UI-local state，明确 Core 校验与持久化 | §5 目录 18 行 + §5.1 `PipelineScope` 判别联合 + §5.2 UI-local 动作清单（含"写持久状态必须提升为 Core 命令"）；§2/§10 明确 Core 权威 | 满足 |
| C4 typed error | 保留源 code 的 envelope 与候选分类，未映射留 UNKNOWN | §8 `ErrorEnvelope` 保留 `code`，category 为粗分类；未映射显式 `unknown`/`UNKNOWN`；已观察 code（`INVALID_RUN_TRANSITION`/`RUN_NOT_INTERRUPTED`/`TARGET_NOT_FOUND`/`RegionCanvasError.code`）与源码一致 | 满足 |
| C5 lifecycle/recovery | 区分已有 Run 状态机与未来 session Proposal，记录 pause/stop/continue/restart/abandon/retry/recovery 与断连边界 | §7.1 七条控制语义与 `service.py:829-916` 逐行一致（含 `abandon` 不写 `interruption_disposition`、`restart` 写 `"restarted"`）；§7.2 断线不自动重放、以快照重取为准 | 满足 |
| C6 数据安全 | Core/SQLite 单一写入权威；保源文件/Managed Copy/人工编辑/Lock/current+pinned Revision/recovery；禁止大媒体进 JSON/Base64；通道留 Spike | §1/§2/§10 与 AD-001 `:24/:35` 一致；§10 逐条列出保护项与禁令；选型 `DEFERRED` | 满足 |
| C7 未决 UI 语义 | Page `blocked` 与 Run status 分域；glyph/文案/行为 `DEFERRED / USER_DECISION_REQUIRED`；React UI Owner 未决定 | §7.1 与 §11 分域成立（`PipelineRunStatus` 九值与 Page 值域实测为两套）；§11 六项未决逐项标注 | 满足 |
| C8 范围与交接 | 仅文档/证据/治理路径；产品代码/测试/Schema/依赖/QML/React/Tauri/runtime 未改；Handoff 固定 | diff scope 8 个 `A` 全在允许范围；`git diff --check` exit 0；Handoff frontmatter 绑定 base/delivery/tip | 满足（Task 状态推进本身仍归 Codex） |

- **来源要求但缺失/部分完成**：无。
- **diff 中来源未要求的行为（scope creep）**：无。
- **看似实现但实现有误**：不适用（纯文档；PROPOSAL 均未声称已实现）。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| F-001 | P3 | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:16` | 契约中**唯一**的 Markdown 相对链接 `../../verification/M2-C1/source-trace.md` 在 Owner final tree 中无目标。触发：审计者从 reviewed_head 打开契约并点击该"来源"链接。影响：契约自述的溯源指针不可达，可审计性下降（目标须凭 `ac38dede…` 对象 hash 才能只读恢复）。**不改变任何 normative 条款**，且 Owner 已提供树内等效 trace。 | `git cat-file -e b237728:verification/M2-C1/source-trace.md` → exit 128；`git cat-file -e ac38dede…:同路径` → exit 0；本机 `Test-Path` → False。[04-link-audit.log](04-link-audit.log)、[03-link-adjudication.md](03-link-adjudication.md) | **不要求 Owner 在本轮返修**（见下"链接裁定"）。建议 Codex 作为 Integrator 在集成面处置：把冻结的 `source-trace.md` 落到集成分支，或加治理导航注记；**不得修改 Contract blob**。 | open（non-blocking，转 Codex 集成面） |
| F-002 | P3 | `verification/M2-C1/zcode-owner/00-environment.md:30`；`verification/M2-C1/zcode-owner/03-blob-equivalence.md:47,48,50,51`；被审树缺 `doc/tasks/M2-C1.md` | 交付内 6 处反引号路径引用在 reviewed_head 无目标：1 处（`scheduler-registration-7478f72.md`）只在 `origin/master`；5 处是 `03-blob-equivalence.md` 中"草案头存在、Owner 交付故意不复现"表格自身的行（语义即"不存在"，属正当）。另：Handoff 引用的"本 Task §Review 阶段授权条款"无法从被审树自证，因 Task 文件不在 Owner 分支。影响：从被审头自证的审计路径不完整，读者须改从 mainline 读取 Task 与 Scheduler 记录。 | `git ls-tree -r --name-only b237728 -- doc/tasks`（过滤 M2）→ 无匹配；`git cat-file -e origin/master:doc/tasks/M2-C1.md` → exit 0；`git cat-file -e origin/master:verification/M2-C1/scheduler-registration-7478f72.md` → exit 0。[04-link-audit.log](04-link-audit.log) | 无需返修（作者已在 `03-blob-equivalence.md` 逐条解释缺失原因）。建议 Codex 集成时把 Task/Scheduler 记录一并纳入集成分支，使被审头可自证。 | open（non-blocking，治理导航建议） |
| F-003 | P2 | `verification/M2-C1/zcode-owner/03-blob-equivalence.md:21`（第 4 条复现命令） | 该命令对**工作区原始字节**计算 SHA-256 并声明结果 = `c04b5af5…`；在本 checkout（`core.autocrlf=true`，工作区文件 CRLF）实际得到 `ae68c0e1…`。触发：任何独立复现者按字面执行。影响：复现者会误以为 Owner 文件与草案 blob 存在内容差异（实际完全一致，25122 字节 LF blob 双侧相同），浪费审计轮次；这是**证据可复现性缺陷，不是内容缺陷**。 | `python hashlib.sha256(raw worktree bytes)` → `ae68c0e1…`；`hashlib.sha256(LF-normalized)` → `c04b5af5…`；`git show HEAD:` 与 `git show ac38dede…:` 均 25122 字节且 `identical=True`。[01-blob-command-discrimination.log](01-blob-command-discrimination.log) | 建议 Owner 在 03 文档补注实际输出与 CRLF/LF 口径（或改用 `git rev-parse <rev>:<path>` / `git hash-object` / LF 归一化后的 SHA-256）。**不阻塞**：Case A 结论由 blob OID 与 `git show` 字节比较独立证实为真。 | open（non-blocking，建议下一轮文档修订时一并处理） |

无 P0/P1 finding。未发现设计性错误、边界越权或未声明的运行时假设。

## 链接裁定（特别重新裁定，不继承 r2）

**问题**：Contract `:16` 的 `../../verification/M2-C1/source-trace.md` 在 Owner final tree 中无目标。

**裁定：NON-BLOCKING。不要求 Owner 修复。Decision 因此可以为 APPROVED。**

独立确认的事实：

1. **确实断链**：`git cat-file -e b237728:verification/M2-C1/source-trace.md` → exit 128；
   该文件也不在本 checkout 文件系统中。这是被审树内的客观事实，不是解释。
2. **但目标可只读恢复且被冻结**：`git cat-file -e ac38dede84ff22290c9b9d579c1372c8184a7bd5:verification/M2-C1/source-trace.md`
   → exit 0。任何审计者可用固定对象 hash 恢复，不依赖任何未版本化材料。
3. **实际可审计性影响有限且已量化**：契约 §1 引用该文件只为"来源、行号、commit 和证据分类"提供索引；
   §1 的证据分类定义（AS-IS/TO-BE/PROPOSAL/UNKNOWN）、基线 `eec1aa4…` 与"当前无 IPC runtime"结论
   都在契约正文自身完整成立。**没有任何 normative 条款、AC 或数据安全不变式依赖打开该文件。**
   本 Review 在固定 base 上直接重验了该索引所指向的全部负载事实
   （9 文件 blob 全等、`TaskProjection` 23 字段、`control_run:829`/`recover_running_runs:886`/
   `retry_failed_targets:903`+`TARGET_NOT_FOUND:913`、`PipelineRunStatus` 九值、
   `_to_pixels` half-up+clamp、`list_revisions` 在 port、`CredentialRef` 零命中、AD-001 `:15/:33/:35`），
   全部与 Owner 树内等效 trace 一致。因此该断链造成的是**导航摩擦**，不是证据缺口。
4. **Owner 已提供树内等效且非空壳的替代**：`zcode-owner/01-source-trace-owner-base.md`
   将同一证据集合重新锚定到 Owner base，并逐条给出可复跑命令；本 Review 独立复现其核心结论。
5. **在 Case A + 允许路径下，断链是结构性后果而非 Owner 疏漏**：修链接要么改 Contract
   （破坏 blob `4b503a17…`，即摧毁本 Task 赖以成立的等价性），要么在
   `zcode-owner/**` 之外新增 verification 文件。两者都超出该采用路径的授权语义。
6. **批准门槛不触发**：`doc/templates/REVIEW.md` 与 `09_COLLABORATION.md` §6 item 8 将"不可批准"
   限定为 P0/P1 未解决或关键验证缺失；本项既非 P0/P1，也无关键验证缺失。

**是否要求 Owner 修复：否（本轮）。** 已记录为 F-001（P3），并作为治理导航建议转 Codex 集成面。
本 Review 明确不修改 Contract、不修改 Owner 任何文件。

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 预检与对象类型 | `rev-parse --show-toplevel / branch --show-current / rev-parse HEAD / --path-format=absolute --git-dir / --git-common-dir / status --short`；4 × `cat-file -t` | 本 checkout，HEAD=`b237728` | PASS：root/branch/HEAD/common dir 全部符合；初始 status 0 行；`7de1cd2`/`b237728`/`0d73983`=commit，`4b503a17`=blob | [00-review-environment.md](00-review-environment.md) |
| Delivery/Handoff/head 绑定 | `git diff --name-status 7478f72..7de1cd2`；`7478f72..b237728`；`7de1cd2..b237728`；`merge-base --is-ancestor 7de1cd2 b237728` | 同上 | PASS：delivery 7 个 `A`；reviewed_head 8 个 `A`；head 相对 delivery 仅 +Handoff；ancestry exit 0 | [01-scope-and-binding.md](01-scope-and-binding.md) |
| Case A blob 等价 AC-3A | `git rev-parse HEAD:doc/contracts/…`、index 同路径、`git cat-file blob 4b503a17` 经 `git hash-object --stdin` 重算；`git show HEAD:` 与 `git show ac38dede…:` 字节比较；SHA-256 双侧 | 同上 | PASS：blob/index/re-hash 均 `4b503a17…`；`git show` 双侧 25122 字节 `identical=True`；LF 归一化 SHA-256 双侧 `c04b5af5…`。工作区原始字节 SHA-256 为 `ae68c0e1…`（CRLF 口径，见 F-003） | [01-scope-and-binding.md](01-scope-and-binding.md)、[01-blob-command-discrimination.log](01-blob-command-discrimination.log) |
| Diff scope 与禁止路径 | `git diff --name-status`（三个区间）；禁止路径 `git diff --name-only` 探针 | 同上 | PASS：8 个 `A` 全在允许路径；禁止路径探针空输出 exit 0 | [01-scope-and-binding.md](01-scope-and-binding.md) |
| Whitespace / conflict markers | `git diff --check 7478f72 b237728`；`-- doc/contracts/…` | 同上 | PASS：两次均无输出，exit 0 | [01-scope-and-binding.md](01-scope-and-binding.md) |
| 依赖 ancestry | 5 × `git merge-base --is-ancestor <dep> 7478f72` | 固定 base | PASS：D1/I1/I2/R1/UI1 全 exit 0 | [01-scope-and-binding.md](01-scope-and-binding.md) |
| 来源溯源独立重跑 | 9 文件三基线 blob 对比；`TaskProjection` 字段遍历；`control_run`/`recover_running_runs`/`retry_failed_targets` 行级阅读；`PipelineRunStatus` 枚举；`_to_pixels`；`ports.py:30` 与 service 零定义；`git grep -c CredentialRef src/`；`CommandType` 18 值与 §5.1 集合比较 | 固定 base `7478f72`、Delivery `7de1cd2` | PASS：全部复现 Owner/R3 结论（含 `TARGET_NOT_FOUND` 于 `:913`、`abandon` 不写 `interruption_disposition`、`restart` 写 `"restarted"`） | [02-source-trace-recount.log](02-source-trace-recount.log)、[03-lifecycle-lines.log](03-lifecycle-lines.log)、[02-source-trace-and-lifecycle.md](02-source-trace-and-lifecycle.md) |
| AD-001 引用核对 | `git show 7478f72:doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md`，逐行读 `:15/:19-24/:28/:33/:35` | 固定 base | PASS：契约 §2/§10 引用与原文逐字一致 | [02-source-trace-and-lifecycle.md](02-source-trace-and-lifecycle.md) |
| Qt 信号与 Qt 耦合例外 | `git grep -nE "runStatusChanged\|runFinished\|taskProgressChanged" b237728 -- src/`；`git cat-file -e HEAD:src/application/export/pdf_qt.py` | reviewed_head | PASS：§6.2 三个信号名真实存在；§2 声明的 `pdf_qt` 例外文件存在；IPC 事件标为未实现 | [02-source-trace-and-lifecycle.md](02-source-trace-and-lifecycle.md) |
| 链接与引用可达性 | `probe-link-audit.py`：提取 8 个被审路径全部 Markdown 链接与反引号仓库路径，逐条在 reviewed_head / `ac38dede…` 解析 | 同上 | 49 条引用，9 条在 reviewed_head 不解析（1 条 Markdown 链接 + 8 条文本路径引用），逐条分类见 F-001/F-002 | [04-link-audit.log](04-link-audit.log)、[03-link-adjudication.md](03-link-adjudication.md) |
| Qoder Reviewer B 原件核查 | `git show 0d73983:doc/reviews/M2-C1-zcode-7de1cd2-qoder.md`；`git ls-tree` 其 evidence；`git diff --name-status 0d73983^..0d73983`；`git show --check 0d73983`；逐条对账其 12 项负载结论 | `0d73983`（**不在被审树内**） | PASS（可对账 11 项一致，1 项处置分歧已记录；无伪造证据迹象；decision=`approved`，其 session 自标 `UNVERIFIED`） | [06-qoder-crosscheck.md](06-qoder-crosscheck.md) |
| 产品 pytest / GUI / IPC runtime / 大媒体 | 未运行 | 文档-only Task | **NOT_RUN**（Collected/Passed/Failed/Skipped/Exit = N/A） | [07-notrun-register.md](07-notrun-register.md) |

**环境偏差（如实记录）**：Task 规定的命令块以 PowerShell 书写；本 Review 亦在 PowerShell 7
（`pwsh`）下执行，Git 为 2.52.0.windows.1，Python 3.14.6。与 Owner/Qoder 的 Git Bash 记录相比，
命令参数与 exit code 语义一致。本会话未遇到 ACL 或权限错误。
（备注：`00-environment.md` 与 `03-blob-equivalence.md` 中出现的 `4d665238cc43ae9a54d70a117f2e58ba596cf1f5`
是**草案** Delivery，不是本 Task 的 ZCode Owner Delivery；本 Review 全程以任务固定的
Owner Delivery `7de1cd27e22037d4b76b235c9f11399b0cea9463` 为准，未受该历史对象影响。）

### 关键验证结论（独立于作者与 r2）

- Case A 等价性 **成立**：`git rev-parse HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`
  = `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`，且 `git show` 字节与 `ac38dede…` 完全相同（25122 字节）。
- 交付范围 **零越界**：8 个 `A` 路径全部落在 `doc/tasks/M2-C1.md` 允许范围内；`src/**`、`tests/**`、
  Schema、依赖、bootstrap、QML/React/Tauri/runtime、Task/Plan/Status/Index、历史 Review/evidence 零改动。
- `git diff --check` **exit 0**（全区间与单文件两次）。
- 契约 AS-IS 断言在固定 base 上 **全部可复现**；PROPOSAL/UNKNOWN 标记 **无一处被伪装为现状**。
- 链接问题为 **非阻塞**（见上"链接裁定"）。

## 结论与复审

**Architecture 结论（executed）**：通过，可以交 Codex 进入其自身的集成决策。
依赖方向与权威边界与 AD-001 一致（Core 业务与持久化权威、Rust 无领域逻辑、React 仅呈现与意图）；
单一 SQLite 写入权威、源文件/Managed Copy/人工编辑/Lock/current+pinned Revision/recovery 保护
逐条在场；大媒体禁止入 JSON/Base64 且通道选型 `DEFERRED`；two status domains 未被混用；
`PROPOSAL` 与 `AS-IS` 分离彻底；发布边界（§12 只冻结设计，不授权 runtime/M2-S1/Schema/集成）明确。
未发现未声明的运行时假设或反向依赖。

**Verification 结论（executed）**：通过，且未把任何未运行项写成 PASS。
预检、范围、等价性、ancestry、whitespace、溯源逐项均在本 checkout 实际复跑并留证；
产品 pytest/GUI/IPC runtime/大媒体容量全部如实记为 `NOT_RUN`。

**decision = `APPROVED`**（针对 `reviewed_head=b2377288680569dbee4e2299fd7dfae4de067c54`）。

理由：Case A 等价性由 blob OID 与字节比较独立证实；8 路径交付零越界且 `diff --check` exit 0；
五个依赖在固定 base 上 ancestry 全 exit 0；契约的每项 AS-IS 断言在固定 base 可独立复现；
唯一链接缺陷（F-001）经裁定为非阻塞且为采用路径的结构性后果；F-002/F-003 均为非阻塞的
引用可达性与证据可复现性问题。无 P0/P1，无关键验证缺失。

**findings_disposition**：F-001 `open / non-blocking / 转 Codex 集成面`；
F-002 `open / non-blocking / 治理导航建议`；F-003 `open / non-blocking / 建议下轮文档修订处理`。
三项均不阻断本次批准，也不要求 Owner 在本轮返修。

**批准的有效边界**：

- 本 Review **不**进入 Integration Gate、**不**集成、**不**启动 M2-S1，**不**变更 M2-C1、M2-S1
  或 Integration Gate 的任何状态。M2-C1 仍为 `blocked`（进行中、未集成），Integration Gate 仍
  `NOT READY`，M2-S1 仍 `NOT_RELEASED`。
- `APPROVED` 只覆盖**文档契约本身**。本 Review 未运行任何产品测试与 runtime 语义验证，
  因此 runtime 语义（版本握手、事件投递/重放/幂等、错误映射落地、大媒体通道容量与安全）
  仍为契约自述的 `PROPOSAL / UNKNOWN`。任何后续实现 Task 必须自行验证，不得复制本批准为
  实现 PASS。
- 页级 `blocked` 的 UI 含义、glyph/文案/行为与 React UI Owner 仍为
  `USER_DECISION_REQUIRED / DEFERRED`，本 Review 未代答。

**剩余风险**：

1. 集成时若复制契约的 §5 As-Is 叙述而压缩 port/service 归属，会重现 R-008 类错位；
2. 若后续 Task 直接按 §6.1 wire DTO 生成 schema 而不回填 §11 未决项，会把 PROPOSAL 固化为
   既成契约；
3. 若无人接管 F-001，契约内将长期保留一个指向交付树之外的门牌号（目标仍可经 `ac38dede…`
   恢复，风险不随时间扩大，但每次审计都要重复该解释）；
4. F-003 若不补注，后续复现者可能重复产生"内容不一致"的误判。

**复审规则**：任何新 head 必须重新独立审查；本批准仅对该 `reviewed_head` 有效，
分支后续变化不延用。
