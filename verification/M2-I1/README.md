# M2-I1 — Core Assembly Seam 验证证据索引

| 字段 | 值 |
|---|---|
| Task | [M2-I1](../../doc/tasks/M2-I1.md)（Owner=ZCode，Reviewer=Codex） |
| 固定 base | `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`（开工 HEAD `5d989ba`，两者间仅 docs 提交） |
| Worktree / branch | `G:/CODEX/New Manga.worktrees/M2-I1-zcode` / `agent/zcode/M2-I1-core-assembly-seam` |
| 解释器 | `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（3.12.3，PySide6 6.11.2） |
| Shell / env | Git Bash；`PYTHONDONTWRITEBYTECODE=1`；`QT_QPA_PLATFORM` 不设（TASK-030 产品边界） |
| 日期 | 2026-09-25（Asia/Shanghai） |

## 证据文件与 AC 映射

| 文件 | 覆盖 | 结论 |
|---|---|---|
| `probe_import_blocker.py` | I1-AC1/AC6 探针脚本 | 子进程 meta-path blocker 拒绝 `PySide6`/`shiboken6`/`ui` 后逐模块 `import`；探针自身恒 EXIT=0，结论由 stdout 承载 |
| `01-import-blocker-probe-delivery.log` | I1-AC1/AC6 | 交付树：`bootstrap.core_assembly` **PASS**（无 Qt/UI 泄漏）；`bootstrap.app` **FAIL: BLOCKED-IMPORT: PySide6**（blocker 判别力对照） |
| `01-import-blocker-probe-base.log` | I1-AC6 修前对照 | base `6a68fde`（`git archive` 隔离副本）：`bootstrap.core_assembly` **FAIL: ModuleNotFoundError**（修前模块不存在）；`bootstrap.app` 与交付树一致被拦。core_assembly 的 FAIL→PASS 翻转即判别证据 |
| `02-core-layer-rg-audit.log` | I1-AC2 | `rg 'PySide6\|src\.ui\|from ui\|import ui'` 在交付树与 base 树命中集合**完全一致**（7 行：domain/ports 纯度注释 + `application/export/pdf_qt.py` docstring 与 2 行惰性导入，均为 M2-D1 已盘点存量）→ 零新增依赖 |
| `03-diff-scope-and-check.log` | I1-AC5/AC8 范围 | 相对开工 HEAD 的作者 delta 限于 `src/bootstrap/{app.py,core_assembly.py}`、`tests/core/{test_bootstrap.py,test_core_assembly.py}`、`verification/M2-I1/**`；React/Tauri/tsx/package.json/Cargo **零命中**；`git diff --check` EXIT=0 |
| `04-task-suite.log` | I1-AC3/AC6/AC7 | Task 指定命令：`pytest tests/core/test_bootstrap.py tests/core/test_core_assembly.py tests/ui_shell tests/providers tests/pipeline` → **467 passed, 5 skipped, EXIT=0**（skip 全为 docTR/numpy/torch 未安装的环境 skip） |
| `05-full-suite-delivery.log` | I1-AC7 | 全量 `pytest tests`（交付树）→ **1226 passed, 5 skipped, EXIT=0**（QML TypeError 为既有 teardown 噪音，已过滤，见日志头说明） |
| `06-full-suite-baseline-control.log` | I1-AC7 对照 | 同一命令在 base 代码（`git stash push -u` 后的干净开工 HEAD）→ **1218 passed, 5 skipped, EXIT=0**；1226−1218 = 新增的 8 个 `test_core_assembly.py` 测试，skip 集合一致 → 无隐藏行为变化 |
| `07-entry-compileall-smoke-screenshot.log` | I1-AC3 | `compileall -q src` EXIT=0；`python -m bootstrap.app --smoke-test --data-root <temp>` EXIT=0（默认 Windows Qt 平台）；`--screenshot` EXIT=0 并产出真实 1280×800 PNG 帧。**真实人工 GUI 交互 = NOT_RUN**（本环境无交互会话） |

## AC 总览

- **I1-AC1 PASS**：Core Assembly（`bootstrap.core_assembly`）在禁止 PySide6/`src/ui` 的探针环境可按模块名导入（log 01-delivery）。
- **I1-AC2 PASS**：Core 三层 rg 命中与 base 逐行一致，零新增（log 02）。
- **I1-AC3 PASS（人工 GUI = NOT_RUN）**：入口/装配/QML 契约由 04/07 覆盖；smoke+screenshot 在默认 Windows Qt 平台真实渲染。
- **I1-AC4 PASS**：keyword-only 必填注入（`image_decoder`/`font_catalog`/`layout_engine`/`compositor`/`source_styles`，`content_decoder` 可选默认惰性桥）；AST 判别 Core 零 Qt 四类构造、零 QObject ViewModel 构造、零 `ui` 导入；运行期 identity 断言注入对象被原样使用（`tests/core/test_core_assembly.py`，log 04）。
- **I1-AC5 PASS**：装配副作用顺序原样迁移（schema check→migrations→managed layout→provider settings→`recover_running_runs`→diagnostics→legacy JSON import），全量两树对照绿（log 05/06）；SQLite/Managed Copy/Provider/Pipeline 权威未移动（diff 范围仅 bootstrap/tests/verification，log 03）。
- **I1-AC6 PASS**：判别探针 + 修前对照失败证据（log 01 两份）。
- **I1-AC7 PASS**：1226 vs 1218 全量对照，skip 集合一致，失败为零（log 05/06）。
- **I1-AC8 PASS**：零 React/Tauri/IPC 产物（log 03）。

## R2 修订（2026-09-25，回应 [Review a89447f](../../doc/reviews/M2-I1-a89447f.md) `changes_requested`）

| 项 | 修复 | 判别证据 |
|---|---|---|
| **P-01 (P1)** Qt ViewModel/接线段失败时连接泄漏 | `assemble_services` 把 Qt 层装配移入 `_assemble_legacy_qt_layer(core)` 并以 `try/except: core.conn.close(); raise` 覆盖（恢复原版整体 close-on-error 语义；成功路径不提前关闭） | `08-p01-cleanup-probe.log`：unfixed head a89447f（git archive 副本）`CONNECTION_CLOSED=False`→FAIL；修订树 `True`→PASS（与 Review 的 `qt-assembly-failure-probe.log` 同口径）。回归测试 `test_assemble_services_closes_connection_when_qt_assembly_fails`：未修复树上实测 FAIL、修复版 PASS（含成功路径 SELECT 断言 + win32 库文件 unlink 锁判别） |
| **S-01 (P2)** 无 Qt 解释器整模块跳过 | `tests/core/test_core_assembly.py` 移除模块级 `pytest.importorskip("PySide6")`；唯一需要真实 Qt 实例的注入断言测试改函数内局部 skip；identity 测试改用 Qt-free stub analyzer | `10-r2-qtfree-probes.log`：Python 3.14.6（无 PySide6）`7 passed, 1 skipped, exit 0`（Review 记录的修订前结果为 `1 skipped`、pytest exit 5） |

R2 复跑（venv 3.12.3 + PySide6 6.11.2，Git Bash，`PYTHONDONTWRITEBYTECODE=1`，`QT_QPA_PLATFORM` 不设）：
- Task 指定套件 `09-r2-task-suite.log`：**468 passed, 5 skipped, exit 0**（467+1=新增 P-01 回归测试；skip 集与 R1/base 相同）。
- 全量 + 入口 `11-r2-full-suite-and-entry.log`：全量 **1227 passed, 5 skipped, exit 0**（1226+1）；compileall/smoke/screenshot exit 0（真实 1920×1200 帧）；真实人工 GUI 交互仍 **NOT_RUN**。
- P-01 判别探针脚本：`probe_qt_assembly_cleanup.py`（子进程强制 NavigationViewModel 失败，探针自身恒 EXIT=0，结论由 stdout 承载）。

## 设计说明（供 Review）

- `src/bootstrap/core_assembly.py`：Qt-free Core Assembly。`assemble_core_services()` 承接原 `assemble_services` 的全部持久化副作用（顺序不变），Qt 适配器全部经 keyword-only 注入。`_ManagedPageImageSource` 与 `_render_content_decoder` 保留函数体内惰性 Qt 导入（M2-D1 M2D1-10/15 已盘点的 DECOUPLE 形态，替代实现属后续切片），模块导入期零 Qt。
- `src/bootstrap/app.py`：Legacy Qt 装配。构造 `QtImageDecoder`/`QtFontCatalog`/`QtTextLayoutEngine(font_catalog)`/`QtImageCompositor`/`SourceStyleService(PixelSourceStyleAnalyzer())` 注入 Core，再组装 6 个 QObject ViewModel 与导航/导出接线；`assemble_engine`/`_shutdown_services`/`main`/`QML_PATH` 原样。被既有测试引用的移位私有名经 re-export 保持 `from bootstrap.app import ...` 兼容。
- 顺序重排说明：QObject ViewModel（Navigation/Settings/Reader/Bookshelf/Workbench）与 export_state 接线的构造点从「散布于 Core 副作用之间」变为「Core 副作用完成后」——这些构造均无外部持久化副作用，全部持久化副作用顺序不变（log 05/06 两树全量对照为证）。

## R3 reconcile、非作者 Review 与集成（2026-09-25）

| 证据 | 对象与口径 | 结论 |
|---|---|---|
| [`12-r3-reconcile-verification.log`](12-r3-reconcile-verification.log) | ZCode 将已审 I1 R2 交付协调到含 I2 的 `master@0275290`，固定 Product Delivery=`09ad43a`；P3-001 结论句已修正 | 交付 delta **包含已审 I1 产品代码**，未新增产品改写；21 个授权路径，`git diff --check` exit 0 |
| [R3 Handoff](../../doc/handoffs/M2-I1-09ad43a.md) | 作者 Handoff head=`8dab0ab`，产品交付=`09ad43a` | 固定 merge 祖先和恢复点；真实人工 GUI 交互 `NOT_RUN` |
| [DeepSeek Harness R3 Review](../../doc/reviews/M2-I1-09ad43a-deepseek.md) 与 [`review-09ad43a/`](review-09ad43a/) | 独立非作者 Review 的原始 Task/架构/无 Qt/双树全仓证据 | `approved`；P3-001～P3-003 由集成登记处理；P3-004 reading_export 间歇失败是基线已有的范围外发现 |
| [`integration-cff1e0a/`](integration-cff1e0a/) | Codex 在产品 merge `cff1e0a` 上运行全仓 pytest（含 `openssl`）、架构守卫和范围核验 | 以目录内原始日志及 [集成记录](integration-cff1e0a/record.md) 为准；测试完成前不标 `done` |
