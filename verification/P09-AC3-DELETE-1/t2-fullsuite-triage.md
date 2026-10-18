# T2：全量 Python 测试 4 项失败的定性（Coordinator 独立复跑）

- **执行者**：Coordinator = dsh，epoch **8**（lease `39640ba370ec4a7cade35c1abd67f234`）
- **执行时间**：2026-10-18 16:33–16:47（Asia/Shanghai）
- **触发**：交接文件 §3 **T2** —— "定性全量 Python 测试的 4 个失败是否由 P09 引起"
- **方法**：**独立临时 worktree** `G:\CODEX\New Manga.workspace\P09-BASELINE-T2`（detached），**未在用户工作区做任何 `stash` / `reset` / `checkout`**
- **解释器**：`G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe`
- **命令**：`python -m pytest tests -q -p no:cacheprovider -rf --tb=line`（worktree 内独占执行，未被管道包裹）

## 1. 前置验证：worktree 确实隔离

在 worktree 内实测 import 解析：

```
sys.path.insert(0, r'...\P09-BASELINE-T2\src')
import infrastructure.sqlite.connection
-> __file__ = G:\CODEX\New Manga.workspace\P09-BASELINE-T2\src\infrastructure\sqlite\connection.py
```

且 `grep 'G:\CODEX\New Manga'` 在 `tests/**/*.py` 中命中 **0** 次，无硬编码仓库路径。→ 基线实验测的是 worktree 自身代码，不是用户工作区。

## 2. 三个基线的全量结果

| 基线 | commit | 说明 | 结果 |
|---|---|---|---|
| **PRE-P09** | `fdf715e7913798e4c220b09c41d288abdde69b1c` | 等于 `d9f7a628c^`（P09 实现前） | **13 failed, 2245 passed, 7 skipped**（175.30 s） |
| **HEAD~1** | `e99791f927d109b07634c8f7e628f5c52b887ffe` | 含 P09 实现，不含 R2 修复 | **4 failed, 2268 passed, 7 skipped**（182.11 s） |
| **HEAD** | `a04e4ea78d5b33a0f91efcdc06b396391c4b165e` | 含 R2 修复 | 4 failed, 2273 passed, 7 skipped（交接记录；本轮未重跑全量，见 §4 bisect 复跑） |

## 3. 失败集合差异

**只在 PRE-P09 失败（即在该区间被修复，共 10 项）**：

```
tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py::test_ac2_continue_passes_stale_and_missing_distinguishable
tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py::test_ac2_history_records_which_stale_pages_were_included
tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py::test_ac2_stale_abort_fail_closed_zero_side_effects
tests/pipeline/test_pipeline_production_seam.py::test_production_service_round_trips_and_recovers_without_fake_executor
tests/pipeline/test_pipeline.py::test_pause_is_safe_boundary_and_continue_reuses_completed_step
tests/pipeline/test_pipeline.py::test_recover_continue_restart_and_abandon_have_distinct_crash_semantics
tests/pipeline/test_regionless_rebinding.py::test_n7_detect_committed_then_interrupted_then_plan_continue
tests/reading_export/test_export.py::test_translated_export_can_explicitly_continue_with_existing_versions
tests/reading_export/test_export.py::test_translated_export_with_stale_pages_is_refused_by_default
tests/reading_export/test_reading.py::test_stale_translated_flagged_with_message
```

**两个基线都失败（与 P09 无关，共 3 项）**：

```
tests/workbench/test_projection.py::test_pending_run_all_waiting_and_pause_stop_enabled
tests/workbench/test_projection.py::test_button_matrix_all_statuses
tests/workbench/test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately
```

**只在 P09 之后失败（P09 引入，共 1 项）**：

```
tests/packaging/test_frozen_runtime_contract.py::test_explicit_data_root_isolation
```

> 注：PRE-P09 → HEAD~1 之间同时包含 P09 实现（`d9f7a628c`、`e44a589a0`）与 P20-CLOSE-BOUND-1 的 4 轮提交（`41bb13679`…`835f4bb17`），因此"10 项被修复"不能单独归因于 P09；**唯一需要归因的是那 1 项新增失败，故做 bisect**。

## 4. Bisect：定位唯一新增失败的引入者

在同一 worktree 逐点 `checkout --detach` 后，对四个相关测试文件独占复跑
（`tests/packaging/test_frozen_runtime_contract.py`、`tests/workbench/test_projection.py`、`tests/workbench/test_workbench_viewmodel.py`）：

| commit | 说明 | 结果 |
|---|---|---|
| `fdf715e79` | PRE-P09 + PRE-P20-R4 | **3 failed, 58 passed** ← `test_explicit_data_root_isolation` **通过** |
| `d9f7a628c` | **P09 实现提交 1** | **4 failed, 57 passed** ← 该测试**首次失败** |
| `e44a589a0` | P09 实现提交 2 | 4 failed |
| `41bb13679` | P20-CB R4 | 4 failed |
| `7ee8b2639` | P20-CB evidence | 4 failed |
| `835f4bb17` | P20-CB R6 | 4 failed |
| `e99791f92` | HEAD~1 | 4 failed |
| `a04e4ea78` | HEAD（P09 R2 fix） | 4 failed |

**结论：该失败由 `d9f7a628c`（P09 首个实现提交）引入，自此在后续 6 个提交中持续失败。**

## 5. 根因

`tests/packaging/test_frozen_runtime_contract.py:67-71`：

```python
# Verify schema version is current (v4)
ver = services.conn.execute(
    "SELECT CAST(value_json AS INTEGER) FROM application_metadata WHERE metadata_key='schema_version'"
).fetchone()[0]
assert ver == 4
```

P09 将 Schema 由 **v4 升到 v5**（新增 `book_cleanup_manifests`、解除 pipeline 表对 `pages` 的物理外键），断言硬编码 `ver == 4` 随之失效。

**同源问题此前已出现过一次**：`doc/tasks/P09-AC3-DELETE-1.md` 的 Coordinator 复核记录载明 `tests/core/test_bootstrap.py::test_assemble_services_injects_and_exports_diagnostics` 亦断言 `schema_version == "4"`，当时已派最小范围修正，并要求"**全仓搜索其他硬编码** + 重跑全量"。该要求未被执行到位 —— 本文件即遗漏项。

## 6. 对 T1 与 AC 判定的影响（如实记录）

1. **这是 P09 引入的真实回归**，不是环境噪声；Codex 第三轮复审报告明确写了"**pytest … NOT_RUN**，本轮依据源码和现有测试断言静态复核"，因此该回归**未进入 R3 的 finding 表**。
2. 按用户 T1 指令"若仍有阻断项 → 如实上报，不自行加轮"，本结论**不触发新的复审轮次**，仅作为决策输入上报。
3. P09 已使用 R1fix、R2fix **两次返修**，R3 仍为 `changes_requested` → 已达 **DIR-4**"同一失败面最多 2 次返修"上限，第三次修复须用户显式授权。
4. 因此：**P09 的 AC3 不得由 BLOCKED 翻为 PASS；P09-AC3-DELETE-1 不得收口。**

## 7. 证据与可复现性

| 文件 | sha256 | bytes |
|---|---|---|
| `t2-logs/P09-BASELINE-PRE-fullpytest.log` | `d4df686fea639f37987c0bad65f10371ab5aa837b4ec6b58def370d9948c9807` | 63070 |
| `t2-logs/P09-BASELINE-T2-HEADminus1-fullpytest.log` | `ab0717aad6f6ad9545a436ca7443453250c4e8f81bc46afcd703c78ff3de05d5` | 58666 |
| `t2-logs/P09-T2-bisect.log` | `f962a032b9d8668aec09eafe8324808547ed9ab2fc4cc1b81874ee74a726eb22` | 1956 |

全部 `sha256` 取自**磁盘真实字节**（`Get-FileHash -Algorithm SHA256`）。

**复现步骤**：

```powershell
$wt = 'G:\CODEX\New Manga.workspace\P09-BASELINE-T2'
$py = 'G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe'
git -C $wt checkout --detach fdf715e79   # 或任一上表 commit
Set-Location $wt
& $py -m pytest tests -q -p no:cacheprovider -rf --tb=line
```

**未执行的动作（如实声明）**：本轮未在用户工作区做 `stash` / `reset` / `checkout`；未修改任何产品代码、测试或契约；未删除或移动任何文件；未 `git add` / `commit` / `push`。worktree 为新建，保留待后续复用或由用户决定处置。
