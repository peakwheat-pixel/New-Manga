# M2-TA1 Integration Verification

- Date: 2026-09-29
- Integration merge: `1ef8fe7e7e66044869f8c59646d28bfca7692bbe`
- First parent / base: `40ce1f91cc41a8ed13e10e397fe0ddab43d9f5be`
- Second parent: `b72f865b234943b6b075f36d72ede527d0cb74c7`
- Reviewed implementation: `00df8f1dd4d480d4e4432c833981481f2c01dd3e`
- Independent Review: [M2-TA1-codex](../../doc/reviews/M2-TA1-codex.md), `approved`.

## Integration result

The approved test-only asset foundation merged without conflicts. The main checkout had pre-existing user modifications and untracked files; their status was captured before integration in `main-worktree-preexisting-status.txt`. The 30 feature paths had zero overlap with the pre-existing dirty paths. No pre-existing file was staged or committed by this Task.

The branch's ignored KO smoke media was copied into the integrated main checkout. Source and target each contain 80 files / 884,913,245 bytes; relative path names and individual file lengths match. All 10 KO cases validate as `READY` after the copy. The destination was absent before copy, and the copy command refused to overwrite any existing destination.

## Post-integration verification

| Check | Result |
|---|---|
| `python -m pytest tests/m2_test_assets -q` | PASS: 10 passed, EXIT=0 |
| KO `assets.py verify --language ko --level smoke` | PASS: READY=10, EXIT=0 |
| KO repeated explicit `download` | PASS: downloaded=0, existing=80; no duplicate files, EXIT=0 |
| JA explicit `download --language ja --level smoke` | PASS: 10 `BLOCKED_BY_ASSET_ACCESS`, downloaded=0, EXIT=0 |
| JA/KO `list --level smoke` | PASS: 10 KO READY + 10 JA MISSING_GATED_ASSET, EXIT=0 |
| Git media tracking / ignore | PASS: 7 suite metadata paths tracked, 0 image/archive files tracked; KO/JA image paths match local `.gitignore`, EXIT=0 |
| `git diff --check 40ce1f91..1ef8fe7e` | PASS, EXIT=0 |
| `python -m pytest tests/m2_acceptance -q --tb=no` | `BASELINE_FAILURE`: 8 failed / 24 passed / 3 skipped, EXIT=1; same 8 failed test names as base and Task delivery |

Environment and raw output: `post-integration.log`, `post-integration-acceptance.log`, `asset-copy.log`. External-source HEAD checks: `asset-url-head-check.log`.

## State after integration

- KO Webtoon: `READY` locally; images are ignored by Git.
- Manga109: `BLOCKED_BY_ASSET_ACCESS`; no approved archive, actual archive import `NOT_RUN`.
- JMangaBench usable image set: `BLOCKED_BY_ASSET_ACCESS` (Manga109-s images not acquired).
- COO and Manga109Dialog: `PARTIAL` (annotation sources registered; gated images absent).
- Text Mask: `MISSING` (not downloaded; source image redistribution rights unresolved).
- Open Ground Truth / Pepper&Carrot pages: `MISSING` locally (8 source cases registered; pages not downloaded).
- L0 pipeline run, L1 benchmark execution and L2 benchmarks: `NOT_RUN`.

**Integration Gate: PASS** for the authorized asset-infrastructure scope. The inherited acceptance-suite failures, inaccessible gated assets, and application pipeline runs remain explicitly classified above and in the Task; they are not represented as passing.
