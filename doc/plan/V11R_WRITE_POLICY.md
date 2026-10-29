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

## 6. 启动自检（V11R-A-6，A-5 遗留 #1）

Host 启动、Core 握手成功后执行一次**契约自检**（`StartupSelfCheck`，`HostRuntime.SelfCheck`），
目标是"Core/Host 契约漂移时先降级只读并给出 typed error"，而不是让用户第一次写入才失败。

### 6.1 可低成本验证的面

`core.ping` 只公开：`status`、`protocol_version{major,minor}`、`capabilities`（当前仅
`["library.list_books"]`）。**没有完整命令面枚举**；在启动时逐条探测 66 条命令会执行写命令，不可接受。

因此自检执行三项廉价校验：

| 校验 | 失败码（typed） | 结果 |
|---|---|---|
| `core.ping.status == ready` | `CORE_NOT_READY` | 只读 |
| `protocol_version.major == 2` | `PROTOCOL_VERSION_MISMATCH` | 只读 |
| `protocol_version.minor >= 3`（`CoreProtocol.DefaultMinor`；7/8/10 是逐命令请求级扩展，不由 ping 报告） | `CORE_PROTOCOL_MINOR_TOO_OLD` | 只读 |
| `capabilities` 含 `library.list_books` | `CORE_CAPABILITY_MISSING` | 只读 |

全部通过 → `SelfCheckStatus.Degraded`（写入保持开启）：这是**诚实的降级状态**，不是"永远通过"——
`HostRuntime.SelfCheck.Detail` 与 host.log 明确记录"完整命令面比对未执行（follow-up：Core 在
`core.ping` 中提供命令面摘要）"。

### 6.2 失败时的行为

- 新增 `HostMode.ReadOnlySelfCheckFailed`；`DataRootPolicy.WritesAllowed=false`；
- `HostStartResult`：`Status=Ready`（sidecars 已启动，只读浏览可用）、`Mode=ReadOnlySelfCheckFailed`、
  `ErrorCode=<上表 typed code>`、`UserMessage=<中文原因>`；
- UI：`HostViewSnapshot.WritesAllowed=false`、`ReadOnlyReason="只读（启动自检失败）"`、`ErrorCode` 可见；
- 写 API 抛 `ReadOnlyHostException.Code=HOST_READ_ONLY`；
- 诊断：host.log 输出 `self-check status=… code=… detail=…`（不含路径/凭据）。

### 6.3 探测本身失败

`StartupSelfCheck.RunAsync` 的探测抛 `SidecarException`/`CoreOperationException`/取消时：
**保持 ReadWrite**，记录 `SelfCheckStatus.Degraded` + `ErrorCode=SELF_CHECK_PROBE_FAILED` + 诊断；
理由：启动阶段 `core.ping` 握手已经成功，一次自检请求失败不足以判定 Core 不可用（且用户主旅程优先）。

### 6.4 测试与证据

- 单测（无需 sidecar）：`StartupSelfCheckTests` 覆盖匹配/主版本/次版本/能力/未 ready/探测失败；
- 集成（真实 sidecar）：真实 Core → `Degraded` + `ReadWrite` + 真实建书成功；
- 故障注入（真实 sidecar + `HostOptions.StartupPingProbe`）：主版本不匹配 → `ReadOnlySelfCheckFailed`
  + `PROTOCOL_VERSION_MISMATCH` + 写拒绝；能力缺失 → `CORE_CAPABILITY_MISSING`；
- UI：`StartupSelfCheckUiTests`（App 控制器快照只读 + 原因 + typed error）；
- 证据：`verification/V11R-A-6/`。

### 6.5 Follow-up（不硬凑）

1. Core 在 `core.ping` 暴露命令面摘要（例如 `command_surface_sha256` 或命令名列表）后，
   自检可升级为真正比对 `HostCommandRegistry` 的 core-channel 集合 → `SelfCheckStatus.Passed`；
   在此之前 `Degraded` 是准确状态（Core 侧归属：core-writer / V11R-F0-1 后续）。
2. 每次启动的探测只发 1 条 `core.ping`（无额外进程、无写命令），成本可忽略。

## 7. 风险与遗留

1. **默认可写是必要能力**，安全网 = 旧壳共存门 + 显式只读开关 + first-run 备份；三者均有测试。
2. **启动自检已实现基础版（V11R-A-6）**：协议版本 + 能力集 + ready 三项廉价校验；不匹配 → 只读
   + typed error。**完整命令面比对仍待 Core 在 `core.ping` 暴露命令面摘要**（见 §6.5 follow-up），
   当前通过时状态为 `Degraded`（诚实降级，非静默通过）。
3. **旧壳共存策略不变**：检测到旧壳时仍"只读 + 提示"，不杀进程、不双写。
4. **安装器无需改动**：默认参数即写入；`--parity=false` 仅排障/回滚用。
