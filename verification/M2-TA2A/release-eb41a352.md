# M2-TA2A Release Record

- Released: 2026-09-29 (Asia/Shanghai)
- User authorization: current request explicitly asks Codex to plan/release M2-TA2A and continue without another permission step.
- Base: `eb41a352c03df84400d90a78c29d2dfbe28a76c9`
- Owner: Codex Desktop (executing this released task)
- Reviewer: DeepSeek Harness, non-author
- Integrator: Codex Desktop
- Branch: `agent/codex/M2-TA2A-ja-public-assets`
- Worktree: `C:/Users/49745/.codex/worktrees/comic-test-assets/New Manga`, reused from completed M2-TA1 after checking clean tracked state; 80 ignored KO files were preserved.
- Dependency: M2-TA1=`done` at integration `1ef8fe7e`; no other active task.

## Frozen scope

Acquire and verify lawful public JA assets, distinguish annotations/code from actual image data, record per-source file counts/bytes/hashes/license/redistribution/ground-truth/pipeline scope, retain gated Manga109-dependent resources as blocked or partial, and keep all raw media out of Git. No production Schema/migration/Pipeline/Provider/dependency/UI changes.

## Parallel work

Read-only source audits ran independently for Manga109/JMangaBench/COO/Manga109Dialog and for Text Mask/open Japanese-language comics. After license checks, local downloads may proceed concurrently only into distinct source directories. Manifest, README, status and final inventory integration remain serial under Codex.

## Baseline boundaries

- `tests/m2_acceptance`: existing `8 failed / 24 passed / 3 skipped`, previously proven `BASELINE_FAILURE`; not a blocker for this asset-only Task.
- `tests/core`: existing PySide6 collection failures, `BLOCKED_BY_ENV`; not a blocker for this asset-only Task.
- Application-level OCR/Detection/Translation/Inpainting/Typesetting/Webtoon pipeline: `NOT_RUN` unless explicitly run as a separate authorized product verification.
