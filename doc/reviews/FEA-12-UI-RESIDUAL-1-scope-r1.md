---
task: FEA-12-UI-RESIDUAL-1
title: FEA-12-UI-RESIDUAL-1 独立 scope review r1（四项 P3 残余的最小冻结面与可测缺口）
reviewer: fresh subagent（独立上下文；未参与实现；只读）
session: bfb8f132-06a5-4805-85cf-4a0b725e759f（DSH fresh subagent）
parent_session: session-c2883c5f-dcf8-400d-b161-9c84f562486a
reviewer_kind: subagent
date: 2026-11-06
repo: G:\CODEX\New Manga
branch: main
worktree: clean
reviewed_head: 57f62b3fe
verdict: READY-TO-FREEZE
---

# FEA-12-UI-RESIDUAL-1 Scope Review r1（独立只读）

> **结论先行：`READY-TO-FREEZE`（仅按“App 侧四项残余”解释）。**
>
> - 四项候选全部可落在 `apps/desktop-avalonia/src/NewManga.App/**` 与 `NewManga.App.Tests/**`，**不需要** Core/Host wire、能力表、schema、依赖或任何冻结契约字节变更；`IHostController`/`ITrashController` 签名也无需改。
> - 逐项现状不是“四项都只是缺测试”：①delete-time `CORE_CAPABILITY_MISSING` 分支存在但**生产不可达**且目前会错误地把页级标成 missing；②preview `BOOK_NOT_FOUND` **未实现自动刷新**；③cleanup retry `BOOK_NOT_FOUND` 分支存在，但“提示已不存在”的文案会被 `ResetPreview()` 清掉且没有 `_notify`，**只补测试会红**；④只读 banner 在能力缺口时被**有意抑制**，需要先冻结“两个独立事实是否同时展示”的文案规则，不能只加断言。
> - 因此冻结时必须带上 4 个口径：①第 1 项只做 **defensive invariant**，不得声称生产可达，也不得顺手给 delete 命令加 Host 能力门；②第 3 项包含最小 `_notify` 修复，不是纯测试卡；③第 4 项冻结“Host 只读 + 能力缺口 = 同时展示两个独立原因，且只读文案不得在 read 缺失时声称可浏览”；④写域严格限定为 `TrashViewModel.cs` + `TrashUiTests.cs`，XAML/Fake/契约/Host/Core 一律不动；若实现需要触碰，停下请 DSH 增列 `allowed_paths`（SCAN-2 P2-4 先例）。
> - 不建议 UNFREEZE。若 Lead 想让 delete-time `CORE_CAPABILITY_MISSING` **生产可达**，那是 Host/Core 能力门的新增（`HostCommandRegistry.RequiredCapabilities` + `HostRuntime` + 可能的能力矩阵说明），应另卡/另行契约审查，不能塞进本 P3 收尾卡，否则本卡应判 `BLOCKED` 的那一部分。

---

## 1. 只读核验基线（review 时点）

| 项 | 事实 | 证据 |
|---|---|---|
| 分支 / 工作树 | `main` / clean（无 modified/untracked；review 写入本报告前） | `git status --porcelain` |
| 任务基线 | `57f62b3fefb98a1c298358adce7fc7d0f3e52aa5`（任务给定基线） | `git rev-parse HEAD`（review 启动时） |
| 复审时实际 HEAD | `690c77eb0c95b9eb764923468fedae501468159f`（Lead 在 review 开始后追加 `docs(fea-11-rendition-1): 回填 push 记录`） | `git rev-parse HEAD`、`git log -1` |
| HEAD 漂移内容 | 仅 3 个 docs 文件、3 行：`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/FEA-11-RENDITION-1.md`；**代码/测试树与 57f62b3fe 等价** | `git diff --name-only 57f62b3fe..690c77eb0`、`git diff --stat` |
| .NET 基线 | **1527 passed / 0 failed / 86 skipped**（8 项目：21+38+253+117+31+185+167+715=1527；skip=86；2026-11-06 实测） | `doc/STATUS.md:20`；`doc/tasks/FEA-11-RENDITION-1.md:125,134,220`；reviewer 未重跑全量 |
| pytest 基线 | **3249 passed / 10 skipped**（RENDITION-1 closeout 实测；`pytest tests/fea11` 145） | `doc/tasks/FEA-11-RENDITION-1.md:125,134,220`；注意 `doc/STATUS.md:20` 仍写 3212/10（见 §9 P3） |
| pins | **18/18 PASS** | reviewer 实跑 `pwsh -NoProfile -File tools/governance/verify_pins.ps1` |
| 治理检查 | **PASS（3 warnings）** | reviewer 实跑 `pwsh -NoProfile -File tools/governance/check.ps1`；warning 为 9 个非终态 Task、STATUS/PLAN 预算 80% |
| API inventory | **PASS（exit 0，`OK: rendered counts match FEA-C07 doc`）** | reviewer 实跑 `python tools/generate_api_inventory.py --check` |
| 定向 UI 测试 | **35/35 passed（TrashUiTests，73 ms，`--no-build`）** | reviewer 实跑 `dotnet test ... --filter FullyQualifiedName~TrashUiTests` |
| FEA-12-UI 终态 | `done`；delivery/integration `a46d4d5c7`；AC1–AC10 全 MET；L3 真机 `NOT_RUN`；P3 follow-up ①–④ 登记于 closeout | `doc/tasks/FEA-12-UI.md:284-289` |
| 占位卡 | `proposed`；`allowed_paths` 目前只有本卡/Review/Handoff/evidence（**无生产代码**），`out_of_scope` 含生产实现 | `doc/tasks/FEA-12-UI-RESIDUAL-1.md:6,21-27` |
| 当前候选指针 | 无活动 Task；下一候选 `FEA-12-UI-RESIDUAL-1`（proposed，需先 scope review） | `doc/STATUS.md:7`；`doc/REBASELINE_PLAN.md:19,53`；`doc/TASK_LEDGER.md:45` |

> 说明：HEAD 在 review 期间从 `57f62b3fe` 前进到 `690c77eb0`，仅 docs 变更；本报告所有代码/测试事实在两者之间**树等价**。释放时 `base_commit` 仍应由 DSH 按释放时 HEAD 重新固定，不能直接沿用 `57f62b3fe` 或 `690c77eb0`。

本 review 未修改生产代码/测试/契约/STATUS/PLAN/LEDGER/证据，未 commit/push；唯一写入是本报告文件。

---

## 2. 四项候选逐项核验（现状—缺口—最小改动）

### 2.1 ① delete-time `CORE_CAPABILITY_MISSING` 防御边

**现状事实**

| 事实 | path:line |
|---|---|
| `TrashViewModel` 在删除结果为 `CapabilityMissing` 时，设置 `_capabilityMissing = true`、`_capabilityMessage = "Core 未公布删除能力…"`，并 `RaiseStates()` | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/TrashViewModel.cs:769-777` |
| 该结果由 App 侧 `HostController` 对 Host/Core 错误码的映射产生：`TrashErrorCodes.CapabilityMissing → TrashDeleteOutcome.CapabilityMissing` | `apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs:3071-3088` |
| Host 的删除/回收站能力门**没有**覆盖 `library_delete_book_permanently`：`RequiredCapabilities` 只映射 preview/list/move/restore/purge，无单本 delete | `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs:94-101` |
| HostRuntime 只在 `RequiredCapabilities(name).Count > 0` 时调用能力门；delete-permanently 因此不 probe | `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs:1149-1158` |
| CoreClient 测试的 capability-gated 命令集合同样**不含** `library_delete_book_permanently` | `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:605-613,630-647` |
| Core 的 `PermanentlyDeleteBook` handler 没有 `CORE_CAPABILITY_MISSING` 分支；旧 Core 对未知命令返回 `UNKNOWN_COMMAND`，App 映射为 `Unknown` 而非 `CapabilityMissing` | `src/bootstrap/core_service.py:2345,6215-6218`；`HostController.cs:3086` |
| 现有测试没有 delete-time capability 用例；只有 Enter/probe 时的能力测试 | `apps/desktop-avalonia/tests/NewManga.App.Tests/TrashUiTests.cs:132-160,514-602` |

**可达性判定：生产不可达（当前 Host/Core 都不会在 delete-time 发 `CORE_CAPABILITY_MISSING`）。** 该分支目前只能由 fake 注入或未来 Host 增加能力门/Core 改变行为后才会出现。但当前行为有真实危害：一条删除命令的返回码会把**已经成功读取的列表**整页替换成 read 能力缺失态（`ShowCapabilityState=true`、`ShowList=false`），并把原因写成“Core 未公布删除能力”，与 `read` 能力无关。这是 AC7⑤“按操作禁用、不因一个能力缺失禁用全部”的潜在违反。

**缺口**

1. 页级 `_capabilityMissing` 被 delete 结果污染；`_capabilityMessage` 也覆盖了 read 侧的 typed 文案。
2. 无测试把“删除返回能力缺失 ≠ read 能力缺失”钉住。
3. Host/Core 侧的可达性问题（是否给 delete-permanently 加能力门）不在 App 写域；本卡不解决、也不得声称解决。

**最小改动（App-only）**

- 在 `TrashViewModel.ConfirmDeleteAsync` 的 `CapabilityMissing` 分支：
  - **不再**设置 `_capabilityMissing` / `_capabilityMessage`；
  - 保留 `_deleteOutcomeCode = result.Code`、`_deleteResultTitle = "删除被拒绝"`、`_deleteOutcomeText` 含 `CORE_CAPABILITY_MISSING` 与“未删除任何内容/可刷新重新探测”；
  - 用 `_previewBlockedReason`（或等价状态）使 `CanConfirmDelete=false`，防止用户对同一预览连续重试；面板保留，显示 typed 结果与关闭按钮；
  - 不改变 `_writeAvailable/_previewAvailable`（没有新 probe 就不推断），列表保持真实；用户可用既有“刷新”重新 probe。
- 只改 `TrashViewModel.cs`；不需要 `HostController.cs`/`TrashModels.cs`/XAML 改动。

**判别测试（新增于 `TrashUiTests.cs`）**

`Delete_CapabilityMissing_DoesNotTurnThePageIntoReadCapabilityMissing`：

- Enter → Begin preview → `UnderstandIrrecoverable=true` → 注入 `ScriptedTrashDeletes` 为 `CapabilityMissing/CORE_CAPABILITY_MISSING` → Confirm；
- 断言：恰好 1 个 delete 帧；`Items.Count` 仍为 2；`ShowList=true`；`IsCapabilityMissing=false`；`ShowCapabilityState=false`；`DeleteOutcomeCode=="CORE_CAPABILITY_MISSING"`；`DeleteResultTitle=="删除被拒绝"`；`IsPreviewOpen=true`；`CanConfirmDelete=false`；无成功提示；
- 变异：恢复 `_capabilityMissing=true` → `ShowList`/`Items` 断言红；把分支落入 default → `DeleteResultTitle` 红。

### 2.2 ② preview `BOOK_NOT_FOUND` 自动刷新

**现状事实**

| 事实 | path:line |
|---|---|
| `BeginPermanentDeleteAsync` 在 preview 失败时只设置 `_previewErrorCode/_previewErrorMessage`，不做 code 分支、不 `_notify`、不 `ReloadAsync` | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/TrashViewModel.cs:634-649` |
| 面板会显示错误与“重新预览”按钮（就地提示存在，但重新预览仍会失败；列表不刷新） | `RecycleBinView.axaml:158-165` |
| `ReloadAsync()` 已存在，且会 `ResetTransientState()` + 重新 probe/list | `TrashViewModel.cs:390-400` |
| AC4 明文要求 `BOOK_NOT_FOUND → 提示并刷新` | `doc/tasks/FEA-12-UI.md:135` |
| 现有测试只覆盖 delete-time `BOOK_NOT_FOUND`，不覆盖 preview 失败 | `TrashUiTests.cs:326-341`；preview 失败测试 `:208-241` 只覆盖 old Core/current 缺失与 `BOOK_BUSY` |

**缺口：未实现 AC4 的“刷新”半边。** 当前“提示”是面板内就地错误；用户必须手动点“刷新”才会移除已不存在的行。`BOOK_NOT_FOUND` 的失败分支没有归类，浪费了 typed code 的可用信息。

**最小改动（App-only）**

- 在 preview 失败块内先判断 `string.Equals(preview.Code, TrashErrorCodes.BookNotFound, StringComparison.Ordinal)`：
  - `_notify("作品已不存在（BOOK_NOT_FOUND）：已刷新回收站列表", NmStatus.Failed)`；
  - `ResetPreview()` 关闭披露面板（目标已不存在，保留面板会形成幽灵上下文）；
  - `await ReloadAsync()`，让列表刷新并更新 `Items`；
  - 不发送任何 delete 帧，不自动重试 preview。
- 与 delete-time `NotFound` 的现成处置（`TrashViewModel.cs:754-759`）保持同一口径/文案。
- 只改 `TrashViewModel.cs`。

**判别测试**

`Preview_BookNotFound_ClosesPanel_AndReloadsTheList`：

- Enter 后，将下一页脚本设置为只含 `book-1`（模拟已删作品不再返回）；再注入 `ScriptedTrashPreviews` 为 `TrashPreviewResult.Failure(BOOK_NOT_FOUND, "gone")`；
- `await trash.BeginPermanentDeleteAsync(trash.Items[0])`；
- 断言：`library_list_trash` 恰 2 帧（初始 + 刷新）；`Items.Count==1` 且只剩 `book-1`；`IsPreviewOpen=false`；notice 含 `BOOK_NOT_FOUND` 且含“已刷新”；delete 帧 0；probe 2 次（初始 + `ReloadAsync` 重新探测）；
- 变异：删除 `ReloadAsync` → list 帧 1/Items 2 红；删除 `_notify` → notice 红。

### 2.3 ③ 第二次 cleanup retry → `BOOK_NOT_FOUND` 有实现无测试

**现状事实**

| 事实 | path:line |
|---|---|
| `RetryCleanupAsync` 对非 `Deleted` 结果设置 `_cleanupPendingVisible`、`_deleteOutcomeCode/_deleteOutcomeText`；`NotFound` 时先 `ResetPreview()` 再 `ReloadAsync()` | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/TrashViewModel.cs:792-832`（NotFound 分支 `:820-829`） |
| NotFound 的 `_deleteOutcomeText = "清理重试：条目已不存在，已刷新列表"` 在 `:822-824` 设置 | `TrashViewModel.cs:822-824` |
| 紧接着 `ResetPreview()` 在 `:827` 调用；它把 `_deleteOutcomeCode/_deleteOutcomeText/_deleteResultTitle` 清空 | `TrashViewModel.cs:897-920`（`:912-914`） |
| 该分支没有 `_notify`；`RaisePreviewStates()` 在 `ReloadAsync()` 之后，字段已为空 | `TrashViewModel.cs:825-831` |
| 现有测试覆盖 pending→Deleted（同一 digest、1 次 preview）与关闭结果，但不覆盖 pending→pending→NotFound | `TrashUiTests.cs:296-324,606-624` |
| AC6③ 要求“第二次重试 → `BOOK_NOT_FOUND` 且提示已不存在” | `doc/tasks/FEA-12-UI.md:137` |

**判定：不是纯“有实现无测试”。** 分支存在，但“提示已不存在”的用户可见文案实际被 `ResetPreview()` 清空，用户只看到列表刷新，没有 typed 提示。只补测试会按 AC6③ 变红；必须先做一个最小修复。

**最小改动（App-only）**

- 在 NotFound 分支、`ResetPreview()` 之前（或在 Reload 之后重新设置可见状态）加入：
  - `_notify("作品已不存在（BOOK_NOT_FOUND）：已刷新回收站列表", NmStatus.Failed)`；
  - 保持 `ResetPreview()` + `await ReloadAsync()` 的既有顺序；
  - 不保留幽灵结果面板；不自动重试，不新发 preview。
- 如果 Owner 选择保留结果面板，则必须在 Reload 后重新设置 `_deleteOutcomeText` 并断言可见；**不得**只设置后又被 `ResetPreview()` 清空。
- 只改 `TrashViewModel.cs`。

**判别测试**

`CleanupRetry_SecondRetryBookNotFound_NotifiesAndRefreshes_WithSameDigest`：

- Enter → Begin → understood → `ScriptedTrashDeletes` 依次：`CleanupPending` → `CleanupPending` → `NotFound`；
- Confirm → Retry → Retry；
- 断言：3 个 delete 帧；三次 `inventory_digest` **逐字节相等**（逐书 digest，不是集合 digest）；仅 1 个 preview 帧；2 个 list 帧（初始 + 刷新）；notice 含 `BOOK_NOT_FOUND` 与“已不存在”；`IsCleanupPending=false`；`CanRetryCleanup=false`；`IsPreviewOpen=false`；无成功提示；
- 变异：移除 `_notify` → notice 红；使用新 digest/集合 digest → digest 断言红；移除 Reload → list 帧 1 红。

### 2.4 ④ Host 只读 + 能力缺口时 `HOST_READ_ONLY` banner 被抑制的文案取舍

**现状事实**

| 事实 | path:line |
|---|---|
| `ShowHostReadOnlyBanner => _hostReadOnly && !HasCapabilityGap`：只要存在任一能力缺口就抑制只读 banner | `TrashViewModel.cs:190` |
| `HasCapabilityGap => _capabilityProbed && (!_readAvailable || !_writeAvailable || !_previewAvailable)` | `TrashViewModel.cs:158-159` |
| `HostReadOnlyBannerText` 固定写“回收站可浏览，但软删/恢复/彻底删除已禁用” | `TrashViewModel.cs:193-194` |
| `ShowCapabilityDegraded` 在 read 可用、write/preview 缺失时显示降级横幅 | `TrashViewModel.cs:226`；`RecycleBinView.axaml:78-81` |
| read 缺失时整页显示 `ShowCapabilityState` 的能力缺失态；只读 banner 位于其下方但被上面的公式抑制 | `TrashViewModel.cs:223`；`RecycleBinView.axaml:33-40,64-67` |
| 现有测试只覆盖单状态：仅 Host 只读、仅缺 read、仅缺 write、仅缺 preview、probe 失败；**没有**“Host 只读 + 任一能力缺口”的组合测试 | `TrashUiTests.cs:162-184,514-602` |
| AC7② 要求 Host 只读 ⇒ 写入口禁用 + `HOST_READ_ONLY` 原因；AC7⑤ 要求按操作禁用 | `doc/tasks/FEA-12-UI.md:138` |

**缺口：两个独立事实被互斥展示。** 当前抑制不是“假 banner”（r2 P1 已修：能力缺失不会伪造 Host 只读），而是**真实 Host 只读原因在组合态不可见**。能力缺口横幅只说明“Core 未公布某能力”，不能替代“Host 策略只读”；用户需要区分“升级 Core/换能力”与“Host 只读策略”两种处置。反过来，read 缺失时只读 banner 的“回收站可浏览”也会变成假话，因此不能简单去掉抑制。

**冻结规则（推荐）**

1. **两个独立原因，同时为真时同时展示**：`ShowHostReadOnlyBanner` 只由 `_hostReadOnly` 决定，不再被 `HasCapabilityGap` 抑制；
2. **只读 banner 文案不得声称“可浏览”**：去掉“回收站可浏览”分句，改为“不会执行任何写入；软删/恢复/彻底删除已禁用”，在 read 可用/不可用两种情况下都为真；
3. **能力横幅只谈能力**：`CapabilityGapMessage`/`CapabilityMessage` 不提 Host 只读；只读 banner 不提 `CORE_CAPABILITY_MISSING`；
4. 只有一种原因时只显示一种 banner（现有单状态行为不变）；probe 失败 + Host 只读时两者都显示（现状已允许，因为 `HasCapabilityGap` 在 probe 失败时为 false）。

**最小改动（App-only）**

- `ShowHostReadOnlyBanner => _hostReadOnly;`（`TrashViewModel.cs:190`）；
- `HostReadOnlyBannerText` 删除“回收站可浏览，”分句（`TrashViewModel.cs:193-194`）；
- 不改 `RecycleBinView.axaml`：两个 `AlertBanner` 已经独立存在，只是第二个之前被 VM 公式隐藏；XAML 结构无需变化。若 Owner 认为需要调整 XAML，必须先停下请 DSH 增列 `allowed_paths`。

**判别测试**

1. `HostReadOnly_PlusWriteCapabilityGap_ShowsBothIndependentCauses`：
   - `TrashCapabilities = new(true, true, false, true, CapabilityMissing, "缺 library.trash.write/1")`；`Snapshot with { WritesAllowed=false }`；
   - Enter → 断言 `IsHostReadOnly=true`、`ShowHostReadOnlyBanner=true`、`ShowCapabilityDegraded=true`、列表仍真实、`CanWrite=false`；`HostReadOnlyBannerText` 含 `HOST_READ_ONLY` 且不含 `CORE_CAPABILITY_MISSING`；`CapabilityGapMessage` 含 `CORE_CAPABILITY_MISSING` 且含 `library.trash.write/1` 且不含 `HOST_READ_ONLY`；
   - 变异：恢复 `&& !HasCapabilityGap` → `ShowHostReadOnlyBanner` 红。
2. `HostReadOnly_PlusReadCapabilityMissing_ShowsCapabilityStateAndReadOnlyReason`：
   - `TrashCapabilities = new(true, false, true, true, CapabilityMissing, "缺 library.trash.read/1")`；`WritesAllowed=false`；
   - Enter → 断言 `ShowCapabilityState=true`、`ShowHostReadOnlyBanner=true`、`HostReadOnlyBannerText` 含 `HOST_READ_ONLY` 且**不含“可浏览”**；`CapabilityMessage` 含 `library.trash.read/1`；`ShowEmptyState=false`；
   - 变异：保留“回收站可浏览” → 断言红；恢复抑制 → `ShowHostReadOnlyBanner` 红。

**取舍说明**：允许两条 banner 同时出现（可接受的冗余），优先保证“原因不丢失”。若 Lead 认为视觉噪音不可接受，唯一合法的替代是**把只读原因合并进同一条降级/能力文案**并加判别测试；不能既不显示也不在文案中说明。当前“静默抑制”不可接受。

### 2.5 四项汇总

| # | 现状分类 | 是否需 Host/Core | 现有测试 | 最小改动 | 量级 |
|---|---|---|---|---|---|
| ① | 已实现但生产不可达；行为错误（页级 missing） | 否（可达性另卡） | 无 | 删除两行状态污染 + 加 block/结果文案 | ~5–10 行 |
| ② | 未实现自动刷新 | 否 | 无（仅 delete-time NotFound） | NotFound 分支 + notify + Reload | ~8–12 行 |
| ③ | 分支已实现；提示被清空，无测试 | 否 | 无（仅 pending→Deleted） | 加 `_notify`（或重设结果） | ~2–5 行 |
| ④ | 有意抑制；无组合测试/规则 | 否 | 仅单状态 | 公式 + 文案 | ~2–4 行 |

---

## 3. 契约/边界与可达性裁决

### 3.1 是否触及冻结契约

| 契约/面 | 结论 | 依据 |
|---|---|---|
| C-07 / `IHostController.cs` | **不触及** | 本卡只改 `TrashViewModel`；`IHostController` 54 方法面不变；`generate_api_inventory.py --check` review 时 PASS |
| `ITrashController` / `TrashModels.cs` | **不触及** | 端口/typed DTO/错误码已齐；仅消费既有 `BOOK_NOT_FOUND`/`CORE_CAPABILITY_MISSING` |
| M2-C1 rev 2.14 / C-04b v1.1 / C-09 | **不触及** | 无新命令/字段/错误码/capability；preview/delete payload 不变 |
| ADJ-001（PD-01/PD-04） | **不触及** | 不改变披露、digest、事务或删除语义；只改结果处置/文案 |
| C-08 / 18 pins | **不触及** | `verify_pins.ps1` 18/18 PASS（review 实测） |
| Host wire / Core handler | **不触及** | `NewManga.Host/**`、`NewManga.CoreClient/**`、`src/**` 零 diff（本卡 `allowed_paths` 不含） |
| schema / migration / 依赖 | **不触及** | 无新增依赖；无 SQLite/schema 改动 |
| FEA-12-UI 历史 AC | **不回填** | 见 §10 |

### 3.2 是否必须 Host/Core 新能力？

**就本卡冻结的四项而言：否。** 四项都能在 App 侧用 fake 注入完成验证：

- ① 的“分支存在但不可达”是 Host/Core 的已知事实，不是本卡要修的可达性；
- ②③ 是 App 对既有 typed code 的处置；
- ④ 是 App 的 banner 计算/文案；
- 不需要新 capability、命令、DTO、错误码或 wire。

**但必须明确边界**：如果 Lead 要求 ① 的 `CORE_CAPABILITY_MISSING` **生产可达**，需要：

- 在 `HostCommandRegistry.RequiredCapabilities` 为 `library_delete_book_permanently` 增加能力映射（例如 `library.trash.write/1`，具体集合需 DSH/契约裁决）；
- 可能修改 `HostRuntime` 能力门与 `NewManga.Host.Tests`/`CoreClient.Tests`；
- 这属于 Contract/Host/Core 面，且会改变 `CommandIntegrationTests` 的“gated 命令集合”证据；**不在本卡**。若坚持并入，本卡该部分判 `BLOCKED`，应拆为独立 Host/Core 卡并重新 scope review。

---

## 4. In / Out 冻结草案（到文件/类/方法级）

### 4.1 In

| # | 冻结项 | 文件 / 类 / 方法 | 必须行为 | AC |
|---|---|---|---|---|
| **I-1** | delete-time capability 防御边 | `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/TrashViewModel.cs` · `TrashViewModel.ConfirmDeleteAsync` 的 `TrashDeleteOutcome.CapabilityMissing` 分支 | 不设置页级 `_capabilityMissing/_capabilityMessage`；保留列表；typed 结果“删除被拒绝”；`CanConfirmDelete=false`；不伪造成功 | AC-R1 |
| **I-2** | preview `BOOK_NOT_FOUND` 自动刷新 | 同文件 · `TrashViewModel.BeginPermanentDeleteAsync` 的 preview 失败块 | `BOOK_NOT_FOUND` → notify + 关闭 panel + `ReloadAsync`；零 delete 帧、零自动重试 | AC-R2 |
| **I-3** | cleanup retry `BOOK_NOT_FOUND` 提示 | 同文件 · `TrashViewModel.RetryCleanupAsync` 的 NotFound 分支 | 同一 digest 重试；NotFound 时用户可见“已不存在/已刷新”；列表刷新；清理面板关闭；不伪报完成 | AC-R3 |
| **I-4** | 只读/能力缺口双原因文案 | 同文件 · `ShowHostReadOnlyBanner`、`HostReadOnlyBannerText` | 只读由 `_hostReadOnly` 独立决定；组合态同时展示 `HOST_READ_ONLY` 与 `CORE_CAPABILITY_MISSING`；只读文案不声称“可浏览” | AC-R4 |
| **I-5** | 测试 / 证据 / 门禁 | `apps/desktop-avalonia/tests/NewManga.App.Tests/TrashUiTests.cs`；`verification/FEA-12-UI-RESIDUAL-1/**` | 4–5 个判别测试 + 4 个变异红日志；全量门禁不降；无真实用户数据 | AC-R5 |

### 4.2 Out（明确不做）

| # | 不做项 | 理由 / 边界 |
|---|---|---|
| **O-1** | 给 `library_delete_book_permanently` 增加 Host 能力门/可达性 | 属 `NewManga.CoreClient`/`NewManga.Host` 与契约面；本卡不碰；需要则另卡 |
| **O-2** | 新 command / capability / DTO / 错误码 / schema / migration / 依赖 | 现有 wire 已够；本卡零新增 |
| **O-3** | `IHostController.cs`、`RunContracts.cs`、`FEA-C07_API_INVENTORY.md`、任何 pinned 契约字节 | C-07 冻结面 |
| **O-4** | `NewManga.Host/**`、`NewManga.CoreClient/**`、`NewManga.DesignSystem/**`、`src/**`（Python） | 非 App 写域 |
| **O-5** | `RecycleBinView.axaml` / `.axaml.cs`、`LibraryViewModel.cs`、`HostController.cs`、`NullHostController.cs`、`TrashModels.cs`、`FakeHostController.cs` | 现有绑定/端口/fake 已够；若实现发现必须改，停下请 DSH 增列 |
| **O-6** | 真实用户数据 / `%APPDATA%` / 外部卷 / 真实回收站 / 真实原文件删除 / push | 硬边界 |
| **O-7** | 批量删除、`PurgeTrash`、页面级/章节级删除、缩略图/内容预览、保留期限/自动清理、Fluent 真实接线 | FEA-12-UI 已 OUT 的 L1–L10，本卡不扩 |
| **O-8** | 修改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、FEA-12-UI 历史字节 | DSH 单点指针/历史证据 |
| **O-9** | 声称 ① 生产可达、AC 已回填、L3/L4 已通过 | 见 §9/§10 |

### 4.3 allowed_paths（精确到文件）

**允许**

- `doc/tasks/FEA-12-UI-RESIDUAL-1.md`
- `doc/reviews/FEA-12-UI-RESIDUAL-1-*.md`
- `doc/handoffs/FEA-12-UI-RESIDUAL-1-*.md`
- `verification/FEA-12-UI-RESIDUAL-1/**`
- `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/TrashViewModel.cs`
- `apps/desktop-avalonia/tests/NewManga.App.Tests/TrashUiTests.cs`

**明确不再放宽（除非 DSH 书面增列）**

- `apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/RecycleBinView.axaml` / `.axaml.cs`
- `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs`
- `apps/desktop-avalonia/src/NewManga.App/Services/{HostController.cs,NullHostController.cs,TrashModels.cs,IHostController.cs,RunContracts.cs}`
- `apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs`
- `apps/desktop-avalonia/src/NewManga.Host/**`、`NewManga.CoreClient/**`、`NewManga.DesignSystem/**`
- `src/**`（Python）、`doc/plan/**`、`doc/contracts/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、任何既有 Task/Review/Handoff/evidence 字节

> 说明：现有 `FakeHostController` 已提供 `TrashCapabilities`、`Snapshot with { WritesAllowed=false }`、`ScriptedTrashPages/Previews/Deletes`、`TrashFrames/TrashFramePayloads`、`TrashProbeGolden`，足以覆盖四项；**不需要**改 fake。若 Owner 为了测试可读性想改 fake，属写域扩大，先报 DSH。

---

## 5. AC-R1…AC-R5（可验证条款 + 判别性 .NET 测试）

> 所有测试均加在 `apps/desktop-avalonia/tests/NewManga.App.Tests/TrashUiTests.cs`，复用 `NewTrash()`/`FakeHostController`；不新增 Avalonia 窗口、不用真实 Host/Core、不用 sleep。每条 AC 都要求：**删掉实现/改坏关键分支必须变红**，并把红/绿日志落 `verification/FEA-12-UI-RESIDUAL-1/logs/`。

### AC-R1 delete-time capability 防御边

**冻结判定**：

- 当单本删除返回 `TrashDeleteOutcome.CapabilityMissing` / `CORE_CAPABILITY_MISSING` 时，**不得**把页级 `_capabilityMissing` 设为 true，**不得**覆盖 read 侧 `_capabilityMessage`；
- 已加载的列表保持可见（`ShowList=true`、`ShowCapabilityState=false`、`Items` 数量不变）；
- 结果面板保留并显示 typed `CORE_CAPABILITY_MISSING`；`DeleteResultTitle="删除被拒绝"`；`CanConfirmDelete=false`；零成功提示、零 restore/preview 副作用；
- 不改变 probe 得到的 `read/write/preview` 能力布尔值（没有新 probe 就不推断）；用户可用既有“刷新”重新 probe；
- **不要求**该分支生产可达；卡/Handoff 必须写明“defensive invariant only”。

**判别测试**：`Delete_CapabilityMissing_DoesNotTurnThePageIntoReadCapabilityMissing`（见 §2.1）。
**变异**：`_capabilityMissing=true` 回归、分支落入 default 各至少 1 红。

### AC-R2 preview `BOOK_NOT_FOUND` 自动刷新

**冻结判定**：

- preview 返回 `BOOK_NOT_FOUND` 时，UI 必须 `_notify` 提示并自动 `ReloadAsync`；
- 恰好 2 个 `library_list_trash` 帧（初始 + 刷新），0 个 delete 帧；probe 2 次（初始 + `ReloadAsync` 重新探测）；
- 披露面板关闭；刷新后的列表不含已不存在的条目（幽灵行清除）；不自动重试 preview；
- 其他 preview 失败码（`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE`、`CORE_UNAVAILABLE`、未知码）保持现有“就地错误 + 重新预览”行为，不被误改成刷新。

**判别测试**：`Preview_BookNotFound_ClosesPanel_AndReloadsTheList`（见 §2.2）。
**变异**：移除 `ReloadAsync`、移除 `_notify`、把 `BOOK_NOT_FOUND` 误并入通用错误分支，各至少 1 红。

### AC-R3 cleanup retry 的 `BOOK_NOT_FOUND`

**冻结判定**：

- `CleanupPending` → 重试 → 再重试 → `BOOK_NOT_FOUND`：3 个 delete 帧；三次 `inventory_digest` 与首次**逐字节相等**（逐书 digest）；仅 1 个 preview 帧；
- NotFound 时用户可见“作品已不存在（`BOOK_NOT_FOUND`）/已刷新”的 typed 提示；列表刷新（2 个 list 帧）；`IsCleanupPending=false`、`CanRetryCleanup=false`、结果面板关闭；不伪报“清理成功”；
- 失败不得自动重试；不得为 NotFound 重新 preview。

**判别测试**：`CleanupRetry_SecondRetryBookNotFound_NotifiesAndRefreshes_WithSameDigest`（见 §2.3）。
**变异**：移除 `_notify`、改用集合 digest/新 digest、移除 `ReloadAsync`，各至少 1 红。

### AC-R4 只读/能力缺口双原因文案

**冻结判定**：

- `ShowHostReadOnlyBanner` 仅由 `_hostReadOnly` 决定，不再被 `HasCapabilityGap` 抑制；
- Host 只读 + write/preview 缺口：两个 banner 同时可见；`HOST_READ_ONLY` 与 `CORE_CAPABILITY_MISSING` 分别出现且不互相冒充；列表仍真实；`CanWrite=false`；
- Host 只读 + read 缺失：`ShowCapabilityState=true` 且只读 banner 仍可见；只读文案不得含“回收站可浏览”（read 不可用时是假话）；能力文案不得含 `HOST_READ_ONLY`；
- 单一原因时仍只显示一个 banner（既有单状态测试全绿）；
- 不改 XAML 结构；不新增控件/令牌。

**判别测试**：`HostReadOnly_PlusWriteCapabilityGap_ShowsBothIndependentCauses`、`HostReadOnly_PlusReadCapabilityMissing_ShowsCapabilityStateAndReadOnlyReason`（见 §2.4）。
**变异**：恢复 `&& !HasCapabilityGap`、恢复“可浏览”文案，各至少 1 红。

### AC-R5 写域、门禁与证据

**冻结判定**：

- `git diff --name-only <base>..HEAD` ⊆ `allowed_paths`；`doc/plan`、`doc/contracts`、`src/**`、`NewManga.Host/**`、`NewManga.CoreClient/**`、`NewManga.DesignSystem/**`、`RecycleBinView.axaml` 零 diff；无新依赖；
- 定向 `TrashUiTests` 全绿（基线 35；新增 4–5 个）；
- 全量 .NET **≥1527 passed / 0 failed / ≤86 skipped**（before/after 分列、8 项目分列，不抄旧卡数字）；
- pytest 全量 **3249/10 不降**；本卡零 Python 改动，按先例可 `NOT_RUN` + `git diff -- src tests` 为零，但 Handoff 必须写明理由；`pytest tests/fea11` 145 若跑不得降；
- `verify_pins.ps1` 18/18 PASS；`generate_api_inventory.py --check` PASS；`check.ps1` PASS（允许既有 3 warnings）；
- 证据含 `changed-files.txt`、`scope-validation.log`、`gates.log`、`logs/scope-mutations.log`（4 个变异红）、before/after 测试计数；L3 真机 **NOT_RUN**，不得写 PASS；
- 无真实用户数据/AppData/外部卷/真实回收站；不 push。

**判别测试/证据**：上述命令实跑日志 + changed-files + 变异日志；Review 需逐项核对，不以“全绿”替代断言。

---

## 6. allowed_paths / Owner / Reviewer / base / depends_on / 门禁

### 6.1 Owner / Reviewer

| 角色 | 建议 | 说明 |
|---|---|---|
| **Owner** | **ZCode**（首选） | UI/UX 与 Avalonia 主责；本卡 App 侧小范围收尾，符合其职责。若 ZCode 不可用，可用 DSH Agent Teams teammate；必须在卡内记录 owner。 |
| **Reviewer** | 独立上下文 fresh subagent（不得为实现会话/实现者自审） | 只读被审 head；记录 session ID 与来源；本报告即该模式。Lead 保留 Appointment 与 findings 处置。 |
| **Lead / Integrator** | DSH | 范围冻结、base 固定、契约/架构裁决、集成验证、push。 |

### 6.2 base / depends_on

- `depends_on`：`FEA-12-UI`（`done`；delivery/integration `a46d4d5c7`）。
- `base_commit`：**null，释放时由 DSH 固定为当时 HEAD**；review 时基线 `57f62b3fe`，复审时 HEAD 已到 `690c77eb0`（仅 docs），不能把任一值直接写成释放 base。
- `branch` / `worktree`：沿用 main 工作树，或由 DSH 决定；本卡不需要 worktree。
- 卡状态：当前 `proposed`；释放前必须先把 `allowed_paths` 扩到 §4.3 的 6 条，再进入 ready。

### 6.3 门禁（释放/收尾）

| # | 门禁 | 预期 | 备注 |
|---|---|---|---|
| 1 | 定向 `dotnet test ... --filter FullyQualifiedName~TrashUiTests` | PASS（≥35 + 新增） | fake 驱动，无窗口 |
| 2 | 全量 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **≥1527 passed / 0 failed / ≤86 skipped** | before/after 分列；8 项目合计 1527 |
| 3 | `pytest tests` | **3249/10 不降**；或 NOT_RUN + 零 Python diff 理由 | 本卡零 Python；`pytest tests/fea11` 145 参考 |
| 4 | `verify_pins.ps1` | **18/18 PASS** | review 实测 PASS |
| 5 | `generate_api_inventory.py --check` | PASS | review 实测 exit 0 |
| 6 | `check.ps1` | PASS（3 warnings） | review 实测 PASS |
| 7 | scope diff | ⊆ §4.3；禁止面零 diff | `git diff --name-only base..HEAD` |
| 8 | 证据 | `verification/FEA-12-UI-RESIDUAL-1/**` 完整 | 含变异红日志 |
| 9 | 独立 Review + DSH 集成 | 通过 | Reviewer 不得参与实现 |
| 10 | L3/L4 | **NOT_RUN**，不得声称通过 | 本卡不新增真机走查 |

---

## 7. 契约影响表（预期零触碰）

| 契约/面 | 是否改 | 证据/说明 |
|---|---|---|
| **C-07 / `IHostController.cs`** | **否** | 只改 `TrashViewModel`；`IHostController` 54 方法面不变；API inventory PASS |
| **`ITrashController` / `TrashModels.cs`** | **否** | 端口、DTO、错误码已存在；本卡只消费 |
| **M2-C1 rev 2.14** | **否** | 无新命令/DTO/字段/capability；`BOOK_NOT_FOUND`、`CORE_CAPABILITY_MISSING` 均为既有码 |
| **C-04b v1.1** | **否** | delete payload 键集不变；digest 绑定语义不变 |
| **C-09** | **否** | 回收站命令面不变；不新增/不调用 `PurgeTrash` |
| **ADJ-001（PD-01/PD-04）** | **否** | 不改披露项、保护语义、事务或文件行为 |
| **`AllowedDeleteTrashErrorCodes`（Host 删除/回收站投影）** | **否（但仍有跨卡债）** | 本卡不把 `CORE_CAPABILITY_MISSING` 加入白名单；见 §9 L-R2 |
| **18 pins** | **18/18 PASS** | review 实测；卡实施时复跑 |
| **Schema / migration / 依赖** | **否** | 无 SQLite/schema/包变更 |
| **Host / Core / Python** | **否** | `NewManga.Host/**`、`NewManga.CoreClient/**`、`src/**` 零 diff |
| **FEA-12-UI 历史 AC** | **否（不回填）** | 见 §10 |

**结论**：本卡是纯 App 行为/测试/文案切片，预期**零契约字节、零 wire、零 schema、零依赖、零 pins 数量变化**；唯一“契约相关”点是 `CORE_CAPABILITY_MISSING` 的 Host 白名单旧债，明确留在 Host/Core 侧。

---

## 8. 测试与证据可行性

### 8.1 可复用的测试面

| 测试面 | 位置 | 可复用性 | 约束 |
|---|---|---|---|
| `TrashUiTests` | `apps/desktop-avalonia/tests/NewManga.App.Tests/TrashUiTests.cs` | **直接复用**：纯 VM、fake controller、frame/payload 断言；review 实跑 35/35、73 ms | 不创建 Avalonia 窗口；`RelayCommand` fire-and-forget，测试需 `await` 方法或依赖 completed fake |
| `FakeHostController` | 同目录 `FakeHostController.cs:1612-1749` | **直接复用**：`TrashCapabilities`、`ScriptedTrashPages/Previews/Deletes`、`TrashFrames/TrashFramePayloads`、`TrashProbeGolden`、`Snapshot with { WritesAllowed=false }` | 不需改 fake；若需要新 hook，先请 DSH 增列 |
| `V2ShellUiTests` | 同目录 | **不需要**：真实 Avalonia headless 窗口，成本高；本卡 banner 行为在 VM 层即可判别 | 若 Lead 要求视觉快照，另议；不在本卡 allowed_paths |
| `NoDbOsAccessTests` | 同目录 | 全量门禁会跑；本卡无新增 DB/OS 访问 | 无需改 |
| `Fea12TrashUiIpcTests` | `tests/NewManga.Host.Tests` | **不新增**：真实 IPC 已有 27 帧证据；本卡四个分支是 App 状态机细节，真实 Core 难以注入 cleanup retry NotFound 序列 | 不加 Host 测试，避免扩大写域 |
| `CommandIntegrationTests` | `tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs:605-678` | **只读证据**：证明 delete-permanently 不在能力门集合、`CORE_CAPABILITY_MISSING` 不在白名单；本卡不修改 | 作为 §2.1 可达性证据 |

### 8.2 headless / Avalonia 约束

- 四项测试全部在 `TrashViewModel` 层完成，不需要 `Avalonia.Headless` 窗口、不需要 dispatcher pump；与现有 `TrashUiTests` 一致。
- `RelayCommand` 不是 `AsyncRelayCommand`：与本卡相关的命令由 `RelayCommand(() => _ = XxxAsync())` 触发；测试优先 `await` 公共方法（`EnterAsync`/`BeginPermanentDeleteAsync`/`RestoreSelectedAsync`），仅在 fake 同步完成时使用 `Command.Execute`（现有测试已如此）。
- 不要在测试中引入 `Task.Delay`/固定 sleep；fake 全部返回 completed Task，确定性高。
- 若要验证 XAML 可见性，只做静态绑定断言（`RecycleBinView.axaml` 中两个 `IsVisible` 仍分别绑定 `ShowHostReadOnlyBanner`/`ShowCapabilityDegraded`），不要求启动窗口。

### 8.3 flaky 风险

| 风险 | 说明 | 缓解 |
|---|---|---|
| 低 | 纯 VM + fake，无时钟/IO/窗口 | 不用 sleep；断言帧数/字段，不断言 UI 渲染时序 |
| 低 | 全量 .NET 既有 flaky（与本卡无关） | 命中时隔离复跑并如实记录，不删测试/不放宽断言 |
| 低-中 | 未来若有人把 `ReloadAsync` 改成 fire-and-forget，测试可能偶发 | 测试直接 `await` 方法；Review 要求 `BeginPermanentDeleteAsync` 内 `await ReloadAsync` |
| 中 | ① 的测试注入的是“生产不可达”结果，容易被误读为已修用户可见缺陷 | AC/Handoff 明写 defensive invariant；不写“修复用户可见问题” |

### 8.4 预估改动量级

| 项 | 预计 |
|---|---|
| 生产代码 | `TrashViewModel.cs` **约 15–30 行**（4 个分支/2 个属性/文案） |
| 测试 | `TrashUiTests.cs` **约 120–180 行**（4–5 个测试 + 少量 helper） |
| 证据 | 1 个 `verification/FEA-12-UI-RESIDUAL-1/`，4–5 个日志 + 1 个 mutation 日志 |
| 依赖/契约 | 0 |
| 风险等级 | 低（App 状态机微调） |

---

## 9. 风险 / limitation（≥4）与 P3 观察

### 9.1 limitation（预登记）

- **L-R1（①的生产可达性）**：本卡只钉住“删除返回能力缺失不得污染页级 read 能力态”的防御不变量；当前 Host 不对 `library_delete_book_permanently` 做能力门，Core 也不返回 `CORE_CAPABILITY_MISSING`，因此该分支**生产不可达**。卡/Handoff 不得写成“已修复用户可见的能力缺失 bug”。若未来要让其可达，另卡处理 Host 能力门。
- **L-R2（R-002 旧债仍在）**：`CORE_CAPABILITY_MISSING` 不在 `AllowedDeleteTrashErrorCodes`；若未来 Core 在 delete 路径返回该码，Host 的 `ProjectDeleteTrashError` 会把 category 降为 `unknown`（code 保留），App 仍能按 code 分类，但 Host 契约层面的错误分类仍不完整。该债属 Host/Core，不在本卡修；本卡不把它加入白名单。
- **L-R3（②的刷新失败）**：preview `BOOK_NOT_FOUND` 后自动 `ReloadAsync` 若自身失败，用户看到列表错误态，不会自动重试；这是有意的“只刷新一次”，不引入循环。
- **L-R4（③的面板关闭）**：cleanup retry NotFound 后关闭结果面板，提示只通过 notify；若产品希望保留结果面板，必须改为 Reload 后重设可见文案，不能沿用当前“设置后被 ResetPreview 清空”的实现。本卡推荐关闭。
- **L-R5（④的视觉冗余）**：组合态允许两条 banner 同时出现，接受一定视觉冗余以换取原因不丢失；若 Lead 要求单条合并文案，必须重新冻结文案规则并加测试，不属于“删掉抑制”即可。
- **L-R6（证据层级）**：四项均为 VM 级 fake 测试，不新增真实 Host/Core IPC；`cleanup retry NotFound` 的真实 wire 行为仍无 L2 IPC 证据。若 Lead 要求真实 IPC，需要扩大写域到 `NewManga.Host.Tests`，本卡不默认做。
- **L-R7（④的 read 缺失文案）**：只读 banner 去掉“可浏览”后，read 可用时信息量略减；这是为了在 read 缺失时不撒谎。若未来要做动态文案（可浏览/不可浏览），可在不改契约的前提下追加，但需新增测试。

### 9.2 P3 观察

1. **P3-1（③的“有实现无测试”不准确）**：`RetryCleanupAsync` 的 NotFound 分支存在，但 `_deleteOutcomeText` 在 `TrashViewModel.cs:822-824` 设置后被 `:827` 的 `ResetPreview()` 清空（`:912-914`），且分支没有 `_notify`；用户实际看不到“已不存在”。因此本卡必须包含最小修复，不能只补测试。建议 Lead 在冻结卡中把 ③ 的描述改为“分支存在但提示丢失 + 无测试”。
2. **P3-2（①的可达性证据链）**：`HostCommandRegistry.RequiredCapabilities`（`:94-101`）不含 delete-permanently；`HostRuntime` 能力门只在 `Count>0` 时执行（`:1149-1158`）；`CommandIntegrationTests` 的 gated 集合也不含它（`:605-613`）。这是明确证据，但也是 Host/Core 侧的潜在缺口：若 DSH 认为 delete 也应受 `library.trash.write/1` 门控，应另卡并在 M2-C1/C-04b 层裁决，不能由 UI 卡顺手改。
3. **P3-3（STATUS 的 pytest 基线过期）**：`doc/STATUS.md:20` 仍写 pytest 3212/10，而 RENDITION-1 closeout 与 `FEA-11-RENDITION-1.md:125,134,220` 为 3249/10；本卡门禁应使用 3249/10。STATUS 属 DSH 单点，不由本卡改。
4. **P3-4（HEAD 漂移）**：review 启动时 57f62b3fe，复审时 690c77eb0（仅 3 docs/3 行）；释放时 base 必须由 DSH 重新固定，不能抄 review 数值。该漂移不影响本报告代码事实（树等价）。
5. **P3-5（FEA-12-UI closeout 的 L1/L2 指代不一致）**：`doc/tasks/FEA-12-UI.md:289` 写“L1（批量 OUT）、L2（无总数/无缩略图）”，而卡内 L2 是缩略图/内容预览、L4 才是无总数；历史字节不动，本卡只按卡内 L1–L10 引用，不据此改 AC。
6. **P3-6（XAML 注释）**：`RecycleBinView.axaml:64` 注释“能力缺失时绝不显示此假 banner”在 ④ 改为“真实只读 + 能力缺口同时显示”后语义略变（不再是“假”banner，而是真实第二原因）。建议实现时若允许改 XAML 则同步注释；本卡为最小写域不改 XAML，Review 不因注释判缺陷。
7. **P3-7（Probe 时点）**：`_hostReadOnly` 在 `ProbeAndLoadAsync` 每次刷新时重新读取 `_writesAllowed()`（`TrashViewModel.cs:405`），但 `ShowHostReadOnlyBanner` 不会在 Host 写闸变化时主动刷新；组合态测试需在 Enter 前设置 `WritesAllowed=false`，或在 Enter 后触发 Refresh。实现/测试不要假设运行中自动响应 Host 策略变化。
8. **P3-8（Fake 的 `WritesAllowed`）**：`FakeHostController` 的 `Snapshot` 是 record，测试用 `fake.Snapshot = fake.Snapshot with { WritesAllowed = false }`；不要新增 fake 字段。现有 `NewTrash` 的 `_writesAllowed` 委托捕获 fake，设置顺序需在 `EnterAsync` 前。

---

## 10. 是否需要 FEA-12-UI 历史 AC 回填

**结论：不回填，只登记 follow-up 收口。**

- `FEA-12-UI` 已 `done`，AC1–AC10 全 `MET`，`delivery/integration a46d4d5c7`；其 AC 文本、L1–L10、Closeout 字节是历史证据，不由本卡改（`doc/tasks/FEA-12-UI.md:284-289`）。
- 本卡的 ①–④ 是 closeout `:288` 明确登记的 P3 follow-up；本卡只需在自己的 AC/Closeout 中写“对应 FEA-12-UI AC4/AC6/AC7 的 residual 边”，**不**改 `FEA-12-UI.md` 的 `[x] <<MET>>` 标记。
- L3/L4 仍保持 `NOT_RUN`；本卡不得把 L3/L4 回填为通过，也不得把 `AC1–AC10` 重新标 `PARTIAL`/`MET`。
- 如果 DSH 需要历史可追溯性，建议只在 RESIDUAL-1 的 Closeout 写映射表；不改旧卡字节，避免破坏历史证据 pin。

---

## 11. 摘要

- **裁决：`READY-TO-FREEZE`（App-only，四项残余）。** 四项均可在 `TrashViewModel.cs` + `TrashUiTests.cs` 内收口，不需要 Core/Host wire、能力表、schema、依赖或任何冻结契约字节；`IHostController`/`ITrashController` 不变。
- **现状修正**：①分支生产不可达且会污染页级 read 能力态；②preview `BOOK_NOT_FOUND` 未实现自动刷新；③retry NotFound 分支存在但提示被 `ResetPreview` 清空、无 notify；④只读 banner 在能力缺口时被有意抑制，需冻结“两个独立事实同时展示”的规则。
- **冻结边界**：In = 四项 App 行为/文案 + 4–5 个判别测试；Out = Host/Core 能力门、`IHostController`/契约/pins、XAML/Fake/LibraryViewModel、真实数据/push、FEA-12-UI AC 回填。
- **Owner=ZCode**（备选 DSH teammate）；Reviewer=独立上下文 fresh subagent；base=释放时 DSH 固定（review 基线 57f62b3fe，复审时 690c77eb0 docs-only）；depends_on=FEA-12-UI（done）。
- **门禁**：定向 `TrashUiTests` + 全量 .NET ≥1527/0/≤86 + pytest 3249/10 或零 Python NOT_RUN 理由 + pins 18/18 + API inventory PASS + check PASS + scope diff ⊆ 6 条 allowed_paths + 证据/变异红日志；L3 **NOT_RUN**。
- **不建议**把 ① 的生产可达性或 delete 的 Host 能力门并入本卡；若要求，另卡/另契约审查。

UI-RESIDUAL-1-SCOPE: READY-TO-FREEZE — 四项均为 App 侧可测收口；①仅作 defensive invariant（Host 当前不对 `library_delete_book_permanently` 做能力门，生产不可达），③需补最小 `_notify` 而非纯测试，④需冻结“只读+能力缺口同时展示且只读文案不声称可浏览”的规则；写域仅 `TrashViewModel.cs` + `TrashUiTests.cs`，零契约/wire/Host/Core 变更；若要求 ① 生产可达或 delete 能力门，另卡并重新 scope review。
