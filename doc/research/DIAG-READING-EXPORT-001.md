# DIAG-READING-EXPORT-001 — reading_export 间歇失败诊断报告

- Task：[doc/tasks/DIAG-READING-EXPORT-001.md](../tasks/DIAG-READING-EXPORT-001.md)（`kind: diagnostic`，Owner=DeepSeek Harness，非作者 Reviewer=Codex）
- 固定 base：`83de13dfe0521125715c2e26da75b96a63103938`（main）；Owner worktree `C:/Users/49745/.codex/worktrees/diag-reading-export-001/New Manga`；branch `agent/deepseek/DIAG-READING-EXPORT-001-reading-export-flaky-diagnosis`
- 认领 commit：`064ff980`（仅取入释放版 Task 文件 + `status: in_progress`）
- 证据根：`verification/DIAG-READING-EXPORT-001/`（`environment.txt`、`matrix.tsv`、`run-01..15.log`、两个探针脚本与日志）
- 结论一句话：**15 次固定矩阵 NOT_REPRODUCED（0 失败、全部 exit 0）**；但两个历史症状的**机制均已定位**，其中导出终态信号竞态已由隔离探针**实证复现**（忙碌主线程 26/200 命中历史形态），读者心跳泄漏写已关闭 SQLite 由探针**确定性复现且逐帧同栈**。

## 0. 诚实边界声明

- 本 Task 只诊断，不修改任何生产代码/测试/断言/等待预算/Schema/依赖：worktree 相对 base 的唯一差异是新目录 `verification/DIAG-READING-EXPORT-001/`（`git status --porcelain` = 一条 `??`）。未加 skip、未加等待、未重试掩盖。
- **NOT_REPRODUCED 不等于已修复**：矩阵未复现（§2），但 §4 的探针证明触发窗口真实存在，只是本轮矩阵没有制造出足够的触发条件。
- 环境缺依赖导致的 **skip 不计为通过**：run-01 的 11 个 skip 逐条列在 §1（6 OpenSSL、2 docTR、1 numpy、2 torch）。
- 探针 1 经过三次修订（r1 因页面缺译文误走 `_fail` 分支、判定无效；r2 仅隔离阶段；r3 两阶段最终版）。同文件名重跑覆盖了前两次日志，本报告只引用 r3；修订史如实记录，Codex 可原样复跑 r3。

## 1. 冻结环境（AC1）

完整清单与导入检查：[`verification/DIAG-READING-EXPORT-001/environment.txt`](../../verification/DIAG-READING-EXPORT-001/environment.txt)

| 项 | 值 |
|---|---|
| OS / Shell | Windows 11 专业版 build 26200 / pwsh 7.6.6 |
| 解释器（**全部 15 次运行同一绝对路径**） | `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe` |
| Python | 3.12.3（与 `requirements.txt` / `requirements-dev.txt` 的 pin 口径一致） |
| pytest | 9.1.1（= `requirements-dev.txt` pin） |
| PySide6 / Qt / shiboken6 | 6.11.2 / 6.11.2 / 6.11.2（= `requirements.txt` 的 `PySide6_Essentials==6.11.2`） |
| sqlite3 | 3.45.1（模块 2.6.0） |
| openssl | **CLI 不在 PATH**；Python `ssl.OPENSSL_VERSION` = OpenSSL 3.0.13 30 Jan 2024 |
| `QT_QPA_PLATFORM` | 空（Qt 默认 Windows 平台） |

**环境 Gate 判定：PASS**（找到项目支持且可导入 PySide6 的环境）。该 venv 也是本项目既有 Qt 复现路径：`verification/T1.1.1/review-2f116a2.md:77` 的基线全量与 `verification/M2-I1/review-09ad43a/baseline-full-suite-0275290.log` 均用 `TASK-012-py312`。主 `python`（`C:\Python314\python.exe`，3.14.6）**无 PySide6**，故不用。

skip 清单（run-01，均因环境缺依赖，非通过）：`docTR` ×2（`test_detect_seam_t111.py`、`test_detection_doctr_real.py`）、`openssl unavailable` ×6（`test_connection_tester.py`、`test_transport_tls.py`）、`numpy` ×1、`torch` ×2（`test_detection_doctr.py`）——与 `review-2f116a2.md:77` 记录的同一 venv 跳过构成一致。

## 2. 固定矩阵结果（AC2）— NOT_REPRODUCED

逐行转录（命令、顺序、结果、exit、日志、起止 UTC）：[`matrix.tsv`](../../verification/DIAG-READING-EXPORT-001/matrix.tsv)

| Run IDs | 场景 | 结果 | exit |
|---|---|---|---|
| `01` | 全仓基线 `python -m pytest -q -p no:cacheprovider -rs tests` | **1310 passed, 11 skipped**, 76.44s | 0 |
| `02`–`04` | `tests/reading_export/test_viewmodels.py` | 15 passed ×3 | 0 |
| `05`–`09` | `...::test_start_export_completes_and_updates_history` | 1 passed ×5 | 0 |
| `10`–`12` | `test_reading.py` → `test_viewmodels.py` | 30 passed ×3 | 0 |
| `13`–`15` | `test_viewmodels.py` → `test_reading.py` | 30 passed ×3 | 0 |

- **15/15 exit 0，目标测试 0 次失败**：结论 `NOT_REPRODUCED`（矩阵次数用满，未擅自扩次数）。
- 历史对照不变的事实：`master@0275290` 首次全仓 `1 failed, 1228 passed, 5 skipped`（[baseline-full-suite-0275290.log](../../verification/M2-I1/review-09ad43a/baseline-full-suite-0275290.log)）；第二次全仓与交付树/基线树各 3 次单文件均通过（M2-I1 Review P3-004）。本 base 全仓为 1310 passed + 11 skipped（collect 1321），与 0275290 的 1229+5 不是同一树，失败的概率/条件不可直接类比。
- run-01 输出含大量 `ReaderView.qml:204 / AppShell.qml / PrimaryNavigationRail.qml … TypeError: Cannot read property … of null` 行——**历史日志同样存在**（0275290 日志逐段可见），属既有控制台噪音，不改变 exit 与计数，未计入失败。

## 3. 历史失败原始证据（复读，AC3 的一半）

来源：[baseline-full-suite-0275290.log](../../verification/M2-I1/review-09ad43a/baseline-full-suite-0275290.log)（`1 failed, 1228 passed`）+ [M2-I1 Review P3-004](../reviews/M2-I1-09ad43a-deepseek.md:56) + 更早同测先例 [T1.1.1 Review R2-I02](../../verification/T1.1.1/review-2f116a2.md:60)

失败形态（本 Task 的判据模板）：

```
AssertionError: export did not settle as expected:
  running=False signals=[] staleWarningVisible=False
  statusMessage='导出完成：...\out\result.zip' history=1
assert 0 == 1        # len(finished) == 1
```

即：**导出确实完成了**（statusMessage=导出完成、history=1、zip 已生成、`running` 已 False），但测试收集到的 `exportFinished` 列表为空。同一测试的 stderr 还有第二条独立症状：

```
settleReadingTime -> add_time -> _touch -> _persist -> store.write
  -> connection.__enter__ -> sqlite3.ProgrammingError: Cannot operate on a closed database
```

T1.1.1 Review（R2-I02）已记录同一测试在**实现环境与基线环境都失败**、症状同为"状态/历史已完成但 `exportFinished` 未收到"，并建议独立修复窗口——说明这不是 M2-I1/I2 的回归，而是更早的既有间歇问题。

## 4. 机制分析（AC3）与探针实证

### 4.1 症状 A：`exportFinished` 未投递（**已实证**）

源码事实（只读）：

1. 导出跑在 `threading.Thread(daemon=True)`（`src/ui/viewmodels/export/viewmodel.py:291,344`）。
2. `_finish()`（同文件 `:379-394`）在**工作线程**内依次执行：写 `_status` → `changed.emit()` → **`exportFinished.emit(summary)`** → `self._running = False` → `changed.emit()`。
3. 测试/主线程连接的槽因此走 Qt **排队投递**；而 `pump_until` 的等待谓词读的是普通属性 `vm.running`（`tests/reading_export/test_viewmodels.py:34-48, 274-275`）——**谓词不需要事件投递，终态信号需要**。
4. 结论：只要工作线程在"主线程刚跑完一次 `processEvents()`（或正在其中）"时完成 `_finish`，主线程就能先看到 `running == False`，而排队的 `exportFinished` 还没被派发；测试紧接着的无泵断言 `len(finished) == 1` 于是失败，且 `statusMessage`/`history` 已经是完成态——与历史诊断字符串**逐字段一致**。
5. 补充反证：`_finish` 的 emit→flag 顺序在历史失败 head `0275290` 与当前 base **完全相同**（`git show 0275290:src/ui/viewmodels/export/viewmodel.py`），因此**不是发布顺序回归**，而是"排队投递 vs 轮询标志位"的固有窗口。

探针 1（[脚本](../../verification/DIAG-READING-EXPORT-001/probe-export-signal-window.py) / [日志](../../verification/DIAG-READING-EXPORT-001/probe-export-signal-window.log)，只读驱动真实 `ExportViewModel`，未编辑/未 monkeypatch 产品与测试文件，仅用探针内子类打时间戳）：

| 阶段 | 复现测试等待模式 | 命中（`running=False` 且槽未运行） | 命中后一次 `processEvents()` 内到达 | 槽所在线程 |
|---|---:|---:|---:|---|
| 隔离（空事件队列） | 400 | **0** | — | main（排队投递） |
| 忙碌主线程（`processEvents` 内 2 ms 忙等，模拟全仓负载） | 200 | **26** | **26/26** | main |

命中样例（与历史字符串同形）：`iteration=28 running=False statusMessage='导出完成：…busy-main-thread-28.zip' history=429`。
⇒ **窗口存在且可被放大**；隔离条件下 0/400 解释了"为什么单文件/隔离重跑总是过"，而全仓（主线程事件队列被其它 Qt 测试、延迟删除、遗留定时器占满）正是放大条件。

### 4.2 症状 B：后台 `settleReadingTime` 写已关闭连接（**确定性复现**）

源码事实（只读）：

1. `ReaderViewModel.__init__` 建 `QTimer(self)`（间隔 `HEARTBEAT_MS = 5000`），`openChapter()` 里 `self._heartbeat.start()`；只有 `closeReader()` 会 `stop()`（`src/ui/viewmodels/reader/viewmodel.py:42,69-72,104-105,110-112`）。
2. `settleReadingTime()`（`:441-451`）在 `progress is not None and elapsed > 0` 时直接 `self._reading.add_time(elapsed)`；**没有"存储已关闭/连接失效"的保护**。
3. 全仓里 `closeReader()` 只在 `tests/reading_export/test_viewmodels.py:163` 出现过一次；而 `tests/reading_export/test_qml_contract.py`（多处 `openChapter`）、`tests/core/test_bootstrap.py:604-611`（经 `assemble_services` 的**生产装配**，reading 存储是 SQLite；`services.navigation.enterReader(...)` 打开章节，心跳启动）都不关闭读者。
4. SQLite 侧连接由测试夹具/装配在用例结束时关闭（如 `test_sqlite_reading_export.py` 的 `fresh_db` 夹具 `yield conn` 后 `conn.close()`）。被心跳（或任何后续 `settleReadingTime`）写入时即 `sqlite3.ProgrammingError: Cannot operate on a closed database`。

探针 2（[脚本](../../verification/DIAG-READING-EXPORT-001/probe-reader-heartbeat-closed-db.py) / [日志](../../verification/DIAG-READING-EXPORT-001/probe-reader-heartbeat-closed-db.log)）：用真实 `open_database` + `MigrationRunner` + `SqliteReadingProgressStore` + `ReadingService` + `ReaderViewModel` 按生产装配方式构造，`openChapter`（心跳 active=True），随后关闭连接并
(a) 同步调用 `settleReadingTime()` → `sqlite3.ProgrammingError`；
(b) 跑真实事件循环跨过一个心跳周期（5 s + 0.8 s）→ **捕获 1 次未处理异常，栈帧与历史 stderr 逐帧相同**（`viewmodel.py:450 → service.py:241 → service.py:377 → service.py:380 → reading_export.py:84 → connection.py:292 → ProgrammingError`），且**失败后心跳仍然 active**（会每 5 s 重复）。

⇒ 症状 B 的机制成立且可确定复现；历史那次失败只差"哪个用例留下的活心跳最先撞上已关闭连接"这一步（见 §5 未决项）。

## 5. 未决项与反证条件（可证伪）

| # | 未决项 | 反证/收口方式 |
|---|---|---|
| U1 | 历史那次全仓运行中，**具体是哪个用例**留下了跑着心跳且持有已关闭 SQLite 的 `ReaderViewModel` | 历史日志的 traceback 只给调用栈不给宿主用例。可用一个隔离探针（需 Codex 授权，见 §6）在 `pytest_runtest_teardown` 后枚举存活 `ReaderViewModel` 与其 `_heartbeat.isActive()`，一次全仓即可点名 |
| U2 | 症状 B 是否**必然**由 SQLite 读者用例引起（而非 JSON 用例 + 其它 SQLite 服务） | 同上探针：记录每个存活 VM 所持 store 的类型 |
| U3 | 症状 A 的真实触发条件是"主线程事件负载"还是别的（如系统负载下的 GIL 抢占） | 探针 1 换刺激方式（长 `processEvents`、并发 CPU 负载、加入全仓前置用例）若命中率随之变化即支持本假设；若在隔离阶段也能命中则说明窗口比我测得更大 |
| U4 | 症状 A 与症状 B 在历史那次失败中是否**同一原因的两面** | 目前证据表明是**两个独立缺陷**：A 是测试等待/投递竞态（导出路径本身正确完成），B 是读者心跳生命周期泄漏。A 的失败信息里 B 只是同期噪音 |

## 6. 风险、影响与修复建议（**本 Task 不实施**，需 Codex 另行冻结与释放）

风险界定：

- **产品正确性**：症状 A 显示导出**实际成功**（zip 落盘、历史写入、状态更新），失败的是"测试观察到终态信号"的时序；用户路径上 `changed`/状态会被事件循环正常派发。症状 B 的影响面是"残留心跳在连接关闭后报错并可能反复报错"，也可能在真实退出流程中产生噪音/掩盖真实错误。两者都属**可靠性/测试确定性**问题，**不是数据损坏或安全缺陷**。
- **影响范围**：`tests/reading_export/test_viewmodels.py`（A，任何 Qt 全仓/高负载运行）、任何"打开章节但不关闭读者"的用例与装配路径（B）。

建议拆成两个独立修复 Task（由 Codex 冻结范围后释放，Owner 与 Reviewer 需不同）：

1. **FIX-A（测试/等待语义，低风险）**：把该用例的等待谓词从"仅 `not vm.running`"改为"终态信号已到达或终态状态已发布"（例如 `pump_until(qapp, lambda: not vm.running and finished)`），或在断言前补一次 `processEvents()`；更彻底的产品侧方案是让终态信号在**主线程**派发（工作线程经队列调用/`QMetaObject.invokeMethod`），使"flag 已清 ⇒ 终态已投递"成立。后者需评估是否改变 QML 侧可观察时序。
2. **FIX-B（读者心跳生命周期）**：`ReaderViewModel` 增加停止心跳的明确终结点（离开读者页/`closeReader`/`aboutToQuit`）并在存储不可用时不再写；同时让测试在 teardown 关闭读者（生产装配路径尤其需要）。需注意不要以"吞异常"代替生命周期修复。

不建议的做法（会被 Reviewer 拒绝）：给测试加 `sleep`/重试、给心跳写包 `try/except` 吞掉 `ProgrammingError`、把用例标 skip。

## 7. 交付物与证据索引

| 交付物 | 路径 |
|---|---|
| 环境清单（含导入检查与 skip 构成） | `verification/DIAG-READING-EXPORT-001/environment.txt` |
| 矩阵转录（15 行 + 探针注释行） | `verification/DIAG-READING-EXPORT-001/matrix.tsv` |
| 逐次原始日志（命令、时间、stdout/stderr、`EXIT=`） | `verification/DIAG-READING-EXPORT-001/run-01..15.log` |
| 探针 1（导出终态信号窗口） | `probe-export-signal-window.py` / `probe-export-signal-window.log` |
| 探针 2（读者心跳 ↔ 已关闭 SQLite） | `probe-reader-heartbeat-closed-db.py` / `probe-reader-heartbeat-closed-db.log` |
| 本报告 | `doc/research/DIAG-READING-EXPORT-001.md` |
| Handoff | `doc/handoffs/DIAG-READING-EXPORT-001-<head>.md` |

历史证据（只读引用，未改写）：`verification/M2-I1/review-09ad43a/baseline-full-suite-0275290.log`、`doc/reviews/M2-I1-09ad43a-deepseek.md`（P3-004）、`verification/T1.1.1/review-2f116a2.md`（R2-I02）、`verification/M2-I1/integration-cff1e0a/record.md`。

## 8. 结论

1. 固定矩阵 15 次**未复现**目标间歇失败（`NOT_REPRODUCED`，0 失败、全 exit 0），未声称已修复。
2. 历史两个症状的机制均已定位：**A = 终态信号排队投递 vs 等待谓词轮询 `running` 的竞态**（探针 1 在忙碌主线程下 26/200 命中历史形态，隔离下 0/400）；**B = 未关闭的读者心跳向已关闭 SQLite 连接写入**（探针 2 确定性复现，栈帧与历史 stderr 逐帧相同，且失败后心跳继续运行）。
3. 两者均与 M2-I1/I2 交付无关，属既有 Legacy reliability 问题，与 T1.1.1 Review R2-I02 的既有记录一致。
4. 建议另立两个修复 Task（FIX-A 等待/投递语义、FIX-B 读者心跳生命周期），由 Codex 冻结并释放；在修复落地前，任何"该 flaky 已解决"的表述都不成立。
