# M2-AC3 Release Evidence — release 319c5e4b

- Release commit: 本次治理 commit（即 `doc/tasks/M2-AC3.md` 首次登记 commit，父 commit = `319c5e4b`；实际 hash 见 `git log --grep "release(M2-AC3)"` 与 STATUS release checkpoint）
- Fixed base: `319c5e4b94fab4e43c8ec8c797c6545915ed7efa`（release 时 main HEAD；Task frontmatter `base_commit`）
- Approval: 用户 2026-09-28 转发释放指令批准（指令原文存档于本文 §4）
- Branch / worktree: `agent/zcode/M2-AC3-provider-fail-closed` / `G:/CODEX/New Manga.worktrees/M2-AC3-zcode`（从 release commit 检出，创建时干净）
- Roles: Owner=ZCode / 非作者 Reviewer=DeepSeek Harness / Integrator=新会话代行 Codex（Owner≠Integrator 保持）
- Depends_on: M2-AC2（`done` @ integration `9d3c1db5`，收口 `319c5e4b`）

## 1. 登记内容

- [Task](../../doc/tasks/M2-AC3.md)：Provider Fail-closed Acceptance——production 装配 + 真实 SQLite 上验收 Provider 未配置/网络失败/部分失败时命令计划与页面的 fail-closed 语义（不产出半成品成果、typed 错误可诊断、可恢复、源文件零风险）。纯验收，产品代码零改动；发现缺陷只记 FAIL/BLOCKED 证据。
- Allowed paths：`tests/m2_acceptance/` 新增文件、`doc/tasks/M2-AC3.md`、`verification/M2-AC3/**`、`doc/handoffs/M2-AC3-*.md`。
- 验证命令：Task §测试要求（两级 pytest + `git diff --check`）。
- AC 锚点经代码核对：`PipelineError`（`models.py:150`）、`ProviderNotConfigured`/`ProviderUnavailable`（`registry.py:246-253`）、`PROVIDER_NOT_CONFIGURED` slot（`handlers.py:234`）、`COMPLETED_WITH_FAILURES`（`models.py:96`）。
- 同批登记 proposed / NOT_RELEASED 候选：[M2-FIX-STUB-DECODER](../../doc/tasks/M2-FIX-STUB-DECODER.md)（M2-AC2 集成遗留的 core_service stub decoder 签名缺陷，ImportPages 扩面前置，未释放禁止实施）。

## 2. 释放时核验

- main HEAD = `319c5e4b`（M2-AC2 收口 commit），治理文档 clean、无 STATE_CONFLICT（REBASELINE 盘点 2026-09-28 实证）。
- 无 `in_progress`、无其他 `ready` Task 争用；worktree 名未被占用（`git worktree list` 核验）。
- 本 Task 为登记释放：release commit 仅含 Task/evidence/治理文档，**零验收代码**（Owner 认领后才实施）。

## 3. M2 Acceptance Backlog 状态

| 行 | 内容 | 状态 |
|---|---|---|
| 1 | M2-AC1 端到端验收 | done @ `f162193b` |
| 2 | M2-AC2 数据完整性验收 | done @ `9d3c1db5` |
| 3 | **Provider fail-closed acceptance** | **本 Task `ready`（已释放）** |
| 4 | Reader lineage + Library page-count | backlog 未登记 |
| 5 | Package / clean-start | backlog 未登记 |
| 6 | Real docTR qualification | backlog 未登记 |
| 7 | M2 Release Gate | backlog 未登记 |

## 4. 释放指令存档（用户转发原文）

> 你是 Codex（Lead/治理，代行身份，用户已全权授权）。在 G:/CODEX/New Manga（main @ 319c5e4b）执行：
> ① 按 doc/templates/TASK.md 起草 doc/tasks/M2-AC3.md：Provider fail-closed acceptance（M2 Acceptance Backlog 第 3 行），纯验收 Task：production 装配 + 真实 SQLite 上验收 Provider 未配置/网络失败/部分失败时命令计划与页面的 fail-closed 语义（不产出半成品成果、typed 错误可诊断、可恢复、源文件零风险）；产品代码零改动，发现缺陷只记 FAIL/BLOCKED 证据。Owner=ZCode，非作者 Reviewer=DeepSeek Harness，Integrator=新会话代行 Codex（保持 Owner≠Integrator）。depends_on=[M2-AC2]；base=319c5e4b94fab4e43c8ec8c797c6545915ed7efa；branch=agent/zcode/M2-AC3-provider-fail-closed；worktree=G:/CODEX/New Manga.worktrees/M2-AC3-zcode。Allowed paths 只允许：tests/m2_acceptance/ 新增文件、doc/tasks/M2-AC3.md、verification/M2-AC3/**、doc/handoffs/M2-AC3-*.md。同步登记 M2-AC2 集成遗留的 core_service stub decoder 缺陷为 proposed 候选。
> ② 写 release evidence 到 verification/M2-AC3/release-319c5e4b.md，更新 STATUS/REBASELINE_PLAN/00_INDEX/doc/tasks/README，提交治理 commit 并汇报可转发给 Owner（ZCode）的开工指令。
> ③ 不实施任何验收代码；登记释放完成后停止，等 Owner 认领。
