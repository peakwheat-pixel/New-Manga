---
task_id: HOST-CORECLIENT-1
author: avalonia-spike
recipient: DeepSeek Harness
base_commit: a93f20c7b
delivery_head: pending
status: draft
---

# Handoff：HOST-CORECLIENT-1

## 交付结果

在 `apps/desktop-avalonia/` 落地 S1 新壳工程（分支 `task/HOST-CORECLIENT-1`，base `a93f20c7b`）：

- `NewManga.sln` + 4 个 src 工程：`NewManga.App`（Avalonia 11.3.22 桌面壳）、`NewManga.Host`（生命周期/共存/数据安全）、`NewManga.CoreClient`（Python Core 双通道客户端）、`NewManga.Theme`（三皮肤运行时切换）。
- 3 个测试工程：`NewManga.CoreClient.Tests`、`NewManga.Host.Tests`、`NewManga.App.Tests`（xunit + Avalonia.Headless）。
- `scripts/{prepare-sidecar,build,test,publish,smoke}.ps1`：一键无标签副本准备、`-warnaserror` 构建、真实 sidecar 测试、S0 单文件发布配方、端到端 smoke（截图 + 无控制台 + 无残留进程）。
- 证据：`verification/HOST-CORECLIENT-1/**`（wire 原始帧 + hex、负例、typed 诊断、单实例/旧壳、发布清单、smoke、vitest 基线），清单见 `verification/HOST-CORECLIENT-1/MANIFEST.json`。

与 AC 逐项对照见 Task 卡 Canonical Evidence（E1–E15）。**未修改** `apps/desktop/**`（旧壳）与 Python Core `src/**`；未 push。

关键数字：`dotnet build -warnaserror` 0 警告 0 错误；`dotnet test` 57/57 通过（App 4 + Host 22 + CoreClient 31）；发布单文件 **27.64 MiB**（≤45 MiB）；smoke 窗口可见 **373.5 ms**、控制台窗口 **0**、退出码 0、退出后无 sidecar 残留；旧壳 vitest **60 文件 / 567 用例全绿**。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| AC1 构建 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/build.ps1` | SDK 9.0.308，Debug，交付分支 | PASS | `verification/HOST-CORECLIENT-1/build/dotnet-build-Debug.log` |
| AC1 发布 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/publish.ps1` | win-x64，SingleFile+Trim+R2R+压缩 | PASS（1 文件 27.64 MiB） | `verification/HOST-CORECLIENT-1/publish/publish_files.json` |
| AC2 双 sidecar | `scripts/test.ps1` → `CoreServiceIntegrationTests`/`HostBridgeIntegrationTests` | 无标签副本 + 隔离 data root | PASS | `test/dotnet-test-Debug.log`、`wire/*.ndjson` |
| AC3 中文往返 | `ChineseTitle_CreateThenList_RoundTripsExactly_AndWireIsAsciiEscaped` | 同上；向量 `雾港来信・日本語テスト` | PASS（UTF-8 hex 相等；wire 含 `\u96fe…`，request_ascii_only=true） | `wire/core-chinese-roundtrip.json` |
| AC3 UTF-8 负例 | `RawUtf8Request_ReplicatesUnknownError` | 同上 | PASS（`UNKNOWN`） | `wire/core-raw-utf8-negative.json` |
| AC4 typed 失败 | `SidecarFailureTests`（缺失 exe / 非法 exe / 启动超时 / 请求超时） | 同上 | PASS（stderr 文件必存在；无 panic） | `diagnostics/*.json` |
| AC5 单实例 | `SecondInstance_IsAlreadyRunning_WithoutSpawningSidecars` | Local 唯一名 + 真 Mutex | PASS（`HOST_ALREADY_RUNNING`，未 spawn） | `host/second-instance.json` |
| AC5 旧壳共存 | `LegacyShellRealTests`（真 `new-manga.exe` 副本进程） | Windows 11，真进程探测 | PASS（检测→`ReadOnlyLegacyShellRunning`，写被拒） | `legacy-shell/runtime-readonly.json` |
| AC5 只读策略 | `HostRuntimeIntegrationTests.ReadOnlyUntilParity_*` | 隔离 data root | PASS（parity 前 `HOST_READ_ONLY`） | `host/runtime-readonly.json` |
| AC6 端到端 | `pwsh -NoProfile -File apps/desktop-avalonia/scripts/smoke.ps1` | 发布 exe + 副本 + `--parity --demo-write --auto-roundtrip` | PASS（无控制台、无残留、中文 wire 证据） | `smoke/smoke.json`、`smoke/window.png` |
| AC6 旧壳回归 | `npx vitest run`（`apps/desktop/frontend`） | 旧前端依赖已装 | PASS（60/60 文件，567/567 用例） | `test/vitest-baseline.log` |
| AC6 治理 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/HOST-CORECLIENT-1.md` | 本 worktree | PASS | 本卡 Canonical Evidence |

未运行项：无。说明：`ProcessIntegrity.EnsureChildMatchesParent` 的“不一致”分支只有单测（Windows 子进程天然继承父 integrity level），真实链路以“所有真 sidecar 均能通过校验启动”间接证明；`Global\` 命名空间权限不足时回退 `Local\` 的行为已单测 + 真机获取验证（见 record decision）。

## 接收方式

- 仓库：`G:/CODEX/New Manga`；分支 `task/HOST-CORECLIENT-1`；worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-CORECLIENT-1`；base `a93f20c7b`；`delivery_head` 见 front matter（本 Handoff 可在后续文档提交中记录）。
- 前置条件：Windows 11；.NET SDK 9（已装 9.0.308，另有 10.0.401）；无需管理员权限。
- sidecar：使用 `apps/desktop/src-tauri/target/release/resources/core-sidecar` 的**无标签副本**（AC11）。准备命令：
  `pwsh -NoProfile -File apps/desktop-avalonia/scripts/prepare-sidecar.ps1`
  默认落到 `G:/CODEX/New Manga.workspace/task-envs/HOST-CORECLIENT-1/sidecar-copy`。
- 复跑门禁：
  1. `pwsh -NoProfile -File apps/desktop-avalonia/scripts/build.ps1`
  2. `pwsh -NoProfile -File apps/desktop-avalonia/scripts/test.ps1`（自动设 `NEWMANGA_CORECLIENT_SIDECAR_DIR`、`NEWMANGA_EVIDENCE_DIR`）
  3. `pwsh -NoProfile -File apps/desktop-avalonia/scripts/publish.ps1`
  4. `pwsh -NoProfile -File apps/desktop-avalonia/scripts/smoke.ps1`
  5. `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/HOST-CORECLIENT-1.md`
- 接收者应检查：E1–E15 pin 是否仍匹配；`apps/desktop/**` 无 diff；`git diff --stat base_commit..delivery_head` 只含允许路径；旧壳 vitest 仍 60/567。

## Record Decision（AC7 要求）

1. **协议字段映射（保持不变，零改动 Core）**
   - `core_service`：`{"protocol":"new-manga.core","version":{"major":2,"minor":<3|8>},"request_id","command","payload"}`；`core.ping`/`ListBooks`/`core.shutdown` 用 minor **3**，`CreateBook`/`CreateChapter` 用 minor **8**（冻结 Core 的既有版本选择，未改）。
   - `host_bridge`：`{"id":<int>,"method","params"}` → `{"id":n,"result":{…}}` / `{"id":n,"error":{"code":"…"}}`；方法 `ping/issue/resolve/touch/revoke/revoke_resource/shutdown`；`issue` 仅接受 `resource_id` + `revision_fingerprint`，resolve 返回 `scope_class/resource_id/revision_fingerprint/rel_path/size/sha256/volume_serial/file_index`。
   - 非 ASCII：请求侧统一 `\uXXXX`（小写 4 位 hex，含代理对），响应侧冻结 sidecar 也回 `\uXXXX`；两侧均断言 ASCII-only 并保存原始 UTF-8 hex。
2. **错误码映射（UI 只展示 typed code + 中文提示，不展示绝对路径）**
   - `SidecarErrorCode`：`SidecarBundleMissing` / `SidecarExeMissing` / `SpawnFailed` / `StartupTimeout` / `RequestTimeout` / `ProcessExited` / `ProtocolMismatch` / `MalformedResponse` / `IntegrityMismatch` / `HandshakeFailed` / `IoFailure` / `AlreadyRunning` / `InvalidArguments` → `SidecarException.UserMessage` 中文文案；完整路径只进 `host.log`。
   - Core 业务错误 → `CoreOperationException`（透传 `code/category/retryable`）；资源通道错误 → `BridgeException`（`RESOURCE_NOT_CATALOGED`/`REF_REVOKED`/`REF_MALFORMED` 中文文案）。
   - Host 层把失败收敛为 `HostStartResult{Status,Mode,ErrorCode,UserMessage,StderrLogPath}`，启动失败绝不抛到 UI 线程导致 panic。
3. **sidecar 发现顺序（第一命中即用）**
   1. 显式 `--sidecar-dir` / `HostOptions.SidecarDirectoryOverride`（测试、运维、打包）；
   2. 环境变量 `NEWMANGA_CORE_SIDECAR_DIR`；
   3. `<AppContext.BaseDirectory>/core-sidecar`（对齐 Tauri 打包布局）；
   4. `<AppContext.BaseDirectory>/resources/core-sidecar`（资源目录布局）；
   5. 都不含 `core_service.exe` + `host_bridge.exe` → `SidecarBundleMissing`（中文提示，不泄漏路径）。
4. **单实例与权限**：默认 `Global\NewManga.Host`（ADR-0001 D3）；若令牌无 `SeCreateGlobalPrivilege`（标准用户）→ 回退 `Local\NewManga.Host`（数据根本身按用户隔离，会话级足以防止双写）。互斥体在专用后台线程持锁/释放，避免线程亲和性错误。
5. **共存策略**：旧壳 `new-manga.exe` 运行时 → 新 Host 进入 `ReadOnlyLegacyShellRunning`（只读 + 提示），不杀旧壳、不双写；S2 parity 前默认 `ReadOnlyUntilParity`；`ParityReached=true` 仅用于隔离 demo/测试。
6. **数据安全**：首次运行把 `catalog/catalog.sqlite` 复制到 `<data root>/backups/*.nmbak`（幂等，不覆盖）；只读模式下 `HostRuntime.CreateBookAsync` 抛 `HOST_READ_ONLY`。

## 下一任务建议（必填）

- Task ID / 标题：建议 `HOST-CORECLIENT-2`（S2 命令面 parity 与只读书架 UI 接线）—— 待 DSH 释放；本 Handoff 不创建占位 Task。
- 推荐 Agent / Reviewer：ZCode（实现）/ DSH 集成 + 未参与实现的独立 Reviewer（Antigravity 或 Codex）。
- 推荐原因与前置依赖：S1 已有双通道、typed 诊断、单实例/共存/只读骨架与证据链，S2 可直接扩命令面（57/66）与 UI 数据绑定；前置为本 Task 复核通过。
- Recovery point：仓库 `G:/CODEX/New Manga`，branch `task/HOST-CORECLIENT-1`，worktree `G:/CODEX/New Manga.workspace/worktrees/HOST-CORECLIENT-1`，base `a93f20c7b`，head 见 front matter。
- 允许修改路径：`apps/desktop-avalonia/**`、`doc/tasks|handoffs`、`doc/STATUS|REBASELINE_PLAN|TASK_LEDGER`、`verification/HOST-CORECLIENT-2/**`、workspace task-env。
- 禁止范围与新增授权条件：禁改 `apps/desktop/**` 与 `src/**`；禁 push；新材料/字体/依赖需先核许可。扩到 Python Core 需新授权。
- 交付物：S2 parity 清单 + 剩余命令客户端 + 书架/阅读器只读数据绑定 + 回归证据。
- 验证命令、环境与完成 Gate：同 S1 五条命令（build/test/publish/smoke/check），vitest 基线保持 60/567，`check.ps1` PASS。
- 可直接转发给 Agent 的指令：见 DSH 释放的 S2 Task 卡；转发时附本 Handoff 的 Record Decision 1–6 作为共享契约。

## 风险与遗留

- **S2 parity 未做**：本 Task 只跑通 `core.ping`/`ListBooks`/`CreateBook` 与 bridge 全生命周期；57/66 命令差异留待 S2。
- **`Global\` 回退**：标准用户场景实际使用 `Local\`；多用户会话下各自单实例，但数据根按用户隔离，无双写风险。若未来要求全机单实例，需服务/计划任务持 Global 锁。
- **UI 演示写入**：`--parity --demo-write` 才允许写，且要求显式隔离 `--data-root`；默认生产数据根只读。真实用户数据从未被写入（所有测试/smoke 均用临时 data root）。
- **裁剪告警**：`Avalonia.Desktop` 的 DesignerSupport 在 trimmed publish 下产生 IL2026/IL2072 提示（S0 spike 同样存在），仅 publish 阶段放行；普通 `-warnaserror` 构建 0 警告。
- **未提交的 workspace 副本**：`task-envs/HOST-CORECLIENT-1/sidecar-copy`（~1 GB，排除 models/python）按资源 manifest `PRESERVE_REFERENCED` 保留，供复跑与复核；删除需新授权。
- 回退方法：`git worktree remove` 本 worktree、删除 `apps/desktop-avalonia/` 与 `verification/HOST-CORECLIENT-1/` 即回到 base；旧壳与 Core 未改动。
