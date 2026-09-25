---
task_id: M2-I2
reviewer: Codex
author: Antigravity
base_commit: 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a
reviewed_head: 0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716
delivery_commit: e359da759d1160467f61ced7061cdfe09772232f
decision: approved
integration_commit: pending
---

# Review：M2-I2（R-003 / R-004 修订）

## 范围与依据

固定审查工作树 `G:/CODEX/New Manga.worktrees/M2-I2-antigravity`、分支 `agent/antigravity/M2-I2-qtfree-logic-extraction`，审查 Reviewed HEAD `0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716`；固定 Base `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`，Delivery `e359da759d1160467f61ced7061cdfe09772232f`，前次 Reviewed HEAD `a4705a9f473d0e8d9087068edc4bec572d90439a`。对照 M2-I2 AC1–AC5、`doc/09_COLLABORATION.md`、架构分层约束及前次 Review 中 R-003/R-004；独立 Standards 与 Spec 视角均已执行。

本轮修订范围为架构守卫测试与 Task/Handoff/验证证据；此前已审查的 Application 迁移代码仍保持在冻结的 M2-I2 边界内。未发现 Domain Contract、Schema、Ports、依赖或 M2-I1 独占 `src/bootstrap/**` 越界修改。

## Architecture

**通过。** `LEGACY_UI_SHIM_SEAMS` 为两个旧 shim 分别固定唯一对应的 `application.*` 来源；`find_shim_violations` 对 `__all__` 只接受 RHS 为静态 `ast.List` / `ast.Tuple` 且每个元素均为字符串常量。`test_legacy_ui_shims_contain_no_authoritative_logic` 检查真实 shim；负例覆盖本地定义、`ui.*` 导入、lambda 调用、变量名、推导式和非字符串元素，并以静态字符串元组作为正例。

## Verification

| 场景 | 命令或手工步骤 | 环境 / commit | 结果 | 证据 |
|---|---|---|---|---|
| 固定 HEAD / 范围 | 核对 branch、HEAD、clean 状态；`git diff --check 6a68fdeb..0d6acc7d` | 固定作者 worktree；Reviewed HEAD `0d6acc7d` | PASS | `verification/M2-I2/review-0d6acc7/review-scope.log` |
| R-003 shim 守卫 | 执行 pure-shim、local-definition、`ui.*` 与 dynamic-`__all__` 四项测试 | Python 3.12.3；集成候选树中的固定代码 | PASS：4 passed, 12 deselected，Exit 0 | `verification/M2-I2/integration-shim-guards.log` |
| Workbench + Architecture | `python -m pytest -v tests/workbench tests/core/test_architecture.py` | Python 3.12.3；集成候选树 | PASS：143 passed，Exit 0 | `verification/M2-I2/integration-workbench-architecture.log` |
| Qt-free | `python -m pytest -v -rs tests/workbench/test_projection.py tests/workbench/test_region_canvas.py tests/core/test_architecture.py` | Python 3.14.6，无 PySide6；集成候选树 | PASS：40 passed, 2 skipped，Exit 0；两个兼容重导出用例因缺少 PySide6 跳过 | `verification/M2-I2/integration-qtfree-suite.log` |
| 全仓 | `python -m pytest -v -rs` | Python 3.12.3；固定 Reviewed HEAD `0d6acc7d` | 1249 passed, 6 skipped, 1 failed，Exit 1，1256 collected；六个 skip 因 PATH 中无 openssl CLI（`shutil.which("openssl") is None`）；唯一 failure 为环境已安装 `torch` 导致的 `test_no_model_runtime_is_installed_in_this_environment` | `verification/M2-I2/full-suite.log` 与 `review-0d6acc7/full-suite-environment.log` |

全仓测试作者原始日志早于动态 `__all__` 新增测试，故其 1254 collected / 1247 passed 不能代表当前树。Codex 已在固定 Reviewed HEAD 独立重跑，当前日志记录 1256 collected / 1249 passed；旧日志作为 `full-suite-delivery-pre-rerun.log` 保留。全仓唯一失败与 skip 原因均有对应环境探针和逐项归因；受影响的 Workbench、Architecture 与 Qt-free 门禁通过。

## Standards / Spec 视角

- **Standards：通过。** 未发现违反 Task 范围、依赖方向、Legacy shim 非权威性或验证证据纪律的其他问题。
- **Spec：通过。** R-003 已以 AST 限制静态 `__all__` 并覆盖全部指定负例；R-004 在 Handoff 和全仓日志中准确说明 PATH 中无 openssl 命令行可执行文件及 `shutil.which` 返回 `None`。Task 与 Handoff 的状态为 `in_review`，Delivery SHA 完整。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-003 | P1 | `tests/core/test_architecture.py` `find_shim_violations` | 动态 `__all__` RHS 可绕过 Legacy shim 纯重导出守卫 | lambda 调用、变量名、推导式与非字符串元素负例均被拒绝；静态字符串 tuple 被允许 | 限定为静态字符串 list/tuple | fixed：`0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716` |
| R-004 | P2 | `doc/handoffs/M2-I2-delivery.md`、`verification/M2-I2/full-suite.log` | OpenSSL skip 原因需准确指向系统 CLI/PATH 检测 | 日志说明 `shutil.which("openssl") is None`，并列出 6 个 skip 位置 | 使用 CLI/PATH 术语，避免描述成 Python 模块缺失 | fixed：`0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716` |
| R-005 | P1 | `verification/M2-I2/full-suite.log` | 原作者全仓日志运行过早，未收录最新架构负例 | 固定 HEAD 独立复跑 1256 项；新测试纳入且结果记录完整 | 刷新当前日志及 Task/Handoff 统计，保留旧日志作为历史证据 | fixed：本次 Codex 独立复跑，证据随集成提交入库 |

在上述记录范围内未发现未解决问题。Architecture 与 Spec 均通过；Verification 中全仓命令如实记录一个已归因的环境 failure，M2-I2 受影响测试门禁通过。

## 结论与复审

**批准集成。** 固定 Reviewed HEAD `0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716` 可集成至 `master`。集成后 Workbench + Architecture、Qt-free 与指定 shim 守卫测试已在集成候选树复跑通过。集成 commit 待写入完成 Task 状态的后续提交；本 Review 不替代集成 commit 记录。
