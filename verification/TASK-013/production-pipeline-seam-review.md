# TASK-013 生产 Pipeline seam 独立 Review

- Reviewer：DeepSeek Harness（非本变更作者；作者为 Codex）
- **base_commit**：`126bab54e03849d2684921a5d7fb211f7ad7c23b`
- **reviewed_head**：`e5b58e7378a9fa4e5737220e51a9000a19a21a4e`（实际被审 head，本报告绑定此值）
- 审计分支：`agent/codex/TASK-013-production-pipeline-seam`；提交链 `80fdc7e`（设计）→ `8151151`（绑定生产 seam）→ **`e5b58e7`**（修复 catalog 失败码）
- Reviewer 工作区：`G:/CODEX/New Manga.worktrees/TASK-013-deepseek-review`（`agent/deepseek/TASK-013-review`，已 fast-forward 至 `e5b58e7`）
- 上级 Review：[TASK-013 第一轮（da1daf1）](../../../doc/reviews/TASK-013-da1daf1.md)
- **结论：approved**（P0 = 0，P1 = 0，P2 = 2）

## 变更范围

`git diff 126bab5 e5b58e7` = 23 文件、`+1596/−62`：

| 类别 | 路径 |
|---|---|
| Schema | `src/infrastructure/sqlite/schema.py`（+135，追加 v3） |
| 生产 seam | `src/infrastructure/sqlite/pipeline.py`（**新增 835 行**）、`src/infrastructure/pipeline/{__init__,assembly,executor}.py` |
| 应用层 | `src/application/tasks/service.py`（+28/−…，生命周期持久化） |
| UI（来自第一轮合入） | `src/ui/qml/workbench/WorkbenchView.qml`、`src/ui/viewmodels/workbench/{run_controller,viewmodel}.py` |
| 测试 | `tests/pipeline/test_pipeline_production_seam.py`（新增 154）、`tests/storage/test_schema_migration.py`、`tests/editing/test_sqlite_regions.py`、`tests/library/test_sqlite_library.py`、`tests/workbench/test_workbench_viewmodel.py` |
| 文档/证据 | `doc/handoffs/TASK-013-workbench-task-progress.md`、`doc/tasks/TASK-013.md`、`verification/TASK-013/{production-pipeline-seam-design,r1-assembly-decision,integration-f0814a8}.md`，另 4 个状态文档（见 R-02） |

**必查 whitespace**：`git diff --check 126bab5 e5b58e7 --` → **退出码 2**（见 R-01）。

## 八项审查结论

### ① v3 仅追加、v1/v2 未变 —— **PASS**

`git diff 126bab5 e5b58e7 -- src/infrastructure/sqlite/schema.py` 的**删除行为空集**——即 v1/v2 的 SQL 文本一字未动。新增 `SCHEMA_VERSION_V3 = 3`、`MIGRATION_V3_NAME = "v3__production_pipeline_persistence"`，`default_migrations()` 由 `(v1, v2)` 扩展为 `(v1, v2, v3)`。v3 追加 **9 张表 + 4 个索引**：`pipeline_runs`、`pipeline_run_targets`、`pipeline_tasks`、`step_runs`、`step_run_input_refs`、`step_run_output_refs`、`step_result_candidates`、`pipeline_stage_states`、`pipeline_defaults`（及 `idx_pipeline_runs_status`、`idx_pipeline_run_targets_page`、`idx_pipeline_tasks_run`、`idx_step_runs_run`、`idx_step_result_candidates_run`）。设计文档的"v1/v2 SQL 不改"与验收门槛"v3 只追加表"均成立。

### ② `SqliteTargetCatalog` 真实查询 + Revision/Lock 原子 guard —— **PASS**

真实层级查询由 `expand`（scope 展开）、`current`、`_page_or_error`、`_region_or_error`、`_region_from_id`、`_page_deleted`、`_page_revisions`、`_stage_states` 组成，无任何内存替身。

**`commit_step` 是真正的单事务 compare-and-write**：`BEGIN IMMEDIATE` → 在**同一事务内**重读 `current(target_id)` → 逐项比对 `expected_revisions`（不符即 `rollback` + `input_revision_changed`）→ 比对 `expected_lock`（不符即 `lock_changed`）→ 按目标类型写入：Region 走 `UPDATE regions … WHERE region_id = ? AND deleted_at IS NULL`，Page 按 `artifact_type` 走 `UPDATE media_artifacts … WHERE page_id = ? AND artifact_type = ?`，两者都检查 `rowcount != 1` 并回滚为 `target_not_found` → `pipeline_stage_states` 以 `ON CONFLICT … DO UPDATE` 幂等 upsert → `commit()`；任何异常统一 `rollback` 并返回 `db_failed`。Region 路径还显式拒绝非 `"region"` 的 revision key，与 TASK-002 §2.1 的"同属"语义一致。

### ③ `SqlitePipelineStore` round-trip 与 recovery —— **PASS**

`put` / `get` / `list_ids` 三个方法背后是完整的成对编解码器：`_run_dict`/`_run`、`_task_dict`/`_task`、`_step_dict`/`_step`、`_candidate_dict`/`_candidate`、`_run_target_dict`/`_run_target`、`_unit_dict`/`_unit`、`_scope_dict`/`_scope`、`_target_dict`/`_target`、`_region_dict`/`_region`、`_lock_dict`/`_lock` —— 覆盖 Run / RunTarget / Task / StepRun / PlanUnit / StepResultCandidate / Scope / Target / RegionSnapshot / LockSnapshot，无遗漏族。`recover_running_runs` 在持久化 store 上把 `RUNNING` 的 step 标记为 `INTERRUPTED` 并 `_persist`，使"进程重启后识别 interrupted"在真实 SQLite 上成立（这正是 TASK-011 Review 中 R-003 登记的未证明路径）。

### ④ Snapshot 脱敏与冻结语义 —— **PASS**

`_SENSITIVE_PARTS = ("secret", "password", "token", "api_key", "apikey")` 配 `_redact()` 递归处理 dict/list，并**同时**用于两条出口：写库时的 `_dump(_redact(settings))` / `_dump(_redact(provider_bindings))` / `_dump(_redact(context_policy))`，以及 `freeze()` 返回的 `freeze_snapshot(_redact(...))`。即：**落库与冻结都只见到脱敏值**，Secret 不可能经该 seam 进入 SQLite；冻结侧使用 `freeze_snapshot` 得到不可变副本，满足"Run 自己保存冻结值"。设计文档要求"数据库中不出现 Secret 字段值"与实现一致。

### ⑤ `ProductionStepExecutor` 禁止假输出 —— **PASS**

docstring 明确："Dispatch to registered production handlers **without fake output**. The registry is deliberately explicit: an absent handler is a **provider availability error, never a successful deterministic placeholder**."实现按 `run.provider_binding_snapshot[unit.step_type]` 解析 handler，**无 handler 即抛 `StepExecutionError("PROVIDER_UNAVAILABLE", …)`**；handler 内异常统一转 `PROVIDER_FAILED`；返回非 `StepResult` 亦被拒绝。**不存在任何回退到 Deterministic/InMemory 的分支**——即"假输出"在结构上不可达，与第 5 项要求完全一致。

### ⑥ `PipelineService` 生命周期持久化 —— **PASS**

引入统一的 `_persist(run)`（薄封装 `self._store.put(run.run_id, run)`）并替换原先零散的直接 `put` 调用，使持久化点**可枚举**。实际在每个生命周期边界都调用了它：`create_run`、`plan_run`、`record_step_attempt`、`commit_step_result` 的 committed 与 candidate 两分支、`_fail_mapping`、`_fail_step`、`execute_run` 的 running / paused / RESOURCE_LIMIT_EXCEEDED / cancelled / aggregate 五处、`control_run` 的 pause / stop / continue / restart / abandon 五处、以及 `recover_running_runs`。此外把 catalog 的 `db_failed` 与 `target_not_found` 区分开（`code = "DB_FAILED" if outcome.status == "db_failed" else "TARGET_NOT_FOUND"`），这正是 `e5b58e7` 这次修复的内容——保留了生产 catalog 的失败码语义。

### ⑦ 变更路径与 TASK-012/013、R-1、冻结 Task 边界 —— **PASS（含一处登记问题，见 R-02）**

- **TASK-012 已审实现**：`src/ui/models/tasks/**`、`src/ui/viewmodels/workbench/{viewmodel,run_controller}.py`、`WorkbenchView.qml` 未被破坏性改写；`tests/workbench` 由 50 → **51 passed**（新增 1 项），未削弱既有断言。
- **R-1**：`verification/TASK-013/r1-assembly-decision.md` 记录清晰——R-1 作为**独立最小装配切片**批准登记，**不并入** TASK-013；当时因"完整生产 Pipeline seam 尚未就绪"而 `BLOCKED/NOT_RUN`，并给出 seam 核实表与 4 条接线验收门槛。**本轮 `e5b58e7` 恰好补齐了该表中标记为 BLOCKED 的四项**（pipeline catalog / store / snapshot / executor），因此 R-1 现在具备推进条件；但本切片**未**触碰 `src/bootstrap/app.py`，边界保持干净。
- **冻结 Task**：`src/domain/**`、共享 Protocol、`src/bootstrap/**`、依赖清单、`AGENTS.md`、QML（除第一轮合入项）均未改动；TASK-015 及其他冻结 Task 未释放。
- **其他 Task 的测试改动**（重点核验）：`tests/editing/test_sqlite_regions.py`、`tests/library/test_sqlite_library.py` 把硬编码的 `latest_known_schema_version=2` 改为 `default_migrations()[-1].schema_version`（**去硬编码，是改进**）；`tests/storage/test_schema_migration.py` 相应把 `[1, 2]` 更新为 `[1, 2, 3]`、TOO_NEW 用例的"未来版本"由 3 改为 4、备份行数 1→2 / 文件数 2→3，并把 checksum 断言消息由硬编码 `"v2 checksum mismatch"` 泛化为 `f"v{migration.schema_version} checksum mismatch"`，`test_v2_introduces_no_out_of_scope_tables` 改用 `:memory:` 库只应用 `default_migrations()[:2]` 以**精确**验证 v2 边界。**全部为对 v3 的正确适配，未发现为掩盖回归而放宽的断言**；`tests/storage` 33 passed、`tests/editing`/`tests/library` 全量通过佐证。
- **边界问题**：本切片实际改动了白名单**未列出**的路径（`src/infrastructure/**`、`src/application/tasks/service.py`、`tests/{pipeline,storage,editing,library}/**`）→ R-02。

### ⑧ Windows 默认 Qt 测试与 passed/skipped 分列 —— **PASS**

环境：Windows `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；**`QT_QPA_PLATFORM` 实测为空**（默认 Windows Qt，未使用 offscreen）。

| # | 命令 | 退出码 | passed | skipped | skip 原因 |
|---|---|---|---|---|---|
| 1 | `…TASK-012-py312/python.exe -m pytest tests/pipeline -v` | **0** | **30** | **0** | 无 skip |
| 2 | `…python.exe -m pytest tests/storage -v` | **0** | **33** | **0** | 无 skip |
| 3 | `…python.exe -m pytest tests/workbench -v` | **0** | **51** | **0** | 无 skip |
| 4 | `…python.exe -m pytest tests -q -rs` | **0** | **463** | **6** | 全部 `openssl unavailable` |

**命令 4 的 6 项 skip 逐项原因**：

| 数量 | 位置 | 原因 |
|---|---|---|
| 1 | `tests/network/test_connection_tester.py:106` | `openssl unavailable` |
| 1 | `tests/network/test_transport_tls.py:39` | `openssl unavailable` |
| 1 | `tests/network/test_transport_tls.py:47` | `openssl unavailable` |
| 1 | `tests/network/test_transport_tls.py:62` | `openssl unavailable` |
| 1 | `tests/network/test_transport_tls.py:69` | `openssl unavailable` |
| 1 | `tests/network/test_transport_tls.py:83` | `openssl unavailable` |

## Findings

| ID | 级别 | 文件/行 | 触发条件 | 影响 | 复现证据 | 建议 | disposition |
|---|---|---|---|---|---|---|---|
| R-01 | P2 | `verification/TASK-013/production-pipeline-seam-design.md:3,4,5` | 任何执行 `git diff --check` 的场景（本项目 Review/集成必查项） | 三行存在**行尾空白**，使 `git diff --check 126bab5 e5b58e7 --` **退出码为 2**。从内容看疑似 Markdown 硬换行（行尾两个空格）的书写习惯，不影响渲染语义，但会使按退出码判定的 whitespace 门禁失败 | `git diff --check 126bab5 e5b58e7 --` 输出三行 `trailing whitespace`（`状态：APPROVED…`／`基线：…`／`Owner：…`） | 去除行尾空白（Markdown 中如需硬换行可改用显式 `<br>` 或独立段落）。属证据文档格式修正，不涉及实现 | open（非阻塞） |
| R-02 | P2 | `doc/tasks/TASK-013.md`（`允许修改范围` 未更新）；本切片实际改动的 `src/infrastructure/**`、`src/application/tasks/service.py`、`tests/{pipeline,storage,editing,library}/**` | 任何按 Task 白名单核对范围的人 | TASK-013 的 `允许修改范围` 仍只有 `src/ui/qml/workbench/**`、`src/ui/viewmodels/workbench/**`、`src/ui/models/tasks/**`、`tests/workbench/**`、`doc/tasks/TASK-013.md`、`doc/handoffs/TASK-013-*.md`、`verification/TASK-013/**`；本切片的实现路径**不在其中**。实际授权来源是 `verification/TASK-013/production-pipeline-seam-design.md`（"APPROVED FOR IMPLEMENTATION（用户已授权）"，且该文件落在白名单内的 `verification/TASK-013/**`），授权本身可查，但**未同步到 Task 文件**，使"按白名单核对零越界"这一常规手段失效 | `git -C $w show e5b58e7:doc/tasks/TASK-013.md \| Select-String '^- (src/\|tests/\|doc/\|verification/)'` 与 `git diff --name-status 126bab5 e5b58e7` 对照 | 由 Codex 在 `doc/tasks/TASK-013.md` 中以独立小节登记"生产 Pipeline seam 切片"的实际授权路径与授权来源（或把该切片拆为独立 Task 文件），使白名单与实现一致 | open（非阻塞） |
| R-03 | 观察 | `src/ui/qml/workbench/WorkbenchView.qml:174`（`stepPage`） | 沿用第一轮 R-003 | 第一轮 Review 的 **R-003 仍未关闭**：`stepPage` 的索引运算与边界钳制仍在 QML 侧（`git grep 'function stepPage'` 在 `e5b58e7` 仍命中）。本轮范围为生产 seam，未处理该项属正常；在此仅记录状态，**不重复计为本轮 finding** | `git -C $w grep -n 'function stepPage' e5b58e7 -- src/ui/qml/workbench/WorkbenchView.qml` | 按第一轮建议下沉为 ViewModel `Slot`；可随 R-1 接线切片一并处理 | 既有，未关闭 |

**同时确认：第一轮的 R-001 已修复** —— `git grep 'terminate'` 在 `e5b58e7` 的 `run_controller.py` **无命中**（退出码 1），`QThread.terminate()` 强杀路径已移除，与 TASK-011 明文"不可用线程强杀破坏事务"的约束不再冲突。

**未发现 P0/P1 问题。** 两项 P2 分别为证据文档的 whitespace 与范围登记口径，均不影响实现正确性与数据安全。

## 未执行项

| 项 | 状态 | 说明 |
|---|---|---|
| R-1 入口装配（`src/bootstrap/app.py` 注入 `workbenchViewModel`） | **NOT_RUN（按裁决不在本切片）** | 设计文档与 `r1-assembly-decision.md` 均声明本切片不做 R-1；seam 现已就绪，可另立切片 |
| 真实 OCR / 翻译 / Inpaint / Provider 端到端 | **NOT_RUN** | `ProductionStepExecutor` 在无 handler 时按设计抛 `PROVIDER_UNAVAILABLE`；真实 provider 尚未存在。本报告不把 registry 结构视为 provider 质量证据 |
| 真实进程被杀（kill -9）后的恢复 | **NOT_RUN** | `recover_running_runs` 与 `INTERRUPTED` 标记已在真实 SQLite 上验证；但"操作系统强杀进程后重开"的端到端演练未执行 |
| 并发多 Run / 多连接写竞争 | **NOT_RUN** | 本切片为串行执行语义；`BEGIN IMMEDIATE` 的并发行为未压测 |
| 性能 / 大 Run 规模 | **N/A** | 无性能 AC |

## 三轴结论

**Spec**：设计文档给出的 7 项最小设计与 7 条验收门槛，本轮实现逐项对应且可核验——v3 纯追加、真实层级查询与单事务 Revision/Lock guard、Run/Task/Step/Ref/Candidate 完整 round-trip 与 recovery、双层脱敏 + 冻结、生产执行器无假输出、生命周期边界持久化、assembly helper 就位且不碰 bootstrap。**从设计到实现到证据，链路自洽。**

**Architecture**：新增代码集中在 `src/infrastructure/sqlite/pipeline.py` 与 `src/infrastructure/pipeline/**`，实现的是 TASK-011 已定义的 `TargetCatalog` / `PipelineStore` / `SnapshotProvider` / `StepExecutor` 四个消费侧 Protocol 的**生产适配**，未改动任何共享 Protocol 或领域模型；`PipelineService` 的改动是把"何时持久化"从零散调用收敛为可枚举的 `_persist`，属应用层内部重构，未改变其对外契约。生产与测试替身（InMemory/Deterministic）在两个不同实现中共存，生产路径**结构上不允许**回退到替身。唯一架构治理问题是范围登记的同步（R-02）。

**Verification**：四条必需命令在指定任务环境、默认 Windows Qt 平台下**全部退出码 0**，passed/skipped 已分列，6 项 skip 逐项归因于 `openssl unavailable`（本机 PATH 无 openssl）。`tests/pipeline` 由 27 → 30（新增生产 seam 用例）、`tests/workbench` 由 50 → 51（新增 1 项），既有套件无退化。必查 whitespace 因 R-01 未通过。

## 结论与复审

**`e5b58e7378a9fa4e5737220e51a9000a19a21a4e` 可交 Codex 集成：decision = approved。**

- 八项审查中 ①~⑥ 与 ⑧ 全部 PASS，⑦ 除一处范围登记口径外均合规；**未发现 P0/P1**；两项 P2（R-01 whitespace、R-02 范围登记）可在集成前后的提交中关闭，**不需新的 reviewed head**。
- 本轮实测补齐了 TASK-011 Review 中登记为 NOT_RUN 的两条路径（PipelineRun/StepRun/Candidate 持久化、崩溃后 `INTERRUPTED` 识别），使 TASK-011 的 R-003 证据边界在**进程内 + SQLite 重启读取**意义上得到闭合；但操作系统强杀进程的端到端演练与并发写竞争仍未执行。
- **本报告绑定实际 `reviewed_head = e5b58e7378a9fa4e5737220e51a9000a19a21a4e`**；不包含任何 `integration_commit`（该值只能由 Codex 在集成动作完成后填写，不得由 Review 报告虚构）。

**集成时须由 Codex 完成**：①按协议 §6.6 串行集成并**由你填写 `integration_commit`**；②关闭 R-01（去除设计文档行尾空白）；③关闭 R-02（在 TASK-013 登记本切片的实际授权路径，或拆为独立 Task）；④R-03 与 R-1 可合并到下一个 R-1 接线切片处理；⑤集成后可启动 R-1，验收时按 `r1-assembly-decision.md` 的 4 条门槛执行，并注意该记录中"seam 未就绪"的前提已被本轮解除。

**剩余风险**：真实 provider 尚不存在，`ProductionStepExecutor` 的正确行为是"无 handler 即 `PROVIDER_UNAVAILABLE`"，因此**当前没有端到端 AI 链路证据**；进程强杀与并发写竞争未验证；R-1 未接线使生产入口的工作台仍为空状态；R-03（QML 侧 `stepPage` 计算）未关闭。本报告不释放任何冻结 Task，未修改任何生产代码或测试。
