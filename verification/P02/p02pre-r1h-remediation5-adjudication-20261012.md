# P02PRE-R1H Round 5 Codex Adjudication

- Task=`P02PRE-R1H`; Integrator/Adjudicator=`/root`.
- Owner=`/root/p02_r1h_codex_owner`, not Reviewer.
- Independent non-author Reviewer=`/root/p02_r1h_remediation_review`.
- Delivery branch=`agent/codex/P02PRE-R1H`; HEAD=`dd5d2e3bc8e0702da9d059131f6364a997897661`; parent=`7e7d0bce8dd86a2302d2a9eb278702d9c70354ff`; tree=`8cf6cf2dec8b375746b4c423f3c00ffe611a60d7`; frozen Task base/merge-base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`.

## Review evidence and adjudication

Independent Review report=`verification/P02/codex-subagent-p02pre-r1h-static-review-remediation5-20261012.md`, 8,235 bytes / SHA-256=`F4AFD13627E2DA701DC6934FB827CC0D71FFC5454851E3DC94AE0B83BE8A6AEB`. Verdict=`APPROVED_STATIC_CONTENT`; P0/P1/P2/P3=`0/0/0/0`. Reviewer model/effort=`UNKNOWN` because it was not visible in that execution context.

Effective dispatch prompt=`verification/P02/codex-p02pre-r1h-remediation5-review-dispatch-r2-20261012.prompt.md`; prompt pins=`verification/P02/codex-p02pre-r1h-remediation5-review-input-pins-r2-20261012.json`, SHA-256=`756279303267EE0C5381E395284AB038531E1AD7AEF15134CE32843C7B98136E`. The initial dispatch was stopped before substantive Review because it pinned only the already integrated Round4 main bytes. It produced no verdict/report and ran no code. The revised dispatch explicitly separated 12 main reference inputs from 3 Round5 commit candidates. Reviewer and Codex independently confirmed all `12/12` reference and `3/3` candidate pins before/after review; no mismatch. Candidate commit blobs, sizes, and SHA-256 values are captured in the pins file and report.

The exact fix adds only `'$parts.Count'` to `Test-RepositorySkipAstContract`'s `$allowedMemberExpressions`. Round4 failed at the AST allowlist because the actual component-loop body contains the legal `$parts.Count` access in `$isLeaf` assignment. The new allowlist entry is exact; it does not add a wildcard, external member call, API, filesystem access, or permission relaxation. Reviewer confirmed the full frozen Task base→delivery candidate diff and no regression to R1H-001..007 static controls.

Adjudication:

- The Round5 source change is accepted as `APPROVED_STATIC_CONTENT` and the identified static finding is closed.
- R1H-004 selfcheck AST coverage is `FIXED_STATIC_CONTENT`; the missing exact allowlist member is now represented. This does **not** predict successful runtime selfcheck.
- R1H-005=`FIXED_STATIC`; R1H-006=`FIXED_STATIC_COVERAGE`; R1H-007=`FIXED_STATIC`; earlier accepted R1H-001 fail-stop, R1H-002 and R1H-003 remain unchanged.
- Round4 selfcheck execution remains an actual `FAILED` result (PID 48712, exit 1, evidence=`verification/P02/p02pre-r1h-selfcheck-round4-20261012.json`). Do not overwrite or recategorize it.
- Round4 engine preflight remains `PASS_WITH_EVIDENCE` only for its exact execution and inputs (`verification/P02/p02pre-r1h-engine-preflight-round4-20261012.json`).
- AC3 independent Review=`PASS_WITH_EVIDENCE`. AC4=`NOT_VERIFIED` until the Round5 bytes are safely integrated and fixed PowerShell 7.6.6 parser/selfcheck and no-profile engine preflight are rerun successfully. AC5–AC7 remain `NOT_RUN / BLOCKED`.
- Frozen main/scratch status/index baseline remains `UNPROVABLE`. No capture, getter, OS dynamic validation, Build/Cargo, AC1–AC7 system test, or Sandbox action is authorized by this static adjudication.

## Governance and next integration step

The initial Round4 integration wrote the root-owned selfcheck at the AC4 path with `CreateNew`; its expected reviewed working-tree bytes are `57,623` bytes / `EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1`. Round5 is a required revision to that existing root-created integration. The original replacement procedure was not approved: independent protocol Review found two P2 gaps (status delta and Replace exception state). Raw Git blobs are LF-normalized and differ in bytes from the Windows working-tree pins; root independently proved the Round4 and Round5 working-tree files become byte-identical to their respective blobs after CRLF→LF normalization. To avoid reconstructing line endings, the revised Task procedure creates a dedicated `CreateNew` recovery copy from the exact, hash-verified local destination, then calls `File.Replace(stage, destination, apiBackup)` with a separate, absent API backup path; it requires exact four-path state evidence, allows only the recovery/API-backup status deltas on success, and forbids automatic retry/cleanup/rollback after exceptions. These revisions require a new non-author Review and Codex adjudication before any replacement. Capture and Handoff bytes remain unchanged. This is task integration only; it adds no product scope and releases no Gate.

## Raw Git blob and Windows working-tree byte reconciliation

Using the configured Windows PowerShell 7.6.6 runtime, root read the pinned local Round4 target, the pinned Owner Round5 worktree candidate, and each corresponding Git blob. For each working-tree byte array it removed only CR bytes immediately followed by LF and compared every remaining byte against the Git blob; both normalized arrays matched exactly:

| File | Working-tree bytes / SHA-256 | Git blob bytes / SHA-256 | CRLF pairs | normalized exact match |
|---|---|---|---:|---|
| Round4 integrated target | 57,623 / `EEFB41141EBE162503047C20CAF4F41D5E8E01EEF2FCEE0C90DA7185A8164CF1` | 56,901 / `31CFCEB6E78830C294DA4E32A5A7CB495B1262CE0F684DDA1CA69DDDEC239D7E` | 722 | yes |
| Round5 Owner candidate | 57,648 / `977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA` | 56,925 / `31E996B03A3F2400F3920F5C5B3C8A2A8DAA62C0A5603E1F901571BDE210F376` | 723 | yes |

This proves the byte-length/hash differences are the expected CRLF checkout representation, not a code-content mismatch. It does not prove file metadata or ACL equivalence. The execution protocol therefore still copies the exact verified current target bytes into a dedicated `CreateNew` recovery file and separately retains the API-generated backup.

## Gate (unchanged)

`private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`; Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN` for system acceptance. No technical condition is represented as PASS by the owner waiver or this Review.

### Actual Review boundary

Reviewer performed read-only hashes, Git metadata/diff and static inspection, and wrote only its designated report. It did not run the Round5 parser/selfcheck/fixtures, preflight, capture, getter/API, tests, Build/Cargo, ACs, OS dynamic validation or Windows Sandbox. Codex root independently recalculated all 15 frozen file pins and verified delivery refs/status; no candidate execution has occurred after this static Review.
