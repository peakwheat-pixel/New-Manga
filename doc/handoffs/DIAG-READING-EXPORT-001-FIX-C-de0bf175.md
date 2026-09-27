---
task_id: DIAG-READING-EXPORT-001-FIX-C
author: ZCode
recipient: DeepSeek Harness（非作者 Review）→ 代行 Codex（集成）
base_commit: 0e34c5c3c0a753be3e9f310daa0e413959f4ca5d
owner_head: de0bf175（R1 实现交付）
reviewed_head: 46c7ff5a（R4 交付，当前被审固定点；区间 27dbedda..46c7ff5a）
status: delivered
review_status: re_review_4_requested
parent_task: doc/tasks/DIAG-READING-EXPORT-001-FIX-C.md
---

# Handoff：DIAG-READING-EXPORT-001-FIX-C — 生产侧读者心跳终结点接线

- **Owner**：ZCode；**非作者 Reviewer**：DeepSeek Harness；**Integrator**：代行 Codex（ZCode 会话，待真 Codex 追认）
- **Base**：`0e34c5c3c0a753be3e9f310daa0e413959f4ca5d`（FIX-B 集成治理 commit；FIX-B AC1 生产接线缺口的承接 Task）
- **Branch / worktree**：`agent/zcode/DIAG-READING-EXPORT-001-FIX-C-quit-and-leave-wiring` / `G:/CODEX/New Manga.worktrees/DIAG-FIX-C-zcode`
- **Commit 链**：`0e34c5c3`（base）→ `b1f4cedf`（claim）→ `de0bf175`（R1 实现交付）→ 本 Handoff（R1 docs）→ `e9f61f5b`（R2 返修，当前被审 HEAD）
- **变更面**（git 实际 7 文件 = 代码 2 + 证据 4 + 治理 1；Task 文件为 R0 释放带入，无独立改动提交）：
  - 代码 2：`src/bootstrap/app.py`（两处接线，见 §1）、`tests/core/test_bootstrap.py`（接线断言测试）
  - 证据 4：`verification/DIAG-READING-EXPORT-001-FIX-C/` 下 `wiring-test-pre-wiring-red.log`、`wiring-test-post-wiring-green.log`、`targeted-suite.log`、`full-suite.log`
  - 治理 1：本 Task 文件（claim，R0）；本 Handoff 为第 8 文件（docs commit）

## 1. 做了什么（纯 Python bootstrap 接线，零 QML 改动）

FIX-B `done` 时披露的生产缺口（DSH R-01）：`closeReader()` 终结点在生产 QML/bootstrap 无任何调用。本 Task
在 [bootstrap](../../src/bootstrap/app.py) 补两个终结点：

1. **离开读者页**（`_assemble_legacy_qt_layer` 内，`readerContextChanged` 接线之后）：
   `navigation.currentPageChanged.connect(_close_reader_when_leaving)`——handler 对任何非 `"reader"` 目标页且
   读者有打开章节时调用 `reader.closeReader()`（flush 进度 + 停心跳）。进入读者页 emit 的 page 恰为
   `"reader"`，永不误触发；`closeReader` 对无章节安全（`progress is None` 守卫链）。
2. **应用退出**（`main()` 内，`window = engine.rootObjects()[0]` 之后）：
   `application.aboutToQuit.connect(services.reader.closeReader)`——在 `exec()` 返回、
   `_shutdown_services(services)` 关闭连接**之前**干净停止心跳并 flush 进度。

语义注记（测试已锁定）：`closeReader()` 不清 `hasChapter`（`ReadingService.close()` 只 flush 持久化，
`progress` 保持可读——与 `tests/reading_export/test_viewmodels.py` 既有断言一致）；接线契约是
**心跳停止 + 进度 flush**，不是清空章节。不改 `NavigationViewModel`/`ReaderViewModel`/reading service 语义、
不改 QML、不引入依赖。

## 2. AC 对照

- **AC1（离开读者页触发 closeReader；红→绿）**：接线断言测试
  `test_navigation_away_from_reader_closes_it`（生产 `assemble_services` 装配 + 真实 SQLite + `enterReader`
  打开章节 → `navigate("bookshelf")` → 断言心跳停 + 幂等重进）：
  **PRE-wiring（base bootstrap）FAILED EXIT=1**（[red log](../../verification/DIAG-READING-EXPORT-001-FIX-C/wiring-test-pre-wiring-red.log)）
  → **POST-wiring PASSED EXIT=0**（[green log](../../verification/DIAG-READING-EXPORT-001-FIX-C/wiring-test-post-wiring-green.log)）。PASS。
- **AC2（读者页内不误触发）**：同一测试覆盖——`enterReader` 后心跳 active（若接线误触发读者会被立即关闭，
  `hasChapter` 断言先失败）；navigate 回 bookshelf 再 `enterReader` 重新打开、心跳重新 active。PASS。
- **AC3（aboutToQuit 接线）**：`main()` 一行 connect（§1.2）。单测不覆盖 `main()` 内接线（无 application
  注入路径）；以 Review 静态审查 + 运行时 smoke 覆盖。**披露为弱验证面**（一行标准 Qt connect，风险低）。
- **AC4（定向 + 全仓，分列）**：定向 `tests/core tests/reading_export` **210 passed**，EXIT=0
  （[targeted-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/targeted-suite.log)）；全仓
  **1318 passed, 5 skipped, 1 warning**，EXIT=0（[full-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/full-suite.log)）。
  5 skip = 2 docTR + 1 numpy + 2 torch（环境缺依赖）；6 OpenSSL = 本 shell PATH 实跑通过（同 FIX-A/B 口径）；
  +1 = 本 Task 新接线测试。PASS。
- **AC5（不新增 skip/放宽断言/依赖；不改 QML/Schema/Contract）**：diff 仅 §变更面 7 文件。PASS。
- **AC6（Handoff + 非作者 Review + 集成）**：本 Handoff；DSH Review 待派发。

## 3. 测试证据（Q-009 口径）

| # | 命令 | 环境 | 结果 | EXIT | 证据 |
|---|---|---|---|---|---|
| 1 | 接线测试（PRE-wiring，base bootstrap；R4 最终测试版重取） | TASK-012-py312，Git Bash | FAILED（红，接线缺失） | 1 | [red log](../../verification/DIAG-READING-EXPORT-001-FIX-C/wiring-test-pre-wiring-red.log) |
| 2 | 接线测试（POST-wiring；R4 最终测试版重取） | 同上 | passed（绿） | 0 | [green log](../../verification/DIAG-READING-EXPORT-001-FIX-C/wiring-test-post-wiring-green.log) |
| 3 | `python -m pytest -q -p no:cacheprovider -rs tests/core tests/reading_export` | 同上 | 210 passed | 0 | R1：[targeted-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/targeted-suite.log)；**R4（最终）：[targeted-suite-r4.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/targeted-suite-r4.log)**；R3 历史：[targeted-suite-r3.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/targeted-suite-r3.log) |
| 4 | `python -m pytest -q -p no:cacheprovider -rs tests` | 同上 | 1318 passed, 5 skipped, 1 warning | 0 | R1：[full-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/full-suite.log)；**R4（最终）：[full-suite-r4.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/full-suite-r4.log)**；R3 历史：[full-suite-r3.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/full-suite-r3.log) |

注：`wiring-test-pre-wiring-red.log` 内含原始 pytest 输出的行尾空白（忠实转录，按 Q-009 原始字节入库，
未清洗）；代码与治理文件无卫生问题（`git diff --check` 对非日志文件干净）。

## 4. 未跑项、残余边界（给 Reviewer 的要点）

1. **aboutToQuit 接线无自动化测试**（AC3 弱验证面）：`main()` 内一行 `application.aboutToQuit.connect(
   services.reader.closeReader)`；拆出可注入函数属过度工程，选择 Review 审查覆盖。
2. **离开读者页会 flush 进度**（closeReader 语义）：从读者页导航离开即持久化当前进度——与"心跳粗粒度
   保存"的既有语义一致（提前 flush 无损）；若产品想要"离开不保存"，属需求变更另议。
3. **workbench 章节 ↔ reader 关闭无耦合**：`closeReader` 不触碰 export history/workbench；reader-initiated
   export window（path A controller）在关闭后仍持有自身引用，既有行为未变。
4. 定向套件未含 QML 契约测试文件变更（本 Task 零 QML 改动，`test_qml_contract.py` 在定向 210 内通过）。

## 5. 复现方式

```powershell
cd 'G:\CODEX\New Manga.worktrees\DIAG-FIX-C-zcode'
G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/core/test_bootstrap.py::test_navigation_away_from_reader_closes_it
```


## 6. R2 修订记录（DSH 首轮 approved 的 F-1..F-6 处置）

DSH 首轮 Review `decision=approved`（0×P0/P1；6×Minor）。逐条处置：

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| F-1 | Minor（集成前须 Codex 处置） | Task AC1 字面要求 `hasChapter is False` 与 closeReader 冻结语义矛盾 | **交代行 Codex 于集成时裁决**（建议采纳 Review 建议：AC 判"文本缺陷，非实现缺陷"，集成时修订 AC1 为"心跳停 + 进度 flush（hasChapter 按既有语义保留）"并记入集成记录） |
| F-2 | Minor | AC1"进度已持久化"无断言 | **fixed**：navigate 后断言 `services.reading.progress` 非 None 且 chapter_id 匹配 |
| F-3 | Minor | 新测试 finally 未收口心跳（FIX-B 纪律） | **fixed**：finally 改为 `if hasChapter: closeReader()` + `conn.close()` |
| F-4 | Nit | docstring 与红日志失败点不符 | **fixed**：改为"failed on the heartbeat-stopped assertion" |
| F-5 | Minor（行为回退） | 经导航栏重返读者页仅 emit page 信号，心跳不 re-arm（丢 5s 粒度） | **fixed**：handler 的 `page == "reader"` 分支加 re-arm（有章节且心跳停时复用 `_open_reader_chapter()` 重开；无章节 no-op） |
| F-6 | Minor | 退出 flush 与 workbench 写者争锁时 `_reading.close()` 异常可从 aboutToQuit 槽逃逸 | **fixed**：`_close_reader_on_quit` 包 try/except，stderr 报告（沿用 `_shutdown_services` 惯例） |

R2 变更（`de0bf175..e9f61f5b`，git 实际）：`src/bootstrap/app.py`（F-5 re-arm、F-6 quit 守卫）、`tests/core/test_bootstrap.py`（F-2/F-3/F-4）、`verification/DIAG-READING-EXPORT-001-FIX-C/targeted-suite-r2.log`、`full-suite-r2.log`、本 Handoff。R2 证据：定向 **210 passed** EXIT=0（[targeted-suite-r2.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/targeted-suite-r2.log)）、全仓 **1318 passed, 5 skipped** EXIT=0（[full-suite-r2.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/full-suite-r2.log)）。F-1 的 AC1 修订按 R1 建议留给集成裁决，本 Handoff 不改 Task AC 文本。


## 7. R3 修订记录（DSH R2 复核 changes_requested 处置）

R2 复核实体认可（F-3/F-4/F-6 通过、F-5 re-arm 目标成立、F-1 交集成裁决），新报 N-1（P2）+ N-2/N-3/N-4/N-5（P3）+ N-6（P4 观察）。逐条处置：

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| N-1 | P2 | 离开读者页的墙钟时长经重返 openChapter 的 settle 语义被计入旧章节 total_read_seconds（FIX-B/FIX-C 修复后暴露） | **fixed（选项 A 最小规避）**：`_open_reader_chapter` 顶部——心跳非 active（离开态）时先重置 `_last_settle` 再 openChapter（settle 折叠为 0）；阅读中切章（心跳 active）保持既有结算语义。判别测试：模拟 600s 缺席后重返，断言 `total_read_seconds` 不变（红→绿见 §3 更新） |
| N-2 | P3 | enterReader 路径同一章节双重 openChapter | **fixed**：`_open_reader_chapter` 顶部幂等守卫（同章节 + 心跳活 → return）；测试断言 re-arm 恰开 1 次、随后的 enterReader 守卫跳过（opens 计数） |
| N-3 | P3 | re-arm 的 _open_reader_chapter 无失败保护 | **fixed**：re-arm 调用包 try/except + stderr（与 F-6 同规格） |
| N-4 | P3 | 红→绿证据与 R2 测试版本 drift | **fixed**：以 R3 最终测试重取红/绿日志（pre-wiring EXIT=1 / post EXIT=0）覆盖同名文件 |
| N-5 | P3 | F-2 断言判别力不足（progress 在 open 时已持久化） | **fixed**：改为 closeReader 调用计数断言（修前 navigate 永不触发 close → 计数空 → 红） |
| N-6 | P4 | handler 访问私有 `_heartbeat`/`_last_settle` | **accepted + 披露**：公开 pause/resume 面留给后续 VM Task；bootstrap 访问点已在注释标注 |

R3 变更（git 实际 `ee30172f..<R3 head>`）：`src/bootstrap/app.py`（N-1/N-2/N-3 守卫 + `import time`）、`tests/core/test_bootstrap.py`（N-5 计数 + N-1 判别 + N-2 断言 + import time + import time 顺序）、红/绿日志重取、`targeted-suite-r3.log`、`full-suite-r3.log`、本 Handoff。R3 证据：接线测试红（EXIT=1）→绿（EXIT=0）；定向 **210 passed** EXIT=0；全仓 **1318 passed, 5 skipped** EXIT=0（[targeted-suite-r3.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/targeted-suite-r3.log) / [full-suite-r3.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/full-suite-r3.log)）。F-1（Task AC1 文本裁决）仍按计划留集成层。


## 8. R4 修订记录（DSH R3 复核收口）

R3 复核：N-1 产品修复正确（守卫位置/顺序正面确认）、N-2/N-3 通过、无新产品缺陷与越权。剩余 3 项小修：

| ID | 内容 | 处置 |
|---|---|---|
| T-1 | N-1 判别断言严格相等对时钟 tick 非确定 | **fixed**：改容忍式 `total_read_seconds - total_before_return < 1.0`（无守卫时增量 ≈600，判别力保留）；以 R4 最终测试重取红/绿日志（pre EXIT=1 / post EXIT=0） |
| T-2 | Handoff 证据链接仍指 R1 日志 | **fixed**：§3 表改为 R1/R3 双指针（R3 实际证据 = `-r3.log`） |
| T-3 | `import time` 顺序 | **fixed**：移至 `tempfile` 后恢复字母序 |
| T-4 | "心跳非 active=离开态"在 FIX-B 存储故障停跳时也重置基线（该段时长本已写不入库，无实质损失） | **accepted + 注释披露**：守卫注释已含该口径；公开 pause/resume 面留后续 VM Task（同 N-6） |

R4 变更（git 实际 `27dbedda..46c7ff5a`，7 文件）：`tests/core/test_bootstrap.py`（断言）、`src/bootstrap/app.py`（import 顺序）、`verification/DIAG-READING-EXPORT-001-FIX-C/` 下 `wiring-test-pre-wiring-red.log`、`wiring-test-post-wiring-green.log`（R4 重取）、`targeted-suite-r4.log`、`full-suite-r4.log`（新增）、本 Handoff。R4 证据（最终交付测试版）：定向 **210 passed** EXIT=0（[targeted-suite-r4.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/targeted-suite-r4.log)）、全仓 **1318 passed, 5 skipped** EXIT=0（[full-suite-r4.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/full-suite-r4.log)）。产品接线自 R3 起零改动（R3 复核确认）。

R5 doc-only 收口（DSH R4 复核 H-1/H-2/H-3）：本提交仅改本 Handoff——补被审固定点 `27dbedda..46c7ff5a`（H-1）、§3 第 1/2 行轮次标签 R3→R4（H-2）、§3/§8 补引 r4 日志（H-3）。不改产品/测试/日志，不重跑 suite。
