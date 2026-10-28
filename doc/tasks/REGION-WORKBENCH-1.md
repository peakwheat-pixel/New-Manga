---
id: REGION-WORKBENCH-1
title: 工作台接真实 region（读/改标/撤销/重渲染）+ 只读门
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups
suggested_owner: region-workbench-owner
owner: null
reviewer: dsh
depends_on: [S4-CMD-BATCH-1]
base_commit: 8831b4273d48faf4b6fd1e105321e89fdb7427bc
branch: task/REGION-WORKBENCH-1
worktree: G:/CODEX/New Manga.workspace/worktrees/REGION-WORKBENCH-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/REGION-WORKBENCH-1
allowed_paths:
  - doc/tasks/REGION-WORKBENCH-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/REGION-WORKBENCH-1/**
  - G:/CODEX/New Manga.workspace/task-envs/REGION-WORKBENCH-1/**
  - G:/CODEX/New Manga.workspace/worktrees/REGION-WORKBENCH-1/**
---

# REGION-WORKBENCH-1：工作台接真实 region + 写入口 + 只读门

## 来源与目标

- 登记来源：[AD002-FOLLOWUPS-1](AD002-FOLLOWUPS-1.md) 遗留 #19「region 写 UI 入口 + 只读门（S5）」。
- 前序：[S4-CMD-BATCH-1](S4-CMD-BATCH-1.md) `done`（集成 `0fba83021`）已把 region 读/写命令接到 `HostCommandDispatcher`，但**未新增 `HostRuntime` 公开写方法、未接 UI**；其 Review 遗留明确「region 写 UI 入口 + 只读门留 S5」。
- 现状（2026-10-28 HEAD `8831b4273` 实测）：
  - `apps/desktop-avalonia/src/NewManga.App/Views/ReaderWorkbenchPages.cs:19` 的工作台是 S4 骨架：`RegionItem` 为内存模型（`ViewModels/WorkbenchViewModel.cs`）、画布标注「Core tile 预览占位」；`RegionList` 来自内存 `AddRegion`，不接 Core。
  - `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` 只有 ListBooks/CreateChapter/CreateBook/RoundTripChineseTitle/ListChapters/GetReaderProjection/SaveReadingProgress/ReadPageImage 公开方法，**无 region 读/写方法**。
  - `CoreServiceClient` 无 `ListChapterPages`/`ListRegions`/`ListRegionRevisions`/`SetRegionType`/`RestoreRegionRevision`/`RerenderPage` 强类型方法（仅 dispatcher 层可执行）。
- 目标（一个可观察交付）：真机打开工作台 → 选书/章/页 → 看到真实页图与 Core region 覆盖框 → 选中 region 看到类型/origin/revision → 改类型、撤销到上一 revision、重渲染本页；只读 Host 下写入口禁用且后端 typed 拒绝。

## 范围冻结（首切片，超范围须先经 DSH 登记）

**包含**：单页工作台的 region 读取（`list_chapter_pages` + `list_regions` + `list_region_revisions`）、改类型（`set_region_type`）、撤销（`restore_region_revision`）、重渲染（`rerender_page`）、`Policy.WritesAllowed` 只读门（Host 层 + UI 层）。

**不包含**：新建/删除 region（`CreateRegion`/`DeleteRegion`）、译文编辑（`SaveManualTranslation`）、锁定/取消锁定（`SetRevisionPinned`）、批量操作、Run 触发、翻译 provider、多页缩略图导航（页选择用章内有序页列表）、旧壳改动、Python Core 改动、冻结契约改动。

## Acceptance Criteria

- [ ] **AC1 读面接线**：`CoreServiceClient` 新增 `ListChapterPagesAsync`（wire `list_chapter_pages`，minor 6）、`ListRegionsAsync`（wire `list_regions`）、`ListRegionRevisionsAsync`（wire `list_region_revisions`，minor 3）强类型读；`HostRuntime` 暴露同名读方法并与既有 reader I/O gate 串行（core pipe 严格请求/响应）；`IHostController`/`HostController`/`NullHostController` 同步扩展；工作台通过真实 book→chapter→page 选择加载页图（复用 `ReadPageImageAsync`）与 region 覆盖（`geometry` 归一化 + `page_size` 像素投影，沿 `1.5` additive widening），左侧列表显示真实 region 且与画布选中双向同步。证据：Host 集成测试对真实 fixture 断言 region 投影与几何；App headless 测试断言接线；真机截图。
- [ ] **AC2 写入口**：`HostRuntime` 新增 `SetRegionTypeAsync`/`RestoreRegionRevisionAsync`/`RerenderPageAsync`，**全部先检查 `Policy.WritesAllowed`**（沿 `CreateBookAsync`/`SaveReadingProgressAsync` 模式，typed `ReadOnlyHostException`、请求不达 Core）；工作台提供改类型下拉+应用、撤销上一 revision（需先 `list_region_revisions` 取得上一版）、重渲染本页按钮；写成功后刷新 region 列表/revision 与页图。证据：Host 集成测试真实写入（revision_no 递增、restored revision、rerender 产物/预览）、App headless 测试。
- [ ] **AC3 只读门**：`ReadOnlyUntilParity`（`ParityReached=false`）下三个写方法均由 `ReadOnlyHostException` 拒绝且 Core 帧零增量；UI 写控件 `IsEnabled=false` 并显示只读原因，读面仍可用。证据：Host 测试断言异常类型与 Core 零请求；App headless 断言禁用态与原因文案。
- [ ] **AC4 回归与门禁**：`apps/desktop-avalonia/scripts/test.ps1` 全绿且 ≥249（当前基线 249/249）；`python -m pytest -q` 0 新增失败（基线 0F/2773P/10S）；`python apps/desktop-avalonia/scripts/extract-command-surface.py --check` PASS（66 命令零漂移）；`check.ps1 -TaskPath` PASS；64-hex sha256 evidence pin；Handoff。证据：logs/trx/summary。
- [ ] **AC5 真机证据**：用 S4 region fixture 的**数据根副本**（`G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1/region-fixture`，region `117094eb…`、revision 3、page `f52f2772…`）启动发布/调试件：工作台选书→选页→真实 region 可见→改类型成功（revision 增）→撤销恢复→重渲染；截图 + host/wire 日志 + DB 前后对照。环境不可得时如实标 `BLOCKED` 并保留 headless + Host 集成证据。证据：screens、wire ndjson、before/after json。

## 实现提示（Lead 提供的既有事实，非强制设计）

- 命令已在 dispatcher 接线：`src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs:389-409`（旧壳签名→Core payload 翻译）；registry minor 见 `Commands/HostCommandRegistry.cs:126,177-197`。
- 契约 DTO：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §5（`SetRegionType`/`ListRegions`/`ListRegionRevisions`/`RestoreRegionRevision`/`RerenderPage`）；RC-4 细节 `doc/contracts/M2-RC4_DOMAIN_COMMANDS.md`。
- 只读门与 reader gate 模式：`HostRuntime.cs:72-128`（CreateBook/CreateChapter 写门）、`:204-236`（SaveReadingProgress + gate）、`:244`（ReadPageImage 资源通道）。
- Host 集成测试模式（真实 frozen sidecar + BOOK-FIXTURE 副本）：`tests/NewManga.Host.Tests/HostReaderProgressIntegrationTests.cs`；fixture 支持类 `HostFixture`/`BookFixture`。
- App headless 测试模式：`tests/NewManga.App.Tests/`（如 `F11HotkeyTests`、`ReaderLibraryTests`）；`FakeHostController` 需同步新增方法。
- 工作台 UI 文件：`Views/ReaderWorkbenchPages.cs` 的 `WorkbenchPage`（左 300/中/右 230 三列）、`ViewModels/WorkbenchViewModel.cs`。
- 事务/并发：写前必须持当前 `revision_no`；并发写由 Core 乐观锁返回 `INPUT_REVISION_CHANGED`（`conflict`），Host 不得猜测 revision。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER、`verification/REGION-WORKBENCH-1/**`、自己的 Handoff、worktree 与 task-env。

## 禁止范围

不改 Python Core 语义（发现缺陷先回报）、不改 Host 协议/冻结契约语义、不改旧壳 Tauri/React、不 push、不 gc/prune、不删除/搬迁 fixture 原件、不对用户真实数据根写操作（只用副本）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2/AC3 | `apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <private>` | Win11 + frozen sidecar | NOT_RUN | planned |
| AC1/AC2/AC3 | Host 集成测试（真实 fixture 副本，含 read-only 分支） | `task-envs/S4-CMD-BATCH-1/region-fixture` 副本 | NOT_RUN | planned |
| AC4 | `python -m pytest -q` | 仓库 venv | NOT_RUN | planned |
| AC4 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | 仓库 | NOT_RUN | planned |
| AC4 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REGION-WORKBENCH-1.md` | 仓库 | NOT_RUN | planned |
| AC5 | 真机：工作台选页→改类型→撤销→重渲染 + 截图/wire | fixture 副本数据根 | NOT_RUN | planned |

## 依赖、风险与阻塞

- 硬依赖：`S4-CMD-BATCH-1`（命令接线，`done`，集成 `0fba83021`）；`READER-LIBRARY-WIRE-1`/`CHAPTER-SELECTOR-1` 已提供读门与选择器先例（`done`）。
- 风险：①region fixture 为仓外 `PRESERVE_REFERENCED` 资源，测试必须复制后写，不得改原件；②core pipe 单请求通道，新增读方法必须与 reader/资源通道共用串行 gate，避免并发交叉；③工作台 UI 改动面较大，需保持既有 headless 测试绿（工作台骨架测试可能断言内存模型行为，必要时按真实数据语义调整并留下说明）；④真机不可得时 AC5 标 BLOCKED，不影响 AC1–AC4 交付。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/REGION-WORKBENCH-1 | PRESERVE_REFERENCED | 原路径 | branch `task/REGION-WORKBENCH-1` @ `8831b4273` | 交付后按 Worktree Safety Inventory 复核 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/REGION-WORKBENCH-1 | PRESERVE_REFERENCED | 原路径 | 待交付时登记 | 证据/数据根副本只写此处 |
| fixture | G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1/region-fixture | PRESERVE_REFERENCED（只读消费，复制后写） | 原路径 | `fixture.json`（`library_db_sha256` 覆盖 db+wal） | 原件零修改 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：交付时更新 STATUS/PLAN/LEDGER。
