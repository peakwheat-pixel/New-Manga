# P09 integration 落盘意图（Coordinator lease 阻止）

日期：2026-10-19

## 本轮守卫结果

`coordinator-lease.py guarded-write` 使用 `agent=codex`、`epoch=8` 和当前 lease id 检查 `doc/STATUS.md` 时返回 `STALE_COORDINATOR`：运行时持有人是 `dsh@8`。未修改任何治理文件。此记录仅固定待有效 Coordinator 落盘的意图，不改变 Task、Plan 或 STATUS 权威状态。

## 建议由持有 lease 的 Coordinator 落盘

1. `P09-AC3-DELETE-HARDEN-1`：设为 `closed_with_limitations`，明确其未集成；保留 `integration_commit: null`。Plan 对应节点改为相同终态。
2. `P09-PREVIEW-LIFECYCLE-RECLAIM-1`：将 AC6 统一记录为未满足、证据状态 `NOT_VERIFIED`，无 `N/A`、无豁免；依 AC6 裁决将 Task 设为 `closed_with_limitations`，明确未集成并保留空集成提交。Plan 与 STATUS 移除其 `in_review` 指针，并记录该限制。
3. 所有记录均保持 `P09` AC3 delete 子条件为 `BLOCKED`。不得把 HARDEN-1 的 Review `approved` 写成已集成。
4. 预览分支当前已在 `49329f9b3d1f5d18e3a321f464ecff9323889c45`，`delivery_head` 仍为 `392977a83cc496206728ad26dded96274ead41dc`。不再追着本轮文档提交重复快进；后续分支落后于记录文档提交可接受，且快进不代表集成。

## R23 记录政策

协作协议要求当前 Review 指针可由仓库中的 canonical evidence 引用，因此 R23 应属于版本化项目审查记录。本目录的 `codex-review-r23.md` 保存了来自 workspace 的审查结果；其 `reviewed_head` 为 `df30b9d30498fda0701aee0a56b7b2b230514733`，该提交经 Git 验证为当前预览分支 tip `49329f9b3d1f5d18e3a321f464ecff9323889c45` 的祖先。R23 仅确认 Owner 半，不代表 Codex 集成或任务终态已落盘。

## 状态

以上为待处理意图，不是 Task 关闭记录，也不代表集成、技术 Gate 通过或任何验收项变更。Coordinator lease 持有人可在重新核对当前仓库状态后落盘并运行治理检查。
