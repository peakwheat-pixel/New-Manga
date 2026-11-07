---
task: FEA-11-L-S4-B-AUTO-RECOVERY-1
title: 独立实现 Review r1 — B1 重授权后的零交互枚举恢复（C-16 v1.5 §2.5）
reviewer: DSH fresh-context subagent（r1；未参与本卡实现/返修/scope review）
session: 5ad3bb8a-6c5a-4ac5-8513-4b7ccaadaa68
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: 30bdeb4ce
verdict: approved
---

# 独立实现 Review r1 — FEA-11-L-S4-B-AUTO-RECOVERY-1

> **审查基线**：实现/测试字节 = `30bdeb4ce`（delivery head）；证据字节 = `9dda04b75`（main HEAD，docs-only 提交）；卡 `doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md`；契约 C-16 v1.5 `doc/plan/FEA-C16_SOURCE_READ_WIRE_DRAFT.md`（`a7f57ebd…`，与 `c6ca1aa3c` 字节相同）；载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-07-C16-V15.md`；scope `doc/reviews/C16-V15-BATCH-scope-r1.md`。
>
> **独立性**：本 Review 由 fresh-context 子 agent 执行（session `5ad3bb8a-6c5a-4ac5-8513-4b7ccaadaa68`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）。审查者未参与本卡实现、返修或 scope review；除本报告外只读，未改实现/测试/证据/卡/契约，未 `git add/commit/push`。破坏性复跑只临时改 2 个实现文件，已逐字节恢复并用 sha256 复核（§4）。

## 0. 结论先行

- **P0 = 0；P1 = 0；P2 = 0；P3 = 5**（均为证据/流程可改进项，非产品行为缺陷，不阻断集成）。
- **verdict：`approved`**。C-16 v1.5 §2.5 的条件单行写、Host 候选精确性/能力门禁、App 成功分支触发、gated 真实 IPC 枚举恢复与扩域合规均与冻结契约/卡面一致；未发现越权写、自动重新授权、identity 重建或扫描执行面夸大。
- **必须保留的口径**：本卡只兑现「B1 显式重授权后无需重导入/apply，**枚举**恢复」。扫描执行面仍被既有 `ResolveRegistryEntry` 的 revoked-exact-match fail-closed 拦住，gated IPC 的 tick 结果如实为 `error`（L-S4-B-1）；不得据此写「扫描恢复/自愈/自动恢复」。
- 独立实跑：Core 定向 **100**、回归 **89**、Host **24/0/0**、App **18/0/0**、gated IPC **4/0/0**、全量 pytest **3360/10**（独立复跑，255.31s，EXIT=0）、pins **18/18**、check ×2 **PASS(3 warnings)**、API inventory **EXIT=0**。

## 1. 范围与方法

- 只读核对 5 个交付提交：`ec171f0d3`（Core）→ `3ccb0509e`（Host）→ `f76620e39`（App）→ `c4345a632`（测试）→ `30bdeb4ce`（DSH 批准扩域）；证据在 `9dda04b75` 的 `verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/**`。
- 逐项对照：C-16 v1.5 §2.5/§1/§6、卡 In/Out/AC-LS4B-1…10/红线/L-S4-B-1、DSH 扩域裁决；代码真实字节用 `git show 30bdeb4ce:<path>` / 工作树（工作树与 delivery 的 `src/apps/tests` 零 diff）。
- 独立实跑、独立只读 scope 检查和 2 个破坏点；所有命令均在 `G:\CODEX\New Manga` 或 `apps/desktop-avalonia` 下执行。
- 证据中的 `RESOURCE-MANIFEST.json` 逐文件 sha 用独立脚本复核（§3 F/§5）。

## 2. A–G 逐项核对

### A. 契约 §2.5 一致性 — **PASS**

| 核对项 | 判定 | 证据 |
|---|---|---|
| 请求恰 2 键 `{source_id, grant_id}`，closed shape；缺键/多键/类型错 `INVALID_REQUEST` | PASS | `src/application/sources/reattest.py:77,181-192`；`src/bootstrap/core_service.py:5095-5105`；两层校验（host-control handler + 模块）；`tests/fea11/test_source_reattest.py:534-577`、`tests/core/test_host_control.py:1095-1122` |
| 校验顺序 host-only→shape→grant live/未过期/未撤销+`scope.source_id`→四键身份→条件 UPDATE | PASS | envelope/session 在 `core_service.py:1445-1457`；dispatch 分支 `:1517-1531`；handler `:5071-5124`；模块 `reattest.py:116-175`；grant 优先级复用 `_checked`：`src/infrastructure/resource_channel/source_read_refs.py:855-880`；source_id 校验 `reattest.py:125-126`；身份 `:138-141,205-229` |
| 只写 `registry_id/authorization_generation`；`last_verified_at` 读原值回写、不取 now | PASS | `reattest.py:158-167` 传入 `location.get("last_verified_at")`；读取在 `core_service.py:5126-5147`；唯一 SQL `src/infrastructure/sqlite/library.py:2324-2339`。SQL 的 SET 含第三列 `last_verified_at`，但写的是 SELECT 读到的原值（契约 §2.5 明确要求「读取原值并原样回写」）；逐列 diff 断言 changed == {`registry_id`, `authorization_generation`}：`tests/fea11/test_source_reattest.py:340-343` |
| 复用唯一 SQL，无第二份 | PASS | `src/**` 中 `UPDATE source_locations SET registry_id` 仅 `library.py` 一处；判别测试 `tests/fea11/test_source_reattest.py:619-626`；`commit_source_location_auth_refresh` 只是同一 SQL 的事务包装（`library.py:2341-2353`） |
| 拒绝/无匹配零写 | PASS | 服务在 update 前完成全部校验；逐负例快照 `tests/fea11/test_source_reattest.py:412-527`（grant 缺失/过期/撤销、source_id、四键身份、无 current location、folder）；host-control envelope 用例 `tests/core/test_host_control.py:1043-1093,1124-1172` |
| 幂等 `updated:0` 且零写 | PASS | SQL `(registry_id <> ? OR authorization_generation <= ?)` + 相等分支；`tests/fea11/test_source_reattest.py:364-383`（重复调用后逐表快照字节相等） |
| 单调：同 registry 不倒退、跨 registry 允许 1 | PASS | `library.py:2329-2337`；`tests/fea11/test_source_reattest.py:385-405`（reg-high gen5→gen4 = 0；reg-other gen1 = 1） |
| folder 排除 | PASS | `reattest.py:128-133`（`container_facts is None` → `SOURCE_ACCESS_DENIED`）；`source_read_refs.py:1021,1058`；`tests/fea11/test_source_reattest.py:506-526` |
| 响应 closed shape `{source_id, updated, version}` | PASS | `reattest.py:175`；`tests/fea11/test_source_reattest.py:328-332`；Host 侧严格三键校验 `SourceReadCoordinator.cs:204-233` |
| 无新错误码 | PASS | `tests/fea11/test_source_reattest.py:629-650`（codes ⊆ §6 闭集 ∪ `INVALID_REQUEST`）；`test_host_control.py:1124-1172` 用 §6 category |

**结论**：A 全部 PASS。特别注意：SQL 的 `last_verified_at = ?` 不是「刷新审计时间」，而是契约要求的原值回写；测试以哨兵值逐字节证明未变，且 changed-set 只含两列。

### B. Host 候选精确性/能力门禁 — **PASS**

| 核对项 | 判定 | 证据 |
|---|---|---|
| 能力探测 `source.reattest/1`，仅用 `core.ping`，缓存；旧 Core 不发 | PASS | Core 广告 `core_service.py:1632-1636`；Host `SourceReadCoordinator.cs:63,143-150`；enumerator 能力门 `SourceScanScheduler.cs:2152,2198-2215`；缺失用例 `SourceReattestTests.cs:376-398`；探测异常 `:401-424` |
| planner 候选规则：旧条目已撤销、恰 1 根、live 唯一且恰 1 根、路径 normalize 相等、volume/file 相等、`live.CreatedAt > old.RevokedAt`、非 folder | PASS | `SourceRootReattestPlanner.cs:181-246`（逐规则分支）；候选矩阵 `SourceReattestTests.cs:123-316`（含旧条目缺失/未撤销/多根、无 live、双 live、路径/卷/文件不符、live 多根、时间序、坏时间戳、畸形 target、folder）；13 类负例均 `IsCandidate=false` |
| 每轮每源至多一次；失败 typed 即止 | PASS | `seen` 去重 `SourceScanScheduler.cs:2129-2145`；单次发送 `:2157-2185`；失败 catch 仅日志、不重试；`SourceReattestTests.cs:427-471`（同 source 两 target → 1 次尝试、无预检二次读取） |
| 不新增 UI→Host 命令（命令数 111 不变） | PASS | `HostCommandRegistry.cs` 在 `c6ca1aa3c..9dda04b75` 零 diff；`generate_api_inventory.py --check` EXIT=0（`IHostController` 54 / `IRunController` 6 / 合计 61）；App 只复用既有 `RequestSourceScanRefresh()`（`ImportDockViewModel.cs:589`；端口 `SourceRecoveryUiTests.cs:1341-1352`） |
| 不自动重授权/不重建 identity | PASS | planner 只产生候选，不调用 `Register/Revoke`；witness grant 走既有 `IssueLockedAsync`（`SourceReadCoordinator.cs:186-198,498-619`）；Core 不创建/复活 grant；gated 测试断言 Host Registry 身份串不变（`Fea11ScanIpcTests.cs:657`） |
| `scope.version="1"` 作为 witness grant 占位合理 | PASS | `SourceRootReattestPlanner.cs:87` 的 `EnumeratedTargetVersion="1"` 与既有扫描 target 的占位同值（`SourceScanScheduler.cs:2319-2323`）；§2.5 不消费 `scope.version`；`IssueLockedAsync` 只要求非空（`:509`）；gated 真实 Core 接受并完成闭环 |
| 旧 Core 行为不变（legacy 构造器） | PASS | `SourceReattestTests.cs:474-488`；`SourceScanScheduler.cs:2078` 仅在 `_sources != null && _options != null` 时预热 |

**结论**：B 全部 PASS；候选规则与 §2.5 Host 前置义务逐项对应，歧义/部分匹配 fail-closed。

### C. 触发与恢复（AC-LS4B-6） — **PASS（仅枚举恢复）**

| 核对项 | 判定 | 证据 |
|---|---|---|
| B1 显式重授权成功分支调用既有 refresh 恰 1 次；失败 0 次 | PASS | `ImportDockViewModel.cs:572-578`（失败提前 return）→ `:589` 唯一新增 `RequestSourceScanRefresh`；`tests/…/SourceRecoveryUiTests.cs:1291-1339`（成功 1、失败 0） |
| reattest 后枚举 target 恢复；无需重导入/apply | PASS | gated `Fea11ScanIpcTests.cs:549-729`：phase A 0 target/skip 1；phase B 恰 1 帧 `ReattestSourceLocation`（payload 恰 `{grant_id, source_id}`，无路径）→ Core 两 auth 列更新 → 重枚举 live pair 入集；`reattest-ipc.json` 记录 `reimport_or_apply=false` |
| 不宣称扫描执行恢复（L-S4-B-1） | PASS | gated 测试末尾如实记录 `tick_verdict.last_result="error"`；`verification/…/logs/ipc-closed-loop.json:29-32`；卡/EV/Handoff 均登记 L-S4-B-1，未写「扫描恢复/扫描成功」 |
| 失败 typed、无自动重试成自动恢复 | PASS | enumerator 失败仅 warning、不重试（`SourceScanScheduler.cs:2176-2184`）；App 失败分支 0 refresh；`SourceReattestTests.cs:427-471` |

**结论**：C PASS，但严格限定为**枚举恢复**；扫描执行面 limitation 保持。独立复跑 gated IPC 4/0/0，证据中的 tick error 与最新 fixture 再次一致。

### D. 独立实跑 — **PASS**

| 场景 | 命令 | 结果 |
|---|---|---|
| Core 定向 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_reattest.py tests/core/test_core_scan_target_commands.py -q` | **100 passed in 8.62s** |
| 回归 | `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **89 passed, 1 warning in 11.55s** |
| Host 单测 | `dotnet test tests/NewManga.Host.Tests/… -c Release --filter "FullyQualifiedName~SourceReattest"` | **24 passed / 0 failed / 0 skipped** |
| App 单测 | `dotnet test tests/NewManga.App.Tests/… -c Release --filter "FullyQualifiedName~SourceRecoveryUiTests"` | **18 passed / 0 failed / 0 skipped** |
| gated 真 IPC | `NEWMANGA_FEA11_IPC=1 dotnet test … --no-build --filter "FullyQualifiedName~Fea11ScanIpc"` | **4 passed / 0 failed / 0 skipped**（含新闭环） |
| 全量 pytest | `C:/Python314/python.exe -m pytest tests -q`（输出落 `.workspace/.../review/full-pytest-review.log`） | **3360 passed, 10 skipped, 11 warnings in 255.31s；EXIT=0**（交叉核对 Lead 的 3360/10） |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PIN AUDIT: PASS (all 18)**；C16 `a7f57ebdbd67` |
| check（默认） | `pwsh -NoProfile -File tools/governance/check.ps1` | **PASS (3 warnings)**，EXIT=0 |
| check（`-TaskPath`） | 同上 `-TaskPath doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md` | **PASS (3 warnings)**，EXIT=0 |
| API inventory | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT=0**（54/6/61） |
| 全量 .NET | 未由 Review 重跑（避免改写 tracked `verification/FEA-09`）；交叉核对 `logs/full-dotnet.log`：8 程序集 **1644 passed / 0 failed / 94 skipped**，与 Handoff 一致 | **交叉核对 PASS；Review 侧 NOT_RUN** |

独立只读 scope 复核（不写证据）：`c6ca1aa3c..9dda04b75` 共 **39** 个变更；scope 工具把 4 个 Lead docs（2 个 DSH 并发 docs + r8/r9）列为 `CONCURRENT_NON_DELIVERY`，故 `delivery=35`。独立检查把 r8/r9 按卡允许 glob 视为 allowed，仍 `out_of_scope=[]`、`forbidden=[]`；`PROTOCOL_MINOR = 3`；C16 sha `a7f57ebd…`；`HostCommandRegistry.cs` 零 diff。`git status` 无本 Review 造成的 tracked 变更；`verification/FEA-09` 零 status（未写）。

### E. 扩域合规 — **PASS**

- `git show --stat 30bdeb4ce`：仅 `tests/core/test_core_service.py`（+2，两处精确 capability 列表各 +1 行 `"source.reattest/1",`）与 `tests/fea09/test_referenced_wire.py`（+1，同一模式）；共 2 文件 3 行，零行为改动。
- 逐行核对：三处均只是既有精确列表追加预期，未放宽/删除其他断言；C-16 v1.5 §0 的新能力确使原断言失败（同 v1.3 `source.read.run/1` 先例）。
- **.NET 预批未消耗**：`SourceReattestTests.cs`/`Fea11ScanIpcTests.cs`/`SourceRecoveryUiTests.cs` 之外无 .NET 测试文件改动；全量 .NET 无精确 capability 列表断言（既有断言为 `Contains`）。Handoff 的「.NET 未使用预批」属实。
- 扩域未改变产品行为/契约/证据；`core.ping` 只增一个能力（`core_service.py:1626-1637`）。

### F. 证据/判别性 — **PASS（含 5 项 P3 说明）**

- **EV/Manifest 逐文件 sha**：独立脚本复核 `RESOURCE-MANIFEST.json` 的 15 个交付文件 + 17 个证据文件，共 32 项，**worktree 字节全部匹配**。其中 5 个既有文件（`src/bootstrap/core_service.py`、`SourceScanScheduler.cs`、`ImportDockViewModel.cs`、`Fea11ScanIpcTests.cs`、`test_core_scan_target_commands.py`）的 **committed blob** sha 与 manifest 不同，原因是 `core.autocrlf=true` 下工作树 CRLF、Git blob 存储 LF；`git diff 30bdeb4ce -- <paths>` 为空，内容零漂移。属 P3 证据口径说明（见 R1-P3-01）。
- **`logs/discrimination.log` 11/11 可信**：11 例均 `status=RED_AS_EXPECTED`、`restore_sha256=MATCH`、逐例有目标用例与失败输出；独立复现 2 个破坏点（Core 身份、Host 能力门禁）均 RED（§4）。日志末尾 `restored_tree_git_status` 显示 M/??，说明该轮跑在提交前的同一交付字节上；见 P3 R1-P3-02。
- **`ipc-closed-loop.json` 如实记录 tick error**：`last_result="error"`，`enumeration_recovered=true`、`reattest_frames=1`、payload 恰 ids、`host_registry_unchanged=true`、`other_tables_unchanged=true`；与 L-S4-B-1 一致。
- **scope diff ⊆ allowed_paths（35 文件）**：`changed-files.txt` 35 行；`scope-validation.log` `changed_count=39 delivery=35 concurrent_non_delivery=4`、`result=PASS`、`PROTOCOL_MINOR=3`、C16 pin match、`COMMAND_REGISTRY_HAS_REATTEST=False`。独立复核见 §2 D。
- **禁止面零 diff**：`doc/plan/**`、`doc/contracts/**`、`src/infrastructure/sqlite/library.py`、schema/migrator、requirements/pyproject/package、`HostCommandRegistry.cs`、C-07 registry 均零 diff；全 `src/**` 唯一 SQL 留在 `library.py`。
- **数字一致**：`feature.log` 100、`regression-74.log` 89、`host-unit.log` 24、`app-unit.log` 18、`host-ipc.log` 4、`full-pytest.log` 3360/10、`full-dotnet.log` 1644/0/94、`gates.log` 18/18 + PASS(3) + EXIT=0 + API EXIT=0；与 Handoff/EV 一致。唯一措辞差异是 EV 的「16 表快照」与实测动态快照 36 张表（更强）不符，见 P3 R1-P3-04。
- **跑后恢复**：Review 的 gated IPC/定向测试未改 tracked 证据；全量 pytest 后 `git status --porcelain` 为空；未执行全量 .NET，故未触碰 `verification/FEA-09`（现状 clean）。

### G. 不夸大 — **PASS**

- 卡/EV/Handoff 中「自动恢复/自愈/自动重新授权/扫描恢复/扫描成功」的所有出现均为**禁止/否定/limitation**语境；无承诺句。App 成功文案保持「已重新授权…请重新预览」；判别测试断言 VM 文案与 notice 均不含红线词（`SourceRecoveryUiTests.cs:1291-1319`）。
- 只承诺「B1 显式重授权后无需重导入/apply，**枚举**恢复」；B2 `roots_available` 未实现；folder（L-S4-2）双侧拒绝；`source_reset_registry` 后无旧条目可桥接；L-S4-1/L-R1 未全修；L-S4-B-1 保留。
- 代码注释/文档把 reattest 明确为「事实传播，不是授权/恢复动作」；Core 模块/docstring 与 Host/App 注释同口径。

## 3. AC-LS4B-1…10 判定

| AC | 判定 | 关键证据 |
|---|---|---|
| **AC-LS4B-1 能力门禁/四象限** | **MET** | `core.ping` 仅增 `source.reattest/1`（`core_service.py:1626-1637`）；Host 只用 ping 探测/缓存（`SourceReadCoordinator.cs:143-150`）；缺失/异常不发（`SourceReattestTests.cs:376-424`）；legacy 构造器保持旧行为（`:474-488`）；gated 新×新生效 |
| **AC-LS4B-2 候选精确性** | **MET** | `SourceRootReattestPlanner.cs:181-246`；13 类负例 + 精确候选（`SourceReattestTests.cs:123-316`）；歧义/多根/时间序/身份/路径不匹配均零 wire |
| **AC-LS4B-3 Core 身份门禁与零写** | **MET** | closed shape 双层（`core_service.py:5095-5105`、`reattest.py:181-192`）；host-only/session（`test_host_control.py:1043-1093`）；grant 状态/scope/四键/无行/folder 均 typed；逐例零写（`test_source_reattest.py:412-527`） |
| **AC-LS4B-4 单行写/幂等/单调** | **MET** | 只改两 auth 列、`last_verified_at` 原值哨兵、行数/其余列/`page_bindings` 不变（`test_source_reattest.py:312-405`）；重复 `updated:0` 零写；同 registry 不倒退、跨 registry 1 允许；唯一 SQL 判别 `:619-626` |
| **AC-LS4B-5 无授权/无 identity 重建/不扩面** | **MET** | Core 不创建/复活 grant（`_grants == {grant_id}` 断言）；Host Registry 不新增/撤销/改 roots/identity/generation（gated `Fea11ScanIpcTests.cs:657`）；无新 source/version/entry；无新错误码/能力（除冻结能力）/wire minor/schema/依赖；无新 UI 命令（API 61、registry 零 diff）；folder 拒绝 |
| **AC-LS4B-6 触发与恢复** | **MET（仅枚举恢复）** | App 成功分支 1 次、失败 0 次（`SourceRecoveryUiTests.cs:1291-1339`）；gated IPC phase A skip→phase B 恰 1 帧→枚举 live pair 入集；`tick_verdict.last_result=error` 如实登记 L-S4-B-1；不宣称扫描执行恢复 |
| **AC-LS4B-7 零漂移/门禁** | **MET** | pins 18/18；check 默认 + `-TaskPath` PASS(3)；API EXIT=0；scope PASS；全量 pytest 3360/10（基线 3317/10）、全量 .NET 1644/0/94（基线 1617/0/93，交叉核对日志）；`verification/FEA-09` clean |
| **AC-LS4B-8 不夸大** | **MET** | 只承诺枚举恢复；撤销后不自动；不自动重新授权；folder/B2/L-S4-1/L-R1/扫描执行面 limitation 全部保留；`source_reset_registry` 后需重导入 |
| **AC-LS4B-9 每轮至多一次** | **MET** | `seen` 去重（`SourceScanScheduler.cs:2129-2145`）；失败不重试（`:2176-2184`）；单测同 source 两 target → 1 次（`SourceReattestTests.cs:427-471`）；gated 恰 1 帧 |
| **AC-LS4B-10 措辞红线** | **MET** | 卡/EV/Handoff 无红线**承诺**；App 测试断言 VM 文案与 notice 0 红线词（`SourceRecoveryUiTests.cs:1291-1319`）；reattest 语义明确为事实传播 |

## 4. 破坏性复跑记录（自选 2 点）

> 备份与恢复均在 `G:\CODEX\New Manga.workspace\FEA-11-L-S4-B-AUTO-RECOVERY-1\review\backup\`；恢复后 `git status --porcelain` 为空，`verification/FEA-09` 零 status。

### 4.1 Core：删除四键身份校验（B1 同类破坏点）

- 文件：`src/application/sources/reattest.py`；破坏方式：删除 `_require_identity` 中 `content_digest/volume_serial/file_id/size_bytes` 与 grant facts 的比较与 `_denied`。
- `before_sha256=694f21725f15c5bddc94619640e3bd45be6ac2b047050d3a67ceef429fd6e699`；`broken_sha256=deb27b557e7e5d90f1b3b47046d0d8fe922b7219a7b04bed6caa01f2fb23e628`。
- `pytest tests/fea11/test_source_reattest.py -q -k same_physical_identity` → **4 failed, 23 deselected**（digest/volume/file/size 四例全红），EXIT=1。
- 恢复后 sha256 回到 `694f2172…`（MATCH）；同命令 **4 passed**，EXIT=0。

### 4.2 Host：删除能力门禁（B8 同类破坏点）

- 文件：`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs`；破坏方式：删除 `ReattestRevokedTargetsAsync` 中 `if (!await ProbeReattestCapabilityAsync(...)) return targets;` 门禁。
- `before_sha256=3583d30fbf7f676b3dad5fec1851a505a901697ff7cd9f83234bcb6504e74c32`；`broken_sha256=e8d10dc0455be6d4fa0b9b977856c3d217ddc6c88481e95c5ca752163e938e8e`。
- `dotnet test … --filter "FullyQualifiedName~Enumerator_MissingCapability"` → **1 failed / 0 passed**（`Assert.Empty` 失败：出现 `source reattest skipped code=NullReferenceExceptio…`），EXIT=1。
- 恢复后 sha256 回到 `3583d30f…`（MATCH）；重建并跑 `SourceReattest` → **24 passed / 0 failed / 0 skipped**，EXIT=0。

## 5. Findings

| ID | 级别 | 文件/位置 | 触发与影响 | 证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| R1-P3-01 | P3 | `verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/RESOURCE-MANIFEST.json`；5 个既有交付文件 | Manifest 的 `sha256` 取工作树字节；`core.autocrlf=true` 下 5 个既有文件工作树 CRLF 与 Git blob LF 的 sha 不同，直接用 `git show` 复核会误判 MISMATCH。内容零漂移。 | 独立脚本：32/32 worktree match；5 个文件的 committed blob sha 不同；`git diff 30bdeb4ce -- <paths>` 为空。 | Manifest 注明「worktree bytes / autocrlf」或在生成时按 canonical LF 归一化；不影响本卡行为。 | open（非阻断） |
| R1-P3-02 | P3 | `verification/…/logs/discrimination.log` | 日志末尾 `restored_tree_git_status` 为 M/??，且未记录运行 HEAD；说明该轮在提交前的同一交付字节上运行，严格追溯需结合 final commit/manifest。 | 日志 `:46-50`；实测 2 个破坏点均能独立复现 RED；manifest/工作树 sha 匹配。 | 未来判别性脚本记录 `git rev-parse HEAD`/`git diff --stat`，或直接在 delivery_head 上跑。 | open（非阻断） |
| R1-P3-03 | P3 | `verification/…/tools/scope_validation.py:210-224` | `COMMAND_REGISTRY_BASELINE=111` 是打印常量；工具只检查 registry 文本不含 `ReattestSourceLocation`，并未真正计数 111 条命令。 | 独立复核：`HostCommandRegistry.cs` 零 diff；API inventory 54/6/61、EXIT=0；因此 AC 实际成立，但工具判别力弱。 | 增加 registry 计数断言（或解析 `All.Count`），再报 PASS。 | open（非阻断） |
| R1-P3-04 | P3 | `verification/…/EV.md:26-28`、Handoff `:27` | EV/Handoff 写「16 表快照」，而 `test_source_reattest.py::_table_snapshot` 实际动态快照全部 36 张非 sqlite 表（更强）；gated 侧 `QueryScanTables` 为 15 表。 | `tests/fea11/test_source_reattest.py:260-273`；`schema_count.py` 实测 36 表；gated `Fea11ScanIpcTests.cs:359-365` 15 表。 | 将措辞改为「全表（36）/15 张扫描相关表」，避免数字误导。 | open（非阻断） |
| R1-P3-05 | P3 | `apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11ScanIpcTests.cs:935-950` | 新的 gated 闭环沿用既有 `FEA-11/fixtures/scan-*` 根，而本卡工作区隔离约定为 `.workspace/FEA-11-L-S4-B-AUTO-RECOVERY-1/`；不写 `verification/FEA-09`，也不污染 tracked 证据。 | EV §2 已披露；Review 复跑确认输出在 `.workspace/FEA-11/fixtures`；无 tracked 副作用。 | 在后续卡/测试中改为任务专用 fixture 根；本卡按既有 SeedAsync 约定保留并披露。 | open（非阻断） |

**无 P0/P1/P2 finding。**

### 残余风险（不构成 finding）

- **审计时间读-写竞态**：`last_verified_at` 由 SELECT 读原值、随后 UPDATE 原样回写；若并发 import 恰在两者之间刷新审计列，SQL 的 `last_verified_at IS NOT ?` 分支可能把旧值写回。当前 Core/测试未覆盖并发写者；属既有 A 卡 SQL 条件写语义的窄竞态，非本卡新增授权面，建议后续在 A 卡 SQL 层面评估。
- **witness grant 未显式撤销**：成功/失败后 grant 留在 ledger 直到 ≤300s TTL；无 page binding，未观察到可读放大；属资源卫生，建议后续统一回收。
- **全量 .NET**：Review 未重跑（避免改写 `verification/FEA-09` tracked 文件），以 Lead 的 1644/0/94 日志交叉核对；定向 Host/App/IPC 已独立复跑。

## 6. 结论

- **P0/P1/P2 = 0**；P3 均为证据/流程可改进项，不影响行为正确性、契约一致性或 AC 达成。
- **Decision：`approved`**。可将 `30bdeb4ce` 交 DSH 集成验证；集成时只需按 Lead 既有流程复跑门禁并保留 L-S4-B-1 的「仅枚举恢复」口径。若 DSH 要求零 P3，可先处置 R1-P3-01…05（均为文档/工具/测试路径改进，不改变产品代码）。
- **不建议**在本卡外扩：扫描执行面（`ResolveRegistryEntry`）、B2 roots 管理、folder（L-S4-2）、L-S4-1/L-R1 均应按卡面 limitation 另卡设计。

## 7. 真实性声明

- 本报告只写 `doc/reviews/FEA-11-L-S4-B-AUTO-RECOVERY-1-r1.md`；未修改实现/测试/证据/卡/契约，未 `git add/commit/push`，未运行真实用户数据，未创建 linked worktree。
- 所有实跑数字来自本 Review 的实际命令（§2 D/§4）；未跑项明确为 `NOT_RUN`（全量 .NET 未重跑；以 `logs/full-dotnet.log` 交叉核对）。
- 破坏性复跑前已备份原字节、结束后逐字节恢复并以 sha256 复核；仓库最终 `git status --porcelain` 为空，`verification/FEA-09` 零 status。
- gated IPC 复跑沿用测试既有 `.workspace/FEA-11/fixtures/scan-*` 根（未写 `verification/FEA-09`）；本卡定向/破坏性 fixture 均在 `.workspace/FEA-11-L-S4-B-AUTO-RECOVERY-1/` 下。
