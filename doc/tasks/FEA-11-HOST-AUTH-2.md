---
id: FEA-11-HOST-AUTH-2
title: Host ACK/recovery 使用 fresh 授权（C-17 §3.2 遵守型；0 pin）+ ACK 重发/恢复 gated e2e + 崩溃点
kind: implementation
governance_version: 3
status: done
approval: 用户 2026-11-08 残余收口指令（R1）；独立 scope review `doc/reviews/FEA-11-HOST-AUTH-2-scope-r1.md`（session `bd32e3f6-…`，verdict **READY-TO-FREEZE**）；DSH 2026-11-08 裁决：判据 (b) 契约对齐（遵守型，0 pin），窄口径 done（limitation 关闭面 + re-home）；Owner=`host-auth-2-impl`
suggested_owner: dsh
owner: host-auth-2-impl
reviewer: 独立上下文 fresh subagent（不得由实现会话/实例自审；r1 指派于实现交付后，session 记入 `doc/reviews/FEA-11-HOST-AUTH-2-r1.md`）
depends_on:
  - FEA-11-HOST-AUTH-1
base_commit: 4070f0043
branch: null
worktree: null
integration_commit: f7016d3fb
delivery_head: f7016d3fb
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA-11-HOST-AUTH-2
allowed_paths:
  - doc/tasks/FEA-11-HOST-AUTH-2.md
  - doc/tasks/FEA-11-HOST-AUTH-1.md
  - doc/reviews/FEA-11-HOST-AUTH-2-*.md
  - doc/handoffs/FEA-11-HOST-AUTH-2-*.md
  - verification/FEA-11-HOST-AUTH-2/**
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostOptions.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/SourceOperationTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11SourceIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthIpcTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/HostRuntimeIntegrationTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Support/HostFixture.cs
out_of_scope:
  - 契约字节：`doc/plan/**`、`doc/contracts/**`、18 pins（本卡为「遵守型」，**不得**新增/修改 C-17 字节；冻结证据见 `doc/reviews/FEA-11-HOST-AUTH-2-scope-r1.md` §1.2）
  - wire/Core：`apps/desktop-avalonia/src/NewManga.CoreClient/**`、`src/**`（Python）、新命令/新错误码/新 DTO/capability
  - `HostOperationOrchestrator.cs`（apply/retry 已 fresh）、`HostErrorCodes.cs`
  - 产品/UI：新增 UI 入口、`RecordSourceOperationFailure` 的 UI 触发（C-17:162 的显式失败路径留待后续卡）、自动重新授权/自动续签 grant
  - 真实用户数据/AppData/外部卷/真实回收站/原文件；L3/L4 真机走查（保持 `NOT_RUN`）
  - C-17 UNFREEZE 类项（limitation 3「retry 命令」/limitation 4「plan-read」）→ **本卡只 re-home，不做**
---

# FEA-11-HOST-AUTH-2：Host ACK/recovery fresh 授权（0 pin）

> **状态：`ready`（已冻结；base `4070f0043`；Owner=`host-auth-2-impl`）。**
> 目标：把 `FEA-11-HOST-AUTH-1` 从 `closed_with_limitations` **翻 `done`**（AC3 PARTIAL → MET），关闭 C-17 §3.2 的 fresh 授权缺口（Codex 终裁附注 P2-7）。
> 契约依据（**冻结字节，0 pin**）：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:161`（ACK 行）、`:169`（「见下」正文）、`:160`、`:162`、`:165`、`:258`、`:260`、`:264`、§8 拒绝码闭集；独立复核见 `doc/reviews/FEA-11-HOST-AUTH-2-scope-r1.md` §1（含 pin `aefa0fa5…` 实测一致、v1.0 冻结字节逐行比对结论）。

## 缺陷（冻结事实，base `4070f0043`）

- **ACK**：`SourceOperationCoordinator.cs:172-174` 读 `committed.AuthorizationJson`（apply 时落盘原字节）经 `:193-194` 原样填入 CompletionRequest；**无** Registry 读取 / `Authorize` / `Mint` / journal 更新。
- **recovery**：同文件 `:232-233`、`:237-268`、`:288-289` 同样使用原 authorization，且回读 receipt 时未核对 operation_id/request_digest/state。
- 后果：Host Registry 已撤销 / root 已替换时，只要 Core 侧 grant 仍 live，旧 authorization 仍可 ACK 成功并开门（Host 读路径每请求仍重验 Registry → 定级 **P1 契约一致性/纵深防御缺口**，非 P0 绕过）。
- 对照：apply/retry 已是 fresh 路径（`HostOperationOrchestrator.cs:273-301`、`:103-136`）→ 缺口精确落在 ACK/recovery。

## Acceptance Criteria（冻结；窄口径 done，见 AC-F5）

- [x] **AC-F1（默认门禁：fresh 完成授权）**：ACK/recovery 不再发送 apply 时授权；`PrepareCompletion`（或等价 seam）重读 live `SourceAccessRegistry` 并 `Authorize`（`LastUsedAt` 推进）+ 重签：`OperationId/RequestDigest/HostReceiptId` 不变、`authorized_at` 晚于 apply 时、journal 的 `AuthorizationJson/AuthorizationDigest` **先于** Core 调用落盘、`AuthorizationDigest == sha256(canonical(authorizations))`；拒绝矩阵（Core 零调用、journal 状态/授权字节不变）：revoked→`SOURCE_GRANT_REVOKED`、缺失 registry→`SOURCE_ACCESS_DENIED`、root identity 变→`SOURCE_REGISTRY_UNAVAILABLE`、基线 generation > live→`SOURCE_GRANT_REVOKED`、digest 不可复现→`SOURCE_SYNC_STATE_CONFLICT`。 <<MET>>
- [x] **AC-F2（gated 真实 IPC：ACK/recovery）**：apply→journal `core-committed` 后 ACK 前 `resolve_page_resource` 拒绝；ACK 成功（wire `authorization.authorized_at` 晚于 apply）→ Core `acknowledged`、gate 开、resolve 出新键；二次 ACK = 0 新增 wire 帧、0 新 binding；同 CompletionRequest 重发 = 同 receipt、0 新 binding；错 digest operation → ACK typed 拒绝、journal 仍 `core-committed`、gate 仍 pending、0 行变化；未 ACK 的 `core-committed` → `RecoverAsync` 成功 + 二次幂等。 <<MET>>
- [x] **AC-F3（gated 崩溃点）**：真实子进程在 journal=`core-committed` 后被 kill（外部驱动脚本，`Process.Kill(entireProcessTree:true)`；**不得** `Environment.FailFast`、**不得**用同进程新 coordinator 冒充）；**新进程**读 journal/registry/Core DB 后 recovery/ACK 成功一次、gate 全开、`page_bindings`/`source_binding_publications` 行数不变、二次调用幂等、`commit_digest` 一致。 <<NOT_APPLICABLE: 架构阻塞（Core source-read grant 仅进程内 TTL，src/infrastructure/resource_channel/source_read_refs.py:106-121；C-17 §5.2:258/§5.3:276 禁止省略 grant_ids）→ re-home 到 FEA-11-HOST-AUTH-3；NOT_RUN 保留>>
- [x] **AC-F4（条件性 HostRuntime e2e）**：`HostOptions` 最小 Core 覆盖 seam + `runtime.Commands.InvokeAsync` 全链路（register→scan→plan/preview/confirm→apply→ACK）；`runtime.Operations.Get(id).State==acknowledged`、gate 开、resolve 新键、源字节守恒、ACK wire 为 fresh；**缺 `source.sync.apply/1` → RED**（不得 skip 冒充 MET）；若打包 sidecar 腿不做，必须在卡面/closeout **显式 re-home**（不得写成真实 sidecar 已覆盖）。 <<NOT_APPLICABLE: re-home 到 FEA-11-HOST-AUTH-5（HostRuntime 全链路 e2e + HostOptions Core 覆盖 seam；打包 sidecar 腿 NOT_RUN）>>
- [x] **AC-F5（门禁 + 翻 done 的窄口径）**：全量 .NET `passed ≥ 当轮实测基线`、`failed=0`（新增 gated 默认 skip 须逐条记原因）；pytest `≥3390/10` 不降；`check.ps1`（默认 + `-TaskPath`）PASS；pins 18/18；API inventory EXIT 0；scope ⊆ allowed_paths；契约/schema/依赖零 diff；**`FEA-11-HOST-AUTH-1` append-only 关闭记录 + AC3→MET + PLAN 行改 `done`**；limitation 关闭面 = {1, 2, 5(若 AC-F1c 做), P2-7}，**{3, 4, 6, 7, 8, 9} 逐项 re-home 到具名后续卡**；不得写「完全实现」。 <<MET>>

## 实现口径（冻结，偏离须先回 DSH）

1. **方案 A（评审推荐）**：`SourceOperationCoordinator` 增可选 `SourceAccessRegistry? registry`（`HostRuntime.cs:1225-1226` 传现有 `Registry`）；新增可测 seam `PrepareCompletion(operationId)`：锁内读 journal → 校验 state → 解析原 authorization 的 `authorizations[]`/基线 `identity_digest` → 对每个 registry `List()` + `Authorize(live.Generation, readableRoots)` → `HostAuthorizationMinter.Mint(...)`（live generation + **基线 identity_digest**，沿用原 `OperationId/RequestDigest/HostReceiptId`）→ 守卫 `minted.RequestDigest == entry.RequestDigest` → 锁内重读 journal + 确认 state 未变 → **先落盘** fresh `AuthorizationJson/Digest` → 返回 material。ACK：早退 → Prepare → 发送 → 锁内 state 守卫后写 `acknowledged`；recovery：回读 receipt（保持现有 `:237-268`）→ Prepare → 发送 → 写 `recovered`。
2. ACK 成功后写 `acknowledged` 必须**锁内重读 + 要求 state 仍为 `core-committed`**（防 `MarkFailed` 竞争）；recovery 前应核对 Core receipt 的 operation_id/plan_id/plan_digest/request_digest/kind/state/commit_digest（AC-F1c）。**不做** `CommitReceipt` canonical 重算。
3. 复用现有拒绝码（C-17 §8 闭集）；**不新增**错误码/命令/DTO/capability；**不改** journal 格式（复用 `authorization`/`host_receipt_id` 字段）。
4. 测试：默认门禁用例必须**不依赖 Core**（`CoreServiceClient` 是 sealed，无法 fake → seam 是必要条件）；gated 用例用 `NEWMANGA_FEA11_IPC=1`；崩溃点用 `verification/FEA-11-HOST-AUTH-2/tools/crash-ack.ps1` + 两个 env-gated fact（`park`/`recover`）。
5. 提交：显式 pathspec，禁 `git add -A`；含中文改动用 edit/UTF-8。

## 待 re-home 的 limitation（本卡不做，但必须在 closeout 具名）

- **limitation 3**（需「retry 命令」→ C-17 UNFREEZE 类）→ re-home 到 `FEA-11-HOST-AUTH-3`（未建，需先 scope review）。
- **limitation 4**（plan-read 命令 → C-17 UNFREEZE 类）→ re-home 到同一后续卡。
- **limitation 6/7/8/9**（输入规则 / Registry atomicity / 分类精度 / capability reason）→ re-home 到 `FEA-11-HOST-AUTH-4`（未建）。
- **limitation 5**（ACK 前 receipt 字段核对）→ 若 AC-F1c 实现则关闭；否则 re-home。

## 行文口径（红线）

- 不得写「FEA-11-HOST-AUTH-1 完全实现 / C-17 §3.3 完全实现 / 10 项 limitation 全部关闭」；只写「AC3 由 PARTIAL 重判 MET；limitation {1,2,5,P2-7} 关闭；{3,4,6,7,8,9} re-home」。
- 不得写「真实打包 sidecar 已覆盖」（若 AC-F4 走 seam 路线）；`NOT_RUN` 不得写成 PASS。
- 不宣称可发布：`Technical Gate=NOT_SATISFIED` 不变。

## Canonical Evidence

> `commit` 列：实现文件填其所在提交；closeout 证据填 `-`（提交 sha 见 handoff §30）。sha256 为工作树字节口径。

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-01 | AC-F1/R2 | apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs | f7016d3fb | a4213091e2b2857d5b1263fd2cd659210eb07efe84383711f7b0c13542e9bfdb | SOURCE_PIN |
| EV-02 | AC-F1 | apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs | f7016d3fb | ca4da7104bf88abde4b5f7481b0f8e7c28e918a549ada027a9a0a76d32b9fc70 | SOURCE_PIN |
| EV-03 | AC-F1 | apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthTests.cs | f7016d3fb | 2e7bdab927851b1cff7d9fe1b99de2b389ab10d4d2bfe73d74b84b236352683d | SOURCE_PIN |
| EV-04 | AC-F2 | apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthIpcTests.cs | f7016d3fb | 3f2c44b50ac040d3dd62b35ce75eb201943d8e579da00430f6eae75400c9ae8c | SOURCE_PIN |
| EV-05 | 冻结面 | doc/reviews/FEA-11-HOST-AUTH-2-scope-r1.md | - | ab3979598eb8e561a7d03c42e2f8645451fa367946b0b13495c6dd9019a23619 | CANONICAL |
| EV-06 | 独立 Review r1（approved；P0/P1=0） | doc/reviews/FEA-11-HOST-AUTH-2-r1.md | - | f3ec4f8bc910399df14bf4c1aa31f03df878e8ac149c5deae0b46ff81a4399e8 | CANONICAL |
| EV-07 | AC-F5（证据总览） | verification/FEA-11-HOST-AUTH-2/EV.md | - | d0b13e34de427e1303645e8f4e53ef5a039e8a8b78651b8537e8a92d7f4aa6d9 | CANONICAL |
| EV-08 | AC-F5（资源清单） | verification/FEA-11-HOST-AUTH-2/RESOURCE-MANIFEST.json | - | c19ccbe64239aff933879651791270f260b56ea21e7dd83c91326fdeacba9779 | CANONICAL |
| EV-09 | AC-F5（改动清单） | verification/FEA-11-HOST-AUTH-2/changed-files.txt | - | 50bdc34eacffcad3dca9b0945676a67906af6c770b55e610108b6c091e371769 | CANONICAL |
| EV-10 | AC-F5（Lead 门禁日志） | verification/FEA-11-HOST-AUTH-2/logs/gates-lead.log | - | fc608745572e48279cc8c2692cd0533a1bc0e66a7f00d0ea2e734fd8eca8b994 | CANONICAL |
| EV-11 | re-home 载体 | doc/tasks/FEA-11-HOST-AUTH-3.md | - | 4a7e1ca8bacfebcd74b5347eb1bed9b6fa8bd49e2e480ffc904296389413a82c | CANONICAL |
| EV-12 | re-home 载体 | doc/tasks/FEA-11-HOST-AUTH-4.md | - | 60a3d02a4d45ab16147458ab9dfce6526b7b9b006029c6abf32f7c0b38a54c00 | CANONICAL |
| EV-13 | re-home 载体 | doc/tasks/FEA-11-HOST-AUTH-5.md | - | cdc51f9640d23d62f5437bfa2a4a1b15ceab98c73e2961f6b5b4394ace2653c5 | CANONICAL |
| EV-14 | AC-F3（NOT_RUN 骨架） | verification/FEA-11-HOST-AUTH-2/tools/crash-ack.ps1 | - | 8150d58cbe9192a8baa0a41efae5549cb665de6c4630b460a0c3b3e81206483f | CANONICAL |
| EV-15 | AC-F2（fixture 工具） | verification/FEA-11-HOST-AUTH-2/tools/build_plan_body.py | - | 8e39aed36be5e50e4b85d5f254a37c622da99ea5f3bd2dc7e72880208f3f8b53 | CANONICAL |
| EV-16 | AC-F2（行数核对工具） | verification/FEA-11-HOST-AUTH-2/tools/count_bindings.py | - | 23b31c4cd3f580e629c8135d1ee1011758006d2991c6de7c54767459b85816b4 | CANONICAL |
| EV-17 | AC-F5（交付说明） | verification/FEA-11-HOST-AUTH-2/README.md | - | 32b51373f53e3f4bdd9dcdbeda07ea9191253a686c67324c8407802193ab7fb8 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `2849001a8`，impl `f7016d3fb`） | NOT_APPLICABLE | — | — | 未创建 linked worktree |
| temp | `G:\CODEX\New Manga.workspace\FEA-11\review-host-auth-2\`（reviewer pristine + 日志） | PRESERVE_REFERENCED | `G:\CODEX\New Manga.workspace\FEA-11\review-host-auth-2` | `verification/FEA-11-HOST-AUTH-2/RESOURCE-MANIFEST.json` | 仓外；reviewer 已逐字节复原（sha256 MATCH），工作树 clean；保留供审计 |
| test-fixture | `verification/FEA-11-HOST-AUTH-2/tools/*`（含 `crash-ack.ps1` 骨架）+ Host.Tests | NOT_APPLICABLE | — | — | gated fixture 在 workspace；`crash-ack.ps1` 为未实现骨架，随 `FEA-11-HOST-AUTH-3` |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 只用隔离临时数据根，未触碰真实数据 |
| tracked-side-effect | `verification/FEA-09/logs/wire-redacted.ndjson` | NOT_APPLICABLE | — | — | 全量 .NET 既有副作用；每次跑后 `git checkout -- verification/FEA-09` 恢复 |

## Closeout Record

- **Closeout date / DSH**：2026-11-08。
- **终态**：`done`；`integration_commit` = `delivery_head` = **`f7016d3fb`**；冻结卡 `2849001a8`；closeout 提交见 handoff §30。
- **Review**：独立 r1 **approved（P0=0/P1=0/P2=5/P3=9）**；7 组变异（M1/M2/M3/M5/M8 RED；M4/M6 存活→P3-2/3 登记）。
- **AC 定稿**：AC-F1 / AC-F2 / AC-F5 **MET**；**AC-F3 / AC-F4 `NOT_APPLICABLE` + re-home**（`FEA-11-HOST-AUTH-3` / `-5`），**不写 MET**。
- **重大发现**：既存 latent bug（ACK/recovery payload 双层对象）导致生产 coordinator **从未发出过 ACK/recovery 帧**；本卡修复（wire 形状=契约六字段）。
- **乐观收益**：`FEA-11-HOST-AUTH-1` 由 `closed_with_limitations` → `done`（AC3 MET），limitation 关闭面 {2, 5, P2-7}，其余按 §3 具名 re-home。
- **limitation**：表现状保留 —— AC-F3/F4 `NOT_RUN`；limitation 1（HostRuntime e2e）→ HOST-AUTH-5；3/4 → HOST-AUTH-3；6/7/8/9 + P3-1…8/10 → HOST-AUTH-4；`AuthorizationDigest` 双口径（P3-1）未统一；gated 用例默认 skip（2 例）并逐条记原因。
- **行文**：不得写「完全实现」「10 项 limitation 全部关闭」。
