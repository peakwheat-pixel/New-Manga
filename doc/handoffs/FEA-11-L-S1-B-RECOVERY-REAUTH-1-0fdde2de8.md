---
task_id: FEA-11-L-S1-B-RECOVERY-REAUTH-1
author: l-s1b-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 3d97e3b18
start_head: e0b37622b
delivery_head: 0fdde2de8953ffcfd847471fdf8c6d82bf507257
status: in_review
supersedes_handoff: null
---

# Handoff — FEA-11-L-S1-B-RECOVERY-REAUTH-1（B1：App 显式恢复/重授权入口；App-only、零契约、0/18 pins）

- Task：`doc/tasks/FEA-11-L-S1-B-RECOVERY-REAUTH-1.md`（Owner=`l-s1b-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-07（Asia/Shanghai）
- 交付基线：卡 `base_commit=3d97e3b18`；实现起点 `e0b37622b`（工作树 clean，实测）；**`delivery_head=0fdde2de8953ffcfd847471fdf8c6d82bf507257`**
- 交付 commit：`be3b0c242`（实现）、`0fdde2de8`（测试，**delivery_head**）；卡/本 Handoff/证据为同批文档提交（未 push、未建 worktree）
- 环境：Windows 11 / PowerShell 7.6.8 / CPython 3.14.6 / .NET（net9.0）；零新依赖、零 schema/migration/wire/契约改动
- 依据：卡 D-1…D-10 + 权威 scope review `doc/reviews/FEA-11-L-S1-B-RECOVERY-REAUTH-1-scope-r1.md`（READY-TO-FREEZE，App-only）+ 依赖卡 `FEA-11-L-S1-REGISTRY-RESILIENCE-1`/`FEA-11-L-S4-LOCATION-AUTH-REFRESH-1`（均 done）

## 1. 交付结果（AC-LSB-1…10 全 MET；卡面已勾选，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| AC-LSB-1 入口仅显式 | **MET** | 失败分支只做 1 次**只读**探针；VM 端口计数 `reauthorize=0/reset=0/resetConfirm=[]`；真实 IPC `registry_unchanged_after_failure=true`；判别 B1（挂进失败分支 → RED） |
| AC-LSB-2 分流正确 | **MET** | 探针 UNAVAILABLE → 只给重置；探针成功 + mint 失败 → 只给重授权；其它码（实跑 `CORE_CAPABILITY_MISSING`/`SOURCE_REGISTRY_BUSY`）→ 无动作且**显示该码**；Core 侧 UNAVAILABLE/preview 其它码 → **不探针**、无动作 |
| AC-LSB-3 顺序与幂等 | **MET** | 2 条 stale 全撤销（generation+1/`revoked_at`）后只注册 1 条；帧序 `list→revoke×2→register`；重复执行恒 1 active；注册用条目**已登记** `roots[0]`（大小写不同也原样）；判别 B2/B3 |
| AC-LSB-4 部分失败 fail-closed | **MET** | 撤销成功/注册失败 → `RevokedButNotRegistered` + 「已撤销…未重新授权（typed 码）」；无回滚、不显示成功；可重试（撤销完成后的 retry 直接补注册 leg）；撤销失败 → 中止且**零注册** |
| AC-LSB-5 不自动重授权（安全核心） | **MET** | 计划/mint 路径零恢复命令（源码守卫：`SourceImportModels.cs` 仅 1×list+1×register、0 revoke/reset）；复用选择器抽出为纯函数、语义逐字不变（首个非 revoked 匹配）；无 stale 条目时**拒绝而非盲注册**；只读 Host 零写入；判别 B1 |
| AC-LSB-6 授权面不扩大 | **MET** | 恢复成员参数仅 `bool`/`CancellationToken`（无任何路径/ID）；只加在 `ISourceImportController`，`IHostController` 无成员；`HostCommandRegistry.All.Count == 111` 冻结（无 recover/reauthor 命令）；API inventory EXIT=0 |
| AC-LSB-7 脱敏 | **MET** | 恢复文案/通知只含叶子名/typed 码/计数；VM 全文本 `C:\manga` 与 `quarantine` 0 命中；脚本 Host 响应**故意带** `quarantine_path` 也不得泄漏；真实 IPC：wire `quarantine` 0、含路径帧仅既有 `RegisterSourceReadGrant`、stderr 0 命中；判别 B4 |
| AC-LSB-8 零漂移/门禁 | **MET** | build 0/0；定向 34/0/0；gated IPC 1/0/0；定向 pytest 74；全量 pytest 3317/10（=基线）；全量 .NET 1604/0/93（基线 1570/0/92：+33、+1 skip）；pins 18/18；check PASS(3w)×2；API EXIT=0；scope PASS（禁止面 10 项 ZERO_DIFF、`CORE_PROTOCOL_MINOR=3`）；FEA-09 CLEAN |
| AC-LSB-9 闭环证据（gated 真实 IPC 1 条） | **MET** | `logs/ipc-closed-loop.{json,txt}`：phase A 真实同路径替换 → typed 失败 → 显式重授权 → 再预览成功 → 重新导入 Completed → `source_list_scan_targets` 新 registry/gen；phase B 同物理身份 + 新 registry → **L-S4-A 原地刷新**（同 `location_id`、registry 换新、`last_verified_at` 非空、枚举 gen=1） |
| AC-LSB-10 边界/不夸大 | **MET** | 只承诺 file-source 同路径恢复；L-S4-1/L-S4-2/B2/B3 保留；C-17 journal 撤销撕裂仅登记；未出现「零交互自愈/根级问题全解/自动恢复」 |

### 1.1 实现要点（4 生产文件 + 1 新文件 + 视图）

1. `Services/SourceRecoveryModels.cs`（**新增**）：`SourceRecoveryAction`/`SourceRecoveryDiagnosis`/`SourceRecoveryResult`/`SourceRecoveryText`/`SourceRecoveryPayloads` + `SourceRecoveryCoordinator`（诊断分流、撤销全部→注册一次、部分失败 fail-closed、重置二次确认语义、路径只用于 App 内存匹配与叶子名、**`quarantine_path` 从不读取**）。
2. `Services/SourceImportModels.cs`：`ISourceImportController` 增 3 个恢复成员（无路径入参；XML 注释写清红线）；`FindOrRegisterRootAsync` 的选择器抽出为 `internal static SelectReusableRoot`（**语义逐字不变**，仅便于判别测试）；`IsTypedFailure`/`TypedCode` 提升为 `internal static` 供恢复面复用（未改行为）。
3. `Services/HostController.cs`：实现 3 成员（复用 `HostCommandDispatcher` → Host 既有 C-16 v1.4 root 命令；`Policy.WritesAllowed` 写门、typed 结果、失败时只 pin「App 自己选过的 sources + 失败码 + 是否 Host 侧 mint」）；`NullHostController.cs` 编译义务 + typed not-ready。
4. `ViewModels/V2/Library/ImportDockViewModel.cs` + `Views/V2/Library/ImportDockView.axaml`：预览失败后**只读诊断**→ 只显示**唯一分支动作**；「重新授权此来源」（一次确认，成功后同一动作重跑预览）与「重置源授权存储」（**二次确认** + 全量丢弃披露）；失败/部分失败文案 fail-closed；面板关闭清空恢复态；无路径展示。
5. 红线 R-1/R-2/R-3 保持：`SourceAccessRegistry`/Host/Core/契约/`IHostController` **零字节**；错误分支零恢复调用；撤销后不自动放行、不自动重建 identity。

## 2. 验证证据（实跑；`delivery_head=0fdde2de8`）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **成功 0 warning / 0 error（EXIT 0）** | `logs/build.log` |
| VM/编排级（卡面命令） | `dotnet test .../NewManga.App.Tests -c Release --filter "FullyQualifiedName~SourceRecovery"` | **PASS 34 / 0 / 0** | `logs/app-unit.log` |
| gated 真实 IPC（卡面命令） | `NEWMANGA_FEA11_IPC=1 dotnet test .../NewManga.Host.Tests --filter "FullyQualifiedName~SourceRecoveryIpc"` | **PASS 1 / 0 / 0**；隔离 receipt `logs/ipc-closed-loop.{json,txt}` | `logs/host-ipc.log` |
| 定向 Core 回归 | `python -m pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 74 passed**（基线 74，不降） | `logs/feature.log` |
| 全量 Python | `python -m pytest tests -q` | **PASS 3317 passed / 10 skipped**（= 基线）；跑后 `git checkout -- verification/FEA-09` → CLEAN | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test apps/desktop-avalonia/NewManga.sln -c Release` | **PASS 1604 / 0 failed / 93 skipped**（基线 1570/0/92：+34 本卡、+1 新增 opt-in skip） | `logs/full-dotnet.log` |
| 治理 | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **18/18 PASS** / **PASS(3 warnings)** ×2 / **EXIT=0** | `logs/gates-governance.log` |
| 范围 | scope 校验 | **PASS**（changed=12 全 ALLOWED、forbidden=0、禁止面 11 项 ZERO_DIFF；1 项并发非交付（ac528828b）显式标注、`CORE_PROTOCOL_MINOR=3`） | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\tools\discrimination.ps1` | **4/4 RED_AS_EXPECTED + 4/4 RESTORED（sha256）+ final rebuild EXIT 0** | `logs/discrimination.log` |

- **判别性 4 破坏点**：B1 把恢复挂进预览失败分支（自动重授权，AC-LSB-1/5）；B2 只撤首条 stale（AC-LSB-3）；B3 先注册后撤销（AC-LSB-3）；B4 读取/渲染响应 `quarantine_path`（AC-LSB-7）。每个破坏点只跑**一个**目标用例并变红，随后按原字节恢复（sha256 一致）再重建。
- **共享工作树披露（诚实记录）**：同一 `main` 工作树同期由 Lead 提交 `ac528828b`（`doc/handoffs/DSH-PROGRESS-2026-11-07.md`，docs-only）。本卡实现/测试 commit 全部落在其之后，scope 按本卡自有 commit 链（`be3b0c242`/`0fdde2de8`）计算，**未修改/暂存/提交**任何非本卡字节。
- **真实 IPC 的如实口径**：phase A 的「同路径替换」改变文件物理身份 → Core 侧必然写**新的** `source_locations` 行（旧行留在只读投影，Host 调度器按撤销 registry fail-closed 丢弃）；**L-S4-A 的原地刷新**只在「同物理身份 + 新 registry」成立，故 phase B 用隔离 registry（Passthrough protector，文件不动）构造「登记身份不再匹配」这一等价不变量并实测**同一 `location_id`** 刷新。两条都在 EV/Handoff/IPC 证据里明示，**不宣称**替换场景是原地刷新。
- **未运行/不可判定（NOT_RUN）**：无。卡面要求的构建/定向/gated IPC/回归 + 全量 均实跑；未把任何未跑项写成 PASS。
- 已知 flaky `FluentResidual2VisualEvidenceTests`（git-status 快照竞态）本次**未命中**（全量 1604/0），未重跑凑绿。
- 隔离根：`G:\CODEX\New Manga.workspace\FEA-11-L-S1-B-RECOVERY-REAUTH-1\`（IPC 夹具 `fixtures/ipc-*`、判别性备份 `tmp/discrimination/`、原始日志）；**未写** `verification/FEA-09/**`。

## 3. 已知 limitation（closeout 必须保留）

- **B2（roots 可用性投影）/ B3（扫描侧投影）未做**：多根健康与逐条管理不可见、扫描状态不可见（B2 需 C-16 v1.5 1 pin）。
- **L-S4-1**（零交互自动恢复枚举）仍开放（需 C-16 v1.5 批量载体）；**L-S4-2**（folder 身份键）未修 → 本卡只承诺 **file-source 同路径恢复**；重定位（换路径）走「重新导入成新源」。
- **C-17 journal 撤销撕裂（仅登记，不处理）**：撤销后，绑定旧 `registry_id` 的 C-17 apply/journal 重试会永久失败（`HostOperationOrchestrator.cs:112-133`；scope review `:87/:249/:263`）；需 B2/L-S4-B 批量设计，文案不承诺「重试自动恢复」。
- **`quarantine_path` 不展示**：`source_reset_registry` 响应带绝对路径，与 C-16 §7.3 冲突；本卡**不读、不返回、不渲染**，契约澄清留 UNFREEZE。
- **folder 变体/多根条目**：恢复只处理**单根**条目（导入面只登记单根）；多根条目的重授权不在本卡。
- **不宣称**：不写「零交互自愈」「根级问题全解」「自动恢复/撤销后自动放行」；不写「替换场景=原地刷新」；L-R1 未全修；独立 Review 由 Lead 指派（本会话不自审）。

## 4. 接收方式

- 分支 `main`，未建 worktree、未 push；`delivery_head=0fdde2de8`（实现 `be3b0c242` + 测试 `0fdde2de8`），卡/Handoff/证据为同批文档提交。
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
- 前置：Windows 交互用户（IPC 主路径用默认 `C:/Python314/python.exe` 或 `NEWMANGA_BUILD_PYTHON`）；判别性脚本会临时改写并**按原字节恢复** `ImportDockViewModel.cs`/`SourceRecoveryModels.cs`（不要在并发实施同一文件时运行）。

## 5. 下一任务建议（供 DSH 裁决；本 Handoff 不授权）

- **立即下一步**：Lead 指派**独立上下文** Review（只读 `0fdde2de8` + `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/**`；作者会话不自审）。
- **后续候选（非本卡授权）**：B2（`source_list_roots` 可用性投影 + 多根管理面，与 L-S4-B 共用**一个** C-16 v1.5 载体，1/18 pins）；B3（扫描侧投影）；L-S4-2（folder 身份键）；C-17 journal 撤销撕裂的批量处置设计。
- Recovery point：`G:\CODEX\New Manga`，`main`，`0fdde2de8`（证据目录 `verification/FEA-11-L-S1-B-RECOVERY-REAUTH-1/`）。

## 6. 风险与遗留

- **最高风险已按卡处置**：把「mint 失败就重注册」当修法是**自动重新授权**；本卡把该捷径写成判别点（B1 判别 + 源码守卫 + 选择器纯函数测试），任何把恢复接进失败分支或给选择器加回退的改动都必须重新跑判别性。
- 撤销是**不可回退的持久事实**：部分失败只能如实展示 + 可重试；不得增加「自动回滚撤销」的实现（AC-LSB-4 判别已钉住消息与行为）。
- `HostCommandRegistry` 命令面与 C-07 inventory 都是零扩：任何新增命令/能力/错误码都会使 `RecoverySurface_AddsNoWireCommand_AndKeepsTheFrozenCommandCount` 与 API inventory 同时变红。
- 重置会丢弃**全部**来源授权：只在「探针本身 typed 不可用」时提供，且必须二次确认；文案不得暗示「只影响该来源」。
