---
id: TASK-057
title: TASK-021 冻结子集③：备份与恢复
kind: implementation
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: Qoder（历史交付复审 + T1.3.1 Round 4 独立非作者 Reviewer，approved）
depends_on: [TASK-021, TASK-053]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-057-backup-restore
worktree: G:/CODEX/New Manga.worktrees/TASK-057-zcode
integration_commit: 38d6eaaefe9d344d8534996f469f2ba868922845
---

# TASK-057：备份与恢复（TASK-021 冻结子集③）

**READY（2026-09-19，ZCode 全权窗口 W10）**：Owner=`ZCode`、Reviewer=**独立子对话**、base=`8bf8da3`。**前置：TASK-053 已集成**（备份/恢复必须建立在 purge/孤儿文件语义已收口之上）。既有材料：`src/infrastructure/sqlite/backup.py`、`backup_records` 表。

## 来源与目标

来源＝TASK-021 冻结子集之一。**目标**：可用的库备份与恢复（DB + 清单一致性），**不破坏用户源文件**，失败可诊断、可重试。

## Acceptance Criteria

- [x] **AC ①（备份完整性）**：备份产物包含 DB 与必要清单（形状自定但须写明），并在完成后校验可读；`backup_records` 落记录。
- [x] **AC ②（恢复语义）**：恢复路径明确**覆盖/合并**语义；恢复后指针（current/pinned/translated）与 Managed Copy 一致性有断言。
- [x] **AC ③（安全边界）**：备份/恢复**不写用户源文件目录**；路径必须落在受控范围内；异常时不留半成品（原子/可回滚）。
- [x] **AC ④（幂等与失败可诊断）**：失败返回 typed 原因；重复操作用例。
- [x] **AC ⑤（不回归 + 判别力）**：全仓 passed 不减少；≥5 次逐次记录（不设 `QT_QPA_PLATFORM`）。
- [x] **AC ⑥** Handoff + `verification/TASK-057/**` + 独立子对话 Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/application/**`、`src/infrastructure/sqlite/**`（备份/恢复相关；**待按实际结构收紧**）
- `src/ui/viewmodels/workbench/**`（仅 restore admission / Worker 生命周期门）
- `tests/storage/**`、`tests/core/**`
- `tests/workbench/**`（仅 restore admission / Worker 生命周期验证）
- 本 Task、Handoff、`verification/TASK-057/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 Schema/migration（确需 → BLOCKED）、`requirements.txt`、`AGENTS.md`、其他 Task、`src/ui/qml/**`；不得放宽断言或新增 skip；不 push。

## 交付与运行记录

- Handoff：[TASK-057-delivery.md](../handoffs/TASK-057-delivery.md)（冻结交付）。Review：Qoder 窗口复审维持冻结 + 三项前置（`doc/reviews/POSTHOC-WINDOW-2026-09-19-Qoder.md` Q-008）。实际测试：新套件 8/0 + 相邻 storage/core 97/0 + 全仓（4×912/0 有效绿 + 1 既有时序 flaky + 1 环境中断，逐次分列入库）。
- 2026-09-19 冻结交付（实现提交 `c5515fb`）：sidecar 清单 + `verify_backup_file` + typed `restore_backup`（覆盖语义/pre_restore 自动备份/一致性报告/sidecar 兜底）+ `BackupLedger` 端口。零 Schema/依赖/QML。
- **最近状态（被返修段取代）**：2026-09-19 ZCode 解冻前置切片（实现提交 `2707ea8`；范围=Q-008 前置②③ + R-004/R-005，Qoder Review）：① AC③ 恒真断言删 `or True` 补真实边界断言 ② R-004 三件式门（VM `beginRestore/endRestore` 闩拒绝全部 start 路径；`RunController`/`any_in_transaction` docstring 写明唯一写者前提与「快照非准入闸门」约束）③ R-005 聚合方向判别用例 ④ R-003/R-006 docstring 收窄 + N-002 `barrier.wait(5)` ⑤ backup.py 最小 facade 适配（`_current()`；超出开工指令字面白名单，依据原 Task 白名单 `src/infrastructure/sqlite/**` 执行，登记于 Handoff 交 Reviewer 裁定）。修前/修后判别探针与日志 `verification/TASK-057/pre-fix-probes/`（TRUTHY-PASS→DISCRIMINATING-FAIL、AttributeError→POST-FIX 双翻转）；全量 3×942 passed EXIT=0（`unfreeze-full-suite-run{1,2,3}.log`，942≥930 基线）。`base=50c4b1a`（开工 merge master `49f45f6` → `0d15018`）。Handoff：[TASK-057-unfreeze.md](../handoffs/TASK-057-unfreeze.md)。
- **最近状态（当前，唯一）**：2026-09-19 ZCode 返修（review `TASK-057-b0e4cb1` changes_requested R-001~R-006 闭合；闩落咽喉点）：① R-001 闩移至 `RunController`（`set_restore_latch`/`admission_closed`/`RestoreLatchClosedError`，`start()` 顶部置位即拒=唯一 worker 出生地），VM `beginRestore/endRestore` 转调控制器，`continueRun`/`_restart_or_abandon`/`retryFailedPages` 三面统一经 `_start_pending_worker`（typed 错误面），`_start_run` 前置检查保留（先于 create_run/plan_run 写拒绝）② R-002 `restoreGate()` 上下文管理器（主体抛异常 finally 解闩）③ 门测试 3→9 条真枚举四面（两 translate 入口 + PAUSED continueRun 真链路 + restart/retry 探针 MODE B 手法）各断言无 worker 出生 + 错误面命中 ④ R-004 三处 docstring 真话化（含 `connection.py any_in_transaction` 指向控制器咽喉点）⑤ R-006 两支判别探针翻转进 EXIT（0d15018 双 EXIT=1 / 修复树双 EXIT=0）。判别：门测试在 b0e4cb1 上 6/9 挂（三面 "worker was born"=R-001 复现）`review-b0e4cb1/gate-fix-discrim-b0e4cb1-run1.log`；Reviewer 探针复跑四面全 False+错误面命中 `probe-gate-fix-zcode-run1.log`。验证：定向 16 passed + 全仓 **948 passed EXIT=0**（942+6；`full-suite-fix-run1.log`）。942 差值实证（R-005）：`49f45f6`=930 → merge 头 `0d15018`=938（+8 冻结交付 storage 套件）→ 解冻切片=942（+4：R-005 1 + 门 3）→ 返修=948（+6 门测试扩枚举），各锚点 `--collect-only` 实测。Handoff：[TASK-057-unfreeze.md](../handoffs/TASK-057-unfreeze.md) 返修节（Reviewer=Qoder 复审，in_review）。
- **T1.3.1 reconciliation（2026-09-21，待独立复审）**：Codex 以 rebaseline activation `676319b` 为基线，无冲突合入固定 delivery `29546f7`（merge `3087975`）及 Qoder review 分支 `257ee5b`（merge `1433e02`）。Codex 明确追认上列 Workbench 路径，仅限 TASK-057 restore admission；R-008 以 `beginRestore()` 重入拒绝关闭，R-009 在 `continueRun` / restart / retry 的任何 control/plan 写入前拒绝，`abandonRun` 保持可用。实现提交 `3fa7958`，验证候选 `f92530e`；定向 18 passed、相关集成 28 passed、旧 reviewer choke-point probe EXIT=0、全仓同一 HEAD 5× **964 passed / 6 skipped / EXIT=0**（970 collected；6 条均为既有 `openssl unavailable`；无 xfail）。Handoff：[T1.3.1-TASK-057-integration.md](../handoffs/T1.3.1-TASK-057-integration.md)。
- **T1.3.1 Review round 1 / 返修（2026-09-21）**：独立 Review `8318b64` = `changes_requested`（[Review](../reviews/T1.3.1-TASK-057-8318b64.md)）。P1 R-001~R-005 与 P2 R-006 均留在本 Task 闭合：service 内 read-back；临时 DB + 失败清理 + typed create failure；backup ID/root 边界；DB/sidecar/ledger schema 交叉校验与 newer-schema 拒绝；真实 original/translated current+pinned 回滚证据；restart/retry 零调用与 abandon 放行。返修 delivery `940d373`；定向 26 passed、相关集成 44 passed、probe EXIT=0、全仓同一 HEAD 5× **972 passed / 6 skipped / EXIT=0**（978 collected，无 xfail）。R-007 历史 raw log 尾随空格保留为原始证据；返修源码/测试与本轮 evidence 子范围 `diff --check` 干净。状态仍 `in_review`，等待新 head 独立复审。
- **T1.3.1 Review round 2 / 返修（2026-09-21）**：独立 Review `d7e9aa9` = `changes_requested`（[Review](../reviews/T1.3.1-TASK-057-d7e9aa9.md)）；仅 R-002 原子发布窗口与新 R-010 v0 restore/typed rollback 仍开。delivery `b2dd525` 将 read-back/hash/sidecar 移到临时 DB，manifest→DB 发布并统一中断清理；旧 schema restore 后复用正式 migration，任何 write/post-check failure 用 pre-restore 自动回滚并保持 typed。定向 29 passed、相关集成 47 passed、probe EXIT=0、全仓同一 HEAD 5× **975 passed / 6 skipped / EXIT=0**（981 collected，无 xfail）。状态仍 `in_review`，等待 Round 3 独立复审。
- **T1.3.1 Review round 3 / 返修（2026-09-21）**：独立 Review `85832bb` = `changes_requested`（[Review](../reviews/T1.3.1-TASK-057-85832bb.md)）；R-002/R-010 已关闭，仅 R-011 前置 hash I/O typed mapping 未闭。delivery `0b957d1` 将该 `OSError` 映射为 `BACKUP_FILE_UNREADABLE`，并固定 live/ledger 不变断言。定向 30 passed、相关集成 48 passed、probe EXIT=0、全仓同一 HEAD 5× **976 passed / 6 skipped / EXIT=0**（982 collected，无 xfail）。状态仍 `in_review`，等待 Round 4 独立复审。
- **T1.3.1 Review round 4 / 批准（2026-09-21）**：独立非作者 Review **`approved`**，reviewed head `c79cd36`，review commit `ad17dbf`（[Review](../reviews/T1.3.1-TASK-057-c79cd36.md)；Reviewer=Qoder，Owner=ZCode，Rebaseline Integrator=Codex）。R-011 判定 **fixed**，判别力**双向实测**：交付测试在 pre-fix 源（`85832bb` 版 `backup.py` + head 版测试）上 **FAIL**（裸 `OSError: forced read failure`，EXIT=1），在 head 上 **PASS**；Reviewer 另以**真实 OS 失败**（Windows ACL read-deny，非 Mock）独立复现 `PermissionError/errno=13` —— pre-fix 树 `CODE=None` / probe EXIT=1，head 树 `CODE=BACKUP_FILE_UNREADABLE` / probe EXIT=0，且 live `artifact_revisions == 1`、`backup_records` 计数不变、backup root 无 pre_restore/tmp 半成品、ACL 复位后文件可再读。Reviewer 自有证据 21 件：`verification/TASK-057/review-c79cd36/**`（targeted 30/EXIT=0、affected integration 48/EXIT=0、chokepoint probe EXIT=0、全量 3×976 passed+6 skipped（PowerShell，PATH 取自注册表，openssl 不可见）与 5×982 passed（Git Bash，Git 自带 openssl 在 PATH 上故 6 条 skip 转为 pass；两口径 **collected 同为 982**，差值已在 Review 单处说明）、R-011 双向判别日志、`diff --check`/skip-xfail/scope-paths）。全范围复核：无禁止路径命中、无新增 skip/xfail（base 与 head 同为既有 5 处）、无断言放宽（`0b957d1` = `backup.py` +7/-1、测试 +27/-0）、历史 Review 结论未被修改。
- **T1.3.1 集成与收口（2026-09-21，AC⑥ 完成）**：`--no-ff` merge **`38d6eaa`**（parents `676319b` + `ad17dbf`）到 master，由 Qoder 作为用户本轮指定的集成代行者执行；`git diff --stat c79cd36 HEAD -- src tests` 与 `git diff --stat ad17dbf HEAD -- src tests` 均为空 ⇒ **合入内容 == 被审 head**。post-integration regression 在 master `38d6eaa`：**982 collected = 976 passed + 6 skipped / EXIT=0**（两次一致；6 条均为既有 `openssl unavailable`；无 xfail；`src`/`tests` 树 clean；`QT_QPA_PLATFORM` 未设）—— [integration-master-38d6eaa.log](../../verification/TASK-057/integration-master-38d6eaa.log)。相对 rebaseline 基线 951 collected 净增 31。`experiments/TASK-017/README.md` 与 `.qoder-credits/` 既有改动原样保留。**未 push**。回退方式：在 master 上 revert 本 merge commit（`git revert -m 1 38d6eaa`）；不得单独回退 restore gate 而保留其测试。
- **遗留登记（P2，不阻断 done）**：
  - **R-012（deferred）** `src/infrastructure/sqlite/backup.py:152-156`：restore 前置读 ledger 行的 `self._conn.execute(...)` 位于任何 typed 边界之外；当 live DB 没有 `backup_records` 表（v0 形态/未迁移）时抛裸 `sqlite3.OperationalError`，调用者拿不到 `code`。可达性极低（该表自 migration v1 即存在；backup service 至今未接线生产 bootstrap），且该失败发生在**任何写入之前**，AC③ 安全边界完好，影响仅限诊断面。**处置要求**：在把 backup service 接线到生产 bootstrap 的那个切片里，把 restore 前置 live 读（`backup_records` 缺失 / `database is locked` / `disk I/O error`）一并纳入 typed 映射（如 `LEDGER_UNREADABLE`）并补一条判别测试，否则该缺口会随接线变成可达。不需为本项单独返修 T1.3.1。证据：Reviewer probe Scenario B `LEDGER_READ_TYPE=OperationalError CODE=None`，同场景 live 未写（`artifact_revisions == 1`）PASS；pre-fix 与 head 表现相同。
  - **R-013（fixed at closure）** `doc/REBASELINE_PLAN.md` 的 T1.3.1 Verification 曾引用全仓不存在的 `tests/maintenance/test_sqlite_backup.py`（`tests/maintenance/` 只有 `test_cleanup.py`）；本次收口已更正为实际套件 `tests/storage/test_backup_restore.py` + `tests/workbench/test_restore_gate.py`。属计划文本与仓库事实不一致，非作者实现缺陷。
  - **既有产品限制不变**：生产 bootstrap 仍未接线 backup service。这不是 T1.3.1 的集成验收缺口，未在本轮扩展。
