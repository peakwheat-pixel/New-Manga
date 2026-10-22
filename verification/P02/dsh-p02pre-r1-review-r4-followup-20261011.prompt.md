# DeepSeek Harness Review Task：P02PRE-R1 Round 4 窄范围复核

这是同一 Round 4 `CHANGES_REQUESTED` 后的 focused follow-up，Reviewer=`DeepSeek Harness`；Owner/Author/Integrator/Adjudicator=`Codex /root`。仅核 manifest 的两处过期文字及同一证据中 parser 输入/hash/result 的绑定。不要编辑文件，不要调用 capture script，不要运行 PowerShell/Git/OS/API/registry/WER/token/ACL/path/environment/hash query，不要 build/Cargo/AC，不要改 Gate 或 Task 状态。只读取以下冻结文件内容。

## Exact pins

- Repo=`G:/CODEX/New Manga`; branch=`main`; HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`; tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Current Task `doc/tasks/P02PRE-R1.md`: `16148 bytes / SHA-256 998586262234FFC67151B9831933DF2329415CC2354702AEC32CF7392F84AFCB`。
- Revised manifest `verification/P02/p02pre-r1-manifest-20261011.md`: `12598 bytes / SHA-256 41D4EBFD36135AA3AACFCE62DE0D6A4BF23C98D2B8F69103B422F2CDE4A1F144`。
- Capture script (unchanged since R4 Review): `verification/P02/p02pre-r1-capture.ps1`, `38729 bytes / SHA-256 97400A9EF16E47242DA3C4E53C8265F16BA9A70853B26D3905748B9CA69884AB`。
- R4 full report `verification/P02/dsh-p02pre-r1-review-r4-20261011.md`: `18995 bytes / SHA-256 DD099DCDCA59E1C7EBBB5B9A938C2F50BF31A9F5B39872B738874CF4DEB7ED98`；it closed all 19 Round 1–3 findings and left only P3-DOC-1.
- Hash-bound parser artifact `verification/P02/p02pre-r1-windows-powershell-parse-r4-20261011.json`: `2086 bytes / SHA-256 1AE3462C5EB16E85B47A03E90CBC53DA33F5EAD74BFCFB1992BADC5F6A805841`.

## Required checks

1. Confirm manifest `:9` now says the three R3 findings (path snapshot classification, manifest round wording, retaining direct entry count on `Get-Acl` failure) were revised for R4 and are awaiting current Review/adjudication, with no false approval claim.
2. Confirm manifest `:13` points the single host capture to the current R4 independent Review and Codex adjudication, with no stale “second-round review” prerequisite.
3. Inspect the parser JSON content and confirm it records Windows PowerShell `5.1.26100.9549`, `ScriptBlock::Create`, `PARSE_OK`, process exit `0`, `captureScriptInvoked=false`, the exact script byte count/SHA above, and an in-process parent recheck match. The artifact also preserves raw startup-progress stderr bytes/hash/base64.
4. Confirm the script pin is unchanged from the R4 full review input. R4 already found no script defect or side-effect risk; do not repeat the full source review unless a material inconsistency appears.
5. Confirm the change did not alter any preserved Gate or owner-risk state. This review is not a Gate PASS.

If hashes cannot be independently recalculated because of the known DSH sandbox ACL failure (`SetNamedSecurityInfoW failed (Win32 5)`), report that limitation; do not claim independent hash verification. Do not read user manga/library file contents or execute any command.

Return a Chinese report with exactly one result from `APPROVED`, `CHANGES_REQUESTED`, `NOT_VERIFIED`, `BLOCKED_BY_MISSING_EVIDENCE`; P0/P1/P2/P3 counts; a disposition for P3-DOC-1; exact scope/limitations; and whether the unchanged readonly capture script may proceed to Codex adjudication for one invocation. `APPROVED` is review-only, not Gate authorization.
