# FLAKY-PYTEST-1 稳定性报告（3 个长期失败归因与消除）

- Task：`doc/tasks/FLAKY-PYTEST-1.md`（base HEAD `170878dc4`）；Owner `sandbox-verify`（DSH 委派，team task-50）；Reviewer：DSH
- 分支 / worktree：`task/FLAKY-PYTEST-1` / `G:/CODEX/New Manga.workspace/worktrees/FLAKY-PYTEST-1`
- 证据目录：`verification/FLAKY-PYTEST-1/`
- 结论：**基线 3F/2772P/9S 的 3 个失败全部归因并消除**——1 个产品真 bug（Workbench VM `continueRun` 不启动 worker）已修复；2 个同为可选 torch 检测栈的**运行时版本缺口**，改为机器可判定的显式 skip；另把 `test_sandbox_job_kills_grandchildren` 的 2 s 固定窗口改为 20 s 有界等待（OS Job Object 异步回收，不掩盖泄漏）。处理后**连续 5 次**全量 pytest 结果完全一致：**0 failed / 2773 passed / 10 skipped**（EXIT=0）；`test.ps1` **225/225**；vitest **60 files / 567 tests** 不变。

---

## 1. AC1 基线与逐个归因

基线（修复前，未改动 base `170878dc4`，`logs/run0-baseline.log`）：**3 failed / 2772 passed / 9 skipped**，失败名单：

| # | 失败测试 | 归因类别 | 结论 |
|---|---|---|---|
| 1 | `tests/providers/test_detection_manga_real.py::test_real_detection_returns_block_candidates` | **环境（可选运行时版本缺口）** | 非产品回归；显式 skip |
| 2 | `tests/providers/test_detection_manga_real.py::test_real_blank_page_yields_zero_candidates` | **环境（同上，同模块同根因）** | 非产品回归；显式 skip |
| 3 | `tests/workbench/test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately` | **真 bug（产品 UI 视图模型）** | 修复 `continueRun` |
| 观察项 | `tests/infrastructure/test_plugin_sandbox.py::test_sandbox_job_kills_grandchildren` | 并发/OS 时序 flaky（基线通过，负载下偶发） | 测试窗口 2 s→20 s 有界等待 + 说明 |

### 1.1 失败 1/2：可选 torch 检测栈版本缺口（不是产品 bug）

最小重跑（pre-fix base，`logs/ac1-prefix-detection.log`）：`2 failed`，根因链固定可判：

```text
AttributeError: module transformers has no attribute RTDetrV2ForObjectDetection
  -> ports.providers.errors.ProviderError: PROVIDER_FAILED: manga detector engine failed to load
     from .../ogkalu-comic-text-and-bubble-detector: AttributeError(...)
     at src/infrastructure/providers/detection_manga.py:535
```

机器可判定事实（`logs/ac1-env-probe.log`）：

| 事实 | 值 |
|---|---|
| 本机 `transformers.__version__` | **4.48.3** |
| `hasattr(transformers, "RTDetrV2ForObjectDetection")` | **False**（该类 4.49 才引入） |
| `requirements.txt` pin | **`transformers==5.17.0`**（torch==2.14.0） |
| snapshot `config.json` | `architectures=["RTDetrV2ForObjectDetection"]`、`model_type=rt_detr_v2`、`transformers_version=4.49.0` |
| 产品默认检测后端 | **ONNX**（`detection_manga_onnx.py`）；torch 适配器自 CORE-SLIM-2 起为可选 fallback（`requirements.txt` 注释原文） |

判定：这是 **dev venv 落后于仓库 pin** 的环境缺口（torch 2.11.0+cu128 vs pin 2.14.0；transformers 4.48.3 vs pin 5.17.0），不是产品缺陷；随包 Core 走 ONNX 不受影响。原测试文件本就以 `pytest.importorskip(...)`/`pytest.skip(...allow_module_level=True)` 处理环境缺失，本次按同一风格补齐**版本可判定**的 skip。

### 1.2 失败 3：真 bug——`continueRun` 不启动 worker（产品 UI 视图模型）

最小重跑（pre-fix base，`logs/ac1-prefix-workbench-pause.log`）：**3/3 稳定失败**（本机），失败点为暂停后 `continueRun()` 15 s 内 run 到不了 `completed`（`tests/workbench/test_workbench_viewmodel.py:210`）。

根因（代码级）：

- `PipelineService.control_run(run_id, "continue")` 对 `PAUSED` run 的实际动作是：清 `pause_requested`、把 **`run.status` 置 `RUNNING`**、把 run_id 记入 `_resumed_runs`（等待执行器再入），并返回 `ControlResult(status=PENDING)` —— **"PENDING" 是控制契约里"请起 worker"的应答**（`src/application/tasks/service.py:1030-1036`）。
- `WorkbenchViewModel.continueRun()` 却按 **`self._run.status is PipelineRunStatus.PENDING`** 才调用 `_start_pending_worker`（`src/ui/viewmodels/workbench/viewmodel.py:956` 起）。`continue` 之后 run.status 是 `RUNNING`，条件永假 → **worker 永不启动**，run 停在 RUNNING，`wait_until(completed)` 超时。
- 修复：以控制结果 `result.status is PENDING` 作为 worker 准入信号（仅此一处判定；`restart/abandon/retry` 路径不变）。

### 1.3 观察项：`test_sandbox_job_kills_grandchildren`

- 该测试断言"关闭 Job Object 后孙进程被杀"，原实现用 **固定 2 s 窗口**（20×0.1 s）。Windows 的 job 回收是**异步**的，负载高时通知延迟可能超过 2 s。
- 隔离探针（`tools/probe_sandbox_tree.py`，直接调用生产 `AppContainerSandbox`，6 次；`logs/ac1-sandbox-probe.log`）：孙进程 **6/6 均在 ~20 ms 内死亡**，无泄漏；本任务基线全量运行与 6 次单测重跑（`logs/ac1-sandbox-single-6x.log`）均通过 → 判定为**测试时序 flake**，非产品泄漏。
- 处置：保留严格断言，改为**20 s 有界等待**（死亡即通过；真正泄漏仍会失败），并在注释中记录依据（见 `tests/infrastructure/test_plugin_sandbox.py`）。不引入无上限重试、不静默跳过。

---

## 2. AC2 处置清单

| 文件 | 改动 | 类别 |
|---|---|---|
| `src/ui/viewmodels/workbench/viewmodel.py` | `continueRun()` 以 `result.status is PENDING` 启动 pending worker；注释记录 FLAKY-PYTEST-1 根因 | **真 bug 修复**（产品 UI VM，未改协议/持久化语义） |
| `tests/providers/test_detection_manga_real.py` | 在 module 级 `importorskip` 后新增 `hasattr(transformers, "RTDetrV2ForObjectDetection")` 判定；缺失时 `pytest.skip(..., allow_module_level=True)`，reason 含：本机实际版本、所需类、`requirements.txt` pin、修复方式 | **环境依赖 → 显式 skip（机器可判定 reason）** |
| `tests/infrastructure/test_plugin_sandbox.py` | 2 s 固定窗口 → 20 s 有界等待 + 时序依据注释 | **并发/OS 时序 flaky → 有界等待，断言不放宽** |

禁止项核对：未改协议/Host 契约/旧壳；未改持久化或 Run 语义；无静默 skip（所有 skip 均打印可判定原因，见 §4 skip 集合）；未引入无上限 retry。

## 3. AC3：连续 5 次全量 pytest（顺序执行、无并行负载）

`tools/run_five.py`（记录头含 git head/status、EXIT 码；原始日志 `logs/run1..5-pytest.log`，汇总 `ac3-five-runs.json`）：

| 运行 | 命令 | 结果 | EXIT | 耗时 |
|---|---|---|---|---|
| run 1 | `python -m pytest tests -q` | 0 failed / 2773 passed / 10 skipped | 0 | 219.7 s |
| run 2 | 同上 | 0 failed / 2773 passed / 10 skipped | 0 | 227.8 s |
| run 3 | 同上 | 0 failed / 2773 passed / 10 skipped | 0 | 210.3 s |
| run 4 | 同上 | 0 failed / 2773 passed / 10 skipped | 0 | 204.1 s |
| run 5 | 同上 | 0 failed / 2773 passed / 10 skipped | 0 | 204.3 s |

- `distinct_results = [[0, 2773, 10]]`，`consistent = true`。
- 总数核对：基线 3F+2772P+9S = 2784 项；处理后 2773P+10S = 2783 项，差 1 = 检测模块级 skip 把 2 个用例合并为 1 个 collection 级 skip（与文件原有 `allow_module_level` 风格一致）。
- 另有一次 `-q -rs` 全量运行（`logs/run6-skipset.log`）：2773 passed / 10 skipped / EXIT=0，用于固化 skip 集合（§4）。

## 4. 稳定 skip 集合（10 项，均可判定、非静默）

| # | 位置 | reason（原文摘要） |
|---|---|---|
| 1 | `tests/providers/test_detect_seam_t111.py:15` | docTR (python-doctr) is not installed |
| 2 | `tests/providers/test_detection_doctr_real.py:11` | docTR (python-doctr) is not installed |
| 3 | `tests/providers/test_detection_manga_real.py:30` | **本任务新增**：installed transformers 4.48.3 has no RTDetrV2ForObjectDetection; needs >=4.49 (requirements pins 5.17.0) |
| 4 | `tests/network/test_connection_tester.py:106` | openssl unavailable |
| 5 | `tests/network/test_transport_tls.py:39` | openssl unavailable |
| 6 | `tests/network/test_transport_tls.py:47` | openssl unavailable |
| 7 | `tests/network/test_transport_tls.py:62` | openssl unavailable |
| 8 | `tests/network/test_transport_tls.py:69` | openssl unavailable |
| 9 | `tests/network/test_transport_tls.py:83` | openssl unavailable |
| 10 | `tests/providers/test_registry_readiness.py:274` | dev venv intentionally carries ML stack …（既有说明性 skip） |

说明：本机未安装 openssl / python-doctr 属既有环境缺口（原本即稳定 skip，非本任务引入）；唯一新增 skip 为第 3 项，原因是已判定的版本缺口。

## 5. AC4 回归

- `apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <私有>` → **TEST PASS (Debug): 225/225 passed, 0 skipped**（`test/avalonia-summary.json`、`logs/ac4-dotnet-test.log`；coreclient 40 / host 76 / app 109）。
- `npx vitest run`（`apps/desktop/frontend`）→ **Test Files 60 passed (60)，Tests 567 passed (567)**，EXIT=0（`logs/ac4-vitest.log`）。
  说明：本卡 worktree 无 `node_modules`（依赖不入库），vitest 在主 checkout 的同一 `apps/desktop/frontend` 上运行；两树 frontend tracked 源零 diff（本卡只改 Python `src/ui` 与 tests），结果等价。
- 未运行：frozen sidecar 重打包（无产品闭包变化；`src/ui` 为 legacy shell 视图模型，不入随包 Core 闭包，见 AD-002/CORE-SLIM 结论）。

## 6. AC5 门禁

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FLAKY-PYTEST-1.md` → PASS（`check-taskpath.log`）。
- 64-hex sha256 pin：见任务卡 `## Canonical Evidence`（pin 口径=提交内 blob 字节，commit 列=包含该文件的交付/证据提交）。
- Handoff：`doc/handoffs/FLAKY-PYTEST-1-handoff.md`；Record Decision（flaky 政策）见 §8。
- Resource Manifest：`verification/FLAKY-PYTEST-1/resource-manifest.json`。

## 7. 源码改动

`git diff 170878dc4 -- src tests`（`src-changes-vs-base.patch`）：3 文件，+36/−4；无协议/DB/打包/依赖变更。

## 8. Record Decision：flaky 测试政策

以后遇到长期红/偶发红，按以下顺序处置（本卡即模板）：

1. **先归因，禁止直接 skip 掩盖**：给出最小重跑（含 EXIT 与命令头）+ 机器可判定证据（版本、文件存在性、能力探测、进程/时序实测）。
2. **真 bug → 修产品/测试逻辑本身**，并在代码注释与报告写明根因链（本卡失败 3：控制契约 `ControlResult.status` vs Run 状态的判定错位）。
3. **环境依赖 → 显式 skip，且 reason 必须机器可判定**：包含"实际值 vs 需求值 + 修复指引"（例：`installed transformers 4.48.3 has no RTDetrV2ForObjectDetection; needs >=4.49 (requirements pins 5.17.0)`）。禁止 `try/except: pytest.skip()` 吞错、禁止无 reason 的空 skip；skip 必须出现在 `-rs` 输出中可审计。
4. **并发/OS 时序类 → 有界等待 + 严格断言**：给出实测分布与上界依据（本卡：生产 sandbox 实测 ~20 ms 死亡，窗口取 20 s 上限），死亡/成功即通过，真实违规仍失败；禁止无上限重试或"失败重跑直到绿"。
5. **稳定性门槛**：处置后必须连续 5 次全量运行结果一致，并记录原始日志（含 EXIT），不得只报汇总结论。
6. **环境 pin 漂移不静默**：dev venv 落后 `requirements*.txt` 时，skip 是测试侧的诚实表达；是否重建 venv/升级 pin 由 DSH 决策，不在本卡范围（见 §9）。

## 9. 遗留 / 建议

1. **本机 dev venv 落后要求 pin**：transformers 4.48.3（pin 5.17.0）、torch 2.11.0+cu128（pin 2.14.0）。建议 DSH 决策：`pip install -r requirements-dev.txt` 后重跑两个 detection 测试（当前 skip 会自动转为真跑）或明确接受 optional fallback 不可用。**本卡未改动机器环境**。
2. `test_sandbox_job_kills_grandchildren` 的 20 s 上界为经验值（实测 ~20 ms）；若未来仍复现，应作为独立诊断卡（AppContainer/job 语义）而非继续放大窗口。
3. 5 次运行均为**单机顺序**执行（记录中 git head 固定为 `170878dc4` + 本卡工作树改动）；并行跑 pytest 不在本卡证据口径内。
4. 本卡未改随包 Core 闭包（`src/ui` legacy VM 不入 sidecar），无需重打包。
