---
task_id: FEA-11-SCAN-2
review: r1（独立上下文、只读）
reviewer: fresh subagent（未参与 SCAN-2 的实现 / 分片 / 集成 / 返修；只读 reviewed_head 与证据）
reviewer_session: subagent-of-session-8db9dae5-49df-4d09-ac62-696f0805a95c（子会话 ID 以 DSH 派发记录为准）
date: 2026-11-06
repo: G:\CODEX\New Manga（main）
reviewed_head: fa38c47ef
implementation_commits:
  - 0cb5177ca（分片 A：Core Python）
  - 6c8b4cb2b（分片 B：Host/App .NET）
  - 3e6e35b19（分片 B 证据记录修正）
base_commit: 703d9eb12
contract: doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md v1.1
contract_sha256: aefa0fa5b17e0f10d9f23aebc3146c98c3c2bc170f2a18154d56a148e9701a59（与 pin 一致）
decision: changes_requested
severity_counts: P0=0 P1=1 P2=5 P3=6
repo_state_at_end: clean（HEAD fa38c47ef；未 push；Review 期间仓内无写入，verification/FEA-09 变更已 git checkout 恢复）
evidence_dir_review: G:\CODEX\New Manga.workspace\FEA-11\review-scan-2\（仓外：logs/、mut-core/、mut-dotnet/）
---

# FEA-11-SCAN-2 r1 独立 Review（只读、上下文独立）

## 0. 结论摘要

- **Decision: `changes_requested`（P0=0，P1=1，P2=5，P3=6）。**
- 交付的**只读枚举命令、closed shape、排序/去重/上限、typed skip、registry 核验、S-1② fail-closed、零写/脱敏与范围纪律总体扎实**：我独立复跑全量 pytest **3211 passed / 10 skipped**（273.16s，EXIT 0）、`tests/fea11` **108 passed**、`tests/core+fea09+fea11` **1206 passed**；全量 .NET 首跑 **1495/1/83**（失败为已登记 flaky `FluentResidual2VisualEvidenceTests` 的 `git status` 竞态，隔离复跑 PASS），复跑 **1496 passed / 0 failed / 83 skipped**；门禁 `check.ps1 -TaskPath`、`check.ps1`、`verify_pins.ps1`（18/18）、`generate_api_inventory.py --check` 全 PASS；C-17/C-16/C-15/C-06/M2-C1/ADJ-001 与 schema.py 零 diff；29 个 Canonical EV sha256 全部 MATCH；真实 IPC（`NEWMANGA_FEA11_IPC=1`）2/0/0 PASS，wire 精确五命令、15 表快照不变；工作树 clean、未 push。
- **阻断项 P1-1（新路径的真实功能缺陷）**：冷启动枚举会产出**多 book 共享源** target（`project_ids` 2..20），但 `HostSourceScanExecutor` 的 scan 与 missing 路径都**硬编码 `scope="current"` 并携带全部 project_ids**；C-17/Core 规定 `scope=current` 必须恰好一个 project。我用隔离 Core 栈复现：枚举返回 2 个 project_ids 的 target 后，用该 target 的原始字段发 `ScanSourceSync` → **`INVALID_REQUEST: scope=current needs exactly one project`**。即 AC-S2-6 明确纳入的共享源在冷启动后**每轮都以 typed error/退避失败，永远不会被扫描**（单 book 源正常）。最小修复：按 `ProjectIds.Count` 选 `scope`（1→`current`，>1→`all`，`all` 的 guard 我已验证可通过），并补 frame 级判别测试。
- **其余 P2**：tick 在跑时 App 触发的 Refresh 被**直接丢弃**（“merged”只是返回 false，无 pending/重放），SCAN-1 的“Completed 必注册”保证在该竞争窗口退化；Core 枚举会给**零 live 绑定**的源产出 `project_ids: []` target（C-17 §5 规定 1..20；Host 必 skip，且 Core 测试把该空数组目标当“healthy”）；AC-S2-3 标 `<<MET>>` 但卡面自述“真实导入→枚举 E2E 未跑（seed 为合成 s1）”；AC-S2-9 的“scope diff 仅 allowed_paths”严格不成立（分片 B 改了 `LibraryViewModel.cs`，不在冻结 allowed_paths，分片记录却写“均在卡 allowed_paths”）；AC-S2-1 的“新 Host 进程 Ready”只到组件级对象图，HostRuntime Ready→后台枚举接线仅代码审查。
- 结论：**不满足 closeout 条件**；建议按 §6 最小返修后做 r2 窄面复审。AC-S2-3/AC-S2-1 的“限定 MET”与 AC-S2-6/AC-S2-9 的 PARTIAL 需在卡面如实改标，不得维持全 `<<MET>>`。

## 1. AC-S2-1…9 判定（独立核验，不只信卡面）

### AC-S2-1 冷启动枚举（真实重启）— MET（限定：组件级）

- 证据：`verification/FEA-11-SCAN-2/host-cold-start.json` / `.txt`、`logs/host-restart-ipc.log`、`Fea11ScanIpcTests.ColdStartEnumeration_WithoutAppRegistration_IsReadOnly`。
- 独立复核：以 `NEWMANGA_FEA11_IPC=1` 复跑 Host.Tests IPC → **2 passed / 0 failed**（真实 Python Core + 真实隔离 SQLite + 真实 stdio）；我生成的新 fixture `scan-0201438e…/cold-start.json` 与入库证据语义一致：`app_registration_used=false`、枚举 `available=true / last_result=ok`、wire 恰为 `{OpenHostSession, RegisterSourceReadGrant, ScanSourceSync, core.ping, source_list_scan_targets}`（集合精确相等，故无 plan/apply/删除帧）、15 表快照相等。
- 枚举失败不阻塞启动：`RefreshTargetsAsync` 对 `CORE_CAPABILITY_MISSING`/transport/storage 全部转 typed 状态并返回 false；`Refresh_Unavailable_…` 单测证明不阻塞 tick、不重试风暴；`HostRuntime` 在 Ready 之后 fire-and-forget。
- 限定（→ P2-5）：证据没有启动真正的 Host 进程/`HostRuntime.StartAsync`；“Ready 后后台触发枚举”这条接线只有代码审查 + 组件级 IPC，未有任何 HostRuntime 级测试执行它。
- 判定：**MET（限定）**。若 Lead 坚持 AC 字面“新 Host 进程 Ready”，须补 gated HostRuntime 级用例或把 AC 降为限定 MET 并记录 limitation（二选一）。

### AC-S2-2 与会话导入合并/去重 — MET（限定：tick 竞争窗口丢弃 Refresh）

- 代码：`RefreshTargetsAsync` 与 `TickAsync` 共用 `_tickGate`；`MergeTargetsLocked` 按 `source_id` 覆盖/新增，重复 Refresh 不增长；`HostSourceScanEnumerator` 按 `source_id` 去重后升序。
- 单测：`Refresh_MergesAndDeduplicatesTargets_AndIsIdempotent`、`Refresh_IsSingleFlightWithTicks`、App VM `CompletedReceipt_RequestsExactlyOneRefresh` / `NonCompletedReceipt_RequestsNoRefresh` / `RefreshRequest_CarriesNoAppComputedTargetIdentity` 均通过。
- 缺陷（→ P2-1）：`RefreshTargetsAsync` 在 `_tickGate.WaitAsync(0)` 失败时**只记 “merged” 日志并返回 false**，没有 pending 标志/重放；`TickAsync` 结束后也不会补跑。tick 扫描 8 个目标可能持续数秒，App 在此时完成导入则该次 Refresh 丢失；由于**没有周期性枚举**，该新源要到下一次导入 Completed 或 Host 重启才会进入 targets——SCAN-1 的“Completed 必注册”语义在该窗口退化。
- 判定：**MET（限定）**，需修 P2-1 或登记为该卡 limitation。

### AC-S2-3 Core source_id 权威（S-2 判别）— PARTIAL（机制成立，AC 字面 E2E 未跑）

- Core 侧：`source_id` 来自 `sources`（真导入为 `src-<uuid>`，见 `runtime.py:470`）；`registry_id/generation/source_kind/identity_digest/project_ids` 均来自 Core 当前行；测试断言 DTO 键集合恰六字段、identity 由冻结 `identity_digest_of` 重算。
- Host 侧：真实 IPC 断言 `target.source_id == Core sources.source_id` 且 `!= ExpectedStableSourceId(path)`；App 侧删除 `RegisterCompletedImportScanTargets`/`StableSourceId` 目标派生/`bookId` 管道（我以 grep 核验：`RegisterCompleted*`/`SourceScanTargetRegistration`/`_referenceBookId` 0 命中；`StableSourceId` 仅剩 C-16 read-grant 身份用途，符合 S-2 只禁止“扫描目标权威”）。`ImportDockViewModel` 在 Completed 恰好调用一次无参 `RequestSourceScanRefresh()`，Failed/Cancelled 不触发。
- 缺口（→ P2-3）：AC 字面要求“真实导入一本书 → 枚举”，实际 seed 的 `sources.source_id` 是**合成 `s1`**（非生产 `src-<uuid>` 生成链），App 真实导入 → Host Refresh → Core 枚举的整链没有 E2E。卡面 §“未运行/保留”已如实登记，但 AC 仍标 `<<MET>>`，口径自相矛盾。
- 判定：**PARTIAL**。S-2 安全属性在两个 seam 上可判别（若 Host 误用 StableSourceId，`target.source_id` 会等于 `src-<hash16>` 而测试转红），但 AC 的“真实导入”证据缺失；见 §5 意见。

### AC-S2-4 registry 授权核验 — MET

- 代码：`HostSourceScanTargetEnumerator.TryMap` 先按持久 registry 校验 `registry_id` 存在、`RevokedAt is null`、`Generation == target.Generation`、存在 readable root；`HostSourceScanExecutor.VerifyEnumeratedTarget` 在铸 grant/发帧前**再次**核验 registry（撤销/代次/root identity），失败返回 `Skipped`（无 scan 帧、无 grant、不自动重授权），错误/日志只有 typed code，不泄露路径。
- 单测：`EnumeratorMapping_SkipsMissingRevokedAndGenerationDriftedRegistry`、`Executor_EnumeratedTarget_RevokedRegistry_IsSkipped_NoScan`、`Executor_EnumeratedTarget_GenerationDrift_IsSkipped`；我以变异 H-M1（去掉 revoked 检查）与 H-M3（去掉 generation 检查）分别使对应测试转红，判别力成立。
- 撤销后：target 留在内存，但每轮 `Skipped`（`LastResult=skipped`、无 scan 帧、不暂停），满足“撤销后同 target 不再扫描”。
- 判定：**MET**。

### AC-S2-5 启动前缺失/删除（S-1②）— MET

- 代码：`VerifyEnumeratedTarget` 对 `_sources.Registry.List()` 抛错（`SOURCE_REGISTRY_UNAVAILABLE`，L-S1 整库不可读）→ `Error("SOURCE_REGISTRY_UNAVAILABLE")`，绝不进入 missing 分支、不发 `ScanSourceSync`；对同一路径不同物理文件（volume/fileId 漂移）同样 fail-closed；只有“本会话已成功校验过”的源消失才走 C-17 §5.3 missing。
- 单测：`Executor_EnumeratedTarget_ColdStartMissingRoot_IsRegistryUnavailable`、`Executor_EnumeratedTarget_ReplacedRoot_IsRegistryUnavailable`。
- 变异：只去掉内层 catch 的 fail-closed（H-M2）测试**仍全绿**——因为 `SourceAccessRegistry.Load()` 会先对每个 root 重验 identity，整库抛 `SOURCE_REGISTRY_UNAVAILABLE`，外层 catch 已守住（防御纵深，不是测试缺口）。同时去掉 registry 重验 + 内层 fail-closed（H-M4）后该测试转红（实际 `SOURCE_ENTRY_MISSING`），证明 S-1② 语义被测试覆盖。
- 判定：**MET**（L-S1 继续保留：file-root 缺失时整库不可读，需另立缺陷卡）。

### AC-S2-6 共享源 project_ids 边界（P3-4）— PARTIAL

- >20：Core `list_scan_targets` distinct 后 >20 → 不进入 targets + stderr 计数 `project_ids_over_limit`（不截断、不回退 current）；Host `TryMap` 亦拒绝 <1 与 >20 并计数。两端一致；我以变异 C-P3（去掉 Core 上限）使测试转红。
- ≤20：可进入 targets（Core 测试 2 projects 用例、Host `TryMap` 单测），但**不能扫描**——见 P1-1（多 book target 以 `scope=current` 发出被 Core 拒绝）。AC-S2-6 只写了“正常进 targets”，字面可判 MET；但结合卡目标“可扫描目标集”与“不静默回退 current”，实际行为是“进 targets 后用 current 语义发无效帧”，应视为未完成。
- 零 project_ids：Core 会产出 `project_ids: []` 的 target（我复现；`test_typed_skips…` 还把无绑定源当 healthy 断言返回），违反 C-17 §5“project_ids 1..20”，Host 侧必然 skip，属形状不一致（→ P2-2）。
- 判定：**PARTIAL**（>20 正确；≤20 共享源不可扫描 + 0 形状问题）。

### AC-S2-7 预算/单飞/退避/取消 — MET（限定：refresh 无停机取消）

- 首轮预算：tick 沿用 SCAN-1 `MaxTargetsPerTick=8` / `MaxBytesPerSource=256MiB`，枚举在 tick 外、Ready 后后台执行，不阻塞启动。
- 单飞：Refresh 与 Tick 共用 `_tickGate`（互不重叠；但见 P2-1 丢弃语义）。
- 退避：`Skipped` 不 backoff、Error/Denied 指数退避 `min(60×2^n,3600)`；枚举失败不自动重试。
- 注入时钟/零 sleep：`ManualTimeProvider` + 直接 `TickAsync`，测试无 sleep；真实 IPC 也不依赖定时循环（直接 Refresh/Tick）。
- 停机取消：scheduler `Stop`/`DisposeAsync` 取消 loop 并 join；但 HostRuntime 的 `RefreshSourceScanTargetsAsync` fire-and-forget 使用 `CancellationToken.None`，停机时不会取消在途枚举（其本身零写、异常被吞，风险低）。
- 判定：**MET（限定）**；建议把 refresh 与 shutdown token 绑定（P3）。

### AC-S2-8 零写/脱敏 — MET（限定：口径与措辞）

- 零写：Core 侧枚举前后 14 表（含 `source_sync_plans`/`source_operations` 等）逐行相等；Host 真实 IPC 枚举+扫描前后 15 表逐行相等；无 plan/journal/grant 落库（Host grant 仅会话内存，registry `authorize` 更新 last-used 属既有允许行为）。
- 14 vs 15 表口径差异：Core 集合含 `book_cleanup_manifests`/`reading_progress`、不含 `regions`/`region_revisions`/`rendition_cache`；Host 集合含后三者、不含前两者。两个集合各自覆盖其路径可能写入的业务表，**可接受**，但不是同一口径（P3，建议卡面写清并集覆盖）。
- 脱敏：status/日志单测断言无 `C:\`、无 `secret-root`、无 `source-`、无 `host_session`；异常路径只回 typed code。
- 限定（→ P3）：wire NDJSON（fixture `wire.ndjson`）按 C-16 §7 冻结口径脱敏 `path/signing_key/host_session_credential/secret_ref`，但**保留 `grant_id`、`host_session_id`、`core_session_id`、`signature` 原文**；这是 C-16/SCAN-1 既有行为，本卡新命令无新增敏感字段。AC-S2-8 的“wire/日志…无 grant/session 原文”严格不成立于 wirelog，需澄清为“无路径/无凭据/无 secret 原文；grant/session ID 按 C-16 §7 口径”。
- 判定：**MET（限定）**。

### AC-S2-9 门禁与回归 — PARTIAL（门禁 PASS；scope 口径不成立）

- 我独立复跑（详见 §2）：全量 pytest 3211/10、fea11 108、组合 1206、全量 .NET 1496/0/83（首跑 1495/1/83 = 已知 flaky）、check/pins/API PASS、scope diff（`doc/plan doc/contracts src/infrastructure/sqlite/schema.py`）空、EV 29/29 MATCH、C-17 sha 与 pin 一致。
- **不成立项（→ P2-4）**：`git show --name-only 6c8b4cb2b` 含 `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs`，该路径**不在** frontmatter `allowed_paths`（冻结卡与最终卡均无）；`host-shard-record.md` §1 写“本分片改动，均在卡 allowed_paths”、`host-changed-files.txt` 亦把它列为“Modified apps”。该改动是 `ImportDockViewModel` 删除 `bookId` 形参后的**编译必需连带修改**，但按 AC 字面“scope diff 仅本卡 allowed_paths”仍是越界；需 Lead 记录 scope 修订/例外或改卡，不能说“仅 allowed_paths”。
- AC11-1 仍 PARTIAL（`doc/tasks/FEA-11.md` 维持 PARTIAL，STATUS 亦如此）；L10 不解决（卡面明示）——与事实一致。
- 判定：**PARTIAL**（门禁数字全部复现 PASS；scope 条款不成立）。

## 2. 独立复跑（我的实跑，不引用卡面数字）

命令均在仓根 `G:\CODEX\New Manga`，日志在仓外 `G:\CODEX\New Manga.workspace\FEA-11\review-scan-2\logs\`。

| # | 命令 | 结果 | 日志 |
|---|---|---|---|
| 1 | `python -m pytest tests -q -p no:cacheprovider --tb=short` | **3211 passed / 10 skipped / 10 warnings，273.16s，EXIT 0** | `r1-pytest-full.log` |
| 2 | `python -m pytest tests/fea11 -q -p no:cacheprovider` | **108 passed**，EXIT 0 | `r1-pytest-fea11.log` |
| 3 | `python -m pytest tests/core tests/fea09 tests/fea11` | **1206 passed**（956+142+108），EXIT 0 | `r1-pytest-core-fea09-fea11.log` |
| 4 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **0 warning / 0 error**，EXIT 0 | `r1-dotnet-build.log` |
| 5 | `dotnet test …NewManga.sln -c Release --no-build`（首跑） | **1495 passed / 1 failed / 83 skipped**；失败 = 已知 flaky `FluentResidual2VisualEvidenceTests`（`Assert.Equal("" , "M verification/FEA-09/logs/wire-redacted.ndjson")`，git-status 证据写竞态），与本卡改动无交集 | `r1-dotnet-full.log` |
| 6 | 隔离复跑该 flaky | **1 passed / 0 failed**，EXIT 0 | `r1-dotnet-flaky-rerun.log` |
| 7 | 全量复跑 `--no-build` | **1496 passed / 0 failed / 83 skipped**，EXIT 0；分程序集：Appearance 21、Presentation 38、ThemeEngine 253、DesignSystem 117、ApplicationCore 31、Host 154+52 skip、CoreClient 167+24 skip、App 715+7 skip | `r1-dotnet-full-2.log` |
| 8 | `NEWMANGA_FEA11_IPC=1 dotnet test … --filter Fea11ScanIpcTests` | **2 passed / 0 failed**（PeriodicScan + ColdStartEnumeration），EXIT 0；独立 fixture `scan-0201438e…/cold-start.json` 与入库证据一致（s1 / 15 表 / 五命令） | `r1-dotnet-real-ipc.log` |
| 9 | `check.ps1 -TaskPath doc/tasks/FEA-11-SCAN-2.md` | **PASS（3 warnings）**，EXIT 0 | `r1-check-task.log` |
| 10 | `check.ps1` | **PASS（3 warnings）**，EXIT 0 | `r1-check.log` |
| 11 | `verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**，EXIT 0 | `r1-pins.log` |
| 12 | `python tools/generate_api_inventory.py --check` | **PASS**（`IHostController 54`、`IReaderProgressSink 1`、`IRunController 6`，合计 61；C-07 未变），EXIT 0 | `r1-api.log` |
| 13 | `git diff --stat 703d9eb12..fa38c47ef -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py` | **空**（0 文件），EXIT 0 | 本报告 §4 |
| 14 | EV sha256 复算（29 行） | **29/29 MATCH**；C-17 文件 sha256 = `aefa0fa5…1a59`（pin 一致） | 本报告 §4 |

- 每次全量 .NET 后执行 `git checkout -- verification/FEA-09`；Review 结束时 `git status --porcelain` 为空。
- 入库的 `logs/gates-integration.log` 头部为 `head=3e6e35b19`（比 reviewed_head 早一个 docs-only commit）；我在 **fa38c47ef** 上重跑了 check/pins/API/pytest/.NET，数字与卡面一致，故该差异不构成问题，但建议 closeout 时把门禁日志头改为最终 HEAD。

## 3. 变异 / 反证（7 项，全部在仓外隔离副本执行，仓内零改动）

Core：复制 `src/` + `tests/core/` 到 `mut-core/`，逐次改副本并跑 `pytest tests/core/test_core_scan_target_commands.py`，每次后从 `.orig` 还原（还原后 sha256 与副本原文件一致）。

| ID | 变异 | 结果 | 判别 |
|---|---|---|---|
| C-P1 | 去掉 Python 排序（`ordered = list(targets.values())`） | 1 failed, 7 passed | `test_duplicate_candidates_are_deduped_and_sorted` 转红；DB 路径有 SQL `ORDER BY source_id`，故 DB 级排序测试不敏感（冗余防御，非缺口） |
| C-P2 | 伪造 identity（`identity_digest = "0"*64`） | **2 failed**, 6 passed | `test_enumeration_is_sorted_unique_and_computes_identity`、`test_identity_and_facts_are_recomputed_from_current_location` 转红 |
| C-P3 | 去掉 `project_ids > 20` skip | 1 failed, 7 passed | `test_typed_skips_missing_facts_unknown_kind_and_project_limit` 转红 |
| H-M1 | 去掉 revoked registry 检查 | 1 failed, 46 passed | `Executor_EnumeratedTarget_RevokedRegistry_IsSkipped_NoScan` 转红（实际 `SOURCE_REGISTRY_BUSY`） |
| H-M2 | 只去掉内层 cold-start fail-closed catch | 0 failed, 47 passed | **等价变异**：外层 `Registry.List()` 先因 identity 重验失败抛 `SOURCE_REGISTRY_UNAVAILABLE`，行为不变；证明防御纵深，非测试缺口 |
| H-M3 | 去掉 `entry.Generation != target.Generation` skip | 1 failed, 46 passed | `Executor_EnumeratedTarget_GenerationDrift_IsSkipped` 转红 |
| H-M4 | 同时去掉 registry root identity 重验 + 内层 cold-start fail-closed | 1 failed, 46 passed | `Executor_EnumeratedTarget_ColdStartMissingRoot_IsRegistryUnavailable` 转红（实际 `SOURCE_ENTRY_MISSING`），证明 S-1② 语义有判别力 |

附加反证（隔离 Core 栈，非测试改动入库）：
- 2 book 共享源：枚举返回 `project_ids=["book-s1","book-s2"]`；按 Host 现状发 `scope=current` + 两 id → `INVALID_REQUEST: scope=current needs exactly one project`（**P1-1 复现**）；同 payload 改 `scope=all` → 通过 scope guard（随后因无 grant 报 `a non-missing source requires read grants`，属预期），说明 `scope=all` 修复可行。
- 零绑定源：枚举返回 `project_ids=[]`（**P2-2 复现**）。

## 4. 契约一致性、证据与范围

**契约（C-17 v1.1，sha `aefa0fa5…` 与 pin 一致）**
- 命令名 `source_list_scan_targets`、application 面、closed shape `{}`、未知键/非对象 → `INVALID_REQUEST`：与 §5.1/§5.2 一致。
- `ScanTarget` 六字段恰为 `{source_id, registry_id, generation, source_kind, identity_digest, project_ids}`；`source_id` 来自 `sources`；`identity_digest = identity_digest_of(location facts)`；`targets` 按 `source_id` 升序、唯一、空数组合法；数组上限 10000、8MiB → `SOURCE_BUDGET_EXCEEDED` 不截断：一致。
- `source.sync.enumerate/1` **只**进 `core.ping.capabilities`；Host §5.2 `Capabilities` DTO 仍恰 7 项（`RunCapabilityProbeAsync` token 表 7 项未变）；未登记 HostCommandRegistry/C-07；无 UI 面：一致。
- 错误码零新增：新增路径只复用 `INVALID_REQUEST`、`SOURCE_BUDGET_EXCEEDED`、`SOURCE_REGISTRY_UNAVAILABLE`、`SOURCE_GRANT_REVOKED`、`SOURCE_REGISTRY_BUSY`、`CORE_CAPABILITY_MISSING`、`SOURCE_SYNC_STORAGE_FAILED`（均在 §8/M2-C1 闭集）；`UNKNOWN`/`skipped` 仅进程内 status，不上 wire。
- 契约/计划/schema/依赖零 diff：`git diff 703d9eb12..fa38c47ef -- doc/plan doc/contracts src/infrastructure/sqlite/schema.py` 空；`schema.py` 无改动；无新依赖。
- 唯一契约口径偏差：Core 产出 `project_ids: []`（§5 规定 1..20）→ P2-2。

**证据（Canonical Evidence）**
- EV-01…EV-29 全部存在且 sha256 **29/29 MATCH**（我逐行复算）；`host-cold-start.json/text` 与我独立复跑的 fixture 语义一致。
- 门禁日志可信度：`gates-integration.log` 记录 head=3e6e35b19；我在最终 HEAD fa38c47ef 复跑 key gates 全 PASS，未发现“日志与代码不符”。pytest Core 956、fea09 142、组合 1098 与卡面一致（我复跑组合 1206 = 956+142+108，因包含 fea11）。

**范围/纪律（`git show --name-only` 逐 commit 核对）**
- 分片 A `0cb5177ca`：`src/application/sources/scanner.py`、`src/bootstrap/core_service.py`、`src/infrastructure/sqlite/source_sync.py`、`tests/core/test_core_scan_target_commands.py`、`tests/core/test_core_service.py` + `verification/FEA-11-SCAN-2/core-*`：**均在 allowed_paths**。
- 分片 B `6c8b4cb2b`：apps 13 个文件（10 src + 3 tests）+ `verification/.../host-*`：**12 个在 allowed_paths，`LibraryViewModel.cs` 越界**（→ P2-4）。
- 证据提交 `3e6e35b19`：仅 `verification/FEA-11-SCAN-2/host-shard-record.md`，允许。
- Lead `fa38c47ef`：STATUS/PLAN/LEDGER/任务卡/`gates-integration.log`，属 Lead 保留指针（卡面 §允许修改范围 明示），不视为实现越界；但其中任务卡把全部 AC 标 `<<MET>>` 与上述 PARTIAL 不一致（见 §1）。
- 未 push：本地 `main` 相对 `origin/main` 跟踪引用领先 965（未 fetch，不作远端事实），Review 期间无 push 操作；工作树 clean。
- 未发现 SQLite schema/migration/索引、依赖、其他冻结契约、真机数据/回收站改动；`tests/fea11` 未改（108 为既有基线）。

## 5. S-2 E2E 缺口意见（AC-S2-3）

**我的意见：当前证据足以证明“S-2 机制”但没有证明 AC 字面的“真实导入→枚举 E2E”，因此不能把 AC-S2-3 当完整 MET，也不建议只靠“seed s1”就关闭。**

- 已经证明的：①Core `sources.source_id` 是唯一权威（`src-<uuid>` 生成点在 `runtime.py`）；②Host 把 Core 返回值原样用作 target id，且与 `StableSourceId` 判别（若 Host 用 App 计算的 id，测试会转红）；③App→Host 的刷新接口**无参数**，VM 级断言 App 无法夹带 id；④App 的 StableSourceId/registry_id 目标权威与 `bookId` 管道已删除（grep 0 命中）。
- 未证明的：真实 `ImportController` 导入 → Core 生成 `src-uuid`/`source_locations` → App Completed 触发 Host Refresh → Core 枚举 → Host 合并/核验 的**同一条链**。合成 `s1` 绕过了生产 `src-uuid` 生成器与真实 registry/grant 的联动；若该链路存在 wiring 缺陷（例如 Refresh 时序、registry 生成代次与 Core location 不一致），现有证据无法发现（且 P2-1 的丢弃问题正属此类）。
- 建议（二选一，Lead 裁决）：
  1. **补 E2E（推荐）**：在 `Fea11ScanIpcTests` 增加 gated 用例——真实 Core + 真实 App `HostController`/`ImportController` 导入一个小 zip 到一个 book，完成 receipt 后调用 `RequestSourceScanRefresh`，断言枚举 target 的 `source_id` 从 Core DB 读出且为 `src-<uuid>`、`!= StableSourceId`，then tick 扫描成功；同时覆盖 Completed 只触发一次与 tick 竞争窗口。
  2. **降级为限定 MET**：卡面把 AC-S2-3 标 `<<MET: S-2 seam-level; real-import E2E NOT_RUN>>`，并在 limitation 明确“合成 seed 不覆盖真实导入链”，closeout 时由 DSH 记录；不得维持裸 `<<MET>>`。

## 6. Findings 与最小返修点

### P1（阻断）

**P1-1 共享源（多 book）target 永远无法扫描**
- 位置：`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs` `HostSourceScanExecutor.ScanAsync`（`writer.WriteString("scope", ScopeCurrent)` + 全部 `target.ProjectIds`）与 `ScanMissingAsync`（同）。
- 事实：Core 枚举对共享源返回 2..20 个 `project_ids`（我实测 2 个）；Core `scan()` 对 `scope=current` 强制恰好 1 个 project（`scanner.py:267-269`，`model.py:870`）。现状每轮 `INVALID_REQUEST` → Host `Error` → 指数退避，**永远不会扫描**；这不是“尚未覆盖”，而是卡目标“可扫描目标集”在 AC-S2-6 场景下的直接失败。
- 最小修复：`var scope = target.ProjectIds.Count == 1 ? "current" : "all";`（scan 与 missing 两处）；`scope=all` 需 `project_ids == 冻结引用集合 book 去重值`，而枚举的 project_ids 与 Core `list_source_references` 使用同一过滤（`page_bindings.status != 'superseded'`），我实测该 guard 可通过。补判别测试：fake core 捕获 `ScanSourceSync` 帧，断言 2-book target 发 `scope=all` + 两个 id、1-book 发 `scope=current`；并加真实 IPC 的共享源用例（同一 zip 导入两个 book）。
- 备选：若认为多 book 扫描超出本卡，则必须在 `TryMap` 对 `ProjectIds.Count > 1` 做 **typed skip + 计数** 并登记 limitation（不能静默发无效帧），同时改 AC-S2-6 文案。

### P2

**P2-1 tick 期间 App Refresh 被丢弃（“merged”名不副实）**
- 位置：`SourceScanScheduler.RefreshTargetsAsync`（`_tickGate.WaitAsync(0)` 失败即返回 false，无 pending 标志）；`TickAsync` 结束不重放。
- 影响：Completed 导入恰逢 tick 运行时，新源本会话不再被枚举/扫描（无周期枚举），退化 SCAN-1 “Completed 必注册”。
- 最小修复：加 `_refreshPending`（在 gate 失败时置位，`TickAsync`/`RefreshTargetsAsync` 结束时若置位则后台再跑一次，需防重入）；或由 HostRuntime 在 false 时延迟一次重试。补竞争窗口测试（tick 阻塞时请求 Refresh，tick 结束后 targets 含新源）。

**P2-2 Core 枚举产出 `project_ids: []` target（C-17 §5 形状 1..20）**
- 位置：`scanner.list_scan_targets` 未对空 project_ids 做 skip；`SourceSyncStore.list_scan_target_candidates` 用 LEFT JOIN，无绑定源返回空数组。测试 `test_typed_skips…` 把无绑定的 `ok_source` 当作“健康源”断言返回。
- 影响：wire DTO 违反 §5“project_ids 1..20”；Host `TryMap` 必 skip（计数），Core 侧与 Host 侧口径不一致。
- 最小修复：Core 对该候选做 typed skip（新增 stderr 计数 `no_project_references`），同时把测试里的“健康源”补一条 live binding（空库用例保留）；或另走 additive 契约放行 0（本卡不允许改契约字节，不推荐）。

**P2-3 AC-S2-3 标 MET 但真实导入 E2E 未跑**
- 最小修复：按 §5 方案 1 补 E2E，或方案 2 在卡面降级并记录 limitation（二选一，不可维持现状）。

**P2-4 AC-S2-9 scope 口径不成立（`LibraryViewModel.cs` 越界）**
- 位置：`6c8b4cb2b` 修改 `apps/desktop-avalonia/src/NewManga.App/ViewModels/V2/Library/LibraryViewModel.cs`（移除 `bookId:` 传参），该路径不在 `allowed_paths`；`host-shard-record.md` §1 与 `host-changed-files.txt` 未如实标注例外。
- 说明：该改动是 `ImportDockViewModel` 删除 `bookId` 形参的编译必需连带修改，技术上合理、无越界功能。
- 最小修复：Lead 在卡面/Review 处置中记录“allowlist 例外 + 理由”（或把该文件补入 allowed_paths 的 scope 修订记录），并修正 shard record 的“均在卡 allowed_paths”表述；无需回退代码。

**P2-5 AC-S2-1 “新 Host 进程 Ready”只有组件级证据**
- 位置：`Fea11ScanIpcTests.ColdStartEnumeration…` 在测试进程内新建 Host 侧对象图，未 `HostRuntime.StartAsync`；`HostRuntime.StartSourceScanScheduler` 的 Ready→后台枚举只有代码审查。
- 最小修复：补 gated HostRuntime 冷启动用例（启动真实 Host + 隔离 DataRoot，断言 Ready 后枚举状态、wire 五命令、不阻塞）；或把 AC-S2-1 降为限定 MET 并在 limitation 记录“wiring 仅代码审查”。

### P3（非阻断，建议 closeout 前后处理）

1. **wire NDJSON 与 AC-S2-8 措辞**：fixture `wire.ndjson` 保留 `grant_id`/`host_session_id`/`core_session_id`/`signature`（C-16 §7 只脱敏 `secret_ref/signing_key/host_session_credential/**path`），与本卡新命令无关；建议把 AC-S2-8 改为“无路径/无凭据/无 secret 原文（grant/session ID 按 C-16 §7 口径）”，避免 closeout 时被误读为“wirelog 无 grant id”。
2. **targets 只增不减 + refresh 无停机取消**：Core 中软删/删除或 project_ids 变化后，内存 target 不收缩，后续每轮 typed skip/error（无写）；`RefreshSourceScanTargetsAsync` 用 `CancellationToken.None`，停机不取消在途枚举。可登记为 limitation，不必本卡修。
3. **`HostRuntime.cs:1181-1184` 注释过期**：仍写“Cold start enumerates no sources (L-A) … only over App-registered targets”，与本卡行为矛盾，建议随返修改为“Ready 后后台枚举”。
4. **VM 测试名不副实**：`ConfirmInFlight_LaterSelectionSwitch_StillOneRefresh` 实际未切换选择（只是用 TCS 延迟 receipt 后释放），未覆盖 r1 P3-1 的“在途切换”场景，建议改名或补切换动作。
5. **14 vs 15 表快照口径**：Core 14 表与 Host 15 表集合不同（见 §1 AC-S2-8），并集覆盖合理但非同一口径，建议卡面写明。
6. **generation drift 用 `SOURCE_REGISTRY_BUSY`**：该码在 §8 为 retryable=true，而注释语义是“只有重新导入/授权才能再证明”；不新增码是对的，但建议注释/文档说明“本命令投影里 retryable 不代表自动重授权”。另外 `HostRuntime.RegisterSourceScanTarget` 已无生产调用方（仅单测），可作为后续清理项。

## 7. Limitation（closeout 应保留/新增）

- **L-S1**（既有）：file-root 缺失/替换导致持久 registry 整库 `SOURCE_REGISTRY_UNAVAILABLE`；本卡 fail-closed 正确，但 registry 韧性另立缺陷卡。
- **L-S4**（既有）：`refresh_source_location_auth` 死代码，撤销/重注册后 Core location auth 不更新。
- **L-A/L-G**：SCAN-2 承接并修复冷启动目标集为空；L-G 口径保留（首次成功扫描前 missing 不伪造）。
- **新增（若接受而不修 P1-1）**：共享源（多 book）冷启动 target 不可扫描；必须显式登记并改 AC-S2-6。
- **新增**：真实导入→枚举 E2E 未跑（合成 `s1`）；HostRuntime Ready 级 wiring 仅代码审查；大库 IO/冷启动预算未标定；AC11-1 仍 PARTIAL；L10 不解决。

## 8. Closeout 建议

- **不得**在 `fa38c47ef` closeout：存在 P1-1（共享源不可扫描）与 P2-1（Refresh 丢弃），且 AC-S2-3/AC-S2-9 的 MET 标记与证据不符。
- 返修提交后（建议新 commit，不 amend 已入库的集成提交）：
  - `delivery_head`：返修与重签证据后的最终交付 HEAD（若 Lead 只按 P1-1 + P2-1 返修，则为其 commit；若同时补 E2E/降级 AC，则取最终 commit）。
  - `integration_commit`：返修验证通过后的 Lead 集成提交（保持 `null` 直到那时）。
  - `canonical_evidence_status`：返修后重跑门禁 → 更新/新增 EV pin（29 项全量复算），`canonical_evidence_status=complete`；若证据文件字节变化必须重签全部受影响 sha。
  - `resource_closeout_status`：按 Resource Manifest 清 temp/保留 agent-output；本卡无 worktree。
- AC 口径收口建议：
  - AC-S2-1：`<<MET: component-level; HostRuntime Ready wiring code-reviewed>>`（或补测试后维持 MET）。
  - AC-S2-3：`<<MET: S-2 seam-level; real-import E2E NOT_RUN>>`（或补 E2E 后维持 MET）。
  - AC-S2-6：`PARTIAL`（共享源不可扫描 + 0 形状），修复后改 MET。
  - AC-S2-9：`PARTIAL`（`LibraryViewModel.cs` scope 例外未记录），Lead 记录例外后改 MET。
  - 其余 AC 维持 MET（带 §1 限定）。
- **AC11-1 仍 PARTIAL**：本卡只闭合冷启动枚举/扫描目标半边；watcher 与访问前策略未承接，WATCH-1 不同时释放，不得借本卡回填 AC11-1。
- **L10 不解决**：真实 referenced 图源/rendition 留待后续卡。

## 9. 复核边界

- 本 Review 只读仓内文件；所有变异在仓外副本执行；证据日志写在 `G:\CODEX\New Manga.workspace\FEA-11\review-scan-2\`。
- Review 结束时仓内 `git status` clean、未 push；未修改任务卡/STATUS/PLAN/LEDGER/verification 证据字节。
- 独立复跑数字见 §2；未复核项：真实 App UI 手工导入、旧 Core 兼容矩阵实跑（capability 缺失路径仅单测覆盖）、多 book 真实导入 E2E（即 §5 缺口）。

SCAN-2-R1-REVIEW: CHANGES (P0=0 P1=1 P2=5 P3=6; P1-1 多 book 共享源 target 无法扫描; P2-1 tick 期间 Refresh 丢弃; P2-2 Core 产出 project_ids=[] target; P2-3 AC-S2-3 真实导入 E2E 未跑却标 MET; P2-4 LibraryViewModel.cs 越界且记录失实; P2-5 AC-S2-1 HostRuntime Ready 级未验证; 门禁独立复跑 pytest 3211/10、.NET 1496/0/83、真实 IPC 2/0/0、check/pins/API/EV 均 PASS)
