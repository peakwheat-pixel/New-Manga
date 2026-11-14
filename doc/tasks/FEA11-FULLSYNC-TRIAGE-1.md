---
id: FEA11-FULLSYNC-TRIAGE-1
title: 归因 2 个 FullSyncChain 失败 —— 种子缺 pixel 证据，产品行为正确
kind: evidence
governance_version: 3
status: done
disposition: "SCHEMA-VERSION-ASSERT-1 修复后残留的 2 个失败：new container must produce a changed page"
approval: DSH 2026-11-15
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - SCHEMA-VERSION-ASSERT-1
base_commit: 003ba5fb3
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/FEA11-FULLSYNC-TRIAGE-1
allowed_paths:
  - doc/tasks/FEA11-FULLSYNC-TRIAGE-1.md
  - doc/reviews/FEA11-FULLSYNC-TRIAGE-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-3-MATRIX-2026-11-15.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/FEA11-FULLSYNC-TRIAGE-1/**
---

# FEA11-FULLSYNC-TRIAGE-1

## 结论（一句话）

**产品行为正确，缺陷在测试基础设施**：种子库的旧侧条目缺 pixel 画像 ⇒ matcher 按 C-17 §7.3 row 4
**拒绝伪造旧证据**，诚实降级为 `ambiguous / missing_old`；而测试断言要求 `changed >= 1`。

## 证据链

1. **失败点**：`Fea11SourceIpcTests.cs:241` 的 `changed >= 1`。
2. **实测 totals**：`{"unchanged":0,"added":0,"missing":0,"changed":0,"ambiguous":1}`。
3. **决定性字段**：`"evidence":"missing_old"`、`"classification":"ambiguous"`。
4. **代码依据**：`src/application/sources/matcher.py` 的 `if not _pixel_present(old): classification = "ambiguous", evidence = "missing_old"`，
   注释明写 "v7-era row … never forge the old profile from the new image (C-17 §7.3 row 4)"。
5. **种子根因**：`tests/fea11/support/ipc_seed.py` 的 `old_entries` 只给 3 元组（无 pixel），
   虽然传 `legacy_v7_evidence=False`，但缺数据时 `add_source_tree` 只能写 v7-era 行。

## 为什么不能改断言

`changed + ambiguous >= 1` 会把"无法验证"当成"已验证"，属**放宽**，纪律禁止。
正解是让种子提供 pixel 画像，**未实施**（属测试基础设施改造，需单独冻结范围）。

## 未做

- 未改种子、未改断言、未改产品代码。
- `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_…` 为同族失败，未单独复跑确认，
  但错误文本相同（同一断言 + 同一 `missing_old` 机制）。**如实标注：只确认了一个的直接证据。**
