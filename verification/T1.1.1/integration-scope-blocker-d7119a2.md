---
task_id: T1.1.1
kind: integration_gate_blocker
owner: Codex
status: blocked
declared_master_head: 94ab0d3
observed_master_head: d7119a2
author_head: 4a631355
candidate_merge: f56f441
---

# T1.1.1 Integration Gate — Scope Blocker

## Observed repository state

任务给定 master `94ab0d3`，实际开始预检时 master 已前进到
`d7119a2669004d233832cc0e4b9877f2e51bde93`。`94ab0d3..d7119a2` 只有
`wiki/codewiki/**` 双语文档变更，没有产品代码或 T1.1.1 文件变化；该提交和主工作区
既有 dirty 文件均保留。

作者 worktree 核对结果：

- path: `G:\CODEX\New Manga.worktrees\T1.1.1-production-text-detector`
- branch: `agent/zcode/T1.1.1-production-text-detector`
- HEAD: `4a631355316e959e9a9704f1ead2eaed39cbf7a3`
- status: clean

## Blocking scope conflict

本次 Integration Gate 的收窄清单只列出 `detection_doctr.py`、requirements、
`tests/providers/test_detection_doctr.py`、`verification/T1.1.1/**` 和 Handoff，
但没有授权：

- `src/bootstrap/app.py`
- `tests/providers/t111_support.py`
- `tests/providers/test_detect_seam_t111.py`
- `tests/providers/test_detection_doctr_real.py`
- `tests/providers/test_detector_assembly.py`

正式 [T1.1.1 Task](../../doc/tasks/T1.1.1.md) 的 allowed paths 则明确允许：

- `src/bootstrap/app.py` 的最小 detector 构造/注入变更；
- `tests/**` 的 adapter、bootstrap、SQLite seam 和 source-protection tests。

这些不是可选文件：当前 master 的 `src/bootstrap/app.py` 仍为
`detector=None`；若只集成本次收窄清单，生产 detector 不会连通，无法满足
T1.1.1 的 production bootstrap acceptance criterion。

## Reproducible candidate state

在隔离 worktree
`C:\Users\49745\.codex\worktrees\t111-codex-integration\New Manga`
以实际 master `d7119a2` 创建 `agent/codex/T1.1.1-integration`，保留原始 ZCode
提交历史并执行：

```powershell
git merge --no-ff --no-edit agent/zcode/T1.1.1-production-text-detector
```

生成候选 merge commit `f56f441`。其 diff 明确包含上述 bootstrap 与 seam/real
tests；该候选尚未合并到 master，未执行集成后验证，也不构成批准状态。

## Decision

当前不能在不违反最新收窄 allowed paths 的情况下完成 T1.1.1 集成。保持：

- master product state 不变；
- `T1.1.1` 不标记 `INTEGRATED` 或 `VERIFIED_COMPLETE`；
- ZCode 分支和隔离 integration worktree 保留；
- 不执行 `git reset --hard` 或 `git clean -fd`。

待用户/Codex 明确授权将正式 Task 的最小 bootstrap seam 与 T1.1.1 全部测试纳入本次
integration scope 后，才能继续 fresh integration verification。
