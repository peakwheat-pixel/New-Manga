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
base_commit: cc4d9660b3f30d32b87d80c440e2dceb323c6a99
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

- [ ] **AC ①（驱逐 + 判别力）**：给出驱逐时机与并发安全的理由（worker 线程结束 / run 终态 / 显式 release；**不得**在另一线程仍持有该连接时回收）；新用例证明**连接注册表大小与打开连接数不随 run 数线性增长**（修前应呈 `1 → N+1`，修后应有界），并留修前/修后对照。
- [ ] **AC ②（解析一致性 + 判别力）**：`remove_managed` 对「**根内** junction / 符号链接指向**同根受保护文件**」必须 **typed 拒绝**、且**目标文件存活**；对合法删除路径零回归。用例可用 `mklink /J`（或等价模拟，须写明限制），并断言"目标存在 + 返回 typed 拒绝"。
- [ ] **AC ③（R-011）**：`"." in parts` 死条件**删除或改成真的生效**，并有用例说明 `.` 段的实际行为（不得留"看起来覆盖了"的假象）。
- [ ] **AC ④（供 TASK-057 前置①引用）**：把「drained ⇒ 无其他写者」写成**可判定**形式（例如 release 之后断言无活动连接 / 无 `running` run），并在 Task 内写明 TASK-057 前置①应引用哪条断言。
- [ ] **AC ⑤（不回归）**：`tests/storage`、`tests/workbench`、`tests/maintenance`、`tests/core` 与全仓 **不得跌破 923 collected**（openssl 可用口径 `923 passed / 0 skipped`；本机 PowerShell 口径 `917 passed / 6 skipped`，总数须仍为 923）；不得新增 `skip`/`xfail`、不得放宽既有断言。
- [ ] **AC ⑥（证据口径）**：每份日志带 **EXIT 码** 与 **shell/venv 头**、逐次入库；判别力必须是 **artefact**（协议 §6 第 12 条，Q-009）。
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
| AC ① 驱逐 | 真实 `assemble_services` 连跑 N 次 run，读注册表大小与打开连接数（planned） | PowerShell + `TASK-012-py312`，不设 `QT_QPA_PLATFORM` | NOT_RUN | 无 |
| AC ② 解析一致性 | `mklink /J` 根内 junction 指向同根受保护文件，断言 typed 拒绝且目标存活（planned） | 同上（Windows） | NOT_RUN | 无 |
| AC ⑤ 全仓 | `pytest tests -q -rs` ×5（planned） | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- 依赖：TASK-060（每线程连接归属已落地，`e7de64d`）。
- 风险：驱逐时机与「连接可能仍被另一线程使用」冲突 ⇒ 必须给出并发安全论证（不能靠"应该没人在用"）。
- 风险：Windows 的 junction/符号链接行为与 POSIX 不同；用例须在 Windows 上可跑，并如实声明未覆盖的链接形态。
- 阻塞：无。

## 交付与运行记录

- Handoff：尚无。Review：尚无（Reviewer=`Qoder`，非作者）。实际测试：尚无（`ready`）。
- **最近状态（当前，唯一）**：2026-09-19 由 Codex 依 TASK-060 复审的 R-002/R-010/R-011 开立为 `ready`；base=`cc4d966`。`in_progress`（2026-09-19，开工于 master 头 `6cb0afb`，base 已是 master 头故无 merge；三项机制 spike 已完成：QThread 死亡会回收 `threading.local` 值、`_DummyThread` 残留 enumerate 故死线程扫描不可用、`sqlite3.Connection` 不可弱引用 ⇒ 驱逐采用 lease 哨兵 + weakref 回调方案）。
