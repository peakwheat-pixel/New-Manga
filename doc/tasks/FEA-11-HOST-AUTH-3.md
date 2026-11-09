---
id: FEA-11-HOST-AUTH-3
title: 跨进程崩溃恢复的 grant 语义（C-17 v1.2 计划物化投影 + Host 恢复重铸）
kind: implementation
governance_version: 3
status: ready
approval: **scope review r2 `READY-TO-FREEZE`（`doc/reviews/FEA-11-HOST-AUTH-3-scope-r2.md`）** + ZCode 独立裁决（`doc/reviews/ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md`）+ **C-17 v1.2 已冻结**（载体 `doc/reviews/CONTRACT-UNFREEZE-2026-11-09-C17.md`；`verify_pins` 18/18）。**实现范围按本卡冻结；不得自行 UNFREEZE/重算 pin。**
suggested_owner: dsh
owner: null
reviewer: 待指派（必须独立上下文）
depends_on:
  - FEA-11-HOST-AUTH-2
base_commit: e9ab2ef7c
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEA-11-HOST-AUTH-3
allowed_paths:
  - doc/tasks/FEA-11-HOST-AUTH-3.md
  - doc/reviews/FEA-11-HOST-AUTH-3-*.md
  - doc/handoffs/FEA-11-HOST-AUTH-3-*.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/FEA-11-HOST-AUTH-3/**
  - src/bootstrap/core_service.py
  - src/application/sources/materialization.py
  - src/application/sources/errors.py
  - tests/fea11/test_source_plan_materialization.py
  - tests/fea11/test_source_command_parity.py
  - apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/SourceReadCoordinator.cs
  - apps/desktop-avalonia/src/NewManga.Host/HostRuntime.cs
  - apps/desktop-avalonia/src/NewManga.Host/Sources/HostErrorCodes.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthTests.cs
  - apps/desktop-avalonia/tests/NewManga.Host.Tests/Fea11HostAuthIpcTests.cs
out_of_scope:
  - **契约字节零改动**：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（v1.2 已冻 `cdeee487…`）、`FEA-CONTRACT-FROZEN-C17.md`、`CONTRACT-UNFREEZE-2026-11-09-C17.md`、其余 17 份契约、`doc/contracts/FEA-C07_API_INVENTORY.md`
  - **不得改动**：`HostCommandRegistry.cs`、`HostCommandDispatcher.cs`（契约 :196 不登记/C-07 零增量）、`src/infrastructure/resource_channel/source_read_refs.py`、`src/application/sources/runtime.py`、`src/infrastructure/sqlite/source_sync.py`、`src/application/sources/ports.py`
  - 不实现 retry 命令（D-3 out_of_scope）、不修 R-03（另立缺陷卡）、不实现 FEA-13 备份/恢复、不改 UI 面
  - 不把 gated 未跑写成 PASS；不得使用禁止措辞（见 AC-H3-6）
---

# FEA-11-HOST-AUTH-3：跨进程崩溃恢复的 grant 语义

## 来源与冻结依据

- 来源：`FEA-11-HOST-AUTH-2` 的 AC-F3 被范围审查判架构阻塞后 re-home；A/C 路线 `ARCHITECTURE_BLOCKED`，B+D-4 单 pin additive 经 ZCode 裁决批准。
- **C-17 v1.2 已冻结**：新增只读 host-control `GetSourceSyncPlanMaterialized / source_get_sync_plan_materialized`（`plan_id!`/`plan_digest!`），读回 Core 已持久化计划子集（`body_json` 的 kind/source_id/version_id/content_digest/entries/reference_set_digest + 表列 state/expires_at）；`SOURCE_PLAN_NOT_FOUND`/`SOURCE_PLAN_UNAVAILABLE`；capability `source.sync.plan-materialization/1`；零写、不铸 grant。
- scope r2 冻结：19 条 allowed_paths、AC-H3-1…6、证据计划、风险。

## 实现口径

| 侧 | 内容 |
|---|---|
| Core | `core_service.py` 注册 host-control 命令 + handler；`application/sources/materialization.py`（新）单函数 `materialize(store, payload)` closed shape；`errors.py` 两错误码；capability 仅在装配时出现 |
| Host | `CoreServiceClient` 新常量与调用；`SourceOperationCoordinator` 在 `Acknowledge/Recover` 的 **Core-backed 段**（非 `PrepareCompletion`）读物化并重铸；`SourceReadCoordinator.IssueForRecoveryAsync` 窄 seam；`HostRuntime` 注入 `Sources` |
| 重铸输入规则 | `registry_id/generation/identity_digest` 来自 journal `authorization`；**source 路径 = `SourceAccessRegistry` 的 `Roots`（必须恰好 1 个 readable root，否则 typed fail-closed）**；`source_kind` = `ScanTarget.source_kind`；`version_id/entries` = 物化投影。**不得猜 locator/kind** |
| 语义边界 | `_verify_fresh` 只校验 grant 的物理 identity 与 authorization 基线 → 重铸 grant 必须真实、同源，不得伪造；entries 不必与 plan 逐条相同 |
| 通道 | 新命令 host-control（普通面 `HOST_ONLY_REQUIRED`）；不登记 HostCommandRegistry/C-07 |
| state 语义（r2 定稿） | Core **不过滤** state（`draft/previewed/confirmed/applied/stale` 均可物化，守卫只校验 plan_id/digest）；`applied` 仅为 **Host 恢复的前置条件**（Host 侧拒绝矩阵负责） |

## Acceptance Criteria（AC-H3-1…6）

- [x] **AC-H3-1 契约与字节不回退**：`verify_pins` 18/18（C17 `cdeee487…`，其余 17 零变化）；`git diff --name-only` 不含「不列入」清单；C-17 工作树 SHA-256 不变。 <<MET>>
- [x] **AC-H3-2 Core 新命令**：零写（逐表相等）、closed shape/类型/未知键负例、host-control vs 普通面、typed 矩阵（NOT_FOUND/STALE/UNAVAILABLE/BUDGET）、entries ordinal 升序唯一、missing 目标 null、过期 applied 可读、脱敏 0 命中。 <<MET>>
- [x] **AC-H3-3 Host 重铸**：completion 不再用 journal `GrantIds`；每 registry `Authorize(liveGeneration, root)` 后 mint（TTL ≤300s）；≥6 拒绝矩阵全部 typed、零帧、journal 不变、gates pending。 <<MET>>
- [x] **AC-H3-4 真实 kill 恢复一次**：park（`core-committed`）→ `Kill(entireProcessTree)`（断言 dotnet 与全部 Python PID 消失，未证实记 FAIL）→ 新进程 recover 成功一次；行数不变、`read_gate` 0 pending、`commit_digest` 一致、源 sha 不变、**三重防伪**（PID/session/grant_id 不在 journal）；二次调用 0 新帧。 <<MET>>
- [x] **AC-H3-5 变异判别**：M1 复用 journal grant → typed `SOURCE_ACCESS_DENIED`；M2 移除 host-control → `HOST_ONLY_REQUIRED`；M3 投影写库 → 零写断言失败；M4 删 digest 校验 → 负例被抓；M5 删 state!=applied → 拒绝矩阵失败；M6 猜路径/kind → 负例抓住。变异证据入 `mutations/`。 <<MET>>
- [x] **AC-H3-6 门禁/范围/不夸大**：`check.ps1`（默认 + `-TaskPath`）PASS；`verify_pins` 18/18；`generate_api_inventory.py --check` EXIT 0；diff ⊆ allowed_paths；工作树 clean；全量 pytest 不低于当轮基线、.NET failed=0；gated 用例默认 skip 且逐条原因。 <<MET>>

## 卡面 errata（冻结时已落盘）

- `SOURCE_GRANT_EXPIRED` → **`SOURCE_ACCESS_DENIED`**（整树 kill 后未注册 grant 的码）；AC 与实现诊断以 `SOURCE_ACCESS_DENIED` 为准。
- AC-H3-2 的 state 语义按 v1.2 DTO 全枚举（`draft/previewed/confirmed/applied/stale`），不只 applied。
- 物化读取位置：`Acknowledge/Recover` 的 Core-backed 段，**不进 `PrepareCompletion`**。
- 禁止措辞（AC-H3-6）：任意崩溃点均可恢复 / grant 已持久化 / 自动重新授权 / limitation 3 或 4 已闭合 / 无副作用。

## 证据计划

`verification/FEA-11-HOST-AUTH-3/`：`crash-ack.ps1`（从 HOST-AUTH-2 骨架复制后改）、`park.json`/`recover.json`、kill 前后 PID 列表、DB 前后导出、脱敏 wirelog、两次 ACK 帧计数、源文件 sha256、`mutations/`（M1–M6 diff+失败输出）、日志（命令头/EXIT）。

## 风险与回退

| 风险 | 处置 |
|---|---|
| 重铸输入缺口（路径/kind） | 规则 + fail-closed（多 root/缺 kind → typed 拒绝） |
| Core-free 默认门禁被破坏 | 物化读取不进 `PrepareCompletion` |
| kill 未真正杀 Python | AC-H3-4 显式 PID 断言；未证实记 FAIL/NOT_RUN |
| 契约回退风险 | AC-H3-1 字节与 pin 断言；需要重算 pin 即停止回 DSH |
| 回退 | `git revert` 实现提交；无 schema/契约变更 |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | NOT_APPLICABLE（main；base `e9ab2ef7c`） | NOT_APPLICABLE | — | — | 未创建 worktree |
| temp | pytest / gated IPC 临时目录 | NOT_APPLICABLE | — | — | 测试隔离 |
| build | `apps/desktop-avalonia/**/bin,obj` | NOT_APPLICABLE | — | — | 既有 ignore |
| user-data | NOT_APPLICABLE | NOT_APPLICABLE | — | — | 未访问真实库 |

## Closeout Record

- 未开始（ready，待实施）。
