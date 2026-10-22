# P02PRE-R1H Round6 controlled integration and AC4 protocol — Review attempt 2

Status: REVISED_FROZEN_FOR_INDEPENDENT_REVIEW
Task: P02PRE-R1H
Integrator/Executor: Codex root
Independent protocol Reviewer: /root/p02_r1h_remediation_review (non-author)
Owner: /root/p02_r1h_codex_owner
Scope: exact installation of the statically reviewed Round6 selfcheck, creation of the matching Handoff and evidence, then PowerShell 7 parser/selfcheck and no-profile capability preflight only.

## 1. Fixed source and destination

Owner branch=agent/codex/P02PRE-R1H; HEAD=c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d; parent/base=dd5d2e3bc8e0702da9d059131f6364a997897661; tree=96e7273ddd5fd27bee567bba27f19453cabe0842; common-dir=G:/CODEX/New Manga/.git; controlled Owner status was empty at Review. Owner source selfcheck is 57812 bytes / SHA-256 6BD9160854275DA94C61B8FC48B180CD16368AF56C2AF7D63D616490A1AB85A9. Owner capture source is frozen at 93124 bytes / SHA-256 0BD41442800BA2336B277C3F8C16C41D4DDF983B2B5D5967378A9EF564078DA3 and is not to be copied or changed. Owner Handoff source is 3551 bytes / SHA-256 700B79F3FA01308DFFEC374A4FFB92DAC69C2FD8355DE623F6A250E9F1511658. Existing root capture verification/P02/p02pre-r1h-capture.ps1 is protected at 93124 / 0BD41442800BA2336B277C3F8C16C41D4DDF983B2B5D5967378A9EF564078DA3. Existing root Round5 Handoff verification/P02/p02pre-r1h-handoff-20261012.md is protected at 8651 / 394CCF80E58017798CA2994C0505F2F5B5BB571143D21C655CEFC77B6173520F.

Root main=main@cddff58469b56e181019a8ddfeade80684bc7eb9; tree=c25d051a4b9a0bd9773b50170e100f575ea19f2b; common-dir=G:/CODEX/New Manga/.git; index SHA-256=214767403C469B15D2BDEE786080E58B4D78BF12C541B9FFB7E8A7FA08F3B89C. Existing root destination verification/P02/p02pre-r1h-selfcheck.ps1 is the prior Round5 integrated artifact, not arbitrary scratch data: ordinary System.IO.FileInfo, attributes Archive, 57648 bytes / SHA-256 977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA. Its read-only observed security descriptor was O:S-1-5-21-2196946971-914346751-4210154634-1001 G:S-1-5-21-2196946971-914346751-4210154634-1001 D:AI(A;ID;0x1301bf;;;S-1-5-21-2196946971-914346751-4210154634-1003)(A;ID;0x1301bf;;;S-1-5-21-884840046-396652784-710274065-85489587)(A;ID;FA;;;BA)(A;ID;FA;;;SY)(A;ID;0x1301bf;;;AU)(A;ID;0x1200a9;;;BU). The only observed stream is the default data stream, length 57648. The destination is currently untracked relative to root HEAD; do not infer absence from Git status.

The current execution host was observed as C:\Program Files\PowerShell\7\pwsh.exe, PowerShell 7.6.6/Core/FullLanguage, user HOME-MY\49745, SID S-1-5-21-2196946971-914346751-4210154634-1001, administrator=false. Re-verify these values immediately before any integration write; a mismatch stops before writing.

## 2. Exact write manifest

Only these project paths may be written for the integration and AC4 evidence:

- Existing destination: verification/P02/p02pre-r1h-selfcheck.ps1. It may be changed only by the single reviewed three-argument File.Replace described below, after exact old/new pins and prechecks pass.
- New stage: verification/P02/p02pre-r1h-selfcheck-round6-stage-20261012.ps1.
- New byte recovery: verification/P02/p02pre-r1h-selfcheck-round5-recovery-20261012.ps1.
- New File.Replace backup: verification/P02/p02pre-r1h-selfcheck-round5-integrated-backup-20261012.ps1.
- New Handoff: verification/P02/p02pre-r1h-round6-handoff-20261012.md, copied from the pinned Owner Handoff with CreateNew.
- New execution evidence: verification/P02/p02pre-r1h-integration-round6-execution-20261012.json.
- New parser/selfcheck evidence: verification/P02/p02pre-r1h-selfcheck-round6-20261012.json.
- New child capability evidence: verification/P02/p02pre-r1h-engine-preflight-round6-20261012.json.
- The separately frozen Review prompt, pins, report, protocol-adjudication report and rolling checkpoint at the exact paths recorded in the Task and frozen Review artifacts.

All stage/recovery/backup/Handoff/evidence paths must be rechecked immediately before execution: absent, unignored, ordinary parent directory, same G: NTFS volume where applicable, no reparse component. If any path exists, is ignored, is a reparse point, or cannot be queried, stop before the first write. Do not clean or repurpose any collision. The destination must still be the exact prior Round5 ordinary file with the frozen length and hash above; any mismatch stops. The Owner source and Handoff pins, plus both protected root files, must remain exact. No other file may be written; read-only access is limited to the frozen inputs and explicitly enumerated paths here. Do not read, enumerate, resolve, stat, hash, open, follow, or otherwise query anything under `.tmp.driveupload`; treat it as excluded and unavailable. Do not query/follow user data, registry/profile/ACL/TEMP/cache/scratch paths.

## 3. Required pre-write evidence and process closure

Use only PowerShell 7.6.6/Core via `C:\Program Files\PowerShell\7\pwsh.exe` (PowerShell 7, not Windows PowerShell 5.1). Record actual PID, executable, version, edition, language mode, user, SID, and administrator status. CreateNew/File.Replace and all file/ACL/hash/path queries run in the root PowerShell 7 process. The only permitted child executable is `C:\Program Files\Git\cmd\git.exe` for the read-only queries frozen in §3.1, plus exactly two PowerShell 7 validation children frozen in §3.2. Launch each child with `ProcessStartInfo.UseShellExecute=false` and `ArgumentList`; capture PID, executable, working directory, each argument item, start/finish time, stdout/stderr byte counts and hashes, and exit code. Do not start a shell, wrapper, pager, hook, fsmonitor, external diff, or any other child. Stop if any unlisted child or descendant is observed.

### 3.1 Fixed read-only Git child manifest

Git executable is exactly `C:\Program Files\Git\cmd\git.exe`. `ProcessStartInfo.WorkingDirectory` is exactly `G:\CODEX\New Manga` for main-repository queries and exactly `C:\Users\49745\.codex\worktrees\p02pre-r1h-codex` for Owner-worktree queries; no `-C`, shell, alias, or command-string execution. Every invocation uses this exact argument prefix as separate `ArgumentList` items: `--no-pager`, `-c`, `core.fsmonitor=false`, `-c`, `core.hooksPath=NUL`. The only permitted subcommands/remaining arguments are:

- Repository identity on each worktree: `symbolic-ref`, `--short`, `HEAD`; `rev-parse`, `--show-toplevel`; `rev-parse`, `--git-common-dir`; `rev-parse`, `HEAD`; `rev-parse`, `HEAD^{tree}`. On the Owner worktree only, also `rev-parse`, `HEAD^`.
- Controlled status snapshots on each worktree at S0/S1/S2/S3 as applicable: append `--no-optional-locks`, `status`, `--porcelain=v2`, `-z`, `--untracked-files=all`, `--no-renames`, `--ignore-submodules=none`, `--`, `.`, `:(exclude).tmp.driveupload`. Each item is a separate argument. Never run status without the final separate exclude pathspec.
- Ignore checks, once per each new integration output path enumerated in §2: `check-ignore`, `--no-index`, `--quiet`, `--`, `<one exact relative output path>`. Exit 1 means that path is not ignored; exit 0 means stop before writes; any other exit is an error and stops. Do not batch away per-path results.

Run repository identity checks for main and Owner before any output creation and repeat them immediately before the first stage/recovery/Handoff write. Run the seven per-path ignore checks during the same pre-write pass. Run main and Owner controlled status for S0 after the execution-evidence file has been created with CreateNew; main status for S1 after stage/recovery/Handoff creation; main status for S2 immediately after File.Replace; and main status for S3 after both validation-evidence files are created. Do not launch Git for any other phase. For every Git child, capture its exact `ArgumentList`, `WorkingDirectory`, PID, stdout/stderr bytes and hashes, and exit code in the execution evidence. Use `ProcessStartInfo.Environment` to remove inherited `GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_COMMON_DIR`, `GIT_PREFIX`, `GIT_CEILING_DIRECTORIES`, `GIT_EXTERNAL_DIFF`, and all `GIT_TRACE*` keys; set `GIT_OPTIONAL_LOCKS=0` and `GIT_TERMINAL_PROMPT=0`. Any inherited Git context override or unexpected Git child stops execution.

Use no other Git invocation. Disable optional locks with the status argument above; `core.fsmonitor=false` and `--no-pager` prevent those helpers; the listed query subcommands do not invoke hooks. Capture all Git process evidence in the execution JSON. PowerShell/.NET performs the frozen file SHA-256, ACL, stream, path, and index-file hash reads without spawning a child. The `.tmp.driveupload` path itself remains excluded: do not inspect its contents or metadata through any filesystem API.

### 3.2 Fixed PowerShell validation children

Both children use executable `C:\Program Files\PowerShell\7\pwsh.exe`, `WorkingDirectory=G:\CODEX\New Manga`, `UseShellExecute=false`, `-NoLogo`, `-NoProfile`, and `-NonInteractive`; pass arguments individually through `ArgumentList`.

1. Selfcheck arguments, in order: `-NoLogo`, `-NoProfile`, `-NonInteractive`, `-File`, `verification/P02/p02pre-r1h-selfcheck.ps1`.
2. Engine capability query arguments, in order: `-NoLogo`, `-NoProfile`, `-NonInteractive`, `-Command`, `$ErrorActionPreference='Stop'; $mods=@(Get-Module -ListAvailable Microsoft.PowerShell.Utility,Microsoft.PowerShell.Security | ForEach-Object {[ordered]@{name=$_.Name;version=$_.Version.ToString();path=$_.Path}}); $cmds=[ordered]@{}; foreach($n in @('Get-FileHash','Get-Acl')){$c=Get-Command -Name $n -ErrorAction Stop; $cmds[$n]=[ordered]@{commandType=$c.CommandType.ToString();source=$c.Source;version=[string]$c.Version}}; $o=[ordered]@{version=$PSVersionTable.PSVersion.ToString();edition=$PSVersionTable.PSEdition;psHome=$PSHOME;modulePath=$env:PSModulePath;languageMode=$ExecutionContext.SessionState.LanguageMode.ToString();modules=$mods;commands=$cmds}; ConvertTo-Json -InputObject $o -Depth 8 -Compress`.

No other PowerShell child is permitted. The selfcheck may not call capture, Git, host getters, registry/ACL/profile APIs, Build/Cargo, or system AC. The engine query is limited to the exact command above.

Before creating stage, recovery, Handoff or replacing destination:

1. Recompute and match the Owner branch/HEAD/parent/tree/common-dir/clean controlled status and all three Owner source hashes. Verify the main branch/HEAD/tree and index remain at the frozen values, using only §3.1 Git queries. Every controlled status query must use the frozen separate `.tmp.driveupload` exclusion; do not otherwise touch that path.
2. Resolve and inspect the exact source/destination path chains; reject every reparse component. Confirm the destination is an ordinary file, matches the old Round5 pin, and query its ACL SDDL, stream list and stream content hashes. Query the Owner source and parent-directory ACL/streams read-only. If the destination has an unknown stream or required metadata cannot be read, stop.
3. Confirm every new output path above is absent and not ignored. Recheck that the stage, recovery, backup and destination are in the same directory/volume. Record all initial path states, all protected-file hashes, main index SHA, and the complete controlled porcelain-v2 NUL status record multiset as S0 in the new execution evidence. The evidence file itself must be created using CreateNew before S0 so it is included in the snapshot; its initial state is then frozen.
4. Do not modify Task/Plan/STATUS/Index/checkpoint during S0-to-S2. These governance updates occur only after the operation and checks; their preexisting Git status records stay in the baseline multiset.

## 4. CreateNew and single replacement

After all prechecks pass, use FileStream(CreateNew, Write, FileShare.None) to copy the exact pinned Owner selfcheck working-tree bytes into the unique stage and to copy the exact old destination bytes into the unique recovery. Use CreateNew to copy the pinned Owner Handoff to its absent target. Flush and read back every output; verify exact byte counts and SHA-256. Do not substitute a Git blob for pinned working-tree bytes. Capture S1 before replacement. Relative to S0, the only permitted new status records are stage, recovery and Handoff; index hash must remain unchanged and every unrelated status record identical. A precheck or CreateNew failure stops the sequence; never delete a partial artifact.

Only after S1 and every per-path/hash/ACL/stream check match, call exactly once:
[IO.File]::Replace(stage, destination, apiBackup)
Use the three-argument overload. Do not retry, clean, restore, or call another write API.

Immediately after return, query destination, stage, recovery, API backup and Handoff. Required results: destination=57812 bytes / 6BD9160854275DA94C61B8FC48B180CD16368AF56C2AF7D63D616490A1AB85A9; stage absent; recovery and API backup each equal the exact old destination bytes=57648 / 977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA; Handoff=3551 / 700B79F3FA01308DFFEC374A4FFB92DAC69C2FD8355DE623F6A250E9F1511658. Compare destination and API-backup ACL/stream evidence to the S0 destination; compare recovery content to the old default-stream bytes. Capture S2 status and index; permitted S0-to-S2 delta is exactly the retained recovery, API-backup and Handoff records, with stage absent and destination's prior record unchanged. Retain recovery and API backup. Attributes, timestamps and file identity are not claimed preserved unless separately proven.

If File.Replace throws, a path/hash/ACL/stream/status check fails, or any unexpected child/write is observed, stop immediately. Do not retry, clean, restore or delete. Preserve every partial artifact, capture read-only actual state and exception/HResult, record the exact status/index delta and mark integration BLOCKED for Codex adjudication.

## 5. AC4 parser, selfcheck and child preflight

Only after S2 proves the exact integrated source:

- Use PowerShell 7.6.6/Core direct Parser on the pinned capture.ps1 and the new integrated selfcheck.ps1; record per-file errors and require zero parser errors.
- Execute the assertion selfcheck with the exact no-profile argv from the Task: pwsh.exe -NoLogo -NoProfile -NonInteractive -File verification/P02/p02pre-r1h-selfcheck.ps1. Launch it via ProcessStartInfo.ArgumentList. Capture actual PID, stdout/stderr byte counts and hashes, exit code, and output. Require exit=0 and all positive/negative assertions to pass. The selfcheck itself must not call capture, Git, host getters, registry/ACL/profile API, Build/Cargo or system AC.
- Run exactly the Round5 frozen child capability query command and argv using ProcessStartInfo.ArgumentList and the fixed pwsh.exe. Keep the child query arguments unchanged; record the result in the new Round6 evidence path. Verify PS 7.6.6/Core/FullLanguage and required commands; record actual child PID, argv items, output hashes and exit. No command-string concatenation.
- Create the two validation evidence artifacts with CreateNew; do not reuse Round5 evidence names. Record their exact status additions in a post-test S3 snapshot. Preserve the Round5 parser/selfcheck/engine artifacts unchanged.
- Do not call capture/getters beyond the specified read-only capability query; do not run AC1–AC7, Build, Cargo or Windows Sandbox. A parser/selfcheck failure is a real failure; locate and fix the cause, require a new Owner delivery if source changes, and repeat independent Review before another integration attempt. Never convert failure or missing evidence to PASS.

## 6. Gate and evidence limits

This protocol does not change or waive any Gate. private_registry_absence remains UNPROVABLE; Technical Gate=NOT_SATISFIED; Owner Risk Acceptance=APPROVED; Gate Disposition=WAIVED_BY_OWNER; Build Authorization=AUTHORIZED_WITH_EXCEPTION; preserve exact residual text: technical condition unmet; user explicitly accepted residual risk. Build Gate remains BLOCKED, Hard Build Barrier remains EFFECTIVE, Build/Cargo remains NOT_RUN, and system AC1–AC7 remain BLOCKED / NOT_RUN. The earlier R5 AC2 failure remains historical FAILED until the R6 test produces a new real result. No result in this protocol is evidence for AC1, AC5, AC6, system ACs or Build.
