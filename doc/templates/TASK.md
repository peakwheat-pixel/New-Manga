---
id: TASK-xxx
title: 待填写
kind: design
governance_version: 2
status: proposed
approval: pending_user_review
suggested_owner: Codex
owner: null
reviewer: null
depends_on: []
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/TASK-xxx
---

# TASK-xxx：任务标题

## 来源与目标

需求文件/章节/AC ID、当前代码或测试证据；一个可观察的交付结果。不存在的代码路径必须标为拟议路径。

## Acceptance Criteria

- [ ] 具体前置条件、动作、预期结果及对应证据。
- [ ] 每项必要 AC 有实际验证记录，未跑项明确标 NOT_RUN/BLOCKED。

## 允许修改范围

- 明确相对项目根目录的文件/目录；共享接口、Schema、依赖变更单列。
- 本 Task、自己的 Handoff、经分配的测试/verification 路径。

## 禁止范围

写明非目标、依赖方模块、用户原始数据；范围扩大须先由 Codex登记。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| 必填 | 标注 planned，不伪装为已存在命令 | 必填 | NOT_RUN | 无 |

## 依赖、风险与阻塞

depends_on 必须是已存在 Task ID。区分硬依赖与可并行条件；记录未定契约及解除阻塞标准。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。
- 后续实际记录包含日期、commit、环境、结果、遗留项；最终由 Codex填写 integration_commit 并改 done。

## Canonical Evidence

进入 `in_review` 前，逐项列出已释放 AC/Gate 的唯一当前证据。仓库内文件 pin commit；仓外原始输入 pin SHA-256。不要把尝试日志全复制进本表。

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

记录 Task 产生或使用的 worktree、task-env、dataset/model/test-material、artifact、temp、agent-output 和 exchange。`NOT_APPLICABLE` 也要明确记录。路径、来源和关闭 disposition 以证据为准。

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|

允许 disposition：`DELETE_SAFE`、`MIGRATE`、`ARCHIVE`、`PRESERVE_REFERENCED`、`PRESERVE_USER_DATA`、`PRESERVE_UNKNOWN`、`NOT_APPLICABLE`。未知、dirty、unique、pinned 项不得删除。Worktree 必须另外通过当前 Worktree Safety Inventory 的检查。

## Closeout Record

- Closeout date / Codex：待关闭时填写。
- canonical_evidence_status：`pending` / `complete`。
- resource_closeout_status：`pending` / `complete`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：无则填写“无”。
- 当前指针清理：STATUS / Plan / Task 导航 / rolling checkpoint 已更新，或说明无需更新。
