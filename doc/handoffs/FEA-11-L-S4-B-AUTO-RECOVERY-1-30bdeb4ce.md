---
task_id: FEA-11-L-S4-B-AUTO-RECOVERY-1
author: l-s4b-impl（DSH Agent Teams 成员；Lead `lead`）
recipient: DeepSeek Harness
base_commit: a7360839d
start_head: c6ca1aa3c
delivery_head: 30bdeb4ce
status: in_review
supersedes_handoff: null
---

# Handoff — FEA-11-L-S4-B-AUTO-RECOVERY-1（L-S4-B：重授权后的零交互恢复）

- Task：`doc/tasks/FEA-11-L-S4-B-AUTO-RECOVERY-1.md`（Owner=`l-s4b-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-07（Asia/Shanghai）
- 交付基线：卡 `base_commit=a7360839d`；**实现起点 `c6ca1aa3c`**（Lead 释放，`main` clean，实测）
- **delivery_head=`30bdeb4ce`**（Core→Host→App→测试→扩域断言 5 个提交；本 Handoff/卡面/证据为随后同批文档提交）
- 权限依据：卡面（`status: ready`，C-16 v1.5 已冻 `a7f57ebd…`）+ scope review `doc/reviews/C16-V15-BATCH-scope-r1.md`（推荐 b3）+ PREREQ r9 approved + DSH 裁决（2026-11-07：scope 扩域 2 个既有测试文件仅 +1 行断言；L-S4-B-1 扫描执行面 limitation 登记）
- 环境：Windows 11 / PowerShell 7 / CPython 3.14.6 / .NET SDK 10.0.401（测试目标 net9.0）；零新依赖、零 schema/迁移、零契约字节

## 1. 交付结果（AC-LS4B-1…10 全 MET；卡面已勾选 + `<<MET>>`，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| **AC-LS4B-1 能力门禁/四象限** | MET | Core `core.ping` 增 `source.reattest/1`（仅此一个，无第二能力）；Host 只用 ping 探测并缓存，缺失/探测异常 → **不 mint、不发送、不建文件**，目标保持既有 typed skip；legacy 构造器 = 旧行为 |
| **AC-LS4B-2 Host 候选精确性** | MET | `SourceRootReattestPlanner` 纯函数：旧条目 revoked + 恰 1 根、live 唯一 + 恰 1 根、路径 normalize 相等、volume/file 相等、`live.CreatedAt > old.RevokedAt`、kind 非 folder → 候选；13 类负例全部 typed skip、零 wire |
| **AC-LS4B-3 Core 身份门禁与零写** | MET | closed shape 恰 2 键（host-control + 模块双层）；grant 缺失/过期/撤销按 §6 优先级；scope.source_id / 四键身份 / 无 current location / folder → typed 拒绝，逐例 16 表快照零写 |
| **AC-LS4B-4 单行写/幂等/单调** | MET | 只改 `registry_id/authorization_generation`；`last_verified_at` 原值逐字节回写（不取 now）；location 行数/其余列/`page_bindings` 不变；重复 `updated:0` + 字节不变；同 registry 代次回退 0 行、跨 registry 允许 1；全 `src/**` 唯一 `UPDATE source_locations SET registry_id`（grep 判别） |
| **AC-LS4B-5 无授权/无 identity 重建/不扩面** | MET | 不创建/复活 grant；Host Registry 条目不新增/撤销/改 roots/identity/generation（仅既有 mint `last_used_at`）；无新 source/version/entry；无新错误码/wire minor/schema/依赖；无新 UI→Host 命令（C-07 registry 111 不变）；folder 拒绝 |
| **AC-LS4B-6 触发与恢复** | MET（**仅枚举恢复**） | gated 真 IPC：phase A B1-only → 0 targets/skip 1；phase B → 恰 1 帧 `ReattestSourceLocation`（ids-only、无路径）→ Core 行两 auth 列更新 → 重枚举返回 live pair → target 入集；其它表/审计列/Host Registry 不变；零重导入/零 apply；App 成功分支请求既有 refresh 恰 1 次、失败 0 次 |
| **AC-LS4B-7 零漂移/门禁** | MET | pins **18/18**；check（默认 + `-TaskPath`）**PASS(3 warnings)**；API inventory EXIT=0；scope PASS（diff ⊆ allowed_paths、zero-drift=[]、`PROTOCOL_MINOR=3`、C16 pin 命中）；全量 pytest **3360/10**（基线 3317/10）、全量 .NET **1644/0/94**（基线 1617/0/93）；跑后 `verification/FEA-09` 已恢复 CLEAN |
| **AC-LS4B-8 不夸大** | MET | 只承诺「B1 显式重授权后无需重导入/apply，**枚举**恢复」；folder/B2/L-S4-1/L-S4-2/L-R1/扫描执行面（L-S4-B-1）均保留并明确不宣称修复；`source_reset_registry` 后无旧条目可桥接 |
| **AC-LS4B-9 每轮至多一次 reattest** | MET | 每轮按 source_id 去重、每候选恰 1 次发送；失败 typed 即止不重试；单测（同一 source 两条 target → 恰 1 次尝试、无第二轮重读）+ gated IPC 恰 1 帧 |
| **AC-LS4B-10 措辞红线** | MET | 卡/EV/Handoff 无「自动恢复/自愈/自动重新授权」；App 成功文案保持「已重新授权…请重新预览」，判别用例断言 VM 文案与 toast 均不含红线词；reattest 语义明确为「事实传播，不是授权/恢复动作」 |

## 2. 验证证据（实跑；`delivery_head=30bdeb4ce`）

| 场景 | 命令 | 环境与被测 commit | 结果 | 日志 |
|---|---|---|---|---|
| Core 定向 | `C:/Python314/python.exe -m pytest tests/core/test_host_control.py tests/fea11/test_source_reattest.py tests/core/test_core_scan_target_commands.py -q` | delivery tree | **PASS 100 passed in 8.27s** | `logs/feature.log` |
| 回归（host_control+run_grant） | `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | delivery tree | **PASS 89 passed in 8.05s**（基线命名 74 的实跑计数 89，无失败） | `logs/regression-74.log` |
| Host 单测 | `dotnet test tests/NewManga.Host.Tests/… --filter "FullyQualifiedName~SourceReattest"` | delivery tree | **PASS 24/0/0** | `logs/host-unit.log` |
| App 单测 | `dotnet test tests/NewManga.App.Tests/… --filter "FullyQualifiedName~SourceRecoveryUiTests"` | delivery tree | **PASS 18/0/0** | `logs/app-unit.log` |
| gated 真 IPC | `NEWMANGA_FEA11_IPC=1 dotnet test … --filter "FullyQualifiedName~Fea11ScanIpc"` | real volatile Python Core | **PASS 4/0/0**（含新闭环） | `logs/host-ipc.log` |
| 全量 Python | `C:/Python314/python.exe -m pytest tests -q` | HEAD `30bdeb4ce` | **PASS 3360 passed / 10 skipped / 251.59s**（基线 3317/10；+43 为本卡新增） | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test NewManga.sln -c Release`（cwd `apps/desktop-avalonia`） | 代码树同 delivery_head（之后仅 Python 断言扩域提交） | **PASS 1644 / 0 / 94**（基线 1617/0/93；+27/+1 归本卡 + gated skip） | `logs/full-dotnet.log` |
| 治理 | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | delivery tree | **PIN PASS 18/18** / **PASS(3 warnings)×2** / **EXIT=0** | `logs/gates.log` |
| scope | `python verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/tools/scope_validation.py` | delivery diff vs `c6ca1aa3c` | **PASS**（全 ALLOWED；zero-drift=[]；minor=3；C16 pin match；registry 无新命令） | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `python verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/tools/discrimination.py` | delivery tree | **PASS 11/11 RED_AS_EXPECTED + 逐例 sha256 复原 + 复绿** | `logs/discrimination.log` |

- **跑后恢复**：全量 .NET 重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson` → 已 `git checkout -- verification/FEA-09`（`git status -- verification/FEA-09` 为空）。
- **并发披露**：共享 `main` 同期由 Lead 提交 PREREQ r8/r9 close-out + progress handoff（`8c0d2d8af`/`5f64ba972`/`d354a1390`/`5a02214a5`）与 scope 扩域卡面（`4e9ab8d90`），均 docs-only，`git diff c6ca1aa3c..HEAD -- src apps tests` 中非本卡部分为空；本卡提交均显式 pathspec，未夹带他人字节。

## 3. 扩域清单（DSH 2026-11-07 批准；仅断言预期，零行为改动）

| 文件 | 改动 | 原因 |
|---|---|---|
| `tests/core/test_core_service.py` | 2 处精确 capability 列表 +1 行 `"source.reattest/1",` | C-16 v1.5 §0 新能力使既有精确断言失败（v1.3 `source.read.run/1` 同先例） |
| `tests/fea09/test_referenced_wire.py` | 1 处精确 capability 列表 +1 行 `"source.reattest/1",` | 同上 |
| `.NET` 侧 | **未使用**（全量 .NET 无精确 capability 列表断言；已有断言均为 `Contains`） | 预批未消耗 |

## 4. 已知 limitation（closeout 必须保留）

- **L-S4-B-1（DSH 裁决登记）**：reattest 后**枚举恢复**成立；该 target 的**扫描执行面**仍被既有
  `ResolveRegistryEntry`「同路径 revoked 旧条目 fail-closed」拦住（`Revoke` 累积旧条目 → 路径精确匹配先命中
  revoked → null → tick typed `SOURCE_ACCESS_DENIED`）。本卡只承诺枚举恢复（冻结 AC-LS4B-6 原文），
  **不得**写「扫描恢复/扫描成功」；gated IPC 证据 `tick_verdict.last_result` 如实记录。后续另卡（与 B2/roots 管理一起设计）。
- **B2 `roots_available`**：字段已冻结，**实现延后**（无消费者）。
- **folder（L-S4-2）**：身份键口径未修；reattest 双侧排除 folder。
- **`source_reset_registry` 后**：无 revoked 旧条目可反查 → 不能 reattest，仍需重导入。
- **不自动重新授权/不重建 identity/撤销后不放行**；**L-S4-1/L-R1 未全修**；多根 first-root 启发式未修。
- **revoked 行累积**是既有 B1 行为（L-S4-B-1 根因之一）。

## 5. 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`；实现起点 `c6ca1aa3c`；**delivery_head=`30bdeb4ce`**（未 push、未建 worktree）。
- 复现（repo root）：见 `verification/FEA-11-L-S4-B-AUTO-RECOVERY-1/EV.md` §6（含全量/定向/gated/判别性/scope/manifest 命令）。
- 接收者下一步：①Lead 指派**独立上下文** Review（只读 `30bdeb4ce`；重点：C-16 v1.5 §2.5 校验顺序与两列写/last_verified_at 原值、Host 候选矩阵、能力门禁、gated IPC 闭环、11/11 判别性、扩域仅 2 文件 3 行、L-S4-B-1 措辞）；②核对 `EV.md`/`RESOURCE-MANIFEST.json` 逐文件 sha256；③Lead 集成门禁重跑与 closeout（本 Handoff 不改卡 `status`；卡面 `delivery_head` 已回填，若 Lead 口径不同可回退）。

## 6. 下一任务建议

- 本卡 Review/集成前不释放后续实现。
- Review 通过后建议队列（由 DSH 裁决）：**L-S4-B-1 扫描执行面**（与 B2 `roots_available`/roots 管理一起设计；
  修订 `ResolveRegistryEntry` 的 revoked-exact-match 与 live exact-match 优先级，需 C-17 §5.3 语义裁决）；
  或 **L-S4-2 folder 身份键**、**RUN-GRANT-2C**（长 Run 授权续期）。均需先 scope/设计 review 再冻结。
- **Recovery point**：`G:\CODEX\New Manga` / `main` / `30bdeb4ce`（未创建 worktree，若需隔离 worktree 待 DSH 创建）。

## 7. 风险与遗留

- **R1（已登记）**：扫描执行面 typed error 可能被读成「恢复失败」；口径固定为「枚举恢复，不是扫描恢复」（L-S4-B-1）。
- **R2 口径风险**：reattest 使枚举由 skip 变通过，产品上接近「恢复」；本卡口径锚定「用户显式动作之后的事实传播」，
  不代表撤销后自动放行或自动重新授权。
- **R3 双哈希成本**：恢复目标会「reattest grant 哈希 + 随后 scan grant 哈希」各一次（一次性成本；未为省哈希放宽身份校验）。
- **R4 并发共享工作树**：证据已按 `delivery_head` 与 `repo_head` 归因；Lead 集成若 HEAD 前进需按其 head 重跑门禁。
- **回退**：`git revert 30bdeb4ce c4345a632 f76620e39 3ccb0509e ec171f0d3`（5 个提交，或按文件 checkout）；
  无 schema/数据迁移，回退无数据风险（Core DB 仅新增条件 UPDATE 行为，不改变既有行结构）。
