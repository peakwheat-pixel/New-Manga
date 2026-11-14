---
id: FEA-06-RESIDUAL-4
title: RegionBox 逐 region 冲突投影与「查看对照」（原 RESIDUAL-2 格 3；需 C-07 additive）
kind: implementation
governance_version: 3
status: superseded
disposition: "RO-1 重开（2026-11-14 用户指令撤销 Q7 OUT；路线＝C-07 additive UNFREEZE；见 doc/reviews/MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md）；原 OUT 记录保留：OUT（2026-11-14 DSH；双签：Codex OUT + 独立子 agent OUT；见 doc/reviews/MAINT-1-P4A-Q7-Q8-ADJUDICATION.md。性质＝冻结设计意图的产品可见缩减，非缺陷修复）"
approval: 占位卡：由 `FEA-06-RESIDUAL-3` scope review r1（格 3 未解除）与 DSH 2026-11-08 裁决 re-home；**scope 未冻结，不得实施**；须先独立 scope review + 可能需要 C-07/UNFREEZE 类载体
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-06-RESIDUAL-3
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: complete
evidence_dir: verification/FEA-06-RESIDUAL-4
allowed_paths:
  - doc/tasks/FEA-06-RESIDUAL-4.md
  - doc/reviews/FEA-06-RESIDUAL-4-*.md
  - doc/handoffs/FEA-06-RESIDUAL-4-*.md
  - verification/FEA-06-RESIDUAL-4/**
out_of_scope:
  - 未 scope review 前不得实施任何实现
---
# FEA-06-RESIDUAL-4：RegionBox 冲突投影与「查看对照」（占位）

## 来源与已核事实

`FEA-06-RESIDUAL-2` 的 BLOCKED 表**格 3**「RegionBox 冲突态（查看对照）」在 `FEA-06-RESIDUAL-3` scope review 中被判**未解除**：

- `RegionSummary` 无任何冲突字段（`apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs:172-178`）；
- 区域文本投影 `list_page_region_texts` 已注册（`HostCommandRegistry.cs:191`）但**未经 `IHostController` 暴露**（`RegionTextProjection.cs:224-281` 仅测试使用）；
- 术语/冲突面为 NOT_WIRED（`StudioTermsViewModel.cs:36-62`）；
- **Current V2 也没有**「查看对照」；现有仅"并发冲突横幅 + 禁止伪造对照"（RESIDUAL-1 已完成，`FluentResidualBatchATests.cs:613-641`）。

## 阻塞与候选路线（须 scope review 定稿）

1. 补数据：把 `list_page_region_texts`（或等价的逐 region 冲突投影）加入 `IHostController` → 触 `tools/generate_api_inventory.py` 抽取面与 **C-07 pin** → 需 `FEA-C07` additive UNFREEZE 载体 + API inventory 重算。
2. 或降级产品范围：正式裁决「不提供查看对照，仅保留冲突横幅与 typed 原因」→ 以 `NOT_APPLICABLE: 产品范围决定` 记录（必须写清用户可见后果）。

## 验收（草案，待冻结）

- 若走 1：逐 region 冲突字段投影 + UI 对照面板 + 判别测试；契约/pin 变更须走 UNFREEZE 且独立 byte-level 复核。
- 若走 2：DSH/用户裁决记录 + `FEA-06-RESIDUAL-2` 卡面 append-only 更新（不得删改原 limitation 字节）。

## 处置记录（append-only，2026-11-14）

**结论：OUT / `cancelled`**（双签见 `doc/reviews/MAINT-1-P4A-Q7-Q8-ADJUDICATION.md`；Codex 与独立子 agent 均判 OUT）。

**性质必须说准**：「查看对照」是**冻结设计意图**（`doc/design/fluent-v1/06-page-workbench.md:50`、`09-state-matrix.md:14`），`FEA-06` AC3 为 PARTIAL 且明写缺该动作；2026-11-08 裁决是 re-home 而非 waive。因此本 OUT ＝**正式放弃该设计行**，不是"修掉一个 bug"，**不得**读作已实现或无缺口。

**用户可见后果**：区域冲突时只能看到并发冲突横幅 + typed 原因 + 「请重新读取并对照」的文字提示，无法并排比对冲突 region 的基底文本与对方草稿。

**重开条件**：① 用户要求冲突对照或列为发布前必做；② 出现第二个基底文本消费者（如 V2 Studio）；③ 真实多会话/外部工具编辑使区域冲突成为常见路径。重开时须先补「对照内容规格」（显示哪两层、字段、布局、交互），再走 C-07 additive UNFREEZE 载体 + 独立 byte-level 复核 + 重冻。

**Errata（更正卡面两处过期事实，wont-fix body bytes）**：
1. `RegionSummary` 行号已漂移：现为 `CoreServiceClient.cs:204-210`（非 `:172-178`）；冲突用例现为 `FluentResidualBatchATests.cs:642-670`（非 `:613-641`）。
2. 「术语/冲突面 NOT_WIRED（`StudioTermsViewModel.cs:36-62`）」是**范畴错误**——术语表冲突 ≠ 区域冲突，不能作为 region 对照的证据。
3. 补充更正：`list_page_region_texts` 在 Core 侧**已实现**（`src/bootstrap/core_service.py:3533/7787/7796`），注册与分发就绪（`HostCommandRegistry.cs:191/357/462-466`、`HostCommandDispatcher.cs:868-871`）；缺的只是 **App 侧端口**，不是数据面。

**保留**：本卡原 limitation、设计文档、`FEA-06-RESIDUAL-2` 的历史字节全部不动；`FEA-06-RESIDUAL-2` 的格 3 由本裁决转为 OUT，其卡面更新留待专门载体（未在本轮改）。

## RO-1 重开记录（append-only，2026-11-14）

**状态：`cancelled` → `proposed`。** 上一节 OUT 处置记录**整段原样保留**，本节为后续裁决，不删除、不改写任何历史字节。

**依据**：用户 2026-11-14 直接指令「继续 FEA 线收口，且重开卡走 C-07 UNFREEZE 路线」，命中 `MAINT-1-P4A-Q7-Q8-ADJUDICATION.md:38` 的推翻条件与本节 `:59` 重开条件①。完整裁决见 [`MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md`](../reviews/MAINT-1-RO-1-REOPEN-RESIDUAL-4-2026-11-14.md)。

**路线（固定）**：规格冻结 → C-07 additive UNFREEZE（独立字节级复核 + 重冻 + pin 重算）→ App 端口 + UI 对照面板 + 判别测试 → 独立 Review + 集成验证。

**拆卡**：

- `FEA-06-RESIDUAL-4A`（契约前置）：对照内容规格 v0 → v1 冻结；`IHostController` 增 `ListPageRegionTextsAsync`（79→80 / 86→87）；`generate_api_inventory.py` 重跑；C-07 pin 重算；UNFREEZE 载体；独立 byte-level 复核；重冻。
- `FEA-06-RESIDUAL-4B`（实现）：HostController/NullHostController/Fake 实现 + RegionBox 对照面板 + 判别与负向测试；复用既有 `WithoutFabricatedCompare` 不变量，不得削弱。

**未变的事实**：`FEA-06` AC3 仍为 **PARTIAL**，直到 4B 集成验证通过；本卡当前仍是**占位卡**，`scope 未冻结，不得实施**（原 `approval` 行继续有效）。

**下一步**：由 DSH 释放 4A（scope 冻结 + 允许路径 + 预算登记），Owner 建议 Codex/ZCode，独立 Review 由未参与实现的上下文执行。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| none | - | NOT_APPLICABLE | - | - | 本卡为占位提案，从未实施（`proposed` 直接处置为 `cancelled`），无 task-env、无派生产物；2026-11-14 DSH 复核 |

## 收口（2026-11-14，DSH）

**`status: superseded`** —— 本占位卡由 RO-1 拆出的两张子卡取代，均已 `done`：

| 子卡 | 内容 | 终态 |
|---|---|---|
| `FEA-06-RESIDUAL-4A` | 对照内容规格 v1.1 + C-07 additive UNFREEZE v1.9（预授权）+ 独立复核 r2 approved | `done`（`3519664d3`） |
| `FEA-06-RESIDUAL-4B` | 四刀实现（wire → 端口 → 统计翻转 pin v1.10 → UI）+ 独立复核 approved | `done`（`16209b0df`） |

**取代语义**：本卡原「占位/未 scope 冻结」状态不再有效；实现与验收证据见两张子卡与 `verification/FEA-06-RESIDUAL-4A|4B/`。`FEA-06` AC3 的「冲突态缺查看对照」子项已关闭（AC3 整体仍 PARTIAL）。