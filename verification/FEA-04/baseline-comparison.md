# FEA-04 基线对照

## Commit 与基线

- Task 声明的 base_commit：7a91352609d3336c9256fd77e572c0786107d950。
- 实际 worktree 分支：feat/fea-04；开始与交付时 HEAD：68c72ba5710184952ff25686a911d20839f7c8b6；该提交的父提交正是 Task base_commit。
- 冻结行为基线：91be6c134（Task R-CURRENT-2）。开始改动前对照源码与该冻结点一致；本交付没有提交，交付差异仍是相对 HEAD 的 dirty worktree diff。
- 基线测试计数因基线 build 被 NuGet restore 阻断而不可取得。不得将它记为 0 个测试通过，也不得把后续 NOT_RUN 视为基线计数。

## Build / Test 对照

| 阶段 | 命令与结果 | 工程/测试计数 |
|---|---|---|
| 基线 build | dotnet build apps/desktop-avalonia/NewManga.sln --artifacts-path C:/Users/49745/AppData/Local/Temp/FEA-04-impl-artifacts --verbosity minimal；失败，NuGet.targets(782,5) 报 Value cannot be null. (Parameter 'path1')，14 errors、0 warnings。 | Restore 阶段失败，未进入编译。完整输出：[baseline-build.log](baseline-build.log)、[baseline-build-retry.log](baseline-build-retry.log)。 |
| 基线 no-build test | dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --artifacts-path G:/CODEX/New Manga.workspace/FEA-04/verification/FEA-04/baseline-artifacts --verbosity minimal；exit 1。 | 6 个测试工程均缺失对应 DLL；测试用例未执行，逐工程记录见 [baseline-test-no-build.log](baseline-test-no-build.log)。 |
| 实现 build | dotnet build apps/desktop-avalonia/NewManga.sln --artifacts-path G:/CODEX/New Manga.workspace/FEA-04/verification/FEA-04/artifacts --verbosity minimal；失败，同一 path1 restore 错误，14 errors、0 warnings。 | Restore 阶段失败，未进入编译。完整输出：[implementation-build-final.log](implementation-build-final.log)。 |
| 实现 no-build test | dotnet test apps/desktop-avalonia/NewManga.sln --no-build --settings apps/desktop-avalonia/tests/NewManga.runsettings --artifacts-path G:/CODEX/New Manga.workspace/FEA-04/verification/FEA-04/artifacts --verbosity minimal；exit 1。 | 6 个测试工程均缺失对应 DLL；测试用例未执行，逐工程记录见 [sln-test-results.md](sln-test-results.md) 与 [implementation-test-no-build-final.log](implementation-test-no-build-final.log)。 |

## 解释与限制

基线 build 和实现 build 都在 NuGet restore 阶段失败，无法得到被冻结的逐工程通过数，也无法编译或执行新测试。实现前的测试结果与实现后的结果因此没有可比较的 executed test counts。实现前后源码差异和测试用例只作为交付内容，不能替代 AC2 的行为回归证据。

已尝试使用 RestorePackagesPath、RestoreRootConfigDirectory 与显式 RestoreConfigFile 重试 restore；错误仍在 NuGet.Configuration.ConfigurationDefaults/path1 初始化阶段，详见 [implementation-build-nuget-path-retry.log](implementation-build-nuget-path-retry.log)、[implementation-build-config-retry.log](implementation-build-config-retry.log)。
