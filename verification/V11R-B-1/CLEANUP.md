# V11R-B-1 证据目录清理记录（P1 返修）

## 问题

`35f4dfd29` 提交时执行了 `git add -A`，把工作树中其它任务的证据副本一并提交进
`verification/V11R-B-1/`：135 个文件里只有 20 个是本任务产物，其余 115 个属于其它
11 个任务（含 SQLite `.db/.db-wal` 二进制）。这违反证据归属纪律。

## 清理方法与可复核结论

1. **字节级重复检测**：对 `verification/**`（排除 B-1）所有文件计算 SHA-256，与 B-1 内每个文件比对。
   结果：**57 个文件与其它任务证据字节级完全相同**（与 Lead 审查结论一致），来源分布：
   CORE-SLIM-1(1)、CREDENTIAL-PORT-1(4)、CREDENTIAL-UI-1(7)、HOST-COMMAND-MIGRATION-1(4)、
   HOST-RESOURCE-SECURITY-1(3)、IMPORT-EXPORT-UI-1(4)、PDF-EXPORT-UI-1(6)、READER-SELECTOR-UI-1(5)、
   REGION-WORKBENCH-1(3)、SETTINGS-PROFILE-UI-1(9)、THEME-MACOS-1(3)、THEME-MACOS-2(8)。
2. **其余 58 个非重复文件**同样不属于本任务（路径/内容属于 A-3/A-4/B-3/B-4/C-1 等任务的日志、
   ndjson、截图、DB 变体），按"删除全部外任务文件"一并删除。
3. 删除清单（20 个外来目录，115 个文件）：
   `commands(16) contract(1) credential-ui(8) diagnostics(3) e2e(1) host(1) host-logs(1)
   import-export-ui(6) layout(4) legacy-shell(1) logs(4) pdf-export-ui(6) performance(6)
   reader-selector-ui(5) screenshots(16) security(13) settings-profile-ui(10) theme(7) wire(3) workbench(3)`。
4. **保留/重新生成的本任务证据**（23 个文件）：
   - 7 个根文件：`README.md BUILD_TEST.md AC_COVERAGE.md DEVIATIONS.md NOT_WIRED.md build.log test.log`
   - `screens/` 13 张（R-19 命名：`<TestName>--<name>.png`）——由 `curate.ps1` 显式生成
   - `conformance/v2-tokens-and-classes.json`——由 `curate.ps1` 显式生成
5. 说明：若只删除 57 个字节级重复件，目录里仍会留下 58 个外任务独有文件（仍是污染）；
   因此本次按"删除全部外任务文件"清理到仅剩本任务证据。Lead 若希望保留那 58 个另行归档，
   可再指示（它们已在 main 对应任务目录中存在同名/同源证据）。

## 防复发

- `git add -A` 不再用于该目录；证据只由 `curate.ps1` 显式生成（R-19）。
- 普通 `dotnet test` 写入 `%TEMP%/newmanga-evidence/<TASK>/`，不触碰仓库；
  仅 `NEWMANGA_EVIDENCE_SYNC=1`（curate 脚本设置）才镜像进 `verification/<TASK>/`。
- 新增 conformance 断言：`V2ConformanceTests` 扫描本任务 XAML/C# 裸设计值，避免证据与实现漂移。

## 复核命令

```powershell
# 计算 B-1 内文件与其它 verification 证据的字节级重复（应无输出）
$b1 = Get-ChildItem verification/V11R-B-1 -Recurse -File
$pairs = @{}
Get-ChildItem verification -Recurse -File | ? { $_.FullName -notlike '*\V11R-B-1\*' } |
  % { $pairs[(Get-FileHash $_.FullName).Hash] = $true }
$b1 | % { if ($pairs[(Get-FileHash $_.FullName).Hash]) { $_.FullName } }

# 重新生成本任务证据（唯一入口）
pwsh -NoProfile -File verification/V11R-B-1/curate.ps1
```
