# Independent Review request — P02PRE-R1F Review Round 5 follow-up #2

You are the independent, non-author Reviewer for Task `P02PRE-R1F`. Review the exact candidate bytes below in read-only mode. The repository is `G:/CODEX/New Manga`, branch `main`, base HEAD `cddff58469b56e181019a8ddfeade80684bc7eb9`; candidate changes are uncommitted in the shared working tree. Codex is the author and adjudicator. You did not author these changes.

## Exact candidate pins

- Task: `doc/tasks/P02PRE-R1F.md` — `21428 bytes / SHA-256 81D4EB50480475B41BCA366C37078B93370E85B1AB8AB6CFAC73F89649765E73`
- Manifest: `verification/P02/p02pre-r1f-manifest-20261011.md` — `20571 bytes / SHA-256 06B724979F8F4065372DACDE0BBE713013864FE4431BD5BE1ACE871DEAE5F946`
- Capture script: `verification/P02/p02pre-r1f-capture.ps1` — `65533 bytes / SHA-256 6B7556C784607B9CA52EC0879895676C13FE1AD67E0639A0C64269C700240CD1`
- Isolated self-check: `verification/P02/p02pre-r1f-r5-followupfix2-selfcheck-20261011.json` — `2308 bytes / SHA-256 1696B781A65D87D210F4CA909891FAF7ACCD088167091DF1EEB381E41A2CF1E2`
- Codex adjudication of follow-up #1 and repairs: `verification/P02/p02pre-r1f-r5-followup2-adjudication-20261011.md` — `6330 bytes / SHA-256 ED8A9D950A75E4BF8778E5F737D40BB73C008A134956C74573C51FAC830B779C`
- Prior independent Review report: `verification/P02/dsh-p02pre-r1f-review-r5-followup-20261011.stdout.md` — `16554 bytes / SHA-256 998905D33EF2FC18766999AE7D184A559836DB9F0AF138AF521787411C934B5D`
- Self-check wrapper attempt #1 evidence: `verification/P02/p02pre-r1f-followupfix-selfcheck-wrapper-attempt1-20261011.md` — `1179 bytes / SHA-256 CABB770B21701E96A083D1FB22E55122ECD89CCA5EE86114A5393697027D9703`

## Review scope

Read only the seven files listed above. Assess the exact candidate and whether Codex correctly adjudicated and fixed each prior finding:

1. `R5F-F1`: stale parser-round wording and ambiguity between Review Round 5 and parser R5–R8.
2. `R5F-F2`: missing/empty PowerShell `LinkType` behavior; sentinel semantics must remain honest and must not inspect/follow a symlink target.
3. `R5F-F3`: protected-hash path lists must not contain duplicate keys or read one file twice.
4. `R5F-F4`: a Windows DOS 8.3 alias form such as `TMPDRI~1/...` must stop before any per-candidate filesystem getter, hash or ACL query.

Also independently inspect the surrounding call order, Windows PowerShell 5.1 syntax compatibility, and any new P0/P1/P2/P3 issue affecting the `.tmp.driveupload` no-content-read boundary, protected-file/hash baseline, sole `CreateNew` output, sub-process/write scope, or whether the next R8 parse and pre-run sequence is accurately described. State any evidence boundary or unresolved limitation plainly. Do not treat the isolated self-check, this Review, or the owner's existing risk waiver as a Gate PASS.

## Strict limits

- Read files only. Do not execute commands, scripts, tests, getters, capture, registry/ACL APIs, or filesystem probes. Do not modify, create, or delete repository files. Do not read `.tmp.driveupload` content or metadata.
- Do not rerun the prior Review or infer test results from static analysis.
- Return a report in stdout only, with `Decision` (`APPROVED` or `CHANGES_REQUESTED`), explicit `P0/P1/P2/P3` counts, finding IDs/severity/evidence/minimal fix, a four-row disposition for `R5F-F1`–`R5F-F4`, and clear statements of what you did and did not execute/read.
- Approval applies only to these seven exact bytes. It does not authorize R8, capture, Build/Cargo, AC1–AC7, or mark any Gate PASS. Codex retains integration and final adjudication responsibility.
