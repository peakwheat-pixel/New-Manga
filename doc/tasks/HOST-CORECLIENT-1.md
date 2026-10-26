---
id: HOST-CORECLIENT-1
title: S1 C# Host/CoreClient——spawn 双 sidecar + JSON-lines + 中文零乱码 + 失败可诊断
kind: implementation
governance_version: 3
status: changes_requested
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: avalonia-spike
reviewer: dsh
depends_on: [DISPLAY-PERF-DECISION-1]
base_commit: a93f20c7b
branch: task/HOST-CORECLIENT-1
worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-CORECLIENT-1
integration_commit: null
delivery_head: eb123ad4f7e758010ee6597f276c34b6c9807e26
canonical_evidence_status: pinned
resource_closeout_status: pending
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
| AC1 构建 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/build.ps1` | .NET SDK 9.0.308 / Avalonia 11.3.22 | PASS（0 警告 0 错误，`-warnaserror`） | `verification/HOST-CORECLIENT-1/build/dotnet-build-Debug.log` |
| AC1 发布 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/publish.ps1` | Release win-x64 单文件 | PASS（1 文件 27.64 MiB ≤ 45 MiB） | `verification/HOST-CORECLIENT-1/publish/publish_files.json` |
| AC2/AC3 双通道 | `dotnet test`：`CoreServiceIntegrationTests` + `HostBridgeIntegrationTests` | 无标签 sidecar 副本（`task-envs/HOST-CORECLIENT-1/sidecar-copy`） | PASS（57 用例全绿） | `verification/HOST-CORECLIENT-1/test/dotnet-test-Debug.log` |
| AC3 中文 + wire hex | `ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped` | 同上 + 隔离 data root | PASS（UTF-8 hex 相等；CreateBook 原始帧含 `5c7539366665`） | `verification/HOST-CORECLIENT-1/wire/core-chinese-roundtrip.json` |
| AC3 原始 UTF-8 负例 | `RawUtf8Request_ReplicatesUnknownError` | 同上 | PASS（`UNKNOWN`，request_ascii_only=false） | `verification/HOST-CORECLIENT-1/wire/core-raw-utf8-negative.json` |
| AC2 bridge 授权闭环 | `Ping_IssueResolveRevoke_FullLifecycle` | catalog_loader 初始化 + 播种 `res-1` | PASS（resolve 字段齐全；撤销后 `REF_REVOKED`；未知资源 `RESOURCE_NOT_CATALOGED`） | `verification/HOST-CORECLIENT-1/wire/host-bridge-lifecycle.json` |
| AC4 缺失/超时/生成失败 | `SidecarFailureTests`（4 场景） | 同上 | PASS（typed code + stderr 文件存在） | `verification/HOST-CORECLIENT-1/diagnostics/startup-timeout.json` |
| AC5 单实例 | `SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars` | Local 测试名 + 真进程互斥 | PASS（`HOST_ALREADY_RUNNING`，未 spawn） | `verification/HOST-CORECLIENT-1/host/second-instance.json` |
| AC5 旧壳共存 | `LegacyShellRealTests`（真 `new-manga.exe` 进程） | cmd.exe 副本改名 + 真探测 | PASS（检测成功→只读、写被拒） | `verification/HOST-CORECLIENT-1/legacy-shell/runtime-readonly.json` |
| AC5 只读/备份 | `HostRuntimeIntegrationTests` + `DataSafetyTests` | 隔离 data root | PASS（parity 前写被拒；首次运行 catalog 备份幂等） | `verification/HOST-CORECLIENT-1/host/runtime-readonly.json` |
| AC6 旧壳回归 | `npx vitest run`（`apps/desktop/frontend`） | 旧前端依赖已装 | PASS（60 文件 / 567 用例） | `verification/HOST-CORECLIENT-1/test/vitest-baseline.log` |
| AC6 无控制台 + 端到端 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/smoke.ps1` | 发布 exe + sidecar 副本 + 隔离 data root | PASS（window 373.5ms；console 窗口 0；退出后无残留 sidecar） | `verification/HOST-CORECLIENT-1/smoke/smoke.json` |
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
| E1-build | AC1/AC6 | verification/HOST-CORECLIENT-1/build/dotnet-build-Debug.log | - | 2943b1f5fc6b808ce1da8537da29444833f2c3de298ee347636ea02be9131666 | CANONICAL |
| E2-test | AC2/AC3/AC4/AC5/AC6 | verification/HOST-CORECLIENT-1/test/dotnet-test-Debug.log | eb123ad4f7e758010ee6597f276c34b6c9807e26 | 4161c65553511dcd56e915c4c5264de53ebc185e303f32acee58cf5568f8c4f2 | CANONICAL |
| E3-trx | AC2/AC3/AC4/AC5 | verification/HOST-CORECLIENT-1/test/results-Debug.trx | eb123ad4f7e758010ee6597f276c34b6c9807e26 | 354c7b2699fee8009529860b2a1ad7839d2a4d9717e59bd9a4ab9f90bad8de4d | CANONICAL |
| E4-vitest | AC6 | verification/HOST-CORECLIENT-1/test/vitest-baseline.log | eb123ad4f7e758010ee6597f276c34b6c9807e26 | 8879a2097807f6388880344f0026caab119128bccbeb35d04ca9faffe03b43a2 | CANONICAL |
| E5-publish | AC1 | verification/HOST-CORECLIENT-1/publish/publish_files.json | eb123ad4f7e758010ee6597f276c34b6c9807e26 | 00d5ec9b5a09fc0d921701049817e17bf87a405a491c71b3184569f97ba40000 | CANONICAL |
| E6-cn-roundtrip | AC2/AC3 | verification/HOST-CORECLIENT-1/wire/core-chinese-roundtrip.json | eb123ad4f7e758010ee6597f276c34b6c9807e26 | 978de43ca074205f9be417fff8f5c617d057c9696f9aa663b442fa88be1be052 | CANONICAL |
| E7-utf8-negative | AC3 | verification/HOST-CORECLIENT-1/wire/core-raw-utf8-negative.json | eb123ad4f7e758010ee6597f276c34b6c9807e26 | 611962501be106ce97c22a0c6cc3ac7c157d7c691c1378eb44b25834d64ca084 | CANONICAL |
| E8-bridge | AC2/AC4 | verification/HOST-CORECLIENT-1/wire/host-bridge-lifecycle.json | eb123ad4f7e758010ee6597f276c34b6c9807e26 | 3e29eaa8bf17e2663b7d7cdb28e1ab751308bc3880f0ee437f97cb78e8a78f86 | CANONICAL |
| E9-diagnostics | AC4 | verification/HOST-CORECLIENT-1/diagnostics/startup-timeout.json | eb123ad4f7e758010ee6597f276c34b6c9807e26 | 95a65b02f59bd9d5259d3fe0f81839c99d6ba872c7461c0710eff8c9e2d4dbf7 | CANONICAL |
| E10-host-readonly | AC5 | verification/HOST-CORECLIENT-1/host/runtime-readonly.json | eb123ad4f7e758010ee6597f276c34b6c9807e26 | 855710ca4f5b6c4e61e705f50c735781ec1b496fd93ff15bb35f8b5c8f954790 | CANONICAL |
| E11-single-instance | AC5 | verification/HOST-CORECLIENT-1/host/second-instance.json | eb123ad4f7e758010ee6597f276c34b6c9807e26 | ac9bb4a7868524ad22c847ce222884c49372801ff30e74b6a22b0699735d7662 | CANONICAL |
| E12-legacy-shell | AC5 | verification/HOST-CORECLIENT-1/legacy-shell/runtime-readonly.json | eb123ad4f7e758010ee6597f276c34b6c9807e26 | ef4301465315daf4a7edef6d70b66512fbcba9db5277c8cecc549fc59fdd468f | CANONICAL |
| E13-smoke | AC6 | verification/HOST-CORECLIENT-1/smoke/smoke.json | eb123ad4f7e758010ee6597f276c34b6c9807e26 | 3cb09e935ea897a2cb8b96b53c9fd3e678b1786cfe6b1a739e6b02b8187c5021 | CANONICAL |
| E14-smoke-window | AC6 | verification/HOST-CORECLIENT-1/smoke/window.png | eb123ad4f7e758010ee6597f276c34b6c9807e26 | 6634709274fdfbecb0a399d284f5113baf8f3cb7eabbaba60c2fa7b8c6604741 | CANONICAL |
| E15-manifest | 全 AC | verification/HOST-CORECLIENT-1/MANIFEST.json | eb123ad4f7e758010ee6597f276c34b6c9807e26 | f2941cf68d676ec9d5b0c9f69e569f7824ca9143996117fe6bef4eb7dea88bb6 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1 | f2941cf68d676ec9d5b0c9f69e569f7824ca9143996117fe6bef4eb7dea88bb6 | 本 Task 集成前保留：无标签 sidecar 副本供复跑测试；未删除、未移动。关闭时由 DSH 复核。 |

## Review（DSH 集成复核，2026-10-27）

结论：**changes_requested**（2 项修复后才能 done）：

1. **AC6 测试可复现性**：DSH 集成后跑 `dotnet test apps\desktop-avalonia\NewManga.sln` → `NewManga.App.Tests` 4/4 通过，但 `NewManga.CoreClient.Tests` **23 passed / 8 failed**，失败全在 `CoreServiceIntegrationTests`（Ping、中文往返、UTF-8 负例、wire 帧）。交付声称 57/57 但**没有给出可复现的单一命令/环境**。要求：集成测试在 sidecar fixture 缺失时显式 `Skip` 写明原因，或提供带环境变量的一键命令写入 Handoff；"一条命令 57/57"必须成立。
2. **E3-trx 证据 pin 陈旧**：pin 值（`68b5c79e…`）与合并后实际产物（`354c7b26…`）不一致——文件在 pin 之后被重写 → `check.ps1` SHA-256 校验 FAIL。DSH 已临时改为当前全量哈希；**重跑测试后必须重新 pin 最终产物**，且 pin 之后不得再重写证据文件。

其余通过：分支仅新增 `apps/desktop-avalonia/**` 与 `verification/HOST-CORECLIENT-1/**`（未触碰旧壳/Python Core）；wire 证据含 `5c75` 转义与 ASCII-only；AC11 无标签副本规则遵守。修复后 DSH 复跑单命令 + `check.ps1` 通过即 done。

## Closeout Record

- Closeout date / DSH：待 DSH 集成与 ZCode 复核后填写（本卡 `in_review`）。
- canonical_evidence_status：`pinned`（15 条证据已 pin SHA-256；集成/关闭时由 DSH 收口）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：0（仅新增 `apps/desktop-avalonia/**` 与 `verification/HOST-CORECLIENT-1/**`；workspace 新增无标签副本目录）。
- 未关闭项及保留原因：S2 命令 parity 未做（按 Task 范围留待 S2）；`Global\` 回退 `Local\` 已在 Handoff 记录；IL 不一致分支仅单测覆盖（子进程天然继承父 IL）。
- 当前指针清理：已更新 STATUS/PLAN/LEDGER，指向 `in_review`。
