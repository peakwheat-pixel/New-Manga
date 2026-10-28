---
id: REGION-WORKBENCH-1
title: 工作台接真实 region（读/改标/撤销/重渲染）+ 只读门
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_followups
suggested_owner: region-workbench-owner
owner: region-workbench-owner
reviewer: dsh
depends_on: [S4-CMD-BATCH-1]
base_commit: 8831b4273d48faf4b6fd1e105321e89fdb7427bc
branch: task/REGION-WORKBENCH-1
worktree: G:/CODEX/New Manga.workspace/worktrees/REGION-WORKBENCH-1
integration_commit: 60d08762794a53dce7a6aab951f11d9ba9f97003
delivery_head: 54118364022588d9dea95ba44d09134a1065dae7
canonical_evidence_status: complete
resource_closeout_status: complete
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

> 交付说明：本卡在 `in_review` 时固定 `delivery_head = 541183640`（实现提交 `ce023a02b` + 证据提交 `541183640`；Task 卡与 Handoff 为紧随其后的文档提交）。静态 id 说明见 §「Record Decisions」第 7 条：region fixture 每次 `test.ps1` 重播种会换 region_id，测试/证据一律从 `fixture.json` 动态读取。

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

- [x] **AC1 读面接线**：`CoreServiceClient` 新增 `ListChapterPagesAsync`（wire `list_chapter_pages`，minor 6）、`ListRegionsAsync`（wire `list_regions`）、`ListRegionRevisionsAsync`（wire `list_region_revisions`，minor 3）强类型读；`HostRuntime` 暴露同名读方法并与既有 reader I/O gate 串行（core pipe 严格请求/响应）；`IHostController`/`HostController`/`NullHostController` 同步扩展；工作台通过真实 book→chapter→page 选择加载页图（复用 `ReadPageImageAsync`）与 region 覆盖（`geometry` 归一化 + `page_size` 像素投影，沿 `1.5` additive widening），左侧列表显示真实 region 且与画布选中双向同步。证据：Host 集成测试对真实 fixture 断言 region 投影与几何；App headless 测试断言接线；真机截图。 <<MET>>
- [x] **AC2 写入口**：`HostRuntime` 新增 `SetRegionTypeAsync`/`RestoreRegionRevisionAsync`/`RerenderPageAsync`，**全部先检查 `Policy.WritesAllowed`**（沿 `CreateBookAsync`/`SaveReadingProgressAsync` 模式，typed `ReadOnlyHostException`、请求不达 Core）；工作台提供改类型下拉+应用、撤销上一 revision（需先 `list_region_revisions` 取得上一版）、重渲染本页按钮；写成功后刷新 region 列表/revision 与页图。证据：Host 集成测试真实写入（revision_no 递增、restored revision、rerender 产物/预览）、App headless 测试。 <<MET>>
- [x] **AC3 只读门**：`ReadOnlyUntilParity`（`ParityReached=false`）下三个写方法均由 `ReadOnlyHostException` 拒绝且 Core 帧零增量；UI 写控件 `IsEnabled=false` 并显示只读原因，读面仍可用。证据：Host 测试断言异常类型与 Core 零请求；App headless 断言禁用态与原因文案。 <<MET>>
- [x] **AC4 回归与门禁**：`apps/desktop-avalonia/scripts/test.ps1` 全绿且 ≥249（当前基线 249/249）；`python -m pytest -q` 0 新增失败（基线 0F/2773P/10S）；`python apps/desktop-avalonia/scripts/extract-command-surface.py --check` PASS（66 命令零漂移）；`check.ps1 -TaskPath` PASS；64-hex sha256 evidence pin；Handoff。证据：logs/trx/summary。 <<MET>>
- [x] **AC5 真机证据**：用 S4 region fixture 的**数据根副本**（`G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1/region-fixture`，region `117094eb…`、revision 3、page `f52f2772…`）启动发布/调试件：工作台选书→选页→真实 region 可见→改类型成功（revision 增）→撤销恢复→重渲染；截图 + host/wire 日志 + DB 前后对照。环境不可得时如实标 `BLOCKED` 并保留 headless + Host 集成证据。证据：screens、wire ndjson、before/after json。 <<MET>>

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
| AC1/AC2/AC3 | `apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <private>` | Win11 + frozen sidecar + 自动播种 fixture | **PASS 258/258, 0 skipped**（coreclient 61 / host 60 / app 137；基线 249 + 新增 9） | `verification/REGION-WORKBENCH-1/test/summary.json`、`logs/test-ps1-console.log` |
| AC1/AC2/AC3 | Host 集成测试（真实 frozen sidecar + region fixture 副本，含 read-only 分支） | `task-envs/REGION-WORKBENCH-1/region-fixture-copy`（S4 副本） | **PASS 4/4**：读写全链路、stale guard typed conflict、只读门零 Core 帧、4 路读串行 | `host/region-workbench-*.json`、`host/wire/*.ndjson` |
| AC1/AC2/AC3 | App headless 测试 `RegionWorkbenchUiTests` | Avalonia headless + Skia | **PASS 5/5**：真实链路+几何、双向选中、改标/撤销/重渲染刷新、只读门、MainWindow 导航 | `app/ui-*.json` |
| AC4 | `python -m pytest -q` | 仓库 Python venv | **PASS：2773 passed, 10 skipped, 0 failed**（215.48s；与基线 0F/2773P/10S 一致） | `logs/pytest.log` |
| AC4 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | 仓库 | **PASS：66 commands**，零漂移 | `logs/extract-command-surface.log` |
| AC4 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REGION-WORKBENCH-1.md` | 仓库（rebase main 后） | **PASS**（证据 pin 全部 64-hex 校验通过） | `logs/check-governance.log` |
| AC5 | 真机：工作台选页→改类型→撤销→重渲染 + 截图/wire | task-env 副本数据根 + frozen sidecar | **PASS**：narration rev4 → restore rev5(speech/restored) → rerender(artifact+preview)；截图 6 张 + wire + DB 前后 sha256 | `ac5/**`、`fixture/fixture-audit.json` |

## Record Decisions（交付记录）

1. **`list_chapter_pages` 使用 wire minor 6**：frozen sidecar 实测 minor 3 与 6 均接受（`logs/wire-probe.json`，8 页返回）；按 AC1 契约要求客户端固定 minor 6，既有 dispatcher 绑定（minor 3，S4 已证明）不动，避免无谓改命令面。
2. **读写共用 reader I/O gate**：`HostRuntime` 新增读/写方法全部复用既有 `_readerIoGate`；Host 集成测试并发 4 读验证严格请求/响应不串帧。
3. **只读门在 Host 层，UI 只镜像**：`RequireWrites()` 在 gate/Core 帧之前抛 typed `ReadOnlyHostException`；UI 依 `HostViewSnapshot.WritesAllowed` 禁用控件并显示原因。测试断言拒绝前后 `CoreService.Wire.Count` 不变。
4. **写前持当前 revision**：改类型用 `list_regions` 的 `revision_no` 作 `expected_revision`；撤销先 `list_region_revisions` 取“小于 current 的最大 revision_no”，再以 current 作 guard；stale guard 实测 `INPUT_REVISION_CHANGED/conflict` 且状态不变。
5. **重渲染刷新语义**：`rerender_page` 提交 translated artifact revision，页图仍经 `resolve_page_resource` 读 original；“刷新页图”= 重走资源通道 + 重新 `list_regions`；重渲染结果（artifact/revision/预览 resource_id）显示在状态行。预览像素展示不在范围。
6. **修复 S4 骨架真实缺陷**：原 `WorkbenchPage` 三列未 `Grid.SetColumn`，右栏覆盖左栏；真机首屏截图暴露后已修复并复验。
7. **fixture id 动态口径**：`test.ps1` 每次门禁重播种 `task-envs/S4-CMD-BATCH-1/region-fixture`，region_id 每次新生成（book/chapter/page id 稳定）。本卡登记时的 `117094eb…` 仅作释放时事实；代码/测试/证据一律从副本 `fixture.json` 动态读取，真机 AC5 用 12:29 播种副本（region `436da52c…`）。共享 fixture 仅读、未写；审计见 `verification/REGION-WORKBENCH-1/fixture/fixture-audit.json`。

## 依赖、风险与阻塞

- 硬依赖：`S4-CMD-BATCH-1`（命令接线，`done`，集成 `0fba83021`）；`READER-LIBRARY-WIRE-1`/`CHAPTER-SELECTOR-1` 已提供读门与选择器先例（`done`）。
- 风险：①region fixture 为仓外 `PRESERVE_REFERENCED` 资源，测试必须复制后写，不得改原件；②core pipe 单请求通道，新增读方法必须与 reader/资源通道共用串行 gate，避免并发交叉；③工作台 UI 改动面较大，需保持既有 headless 测试绿（工作台骨架测试可能断言内存模型行为，必要时按真实数据语义调整并留下说明）；④真机不可得时 AC5 标 BLOCKED，不影响 AC1–AC4 交付。

## 交付与运行记录

- Handoff：[REGION-WORKBENCH-1-handoff.md](../handoffs/REGION-WORKBENCH-1-handoff.md)
- Review：尚未（reviewer=`dsh`；Owner 与 Reviewer 不同）。
- 实现提交：`ce023a02be85070ad5f041d179feaad33ee7679b`（feat：CoreClient/HostRuntime/Controller/工作台/测试）。
- 证据提交 / delivery_head：`54118364022588d9dea95ba44d09134a1065dae7`（verification/** + REPORT）。
- 本卡与 Handoff：紧随 delivery head 的文档提交（rebase main 后；仅文档，不改代码/证据内容）。
- 实际测试：`test.ps1` 258/258、`pytest -q` 2773P/10S/0F、`extract-command-surface --check` PASS、`check.ps1 -TaskPath` PASS；真机 AC5 见 `verification/REGION-WORKBENCH-1/ac5/`。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| ac1-host-read-write | AC1/AC2 | verification/REGION-WORKBENCH-1/host/region-workbench-read-write.json | 54118364022588d9dea95ba44d09134a1065dae7 | 78b58b6a12971a35042222afda8bfb34667c82903b796199f5f8594585b20704 | CANONICAL |
| ac1-app-load | AC1 | verification/REGION-WORKBENCH-1/app/ui-load.json | 54118364022588d9dea95ba44d09134a1065dae7 | e0c32d231e8806077e3911a6dfe6751e391374971168843b3d4a1f09a5869bee | CANONICAL |
| ac1-wire-probe | AC1 | verification/REGION-WORKBENCH-1/logs/wire-probe.json | 54118364022588d9dea95ba44d09134a1065dae7 | 4b9f03ac97650849524afbdbd2dcaa81b468a21c16f47d27d1cfbb361d2dc9c6 | CANONICAL |
| ac1-real-loaded-screen | AC1 | verification/REGION-WORKBENCH-1/ac5/screens/ac5-01-loaded.png | 54118364022588d9dea95ba44d09134a1065dae7 | e67975b7f785084ba38d60916287888bbfbd3ea30c37a9ea52d3b9916f92de28 | CANONICAL |
| ac2-app-write | AC2 | verification/REGION-WORKBENCH-1/app/ui-write.json | 54118364022588d9dea95ba44d09134a1065dae7 | 1cb1b78a4604346ca8a3cb7dc624f560cf6d3f83d315943162066d18b4dc37b2 | CANONICAL |
| ac2-stale-guard | AC2 | verification/REGION-WORKBENCH-1/host/region-workbench-stale-revision.json | 54118364022588d9dea95ba44d09134a1065dae7 | b162d1e47cd4a957a04f95dd16786002059b740fbb87f2c81094d1f6f58f8167 | CANONICAL |
| ac2-real-retyped-screen | AC2/AC5 | verification/REGION-WORKBENCH-1/ac5/screens/ac5-03-retyped.png | 54118364022588d9dea95ba44d09134a1065dae7 | ff02e832a7c02695440d0d86a6e1de19ad569b54cf100d42be31be1a71098fde | CANONICAL |
| ac2-real-restored-screen | AC2/AC5 | verification/REGION-WORKBENCH-1/ac5/screens/ac5-04-restored.png | 54118364022588d9dea95ba44d09134a1065dae7 | 2abdd7b28f0cb565ba307560671b8f8ce9813cb071366e07f0b89f950428bf4c | CANONICAL |
| ac2-real-wire | AC2/AC5 | verification/REGION-WORKBENCH-1/ac5/wire/core-service.ndjson | 54118364022588d9dea95ba44d09134a1065dae7 | 257fbdac838755788a8682f83e23e5670164ed0b74a991eeb646123e34b8ce10 | CANONICAL |
| ac2-host-wire | AC2 | verification/REGION-WORKBENCH-1/host/wire/region-workbench-core-service.ndjson | 54118364022588d9dea95ba44d09134a1065dae7 | 98a29a0c855ffa7bfa0d15afafc1f84ac762ef74c3e1863c58f61c7a37c77c87 | CANONICAL |
| ac1-host-log | AC1/AC2 | verification/REGION-WORKBENCH-1/host/wire/region-workbench-host.log | 54118364022588d9dea95ba44d09134a1065dae7 | b9ecfe8a300a810eed4d0f1a3f92711bf140a9f224796442a802abaa4fe29208 | CANONICAL |
| ac3-host-readonly | AC3 | verification/REGION-WORKBENCH-1/host/region-workbench-readonly.json | 54118364022588d9dea95ba44d09134a1065dae7 | fa0e28c8a0b9a7b520d74bfb7e20fe64c7eba96a1672a666753b51c399a65a32 | CANONICAL |
| ac3-app-readonly | AC3 | verification/REGION-WORKBENCH-1/app/ui-readonly.json | 54118364022588d9dea95ba44d09134a1065dae7 | 5387cd47207ee11d843984b5bf2d9e3c41ce26eacecf25793005cc34230aa52c | CANONICAL |
| ac3-readonly-wire | AC3 | verification/REGION-WORKBENCH-1/host/wire/region-workbench-readonly-core-service.ndjson | 54118364022588d9dea95ba44d09134a1065dae7 | 53d405ccb03cc2d005f6781aef10dabfa3cf354e25254160154e18f15a264752 | CANONICAL |
| ac3-readonly-log | AC3 | verification/REGION-WORKBENCH-1/host/wire/region-workbench-readonly-host.log | 54118364022588d9dea95ba44d09134a1065dae7 | bb5218c35d97ab9c87aa2ddaf3844483ecc74f5142cf524d573dd8eca71a5cce | CANONICAL |
| ac4-test-summary | AC4 | verification/REGION-WORKBENCH-1/test/summary.json | 54118364022588d9dea95ba44d09134a1065dae7 | a58325bc31a9256a97830063feee8bffa7fc439e1fec1d170184662fd53f06e5 | CANONICAL |
| ac4-test-console-log | AC4 | verification/REGION-WORKBENCH-1/logs/test-ps1-console.log | 54118364022588d9dea95ba44d09134a1065dae7 | 71c1c857f9531168f81e54e7f12527145d51613a7747d372df7e2879eedc4d9d | CANONICAL |
| ac4-trx-coreclient | AC4 | verification/REGION-WORKBENCH-1/test/results-coreclient.trx | 54118364022588d9dea95ba44d09134a1065dae7 | 542fb86e52dcaf1d489ffc547031ab0715fd2291a34976c9f2039e7615d96010 | CANONICAL |
| ac4-trx-host | AC4 | verification/REGION-WORKBENCH-1/test/results-host.trx | 54118364022588d9dea95ba44d09134a1065dae7 | 4e3cadf550b0bf4b2e83a762ba2230a2c20903b8f337ba6fc88e855075e7d8dc | CANONICAL |
| ac4-trx-app | AC4 | verification/REGION-WORKBENCH-1/test/results-app.trx | 54118364022588d9dea95ba44d09134a1065dae7 | f51a49154c889ed269417271b16ced55ca6a2111fa9359bd00e27742d25591e4 | CANONICAL |
| ac4-dotnet-test-log | AC4 | verification/REGION-WORKBENCH-1/test/dotnet-test-Debug.log | 54118364022588d9dea95ba44d09134a1065dae7 | e29d24b93272eaf257d8807ac562910982383d7345352be38ab7e09eb2a6b9bc | CANONICAL |
| ac4-pytest | AC4 | verification/REGION-WORKBENCH-1/logs/pytest.log | 54118364022588d9dea95ba44d09134a1065dae7 | 62ac6f1d5b953a3dd32e58c6d3588e826e4f9c7add4f61b33aace620a9a62274 | CANONICAL |
| ac4-command-surface | AC4 | verification/REGION-WORKBENCH-1/logs/extract-command-surface.log | 54118364022588d9dea95ba44d09134a1065dae7 | 564676d393ad475f6924d84dce57281e51ba6ae22d4f7984379030a8e05dfda1 | CANONICAL |
| ac5-run | AC5 | verification/REGION-WORKBENCH-1/ac5/ac5-run.json | 54118364022588d9dea95ba44d09134a1065dae7 | deaa0d3a1641b35335144b4e67f891db0f5f3a1f7c466129d2afe57b70861ab7 | CANONICAL |
| ac5-db-before-after | AC5 | verification/REGION-WORKBENCH-1/ac5/db-before-after.json | 54118364022588d9dea95ba44d09134a1065dae7 | 97f92434cc424d493135a1fafde21e4d11c15ec049350ef16091d7b62ba03285 | CANONICAL |
| ac5-fixture-audit | AC5 | verification/REGION-WORKBENCH-1/fixture/fixture-audit.json | 54118364022588d9dea95ba44d09134a1065dae7 | f0305ea377e3e3537011eadc2be8d0fd500f4e239f654c71ffee16d882e5b776 | CANONICAL |
| ac5-type-selected-screen | AC5 | verification/REGION-WORKBENCH-1/ac5/screens/ac5-02-type-selected.png | 54118364022588d9dea95ba44d09134a1065dae7 | a7b2111e96554f2c612b4b276feb2d9737b501fb7128969db9d2100bfdba5132 | CANONICAL |
| ac5-rerendered-screen | AC5 | verification/REGION-WORKBENCH-1/ac5/screens/ac5-05-rerendered.png | 54118364022588d9dea95ba44d09134a1065dae7 | e97edfca4a23858a5c4ea2d42f49fb71315b961ea0b5d64f734d783a8d82ac6c | CANONICAL |
| ac5-host-bridge-wire | AC5 | verification/REGION-WORKBENCH-1/ac5/wire/host-bridge.ndjson | 54118364022588d9dea95ba44d09134a1065dae7 | 05b92b347647c21ceb2d43416993cb6672dbb2ee9d8ef50d3d90f03c65d035c1 | CANONICAL |
| delivery-report | 交付报告 | verification/REGION-WORKBENCH-1/REPORT.md | 54118364022588d9dea95ba44d09134a1065dae7 | 6e8467a9fd3c63705d4b4fb9379c4bad807b2c7d57b8a5ab1fb3ce9303f20067 | CANONICAL |
| ac4-check-governance-log | AC4 | verification/REGION-WORKBENCH-1/logs/check-governance.log | f47cadc54c15032b36df6401a1b0fa042b441707 | 26c1b0a27a5c8062ace07f92bc62dbdd9ecc5f603d0398aadb1b89c37d068bb4 | SOURCE_PIN |
| resource-manifest | Closeout | verification/REGION-WORKBENCH-1/resource-manifest.json | - | 32ebe37487bd1a520a3b874874a90afffc42bec698bd139480593954b69970c2 | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/REGION-WORKBENCH-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/REGION-WORKBENCH-1 | verification/REGION-WORKBENCH-1/resource-manifest.json | 交付后按 Worktree Safety Inventory 复核；未 push；已 merge 到 main `60d087627` |
| task-env | G:/CODEX/New Manga.workspace/task-envs/REGION-WORKBENCH-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/REGION-WORKBENCH-1 | 8abd39b3689f6fb413c9c615de8aec1b95c3d570a7b7927120f709222319485a | 证据/数据根副本只写此处；AC5 后 `region-fixture-copy/library.db` 指纹（目录资源，hash 供复核） |
| fixture | G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1/region-fixture | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1/region-fixture | 90ade2a84ab13650eff6ee3f97bca08eded54720c34fe5334d40f63914e27cd7 | 共享 fixture 本任务只读；重播种由既有 `test.ps1` 执行，审计见 `verification/REGION-WORKBENCH-1/fixture/fixture-audit.json` |
| upstream fixture | G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/isolated-data | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/isolated-data | 6e6e10f73f0c28534fc2083a7c809b4829aea91f208024126c26dbb62b8b74f5 | `library.db` 指纹（目录资源，hash 供复核）；仅经既有 seed 脚本间接读取，未写 |

## Closeout Record

- Closeout date / DSH：2026-10-28（集成 `60d087627`；DSH 独立复核 PASS）。
- canonical_evidence_status：`complete`（29 条 CANONICAL + 1 条 SOURCE_PIN；worktree/blob 双 basis 校验通过）。
- resource_closeout_status：`complete`（worktree/task-env/fixture 均 `PRESERVE_REFERENCED`；未删除/迁移/归档）。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项及保留原因：① region_id 每次播种非稳定（代码/测试/证据动态读取）；② rerender 预览像素展示不在首切片范围；③ 页选择器无多页缩略图导航；④ pytest 2 条 Pillow DeprecationWarning 为既有。均记录不阻塞。
- 当前指针清理：STATUS/PLAN/LEDGER 已更新。

## Review（DSH 独立复核，2026-10-28）— PASS

- 独立复跑（Owner worktree `b3331cdab`，隔离 evidence 目录，不复用 Owner 的 evidence）：`scripts/test.ps1` → **TEST PASS 258/258, 0 skipped**（coreclient 61 / host 60 / app 137）；`python -m pytest -q` → **2773 passed, 10 skipped, 0 failed**（205.41s）；`extract-command-surface.py --check` → **PASS（66 commands）**；`check.ps1 -TaskPath` → **PASS（3 非阻断 warning）**。
- 证据：29 条 CANONICAL + 1 条 SOURCE_PIN 全部校验通过（worktree 字节或 commit blob 双 basis）；`verification/REGION-WORKBENCH-1/` 31 个文件全部登记（补登 `logs/check-governance.log`）。
- 代码复查：`HostRuntime` 三个写方法均先 `RequireWrites()`（在 gate/Core 帧之前）→ typed `ReadOnlyHostException`；读写共用 `_readerIoGate`；`CoreServiceClient` 以 `ChapterPagesMinor = 6` 固定 wire minor、payload 键与契约一致；Host 集成测试真实 frozen sidecar（几何 0.1→120px@1200×1660、revision 递增、stale guard `INPUT_REVISION_CHANGED` 且状态不变、只读三写零 Core 帧、读面仍可用）；App headless 断言真实接线/双向选中/只读禁用+原因；未发现伪造或 mock Core 语义。
- 真机 AC5：task-env 副本数据根（region `436da52c…`、rev3、page `f52f2772…`）改类型 narration rev4 → 撤销 rev5 speech/restored → 重渲染 artifact+preview；6 张截图 + core/host wire + DB 前后 sha256；共享 S4 fixture 只读审计见 `fixture/fixture-audit.json`。
- 集成：`git merge --no-ff` → `60d08762794a53dce7a6aab951f11d9ba9f97003`。
- 结论：AC1–AC5 MET，PASS；标 `done`。
