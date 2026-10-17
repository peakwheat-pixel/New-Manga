# P19-UI-FIX-1：修复前后 UIA 对照

被测修复提交：`f19275aedcf3ae02c11473ca46ad8b65a8c9a1a0`。修复前证据来自主仓 P19 D 验收，只读引用；修复后证据来自本 worktree 的最终构建和隔离数据副本。

## 设置页：9 个「未开放」分区

| 分区 | 修复前 UIA（`04-settings.uia.txt` 索引） | 修复前 Invoke | 修复后 UIA |
|---|---|---|---|
| OCR | 第 21 项，`en=True` | `invoked PAGE_CHANGED` | `IsEnabled=False`，可见，Invoke blocked |
| 图片修复 | 第 24 项，`en=True` | `invoked PAGE_CHANGED` | `IsEnabled=False`，可见，Invoke blocked |
| 排版样式 | 第 26 项，`en=True` | `invoked PAGE_CHANGED` | `IsEnabled=False`，可见，Invoke blocked |
| 模型/GPU | 第 28 项，`en=True` | `invoked PAGE_CHANGED` | `IsEnabled=False`，可见，Invoke blocked |
| 任务/并发 | 第 30 项，`en=True` | `invoked PAGE_CHANGED` | `IsEnabled=False`，可见，Invoke blocked |
| 缓存/Revision | 第 32 项，`en=True` | `invoked PAGE_CHANGED` | `IsEnabled=False`，可见，Invoke blocked |
| 回收站 | 第 34 项，`en=True` | `invoked PAGE_CHANGED` | `IsEnabled=False`，可见，Invoke blocked |
| 备份/恢复 | 第 36 项，`en=True` | `invoked PAGE_CHANGED` | `IsEnabled=False`，可见，Invoke blocked |
| Plugin/Hooks | 第 38 项，`en=True` | `invoked PAGE_CHANGED` | `IsEnabled=False`，可见，Invoke blocked |

修复前转储中的按钮名称仍含「未开放」。修复后名称包含「未开放：等待 section schema 冻结」，9 项均 `IsOffscreen=False`。逐项完整记录见修复后 UIA 转储和 trace。

- 修复前：`G:/CODEX/New Manga/verification/P19/d-run-v2/uia/04-settings.uia.txt`，`G:/CODEX/New Manga/verification/P19/d-run-v2/trace.log`（逐项 `PROBE ... en=True invoke=invoked PAGE_CHANGED`）。
- 修复后：[`04-settings.uia.txt`](04-settings.uia.txt)、[`uia-run.log`](uia-run.log)，运行器断言 `SETTINGS_ASSERTIONS=9/9 PASS`，9 次 Invoke 均 blocked。

## 书架「导入作品」

| 时点 | 点击后的 UIA 观察 | 结论 |
|---|---|---|
| 修复前 | 连续 10 次、间隔约 0.9 秒采样；无 `#32770`/FileDialog、无打开/选择窗口、无错误或反馈 | 入口静默无反应 |
| 修复后（空书架隔离副本） | 点击后打开导入面板；UIA 捕获 `role=status` 对应可见文本「未开放：空书架暂不支持创建作品和章节，当前无法导入文件或文件夹。」及文件/文件夹入口；应用退出码 0 | 用户得到明确原因，不再静默；因无目标章节，两个选择按钮按现有流程禁用 |

- 修复前：`G:/CODEX/New Manga/verification/P19/import-no-response-r4.md`。
- 修复后：[`import-open.uia.txt`](import-open.uia.txt)、[`uia-run.log`](uia-run.log)。UIA 反馈共 5 个元素；其中说明文本与两个选择按钮均 `IsOffscreen=False`。
- 取消与系统调用失败的可见状态由现有 `ImportDialog` 处理；前端回归测试覆盖取消、错误反馈，以及导入入口在空书架显示未开放原因。

## 隔离和数据保护

GUI 使用 `%APPDATA%\com.newmanga.m2rc1.desktop\{catalog,data,derived}` 的真实布局副本，并将 `NEWMANGA_DATA_ROOT`、`M2RC1_CATALOG_DB`、derived/managed roots 和临时目录重绑定到 `target/p19-ui-fix-1-isolation-20261017`。Namespace identity 调整只作用于隔离副本。原始 `catalog/data/derived` 四个文件在 GUI 前后长度和 SHA256 均相同，证据见 [`appdata-source-preservation-check.json`](appdata-source-preservation-check.json)。
