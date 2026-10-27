# RUN-STORE-CACHE-RACE-FIX-1 实现报告（Core 共享缓存跨线程竞态修复）

- Task：`doc/tasks/RUN-STORE-CACHE-RACE-FIX-1.md`（base `97de0fa99`；交付 worktree 基于 HEAD `9ef53f24d`）
- Owner：`sandbox-verify`（DSH 委派，team task-39）；Reviewer：DSH
- 分支 / worktree：`task/RUN-STORE-CACHE-RACE-FIX-1` / `G:/CODEX/New Manga.workspace/worktrees/RUN-STORE-CACHE-RACE-FIX-1`
- 证据目录：`verification/RUN-STORE-CACHE-RACE-FIX-1/`
- 结论：**AC1–AC5 全部 MET**。`fresh=True` 投影读取不再替换执行缓存；`run_json` 写入新增 owner/修订 CAS；同一数据根、同一请求下"执行线程 + 100 ms 投影轮询"从修复前 **8/8 StepRun 卡 running、8 个 regionless INVALID_INPUT、8/8 任务失败** 变为修复后 **0 卡 running、0 regionless INVALID_INPUT**，与未轮询对照逐项一致。

---

## 1. 根因（沿用 SCHEDULER-THREAD-DIAG-1，不改判定）

`SqlitePipelineStore._cache`（普通 dict）跨线程共享 `PipelineRun` 可变对象；`GetTaskProjection` →
`get_task_projection(fresh=True)` → `store.refresh()` 在请求线程用"新加载克隆"替换 `_cache[run_id]`。
执行线程 `execute_run` 仍持有旧对象：`commit_step_result → _find_step → store.get()` 拿到克隆并提交/回填，
旧对象继续用未回填的 regionless unit 列表执行（下游 `ocr` → `INVALID_INPUT`），其后续 `_persist`
再把提交前状态整份写回 `run_json`（last-writer-wins）→ 已提交 StepRun 回退 `running`。

代码点（修复前）：`core_service.py:3236/3246` → `service.py:1394/1454/1531` →
`infrastructure/sqlite/pipeline.py:415`（`refresh` 替换缓存）。

---

## 2. 修复点（AC1 / AC2；不改 Core 语义、协议、Host 契约、旧壳）

| 文件 | 改动 |
|---|---|
| `src/infrastructure/sqlite/pipeline.py` | **AC1** `SqlitePipelineStore.refresh()`（现 L669）只返回 `_read_run()` 的**独立视图对象**，不再 `pop`/替换 `_cache[run_id]`；执行缓存只由 `get()/put()/write_in_current_transaction()` 持有。**AC2** 新增 `_write_revision`（每 Run 修订号）、`_adopt_revision()`（L627，加载即盖修订）与 `_check_write_revision()`（L632，写前 CAS）；`_write_run()`（L429）在写 `run_json` 前校验快照修订，成功后递增并回写对象（L529）。过期快照写入抛 `PipelineError("STALE_RUN_SNAPSHOT")`。 |
| `src/application/tasks/store.py` | **AC1** `InMemoryPipelineStore.refresh()` 返回 `_detached_run()` 结构克隆（L386/L434），与执行缓存对象分离：可变容器逐层复制，冻结快照（settings/provider/context/candidate payload/PlanUnit）不可变可共享。 |

语义边界：

- **保留 `fresh=True` 轮询**：`GetTaskProjection` 仍走 `get_task_projection(run_id, fresh=True)`，只把"视图读"与"执行缓存"解耦，没有关闭/降级轮询，也没有放宽任何并发或输入校验。
- **无 Schema 变更 / 无数据迁移**：修订号是进程内每 store 实例内存状态（见 §8 限制），`run_json` 格式不变。
- **无协议变更**：`PipelineStore` Protocol 签名、`GetTaskProjection`/`GetRunSnapshot` 线格式均未改。

---

## 3. AC1 证据（视图读不替换执行缓存）

`tests/pipeline/test_run_store_cache_race.py`（新增 7 项）：

- `test_refresh_returns_detached_view_and_keeps_execution_cache`：`refresh()` 返回对象 `is not` 缓存对象，且 `store.get()` 仍是原 owner 对象。
- `test_fresh_view_sees_committed_state_without_touching_owner`：owner 未落盘的内存态不出现在视图，视图不反改 owner。
- `test_in_memory_refresh_returns_independent_view`：内存 store 视图独立（改视图不影响 owner）。
- `test_get_run_snapshot_fresh_is_read_only`：服务层 `get_run_snapshot(fresh=True)` 不改 `_cache`。

判别力：修复前同一文件 **6 failed / 1 passed**（`DID NOT RAISE`/identity 断言失败），修复后 **7 passed**（`logs/pre-fix-pytest-unit.log` vs `logs/post-fix-pytest-unit.log`，均带 EXIT 码）。

## 4. AC2 证据（run_json 写入 owner/修订 CAS）

- `test_stale_snapshot_write_is_rejected`：owner 提交后，早于提交捕获的视图再 `put(...)` → `STALE_RUN_SNAPSHOT`，DB 保留新提交。
- `test_stale_write_inside_transaction_is_rejected`：`write_in_current_transaction()` 同一守卫（事务内被拒并回滚）。
- `test_repeated_owner_writes_are_accepted`：同一 owner 对象连续 3 次写入均被接受（不会误伤正常生命周期写）。

修复前 3 项全失败（无守卫），修复后全通过（`logs/post-fix-pytest-unit.log`：7 passed）。

## 5. AC3 证据（并发回归：执行线程 + 100 ms 投影轮询）

工具：`tools/repro_scheduler.py`（`verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py`）——与 `python -m bootstrap.core_service` 同拓扑（`assemble_production_core` + `CoreServiceServer` + 真实 `core-run-scheduler` 线程 + `accept_start_run`），第二线程按 `GetTaskProjection` 处理器等价路径轮询；每次运行使用 BOOK-FIXTURE-1 的**私有副本数据根**。

A/B 矩阵（`ab-matrix.json`，原始 JSON 见 `repro/`）：

| 场景 | 修复前 | 修复后 |
|---|---|---|
| `scheduler` + `projection-fresh`（100 ms） | **FAIL**：`running` 8 / `failed` 8，8/8 任务 failed，**8 卡 running + 8 regionless INVALID_INPUT** | **PASS**：`completed` 17 / `failed` 3，5 任务 completed、3 任务 failed，0 卡 running、0 regionless INVALID_INPUT |
| `scheduler` + `projection-cached`（对照） | PASS（同上干净结果） | PASS（同上干净结果） |
| `scheduler` + 不轮询（对照） | PASS | PASS |

- 修复前失败产物：`repro/pre-fix-projection-fresh.json`（verdict=FAIL）、`logs/pre-fix-repro-projection-fresh.log`（RESULT + `EXIT=1`）。
- 修复后通过产物：`repro/post-fix-projection-fresh.json`（verdict=PASS）、`logs/post-fix-repro-projection-fresh.log`（`EXIT=0`）。
- **修复后 fresh 轮询结果与 cached/不轮询对照逐项一致**（17/3/0/0），证明轮询不再影响执行语义，而不是"把轮询关掉"。

pytest 侧并发用例：`tests/pipeline/test_regionless_rebinding.py::test_projection_fresh_polling_does_not_corrupt_execution`（新增；SlowDetector/SlowOcr 拉宽窗口，10 ms 轮询，SQLite store + 真实 detect→回填→ocr 链）：修复前 FAIL（run `completed_with_failures`），修复后 PASS（3/3 重复稳定，`logs/post-fix-pytest-concurrency.log`）。

## 6. AC4 回归

同机同时段 A/B（全量 `python -m pytest tests -q`；本机为唯一运行环境）：

| 运行 | 被测源码 | 结果 | 失败集合 |
|---|---|---|---|
| pre-fix baseline（base `9ef53f24d`；排除本卡新增/改写用例：`--ignore=tests/pipeline/test_run_store_cache_race.py` + `-k "not projection_fresh_polling_does_not_corrupt_execution"`，1 deselected） | 修复前 | **4F / 2752P / 9S / 1 deselected** | `test_plugin_sandbox::test_sandbox_job_kills_grandchildren` + 基线既有 3 项 |
| post-fix（`dadcf72b9`） | 修复后 | **4F / 2760P / 9S** | 同上 4 项 |
| post-fix 辅助运行（同一模块；沙箱 flake 未触发） | 修复后 | 3F / 2761P / 9S | 基线既有 3 项 |

- 结论：**失败集合完全相同、0 新增失败**；通过数 **2752 → 2760（+8）** = 本卡新增 7 项单测 + 1 项并发用例。
- 第 4 个失败 `test_sandbox_job_kills_grandchildren` 是**既有 flaky**（Windows Job Object 异步回收断言，断言窗口 2 s）：**pre-fix base 同机同跑同样失败**（`logs/pre-fix-pytest-full-baseline.log`），同树 6 次重复 pass/fail 交替（`logs/flaky-plugin-sandbox-reruns.log`），模块级复跑也不稳定（`logs/post-fix-plugin-sandbox-module.log`）；与 `PipelineStore` 改动无调用关系。任务卡发布时的历史基线 3F/2753P/9S 对应 flake 未触发的运行，本卡辅助运行 3F/2761P/9S 与其一致（`logs/post-fix-pytest-full-runA-aux.log`）。
- `tests/pipeline` 定向：**104 passed**。
- `apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <私有>` → **TEST PASS：177/177 passed, 0 skipped**（`test/avalonia-summary.json`、`logs/dotnet-test.log`）。
- 未运行：`vitest`（本卡未改前端/`apps/desktop/frontend`，协议与线格式未变；沿用基线 60/567 结论）。

## 7. AC5 门禁

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/RUN-STORE-CACHE-RACE-FIX-1.md` → 结果见 `check-taskpath.log` 与 §10 交付记录。
- Canonical Evidence：64-hex sha256 pin 见任务卡证据表（commit 列留空，由 DSH 集成时填写）。
- Resource Manifest：`verification/RUN-STORE-CACHE-RACE-FIX-1/resource-manifest.json`。
- Handoff：`doc/handoffs/RUN-STORE-CACHE-RACE-FIX-1-handoff.md`。

## 8. Record Decision：缓存 / 归属模型

- **D1（视图读与执行缓存分离）**：`SqlitePipelineStore.get()` 仍是**执行缓存**（run_id → 唯一 owner 对象，`execute_run`/`_find_step`/`_persist` 共用）；`refresh()` 及 `get_run_snapshot(fresh=True)`/`GetTaskProjection` 是**视图读**，每次读取 DB 生成独立对象，**永不替换/弹出缓存**。理由：投影是只读轮询面，读取频率高于执行提交；让读路径不参与 owner 生命周期是消除数据竞争的最小、可证伪变更。
- **D2（写入归属 + 修订 CAS）**：`run_json` 整份写入前校验"该对象捕获时的 store 修订 == 当前修订"；owner 每次成功写递增修订；旧快照写入被 `STALE_RUN_SNAPSHOT` 拒绝而非静默覆盖。理由：last-writer-wins 是本次"提交被回退"的直接机制，必须显式失败以便尽早暴露任何回归。
- **影响面**：仅 Core 进程内 `PipelineStore` 实现（SQLite + 内存 double）；不改 `run_json`/DB 列/协议/UI/Host。
- **回退开关**：`git revert` 本卡两个文件（`src/infrastructure/sqlite/pipeline.py`、`src/application/tasks/store.py`）即回到修复前行为；无 Schema 迁移、无数据改写，回退无数据风险（缺陷会随 fresh 轮询复现）。
- **限制（必须知悉）**：修订号是**每 store 实例内存状态**，前提是"一个 Core 进程独占一个 data root"（当前产品与协议既有约束）。跨进程/同库多 store 实例的并发写不在本卡范围；若未来出现，应升级为 `run_json` 内持久化修订列 + 迁移。

## 9. 遗留 / 未做

1. **frozen sidecar 未重打包**：发布包中的 `core_service.exe`（sha256 `2b36bfeb…4ec519b`）仍含旧缺陷；修复需经后续打包 Task（`RELEASE-REPACK-1` 重打包）才能随产品发布。与 CORE-PIPELINE-FIX-1 的处理口径一致（PyInstaller 不能原地补丁）。
2. `run_json` 仍是整份序列化；本卡只防"旧快照覆盖新提交"，不做字段级合并（当前无需求）。
3. `GetTaskProjection(fresh=False)` 仍读执行缓存对象（协议既定、只读、无写回）；并发下可能读到执行中的内存中间态，属既有行为，本卡未改变。

## 10. 交付与资源处置

- 交付形态：分支 `task/RUN-STORE-CACHE-RACE-FIX-1` 上的固定 commit（`src/**` 2 文件 + `tests/**` 2 文件 + 本 Task 卡/Handoff + `verification/RUN-STORE-CACHE-RACE-FIX-1/**` 证据）；未 push、未 gc/prune。
- 复验环境：BOOK-FIXTURE-1 `isolated-data` 私有副本（每轮复制、原件零修改）；models 包 `FINAL-VALIDATION-1/.../core-sidecar/models`（只读）；全部数据根与日志写入私有 `G:/CODEX/New Manga.workspace/task-envs/RUN-STORE-CACHE-RACE-FIX-1/**`。
- Resource Manifest 见同名文件；closeout 由 DSH 在集成关闭时复核。
