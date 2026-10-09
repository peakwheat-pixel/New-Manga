# P02 Preflight R2 Validation

- Verification time: 2026-10-10 00:34 Asia/Shanghai (2026-10-09 16:34 UTC).
- Fixed change commit: 80cf56514e7b079fc18c71730558edd6913f80f3; tree=234cd26f735774400838f898910fc2454f7f9dde; parent=cd3e86d6f072888270d0179627fe4c39cce4829c; base=6855c113e6a44320d9555777900cfb78a218d383. Branch=codex/P02-process-isolation; author worktree clean; three commits from base through fixed change.
- Scope delta r7 authorizes the exact changes and evidence in this candidate. The 24 current candidate paths equal the 24-path allowlist; unexpected paths=0. Product source, tests, dependencies, IPC, Schema, build inputs, user data, and Owner allowlist are unchanged.

## Validation results

| Check | Command / method | Result |
|---|---|---|
| Project route validator | `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` at fixed change commit | EXIT=0; 196 nodes/classifications/dependencies valid; Task states and Plan align; all 21 planned nodes acyclic; navigation links resolve; zero P01 production/code delta; product tests/build/GUI=`NOT_RUN`. |
| Diff whitespace | `git diff --check 6855c113e6a44320d9555777900cfb78a218d383 HEAD` | EXIT=0. |
| Focused Markdown links | Changed Markdown files, relative links resolved from their source files and compared with the base snapshot | 13 Markdown files; 765 relative targets scanned; 10 pre-existing historical missing targets; new missing targets=0. The project route validator also reports its delivery/navigation links resolve. |
| Frozen root manifest | Replayed manifest path/status/kind/size/SHA-256 against live root `git status --porcelain=v1 --untracked-files=all -z` | 203/203 match; missing/extra/mismatch=0; staged=0; canonical entries SHA-256=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`. Manifest `head=549a6544f0be1eec66c09ece393fd1a409f10bf3` is its frozen creation HEAD; live root remains `main@6855c113e6a44320d9555777900cfb78a218d383`. |
| Candidate/root collision | Exact candidate path set versus the 203 live root dirty paths | Candidate paths=24; path overlap=0; author worktree clean. |
| R1 condition repair | R1 DSH findings P2-01 and P3-01..P3-05 | Authorization basis is registered in scope-delta r7; predicted source pin state no longer says PASS; machine-readable CIM/WSB observations and provenance added; delivery count corrected; frozen manifest HEAD explained; mapping domains labeled. Independent R2 confirmation is still pending. |

## Gate status

- This is a documentation/evidence repair candidate, not a product verification result.
- Windows Sandbox Feature remains `UNKNOWN` and was not queried. Full preflight remains `BLOCKED / INCOMPLETE`; Smoke admission=`NOT_ADMITTED`; Smoke=`NOT_AUTHORIZED / NOT_RUN`; Build Gate=`BLOCKED`; build=`NOT_AUTHORIZED / NOT_RUN`; P02 AC1–AC7=`BLOCKED / NOT_RUN`; Hard Build Barrier remains effective.
- No elevation, Sandbox, clone creation, Smoke, Build, Vitest, product test, GUI, or WebView was run.

## Exact next action

Add this validation record and the R2 delivery checkpoint under the frozen scope, run validation once more on the resulting review target HEAD, and dispatch DeepSeek Harness for exact-head R2 Review. Do not fast-forward until P2-01/P3-01..P3-05 are independently closed.