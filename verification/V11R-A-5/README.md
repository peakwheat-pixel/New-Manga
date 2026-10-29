# V11R-A-5 证据包：生产写入策略修复（P0，默认可写 + 三重护栏 + first-run 备份）

- Task：`V11R-A-5`（团队任务板 task-11；Lead 裁定 R-09）
- Owner：`core-bridge`（写域扩展：`src/NewManga.Host/**` + `src/NewManga.App/AppOptions.cs`，Lead 授权）
- Worktree：`G:/CODEX/New Manga.workspace/worktrees/V11R-CORE-BRIDGE`，分支 `v11r/core-bridge`
- 基线：`c73239999`（含 R-08/R-09 的 main 已合入）
- 交付 commit：见 Handoff 钉 SHA（本证据 commit 的父 commit）
- 状态：AC1–AC7 已实现并有真实执行证据；Owner 未自审，待独立 Reviewer。

## 1. 问题（P0）

发布版 GUI 默认不可写：`HostOptions.ParityReached` 默认 `false`、`AppOptions` 仅 `--parity`/`--demo-write`
置 true、NSIS 快捷方式不带参数 → `CoexistenceRules.Decide(false,false)` → `ReadOnlyUntilParity` →
导入/建书/建章/编辑/Run 全部 `HOST_READ_ONLY`。审计未覆盖，Lead 核实为比审计 P0 更严重的"主旅程无法操作"。

## 2. 变更

| 文件 | 变更 |
|---|---|
| `apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs` | `ParityReached` 默认 **true**（文档说明新策略：只读仅由真实前置条件触发）。 |
| `apps/desktop-avalonia/src/NewManga.App/AppOptions.cs` | `ParityReached` 默认 **true**；`--parity=false` 显式降级；`--demo-write` 保留为兼容开关（仍要求隔离 `--data-root`，不再用于"开启写入"）。 |
| `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` | 保留保守 pre-start 只读门；`StartInternalAsync` 用 `CoexistenceRules.Decide(legacyShellDetected, ParityReached)` 得出最终策略（旧壳共存保护未改）；更新写入 API 注释。 |
| `apps/desktop-avalonia/src/NewManga.App/Services/IHostController.cs` | `HostViewSnapshot` 追加 init-only `ReadOnlyReason`（`CoexistenceRules.Describe` 文案），只读原因对 UI 可见。 |
| `apps/desktop-avalonia/src/NewManga.App/Services/HostController.cs` | 初始/启动失败/刷新失败/往返失败时关闭写门并给 `ReadOnlyReason`；`UpdateFromRuntime` 从 `Policy` 同步 `WritesAllowed` + `ReadOnlyReason`。 |
| `apps/desktop-avalonia/tests/NewManga.Host.Tests/WritePolicyTests.cs` | **新建** 6 条（默认可写、显式只读、旧壳只读、first-run 备份、默认值/共存规则单测）。 |
| `apps/desktop-avalonia/tests/NewManga.App.Tests/WritePolicyUiTests.cs` | **新建** 4 条（AppOptions 默认/降级/兼容 + 真实 HostController 默认可写 / `--parity=false` 只读且带原因与 typed error）。 |
| `doc/plan/V11R_WRITE_POLICY.md` | **新建**：策略、只读条件、first-run 备份语义、回滚/排障、验证矩阵、风险与遗留。 |
| `README.md` | 更新"默认可写 + 只读条件 + first-run 备份"说明（中英各一处）。 |

未修改：Python Core、UI 视图/ViewModel、旧 `apps/desktop`、安装器（默认参数即写入，无需改）。

## 3. 新策略（写入门）

| 条件 | Host 模式 | 写入 | UI 文案 |
|---|---|---|---|
| 默认启动（无参数） | `ReadWrite` | 允许 | `读写就绪`，`ReadOnlyReason=null` |
| 旧 Tauri 壳运行（优先级最高） | `ReadOnlyLegacyShellRunning` | 拒绝 | `只读（旧壳运行中）` |
| 显式 `--parity=false` | `ReadOnlyUntilParity` | 拒绝 | `只读（S2 parity 前）` |
| Host 启动失败/未就绪 | 保持只读 | 拒绝 | `Host 未就绪（只读）` / `Host 启动失败（只读）` |

被拒绝的写操作仍返回既有 typed 通道：`HostViewSnapshot.LastError = "HOST_READ_ONLY"`（A-1 通道），
UI 不得静默失败。

## 4. AC 覆盖

| AC | 结论 | 证据 |
|---|---|---|
| AC1 默认启动 `Policy.WritesAllowed==true`、`Mode==ReadWrite`（单测 + 启动证据） | PASS | `WritePolicyTests.DefaultStart_IsReadWrite_AndCanCreateBook`（真实 sidecar + 真实建书）；`write-policy/default-start.json`；`WritePolicyUiIntegrationTests`（AppOptions 默认 → HostController） |
| AC2 `--parity=false` 写入被拒且有 typed error | PASS | `WritePolicyTests.ExplicitParityFalse_RefusesWrites_WithTypedReadOnlyError`（`ReadOnlyHostException.Code=HOST_READ_ONLY`）；`write-policy/parity-false.json`；App 集成断言 `LastError=HOST_READ_ONLY` |
| AC3 旧壳运行检测仍使写只读（既有 Coexistence 测试保持 PASS） | PASS | `LegacyShell_StillWins_OverDefaultParity`；`LegacyShellDetected_KeepsHostReadOnly_EvenWithDefaultParity`（真实 HostRuntime + scripted probe，无 sidecar 也拒绝写）；`write-policy/legacy-shell.json`；既有 `HostUnitTests.CoexistenceTests.Decide_Table` 全绿 |
| AC4 first-run backup 在 ReadWrite 首次启动真实产生备份文件（含路径与大小） | PASS | `FirstRunBackup_CreatesRealBackupFile_OnFirstWritableStartWithCatalog`；`write-policy/first-run-backup.json`（路径 + 24576 bytes）；`write-policy/first-run-backup.nmbak`（真实备份字节副本） |
| AC5 现有全部测试不回归 | PASS | `logs/dotnet-test-full.log`：App 165 + Host 66 + CoreClient 67 = **298 通过 / 0 失败 / 0 跳过**（含 ChapterCreation/RunController/Import/Region 集成测试） |
| AC6 文档（策略/护栏/回滚 + README 更新"不再默认只读"） | PASS | `doc/plan/V11R_WRITE_POLICY.md`；`README.md` 两处更新 |
| AC7 证据 | PASS | 本目录（命令/日志/TRX/headless 断言/备份文件） |

## 5. 质量门（命令 / exit code / 结果）

| # | 命令（工作目录 `apps/desktop-avalonia`） | exit | 结果 | 证据 |
|---|---|---:|---|---|
| 1 | `dotnet build NewManga.sln -warnaserror` | 0 | 0 warning / 0 error | `logs/build.log` |
| 2 | `dotnet test tests/NewManga.Host.Tests/... --filter WritePolicy` | 0 | 6/6 PASS | `logs/dotnet-test-host-write-policy.log`, `trx/host-write-policy.trx` |
| 3 | `dotnet test tests/NewManga.App.Tests/... --filter WritePolicy` | 0 | 4/4 PASS | `logs/dotnet-test-app-write-policy.log`, `trx/app-write-policy.trx` |
| 4 | `dotnet test NewManga.sln --no-build`（整解） | 0 | 165 + 66 + 67 = 298 PASS / 0 failed / 0 skipped | `logs/dotnet-test-full.log` |

环境：`NEWMANGA_CORECLIENT_SIDECAR_DIR=task-envs/HOST-CORECLIENT-1/sidecar-copy`；
`NEWMANGA_BOOK_FIXTURE_ROOT=task-envs/BOOK-FIXTURE-1/isolated-data`；所有数据根均为一次性临时目录，
**不触碰用户真实数据根**（`%APPDATA%\com.newmanga.desktop`）。

## 6. 偏差 / 遗留

1. **启动自检（Core 命令面 vs 注册表 → 不匹配降级只读）未实现**：任务卡列为"可选但推荐"。当前由
   `core.ping` 握手 + 既有 parity 注册表测试覆盖；运行时自检降级登记为 follow-up（建议并入
   `V11R-A-4` 或后续运维任务），不在 P0 修复里硬凑。
2. **`--demo-write` 保留**：仍要求显式 `--data-root`（隔离演示），语义收窄为兼容开关；未删除以免破坏
   既有演示/证据脚本。
3. **旧壳共存策略不变**：检测到旧壳仍"只读 + 提示"，不杀进程、不双写（AC3 固化）。
4. **sidecar 副本非本 SHA 构建**（既有 AC11 副本）：本证据保留该声明；L4 前由 Lead 安排同 SHA 构建复验。
5. 备份证据副本 `first-run-backup.nmbak` 是测试临时数据根中真实备份文件的字节拷贝（临时根在测试结束时清理）。

## 7. 文件清单

```
verification/V11R-A-5/
  README.md                          （本文件）
  logs/build.log                     0 warning / 0 error (EXIT=0)
  logs/dotnet-test-host-write-policy.log    6/6 PASS (EXIT=0)
  logs/dotnet-test-app-write-policy.log     4/4 PASS (EXIT=0)
  logs/dotnet-test-full.log                 298 PASS / 0 failed / 0 skipped (EXIT=0)
  trx/host-write-policy.trx / app-write-policy.trx
  write-policy/default-start.json            AC1 默认可写 + 真实建书
  write-policy/parity-false.json             AC2 只读 + HOST_READ_ONLY
  write-policy/legacy-shell.json             AC3 旧壳只读
  write-policy/first-run-backup.json         AC4 备份路径 + 字节数
  write-policy/first-run-backup.nmbak        AC4 真实备份文件副本（24576 bytes）
  host-logs/**                               各场景 host.log / core stderr / wire NDJSON
```

