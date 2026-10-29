# V11R 集成计划（INT-1）— 新壳切换为默认入口

状态：`PREPARED`（2026-10-30，DSH）。执行任务：`V11R-INT-1`（Owner: DSH；Reviewer: 独立）。
前置：`V11R-D-1` 收口、`V11R-B-1..B-4` I1 返修通过、`V11R-C-2` 交付、`V11R-F0-1/F0-2` 合入。

---

## 1. 目标

把已实现的新 UI（`AppShellV2` + 三空间 + Studio 双模式 + Theme Studio 表面）接成**产品默认入口**，并接真实 Core：
1. `MainWindow` 承载 `AppShellV2`（旧 `MainWindow.axaml.cs` 的 code-built 页面退居 fallback）。
2. 单一状态源与单一选择模型（R-16）、键盘仲裁（R-17）、工作区注册（`IWorkspaceView`）。
3. Theme Studio 成为真实可用表面（TopBand「主题」、`Ctrl+,`、Console「外观」三入口）。
4. DS 自定义控件/图标上收（替换各 Owner 的本地实现）。
5. 保留**回滚开关**：`--shell=legacy` 可启动旧壳（v1 版本内），默认 `--shell=v2`。

## 2. 接线步骤（顺序执行，每步可独立验证）

| 步 | 内容 | 验证 |
|---|---|---|
| I-1 | `Program.cs`/`App.axaml.cs`：解析 `--shell`（默认 `v2`），v2 时构造 `AppShellV2.CreateRoot(controller, options)` 并设为 `MainWindow`；legacy 时沿用旧路径 | 两种 shell 均可启动（headless/smoke）；`--shell=legacy` 截图 |
| I-2 | 工作区注册：Library/Console（ui-shell）、Studio（ui-studio）、ThemeStudio（theme-studio）实现/适配 `IWorkspaceView`；`AppShellV2.RegisterWorkspace(...)` 注册四个 | 三空间 + ThemeStudio 表面可进入；未注册时空态 |
| I-3 | 选择模型归一：`ShellState.Selection` 权威；Studio 侧 `StudioSelection` 改投影 + 路由；`ScopeKind` 优先级 SelectedPages > Page > Region | 单测：Batch 选 3 页 → Page 作用域 3 页；Region 选中不吞多选 |
| I-4 | 键盘仲裁：shell `TryHandleKey` 先问当前工作区；Studio Tab/Esc/J/K/[ ]/+/-/0 归 Studio；其余归 KeyMap；冲突启动断言 | 键盘矩阵测试（每个空间 × 关键键） |
| I-5 | `StatusBand`/`AttentionMenu` 接 `IRunController` 快照（无 Run 隐藏）；主题按钮/Ctrl+,/Console 外观入口 → Theme Studio | 有 Run/无 Run 两态截图；三入口都能打开 C-2 |
| I-6 | Theme Studio 真接入：`IThemeService`（Part B）→ `ThemeStudioViewModel`；应用/取消/恢复默认走真实服务；旧主题 ID 迁移到默认 | 7 分区可用；应用后重启保持；取消回滚；主题切换画布像素不变 |
| I-7 | DS 上收：删除各 UI Owner 的本地 `StatusGlyph/StatusBadge/Kbd/EmptyState/AlertBanner/Modal/图标` 实现，改用 DS 版本；本地 conformance 测试改断言 DS 来源 | 全局无重复实现（grep 双份符号表为 0）；构建/测试绿 |
| I-8 | 旧主题入口下线（配合 C-3）：旧设置页主题中心不可达；`--theme/--variant` 旧参数改为 `--theme-id`（或保留兼容映射） | 旧参数不崩溃；旧配置启动成功 |
| I-9 | E2E 冒烟：E2E-01（空库→建书→建章→导入→重启）、E2E-03（Run 暂停/继续/停止）、E2E-04（编辑→保存→重启）、E2E-05（阅读/进度）、E2E-06（导出） | `verification/V11R-INT-1/` 真实日志+截图 |
| I-10 | 默认入口证据：1600×1000 / 1280×800 / 1024×700 三档截图（暗/浅）；主题切换前后；无窗口闪烁 | 截图 + 像素哈希 |

## 3. 关键风险与对策

| 风险 | 对策 |
|---|---|
| 新壳首次成为默认入口后，旧壳回归问题 | 保留 `--shell=legacy` 一个版本；两种 shell 都跑 smoke；L4 前不删除旧壳代码（C-3 之后） |
| 选择模型重构引发 Studio 页面回归 | I-3 单独 commit + 现有 29 条 Studio 测试全绿；Batch→Page→Batch 往返测试 |
| 键盘冲突（shell 吞掉工位键） | I-4 先加仲裁再切默认；键盘矩阵测试覆盖 Tab/Esc/J/K/[ ]/+/-/0 |
| Theme Studio 与壳的表面栈耦合 | 表面栈归 shell（`ShellState.Surface`），C-2 只暴露 `Open/Close/RequestClose` |
| DS 上收导致视觉回归 | 上收前后同屏截图对比；conformance 断言无本地符号表 |
| 旧配置/旧主题 ID 导致启动失败 | 迁移层 fail-open 到默认主题（C-1 已实现迁移）；启动 smoke 用旧配置 fixture |

## 4. 回滚

- 代码：`git revert` I-1 单步即可回到 legacy 默认（`--shell` 默认值改回 legacy）。
- 数据：本阶段不迁移用户数据；主题设置写入新文件（`theme-settings.json`），不删除旧配置。
- 证据：每步 commit + `verification/V11R-INT-1/` 记录 step → commit 映射。

## 5. 完成判据（L3）

1. 默认启动进入新壳；三空间 + 双模式 + Theme Studio 全部真实可用（无 NOT_WIRED 的一级入口）。
2. E2E-01/03/04/05/06 至少各 1 次真实执行 PASS（其余写 NOT_RUN 并说明环境）。
3. 键盘矩阵、上下文保留、主题切换不改画布像素三类测试全绿。
4. 独立 Reviewer 对集成结果签署 L3；发现的 P1 修复后重跑受影响范围。
