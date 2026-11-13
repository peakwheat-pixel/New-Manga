# P1 · .NET 全量基线归因与复跑（MAINT-1，2026-11-14）

对象：`FEA-15-ACCEPT-1` 保留的「.NET 127 failed」限制项。只做归因与复跑取证，**不翻转任何节点状态**。

## 1. 来源

`verification/FEA-15-ACCEPT-1/dotnet-full.log`（2026-11-10，隔离 clean-tree，8 项目，`failed_projects=2 EXIT=1`；`PROJECT_EXIT` 序列 `1,0,0,0,0,1,0,0`）。

## 2. 127 个失败的首帧归因（逐条统计）

| 首帧 | 数量 | 性质 |
|---|---:|---|
| `System.Security.AccessControl.Win32.SetSecurityInfo` | 93 | 环境：ACL 写入被拒 |
| `NewManga.Host.Tests.SourceReattestTests.RepoWorkspaceRoot` | 24 | 环境：仓库根发现失败 |
| `NewManga.App.Tests.NoDbOsAccessTests.get_RepoRoot` | 4 | 环境：仓库根发现失败 |
| `System.IO.FileSystem.RemoveDirectoryRecursive` | 3 | 环境：目录删除（同 ACL 族） |
| `NewManga.Host.Tests.SourceRegistryTests.FindRepository` | 2 | 环境：仓库根发现失败 |
| `NewManga.Host.Tests.Fea11SourceIpcTests.RepositoryRoot` | 1 | 环境：仓库根发现失败 |
| **合计** | **127** | **0 条产品断言回归** |

## 3. 机制证据（源码优先）

三处仓库根发现实现完全一致：从 `AppContext.BaseDirectory` 向上找 `.git`，找不到即抛错/断言：

- `apps/desktop-avalonia/tests/NewManga.App.Tests/NoDbOsAccessTests.cs:43-50`（`Assert.NotNull(directory)`）
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceReattestTests.cs:53-62`（`throw InvalidOperationException`）
- `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceRegistryTests.cs:1062-1066`

验收运行时工作目录是 `G:\CODEX\New Manga.workspace\FEA-15-ACCEPT-1\clean-tree\...`，**该副本不含 `.git`** → 依赖仓库根的 31 个用例必然失败；副本在 workspace 下继承受限 ACL → 依赖 ACL 写入的 93 个用例必然失败。两者均为运行环境产物。

## 4. 复跑证据（真实仓库，同一 HEAD）

| 运行 | 配置 | 结果 | 证据 |
|---|---|---|---|
| App.Tests | Debug/net9.0 | 0 failed / 889 passed / 11 skipped / 900 | `logs/dotnet-app-tests.log` |
| Host.Tests | Debug/net9.0 | 0 failed / 321 passed / 74 skipped / 395 | `logs/dotnet-host-tests.log` |
| **全量 8 项目** | **Release/net9.0** | **0 failed / 1875 passed / 109 skipped / 1984，`EXIT=0`** | `logs/dotnet-full-current.log` |

分项目（全量 Release）：Appearance 21、Presentation.Avalonia 72、ThemeEngine 253、DesignSystem 117、ApplicationCore 31、Host 321（skip 74）、CoreClient 171（skip 24）、App 889（skip 11）。

与登记基线对比：`RESIDUAL-CLOSEOUT-PLAN §11.4` 记 1691/0/96；`STATUS` 历史记 1804/0/107；**本次 1875 passed 高于两者，failed=0**。

## 5. 结论

1. 「.NET 127 failed」**不是产品回归**，而是验收运行环境（无 `.git` 的副本 + 受限 ACL）导致的脚手架失败；127 条已逐条归因，无一条落在产品断言上。
2. 在当前 `main`（`fa116ca23`）真实仓库、Release 配置下，8 个项目 **0 失败**，满足 DoD-Line §4 中 ".NET 不低于登记基线且无未归因失败" 的机检部分。
3. 本记录**不**改变 `FEA-15-ACCEPT-1` 的 `closed_with_limitations` 状态；该状态的解冻需独立 Review 与显式关闭记录（P3 处置）。

## 6. 限制

- 复跑为 net9.0 Release；未覆盖各测试项目的 gated/硬件类用例（`Host` skip 74、`CoreClient` skip 24 等由设计默认 skip，不构成失败）。
- `pytest` 侧仍有 16 个既有失败（`V1_COMMITMENT_MANIFEST:16` 登记），本记录不涉及。
- 首次全量尝试使用仓库根 `NewManga.sln` 报 `MSB1009`；实际解决方案为 `apps/desktop-avalonia/NewManga.sln`，已按正确路径重跑（过程留痕于本文件，不作为缺陷登记）。
