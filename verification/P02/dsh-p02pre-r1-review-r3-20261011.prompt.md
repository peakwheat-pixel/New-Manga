# DeepSeek Harness Review Task: P02PRE-R1 Round 3

请对以下冻结 bytes 做非作者、只读 Review。不要编辑文件，不要调用 capture script，不要运行 PowerShell/Git/OS/API/registry/WER/token/ACL/path/environment/hash query，不要 build/Cargo/AC，不要改 Gate 或 Task 状态。只检查文件内容与静态契约；遵从 P02 Task 的用户数据范围。

## Exact review-input pins

- Repo=`G:/CODEX/New Manga`; branch=`main`; HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`; tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`.
- Task `doc/tasks/P02PRE-R1.md`: `11866 bytes / SHA-256 6BB5CD644F601658B5C28D11FFA67BA0C4BEBD3E635D73D6DC46BC4B53952DB3`.
- Manifest `verification/P02/p02pre-r1-manifest-20261011.md`: `11908 bytes / SHA-256 06E3351D0DBF0CC5194D61A6E491151CFC58D2FA837DEF97BDCE1F1BC3C01FD2`.
- Script `verification/P02/p02pre-r1-capture.ps1`: `37945 bytes / SHA-256 E97AD8A05B36753FC3F646E480628665328442B0EE8BAACB5C80B45DBDBB5893`.
- Round 2 report `verification/P02/dsh-p02pre-r1-review-r2-20261011.md`: `18951 bytes / SHA-256 DD49F407A2C639DBC53427C5459622D33CBF6B6AC9B56C2335CCD754FD3BF6D8`.
- Current Windows PowerShell 5.1 parser result: version `5.1.26100.9549`, `PARSE_OK`, stderr empty, exit `0`. It used `ScriptBlock::Create` only and did not invoke the capture script. The exact parser outputs are in `verification/P02/p02pre-r1-windows-powershell-parse-r2-20261011.*`.
- R6 source manifest: `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`.

## Authorization and preserved status

The user authorizes the one-time P02 scope including host getters, dynamic isolation, P02PRE, Build/Cargo, AC1–AC7, fixes, reviews, retests and integration, and accepts runner/source-contract and host getter absolute-no-side-effect preproof risk. R0 is closed; do not repeat its static runner/source research. This is not a technical PASS.

Preserve exactly: `private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`. Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`. Windows Sandbox is out of scope by prior user decision.

## Prior Review findings to disposition

### Round 1

Round 1 result=`CHANGES_REQUESTED`, P0/P1/P2/P3=`0/2/6/3`, report=`verification/P02/dsh-p02pre-r1-review-20261011.md`. Round 2 judged 9/11 closed, with P1-1 and P3-1 partially closed. Independently verify against Round 1 and Round 2 reports and state the disposition of every Round 1 item; do not rely on the author’s summary.

### Round 2

Round 2 result=`CHANGES_REQUESTED`, P0/P1/P2/P3=`0/0/3/2`, report pinned above. Findings:

- P2-1: 64 MiB partial path overwrote an earlier top-level stopReason with `EVIDENCE_SIZE_LIMIT_PARTIAL`, losing the first stop reason.
- P2-2: reviewer believed LocalDumps registry `QUERY_ERROR` was not in the global fail-stop. Codex’s inspection of the Round 2 input showed `$werRegistryQueryErrorCount` flowed through `$werQueryErrorCount` into `$queryErrorCount`; to remove ambiguity, the new revision splits WER-directory and WER-registry errors and explicitly adds both into the fail-stop counter. Verify this exact dataflow; treat the old finding as closed only if the revised source is unambiguous.
- P2-3: empty/unavailable owner or SDDL could leave a PRESENT record and permit false ACL `PASS_WITH_EVIDENCE`.
- P3-1: evidence-write exception text did not include the already-known stopReason.
- P3-2: the human-readable `whoami.exe` text decoding used ambient `Console.OutputEncoding` without recording the chosen encoding.

Codex says the current revision: preserves `originalStopReason` on both bounded and minimal size partials; sets a size-limit stop only if no earlier reason exists; distinguishes WER directory/registry error counts and routes both into fail-stop; marks empty ACL owner/SDDL `ACL_UNVERIFIABLE`, classifies ACL snapshots `UNPROVABLE` and stops downstream use; carries stopReason into write failure errors; records text encoding name/code page and states raw bytes remain authoritative. Independently verify each claim and check for regressions/new issues.

## Static review scope

Read the complete pinned Task, manifest, script, Round 1 report, Round 2 report and only necessary R6 sections. Compare exact path/registry/environment allowlists, child executables/arguments, partial serialization, ACL/owner/SDDL classification, stopReason behavior, error counts, protected hashes and sole `CreateNew` write. Check Windows PowerShell 5.1 compatibility. Ensure unknown host home/cache mapping, effective WER policy, missing-object ACL, transient ACL writes, effective permissions, dynamic child/path/write closure and private registry absence remain `UNPROVABLE`/`REQUIRES_ACTIVE_TEST` rather than PASS. Do not infer any runtime result from static review or parser output.

State review coverage and limitations. The first two Reviews could not independently recalculate bytes/SHA because their sandbox ACL initialization failed (`SetNamedSecurityInfoW failed (Win32 5)`); if the same applies, report it honestly and do not claim independent hash verification. Review itself must not read user manga/library file contents or execute commands.

Return a Chinese report with exactly one result from `APPROVED`, `CHANGES_REQUESTED`, `NOT_VERIFIED`, `BLOCKED_BY_MISSING_EVIDENCE`; P0/P1/P2/P3 counts; precise file/line, trigger, impact and fix for any findings; a row for every Round 1 and Round 2 finding marked `CLOSED`, `PARTIALLY_CLOSED`, or `OPEN`; exact scope/limitations; and whether this specific readonly capture script may be released for one invocation. `APPROVED` is review-only, not a Gate PASS.