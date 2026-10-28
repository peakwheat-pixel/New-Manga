# REGION-WORKBENCH-1 实施报告（工作台接真实 region：读 / 改标 / 撤销 / 重渲染 + 只读门）

- Task：`doc/tasks/REGION-WORKBENCH-1.md`（shared task-1，Owner `region-workbench-owner`，Reviewer `dsh`）
- Branch / Worktree：`task/REGION-WORKBENCH-1` / `G:/CODEX/New Manga.workspace/worktrees/REGION-WORKBENCH-1`
- Base：`4f1796f17`（Task 卡释放提交；其父 `8831b4273` 为任务卡登记 base）
- 实现提交：`b03cecfc4`（feat：CoreClient/HostRuntime/Controller/工作台/测试）
- 证据提交：本目录所在提交（`test(workbench): REGION-WORKBENCH-1 ...`；Handoff 记录 delivery head）
- 未 push；未改 Python Core、未改旧壳 Tauri/React、未改冻结契约语义、未改 Host 协议语义。

## 1. 交付摘要

| AC | 结论 | 关键证据 |
|---|---|---|
| AC1 读面接线 | **MET** | `CoreServiceClient` 新增 `ListChapterPagesAsync`（wire minor 6）/`ListRegionsAsync`/`ListRegionRevisionsAsync`；`HostRuntime` 同名读方法共用既有 `_readerIoGate`；工作台 book→chapter→page 真实加载（`list_books`→`list_chapters`→`list_chapter_pages`→`resolve_page_resource` 页图→`list_regions`），左列 region 列表/画布覆盖框与选中双向同步；几何按 `geometry.bbox × page_size` 投影为页面像素（fixture: 0.1/0.1/0.8/0.8 → 120/166/960/1328 @1200×1660）。证据：`host/region-workbench-read-write.json`、`app/ui-load.json`、`logs/wire-probe.json`、`ac5/screens/ac5-01-loaded.png` |
| AC2 写入口 | **MET** | `HostRuntime.SetRegionTypeAsync`/`RestoreRegionRevisionAsync`/`RerenderPageAsync` 全部先检查 `Policy.WritesAllowed`（typed `ReadOnlyHostException`，请求不达 Core，见 AC3）；工作台类型下拉+应用、撤销到上一 revision（先 `list_region_revisions` 取 current-1）、重渲染本页；写成功后刷新 region/revision/页图。真实写入：retype rev3→4、restore rev3→rev5、rerender artifact+preview；乐观锁 stale guard 返回 typed `INPUT_REVISION_CHANGED`。证据：`host/region-workbench-read-write.json`、`host/region-workbench-stale-revision.json`、`app/ui-write.json`、`ac5/*` |
| AC3 只读门 | **MET** | `ReadOnlyUntilParity` 下三个写方法均抛 `ReadOnlyHostException("HOST_READ_ONLY")` 且 Core 帧数零增量（读面仍可用）；UI 写控件 `IsEnabled=false`、只读原因横幅可见，读面 region/页图正常加载。证据：`host/region-workbench-readonly.json`、`app/ui-readonly.json`、`host/wire/region-workbench-readonly-core-service.ndjson` |
| AC4 回归与门禁 | **MET** | `test.ps1` **258/258 passed / 0 skipped**（coreclient 61 + host 60 + app 137；基线 249 + 本 Task 新 9）；`pytest -q` **2773 passed / 10 skipped / 0 failed**（与基线 0F/2773P/10S 一致）；`extract-command-surface.py --check` PASS（66 命令零漂移）；`check.ps1 -TaskPath` PASS（日志见 `logs/check-governance.log`）。证据：`test/summary.json`、`test/results-*.trx`、`logs/test-ps1-console.log`、`logs/pytest.log`、`logs/extract-command-surface.log` |
| AC5 真机证据 | **MET** | 在 `task-env/REGION-WORKBENCH-1/region-fixture-copy`（S4 fixture 的 durable 副本）上启动 Debug 桌面件（`--demo-write --page=workbench`）：真实页图+region 覆盖可见 → 改类型 narration(rev4) → 撤销 rev3→rev5(speech, origin=restored) → 重渲染（artifact+preview）→ 正常关闭；截图 6 张 + host/core wire ndjson + DB 前后 sha256/行级对照。证据：`ac5/` |

## 2. 代码改动

| 文件 | 改动 |
|---|---|
| `src/NewManga.CoreClient/CoreServiceClient.cs` | 新增 3 个强类型读方法（`ListChapterPagesAsync` minor 6、`ListRegionsAsync`、`ListRegionRevisionsAsync`）与 3 个写方法（`SetRegionTypeAsync`/`RestoreRegionRevisionAsync`/`RerenderPageAsync`），以及 `ChapterPageSummary`/`RegionSummary`/`RegionGeometrySummary`/`RegionPageProjection`/`RegionRevisionHistory`/`RegionWriteSnapshot`/`PageRerenderResult` 等 DTO；`list_regions` 的 `geometry.bbox/polygon` 与 `page_size` 可选字段解析（缺失不伪造），`rerender_page` 的 reports/preview/preview_error 投影 |
| `src/NewManga.Host/HostRuntime.cs` | 新增读方法 `ListChapterPagesAsync`/`ListRegionsAsync`/`ListRegionRevisionsAsync`（全部走既有 `_readerIoGate` 串行 Core pipe）；新增写方法 `SetRegionTypeAsync`/`RestoreRegionRevisionAsync`/`RerenderPageAsync`，统一 `RequireWrites()` 在 gate 之前做 typed 只读拒绝 |
| `src/NewManga.App/Services/IHostController.cs` | `HostViewSnapshot.WritesAllowed`（UI 只读门数据源）；新增 7 个工作台 seam：3 读 + 页图读取 + 3 写，全部 typed 结果/空值降级，不向 UI 抛异常 |
| `src/NewManga.App/Services/RegionWorkbenchContracts.cs` | 新增 `RegionOperationResult`/`PageRerenderOutcome`（Success/NotReady/ReadOnly/Failed）typed 结果 |
| `src/NewManga.App/Services/HostController.cs` | 实现上述 seam：读面失败降级 empty/null；写面 `ReadOnlyHostException→ReadOnly`、`CoreOperationException→Failed(code)`；`UpdateFromRuntime` 写入 `WritesAllowed` |
| `src/NewManga.App/Services/NullHostController.cs` | 设计时/无 Host 实现：读 empty/null，写 NotReady |
| `src/NewManga.App/ViewModels/WorkbenchViewModel.cs` | `RegionItem` 扩展真实字段（region_id/type/origin/revision/sfx/页面像素矩形/Label），`ReplaceRegions`/`SelectRegionById`/`SelectedRegionDetail`；保留 S4 骨架内存模型方法与既有 UX 断言 |
| `src/NewManga.App/Views/ReaderWorkbenchPages.cs` | `WorkbenchPage` 重写：真实 book/chapter/page 选择器、页图（Host 资源通道，无插值）、region 覆盖框（归一化×page_size×zoom）、左侧真实 region 列表与画布双向选中、类型下拉+应用/撤销上一 revision/重渲染本页、状态行与只读横幅；**修复 S4 骨架三列未 `Grid.SetColumn` 导致右栏覆盖左栏的真实 UI 缺陷** |
| `src/NewManga.App/Views/MainWindow.axaml.cs` | 进入工作台 / Host 就绪后（`--page=workbench` 启动场景）触发 `Workbench.EnsureLoadedAsync()` |
| `tests/NewManga.App.Tests/FakeHostController.cs` | 新增脚本化 region 数据（页列表/regions/revisions/页图）、写调用记录与消息队列；内存中模拟 Core 乐观提交语义（每次成功写 revision+1、restore 追加新 revision）；`ReadOnlySnapshot()` |
| `tests/NewManga.App.Tests/RegionWorkbenchUiTests.cs` | 新增 5 条 headless 测试：真实链路加载+几何投影、列表/画布双向选中、改标+撤销+重渲染刷新、只读门禁用+理由+零写调用、MainWindow 导航加载 |
| `tests/NewManga.Host.Tests/HostRegionWorkbenchIntegrationTests.cs` | 新增 4 条真实 frozen sidecar 集成测试：读写全链路（含几何/页图/revision 历史）、stale revision typed conflict、只读门 typed 拒绝+零 Core 帧、4 路读串行不串帧 |
| `tests/NewManga.Host.Tests/Support/RegionFixture.cs` | region fixture 定位/`fixture.json` 动态元数据读取/durable state 复制到一次性 data root/DB sha256 辅助 |

## 3. 关键决策（Record Decision）

1. **`list_chapter_pages` 发送 minor 6**：AC1 要求该命令 wire minor 6（契约 M2-C1 rev 1.8 引入版本）。用真实 frozen sidecar 实测（`logs/wire-probe.json`）：minor 3 与 6 均被接受且返回 8 页；因此 `CoreServiceClient.ListChapterPagesAsync` 固定 minor 6，既有 dispatcher 绑定（minor 3，S4 已证明）保持不动，避免无谓改动命令面。
2. **读面与写面都串行核心 pipe**：新增读/写方法全部复用 HostRuntime 既有 `_readerIoGate`；Host 集成测试并发 4 读验证响应不串帧（`lastFour` 帧命令集合断言）。
3. **只读门在 Host 层，UI 只镜像**：`RequireWrites()` 在任何 gate/Core 帧之前抛 `ReadOnlyHostException`；UI 不直接持有 dispatcher，只依据 `HostViewSnapshot.WritesAllowed` 禁用控件并显示原因。真实测试断言拒绝前后 `CoreService.Wire.Count` 不变。
4. **写前必须持当前 revision**：改类型使用 `list_regions` 行的 `revision_no` 作为 `expected_revision`；撤销先 `list_region_revisions` 取“小于 current 的最大 revision_no”再以 current 作为 guard。stale guard 实测 `INPUT_REVISION_CHANGED/conflict` 且 region 状态不变。
5. **重渲染后的刷新语义**：`rerender_page` 提交的是 translated artifact revision（不是 page original），页图仍经 `resolve_page_resource` 读 original；因此“刷新页图”= 重新走资源通道+重新 `list_regions`（原图字节不变），重渲染结果（artifact/revision/预览 resource_id）在状态行显示。翻译预览的像素展示不在本 Task 范围。
6. **工作台选择链**：书来自 Host 快照（`RefreshBooksAsync` 后 Snapshot.Books），章来自 `list_chapters`，页来自 `list_chapter_pages`（按 sort_order 排序），页图/region 来自 Host 读面；无 Host/设计时保留占位画布，不伪造数据。
7. **fixture id 动态读取**：`test.ps1` 每次门禁都重播种 `task-envs/S4-CMD-BATCH-1/region-fixture`，region_id 每次新生成（book/chapter/page id 稳定）。所有测试与真机 AC5 均从副本 `fixture.json` 动态读取 id；Task 卡登记时的静态 region id 仅作历史事实。审计见 `fixture/fixture-audit.json`。
8. **修复 S4 骨架真实缺陷**：原 WorkbenchPage 三个栏位未设置 `Grid.SetColumn`，右栏（缩略图/气泡检查器）盖住左栏；真机 AC5 首次截图暴露该问题，已显式分列并复验。

## 4. 测试命令与结果

| # | 命令/步骤 | 环境 | 结果 | 证据 |
|---|---|---|---|---|
| 1 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <task-env>/evidence-test` | Win11 + frozen sidecar copy + 自动播种 S4/reader fixtures | **PASS：258/258 passed, 0 skipped**（coreclient 61 / host 60 / app 137） | `test/summary.json`、`test/results-*.trx`、`logs/test-ps1-console.log`、`test/dotnet-test-Debug.log` |
| 2 | `python -m pytest -q`（worktree 根） | 仓库 venv/Python 3.14 | **PASS：2773 passed, 10 skipped, 0 failed**（215.48s），与基线 0F/2773P/10S 一致 | `logs/pytest.log` |
| 3 | `python apps/desktop-avalonia/scripts/extract-command-surface.py --check` | 仓库 | **PASS：66 commands**，域计数 resource 3 / workbench 12 / library 8 / settings 33 / region 6 / reader 4，快照零漂移 | `logs/extract-command-surface.log` |
| 4 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REGION-WORKBENCH-1.md` | 仓库 | **PASS**（交付卡入 in_review 后运行；见日志） | `logs/check-governance.log` |
| 5 | Host 集成定向：`dotnet test tests/NewManga.Host.Tests --filter FullyQualifiedName~HostRegionWorkbenchIntegrationTests` | frozen sidecar + region fixture 副本 | 4/4 passed（读链/写链/stale/只读零帧/串行） | `host/*.json`、`host/wire/*.ndjson` |
| 6 | App headless 定向：`RegionWorkbenchUiTests` | Avalonia headless + Skia | 5/5 passed | `app/*.json` |
| 7 | 真机 AC5（见 §5） | Debug 桌面件 + frozen sidecar + fixture 副本 | PASS（UI 读/写/撤销/重渲染 + 正常退出） | `ac5/**` |

## 5. AC5 真机步骤与证据

1. 复制数据根：`S4-CMD-BATCH-1/region-fixture` 的 durable state（`library.db` + `managed/` + `fixture.json`）→ `G:/CODEX/New Manga.workspace/task-envs/REGION-WORKBENCH-1/region-fixture-copy`（只写副本）。本次副本取的播种：region `436da52c…`、revision 3、page `f52f2772…`。
2. 启动命令（窗口实际 1280×820，MainWindow.axaml 默认尺寸；`--page=workbench` 触发启动后自动加载）：
   ```
   NewManga.App.exe --data-root="<task-env>/region-fixture-copy" --demo-write
     --sidecar-dir="G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy"
     --log-dir="<task-env>/ac5-logs" --mutex-name=Local\REGION-WORKBENCH-1-AC5
     --legacy-shell-check=off --page=workbench
   ```
3. 实测 UI 流程（窗口截图见 `ac5/screens/`）：
   - 自动加载：书 `BOOK-FIXTURE-1 日漫_JA 测试书` / 章 `第 1 章` / 页 `1 · …E04P02.jpg`；页图可见；状态 `已加载 1 个 region · 页 1200×1660`；region 行 `speech · user · rev 3`；覆盖框位于页面像素 (120,166)-(1080,1494)（`ac5-01-loaded.png`）。
   - 类型下拉 `speech → narration`（`ac5-02-type-selected.png`），点「应用类型」→ 状态 `类型已更新为 narration（revision 4）`，列表刷新为 `narration · user · rev 4`（`ac5-03-retyped.png`）。
   - 点「撤销到上一 revision」→ 状态 `已恢复 revision 3 → revision 5（speech）`，列表 `speech · restored · rev 5`（`ac5-04-restored.png`；origin=restored 证明 Core 追加了新 revision）。
   - 点「重渲染本页」→ 状态 `已重渲染 revision 1（1 区域，预览已发布）`（`ac5-05-rerendered.png` / `ac5-06-final.png`）；wire 响应含 `artifact_id=e5cc69f3…`、`reports[{region 436da52c…, status=rendered, font_substituted=true}]`、`preview.resource_id=preview-a0ddba96…`。
   - Alt+F4 正常关闭（SQLite checkpoint 落盘）。
4. wire 证据：`ac5/wire/core-service.ndjson`（26 帧，关键序列 req-7 `list_chapter_pages` minor 6 → req-8 `resolve_page_resource` → req-9 `list_regions` → req-17 `set_region_type` → req-19 `list_regions` → req-20 `list_region_revisions` → req-21 `restore_region_revision(revision_no=3, expected_revision=4)` → req-24 `rerender_page` → req-25/26 刷新）；`ac5/wire/host-bridge.ndjson` 对应资源 grant。逐帧摘要见 `ac5/ac5-run.json`。
5. DB 前后对照：`ac5/db-before-after.json`（before 来自 12:29 播种的 pristine 副本，after 来自 AC5 副本）：
   - `library.db` sha256：`5333a4c5…f2ed` → `8abd39b3…854a`（WAL checkpoint 后单文件；before 的 WAL 为空）。
   - region 行：同一 `436da52c…`；`region_type` speech→speech（中途 narration）、`current_revision_id` `1c8bfcbf…` → `c4c3d68e…`、`updated_at` 更新；`region_revisions` 3 → 5 行（seed 3 + retype + restore）；geometry bbox `[120,166,960,1328]` 不变。
6. 共享 fixture 审计：见 `fixture/fixture-audit.json`。摘要：共享 `task-envs/S4-CMD-BATCH-1/region-fixture` 是派生 fixture，被既有 `scripts/test.ps1` 每次门禁重播种（region_id 每次变；book/chapter/page id 稳定）；本 Task 只读共享原件并复制 durable state 到自己的 task-env 再写，未直接写共享路径；`BOOK-FIXTURE-1` 上游只读。

## 6. 风险与遗留

1. **region_id 非稳定**：fixture 播种使用新 uuid，Task 卡登记值（117094eb…）与任何后续播种都不同；已全部改为动态读取口径。若 Reviewer 复跑 `test.ps1` 会再次重播种（属既有行为，非本 Task 引入）。
2. **重渲染预览不显示像素**：本 Task 只把 preview `resource_id`/错误投影到状态行；derived preview 像素展示（grant 到 derived read-only）不在冻结范围。
3. **未包含写能力**：新建/删除 region、译文编辑、锁定/取消锁定、批量、Run 触发均明确不在范围，UI 未提供入口。
4. **页选择器**：按契约使用章内有序页列表（`list_chapter_pages`），未做多页缩略图导航；右栏缩略图目前是页标签列表（既有骨架）。
5. **Avalonia 控件像素点击**：真机证据用 UIA/坐标驱动，非产品能力；不影响交付语义。
6. **pytest 有 2 条 Pillow DeprecationWarning**（既有，非本 Task 引入）。
7. **STATUS/PLAN/LEDGER 指针**：由 DSH 在 Review/集成阶段更新（Owner 未改）。
8. 既有骨架测试语义：`WorkbenchViewModel` 的内存 `AddRegion/Delete/Move/Resize` 方法保留（S4 模型测试）；真实工作台不再提供“添加/删除区域”入口，符合范围冻结。

## 7. 复现方式

```powershell
# 1) 全部门禁（自动播种 fixture；会重播种共享 S4 region fixture）
cd "G:\CODEX\New Manga.workspace\worktrees\REGION-WORKBENCH-1"
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 `
  -EvidenceDirectory "G:\CODEX\New Manga.workspace\task-envs\REGION-WORKBENCH-1\evidence-rerun"

# 2) Python 回归
python -m pytest -q

# 3) 命令面
python apps/desktop-avalonia/scripts/extract-command-surface.py --check

# 4) 治理指针/证据 pin
pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/REGION-WORKBENCH-1.md

# 5) 真机（先把 S4 region fixture 的 durable state 复制到自己的 task-env）
NewManga.App.exe --data-root="<copy>" --demo-write --sidecar-dir="<sidecar-copy>" `
  --log-dir="<logs>" --mutex-name=Local\REGION-WORKBENCH-1-AC5 --legacy-shell-check=off --page=workbench
```

## 8. 证据索引（`verification/REGION-WORKBENCH-1/`）

| 路径 | 内容 |
|---|---|
| `ac5/ac5-run.json` | AC5 真机运行元数据 + 26 帧 core wire 逐帧摘要（命令/minor/payload/结果摘要） |
| `ac5/screens/*.png` | 6 张真机窗口截图（加载/选类型/改标完成/撤销完成/重渲染/最终） |
| `ac5/wire/*.ndjson` | 真机 core_service / host_bridge wire 原始帧 |
| `ac5/db-before-after.json` | SQLite `regions`/`region_revisions` 等行级 before/after + 文件 sha256 |
| `fixture/fixture-audit.json` | 共享 fixture 被既有脚本重播种的审计 + 本 Task 副本读写边界 |
| `host/region-workbench-*.json` | Host 集成证据（读写链、stale guard、只读门零 Core 帧） |
| `host/wire/*.ndjson`、`host/wire/*.log` | Host 集成测试的真实 wire/host 日志 |
| `app/ui-*.json` | App headless 证据（真实链路/写/只读门） |
| `logs/wire-probe.json` | frozen sidecar 对 `list_chapter_pages` minor 3/6 与 region 读面形状的探测 |
| `logs/test-ps1-console.log` | `test.ps1` 全量门禁控制台日志（含 build、播种、命令面 --check、3 项目测试、summary） |
| `logs/pytest.log` | `pytest -q` 全量输出与最终计数 |
| `logs/extract-command-surface.log` | 命令面 `--check` PASS 日志 |
| `logs/check-governance.log` | `check.ps1 -TaskPath` 输出 |
| `test/summary.json`、`test/results-*.trx`、`test/dotnet-test-Debug.log` | dotnet 测试汇总/逐项目 TRX/测试日志 |
