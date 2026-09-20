---
id: TASK-064
title: diagnostics production wiring（TASK-055 装配接线后续）
kind: implementation
status: approved
approval: approved_by_user
suggested_owner: Codex
owner: Codex
reviewer: DeepSeek Harness（非作者）
depends_on: [TASK-055, TASK-063]
base_commit: 604c47a1dade46522cf496817861742a454deeb9
branch: agent/codex/TASK-064-diagnostics-production-wiring
worktree: G:/CODEX/New Manga
integration_commit: null
---

# TASK-064：diagnostics production wiring

## 来源与目标

来源为 TASK-055 Handoff/Task 中明确登记的“装配接线与 QML 入口 NOT_RUN”，以及 TASK-063 完成后的可比基线。TASK-055 已完成并集成 `0493ea9`，不得重开或改写；本 Task 只把现有 `DiagnosticsService`、`DiagnosticsSnapshotProvider`、`DiagnosticsBundleSink` 接入真实 `assemble_services` / `AppServices`，并以 bootstrap contract tests 证明生产装配可取得该服务。

QML/UI 入口仍不在本 Task；不得新增 `diagnosticsService` QML context property。诊断导出 API 必须继续使用既有脱敏报告、错误码/字段清单和 `BoundedLogStore` 的 data-root 有界约束。

## Acceptance Criteria

- [x] **AC ①（真实装配）**：`assemble_services` 返回的 `AppServices` 持有可用 `DiagnosticsService`；`assemble_engine(services)` 在该服务存在时正常装配，且不新增 QML/UI 入口或 context property。
- [x] **AC ②（真实导出）**：从真实装配取得的服务执行一次导出，生成可读取的脱敏诊断报告；保留固定字段清单、错误码与现有凭据零泄漏行为。
- [x] **AC ③（有界 sink）**：导出 sink 复用 `BoundedLogStore` 与既有 data-root 约定；输出不进入用户源文件树，且文件数量/单文件大小上限仍由已有有界存储保证。
- [x] **AC ④（生产 contract tests）**：新增/扩展 `tests/core/test_bootstrap.py` 与 `tests/diagnostics/**`，覆盖 provider/sink 注入、真实导出和装配失败边界；不得修改 QML、Schema 或 SQLite 实现。
- [x] **AC ⑤（回归与证据）**：全仓 collected 不低于 948；无新增 skip/xfail、无放宽/删除既有断言；全仓至少连续 5 次，日志逐次含 shell/venv、命令、EXIT、passed/skipped 与逐条 skip 原因。
- [ ] **AC ⑥（交付）**：Handoff、verification、独立非作者 Review、STATUS/任务索引齐全；Review approved 后由 Codex 合并并填写 `integration_commit`，合并后复跑全仓再置 `done`。

## 允许修改范围

- `src/bootstrap/app.py`（AppServices 与 diagnostics 生产装配；不向 QML 暴露）
- `src/infrastructure/filesystem/bounded_log_store.py`（仅在现有接口无法满足真实 sink 契约时，且只能做 diagnostics/log 相关最小适配）
- `tests/core/test_bootstrap.py`
- `tests/diagnostics/**`
- 本 Task、Handoff、`verification/TASK-064/**`、`doc/STATUS.md`（台账行）、`doc/tasks/README.md`

## 禁止范围

- 不得修改 TASK-055 正文、历史 Handoff 或历史 Review。
- 不得改 Schema/migration、SQLite 实现、`requirements.txt` 或新增任何依赖。
- 不得改 `src/ui/qml/**`、QML/UI 入口、`managed_storage.py`、`cleanup.py`、`tests/workbench/**`。
- 不得放宽/删除断言、新增 skip/xfail、push；范围扩大须先由 Codex登记。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC ①～④ 定向 | `pytest tests/diagnostics tests/core -q -p no:cacheprovider -rs` | PowerShell 7 + `TASK-012-py312`；`2024bfb` | PASS：75 passed / 0 skipped，EXIT=0 | `verification/TASK-064/diagnostics-bootstrap-suite.log` |
| AC ⑤ 全仓 ×5 | `pytest tests -q -p no:cacheprovider -rs`，连续 5 次逐次记录 | 同上；`2024bfb` | PASS：每次 951 collected、945 passed / 6 skipped，EXIT=0 | `verification/TASK-064/full-suite-{1..5}.log` |
| AC ⑤ skip 审计 | 读取每次 `-rs` 输出并逐条登记 | 同上 | PASS：6 项均为 `openssl unavailable`，无新增 skip/xfail | `verification/TASK-064/full-suite-{1..5}.log` |

## 依赖、风险与阻塞

- 硬依赖：TASK-055 已集成 `0493ea9`；TASK-063 已集成 `94a0091`。
- 风险：生产装配若把诊断写入 managed/user source 边界，可能泄露或破坏用户源文件；必须由 sink 根路径 contract test 钉住。
- 阻塞：无；本 Task 已获用户批准，交付 head 为 `2024bfb`，独立非作者 Review 已 approved，等待 Codex 集成。

## 交付与运行记录

- Handoff：[TASK-064-e39cc27](../handoffs/TASK-064-e39cc27.md)，delivery head=`2024bfb`。
- Review：[TASK-064-d154044](../reviews/TASK-064-d154044.md)；独立非作者复审结论 `approved`。
- 实际测试：定向 75 passed / 0 skipped；全仓连续 5 次均 945 passed / 6 skipped；P1 修复前后判别日志已入库；详见 `verification/TASK-064/`。
