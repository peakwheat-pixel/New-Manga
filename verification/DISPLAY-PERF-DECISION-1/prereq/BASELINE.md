# P4 测试基线记录（AD-002 前置件）

Status: BASELINE_ESTABLISHED · Date: 2026-10-26 · Commit: `63ec54527` · 环境：Windows 11 26300 / Python 3.14.6 / node 24.15.0 / .NET SDK 9.0.308 + 10.0.401

## 1. 后端 pytest 基线

命令：`python -m pytest -q --tb=no`（仓库根，`pytest.ini testpaths=tests`）

```
4 failed, 2686 passed, 9 skipped, 2 warnings in 261.23s (0:04:21)
```

**既有失败（4，记为基线，不得视为新回归）**：

| 测试 | 备注 |
|---|---|
| `tests/providers/test_detection_manga_real.py::test_real_detection_returns_block_candidates` | 真实检测（可能依赖模型权重/环境）——S1/S2 内 triage |
| `tests/providers/test_detection_manga_real.py::test_real_blank_page_yields_zero_candidates` | 同上 |
| `tests/workbench/test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately` | 工作台 VM 时序 |
| `tests/workbench/test_workbench_viewmodel.py::test_stop_cancels_running_job` | 工作台 VM 取消 |

**门禁口径**：后续 Task 以「**无新增失败、无新增 skip**」判定；新增 skip 必须写原因。上述 4 个失败在 triage 前保持登记。

## 2. 旧前端 vitest 基线

命令：`npx vitest run`（`apps/desktop/frontend`）

```
Test Files  60 passed (60)
Tests       567 passed (567)
Duration    ~15s（collect 299s，环境首跑）
exit code   0
```

**门禁口径**：S5 之前旧壳必须保持 60/60 文件、567/567 用例通过。

## 3. 新壳 dotnet 基线

- 目前**无** `apps/desktop-avalonia/` 工程 → 基线为空；S1 创建后建立：`dotnet build -warnaserror` + `dotnet test`（xunit + Avalonia.Headless）。

## 4. 参考基线（S0 spike，GO）

来源：`verification/DISPLAY-PERF-DECISION-1/spike/SPIKE_REPORT.md`

| 项 | 实测 |
|---|---|
| 单文件发布 | 1 exe 29.31 MB（R2R + 压缩 + native libs 自解压） |
| 冷启动 | p50 408 ms（默认无 R2R 841 ms） |
| 运行时换肤 | p95 3.74 ms，30 次切换截图差分 0 |
| 长条 4000×60000 | 首块 53.9 ms、DPR2 设备光栅 p95 3.725 ms、内存 703 MB、0 掉帧 |
| 竖排 1:1 | DPR1/DPR2 全像素一致 |
| sidecar + 中文 | ping 214 ms、中文 hex 一致、UTF-8 负例 UNKNOWN、无控制台 |

## 5. 环境注意（AC11）

本机仓库树带 Low 强制标签：**非提权测试必须用无标签副本**（zip 释放/新拷贝），否则进程被降为 Low IL 导致 Core 写失败（见 `nonadmin/sandbox/REPORT.md`）。
