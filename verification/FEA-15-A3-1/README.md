# FEA-15-A3-1 证据索引（四壳回归）

- Task：`FEA-15-A3-1`（FEA-15 A3：legacy / current-v2 / fluent / presentation-host + 四页真实进程冒烟）
- 执行 head：`a9518a7e2`；exe：A2 staging `NewManga-0.1.1-win-x64/app/NewManga.App.exe`
- 日期：2026-11-10

## 结论状态

| AC | 判别 | 结果 |
|---|---|---|
| AC1 四壳冒烟 | legacy / current-v2 / fluent / presentation-host 各 EXIT 0 + 窗口句柄 | **MET**：4/4 `window=True, exit=0`（handles **67703052 / 19006476 / 34606288 / 14159454**（重跑修复后 JSON）） |
| AC2 Fluent 四页 | bookshelf/workbench/reader/settings 各 EXIT 0 + 窗口句柄 | **MET**：4/4 `window=True, exit=0`（handles **9699996 / 51973638 / 36965272 / 9896604**（重跑修复后 JSON）） |
| AC3 隔离 | 真实双根 AppData 前后一致 | **PARTIAL**：`%APPDATA%\NewManga`（1 文件/359 B/digest `b50c6ce4…`）不变；`%APPDATA%\com.newmanga.desktop` 文件数 524 不变但 **`logs/window-material.log` 每次冒烟追加 83 B**（原 1,206,936 → 首轮 1,207,019 → 重跑后 1,207,102；累计 +166 B），data bytes 209,813,290→209,813,456，digest 变。该日志路径固定真实 data root、不被 `--data-root` 重定向（limitation，见下） |
| AC4 headless 关键路径 | FluentShellTests / StartupCompatibilityMatrixTests / PresentationHostCompositionTests | **MET**：14 passed / 0 failed（`logs/dotnet-headless.log`） |
| AC5 NOT_RUN 登记 | 真实手势/IME/多屏/DPI/系统主题/托盘 | **MET（登记）**：见 NOT_RUN |
| AC6 门禁与证据 | check PASS；无产品代码/契约/DDL diff；证据含 EXIT | **MET**：check（默认 + TaskPath）PASS；无 src 产品/契约/DDL 改动 |

## 门禁与证据（本目录）

| 文件 | 内容 | EXIT |
|---|---|---|
| `logs/smoke-shells.log` | 四壳 + 四页冒烟（`logs/smoke-shells.json`，cases=8 全对象） | 1（因 AC3 limitation，非用例失败） |
| `logs/dotnet-headless.log` | headless 关键路径 **14/0** | 0 |
| `logs/appdata-window-material-write.log` | AC3 limitation 证据（文件/字节/mtime + 结论） | — |
| `scripts/smoke-shells.ps1` | 冒烟脚本（双根隔离 + 真实 roots 指纹） | — |

**JSON 结果**（`logs/smoke-shells.json`，重跑修复后）：`cases.Count=8`（全对象）、`shells_ok=true`、`pages_ok=true`、`appdata_unchanged=false`（window-material.log 每次冒烟追加 83 B；本次重跑后累计追加 166 B；用户数据与主题未变）。

## limitation（不阻断 AC1/AC2/AC4，AC3 判 PARTIAL）

- `logs/window-material.log`（窗口材质诊断日志）的路径固定为真实 `%APPDATA%\com.newmanga.desktop\logs\`，**不随 `--data-root` 重定向**；四壳冒烟各启动一次后追加 83 B。属产品侧日志路径行为，建议另立任务（日志路径跟随数据根）或在正式验收中接受为已知 limitation。

## NOT_RUN（不得记 PASS）

- 真实手势 / IME / 多显示器 / DPI 100–200% / 系统主题跟随 / 托盘 = NOT_RUN（无交互会话；headless/进程级只到「窗口出现 + 参数生效 + 退出码」）。
- A2 已登记的 NOT_RUN 继续有效（真实 setup.exe `/S`、交互向导、SmartScreen、快捷方式人工确认、人工目视四页）。
- `window-material.log` 写入**不可逆已发生**（披露，不冒充未发生）；用户数据未变。

## 复现

```powershell
pwsh -NoProfile -File verification/FEA-15-A3-1/scripts/smoke-shells.ps1 -Exe "G:\CODEX\New Manga.workspace\FEA-15-A2-1\out\NewManga-0.1.1-win-x64\app\NewManga.App.exe" -IsoRoot "G:\CODEX\New Manga.workspace\FEA-15-A3-1\iso" -Out "G:\CODEX\New Manga.workspace\FEA-15-A3-1\smoke-shells.json"
dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj --filter "FullyQualifiedName~FluentShellTests|FullyQualifiedName~StartupCompatibilityMatrixTests|FullyQualifiedName~PresentationHostCompositionTests"
```
