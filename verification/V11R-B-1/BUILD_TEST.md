# V11R-B-1 构建与测试记录

执行目录：`apps/desktop-avalonia`
证据文件：`build.log`、`test.log`（本目录，命令原样输出）

## 1. 构建

```
dotnet build NewManga.sln -warnaserror --nologo
```

- exit code：**0**
- 结果：`已成功生成。 0 个警告，0 个错误`
- 解决方案项目：CoreClient / Host / Theme / App / **DesignSystem（V11R-D-1 M0）** / 四个测试项目

## 2. 测试

```
dotnet test NewManga.sln --no-build --nologo
```

- exit code：**0**
- 汇总（`test.log` 原始行）：

| 测试项目 | 通过 | 跳过 | 失败 | 总计 |
|---|---|---|---|---|
| NewManga.DesignSystem.Tests | 24 | 0 | 0 | 24 |
| NewManga.Host.Tests | 39 | 21 | 0 | 60 |
| NewManga.App.Tests | 178 | 2 | 0 | 180 |
| NewManga.CoreClient.Tests | 39 | 22 | 0 | 61 |

跳过项都是既有环境依赖用例（真实 sidecar / 冻结二进制），与本次改动无关。

## 3. 本任务新增测试（33 条，全部通过）

| 测试类 | 条数 | 覆盖 |
|---|---|---|
| `V2ShellStateTests` | 6 | 唯一状态源、表面栈逐级 Esc、空间/模式切换保留 selection+筛选+滚动、Studio Page/Batch 独立滚动、PropertyChanged、寻址路径 |
| `V2KeyMapTests` | 5 | 契约 §6.3 全量快捷键（Ctrl+1/2/3、Tab、Ctrl+K、Ctrl+P、Ctrl+E、Ctrl+,、F1、F5、Ctrl+Shift+F、Esc、J/K、`[`/`]`、Shift+`[`/`]`）、无冲突、冲突检测、可用性/待接入原因、命令面板覆盖 |
| `V2DeepLinkTests` | 4 | `?space=&mode=&book=&chapter=&page=&region=` 解析/拒绝/回写 |
| `V2PinyinTests` | 3 | 中文子串、拼音首字母、混合 ASCII/空查询 |
| `V2ShellUiTests`（`[AvaloniaFact]` 真渲染） | 11 | 三空间路由 + 1600 渲染、上下文不重建 VM、命令面板/跳转/F1/Esc、IME 让位、主题切换不丢选择、导入逐文件状态+重试、无章节→真实新建章节→导入、回收站危险确认可取消且不写、阅读浮层双模态进度+保存+Esc、工位/控制台占位、1280/1024 两档 |
| `V2ConformanceTests` | 4 | V2 XAML 无裸色值/裸字号/裸尺寸/阴影/渐变/模糊/圆角>3px、`Nm.*` 全部存在于 DS、令牌/Classes 清单 JSON、预置兜底文件已删除 |

## 4. 截图生成

```
$env:NEWMANGA_EVIDENCE_DIR = "<repo>/verification/V11R-B-1"
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter "FullyQualifiedName~V2"
```

同一命令生成 `screens/*.png`（12 张）与 `conformance/v2-tokens-and-classes.json`。

## 5. NOT RUN（环境限制，非本任务失败）

| 项 | 原因 |
|---|---|
| 真实 Python Core sidecar 端到端（空库→建书→建章→导入 2 页→重启可见） | 本机无可用 Core sidecar / 隔离数据根；未运行真实进程。UI 侧用 `FakeHostController`（真实 DTO/真实命令调用记录）覆盖，逻辑与 IPC 调用次数均有断言 |
| 真实窗口 `MainWindow` 承载 `AppShellV2` 的启动截图 | `MainWindow.axaml(.cs)` 归 `V11R-INT-1`（DSH）切换，本任务不改；`AppShellV2` 可独立承载且已用真实窗口 headless 渲染截图 |
| 100/150/200% DPI 实机验证 | 需要真实桌面；headless 无 DPI 缩放模拟，规格要求由 INT-1/发布验证覆盖 |
