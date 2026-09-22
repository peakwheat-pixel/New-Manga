# V2 Project Control Baseline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. This plan is for the Codex-led audit and governance baseline; it does not authorize product feature development.

**Goal:** Complete the modified V2 project-wide audit and establish the smallest agent-neutral, evidence-backed control baseline that can survive an executor change.

**Architecture:** Reuse the repository's existing authoritative documents: `AGENTS.md` for entry rules, `doc/REBASELINE_PLAN.md` for sequencing and dependencies, `doc/STATUS.md` for live state, Task/Handoff/Review files for task facts, and `doc/AI_COORDINATION.md` for knowledge-layer ownership. Store detailed audit evidence in one dated verification report and keep maps/status as derived summaries. No second status machine, product feature work, schema change, or parallel global-state writer is introduced.

**Tech Stack:** Markdown, Git, PowerShell, Python 3.12 project environment, pytest, compileall, application smoke test, RepoWiki/CodeWiki derived knowledge already present in the repository.

**Spec:** User-provided modified V2 project-wide audit, task governance, and multi-agent sustainability instruction; repository-native rules in `AGENTS.md` and `doc/09_COLLABORATION.md` take precedence.

## Global Constraints

- `PROJECT > TASK > EXECUTOR`; executor identity is replaceable.
- Reality is established from source, tests, Git, runtime evidence, then documents and derived maps.
- `REBASELINE_PLAN.md` is the planning source of truth and `STATUS.md` is the live execution checkpoint.
- Do not create duplicate `CURRENT_STATE`, `PROGRESS`, `TASK_GRAPH`, or project-map systems when existing documents can hold the role.
- Preserve unrelated dirty files and worktrees; do not reset, clean, stash, delete, or modify user data.
- This plan performs audit/control work only; T1.2.1 product repair remains separately released and must not be started by this plan.

## Review Focus

- Stale completion claims versus integrated commits: every completed claim must name code, test, Git, and verification evidence.
- Current T1.2.1 review blockers versus its formal Task scope: the five R3 blockers remain blocked until a new author head and review.
- Derived RepoWiki/CodeWiki freshness versus source HEAD: stale knowledge is reported, not treated as implementation truth.
- Dirty worktrees and untracked material: inventory is preserved and never used as a baseline without a clean-state check.
- Test-environment differences: passed, skipped, known environment failure, and NOT_RUN remain separate.

## Task 1: Reality inventory and evidence

**Files:**
- Read: `AGENTS.md`, `doc/00_INDEX.md`, `doc/REBASELINE_PLAN.md`, `doc/STATUS.md`, `doc/09_COLLABORATION.md`, `doc/AI_COORDINATION.md`, `doc/11_ARCHITECTURE_MAPS.md`, `doc/WORKTREE_SAFETY_INVENTORY.md`, all current Task/Handoff/Review evidence.
- Inspect: `src/**`, `tests/**`, `wiki/repowiki/**`, `wiki/codewiki/**`, Git branches/worktrees/status/history.
- Create: `verification/PROJECT-AUDIT-2026-09-22.md`.

- [x] Record repository rules, state-file inventory, Git/worktree reality, source/test map, task map, and evidence limits in `verification/PROJECT-AUDIT-2026-09-22.md`.
- [x] Run fresh collection, full tests, compile, and smoke checks where the current environment supports them; record shell, interpreter, exit code, skips, and failures.
- [x] Classify unknowns instead of inferring them from stale docs.

## Task 2: Minimal control baseline

**Files:**
- Modify: `doc/REBASELINE_PLAN.md`, `doc/STATUS.md`, `doc/11_ARCHITECTURE_MAPS.md`, `doc/09_COLLABORATION.md` only where the audit proves a current control gap.
- Do not create: a duplicate status file, a product task, a new schema, or a new executor-specific control system.

- [x] Add concise project overview, current position, maturity, dependency blocking chain, parallel-readiness matrix, and Task↔Code/Test evidence pointers to existing authoritative/derived files.
- [x] Add minimal rolling checkpoint/resume rules to the existing collaboration protocol.
- [x] Keep detailed findings in the dated verification report; do not duplicate every fact across multiple files.

## Task 3: Self-verification and closure

**Files:**
- Verify only: the files changed by Tasks 1–2 and their Git diff.

- [x] Check every report claim against current source, tests, Git, and evidence paths.
- [x] Run `git diff --check`, staged-path inspection, and final status/worktree checks.
- [x] Mark the audit/control baseline `READY_FOR_NEXT_EXECUTOR` only if its required evidence and recovery point are persisted; leave product tasks blocked where their own gates remain open.

## Completion gate

The plan is complete when the dated audit report and existing control documents answer the V2 questions, the current dashboard names TaskStatus and ExecutionState separately, the blocking chain and parallel matrix are evidence-backed, the next executor can resume from a fixed path/HEAD, and no product feature Task was auto-started. This gate is met; CodeWiki freshness remains a recorded follow-up because the source metadata is stale and the incremental run was stopped after no progress.
