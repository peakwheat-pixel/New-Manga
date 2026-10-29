# V11R 生产写入策略（V11R-A-5，P0 修复）

状态：`ACTIVE`（2026-10-30，Owner `core-bridge`，Lead 裁定 R-09）。
上游：[AD-002 目标架构](../AD-002_TARGET_DESKTOP_ARCHITECTURE.md)、
[V11R_PROGRAM](../V11R_PROGRAM.md)、[V11R_AVALONIA_CONTRACT](../plan/V11R_AVALONIA_CONTRACT.md)。
证据：`verification/V11R-A-5/`。

## 1. 背景（为什么这是 P0）

迁移期的写入门把 **S2 命令 parity 未达成** 当作永久只读条件：

- `HostOptions.ParityReached` 默认 `false`，`AppOptions` 只有 `--parity` / `--demo-write` 会置 `true`；
- NSIS 安装快捷方式不带任何参数（`packaging/.../installer.nsi`）；
- `CoexistenceRules.Decide(false, parityReached:false)` → `ReadOnlyUntilParity`；
- 因此**发布版 GUI 默认不可写**：导入、建书、建章、区域编辑、Run 全部被拒（`HOST_READ_ONLY`）。
  这是审计未覆盖的"主旅程无法操作"阻断，比审计列出的 P0 更严重。

## 2. 新策略（默认可用 + 真实前置条件门）

写入策略不再是"迁移期默认只读"，而是**默认可写 + 三类真实只读条件**：

| 条件 | 判定 | Host 模式 | UI 表现 |
|---|---|---|---|
| 默认启动（无参数） | `ParityReached = true` | `ReadWrite` | 写入控件可用；`ModeLine = 读写就绪` |
| 检测到旧 Tauri 壳 `new-manga.exe` 运行 | `CoexistenceRules.Decide(legacy:true, …)`（**优先级最高**） | `ReadOnlyLegacyShellRunning` | `只读（旧壳运行中）`，`WritesAllowed=false` |
| 显式 `--parity=false` | `AppOptions.ParityReached=false` | `ReadOnlyUntilParity` | `只读（S2 parity 前）`，`WritesAllowed=false` |
| Host 启动失败 / 未就绪 | `HostRuntime.Result` 非 Ready 或启动异常 | 保持/回落到只读 | `Host 未就绪（只读）` / `Host 启动失败（只读）` |

实现要点：

- `HostOptions.ParityReached` 默认 **true**（`src/NewManga.Host/HostOptions.cs`）；
- `AppOptions.ParityReached` 默认 **true**，`--parity=false` 显式降级（`src/NewManga.App/AppOptions.cs`）；
- `HostRuntime` 构造时保持保守的 pre-start 只读门，`StartInternalAsync` 用
  `CoexistenceRules.Decide(legacyShellDetected, ParityReached)` 覆盖为最终策略
  （`src/NewManga.Host/HostRuntime.cs`）；旧壳共存保护**未删除、未弱化**；
- UI 只读原因：`HostViewSnapshot.WritesAllowed`（既有）+ **新增 `ReadOnlyReason`**
  （`CoexistenceRules.Describe` 文案，如 `只读（旧壳运行中）`）+ `ModeLine`；被拒绝的写操作同时通过
  `HostViewSnapshot.LastError = "HOST_READ_ONLY"` 给出 typed code，不静默失败；
- `--demo-write` 保留为兼容开关：仍要求显式 `--data-root`（隔离演示），不再用于"开启写入"。

## 3. First-run backup（首次写入前的安全网）

既有 `FirstRunBackup.EnsureBackup(dataRoot, <dataRoot>/backups)` 在 `FirstRunBackupEnabled=true`（默认）时
于**每次 Host 启动、sidecar 启动之前**执行：

- 若 `<dataRoot>/catalog/catalog.sqlite` 不存在（全新安装）→ 跳过（没有可备份内容）；
- 若存在 → 复制为 `<dataRoot>/backups/catalog.<UTC>.sqlite.nmbak`；
- 幂等：backups 目录已有 `*.nmbak` 时跳过，绝不覆盖既有备份。

因此"首次写入前已有备份"由**第二次启动**保证（第一次启动由 Core 建库，第二次启动前复制）。
证据：`verification/V11R-A-5/write-policy/first-run-backup.json`（含真实文件路径与字节数）+
`verification/V11R-A-5/write-policy/first-run-backup.nmbak`（真实备份文件的字节副本，防临时目录清理）。

## 4. 回滚 / 排障

| 目的 | 方法 |
|---|---|
| 恢复迁移期只读 | `NewManga.App.exe --parity=false`（或安装快捷方式追加该参数） |
| 复现旧壳共存只读 | 启动旧 Tauri 壳 `new-manga.exe` 后再启动新 App（或 `--legacy-shell-check=on`，默认 on） |
| 隔离演示/测试数据 | `--data-root=<临时目录>` + `--log-dir=<临时目录>`（不得指向用户真实数据根） |
| 只读原因排查 | UI `ModeLine` / `HostViewSnapshot.ReadOnlyReason`；日志 `host.log` 中 `mode=… reason=…` |
| 关闭备份（仅测试） | `HostOptions.FirstRunBackupEnabled=false`（测试夹具可显式设置；生产不建议） |

## 5. 验证（全部真实执行）

| 验证 | 位置 |
|---|---|
| 默认 `HostOptions.ParityReached == true`、`Decide(false, true) == ReadWrite` | `tests/NewManga.Host.Tests/WritePolicyTests.HostOptions_DefaultParity_IsWritable` |
| 旧壳检测仍压过默认可写 | `WritePolicyTests.LegacyShell_StillWins_OverDefaultParity` + `LegacyShellDetected_KeepsHostReadOnly_EvenWithDefaultParity` |
| 默认启动 `Mode == ReadWrite`、`Policy.WritesAllowed == true` 且真实建书成功 | `WritePolicyTests.DefaultStart_IsReadWrite_AndCanCreateBook` |
| `--parity=false` → `ReadOnlyUntilParity` + `ReadOnlyHostException.Code == HOST_READ_ONLY` | `WritePolicyTests.ExplicitParityFalse_RefusesWrites_WithTypedReadOnlyError` |
| first-run backup 真实文件（路径/大小） | `WritePolicyTests.FirstRunBackup_CreatesRealBackupFile_OnFirstWritableStartWithCatalog` |
| AppOptions 默认/降级/`--demo-write` 兼容 | `tests/NewManga.App.Tests/AppOptionsWritePolicyTests` |
| GUI 控制器默认可写、`--parity=false` 只读 + `ReadOnlyReason` + `HOST_READ_ONLY` | `tests/NewManga.App.Tests/WritePolicyUiIntegrationTests` |
| 全量回归 | `verification/V11R-A-5/logs/dotnet-test-full.log`（0 failed / 0 skipped） |

## 6. 风险与遗留

1. **默认可写是必要能力**，安全网 = 旧壳共存门 + 显式只读开关 + first-run 备份；三者均有测试。
2. **启动自检（Core 命令面 vs 注册表）未实现**：任务卡列为"可选但推荐"。当前以
   `core.ping` 握手 + 既有 parity 注册表测试覆盖；运行时自检降级只读登记为 follow-up
   （建议并入 `V11R-A-4` 或后续运维任务），避免在 P0 修复里硬凑。
3. **旧壳共存策略不变**：检测到旧壳时仍"只读 + 提示"，不杀进程、不双写。
4. **安装器无需改动**：默认参数即写入；`--parity=false` 仅排障/回滚用。
