---
task: FEA-11-RUN-GRANT-1
title: FEA-11-RUN-GRANT-1 r3 最终窄面复审（Review r2 findings 返修；R2-01…R2-04 关闭判定）
reviewer: fresh subagent（独立上下文；未参与实现/返修/证据生成；只读被审 head）
session: 19aa49d5-f5f6-4fa7-b982-a85a70a5520d（Lead 记录）
parent_session: session-5f1e719c-f1f3-4193-8393-caf4d0936e4a
reviewer_kind: subagent
date: 2026-11-07
repo: G:\CODEX\New Manga
branch: main
worktree: 复核前 clean；复核后本报告为 untracked；随后 Lead 并发 closeout 修改卡面（非本 Review 写入，见 §0 注）
reviewed_head: a11ded0d3794bdb1afa5f7889d2e25aa4ea7b853
verdict: approved
---

# FEA-11-RUN-GRANT-1 r3 最终窄面复审

> **结论先行：`approved`。P0=0 / P1=0 / P2=0 / P3=2（均为非阻断观察）。**
>
> - **R2-01（P2）CLOSED**：`RunSourceRange.KindOfSource` 已按「枚举声明 `SourceKind` 优先 → `Directory.Exists` → folder → 扩展名」判定（`HostRuntime.cs:1741-1749`），`Resolve` 已改用它（`:1717-1720`）；新增真实目录源 IPC 用例（`Fea11RunGrantIpcTests.cs:250-338`）在真实 Core 上完成 folder mint → `bound_pages=1` → `resolve_page_resource` 成功。我独立实跑 `NEWMANGA_FEA11_IPC=1` 的 `Fea11RunGrant` **3 passed**；并自选破坏点（把 `KindOfSource` 改回扩展名判定）→ **folder kind 单测 + 真实 folder IPC 两条同时变红**（Expected `folder` / Actual `image`）→ 按原字节恢复、sha256 复核 `6184a0f0…` 一致、重建后 **2 passed**。
> - **R2-02（P2）CLOSED**：能力缺失用例已改为 **known 源非空 + entries 非空 + 计数 authorize**（`SourceRegistryTests.cs:297-316`），断言 0 次 mint 且不抛；另有 dispatcher 级「能力缺失仍到达 dispatch」用例（`:317-336`）。我独立删掉能力门 → 目标用例 **RED（Expected 0 / Actual 1）** → 恢复 sha 一致；判别点 B7 记录可信。
> - **R2-03（P3）CLOSED（有残差）**：`HostRuntime.AcceptRunAsync`（`:71-84`）已直接委托可测 seam `AuthorizePreparedRunForAcceptAsync`（`:93-106`）；两个接线用例覆盖冻结 `{command, scope}`、缺失/过期 `RUN_STALE_PREVIEW`、无 authorizer 仍先取 slice（`SourceRegistryTests.cs:361-422`）。我独立删除 seam 内的授权调用 → 目标用例 **RED（`Assert.Single` empty）**；B8 记录可信。残差：删除 `AcceptRunAsync` 到 seam 的那一行委托时，`SourceRegistry` 21 仍全绿（我已实测），即「委托本身」未被测试判别；列为 **R3-02（P3，非阻断）**。
> - **R2-04（P3）CLOSED**：卡 I-2「铸造」「源范围」已改为 best-effort 权威口径（卡 `:96`/`:99`）；`RESOURCE-MANIFEST.json` 含 `delivery_head=a11ded0d3…`，worktree `source_path` 指向「main worktree; delivery head a11ded0d3」；卡/现行 Handoff/EV 的 L-G12 均为「image 单 entry + folder 源（逐成员 entry，已实证）+ 归档首成员」，并保留 version 通道与多成员容器限制。
> - **证据与门禁**：定向 pytest **50 passed**；`SourceRegistry` **21 passed**；真实 IPC **3 passed**；pins **18/18**；check（默认 + `-TaskPath`）**PASS(3 warnings)**；API inventory **EXIT=0**；EV **27/27 sha256** 全匹配；scope diff `218775bca..a11ded0d3` **31 文件全部 ⊆ allowed_paths、禁止面零 diff、`PROTOCOL_MINOR=3`**；Handoff/EV 数字（**3281/10、1551/0/89**）与 Lead 实测及日志一致；判别性 9/9 记录可信（9 个破坏点 `old` 片段各出现 1 次、目标用例存在、日志 restore sha 与现行文件 sha 逐一对齐；B7/B8/B9 由我独立复现）。
> - **无 P0/P1/P2**；无授权放宽、静默放行、数据破坏、未登记 wire/schema/依赖变化；无测试删除或弱化。R2 返修可集成，建议 Lead 在 closeout 时回填 AC-R7（并顺手处理两个 P3 观察）。
>
> ---
>
> **复核边界**：`HEAD=5eb69b3f144b1704cf6a28cdb86da2cdea93302e`（docs/evidence），实现+测试 delivery head=`a11ded0d3794bdb1afa5f7889d2e25aa4ea7b853`（`git rev-parse` 实测）；r2 reviewed head=`3ffabeb81`，r2 修 commit=`9e1861ee0`。工作树 clean；实现/测试文件与 `a11ded0d3` 逐字节一致（`git diff a11ded0d3 -- <实现/测试文件>` 为空）；`a11ded0d3..HEAD` 仅 docs/evidence 差异。
>
> **未重跑全量**：按任务约定，全量 pytest/.NET 由 Lead 在 `a11ded0d3` 实跑（**3281 passed / 10 skipped**、**1551 / 0 / 89**，均 exit 0）；我核对了 `logs/full-pytest.log`、`logs/full-dotnet.log`、`logs/gates-governance.log` 的数字与 Handoff/EV 一致，并独立重跑全部定向门禁。全量未跑不等于未核对：数字、head、skip 说明与 r2 基线差值（+4 单测、+1 opt-in skip）均已对齐。

---

## 0. 复核对象、方法与边界

- 仓库 `G:\CODEX\New Manga`，`main`；复核开始 `HEAD=5eb69b3f1`，工作树 clean；唯一写入为本报告。
- **只读事实以 `a11ded0d3` 字节为准**：`HostRuntime.cs`、`SourceRegistryTests.cs`、`Fea11RunGrantIpcTests.cs`、`SourceReadCoordinator.cs` 等与 delivery head 一致；证据/卡/Handoff 取 `5eb69b3f1` 的提交字节。
- 本复核**未参与**该卡实现、r1/r2 返修或证据生成；未 `git add`/`commit`/`push`；未删除/移动任何文件；未改写任何 tracked 证据。
- 运行了生成型/破坏型动作：
  - 定向 pytest、`SourceRegistry`、真实 IPC；
  - **4 次破坏性复跑**（B9-equivalent、B7、B8、AcceptRun 委托删除），每次先备份、按原字节恢复并 sha256 复核；
  - 其中一次恢复后因 `dotnet test` 增量构建用了旧 DLL 出现「恢复后仍红」，改用 `dotnet build --no-incremental` 重建后绿；这是构建缓存问题，不是代码问题（详见 §5）。
- 未运行 `tools/discrimination.py` 全脚本（它会重写被审的 `logs/discrimination.log`）；改为静态核对 9 个破坏点 + 独立复现 B7/B8/B9（§5）。
- 未重跑全量 pytest/.NET，理由见文首；未以静态判断冒充全量实测。
- **复核后状态注**：本报告完成后，Lead 在共享工作树把卡 `status` 改为 `done`、`integration_commit=a11ded0d3`、AC-R7 改为 `<<MET>>` 并记录 r3 reviewer session；该修改非本 Review 写入、不在 `a11ded0d3` 被审字节内，不改变本报告的判定与结论。

### 0.1 本 Review 实跑命令与结果（全部实测）

| # | 命令 | 实测结果 |
|---|---|---|
| 1 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **50 passed** in 7.69s |
| 2 | `dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRegistry"` | **21 passed / 0 failed / 0 skipped** |
| 3 | `$env:NEWMANGA_FEA11_IPC=1; dotnet test … --no-build --filter "FullyQualifiedName~Fea11RunGrant"` | **3 passed / 0 failed / 0 skipped** |
| 4 | `pwsh -NoProfile -File tools/governance/verify_pins.ps1` | `PIN AUDIT: PASS (all 18)`，exit 0 |
| 5 | `pwsh -NoProfile -File tools/governance/check.ps1`（默认） | `Governance check: PASS (3 warnings)`，exit 0 |
| 6 | `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-RUN-GRANT-1.md` | `Governance check: PASS (3 warnings)`，exit 0 |
| 7 | `C:/Python314/python.exe tools/generate_api_inventory.py --check` | **EXIT=0**（rendered counts match FEA-C07） |
| 8 | EV.md 27 个 sha256 逐文件复算（脚本） | **rows=27 / OK=27 / MISMATCH=0 / MISSING=0** |
| 9 | `git diff --name-status 218775bca..a11ded0d3` 对照 `changed-files.txt` | **31 = 31，完全一致**；禁止面 `NONE`；`PROTOCOL_MINOR=3`；`DefaultMinor=3` |
| 10 | 判别性记录静态核对（9 个 `old` 片段/目标/日志 sha） | **9/9 `old` 各出现 1 次；目标存在；日志 restore sha 与现行文件一致；`result=PASS breaks=9`；`final_rebuild exit_code=0`** |
| 11 | 破坏性复跑 B9-equivalent（folder 检测改回扩展名） | **2 failed（unit + 真实 folder IPC，Expected folder / Actual image）**；恢复 sha `6184a0f0…`；重建后 **2 passed** |
| 12 | 破坏性复跑 B7（删能力门） | **1 failed（Expected 0 / Actual 1）**；恢复 sha 一致 |
| 13 | 破坏性复跑 B8（删 seam 内授权调用） | **1 failed（`Assert.Single` empty）**；恢复 sha 一致 |
| 14 | 破坏性复跑「删除 AcceptRun→seam 委托」 | **21 passed（未变红，负向事实）**；恢复 sha 一致 |

---

## 1. 结论与判定摘要

| 项 | 判定 |
|---|---|
| P0 | **0** |
| P1 | **0** |
| P2 | **0** |
| P3 | **2**（R3-01 卡面历史措辞残留；R3-02 AcceptRun 委托行覆盖残差；均非阻断） |
| A. R2-01 folder 边界 | **PASS** |
| B. R2-02 能力缺失判别性 | **PASS** |
| C. R2-03 AcceptRun 接线 | **PASS（有残差，见 R3-02）** |
| D. R2-04 卡/Manifest 口径 | **PASS** |
| E. 证据与门禁一致性 | **PASS** |
| F. 回归/新问题 | **PASS** |
| R2-01…R2-04 | **4/4 CLOSED** |
| AC-R1 | **MET** |
| AC-R2 | **MET（保留）** |
| AC-R3 | **MET（保留）** |
| AC-R4 | **MET（含 R3-02 残差说明）** |
| AC-R5 | **MET** |
| AC-R6 | **MET** |
| AC-R7 | **MET（本 r3 批准后；待 Lead closeout 回填卡面）** |

---

## 2. A–F 逐项核验

### A. R2-01（P2）folder 边界 —— **PASS**

**代码（`a11ded0d3` 字节）**

- `RunSourceRange.Resolve` 已把 kind 判定改为 `KindOfSource(target, normalized)`（`HostRuntime.cs:1717-1720`）。
- `KindOfSource`（`:1741-1749`）：
  - `target.SourceKind` ∈ `{image, folder, zip, cbz, pdf}` → 直接采用（冷启动枚举在 `SourceScanScheduler.TryMap` 读取 Core 的 `source_kind` 并校验，`:1835-1839`；`:1894-1895` 写入 `SourceScanTarget`）；
  - 否则 `Directory.Exists(normalizedPath)` → `folder`；
  - 最后才 `KindOf(normalized)`（扩展名）。
- `SourceReadCoordinator.IssueLockedAsync` 对 `folder` 走 `EnumerateFolder` + 逐成员 locator/ordinal/facts（`SourceReadCoordinator.cs:317-360`）；对目录不再以 `image` 打开 `FileStream`。

**测试与证据**

- 单测 `RunSourceRangeKindDetectsFolderSources`（`SourceRegistryTests.cs:338-359`）：目录 → `folder`；声明 `SourceKind=folder` 对文件路径也优先；zip/image 维持冻结名；声明 `zip` 优先。
- 真实目录源 IPC `FolderSourceMintsABindableGrantThroughTheProductionRange`（`Fea11RunGrantIpcTests.cs:250-338`）：
  - seed 真实 migrations DB + `sources.source_kind='folder'` + `source_locations`/`source_versions` folder manifest facts + 两条 `source_entries`（`001.png`/`002.png`）+ 页 `pf1` 绑定 `se-101`；
  - 构造 **无 `SourceKind`** 的 `SourceScanTarget`，由生产 `RunSourceRange.Resolve` 判为 `folder`，断言 `targets=1`、`unresolved=0`；
  - 真实 `SourceReadCoordinator.AuthorizeRunAsync` → `BoundPages=1`、`MintedGrants=1`、`!Skipped`；
  - 真实 Core `resolve_page_resource(pf1)` 成功；wire/stderr 无 fixture 路径。
- 我实跑 `Fea11RunGrant` **3 passed**，并检查了本次运行的 workspace 证据文件：
  `RunSourceRange folder -> kind=folder, targets=1, unresolved=0` / `folder mint+bind -> bound_pages=1 minted=1` / `resolve_page_resource(folder member) -> OK` / `wire path leak -> 0`。
- **自选破坏点（B9-equivalent）**：把 `KindOfSource` 改回 `return KindOf(normalizedPath);` →
  - `RunSourceRangeKindDetectsFolderSources` **RED**（Expected `folder` / Actual `image`）；
  - `FolderSourceMintsABindableGrantThroughTheProductionRange` **RED**（同断言，真实 IPC 也判别）；
  - 恢复原字节后 sha256 = `6184a0f0b7bca202c1eaa832103a7265de1e94d09969c3b62d580d20cf201802`（与 EV/备份一致），`git status` clean；`--no-incremental` 重建后 **2 passed**。

**口径**

- 卡 L-G12（`:143`）、Handoff §3（`:52`）、EV §7（`:169`）均改为「image 单 entry 源 + folder 源（逐成员 entry 匹配，真实目录源 IPC 证明）+ zip/cbz/pdf 归档首成员（ordinal=0）」，并保留 ①version 通道缺口、②多成员容器其余页不可用。
- **限定（不构成 finding）**：该 folder IPC 的 `SourceScanTarget.Version` 取自 seed receipt 的 `svf1`，与 `binding.accepted_source_version` 匹配；它证明的是 folder kind/成员 entry 通道，不证明生产冷启动 `Version="1"` 的 version 通道（后者已由 L-G12① 登记为不可用）。文档已同时保留 version 缺口，未被表述为「生产全链路可用」。

**判定：PASS（CLOSED）。**

### B. R2-02（P2）能力缺失判别性 —— **PASS**

- 用例 `RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting`（`SourceRegistryTests.cs:297-316`）：
  - `NewSourceDirectory` 构造真实目录 + `source.zip`；
  - `known: [ScanTarget("s1", file, "b1")]`（非空）、`entries: [RegistryEntry("reg-1", root)]`（非空）；
  - `probe:false`，`authorize` 回调会计数；
  - 调用 `AuthorizeSliceAsync("reocr_all", {kind:page,page_id:p1})`，断言 `minted==0`；若抛异常用例同样失败（无 catch）。
- 判别链：`AuthorizeSliceAsync` 第一道 `if (!_enabled || !await ProbeAsync(...)) return;`（`HostRuntime.cs:1869-1872`）。删除能力门后，known+entries 会经 `Resolve` 得到 1 个 target，`_authorize` 被调用 → `minted=1` → 用例红。
- dispatcher 级 `RunAuthorizerCapabilityMissingStillReachesDispatch`（`:317-336`）：`RunAuthorize` 回调若被调用会抛 `InvalidOperationException`；实际以 `probe:false` 跳过授权并到达 dispatch（无 Core → `SidecarException(ProcessExited)`），证明「能力缺失不阻断 dispatch」。
- **我独立删能力门（B7）**：目标用例 **RED（Expected 0 / Actual 1）**；恢复 sha `6184a0f0…` 一致。与 `logs/discrimination.log` B7 的 `RED_AS_EXPECTED + RESTORED sha256=6184a0f0…` 一致。
- 结论：该用例现在**真的**判别能力门（不是 `known: []` 的恒真断言）；AC-R4 该子项证据成立。

**判定：PASS（CLOSED）。**

### C. R2-03（P3）AcceptRun 接线 —— **PASS（CLOSED，残差 R3-02）**

- **生产接线**：`HostRuntime.AcceptRunAsync`（`:71-84`）在 `Policy.WritesAllowed` 检查后直接调用
  `await AuthorizePreparedRunForAcceptAsync(_preparedSlices, _runAuthorizer, preparedRunId, ct)`，再委托 Core `AcceptRunAsync`。
- **Seam**（`:93-106`）：`slices.Take(preparedRunId)`（缺失/过期 → typed `RUN_STALE_PREVIEW`，由 `PreparedRunSlices` 抛出）→ 若 authorizer 非空，调用 `AuthorizePreparedRunAsync(slice.Command, slice.Scope, token)`。
- **测试**：
  - `AcceptRunAuthorizationSeamUsesTheFrozenSlice`（`SourceRegistryTests.cs:361-386`）：真实 `PreparedRunSlices.Remember` 冻结 `{reocr_all, page p1}`，断言 authorizer 收到 `("reocr_all","p1")`；
  - `AcceptRunAuthorizationSeamIsTypedWithoutAUsableSlice`（`:388-422`）：缺失 → `RUN_STALE_PREVIEW`；过期（clock 注入）→ `RUN_STALE_PREVIEW`；无 authorizer 仍先取 slice → `RUN_STALE_PREVIEW`。
- **B8 独立复现**：删除 seam 内 `if (authorizer is not null) { await authorizer.AuthorizePreparedRunAsync(...) }` → `AcceptRunAuthorizationSeamUsesTheFrozenSlice` **RED（`Assert.Single` empty）**；恢复 sha 一致。
- **残差（R3-02，P3）**：删除 `AcceptRunAsync` 对 seam 的那一行/两行委托（保留 seam 实现）后，`SourceRegistry` **21 仍全绿**（我实测）。即：seam 的逻辑被判别，但「`AcceptRunAsync` 确实调用 seam」这一行本身没有测试判别；只能靠代码阅读/评审。r2 的最小修复允许「内部 seam」，且该委托是无条件直接调用，风险低；不阻断。
- 结论：R2-03 的实质（冻结 slice + best-effort authorizer + typed 缺失/过期）已被判别性测试覆盖；CLOSED，附覆盖残差。

### D. R2-04（P3）卡 I-2 / Manifest 口径 —— **PASS**

- **卡 I-2**：
  - 铸造行（`:96`）：「能力 `source.read.run/1` 存在 → 为 Run 相关源调用既有 `IssueAsync`… **Review r1 R1-01 / r2 R2-04 修订**：Host 侧铸造/能力/registry 失败 → **跳过该源（或整体跳过）并继续 dispatch**；仅 Core 对目标页的 typed 拒绝才阻断（R-5 不变）。」
  - 源范围行（`:99`）：「无法解析的已知源计为 unresolved 并**跳过**（不阻断无关 Run）；若 Run 含其 referenced 页，由 Core 对目标页 typed fail-closed。」
  - 与权威「Review r1 处置」R1-01/R1-04、实现（`RunSourceAuthorizer` best-effort）及 R-5 一致。
- **`RESOURCE-MANIFEST.json`**：
  - `delivery_head = a11ded0d3794bdb1afa5f7889d2e25aa4ea7b853`；
  - worktree resource `source_path = "NOT_APPLICABLE（main worktree; delivery head a11ded0d3）"`；
  - temp resource 指向 `G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-1\`（PRESERVE_REFERENCED）；closeout counts deleted/moved/migrated/archived 均 0。
- **L-G12 三处**（卡 `:143`、Handoff `:52`、EV `:169`）均含：
  - 「image 单 entry 源 + folder 源（逐成员 entry 匹配）+ zip/cbz/pdf 归档首成员」；
  - version 通道缺口（枚举 DTO 无 version、冷启动固定 `"1"` → typed `SOURCE_ACCESS_DENIED`、不 dispatch）；
  - 多成员容器其余页不可用；follow-up `FEA-11-RUN-GRANT-2`（proposed，不释放）。
- **观察（R3-01，P3）**：卡面历史段落 `:228`（「交付记录」）与 `:235`（「Review r1 返修」）仍保留旧措辞「image/folder 单 entry 源与归档首成员」；现行 L-G12、Handoff、EV 与「Review r2 返修」段（`:242`）均为修正后的 folder 逐成员口径。属历史文本卫生，不影响当前权威口径；不阻断。

**判定：PASS（CLOSED）。**

### E. 证据与门禁一致性 —— **PASS**

| 项 | 实测 |
|---|---|
| 定向 pytest | **50 passed**（`tests/core/test_host_control.py tests/fea11/test_source_run_grant.py`） |
| `SourceRegistry` | **21 passed**（r1 17 + r2 4） |
| 真实 IPC `Fea11RunGrant` | **3 passed**（首成员 / 多成员 fail-closed / mint 部分失败 / 真实 folder 源） |
| pins | **18/18 PASS** |
| check | 默认 **PASS(3 warnings)**；`-TaskPath` **PASS(3 warnings)** |
| API inventory | **EXIT=0** |
| EV sha256 | **27/27**（11 实现/测试 + 14 证据 + 2 文档；EV 自身排除） |
| scope diff | `218775bca..a11ded0d3` **31 文件**，`changed-files.txt` 逐行一致；全部 ⊆ allowed_paths；`doc/plan`、`doc/contracts`、`schema.py`、migrations、依赖、`core_assembly.py`、`NewManga.App/**`、apps 非允许面 **零 diff**；`PROTOCOL_MINOR=3`、`CoreProtocol.DefaultMinor=3` |
| 全量数字 | 日志/Handoff/EV：**pytest 3281 passed / 10 skipped**、**.NET 1551 / 0 / 89**；gates log `aggregate=1551 passed / 0 failed / 89 skipped`；与 Lead 实测一致（本 Review 未重跑全量，按任务约定核对） |
| 判别性 | 9/9 破坏点定义与目标逐条核对；每个 `old` 片段在当前文件中**恰好出现 1 次**；日志 `RESTORED sha256` 与现行文件 sha 一致；`result=PASS breaks=9`、`final_rebuild exit_code=0`；B7/B8/B9 独立复现 |

- IPC 证据 artifact 抽查：`ipc-folder-*` 的 `run-grant-ipc-folder.txt` 4 行断言均出现；wire 无 fixture 路径。
- 全量 skip 口径：3 个 `NEWMANGA_FEA11_IPC` opt-in（未设 env 时 skipped）是唯一新增 skip；无新增环境 skip 条件，未删除/弱化既有断言。

**判定：PASS。**

### F. 回归 / 新问题 —— **PASS**

- **r2 返修 diff 范围**（`3ffabeb81..a11ded0d3`）：`HostRuntime.cs` +61/-12；`SourceRegistryTests.cs` +124/-5；`Fea11RunGrantIpcTests.cs` +213/-0；无其他实现/测试文件。删除行只有：
  - 旧能力缺失测试体（`known: []` + `AuthorizeForCommandAsync`），被替换为判别性版本（强化，不是弱化）；
  - `AcceptRunAsync` 原内联授权块，被替换为对 seam 的委托（等价重构）。
- **无未登记行为变化**：folder kind 修正 + AcceptRun seam 抽取均在卡/Handoff/EV 登记；无 wire/schema/依赖/契约改动；`HostCommandDispatcher` 在本轮未改。
- **无 `SOURCE_*` 进入 Run 面错误码**：`AllowedRunErrorCodes` 未新增；dispatcher 对非白名单 code 仍降级（沿用 r1/r2 实现）。
- **无路径泄漏**：folder IPC wire/stderr 无 fixture 路径（断言 + 本次运行 artifact）。
- **AC-R4**：五类 step-triggering 命令覆盖（dispatcher 4 命令 + AcceptRun seam）、能力缺失、folder、剪枝、真实 IPC 均成立 → **MET**（附 R3-02 残差说明）。
- **AC-R7**：EV 27/27 + 每文件 commit 链、Manifest 真实路径/`delivery_head`、Handoff limitations（L-G1/2/8/9/10/11/12/13/14）与未宣称项、r1→r2→r3 复审链均成立；卡面未写「全场景可用 / L-R1 全修」→ **MET**（本 r3 批准后；卡面 `<<PARTIAL: … 待 r3>>` 由 Lead closeout 回填）。

**判定：PASS。**

---

## 3. R2-01…R2-04 逐条判定

| Finding | 严重度 | 判定 | 依据 |
|---|---|---|---|
| **R2-01** folder 边界不实 | P2 | **CLOSED** | `KindOfSource` 修正；真实 folder IPC `bound_pages=1` + resolve OK；B9 独立 RED+RESTORED；L-G12/Handoff/EV 边界修正 |
| **R2-02** 能力缺失测试不判别 | P2 | **CLOSED** | known+entries 非空 + 计数 authorize + 0 mint；dispatcher 到达 dispatch；B7 独立 RED+RESTORED |
| **R2-03** AcceptRun 接线未测 | P3 | **CLOSED（残差 R3-02）** | 生产委托 + seam 2 用例；B8 独立 RED+RESTORED；委托行本身未被判别（负向实测） |
| **R2-04** 卡 I-2/Manifest 旧口径 | P3 | **CLOSED** | I-2 两行改写；Manifest `delivery_head`/`source_path` 更新（R3-01 为历史行措辞观察） |

---

## 4. AC-R1…R7 判定

| AC | 判定 | 理由 |
|---|---|---|
| **AC-R1** 协议面 | **MET** | 50 passed 含 host-only/session/closed shape/typed/零写/幂等/能力公告；错误 JSON 无路径（沿用 r1/r2 实测） |
| **AC-R2** 真实装配 E2E | **MET（保留）** | r2 已核；r2 返修未改 Python 实现/测试；grant 测试侧成员形状的说明仍在 |
| **AC-R3** fail-closed | **MET（保留）** | 6 类 typed/零业务写/双 spy/mixed gate 未受 r2 返修影响（r2 已核） |
| **AC-R4** Host 接线 | **MET** | dispatcher 4 命令 + AcceptRun seam + 能力缺失 + folder + 剪枝 + 真实 IPC；B5/B6/B7/B8/B9 判别；R3-02 仅「委托行」覆盖残差 |
| **AC-R5** managed 零回归 | **MET** | Core managed 跳过 + Host best-effort 未变；能力缺失用例强化；全量数字不降 |
| **AC-R6** 零漂移与门禁 | **MET** | 31 文件 ⊆ allowed、禁止面零 diff、minor=3、pins/check/API/全量数字一致 |
| **AC-R7** 证据/Handoff/不夸大 | **MET（本 r3 批准后）** | EV 27/27、Manifest/Handoff/L-G12 边界正确、r1→r2→r3 链成立；待 Lead closeout 回填卡面 AC 勾选/状态 |

---

## 5. 破坏性复跑记录（备份 / 变红 / 恢复 / sha）

| # | 破坏点 | 文件 / 原始 sha256 | 目标用例 | 实测 | 恢复 |
|---|---|---|---|---|---|
| 1 | **B9-equivalent**：`KindOfSource` 改回扩展名判定 | `HostRuntime.cs` / `6184a0f0…`；mutated `dd8b089b…` | `RunSourceRangeKindDetectsFolderSources` + `FolderSourceMintsABindableGrant…` | **2 failed**（两条均 Expected `folder` / Actual `image`），EXIT=1 | 原字节恢复 `6184a0f0…`；`git status` clean；`--no-incremental` 重建后 **2 passed** |
| 2 | **B7**：删能力门 | 同上；mutated `08ad2183…` | `RunAuthorizerSkipsWhenTheCapabilityIsMissingWithoutMinting` | **1 failed**（Expected 0 / Actual 1），EXIT=1 | 恢复 `6184a0f0…` 一致 |
| 3 | **B8**：删 seam 内授权调用 | 同上；mutated `1103a4f2…` | `AcceptRunAuthorizationSeamUsesTheFrozenSlice` | **1 failed**（`Assert.Single` empty），EXIT=1 | 恢复 `6184a0f0…` 一致 |
| 4 | **委托行删除**：删 `AcceptRunAsync` 内对 seam 的调用 | 同上；mutated `4c2b5378…` | `SourceRegistry`（21 例） | **21 passed（GREEN，未判别）** | 恢复 `6184a0f0…` 一致 |

**过程注记**：第 1 次恢复后首次 `dotnet test` 仍红，原因是恢复文件的 mtime 早于破坏构建产物、增量构建未重编译（输出仍为 mutated DLL）；`dotnet build … --no-incremental` 后恢复代码 **2 passed**。这是构建缓存造成的假象，不是代码/断言问题；最终二进制与 tracked 字节一致。第 2/3/4 次均在破坏构建后运行目标用例，恢复后统一 `--no-incremental` 重建；最终 `SourceRegistry` **21 passed**、`Fea11RunGrant` **3 passed**、`HostRuntime.cs` sha `6184a0f0…`、`git status --porcelain` 空。

**备份**：`G:\CODEX\New Manga.workspace\FEA-11-RUN-GRANT-1\review-r3-HostRuntime.cs.bak`（仓外，未入库）；恢复使用 `Copy-Item` 原字节，未经过文本重编码。

---

## 6. 新 findings

| ID | 严重度 | 事实 | 最小修复 | 阻断 |
|---|---|---|---|---|
| **R3-01** | **P3（非阻断）** | 卡面历史段落仍保留旧措辞：`doc/tasks/FEA-11-RUN-GRANT-1.md:228`（交付记录）与 `:235`（Review r1 返修）写「image/folder 单 entry 源与归档首成员」，与现行 L-G12（folder 逐成员 entry）不一致；现行 L-G12/Handoff/EV/「Review r2 返修」段（`:242`）均正确。 | closeout 时把这两处改为「image 单 entry + folder 源（逐成员）+ 归档首成员」，或标注为历史快照。 | 否 |
| **R3-02** | **P3（非阻断）** | `HostRuntime.AcceptRunAsync` 到 `AuthorizePreparedRunForAcceptAsync` 的无条件委托**未被测试判别**：删除该委托、保留 seam 后 `SourceRegistry` 21 仍全绿（实测）；seam 内的授权调用本身由 B8 判别（RED+RESTORED）。 | 可选：补一个 HostRuntime 级接线用例（fake Core/authorizer），或在 Handoff 明确「委托行为由代码评审 + seam 测试覆盖」；不要求本轮返修。 | 否 |

> 说明：不存在 P0/P1/P2 级新问题；R3-01/R3-02 均为文档/覆盖精度，不影响 R2-01…R2-04 的 CLOSED 判定，也不改变 AC-R4 的 MET 结论。

---

## 7. 最终 verdict

**`approved`。**

- R2-01（folder）与 R2-02（能力缺失判别性）这两个 r2 的 P2 均已实质修复，并由**真实 folder IPC + 独立破坏性复跑**证明可判别；R2-03（AcceptRun seam）与 R2-04（I-2/Manifest）也已闭合。
- 定向门禁、pins/check/API inventory、EV 27/27、scope 31 文件零漂移、9/9 判别记录全部一致；没有 P0/P1/P2，没有授权放宽/静默放行/数据破坏/未登记 wire/schema/依赖变化，没有测试删除或弱化。
- 剩余风险仅为 R3-01/R3-02 两个 P3（卡面历史措辞、委托行覆盖残差）与既有 limitations（L-G1/L-G2/L-G8/L-G9/L-G10/L-G11/L-G12/L-G14）；均应在 closeout 保留，不影响集成。
- **集成建议**：Lead 可将 `a11ded0d3` 交付纳入集成；closeout 时更新卡面 AC-R7 勾选/`<<PARTIAL>>`、处理 R3-01，并在 STATUS/Handoff 保留 L-G12 边界与未宣称项。本 Review 不代替 Lead 的 Review Appointment/集成验证与 push 决策。

---

## 8. 真实性声明

- 本报告是 fresh 上下文独立只读 Review：未参与 `FEA-11-RUN-GRANT-1`（或 PREREQ-1）的实现、r1/r2 返修、证据生成或 Handoff 编写；未在同一会话中实现该变更。
- 唯一仓库写入是 `doc/reviews/FEA-11-RUN-GRANT-1-r3.md`（本文件）。未修改实现、测试、证据、卡、契约、STATUS/PLAN/LEDGER；未 `git add`/`commit`/`push`；未删除/移动/归档任何 tracked 文件。
- 破坏性复跑记录见 §5：每次修改前备份、目标用例实跑、按原始字节恢复、sha256 复核 `6184a0f0…` 一致、`git status --porcelain -- <file>` 为空；最终 `--no-incremental` 重建后 21/3 全绿、工作树 clean。
- 运行副作用：仅仓外 workspace 测试夹具（`G:/CODEX/New Manga.workspace/FEA-11-RUN-GRANT-1/fixtures/`）与本 Review 的临时备份/核对脚本；未改写任何 tracked 证据。未运行会重写 `logs/discrimination.log` 的全脚本；判别性以静态核对 + B7/B8/B9 独立复现为准。
- 未重跑全量 pytest/.NET，已在文中明确；全量数字来自 Lead 实测日志与本 Review 的日志一致性核对，未以静态判断冒充实测。
- 本报告所有「实测」均有命令与结果记录；未执行项已明确标注。
