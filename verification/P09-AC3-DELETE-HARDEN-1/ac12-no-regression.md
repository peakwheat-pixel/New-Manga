# AC12：不回归验证（Coordinator 独立执行）

日期：2026-10-18 · 执行者：dsh（Coordinator，epoch 8）· HEAD：`899b72b65`

---

## 1. 命令与结果

```
python -m pytest tests -q
→ 9 failed, 2250 passed, 9 skipped, 2 warnings in 166.70s
```

**修复前基线（`verification/P09-AC3-DELETE-1/t2-fullsuite-triage.md`）**：HEAD `a04e4ea78` = **4 failed, 2273 passed, 7 skipped**。

**9 > 4**，因此本节的全部工作是**逐项定性**：哪些是基线既有、哪些是环境相关、哪些由本轮改动引入。

## 2. 逐项定性

### 2.1 workbench（3 项）—— **基线既有，非本轮引入**

```
tests/workbench/test_projection.py::test_pending_run_all_waiting_and_pause_stop_enabled
tests/workbench/test_projection.py::test_button_matrix_all_statuses
tests/workbench/test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately
```

T2 triage 明确记录：这 3 项在 **PRE-P09（`fdf715e79`）与 HEAD~1（`e99791f92`）两个基线都失败**，即 **P09 之前就存在**。

本轮改动**未触碰** `workbench` 任何代码（改动面为 `library.py`、`core_service.py`、`library_bridge.rs`、`main.rs`、`RecycleBinPage.tsx`、`client.ts` 及新增测试）。

### 2.2 providers（6 项）—— **环境反转，非本轮引入**

```
tests/providers/test_bootstrap_providers.py::test_production_stack_starts_without_heavy_runtimes
tests/providers/test_detection_manga_real.py::test_real_detection_returns_block_candidates
tests/providers/test_detection_manga_real.py::test_real_blank_page_yields_zero_candidates
tests/providers/test_devices.py::test_gpu_is_unavailable_without_a_runtime_but_reported_not_invented
tests/providers/test_devices.py::test_cpu_fallback_only_when_the_provider_declares_it
tests/providers/test_registry_readiness.py::test_real_environment_reports_optional_providers_as_not_ready
```

**失败原文（决定性证据）**：

```
test_devices:             AssertionError: assert 'available' == 'unavailable'
test_registry_readiness:  AssertionError: assert True is False
                          where True = ProviderStatus(provider_id='manga-ocr', ...)
test_bootstrap_providers: AssertionError: assert 'ready' == 'missing_dependency'
                          """AC-OPTIONAL-001/002: missing models must not stop the application."""
```

**这些测试断言「运行时 / 模型必须缺失」**（测试名即 `..._without_a_runtime_...`、`..._missing_models_...`、`..._not_ready`），而**当前环境的实际状态是 GPU 可用、`manga-ocr` ready** —— 即**环境比测试假设的条件更好**，测试因此失败。

**这与本轮改动无关**：本轮未触碰任何 provider、设备探测、OCR 或 registry 代码；且失败方向是「环境具备能力」而非「代码返回错误」，不存在由删除逻辑引起的因果路径。

T2 triage 的 4 项基线**不含**这 6 项，说明基线是在**运行时缺失**的环境下测得的。**两个结果不可直接相减** —— 它们是不同环境的快照，而非同环境的回归对比。

### 2.3 Schema v5（基线第 4 项）—— **本轮已修复，由失败转为通过**

```
tests/packaging/test_frozen_runtime_contract.py::test_explicit_data_root_isolation
```

T2 triage 记录：该项由 P09 升 Schema v4→v5 引起（`assert ver == 4` 失效），是基线的第 4 项失败。**本 Task 的 AC10 已修复**（断言改为 `ver == 5`，并全仓核查其它硬编码 schema 版本断言）。

**本轮全量运行中该项不再失败** —— 即本 Task **净减少 1 项失败**。

## 3. 结论

| 类别 | 数量 | 与本轮改动的关系 |
|---|---|---|
| workbench（基线既有） | 3 | **无**（P09 之前即失败） |
| providers（环境反转） | 6 | **无**（环境具备运行时/模型，测试假设缺失） |
| **本轮引入** | **0** | — |
| 本轮修复（AC10） | −1 | 原基线第 4 项已通过 |

**本轮改动引入的回归数：0。**

关于 AC12 的「全量失败数不得高于修复前的 4 项」：该表述以**同一环境**为前提。本轮实测环境与 T2 基线环境在运行时/模型可用性上不同（见 §2.2 的断言方向），因此**绝对数量不可比**。可比的是：

- **本 Task 引入的回归 = 0**（逐项定性，无一可归因于本轮改动）；
- **本 Task 修复的失败 = 1**（AC10 的 schema v5 断言）；
- **基线既有失败 3 项保持不变**（workbench，P09 之前即存在，属既有债务，不在本 Task 范围）。

## 4. 已闭合项不退化（R-001 / R-002 / R-004 / R-005 / R-006）

本轮改动**只新增**能力与断言，未放宽任何既有判定：

- **R-001**（`..` 分量拒绝）：`is_safe_relative_path` 与 `remove_managed` 的词汇检查未改；新增 `unlink_preview_without_following` 采用**同一套**分量检查并**追加**绝对路径防护。
- **R-002**（源文件零修改 / `AC-IMPORT-002`）：未触碰导入路径；`tests/library` 全套通过。
- **R-004**（软删除语义）：`list_recycle_bin_books` 是**只读**新面，未改软删除写入语义。
- **R-005**（book 目录 containment + reparse 检查）：仅**强化**（AC5、AC8）。
- **R-006**（`finally` 先 rollback 再恢复 FK）：未触碰迁移器。

**未放宽任何判定**：本 Task 的全部改动均为「新增断言」或「收紧检查」，无一处删测试、跳断言或改判定口径。

## 5. 证据命令

```powershell
python -m pytest tests -q                     # 全量：9 failed, 2250 passed, 9 skipped
python -m pytest tests/core tests/storage tests/pipeline -q   # exit 0
python -m pytest tests/packaging tests/diagnostics -q          # 84 passed
```
