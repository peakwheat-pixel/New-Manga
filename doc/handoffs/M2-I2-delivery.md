---
task_id: M2-I2
author: Antigravity
recipient: Codex（独立非作者 Review 与集成）
base_commit: 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a
opening_head: 5d989bab6c5c8a24a5112303f95c2b8eea356bdc
delivery_commit: e359da759d1160467f61ced7061cdfe09772232f
status: done
---

# Handoff：M2-I2 Qt-free Logic Extraction（修订版 3）

## 1. 交付概况

- **任务 ID**：`M2-I2`（Qt-free Logic Extraction）
- **执行环境**：Worktree `G:/CODEX/New Manga.worktrees/M2-I2-antigravity`，分支 `agent/antigravity/M2-I2-qtfree-logic-extraction`
- **Git Common Directory**：`G:/CODEX/New Manga/.git`
- **固定 Base Commit**：`6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`
- **开工 HEAD**：`5d989bab6c5c8a24a5112303f95c2b8eea356bdc`
- **本次开工前 Reviewed HEAD**：`a4705a9f473d0e8d9087068edc4bec572d90439a`
- **本次产品与架构测试 Delivery Commit**：`e359da759d1160467f61ced7061cdfe09772232f`
- **交付状态**：`done`
- **交付目标**：迁出 M2-D1 矩阵 M2D1-25/26 已验证为 Qt-free 的两个模块至应用层权威位置；严格限定两个旧 shim 只能从各自对应的 `application.*` seam 重导出；彻底闭环 Codex 非作者复审 `doc/reviews/M2-I2-a4705a9.md` 提出的 Finding R-003（收紧 `__all__` 静态语法分析与增加动态 RHS 负例）与 Finding R-004（纠正 OpenSSL CLI 可执行文件检测文案）。

---

## 2. Codex Review（a4705a9）Findings 专项闭环说明

### 2.1 Finding R-003：收紧 `__all__` 静态守卫与判别性负例（已闭环）
- **问题与复现**：前次 `find_shim_violations` 仅核对了 `targets == ["__all__"]`，未对右侧表达式（RHS）做语法约束，Reviewer 复现发现 `__all__ = (lambda: ["TaskProjection"])()` 可被放行，存在动态执行漏洞。
- **实施改动**：
  1. 在 `tests/core/test_architecture.py` 的 `find_shim_violations` 中增加对 `__all__` RHS 值的深度静态 AST 校验：
     - RHS 必须为 `ast.List` 或 `ast.Tuple`，严禁任何动态函数/lambda 调用、变量名赋值或列表推导式；
     - 列表/元组中的每一个元素必须是字符串常量（`isinstance(elt, ast.Constant) and isinstance(elt.value, str)`）；
  2. 新增判别性负例测试 `test_reversal_guard_reports_dynamic_all_assignment_in_legacy_shims(tmp_path)`：
     - 包含 Reviewer 复现的 Lambda 调用：`__all__ = (lambda: ["TaskProjection"])()` 触发 `Call` 告警；
     - 包含变量赋值：`__all__ = exported_names` 触发 `Name` 告警；
     - 包含列表推导式：`__all__ = [name for name in names]` 触发 `ListComp` 告警；
     - 包含非字符串元素：`__all__ = ["TaskProjection", 123]` 触发非字符串常量告警；
     - 包含静态元组正例：`__all__ = ("TaskProjection",)` 验证安全放行；
  3. `tests/core/test_architecture.py` 扩充至 **16 项测试全部通过**（在 Python 3.12 与 Python 3.14 下均 16/16 passed）。

### 2.2 Finding R-004：更正 OpenSSL Skip 文案与依据（已闭环）
- **文案修正**：
  - 测试源码（`tests/network/test_connection_tester.py:24-25` 与 `tests/network/test_transport_tls.py:22-23`）通过 `openssl = shutil.which("openssl")` 判断 OpenSSL 命令行可执行文件是否在系统 PATH 中。
  - 纠正原先“无 OpenSSL 模块”的表述，准确更正为：
    > 当前环境 PATH 中未发现 openssl 命令行可执行文件（`shutil.which("openssl")` 返回 None）；测试通过 `pytest.mark.skipif(openssl is None, reason="openssl unavailable")` 判定后执行跳过。
  - 严禁将该现象描述为 Python OpenSSL / ssl / cryptography 模块缺失。
  - 在 `doc/handoffs/M2-I2-delivery.md` 与 `verification/M2-I2/full-suite.log` 均完成精确修正。

---

## 3. 核心设计与架构边界

### 3.1 权威逻辑迁入 Application 目标位置
- `src/application/tasks/projection.py`（338 行）：权威任务投影规则、状态与按钮矩阵、步骤流计算与页面排序/统计逻辑；完全纯数据与纯函数，无任何 Qt 依赖。
- `src/application/editing/region_canvas.py`（99 行）：权威归一化到页面像素几何映射、Half-up 舍入规则、Shoelace 面积校验及 typed 拒绝异常；完全纯数据与数学逻辑，无任何 Qt 依赖。

### 3.2 原 UI 位置缩为受严格守卫保护的兼容层
- `src/ui/models/tasks/projection.py`：缩为 39 行非权威兼容层，严格仅从 `application.tasks.projection` 导入，并通过静态 `__all__` 字符串列表重导出公共符号；
- `src/ui/viewmodels/workbench/region_canvas.py`：缩为 25 行非权威兼容层，严格仅从 `application.editing.region_canvas` 导入，并通过静态 `__all__` 字符串列表重导出公共符号。

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
| **I2-AC4** | 迁移/补强原测试，新增 architecture guard 防止权威逻辑倒流 UI；禁止导入探针须有判别力与原始证据。 | **PASS** | `tests/core/test_architecture.py` 16 项测试全部通过（在 Python 3.14.6 与 Python 3.12.3 均 16/16 passed）；shim 严格限定 application seam 重导出，静态 `__all__` 守卫生效，负例测试（本地定义、`ui.*` 导入、动态 `__all__`）均精准生效。 |
| **I2-AC5** | 既有 UI/业务测试通过；任何 skip、环境阻塞或兼容例外明确记录。 | **PASS** | ① 集成候选树 Workbench 全套 127 项 + Architecture 16 项 = 143 项测试全部 passed（`integration-workbench-architecture.log`，Exit 0）；<br>② Python 3.14 无 Qt 环境下跑 `tests/workbench/test_{region_canvas,projection}.py` + 架构守卫 40 passed, 2 skipped（`integration-qtfree-suite.log`，Exit 0，2 skips 已归因）；<br>③ Codex 在固定 Revised HEAD `0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716` 独立重跑全仓测试：1256 collected，1249 passed, 6 skipped, 1 failed（Exit 1）；旧交付日志的 1247 passed 未覆盖新增测试，已归档为 `full-suite-delivery-pre-rerun.log`，当前 `full-suite.log` 为重跑日志。 |

---

## 5. 测试运行与归因记录

- **Workbench + Architecture 套件**：
  - 解释器：`G:\CODEX\New Manga.task-envs\T3.2.1-packaging-py312\Scripts\python.exe` (Python 3.12.3)
  - 命令：`& 'G:\CODEX\New Manga.task-envs\T3.2.1-packaging-py312\Scripts\python.exe' -m pytest -v tests/workbench tests/core/test_architecture.py`
  - 结果：**143 passed in 11.77s，Exit code: 0**
  - 日志：[`verification/M2-I2/workbench-suite.log`](../../verification/M2-I2/workbench-suite.log)
- **No-Qt 独立套件**：
  - 解释器：`C:\Python314\python.exe` (Python 3.14.6，未安装 PySide6)
  - 命令：`& C:\Python314\python.exe -m pytest -v tests/workbench/test_projection.py tests/workbench/test_region_canvas.py tests/core/test_architecture.py`
  - 结果：**40 passed, 2 skipped in 0.26s，Exit code: 0**
  - 日志：[`verification/M2-I2/qtfree-suite.log`](../../verification/M2-I2/qtfree-suite.log)
- **Focused Shim & 负例套件**：
  - 命令：`pytest -v tests/core/test_architecture.py -k "legacy_ui_shims or reversal_guard"`
  - 指定的四个 pure-shim / 本地定义 / `ui.*` / 动态 `__all__` 守卫在集成候选树的复验：**4 passed, 12 deselected，Exit code: 0**
  - 日志：[`verification/M2-I2/integration-shim-guards.log`](../../verification/M2-I2/integration-shim-guards.log)
- **全仓测试记录（Codex 独立复跑；固定 Revised HEAD `0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716`）**：
  - 解释器：`G:\CODEX\New Manga.task-envs\T3.2.1-packaging-py312\Scripts\python.exe` (Python 3.12.3)
  - 命令：`& 'G:\CODEX\New Manga.task-envs\T3.2.1-packaging-py312\Scripts\python.exe' -m pytest -v -rs`
  - 结果：**1256 items collected；1249 passed, 6 skipped, 1 failed, 1 warning in 70.01s，Exit code: 1**
  - **6 项 SKIPPED 精确归因**：
    1. `tests/network/test_connection_tester.py:106`: `reason="openssl unavailable"`；
    2. `tests/network/test_transport_tls.py:39`: `reason="openssl unavailable"`；
    3. `tests/network/test_transport_tls.py:47`: `reason="openssl unavailable"`；
    4. `tests/network/test_transport_tls.py:62`: `reason="openssl unavailable"`；
    5. `tests/network/test_transport_tls.py:69`: `reason="openssl unavailable"`；
    6. `tests/network/test_transport_tls.py:83`: `reason="openssl unavailable"`。
    跳过原因均为当前环境 PATH 中未发现 openssl 命令行可执行文件（`shutil.which("openssl")` 返回 None），完全符合 `STATUS.md` 所载 "six OpenSSL skips"。
  - **1 项 FAILED 详细归因**：
    `tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment` 断言当前虚拟环境中不应安装模型运行时，但当前全局工作环境已预装 `torch`，属于已知环境固有状态（与 `STATUS.md` 记载一致），非 M2-I2 变更引起。
  - 环境探针：`ssl=OpenSSL 3.0.13`、`shutil.which("openssl") is None`、`torch_installed=True`，见 [`verification/M2-I2/review-0d6acc7/full-suite-environment.log`](../../verification/M2-I2/review-0d6acc7/full-suite-environment.log)。
  - 当前全仓原始日志：[`verification/M2-I2/full-suite.log`](../../verification/M2-I2/full-suite.log)；作者交付时旧运行日志保留在 [`verification/M2-I2/full-suite-delivery-pre-rerun.log`](../../verification/M2-I2/full-suite-delivery-pre-rerun.log)。

- **Codex 集成候选树复验**（产品代码与固定 Reviewed HEAD 一致）：
  - `python -m pytest -v tests/workbench tests/core/test_architecture.py`：**143 passed in 12.49s，Exit 0**；日志：[`verification/M2-I2/integration-workbench-architecture.log`](../../verification/M2-I2/integration-workbench-architecture.log)。
  - Python 3.14.6 无 Qt 环境执行 `python -m pytest -v -rs tests/workbench/test_projection.py tests/workbench/test_region_canvas.py tests/core/test_architecture.py`：**40 passed, 2 skipped in 0.91s，Exit 0**。两个 skip 是兼容重导出测试因未安装 PySide6；日志：[`verification/M2-I2/integration-qtfree-suite.log`](../../verification/M2-I2/integration-qtfree-suite.log)。
  - 四个 R-003 shim guard 测试：**4 passed, 12 deselected，Exit 0**；日志：[`verification/M2-I2/integration-shim-guards.log`](../../verification/M2-I2/integration-shim-guards.log)。

---

## 6. 范围核验与空白审计（Scope & Whitespace Audit）

- **空白审计**：
  - `git diff --check 5d989bab6c5c8a24a5112303f95c2b8eea356bdc e359da759d1160467f61ced7061cdfe09772232f`：**Exit Code 0**（零警告、零 trailing whitespace、零 EOF 换行问题）。
  - `git diff --check a4705a9f473d0e8d9087068edc4bec572d90439a e359da759d1160467f61ced7061cdfe09772232f`：**Exit Code 0**。
  - Codex 集成检查：固定 Base→Reviewed HEAD、Reviewed HEAD→产品集成提交及产品集成→完成记录的 `git diff --check` 均 **Exit Code 0**，见 [`verification/M2-I2/integration-check.log`](../../verification/M2-I2/integration-check.log)。
- **受保护路径审计**：
  `src/application/**`、`src/ui/**`、`src/bootstrap/**`、`src/domain/**`、`src/ports/**`、`src/infrastructure/**`、Schema、requirements、React、Tauri、IPC 零改动。本次修改严格限于 `tests/core/test_architecture.py`、`doc/handoffs/M2-I2-delivery.md`、`doc/tasks/M2-I2.md` 与 `verification/M2-I2/**`。

---

## 7. 证据文件清单

- [`verification/M2-I2/pre-migration-baseline.log`](../../verification/M2-I2/pre-migration-baseline.log)：修改前基线证据，记录 Git 状态、测试套件修前结果以及旧位置在无 Qt 环境导入失败的原始日志。
- [`verification/M2-I2/workbench-suite.log`](../../verification/M2-I2/workbench-suite.log)：Workbench 全套 127 项 + Architecture 16 项 = 143 项测试全绿原始日志（Exit Code 0）。
- [`verification/M2-I2/qtfree-suite.log`](../../verification/M2-I2/qtfree-suite.log)：Python 3.14.6 无 Qt 纯净环境下运行迁移模块与架构测试的原始日志（40 passed, 2 skipped, Exit Code 0，含 skip 归因）。
- [`verification/M2-I2/full-suite.log`](../../verification/M2-I2/full-suite.log)：固定 Revised HEAD 的 Codex 全仓重跑原始日志（1256 collected、1249 passed, 6 skipped, 1 failed, Exit Code 1）。
- [`verification/M2-I2/full-suite-delivery-pre-rerun.log`](../../verification/M2-I2/full-suite-delivery-pre-rerun.log)：作者原始交付日志；运行早于新增架构测试，统计为 1254 collected / 1247 passed，不作为当前结果。
- [`verification/M2-I2/review-0d6acc7/`](../../verification/M2-I2/review-0d6acc7/)：固定 Revised HEAD 的环境探针、工作台/架构与 Qt-free 独立复跑原始日志。
- [`verification/M2-I2/integration-*.log`](../../verification/M2-I2/)：Codex 集成候选树的工作台+架构、Qt-free 与 shim guard 验证日志。
- [`verification/M2-I2/integration-check.log`](../../verification/M2-I2/integration-check.log)：固定 Base、Reviewed HEAD、集成提交与完成记录之间的 diff/whitespace 检查。
- [`verification/M2-I2/post-migration-verification.log`](../../verification/M2-I2/post-migration-verification.log)：修改后 65 项 focused 测试通过日志与 28 项跨模块语义/字节等价性探针聚合日志。
- [`verification/M2-I2/verify_m2_i2.py`](../../verification/M2-I2/verify_m2_i2.py)：综合验证探针脚本，覆盖 AC1~AC4 的可重复自动测试。
- [`verification/M2-I2/diff-check.log`](../../verification/M2-I2/diff-check.log)：空白检查（Exit Code 0）及对开工 HEAD、基线 Commit、前次 HEAD 的 diff stat 记录。

---

## 8. 后续交接与下一步建议

- 按照《协作协议》（09_COLLABORATION.md §5.1）规范：修订交付提交为 `e359da759d1160467f61ced7061cdfe09772232f`，完整 Revised HEAD 为 `0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716`；Codex Review 已批准，M2-I2 集成提交=`7e2da6b8eb55e437d36fa3fa11cbf3e976a834c9`，Task 与 Handoff 均为 `done`。
- **下一 Task：M2-I1 Core Assembly Seam（ZCode）**。先将原交付 HEAD `cb459027f111f381d906e944edb5ac78eb641dea` reconcile 到 M2-I2 集成基线 `7e2da6b8eb55e437d36fa3fa11cbf3e976a834c9`，保留 Task 冻结写集合；提交新的固定 HEAD/Handoff 后由 Codex 复审并做集成验证。不得把 I1 状态直接推进为 `done`。
