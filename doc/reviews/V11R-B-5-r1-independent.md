# 独立审查报告 · V11R-B-5 独立复核 r1（导出预检 / 进度·取消·历史 / 术语与约束）

**审查者**：reviewer（独立、只读，未参与实现；本轮写操作仅本文件）。
**纪律**：pin 固定、不重跑 build/test（以 pin 内日志为准，未核项记 UNVERIFIED）、不采信 Owner 自述、只读代码/证据/doc。

**Pin**
- **`455d2c4328c67ee231a3a4ded691ecbc7f3fcaca`**（Lead 指定；已核实为 main 祖先，merge `1e6a3c4ee`）。
- 说明：该 pin 的**最后一条 commit 是 B-4 I2d**（`fix(V11R-B-4-I2d)`），B-5 功能 commit 为其父 **`e3e928869`**（`feat(V11R-B-5): export preflight …`）；B-5 的代码与证据在 `e3e928869` 引入，`455d2c432` 仅追加 B-4 VM/测试/证据（7 文件），**未改 B-5 代码**。本报告以 pin 树为准，并逐项核对「证据生成时的代码」与 pin 的一致性。
- 参照：`verification/V11R-B-5/*`、`doc/tasks/V11R-B-5.md`、`V11R_SCREEN_SPECS` 导出/术语相关章节、`doc/plan/V11R_AVALONIA_CONTRACT.md`（A-7 导出契约）、`IHostController` 导出面。

---

## 一、结论

**V11R-B-5 = PASS_WITH_ISSUES（无 P1，可合入；证据需重生成后归档）**

一句话：B-5 是「用真实 Host 导出面 + 诚实 NOT_WIRED」完成度较高的一张卡——预检、启动、轮询、取消、揭示、历史、只读降级、术语三页全部走真实调用或明示未接入，未发现伪造数据/假进度；问题集中在**证据与 pin 的对账**（日志无 HEAD/EXIT、test.log 早于 pin 的 I2d +2 测试、无 curate 脚本）与几处 P3 措辞/测试强度。

---

## 二、已核实正确（关键项）

1. **预检数据真实、不可预读项诚实置「—」**
   `StudioExportViewModel.RefreshPreflightAsync`（`ViewModels/V2/Studio/StudioExportViewModel.cs:403-431`）调真实 `_host.GetTranslatedPageIdsAsync(chapterId)`；失败/阻塞计数取 `_page.RunProjection?.FailedPageCount/BlockedPageCount`（`:328-333`）；`UnconfirmedPageCount/StalePageCount` 返回 **null**（`:335-339`），渲染「—」并带原因 tooltip（`:341-347`，UnconfirmedNotWired 明示「review 面属 F0-2」、StaleNotWired 明示「由 Core 在 StartExport 内算，EXPORT_STALE」）。
   测试 `Preflight_UsesRealReads_AndRendersUnavailableCountsAsDash`（`V2StudioExportTermsTests.cs:45-95`）断言：`TranslatedPageCount=3`、`host.TranslatedPageCalls=1`、`UnconfirmedPageCount/StalePageCount is null`、UI 文本「—」；证据 `preflight.json` 字段均从 VM/Host 实测写出（非字面量）。

2. **作用域不静默扩大**：`ExportablePageIds`（`:303-322`）= 本章→全部已翻译页；选中页→与共享 `_selection.SelectedPageIds` **交集**；空集时 `CanStart=false`（`:188-190`）且 `StartExportAsync` 拒绝并说明（`:465-476`）。测试断言交集 `["p2","p3"]` 与 `ScopeText="选中 2 页"`。无 B-4 曾出现的「选中→回落整章」问题。

3. **真实导出调用与参数**：`StartExportAsync`（`:465-524`）向 `IHostController.StartExportAsync(bookId, chapterId, ExportablePageIds, target, format, pdfContent?, ct)` 传真实页集与格式；目标文件名为 `newmanga-{chapter}-{stamp}.{ext}`（`:453-460`），目标目录取 `_host.ExportDirectorySuggestion`；**UI 从不显示绝对路径**：`OutputText` 只用 `Path.GetFileName`+`ShortHash`（`:365-370`），`TargetHint` 只显示路径字符数（`:351`）。测试断言 `start.Format="pdf"`、`PdfContent="searchable_dual_layer"`、`PageIds`、`TargetPath` 前缀，并断言 `OutputText` 含 `ch1.zip` 而**不含** `/exports`（`:166-167`），证据 `output_hides_absolute_path` 由该断言派生。

4. **进度/取消/无残留**：`RefreshSnapshotAsync`（`:533-561`）走真实 `GetExportSnapshotAsync`；终态由 `ApplySnapshotState` 落 `Completed/Cancelled/Failed`（`:563-583`）；`TickAsync` 在非 Running 或未到注入间隔（默认 700ms，`:146`）时 no-op（`:586-600`）；`CancelAsync` 调真实 `CancelExportAsync` 并落快照状态（`:602-622`）。测试 `Start_PollsSnapshot_CancelLeavesNoResidual_AndRevealCallsHost`（`:131-201`）断言：单次 Start 参数、`SnapshotCompleted/Total/Percent`、完成后 `IsTerminal/CanReveal`、`RevealAsync` 调真实 `RevealExportFolderAsync`、取消后 `CancelCalls=["exp-10"]`、**再 `TickAsync` 快照调用数不增**（`:181-183`），证据 `export-job.json` 全字段由 Host 调用计数/快照实测写出。

5. **历史真实、只显示文件名与 SHA 前缀**：`LoadHistoryAsync`（`:654-679`）调真实 `GetExportHistoryAsync`，按 `CompletedAt` 倒序；`StudioExportHistoryItemViewModel`（`:48-90`）仅暴露 `Path.GetFileName(OutputPath)`、`ShaPrefix`（≤12）、状态符号/文案（经 `StudioStates`/DS）。测试 `History_LoadsRealEntries_AndRendersStates`（`:230-263`）断言 2 条、ZIP/PDF、`●`/`✗`、`a.zip`、UI 列表计数；证据 `history.json` 为实测值。

6. **只读 Host 零调用**：`ReadOnlyHost_CannotStartExport_AndSaysWhy`（`:203-226`）断言 `WritesAllowed=false → CanStart=false → StartExportAsync 返回 null`、`StartExportCalls` 为空、状态含「只读」；证据 `readonly.json` `start_calls:0` 真实。

7. **stale 策略「未支持」在 pin 上是诚实事实（现已过时）**：
   - pin 的 `IHostController.StartExportAsync`（`Services/IHostController.cs:323` 起）**没有** `stalePolicy` 参数；`HostController.StartExportAsync`（`:1289`）固定按默认 abort 走；`ImportExportContracts` 里 request 写入器有 `stalePolicy` 形参默认 `"abort"`，但宿主未暴露。
   - UI 因此把 `continue_existing` 标为「未支持」并禁用（`StudioExportViewModel.cs:98-112,281-297`），尝试选择时 `TrySelectStalePolicy` 返回 false 并给出「未暴露 stale_policy」原因；测试 `StalePolicy_OnlyTheHostSupportedOptionIsSelectable`（`:98-127`）断言按钮禁用+文案「未支持」+选择被拒+仍为 abort；证据 `stale-policy.json` 的 `abort_supported/continue_existing_supported/ui_option_disabled/selection_attempt_refused` 全部由 UI/VM 实测派生。
   - **A-7 之后（main）**：`IHostController.StartExportAsync` 已增加 `string? stalePolicy = null`（main `IHostController.cs:322-333`、`HostController.cs:1296-1339`）→ B-5 的「未支持」在 main 上已过时。**pin 上诚实，现状需 follow-up**（见 §四）。

8. **术语三页 NOT_WIRED 零伪造**：`NotWiredTermsSource`（`Views/.../ViewModels/V2/Studio/StudioTermsViewModel.cs:37-62`）三个 `List*Async` 全部返回空数组、`IsWired=false`、`CapabilityNote` 明示原因；VM（`:72-160`）`Rows` 恒空、`IsSearchEnabled=false`、`EmptyText="未接入：不展示任何条目"`，编辑/新建/解决冲突全部拒绝并给原因。测试 `Terms_AreNotWired_NoFabricatedRows_AndExplainWhy`（`:268-321`）断言三页均 0 行、搜索禁用、`TryEdit/TryCreate/TryResolveConflict` 全 false、能力清单含 glossary/不译表；证据 `terms.json` `rows:0/search_disabled/edit_refused` 均为实测，无编造行。

9. **入口与浮层**：`StudioWorkspaceView`（pin 树 `Shell/V2/Studio/StudioWorkspaceView.axaml.cs:33,50,77-80,95-97`）头部「导出」「术语」按钮打开同一 `StudioToolsOverlay`，三页签（预检/历史/术语），`RowSpan=2` 覆盖；overlay 有 `KeyDown Esc→Close`（`StudioToolsOverlay.cs:76-80`）与 scrim 点击关闭（`:38`）。测试 `ToolsOverlay_OpensAndCloses_KeyboardEscape`（`:324-337`）验证开关/三页签/轮询间隔 500–1000ms 边界。我抽查 `artifacts/export-preflight.png`：真实渲染，预检数字 3/2/—/—/—、范围本章/选中页、格式 ZIP/PDF、stale abort(已支持)/continue_existing·未支持、进度尚未开始、目标文件名生成且不露绝对路径——与代码/证据一致。

10. **错误路径 typed 化**：StartExport 被拒时按 `_host.Snapshot.LastError` 映射 `EXPORT_STALE`（`:503-506`）、只读/未就绪分别给原因；无异常逸出（Start/Snapshot/History 均有 null/取消分支处理）。

---

## 三、问题清单

### P1
*无。*

### P2
| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| **B5-P2-1** | `verification/V11R-B-5/{build.log,test.log}` + `verification/V11R-B-5/README.md` | **证据与 pin 不对账（R-19 纪律未落实）**：<br>①`test.log` 的 App 汇总为 **256 通过/6 跳过**，但 pin `455d2c432` 在证据生成（`e3e928869`）之后又加入了 B-4 I2d 的 **2 个 App 测试**（`Scope_SelectionDisappearsFromProjection_…`、`SubmitInFlight_BlocksSecondSubmit_…`）→ pin 上应为 **258**；说明日志生成于旧 commit、未在 pin 重生成。<br>②`build.log`/`test.log` 是裸控制台输出：**无命令、无 HEAD、无 EXIT 码**（对比 B-1/C-1/C-2 的同一纪律），无法证明对应当前 pin。<br>③README 无「质量门（命令+exit+计数）」表，也未声明证据生成时的 commit；`V11R-B-5/` 下**没有 curate 脚本**（README 声称「测试写 %TEMP%，curate 落仓」，但入口未随证据交付）。 | 在 pin 上重跑并落 `build.log/test.log`（记录命令、HEAD=`455d2c432`、EXIT、逐套件计数），补 `curate.ps1`（与 B-1/C-1 同构：temp-first + `NEWMANGA_EVIDENCE_SYNC=1` 显式镜像），README 增加质量门表并把 B-5 功能 commit 与 pin 的关系写清。 |

### P3
| # | 位置 | 问题 | 建议 |
|---|---|---|---|
| B5-P3-1 | `StudioExportViewModel.cs:695-698` + `verification/V11R-B-5/stale-policy.json.verified_fact` | `verified_fact` 直接写代码常量 `ContinueExistingNotSupported`（UI 文案），不是对「IHostController 无 stalePolicy」这一事实的测量 | 用反射断言 `IHostController.StartExportAsync` 无 `stalePolicy` 形参（或断言 Host 请求里 `stale_policy` 恒为 `abort`）作为证据来源；常量只作文案 |
| B5-P3-2 | `V2StudioExportTermsTests.cs:324-337` | 测试名 `…KeyboardEscape`，但测试体只调 `view.Tools.Close()`，从未发送 Esc 键；overlay 的 `KeyDown Esc` 分支（`StudioToolsOverlay.cs:76-80`）因此**无测试覆盖** | 用 `window.KeyPressQwerty(PhysicalKey.Escape)`（与 B-3/B-4 同手法）断言 `IsOpen=false` |
| B5-P3-3 | `doc/tasks/V11R-B-5.md` `allowed_paths` | 写 `Views/V2/Studio/Export*, Views/V2/Studio/Terms*`，实际实现是 `Views/V2/Studio/Controls/StudioToolsOverlay.cs` + `ViewModels/V2/Studio/StudioExportViewModel.cs/StudioTermsViewModel.cs`；`Shell/V2/Studio/StudioWorkspaceView.axaml.cs` 也被改（入口按钮） | Lead 在任务卡回填实际路径范围（或 Owner 归类说明） |
| B5-P3-4 | `verification/V11R-B-5/README.md` | 内容过薄：无质量门表、无逐 AC 覆盖表、未列 `NOT_RUN`/`test.log` 对应关系，也未写「pin 包含 B-4 I2d」这一事实 | 按 B-1/C-2 的证据规范重写 README（AC→代码/测试/证据映射 + 质量门 + 限制） |
| B5-P3-5 | `export-preflight` 截图 `TargetHint` | 假 Host 下 `ExportDirectorySuggestion` 为空，UI 显示「0 字符路径」；真实 Host 下应 >0。当前不误导（明示由 Host 授予），但文案在 0 时略怪 | 0 长度时显示「目标目录未就绪」之类 |

---

## 四、与 A-7 的关系（重要，需 Lead 决策 follow-up）

- pin `455d2c432` 上「continue_existing 未支持」是**事实**：该 pin 的 `IHostController.StartExportAsync` 无 `stalePolicy` 形参，Host 固定发送默认 `abort`（我从 pin 源码逐行核实）。
- main 现已合入 **A-7**（`IHostController.StartExportAsync(..., string? stalePolicy = null, ...)`，`HostController` 按需透传、默认 abort）。因此 B-5 的 UI 现状（禁用 continue_existing + 「未支持」文案）在 main 上**已可升级**：`StudioExportViewModel` 只需把 `CanSelectStalePolicy`/`TrySelectStalePolicy`/StartExport 调用改为使用真实参数即可。
- 结论：**不是 B-5 pin 的缺陷**，但构成「B-5 后续返修/INT-1 上收」项；建议 Lead 在派 B-5 二轮或 INT-1 时明确：暴露 continue_existing、更新 `stale-policy.json` 证据（`continue_existing_supported:true` + 真实 StartExport 传参断言）、删除「未支持」文案。
- 另：`UnconfirmedPageCount`（review 面/F0-2）在 A-7/本轮仍未提供读数，保持 `—` 正确；若 F0-2 后续落地需再上收。

---

## 五、UNVERIFIED
| 项 | 说明 |
|---|---|
| 两个 pin 的 build/test 结果 | 未重跑（禁写 bin/obj）；只核对日志数字与代码/测试清点 |
| `test.log` 与 pin 的对应 | 已证明不对应（B5-P2-1：256 vs 258，无 HEAD/EXIT） |
| 真实 Host 端到端导出（真 Core/sidecar） | 单测用 `FakeHostController` 脚本化导出面；真实 zip/pdf 产物、EXPORT_STALE 真实触发未在此环境验证（属 INT-1/E2E） |
| 真机 DPI / 大文件进度表现 | 未验证 |
| A-7 之后 continue_existing 的真实行为 | 需 ui-studio 返修后由测试覆盖 |

---

## 六、最终判断

- **可合入 main**：**可以**（pin 已合入且 App/ThemeEngine 全绿；无 P1、无用户可见伪造/数据破坏风险）。但必须在归档前完成 **B5-P2-1**（证据在 pin 上重生成 + curate 脚本 + 质量门表），否则 B-5 的证据无法作为 L3 审计依据。
- **是否达 L3（导出/术语工作面）**：本卡是 **达标候选**——预检/进度/取消/历史真实、NOT_WIRED 零伪造、只读降级正确；但 L3 还要求「证据可复核 + A-7 能力已上收」，当前两处未满足（B5-P2-1、§四 follow-up）。
- **建议下一步（可转派）**：
  1. ui-studio 返修 B-5：A-7 `stalePolicy` 上收（continue_existing 可选并真实传参）、`Esc` 键测试、证据在固定 pin 重生成 + `curate.ps1` + README 质量门表；返修 pin 建议 = `v11r/ui-studio` 新 head。
  2. Lead 回填 `doc/tasks/V11R-B-5.md` 实际写域（B5-P3-3）并把 B-5 的 `reviewer` 记录为本轮独立审查。
  3. 建议复审只覆盖：`V2StudioExportTermsTests` + `verification/V11R-B-5/*` 重生成结果 + `stale-policy` 新证据，无需重审本轮已核实项。
