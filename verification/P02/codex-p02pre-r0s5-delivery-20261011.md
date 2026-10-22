# P02PRE-R0S5 Owner Delivery

## Scope and execution

Task=`P02PRE-R0S5`; base=`cddff58469b56e181019a8ddfeade80684bc7eb9`; branch=`main`; worktree=`G:/CODEX/New Manga`. The current user authorized a separate R0 read-only preflight and required that uncertain methods be skipped as `NOT_SAFE_FOR_R0`.

I froze `p02-readonly-preflight-r0s5-manifest-20261011.md` against r6's exact object inventory and carried forward the prior independent R0S4 runner finding. DeepSeek Harness Round 1 returned `changes_requested` with P0/P1=`0/0`, P2=`2`, P3=`4`; its report is `dsh-p02pre-r0s5-review-20261011.md`. The report identifies the exact historical hash scope, identity baseline, ACL object set, task/review status wording, new-authorization wording, and AC checkbox states as items to tighten before final adjudication.

The historical R0 collection has exactly 13 entries: the 12 named documents plus `.git/index`, as shown in the R0 evidence's `固定文件 hash 前/后对照` table. Its historical `Get-FileHash` command does not prove the current `exec_command` runner safe. The current identity comparison baseline is r6's user `HOME-MY\49745`, SID `S-1-5-21-2196946971-914346751-4210154634-1001`, non-elevated token and no thread impersonation. ACL candidates are exactly 28 r6 objects: 12 read-only input roots, 13 scratch output leaves and three canary leaves; the full list is in the frozen manifest.

DSH dispatch=`dsh headless`, exit=`0`, session=`session-fe73b6c6-4296-4259-bf90-b5363bd15a7a`; `mount_session.py --latest` exit=`0` and reported mounting to the `New Manga` workspace. The independent report is `17644 bytes / SHA-256 A059009D3783F88F9D77D27392B0577D5C516A7452E61AECFB5BAA9B212042DC`.

Round 2=`changes_requested` (P0/P1/P2/P3=`0/0/1/4`), report=`verification/P02/dsh-p02pre-r0s5-review-r2-20261011.md`, `14531 bytes / SHA-256 88AF93CA3B1D7D11A7B45C059201C06DE6DB1BA9D4250FCB9FC26DC36D0508A5`. It confirms the historical hash scope and identity baseline, but found the canary root must be bound to the r6 scratch clone; it also requests a corrected R0 evidence section reference, safer Task objective order, and an exact Round 2 reviewer write path. Codex accepted these findings and updated the candidate canary paths to `G:\CODEX\P02-scratch-build-source\verification\P02\tmp\...`, as specified by r6's scratch root and R0 evidence. The revised object set is awaiting Round 3 Review; it has not been used for any query.

Round 2 dispatch=`dsh headless`, exit=`0`, stdout=`3839 bytes / SHA-256 0013239CE17811FB148338428E56A652B1CD29A195FE5FC1B80A6825BADE3995`; session=`session-9295f595-2e84-4162-bf28-780dc7ce4604`. `mount_session.py --latest` exit=`0`; it reported mounting into workspace `New Manga`. The Reviewer identified that R0S4 had recorded a main-repository canary candidate, but no query was run from that earlier candidate; this R0S5 revision supersedes that path with the r6 scratch root. No user/project path was opened or queried as part of this review.

Round 3=`approved` (P0/P1/P2/P3=`0/0/0/1`), report=`verification/P02/dsh-p02pre-r0s5-review-r3-20261011.md`, `10056 bytes / SHA-256 02AB67DD56CD3D5E8F33364909B6D769A5BA8EB72B67D51FEBC3DF4E36F5FD98`. The only finding is non-blocking wording on Task L55; Codex clarified that the 12 input roots are not scratch paths. The reviewed canary paths, query scope, and safety boundary did not change. Dispatch=`dsh headless`, exit=`0`, session=`session-f78b23bc-9619-47b8-83b8-84507d9b74ef`; stdout=`4967 bytes / SHA-256 39B5DD9275522A94AFE7647A7689CB634DFDCD6476D36A14BE9C6F442244FB60`. `mount_session.py --latest` output confirmed mounting into workspace `New Manga`; its numeric exit was not separately captured.

I did not run any P02PRE host/OS/Registry/WER/profile/token/ACL/path/environment/hash query. The actual `exec_command` launch executable, complete argv and wrapper startup/cache/history/temp/log boundary are not available as evidence for the current tool instance; an explicit shell selection and `login=false` do not close that gap. No command was launched to test the boundary.

## Five-way classification at this checkpoint

| P02PRE condition | Classification | Evidence boundary |
|---|---|---|
| Historical R0 user/SID observation, exact limited path/ACL snapshot, WER candidate metadata and 13-item hash collection (12 named documents + `.git/index`) | `PASS_WITH_EVIDENCE` | Historical capture only; exact objects/time in `p02-readonly-preflight-r0-evidence-20261011.md` §`固定文件 hash 前/后对照`; not a complete protected-file inventory and no claim of current state or current runner safety |
| Any current P02PRE check | `FAILED=∅` | No such query ran in this task; absence of execution is not a failure |
| Current user/SID/token (expected identity is `HOME-MY\49745` / `S-1-5-21-2196946971-914346751-4210154634-1001`, with non-elevated/no-impersonation requirement); r6 path existence/metadata; 28 exact ACL objects; TEMP/cache/scratch resolution; current 13-item R0 hash set; WER/T0 state; private registry absence | `UNPROVABLE` | No fresh host evidence; runner/method gate prevents a safe capture |
| Effective LPAC access; canary outcomes; child/broker/write closure; stop/cleanup behavior | `REQUIRES_ACTIVE_TEST` | These require active behavior outside the read-only task |
| Current `exec_command`/PowerShell startup chain and any candidate getter whose full call path is not independently proven side-effect-free | `NOT_SAFE_FOR_R0` | R0S4 independent Review and Codex adjudication; current manifest keeps each method closed until exact runner evidence is reviewed |

These are separate condition and method statuses: a not-safe query does not make its target condition pass or fail; its current value remains `UNPROVABLE`.

## Preserved restrictions

`private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`. P02PRE remains blocked. Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`. No AppContainer/profile or registry/ACL/file state was changed; Windows Sandbox was not queried, installed, enabled or launched.

DeepSeek Harness Review and Codex adjudication are complete for the static R0S5 documents. The final classification, finding dispositions and remaining runner blocker are in `codex-p02pre-r0s5-adjudication-20261011.md`; integration verification and Live Git evidence are in `codex-p02pre-r0s5-verification-20261011.md`. P02PRE-R0S5 remains `blocked / NOT_SAFE_FOR_R0`: no current host query was run because the exact runner/getter safety boundary remains unproven. This delivery does not claim current host evidence, Technical Gate PASS, Build Gate PASS, build, test or AC success.
