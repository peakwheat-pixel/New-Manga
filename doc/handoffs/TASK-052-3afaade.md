# Handoff — TASK-052 命令失败可见化（§11 P-4；最小可见 + provisional）

- 分支 head：见 Task 元数据（实现提交 `3afaade`；base 侧 `667024c` = in_progress + master 6cb1af3）
- worktree：`G:/CODEX/New Manga.worktrees/TASK-052-zcode`
- Review 材料：`git diff 667024c..3afaade` + 本文件 + `verification/TASK-052/**`

> **PROVISIONAL 声明（AC⑤）**：本切片是**最小可见**实现——一个状态条（文本 + 复制 + 关闭），满足"失败对用户可见且可复制"。视觉语言、信息层级、历史错误列表、错误分组等呈现设计**归 TASK-047（Qoder 设计门）及其后的设计切片收敛**；源码中 `_record_command_error` 与 `commandErrorBar` 处均有同义注释。

## 实施范围（对 Task 白名单）

| 文件 | 变更 |
|---|---|
| `src/ui/viewmodels/workbench/viewmodel.py` | + `commandErrorChanged` 信号、`_command_error_text` 状态、`commandErrorText` Property（notify）、`clearCommandError()` Slot、**单一 sink** `_record_command_error(error, *, stage)`；原 12 处 `commandError.emit(...)` 全部改走 sink（5 处字符串 guard + 6 处 PipelineError 对象 + 1 处 worker crash） |
| `src/ui/qml/workbench/WorkbenchView.qml` | + `wCommandError` 别名；工作台页面内新增最小状态条 `commandErrorBar`（`commandErrorText` Label + `commandErrorCopyButton` + `commandErrorCloseButton`，非阻塞） |
| `tests/workbench/test_command_error_surface.py`（新） | VM 3 用例（selection/对象分支/worker crash） |
| `tests/workbench/test_qml_workbench.py` | + QML 契约用例 1 条（bar 可见性状态机 + 复制 + 关闭） |

白名单核对：仅工作台页面 QML（reader/bookshelf 零改动）、无 Schema/requirements/AGENTS 改动。**既有断言零改动**：`commandError` 信号保持发**裸 detail**（既有用例 `errors == ["未选择任何 Page"]` 等逐字节不变），诊断前缀只进 `commandErrorText` 状态。

## 机制（AC①：emit 路径集中）

`_record_command_error` 是唯一出口：

```python
text = f"[{stage}/{code}] {detail}"   # BaseException：code 取 error.code 或类名
self._command_error_text = text
self.commandError.emit(detail)        # 既有信号：裸 detail（兼容面不变）
self.commandErrorChanged.emit()       # 驱动 commandErrorText / QML 状态条
```

stage 取值如实描述失败面：`selection`（guard 类）/ `command`（PipelineError 对象）/ `run`（重复启动）/ `editor` / `worker`（runCrashed）。

## AC 逐条

### AC ① VM 状态 — 达成
`commandErrorText`（Property + `commandErrorChanged` notify）+ `clearCommandError()`；12 处 emit 全部收口单一 sink（提交 diff 可数：`self.commandError.emit(` 仅剩 sink 内 1 处）。

### AC ② QML 最小消费者 — 达成
`src/ui/qml/workbench/WorkbenchView.qml`：`commandErrorBar`（objectName 寻址）位于工具栏下方，`visible: wCommandError !== ""`，含错误文本、"复制"、"×"关闭；非阻塞（无弹窗）。reader/bookshelf QML 零改动。

### AC ③ 可诊断性 — 达成
状态文本携带 `[stage/错误码] detail`（例：`[command/PROVIDER_NOT_CONFIGURED] no provider binding configured for step 'ocr'`），复制按钮一键复制全文（QML TextEdit copy()）。

### AC ④ 断言（三类真实失败 + QML 契约）— 达成
- 无 Region / 无 Page：`startRegionCommand("ocr_region")` / `startTranslateSelected()` 真实入口 guard → 状态可见、可清空；
- 无 provider 绑定：**生产错误文本 + 等价形态构造**——用例以 `PipelineError("PROVIDER_NOT_CONFIGURED", "no provider binding configured for step 'ocr'")` 走 sink 对象分支，文本与生产 `_chain` 逐字一致。**勘误（R-001，Review 指出）**：生产该场景实际抛 `ProviderNotConfigured`（`ProviderError` 子类，非 `PipelineError`、无 `.code` 实例属性），且该异常经 handler→service 终止于 run 内部（`completed_with_failures`，真实终态），**不经 commandError/sink**（见「已知边界」）——用例覆盖的是 sink 对象分支与真实文本，非该异常的真实抛出路径；
- worker 崩溃：`_on_run_crashed`（RunController.runCrashed 的真实接收器）→ `[worker] ...`；
- QML 契约：`test_command_error_bar_visible_only_when_a_failure_is_held`——空闲不可见 → 真实 VM 失败后可见且文本正确 → 复制动作可执行 → 关闭后不可见且 VM 状态清空（机器可验证）。

### AC ⑤ provisional 声明 — 达成
见文首；`viewmodel.py` sink docstring 与 QML 注释均标注。

### AC ⑥ 不回归 + 判别力 — 达成
- **判别力（修前 detached 树 `667024c`）**：新 VM 用例 **3 failed / exit 1**（`commandErrorText` 属性不存在），`discriminating-new-tests-vs-prefix.log`；QML 契约用例对修前因 `commandErrorBar` 不存在而无法通过（import/对象缺失级）。
- **不回归**：定向 `tests/workbench tests/ui_shell tests/reading_export` **216 passed / 0 skipped**（`targeted-workbench-uishell-reading.log`，含全部既有 QML 契约断言）；全仓 ×5 **899 passed / 0 skipped / exit 0**（895 基线 +4 新用例），逐次 `full-suite-post-fix-run{1..5}.log`。无新增 skip/xfail。

### AC ⑦ Handoff/证据/Review/集成/台账
本文件 + `verification/TASK-052/**`；Review、集成、台账在本提交后进行。

## 设计取舍（Review 关注点）

1. **signal 保裸文本、状态带前缀**：修改既有信号载荷会破坏既有断言与未知监听者（兼容面最小化）；诊断信息放新状态通道。
2. **对象分支保码**：PipelineError 原样传入 sink（不再 `error.detail or error.code` 丢码），code/detail 在状态文本中都在；裸 signal 仍只发 detail（与修前行为一致）。
3. **QML 复制实现**：隐藏 `TextEdit` + `selectAll()+copy()`（Qt Quick 无独立 Clipboard 单例 API 的最小方案），不引 Python 依赖。
4. **bar 用 `Layout.preferredHeight: visible ? 32 : 0`**：隐藏时不占布局空间。
5. **clearCommandError 幂等**：空状态下再清空不发通知。

## 证据索引（`verification/TASK-052/`）

| 文件 | 内容 |
|---|---|
| `discriminating-new-tests-vs-prefix.log` | 新用例对修前树 3 failed / exit 1 |
| `targeted-workbench-uishell-reading.log` | 定向 216 passed（既有 QML 契约全绿） |
| `full-suite-post-fix-run{1..5}.log` | 全仓 899 passed ×5 |

## 已知边界 / 留给后续

- **typed step 失败（如 PROVIDER_NOT_CONFIGURED 终止于 run 内部 → completed_with_failures）不经过 commandError**——run 内失败可见化属任务进度面板（TASK-051 已交付工作台三档视图；失败面板细节待 TASK-047 后切片）。本切片覆盖的是 VM 命令入口与 worker 崩溃面。
- 呈现为 provisional：颜色/文案/位置按 TASK-047 设计收敛。
- 错误历史（多条）不做：状态只保留最近一条（AC① 口径）。
