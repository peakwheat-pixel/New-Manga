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
## E-6：`list_chapters` 间歇返回空（被 E-2 掩盖的既有竞态，2026-11-15 由 `SIDECAR-REBUILD-1` 暴露）

**严重度：P1（已确证，2026-11-15 第七轮诊断）。根因明确，证据为 wire 帧的 request_id 错配。**

### 现象（可复现）

- `HostReaderChaptersIntegrationTests.ListChapters_MatchesReaderProjection` 在
  `:47 Assert.NotEmpty(chapters)` 处失败（`chapters` 为空），**两个测试单独跑都通过、连跑时交替失败**：
  - 连跑①：`ConcurrentChapterAndProjectionReads_AreSerialized` 失败（`Assert.Single` 空）
  - 连跑②：`ListChapters_MatchesReaderProjection:47` 失败
- 仅在**新 sidecar**（2026-11-15 重建）下出现；旧 sidecar 时代这两测试是 **SKIP**（E-2）⇒ **缺陷一直存在，只是从未执行**。

### 已排除（均有证据，见 `verification/SIDECAR-REBUILD-1/README.md` §7–§13）

| 假设 | 结论 |
|---|---|
| sidecar 有问题 | **排除**：wire 帧显示该 session 的 `list_chapters` 返回了 1 个 chapter；`errors: {}`；`core_service.stderr.log` 无 error |
| 数据根/参数传错 | **排除**：Host 用 `NEWMANGA_DATA_ROOT`（`CoreServiceClient.cs:499`）；`--data-root` 从来不被 sidecar 支持 |
| namespace re-bind | **排除**：`_ensure_preview_namespace` 只处理 preview/derived catalog |
| xunit 并行 | **排除**：两项目均已 `DisableTestParallelization = true` |
| 残留进程 | **排除**：连跑后无 `core_service` 进程 |
| 客户端串帧（gate 缺失） | **排除**：`HostRuntime._readerIoGate`（`:34`）覆盖 `ListChaptersAsync`（`:511`）**与** `GetReaderProjectionAsync`（`:784`） |

### ★ 根因（已确认）

失败 session 的 wire 最后一帧：
```
# 6  REQ list_chapters req-7  → RESP req-6  result: {"targets": []}
```
**`list_chapters`(req-7) 读到了 `source_list_scan_targets`(req-6) 的响应** ⇒ 解析器找不到 `chapters`
⇒ 静默返回空 ⇒ `Assert.NotEmpty` 失败。

三方同时成立：
1. `SidecarProcess.ExchangeAsync`（`:186-240`）**无锁**，假定"一次只有一个请求在途"；
2. `HostRuntime._readerIoGate` 只覆盖 reader 类方法（`:511/527/543/559/576/784`）；
3. **漏洞**：后台 source 扫描**直接调 `CoreServiceClient`，不经过 gate** ——
   `SourceScanScheduler.cs:2415`、`SourceOperationCoordinator.cs:219`。

另：`CoreServiceClient.SendAsync` **不校验响应的 `request_id`**，这是它能"静默错配"的直接原因。

### 建议

单独建卡 `LISTCHAPTERS-EMPTY-RACE-1`：在 `ListChaptersAsync` 解析前临时打印 `result.GetRawText()`，
连跑复现，据输出判定是"事件帧循环吃掉响应"还是"解析 bug"；修复须附**回退后测试变红**的判别证据。
**不得**用放宽断言、跳过测试或降低覆盖来"解决"。

### 与 Gate 的关系

不属于条件 1 的 8 项（那 8 项是审计 finding）。它是 E-2 解除后暴露的**产品级缺陷候选**，
在定位前不影响 Gate 判定口径，但**构成条件 3/4 的真实性证据**：真实 UI 同时读章节与投影可能空显示。
## E-7：`E-6` 修复后仍有 4 处同型"管道并发"窗口（2026-11-15，`CORE-PIPE-EXCLUSIVE-1` r1 复核发现）

`CORE-PIPE-EXCLUSIVE-1` 已给 **core_service 管道**加了全局独占（`CoreServiceClient._pipeGate`）并加了
`request_id` 校验，实测 `Host` 失败 9→2~3。但 r1 复核指出**同类窗口还有 4 处**：

| # | 窗口 | 位置 | 性质 |
|---|---|---|---|
| 1 | `HostBridgeClient` 的管道**完全无锁**，且 `ParseResponse` 从不校验 id | `HostBridgeClient.cs:269/291` | 与 core_service 同型的第二条管道 |
| 2 | 公开 `SendRawAsync` 直调 `_process`，绕开 `_pipeGate` | `CoreServiceClient.cs:2384` | 锁覆盖不全 |
| 3 | 独占加在 `CoreServiceClient` 而非**传输层**，今后任何直调 `_process` 的代码天然在锁外 | `Transport/SidecarProcess.cs` | 架构性 |
| 4 | 响应**无 `request_id`** 时校验 fail-open | `CoreServiceClient.EnsureResponseBelongsToRequest` | 已知限制，已由文档测试固定 |

另有 r1 指出的 **R-002**：错配抛错后管道可能**残留一帧**（off-by-one），无重同步。

### 建议

单独建卡 `PIPE-EXCLUSIVE-TRANSPORT-1`：把独占**下沉到 `SidecarProcess.ExchangeAsync`**
（连同事件帧窗口一起，用"进入时取锁、整周期释放"的模式），并给 `HostBridgeClient` 加等价保护与 id 校验；
同时处理 R-002 的 off-by-one（错配后丢弃直到 id 匹配）。

### 与 Gate 的关系

不影响条件 1–6 的判定口径；但它是**数据正确性**类缺陷的同类风险，修复前不应宣称"并发安全"。
