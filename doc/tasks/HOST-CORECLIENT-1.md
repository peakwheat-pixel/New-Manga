---
id: HOST-CORECLIENT-1
title: S1 C# Host/CoreClient——spawn 双 sidecar + JSON-lines + 中文零乱码 + 失败可诊断
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: avalonia-spike
reviewer: dsh
depends_on: [DISPLAY-PERF-DECISION-1]
base_commit: a93f20c7b
branch: task/HOST-CORECLIENT-1
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-CORECLIENT-1
integration_commit: 9126090eb
delivery_head: c1efb938f5b12c989b406316a8eabd62e0a34a6a
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/HOST-CORECLIENT-1
allowed_paths:
  - doc/tasks/HOST-CORECLIENT-1.md
  - doc/handoffs/HOST-CORECLIENT-1-handoff.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/HOST-CORECLIENT-1/**
  - G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/**
  - G:/CODEX/New Manga.workspace/worktrees/HOST-CORECLIENT-1/**
---

# HOST-CORECLIENT-1：S1 Host 与 CoreClient

## 来源与目标

依据 [AD-002](../AD-002_TARGET_DESKTOP_ARCHITECTURE.md)、[ADR-0001](../design/ADR-0001_REPO_LAYOUT_AND_COEXISTENCE.md)、[EXECUTION_DIRECTIVE_AD002_V2](../design/EXECUTION_DIRECTIVE_AD002_V2.md) §8；S0 spike 已 **GO**（`verification/DISPLAY-PERF-DECISION-1/spike/SPIKE_REPORT.md`）。

目标：在 `apps/desktop-avalonia/` 建立 C# 工程骨架，实现与既有 Python Core 的 stdio 通信层，跑通 `core.ping` 与 `list_books`，并保证中文零乱码、sidecar 启动失败可诊断（不 panic）。

## Acceptance Criteria

- [x] **AC1 工程骨架**：`apps/desktop-avalonia/NewManga.sln` + `src/NewManga.App`（Avalonia）+ `src/NewManga.Host` + `src/NewManga.CoreClient` + `src/NewManga.Theme` + `tests/`（xunit + Avalonia.Headless）；`dotnet build -warnaserror` 通过；发布配方按 spike：`PublishSingleFile + SelfContained + PublishTrimmed + IncludeNativeLibrariesForSelfExtract + ReadyToRun + 压缩`。 <<MET>>
- [x] **AC2 双通道**：`CoreClient` 以 `Process` spawn **两个** sidecar —— `host_bridge`（wire v1：issue/resolve/revoke）与 `core_service`（protocol 2.3：`core.ping`/`ListBooks`）；`CREATE_NO_WINDOW`；stdio 单行 JSON；非 ASCII 一律 `\uXXXX` 转义。 <<MET>>
- [x] **AC3 功能与编码**：`core.ping` 返回 ready；`list_books` 返回真实书架；**中文书名往返**（至少 `雾港来信・日本語テスト`）且抓**原始 wire 字节**证明 `\uXXXX`；原始 UTF-8 负例复现 `UNKNOWN`（与 spike 结论一致）。 <<MET>>
- [x] **AC4 失败可诊断（不得 panic）**：sidecar 路径缺失/启动失败/启动超时/令牌完整性异常（子进程 IL 与父不一致）→ 记录 stderr 到文件、返回 typed 错误、UI 可显示；不需要提权即可运行（AC11：非提权测试用无标签副本）。 <<MET>>
- [x] **AC5 共存约束**：按 ADR-0001 实现全局单实例 Mutex `Global\NewManga.Host`；启动检测旧壳 `new-manga.exe` 存在时进入只读/提示（二选一并测试）；S2 parity 前对生产数据只读；首次运行备份。 <<MET>>
- [x] **AC6 门禁**：`check.ps1 -TaskPath` PASS；`dotnet build/test` 绿；旧壳 `vitest` 基线不受影响（60 文件/567 用例）；中文 IPC 证据入库；无控制台窗口泄漏；lifecycle v3 AC 标记与证据 pin 齐全。 <<MET>>
- [x] **AC7 交接**：Handoff（`doc/handoffs/HOST-CORECLIENT-1-handoff.md`）+ 可复跑命令 + 未完成项；record decision 段（协议字段映射、错误码映射、sidecar 发现顺序）。 <<MET>>

## 允许修改范围

- `apps/desktop-avalonia/**`（新工程）、本 Task 卡、Handoff、STATUS/PLAN/LEDGER 指针、`verification/HOST-CORECLIENT-1/**`、workspace task-env/worktree。
- 只读引用：`apps/desktop/src-tauri/src/{core_bridge.rs,library_bridge.rs,main.rs}`、`doc/AD-002*`、`doc/design/ADR-*`、`verification/DISPLAY-PERF-DECISION-1/**`。

## 禁止范围

- **不得修改旧壳** `apps/desktop/**`（S5 才退役）；不得修改 Python Core（`src/**`）、`requirements*.txt`、AD-002/ADR、旧前端。
- 不得 push main；不得 gc/prune；不得动受保护资源。
- 不得引入商业字体；依赖需核许可并登记 `THIRD_PARTY_LICENSES.md`（若新增）。
- 不得把 sidecar 的 OS 绝对路径暴露给 UI 层。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 构建 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/build.ps1` | .NET SDK 9.0.308 / Avalonia 11.3.22 | PASS（0 警告 0 错误，`-warnaserror`） | E1 |
| AC1 发布 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/publish.ps1` | Release win-x64 单文件 | PASS（1 文件 27.64 MiB ≤ 45 MiB） | E5 |
| AC2/AC3/AC4/AC5 全量（**一条命令**） | **`pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1`**：自备 AC11 无标签副本 → 导出 `NEWMANGA_CORECLIENT_SIDECAR_DIR`/`NEWMANGA_EVIDENCE_DIR` → `dotnet build -warnaserror` → 三个项目分别跑并写确定性 TRX | Windows 11，无需管理员 | **PASS：57 passed / 0 skipped / 0 failed** | E2、E3a–c、E18 |
| AC6 可复现性（**无 fixture env**） | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test-without-fixture.ps1`（等价于裸 `dotnet test apps\desktop-avalonia\NewManga.sln`） | 清空 `NEWMANGA_CORECLIENT_SIDECAR_DIR` | **PASS：45 passed / 12 skipped / 0 failed**；12 条 skip 均带 `reason: needs sidecar fixture …`（CoreClient 8 + Host 4） | E16、E17 |
| AC3 中文 + wire hex | 上述一条命令中的 `ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped` | 隔离 data root | PASS（UTF-8 hex 相等；CreateBook 原始帧含 `5c7539366665`；ASCII-only=true） | E6 |
| AC3 原始 UTF-8 负例 | `RawUtf8Request_ReplicatesUnknownError` | 同上 | PASS（`UNKNOWN`，request_ascii_only=false） | E7 |
| AC2 bridge 授权闭环 | `Ping_IssueResolveRevoke_FullLifecycle` | catalog_loader 初始化 + 播种 `res-1` | PASS（resolve 字段齐全；撤销后 `REF_REVOKED`；未知资源 `RESOURCE_NOT_CATALOGED`；走私 `rel_path` → `REF_MALFORMED`） | E8 |
| AC4 缺失/超时/生成失败 | `SidecarFailureTests`（4 场景） | 同上 | PASS（typed code + stderr 文件存在） | E9 |
| AC5 单实例 | `SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars` | Local 唯一名 + 真 Mutex | PASS（`HOST_ALREADY_RUNNING`，未 spawn） | E11 |
| AC5 旧壳共存 | `LegacyShellRealTests`（真 `new-manga.exe` 副本进程） | Windows 11 真进程探测 | PASS（检测→`ReadOnlyLegacyShellRunning`，写被拒） | E12 |
| AC5 只读/备份 | `HostRuntimeIntegrationTests` + `DataSafetyTests` | 隔离 data root | PASS（parity 前写被拒；首次运行 catalog 备份幂等） | E10 |
| AC6 旧壳回归 | `npx vitest run`（`apps/desktop/frontend`） | 旧前端依赖已装 | PASS（60 文件 / 567 用例） | E4 |
| AC6 无控制台 + 端到端 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/smoke.ps1` | 发布 exe + sidecar 副本 + 隔离 data root | PASS（window 373.5 ms；console 窗口 0；退出后无残留 sidecar） | E13、E14 |
| AC6 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/HOST-CORECLIENT-1.md` | 本 worktree | PASS | 本卡 Canonical Evidence |
## 依赖、风险与阻塞

- `depends_on`：DISPLAY-PERF-DECISION-1（S0 GO 已达成）。
- 风险 1：cp936 编码坑（历史事故）→ AC3 用原始字节验证；已定位为冻结 sidecar 以 ANSI(936) 读 stdin，故非 ASCII 必须 `\uXXXX`。
- 风险 2：sidecar 启动路径（packaged 目录 vs 仓库树）→ 用无标签副本 + 隔离 env；发现顺序见 Handoff record decision。
- 风险 3：57/66 命令面差异 → S2 才需 parity，本 Task 只跑通两个通道；Host 只读策略覆盖该差异期。
- 风险 4：单实例 Mutex 与旧壳无协作 → 检测进程并降级只读（已真机测试）。
- 风险 5：`Global\` 互斥需 `SeCreateGlobalPrivilege`，标准用户可能没有 → 已实现 `Local\NewManga.Host` 回退（数据根本来就是按用户隔离）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E1-build | AC1/AC6 | verification/HOST-CORECLIENT-1/build/dotnet-build-Debug.log | c1efb938f5b12c989b406316a8eabd62e0a34a6a | b64f1e8079711150ef9b3caf8d28f3dc28e62550b6eaed2ce6f4975bf9be8a9c | CANONICAL |
| E2-test-log | AC2/AC3/AC4/AC5/AC6 | verification/HOST-CORECLIENT-1/test/dotnet-test-Debug.log | c1efb938f5b12c989b406316a8eabd62e0a34a6a | e027f355d195b5221dd1719001f149a7e09bc42a7711afe11a7458e4ac011657 | CANONICAL |
| E3a-trx-coreclient | AC2/AC3/AC4/AC6 | verification/HOST-CORECLIENT-1/test/results-coreclient.trx | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 3b18a3f97ce58f5ee432cc4841e59e5f5a55fc87882c30d4f77f60fa2ff9a530 | CANONICAL |
| E3b-trx-host | AC2/AC5/AC6 | verification/HOST-CORECLIENT-1/test/results-host.trx | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 79d6904cf38eff6b75b93c4c205afd29ac91dae847156ae3eb86d1d103eb1215 | CANONICAL |
| E3c-trx-app | AC1/AC6 | verification/HOST-CORECLIENT-1/test/results-app.trx | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 1817d1836591d7e06f1b5c97dacd0b55dffe60440bd73e0043dd1c23f66e3d89 | CANONICAL |
| E4-vitest | AC6 | verification/HOST-CORECLIENT-1/test/vitest-baseline.log | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 8879a2097807f6388880344f0026caab119128bccbeb35d04ca9faffe03b43a2 | CANONICAL |
| E5-publish | AC1 | verification/HOST-CORECLIENT-1/publish/publish_files.json | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 00d5ec9b5a09fc0d921701049817e17bf87a405a491c71b3184569f97ba40000 | CANONICAL |
| E6-cn-roundtrip | AC2/AC3 | verification/HOST-CORECLIENT-1/wire/core-chinese-roundtrip.json | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 9a24c58d6ad5e50c622901fb63b6484c6248af50b1f1d3c5cb9b4313ac02d9c9 | CANONICAL |
| E7-utf8-negative | AC3 | verification/HOST-CORECLIENT-1/wire/core-raw-utf8-negative.json | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 611962501be106ce97c22a0c6cc3ac7c157d7c691c1378eb44b25834d64ca084 | CANONICAL |
| E8-bridge | AC2/AC4 | verification/HOST-CORECLIENT-1/wire/host-bridge-lifecycle.json | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 43ea607c88ef39b12fd11567fb8c4695edd17f0e4beebc8ab393ed66d2af9e76 | CANONICAL |
| E9-diagnostics | AC4 | verification/HOST-CORECLIENT-1/diagnostics/startup-timeout.json | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 95a65b02f59bd9d5259d3fe0f81839c99d6ba872c7461c0710eff8c9e2d4dbf7 | CANONICAL |
| E10-host-readonly | AC5 | verification/HOST-CORECLIENT-1/host/runtime-readonly.json | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 855710ca4f5b6c4e61e705f50c735781ec1b496fd93ff15bb35f8b5c8f954790 | CANONICAL |
| E11-single-instance | AC5 | verification/HOST-CORECLIENT-1/host/second-instance.json | c1efb938f5b12c989b406316a8eabd62e0a34a6a | de8aaf4da3c9e7bc81fc4d9af63ae46ca959b3ab68c9209775705a6e92eefee0 | CANONICAL |
| E12-legacy-shell | AC5 | verification/HOST-CORECLIENT-1/legacy-shell/runtime-readonly.json | c1efb938f5b12c989b406316a8eabd62e0a34a6a | ef4301465315daf4a7edef6d70b66512fbcba9db5277c8cecc549fc59fdd468f | CANONICAL |
| E13-smoke | AC6 | verification/HOST-CORECLIENT-1/smoke/smoke.json | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 3cb09e935ea897a2cb8b96b53c9fd3e678b1786cfe6b1a739e6b02b8187c5021 | CANONICAL |
| E14-smoke-window | AC6 | verification/HOST-CORECLIENT-1/smoke/window.png | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 6634709274fdfbecb0a399d284f5113baf8f3cb7eabbaba60c2fa7b8c6604741 | CANONICAL |
| E15-manifest | 全 AC | verification/HOST-CORECLIENT-1/MANIFEST.json | c1efb938f5b12c989b406316a8eabd62e0a34a6a | d7478ceba5112dd7dbc524ef3862c64e7217d6693816abac2d36ae0b7f6aad13 | CANONICAL |
| E16-no-fixture-log | AC6 | verification/HOST-CORECLIENT-1/test/dotnet-test-Debug-no-fixture.log | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 48c365afea673d4a696ad4f1a99d3d637b4a4a03f571172014a3548aede7920c | CANONICAL |
| E17-no-fixture-summary | AC6 | verification/HOST-CORECLIENT-1/test/no-fixture-summary.json | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 18f1bca63c095645d63e3d4e6c4fb32e50f4d3f80d6e3a2faf6d0ea7a73ffb4d | CANONICAL |
| E18-test-summary | AC2/AC6 | verification/HOST-CORECLIENT-1/test/summary.json | c1efb938f5b12c989b406316a8eabd62e0a34a6a | 0535aff85784df6f04c62581895f9a627837c04b482961cb0df1a14c34ab6207 | CANONICAL |
| X1-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-legacy-running/wire/core-service.ndjson | 9126090eb | ef9b3d2c54d0dc062db4122b45f0eeb00d45402f672e24031c1b597b9b74eb62 | SOURCE_PIN |
| X2-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-legacy-running/wire/host-bridge.ndjson | 9126090eb | 88d830761d9bfbc5fed36ea886606c3e5f38c781d9bcc2366aa84c25c0581f67 | SOURCE_PIN |
| X3-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-missing-sidecar/host.log | 9126090eb | bba61a9a99a0bc9d2495eb8c806f628e58229798361aa894ab4827dab8556325 | SOURCE_PIN |
| X4-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-parity-roundtrip/core_service.stderr.log | 9126090eb | abf57e1da3e4af542b5ffdb02a33419836eff04a8efed71d8867ab2029c2672f | SOURCE_PIN |
| X5-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-parity-roundtrip/host_bridge.stderr.log | 9126090eb | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| X6-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-parity-roundtrip/host.log | 9126090eb | 3f1604a2f178ded4ffa5b036c966b33270ce0ce494799cff7eb6fdadb1690a84 | SOURCE_PIN |
| X7-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-parity-roundtrip/wire/core-service.ndjson | 9126090eb | a46eaf26c1ec6430a7cff7086af8c0e6dc838d6be08c0c13e59baabd3901c116 | SOURCE_PIN |
| X8-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-parity-roundtrip/wire/host-bridge.ndjson | 9126090eb | 02b5f54421b6a4d054f84267e740b5b94ddaabff923582d3f6efd466f39aa252 | SOURCE_PIN |
| X9-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-readonly/core_service.stderr.log | 9126090eb | 1d3a102e47b2e054d0e33783807c508e1c473cf17aee6263d74355e5dc64349c | SOURCE_PIN |
| X10-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-readonly/host_bridge.stderr.log | 9126090eb | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| X11-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-readonly/host.log | 9126090eb | 95d378d27ad096e21c3bed146ba6715014b34182031546c180deeade7819408b | SOURCE_PIN |
| X12-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-readonly/wire/core-service.ndjson | 9126090eb | 3c3c47aafeeb0596e75db5765baddc51cf7d58cf34408a1b0668a23721085602 | SOURCE_PIN |
| X13-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-readonly/wire/host-bridge.ndjson | 9126090eb | 919d4780ca4c9cd46b9b031cc2560833fb11ea4e1624ec78ba51f9ed4d326215 | SOURCE_PIN |
| X14-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-second-instance/host.log | 9126090eb | 5d8fe660f8f7bca9585afdbf81d610acf67ca6d012d9e9958177bda7ea43e7b3 | SOURCE_PIN |
| X15-src | AC4/AC5 | verification/HOST-CORECLIENT-1/legacy-shell/detected.json | 9126090eb | 3250dbf34df47e259458f5cd28be03b0fc811359e505eb3173fde9d6a8fd632c | SOURCE_PIN |
| X16-src | AC4/AC5 | verification/HOST-CORECLIENT-1/logs/bridge-errors/host_bridge.stderr.log | 9126090eb | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| X17-src | AC4/AC5 | verification/HOST-CORECLIENT-1/logs/bridge-lifecycle/host_bridge.stderr.log | 9126090eb | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| X18-src | AC4/AC5 | verification/HOST-CORECLIENT-1/logs/bridge-wire/host_bridge.stderr.log | 9126090eb | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| X19-src | AC4/AC5 | verification/HOST-CORECLIENT-1/logs/core-chinese/core_service.stderr.log | 9126090eb | dd67e0045d2a5048a87d54a4b6f9260aabf29c4a481a0fac362166896bd274c9 | SOURCE_PIN |
| X20-src | AC4/AC5 | verification/HOST-CORECLIENT-1/logs/core-ping/core_service.stderr.log | 9126090eb | e6daaada8a898a50d256c415d2ff405cc186c2d5a32b044e235e559a290ac148 | SOURCE_PIN |
| X21-src | AC4/AC5 | verification/HOST-CORECLIENT-1/logs/core-raw-utf8/core_service.stderr.log | 9126090eb | a82a4e69d1aa0a891a7add2d457fb340bfa0b409610991b43d577236d4036c49 | SOURCE_PIN |
| X22-src | AC4/AC5 | verification/HOST-CORECLIENT-1/logs/core-wire-shape/core_service.stderr.log | 9126090eb | 53a6e286b32bcb84a4a5159c91b9307e095cc99fbc561309af16f76b4d2fd003 | SOURCE_PIN |
| X23-src | AC4/AC5 | verification/HOST-CORECLIENT-1/logs/failure-request-timeout/fake.stderr.log | 9126090eb | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| X24-src | AC4/AC5 | verification/HOST-CORECLIENT-1/logs/failure-startup-timeout/core_service.stderr.log | 9126090eb | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| X25-src | AC4/AC5 | verification/HOST-CORECLIENT-1/publish/publish.log | 9126090eb | c298bc6aa063f85f7dbea13f37db8934a320c3485d67eed71e11ffce9e10283b | SOURCE_PIN |
| X26-src | AC4/AC5 | verification/HOST-CORECLIENT-1/smoke/host.log | 9126090eb | d4767928e62d2beb94621eae7ebdae27981669eb0f353cfd60e3f2e3604e076c | SOURCE_PIN |
| X27-src | AC4/AC5 | verification/HOST-CORECLIENT-1/smoke/wire/core-service.ndjson | 9126090eb | 9fdc0b98040aae8ae12a9717bff62080047151223ed80afad3f0dd4459542f89 | SOURCE_PIN |
| X28-src | AC4/AC5 | verification/HOST-CORECLIENT-1/smoke/wire/host-bridge.ndjson | 9126090eb | f0eadf6df1ad246fb9051864c3b4faca483a1a6a80076d782b8cac6fa15481e3 | SOURCE_PIN |
| X29-src | AC4/AC5 | verification/HOST-CORECLIENT-1/wire/bridge-errors.ndjson | 9126090eb | caa0389bb21dc0fd7565999b5069b275c8768f4c2fbf596e16ec4564889a651e | SOURCE_PIN |
| X30-src | AC4/AC5 | verification/HOST-CORECLIENT-1/wire/bridge-lifecycle.ndjson | 9126090eb | e6a3dc44a9c9f2e2eb469092e04ccbdcd6483eb54cab95ab24a66d2c31d8a4db | SOURCE_PIN |
| X31-src | AC4/AC5 | verification/HOST-CORECLIENT-1/wire/bridge-wire.ndjson | 9126090eb | d80f888b9fd2efaee31e83646f0648ac68add7fdf1d2b20f6ef44eaef35d6bc8 | SOURCE_PIN |
| X32-src | AC4/AC5 | verification/HOST-CORECLIENT-1/wire/core-chinese.ndjson | 9126090eb | 1808e9d7862bdc4037033dc36ba167258369ab4535e159fabb8b43f6ef93c6fd | SOURCE_PIN |
| X33-src | AC4/AC5 | verification/HOST-CORECLIENT-1/wire/core-ping.json | 9126090eb | 7d466bb22deba069a8f4bd303fef84709721c0802f24cd6e2e69afe39f026812 | SOURCE_PIN |
| X34-src | AC4/AC5 | verification/HOST-CORECLIENT-1/wire/core-ping.ndjson | 9126090eb | 71239e07f27888f44f5c2b4946c4891ef90733e611511ec57b0797aa0e1bc3ee | SOURCE_PIN |
| X35-src | AC4/AC5 | verification/HOST-CORECLIENT-1/wire/core-raw-utf8.ndjson | 9126090eb | cf3c7e4653d00401c2bcf50820dd9c164723fbeceea5765cbf092a30032edb42 | SOURCE_PIN |
| X36-src | AC4/AC5 | verification/HOST-CORECLIENT-1/wire/core-wire-shape.json | 9126090eb | 818f1ceae873300662f4c0641120e4d4724e948ee0e2ad076cd2bbf442eeaaa0 | SOURCE_PIN |
| X37-src | AC4/AC5 | verification/HOST-CORECLIENT-1/wire/core-wire-shape.ndjson | 9126090eb | 73110ffecc4041fc5e81318ed7382b9911c1cf6b7160612f4ab91c1084d3079c | SOURCE_PIN |
| X38-src | AC4/AC5 | verification/HOST-CORECLIENT-1/wire/host-bridge-errors.json | 9126090eb | fc7ffa5f88e93247b725eb04c6a9d0cd356a9c029aef6fc12437cd3b537cf86a | SOURCE_PIN |
| S1-src | AC4/AC5 | verification/HOST-CORECLIENT-1/diagnostics/missing-exe.json | 9126090eb | 4594512db61c9500844d52d13c3b289c0322cdfed7dc471e8f3a1eac425391dd | SOURCE_PIN |
| S2-src | AC4/AC5 | verification/HOST-CORECLIENT-1/diagnostics/request-timeout.json | 9126090eb | d92e4e444d02eda85d8f361a1d140e43d818429a18ea7c3244dc82df40d76269 | SOURCE_PIN |
| S3-src | AC4/AC5 | verification/HOST-CORECLIENT-1/diagnostics/spawn-failed.json | 9126090eb | d328eb1713bbede1e76649b4474c555dfbde7c72e00736d1828a2118afc6760b | SOURCE_PIN |
| S4-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host/runtime-chinese-roundtrip.json | 9126090eb | 344024d1ddb450ab1e3e32b328208c909b4405def1077f867f458e04c7151b28 | SOURCE_PIN |
| S5-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host/runtime-missing-sidecar.json | 9126090eb | 294565828007d46dca8cba7ce0f2705cf89cb7e20f55d45e3dbb0c68420ae74e | SOURCE_PIN |
| S6-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-legacy-running/core_service.stderr.log | 9126090eb | 1aaa98de18b87e2e91b379133ed6451d473604d1edf09b833232ce7d8cffff06 | SOURCE_PIN |
| S7-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-legacy-running/host_bridge.stderr.log | 9126090eb | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 | SOURCE_PIN |
| S8-src | AC4/AC5 | verification/HOST-CORECLIENT-1/host-logs/runtime-legacy-running/host.log | 9126090eb | 4cc416ef39002c3258ee6b7d71f70a2965921c00a4e578716c427d14a1b6e112 | SOURCE_PIN |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1 | d7478ceba5112dd7dbc524ef3862c64e7217d6693816abac2d36ae0b7f6aad13 | 本 Task 集成前保留：无标签 sidecar 副本供复跑测试；未删除、未移动。关闭时由 DSH 复核。 |

## Review（DSH 集成复核，2026-10-27）

结论：**changes_requested**（2 项修复后才能 done）：

1. **AC6 测试可复现性**：DSH 集成后跑 `dotnet test apps\desktop-avalonia\NewManga.sln` → `NewManga.App.Tests` 4/4 通过，但 `NewManga.CoreClient.Tests` **23 passed / 8 failed**，失败全在 `CoreServiceIntegrationTests`（Ping、中文往返、UTF-8 负例、wire 帧）。交付声称 57/57 但**没有给出可复现的单一命令/环境**。要求：集成测试在 sidecar fixture 缺失时显式 `Skip` 写明原因，或提供带环境变量的一键命令写入 Handoff；"一条命令 57/57"必须成立。
2. **E3-trx 证据 pin 陈旧**：pin 值（`68b5c79e…`）与合并后实际产物（`354c7b26…`）不一致——文件在 pin 之后被重写 → `check.ps1` SHA-256 校验 FAIL。DSH 已临时改为当前全量哈希；**重跑测试后必须重新 pin 最终产物**，且 pin 之后不得再重写证据文件。

其余通过：分支仅新增 `apps/desktop-avalonia/**` 与 `verification/HOST-CORECLIENT-1/**`（未触碰旧壳/Python Core）；wire 证据含 `5c75` 转义与 ASCII-only；AC11 无标签副本规则遵守。修复后 DSH 复跑单命令 + `check.ps1` 通过即 done。

## Fix Record（2026-10-27，avalonia-spike）

回应 Review 的两项 `changes_requested`：

1. **单命令可复现（AC6）**
   - 一条命令：`pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1`。脚本自动准备 AC11 无标签 sidecar 副本、导出 `NEWMANGA_CORECLIENT_SIDECAR_DIR`/`NEWMANGA_EVIDENCE_DIR`、执行 `dotnet build -warnaserror`，再按项目分别跑并写确定性 TRX 与 `test/summary.json`。实测 **57 passed / 0 skipped / 0 failed**（E2、E3a–c、E18）。
   - 裸 `dotnet test apps\desktop-avalonia\NewManga.sln`（无 fixture env）不再失败：新增 `[SidecarFact]`/`[HostSidecarFact]`，fixture 缺失时显式 `Skip("reason: needs sidecar fixture …")`。实测 **45 passed / 12 skipped / 0 failed**，12 条 skip 全部携带原因（CoreClient 8 + Host 4），见 E16/E17。
   - 对“8 个失败”的真实状态说明：它们就是这 8 条需要 fixture 的 CoreClient 集成测试；无 env 时原实现抛 fixture 异常（故失败）。在有 fixture 时它们**真实执行并通过**（非跳过），本次一条命令 57/57 即证。
2. **E3-trx pin 陈旧**
   - 原因：旧单一 `results-Debug.trx` 会在之后重跑时被重写，pin 随之失效。现改为每项目独立 TRX（`results-coreclient.trx`/`results-host.trx`/`results-app.trx`），全部以**完整 64 hex SHA-256** pin 到交付提交（E3a–c）；`test/summary.json` 同时记录三条 TRX 的 sha256 与计数。
   - 本次 pin 之后未再重写任何证据文件；修复提交（代码+证据）为 `c1efb938f5b12c989b406316a8eabd62e0a34a6a`，本卡 pin 即指向该提交。

4. **复跑不覆盖 pin**：`scripts/test.ps1` / `scripts/test-without-fixture.ps1` 默认把证据写到 `G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/evidence-rerun`，只有显式 `-CanonicalEvidence` 才会重生成仓内 pinned 证据。DSH 复跑上面一条命令实测 57 passed / 0 skipped，且 `git status verification/HOST-CORECLIENT-1` 干净（pin 字节未被触碰）。
改动文件：`tests/**/Support/{SidecarFixture,HostFixture}.cs`（新增 `TryGetSidecarDirectory`）、新增 `SidecarFactAttribute.cs`/`HostSidecarFactAttribute.cs`、8+4 条集成测试改为可跳过属性、`scripts/test.ps1`（一条命令 + 确定性 TRX + summary）、新增 `scripts/test-without-fixture.ps1`、`verification/HOST-CORECLIENT-1/**`（重跑证据 + MANIFEST）、本卡与 Handoff。
## Closeout Record

- Closeout date / DSH：2026-10-27 DSH（作者 avalonia-spike，reviewer dsh；author≠reviewer）。
- canonical_evidence_status：`complete`（E1–E18 + S1–S8 SOURCE_PIN，共 28 条；TRX 已按合并后产物重钉）。
- resource_closeout_status：`complete`（task-env 无标签副本 ~1GB 按 PRESERVE_REFERENCED 保留，删除需另行授权）。
- 删除、迁移、归档数量/字节数：0（仅新增 `apps/desktop-avalonia/**` 与 `verification/HOST-CORECLIENT-1/**`；workspace 新增无标签副本目录）。
- 未关闭项及保留原因：S2 命令 parity 未做（按 Task 范围留待 S2）；`Global\` 回退 `Local\` 已在 Handoff 记录；IL 不一致分支仅单测覆盖（子进程天然继承父 IL）。
- 当前指针清理：STATUS 指向 S2；PLAN/LEDGER 同步；集成 9126090eb。

## Review 2（DSH 集成复核，2026-10-27）— PASS

- 单命令验收：pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1 → **57 passed / 0 skipped / 0 failed**（证据写 workspace evidence-rerun，不覆盖仓内 pin）。
- 裸跑合同：无 fixture 时 45 passed / 12 skipped / 0 failed，12 条 skip 均带 
eeds sidecar fixture 原因（已抽查 ScriptFact/HostSidecarFact 属性）。
- 证据 pin：per-project TRX 与 MANIFEST 均为完整 64-hex；旧单一 
esults-Debug.trx 已删除，与卡内 E 表一致。
- 集成：分支 	ask/HOST-CORECLIENT-1 合入 main；范围仅 pps/desktop-avalonia/** + erification/HOST-CORECLIENT-1/** + 文档；未改旧壳/Python Core。
- 结论：**修复验收 PASS**（closeout 下一轮完成）；
esource_closeout_status=complete（~1GB 无标签 sidecar 副本按 PRESERVE_REFERENCED 保留，删除需另行授权）。
