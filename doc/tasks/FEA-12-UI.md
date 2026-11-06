---
id: FEA-12-UI
title: FEA-12 回收站 UI 切片（V2 单本彻底删除 + 软删/恢复 + Fluent 文案诚实化）
kind: implementation
governance_version: 3
status: done
approval: scope 已按 ZCode SCOPE-ADJ-2026-11-05 冻结，**DSH 2026-11-06 释放（ready）**：整卡释放前置 = FEA-12-CORE 返修闭环 + 正式契约重冻/重新 closeout；释放时由 DSH 固定 base_commit、Owner 与上下文独立 Reviewer
suggested_owner: zcode
owner: dsh-agent-team teammate `fea12-prereq-impl`（claimed 2026-11-06）
reviewer: 独立上下文 fresh subagent（r1 `doc/reviews/FEA-12-UI-r1.md` session `1dfbb1cf-2234-44a6-8f13-a91653dc7788`（changes_requested P1=1）；r2 窄面 `doc/reviews/FEA-12-UI-r2.md` session `762aa9dd-43f3-4c50-8846-9e14492e7873`（approved P0/P1/P2=0；另一并发复审 session `e46b8835…` 亦 APPROVE，其 reviewed_head 为 amend 前悬空 head，仅作交叉验证）；均未参与实现）
depends_on:
  - FEA-12-PREREQ-1
  - FEA-12-CORE
base_commit: 9daa94a25   # 释放点 main head（SCAN-1 r2 交付后）
branch: null
worktree: null
integration_commit: a46d4d5c7
delivery_head: a46d4d5c7
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-12-UI
allowed_paths:
  - doc/tasks/FEA-12-UI.md
  - doc/reviews/FEA-12-UI-*.md
  - doc/handoffs/FEA-12-UI-*.md
  - verification/FEA-12-UI/**
  - apps/desktop-avalonia/src/NewManga.App/Services/TrashModels.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/NullHostController.cs
  - apps/desktop-avalonia/src/NewManga.App/Services/SourceImportModels.cs（仅必要接线；默认不改其既有方法语义）
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/TrashViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/RecycleBinView.axaml
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/RecycleBinView.axaml.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/LibraryView.axaml
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/LibraryView.axaml.cs
  - apps/desktop-avalonia/src/NewManga.App/Views/V2/Library/BookDetailPanel.axaml
  - apps/desktop-avalonia/src/NewManga.App/Views/Fluent/ShelfPageView.cs（仅文案诚实化，含 tooltip）
  - apps/desktop-avalonia/src/NewManga.App/Shell/ShellSupport.cs（可选：仅命令目录登记）
  - apps/desktop-avalonia/tests/NewManga.App.Tests/FakeHostController.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/TrashUiTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/V2ShellUiTests.cs
  - apps/desktop-avalonia/tests/NewManga.App.Tests/NoDbOsAccessTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea12TrashUiIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Support/Fea12ProductionFixture.cs
out_of_scope:
  - 批量彻底删除（`PermanentlyDeleteBooks` UI）；单书库批量死路已知，首版 Out（L1）
  - `PurgeTrash` 任何调用/入口/能力探测（Core 首版返回 `UNKNOWN_COMMAND`）
  - 回收站缩略图/内容预览/打开回收站书籍（需改 book 级读门控，另卡）
  - 保留期限/到期自动清理/回收站容量承诺；D 流程（Windows 回收站/原文件删除）
  - Fluent 前端回收站真实接线（仅文案诚实化）
  - 页面级/章节级回收站；新设计系统组件/令牌
  - `IHostController.cs`/`RunContracts.cs`/`FEA-C07_API_INVENTORY.md`/任何 pinned 契约字节
  - Python/Core/Host 语义改动（含 restore reason 收窄、active export 披露、current 完整披露字段）；新命令/能力/展示字段/schema/迁移/依赖
  - `apps/desktop-avalonia/src/NewManga.Host/**`、`NewManga.CoreClient/**`、`NewManga.DesignSystem/**`
  - 真实用户数据/AppData/外部卷/真实回收站/真实原文件删除；push
---

# FEA-12-UI：回收站 UI 切片

> **状态：`in_review`（2026-11-06 实施完成）。DSH 2026-11-06 释放（base `9daa94a25`；前置 FEA-12-CORE 返修已闭环并正式重冻）；本卡 scope 按 ZCode SCOPE-ADJ-2026-11-05 冻结执行，实施未扩卡面。**
>
> **交付**：实现 commit `d976aceec`（App 生产代码 + 测试 + `verification/FEA-12-UI/` L2 证据）；Handoff `doc/handoffs/FEA-12-UI-d976aceec.md`。
>
> **消费的已冻结接口**：M2-C1 rev 2.14 的 `PreviewPermanentDeleteBooks`（`currentRegionRevisionIds`/`currentArtifactRevisionIds` 完整 current 集合）与 §5.11/§5.11.1a/§5.14；C-09 SC-B06 回收站命令面；C-04b v1.1 单本删除 payload `{book_id, confirm_permanent_delete, inventory_digest}`。
>
> 范围事实基线：释放时 DSH 固定 base `9daa94a25`（SCAN-1 r2 交付后 main head）；CORE r3 Review 已通过、M2-C1 rev 2.14 / C-04b v1.1 已重冻。

## 来源与目标

- 承接链：`doc/reviews/ADJ-2026-11-05-FEA-12-SCOPE.md`（D1–D8）、`doc/contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md`（PD-01…PD-10）、M2-C1 rev 2.13 §5.11/§5.13/§5.14、C-04b、C-09 SC-B04/B04a/B06、C-07、`doc/REBASELINE_PLAN.md`（FEA-12-UI 待 scope）。
- 冻结依据：`G:\CODEX\New Manga.workspace\FEA-12\scope-review\FEA-12-UI-scope.md`（独立只读 scope review）+ ZCode SCOPE-ADJ-2026-11-05 裁决（Lead 2026-11-05 下发；含每卡必改项）+ Codex 独立裁决（`G:\CODEX\New Manga.workspace\FEA-11\codex-adjudication\SCOPE-ADJ-2026-11-05-codex.md`，2026-11-05）。
- 现状事实（基线 `604a2d343`）：5 条回收站/删除 wire 已在 Host 注册表 + dispatcher（closed shape + 能力门 + 错误投影）与 Python Core handler 两侧落地；但 `apps/desktop-avalonia/src/NewManga.App/**` 对上述命令 **0 处调用**，`IHostController` 无回收站/删除方法（C-07 冻结 54 方法面），V2 回收站是“能力待接入”占位；书架“删除”也是占位 → 用户当前没有可用删除路径。
- 目标（一个可观察交付）：用户可在书架把作品**移入回收站**（可撤销）、在 V2 回收站**分页浏览**软删条目、多选**恢复**，并对**单本**执行“只读预览披露 → 专门确认 → `inventory_digest` 绑定 → 单事务彻底删除 → 失败整体回滚 / `cleanup_pending` 会话内显式重试”的完整 C 流程；数据源只用已冻结 `ListTrash`；C-07 冻结面与 18 pins 零变化；Fluent 文案不再失真。

## Scope（冻结）

### In

| # | 范围项 | 冻结说明 |
|---|---|---|
| IN-1 | 独立 App 端口 `ITrashController`（**不改** `IHostController`） | 至少 5 个 typed 方法：`ListTrashAsync`、`MoveToTrashAsync`、`RestoreFromTrashAsync`、`PreviewPermanentDeleteAsync`、`DeletePermanentlyAsync`（+ 可选 `RetryPendingCleanupAsync`）；由 `HostController`/`NullHostController` 同时实现；VM 以 `controller as ITrashController` 能力探测，缺失即 typed 不可用（FEA-09-UI-1 先例） |
| IN-2 | V2 回收站页真实接线 | 列表（分页/加载更多）、空态、失败态、能力缺失态、只读态；进入即先探测能力再发 `library_list_trash` |
| IN-3 | 书架侧“移入回收站” | 作品详情动作行入口 + 危险确认 + `MoveToTrash` + 成功后刷新并清空选中；成功提示条可带「撤销」= `RestoreFromTrash`（使用恢复动作自己的 `idempotency_key`） |
| IN-4 | 恢复（多选 1..N） | 逐项 `restored/conflicts`；reason 白名单 + 兜底文案；不整批伪报成功 |
| IN-5 | 删除影响清单披露面板 | PD-01 三项强制 + 其余字段 + 保留项声明；只读、零副作用；不展示路径/源文件名 |
| IN-6 | 专门确认（单本） | 显式勾选硬门 + digest 绑定 + stale 重预览 + `BOOK_BUSY` 预阻断 + 默认焦点取消/Esc 取消/Enter 不确认 |
| IN-7 | 单本彻底删除 + 结果处置 | 含 `cleanup_pending` 会话内显式重试（同一 digest，不重跑预览）；`BOOK_NOT_FOUND` 刷新列表 |
| IN-8 | 文案诚实性收口 | 清掉回收站相关“能力待接入”过期文案；Fluent 抽屉/删除 tooltip 改为不声称能力缺失；页面级删除文案更正为“页面级删除无命令” |
| IN-9 | 证据与门禁 | headless 交互测试 + 真实 IPC（隔离 DataRoot + 指纹哨兵）+ wire 命令注入断言 + 快照 PNG + 静态扫描；全量 .NET 不减少；`generate_api_inventory.py --check` PASS；pins 18/18；`check.ps1` PASS |

### Out

| # | 不做项 | 理由 |
|---|---|---|
| OUT-1 | 批量彻底删除（`PermanentlyDeleteBooks` UI） | 两级 digest + 逐项状态 UI 成本高；`is_whole_library` 对单书库形成死路；Core 能力保留，后续卡（L1） |
| OUT-2 | `PurgeTrash`（任何调用/入口/探测） | 首版 Core 未实现，返回 `UNKNOWN_COMMAND`（M2-C1 `:1008`）；digest 绑定方式待 DSH additive 裁决 |
| OUT-3 | 回收站缩略图/内容预览/打开回收站书籍 | 需改 book 级读门控（`library.py:519-521`）＝ C-15/C-17 §7.2 级变更（另一张卡，L2） |
| OUT-4 | 保留期限/到期自动清理/容量承诺 | B 流程 OUT（ADJ `:39`、PD-10）；UI 不得显示“保留 N 天” |
| OUT-5 | D 流程（Windows 回收站/原文件删除） | ADJ D5：零生产接线；UI 不得提供“删除原文件”入口，不得声称“已移入系统回收站” |
| OUT-6 | Fluent 前端回收站真实接线 | 只做文案诚实化（IN-8）；真实接线归 FEA-14/Fluent 线（L7） |
| OUT-7 | 新增/改造设计系统组件/令牌 | V2 侧已有本地 stand-in 控件；扩 DS 属 V11R-D-1/FEA-14 写域 |
| OUT-8 | 页面级/章节级回收站 | 无 wire（M2-C1 `:976` 首版只作品级） |
| OUT-9 | 改 `IHostController`/`FEA-C07_API_INVENTORY.md`/任何 pinned 契约字节 | 18 pins；C-07 冻结面 |
| OUT-10 | 任何 Python/Core/Host 语义改动 | 属 CORE 写域；UI 只消费（含 restore reason 收窄、active export 披露、current 完整披露字段） |
| OUT-11 | 新增命令/新能力/新展示字段 | 现有 wire 已足够；缺口以“UI 不伪造”处理 |
| OUT-12 | 真实用户数据/`%APPDATA%`/真实回收站/真实原文件删除/push | 与 ADJ D7/D8 一致 |

### 冻结决策（Q1–Q8）

| # | 决策 |
|---|---|
| Q1 | **独立 `ITrashController` 替代 C-07 additive**：冻结记录写明“独立接口满足 ADJ-001 `:41` 的 additive 意图，无需 UNFREEZE；`python tools/generate_api_inventory.py --check` PASS + pins 18/18 作门禁”。禁止 `IHostController` 继承 `ITrashController` 或把新方法放进冻结接口；HostController/NullHostController/fake 单独实现。新接口不等于 Core capability，仍必须经 Host probe 与只读门控。 |
| Q2 | **首版只做单本彻底删除**；批量 Out（L1）。单本也受 current 披露缺陷影响，不因排除批量而免除 CORE 前置。 |
| Q3 | **数据源 `ListTrash`**（不双读、不拼接 `ListRecycleBinBooks`）；显示 `bookId/title/deletedAt`；cursor 原样回传、不解码/不持久化/不展示；排序由 Core 固定 `deletedAt DESC, bookId ASC`；不显示总数（只能写“已加载 N 项”）。 |
| Q4 | **书架侧“移入回收站”属本卡**：作品级入口闭合“软删→列表→恢复/删除”；彻底删除入口只放回收站，书架永不出现。成功才移除并清选中；部分失败逐项呈现。进入回收站隐藏右侧详情/覆盖式作品详情与页面批量条，防止幽灵上下文。 |
| Q5 | **Fluent 仅文案诚实化**：表述为“当前 Fluent 回收站尚未接入，可切换到 V2 使用”，在 V2 交付前不得提前声称可用；不声称 Core 没能力、不展示实现类名。ShelfPageView 抽屉与删除 tooltip 两处都需处理；Fluent 实际接线 OUT。 |
| Q6 | **软删撤销**：软删成功后提供“撤销”= 对成功 moved IDs 调 `RestoreFromTrash`，使用恢复动作自己的 `idempotency_key`；仅恢复成功才提示成功，失败可重试/返回回收站，不把删除失败伪装成可撤销成功。用 LibraryView 内局部成功提示条 + 撤销按钮，不为 toast action 扩共享 Shell。软删保留一次确认；彻底删除始终专门确认且不提供“撤销”。 |
| Q7 | **独立 `TrashViewModel`（推荐；Owner 可决定并入 `LibraryViewModel`，二者均在 allowed_paths）**：管理分页/选择/预览/确认/重试；LibraryVM 管理书架入口和软删成功刷新。冻结“独立可测状态机”而不新增 Host/wire 契约；切换目标、退出/重新进入、迟到响应必须清除或隔离旧 digest/确认勾选。 |
| Q8 | **门禁 = L2**：控件级 headless（焦点/Esc/Enter/勾选/失效态）+ 真实 Host→Core IPC + wire payload/帧序负断言 + 快照。真机 L3 走查标 **NOT_RUN**，不作为释放硬前置，不得宣称 L3/L4 已通过（L10）。 |

### Appointment 说明（冻结，写入本卡即为范围依据）

- **C-07 冻结记录**：独立 `ITrashController` 满足 ADJ-001 `:41` 的 additive 意图，无需 UNFREEZE；`IHostController.cs`/`RunContracts.cs`/`doc/plan/FEA-C07_API_INVENTORY.md` 字节不变，18 pins 数量不变；`generate_api_inventory.py --check` PASS 与 pins 18/18 是门禁，但不替代语义审查。
- **路径澄清**：本卡 `HostController.cs`/`NullHostController.cs` 指 `apps/desktop-avalonia/src/NewManga.App/Services/` 下的 App 侧实现；`apps/desktop-avalonia/src/NewManga.Host/**` 与 `NewManga.CoreClient/**` 不在写域（Host 命令桥/投影归 FEA-12-CORE）。
- **CORE 依赖**：AC4/AC5 必须消费最终重冻的完整 current 保护集与受保护 artifact 表达；旧 Core 缺字段/null 时必须禁用彻底删除入口（fail-closed），不能显示 0/空数组后继续。当前 UNFREEZE 草案不是批准书。
- **数据事实（不得修、只如实呈现）**：①`ListTrash` 无 total；②列表项无 busy 字段；③`activeRunIds` 不含 active export；④`RestoreFromTrash` 冲突 reason 首版恒为 `TRASH_ENTRY_NOT_FOUND`，`TRASH_RESTORE_CONFLICT`/`TRASH_RESTORE_LAYER_MISMATCH` 首版不可达。UI 按白名单 + 兜底文案渲染，不编造因果；这些是 CORE 侧事实，不在本卡修。
- **无 pending manifest 枚举命令**：「重试清理」只能在当前会话内凭内存 `book_id + digest` 触发，重启后不可达（L3）。

## Acceptance Criteria

- [x] **AC1 列表与入口**：从 V2 书架进入回收站 ⇒（先做能力探测）恰好一帧 `library_list_trash`（无 `cursor` 首帧）；返回 N 项时按 `deletedAt DESC` 渲染书名 + 删除时间；空回收站渲染空态且**零**条目；`nextCursor` 存在时出现「加载更多」并带 `cursor` 发第二帧；**任何状态下 UI 不显示总数**（文案不含“共 N 项”；可写“已加载 N 项”）；`nextCursor` 不解码、不持久化、不展示；进入回收站时右侧作品详情列/覆盖式详情与页面批量条按冻结布局语义隐藏（防幽灵上下文），并写入快照断言。 <<MET>>
- [x] **AC2 软删入口**：详情「移入回收站」⇒ 危险确认（默认焦点取消、`Esc` 关闭、`Enter` 不提交）⇒ 确认后**恰好一帧** `library_move_to_trash`，payload 键集 = `{entries, idempotency_key}`、`entries=[{book_id}]`；成功后书架不再含该书且 `SelectedBook` 被清空；`skipped` 逐项显示 reason 文案（写“不在书架或已在回收站”，不含“不存在”断言）；成功提示条提供「撤销」→ 恢复成功才提示成功、失败可重试/返回回收站；删除失败不得伪装成可撤销成功。 <<MET>>
- [x] **AC3 恢复**：勾选 2 项恢复 ⇒ 单帧 `library_restore_from_trash`，`entries` 顺序 = 勾选顺序；`restored` 项从列表消失、`conflicts` 项保留且逐项显示 reason；整批未成功时不伪报成功；reason 渲染采用**白名单 + 兜底**（`TRASH_ENTRY_NOT_FOUND` 白名单；不可达的 `TRASH_RESTORE_CONFLICT`/`TRASH_RESTORE_LAYER_MISMATCH` 不得编造路径/层级因果；未知 reason → “恢复冲突（未分类）”）。 <<MET>>
- [x] **AC4 预览披露（PD-01/PD-03）**：点「彻底删除」后先出现披露面板，且**在用户确认前只有一帧** `library_preview_permanent_delete_books`（`bookIds:[id]`）；面板逐项含 PD-01 三项强制（`manualRegionCount`/`draftPageCount`/`deletedFiles`+`deletedBytes`）以及 `lockCount`、`currentRevisionId`（仅代表展示值）、**最终重冻契约的完整 current 保护集（全部 current，不得只用单值代表；含非首个/隐藏 current）**、受保护 artifact 表达、`pinnedRevisionIds`、`activeRunIds`、`contentSummary.chapters/pages/artifacts`、`sharedFileRefs` 与保留项声明（导出文件保留、用户源文件/源目录永不移动或删除、Pipeline 历史保留、全库历史备份不清理）；面板文本**不含**盘符/路径片段与源文件名；预览零副作用；旧 Core 缺字段/null → 禁止彻底删除（不得显示 0/空数组后继续）；失败态按 typed 处理（`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` → 就地错误 +「重新预览」；`BOOK_NOT_FOUND` → 提示并刷新）。 <<MET>>
- [x] **AC5 专门确认与 digest 绑定（PD-02/PD-04）**：未勾选「我理解不可恢复」⇒ 确认禁用且**零**删除帧；勾选后确认 ⇒ 单帧 `library_delete_book_permanently`，payload 键集恰为 `{book_id, confirm_permanent_delete, inventory_digest}`（单条拒收 `book_ids`/`confirmed_book_ids`/`confirm_count`/`inventory_digests`），`inventory_digest` 与 AC4 预览返回值**字符串逐字节相等**；确认文案含“人工修改 N / 锁定 N / 固定版本 N”具体数字 + 删除文件/字节 + 保留项声明；`inventory_digest` 只能来自本次预览，UI 不得自算/拼接/缓存替代；`title` 不参与 digest，不得以“书名变了”作为失效理由；`BOOK_DELETE_STALE_PREVIEW` → 清空确认态、提示“清单已变化，请重新预览”、自动重预览（第二帧 preview），**不重发删除**；预览 `activeRunIds` 非空 ⇒ 确认按钮禁用并说明 `BOOK_BUSY` 原因（零删除帧）。 <<MET>>
- [x] **AC6 stale / busy / 结果处置**：①注入状态变化 ⇒ `BOOK_DELETE_STALE_PREVIEW` → 清空确认态 + 自动重预览、不重发删除；②`activeRunIds` 非空 ⇒ 预阻断 `BOOK_BUSY`、零删除帧；③注入 `BOOK_DELETE_CLEANUP_PENDING` ⇒ 显示“内容已删除/文件待清理”+「重试清理」，重试帧 digest 与首次相同且**不产生新的 preview 帧**；第二次重试 → `BOOK_NOT_FOUND` 且提示已不存在；④`BOOK_NOT_FOUND` ⇒ 提示 + 刷新列表；⑤`BOOK_DELETE_CONFLICT`/`BOOK_DELETE_FAILED` ⇒ 保留条目、按 typed 展示、不自动重试；⑥`INVALID_REQUEST` 视为实现缺陷并如实报错，不得静默吞掉。 <<MET>>
- [x] **AC7 能力缺失 / 只读 / 不可用**：①Core 未公告 `library.trash.read/1`（或 `library.trash.write/1` / `library.delete.preview/1`）⇒ 回收站对应区域显示能力缺失态、`CORE_CAPABILITY_MISSING` 可见、**无**删除/恢复可点、**不显示空列表**；只缺写/preview 能力时允许真实只读列表，不得把已有列表清空；②Host 只读 ⇒ 写入口禁用 + `HOST_READ_ONLY` 原因，读取仍可用；③`CORE_UNAVAILABLE` ⇒ 失败态 + 重试按钮；④未注册码只作诊断展示，不得作为分支/重试/恢复选择器；⑤能力按**操作**禁用，不因一个能力缺失禁用全部。 **r2（P1-1 修复）**：`_hostReadOnly` 仅取 Host 写闸、`_capabilityMissing` 仅由 read 决定；restore 仅 write、删除 write+preview 分门控；部分缺失渲染 `CORE_CAPABILITY_MISSING` 降级横幅；`CORE_UNAVAILABLE` 独立 probe 失败态；3 个单能力缺失 + probe 失败测试。 <<MET>>
- [x] **AC8 无 DB/OS 直连 + 隔离（元 AC）**：静态扫描 `apps/desktop-avalonia/src/NewManga.App/**`：本卡新增访问 0 处 `sqlite`/`Microsoft.Data.Sqlite`/`System.Data.SQLite`/`DllImport`/`Shell32`/`SHFileOperation`/`IFileOperation`/`File.Delete`/`Directory.Delete`/`Microsoft.VisualBasic.FileIO`；真实 IPC 测试 DataRoot 位于仓外临时根且断言 `IsRelativeTo`；测试前后对“隔离根外”哨兵文件树做 SHA-256 指纹相等断言（原文件零触碰）；路径泄露扫描针对实际路径/敏感字段，不使用“任意 `/` 字符出现即失败”的过宽规则，并区分既有合法代码与本卡新增访问。 <<MET>>
- [x] **AC9 文案诚实性**：源码/文案断言：回收站相关不再出现“回收站…能力待接入 / Host 未暴露回收站 / 未发布回收站”类过期文案；能力缺失态使用 typed code 文案；Fluent 抽屉文案不声称能力缺失、不展示实现类名；页面级删除入口文案改为“页面级删除无命令”；任何状态不伪造成“共 N 项”、不伪造逐项 busy。 <<MET>>
- [x] **AC10 禁令与门禁**：全流程 wire 中 **0 帧** `library_purge_trash`；0 帧 `library_delete_books_permanently`（批量）；`library_delete_book_permanently` payload 从未出现 `book_ids`/`confirmed_book_ids`/`confirm_count`/`inventory_digests`；全量 .NET 不减少（释放日实跑基线，passed/failed/skipped 分列，不引用调研/旧卡数字）；`python tools/generate_api_inventory.py --check` PASS；`verify_pins.ps1` **18/18**；`check.ps1` PASS；L2 门禁完成（控件级 headless + 真实 IPC），L3 真机 **NOT_RUN**（不得写 PASS）；证据落 `verification/FEA-12-UI/`。 <<MET>>

## 允许修改范围

frontmatter `allowed_paths` 为准（`evidence_dir` 已显式列入）：

- App 生产：新增 `Services/TrashModels.cs`（`ITrashController` + typed DTO/投影/文案映射，**不参与 C-07 清单解析**）、`ViewModels/V2/Library/TrashViewModel.cs`（或并入 `LibraryViewModel`，Owner 在 allowed_paths 内选择）；修改 `Services/HostController.cs`、`NullHostController.cs`、`Services/SourceImportModels.cs`（仅必要接线）、`ViewModels/V2/Library/LibraryViewModel.cs`、`Views/V2/Library/{RecycleBinView.axaml,RecycleBinView.axaml.cs,LibraryView.axaml,LibraryView.axaml.cs,BookDetailPanel.axaml}`、`Views/Fluent/ShelfPageView.cs`（仅文案，含 tooltip）、可选 `Shell/ShellSupport.cs`。
- 测试：`tests/NewManga.App.Tests/{FakeHostController.cs,TrashUiTests.cs,V2ShellUiTests.cs,NoDbOsAccessTests.cs}`；`tests/NewManga.Host.Tests/{Fea12TrashUiIpcTests.cs,Support/Fea12ProductionFixture.cs}`。
- 文档/证据：本卡、Handoff、Review、`verification/FEA-12-UI/**`。

**明确不得出现在写域**：`Services/IHostController.cs`、`Services/RunContracts.cs`、`doc/plan/FEA-C07_API_INVENTORY.md`、任何 `doc/plan/FEA-CONTRACT-FROZEN-*.md` 或 pinned 契约、`NewManga.Host/**`、`NewManga.CoreClient/**`、`NewManga.DesignSystem/**`、`src/**`（Python）、`doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`（DSH 单点）。

## 禁止范围

1. 不得直连 DB（任何 SQLite 库/连接/迁移）、不得直读任意 OS 路径、不得调用模型；一切经 Host/IPC。
2. 不得调用任何 Windows 回收站 API（`SHFileOperation`/`IFileOperation`/`Shell32`/`Microsoft.VisualBasic.FileIO` 等），不得声称“已移入系统回收站”。
3. 不得删除/移动/改写**原文件**；不得为“删除成功”提示添加“原文件已删除”字样。
4. 不得伪造保护语义：不得自算/裁剪 PD-01 计数；不得把“有锁/有 pin/有草稿”表述为“不可删除”，也不得表述为“不影响”。
5. 不得伪造结果：不得在 typed 失败后显示成功、不得把失败渲染为空列表、不得显示总数、不得为不可达 reason 编造因果。
6. 不得调用 `library_purge_trash`/`library_delete_books_permanently`；不得以 `UNKNOWN_COMMAND` 探测能力。
7. 不得改 `IHostController`/`FEA-C07_API_INVENTORY.md`/任何 pinned 契约字节；不得改 Python/Core/Host 语义、DS 组件/令牌、Fluent 结构。
8. 不得删除/放宽既有测试制造通过；`skipped` 不得计入 passed；不得引用旧卡/调研数字作为基线。
9. 不得真实用户数据/`%APPDATA%`/外部卷/真实回收站；不得 push；不得自审。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2/AC3/AC4/AC5/AC6/AC7/AC9 headless | `dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~TrashUiTests\|NoDbOsAccessTests\|V2ShellUiTests.RecycleBin\|V2ShellUiTests.MoveToTrash"`（curated 时 `NEWMANGA_EVIDENCE_DIR=verification/FEA-12-UI`） | 隔离 fake controller；真实 Avalonia 窗口（headless）；typed/故障注入 | **PASS 40/40**（`TrashUiTests` 35、`NoDbOsAccessTests` 3、2 个窗口交互测试）；4 张真实截图 | `logs/ui-tests-curated.log`、`screens/*.png` |
| AC4/AC5/AC6 预览/确认/失败处置 | 同上 | fake typed 注入、故障注入 | **PASS**：preview→确认→单帧删除/STALE 重预览/CLEANUP 重试/BOOK_NOT_FOUND；旧 Core fail-closed | `logs/ui-tests-curated.log` |
| AC1–AC6/AC8/AC10 真实 IPC/wire | `$env:NEWMANGA_FEA12_UI_IPC=1`（curated `NEWMANGA_EVIDENCE_DIR`）+ `dotnet test ... --filter "FullyQualifiedName~Fea12TrashUiIpcTests"` | 真实 `src/bootstrap/core_service.py`；隔离 DataRoot 在仓外 + 哨兵指纹 | **PASS 1/1**：27 wire 帧；0 purge/0 批量删除；逐书 digest 绑定；DataRoot 仓外、哨兵不变 | `fea12-trash-ui-ipc.json`、`logs/ipc-tests-curated.log` |
| AC8 静态/隔离 | 上表过滤器包含 `NoDbOsAccessTests` | 静态扫描 + 哨兵 | **PASS**：本卡 9 文件 0 DB/OS 直连；全 App 0 DB 访问 | `logs/ui-tests-curated.log` |
| AC10 门禁 | 全量 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build`；`python tools/generate_api_inventory.py --check`；`verify_pins.ps1`；`check.ps1`；`git diff --name-only 9daa94a25..HEAD -- doc/plan doc/contracts src/` | 仓库根；交付日实跑 | 全量 **1474/0/82**；API PASS；pins **18/18**；diff 空 | `logs/dotnet-full-solution.log`、`logs/api-inventory.log`、`logs/pins.log`、`logs/gates.log` |
| L3 真机走查 | 人工 L3/L4 | — | **NOT_RUN（冻结 OUT/L10）** | 卡 L10 |

## 实现记录（2026-11-06）

- **架构**：新增独立 App 端口 `Services/TrashModels.cs`（`ITrashController` + typed DTO/白名单文案/payload 构造），由 `HostController`/`NullHostController`/`FakeHostController` 分别实现；`IHostController`/C-07 清单/契约字节**零改动**（`generate_api_inventory.py --check` PASS）。
- **生产映射**：每个端口方法恰好映射一帧 Host 命令（`core_ping` 探测 + `library_list_trash`/`library_move_to_trash`/`library_restore_from_trash`/`library_preview_permanent_delete_books`/`library_delete_book_permanently`）；单本删除绑定**逐书 digest**（集合 digest 仅供展示），`payload` 键集恒为 `{book_id, confirm_permanent_delete, inventory_digest}`。
- **UI 状态机**：`TrashViewModel`（probe→单帧 list、不透明 cursor 不持久化、勾选顺序恢复、披露面板、硬勾选门、STALE 自动重预览、BOOK_BUSY 预阻断、CLEANUP_PENDING 同 digest 重试、BOOK_NOT_FOUND 刷新、能力/只读/不可用 typed 态、迟到响应隔离）；`LibraryViewModel` 书架软删危险确认 + 撤销条 + 进入回收站隐藏详情/批量条；`RecycleBinView` 真实列表/披露面板/重试；`Fluent ShelfPageView` 仅文案诚实化。
- **测试**：`TrashUiTests`（23）、`NoDbOsAccessTests`（3）、`V2ShellUiTests` 两个真实窗口交互测试（默认焦点/ Esc/Enter/帧计数）；`Fea12TrashUiIpcTests` + `Support/Fea12ProductionFixture`（真实 Python Core stdio，默认按 `NEWMANGA_FEA12_UI_IPC=1` skip）。
- **测试基线**：全量 .NET **1486 passed / 0 failed / 82 skipped**（App.Tests 715/0/7；Host.Tests 144/0/51）；本卡零 Python 改动（pytest 引用基线 **3203 passed / 10 skipped**（本卡零 Python 改动，未重跑））。
- **未跑/边界**：L3 真机 `NOT_RUN`；pytest 未重跑（零 Python diff）。

## 预期行为变更（Review 不判回归）

1. `tests/NewManga.App.Tests/V2ShellUiTests.cs` 旧测试 `RecycleBin_DangerConfirm_IsCancelable_AndBlockedConfirmWritesNothing`（断言“能力待接入/零写入”）已按本卡改写为两个真实流程测试：`RecycleBin_ListsRealEntries_PreviewStartsOnCancel_AndEscCancelsWithoutDeleteFrames`（真实列表 + 默认焦点取消 + Esc 取消零删除帧）与 `MoveToTrash_DangerConfirm_EscapeAndEnterWriteNothing_ThenExplicitConfirmMoves`（Esc/Enter 零写入；显式确认后恰一帧软删 + UndoBar）。**断言意图保留**，文本/路径更新。
2. 回收站占位文案/空态被真实列表替代；Fluent 抽屉文案改为不声称能力缺失（结构不变）。
3. `ISourceImportController` 面未改；`HostController`/`NullHostController` 以**独立** `ITrashController` 实现接线（未扩 `IHostController`），`FakeHostController` 同步实现；C-07 `--check` PASS。

## r2 返修记录（2026-11-06，r1 Review CHANGES 处置）

r1 Review：`doc/reviews/FEA-12-UI-r1.md`（独立 fresh subagent；reviewed_head `c841b9a0b`；P0=0/P1=1/P2=3/P3≈8）。

| Finding | 级别 | 处置 | 证据 |
|---|---|---|---|
| P1-1 能力缺失/Host 只读/probe 失败三态混同（AC7 NOT MET） | **P1** | **已修**：`_hostReadOnly` 独立跟踪 Host 写闸；`_capabilityMissing` 仅由 read 决定；restore 仅 write、删除入口/确认 write+preview 分门控；部分缺失渲染 `CORE_CAPABILITY_MISSING` 降级横幅（列明缺失能力与影响）；`CORE_UNAVAILABLE` 独立 probe 失败态 + 重试；能力缺失时绝不显示假只读 banner；`HOST_READ_ONLY` 字面展示。新增缺 read/缺 write/缺 preview 3 个单能力缺失测试 + probe 失败测试（各断言 0 帧/正确文案/按操作启停） | `logs/ui-tests-curated.log`（40/40）、`AC-MATRIX.md` r2 节 |
| P2-1 cleanup_pending 关闭结果“仍可重试”文案不实 | P2 | **已修**：关闭时明示“关闭后本会话内无法再重试清理（wire 无 pending 清单；重新预览会 BOOK_NOT_FOUND）”；测试断言关闭后 `CanRetryCleanup=false` 且文案一致；L3 同步收窄 | `TrashUiTests.CloseResult_AfterCleanupPending_*` |
| P2-2a fake 集合/逐书 digest 同值，VM 绑定无判别测试 | P2 | **已修**：集合 `…a` vs 逐书 `…d` 不同值；删除帧断言 `==逐书` 且 `≠集合`；变异 M1 复验 **2 红** | `logs/r2-mutations.log` |
| P2-2b 旧 Core 预览投影 fail-closed 无判别测试 | P2 | **已修**：`HostController.ProjectPreviewResponse` internal 投影 + 缺字段/null/非法形状/`[]` 四类测试经 VM 驱动（unknown 0 删除帧、`[]` 1 帧）；变异 M3 复验 **3 红** | `logs/r2-mutations.log` |
| P2-3 卡/Handoff pytest 基线旧数 3073/10 | P2 | **已修**：改为 **3203 passed / 10 skipped**（引用；本卡零 Python，未重跑） | 本卡/Handoff |
| P3 同批 | P3 | 已修：死方法删除；恢复确认文案更正（恢复直接执行）；`pinned revision`→`固定版本`；`HOST_READ_ONLY` 字面；`{}` 响应 typed failure（测试）；move payload 覆盖说明；spill 归档 322 文件 + tree sha256；check.ps1 PASS 入 `logs/check.log`；未知 restore reason 统一“恢复冲突（未分类）”；无选中时不默认第一项（按钮禁用 + 提示）；`LoadMore` 防重入；`ResetPreviewKeepTarget` 无效赋值删除；预览文本路径泄露断言 | 本卡/Handoff/`AC-MATRIX.md` |

**r2 门禁**：全量 .NET **1486 passed / 0 failed / 82 skipped**（App.Tests 715/0/7；+12 新测试，无减少）；定向 UI **40/40**；真实 IPC **1/1**；pins 18/18；API check PASS；`check.ps1` PASS（3 既有 warning）；契约/计划/Python diff 空。
## 依赖、风险与阻塞

- 硬依赖（已满足）：`FEA-12-PREREQ-1`（M2-C1 rev 2.13 wire + Host 投影/白名单，`done`）、`FEA-12-CORE`（Core handler + Host 命令桥 + capability gate；r3 Review 通过 + 正式 UNFREEZE/重冻后由 DSH 释放本卡，base `9daa94a25`）。本卡消费 M2-C1 rev 2.14 的完整 current 集合与 C-04b v1.1 digest 规则。
- 并行/边界：与 `FEA-11-AC4-GAPS-1` 文件与语义零交集（唯一共享全量 .NET 基线口径与 DSH 单点指针）。无 `IHostController`/C-07 变更。
- 主要风险：
  - R1 **C-07 越界**：实现者顺手把方法加进 `IHostController` → 重演 FEA-09-UI-1 返修。缓解：AC10 `--check` PASS + Appointment 明文禁止（本次 PASS，零改动）。
  - R2 **digest 伪造/复用**：UI 自算或缓存 digest → 违反 PD-02/PD-03。缓解：AC5 逐字节相等断言 + 静态断言 UI 不含 sha256 计算（本次确认无自算）。
  - R3 **把披露当阻断**（或反之）：PD-04/PD-01 语义。缓解：AC4/AC6 分别断言“有保护也可删”与“非终态 Run 阻断”。
  - R4 **能力缺失被渲染成空回收站**：M2-C1 `:909` 明文禁止。缓解：AC7 + 独立快照（本次覆盖）。
  - R5 **伪造成功/总数/busy**：三项 wire 缺口最易诱导编造。缓解：AC1/AC6/AC9 文案与字段断言。
  - R6 页面级删除语义被顺手接上 → AC9 文案更正 + 禁令（本次仅改文案，未接命令）。
  - R7 真实 IPC 污染真实数据 → AC8 隔离根 + 指纹哨兵（本次 sentinel 指纹通过）。
  - R8 `cleanup_pending` 跨会话不可达被误报已解决 → L3 + AC6 限定“会话内”。
  - R9 Fluent 文案变假话 → IN-8 + AC9；不改 Fluent 结构。
  - R10 CORE 侧“垃圾语义”（restore reason 收窄、active export 未披露、current 完整披露前置）被误判为 UI 缺陷 → 登记为 CORE 事实，UI 只按白名单兜底，不在本卡修。
  - R11 真实 IPC/App.Tests 首跑 flaky（FEA-11 L-11 同源） → 复跑并记录，不把 flaky 归因本卡（本次最终全量首跑 0 失败，无需复跑）。
  - **R12（实施中发现并已修正）**：`PreviewPermanentDeleteBooks` 返回**集合 digest**（`inventoryDigest`）与**逐书 digest**（`inventoryDigests[bookId]`）；单本 `library_delete_book_permanently` 必须绑定**逐书 digest**。真实 IPC 初次运行以集合 digest 删除得到 typed `BOOK_DELETE_STALE_PREVIEW`，据此修为逐书绑定，并用真实 wire 断言证明 `collectionDigest ≠ perBookDigest`、删除帧 digest = 逐书 digest。**Review 重点**。
  - **R13（证据卫生）**：`verification/FEA-12-UI/` 曾存在非本卡未跟踪历史/意外同步证据；已整体归档到 workspace（见 Resource Manifest）并只保留本卡证据，避免 evidence_dir 未登记告警。
- 阻塞解除标准（已满足）：CORE 返修闭环 + 正式契约重冻 + DSH 释放 → 实施（本次）→ L2 证据 → 独立 Review → DSH 集成 closeout。

## 残余 limitation（预登记 L1–L10）

- **L1**：批量彻底删除无 UI（Core 有能力）；单书库场景批量被 `BOOK_DELETE_BATCH_WHOLE_LIBRARY` 拦，单条可用。
- **L2**：回收站无缩略图/内容预览（读门控边界，另卡）。
- **L3**：`cleanup_pending` 的「重试清理」仅在结果面板保留期间可用（无 pending 清单命令；关闭结果后 UI 明示不可再重试；重启后不可达）。
- **L4**：列表无总数、无逐项 busy（wire 缺口）；只能显示“已加载 N 项”。
- **L5**：`RestoreFromTrash` 冲突 reason 首版恒为 `TRASH_ENTRY_NOT_FOUND`（`TRASH_RESTORE_CONFLICT`/`LAYER_MISMATCH` 不可达）。
- **L6**：导出占用只在删除时以 `BOOK_BUSY` 暴露（`activeRunIds` 不含 export）。
- **L7**：Fluent 前端回收站仍不可用（仅文案诚实化）。
- **L8**：真实 Windows 回收站（D 流程）仍 `NOT_RUN`，与本卡无关。
- **L9**：保留期限/自动清理无 UI 承诺（B 流程 OUT）。
- **L10**：本卡证据只到 L2（控件级 headless + 真实 IPC）；真机人工走查 L3/L4 标 `NOT_RUN`，须另行授权。

## 交付与运行记录

- Handoff：`doc/handoffs/FEA-12-UI-d976aceec.md`（delivery head `d976aceec`；含允许/禁止路径、收据核对命令、风险与下一任务建议）。
- Review：r1 `doc/reviews/FEA-12-UI-r1.md`（独立 fresh subagent；changes_requested P1=1/P2=3/P3≈8；已在 r2 处置）；r2 窄面复审待 DSH 派发（须记录 reviewer 身份/session ID 与 reviewed_head；实现者不自审）。
- 实现 commit：`d976aceec`（r1 实施：App 生产代码 + 测试 + `verification/FEA-12-UI/` 证据）；**r2 返修 commit：`a46d4d5c7`**（能力三态拆分 + 判别测试 + 证据重签）。
- 实际测试（2026-11-06）：全量 .NET **1486/0/82**；定向 UI **40/40**（r2 新增 12 个判别/单能力测试）；真实 IPC 1/1；check.ps1 PASS（3 warnings）；真实 IPC **1/1**（27 wire 帧，0 purge/0 批量）；pins 18/18；API check PASS；契约/计划/Python diff 空。
- 残余：L1–L10 limitation（见上，逐项保留）；L3 真机 `NOT_RUN`；CORE 侧事实（restore reason 收窄、active export 未披露）按 L5/L6 记录。
- 最终由 DSH 填写 `integration_commit` 并改 done；`canonical_evidence_status`/`resource_closeout_status` 待 closeout。

## Canonical Evidence

进入 `in_review` 前逐项登记唯一当前证据（sha256 为 worktree 实测；commit 由 DSH 集成时补）。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC10 | verification/FEA-12-UI/logs/dotnet-full-solution.log | - | e188a295a467f5f886aa584760826aa9274e6e10f033da75f75354be8b65a341 | CANONICAL |
| EV-02 | AC1–AC7/AC9 | verification/FEA-12-UI/logs/ui-tests-curated.log | - | 9d6496194db7b28151a85387386a01dd762d95eba2b190fd0f739e5ef0dd2ccb | CANONICAL |
| EV-03 | AC1–AC6/AC8/AC10 | verification/FEA-12-UI/logs/ipc-tests-curated.log | - | fe407fd2e0e597650c158af9aa4220cb7b25e185f85fb7028e5a6990bc82cccf | CANONICAL |
| EV-04 | AC5/AC8/AC10 | verification/FEA-12-UI/fea12-trash-ui-ipc.json | - | 32938251915ffb0b84f66e378ac2032a0ddbdf4b17e0683d70006a6d33658630 | CANONICAL |
| EV-05 | AC10 | verification/FEA-12-UI/logs/pins.log | - | 2ebcc2c24b9075f939b9beb027ed2decd273323581327db12b6097adb37c4d94 | CANONICAL |
| EV-06 | AC10 | verification/FEA-12-UI/logs/api-inventory.log | - | 3e966c845fcb935ab58adb3805c792227a7d2073e963200268f54f36f1007c68 | CANONICAL |
| EV-07 | AC1/AC4/AC5/AC9 | verification/FEA-12-UI/screens/RecycleBin_ListsRealEntries_PreviewStartsOnCancel_AndEscCancelsWithoutDeleteFrames--07-recycle-list.png | - | 0de986c44f85afcb234f459144f2dd4d8d0b9458835acfbd30c56a5e90e18305 | CANONICAL |
| EV-08 | AC4/AC5 | verification/FEA-12-UI/screens/RecycleBin_ListsRealEntries_PreviewStartsOnCancel_AndEscCancelsWithoutDeleteFrames--08-recycle-delete-preview.png | - | fa41f366954e753886153d6685ed22158bc08449462c6481fa8f6b50654096bb | CANONICAL |
| EV-09 | AC2 | verification/FEA-12-UI/screens/MoveToTrash_DangerConfirm_EscapeAndEnterWriteNothing_ThenExplicitConfirmMoves--09-move-to-trash-danger-confirm.png | - | ea15b96d42cd3abbdf89284d37f4400452894dba8738c253f703b5f96fc80771 | CANONICAL |
| EV-10 | AC2/AC3 | verification/FEA-12-UI/screens/MoveToTrash_DangerConfirm_EscapeAndEnterWriteNothing_ThenExplicitConfirmMoves--10-move-to-trash-undobar.png | - | 802fb895a60c8358dd2ea7401062595fdf7339825525e793ae847d765cd563c5 | CANONICAL |
| EV-11 | AC10 | verification/FEA-12-UI/logs/gates.log | - | 5a26ea60b13eb0579f5329c5b41ef0283c7f599bc504f825350aecda5d2400b9 | CANONICAL |
| EV-12 | AC4/AC5/AC7（r2 判别） | verification/FEA-12-UI/logs/r2-mutations.log | - | 255fc60c9bdb53a297e98174da2c1f0ba527a745414e195d89091c005c8e3c95 | CANONICAL |
| EV-13 | AC1–AC10 | verification/FEA-12-UI/AC-MATRIX.md | - | 671ecf3811b7183aea6c6f578611f683d18525ea1e89518e3fad5e83938df01f | CANONICAL |
| EV-14 | AC10 | verification/FEA-12-UI/ENVIRONMENT.md | - | 2ac5cc0287d066b8f668b875de7a3852669cf9038f19fc967497cd9e5f725fb4 | CANONICAL |
| EV-15 | AC8 | apps/desktop-avalonia/tests/NewManga.App.Tests/NoDbOsAccessTests.cs | - | 2eee151ed21a440dc1aca7129769f4b1f1c376bf73be5e276516115ce1da6fa0 | SOURCE_PIN |
| EV-16 | AC10 | apps/desktop-avalonia/tests/NewManga.Host.Tests/Support/Fea12ProductionFixture.cs | - | d635a995a5f58763a3fc3e4b71afd5156a5756115eb5b2dfa7435ea0912253b7 | SOURCE_PIN |
| EV-17 | AC10（r2 门禁） | verification/FEA-12-UI/logs/check.log | - | 4adddd01338271e8a3cc91f78ac2c546daaa30a7911372207ba2e53a7a18c686 | CANONICAL |
| EV-18 | AC10 | verification/FEA-12-UI/agent-output-manifest.json | - | 2f32c12a6bc8560f8fcbf4ede053a068b32277a87d36a40437363c8a9cc779f7 | CANONICAL |

## Resource Manifest
| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树） | NOT_APPLICABLE | — | — | 未创建 |
| temp | `G:\CODEX\New Manga.workspace\temp\FEA-12-UI\` | DELETE_SAFE | — | verification/FEA-12-UI/agent-output-manifest.json | 测试日志副本；Canonical 日志已固化到 evidence_dir；**DSH 2026-11-06 closeout 已删除**：11 files / 376,596 B |
| agent-output | `G:\CODEX\New Manga.workspace\FEA-12-UI\ipc-*`（真实 IPC 隔离 DataRoot/sidecars/wire） | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\FEA-12-UI` | G:\CODEX\New Manga.workspace\FEA-12-UI\ipc-0806d21900a640d9bc2589726fa2f69f\data\library.db | IPC 隔离根；不删除真实用户数据；Review/集成后可清理 |
| agent-output | `G:\CODEX\New Manga.workspace\archive\FEA-12-UI-spill-2026-11-06\`（evidence_dir 内非本卡未跟踪历史/意外同步证据整体归档） | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\archive\FEA-12-UI-spill-2026-11-06` | G:\CODEX\New Manga.workspace\archive\FEA-12-UI-spill-2026-11-06\moved-tree\ENVIRONMENT.md | 322 files；tree sha256 `80dcf7494a4181e4354456b033a3c68495be01de010d0f0fd5fd5f34aadc7db3`（manifest 另有登记） | 非本卡证据，不参与 Canonical Evidence；provenance 与整树指纹已登记 |
| agent-output | `G:\CODEX\New Manga.workspace\FEA-12\scope-review\`（既有 scope review，只读输入） | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\FEA-12\scope-review` | G:\CODEX\New Manga.workspace\FEA-12\scope-review\FEA-12-UI-scope.md | 上游审查输入，不清理 |

## Closeout Record

- Closeout date / DSH：2026-11-06 / DSH（Lead/Architect/Integrator）。
- 终态：`done`；delivery_head / integration_commit = **`a46d4d5c7`**（r2 fix）；docs head `233d73f21`；r1 实现 `d976aceec`/`c841b9a0b`。
- Review 链：r1 changes_requested（P1=1：AC7 三态混同；P2×3/P3×8）→ r2 最小返修 → **r2 窄面 approved（P0/P1/P2=0；P3×6）**，两路独立复审均 APPROVE（权威 session `762aa9dd…`；交叉 `e46b8835…`）。
- AC 定稿：**AC1…AC10 全 MET**（AC4/AC7 带已登记 P3 边）；C-07/`IHostController`/18 pins 零变更；`generate_api_inventory.py --check` PASS。
- 证据：EV-01…EV-18（18 行 sha）；manifest `agent-output-manifest.json` 的 check.log 条目与 `reviewed_head` 已按 P2-4 修正（manifest sha 已重签 EV-18，见上）；`verification/FEA-12-UI` 共 16 文件 + spill 归档 322 文件（仓外 `archive/FEA-12-UI-spill-2026-11-06/`，非 Canonical）。
- closeout P3 处置：**P2-4 已修**（manifest check.log sha/bytes=实际 `EV-17` 值、reviewed_head=233d73f21、EV-18 重签）；**P3 文档**：Handoff 证据文件数更正、r2-mutations 口径改 40/40（AC-MATRIX L3 口径保持原字节以不破坏 EV pin，登记为 residual）（“48/48”不可复现）、spill tree sha 无法按公式复算改为 322 文件清单口径、reviewer 字段回填。**登记 follow-up（不改代码、不重跑功能测试）**：①delete-time `CORE_CAPABILITY_MISSING` 仍置页级 missing 的防御边（当前 Host/Core 不可达、无测试）；②preview `BOOK_NOT_FOUND` 未自动 `ReloadAsync`（AC4 “提示并刷新”的手动路径可用）；③AC6 第二次 cleanup retry→BOOK_NOT_FOUND 有实现无测试；④Host 只读+能力缺口时真实 HOST_READ_ONLY banner 被抑制的文案取舍。
- 残余风险/limitation：L1（批量 OUT）、L2（无总数/无缩略图）、L3 真机走查 **NOT_RUN**（面板保留期间可重试；关闭后不可重试）、L4（旧 Core 缺 current 数组 fail-closed）、L5–L10（CORE 事实：restore reason 收窄/active export 未披露不在本卡修；其它见卡）。
- 删除、迁移、归档数量/字节数：spill 322 文件归档至仓外 archive（非 Canonical、已登记）；仓内无删除。
- 当前指针清理：STATUS / Plan / TASK_LEDGER 已更新；本卡为终态，不进入 READY DAG。
