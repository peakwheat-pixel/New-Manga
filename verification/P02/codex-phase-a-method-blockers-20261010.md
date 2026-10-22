# P02 Phase A measurement method blockers

Status: `BLOCKED / NOT_RUN`. This is a design-readiness assessment, not a test result, OS measurement, or Gate decision.

## Baseline and sources

- Live repository at assessment: `G:\CODEX\New Manga`, `main@cddff58469b56e181019a8ddfeade80684bc7eb9`, tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`.
- P02 Task authorization is recorded under `PROJECT_ORCHESTRATION_AUTHORIZATION`; user authorization allows Codex to select precise local isolation scope but is not evidence or Gate approval.
- Inputs: [P02 r7 adjudication](codex-appcontainer-contract-r7-adjudication.md), [contract r7](appcontainer-isolation-contract-r7.md), and [read-only manifest r3](appcontainer-readonly-preflight-r3.md).
- Read-only consultation: ExpertAdvisor `/root/p02_isolation_advisor`, actual configuration `gpt-6.1-sol/high`. It made no file changes and ran no APIs or measurements. Its conclusion is technical advice only, not an independent Review or Gate.

## Findings

1. `METHOD_BOOTSTRAP`: r3 does not freeze the exact implementation binding, startup sequence, native structure/layout handling, handle flags, access masks, or error mapping for token/security/file-ID queries. A native API call plan does not establish that PowerShell/CLR loading and execution cause no undeclared file access, child launch, or cache write.
2. `PROGRAMDATA_EQUIVALENCE`: r3's 23-variable allowlist omits `ProgramData`, while WER targets require a `%ProgramData%` path. No allowed evidence currently establishes that a special-folder resolver equals this process's environment mapping. Do not read a 24th variable or guess the mapping.
3. `NO_CHILD_NO_WRITE_EVIDENCE`: r3 forbids child-process checks and defines no external OS observation or enforcement that covers short-lived descendants and all write attempts. The selected API handles being read-only is not proof that the whole host process tree wrote nothing.
4. `PRIVATE_REGISTRY_ABSENCE`: remains `UNPROVABLE / BLOCKED` under the currently approved method. Do not create a profile or query speculative private-registry paths.

## Candidate APIs are advisory only

The ExpertAdvisor suggested specific read methods (including `GetTokenInformation`, `NtOpenFile` with `OBJ_DONT_REPARSE`, `GetSecurityInfo` limited to owner/DACL/label, explicit-view `RegOpenKeyExW`, and `FileIdExtdDirectoryInfo`). These are unapproved candidates only. They do not solve the bootstrap or process-tree/write-observation gaps and have not been independently reviewed against the complete r3 access contract. No API was invoked.

A new executable manifest must first define the allowed bootstrap, exact paths/fields/permissions, T0/T1 ordering, all failures, output and hash preservation, and a separately reviewed OS mechanism that can observe/enforce every descendant and write boundary without unenumerated writable paths. If that cannot be demonstrated within the user's authorization and available local capabilities, retain `BLOCKED / NOT_RUN`.

## Gate state

`profile=NOT_CREATED`; `ACL/registry=NOT_MODIFIED`; `OS isolation preflight=NOT_RUN`; `Build Gate=BLOCKED`; `build=NOT_AUTHORIZED / NOT_RUN`; `Hard Build Barrier=EFFECTIVE`; `AC1–AC7=BLOCKED / NOT_RUN`. No tests, Cargo, build, profile/ACL/registry operation, Windows Sandbox operation, or OS measurement was performed for this memo.
## Additional method defects and OS observation limits

- `FILE_INFO_CLASS_MISMATCH`: contract r7 §5, line 115 proposes `GetFileInformationByHandleEx(FileHardLinkInfo)`. Microsoft's valid `FILE_INFO_BY_HANDLE_CLASS` table lists `FileStandardInfo`, `FileStreamInfo`, and directory/file ID classes, but not `FileHardLinkInfo`. `FILE_STANDARD_INFO.NumberOfLinks` exposes a link count; a conservative unreviewed candidate is to block whenever it exceeds 1. `FileStreamInfo` enumerates streams for the opened handle. These are design suggestions only; no API was called and r7 requires correction/re-review. Sources: [GetFileInformationByHandleEx valid classes](https://learn.microsoft.com/en-us/windows/desktop/api/winbase/nf-winbase-getfileinformationbyhandleex), [FILE_STANDARD_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_standard_info), [FILE_STREAM_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_stream_info).
- The ExpertAdvisor considered `DEBUG_PROCESS` + a Job Object + ETW as a possible observer, then rejected it as complete evidence: Microsoft's process creation documentation says the debug chain ends when another process in that chain is created with `DEBUG_PROCESS`; Job Object defaults do not cover children created using `Win32_Process.Create`; NT Kernel Logger control requires admin or LocalSystem; ETW exposes event/buffer loss counters. Thus this candidate cannot certify every transient descendant and every file operation under the current non-elevated, path-limited scope. Do not elevate, install a tool, or widen write paths to make it work. Sources: [process creation flags](https://learn.microsoft.com/en-us/windows/desktop/ProcThread/process-creation-flags), [Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects), [StartTrace permissions](https://learn.microsoft.com/en-us/windows/win32/api/evntrace/nf-evntrace-starttracea), [ETW loss counters](https://learn.microsoft.com/en-us/windows/desktop/ETW/event-trace-properties).

These are newly discovered design blockers, not test failures. No Windows API, ETW session, process observer, profile, ACL, registry, build, Cargo, or Windows Sandbox operation was performed.