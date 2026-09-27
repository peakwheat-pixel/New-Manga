---
task_id: DIAG-READING-EXPORT-001-FIX-B
author: ZCode
recipient: DeepSeek Harness（非作者 Review）→ 代行 Codex（集成）
base_commit: a8b94df1f1ee091a9cca894c421e9ffc3ad30614
owner_head: 3ce82240（实现交付；Handoff 为其后的 docs commit）
status: delivered
review_status: awaiting_review
parent_task: doc/tasks/DIAG-READING-EXPORT-001-FIX-B.md
---

# Handoff：DIAG-READING-EXPORT-001-FIX-B — Reader 心跳生命周期修复

- **Owner**：ZCode；**非作者 Reviewer**：DeepSeek Harness；**Integrator**：代行 Codex（ZCode 会话，待真 Codex 追认）
- **Base**：`a8b94df1f1ee091a9cca894c421e9ffc3ad30614`（FIX-A 集成 merge；串行释放）
- **Branch / worktree**：`agent/zcode/DIAG-READING-EXPORT-001-FIX-B-reader-heartbeat-lifecycle` / `G:/CODEX/New Manga.worktrees/DIAG-FIX-B-zcode`
- **Commit 链**：`a8b94df1`（base）→ `6e37f05d`（claim：Task 置 `in_progress`）→ `3ce82240`（实现交付）→ 本 Handoff
- **变更面**（8 文件，全在 allowed 清单）：
  - `src/ui/viewmodels/reader/viewmodel.py`（唯一产品文件；Task allowed 首项）
  - `tests/reading_export/test_viewmodels.py`（回归测试 + reader fixture teardown）
  - `tests/reading_export/test_qml_contract.py`（三个 reader_stack fixture teardown）
  - `tests/core/test_bootstrap.py`（生产装配读者路径 teardown，仅 :636 一处 finally）
  - `verification/DIAG-READING-EXPORT-001-FIX-B/**`（探针 + 三份日志）+ 本 Task 文件 + 本 Handoff

## 1. 做了什么

诊断症状 B：`ReaderViewModel` 心跳由 `openChapter()` 启动、仅 `closeReader()` 停止；`settleReadingTime()`
对已关闭的存储连接无保护；测试/生产装配多处打开章节后不关闭读者，SQLite 夹具 teardown 关连接后心跳触发即
`sqlite3.ProgrammingError` 且每 5 s 重复（诊断探针 2 确定性复现，栈帧与历史 stderr 逐帧相同）。

三层修复：

1. **类型化存储失败处理**（`settleReadingTime`）：`self._reading.add_time(elapsed)` 包 `try/except sqlite3.Error`
   —— 捕获后**停止心跳**（不再每 5 s 重复）、把完整类型化错误记到公开属性 `heartbeat_error`
   （`"sqlite3.ProgrammingError: …"`）并 emit 新信号 `heartbeatErrorChanged`。**不是吞异常**：错误被类型化
   记录、可观察、可断言，心跳死亡；不向 Qt 事件循环泄漏原始 traceback（历史 stderr 噪音源）。`import sqlite3`
   为 stdlib，不构成跨层依赖（UI→application→infrastructure 方向未变）。
2. **测试 teardown 关闭读者**（4 处）：`test_viewmodels.py` 的 `reader` fixture（yield + `if vm.hasChapter:
   vm.closeReader()`）、`test_qml_contract.py` 的 `reader_stack`/`reader_stack_webtoon`/`reader_stack_tiled`
   三个 fixture（共享 `_close_reader_stack` 帮助函数）、`test_bootstrap.py:636` 的 finally（`enterReader` 的
   生产装配用例——在 `conn.close()` **之前** `services.reader.closeReader()`，进度在连接存活时 flush）。
   未开章节的 VM teardown 为 no-op（`hasChapter` 守卫 / `closeReader` 对无章节安全）。
3. **回归测试** `test_reader_heartbeat_stops_after_store_tear_down`：真实 SQLite（`open_database` +
   `MigrationRunner` v4 + `SqliteReadingProgressStore`）+ `openChapter` → `conn.close()` → 心跳同款调用
   `settleReadingTime()` → 断言无异常、`heartbeat_error` 含 `sqlite3.ProgrammingError`、心跳已停。
   修前该调用直接抛 `ProgrammingError`（测试红；确定性修前复现 = 诊断探针 2 的已归档 artefact）。

未以 sleep/重试/skip/吞异常处理；未改 QML、`src/bootstrap/**`、`src/application/reading/**`、
`src/infrastructure/sqlite/**`、Schema、依赖。

## 2. AC 对照

- **AC1（心跳生命周期闭环；泄漏形态不可复现）**：[泄漏探针](../../verification/DIAG-READING-EXPORT-001-FIX-B/probe-heartbeat-leak-fixed.log)（真实事件循环跨 **2 个**完整心跳周期）**7/7 PASS、EXIT=0**：0 未处理异常、首次触发后心跳自停、`heartbeat_error` 已记录、第二周期 0 异常（停表不会重响）、同步 settle 安全。verdict=`LEAK CLOSED`。PASS。
- **AC2（类型化可诊断处理，不吞 ProgrammingError）**：`sqlite3.Error` 类型化捕获；错误全文（含类型名）落 `heartbeat_error` + signal；心跳停止 = 行为后果可见；回归测试逐断言锁定。PASS。
- **AC3（teardown 关闭读者 + 先红后绿回归）**：4 处 teardown（§1.2）；回归测试修前红（诊断探针 2 的确定性复现为同构红证据，已归档）、修后绿（定向 163 passed 含新用例）。PASS。
- **AC4（U1/U2 收口记录）**：teardown 关闭后全仓再无存活心跳指向已关闭连接的面；U1（历史那次具体是哪个用例）与 U2（store 类型归属）作为历史归因问题**关闭为不再可复现**——修复后无论哪个用例留下读者，teardown 都会关闭它，且即使泄漏也已类型化防御。见 §4 残余边界。
- **AC5（定向 + 全仓，passed/skipped 分列）**：定向 `tests/reading_export tests/core/test_bootstrap.py` **163 passed**，EXIT=0（[targeted-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-B/targeted-suite.log)）；全仓 **1317 passed, 5 skipped, 1 warning**，EXIT=0（[full-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-B/full-suite.log)）。5 skip = 2 docTR + 1 numpy + 2 torch（环境缺依赖）；6 个 OpenSSL 用例本 shell 实跑通过（同 FIX-A 口径差异说明）。PASS。
- **AC6（未新增 skip/放宽断言/新依赖）**：diff 仅上述 8 文件；无新 skip；`import sqlite3` 为 stdlib。PASS。
- **AC7（Handoff + 非作者 Review + 集成）**：本 Handoff；DSH Review 待派发。

## 3. 测试证据（Q-009 口径）

| # | 命令 | 环境 | 结果 | EXIT | 证据 |
|---|---|---|---|---|---|
| 1 | `python verification/DIAG-READING-EXPORT-001-FIX-B/probe-heartbeat-leak-fixed.py` | TASK-012-py312，Git Bash | 7/7 检查 PASS，LEAK CLOSED | 0 | [probe log](../../verification/DIAG-READING-EXPORT-001-FIX-B/probe-heartbeat-leak-fixed.log) |
| 2 | `python -m pytest -q -p no:cacheprovider -rs tests/reading_export tests/core/test_bootstrap.py` | 同上 | 163 passed | 0 | [targeted-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-B/targeted-suite.log) |
| 3 | `python -m pytest -q -p no:cacheprovider -rs tests` | 同上 | 1317 passed, 5 skipped, 1 warning | 0 | [full-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-B/full-suite.log) |

全仓 1317+5 与 FIX-A 集成基线 1316+5 的差值 = 本 Task 新增的 1 个回归测试；5 skip 口径与 FIX-A 相同。

## 4. 未跑项、残余边界与设计取舍（给 Reviewer 的要点）

1. **`closeReader()` 自身的 `self._reading.close()` 仍 fail-loud**：若在连接已关闭后调用 `closeReader`，
   `ReadingService.close()` 的 `_touch/_persist` 会抛 `ProgrammingError`（保持"用户主动关闭时持久化失败
   必须被看见"的语义，属 Task 点名的 `settleReadingTime` 范围之外）。测试 teardown 的正确顺序
   （先 `closeReader` 后 `conn.close()`）已在 4 处落实。
2. **捕获范围 = `sqlite3.Error`**（`ProgrammingError` 的基类族）：类型化于存储层错误族；非存储错误照常
   抛出。若 Reviewer 认为应收窄到 `ProgrammingError`，为单行返修。
3. **产品排队投递行为未变**（同 FIX-A 口径）；本修复不改变任何 QML 可观察时序（`heartbeatErrorChanged`
   为新增可选信号，QML 未消费）。
4. **U1/U2 的历史归因**（历史那次具体是哪个用例留下活心跳）随泄漏面关闭而失去现实意义，未再单独立探针
   点名（修复前需要第三个诊断探针，已超上限；修复后该问题不可再发生）。
5. **约 6 秒/用例的心跳等待**：泄漏探针真实等待 2×5.8 s 心跳周期（真实 QTimer 路径，不接受缩短周期的
   模拟替代）；回归测试用同步 settle 调用（心跳同款函数），不等待真实周期，测试套件耗时不受影响。

## 5. 复现方式

```powershell
cd 'G:\CODEX\New Manga.worktrees\DIAG-FIX-B-zcode'
G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe verification/DIAG-READING-EXPORT-001-FIX-B/probe-heartbeat-leak-fixed.py
G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe -m pytest -q -p no:cacheprovider -rs tests/reading_export tests/core/test_bootstrap.py
```
