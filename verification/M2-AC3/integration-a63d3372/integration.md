# M2-AC3 集成记录（integration of a63d3372）

- **Integrator**: Codex（代行，ZCode 子 agent 会话，用户授权 2026-09-28）；Owner=ZCode（另一会话），**Owner≠Integrator 保持**。
- **集成对象**: `agent/zcode/M2-AC3-provider-fail-closed` tip `a63d3372ebbd364da9fb5fb53af835559235bb6c`（交付 tip；Owner 3 commit：claim `c754e714` → 实现 `b0112834` → 交付 `a63d3372`）。
- **DSH r1 非作者静态 Review**: `approved_with_conditions`，0×P0（报告原字节归档：[doc/reviews/M2-AC3-a63d3372-dsh-r1.md](../../reviews/M2-AC3-a63d3372-dsh-r1.md)，SHA256 见文末）。报告尾部一段模型重复生成的残句（"gration_merge`，并在合并前…"）属 DSH 输出原貌，逐字节保留未修。
- **merge**: `cac374855b6e6a4310f557ae362d34d0572cd649`（--no-ff，parents=`3c210e3a`+`a63d3372`，无冲突；分叉点后 main 仅 `3c210e3a` governance commit，与 Owner 允许路径零重叠）。
- **拓扑口径说明**: release commit `7e88de4b` 即 main 与 Owner 分支的 merge-base（`git merge-base` 实测）。因此范围核验与 commit 计数以 `7e88de4b..a63d3372` 为交付区间口径；`319c5e4b..a63d3372` 会额外包含 `7e88de4b` 本身的 release 治理改动（`doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/M2-AC3.md`、`doc/tasks/M2-FIX-STUB-DECODER.md`、`doc/tasks/README.md`、`verification/M2-AC3/release-319c5e4b.md`），这些已在 main 上、不属 Owner 交付，merge 不重复带入。

## C1 — 冻结 tip 复跑两条 pytest（关闭 P1-1）

原始 Owner 日志（`verification/M2-AC3/raw/pytest-*.log`）HEAD 记录为 `c754e714`，系**工作区未提交状态运行**（实现 commit `b0112834` 尚未提交时执行）；集成方在冻结 tip `a63d3372` 复跑，以下列新日志为准：

| 命令（`G:/CODEX/New Manga.worktrees/M2-AC3-zcode`，`QT_QPA_PLATFORM=offscreen`，$py=TASK-012-py312） | 结果 | EXIT | 日志 |
|---|---|---|---|
| `$py -m pytest tests/m2_acceptance/test_provider_fail_closed.py -v` | **8 passed** in 5.80s | 0 | [raw/pytest-provider-fail-closed-tip-rerun.log](raw/pytest-provider-fail-closed-tip-rerun.log) |
| `$py -m pytest tests/m2_acceptance -q` | **23 passed** in 8.50s（既有 15 + 新增 8，零回归） | 0 | [raw/pytest-m2-acceptance-regression-tip-rerun.log](raw/pytest-m2-acceptance-regression-tip-rerun.log) |

每条日志头部含 shell、解释器版本（Python 3.12.3 / pytest 9.1.1）、完整 HEAD（`a63d3372ebbd364da9fb5fb53af835559235bb6c`）、时间戳。`doc/tasks/M2-AC3.md` 测试矩阵的 HEAD 声称已同步修正（标注集成方修正）。

## C2 — delivery_head hash 落地（关闭 P1-2）

- `doc/tasks/M2-AC3.md` frontmatter `delivery_head: null` → `a63d3372ebbd364da9fb5fb53af835559235bb6c`（集成方修正）。
- `doc/handoffs/M2-AC3-owner-delivery.md` Head ledger 行补 tip hash（标注「集成方补充」）。
- merge 以该 hash 为基线实测：merge parents = `3c210e3a` + `a63d3372`。

## C3 — 范围证明（关闭 P1-3）

命令（Owner worktree，tip=`a63d3372`）：

1. `git status --porcelain` → **空**（EXIT=0；无任何未跟踪/未提交残留，`.pytest_cache/`、`__pycache__` 均被 ignore）。
2. `git diff --name-status 7e88de4b..a63d3372`（交付区间）→ 恰 8 路径，全部在允许清单内：

| 状态 | 路径 | 允许依据 |
|---|---|---|
| A | `doc/handoffs/M2-AC3-owner-delivery.md` | 允许（handoff） |
| M | `doc/tasks/M2-AC3.md` | 允许（task 文件） |
| A | `tests/m2_acceptance/test_provider_fail_closed.py` | 允许（新增验收模块） |
| A | `verification/M2-AC3/discrimination-mutations.md` | 允许（verification/M2-AC3/**） |
| A | `verification/M2-AC3/raw/git-diff-check.log` | 允许（verification/M2-AC3/**） |
| A | `verification/M2-AC3/raw/pytest-m2-acceptance-regression.log` | 允许（verification/M2-AC3/**） |
| A | `verification/M2-AC3/raw/pytest-provider-fail-closed-v.log` | 允许（verification/M2-AC3/**） |
| A | `verification/M2-AC3/verification-results.md` | 允许（verification/M2-AC3/**） |

3. 禁改路径命中数：`git diff --name-only 7e88de4b..a63d3372 | grep -cE '^(src/|apps/|doc/contracts/)'` → **0**（产品代码零改动实证）。
4. `git diff --check 7e88de4b..a63d3372` → **EXIT=0**（无空白/冲突标记问题）。
5. 既有套件未改：`test_acceptance_loop.py`、`test_data_integrity.py` 不在 diff 命中清单中；回归 23 passed 实证行为未变。

日志：[raw/c3-scope-proof.log](raw/c3-scope-proof.log)（含 `319c5e4b..a63d3372` 与 `7e88de4b..a63d3372` 双口径记录及拓扑核验 [raw/owner-worktree-verify.log](raw/owner-worktree-verify.log)、[raw/topology-check.log](raw/topology-check.log)）。

## C4 — AC1 判定文字改逐场景事实（已修订）

`doc/tasks/M2-AC3.md` AC1 判定由「三场景均零 Region/零 candidate/零 revision/零新 managed 文件」改为逐场景事实（集成方修正）：

- 仅**零配置**场景（test_ac1_zero_config_detect_fails_closed_without_fabricated_regions，test:281-289）断言全套零半成品：零 Region、零 candidate、managed 清单不变。
- **无 binding** 与**悬空 binding** 场景（test:292-367）断言零新增 revision + current 指针不变 + 已存在 Region 不被改写（两场景的 Region 系故意先创建，"零 Region"在其语境下不是合法断言）。

## C5 — 两项集成裁决（代理裁决，用户可撤销）

以下裁决由 Lead（代行 Codex 主会话）2026-09-28 作出，本次集成按裁决落字；**标注：代理裁决，用户可撤销**；撤销后需开后续 slice 补强，不追溯本次 merge。

1. **AC5「失败 run 可被重试/恢复路径触达」（P2-2）：接受现有 AC5 措辞。** AC 原文「如 `recover_running_runs` 语义、剩余 units 可重试」为可选示例措辞；Owner 实测路径（重装配 + 新建同命令 run，`_plan_and_execute` → `create_run`）满足 AC 字面（重装配后状态持久可查询、修复后重试无重复无悬空）。`retry_failed_targets`（`src/application/tasks/service.py:903-919`）/ `recover_running_runs`（`service.py:886-901`）直达断言登记为**后续增强候选**，不阻断。
2. **AC2 注入手法（P2-3）：接受现有注入手法。** Task 风险节（`doc/tasks/M2-AC3.md` 风险条目）明确允许 Owner 自选注入手法（mock provider 抛错 vs 断网）；本模块证明的是「typed code 跨 seam 传递 + 既有成果零损坏」。transport→taxonomy 映射由既有单测承担：`tests/providers/test_remote_providers.py:132`（`(TransportTimeoutError, ProviderTimeout)`）与 `tests/network/test_retry_classification.py:19,51`——集成记录在此标注，DSH r1 已独立核对。

## 判别力边界披露（两条，源自 DSH r1 判别力意见）

1. **AC4 源不变断言为构造性不变式**：mtime/bytes 基线取在 `_import_page` 之后（test:538-541），import 读路径本身不在「全程」窗口内；威胁模型是流水线写源文件，故可接受，但「全程」字面强于证据。
2. **AC2 保护断言只覆盖失败路径**：既有成果保护断言围绕 transport 失败 run 展开；成功路径的既有成果共存由 AC3（A 页 COMPLETED 且 +1 revision）与 AC5（重试 revision `[1,2]` 连续）间接承重。

另按 DSH 判别力意见原文要点登记 M1/M2 覆盖边界：M1 只证 run 级聚合对 FAILED 敏感（task 行仍如实）；M2 模拟 step 级单点塌缩，生产真实塌缩路径（`service.py:793-795` `except Exception` → `_fail_step(..., "STEP_FAILED", ...)` 同时污染 task/step 两侧）由 test:409+test:413 双断言覆盖但未被 mutation 直接证明。DSH 建议的两类补强 mutation（task 级状态伪造、真实塌缩路径）留后续 slice。

## mutation M1/M2 集成方独立复放（关闭 P3-7）

全程 raw 日志：[raw/mutation-replay.log](raw/mutation-replay.log)（Owner worktree，tip=`a63d3372`，2026-09-28）。

| 步骤 | 命令/操作 | 结果 | EXIT |
|---|---|---|---|
| 基线 | `git status --porcelain src/` | 空 | 0 |
| M1 命中校验 | `grep -c 'elif PipelineTaskStatus.FAILED in statuses:'` | 1（唯一命中） | 0 |
| M1 应用 | sed：`elif FAILED` → `elif False and FAILED` | 替换成功（grep 复核=1） | 0 |
| M1 复跑 AC2 | `$py -m pytest …::test_ac2_network_failure_typed_and_existing_results_intact -q` | **红**：`test_provider_fail_closed.py:404`（run 报 COMPLETED 而非 COMPLETED_WITH_FAILURES） | 1 |
| M1 还原 | `git checkout -- src/application/tasks/service.py`；`git status --porcelain src/` | 空 | 0 |
| M2 命中校验 | python 精确块匹配（`_fail_step` 五行块，`service.py:713-717`） | `match count: 1`；`task.error_code = code` 保留确认 | 0 |
| M2 应用 | `step_run.error_code = code` → `step_run.error_code = "STEP_FAILED"` | diff --stat：1 file changed, 1 insertion(+), 1 deletion(-) | 0 |
| M2 复跑 AC2 | 同上 | **红**：`test_provider_fail_closed.py:413`（`'STEP_FAILED' != 'PROVIDER_TIMEOUT'`；task 级断言 test:409 通过，仅 step 级红） | 1 |
| M2 还原 | `git checkout -- …`；`git status --porcelain src/` | 空 | 0 |
| 零残留证明 | 基线复跑 `$py -m pytest tests/m2_acceptance/test_provider_fail_closed.py -q` | **8 passed** in 5.84s | 0 |

两 mutation 均按预期红、失败行号与 DSH r1 判别力意见完全一致（404/413），还原后零残留。P3-7 关闭。

**M2 替换点口径说明**:任务指令描述替换点为「五行块 `try:` 内赋值段（20 空格缩进）」，实际原文为 `_fail_step` 方法内 **8 空格缩进**赋值段（`src/application/tasks/service.py:713-717`，与 DSH 报告 §not_verified 第 3 组给出的 `:713-717` 一致；文件中另一处 `step_run.error_code = code` 位于 `:663`，属 `input_revision_changed`/`lock_changed` 分支，非 provider 失败路径，未被替换）。替换采用带上下文的精确块匹配（count==1 守卫），语义与指令意图（仅塌缩 step 级 code、保留 task 级）完全一致。

## P3-1..P3-8 处置表

| 项 | 内容（DSH r1） | 处置 |
|---|---|---|
| P3-1 | 场景厚度不均（AC1#3/AC3 缺 managed/candidate 断言） | deferred（后续 slice 可补强，不阻断） |
| P3-2 | AC4「全程」窗口基线在 import 之后 | deferred（威胁模型可接受；见上文判别力边界 1） |
| P3-3 | `_fail_step` helper 自述强于断言；缺 `task.error_code == step.error_code` 交叉断言 | deferred（后续 slice 一行增强） |
| P3-4 | test:330 空串比空串弱等值断言 | deferred（显式 `== ""` 更硬，后续 slice） |
| P3-5 | 未覆盖 binding alias 投影 | deferred（Handoff #2 已如实披露，不构成 AC 缺口） |
| P3-6 | STATUS/REBASELINE_PLAN 漂移 | **本次已处置**：`doc/REBASELINE_PLAN.md` M2-AC3 行由集成方同步为 done；`doc/STATUS.md` 留主会话收口（按集成指令分工） |
| P3-7 | mutation 记录无 raw 日志/EXIT | **本次已补**：集成方独立复放 raw 日志入 [raw/mutation-replay.log](raw/mutation-replay.log)（含两红、还原零残留、基线复跑 8 passed） |
| P3-8 | Qt/WebView2 读面 NOT_RUN 成立 | deferred（与 M2-AC2 同因同处置，登记后续 E2E slice） |

## SHA256

| 文件 | SHA256 |
|---|---|
| `doc/reviews/M2-AC3-a63d3372-dsh-r1.md` | `5f5fc29c09a7d700aed9d410aa8822e72e173ee4f3f4c5d2a4319c5bf829ba09` |
| 原始来源 `/tmp/m2ac3-review/dsh-r1-result.md` | `5f5fc29c09a7d700aed9d410aa8822e72e173ee4f3f4c5d2a4319c5bf829ba09`（`cmp` 逐字节一致） |

## 集成后复跑（集成 head）

`G:/CODEX/New Manga`（merge 之上、集成修正 commit 后）：`$py -m pytest tests/m2_acceptance -q` → **23 passed**，EXIT=0；日志 [raw/pytest-m2-acceptance-postmerge.log](raw/pytest-m2-acceptance-postmerge.log)。

## 结论

M2-AC3 以 Owner tip `a63d3372` 进入 main（merge=`cac37485`）。C1-C5 全部关闭；P3-6/P3-7 本次补齐，P3-1..P3-5/P3-8 deferred。Task 置 `done`。
