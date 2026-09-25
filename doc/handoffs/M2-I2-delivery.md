---
task_id: M2-I2
author: Antigravity
recipient: Codex（独立非作者 Review 与集成）
base_commit: 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a
opening_head: 5d989bab6c5c8a24a5112303f95c2b8eea356bdc
delivery_commit: df26908354c4146a48f4388a10787e221323aa04
status: in_review
---

# Handoff：M2-I2 Qt-free Logic Extraction

## 1. 交付概况

- **任务 ID**：`M2-I2`（Qt-free Logic Extraction）
- **执行环境**：Worktree `G:/CODEX/New Manga.worktrees/M2-I2-antigravity`，分支 `agent/antigravity/M2-I2-qtfree-logic-extraction`
- **Git Common Directory**：`G:/CODEX/New Manga/.git`
- **固定 Base Commit**：`6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`
- **开工 HEAD**：`5d989bab6c5c8a24a5112303f95c2b8eea356bdc`
- **产品与测试 Delivery Commit**：`df26908354c4146a48f4388a10787e221323aa04`（short: `df26908`）
- **交付目标**：迁出 M2-D1 矩阵 M2D1-25/26 已验证为 Qt-free 的两个模块（任务投影与 Region 画布几何转换/拒绝规则）至应用层权威位置，重接消费方与测试，建立架构防倒流守卫，保存完整验证对照证据。

---

## 2. 变更内容与架构边界

### 2.1 权威逻辑迁入 Application 目标位置
- `src/application/tasks/projection.py`（338 行）：接收原 `ui/models/tasks/projection.py` 的任务投影规则、状态与按钮矩阵、步骤流计算与页面排序/统计逻辑；完全纯数据与纯函数，无任何 Qt 依赖。
- `src/application/editing/region_canvas.py`（99 行）：接收原 `ui/viewmodels/workbench/region_canvas.py` 的归一化到页面像素几何映射、Half-up 舍入规则、Shoelace 面积校验及 typed 拒绝异常；完全纯数据与数学逻辑，无任何 Qt 依赖。

### 2.2 原 UI 位置缩为非权威向后兼容层（Backward-compatibility Shim）
- `src/ui/models/tasks/projection.py`：缩为 34 行非权威兼容层，直接从 `application.tasks.projection` 导出所有公共符号，不含任何计算与定义。
- `src/ui/viewmodels/workbench/region_canvas.py`：缩为 24 行非权威兼容层，直接从 `application.editing.region_canvas` 导出所有公共符号，不含任何计算与定义。

### 2.3 消费方导入路径重接（Rewire Consumers）
- `src/ui/models/tasks/__init__.py`：改由 `application.tasks.projection` 导出 `PageProjectionRow`、`TaskProjection`、`build_projection`。
- `src/ui/models/tasks/page_list_model.py`：改从 `application.tasks.projection` 导入 `PageProjectionRow`, `TaskProjection`。
- `src/ui/viewmodels/workbench/viewmodel.py`：改从 `application.tasks.projection` 与 `application.editing.region_canvas` 导入权威符号（含第 225 行 `_idle_projection` 内部局部导入）。

### 2.4 测试迁移与增强
- `tests/workbench/test_projection.py`：主测试导入切换至 `application.tasks.projection`，增加向后兼容性验证 `test_backward_compatibility_reexports`。
- `tests/workbench/test_region_canvas.py`：主测试导入切换至 `application.editing.region_canvas`，增加向后兼容性验证 `test_backward_compatibility_reexports`。
- `tests/workbench/test_page_list_model.py`：`build_projection` 导入切换至 `application.tasks.projection`。
- `tests/workbench/test_qml_workbench.py`：两处 `normalized_to_page_geometry` 导入切换至 `application.editing.region_canvas`。

### 2.5 架构防倒流守卫强化（Architecture Guards）
- 在 `tests/core/test_architecture.py` 中：
  - 设置 `APPLICATION_FORBIDDEN = frozenset({"infrastructure", "ui"})`，防止 `src/application` 发生架构倒流依赖 `src/ui`；
  - 增加 `test_migrated_application_modules_are_qt_free`，断言 `src/application/tasks/projection.py` 与 `src/application/editing/region_canvas.py` 绝无 `PySide6` 导入；
  - 增加 `test_workbench_ui_consumers_import_from_application_seams`，防止 UI 消费方倒流引用旧 UI shim 模块；
  - 增加三组具有判别力的正反探针测试（反向导入 UI 探针、PySide6 探针、倒流引用探针）。

---

## 3. Acceptance Criteria 达成证据矩阵

| AC 项 | 目标与要求 | 状态 | 验证证据与输出 |
|---|---|---|---|
| **I2-AC1** | 两个模块迁移前后输出 byte/semantic compatible；覆盖投影状态/按钮矩阵/步骤流与 region rounding/边界/零面积拒绝规则。 | **PASS** | `verify_m2_i2.py` 执行 28 项跨模块对比探针全部通过；`test_projection.py`（13 用例）与 `test_region_canvas.py`（13 用例）全部通过；输出完全一致。 |
| **I2-AC2** | `src/ui` 不再是两类规则的权威位置；Legacy ViewModel、PageListModel、QML 使用方经 `src/application` seam 消费。 | **PASS** | AST 扫描证明两个旧 UI 模块不含函数/类定义，所有消费方（`page_list_model.py`、`viewmodel.py`、`__init__.py`）均已切至 `src/application`；QML 工作台测试全绿。 |
| **I2-AC3** | 新位置按模块名无 PySide6 可导入；不新增 `src/application → src/ui` 依赖。 | **PASS** | 独立 Python 3.14.6（未安装 PySide6）成功以模块名 `import application.tasks.projection` 与 `import application.editing.region_canvas` 并执行计算；`APPLICATION_FORBIDDEN` 包含 `ui`，全仓 AST 检查 0 违规。 |
| **I2-AC4** | 迁移/补强原测试，新增 architecture guard 防止权威逻辑倒流 UI；禁止导入探针须有判别力与原始证据。 | **PASS** | `tests/core/test_architecture.py` 12 项测试全部通过（在 Python 3.14.6 与 Python 3.12.3 均 12/12 passed）；三组判别性探针验证了对违规行为的准确告警。 |
| **I2-AC5** | 既有 UI/业务测试通过；任何 skip、环境阻塞或兼容例外明确记录。 | **PASS** | ① 针对性套件 `tests/workbench/test_{projection,region_canvas,page_list_model,qml_workbench}.py` + `tests/core/test_architecture.py` 共有 61 项测试全部 passed；<br>② `tests/workbench/` 全套 127 项测试全部 passed；<br>③ 全仓全套测试 1245 passed, 6 skipped, 1 failed（唯一的 1 failure 为已知的 torch 安装环境断言 `test_no_model_runtime_is_installed_in_this_environment`，与本任务完全无关）；<br>④ Python 3.14 无 Qt 环境下跑 `tests/workbench/test_{region_canvas,projection}.py` 24 passed, 2 skipped（2 skips 明确原因为旧 UI 包 `__init__` 含有 PySide6 依赖）。 |

---

## 4. 范围核验与空白审计（Scope & Whitespace Audit）

- **空白审计**：
  `git diff --check 5d989bab6c5c8a24a5112303f95c2b8eea356bdc`：实测 **Exit Code 0**（零警告、零 trailing whitespace、零 EOF 换行问题）。
- **受保护路径审计**：
  `src/bootstrap/**` 零修改（属 I1 独占）；Domain Contract、Schema、ports、依赖配置（`requirements.txt` / `pyproject.toml`）零修改。
- **允许修改范围清单核对**：
  - `src/application/tasks/projection.py` (新增)
  - `src/application/editing/region_canvas.py` (新增)
  - `src/ui/models/tasks/projection.py` (修改，缩为兼容 shim)
  - `src/ui/viewmodels/workbench/region_canvas.py` (修改，缩为兼容 shim)
  - `src/ui/models/tasks/__init__.py` (修改，重接导入)
  - `src/ui/models/tasks/page_list_model.py` (修改，重接导入)
  - `src/ui/viewmodels/workbench/viewmodel.py` (修改，重接导入)
  - `tests/core/test_architecture.py` (修改，加 guard 与 probes)
  - `tests/workbench/test_page_list_model.py` (修改，重接导入)
  - `tests/workbench/test_projection.py` (修改，重接导入与兼容测试)
  - `tests/workbench/test_qml_workbench.py` (修改，重接导入)
  - `tests/workbench/test_region_canvas.py` (修改，重接导入与兼容测试)
  - `doc/tasks/M2-I2.md` (修改，状态与记录更新)
  - `doc/handoffs/M2-I2-delivery.md` (本交付文档)
  - `verification/M2-I2/**` (新增证据文件)

---

## 5. 证据文件清单

- [`verification/M2-I2/pre-migration-baseline.log`](../../verification/M2-I2/pre-migration-baseline.log)：修改前基线证据，记录 Git 状态、测试套件修前结果以及旧位置在无 Qt 环境导入失败的原始日志。
- [`verification/M2-I2/post-migration-verification.log`](../../verification/M2-I2/post-migration-verification.log)：修改后验证证据，包含 PySide6 环境 61 项 focused 测试通过日志、Python 3.14 无 Qt 环境测试日志及综合探针日志。
- [`verification/M2-I2/verify_m2_i2.py`](../../verification/M2-I2/verify_m2_i2.py)：综合验证探针脚本，覆盖 AC1~AC4 的可重复自动测试。
- [`verification/M2-I2/diff-check.log`](../../verification/M2-I2/diff-check.log)：空白检查（Exit Code 0）及对开工 HEAD、基线 Commit 的 diff stat 记录。

---

## 6. 后续交接与下一步建议

按照《协作协议》（09_COLLABORATION.md §5.1）规范：
- 本 Task `M2-I2` 已在独立工作树 `G:/CODEX/New Manga.worktrees/M2-I2-antigravity` 完成实现、测试与固化。
- 推荐下一步：交由 **Codex** 进行独立非作者 Review 与集成验证（先集成 I2，再由 I1 reconcile）。
- 可直接转发给 Codex 的指令见最终回复。
