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
- **根因（已精确到 21 条 = 15 + 6）**：
  - `Drafts` 域 **6** 条（`drafts_open`/`drafts_patch`/`drafts_prepare`/`drafts_apply`/`drafts_status`/`drafts_discard`，
    `HostCommandRegistry.cs:209`）由 **`HostCommandDispatcher` 的 switch 分支直接处理**
    （`HostCommandDispatcher.cs:882/889/896/904/910/924`），不经 `HostDomainService`。
  - `SourceSync` 域 **15** 条（`SourceSyncNames`，`HostCommandRegistry.cs:410`）同样由 dispatcher 直通
    （`HostCommandDispatcher.cs:346` 等）。
  - 15 + 6 = **21** = 111 − 90，与失败值完全吻合。
  - `CommandIntegrationTests` 只构造六个 `HostDomainService`（Settings/Library/Region/Reader/Resource/Workbench），
    断言却是"六服务覆盖**全部** `HostCommandRegistry.All`"。
- **性质**：不是"缺两个服务"，而是**测试断言与现行两通路架构不符**；`Drafts`/`SourceSync` 走 dispatcher
  是有意设计。因此修复方向是把断言限定为"六服务覆盖其各自域的每条命令 + 全局无重复 + 每个 domain 至少一条通路"，
  而非补造两个空壳服务。
- **判别力价值**：修好后该测试在夹具下可真实运行，并能抓住"新命令既不进服务也不进 dispatcher"的漏接线。
- **为何此前未暴露**：该测试标注 `[SidecarFact]`；未设置 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 时 SKIP，
  历史全量记录多为无夹具模式，故长期以 SKIP 存在。
- **与 Gate 的关系**：属 Gate 条件 3（完整 GUI/Core/Host 流程矩阵）的直接输入 —— 该断言坏掉意味着
  "命令可达性"这一层没有有效守卫。
- **判别力**：`git stash` 暂存 `CHAPTER-MANUAL-SORT` 全部已跟踪改动后，在基线 `79606ea4a` 上跑同一测试
  —— **同样 111 vs 90 失败**。故与本卡无关。
- **为何此前未暴露**：该测试标注 `[SidecarFact]`；未设置 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 时 SKIP，
  历史全量记录多为无夹具模式，故长期以 SKIP 存在。
- **性质**：需要 DSH 裁决是「补两个 DomainService（Drafts/SourceSync 端口）」还是「该测试的正确断言应为
  '每个 domain 都有服务覆盖且无重复'」。两者都要动代码或测试口径，属范围决策，**不在本卡内**。
- **与 Gate 的关系**：属 Gate 条件 3（完整 GUI/Core/Host 流程矩阵）的直接输入 —— 21 条命令没有
  C# 端口服务 —— 但这**不等于命令不可达**：`drafts_*` 由 `HostController.cs:3121-3263` 直接
  `commands.InvokeAsync`，`source_*` 经 `HostRuntime.cs:1275/1368` 等路径发出。准确表述是
  **"这 21 条未经 `HostDomainService` 覆盖，测试口径与生产分派方式不一致"**（r1 复核 F5 指出原表述过强）。

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

## E-4：阅读偏好只有"应用"没有"保存"入口（用户改了不落库）

- **事实**：`ReaderViewModel` 有 `ApplyReadingPreferencesAsync`（`ReaderViewModel.cs:146`，由
  `LoadAsync:273` 调用 ⇒ 偏好**应用**已接线）与 `SaveReadingPreferencesAsync`（`:175`）。
  但 `apps/desktop-avalonia/src/NewManga.App/**` 内**没有任何调用 `SaveReadingPreferencesAsync` 的地方**
  ——除 `ReaderReadingPreferencesTests` 直接驱动 VM 外，生产路径上它是死方法。
- **用户可见后果**：阅读器里的「单页 / 双页」「反向翻页」「放大 / 缩小 / 适合页面」只改 VM 内存状态，
  重启或重开书后回到 Core 里存的旧值。用户"改了设置却保存不下来"。
- **与 `L-R1-1` 的关系**：`L-R1-1` 的字面是"**偏好应用**/书签面板/整书进度/reset 确认"，四项
  逐项核实**均已实现**（书签面板/整书进度/reset 确认由 `MAINT-2-C1-BATCH-1` AC1 交付，
  `ReaderVisibleControlsTests` 4 项通过；偏好应用由 `LoadAsync` 调用）。故 `L-R1-1` 按字面可判关闭。
  **但"偏好持久化"是一个相邻且真实的新缺口，不能因为字面已满足就说这块没问题。**
- **建议**：开一张 UI 卡，把「单页/双页、方向、缩放」三处用户改动接到 `SaveReadingPreferencesAsync`
  （已有 partial-patch 语义，只需接入口），并加判别测试：控件操作后断言 `ReadingPreferencesPatch` 落到 Host。
- **性质**：用户可见缺陷，非数据损坏；与 `L-R1-1` 同功能面，**不计入条件 1 的 8 项**。

## E-5：`L-F1-3` 的"压测"仍未被替代物覆盖（边界测试 ≠ 压测）

- `MAINT-2-C1-BATCH-1` AC3 交付的是"FONT 大文件/并发导入的**边界测试**"（MET），
  而 `L-F1-3` 的原文是"大文件 / 并发 / 占用文件**未压测**"。
- 二者不是一回事：边界测试证明"不会错"，压测证明"在规模/并发下仍可接受"。
  故 `L-F1-3` 的处置仍应是 `KEEP-NOTRUN`（已由条件 1 裁决给出重开条件），
  **不得用 AC3 的 MET 声称 L-F1-3 的压测已完成**。

