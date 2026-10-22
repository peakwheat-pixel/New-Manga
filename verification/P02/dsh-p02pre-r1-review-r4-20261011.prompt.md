# DeepSeek Harness Review Task：P02PRE-R1 Round 4

请对以下冻结 bytes 做非作者、只读 Review。Reviewer=`DeepSeek Harness`；Owner/Author/Integrator/Adjudicator=`Codex /root`。不要编辑文件，不要调用 capture script，不要运行 PowerShell/Git/OS/API/registry/WER/token/ACL/path/environment/hash query，不要 build/Cargo/AC，不要改 Gate 或 Task 状态。只检查文件内容与静态契约；遵从 P02 Task 的用户数据范围。

## Exact review-input pins

- Repo=`G:/CODEX/New Manga`; branch=`main`; HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`; tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Task `doc/tasks/P02PRE-R1.md`: `14115 bytes / SHA-256 C1E5EFE4129C594FD3D688248D7CAA85786EDA117A26375ADFF966A2A6112069`。
- Manifest `verification/P02/p02pre-r1-manifest-20261011.md`: `12489 bytes / SHA-256 23FF89EC419DF0D31071BBBD6646D9BA9E063A6D30718F64141E266CEA0F8662`。
- Capture `verification/P02/p02pre-r1-capture.ps1`: `38729 bytes / SHA-256 97400A9EF16E47242DA3C4E53C8265F16BA9A70853B26D3905748B9CA69884AB`。
- Round 3 report `verification/P02/dsh-p02pre-r1-review-r3-20261011.md`: `17502 bytes / SHA-256 0CFD9402D196E4BB1477A1325F6FD6D26331F4993C0956565795F8A9D7CBA4B9`; raw DSH JSONL is in the same directory.
- R3 revised-script parser evidence used Windows PowerShell `5.1.26100.9549` and `ScriptBlock::Create` only. stdout=`verification/P02/p02pre-r1-windows-powershell-parse-r3-20261011.stdout.log` (`45 bytes / SHA-256 C076120D0E62CF013CE1C521C5F091133497468263805D4B417F968B910D952A`, `PARSE_OK`); stderr=`verification/P02/p02pre-r1-windows-powershell-parse-r3-20261011.stderr.log` (`382 bytes / SHA-256 4F2B6B3ED9201CA459DB2DD042E0A137C4E58BFE8E15A068E45AD8535FA5B1EF`, PowerShell startup progress CLIXML); exit file=`verification/P02/p02pre-r1-windows-powershell-parse-r3-20261011.exit` (`0\r\n`, 3 bytes / SHA-256 `13BF7B3039C63BF5A50491FA3CFD8EB4E699D1BA1436315AEF9CBE5711530354`). This parser did not invoke the capture script.
- R6 source manifest=`verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`.

## Authorization and preserved status

The user authorizes the one-time P02 scope including host getters, dynamic isolation, P02PRE, Build/Cargo, AC1–AC7, fixes, reviews, retests and integration, and accepts runner/source-contract and host-getter absolute-no-side-effect preproof risk. R0 is closed; do not repeat its static runner/source research. This authorization is not a technical PASS.

Preserve exactly: `private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`. Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`. Windows Sandbox remains out of scope by prior user decision.

## Prior Review findings to disposition

Round 1=`CHANGES_REQUESTED` (`0/2/6/3`), Round 2=`CHANGES_REQUESTED` (`0/0/3/2`), and Round 3=`CHANGES_REQUESTED` (`0/0/1/2`). Read the complete Round 1, Round 2 and Round 3 reports, the current Task, manifest and script. Independently verify the Round 3 fixes and state the disposition of every finding from all three rounds; do not rely only on the author summary.

### Round 3 findings requiring closure

- P2-1: `ACL_UNVERIFIABLE` previously allowed `hostPathSnapshots=PASS_WITH_EVIDENCE` while `hostAclSnapshots=UNPROVABLE`. Verify the revised classifier cannot report PASS when any applicable path ACL is unverifiable. Verify query errors and missing input roots retain their correct classifications.
- P3-1: manifest header previously described an R2 freeze while containing R3 edits. Verify it now identifies the current review round without falsely claiming approval.
- P3-2: `Get-Acl` exception previously discarded `directEntryCount` and attributes. Verify the revised getter keeps already-collected metadata and count, accurately classifies ACL failure, and uses a known positive count to detect a nonempty scratch leaf even if its ACL query fails.

Also check how `ACL_QUERY_ERROR` flows through `hostPathSnapshots`, `hostAclSnapshots`, summary counters and the stop condition; ensure the new status cannot be misread as PASS or silently omit a failure.

## Static review scope

Review the complete frozen Task, manifest, script and relevant R6 source rows. Verify exact read/path/registry/environment allowlists, child executables/arguments, partial serialization, status classification, query-error counts, protected-file hashes and the sole `CreateNew` evidence write. Check Windows PowerShell 5.1 compatibility of the current revision. Ensure host home/cache mapping, effective WER policy, missing-object ACL, transient ACL writes, effective permissions, dynamic child/path/write closure and private registry absence remain `UNPROVABLE`/`REQUIRES_ACTIVE_TEST`, not PASS. Do not infer runtime results from static review or parser output.

State review coverage and limitations. Prior DSH reviews could not independently recalculate bytes/SHA because sandbox ACL initialization failed (`SetNamedSecurityInfoW failed (Win32 5)`); if this still applies, report it honestly and do not claim independent hash verification. Do not read user manga/library file contents or execute commands.

Return a Chinese report with exactly one result from `APPROVED`, `CHANGES_REQUESTED`, `NOT_VERIFIED`, `BLOCKED_BY_MISSING_EVIDENCE`; P0/P1/P2/P3 counts; precise file/line, trigger, impact and minimum fix for each new finding; a row for every Round 1, Round 2 and Round 3 finding marked `CLOSED`, `PARTIALLY_CLOSED`, or `OPEN`; exact scope/limitations; and whether this specific readonly capture script may be released for one invocation. `APPROVED` is review-only, not a Gate PASS.
