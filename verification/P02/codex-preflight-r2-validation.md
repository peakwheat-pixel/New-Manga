# P02 Preflight R2 Validation

- Verification time: 2026-10-10 00:34 Asia/Shanghai (2026-10-09 16:34 UTC).
- Fixed change commit: 80cf56514e7b079fc18c71730558edd6913f80f3; tree=234cd26f735774400838f898910fc2454f7f9dde; parent=cd3e86d6f072888270d0179627fe4c39cce4829c; base=6855c113e6a44320d9555777900cfb78a218d383. Branch=codex/P02-process-isolation; author worktree clean; three commits from base through fixed change.
- At fixed change HEAD `80cf56514e7b079fc18c71730558edd6913f80f3`, the base-relative diff was 24 paths; at exact-head review HEAD `7d8951c28cd954d7e325cd53e7991f3bec87d971`, it was 26. Authorization is the union of the original R1 frozen scope (`codex-checkpoint-p02-preflight-scope-frozen.md:6`) and r7, not r7 alone. Six unchanged R1 carry-forward files omitted from r7's enumeration are `codex-scratch-build-preflight-inputs-r1.tsv`, `wsb-version-r1.stdout.txt`, `wsb-version-r1.stderr.txt`, `wsb-list-raw-r1.stdout.txt`, `wsb-list-raw-r1.stderr.txt`, and `codex-checkpoint-p02-non-elevated-preflight-start.md`; all six are byte-identical from R1 candidate `561f4105` through reviewed HEAD `7d8951c2`. R7 enumerates 27 paths, seven of which (the R2 review checkpoint and six R2 review packet artifacts) did not yet exist at `7d8951c2`. The exact 24/26 path counts have commit anchors; unexpected paths under the union=0. Product source, tests, dependencies, IPC, Schema, build inputs, user data, and Owner allowlist are unchanged.

## Validation results

| Check | Command / method | Result |
|---|---|---|
| Project route validator | `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py` at fixed change commit | EXIT=0; 196 nodes/classifications/dependencies valid; Task states and Plan align; all 21 planned nodes acyclic; navigation links resolve; zero P01 production/code delta; product tests/build/GUI=`NOT_RUN`. |
| Diff whitespace | `git diff --check 6855c113e6a44320d9555777900cfb78a218d383 HEAD` | EXIT=0. |
| Focused Markdown links | Changed Markdown files at fixed change HEAD `80cf5651`; relative links resolved from source files and compared with base | 13 Markdown files; 765 relative targets scanned; 10 pre-existing historical missing targets; new missing targets=0. Exact reviewed HEAD `7d8951c2` was independently rescanned by DSH as 15 Markdown files / 766 targets / 10 base-existing missing / 0 new missing (see R2 Review checkpoint). |
| Frozen root manifest | Replayed manifest path/status/kind/size/SHA-256 against live root `git status --porcelain=v1 --untracked-files=all -z` | 203/203 match; missing/extra/mismatch=0; staged=0; canonical entries SHA-256=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`. Manifest `head=549a6544f0be1eec66c09ece393fd1a409f10bf3` is its frozen creation HEAD; live root remains `main@6855c113e6a44320d9555777900cfb78a218d383`. |
| Candidate/root collision | Exact fixed-change candidate path set versus the 203 live root dirty paths | At `80cf5651`: 24 base-relative candidate paths; path overlap=0; author worktree clean. At reviewed `7d8951c2`: 26 paths and overlap=0 (independent DSH exact-head check). |
| R1 condition repair | R1 DSH findings P2-01 and P3-01..P3-05 | DSH exact-head R2 Review at `7d8951c2` returned `APPROVED` (P0/P1/P2/P3=`0/0/0/3`) and independently closed all six R1 conditions. R2 N-01..N-03 are nonblocking documentation/evidence findings; the r8 repair scope is frozen at `6ffba27b`. |

## Gate status

- This is a documentation/evidence repair candidate, not a product verification result.
- Windows Sandbox Feature remains `UNKNOWN` and was not queried. Full preflight remains `BLOCKED / INCOMPLETE`; Smoke admission=`NOT_ADMITTED`; Smoke=`NOT_AUTHORIZED / NOT_RUN`; Build Gate=`BLOCKED`; build=`NOT_AUTHORIZED / NOT_RUN`; P02 AC1–AC7=`BLOCKED / NOT_RUN`; Hard Build Barrier remains effective.
- No elevation, Sandbox, clone creation, Smoke, Build, Vitest, product test, GUI, or WebView was run.

## Exact next action

Historical next action at the initial R2 repair snapshot; superseded by the R2 exact-head decision and the r8 follow-up below.
## R2 exact-head review and N-01..N-03 follow-up

- DeepSeek Harness reviewed exact HEAD=`7d8951c28cd954d7e325cd53e7991f3bec87d971` / tree=`1340c5282e32361c117f0aeacb670d412fe568c9`; decision=`APPROVED`, P0/P1/P2/P3=`0/0/0/3`. R1 P2-01 and P3-01..P3-05 are closed. Full independent report: [R2 response](dsh-review-p02-preflight-r2.response.md).
- N-01 path authorization is the R1 frozen scope ∪ r7. The six inherited paths are enumerated above and unchanged from `561f4105`; 24 paths is the `80cf5651` snapshot, 26 is the reviewed `7d8951c2` snapshot. At reviewed HEAD, no candidate path was outside the union.
- N-02 exact-head rerun was performed and recorded by the independent DSH reviewer on `7d8951c2`: route validator EXIT=0 (196 nodes); `git diff --check 6855c113..HEAD` EXIT=0; changed-Markdown scan=15 files / 766 relative targets / 10 already missing in base / 0 new missing. Root manifest=203/203, staged=0, candidate/root path overlap=0. The full command/result record is in the R2 response and [R2 review checkpoint](codex-checkpoint-p02-preflight-r2-review.md).
- N-03 is resolved in `codex-checkpoint-p02-non-elevated-preflight-start.md`: the original `23:58` scope-freeze timestamp is retained, and its completion sentence is explicitly labeled as a retrospective delivery-time note. The collection window starts after the freeze checkpoint as recorded in the report.
- R3 will rerun route/link/diff/protected-root checks on the final repair candidate before exact-head DSH review. Product source/tests/contracts/dependencies remain unchanged; all product gates remain blocked or not run as stated above.
## R3 repair candidate validation at `6f47d4812e269a7c4c6192f302842b902e5f5ae4`

- Exact author checkout: branch=`codex/P02-process-isolation`; HEAD=`6f47d4812e269a7c4c6192f302842b902e5f5ae4`; tree=`5f9d94b9af3ebfd2398e422501b53408591dab6b`; parent=`ed0fb8a28484e547da953cf2b68ec32d21a320b8`; worktree clean.
- Route validator `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`: EXIT=0; 196 nodes/classifications/dependencies valid; Task/Plan states align; all 21 planned nodes acyclic; delivery/navigation links resolve; product tests/build/GUI=`NOT_RUN`.
- `git diff --check 6855c113e6a44320d9555777900cfb78a218d383 HEAD`: EXIT=0.
- Focused changed-Markdown scan (inline and reference links, fenced code excluded, external/anchor links skipped): 19 Markdown files / 772 relative targets / 10 missing targets already absent at base / 0 new missing targets.
- Root protected manifest replay: live root=`main@6855c113e6a44320d9555777900cfb78a218d383`; 203 manifest entries and 203 live dirty paths; path/status/kind/size/SHA-256 missing/extra/status/content mismatches=`0/0/0/0`; staged=0; manifest entries SHA-256=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`. Candidate diff=`34 paths`; candidate/root dirty-path overlap=`0`.
- No Smoke, Build, product test, GUI/WebView, Windows Feature query/change, elevation, Sandbox, or clone operation was run. These results validate only documentation/routes and protected-path isolation.
## R3 exact-head Review and union-containment evidence

- DSH exact-head target=`c36435aec5042143b816c01aa6da2ff3e80ba154`; tree=`cba4d7f25bf8d68827b41449d0cfbde62539fd7f`; parent=`9a96b5ae0695f56da9f19bfaf0771adda7999ea7`. Decision=`APPROVED`, P0/P1/P2/P3=`0/0/0/3`; R2 N-01..N-03 are closed. New R3-N-01..N-03 are nonblocking; see [R3 response](dsh-review-p02-preflight-r3.response.md).
- Fresh exact-target reviewer validation: route EXIT=0 (196 nodes), diff check EXIT=0, changed Markdown=20 files / 772 relative targets / 10 base-existing missing / 0 new missing; root manifest=203/203, all five path/status/kind/size/SHA-256 mismatch counts=0, staged=0, candidate/root overlap=0.
- Exact reviewed candidate scope: 35 base-relative paths; DSH independently confirmed `35 paths ⊆ original R1 frozen scope ∪ r7 ∪ r8`, outside-union=0. The fixed-change and earlier review snapshots remain separately anchored at `80cf5651`=24 and `7d8951c2`=26.
- R3-N-03 is closed by this explicit containment record. R3-N-01/N-02 are closed by the current status refresh and R3 delivery checkpoint, which state that the repair is fixed/approved and link to the latest R3 recovery point.
