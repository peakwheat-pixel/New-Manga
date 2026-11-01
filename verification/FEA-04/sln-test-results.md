# FEA-04 解决方案测试结果

## 命令

Build：dotnet build apps/desktop-avalonia/NewManga.sln --artifacts-path G:/CODEX/New Manga.workspace/FEA-04/verification/FEA-04/artifacts --verbosity minimal

Test：dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --artifacts-path G:/CODEX/New Manga.workspace/FEA-04/verification/FEA-04/artifacts --verbosity minimal

## Build

Build 在 NuGet restore 阶段失败，0 warnings、14 errors。所有错误都来自 NuGet.targets(782,5)，内容为 Value cannot be null. (Parameter 'path1')。编译未开始。

## 逐工程计数

基线与实现均未执行任何测试用例。通过/失败/跳过执行计数分别为 0/0/0；这不是成功结果，测试工程状态为 NOT_RUN。测试命令因为找不到 DLL 返回 exit 1。

| 测试工程 | 基线状态 | 基线 P/F/S | 实现状态 | 实现 P/F/S |
|---|---|---|---|---|
| NewManga.App.Tests | NOT_RUN：baseline-artifacts 中无 DLL | 0/0/0（未执行） | NOT_RUN：artifacts 中无 DLL | 0/0/0（未执行） |
| NewManga.ApplicationCore.Tests | NOT_RUN：baseline-artifacts 中无 DLL | 0/0/0（未执行） | NOT_RUN：artifacts 中无 DLL | 0/0/0（未执行） |
| NewManga.CoreClient.Tests | NOT_RUN：baseline-artifacts 中无 DLL | 0/0/0（未执行） | NOT_RUN：artifacts 中无 DLL | 0/0/0（未执行） |
| NewManga.Host.Tests | NOT_RUN：baseline-artifacts 中无 DLL | 0/0/0（未执行） | NOT_RUN：artifacts 中无 DLL | 0/0/0（未执行） |
| NewManga.ThemeEngine.Tests | NOT_RUN：baseline-artifacts 中无 DLL | 0/0/0（未执行） | NOT_RUN：artifacts 中无 DLL | 0/0/0（未执行） |
| NewManga.DesignSystem.Tests | NOT_RUN：baseline-artifacts 中无 DLL | 0/0/0（未执行） | NOT_RUN：artifacts 中无 DLL | 0/0/0（未执行） |

测试 host 列出了 6 个测试 DLL 路径，但每个路径都缺少文件；完整 stderr 见 [baseline-test-no-build.log](baseline-test-no-build.log) 与 [implementation-test-no-build-final.log](implementation-test-no-build-final.log)。

Restore 重试包括 RestorePackagesPath、RestoreRootConfigDirectory、显式 RestoreConfigFile，以及设置 pwsh 子进程用户配置路径后运行 dotnet nuget locals；均仍报 path1 为空。完整记录见 [implementation-build-nuget-path-retry.log](implementation-build-nuget-path-retry.log)、[implementation-build-config-retry.log](implementation-build-config-retry.log)、[nuget-profile-path-probe.log](nuget-profile-path-probe.log)。

## 其他检查

- pwsh -NoProfile -File tools/governance/verify_pins.ps1（主仓库 G:/CODEX/New Manga）：PASS，all 15 pins；输出见 [verify-pins.log](verify-pins.log)。
- git diff --check：PASS，exit 0；仅有 Git 的 LF-to-CRLF 提示。
- 未运行任何单独测试绕过解决方案门禁。
