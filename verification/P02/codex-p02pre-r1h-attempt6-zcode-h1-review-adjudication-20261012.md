# P02PRE-R1H-R6-ZCODE-H1 — Codex Review Adjudication

- Adjudicator: Codex /root, non-author.
- Date: 2026-10-12.
- DSH session: session-2e6e238c-1814-40b9-b0c6-b253f102296a; mounted to the New Manga workspace.
- DSH verdict: CHANGES_REQUESTED (P0=0 / P1=0 / P2=1 / P3=6), process exit 0.
- Input verification: verification/P02/codex-p02pre-r1h-attempt6-zcode-h1-review-input-verification-20261012.json, 14002 bytes, SHA-256 7B823A05313DA2B053C76B81744667BF041B8FD9AF0933F1162DCDADFB372515.
- Review response: verification/P02/dsh-p02pre-r1h-attempt6-zcode-h1-final-pre-run-review-20261012.response.md, 14078 bytes, SHA-256 6AAD7750AFABCCD5B159C69F40EF49149E3D3EBB1CA6613CD0FD91FDCB960C19.

## Adjudication result

The 13 immutable inputs match their recorded byte lengths and SHA-256 values both before dispatch and after the Review. The v2 JSON verdict is PRE_RUN_PASS, its checks are 23 PASS and 1 NOT_VERIFIED, and its previous_attempt references match all four actual attempt1 pins. The recorded protected-file pre/post values are identical: 57648 bytes, SHA-256 977C99434C2ED10AD5EAEDF34271781DA330AF495AD78D2F9DD593BD88DBD6EA.

I accept the P2-1 evidence-traceability finding. H1 acceptance condition 3 is not satisfied by the current pinned evidence package. The execution verdict remains recorded as PRE_RUN_PASS; this adjudication does not rewrite that historical result. H1 independent-review acceptance is pending evidence closure, so no X6 Task is eligible or created.

## Finding-by-finding decisions

### P2-1 — Generic evidence pointers do not resolve to item-level raw evidence

**Decision: ACCEPTED — OPEN — BLOCKS H1 review acceptance and X6.**

The v2 JSON assigns generic evidence labels to 15 of its 23 PASS checks: five “collection A” references (JSON lines 172, 180, 188, 196, 204), eight “collection B” references (lines 244 through 300), one “v2 precheck” reference (line 324), and one “write script guard” reference (line 348). A scoped search across the exact 13 pinned inputs found these labels only in the v2 JSON. The pinned v2 stdout contains the summary and status snapshots, but not an item-level raw capture resolving those 15 references. The temporary staging material named by the JSON harnessNote was not among the frozen review inputs and is not used to close this finding.

This is an evidence provenance gap, not evidence that a recorded value is false. Preserve the v2 JSON and all attempt1 outputs unchanged. A separately authorized evidence-closure task must either provide traceable item-level raw sources under new, pinned evidence names or show a deterministic mapping to existing pinned source spans, then obtain independent re-review. Do not rerun the final pre-run or invoke the executor to manufacture replacement evidence.

### P3-1 — Atomic-write description is not independently verifiable

**Decision: PARTIALLY ACCEPTED — NON-BLOCKING.**

The v2 JSON says the writes used “one atomic try block”; the v2 stderr says the scripts used flat statements and “no multi-line try blocks.” These statements do not logically contradict each other: a try block could be single-line. The write script itself is not pinned, so the atomicity claim cannot be independently verified. The four v2 result artifacts are complete and pinned, but that does not establish the claimed write mechanism. Do not rely on the atomicity description as a verified property; preserve the raw outputs.

### P3-2 — The +4 root-status attribution is unsupported

**Decision: ACCEPTED — NON-BLOCKING.**

The v2 status snapshot contains the H1 Task as an untracked path. Editing an already untracked file does not add another porcelain record. The same v2 snapshot also contains the four attempt1 output files as untracked records. Without a per-path baseline for both measurements, the claimed attribution of the +4 records to H1 text changes is unsupported. Keep the change attribution UNKNOWN / NOT_VERIFIED; do not assign it to an Agent.

### P3-3 — The .exit file does not distinguish PRE_RUN_PASS from PRE_RUN_BLOCKED

**Decision: ACCEPTED — NON-BLOCKING.**

The attempt1 and v2 .exit files both contain 0 and have the same pinned SHA-256, while their JSON verdicts are PRE_RUN_BLOCKED and PRE_RUN_PASS. The .exit value records the wrapper/process exit; the JSON verdict and associated evidence determine the pre-run disposition. Future summaries must not present .exit=0 as standalone support for PRE_RUN_PASS.

### P3-4 — H1 current-state rows are stale

**Decision: ACCEPTED — ACTION REQUIRED IN CURRENT-STATE SUMMARIES.**

The H1 test table and delivery notes still say final pre-run and Review are NOT_RUN or awaiting outputs, while later pinned sections record the v2 PRE_RUN_PASS and its evidence. After both Codex adjudication artifacts were written, update only H1's current-state summaries and pointers, including the current Owner/Coordinator, to say DSH Review is CHANGES_REQUESTED and P2-1 remains open. Preserve dated history. Keep the attempt1 four-file author allowlist as historical scope and clearly link the separately authorized v2 four-file set; do not retroactively claim the original allowlist included v2.

### P3-5 — v2 status argv claim is unsubstantiated; do not use v2 as an X6 baseline

**Decision: PARTIALLY ACCEPTED — CONSERVATIVE LIMITATION ADOPTED.**

The DSH report says the v2 stdout records a status argv using porcelain v1. The pinned v2 stdout lines 1 through 6 show the Git argv prefix, key values, and root-status result, but do not record the full status argv. The v2 JSON statusSnapshots fields include the result, finalExcludeArg, and note, but no argv field. Therefore the specific claim that v2 used the cited argv is not independently verified from the frozen inputs.

The pinned executor does freeze its S0 command at line 390 as porcelain v2 with --untracked-files=all, --no-renames, --ignore-submodules=none, and the final pathspec pair. Because the v2 command cannot be established as identical from its pins, accept the practical restriction: do not treat the v2 status snapshot as an X6 S0/delta baseline. If X6 is later authorized, collect a fresh S0 using the executor's exact frozen argv and record it before execution.

### P3-6 — Executor line-count claim differs

**Decision: ACCEPTED — NON-BLOCKING; COUNTING CONVENTION UNRESOLVED.**

The pinned executor yields 638 logical lines by LF count and PowerShell line enumeration. The A6 Task and Handoff cite 639. This is a documented factual discrepancy; the likely terminal-newline/counting explanation is not proven. Leave the frozen A6 Task, Handoff, and executor unchanged. No runtime conclusion follows from this count.

## Gate and next step

All original Gate values remain unchanged:

- private_registry_absence=UNPROVABLE
- Technical Gate=NOT_SATISFIED
- Owner Risk Acceptance=APPROVED
- Gate Disposition=WAIVED_BY_OWNER
- Build Authorization=AUTHORIZED_WITH_EXCEPTION
- residual text=technical condition unmet; user explicitly accepted residual risk
- Build Gate=BLOCKED
- Hard Build Barrier=EFFECTIVE
- Build/Cargo=NOT_RUN
- AC1–AC7=BLOCKED / NOT_RUN
- dynamic process closure=REQUIRES_ACTIVE_TEST / NOT_RUN

Next READY Task: none. H1 remains active with an open P2-1 evidence-closure prerequisite. The next recommended action is for Codex /root to propose and, after the Plan activates it, own a narrowly scoped evidence-closure task; that task must preserve all existing pins, avoid rerunning the pre-run and executor, and obtain a focused independent Review. Only after P2-1 is closed and the H1 Review is accepted may a separate X6 one-shot Task be registered.
