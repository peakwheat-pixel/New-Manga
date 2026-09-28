---
task_id: M2-I2
reviewer: Codex
decision: changes_requested
base_commit: 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a
opening_head: 5d989bab6c5c8a24a5112303f95c2b8eea356bdc
prior_reviewed_head: 86ecb94b7f2acd356923d5408c80ac81d942fd03
product_delivery: be5e8d830fba2f9ca1b0cd79148cc386c4468061
reviewed_head: a4705a9f473d0e8d9087068edc4bec572d90439a
integration_commit: null
---

# M2-I2 — Codex 独立再审（2026-09-25）

## 决定

**CHANGES_REQUESTED。不得进入 Integration Gate；integration_commit 仍为 null。**

两个业务实现已迁至 Application，当前 Legacy shim 与消费方方向正确，所要求的行为对照也通过。但 AC4 的 shim guard 仍接受可执行的动态 __all__ 表达式；Handoff 的 OpenSSL 说明错误，且随最终代码交付的全仓日志少记一个新架构测试。发现 R-003、R-004、R-005 尚未关闭。本轮没有集成或修改作者产品代码。

主线已有同一 head 的 Review [M2-I2-a4705a9.md](M2-I2-a4705a9.md)；本报告是独立复核，未覆盖或改写该记录。

## 固定对象与范围

固定对象、完整起始核验、name-status 与 diff-check 命令及结果记录在 [review-scope.log](../../verification/M2-I2/review-a4705a9/review-scope.log)。

- 作者 worktree：G:/CODEX/New Manga.worktrees/M2-I2-antigravity；branch 为 agent/antigravity/M2-I2-qtfree-logic-extraction；HEAD 为 a4705a9f473d0e8d9087068edc4bec572d90439a；开始时 clean。指定 base 是 Handoff head 的祖先。
- 固定 Product Delivery 为 be5e8d830fba2f9ca1b0cd79148cc386c4468061；固定 Handoff head 为 a4705a9f473d0e8d9087068edc4bec572d90439a。Delivery 到 Handoff head 没有 src 或 tests 变更。
- 复核结束前再次检查时，作者分支仍为 `agent/antigravity/M2-I2-qtfree-logic-extraction` 且 worktree clean，但 HEAD 已推进至 `0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716`（提交标题：`docs(handoff): deliver revised M2-I2 evidence, static __all__ guard, and CLI skip attribution`）。本报告、所有测试与 finding 均固定于用户指定的 `a4705a9f473d0e8d9087068edc4bec572d90439a`；新 HEAD 未检查、不属于本次决定范围，需以新固定对象重新 Review。最终漂移核验记录见 review-scope.log。
- base..Delivery 名称差异包含 58fa0df/5d989ba 的 Codex M2 释放和开工前治理文档；以记录的 opening_head 5d989bab6c5c8a24a5112303f95c2b8eea356bdc 为界审查作者增量，产品源代码、允许的消费者、测试、Task、Handoff、verification 均在冻结范围。
- 没有 src/bootstrap、src/domain、Domain Contract、Schema、ports、依赖、packaging、React/Tauri/IPC 或其他 Agent 产品代码改动。M2-I1 仍未集成。
- git diff --check base..Handoff head：exit 0。

## 上轮与同 head finding disposition

| Finding | 来源 / 严重度 | 当前 disposition |
|---|---|---|
| R-001 | 86ecb94 Review / P1 | **PARTIAL**：六个 skip 与 torch failure 的测试路径已修正；全仓日志统计仍过时（见 R-005），skip 机制说明仍错误（见 R-004）。 |
| R-002 | 86ecb94 Review / P2 | **RESOLVED**：shim guard 已按文件限定到各自 application seam；持久化 ui.* 来源负例存在并通过；本 Review 的 Negative A/B 也检出倒流。 |
| R-003 | 同 head Review / P2 | **OPEN**：动态 __all__ 表达式仍未被纯 shim guard 拦截；本 Review 在安全临时文件中独立复现。 |
| R-004 | 同 head Review / P2 | **OPEN**：Handoff 把缺少 openssl 命令误写为缺少 Python OpenSSL 模块；运行时显示 Python SSL 使用 OpenSSL 3.0.13。 |
| R-005 | 本 Review / MAJOR | **OPEN**：固定 head 上全仓新跑收集 1255 项；交付日志仍记 1254 项，并缺少新增的 UI 导入负例测试。 |

## Architecture 与行为等价

### 依赖方向与兼容性

- src/application/tasks/projection.py 与 src/application/editing/region_canvas.py 分别从 domain.tasks.models、domain.regions.entities 导入；未导入 PySide6、src.ui 或 src.infrastructure。
- 两个旧 UI 文件仅从其各自 application seam 重导出；PageListModel、Workbench ViewModel 与任务 package initializer 改从 application seam 消费。架构测试通过。
- Python 3.14.6 无 PySide6 环境成功导入并运行两个 application 模块；Python 3.12.3 Workbench 套件中的两个兼容性 re-export 测试均通过。

### Projection 与 Region Canvas

Reviewer probe 从固定 base 用 git show 读取旧 UI 实现。移除模块文档字符串后，两个迁移前后 AST 均完全一致；不是拿新 Application 实现和其自身 shim 互比。

[semantic-probe.py](../../verification/M2-I2/review-a4705a9/semantic-probe.py) 及 [semantic-probe.log](../../verification/M2-I2/review-a4705a9/semantic-probe.log) 记录：

- Projection：5 个完整 PipelineRun 场景的 TaskProjection 字段相等；对 64 种页面状态集合逐项比较；遍历全部 PipelineRunStatus 和 has_failures 组合比较按钮映射。明确优先级断言通过：failed > processing > blocked > completed > skipped > waiting。场景覆盖 overall_progress、current_page_id、current_step_type、step_flow、pause/stop/continue/restart/abandon/retry_failed。
- Region Canvas：14 组有效几何与错误路径迁移前后输出一致，包含 2 点矩形、3+ 点 polygon、normalized 坐标、超界 clamp、zero-area、collinear、invalid page size、too few points 与 RegionCanvasError 的 type/code/detail/message。半像素 tie 实测输出 13、63，符合 floor(n * size + 0.5)，没有 Python round() 退化。
- 用户要求的判别负例：临时 application/tasks/projection.py 加入 from ui.models.tasks.projection import ...，guard 报告 forbidden import；临时复制 application seam 并加入 import PySide6，guard 报告 forbidden import。两项均未触碰正式产品文件。

### Architecture guard 尚存缺口

负例 C 的变体也在临时目录检查：shim 仅允许 import application.tasks.projection，但把 __all__ RHS 改成 __all__ = (lambda: ["TaskProjection"])()。当前 tests/core/test_architecture.py 的 find_shim_violations 只检查 Assign 的 target 是否为 __all__，不检查 RHS；结果是 Guard violations: []。这说明现在的 guard 可以抓住本地 FunctionDef/ClassDef 与错误 import source，但还不能保证所有接受的 shim 语句是静态 re-export。详见 R-003。

## 测试记录

所有命令在固定 Handoff head 的独立 Review worktree 中运行；完整 stdout 与命令头均保存于新增 verification 证据。

| Command | Shell | Python / Environment | Collected | Passed | Failed | Skipped | Exit |
|---|---|---|---:|---:|---:|---:|---:|
| python -m pytest -q tests/workbench tests/core/test_architecture.py | Windows PowerShell 7.6.6 | Python 3.12.3；Windows 11 build 26200；pytest 9.1.1 / anyio 4.15.1；PySide6 available | 142 | 142 | 0 | 0 | 0 |
| python -m pytest -v -rs tests/workbench/test_projection.py tests/workbench/test_region_canvas.py tests/core/test_architecture.py | Windows PowerShell 7.6.6 | Python 3.14.6；Windows；PySide6 absent | 41 | 39 | 0 | 2 | 0 |
| python -m pytest -v -rs | Windows PowerShell 7.6.6 | Python 3.12.3；Windows 11 build 26200；pytest 9.1.1；ssl.OPENSSL_VERSION=OpenSSL 3.0.13；openssl CLI absent；torch present | 1255 | 1248 | 1 | 6 | 1 |

- Focused Workbench + architecture 完整输出：[focused-workbench-architecture.log](../../verification/M2-I2/review-a4705a9/focused-workbench-architecture.log)。
- 无 Qt 套件输出：[qtfree-suite.log](../../verification/M2-I2/review-a4705a9/qtfree-suite.log)。
- 本 Review 全仓重跑输出：[full-suite.log](../../verification/M2-I2/review-a4705a9/full-suite.log)。
- semantic 与 Negative A/B/C probe 的命令、Python、Environment、结果和 Exit code：[semantic-probe.log](../../verification/M2-I2/review-a4705a9/semantic-probe.log)。

### Full suite failure

失败仍存在：tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment，在 tests/providers/test_registry_readiness.py:193 因 torch 可发现而失败。当前 Python 解释器报告 torch_spec 位于 G:/CODEX/New Manga.task-envs/T3.2.1-packaging-py312/Lib/site-packages/torch；同一测试文件在 base..Delivery 无改动，测试也不引用迁移的 UI seam。此项是现有环境与测试断言不匹配，pre-existing、environment-dependent、与 M2-I2 无关；不得把 exit 1 记成全套通过。

### Full suite 六项 skip 逐条归因

| Test | Skip reason | Pre-existing? | Environment-dependent? | M2-I2-related? | Disposition |
|---|---|---|---|---|---|
| tests/network/test_connection_tester.py::test_tls_stage_fails_typed_for_untrusted_cert (line 106) | 测试原因文本为 openssl unavailable；tests/network/test_connection_tester.py:24-25 用 shutil.which("openssl") 检查 openssl 可执行文件；当前为 None | Yes：测试/marker 未变 | Yes：PATH 中无 openssl CLI | No | 环境 skip 合法；Handoff 对模块的解释错误，见 R-004 |
| tests/network/test_transport_tls.py::test_verified_tls_direct (line 39) | 同上：缺 openssl CLI | Yes | Yes | No | 同上 |
| tests/network/test_transport_tls.py::test_verified_tls_through_connect_tunnel (line 47) | 同上：缺 openssl CLI | Yes | Yes | No | 同上 |
| tests/network/test_transport_tls.py::test_untrusted_cert_fails_typed (line 62) | 同上：缺 openssl CLI | Yes | Yes | No | 同上 |
| tests/network/test_transport_tls.py::test_untrusted_through_tunnel_fails_typed (line 69) | 同上：缺 openssl CLI | Yes | Yes | No | 同上 |
| tests/network/test_transport_tls.py::test_verify_tls_false_allows_untrusted (line 83) | 同上：缺 openssl CLI | Yes | Yes | No | 同上 |

Python 3.14 无 Qt 套件的另外两个 skip 是 tests/workbench/test_projection.py::test_backward_compatibility_reexports 与 tests/workbench/test_region_canvas.py::test_backward_compatibility_reexports：当前环境没有 PySide6，Legacy UI package __init__ 导入 Qt 依赖而跳过 shim 兼容测试。它们在 Python 3.12 Workbench 套件通过；不是上述六项全仓网络 skip。

## Findings

### R-003 — MAJOR：动态 __all__ 绕过纯 shim guard

- **Path / Line**：tests/core/test_architecture.py:139-151，find_shim_violations。
- **Reproduction**：在临时 shim 加入允许的 application 导入和 __all__ = (lambda: ["TaskProjection"])()；运行 guard 得到空违规列表，见 semantic-probe.log。
- **Expected**：纯 shim 的导出声明只接受静态字符串列表/元组，不允许导入时执行任意表达式；动态表达式 mutant 应失败。
- **Actual**：只检查赋值 target 为 __all__ 就放行 RHS。
- **Minimal correction boundary**：把 __all__ RHS 限制为元素全为字符串常量的静态 list/tuple；添加动态 RHS 负例。无需改 application 规则或消费者。
- **Re-review requirement**：重跑 tests/core/test_architecture.py 与新的动态 RHS negative probe；确认真实两个 shim 和 Legacy import 兼容测试仍通过。

### R-004 — MINOR：skip 环境解释仍然不准确

- **Path / Line**：doc/handoffs/M2-I2-delivery.md:52-57。
- **Reproduction**：Handoff 写“本地测试环境无 OpenSSL 模块”；同一 reviewer Python 输出 ssl.OPENSSL_VERSION 为 OpenSSL 3.0.13，shutil.which("openssl") 为 None。tests/network/test_connection_tester.py:24-25、tests/network/test_transport_tls.py:22-23 检测的是 CLI。
- **Expected**：说明缺少 PATH 中的 openssl 可执行文件；区分 Python ssl 模块存在与否。
- **Actual**：错误称 Python OpenSSL 模块缺失。
- **Minimal correction boundary**：更正 Handoff 六项 skip 说明，不改网络产品代码。
- **Re-review requirement**：核对新 Handoff 与 pytest -rs 的六项节点和 skip reason 一致。

### R-005 — MAJOR：全仓测试日志未覆盖最终架构测试集

- **Path / Line**：verification/M2-I2/full-suite.log:15, 1302；doc/handoffs/M2-I2-delivery.md:50, 90, 125；新增测试 tests/core/test_architecture.py:327-340。
- **Reproduction**：交付日志写 collected 1254 / 1247 passed，并只列 14 个 architecture tests；固定 head 当前 architecture suite 有 15 项，含 test_reversal_guard_reports_ui_imports_in_legacy_shims。复跑相同 Python 3.12.3、pytest 9.1.1 命令得到 1255 collected / 1248 passed / 6 skipped / 1 failed，exit 1，详见本 Review 的 full-suite.log。
- **Expected**：完整测试证据与固定 Product Delivery 的测试树一致，计数、失败、skip 均来自最终代码运行。
- **Actual**：Handoff/full-suite.log 少记一个已交付 guard test，counts 与固定 head 不匹配。
- **Minimal correction boundary**：在最终 Delivery tree 重跑完整套件，更新作者 full-suite.log 与 Handoff 数字；保留 torch failure 和六项 skip 为非通过结果，并精确写明 CLI 环境原因。
- **Re-review requirement**：复核新增日志的 Shell/Python/Environment/Collected/Passed/Failed/Skipped/Exit code，确认 architecture test 清单含新增 UI-import mutant。

## Standards / Spec 视角

### Standards — executed

对照 AGENTS.md、doc/09_COLLABORATION.md §4/§6、doc/02_TECHNICAL_ARCHITECTURE_.md 架构方向与 §16、M2-I2 冻结范围检查。按固定 opening_head 到 Reviewed head 的作者增量，代码/测试范围符合 Task；架构依赖方向也符合记录标准。R-003 是 AC4 guard 覆盖缺口，不是当前 Application 实现倒依赖 UI。可选清理项：tests/core/test_architecture.py:27 的 LEGACY_UI_SHIMS 定义目前无引用，属于低影响的 Dead Code heuristic，不是 gate finding。

### Spec — executed

- AC1：旧源与迁移源 AST 一致；Reviewer 的真实旧实现对照通过。
- AC2：application seam 是权威实现，Legacy consumer 经 application；通过。
- AC3：新模块无 PySide6、UI、Infrastructure 导入；无 Qt 环境直接运行通过。
- AC4：当前两个 shim 是正确 re-export，Negative A/B 检出；动态 __all__ mutant 未检出，故部分满足，R-003 open。
- AC5：Workbench + architecture 142 passed；无 Qt 运行 39 passed / 2 skipped；全仓重跑 1248 passed / 6 skipped / 1 failed。failure 经环境证据确认与 M2-I2 无关，但作者日志过时且 Handoff skip 原因错误，R-004/R-005 open。


## Architecture / Verification 结论

- **Architecture**：当前业务代码 PASS；Application → Domain、Legacy adapter → Application。长期 shim guard 因 R-003 为 PARTIAL。
- **Verification**：Workbench + architecture PASS 142/142；no-Qt PASS 39/39，另有 2 个因无 PySide6 的兼容性测试 skip；full suite 为 1248 passed、6 skipped、1 failed，exit 1。失败本身经证据确认是既有 torch 环境断言；作者 full-suite artifact 仍不覆盖最终测试树。
- **未运行**：集成验证、M2-I1 reconcile 或任何 M2-C1/React/Tauri 工作。

## 停止点

R-003、R-004、R-005 修订并经新的固定 Handoff head 复审前，M2-I2 保持 changes_requested、integration_commit=null。作者分支现 HEAD `0d6acc7d985a0a96f5a27c2f25b7b2afcd66e716` 尚未审查；本报告不对其内容作结论。此 Review 不授权集成、M2-I1 重定基线、M2-C1、React 或 Tauri。


