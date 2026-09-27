---
task_id: DIAG-READING-EXPORT-001-FIX-C
author: ZCode
recipient: DeepSeek Harness（非作者 Review）→ 代行 Codex（集成）
base_commit: 0e34c5c3c0a753be3e9f310daa0e413959f4ca5d
owner_head: de0bf175（实现交付；Handoff 为其后的 docs commit）
status: delivered
review_status: awaiting_review
parent_task: doc/tasks/DIAG-READING-EXPORT-001-FIX-C.md
---

# Handoff：DIAG-READING-EXPORT-001-FIX-C — 生产侧读者心跳终结点接线

- **Owner**：ZCode；**非作者 Reviewer**：DeepSeek Harness；**Integrator**：代行 Codex（ZCode 会话，待真 Codex 追认）
- **Base**：`0e34c5c3c0a753be3e9f310daa0e413959f4ca5d`（FIX-B 集成治理 commit；FIX-B AC1 生产接线缺口的承接 Task）
- **Branch / worktree**：`agent/zcode/DIAG-READING-EXPORT-001-FIX-C-quit-and-leave-wiring` / `G:/CODEX/New Manga.worktrees/DIAG-FIX-C-zcode`
- **Commit 链**：`0e34c5c3`（base）→ `b1f4cedf`（claim）→ `de0bf175`（实现交付）→ 本 Handoff
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
| 1 | 接线测试（PRE-wiring，base bootstrap） | TASK-012-py312，Git Bash | FAILED（红，接线缺失） | 1 | [red log](../../verification/DIAG-READING-EXPORT-001-FIX-C/wiring-test-pre-wiring-red.log) |
| 2 | 接线测试（POST-wiring） | 同上 | passed（绿） | 0 | [green log](../../verification/DIAG-READING-EXPORT-001-FIX-C/wiring-test-post-wiring-green.log) |
| 3 | `python -m pytest -q -p no:cacheprovider -rs tests/core tests/reading_export` | 同上 | 210 passed | 0 | [targeted-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/targeted-suite.log) |
| 4 | `python -m pytest -q -p no:cacheprovider -rs tests` | 同上 | 1318 passed, 5 skipped, 1 warning | 0 | [full-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-C/full-suite.log) |

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
