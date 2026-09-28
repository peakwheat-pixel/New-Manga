---
id: M2-AC2
title: Data Integrity Acceptance (source hash / Managed Copy / user edits / Lock / current & pinned Revision)
kind: acceptance
status: in_review
release_state: M2_AC2_DATA_INTEGRITY_RELEASED
approval: approved_by_user_2026-09-28_m2ac2_release
execution_approval: approved_by_user_2026-09-28_m2ac2_release
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
integrator: Codex
depends_on: [M2-IPC1, M2-P1]
base_commit: 61f9db9b54ae4b7420c7d1a5751cc040a502c88f
branch: agent/zcode/M2-AC2-data-integrity
worktree: G:/CODEX/New Manga.worktrees/M2-AC2-zcode
delivery_head: c3ee8dbebc860f67abd668301dc81ab78d917bac
review: doc/reviews/M2-AC2-375cf43b-dsh-r2.md (approved_with_conditions; C1-C3 closed by owner)
dispatch_state: DELIVERED_FOR_REVIEW
---

# M2-AC2 — Data Integrity Acceptance

## 目标

在 production 装配 + 真实 SQLite + 真实文件系统上，验收 [Rebaseline Plan](../REBASELINE_PLAN.md) M2 Acceptance Backlog 第 2 行的全部数据安全承诺：**source hash 完整性、Managed Copy 隔离、人工修改保留、Lock 与 current/pinned Revision 完整性、端到端恢复**。这是产品"保护用户源文件、人工修改、Lock、current/pinned Revision"核心主张的验收 Task（[AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md)）。

验收形态：纯 Python Core 层验收模块（`tests/m2_acceptance/test_data_integrity.py`），复用 M2-AC1 的真实装配手法（production assembly、临时 data root、真实进程级重启=重装配），**不扩 IPC 命令面、不走 test-mode bridge**。与 M2-P1 的单缺陷判别不同，本 Task 是矩阵化验收：每个承诺一个场景族，先证明语义存在，再证明破坏被拒绝/检出。

Owner=ZCode（本会话亲自实现）；非作者 Reviewer=DeepSeek Harness；Integrator=Codex（**新 ZCode 会话以 Codex 身份执行**，保持 Owner≠Integrator）。

## Acceptance Criteria

- [ ] **AC1 — source hash 完整性与源文件不可侵犯：** 导入后 `page.source_hash == sha256(源文件字节)`；导入全程源文件字节与 mtime 不变（Core 对源目录零写入）；同一文件按默认 `DuplicatePolicy.SKIP` 重复导入被拒且不产生第二个 page 或第二份 managed copy。
- [ ] **AC2 — Managed Copy 隔离：** `managed_original_ref` 指向 managed 根下真实文件且字节与源一致；删除/改名用户源文件后 Core 经 managed 副本照常读取（managed 是权威副本）；反向地，managed 文件缺失必须可检出（typed 错误或明确缺失状态），不得静默伪造内容。
- [ ] **AC3 — 人工修改保留：** `save_manual_translation` 产生 `manual_edited` revision 并自动置 `translation_locked`；锁定 Region 上的 pipeline OCR 结果只以 StepResultCandidate 呈现（不覆盖人工文本）；current 指针保持在人工版本。
- [ ] **AC4 — Lock 与 current/pinned Revision：** `page_locked → plan SKIP_LOCK`（无 StepRun）；`region_locked →` OCR `LOCK_CHANGED` 零写（复用 M2-P1 N2 判别口径）；`set_revision_pinned(True)` 的 revision 及其 artifact 文件在 `CleanupService.run()` 前后保持存在；`restore_revision` 后 current 指针正确指向恢复版本且产生新 revision 记录。
- [ ] **AC5 — 端到端恢复：** 同一 data root 重新装配（进程重启等价）后，source hash、Lock、pinned、current 指针、人工文本全部保持；既有 `recover_running_runs` 语义可从装配层触达。
- [ ] **AC6 — 证据纪律：** 所有命令记录 shell、解释器、固定 HEAD、EXIT；`FAIL`/`BLOCKED`/`NOT_RUN` 分开报告；提交 Handoff 与 delivery head；`git diff --check <base>..<delivery-head>` exit 0。

## 允许修改范围

- `tests/m2_acceptance/test_data_integrity.py`（新增）
- `doc/tasks/M2-AC2.md`、`verification/M2-AC2/**`、`doc/handoffs/M2-AC2-*.md`

## 禁止范围

- `src/**`、`apps/**`、`doc/contracts/**`：**纯验收 Task，产品代码零改动**。发现缺陷（如 managed 缺失静默、pinned 被清理等）时如实记录为 FAIL/BLOCKED 证据并停在该场景，由后续修复 Task 处理——验收不通过本身就是合法交付结果。
- SQLite schema/migration、依赖、打包、Legacy PySide6/QML、IPC 命令面扩展。

## 验证命令

在固定 worktree 根目录执行；`$py` = `G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`。

```powershell
& $py -m pytest tests/m2_acceptance/test_data_integrity.py -q
& $py -m pytest tests/m2_acceptance -q
git diff --check <base>..<delivery-head>
```

第二条确认新模块不破坏 M2-AC1 既有验收套件。

## 交付

- 验收模块 + 全部场景证据（Owner branch）
- Handoff：`doc/handoffs/M2-AC2-<short-head>.md`
- 非作者 Review（DeepSeek Harness）通过后由 Codex（新会话）集成。
