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

### 进展（2026-11-15，`PIPE-EXCLUSIVE-TRANSPORT-1`）

**已修**：① `HostBridgeClient` 管道现在有独占（传输层 `AcquireExchangeLeaseAsync` 租约，两处调用点全覆盖）
+ 数字 `id` 校验；② `CoreServiceClient.SendRawAsync` 现在持 `_pipeGate`。
两条管道的并发判别都有测试，**均能回退变红**。带新 sidecar 的 Host 失败从 9 降到 1。

**仍未修（本 E-7 的开放部分）**：
1. `CoreServiceClient` 仍用自己的 `_pipeGate`，**未**改用传输层租约；`ExchangeAsync` 仍 `public`
   ⇒ 未来任何直调即绕过独占（AC1 PARTIAL / AC2 NOT MET）；
2. 无 `request_id` 时仍 **fail-open**；bridge 仅校验**数字** id（AC4 后半 NOT MET）；
3. **R-002**：id 错配后无重同步，流中可能残留一帧（AC5 NOT MET）；
4. **R-005**：取消（`CancellationToken`）后流状态可能永久失步；
5. `Dispose`/`StopAsync` 在租约外，在途命令会得 `ProcessExited`。

⇒ **"并发安全"仍不可宣称**。上述 1–5 应作为后续卡的验收项。

### 与 Gate 的关系

不影响条件 1–6 的判定口径；但它是**数据正确性**类缺陷的同类风险，修复前不应宣称"并发安全"。
## E-8：V2 Studio 页面成批 XAML 绑定错误（2026-11-15，`INSTALLER-MATRIX-1` 首次真实启动发现）

**严重度：P2（静默 UI 失效，不影响数据）。**

安装后启动的 `startup.log` 出现 6 条以上绑定错误，全部指向 `NewManga.App.ViewModels.V2.Studio.StudioPageViewModel`：

```
[Binding] An error occurred binding 'IsEnabled' to 'IsEnabled' at 'IsEnabled':
  'Could not find a matching property accessor for 'IsEnabled' on '...StudioPageViewModel'.'
[Binding] An error occurred binding 'Text' to 'ActiveTabLabel' at 'ActiveTabLabel':
  'Could not find a matching property accessor for 'ActiveTabLabel' on '...StudioPageViewModel'.'
```

### 性质

VM **没有** `IsEnabled` / `ActiveTabLabel` 属性，XAML 却绑定它们 ⇒ 这些控件在运行时**不会**反映状态
（按钮启用态与标签文案静默失效）。**不抛异常、不黑屏**，所以很容易漏掉。

### 为什么现在才发现

headless UI 测试**不读** `startup.log` 的绑定诊断；此前也没有在**打包产物**上做真实启动并检查该日志。
这是"打包产物验证"带来的新发现 —— 也正是条件 4 存在的意义。

### 建议

单独建卡：①在 `StudioPageViewModel` 补齐缺失属性（或用 `AvaloniaProperty`/`StyledProperty` 适配）；
②**加一个能固定住的测试**：解析 `startup.log`（或订阅 Avalonia 的 binding-error 事件），
一旦出现 `[Binding] An error occurred` 就失败 —— 这样同类问题今后不会静默复发。
## E-9：source 恢复路径把 **registry root 目录** 当成**容器文件**（P2，2026-11-15 定位）

**严重度：P2（恢复路径对非 folder 来源必然失败）；证据：完整调用栈 + 代码 + 实测异常。**

### 现象

`Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved` 失败：

```
SourceAccessException : SOURCE_ENTRY_MISSING
---- System.UnauthorizedAccessException : Access to the path
     'G:\CODEX\New Manga.workspace\FEA-11\fixtures\r4a-production-<guid>' is denied.
```

**被拒绝的是 fixture 的 root 目录**，不是 `source-v2.zip`。

### 调用链（实测堆栈）

```
DescribeContainer ← IssueLockedAsync ← IssueAsync ← IssueForRecoveryAsync
  ← SourceOperationCoordinator.MintRecoveryGrantsAsync ← AcknowledgeAsync
  ← HostRuntime.SourceOperationCompletionAsync ← HostCommandDispatcher.InvokeHostControlAsync
```

### 根因

`SourceOperationCoordinator.MintRecoveryGrantsAsync`：

```csharp
var roots = live.Roots.Where(root => root.Readable).Select(root => root.Root).ToArray();
// R-r2-03: exactly one readable root, otherwise the source path would be guessed.
if (roots.Length != 1) throw new SourceAccessException("SOURCE_ACCESS_DENIED");
var grantId = await readsCoordinator.IssueForRecoveryAsync(
    baseline.RegistryId, live.Generation,
    roots[0],        // <-- registry root（目录）
    sourceKind,      // <-- "zip"
    ...);
```

`roots[0]` 是"允许访问的根目录"，**不是容器文件路径**。
`sourceKind == "folder"` 时碰巧成立；`zip`/`cbz`/`pdf`/`image` 时 `DescribeContainer(目录)` 必然失败。

**注释点出了风险（"path would be guessed"），但"恰好一个 root"解决不了语义错位。**

### 建议

恢复应使用**记录下来的容器路径**（journal / plan materialization），而不是 registry root；
若确无权威来源，应 typed 拒绝而非猜目录。**未实施**（需 DSH 裁决权威来源）。

### 与 Gate 的关系

不属条件 1 的 8 项；属**条件 3 带 opt-in 面**的真实产品缺陷，且是"恢复"这种数据安全相邻路径。
### E-9 进展（2026-11-15，`E9-RECOVERY-PATH-FIX-1`）

**已实施 typed 拒绝**：`MintRecoveryGrantsAsync` 在 `sourceKind != "folder"` 时抛 `SOURCE_PLAN_UNAVAILABLE`
（此前是 `roots[0]` 目录 → `UnauthorizedAccessException` → 被兜底成 `SOURCE_ENTRY_MISSING`）。

**查询结论**：`JournalEntry`（16 字段）、`AuthorizationJson`（只解析 registry_id/identity_digest/generation）、
`SourceSyncPlanMaterialization`（11 字段）**都没有容器路径** ⇒ 无权威路径可改用。

**效果**：错误码从误导性的 `SOURCE_ENTRY_MISSING` 变为准确的 `SOURCE_PLAN_UNAVAILABLE`；
**但 `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_…` 仍失败** —— 它期望恢复**成功**，
而无权威路径时成功不可能。**本卡没有让它转绿**。

**真修需要 UNFREEZE**：在持久化位置记录容器路径（journal 的 AuthorizationJson 或 plan materialization）。
这属契约变更，需 DSH 裁决载体与兼容性。

**未做**：无专门的 typed 拒绝判别测试（`MintRecoveryGrantsAsync` 为 private）；未实测 folder 类恢复仍正常。
### E-9 载体可行性核实（2026-11-15，`E9-PATH-CARRIER-STUDY-1`）

Codex 被要求裁决"journal（A）vs Core plan（B）"，但其命令因 Windows 740 无法启动，**未读到代码**，
只给出"倾向 A"的**有条件**意见并列了 4 项待核实条件。DSH 已补齐：

| 项 | 结论 |
|---|---|
| 载体 | journal 表列 `authorization_json TEXT`（Host 内部持久化，非 wire） |
| `RequestDigest` | `sha256({operation_id, plan_id, plan_digest, kind})` —— 不含 authorization 结构 |
| `minted.AuthorizationDigest` | `sha256(canonical(authorizations[]))` —— 外层字段不在范围 |
| **`Authorize()` 的 `AuthorizationDigest`** | **`Sha256Hex(整个 JSON)`** —— **加外层字段会变** |
| `AuthorizationDigest` 校验点 | **全仓无**（只写不验） |

**★ 关键发现**：两个写入点对 `AuthorizationDigest` 用了**不同定义**（`:425` 用 minter 的，
`:152` 用整 JSON 的 sha256）。

**结论**：A 可行，但**"塞进 `authorizationJson`"会改变 `:152` 的摘要语义** ——
更小风险的等价方案是 **journal 表新增独立列 `container_path TEXT NULL`**，完全不碰既有 JSON、
摘要与消费者。**本卡未实施**，待 DSH 冻结范围。
### E-9 路径可得性核实（2026-11-15，`E9-PATH-AVAILABILITY-1`）

**结论：六个 journal 写入入口全都没有容器路径。**

| 入口 | 签名/上下文 | 有路径？ |
|---|---|---|
| `SourceOperationCoordinator.Begin` | `(planId, planDigest, kind, requestDigest, operationId?, grantIds?)` | **无** |
| `SourceOperationCoordinator.Authorize` | `(operationId, authorizationJson, hostReceiptId)` | **无** |
| `MarkCommitted` | 只带 receipt | **无** |
| `HostOperationOrchestrator` 的 `payload` | 只读 `authorization` / `grant_ids` | **无** |
| `registryAuthorizations[]` | `registry_id` / `generation` / `identity_digest` | **无** |
| `HostAuthorizationMinter.Mint` | 只接收上述 authorizations | **无** |

唯一知道路径的是 `SourceReadCoordinator.IssueLockedAsync` 的 `sourcePath`（Run 授权链，`:564`），
与 operation journal 之间**没有传递通道**。

**因此 E-9 只剩两个选项**：
1. **扩 Core**（scan target 或 plan materialization 加容器路径）—— 改 wire 契约，且**跨职责**
   （Host 的授权材料搬进 Core）；
2. **接受为能力限制**—— 保持 typed 拒绝，并在文档/UI 明确"仅 folder 来源支持崩溃恢复"。**零代码**。

**DSH 技术判断倾向 2**（成本收益不成比例），但**这是产品取舍**（是否限制 zip 来源的崩溃恢复能力），
按 goal 应派 codex/zcode 裁决；上一轮 codex 因 Windows 740 无法读代码，**该裁决尚未作出**。

**E-9 状态更新**：从"待修的 P2 缺陷"调整为 **"已定位、修复路径受产品裁决阻塞的能力限制"**。
typed 拒绝已使失败**可解释**（`SOURCE_PLAN_UNAVAILABLE` 而非误导性的 `SOURCE_ENTRY_MISSING`）。
### E-9 产品裁决（2026-11-15，ZCode，`E9-PRODUCT-ADJUDICATION`）

**裁决：B（接受为能力限制）**。A（扩 Core）**任何时点都不采**。登记**第三方案**为后续解锁候选。

#### ★ 三处对 DSH 的纠正

1. **影响面被 DSH 低估**：不止"崩溃恢复"—— **`AcknowledgeAsync:468` 与 `RecoverAsync:581` 走同一 fresh re-mint**，
   故 **zip/cbz/pdf/image 的 sync 完成链（含正常 ACK）整体不可用**；ACK 失败 → gate 停 pending
   （`source_sync.py:150`）→ 新 binding 不可读。
2. **A 的成本被 DSH 低估**：Core `source_locations` **刻意只存物理 facts**（`volume_serial`/`file_id`/`size_bytes`，**无路径列**）；
   A 不是"暴露已有列"，而是 **Core 新接收并持久化 Host 授权材料** → **路径双权威必漂移**。
3. **DSH 设想的"`JournalEntry` 加字段"同样受阻**：journal closed shape 冻结、**禁绝对路径**（`SourceOperationCoordinator.cs:22-23`，C-17 §5.2）。

#### 测试口径（DSH 须执行）

改为**断言 typed 拒绝**，**不 skip**（保留 scan/plan/apply 段的 wire 级覆盖）。三断言：
①精确码 `SOURCE_PLAN_UNAVAILABLE`；②journal 状态保持 `core-committed` **无损**；③重复 ACK **幂等同拒**。

**是否放宽**：**形式收紧、实质是能力边界重新声明** —— 旧"acknowledged"期望**从未可达**
（修复前同样失败，只是错误码被兜底成 `SOURCE_ENTRY_MISSING`），**不属放宽断言**；
但**须显式留痕**（含解锁条件 + 测试名标记 `KNOWN-LIMITATION-E9`），**禁止静默改绿**。

#### 最小产品动作：**仅文档**

"非 folder 来源 sync 完成（ACK/恢复）暂不可用，typed 拒绝 `SOURCE_PLAN_UNAVAILABLE`；
解锁路径 = **mint-time 路径映射**"（`IssueLockedAsync` 手中已有真实路径 → Host 侧 DPAPI 映射
`registry_id`→`container_path`，恢复时取候选路径、身份仍经 `IssueAsync` 全量物理 facts 验证）。
**不做导入 UI 提示** —— sync UI 入口尚不存在，无载体。

#### 保留给用户

1. 近期若上**非 folder 来源的书架重同步**，B 即**挡路项**，应提前释放路径映射 Task；
2. 接受 B 的安全前提：**数据无损边界** —— 只挡"读门打开"，**无业务数据损坏**。

#### DSH 采纳

**采纳**。待执行：测试三断言 + `KNOWN-LIMITATION-E9` 标记 + 本口径落 C-17/FEA-11 已知限制。
#### E-9 已知限制登记（`E9-LIMITATION-DOC-1`）

限制的正式登记入口：**`doc/reviews/E9-KNOWN-LIMITATION-REGISTER.md`**。

**未改 C-17**：`doc/plan/FEA-CONTRACT-FROZEN-C17.md` 被 pin 覆盖
（附录自陈三指纹与 `truth 17 OK + C17 OK = 18/18`；`verify_pins.ps1` 动态构造
`doc/plan/FEA-CONTRACT-FROZEN-$id.md`），改它会使 18/18 变红。

本限制**不需要改契约语义**（契约要求"恢复需要容器路径"，产品只是暂时无法提供），
故用独立登记文件承载，**不动冻结字节**。

登记文件内含：真实口径（**含正常 ACK**，不是"仅崩溃恢复"）、数据安全边界、
解锁条件（mint-time DPAPI 路径映射）、被挡住的测试名、以及四处引用。
