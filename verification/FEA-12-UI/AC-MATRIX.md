# FEA-12-UI AC Matrix（L2 证据）

- 卡：`doc/tasks/FEA-12-UI.md`；base `9daa94a25`；证据根 `verification/FEA-12-UI/`
- 结果时间：2026-11-06（Asia/Shanghai）；实现 head 见 Handoff 与卡 frontmatter `delivery_head`
- 结论总览：AC1–AC10 全部 **MET**（L1–L10 limitation 见卡）；L3 真机 **NOT_RUN**（冻结 OUT/L10，不写 PASS）

## 门禁与实测结果

| 场景/AC | 命令/环境 | 实际结果 | 证据 |
|---|---|---|---|
| 全量 .NET（AC10） | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo`；`dotnet test ... --no-build --nologo` | **PASS**：8 个测试程序集合计 **1474 passed / 0 failed / 82 skipped**；App.Tests **703/0/7**、Host.Tests **144/0/51**（含本卡 IPC 测试默认 skip 理由）、CoreClient 167/0/24；无失败 | `logs/dotnet-full-solution.log` |
| UI 定向（AC1–AC7/AC9/AC10） | `dotnet test NewManga.App.Tests -c Release --no-build --filter "FullyQualifiedName~TrashUiTests\|NoDbOsAccessTests\|V2ShellUiTests.RecycleBin\|V2ShellUiTests.MoveToTrash"`（curated 时设 `NEWMANGA_EVIDENCE_DIR`） | **PASS 28/28**：`TrashUiTests` 23、`NoDbOsAccessTests` 3、2 个真实窗口交互测试（含 4 张截图） | `logs/ui-tests-curated.log`、`screens/*.png` |
| 真实 IPC（AC1/AC5/AC6/AC8/AC10） | `NEWMANGA_FEA12_UI_IPC=1` + curated `NEWMANGA_EVIDENCE_DIR`；真实 `src/bootstrap/core_service.py`（非冻结旧 sidecar） | **PASS 1/1**：真实 Host→Python Core stdio；wire 27 帧；`purge_frames=false`、`batch_permanent_delete_frames=false`；DataRoot 在仓外；哨兵树前后 SHA-256 相等 | `fea12-trash-ui-ipc.json`、`logs/ipc-tests-curated.log` |
| pins（AC10） | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS 18/18**（EXIT 0） | `logs/pins.log` |
| API inventory / C-07（AC10） | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **PASS**（EXIT 0；`IHostController.cs` 零改动，`ITrashController` 为独立 App 端口不参与 C-07 解析） | `logs/api-inventory.log` |
| 契约/计划零漂移（AC10） | `git diff --name-only 9daa94a25..HEAD -- doc/plan doc/contracts src/` | **空**（零契约/计划/Python 生产改动；18 pins 不受影响） | Handoff/本文件 |
| L3 真机走查 | 人工 L3/L4 | **NOT_RUN**（卡 L10/OUT） | — |

## AC 对照

| AC | 要求（卡内摘要） | 实现/证据 | 结论 |
|---|---|---|---|
| AC1 | 进入回收站先探测能力，再**恰好一帧** `library_list_trash`；只读披露→硬勾选+digest 绑定→单帧 `library_delete_book_permanently`；payload 键集 `{bookIds}`（预览）；不显示总数、cursor 不持久化、无缩略图；退出/重进清 digest/勾选；迟到响应隔离 | `TrashViewModel.EnterAsync`：`core_ping`（probe）→ 1×list；`LoadMoreAsync` 只回传不透明 cursor；`Exit()` 清空列表/digest/确认；`_generation` 隔离迟到响应。`TrashUiTests.Enter_*`/`LoadMore_*`/`Exit_*`/`LateListResponse_*`；真实 IPC 27 帧证据 | **MET** |
| AC2 | 书架「移入回收站」危险确认（默认焦点取消、Esc 关闭、Enter 不提交）→ 恰好一帧 `library_move_to_trash`（`entries=[{book_id}]` + `idempotency_key`）；成功后才移除并清选中；skipped 逐项 reason；成功条可撤销（恢复成功才成功） | `LibraryViewModel.RequestMoveSelectedToTrash` + `MoveSelectedBookToTrashAsync` + `UndoMoveToTrashAsync`；`V2ShellUiTests.MoveToTrash_DangerConfirm_*`（Esc/Enter 零帧、确认后 1 帧、UndoBar）；`TrashUiTests.MoveToTrash_*`/`Undo*`；`TrashCopy.MoveSkipReason` 白名单文案 | **MET** |
| AC3 | 勾选 2 项恢复 → 单帧 `library_restore_from_trash`，entries 顺序=勾选顺序；restored 移除、conflicts 保留且逐项 reason；不伪报整批成功；白名单+兜底 | `_selectionOrder` 维护勾选顺序；`RestoreSelectedAsync` 逐项应用；`TrashCopy.RestoreReason`（`TRASH_ENTRY_NOT_FOUND` 白名单，其余 → 暂未分类/未分类兜底，不编造因果）；`TrashUiTests.Restore_*` | **MET** |
| AC4 | 披露面板先出现；确认前仅 1 帧 preview（`bookIds:[id]`）；PD-01 三项 + 完整 current 集合 + 受保护 artifact 表达 + 保留项声明；文本无路径/源文件名；预览零副作用；旧 Core 缺字段 fail-closed；typed 失败就地错误+重新预览 | `TrashViewModel.BeginPermanentDeleteAsync` 解析 `protection.currentRegionRevisionIds`/`currentArtifactRevisionIds`（缺失/null → `CurrentSetKnown=false` → 阻断）；`PreviewProtectionText` 展示 PD-01 数字与 complete current/artifact 计数；XAML 保留项声明；`revision` 面板文本不含路径；preview 只读（Core 侧 PD-03，wire 证据）。`TrashUiTests.Preview_*`/`OldCore*`；快照 `--08` | **MET** |
| AC5 | 未勾选 ⇒ 确认禁用且 0 删除帧；勾选后 1 帧，payload 恰 `{book_id, confirm_permanent_delete, inventory_digest}`；digest 逐字节等于**本次预览逐书 digest**；STALE → 清确认+自动重预览不重发删除；`activeRunIds` 非空预阻断 BOOK_BUSY | 确认门 `CanConfirmDelete`（勾选+已知 current+非 busy+可写+digest）；删除 payload 键集断言（fake 与真实 wire 双重）；`inventoryDigests[bookId]` 作为绑定 digest（真实 IPC 证明集合 digest ≠ 逐书 digest，且删除只用逐书）；STALE 分支 `BeginPermanentDeleteAsync` 重预览 | **MET** |
| AC6 | stale/busy/cleanup_pending（同 digest 重试、无新 preview；二次→NOT_FOUND）/BOOK_NOT_FOUND 刷新/CONFLICT/FAILED 保留条目 typed/INVALID_REQUEST 如实报错 | `TrashDeleteOutcome` 全分支处置；`RetryCleanupAsync` 复用 `_activeDigest`；`BookNotFound_*`、`CleanupPending_*`、`StalePreview_*`、`BusyTarget_*` 测试 | **MET** |
| AC7 | 3 capability 缺失 fail-closed（不显示空列表）；只缺写/preview 允许只读列表；Host 只读禁用写 + `HOST_READ_ONLY`；`CORE_UNAVAILABLE` 失败态+重试；未注册码仅诊断；按操作禁用 | `ProbeTrashCapabilitiesAsync` 解析 `core.ping` 三能力；`CapabilityMissing_FailsClosed_NoListFrame`、`OldCoreWithoutCapabilityList_*`、`HostReadOnly_BrowsesButBlocks*`；`CORE_CAPABILITY_MISSING` 文案可见；`RetryPreviewCommand` | **MET** |
| AC8 | App 静态扫描本卡新增 0 处 DB/OS 直连；真实 IPC 隔离根在仓外 + 哨兵指纹相等；路径泄露扫描按敏感字段 | `NoDbOsAccessTests`（本卡 9 个文件 0 命中；全 App 无 DB 访问；`HostController.cs` 既有 `Directory.CreateDirectory` 单独登记）；IPC 证据 `dataRootOutsideRepo=true`、`sentinelUnchanged=true`、`sentinelFingerprint` | **MET** |
| AC9 | 清除过期“回收站能力待接入/未发布”文案；能力缺失用 typed code；Fluent 抽屉/tooltip 不声称能力缺失、不展示实现类名；页面级删除改“页面级删除无命令”；不伪造总数/busy | `RecycleBinView` 真实列表/空态/失败态/能力缺失态/只读态；`ShelfPageView` 抽屉与 tooltip 改为“Fluent 前端未接线、请用 V2 前端”且不含“能力待接入”；`DeleteSelectionCommand` 文案；`PageLevelDeleteCopy_*` 测试；`LoadedCountText`=“已加载 N 项”无“总数” | **MET** |
| AC10 | 全流程 0 帧 `library_purge_trash`；0 帧批量 `library_delete_books_permanently`；删除 payload 从未出现 batch 字段；全量 .NET 不减少（分列）；API check/pins 18/18/check.ps1 PASS；L2 完成、L3 NOT_RUN | `ITrashController` 无 purge/batch 成员（`Port_HasNoPurge*` 断言）；fake 与真实 wire 均 0 purge/0 batch；`FullFlow_NeverEmitsPurgeOrBatchFrames`；IPC `deleteFrames` 仅 3 键；门禁见上表 | **MET** |

## 判别性证据要点（Review 可直接复核）

1. **单帧语义**：`TrashUiTests` 断言 probe→list 恰好 1 帧；删除帧计数=1（stale 分支 1 preview+1 delete+1 preview，无第二次 delete）；cleanup 重试不产生新 preview。
2. **digest 绑定**：`fea12-trash-ui-ipc.json` 中 `collectionDigest ≠ perBookDigest`；wire 删除帧的 `inventory_digest` 等于 `perBookDigest`，证明绑定的是逐书值（集合 digest 会被 Core 判 STALE）。
3. **fail-closed**：旧 Core 缺 `currentRegionRevisionIds`/`currentArtifactRevisionIds` 时，即使勾选理解也无法确认（0 删除帧）；能力缺失时 0 列表帧、不渲染空列表。
4. **禁令**：真实 wire 与 fake 帧日志中 0 帧 purge、0 帧批量删除；`ITrashController` 接口无对应成员。
5. **隔离**：真实 IPC 的 DataRoot 位于 `G:\CODEX\New Manga.workspace\FEA-12-UI\ipc-*`（仓外），哨兵树（含“原文件零触碰”文本）SHA-256 前后一致。

## Limitations（预登记 L1–L10，逐项保留）

- L1 批量彻底删除无 UI（Core 有能力；单书库批量死路）—OUT。
- L2 回收站无缩略图/内容预览（读门控边界，另卡）—OUT。
- L3 `cleanup_pending` 重试仅当前会话可用（无 pending 清单命令）。
- L4 列表无总数、无逐项 busy（wire 缺口）；只显示“已加载 N 项”。
- L5 restore 冲突 reason 首版恒为 `TRASH_ENTRY_NOT_FOUND`；其余码按白名单+兜底渲染，不编造因果。
- L6 导出占用只在删除时以 `BOOK_BUSY` 暴露（`activeRunIds` 不含 export）。
- L7 Fluent 前端回收站仍不可用（仅文案诚实化）。
- L8 真实 Windows 回收站（D 流程）仍 NOT_RUN。
- L9 保留期限/自动清理无 UI 承诺（B 流程 OUT）。
- L10 本卡证据只到 L2；L3/L4 真机未跑（NOT_RUN，须另行授权）。

## 证据归档说明

- `verification/FEA-12-UI/` 曾存在**非本卡**的未跟踪历史/意外同步证据（旧日期与全量 solution 运行落盘）。本卡已将其整体移动到
  `G:\CODEX\New Manga.workspace\archive\FEA-12-UI-spill-2026-11-06\`（保留原树 `spill-tree`/`moved-tree`），
  仅在本目录保留本卡证据；该归档不属于 Canonical Evidence。原因与命令见 Handoff「资源处置」。
