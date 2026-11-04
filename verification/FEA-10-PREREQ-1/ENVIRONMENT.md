# 验证环境与限制

- 仓库：`G:/CODEX/New Manga`；branch `main`；开始/当前 HEAD `e45baa8b5946a1d581f30b025db045c77e99a6df`；Task 指定 base `1254d4e01608d3c9577872abb1dedea5661889aa`。
- Windows；目标 .NET `net9.0`；默认 CLI SDK `10.0.401`，另装 SDK `9.0.308`；runtime `9.0.11`。未新增依赖、未改项目文件。
- `exec_command` 入口在启动时被 Windows 740 拒绝；使用 Node `child_process.execFile` 启动既有 Git/dotnet/pwsh。无提权、无权限修改。
- 子进程初始缺少 APPDATA / ProgramFiles / ProgramFiles(x86) / ProgramW6432 / ProgramData。逐步补齐后 NuGet restore 仍报 `GetRestoreSettingsTask -> NuGetEnvironment.CalculateFolderPath -> Path.Combine(path1)`。默认 SDK 和显式 SDK 9 均复现。最终环境显式包含这些路径、原 PATH/TEMP/TMP/SystemRoot/ComSpec/USERPROFILE/LOCALAPPDATA/PROCESSOR_ARCHITECTURE/OS，及 `DOTNET_CLI_WORKLOAD_UPDATE_NOTIFY_DISABLE=true`、`MSBUILDDISABLENODEREUSE=1`、`DOTNET_CLI_USE_MSBUILD_SERVER=0`。
- 原始继承环境的 `NEWMANGA_*` 变量名清单为空；未清除已配置 fixture。本次无打包 sidecar/book/region fixture、无 FEA09 IPC opt-in、无模型/API 调用。74 个 skipped 逐项记录在 `logs/skipped-tests.json`，不计作 passed。
- 完整编译补充命令：`dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo --no-restore -p:UsedAvaloniaProducts=`；使用既有依赖缓存，关闭 Avalonia 构建遥测 target，0 warnings / 0 errors。`AVALONIA_TELEMETRY_OPTOUT=1` 单独设置仍遭遥测日志访问拒绝，见尝试日志；最终环境保留该 opt-out。未修改 NuGet 配置或包内容。
- Task 规划的仓外 `G:/CODEX/New Manga.workspace/FEA-10-PREREQ-1/` 不在本会话可写根内，未创建。新投影测试全部为纯内存测试；既有全量测试按其原 fixture 使用 OS TEMP 或既有固定 evidence/task-env 路径。权限不足如实记录，不迁移或清理旧目录、不修改测试以跳过失败。
- 原始带 restore 的 build、全量测试和治理检查未达 PASS；补充编译成功不代替原门禁。
- 日志逐条含命令、时间、EXIT。早期日志中的 ENV 行仅列当时记录的部分环境，不表示完整变量清单；各次追加环境按本节描述。`build-diagnostic.log` 仅保留异常栈摘录，省略一般 diagnostic 环境转储。
