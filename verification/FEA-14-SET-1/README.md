# FEA-14-SET-1 证据索引（字体只读投影 · 窄化口径）

- Task：`FEA-14-SET-1`（设置页「字体」组 = 只读投影 + 回退解析 + 本地样例预览）
- Base：`c4e40509b`（scope 冻结点）；scope 依据 `doc/reviews/FEA-14-SET-1-scope-r1.md`（窄化口径 = READY-TO-FREEZE）
- 契约：C-03/C-02/P15/C-07 **零字节变更**（不提供字体选择/持久化；那需 UNFREEZE，另立卡）
- 日期：2026-11-10

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 投影正确性 | 注入 source → 3 行（token/栈/实际族+缺失/缩放行高）；未初始化 → 稳定占位 | **PASS**（`TypographyResolverTests` + `SettingsTypographyPanelTests`） |
| AC2 回退解析纯函数矩阵 | 已装命中 / 全缺失回退 generic / 空栈不伪造 / scale+lineHeight 透传 | **PASS** |
| AC3 零全局副作用 | 读取投影不创建/不改 `Application.Current`、不写 Styles/资源 | **PASS** |
| AC4 无 AppData 写入 | 真实 `%APPDATA%\NewManga` 前后指纹（路径/大小/mtime）一致 | **PASS** |
| AC5 UI/逻辑分离 + 搜索 + 只读 | 无 Avalonia `Application` 构造 VM；`字体`/`typography.ui` 命中；只读态 | **PASS** |
| AC6 边界与零契约变更 | `check.ps1`（默认 + `-TaskPath`）PASS；`verify_pins` 18/18；定向/全量测试 0 failed；diff ⊆ 16 paths | **PASS**（见下） |

## 门禁（本目录日志）

| 日志 | 内容 | EXIT |
|---|---|---|
| `logs/dotnet-typography-tests.log` | SET-1 定向 11 passed | 0 |
| `logs/dotnet-app-tests.log` | App.Tests 全量 849 / 0 / 11 | 0 |
| `logs/gates-check.log` | check.ps1 默认 + `-TaskPath` | 0 |
| `logs/gates-pins.log` | verify_pins 18/18 | 0 |

## 变异（`mutations/`）

| 变异 | 判别 | 结果 |
|---|---|---|
| M1 缺失族不记录（面板隐藏回退） | `TypographyResolverTests` | **RED**（2 failed，EXIT 1） |
| M2 投影直接取栈首（不做解析） | `TypographyResolverTests` | **RED**（2 failed，EXIT 1） |

复原后定向 11 passed（`-t:Rebuild` 验证）。

## 实现要点

- `TypographyResolver`：纯函数，逐段判断本机安装 → 首个已装为实际使用族，缺失段按序记录；全缺失回退 generic tail（`sans-serif`/`serif`/…）且 `Fallback=true`
- `AvaloniaTypographySource`：只读 `Nm.FontFamily.Ui/Data/Display` 资源 + `FontManager.TryGetGlyphTypeface` 探测；**不写资源/样式/设置**
- `SettingsPageView.BuildTypographyGroup`：3 行投影 + 未初始化占位 + 三种样例预览（字体只设在样例控件）+「字体族属于视觉主题」文案
- **不提供**字体选择/持久化：字体族归视觉主题（Theme Studio 是唯一写者；Fluent 无 Theme Studio = 已知 limitation）

## NOT_RUN（不得记 PASS）

- **UI 截图基线 = NOT_RUN**：本机无被审查的 Avalonia 渲染环境（headless 截图依赖未安装），交互由 VM/纯函数测试覆盖；FEA-15 可在真实 UI 环境补。

## 复现

```powershell
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter "FullyQualifiedName~TypographyResolverTests|FullyQualifiedName~SettingsTypographyPanelTests"
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-14-SET-1.md
pwsh -NoProfile -File tools/governance/verify_pins.ps1
```
