---
task_id: GOV-PLAN-BUDGET-1
author: dsh
recipient: Codex
base_commit: 960188271d62bf40db4b3646b6fa02ab869bade0
delivery_head: 126f9f31c857a728c5818b01aab91071dc7ed273
status: ready_for_review
---

# Handoff：GOV-PLAN-BUDGET-1

## 交付结果

按用户裁决 1（Plan 预算 2500/35 → 7000/64）与 Codex r5 的范围冻结，把检查器中 `doc/REBASELINE_PLAN.md`
的预算上限改为 **7000 bytes / 64 lines**。

实际改动**只有一行**：

```diff
-    @{ Path = 'doc/REBASELINE_PLAN.md'; Bytes = 2500; Lines = 35 }
+    @{ Path = 'doc/REBASELINE_PLAN.md'; Bytes = 7000; Lines = 64 }
```

`doc/STATUS.md` 的预算项（`3200 / 45`）未动，比较与 warning 逻辑未动，文件行尾保持 275 LF / 0 CRLF。

提交：`126f9f31c`（本 Task 唯一实现提交）。基线 `960188271` 是首次把 checker 纳入版本控制的提交。

## 验证证据

| AC | 实际命令/步骤 | 结果 | 证据 |
|---|---|---|---|
| AC1 只改目标预算项 | 读取 L127 并替换；断言 STATUS 项仍存在且仅 1 次 | **PASS**：diff 1 行，STATUS 项未改 | `ac1-ac3-budget-and-boundary.md` |
| AC3 边界 fixture | 在隔离 worktree 内用精确大小的 Plan 覆盖 → 跑真实 checker → 从备份恢复 | **PASS**：7000/64 仅 WARN；7001 与 65 行均 FAIL；80% 阈值移至 5600 bytes | 同上 |
| AC4 治理输出 | `check.ps1` 全局 + `-TaskPath`，原始 stdout/exit 保存 | **记录在案**：worktree 初建时报 7 errors，其中 6 个是环境性的；补齐后为 **1 error** | `ac4-governance-output.txt` |
| AC2 范围遵守 | 未改 Plan / STATUS 指针 | **PASS** | 见下「未做」 |
| AC5 交接 | 本 Handoff + Antigravity Review | 进行中 | 本文件 |

## AC4 的那 1 个错误：不是本 Task 引入，也不是 Owner 该修

```
FAIL: READY DAG 只允许 status: ready；GOV-PLAN-BUDGET-1 当前为 in_progress
```

Task 被认领（`ready` → `in_progress`）后，Plan 的 READY 声明仍列着它。按本 Task **AC2**
「Plan/STATUS/导航仅由 Codex 维护生命周期指针」，此项由 Codex 更新，Owner 未擅自修改。

**另有一个环境性问题需要 Codex 知悉**：主 checkout 有 **33 个 `doc/` + `archive/` 下的文件
从未入库**（含 `doc/WORKSPACE_GOVERNANCE.md` 与整个 `archive/` 目录）。新建的隔离 worktree
看不到它们，检查器因此报「缺少当前治理入口」与 5 条「失效的本地引用」——这 6 个错误与本 Task
无关，是环境差异。我已把这 33 个文件镜像进 worktree（**未入库**）以复现主 checkout 的检查环境；
若不处理，**每个新建 worktree 都会撞上同样的假错误**。

## 明确未做

- 未修改 `doc/STATUS.md`、`doc/REBASELINE_PLAN.md`（AC2 划归 Codex）。
- 未改动检查器的比较条件、warning/error 逻辑或 STATUS 预算项。
- 未登记或修改 29 个被暂缓 Task。
- 未修改 `GOV-DEBT-CLEANUP-2` 的 approved 行。
- 未删除、移动任何资源；未执行 git 写命令于主分支。

## 接收方式

Reviewer：**Antigravity**（不得由 dsh 自审），针对固定 `delivery_head = 126f9f31c857a728c5818b01aab91071dc7ed273`。
请重点核对：
1. 是否真的只改了目标预算项（`git diff 960188271..126f9f31c -- tools/governance/check.ps1`）；
2. AC3 的边界结论是否成立（可自行构造 fixture 复跑）；
3. AC4 中「1 个真实错误 + 6 个环境性错误」的归因是否正确。

Review 通过后交 Codex：更新 Plan 的 READY 指针、集成、更新 `integration_commit`、closeout。
