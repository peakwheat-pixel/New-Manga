# S4-CMD-BATCH-1 Handoff（S4-A/B/C：region 写 4 + reader 2 命令接线）

- Task: `doc/tasks/S4-CMD-BATCH-1.md`（team task-30）
- Branch: `task/S4-CMD-BATCH-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/S4-CMD-BATCH-1`
- Base: `171529b5d`（任务卡基线，释放提交）；**已 rebase 到 `main` `b993e68bb`**（RUN-EXPORT-E2E-1 先落地，registry 24→33；按“先落地者为准”合并）
- Delivery head: `c6beb61c60ae876b79dd0b09ff0e275b0d4a53d5`（实现+证据提交；Task 卡 Canonical Evidence 的 sha256 pin 均指向该树）
- 未 push；未改 Python Core 语义、未改 Host wire 契约/旧壳。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 清单（6 条） | **MET** | `verification/S4-CMD-BATCH-1/command-list.json`（逐条：旧壳 handler/参数/返回/错误类型、Core 路由、payload、result、wire error、before→after、rebase 前后 parity） |
| AC2 接线 | **MET** | registry 5 条 Core 绑定 + dispatcher 旧壳签名边界校验/负载翻译 + S4Wiring 账本更新；真实执行：`evidence/commands/s4-region-reader-results.json`（7/7，含 6 条目标命令，region 写带有效 target）+ raw wire 探针 `commands/core-command-probe.json`（6 目标路由 + list_regions/list_region_revisions 全 `ok:true`） |
| AC3 parity | **MET** | `--check` PASS、快照 sha 未变；任务基线 24/42 → rebase main 33/33 → 合并后 **38 IMPLEMENTED / 28 NOT_SUPPORTED**（本批 5 条变更）；`parity-update.json` + `evidence/commands/parity-contract.json` |
| AC4 回归 | **MET** | test.ps1 **158/158**（coreclient 41 / host 42 / app 75，0 skipped）；vitest **60/567**；pytest **3 failed / 2746 passed / 9 skipped**（失败集合与任务书基线 3F/2739P/9S 完全一致；main 已合入 7 个 device 测试使通过数 2739→2746，无新增失败） |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；13 条 64-hex sha256 pin；本 Handoff + Task 卡 Record Decision |

## 2. 代码改动（全部 `apps/desktop-avalonia/**`，合并后）

| 文件 | 改动 |
|---|---|
| `src/NewManga.CoreClient/Commands/HostCommandRegistry.cs` | `CoreBindings` 新增 5 条（`set_region_type` / `restore_region_revision` / `rerender_page` / `resolve_page_resource` / `SaveReadingProgress`，envelope minor 均为 3）；从 `CoreRoute` NS 原因表移除这 5 条；类注释与实现集清单更新为合并后 38 条 |
| `src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs` | `WriteCorePayload` 新增 5 个 case：按旧壳 Tauri 签名校验必填/可选参数并构造精确 Core payload（`region_id` / `new_region_type` / `expected_revision` / `revision_no` / `page_id` / `chapter_id` / `mode` / `scroll_offset_y` / `elapsed_seconds_delta`），新增 `RequireInt64` / `WriteOptionalInt64` / `WriteOptionalDouble`；参数错 → `INVALID_ARGUMENTS` |
| `src/NewManga.App/Shell/ReaderWorkbenchSupport.cs` | `S4Wiring.WiredImplemented` 合并后 28 条（RUN-EXPORT 9 条 + 本批 5 条 + 既有）；`NsBatch` 清空（S4-A/B/C 全部接线）；`VerifyAgainstRegistry()` 仍为空 |
| `scripts/seed_s4_region_fixture.py` | 新增 fixture 播种：复用 BOOK-FIXTURE durable state（缺失时回退 `test_assets` 导入），用生产 assembly/导入/编辑/artifact 用例追加 1 个 CLEAN artifact + 1 个 confirm 翻译区域；输出 `fixture.json` |
| `scripts/test.ps1` | 自动执行播种并导出 `NEWMANGA_S4_REGION_FIXTURE` |
| `scripts/probe-core-commands.ps1` | 新增可选 `-RegionFixtureDataRoot`：用真实 id 对一次性副本探针 region/reader 6 路由；默认行为不变（S2 历史探针） |
| `tests/NewManga.CoreClient.Tests/Support/S4RegionFixture.cs` | fixture 定位/元数据读取/durable state 复制/独立 data root 的 CoreOptions |
| `tests/NewManga.CoreClient.Tests/Commands/S4RegionReaderCommandTests.cs` | 6 命令 + list_regions 读改前的真实执行断言（fixture 缺失时自我跳过并给 reason），写 AC2 证据 |
| `tests/.../CommandIntegrationTests.cs` | 5 条 routing typed-error 断言（`TARGET_NOT_FOUND`，`resolve_page_resource` 为 `PAGE_NOT_FOUND`）+ 合并后计数（24 成功执行 / 28 NS / 38 implemented） |
| `tests/.../CommandParityContractTests.cs` | 38/28 |
| `tests/NewManga.App.Tests/S4ReaderWorkbenchTests.cs` | 28 wired / 0 NS（含 JSON 断言）；S4 wiring 证据改名 `commands/s4-wiring.json`，不再与 S3 的 `commands/wiring.json` 互相覆盖 |

## 3. 关键决策（Record Decision）

1. **写权限 / 只读门（AC5 要求）**：本批只在 CoreClient registry/dispatcher/domain service 层接线，**不新增** `HostRuntime` 公开写方法，不改变“parity 前只读”门。
   - 既有门：`HostRuntime.CreateBookAsync` / `SaveReadingProgressAsync` 在 `Policy.WritesAllowed == false` 时抛 typed `ReadOnlyHostException`，请求不达 Core（`src/NewManga.Host/HostRuntime.cs:70-79,155-167`）。
   - S5 若把 region 写 4 条经 `HostRuntime` 暴露给 UI，必须复用同一 `Policy.WritesAllowed` 门与 typed 拒绝；App 不得直接持 `HostCommandDispatcher` 绕过。
   - 真实写前先读当前 revision（`list_regions` → `expected_revision`）；并发写由 Core 乐观锁返回 `INPUT_REVISION_CHANGED`，Host 不猜测/伪造 revision 或 id。
2. **未验证不标 IMPLEMENTED**：5 条全部有冻结 sidecar 真实成功执行；`library_get_reader_projection` 在 base 已实现（NS-WIRE-A1），本轮补真实 chapter 复验而非重复接线；`list_region_revisions`（读，非本批）仍 typed NOT_SUPPORTED。
3. **region 写成功路径必须用真实 target**：BOOK-FIXTURE 初始 0 region/0 clean artifact，故新增 fixture 播种（生产用例，不写 SQL 领域状态），测试只在 durable 副本上执行；缺 fixture 时测试自我跳过并写明 reason，不会静默通过。
4. **`resolve_page_resource` 的错误码特殊性**：冻结 Core 对该路由把缺失 page 映射为 `PAGE_NOT_FOUND`（`core_service.py:4409-4424`），不是 `TARGET_NOT_FOUND`；集成断言按真实契约写。
5. **先落地者为准**：RUN-EXPORT-E2E-1 先落 main（`b993e68bb`）；本分支 rebase 后人工合并两批 registry/dispatcher/测试计数，保留其 9 条 + 本批 5 条，S4 账本清零；未触碰其契约。
6. **Rust 命令面快照零改动**：`extract-command-surface.py --check` PASS、sha `4c6a4da0…` 未变；状态变化只在 C# registry。

## 4. 证据索引（`verification/S4-CMD-BATCH-1/`）

- `command-list.json`（AC1 6 条契约 + rebase 前后 parity）
- `commands/core-command-probe.json`（raw wire：真实 fixture 副本，6 目标路由 `ok:true`）
- `parity-update.json` + `parity-check.log`（AC3：24/42 → 33/33 → 38/28；`--check` PASS）
- `evidence/commands/{s4-region-reader-results,integration-results,parity-contract,not-supported-typed-errors,s4-wiring,domain-services,chinese-roundtrip}.json`
- `evidence/test/summary.json` + `evidence/test/{dotnet-test-Debug.log,results-*.trx}`
- `vitest.log`（60/567）、`pytest.log`（3F/2746P/9S，失败集合同基线）
- `REPORT.md`

## 5. 遗留 / NOT_RUN

1. `list_region_revisions`（region 读）仍 NOT_SUPPORTED：不属本批 6 条；其路由在真实 fixture 探针已 `ok:true`，可直接作为下一批接线。
2. region 写的 UI 入口与只读门落地属 S5（本批只到 `HostCommandDispatcher`）。
3. `rerender_page` 的既有 preview 投影只断言存在性（`preview` 或 `preview_error`），未逐像素比对渲染质量（S4-A 视觉验收由后续 UI 验收覆盖）。
4. 本分支 rebase 后未重新验证 RUN-EXPORT 的 `Export/Run 真跑` 结论（其 Task 已如实记录 BLOCKED）；本批只回归其命令接线与计数。
5. 需独立 Review（Owner 不得自审；reviewer=`dsh`）。
