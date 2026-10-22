# Antigravity continuation: P02 Stage A r5 corrections

Continue the existing P02 Owner conversation `054911c9-b133-4514-b471-143b80249fce`. This is an authorized continuation of the already frozen P02 implementation task, not a new scope freeze.

## Fixed context

- Repository: `G:/CODEX/New Manga`
- Owner worktree: `G:/CODEX/New Manga.worktrees/P02-real-webview-harness-antigravity`
- Branch: `agent/antigravity/P02-real-webview-harness`
- Current reviewed HEAD: `cc1bd7505f3fc48079db7ea2719040e77a8c58dd`
- Current tree: `d2569f6c4854c05e18cf22fa363397525962eec8`
- Diff base: `5de8d44c784cbd20b23bcd41a8f1a7258c7addff`
- Frozen P02 scope/allowlist SHA-256: `27DC31A8CF3304ABA6783E243F36895FFE4AAA3CCBCA76D58E8B766C403E1425`
- P02 remains `in_progress / ACTIVE`; `integration_commit: null`.
- Do not redo P01, change P02 requirements, re-freeze scope, alter shared contracts/dependencies/product implementation, or broaden the allowlist. Read the current P02 Task, `RESUME.md`, collaboration protocol, and existing Handoff before editing. Make changes only in the already authorized P02 paths.

## Review inputs

- Formal non-author DSH report: `G:/CODEX/New Manga/verification/P02/implementation-stage-a-r4-dsh-review.md` (`changes_requested`, P0/P1/P2/P3=`0/0/3/8`).
- Codex independent corroboration: `G:/CODEX/New Manga/verification/P02/r4-codex-independent-review.md`.
- Exact replay: `G:/CODEX/New Manga/verification/P02/r4-clean-commit-validation.md`.
- Codex's exact TypeScript output: `G:/CODEX/New Manga/verification/P02/r4-codex-tsc-exact.stdout.log` (TS2556 at line 164, process exit 2).

## Required disposition

Address each applicable DSH finding R4-01 through R4-11 within the existing scope and record a precise disposition for every ID in Task/Handoff/RESUME:

- R4-01: fix the `TS2556` tuple/spread failure and add a runnable focused type check for the E2E protocol file using existing tooling only.
- R4-02: validate `sfx_policy` and `origin` against the exact closed wire enums in `apps/desktop/frontend/src/region/types.ts`; valid values include `manual`, `imported`, and `restored` as defined by the source types, and invalid values must not pass.
- R4-03: restructure finalization so reported artifact hashes correspond to the final bytes of the current run after the PowerShell log is flushed. Do not claim hashes for artifacts that cannot yet be final; avoid self-referential report hashing.
- R4-04: freshness must account for exact execution inputs/current dirty state (or otherwise prevent same-HEAD stale PASS reuse); missing child `exit_code` must remain unverifiable rather than be synthesized from status.
- R4-05: make PRE-02 self-check exercise the real report-consumption path and compute `report_freshness_verified` from observed results rather than a constant.
- R4-06: persist the exact failed command, output, and child exit status on thrown PowerShell paths. Do not claim PS 5.1 behavior was executed unless it was.
- R4-07: fail closed or explicitly report unverified fallback if authoritative enum source parsing fails; never silently call hard-coded values authoritative.
- R4-08: count and record mutation groups actually executed/skipped; only claim all four were rejected if all four ran and were rejected.
- R4-09: make `large_text` obey the frozen Task threshold for text (`>=4.5:1`) or remove the unused role; do not loosen the product requirement.
- R4-10: prevent a pre-`try` probe failure or interruption from leaving an old PASS log looking current; accurately label each run's start/finalization state.
- R4-11: accept nullable `page_count` as permitted by the source contract and validate bbox/polygon values against the existing wire shape.

Clarify the historical review-ID mapping in the authorized P02 history documents: cite which original DSH report/version each historical ID came from and distinguish it from the owner's G/H labels. Preserve original reports and historical snapshots; do not rewrite history or claim closed findings are newly open.

## Verification and delivery

- Run only focused, in-scope checks: the existing exact TypeScript check, the P02 PRE-01..03 harness/mutation self-checks, ProbeOnly and Full runner, plus `git diff --check`. Do not run Cargo, Tauri, sidecar builds, Vitest, or product GUI/WebView interactions; the build barrier remains active and AC1–AC6 remain BLOCKED.
- Preserve all source files, user data, locks, current/pinned revisions, and recovery paths. Do not shut down the machine or stop unrelated work.
- Commit the corrections on the existing Owner branch and return a clean worktree at the exact new HEAD/tree. Do not merge or integrate to `main`.
- Update the Task, Handoff, and `verification/P02/RESUME.md` with the new fixed commit, per-finding dispositions, exact commands/results, artifacts, limitations, and next Gate. Keep the P02 task active and integration commit null.
- In your response provide the fixed HEAD/tree/parent, worktree status, changed paths, commands with exact exit codes, evidence paths, and explicit NOT_RUN/blocked items. Do not describe an unrun check as passing.
