---
task_id: TASK-052
reviewer: 独立子对话 Reviewer（ZCode 窗口，非本切片实现作者）
author: ZCode
base_commit: 667024c（切片起点 in_progress；Task 元数据 base 8bf8da3 系开立基线）
reviewed_head: c0d1fd0
decision: approved_subagent
---

# Review：TASK-052（命令失败可见化，§11 P-4，最小可见 + provisional）

独立 Reviewer 依据仓库事实（代码、测试、Task、Handoff、verification 日志、复跑）对
`git diff 667024c..c0d1fd0` 做验收审查。实现提交 `3afaade`，handoff 提交 `c0d1fd0`。
**结论：approved_subagent** —— 无 P0/P1；1 项 P2（Handoff AC④ 证据措辞高估，要求集成前勘误）+ 3 项 P3。
准予交 Codex 集成，P2 勘误作为集成前置小改（不改变代码与测试）。

## 范围与依据

- Task：`doc/tasks/TASK-052.md`（AC ①～⑦、允许/禁止范围、provisional 定位）。
- Handoff：`doc/handoffs/TASK-052-3afaade.md`（其结论全部自行验证，未直接采信）。
- diff：`git diff 667024c..c0d1fd0`（13 个文件：viewmodel.py、WorkbenchView.qml、
  tests/workbench 两文件、Task/Handoff、verification 7 个日志）。
- 未审到部分：QML 运行时视觉呈现（无截图人工验收；以契约测试 + provisional 定位覆盖）；
  Windows 真实用户会话中的剪贴板行为（测试为 metaObject 直调，见 R-004）。

## 白名单核对（PASS）

- diff 文件清单逐一对照 Task「允许修改范围」：全部落在
  `src/ui/viewmodels/workbench/**`、`src/ui/qml/workbench/**`（仅工作台页面）、
  `tests/workbench/**`、Task/Handoff/`verification/TASK-052/**` 内。
- 未触碰：reader/bookshelf 等其他页面 QML（零改动）、Schema/migration、`requirements.txt`、
  `AGENTS.md`、其他 Task、`doc/STATUS.md`（台账行按 Task/Handoff 声明留待 review 后，
  属 AC⑦ 待闭环项，非违规）。
- 禁止项扫描：diff 中无 skip/xfail 标记、无 QDialog/Popup 等阻塞弹窗、
  `tests/` 被删除行仅文件头（**既有断言零删改**）；`tests/workbench/test_qml_workbench.py`
  的 diff 为纯新增（+38 行，仅 `test_command_error_bar_visible_only_when_a_failure_is_held` 一例）。
- Task 文件自身 diff 仅 AC 勾选、测试表 NOT_RUN→结果回填、交付记录更新，无范围/AC 语义篡改。

## 代码审读（Architecture，PASS）

### VM sink（`src/ui/viewmodels/workbench/viewmodel.py`）

- 单一 sink `_record_command_error`（viewmodel.py:817-839）：修前 12 处
  `commandError.emit` 逐条对照修后，grep `commandError.emit` 仅剩 sink 内 1 处（viewmodel.py:838）。
  12 处替换 = 5 字符串 guard（editor/selection×3/run）+ 6 处 `except PipelineError` 对象 +
  1 处 `_on_run_crashed`，与 Handoff 清单一致，**无遗漏**。
- **语义无漂移（bare signal 逐字节兼容）**：字符串分支 emit `str(error)` 原文；对象分支
  `detail or str(error)` 与修前 `error.detail or error.code` 等价——已核实
  `PipelineError`（`src/domain/tasks/models.py:150-156`）`detail` 默认 `""` 且 `__str__`
  在 detail 空时返回 `code`，仓库全部构造点均为 `(code, detail)` 双参，两式在所有形态下载荷相同；
  worker crash 载荷为 str（`run_controller.py:129`，Signal(str,str)），原样透传。
- 新增面：`commandErrorChanged` 信号、`commandErrorText` Property（notify）、
  `clearCommandError()`（幂等：空态再清不发 notify，viewmodel.py:452-458）。emit 路径集中，AC① 达成。
- PROVISIONAL 注释在 sink docstring（viewmodel.py:820-826）与 QML 处同义标注，AC⑤ 达成。

### QML 状态条（`src/ui/qml/workbench/WorkbenchView.qml`）

- `commandErrorBar`（Rectangle）位于工具栏下方、主 RowLayout 之前，工作台页面内；非阻塞（无弹窗）。
- objectName 四件套齐全：`commandErrorBar` / `commandErrorText`（Label，elide）/
  `commandErrorCopyButton` / `commandErrorCloseButton`。
- visible 绑定链成立：`workbench.wCommandError`（根 property ← `vm.commandErrorText`，
  Property notify=commandErrorChanged）→ `bar.visible !== ""` 判空；
  `Layout.preferredHeight: visible ? 32 : 0` 隐藏时不占布局。链路经 QML 契约用例实证
  （idle 不可见 → 真实 selection guard 失败后可见且文本正确 → 关闭后不可见且 VM 清空）。
- 复制实现：隐藏 `TextEdit`（visible:false, 0×0）+ `selectAll()+copy()`。`copy()` 为方法调用
  不需要焦点；测试 helper `click_button` 经 metaObject 直调 `clicked()`（test_qml_workbench.py:53-57），
  无焦点副作用；覆盖用户剪贴板为功能本意。AC②③ 达成。

### AC④ 证据强度核查（见 R-001）

- 无 Region / 无 Page：经 `startRegionCommand` / `startTranslateSelected` 真实入口 guard。实证充分。
- worker crash：直调 `_on_run_crashed`（runCrashed 的真实接收器，viewmodel.py:116 连接），
  Handoff 表述（"真实接收器"）未夸大。
- 无 provider 绑定：测试**直接构造 `PipelineError` 对象调 sink**，非端到端。文本
  `"no provider binding configured for step 'ocr'"` 与生产 `handlers._chain`
  （`src/infrastructure/providers/handlers.py:914`）逐字节一致；但生产抛出的类型是
  `ProviderNotConfigured`（`src/ports/providers/errors.py:59-62`，`ProviderError(RuntimeError)`
  子类，**非 PipelineError**，且无 `.code` 实例属性）。Handoff "真实错误类型" 声明不成立 → R-001。
- 已知边界核实：`ProviderNotConfigured` 在 handler 层被转 `StepExecutionError`
  （handlers.py:209-218），service.py:790-795 捕获后 `_fail_step` 终止于 run 内部，
  run 终态 `completed_with_failures` 为真实状态值（`src/domain/tasks/models.py:96`，
  service.py:977 设置），不经 VM commandError。**Handoff「已知边界」登记如实**。

## Standards（已执行，硬性项无违规）

- 分层：QML 无业务逻辑（状态条仅绑定 VM property + 调 Slot），符合 D05 §60 口径与
  WorkbenchView 既有的 `w*` 别名模式；VM 不触 UI 组件。
- 契约兼容：既有 `commandError` 信号载荷逐字节不变（见上），既有断言零改动。
- 本 Task 允许/禁止范围：全部合规（见白名单核对）。
- baseline smell：未命中需报告项（sink 收口本身消除 12 处重复，属改善）。

## Spec（已执行）

- AC ①②③⑤：达成（证据见上）。AC④：实质达成，provider 绑定用例的证据措辞需勘误（R-001）。
- AC⑥：达成——判别力经 Reviewer 在修前树实证（4 failed / exit 1，含 QML 契约用例）；
  定向 216 / 全仓 899 复跑一致；修前基线全仓 895 实测（899 = 895 + 4 新用例成立，passed 不减少）；
  ×5 日志齐备。AC⑦：Handoff/证据/本 Review 齐；集成与 STATUS 台账行留待 Codex（Task 声明的后续步骤）。
- 无 scope creep；无"来源要求但缺失"项。
- 观察项：AC④ 原文"成功后不可见"由用例 idle 态断言覆盖（无动态成功命令后的二次断言），
  可接受的最低实现（R-004 一并记录，不要求整改）。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| R-001 | P2 | `doc/handoffs/TASK-052-3afaade.md:46`；`tests/workbench/test_command_error_surface.py:46-52` | Handoff AC④ 称 provider 绑定用例使用"生产 `_chain` 的**真实错误类型**与真实文本（`PipelineError("PROVIDER_NOT_CONFIGURED", …)`）"。事实：生产 `_chain` 抛 `ProviderNotConfigured`（handlers.py:911-915），其为 `ProviderError(RuntimeError)` 子类、**非 PipelineError**，且无 `.code` 实例属性（仅类属性 `error_code`）；真实对象若走 sink，`getattr(error,"code","")` 落空将退化为类名（`[command/ProviderNotConfigured]`），与测试断言的 `[command/PROVIDER_NOT_CONFIGURED]` 不同。文本真实、类型冒充，证据强度被高估。缓解：该异常经 handlers.py:209-218 → service.py:790-795 终止于 run 内部（completed_with_failures），当前架构不达 sink，Handoff「已知边界」已如实登记，运行时行为不受影响 | 本审查"AC④ 证据强度核查"节；`src/ports/providers/errors.py:27-43,59-62`；`src/domain/tasks/models.py:150-156` | 集成前由作者在 Handoff AC④ 追加一行勘误：降格为"真实错误文本 + 等价形态 PipelineError 构造；生产异常类型为 ProviderNotConfigured 且按已知边界不经 commandError"。不改代码与测试 | open |
| R-002 | P3 | `verification/TASK-052/discriminating-new-tests-vs-prefix.log` | 判别力日志截断：仅 2/3 条 FAILED 行 + 计数行（缺 `test_selection_failures…` 行与 summary 头），未记录 exit code；QML 契约用例未在修前树跑，Handoff 关于其判别力（"commandErrorBar 不存在而无法通过"）为推理而非实证 | Reviewer 补跑实证（修前 src `667024c` + 修后 tests）：**4 failed / exit 1**——3 个 VM 用例 AttributeError（`commandErrorText`/`_record_command_error` 不存在），QML 用例 `findChild("commandErrorBar")` 为 None，Handoff 推理成立 | 以 `verification/TASK-052/review-discriminating-vs-prefix.log`（Reviewer 补跑）为准，作者无需重做 | fixed（by review） |
| R-003 | P3 | `verification/TASK-052/targeted-workbench-uishell-reading.log`、`full-suite-post-fix-run{1..5}.log` | 各日志均为尾部 2 行截断式记录，"≥5 次逐次记录"的可追溯性弱（无法从日志复核环境变量、警告明细）；关键计数（216 / 899×5）经 Reviewer 完整复跑全部吻合 | `verification/TASK-052/review-rerun-targeted.log`、`review-rerun-full.log`（Reviewer 完整输出） | 后续切片的 verification 日志保留完整输出 | deferred |
| R-004 | P3 | `tests/workbench/test_qml_workbench.py:262-286` | 观察项：①"成功后不可见"以 idle 初始态断言覆盖，无动态成功命令后的二次断言；②复制按钮验证为"动作可执行"弱断言（metaObject 直调，未断言剪贴板内容）。Handoff 表述（"复制动作可执行"）与证据强度相符，无夸大，不构成 AC 违规 | 用例源码；helper `click_button`（test_qml_workbench.py:53-57） | TASK-047 设计收敛切片可顺带补剪贴板内容断言 | deferred |

## 验证（全部实际执行；环境：PowerShell + `TASK-012-py312` venv，不设 `QT_QPA_PLATFORM`，目录形式跑）

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 定向三目录复跑 | `python -m pytest tests/workbench tests/ui_shell tests/reading_export -q -rs -p no:cacheprovider` | c0d1fd0 | **PASS**：216 passed / 0 skipped / **exit 0** | `verification/TASK-052/review-rerun-targeted.log` |
| 全仓复跑 | `python -m pytest -q -rs -p no:cacheprovider` | c0d1fd0 | **PASS**：899 passed / 0 skipped / 1 warning（mobi 库 imghdr 弃用，环境性非本切片引入）/ **exit 0** | `verification/TASK-052/review-rerun-full.log` |
| 判别力实证（修前 src + 修后 tests） | `git checkout 667024c -- src/` 后 `-k command_error`，跑毕恢复 | src=667024c / tests=c0d1fd0 | **PASS**（判别力成立）：4 failed / **exit 1**（3 VM + 1 QML） | `verification/TASK-052/review-discriminating-vs-prefix.log` |
| 修前全仓基线 | `git checkout 667024c -- src tests`、移除新测试文件后全仓，跑毕恢复 | 667024c | **PASS**：895 passed / **exit 0**（899 = 895 + 4 成立，passed 不减少） | `verification/TASK-052/review-baseline-prefix.log` |
| 实现者 ×5 全仓日志核对 | 逐个 tail `full-suite-post-fix-run{1..5}.log` | c0d1fd0 | PASS：均 899 passed（run1-5 计数一致） | 同目录 5 个日志 |
| 工作区恢复核对 | 每次 checkout 实验后 `git status` | c0d1fd0 | PASS：src/tests 无残留修改，仅余 Reviewer 新增 4 个日志（未跟踪，未提交） | 本文件交付时工作区状态 |

实现者声称的定向 216、全仓 899×5、修前判别力失败均与实测一致；Handoff 唯一不符项为 R-001 的类型措辞。

## 结论与复审

**decision: approved_subagent** —— 固定 head `c0d1fd0` 可交 Codex 集成。

理由：白名单完全合规、既有契约断言零改动、12 处 emit 收口语义无漂移（bare signal 逐字节兼容
已经代码级核实）、QML 状态条非阻塞且 objectName 寻址完整、判别力在修前树实证（4 failed / exit 1）、
定向 216 / 全仓 899（基线 895 + 4）复跑全绿、已知边界（typed step 失败不经 commandError，
终止于 completed_with_failures）与代码事实一致且已如实登记。

剩余风险与前置：

1. **R-001（P2）集成前勘误**：Handoff AC④"真实错误类型"须降格为"真实错误文本 + 等价形态构造"
   （不改代码/测试）。若后续设计切片把 provider 失败面接入 commandError sink，须先处理
   `ProviderError` 家族无 `.code` 导致的码退化（类名替代稳定码）。
2. provisional 呈现（颜色/文案/位置/单条历史）待 TASK-047 设计收敛，Task 已声明。
3. STATUS 台账行与集成验证由 Codex 在集成时补（AC⑦ 后半，Task 声明的后续步骤）。

复审规则：若作者就 R-001 追加勘误提交，Codex 核对勘误内容与本文件 R-001 建议一致即可集成，
无需重开 Review；其余 findings 已 disposition（R-002 fixed by review，R-003/R-004 deferred）。
