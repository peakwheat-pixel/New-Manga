---
id: FEA-11-HOST-AUTH-3
title: 跨进程崩溃恢复的 grant 语义（原 FEA-11-HOST-AUTH-2 AC-F3）+ limitation 3/4（C-17 UNFREEZE 类）
kind: implementation
governance_version: 3
status: proposed
approval: 占位卡：由 `FEA-11-HOST-AUTH-2` Review r1（R1-P2-1）与 DSH 2026-11-08 裁决 re-home；**scope 未冻结，不得实施**；须先独立 scope review
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
