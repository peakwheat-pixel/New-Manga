# FEA-11-L-S4-B-AUTO-RECOVERY-1（L-S4-B）：重授权后的零交互恢复 — 证据（EV）

> 本 EV 只陈述**实跑**事实；未跑的项目逐项标注。措辞红线（AC-LS4B-10）：「零交互」严格限定为
> **用户完成 B1 显式「重新授权」动作之后**系统不再要求第二次交互；不是撤销后自动恢复、不是自动
> 重新授权、不是自愈。**不宣称扫描执行恢复**（见 limitation L-S4-B-1）。

- Task：`doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md`（Owner=`l-s4b-impl`，Lead=`lead`）
- 契约：C-16 v1.5（`doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`，§0 能力 / §1 `roots_available` / §2.5 `ReattestSourceLocation`），已冻 `a7f57ebd…`；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md`
- 卡 `base_commit=a7360839d`；**实现起点 `c6ca1aa3c`**（Lead 释放；`main` clean）
- **delivery_head=`30bdeb4ce`**；交付 commit 链：
  - `ec171f0d3` Core `ReattestSourceLocation`（`reattest.py` + `core_service.py`）
  - `3ccb0509e` Host 能力探测 / `SourceRootReattestPlanner` / 枚举 pre-pass / `HostRuntime` 接线
  - `f76620e39` App B1 成功分支触发既有 scan refresh
  - `c4345a632` 测试矩阵（Core / Host / App / gated IPC）
  - `30bdeb4ce` DSH 批准扩域的既有 capability 断言 +`source.reattest/1`（仅预期 1 行）
  - （Lead 的 `4e9ab8d90` 为 scope 扩域卡面 docs 提交，`8c0d2d8af`/`5f64ba972`/`d354a1390`/`5a02214a5` 为 PREREQ close-out docs，均非本交付代码）
- 权限依据：卡面 + scope review `doc/reviews/C16-V15-BATCH-scope-r1.md`（推荐 b3 形状）+ PREREQ r9 approved + DSH 裁决（scope 扩域 2 文件；L-S4-B-1 登记）
- 环境：Windows 11 / PowerShell 7 / CPython 3.14.6 / .NET SDK 10.0.401（测试目标 net9.0）；零新依赖、零 schema/迁移、零契约字节

## 1. AC 达成（AC-LS4B-1…10 全 MET）

| AC | 结果 | 关键证据（实跑） |
|---|---|---|
| **AC-LS4B-1 能力门禁/四象限** | MET | Core `core.ping` 增 `source.reattest/1`（`tests/core/test_host_control.py::test_ping_announces_the_reattest_capability`、`tests/fea11/test_source_reattest.py::test_reattest_uses_the_single_location_refresh_sql` 邻域）；Host `SourceReadCoordinator.SupportsReattestAsync` 仅用 `core.ping` 探测并缓存，缺失/异常 → **不 mint、不发送、不建文件**（`SourceReattestTests.Enumerator_MissingCapability_SendsNothing_AndKeepsTheTypedSkip` / `Enumerator_CapabilityProbeFailure_IsTreatedAsMissing`）；旧 Core 行为不变（legacy 构造器用例；gated IPC phase A 现状 skip） |
| **AC-LS4B-2 Host 候选精确性** | MET | `SourceRootReattestPlanner` 纯函数矩阵 13 例：旧条目 revoked/恰 1 根、live 唯一/恰 1 根、路径 normalize 相等、volume/file 相等、`live.CreatedAt > old.RevokedAt`、kind 非 folder → 候选；其余（旧条目缺失/未撤销/多根、无 live、多 live 歧义、路径不等、身份不等、时间序不成立、未知 kind/坏 digest/21 projects/畸形 target）→ typed skip、零 wire（`SourceReattestTests` 24 passed）；Host 不发送时目标保持既有 typed skip |
| **AC-LS4B-3 Core 身份门禁与零写** | MET | closed shape 恰 2 键（host-control 层 + 模块层双层）；host-only/session 守卫沿用既有码；grant 缺失/过期/撤销 → `SOURCE_ACCESS_DENIED`/`SOURCE_GRANT_EXPIRED`/`SOURCE_GRANT_REVOKED`（与 §6 优先级一致）；`grant.scope.source_id` 不符 / 四键身份（digest/volume/file/size 各一例）不符 / 无 current location / folder grant → `SOURCE_ACCESS_DENIED`，逐例 **16 表快照零写**（`test_reattest_refuses_when_the_grant_is_not_live`、`test_reattest_requires_the_grant_scope_source`、`test_reattest_requires_the_same_physical_identity[4]`、`test_reattest_without_a_current_location_is_refused`、`test_reattest_rejects_folder_grants`） |
| **AC-LS4B-4 单行写/幂等/单调** | MET | 成功仅改 `registry_id/authorization_generation` 两列（逐列 diff == {registry_id, authorization_generation}），`last_verified_at` 保持原值（哨兵 `2026-01-01T00:00:00.000+00:00` 逐字节不变）、`observed_at`/identity/is_current/location_id 不变、location 行数不变、`page_bindings` 逐行不变、除 `source_locations` 外 16 表哈希全等；重复调用 `updated:0` + 快照字节不变；同 registry 代次回退 → 0 行、跨 registry 代次 1 允许（`test_reattest_updates_only_the_two_auth_columns`、`..._is_idempotent_...`、`..._generation_is_monotonic_...`）；单点 SQL 判别：全 `src/**` 仅 `library.py` 含 `UPDATE source_locations SET registry_id` 1 处 |
| **AC-LS4B-5 无授权/无 identity 重建/不扩面** | MET | Core 不创建/复活/延长 grant（拒绝路径 16 表零写；成功路径仅 location 两列）；Host Registry 不新增/撤销/改 roots/identity/generation（gated IPC 断言 reattest 前后条目身份串全等，仅既有 mint `last_used_at`）；不新增 source/version/entry；请求无路径；无新错误码（错误码 ⊆ C-16 §6 闭集 ∪ 既有 envelope 守卫）；无新 wire minor（`PROTOCOL_MINOR=3`）/schema/依赖；folder 拒绝；**不新增 UI→Host 命令**（C-07 registry 111 不变，`SourceRecoveryUiTests.RecoverySurface_AddsNoWireCommand_AndKeepsTheFrozenCommandCount`） |
| **AC-LS4B-6 触发与恢复** | MET（**仅枚举恢复**） | gated 真实 IPC（`NEWMANGA_FEA11_IPC=1`）：真实 Python Core + 真实 Registry + 真实 zip。phase A（B1 只改 Registry，Core 行仍旧）→ 枚举 0 target / skip 1；phase B（生产 enumerator+coordinator）→ **恰 1 帧 `ReattestSourceLocation`**（payload 恰 `{grant_id, source_id}`，无绝对路径）→ Core 行两 auth 列更新 → 重枚举返回 live `(registry_id, generation)` → target 入集；其它 14 表不变、审计列不变、Host Registry 不变、**零重导入/零 apply**。App 侧成功分支请求既有 `RequestSourceScanRefresh` 恰 1 次、失败分支 0 次 |
| **AC-LS4B-7 零漂移/门禁** | MET | 见 §3：pins 18/18、check（默认+`-TaskPath`）PASS(3 warnings)、API inventory EXIT=0、scope PASS（见 `scope-validation.log`）、全量 pytest **3360/10**（基线 3317/10 不降）、全量 .NET **1644/0/94**（基线 1617/0/93 不降；+27 passed/+1 skipped 归本卡新增测试与 gated skip）、跑后 `verification/FEA-09` 已恢复 CLEAN |
| **AC-LS4B-8 不夸大** | MET | 只承诺「B1 显式重授权后无需重导入/apply，**枚举**恢复」；不承诺撤销后自动恢复/自动重新授权/folder；`roots_available`/B2 未实现（字段冻结）；`source_reset_registry` 后无旧条目可桥接（需重导入）；L-R1 未全修；扫描执行面 limitation L-S4-B-1 如实登记（见 §4） |
| **AC-LS4B-9 每轮至多一次 reattest** | MET | enumerator 按 source_id 去重 + 每轮每候选恰 1 次发送、失败不重试（`SourceReattestTests.Enumerator_AttemptsEachSourceAtMostOncePerRound`：同一 source 两条 target → 恰 1 次尝试、无第二轮重读）；gated IPC 恰 1 帧 |
| **AC-LS4B-10 措辞红线** | MET | 卡/EV/Handoff 无「自动恢复/自愈/自动重新授权」承诺；App 成功文案保持既有「已重新授权…请重新预览」，判别用例断言 VM 文案与 notice 均不含红线词；`reattest` 语义在代码注释/文档中明确为「事实传播，不是授权/恢复动作」 |

### 判别性（11/11 RED_AS_EXPECTED，`logs/discrimination.log`）

删/放宽每一条红线实现点后，对应用例必红；恢复后逐字节复原并复绿：

| # | 破坏点 | 目标用例 | 结果 |
|---|---|---|---|
| B1 | 删 Core 四键身份校验 | `-k same_physical_identity` | RED |
| B2 | 删 Core `grant.scope.source_id` 校验 | `-k requires_the_grant_scope_source` | RED |
| B3 | Core 用新时间戳覆盖 `last_verified_at` | `-k updates_only_the_two_auth_columns` | RED |
| B4 | 放宽 closed shape（双层一起去掉） | `-k non_closed_shapes` | RED |
| B5 | 删 folder 排除 | `-k rejects_folder_grants` | RED |
| B6 | 删 Host 时间序校验 | `Plan_HistoricalDuplicate…` | RED |
| B7 | 删 Host 多 live 歧义守卫 | `Plan_TwoLiveEntries_AreAmbiguous…` | RED |
| B8 | 删 Host 能力门禁 | `Enumerator_MissingCapability…` | RED |
| B9 | 删 App 成功分支 refresh 触发 | `ReauthorizeSuccess_Requests…` | RED |
| B10 | App 失败分支也 refresh | `ReauthorizeFailure_RequestsNoScanRefresh` | RED |
| B11 | App 成功 toast 改「自动恢复」 | `ReauthorizeSuccess_Requests…` | RED |

驱动：`tools/discrimination.py`（每例比对 sha256 + 恢复后复绿；`restored_tree_git_status` 显示交付文件在工作树中属正常，逐例 restore_sha256=MATCH）。

## 2. 定向 / gated 证据（实跑）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| Core 定向 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_reattest.py tests/core/test_core_scan_target_commands.py -q` | **100 passed in 8.27s** | `logs/feature.log` |
| 回归（host_control+run_grant） | `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **89 passed in 8.05s**（基线 74 的实跑计数为 89，无失败） | `logs/regression-74.log` |
| Host 单测 | `dotnet test … --filter "FullyQualifiedName~SourceReattest"` | **24 passed / 0 failed / 0 skipped** | `logs/host-unit.log` |
| App 单测 | `dotnet test … --filter "FullyQualifiedName~SourceRecoveryUiTests"` | **18 passed / 0 failed** | `logs/app-unit.log` |
| gated 真 IPC | `NEWMANGA_FEA11_IPC=1 dotnet test … --filter "FullyQualifiedName~Fea11ScanIpc"` | **4 passed / 0 failed**（含新「B1→reattest→枚举恢复」闭环） | `logs/host-ipc.log` |
| 全量 Python | `pytest tests -q` | **3360 passed / 10 skipped in 251.59s**（基线 3317/10，不降；+43 为本卡新增用例） | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test NewManga.sln -c Release`（cwd `apps/desktop-avalonia`） | **1644 passed / 0 failed / 94 skipped**（8 程序集：21+38+253+117+31+247+167+770；基线 1617/0/93，+27/+1 归本卡） | `logs/full-dotnet.log` |
| 判别性 | `python tools/discrimination.py` | **PASS 11/11 RED_AS_EXPECTED** | `logs/discrimination.log` |
| gated IPC 证据快照 | 测试落盘 | `reattest-ipc.json/.txt`（见 §4 L-S4-B-1） | fixture 根 `G:/CODEX/New Manga.workspace/FEA-11/fixtures/scan-*/` |

- 跑后恢复：全量 .NET 重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson` → 已 `git checkout -- verification/FEA-09`，`git status -- verification/FEA-09` 为空。
- gated IPC 关闭时该用例按 `Fea11ScanIpcFact` skip（全量 .NET 的 94 skipped 含此 1 条 + 既有 93 条）。

## 3. 治理 / 零漂移（实跑）

| 门禁 | 命令 | 结果 | 日志 |
|---|---|---|---|
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**；C16 `a7f57ebdbd67`（其余 17 不变） | `logs/gates.log` |
| check（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**，EXIT=0 | `logs/gates.log` |
| check（`-TaskPath`） | `… check.ps1 -TaskPath doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | **PASS (3 warnings)**，EXIT=0 | `logs/gates.log` |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT=0** | `logs/gates.log` |
| scope | `python verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/tools/scope_validation.py` | **PASS**（交付 diff ⊆ allowed_paths；zero-drift=[]；`PROTOCOL_MINOR=3`；C16 pin 命中；C-07 registry 无 `ReattestSourceLocation`） | `scope-validation.log`、`changed-files.txt` |
| 契约字节 | C-16 v1.5 sha256 | `a7f57ebdbd673a6bac0e148f54223301bb4117e0cbeafce008ab7adc1347b22d` = 冻结 pin；`doc/plan/**` 交付零 diff | pins + scope |

## 4. 已知 limitation（必须保留；均未宣称修复）

- **L-S4-B-1（本卡登记，DSH 2026-11-07 裁决）**：reattest 后**枚举恢复**成立（target 不再丢失、不再 typed skip），
  但该 target 的**扫描执行面**仍被既有 `SourceScanExecutor.ResolveRegistryEntry` 的「同路径 revoked 旧条目
  fail-closed」拦住（`Revoke` 累积旧条目，路径精确匹配先命中 revoked → 返回 null → tick typed `SOURCE_ACCESS_DENIED`）。
  **本卡只承诺枚举恢复**（冻结 AC-LS4B-6 原文），卡/Handoff/EV 不写「扫描恢复/扫描成功」；gated IPC 证据中
  `tick_verdict.last_result` 如实记录。该限制后续另卡（与 B2/roots 管理一起设计）。
- **B2 `roots_available`**：字段已随 C-16 v1.5 冻结（additive），**实现延后**（无消费者；本卡未接线）。
- **folder（L-S4-2）**：folder 身份键口径未修；reattest 明确排除 folder（Host planner 与 Core 双侧拒绝）。
- **`source_reset_registry` 后无旧条目可桥接**：reset 丢弃全部条目 → 无 revoked 旧条目可反查 → 不能 reattest，
  用户仍需重导入。
- **不自动重新授权 / 不自动重建 identity / 撤销后不放行**：仅 live 非撤销条目 + 同一物理身份 + 显式动作后的
  事实传播；Core 不创建/复活 grant。
- **L-S4-1 / L-R1**：不宣称扫描/读切片全链路恢复；L-R1 未全修；多根 first-root 启发式未修。
- **revoked 行累积**：B1 每次显式重授权保留旧 revoked 条目（既有行为），是 L-S4-B-1 的根因之一。

## 5. 真实性 / 未跑（NOT_RUN）

- **NOT_RUN**：真实用户数据（禁用，仅隔离 fixture）；push（未执行）；linked worktree（未创建）；B2 实现（未实现）；
  多根/roots 管理 UI（不在本卡）；folder 恢复（L-S4-2）；撤销后自动恢复（红线禁止）。
- 全量 .NET 的 gated IPC 用例在未设 `NEWMANGA_FEA11_IPC=1` 时 skip（已在 §2 单独 gated 实跑记录 4 passed）。
- 所有数字均来自上表命令的实跑输出；未用「预期/应为」替代。

## 6. 复现（repo root）

```powershell
C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_reattest.py tests/core/test_core_scan_target_commands.py -q
C:/Python314/python.exe -m pytest tests -q                     # 3360 passed / 10 skipped
cd apps/desktop-avalonia
dotnet test tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceReattest"
dotnet test tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRecoveryUiTests"
$env:NEWMANGA_FEA11_IPC='1'; dotnet test tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~Fea11ScanIpc"
dotnet test NewManga.sln -c Release                          # 1644 passed / 0 failed / 94 skipped
cd ../..
C:/Python314/python.exe verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/tools/discrimination.py
C:/Python314/python.exe verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/tools/scope_validation.py
C:/Python314/python.exe verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/tools/gen_manifest.py --commits ec171f0d3,3ccb0509e,f76620e39,c4345a632,30bdeb4ce --delivery-head 30bdeb4ce
# 跑后如 tracked 证据被测试改写：
git checkout -- verification/FEA-09
```
