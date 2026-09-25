---
task_id: M2-I2
author: Antigravity
recipient: Codex（独立非作者 Review 与集成）
base_commit: 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a
opening_head: 5d989bab6c5c8a24a5112303f95c2b8eea356bdc
delivery_commit: d9b718242b6516a2e9e5b3b36913ef2a63be4665
status: in_review
---

# Handoff：M2-I2 Qt-free Logic Extraction（修订版）

## 1. 交付概况

- **任务 ID**：`M2-I2`（Qt-free Logic Extraction）
- **执行环境**：Worktree `G:/CODEX/New Manga.worktrees/M2-I2-antigravity`，分支 `agent/antigravity/M2-I2-qtfree-logic-extraction`
- **Git Common Directory**：`G:/CODEX/New Manga/.git`
- **固定 Base Commit**：`6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`
- **开工 HEAD**：`5d989bab6c5c8a24a5112303f95c2b8eea356bdc`
- **前次 Reviewed HEAD**：`5d4a4650943507ca4053376d6acea36f146c704a`
- **本次产品与测试 Delivery Commit**：`d9b718242b6516a2e9e5b3b36913ef2a63be4665`
- **交付状态**：`in_review`
- **交付目标**：迁出 M2-D1 矩阵 M2D1-25/26 已验证为 Qt-free 的两个模块（任务投影与 Region 画布几何转换/拒绝规则）至应用层权威位置，重接消费方与测试，建立架构防倒流守卫，并按 Codex Review 意见彻底闭环 P-01、S-01、S-02、S-03。

---

## 2. Codex Review（5d4a465）修订闭环说明

针对 Codex 在 `doc/reviews/M2-I2-5d4a465.md` 中提出的 4 项诊断意见，本次修订已逐项实施严格闭环：

### 2.1 P-01 (Architecture Guard 守卫强化与负例验证)
- **原因与缺陷**：前次仅验证了 UI 消费方切至 application seam，但未在长期架构测试中对两个旧 UI shim（`src/ui/models/tasks/projection.py` 与 `src/ui/viewmodels/workbench/region_canvas.py`）本身做 AST 语法树结构限定，缺乏长期防死灰复燃守卫与判别性负例。
- **实施改动**：
  1. 在 `tests/core/test_architecture.py` 中定义 `LEGACY_UI_SHIMS` 常量与 AST 解析函数 `find_shim_local_definitions(path: Path) -> list[str]`；
  2. 严禁旧 UI shim 包含任何 `FunctionDef`、`AsyncFunctionDef`、`ClassDef` 或非 `__all__` 赋值语句；
  3. 新增持久化守卫测试 `test_legacy_ui_shims_contain_no_authoritative_logic`；
  4. 新增判别性负例测试 `test_reversal_guard_reports_local_definitions_in_legacy_shims(tmp_path)`，针对构造的包含 `revived_business_rule` 和 `RevivedModel` 的变异 shim 精准变红告警；
  5. `tests/core/test_architecture.py` 测试套件扩展至 14 项，全部 PASS。

### 2.2 S-01 (Verification Evidence 原始日志补齐与归因)
- **改进措施**：补齐所有声称运行的原始全量日志，附带完整 Shell、解释器路径、时间戳、命令、逐项测试状态与 Exit Code；对所有 skip 与 failure 给出逐条归因分析：
  - `verification/M2-I2/workbench-suite.log`：Workbench 全套（127 项）+ Architecture（14 项）= 141 项测试全部 PASSED（Exit Code 0）；
  - `verification/M2-I2/qtfree-suite.log`：在独立 Python 3.14.6（无 PySide6 环境）下运行迁移模块业务测试与架构守卫，38 passed, 2 skipped（Exit Code 0）。对 2 个 skip 明确归因：向后兼容性测试导入了旧 UI shim，而旧 UI 包顶层 `src/ui/models/tasks/__init__.py` 等引用了含有 PySide6 的模块，触发环境探测并安全 skip，符合预期；
  - `verification/M2-I2/full-suite.log`：全仓全套测试运行日志，结果 1247 passed, 6 skipped, 1 failed（Exit Code 1）。
    - 6 个 skipped 逐条归因：`tests/infrastructure/test_http_client.py` 内部测试跳过（6 项均为本地环境无活动网络或 OpenSSL CA 握手配置跳过，与业务逻辑无关）；
    - 1 个 failure 详细归因：`tests/core/test_model_runtime_boundary.py::test_no_model_runtime_is_installed_in_this_environment` 断言当前虚拟环境不应预装任何深度学习运行时，但当前全局工作环境预装了 `torch`，属于已知环境固有状态（与 `STATUS.md` 记载一致），非 M2-I2 引入；
  - `verification/M2-I2/post-migration-verification.log`：整合包含 28 项跨模块语义与字节等价性探针的验证日志。

### 2.3 S-02 (Task Status 纠正)
- **更正**：`doc/tasks/M2-I2.md` 的 `status` 字段保持为标准状态机要求的 `in_review`，不跳过独立 Review 与集成阶段。

### 2.4 S-03 (Delivery SHA 修正)
- **更正**：修正前次笔误，本次产品与测试 Delivery Commit 精确使用 `git rev-parse HEAD` 输出的完整 40 位 SHA：
  `d9b718242b6516a2e9e5b3b36913ef2a63be4665`。

---

## 3. 核心设计与架构边界

### 3.1 权威逻辑迁入 Application 目标位置
- `src/application/tasks/projection.py`（338 行）：接收原 `ui/models/tasks/projection.py` 的任务投影规则、状态与按钮矩阵、步骤流计算与页面排序/统计逻辑；完全纯数据与纯函数，无任何 Qt 依赖。
- `src/application/editing/region_canvas.py`（99 行）：接收原 `ui/viewmodels/workbench/region_canvas.py` 的归一化到页面像素几何映射、Half-up 舍入规则、Shoelace 面积校验及 typed 拒绝异常；完全纯数据与数学逻辑，无任何 Qt 依赖。

### 3.2 原 UI 位置缩为非权威向后兼容层（Backward-compatibility Shim）
- `src/ui/models/tasks/projection.py`：缩为 34 行非权威兼容层，直接从 `application.tasks.projection` 导出所有公共符号，不含任何计算与定义。
- `src/ui/viewmodels/workbench/region_canvas.py`：缩为 24 行非权威兼容层，直接从 `application.editing.region_canvas` 导出所有公共符号，不含任何计算与定义。

### 3.3 消费方导入路径重接（Rewire Consumers）
- `src/ui/models/tasks/__init__.py`：改由 `application.tasks.projection` 导出 `PageProjectionRow`、`TaskProjection`、`build_projection`。
- `src/ui/models/tasks/page_list_model.py`：改从 `application.tasks.projection` 导入 `PageProjectionRow`, `TaskProjection`。
- `src/ui/viewmodels/workbench/viewmodel.py`：改从 `application.tasks.projection` 与 `application.editing.region_canvas` 导入权威符号（含第 225 行 `_idle_projection` 内部局部导入）。

### 3.4 架构防倒流守卫强化（Architecture Guards）
在 `tests/core/test_architecture.py` 中：
- `APPLICATION_FORBIDDEN = frozenset({"infrastructure", "ui"})`，防止 `src/application` 依赖 `src/ui`；
- `test_migrated_application_modules_are_qt_free` 断言新应用层模块绝无 `PySide6` 导入；
- `test_workbench_ui_consumers_import_from_application_seams` 防止 UI 消费方倒流引用旧 UI shim 模块；
- `test_legacy_ui_shims_contain_no_authoritative_logic` 防止旧 UI shim 死灰复燃或添加业务定义；
- 四组判别性探针（反向导入 UI 探针、PySide6 探针、倒流引用探针、shim 本地定义探针）确保告警能力有效。

---

## 4. Acceptance Criteria 达成证据矩阵

| AC 项 | 目标与要求 | 状态 | 验证证据与输出 |
|---|---|---|---|
| **I2-AC1** | 两个模块迁移前后输出 byte/semantic compatible；覆盖投影状态/按钮矩阵/步骤流与 region rounding/边界/零面积拒绝规则。 | **PASS** | `verify_m2_i2.py` 执行 28 项跨模块对比探针全部通过；`test_projection.py`（13 用例）与 `test_region_canvas.py`（13 用例）全部通过；输出完全一致。 |
| **I2-AC2** | `src/ui` 不再是两类规则的权威位置；Legacy ViewModel、PageListModel、QML 使用方经 `src/application` seam 消费。 | **PASS** | AST 扫描证明两个旧 UI 模块不含任何函数/类定义；消费方（`page_list_model.py`、`viewmodel.py`、`__init__.py`）均已切至 `src/application`；持久化守卫 `test_legacy_ui_shims_contain_no_authoritative_logic` 通过。 |
| **I2-AC3** | 新位置按模块名无 PySide6 可导入；不新增 `src/application → src/ui` 依赖。 | **PASS** | 独立 Python 3.14.6（无 PySide6 环境）成功以模块名 `import application.tasks.projection` 与 `import application.editing.region_canvas` 并执行全部业务逻辑；`APPLICATION_FORBIDDEN` 包含 `ui`，全仓 AST 检查 0 违规。 |
| **I2-AC4** | 迁移/补强原测试，新增 architecture guard 防止权威逻辑倒流 UI；禁止导入探针须有判别力与原始证据。 | **PASS** | `tests/core/test_architecture.py` 14 项测试全部通过（在 Python 3.14.6 与 Python 3.12.3 均 14/14 passed）；包含 P-01 新增的 shim 纯净性守卫与判别性负例测试。 |
| **I2-AC5** | 既有 UI/业务测试通过；任何 skip、环境阻塞或兼容例外明确记录。 | **PASS** | ① Workbench 全套 127 项 + Architecture 14 项 = 141 项测试全部 passed（`workbench-suite.log`）；<br>② Python 3.14 无 Qt 环境下跑 `tests/workbench/test_{region_canvas,projection}.py` + 架构守卫 38 passed, 2 skipped（`qtfree-suite.log`，2 skips 已归因）；<br>③ 全仓全套测试 1247 passed, 6 skipped, 1 failed（`full-suite.log`，6 skips 与 1 failure 已详细归因）。 |

---

## 5. 范围核验与空白审计（Scope & Whitespace Audit）

- **空白审计**：
  - `git diff --check 5d989bab6c5c8a24a5112303f95c2b8eea356bdc d9b718242b6516a2e9e5b3b36913ef2a63be4665`：**Exit Code 0**（零警告、零 trailing whitespace、零 EOF 换行问题）。
  - `git diff --check 5d4a4650943507ca4053376d6acea36f146c704a d9b718242b6516a2e9e5b3b36913ef2a63be4665`：**Exit Code 0**。
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

## 6. 证据文件清单

- [`verification/M2-I2/pre-migration-baseline.log`](../../verification/M2-I2/pre-migration-baseline.log)：修改前基线证据，记录 Git 状态、测试套件修前结果以及旧位置在无 Qt 环境导入失败的原始日志。
- [`verification/M2-I2/workbench-suite.log`](../../verification/M2-I2/workbench-suite.log)：Workbench 全套 127 项 + Architecture 14 项 = 141 项测试全绿原始日志（Exit Code 0）。
- [`verification/M2-I2/qtfree-suite.log`](../../verification/M2-I2/qtfree-suite.log)：Python 3.14.6 无 Qt 纯净环境下运行迁移模块与架构测试的原始日志（38 passed, 2 skipped, Exit Code 0，含 skip 归因）。
- [`verification/M2-I2/full-suite.log`](../../verification/M2-I2/full-suite.log)：全仓测试原始运行日志（1247 passed, 6 skipped, 1 failed, Exit Code 1，含 6 skips 与 1 failure 详细归因）。
- [`verification/M2-I2/post-migration-verification.log`](../../verification/M2-I2/post-migration-verification.log)：修改后综合验证探针与各测试命令聚合日志。
- [`verification/M2-I2/verify_m2_i2.py`](../../verification/M2-I2/verify_m2_i2.py)：综合验证探针脚本，覆盖 AC1~AC4 的可重复自动测试。
- [`verification/M2-I2/diff-check.log`](../../verification/M2-I2/diff-check.log)：空白检查（Exit Code 0）及对开工 HEAD、基线 Commit、Review HEAD 的 diff stat 记录。

---

## 7. 后续交接与下一步建议

按照《协作协议》（09_COLLABORATION.md §5.1）规范：
- 本 Task `M2-I2` 已在独立工作树 `G:/CODEX/New Manga.worktrees/M2-I2-antigravity` 完成代码、测试与证据的完整修订与固化。
- 推荐下一步：交由 **Codex** 进行独立非作者复审（Review of revised head）与集成验证（先集成 I2，再由 I1 reconcile）。
- 可直接转发给 Codex 的指令见最终回复。
