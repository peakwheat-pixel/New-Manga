# V11R-INT-1 集成证据（进行中）

## 已完成
| 步骤 | 内容 | 证据 |
|---|---|---|
| I-1 | --shell=v2 由 AppShellV2.CreateRoot(...) 承载主窗口；--shell=legacy 保留回滚路径；--page 映射到三空间；--theme-id 兼容旧 --theme | App.axaml.cs、AppOptions.cs、本目录截图 |
| I-2 | Theme Studio 表面经 ThemeStudioSurfaceAdapter 注册到 ISurfaceWorkspace 表面栈，绑定**真实** ThemeEngineThemeStudioService.CreateProduction（与 shell 共享同一个 DesignSystemThemeManager）；持久化设置在启动后异步应用 | Shell/V2/ThemeStudioSurfaceAdapter.cs |
| I-3 | 真实窗口首启：dark 主题、TopBand 四入口、Library 空态、状态带显示 Host 未就绪：等待 Core sidecar（诚实，不伪造） | 2-shell-first-run.png（2560×1440 桌面截图，窗口 1100×760 默认尺寸） |

## 待完成（L3 前）
- D-1 I2（启动全局令牌修复、Light Skipped 对比度）合入后复测视觉。
- 接入真实 Core sidecar 的 E2E 冒烟（建书→建章→导入→重启）。
- 三档尺寸截图（1600×1000 / 1280×800 / 1024×700）+ 明/暗。
- 主题切换画布像素不变（在 v2 壳内）。
- 默认 shell 翻转（DefaultShellId legacy→v2）仅在上述全绿后执行。

## 复现
```
cd apps/desktop-avalonia
dotnet run --project src/NewManga.App/NewManga.App.csproj -- --shell=v2 --exit-after=25000 --data-root <temp>\data --log-dir <temp>\logs
```
