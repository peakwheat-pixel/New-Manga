---
id: TASK-063
title: 诊断脱敏边界与多过滤器测试补强（TASK-062 Review R-001/R-002/R-003/R-004/R-006）
kind: bugfix
status: proposed
approval: approved_by_user
suggested_owner: Codex
owner: null
reviewer: Qoder（非作者）
depends_on: [TASK-062]
base_commit: null
branch: null
worktree: null
integration_commit: null
---

# TASK-063：诊断脱敏边界与多过滤器测试补强

## 来源与目标

来源为 [TASK-062 Review](../reviews/TASK-062-9ba21f8.md) 的 R-001/R-002/R-003/R-004/R-006。目标是把当前已集成的脱敏与 Qt/libpng 补证收口到可长期维护的边界：设置/路径字典键也过屏、错误码不因消息命中而丢失、值形状边界写实、PNG 过滤器解析助手自证，并补稳定的 Up/Average 过滤器覆盖。

**排队规则**：本切片必须排在任何 TASK-055 诊断包生产接线之前；TASK-055 本身保持 `done`，不回滚、不重开。

## Acceptance Criteria

- [ ] **AC ①（R-001）**：`settings_summary` 与 `environment_paths` 的数据键按与值一致的屏蔽规则进入报告；凭据形状不残留，普通键名保持可诊断，并有判别用例。
- [ ] **AC ②（R-002）**：`recent_errors` 的 `code` 与 `message` 分别过屏；消息命中凭据时错误码仍保留，消息中的凭据不残留，并有真实报告级用例。
- [ ] **AC ③（R-003）**：`redact_value` docstring 明确左守卫实际只排除字母数字邻接、`_`/`.`/`/` 仍是边界、短于 8 个 token 字符的 `sk-` 形状不遮；测试钉住该约定，不扩大守卫导致保护变弱。
- [ ] **AC ④（R-004）**：`png_row_filter_types` 对解压长度与非交错 PNG 做健全性断言；解析失败必须测试失败，不得静默制造“非全 filter-0”的假证据。
- [ ] **AC ⑤（R-006）**：新增稳定的 Up/Average 过滤器页，验证 overlap `0`/`64` 瓦片逐字节相同且拼接等于整页；不得删除或放宽 TASK-062 既有断言。
- [ ] **AC ⑥**：全仓 collected 不下降、无新增 skip/xfail；每份日志带 shell/venv、命令和 EXIT，判别性 artefact 入库。
- [ ] **AC ⑦**：Handoff、verification、Qoder 非作者 Review、集成和 STATUS 收口齐全。

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
| AC ①～③ 脱敏 | `pytest tests/diagnostics -q -rs -p no:cacheprovider` | PowerShell + `TASK-012-py312`，不设 `QT_QPA_PLATFORM` | NOT_RUN | 无 |
| AC ④～⑤ 瓦片 | `pytest tests/reading_export -q -rs -p no:cacheprovider` | 同上 | NOT_RUN | 无 |
| AC ⑥ 全仓 | `pytest tests -q -rs -p no:cacheprovider` | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- 硬依赖：TASK-062 已集成；TASK-055 的生产接线不得先于本切片。
- 风险：键侧过屏和错误码保留的实现若混淆 key/value 形状，可能产生假阴性；以报告级判别用例锁定。
- 阻塞：实施前由 Codex 依当前 master 创建 branch/worktree 并填写实际 base。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（Reviewer=Qoder，非作者）。
- 实际测试：尚无（`proposed`）。
