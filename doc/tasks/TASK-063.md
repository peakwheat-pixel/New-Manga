---
id: TASK-063
title: 诊断脱敏边界与多过滤器测试补强（TASK-062 Review R-001/R-002/R-003/R-004/R-006）
kind: bugfix
status: in_review
approval: approved_by_user
suggested_owner: Codex
owner: Codex
reviewer: Qoder（非作者）
depends_on: [TASK-062]
base_commit: ea56119ba16a8a57832a1ae9660845235ec58fc4
branch: agent/codex/TASK-063-diagnostics-boundaries
worktree: G:/CODEX/New Manga
integration_commit: null
---

# TASK-063：诊断脱敏边界与多过滤器测试补强

## 来源与目标

来源为 [TASK-062 Review](../reviews/TASK-062-9ba21f8.md) 的 R-001/R-002/R-003/R-004/R-006。目标是把当前已集成的脱敏与 Qt/libpng 补证收口到可长期维护的边界：设置/路径字典键也过屏、错误码不因消息命中而丢失、值形状边界写实、PNG 过滤器解析助手自证，并补稳定的 Up/Average 过滤器覆盖。

**排队规则**：本切片必须排在任何 TASK-055 诊断包生产接线之前；TASK-055 本身保持 `done`，不回滚、不重开。

## Acceptance Criteria

- [x] **AC ①（R-001）**：`settings_summary` 与 `environment_paths` 的数据键按与值一致的屏蔽规则进入报告；凭据形状不残留，普通键名保持可诊断；多脱敏键冲突时以 `#2` 后缀保留全部字段，并有报告级判别用例。
- [x] **AC ②（R-002）**：`recent_errors` 的 `code` 与 `message` 分别过屏；消息命中凭据时错误码仍保留，消息中的凭据不残留，并有真实报告级用例。
- [x] **AC ③（R-003）**：`redact_value` docstring 明确左守卫实际只排除字母数字邻接、`_`/`.`/`/` 仍是边界、短于 8 个 token 字符的 `sk-` 形状不遮；测试同时钉住文档与运行时行为。
- [x] **AC ④（R-004）**：`png_row_filter_types` 对解压长度、非交错 PNG 与 filter byte `0..4` 做健全性断言；非法解析均有失败测试。
- [x] **AC ⑤（R-006）**：新增稳定的 Up/Average 过滤器页，验证 overlap `0`/`64` 瓦片逐字节相同且拼接等于整页；既有 TASK-062 断言未删除或放宽。
- [x] **AC ⑥**：全仓 `948 collected = 942 passed / 6 skipped / EXIT=0` ×5；无新增 skip/xfail；日志含 shell/venv、命令、EXIT，且基线失败/head 通过判别 artefact 已入库。
- [ ] **AC ⑦**：Handoff、verification、独立非作者 Review、STATUS 已准备；**待 Codex 将 approved delivery 合并回 master 后**填写 `integration_commit` 并勾选本项。

## 允许修改范围

- `src/application/maintenance/diagnostics.py`（仅脱敏 docstring/实现）
- `tests/diagnostics/**`
- `tests/reading_export/**`
- 本 Task、Handoff、`verification/TASK-063/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 Schema/migration、`requirements.txt`、`src/ui/qml/**`、`AGENTS.md`。
- 不得改 `src/infrastructure/sqlite/**`、`managed_storage.py`、`cleanup.py`、`tests/workbench/**` 或 TASK-055 生产接线。
- 不得把 TASK-055 诊断包接线与本切片混做一批；不得新增 skip/xfail、放宽/删除既有断言或 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC ①～③ 脱敏 | `pytest tests/diagnostics -q -p no:cacheprovider -rs` | PowerShell + `TASK-012-py312`，不设 `QT_QPA_PLATFORM`；head `3fbbfe4` | **PASS 31 passed / 0 skipped / EXIT=0** | [diagnostics-suite.log](../../verification/TASK-063/diagnostics-suite.log) |
| AC ④～⑤ 瓦片 | `pytest tests/reading_export -q -p no:cacheprovider -rs` | 同上；head `3fbbfe4` | **PASS 118 passed / 0 skipped / EXIT=0** | [reading-export-suite.log](../../verification/TASK-063/reading-export-suite.log) |
| AC ⑥ 全仓 | `pytest tests -q -p no:cacheprovider -rs` | 同上；head `3fbbfe4` | **PASS ×5：948 collected = 942 passed / 6 skipped / EXIT=0** | [full-suite-run1..5.log](../../verification/TASK-063/) |
| AC ⑥ 判别力 | 同一新增诊断用例选择集，分别在 `ea56119` 与 `3fbbfe4` | 同上 | **基线 5 failed / 1 passed / EXIT=1；head 6 passed / EXIT=0** | [discrimination-base.log](../../verification/TASK-063/discrimination-base.log)、[discrimination-head.log](../../verification/TASK-063/discrimination-head.log) |

## 依赖、风险与阻塞

- 硬依赖：TASK-062 已集成；TASK-055 的生产接线不得先于本切片。
- 风险：键侧过屏和错误码保留的实现若混淆 key/value 形状，可能产生假阴性；以报告级判别用例锁定。
- 阻塞：无；实现分支已从 `ea56119` 建立。

## 交付与运行记录

- Handoff：[TASK-063-3fbbfe4.md](../handoffs/TASK-063-3fbbfe4.md)。
- Review：独立非作者 Review 待最终 head 复审（Task 元数据 Reviewer=Qoder，非作者）。
- 实现提交：`30db4a2`（首轮 GREEN）、`3fbbfe4`（Review P2 修复）。
- 实际测试：已完成；当前状态 `in_review`，尚未合并 master。
