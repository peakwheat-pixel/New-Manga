# M2-C1 ZCode Owner Delivery — DSH independent Review r3: relative-link adjudication

Reviewer: DeepSeek Harness (non-author). reviewed_head: `b2377288680569dbee4e2299fd7dfae4de067c54`.
Method: `probe-link-audit.py` (committed beside this file) extracts every Markdown inline
link `[..](target)` and every backticked repo path from the eight paths added by
`7478f72..b237728`, resolves each target against its own file directory, and tests
existence with `git cat-file -e` at reviewed_head, at the frozen adopted object
`ac38dede…`, and (for the Qoder artefacts) at `0d73983…`.

Raw output: `04-link-audit.log`.

## 1. Result summary

```text
total repository references checked inside reviewed_head = 49
non-resolving                                            = 9
```

Every non-resolving reference is listed below. Only one of the nine is a Markdown
hyperlink; the other eight are backticked path mentions inside prose or tables.

| # | File:line | Kind | Target | At reviewed_head | At `ac38dede` | Context |
|---|---|---|---|---|---|---|
| a | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:16` | **Markdown link** | `verification/M2-C1/source-trace.md` | MISSING | present | §1 evidence pointer: "来源、行号、commit 和证据分类见 …" |
| b | `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:16` | code path | same target (same sentence) | MISSING | present | duplicate extraction of (a) |
| c | `verification/M2-C1/zcode-owner/00-environment.md:30` | code path | `verification/M2-C1/scheduler-registration-7478f72.md` | MISSING | absent | "reproduces the Scheduler registration result in …" |
| d | `verification/M2-C1/zcode-owner/00-environment.md:56` | code path | `verification/M2-C1/review-r3-4d66523/03-finding-recheck.md` | MISSING | absent | explicitly labelled as a dispatching-prompt example filename that does **not** exist |
| e | `03-blob-equivalence.md:47` | code path | `doc/tasks/M2-C1.md` | MISSING | present | row of the table "Draft-head path (`ac38dede…`) / Present in Owner delivery? / Reason" |
| f | `03-blob-equivalence.md:48` | code path | `doc/handoffs/M2-C1-4d66523.md` | MISSING | present | same table, marked "NO — stays frozen in history" |
| g | `03-blob-equivalence.md:50` | code path | `verification/M2-C1/review-remediation-r3.md` | MISSING | present | same table, marked "NO" |
| h | `03-blob-equivalence.md:50` | code path | `verification/M2-C1/reviewer-prompt-r3.md` | MISSING | present | same table, marked "NO" |
| i | `03-blob-equivalence.md:51` | code path | `verification/M2-C1/source-trace.md` | MISSING | present | same table, row that explicitly names the equivalent Owner-base trace |

References (e)–(i) sit inside a table whose subject is precisely "which draft-head
paths are absent from the Owner delivery and why". Their non-resolution is the table's
own content, so they are not defects.

Reference (d) is reported by the Owner itself as a filename that does not exist; it is an
honest correction note, not a defect.

Reference (c) is a prose cross-reference to a Codex governance artefact that exists on
mainline (`origin/master`) but not on the Owner branch. Its content is a verbatim
restatement in the same file, so no information is lost.

## 2. Blocking adjudication

**Decision: reference (a)/(b) is NOT BLOCKING. No Owner rework is required for it.**

Facts established independently in this Review:

1. The target genuinely does not exist at reviewed_head
   (`git cat-file -e b237728:verification/M2-C1/source-trace.md` -> exit 128; the file is
   also absent from the filesystem of this checkout).
2. The target **does** exist at the frozen adopted object
   (`git cat-file -e ac38dede…:verification/M2-C1/source-trace.md` -> exit 0), so it stays
   byte-recoverable by any auditor with the repository object database:
   `git show ac38dede84ff22290c9b9d579c1372c8184a7bd5:verification/M2-C1/source-trace.md`.
3. The Contract clause that carries the link, §1, is a self-contained statement: it
   defines the four evidence classes and asserts the AS-IS baseline in prose
   (`eec1aa49d07119f0aa66ff461ebbb55e4595e624`, AS-IS: UNKNOWN / NOT_IMPLEMENTED for the
   runtime). No normative clause and no reader-facing meaning depends on opening the file.
4. The Owner ships an in-tree, Owner-base-anchored equivalent
   (`verification/M2-C1/zcode-owner/01-source-trace-owner-base.md`) and this Review
   independently reproduced its load-bearing content: all nine cited evidence files are
   blob-identical across `eec1aa4…`, `7478f72…` and `7de1cd2…`; `TaskProjection` = 23
   fields; `control_run` at `:829`, `recover_running_runs` at `:886`,
   `retry_failed_targets` at `:903` with `TARGET_NOT_FOUND` at `:913`; `PipelineRunStatus`
   nine values; `_to_pixels` half-up+clamp; `list_revisions` on the port and zero service
   definitions; `CredentialRef` zero hits; AD-001 `:15/:33/:35` verbatim. The equivalent
   trace is not a hollow replacement — it carries the same verifiable content re-anchored
   to the Owner base.
5. Under Case A (`OWNER_ADOPTED_WITHOUT_SEMANTIC_CHANGE`) and the adopted allowed paths,
   the link cannot be repaired without either editing the Contract (destroying blob
   identity `4b503a17…`, i.e. breaking the very equivalence this Task is built on) or
   introducing a verification file outside `verification/M2-C1/zcode-owner/**`. The link
   is therefore a structural consequence of the adoption path, not an Owner omission.
6. The repository's own review standard ties approval to unresolved P0/P1 findings and
   missing key verification (`doc/templates/REVIEW.md` "批准门槛"; `doc/09_COLLABORATION.md`
   §6 item 8). This item is neither: it is a navigation-quality limitation whose content
   is verified and recoverable.

**Actual auditability impact (stated honestly):**

- An auditor who opens the Contract at reviewed_head and follows its only source pointer
  reaches nothing. They must know the adopted object hash to recover the trace. That is a
  real, if bounded, friction cost and it is the reason this Review records a finding
  instead of passing it silently.
- The impact is bounded because the pointer is a *convenience index* over an evidence set
  that this Review re-verified from the fixed base directly, and because the frozen object
  hash is recorded in three places inside the delivery itself
  (`03-blob-equivalence.md`, `01-source-trace-owner-base.md`, Handoff §"验证证据").
- No product behaviour, contract semantics, data-safety invariant or AC is affected.

**Required action:** none from the Owner in this round. The recommendation below is
addressed to Codex as Integrator, because removal of the in-tree dangling link is an
integration/governance-navigation decision (for example by landing the frozen
`source-trace.md` on the integration branch, or by a governed navigation note). It must
not be done by editing the Contract blob.

## 3. Second-order observation

Two further reachability facts are worth recording even though neither is a defect:

- The M2-C1 Task file (`doc/tasks/M2-C1.md`), which carries the allowed-path authorisation
  the Handoff cites, is not in the reviewed tree; it exists at `ac38dede…` and on
  `origin/master`. The Owner branch therefore cannot self-prove its own scope. This
  Review verified the authorisation from `origin/master` and the ancestry record instead
  (finding F-002).
- All remaining 40 references in the reviewed range resolve at reviewed_head, including
  every link in the Handoff and every path in `01-source-trace-owner-base.md`,
  `02-decision-log.md`, `04-git-scope-check.md` and `05-drift-and-links.md`.
