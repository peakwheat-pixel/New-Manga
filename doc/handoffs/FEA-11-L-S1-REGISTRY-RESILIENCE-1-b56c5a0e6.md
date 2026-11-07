---
task_id: FEA-11-L-S1-REGISTRY-RESILIENCE-1
author: l-s1-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 55306cb84
start_head: db12dc5e5
delivery_head: b56c5a0e6adf6f4cba31f1b3b1d8ee950c7bb84b
status: in_review
supersedes_handoff: null
---

# Handoff — FEA-11-L-S1-REGISTRY-RESILIENCE-1（A：Registry 读取韧性；C-15 v1.5 §5）

- Task：`doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md`（Owner=`l-s1-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-07（Asia/Shanghai）
- 交付基线：卡 `base_commit=55306cb84`；实现起点 `db12dc5e5`（工作树 clean，实测）；**`delivery_head=b56c5a0e6adf6f4cba31f1b3b1d8ee950c7bb84b`**
- 交付 commit：`1ac8cc0b7`（实现）、`b56c5a0e6`（测试，**delivery_head**）；证据/卡/本 Handoff 为同批文档提交（未 push、未建 worktree）
- 环境：Windows 11 / PowerShell 7.6.8 / CPython 3.14.6 / .NET（net9.0）；零新依赖、零 schema/migration/wire/契约改动
- 依据：卡「DSH 裁决」+ `doc/reviews/FEA-11-L-S1-REGISTRY-RESILIENCE-1-scope-r1.md`（READY-WITH-UNFREEZE）+ `doc/plan/FEA-C15_SOURCE_STORAGE_DRAFT.md` **v1.5 §5**（pin `f9e376a0ed4c`）

## 1. 交付结果（AC-L1…L8 全 MET；卡面已勾选，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| AC-L1 文件级损坏仍整库 fail-closed（零放宽） | **MET** | `Load()` 仍只对 magic/version/长度/DPAPI/JSON/条目结构判损坏并原样走「`.corrupt-<utc>` 复制 + 不覆盖 + 不建空文件 + `SOURCE_REGISTRY_UNAVAILABLE`」；新增 12 例矩阵（短文件/截断/magic/length/JSON/format_version/重复 id/generation 0/空 roots/非规范 root/readable=false/**真实 DPAPI 篡改**）逐一断言原字节保留 + corrupt 副本 + `List`/`Authorize` 均 typed；判别点 B4（放宽为「空 registry」）→ 红 |
| AC-L2 根级不可用不再整库不可读 | **MET** | 混合 registry（有效根 + 已删根）：`List()` 返回 2 条（顺序/字段/root 不变、`List` 零字节写）；有效根 `Authorize` 成功且只持久化其 `last_used_at`；缺失根请求 typed + 字节不变 + **不产生 `.corrupt-*`**；缺失根存在时 `Register` 新根成功（导入解阻）；判别点 B1（恢复 Load 预探针）→ 红 |
| AC-L3 授权期逐请求校验（安全核心） | **MET** | `Authorize` 在**同一 `Locked()` 内、读盘之后**按「请求路径所属根」重新探针 identity（存在/可读/volume+file id），不可用/不匹配 → 该请求 `SOURCE_REGISTRY_UNAVAILABLE` 且**零写**；**不跨调用缓存**（先成功后删根 → 第二次调用即 typed）；被替换根**不重新获得授权**（B2 删除补位 → 红）；缺失根被当作无授权 → `SOURCE_ACCESS_DENIED` 而非 typed（B3 → 红）；根外/前缀兄弟/`..`/相对路径仍 `SOURCE_ACCESS_DENIED`，无回退（B5 → 红） |
| AC-L4 不自动重建/恢复/重授权 | **MET** | 不匹配后 registry 字节不变、持久化 identity 保持原（错误）值（无写回/无重建）；无自动重注册路径；`Revoke`（generation+1/`revoked_at`）与显式 `source_reset_registry` 行为不变（`Reset(false)`→`INVALID_REQUEST`、`Reset(true)`→quarantine + 空库） |
| AC-L5 错误码/语义零新 | **MET** | 复用 `SOURCE_REGISTRY_UNAVAILABLE`；零新错误码/命令/字段/能力/schema/依赖；`doc/plan`、`doc/contracts`、`schema.py`、`NewManga.App/**`、`NewManga.CoreClient/**` 全空 diff（`scope-validation.log`）；撤销/ACL/加密边界零改动 |
| AC-L6 测试/证据 | **MET** | 混合 registry 单测 8 例 + 1 条 gated 真机 IPC（`NEWMANGA_FEA11_IPC=1`，真实 Python Core + 真实 DPAPI registry：`source_list_roots` 2 条、有效根铸造成功、缺失根 typed 零写、`source_register_root` 成功、`List` 3 条）+ 判别性 **5/5 RED + 5/5 字节级 RESTORED + final rebuild EXIT 0**；EV 逐文件 sha256；本 Handoff |
| AC-L7 零漂移/门禁 | **MET** | pins 18/18（C15 `f9e376a0ed4c`）；`check.ps1` 默认与 `-TaskPath` PASS（3 warnings）；API inventory EXIT 0；全量 pytest **3317 passed / 10 skipped**（≥ 卡基线 3305/10；+12 来自同期 L-S4 已提交的 Python 测试，见 §2 披露）；全量 .NET **1570 passed / 0 failed / 92 skipped**（基线 1562/0/91：+8 本卡单测、+1 opt-in IPC skip）；scope diff ⊆ allowed_paths；跑后 `git checkout -- verification/FEA-09` 已执行且 `git status` 复查 CLEAN |
| AC-L8 不夸大 | **MET** | 未写「恢复已可用/根级问题全解/L-R1 全修」；limitation B/C 保留并写入本 Handoff §3；明确「条目级不可用为派生状态、不持久化」 |

### 1.1 实现要点（1 文件）

`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceAccessRegistry.cs`

1. `Load()`：删除逐根 `SourceSecurity.Identity()` 比对；仅保留文件级 + **持久化结构**校验（root 已 normalize、`readable` 结构位保留）。文件级失败路径**一字未改**。
2. `Authorize()`：路径 → 所属注册根（containment 精确，不跨根不回退）→ **逐请求** `VerifyRootIdentity(root)`（每调用内每根至多 1 次探针，**不跨调用缓存**）→ 再 `RejectReparseAncestors(path)`（保持原有 reparse/遍历拒绝）；全部通过后才 `Save`（失败零写）。
3. `VerifyRootIdentity()`：`SourceSecurity.Identity(root.Root)` 的 existence/readability/volume+file id 复核；任何失败 → typed `SOURCE_REGISTRY_UNAVAILABLE`（零新码）；不写回、不重建、不重授权。
4. `List()`：行为不变，仅补文档口径（返回全部条目；不可用为派生状态、无新增持久字段）。

## 2. 验证证据（实跑；`delivery_head=b56c5a0e6`）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **成功 0 warning / 0 error**（EXIT 0） | `logs/build.log` |
| Host 单测（AC-L1/L2/L3 + 既有回归） | `dotnet test tests/NewManga.Host.Tests/... --filter "FullyQualifiedName~SourceRegistry"` | **PASS 40 / 0 / 1 skipped（41）**（全量 filter 基线 32：2A 21+8、2B +3；本卡 +8） | `logs/host-unit.log` |
| gated 真机 IPC（AC-L2/L6、D-7 混合 registry） | `NEWMANGA_FEA11_IPC=1 dotnet test ... --filter "FullyQualifiedName~Ipc_MixedRegistry"` | **PASS 1 / 0 / 0**；隔离 receipt：`source_list_roots=2`、`IssueAsync(healthy)=minted`、`IssueAsync(missing)=SOURCE_REGISTRY_UNAVAILABLE zero_write=1 no_corrupt_copy=1`、`source_register_root=registered`、`List=3` | `logs/host-ipc.log`（+隔离根 receipt） |
| 定向 Core 回归 | `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 74 passed**（基线 74，不降） | `logs/feature.log` |
| 全量 Python（AC-L7） | `pytest tests -q` | **PASS 3317 passed / 10 skipped**；`git checkout -- verification/FEA-09` 后 CLEAN | `logs/full-pytest.log` |
| 全量 .NET（AC-L7） | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **PASS 1570 / 0 / 92**；`git checkout -- verification/FEA-09` 后 CLEAN | `logs/full-dotnet.log` |
| 治理（AC-L7） | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** / **EXIT=0** | `logs/gates-governance.log` |
| 范围（AC-L7） | `python verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/scope_validation.py` | **PASS（changed 全 ALLOWED；zero-drift 全空）** | `scope-validation.log`、`changed-files.txt` |
| 判别性（AC-L1/L2/L3/L4） | `python verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/discrimination.py` | **5/5 RED_AS_EXPECTED + 5/5 RESTORED + final rebuild EXIT 0** | `logs/discrimination.log` |

- **判别性 5 破坏点**：B1 恢复 Load 预探针（单根缺失再判整库损坏）；B2 删除 `Authorize` 逐请求身份补位（**被替换根重新获得授权**——本卡最大安全回退）；B3 缺失根当「无授权」；B4 文件级损坏放宽为「空 registry」；B5 根外路径回退。每个破坏点均落到**一个**目标用例变红并按原字节恢复（sha256 一致）。
- **共享工作树披露（诚实记录）**：同一 `main` 工作树同期由 `FEA-11-L-S4-LOCATION-AUTH-REFRESH-1` 会话使用，其 commit `6dd36aad7`/`0ebb234bf`（Python `src/**` + `tests/**`）落在本卡 `delivery_head` 之后。本卡**零 Python/契约/STATUS/PLAN/LEDGER diff**；scope 校验按本卡自有 commit 链（`1ac8cc0b7`/`b56c5a0e6`）计算，不含其文件。全量 pytest 的 +12 passed 即来自该会话已提交的测试，**不归属本卡**；本卡未修改/暂存/提交其任何文件。
- **未运行/不可判定（NOT_RUN，不写 PASS）**：mixed registry 的**调度器级**用例未新增（`SourceScanSchedulerTests.cs` 不在本卡 frozen write domain，D-6）；以「registry 级混合单测 + 既有单目标 scheduler 用例保持绿（缺失/替换根仍 `Error(SOURCE_REGISTRY_UNAVAILABLE)`）+ 真实 IPC 混合」组合证据替代，**不**宣称调度器级混合矩阵已覆盖。
- 已知 flaky：`FluentResidual2VisualEvidenceTests`（git-status 快照竞态）。本次全量 .NET 先落盘证据后运行，未命中；`obj/bin` 由判别性 final rebuild 恢复为交付字节。
- 隔离根：`G:\CODEX\New Manga.workspace\FEA-11-L-S1-REGISTRY-RESILIENCE-1\`（IPC 夹具 + discrimination 备份 + 门禁原始输出）；**未写** `verification/FEA-09/native-registry/**`。该隔离根中 PREREQ 会话的遗留脚本/`tmp/c15.blob` 原样保留（见 `RESOURCE-MANIFEST.json` note）。

## 3. 已知 limitation（closeout 必须保留）

- **B（恢复/重授权入口不存在，未修）**：产品内仍无根级恢复/重授权 UI；`source_reset_registry`/`source_revoke_root` App 侧 0 调用。本卡只保证「撤销/重置命令在 registry 部分不可用时仍可用」（B 卡的最小台阶），**不**宣称用户可自行恢复。被替换/缺失根在该入口接线前无法在产品内恢复。
- **C（`.corrupt-*` 无界复制，未修）**：文件级损坏每次 `Load` 失败复制一份且无清理；本卡消除了「根缺失」这一主驱动，文件级损坏的放大仍在（另案/limitation）。
- **错误码码义收窄（未新增码）**：`SOURCE_REGISTRY_UNAVAILABLE` 现同时表示「文件级损坏」与「该请求所属根当前不可用」；词表细化（区分整库 vs 单根）需 C-16 §6 + C-06 各 1 pin，另案。
- **D-6 投影不在本卡**：`SourceScanScheduler/HostRuntime/SourceWatcher` 的可用性投影未改；`SourceScanScheduler.cs:1570-1571` 的注释仍描述旧「整库不可读」口径（**注释过时、行为已按目标级 typed 工作**），建议随 D-6/后续维护卡更新文案。
- **被替换根的真实「删除+重建」物理夹具未使用**：NTFS 可能复用 File ID（scope review R4 flaky 风险），故确定性夹具采用「注册侧 identity 与当前 identity 不匹配」（与替换后的状态等价）；调度器既有 `ReplacedRoot` 用例仍保留真实重建路径并保持绿。
- **`SourceRegistryTests.cs` 未改**：既有 DPAPI/字节级/Reset 覆盖原样保留（本卡回归依赖它），新增矩阵落在新文件；不重复断言。
- **不宣称**：不写「恢复已可用」「根级问题全解」「L-R1 全修」「调度器级混合矩阵已覆盖」；FEA-11 AC11-5/AC11-9 未回填；独立 Review 由 Lead 指派（本会话不自审）。

## 4. 接收方式

- 分支 `main`，未建 worktree、未 push；`delivery_head=b56c5a0e6`（实现 `1ac8cc0b7` + 测试 `b56c5a0e6`），证据/卡/Handoff 为同批文档提交。
- 复现：
  ```powershell
  dotnet build apps/desktop-avalonia/NewManga.sln -c Release
  dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRegistry"
  $env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~Ipc_MixedRegistry"
  C:/Python314/python.exe -m pytest tests -q; git checkout -- verification/FEA-09
  dotnet test apps/desktop-avalonia/NewManga.sln -c Release; git checkout -- verification/FEA-09
  pwsh -NoProfile -File tools/governance/verify_pins.ps1
  pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-L-S1-REGISTRY-RESILIENCE-1.md
  C:/Python314/python.exe tools/generate_api_inventory.py --check
  C:/Python314/python.exe verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/scope_validation.py
  C:/Python314/python.exe verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/tools/discrimination.py
  ```
- 前置：Windows 交互用户（DPAPI）；`C:/Python314/python.exe`（或 `NEWMANGA_BUILD_PYTHON`）；判别性脚本会临时改写并**按原字节恢复** `SourceAccessRegistry.cs`（不要在并发实施同一文件时运行）。

## 5. 下一任务建议（供 DSH 裁决；本 Handoff 不授权）

- **立即下一步**：Lead 指派**独立上下文** Review（只读 `b56c5a0e6` + 证据目录；作者会话不自审），Review 通过后再谈集成/closeout。
- **后续候选**（非本卡授权）：`FEA-11-L-S1-RECOVERY-1`（B：`source_list_roots` 可用性投影 + App 分流不复用失效条目 + 撤销/重置/重注册入口 + L-S4 刷新），需 C-16 §1 增补；以及 D-6 的调度器/watcher 可用性投影与注释同步。
- Recovery point：`G:\CODEX\New Manga`，`main`，`b56c5a0e6`（证据目录 `verification/FEA-11-L-S1-REGISTRY-RESILIENCE-1/`）。

## 6. 风险与遗留

- 安全回退风险已由 AC-L3 逐请求补位 + B2/B3/B5 判别性 + 零字节写断言覆盖；任何后续把探针移出 `Locked()` 或缓存跨调用结果的改动都必须重新走判别性。
- 根不可用请求统一给 `SOURCE_REGISTRY_UNAVAILABLE`（不区分「不存在/不可读/身份不符」），避免泄漏路径与根级状态（C-16 §7）；如需细分码，另案加 additive 契约。
- 本卡不动 `SourceScanScheduler/HostRuntime/SourceWatcher`（D-6），其可用性投影仍是旧口径；scheduler 注释文案过时已登记。
