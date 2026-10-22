# P02PRE-R1H-R6-EXEC-A5 Review adjudication

- Timestamp: 2026-10-12 (Codex adjudication; exact wall-clock time not independently recorded)
- Adjudicator / Integrator: Codex `/root`
- Task: `P02PRE-R1H-R6-EXEC-A5`
- Candidate baseline: `main@343895fb5f0329c0c07a7104ec321b698f967607`, tree `e12bd627c307d4bf3c851dc09d0b82f97c86ec63`
- Owner worktree: `C:/Users/49745/.codex/worktrees/p02pre-r1h-codex`, branch `agent/codex/P02PRE-R1H`, HEAD `c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d`, tree `96e7273ddd5fd27bee567bba27f19453cabe0842`, controlled status `0 records / 0 bytes`.
- Adjudication: static content gate accepted after recorded fixes and limitations. This is not execution authorization by itself; parser/selfcheck and final pre-run remain required.

## Review evidence and pin adjudication

The initial DSH report returned `APPROVED_STATIC_CONTENT` with P0/P1/P2/P3=`0/0/2/3`. That raw verdict did not satisfy the frozen protocol: unresolved P0/P1/P2 findings require `CHANGES_REQUESTED`. Codex therefore recorded `CHANGES_REQUESTED / NOT_GATE_APPROVED` and did not release the executor.

The original review pins manifest was restored byte-for-byte to SHA-256 `21C691A6044757B2F00A10F4FD1A71BFC1A198495FE15BD959C256246B0E9500`. Its historical Task and protocol pins are 7637 bytes / `696D2E690E931EF3178273366ED2E93DEDACC1DB1E2C1F57A29BC2F13652F971` and 11503 bytes / `3BA69EA42DC8E4CA1AF725292E21FBBFD700D12C9FCC24D950B290BA1456763C`. These values match the original review postpins expected/actual rows; they describe the initial-review snapshot only.

Follow-up #1 returned `CHANGES_REQUESTED` (P0/P1/P2/P3=`0/0/3/2`). Its 15/15 Codex pre/post pin result is retained as that follow-up's historical snapshot. The competing Task/protocol pin values belonged to later record revisions and must not be substituted for the initial snapshot.

Follow-up #2 returned `APPROVED_STATIC_CONTENT` (P0/P1/P2/P3=`0/0/0/4`) for its static record-consistency scope. Its manifest pins 22 inputs; the DSH postpins record `22/22 MATCH` at dispatch/review time. DSH did not independently calculate hashes: `reviewerIndependentHashes=NOT_VERIFIED`. After the report, Codex rechecked the 22 paths: 21 still match; the only mismatch is the Task file, which was subsequently edited by Codex to record the requested current protocol pin and review/adjudication metadata. At review time it was 11473 bytes / `9B10217614F9F72DDF076D7B41A2654C0816F456B94A64A8B8E72E45530A6009`; current Task is 12248 bytes / `635C9728609119BC9D16773A2099F6091C3F472EF95CF4EDD518C3B0B6B76233`. This is an intentional post-review documentation change, not source or executor drift. Current protocol is 11641 bytes / `0E80C83100DB997E7ED81AFF87F058927246D24222931CED54AA44A7809C6AF3`; current executor is 43464 bytes / `9B52BEA5FD108FADC78141318337A98C74C77ED18CDA9D31B8748CB6BDEEAA10`; current Handoff is 2391 bytes / `B903949584773318B7C17695E43B9E7301D34F885783825DD47DA29E03E192A0`.

The live `.git/index` was independently rehashed before and after this Codex pin check: `C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68` both times, matching the frozen main binding. Live branch/HEAD/tree also match the candidate baseline above. Codex pin verification is separate from DSH review; it does not convert the DSH reviewer hash status to verified.

## Finding dispositions

### Initial review findings

| Finding | Disposition |
|---|---|
| P2-001: reviewer could not independently hash inputs or verify root ACL/streams | Closed for the static-record gate by Codex historical 12/12 postpins, current follow-up pin check, and the read-only identity/ACL/stream evidence recorded in `verification/P02/codex-checkpoint-p02pre-r1h-round6-attempt5-review-findings-20261012.md`. DSH independent hashes remain `NOT_VERIFIED`. Final pre-run must recheck live refs, index, identity, ACL, streams, paths, and protected hashes; this finding is not evidence those runtime conditions pass. |
| P2-002: initial manifest did not clearly declare checkpoint membership | Resolved in the restored original manifest and subsequent manifests: `checkpointIncludedInInputPins=false`, and the checkpoint is not an input pin. |
| P3-001: Task result row was pending | Resolved by the Task review rows, which distinguish completed static review from parser/selfcheck, pre-run, executor, and post-run items that remain `NOT_RUN`. |
| P3-002: DSH channel/model/session/web visibility were incomplete | Recorded below for all three DSH calls. Model remains `UNKNOWN`; desktop visibility remains `unverified`. |
| P3-003: protocol used an unsupported `APPROVED_STATIC_PROTOCOL` value | Resolved: protocol release condition now names `APPROVED_STATIC_CONTENT`, Codex pin recheck/adjudication, and a separate `PRE_RUN_PASS`. |

### Follow-up #1 findings F-01 through F-05

| Finding | Disposition |
|---|---|
| F-01: two Task/protocol pin snapshots appeared contradictory | Resolved as a snapshot chronology issue. The original manifest is restored to its original SHA and historical values; follow-up #1 and #2 use separate manifests for later snapshots. Initial 7637/11503 values and current 12248/11641 values are explicitly time-scoped above. |
| F-02: Task AC3 and protocol used different unresolved-finding rules | Resolved. Task AC3 and protocol §7 both block release when any P0/P1/P2 finding is unresolved. The initial raw approval with two open P2s was not accepted as gate approval. |
| F-03: rolling checkpoint was reported as unreadable/binary | Resolved as a format/readability issue, not as missing content. Codex regenerated it as strict UTF-8 Markdown without NUL/control bytes; follow-up #2 read the checkpoint reference and confirmed it was readable. It remains outside the review pin set. |
| F-04: initial prompt and dispatch outputs were not pinned in follow-up #1 | Resolved for provenance coverage: follow-up #2 pins the initial prompt, raw stdout, stderr, and exit artifacts. DSH did not read the initial raw stdout line-by-line; Codex records that limitation and retains its pinned bytes/hash comparison as Codex evidence only. |
| F-05: actual channel/model/session/web visibility were absent | Resolved at the record level: initial review used `dsh --profile headless --json`, DSH `0.2.0-rc.2`, session `session-c8fb0770-b258-4dc3-aeb0-efc0e26d6484`; follow-up #1 used the same CLI/version, session `session-ba3bfaaf-a735-42d5-aa68-0c3bbbd3deee`; follow-up #2 used the same CLI/version, session `session-6c23dd53-9ca7-468c-ba4a-a39571e47f93`. Model was not exposed (`UNKNOWN`) and actual desktop visibility was not checked (`web_visibility=unverified`); mount success alone is not visibility evidence. |

### Follow-up #2 findings P3-1 through P3-4

| Finding | Disposition |
|---|---|
| P3-1: Task did not inline the current protocol pin | Resolved after the review by adding the current 11641-byte / `0E80C831…9C6AF3` and historical 11503-byte / `3BA69EA4…456763C` pins to the Task. Handoff and protocol agree on the current pin. This documentation-only change is why the post-review Task hash differs from the 22-input review snapshot. |
| P3-2: adjudication record was missing | Resolved by this file. It records the review chronology, finding dispositions, method limitations, current pins, and the unchanged Gate state. |
| P3-3: DSH did not independently hash the 22 pins or index | Recorded limitation, not a content defect. DSH hashes remain `NOT_VERIFIED`; Codex independently checked the 22-input snapshot and current index. Twenty-one input paths still match the reviewed snapshot; the sole difference is the intentional post-review Task metadata update described above. The root index hash remained stable. |
| P3-4: follow-up #1 report said one glob although two calls were made | Corrected here: the raw follow-up #1 transcript records two read-only path-pattern (`glob`) calls. The report disclosed a path-enumeration deviation but understated its count. Returned results did not mention `.tmp.driveupload`; traversal behavior was not independently verified. |

## Method and scope deviations

- Initial review: DSH CLI `0.2.0-rc.2`; its attempted `pwsh` hash commands failed before execution with `SetNamedSecurityInfoW Win32 5`; reviewer hashes are `NOT_VERIFIED`. No executor, OS/API, build, or AC ran.
- Follow-up #1: DSH report disclosed two read-only path-pattern calls despite the no-glob instruction. This is a method deviation. The returned results did not mention `.tmp.driveupload`; traversal semantics remain unverified. No write, shell, OS, or API operation was reported.
- Follow-up #2: the raw tool-call list shows read operations only and no shell, glob, hash, script, OS/API, ACL, or write operation. It did read paths outside the 22 pinned inputs: `doc/STATUS.md`, the checkpoint reference despite the prompt saying not to read it, the then-missing adjudication path, and follow-up #1 prompt/stdout/stderr/exit artifacts. These were read-only scope deviations; no `.tmp.driveupload` access or repository write was reported. The follow-up #2 report also states it did not read eight listed inputs and did not independently read initial raw stdout line-by-line; these limits remain in force.
- DSH version and sessions are recorded above. The CLI mount succeeded, but `web_visibility=unverified`; DSH model is `UNKNOWN` for all three calls.

## Gate state and exact next step

No technical Gate is promoted by these reviews. Preserve:

- `private_registry_absence=UNPROVABLE`
- Technical Gate=`NOT_SATISFIED`
- Owner Risk Acceptance=`APPROVED`
- Gate Disposition=`WAIVED_BY_OWNER`
- Build Authorization=`AUTHORIZED_WITH_EXCEPTION`
- Residual risk: `technical condition unmet; user explicitly accepted residual risk`
- Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`
- Build/Cargo=`NOT_RUN`; system AC1–AC7=`BLOCKED / NOT_RUN`

Attempt5 executor, `File.Replace`, parser/selfcheck, final pre-run, R1H capture, OS/API mutation, dynamic isolation, Build/Cargo, and system AC1–AC7 have not run in this adjudication. The next authorized step is the prescribed PowerShell 7.6.6 parser and pure in-memory selfcheck only. If they pass, Codex must perform every frozen final pre-run item and preserve its evidence before considering the single executor invocation. Any mismatch or unknown process/path/write is a stop condition; no retry, cleanup, or rollback.

