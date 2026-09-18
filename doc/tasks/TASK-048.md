---
id: TASK-048
title: 修复生产任务执行的跨线程 SQLite 连接（§11 P-1，P0）+ 生产路径端到端测试资产
kind: bugfix
status: in_progress
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: 窗口内独立子对话（approved_subagent；T1 后由 Codex/DSH/Qoder post-hoc）
depends_on: [TASK-013, TASK-038]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-048-thread-sqlite
worktree: G:/CODEX/New Manga.worktrees/TASK-048-zcode
integration_commit: null
---

# TASK-048：跨线程 SQLite 连接（§11 P-1）+ 生产路径端到端测试资产

**READY（2026-09-19，ZCode 全权窗口 W1）**：Owner=`ZCode`、Reviewer=**窗口内新开的独立子对话**（不得自审；结论只能 `approved_subagent`/`changes_requested`）、base=`8bf8da3`。开工先 `git merge master`，再把 `status` 置 `in_progress`。

## 来源与目标

来源＝[10 现状与差距](../10_CURRENT_STATE_AND_GAPS.md) §11 第 1 项（P0）与 [Qoder 盘点复核](../../verification/POSTHOC-REACHABILITY-AUDIT-2026-09-18/codex-verification.md)：

- `src/bootstrap/app.py:426` 在启动线程 `open_database(...)`；`src/infrastructure/sqlite/connection.py:58` 为 `sqlite3.connect(str(path))`（无 `check_same_thread=False`，全仓无按线程取连接的机制）；
- `src/ui/viewmodels/workbench/viewmodel.py` 把**同一个** `PipelineService` 交给 `RunController`，后者用 `QThread` + `moveToThread` + queued `_startRequested` 在 worker 线程执行 `execute_run`；
- 结果：首个 store 访问即 `sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread`，被 `_Worker.execute` 的 `except Exception` 吞成 `runCrashed`，又因 `commandError` 无 QML 消费者（TASK-052）而对用户完全静默；
- **Reviewer 已端到端复现**（真实 `assemble_services` + 真实 `RunController` → `runCrashed` 报该错误；同装配在主线程可跑完 ⇒ 纯连接归属问题），并发现**崩溃后 run 在 DB 停留 `running`**。

**目标（可观察）**：从生产装配出发，经 worker 线程执行一条完整命令，**不再出现跨线程异常**；run 落到终态（含失败语义）；并新增一条穿过"生产装配 + 真 SQLite + worker 线程"的**端到端测试资产**（§11 P-11 点名的证据缺口）。

## Acceptance Criteria

- [x] **AC ①（根因与方案）**：写明连接归属方案与理由（每线程取连接 / 连接工厂 / 串行化访问；若采用 `check_same_thread=False` 必须说明 WAL/锁语义与**串行化**策略）。方案须解释为何不产生并发写竞争，并给出并发的负向用例或论证。
- [x] **AC ②（端到端不复现）**：真实 `assemble_services` + 真实 `RunController`(QThread) 跑一条 `TRANSLATE_ALL`：**不再出现** `ProgrammingError`；给出修复前后对照（修前必须复现，作为判别力）。
- [x] **AC ③（run 终态）**：崩溃路径消失后，run **不再停留 `running`**；同时把 `PipelineService.recover_running_runs()` 接入**生产启动路径**（`src/bootstrap/app.py`），并有用例证明启动即可回收上轮遗留的运行中记录。
- [x] **AC ④（新增端到端测试资产）**：新增一条集成测试：`assemble_services` + 真实 SQLite 文件 + worker 线程（`RunController`）+ 一条完整命令，断言"能跑完 + DB 落终态"。该用例对**修前**代码失败（判别力留证）。
- [x] **AC ⑤（不回归）**：`tests/storage/**`、`tests/core/**`、`tests/workbench/**` 既有断言**逐条不变**；全仓 passed 不减少；全仓 ≥5 次逐次记录（同一 shell + 同一 venv；**不得设 `QT_QPA_PLATFORM`**）。
- [ ] **AC ⑥** 交付 Handoff、`verification/TASK-048/**`，经**独立子对话** Review + 集成后才能 done；STATUS 台账行记录结论。（实现/取证/Handoff 已交付，独立子对话 Review 与集成进行中）

## 允许修改范围

- `src/infrastructure/sqlite/**`（连接归属/工厂；**不得改 Schema/migration**）
- `src/bootstrap/app.py`（装配与启动回收）
- `src/application/tasks/**`（若有并发/事务边界需要）
- `src/ui/viewmodels/workbench/**`（若 worker 侧需要）
- `tests/storage/**`、`tests/core/**`、`tests/workbench/**`
- `doc/tasks/TASK-048.md`、`doc/handoffs/TASK-048-*.md`、`verification/TASK-048/**`、`doc/STATUS.md`（仅台账行）

## 禁止范围

- 不得改 Schema/migration、`requirements.txt`、pipeline seam 本体、`AGENTS.md`、其他 Task；确需 Schema 或依赖 → **停切片、记 BLOCKED、转下一项**（见窗口章程）。
- 不得用"全局加锁 + 吞掉异常"掩盖问题；不得放宽/删除既有断言；不得新增 `skip`/`xfail`；不 push。
- 不得把 `check_same_thread=False` 当作唯一措施而不说明并发控制。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC ② 修前复现 | `python verification/TASK-048/thread_probe_pre.py <tree>` | venv `TASK-012-py312` | 修前 ×2 `OUTCOME=crashed`（sqlite3.ProgrammingError）；修后 ×2 `OUTCOME=finished, status=completed_with_failures` | `thread-{pre,post}-fix-run{1,2}.txt` |
| AC ④ 端到端新用例 | `pytest tests/workbench/test_run_thread_e2e.py -q` | 同上 | 修后 3 passed；修前树 3 failed / exit 1（判别力，失败文本=跨线程异常） | `discriminating-new-tests-vs-prefix.log` |
| AC ⑤ 定向 | `pytest tests/storage tests/core tests/workbench -q` | 同上 | **126 passed / 0 skipped，exit 0** | `targeted-storage-core-workbench.log` |
| AC ⑤ 全仓 | `pytest -q -rs` ×5 | 同上，不设 `QT_QPA_PLATFORM` | **854 passed / 0 skipped / exit 0 ×5**（851 基线 + 3 新用例；无新 skip） | `full-suite-post-fix-run{1..5}.log` |

## 依赖、风险与阻塞

- 硬依赖：TASK-013（worker 执行）、TASK-038（生产装配）——均 done。
- 风险：SQLite 并发写语义（`database is locked`）与事务边界；WAL 与 `PRAGMA` 现状需先查明（`_apply_pragmas`）。
- 风险：`recover_running_runs()` 接入启动路径可能影响既有启动时序用例 → AC ⑤ 覆盖。

## 交付与运行记录

- Handoff：[TASK-048-011ee16.md](../handoffs/TASK-048-011ee16.md)。Review：独立子对话（进行中）。实际测试：修前判别 1 次（3 failed / exit 1）+ 探针前后各 ×2 + 定向 126/0 + 全仓 ×5（854/0 ×5），全部入库 `verification/TASK-048/`。
- **最近状态（当前，唯一）**：2026-09-19 ZCode 开工（merge master `7537136` 后置 `in_progress`）；实现提交 `011ee16`（`check_same_thread=False` + AC① 论证入 `connection.py` docstring + `recover_running_runs()` 接入启动装配 + 3 条端到端用例）；AC ①～⑤ 达成，AC ⑥ 待独立子对话 Review + 集成。`base=8bf8da3`。
