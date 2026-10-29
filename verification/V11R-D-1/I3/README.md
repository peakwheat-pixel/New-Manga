# V11R-D-1 I3 证据

- 分支 `v11r/d1-i3`，基线 main `b5f7d88fc`。
- 逐条处置：`DISPOSITION.md`。
- 日志：`build.log`、`test.log`、`badge-surface-tests.log`、`focus-provider-tests.log`、
  `token-gen-check.log`、`theme-gen-check.log`、`contrast-matrix.log`、`contrast-matrix.json`。

复现：

```powershell
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln --no-build
dotnet test tests/NewManga.DesignSystem.Tests/NewManga.DesignSystem.Tests.csproj --no-build --filter "FullyQualifiedName~BadgeCompositeContrast"
```
