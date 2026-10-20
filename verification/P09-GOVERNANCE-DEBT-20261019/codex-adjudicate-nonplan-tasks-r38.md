# 40 个非终态 Task 的处置裁定（r38）

日期：2026-10-20  
裁定人：Codex（Lead / Architect / Integrator）  
范围：核实 `doc/tasks/*.md` 中非终态 Task 与 `REBASELINE_PLAN`、`STATUS` 的关系；评估是否有真实活动、给出逐类处置与治理缺陷裁定。仅新增本文件；未修改 Task、Plan、STATUS、既有 verification、工具、源码或测试；未执行 Git 写命令，未调用 `coordinator-lease.py`。

## 裁定摘要

1. **“40 个都不在 Plan”不成立。** 当前 40 个非终态 Task 文件中，`GOV-DEBT-CLEANUP-1` 和 `RUST-ENV-BASELINE-1` 明确出现在 `doc/REBASELINE_PLAN.md`：前者是 `blocked`，后者是 `proposed`。据 Task ID 节点核对，准确表述是：**38 个 Plan 外非终态 Task，加 2 个虽被 Plan 提及但未激活的非终态 Task**。`P22` 等仅以依赖/背景文字出现，不因此成为已激活节点。
2. **40 个的精确状态分布**为 `blocked=10`、`proposed=10`、`changes_requested=4`、`ready=4`、`approved=5`、`in_review=5`、`in_progress=2`。用户给出的表把 `blocked` 多算 1、`approved` 少算 1；这两项误差互相抵消，故总数仍为 40。
3. **状态字段不能证明“仍有人在做”，也不能证明“僵尸”。** 证据显示若干 Task 确有交付、集成、审查或等待动作，但它们并未因此获得当前 Plan 激活资格；另一些 Task 记录的是旧尝试、旧阻塞或尚未开始。不能批量判 `superseded`，也不能仅凭 `approved`/`ready` 状态开工。
4. **本轮不改变 40 个 Task 状态。** 建议保留各自原状态作为历史事实；在有授权的独立治理工作中逐项做状态处置，并建立机器可复核的全量 Task 台账及 Plan 对账。当前唯一允许的动作是记录本裁定。
5. **存在治理缺陷。** 关键缺陷不是 Plan 与 STATUS 描述不同集合本身，而是没有可靠的“所有 Task 文件状态 ↔ Plan 激活集合 ↔ STATUS 汇总”对账机制，导致 `STATUS` 的“当前无活动”与仓库仍有 12 个 `in_progress`/`in_review` Task 并列，且“40 个均为 Plan 外”及“Rust 是非 Plan Task”等表述未经精确核数。

## 1. 核对口径与事实差异

### 1.1 盘点口径

逐个读取 `doc/tasks/*.md` 的 frontmatter `status:`。本次将 `done`、`superseded`、`historical`、`closed_with_limitations`、`cancelled`、`wont_do`、`not_applicable` 视为终态；其余已有状态值作为非终态纳入。本轮实际结果为 40 个文件。没有把仅在 Plan 的依赖列、说明文字或汇总行提及的名字算作 Plan 已激活节点。

### 1.2 核实出的状态与名单

| 状态 | 数量 | Task |
|---|---:|---|
| `blocked` | 10 | `GOV-DEBT-CLEANUP-1`、`P02PRE-R0S2`、`P02PRE-R0S4`、`P02PRE-R0S5`、`P02PRE-R0S6`、`P02PRE-R1H-P2-1-EVIDENCE-CLOSURE`、`P02PRE-R1H-R6-EXEC-A4`、`P02PRE-R1H-R6-EXEC-A5`、`P15-CORE-1`、`P19-UI-FIX-3` |
| `proposed` | 10 | `RUST-ENV-BASELINE-1`、`P09-MANAGED-READ-ROOT-TRUST-1`、`T3.2.1-REPAIR-15-reader-export-lineage`、`T3.2.1-REPAIR-16-bookshelf-page-count`、`T3.2.1-REPAIR-17-mock-local-pipeline-smoke`、`TASK-022`、`TASK-025`、`TASK-026`、`TASK-027`、`M2-TA2B` |
| `changes_requested` | 4 | `T3.2.1-REPAIR-4`、`T3.2.1-REPAIR-5`、`T3.2.1-REPAIR-6`、`T3.2.1-REPAIR-11` |
| `ready` | 4 | `T3.2.1-REPAIR-3`、`T3.2.1-REPAIR-7`、`T3.2.1-REPAIR-9`、`T3.2.1-REPAIR-10` |
| `approved` | 5 | `P02-NEW-TIME-X6`、`P02-NEW-TIME-X6-BUILD-CARGO`、`P02-NEW-TIME-X6-POSTRUN-REVIEW`、`T3.2.1-REPAIR-8`、`T3.2.1-REPAIR-12` |
| `in_review` | 5 | `M2-SFX-ANNOTATE-R2`、`M2-SFX-SYNTH-BG-AUTO`、`P02PRE-R1H-R6-ZCODE-H1`、`P19-AC3-1`、`P22` |
| `in_progress` | 2 | `P02PRE-R1H`、`P02PRE-R1H-R6-EXEC-A6` |
| **合计** | **40** | |

当前 Plan 明确写有 `GOV-DEBT-CLEANUP-1`（`blocked`）和 `RUST-ENV-BASELINE-1`（`proposed`）。Plan 末尾同时写“READY 节点：无”。据此，Plan 中的文字提及并不等于 Task 已被释放；但不能再称这两个 Task 完全不在 Plan。`STATUS.md` 将 `RUST-ENV-BASELINE-1` 称为“下一个可处理的非 Plan Task”，与 Plan 的明确提及冲突，应在后续权威指针更新中更正。

Plan 的“READY 为空”与仓库有四个 `ready` Task 并非同一集合，可以同时为真；同理“Plan 内无活动节点”仅能描述 Plan 的活动集合，不能写成“所有 Task 均终态”或不加限定的“无活动 Task”。当前 Plan 也仍包含 `blocked` 的 GOV 节点与 `proposed` 的 Rust 行，因此“Plan 的全部节点均已终态”若按文件中的每行状态作字面理解也不成立；更准确说法是：**当前没有可释放的 Plan READY 节点，已排期执行主线已收口，但 Plan 中保留 blocked/proposed 条目。**

## 2. 逐类处置裁定

### 2.1 `proposed`（10）——保留原状态，等待范围/优先级裁定

`proposed` 表明尚未释放，不代表被 Plan 取代，也不代表应自动纳入。`RUST-ENV-BASELINE-1` 已列入 Plan，但仍是 `proposed`；其余 9 项未列为活动节点。它们覆盖的路线和来源差异较大，当前材料不足以将其整体归为 A（已被替代）或 B（有意废弃），也不足以判为 C（Plan 漏项）。**逐项保持 `proposed`，不得批量改为 `superseded`，不得直接开工。**后续若继续，应先由 Codex 建立来源/目标架构映射、依赖和冻结范围，再依流程激活；确定不再做时才逐项记录替代/取消依据并走终态生命周期。

### 2.2 `blocked`（10）——保留阻塞记录，不推断所有阻塞仍有效

这些任务的阻塞类型不同：`GOV-DEBT-CLEANUP-1` 的阻塞包含用户审阅/处置授权；P02PRE 家族包含历史运行的外部裁决、源材料或安全 Gate；`P15-CORE-1`、`P19-UI-FIX-3` 的正文仍指向旧架构/旧产品问题。Task 状态本身不足以证明每项外部条件在 2026-10-20 仍未满足。故逐项保留 `blocked`，不批量转 `superseded`，也不把历史 `blocked_by` 当作现行真实依赖。只有重新核实阻塞条件、当前目标架构适用性及 Plan 资格后，才能解除或关闭。

### 2.3 `in_review` / `approved` / `in_progress`（12）——有活动痕迹，但没有统一的“仍活跃”结论

这些状态是流程状态，不能只看状态字段推断当前有人执行，也不能因 Plan 收口就抹除已发生的工作。已查 Task 记录可见以下差别：

- **有近期明确交付/集成/Review 痕迹：**`P19-AC3-1` 记录 2026-10-17 Codex 交付、集成及后续 pin 对账；`P02-NEW-TIME-X6` 与 `P02-NEW-TIME-X6-BUILD-CARGO` 记录 2026-10-14 的执行、独立 Review、构建及集成证据，`P02-NEW-TIME-X6-POSTRUN-REVIEW` 也列为已批准的后继；这些不是“从未做过”的 Task。但它们的当前 `approved`/`in_review` 生命周期状态与“集成完成/审查已通过”的正文记录需要生命周期核对，不能靠本裁定代替正式关闭。
- **有尚未解决的实际 Review/阻塞痕迹：**`P22` 有具体的 DeepSeek Review finding、Cargo/runtime 验收被 P02 Hard Build Barrier 阻止、未集成等记录，表明它曾是实际执行中的 Task；但其历史记录为 2026-10-10，现有 Plan 对 P04/P22 的摘要又称 P22 已集成/完成相关节点，存在明显状态/事实冲突。不能据 `in_review` 判断当前仍有人复审，也不能无证据改成终态。
- **P02PRE 当前运行链仍有多个进行中标签：**`P02PRE-R1H`、`R6-EXEC-A6`、`R6-ZCODE-H1` 等记录了多轮派发、执行、审查和外部等待证据；这是活动痕迹，但不能证明今天仍有 Owner 在工作。Plan 已收口且 P02 未列为可激活主线，因此现状是**未获当前实施授权的历史执行链**，不是可自行续跑的活动 Task。
- **M2 两项 `in_review`：**状态字段说明尚未完成 Review 生命周期；仅凭本轮指定事实来源没有足够依据确认 Reviewer 当前仍在处理或这些 Task 已被其他节点替代，故判为“活性未证实”，保留原状态等待逐项核实。

裁定：这 12 项中**存在真实发生过的活动/交付，不等于当前仍活跃**。没有足够证据证明每项仍有人在做，也没有依据证明每项均已僵死。统一保留状态，并将其标注为“需核实的遗留非终态”；不得由状态名自动触发 dispatch、返修、Review 或集成。尤其 P22 与 P19-AC3-1 应先对照 Plan 摘要、集成提交及 Review 记录做事实核销。

### 2.4 `changes_requested`（4）——不自动返修或重派

四个 T3.2.1 Repair Task 属于旧 PySide6/QML/Qt 产品线；当前 `AGENTS.md` 明确仅允许演进 Windows / React + TypeScript / Tauri / Python Core 新架构，并将旧栈 Task 留作历史证据。它们的返修意见可以是曾发生的真实 Review 事实，但**不构成当前允许实施的返修授权**。均保留状态，停止将其作为待派发实施队列；若相应用户可见行为仍是产品问题，应转换成新架构产品需求后再由 Codex立项，而不是在旧 Task 上继续修。

### 2.5 `ready`（4）——不能开工，必须视为治理冲突优先处理

`T3.2.1-REPAIR-3/7/9/10` 均为旧 Qt/PySide6 打包或发布链任务，带有 owner、branch、worktree 和实施指令；状态 `ready`/`approval: approved_by_user` 只说明其原先曾达到可派发条件。它们不在当前 Plan 激活范围内，且旧架构实现已被 `AGENTS.md` 明确禁止继续演进。**四项均不得开工、恢复分支或派给 Antigravity。**保留 `ready` 作为原始生命周期事实，但标记它们为“未获现行 Plan 授权且与当前产品边界冲突，待 Codex 逐项完成状态处置”。不能仅因矛盾明显而未经 Task 生命周期流程批量写成 `superseded`。

## 3. 是否建立 Plan 外 Task 清单 / 是否批量清理

裁定：**需要一份可查询的 Task 全量/Plan 对账台账，但本次不创建第二个文件，也不批量修改状态。**当前授权只允许产出本 r38 文件。后续应在经授权的治理 Task 中建立版本化或可再生成的清单，逐项记录：Task ID、frontmatter 状态、是否为 Plan 节点/仅文本引用、Plan 激活状态、所属架构、最后可证活动证据日期、当前 Owner/Reviewer 是否仍有效、阻塞条件、建议处置、证据来源及核对日期。STATUS 只摘要计数与当前授权/阻塞项，完整清单应能从仓库事实重复生成。

不建议用一个笼统的 `historical` 批量覆盖所有现有状态：这会抹掉有证据的 Review/返修/阻塞阶段。`superseded` 也必须有明确替代 Task 或架构裁决作依据。建议顺序：先按 Task ID 对账并核实活性；再分别决定 Plan 激活、终态关闭/替代、或保留为 blocked/proposed；最后通过 Task lifecycle 更新 Task、Plan、STATUS 并运行只读 governance checker。清单记录“不可实施理由”可避免误派，但**清单本身不自动改变授权，也不替代 Task 生命周期终态**。

## 4. `GOV-DEBT-CLEANUP-1` 与本问题的关系

`GOV-DEBT-CLEANUP-1` 与本问题有关，但**不是当前这 40 项盘点与处置的既定承接 Task**。Task 标题/AC 聚焦历史 pin 失效、44 项治理检查失败、未跟踪证据分类及经授权的资源处置；Task 本身已记录其 AC1/AC2 清单、AC3–AC5 尚未执行，且用户只授权分类结果，任何入库/清理/归档仍需另行授权。其 `blocked_by` 明确是等待用户审阅和后续处置裁决。

`GOV-DEBT-CLEANUP-1` 确实在 Plan 中出现且状态为 `blocked`，也在 40 个非终态文件内。**不能因本次发现就假定它的 AC 自动扩展为“清理所有 Plan 外 Task”**，更不能自行解除阻塞、改 Task AC 或重派。可以把本裁定作为其后续治理评估的输入；是否由该 Task 承接台账/生命周期核销，须经 Codex 确认范围与授权。它目前 `blocked` 的直接理由不是本轮发现，而是既有的用户审阅/处置授权缺口。

## 5. 治理缺陷及应修层面

**裁定：这是治理缺陷，分为统计/权威指针一致性和生命周期闭环两层。**

1. **报告层（立即纠正事实口径）：** `STATUS` 的“Plan 内无活动节点”必须显式限定为 Plan 集合；不能外推成“仓库内无活动 Task”。`STATUS` 当前提及“40 个非 Plan”及把 Rust 说成非 Plan，与 Task/Plan 实际不符。Plan 中 blocked/proposed 行与“全部节点终态”口径也需区别“排期主线收口”和“文件所有行终态”。本裁定只记录冲突，不越权修改 STATUS。
2. **索引/审计层（建立可复核对账）：** 需要以 `doc/tasks/*.md` 为 Task 文件全集，生成并核对所有非终态计数；将 Plan 的正式节点集合与 Task 文件集合做差集/交集，区分“节点”“依赖引用”“背景提及”。每次发布“无活动”“READY 为空”或“所有 Task 终态”等陈述都应写清统计集合，并能复算。
3. **治理机制层（防止复发）：** 在获授权的治理 Task 中评估只读 checker 或 closeout checklist：检查 STATUS 声明与 Plan/Task 状态分布是否一致；检测 `ready`/`approved`/`in_progress`/`in_review` Task 未被 Plan 激活的情况；输出显式例外（例如历史证据保留/blocked/proposed）。不能把“Plan READY 为空”当作“全仓无待处理 Task”的校验结果。
4. **生命周期层（逐项核销）：** 对真实已交付/已集成却仍 `approved`、真实仍待 Review 的 Task、旧架构 `ready` Task、外部决策 `blocked` Task 分别按协作协议处理，不能用单一状态规则批量推导。

因此“谁会数”的答案是：流程应由可复算的全量 Task 台账/只读治理检查承担，而不是依赖某个参与者记得扫描状态，也不是由 Plan 的 READY 计数代替 Task 文件清点。

## 6. 来源与边界

- `AGENTS.md`：现行唯一目标架构、Plan 授权/激活边界、旧栈不再释放实现 Task 的约束。
- `doc/REBASELINE_PLAN.md`：Plan 行、节点状态、依赖与“READY 节点：无”；明确列出 `GOV-DEBT-CLEANUP-1` 和 `RUST-ENV-BASELINE-1`。
- `doc/STATUS.md`：当前 Plan 内无活动指针、40 项概述、GOV 阻塞项及“RUST 是非 Plan Task”表述。
- `doc/tasks/*.md`：40 个 frontmatter 状态与相关 Owner、阻塞、交付/Review 记录；特别核对 `GOV-DEBT-CLEANUP-1`、P02-NEW-TIME-X6 家族、P02PRE-R1H 家族、`P19-AC3-1`、`P22` 与四个 `T3.2.1-REPAIR-*` ready Task。
- `verification/P09-GOVERNANCE-DEBT-20261019/codex-adjudicate-archdoc-closeout-r37.md`：ARCH-DOC-REBASELINE 的 Gate/消费层裁定，仅作为治理分层参考；不扩展其范围。

本裁定没有为任何 Task 激活 Plan 节点、解除阻塞、授权返修或修改终态。下一步需在授权的治理 Task 中，对上述 40 项建立可复算台账并逐项作生命周期裁定；在完成前，`STATUS` 中“Plan 内无活动”不得解释为“全仓无活动/全部 Task 终态”。
