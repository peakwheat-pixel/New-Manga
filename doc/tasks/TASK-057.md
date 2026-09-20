---
id: TASK-057
title: TASK-021 冻结子集③：备份与恢复
kind: implementation
status: in_review
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: Qoder（历史交付）/ 独立非作者 Reviewer（T1.3.1 reconciliation pending）
depends_on: [TASK-021, TASK-053]
base_commit: 8bf8da3f988cdeffce83ad251a15c22ce862dd1a
branch: agent/zcode/TASK-057-backup-restore
worktree: G:/CODEX/New Manga.worktrees/TASK-057-zcode
integration_commit: null
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
- [ ] **AC ⑥** Handoff + `verification/TASK-057/**` + 独立子对话 Review + 集成 + STATUS 台账行。

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
