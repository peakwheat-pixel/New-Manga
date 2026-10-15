# Codex adjudication r1 — P02-NEW-TIME-X6-POSTRUN-REVIEW

## Decision

**ACCEPTED_WITH_BACKLOG** for the new-time X6 result only. DSH reviewed Task `P02-NEW-TIME-X6-POSTRUN-REVIEW`, `reviewed_head=303dbe5c7f5b8bcb1902b16ad5c208e205a6b50c`, RunId `x6-20261014T1305CST-p02-newtime-r1`, and immutable manifest r2 SHA-256 `BD049F9E4C20363E837900256CDFF21C3D972C44E915A7EC0B3F3DE234922DC4`. DSH decision=`APPROVED`; P0/P1/P2/P3/P4=`0/0/0/1/6`.

Codex independently verified 10/10 immutable Git inputs, 14/14 external inputs, all 282 DSH JSONL events and the single final event, exact report-byte copy (SHA-256 `A05018611820D571A6DD098E0F327AEBFFFBD568B7F5F1E456322255EB19E6FE`), the frozen Task blob, source pins and commit ancestry. Deterministic verification output is `G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6-POSTRUN-REVIEW/codex-postrun-pin-verify-r1/stdout.json` (1,847 B; SHA-256 `44484FC01554A75526926B980EE0831A50B9171012088C72B3B8FF2AF75945F6`; exit 0). DSH's shell limitation therefore does not leave a missing integrity check.

The official result protocol returned `ACCEPT` (artifact complete, verification pass; stdout SHA-256 `6B02A7199A2B700835859BEFCBEB4D164067E77EB3A7BA046F4F8EA34873BF5D`). The official convergence helper dry-run and live run both returned `APPROVED`, `REPLAN_DAG`, `BACKLOG_NONBLOCKERS`, `wait_external=false`, with no follow-up/resolution Task and no I repair. Live output SHA-256 `C7BDEE323166D2407EAE156CA3350ACFF28842EF86C1E48BBB664EA5FE3ED320`; input SHA-256 `EAE539D5A905224505D7D81A24BE1B1770D0B969CC1BD3CF913E3D8E2353F015`. Documentation pointer normalization/dedup was separately classified `E`, no I-budget use, `reviewer_needed=false` (output SHA-256 `615A70A4403C3CEA0098CD886AEADA50279A64852F094CA19055E714A6A21C6A`). Full commands, inputs, outputs, stderr and exits remain in the referenced workspace directories.

## Finding adjudication

| Finding | Disposition | Gate impact |
|---|---|---|
| `X6-PR-01` P3 — two byte-identical temp captures omitted from the frozen output-target inventory | BACKLOG; preserve both files and their pins. No rerun or move. The frozen X6 result and security boundary remain verifiable. | Non-blocking |
| `X6-PR-02` P4 — source manifest r2 has a superseded selftest pin | BACKLOG; the execution freeze and source Review r3 both pin the final selftest, and Codex verified the source blobs match. | Non-blocking |
| `X6-PR-03` P4 — noncanonical dry-run manifest has two different blob IDs | BACKLOG; `frozen_git_checked=false`; the live manifest is canonical and was verified. | Non-blocking |
| `X6-PR-04` P4 — manifest r2 verification attempt lacks its own command file | BACKLOG; keep the preserved verification output/exit and r1 command example; no input or result mismatch. | Non-blocking |
| `X6-PR-05` P4 — duplicate selftest source row in the X6 branch Task | BACKLOG; the root working copy was normalized before dispatch. Leave the reviewed branch snapshot unchanged; its duplicate does not affect the pin or result. | Non-blocking |
| `X6-PR-06` P4 — `delivery_head` is used for two different snapshots | Accepted as a naming ambiguity, not a lineage failure: `839e0089…` is code delivery/source Review, `717b2c1…` is the executed worktree snapshot frozen in the manifest, and `303dbe5…` is the post-run evidence review head. Codex verified ancestry `839e0089→717b2c1→303dbe5→1c43e138→4e72e2b8→49d2a2f9`; the five runtime source blobs are identical at `839e0089` and `717b2c1`. Record the distinct semantics in this adjudication. | Non-blocking |
| `X6-PR-07` P4 — DSH could not run shell/Git/hash tools | Accepted limitation; Codex independently recalculated the frozen/external hashes, ancestry, source blobs, Task blob and dispatch artifacts. No second DSH dispatch is needed. | Non-blocking |

No finding is upgraded to P0/P1/P2. No I1/I2 counter is changed; the parent X6 budget remains `1/2`, this verification Task used `0/2`, and I3 remains forbidden. P3/P4 items remain visible as backlog and do not trigger repair or another review.

## Scope and next gate

This decision supports only the current new-time X6 result. It does **not** supplement, replace, close, or rewrite old H1/P2-1 conclusions or the 13 missing raw-source records. The X6 result is not old-path evidence. Build/Cargo and product AC1–AC7 were not run during this Review; they remain unreleased until the separate Build/Cargo Task is frozen, registered in the DAG and passes its own preflight. The next eligible stage is Build/Cargo, followed by a separate Build result Review before any product AC1–AC7 Task is released. No `BLOCKED_WAITING_EXTERNAL_DECISION` condition is met.
