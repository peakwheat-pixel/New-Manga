---
task: FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1
title: 独立实现 Review r1：Run 源范围解析恢复（L-S4-B-2：枚举 target 复用自身 live registry 身份；Host-only 零契约）
reviewer: DSH fresh-context subagent（r1；未参与本卡实现/返修/scope review；只读）
session: d7f8c2b3-c4e3-4dfd-b008-6d46b898f73c
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
reviewed_head: fad1ec776
reviewed_evidence_head: ca929aade
base_commit: 2ef3f1024
implementation_start: e78c144bb
verdict: approved
---

# 独立实现 Review r1 — FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1

> **审查基线**：实现/测试字节 = `fad1ec776`（实现 `f6b5a761a` + 测试/gated `fad1ec776`）；证据字节 =
> `ca929aade`（main HEAD，docs/evidence，`status` 未改）；卡
> `doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md`；权威 scope review
> `doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-scope-r1.md`（READY-TO-FREEZE；Host-only 形状；
> 0 UNFREEZE / 18 pins）；Handoff `doc/handoffs/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-fad1ec776.md`；
> 证据 `verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/**`。
>
> **独立性**：本 Review 由 fresh-context 子 agent 执行（session
> `d7f8c2b3-c4e3-4dfd-b008-6d46b898f73c`，parent `session-5f1e719c-f1f3-4193-8393-caf4d0936e4a`）。
> 审查者未参与本卡实现、返修或 scope review；除本报告外只读，未改实现/测试/证据/卡/契约，未
> `git add/commit/push`。破坏性复跑只临时改 `HostRuntime.cs`，结束后逐字节恢复并以 sha256 + `git status` 复核（§4）。
>
> **口径红线（本报告同样遵守）**：本卡只兑现**「B1 显式重授权 → 既有 refresh/reattest → 枚举 → Run 预授权/
> 冷源分类」**这一段的恢复。**不**承诺「Run 全面恢复」、**不**承诺自动恢复/自愈/自动重新授权/撤销后自动放行、
> **不**承诺扫描面（已由 L-S4-B-1 交付）、B2、folder（L-S4-2）、L-S4-1、L-R1、2C；managed-only Run 不依赖
> source 授权，不在承诺面内。

## 0. 结论先行

- **P0 = 0；P1 = 0；P2 = 0；P3 = 7**。全部 P3 为证据容器/文档精度/测试覆盖注释/可维护性项，不改产品行为、
  不改授权语义、不阻断集成。
- **verdict：`approved`**。`RunSourceRange.Resolve` 对枚举 target 确实改用其**自身 live
  `(registry_id, generation)`**（复用 L-S4-B-1 的 `SelectEnumeratedEntry`，不回落同路径 sibling）；非枚举
  target 仍走字节未变的 `ResolveRegistryEntry`；解析失败/异常最多计 `Unresolved`，不向 best-effort authorizer
  抛；live 但无 Core version 的枚举 source 正常进入 `ColdSources` 并走既有 bounded on-demand scan。
- **独立实跑（本 Review 亲自执行）**：build **PASS 0/0**；新单测 **9/0/0**；`SourceRegistryTests`
  **32/0/0**；gated 真 IPC `Fea11RunGrantIpc` **6/0/0**；定向 pytest **89 passed**；pins **18/18**；
  `check.ps1`（默认 + `-TaskPath`）**PASS(3 warnings) ×2**；API inventory **EXIT=0**。gated 的
  before/after 与交付证据一致（before `path_resolver=null` / 页读 `SOURCE_ACCESS_DENIED` / 0 帧；
  after `targets=1/unresolved=0/bound_pages=1/minted=1/resolve p1 OK`）。
- **判别性独立复现**：自选 **D1**（枚举分支改回 path resolver）→ 单测 **4 failed / 5 passed**；
  **D2**（改为接受任意 live 条目）→ 同路径 sibling 红线用例 **1 failed**；**D1b**（同一破坏点跑 gated 真
  IPC）→ **1 failed**。三者均逐字节恢复，sha256 与交付字节一致并复绿（§4）。
- **flaky 复核**：Lead 报告的 `FluentR2ReworkTests.R3001_...` 在隔离复跑中 **5 次 × 9/0/0 = 45/45 pass**；
  我另跑完整 `NewManga.App.Tests` 程序集 **770 passed / 0 failed / 7 skipped**，未复现失败；该 UI/时序用例
  不在本卡改动面。接受「既有 flaky、与本卡无关」判断，但原始失败堆栈未入库（F7）。
- **必须保留的 limitation**：本卡**没有**恢复 Run 全面授权；gated 的 Core `source_locations` 由测试侧
  `AlignRegistryAsync` 对齐（等价既有 reattest 结果）；Scheduler 未启动/枚举失败时 `known` 为空、无 grant；
  Host 侧 mint 仍可能 typed skip（best-effort）；2C 长 Run 保留。

## 1. 审查范围与方法

- **交付链**：`f6b5a761a`（`HostRuntime.cs`：`RunSourceRange.Resolve` 枚举分支复用
  `SelectEnumeratedEntry` + XML 注释；非枚举保持 `ResolveRegistryEntry` 字节不变）→ `fad1ec776`
  （新增 `SourceRunRangeResolutionTests.cs` 9 例；`Fea11RunGrantIpcTests.cs` 新增 1 条 gated 真 IPC 闭环）。
  `git diff --stat e78c144bb..fad1ec776`：**4 files changed, 671 insertions(+), 3 deletions(-)**；其中生产
  改动仅 `HostRuntime.cs`（+34/−3 区域），`SourceScanScheduler.cs` 及 `Sources/**` 零 diff。
- **卡范围**：`2ef3f1024..ca929aade` 共 **24** 个文件（3 个代码/测试 + 21 个 docs/evidence），全部落在
  `allowed_paths`；`2ef3f1024..e78c144bb` 为 docs-only 释放提交；禁止面（`src/`、`tests/`、
  `doc/plan/`、`doc/contracts/`、`Sources/**`、`NewManga.App`、`NewManga.CoreClient`、
  STATUS/PLAN/LEDGER、依赖文件）在交付范围内**零 diff**。
- **实际核对**：`git show/diff` 逐字节；`SourceScanScheduler.cs` 的 `SelectEnumeratedEntry` /
  `ResolveRegistryEntry` 方法体读取；新测试逐例审阅；gated 测试源码逐段审阅；独立 build/单测/回归/
  gated 真 IPC/定向 pytest/pins/check×2/API；证据逐文件 sha256 复算（19/19 当前工作树命中）并与
  fixture 原件同哈希比对；自选 3 个破坏点做「破坏 → RED → 字节恢复 → sha 复核 → 复绿」。
- **未跑/不声明**：未重跑全量 `pytest tests` 与全量 `dotnet test NewManga.sln`（避免重写 tracked
  `verification/FEA-09/**`；仅交叉核对 Owner 日志与合计，并独立重跑 App.Tests 程序集与 flaky 隔离）；
  未跑完整 Core reattest 往返（本卡不发送 `ReattestSourceLocation`，该环由 L-S4-B 证据覆盖）；
  未触碰真实用户数据/AppData/回收站；未 push、未建 worktree。
- **并发披露（收尾时观察，非本 Review 写入）**：我的独立实跑完成（约 17:19）后，Lead 在共享 main
  工作树发起 closeout 文档事务（**截至本报告收尾约 17:33 仍未提交**）：`doc/STATUS.md`、
  `doc/REBASELINE_PLAN.md`、`doc/TASK_LEDGER.md`、本卡卡面、`verification/…/EV.md` 被修改，并新增
  `doc/tasks/FEA-11-L-S1-B2-ROOTS-AVAILABILITY-1.md`；卡面 `status→done`、`integration_commit→fad1ec776`、
  新增 Canonical Evidence/Closeout 段，EV 被重写。**本报告的事实仍以 `fad1ec776` 代码/测试与
  `ca929aade` 证据字节为准**；我没有触碰这些并发文件。该事务进行中时，默认 `check.ps1` 因 STATUS 指针
  被改写到中间态而 **FAIL**（`STATUS 未提供可解析的当前 Task 指针`），`-TaskPath` 仍 **PASS**；我在
  §2F 的 **PASS×2** 是在该事务开始前实测的。并发事务结束后需由 Lead 重新跑一次默认 check。

## 2. 必做核对 A–G

### A. AC-RUN-1 主 AC：枚举 target 用自身 live 身份 — **PASS**

1. **实现形状正确**：`HostRuntime.cs:1794-1818` 仅对 `target.IsEnumerated` 走
   `HostSourceScanExecutor.SelectEnumeratedEntry(registryEntries, target, out _)`（`:1806`）；非枚举仍走
   `ResolveRegistryEntry(registryEntries, target.Path)`（`:1817`）。`SelectEnumeratedEntry`
   （`SourceScanScheduler.cs:1957-1988`）按 `RegistryId` **Ordinal 精确匹配**（`:1963-1968`），再检查
   `RevokedAt is null`（`:1971-1975`）与 `Generation == target.Generation`（`:1977-1985`）；**没有**任何
   回落同路径或任意 live entry 的分支。
2. **before 可判**：新单测 `Resolve_EnumeratedTarget_UsesItsOwnLiveEntry_WhenARevokedSiblingSharesThePath`
   先在**同一 entries 快照**上断言 path-only `ResolveRegistryEntry(...) == null`（revoked 旧条目 +
   同路径 live 新条目），再断言 `RunSourceRange.Resolve` 返回 1 个 scope、`Unresolved=0`、
   `RegistryId/Generation` = live，且 path/kind/version/container members 与现行为一致。
3. **after 真 IPC 独立复现**：我的 gated 运行生成 fixture
   `G:\CODEX\New Manga.workspace\FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1\fixtures\ipc-232ffe8cf2e3498cbaa918ac8eca82ae`：
   `before.path_resolver="null"`、`before.page_read="SOURCE_ACCESS_DENIED"`、`before.authorize_frames=0`；
   `after` = `targets=1/unresolved=0/registry_id=<live>/generation=1/version=sv1/container_entries=2`；
   `bound_pages=1`、`minted_grants=1`、`resolve_p1="ok"`、`reattest_frames=0`、`authorize_frames=1`、
   `host_registry_unchanged=true`、`path_hits=0`。wire/stderr 对 fixture 根与 archive 路径的匹配均为 0。
4. **判别性**：D1 把枚举分支改回 path resolver → `SourceRunRangeResolution` **4 failed / 5 passed**（正是
   `UsesItsOwnLiveEntry`、`MissingRegistryAndGenerationDrift`、`DuplicateRegistryId`、
   `ResolvedEnumeratedSource_LeavesRegistryStructureUntouched`）；D1b 在 gated 真 IPC 上同破坏 →
   **1 failed**（`ReauthorizedLiveEntry_RunRangeResolvesAndBindsOverRealIpc`）。均恢复后复绿（§4）。

### B. AC-RUN-2 fail-closed 矩阵与不回落 sibling — **PASS**

| 场景 | 期望 | 实现/测试 | 我的核对 |
|---|---|---|---|
| target 自身 registry 缺失 | `Unresolved` | `SelectEnumeratedEntry` 无 id → null（`:1963-1969`）；`Resolve_EnumeratedTarget_IsUnresolved_OnMissingRegistryAndGenerationDrift` | 9/0/0 通过 |
| target 自身 revoked | `Unresolved`，**不采用**同路径 live sibling | `:1971-1975`；`Resolve_EnumeratedTarget_NeverFallsBackToALiveSibling_WhenItsOwnEntryIsRevoked`；gated `revoked_target` 实测 `targets=0/unresolved=1/cold_sources=0` | D2 破坏该红线 → 该用例 **RED** |
| generation 漂移 | `Unresolved` | `:1977-1985`；同负责例的 drift 分支 | 9/0/0 通过 |
| 未解析时零 grant / 零 `AuthorizeSourceReadForRun` 帧 | 不调用 `authorize` | `Authorizer_UnresolvedEnumeratedSource_NeverSendsAuthorizeSourceReadForRun`（`authorizeCalls=0`，warn `unresolved_sources=1`）；gated before `authorize_frames=0` | 通过 |

**安全兜底**：即使解析选错条目，mint 仍由 `SourceReadCoordinator.IssueLockedAsync` 在锁内三次调用
`Registry.Authorize(registryId, generation, paths)`（`SourceAccessRegistry.Authorize` 逐请求复核 entry
存在、未撤销、generation 相等、path 属于已登记 root、root 卷/文件身份未变），失败只会 typed skip，
不会铸出错误 grant。本卡未改该路径。

### C. AC-RUN-3 非枚举语义零变化 — **PASS**

- **字节零变化**：`git diff e78c144bb..fad1ec776 -- apps/desktop-avalonia/src/NewManga.Host/Sources/SourceScanScheduler.cs`
  为空；`ResolveRegistryEntry`（`:1897-1938`）与 `Sources/**` 均不在交付 diff 中。`HostRuntime.cs:1817`
  的非枚举分支仍原样调用它。
- **行为保持**：`Resolve_NonEnumeratedTarget_KeepsThePathOnlyResolver` 在「同路径 revoked + live」快照上
  仍返回 `Unresolved=1`，并验证 plain live exact 仍可解析；Owner B4 式破坏（把 own-entry 逻辑用于非枚举）会
  使该用例 RED（我审阅其 mutation 为 `if (target.IsEnumerated || target.SourceKind is null)`，
  属行为级 RED）。
- **既有回归**：我独立运行 `--filter FullyQualifiedName~SourceRegistryTests` **32 passed / 0 failed /
  0 skipped**（含 `RunSourceRangePrefersTheRunProjectAndSkipsUnresolvedSources`、
  `RunSourceRangeUsesTheCachedCoreVersionAndReportsColdSources`）。

### D. AC-RUN-4 冷源分类与 on-demand 恢复 — **PASS**

1. 顺序保持「先 entry 后 identity」：`HostRuntime.cs:1826` 在 entry 解析成功后才检查
   `identities.TryGet`；枚举 live 但无 version → `cold.Add(target)` 并 `continue`，不再先被
   `Unresolved` 短路。
2. `Resolve_EnumeratedColdSource_IsReportedAsCold_NotUnresolved`：`Targets=0`、`Unresolved=0`、
   `ColdSources=1`。
3. `Authorizer_EnumeratedColdSource_PerformsOneOnDemandScan_ThenMints`：脚本化 `onDemandScan` 恰 1 次、
   第二次 `AuthorizeSliceAsync` 不再扫描；mint 收到 live `RegistryId` 与 Core-authoritative version。
4. 预算/失败：既有 `RunAuthorizerOnDemandScanBudgetIsExplicitAndBounded`（`MaxOnDemandScansPerSlice=8`，
   `HostRuntime.cs:1890`）与 `RunAuthorizerOnDemandScanFailureIsASkipNotABlock` 原样通过（32/0/0）；
   30s 超时常量 `HostRuntime.cs:1893`、`CancelAfter` 在 `:2104`，本卡未改该逻辑。**但「超时」无专门
   用例**（只有失败用例注释覆盖），见 F5。

### E. AC-RUN-5 无自动授权/不写 registry/不抛 — **PASS**

- **不写结构**：`RunSourceRange.Resolve` 只读 `registryEntries` 快照与 `SourceIdentityCache`；无
  `Register`/`Revoke`/`Reset` 调用；唯一既有持久写仍是 mint 时 `Registry.Authorize` 的 `last_used_at`
  审计（`SourceAccessRegistry.Authorize`）。
- **结构相等**：`Authorizer_ResolvedEnumeratedSource_LeavesRegistryStructureUntouched` 用真实
  `SourceAccessRegistry`（旧 revoked + 新 live 同路径）断言解析/授权前后
  `DescribeRegistryEntries`（不含 `LastUsedAt`）相等、旧 revoked 行仍在、`revoked_at/generation` 未变、
  条目数 2；gated 亦断言 `entriesBefore` 与 mint 后投影相等（`Fea11RunGrantIpcTests.cs:839`、`:915`、
  JSON `host_registry_unchanged=true`）。
- **不抛**：`HostRuntime.cs:1804-1811` 的 `try/catch (Exception error) when (error is not OutOfMemoryException)`
  将 `SelectEnumeratedEntry` 的异常（如重复 id 触发 `SingleOrDefault` 的 `InvalidOperationException`）
  降级为 `entry=null` → `Unresolved`；`Resolve_DuplicateRegistryId_IsUnresolved_NotThrown` 覆盖，D3 式
  删除 catch 会使该用例 RED（Owner 证据 B3）。异常不会向 `AuthorizeSliceAsync` 新增抛出。

### F. 独立实跑 — **PASS**

| 场景 | 我执行的命令（repo root） | 我的实测 | 与证据 |
|---|---|---|---|
| build | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **PASS 0 warning / 0 error**，EXIT=0 | 一致 |
| 新单测 | `dotnet test …/NewManga.Host.Tests.csproj -c Release --no-build --filter "FullyQualifiedName~SourceRunRangeResolution"` | **9 passed / 0 failed / 0 skipped**，EXIT=0 | 一致 |
| 回归 | 同上 `--filter "FullyQualifiedName~SourceRegistryTests"` | **32 / 0 / 0**，EXIT=0 | 一致 |
| gated 真 IPC | `NEWMANGA_FEA11_IPC=1 dotnet test … --filter "FullyQualifiedName~Fea11RunGrantIpc"` | **6 / 0 / 0**，EXIT=0，9 s | 一致；新 fixture 的 JSON 与交付 `ipc-closed-loop.json` 同形 |
| 定向 pytest | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q`（`PYTHONDONTWRITEBYTECODE=1`） | **89 passed / 1 warning**，EXIT=0，10.51 s | 一致 |
| pins | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | **PASS (all 18)**，EXIT=0（C15 `f9e376a0ed4c`、C16 `a7f57ebdbd67`、C17 `aefa0fa5b17e`） | 一致 |
| check | `check.ps1` 默认 + `-TaskPath doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md` | **PASS (3 warnings) ×2**，EXIT=0（3 warnings = 9 个非终态 Task + STATUS/PLAN 预算 80%）；**收尾时 Lead 并发 closeout 使默认 check 暂时 FAIL，见 §1 并发披露** | 一致（事务前） |
| API | `C:/Python314/python.exe tools/generate_api_inventory.py --check`（`PYTHONDONTWRITEBYTECODE=1`） | **EXIT=0**（61 不变） | 一致 |
| 全量 Python/.NET | **未重跑**（见 §1） | 交叉核对 Owner 日志：pytest **3360/10**、.NET **1661/0/95**（8 个程序集合计 1661 passed / 95 skipped / 1756 total，`FULL_DOTNET_EXIT=0`） | 数字自洽 |
| App.Tests 全量 | `dotnet test …/NewManga.App.Tests.csproj -c Release --no-build` | **770 passed / 0 failed / 7 skipped / 777 total**，EXIT=0，2 m 55 s | 补充 flaky 复核 |
| flaky 隔离 | 同 filter `FullyQualifiedName~R3001_OtherControlPress_Wheel_AndShellHandledKey_WakeHiddenBarsAndRenewDeadline` ×5 | 每次 **9/0/0**（共 45/45），EXIT=0 | 见 §5 |

### G. 证据/判别性/不夸大 — **PASS（附 P3 证据卫生项）**

- **证据逐文件 sha**：按 `RESOURCE-MANIFEST.json` 复算 **19/19 命中**；交付的 gated 证据
  `logs/ipc-closed-loop.json` / `.txt` 与其 fixture 原件（`ipc-0cf0a5b65a144d25b8f1772ebe8258f3`）
  sha256 逐一相等（`7f31dcc…` / `25ba1210…`），且内容逐字相同。代码/测试哈希与 manifest 一致：
  `HostRuntime.cs c91deee6…`、`Fea11RunGrantIpcTests.cs 3365bb18…`、`SourceRunRangeResolutionTests.cs 27984724…`。
- **判别性 5/5 可信**：`logs/discrimination.log:5-76` 记录了真实 break → 对应测试非 0 退出 →
  原字节回写 sha256 MATCH → 复绿；我审阅 `tools/discrimination.py` 确认其真实写入/恢复并调用
  `dotnet test`，且自选 D1/D2/D1b 独立复现（§4）。B4 的 mutation 是行为级（guard 加 `SourceKind is null`），
  RED 属断言失败而非编译失败，日志描述准确。
- **scope**：`scope-validation.log` PASS；`2ef3f1024..ca929aade` **24 文件**全部在 `allowed_paths`；
  `changed-files.txt` 的 21 项 = 3 个代码/测试 + 18 个 docs/evidence（采集时点）；`ca929aade` 实际 24 文件
  （另 3 个为 `RESOURCE-MANIFEST.json`、`changed-files.txt`、`scope-validation.log`，见 F3）；禁止面零 diff；
  `PROTOCOL_MINOR=3`；C15/C16/C17 git blob 在 base/delivery/HEAD 逐 blob 相同；`card_status_unchanged=True`。
- **不夸大**：卡/Handoff/EV 均保留「Run 预授权/冷源分类恢复 ≠ Run 全面恢复」、managed-only、mint typed
  skip、gated 测试侧对齐、2C 保留等 limitation；未出现「自动恢复/自愈/自动重新授权/撤销后放行/扫描面恢复/
  B2/folder/2C」承诺。
- **P3 证据卫生**：manifest 含 ignored pyc（F1）、起点基线无独立日志（F2）、changed-files 自指文件说明
  不全（F3）、manifest 记录非祖先 docs head（F4）。

## 3. AC-RUN-1…8 判定

| AC | 判定 | 依据（本次复核） |
|---|---|---|
| **AC-RUN-1** 枚举 target 的 Run 范围恢复（主 AC） | **MET** | `HostRuntime.cs:1794-1818`；`SelectEnumeratedEntry` 精确 id/revoked/generation；单测 + gated before/after；D1/D1b RED |
| **AC-RUN-2** fail-closed 矩阵与不回落 sibling | **MET** | 缺失/revoked/drift → `Unresolved`；`NeverFallsBack…` + authorizer 零 frame + gated revoked target；D2 RED |
| **AC-RUN-3** 非枚举语义零变化 | **MET** | `SourceScanScheduler.cs` 零 diff；`:1817` 原样调用；`Resolve_NonEnumerated…` + `SourceRegistryTests` 32/0/0；B4 RED |
| **AC-RUN-4** 冷源 on-demand 分类恢复 | **MET**（F5 备注：无专门 timeout 用例） | `:1826` 后分类；cold 单测；authorizer 恰 1 次扫描后 mint；预算/失败既有用例通过；`MaxOnDemandScansPerSlice=8`/30s 未改 |
| **AC-RUN-5** 无自动授权/identity 重建/不写 registry/不抛 | **MET** | 只读快照；无 Register/Revoke/Reset；真实 registry 结构全等、旧 revoked 行保留；重复 id → Unresolved；catch 覆盖 |
| **AC-RUN-6** gated 真实 IPC 闭环（before/after） | **MET** | 独立 gated 6/0/0；fixture JSON before/after 如上；`bound_pages=1/minted=1/resolve p1 OK`；`reattest_frames=0`；wire/stderr 无路径 |
| **AC-RUN-7** 零契约/零漂移 | **MET** | C15/C16/C17 blob 三处相同；pins 18/18；`PROTOCOL_MINOR=3`；API 61；禁止面零 diff；无新命令/能力/错误码/schema/依赖 |
| **AC-RUN-8** 门禁/不夸大/触发口径 | **MET**（F2/F7 备注） | build/定向/gated/pytest/pins/check×2/API 实跑；全量 Owner 日志 3360/10、1661/0/95；跑后 `verification/FEA-09` 无 diff；措辞红线检查通过 |

## 4. 破坏性复跑（独立，逐字节恢复）

- **备份**：`HostRuntime.cs` 原字节
  sha256=`c91deee69f7785931e42ebd84642f796e6d3c7c2308a06c62bc393afbdee1f40`（**等于交付字节**）；
  备份副本在
  `G:\CODEX\New Manga.workspace\FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1\review-r1\HostRuntime.cs.original`。
  `git status --porcelain` 起点为空；文件 newline=`\n`。
- **D1（纯函数，AC-RUN-1）**：把枚举分支的 `SelectEnumeratedEntry(...)` 替换为
  `ResolveRegistryEntry(registryEntries, target.Path)` → `--filter FullyQualifiedName~SourceRunRangeResolution`
  **EXIT=1，4 failed / 5 passed**；回写原字节，sha256 MATCH=True；复跑 **9/0/0，EXIT=0**。
- **D2（授权红线，AC-RUN-2）**：把枚举分支替换为 `registryEntries.FirstOrDefault(candidate => candidate.RevokedAt is null)`
  → `NeverFallsBackToALiveSibling` **EXIT=1，1 failed**；恢复 sha256 MATCH=True；复跑 **1/0/0**。
- **D1b（gated 真 IPC，AC-RUN-1/6）**：同 D1 破坏 + `NEWMANGA_FEA11_IPC=1` 跑
  `ReauthorizedLiveEntry_RunRangeResolves…` → **EXIT=1，1 failed**（before/cold 断言在 path resolver
  下失败）；恢复 sha256 MATCH=True；复跑 **1/0/0，EXIT=0**。
- **收尾**：`final_sha256=c91deee6… MATCH=True`；`git status --porcelain` 为空；未在交付树留下破坏。
  复跑日志在 `review-r1/discrimination-review.log` 与 `discrimination-gated-review.log`（仓外 workspace，
  不属交付证据）。
- **证明力**：三个破坏点分别覆盖主 AC、授权红线与真实 IPC 闭环；恢复后复绿，说明测试对修复确实具有判别性，
  且临时编辑未污染交付字节。

## 5. flaky 复核

- **Lead 报告**：全量 .NET **1660 passed / 1 failed / 95 skipped，EXIT=1**；唯一失败
  `NewManga.App.Tests.FluentR2ReworkTests.R3001_OtherControlPress_Wheel_AndShellHandledKey_WakeHiddenBarsAndRenewDeadline`；
  Lead 隔离复跑 **9/0/0 PASS**。交付证据 `logs/full-dotnet.log` 是 **1661/0/95、EXIT=0**（8 程序集合计
  1661/95/1756），两者总数相同（1756），失败 run 只是把 1 个 pass 变成 fail。
- **我的独立复核**：
  1. 同一 filter 隔离复跑 **5 次，每次 9/0/0（共 45/45 pass）**，EXIT=0；
  2. 完整 `NewManga.App.Tests` 程序集 **770 passed / 0 failed / 7 skipped**，EXIT=0，未复现失败；
  3. 该用例是 Avalonia headless UI/时序测试（`FluentR2ReworkTests.cs:570-638`，含 `Pump(20)`、真实
     hit-test 与 2 s deadline 断言），与 `HostRuntime.RunSourceRange` 无调用关系；本卡改动面只在 Host
     授权解析，App.Tests 该用例不经过它。
- **判断**：接受「既有 flaky、与本卡无关」这一处置；它不构成 AC-RUN-8 的失败（交付日志全绿，Lead 的
  gate run 也已隔离复绿）。**保留项 F7**：原始失败堆栈/日志未入库，无法从证据字节独立验证失败的具体断言。

## 6. Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 状态 |
|---|---|---|---|---|---|---|
| **F1** | P3 | `verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/RESOURCE-MANIFEST.json:119-122`；`tools/gen_manifest.py:74-81` | `rglob("*")` 把 ignored 的 `tools/__pycache__/discrimination.cpython-314.pyc` 计入 evidence_tree（`file_count=19`）；`.gitignore:1` 忽略 `__pycache__/`，`ca929aade` 实际只跟踪 19 个 evidence 文件（含 manifest 自身，不含 pyc）。clean clone 只能验证 18/19 列表项，与 manifest note 的「tracked delivery tree」不一致 | 我按 manifest 复算当前工作树 19/19 命中；`git ls-tree -r ca929aade` 的 evidence 文件为 19（含 manifest）；pyc 不在 `git ls-files` | closeout 前重生 manifest 时排除 `__pycache__/`/`*.pyc`（勿提交 pyc），或注明该文件为未跟踪派生物 | open |
| **F2** | P3 | `verification/…/EV.md:48-49`；`doc/tasks/…:93`；`doc/handoffs/…:45`；`doc/STATUS.md:20` | AC-RUN-8 的「起点 1652/0/94、pytest 3360/10」只有 Owner 自述与 STATUS/ B1 closeout 记录，`logs/` 无独立 baseline 运行；scope review §0/§4.4 曾要求 clean-head 起点重测并留证 | `logs/` 只有交付时的 `full-dotnet.log`/`full-pytest.log`；测试数差 +9/+1 skip 与新增文件/ gated fact 结构一致；无 Python diff | 保留一份起点日志，或明写「起点 = L-S4-B-1 closeout / STATUS 记录值」，避免 AC-RUN-8 依赖单一自述 | open |
| **F3** | P3 | `verification/…/changed-files.txt`（21 行）；`EV.md:58` | 21 项 delivery 列表在 `RESOURCE-MANIFEST.json`、`changed-files.txt`、`scope-validation.log` 生成之前采集，故不含这三个自指文件；EV 脚注只说「不含 manifest 自身」，未提 `scope-validation.log`。`2ef3f1024..ca929aade` 实际 24 个文件 | `changed-files.txt` 无 `scope-validation.log`；HEAD 该范围 24 文件；manifest/EV 数字关系可复算 | 把「21 = 采集时点 delivery 列表；另 3 个为证据容器/自身日志」写清，或 closeout 时补一段清单说明 | open |
| **F4** | P3 | `RESOURCE-MANIFEST.json:11` | `repo_head_at_generation=26d43c108…` 不是 `ca929aade` 的祖先（docs 提交被 amend；对象仍在本地但 main 不可达）；manifest 的「generation-time snapshot」因此无法从 main 直接复核 | `git merge-base --is-ancestor 26d43c108 HEAD` → exit 1；`git cat-file -t` 显示对象存在 | 记录最终 docs head，或在 note 标注该 head 为 amend 前中间提交；无需重写既有哈希 | open |
| **F5** | P3 | `doc/tasks/…:69`（AC-RUN-4）；`apps/…/SourceRegistryTests.cs:876-890`；`HostRuntime.cs:2104` | AC-RUN-4 写「预算/超时/失败仍 skip（既有用例原样通过）」；预算与失败有既有用例，30s 超时只有代码与失败用例注释覆盖，**无专门 timeout 测试** | `grep OnDemandScanTimeout` 在 tests 下无命中；`RunAuthorizerOnDemandScanFailureIsASkipNotABlock` 覆盖异常而非超时 | 把 AC 措辞改为「预算/失败有既有用例；超时逻辑未改但无专门用例」，或在后续卡补 timeout 用例 | open |
| **F6** | P3 | `apps/…/Fea11RunGrantIpcTests.cs:1333-1336`、`:1364` | 新增 `DescribeRegistryEntries` 插在 `AlignRegistryAsync` 原有 `<summary>` 与 `AlignRegistryAsync` 方法之间，造成一段 doc comment 内两个 `<summary>`，且第一个 summary 实际描述的是 `DescribeRegistryEntries`；`AlignRegistryAsync` 失去自己的注释。纯注释/可维护性问题，编译 0 warning | 逐行读 `:1333-1364`；build 0 warning | 将 helper 移到 `AlignRegistryAsync` 之后，或恢复 `AlignRegistryAsync` 自己的 summary | open |
| **F7** | P3 | `FluentR2ReworkTests.cs:570-638`；Lead gate run | Lead 的 1660/1/95 唯一失败为 UI/时序用例；原始失败日志/堆栈未入库，证据目录只有 1661/0/95 的全绿日志；我的隔离 45/45 与 App.Tests 777 全量均未复现 | 见 §5；交付 `logs/full-dotnet.log` 无失败 trace | 若再次命中，保留失败 run 的完整日志/堆栈再登记 flaky；本次不阻塞 | open |

**P0/P1/P2：0。** 未发现产品行为、授权语义、契约/接口/依赖或证据完整性方面的阻断问题。

## 7. 结论与复审

- **结论：`approved`。** `fad1ec776` 的实现/测试与 `ca929aade` 的证据一致，可交 DSH 集成验证/closeout；
  P0/P1/P2 为 0，7 个 P3 不阻断，建议在 closeout 顺手处理 F1/F3/F4（证据容器）与 F6（注释），F2/F5/F7
  在卡面/证据中补一句精度说明即可。
- **剩余风险**：只恢复「B1 显式动作 → refresh/reattest → 枚举 → Run 预授权/冷源分类」；managed-only Run
  不经 source 授权；Scheduler 未启动/枚举失败时无 `known`；Host 侧 mint 仍可 typed skip；gated 的 Core
  `source_locations` 由测试侧 `AlignRegistryAsync` 对齐；2C 长 Run、B2、folder、L-S4-1/L-R1 仍保留。
- **复审口径**：本报告只对 `fad1ec776`（实现/测试）与 `ca929aade`（证据）有效；head 前进或出现新
  Review 后，本报告自动成为历史记录，不得覆盖或继续当作当前批准。

## 8. 真实性声明

1. **唯一仓库写入（本 Review）**：本 Review 只写了
   `doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-r1.md` 这一个仓库文件。**未**修改/删除/移动任何
   生产代码、测试、契约、Task 卡、STATUS、REBASELINE_PLAN、TASK_LEDGER 或证据字节；**未**执行
   `git add`/`git commit`/`git push`。收尾 `git status --porcelain` 显示本报告为未跟踪新增（`??`），
   另有 §1 披露的 Lead 并发 closeout 文档修改（非本 Review 写入）；实现/测试/证据的已提交字节未变。
2. **仓外派生产物**：破坏性复跑的备份/日志、独立 gated 的 fixture 与日志均写在
   `G:\CODEX\New Manga.workspace\FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1\review-r1\` 与
   `…\fixtures\`（仓外、未被 tracked）；未写 `verification/FEA-09/**`。
3. **破坏-恢复**：D1/D2/D1b 三个破坏点均先备份原字节，结束回写并 sha256 复核
   （`c91deee6…` MATCH=True），最后一次 `git status` 为空；未把破坏后的字节留在交付树。
4. **实测数字**：§2F 列出的 build/9/32/6/89/18/check/API 与 App.Tests 777、flaky 45/45 均为本 Review
   现场执行；全量 pytest/.NET 的数字来自 Owner 证据日志的交叉核对，**不是**我重跑；gated 的 before/after
   JSON 来自我本次新建 fixture，和交付 fixture 同形（不同随机 registry id）。
5. **证据哈希**：当前工作树按 manifest 复算 19/19 命中；但其中 `tools/__pycache__/…pyc` 是 ignored/untracked
   （F1），`ca929aade` 的 evidence 树实际为 18 个非 manifest 跟踪文件 + manifest 自身。
6. **NOT_RUN**：完整 Core reattest 往返；全量 `pytest tests`；全量 `dotnet test NewManga.sln`；真实用户
   数据/AppData/回收站；push；linked worktree；契约 byte-level 逐字节审阅（以 blob/pins 比对代替）。
7. **独立性**：fresh-context 子 agent，未参与本卡实现、返修、scope review；只读 `fad1ec776` 代码/测试字节
   与 `ca929aade` 证据字节；未接受实现者的口头/文本自述作为实现事实。
