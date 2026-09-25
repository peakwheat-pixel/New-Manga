---
task_id: M2-I2
author: Antigravity
recipient: Codex（独立非作者 Review 与集成）
base_commit: 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a
opening_head: 5d989bab6c5c8a24a5112303f95c2b8eea356bdc
delivery_commit: be5e8d830fba2f9ca1b0cd79148cc386c4468061
status: in_review
---

# Handoff：M2-I2 Qt-free Logic Extraction（修订版 2）

## 1. 交付概况

- **任务 ID**：`M2-I2`（Qt-free Logic Extraction）
- **执行环境**：Worktree `G:/CODEX/New Manga.worktrees/M2-I2-antigravity`，分支 `agent/antigravity/M2-I2-qtfree-logic-extraction`
- **Git Common Directory**：`G:/CODEX/New Manga/.git`
- **固定 Base Commit**：`6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`
- **开工 HEAD**：`5d989bab6c5c8a24a5112303f95c2b8eea356bdc`
- **前次 Reviewed HEAD**：`5d4a4650943507ca4053376d6acea36f146c704a`
- **前次修订 HEAD**：`86ecb94b7f2acd356923d5408c80ac81d942fd03`
- **本次产品与架构测试 Delivery Commit**：`be5e8d830fba2f9ca1b0cd79148cc386c4468061`
- **交付状态**：`in_review`
- **交付目标**：迁出 M2-D1 矩阵 M2D1-25/26 已验证为 Qt-free 的两个模块至应用层权威位置；严格限定两个旧 shim 只能从各自对应的 `application.*` seam 重导出；补齐针对 `ui.*` 导入的判别性负例；精准更正 6 个 skip 与 1 个 failure 的全仓归因；记录完整的解释器、命令与 Exit Code 证据。

---

## 2. 本次修订专项强化说明

### 2.1 强化 Legacy UI Shim 守卫（Architecture Guard）
在 `tests/core/test_architecture.py` 中对旧 UI 兼容 shim 施加了更高精度的双向约束：
1. **严格限定重导出源**：
   - `src/ui/models/tasks/projection.py` 只允许从 `application.tasks.projection` 导入；
   - `src/ui/viewmodels/workbench/region_canvas.py` 只允许从 `application.editing.region_canvas` 导入；
   - 严禁任何来自 `ui.*`、相对路径或其他未授权模块的导入。
2. **AST 语法树解析与全面禁止项**：
   - 严禁任何 `FunctionDef`、`AsyncFunctionDef`、`ClassDef`；
   - 严禁任何非 `__all__` 的变量赋值；
   - 严禁任何 `import xxx` 形式的裸导入；
   - 仅允许模块文档字符串、`from __future__ import annotations`、指定的单向应用层导入以及 `__all__` 导出列表。
3. **新增与保留两类判别性负例测试**：
   - **保留本地函数/类定义负例**：`test_reversal_guard_reports_local_definitions_in_legacy_shims(tmp_path)` 验证对注入本地函数 `revived_business_rule` 和类 `RevivedModel` 能精准变红告警；
   - **新增从 `ui.*` 导入负例**：`test_reversal_guard_reports_ui_imports_in_legacy_shims(tmp_path)` 验证当旧 shim 尝试从 `ui.models.tasks.page_list_model` 或 `ui.viewmodels.workbench.viewmodel` 导入时，守卫精准拦截并报告违规行号与非应用层来源；
   - 架构测试套件增至 15 项，在 Python 3.12 与独立纯净无 Qt 环境 Python 3.14 下均全部 PASS。

### 2.2 精准更正全仓测试日志（full-suite）归因
在 `verification/M2-I2/full-suite.log` 中，撤回先前泛化推断，依据原始 pytest 输出对跳过与失败给出精确到文件行号的归因：
- **运行命令**：`& 'G:\CODEX\New Manga.task-envs\T3.2.1-packaging-py312\Scripts\python.exe' -m pytest -v -rs`
- **解释器**：`Python 3.12.3`（Windows win32, pytest-9.1.1）
- **结果统计**：`1247 passed, 6 skipped, 1 failed, 1 warning in 75.38s (0:01:15)`，**Exit code: 1**
- **6 项 SKIPPED 逐条精确归因**：
  1. `tests/network/test_connection_tester.py:106`: `openssl unavailable` (本地测试环境无 OpenSSL 模块跳过)；
  2. `tests/network/test_transport_tls.py:39`: `openssl unavailable` (本地测试环境无 OpenSSL 模块跳过)；
  3. `tests/network/test_transport_tls.py:47`: `openssl unavailable` (本地测试环境无 OpenSSL 模块跳过)；
  4. `tests/network/test_transport_tls.py:62`: `openssl unavailable` (本地测试环境无 OpenSSL 模块跳过)；
  5. `tests/network/test_transport_tls.py:69`: `openssl unavailable` (本地测试环境无 OpenSSL 模块跳过)；
  6. `tests/network/test_transport_tls.py:83`: `openssl unavailable` (本地测试环境无 OpenSSL 模块跳过)；
  （上述 6 项均与 STATUS.md 所载 "six OpenSSL skips" 完全一致）。
- **1 项 FAILED 详细归因**：
  - `tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment`
  - 失败原因：测试断言当前环境不应预装任何深度学习运行时，但当前全局工作环境已预装 `torch`，属于已知环境固有状态（与 STATUS.md 记载一致），非 M2-I2 引入。

---

## 3. 核心设计与架构边界

### 3.1 权威逻辑迁入 Application 目标位置
- `src/application/tasks/projection.py`（338 行）：权威任务投影规则、状态与按钮矩阵、步骤流计算与页面排序/统计逻辑；完全纯数据与纯函数，无任何 Qt 依赖。
- `src/application/editing/region_canvas.py`（99 行）：权威归一化到页面像素几何映射、Half-up 舍入规则、Shoelace 面积校验及 typed 拒绝异常；完全纯数据与数学逻辑，无任何 Qt 依赖。

### 3.2 原 UI 位置缩为受严格守卫保护的兼容层
- `src/ui/models/tasks/projection.py`：缩为 39 行非权威兼容层，严格仅从 `application.tasks.projection` 导入并重导出公共符号；
- `src/ui/viewmodels/workbench/region_canvas.py`：缩为 25 行非权威兼容层，严格仅从 `application.editing.region_canvas` 导入并重导出公共符号。

### 3.3 消费方导入路径重接（Rewire Consumers）
- `src/ui/models/tasks/__init__.py`：改由 `application.tasks.projection` 导出公共投影符号；
- `src/ui/models/tasks/page_list_model.py`：改从 `application.tasks.projection` 导入；
- `src/ui/viewmodels/workbench/viewmodel.py`：改从 `application.tasks.projection` 与 `application.editing.region_canvas` 导入权威符号。

---

## 4. Acceptance Criteria 达成证据矩阵

| AC 项 | 目标与要求 | 状态 | 验证证据与输出 |
|---|---|---|---|
| **I2-AC1** | 两个模块迁移前后输出 byte/semantic compatible；覆盖投影状态/按钮矩阵/步骤流与 region rounding/边界/零面积拒绝规则。 | **PASS** | `verify_m2_i2.py` 执行 28 项跨模块对比探针全部通过；`test_projection.py`（13 用例）与 `test_region_canvas.py`（13 用例）全部通过；输出完全一致。 |
| **I2-AC2** | `src/ui` 不再是两类规则的权威位置；Legacy ViewModel、PageListModel、QML 使用方经 `src/application` seam 消费。 | **PASS** | 两个旧 UI 模块受 `find_shim_violations` 严格守卫；消费方（`page_list_model.py`、`viewmodel.py`、`__init__.py`）切至 `src/application`；持久化守卫通过。 |
| **I2-AC3** | 新位置按模块名无 PySide6 可导入；不新增 `src/application → src/ui` 依赖。 | **PASS** | 独立 Python 3.14.6（无 PySide6 环境）成功以模块名 `import application.tasks.projection` 与 `import application.editing.region_canvas` 并执行全部业务逻辑；`APPLICATION_FORBIDDEN` 包含 `ui`，全仓 AST 检查 0 违规。 |
| **I2-AC4** | 迁移/补强原测试，新增 architecture guard 防止权威逻辑倒流 UI；禁止导入探针须有判别力与原始证据。 | **PASS** | `tests/core/test_architecture.py` 15 项测试全部通过（在 Python 3.14.6 与 Python 3.12.3 均 15/15 passed）；shim 严格限定 application seam 重导出，负例测试（本地定义与 `ui.*` 导入）均精准生效。 |
| **I2-AC5** | 既有 UI/业务测试通过；任何 skip、环境阻塞或兼容例外明确记录。 | **PASS** | ① Workbench 全套 127 项 + Architecture 15 项 = 142 项测试全部 passed（`workbench-suite.log`，Exit 0）；<br>② Python 3.14 无 Qt 环境下跑 `tests/workbench/test_{region_canvas,projection}.py` + 架构守卫 39 passed, 2 skipped（`qtfree-suite.log`，Exit 0，2 skips 已归因）；<br>③ 全仓全套测试 1247 passed, 6 skipped, 1 failed（`full-suite.log`，Exit 1，6 skips 与 1 failure 均已精准指明行号与归因）。 |

---

## 5. 范围核验与空白审计（Scope & Whitespace Audit）

- **空白审计**：
  - `git diff --check 5d989bab6c5c8a24a5112303f95c2b8eea356bdc be5e8d830fba2f9ca1b0cd79148cc386c4468061`：**Exit Code 0**（零警告、零 trailing whitespace、零 EOF 换行问题）。
  - `git diff --check 86ecb94b7f2acd356923d5408c80ac81d942fd03 be5e8d830fba2f9ca1b0cd79148cc386c4468061`：**Exit Code 0**。
- **受保护路径审计**：
  `src/bootstrap/**` 保持只读（零改动）；Domain Contract、Schema、ports、依赖配置（`requirements.txt` / `pyproject.toml`）零修改。
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
  - `verification/M2-I2/**` (新增/更新证据文件)

---

## 6. 证据文件清单

- [`verification/M2-I2/pre-migration-baseline.log`](../../verification/M2-I2/pre-migration-baseline.log)：修改前基线证据，记录 Git 状态、测试套件修前结果以及旧位置在无 Qt 环境导入失败的原始日志。
- [`verification/M2-I2/workbench-suite.log`](../../verification/M2-I2/workbench-suite.log)：Workbench 全套 127 项 + Architecture 15 项 = 142 项测试全绿原始日志（Exit Code 0）。
- [`verification/M2-I2/qtfree-suite.log`](../../verification/M2-I2/qtfree-suite.log)：Python 3.14.6 无 Qt 纯净环境下运行迁移模块与架构测试的原始日志（39 passed, 2 skipped, Exit Code 0，含 skip 归因）。
- [`verification/M2-I2/full-suite.log`](../../verification/M2-I2/full-suite.log)：全仓测试原始运行日志（1247 passed, 6 skipped, 1 failed, Exit Code 1，含精确到测试行号的 6 skips 与 1 failure 归因）。
- [`verification/M2-I2/post-migration-verification.log`](../../verification/M2-I2/post-migration-verification.log)：修改后 64 项 focused 测试通过日志与 28 项跨模块语义/字节等价性探针聚合日志。
- [`verification/M2-I2/verify_m2_i2.py`](../../verification/M2-I2/verify_m2_i2.py)：综合验证探针脚本，覆盖 AC1~AC4 的可重复自动测试。
- [`verification/M2-I2/diff-check.log`](../../verification/M2-I2/diff-check.log)：空白检查（Exit Code 0）及对开工 HEAD、基线 Commit、前次 HEAD 的 diff stat 记录。

---

## 7. 后续交接与下一步建议

按照《协作协议》（09_COLLABORATION.md §5.1）规范：
- 本 Task `M2-I2` 已在独立工作树 `G:/CODEX/New Manga.worktrees/M2-I2-antigravity` 完成代码强化、测试与证据的完整修订与固化，状态置为 `in_review`。
- **推荐下一步**：交由 **Codex** 进行独立非作者复审（Review of revised head），获批后再进行集成验证；之后再协调 M2-I1 基线。
- 可直接转发给 Codex 的指令见最终回复。
