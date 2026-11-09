---
id: FEA-11-HOST-AUTH-3
title: 跨进程崩溃恢复的 grant 语义（原 FEA-11-HOST-AUTH-2 AC-F3）+ limitation 3/4（C-17 UNFREEZE 类）
kind: implementation
governance_version: 3
status: blocked
approval: 占位卡 re-home（`FEA-11-HOST-AUTH-2` R1-P2-1 + DSH 2026-11-08 裁决）；独立 scope review r1 结论 **NEEDS_UNFREEZE**（`doc/reviews/FEA-11-HOST-AUTH-3-scope-r1.md`，head `461684432`）：真实跨进程恢复在冻结字节下不可达，唯一不破坏架构的载体 = **C-17 单 pin ADDITIVE_UNFREEZE**（路线 B + D-4 合批）；**未过 UNFREEZE 流程前不得实施**
suggested_owner: dsh
owner: null
reviewer: null
depends_on:
  - FEA-11-HOST-AUTH-2
base_commit: null
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
  - verification/FEA-11-HOST-AUTH-3/**
out_of_scope:
  - 未 scope review 前不得实施任何实现
---
# FEA-11-HOST-AUTH-3：跨进程崩溃恢复的 grant 语义（占位）

## 来源

`FEA-11-HOST-AUTH-2` 的 **AC-F3**（真实子进程 kill 后新进程恢复）被独立 Review 判 **架构阻塞**后，由 DSH re-home 到本卡；同卡还承接 `FEA-11-HOST-AUTH-1` 的 **limitation 3**（需「retry 命令」→ C-17 UNFREEZE 类）与 **limitation 4**（plan-read 命令 → UNFREEZE 类）。

## 已核实的阻塞事实（不得改写）

1. Core 的 source-read grant registry **仅进程内存**：`src/infrastructure/resource_channel/source_read_refs.py:106-121`（`SourceReadGrantRegistry(_grants: dict)`），`register` 要求 `expires_at ≤ now+300`（`:178-180`）。
2. C-17 **不允许省略 `grant_ids`**：锚点 `doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md:258`（六字段必填）与 `:276`（非缺失源不能为空）+ Core `src/application/sources/runtime.py:220-260`。
3. 因此：整树 kill（Host+Core 同死）→ 新 Core 无 grant → `_verify_fresh` 抛 `SOURCE_GRANT_EXPIRED`；`reattest.py` 不发放 sync grant；`SourceReadCoordinator.IssueAsync` 可造 grant 但 completion 只读 journal `GrantIds` 且 journal 无 source 定位数据。

## 候选路线（须由 scope review 定稿，禁止直接实施）

- (A) Core 侧 grant 持久化/重绑定（安全敏感：重放、TTL、撤销语义；可能需 C-15/C-17 解释或 additive）。
- (B) recovery 路径显式重发 grant：需 journal 扩展（source 定位）+ 新 Host 路径 + 可能 C-17 additive（UNFREEZE 类）。
- (C) 改崩溃口径为「Host-only kill + Core 外部托管」：stdio 下不可行，需新传输层。
- (D) limitation 3/4 的 UNFREEZE 载体（retry 命令 / plan-read 命令）。

## 验收（草案，待冻结）

- 真实进程 kill 后新进程恢复/ACK 成功一次、gate 全开、行数不变、幂等、`commit_digest` 一致；或（若走 UNFREEZE）契约载体 + 独立 byte-level 复核 + 重冻 + pin 重算。
- 不得以「同进程新 coordinator」冒充；不得伪造 PASS。

## Scope review 结论（2026-11-09，r1：doc/reviews/FEA-11-HOST-AUTH-3-scope-r1.md）

- **verdict：NEEDS_UNFREEZE**。阻塞事实 1/2/3 均成立，但卡面三处须改写（以报告为准）：
  1. **错误码纠正**：整树 kill 后新进程 resolve 抛 **SOURCE_ACCESS_DENIED**（"source-read grant is not registered"，source_read_refs.py:855-861），**不是** SOURCE_GRANT_EXPIRED（该码仅用于「已注册但过期」/「注册窗口非法」）；报告已实测复现。
  2. **最省载体**：不是「journal 扩展」，而是**新增一条只读计划物化投影命令**——Core 已把 PlanBody 持久化在 source_sync_plans.body_json，读回成本极低；Host 侧现有路径缺 ersion_id/ntries。
  3. **limitation 3（retry 命令）与 AC-F3 无因果关系**，应拆出本卡（否则一张可单 pin 的卡被拖成多 pin UNFREEZE）；D-3 同理拆出。
- **推荐载体**：C-17 **单 pin ADDITIVE_UNFREEZE**（路线 B + D-4 合批）；A（grant 持久化/重绑定）与 C（改崩溃口径）需用户/架构裁决，本卡不建议。
- **阻塞条件**：UNFREEZE 流程（载体草案 → 独立 byte-level 复核 → 重冻 → pin 重算 → 复冻记录）未完成前，本卡不得实施。恢复条件：UNFREEZE 冻结记录落盘且 erify_pins 18/18 重新全绿。
- **本卡不构成**：不批准任何实现；不构成对卡面 pproval 的解冻。
## ZCode 裁决采纳（2026-11-09，`doc/reviews/ADJ-2026-11-09-ZCODE-ARCH-ADJUDICATION.md`）

| 项 | 裁决 |
|---|---|
| 载体 | **B + D-4 合批，C-17 单 pin ADDITIVE_UNFREEZE**（新增只读计划物化投影命令，读回 Core 已持久化的 `source_sync_plans.body_json`；不新增披露面、零写、无 schema/migration；C-17 v1.1 有同型 additive 先例） |
| A（Core grant 持久化） | **ARCHITECTURE_BLOCKED**：抵触 C-15:304 / C-16:224 / C-06:40/42 / C-17:266；签钥随载荷 → 落盘即可重签材料 |
| C（Host-only kill） | **ARCHITECTURE_BLOCKED**：语义+传输双阻断（C-16:24/224、C-06:42；已实现 `source_read_refs.py:253-260`） |
| D-3（retry 命令） | **out_of_scope**（无消费者） |
| R-01 | 期望码 **`SOURCE_ACCESS_DENIED`**（非 `SOURCE_GRANT_EXPIRED`），须落进 AC |
| R-03 | 另立缺陷卡（契约允许全缺失源空 `grant_ids` 但 Core 拒绝、分支不可达） |

**恢复条件（当前仍 blocked）**：C-17 UNFREEZE 程序完成（载体草案 → 独立 byte-level 复核 → 重冻 → pin 重算 → 复冻记录）且 `verify_pins` 18/18 重新全绿。

**风险（裁决附带）**：新只读命令须 host-only + closed shape + wirelog 脱敏断言；崩溃注入须断言 Python sidecar 确被杀（否则记 NOT_RUN，不得冒充 PASS）。
