---
id: TASK-065
title: TASK-058 复审尾项 docs+tests 小切片
kind: maintenance
status: ready
approval: approved_by_user
suggested_owner: Codex
owner: Codex
reviewer: Qoder
depends_on: ["TASK-058", "TASK-064"]
base_commit: 97fc5aa
branch: agent/codex/TASK-065-task058-followups
worktree: "G:/CODEX/New Manga.worktrees/TASK-065-codex"
integration_commit: null
---

# TASK-065：TASK-058 复审尾项 docs+tests 小切片

## 来源与目标

来源为 Qoder 的 [TASK-058 Review](../reviews/TASK-058-9c8cd52.md) F-002/F-003/F-005/F-006。该切片排在 F-007 所在的 diagnostics 后续之前；只补测试判别力、证据日志和文档型注解，不改变产品行为。

## Acceptance Criteria

- [ ] AC1：把 TASK-058 AC2 用例改成真实活动 worker 形状：调用 `_shutdown_services` 前可证明 worker 仍活跃，返回后线程排空且连接关闭；保留既有强断言。
- [ ] AC2：重采一次全仓测试日志，日志逐项包含 shell、venv、命令、`EXIT`、collected/passed/skipped 与逐条 skip 原因；不得用散文替代日志证据。
- [ ] AC3：修正 `AppServices.conn` 的过时类型注解及相关 single-connection 历史措辞；仅注解/docstring 变化，运行行为不变。
- [ ] AC4：移除 `tests/workbench/test_drain_shutdown.py` 的恒真 `assert sys.stderr is not None`，保留前一条有判别力的 stderr 断言；不得放宽或删除有效断言。
- [ ] AC5：完成 Handoff 与独立非作者 Review；全仓 collected 不低于 `951`，无新增 skip/xfail。

## 允许修改范围

- `src/bootstrap/app.py`（仅类型注解与 docstring）
- `tests/core/test_shutdown_drain.py`（F-002）
- `tests/workbench/test_drain_shutdown.py`（F-006）
- `doc/tasks/TASK-065.md`、`doc/tasks/TASK-058.md`、`doc/tasks/README.md`、`doc/STATUS.md`
- `doc/handoffs/TASK-065-*.md`
- `doc/reviews/TASK-065-*.md`
- `verification/TASK-065/**`

## 禁止范围

- 不修改产品逻辑、SQLite、Schema/migration、依赖、QML/UI 行为、managed storage、cleanup、TASK-055 正文或历史 Review。
- 不实施 F-007 diagnostics 接线；不重开或改写 TASK-055/TASK-064。
- 不新增 skip/xfail，不放宽/删除有效断言，不 push，不触碰用户未提交内容。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `pytest tests/core/test_shutdown_drain.py tests/workbench/test_drain_shutdown.py -q -p no:cacheprovider -rs` | 与仓库既有 TASK-012-py312 venv；不设 `QT_QPA_PLATFORM` | NOT_RUN | `verification/TASK-065/` |
| AC2/AC5 | `PYTHONPATH=src python -m pytest tests -q -p no:cacheprovider -rs`（另行 `--collect-only` 计数） | 同一 PowerShell + venv；`PYTHONDONTWRITEBYTECODE=1`；不设 `QT_QPA_PLATFORM` | **基线 PASS：951 collected / 945 passed / 6 skipped / EXIT=0；最终切片结果 NOT_RUN** | [baseline-full-suite.log](../../verification/TASK-065/baseline-full-suite.log)；6 条 skip 均为 `openssl unavailable` |

## 依赖、风险与阻塞

TASK-058 与 TASK-064 已集成。F-007 仍是后续 diagnostics 设计/接线事项，本切片不触碰。风险限定为测试/证据/文档精度；若活动 worker 判别需要产品改动，立即记为 blocker，不扩大范围。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- integration_commit：待 Codex 合并后填写。
- 实际测试：尚无。
