---
task_id: DIAG-READING-EXPORT-001-FIX-A
author: ZCode
recipient: DeepSeek Harness（非作者 Review）→ 代行 Codex（集成）
base_commit: 32ef1dd60cd82ac3a5fa18dfc5f834ec8639164a
owner_head: 77a78b25（实现交付；Handoff 为其后的 docs commit）
status: delivered
review_status: awaiting_review
parent_task: doc/tasks/DIAG-READING-EXPORT-001-FIX-A.md
---

# Handoff：DIAG-READING-EXPORT-001-FIX-A — 导出终态等待/信号投递语义修复

- **Owner**：ZCode；**非作者 Reviewer**：DeepSeek Harness；**Integrator**：代行 Codex（ZCode 会话，待真 Codex 追认）
- **Base**：`32ef1dd60cd82ac3a5fa18dfc5f834ec8639164a`（main @ FIX-A 释放冻结点）
- **Branch / worktree**：`agent/zcode/DIAG-READING-EXPORT-001-FIX-A-terminal-wait-semantics` / `G:/CODEX/New Manga.worktrees/DIAG-FIX-A-zcode`
- **Commit 链**：`32ef1dd6`（base）→ `d793939d`（claim：Task 置 `in_progress`，唯一改动为 Task 文件）→ `77a78b25`（实现交付）→ 本 Handoff
- **交付范围**（相对 base 的 tracked diff，4 文件）：
  - `tests/reading_export/test_viewmodels.py`：4 处等待谓词改为终态信号语义（详见 §1）
  - `verification/DIAG-READING-EXPORT-001-FIX-A/probe-terminal-wait-discrimination.py`（判别探针脚本）
  - `verification/DIAG-READING-EXPORT-001-FIX-A/probe-terminal-wait-discrimination.log`（判别证据，EXIT=0）
  - `verification/DIAG-READING-EXPORT-001-FIX-A/full-suite.log`（全仓一次，EXIT=0）
  - 本 Task 文件 + 本 Handoff（docs）
- **产品代码零改动**：`src/**` 未触碰（Task 默认测试侧方案；探针实证测试侧足以关闭窗口）。

## 1. 做了什么

诊断（DIAG-READING-EXPORT-001）证明：TASK-036 AC④ 的 `_finish` 程序顺序（先发终态信号/状态、后清
`running`）只在**工作线程内**成立；跨线程时槽走 Qt 排队投递，主线程轮询普通属性 `vm.running` 不需要
事件投递，可在终态信号槽运行前看到 `running == False`——历史全仓失败形态（`running=False, finished=[]`
而 `statusMessage` 已完成）由此产生。

修复（纯测试侧）：凡谓词返回后**立即消费信号列表**的 4 处等待，改为轮询"终态信号已到达"：

| 测试（test_viewmodels.py） | 旧谓词 | 新谓词 |
|---|---|---|
| `test_start_export_completes_and_updates_history`（历史失败点 :274） | `not vm.running` | `not vm.running and finished` |
| `test_start_export_stale_abort_surfaces_failure`（:289） | `not vm.running` | `not vm.running and failures` |
| `test_repeat_export_os_error_surfaces_failure_not_stuck`（:426） | `not vm.running` | `not vm.running and failures` |
| `test_export_without_pages_surfaces_status`（:442） | `not vm.running` | `not vm.running and failures` |

其余 6 处 `not vm.running` 等待只读工作线程先写的**普通属性**（`statusMessage`/`history`/DirectConnection
槽内记录，GIL 下跨线程读无需事件投递），无排队竞态暴露面，保持原样；文件头 TASK-036 注释已更正为
"程序顺序 ≠ 跨线程可观察顺序"的准确表述。未加 sleep/重试/skip，未放宽任何断言（信号永不到达时
`pump_until` 超时返回 False → 断言照常失败）。

## 2. AC 对照

- **AC1（历史形态不可再命中，≥200 次）**：判别探针阶段 B——新谓词 + 忙碌主线程刺激 **0/400 miss**。PASS。
- **AC2（判别力：先红后绿 + 故障注入保持红）**：
  - 阶段 A——同一刺激下**旧谓词 324/400 miss**（历史形态复现：`running=False statusMessage='导出完成：…' history=49`，与诊断字符串同形）→ 修复前红；
  - 阶段 B——新谓词 0/400 → 修复后绿；
  - 阶段 C——探针内 `BrokenVM`（清 flag 不发终态信号，受控历史形态）+ 新谓词：**3/3 正确超时报告"终态未达"** → 修复未学会接受缺失信号。PASS。
- **AC3（产品侧方案）**：未采用（Task 默认；测试侧探针实证已足够）。
- **AC4（定向 + 全仓，passed/skipped 分列）**：
  - 定向 `tests/reading_export/test_viewmodels.py`：**15 passed**，EXIT=0；
  - 全仓 `python -m pytest -q -p no:cacheprovider -rs tests`：**1316 passed, 5 skipped, 1 warning, 71.48s**，EXIT=0（[full-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-A/full-suite.log)）。
- **AC5（不以 sleep/重试/skip 掩盖）**：diff 仅谓词与注释；无新 skip。PASS。
- **AC6（Handoff + 非作者 Review + 集成）**：本 Handoff；DSH Review 待派发。

## 3. 测试证据（Q-009 口径）

| # | 命令 | 环境 | 结果 | EXIT | 证据 |
|---|---|---|---|---|---|
| 1 | `python -m pytest -q -p no:cacheprovider -rs tests/reading_export/test_viewmodels.py` | TASK-012-py312（Python 3.12.3 / PySide6 6.11.2），Git Bash | 15 passed | 0 | 会话转录（本节文字） |
| 2 | 判别探针 `probe-terminal-wait-discrimination.py 400 400 3` | 同上 | 旧谓词 324/400 miss；新谓词 0/400；故障注入 3/3 检出 | 0 | [probe log](../../verification/DIAG-READING-EXPORT-001-FIX-A/probe-terminal-wait-discrimination.log) |
| 3 | 全仓 `python -m pytest -q -p no:cacheprovider -rs tests` | 同上 | 1316 passed, 5 skipped, 1 warning | 0 | [full-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-A/full-suite.log) |

**口径差异说明**：全仓 1316+5 与 DIAG run-01 基线 1310+11 的差值 = 6 个 OpenSSL TLS 用例
（`test_connection_tester.py:106` + `test_transport_tls.py:39/47/62/69/83`）：本运行 shell（Git Bash）PATH
含 `/mingw64/bin/openssl`（OpenSSL 3.5.4），这 6 例实际运行并通过；DIAG 基线运行的 pwsh 环境 openssl
CLI 不在 PATH 而记 skip（[T1.2.1 R5 已记录的同款 shell 差异](../../verification/T1.1.1/review-2f116a2.md)）。
5 个剩余 skip = 2 docTR + 1 numpy + 2 torch（环境缺依赖，逐条见 full-suite.log），与 DIAG 基线一致。

## 4. 未跑项与风险

- 未跑：`tests/reading_export` 之外的定向套件未单独重跑（全仓已覆盖）；未多次重复全仓（本 Task 的
  竞态判别由探针承担，不以单次全仓绿作为消除证明——探针 800 次对比即判别 artefact）。
- 风险：① 本修复只改**测试等待语义**，产品 `_finish` 的排队投递行为不变——QML/用户路径不受影响，
  但若未来有**主线程代码**在 `running==False` 后立即依赖 `exportFinished` 副作用，同类窗口仍在产品层
  存在（诊断报告 §4.1 U3 未决；如需产品侧关闭，另立 Task 评估 QML 可观察时序）；② 忙等刺激强度
  （2 ms/次）下旧谓词命中率 81%，真实全仓负载构成仍属 U3 未决。
- 剩余：FIX-B（读者心跳生命周期）待本 Task 集成后串行释放。

## 5. 给 Reviewer（DeepSeek Harness）的要点

1. 核对 4 处谓词修改与其余 6 处不动的理由（§1 表；普通属性读 vs 信号消费的区别）。
2. 核对判别探针三阶段判定与日志数字（324/0/3）及脚本无 monkeypatch、无产品/测试文件编辑。
3. 核对全仓口径差异解释（1316+5 vs 1310+11，6 OpenSSL）。
4. 结论格式：`decision=approved|changes_requested` + findings（级别/文件行/触发/建议）。
