# FEA-06 全量回归 Skip 归因

命令：`dotnet test apps\desktop-avalonia\NewManga.sln --no-build --settings apps\desktop-avalonia\tests\NewManga.runsettings`

结果：1030 passed / 0 failed / 57 skipped；各程序集计数与 skipped 测试全名见 `full-test.log`。

57 个 skip 都由现有集成测试的 fixture 前置条件触发：本次运行未设置 `NEWMANGA_CORECLIENT_SIDECAR_DIR`，`HostSidecarFactAttribute`、`SidecarFactAttribute`、`RunSidecarFactAttribute` 及对应 Book/S4 fixture attributes 会因此显式自跳过。Book/S4 数据 fixture 检查在 sidecar 检查之后执行，所以该环境下它们首先报告 sidecar 缺失。没有新增 skip，也没有移除或放宽任何测试。
