# DSH Review Request — P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE R2

Reviewer: DeepSeek Harness (non-author). Owner: Codex. Read only the exact inputs listed below. Do not edit files, run commands, enumerate directories, or access paths outside this list.

Exact review inputs (21 paths; the pin manifest itself is listed and is the only self-excluded hash):
- doc/tasks/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE.md
- doc/handoffs/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE-R1.md
- doc/handoffs/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE-R2.md
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/input-freeze-r1.json
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/existing-pins-validation-r1.json
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/store-inventory-r1.json
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/candidate-trace-r1.json
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/pre-review-pins-r1.json
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/review-request-r1.md
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-review-r1.md
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/post-review-pins-r1.json
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-review-run-r1.json
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/codex-adjudication-r1.md
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/r1-commit-normalization-map-r1.json
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-probe-version-r1.log
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-probe-stdout-r1.log
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-probe-stderr-r1.log
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/dsh-probe-exit-r1.txt
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/checkpoint.md
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/review-request-r2.md
- verification/P02PRE-R1H-P2-1-EXTERNAL-HARNESS-TRACE/review-input-pins-r2.json

The exact target commit is supplied in the dispatch prompt and must be repeated as reviewed_head in your report. The manifest contains one entry for each of the other 20 paths, explicitly including the Task. It omits only review-input-pins-r2.json itself to avoid a self-referential hash. Codex will independently verify every declared size/hash against this frozen worktree before and after review.

Review these points:
1. Confirm the manifest has 20 unique entries, includes the Task file, and omits no listed exact input except its own self hash.
2. Confirm the Codex adjudication resolves R1 P2-1 without changing the bounded search result or H1/P2-1/X6 states.
3. Confirm the R1-to-commit hash map accurately describes the documented line-ending normalization and explicitly preserves R1 identity limitations rather than overstating them.
4. Confirm the R1 P3 dispositions, probe evidence, path boundaries, and user-source preservation are sound.
5. Confirm the only supported search conclusion remains NO_PRECISE_STORE_PATH for the immediate-child inventory; do not infer no source exists elsewhere.

Return APPROVED_STATIC_CONTENT or CHANGES_REQUESTED, severity counts, exact path/line findings, scope and limitations, and whether any repair is required. This is a static evidence-package review only. Do not rerun any search, inspect credentials or unrelated data, or make implementation/runtime claims.