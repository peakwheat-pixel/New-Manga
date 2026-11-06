---
task: FEA-12-UI
review_round: r2b
title: FEA-12-UI r2 窄面独立复审（只读；r1 P1/P2/P3 核销 + 回归）
reviewed_head: 233d73f21
reviewed_implementation_head: a46d4d5c7
reviewed_range: 9daa94a25..233d73f21
base_commit: 9daa94a25
r1_implementation_head: d976aceec
delivery_head: a46d4d5c7
reviewer: independent fresh subagent（未参与 FEA-12-UI 实现或 r1 复核）
reviewer_kind: subagent
reviewer_source: DSH Lead 派发；parent session session-8db9dae5-49df-4d09-ac62-696f0805a95c
review_environment: Windows；仓库 G:\CODEX\New Manga（main）；.NET SDK 10.0.401（net9.0 targets）；Python 3.14.6；隔离 worktree 仅用于变异（已删除）
review_date: 2026-11-06
decision: APPROVE
findings: P0=0 / P1=0 / P2=1 / P3=5（详见 §7；无功能阻断）
---

# FEA-12-UI r2 窄面独立复审

> **结论：APPROVE。** r1 的 P1-1（AC7 三态混同）与 P2-1/P2-2a/P2-2b/P2-3 全部按最小返修闭环，且有**独立可判别**的测试与变异证据：我在干净隔离树上复做 M1=2 红、M3=3 红，并额外做了 M4（缺 preview 仍禁 restore）、M5（能力缺失仍显示只读 banner）、M6（probe 失败归为能力缺失）、M7（cleanup 关闭假“仍可重试”），均应红。AC1–AC10 可判 MET；全量 .NET、定向 UI、真实 IPC、pins/API/check 全部独立通过，4 张快照与交付逐字节相同；范围/纪律/未 push/工作树 clean 均满足。
>
> 剩余问题只有 **P2-4（证据 manifest 内 check.log 的 sha/bytes 陈旧）** 与 5 个 P3 文档/证据卫生项；均不影响 AC 或功能，建议 DSH 在 closeout docs commit 中一并修正（不需要重跑功能测试）。L3 真机仍 **NOT_RUN**，不得写 PASS。
>
> 被审对象：`doc/tasks/FEA-12-UI.md`（in_review，AC1–AC10 `<<MET>>`；EV-01…EV-18）、`doc/handoffs/FEA-12-UI-d976aceec.md`（r2 更新）、`verification/FEA-12-UI/**`（16 文件）、r2 返修 `a46d4d5c7`（21 文件）、docs head `233d73f21`（卡+Handoff）。`e9d797f7a` 为 amend 前悬空 docs head，`e9d797f7a..233d73f21` 仅卡面 Review 行 1 行差异，已核对。

## 1. r1 findings 核销

| r1 finding | r1 级别 | r2 处置 | 独立核验 | 判定 |
|---|---|---|---|---|
| P1-1 能力缺失 / Host 只读 / probe 失败三态混同（AC7 NOT MET） | P1 | `_hostReadOnly` 独立（仅 `_writesAllowed()` Host 写闸）；`_capabilityMissing` 仅由 read 决定；restore 仅 write、删除入口/确认 write+preview 分门控；部分缺失 `ShowCapabilityDegraded` + `CORE_CAPABILITY_MISSING` 横幅；`CORE_UNAVAILABLE` 独立 probe 失败态 +「重试探测」；`HOST_READ_ONLY` 字面；新增缺 read/缺 write/缺 preview + probe 失败 4 个测试 | 代码审阅（`TrashViewModel.cs:34-39/158-226/337/402-458/597-618/950-976`、`RecycleBinView.axaml:64-81`）；`TrashUiTests` 40/40；变异 M4=1 红、M5=3 红、M6=1 红（见 §4）；只缺 preview 时 restore 真实发出 1 帧、删除 0 帧 | **fixed / MET** |
| P2-1 cleanup_pending 关闭结果后“仍可重试”不实 | P2 | `CloseResult()` 改为“关闭后本会话内将无法再重试清理（wire 无 pending 清单；重新预览会 BOOK_NOT_FOUND）；如需重试请先点「重试清理」”；`CanRetryCleanup=false`；L3 收窄为“结果面板保留期间可重试” | 代码审阅 `TrashViewModel.cs:834-851`；`CloseResult_AfterCleanupPending_SaysRetryIsLost_AndDisablesRetry` 通过；变异 M7（把文案改回旧“仍可重试”）→ 该测试 1 红 | **fixed** |
| P2-2a fake 集合/逐书 digest 同值，VM 绑定无判别测试 | P2 | fake `DefaultPreview` 集合 `…a`、逐书 `…d`；删除帧断言 `==逐书` 且 `≠集合` | 代码审阅；复做 M1（`_activeDigest = preview.InventoryDigest`）→ **2 红**：`Delete_SendsExactlyOneFrame_WithExactlyTheFrozenPayloadKeys`、`OldCoreProjection_EmptyCurrentArrays_AreKnown_AndAllowExactlyOneDelete`（33 绿）；与 `logs/r2-mutations.log` 的 2 红/名称一致 | **fixed；判别有效** |
| P2-2b 旧 Core current 数组 fail-closed 无判别测试 | P2 | 抽出 `HostController.ProjectPreviewResponse` internal 投影；缺字段/null/非法形状 → unknown → 0 删除帧；`[]` → 已知 → 1 帧；`ProjectTrashWriteResult` 同批可测 | 4 个 VM 驱动测试通过；复做 M3（`TrashStringArrayOrUnknown`→`TrashStringArray`）→ **3 红**（三个 `OldCoreProjection_UnknownCurrentSet_FailsClosed_ZeroDeleteFrames` case，32 绿）；与 mutation log 一致 | **fixed；判别有效** |
| P2-3 卡/Handoff pytest 基线旧数 3073/10 | P2 | 改为 **3203 passed / 10 skipped**（引用；零 Python 改动，未重跑） | `doc/tasks/FEA-12-UI.md:182`、`doc/handoffs/FEA-12-UI-d976aceec.md:76` 均为 3203/10；全仓该两文件无 3073 残留 | **fixed** |
| P3 同批 13 项（见 r1 §6） | P3 | 死方法删除、恢复不确认文案、`固定版本`、`HOST_READ_ONLY`、`{}` typed failure、move payload 覆盖说明、spill 322+tree sha、check.ps1 PASS 入证据、未知 reason 措辞、无选中不默认第一项、LoadMore 防重入、无效赋值、路径泄露断言；另补 AC2 书架移除断言 | 逐项核验见 §5；P2-4/P3-1/P3-2/P3-3 为遗留卫生项 | **fixed（除 §7 卫生项）** |

补充：r1 的 P3-9（AC2 成功后书架不再含该书）在 r2 通过 `FakeHostController.MoveToTrashAsync` 移除 `Snapshot.Books` 并由 `Assert.DoesNotContain(library.AllBooks, …)` 断言，已从“只断言 Selection”升级为真实书架断言；r1 P3-5（`{}` 伪成功）由 `ProjectTrashWriteResult` 的“必须存在 `moved`/`restored` 数组、成功项 >0 才 ok”修复，并有测试。

## 2. 独立复跑（reviewed_head 233d73f21，main）

| 场景 | 命令 | 结果 |
|---|---|---|
| 全量 .NET（首跑） | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release --nologo`；`dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build --nologo` | BUILD EXIT 0（0 warning/0 error）；**1486 passed / 0 failed / 82 skipped**；App.Tests **715/0/7**、Host.Tests **144/0/51**、CoreClient 167/0/24、ThemeEngine 253、DesignSystem 117、Presentation 38、ApplicationCore 31、Appearance 21。**首跑 0 失败，无需 flaky 复跑**。跑后 `verification/FEA-09/logs/wire-redacted.ndjson` 被既有行为重写，已 `git checkout -- verification/FEA-09` 恢复，工作树 clean |
| 定向 UI（curated 到仓外 temp） | `NEWMANGA_EVIDENCE_DIR=<review-ui-r2b>/temp/ui-evidence dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --no-build --nologo --filter "FullyQualifiedName~TrashUiTests|NoDbOsAccessTests|V2ShellUiTests.RecycleBin|V2ShellUiTests.MoveToTrash"` | **40/40 PASS**（`TrashUiTests` 35、`NoDbOsAccessTests` 3、2 个真实窗口交互）；4 张 1600×1000 快照重新生成，**4/4 与交付 `verification/FEA-12-UI/screens/*.png` 逐字节相同**（07 `0de986c4…`、08 `fa41f366…`、09 `ea15b96d…`、10 `802fb895…`） |
| 真实 IPC（真实 `src/bootstrap/core_service.py`） | `NEWMANGA_FEA12_UI_IPC=1` + `NEWMANGA_EVIDENCE_DIR=<review-ui-r2b>/temp/ipc-evidence` + `dotnet test ... --filter FullyQualifiedName~Fea12TrashUiIpcTests` | **1/1 PASS**；**27 wire 帧**；`purge_frames=false`、`batch_permanent_delete_frames=false`；集合 digest ≠ 逐书 digest（本次 `03d206eb…` vs `843372a7…`），删除帧绑定逐书；DataRoot 在仓外（`G:\CODEX\New Manga.workspace\FEA-12-UI\ipc-<guid>`）；sentinel 树指纹前后相等 `cb20e326…` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS 18/18**，EXIT 0 |
| API inventory / C-07 | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **PASS**，EXIT 0；`IHostController` 54 方法不变；`ITrashController` 不在 C-07 解析清单 |
| 契约/计划/Python 零漂移 | `git diff --name-only 9daa94a25..HEAD -- doc/plan doc/contracts src/` | **空**（0 文件） |
| check.ps1 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-12-UI.md` | **PASS（3 warnings）**，EXIT 0；warning 为既有类型（11 非终态 Task / STATUS 80% / PLAN 80%），与 `logs/check.log` 逐行一致 |
| 18 EV sha256 复算 | 对卡 EV-01…EV-18 全部文件重算 | **18/18 与卡表逐字节 MATCH**（含 EV-15/16 两个 SOURCE_PIN；EV-17 check.log=`4adddd01…`、EV-18 manifest=`54ce1006…`） |

## 3. 证据真实性

- `verification/FEA-12-UI/**` 当前 **16 文件**（4 PNG + AC-MATRIX/ENVIRONMENT/IPC JSON/manifest + 8 log）；卡 EV-01…EV-18 全部 MATCH；无未登记文件。
- `logs/dotnet-full-solution.log` 分列与我的独立复跑一致（1486/0/82；App 715、Host 144）；`logs/ui-tests-curated.log` 40/40；`logs/ipc-tests-curated.log` 1/1；`logs/r2-mutations.log` 的 M1/M3 红数与名称经我复做一致；`logs/check.log` 与我的 check.ps1 输出一致。
- 真实 IPC JSON 的 `collectionDigest ≠ perBookDigest`、`wire_frames=27`、`purge/batch=false`、`dataRootOutsideRepo=true`、`sentinelUnchanged=true` 均独立复现（每次运行 digest/bookId 变化属预期）。
- 快照 07/08/09/10 与交付 PNG 逐字节相同（比 r1 更强：r1 的 09 曾因时序字节不同；本次同一构建下 4/4 相同）。
- **P2-4**：`agent-output-manifest.json` 的 `logs/check.log` 条目仍写 `sha256=ad6c20d9…`、`bytes=625`，实际为 `4adddd01…`、`408` 字节（卡 EV-17 正确）；manifest 的 `reviewed_head` 仍为 `c841b9a0b`（r1 head，未更新到 r2）。其余 14 个 manifest 条目全部 MATCH。见 §7。

## 4. 独立变异 / 反证（全部在隔离 worktree 中执行，已删除）

> **并发环境说明（重要）**：审查期间检测到另一复审子 agent 在同一主工作树做变异（workspace `review-ui-r2` 目录；主树曾出现 `HostController.cs` 的 M3 改动，随后被其还原）。我第一次在主树施加 M1 时，改动被并发还原，得到的“35/35 绿”**不是有效结论**。为消除竞态，我改用 `git worktree add --detach 233d73f21` 的隔离干净树执行下列全部变异；主树全程不再改动，评审结束时主树 `git status` clean、该 worktree 已 `git worktree remove --force` 删除。下列结果均来自隔离树（基线 35/35 绿）。

| # | 变异 | 预期 | 实测 | 结论 |
|---|---|---|---|---|
| M1 | `TrashViewModel.cs:663` `_activeDigest = boundDigest` → `preview.InventoryDigest`（逐书→集合） | 应红 | **2 红**：`Delete_SendsExactlyOneFrame_WithExactlyTheFrozenPayloadKeys`、`OldCoreProjection_EmptyCurrentArrays_AreKnown_AndAllowExactlyOneDelete`；33 绿 | 复现交付日志 **2 红**；P2-2a 判别有效 |
| M3 | `HostController.cs:3030-3031` current 两数组 `TrashStringArrayOrUnknown` → `TrashStringArray`（fail-open） | 应红 | **3 红**：`OldCoreProjection_UnknownCurrentSet_FailsClosed_ZeroDeleteFrames` 三个 case（缺字段/null/非法形状）；32 绿；`[]` 用例仍绿 | 复现交付日志 **3 红**；P2-2b 判别有效，且“只有 unknown 阻断、`[]` 可确认”成立 |
| M4 | `CanRestore => HasSelection && CanWrite && CanPreview && !IsBusy`（缺 preview 仍禁 restore，即 r1 旧缺陷） | 应红 | **1 红**：`PreviewCapabilityMissing_RestoreStillAllowed_DeleteBlocked`；34 绿 | AC7⑤ 的“按操作门禁”被测试真实保护 |
| M5 | `ShowHostReadOnlyBanner => _hostReadOnly \|\| HasCapabilityGap`（能力缺失时显示假只读 banner） | 应红 | **3 红**：`ReadCapabilityMissing_ShowsTypedGap_FailsClosed_NoReadOnlyBanner`、`WriteCapabilityMissing_ListsForReal_RestoreAndDeleteDisabled_TypedDegraded`、`PreviewCapabilityMissing_RestoreStillAllowed_DeleteBlocked`；32 绿 | P1 的“无假只读 banner”被测试真实保护 |
| M6 | probe 失败分支 `_capabilityMissing` 由 `false` 改为 `true`（把 CORE_UNAVAILABLE 归为能力缺失） | 应红 | **1 红**：`ProbeFailure_CoreUnavailable_IsIndependentFailureState_NotCapabilityMissing`；34 绿 | P1 的“probe 失败独立态”被测试保护 |
| M7 | `CloseResult` 文案改回“已记录待清理状态：本会话内仍可重试清理” | 应红 | **1 红**：`CloseResult_AfterCleanupPending_SaysRetryIsLost_AndDisablesRetry`；1 个过滤测试执行 | P2-1 的文案一致性有判别力 |

还原核验：每次变异后 `git checkout --` 还原；最终隔离树 `git status` clean、基线重建后 35/35 绿；主树 clean。M1/M3 与 `logs/r2-mutations.log` 的“M1 2 红 / M3 3 红”完全一致，**未夸大**。

## 5. 范围 / 纪律 / 交付事实

- **r2 实现 commit `a46d4d5c7`（21 文件）**：5 个 App 生产（`HostController.cs`、`TrashModels.cs`、`LibraryViewModel.cs`、`TrashViewModel.cs`、`RecycleBinView.axaml`）、2 个 App 测试（`FakeHostController.cs`、`TrashUiTests.cs`）、14 个 `verification/FEA-12-UI/**` 证据；**全部在 allowed_paths**。
- **r2 docs commit `233d73f21`（2 文件）**：`doc/tasks/FEA-12-UI.md`、`doc/handoffs/FEA-12-UI-d976aceec.md`；均在 allowed_paths。`e9d797f7a..233d73f21` 仅卡面 Review 行 1 行差异，与任务说明一致。
- **禁止路径零改动**：`IHostController.cs`、`RunContracts.cs`、`doc/plan/FEA-C07_API_INVENTORY.md`、`doc/plan/FEA-CONTRACT-FROZEN-*`、`NewManga.Host/**`、`NewManga.CoreClient/**`、`NewManga.DesignSystem/**`、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、`doc/reviews/**`、Python `src/**` 在 `9daa94a25..HEAD` 均 0 diff；`doc/plan`/`doc/contracts`/`src/` 的 diff 为空。
- `ITrashController` 独立于 `IHostController`，`HostController`/`NullHostController`/`FakeHostController` 分别实现；App 源码对 `library_purge_trash`/`library_delete_books_permanently` **0 调用**（仅 `TrashWireCommands` 常量与注释）；`Port_HasNoPurgeOrBatchMember_AtAll` 测试通过。
- **未 push**：`origin/main` 不含 `a46d4d5c7`/`233d73f21`（`git branch -r --contains` 为空；本地 main 领先 origin/main 为既有状态）。
- **工作树 clean**：审查开始/结束 `git status --porcelain` 均为空；未 commit、未 push；变异用隔离 worktree 已删除；`verification/FEA-09` 已恢复。
- 资源：真实 IPC 隔离根在仓外 `G:\CODEX\New Manga.workspace\FEA-12-UI\ipc-*`；spill 归档 `G:\CODEX\New Manga.workspace\archive\FEA-12-UI-spill-2026-11-06\` 实测 **322 文件 / 2×161 文件双树**，manifest 标记 `ARCHIVED` 且明确“不属 Canonical Evidence”。

## 6. AC / Limitation 判定

| AC | 判定 | 依据摘要 |
|---|---|---|
| AC1 列表与入口 | **MET** | probe 后恰 1 帧 `library_list_trash`（首帧无 cursor）、LoadMore 原样回传不透明 cursor、无总数、进入隐藏详情/批量条、迟到响应隔离；测试 + 快照 07 |
| AC2 软删入口 | **MET** | 默认焦点取消 / Esc / Enter 零写入、确认后恰 1 帧、payload `{entries,idempotency_key}`、成功后才刷新/清选中、UndoBar、skipped 白名单、书架移除断言；测试 + 快照 09/10 |
| AC3 恢复 | **MET** | 勾选顺序单帧、restored 移除/conflicts 保留逐项 reason、白名单+“恢复冲突（未分类）”兜底、不整批伪成功 |
| AC4 预览披露 | **MET** | 确认前仅 1 帧 preview、PD-01 三项 + 完整 current 计数 + artifact 表达 + pinned/active + 保留项声明、文本无路径/源文件名、旧 Core 缺字段/null/非法形状 fail-closed、`[]` 已知；测试 + 快照 08 |
| AC5 专门确认与 digest 绑定 | **MET** | 未勾选 0 删除帧；勾选后 1 帧；payload 恰 3 键；digest=逐书且真实 IPC 集合≠逐书；STALE 自动重预览不重发删除；activeRunIds 预阻断 |
| AC6 stale / busy / 结果处置 | **MET** | STALE/BUSY/CLEANUP_PENDING 同 digest 重试且无新 preview/NOT_FOUND 刷新/CONFLICT/FAILED typed/INVALID_REQUEST 不静默；关闭 cleanup 结果文案与 `CanRetryCleanup=false` 一致 |
| AC7 能力缺失 / 只读 / 不可用 | **MET** | 三态独立、按操作门控、部分缺失 typed 降级横幅、无假只读 banner、`CORE_UNAVAILABLE` 独立失败态+重试、`HOST_READ_ONLY` 字面；M4/M5/M6 判别通过 |
| AC8 无 DB/OS 直连 + 隔离 | **MET** | 本卡 9 文件 0 DB/OS 直连；真实 IPC DataRoot 仓外 + sentinel 前后指纹相等 |
| AC9 文案诚实性 | **MET** | 回收站“能力待接入”类过期文案清零；能力缺失用 typed code；Fluent 抽屉/tooltip 改为“Fluent 前端暂未接入回收站数据/请用 V2”，不称能力缺失、不含实现类名；页面级删除“页面级删除无命令”；无总数/逐项 busy |
| AC10 禁令与门禁 | **MET** | 真实 wire + fake 0 帧 purge/0 帧批量；删除 payload 无批量字段；全量 1486/0/82（不减少）；pins 18/18；API check PASS；check.ps1 PASS；L3 NOT_RUN |

**Limitation**：L1–L10 在卡内逐项保留且与实现一致；**L3 真机走查在卡/Handoff/AC-MATRIX 均为 `NOT_RUN`，未写 PASS**；L3 已按 r2 收窄为“结果面板保留期间可重试；关闭后 UI 明示不可重试”；pytest 未重跑（零 Python 改动，引用 3203/10 正确）；CORE 侧事实（restore reason 收窄、active export 未披露）按 L5/L6 记录，未在本卡修。

## 7. Findings（P2/P3；无 P0/P1）

### P2-4 证据 manifest 的 `check.log` 哈希/字节陈旧，`reviewed_head` 未更新

- **位置**：`verification/FEA-12-UI/agent-output-manifest.json:38-40`（check.log 条目）与 `:6`（`reviewed_head`）。
- **事实**：manifest 写 `sha256=ad6c20d905abdf01039e9da76d0d7744cfa78eac04729763b04182043763cbb0`、`bytes=625`；实际文件为 `sha256=4adddd01338271e8a3cc91f78ac2c546daaa30a7911372207ba2e53a7a18c686`、`bytes=408`。卡 Canonical Evidence **EV-17 的哈希是正确的**，因此不是 EV 表错误，而是 EV-18/manifest 内部索引未随 r2 重签同步；manifest 的 `reviewed_head` 仍为 `c841b9a0b`（r1 head），与 `round: r2` 不一致。
- **影响**：不影响任何 AC 或功能；但“证据已按 r2 重签”在 manifest 层不完整，canonical evidence index 指向不存在的哈希，closeout 若直接采信 manifest 会核验失败。
- **最小返修**：更新 manifest 的 check.log `sha256`/`bytes` 与 `reviewed_head`（建议 `233d73f21` 或注明 reviewed implementation head `a46d4d5c7`）；重新计算 manifest 的 EV-18 sha 并更新卡 EV-18 行；docs-only commit（allowed_paths），无需重跑功能测试。建议 DSH 在填 `integration_commit` 前完成。

### P3-1 卡/Handoff 的旧 1474 表与 r2 1486 并存

- `doc/tasks/FEA-12-UI.md:173`（测试要求表的“实际结果”）仍写“全量 **1474/0/82**”，而同文件 `:182`/`:204` 写 **1486/0/82**；`doc/handoffs/FEA-12-UI-d976aceec.md:51` 也仍写 1474，`:99` 写 1486。1474 是 r1 的实测（历史真实），但在 r2 卡/Handoff 的“当前实际结果”表里未更新/未标注 r1，读者会误以为 r2 门禁数字矛盾。**最小返修**：把两处表更新为 1486 或标注“r1 实测 1474；r2 实测 1486”。

### P3-2 `logs/r2-mutations.log` / `logs/gates.log` 的“48/48”口径未解释

- `logs/r2-mutations.log:41` 与 `logs/gates.log` G14 写“定向复跑 48/48 绿”，而卡/`logs/ui-tests-curated.log` 的 curated 口径是 **40/40**（35+3+2）。M1/M3 红数（2/3）与我的复做完全一致，故不影响结论；但 48 与 40 的差异没有说明。**最小返修**：说明 48 的 filter/包含项，或统一改为 40/40。

### P3-3 spill 归档 tree sha256 无法按文档公式独立复现

- 归档实测 **322 文件**（`spill-tree` 与 `moved-tree` 各 161，且两树内容相同），与卡/manifest 的 322 一致；但 manifest 所述“按（相对路径|文件 sha256）排序拼接后整体 SHA-256”的 `80dcf749…` 我用多种分隔符/路径/排序/整树组合均未复现（得到 per-tree `ebeb5ac8…`、整树 `5e9cffb9…`/`19607e79…` 等）。该归档明确 **非 Canonical**，不影响 AC，但 tree sha 的 provenance 目前不可独立核验。**最小返修**：在归档内落一个生成脚本/清单文件，或把确切拼接格式写进 manifest note。

### P3-4 卡/Handoff 的 reviewer 字段仍为“待派发”

- `doc/tasks/FEA-12-UI.md:10` `reviewer: 独立上下文 fresh subagent（待 DSH 派发…）`；`doc/handoffs/FEA-12-UI-d976aceec.md:6` `reviewer: null`。r1 与 r2 复审实际均已派发（本报告为 r2b）。建议在 closeout 时登记 r1/r2 reviewer 身份与 session/source，或明确保留“待 DSH 汇总”；不影响实现。

### P3-5 部分能力缺失 / Host 只读时删除入口按钮未视觉禁用

- `RecycleBinView.axaml:121-124` 的“彻底删除选中（单本）”只绑定 `Trash.HasSelection`；在只缺 write/preview 或 Host 只读时按钮仍可点，点击后由 `BeginPermanentDeleteAsync` typed 阻断并 0 帧（测试已覆盖）。AC7⑤ 的功能门禁成立，但与“按操作禁用”的视觉语义不完全一致。**最小返修（可选）**：增加 `CanDeleteSelected => HasSelection && CanWrite && CanPreview` 并绑定 `IsEnabled`，命令仍保留二次门禁。

### 其他 P3 观察（不单列严重度）

- `verification/FEA-12-UI/AC-MATRIX.md:25` 仍写“暂未分类/未分类兜底”，实现已统一为“恢复冲突（未分类）”；建议同步措辞。
- `RecycleBinView.axaml:67` 只读 banner 文本称“软删/恢复/彻底删除”，本页无软删入口；如需严格，可改为“恢复/彻底删除”。
- `ShowHostReadOnlyBanner` 在“Host 只读 + 能力缺失”同时成立时隐藏只读 banner（显示能力缺失）；这是为消除假 banner 的权衡，非当前 AC 反例，但 `HOST_READ_ONLY` 字面在该组合态不可见，建议在 degraded 文案中补一句 Host 写闸原因（可选）。

## 8. Closeout 建议

- **delivery_head = `a46d4d5c7`**（r2 实现+测试+证据）；**reviewed_head = `233d73f21`**（r2 docs head；`e9d797f7a` 已悬空、不采用）。
- **integration_commit**：**待 Lead（DSH）集成时填写**；`canonical_evidence_status` / `resource_closeout_status` 保持 pending；本 Review 不代填。
- **L3 真机：NOT_RUN**（冻结 OUT/L10；不得写 PASS/L4 已通过）。
- 建议 DSH 在 closeout docs commit 中：①修 P2-4（manifest check.log hash/bytes + reviewed_head，重签 EV-18）；②按需修 P3-1/P3-2/P3-3/P3-4；③保持 L1–L10 与 L3 NOT_RUN 原文。P3-5 为可选 UX 改进，若要改 UI 需重新跑定向 UI 40/40 与快照哈希。
- 若 Lead 接受“manifest 为辅助索引、卡 EV 表为准”的解释，P2-4 也可降为 P3 并在 closeout 修正；但**不建议在 manifest 仍指向旧 hash 的状态下把 canonical_evidence_status 置为 complete**。
- 本轮审查未发现功能/AC/契约/范围问题，未见需要重跑的失败；未 push、未 commit、主树 clean。

## 9. 审查者独立性与方法

本 Review 由 DSH Lead 派发的独立上下文 fresh subagent 执行，未参与 FEA-12-UI 的实现、r2 返修或证据制作；只读被审 head `233d73f21`/实现 `a46d4d5c7`，变异仅在隔离 worktree 的同一 commit 树上临时进行并已删除。审查依据：卡 AC1–AC10、Handoff、`verification/FEA-12-UI/**`、`doc/reviews/FEA-12-UI-r1.md`、C-04b v1.1、M2-C1 rev 2.14 §5.11/§5.13/§5.14、C-09 SC-B06、ADJ-001 PD-01/02/04、SCOPE-ADJ-2026-11-05 B 节、C-07。审查日志/变异日志/复算截图写在仓外 `G:\CODEX\New Manga.workspace\FEA-12\review-ui-r2b\temp\`，未写入 repo、未提交。

UI-R2-REVIEW: APPROVE — r1 P1/P2 全部核销（AC7 三态独立、cleanup 关闭语义、digest/旧 Core 判别测试、3203/10 基线）；全量 1486/0/82、定向 UI 40/40（4 快照逐字节同交付）、真实 IPC 1/1（27 帧/0 purge/0 批量/逐书 digest）、pins 18/18、API/check.ps1 PASS、18 EV sha MATCH、范围/未 push/clean 均通过；独立变异 M1=2 红、M3=3 红，另 M4/M5/M6/M7 判别有效。仅余 P2-4（manifest check.log hash/bytes 与 reviewed_head 陈旧，docs-only 修正）+ P3×5 文档/证据卫生项；L3 真机 NOT_RUN。delivery_head=a46d4d5c7；integration_commit 待 Lead。
