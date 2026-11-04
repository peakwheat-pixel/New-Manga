# FEA-09-UI-1 DSH 成功门禁实际命令与时间（整理记录）

整理时间：2026-11-04T10:45:00+08:00（本文件写入时间；非运行时间）
运行环境：Windows / pwsh 7 / .NET 9 / C:/Python314/python.exe；CWD = `G:\CODEX\New Manga`
说明：以下命令按项目实际执行顺序记录；运行时间取自日志/TRX 文件时间戳（约 10:11–10:15），本文件为其整理说明。

1) build（日志 `logs/dsh/build.log`，含 COMMAND/CWD/DATE 头 + EXIT=0）
   `dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo`

2) 全量测试（逐项目；日志 `logs/dsh/full-test.log` 每个项目 COMMAND/EXIT；TRX 唯一）
   对以下 8 个项目分别执行：
   `dotnet test <project>.csproj -c Release --no-build --nologo --logger "trx;LogFileName=dsh-full-<project>.trx" --results-directory verification/FEA-09-UI-1/logs/dsh/trx`
   项目：NewManga.App.Tests / NewManga.Appearance.Tests / NewManga.ApplicationCore.Tests /
         NewManga.CoreClient.Tests / NewManga.DesignSystem.Tests / NewManga.Host.Tests /
         NewManga.Presentation.Avalonia.Tests / NewManga.ThemeEngine.Tests
   结果：1317 passed / 0 failed / 74 skipped（TRX 逐项可核）。

3) 真实 IPC（日志 `logs/dsh/ipc-test.log`，EXIT=0；TRX `logs/dsh/trx/dsh-ipc.trx`）
   `$env:NEWMANGA_FEA09_IPC='1'; $env:NEWMANGA_BUILD_PYTHON='C:/Python314/python.exe'`
   `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build`
   `  --filter "FullyQualifiedName~Fea09UiImportIpc" --logger "trx;LogFileName=dsh-ipc.trx"`
   结果：16 passed / 0 failed / 0 skipped。

4) 其它：`python tools/generate_api_inventory.py --check` PASS；`pwsh tools/governance/check.ps1` PASS（3 warnings）；`pwsh tools/governance/verify_pins.ps1` 17/17 PASS。
