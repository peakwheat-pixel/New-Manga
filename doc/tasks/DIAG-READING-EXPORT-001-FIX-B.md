---
id: DIAG-READING-EXPORT-001-FIX-B
title: Reader heartbeat lifecycle fix (symptom B)
kind: fix
status: done
approval: released_by_user_overnight_2026-09-28
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: []
base_commit: a8b94df1f1ee091a9cca894c421e9ffc3ad30614
branch: agent/zcode/DIAG-READING-EXPORT-001-FIX-B-reader-heartbeat-lifecycle
worktree: G:/CODEX/New Manga.worktrees/DIAG-FIX-B-zcode
integration_commit: 9c9c9087b8f2a6e51fa670ab99486d4a11edff49
---

# DIAG-READING-EXPORT-001-FIX-B — Reader 心跳生命周期修复（症状 B）

## 来源与目标

[DIAG-READING-EXPORT-001](DIAG-READING-EXPORT-001.md) 定位的**症状 B**：`ReaderViewModel` 的 5 s `QTimer`
心跳由 `openChapter()` 启动、仅 `closeReader()` 停止（`src/ui/viewmodels/reader/viewmodel.py:42,69-72,104-105,110-112`）；
`settleReadingTime()`（`:441-451`）对"存储已关闭/连接失效"无保护。全仓中 `closeReader()` 仅被
`tests/reading_export/test_viewmodels.py:163` 调用过一次；`test_qml_contract.py`（多处 `openChapter`）与
`tests/core/test_bootstrap.py:604-611`（生产装配 + SQLite reading store）都不关闭读者。心跳在连接关闭后触发即
`sqlite3.ProgrammingError: Cannot operate on a closed database`（诊断探针 2 确定性复现，栈帧
`viewmodel.py:450 → service.py:241/377/380 → reading_export.py:84 → connection.py:292` 与历史 stderr 逐帧相同，
且失败后心跳仍 active、每 5 s 重复）。

目标：给读者心跳一个明确的终结点（离开读者页 / `closeReader` / `aboutToQuit` 的生产装配路径），并让
`settleReadingTime` 在存储不可用时不再写入——**不以 `try/except` 吞异常代替生命周期修复**；同时让测试在
teardown 关闭读者，使诊断未决项 U1（哪个用例留下活心跳）/U2（store 类型归属）在修复后自然收口。

**释放记录（2026-09-28 01:3x，用户全夜自主推进指令授权；FIX-A 集成后按串行规则释放）：** 本 Task 已由代行
Codex（ZCode 会话）释放为 `ready`。FIX-A 已 `done`（integration=`a8b94df1`，DSH r2 approved），`tests/reading_export/**`
写集合冲突解除。Owner=ZCode 开始实现，交付后交 DeepSeek Harness 非作者 Review；Integrator=代行 Codex（待追认）。

## 固定恢复点与角色

- 固定 base：`a8b94df1f1ee091a9cca894c421e9ffc3ad30614`（FIX-A 集成 merge，治理提交之前）。
- Owner：ZCode（本会话亲自实现）；非作者 Reviewer：DeepSeek Harness（诊断方，非修复作者）；Integrator：代行 Codex（ZCode 会话，待追认）。
- branch/worktree：`agent/zcode/DIAG-READING-EXPORT-001-FIX-B-reader-heartbeat-lifecycle` / `G:/CODEX/New Manga.worktrees/DIAG-FIX-B-zcode`。
- depends_on：`[]`（FIX-A 已 done；串行释放已执行）。

## Acceptance Criteria

- [x] 心跳生命周期闭环：泄漏形态（连接关闭后心跳触发写库）不再可复现——泄漏探针（真实事件循环跨 2 个完整心跳周期）7/7 PASS、EXIT=0、verdict=`LEAK CLOSED`（[probe log](../../verification/DIAG-READING-EXPORT-001-FIX-B/probe-heartbeat-leak-fixed.log)）。**部分达成披露（DSH R-01，代行 Codex 采信）**：`closeReader()` 终结点在 API/测试面成立，生产 QML/bootstrap 接线为零（禁止范围），生产路径由 stop-on-error 兜底；生产接线缺口登记为后续候选 Task（见集成记录）。
- [x] `settleReadingTime` 对存储不可用路径类型化处理：`except sqlite3.Error` → 停心跳 + `heartbeat_error` 属性 + `heartbeatErrorChanged` 信号；不吞（错误全文可断言、心跳死亡不重复）；DSH r3 确认捕获范围裁决成立。
- [x] 相关测试 teardown 关闭读者：6 处落点（reader fixture、3 个 qml_contract fixture、bootstrap finally、missing_translation 用例 try/finally）；webtoon_tiles 三处 JSON-store 局部 VM 按披露理由不收口（Handoff §2 AC3）；回归测试 `test_reader_heartbeat_stops_after_store_tear_down` 修前红（诊断探针 2 同构 artefact）修后绿。
- [x] U1/U2 收口：泄漏面关闭后"哪个用例留下活心跳"失去现实意义（修复后 teardown 都会关闭、即使泄漏也已类型化防御），结论记录于 Handoff §4.4。
- [x] 定向 163 passed、全仓 1317 passed/5 skipped（R1/R2 双轮同值），均 EXIT=0（Handoff §3 表 2a/2b/3a/3b）；skip=2 docTR+1 numpy+2 torch 逐条给原因，6 OpenSSL=shell PATH 口径已解释。
- [x] 未新增 skip、未放宽既有断言、不引入新依赖（`import sqlite3` 为 stdlib；DSH 三轮核对确认）。
- [x] Handoff 与非作者 Review 齐备：DSH R1 `changes_requested`（2P2+4P3 全处置）→ R2 复核"代码与测试面通过"（5 条文档缺口 N-01..N-05）→ R3 docs-only 返修后 [approved](../reviews/DIAG-READING-EXPORT-001-FIX-B-dsh-r3.md) @`f93ea667`；集成核验通过（[integration-9c9c9087](../../verification/DIAG-READING-EXPORT-001-FIX-B/integration-9c9c9087/integration.md)）。

## 允许修改范围（释放时最终冻结）

- `src/ui/viewmodels/reader/viewmodel.py`（心跳终结点与 `settleReadingTime` 存储不可用路径）。
- `tests/reading_export/**`（teardown 与回归测试）。
- `tests/core/test_bootstrap.py`（仅生产装配读者路径的 teardown）。
- `verification/DIAG-READING-EXPORT-001-FIX-B/**`、本 Task 文件、`doc/handoffs/DIAG-READING-EXPORT-001-FIX-B-*.md`。
- 只读参考：`src/bootstrap/**`、`src/infrastructure/sqlite/**`、诊断报告与探针 2。

## 禁止范围

不改 export 侧任何文件（FIX-A 范围）、SQLite 连接/存储实现本身（`src/infrastructure/sqlite/**`、
`src/application/reading/**` 只读）、Schema、Domain Contract、依赖清单、QML 文件、`src/bootstrap/**`；
不改写 DIAG-READING-EXPORT-001 的报告/Handoff/证据；不加 sleep/重试/skip、不以 try/except 吞 `ProgrammingError`。

## 验证 Gate（草案，释放时冻结命令与环境）

1. 心跳泄漏判别探针（诊断探针 2 修复版）：真实事件循环跨 ≥2 个心跳周期，0 次未处理异常，EXIT=0 入库。
2. `python -m pytest -q -p no:cacheprovider tests/reading_export tests/core/test_bootstrap.py` 全绿（passed/skipped 分列）。
3. 全仓 `python -m pytest -q -p no:cacheprovider -rs tests` 一次，结果如实记录；teardown 后无 `Cannot operate on a closed database` 噪音。
4. 非作者 Review approved + Codex 集成核验（scope/`diff --check`/合并历史完整）。

## 已知阻塞

- 无（已集成 done）。生产终结点接线缺口与 r3 的 2 条 P3 advisory 见集成记录（deferred/候选 Task）。

## 集成记录（Integrator=代行 Codex，2026-09-28）

- **三轮非作者 Review**：R1 `changes_requested`（2×P2 + 4×P3；[r1](../reviews/DIAG-READING-EXPORT-001-FIX-B-dsh-r1.md)）→ R2 返修后复核"代码与测试面通过"，剩 5 条文档缺口（[r2](../reviews/DIAG-READING-EXPORT-001-FIX-B-dsh-r2.md)）→ R3 docs-only 返修后 `approved` @`f93ea667`（[r3](../reviews/DIAG-READING-EXPORT-001-FIX-B-dsh-r3.md)）。报告逐字节导入，SHA256 见 `verification/DIAG-READING-EXPORT-001-FIX-B/review-dsh-import/sha256.txt`。
- **交付链**：claim `6e37f05d` → R1 `3ce82240`/`528ba4d4` → R2 `2a1078b6` → R3 docs `f93ea667`（Owner tip）。
- **集成 merge**：`9c9c9087b8f2a6e51fa670ab99486d4a11edff49`（parents `dbae0240`（Review 归档）+ `f93ea667`；Owner 历史未改写；唯一冲突 Task 文件取 Owner 交付版）。Owner 变更 12 路径全授权、禁改路径（bootstrap/QML/reading service/sqlite 实现）零命中、`diff --check` exit 0、集成 head 全仓 1317 passed/5 skipped EXIT=0。
- **AC1 范围缺口裁决（代行 Codex，待追认）**：本 Task 的诊断修复目标（泄漏噪音/重复写/测试泄漏面）全部达成，判 `done`；**生产终结点接线**（QML 离开读者页 / `aboutToQuit` 调 `closeReader`）登记为独立 `proposed` 候选 Task，不在本 Task 内实现。
- 诊断三症状至此全部修复落位：症状 A（FIX-A `done`）、症状 B（本 Task `done`）；DIAG-READING-EXPORT-001 `done`。
