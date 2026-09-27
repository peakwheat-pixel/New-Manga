---
task_id: DIAG-READING-EXPORT-001-FIX-B
author: ZCode
recipient: DeepSeek Harness（非作者 Review）→ 代行 Codex（集成）
base_commit: a8b94df1f1ee091a9cca894c421e9ffc3ad30614
owner_head: 3ce82240（R1 实现交付）
reviewed_head: 2a1078b6（R2 交付，当前被审固定点）
status: delivered
review_status: re_review_2_changes_requested_docs_only
parent_task: doc/tasks/DIAG-READING-EXPORT-001-FIX-B.md
---

# Handoff：DIAG-READING-EXPORT-001-FIX-B — Reader 心跳生命周期修复

- **Owner**：ZCode；**非作者 Reviewer**：DeepSeek Harness；**Integrator**：代行 Codex（ZCode 会话，待真 Codex 追认）
- **Base**：`a8b94df1f1ee091a9cca894c421e9ffc3ad30614`（FIX-A 集成 merge；串行释放）
- **Branch / worktree**：`agent/zcode/DIAG-READING-EXPORT-001-FIX-B-reader-heartbeat-lifecycle` / `G:/CODEX/New Manga.worktrees/DIAG-FIX-B-zcode`
- **Commit 链**：`a8b94df1`（base）→ `6e37f05d`（claim）→ `3ce82240`（R1 实现交付）→ `528ba4d4`（R1 Handoff）→ `2a1078b6`（R2 交付 = R1 复核返修 + Handoff 修订，当前被审 HEAD）
- **变更面**（以 git 为准：`git diff --name-only a8b94df1..2a1078b6` = **12 文件 = 代码 4 + 证据 6 + 治理 2**，全在 allowed 清单）：
  - 代码 4：`src/ui/viewmodels/reader/viewmodel.py`（唯一产品文件）、`tests/reading_export/test_viewmodels.py`、`tests/reading_export/test_qml_contract.py`、`tests/core/test_bootstrap.py`
  - 证据 6：`verification/DIAG-READING-EXPORT-001-FIX-B/` 下 `probe-heartbeat-leak-fixed.{py,log}`、`targeted-suite.log`、`full-suite.log`、`targeted-suite-r2.log`、`full-suite-r2.log`
  - 治理 2：本 Task 文件 + 本 Handoff
  - R2 增量（`528ba4d4..2a1078b6`，5 文件）：Handoff、`viewmodel.py`（docstring/注释）、`test_viewmodels.py`（:162 teardown）、两份 `-r2.log`

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
2. **测试 teardown 关闭读者**（5 处落点）：`test_viewmodels.py` 的 `reader` fixture（yield + `if vm.hasChapter:
   vm.closeReader()`）、`test_qml_contract.py` 的 `reader_stack`/`reader_stack_webtoon`/`reader_stack_tiled`
   三个 fixture（共享 `_close_reader_stack` 帮助函数）、`test_bootstrap.py:636` 的 finally（`enterReader` 的
   生产装配用例——在 `conn.close()` **之前** `services.reader.closeReader()`，进度在连接存活时 flush）、
   `test_viewmodels.py` 的 `test_reader_missing_translation_message`（R2 补 try/finally）。
   未开章节的 VM teardown 为 no-op（`hasChapter` 守卫 / `closeReader` 对无章节安全）。
3. **回归测试** `test_reader_heartbeat_stops_after_store_tear_down`：真实 SQLite（`open_database` +
   `MigrationRunner` v4 + `SqliteReadingProgressStore`）+ `openChapter` → `conn.close()` → 心跳同款调用
   `settleReadingTime()` → 断言无异常、`heartbeat_error` 含 `sqlite3.ProgrammingError`、心跳已停。
   修前该调用直接抛 `ProgrammingError`（测试红；确定性修前复现 = 诊断探针 2 的已归档 artefact）。

未以 sleep/重试/skip/吞异常处理；未改 QML、`src/bootstrap/**`、`src/application/reading/**`、
`src/infrastructure/sqlite/**`、Schema、依赖。

## 2. AC 对照

- **AC1（心跳生命周期闭环；泄漏形态不可复现）**：**达成一半，另一半披露为范围缺口（R2，DSH R-01）**。
  - 已达成：泄漏形态（连接关闭后心跳触发写库）不可复现——[泄漏探针](../../verification/DIAG-READING-EXPORT-001-FIX-B/probe-heartbeat-leak-fixed.log)（真实事件循环跨 **2 个**完整心跳周期）**7/7 PASS、EXIT=0**：0 未处理异常、首次触发后心跳自停、`heartbeat_error` 已记录、第二周期 0 异常、同步 settle 安全。verdict=`LEAK CLOSED`。
  - 范围缺口（披露）：**生产侧终结点接线为零**——`closeReader()` 作为终结点仅存在于 API 面，生产 QML 从不调用、`aboutToQuit` 无接线（`src/bootstrap/**` 与 QML 属本 Task 禁止范围；Task §已知阻塞要求此时停止并交 Codex 裁决，本交付按此停止并在此披露）。生产泄漏由 `settleReadingTime` 的 stop-on-error 兜底（异常噪音与重复写已消除，但心跳在真实连接消失时是"报错一次后停止"而非"离开页面时干净停止"）。**需要 Codex/用户裁决**：是否另立 Task 在生产装配/QML 层接线终结点。
- **AC1-附（心跳自停行为）**：PASS（见上）。
- **AC2（类型化可诊断处理，不吞 ProgrammingError）**：`sqlite3.Error` 类型化捕获；错误全文（含类型名）落 `heartbeat_error` + signal；心跳停止 = 行为后果可见；回归测试逐断言锁定。PASS。
- **AC3（teardown 关闭读者 + 先红后绿回归）**：teardown 共 **6 处落点**（§1.2 枚举的 reader fixture、三个 qml_contract fixture、bootstrap finally、`test_reader_missing_translation_message` 的 try/finally）；`test_webtoon_tiles.py` 的三处共享辅助函数构造（`_make_reader_stack`/`_make_multipage_webtoon_stack`/一处内联）**判定不收口并在此披露**（DSH R-02 选项 ii）：均为 JSON-store 局部 VM、测试函数结束即 GC、QTimer 随 QObject 销毁、无 sqlite 错误面，收口需改动全部调用方测试而收益为零。回归测试修前红（诊断探针 2 的确定性复现为同构红证据，已归档）、修后绿（定向含新用例全过）。PASS（覆盖面披露如上）。
- **AC4（U1/U2 收口记录）**：teardown 关闭后全仓再无存活心跳指向已关闭连接的面；U1（历史那次具体是哪个用例）与 U2（store 类型归属）作为历史归因问题**关闭为不再可复现**——修复后无论哪个用例留下读者，teardown 都会关闭它，且即使泄漏也已类型化防御。见 §4 残余边界。
- **AC5（定向 + 全仓，passed/skipped 分列）**：R1 与 R2 各一轮，数值相同——定向 `tests/reading_export tests/core/test_bootstrap.py` **163 passed**，EXIT=0（R1：[targeted-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-B/targeted-suite.log)；**R2：[targeted-suite-r2.log](../../verification/DIAG-READING-EXPORT-001-FIX-B/targeted-suite-r2.log)**）；全仓 **1317 passed, 5 skipped, 1 warning**，EXIT=0（R1：[full-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-B/full-suite.log)；**R2：[full-suite-r2.log](../../verification/DIAG-READING-EXPORT-001-FIX-B/full-suite-r2.log)**）。5 skip = 2 docTR + 1 numpy + 2 torch（环境缺依赖）；6 个 OpenSSL 用例本 shell 实跑通过（同 FIX-A 口径差异说明）。PASS。
- **AC6（未新增 skip/放宽断言/新依赖）**：diff 仅 §变更面所列 12 文件（git 清单为准）；无新 skip；`import sqlite3` 为 stdlib。PASS。
- **AC7（Handoff + 非作者 Review + 集成）**：本 Handoff（R2 修订版）；DSH R1 `changes_requested`（6 findings）→ R2 处置后复核"代码与测试面通过，剩余 5 条文档事实性缺口（N-01..N-05）"→ R3 本轮文档修订收口；集成待代行 Codex 复验。

## 3. 测试证据（Q-009 口径）

| # | 命令 | 环境 | 结果 | EXIT | 证据 |
|---|---|---|---|---|---|
| 1 | `python verification/DIAG-READING-EXPORT-001-FIX-B/probe-heartbeat-leak-fixed.py` | TASK-012-py312，Git Bash | 7/7 检查 PASS，LEAK CLOSED | 0 | [probe log](../../verification/DIAG-READING-EXPORT-001-FIX-B/probe-heartbeat-leak-fixed.log) |
| 2a | 定向（R1 交付时点） | 同上 | 163 passed | 0 | [targeted-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-B/targeted-suite.log) |
| 2b | 定向（R2 交付时点，含 :162 teardown） | 同上 | 163 passed | 0 | [targeted-suite-r2.log](../../verification/DIAG-READING-EXPORT-001-FIX-B/targeted-suite-r2.log) |
| 3a | 全仓（R1 交付时点） | 同上 | 1317 passed, 5 skipped, 1 warning | 0 | [full-suite.log](../../verification/DIAG-READING-EXPORT-001-FIX-B/full-suite.log) |
| 3b | 全仓（R2 交付时点） | 同上 | 1317 passed, 5 skipped, 1 warning | 0 | [full-suite-r2.log](../../verification/DIAG-READING-EXPORT-001-FIX-B/full-suite-r2.log) |

全仓 1317+5 与 FIX-A 集成基线 1316+5 的差值 = 本 Task 新增的 1 个回归测试；5 skip 口径与 FIX-A 相同。

## 4. 未跑项、残余边界与设计取舍（给 Reviewer 的要点）

0. **生产终结点缺口（R2 新增，DSH R-01）**：见 §2 AC1 披露——生产 QML/bootstrap 无 `closeReader`/`aboutToQuit`
   接线（禁止范围），生产路径为"报错一次后心跳自停"兜底而非"离开页面干净停止"；是否补接线交 Codex/用户裁决。
1. **`closeReader()` 自身的 `self._reading.close()` 仍 fail-loud**：若在连接已关闭后调用 `closeReader`，
   `ReadingService.close()` 的 `_touch/_persist` 会抛 `ProgrammingError`（保持"用户主动关闭时持久化失败
   必须被看见"的语义）。组合场景披露：心跳已因 stop-on-error 停止后，再调 `closeReader` 仍会抛（存储已关时）。
   测试 teardown 的正确顺序（先 `closeReader` 后 `conn.close()`）已在各处落实；`ReadingService.close` 对
   无章节有 `progress is None` 守卫，早期失败的测试 finally 不会二次抛错。
2. **捕获范围 = `sqlite3.Error`**（DSH R2 裁决：接受、不必收窄——收窄到 `ProgrammingError` 会漏掉
   `OperationalError` 等真实"存储不可用"形态）。**R2 增列残余边界（DSH R-06）**：stop 之后无重启路径，
   一次瞬时 `OperationalError`（如 `database is locked`）也会停表，阅读时长累积静默停止直到下次
   `openChapter()`；如需区分可恢复错误，另立 Task 按异常类型分类处理。
3. **产品排队投递行为未变**（同 FIX-A 口径）；**`heartbeatErrorChanged` 信号归属（DSH R-04）**：保留——
   它是状态通知语义的最小面，供下一个触碰 reader UI 的 Task 消费（Owner 未定）；当前 QML 未消费，
   Python 侧测试/调用方为观察者（已写进 docstring）。
4. **U1/U2 的历史归因**（历史那次具体是哪个用例留下活心跳）随泄漏面关闭而失去现实意义，未再单独立探针
   点名（修复前需要第三个诊断探针，已超上限；修复后该问题不可再发生）。
5. **约 6 秒/用例的心跳等待**：泄漏探针真实等待 2×5.8 s 心跳周期（真实 QTimer 路径，不接受缩短周期的
   模拟替代）；回归测试用同步 settle 调用（心跳同款函数），不等待真实周期，测试套件耗时不受影响。
6. **非 SQLite 存储失败不在捕获范围**（DSH 未覆盖风险 3）：`JsonProgressDocumentStore.write` 的
   `OSError` 等照常抛出（`sqlite3.Error` 捕获面之外的既有行为，本 Task 未扩大）。
7. **全仓 1 warning**（DSH 未覆盖风险 5）＝无关的 `imghdr` DeprecationWarning（Python 3.12 对该 stdlib
   模块的弃用告警，非本 Task 引入）。

## 5. 复现方式

```powershell
cd 'G:\CODEX\New Manga.worktrees\DIAG-FIX-B-zcode'
G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe verification/DIAG-READING-EXPORT-001-FIX-B/probe-heartbeat-leak-fixed.py
G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe -m pytest -q -p no:cacheprovider -rs tests/reading_export tests/core/test_bootstrap.py
```

## 7. R2 修订记录（DSH 首轮 changes_requested 处置）

DSH 首轮 Review（只读；沙箱 shell 不可用，以 base 等价 worktree 内容级比对）返回 `changes_requested`（2×P2、4×P3）。逐条处置：

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| R-01 | P2 | 生产终结点（closeReader/aboutToQuit 接线）为零而 AC1 整条标 PASS；Task 要求此时停止交 Codex 裁决 | **fixed（披露式）**：AC1 改为"泄漏形态不可复现=已达成；生产终结点接线=范围缺口"（§2），bootstrap/QML 属禁止范围故停止实现，交 Codex/用户裁决是否另立接线 Task |
| R-02 | P2 | teardown 未穷尽：test_viewmodels.py:162 + test_webtoon_tiles.py 三处 | **fixed（:162 补 try/finally closeReader）+ accepted（webtoon_tiles 三处按选项 ii 判定不收口并披露理由**：JSON-store 局部 VM、GC 即销毁 timer、无 sqlite 错误面；见 §2 AC3） |
| R-03 | P3 | docstring 引用不存在的 heartbeatError Property | **fixed**：docstring/注释改为 `heartbeat_error` 属性 + `heartbeatErrorChanged` 信号，注明无 QML 消费者 |
| R-04 | P3 | heartbeatErrorChanged 为死信号 | **accepted（保留 + 注明归属）**：状态通知最小面，供下一个 reader UI Task 消费；Python 侧为观察者（docstring 已注明） |
| R-05 | P3 | Handoff 变更面"8 文件"计数不实 | **fixed**：改分组口径"10 文件 = 代码 4 + 证据 4 + 治理 2" |
| R-06 | P3 | stop 后无重启路径；OperationalError 也停表 | **accepted + 披露**：§4.2 增列残余边界（瞬时 locked → 静默停表至下次 openChapter；分类处理另立 Task）；DSH 明确不建议收窄捕获范围 |

设计取舍裁决（Handoff §4）：(a) closeReader fail-loud 接受（含心跳停止后再调用的组合场景披露）；(b) `sqlite3.Error` 捕获范围接受不收窄；(c) 信号不改 QML。

R2 交付（`2a1078b6`）的 git 变更（`git diff --name-only 528ba4d4..2a1078b6`，5 文件）：`doc/handoffs/DIAG-READING-EXPORT-001-FIX-B-3ce82240.md`（本 Handoff 修订）、`src/ui/viewmodels/reader/viewmodel.py`（docstring/注释）、`tests/reading_export/test_viewmodels.py`（:162 try/finally teardown）、`verification/DIAG-READING-EXPORT-001-FIX-B/targeted-suite-r2.log`、`verification/DIAG-READING-EXPORT-001-FIX-B/full-suite-r2.log`。R2 重跑数值与 R1 相同（163 / 1317+5），仅证据指针更新至 `-r2.log`（§2 AC5、§3 表）。
