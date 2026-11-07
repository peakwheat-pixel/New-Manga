---
task: FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1
title: 独立实现 Review r1：枚举 target 扫描执行面恢复（Host-only，零契约）
reviewer: DSH fresh-context subagent（r1；未参与本卡实现/返修/scope review；只读）
session: 9403610b-6c79-40c8-bc92-18cab8d177fc
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: bcc88e4a2
reviewed_evidence_head: 0c1390b2a
base_commit: 58395b9a2
implementation_start: 16082d3a9
verdict: approved
---

# 独立实现 Review r1 — FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1

> **审查基线**：实现/测试字节 = `bcc88e4a2`（delivery head：`8709d6159` + `bcc88e4a2`）；证据字节 = `0c1390b2a`（main HEAD，docs-only）；卡 `doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md`；权威 scope review `doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-scope-r1.md`（READY-TO-FREEZE；Host-only 形状；0 UNFREEZE / 18 pins）；Handoff `doc/handoffs/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-bcc88e4a2.md`；证据 `verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/**`。
>
> **独立性**：本 Review 由 fresh-context 子 agent 执行（session `9403610b-6c79-40c8-bc92-18cab8d177fc`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）。审查者未参与本卡实现、返修或 scope review；除本报告外只读，未改实现/测试/证据/卡/契约，未 `git add/commit/push`。破坏性复跑只临时改 `SourceScanScheduler.cs`，结束后逐字节恢复并以 sha256 + `git diff --quiet` 复核（§4）。
>
> **口径红线（本报告同样遵守）**：本卡只兑现**枚举 target 的扫描执行恢复**——B1 显式重授权 → 既有 refresh/reattest → 枚举 → **下一个未被既有 backoff 抑制的 tick**。不承诺 Run 面恢复、自动恢复/自愈、自动重新授权、撤销后自动放行、folder/B2/L-S4-1/L-S4-2/L-R1。

## 0. 结论先行

- **P0 = 0；P1 = 0；P2 = 0；P3 = 9**（全部为证据容器/文档精度/可维护性项，不改产品行为、不改授权语义、不阻断集成）。
- **verdict：`approved`**。枚举 target 的执行面确实改为使用**同一次 `Registry.List()` 快照**中、由其自身 `(registry_id, generation)` 选中的 live entry 铸 grant；非枚举 `ResolveRegistryEntry` 实现字节零改动；fail-closed 矩阵与「不回落任意 live sibling」保持；无自动授权/identity 重建/registry 结构写；gated 真实 Core 闭环由 `error` 变 `ok`、恰 1 帧 `ScanSourceSync`、wire 无路径；零契约（C15/C16/C17 blob 零漂移、`PROTOCOL_MINOR=3`、pins 18/18）。
- **判别性独立复现**：自选破坏点 **R1**（枚举分支恢复二次 path 解析）→ 单测返回 `Error(SOURCE_ACCESS_DENIED)`、gated 同一闭环 `ok→error` 双 RED；**R2**（删 `SelectEnumeratedEntry` 撤销检查）→ 2 例 RED（撤销 target 试图进入 mint 边界）。二者均逐字节恢复并 sha 复核（§4）。
- **必须保留的口径**：本卡**没有**恢复 Run 面——`HostRuntime.RunSourceRange` 仍按路径调用 `ResolveRegistryEntry`（`HostRuntime.cs:1785`，本卡零 diff）；`backoff` 清理未做；`revoked` 旧行累积是 B1 既有行为。

## 1. 审查范围与方法

- **交付 commit 链**：`8709d6159`（`SourceScanScheduler.cs`：`VerifyEnumeratedTarget(..., out entry)` + 纯函数 `SelectEnumeratedEntry` + `ScanAsync` 枚举分支改用 out entry）→ `bcc88e4a2`（新增 `SourceScanExecutionRecoveryTests.cs` 8 例；`Fea11ScanIpcTests.cs` gated 闭环断言 tick `ok`/1 帧/无路径）。docs/证据在 `0c1390b2a`；`58395b9a2..16082d3a9` 实测 docs-only（1 文件 `doc/tasks/...`，非交付）。
- **实际核对**：`git show/diff` 逐字节；对 `ResolveRegistryEntry` 做 base/head **方法体**（剥离 `///` 后 1812 字符）比对；独立实跑 build / 新单测 / 回归 / gated 真 IPC / 定向 pytest / pins / check×2 / API；证据逐文件 sha256 复算与 fixture 原件同哈希比对；自选 2 个破坏点做「破坏 → RED → 字节恢复 → sha 复核 → 强制重建复绿」。
- **未审/未跑**（详见 §7）：Run 面、folder/B2/L-S4-1/L-S4-2/L-R1、真实用户数据、push；全量 pytest/.NET 由 Owner 实跑、我**仅交叉核对日志与合计**（未重跑，避免重写 tracked `verification/FEA-09/**` 的代价与副作用）。

## 2. 必做核对 A–G

### A. AC-SER-1 主 AC（枚举执行面恢复）— **PASS**

1. **同一次快照**：`VerifyEnumeratedTarget` 仅在 `SourceScanScheduler.cs:1583` 调用一次 `_sources.Registry.List()`；`SelectEnumeratedEntry`（`:1957-1988`）只在该 `entries` 上按 `RegistryId` 精确匹配，并要求 `RevokedAt is null` 且 `Generation == target.Generation`；核验通过后 `:1604` 把该 entry 通过 `out` 交回调用方。`ScanAsync` 枚举分支（`:1511-1519`）直接使用它，**不再**调用 `ResolveRegistryEntry(target.Path)`（该调用只剩非枚举分支 `:1520-1523`）。
2. **正确身份铸 grant**：`ScanAsync:1543-1544` 以 `entry.RegistryId, entry.Generation` 调 `_sources.IssueAsync(...)`；由于 `SelectEnumeratedEntry` 已要求两者分别等于 target 的 `RegistryId`/`Generation`，即「target 自己的 live `(registry_id, generation)`」。没有第二次 path 解析、没有第二次 `List()`。
3. **闭环结果（我独立实跑）**：`NEWMANGA_FEA11_IPC=1 --filter Fea11ScanIpc` **4 passed / 0 failed / 0 skipped**（EXIT=0）。新建 fixture `G:\CODEX\New Manga.workspace\FEA-11\fixtures\scan-de38e1d82af54e40b5f9654130787fe3` 的 `reattest-ipc.json`：`tick_verdict.last_result="ok"`、`scan_frames=1`、`counts.Unchanged=1`、`path_hits=0`、`host_registry_unchanged=true`；`wire.ndjson` 共 17 帧，含恰 1 帧 `ReattestSourceLocation`、恰 1 帧 `ScanSourceSync`；我另行用原始字节检查 `ScanSourceSync` 请求行：**不含** `oldZip`、不含 data root、不含任何 `[A-Za-z]:\` 绝对路径（payload 仅 `source_id/project_ids/scope/kind/grant_ids/missing`）。
4. **判别性（自选 R1，独立复现）**：在枚举分支后重新插回 `entry = ResolveRegistryEntry(target.Path);`（即恢复修复前的二次 path 解析）→ 单测 `ScanAsync_RecoveredEnumeratedTarget_PassesTheAuthorizationGate_InsteadOfBeingDenied` 返回 `Error(SOURCE_ACCESS_DENIED)`（正是 L-S4-B 现场症状，EXIT=1）；gated 同一测试 `Expected: "ok" / Actual: "error"`（EXIT=1）。恢复后双绿。
5. **before/after 可信**：before = L-S4-B 交付证据 `verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/ipc-closed-loop.json`（同一测试、`last_result="error"`、`limitation` 明写执行面未修）；after = 本卡证据（`ok`）。我的 R1 在 gated 上重新产生了 `error`，证明两端可比。

### B. AC-SER-2 fail-closed 矩阵不变 — **PASS**

| 场景（target 自身 registry） | 期望（卡/契约） | 实现与覆盖 | 我的核对 |
|---|---|---|---|
| 条目缺失 | `Skipped(SOURCE_REGISTRY_UNAVAILABLE)` | `:1965-1969`；测试 `SelectEnumeratedEntry_IsTypedOnMissingRegistryAndGenerationDrift`、`ScanAsync_EnumeratedTarget_OwnRegistryRevokedMissingOrDrifted_IsTypedSkip` | 绿；返回早于 mint |
| 条目撤销 | `Skipped(SOURCE_GRANT_REVOKED)` | `:1971-1975`；测试 `..._NeverFallsBackToALiveSibling_...`（同快照内**有**同路径 live sibling，仍 skip）、`..._OwnRegistryRevoked...` | 绿；R2 删该检查 → 2 例 RED |
| 代次漂移 | `Skipped(SOURCE_REGISTRY_BUSY)` | `:1977-1985`；上述两测试 | 绿；Owner B3 判别性日志可复核 |
| 注册根缺失（冷启动） | `Error(SOURCE_REGISTRY_UNAVAILABLE)` | `:1618-1631`（`SourceSecurity.Identity` 抛出且本会话未验证过） | 测试 `ScanAsync_EnumeratedTarget_MissingOrReplacedRoot...` 绿 |
| 注册根被替换 | `Error(SOURCE_REGISTRY_UNAVAILABLE)` | `:1633-1638`（volume/file identity 不等） | 同上绿；Owner B4 判别性日志可复核 |
| 整库不可读/损坏 | 既有 typed（`Error(SOURCE_REGISTRY_UNAVAILABLE)`；`SOURCE_REGISTRY_BUSY` 仍 skip） | `:1580-1593`；测试 `..._UnreadableRegistry_IsTypedFailClosed`（并断言损坏文件未被空 registry 覆盖） | 绿 |
| 不得回落任意 live sibling | 无 fallback | `SelectEnumeratedEntry` 只按 target 自身 `RegistryId` 取条目；找不到即 typed skip | 静态核对 + 测试断言（同路径 live sibling 存在时 target revoked 仍 skip） |
| 零 grant / 零 frame | 所有 typed 路径 | 所有 verdict 均在 `:1525-1562` 的 `IssueAsync`/`SendHostControlAsync` 之前返回；null-Core fixture 若进入 mint 会抛异常而非返回 outcome | 8 例全绿；我另跑既有 4 条 `Executor_EnumeratedTarget_*` **4/0/0** |

**判别性（自选 R2）**：删除 `SelectEnumeratedEntry` 的 `RevokedAt` 检查 → `--filter SourceScanExecutionRecovery` **2 failed / 6 passed**（EXIT=1），失败点为 `..._NeverFallsBackTo...` 与 `..._OwnRegistryRevoked...`；失败痕迹显示撤销 target 越过校验进入 `SourceReadCoordinator.RequireCapability`（mint 边界），即「撤销后自动放行」红线被破坏时测试确实会红。

### C. AC-SER-3 非枚举语义零变化 — **PASS**

- **实现零改动**：剥离 XML 注释后，`ResolveRegistryEntry` 方法体在 `58395b9a2` 与 `bcc88e4a2` 均为 **1812 字符且逐字符相同**（`git show` 提取比对，`identical=True`）；diff 只在方法前新增 `///` 注释（`:1884-1896`，明确其只服务非枚举 target）。
- **调用面**：`ScanAsync` 非枚举分支仍 `entry = ResolveRegistryEntry(target.Path)`（`:1520-1523`）；`HostRuntime.cs:1785` 的 Run 面调用未动。
- **既有测试**：`SourceScanSchedulerTests.RegistryResolution_PrefersExactMatch_AndFailsClosedOnRevokedExactEntry`（`:880`）我单独实跑 **1/0/0**；新增 `ScanAsync_NonEnumeratedTarget_KeepsThePathResolverSemantics`（exact-first / revoked-exact→null / containment fallback / executor 层 `Error(SOURCE_ACCESS_DENIED)`）在 8 例中通过。

### D. AC-SER-4 无自动授权 / 无 identity 重建 / 不写 registry 结构 — **PASS**

- **不写结构**：扫描路径（`ScanAsync` / `VerifyEnumeratedTarget` / `SelectEnumeratedEntry` / `ScanMissingAsync`）未出现 `Register`/`Revoke`/`Reset`；`SelectEnumeratedEntry` 是纯函数（无 I/O、无写）。唯一的持久写是既有 `IssueAsync → Registry.Authorize` 的 `last_used_at` 审计（`SourceAccessRegistry.cs:94-96`）。
- **结构相等证据**：单测 `DescribeRegistryEntries`（`SourceScanExecutionRecoveryTests.cs:44-50`，**不含** `LastUsedAt`）在 recover / revoked-missing-drift / root missing-replaced 各例前后全等；旧 revoked 行仍在、`revoked_at` 与 generation 不变、`registry.List().Length == 2`（`:186-190`）。gated IPC 的 `DescribeRegistryEntries`（`Fea11ScanIpcTests.cs:780-786`，同样不含 `LastUsedAt`）在 reattest 后（`:659`）与**真实 mint 后**（`:689`）均全等。
- **verify→mint 间 revoke 兜底**：`IssueLockedAsync` 在铸造前后三次调用 `Registry.Authorize(registryId, generation, paths)`（`SourceReadCoordinator.cs:517/520/584`）；`Authorize` 在同一锁内新读 registry，撤销 → `SOURCE_GRANT_REVOKED`、代次不符 → `SOURCE_REGISTRY_BUSY`、根 identity 不符 → `SOURCE_REGISTRY_UNAVAILABLE`（`SourceAccessRegistry.cs:62-98`）。即 TOCTOU 撤销不会被放行（由 `ExecuteAsync` 的 `catch SourceAccessException → FromCode` 投影为 typed）。这与 Scope review §2.2 的「verify 与 mint 之间 revoke 也不会放行」一致。
- **旧行保留**：未删除/改写任何 revoked 行；卡 S-3 红线满足。

### E. 独立实跑 — **PASS**

| 场景 | 命令（我实际执行） | 结果（我实测） | 与证据日志 |
|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **0 warning / 0 error，EXIT=0** | `logs/build.log` 一致 |
| Host 新单测 | `dotnet test …Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~SourceScanExecutionRecovery"` | **8 passed / 0 failed / 0 skipped，EXIT=0** | `logs/host-unit.log` 一致 |
| 回归 | `--filter "FullyQualifiedName~SourceRegistry\|FullyQualifiedName~SourceReattest\|FullyQualifiedName~SourceScanSchedulerTests"` | **123 passed / 0 failed / 1 skipped，EXIT=0**（skip = 既有 `SourceRegistryResilienceTests.Ipc_MixedRegistry_...`，需另一 gated 环境变量） | `logs/regression.log` 一致 |
| 既有 executor 负例 | `--filter "FullyQualifiedName~Executor_EnumeratedTarget"` | **4 passed / 0 failed** | EV §1 一致 |
| gated 真 IPC | `NEWMANGA_FEA11_IPC=1 … --filter "FullyQualifiedName~Fea11ScanIpc"` | **4 passed / 0 failed / 0 skipped，EXIT=0**；新 fixture tick `ok`、`scan_frames=1`、wire 无路径 | `logs/host-ipc.log`、`logs/ipc-closed-loop.json` 一致 |
| 定向 pytest | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **89 passed / 1 warning，EXIT=0** | `logs/regression-74.log` 一致（卡面「74」为旧命名，实跑计数 89） |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)，EXIT=0**（C16 `a7f57ebd…`、C17 `aefa0fa5…`、C15 `f9e376a0…`） | `logs/gates.log` 一致 |
| check（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)，EXIT=0** | 一致 |
| check（-TaskPath） | `... check.ps1 -TaskPath doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md` | **PASS (3 warnings)，EXIT=0** | 一致 |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT=0**（IHostController 54 + IRunController 6 + IReaderProgressSink 1 = 61） | `logs/gates.log` 一致 |
| 全量 pytest | 未重跑（Owner 日志） | `logs/full-pytest.log:102` = **3360 passed / 10 skipped / 257.51s**（EXIT=0） | 与卡基线 3360/10 相同 |
| 全量 .NET | 未重跑（Owner 日志） | `logs/full-dotnet.log` 各项目合计 **1652 passed / 0 failed / 94 skipped**（21+38+253+117+31+255+167+770；63+24+7），EXIT=0；= 基线 1644/0/94 + 本卡 8 | 与卡/Handoff 一致 |

- **跑后卫生**：我所有 `dotnet test` 运行后 `git status --porcelain` 为空；`verification/FEA-09` 在 `58395b9a2..0c1390b2a` **零 diff**（我实算），gated fixture 均在仓库外 `G:\CODEX\New Manga.workspace\FEA-11\fixtures\scan-*`。
- **说明**：全量 pytest/.NET 属 Owner 实跑 + Lead 交叉核对（3360/10、1652/0/94 与日志相符），我按交付指令只做交叉核对，未二次重跑（重跑会改写 tracked `verification/FEA-09/logs/wire-redacted.ndjson`，需额外备份/恢复；不影响本卡 AC 判定）。

### F. 证据与判别性 — **PASS（附 4 项 P3 容器/计数/排版项，见 §5）**

- **逐文件 sha**：`RESOURCE-MANIFEST.json` 声明的 19 个 evidence 文件我全部重算 sha256 → **19/19 MATCH**；3 个 repo 交付文件（scheduler / IPC tests / recovery tests）→ **3/3 MATCH**（scheduler `a528e8da…`，与判别性日志的 `original_sha256` 相同）。
- **gated 证据来源可追溯**：`logs/ipc-closed-loop.json` 与 `logs/ipc-closed-loop.txt` 的 sha256（`1f91df56…` / `91710e43…`）与 Owner fixture `scan-49d81853692f427c96e8ef1f27e37e05` 下测试原样落盘的 `reattest-ipc.json/.txt` **逐字节相同**；`logs/ipc-fixture.txt` 记录的正是该 fixture 路径与 `1F91DF56A…`，证据是「测试原样产物」而非手写。
- **判别性 6/6 可信**：`logs/discrimination.log` 显示 B1/B1b/B2/B3/B4/B5 每个破坏点均先 `break_exit=1 RED_AS_EXPECTED=True`，随后 `restore_sha256=a528e8da… MATCH=True` 且 `GREEN_AFTER_RESTORE=True`，`final_sha256` 一致；工具 `tools/discrimination.py` 逻辑为「唯一锚点断言（occurrences==1）→ 写破坏 → 目标用例非 0 → 原字节回写 → sha 校验 → 复跑必须 0」，锚点、过滤器、env（B1b 带 `NEWMANGA_FEA11_IPC=1`）与日志吻合。我另外独立复现 B1/B2 的等价破坏（§4），结论一致。
- **before/after**：见 A.5；before 的 `error` 是 L-S4-B 已入库证据，after 的 `ok` 是同一测试在本卡字节下的产物。
- **scope**：`git diff --name-only 16082d3a9..0c1390b2a` = **24 文件**（实现/测试 3 + 卡/Handoff 2 + 证据 19），全部落在卡 `allowed_paths` 的 7 个模式内（含 `verification/.../**` 下的 manifest）；禁止面（`src/**`、`tests/**`、`doc/plan/**`、`doc/contracts/**`、依赖、`HostRuntime.cs`、`SourceAccessRegistry.cs`、`SourceReadCoordinator.cs`、`SourceRootReattestPlanner.cs`、`NewManga.App/**`、`SourceScanSchedulerTests.cs`、`SourceReattestTests.cs`、`STATUS/PLAN/LEDGER`）**零 diff**（我用排除正则对全 diff 复核，输出为空）。
- **零契约**：C15 blob `b0360cc9…`、C16 `67c741d3…`、C17 `f767e158…` 在 `16082d3a9` 与 `0c1390b2a` **逐 blob 相同**；C16 pin `a7f57ebd…`、C17 pin `aefa0fa5…` 由 `verify_pins` 实算命中；`src/bootstrap/core_service.py:320` `PROTOCOL_MINOR = 3`，`src/**` 零 diff。
- **FEA-09**：`58395b9a2..0c1390b2a -- verification/FEA-09` 零 diff；我跑后 clean。
- **P3 项**：manifest 混入未跟踪的 `tools/__pycache__/*.pyc`（P3-01）；`repo_head_at_generation=d87416514` 是被 amend 前的 docs commit（P3-02）；scope 计数 23 与实际 24 的差值（P3-03）；`ipc-fixture.txt` 首行混入西里尔字母（P3-04）。均不影响 AC 或字节事实。

### G. 不夸大 — **PASS**

- 卡/Handoff/EV 的承诺句均限定为「**枚举 target 的扫描执行恢复**（B1 显式动作 → 既有 refresh/reattest → 枚举 → 下一个未被既有 backoff 抑制的 tick）」；对「自动恢复/自愈/自动重新授权/撤销后自动放行/Run 面恢复」均以否定句出现（我逐文件 grep 复核，未发现肯定式承诺）。
- limitation 保留：Run 面（`HostRuntime.RunSourceRange` 仍按路径解析，`HostRuntime.cs:1785`，我实核）、B2 `roots_available`、folder（L-S4-2）、L-S4-1、L-R1、多根 first-root、backoff 延迟、revoked 行累积均登记（卡 §已知 limitation、EV §5、Handoff §3）。
- gated 证据只描述「新 scheduler 首次 tick 的确定性 ok」，没有宣称同会话 error 后立即自愈；符合 Scope review §4.2/§4.4 的提醒。

## 3. AC-SER-1…6 判定

| AC | 判定 | 关键证据（实跑/静态） |
|---|---|---|
| **AC-SER-1 枚举执行面恢复（主 AC）** | **MET** | 单次 `Registry.List()`（`:1583`）+ out entry（`:1604`）+ 以 `entry.RegistryId/Generation` 铸 grant（`:1543-1544`），枚举分支无二次 path 解析；独立 gated **4/0/0**（tick `ok`、`scan_frames=1`、wire 无路径）；R1 双 RED（单测 `SOURCE_ACCESS_DENIED`、gated `ok→error`） |
| **AC-SER-2 fail-closed 矩阵不变** | **MET** | 缺失/撤销/漂移 → typed Skip（`:1965-1985`）；根缺失/替换 → typed Error（`:1618-1638`）；整库不可读 → typed（`:1580-1593`）；全部先于 mint；不回落 sibling；既有 4 负例 4/0/0；R2 2 例 RED |
| **AC-SER-3 非枚举语义零变化** | **MET** | `ResolveRegistryEntry` 方法体 1812 字符逐字符相同；仅新增注释；既有 `RegistryResolution_...` 1/0/0；非枚举 executor 用例通过 |
| **AC-SER-4 无自动授权/无 identity 重建/不写 registry 结构** | **MET** | 扫描路径无 `Register/Revoke/Reset`；单测/gated 前后结构（不含 `last_used_at`）全等；旧 revoked 行保留；`Authorize` 在 mint 前中后三次复核（`SourceReadCoordinator.cs:517/520/584`） |
| **AC-SER-5 零漂移/门禁** | **MET** | C15/C16/C17 blob 零漂移；pins 18/18；check（默认+`-TaskPath`）PASS(3 warnings)×2；API EXIT=0（61）；scope 24/24 ⊆ allowed、禁止面零 diff；全量 pytest 3360/10、全量 .NET 1652/0/94（Owner 日志，我交叉核对合计）；跑后 FEA-09 clean |
| **AC-SER-6 不夸大** | **MET** | 只承诺枚举执行恢复；Run 面/B2/folder/L-S4-1/L-R1 保留且明写；无「自愈/自动重新授权/撤销后放行」肯定句 |

## 4. 破坏性复跑记录（我自选 2 点；非复用 Owner 的 B1–B5）

- **备份**：`G:\CODEX\New Manga.workspace\FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1\SourceScanScheduler.original.cs`（仓库外 `.workspace` 根；未写 `verification/FEA-09/**`）。原始 sha256 = `a528e8daac7dd1c36ef2305ba4b3ed0e40a740942ca939d74403ad77ef3e3f6c`，与 HEAD blob `21d5b53b…` / manifest 一致。

### 4.1 R1 — 枚举分支恢复二次 path 解析（AC-SER-1 判别）

- 破点：在 `ScanAsync` 的枚举 `VerifyEnumeratedTarget` 之后插入 `entry = ResolveRegistryEntry(target.Path);`（等价于把修复回退为「verify 后仍按路径解析」）。落盘 sha256 = `8a1f338f086418f41c7befa4a07fe5cc0b3a79ce6e3f1237272be74e3d8b3e39`。
- 单测 `ScanAsync_RecoveredEnumeratedTarget_PassesTheAuthorizationGate_InsteadOfBeingDenied`：**EXIT=1**，`Actual: SourceScanOutcome { Kind = Error, ErrorCode = SOURCE_ACCESS_DENIED }`（修复前症状）。
- gated `ReauthorizedSource_IsReattested_ThenEnumerated_WithoutReimport`：**EXIT=1**，`Expected: "ok" / Actual: "error"`。
- 恢复：原字节回写 → sha256 `a528e8da…` **MATCH=True**；`--no-incremental` 重建后单测 **1/0/0**。

### 4.2 R2 — 删除 `SelectEnumeratedEntry` 撤销检查（AC-SER-2 判别）

- 破点：删除 `:1971-1975` 的 `RevokedAt` 检查。落盘 sha256 = `8086079873d09e48c2da98fd47d21256ed5f76b115659c26fe55571cfdb1b9ae`。
- `--filter SourceScanExecutionRecovery`：**EXIT=1**，**2 failed / 6 passed**；失败为 `..._NeverFallsBackToALiveSibling_...` 与 `..._OwnRegistryRevokedMissingOrDrifted_...`，堆栈显示撤销 target 已越过校验到达 `SourceReadCoordinator.RequireCapability`（mint 边界）。
- 恢复：sha256 `a528e8da…` **MATCH=True**；强制重建后 **8/0/0**（EXIT=0）。

### 4.3 恢复与最终状态（含过程披露）

- **最终字节**：`SourceScanScheduler.cs` sha256 = `a528e8daac7dd1c36ef2305ba4b3ed0e40a740942ca939d74403ad77ef3e3f6c`，与 HEAD blob `21d5b53b…` 一致；`git diff --quiet -- <该文件>` EXIT=0；我全部实跑/破坏性复跑期间（16:15–16:25）`git status --porcelain=v1` 为空。最终复核时出现的仓库变更均为**并发 Agent**（Lead closeout）在本会话期间写入、非本审查产物：未跟踪占位卡 `doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md`（16:26:34 创建），以及 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、卡面 `doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md` 的已跟踪修改（含 `status: ready→done` 与 Review r1 处置 append）。本报告的结论只基于 `bcc88e4a2` 实现/测试字节与 `0c1390b2a` 证据字节，不以上述工作树后续修改为依据。
- **过程披露（如实）**：R1 恢复的第一次命令因内联子表达式语法错误**未执行**，文件在恢复前短暂保持破坏态；我随即用独立 `Copy-Item` 恢复并 sha 复核 MATCH。该插曲未影响最终字节（上述 sha/git 复核为证）。
- **复现陷阱（供后续审计）**：`Copy-Item` 会保留源文件 `LastWriteTime`（恢复后 scheduler 时间戳仍是 `15:55:35`，而 mutant DLL 为 `16:17:10`），**增量构建会复用 mutant DLL**，使恢复后的树看起来仍红；必须 `dotnet build --no-incremental` 或 touch 后再测。我的 R1 恢复复绿是在 `--no-incremental` 重建后取得的；Owner 的 `discrimination.py` 用 `write_bytes` 写回会更新 mtime，故未踩该坑。
- **Owner 6/6 判别性复核**：日志、脚本、锚点、env、sha 复原链条均自洽；我独立复现的两个等价破坏与 B1/B2 结论一致，未发现「重跑到绿」或伪造 RED 的迹象。

## 5. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| P3-01 | P3 | `verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/RESOURCE-MANIFEST.json`（`evidence_tree.files` 中的 `tools/__pycache__/discrimination.cpython-314.pyc`） | manifest 声明了一个 **gitignored/未跟踪** 的 pyc；交付的 tracked 证据树（19 文件）中并无该文件。容器完整性/计数与交付集出现 1 项组成差异（哈希本身与工作树 pyc 一致，不构成伪造） | `.gitignore:1`（`__pycache__/`）；`git ls-tree -r 0c1390b2a -- verification/…` 19 文件无 pyc；`git status` clean（pyc 被忽略） | closeout 重生成 manifest 时排除 `__pycache__/**`，或删除该 pyc 并注明；不影响本卡 AC | open（非阻断） |
| P3-02 | P3 | `RESOURCE-MANIFEST.json` → `repo_head_at_generation` | 记录 `d87416514…`，该 commit 是 **amend 前**的 docs commit（与 `0c1390b2a` 同父 `bcc88e4a2`、同 author time，committer time 早 20s），已不在 main 历史；读者可能找不到该 head | `git show -s d87416514 0c1390b2a`；`git merge-base --is-ancestor d87416514 0c1390b2a` = 1；manifest `generated_at` 与 docs commit 同秒 | closeout 在最终 head 重生成 manifest，或在 EV 注明「生成时 HEAD=amend 前提交」 | open（非阻断） |
| P3-03 | P3 | `changed-files.txt` / `scope-validation.log` vs 实际 diff | 实际 `git diff --name-only 16082d3a9..0c1390b2a` = **24 文件**；scope/changed-files 为 **23**（manifest 在 scope 快照之后生成，自排除）。EV §2 已披露「manifest 是容器、不自我哈希」，但未写 23→24 的差值；24 全部在 allowed_paths 内，**不构成越界** | 我的 `git diff --name-only` 实测 24；`scope-validation.log:changed_count=23`；`EV.md` §2 | EV 加一行「delivery 24 = scope 23 + manifest」，或 closeout 重跑 scope；建议保留「容器不自哈希」口径 | open（非阻断） |
| P3-04 | P3 | `logs/ipc-fixture.txt:1` | 「IPС fixture root」中的 `С` 是西里尔字母 **U+0421**（非拉丁 C）。纯排版问题；同文件其余内容与 fixture 路径/hash 正确，证据副本与 fixture 原件逐字节相同 | 我逐码点检查 `char[2]=U+0421`；evidence json/txt sha 与 fixture 原件相同（`1f91df56…`/`91710e43…`） | 仅在授权重生成证据时改为 `IPC`；本卡无需为此改字节（会牵动 manifest） | open（非阻断） |
| P3-05 | P3 | `apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs:1571-1574` | XML 注释称 `entry`「stays null on every verdict returned before the authorization could be proven」，但 `:1604` 在 root/identity 校验（`:1605-1638`）之前就赋了值；root 缺失/替换 verdict 时 `entry` 实际非 null（调用方先看 verdict，故无行为影响） | 代码逐行核对；对应测试只断言 verdict，不读取失败路径的 entry | 注释改为「选中后即赋值；调用方必须先判 verdict」；或在失败路径显式清空 | open（非阻断） |
| P3-06 | P3 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceScanExecutionRecoveryTests.cs:177-182` | 以 `Assert.IsType<NullReferenceException>(error)`（null-Core fixture 的 `RequireCapability`）作为「越过授权门」的证据。若未来 mint 面对缺失 Core 改为 typed 拒绝（更合理），该测试会因与 AC 无关的原因变红；gated IPC 才是权威结果断言 | 测试源码；我实跑 8/0/0；gated 断言 `Ok` | 保留并在注释中登记该 fixture 契约，或引入「到达 mint」的显式 seam/typed 信号 | open（非阻断） |
| P3-07 | P3 | 卡 `approval` 字段 / Handoff `:20` | 两处引用「ZCode 故障转移裁决（READY-TO-FREEZE，TOCTOU/backoff/scope 三点已采纳）」，但我在仓库内**未找到独立的 ZCode 裁决文件/会话 ID**（其他卡如 L-S4-B 的裁决有 `cb81fae0-…` 可追）。冻结依据仍由卡面 S-1…S-5 + scope review READY-TO-FREEZE 承接 | 全 `doc/**` grep「ZCode 故障转移」只命中卡/Handoff/进度记录；无本卡专属 review/裁决文件 | closeout 在卡/Handoff 补登 ZCode 裁决 ID 或落盘其摘要；不影响实现字节 | open（非阻断） |
| P3-08 | P3 | 卡 `AC-SER-2`（`doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md:64`）vs `SourceScanScheduler.cs:1613-1616` | 卡写「root 缺失/替换 → `Error(SOURCE_REGISTRY_UNAVAILABLE)`」；实现对「live 条目存在但没有任何 readable root 恰好等于 `target.Path`」另有一条**既有** `Skipped(SOURCE_REGISTRY_UNAVAILABLE)` 分支（本卡未改）。矩阵「不变」成立，但字面读者可能把两个子场景混为一谈 | 代码 `:1605-1616`；测试 6 覆盖物理缺失/替换 → Error；未覆盖「无匹配 root」子场景（既有行为） | 在 EV/卡加脚注区分「注册根物理缺失/替换（Error）」与「无匹配注册根（Skipped，既有）」；非本卡缺陷 | open（非阻断） |
| P3-09 | P3 | `verification/.../EV.md` §1/§6 | EV 只写「零契约（0 UNFREEZE / 18 pins）」而未复述支撑该判定的 **C-17 §5.3 主体解释**（fail-closed 的主体是 target 自己的 registry，同路径 sibling revoked 行不是 target 的 registry）——该前提在 scope review §2.3/D-2 与卡 S-2；缺此引用时「为何不需要 C-17 UNFREEZE」在证据内不可自证 | scope review `:241-248`、`:491`；卡 S-1/S-2；EV §1 | EV 在 AC-SER-5/§6 引用 scope review §2.3/D-2，明确该解释是 0-pin 的前提；不改变任何字节 | open（非阻断） |

**处置建议**：P3-01/02/03 建议随 closeout 一次性重生成证据容器（manifest + scope 计数），避免后续审计反复解释；P3-04/05/06/08/09 属文档/测试精度，可在 next-touch 时修；P3-07 建议 Lead 在 closeout 补登裁决来源。**以上均不阻断集成，也不影响任何 AC 判定。**

## 6. 结论与复审

- **verdict：`approved`**（P0=0 / P1=0 / P2=0 / P3=9）。实现忠实于冻结卡面与 scope review 的 Host-only 形状：枚举 target 用自身已核验的 live `(registry_id, generation)` 执行，非枚举语义零变化，fail-closed 矩阵与「不回落 sibling」保持，无自动授权/identity 重建/registry 结构写，零契约（C15/C16/C17 零漂移、`PROTOCOL_MINOR=3`、pins 18/18）。
- **集成建议（Lead）**：①在同一 gated 测试上复跑 before/after（Owner 复现命令见 EV §7），确认 `error→ok`、`scan_frames=1`、wire 无路径；②在集成 head 重跑全量 pytest/.NET 与 pins/check/API（本卡报告只承诺 Owner head 的实测与日志交叉核对）；③closeout 时按 P3-01/02/03 重生成 manifest/scope 计数并保留「容器不自哈希」说明；④卡/Handoff/EV 保留 Run 面与 B2/folder/L-S4-1/L-R1 limitation 原字节口径。
- **剩余风险**：`backoff` 使「同会话先 error 后恢复」可能延迟（已登记，不属本卡）；Run 面同根因未修（另卡 `L-S4-B-2-RUN-RANGE-RESOLVE`，若复现）；revoked 行累积为 B1 既有；P3-06 的 fixture 脆弱性不影响当前 AC 证据（gated 为权威）。
- **复审规则**：本 Review 只对 `reviewed_head=bcc88e4a2`（+ 证据 `0c1390b2a`）有效；head 改变或出现新 Review 后本文件自动属于历史记录。

## 7. 真实性声明

1. **独立上下文**：本报告由 fresh-context 子 agent（session `9403610b-6c79-40c8-bc92-18cab8d177fc`）产出，未参与本卡实现/返修/scope review；只读交付字节。
2. **实跑**：§2.E 表中标注「我实测」的项目均为本会话现场执行（EXIT 与数字见正文）；gated 真 IPC 使用真实 `C:/Python314/python.exe` Core 与仓库外 fixture 根，产生新 fixture `scan-de38e1d8…`，未写 tracked 证据。
3. **NOT_RUN**：全量 pytest、全量 .NET（仅核对 Owner 日志合计与逐项目计数）；Run 面（`RunSourceRange`）任何测试/IPC；folder/B2/L-S4-1/L-S4-2/L-R1；真实用户数据/回收站/AppData；`git push`；`git add/commit`；契约 byte-level 复核（本卡零契约，以 blob/pins 为证）。
4. **破坏性复跑**：仅临时改 `SourceScanScheduler.cs`（2 个破坏点），每次原字节回写 + sha256 复核 + `git diff --quiet`，最终 sha 与 HEAD blob 一致；过程披露见 §4.3（一次恢复脚本语法失败 + 增量构建陷阱）。未改任何测试/证据/卡/契约。
5. **写入面**：除本报告 `doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-r1.md` 外，未在仓库内写任何文件；备份/临时状态只在仓库外 `G:\CODEX\New Manga.workspace\FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1\`。最终复核时出现的未跟踪占位卡与 `STATUS/PLAN/LEDGER/卡面` 修改均为并发 Agent（Lead closeout）写入，非本审查产物，我未修改。
6. **证据复算**：manifest 19/19 与 3 个交付文件 sha256 我全部重算匹配；判别性 6/6 日志与脚本自洽，且我独立复现了其中 2 个等价破坏点。
7. **不夸大**：本报告不把本卡读成「Run 面恢复/自动恢复/自愈/自动重新授权/撤销后自动放行」；只确认「B1 显式动作之后、枚举 target 的扫描执行面在下一个未被 backoff 抑制的 tick 恢复」。
