---
task_id: FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1
author: l-s4b1-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: 58395b9a2
start_head: 16082d3a9
delivery_head: bcc88e4a2
status: in_review
supersedes_handoff: null
---

# Handoff — FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1（扫描执行面恢复）

- Task：`doc/tasks/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1.md`（Owner=`l-s4b1-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-07（Asia/Shanghai）
- 交付基线：卡 `base_commit=58395b9a2`；**实现起点 `16082d3a9`**（Lead 释放提交，`main` clean，实测）
- **delivery_head=`bcc88e4a2`**（实现 `8709d6159` + 测试/ gated IPC `bcc88e4a2`；随后同批 docs/evidence 提交）
- 权限依据：卡面（`status: ready`，Host-only，零契约 0/18 pins）+ 权威 scope review
  `doc/reviews/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1-scope-r1.md`（READY-TO-FREEZE；推荐形状 = 枚举 target 使用自身已核验 live `(registry_id, generation)`，不改 `ResolveRegistryEntry` 非枚举语义）
  + ZCode 故障转移裁决（READY-TO-FREEZE，无翻案项；TOCTOU/backoff/scope 三点提示已采纳）
- 环境：Windows 11 / PowerShell 7 / CPython 3.14.6 / .NET SDK 10.0.401（测试目标 net9.0）；零新依赖、零 schema/迁移、零契约字节、零 Core/Python 改动

## 1. 交付结果（AC-SER-1…6 全 MET；卡面已勾选 + `<<MET>>`，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| **AC-SER-1 枚举执行面恢复（主 AC）** | MET | `VerifyEnumeratedTarget(target, out entry)` 复用**同一次** registry 快照的 live 条目；`ScanAsync` 枚举分支用它铸 grant，不再二次按路径解析。单测证明同快照下 path 解析返回 null 而 target 自身 live 条目被选中；gated 真 IPC 由 `error` → **`ok` + 恰 1 帧 `ScanSourceSync`**（`scan_frames=1`、`path_hits=0`） |
| **AC-SER-2 fail-closed 矩阵不变** | MET | target 自身 registry 缺失/撤销/代次漂移 → 既有 `Skipped(SOURCE_REGISTRY_UNAVAILABLE / SOURCE_GRANT_REVOKED / SOURCE_REGISTRY_BUSY)`；root 缺失/替换 → `Error(SOURCE_REGISTRY_UNAVAILABLE)`；整库不可读 → 既有 typed；全部零 grant/零 frame；既有 4 条 executor 负例原样通过 |
| **AC-SER-3 非枚举语义零变化** | MET | `ResolveRegistryEntry` 实现字节未改（仅注释）；既有 `RegistryResolution_PrefersExactMatch_AndFailsClosedOnRevokedExactEntry` 原样通过；新增非枚举 executor 层用例 |
| **AC-SER-4 无自动授权/无 identity 重建/不写 registry 结构** | MET | 不调用 `Register`/`Revoke`/`Reset`，不写 roots/identity/generation；单测与 gated IPC 均断言扫描前后 `DescribeRegistryEntries`（不含既有 `last_used_at`）结构全等、旧 revoked 行保留 |
| **AC-SER-5 零漂移/门禁** | MET | pins **18/18**（C16 `a7f57ebd…`、C17 `aefa0fa5…`）；C-16/C-17 git blob 与实现起点逐 blob 相同；`PROTOCOL_MINOR=3`；check（默认 + `-TaskPath`）PASS(3 warnings)；API inventory EXIT=0（61 不变）；scope PASS（全 ALLOWED、禁止面零 diff）；全量 pytest **3360/10**（起点同值）、全量 .NET **1652/0/94**（起点 1644/0/94，+8 本卡）；跑后 `verification/FEA-09` CLEAN |
| **AC-SER-6 不夸大** | MET | 只承诺**枚举 target 的扫描执行恢复**（B1 显式动作 → 既有 refresh → 枚举 → 下一个未被 backoff 抑制的 tick）；不承诺 Run 面/自动恢复/自愈/自动重新授权/folder/B2/L-S4-1/L-R1 |

## 2. 验证证据（实跑；`delivery_head=bcc88e4a2`）

| 场景 | 命令 | 环境与被测 commit | 结果 | 日志 |
|---|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | delivery tree | **PASS 0 warning / 0 error** | `logs/build.log` |
| Host 单测（新） | `--filter "FullyQualifiedName~SourceScanExecutionRecovery"` | delivery tree | **PASS 8/0/0** | `logs/host-unit.log` |
| 回归 | `--filter "SourceRegistry\|SourceReattest\|SourceScanSchedulerTests"` | delivery tree | **PASS 123/0/1 skip**（skip = 既有另一 gated 用例，需其独立环境变量） | `logs/regression.log` |
| gated 真 IPC | `NEWMANGA_FEA11_IPC=1 … --filter "FullyQualifiedName~Fea11ScanIpc"` | real volatile Python Core + 真 zip | **PASS 4/0/0**（含 B1→reattest→枚举→tick **ok** 闭环） | `logs/host-ipc.log`、`logs/ipc-closed-loop.json/.txt` |
| 定向 pytest | `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | delivery tree | **PASS 89 passed**（卡面命名「74」的实跑计数；零 Python 改动） | `logs/regression-74.log` |
| 全量 Python | `pytest tests -q` | HEAD 实现树 | **PASS 3360 passed / 10 skipped / 257.51s**（起点同值） | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test NewManga.sln -c Release`（cwd `apps/desktop-avalonia`） | HEAD 实现树 | **PASS 1652 / 0 / 94**（起点 1644/0/94；+8 本卡） | `logs/full-dotnet.log` |
| 治理 | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | delivery tree | **PIN PASS 18/18** / **PASS(3 warnings)×2** / **EXIT=0** | `logs/gates.log` |
| scope | `python …/tools/scope_validation.py` | delivery diff vs `16082d3a9` | **PASS**（全 ALLOWED；zero-drift=[]；minor=3；C16/C17 blob 零漂移；卡 status 未改） | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `python …/tools/discrimination.py` | delivery tree | **PASS 6/6 RED_AS_EXPECTED + 逐例 sha256 复原 + 复绿** | `logs/discrimination.log` |

- **before / after**：before = L-S4-B 交付时同一 gated 闭环证据 `verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/logs/ipc-closed-loop.json`（`last_result="error"`）；after = 本卡 `logs/ipc-closed-loop.json`（`last_result="ok"`、`scan_frames=1`）。
- **跑后恢复**：全量 .NET 重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson` → 已 `git checkout -- verification/FEA-09`。
- **并发披露**：共享 `main` 同期仅 Lead 的 docs 提交（`16082d3a9` 释放实现起点；`58395b9a2..16082d3a9` 实测 docs-only）；本卡提交均显式 pathspec；`git diff 16082d3a9..HEAD -- src tests` 为空。

## 3. 已知 limitation（closeout 必须保留）

- **Run 面不在本卡（S-4）**：`HostRuntime.RunSourceRange.Resolve`（`HostRuntime.cs:1785` 一带）仍按路径解析；「同路径 revoked 旧条目」对 Run 预授权/冷源 on-demand scan 的影响**未测未修**。若复现另卡（`L-S4-B-2-RUN-RANGE-RESOLVE`）。
- **B2 `roots_available`**：字段已冻结，实现延后（无消费者）。
- **folder（L-S4-2）**、**L-S4-1**、**L-R1**、多根 first-root 启发式：未修/保留。
- **backoff 口径**：只承诺「下一个未被既有 backoff 抑制的 tick」；同会话此前已 error 的 scheduler 可能被既有 backoff 延迟。
- **revoked 行累积**：B1 既有行为；本卡只读、不删除/不改写。
- 非枚举 target 的 `ResolveRegistryEntry` 语义不变（C-17 §5.3 零改动）。

## 4. 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`；实现起点 `16082d3a9`；**delivery_head=`bcc88e4a2`**（未 push、未建 worktree）。
- 复现（repo root）：见 `verification/FEA-11-L-S4-B-1-SCAN-EXEC-RECOVERY-1/EV.md` §7（构建/定向/gated/全量/治理/scope/判别性命令）。
- 接收者下一步：①Lead 指派**独立上下文** Review（只读 `bcc88e4a2`；重点：`VerifyEnumeratedTarget` out 参数是否确为同一快照、非枚举语义零变化、fail-closed 矩阵逐项、gated tick before/after、registry 结构不变、6/6 判别性、零契约/零 Python diff、措辞不夸大）；②Lead 复跑 gated before/after；③Lead 集成门禁与 closeout（本 Handoff 不改卡 `status`；卡面 `delivery_head` 已回填）。

## 5. 下一任务建议

- 本卡 Review/集成前不释放后续实现。
- Review 通过后建议队列（由 DSH 裁决）：**`L-S4-B-2-RUN-RANGE-RESOLVE`**（Run 源范围同一根因；`HostRuntime.cs`，若复现需另冻结允许该文件）；或 **B2 `roots_available`**（无消费者，延后）、**L-S4-2 folder 身份键**、**RUN-GRANT-2C**（长 Run 授权续期）。均需先 scope/设计 review 再冻结。
- **Recovery point**：`G:\CODEX\New Manga` / `main` / `bcc88e4a2`（未创建 worktree，若需隔离 worktree 待 DSH 创建）。

## 6. 风险与遗留

- **R1 口径风险**：「执行面恢复」易被读成「自动恢复/自愈/撤销后自动放行」；本卡口径固定为「B1 显式重授权 → 既有 refresh/reattest → 枚举 → 下一个未被 backoff 抑制的 tick」，且 Run 面明确未含。
- **R2 依赖用户显式动作**：无 B1 显式重授权即无新 live 条目 → 仍 typed skip；不自动重新授权。
- **R3 fixture 噪声**：gated IPC 沿用既有 workspace fixture 根（无 tracked 副作用）；证据 JSON 已复制入 `logs/ipc-closed-loop.json` 并记录来源 hash（`logs/ipc-fixture.txt`）。
- **R4 并发共享工作树**：证据按 `delivery_head` 归因；Lead 集成若 HEAD 前进需按其 head 重跑门禁。
- **回退**：`git revert bcc88e4a2 8709d6159`（2 个实现/测试提交）；无 schema/数据迁移、无 Core 写行为变化，回退无数据风险。
