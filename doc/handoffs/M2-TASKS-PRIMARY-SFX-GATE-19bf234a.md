---
task_id: M2-TASKS-PRIMARY-SFX-GATE
author: ZCode
recipient: Codex（Integrator）；DeepSeek Harness（非作者 Reviewer）
base_commit: 1c3ac590
delivery_head: 19bf234a
status: in_review
---

# Handoff：M2-TASKS-PRIMARY-SFX-GATE（primary region 纳入 SFX 门重决策）

## 交付结果

### 裁决落地说明（用户裁决 2026-10-02 ②，BACKFILL R2 关闭）

`_backfill_detected_regions`（`src/application/tasks/service.py`）不再对 primary（`region_ids[0]`）做 in-place 重绑：**每个检出 region——primary 包含在内——都由 `_plan_region` 对 live Region 快照规划 unit 链**（unit_id `{task_id}:{region_id}:{step_type}`，与恢复路径 `plan_run(mode="continue")`/`resume_blocked` 完全同形同决策过程）。初始执行与恢复的语义不一致在 primary 上就此消除；被替换的页级决策链整体退役，仅 detect unit 保留 plan 期 id（其终态由紧随的 commit 标记）。

**D06 §85 全域合规声明**：SFX gate 此前对 primary 不可见（`_decide_step` 仅在 `region is not None` 时经 `_sfx_gate_suppresses`），DSH r1 R2 反例——对调 reading_order 使 SFX region 成为 primary + `policy=manual`——会在同一 run 内机器翻译该 SFX region、却对同 run 内相同的 secondary SFX region 正确 SKIP_POLICY。本交付后 gate 的三值语义（`gate.py` 零改动）经 plan 层对**任何 reading_order 位置的 SFX region** 一致生效：manual/skip ⇒ SKIP_POLICY 及向 segment/mask_refine/inpaint/render 的传播；translate ⇒ 同 run 翻译。单 region SFX 页（唯一 region=primary）行为随之改变——这正是裁决目的（D06 §85 更彻底闭环）。

**单 region 非 SFX 页零变化（等价性）**：非 SFX region 的 live 重决策与原页级决策**逐步（step-for-step）decision/reason 全等**——gate 不触发（region_type ≠ sfx）、lock/stage/provider/forced 全同源。由两条测试钉住：`test_backfill_single_region_nonsfx_page_decisions_unchanged`（F2，REOCR_ALL）与 `test_single_region_nonsfx_redecision_equals_page_level_plan`（TRANSLATE_ALL 全链 8 步等价 + 9 unit 账目闭合）。

### 实现要点（单文件 `src/application/tasks/service.py`，net -37 行）

- `_backfill_detected_regions`：primary 与 `region_ids[1:]` 统一进同一 `_plan_region` 循环（DSH r1 R3 的 try/except `PipelineError` → TARGET_DELETED 跳过语义顺带覆盖 primary 读取窗口，原实现 primary 不可读会让 PipelineError 穿透 `execute_run` 滞留 RUNNING——本交付顺带消除该不对称）。
- 旧链替换：`stale_ids`（detect 之后 region_id is None 的 units）整体移除；`task.units = 未替换部分 + replanned`。index-based 执行循环（TASK-049）天然读取替换后的 units，无需调度层改动。
- 账目（BACKFILL R1 口径统一到 primary）：`planned_step_units += len(replanned) - len(stale_ids)`；`terminal_unit_ids` 先 `difference_update(stale_ids)` 再纳入 replanned 中 `decision.is_terminal` 的 unit；`terminal_step_units = len(terminal_unit_ids)`（与 `plan_run` 同式）。primary 链上 SKIP_POLICY 的 unit 与克隆链同口径计入终态——COMPLETED run 的 `overall_progress` 精确到 1.0（反例测试断言 `terminal==planned==17`）。
- 附带效果（登记）：「unit_id 内嵌 target 与真实 target 不一致」的展示层债务（BACKFILL handoff 风险 #4）就此消除——region 步骤 unit 全部为 region-id 形态，不再有两种形态并存。
- 零协议/schema/禁改面变更：`CommandType`、DB schema、store、`gate.py`、domain/infrastructure/ports/bootstrap/contracts/packaging/apps/STATUS 零 diff。

### AC 对照

- [x] **AC1 实现**：primary 与 `region_ids[1:]` 同路径 `_plan_region` 重决策；单 region 非 SFX 页决策零变化由等价性单测钉住（见上）。
- [x] **AC2 先红后绿**：红 **4 failed / 19 passed**（`red-1c3ac590-src-plus-tests.log`：DSH 反例 pipeline + e2e 对调 2 条新测试红在「primary translate decision RUN / machine_translation 落库」；R1/F1 适配断言红在 unit_id 页级形态）→ 绿目标文件 **23 passed**（`green-target-files.log`：18 既有 + 3 新增；其中 F2/等价性 2 条在旧 src 下即绿，正是「零变化」的平凡证明）→ 三套件 **630 passed + 1 skipped + 0 failed**（`green-three-suites.log`）。
- [x] **AC3 联动登记**：BACKFILL handoff「独立 Task 候选登记」节由本 Task 关闭——superseded-by 互指文字备置于下文「BACKFILL 登记节关闭」，供集成方搬运（BACKFILL handoff 文件在本 worktree 不可改）；测试适配登记见下文专节。
- [x] **AC4 文档**：本 handoff + Task 回填 + verification 五份日志；D06 §85 合规声明见上。

## 测试适配登记（AC3，按裁决新语义更新）

| 测试 | 适配内容 | 红态表现（旧 src） |
|---|---|---|
| `test_r1_backfill_replans_primary_chain_and_clones_secondary`（原 `test_r1_backfill_rebinds_target_id_and_preserves_unit_ids`） | R1 契约从「preserve unit_ids」改为「primary 重决策（region-id 形态）+ secondary 克隆」；detect unit plan 期 id 保留断言 | 红：primary unit_id 仍为 page 形态 |
| `test_multiregion_backfill_fans_out_to_every_detected_region`（F1） | unit_id 集合断言改为双 region-id 形态（primary 重决策 + 克隆） | 红：集合含 page 形态 id |
| `test_backfill_single_region_nonsfx_page_decisions_unchanged`（原 `test_backfill_single_region_page_unchanged`，F2） | 「byte-for-byte plan shape」改为「决策逐步等价 + 行为/账目零变化」——unit_id 形态变化是裁决的直接后果，不再属零变化口径 | 绿（决策等价在旧实现下平凡成立，恰为零变化证明） |
| 既有 BACKFILL 其余 16 条 + SFX e2e 原 2 条 | 零改动全过（多 region 页回归 + R1 断言 `terminal==planned==17` + e2e translate/manual 场景原语义保持） | 绿 |

新增 3 条：`test_sfx_primary_region_gated_by_manual_policy`（DSH 反例固化 + terminal 账目）、`test_single_region_nonsfx_redecision_equals_page_level_plan`（等价性护栏）、`test_manual_policy_gates_the_sfx_primary_region_end_to_end`（e2e 生产缝对调场景）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| 基线（本分支 base） | `QT_QPA_PLATFORM=offscreen PYTHONPATH=src <venv>/python -m pytest tests/core tests/pipeline tests/providers -q` | T1.1.1-impl-py312（py3.12.3，transformers 5.17.0+PySide6）@ 1c3ac590 | **627 passed + 1 skipped + 0 failed**。注：任务书/STATUS 的「575+1sk」文字快照早于 SETTINGS-IPC 批次集成（1c3ac590 已含其测试）；回退口径以本实测为准 | `verification/M2-TASKS-PRIMARY-SFX-GATE/baseline-1c3ac590-three-suites.log` |
| AC2 红 | 同环境 @ 1c3ac590 src + 本 tip tests | 同上 | **4 failed / 19 passed**（反例 pipeline：primary translate decision `RUN` ≠ 期望 `SKIP_POLICY`；e2e 对调：decision `run` ≠ `skip_policy`；R1/F1 适配断言） | `verification/M2-TASKS-PRIMARY-SFX-GATE/red-1c3ac590-src-plus-tests.log` |
| AC2 绿（目标文件） | `pytest tests/pipeline/test_regionless_rebinding.py tests/core/test_sfx_policy_end_to_end.py -q` @ 19bf234a | 同上 | **23 passed**（18+2 适配+3 新增） | `verification/M2-TASKS-PRIMARY-SFX-GATE/green-target-files.log` |
| AC2 绿（三套件） | `pytest tests/core tests/pipeline tests/providers -q` @ 19bf234a | 同上 | **630 passed + 1 skipped + 0 failed**（= 基线 627 + 新增 3，零回退） | `verification/M2-TASKS-PRIMARY-SFX-GATE/green-three-suites.log` |
| 溢出回归（PipelineService 消费方） | `pytest tests/workbench tests/m2_acceptance tests/editing -q` @ 19bf234a | 同上 | **188 passed 0 failed** | `verification/M2-TASKS-PRIMARY-SFX-GATE/green-overflow-suites.log` |
| 禁改面 | `git status --porcelain`；`git diff --check`；逐面核对 | @ 19bf234a | EXIT=0；改动=src/application/tasks/service.py + 2 测试文件 + verification/Task/handoff；domain/infrastructure/ports/bootstrap/contracts/packaging/apps/STATUS/gate.py 零 diff | 会话记录 |

未运行：其余套件（本任务纪律口径=三套件 + 消费方溢出检查，与 BACKFILL 同口径）。Mock 成功不表述为模型质量达标——本任务为规划语义修复，不涉及质量判断。

## 接收方式

- 分支 `agent/zcode/M2-TASKS-PRIMARY-SFX-GATE`，worktree `G:/CODEX/New Manga.worktrees/M2-TASKS-PRIMARY-SFX-GATE-zcode`，base=`1c3ac590`，delivery_head=`19bf234a`。
- 复现命令（红态）：`git checkout 1c3ac590 -- src/application/tasks/service.py && QT_QPA_PLATFORM=offscreen PYTHONPATH=src <venv>/python -m pytest tests/pipeline/test_regionless_rebinding.py tests/core/test_sfx_policy_end_to_end.py -q`（预期 4 failed）；绿态：`git checkout HEAD -- src/application/tasks/service.py` 后同命令（预期 23 passed）。
- 测试环境：`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`（主 venv，含 transformers/PySide6；e2e 需 offscreen）。
- Reviewer 检查建议：① `_backfill_detected_regions` 的替换语义——`stale_ids` 退出账目与 replanned `is_terminal` 进入账目的对称性（对照 `plan_run` 初始账目）；② 等价性：非 SFX region 重决策 vs 页级决策的同源性论证（gate 短路 / `_effective_lock` / stage_states / provider_binding / forced 五输入）；③ 反例红绿证据链（`red-1c3ac590-src-plus-tests.log` 中 primary decision `RUN` → 绿态 SKIP_POLICY + `sfx_step_types` 仅 ungated 步）；④ D06 §85 全域性——对调 reading_order 后 SFX primary 与 secondary 在同一 run 内行为一致。

## BACKFILL 登记节关闭（AC3；superseded-by 文字供集成方搬运）

M2-TASKS-BACKFILL-MULTIREGION handoff 的「独立 Task 候选登记（DSH r1 R2，登记不修）」节所登记的缺陷与裁决请求，已由本 Task 交付（用户裁决 2026-10-02 ②，delivery `19bf234a`）落地。集成时请将以下文字原样搬运至 BACKFILL handoff 该节末尾（BACKFILL handoff 在本 worktree 不可改）：

> superseded-by M2-TASKS-PRIMARY-SFX-GATE：本节登记的「primary region 重决策——SFX gate 对初始页级决策不可见」缺陷与裁决请求已由用户裁决 2026-10-02 ②（采纳重决策）落地——`_backfill_detected_regions` 现对每个检出 region（`region_ids[0]` 含在内）经 `_plan_region` live region 重决策，DSH 反例（SFX region 为 primary + policy=manual）规划 SKIP_POLICY 不再机器翻译（D06 §85 全域生效）；本节自此关闭，事实源移至 `doc/handoffs/M2-TASKS-PRIMARY-SFX-GATE-19bf234a.md`。注意「单 region SFX 页行为改变」为裁决明示后果，相关 e2e 期望已同步（SFX e2e 新增对调场景）。

集成时同步项（与 BACKFILL 集成时的 R6 搬运同机制）：STATUS 的 R2 裁决请求候选行、REBASELINE_PLAN 盘点表对应行由集成方按本 Task 终态更新（本 worktree 不改 STATUS/PLAN）。

## 下一任务建议（必填）

- Task ID / 标题：无需新建 Task——本 Task 待 DSH 非作者 Review → Codex 集成即闭环；M2-TA3-B2-KO-RERUN 的前置（「PRIMARY-SFX-GATE integrated — pipeline semantics finalized」）由本交付满足。
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者静态 Review，按任务书 frontmatter）；集成由编排会话代行 Codex。
- 推荐原因与前置依赖：本 handoff + delivery 19bf234a 已就绪；ko rerun（wave 2）依赖本 Task 集成后 pipeline 语义冻结。
- Recovery point：仓库 G:/CODEX/New Manga，branch `agent/zcode/M2-TASKS-PRIMARY-SFX-GATE`，base `1c3ac590`，head `19bf234a`（文档 commit 随后）。
- 允许修改路径：review 意见落 `src/application/tasks/service.py` / `tests/pipeline/**` / `tests/core/test_sfx_policy_end_to_end.py` / Task/handoff/verification。
- 禁止范围与新增授权条件：任务书禁改面不变（domain/infrastructure/ports/bootstrap/contracts/packaging/apps/STATUS/gate.py）；schema/命令协议变更仍需停等登记。
- 交付物：本 Task 全链（Task+handoff+verification+commit）。
- 验证命令、环境与完成 Gate：三套件 0 failed（命令见验证证据表）；红绿日志在 `verification/M2-TASKS-PRIMARY-SFX-GATE/`。
- 可直接转发给 Agent 的指令：见 STATUS 交接口径（本文件即为转发载体）。

## 风险与遗留

1. **单 region SFX 页行为改变（裁决明示后果，非回归）**：唯一 region=SFX 的页任务从「机器翻译」变为「gate 拦截（manual/skip）」。既有 BACKFILL/SFX-ENTRY 测试无一依赖旧行为（全部原样通过）；生产数据不受影响（无 schema/迁移）。
2. **color/term_extract 不属 gated 步（既有语义，如实登记）**：`_SFX_GATED_STEPS` 只含 translate/segment/mask_refine/inpaint/render；SFX region（primary 或 clone）的 color/term_extract 照常规划执行。本 Task 未改变该边界（反例测试按此口径断言 `sfx_step_types == {ocr, color, term_extract}`）。如需把 ungated 预处理也纳入门语义，属产品取舍，需另行登记裁决。
3. **primary 读取窗口 TARGET_DELETED 跳过（顺带修复，登记）**：原实现 primary 不可读时 PipelineError 穿透 `execute_run` 使 run 滞留 RUNNING；现与 `region_ids[1:]` 同语义跳过、由下一次（重）规划拾取。未新增独立测试（复用 BACKFILL R3 的既有防护路径，同分支同 except），如需独立红绿证据可另立 follow-up。
4. **回退方法**：`git revert 19bf234a`（单实现 commit，纯 `service.py`+测试+日志；无 schema/数据迁移）。回退即回到「primary 保留页级决策」的 1c3ac590 口径（含其已知 D06 §85 缺陷）。
5. **登记搬运依赖集成方**：BACKFILL handoff superseded-by 文字、STATUS/PLAN 行更新均需集成侧执行（本 worktree 不可改跨 Task 文件）；未搬运前 BACKFILL handoff 登记节与本 handoff 并存，以本 handoff 为最新事实源。
