## 结论：**FAIL**

固定 pin `a466a150…` 的旧主题项目已删除，但迁移和验收仍有缺口，**C-3 不能标记完成**。

1. **删除完整性 — 通过，有范围说明。** `NewManga.Theme` 源码、项目文件及 `.sln`、`App.csproj` 引用均已删除。生产代码没有旧符号的实际依赖；但 `DependencyBoundaryTests` 仍以字符串列出旧符号，`LayoutKind` 也保留在 P/Invoke 声明中。因此 R6 证明的是“被分类为待删除的依赖为零”，不是 `src/tests` 字面匹配为零。

2. **迁移正确性 — 有问题 [P2]。** `LegacyChrome` 只解析 `Nm.*` 令牌，不引用旧项目；旧壳固定 Sonoma 布局符合执行报告。不过，设置页和 `CycleTheme` 只切换 `RequestedThemeVariant`，没有同步 DS palette，旧壳的浅/暗切换可能只改变 Avalonia variant，颜色仍维持原 palette。[MainWindow.axaml.cs](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.App/Views/MainWindow.axaml.cs:535>) 另外 `LegacyChrome` 有硬编码 fallback 色值和圆角；视觉等价未验证。

3. **替代断言 — 不充分 [P2]。** 五条新测试在交付日志中通过，`Evidence.cs` 共享 helper 也保留了。但 chrome 和首帧测试构造的是旧 `MainWindow`，无法替代清单要求的新壳断言；现有迁移测试验证设置文件迁移，不验证 App 启动接线。

4. **零引用门与证据 pin — 部分可信，有治理问题 [P2]。** 142 条剩余引用拆为 87 条证据/文档和 55 条非依赖，计数自洽；P/Invoke 假阳性也有分类。脚本用大小写敏感的 `git grep` 扫描跟踪文件，包含 `.axaml`、`.csproj`，但不识别大小写变体或拼接字符串。R6 生成时记录 `workingTreeDirty=True`、`repoHead=754dc0d`；到 pin 的代码差异仅是 `LegacyChrome` 注释。另有六个 `V11R-C-3-READY` 文件被原位改写，与 Task 的“只新增日志，不覆盖 READY 原始字节”及 `allowed_paths` 不符。

5. **兼容映射与启动证据 — 有问题 [P2]。** [`App.axaml.cs`](<G:/CODEX/New Manga/apps/desktop-avalonia/src/NewManga.App/App.axaml.cs:45>) 调用迁移后只写 Trace，没有应用 `migrated.Settings.Appearance`；因此 `--theme=saber-light`/`sakura` 的 Light 映射会丢失，除非另传 `--variant`。`ThemePackService.ApplyDefault` 已清理。smoke 记录窗口标题和 Legacy Host session，但进程由 harness 终止，没有正常退出码；R1 后的 tag-exists DryRun 和 L1 回滚演练也未见证据。`R6-report` 引用的 `R6-v2-host.log` 不在 pin 文件清单中。

6. **字体测试失败 — 测试缺陷 [P2]，不是随包字体证据。** [`No_font_binaries_ship_with_the_application`](<G:/CODEX/New Manga/apps/desktop-avalonia/tests/NewManga.App.Tests/ThemeRetirementR4Tests.cs:23>) 递归扫描整个仓库，未排除 `.gitignore` 忽略的根目录 `training_data/`；`NewManga.App.csproj` 没有将该目录纳入应用内容，且没有跟踪的字体文件。该失败反映扫描边界错误，不能证明字体随包。

**已核实正确：** 旧项目及工程引用已删除；`--shell=legacy` 的 smoke 记录 `started=True`、窗口标题 `New Manga`，并有 Host session opened 日志。  
**UNVERIFIED：** tag 建立后的 DryRun、L1 实际回滚演练、新壳替代断言，以及旧壳外观切换的有效性。本次只读审查未运行测试、未修改文件。

**退役状态：** `NewManga.Theme` 核心实现已退役，但完整验收不成立。当前 `main`（`67b86c519`）包含该 pin；**没有必须立即回滚 main 的理由**，可继续无关工作，但应先修复上述缺口再关闭 C-3。推荐由 DSH 释放定点返修并安排未参与实现者复审。