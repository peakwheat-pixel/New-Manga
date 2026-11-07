---
task_id: FEA-11-L-S1-B-RECOVERY-REAUTH-1
author: l-s1b-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 3d97e3b18
start_head: e0b37622b
delivery_head: e9e1132a55d8a04617b7e69e9f93f043e08f450b
status: in_review
supersedes_handoff: doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-0fdde2de8.md
---

# Handoff — FEA-11-L-S1-B-RECOVERY-REAUTH-1（B1：App 显式恢复/重授权入口；r1 返修交付）

- Task：`doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md`（Owner=`l-s1b-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-07（Asia/Shanghai）
- 交付基线：卡 `base_commit=3d97e3b18`；实现起点 `e0b37622b`（工作树 clean，实测）；**`delivery_head=e9e1132a55d8a04617b7e69e9f93f043e08f450b`**
- 本次 commit：`019feeb6e`（r1 修复）、`e9e1132a5`（r1 测试，**delivery_head**）；r1 卡/本 Handoff/证据为同批文档提交（未 push、未建 worktree）
- 首轮交付（被本次取代）：`0fdde2de8`（实现 `be3b0c242` + 测试 `0fdde2de8`）+ docs `710e749a9`；对应 Handoff `doc/handoffs/FEA-11-L-S1-B-RECOVERY-REAUTH-1-0fdde2de8.md`
- 独立 Review r1：`doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-r1.md`，**approved（P0=0/P1=0/P2=2/P3=11）**；本 head 处置 P2×2 + P3×11（见 §2.1 / EV §7）
- 环境：Windows 11 / PowerShell 7.6.8 / CPython 3.14.6 / .NET（net9.0）；零新依赖、零 schema/migration/wire/契约改动

## 1. 交付结果（AC-LSB-1…10 全 MET；卡面已勾选，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| AC-LSB-1 入口仅显式 | **MET** | 失败分支只做 1 次**只读**探针；VM 端口计数 `reauthorize=0/reset=0/resetConfirm=[]`；真实 IPC `registry_unchanged_after_failure=true`；判别 B1 |
| AC-LSB-2 分流正确 | **MET** | 探针 UNAVAILABLE → 只给重置；探针成功 + mint 失败 → 只给重授权；其它码 → 无动作且**显示该码**；**r1 P2-01**：批量/歧义 → `MultipleSources` 无动作且不探针；**r1 P3-04**：folder → `FolderSource` 无动作 |
| AC-LSB-3 顺序与幂等 | **MET** | 2 条 stale 全撤销（generation+1/`revoked_at`）后只注册 1 条；帧序 `list→revoke×2→register`；重复执行恒 1 active（revoked 行累积已登记）；注册用条目**已登记** `roots[0]`；判别 B2/B3 |
| AC-LSB-4 部分失败 fail-closed | **MET** | 撤销成功/注册失败 → `RevokedButNotRegistered` + 「已撤销…未重新授权（typed 码）」；无回滚、不显示成功；可重试；撤销失败 → 中止且**零注册**；传输/只读失败 → typed 结果不逃逸到 UI；r1 P3-11 文案「已确认撤销 N 条」 |
| AC-LSB-5 不自动重授权（安全核心） | **MET** | 计划/mint 路径零恢复命令（源码守卫）；复用选择器语义逐字不变；**r1 P2-01**：`LastPlanFailureSource` + `AttributeFailedSource` 只指向唯一失败源，批量在任何 wire 调用前被拒绝（健康源零撤销/零注册）；无 stale 条目时拒绝而非盲注册；判别 B1/B5 |
| AC-LSB-6 授权面不扩大 | **MET** | 恢复成员参数仅 `bool`/`CancellationToken`（无路径/ID）；只在 `ISourceImportController`，`IHostController` 无成员；`HostCommandRegistry.All.Count == 111` 冻结；API inventory EXIT=0 |
| AC-LSB-7 脱敏 | **MET** | 文案/通知只含叶子名/typed 码/计数；VM 全文本 0 绝对路径 & 0 `quarantine`；脚本 Host 响应**故意带** `quarantine_path` 也不得泄漏；**r1 P2-02**：真实 IPC wire **77 帧 0 路径命中**、`[REDACTED]` 帧 **7**（证明脱敏发生）、wire/stderr `quarantine` 0；判别 B4 |
| AC-LSB-8 零漂移/门禁 | **MET** | build 0/0；定向 **43/0/0**；gated IPC 1/0/0；定向 pytest 74；全量 pytest 3317/10（=基线）；全量 .NET **1613/0/93**（基线 1570/0/92：+43、+1 skip）；pins 18/18；check PASS(3w)×2；API EXIT=0；scope PASS（禁止面 11 项 ZERO_DIFF、`CORE_PROTOCOL_MINOR=3`）；FEA-09 CLEAN |
| AC-LSB-9 闭环证据（gated 真实 IPC 1 条） | **MET** | `logs/ipc-closed-loop.{json,txt}`：phase A 真实同路径替换 → typed 失败 → 显式重授权 → 再预览成功 → 重新导入 Completed → `source_list_scan_targets` 新 registry/gen；phase B 同物理身份 + 新 registry → **L-S4-A 原地刷新**（同 `location_id`、registry 换新、`last_verified_at` 非空、枚举 gen=1） |
| AC-LSB-10 边界/不夸大 | **MET** | 只承诺 file-source 同路径恢复；多选/歧义不给恢复；folder 不给动作；revoked 行累积登记；L-S4-1/L-S4-2/B2/B3 保留；C-17 journal 撤销撕裂仅登记 |

### 1.1 实现要点（r1 变更）

1. `Services/SourceRecoveryModels.cs`：新增 `SourceRecoveryTarget`/`SourceRecoveryBlockReason`；`DiagnoseAsync` 对**批量/歧义/folder** 直接返回 blocked（不发探针）；`ReauthorizeAsync` 拆为「守卫入口 + 单源 kernel」——批量在任何 wire 调用前 `INVALID_REQUEST`，folder 拒绝；revoke 失败文案改为「已确认 N 条（ACK 失败可能多一条）」；成功文案与叶子名保持脱敏。
2. `Services/SourceImportModels.cs`：`SourceImportCoordinator.LastPlanFailureSource` 记录使预览中止的**那一个** source（Core 侧失败保持 null）。
3. `Services/HostController.cs`：`PinPendingSourceRecovery` 用 `AttributeFailedSource` 只 pin 唯一失败源（无归因 + 多选 = ambiguous → 零 target）；`Diagnose/Reauthorize` 传 targets + ambiguous。
4. `ViewModels/.../ImportDockViewModel.cs`：blocked 诊断显示「请只选择一个来源 / folder 不支持」提示而不给动作；`HasSourceRecoveryHint`；新预览清 `RecoveryOutcomeText`，恢复成功在自动重预览后发布 outcome。
5. `Views/.../ImportDockView.axaml`：恢复区按 `HasSourceRecoveryHint` 显示（含 blocked 说明），按钮仅在有动作时出现。
6. Host/CoreClient/Core/契约/`IHostController` 零字节；红线 R-1 不变。

## 2. 验证证据（实跑；`delivery_head=e9e1132a5`）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **成功 0 warning / 0 error（EXIT 0）** | `logs/build.log` |
| VM/编排级（卡面命令） | `dotnet test .../NewManga.App.Tests -c Release --filter "FullyQualifiedName~SourceRecovery"` | **PASS 43 / 0 / 0** | `logs/app-unit.log` |
| gated 真实 IPC（卡面命令） | `NEWMANGA_FEA11_IPC=1 dotnet test .../NewManga.Host.Tests --filter "FullyQualifiedName~SourceRecoveryIpc"` | **PASS 1 / 0 / 0**；receipt `wire_frame_count=77 wire_path_hits=0 wire_redacted_frames=7` | `logs/host-ipc.log`、`logs/ipc-closed-loop.{json,txt}` |
| 定向 Core 回归 | `python -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 74 passed**（基线 74，不降） | `logs/feature.log` |
| 全量 Python | `python -m pytest tests -q` | **PASS 3317 passed / 10 skipped**（= 基线）；跑后 `git checkout -- verification/FEA-09` → CLEAN | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **PASS 1613 / 0 failed / 93 skipped**（基线 1570/0/92：+43 本卡、+1 新增 opt-in skip） | `logs/full-dotnet.log` |
| 治理 | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** ×2 / **EXIT=0** | `logs/gates-governance.log` |
| 范围 | scope 校验（最终 docs commit 后重算） | **PASS**（全部路径 ALLOWED、forbidden=0、禁止面 11 项 ZERO_DIFF、`CORE_PROTOCOL_MINOR=3`；1 项并发非交付标注） | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\tools\discrimination.ps1` | **5/5 RED_AS_EXPECTED + 5/5 RESTORED（sha256）+ final rebuild EXIT 0** | `logs/discrimination.log` |

### 2.1 Review r1 处置摘要（详见 EV §7）

- **P2-01 FIXED**：恢复面**单源归因**；批量/歧义无动作且在任何 wire 调用前被拒；健康兄弟源零撤销/零注册；folder 拒绝（P3-04）。判别 **B5**。
- **P2-02 FIXED**：wire 日志在存帧前把绝对路径重写为 `[REDACTED]`，原「含路径帧仅 RegisterSourceReadGrant」断言恒空/措辞不实；改为真实断言 **0 命中 + `[REDACTED]` 帧存在**，evidence 字段改 `wire_path_hits` / `wire_redacted_frames` / `wire_frame_count`。
- **P3-01/02/08 FIXED**：数字口径（43 / +43 / 禁止面 11 / Manifest 3 新增 + 6 修改）、scope 快照按最终 docs commit 重算、卡面构建命令路径修正。
- **P3-03/11 登记**：重复恢复累积 revoked 行（active 恒 1 ≠ 无副作用）；revoke ACK 失败计数口径写入 limitation 与文案。
- **P3-04/06/07 FIXED**：folder 分离 + 文案；View 测试只经按钮命令驱动；新预览清 outcome。
- **P3-05 部分修复 + 接受**：生产代码级覆盖 pin 归因；HostController 端到端需可启动 runtime，登记接受。
- **P3-09 FIXED**：判别性日志改为一次干净重跑并标注早期探索性失败。
- **P3-10 FIXED**：gated IPC 夹具在 gate 关闭时不再启动真实 Core。

### 2.2 诚实披露

- **共享工作树**：`main` 同期由 Lead 提交 `ac528828b`（docs-only progress handoff）；本卡 scope 按自有 commit 链计算，禁止面零 diff。
- **真实 IPC 口径**：phase A 的「同路径替换」改变文件物理身份 → Core 写**新的** `source_locations` 行（旧行留只读投影，Host 调度器按撤销 registry fail-closed 丢弃）；**L-S4-A 原地刷新**只在「同物理身份 + 新 registry」成立，故 phase B 用隔离 registry（Passthrough，文件不动）构造等价不变量并实测同一 `location_id` 刷新；**不宣称**替换场景是原地刷新。
- **wire 脱敏事实**：Core wire 日志存帧前把绝对路径重写为 `[REDACTED]`，所以「哪些帧原本带路径」不可观测；本卡只断言可观测事实（0 命中 + 存在 `[REDACTED]` 帧）。
- **NOT_RUN：无**；已知 flaky `FluentResidual2VisualEvidenceTests` 未命中（1613/0 无失败）。
- 隔离根：`G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\`（IPC 夹具、判别性备份、原始日志）；**未写** `verification/FEA-09/**`。

## 3. 已知 limitation（closeout 必须保留）

- **B2（roots 可用性投影）/ B3（扫描侧投影）未做**（B2 需 C-16 v1.5 1 pin）。
- **L-S4-1**（零交互自动恢复枚举）仍开放（需 C-16 v1.5 批量载体）；**L-S4-2**（folder 身份键）未修 → 本卡只承诺 **file-source 同路径恢复**；重定位走「重新导入成新源」。
- **多选/歧义不给恢复**：只针对唯一失败来源；无法唯一归因时不提供动作、不探针、不写注册表，UI 提示单选。
- **folder 源不给恢复**：folder 根进入恢复面被拒绝并说明（file-source only）。
- **重复显式恢复累积 revoked 行**：active 恒 1，但 registry 只置位不删除；每次重复新增 revoked + active 各一条。
- **revoke ACK 失败计数口径**：Host 先持久化再等 ACK；失败时计数为「已确认」条数，实际可能多一条；无回滚。
- **C-17 journal 撤销撕裂（仅登记）**：撤销后绑定旧 `registry_id` 的 C-17 apply/journal 重试永久失败；需 B2/L-S4-B 批量设计；文案不承诺「重试自动恢复」。
- **`quarantine_path` 不展示**：不读、不返回、不渲染（C-16 §7.3 冲突留 UNFREEZE）。
- **真实 `HostController` 恢复接缝无端到端测试**：需可启动 runtime；以生产代码级归因单测 + 真实 IPC 覆盖，登记接受。
- **不宣称**：不写「零交互自愈」「根级问题全解」「自动恢复/撤销后自动放行」；不写「替换场景=原地刷新」；L-R1 未全修；独立 r2 复审由 Lead 指派（本会话不自审）。

## 4. 接收方式

- 分支 `main`，未建 worktree、未 push；`delivery_head=e9e1132a5`（r1 修复 `019feeb6e` + r1 测试 `e9e1132a5`），r1 卡/Handoff/证据为同批文档提交。
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

- **立即下一步**：Lead 指派 **r2 窄面复审**（只读 `e9e1132a5` + `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/**`；重点复看 P2-01 单源归因、P2-02 wire 断言、P3-04 folder 分离；作者会话不自审）。
- **后续候选（非本卡授权）**：B2（`source_list_roots` 可用性投影 + 多根管理面，与 L-S4-B 共用**一个** C-16 v1.5 载体，1/18 pins）；B3（扫描侧投影）；L-S4-2（folder 身份键）；C-17 journal 撤销撕裂的批量处置设计。
- Recovery point：`G:\CODEX\New Manga`，`main`，`e9e1132a5`（证据目录 `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/`）。

## 6. 风险与遗留

- **最高风险已按 r1 加强**：多选时若恢复面再次退化为「对全部选中执行」，会撤销/重注册健康源——判别 B5 + `Reauthorize_RefusesABatchBeforeAnyWireCall` + `AttributedFailure_LeavesTheHealthySiblingCompletelyUntouched` 三重钉住。
- **撤销不可回退**：部分失败只如实展示 + 可重试；不得增加「自动回滚撤销」。
- **命令面/C-07 零扩**：任何新增命令/能力/错误码都会使命令计数守卫与 API inventory 同时变红。
- **重置丢弃全部授权**：只在「探针本身 typed 不可用」时提供，二次确认；文案不得暗示「只影响该来源」。
