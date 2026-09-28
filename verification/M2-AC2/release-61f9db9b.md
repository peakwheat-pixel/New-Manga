# M2-AC2 Release Record

- **Decision:** 用户批准释放（2026-09-28；"批准释放 M2-AC2"，采纳上轮建议分工 Owner=ZCode、Reviewer=DeepSeek Harness、Integrator=Codex 新会话）。
- **Task / state:** [`M2-AC2`](../../doc/tasks/M2-AC2.md), `ready / M2_AC2_DATA_INTEGRITY_RELEASED`。
- **Owner / Reviewer / Integrator:** ZCode（本会话亲自实现）/ DeepSeek Harness（非作者）/ Codex（**新 ZCode 会话以 Codex 身份**，保持 Owner≠Integrator）。
- **Dependency:** M2-IPC1=`done`（`04c1394a`）、M2-P1=`done`（`a174fb9c`）；M2 Acceptance Backlog 第 2 行（source hash / Managed Copy / user edits / Lock / current & pinned Revision）。
- **Fixed base (code freeze point):** `61f9db9b54ae4b7420c7d1a5751cc040a502c88f`。
- **Branch:** `agent/zcode/M2-AC2-data-integrity`；**Worktree:** `G:/CODEX/New Manga.worktrees/M2-AC2-zcode`（从 release commit 检出）。
- **形态:** 纯验收 Task——产品代码零改动；`tests/m2_acceptance/test_data_integrity.py` 矩阵化场景（AC1–AC5），验收不通过本身是合法交付结果（缺陷记录后另立修复 Task）。

## Release Gate

| Required field | Frozen evidence |
|---|---|
| Base | `61f9db9b54ae4b7420c7d1a5751cc040a502c88f`（代码面与 release commit 零差异） |
| Branch / worktree | 已固定于 Task frontmatter |
| Allowed paths | `tests/m2_acceptance/test_data_integrity.py`（新增）+ Task/Handoff/verification 路径 |
| Forbidden paths | `src/**`、`apps/**`、contracts、Schema、依赖、打包、Legacy QML、IPC 面扩展 |
| Acceptance Criteria | AC1–AC6 已冻结（验收矩阵 + 端到端恢复 + 证据纪律） |
| Verification commands | pytest 两级（新模块 / m2_acceptance 全套）+ `git diff --check` |
