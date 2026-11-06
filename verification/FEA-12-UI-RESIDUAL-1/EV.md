# FEA-12-UI-RESIDUAL-1 Canonical Evidence（App-only 四项 P3 残余收口）

> **结论先行：本卡只做 App 侧（`TrashViewModel.cs` + `TrashUiTests.cs`）四项 P3 残余收口。**
>
> - **I-1 仅钉防御不变量（defensive invariant only）**：删除结果 `CORE_CAPABILITY_MISSING` 不再把页级 READ 能力态置为缺失；该分支**生产不可达**（Host 当前不对 `library_delete_book_permanently` 做能力门、Core 不返回该码，L-R1），**不得**表述为“修复用户可见缺陷”。
> - I-2 preview `BOOK_NOT_FOUND` → `_notify` + 关面板 + `await ReloadAsync()`（只刷新一次、零 delete 帧、零自动重试）；I-3 cleanup retry `BOOK_NOT_FOUND` 的最小 `_notify` 修复（旧实现文案被 `ResetPreview` 清空、用户不可见）+ 列表刷新 + 状态复位，digest 沿用首次逐字节相同值；I-4 只读与能力缺口是两个独立原因，组合态同时展示，只读文案不再声称“可浏览”。
> - **零契约/wire/schema/迁移/依赖变更**；`IHostController`/`ITrashController`/`TrashModels`/`FakeHostController`/XAML 零 diff；FEA-12-UI 历史 AC **未回填**；L3/L4 真机走查 **NOT_RUN**（不得声称通过）。

| 项 | 值 |
|---|---|
| task | `FEA-12-UI-RESIDUAL-1`（冻结卡 `doc/tasks/FEA-12-UI-RESIDUAL-1.md`；scope review `doc/reviews/FEA-12-UI-RESIDUAL-1-scope-r1.md`（READY-TO-FREEZE）） |
| Owner | `ui-residual-impl`（DSH Agent Teams teammate；Lead=`lead`） |
| base | `9c6ba2da1`（main，clean；与冻结卡 `base_commit 690c77eb0` 之间仅 docs 差异） |
| 实现 + 测试 commit | **`8e3bd03d6`**（`TrashViewModel.cs` +32/−8；`TrashUiTests.cs` +183/−0；2 files changed, 215 insertions, 8 deletions） |
| 证据/卡/Handoff | 本目录所在证据提交（提交 sha 见 `git log -- verification/FEA-12-UI-RESIDUAL-1`；`delivery_head=8e3bd03d6`） |
| 分支/工作树 | `main` / `G:\CODEX\New Manga`（未创建 linked worktree） |
| 环境 | Windows 11 10.0.26300；.NET SDK 10.0.401（net9.0 测试目标）；CPython 3.14.6；PowerShell 7 |
| 契约字节 | **零变更**（`doc/plan`、`doc/contracts`、`src/**`、`tests/**`、`NewManga.Host/**`、`NewManga.CoreClient/**`、`NewManga.DesignSystem/**`、`RecycleBinView.axaml` 全空 diff；pins 18/18） |
| 依赖 | **零新增**（无 `.csproj`/`props`/`targets`/`pyproject`/lock 文件 diff） |

## 1. 门禁实测（before → after）

| Gate | Before（基线树） | After（本卡） | 结果 | 证据 |
|---|---|---|---|---|
| 定向 `TrashUiTests` | **35 passed / 0 failed / 0 skipped**（82 ms） | **40 passed / 0 failed / 0 skipped**（35 + 新增 5；76 ms） | PASS | EV-1 / EV-2 |
| 全量 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **1527 passed / 0 failed / 86 skipped**（8 项目 21+38+253+117+31+185+167+715） | **1532 passed / 0 failed / 86 skipped**（8 项目 21+38+253+117+31+185+167+720；+5 = 新增用例，skip 不变） | PASS | EV-3 / EV-4 |
| 全量 `pytest tests -q` | 3249 passed / 10 skipped | **3249 passed / 10 skipped / 0 failed**（278.59 s，EXIT=0；`git diff -- src tests` 零 diff） | PASS（不降） | EV-5 |
| `verify_pins.ps1` | 18/18 | **PIN AUDIT: PASS (all 18)** | PASS | EV-6 |
| `check.ps1` | PASS(3 warnings) | **Governance check: PASS (3 warnings)**（9 非终态 Task / STATUS 80% / PLAN 80%，均为既有） | PASS | EV-6 |
| `generate_api_inventory.py --check` | PASS | **OK: rendered counts match FEA-C07 doc**（`IHostController`=54 / `IRunController`=6 / `IReaderProgressSink`=1，EXIT=0） | PASS | EV-6 |
| scope diff ⊆ allowed_paths | — | 实现提交仅 2 个允许的 App 文件；禁止面零 diff；依赖/API 文件零 diff | PASS | EV-7 |
| 判别性（变异） | — | **9/9 破坏点全部变红**（EXIT=1，断言失败；恢复字节一致） | PASS | EV-8 |
| L3/L4 真机走查 | NOT_RUN | **NOT_RUN**（本卡不新增真机证据） | NOT_RUN | 本文件 |

**skip 原因（before/after 相同，共 86）**：`Host.Tests` 55 + `CoreClient.Tests` 24 —— 既有真实 IPC / frozen sidecar / 环境门控集成测试（`[Fact(Skip=…)]` 或既有 skip-if 条件，base `9c6ba2da1` 已存在）；`App.Tests` 7 —— 既有 UI host-integration 环境门控（StartupSelfCheck / WritePolicy / CreateChapter / RunController）。本卡未新增或改变任何 skip 条件。

**已知副作用（既有，已恢复）**：全量 .NET 会重写 tracked 文件 `verification/FEA-09/logs/wire-redacted.ndjson`（`WireLogSourceRedactionTests` 的既有副作用，FEA-11-RENDITION-1 已记录）。每次全量后执行 `git checkout -- verification/FEA-09`（EXIT=0），最终 worktree 仅本卡改动。

## 2. 判别性验证（删掉实现必须变红）

`logs/scope-mutations.log`：对 `TrashViewModel.cs` 做 9 个破坏性文本替换，逐个运行目标用例；**9/9 全部 RED（EXIT=1，均为断言失败，无编译错误）**，随后从 pristine 备份逐字节恢复（SHA-256 相等，记录在日志末尾）。运行器：`G:\CODEX\New Manga.workspace\FEA-12-UI-RESIDUAL-1\temp\run-mutations.ps1`（仓外）。

| Case | AC | 破坏点 | 目标用例 | 实测 |
|---|---|---|---|---|
| M1 | AC-R1 / I-1 | 恢复 `_capabilityMissing=true` + `_capabilityMessage` 页级污染 | `Delete_CapabilityMissing_DoesNotTurnThePageIntoReadCapabilityMissing` | **1 failed**（`Assert.True(ShowList)`） |
| M2 | AC-R2 / I-2 | 删除 preview `BOOK_NOT_FOUND` 的 `await ReloadAsync()` | `Preview_BookNotFound_ClosesPanel_AndReloadsTheList` | **1 failed**（List 帧/Items 断言） |
| M3 | AC-R2 / I-2 | 删除 preview `BOOK_NOT_FOUND` 的 `_notify` | 同上 | **1 failed**（notice `Assert.Contains`） |
| M4 | AC-R2 / I-2 | 整块删除 notion 分支（落入通用错误分支） | 同上 | **1 failed**（面板未关/无刷新） |
| M5 | AC-R3 / I-3 | 删除 cleanup retry `BOOK_NOT_FOUND` 的 `_notify`（复现旧“不可见文案”） | `CleanupRetry_SecondRetryBookNotFound_NotifiesAndRefreshes_WithSameDigest` | **1 failed**（notice `Assert.Contains`） |
| M6 | AC-R3 / I-3 | 重试帧改用变化后的 digest（`_activeDigest + "0"`） | 同上 | **1 failed**（digest `Assert.Equal`） |
| M7 | AC-R3 / I-3 | 删除 cleanup retry `BOOK_NOT_FOUND` 的 `await ReloadAsync()` | 同上 | **1 failed**（List 帧 1≠2） |
| M8 | AC-R4 / I-4a | 恢复 `ShowHostReadOnlyBanner => _hostReadOnly && !HasCapabilityGap` 抑制 | `HostReadOnly_PlusWriteCapabilityGap_ShowsBothIndependentCauses` | **1 failed**（`Assert.True(ShowHostReadOnlyBanner)`） |
| M9 | AC-R4 / I-4b | 恢复只读文案“回收站可浏览” | `HostReadOnly_PlusReadCapabilityMissing_ShowsCapabilityStateAndReadOnlyReason` | **1 failed**（`Assert.DoesNotContain("可浏览")`） |

**过程说明（如实记录）**：变异循环用 `Copy-Item` 恢复 pristine 文件时会保留其 mtime，MSBuild 增量构建因此一度把 M9 变异产物当成最新，导致第一次 AFTER 全量出现 1 个伪红（M9 目标用例读到旧 App.dll）。已刷新源文件时间戳后重跑定向（40/0）与全量（1532/0/86）门禁，本目录采用**重跑后的干净日志**为 canonical；该伪红不涉及任何源码缺陷。

## 3. Evidence 索引（sha256）

所有证据文件对应代码状态 = 实现+测试 commit `8e3bd03d6`（base `9c6ba2da1`）；日志/卡/Handoff 由紧随其后的证据提交收录。

| evidence_id | AC/Gate | path | sha256 |
|---|---|---|---|
| EV-1 | AC-R1…AC-R4 定向基线（35/0） | `verification/FEA-12-UI-RESIDUAL-1/logs/gates-targeted-before.log` | `ea544fedda4828a02a5652b33ac7ce69ce741c0282eaf86c2ff1b1ab6672d31e` |
| EV-2 | AC-R1…AC-R5 定向 after（40/0，新增 5） | `verification/FEA-12-UI-RESIDUAL-1/logs/gates-targeted-after.log` | `3128e92f44ffea5f4dd1b7d074d95d37d2e22195369a4755739fea95165626f0` |
| EV-3 | AC-R5 全量 .NET before（1527/0/86） | `verification/FEA-12-UI-RESIDUAL-1/logs/gates-dotnet-before.log` | `baab20fdfc22b9c9ffc479496e5e487dcb9ae624bd36b12de7363f31fe040a88` |
| EV-4 | AC-R5 全量 .NET after（1532/0/86） | `verification/FEA-12-UI-RESIDUAL-1/logs/gates-dotnet-after.log` | `3fbf0840f9d4d5f07d053a132a846e9b701938298abb8d8d92f112b1f5180c20` |
| EV-5 | AC-R5 全量 pytest（3249/10，零 Python diff） | `verification/FEA-12-UI-RESIDUAL-1/logs/gates-pytest.log` | `69beb5ca4c805327d2fc47e3290a88eaf700a824b384bb0e1b114af19753704d` |
| EV-6 | AC-R5 pins 18/18 + check PASS(3 warnings) + API inventory PASS | `verification/FEA-12-UI-RESIDUAL-1/logs/gates-governance.log` | `2b83261984c08eaf48a8380c122217143fb379d0c0701d6e1db28e4fbb512d76` |
| EV-7 | AC-R5 scope diff ⊆ allowed_paths；禁止面/依赖/API 零 diff | `verification/FEA-12-UI-RESIDUAL-1/logs/scope-validation.log` | `a21eede24ea5f701b3ed56f9fe37eb3b941f6973bb2dcc5c3c3a4566319b2894` |
| EV-8 | AC-R1…AC-R4 判别性（9/9 变红，逐字节恢复） | `verification/FEA-12-UI-RESIDUAL-1/logs/scope-mutations.log` | `f95d41527212d65005c12a2df3f7c0129ad24455dc4ecee5e1529f11762892de` |
| EV-9 | AC-R5 门禁汇总（before/after、skip 原因、L3 NOT_RUN） | `verification/FEA-12-UI-RESIDUAL-1/logs/gates.log` | `d0ad14579d3904b363adbbbd74fc3e416ac488b8bdb519faed142e6b1c79f353` |
| EV-10 | AC-R5 Resource Manifest（仓外隔离根 10 文件聚合 + 资源处置） | `verification/FEA-12-UI-RESIDUAL-1/RESOURCE-MANIFEST.json` | `1c78ec610f5bec011a7850d3bd0697e43f9d482360b72c3dcc9e90247dc80ed7` |
| EV-11 | AC-R5 变更清单（base..证据 head，逐文件） | `verification/FEA-12-UI-RESIDUAL-1/changed-files.txt` | `1e0ba244e5bec73c900b45c221a7c3aeeb4da1d74b1879024835d473096f4b50` |

> **EV-12 自引用说明（Review F3）**：`EV-12` = 本文件（Evidence 索引）。文件无法在自身字节内嵌自身 sha256；其 sha256 由卡面 `Canonical Evidence` 表登记（pin 到包含本文件的证据提交）。本索引表因此只列 EV-1…EV-11，EV-12 以卡面为准（不改变任何 evidence 字节口径）。

## 4. AC → 实现 → 测试 → 证据

| AC | 判定 | 实现（`TrashViewModel.cs`，commit `8e3bd03d6`） | 判别性测试（`TrashUiTests.cs`） | 证据 |
|---|---|---|---|---|
| **AC-R1** delete-time capability 防御边 | **MET** | `ConfirmDeleteAsync` 的 `TrashDeleteOutcome.CapabilityMissing` 分支：不再写 `_capabilityMissing`/`_capabilityMessage`；保留列表与 probe 布尔；`_deleteOutcomeCode` typed `CORE_CAPABILITY_MISSING`（缺省兜底）；`DeleteResultTitle="删除被拒绝"`；`_previewBlockedReason` 使 `CanConfirmDelete=false`；零成功提示、零额外帧 | `Delete_CapabilityMissing_DoesNotTurnThePageIntoReadCapabilityMissing` | EV-2 / EV-8（M1） |
| **AC-R2** preview `BOOK_NOT_FOUND` 自动刷新 | **MET** | `BeginPermanentDeleteAsync` preview 失败块前置 `BOOK_NOT_FOUND` 分支：`_notify("作品已不存在（BOOK_NOT_FOUND）：已刷新回收站列表", Failed)` + `ResetPreview()`（关面板）+ `await ReloadAsync()`（恰一次）；其它失败码走原通用分支不变 | `Preview_BookNotFound_ClosesPanel_AndReloadsTheList`（2 list 帧、0 delete 帧、probe 2、幽灵行清除） | EV-2 / EV-8（M2/M3/M4） |
| **AC-R3** cleanup retry `BOOK_NOT_FOUND` | **MET** | `RetryCleanupAsync` 的 NotFound 分支在 `ResetPreview()` 前补 `_notify`（typed 提示经 notify 可见，不再被清空）；随后 `ResetPreview()` + `await ReloadAsync()` + `_cleanupPendingVisible=false`；digest 仍为首次 `_activeDigest` | `CleanupRetry_SecondRetryBookNotFound_NotifiesAndRefreshes_WithSameDigest`（3 delete 帧 + 3 次逐字节相同 digest + 1 preview 帧 + 2 list 帧 + 状态复位） | EV-2 / EV-8（M5/M6/M7） |
| **AC-R4** 只读/能力缺口双原因文案 | **MET** | `ShowHostReadOnlyBanner => _hostReadOnly`（去掉 `&& !HasCapabilityGap`）；`HostReadOnlyBannerText` 删除“回收站可浏览”分句，改为“不会执行任何写入；软删/恢复/彻底删除已禁用”；未改 XAML | `HostReadOnly_PlusWriteCapabilityGap_ShowsBothIndependentCauses`、`HostReadOnly_PlusReadCapabilityMissing_ShowsCapabilityStateAndReadOnlyReason`；既有单状态用例全绿 | EV-2 / EV-8（M8/M9） |
| **AC-R5** 写域/门禁/证据 | **MET** | 仅 2 个允许的 App 文件；零契约/wire/schema/依赖；pins 18/18；API inventory PASS；check PASS(3 warnings)；全量 .NET 1532/0/86、pytest 3249/10；变异 9/9 红；L3/L4 NOT_RUN | §1/§2/§3 | EV-1…EV-11 |

## 5. 保留 limitation（预登记，closeout 必须如实保留）

- **L-R1（I-1 生产不可达）**：本卡只钉“删除返回能力缺失不得污染页级 read 能力态”的防御不变量；Host 当前不对 `library_delete_book_permanently` 做能力门、Core 不返回 `CORE_CAPABILITY_MISSING`，故该分支**生产不可达**；不得写成“已修复用户可见 bug”。
- **L-R2（R-002 旧债）**：`CORE_CAPABILITY_MISSING` 不在 `AllowedDeleteTrashErrorCodes`，Host 投影会把 category 降为 `unknown`（code 保留）；属 Host/Core，本卡不改。
- **L-R3（I-2 刷新失败；Review F1 补充）**：`BOOK_NOT_FOUND` 后 `ReloadAsync` 自身失败只显示列表错误态，不自动重试（有意，不引入循环）；「已刷新回收站列表」通知在 `await ReloadAsync()` **之前**发出（文案由 scope review 冻结，且既有 delete-NotFound 分支同模式），刷新失败时通知与列表错误态可能并存——已知 P3 文案时序限制，不改代码。
- **L-R4（I-3 面板关闭）**：cleanup retry NotFound 后关闭结果面板，typed 提示仅通过 `_notify` 传递；若产品要求保留面板需另冻结文案规则。
- **L-R5（I-4 视觉冗余）**：组合态两条 banner 同时出现，接受冗余以不丢原因；合并文案需重新冻结。
- **L-R6（证据层级）**：四项均为 VM 级 fake 测试，不新增真实 Host/Core IPC；cleanup retry NotFound 无 L2 IPC 证据。
- **L-R7（I-4 read 可用时信息量略减）**：只读文案移除「可浏览」；动态文案追加需另加测试。
- **L3/L4**：真机走查 `NOT_RUN`；本卡不新增真机证据，不得声称通过。
- **FEA-12-UI 历史 AC 未回填**：不修改 `doc/tasks/FEA-12-UI.md` 任何字节；本卡只登记 residual 边映射（AC4 的 BOOK_NOT_FOUND 刷新边、AC6③ 的第二次 retry NotFound、AC7②/⑤ 的双原因与按操作禁用）。

## 6. 资源处置

- 仓外隔离根 `G:\CODEX\New Manga.workspace\FEA-12-UI-RESIDUAL-1\`（agent 脚本 + 原始门禁日志 + pristine 备份）**PRESERVE_REFERENCED**，聚合 sha256 `97fdbd1e5bb0fc8d15eb44f42cd88580e76eb43b25b0fa086222abb792d28428`（10 文件，逐文件 sha 见 `RESOURCE-MANIFEST.json`）。
- 未触碰真实用户数据 / AppData / 外部卷 / 真实回收站 / 原文件；未创建 linked worktree；无删除/移动/迁移/归档（`closeout_counts` 全 0）。
- 全量 .NET 的 FEA-09 tracked 字节副作用已恢复（`git checkout -- verification/FEA-09`）。

## 7. Review r1 处置（DSH，2026-11-06）

- 独立 Review：`doc/reviews/FEA-12-UI-RESIDUAL-1-r1.md`（fresh subagent，未参与实现/返修）→ **approved（P0=0/P1=0/P2=0/P3=4）**；无代码返修。
- **F1（P3，通知先于刷新）**：维持 scope review 冻结文案；已在 L-R3 补记「通知在 `await ReloadAsync()` 之前发出；刷新失败时通知与列表错误态可并存」，不宣称强一致。
- **F2（P3，其它 preview 失败码无回归测试）**：AC-R2 的「其它失败码行为不变」只在结构上成立（仅精确 `BOOK_NOT_FOUND` 分支前置，通用分支 diff 未改），**未单独回归测试**；卡面 AC-R2 与本节按此如实限定，登记 follow-up（不阻塞）。
- **F3（P3，EV.md 自索引缺 EV-12）**：本文件 §3 增补「EV-12 自引用说明」；EV-12 的 sha256 由卡面 Canonical Evidence 登记（自引用文件无法内嵌自身哈希）。
- **F4（P3，`ITrashController is null` + 只读组合未测）**：防御路径；生产两实现均非空（`LibraryViewModel.cs:66-70`），登记 follow-up（不阻塞）。
- Review 独立复跑：定向 `TrashUiTests` 40/0/0；全量 .NET 1532/0/86；`pytest tests` 3249/10（隔离复跑 EXIT=0；如实记录一次与 .NET 并行时的中断/单 F，不归因本卡）；pins 18/18；check PASS(3 warnings)；API inventory PASS；另做 3 处独立破坏（3/3 变红，恢复后 blob 一致）。
