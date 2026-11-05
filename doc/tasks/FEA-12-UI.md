---
id: FEA-12-UI
title: FEA-12 回收站 UI 切片（V2 单本彻底删除 + 软删/恢复 + Fluent 文案诚实化）
kind: implementation
governance_version: 3
status: ready
approval: scope 已按 ZCode SCOPE-ADJ-2026-11-05 冻结，**DSH 2026-11-06 释放（ready）**：整卡释放前置 = FEA-12-CORE 返修闭环 + 正式契约重冻/重新 closeout；释放时由 DSH 固定 base_commit、Owner 与上下文独立 Reviewer
suggested_owner: zcode
owner: null
reviewer: null
depends_on:
  - FEA-12-PREREQ-1
  - FEA-12-CORE
base_commit: 9daa94a25   # 释放点 main head（SCAN-1 r2 交付后）
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

> **状态：`proposed`。本卡 scope 已按 ZCode SCOPE-ADJ-2026-11-05 冻结，待 Lead（DSH）释放；释放前不得实施、不得改卡面语义。**
>
> **释放门禁（硬）**：FEA-12-CORE 返修（完整 current 保护披露/摘要绑定 + 混合 retry 集合 digest）完成 r3 Review + DSH 集成验证 + 正式 UNFREEZE/契约重冻后，才可释放本卡。本卡 AC4/AC5 消费**最终重冻的完整 current 保护集与受保护 artifact 表达**；当前 UNFREEZE 草案不得直接当作已冻接口。
>
> 范围事实基线：`main@604a2d343`（scope review 基线）；committed `main@f4882077a` 记录 FEA-12-CORE 为 `changes_requested` 重开；当前工作树已出现 CORE r3 返修交付（`in_review`，未提交），另有 M2-C1 rev 2.14 / C04b v1.1 重冻草案（未提交、未批准）。本卡释放仍待 r3 Review + DSH 集成 + 正式重冻/重新 closeout。

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

- [ ] **AC1 列表与入口**：从 V2 书架进入回收站 ⇒（先做能力探测）恰好一帧 `library_list_trash`（无 `cursor` 首帧）；返回 N 项时按 `deletedAt DESC` 渲染书名 + 删除时间；空回收站渲染空态且**零**条目；`nextCursor` 存在时出现「加载更多」并带 `cursor` 发第二帧；**任何状态下 UI 不显示总数**（文案不含“共 N 项”；可写“已加载 N 项”）；`nextCursor` 不解码、不持久化、不展示；进入回收站时右侧作品详情列/覆盖式详情与页面批量条按冻结布局语义隐藏（防幽灵上下文），并写入快照断言。
- [ ] **AC2 软删入口**：详情「移入回收站」⇒ 危险确认（默认焦点取消、`Esc` 关闭、`Enter` 不提交）⇒ 确认后**恰好一帧** `library_move_to_trash`，payload 键集 = `{entries, idempotency_key}`、`entries=[{book_id}]`；成功后书架不再含该书且 `SelectedBook` 被清空；`skipped` 逐项显示 reason 文案（写“不在书架或已在回收站”，不含“不存在”断言）；成功提示条提供「撤销」→ 恢复成功才提示成功、失败可重试/返回回收站；删除失败不得伪装成可撤销成功。
- [ ] **AC3 恢复**：勾选 2 项恢复 ⇒ 单帧 `library_restore_from_trash`，`entries` 顺序 = 勾选顺序；`restored` 项从列表消失、`conflicts` 项保留且逐项显示 reason；整批未成功时不伪报成功；reason 渲染采用**白名单 + 兜底**（`TRASH_ENTRY_NOT_FOUND` 白名单；不可达的 `TRASH_RESTORE_CONFLICT`/`TRASH_RESTORE_LAYER_MISMATCH` 不得编造路径/层级因果；未知 reason → “恢复冲突（未分类）”）。
- [ ] **AC4 预览披露（PD-01/PD-03）**：点「彻底删除」后先出现披露面板，且**在用户确认前只有一帧** `library_preview_permanent_delete_books`（`bookIds:[id]`）；面板逐项含 PD-01 三项强制（`manualRegionCount`/`draftPageCount`/`deletedFiles`+`deletedBytes`）以及 `lockCount`、`currentRevisionId`（仅代表展示值）、**最终重冻契约的完整 current 保护集（全部 current，不得只用单值代表；含非首个/隐藏 current）**、受保护 artifact 表达、`pinnedRevisionIds`、`activeRunIds`、`contentSummary.chapters/pages/artifacts`、`sharedFileRefs` 与保留项声明（导出文件保留、用户源文件/源目录永不移动或删除、Pipeline 历史保留、全库历史备份不清理）；面板文本**不含**盘符/路径片段与源文件名；预览零副作用；旧 Core 缺字段/null → 禁止彻底删除（不得显示 0/空数组后继续）；失败态按 typed 处理（`BOOK_DELETE_PROTECTION_INVENTORY_UNAVAILABLE` → 就地错误 +「重新预览」；`BOOK_NOT_FOUND` → 提示并刷新）。
- [ ] **AC5 专门确认与 digest 绑定（PD-02/PD-04）**：未勾选「我理解不可恢复」⇒ 确认禁用且**零**删除帧；勾选后确认 ⇒ 单帧 `library_delete_book_permanently`，payload 键集恰为 `{book_id, confirm_permanent_delete, inventory_digest}`（单条拒收 `book_ids`/`confirmed_book_ids`/`confirm_count`/`inventory_digests`），`inventory_digest` 与 AC4 预览返回值**字符串逐字节相等**；确认文案含“人工修改 N / 锁定 N / 固定版本 N”具体数字 + 删除文件/字节 + 保留项声明；`inventory_digest` 只能来自本次预览，UI 不得自算/拼接/缓存替代；`title` 不参与 digest，不得以“书名变了”作为失效理由；`BOOK_DELETE_STALE_PREVIEW` → 清空确认态、提示“清单已变化，请重新预览”、自动重预览（第二帧 preview），**不重发删除**；预览 `activeRunIds` 非空 ⇒ 确认按钮禁用并说明 `BOOK_BUSY` 原因（零删除帧）。
- [ ] **AC6 stale / busy / 结果处置**：①注入状态变化 ⇒ `BOOK_DELETE_STALE_PREVIEW` → 清空确认态 + 自动重预览、不重发删除；②`activeRunIds` 非空 ⇒ 预阻断 `BOOK_BUSY`、零删除帧；③注入 `BOOK_DELETE_CLEANUP_PENDING` ⇒ 显示“内容已删除/文件待清理”+「重试清理」，重试帧 digest 与首次相同且**不产生新的 preview 帧**；第二次重试 → `BOOK_NOT_FOUND` 且提示已不存在；④`BOOK_NOT_FOUND` ⇒ 提示 + 刷新列表；⑤`BOOK_DELETE_CONFLICT`/`BOOK_DELETE_FAILED` ⇒ 保留条目、按 typed 展示、不自动重试；⑥`INVALID_REQUEST` 视为实现缺陷并如实报错，不得静默吞掉。
- [ ] **AC7 能力缺失 / 只读 / 不可用**：①Core 未公告 `library.trash.read/1`（或 `library.trash.write/1` / `library.delete.preview/1`）⇒ 回收站对应区域显示能力缺失态、`CORE_CAPABILITY_MISSING` 可见、**无**删除/恢复可点、**不显示空列表**；只缺写/preview 能力时允许真实只读列表，不得把已有列表清空；②Host 只读 ⇒ 写入口禁用 + `HOST_READ_ONLY` 原因，读取仍可用；③`CORE_UNAVAILABLE` ⇒ 失败态 + 重试按钮；④未注册码只作诊断展示，不得作为分支/重试/恢复选择器；⑤能力按**操作**禁用，不因一个能力缺失禁用全部。
- [ ] **AC8 无 DB/OS 直连 + 隔离（元 AC）**：静态扫描 `apps/desktop-avalonia/src/NewManga.App/**`：本卡新增访问 0 处 `sqlite`/`Microsoft.Data.Sqlite`/`System.Data.SQLite`/`DllImport`/`Shell32`/`SHFileOperation`/`IFileOperation`/`File.Delete`/`Directory.Delete`/`Microsoft.VisualBasic.FileIO`；真实 IPC 测试 DataRoot 位于仓外临时根且断言 `IsRelativeTo`；测试前后对“隔离根外”哨兵文件树做 SHA-256 指纹相等断言（原文件零触碰）；路径泄露扫描针对实际路径/敏感字段，不使用“任意 `/` 字符出现即失败”的过宽规则，并区分既有合法代码与本卡新增访问。
- [ ] **AC9 文案诚实性**：源码/文案断言：回收站相关不再出现“回收站…能力待接入 / Host 未暴露回收站 / 未发布回收站”类过期文案；能力缺失态使用 typed code 文案；Fluent 抽屉文案不声称能力缺失、不展示实现类名；页面级删除入口文案改为“页面级删除无命令”；任何状态不伪造成“共 N 项”、不伪造逐项 busy。
- [ ] **AC10 禁令与门禁**：全流程 wire 中 **0 帧** `library_purge_trash`；0 帧 `library_delete_books_permanently`（批量）；`library_delete_book_permanently` payload 从未出现 `book_ids`/`confirmed_book_ids`/`confirm_count`/`inventory_digests`；全量 .NET 不减少（释放日实跑基线，passed/failed/skipped 分列，不引用调研/旧卡数字）；`python tools/generate_api_inventory.py --check` PASS；`verify_pins.ps1` **18/18**；`check.ps1` PASS；L2 门禁完成（控件级 headless + 真实 IPC），L3 真机 **NOT_RUN**（不得写 PASS）；证据落 `verification/FEA-12-UI/`。

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
| AC1/AC2/AC3/AC7/AC9 headless | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --filter "FullyQualifiedName~TrashUiTests"` | 隔离 fake controller；headless | NOT_RUN（待释放） | `verification/FEA-12-UI/logs/app-trash-ui.log`（计划） |
| AC4/AC5/AC6 预览/确认/失败处置 | 同上（`TrashUiTests` + `V2ShellUiTests` 预期行为变更） | fake typed 注入、故障注入 | NOT_RUN | 同上 |
| AC1–AC6 真实 IPC/wire | `$env:NEWMANGA_FEA12_UI_IPC=1; dotnet test ... --filter "FullyQualifiedName~Fea12TrashUiIpcTests"` | 真实 Python Core；隔离 DataRoot + 指纹哨兵 | NOT_RUN | `logs/fea12-trash-ui-ipc.log`、wire NDJSON |
| AC8 静态/隔离 | `dotnet test ... --filter "FullyQualifiedName~NoDbOsAccessTests"` + 指纹断言 | 静态扫描 + 哨兵 | NOT_RUN | `logs/no-db-os-scan.log` |
| AC10 门禁 | 全量 `dotnet test apps/desktop-avalonia/NewManga.sln -c Release`；`python tools/generate_api_inventory.py --check`；`verify_pins.ps1`；`check.ps1`；`git diff --stat` | 仓库根；释放日基线实跑 | NOT_RUN | `logs/dotnet-full.log`、`api-inventory-check.log`、`pins.log`、`check.log` |
| L3 真机走查 | 人工 L3/L4 | — | **NOT_RUN（冻结 OUT/L10）** | `logs/l3-not-run.md` |

## 预期行为变更（Review 不判回归）

1. `tests/NewManga.App.Tests/V2ShellUiTests.cs:566-595`（`RecycleBin_DangerConfirm_IsCancelable_AndBlockedConfirmWritesNothing`）现断言“能力待接入/零写入”；本卡后该场景变为真实流程，测试改写为“未勾选时零删除帧 + 取消零写入”（**断言意图保留**，文本与路径更新）。
2. 回收站占位文案/空态被真实列表替代；Fluent 抽屉文案更新（结构不变）。
3. `ISourceImportController`/`HostController`/`NullHostController` 若为接线做必要扩展，`FakeHostController` 同步实现；C-07 `--check` 必须仍 PASS。

## 依赖、风险与阻塞

- 硬依赖：`FEA-12-PREREQ-1`（M2-C1 rev 2.13 wire + Host 投影/白名单，`done`）、`FEA-12-CORE`（Core handler + Host 命令桥 + capability gate）。**`FEA-12-CORE` 处于重开返修链**（current 完整披露/摘要绑定 + 混合 retry 集合 digest；committed `main@f4882077a` 为 `changes_requested`，工作树已有 r3 `in_review` 交付但未提交）；整卡释放必须等其 r3 Review + DSH 集成验证 + 正式 UNFREEZE/契约重冻 + 重新 closeout。
- 并行/边界：与 `FEA-11-AC4-GAPS-1` 文件与语义零交集（唯一共享全量 .NET 基线口径与 DSH 单点指针）。无 `IHostController`/C-07 变更。
- 主要风险：
  - R1 **C-07 越界**：实现者顺手把方法加进 `IHostController` → 重演 FEA-09-UI-1 返修。缓解：AC10 `--check` PASS + Appointment 明文禁止。
  - R2 **digest 伪造/复用**：UI 自算或缓存 digest → 违反 PD-02/PD-03。缓解：AC5 逐字节相等断言 + 静态断言 UI 不含 sha256 计算。
  - R3 **把披露当阻断**（或反之）：PD-04/PD-01 语义。缓解：AC4/AC6 分别断言“有保护也可删”与“非终态 Run 阻断”。
  - R4 **能力缺失被渲染成空回收站**：M2-C1 `:909` 明文禁止。缓解：AC7 + 独立快照。
  - R5 **伪造成功/总数/busy**：三项 wire 缺口最易诱导编造。缓解：AC1/AC6/AC9 文案与字段断言。
  - R6 页面级删除语义被顺手接上 → AC9 文案更正 + 禁令。
  - R7 真实 IPC 污染真实数据 → AC8 隔离根 + 指纹哨兵。
  - R8 `cleanup_pending` 跨会话不可达被误报已解决 → L3 + AC6 限定“会话内”。
  - R9 Fluent 文案变假话 → IN-8 + AC9；不改 Fluent 结构。
  - R10 CORE 侧“垃圾语义”（restore reason 收窄、active export 未披露、current 完整披露前置）被误判为 UI 缺陷 → 登记为 CORE 事实，UI 只按白名单兜底，不在本卡修。
  - R11 真实 IPC/App.Tests 首跑 flaky（FEA-11 L-11 同源） → 复跑并记录，不把 flaky 归因本卡。
- 阻塞解除标准：CORE 返修闭环 + 正式契约重冻（完整 current/受保护 artifact 表达）+ DSH 冻结 UI 最终 DTO/AC/base/head → 释放 ZCode → 实施 → L2 证据 → 独立 Review → DSH 集成 closeout。

## 残余 limitation（预登记 L1–L10）

- **L1**：批量彻底删除无 UI（Core 有能力）；单书库场景批量被 `BOOK_DELETE_BATCH_WHOLE_LIBRARY` 拦，单条可用。
- **L2**：回收站无缩略图/内容预览（读门控边界，另卡）。
- **L3**：`cleanup_pending` 的「重试清理」仅当前会话可用（无 pending 清单命令），重启后不可达。
- **L4**：列表无总数、无逐项 busy（wire 缺口）；只能显示“已加载 N 项”。
- **L5**：`RestoreFromTrash` 冲突 reason 首版恒为 `TRASH_ENTRY_NOT_FOUND`（`TRASH_RESTORE_CONFLICT`/`LAYER_MISMATCH` 不可达）。
- **L6**：导出占用只在删除时以 `BOOK_BUSY` 暴露（`activeRunIds` 不含 export）。
- **L7**：Fluent 前端回收站仍不可用（仅文案诚实化）。
- **L8**：真实 Windows 回收站（D 流程）仍 `NOT_RUN`，与本卡无关。
- **L9**：保留期限/自动清理无 UI 承诺（B 流程 OUT）。
- **L10**：本卡证据只到 L2（控件级 headless + 真实 IPC）；真机人工走查 L3/L4 标 `NOT_RUN`，须另行授权。

## 交付与运行记录

- Handoff：尚无（待释放/实施后新增 `doc/handoffs/FEA-12-UI-*.md`）。
- Review：尚无（独立上下文 Reviewer，须记录 session ID 与来源；作者不得自审）。
- 实际测试：尚无（当前 `status: proposed`，未实施、未跑本卡测试）。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 DSH 填写 `integration_commit` 并改 done。

## Canonical Evidence

进入 `in_review` 前逐项登记唯一当前证据；本卡尚未实施，表格为空。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main 工作树；释放时由 DSH 固定） | NOT_APPLICABLE | — | — | 未创建 |
| temp | `G:\CODEX\New Manga.workspace\temp\FEA-12-UI\`（预计隔离 DataRoot） | DELETE_SAFE（预计） | — | — | 未创建；实施后按实际登记 |
| agent-output | `G:\CODEX\New Manga.workspace\FEA-12\scope-review\`（既有 scope review，只读输入） | PRESERVE_REFERENCED | 原路径 | — | 上游审查输入，不清理 |
| agent-output | — | NOT_APPLICABLE | — | — | 本卡尚未产生 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：L1–L10（见上）；CORE 侧事实（restore reason 收窄、active export 未披露）不在本卡修。
- 当前指针清理：待 DSH closeout 时更新 STATUS / Plan / TASK_LEDGER 或说明无需更新。
