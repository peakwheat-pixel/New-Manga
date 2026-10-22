# Codex adjudication — P02PRE-R1F R5 follow-up #7

Date=`2026-10-11`; Owner/author/adjudicator=`Codex /root`; non-author Reviewer=`DeepSeek Harness`.

## Review evidence

- DSH CLI=`0.2.0-rc.2`; session=`session-a4ad5186-1281-4da8-996e-4696cc492079`; CLI exit=`0`.
- Prompt=`verification/P02/dsh-p02pre-r1f-r5-followup7-20261011.prompt.md`, `3563 bytes / SHA-256 9CE41DAEEB7BED5C4B0D812A9E66DF6781DC988F51096BC2B7161F92EA04ACC2`.
- Raw stdout/report=`verification/P02/dsh-p02pre-r1f-r5-followup7-20261011.stdout.md`, `203071 bytes / SHA-256 E72F8B4CD8AF9513785DB3776A94DC17559DF052A0E9828AC1869331A8F5D4BB`.
- Stderr=`verification/P02/dsh-p02pre-r1f-r5-followup7-20261011.stderr.log`, `0 bytes / SHA-256 E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`.
- Exit artifact=`verification/P02/dsh-p02pre-r1f-r5-followup7-20261011.exit`, content=`0\n`, `2 bytes / SHA-256 9A271F2A916B0B6EE6CECB2426F0B3206EF074578BE55D9BC94F6F3FE3AB86AA`.
- Decision=`CHANGES_REQUESTED (P0=0, P1=0, P2=2, P3=4)`. Review was static/read-only; it did not run getters, capture, Build/Cargo, AC1–AC7, or mutate the capture candidate.

## Codex decisions

| Finding | Decision | Disposition |
|---|---|---|
| P2-1: manifest called the review “Codex-only,” conflicting with the non-author reviewer/Codex adjudicator split | ACCEPTED | Manifest now explicitly names DeepSeek Harness as independent Reviewer and Codex as adjudicator. |
| P2-2: pre-capture Review artifacts lacked a frozen, checkable inventory/hash evidence step; prior follow-up #3 required protected-list coverage | ACCEPTED | Manifest and Task now enumerate both review rounds and adjudications. Final pre-run must verify every exact pre-capture path appears in main `git ls-files --cached --others --exclude-standard -z` inventory and record its size/SHA-256 in the frozen checkpoint. After capture, compare each recorded SHA-256 against a non-null `repository.main.fileInventory[].sha256`; any absent, unhashed, ignored, omitted, or mismatched record is `FAILED`/`UNPROVABLE`, never PASS. |
| P3-1: “R1F-R7” could be confused with parser R7 or a capture round | ACCEPTED | Manifest and Task clarify it denotes the R5 follow-up #7 governance scope review only; parser R7 remains a historical artifact. |
| P3-2: Task did not freeze all four pre-run Review output names | ACCEPTED | Task now gives the exact prompt/stdout/stderr/exit names and binds them to the manifest. |
| P3-3: Task did not state the disposition if a pre-capture artifact is absent/unhashed | ACCEPTED | Task requires `FAILED` or `UNPROVABLE`, refuses release, and retains capture=`BLOCKED / NOT_RUN`. |
| P3-4: review adjudication hash timing was ambiguous | ACCEPTED | The review and adjudication are finalized first; status/checkpoint documents are then frozen; only then does final pre-run compute and record artifact hashes before release. |

The reviewer identified a precedent in `p02pre-r1f-r5-followup3-review-adjudication-20261011.md`: that candidate added review evidence to the script's protected list. This candidate intentionally keeps the reviewed capture script, its 96-key `protectedHashes` array, and R8 unchanged. The alternative is acceptable only because the new governance files are independently required to appear and hash in the full main Git inventory before release and are reconciled against capture output afterward. They are not claimed to be members of the 96-key protected set. If the inventory omits any path (including from partial evidence), the related result remains `FAILED`/`UNPROVABLE`; there is no retry or Gate promotion.

## PowerShell runtime clarification

The outer orchestrator used PowerShell 7.6.6. The frozen R1F executor and parser target are `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` / Windows PowerShell 5.1.26100.9549, and R8 proves only that the exact candidate parses under that engine. Existing evidence does not establish that PowerShell 7 is incompatible. The current candidate stays on 5.1 to preserve the already reviewed execution contract and evidence; changing to PowerShell 7 would require a new frozen candidate and independent Review. This is not a technical Gate result.

## Release state

This adjudication accepts the findings and their documented fixes; it does **not** approve capture release. The repaired Task/manifest/status/checkpoint require an independent narrow follow-up Review and Codex adjudication. Only afterward may Codex perform the final pre-run verification. Current capture remains `BLOCKED / NOT_RUN`; Build Gate remains `BLOCKED`; Hard Build Barrier remains `EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`.

Owner exception remains exactly: `private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`.
