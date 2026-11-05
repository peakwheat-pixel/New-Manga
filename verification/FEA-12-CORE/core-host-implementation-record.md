# FEA-12-CORE 分片 B 实施记录（.NET Host 桥：capability probe + R-002 处置 + 回归）

- Owner：`fea12-core-host`（DSH Agent Teams 分片 B；共享任务 task-7；Lead 为 DSH 主会话 `lead`）。
- 任务卡：`doc/tasks/FEA-12-CORE.md`（AC11 Host 命令桥 + 「前置事实」R-002 二选一）。
- 冻结 wire：`doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` §5.13/§5.14（rev 2.13 by FEA-12-PREREQ-1，delivery `3e37c595b`）。
- 分片范围：**只碰 `apps/**` 的 .NET 文件 + `verification/FEA-12-CORE/**`**；不改 Python/src/**、冻结契约、schema/依赖、真实数据/回收站；不 push；不分片 A 的 `doc/tasks/FEA-12-CORE.md`（单写者规则：本记录由 Lead 集成时并入卡，**本分片不改 AC 标记**）。
- 基线：卡 base `e47fd47e`、CORE 释放 commit `c8d9adc8d`；实跑 HEAD `d5925957b`（其上其他 commit 为 DSH/DSIM 文档与 DSIM r2 修复）。
- 本分片实现 commit / 交付 head：见交付报告与 `git log`（作者 `fea12-core-host` 的 commit；本记录不写自指 hash）。

## 1. R-002 处置：选择 **(b) probe 错误在 Host 层抛出、绕开 `ProjectDeleteTrashError`**

**选择**：`CORE_CAPABILITY_MISSING` **不**加入 `AllowedDeleteTrashErrorCodes`；probe 在 dispatcher 的投影 try-block **之前**执行（Host 注入的 gate / CoreClient 直接 probe），typed 错误以 `protocol` / `retryable=false` 直接上抛。

**理由**：

1. **语义分层**：`CORE_CAPABILITY_MISSING` 是 Host 侧 protocol 判定（Core 能力面缺失），不是 Core 应用错误；`AllowedDeleteTrashErrorCodes` / `ProjectDeleteTrashError` 表达的是 M2-C1 §5.11.3/§5.14 的 **Core 稳定应用码** taxonomy。把 Host 门禁码混入 Core 码白名单会混淆两层错误语义。
2. **不污染 PREREQ-1 负向对照**：B1/B2 负向对照以 `AllowedDeleteTrashErrorCodes − Fea12DeleteTrashErrorCodes` 重建「注册前白名单」。若 CORE 再往 Allowed 加码，该码会被静默吸收进「注册前」基线，削弱 PREREQ-1 已批准的判别力；选 (b) 白名单保持 rev 2.13 的 20 码原样。
3. **保持冻结分类**：§5.13/§5.14 明确 capability 缺失/探测异常 → `CORE_CAPABILITY_MISSING`（`protocol`/`false`）。若走 `ProjectDeleteTrashError`，该码不在白名单 → 会降级为 `category=unknown`，与冻结分类不符。判别测试实测该降级路径（见 §5 `R002_DiscriminatorProjectionDegrades`）。
4. **门禁顺序 = 零 command frame**：probe 在 dispatch 之前 → 旧 Core 收到的只有 `core.ping`，不再出现「发命令后看 `UNKNOWN_COMMAND`」的非法探测方式（§5.13/§5.14 明文禁止）。

## 2. 实现要点（4 个文件，全部在卡 allowed_paths 内）

| 文件 | 变更 | 位置 |
|---|---|---|
| `apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs` | 新增 `RequireCapabilitiesAsync(IReadOnlyCollection<string>)`：`core.ping` → capabilities；缺失/探测异常（`CoreOperationException`/`SidecarException`）→ `CORE_CAPABILITY_MISSING`(`protocol`,`false`)；空需求直接返回。唯一合法探测通道。 | `:457-495`（`:462` 方法） |
| `apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs` | `InvokeAsync` 在 dispatch try-block **之前**对 `HostCommandRegistry.RequiredCapabilities(name)` 非空命令执行 gate：① 注入的 `_capabilityGate`；② 否则 `_core.RequireCapabilitiesAsync`；③ 两者都无 → fail-closed `CORE_CAPABILITY_MISSING`。gate 抛出的 typed 错误不进入 `ProjectRunError` / `ProjectDeleteTrashError`。 | `:97-123` |
| `apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs` | 新增 Host 层 `DeleteTrashCapabilityAsync`（调 `RequireCapabilitiesAsync(RequiredCapabilities(name))`）；dispatcher 的单一 `capabilityGate` 委托按命令分流：有能力需求 → delete/trash probe，否则 → 原 `SourceSyncCapabilityAsync`（source sync 行为不变）；host-control session 失败回退路径由 dispatcher 的 `_core` probe 兜底（不会 fail-open）。 | `:891-902`、`:1058-1082` |
| `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs` | 新增 2 个 Fact + 1 个 SidecarFact；更新 PREREQ-1 的 `Fea12NewCommands_FrozenCoreFailsClosedWithTypedError`（见 §3）。 | `:603` 起：`:616`、`:682`、`:703`；更新版 `:470` |

能力映射（`HostCommandRegistry.RequiredCapabilities`，rev 2.13 已冻结，本分片复用未改）：

| host command | Core command（minor） | required capability |
|---|---|---|
| `library_preview_permanent_delete_books` | `PreviewPermanentDeleteBooks`（11） | `library.delete.preview/1` |
| `library_list_trash` | `ListTrash`（13） | `library.trash.read/1` |
| `library_move_to_trash` | `MoveToTrash`（13） | `library.trash.write/1` |
| `library_restore_from_trash` | `RestoreFromTrash`（13） | `library.trash.write/1` |
| `library_purge_trash` | `PurgeTrash`（13） | `library.trash.write/1` |

说明：`PurgeTrash` 首版 **不实现**（只登记 wire）。Host 侧仍按其冻结 wire 登记能力需求并按上表 fail-closed；本分片不实现任何 Core 侧行为，是否调用 `PurgeTrash` 由 CORE/UI 决定。

## 3. 预期行为变更：旧断言 → 新断言 → 原因（Lead 要求记录）

被更新测试：`CommandIntegrationTests.Fea12NewCommands_FrozenCoreFailsClosedWithTypedError`（allowed_paths 内；PREREQ-1 的 AC3 负向对照）。

| 项 | 旧断言（PREREQ-1，注册-only Host） | 新断言（CORE，capability-gated Host） | 为什么 |
|---|---|---|---|
| 4 个 rev 2.13 命令（preview/move/list/purge） | typed 失败码 ∈ {`UNKNOWN_COMMAND`,`PROTOCOL_VERSION_UNSUPPORTED`,`UNKNOWN`}；且**存在该 Core command 的 frame**（命令先发到旧 Core 再被拒） | `CORE_CAPABILITY_MISSING`，`category=protocol`，`retryable=false`；每次恰好 **1 个 `core.ping`**、**零 command frame** | M2-C1 §5.13/§5.14 要求 Host **先 probe**；缺失/探测异常 → `CORE_CAPABILITY_MISSING`（`protocol`/`false`）；**不得**以发命令后看 `UNKNOWN_COMMAND` 探测能力。旧行为恰是被契约禁止的探测方式，属预期行为变更，不判回归。 |
| additive `inventory_digest`（`library_delete_book_permanently`，minor 10） | 旧 Core closed-shape → `INVALID_REQUEST`，frame 含 `inventory_digest` | **不变**（minor 10 无 capability 需求 → 不 gate，仍发到旧 Core 并 `INVALID_REQUEST`） | AC5 fail-closed 不降级软删的回归必须保留；能力门禁只作用于 rev 2.13 新命令。 |
| 旧 Host 路径（PREREQ-1 baseline script，旧 assembly） | 5 命令 absent → `Get()` typed `UNKNOWN_COMMAND`；5 新码在 run 白名单外 → `category=unknown` 且 code 原文保留；旧 Core 拒绝新命令 | **不变**（G6 复跑结论与 `baseline-negative-control-base-035468a81.log` 一致） | PREREQ-1 负向对照不回归。 |

结论：负向对照的四项原始含义（typed 失败、非静默丢弃、无软删降级、digest 被旧 Core 拒绝）全部保留；仅「新 Host 对旧 Core 的失败码/时序」按冻结契约升级为 probe-first。

## 4. 测试清单（全部在 `CommandIntegrationTests.cs`）

| 测试 | 类型 | 判别内容 |
|---|---|---|
| `Fea12Core_CapabilityProbe_GateVerdictBypassesDeleteProjection` | Fact | ① 注入 gate 抛 `CORE_CAPABILITY_MISSING` → 5 个命令全部以 `protocol`/`false` 上抛且 gate 先于任何 Core 通道（core=null 下仍是 `CoreOperationException` 而非 `SidecarException`）；② 放行 gate → 命令继续走正常 dispatch；③ 无能力需求的命令不触发 gate；④ **R-002 判别**：该码不在 `AllowedDeleteTrashErrorCodes`，若走 `ProjectDeleteTrashError` 会降级 `category=unknown`（证明必须选 (b) 的绕行）；⑤ registry `RequiredCapabilities` 与 5 命令映射逐项一致（含 PurgeTrash）。 |
| `Fea12Core_CapabilityGatedCommand_WithoutAnyProbeChannelFailsClosed` | Fact | 无注入 gate 且无 Core 通道 → 5 个命令全部 fail-closed `CORE_CAPABILITY_MISSING`（不 unprobed dispatch）。 |
| `Fea12Core_DeleteTrashCapabilityProbe_OldCoreFailsClosedBeforeAnyCommandFrame` | SidecarFact（冻结旧 Core 实测） | ① 旧 Core `core.ping` capabilities 实测只有 `library.list_books`，3 个 rev 2.13 capability 均不广播；② 逐命令直接 probe（delete.preview / trash.read / trash.write 各一例，5 命令全覆盖）→ `CORE_CAPABILITY_MISSING`(`protocol`,`false`)，每次恰好 +1 `core.ping`、零 command frame；③ 正向对照 `library.list_books` 通过同一 probe；④ dispatcher 回退 probe（未注入 gate）逐命令同样 fail-closed 且零 command frame；⑤ stub 放行 gate → 同一 `library_list_trash` 真正 dispatch 到旧 Core 并收到 Core 自身 typed `UNKNOWN_COMMAND`（失败来自 gate，不是命令不可用）→ 证据 `core-host-capability-probe.json`。 |
| `Fea12NewCommands_FrozenCoreFailsClosedWithTypedError`（更新） | SidecarFact | 新 Host + 旧 Core：4 命令 probe-first `CORE_CAPABILITY_MISSING`、每次 1 ping、零 command frame；additive digest（minor 10）仍 `INVALID_REQUEST` 且 frame 含 `inventory_digest` → 证据 `core-host-old-core-negative-control.json`。 |

已复跑的相关既有测试（无回归）：B1/B2 frozen-Core 执行面、命令治理过滤（全部 `~Command`）。

## 5. 证据清单（`verification/FEA-12-CORE/`，`core-host-` 前缀；不覆盖分片 A 文件）

| 文件 | sha256 | 说明 |
|---|---|---|
| `core-host-capability-probe.json` | `20fd4695ca5d08b9f61259bf9c6e999883b17b8821b520e638488f1b906bca33` | G2 侧车实测判别证据；两次独立运行 byte-identical |
| `core-host-old-core-negative-control.json` | `61c1f0045133a132a6180f72daec2c4c443f1eefff716c633c8577c8d93ed300` | 更新后的 PREREQ-1 负向对照证据（probe-first + digest 回归）；两次 byte-identical |
| `logs/gates-core-host.log` | —（本文件同目录；不自指 hash） | G1–G7 门禁记录（命令/结果/EXIT/日志路径） |
| `logs/core-host-dotnet-command-filter.log` | `0f940ac008d4bff3fa9a874c544ff05fd3c323375a4fbc5ce45fdf4701fa406f` | G1 |
| `logs/core-host-dotnet-sidecar-negative.log` | `6cbe8b5908091d1b68061d9f60cddb4ce32f7dda8d1c5246afa4b9351ae77326` | G2 |
| `logs/core-host-dotnet-full-1.log` | `69dba3db821748c1c6c251118c2c9a3282f1f0be630bac6e61accd57cfcbfecc` | G3 run1 |
| `logs/core-host-dotnet-full-2.log` | `2d721e2a7f7e280dec3b4e7a0864c1a820293004a1c0b0ec319d1b7037650187` | G3 run2 |
| `logs/core-host-check.log` | `3f54e116f7de2c5017c2837820e776e3e444c578e884352cbafb145d312df5a9` | G4 |
| `logs/core-host-pins.log` | `991a8cbb25a884e4063157042dbaca2b04ab53866247c4e5b9e19b154cd83c13` | G5 |
| `logs/core-host-baseline-negative-control-oldhost.log` | `ac38d5ecc97409e3405743a84c451279b1c95e2f5bc5b739615980e464d582d8` | G6 旧 Host 负向对照 |

## 6. AC11 对照

| AC11 要求 | 本分片证据 |
|---|---|
| 新命令在 registry/dispatcher/client 注册且与 Core shape 一致 | PREREQ-1 已注册（本分片未改 registry/wire）；`RequiredCapabilities` 逐命令映射由新 Fact 断言；Core shape 由 PREREQ-1 B1/B2 既有测试 + 本分片回归覆盖。 |
| capability 缺失 → `CORE_CAPABILITY_MISSING` | Fact（gate 判别）+ 冻结旧 Core 侧车实测（3 capability 各一例），`protocol`/`false`。 |
| R-002 二选一处置 + 判别测试 | 选 (b)；`R002_DiscriminatorProjectionDegrades` 判别（不在白名单/若投影则 unknown）+ gate 路径保 protocol。 |
| 旧 Core fail-closed | `Fea12Core_DeleteTrashCapabilityProbe_OldCoreFailsClosedBeforeAnyCommandFrame`（probe-first，零 command frame）；更新后的 PREREQ-1 负向对照。 |
| 旧 Host fail-closed | G6 旧 assembly 负向对照复跑（结论与 PREREQ-1 基线一致，不回归）。 |
| `PurgeTrash` 不实现（只登记 wire） | 本分片零 Core 侧实现；仅按冻结 wire 登记能力需求并 fail-closed（测试覆盖）。 |
| 不得以 `UNKNOWN_COMMAND` 探测能力 | probe 只发 `core.ping`；每次恰好 1 ping、零 command frame（Fact + 侧车实测断言）。 |

## 7. 门禁数字（详见 `logs/gates-core-host.log`）

- G1 命令治理过滤：**137 passed / 0 failed / 16 skipped / 153 total**，EXIT 0（两次一致；基线 135/0/15/150，+2 新 Fact、+1 新 SidecarFact skip）。
- G2 冻结旧 Core probe/负向：**6 passed / 0 failed / 0 skipped**，EXIT 0（两次一致）。
- G3 全量 .NET：RUN1 & RUN2 均 **1405 passed / 0 failed / 80 skipped / 1485 total**，EXIT 0（分程序集见 gates log；已知 flaky 未触发，如实记录不称稳定 PASS；两次后均 `git checkout -- verification/FEA-09` 恢复）。
- G4 `check.ps1 -TaskPath doc/tasks/FEA-12-CORE.md`：PASS (3 warnings，均既有)，EXIT 0。
- G5 `verify_pins.ps1`：PASS (all 18)，EXIT 0。
- G6 旧 Host 负向对照：CAPTURED，EXIT 0，结论与 PREREQ-1 基线一致。
- G7 全量 pytest：引用交付基线 FEA-12-PREREQ-1 G4 = 3073 passed / 10 skipped（本分片零 Python 改动；并发 Python 写入使其重跑不代表本分片交付状态）。

## 8. 残余风险（Review 关注点）

1. **HostRuntime 接线无 Host.Tests 单测**：卡 allowed_paths 仅含 `CommandIntegrationTests.cs`，故未新增 `NewManga.Host.Tests` 用例。缓解：HostRuntime 分支仅 3 行（按 `RequiredCapabilities` 分流 + 调已测 `RequireCapabilitiesAsync`）；source-sync gate 行为不变（既有 Host.Tests 全绿）；dispatcher 层 gate 契约有 Fact + 侧车实测。若 Review 要求，需 Lead 窄批放开一个 Host.Tests 文件。
2. **每次调用多一次 `core.ping`**（不缓存 capabilities）：单命令延迟 +1 RTT，换来不会因 Core 升级/降级而缓存过期。若 UI 高频调用 trash 面，可后续在 Host 层加短 TTL 缓存（需先由契约裁定，超出本卡）。
3. **探测异常统一映射 `CORE_CAPABILITY_MISSING`**：按 §5.13/§5.14 capability 条目「缺失/探测异常 → `CORE_CAPABILITY_MISSING`」执行；因此 Core 通道完全不可用时，delete/trash 命令得到的是 `CORE_CAPABILITY_MISSING` 而非 `CORE_UNAVAILABLE`（后者只会在 probe 成功后的命令发送阶段出现）。此为按冻结契约的取舍，已在实现注释标注。
4. **`PurgeTrash` 只登记**：Host 侧能力需求/失败关闭已覆盖；真正实现仍待后续 additive 裁决（不属本卡）。
5. 全量 .NET 的既有 flaky 债务仍在（本轮未触发，不作为稳定 PASS 证明）。

## 9. Review 就绪声明

- 本分片实现完成，门禁 G1–G6 全绿，证据已按 `core-host-` 前缀落库并附 sha256。
- 作者身份：`fea12-core-host`（DSH Agent Teams 分片 B）。**本分片未自审、未 commit Lead-owned 文档、未 push**。
- 请 Lead 安排**上下文独立**的 Reviewer（非本分片实现者）审查交付 commit 的 .NET diff 与上述证据；Review 重点建议：§3 行为变更是否可接受、§8 残余风险 1/3、以及 `RequiredCapabilities` 与冻结 wire 的一致性。
- 卡内 AC 标记由 Lead/分片 A 维护；本记录供 Lead 集成并入 `doc/tasks/FEA-12-CORE.md` 使用。
