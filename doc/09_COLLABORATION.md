# Codex / ZCode / DeepSeek Harness / Antigravity 协作协议

本协议固化协作方式；当前 Milestone、任务树、依赖与 Legacy Mapping 以 [REBASELINE_PLAN](REBASELINE_PLAN.md) 为唯一规划事实源，当前唯一 Active Task 与运行状态以 [STATUS](STATUS.md) 为准。

2026-10-08用户裁决已登记于[GOV-001追加治理范围](tasks/GOV-001.md)：Qoder退出本项目的Owner、Reviewer、设计与接管名单。历史署名与已交付结果仍是历史事实；旧分支/worktree及未提交内容保留。项目策略为`primary_orchestrator=codex; fallback_order=zcode,antigravity; heavy_task_executor=zcode`，优先于共享skill默认配置；不因额度恢复或旧Task引用自动恢复Qoder资格。

## 1. 角色与权限

| Agent | 主责 | 交付物 | 集成权限 |
|---|---|---|---|
| Codex Desktop | Lead / Architect / Integrator；盘点、契约、拆任务、协调依赖、处理冲突 | 基线文档、Task、集成验证与决策记录 | 唯一主线写入和合并责任人 |
| ZCode | 独立 Feature、长任务；新架构 React/Tauri UI/UX 与 GUI 视觉/交互设计及实现主责 | 设计规范、视觉/交互参考、固定 commit、代码与必要测试、Handoff | 自己的任务分支；不得自行合并主线；不得审自己的变更 |
| DeepSeek Harness | 技术实验、OCR/Translation/Inpainting 研究、测试、Bug 分析、独立 Code Review | 可复现实验、测试证据、诊断/Review 报告 | 自己的实验或测试分支；不得自行改生产实现以“证明”Review |
| Antigravity | 通用编程实现；承担 Codex 释放的 Python、应用、基础设施或测试 Feature/长任务 | 固定 commit、代码、必要测试与 Handoff | 自己的任务分支；不得自行合并主线；不得审自己的实现 |
| 用户 | 产品取舍、阶段审核、重大范围变化 | 由 Codex 记录的审核决定 | 决定接管及后续阶段范围 |

Owner 与 Reviewer 必须不同。DeepSeek 自己的测试/实验由 Codex 或 ZCode 独立审查；Codex 的实现优先由 DeepSeek 审查；ZCode / Antigravity 的实现由 Codex或DeepSeek Harness（非作者）独立审查。工具不可用时记录 reviewer_unavailable，等待可用 Reviewer；不得虚构独立批准。

UI/UX/GUI 的规范、信息层级、交互状态、视觉系统和 React 组件边界由 ZCode 主责设计；设计结论先以只读设计 Task 固化并经非作者 Review、Codex 集成，之后才能在单独释放的实现 Task 中落代码。设计身份不自动授予产品代码写权限，也不改变产品需求、四页一级导航、共享契约或 Schema。产品取舍仍由用户决定。

研究结论不自动成为产品需求。诊断任务只读分析与复现；修复需要有允许修改生产代码的 Task。Reviewer 默认只写 Review 报告。

## 2. Git：一个仓库、多个 linked worktree

实际主工作区 `G:/CODEX/New Manga`。当前分支、HEAD、remote 和 dirty 状态必须在每次 Task 开始时由 Git 实测，不在本协议静态写死；截至 2026-09-28 主分支名为 `main`。

批准接管后先由 Codex 创建可复现的初始基线 commit，再开放任务分支。未提交的当前接管文件不能充当可跨 worktree 同步的基线。第一次提交的 author 使用实际 Git 身份，不能冒用其他 Agent 的签名。

并行模式：Codex 使用主工作区；ZCode、DeepSeek 与 Antigravity 使用同仓库的 linked worktree。每个 worktree 独立 checkout/index，Git common directory 相同。另建同名仓库、复制源码目录当真值、在任务 worktree 再执行 git init 均不符合此约定。

开始时记录以下检查结果：

~~~powershell
git rev-parse --show-toplevel
git rev-parse --path-format=absolute --git-common-dir
git branch --show-current
git status --short --branch
git worktree list --porcelain
git rev-parse HEAD
~~~

linked worktree 的 toplevel 可以不同，但 common directory 必须指向本项目 .git。初始仓库 HEAD 不存在时，由 Codex先完成基线提交；其他 Agent 不自行绕过。

分支约定：agent/codex/TASK-xxx-slug、agent/zcode/TASK-xxx-slug、agent/deepseek/TASK-xxx-slug、agent/antigravity/TASK-xxx-slug。一个 Task 一个 Owner，一个分支；实际路径由 Codex 分配并填进 Task，不能复制模板中的示例命令直接执行。

同一物理 checkout 同时只允许一个写入者；无法使用 worktree 时串行交接。read-only Review 也固定被审查 commit，不对正在写的 checkout 运行会改文件的命令。

## 3. 任务释放、并行和共享文件

1. Codex 将用户批准的范围落入 STATUS。
2. Task 依赖全部 done，接口和允许路径具体化，填 owner、base_commit、branch/worktree 后才能从 proposed 变 ready。
3. Codex 串行登记认领，然后 Owner 在任务分支将 ready 改 in_progress；所有 Agent 以已集成 Task 记录为准。两个 Agent 不能仅靠各自编辑副本宣称同时认领成功。
4. 并行只用于无未完成依赖且写集合互不重叠的 Task。共用 Schema、ports、启动配置、依赖清单、AGENTS、Task 总索引由 Codex协调；超出 allowed_paths 时暂停越界部分，在 Task 提出范围变更。
5. Task 文档由 Owner 更新；总索引由 Codex更新。工作日志、阻塞、测试结果及时写进任务文件，长任务不能只留在聊天。
6. 为统一授权口径，所有 Task 的默认元数据维护范围包括由 Codex 负责的 `doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/STATUS.md`、`doc/tasks/README.md`；仅可回填状态、Task 导航和链接，不得借此修改需求、契约或代码范围。Task 的 `allowed_paths` 仍决定 Owner 可写范围。
7. 每个 Agent 的测试数据根目录、临时目录、数据库、模型缓存及输出分别隔离。共享 Git 仓库不等于共享可写 app.db 或用户漫画库。

禁止覆盖他人未提交修改、未经协调切换他人分支、自动 stash 他人内容、强制 push 或清理他人 worktree。冲突由 Codex结合两侧需求处理，禁止整文件盲选 ours/theirs。

## 4. Task 文件约定

任务文件：doc/tasks/TASK-xxx.md；复制 [模板](templates/TASK.md)。

必须包含：ID、kind、status、suggested_owner、实际 owner、reviewer、depends_on、approval、base_commit、branch、worktree、需求来源、结果目标、Acceptance Criteria、allowed_paths、禁止范围、测试计划、产物与交接链接、已知阻塞。

标准阶段为 `READY → ACTIVE → REVIEW → DONE`，前置规划状态为 `proposed`。Task YAML 的 `status` 是唯一状态字段：`ready`=READY；`in_progress`=ACTIVE；`in_review`、`changes_requested`、`approved`=REVIEW；`done`=DONE。

- `proposed`：尚未释放，不得实施。只有 Plan 已列入 DAG、依赖已集成、范围/Owner/Reviewer/base/allowed_paths 已冻结且 STATUS 已登记后，Codex 才能设为 `ready`。
- `ready` → `in_progress`：Owner 明确认领后进入 ACTIVE；同一 Task 同时只能有一个 Owner。
- `in_progress` → `in_review`：交付 head 固定，AC 结果、Handoff 和 canonical evidence 就绪后请求独立 Review。
- `changes_requested`：Review 要求修改；回到 `in_progress` 后修订，并以新 head 再次进入 `in_review`。旧 Review 不随新 head 自动适用。
- `approved`：独立 Review 接受精确 head，等待 Codex 集成；它仍属 REVIEW，不是完成。
- `approved` 集成窗口：Codex 集成后写 integration_commit 与集成后验证；Task 暂留 `approved`，先完成资源 closeout。此时 worktree 只有通过所有独有内容/引用/dirty 检查后才可移除。
- `done`：仅 Codex 可在集成、验证及 closeout 全部通过后设置；须有逐项 AC 证据。随后从 STATUS/Task README 的 Active 指针移除；Plan 可保留必要依赖事实，但终态 Task 不再是 READY 节点。
- `blocked`：暂停态，必须记录 blocker、恢复条件和暂停前状态；解除后回到记录的阶段，不算完成。
- `cancelled`、`superseded`、`historical`、`closed_with_limitations`：终态但不等于技术完成或可发布；不得进入 READY DAG。`historical` 用于保留的旧 Task 记录。`closed_with_limitations` 仅用于用户明确裁决或已批准目标架构取代旧 Task；记录替代依据、closure evidence、未完成 AC/Finding 原始状态及分类，不得改写为 PASS；除新授权外不恢复实施。

只有 Codex 登记/释放 Task、批准集成并设置 `done`；Owner 更新自身 Task 和交付证据；Reviewer 只写独立 Review。Task 状态不能由聊天、分支名或 checklist 推断。`REBASELINE_PLAN` 是 DAG/READY 权威，`STATUS` 是唯一 Active Task 与运行状态权威。

### 4.1 Canonical evidence 与 Review 生命周期

采用 Task 模板中的 `Canonical Evidence` 表：每个已释放 AC/Gate 指向一个当前证据项，并记录仓库相对路径、含该文件的 commit，或仓外/原始输入的 SHA-256。重复执行的尝试输出默认放在 `New Manga.workspace/agent-output/<agent>/<TASK-ID>/`；只有判别力结果进入版本化 `verification/<TASK-ID>/`。已有 Task 指定的共享证据目录和 pins 原位保留。

当前 Task 指针所指的最新 Review/adjudication 才是当前审查结论；它们必须绑定精确 `base_commit` / `reviewed_head`。新 head 或新 Review 使旧结论自动降为 `HISTORICAL` / `SUPERSEDED`，原文件不改写。STATUS 指向的一个 rolling checkpoint 仅供当前恢复；更新指针后旧 checkpoint 降为历史，Task 终态后不再默认读取。

检查器只验证当前权威文档和当前 Task 的相对引用、目标架构哨兵、体量预算、启用 lifecycle v2 的证据 pin，以及 lifecycle v3 的 AC 状态标记（§4.3）。引用缺失、commit 中无对应文件、SHA-256 不匹配或 pin 未填写时为 FAIL；历史目录不作全量扫描。机器检查不能判定语义授权，也不能代替 Reviewer/Codex adjudication。

### 4.2 Task closeout 与派生资源

每个新 Task 在模板 `Resource Manifest` 中记录 worktree、task-env、dataset/model/test-material、artifact、temp、agent-output、exchange；不适用也明确填 `NOT_APPLICABLE`。在 approved 集成窗口由 Codex逐项给出 `DELETE_SAFE`、`MIGRATE`、`ARCHIVE`、`PRESERVE_REFERENCED`、`PRESERVE_USER_DATA`、`PRESERVE_UNKNOWN` 或 `NOT_APPLICABLE`，并记录源/目标、hash 或 manifest、当前引用检查及结果。

仅当已证明可重建、无当前引用/进程使用、无用户修改/独有提交/未跟踪重要文件时，才执行 `DELETE_SAFE`。Worktree 还必须刷新 [Worktree Safety Inventory](WORKTREE_SAFETY_INVENTORY.md)、clean、无独有 commit/untracked 且用普通 `git worktree remove`；不使用 `--force`。有价值数据先迁移到 workspace registry 并验证 hash/文件数，再移除来源。dirty、pinned、未知或无法核实的项目保留并说明原因；保留不阻止 Task DONE，但必须在 manifest 中闭环。

`done` 前完成 `canonical_evidence_status: complete` 与 `resource_closeout_status: complete`，更新 STATUS/Plan/Task 导航中的当前指针，并运行 `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/<TASK-ID>.md`。检查器只读、不删文件；安全清理由 Codex按 manifest 逐项执行并记录，未满足门槛即保留。关闭或取消 Task 同样必须核销资源；只有 `done` 要求所有已释放 AC 通过。

**`allowed_paths` 必须显式包含 `evidence_dir`。** Task 的判别力证据按 §4.1 与 §5 提交到 `verification/<TASK-ID>/`（即模板 frontmatter 的 `evidence_dir`）。仅声明 `evidence_dir` 而不在 `allowed_paths` 中列出该目录，属于**释放时清单不完整**：该类证据**不因 frontmatter 漏列而被追溯判为越界**（其交付依据来自 §4.1 / §5，不是 `allowed_paths` 的逐项授权），但**释放 Task 时的范围冻结必须由 Codex 把 `evidence_dir` 显式列入 `allowed_paths`**。依据：Codex R29 资源裁定第 2 节（`verification/P09-PREVIEW-LIFECYCLE-RECLAIM-1/codex-resource-ruling.md`）。

Task 的开发状态与产品 PipelineRun 状态是两套不同概念，不能混入应用 Schema。

测试项必须注明 planned / executed、命令、环境、结果、证据；结果中的 `passed` 与 `skipped` 必须分列（如 `290 passed, 6 skipped`），并为每个 skip 记录原因。测试命令尚无实现时写“计划命令”，不能假装可立即运行。Acceptance Criteria 的逐项满足需实际证据，不能仅引用 D08 标题。

### 4.3 AC 状态的显式标记（lifecycle v3）

**为什么需要它。** 只靠 `- [ ]` / `- [x]` 无法区分三种完全不同的情况：
「已完成但忘了勾」「确实未完成」「因外部原因阻塞」。前两种在文件里长得一样，
第三种也没有位置记录原因。结果是**漏勾无法被机械发现**——检查器不知道该不该报错，
Reviewer 只能靠肉眼。本项目已多次发生「AC 全部做完、一个框都没勾」。

**适用范围。** 本节对 `governance_version: 3` 的 Task 生效。v1/v2 Task 保持原状，
**不回溯补标**：它们的 `[x]`/`[ ]` 语义不变，检查器也不对它们套用本节规则。
`governance_version: 3` 由 Codex 释放新 Task 时写入；已释放的 v2 Task 不因本节升级。

**标记形式。** 每个 AC 行末（不受行内格式影响）追加一个状态标记：

```
- [x] **AC1 标题**：正文…… <<MET>>
- [ ] **AC2 标题**：正文…… <<BLOCKED: 无头 Windows 无法取得 WebView2 句柄>>
- [ ] **AC3 标题**：正文…… <<PARTIAL: ①/② 达成，③ 阻塞>>
- [x] **AC4 标题**：正文…… <<NOT_APPLICABLE: 本 Task 无数据面>>
```

语法：`<<STATUS>>` 或 `<<STATUS: 原因>>`，`STATUS` ∈
`MET` / `PARTIAL` / `BLOCKED` / `NOT_APPLICABLE`（大小写敏感，全大写）。
`PARTIAL` / `BLOCKED` / `NOT_APPLICABLE` **必须带非空原因**；`MET` 不得带原因。
标记在行末，其后不得再有其它内容。

**勾选与标记的一致性规则**（这是门禁的核心）：

| 勾选 | 允许的标记 | 语义 |
|---|---|---|
| `[x]` | `MET` / `NOT_APPLICABLE` | 已达成，或本 Task 范围内不适用 |
| `[ ]` | `PARTIAL` / `BLOCKED` | 未达成且**必须**写明原因 |

**矛盾组合一律不允许**：`[x]` + `BLOCKED`、`[ ]` + `MET`、
以及任何缺标记的 AC（在 v3 Task 中）。

**为什么 `MET` 不能带原因。** `MET` 表示该 AC 已达成，其依据应在
`Canonical Evidence` 中登记，而不是写在 AC 行末。允许 `MET` 附原因会诱导
「用文字解释代替证据」——正是本规则要防的。

**`NOT_APPLICABLE` 与 `MET` 的区别。** `MET` = 该 AC 在本 Task 范围内成立且已验证；
`NOT_APPLICABLE` = 该 AC 在本 Task 范围内**不产生要求**（例如纯前端 Task 的
数据面 AC）。两者都勾选，但证据门槛不同：`NOT_APPLICABLE` 只需说明理由，
`MET` 需要 Canonical Evidence 支撑。

**门禁。** `tools/governance/check.ps1` 对 v3 Task 施加以下检查：

- 状态进入 `in_review`、`approved`、`done`、`closed_with_limitations` 时，
  **每个 AC 必须带合法标记**；缺失即 FAIL。
- 勾选与标记的组合必须符合上表；矛盾即 FAIL。
- `PARTIAL` / `BLOCKED` / `NOT_APPLICABLE` 缺原因即 FAIL。

**这个门禁不能做什么。** 它只验证**标记的存在与自洽**，
不能验证标记是否**诚实**——把未做的写成 `MET` 不会被它发现。
那需要 `Canonical Evidence` 的 pin 校验与 Reviewer 判断，本节不重复。

**不回溯的代价（明确记录）。** 截至 v3 引入时，本仓库 102 个有 AC 的 Task 共
618 个 AC，其中 149 个未勾选，分布在 25 个已进入 `in_review` 或终态的 Task 中。
这些 Task 一律保持 v2，不补标、不因本节变红。**本门禁只阻止新增此类缺陷，不清算存量。**
存量由后续专项 Task 处理。

## 5. Handoff

交付文件：doc/handoffs/TASK-xxx-<short-head>.md，使用 [Handoff 模板](templates/HANDOFF.md)。

至少记录：基线 commit、交付 commit、提交列表、变更路径、做了什么、AC 对照、实际测试命令和结果、未跑项、风险/遗留问题、启动或复现方式、下一接收者。实验额外记录数据来源/许可、数据 Hash、模型版本/权重 Hash、硬件、参数、耗时/质量测量和结论适用范围。

验证证据提交到本仓库对应 `verification/` 路径并由 Handoff 引用；Agent 会话、仓库外临时路径或未提交的本机状态不能作为唯一证据。安装或构建日志支撑交付结论时一并入库；Secret 只记录脱敏结果。

Handoff 在交付 head 之后以文档提交追加，引用之前的实现 head；避免要求文件包含自己的 commit hash。修订生产内容必须生成新的 handoff/head，并重新审查。

### 5.1 Task 完成后的下一任务建议

每次 Task 进入 `done`，或 Codex 明确关闭一个 review / research / integration
切片时，交付者和 Codex 最终回复都必须提供一个基于当前仓库状态的下一任务建议。
没有安全、已授权的下一任务时，明确写“无需下一步操作”，不能用泛泛的“继续开发”代替。

下一任务建议必须包含：

1. **Task**：Roadmap ID 或现有 Task ID、标题、推荐启动条件和依赖。
2. **Agent**：根据任务性质指定合适的 Owner；ZCode 负责独立 Feature/长任务，
   Antigravity 负责通用编程实现，ZCode同时主责React/Tauri UI/UX，DeepSeek Harness 负责研究/实验/测试/独立 Review，
   Codex 负责契约、共享 seam、主线集成和 Release Gate。Owner 与 Reviewer 必须不同。
3. **Recovery point**：实际仓库路径、branch/worktree、固定 `base_commit` 和当前
   `head`；若 worktree 尚未创建，写明“待 Codex 创建”，不得臆造路径或 commit。
4. **Scope**：允许修改路径、明确的禁止路径、是否需要共享接口/Schema/依赖变更授权。
5. **Deliverables**：代码/测试/Handoff/verification 或研究报告的具体文件和结果。
6. **Verification**：可复制的命令、环境、逐项验收标准、skip/blocker 记录方式和
   完成 Gate。不得把 planned、NOT_RUN 或 BLOCKED 写成 PASS。
7. **Forwardable instruction**：一段可直接发送给 Owner 的完整指令，至少重复上述
   工作路径、Task、base/head、范围、交付物和验证要求。

下一任务建议不等于任务释放。Codex 仍须先在 `STATUS` 登记范围，确认依赖、Owner、
Reviewer、base、branch、worktree 和 allowed paths，再将 Task 从 `proposed` 改为
`ready`。不得因为当前 Task 完成而自动启动下一 Task；若需要用户做产品取舍，建议必须
标为 `BLOCKED` 或 `等待用户裁决` 并停止实施。

### 5.2 Rolling Checkpoint 与 Resume Reality Check

长任务在以下节点写入 Task-local checkpoint：完成 Reality Check、重要
Subtask、关键接口或测试状态变化、首次形成复杂 dirty worktree、出现
Blocker、准备暂停或切换 Agent。优先放在对应的
`verification/<Task-ID>/`；已有 Handoff/Review 能完整承载时复用它们，
不另建全局 `CHECKPOINT.md`。

Checkpoint 至少记录：

```text
Timestamp / Agent / Task ID
TaskStatus / ExecutionState
Branch / Worktree / start commit / current HEAD
Working Tree（modified / added / deleted / staged / untracked）
Completed Steps / Current Working Point / Next Exact Step
Tests Already Run / Tests Remaining / Current Errors
Blockers / Decisions / Open Questions
Evidence / Confidence / Resume Safety
```

`TaskStatus` 继续使用本协议 §4 的状态机；`ExecutionState` 只描述
`IDLE / ACTIVE / PAUSED / CHECKPOINTED / INTERRUPTED`，不写入产品 Schema，
也不替代 Task 状态。没有 checkpoint 的聊天内容不构成可恢复事实。

接手 `in_progress`、`changes_requested`、`blocked` 或带 checkpoint 的 Task
时，先逐项比较：checkpoint HEAD 与当前 HEAD、branch、worktree、记录的
文件集合、Task 状态和测试环境。结果明确记录为 `RESUME_SAFE` 或
`DRIFT_DETECTED`；若 HEAD 或相关文件已变化，先分析漂移来源并由 Codex
重新确认范围，不能盲目覆盖或重置工作区。

每次 Task Exit 必须持久化 Task 状态、最近 checkpoint/Handoff 和必要的
Execution Event；退出不等于完成。只有 AC、独立 Review、集成和集成后
验证全部满足时，才可将 Task 置为 `done`。

## 6. 独立 Review 与集成

使用 [Review 模板](templates/REVIEW.md)。Review 必须固定 base_commit 与 reviewed_head；分支随后变化不延用旧批准。

### 6.1 DeepSeek Harness CLI 与 Web 会话可见性

用真实 DSH CLI 派发 Review 时，从被审查任务的 linked worktree 根目录运行 `dsh --profile headless --json`，保存退出码并记录 JSONL `session` 事件中的 session ID。`--json` 只输出本次运行事件并报告 ID；每次默认新建独立会话，不会把内容追加到当前打开的 Web 对话。只有 Web 端实际看到该会话及其 Review 内容，才可记为 Web 可见。

若需要从 DSH Web 查看 CLI 会话，先把该 Review 的**精确 worktree 路径**登记为 Web Workspace；主仓库 Workspace 不自动覆盖另一个 linked worktree。headless 会话未出现在 Web 列表时，重启 DSH Web 主机以重新发现已持久化会话，再到对应 Workspace 核对会话和 transcript。仅刷新浏览器页面或拥有 session ID 均不算显示成功。

若重启后仍不可见，记录 DSH 版本、worktree 路径、session ID 和检查结果，标记 `web_visibility=unverified`；不要把 headless 运行描述成 Web 对话已显示，也不要用 Codex 模拟代替真实 DSH Review。继续已有会话时才传入 `--session-id <id>`，并确认该会话属于相同工作目录且可由当前 profile 接管。

1. Reviewer 在独立工作区读完整 diff、受影响调用链、需求和测试，不只看作者摘要。
2. **Standards 视角（建议，非强制；2026-09-18 用户决定取消"双轴"强制口径）**：代码是否符合**当前有效**标准——`AGENTS.md`、本协议、[AD-001 目标架构](AD-001_TARGET_DESKTOP_ARCHITECTURE.md)、本 Task 的允许/禁止范围及 Task 明确引用的冻结 contract。`02_TECHNICAL_ARCHITECTURE_.md`、QML 映射和旧 D08 中的 PyInstaller/Qt 条款属于 Legacy/Historical，不得作为新架构实现标准。仓库**未记录**标准的方面适用 Fowler smell baseline（_Refactoring_ 第 3 章）作为**判断项**（须带 label 并引用 hunk）；**仓库记录的标准优先于 baseline**，工具已强制的项跳过。
3. **Spec 视角（建议，非强制；同上）**：AC、写回范围、命令语义、数据保护、失败/暂停/恢复、UI 行为是否符合来源。来源顺序：本 Task 文件 AC → 其引用的 D01～D08 条文与 `doc/contracts/**` → STATUS 中的用户裁决；**不得**用聊天记录或旧仓库推断已有实现。
4. Architecture 轴：分层、共享契约、依赖、安全、持久化、可选 AI 依赖边界；新架构依赖方向为 `React/WebView → explicit Tauri IPC → Python Application → Domain/Ports → Infrastructure Adapters`，禁止 React/Rust 直接访问 SQLite、任意 OS 路径或模型，也禁止反向依赖。Legacy QML 只作历史证据。
5. Verification 轴：运行相关检查；逐项写 PASS/FAIL/BLOCKED/NOT_RUN。没有运行环境时不能批准未核实的关键路径。
6. **报告形式（不强制）**：报告须覆盖 **Architecture** 与 **Verification** 两面（第 4/5 条）。`code-review` 技能的 Standards/Spec 两视角**可采用也可不用**；采用时建议分别呈现（一个变更可能通过一面而在另一面失败），但**不再强制**分节、命名或"不跨轴排名"的写法。**取消**下列强制项（2026-09-18 用户决定，理由：并行双轴子代理能力不可用）：①不再要求两视角各由独立 sub-agent **并行**执行；②不再要求"两遍相互隔离"检查；③不再要求在报告中声明该偏差或附派发尝试证据。该能力**会话相关**（本会话多次派发未启动；DSH 会话曾成功），故不作为任何 Review 的前置条件。
7. **视角状态声明（建议）**：如报告采用了多个视角，建议各自标注 `executed`/`N/A` 并给一行小结；**缺声明不再视为 Review 未完成**，也不影响能否批准。批准与否只取决于第 8 条（P0/P1 是否未解决、关键验证是否缺失）。
8. Findings 写明严重级别、文件/行、触发条件、影响、复现和建议。记录 findings_disposition；P0/P1 未解决不能批准。无发现也记录审查覆盖和未覆盖风险。
9. Codex 核对 Review 与当前 head，检查 Task 路径范围及依赖基线，串行集成。默认保留来源分支的 merge 提交；必要时 cherry-pick 需记录 old→new commit 对应关系。
10. 基线变化或合并冲突影响行为时，重新跑受影响测试并触发复审。即使无冲突，仍执行该切片的集成检查。
11. 集成后更新 Task、STATUS、当前导航及验收证据；测试结果只能适用于记录的 commit。按 §4.2 完成资源收口后，移除来源分支/worktree 仍须满足安全门槛。

12. **证据纪律（2026-09-19 增补，Q-009）**：①凡以「全仓/定向 `N passed`」充当证据的运行日志，**必须带 EXIT 码与 shell/venv 头**（写明 shell 类型与解释器路径，且与声明口径一致），并**逐次入库**；只有末两行、或只写「×N 全绿」的日志**不可复核**，按未提供处理。②**判别力证据（「对修前失败/对照矩阵」）必须是 artefact**（日志或探针输出入库）；**artefact 缺失即记 `NOT_RUN`**，不得以散文（例如「守卫移除必失败」）或 `N passed` 代替。③skip 必须**逐条**列出来源与原因；`BLOCKED`/`NOT_RUN` 不得在 Task、Handoff 或台账里记为通过。④口径不同的数字（如 `openssl` 可用与不可用）必须在同一处写明**总数**并解释差值，避免并排呈现造成「skip 被消除」的误读。

仅元数据归档提交无需重跑产品测试；生产代码/契约/测试变化不能用此规则免检。`tools/governance/check.ps1` 是本地只读守卫；它不作语义裁决或删除。Git hooks 和远端保护未配置，因此 Task 生命周期授权仍由 Codex 按本协议执行。

## 7. 发布与阶段审核

接管通过、契约冻结、切片通过、最终发布是不同 Gate。Mock Pipeline 通过只能证明编排和保存链路，不能证明 OCR/翻译/修复质量。

发布按 D08 执行：P0/P1 和干净 Windows 验证等要求不因 Roadmap 分阶段而降低。范围删减、阈值豁免先形成用户可审查的文档决定，不能把未完成标成 N/A。当前未授权提交远端、创建外部项目或向其他人发送消息。
