---
task_id: REGION-WORKBENCH-1
author: region-workbench-owner
recipient: DeepSeek Harness
base_commit: 8831b4273d48faf4b6fd1e105321e89fdb7427bc
delivery_head: 54118364022588d9dea95ba44d09134a1065dae7
status: in_review
---

# Handoff：REGION-WORKBENCH-1（工作台接真实 region：读 / 改标 / 撤销 / 重渲染 + 只读门）

## 交付结果

- Task：`doc/tasks/REGION-WORKBENCH-1.md`（shared task-1）；Owner `region-workbench-owner` / Reviewer `dsh`。
- Branch / Worktree：`task/REGION-WORKBENCH-1` / `G:/CODEX/New Manga.workspace/worktrees/REGION-WORKBENCH-1`。
- Base：`8831b4273`（Task 卡登记；worktree 起点 `4f1796f17` 释放提交）。
- Delivery head：`54118364022588d9dea95ba44d09134a1065dae7`（实现 + 证据提交；本 Handoff 为紧随其后的文档提交）。
- 实现提交：`ce023a02be85070ad5f041d179feaad33ee7679b`。
- rebase：已 rebase 到 main `a9c4b49ad`（`docs(status): keep STATUS within byte budget for CRLF worktrees`；其前 `46ffadc48`/`d8aadc0de` 亦为纯文档提交）；rebase 只带入文档变化（`git diff fa2294f25… 541183640…` 仅 doc/STATUS、PLAN/LEDGER 与其它 Task 卡，代码树不变）。本 Task 只提交自己的 Task 卡 + Handoff + verification/** + 代码，未改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`。
- 未 push；未改 Python Core 语义、未改 Host 协议/冻结契约语义、未改旧壳 Tauri/React。

| AC | 结论 | 证据（`verification/REGION-WORKBENCH-1/`） |
|---|---|---|
| AC1 读面接线 | **MET** | `host/region-workbench-read-write.json`、`app/ui-load.json`、`logs/wire-probe.json`、`ac5/screens/ac5-01-loaded.png` |
| AC2 写入口 | **MET** | `host/region-workbench-read-write.json`、`host/region-workbench-stale-revision.json`、`app/ui-write.json`、`ac5/screens/ac5-03-retyped.png`、`ac5/screens/ac5-04-restored.png`、`ac5/wire/core-service.ndjson` |
| AC3 只读门 | **MET** | `host/region-workbench-readonly.json`、`app/ui-readonly.json`、`host/wire/region-workbench-readonly-core-service.ndjson` |
| AC4 回归与门禁 | **MET** | `test/summary.json`、`test/results-*.trx`、`logs/test-ps1-console.log`、`logs/pytest.log`、`logs/extract-command-surface.log`、`logs/check-governance.log` |
| AC5 真机证据 | **MET** | `ac5/ac5-run.json`、`ac5/screens/*.png`、`ac5/wire/*.ndjson`、`ac5/db-before-after.json`、`fixture/fixture-audit.json` |

变更路径（全部 `apps/desktop-avalonia/**` + 证据/文档）：

- `src/NewManga.CoreClient/CoreServiceClient.cs`：3 读（`list_chapter_pages` minor 6 / `list_regions` / `list_region_revisions`）+ 3 写（`set_region_type` / `restore_region_revision` / `rerender_page`）强类型方法与 DTO（geometry/page_size/reports/preview 解析）。
- `src/NewManga.Host/HostRuntime.cs`：读/写方法；读共用 `_readerIoGate`，写先过 `RequireWrites()`（typed `ReadOnlyHostException`，请求不达 Core）。
- `src/NewManga.App/Services/IHostController.cs` / `HostController.cs` / `NullHostController.cs` / `RegionWorkbenchContracts.cs`：typed seam 与 `HostViewSnapshot.WritesAllowed`。
- `src/NewManga.App/ViewModels/WorkbenchViewModel.cs`、`src/NewManga.App/Views/ReaderWorkbenchPages.cs`、`Views/MainWindow.axaml.cs`：工作台真实 book→chapter→page→页图→region 覆盖/列表/改标/撤销/重渲染/只读门；修复 S4 骨架三列未 `Grid.SetColumn` 的真实缺陷。
- `tests/NewManga.App.Tests/RegionWorkbenchUiTests.cs`（5 条）、`FakeHostController.cs`；`tests/NewManga.Host.Tests/HostRegionWorkbenchIntegrationTests.cs`（4 条）、`Support/RegionFixture.cs`。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1/AC2/AC3/AC4 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence-test` | Win11 + frozen sidecar copy + 自动播种 fixtures；代码树 `ce023a02b`（rebase 后代码树不变，仅 STATUS 文档变化） | **PASS 258/258 passed, 0 skipped**（coreclient 61 / host 60 / app 137；基线 249 + 新增 9） | `test/summary.json`、`test/results-*.trx`、`logs/test-ps1-console.log`、`test/dotnet-test-Debug.log` |
| AC4 | `python -m pytest -q` | 仓库 Python venv，代码树同上 | **PASS：2773 passed, 10 skipped, 0 failed**（215.48s；与基线 0F/2773P/10S 一致） | `logs/pytest.log` |
| AC4 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | 仓库 | **PASS：66 commands**（resource 3 / workbench 12 / library 8 / settings 33 / region 6 / reader 4），零漂移 | `logs/extract-command-surface.log` |
| AC4 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REGION-WORKBENCH-1.md` | rebase main 后 | **PASS** | `logs/check-governance.log` |
| AC1/AC2/AC3 | Host 集成定向 `dotnet test ... --filter FullyQualifiedName~HostRegionWorkbenchIntegrationTests` | 真实 frozen sidecar + region fixture 副本 | **4/4 passed**（读链+几何、写链 revision、stale guard、只读零 Core 帧、4 读串行） | `host/*.json`、`host/wire/*.ndjson` |
| AC1/AC2/AC3 | App headless `RegionWorkbenchUiTests` | Avalonia headless + Skia | **5/5 passed** | `app/ui-*.json` |
| AC5 | 真机（Debug 桌面件，`--demo-write --page=workbench`，task-env 数据根副本） | frozen sidecar；副本 region `436da52c…`/rev3/page `f52f2772…` | **PASS**：改类型 narration rev4 → 撤销 rev3→rev5(speech, restored) → 重渲染 artifact+preview；截图 + wire + DB 前后 sha256 | `ac5/**` |

AC5 细节：
- 运行命令与逐帧 wire 摘要：`ac5/ac5-run.json`（26 帧；`list_chapter_pages` minor 6、`set_region_type`、`list_region_revisions`、`restore_region_revision(revision_no=3, expected_revision=4)`、`rerender_page` 响应 artifact `e5cc69f3…` / preview `preview-a0ddba96…`）。
- DB 前后：`ac5/db-before-after.json`；`library.db` sha256 `5333a4c5…f2ed` → `8abd39b3…854a`；region `current_revision_id` `1c8bfcbf…` → `c4c3d68e…`；`region_revisions` 3 → 5；geometry bbox `[120,166,960,1328]` 不变。
- fixture 审计（共享 fixture 只读、既有 test.ps1 重播种记录、AC5 只写 task-env 副本）：`fixture/fixture-audit.json`。

## 接收方式

```powershell
git -C "G:\CODEX\New Manga.workspace\worktrees\REGION-WORKBENCH-1" status   # 检查 clean
# 复跑门禁（会由既有 test.ps1 重播种共享 S4 region fixture；属既有行为）
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 `
  -EvidenceDirectory "G:\CODEX\New Manga.workspace\task-envs\REGION-WORKBENCH-1\evidence-rerun"
python -m pytest -q
python apps/desktop-avalonia/scripts/extract-command-surface.py --check
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REGION-WORKBENCH-1.md
```

前置：Win11 + `apps/desktop-avalonia/scripts/prepare-sidecar.ps1`（或既有 frozen sidecar copy）；证据原始产物在 `G:/CODEX/New Manga.workspace/task-envs/REGION-WORKBENCH-1/`。

## 下一任务建议（必填）

无需下一步操作（当前唯一 Active Task 即本 Task；region 新建/删除、译文编辑、锁定、批量、Run 触发等明确不在本 Task 范围，需 DSH 依据 `AD002-FOLLOWUPS-1` 另行释放并冻结范围后才能实施）。

## 风险与遗留

1. **region_id 非稳定**：fixture 每次播种换 region uuid（book/chapter/page id 稳定）；本 Task 全部动态读取，Task 卡登记的 `117094eb…` 仅历史事实。共享 fixture 被既有 `test.ps1` 重复播种，审计已登记；Reviewer 复跑会再次播种。
2. **重渲染预览的像素展示不在范围**：只把 preview `resource_id`/错误显示在状态行；derived preview 像素呈现需新 Task。
3. **页选择器为章内有序页列表**（`list_chapter_pages`），未做多页缩略图导航；右栏缩略图为页标签列表（既有骨架）。
4. **UI 只读门为镜像**：真实拒绝在 Host 层（typed + 零 Core 帧）；UI 依 `WritesAllowed` 禁用。
5. **check-governance.log** 为 rebase 后 gate 运行的过程文件（未 pin，因 pin 自身会改变 checker 的 extras 输出）；路径随交付回报给出。
6. **pytest 2 条 Pillow DeprecationWarning** 为既有，非本 Task 引入。
7. 未 push；STATUS/PLAN/LEDGER 由 DSH 统一更新。
