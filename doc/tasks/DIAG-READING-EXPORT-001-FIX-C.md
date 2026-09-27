---
id: DIAG-READING-EXPORT-001-FIX-C
title: Production reader-page-leave and quit wiring for closeReader (heartbeat endpoint wiring)
kind: fix
status: in_progress
approval: released_by_user_overnight_2026-09-28
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: []
base_commit: 0e34c5c3c0a753be3e9f310daa0e413959f4ca5d
branch: agent/zcode/DIAG-READING-EXPORT-001-FIX-C-quit-and-leave-wiring
worktree: G:/CODEX/New Manga.worktrees/DIAG-FIX-C-zcode
integration_commit: null
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

- [ ] 离开读者页触发 `closeReader`：装配级测试断言（`assemble_services`/engine 后 `enterReader` 打开章节 → `navigation.navigate(<非 reader 页>)` → 断言 `services.reader.hasChapter is False` 且心跳已停、进度已持久化）；对修前行为红（接线缺失时 hasChapter 仍 True）。
- [ ] 在读者页内不误触发：`enterReader`/`openChapter` 与读者页内操作后断言读者仍打开、心跳仍活。
- [ ] `aboutToQuit` 接线：装配/退出路径测试断言心跳停止。
- [ ] 定向套件（`tests/core`、`tests/reading_export` 相关）与全仓一次；passed/skipped 分列，skip 逐条给原因。
- [ ] 未新增 skip、未放宽断言、不引入新依赖；不改 QML/Schema/Contract/reading service 语义。
- [ ] Handoff 与非作者 Review 齐备；Codex 集成核验通过后才可 `done`。

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
