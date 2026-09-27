---
task_id: DIAG-READING-EXPORT-001
author: DeepSeek Harness
recipient: Codex（非作者 Review 与集成）
base_commit: 83de13dfe0521125715c2e26da75b96a63103938
owner_head: 8b36e98e（精确 SHA `8b36e98e8ce11bb54be5d6dfe8921cf64390aa4e`）
status: delivered
review_status: awaiting_review
parent_task: doc/tasks/DIAG-READING-EXPORT-001.md
---

# Handoff：DIAG-READING-EXPORT-001 — reading_export 间歇失败诊断

- **Owner head**：`8b36e98e8ce11bb54be5d6dfe8921cf64390aa4e`（本 Handoff 为其后的 docs commit）
- **Branch / worktree**：`agent/deepseek/DIAG-READING-EXPORT-001-reading-export-flaky-diagnosis` / `C:/Users/49745/.codex/worktrees/diag-reading-export-001/New Manga`
- **Base**：`83de13dfe0521125715c2e26da75b96a63103938`（未 rebase、未 amend、无历史改写）
- **Commit 链**：`83de13df`（base）→ `064ff980`（claim：仅取入释放版 Task 文件 + `in_progress`）→ `8b36e98e`（诊断交付）→ 本 Handoff（docs）
- **报告**：[doc/research/DIAG-READING-EXPORT-001.md](../research/DIAG-READING-EXPORT-001.md)
- **结论**：矩阵 **NOT_REPRODUCED**（15/15 exit 0，目标测试 0 失败）；两个历史症状机制均已定位，其中一个由探针实证复现、另一个确定性复现。**未修复、不声称已修复。**

## 1. 环境 Gate（PASS）

| 项 | 值 |
|---|---|
| 解释器（15 次运行同一绝对路径） | `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe` |
| Python / pytest | 3.12.3 / 9.1.1（与 `requirements*.txt` pin 一致） |
| PySide6 / Qt / shiboken6 | 6.11.2 / 6.11.2 / 6.11.2 |
| sqlite3 | 3.45.1 |
| openssl | CLI 不在 PATH；Python `ssl` = OpenSSL 3.0.13 |
| `QT_QPA_PLATFORM` | 空（Qt 默认 Windows 平台） |

清单与导入检查：[verification/DIAG-READING-EXPORT-001/environment.txt](../../verification/DIAG-READING-EXPORT-001/environment.txt)。
主 `python`（`C:\Python314\python.exe`，3.14.6）无 PySide6，未使用；该 venv 与本项目既有的 Qt 复现路径一致（T1.1.1 Review、M2-I1 baseline 全仓同环境）。

## 2. 矩阵结果（AC2）

转录：[matrix.tsv](../../verification/DIAG-READING-EXPORT-001/matrix.tsv)（15 行，含命令、顺序、结果、exit、日志路径、起止 UTC）；原始日志 `run-01..15.log`（每份含命令头、解释器、环境编号、时间戳与 `EXIT=`）。

| Run IDs | 场景 | 结果 | exit |
|---|---|---|---|
| `01` | 全仓基线 | **1310 passed, 11 skipped**（76.44s） | 0 |
| `02`–`04` | `test_viewmodels.py` 单文件 | 15 passed ×3 | 0 |
| `05`–`09` | 目标测试隔离 | 1 passed ×5 | 0 |
| `10`–`12` | reader → export 收集顺序 | 30 passed ×3 | 0 |
| `13`–`15` | export → reader 收集顺序 | 30 passed ×3 | 0 |

- **`NOT_REPRODUCED`**：15/15 exit 0，目标测试 0 次失败；次数用满，未擅自扩次数。
- 11 个 skip 均为环境缺依赖（6 OpenSSL、2 docTR、1 numpy、2 torch），**不计为通过**。
- 未复现不等于已修复：机制见 §3。

## 3. 机制结论（AC3）

**症状 A：`exportFinished` 未投递（竞态，已实证复现）**
- 导出跑在 `threading.Thread`；`_finish()` 在**工作线程**内 `changed.emit() → exportFinished.emit() → self._running = False`（`src/ui/viewmodels/export/viewmodel.py:291,344,379-394`）；测试等待谓词 `pump_until(qapp, lambda: not vm.running)` 读的是普通属性，而终态信号走 Qt **排队投递**（`tests/reading_export/test_viewmodels.py:34-48,274-275`）。主线程可先看到 `running == False` 而槽尚未执行 → 紧随其后的 `len(finished) == 1` 失败，且 `statusMessage`/`history` 已是完成态（与历史诊断字符串逐字段一致）。
- 历史失败 head `0275290` 的 `_finish` 顺序与当前 base **相同**（`git show 0275290:…/export/viewmodel.py`）⇒ 不是发布顺序回归。
- 探针 1（[脚本](../../verification/DIAG-READING-EXPORT-001/probe-export-signal-window.py) / [日志](../../verification/DIAG-READING-EXPORT-001/probe-export-signal-window.log)）：隔离空队列 **0/400** 命中；忙碌主线程（`processEvents` 内 2 ms 忙等）**26/200** 命中，且 26/26 由再一次 `processEvents()` 内到达；槽始终在 main 线程（排队投递）。命中样例 `iteration=28 running=False statusMessage='导出完成：…zip'`。

**症状 B：后台 `settleReadingTime` 写已关闭 SQLite（确定性复现）**
- `ReaderViewModel.__init__` 建 `QTimer(self)`（5 s），`openChapter()` 启动、仅 `closeReader()` 停止（`src/ui/viewmodels/reader/viewmodel.py:42,69-72,104-112`）；`settleReadingTime()`（`:441-451`）无"存储已关闭"保护。全仓仅 `test_viewmodels.py:163` 调用过 `closeReader()`；`test_qml_contract.py`（多处 `openChapter`）与 `tests/core/test_bootstrap.py:604-611`（生产装配 + SQLite reading store，`enterReader` 打开章节）都不关闭读者。
- 探针 2（[脚本](../../verification/DIAG-READING-EXPORT-001/probe-reader-heartbeat-closed-db.py) / [日志](../../verification/DIAG-READING-EXPORT-001/probe-reader-heartbeat-closed-db.log)）：按生产装配构造后关闭连接，(a) 同步调用即 `sqlite3.ProgrammingError`；(b) 跨一个真实心跳周期后**捕获 1 次未处理异常，栈帧与历史 stderr 逐帧相同**，且失败后心跳仍 active（会重复）。

**未决项（可证伪，见报告 §5）**：U1 历史那次是哪个用例留下的活心跳（历史 traceback 无宿主用例信息；需一个 teardown 后枚举存活 VM 的探针，需 Codex 授权）；U2 store 类型归属；U3 症状 A 的真实触发条件是否即"主线程事件负载"；U4 两症状为独立缺陷（现证据支持独立）。

## 4. 交付物清单

| 路径 | 内容 |
|---|---|
| `doc/tasks/DIAG-READING-EXPORT-001.md` | 状态 `in_progress` + 交付记录（本 Task 唯一被改的 Task 文件） |
| `doc/research/DIAG-READING-EXPORT-001.md` | 诊断报告（方法、环境、逐项结果、假设/反证、风险、修复建议） |
| `doc/handoffs/DIAG-READING-EXPORT-001-8b36e98e.md` | 本 Handoff |
| `verification/DIAG-READING-EXPORT-001/environment.txt` | 冻结环境与导入检查 |
| `verification/DIAG-READING-EXPORT-001/matrix.tsv` | 15 行矩阵转录（+ 探针注释行） |
| `verification/DIAG-READING-EXPORT-001/run-01..15.log` | 逐次原始 stdout/stderr + `EXIT=` |
| `verification/DIAG-READING-EXPORT-001/probe-export-signal-window.{py,log}` | 探针 1（终态信号窗口，两阶段） |
| `verification/DIAG-READING-EXPORT-001/probe-reader-heartbeat-closed-db.{py,log}` | 探针 2（心跳 ↔ 已关闭 SQLite） |

## 5. 越权核对

- 相对 base 的 tracked 差异仅 `doc/tasks/DIAG-READING-EXPORT-001.md`、`doc/research/DIAG-READING-EXPORT-001.md`、`verification/DIAG-READING-EXPORT-001/**`、本 Handoff。
- **未修改**生产代码、测试文件/断言/等待预算、Schema、Domain Contract、依赖文件、M2-I1/I2 产品文件或 T3.2.1 Gate；未改写历史 Review/Handoff/提交/既有证据；未加 skip、未加重试、未以增加等待掩盖失败。
- Task 释放治理 commit `ceab572b` 未合入 Owner 分支；claim 前未运行验证矩阵。

## 6. 阻塞与剩余风险

- **无阻塞**（环境 Gate PASS，矩阵按 Task 固定表完成）。
- 剩余风险：① 该 flaky 仍可能在任何高负载全仓运行中再次出现，本 Task 只给机制与触发条件，**未修复**；② 未决项 U1–U3 未收口（需 Codex 决定是否授权第三个探针，本 Task 探针上限 2 已用满）；③ 环境缺 openssl/docTR/numpy/torch 导致 11 个 skip（与本诊断无关，但同类全仓证据的"全绿"口径需据此打折）。
- 建议：另立两个修复 Task（FIX-A 等待/投递语义；FIX-B 读者心跳生命周期），由 Codex 冻结范围与 allowed paths 后释放；不建议以 sleep/重试/吞异常/skip 处理。

## 7. 给 Codex 的 Review 要点

1. 复跑矩阵成本低：全仓约 76 s，其余 14 次合计约 7 s；`matrix.tsv` 给出命令、顺序、exit 与日志路径，可与 `run-*.log` 交叉核对。
2. 核对 §3 的源码行号与"顺序未回归"的反证（`git show 0275290:src/ui/viewmodels/export/viewmodel.py`）。
3. 复核两个探针**未编辑/未 monkeypatch** 产品与测试文件（探针 1 仅在自身文件内子类化 `ExportViewModel` 打时间戳；探针 2 只用公开 API 复现）。
4. 复核 `NOT_REPRODUCED` 的表述未被写成"已修复"，以及 11 个 skip 未被计为通过。
5. 如批准，本 Task 交 Codex 集成（Task 文件置 `done` + `integration_commit`，登记 STATUS/Roadmap），并决定 FIX-A/FIX-B 的释放。
