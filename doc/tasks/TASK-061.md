---
id: TASK-061
title: 连接注册表驱逐与 remove_managed 解析一致性（R-002 / R-010 / R-011）
kind: bugfix
status: in_progress
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: Qoder（非作者）
depends_on: [TASK-060]
base_commit: 6cb0afb5e53a229c700b0570d19f0f03c9942811
branch: agent/zcode/TASK-061-connection-eviction
worktree: G:/CODEX/New Manga.worktrees/TASK-061-zcode
integration_commit: null
---

# TASK-061：连接注册表驱逐与 `remove_managed` 解析一致性

**READY（2026-09-19，用户批准"开 TASK-061"）**：Owner=`ZCode`、Reviewer=`Qoder`（**非作者**）、base=`cc4d966`。开工先 `git merge master`（若 base 已是 master 头则无操作）并置 `in_progress`。

## 来源与目标

来源＝[TASK-060 复审](../reviews/TASK-060-b28c615.md)的三条 open 项（Reviewer 明确要求"作为后续小切片立案，别让它们无声消失"）：

- **R-002（P2）**：`src/infrastructure/sqlite/connection.py:76-91,105-116` 的每线程连接注册表按 `threading.get_ident()` 键控且**永不驱逐** ⇒ 每个 run 的 worker 线程留下**一条打开的连接**直到进程退出。**这是 TASK-057 前置①（活动写者门）的结构卡点。**
- **R-010（P2）**：`src/infrastructure/filesystem/managed_storage.py:122-142` 的组件规则是**词法**的，而根包含检查跑在 `.resolve()` 之后 ⇒ 经**根内 junction / 符号链接**的穿越不含 `..` 文本即可删除同根另一页的**受保护原件**（与刚闭合的 R-001 同后果、同威胁门槛）。
- **R-011（P3）**：`managed_storage.py:138` 的 `"." in parts` 是**死条件**（`PurePosixPath("./x").parts` 丢掉 `.`），给了"已覆盖 `.`"的错觉。

**目标**：让连接与打开的连接数**有界**（不随 run 数增长）、让删除守卫**解析前后一致且拒 reparse**、并清掉死条件；顺带把 TASK-057 前置①写成**可判定**的形式。

## Acceptance Criteria

- [x] **AC ①（驱逐 + 判别力）**：给出驱逐时机与并发安全的理由（worker 线程结束 / run 终态 / 显式 release；**不得**在另一线程仍持有该连接时回收）；新用例证明**连接注册表大小与打开连接数不随 run 数线性增长**（修前应呈 `1 → N+1`，修后应有界），并留修前/修后对照。
- [x] **AC ②（解析一致性 + 判别力）**：`remove_managed` 对「**根内** junction / 符号链接指向**同根受保护文件**」必须 **typed 拒绝**、且**目标文件存活**；对合法删除路径零回归。用例可用 `mklink /J`（或等价模拟，须写明限制），并断言"目标存在 + 返回 typed 拒绝"。
- [x] **AC ③（R-011）**：`"." in parts` 死条件**删除或改成真的生效**，并有用例说明 `.` 段的实际行为（不得留"看起来覆盖了"的假象）。
- [x] **AC ④（供 TASK-057 前置①引用）**：把「drained ⇒ 无其他写者」写成**可判定**形式（例如 release 之后断言无活动连接 / 无 `running` run），并在 Task 内写明 TASK-057 前置①应引用哪条断言。
- [x] **AC ⑤（不回归）**：`tests/storage`、`tests/workbench`、`tests/maintenance`、`tests/core` 与全仓 **不得跌破 923 collected**（openssl 可用口径 `923 passed / 0 skipped`；本机 PowerShell 口径 `917 passed / 6 skipped`，总数须仍为 923）；不得新增 `skip`/`xfail`、不得放宽既有断言。
- [x] **AC ⑥（证据口径）**：每份日志带 **EXIT 码** 与 **shell/venv 头**、逐次入库；判别力必须是 **artefact**（协议 §6 第 12 条，Q-009）。
- [ ] **AC ⑦** Handoff + `verification/TASK-061/**` + **非作者** Review + 集成；集成后 STATUS 登记，并标注 **TASK-057 前置①是否已可判定**。

## 允许修改范围

- `src/infrastructure/sqlite/connection.py`
- `src/infrastructure/filesystem/managed_storage.py`
- 若确需调用点配合：`src/application/maintenance/**`（须在 Task/Handoff 说明理由）
- `tests/storage/**`、`tests/workbench/**`、`tests/maintenance/**`、`tests/core/**`
- 本 Task、Handoff、`verification/TASK-061/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 Schema/migration、`requirements.txt`、`src/ui/qml/**`、`AGENTS.md`、其他 Task；**不得回滚 TASK-060 的归属改动**；不得放宽断言或新增 skip/xfail；不 push。
- **TASK-057 不要碰**（仍冻结；本切片只负责让它的前置①"可判定"）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC ① 驱逐 | 真实 `assemble_services` 连跑 4 次 TRANSLATE_ALL，读 `registry_size()`/`open_connection_count()`；修前树 `6cb0afb` detached 复跑同用例取对照 | PowerShell + `TASK-012-py312`，不设 `QT_QPA_PLATFORM` @ 6cb0afb（修前）/032dc3a（修后） | PASS：修前 [2,3,4,5] 单调增长（FAIL 判别）→ 修后 [1,1,1,1]、open ≤2 | `verification/TASK-061/prefix-discrimination/connection-eviction-prefix-run1.log`（EXIT=1）+ `tests/workbench/test_connection_eviction.py` |
| AC ② 解析一致性 | `mklink /J` 根内 junction（books/book-twin → books/book-1）指向同根受保护原件，断言 typed 拒绝且目标存活；修前树另跑取证脚本展示"删除成功 + 目标消失" | 同上（Windows NTFS） @ 6cb0afb/032dc3a | PASS：修前 `DID NOT RAISE` + helper `exists: False`（目标确实被删）→ 修后 typed 拒绝 + 目标存活 | `verification/TASK-061/prefix-discrimination/managed-storage-bookjunction-prefix-run2.log`（pytest EXIT=1 / helper EXIT=0）+ `tests/storage/test_managed_storage.py::TestR010ReparseWalk` |
| AC ⑤ 全仓 | `python -m pytest -q -p no:cacheprovider`（全仓）×5 | 同上 @ 032dc3a | PASS：5/5 次 930 passed / 0 skipped，EXIT=0（collected 930 = 923 基线 + 7 新增） | `verification/TASK-061/full-suite/full-suite-run{1..5}.log` |

## 依赖、风险与阻塞

- 依赖：TASK-060（每线程连接归属已落地，`e7de64d`）。
- 风险：驱逐时机与「连接可能仍被另一线程使用」冲突 ⇒ 必须给出并发安全论证（不能靠"应该没人在用"）。
- 风险：Windows 的 junction/符号链接行为与 POSIX 不同；用例须在 Windows 上可跑，并如实声明未覆盖的链接形态。
- 阻塞：无。

## 交付与运行记录

- **实现 commit（本分支）**：`032dc3a`（bounded registry + reparse walk + live dot rule + 判别用例 + 修前判别 artefact）；文档 commit `cbf64f1`。基线 master=`6cb0afb`。
- **AC① 驱逐设计与并发安全论证**：每个 thread-local 槽位同时持一个可弱引用的 lease 哨兵（`_ConnectionLease`，`__slots__=("__weakref__",)`），lease 的 weakref 回调做驱逐（registry 弹槽 + close）。**回调只能在该线程的 thread-local 被销毁后触发**——CPython 引用计数保证触发时除回调闭包外无任何代码可再拿到该连接，即"绝不回收另一线程仍持有的连接"由结构保证，不靠时序。spike 实证（见 `cbf64f1` 记录）：QThread 线程死亡会回收其 `threading.local` 值；`_DummyThread` 死后残留 `threading.enumerate()` 故"死线程扫描"不可用；`sqlite3.Connection` 不可弱引用故需哨兵代理。另提供 `release_current_thread_connection()`（仅调用线程自己，显式路径）、`registry_size()` / `open_connection_count()` 可观测。修前/修后对照（e2e 判别 artefact）：修前 4 次 run registry 呈 **[2,3,4,5]** 单调增长（`connection-eviction-prefix-run1.log`），修后 **[1,1,1,1]**、open ≤2。
- **AC④ 可判定断言（供 TASK-057 前置①引用）**：`ThreadRoutedConnection.any_in_transaction()` 聚合"是否还有任何已注册连接在事务中"（直读注册连接、不建新连——R-004 的 `in_transaction` 本线程语义坑已在类 docstring 声明）。**TASK-057 前置①应引用**：`workbench.shutdown() is True and not services.conn.any_in_transaction()` ⇒ drained 且无其他写者（restore/备份门）。
- **AC②③**：`remove_managed` 现为三层守卫——原始段词法（`.`/`..`/空中段，直接 `split("/")`，R-011 死条件清除）→ resolve 后根包含 → **未解析路径逐级 lstat 拒 reparse point**（junction/symlink，Windows 用 `FILE_ATTRIBUTE_REPARSE_POINT`，POSIX 用 `S_ISLNK`）。junction 用例以 `mklink /J` 构造（声明限制：仅目录 junction 形态；文件符号链接需开发者模式未覆盖）。
- **实际测试**（同一 shell + 同一 venv：PowerShell + `TASK-012-py312`，`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`、未设 `QT_QPA_PLATFORM`；每份日志带 EXIT + shell/venv 头）：
  - 判别力（修前树 `6cb0afb` detached，新用例复制入树未提交）：`verification/TASK-061/prefix-discrimination/`——e2e 驱逐 **1 failed，registry=[2,3,4,5]**（EXIT=1，失败文本即 R-002 机理）；connection 单元 **3 failed**（新 API 缺失，EXIT=1）；managed_storage **3 failed**（junction 删除成功/`.` 段删除成功，EXIT=1；既有 7 例仍 passed）。
  - 修后：四目录回归 **178 passed**；全仓 `verification/TASK-061/full-suite/full-suite-run{1..5}.log`——**5/5 次 930 passed / 0 skipped、EXIT=0**；collected 930 = 923（master `6cb0afb` 基线，openssl 可用口径）+ **7 个本切片新增用例**，未跌破基线、未新增 skip/xfail、未放宽既有断言。
- **AC⑦**：Handoff 见 [TASK-061-zcode-handoff](../handoffs/TASK-061-zcode-handoff.md)；Review 待 Qoder（非作者）。
- **最近状态（当前，唯一）**：2026-09-19 实现完成、AC①~⑥ 证据齐备；待 Qoder Review + 集成 + STATUS 登记（集成时标注 TASK-057 前置①已可判定）。
