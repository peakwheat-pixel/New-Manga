---
task: FEA-12-UI
review_round: r1
title: FEA-12-UI 独立上下文 Review（r1，只读）
reviewed_head: c841b9a0b
reviewed_implementation_head: d976aceec
reviewed_range: 9daa94a25..c841b9a0b
delivery_head: d976aceec
current_head_at_review: 6aff55527
reviewer: independent fresh subagent（未参与 FEA-12-UI 实现；只读被审 head）
reviewer_source: DSH Lead 派发；parent session session-8db9dae5-49df-4d09-ac62-696f0805a95c
review_environment: Windows；仓库 G:\CODEX\New Manga（main）；.NET SDK 10.0.401；Python 3.14.6
review_date: 2026-11-06
decision: CHANGES
findings: P0×0 / P1×1 / P2×3 / P3×若干（见 §6）
---

# FEA-12-UI r1 独立 Review

> **结论：CHANGES。** 单本彻底删除主链（预览披露 → 逐书 digest 绑定 → 单帧删除 → STALE/BUSY/CLEANUP_PENDING/NOT_FOUND 处置）、软删/恢复、0 purge / 0 批量、C-07 零变更、隔离证据均通过独立复跑；但 **AC7 的能力/只读态存在可观察的实现偏差（P1）**，另有 cleanup-pending 关闭文案不实（P2）、两处关键属性的测试判别力缺口（P2，已用变异证实）、卡面/Handoff pytest 基线写旧数（P2）。最小返修后应可 approve。
>
> 审查对象：`doc/tasks/FEA-12-UI.md`（in_review，AC1–AC10 均 `<<MET>>`）、Handoff `doc/handoffs/FEA-12-UI-d976aceec.md`、实现+测试+证据 `d976aceec`、`verification/FEA-12-UI/**`（14 文件）。审查时 HEAD 已前进到 `6aff55527`（Lead 的 STATUS/PLAN/LEDGER 指针提交），未改实现文件；本 Review 以 `c841b9a0b` 的树内容为准，实施内容等价于 `d976aceec`。
>
> 只读纪律：未 commit、未 push、未修改任何交付文件；变异/反证 3 项均为临时改动并已逐字节还原（`TrashViewModel.cs` = `6C9A2614…DDDD`，`HostController.cs` = `C32AADC9…4CBB`），最终 `git status` clean、`git diff --quiet` EXIT=0。

## 1. 总体判定

| 维度 | 判定 | 摘要 |
|---|---|---|
| 单本彻底删除链（AC4/AC5/AC6） | **PASS** | 预览只读、PD-01 三项 + 完整 current/artifact 计数 + 保留项声明；硬勾选 + `inventoryDigests[bookId]` 绑定；单帧删除且 payload 键集恰 3 键；STALE/BUSY/CLEANUP/NOT_FOUND typed 处置正确；旧 Core 缺 current 数组在 VM 层 fail-closed |
| 软删入口（AC2） | **PASS（证据小项 P3）** | danger confirm 默认焦点取消/Esc 不写；单帧 move；UndoBar→restore；skipped reason 白名单 |
| 回收站列表/恢复（AC1/AC3/AC7） | **AC1/AC3 PASS；AC7 FAIL** | 单帧 list、cursor 原样回传、无总数/缩略图/预览；恢复顺序/逐项 reason；**AC7 能力缺失与只读态混同（P1）** |
| C-07 / 契约 / 范围 | **PASS** | `IHostController.cs`、`RunContracts.cs`、C-07 清单 0 diff；`doc/plan`/`doc/contracts`/`src/` 0 diff；pins 18/18；API check PASS |
| 证据真实性 | **PASS** | 14 + 2 个 sha256 全部 MATCH；IPC JSON、截图、日志与卡表一致；隔离根仓外、sentinel 不变 |
| AC10 禁令 | **PASS** | 0 帧 purge、0 帧批量删除；`ITrashController` 无对应成员；真实 wire 与 fake 帧日志双重为空 |
| 文案诚实性（AC9） | **PARTIAL** | 过期“能力待接入”已清零、Fluent/页面级文案正确；但能力缺失时显示错误的“Host 只读”（P1-G2）与 cleanup 关闭的虚假可重试提示（P2-1） |
| 测试判别力 | **PARTIAL（P2）** | 逐书 digest 绑定、旧 Core fail-closed 解析两处无判别测试（变异保持全绿） |
| L3 真机 | **NOT_RUN（如实）** | 卡/Handoff/AC-MATRIX 均写 NOT_RUN，未写 PASS |

## 2. AC1–AC10 逐项判定

| AC | 判定 | 独立依据 / 问题 |
|---|---|---|
| AC1 列表与入口 | **MET** | `TrashViewModel.EnterAsync` 先 `core_ping` 再恰好 1 帧 `library_list_trash`（首帧无 cursor）；`LoadMore` 原样回传不透明 cursor；`LoadedCountText=“已加载 N 项”`、无“总数”；`Exit` 清列表/cursor/digest/勾选；迟到响应按 `_generation` 隔离；进入回收站时 `ShowSideDetail/ShowOverlayDetail/ShowPageBulkBar=false`。测试 `Enter_*`/`LoadMore_*`/`LateListResponse_*`/`EnterRecycleBin_*` 独立通过。P3：`LoadMoreAsync` 无 `IsLoadingMore` 防重入（双击可发两帧同 cursor，正常 UI 隐藏按钮）。 |
| AC2 软删入口 | **MET（证据 P3）** | 详情「移入回收站」走 `ConfirmRequest(IsDanger:true)`；shell 默认焦点 `CancelButton`、Esc 关闭、Enter 不隐式提交；确认后恰 1 帧 `library_move_to_trash`，payload 键集 `{entries,idempotency_key}`（`TrashPayloads.MoveOrRestore` + CoreClient wiring 测试覆盖）；成功后才刷新/清选中/显示 UndoBar；撤销走 `RestoreFromTrash` + 恢复自身 idempotency key。P3：测试未断言“书架不再含该书”（fake 不更新书籍列表，只断言 `Selection.HasBook=false`）。 |
| AC3 恢复 | **MET** | 勾选顺序写入 `_selectionOrder`，单帧 restore；`restored` 行移除、`conflicts` 行保留并逐项显示 reason；白名单 + 兜底（未知码显示“未分类冲突（CODE）”）；不伪报整批成功。测试 `Restore_*` 通过。 |
| AC4 预览披露 | **MET（P2 证据缺口）** | 一次 preview 帧（`bookIds:[id]`）；PD-01 三项 + `lockCount`/`currentRevisionId`（仅代表）+ 完整 current 集合计数 + artifact 计数 + `pinnedRevisionIds`/`activeRunIds` 计数 + `contentSummary` + `sharedFileRefs` + 保留项声明；文本不含路径/源文件名；旧 Core 缺 current 数组时 VM 层 `CurrentSetKnown=false` → 禁止确认；预览失败就地错误 +「重新预览」。**P2-2b**：`OldCorePreview` 直接构造 DTO 绕过 `HostController.TrashStringArrayOrUnknown`，真实 IPC 只测新 Core，适配器“缺字段 fail-closed”无判别测试。 |
| AC5 专门确认与 digest 绑定 | **MET（P2 证据缺口）** | 未勾选 0 删除帧；勾选后单帧，payload 键集恰 `{book_id, confirm_permanent_delete, inventory_digest}`；绑定值取 `inventoryDigests[bookId]`（VM:551）；真实 wire 显示 collection digest ≠ per-book digest，删除帧使用 per-book；STALE 清勾选 + 自动重预览且不重发删除；`activeRunIds` 非空预阻断。**P2-2a**：fake 的集合 digest 与逐书 digest 相同，改成集合 digest 后 23/23 仍绿（见 §5 M1）——绑定选择无判别测试。 |
| AC6 stale / busy / 结果处置 | **MET（文案缺陷归 AC9）** | STALE：清确认 + 自动重预览、删除帧计数 1；BOOK_BUSY 预阻断零删除帧（M2 变异可红，判别有效）；CLEANUP_PENDING：同 digest 重试、无新 preview，二次/关闭后的 NOT_FOUND 刷新；`BOOK_NOT_FOUND` 刷新；CONFLICT/FAILED/INVALID_REQUEST 走 typed 默认分支，不静默、不自动重试。**P2-1**：cleanup_pending 时点「关闭结果」提示“本会话内仍可重试清理”，随后 `ResetPreview()` 清空 digest/cleanup 状态 → 实际不可重试（见 §6）。 |
| AC7 能力 / 只读 / 不可用 | **NOT MET（P1）** | 全能力缺失：`ShowCapabilityState`、0 list 帧、不渲染空列表（测试通过）。但：①`_writesAvailable = writesAllowed && WriteAvailable && PreviewAvailable`（VM:349）、`IsHostReadOnly = !_writesAvailable`（VM:149）、`CanRestore = CanWrite`（VM:175）把三类能力与 Host 只读混为一谈；②只缺 preview 时 restore 被误禁（违反“按操作禁用”），typed `CORE_CAPABILITY_MISSING` 文案因 `ShowCapabilityState=false` 不可见；③任一能力缺失/全缺时 `RecycleBinView.axaml:66` 显示“Host 处于只读模式：回收站可浏览…”（全缺时与“回收站暂不可用”矛盾，且 Host 实际并非只读）；④`HOST_READ_ONLY` 字面未展示；⑤probe 失败（`CORE_UNAVAILABLE`）被归为能力缺失（文案称 Core 未公布能力），无独立失败态。 |
| AC8 无 DB/OS 直连 + 隔离 | **MET（P3）** | `NoDbOsAccessTests` 本卡 9 文件 0 命中、全 App 0 DB、既有 `HostController` 单个 `Directory.Create` 登记不变；真实 IPC DataRoot 在仓外、sentinel 树前后指纹相等（我的复跑指纹与交付相同）。独立 grep 复现：卡写域 9 文件对 `sqlite`/`Microsoft.Data.Sqlite`/`System.Data.SQLite`/`DllImport`/`Shell32`/`SHFileOperation`/`IFileOperation`/`File.Delete`/`Directory.Delete`/`Microsoft.VisualBasic.FileIO` **0 命中**；App 其他文件仍有既有 OS 命中（ThemeStudio/Program/SourceImportModels 与 HostController 的既有 `Directory.Create` 等，均非本卡写域、未被本卡触碰），全 App 数据库访问扫描 0。P3：AC8 提到的“路径泄露扫描”无独立测试（面板无路径由代码审阅确认）。 |
| AC9 文案诚实性 | **PARTIAL** | 过期回收站“能力待接入/未发布回收站”已清零（全 App grep 仅剩导出/标记等非回收站文案）；能力缺失显示 `CORE_CAPABILITY_MISSING`；Fluent 抽屉/tooltip 不称能力缺失、不含实现类名；页面级删除改“页面级删除无命令”；无总数、无逐项 busy。**但** AC7-G2 的假“Host 只读”与 P2-1 的假“仍可重试”属不实文案；P3：头部/空态称“恢复…都会先确认”（恢复无确认）、AC5 写“pinned revision N”而非“固定版本 N”。 |
| AC10 禁令与门禁 | **MET（P3）** | 真实 wire + fake 全流程 0 帧 `library_purge_trash`、0 帧批量；`ITrashController` 反射断言无 purge/batch 成员；删除 payload 无批量字段；全量 .NET 1474/0/82（独立复跑）；pins 18/18；API check PASS；`check.ps1 -TaskPath` PASS（3 既有 warning，我的复跑）。**P3**：交付证据 `gates.log` G8/Handoff 对 check.ps1 只写“见交付后复跑”，未记录 PASS 结果（独立复跑补足）。 |

## 3. 独立复跑（2026-11-06，repo main）

### 3.1 全量 .NET

命令：`dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo`；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build --nologo`。

- BUILD：EXIT 0，0 warning / 0 error。
- 汇总：**1474 passed / 0 failed / 82 skipped / 1556 total**（与卡面一致）。
- 分列：App.Tests **703/0/7**；Host.Tests **144/0/51**；CoreClient **167/0/24**；ThemeEngine 253/0/0；DesignSystem 117/0/0；Presentation 38/0/0；ApplicationCore 31/0/0；Appearance 21/0/0。
- flaky：**首跑 0 失败，无需复跑**（FEA-11 已知 `FluentResidual2VisualEvidenceTests` 噪声本卡未出现）。
- 跑后 `verification/FEA-09/logs/wire-redacted.ndjson` 被既有行为重写，已 `git checkout -- verification/FEA-09` 恢复；最终 `git status` clean。

### 3.2 定向 UI / 真实 IPC

- 定向 UI（curated 证据写到仓外临时目录，未写 repo）：**28/28 PASS**（`TrashUiTests` 23、`NoDbOsAccessTests` 3、2 个真实窗口交互）；4 张 1600×1000 真实窗口截图重新生成。**07/08/10 与交付 PNG 逐字节相同**；09（danger confirm）字节不同（焦点/渲染时序差异，非内容或断言失败）。
- 真实 IPC：`NEWMANGA_FEA12_UI_IPC=1` + `Fea12TrashUiIpcTests` → **1/1 PASS**；真实 `src/bootstrap/core_service.py`；**27 wire 帧**；`purge_frames=false`、`batch_permanent_delete_frames=false`；`collectionDigest ≠ perBookDigest`（本次 `0f18a1e5…` vs `4ff86e80…` 口径与结构一致，书 ID/digest 为新生成）；`dataRootOutsideRepo=true`；sentinel 指纹前后相等（`cb20e326…`，与交付相同）。
- note：IPC 日志显示“持续时间 ~60 ms”是 xUnit 对方法体的计时，fixture 启动未计入；实际命令墙钟约数十秒，非异常。

### 3.3 契约 / 门禁

| 门禁 | 结果 |
|---|---|
| `verify_pins.ps1` | **PASS 18/18**，EXIT 0 |
| `generate_api_inventory.py --check` | **PASS**，EXIT 0；`IHostController 54` 方法未变；`ITrashController` 不在 C-07 解析清单 |
| `check.ps1 -TaskPath doc/tasks/FEA-12-UI.md` | **PASS (3 warnings)**，EXIT 0（11 非终态 Task、STATUS 80% 预算、PLAN 80% 预算，均为既有类型） |
| `git diff --name-only 9daa94a25..HEAD -- doc/plan doc/contracts src/` | **空** |
| `IHostController.cs` / `RunContracts.cs` / `FEA-C07_API_INVENTORY.md` / `FEA-CONTRACT-FROZEN-*` | **0 diff** |
| `NewManga.Host/**` / `NewManga.CoreClient/**` / `NewManga.DesignSystem/**` / `SourceImportModels.cs` | **0 diff** |
| 新依赖 / schema / wire / Python | **无**（`src/` 零 diff；无 `.csproj`/schema 变更） |

## 4. 证据 / 范围 / 资源核对

- `verification/FEA-12-UI/**` 恰 **14 个文件**（4 PNG + AC-MATRIX/ENVIRONMENT/IPC JSON/manifest + 6 log），与卡 EV-01…EV-14 一一对应；**全部 sha256 与卡表/agent-output-manifest 逐字节 MATCH**。
- 卡中 EV-15/16 两个 SOURCE_PIN（`NoDbOsAccessTests.cs` `2eee15…`、`Fea12ProductionFixture.cs` `d635a9…`）独立复算 **MATCH**。
- `d976aceec` = 10 App 生产 + 4 App 测试 + 2 Host 测试 + 14 证据 = 30 文件，**全部在 allowed_paths**；`c841b9a0b` = 卡 + Handoff，均在 allowed_paths；`doc/STATUS.md`、`REBASELINE_PLAN.md`、`TASK_LEDGER.md`、`doc/reviews/**` 未出现在这两个交付 commit（range 内的 FEA-11 closeout `c286e0824` 与 Lead 指针 `6aff55527` 属他人提交）。
- 未 push：`d976aceec`/`c841b9a0b` 仅在本地 main；`git branch -r --contains` 无远端包含（本地 main 整体领先 origin/main 属既有状态）。
- 工作树：Review 前后 **clean**；未提交/推送；变异文件按原始字节还原。
- 证据卫生：`verification/FEA-12-UI/` 非本卡 spill 已整体归档到 `G:\CODEX\New Manga.workspace\archive\FEA-12-UI-spill-2026-11-06\`（`spill-tree`/`moved-tree`，共 322 文件），卡 Resource Manifest/Handoff/manifest `workspace.archived_spill` 均有登记，且明确“不属 Canonical Evidence”。**P3**：manifest 的 `archived_spill` 只有 path/note，未附文件清单或 hash；卡表“sha256/manifest”列指向它但无法核验指纹。
- 隔离：真实 IPC 的 DataRoot/日志/sidecars 在 `G:\CODEX\New Manga.workspace\FEA-12-UI\ipc-<guid>`（仓外），sentinel 在 DataRoot 外、前后 SHA-256 相等；原文件零触碰。
- 资源处置：`temp` DELETE_SAFE、`ipc-*` PRESERVE_REFERENCED、spill ARCHIVED、worktree NOT_APPLICABLE，与 Handoff 一致；本 Review 的复跑产物全部写在 `G:\CODEX\New Manga.workspace\FEA-12\review-ui-1\temp\`（仓外）。

## 5. 变异 / 反证（临时改，已还原）

| # | 变异 | 预期 | 实测 | 结论 |
|---|---|---|---|---|
| M1 | `TrashViewModel.cs:551` `_activeDigest = boundDigest`（逐书）→ `preview.InventoryDigest`（集合） | 单测应变红 | `TrashUiTests` **23/23 全绿** | **判别缺口（P2-2a）**：fake `DefaultPreview` 的集合 digest 与逐书 digest 均为 `sha256:aaaa…`，无法区分；R12 绑定只有代码审阅与 Host 级 IPC 证明，VM 绑定无回归保护 |
| M2 | 删除 `BuildBlockedReason` 的 `activeRunIds>0` 预阻断块 | `BusyTarget_IsPreBlocked_NoDeleteFrame` 应变红 | **恰好 1 红**（`PreviewBlockedReason` 为 null），其余 22 绿 | **判别有效**；BOOK_BUSY 预阻断被测试真实保护 |
| M3 | `HostController.TrashStringArrayOrUnknown` 缺字段/null/非数组 → `Array.Empty<string>()`（fail-open） | 旧 Core fail-closed 测试应变红 | `Fea12TrashUiIpcTests` **1/1 仍绿**（旧 Core 路径无测试；`OldCorePreview` 绕过 HostController） | **判别缺口（P2-2b）**：AC4 适配器 fail-closed 无测试保护 |

还原核验：`TrashViewModel.cs` = `6C9A26146BA02E28B7EC36C47E577BD6E7C398ABE91DC8B2496D34ADFDBDDBDD`（与改动前一致）、`HostController.cs` = `C32AADC90DA848CCAA488750E0C401E92467C4F082CE6855ED7DFAE94E5E4CBB`（一致）；`git status` clean、`git diff --quiet` EXIT=0；还原后重建并复跑定向 UI 28/28 绿。

## 6. Findings（按严重度）

### P1-1（阻断 AC7 MET）能力缺失 / Host 只读 / probe 失败三态混同

**证据（代码）**：

- `TrashViewModel.cs:349`：`_writesAvailable = _writesAllowed() && probe.WriteAvailable && probe.PreviewAvailable;`
- `TrashViewModel.cs:149`：`public bool IsHostReadOnly => !_writesAvailable;`
- `TrashViewModel.cs:151/175`：`CanWrite = _writesAvailable && …`；`CanRestore = HasSelection && CanWrite && !IsBusy`
- `TrashViewModel.cs:344-353`：`_capabilityMissing = !probe.Probed || !probe.ReadAvailable`；仅 `!WriteAvailable` 时覆写 `_capabilityMessage`；preview 缺失没有可见状态（能力面板只在 read 缺失时显示，`_capabilityMessage` 即使非空也不渲染）
- `RecycleBinView.axaml:65-67`：`IsVisible="{Binding Trash.IsHostReadOnly}"`，文案“Host 处于只读模式：回收站可浏览，但恢复与彻底删除已禁用”
- `RecycleBinView.axaml:33-40`：能力缺失面板只在 `ShowCapabilityState` 时可见

**可观察后果**（按 AC7 ①/②/⑤）：

1. **只缺 `library.delete.preview/1`（read/write 有）**：`_capabilityMissing=false` → 不显示能力缺失态，`CORE_CAPABILITY_MISSING` 不可见；`_writesAvailable=false` → **restore 被误禁**（应仅由 write 决定）；同时显示假的“Host 处于只读模式”。
2. **只缺 `library.trash.write/1`**：列表可读、写入本应禁用；restore 禁用正确，但仍显示假的“Host 只读”，且能力缺失码只在被覆写的 `_capabilityMessage` 中、该消息不渲染。
3. **三项全缺**：能力面板“回收站暂不可用”与只读 banner“回收站可浏览”同时出现，自相矛盾。
4. **probe 抛 `CORE_UNAVAILABLE`**（Host 未就绪/通道失败）：`Probed=false` → 归为能力缺失，面板文案称“Core/宿主未公布回收站能力”，不是 AC7 ③ 的失败态 + 明确重试入口（只有常驻头部“刷新”可重试）；实际只读/能力状态未区分。
5. **`HOST_READ_ONLY` 字面**未在任何状态向用户展示（只有自然语言“Host 只读/处于只读模式”）。

**最小返修点**：

- 独立跟踪 `_hostReadOnly = !_writesAllowed()`，`IsHostReadOnly` 只反映 Host 策略；能力缺失时**不**渲染只读 banner。
- 用 `ReadAvailable` / `WriteAvailable` / `PreviewAvailable` 分别控制：`CanRestore = HasSelection && writeAvailable && !busy`；删除入口/确认 = `writeAvailable && previewAvailable`；列表 = `readAvailable`。
- 任何能力缺失都渲染 typed `CORE_CAPABILITY_MISSING`（可新增 `ShowCapabilityDegraded`），并在对应操作旁给出原因；`CORE_UNAVAILABLE` probe 失败走失败态 + 重试。
- 增测试：三个“单能力缺失”用例 + probe 失败用例，断言不出现假只读文案、typed code 可见、按操作启停正确。

### P2-1 cleanup_pending 关闭结果后的“仍可重试”文案不实

`TrashViewModel.cs:722-737`：`CloseResult()` 在 `_cleanupPendingVisible && HasDeleteResult` 时 `_notify("已记录待清理状态：本会话内仍可重试清理", NmStatus.Queued)`，随即 `ResetPreview()` 清空 `_cleanupPendingVisible`、`_activeBookId`、`_activeDigest`；`CanRetryCleanup`（VM:270）依赖这些字段，之后无 pending 清单命令可恢复 → **实际不可重试**。这违反 AC6/L3 的“不得误报可恢复性”与 AC9 诚实性。

**最小返修**：关闭结果时保留 pending 状态（只隐藏结果面板，保留 `bookId+digest` 与“重试清理”入口），或把文案改为“关闭后将无法在本会话内重试清理”；并增加测试断言关闭后 `CanRetryCleanup` 与文案一致。

### P2-2 证据判别力缺口（已用 M1/M3 证实）

- **2a（AC5/R12）**：把 VM 绑定值换成集合 digest，`TrashUiTests` 23/23 仍绿。`FakeHostController.DefaultPreview`（tests/.../FakeHostController.cs）集合 digest 与逐书 digest 相同（`sha256:aaaa…`），`Delete_SendsExactlyOneFrame…` 的断言无法区分；真实 IPC 从 `preview.Digests` 直接调用 `DeletePermanentlyAsync`，**不经过 VM**。因此“单本必须用 `inventoryDigests[bookId]`”在 UI 层只有代码审阅，无回归测试。
- **2b（AC4 旧 Core fail-closed）**：把 `HostController.TrashStringArrayOrUnknown` 改成 fail-open，全部测试仍绿。`OldCorePreview` 直接构造 `TrashProtection(null,null)` 绕过 HostController JSON 投影；真实 IPC 只测新 Core（两数组存在）。适配器“缺字段/null → unknown → 禁止确认”没有被任何测试覆盖。

**最小返修**：

- 把 `DefaultPreview` 的集合 digest 改成与逐书不同的值（并保持逐书断言），使 M1 类回归变红；或新增一个 fake 预览：集合/逐书不同且断言删除 payload == 逐书。
- 将 `HostController` 预览投影抽出为可测的 internal 静态 helper（或给 `Fea12ProductionFixture` 增加脚本化旧 Core 响应），补 `缺字段`/`null`/`[]`/非法形状 四类测试；`[]` 必须仍可确认，缺/null 必须禁止。

### P2-3 卡面/Handoff 的 pytest 基线写旧数

`doc/tasks/FEA-12-UI.md:182` 与 `doc/handoffs/FEA-12-UI-d976aceec.md:74` 写“pytest 引用 FEA-11 基线 **3073/10**”。当前全量基线为 **3203 passed / 10 skipped**（`doc/handoffs/FEA-11-MATCH-1-handoff.md`、`doc/tasks/FEA-11-MATCH-1.md`、`doc/reviews/FEA-11-MATCH-1-r2.md`、`doc/tasks/FEA-11-SCAN-1.md` 均为此口径）。本卡零 Python 改动、未重跑是诚实的，但旧数不得写入卡面/证据；按 Review 要求记为 P2。

**最小返修**：两处改为“3203 passed / 10 skipped（引用；本卡零 Python 改动，未重跑）”，或删去数字只保留“零 Python 改动、未重跑”。

### P3（建议随返修一并处理，不单独阻断）

1. `LibraryViewModel.cs:1048` `CloseRecycleBinLegacyPlaceholderRemoved()` 为无引用死方法，且注释与“public”自相矛盾。
2. `RecycleBinView.axaml:16/59` 称“恢复或彻底删除都会先确认/需显式确认”；恢复（`RestoreSelectedAsync`）无二次确认，仅勾选 + 按钮。
3. `TrashViewModel.cs:861` 用“pinned revision N 个”，AC5 文案要求“固定版本 N”；建议统一术语。
4. `LibraryViewModel.BeginPermanentDeleteForSelection`：未选中任何行时取 `Items.FirstOrDefault()`；按钮文案“彻底删除选中（单本）”与“默认第一项”不一致（建议无选中时禁用或明示）。
5. `HostController.cs:2887`：move 的 `ok` 在“响应为对象但无任何逐项结果（`{}`）”时为 true，VM 再 fallback `[bookId]` → 极端 invalid-response 下可能伪成功；`{moved:[],skipped:[]}` 又会被 :2878 判为“缺少逐项结果”。建议统一为“必须 `moved`/`restored` 数组且成功项>0 才算 ok”，否则 typed failure。
6. 交付证据未记录 `check.ps1` PASS（`gates.log` G8/Handoff 写“见复跑”）；本次独立 PASS，建议 closeout 前补一行结果。
7. Resource Manifest 的 `archived_spill` 无文件清单/hash（322 文件）；建议至少登记 tree 级清单或关键文件 hash。
8. `HostController.ProbeTrashCapabilitiesAsync` 的 `CORE_UNAVAILABLE` 被 VM 归为能力缺失（P1-1 第 4 点）；`HOST_READ_ONLY` 字面未展示（P1-1 第 5 点）。
9. AC2 “成功后书架不再含该书”未被测试断言（fake 不更新 books）；建议 fake 在 move 后移除该书或补断言。
10. AC8 的“路径泄露扫描”无独立测试；AC4 “面板无路径/源文件名”也无断言（实现由代码审阅确认）。建议补一个文本断言。
11. `TrashViewModel.LoadMoreAsync` 无 `IsLoadingMore` 防重入；UI 隐藏按钮时无实害，但建议加 guard。
12. `TrashViewModel.ResetPreviewKeepTarget` 中 `_generation = generation` 为无效赋值（`ResetPreview` 不改 generation）；可删。
13. `TrashCopy.RestoreReason(null)` 为“未分类冲突”，AC3 示例为“恢复冲突（未分类）”；未知码显示“未分类冲突（CODE）”（AC7 允许诊断展示），建议统一措辞。

## 7. Limitation / L3 核对

- 卡 L1–L10 与实现/证据一致：批量无 UI、无缩略图/内容预览、cleanup 重试仅会话内、无总数/逐项 busy、restore reason 首版恒 `TRASH_ENTRY_NOT_FOUND`、activeRunIds 不含 export、Fluent 回收站未接线、D 流程 NOT_RUN、无保留期限、L3 真机 NOT_RUN。
- **L3 真机走查如实 NOT_RUN**：卡、Handoff、AC-MATRIX 均未写 PASS，符合 Q8/L10。
- 注意：卡 L3 写“重试仅当前会话可用”，实现上点“关闭结果”后即失去重试（P2-1），比 L3 更窄；返修后应让实现与 limitation 口径一致。
- 未声称 L4/真机验收；未声称 pytest 重跑（但基线数字错误，P2-3）。

## 8. Closeout 建议

- `delivery_head`：**`d976aceec`**（实现+测试+证据）；reviewed head **`c841b9a0b`**（卡+Handoff）。
- `integration_commit`：**待 Lead（DSH）集成时填写**；`canonical_evidence_status` / `resource_closeout_status` 仍为 pending，本次 Review 不代填。
- **L3 真机：NOT_RUN**（冻结 OUT/L10，须另行授权；不得写 PASS）。
- 建议处置顺序：先按 P1-1 + P2-1 做最小返修（AC7 三态拆分/按操作门控 + cleanup 关闭语义），P2-2 补两个判别测试，P2-3 修正基线数字；P3 择要处理。返修后复跑：全量 .NET 不减少、定向 UI、真实 IPC、pins/API/check，并补齐 `check.ps1` 证据行。
- 若 Lead 决定以“当前 Core 永远公告三能力、partial 不可达”为由接受 P1-1，应至少在卡内登记 limitation 并移除“AC7 全 MET”表述；否则按 CHANGES 返修。
- 本 Review 的独立复跑产物（全量日志、定向 UI 日志、IPC JSON、变异日志、复算截图）位于 `G:\CODEX\New Manga.workspace\FEA-12\review-ui-1\temp\`，未写入 repo、未提交。

## 9. 审查者独立性声明

本 Review 由 DSH Lead 派发的独立上下文 fresh subagent 执行，未参与 FEA-12-UI 的实现、返修或证据制作；仅只读被审 head 并按需做可还原的变异验证。审查依据：卡/Handoff/证据、C-04b v1.1、M2-C1 rev 2.14 §5.11/§5.13/§5.14、C-09 SC-B06、ADJ-001 PD-01/02/04、SCOPE-ADJ-2026-11-05 B 节与 C-07。报告写入仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-ui-1\`，由 Lead 决定是否落盘 repo。

UI-R1-REVIEW: CHANGES — P1×1（AC7 能力/只读态混同：false read-only 文案 + 按操作门控失败）/ P2×3（cleanup 关闭虚假可重试；VM 逐书 digest 与 Host 旧 Core fail-closed 无判别测试；卡面/Handoff pytest 3073/10 旧数）；核心单本删除链、0 purge/0 批量、C-07 零变更、证据哈希与隔离均 PASS；最小返修后建议 approve。
