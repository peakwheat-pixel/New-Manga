# M2-S1 post-integration verification — 2026-09-26

## Fixed identities and scope

- Shared integration workspace: `G:/CODEX/New Manga.worktrees/M2-UI1-integration-final-83a`, branch `codex/M2-S1-integration`; its Git common-dir is the shared `G:/CODEX/New Manga/.git`. The original `G:/CODEX/New Manga` dirty checkout and all old M2-C1 Owner/Review workspaces were left untouched.
- Research base: `85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc`; M2-C1 Contract blob remains `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` at Owner and merge heads.
- DSH standalone clone: `C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel`; independent `.git`, no alternates. Git bundles were created there and fetched into the shared repository. Original DSH SHAs were preserved: initial delivery `4eaad684`, initial Handoff `7766a2bb`, revision reviewed_head `64c87d13faa3889c749096dedeacf5afbe8dda16`, revision Handoff `37808abd`, Owner tip `9f5eb1d51cb4283eb670085410ea9596d1f7b0d2`.
- Non-author Codex Reviews: initial [changes_requested](../../doc/reviews/M2-S1-4eaad68.md) commit `f709e39c`; revised [approved](../../doc/reviews/M2-S1-64c87d1.md) commit `8984b4b38f413325dd0860c5e7bd7751571dc59f`, fixed to `64c87d1`.
- Merge `4103493fd63c0133f62a659390d0367d1c2a98ab` parents: `8984b4b38f413325dd0860c5e7bd7751571dc59f` and `9f5eb1d51cb4283eb670085410ea9596d1f7b0d2`. `git merge-base --is-ancestor` for reviewed_head and approved Review both returned exit 0. The only merge conflict was `doc/tasks/M2-S1.md`: Codex compared the three conflicting blocks (status, pre-execution `NOT_RUN` table, Gate/Owner record), retained Owner's actual execution state, and verified the resolved file's blob equals the DSH tip blob before the subsequent Codex `done` update. No Owner commit was rewritten.

## Integrated checks

| Check | Actual result |
|---|---|
| `git diff --check 8984b4b3 4103493` | exit 0; no whitespace error |
| `git diff --name-status 85a2aa7..9f5eb1d` | Only `doc/tasks/M2-S1.md`, `doc/research/M2-S1_RESOURCE_CHANNEL_SPIKE.md`, two new `doc/handoffs/M2-S1-*.md`, and `verification/M2-S1/**`; protected product, Contract, Schema, dependency and M2-C1 paths unchanged |
| Research scenario summaries | Original A–E = 60/60 `PASS`, five exit codes 0 in `raw/00-run-all.log`; revision F = 8/8 `PASS`, exit 0 in `raw/15-probe-F-boundary.log`. F-03–F-06 PASS means an unsafe race was **observed**, not that product security passed. |
| Fixture regeneration | `raw/16-revision-fixture-reproducibility.log` records 10/10 SHA-256 matches with `raw/fixtures.json`. |
| Contract and product tests | Contract blob unchanged. Product pytest, GUI and Tauri/WebView runtime `NOT_RUN` per research Task; no product implementation is claimed. |
| Markdown relative links | Codex checked 15 Task/report/Handoff/Review/evidence Markdown files, 59 local links; one in `04-verification-plan-results.md` incorrectly used `../tasks/M2-S1.md`. The integration follow-up changes exactly that target to `../../doc/tasks/M2-S1.md`; all 59 then resolve. Including this new integration record, the final check is 16 files / 65 local links / 0 broken. |

## Evidence hashes and checkout line endings

The Owner's `raw/06-evidence-hashes.log` hashes **working-tree bytes in its C: clone**. Recomputing against that clone returned 43 entries, 0 mismatches. The shared worktree has `core.autocrlf=true`; at merge `4103493`, 27 files matched byte-for-byte and 16 Markdown/Python/PowerShell text files matched after CRLF→LF normalization, with 0 unexplained mismatches. This is checkout EOL conversion, not evidence content drift. The original Owner manifest and logs remain unchanged in DSH commits.

The integration follow-up corrects only the broken link in `verification/M2-S1/04-verification-plan-results.md` (new Git blob `e6d7ce122945118223c6bce0a16114408948f506`). After that correction, 27 manifest entries still match directly, 15 match after CRLF→LF normalization, and the one intentionally edited Markdown file differs only by that link target. The original Owner blob can be read at `9f5eb1d:verification/M2-S1/04-verification-plan-results.md` and its original manifest at `9f5eb1d:verification/M2-S1/raw/06-evidence-hashes.log`; this Codex integration note does not rewrite either Owner commit.

## Gate

Research AC1–AC6 have documented evidence and non-author Review `APPROVED`; M2-S1 can be `done` after this post-integration check. The conditional A/B recommendation is **not** a product implementation release. Research report §7 lists seven `USER_DECISION_REQUIRED` thresholds; S1-B1–B12 include Tauri asset protocol, TOCTOU product defense and token path confidentiality as `NOT_RUN/UNVERIFIED`. Future runtime work needs a separately released Task and those decisions/validations.

Review R-003 is a non-blocking docstring scenario-number typo in `m2s1_lab.py`; the report, Handoff and raw JSON use the correct F-05/F-07/F-08 labels. It remains deferred for a later documentation correction.
