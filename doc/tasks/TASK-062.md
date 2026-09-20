---
id: TASK-062
title: 后置复审残留收口（Q-006 诊断脱敏 + TASK-046 R-001 多过滤器补证 + R-009）
kind: bugfix
status: in_review
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

- [x] **AC ①（Q-006：不变式成真）**：`build_diagnostics_report`（`src/application/maintenance/diagnostics.py:123`）对**每一段**的**每一个值**过 `redact_value`（含 application / database / settings_summary / environment_paths / recent_errors），**键也过屏**（`recent_errors` 的合成键 `"{occurred_at} {source}"` 现经 `redact_value("recent_error", …)`）；值形状判据由前缀 `match` 改为带左守卫的 `search`（`(?<![A-Za-z0-9])Bearer\s+[A-Za-z0-9._~+/=\-]{6,}`、`(?<![A-Za-z0-9])sk-[A-Za-z0-9_\-]{8,}`），边界用例两侧钉住（`D:/workspace/sk-tools-market` 被遮＝安全方向；`password=hunter2` 不遮＝非本屏职责）。
- [x] **AC ②（判别用例）**：新增 `TestRedactionReachesEverySection`（`tests/diagnostics/test_report.py:179`，6 例）——凭据出现在 `platform_python`/`database_path`/`recent_errors`（值与键）时被脱敏、令牌在序列化结果中不残留；良性值（`0.1.0`、`CPython 3.12.3`、`…/library.db`、`D:/MangaData`、`a.png`）原样保留；普通路径/版本/单词不被误伤。**既有 `tests/diagnostics/**` 断言逐条不变**（该文件仅追加）。
- [x] **AC ③（docstring 诚实）**：`redact_value` docstring 写明"键名 + 两个窄值形状、**不**扫任意自由文本"并给出 `password=hunter2` 反例；`DiagnosticsReport` 与 `build_diagnostics_report` 的"Every value"改为"**every value and every key**"。过强承诺已消除。
- [x] **AC ④（TASK-046 R-001 补证）**：`tests/reading_export/test_webtoon_tiles.py:935` 新增 `test_overlap_choice_on_a_qt_encoded_page`（+`write_qt_encoded_png`/`png_row_filter_types` 助手，**不改既有断言**）：先断言夹具行过滤**不是全 filter-0**，再断言 overlap `0`/`64` 瓦片文件**逐字节相同**、拼接**== 整页**。独立探针实测过滤器集合 = `[0,1,4]`、3/3 字节相同、拼接==整页（`verification/TASK-062/qt-encoded-filter-probe.txt`）。**注**：`Up`/`Average` 未被 libpng 在本图样上选中，覆盖的是"非退化自适应过滤器"性质，逐过滤器穷尽另议。
- [x] **AC ⑤（不回归）**：全仓 **930 collected = 924 passed / 6 skipped / EXIT=0（×4 次）**，未跌破基线 923 collected（本机口径 917/6 ⇒ **+7 例**）；`tests/diagnostics` 19→**25 passed**、`tests/reading_export` 112→**113 passed**，均未减少；**无新增 `skip`/`xfail`、未放宽既有断言**。
- [x] **AC ⑥（证据口径）**：4 份全仓 + 3 份定向 + 1 份探针日志**均带 EXIT 与 shell/venv 头**并入库 `verification/TASK-062/`。判别力为 artefact（`discriminating-prefix-tree.txt`）：新用例跑在 `git archive 41d7aee` 修前树 ⇒ **diagnostics 组 4 failed / 14 passed / EXIT=1（4/6 例有判别力）**；**webtoon 新例 1 passed / EXIT=0（无判别力，已如实标注"未作修前判别"）**——本切片 `src` 改动仅 `diagnostics.py` 一个文件（`git diff --name-only 41d7aee -- src` 实证）。另两例防假阳性钉子修前亦通过，一并标注。
- [ ] **AC ⑦** Handoff + `verification/TASK-062/**`（**已交付**：[Handoff](../handoffs/TASK-062-9ba21f8.md)、[证据索引](../../verification/TASK-062/README.md)）+ **非作者** Review（**待 Qoder**）+ 集成（**待 Codex**）+ STATUS 台账行（**已登记实施行**）。集成后由集成方勾选本项并填 `integration_commit`。

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
| AC ①② 脱敏 | `pytest tests/diagnostics -q -rs -p no:cacheprovider` | PowerShell + `TASK-012-py312`、`PYTHONDONTWRITEBYTECODE=1`、不设 `QT_QPA_PLATFORM` | **25 passed / 0 skipped / EXIT=0** | [diagnostics-suite.log](../../verification/TASK-062/diagnostics-suite.log) |
| AC ④ 多过滤器补证 | `pytest tests/reading_export/test_webtoon_tiles.py -q -rs -k qt_encoded -p no:cacheprovider` | 同上 | **1 passed / 22 deselected / EXIT=0** | [webtoon-tiles-targeted.log](../../verification/TASK-062/webtoon-tiles-targeted.log) |
| AC ④ 套件级 | `pytest tests/reading_export -q -rs -p no:cacheprovider` | 同上 | **113 passed / 0 skipped / EXIT=0**（修前 112） | [reading-export-suite.log](../../verification/TASK-062/reading-export-suite.log) |
| AC ④ 独立探针 | `python verification/TASK-062/qt-encoded-filter-probe.py` | 同上 | **PASS / EXIT=0**：过滤器 `[0,1,4]`、3/3 瓦片字节相同、拼接==整页 | [qt-encoded-filter-probe.txt](../../verification/TASK-062/qt-encoded-filter-probe.txt) |
| AC ⑤ 全仓 | `pytest tests -q -rs -p no:cacheprovider` | 同上 | **PASS ×4**：924 passed / 6 skipped / EXIT=0（930 collected；基线 923） | [full-suite-run1..3.log](../../verification/TASK-062/full-suite-run1.log)、[run4-post-commit](../../verification/TASK-062/full-suite-run4-post-commit.log) |
| AC ⑥ 判别力 | 新用例置于 `git archive 41d7aee` 修前树运行 | 同上；修前树 = base_commit | diagnostics **4 failed / 14 passed / EXIT=1**；webtoon **1 passed / EXIT=0（无判别，如实声明）** | [discriminating-prefix-tree.txt](../../verification/TASK-062/discriminating-prefix-tree.txt) |
| R-009 核对 | `git diff --name-only 9522f2d a2b23ad -- src tests`（空）+ 路径检索 | 同上 | **PASS（勘误核实并记录；落改待集成方）** | [r009-erratum.md](../../verification/TASK-062/r009-erratum.md) |

## 依赖、风险与阻塞

- 依赖：TASK-046（被补证对象）、TASK-055（诊断包来源）。
- 风险：把值形状判据放宽会误伤普通路径 ⇒ AC ① 要求给出边界用例；实现时按"窄且安全方向"取。
- 阻塞：无。

## 交付与运行记录

- **实施完成（2026-09-19，Codex）**：delivery head=`9ba21f8`（实现+测试+证据一次性提交），文档提交见 Handoff。变更面：`src/application/maintenance/diagnostics.py`、`tests/diagnostics/test_report.py`（+6 例）、`tests/reading_export/test_webtoon_tiles.py`（+1 例），证据 `verification/TASK-062/**`（12 文件，见其 [README](../../verification/TASK-062/README.md)）。
- Handoff：[TASK-062-9ba21f8.md](../handoffs/TASK-062-9ba21f8.md)。Review：**待 Qoder（非作者）** 出 `doc/reviews/TASK-062-9ba21f8.md`。
- **证据口径**：4 次全仓（`924/6/EXIT=0`，930 collected）+ 3 次定向 + 1 份探针；每份含 EXIT 与 shell/venv 头；判别力为 artefact（★ AC ⑥ 与任务书原文的差异已在下条如实登记）。
- **对任务书 §AC ⑥ 的显式修正**：任务书预设"对新用例声明 N/A"。实际**不适用**——diagnostics 组在修前树确实失败（4/6 例），有判别力；webtoon 新例无判别力（`src` 未改），按"未作修前判别"如实标注。两类都给了 artefact，未用散文代替。
- **R-009 状态 = `open`（已记录、未落改）**：允许范围内不含 `doc/tasks/TASK-060.md` 与 `doc/handoffs/TASK-060-zcode-handoff.md`，且禁止"改其他 Task"⇒ 以逐条复核 + 可直接套用补丁文本（[r009-erratum.md](../../verification/TASK-062/r009-erratum.md) §2）+ STATUS 台账句处置，落改留待集成时顺手完成（docs-only）。
- **未触碰**：Schema/migration、`requirements.txt`、`src/ui/qml/**`、`AGENTS.md`、其他 Task；**未触碰 TASK-061 的在飞写集合**（`src/infrastructure/sqlite/**`、`managed_storage.py`、`cleanup.py`、`tests/workbench/**`）；未 push。
- **最近状态（当前，唯一）**：2026-09-19 由 Codex 依 TASK-060 复审 Q-006 与 TASK-046 复审 R-001 开立；当日实施完成，置 **`in_review`**，等 Qoder 非作者 Review。
