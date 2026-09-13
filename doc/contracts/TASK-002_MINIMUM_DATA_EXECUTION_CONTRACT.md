# TASK-002 最小数据与执行契约

状态：**Frozen for implementation planning**。本文件只冻结后续 Schema、Pipeline、UI 与测试共同依赖的最小语义，不代表已有数据库、源码或可执行产品。

依据：[D03 数据模型](../03_DATA_MODEL.md)、[D04 用户流程](../04_USER_FLOW.md)、[D05 UI 映射](../05_UI_MAPPING.md)、[D06 Pipeline](../06_TRANSLATION_PIPELINE.md)、[D08 验收标准](../08_ACCEPTANCE_CRITERIA.md)、Gap G06～G13，以及 TASK-001 Review R-011。发生冲突时，本文件是这些缺口的冻结解释；各目标文档保留各自职责，不复制本文件的完整表格。

## 1. 术语与分层

| 概念 | 唯一含义 |
|---|---|
| Run | 一次用户命令及其冻结快照、目标和聚合状态 |
| RunTarget | Run 创建时展开并固定的 Page 或 Region 叶子目标 |
| Task | 一个叶子目标的可调度工作单元；第一版通常对应一个 Page，Region 命令对应一个 Region |
| StepRun | Task 中一次实际 Step 尝试；自动 retry 新增 StepRun，不改写旧尝试 |
| PlanDecision | Planner 对目标 Step 的执行决定，不是运行状态 |
| StageState | Page/Region 当前结果有效性的投影，不是 Task 或 StepRun 状态 |
| ReviewState | 人工校对状态，不是执行状态 |
| Current Revision | 某实体当前可见、可被下游消费的已提交 Revision |
| Candidate | 因 revision/lock 冲突未能成为 current 的后台结果 |

## 2. Revision 与人工保护

### 2.1 Current 指针

- `Region.current_revision_id` 在 Region 创建事务提交时必须非空，指向该 Region 的 `RegionRevision`。
- `MediaArtifact.current_revision_id` 在首个有效 ArtifactRevision 提交后非空；空值只表示尚无可用版本。
- `TranslationConstraint.current_revision_id` 在 Constraint 创建事务提交时必须非空。
- 恢复旧 Revision 不直接把旧记录设为 current；应复制其快照创建新 Revision，再原子更新 current 指针。
- 失败、冲突或取消不得改变任何 current 指针。

必须满足：

| 对象 | 约束 |
|---|---|
| RegionRevision | FK `region_id → Region`；`UNIQUE(region_id, revision_no)`；current 指针与 Revision 必须属于同一 Region |
| ArtifactRevision | FK `artifact_id → MediaArtifact`；`UNIQUE(artifact_id, revision_no)`；current 指针与 Revision 必须属于同一 Artifact |
| ConstraintRevision | FK `constraint_id → TranslationConstraint`；`UNIQUE(constraint_id, revision_no)`；current 指针与 Revision 必须属于同一 Constraint |

SQL 实现应使用可在同一事务中验证“owner ID + revision ID”的复合唯一键/FK或等价约束，不能只靠事务外查询。

### 2.2 Revision 元数据

`RegionRevision` 最少记录：

```text
region_revision_id
region_id
revision_no
snapshot_json
origin: machine | user | imported | restored
review_state: unreviewed | needs_review | confirmed
source_run_id?
source_step_run_id?
restored_from_revision_id?
is_pinned
created_at
```

`ConstraintRevision` 增加 `is_pinned`。`ArtifactRevision` 继续使用既有 `is_pinned`。Pinned Revision 不被自动清理。

规则：

- 机器结果成为 current 时，`origin=machine`，`review_state=needs_review`。
- 用户保存人工译文时，`origin=user`；只有明确“确认 final”才写 `review_state=confirmed`。
- 自动流程不得把 `confirmed` 或 `origin=user` 的 current 内容静默覆盖。
- `rejected` 属候选/约束候选处置，不进入 Region 的 `ReviewState`。

### 2.3 Translation Memory

`TranslationMemory.status` 冻结为 `active | disabled`，非空、默认 `active`。查询只使用 active；disabled 记录保留来源、历史和计数，不参与匹配。正式 TM 仍要求 `is_confirmed=true`，机器译文不能因存在于 current 就自动写入 TM。

## 3. Run 目标与快照

### 3.1 目标展开

- 用户命令的原始 scope 与选择保存在 `PipelineRun.requested_targets_json`。
- Run 创建事务把 Book、Chapter、PageSelection 展开为稳定的 Page/Region 叶子 `PipelineRunTarget`；后续书库增删不改变该 Run。
- `PipelineRunTarget.target_type` 只允许 `page | region`；`page_id` 始终非空；`region_id` 仅在 Region 目标时非空。
- `UNIQUE(pipeline_run_id, target_order)`；同一 Run 内相同 Page/Region 叶子不得重复。
- 空选择、展开后无叶子目标或目标已软删除：返回错误且不创建 Run。

Restart 沿用原 Run 的叶子目标 ID，但重新读取这些目标的 current revision、Lock 与当前设置。目标已删除时，新 Run 创建失败，不改变原 Run。

### 3.2 快照时点

Run 在从“请求”进入持久化 `pending` 前，用一个创建事务完成：

```text
验证命令与非空选择
→ 展开叶子目标
→ 读取 current Region / Lock
→ 解析当前 Settings / Provider Binding / Constraint / Context Policy
→ 写 Run + RunTarget + snapshots
→ Commit pending Run
```

事务提交后：

- 本 Run 的 settings、provider binding、constraint 与 context policy 均读取冻结快照。
- 运行中修改全局配置只影响新 Run。
- 快照保存 Provider/Profile ID、模型与非密配置、配置版本或 Hash；Credential 只保存引用，不保存 Secret。
- Continue 使用原快照；Restart 创建新 Run，并重新读取当前配置与 current revisions。

## 4. 多目标输入与输出映射

单个 `input_region_revision_id` 不足以表达 Context Group。使用两个有序映射：

```text
StepRunInputRef
- step_run_id FK
- input_order
- role: primary | context
- page_id FK
- region_id FK?
- region_revision_id FK?
- artifact_revision_id FK?

StepRunOutputRef
- step_run_id FK
- output_order
- page_id FK
- region_id FK?
- region_revision_id FK?
- artifact_revision_id FK?
```

约束：

- 每条 Ref 必须且只能引用 RegionRevision、ArtifactRevision 中适用的版本；引用的 Revision 必须属于同行 Page/Region。
- `UNIQUE(step_run_id, input_order)` 与 `UNIQUE(step_run_id, output_order)`。
- 每个可写目标必须有一条 `role=primary` 输入；Context 只读，不得被该 Step 写回。
- Provider 返回的每项必须映射到请求中的 primary Page/Region；未知、重复或缺失映射使 Step 以 `OUTPUT_MAPPING_MISMATCH` 失败，任何 current 指针均不更新。

## 5. 状态与决定

### 5.1 枚举

| 层 | 枚举 | 说明 |
|---|---|---|
| PipelineRunStatus | `pending, running, paused, blocked, completed, completed_with_failures, failed, cancelled, interrupted` | Run 聚合状态；只有 Run 使用 paused |
| PipelineTaskStatus | `pending, running, completed, failed, blocked, skipped, cancelled, interrupted` | 叶子目标执行状态 |
| StepRunStatus | `pending, running, completed, failed, cancelled, interrupted` | 一次实际尝试；没有 paused/blocked/skipped |
| PlanDecision | `run, skip_valid, skip_lock, skip_policy, blocked` | Planner 决定；没有 needs_review |
| StageState | `not_started, pending, running, completed, stale, failed, skipped, interrupted, cancelled` | 当前结果有效性投影 |
| ReviewState | `unreviewed, needs_review, confirmed` | 人工校对状态 |

`blocked` 表示当前条件可由用户修复后重新规划；`failed` 表示一次实际执行失败；`skipped` 表示命令、Lock 或 Policy 明确无需执行。三者不能互换。Page/Region Lock 产生 `skip_lock`，缺少必须输入或 Provider 产生 `blocked`。

### 5.2 Run 聚合优先级

每次 Task/StepRun 状态事务提交后重算：

1. 已提交取消请求且尚未先满足完成条件：`cancelled`。
2. Run 级致命错误：`failed`。
3. 异常退出恢复扫描命中未完成执行：`interrupted`。
4. 暂停请求到达安全边界：`paused`。
5. 存在 running：`running`；仅有尚可调度 pending：`pending`。
6. 无可运行单元且存在 blocked：`blocked`。
7. 全部 Task terminal 且至少一个 failed：`completed_with_failures`。
8. 全部 Task terminal 且无 failed：`completed`；skipped 不算失败。

Run 级调度器/存储故障才使用 `failed`；“38 Page 成功、2 Page 失败”使用 `completed_with_failures`。

### 5.3 进度

```text
overall_progress = terminal_step_units / planned_step_units
terminal = completed | failed | cancelled | skip_valid | skip_lock | skip_policy
```

- `blocked` 不算 terminal。`PlanPipelineRun(mode=resume_blocked)` 可重新评估原 Run 的冻结目标、快照和外部可用性，不改写冻结数据；若修复必须采用新的 current Revision 或设置，则原 Run 保持 blocked，由 UI 以原选择调用 `CreatePipelineRun` 创建新 Run。
- 全部因 Lock/Policy 合法跳过时，Run 为 `completed`、进度 100%，skipped 数量单独显示。
- 空选择不创建 Run，因此不进入零分母计算。
- 同一 Page 只进入一个主计数：failed > processing > blocked > completed > skipped > waiting。
- Region 命令仍归属其 Page；Page 计数按该 Run 的目标范围投影，不把同页未选 Region 混入。

## 6. Pause、Stop、Crash 与 Retry

### 6.1 Pause / Stop

- Pause 只在两个 StepRun 之间生效；不可安全中断的 Step 允许完成。
- `paused + Stop → cancelled`，已提交 Revision/Artifact 保留。
- Stop 与最后 Step 完成并发时，以同一数据库事务的提交顺序裁决：先满足完成聚合则保持 completed；否则取消剩余工作并进入 cancelled。
- Stop 不是 Delete 或 Rollback。

### 6.2 Crash 三动作

| 动作 | 契约 |
|---|---|
| Continue | 原 Run 使用原冻结快照；校验已提交成果后从首个未完成/stale Step 继续 |
| Restart | 创建新 Run；保留原 interrupted Run；沿用原叶子目标，重新读取 current Region/Lock/Settings/Provider/Constraint 并重新规划 |
| Abandon | 原 interrupted Run 转为 cancelled，记录 `termination_reason=abandoned_after_interruption`；不创建新 Run、不回滚或删除成果 |

Restart 新 Run 设置 `source_run_id=<原 Run>`、`retry_reason=restart_after_interruption`；原 Run 保持 `interrupted` 并设置 `interruption_disposition=restarted`，UI 不再重复提供 Continue/Restart/Abandon。Continue 不写 disposition；若再次异常退出，状态仍可正常回到可处置的 interrupted。

失败页重试仍是另一种新 Run：只复制失败叶子目标，`retry_reason=retry_failed_targets`。Step 自动 retry 则留在原 Run/Task 内，新增 StepRun，输入 revision 和快照不变。

## 7. Invalidation 与 SFX

### 7.1 失效矩阵

| 变化 | 必须 stale | 不自动 stale |
|---|---|---|
| Original Artifact | Detect 及全部下游 | 无 |
| Region 内容几何（bbox/polygon/crop） | OCR、Color、Segment、Mask、Inpaint、Render | Translation 先保留；新 OCR 文本变化后再使 Term/Translation stale |
| 仅排版几何/样式（offset、rotation、font、spacing、align） | Render | OCR、Translation、Mask、Inpaint |
| ocr_text | TermExtract、Translation、Render | 已确认人工文本保留但 ReviewState→needs_review |
| Constraint | 不追溯修改既有结果 | 只影响新 Run/Restart 快照 |
| TM | 不追溯修改既有结果 | 只影响后续 Translation |
| final_translation | Render | OCR、Mask、Inpaint |
| Mask | Inpaint、Render | OCR、Translation |
| Clean Artifact | Render | OCR、Translation、Mask |
| Inpaint 参数/Provider | 明确 reinpaint 时 Inpaint、Render | 其它既有结果 |
| Lock | 不直接使结果 stale | 影响 Planner 与提交前 Guard |

### 7.2 SFX 安全规则

| Policy | 自动行为 |
|---|---|
| skip | Translation、Mask、Inpaint、Translated Render 对该 Region 均 `skip_policy`；保留原图文字 |
| manual | 可保留 Detect/OCR 供人工参考；自动 Translation、Mask、Inpaint、Translated Render 均 `skip_policy`，直到用户明确保存人工 final 并发起替换/渲染 |
| translate | 进入正常 Translation、Mask、Inpaint、Render DAG |

显式的单 Region 人工命令可以处理 manual SFX，但必须经过 UI 确认并遵守 Lock；批量自动任务不得擦除一个没有替代译文的 SFX。

## 8. 原子提交、候选与局部合成

### 8.1 Step 提交

每个成功 Step 都是独立持久化点：

```text
写唯一临时文件
→ 验证/Hash
→ 原子移动到不可变 Managed Path
→ 进入同一立即写事务（SQLite 可用 `BEGIN IMMEDIATE`）
→ 重新读取全部 primary current revision 与 Lock
→ 全部匹配：插入 Revision/Ref、更新 current 与 StageState
→ 任一不匹配：写 StepResultCandidate，不更新 current
→ 提交事务
```

数据库事务失败时旧 current 不变；已移动但未被数据库引用的文件进入 orphan 清理，不能覆盖已有正式文件。最终 `save` 只汇总 Run/Task 状态及需要的 Page 合成，不再次“提交”已成功 Step。

`StepResultCandidate` 最少记录：

```text
candidate_id
step_run_id
page_id
region_id?
result_kind: region | artifact
base_revision_id
payload_or_artifact_ref
reason: input_changed | lock_changed | composition_base_changed
status: pending | accepted | rejected
created_at
resolved_at?
```

Candidate 通过 `CommitStepResult` 的处置变体处理：输入 `candidate_id` 与 `decision=accept|reject`，Accept 另带用户看到的 `expected_current_refs`。Reject 只把 Candidate 标为 rejected；Accept 仅在 Candidate 仍为 pending、Lock 允许且 expected refs 未变化时重新执行 compare-and-write，创建新的 machine / needs_review Revision 并更新 current；再次冲突时 current 不变且 Candidate 保持 pending。清理 orphan 或历史版本属于 Infrastructure 内部维护，不新增 Application Port。

### 8.2 单 Region Page 合成

- Region 局部 Render 输出仍形成新的 Page translated ArtifactRevision。
- Step 启动时记录 Page 当前 translated ArtifactRevision，以及所有参与合成 Region 的 current revision。
- 新图以当前 Page artifact 为底，仅替换目标 Region 覆盖区。
- 提交时同时比较 Page artifact current 与目标 Region current；任一变化返回 `COMPOSITION_BASE_CHANGED`，不更新 current。重新读取最新底图再重试，避免覆盖同页其它 Region 的并发结果。

## 9. 最小 DTO / Port

| 接口 | 输入 | 输出 |
|---|---|---|
| `CreatePipelineRun` | command_type、scope、selected_ids、overrides | run_id、冻结 target/snapshot 摘要或错误 |
| `PlanPipelineRun` | run_id、mode=`initial|resume_blocked` | Task、PlanDecision、planned_step_units、blocked reasons；resume_blocked 不改写冻结快照 |
| `RecordStepAttempt` | task_id、step_type、input refs、provider/options snapshot | step_run_id |
| `CommitStepResult` | 结果提交：step_run_id、expected input refs、output mapping、temp artifact metadata；Candidate 处置：candidate_id、decision=`accept|reject`，Accept 另带 expected_current_refs | committed revision refs、candidate_id/conflict 或 Candidate disposition |
| `ControlPipelineRun` | run_id、action=`pause|continue|stop|restart|abandon` | 原/新 run_id、最终状态 |
| `GetTaskProgress` | run_id | 从 Run/Target/Task/Step/Stage 派生的只读快照 |

这些是 Application Port 名称与载荷边界，不指定 Python 类、数据库库或网络协议；TASK-005/006 在不改变语义的前提下选择实现形式。

## 10. 错误码

| Code | 层级 / 结果 |
|---|---|
| `EMPTY_TARGET_SELECTION` | Command reject；不创建 Run |
| `TARGET_NOT_FOUND` / `TARGET_DELETED` | Command reject 或 Restart reject |
| `INVALID_RUN_TRANSITION` | Control reject；状态不变 |
| `RUN_NOT_INTERRUPTED` | Restart/Abandon reject |
| `MISSING_REQUIRED_INPUT` | PlanDecision blocked |
| `PROVIDER_UNAVAILABLE` | PlanDecision blocked |
| `INPUT_REVISION_CHANGED` | Candidate；current 不变 |
| `LOCK_CHANGED` | Candidate；current 不变 |
| `OUTPUT_MAPPING_MISMATCH` | StepRun failed；无 current 更新 |
| `COMPOSITION_BASE_CHANGED` | Candidate/replan；Page current 不变 |
| `ARTIFACT_WRITE_FAILED` / `ARTIFACT_HASH_MISMATCH` | StepRun failed；数据库不引用无效文件 |
| `COMMIT_CONFLICT` | StepRun failed 或 Candidate；按是否存在可保留结果区分 |
| `RUN_FATAL_ERROR` | Run failed；已提交成果保留 |

错误详情可以附带 provider、model、page、region、step 与可重试标志，但不得包含 Credential Secret 或完整敏感请求体。

## 11. 验证向量

### 11.1 覆盖矩阵

| 契约区域 | 正常 | 边界 | 失败 / 拒绝 |
|---|---|---|---|
| Revision、人工保护、Pin | V16 | V17 | V01、V14 |
| Translation Memory | V16 | V18 | V18 |
| RunTarget 与快照 | V16、V08～V10 | V04、V15 | V03 |
| 输入输出映射 | V16 | V11 | V11 |
| 状态、控制与进度 | V16、V08～V10 | V02、V05～V07 | V05 |
| Invalidation 与 SFX | V19 | V12、V19 | V12 |
| 原子提交、Candidate 与局部合成 | V16 | V13、V17 | V01、V14 |

### 11.2 向量

| ID | 类型 | 覆盖契约 | Given / When | Then |
|---|---|---|---|---|
| V01 | 失败 | §2、§8～§10 | Translation 从 RegionRevision 10 启动；用户保存 Revision 12；后台返回；随后分别以 expected current 12 拒绝或接受 Candidate | 冲突先产生 `INPUT_REVISION_CHANGED` Candidate 且 current 保持 12；Reject 不改 current；Accept 在二次比较通过时创建 Revision 13（machine / needs_review），再次冲突则 Candidate 保持 pending |
| V02 | 边界 | §3、§5 | 目标全部 Page/Region Lock，计划 Step 为零 | 所有 Task skipped；Run completed；progress=100%；skipped 计数等于目标数 |
| V03 | 失败 | §3、§10 | 空选择、Book 展开后无叶子或选中目标已软删除 | 不创建 Run；分别返回 `EMPTY_TARGET_SELECTION` 或 `TARGET_DELETED` |
| V04 | 边界 | §3 | Book 创建 Run 后新增 Page | 原 RunTarget 不增加；新 Page 只进入后续新 Run |
| V05 | 边界/失败 | §5、§6 | 40 Page 中 38 completed、2 failed | Run `completed_with_failures`；成功成果 current 保留；失败页可创建派生 Run |
| V06 | 边界 | §5、§6 | paused 后 Stop | Run cancelled；已提交成果保留；无新 Step 启动 |
| V07 | 边界 | §5、§6 | Stop 与最后 Step 同时提交 | 事务先完成聚合则 completed；否则 cancelled；无双终态 |
| V08 | 正常 | §3、§5、§6 | interrupted 后 Continue | 同一 run_id、原快照；有效 Step skip_valid，从首个未完成/stale Step 继续 |
| V09 | 正常 | §3、§5、§6 | interrupted 后 Restart，原叶子目标仍存在 | 新 run_id；原 Run 保持 interrupted 且 disposition=restarted；目标相同，快照/current/Lock 重新解析 |
| V10 | 正常 | §5、§6 | interrupted 后 Abandon | 原 Run cancelled，reason 正确；无新 Run、无回滚 |
| V11 | 边界/失败 | §4、§8、§10 | Context Group 返回未知、重复或缺失 Region | `OUTPUT_MAPPING_MISMATCH`；组内任何 current 均不更新 |
| V12 | 边界/失败 | §7、§10 | SFX skip/manual 的批量任务尝试自动写图 | Translation/Mask/Inpaint/Translated Render 均 skip_policy；原图文字不被擦除 |
| V13 | 边界 | §8、§10 | Region A 局部合成期间 Region B 更新 Page artifact | `COMPOSITION_BASE_CHANGED`；旧 Page current 保持；重读新底图后方可重试 |
| V14 | 失败 | §2、§8、§10 | Managed file Hash 失败或 DB commit 失败 | 无新 current；无效文件不入库，孤儿文件可清理 |
| V15 | 边界 | §3、§5、§6、§9 | Run 因冻结 Provider 暂不可用而 blocked；恢复其可用性，同时修改 Settings/Constraint；调用 `PlanPipelineRun(mode=resume_blocked)` | 原 Run 使用原快照重新规划；Restart 或以原选择创建的新 Run 才使用当前设置并形成新快照 |
| V16 | 正常 | §2～§10 | 两个 Region 形成 Context Group；使用 active 且 confirmed 的 TM；输出映射完整；所有 Step 成功 | 每个 Step 独立原子提交且更新正确 current；Run completed；progress=100%；六个 Port 的输入输出均可追溯 |
| V17 | 边界 | §2、§8 | 历史 Revision 已 pinned；执行候选、孤儿及历史清理 | pinned Revision 及其受管 Artifact 均保留；未引用且未 pinned 的孤儿才可清理 |
| V18 | 边界/失败 | §2、§10 | active confirmed TM、disabled TM 并存，并尝试写入非法 status | 仅 active confirmed 参与匹配；disabled 历史保留；非法枚举被存储约束拒绝 |
| V19 | 正常/边界 | §7 | 分别修改 Region 内容几何与仅排版几何/样式 | 内容几何使 OCR/Color/Segment/Mask/Inpaint/Render stale；排版变化只使 Render stale |

## 12. 冻结边界

本 Task 冻结枚举、关系、不变量、动作语义、端口载荷和错误分类。以下仍由后续已规划 Task 完成：实际 SQL DDL/迁移、Python/QML 类型、Repository 与事务实现、Provider 版本、性能数值、测试素材及自动化实现。任何实现若要改变本文件语义，必须通过新的已授权 Task、固定 commit Review 与集成记录。
