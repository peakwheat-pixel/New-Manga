---
id: TASK-058
title: 应用退出时排空 workbench 运行线程（P-10 优雅退出）
kind: feature
status: in_review
approval: zcode_window_self_approved
suggested_owner: ZCode
owner: ZCode
reviewer: independent_subagent
depends_on: ["TASK-048"]
base_commit: 726c1bb
branch: agent/zcode/TASK-058-graceful-shutdown-drain
worktree: "G:/CODEX/New Manga.worktrees/TASK-058-zcode"
integration_commit: 414a8e1
---

# TASK-058：应用退出时排空 workbench 运行线程（P-10 优雅退出）

## 当前状态与 blocker（2026-09-20 台账复核）

当前置为 `in_review`，不再以 `done` 记账。现有 Handoff 记录了窗口内 `approved_subagent` 复验，但仓库 `doc/reviews/` 中没有对应的 TASK-058 Review 报告，因此缺少可固定 `base_commit=726c1bb`、被审 head 和 `decision` 的非作者 Review artefact。恢复条件：补入独立非作者 Review（至少覆盖 Architecture/Verification，并带完整 frontmatter 与结论），再由 Codex 核对后恢复 `done` 台账。

## 来源与目标

- 来源：`doc/10_CURRENT_STATE_AND_GAPS.md` §11 finding **P-10**（退出不排空 run）——ZCode 全权窗口 W11 动态插入切片，依据 97a69a9 授权「可自建 Task 文件并按前提性插队」。
- 证据：`src/bootstrap/app.py` `main()` 的三条退出路径（smoke_test / screenshot / 正常 exec）在退出后直接 `services.conn.close()`；`WorkbenchViewModel.shutdown`（`src/ui/viewmodels/workbench/viewmodel.py`，内部 `_progress_timer.stop()` + `_controller.shutdown()`）在 `src/` 内零调用者（rg 证实）。`RunController.shutdown`（`src/workbench/run_controller.py:96` 附近）已有完整语义：活动 run 非 PAUSED 时置 cancel_requested → `thread.quit()` → `wait(5000)`（超时不强杀，R-001 注释）→ deleteLater。
- 约束：TASK-048 起 worker 线程与主线程**共享同一 SQLite 连接**，因此排空必须发生在 `conn.close()` 之前。
- 可观察交付：应用任何正常退出路径都会先排空 workbench 运行线程（活动 run 收到取消、worker QThread 结束），再关闭共享连接；不新增存储实现、不改 run 语义。

## Acceptance Criteria

- [x] AC1：`main()` 的退出路径改为经统一函数 `_shutdown_services(services)` 收尾，该函数先 `services.workbench.shutdown()` 再 `services.conn.close()`（顺序固定，含 bootstrap 失败的 except 分支）。
- [x] AC2：真实装配下，存在活动 run 时调用 `_shutdown_services` 能让 worker QThread 在返回前排空（run 不再 running、线程结束），且共享连接随后才关闭。
- [x] AC3：判别力——新增用例在修前代码上失败（`_shutdown_services` 修前不存在：import 级失败 + 顺序契约失败）；仅钉既有 VM/Controller 语义的用例单独声明不计判别。
- [x] AC4：全仓测试 ≥5 次全绿（退出码 0、passed/skipped 分列），不新增 skip/xfail、不放宽既有断言。
- [x] AC5：不改 RunController/WorkbenchViewModel 的既有语义（shutdown 幂等性维持），不动 `src/ui/qml/**`。

## 允许修改范围

- `src/bootstrap/app.py`（main 尾部收口 + 新增 `_shutdown_services`）
- `tests/core/**`（新增退出排空用例）
- `doc/tasks/TASK-058.md`、`doc/handoffs/TASK-058-*.md`、`verification/TASK-058/**`
- `doc/STATUS.md`（台账行）、`doc/README.md`（任务索引行）

## 禁止范围

- `src/ui/viewmodels/workbench/run_controller.py`、`src/ui/viewmodels/workbench/**`（仅复用，不改语义）
- `src/ui/qml/**`、Schema/migration、`requirements.txt`、`doc/10_CURRENT_STATE_AND_GAPS.md`
- 用户源文件 / Managed Copy / DB 结构

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 顺序契约 | `pytest tests/core/test_shutdown_drain.py -q`（文件自包含，单跑可复现） | TASK-012-py312 venv | 3 passed, EXIT=0 | verification/TASK-058/standalone-file.log |
| AC2 真实排空 | 同上（真实装配 + 离开 PENDING 的 run） | 同上 | 3 passed, EXIT=0（同文件）；目录 -k 形态同绿 | verification/TASK-058/directory-k.log |
| AC4 全仓 ×5+1 | `pytest tests -q` | 同上 | 911 passed / 0 skipped, EXIT=0 ×6（分支）；集成后 master 911 passed, EXIT=0 | verification/TASK-058/run01..06.log、post-integration-master-full-suite.log |
