# REALUSE-DATA-SAFETY-6 证据索引

- Task：[doc/tasks/REALUSE-DATA-SAFETY-6.md](../../doc/tasks/REALUSE-DATA-SAFETY-6.md)
- 分支：`task/REALUSE-DATA-SAFETY-6`（base `main@841cbdc4b`）
- Worktree：`G:\CODEX\New Manga.workspace\worktrees\REALUSE-DATA-SAFETY-6`
- 证据生成日期：2026-11-01
- commit / sha256 pin 记录在任务卡 `Canonical Evidence` 表（不在本文件复制第二份）。

## 文件

| 文件 | AC | 内容 |
|---|---|---|
| [ac1-progress-refresh.md](ac1-progress-refresh.md) | AC1 | MA-09 根因、实现、测试矩阵与已知边界 |
| [ac1-progress-refresh-test-log.txt](ac1-progress-refresh-test-log.txt) | AC1 | `dotnet test` 真实输出（新增 5 例 + 全量 401）+ 负向对照记录 |
| [ac2-derived-conclusion.md](ac2-derived-conclusion.md) | AC2 | MA-19 结论：derived 是否必需（结论：现阶段必需，不改代码），含代码路径与真实数据印证 |
| [ac2-derived-realdata.json](ac2-derived-realdata.json) | AC2 | 真实数据根**只读**盘点原始输出（managed/derived 计数、逐字节 sha256 对照、catalog scope 分布） |
| [ac3-options.md](ac3-options.md) | AC3 | MA-11 旧库布局/旧壳共存、MA-20 安装脚本隔离的可选方案与影响（仅方案，未实施） |

## 复现

```powershell
# AC1 新增用例
cd apps/desktop-avalonia
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj `
  --filter "FullyQualifiedName~LibraryProgressRefreshTests" --nologo -v q

# AC1 全量回归（相关子集）
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj --nologo -v q

# AC2 真实数据只读盘点（脚本在仓外 tmp，按 ac2-derived-conclusion.md §6 的只读命令等价复现）
$root = Join-Path $env:APPDATA 'com.newmanga.desktop'
Get-ChildItem (Join-Path $root 'managed')      -Recurse -File | Measure-Object -Sum Length
Get-ChildItem (Join-Path $root 'derived\pages') -Recurse -File | Measure-Object -Sum Length
```

## 边界声明

- 本 Task **未**执行迁移、**未**安装/卸载/打包、**未**删除或改名任何真实数据；真实数据根只做过读取（枚举、只读 SQLite 连接在仓外副本上、读取样本文件算 sha256）。
- 仓外临时物：`G:\CODEX\New Manga.workspace\tmp\REALUSE-DATA-SAFETY-6\`（DB 副本 + 盘点脚本），**不在仓库内**，可随时删除；其中含用户数据副本，未纳入 git。
- 治理检查结果记录在任务卡「治理检查」一节；若为既有债务导致的 FAIL，会如实写明错误原文，不伪造 PASS。
