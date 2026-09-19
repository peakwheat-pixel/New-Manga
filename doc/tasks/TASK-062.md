---
id: TASK-062
title: 后置复审残留收口（Q-006 诊断脱敏 + TASK-046 R-001 多过滤器补证 + R-009）
kind: bugfix
status: ready
approval: approved_by_user
suggested_owner: Codex
owner: Codex
reviewer: Qoder（非作者）
depends_on: [TASK-046, TASK-055]
base_commit: 41d7aee50e8f3d1daf67c7a89daf37ca4e01849c
branch: agent/codex/TASK-062-posthoc-residuals
worktree: G:/CODEX/New Manga.worktrees/TASK-062-codex
integration_commit: null
---

# TASK-062：后置复审残留收口

**READY（2026-09-19，用户批准"按推荐的下一步"）**：Owner=`Codex`、Reviewer=`Qoder`（**非作者**）、base=`41d7aee`。**刻意避开 TASK-061 的写集合**（不碰 `src/infrastructure/sqlite/**`、`managed_storage.py`、`src/application/maintenance/cleanup.py`、`tests/workbench/**`）。

## 来源

- **Q-006（P2，隐私面，来自 [TASK-060 复审](../reviews/TASK-060-b28c615.md)）**：`src/application/maintenance/diagnostics.py` 的 `DiagnosticsReport` docstring 承诺"Every value passes the redaction screen"，但 `build_diagnostics_report` 只对 `settings_summary` 与 `environment_paths` 调 `redact_value`；`app_version`、`platform_python`、`database_path` 与 `recent_errors` 的**值裸传**，且 recent-errors 的**键**由 `"{occurred_at} {source}"` 合成，结构上不可能命中 `_SENSITIVE_KEY`。测试用良性 `"a.png"` 掩盖（`tests/diagnostics/test_report.py:159`）。**诊断包会外发**，按隐私面处理。
- **TASK-046 R-001（P2，证据缺口，来自 [TASK-046 复审](../reviews/TASK-046-7bf476b.md)）**：AC① 的"改 overlap 后瓦片像素逐字节相同"证明只用**手写 filter-0** 页（`tests/reading_export/test_webtoon_tiles.py:485-527` 及其两个夹具），**未覆盖 libpng/Qt 的 Average/Paeth/Up 等行过滤**。
- **R-009（P3，docs）**：记录勘误建议（随手）。

## Acceptance Criteria

- [ ] **AC ①（Q-006：不变式成真）**：`build_diagnostics_report` 生成的**每一个值**都过 `redact_value`（含 application / database / recent_errors 三段），**键也过屏**；`redact_value` 的值形状判据由"仅前缀 match"扩展为**能覆盖嵌入式凭据**（如 `Bearer …` / `sk-…` 出现在串中），且**不得**把普通路径/版本串误伤（给出边界用例）。
- [ ] **AC ②（判别用例）**：新增用例证明——①令牌子串出现在 `recent_errors.message` / `platform_python` / `database_path` 时**被脱敏**；②良性值（版本号、`D:/MangaData`、`a.png`）**原样保留**；③既有 `tests/diagnostics/**` 断言逐条不变。
- [ ] **AC ③（docstring 诚实）**：把 docstring 改到与实现一致——**写清能力与边界**（键名 + 窄值形状；不承诺扫描任意自由文本里的所有秘密），不得再留过强承诺。
- [ ] **AC ④（TASK-046 R-001 补证）**：在 `tests/reading_export/test_webtoon_tiles.py` **新增**（不改既有断言）一个 **Qt/libpng 编码**页变体：断言该夹具的行过滤**确实不是全部 filter-0**（解析 IDAT 得到过滤类型集合），并断言 overlap `0` 与 `64` 的瓦片文件**逐字节相同**、瓦片拼接**仍等于整页**。
- [ ] **AC ⑤（不回归）**：全仓 **不得跌破 923 collected**（openssl 可用口径 `923 passed / 0 skipped`；本机 PowerShell 口径 `917 passed / 6 skipped`，总数须仍为 923）；`tests/diagnostics`、`tests/reading_export` 通过数不减少；不得新增 `skip`/`xfail`、不得放宽既有断言。
- [ ] **AC ⑥（证据口径）**：每份日志带 **EXIT 码** 与 **shell/venv 头**、逐次入库；判别力必须是 artefact（协议 §6 **第 12 条**）。对修前失败：本条对本切片的**新用例**声明 N/A（它们钉的是补强的性质），但必须如实标注"未作修前判别"，不得写成"已判别"。
- [ ] **AC ⑦** Handoff + `verification/TASK-062/**` + **非作者** Review + 集成 + STATUS 台账行。

## 允许修改范围

- `src/application/maintenance/diagnostics.py`
- `tests/diagnostics/**`
- `tests/reading_export/**`
- 本 Task、Handoff、`verification/TASK-062/**`、`doc/STATUS.md`（台账行）

## 禁止范围

- 不得改 Schema/migration、`requirements.txt`、`src/ui/qml/**`、`AGENTS.md`、其他 Task。
- **不得触碰 TASK-061 的在飞写集合**：`src/infrastructure/sqlite/**`、`src/infrastructure/filesystem/managed_storage.py`、`src/application/maintenance/cleanup.py`、`tests/workbench/**`。
- 不得放宽/删除既有断言、不得新增 skip/xfail；不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC ①② 脱敏 | `pytest tests/diagnostics -q`（planned） | PowerShell + `TASK-012-py312`、不设 `QT_QPA_PLATFORM` | NOT_RUN | 无 |
| AC ④ 多过滤器补证 | `pytest tests/reading_export/test_webtoon_tiles.py -q`（planned） | 同上 | NOT_RUN | 无 |
| AC ⑤ 全仓 | `pytest tests -q -rs`（planned） | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- 依赖：TASK-046（被补证对象）、TASK-055（诊断包来源）。
- 风险：把值形状判据放宽会误伤普通路径 ⇒ AC ① 要求给出边界用例；实现时按"窄且安全方向"取。
- 阻塞：无。

## 交付与运行记录

- Handoff：尚无。Review：尚无（Reviewer=`Qoder`，非作者）。实际测试：尚无（`ready`）。
- **最近状态（当前，唯一）**：2026-09-19 由 Codex 依 TASK-060 复审 Q-006 与 TASK-046 复审 R-001 开立为 `ready`；base=`41d7aee`。**实施尚未开始。**
