# SCHEDULER-THREAD-DIAG-1 诊断报告（只诊断，未改任何产品源码）

- Task: `doc/tasks/SCHEDULER-THREAD-DIAG-1.md`（base `97de0fa99`；诊断时 HEAD `ae7fe3334`）
- Owner: `baseline-scout`（DSH 委派，team task-38）
- 证据目录: `verification/SCHEDULER-THREAD-DIAG-1/`
- 结论: **CONFIRMED —— `SqlitePipelineStore` 的进程内共享可变缓存 `_cache[run_id]` 被 `GetTaskProjection` 的 `fresh=True` 路径（`store.refresh`）从请求线程替换成"新加载的克隆"，执行线程 `execute_run` 仍持有旧对象继续跑；`commit_step_result/_find_step` 走缓存拿到克隆提交，旧对象后续 `_persist` 又把提交前状态整体写回 `pipeline_runs.run_json`。** 复现稳定，且**已发布 frozen sidecar 同样存在**。

---

## 1. AC1 最小复现（线程 / 事务 / 连接路由）

### 复现方式
`tools/repro_scheduler.py`：与 `python -m bootstrap.core_service` 同拓扑（`assemble_production_core` + `CoreServiceServer` + `_start_run_scheduler()` 的真实 `core-run-scheduler` 线程 + `accept_start_run`，即 StartRun 处理器所做的事），随后每 100 ms 轮询一次：

| 变量 | 轮询方式 | 结果 |
| --- | --- | --- |
| `projection-fresh` | `pipeline.get_task_projection(run_id, fresh=True)`（= `GetTaskProjection` RPC 的等价调用） | **复现**：detect StepRun 卡 `running`（8 页中 7–8 个），下游 regionless `ocr` 报 `INVALID_INPUT: step 'ocr' requires a Region target`，8 页任务全失败；`regions=26` 已生成 |
| `projection-cached` | `fresh=False`（只读缓存，不 refresh） | 干净：detect 8/8 completed，ocr 3/3、color 3/3、term_extract 3/3 completed；5 页 completed，3 页仅止于 `translate` typed `PROVIDER_NOT_CONFIGURED`；0 卡 running |
| `none` | 不轮询 | 与 `projection-cached` 完全一致（干净） |

**触发条件唯一**：执行期间有 `GetTaskProjection`（`fresh=True` → `store.refresh`）。`GetRunSnapshot` 在 Core 进程内 `fresh=self._serving and not self._run_owner` = False，不触发。

### 线程与连接路由（实测）
| 线程 | 共享 facade（`ThreadRoutedConnection` 对象） | 本线程真实 `sqlite3.Connection` |
| --- | --- | --- |
| `MainThread`（stdio/请求线程） | `0x22f0088fcb0` | `0x22f7f74a6b0` |
| `core-run-scheduler`（执行线程） | `0x22f0088fcb0`（同一 facade） | `0x22f00a4e4d0`（另一个连接） |

结论：**连接路由本身正确**（每线程独立 sqlite 连接，`write_in_current_transaction` 在调度线程上 `in_tx_before=true`、提交后 `applied`）；**泄漏点不是连接，而是未按线程隔离的 `_cache`（普通 dict）**。事务侧证据：`catalog.commit_step` 在调度线程 `BEGIN IMMEDIATE → persist() → commit`，`store.write_in_current_transaction` 观测 `in_tx_before/after = true,true`，`catalog.commit_step.exit status=applied`（见 `source-projection-fresh.json` 的 `store.*`/`catalog.*` 事件）。

---

## 2. AC2 根因（可判定因果链，页 1 `f52f2772`）

| t (ms) | 线程 | 事件 | 关键字段 |
| --- | --- | --- | --- |
| 619 | core-run-scheduler | `_record_step_attempt`（detect） | 执行线程本地 run 对象 `0x...9d7230` |
| 663/764/865/1975/2304 | MainThread | `store.refresh.CACHE-REPLACED` ×5 | 每次 `_cache[run_id]` 被替换成新克隆（`before_vector=[["detect","running"]]`） |
| 2349 | core-run-scheduler | `_find_step` → `commit_step_result` | 返回克隆 `0x...107e580`（**≠** `0x...9d7230`）；`_backfill_detected_regions.exit task_units=105`（回填只落在克隆上） |
| 2355 | core-run-scheduler | `catalog.commit_step.exit` | `applied`（DB 曾正确写入 detect completed + 回填后的 units） |
| 2359 | core-run-scheduler | `_record_step_attempt`（ocr） | **run_obj 仍是 `0x...9d7230`**（旧对象，`task.units` 未回填 → regionless） |
| 2405 | MainThread | `store.refresh` 读到 DB | `before_vector=[detect running, ocr failed, detect running]` → 旧对象后续 `_persist` 把提交前状态写回 → **StepRun 回退为 `running`** |

### 根因一句话
`SqlitePipelineStore` 把 `PipelineRun` 缓存在**跨线程共享的普通 dict**（`_cache`）里；`refresh()`（`get_run_snapshot(fresh=True)` → `GetTaskProjection`）读取 DB 后执行 `self._cache[run_id] = run` **替换对象**。执行线程 `execute_run` 的局部 `run` 不变：

1. **提交落到克隆**：`commit_step_result → _find_step → store.get()` 读缓存拿到克隆，detect 的 commit + `_backfill_detected_regions` 只更新克隆；
2. **执行循环仍用旧对象**：旧对象的 `task.units` 没有 region 回填 → 下一个 unit 是 regionless `ocr` → `INVALID_INPUT: step 'ocr' requires a Region target`；
3. **旧状态回写**：旧对象随后的 `_persist` 把整份 `run_json` 写回 DB（last-writer-wins）→ 已提交的 `completed` 被覆盖成 `running`，形成"卡 running"观感。

代码点（均为既有代码，未改）：
`core_service.py:3236 _cached_task_projection`（`GetTaskProjection → get_task_projection(fresh=True)`）→ `service.py:1394 get_run_snapshot`（`store.refresh`）→ `infrastructure/sqlite/pipeline.py:415 SqlitePipelineStore.refresh`（`self._cache[run_id] = run`）→ `service.py:1531 _find_step`（`store.get` 走缓存）→ `service.py:1454 _persist`（整 run JSON 写回）。

---

## 3. AC3 影响面（真实产品路径）

1. **已发布 frozen sidecar 同样存在**：`tools/probe_frozen.py` 直接启动 models 包里的 `core_service.exe`（sha256 `2b36bfebcf09ea118537a0bc77a6c7c9a47c8845d7a853bc60d56ed004ec519b`，未修改），同一数据根 + 同一请求：
   - `frozen-projection-polling.json`：detect 3 个卡 `running`、3 个 `ocr` regionless `INVALID_INPUT`、8/8 任务失败（另有 5 个旧语义下的空页 `INVALID_INPUT`）；
   - `frozen-snapshot-only.json`（对照）：0 卡 running、3 个 `ocr` completed；
   → **frozen 二进制确认含该竞态**。
2. **当前 Avalonia GUI 是否在 Run 中轮询**：`library_get_task_projection` 已接线（`apps/desktop-avalonia/src/NewManga.App/Shell/ReaderWorkbenchSupport.cs:195`、`NewManga.CoreClient/Commands/HostCommandRegistry.cs:102/147`、`HostCommandDispatcher.cs:214`），但 **当前没有任何 viewmodel/timer 调用点**（全仓 grep 仅注册/接线/测试），即**现状 GUI 不会主动触发**；而 Host 集成测试（`RunBindingFixTests.cs:390`）与诊断/验收工具会调用。
3. **判定**：`shipped binary 含 latent 缺陷`；产品 Run 页面一旦按协议接入投影轮询（Workbench 投影轮询是协议既定用法），或任何客户端在 Run 执行期间调 `GetTaskProjection`，即稳定复现。**必须在投影轮询落地前修复**；`RELEASE-REPACK-1` 重打包不能等它自愈。

---

## 4. AC4 建议（最小修复，不改 Core 语义）

1. **最小改动（首选）**：让"视图读取"不再改写执行缓存——`get_run_snapshot(fresh=True)`/`store.refresh()` 返回**独立读取结果**，不执行 `self._cache[run_id] = run`（或为 `GetTaskProjection` 增加只读路径 `read_only=True`）。该单点修改即可消除本竞态的"克隆替换"，且不改任何 Run/Step 语义。
2. **加固（建议同 Task 完成）**：`pipeline_runs.run_json` 是整份 last-writer-wins；建议对执行写加 owner/线程约束（非执行线程不得 `put` 运行中 run），或加 `updated_at`/`revision` CAS，防止旧快照覆盖新状态。
3. **回归测试**：一个线程 `execute_run`，另一线程以 100 ms 轮询 `get_task_projection(fresh=True)`；断言 run 终态无 `running` StepRun、无 regionless unit 的 `INVALID_INPUT`。
4. 建议新 Task：`RUN-STORE-CACHE-RACE-FIX-1`（implementation，小改 Core，含并发回归测试）；本诊断任务不再动源码。

---

## 5. AC5 门禁

- `check.ps1 -TaskPath doc/tasks/SCHEDULER-THREAD-DIAG-1.md`：PASS（见交付记录）。
- Canonical Evidence：64-hex sha256 pin、commit 列留空；Resource Manifest 指向 `verification/SCHEDULER-THREAD-DIAG-1/resource-manifest.json`。
- 只读约束：未改任何 `src/**` 产品源码（诊断脚本仅在 task-env，用运行时 monkeypatch 采集仪表）；未 push、未 gc/prune。
