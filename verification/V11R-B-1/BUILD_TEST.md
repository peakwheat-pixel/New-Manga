# V11R-B-1 构建与测试记录（I1 返修后）

执行目录：`apps/desktop-avalonia`；本目录 `build.log` / `test.log` 为下述命令原样输出。

## 1. 构建

```
dotnet build NewManga.sln -warnaserror --nologo
```

- exit code：**0**；`0 个警告，0 个错误`

## 2. 测试

```
dotnet test NewManga.sln -m:1 --no-build --nologo
```

- exit code：**0**
- `-m:1` 串行化测试项目：并行运行多个项目时，既有 Host/CoreClient 集成测试会偶发争用同一临时目录
  的 SQLite `-shm`（`IOException: 另一个程序已锁定文件的一部分`，与本任务改动无关，已登记为测试
  基础设施 known issue）。串行是本仓库可复现的绿色基线。

| 测试项目 | 通过 | 跳过 | 失败 | 总计 |
|---|---|---|---|---|
| NewManga.Host.Tests | 39 | 21 | 0 | 60 |
| NewManga.DesignSystem.Tests | 40 | 0 | 0 | 40 |
| NewManga.ThemeEngine.Tests | 159 | 0 | 0 | 159 |
| NewManga.App.Tests | 237 | 5 | 0 | 242 |
| NewManga.CoreClient.Tests | 45 | 22 | 0 | 67 |

## 3. 本任务测试（I1 后：V2 共 85 条，全部通过）

| 测试类 | 覆盖 |
|---|---|
| `V2ShellStateTests` | ShellState 唯一状态源：空间/模式切换保留 selection/filter/scroll、表面栈、告警与寻址 |
| `V2KeyMapTests` | 契约 §6.3 全量快捷键、无冲突、可用性/待接入原因、命令面板覆盖 |
| `V2DeepLinkTests` / `V2PinyinTests` | 深链接解析回写；中文/拼音首字母搜索 |
| `V2WorkspaceIntegrationTests`（I1 新增） | `IWorkspaceView` 注册/反注册；`SwitchSpace`/`SetStudioMode` 先 `OnDeactivated(old)` 再 `OnActivated(new)`；工作区 `TryHandleKey` 优先拒绝（R-17 Tab）；未注册空间显示「尚未注册」占位且无内容 |
| `V2ShellUiTests`（真渲染） | 三空间路由；**真实 ScrollViewer.Offset** 跨 Ctrl+1/2/3 往返保持；加载态同尺寸骨架；上下文不重建 VM；命令面板/跳转/F1/Esc；IME 让位；主题切换不丢选择；导入逐文件状态+重试；无章节→真实 CreateChapter；回收站危险确认可取消；阅读浮层双模态进度+保存+Esc；1600/1280/1024 布局（4/3 列、narrow overlay、TopBand=36） |
| `V2ConformanceTests` | XAML 裸值扫描 + **C# 裸设计值扫描**（Margin/Padding/Spacing/BorderThickness/Opacity/Brushes/4 值 CornerRadius/布局字面量，`ShellLayout` 唯一 allowlist）；`Nm.Size.Breakpoint.*` 前值 1600/1280/1024 与禁用 1400/1200；`Nm.*` 存在性；双主题切换；R-18 断点断言 |

## 4. 证据生成（R-19 纪律：测试默认不写仓库）

```
# 唯一入口：显式设置 NEWMANGA_EVIDENCE_SYNC=1 后镜像到 verification/V11R-B-1/
pwsh -NoProfile -File verification/V11R-B-1/curate.ps1
```

- 普通 `dotnet test` 只写 `%TEMP%/newmanga-evidence/V11R-B-1/`（临时目录，绝不触碰仓库）。
- 仅当 `NEWMANGA_EVIDENCE_DIR` 或 `NEWMANGA_EVIDENCE_SYNC=1` 显式存在时才镜像进仓库；
  镜像失败自动重试/换名，不使测试失败。
- 截图文件名唯一：`<TestName>--<name>.png`（本目录 `screens/` 13 张）。
- `conformance/v2-tokens-and-classes.json` 同样由 curate 脚本生成。

## 5. NOT RUN（环境限制）

| 项 | 原因 |
|---|---|
| 真实 Python Core sidecar 端到端（空库→建书→建章→导入→重启可见） | 本机无可用 Core sidecar / 隔离数据根；UI 侧用 `FakeHostController`（真实 DTO 与命令调用记录）覆盖 |
| `MainWindow` 承载 `AppShellV2` 的启动截图 | 归 V11R-INT-1（Lead），本任务不改 `MainWindow.axaml` / `App.axaml.cs` |
| 100/150/200% DPI 实机验证 | 需真实桌面，归发布/INT-1 验证 |
