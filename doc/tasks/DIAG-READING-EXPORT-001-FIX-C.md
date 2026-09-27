---
id: DIAG-READING-EXPORT-001-FIX-C
title: Production reader-page-leave and quit wiring for closeReader (heartbeat endpoint wiring)
kind: fix
status: done
approval: released_by_user_overnight_2026-09-28
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: []
base_commit: 0e34c5c3c0a753be3e9f310daa0e413959f4ca5d
branch: agent/zcode/DIAG-READING-EXPORT-001-FIX-C-quit-and-leave-wiring
worktree: G:/CODEX/New Manga.worktrees/DIAG-FIX-C-zcode
integration_commit: 0f2e9e31a666eddb4c9b8e17fb5401567c7e3924
---

# DIAG-READING-EXPORT-001-FIX-C — 生产侧读者心跳终结点接线（离开读者页 / 退出）

## 来源与目标

[DIAG-READING-EXPORT-001-FIX-B](DIAG-READING-EXPORT-001-FIX-B.md) `done` 时披露的范围缺口（DSH R-01，集成时由
代行 Codex 裁决转出）：`closeReader()` 作为读者心跳终结点仅在 API/测试面成立；生产 QML 从不调用、
`aboutToQuit` 无接线——生产路径是"存储消失后报错一次 → 心跳自停"兜底，而非"离开页面/退出时干净停止"。

目标（**纯 Python bootstrap 接线，零 QML 改动**）：在 [bootstrap](../../src/bootstrap/app.py) 中
1. 订阅 `NavigationViewModel.currentPageChanged`：当从读者页导航离开（目标页 ≠ reader 页）且读者有打开章节时，
   调用 `services.reader.closeReader()`（flush 进度 + 停心跳）；
2. 在 `QGuiApplication.aboutToQuit` 上接线 `services.reader.closeReader()`，退出时干净停止心跳。

设计约束：接线不改变任何页面语义（在读者页内的 `enterReader`/`openChapter` 触发的 `currentPageChanged`
不得误关闭）；`closeReader` 幂等安全（无章节时 `progress is None` 守卫）；不改 `NavigationViewModel`/
`ReaderViewModel` 语义、不改 QML、不改 reading service。

## 固定恢复点与角色

- 固定 base：`0e34c5c3c0a753be3e9f310daa0e413959f4ca5d`（FIX-B 集成治理 commit；释放时 main HEAD）。
- Owner：ZCode（本会话亲自实现）；非作者 Reviewer：DeepSeek Harness；Integrator：代行 Codex（待追认）。
- branch/worktree：`agent/zcode/DIAG-READING-EXPORT-001-FIX-C-quit-and-leave-wiring` / `G:/CODEX/New Manga.worktrees/DIAG-FIX-C-zcode`。
- depends_on：`[]`（FIX-B 已 done）。

## Acceptance Criteria

- [x] 离开读者页触发 `closeReader`：装配级测试 `test_navigation_away_from_reader_closes_it`（生产 `assemble_services` + 真实 SQLite）红→绿（PRE EXIT=1 / POST EXIT=0）。**AC1 文本集成裁决（DSH F-1，代行 Codex 采信其建议）**：AC 原文"断言 `hasChapter is False`"为文本缺陷——`closeReader` 的冻结语义（FIX-B）只 flush+停心跳、不清 `hasChapter`，AC1 有效契约修订为"心跳停止 + 进度 flush（`hasChapter` 按 `ReadingService.close()` 既有语义保留）"；实现按修订后契约核验通过。
- [x] 在读者页内不误触发：`enterReader`（emit `"reader"`）守卫永不关闭；R3 re-arm 幂等守卫（同章节+心跳活 → 不重开）与 N-1 离园时长不计入判别测试（模拟 600s 缺席，`total_read_seconds` 增量 <1.0s）锁定。
- [x] `aboutToQuit` 接线：`main()` 内 `_close_reader_on_quit`（F-6 stderr 守卫）在 exec 返回、`_shutdown_services` 关连接之前执行；无自动化测试（DSH 两轮裁决可接受——一行标准 connect，smoke 子进程实跑覆盖，Handoff §4 披露）。
- [x] 定向 210 passed、全仓 1318 passed/5 skipped（R4 最终套件），均 EXIT=0；skip=2 docTR+1 numpy+2 torch 逐条给原因；集成 head 复跑见集成记录。
- [x] 未新增 skip、未放宽断言、不引入新依赖；零 QML/Schema/Contract/reading service 改动（DSH 六轮核验确认）。
- [x] Handoff 与非作者 Review 齐备：六轮循环 R1 `approved`（6×Minor）→ R2/R3/R4/R5 `changes_requested`（逐轮处置）→ R6 [approved](../reviews/DIAG-READING-EXPORT-001-FIX-C-dsh-r6.md) @`0e0e699e`；报告逐字节导入（SHA256 于 review-dsh-import）；集成核验通过（[integration-0f2e9e31](../../verification/DIAG-READING-EXPORT-001-FIX-C/integration-0f2e9e31/integration.md)）。

## 允许修改范围

- `src/bootstrap/**`（`app.py` 的导航离开/退出接线；不改装配语义）。
- `tests/core/**`（接线断言测试）、`tests/reading_export/**`（如需）。
- `verification/DIAG-READING-EXPORT-001-FIX-C/**`、本 Task 文件、`doc/handoffs/DIAG-READING-EXPORT-001-FIX-C-*.md`。
- 只读参考：`src/ui/viewmodels/navigation/**`、`src/ui/viewmodels/reader/**`、`src/ui/qml/**`。

## 禁止范围

不改任何 QML 文件、`src/application/**`、`src/infrastructure/**`、Schema、Domain Contract、依赖清单、
其他页面 ViewModel；不改写 DIAG/FIX-A/FIX-B 的报告/Handoff/证据；不加 sleep/重试/skip。

## 验证 Gate

1. 接线断言测试红→绿证据入库（`verification/**`）。
2. `python -m pytest -q -p no:cacheprovider tests/core` 与 `tests/reading_export` 全绿（分列）。
3. 全仓一次，结果如实记录。
4. 非作者 Review approved + Codex 集成核验（scope/`diff --check`/合并历史完整）。

## 已知阻塞

- 无。


## 集成记录（Integrator=代行 Codex，2026-09-28）

- **六轮非作者 Review**：R1 `approved`（F-1..F-6 六×Minor）→ R2 `changes_requested`（N-1 P2 离园时长计入 + N-2..N-5）→ R3 `changes_requested`（T-1 断言时钟敏感性 + T-2..T-4）→ R4 `changes_requested`（H-1..H-3 纯文档）→ R5 `changes_requested`（H-3 尾项 AC4 指针）→ R6 [approved](../reviews/DIAG-READING-EXPORT-001-FIX-C-dsh-r6.md) @`0e0e699e`。报告逐字节导入，SHA256 见 `verification/DIAG-READING-EXPORT-001-FIX-C/review-dsh-import/sha256.txt`。
- **交付链**：claim `b1f4cedf` → R1 `de0bf175` → R2 `e9f61f5b` → R3 `132aa5e1` → R4 `46c7ff5a` → R5 `5d541bee`（doc）→ R6 `0e0e699e`（doc，Owner tip）。
- **集成 merge**：`0f2e9e31a666eddb4c9b8e17fb5401567c7e3924`（parents `601371f5`（Review 归档）+ `0e0e699e`；Owner 历史未改写；唯一冲突 Task 文件取 Owner 交付版）。Owner 变更 15 路径全授权（产品仅 `src/bootstrap/app.py`）、禁改路径零命中、非日志 `diff --check` 干净、集成 head 全仓 EXIT=0（见集成核验记录）。
- **F-1/AC1 裁决（代行 Codex，待追认）**：采信 DSH F-1 建议——AC1 原文 `hasChapter is False` 为文本缺陷（与 FIX-B 冻结的 closeReader 语义矛盾），修订为"心跳停止 + 进度 flush"；实现按修订契约核验通过，非实现缺陷。
- **诊断家族终态**：DIAG（诊断）+ FIX-A（症状 A）+ FIX-B（症状 B 生命周期）+ FIX-C（生产接线）全部 `done`；历史 reading_export flaky 的两个机制均已修复落地；唯一未决知识项 = 诊断 U3（真实全仓触发条件，知识性）。