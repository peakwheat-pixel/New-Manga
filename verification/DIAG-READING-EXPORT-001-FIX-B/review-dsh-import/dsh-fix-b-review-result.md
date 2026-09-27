已完成全部只读核查。现在给出审查结论。

**审查方法与限制（口径披露）**：本会话 pwsh 在 workspace-write 沙箱下初始化即失败（`SetNamedSecurityInfoW Win32 5`，且无审批通道），`git` 命令完全不可用。我改用只读工具：以 `G:/CODEX/New Manga.worktrees/DIAG-FIX-A-zcode`（分支 tip `6fe7bd86`，FIX-A 未触碰 `src/**`）与 main 工作树 `G:/CODEX/New Manga`（`8e57e4df`，其 `viewmodel.py` = 485 行与 FIX-A 版一致）作为 base 等价比对物，按文件内容重建 diff；branch tip 经 `.git` ref 确认为 `528ba4d455b0c52611a16e3a016dc9bf099cc87d` ✓。

decision=changes_requested

## findings

**R-01｜P2｜AC1 的"明确终结点使 `_heartbeat.stop()` 必达"未在生产侧实现，Handoff 却整条标 PASS**
- 文件:行：`doc/handoffs/DIAG-READING-EXPORT-001-FIX-B-3ce82240.md:53`；`doc/tasks/DIAG-READING-EXPORT-001-FIX-B.md:30,47`
- 触发：全仓 grep `aboutToQuit` 在 `src/**` 零命中；`closeReader()` 在生产 QML 中从未被调用（诊断已确认唯一调用点在测试）。Task 目标写明终结点取"离开读者页 / `closeReader` / `aboutToQuit` 的生产装配路径"，而 `src/bootstrap/app.py` 未被改（diff 外，行数 514=514 与 base 一致，符合禁止范围）。
- 影响：症状 B 的**异常噪音**确已消除（catch→stop），但 AC1 的前半句（终结点必达）实现为零；Handoff 用探针（其自身调用 closeReader/制造连接关闭）间接证明后半句，就把整条 AC1 判 PASS。这属于证据口径大于实际达成面。Task §已知阻塞要求"若必须动 bootstrap 才能关闭终结点，停止并交 Codex 作范围决定"，作者未停止亦未披露该缺口。
- 建议：二选一——(i) 在 Handoff §4 显式记录"生产终结点未接线（bootstrap 属禁止范围），生产泄漏由 settleReadingTime 的 stop-on-error 兜底"，并请 Codex 作范围裁决；(ii) 补一个 Codex 放行的 bootstrap 终结点（如 `aboutToQuit` 接线）后再宣称 AC1 完整。

**R-02｜P2｜teardown 覆盖未穷尽，AC3 "test_viewmodels.py 的 openChapter 用例"字面未达成**
- 文件:行：`tests/reading_export/test_viewmodels.py:162-169`（`test_reader_missing_translation_message`，自建 `vm` + `openChapter`，无 teardown）；`tests/reading_export/test_webtoon_tiles.py:272-273,624-627,752-753`（三处自建 VM + `openChapter`，全文件无 `closeReader`）
- 触发：全仓 `openChapter` 调用点共 17 处，仅 `reader` fixture、三个 `reader_stack*` fixture、`test_bootstrap.py:636` finally 与回归测试自身被覆盖；上列 4 处仍留下活心跳。
- 影响：这些 VM 用 `JsonProgressDocumentStore`（`make_reading_service`，非 SQLite）且多为函数内局部对象，实际被 GC/无 ProgrammingError，**运行时危害低**；但它正是 AC3 点名的文件与同类泄漏面，`tests/reading_export/**` 在 allowed 内，本可零成本收口，也削弱"泄漏面已清除"的完整性声明。
- 建议：为 `test_viewmodels.py:164` 起及 `test_webtoon_tiles.py` 三处补 `closeReader`（或在 `tests/reading_export/conftest.py` 加 autouse 夹具统一收尾）；若判定不必要，须在 Handoff 明写"JSON-store 局部 VM 不再收口"的理由。

**R-03｜P3｜docstring 引用不存在的 `heartbeatError` Property**
- 文件:行：`src/ui/viewmodels/reader/viewmodel.py:77`（"observable via ``heartbeatError``/``heartbeatErrorChanged``"）
- 触发：全仓 `heartbeatError` 仅有 `heartbeatErrorChanged = Signal()`（:51），无 `Property` 定义；QML 端无任何引用。
- 影响：注释声称的可观察契约不成立，后续维护/审查会误以为 QML 已能读取错误。
- 建议：改为只提 `heartbeat_error`（Python 属性）与信号，或补 `Property(str, ...)`。

**R-04｜P3｜`heartbeatErrorChanged` 是无消费者的死信号**
- 文件:行：`src/ui/viewmodels/reader/viewmodel.py:51,470`
- 触发：QML 与测试均未 connect（grep 零命中），且无配套 Property 可供读取。
- 影响：新增公开 API 面零价值、增加维护面（QML 未改是本 Task 的约束，所以"加信号"不能改善可观察性）。
- 建议：保留（若计划下个 Task 接 UI）则在 Handoff 注明用途与 Owner；否则删除信号，仅保留属性，等真正接线时再加。

**R-05｜P3｜Handoff 变更面文件计数不实**
- 文件:行：`doc/handoffs/DIAG-READING-EXPORT-001-FIX-B-3ce82240.md:18`
- 触发：其自身列举为 4 个代码文件 + `verification/**`（4 个文件）+ Task + Handoff = 10 个文件，标题写"8 文件"。
- 影响：轻微；但范围类数字是集成核验锚点，应与实际一致。
- 建议：改为 10（或写明按"代码 4 + 证据 4 + 治理 2"分组计数）。

**R-06｜P3｜stop 之后无重启路径，且瞬时 `OperationalError` 也被无条件停表**
- 文件:行：`src/ui/viewmodels/reader/viewmodel.py:465-471`
- 触发：`except sqlite3.Error` 覆盖整个族（含 `database is locked` 这类可恢复错误），捕获即 `stop()`；除再次 `openChapter()` 外没有恢复累积计时的路径。
- 影响：长会话中一次瞬时存储错误会让阅读时长累积静默停止（QML 又读不到错误，见 R-03/R-04），属轻微功能退化。
- 建议：在 Handoff §4 增列该残余边界；若要区分，可按异常类型分类处理（如 `OperationalError` 允许下个周期重试一次），但**不建议**收窄到仅 `ProgrammingError`（见下方设计取舍裁决）。

## 设计取舍裁决（Handoff §4）
- (a) `closeReader()` 保持 fail-loud：**接受**。但请把"心跳已停后再 closeReader 仍会抛"的组合场景写进残余边界（`test_bootstrap.py:642` 的 `closeReader` 位于 `conn.close()` 之前，顺序正确、安全；`reading/service.py:158-161` 对无章节有 `progress is None` 守卫，故 finally 在测试早期失败时也不会二次抛错——已核实）。
- (b) 捕获范围 `sqlite3.Error`：**接受，不必收窄**。`add_time→_touch→_persist→store.write` 的可抛面包含 `OperationalError`（locked/no such table）与 `DatabaseError`，收窄到 `ProgrammingError` 会漏掉真实"存储不可用"形态；`src` 内 `sqlite3.Error` 只影响这一条已类型化路径，不掩盖非存储缺陷。
- (c) 新增信号 QML 未消费：**接受不改 QML**，但按 R-03/R-04 修订注释并明确信号归属。

## 已核实通过项（不计 finding）
- diff हunks 与声明一致：`viewmodel.py` 新增 `import sqlite3`/`heartbeatErrorChanged`/`heartbeat_error` 初始化/`settleReadingTime` try-except（base 485 行 → head 506 行，+21 行全部落在上述位置，无其它语义改动）。
- 回归测试判别力成立：修前 `settleReadingTime` 直调 `add_time` 即抛；`verification/DIAG-READING-EXPORT-001/probe-reader-heartbeat-closed-db.log` 为确定性修前 artefact（1 次 unhandled traceback + `heartbeat still active = True`，栈帧与 `viewmodel.py:450→service.py:241/377/380→reading_export.py:84→connection.py:292` 完全一致），且该探针与本 Task 探针共享同一 `sys.excepthook` 测量机制，故"0 未处理异常"这一读数有效。
- 探针 7/7 PASS 与时间戳自洽（17:35:05.8→17:35:17.7 ≈ 2×(5000+800) ms），`heartbeat_error='sqlite3.ProgrammingError: Cannot operate on a closed database.'`，非静默。
- 顺序正确：`test_bootstrap.py:642 closeReader()` 先于 `:643 conn.close()`。
- 证据口径诚实：`targeted-suite.log` 163 passed/EXIT=0；`full-suite.log` 1317 passed、5 skipped（2 docTR+1 numpy+2 torch，明细逐条列于 :385-389）、1 warning（无关的 `imghdr` DeprecationWarning）/EXIT=0；与 FIX-A 归档基线 `1316 passed, 5 skipped`（`verification/DIAG-READING-EXPORT-001-FIX-A/full-suite.log:390`）差值恰为 +1 ✓。
- 范围未越权（内容级）：`src/bootstrap/app.py`(514=514)、`src/application/reading/service.py`(440=440)、`src/infrastructure/sqlite/reading_export.py`(535=535)、`src/ui/qml/reader/ReaderView.qml`(328=328) 与 base 参照逐一行数一致；`FIX-B` 标记只落在被授权的 4 个代码文件；`STATUS.md`/`REBASELINE_PLAN.md` 等仍写 FIX-B `proposed / NOT_RELEASED`（未被本交付改动，符合 allowed）。

## 未覆盖风险
1. 本 Reviewer 无法执行任何命令（沙箱故障）：未独立运行 `git diff a8b94df1..528ba4d4`、`git diff --check`、未重建 commit 树，也未复跑探针/测试；逐 hunk 结论基于 base 等价 worktree 的内容比对，"零越权"仍是内容级旁证而非 git 树级证明——建议集成者以 `git diff --stat` 与 `diff --check` 复验。
2. 未独立验证 PySide6 是否必然经 `sys.excepthook` 上报 timer-slot 异常；该测量有效性仅由诊断探针 2 的同机制结果旁证。
3. 非 SQLite 存储失败（`JsonProgressDocumentStore.write` 的 `OSError`/权限/磁盘满，`src/application/reading/ports.py:90-102`）不在捕获范围；一旦 R-02 的未收口用例在清理后的目录上触发心跳，仍会向事件循环泄漏未处理异常（同类噪音的另一种异常类型）。
4. 生产侧心跳终结点缺失（R-01）在真实连接被驱逐/重建（TASK-061 方向）时的行为未经端到端验证：静默停表 + 用户不可见（R-04/R-06）叠加后的产品影响未评估。
5. Handoff 所称"6 个 OpenSSL 用例在本 shell 实跑通过"仅与 full-suite 无 openssl skip 一致，未逐用例核对；"1 warning"未在 Handoff 说明内容。
6. 本 Reviewer 未核对 `verification/**` 是否含未被引用的多余产物——目录恰为 4 个文件，未见冗余，但未做内容哈希/字节级比对。

**推荐下一步**：将该报告作为 `doc/reviews/DIAG-READING-EXPORT-001-FIX-B-528ba4d4.md` 落盘（由集成者/作者在授权范围内提交，本会话只读不落盘），Owner（ZCode）按 R-01/R-02 做最小返修（补 4 处 teardown + Handoff §4 增列生产终结点缺口），再交集成者复验；R-03~R-06 可随同一次返修一并处理。
