# P02PRE-R1H Round6 controlled integration protocol — attempt 5

Status: FROZEN_FOR_INDEPENDENT_REVIEW_ATTEMPT5
Task: P02PRE-R1H
Integrator/Executor/Protocol author: Codex /root
Independent Reviewer: DeepSeek Harness CLI (non-author; static review only)
Owner of candidate selfcheck: /root/p02_r1h_codex_owner
Executor author: /root/round6_executor (separate from protocol author and adjudicator)
Remediation author (attempt 4): Antigravity
Baseline-binding repair author (attempt 5): Codex /root

This attempt5 baseline-binding supplement inherits the reviewed attempt4 protocol at `verification/P02/p02pre-r1h-round6-integration-protocol-attempt4-20261012.md` (SHA-256 `EE8F26ECB5C0C894609F2EC0357BCA237BEE72E55E7836E48B6CB1B145E46F7D`). Attempt4 and all earlier protocols remain immutable. Attempt5 supersedes only the executor attempt label and the root main HEAD/tree/index binding documented below; all other reviewed identity, output, source, File.Replace, process, validation and Gate constraints remain unchanged.

## 1. Frozen executor and current boundary

The only newly authorized execution source is `verification/P02/p02pre-r1h-round6-integrator-attempt5-20261012.ps1`. It is a read-only frozen input during execution and must never be changed by this attempt. Attempt4 executor was not invoked because its root refs/index no longer matched after exact A4 integration; this is a precondition BLOCKED state, not a test failure. Attempt5 may be invoked only after its exact independent Review and Codex adjudication. No attempt5 invocation, parser, selfcheck, replacement, validation child, Build, Cargo, capture, getter, AppContainer/profile/registry/ACL API, system AC or Windows Sandbox has run.

Frozen root binding for this attempt is `main@343895fb5f0329c0c07a7104ec321b698f967607`, tree `e12bd627c307d4bf3c851dc09d0b82f97c86ec63`, index SHA-256 `C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68`. Owner refs remain branch `agent/codex/P02PRE-R1H`, HEAD `c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d`, tree `96e7273ddd5fd27bee567bba27f19453cabe0842`. The current controlled root and Owner status evidence and hashes are frozen in `verification/P02/codex-p02pre-r1h-attempt5-exec-review-pins-20261012.json`. Every Git status invocation must pass the separate final pathspec `:(exclude).tmp.driveupload`. No filesystem API or tool may query anything under that excluded path.

## 2. Exact output and write boundary

All attempt2/attempt3 integration output paths remain unchanged:
- `stage`: `verification/P02/p02pre-r1h-selfcheck-round6-stage-20261012.ps1`
- `recovery`: `verification/P02/p02pre-r1h-selfcheck-round5-recovery-20261012.ps1`
- `apiBackup`: `verification/P02/p02pre-r1h-selfcheck-round5-integrated-backup-20261012.ps1`
- `handoff`: `verification/P02/p02pre-r1h-round6-handoff-20261012.md`
- `execution`: `verification/P02/p02pre-r1h-integration-round6-execution-20261012.json`
- `selfcheckEvidence`: `verification/P02/p02pre-r1h-selfcheck-round6-20261012.json`
- `engineEvidence`: `verification/P02/p02pre-r1h-engine-preflight-round6-20261012.json`

The only destination replacement is `verification/P02/p02pre-r1h-selfcheck.ps1` through the single reviewed three-argument `System.IO.File.Replace` call. The attempt5 executor source is read-only and outside that write manifest.

Before execution, verify every output is absent, unignored, on the permitted ordinary parent directory/volume, and has no reparse component. Open the execution evidence stream with exclusive file sharing (`FileShare.None`) so no concurrent reader can observe intermediate writes.

Immediately before the single reviewed three-argument `System.IO.File.Replace` call, re-pin destination bytes, ACL and streams (and any other exact destination invariants already required); verify zero drift against initial precheck and stop on any drift before calling `Replace`.

## 3. Process observation supplement

The main executor must run in `C:\Program Files\PowerShell\7\pwsh.exe`, PowerShell 7.6.6/Core/FullLanguage, from the frozen root, identity and SID. Windows PowerShell 5.1 `powershell.exe` is forbidden. The only permitted child images remain the exact frozen Git executable and the two exact PowerShell 7 validation children.

Attempt4 addresses the attempt3 review findings and adjudication as follows:

1. **Flat P/Invoke method definitions structure (P2-1 / upgraded P1)**:
   The nested `$definitions` array is replaced by an explicit flat collection with named fields (`name`, `returnType`, `parameterTypes`), returned by the pure helper function `GetToolhelpDefinitions`. In-memory validation confirms that `TypeBuilder.DefineMethod` accepts every signature without array-indexing errors. Native methods are not invoked dynamically, and no assembly is persisted.

2. **Process selection pure helper and prelaunch sentinel (P1-1)**:
   Process-record selection and attribution logic is refactored into the pure helper function `SelectProcessRecords`. The prelaunch state ("no child has launched yet") is represented by an explicit `$null` or known-state sentinel, and child PID 0 is strictly rejected as a sentinel, preventing collision with the Windows System Idle Process (PID 0). A prelaunch sample never classifies PID 0 as the child. Unknown descendants, rogue child processes, and ambiguous attribution fail closed.

3. **Fail-closed exception propagation (P3-4)**:
   Every child preparation (executable/CWD allowlist checks, environment inspection, process initialization), launch, observation, capture, and verification exception path in `InvokeChild` sets `$script:ProcessClosureBlocked = $true` before propagating. Callers and the outer error handler stop before any subsequent protected reads or writes, and do not launch further child processes (such as diagnostic status) when process observation or closure is blocked. Current no-kill and no-retry behavior is strictly preserved.

4. **Accepted limitations explicitly retained (P3-3 and P3-5)**:
   - *P3-3 (Observation race)*: The narrow external non-atomic observation window between S2 status execution and subsequent internal file/ACL/stream hash checks is retained as an explicit evidence boundary; atomic system-wide snapshot is not claimed.
   - *P3-5 (No total child timeout)*: No total child timeout is imposed; a hung child process leaves the executor waiting indefinitely (`WaitForExit(10)` loop). Live children are not killed and no automatic retry is performed without a separately reviewed policy.

Primary API references for static review:
- Microsoft Learn, CreateToolhelp32Snapshot: https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot
- Microsoft Learn, Process32FirstW: https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-process32firstw
- Microsoft Learn, TypeBuilder.DefinePInvokeMethod: https://learn.microsoft.com/en-us/dotnet/api/system.reflection.emit.typebuilder.definepinvokemethod
- Microsoft Learn, Marshal.GetLastPInvokeError: https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.getlastpinvokeerror

## 4. Git child and status phase supplement

Use only `C:\Program Files\Git\cmd\git.exe` with `ProcessStartInfo.UseShellExecute = $false`, each argument as an `ArgumentList` item, and the exact root or Owner `WorkingDirectory`. No aliases, `-C`, command strings, wrappers, pagers, hooks, fsmonitor, shell, or other Git process is allowed. Keep exact repository identity commands and fixed status/check-ignore argument lists.

The executor removes inherited Git context variables and all `GIT_TRACE*` entries. It records removed variable names but not values. Inherited Git context override or `GIT_CONFIG*` variables trigger immediate fail-stop before launch. Sets `GIT_OPTIONAL_LOCKS = 0` and `GIT_TERMINAL_PROMPT = 0`.

Required sequence:
1. Fixed Git identity queries and per-output check-ignore queries before creating execution evidence (no status).
2. Create execution-evidence file with `CreateNew` and `FileShare.None`.
3. Capture S0-root and S0-owner (S0 is first status snapshot; Owner must be clean).
4. Capture separate `pre-stage-owner` status before stage/recovery/Handoff creation; require clean.
5. Create stage, exact recovery bytes and Handoff by `CreateNew`; capture S1-root.
6. Re-pin destination bytes, ACL and streams immediately before `File.Replace`; call `File.Replace` exactly once; capture S2-root as first child after return.
7. Run PowerShell 7 Parser, selfcheck child and capability child; create validation evidence with `CreateNew`; capture S3-root.
8. Never modify Task, Plan, STATUS, Index or checkpoint during S0–S2.

## 5. Failure-only status phase

A failure diagnostic is not S0/S1/S2/S3 and must never be labeled PASS. It is allowed only after the execution-evidence file was successfully created and only while `$script:ProcessClosureBlocked` is false (process observer healthy, no unknown/unlisted child or ambiguous process seen). If process observation or closure was blocked, the failure diagnostic records `NOT_RUN: process observation or closure blocked` and does not launch any child process.

Preserve partial outputs, perform only authorized read-only path/hash checks, and record evidence. Do not retry, clean, restore or delete anything.

## 6. Validation and Gate limits

Round6 Parser must report zero errors; the selfcheck must return exit 0 and all frozen assertions must pass; the exact capability query must return its frozen valid output. Parser/selfcheck and engine evidence are real results, not static review. Any failure remains FAILED/BLOCKED as observed; it does not authorize an automatic retry or turn any Gate PASS.

Keep the Owner risk exception exactly:
- `private_registry_absence = UNPROVABLE`
- `Technical Gate = NOT_SATISFIED`
- `Owner Risk Acceptance = APPROVED`
- `Gate Disposition = WAIVED_BY_OWNER`
- `Build Authorization = AUTHORIZED_WITH_EXCEPTION`
- `technical condition unmet; user explicitly accepted residual risk`

Build Gate remains BLOCKED; Hard Build Barrier remains EFFECTIVE; Build/Cargo remains NOT_RUN; system AC1–AC7 remain BLOCKED / NOT_RUN. This protocol does not authorize capture, getters, profile/registry/ACL operations, P02PRE-R2 dynamic isolation, AC1–AC7 or Build/Cargo. Windows Sandbox remains forbidden.

## 7. Independent review, report transport, and pin manifest

Reviewer and transport boundary (P3-1):
- DeepSeek Harness performs static review only. DSH returns its Markdown review report via standard output (`stdout`).
- DSH is not requested or required to write repository files or initialize sandbox/shell security permissions inside the repository workspace (addressing the observed Win32 5 `SetNamedSecurityInfoW` shell failure).
- The outer Codex capture wrapper captures DSH stdout, stderr, and exit status, and separately writes the captured report body into the designated report path using `FileMode.CreateNew` with exclusive file sharing (`FileShare.None`).

Pin manifest consistency (P3-2):
- The pin manifest metadata must strictly agree with the actual pinned inputs list: when the rolling checkpoint is included among the input pins, the metadata must explicitly declare `checkpointIncludedInInputPins = true`.

Any unresolved P0/P1/P2 finding means `CHANGES_REQUESTED`. For this Task, the independent static-review verdict is `APPROVED_STATIC_CONTENT`; Codex pin recheck and adjudication are also required before the static-review gate is released. The executor remains blocked until the separate final pre-run returns `PRE_RUN_PASS`. Static approval is not execution, Gate or AC PASS.
