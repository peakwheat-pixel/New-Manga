# Codex adjudication: H2 source R3

- Task: P02PRE-R1H-H2-COLLECTOR
- Reviewed code commit: f8ea2edc7c2097f6f87676cafe7a3e2377a3f050
- Reviewed branch head including documentation: 8bba48bd9c0f08ffe6e81a5fd2277514595d0d27
- Independent reviewer: DeepSeek Harness
- DSH verdict: APPROVED_STATIC_CONTENT
- Codex disposition: CHANGES_REQUESTED for a narrow R4 hardening pass
- Latest Review: dsh-source-review-r3.md
- Exact input verification: source-review-r3-input-verification.json

## Pin and test adjudication

Codex independently recomputed all 8 input SHA-256 pins before and after the DSH review; 8/8 match. Git blob IDs also match the working-tree file objects for the R3 collector and selftest at code commit f8ea2edc. The DSH runner could not execute Git because its own Windows sandbox rejected the worktree startup; Codex's local blob checks close that identity gap.

Codex ran PowerShell 7.6.6 Parser over both files: 0 errors. The independent pure selftest passed 156 assertions, 0 failed, 6 skipped. The skips are the prohibited live collector, registry/WER, ACL, profile, Git child process, executor, process observer, Build, AC and Sandbox scopes. Source SHA-256 values were unchanged before/after. No live collector or system query was run.

## R2 finding adjudication

R2-01, R2-02, R2-03, R2-04 and the P4 precision item are closed at the reviewed R3 code commit. The DSH Review found the requested ordering, lstat leaf classification, pre-access exclusion checks, dynamic path observation, final index sample ordering and full-plan observation pointer in the code. R3 did not alter historical H1 v2 findings or Gate values.

## Required R4 corrections

The DSH report records four P3 findings. Codex requires correction before H2-RUN because the first three affect the raw-evidence contract and excluded-path boundary, and the fourth leaves fixed execution/read targets without a leaf reparse assertion.

1. R3-CX-01, P2: Get-PathProbeObservation discards the captured GetAttributes exception and returns the legal-absence shape for every failure. The TEMP/TMP/scratch/cache and Packages probe checks then report PASS without distinguishing genuine FileNotFound/DirectoryNotFound from access, argument or I/O errors. Record non-absence errors explicitly and ensure their checks are not PASS. Add a meaningful selftest distinguishing genuine absence from a non-absence attribute error. This implements the task rule that unknown/failure is not PASS.
2. R3-CX-02, P2: for a non-directory reparse leaf, Get-PathProbeObservation calls FileInfo.Length before recording LinkTarget. This follows a file link and loses link metadata for a dangling link. Do not read target metadata for reparse leaves; preserve link-target facts when available and keep the result explicit when the target is dangling. Add a focused selftest or a precise source assertion.
3. R3-CX-03, P2: the tools-pwsh probe checks a runtime $PSHOME-derived path, but its getter input and exclusion manifest contain only the frozen expected path. Include and guard the actual runtime path before any File.Exists call, and record it in an exclusion-scope observation before the probe.
4. R3-CX-04, P2: the fixed-path chain excludes Git, whoami, PowerShell executables and the H1 Task snapshot even though those paths are executed or read. Add them to the chain/reparse validation and require ordinary non-reparse paths before use; do not probe or modify system paths to test this.

The R4 change remains within the frozen two-script allowlist, its selftest, and the Owner Handoff/Task copy. Preserve all R2 closures. Commit a new delivery head; rerun Parser and pure selftest; provide a new Handoff and complete exact-head DSH Review. The prior R3 approval does not transfer to modified code.

## State and safety

The Task returns to Owner implementation after this adjudication. H2-RUN stays proposed and no live collector is released. Preserve the R3 report, pins, fixtures and workspace outputs until R4 review and closeout. Historical H1 v2 remains PRE_RUN_PASS (23 PASS / 1 NOT_VERIFIED), P2-1 OPEN; Technical Gate NOT_SATISFIED, private_registry_absence UNPROVABLE, Build Gate BLOCKED and Hard Build Barrier EFFECTIVE. No value in this record authorizes Build, executor, AC, Sandbox, registry, ACL or profile writes.
