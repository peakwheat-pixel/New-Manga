# P02PRE-R0S6 Frozen Read-only Dynamic Preflight Manifest

## 1. Authorization and unchanged technical state

On 2026-10-11 the user authorized only a controlled, read-only P02PRE-R0 evidence stage. The authorization permits checks only when both the query and its invocation boundary are proven not to create, delete, or modify system/project state. It is not a new risk waiver, a Gate PASS, a Build Barrier release, or authorization for later active tests or risk operations. When query or runner side effects are uncertain, do not execute; classify the method `NOT_SAFE_FOR_R0` and continue other independently safe work.

- `private_registry_absence=UNPROVABLE`
- Technical Gate=`NOT_SATISFIED`
- Owner Risk Acceptance=`APPROVED`
- Gate Disposition=`WAIVED_BY_OWNER`
- Required exact statement: `technical condition unmet; user explicitly accepted residual risk`
- Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`
- The only owner waiver remains the prior private-registry pre-create absence requirement. No other safety condition is waived.

## 2. Exact source pins

- R6=`verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`, `44307 bytes / SHA-256 626E000A94C8C3561DBB13BFA4C5BC66DA315001B9F50B5AC1669339407009DE`.
- R6 independent Review=`verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md`, `APPROVED_AS_STATIC_DOCUMENT_ONLY`.
- R6 Codex adjudication=`verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md`, `ACCEPTED_AS_STATIC_DOCUMENT_ONLY`.
- P02 Task currently pins product range/AC1–AC7. This R0S6 Task does not widen product code allowlists.
- R0S5 remains historical (`blocked / NOT_SAFE_FOR_R0`). This R0S6 Task is an independently named continuation so prior task/evidence is preserved. The latest authorization permits only safe read-only R0 checks and does not authorize follow-on dynamic/write operations.
- R0 evidence source=`verification/P02/p02-readonly-preflight-r0-evidence-20261011.md`, historical recorded pin=`99592 bytes / SHA-256 AE16A27C5843C71C9EC9414C54C2FF23EBE5A612F75DA0CB5EA3A49B154879F3`; this pin is inherited from P02 docs and is not recomputed here. Its 13-object hash table means the table bound by that exact source pin; if the object does not match, its current collection is `UNPROVABLE` and not a future query candidate.
- Review independence: DeepSeek Harness did not author the R0S6 Task or manifest. It reviews Codex's current text and the fidelity of its references; it does not re-adjudicate its own R0S5 Review conclusions.

## 3. Runner and invocation boundary

- The available `exec_command(shell="powershell", login=false)` description does not establish the actual launcher executable/version/argv, startup/profile/history, wrapper behavior, cache/temp/log locations, child-process boundary, or whether invocation itself writes state. `login=false` and an inline same-process command do not prove those properties.
- No host query is released by this manifest. In particular, do not start the current runner merely to observe whether it creates a child or writes history/log/temp state.
- Candidate methods such as PowerShell/.NET identity getters, `Get-Item`, `Get-Acl`, environment/path/hash getters, Git plumbing, and WER/T0 getters require separate method and invocation evidence. Git plumbing requires an external executable; identity/ACL getters can involve API/provider/runtime behavior. None is pre-approved by its name alone.
- Any inaccessible fields remain `UNPROVABLE`; this manifest authorizes no broad process search, helper, external executable, child process, module import, profile inspection, CIM/WMI, P/Invoke, `Add-Type`, compilation, network, or environment-wide dump.
- Dispatching DSH and mounting its Review session are governance transport actions, not R0 host queries. Their session/log/mount side effects are not R0 evidence and do not prove any host getter's invocation boundary safe.

## 4. Exact R6 read sets

1. **Identity**: expected user=`HOME-MY\49745`; user SID=`S-1-5-21-2196946971-914346751-4210154634-1001`; expected moniker/SID values remain those frozen in R6 §`固定身份、Profile 与 API 参数`. Report mismatch rather than repairing it. A `WindowsPrincipal` role result does not substitute for token elevation/impersonation fields that cannot be obtained.
2. **Paths and ACL**: the only candidate objects are the 12 R6 read-only input roots, 13 exact scratch output leaves, and 3 exact scratch canary leaves. Object identities are bound by the source R6 hash and the exact named sections in that file. No current `Get-Item` or `Get-Acl` call is released. Do not query main-repository or linked-worktree ACLs, enumerate directory contents, test effective access, or write.
3. **TEMP/cache**: candidate variables and paths are only those named in R6 §`TEMP/cache 与新 Unicode 环境块`. No environment getter or path traversal is released; do not expand variables, query unlisted variables, or read config/cache/credentials.
4. **Current hashes**: the historical R0 evidence table's 13 entries (12 named documents plus `.git/index`) are only a candidate limited recapture, not the R6 full `protected-invariants` inventory. No current hash query is released.
5. **Scratch Git identity**: candidate root is exactly `G:\CODEX\P02-scratch-build-source`; expected baseline is HEAD=`7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a`, tree=`ce8056b8ef4d2ebd11bb4754b206adf921a39e41`, private common directory, no remotes and no alternates. Git plumbing is not released because it requires an external executable whose invocation and effects are not frozen.

The exact enumerations and strings are inherited unchanged from the R6 pinned file, whose size/SHA-256 are fixed above. No unknown AppContainer profile folder, private registry object, WER view/destination, per-image key, protected/deny path, extra environment variable, or user data path is authorized. Because no host query is released, no inline script or getter parameter list is authorized for execution.

## 5. Output and stop conditions

Owner report writes are limited to these exact repository files: `doc/tasks/P02PRE-R0S6.md`, `verification/P02/p02pre-r0s6-manifest-20261011.md`, `verification/P02/p02pre-r0s6-delivery-20261011.md`, `verification/P02/dsh-p02pre-r0s6-review-20261011.prompt.md`, `verification/P02/dsh-p02pre-r0s6-review-20261011.md` (R1 raw stdout/report), `verification/P02/dsh-p02pre-r0s6-review-20261011.stderr.log`, `verification/P02/dsh-p02pre-r0s6-review-20261011.exit`, `verification/P02/dsh-p02pre-r0s6-review-r2-20261011.prompt.md`, `verification/P02/dsh-p02pre-r0s6-review-r2-20261011.stdout.md`, `verification/P02/dsh-p02pre-r0s6-review-r2-20261011.exit`, `verification/P02/p02pre-r0s6-adjudication-20261011.md`, `verification/P02/p02pre-r0s6-verification-20261011.md`, `verification/P02/p02pre-r0s6-checkpoint-20261011.md`, `doc/REBASELINE_PLAN.md`, `doc/STATUS.md`, `doc/00_INDEX.md`, `doc/tasks/P02.md`, and `doc/tasks/README.md`. No wildcard output path or host/system write path is authorized. The governance files may be changed only for Task/status/link/navigation summaries, not product requirements or contracts. Reviewer output must not run a host query or modify any other file.

R2 prompt, stdout and exit files are created with `apply_patch` Add File semantics (fail if an object already exists); stdout is captured from the tool return and inserted only into that known-new file, and exit records the tool return value. No `>` redirection, append, retry, or overwrite is allowed. The R1 report/stderr/exit outputs were invoked without a verified pre-write existence/hash check (`NOT_VERIFIED`); keep them unchanged and do not overwrite them again. No `.mount.json` file is authorized; mount result, if performed, is recorded in the delivery text.

If a future approved query reports a mismatch, unknown child, scope expansion, unauthorized access/write, unexpected hash result, or evidence anomaly, stop the dependent checks and preserve evidence; no cleanup, retry, repair, or rollback.

This manifest permits no profile/registry/WER API, no ACL/registry/file mutation, no permission canary, no Windows feature/Sandbox operation, no Build/Cargo, and no AC1–AC7. The earlier pre-task scratch metadata observation is not accepted as current R0S6 evidence because it predates the frozen manifest and review and has no invocation-side-effect proof. No successful current host query is claimed.

## 6. Five-way classification

- `PASS_WITH_EVIDENCE`: only exact measured condition/object/time.
- `FAILED`: an executed check failed.
- `UNPROVABLE`: required current state not obtained or method/field unavailable.
- `REQUIRES_ACTIVE_TEST`: condition needs a separately frozen dynamic behavior test.
- `NOT_SAFE_FOR_R0`: a particular query/method cannot run under this frozen slice.

Unrun is not failed. Current conditions and the safety status of the query method must remain separate. This manifest authorizes no Build Gate release.
