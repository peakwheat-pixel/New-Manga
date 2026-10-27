# NS-WIRE-A1 Handoff（NS 命令接线第一批：settings / plugins / backup / cleanup）

- Task: `doc/tasks/NS-WIRE-A1.md`（team task-23）
- Branch: `task/NS-WIRE-A1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/NS-WIRE-A1`
- Base: `230164c5c`（卡面）；实际分支基于释放提交 `b50ab8fc5`（含任务卡与治理 PASS 状态）
- Delivery head: `14e855407`（实现+证据提交；任务卡 Canonical Evidence 的 pin 均指向它）
- 未 push；未改 Python Core 语义、未改 Host 契约（wire 契约不变）、未改旧壳。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 清单（8 条） | **MET** | `verification/NS-WIRE-A1/command-list.json`（逐条：旧壳 handler/参数/返回/错误类型、Core 路由、minor、probe 结果） |
| AC2 实现 | **MET** | registry 8 条 Core 绑定 + dispatcher 参数边界校验/负载翻译；真实执行：`probe-results.json`（8 路由）+ `evidence/integration-results.json`（24 implemented 实测）+ typed-error 反证 |
| AC3 parity | **MET** | `--check` PASS、快照 sha 未变；16→24 IMPLEMENTED / 50→42 NOT_SUPPORTED（8 条变更）；`parity-update.json` + `evidence/` |
| AC4 回归 | **MET** | test.ps1 110/110；vitest 60/567；pytest 3F/2739P/9S（0 新增） |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` PASS；64-hex pin；本 Handoff |

## 2. 代码改动（全部 `apps/desktop-avalonia/**`）

| 文件 | 改动 |
|---|---|
| `src/NewManga.CoreClient/Commands/HostCommandRegistry.cs` | `CoreBindings` 新增 8 条（settings.update_section 3 / P15 settings 3 条 7 / backup.create 3 / plugins.set_enabled 3 / cleanup.run 3 / GetReaderProjection 3）；`library_get_reader_projection` 从"路由未验证"表移除；类注释 16→24 |
| `src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs` | 新增 `WriteCorePayload`：按旧壳签名校验必填/可选参数并翻译为 Core 负载（`backup_type` 缺省 `manual`、P15 三条空负载、resolve_overrides 可选 id、reader projection 三字段）；参数错 → `INVALID_ARGUMENTS` |
| `src/NewManga.App/Shell/ShellSupport.cs` | `ShellCommandCatalog`：8 条从 S3 NS 账本移入 WiredImplemented（wired 13→21 / ns 8→0） |
| `src/NewManga.App/Shell/ReaderWorkbenchSupport.cs` | `S4Wiring`：`library_get_reader_projection` 从 S4 NS 账本移入 wired（wired 13→14 / ns 10→9） |
| `src/NewManga.App/Views/Pages.cs` | 设置页 S2 NS 批次标签更新为「S3-A/B/C 已由 NS-WIRE-A1 接线」 |
| `tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs` | 新增 8 条真实执行（7 成功断言 + reader projection `TARGET_NOT_FOUND` 路由断言）；计数 17→24 行、13→20 core channel、50→42 typed、16→24 implemented |
| `tests/NewManga.CoreClient.Tests/Commands/CommandParityContractTests.cs` | 16→24 / 50→42 |
| `tests/NewManga.App.Tests/S3ShellTests.cs` | 21 wired / 0 NS（含 JSON 断言） |
| `tests/NewManga.App.Tests/S4ReaderWorkbenchTests.cs` | 14 wired / 9 NS（含 JSON 断言） |

## 3. 关键决策（Record Decision）

1. **P15 settings 面必须 minor=7**：冻结 Core 对 `_P15_SETTINGS_COMMANDS` 做 `version.minor != 7` 硬拒
   （probe 反证 minor=3 → `INVALID_REQUEST`）。registry 因此对这 3 条固定 `CoreMinor=7`，其余 5 条 minor=3。
2. **参数边界在 dispatcher 复刻旧壳签名**：旧 Tauri 命令是强类型参数，非法参数在边界被拒；C# dispatcher
   用同一套必填/可选规则做 `INVALID_ARGUMENTS`，业务错误码仍由 Core 原样透传（语义权威不变）。
3. **reader projection 成功路径证据与集成测试分离**：集成测试数据根无页面，只能证明路由 + `TARGET_NOT_FOUND`；
   成功路径由 `probe-results.json` 在 BOOK-FIXTURE-1（8 页）数据根实测覆盖，二者合起来满足"每条真实执行"。
4. **未验证不标 IMPLEMENTED**：本批 8 条全部有成功实测；剩余 42 条保持 typed NOT_SUPPORTED + 原因。
5. **Rust 命令面快照零改动**：`extract-command-surface.py --check` PASS、sha `4c6a4da0…` 未变；
   状态变化只发生在 C# registry（parity 证据见 `parity-update.json`）。

## 4. 证据索引（`verification/NS-WIRE-A1/`）

- `command-list.json`（AC1 清单，含 probe 实测摘要）
- `probe-results.json`（冻结 core_service 直连 8 路由 + 2 负例）
- `parity-update.json` + `parity-check.log`（AC3 前后对比 + `--check` PASS）
- `evidence/{parity-contract,integration-results,not-supported-typed-errors,domain-services,chinese-roundtrip,wiring}.json`
  （由 `scripts/test.ps1` 本轮真实运行生成后复制，AC2/AC4 证据）
- `dotnet-all.log`（110/110）、`vitest.log`（60/567）、`pytest.log`（3F/2739P/9S）
- `REPORT.md`

## 5. 遗留 / NOT_RUN

1. S4-A/B/C 10 条（region 写/save_reading_progress/Run/Export）仍 NOT_SUPPORTED，留后续批次。
2. `cleanup_run` 只覆盖空缓存投影；真实 pending 缓存清理未构造。
3. `backup_create` 只覆盖创建（隔离根 `.nmbak`）；restore/delete 不在本批。
4. reader projection 成功路径依赖 BOOK-FIXTURE-1 数据根（未随仓库提交；task-env 保留）。
5. 需独立 Review（Owner 不得自审）。
