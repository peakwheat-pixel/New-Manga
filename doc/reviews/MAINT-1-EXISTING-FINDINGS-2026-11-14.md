# 既有开放缺陷登记（2026-11-14，接手会话新发现）

本文件只登记**本次工作新发现的、与当前卡无关的既有缺陷**，供 Gate 裁决引用。不改变任何既有 Task 状态、不替代矩阵。

## E-1：`HostCommandRegistry` 111 条命令中 21 条无 `HostDomainService` 覆盖

- **发现方式**：在 `CHAPTER-MANUAL-SORT` 期间启用真实 sidecar 跑 .NET 套件，
  `NewManga.CoreClient.Tests.Commands.CommandIntegrationTests.DomainServices_CoverEveryCommandExactlyOnce` 失败。
- **失败原文**：

  ```
  Assert.Equal() Failure: Values differ
  Expected: 111
  Actual:   90
  ```

  对应断言：`Assert.Equal(HostCommandRegistry.All.Count, services.Sum(s => s.Descriptors.Count));`
  （`apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:416-421`）
- **根因（已定位到域级，未逐条枚举）**：`HostCommandDomain` 有 8 个值
  （`Settings`/`Library`/`Region`/`Reader`/`Resource`/`Workbench`/`Drafts`/`SourceSync`，见
  `HostCommandRegistry.cs` 的 `ByDomain` 构建），而 `CommandIntegrationTests` 只构造
  **六个** `HostDomainService`（`Settings, Library, Region, Reader, Resource, Workbench`）。
  `Drafts` 与 `SourceSync` 两个域的命令（`SourceSyncNames` 计 15 条，加上 `Drafts` 域若干条，合计 21 条）
  没有被计入覆盖。
- **判别力**：`git stash` 暂存 `CHAPTER-MANUAL-SORT` 全部已跟踪改动后，在基线 `79606ea4a` 上跑同一测试
  —— **同样 111 vs 90 失败**。故与本卡无关。
- **为何此前未暴露**：该测试标注 `[SidecarFact]`；未设置 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 时 SKIP，
  历史全量记录多为无夹具模式，故长期以 SKIP 存在。
- **性质**：需要 DSH 裁决是「补两个 DomainService（Drafts/SourceSync 端口）」还是「该测试的正确断言应为
  '每个 domain 都有服务覆盖且无重复'」。两者都要动代码或测试口径，属范围决策，**不在本卡内**。
- **与 Gate 的关系**：属 Gate 条件 3（完整 GUI/Core/Host 流程矩阵）的直接输入 —— 21 条命令没有
  C# 端口服务，即这些命令在前端不可达/未投影。

## E-2：仓库内 sidecar 构建（2026-10-23）早于多条现行 wire 命令

- **事实**：`G:\CODEX\New Manga.workspace\task-envs\HOST-CORECLIENT-1\sidecar-copy` 与
  `apps/desktop/src-tauri/target/release/resources/core-sidecar` 内的 `core_service.exe` 等
  构建时间均为 **2026-10-23 19:21**。
- **影响**：`ReorderChapters`（`83e45cfe5`，2026-11-10）等此后新增/变更的命令不在该 sidecar 内，
  任何依赖真实 sidecar 的集成测试都会因命令缺失而失败或无法验证。
- **与 Gate 的关系**：Gate 条件 4（当前 commit 的 Windows 包）必须重新打包 sidecar；该缺口同时阻塞
  条件 3 的真实流程矩阵与 `CHAPTER-MANUAL-SORT` 的 AC3 集成验证。
- **当前环境阻塞**：重建需 PyInstaller；本环境 PyPI 不可达
  （`ERROR: Could not find a version that satisfies the requirement pyinstaller (from versions: none)`），
  且仓库内无既有 build venv。**这是"需要可获取的构建依赖"而非"需要用户实物"**，故不判 blocked，
  但须登记为环境限制。

## E-3：HostController 的部分写方法失败时不留错误码（本卡已就地修复其一）

- `ReorderChaptersAsync` 原本在 catch 分支直接 `return false`，不调用 `SetLastError`，导致 UI/日志
  无法区分"顺序非法"与"sidecar 太旧不认识命令"（本次 E-2 排查即因此多花时间）。
- 本卡已在该方法内补 `SetLastError(ErrorCodeOf(ex))` 与成功时 `SetLastError(null)`。
- **未覆盖的同类位置**：`HostController` 中其余仅 `return false` 的元数据写方法是否同病，未逐条核实；
  登记为待评估，不在本卡范围。
