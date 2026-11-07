---
task_id: FEA-11-SCAN-RH-1
author: scan-rh-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: ffcfab050
start_head: d09e91d1d
delivery_head: fb74b4ef7
status: in_review
supersedes_handoff: null
---

# Handoff — FEA-11-SCAN-RH-1（SCAN-2 复核残余收口：refresh pending 重放 + refresh 生命周期绑定，Host-only，0 pin）

- Task：`doc/tasks/FEA-11-SCAN-RH-1.md`（`base_commit=ffcfab050`；`status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-08（Asia/Shanghai）
- 权限依据：卡面 `status: ready`（Owner=`scan-rh-impl`）+ 权威 scope review
  `doc/reviews/FEA-11-SCAN-RH-scope-r1.md`（recommended；D-1 重放修复 / D-2 SCAN-2 append-only 订正 / D-3 单卡 /
  D-4 RH-3/RH-5 仅登记）
- 交付基线：**实施起点实测 `d09e91d1d`** = Lead 的 docs-only 释放提交（仅改
  `doc/handoffs/DSH-HANDOFF-2026-11-06.md`；卡面 `base_commit=ffcfab050` 为其父）；实现/测试提交落在其上
- **delivery_head = `fb74b4ef7`**：实现 `938d598ac` + 测试 `fb74b4ef7`；随后同批 docs/evidence 提交
  （EV / `RESOURCE-MANIFEST.json` / 本 Handoff / 卡面交付记录 / SCAN-2 append-only 一行）
- 环境：Windows 11 / PowerShell 7 / .NET SDK 10.0.401（`net9.0`）/ CPython 3.14.6 / pytest 9.1.1；未建 worktree；
  未 push；零新依赖、零 schema/迁移、零 wire/命令/能力/错误码/`PROTOCOL_MINOR`、零契约字节、零 App/UI；
  `HostRuntime.cs` **零 diff**

## 1. 交付结果（AC-RH-1…AC-RH-5 全 MET；卡面已 `<<MET>>`，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| **AC-RH-1 RH-1 重放修复** | MET | `RefreshTargetsAsync` = wrapper + `RefreshTargetsPassAsync`；pass 完成枚举并释放闸门后（成功/typed unavailable）重放一次 `_refreshPending`，取消/已 disposed 的提前返回不重放；`ReplayPendingRefreshAsync` 调用**非重放** pass（每 pass 至多一次、不递归，重放期间新请求留给下一次 pass）；`TickAsync` 既有 refresh→hint 重放顺序未改；XML 注释改为 "coalesced and replayed after the in-flight pass"。新增 2 用例（无 `TickAsync` 即发生第二次枚举并合并新 target；重放有界）。判别性 M1（删重放 → 2 用例 RED） |
| **AC-RH-2 RH-2 lifetime 绑定+停机 join** | MET | 新增 `_lifetimeCts` + `_activeRefreshes`/`_refreshIdle`；枚举 token = caller ∪ lifetime（`CreateLinkedTokenSource`）；`DisposeAsync` 顺序 = 置 disposed → Stop → **cancel lifetime** → join loop → **有界 join refresh（2 s）** → join hint（2 s）→ `_tickGate.Dispose()`；disposed 后 late refresh 返回 false、dispose 竞态 wrapper 收敛为 false → 无 `ObjectDisposedException` 日志。新增 1 用例（枚举阻塞 + Dispose → 观察取消、有界完成、无 ODE 日志）。判别性 M2（改回 caller token/不 cancel/不 join → RED） |
| **AC-RH-3 RH-4 文档订正（零代码）** | MET | 卡面 `## Limitation` RH-4 + `FEA-11-SCAN-2.md` closeout limitation **append-only 一行**（`+1/−0`）：Core 14 表（`tests/core/test_core_scan_target_commands.py:44-59`）/ Host 15 表（`verification/FEA-11-SCAN-2/host-cold-start.json:15-32`）/ C-17 §6.2 派生 16 表（`tests/fea11/test_source_sync.py:588-606`）；并集 **17**；相对 16 表基线缺 `pipeline_runs`/`pipeline_run_targets`/`step_result_candidates`、多 `books`/`chapters`/`sources`/`book_cleanup_manifests`；无「满足 C-17 §6.2 零写基线 / 全库零写」表述 |
| **AC-RH-4 RH-3/RH-5 登记** | MET | 卡面 `## Limitation`：RH-3（只增不减/无删除 API/Skipped 无 backoff/预算稀释 `(N+live)/8`/watch uncovered WARN/枚举省略≠删除/清理需 C-17 additive = Out）；RH-5（时钟 seam `HostOptions.cs:111-112` 存在、无 fake-Core seam（`HostRuntime.cs:1382-1403`）、canonical gated 用例 SKIP、EV-09 不能判别非阻塞、WATCH-1 卡 `:111/:129/:199/:213` 按本卡口径订正理解但**不改其字节**） |
| **AC-RH-5 门禁/证据/不夸大** | MET | 定向 `~SourceScan` **68→71**、`~SourceWatcher` **19→19**；全量 .NET **1680/0/96 → 1683/0/96**；全量 pytest **3369/10 → 3369/10**；pins **18/18**；check×2 **PASS(3 warnings)**；API **EXIT=0**；scope 合规、零漂移；判别性 **2/2 RED + sha256 2/2 MATCH + 复绿**；未写「RH-3 已清理 / RH-5 已补 seam / SCAN-2 残余已全部解决」 |

## 2. 验证证据（实跑；`delivery_head=fb74b4ef7`）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| Release build | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **0 warning / 0 error** | `verification/FEA-11-SCAN-RH-1/logs/build-before.log`、`logs/build-final.log` |
| 定向 SourceScan | `dotnet test ... --no-build --filter "FullyQualifiedName~SourceScan"` | **68/0/0 → 71/0/0** | `logs/dotnet-targeted-sourcescan-before.log`、`-after-final.log` |
| 定向 SourceWatcher | 同上 `--filter "FullyQualifiedName~SourceWatcher"` | **19/0/0 → 19/0/0** | `logs/dotnet-targeted-sourcewatcher-before.log`、`-after-final.log` |
| 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release --no-build` | **1680/0/96 → 1683/0/96**（跑后 `git checkout -- verification/FEA-09`） | `logs/dotnet-full-before.log`(+summary)、`logs/dotnet-full-after.log`(+summary) |
| 全量 pytest | `C:/Python314/python.exe -m pytest tests -q -p no:warnings --tb=no` | **3369 passed / 10 skipped**（before 247.68 s / after 251.18 s，不降） | `logs/pytest-full-before.log`、`logs/pytest-full-after.log` |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)** | `logs/governance/pins.log` |
| check（默认 / `-TaskPath`） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings) ×2** | `logs/governance/check.log`、`check-taskpath.log` |
| API inventory | `python tools/generate_api_inventory.py --check` | **EXIT=0** | `logs/governance/api-inventory.log` |
| scope | `git diff d09e91d1d..HEAD --name-only/--stat` + 零漂移 | 仅 allowed_paths；`HostRuntime.cs`/`doc/contracts`/`src/**`/schema/依赖 **0 字节** | `logs/governance/scope-*.log`、`git-status.log`、`postcommit-commits.log` |
| 判别性 | 备份 → M1/M2 变异 → build → RED → 复原 sha256 MATCH → 复绿 | **2/2 RED_AS_EXPECTED + sha256 2/2 MATCH + 复绿**（2 passed / 3 passed；`~SourceScan` 71、`~SourceWatcher` 19） | `logs/discriminative/**` |

- **before/after 行为口径**：修复前——refresh 在飞时的第二次 refresh 只置 `_refreshPending`，重放只在
  `TickAsync` 尾部发生（最坏等下一次 tick，默认 900 s）；停机时在飞 refresh 不被取消也不被 join，`Release()`
  可能命中已 Dispose 的闸门并把 `ObjectDisposedException` 记进 Host WARN。修复后——第二次 refresh 在第一次 pass
  释放闸门后立即重放（不依赖 tick，新 target 当次合并）；`DisposeAsync` 先取消 lifetime 再有界 join refresh，
  日志无 ODE。**未改** tick 预算/backoff/hint 语义与快照 redaction。
- **并发披露**：共享 `main`；本卡提交均为显式 pathspec（`938d598ac` 只含 `SourceScanScheduler.cs`，
  `fb74b4ef7` 只含 `SourceScanSchedulerTests.cs`），docs/evidence 提交只含本卡 allowed 文件。

## 3. 实现要点（供 Reviewer 定点核查）

1. `RefreshTargetsAsync`（`:702-757`）：入口在 `_gate` 内判 `_disposed` 并 `_activeRefreshes++`；随后
   `CreateLinkedTokenSource(caller, lifetime)`；pass 抛 ODE → 返回 false（不写日志）；`completed` 才
   `ReplayPendingRefreshAsync`；`finally` 递减并唤醒 idle TCS。
2. `RefreshTargetsPassAsync`（`:763-...`）：原 `RefreshTargetsAsync` 主体；返回 `(Ran, Completed)`；单飞抢不到、
   disposed/disabled、枚举后 disposed 三种提前返回 = `(false, false)` → 不重放、pending 保留；正常路径返回
   `(result.Ok, true)`；`finally` 释放闸门。
3. `ReplayPendingRefreshAsync`：清 `_refreshPending` 后调用**非重放** pass（`RefreshTargetsPassAsync`），
   不递归；`TickAsync` 仍先 refresh 重放、后 hint 重放。
4. `DisposeAsync`（`:1135-1188`）：disposed 置位 + 取 loop/refresh-idle → `Stop()` → `_lifetimeCts.Cancel()` →
   join loop → 有界 join refresh（2 s）→ 有界 join hint（2 s）→ `_tickGate.Dispose()` → `_lifetimeCts.Dispose()`。
5. 测试：`FakeTargetEnumerator` 新增 `WaitFor`（按调用序号阻塞）/`BlockUntilCancelled`/`CancellationObserved`/
   `Started`/`WaitForCallsAsync`，未改既有 `Block`/`Script` 语义；3 个新用例见 §1。

## 4. Limitation（如实保留；不夸大）

- **RH-3 未修**：targets 只增不减、无删除 API、Skipped 无 backoff、预算稀释 `(N+live)/8`、watch uncovered WARN；
  「Core 枚举省略 ≠ 已删除」，正确清理需 C-17 additive（Out）。
- **RH-4 仅文档订正**：14/15/16 三套表集 + 并集 17 已写清；**不等于**满足 C-17 §6.2 零写基线、**不是**全库零写。
- **RH-5 仅登记**：时钟 seam 存在；fake-Core seam 未加、sidecar bundle 未升级、CI fixture 未改；canonical 全量 .NET
  中 gated 用例仍 SKIP，EV-09 不能判别非阻塞。
- **本卡只实现 RH-1/RH-2**；未写「RH-3 已清理 / RH-5 已补 seam / SCAN-2 残余已全部解决」。实现 ≠ 集成，
  待独立 Review 与 Lead 集成门禁。

## 5. 建议 Review 焦点

1. **重放有界/不递归**：wrapper → `ReplayPendingRefreshAsync` → 非重放 pass 的链路；`TickAsync` 顺序未被改变；
   「重放期间第三次 refresh」是否确实只置 pending 而不递归（`RefreshReplay_IsBoundedToOncePerCompletedPass`）。
2. **Dispose 顺序与竞态**：cancel lifetime → join → gate.Dispose 的次序；`_activeRefreshes` 计数与 `_refreshIdle`
   TCS 的 unmatched/重复完成风险；disposed 后 late refresh 的 false 路径；是否仍存在 ODE 逃逸路径
   （`DisposeAsync_WithInFlightRefresh_CancelsAndJoinsBeforeTeardown` 断言日志无 ODE）。
3. **单飞语义未变**：`TickAsync`/hint pass 在 `--filter "FullyQualifiedName~SourceScan"` 71 与 `~SourceWatcher` 19
   下零回归。
4. **判别性可复跑**：按 `verification/FEA-11-SCAN-RH-1/logs/discriminative/SUMMARY.txt` 复跑 M1/M2/复原；
   注意增量构建需 touch mtime（SUMMARY 已写明）。
5. **文档零代码**：RH-4 表集与并集按 4 个源码/证据位置复核；SCAN-2 为纯 append（`git diff --numstat` = `1 0`）。

## 6. 仓库状态与资源

- 工作树：提交后 clean（`git status --porcelain` 空，见 `logs/governance/git-status.log`）；未 push、未建 worktree、
  未改 `status`/STATUS/PLAN/LEDGER、未自行 closeout。
- 资源：仓内 0 删除/0 移动/0 归档/0 迁移；仓外仅保留
  `G:\CODEX\New Manga.workspace\FEA-11-SCAN-RH-1\SourceScanScheduler.fixed.cs`（判别性备份，sha256
  `6b77d9ca…`，PRESERVE_REFERENCED）；清单见 `verification/FEA-11-SCAN-RH-1/RESOURCE-MANIFEST.json`。
