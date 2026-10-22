# P02PRE-R1H Round6 controlled integration protocol — attempt 3

Status: FROZEN_FOR_INDEPENDENT_REVIEW_ATTEMPT3
Task: P02PRE-R1H
Integrator/Executor/Protocol author: Codex /root
Independent Reviewer: DeepSeek Harness CLI (non-author; static review only)
Owner of candidate selfcheck: /root/p02_r1h_codex_owner
Executor author: /root/round6_executor (separate from protocol author and adjudicator)

This is the attempt3 controlling supplement to the immutable attempt2 protocol at verification/P02/p02pre-r1h-round6-integration-protocol-20261012.md, SHA-256 26E152C31EF9111ECA55BAB96C3783F249329C5DE111909E9B8C55B2DD666697. Attempt2 remains historical and is not edited. Attempt3 supersedes only the clauses stated here; all non-conflicting identity pins, output paths, source hashes, File.Replace requirements, validation commands and Gate limits in attempt2 remain in force.

## 1. Frozen executor and current boundary

The only newly authorized execution source is verification/P02/p02pre-r1h-round6-integrator-20261012.ps1, 40604 bytes, SHA-256 DACDD544784A035E980F74250207D8EB561E13D0C5A06AA9F810DA9A1B29F222. It is a read-only frozen input during execution and must never be changed by this attempt. It must only be invoked after independent Review and Codex adjudication of attempt3. No invocation, parser, selfcheck, replacement, validation child, Build, Cargo, capture, getter, AppContainer/profile/registry/ACL API, system AC or Windows Sandbox has run for attempt3.

Current main baseline remains main@cddff58469b56e181019a8ddfeade80684bc7eb9, tree c25d051a4b9a0bd9773b50170e100f575ea19f2b, index SHA-256 214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C. The exact current controlled status, Owner worktree status and their hashes are frozen separately in the attempt3 pins. Every Git status invocation must pass the separate final pathspec :(exclude).tmp.driveupload. No filesystem API or tool may query anything under that excluded path.

The prior malformed diagnostics remain process deviations and not execution evidence: one helper passed a leading-space pathspec and Git exited 128 before producing status; no PID was captured for that attempt. The corrected status query later returned exit 0. The malformed command did not query the actual excluded path. Earlier attempt2 deviations remain described in the Task and checkpoint.

## 2. Exact output and write boundary

All attempt2 integration output paths remain unchanged: stage, recovery copy, API backup, Round6 Handoff, execution evidence, selfcheck evidence and engine-preflight evidence. Their exact relative paths are frozen in attempt2 section 2 and in the attempt3 executor. The only destination replacement is verification/P02/p02pre-r1h-selfcheck.ps1 through the single reviewed three-argument System.IO.File.Replace call. The attempt3 executor source is read-only and outside that write manifest.

Before execution, verify every output is absent, unignored, on the permitted ordinary parent directory/volume, and has no reparse component. Use only exact frozen inputs and paths. Create the execution-evidence target with FileMode.CreateNew before any S0 status. Do not run any root or Owner status before this evidence file exists. Identity queries and one-per-output check-ignore commands may occur before CreateNew, but status cannot.

The executor may perform only the frozen source/status/index/path/ACL/stream/hash checks, exact CreateNew writes, one File.Replace, Parser/selfcheck and capability query described by attempt2 and attempt3. No retry, cleanup, rollback, replacement API, temporary file, shell, user-file access, or unrelated write is allowed. Preserve all partial outputs and evidence on failure.

## 3. Process observation supplement

The main executor must run in C:\Program Files\PowerShell\7\pwsh.exe, PowerShell 7.6.6/Core/FullLanguage, from the frozen root, identity and SID. Windows PowerShell 5.1 powershell.exe is forbidden. The only permitted child images remain the exact frozen Git executable and the two exact PowerShell 7 validation children from attempt2.

Attempt3 adds in-process Toolhelp32 process snapshots using kernel32 CreateToolhelp32Snapshot with TH32CS_SNAPPROCESS, Process32FirstW, Process32NextW and CloseHandle. The executor uses Reflection.Emit and in-memory P/Invoke declarations; it must not invoke Add-Type, a compiler, WMI/CIM, another process, or write a temporary artifact. Each observation records the root/descendant PID, ParentPID and executable name. Take an in-process snapshot before every protected write and at the next process checkpoint before any subsequent child or write and repeatedly at 10 ms intervals for each permitted child’s lifetime; also sample after child exit. Seed descendant closure with the root PID and every PID previously launched by the executor, including exited parents, before walking the current parent graph. Any observed process other than the current exact allowed child, an unknown descendant, ambiguous PID ownership, API error, missing root, handle-close error, incomplete stdout/stderr capture or monitor failure sets process closure blocked and fail-stops before any later protected operation.

The monitor’s evidence is a sampled process snapshot, not a proof that an arbitrary process shorter than the sampling interval never existed. Report that limitation; do not call the result proof of absolute process absence. Runtime correctness of the emitted P/Invoke ABI, buffer layout and last-error propagation is NOT_VERIFIED until the reviewed executor runs. The native structures must set dwSize to the documented PROCESSENTRY32W size and use the architecture-correct parent-PID and image-name offsets. The P/Invoke declarations must preserve the native return values and SetLastError behavior; any discrepancy in the static Review blocks execution.

Primary API references for the static review:
- Microsoft Learn, CreateToolhelp32Snapshot: https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-createtoolhelp32snapshot
- Microsoft Learn, Process32FirstW: https://learn.microsoft.com/en-us/windows/win32/api/tlhelp32/nf-tlhelp32-process32firstw
- Microsoft Learn, TypeBuilder.DefinePInvokeMethod: https://learn.microsoft.com/en-us/dotnet/api/system.reflection.emit.typebuilder.definepinvokemethod
- Microsoft Learn, Marshal.GetLastPInvokeError: https://learn.microsoft.com/en-us/dotnet/api/system.runtime.interopservices.marshal.getlastpinvokeerror

## 4. Git child and status phase supplement

Use only C:\Program Files\Git\cmd\git.exe with ProcessStartInfo.UseShellExecute=false, each argument as an ArgumentList item, and the exact root or Owner WorkingDirectory from attempt2. No aliases, -C, command string, wrapper, pager, hook, fsmonitor, shell, or other Git process is allowed. Keep attempt2’s exact repository identity commands and its exact fixed status/check-ignore argument lists.

The executor removes the frozen inherited Git context variables and all GIT_TRACE* entries from each child. It records removed variable names but not values. Any inherited Git context override or any GIT_CONFIG* configuration-injection variable causes fail-stop before launching that child. It sets GIT_OPTIONAL_LOCKS=0 and GIT_TERMINAL_PROMPT=0. Do not broaden or silently reinterpret this environment boundary.

Required sequence:
1. Perform fixed Git identity queries and per-output check-ignore queries before creating the execution evidence. Do not run status.
2. Create the execution-evidence file with CreateNew and flush it.
3. Capture S0-root and S0-owner. S0 is the first status snapshot; Owner must be clean.
4. Capture one separate pre-stage-owner status after S0 and before stage/recovery/Handoff creation. Label it pre-stage-owner, not S0/S1/S2/S3; require it remains clean. This extra Owner status resolves the attempt2 order ambiguity.
5. Create stage, exact recovery bytes and Handoff by CreateNew; capture S1-root. Require exactly those three new status records.
6. Call the three-argument File.Replace exactly once; capture S2-root as the first child after return. Require the exact attempt2 S2 multiset and file/ACL/stream outcomes.
7. Run the exact PowerShell 7 Parser, selfcheck child and capability child from attempt2, capturing their PID, argv, stdout/stderr bytes and hashes, exit codes, output and process samples. Create validation evidence using CreateNew; capture S3-root and require only the two validation-evidence additions.
8. Never modify Task, Plan, STATUS, Index or checkpoint during S0–S2. Governance updates occur only after the operation and validation stages complete or fail.

No other Git child phase is permitted during a normal run.

## 5. Failure-only status phase

A failure diagnostic is not S0/S1/S2/S3 and must never be labeled PASS. It is allowed only after the execution-evidence file was successfully created and only while the process observer is healthy and no unknown/unlisted child or ambiguous process has been observed. In that case the executor may run exactly one FAILURE-root status using the fixed root status argv from attempt2, record its complete process/output evidence, and compare its actual multiset to S0-root when S0 exists; classify it ACTUAL_UNADJUDICATED, not an expected delta. It may also read the exact frozen index file and listed output paths to report actual state.

If execution-evidence CreateNew fails, if Toolhelp fails, if an unknown/unlisted child or ambiguous PID is seen, or if process closure is blocked, do not launch Git or any other child. Preserve partial outputs, do only already-authorized in-process read-only path/hash checks, and record the best available evidence in the existing execution evidence if it exists. Do not retry, clean, restore or delete anything.

## 6. Validation and Gate limits

Attempt2 sections 5 and 6 remain unchanged. Round6 Parser must report zero errors; the selfcheck must return exit 0 and all frozen assertions must pass; the exact capability query must return its frozen valid output. Parser/selfcheck and engine evidence are real results, not static review. Any failure remains FAILED/BLOCKED as observed; it does not authorize an automatic retry or turn any Gate PASS.

Keep the Owner risk exception exactly:
private_registry_absence=UNPROVABLE
Technical Gate=NOT_SATISFIED
Owner Risk Acceptance=APPROVED
Gate Disposition=WAIVED_BY_OWNER
Build Authorization=AUTHORIZED_WITH_EXCEPTION
technical condition unmet; user explicitly accepted residual risk

Build Gate remains BLOCKED; Hard Build Barrier remains EFFECTIVE; Build/Cargo remains NOT_RUN; system AC1–AC7 remain BLOCKED / NOT_RUN. This protocol does not authorize capture, getters, profile/registry/ACL operations, P02PRE-R2 dynamic isolation, AC1–AC7 or Build/Cargo. Those remain in the existing DAG and can be considered only after the required independent review and evidence-driven Gate adjudication. Windows Sandbox remains forbidden.

## 7. Independent review and adjudication

The non-author Reviewer performs only read-only static review of this exact attempt3 protocol, the frozen executor, exact source and cited prior evidence. Reviewer checks all pins before and after review, does not execute the executor or any validation/OS API, and writes only the designated attempt3 report target with CreateNew. Reviewer reports P0/P1/P2/P3, exact findings and evidence, API/ABI concerns, process-closure limits, status phases, one-replacement behavior, path/write allowlist and Gate statements. Any P0/P1/P2 means CHANGES_REQUESTED; only an unblocked independent APPROVED_STATIC_PROTOCOL plus Codex pin recheck and adjudication can release this integration attempt. Static approval is not execution, Gate or AC PASS.