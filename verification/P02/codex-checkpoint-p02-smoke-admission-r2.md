# P02 Sandbox Isolation Smoke Admission — R2 Codex Decision

- Decision recorded: 2026-10-10 04:14:40 +0800; state: `ADMITTED / PRESTART_CHECKS_PENDING`.
- Parent Task=P02 remains `in_progress / ACTIVE`; this is a separate Codex Smoke Gate decision, not completion of P02.
- Fixed R6 reviewed delivery: HEAD=`c85a041c514f3c0dd1c355a2d09f064dbc64e749`, tree=`b67e3e02186a8009c46da0dba819003b04acfec1`, parent=`844aec282416111310d9a9efcac5bc9e0c6eb451`; DeepSeek Harness independent exact-head Review=`APPROVED`, P0/P1/P2/P3=`0/0/0/0`.
- R5 F-01 through F-11 are explicitly dispositioned; R6 accepted the explicit limits for F-04/F-10/F-11. DSH optional notes N1–N3 are recorded as non-finding documentation precision items and do not block this admission.
- Fresh pre-admission stage-1 capture: `2026-10-10T04:11:59.5066498+08:00` through `2026-10-10T04:12:58.602+08:00`; result=`PRESTART_STAGE_1_PASS`, `16/16` frozen thresholds true. Shell=`C:\Program Files\PowerShell\7\pwsh.exe` PowerShell `7.6.6`, PID `20492`, interactive=`True`, elevated=`False`.
- Current checks: feature InstallState=`1`; WSB `MicrosoftWindows.WindowsSandbox_0.8.107.0_x64__cw5n1h2txyewy` / `0.8.107.0`, EXE SHA-256=`247e092b5c5bd37820f225a7dd3ddf10ae37a67e2751a19c24b802c84769c441`, version/list EXIT=`0/0`, parsed `WindowsSandboxEnvironments` count=`0`; 16 CPU cores; total RAM `31.647 GiB`; available RAM `16765 MiB`; C:/G: free `328.904/1299.429 GiB`.
- HostFolder roots=`12/12` with no root-level reparse point; inputs=`20/20` hashes, `14/14` registered sizes, `6` unregistered sizes; source/EOL pins match; r3 config canonical LF=`2609` bytes / `9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`, 11 mappings; fixed clone absent.
- Root protection: live root `main@ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50`; frozen manifest HEAD=`549a6544f0be1eec66c09ece393fd1a409f10bf3`; 203/203 entries, all missing/extra/status/content mismatch counts zero, digest=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`, current candidate/root overlap=0.
- Evidence: [R6 Review](dsh-review-p02-preflight-r6.response.md), [R6 session metadata](dsh-review-p02-preflight-r6.session.json), [current pre-admission report](codex-smoke-admission-preflight-r2.md), [observations JSON](codex-smoke-admission-preflight-r2.json), [prior NOT_ADMITTED checklist](codex-checkpoint-p02-smoke-admission-r1.md).
- Admission scope: exactly one isolation Smoke attempt using the independently reviewed r3 WSB config/hash and only the fixed ordinary clone path `G:\CODEX\P02-scratch-build-source`. This admission permits the clone and pre-start checks; it does not permit `wsb start` until every post-admission checklist item below is verified.

## Required before any `wsb start`

1. From the approved live, interactive, non-elevated host PowerShell process, create the fixed clone using the exact Task sequence: `git clone --no-local --no-hardlinks --no-checkout --single-branch --branch main "G:\CODEX\New Manga" "G:\CODEX\P02-scratch-build-source"`; remove `origin`; set `core.autocrlf=true`; checkout detached at `7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`. If the path is occupied, stop and mark blocked.
2. Verify clone HEAD/tree, empty porcelain, private common Git directory, no remote, no alternates, source pins, and `fsutil hardlink list` link count=1 for every file under `.git/objects`.
3. Produce and verify recursive pre-start manifests for every mapped HostFolder; enumerate reparse points without following unsafe links and prove the approved root set plus scratch-only output boundary.
4. Recheck the exact r3 XML canonical bytes/hash and all mappings; immediately before start run `wsb list --raw` and prove `WindowsSandboxEnvironments=[]`, binding its raw output/time to the one attempt.
5. Bind the running session to the unique visible Windows Sandbox UI window and saved screenshot in the fixed scratch clone. Any unknown/failure means no start or, if already started, stop the same session and preserve all state.

## Independent gates and current state

- Smoke admission=`ADMITTED`; Smoke result=`NOT_RUN`; complete preflight=`BLOCKED / INCOMPLETE` until the pre-start checklist and one Smoke attempt complete.
- Build Gate=`BLOCKED`; build=`NOT_AUTHORIZED / NOT_RUN`; P02 AC1–AC7=`BLOCKED / NOT_RUN`; product acceptance=`NOT_RUN`; Hard Build Barrier=`EFFECTIVE`.
- No clone, Sandbox, Smoke, build, runner, Vitest, GUI, WebView, or product test has run at this decision boundary.
- Next exact action: run the exact clone sequence, verify clone/object-link/source invariants, then recursive HostFolder manifest/reparse checks and the immediate pre-start UI/session bindings. Do not run `wsb start` until all checks above are recorded PASS.
