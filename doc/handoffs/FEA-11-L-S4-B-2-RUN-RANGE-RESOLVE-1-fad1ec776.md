---
task_id: FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1
author: l-s4b1-impl（DSH Agent Teams 成员；Lead `lead`；卡 owner 已由 Lead 对齐）
recipient: DeepSeek Harness
base_commit: 2ef3f1024
start_head: e78c144bb
delivery_head: fad1ec776
status: in_review
supersedes_handoff: null
---

# Handoff — FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1（Run 源范围解析恢复）

- Task：`doc/tasks/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1.md`（Owner=`l-s4b1-impl`，Lead=`lead`；卡面 `status` 由 Lead 维护，本 Handoff 不改）
- 交付日期：2026-11-07（Asia/Shanghai）
- 交付基线：卡 `base_commit=2ef3f1024`；**实现起点 `e78c144bb`**（Lead 释放提交，`main` clean；其后 Lead docs-only `7be65026e` owner 对齐先于本卡实现提交）
- **delivery_head=`fad1ec776`**（实现 `f6b5a761a` + 测试/ gated IPC `fad1ec776`；随后同批 docs/evidence 提交）
- 权限依据：卡面（`status: ready`，Host-only，零契约 0/18 pins）+ 权威 scope review
  `doc/reviews/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1-scope-r1.md`（READY-TO-FREEZE；推荐形状 = 枚举 Run target 复用 L-S4-B-1 的 `SelectEnumeratedEntry`，非枚举保持 `ResolveRegistryEntry`）+ Lead 派发指令 R-1…R-7
- 环境：Windows 11 / PowerShell 7 / CPython 3.14.6 / .NET SDK 10.0.401（测试目标 net9.0）；零新依赖、零 schema/迁移、零契约字节、零 Core/Python 改动；`SourceScanScheduler.cs` 零字节

## 1. 交付结果（AC-RUN-1…8 全 MET；卡面已勾选 + `<<MET>>`，`status` 未改）

| AC | 结果 | 关键证据 |
|---|---|---|
| **AC-RUN-1 枚举 target 的 Run 范围恢复（主 AC）** | MET | 单测证明同 entries 快照下 path-only resolver=null（before）而 Run 范围返回 live scope（`Unresolved=0`）；gated 真 IPC before `path_resolver=null` → after `targets=1/unresolved=0/bound_pages=1/minted=1/resolve p1 OK` |
| **AC-RUN-2 fail-closed 矩阵与不回落 sibling** | MET | 缺失/撤销/代次漂移 → `Unresolved`；同路径 live sibling 不采用；未解析零 grant、零 `AuthorizeSourceReadForRun` 帧（单测 + gated） |
| **AC-RUN-3 非枚举语义零变化** | MET | `ResolveRegistryEntry`/`SourceScanScheduler.cs` 零字节；非枚举 target 在同状态仍 `Unresolved`；既有 `SourceRegistryTests` 32/0/0 原样通过 |
| **AC-RUN-4 冷源 on-demand 分类恢复** | MET | live 但无 Core version → `ColdSources=1`/`Unresolved=0`；authorizer 恰 1 次 bounded scan 后 mint，第二次不再扫描；预算/超时/失败仍 skip（既有用例原样通过） |
| **AC-RUN-5 无自动授权/无 identity 重建/不写 registry/不抛** | MET | 只读快照；无 `Register`/`Revoke`/`Reset`；真实 registry 前后结构全等、旧 revoked 行保留；重复 id 异常降级为 `Unresolved`（判别用例） |
| **AC-RUN-6 gated 真实 IPC 闭环（before/after）** | MET | 真实 Core + registry + zip + referenced 页：before 页读 typed 拒绝/0 帧 → after `bound_pages=1`/`minted=1`/`resolve p1` OK；wire/stderr 无路径；`reattest_frames=0`、`host_registry_unchanged=true` |
| **AC-RUN-7 零契约/零漂移** | MET | C16 `a7f57ebd…`、C17 blob 零漂移；`PROTOCOL_MINOR=3`；pins 18/18；`src/**`/`tests/**`、`NewManga.CoreClient`/`NewManga.App` 零 diff；API inventory 61 不变 |
| **AC-RUN-8 门禁/不夸大/触发口径** | MET | check（默认+`-TaskPath`）PASS；全量 pytest **3360/10**、全量 .NET **1661/0/95**（起点 1652/0/94；+9 单测 +1 gated skip）；跑后 `verification/FEA-09` CLEAN；措辞仅承诺「B1 显式动作 → 既有 refresh/reattest → 枚举 → Run 预授权/冷源分类」 |

## 2. 验证证据（实跑；`delivery_head=fad1ec776`）

| 场景 | 命令 | 结果 | 日志 |
|---|---|---|---|
| 构建 | `dotnet build apps/desktop-avalonia/NewManga.sln -c Release` | **PASS 0 warning / 0 error** | `logs/build.log` |
| Host 单测（新） | `--filter "FullyQualifiedName~SourceRunRangeResolution"` | **PASS 9/0/0** | `logs/host-unit.log` |
| 回归（Run 范围既有） | `--filter "FullyQualifiedName~SourceRegistryTests"` | **PASS 32/0/0** | `logs/regression.log` |
| gated 真 IPC | `NEWMANGA_FEA11_IPC=1 … --filter "FullyQualifiedName~Fea11RunGrantIpc"` | **PASS 6/0/0**（含新闭环） | `logs/host-ipc.log`、`logs/ipc-closed-loop.json/.txt` |
| 定向 pytest | `pytest tests/core/test_host_control.py tests/fea11/test_source_run_grant.py -q` | **PASS 89 passed** | `logs/regression-74.log` |
| 全量 Python | `pytest tests -q` | **PASS 3360 passed / 10 skipped / 262.86s**（起点同值） | `logs/full-pytest.log` |
| 全量 .NET | `dotnet test NewManga.sln -c Release`（cwd `apps/desktop-avalonia`） | **PASS 1661 / 0 / 95**（起点 1652/0/94；+9 单测、+1 新 gated skip） | `logs/full-dotnet.log` |
| 治理 | `verify_pins.ps1` / `check.ps1`（默认 + `-TaskPath`）/ `generate_api_inventory.py --check` | **PASS**（见 EV §2 与 `logs/gates.log`） | `logs/gates.log` |
| scope | `python …/tools/scope_validation.py` | **PASS**（见 EV §2 与 `scope-validation.log`） | `scope-validation.log`、`changed-files.txt` |
| 判别性 | `python …/tools/discrimination.py` | **PASS 5/5 RED_AS_EXPECTED + 逐例 sha256 复原 + 复绿** | `logs/discrimination.log` |

- **before / after**：同一 gated 测试内 before = `path_resolver=null` + `resolve_page_resource` typed `SOURCE_ACCESS_DENIED` + `authorize_frames=0`；after = `targets=1/unresolved=0/bound_pages=1/minted=1/resolve p1 OK`。
- **跑后恢复**：全量 .NET 重写 tracked `verification/FEA-09/logs/wire-redacted.ndjson` → 已 `git checkout -- verification/FEA-09`。
- **并发披露**：共享 `main` 同期 Lead docs-only `7be65026e`；本卡提交均显式 pathspec；`git diff e78c144bb..HEAD -- src tests` 为空。

## 3. 已知 limitation（closeout 必须保留）

- **「Run 预授权/冷源分类恢复」≠「Run 全面恢复」**：只覆盖 B1 显式动作 → 既有 refresh/reattest → 枚举之后的 Run 范围解析与 cold 分类；managed-only Run 无需 source 授权；Host 侧 mint 仍可能 typed skip（best-effort，不阻断 managed 页）。
- **不修**：扫描面（L-S4-B-1 已 done）、`ResolveRegistryEntry` 非枚举语义、B2 `roots_available`、folder（L-S4-2）、L-S4-1、L-R1、多根 first-root。
- **Scheduler 未启动/枚举失败**：`known` 为空，无 grant（既有配置行为，不承诺）。
- gated 闭环的 Core `source_locations` 由测试侧 `AlignRegistryAsync` 对齐（等价既有 reattest 结果）；本卡不发 `ReattestSourceLocation`（`reattest_frames=0`），reattest 往返由 L-S4-B 证据覆盖。
- 2C 长 Run（>300s 失权）保留；L-R11/C-04b/SCAN-RH/UI P3 保留。

## 4. 接收方式

- 仓库/分支：`G:\CODEX\New Manga`，`main`；实现起点 `e78c144bb`；**delivery_head=`fad1ec776`**（未 push、未建 worktree）。
- 复现（repo root）：见 `verification/FEA-11-L-S4-B-2-RUN-RANGE-RESOLVE-1/EV.md` §7。
- 接收者下一步：①Lead 指派**独立上下文** Review（只读 `fad1ec776`；重点：枚举分支只复用 public static helper、非枚举零变化、异常→unresolved、cold 分类/预算、gated before/after、5/5 判别性、零契约/零 Python diff、措辞不夸大）；②Lead 复跑 gated before/after；③Lead 集成门禁与 closeout（本 Handoff 不改卡 `status`；卡面 `delivery_head` 已回填）。

## 5. 下一任务建议

- 本卡 Review/集成前不释放后续实现。
- Review 通过后建议队列（由 DSH 裁决）：**2C 长 Run（L-G1）**（>300s 失权；新 host-control/续期设计，成本/契约面大）→ B2 `roots_available`（无消费者，延后）→ L-S4-2 folder、L-S4-1、L-R1；L-R11/C-04b/SCAN-RH 穿插；UI P3 最后。均需先 scope/设计 review 再冻结。
- **Recovery point**：`G:\CODEX\New Manga` / `main` / `fad1ec776`（未创建 worktree，若需隔离 worktree 待 DSH 创建）。

## 6. 风险与遗留

- **R1 口径风险**：「Run 范围恢复」易被读成「Run 全面恢复/自动恢复」；本卡口径固定为「B1 显式动作 → 既有 refresh/reattest → 枚举 → 预授权/冷源分类」，并明写 managed-only Run 与 mint typed skip 边界。
- **R2 授权面**：枚举分支只认 target 自身 live id（`SelectEnumeratedEntry`），不回落 sibling；`Registry.Authorize` 仍在 mint 时逐请求复核 live/generation/根包含/卷-文件身份。
- **R3 fixture 噪声**：gated 使用本卡 workspace fixture 根（仓外、无 tracked 副作用）；证据 JSON 已复制入 `logs/ipc-closed-loop.json` 并记录来源 hash（`logs/ipc-fixture.txt`）。
- **R4 并发共享工作树**：证据按 `delivery_head` 归因；Lead 集成若 HEAD 前进需按其 head 重跑门禁。
- **回退**：`git revert fad1ec776 f6b5a761a`（2 个实现/测试提交）；无 schema/数据迁移、无 Core 写行为变化，回退无数据风险。
