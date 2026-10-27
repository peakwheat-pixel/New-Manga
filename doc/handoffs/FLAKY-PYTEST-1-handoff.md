---
task_id: FLAKY-PYTEST-1
author: sandbox-verify
recipient: DeepSeek Harness
base_commit: 13cf26f6c
delivery_head: 4b0ac1831928a374ece45317e67933b9e47bc57e
status: in_review
---

# Handoff：FLAKY-PYTEST-1（3 个长期 flaky 失败归因与消除）

## 交付结果

分支 `task/FLAKY-PYTEST-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/FLAKY-PYTEST-1`，基于 HEAD `170878dc4`（卡 base `13cf26f6c`，为其祖先）。实现提交见任务卡 front matter `delivery_head`；本 Handoff、任务卡与证据为后续文档提交。

| AC | 结果 | 交付内容 |
|---|---|---|
| AC1 复现与归因 | **MET** | 基线（base `170878dc4`）3F/2772P/9S：①/② `test_detection_manga_real` 两项 = **环境（dev venv 运行时版本缺口）**：transformers 4.48.3 无 `RTDetrV2ForObjectDetection`，快照为 RT-DETR-v2、requirements pin 5.17.0、产品默认 ONNX 后端；③ `test_workbench_viewmodel::test_pause_shows_optimistic_feedback_immediately` = **真 bug**（VM `continueRun` 用 `run.status is PENDING` 判定 worker 准入，而控制契约 `control_run("continue")` 返回 `ControlResult(PENDING)` 且 run 置 RUNNING+resume）；观察项 `test_sandbox_job_kills_grandchildren` = OS 异步回收时序 flaky（探针 6/6 孙进程 ~20 ms 被杀） |
| AC2 处置 | **MET** | 真 bug → `src/ui/viewmodels/workbench/viewmodel.py` 以 `result.status is PENDING` 启动 worker；环境 → `tests/providers/test_detection_manga_real.py` 增加机器可判定 `hasattr(...RTDetrV2ForObjectDetection)` skip（reason 含实际版本/需求/pin/修复指引）；时序 → `tests/infrastructure/test_plugin_sandbox.py` 2 s→20 s **有界等待**（死亡即过，泄漏仍 fail） |
| AC3 连续 5 次稳定 | **MET** | 5/5 全量顺序运行完全一致：**0 failed / 2773 passed / 10 skipped**，EXIT=0（219.7/227.8/210.3/204.1/204.3 s）；`distinct_results=[[0,2773,10]]`、`consistent=true`；另 `-rs` 固化 10 项 skip 集合 |
| AC4 回归 | **MET** | `apps/desktop-avalonia/scripts/test.ps1` → **225/225 passed, 0 skipped**（coreclient 40 / host 76 / app 109）；`npx vitest run` → **60 files / 567 tests passed** |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS（`verification/FLAKY-PYTEST-1/check-taskpath.log`）；任务卡 26 条 64-hex pin；Record Decision（flaky 政策）见 `REPORT.md` §8 |

完整报告：`verification/FLAKY-PYTEST-1/REPORT.md`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 基线 3F | `python -m pytest tests -q` | base `170878dc4`（交付 worktree 原状） | **3F/2772P/9S**（EXIT=1） | `logs/run0-baseline.log` |
| AC1 失败 1/2 归因 | `python -m pytest tests/providers/test_detection_manga_real.py -q --tb=line -rs`（pre-fix 独立 worktree） | 无修改 base `170878dc4` | 2 failed；`AttributeError: ...RTDetrV2ForObjectDetection` → ProviderError（detection_manga.py:535） | `logs/ac1-prefix-detection.log` |
| AC1 环境事实 | transformers/torch 版本 + hasattr + requirements pin + 快照 config 探针 | 本机 dev venv | 4.48.3 / torch 2.11.0；hasattr=False；pin 5.17.0；快照 RTDetrV2/4.49.0 | `logs/ac1-env-probe.log` |
| AC1 失败 3 归因 | `python -m pytest ...::test_pause_shows_optimistic_feedback_immediately -q --tb=short`（pre-fix） | 无修改 base `170878dc4` | 3/3 稳定失败（15 s 超时于 line 210） | `logs/ac1-prefix-workbench-pause.log` |
| AC1 观察项 | `tools/probe_sandbox_tree.py 6 30`（生产 AppContainerSandbox 直调 6 次） | 交付 worktree | 6/6 孙进程 ~20 ms 死亡、0 泄漏（2 s 窗口有负载敏感风险） | `logs/ac1-sandbox-probe.log`、`logs/ac1-sandbox-single-6x.log` |
| AC2 处置验证 | 三个测试文件定向重跑 | 修复后 worktree | detection 1 skipped（`-rs` 可见 reason）；workbench pass；sandbox 模块 16/16 pass | `logs/ac2-postfix-*.log` |
| AC3 连续 5 次 | `python tools/run_five.py` → 5 × `python -m pytest tests -q` | 修复后 worktree，顺序无并行 | **0F/2773P/10S ×5，EXIT=0，consistent=true** | `logs/run1..5-pytest.log`、`ac3-five-runs.json` |
| AC3 skip 集合 | `python -m pytest tests -q -rs` | 同上 | 2773P/10S（docTR×2、openssl×6、registry×1、新增 detection×1） | `logs/run6-skipset.log` |
| AC4 dotnet | `pwsh -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <私有>` | 交付 worktree 构建 | **TEST PASS: 225/225 passed, 0 skipped** | `test/avalonia-summary.json`、`logs/ac4-dotnet-test.log` |
| AC4 vitest | `npx vitest run`（主 checkout frontend，两树源零 diff） | 交付工作树（无 node_modules） | **60/60 files、567/567 tests passed** | `logs/ac4-vitest.log` |
| AC5 门禁 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FLAKY-PYTEST-1.md` | 分支交付 | PASS（见日志） | `check-taskpath.log` |

未运行：frozen sidecar 重打包（`src/ui` legacy VM 不入随包 Core 闭包，无产品闭包变化）；并行 pytest 稳定性（证据口径为单机顺序）。

## 接收方式

- 仓库：`G:/CODEX/New Manga`（linked worktree `G:/CODEX/New Manga.workspace/worktrees/FLAKY-PYTEST-1`，分支 `task/FLAKY-PYTEST-1`）。
- 复验命令：`cd <worktree> && python -m pytest tests -q`（预期 0 failed / 2773 passed / 10 skipped）；`python -m pytest tests -q -rs` 查看 skip 原因；`python verification/FLAKY-PYTEST-1/tools/run_five.py` 可重放 5 连跑（写 task-env log）。
- 前置条件：本机 dev venv；DOTNET/Avalonia 测试需 `HOST-CORECLIENT-1/sidecar-copy`；vitest 需 `apps/desktop/frontend/node_modules`（主 checkout 已安装）。
- DSH 集成检查建议：① 复核 3 个文件 diff 是否仅为 VM 控制判定 + 测试 skip/等待；② 用 `-rs` 确认 skip 均为机器可判定且无静默；③ 复核 5 次日志的 EXIT 与 git head；④ 决定 dev venv 是否按 requirements pin 重建（见风险）。

## 下一任务建议（必填）

- Task ID / 标题：无新增卡建议；本卡集成后只需 DSH 复核并推进生命周期。若需恢复两个 detection 测试的真实覆盖，建议 DSH 决策"dev venv 对齐 requirements-dev.txt"（运维/环境类，不新建产品 Task）。
- 推荐 Agent / Reviewer：DSH 集成复核；Reviewer 不得为 `sandbox-verify`。
- 推荐原因与前置依赖：3 个失败已闭环，5 连跑稳定；无需新产品代码。
- Recovery point：仓库 `G:/CODEX/New Manga`；分支 `task/FLAKY-PYTEST-1`（delivery head 见任务卡）；worktree 已创建。
- 允许修改路径：以本卡为准（`src/**`、`tests/**`、本卡、`verification/FLAKY-PYTEST-1/**`）。
- 禁止范围与新增授权条件：不改协议/Host/旧壳；不 push；不伪造 5 次记录。
- 交付物：分支 commit（3 文件）+ 本卡 + Handoff + `verification/FLAKY-PYTEST-1/**` 证据。
- 验证命令、环境与完成 Gate：见任务卡 AC1–AC5。
- 可直接转发给 Agent 的指令：`无需新任务；请 DSH 集成 FLAKY-PYTEST-1（task/FLAKY-PYTEST-1）并复核 5 连跑证据。`

## 风险与遗留

1. **dev venv 落后 requirements pin**（transformers 4.48.3 vs `5.17.0`；torch 2.11.0 vs `2.14.0`）：两个 detection 测试以显式 skip 表达；安装 `requirements-dev.txt` 后会自动真跑。本卡**未改动机器环境**（是否重建由 DSH 决策）。
2. `test_sandbox_job_kills_grandchildren` 的 20 s 上界为经验值（实测死亡 ~20 ms）；若未来再次复现应另开诊断卡（AppContainer/Job 语义），不继续放大窗口。
3. 5 次运行是**单机顺序**证据；并行跑 pytest 可能重新诱发负载敏感 flake，不作为验收口径。
4. 回退：`git revert` 本卡 3 个文件即回原行为；无 Schema/协议/数据迁移风险（失败测试会重新变红，属预期）。

DONE 前由 DSH 按任务卡 Canonical Evidence 与 `resource-manifest.json` 收口；本 Handoff 不授予集成、删除或关闭权限。
