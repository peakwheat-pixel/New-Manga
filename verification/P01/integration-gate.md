# P01 Codex Integration Gate

**Result: PASS at fixed target C1; P01 closeout and main fast-forward remain pending.** This report versions the fixed-head results. It does not claim product tests or GUI verification.

## Fixed range and review

- Task base: `826bea12a132c5af2ac0cd1244d00e9170093c71`.
- Integration target C1: `c28a9e49e684105eebc7f62555086d6cccad75a4`; tree: `30611cd144f7b148aaf44ea487aff8359b43be82`; parent C0: `8fdade48c7a10ee1fe56f61cfb974b32a67920ff`.
- Candidate merge M0: `13e66ec5bf9a2fc59f4e6c5623feb0bde22884c8`; parents are root main checkpoint `714138de3da06013e3ea35395e0c11b3d15fc371` and Owner checkpoint `a22a0d935bb1b99be006601a7a2c49cd305b1910`.
- Branch/worktree: `codex/P01-integration-20261009` / `G:/CODEX/New Manga.worktrees/P01-integration-codex`; common Git directory: `G:/CODEX/New Manga/.git`. C1 worktree was clean.
- Formal non-author Review: Antigravity C9, base=`826bea12a132c5af2ac0cd1244d00e9170093c71`, reviewed head=`7645577ab374b581eb7081fd57675c32793249f5`, reviewed tree=`8dafbccda120e718aeb6f40613146320a4d2564f`, decision=`approved`, session=`a421a45b-67fc-464b-896f-07084ca763f4`.
- Canonical Git-blob SHA-256: report `a378eb0395f59b0ce12f494c33a9310e991f6ac9f35da9603f599a0a8578175e`; response `d3d71f0c9ce382bbd58798e4c670c64d3901b816de5fa06e94b825ee506ed3cd`; stdout JSON `46efa931900dd40a72c02e6011b867355f9b9eff872c522c9bac90cc7ba23abc`. Each matched `agy-review-c9-session.json`; the reviewed tree and fixed head are ancestors of C1.
- Formal Review finding `OBS-C9-01` P3 (stale DSH next-task wording) is addressed in the current Handoff/navigation. C8 `changes_requested`, R1/R2 `blocked`, and the truncated C8 ENV-01 carrier remain historical facts; no missing text was reconstructed. R2/SYNTH independent Review carriers remain `NOT_VERIFIED`.
- A pre-C0 read-only review identified a stale P3 Handoff pointer; it was corrected before C0. Code-review skill review at C1 returned Standards: 0 current findings (the unversioned-claim finding was fixed) and Spec: 0 findings. The formal Task reviewer remains Antigravity; these Codex subagent reviews are supplementary.

## Scope and source-task protection

- `git diff --name-only 826bea12a132c5af2ac0cd1244d00e9170093c71..C1`: 75 paths; all match P01 allowed paths; outside paths=0; product/source/test/build paths under `src/`, `apps/`, `tests/`, and `packaging/`=0.
- `doc/tasks/M2-DERIVED-GC-2.md`, `doc/tasks/M2-PROD-DETECT-3.md`, and `doc/tasks/M2-SFX-SYNTH-BG-AUTO.md` differ only in the explicitly allowed `integration_commit` frontmatter metadata. `doc/tasks/M2-SFX-ANNOTATE-R2.md` is byte-identical to the Task base.
- At C1, P01 remained `in_review`, AC7 remained unchecked, and `integration_commit` remained `null`. This Gate does not itself mark P01 `done`.

## Executed checks

Environment: PowerShell Core 7.6.6; Python 3.14.6; Git 2.52.0.windows.1; Windows; timestamp `2026-10-09T00:58:16Z`.

| Check | Command / evidence | Result |
|---|---|---|
| Base ancestry | `git merge-base --is-ancestor 826bea12a132c5af2ac0cd1244d00e9170093c71 c28a9e49e684105eebc7f62555086d6cccad75a4` | EXIT=0 |
| Range whitespace | `git diff --check 826bea12a132c5af2ac0cd1244d00e9170093c71..c28a9e49e684105eebc7f62555086d6cccad75a4` | EXIT=0 |
| Clean-tree whitespace | `git diff --check` at clean C1 | EXIT=0 |
| Route validator | `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` | EXIT=0; 196 unique nodes; 105 architecture/governance integration records are audit-base ancestors; 21 planned nodes; dependency graphs acyclic; local links resolve; zero product/code delta |
| Allowed paths and source protections | fixed-range path check against P01 Task allowed paths; canonical-blob fingerprint checks; source Task frontmatter/body comparison | EXIT=0; 75 allowed paths, 0 outside, 0 product paths; all 3 metadata-only exceptions and unchanged R2 blob verified |
| C9 Review carrier | SHA-256 over Git canonical blob bytes for report, response, and stdout JSON; compared with session metadata | EXIT=0; all three hashes match |
| Protected root checkout | root=`main@714138de3da06013e3ea35395e0c11b3d15fc371`; compare pathset to `verification/P01/ac1-root-status.log` | 24 dirty/untracked paths; pathset match=`True`; intersection with P01 integration paths=0. A fresh status/path/content SHA-256 manifest was captured pre-fast-forward at `verification/P01/root-dirty-manifest-pre-ff.txt` (`b41835453b693b4e62818216e4d67801c01eca6e33450f8d3d3dd72849d578e7`); compare it again after fast-forward. |

## Limits and next gate

- Product pytest, Cargo, Vitest, application build, GUI, and real Tauri WebView checks: `NOT_RUN`. P01 is a documentation/metadata audit with no product or test-code changes.
- C1 fixed-head Gate checks passed, but the P01 Task remains `in_review` until this evidence is committed, the closeout state is validated, and the integration branch is safely fast-forwarded to `main` without changing the protected 24-path manifest. The earlier summary digest `deeb9a3b…` had no versioned serialization/input manifest; this fresh capture establishes a reproducible pre-fast-forward baseline rather than claiming the two digests are comparable.
- Next: commit this Gate evidence; run the route validator against the `done=3 / proposed=18` closeout candidate; verify the final allowed-path range and root content manifest; close P01 only after those checks; then fast-forward and record the live `main` checkpoint in `verification/P01/RESUME.md` before creating the P02 Task.
