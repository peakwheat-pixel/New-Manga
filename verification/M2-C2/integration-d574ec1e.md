# M2-C2 post-integration verification — 2026-09-26

## Fixed identities and scope

- Shared integration workspace: `G:/CODEX/New Manga.worktrees/M2-UI1-integration-final-83a`; Git common-dir is the shared `G:/CODEX/New Manga/.git`. The original `G:/CODEX/New Manga` checkout (branch `codex/preserve-preexisting-main-worktree-20260925`, pre-existing dirty set) and all Owner/Reviewer worktrees were left untouched.
- Release base: `3f468e6eb791ab112e38afaff50f511eb2ebc0c9`; governance parent `47da647785e29d46e3752c53899959243f958d05` (M2-C2 registration/release).
- Owner branch `agent/zcode/M2-C2-typed-ipc-contract-revision`: chain `a7727afe` (baseline self-check, ready→in_progress) → `67f814ffa7528da91335ef28deec3cb18f8ebf75` (contract revision `1.0`→`1.1`; delivery) → `c18f273ad5a7768c6ae1726610da1ac27aa958d3` (Handoff, in_review; **reviewed_head**). The Owner branch tip stays at `c18f273a`; it was not advanced or rewritten.
- Non-author Reviewer: DeepSeek Harness. The review was produced headless **inside the Owner worktree**; its sandbox could not run `pwsh`/git commands (`SetNamedSecurityInfoW Win32 5`, per its report §0), so the Reviewer delivered the report as an **untracked file with no review commit object** and explicitly handed the three pre-integration commands to the integrator. Its disposition note is `verification/M2-C2/dispatch-review-c18f273a.md` (also untracked).
- Integration merge `d574ec1e` parents: `0bbe78f3` and `c18f273a`. `git merge-base --is-ancestor` for `c18f273a` against `d574ec1e` returns exit 0.

## Review-report admission decision

No review branch existed to merge (M2-S1/M2-S2 pattern unavailable). Decision: **byte-for-byte import by the integrator, as a standalone commit before the merge** (`0bbe78f3`), with source SHA-256 recorded here and the commit message stating that content was authored by DeepSeek Harness (report) / ZCode dispatch record (disposition note) and that Codex performed import only:

- `doc/reviews/M2-C2-c18f273a.md` = `f38dbae5755ae1aefb0ccdb0caaa11906f3e72c63621ca05e8297cf86a4a46fb`
- `verification/M2-C2/dispatch-review-c18f273a.md` = `8cb3e3e7ec6965096f1b3606206c395dcf33220437b63e29dd012013771d2e21`

Import compared working-tree bytes via `sha256sum` immediately after `cp` from the Owner worktree; zero content edits. Report frontmatter: `decision: approved`, `findings_disposition: no_blocking_findings (0×P0 / 0×P1 / 0×P2; 4×P3 advisory, non-blocking)`, `reviewed_head: c18f273a`.

## Pre-integration commands (run by the integrator because DSH was sandbox-blocked)

| Command (DSH final message) | Actual result |
|---|---|
| `git diff --name-status 3f468e6e..c18f273a` | 7 paths, all inside the 4 authorized classes: `M doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`; `A doc/handoffs/M2-C2-67f814ff.md`, `A doc/tasks/M2-C2.md`, `A verification/M2-C2/{10-delivery-diff.log, baseline-selfcheck.md, clause-source-trace.md, guard-checks.log}`. Zero forbidden paths. |
| `git diff --check 3f468e6e c18f273a` | exit 0 |
| `git rev-parse <head>:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | `fc35913801297ee1876ea395f9c5041a16226f20` at both `67f814ff` and `c18f273a`; identical on integrated `master` after the merge. |

## Merge conflict handling

Exactly one add/add conflict: `doc/tasks/M2-C2.md` (governance release copy at `47da6477` vs Owner copy). Resolved per the user-directed rule **"master as base + Owner backfill"**: every governance field byte-identical, plus only the Owner AC backfill, executed test table and run records. Because the Owner version's body is exactly the release body plus those backfills (verified by diffing both sides before resolution), the merged file is **blob-identical** to the Owner version — `git rev-parse :doc/tasks/M2-C2.md` = `f0e8bec35d6f76cd06ebf9bc298c2cb7ace2d32a` = `c18f273a:doc/tasks/M2-C2.md`. No information lost on either side; no Owner commit rewritten.

## Integrated checks

| Check | Actual result |
|---|---|
| `git diff --check 3f468e6e HEAD` (integrated) | exit 0 |
| `git diff --name-status 3f468e6e..HEAD` (integrated) | 15 paths: contract `M`, Owner's 7 authorized files, review report + dispatch record (import), release evidence, governance navigation ×5. Forbidden-path grep (`^(src/\|tests/\|packaging/\|src-tauri/)`): zero hits. |
| Contract blob on integrated master | `fc35913801297ee1876ea395f9c5041a16226f20` — the exact reviewed artifact, unchanged by integration. |
| Markdown relative links | 8 M2-C2 Markdown files (Task, contract, Handoff, Review, baseline self-check, clause-source-trace, release evidence, dispatch record): 30 local links, 0 broken. |
| P3 advisories (F-01..F-04) | **Deferred, not fixed in this integration** — fixing them would change the reviewed blob and break the approval↔artifact correspondence (`fc359138`). All four are wording/label precision advisories (F-01 `TO-BE` usage in §10.2 header note; F-02 `RULED` prefix on clause 1 lacking a T# anchor; F-03 T2 lost the "concurrently" qualifier; F-04 digest trust-premise sentence), explicitly rated non-blocking by the Reviewer with one-line fixes allowed in a later contract touch. Disposition: record here, fold into the next contract-touching Task. |
| Product tests / runtime | `NOT_RUN` per contract-revision scope; no implementation is claimed. |

## Gate

M2-C2 AC1–AC5 have documented evidence and non-author Review `approved`; the Task is `done` with integration merge `d574ec1e`. The revision lands ruling T1–T7 and the S1-B11/S1-B12 security semantics as **design requirements** (product-grade guarantees stay `UNVERIFIED/NOT_RUN` where the sources say so, e.g. T3 cold-cache S1-B6, S1-B11 conditions ③④). It does not authorize runtime implementation; the conditional route-A/B recommendation and §8.3 preconditions from M2-S1 remain in force. F-01..F-04 (4×P3) are deferred to the next contract-touching Task with this record as the disposition anchor.
