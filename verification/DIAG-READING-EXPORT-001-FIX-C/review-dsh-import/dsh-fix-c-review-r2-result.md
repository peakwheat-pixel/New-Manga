## decision=changes_requested

### 0. 审查手段与证据限制（必读）

- 本会话为只读审查，**未修改任何文件**。
- 本会话 `pwsh` 沙箱在授权阶段即失败（`SetNamedSecurityInfoW failed (Win32 5): grantWrite(...)`），升级 `danger-full-access` 无审批通道可用，因此 **无法执行 `git diff de0bf175..ee30172f`**。为如实披露：下列核对基于「被审固定点工作树最终态文件 + `verification/**` 日志 + Handoff 交叉核对」，**hunk 级 git 校验与"是否存在第 6 个被改文件"未能独立验证**（已在 §1 标注，请集成方补齐 `git diff --stat de0bf175..ee30172f`）。
- 结论不依赖 git 元数据：N-1/N-2 由信号发射顺序（源码）与持久化链路（源码）逐行推出，可用测试或集成核验复核。

### 1. R2 变更面核对（de0bf175..ee30172f，应含 5 文件）

| 声明变更点 | 最终态证据 | 核对 |
|---|---|---|
| bootstrap re-arm | `src/bootstrap/app.py:257-265`（`page == "reader"` 分支：`reader.hasChapter and not reader._heartbeat.isActive()` → `_open_reader_chapter()`；无章节 no-op），`:269` connect | 一致（git 未验） |
| bootstrap quit 守卫 | `src/bootstrap/app.py:493-499`（`try: services.reader.closeReader() except Exception as error: print(..., file=sys.stderr)`；connect 在 `exec()` 之前、`_shutdown_services` 之前） | 一致（git 未验） |
| 测试三处 | `tests/core/test_bootstrap.py`：F-2 `:674-675`、F-3 `:683-685`、F-4 `:650-651` | 一致（git 未验） |
| `-r2` 日志 ×2 | `targeted-suite-r2.log:14,61`=`210 passed`/`EXIT=0`；`full-suite-r2.log:388,390`=`1318 passed, 5 skipped, 1 warning`/`EXIT=0`，`:383-387` 5 条 skip 逐条给因（2 docTR/1 numpy/2 torch） | 一致 |
| Handoff | `doc/handoffs/DIAG-READING-EXPORT-001-FIX-C-de0bf175.md` 含 `reviewed_head: e9f61f5b`、§6 R2 修订表（F-1..F-6 逐条） | 一致 |
| Task 文件（F-1 未改 AC 文本） | `doc/tasks/DIAG-READING-EXPORT-001-FIX-C.md:43` 仍为 `hasChapter is False`，`status: in_progress` | 与"留给集成裁决"声明一致 |

### 2. F-1..F-6 逐条判定

| ID | 判定 | 依据（一句） |
|---|---|---|
| F-1 | **通过（交集成裁决）** | Task AC1 文本确实未改、Handoff §6 显式转交集成裁决，处置符合 R1 建议；但该文本缺陷仍未处置，**集成记录不写裁决则 AC1 与实现持续矛盾**。 |
| F-2 | **通过（判别力不足，见 N-5）** | `:674-675` 已断言 `progress is not None` 且 `chapter_id` 匹配，字面落实；但 `openChapter` 早已设置并持久化 progress，修前该断言同样通过（红日志 `:37-38` 证明真实判别点是心跳断言）。 |
| F-3 | **通过** | `:683-685` 改为 `if services.reader.hasChapter: closeReader()` + `conn.close()`，符合 FIX-B 纪律。 |
| F-4 | **通过** | `:650-651` docstring 改为 "failed on the heartbeat-stopped assertion"，与红日志 `:37-38`（`viewmodel` 心跳断言）一致。 |
| F-5 | **不通过** | re-arm 语义与守卫组合正确（`reader` 页 + 有章节 + 心跳停才 `_open_reader_chapter()`；无章节 no-op；心跳活不重开），但该实现**引入 P2 缺陷 N-1 与 P3 N-2**（阅读时长虚增、`enterReader` 路径重复 `openChapter`）。 |
| F-6 | **通过** | `_close_reader_on_quit` 用 `except Exception` + stderr 报告包装，闭包捕获 `services`、连接时机在 `exec()` 返回后/`_shutdown_services` 前，槽内异常不再逃逸；仅捕获 `Exception`（不吞 `BaseException`）。 |

### 3. R2 新增问题（复核要求 3）

**N-1（P2，数据面，必须处置）——离开读者页的墙钟时间被计入并持久化为阅读时长。**
- 链条：`src/bootstrap/app.py:263-264` re-arm → `_open_reader_chapter()` → `ReaderViewModel.openChapter` **首行无条件** `settleReadingTime()`（`src/ui/viewmodels/reader/viewmodel.py:96`）；`settleReadingTime`（`:449-476`）以 `_last_settle` 差值调 `self._reading.add_time(elapsed)`（`src/application/reading/service.py:234-241`：累加 `total_read_seconds` 且 `_touch(now=True)` → `_persist()`）。
- 触发路径：`closeReader()` 在离开时 settle 并把 `_last_settle` 置为 T0 后停心跳；用户在书架/工作台停留 Δ 后经**导航栏**（`PrimaryNavigationRail.qml:32` → `navigate("reader")`）或**书架**（`bookshelf/viewmodel.py:424` → `enterReader`）返回 → 再次 settle，`elapsed = Δ`，被加到**离开前章节**的 `total_read_seconds` 并落库。
- 归因诚实说明：根因是既有 `openChapter` 的 settle 语义，**R1 经 `enterReader` 路径已可达**（本轮补报上轮漏检）；R2 的 re-arm 把触发面扩大到"任何经导航栏重返 reader"的常规路径。`settleReadingTime` 仅由心跳与其自身 slot 调用（QML 无调用），窗口期无其他 settle，故该结论确定。
- 这同时**触碰 Task 显式设计约束**（§设计约束"接线不改变任何页面语义"）：阅读时长统计被改变。

**N-2（P3）——`enterReader` 路径下同一章节双重 `openChapter`。**
- `NavigationViewModel.enterReader` 先 `currentPageChanged.emit("reader")`（`src/ui/viewmodels/navigation/viewmodel.py:101`）再 `readerContextChanged.emit()`（`:102`）；离开过 reader 后 `hasChapter` 仍为 True（`_has_chapter` = `progress is not None`，`src/ui/viewmodels/reader/viewmodel.py:162-163`）且心跳停 → 第一个信号命中 re-arm 打开新章节，第二个信号（`:248` 接线）再开一次同一章节。
- 影响：重复 `ReadingService.open`→ 重复 `_persist()`；重复 `_rebuild_tiles()`（`viewmodel.py:317-337` 先 `_rasterizer = None` 再重建，首个 rasterizer 被丢弃）；重复 `stateChanged/summaryChanged`。QTimer 只有单个实例（`start()` 为重启语义），**无定时器泄漏**，因此为 P3 而非 P2。
- 判别性缺口：`:678-680` 恰好走过该路径，但只断言 `hasChapter`/心跳，未断言 open 次数。

**N-3（P3）——re-arm 的 `_open_reader_chapter()` 无失败保护。**
F-6 只保护了 `aboutToQuit` 槽；当 store 仍不可用（FIX-B 的 `heartbeat_error` 自停后 `hasChapter` 仍 True、心跳停，会命中 re-arm）时，`openChapter → _reading.open → _persist` 的异常会从 `currentPageChanged` 槽冒泡到 QML 调用点。属既有面（R1 的 `readerContextChanged` 同源），R2 扩大。

**N-4（P3）——红→绿证据未随 R2 测试变更刷新。**
R2 改了测试与 docstring（F-2/F-4）与两处产品接线，但 `wiring-test-pre-wiring-red.log` / `wiring-test-post-wiring-green.log` 仍是 R1 版本测试的输出：红日志 `:16` 内嵌旧 docstring（"failed on `hasChapter is False`"）与现 `tests/core/test_bootstrap.py:650-651` 不一致。判别链（心跳断言）未变，实质影响小，但 Gate 1"红→绿证据"与当前测试版本存在 drift。

**N-5（P3）——F-2 断言的判别力缺口。**
见上表 F-2：`progress` 在 `open` 时即持久化，`:674-675` 无法证明"离开触发的 flush"；红证据的判别完全来自心跳断言。

**N-6（P4，观察）**：生产 handler 访问私有 `reader._heartbeat`（`app.py:263`），修复建议若采用 `_last_settle` 会再增一处；建议在后续 Task 让 `ReaderViewModel` 暴露公开的 pause/resume 面。

### 4. changes_requested 的修复要求（具体文件行）

1. **N-1（必须，P2）**：`src/bootstrap/app.py:263-264` 在 re-arm 调用前消除"离开时长计入旧章节"。
   - 选项 A（Task 内最小规避，不改 VM）：在 `_open_reader_chapter()` 之前执行 `reader._last_settle = time.monotonic()`（需 `import time`，注释说明是对既有 `openChapter` settle 语义的规避）。
   - 选项 B（若判超范围）：在 Handoff §4 与集成记录中**显式登记该偏差**（量化：Δ = 离开 reader 页墙钟时长，被累加到离开前章节 `total_read_seconds` 并持久化），并立后续 Task 修 `ReaderViewModel.settleReadingTime`（心跳非 active 时只更新 `_last_settle`、不 `add_time`），同时本 Task **不得**宣称"离开/重返语义完整"。
   - 任一选项都需补一条**判别性测试**：离开时长 > 心跳周期后重返，断言 `total_read_seconds` 不增加（先红后绿）。
2. **N-2（P3）**：`src/bootstrap/app.py:224-246` 的 `_open_reader_chapter()` 顶部加幂等守卫——当 `reader.hasChapter and reader._reading.chapter_id == chapter_id and reader._heartbeat.isActive()` 时直接 `return`；并补断言（计数 `openChapter` 调用）证明 `enterReader` 路径只开一次。
3. **N-3（P3）**：`src/bootstrap/app.py:263-264` 的 re-arm 调用与 F-6 同规格包装（`try/except` + stderr），或在 N-2 守卫下明确该路径不再重开。
4. **N-4（P3）**：以 R2 最终测试重跑红（base bootstrap）/绿证据入库到 `verification/DIAG-READING-EXPORT-001-FIX-C/`，或在 Handoff 明记 drift 与判别链不变的理由。
5. **N-5（P3）**：`tests/core/test_bootstrap.py:674-675` 改为可判别"离开触发接线"的断言（例如计数 `closeReader` 调用，或断言离开后 store 行 `last_read_at` 被刷新），避免修前也通过的伪断言。
6. **F-1（集成 Gate 条件）**：集成记录必须给出 AC1 文本裁决（修文本或授权保留），否则 Task 不得 `done`。

### 5. 推荐下一步

- 当前仓库状态：FIX-C 仍 `in_progress`，被审固定点 `ee30172f`；R2 的 F-3/F-4/F-6 与 F-5 的 re-arm 目标本身成立，F-1 按计划待集成裁决，阻塞项是 N-1（P2）与三项 P3 处置。
- 推荐操作：由 Owner（ZCode）做 **R3 返修**（处置 N-1..N-5，其中 N-1 选 A 或 B），再交本 Reviewer 复核；非作者 Review approved 后才交代行 Codex 集成。集成核验时请补 `git diff --stat de0bf175..ee30172f` 与 `git diff --check`（本会话无法执行）。
- 可转发给 ZCode 的指令：

> DIAG-READING-EXPORT-001-FIX-C R3 返修：处置 DSH R2 报告的 N-1（P2：`src/bootstrap/app.py:263-264` re-arm 使离开 reader 页的墙钟时长经 `openChapter→settleReadingTime→add_time` 累加到旧章节 `total_read_seconds` 并持久化；选 A=bootstrap 内对齐 `_last_settle` 或 B=Handoff/集成记录显式登记偏差并立后续 Task，并补"离开时长不计入"判别性测试）、N-2（`_open_reader_chapter` 加同章节+心跳 active 幂等守卫，消 `enterReader` 双重 open）、N-3（re-arm 调用按 F-6 规格包装）、N-4（以最终测试重跑红/绿证据）、N-5（`tests/core/test_bootstrap.py:674-675` 换判别性断言）。允许路径不变（`src/bootstrap/**`、`tests/core/**`、`tests/reading_export/**`、`verification/DIAG-READING-EXPORT-001-FIX-C/**`、Task 文件、Handoff）；不得改 QML/reading service/reader ViewModel 语义（若需改，先请 Codex 放行）。完成后交 DSH 第三轮复核。
