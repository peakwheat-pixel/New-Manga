---
task_id: FEA-11-L-S1-B-RECOVERY-REAUTH-1
author: l-s1b-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 3d97e3b18
start_head: e0b37622b
delivery_head: 80d2799de7195ccdec6954b523eea6830f315335
status: in_review
supersedes_handoff: doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-e9e1132a5.md
---

# Handoff — FEA-11-L-S1-B-RECOVERY-REAUTH-1（B1：App 显式恢复/重授权入口；r2 返修交付）

- Task：`doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md`（Owner=`l-s1b-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-07（Asia/Shanghai）
- 交付基线：卡 `base_commit=3d97e3b18`；实现起点 `e0b37622b`（工作树 clean，实测）；**`delivery_head=80d2799de7195ccdec6954b523eea6830f315335`**
- 本次 commit：`f1272f29a`（r2 修复）、`80d2799de`（r2 测试，**delivery_head**）；r2 卡/本 Handoff/证据为同批文档提交（未 push、未建 worktree）
- 前序交付：首轮 `0fdde2de8` + docs `710e749a9`（Handoff `…-0fdde2de8.md`）；r1 `e9e1132a5` + docs `5dd6f7bb5`（Handoff `…-e9e1132a5.md`）
- 独立 Review：r1 **approved（P0=0/P1=0/P2=2/P3=11）**；r2 **approved（P0=0/P1=0/P2=1/P3=3）**——本 head 处置 r2 P2×1 + P3×3
- 环境：Windows 11 / PowerShell 7.6.8 / CPython 3.14.6 / .NET（net9.0）；零新依赖、零 schema/migration/wire/契约改动

## 1. 交付结果（AC-LSB-1…10 全 MET；卡面已勾选，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| AC-LSB-1 入口仅显式 | **MET** | 失败分支只做 1 次**只读**探针；VM 端口计数 `reauthorize=0/reset=0/resetConfirm=[]`；真实 IPC `registry_unchanged_after_failure=true`；判别 B1 |
| AC-LSB-2 分流正确 | **MET** | 探针 UNAVAILABLE → 只给重置；探针成功 + mint 失败 → 只给重授权；其它码 → 无动作且显示该码；r1 批量/歧义 → `MultipleSources` 无动作且不探针；r1 folder → `FolderSource`；**r2 P2-01**：歧义（0 targets + `ambiguous=true`）**仍到达**「请只选择一个来源」提示，零 wire（`AmbiguousBatchWithNoTargets_*`、`HostControllerAmbiguityPath_*`、VM `AmbiguousBatch_ReachesTheRealDiagnosis_*`） |
| AC-LSB-3 顺序与幂等 | **MET** | 2 条 stale 全撤销（generation+1/`revoked_at`）后只注册 1 条；帧序 `list→revoke×2→register`；重复执行恒 1 active（revoked 行累积已登记）；注册用条目**已登记** `roots[0]`；判别 B2/B3 |
| AC-LSB-4 部分失败 fail-closed | **MET** | 撤销成功/注册失败 → `RevokedButNotRegistered` + 「已撤销…未重新授权（typed 码）」；无回滚、不显示成功；可重试；撤销失败 → 中止且**零注册**；传输/只读失败 → typed 结果不逃逸 UI；r1 P3-11 文案「已确认撤销 N 条」 |
| AC-LSB-5 不自动重授权（安全核心） | **MET** | 计划/mint 路径零恢复命令（源码守卫）；复用选择器语义逐字不变；r1 P2-01：`LastPlanFailureSource` + `AttributeFailedSource` 只指向唯一失败源，批量在任何 wire 调用前被拒绝（健康源零撤销/零注册）；判别 B1/B5 |
| AC-LSB-6 授权面不扩大 | **MET** | 恢复成员参数仅 `bool`/`CancellationToken`；只在 `ISourceImportController`；`HostCommandRegistry.All.Count == 111` 冻结；API inventory EXIT=0 |
| AC-LSB-7 脱敏 | **MET** | 文案/通知只含叶子名/typed 码/计数；VM 全文本 0 绝对路径 & 0 `quarantine`；脚本响应**故意带** `quarantine_path` 也不泄漏；r1 P2-02：真实 IPC wire **77 帧 0 路径命中**、`[REDACTED]` 帧 **7**、wire/stderr `quarantine` 0；判别 B4 |
| AC-LSB-8 零漂移/门禁 | **MET** | build 0/0；定向 **47/0/0**；gated IPC 1/0/0；定向 pytest 74；全量 pytest 3317/10（=基线）；全量 .NET **1617/0/93**（基线 1570/0/92：+47、+1 skip）；pins 18/18；check PASS(3w)×2；API EXIT=0；scope PASS（禁止面 11 项 ZERO_DIFF、`CORE_PROTOCOL_MINOR=3`）；FEA-09 CLEAN |
| AC-LSB-9 闭环证据（gated 真实 IPC 1 条） | **MET** | `logs/ipc-closed-loop.{json,txt}`：phase A 同路径替换 → typed 失败 → 显式重授权 → 再预览成功 → 重新导入 Completed → 枚举返回新 registry/gen；phase B 同物理身份 + 新 registry → **L-S4-A 原地刷新**（同 `location_id`、registry 换新、`last_verified_at` 非空、枚举 gen=1） |
| AC-LSB-10 边界/不夸大 | **MET** | 只承诺 file-source 同路径恢复；多选/歧义不给恢复；folder 不给动作；revoked 行累积登记；L-S4-1/L-S4-2/B2/B3 保留；C-17 journal 撤销撕裂仅登记 |

### 1.1 r2 变更要点

1. `SourceRecoveryModels.cs`（`DiagnoseAsync`）：`ambiguous` 判定移到「空 targets」守卫**之前**——多选无法归因时 `HostController` pin 0 targets + `ambiguous=true`，旧顺序先返回 `NotApplicable`，导致卡/Handoff 承诺的「请只选择一个来源重新预览」提示**不可达**。修复后：歧义 → `MultipleSources` 提示可达，仍**零 wire/零撤销/零注册**；非歧义空列表仍 `NotApplicable`（反向用例钉住）。
2. 其余 r1 语义不变（单源归因、批量在任何 wire 调用前拒绝、folder 拒绝、部分失败 fail-closed、脱敏、命令面冻结）。

## 2. 验证证据（实跑；`delivery_head=80d2799de`）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **成功 0 warning / 0 error（EXIT 0）** | `logs/build.log` |
| VM/编排级（卡面命令） | `dotnet test .../NewManga.App.Tests -c Release --filter "FullyQualifiedName~SourceRecovery"` | **PASS 47 / 0 / 0** | `logs/app-unit.log` |
| gated 真实 IPC（卡面命令） | `NEWMANGA_FEA11_IPC=1 dotnet test .../NewManga.Host.Tests --filter "FullyQualifiedName~SourceRecoveryIpc"` | **PASS 1 / 0 / 0**；receipt `wire_frame_count=77 wire_path_hits=0 wire_redacted_frames=7` | `logs/host-ipc.log`、`logs/ipc-closed-loop.{json,txt}` |
| 定向 Core 回归 | `python -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 74 passed**（基线 74，不降） | `logs/feature.log` |
| 全量 Python | `python -m pytest tests -q` | **PASS 3317 passed / 10 skipped**（= 基线）；跑后 `git checkout -- verification/FEA-09` → CLEAN | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **PASS 1617 / 0 failed / 93 skipped**（基线 1570/0/92：+47 本卡、+1 新增 opt-in skip） | `logs/full-dotnet.log` |
| 治理 | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** ×2 / **EXIT=0** | `logs/gates-governance.log` |
| 范围 | scope 校验（最终 docs commit 后重算） | **PASS**（全变更路径 ALLOWED、forbidden=0、禁止面 11 项 ZERO_DIFF、`CORE_PROTOCOL_MINOR=3`；1 项并发非交付标注） | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\tools\discrimination.ps1` | **6/6 RED_AS_EXPECTED + 6/6 RESTORED（sha256）+ final rebuild EXIT 0**（新增 **B6** 守卫顺序回归点） | `logs/discrimination.log` |

### 2.1 Review r2 处置摘要（详见 EV §8）

- **R2-P2-01 FIXED**：歧义分支可达（守卫顺序）；仍零 wire；判别 **B6**；4 条新测试（orchestrator ×3 + VM/真实编排端到端 ×1）。
- **R2-P3-01 FIXED**：卡面 AC-LSB-8 证据数字改为实测 **47 / 1617 / +47**。
- **R2-P3-02 FIXED**：scope 快照按**最终 docs commit** 重算，保留 `concurrent` 披露。
- **R2-P3-03 FIXED**：卡内全量命令统一 `apps/desktop-avalonia/NewManga.sln`（首轮记录行标注历史数字）。

### 2.2 诚实披露

- **共享工作树**：`main` 同期由 Lead 提交 `ac528828b`（docs-only progress handoff）；本卡 scope 按自有 commit 链计算，禁止面零 diff。
- **真实 IPC 口径**：phase A 的「同路径替换」改变文件物理身份 → Core 写**新的** `source_locations` 行（旧行留只读投影，Host 调度器按撤销 registry fail-closed 丢弃）；**L-S4-A 原地刷新**只在「同物理身份 + 新 registry」成立，phase B 用隔离 registry（Passthrough，文件不动）构造等价不变量并实测同一 `location_id` 刷新；**不宣称**替换场景是原地刷新。
- **wire 脱敏事实**：Core wire 日志存帧前把绝对路径重写为 `[REDACTED]`，所以「哪些帧原本带路径」不可观测；本卡只断言可观测事实（0 命中 + 存在 `[REDACTED]` 帧）。
- **NOT_RUN：无**；已知 flaky `FluentResidual2VisualEvidenceTests` 未命中（1617/0 无失败）。
- 隔离根：`G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\`；**未写** `verification/FEA-09/**`。

## 3. 已知 limitation（closeout 必须保留）

- **B2（roots 可用性投影）/ B3（扫描侧投影）未做**（B2 需 C-16 v1.5 1 pin）。
- **L-S4-1**（零交互自动恢复枚举）仍开放（需 C-16 v1.5 批量载体）；**L-S4-2**（folder 身份键）未修 → 只承诺 **file-source 同路径恢复**；重定位走「重新导入成新源」。
- **多选/歧义不给恢复**：只针对唯一失败来源；无法唯一归因时不提供动作、不探针、不写注册表，UI 显示「请只选择一个来源重新预览」（r2 已保证该提示可达）。
- **folder 源不给恢复**：folder 根进入恢复面被拒绝并说明（file-source only）。
- **重复显式恢复累积 revoked 行**：active 恒 1，但 registry 只置位不删除；每次重复新增 revoked + active 各一条。
- **revoke ACK 失败计数口径**：Host 先持久化再等 ACK；失败时计数为「已确认」条数，实际可能多一条；无回滚。
- **C-17 journal 撤销撕裂（仅登记）**：撤销后绑定旧 `registry_id` 的 C-17 apply/journal 重试永久失败；需 B2/L-S4-B 批量设计；文案不承诺「重试自动恢复」。
- **`quarantine_path` 不展示**：不读、不返回、不渲染（C-16 §7.3 冲突留 UNFREEZE）。
- **真实 `HostController` 恢复接缝无端到端测试**：需可启动 runtime；以生产代码级归因单测 + 真实 IPC 覆盖，登记接受。
- **不宣称**：不写「零交互自愈」「根级问题全解」「自动恢复/撤销后自动放行」；不写「替换场景=原地刷新」；L-R1 未全修；独立 r3 复审由 Lead 指派（本会话不自审）。

## 4. 接收方式

- 分支 `main`，未建 worktree、未 push；`delivery_head=80d2799de`（r2 修复 `f1272f29a` + r2 测试 `80d2799de`），r2 卡/Handoff/证据为同批文档提交。
- 复现：
  ```powershell
  dotnet build apps/desktop-avalonia/NewManga.sln -c Release
  dotnet test apps/desktop-avalonia/tests/NewManga.App.Tests/NewManga.App.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRecovery"
  $env:NEWMANGA_FEA11_IPC=1; dotnet test apps/desktop-avalonia/tests/NewManga.Host.Tests/NewManga.Host.Tests.csproj -c Release --filter "FullyQualifiedName~SourceRecoveryIpc"
  C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q
  C:/Python314/python.exe -m pytest tests -q; git checkout -- verification/FEA-09
  dotnet test apps/desktop-avalonia/NewManga.sln -c Release; git checkout -- verification/FEA-09
  pwsh -NoProfile -File tools/governance/verify_pins.ps1
  pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md
  C:/Python314/python.exe tools/generate_api_inventory.py --check
  pwsh -NoProfile -File "G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\tools\discrimination.ps1"
  ```
- 前置：Windows 交互用户（IPC 默认 `C:/Python314/python.exe` 或 `NEWMANGA_BUILD_PYTHON`）；判别性脚本会临时改写并**按原字节恢复** `ImportDockViewModel.cs`/`SourceRecoveryModels.cs`（不要并发实施同一文件）。

## 5. 下一任务建议（供 DSH 裁决；本 Handoff 不授权）

- **立即下一步**：Lead 指派 **r3 窄面复审**（只读 `80d2799de`；重点 R2-P2-01 守卫顺序/提示可达性、仍零 wire、47 例与 6/6 判别；作者会话不自审）。
- **后续候选（非本卡授权）**：B2（`source_list_roots` 可用性投影 + 多根管理面，与 L-S4-B 共用**一个** C-16 v1.5 载体，1/18 pins）；B3（扫描侧投影）；L-S4-2（folder 身份键）；C-17 journal 撤销撕裂的批量处置设计。
- Recovery point：`G:\CODEX\New Manga`，`main`，`80d2799de`（证据目录 `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/`）。

## 6. 风险与遗留

- **最高风险三重钉住**：B1（自动重授权）、B5（批量退回全部选中）、B6（歧义提示不可达）+ `Reauthorize_RefusesABatchBeforeAnyWireCall` + `AttributedFailure_LeavesTheHealthySiblingCompletelyUntouched`。
- **撤销不可回退**：部分失败只如实展示 + 可重试；不得增加「自动回滚撤销」。
- **命令面/C-07 零扩**：任何新增命令/能力/错误码都会使命令计数守卫与 API inventory 同时变红。
- **重置丢弃全部授权**：只在「探针本身 typed 不可用」时提供，二次确认；文案不得暗示「只影响该来源」。
