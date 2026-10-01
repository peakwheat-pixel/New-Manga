# DIAG-M2-REGIONLESS-LOCK-CHANGED-001 — Owner 执行结果（**BLOCKED：无执行与写入通道**）

## 0. 结论先行

**本 Task 无法按 AC 交付可执行证据。** 沙箱在命令执行前的准备阶段即失败（`SetNamedSecurityInfoW failed (Win32 5)`），且 worktree 位于 session workspace `G:\CODEX\New Manga` 之外，写入被 workspace-write 拒绝、升级审批无可用通道。因此：**AC1/AC2/AC5 = `BLOCKED`；AC3/AC4 = 仅静态分析（`STATIC`，非执行证据）**。

按降级规则，我把全部交付物全文（诊断报告、可独立运行的复现脚本、Handoff、命令与原始错误记录）放在本回答中，由集成方代为落盘与 import 提交。**凡未经实际执行得到的结论，下文一律标注「静态分析」。**

我并未因此放弃产出：借助 DSH 文件工具（`read`/`grep`/`glob`，对 workspace 外路径可读），我在**冻结 base `5789b30b` 的 worktree 源码上**完成了完整的静态根因定位，证据链闭合、可被后续执行一次性验证。

---

## 1. 环境事实与原始错误（逐条原样记录）

| # | 操作 | 目标 | 原始结果 |
|---|---|---|---|
| E1 | `pwsh -Command 'Write-Output ok2'` | workdir=`G:/CODEX/New Manga` | `Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`（命令未执行，无 stdout/stderr/exit code） |
| E2 | `pwsh` 同上 | workdir=worktree | 同上，逐字节相同错误 |
| E3 | `pwsh` 同上 | workdir=`$env:TEMP` | 同上 |
| E4 | `pwsh` 探针（`Directory::Exists`） | — | 同上 |
| E5 | `write` 探针 `...worktree\verification\DIAG-.../.probe` | worktree | `[sandbox: file access denied under workspace-write mode]` + 「escalation available … the approval prompt asks the user」 |
| E6 | `pwsh` 重试并带 `sandbox_permissions: danger-full-access` + justification | — | `Error: sandbox escalation to "danger-full-access" requires approval, but no approval channel is available` |
| E7 | subagent 独立探针（两个命令，无 workdir / workdir=worktree） | — | 同一 E1 错误，两次完全一致；未取得 `SHELL_OK`、PS 版本、`git HEAD`、`GIT_OK` 中任何一项 |

**判定：** 这是环境/权限缺陷（沙箱无法为 workspace 根授予写 ACL），不是某条命令的策略拒绝，也不是模型侧可绕过的限制。子代理继承同一沙箱，故委派亦不可行。

**可用通道（已实证）：** `read` / `grep` / `glob` 可在 workspace **之外**读取 worktree 文件（E8–E11：`read` 成功读到 worktree 的 `AGENTS.md`、`.git`、`doc/tasks` 目录；`grep` 成功命中 worktree 源码）。因此我能读源码，但不能执行、不能写。

**冻结态证据（文件级，非 `git rev-parse`，已标注）：**

- `G:\CODEX\New Manga\.git\refs\heads\agent\deepseek\DIAG-M2-REGIONLESS-LOCK-CHANGED-001` = `5789b30b37dfbf79d9bca707b5fdaaa562ada707` → worktree 分支确实固定在任务声明的 base。
- `.git/worktrees/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-dsh/HEAD` = `ref: refs/heads/agent/deepseek/DIAG-M2-REGIONLESS-LOCK-CHANGED-001`（linked worktree 注册正确）。
- 主仓库 `main` = `acddebcb265c2a4dacd253b9d05a781bdca1c107`（已越过 base；`doc/tasks/DIAG-...md` 与 `verification/DIAG-.../release-5789b30b.md` 只存在于 main，**在 base 5789b30b 的 worktree 中不存在**——这是我读任务文件时读的 main 版本。后续 Owner 若严格按 base 执行，会拿不到任务文件；建议 Codex 确认这是有意的「release 文档后置提交」还是 worktree base 选择偏差）。

---

## 2. 验证命令执行记录（AC5）

所有命令均在 worktree 根目录 `G:/CODEX/New Manga.worktrees/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-dsh` 语义下尝试。

| 命令 | shell | 解释器 | 固定 HEAD | EXIT | 结果 |
|---|---|---|---|---|---|
| `& $py verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/reproduce.py` | pwsh (DSH harness) | — | 未取得 | 无 | **NOT_RUN**（E1 沙箱准备阶段失败；脚本亦无法写入 worktree，E5） |
| `& $py -m pytest tests/providers/test_detect_handler.py tests/providers/test_bootstrap_providers.py -q` | pwsh | — | 未取得 | 无 | **NOT_RUN**（同上） |
| `git diff --check 5789b30b..<delivery-head>` | pwsh | — | 无 delivery head | 无 | **NOT_RUN**（无提交、无 shell） |

`$py` = `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`（**未执行、未验证版本**；任务书声明 3.12.3，我无法复验）。

**FAIL / BLOCKED / NOT_RUN 分离：**
- `FAIL`：无。没有任何命令真正执行到失败。
- `BLOCKED`：AC1 可执行复现、AC2 运行时状态链、AC5 命令证据与交付提交。
- `NOT_RUN`：上表三条验证命令。
- `STATIC`：AC3、AC4，以及 AC2 的「比较点」定位（静态推导，非运行观测）。

---

## 3. AC 状态表

| AC | 要求 | 状态 | 依据 |
|---|---|---|---|
| AC1 | 稳定复现 + 可独立运行脚本 + 先红日志 | **BLOCKED** | 脚本已写就（§6.2 全文），**未落盘、未执行**，无先红日志。原因 E1/E5/E6 |
| AC2 | 记录 detect 前后 PlanUnit/StepRun/catalog/final error | **BLOCKED**（运行时）/ **STATIC**（比较点） | 运行时状态链未采集；比较点已在 §4 用源码行级证据闭合 |
| AC3 | 反事实：正确 snapshot/rebind 位置、多 Region fan-out、终态计数、重启恢复 | **STATIC** | §5（未执行验证，标注为静态分析） |
| AC4 | 最小修复路径、共享 seam、回归/负向矩阵、持久化恢复风险 | **STATIC** | §5.4–5.5（修复须另立 Task，本 Task 未实施任何修改） |
| AC5 | 命令含 shell/解释器/HEAD/EXIT、FAIL/BLOCKED/NOT_RUN 分离、Handoff + delivery head | **BLOCKED** | §1–2 已如实记录；**无 delivery head**（无法 git commit）；Handoff 全文见 §6.3 由集成方落盘 |

---

## 4. 静态根因分析（AC2 的比较点，行级证据）

**根因一句话：** `_backfill_detected_regions` 在 detect 之后只重绑了 `PlanUnit.region_id`，**没有重绑 `target_id`**；于是 `ocr` 的 `StepRun.input_refs` 仍取自 **Page** target（无 `"region"` 键 ⇒ `None`），而真正被写的是 **Region**，`RegionStepWriter` 的乐观守卫拿 `None` 去比对 Region 的真实 current revision（detect 已通过 `create_region` 原子写入首版），必然不等 ⇒ 抛 `LockBlocked(error_code="LOCK_CHANGED")`。

### 4.1 证据链（worktree @ 5789b30b，`path:line`）

1. **plan 时（regionless 分支）** `src/application/tasks/service.py:329-336`：`target.regions` 为空 ⇒ `_plan_region(..., region=None)`。
2. `service.py:346-358`：`region is None and "ocr" in steps` ⇒ `steps = ("detect", *steps)`。
3. `service.py:360-365`：`target_id = region.region_id if region else target.page_id` ⇒ **全部 unit 的 `target_id = page_id`**；`lock = target.lock`（Page 锁）。
4. `service.py:384-395`：`PlanUnit(unit_id=f"{task}:{target_id}:{step}"`, target_id=page_id, region_id=None, expected_revisions=page revisions, expected_lock=page lock)`。
   （注：`PlanUnit.expected_*` 仅被持久化审计，`grep` 全仓确认**从未**用于提交守卫——守卫只用 `StepRun`。）
5. **detect 提交** `service.py:647-657`：`outcome.status == "applied"` ⇒ `if unit.step_type == "detect": self._backfill_detected_regions(task, unit, result)`。
6. **backfill 本体** `service.py:921-946`（关键）：
   ```python
   task.units = tuple(
       (replace(item, region_id=primary) if item.unit_id != unit.unit_id and item.region_id is None else item)
       for item in task.units
   )
   ```
   **只有 `region_id=primary`，没有 `target_id=primary`**（`grep 'target_id='` 全文件确认：除 plan 与 `_record_step_attempt`/`commit` 的读取外，无第二处写 `target_id`）。
7. **ocr 记录 attempt** `service.py:605-618`：`current = self._catalog.current(unit.target_id)` — `target_id` 仍是 `page_id`。
   `src/infrastructure/sqlite/pipeline.py:562-566`：`current()` 先查 `regions WHERE region_id = target_id`，查不到走 `_page_or_error`。
   `pipeline.py:733-738` `_page_revisions()`：Page 的 `current_revisions` = `{artifact_type: current_revision_id}`（`mask`/`clean`/… **绝无 `"region"` 键**；新页面为 `{}`）。
   对比 `pipeline.py:701-725` `_region_from_id()`：Region 的 `current_revisions = {"region": row["current_revision_id"]}`，`lock` = Region 锁。
8. **OCR handler** `src/infrastructure/providers/handlers.py:341-350`：`expected_current_revision_id=step_run.input_refs.get("region")` ⇒ **`None`**。
   （`handlers.py:326-333` 先跑 provider 链——这解释了为什么既有测试 `tests/providers/test_detect_handler.py:212-286` 只观察到 `PROVIDER_NOT_CONFIGURED`：未接 OCR provider 时根本走不到守卫；一旦 OCR 真的成功，才暴露本缺陷。）
9. **失败比较点** `src/infrastructure/providers/step_writes.py:206-231`：
   ```python
   self.conn.execute("BEGIN IMMEDIATE")
   row = ...SELECT current_revision_id FROM regions WHERE region_id = ?...
   if (not isinstance(expected_current_revision_id, _Unchecked)
       and row["current_revision_id"] != expected_current_revision_id):
       raise LockBlocked("region current revision changed during the step"
                         f" (expected {expected_current_revision_id!r}, found {row['current_revision_id']!r})",
                         provider_id=provider_id, stage="region-write")
   ```
   `src/ports/providers/errors.py:152-155`：`class LockBlocked(ProviderError): error_code = "LOCK_CHANGED"`。
   **这就是最终 `LOCK_CHANGED` 的来源**（不是 catalog 的 `commit_step` 锁分支，见 §4.2）。事务语义 OK：`step_writes.py:278-280` `except Exception: rollback(); raise`，不泄漏事务（我核对了，避免了一条假线索）。
10. **锚定 `current_revision_id` 非空** `src/application/editing/service.py:247-274` `create_region()`：`add_region()` + `_commit_user_or_raise(...)`「first revision + pointer in one atomic commit」⇒ Region 的 `current_revision_id` 由 detect 创建时即被赋值。
11. **错误码穿越 seam** `handlers.py:194-217` `_typed()`：`except ProviderError as error: raise StepExecutionError(error.error_code, detail)` ⇒ `Service.execute_run` `service.py:790-792` `except StepExecutionError: _fail_step(..., error.code, error.detail)` ⇒ `step_run.error_code = "LOCK_CHANGED"`。
12. **终态** `service.py:801-803, 820-823, 966-981`：task FAILED ⇒ `_aggregate_run` ⇒ `COMPLETED_WITH_FAILURES`。

### 4.2 排除的竞争假设（负向证据）

- **不是 catalog `commit_step` 的 `lock_changed`**：`src/application/tasks/store.py:182-183` / `pipeline.py:583-585` 的比较对象是 `current(target_id).lock != expected_lock`，二者同源于 Page 快照，恒等；且 handler 在提交前已抛错，`commit_step` 根本不会被调用。
- **不是 `input_revision_changed`**：Page 快照 `expected_revisions` 与 Page 现状一致（`store.py:180-181`）。
- **不是 Region 锁置位**：`step_run.lock_snapshot` 来自 Page（`page_locked=False`），Region 三锁全 False；`prepare_ocr_text` 的 `staged.region_locked` 检查（`step_writes.py:118-121`）不触发。
- **不是 `INVALID_INPUT requires a Region target`**：`_backfill_detected_regions` 补上了 `region_id`，`handlers.py:962-969` `_require_region(unit)` 通过。
- **不是 PlanUnit 陈旧快照**：守卫只读 `StepRun.input_refs/lock_snapshot`（`service.py:640-646`）。

### 4.3 `reproduce.py` 的**先红**判别性预测（供执行者核对，未执行）

- `executed.step_runs[1].step_type == "ocr"`，`status == FAILED`，`error_code == "LOCK_CHANGED"`；
- `error_detail` 含 `expected None`（原文形如 `region current revision changed during the step (expected None, found '<rev>') (provider=fake-ocr) (stage=region-write)`）；
- `ocr_step.target_id == "page-1"` 且 `ocr_step.region_id == <region>`（冒烟证据）；
- `"region" not in ocr_step.input_refs`；
- `executed.status == COMPLETED_WITH_FAILURES`；
- **Region 只应有 1 条 `region_revisions`**（detect 的首版），证明 OCR 未落任何写。

若上述任一条不成立，说明静态结论有误或缺陷已被修复——脚本以 exit 1 明确区分。

---

## 5. AC3 / AC4 静态分析

### 5.1 正确 snapshot/rebind 应发生的位置（反事实）

不变式应为 **`PlanUnit.target_id` ≡ 该步骤的写目标**（Region 步骤 ⇒ Region id；Page 步骤 ⇒ Page id），`StepRun.input_refs/lock_snapshot` 在 `_record_step_attempt` 时由它派生。

- **唯一最小修复点：`src/application/tasks/service.py:_backfill_detected_regions`（L921-946）**，在 detect 提交成功、`_record_step_attempt(ocr)` **之前**，把「仍 regionless 的后续 unit」同时重绑 `region_id=primary` **和** `target_id=primary`。
  - 时序正确性：`commit_step_result` L650-657 先 backfill，再 `_mark_terminal`；`execute_run` 的 index-based 循环 L760-763 使替换对后续 unit 可见（注释 L755-759 已声明该意图）——**这正是 TASK-049 实现时漏掉的一半**。
  - **不要改 `unit_id`**：`unit_id` 是 `run.terminal_unit_ids` 的键（`service.py:724-727`），plan 阶段已把 `SKIP_*` unit 标记为终态（L305-311）；改 id 会丢终态或双计。同时 `unit_id` 里内嵌的 page id 会与真实 target 不一致——这是修复需显式决策的显示/审计问题（见 §5.4 R2）。
- **只改 snapshot 来源（如让 `_record_step_attempt` 用 `unit.region_id or unit.target_id`）是不够的**：`commit_step_result` L635-638 的 mapping 校验与 L640-646 的 `commit_step(target_id=unit.target_id)` 仍走 Page 分支；`pipeline.py:601-610` 会执行 `UPDATE media_artifacts ... artifact_type='region'` ⇒ `rowcount != 1` ⇒ `target_not_found` ⇒ 服务层映射为 **`TARGET_NOT_FOUND`**（`service.py:684-685`）。**即：半修会把 `LOCK_CHANGED` 变成 `TARGET_NOT_FOUND`**——这是 AC4 必须写清的判别点，也是负向测试 N1 的价值。
- **PlanUnit.expected_lock/expected_revisions 不需要同步刷新**（守卫不用它们），但若同批修复触及审计口径，应保持一致（否则持久化后的 plan 审计与真实写入目标不符）。

### 5.2 多 Region fan-out（不得用单 Region 特例掩盖）

- 现状：`_backfill_detected_regions` 只取 `region_ids[0]`，docstring L925-931 明确「fanning a page task out over every detected Region is a later scheduling slice」，`outputs["region_ids"]` 保留全量供审计。
- **修复必须保持该语义**：多 Region 页面上，只有 primary Region 会跑 ocr/translate/segment/inpaint，其余 Region 停在 `NOT_STARTED`。若顺带在 backfill 里为每个 Region 生成新 unit，会改变 `planned_step_units`、`run.tasks[].units` 持久化形状与进度分母，属于**范围外的调度变更**，不应混进本修复。
- 但必须补一条**显式的语义测试**：多候选页面（2+）跑完后，断言「primary 走到 ocr 完成、非 primary 无 stage 状态、`region_ids` 全量可审计」，避免后续实现者把 fan-out 当 bug「顺手修掉」。

### 5.3 终态计数与重启恢复

- **终态计数**：`planned_step_units` = plan 时 unit 数（L309），`terminal_step_units` 由 `_mark_terminal` 按 `unit_id` 去重累加（L723-727）。LOCK_CHANGED 时 `_fail_step` 已把失败 unit 标终态（L719），`_cancel_remaining`（L948-958）把其后的 RUN unit 全部标终态 ⇒ 进度会到 1.0 而 run 为 COMPLETED_WITH_FAILURES（既有语义，非本缺陷引入）。
- **重启/恢复路径会「自愈」，从而掩盖缺陷**（关键 AC3 发现）：
  - `plan_run(mode="continue")`：`service.py:288-293` 对 `resume_blocked/continue` 使用 **`self._catalog.current(run_target.target_id)`**（Page id）重新取视图。此时 Page 已有 Region ⇒ `_plan_target` L328-335 走 `region_views` 分支 ⇒ **每个 Region 各自得到 `target_id=region_id` 的链**，`input_refs={"region": rev}` ⇒ 守卫通过、**不再 LOCK_CHANGED**。
  - 同理 `retry_failed_targets`（L903-919）新建 run，`create_run` 在展开时快照已有 Region ⇒ 重试即成功。
  - **用户可见症状因此是：全新 regionless 页面首次运行在 ocr 处 `LOCK_CHANGED` 失败，重试/重启后成功**；且「重规划后按 Region fan-out」与「同一次运行只绑 primary」两种语义共存于同一代码。修复与测试必须同时固定这两条路径，否则负向测试会假绿。
- **崩溃窗口**：detect 提交与 backfill 之间崩溃时，持久化的 unit 仍是 page-scoped（`_unit_dict` L176-188 存 `target_id`/`region_id`）；`recover_running_runs`（L886-901）把 run 置 INTERRUPTED，`continue` 走 5.3 的重规划路径，`run.step_runs` 在 `continue` 下**不被清空**（L312）而 `terminal_unit_ids` 被**整体重置**（L310-311）——这是与本缺陷相邻的既有恢复语义风险，修复 Task 应至少加一条 resume 用例覆盖。

### 5.4 AC4 最小修复路径（建议，未实施）

- **范围**：`src/application/tasks/service.py` 单文件、`_backfill_detected_regions` 单函数（+ 必要时 docstring）。不触碰契约、schema、providers/handlers、catalog。
- **共享 seam**：`PipelineService._record_step_attempt → StepRun.input_refs/lock_snapshot` 与 `_backfill_detected_regions` 的「target 权威」约定；以及 `PlanUnit.target_id == 写目标` 这一隐含不变式——建议在修复 Task 中把它写成显式注释/断言（`commit_step_result` 前 `assert unit.region_id is None or unit.target_id == unit.region_id`）。
- **回归矩阵（正）**：
  - R0：regionless page + `REOCR_ALL`(page scope) + 可用 detector + 可用 OCR ⇒ run `COMPLETED`，ocr `target_id == region_id`，`region_revisions == 2`（首版 + ocr），`regions.current_revision_id` 前进 1；
  - R1：backfill 后 unit 快照 `target_id == region_id == primary`，其余 unit 的 `unit_id` 不变（断言稳定性）；
  - R2：多候选页面 ⇒ 仅 primary 有 stage 记录，非 primary `NOT_STARTED`，`terminal_step_units == planned_step_units`，run `COMPLETED`；
  - R3：`TRANSLATE_ALL`(page scope, regionless) 全链走到下一个真实能力缺口而非 `LOCK_CHANGED`；
  - R4：既有 `tests/providers/test_detect_handler.py`（6 例，含 reuse-existing-regions、no-candidates `INVALID_INPUT`、无 detector `PROVIDER_NOT_CONFIGURED`）全部保持绿；
  - R5：同页面第二次运行（region-scoped plan）不产生重复 Region / 重复首版。
- **负向矩阵（负）**：
  - N1：只改 snapshot 来源（或手工把 `input_refs["region"]` 设为错误值）⇒ 必须仍是 **锁定守卫语义**（`LOCK_CHANGED` 且**零写**），不得静默改写；同时验证「半修 ⇒ `TARGET_NOT_FOUND`」这一判别（§5.1）；
  - N2：`region_locked=1` 置于 detect 与 ocr 之间 ⇒ `LOCK_CHANGED`，text/`region_revisions` 不变；
  - N3：detector 零候选 ⇒ detect `INVALID_INPUT`，ocr 不运行，无 Region（对齐 `test_detect_handler.py:327-344`）；
  - N4：无 OCR provider ⇒ ocr `PROVIDER_NOT_CONFIGURED`（现测已覆盖，防回归）；
  - N5：`page_locked` ⇒ plan `SKIP_LOCK`，无 StepRun；
  - N6：primary Region 在 detect 与 ocr 之间被软删 ⇒ 硬失败且带类型化错误码，**不得**回退到其它 Region；
  - N7：detect 后中断 + `continue` ⇒ 无 `LOCK_CHANGED`、无重复 Region、`step_runs` 累积与 `terminal_unit_ids` 重置行为被断言固定。
- **持久化/恢复风险**：
  - R-a：修复后持久化 unit 会携带 region-scoped `target_id`；`SqlitePipelineStore` 的 `_unit_dict/_unit`（`pipeline.py:176-203`）已能往返，但需断言 resume 后形状不变；
  - R-b：`plan_run` 三条 mode 的 target 视图来源不同（`run_target.snapshot` vs `catalog.current`），修复后的不变式必须对三者都成立；
  - R-c：`unit_id` 内嵌旧 page id 与真实 target 不一致的审计歧义（§5.4 开头），建议在修复 Task 中明确「保留 id 稳定性优先」并记录为已知展示层债务。

---

## 6. 交付物全文（供集成方落盘）

> 落盘路径与提交可由 Codex/Antigravity 执行；`delivery head` 由落盘者固定后填写。**本回答中的脚本与文档未被我执行验证。**

### 6.1 `doc/research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md`

````markdown
---
id: DIAG-M2-REGIONLESS-LOCK-CHANGED-001
kind: research
status: blocked
owner: DeepSeek Harness
base_commit: 5789b30b37dfbf79d9bca707b5fdaaa562ada707
worktree: G:/CODEX/New Manga.worktrees/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-dsh
branch: agent/deepseek/DIAG-M2-REGIONLESS-LOCK-CHANGED-001
execution_state: BLOCKED_NO_SANDBOX_EXECUTION
evidence_class: STATIC_ONLY (no command executed)
---

# M2 regionless planner `LOCK_CHANGED` 诊断（静态）

## 0. 执行状态声明

本次 Owner 会话**未能执行任何命令**：DSH 沙箱在命令执行前准备阶段失败
（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)`，多次、含
子代理独立复现），worktree 写入被 `workspace-write` 拒绝，升级审批无可用通道。
因此 AC1/AC2/AC5 = BLOCKED，AC3/AC4 与 AC2 的比较点定位 = **静态分析（STATIC）**。
所有结论均可由 §4 的行级证据与 `verification/.../reproduce.py` 一次性证伪或证实。

## 1. 结论

regionless page 走 `detect → backfill → ocr` 时，`_backfill_detected_regions`
只重绑 `PlanUnit.region_id`，**未重绑 `target_id`**；`ocr` 的
`StepRun.input_refs` 因而仍冻结自 **Page** target（无 `"region"` 键 ⇒ `None`），
而实际写目标是 **Region**，`RegionStepWriter._persist` 的乐观守卫以 `None` 比对
Region 真实 current revision（detect 已原子写入首版）⇒ `LockBlocked`
(`error_code="LOCK_CHANGED"`)。

**失败比较点**：`src/infrastructure/providers/step_writes.py:219-231`，
不是 `catalog.commit_step` 的锁分支（后者同源比较，恒等）。

## 2. 证据链（worktree @ 5789b30b）

| # | 位置 | 事实 |
|---|---|---|
| 1 | `src/application/tasks/service.py:329-336` | 页面无 Region ⇒ `_plan_region(..., region=None)` |
| 2 | `service.py:346-358` | 计划链前插 `detect` ⇒ `("detect","ocr",...)` |
| 3 | `service.py:360-365` | `target_id = target.page_id`（regionless） |
| 4 | `service.py:384-395` | `PlanUnit(target_id=page_id, region_id=None, expected_lock=page lock)`；`expected_*` 经 grep 确认仅审计、从不用于守卫 |
| 5 | `service.py:650-655` | detect 提交成功后才调用 `_backfill_detected_regions` |
| 6 | `service.py:921-946` | **只 `replace(item, region_id=primary)`**；全文件 grep 证明 `target_id` 无第二处写入 |
| 7 | `service.py:605-618` | `input_refs`/`lock_snapshot` 取自 `catalog.current(unit.target_id)` = Page |
| 8 | `src/infrastructure/sqlite/pipeline.py:562-566, 733-738` | Page `current_revisions` = `{artifact_type: rev}`，**无 `"region"` 键** |
| 9 | `pipeline.py:701-725` | Region `current_revisions` = `{"region": rev}` |
| 10 | `src/infrastructure/providers/handlers.py:341-350` | `expected_current_revision_id=step_run.input_refs.get("region")` ⇒ `None` |
| 11 | `step_writes.py:206-231` + `:278-280` | `BEGIN IMMEDIATE` 内比对 ⇒ `LockBlocked`（rollback 正确，无事务泄漏） |
| 12 | `src/ports/providers/errors.py:152-155` | `LockBlocked.error_code == "LOCK_CHANGED"` |
| 13 | `src/application/editing/service.py:247-274` | `create_region` 原子写首版 ⇒ `current_revision_id` 非空 |
| 14 | `handlers.py:194-217` → `service.py:790-792` | 错误码穿越 seam 保留 |
| 15 | `service.py:966-981` | 终态 `COMPLETED_WITH_FAILURES` |

## 3. 先红判别性预测（`reproduce.py` 会断言；本会话 NOT_RUN）

- ocr `StepRun`: `status=FAILED`, `error_code=LOCK_CHANGED`, `error_detail` 含 `expected None`；
- ocr `target_id == page_id` 且 `region_id == <region>`；`"region" not in input_refs`；
- run `COMPLETED_WITH_FAILURES`；Region `region_revisions` 恰 1 条（零写）。

## 4. 反事实（AC3）

- 正确不变式：`PlanUnit.target_id ≡ 写目标`；应在 `_backfill_detected_regions`
  （detect 提交后、`_record_step_attempt(ocr)` 前）同时重绑 `target_id=primary` 与
  `region_id=primary`，且**不改 `unit_id`**（`terminal_unit_ids` 以它为键）。
- 半修（只改 snapshot 来源）会把 `LOCK_CHANGED` 变成 `TARGET_NOT_FOUND`
  （`commit_step_result` 仍以 Page 为 `target_id` ⇒ `pipeline.py:601-610` rowcount 0）。
- 多 Region fan-out：现状只绑 `region_ids[0]`，其余 Region 停 `NOT_STARTED`；
  修复须保持该语义（fan-out 属调度切片，不得混入）。
- 重启/恢复会自愈：`plan_run(mode="continue")`/`retry_failed_targets` 走
  `catalog.current` 重规划 ⇒ 已有 Region 时按 Region fan-out ⇒ 不再触发。
  **用户症状 = 首次运行失败、重试成功**；修复必须同时固定两条路径。
- 终态计数：`_fail_step`+`_cancel_remaining` 会把进度推到 1.0 而 run 为
  `COMPLETED_WITH_FAILURES`（既有语义）。崩溃窗口内 `continue` 会重置
  `terminal_unit_ids` 但保留 `step_runs`（`service.py:310-312`）——相邻既有风险。

## 5. 修复建议（AC4，须另立 Task，本 Task 未实施）

最小修复 = `service.py:_backfill_detected_regions` 单函数；共享 seam =
`_record_step_attempt` 的 target 权威约定 + `PlanUnit.target_id == 写目标` 不变式。
回归 R0–R5、负向 N1–N7、持久化风险 R-a–R-c 见 Handoff §矩阵。

## 6. 未覆盖 / 未验证

- 全部运行时证据（命令、日志、pytest、git）未执行；
- `$py` 版本未复验；`git diff --check` 未运行；
- 本报告不含任何已执行的运行观测，除文件级 git 元数据读取外无运行事实。
````

### 6.2 `verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/reproduce.py`

````python
# -*- coding: utf-8 -*-
"""DIAG-M2-REGIONLESS-LOCK-CHANGED-001 / AC1 reproducer.

READ-ONLY with respect to the repository: it writes only into a temporary
directory (SQLite + managed storage).  It does not import or modify tests/**.

Predicted defect (static analysis of base 5789b30b):
    A page-scoped command on a *regionless* page plans ``detect`` first.  After
    detect commits, ``PipelineService._backfill_detected_regions`` rebinds the
    remaining units' ``region_id`` to the first detected Region but leaves
    ``target_id`` on the Page.  The ``ocr`` StepRun therefore snapshots the Page
    target (``input_refs`` has no ``"region"`` key -> ``None``) while the handler
    writes Region text; ``RegionStepWriter._persist`` compares that ``None``
    against the Region's real current revision (written atomically by
    ``RegionEditingService.create_region`` during detect) and raises
    ``LockBlocked`` -- ``error_code == "LOCK_CHANGED"``.

Exit codes:
    0  the predicted defect reproduced (diagnostic RED, as expected)
    1  prediction NOT met (already fixed, or the analysis is wrong)
    2  the harness itself could not set up the scenario

Usage:
    & $py verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/reproduce.py
    & $py verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/reproduce.py --workdir <dir>
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from application.editing.service import RegionEditingService  # noqa: E402
from application.tasks.service import PipelineService  # noqa: E402
from domain.regions.entities import BBox, RegionGeometry, RegionOrigin  # noqa: E402
from domain.tasks.models import (  # noqa: E402
    CommandType,
    PipelineRunStatus,
    PipelineScope,
    ScopeType,
    StepRunStatus,
)
from infrastructure.filesystem.managed_storage import ManagedFileStorage  # noqa: E402
from infrastructure.pipeline.assembly import build_production_pipeline  # noqa: E402
from infrastructure.providers.handlers import (  # noqa: E402
    HandlerDependencies,
    ProductionHandlers,
    RegionMaskGeometry,
    STEP_DETECT,
    STEP_OCR,
)
from infrastructure.providers.registry import (  # noqa: E402
    ProviderDescriptor,
    ProviderRegistry,
)
from infrastructure.providers.retry import RetryPolicy  # noqa: E402
from infrastructure.providers.step_writes import (  # noqa: E402
    ArtifactStepWriter,
    RegionStepWriter,
)
from infrastructure.sqlite.connection import open_database  # noqa: E402
from infrastructure.sqlite.migrator import MigrationRunner  # noqa: E402
from infrastructure.sqlite.pipeline import SqliteTargetCatalog  # noqa: E402
from infrastructure.sqlite.regions import SqliteRegionRepository  # noqa: E402
from infrastructure.sqlite.schema import default_migrations  # noqa: E402
from ports.detection.ports import (  # noqa: E402
    DetectionRequest,
    DetectionResult,
    RegionCandidate,
)
from ports.inpaint.ports import ImageFrame  # noqa: E402
from ports.ocr.ports import OcrResult  # noqa: E402
from ports.providers.profiles import CAPABILITY_OCR  # noqa: E402

NOW = "2026-09-28T00:00:00+00:00"
PAGE_ID = "page-1"
OCR_TEXT = "こんにちは"


# ----------------------------------------------------------------------
# deterministic doubles (no network, no model, no randomness)
# ----------------------------------------------------------------------
class DeterministicDetector:
    provider_id = "fake-detect"
    provider_type = "fake"

    def __init__(self) -> None:
        self.requests: list[DetectionRequest] = []

    def detect(self, request: DetectionRequest) -> DetectionResult:
        self.requests.append(request)
        return DetectionResult(
            page_id=request.page_id,
            candidates=(
                RegionCandidate(
                    polygon=((0.0, 0.0), (10.0, 0.0), (10.0, 5.0)),
                    provider_label="det-0",
                ),
                RegionCandidate(
                    polygon=((20.0, 8.0), (30.0, 8.0), (30.0, 12.0)),
                    reading_order=7,
                    provider_label="det-1",
                ),
            ),
            provider_id=self.provider_id,
            provider_type=self.provider_type,
        )


class DeterministicOcr:
    provider_id = "fake-ocr"
    provider_type = "fake"
    languages = frozenset({"japanese"})
    needs_detection = False
    requires_gpu = False

    def __init__(self, text: str = OCR_TEXT) -> None:
        self.text = text
        self.requests: list = []

    def recognize(self, request) -> OcrResult:
        self.requests.append(request)
        return OcrResult(
            region_id=request.region_id,
            text=self.text,
            provider_id=self.provider_id,
            provider_type=self.provider_type,
            model="fake-model",
            confidence=0.5,
            script=request.script,
            direction=request.direction,
            options=request.options,
        )


class FakeImages:
    def page_frame(self, page_id: str) -> ImageFrame:
        return ImageFrame(width=32, height=16, mode="rgb24",
                          data=b"\x00" * (32 * 16 * 3))

    def region_crop(self, page_id: str, region_id: str) -> tuple[bytes, int, int]:
        return b"crop-bytes", 4, 3

    def page_png(self, page_id: str) -> bytes:  # pragma: no cover - unused here
        raise AssertionError("REOCR_ALL must not need the page PNG")


class FakeGeometrySource:
    def mask_geometry(self, region_id: str) -> RegionMaskGeometry:
        return RegionMaskGeometry(boxes=((0, 0, 2, 2),))


# ----------------------------------------------------------------------
# workspace
# ----------------------------------------------------------------------
def seed(conn: sqlite3.Connection) -> None:
    with conn:
        conn.execute(
            "INSERT INTO books (book_id, title, created_at, updated_at) VALUES (?,?,?,?)",
            ("book-1", "Book", NOW, NOW),
        )
        conn.execute(
            "INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
            " VALUES (?,?,?,?,?)",
            ("chapter-1", "book-1", "Chapter", NOW, NOW),
        )
        conn.execute(
            "INSERT INTO pages (page_id, chapter_id, source_filename, source_order,"
            " sort_order, source_hash, source_size_bytes, width, height,"
            " managed_original_ref, created_at, updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (PAGE_ID, "chapter-1", "001.png", 0, 0, "hash", 3, 32, 16,
             "original/001.png", NOW, NOW),
        )


def build_service(workdir: Path):
    latest = max(m.schema_version for m in default_migrations())
    conn, _ = open_database(workdir / "app.db", latest_known_schema_version=latest)
    MigrationRunner(conn, default_migrations()).apply_pending()
    seed(conn)

    storage = ManagedFileStorage(workdir / "managed")
    storage.ensure_layout()
    regions = SqliteRegionRepository(conn)
    editing = RegionEditingService(regions)

    def region_creator(page_id, polygon, reading_order, provenance):
        xs = [int(round(x)) for x, _ in polygon]
        ys = [int(round(y)) for _, y in polygon]
        region = editing.create_region(
            page_id,
            RegionGeometry(
                bbox=BBox(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)),
                polygon=tuple((int(round(x)), int(round(y))) for x, y in polygon),
            ),
            reading_order=reading_order,
            origin=RegionOrigin.MACHINE,
        )
        return region.region_id

    ocr = DeterministicOcr()
    registry = ProviderRegistry()
    registry.register(
        ProviderDescriptor(
            provider_id=ocr.provider_id,
            provider_type="fake",
            capabilities=frozenset({CAPABILITY_OCR}),
        ),
        lambda: ocr,
    )
    handlers = ProductionHandlers(
        HandlerDependencies(
            registry=registry,
            regions=regions,
            region_writer=RegionStepWriter(conn, regions),
            artifacts=ArtifactStepWriter(conn, storage),
            images=FakeImages(),
            geometry=FakeGeometrySource(),
            retry_policy=RetryPolicy(max_attempts=1, backoff_seconds=0),
            detector=DeterministicDetector(),
            region_creator=region_creator,
        )
    )
    service = build_production_pipeline(
        conn,
        handlers=handlers.as_mapping(),
        settings={"ocr": {"script": "japanese"}},
        provider_bindings={"ocr": {"provider_id": ocr.provider_id}},
    )
    return conn, regions, ocr, service


# ----------------------------------------------------------------------
# reporting helpers
# ----------------------------------------------------------------------
def unit_rows(units) -> list[dict]:
    return [
        {
            "unit_id": u.unit_id,
            "step_type": u.step_type,
            "target_id": u.target_id,
            "region_id": u.region_id,
            "decision": u.decision.value,
        }
        for u in units
    ]


def catalog_view(catalog: SqliteTargetCatalog, target_id: str) -> dict:
    try:
        snap = catalog.current(target_id)
    except Exception as error:  # noqa: BLE001 - diagnostic dump
        return {"target_id": target_id, "error": repr(error)}
    return {
        "target_id": target_id,
        "target_type": snap.target_type.value,
        "current_revisions": dict(snap.current_revisions),
        "lock": {
            "page_locked": snap.lock.page_locked,
            "region_locked": snap.lock.region_locked,
            "translation_locked": snap.lock.translation_locked,
            "inpaint_locked": snap.lock.inpaint_locked,
        },
        "stage_states": {k: v.value for k, v in snap.stage_states.items()},
    }


def dump(title: str, payload) -> None:
    print(f"\n===== {title} =====")
    print(json.dumps(payload, ensure_ascii=False, indent=2, default=str))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workdir", default=None)
    args = parser.parse_args(argv)

    workdir = (
        Path(args.workdir).resolve()
        if args.workdir
        else Path(tempfile.mkdtemp(prefix="diag-m2-regionless-"))
    )
    workdir.mkdir(parents=True, exist_ok=True)
    print(f"[reproduce] workspace: {workdir}")

    try:
        conn, regions, ocr, service = build_service(workdir)
    except Exception as error:  # noqa: BLE001
        print(f"[reproduce] HARNESS SETUP FAILED: {error!r}")
        return 2

    catalog = SqliteTargetCatalog(conn)

    run = service.create_run(
        CommandType.REOCR_ALL,
        PipelineScope(ScopeType.PAGE, selected_ids=(PAGE_ID,)),
    )
    planned = service.plan_run(run.run_id)
    before_units = planned.tasks[0].units          # tuple snapshot, pre-backfill
    dump("AC2-A PlanUnit BEFORE detect (plan time)", unit_rows(before_units))
    dump("AC2-B catalog.current(page) at plan time", catalog_view(catalog, PAGE_ID))

    executed = service.execute_run(run.run_id)
    after_units = executed.tasks[0].units          # post-backfill view

    dump("AC2-C PlanUnit AFTER detect/backfill", unit_rows(after_units))

    region_ids = [r.region_id for r in regions.list_regions(PAGE_ID)]
    dump(
        "AC2-D regions created by detect",
        [
            {
                "region_id": r.region_id,
                "reading_order": r.reading_order,
                "current_revision_id": r.current_revision_id,
            }
            for r in regions.list_regions(PAGE_ID)
        ],
    )
    dump("AC2-E catalog.current(page) after detect", catalog_view(catalog, PAGE_ID))
    for rid in region_ids:
        dump(f"AC2-F catalog.current({rid}) after detect", catalog_view(catalog, rid))

    steps = [
        {
            "step_run_id": s.step_run_id,
            "step_type": s.step_type,
            "unit_id": s.unit_id,
            "target_id": s.target_id,
            "page_id": s.page_id,
            "region_id": s.region_id,
            "status": s.status.value,
            "input_refs": dict(s.input_refs),
            "lock_snapshot": {
                "page_locked": s.lock_snapshot.page_locked,
                "region_locked": s.lock_snapshot.region_locked,
                "translation_locked": s.lock_snapshot.translation_locked,
                "inpaint_locked": s.lock_snapshot.inpaint_locked,
            },
            "error_code": s.error_code,
            "error_detail": s.error_detail,
        }
        for s in executed.step_runs
    ]
    dump("AC2-G StepRun chain (input_refs / lock_snapshot / error)", steps)
    dump(
        "AC2-H final",
        {
            "run_status": executed.status.value,
            "task_status": executed.tasks[0].status.value,
            "task_error_code": executed.tasks[0].error_code,
            "task_error_detail": executed.tasks[0].error_detail,
            "planned_step_units": executed.planned_step_units,
            "terminal_step_units": executed.terminal_step_units,
            "candidates": [c.reason for c in executed.candidates],
        },
    )
    dump(
        "AC2-I region revisions (write evidence)",
        {
            rid: conn.execute(
                "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?", (rid,)
            ).fetchone()[0]
            for rid in region_ids
        },
    )

    # ---------------- verdict ----------------
    print("\n===== AC1 VERDICT =====")
    detect_step = next((s for s in steps if s["step_type"] == STEP_DETECT), None)
    ocr_step = next((s for s in steps if s["step_type"] == STEP_OCR), None)
    checks: list[tuple[str, bool, str]] = []
    checks.append(("detect step ran and committed",
                   bool(detect_step) and detect_step["status"] == "completed",
                   f"detect={detect_step and detect_step['status']}"))
    checks.append(("ocr step is FAILED with LOCK_CHANGED",
                   bool(ocr_step) and ocr_step["error_code"] == "LOCK_CHANGED",
                   f"ocr={ocr_step and ocr_step['error_code']}"))
    checks.append(("failure is the writer guard on a None expectation",
                   bool(ocr_step) and "expected None" in (ocr_step["error_detail"] or ""),
                   f"detail={ocr_step and ocr_step['error_detail']}"))
    checks.append(("smoking gun: ocr target_id still the Page, region_id set",
                   bool(ocr_step) and ocr_step["target_id"] == PAGE_ID
                   and bool(ocr_step["region_id"]),
                   f"target_id={ocr_step and ocr_step['target_id']} "
                   f"region_id={ocr_step and ocr_step['region_id']}"))
    checks.append(("ocr input_refs carries no 'region' key",
                   bool(ocr_step) and "region" not in (ocr_step["input_refs"] or {}),
                   f"input_refs={ocr_step and ocr_step['input_refs']}"))
    checks.append(("run ends COMPLETED_WITH_FAILURES",
                   executed.status is PipelineRunStatus.COMPLETED_WITH_FAILURES,
                   f"status={executed.status.value}"))
    checks.append(("no Region write happened (1 revision = detect first revision)",
                   all(count == 1 for count in (
                       conn.execute(
                           "SELECT COUNT(*) FROM region_revisions WHERE region_id = ?",
                           (rid,),
                       ).fetchone()[0]
                       for rid in region_ids
                   )) and bool(region_ids),
                   f"region_ids={region_ids}"))
    checks.append(("counterfactual: the Region DOES have a current revision",
                   bool(region_ids)
                   and catalog_view(catalog, region_ids[0])["current_revisions"].get("region"),
                   "region current_revision_id non-empty"))

    for name, ok, detail in checks:
        print(f"  [{'PASS' if ok else 'MISS'}] {name}  -- {detail}")

    reproduced = all(ok for _, ok, _ in checks)
    print(
        "\nVERDICT: "
        + ("DEFECT_REPRODUCED (expected red)" if reproduced else "NOT_REPRODUCED")
    )
    if not reproduced:
        print(
            "The predicted regionless detect->backfill->ocr LOCK_CHANGED did not "
            "materialise as analysed: either the defect is fixed at this head, or "
            "the static analysis needs revision."
        )
    return 0 if reproduced else 1


if __name__ == "__main__":
    raise SystemExit(main())
````

### 6.3 `doc/handoffs/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-5789b30b.md`

（命名用 base 短 SHA：**未产生 delivery head**，交付未提交，状态 `blocked`。）

````markdown
# Handoff — DIAG-M2-REGIONLESS-LOCK-CHANGED-001

- Owner: DeepSeek Harness
- Task: doc/tasks/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md（`ready / M2_REGIONLESS_LOCK_CHANGED_DIAGNOSTIC_RELEASED`）
- Base / pull point: `5789b30b37dfbf79d9bca707b5fdaaa562ada707`
- Branch / worktree: `agent/deepseek/DIAG-M2-REGIONLESS-LOCK-CHANGED-001`
  / `G:/CODEX/New Manga.worktrees/DIAG-M2-REGIONLESS-LOCK-CHANGED-001-dsh`
- **Delivery head: NONE（无提交）** — 本会话既不能执行 shell 也不能写 worktree
- Status: **BLOCKED**（AC1/AC2/AC5）+ **STATIC**（AC3/AC4）
- Reviewer（非作者）: Antigravity；Integrator: Codex

## 1. 阻塞原因（原始错误）

```
pwsh: Error: SetNamedSecurityInfoW failed (Win32 5): grantWrite(G:\CODEX\New Manga)
write(worktree): [sandbox: file access denied under workspace-write mode]
escalation: requires approval, but no approval channel is available
```

- 复现次数：4 次直连 + 2 次子代理独立探针，错误逐字节相同，与 `workdir` 无关；
- 沙箱在**命令执行前**准备阶段失败 ⇒ 所有验证命令 `NOT_RUN`，非 `FAIL`；
- worktree 在 session workspace `G:\CODEX\New Manga` 之外 ⇒ 写入被拒；
- `read`/`grep`/`glob` 对 worktree 可读（已实证），故可完成静态诊断。

## 2. 交付物状态

| 交付物 | 状态 |
|---|---|
| `doc/research/DIAG-M2-REGIONLESS-LOCK-CHANGED-001.md` | 全文已产出，**由集成方落盘** |
| `verification/DIAG-M2-REGIONLESS-LOCK-CHANGED-001/reproduce.py` | 全文已产出，**未落盘、未执行** |
| 先红日志 | **NOT_RUN**（不存在） |
| `git diff --check` | **NOT_RUN** |
| 既有受影响测试复跑 | **NOT_RUN** |
| Handoff（本文件） | 全文已产出，**由集成方落盘** |

## 3. 静态根因（一句话）

`_backfill_detected_regions`（`src/application/tasks/service.py:921-946`）只重绑
`region_id`、不重绑 `target_id`；`ocr` 的 `StepRun.input_refs` 仍来自 Page target
⇒ `expected_current_revision_id = input_refs.get("region") = None`，而 Region 已有
detect 原子写入的首版 ⇒ `RegionStepWriter._persist`
（`src/infrastructure/providers/step_writes.py:219-231`）抛 `LockBlocked`
（`error_code="LOCK_CHANGED"`）⇒ run `COMPLETED_WITH_FAILURES`。

失败比较点**不是** `catalog.commit_step` 的锁分支（同源比较，恒等）。

## 4. 判别性预测（执行者须逐条核对）

见 `doc/research/...` §3 与 `reproduce.py` 的 8 条 checks；核心是
`ocr.error_code == "LOCK_CHANGED"` 且 `error_detail` 含 `expected None`、
`ocr.target_id == page_id`、`region_ids` 存在但 `region_revisions == 1`。

## 5. 修复 Task 的最小范围（本 Task 未实施）

- 文件：`src/application/tasks/service.py`，函数：`_backfill_detected_regions`；
- 同时重绑 `target_id=primary` 与 `region_id=primary`；**不改 `unit_id`**；
- 不得改动多 Region 只绑 primary 的既有语义；不得改动 catalog/契约/schema；
- 半修（只改 snapshot 来源）会把 `LOCK_CHANGED` 变成 `TARGET_NOT_FOUND`，必须用 N1 固定。

## 6. 回归 / 负向矩阵

回归 R0–R5、负向 N1–N7、持久化风险 R-a–R-c：见 `doc/research/...` §5.4。

## 7. 未验证项（诚实披露）

- 本 Task 全部运行时证据均未采集；`$py` 未执行、版本未复验；
- git HEAD 仅以工作树元数据文件读取确认为 `5789b30b`，未用 `git rev-parse`；
- 任务文件在 base `5789b30b` 的 worktree 中**不存在**（仅存在于 `main`@`acddebcb`），
  请 Codex 确认 release 文档提交与 worktree base 的一致性。

## 8. 建议下一步

1. Codex 修复沙箱（或为 Owner 提供可用执行与审批通道），把本 Handoff 的三份文件
   落盘并 import 提交，固定 delivery head，再让 Owner 按原验证命令补 AC1/AC2/AC5；
2. 同时另立**修复 Task**（Owner=Antigravity/ZCode，Reviewer=非作者），范围限定
   §5；或先让 Antigravity 以本报告的静态结论做非作者复核（可复核性充分：全部证据为
   `path:line`）。
````

---

## 7. 建议下一步（按协作协议 §5.1）

**无需等待 Owner 的下一步是「修复 Task」，但前置条件是环境修复。** 推荐执行顺序：

1. **Codex（Integrator）先修沙箱**：`SetNamedSecurityInfoW Win32 5` 说明 DSH 无法为 `G:\CODEX\New Manga` 授权写 ACL；同时 worktree 位于 session workspace 之外，导致 workspace-write 不可用。请二选一：把 worktree 纳入 session workspace（或将 session workspace 指向 `G:\CODEX\New Manga.worktrees\DIAG-...-dsh`），或提供可用审批通道。
2. **落盘本次交付物**：把 §6.1/6.2/6.3 三份文件写入 worktree 并提交，固定 delivery head；随后由我（或任一有执行通道的 Agent）跑三条验证命令补 AC1/AC2/AC5 的先红证据。
3. **释放修复 Task**：建议 `FIX-M2-REGIONLESS-REGION-REBIND-001`，
   Owner=Antigravity（或 ZCode），Reviewer=非作者，范围**仅** `src/application/tasks/service.py:_backfill_detected_regions`，AC 直接采用本报告 §5.4 的 R0–R5 / N1–N7 / R-a–R-c 矩阵。若需先做非作者复核，可让 Antigravity 以 §4 的 `path:line` 证据链复核本静态结论（成本低、可独立判定）。

若不需要上述动作，则**无需下一步操作**。
