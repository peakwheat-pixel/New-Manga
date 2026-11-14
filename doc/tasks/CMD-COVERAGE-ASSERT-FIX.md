---
id: CMD-COVERAGE-ASSERT-FIX
title: 修复命令覆盖断言的过时口径（E-1），恢复命令可达性守卫
kind: implementation
governance_version: 3
status: in_progress
disposition: "既有缺陷 E-1（doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md）；DSH 2026-11-15 释放"
approval: DSH 2026-11-15（Gate 条件 3 直接输入，范围冻结）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - MAINT-1-RELEASE-MONITOR
base_commit: 9a79b2a69
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/CMD-COVERAGE-ASSERT-FIX
allowed_paths:
  - doc/tasks/CMD-COVERAGE-ASSERT-FIX.md
  - doc/reviews/CMD-COVERAGE-ASSERT-FIX-*.md
  - doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/CMD-COVERAGE-ASSERT-FIX/**
  - apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/**
---

# CMD-COVERAGE-ASSERT-FIX：修复命令覆盖断言的过时口径（E-1）

## 来源与目标

**既有缺陷 E-1**：`DomainServices_CoverEveryCommandExactlyOnce` 断言"六个 `HostDomainService`
覆盖**全部** `HostCommandRegistry.All`（111 条）"，实际只覆盖 90 条 —— 失败值 `Expected 111 / Actual 90`。

**根因（已实测确认）**：`HostCommandDomain` 有 8 个域，但只有 6 个由 `HostDomainService` 承载；
`Drafts`（6 条）与 `SourceSync`（15 条）由 **`HostCommandDispatcher` 直接处理**
（`drafts_*` 是 `HostCommandDispatcher.cs:882-927` 的显式 case，`source_*` 经 dispatcher/host-control 通道）。
6 + 15 = 21 = 111 − 90。**断言与现行两通路架构不符，不是"缺两个服务"。**

**为何长期未被发现**：该测试标注 `[SidecarFact]`，未设 `NEWMANGA_CORECLIENT_SIDECAR_DIR` 时 SKIP；
而 `HostCommandDispatcher` 的构造参数**全部有默认值**，`HostDomainService.Descriptors` 又完全来自静态
registry —— 这组断言**根本不需要 sidecar**，却被关在 sidecar 门后。

**一个可观察交付结果**：该覆盖断言在**无夹具模式**下也真实执行并通过；且一旦有命令既不进任何
`HostDomainService` 也不属于 dispatcher 直通族，测试变红。

## Acceptance Criteria

- [x] **AC1 脱离 sidecar**：覆盖断言不再标注 `[SidecarFact]`，无 `NEWMANGA_CORECLIENT_SIDECAR_DIR`
      时**实际执行并通过**（不是 SKIP）。
- [x] **AC2 口径正确**：断言组为 —— ① 六服务 `Descriptors` 全局名称唯一；② 六服务覆盖集合
      = `All − (Domain == Drafts ∪ Domain == SourceSync)`；③ 未被六服务覆盖的命令**全部**落在
      `Drafts`/`SourceSync` 域（即 dispatcher 直通族）；④ 每个 domain 至少有一条命令。
- [x] **AC3 判别力**：构造"某条命令既不在服务也不在 `Drafts`/`SourceSync` 族"的情形时断言必须失败。
      用测试内的合成集合验证（不改生产代码），并记录回退实验。
- [x] **AC4 sidecar 专属断言保留**：原测试中真正需要真实 Core 的部分（跨域 `InvokeAsync` 被拒绝、
      `ImplementedCount` 投影）保留在 `[SidecarFact]` 版本里；其失败计数断言按新口径修正，
      **不得删除或放宽**跨域拒绝那一条。
- [x] **AC5 零生产代码改动**：`git diff` 不得触及 `src/**`；`HostCommandRegistry`、`DomainServices`、
      `HostCommandDispatcher` 一行不改。
- [x] **AC6 不回归**：`NewManga.CoreClient.Tests` 无夹具模式 0 failed 且 skip **不增加**；
      `check`/`pins`/`inventory` 三项不降级。

## 允许修改范围

见 frontmatter。核心只有 `apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/CommandIntegrationTests.cs`
（或同目录新文件）与卡面/证据。

## 禁止范围

- **不得**修改生产代码（`src/**`）：不得新增 DomainService、不得改 registry 的域划分、不得改 dispatcher。
- **不得**通过"跳过未覆盖命令""忽略 Drafts/SourceSync""把断言放宽为 Contains"等方式让它变绿。
- **不得**删除既有断言（除按新口径修正计数值外）。
- **不得**新增 skip/xfail。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | `dotnet test --filter CommandCoverageRoutingTests`（无夹具） | 无 sidecar | **4 passed**（76 ms） | `verification/CMD-COVERAGE-ASSERT-FIX/README.md` §3 |
| AC3 判别力 | 同上 `AC3_AnOutOfRouteCommand_IsReportedAsUnrouted`（合成 + 真实数据探针） | 无夹具 | **PASS**（三种方式验证同一谓词） | 同上 |
| AC4 | 设夹具跑原测试 | 旧 sidecar（能启动） | **1 passed**（修复前 `Expected 111 / Actual 90` 失败）；跨域拒绝断言保留未改 | 同上 §3 |
| AC5 | `git diff --stat` | 仓库根 | 仅测试 + 文档，**零 `src/**` 改动** | 同上 §2 |
| AC6 | 无夹具全量 CoreClient；四件套 | 仓库根 | **186 / 0 / 26**（本卡前 182/0/26，skip 未增加）；pins 18/18、inventory `1/80/6=87` | `four-pieces.log` |

## 依赖、风险与阻塞

- **风险 R1**：若把断言写成"每 domain ≥1 条"仍不足以发现"新命令漏接线"，必须有 AC3 的合成验证。
- **风险 R2**：`Drafts`/`SourceSync` 的命令若将来被移入 DomainService，断言会立即失败（这是期望行为，
  届时应同步更新断言口径而非放宽）。
- **环境**：真实 sidecar 集成仍受 E-2 阻塞（sidecar 早于多条现行命令）；本卡不依赖它。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文）。
- 实际测试：尚无。
- 后续记录日期、commit、环境、结果、遗留项；最终由 DSH 填 `integration_commit` 并改 done。
### r1 复核处置（ACCEPT_WITH_LIMITATIONS）

| finding | 处置 |
|---|---|
| **P2-1 未强制"exactly one route"**：把 `create_region` 加入 `SourceSyncCommandNames` 后新类仍 4/4 绿（重叠未被发现） | **已修**：`EveryUncoveredCommand_BelongsToADispatcherRoutedFamily` 增 `Assert.Empty(covered.Intersect(families))`；新增 `P2_1_AnOverlappingRoute_IsReported`（真实数据探针）。实测把 `create_region` 塞进 `SourceSyncCommandNames` → **5/5 变红**，还原后 5 passed。 |
| **P2-2 表述过强**：六个 `HostDomainService` 在生产 `src/**` 从未实例化，生产只经 `HostRuntime` → `HostCommandDispatcher` | **已修（表述）**：README §4.1 明确本守卫校验的是"registry 域划分与六服务端口契约抽象的一致性"，**不证明生产可达性**。 |
| **P2-3 引用了错误的保证链**：`extract-command-surface.py --check` 只比对旧 Rust `PRODUCTION_COMMANDS` 与快照；`core-command-probe.json` 25 条里没有 `drafts_*`/`source_*` | **已修**：README §4.3 更正，并明确"这 21 条与 Core handler 的一致性**未被覆盖**，属未验证面"。 |
| P3 `186/0/26` 未进 `four-pieces.log` | **已修**：重新生成日志并写入该数字。 |
| P3 提交越界带入 `verification/FEA-09/logs/wire-redacted.ndjson` | **已修（我方错误，原样登记）**：`git checkout 9a79b2a69 -- <path>` 还原，diff 归零，`verify_pins` 18/18。这是本会话**第二次**犯同一错误（`git add -A` 卷走 .NET 测试写脏的该文件），已在卡面登记。 |
| P3 `TASK_LEDGER` 计数过期 | 已随本轮重跑 `task_ledger.py --write`。 |
| P3 AC3"合成+真实探针"与 `FirstUnrouted` 同源 | 已在 README §4.2 说明其证明的边界（谓词有效，非独立证据源）。 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| agent-output | 待填 | NOT_APPLICABLE | — | — | 实现期按实际登记 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待填。
- 当前指针清理：待关闭时更新 STATUS / Plan / TASK_LEDGER / rolling checkpoint。
