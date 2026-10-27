# S4-CMD-BATCH-1 — 6 条命令接线（region 写 4 + reader 2）交付报告

| 项 | 值 |
| --- | --- |
| Task | `doc/tasks/S4-CMD-BATCH-1.md` |
| Owner | `route-research` |
| Branch / Worktree | `task/S4-CMD-BATCH-1` / `G:/CODEX/New Manga.workspace/worktrees/S4-CMD-BATCH-1` |
| Base commit | `171529b5d` |
| Scope | C# Avalonia Host `NewManga.CoreClient` registry / dispatcher / domain services；本报告与证据 |
| 结果 | 5 条由 NOT_SUPPORTED → IMPLEMENTED；第 6 条 `library_get_reader_projection` 在 base 已由 NS-WIRE-A1 实现，本轮补真实 chapter 成功复验 |
| 冻结 sidecar | `G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy`（AC11 仓外未标注副本） |

## AC1 — 逐命令契约表

完整 6 条（name / legacy 参数 / Core route / payload / result / wire error / before→after）见
[`command-list.json`](command-list.json)。摘要：

| # | command | 家族 | legacy 参数 | Core route（minor 3） | 结果 |
| --- | --- | --- | --- | --- | --- |
| 1 | `set_region_type` | region 写 | `region_id: String, new_region_type: String, expected_revision?: i64` | `set_region_type` | NOT_SUPPORTED → IMPLEMENTED |
| 2 | `restore_region_revision` | region 写 | `region_id: String, revision_no: i64, expected_revision: i64` | `restore_region_revision` | NOT_SUPPORTED → IMPLEMENTED |
| 3 | `rerender_page` | region 写 | `page_id: String` | `rerender_page` | NOT_SUPPORTED → IMPLEMENTED |
| 4 | `resolve_page_resource` | region 写（资源键） | `page_id: String` | `resolve_page_resource` | NOT_SUPPORTED → IMPLEMENTED |
| 5 | `library_save_reading_progress` | reader 写 | `chapter_id, mode, page_id: String, scroll_offset_y?: f64, elapsed_seconds_delta?: f64` | `SaveReadingProgress` | NOT_SUPPORTED → IMPLEMENTED |
| 6 | `library_get_reader_projection` | reader 读 | `chapter_id, mode, start_position: String` | `GetReaderProjection` | base 已 IMPLEMENTED（NS-WIRE-A1），本轮真实 chapter 复验 |

实现位置：

- `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandRegistry.cs`：新增 5 条 `CoreBindings`（`set_region_type` / `restore_region_revision` / `rerender_page` / `resolve_page_resource` / `SaveReadingProgress`，envelope minor 均为 3），并从 `CoreRoute` NS 原因表移出这 5 条；`list_region_revisions`（读，非本批）仍保持显式 NOT_SUPPORTED。
- `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs`：在 `WriteCorePayload` 中按 legacy Tauri 签名做 Host 边界校验并构造精确 Core payload（含 `RequireInt64` / `WriteOptionalInt64` / `WriteOptionalDouble`）；未知命令保持原透传。
- `apps/desktop-avalonia/src/NewManga.App/Shell/ReaderWorkbenchSupport.cs`：`S4Wiring.WiredImplemented` 14→19，`NsBatch` 9→4（仅剩 Run/Export 4 条 S4-C）；`VerifyAgainstRegistry()` 仍为空。

## AC2 — 对冻结 sidecar 的真实执行断言

fixture：`apps/desktop-avalonia/scripts/seed_s4_region_fixture.py`（生产 assembly + 生产导入/编辑/artifact 用例，reuse BOOK-FIXTURE 的 book/chapter/8 pages，追加 1 个 CLEAN artifact + 1 个 confirm 翻译区域；`scripts/test.ps1` 自动播种并导出 `NEWMANGA_S4_REGION_FIXTURE`）。测试
`S4RegionReaderCommandTests` 只在 durable state 副本上执行，不污染 fixture。

证据 [`commands/s4-region-reader-results.json`](commands/s4-region-reader-results.json)（`all_ok: true`，7/7）：

| 执行 | 结果 |
| --- | --- |
| `list_regions`（读改前拿当前 revision） | `revision_no=3` |
| `set_region_type`（expected_revision=3） | `region_type=narration`, `revision_no=4` |
| `restore_region_revision`（revision_no=1, expected=4） | 新 `revision_no=5`, `region_type=speech` |
| `rerender_page` | `artifact_id` 非空, `revision_no=1`, `reports=1` |
| `resolve_page_resource` | `page-original-{page_id}`, `revision=original` |
| `library_save_reading_progress` | mode=original, 落库 `total_read_seconds≥1.5` |
| `library_get_reader_projection` | `layout=webtoon_vertical`, `pages=8`, `initial_page` 命中 |

另：raw wire 级探针（真实 id，同 fixture 的一次性副本）见
[`commands/core-command-probe.json`](commands/core-command-probe.json)，6 条目标路由 + `list_regions` / `list_region_revisions` 全部 `ok:true`（`raw_request_ascii:true`）。
空数据根上的 typed 边界拒绝（`TARGET_NOT_FOUND`，`resolve_page_resource` 为路由专属 `PAGE_NOT_FOUND`）见
[`evidence/integration-results.json`](evidence/integration-results.json) 的同一次 AC4 集成测试（5 条 routing probe）。

## AC3 — parity 与零漂移

- 命令面提取器：`python apps/desktop-avalonia/scripts/extract-command-surface.py --check` →
  `PASS: production command surface matches snapshot (66 commands, ...)`，见 [`parity-check.log`](parity-check.log)。Rust 命令面未改，snapshot sha256 仍为 `4c6a4da0e8968c6b62516fdbabd5608f4dd14cdd4d91c2c0b9d16a1092ccb574`。
- C# registry parity：`24 IMPLEMENTED / 42 NOT_SUPPORTED` → **`29 IMPLEMENTED / 37 NOT_SUPPORTED`**（66 全归属、每族原因可见），见 [`parity-update.json`](parity-update.json) 与 [`evidence/parity-contract.json`](evidence/parity-contract.json)（`implemented=29, not_supported=37, coverage=100`）。

## AC4 — 回归

| 套件 | 结果 | 证据 |
| --- | --- | --- |
| `apps/desktop-avalonia/scripts/test.ps1` | **PASS：146/146 passed，0 skipped**（coreclient 41 / host 42 / app 63） | [`evidence/test/summary.json`](evidence/test/summary.json)、[`evidence/test/dotnet-test-Debug.log`](evidence/test/dotnet-test-Debug.log) |
| vitest | **60 files / 567 tests passed** | [`vitest.log`](vitest.log) |
| pytest | **3 failed, 2739 passed, 9 skipped**，与基线一致，无新增失败 | [`pytest.log`](pytest.log) |

pytest 3 个基线失败（未变化，与本批无关）：`tests/providers/test_detection_manga_real.py::test_real_detection_returns_block_candidates`、`...::test_real_blank_page_yields_zero_candidates`、`tests/workbench/test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately`。

## AC5 — 治理

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/S4-CMD-BATCH-1.md` → 见交付回报（PASS，0 error）。
- 64-hex pin / delivery head 见 Task 卡 Canonical Evidence 与 Handoff。
- 并发：`core-admin-rca` 的 RUN-EXPORT-E2E-1 同改 `HostCommandRegistry.cs`；本分支先落地，后续集成如遇冲突按先落地者为准 rebase 并只在 Handoff 记一行。

## 复跑方式

```powershell
# 1) 冻结 sidecar 目录（AC11 仓外副本）已存在时：
pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 `
  -SidecarDirectory "G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy" `
  -EvidenceDirectory "G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1/evidence-rerun"
# 2) raw wire 探针（可选，需先有 region fixture）：
pwsh -NoProfile -File apps/desktop-avalonia/scripts/probe-core-commands.ps1 `
  -SidecarDirectory "G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy" `
  -OutputPath "verification/S4-CMD-BATCH-1/commands/core-command-probe.json" `
  -RegionFixtureDataRoot "G:/CODEX/New Manga.workspace/task-envs/S4-CMD-BATCH-1/region-fixture"
```

fixture 依赖：`NEWMANGA_BOOK_FIXTURE_ROOT`（或 workspace 默认 BOOK-FIXTURE-1 路径）；缺失时 `seed_s4_region_fixture.py` 回退到 `test_assets` 页面导入，再缺失则该集成测试自我跳过并给出显式 reason（`NEWMANGA_S4_REGION_FIXTURE`）。

## Record Decision — region 写权限 / 只读门

**决定**：本批 6 条命令只在 `NewManga.CoreClient` 的 registry / dispatcher / domain service 层接线；**不新增** `HostRuntime` 的公开写方法，因此不改变现有“parity 前只读”门。

- 已有只读门：`HostRuntime.CreateBookAsync` / `SaveReadingProgressAsync` 等在 `Policy.WritesAllowed == false` 时抛 typed `ReadOnlyHostException`，请求不达 Core（`src/NewManga.Host/HostRuntime.cs:70-79,155-167`）。
- region 写 4 条同样是写命令：**S5 若通过 `HostRuntime` 向 UI 暴露，必须复用 `Policy.WritesAllowed` 门与 `ReadOnlyHostException` typed 拒绝**，不得让 App 直接持 `HostCommandDispatcher` 绕过；dispatcher 自身不做策略判断（与既有 24 条一致，Core 是语义权威）。
- 真实写操作前必须持当前 revision（`list_regions` → `expected_revision`），Core 的乐观锁在并发写时返回 `INPUT_REVISION_CHANGED`；Host 不得猜测/伪造 revision 或 id。
- 本批未扩大写权限：没有新增可被 UI 直接调用的公开写方法，也没有修改只读策略判定。

## 遗留

1. `list_region_revisions`（region 读）仍 NOT_SUPPORTED：不属本批 6 条，但其 Core 路由在真实 fixture 探针中已 `ok:true`，可作为下一批（S4 读面/撤销 UI）直接接线。
2. `library_get_reader_projection` 仅在 base 已有实现（NS-WIRE-A1），本批未改其代码，只补真实 chapter 成功复验；回执中已明确“5 新 + 1 既有”。
3. 本分支基于 `171529b5d`（落后 main 2 个 commit：`321cbc195` 仅 task card 发布提交）；集成 rebase 时以先落地者为准。
4. `probe-core-commands.ps1` 的 S2 默认探针仍保留旧的 invalid payload 记录（历史证据）；真实 id 探针通过新参数 `-RegionFixtureDataRoot` 启用，默认行为不变。
