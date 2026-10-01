---
task_id: M2-TASKS-BACKFILL-MULTIREGION
author: ZCode
recipient: Codex（Integrator）；DeepSeek Harness（非作者 Reviewer）
base_commit: f99a6c55
delivery_head: f541b2f4
status: in_review
---

# Handoff：M2-TASKS-BACKFILL-MULTIREGION（executor backfill 多 region 页逐 region 跟进调度）

## 交付结果

### AC1 勘察结论（落笔前完成，全部有代码锚点；未触发 BLOCKED_ON_RULING——语义选项内部已有先例可依，见下）

1. **backfill 触发时机**：不是 resume/恢复路径。`_backfill_detected_regions` 在 `commit_step_result` 内、detect 步骤 commit 成功（`outcome.status == "applied"`）时**同步**调用（`src/application/tasks/service.py:650-660`，delivery 版）。detect 失败（0 候选 `INVALID_INPUT` / provider 缺配）不触发。
2. **绑定模型（修复前）**：页任务（`TargetType.PAGE`）plan 时页面无 Region ⇒ `_plan_target` 生成**单个 regionless unit 链**（unit_id=`{task_id}:{page_id}:{step_type}`，target_id=page_id），`_plan_region` 在链首插入 detect（`service.py:346-358`）。detect handler 按 `reading_order` 产出 `result.outputs["region_ids"]`（复用路径排序、新建路径按 candidate 顺序，`infrastructure/providers/handlers.py:258-299`）。backfill 把 detect 之后的 regionless units 重绑到 `region_ids[0]`。
3. **多 region 页当前实际行为（缺陷实证）**：`region_ids[1:]` 没有任何对应 PlanUnit ⇒ 第二个及以后的 region 完全不被初始执行跟进。三重实证：① `test_r2_multiple_regions_only_primary_reocr_completed`（`tests/pipeline/test_regionless_rebinding.py` 旧断言"secondary untouched"）；② `tests/core/test_sfx_policy_end_to_end.py:244` 旧断言 SFX region 译文为空并注释"backfill binds the first region only (the registered scheduling slice)"；③ 修复前 docstring 自认"fanning a page task out over every detected Region is a later scheduling slice"。
4. **恢复路径已天然逐 region fan-out（选定语义的内部先例）**：`plan_run(mode="continue"/"resume_blocked")` 用 `catalog.current()` 替代冻结快照，`_plan_target` 遍历页面**所有**现存 Region、每 Region 调一次 `_plan_region`（unit_id=`{task_id}:{region_id}:{step_type}`）。实证=N7（`test_regionless_rebinding.py:716-725`"fan-out on recovery"，中断恢复后两个 region 各得一次 OCR）。即：修复前**初始执行与恢复路径语义不一致**（初始只跑首 region，恢复后反而跑全部）。
5. **持久化**：`SqlitePipelineStore.put` 每次 persist 全量 DELETE+重插（`pipeline_runs.planned_step_units` 列 + `pipeline_tasks.units_json`，`infrastructure/sqlite/pipeline.py:393-455`）——backfill 追加 units 后的 `_persist(run)` 自动落库，**无需 store/schema 变更**（禁改面零触碰）。
6. **执行层关键事实（红绿过程中发现）**：SFX policy gate 在**plan 层**生效（`_decide_step` → `_sfx_gate_suppresses` → `decide_sfx_translation`，SKIP_POLICY 向 segment/mask_refine/inpaint/render 传播）；production `handle_translate` 本身**不**经 gate。因此"克隆 primary unit 并照抄其 plan 期 decision"的初版实现会让 manual/skip 的 SFX region 被机器翻译（违反 D06 §85 / AC-SFX-001，被 SFX e2e manual 场景红态抓到）——最终实现改用 `_plan_region` 对 live region 快照**真实规划**（与恢复路径同一函数、同一决策过程），SFX/lock/stage/provider 判断全部正确且在允许面内闭环。

### 语义选项对比（任务书 AC1 要求；结论=选项 A，无产品意图歧义故不停等）

| 选项 | 行为 | 改动面 | 风险 | 判定 |
|---|---|---|---|---|
| **A 逐 region 展开（选定）** | detect commit 后 primary 原位重绑（既有单 region 行为逐字节保留）；对 `region_ids[1:]` 每个 region 用 `_plan_region` 规划追加 unit 链；`planned_step_units` 同步增长 | 仅 `service.py` `_backfill_detected_regions`（+`run` 参数） | 克隆链 decision 由 live region 快照决定（=恢复路径同款，无新增近似）；串行先到先停（primary 失败→剩余 cancel，页任务原子性不变，F5 固化） | **采纳**：与恢复路径语义一致（消除不一致而非发明新语义）；唯一落在允许面内的修复 |
| B 1:N 绑定 | 一个 unit 绑多 region 依次执行 | 需改 domain `PlanUnit` 实体 | `src/domain/**` 为禁改面（"schema/实体零变更"） | 排除（禁改面直接排除，非语义偏好） |
| C 页任务完成后 region 自驱动 | primary 完成后由调度创建 N-1 个 region-level run | run 生成 run 的编排，超出 tasks 模块（bootstrap/contracts 禁改） | 改动面最大；进度聚合/run 依赖引入新调度概念 | 排除（超允许面，改动不成比例） |
| D 维持现状 | 多 region 页仅首 region 跟进 | 无 | 缺陷保持；与用户裁决（修复）相悖 | 排除 |

### 实现（AC2；`src/application/tasks/service.py` 单文件，292 行净增含测试）

- `_backfill_detected_regions` 改为实例方法（需 `self._catalog`），签名 `(run, task, unit, result)`；primary 重绑逻辑逐字节保留（单 region 页行为零变化，F2 固化）。
- fan-out：对 `region_ids[1:]` 每个 region `self._catalog.current(region_id)` 取 live 快照 → `_plan_region(run, task, region_view, region_snapshot)` 生成追加 units（unit_id=`{task_id}:{region_id}:{step_type}`，与恢复路径格式一致）。
- `run.planned_step_units += len(extra_units)` + `terminal_unit_ids`/`terminal_step_units` 同步（decision 为终态的克隆 unit 与 `plan_run` 同口径计入）：progress 分母与 terminal 计数精确闭合（R1/F1/F5 断言 + r1 返修新增 SFX 默认 skip 断言）。注：f541b2f4 初版只做分母增量、`SKIP_*` 克隆 unit 不进 terminal（DSH r1 R1，COMPLETED run 的 progress 永远 < 1.0），该「精确闭合」声称在初版**不成立**，r1 返修后才成立。
- fan-out 集合=detect 输出（快照语义）：run 中途新增的 region 不被当前 run 跟进，由下一次（重）规划拾取（F4 固化）。
- **零协议/schema 变更**：命令协议、`CommandType`、DB schema、store 全部未动。

### AC 对照

- [x] **AC1 勘察先行**：见上，结论先写入本 handoff 后落笔（实现 commit f541b2f4）。
- [x] **AC2 最小实现**：`service.py` 单文件；不改命令协议与 DB schema；其他 application 模块零触碰（未触发移交条款）。
- [x] **AC3 先红后绿**：红 6 failed / 11 passed（`red-f99a6c55-src-plus-tests.log`；含 F1 主红/F4/F5 与 R0-R2 旧语义断言）→ 绿 17/17 + SFX e2e 2/2 → 三套件 **579 passed + 2 skipped + 0 failed**（基线 f99a6c55=574+2sk，新增 5 测试零回退）；单 region 页零变化（F2+N1/N2/N6 全过）；0 region 页边界（F3+N3）；region 中途新增边界（F4）。初次红态曾为 7 failed（R3 当时断言 ocr_steps==2），后按 fan-out 执行顺序（primary 链先行失败即 cancel 剩余，可见行为与旧版相同）将 R3 断言定为 1 并在 F5 固化失败传染语义——红绿数字以 verification 日志为准。
- [x] **AC4 文档**：本 handoff + Task 回填 + verification 四份日志；相邻发现只登记（见 §风险与遗留）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 基线（修复前 f99a6c55） | `pytest tests/core tests/pipeline tests/providers -q` | T3.2.1-packaging-py312（py3.12.3+PySide6 6.11.2+onnxruntime 1.30.0，本会话补装）@ f99a6c55 | 574 passed + 2 skipped + 0 failed（2 skip=transformers 未装的环境性 skip+registry_readiness 历史条件；与 STATUS"530+1sk"差异=f99a6c55 批次新增测试） | 会话记录（未入库） |
| AC3 红 | `git checkout f99a6c55 -- src/application/tasks/service.py` 后跑 `pytest tests/pipeline/test_regionless_rebinding.py -q` | 同上 @ f541b2f4 tests + f99a6c55 service.py | 6 failed 11 passed（复现命令见上） | `verification/M2-TASKS-BACKFILL-MULTIREGION/red-f99a6c55-src-plus-tests.log` |
| AC3 绿（目标文件） | `pytest tests/pipeline/test_regionless_rebinding.py tests/core/test_sfx_policy_end_to_end.py -q` | 同上 @ f541b2f4 | 19 passed | `verification/M2-TASKS-BACKFILL-MULTIREGION/green-f541b2f4-target-files.log` |
| AC3 绿（三套件） | `pytest tests/core tests/pipeline tests/providers -q` | 同上 @ f541b2f4 | 579 passed + 2 skipped + 0 failed | `verification/M2-TASKS-BACKFILL-MULTIREGION/green-f541b2f4-three-suites.log` |
| 溢出回归（PipelineService 消费方） | `pytest tests/workbench tests/m2_acceptance tests/editing -q` | 同上 @ f541b2f4 | 188 passed 0 failed | `verification/M2-TASKS-BACKFILL-MULTIREGION/green-f541b2f4-overflow-suites.log` |
| 禁改面 | `git diff --check`；`git status --porcelain` 逐文件核对 | @ f541b2f4 | EXIT=0；改动=src/application/tasks/service.py + 2 测试文件 + verification/Task/handoff | 会话记录 |

未运行：全 11 套件（本任务纪律口径=三套件；另跑 workbench/m2_acceptance/editing 作为消费方溢出检查）。Mock 成功不表述为模型质量达标——本任务为调度语义修复，不涉及质量判断。

## 接收方式

- 分支 `agent/zcode/M2-TASKS-BACKFILL-MULTIREGION`，worktree `G:/CODEX/New Manga.worktrees/M2-TASKS-BACKFILL-MULTIREGION-zcode`，base=`f99a6c55`，delivery_head=`f541b2f4`。
- 复现命令（红态）：`git checkout f99a6c55 -- src/application/tasks/service.py && PYTHONPATH=src <venv>/python -m pytest tests/pipeline/test_regionless_rebinding.py -q`；绿态：还原后同命令。
- 测试环境：`G:/CODEX/New Manga.task-envs/T3.2.1-packaging-py312/Scripts/python.exe`（本会话补装 `onnxruntime` CPU 版以复现 0 failed 基线；未装则 `test_detection_sfx.py` 3 条真实权重测试环境性失败——属环境前置，非本任务改动）。
- Reviewer 检查建议：① `_backfill_detected_regions` 与 `_plan_region` 的复用关系（恢复路径同款决策）；② SFX gate 经 plan 层 SKIP_POLICY 闭环（e2e manual 场景 + N 系）；③ `planned_step_units` 增量与 terminal 闭合（R1/F1/F5 断言；r1 返修后含 `SKIP_POLICY` 克隆 unit 的 SFX 默认 skip 断言）。

## 下一任务建议（必填）

- Task ID / 标题：无需新建 Task——本 Task 待 DSH 非作者 Review → Codex 集成即闭环。
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者静态 Review，按任务书 frontmatter）。
- 推荐原因与前置依赖：本 handoff + delivery f541b2f4 已就绪；集成序=批次约定 TILING → **BACKFILL** → SFX-UI。
- Recovery point：仓库 G:/CODEX/New Manga，branch `agent/zcode/M2-TASKS-BACKFILL-MULTIREGION`，base `f99a6c55`，head `f541b2f4`。
- 允许修改路径：review 意见落 `src/application/tasks/service.py` / `tests/pipeline/test_regionless_rebinding.py` / `tests/core/test_sfx_policy_end_to_end.py` / Task/handoff/verification。
- 禁止范围与新增授权条件：任务书禁改面不变；schema/命令协议变更仍需停等登记。
- 交付物：本 Task 全链（Task+handoff+verification+commit）。
- 验证命令、环境与完成 Gate：三套件 0 failed（命令见上表）；红绿日志在 `verification/M2-TASKS-BACKFILL-MULTIREGION/`。
- 可直接转发给 Agent 的指令：见 STATUS 交接口径（本文件即为转发载体）。

## 风险与遗留

1. **fan-out 后的 SFX 行为面变化（非 primary 已按 gate 正确闭环，如实登记）**：多 region 页 TRANSLATE_ALL 现在会跟进所有检出 region——policy=translate 的 SFX region 在同一次 run 内被翻译（SFX e2e translate 场景新断言）；**非 primary** 的 policy=manual/skip SFX region 由 plan 层 SKIP_POLICY 保持不翻译且图像步骤连带跳过（e2e manual 场景原断言不变全绿）。primary（`region_ids[0]`）仍沿用 detect 前页级决策、SFX gate 不可见（DSH r1 R2：既有缺陷、非本 Task 引入；恢复路径会 gate 它，语义不一致在 primary 上存在）——已登记独立 Task 候选并附裁决请求（见下「独立 Task 候选登记」）。
2. **失败传染语义固化（F5）**：多 region 页 primary 链失败（如 LOCK_CHANGED/provider 缺配）⇒ task FAILED、剩余 region 的克隆 units 被 cancel——页任务串行原子性与单 region 页一致；`retry_failed_targets` 可按页重试（region-level fan-out 在重规划时天然恢复，N7 实证）。
3. **region 中途新增/删除**：fan-out 集合=detect 输出（快照语义，F4 固化）；run 中途新增 region 由下一次规划拾取。删除场景未新增测试（`_record_step_attempt` 对已删 region 的 `TARGET_DELETED` 传播是**既有路径行为**，primary 与克隆 unit 同构暴露，本任务不扩大范围——如需治理建议另立 Task 登记）。另据 DSH r1 R3：backfill 的规划期读取 `self._catalog.current(region_id)` 位于 detect commit 之后、`commit_step_result` 内且原先无异常防护——r1 返修已落地 try/except `PipelineError`：读取窗口内被删/不可读（如 `_region_or_error` 额外前置不满足）的 region 按 `TARGET_DELETED` 语义跳过该 region（与恢复路径重读 live Regions 的最终语义一致），异常不再穿透 `execute_run` 使 run 滞留 `RUNNING`（DB 已落 detect、只能靠 `recover_running_runs` 自愈的失配窗口已消除）。
4. **相邻发现（只登记不修）**：unit_id 内嵌 target 与真实 target 不一致的展示层债务在克隆链上依然存在（primary unit 保留 plan 期 page id 形态 unit_id，克隆 unit 为 region id 形态——两种形态并存；terminal_unit_ids 以 unit_id 为键的正确性不受影响，R1 断言固化）；`get_task_progress` 的 reasons 聚合对 SKIP_POLICY 的展示未验证（非本任务面）。
5. **回退方法**：`git revert f541b2f4`（单实现 commit，纯 `service.py`+测试；无 schema/数据迁移）。注：r1 返修后回退点顺延至返修 commit（同为纯 `service.py`+测试+文档，无 schema 变更）。
6. **规模化提示（DSH r1 R7，只登记）**：fan-out 后单页 unit 数 ≈ region 数 × 步数（TRANSLATE_ALL 17 region ≈ 136+ units/page），多页 chapter 选择触发 `ResourceLimits.max_step_runs=1000` 上限的概率显著上升（例如 20 页 × 17 region × 8 步 ≈ 2720 > 1000）。触发为 `RESOURCE_LIMIT_EXCEEDED` fail-closed（run 以 fatal_error 落 FAILED、剩余 cancel），非数据损坏——这是修复后「逐 region 跟进」的正确代价；若 BJ06 级别（17 region/页）多页批量成为常态，后续按需评估限额调高或批处理策略。

### 独立 Task 候选登记（DSH r1 R2，登记不修）

**建议标题**：primary region 重决策——SFX gate 对初始页级决策不可见（`region_ids[0]` 语义不一致）。

**缺陷本体**：`_backfill_detected_regions` 对 primary 只做 in-place 重绑（`src/application/tasks/service.py:964-971`），其 unit decision 仍是 detect 前 `region=None` 的**页级**决策；`_decide_step` 的 SFX gate 要求 `region is not None`（`src/application/tasks/service.py:418-423`），故 primary 永不经 `_sfx_gate_suppresses`；而恢复路径（`plan_run(mode="continue")`）以 live region 重规划并 gate 它——AC1 定义的「初始 vs 恢复语义不一致」在 primary 上原样存在。**既有缺陷、非本 Task 引入也非回归**（fan-out 之前该 region 同样被翻译；fan-out 只是让非 primary 的 gate 闭环与之形成同 run 内对比）。

**DSH 反例（可直接复现）**：将 `tests/core/test_sfx_policy_end_to_end.py` 的 scripted detector 两个 candidate 的 `reading_order` 对调（SFX region 成为 `region_ids[0]`=primary）并设 `policy=manual`——当前实现会给该 SFX region 落 `machine_translation`（production `handle_translate` 无 gate，`src/infrastructure/providers/handlers.py:382-465`）⇒ 违反 D06 §85，且与「非 primary 的 manual/skip SFX region 被 SKIP_POLICY 保持不翻译」在同一 run 内自相矛盾。

**为何不在本 Task 内修**：修复必然改变单 region 页行为（唯一 region=primary 时从「机器翻译」变为「gate 拦截」），与 Task「单 region 页零变化」纪律/AC 冲突，属产品语义取舍，须先裁决。

**裁决请求**：单 region SFX 页（页级命令）是否也对 primary 重决策（以 live region 快照重订其链上 decision）？
- 裁「是」⇒ 单 region SFX 页行为改变（D06 §85 更彻底闭环），需同步更新相关 e2e 期望与「零变化」口径；
- 裁「否」⇒ primary 语义不一致登记为已知限制（本节保留为事实源）。
请用户/集成方裁决后立独立 Task。
