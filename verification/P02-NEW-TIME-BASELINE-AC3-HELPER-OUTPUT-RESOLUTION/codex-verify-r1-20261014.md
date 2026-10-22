# Codex deterministic VERIFY — P02 helper output resolution

## Scope and binding

- Task: P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.
- Owner code delivery commit: 6420653c1ec8adfcc26da9378072451f921b5930.
- Owner final handoff HEAD: c8434a8e74d5dd211cfad673f9fd46f9d4d73e0f.
- Verification worktree: G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION; branch=agent/zcode/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION.
- Task base: 16db22c707faf8336f2fc1e44397eaf1f8cb51ef.
- I/T/E classification: I1, T1, E1 by decide-convergence.py --mode classify-revision; outputs are pinned in revision-classification-*.

## Deterministic checks

1. Delivery commit 6420653c changes exactly the two Task-allowed files: tools/p02/p02-new-time-baseline.ps1 and tools/p02/p02-new-time-baseline-selftest.ps1; its diff-check exit=0. The code delta is +45/-5.
2. Invoke-HelperProcess success and exception constructions both emit output.value.stdout/stderr using the unchanged ConvertTo-RawBytesRecord; all existing helper consumers and four /output/value/stdout pointers remain unchanged. No Invoke-InProcessGetter, schema, dependency, or external contract changes.
3. Eight helper-shape-* pure static assertions cover both producer paths, exact construction count, absence of legacy unwrapped shape, consumers, and pointers.
4. Owner and Codex selftest runs each report 220 PASS / 0 FAIL / 7 SKIP, exit=0; Codex run was exactly: pwsh -NoProfile -File tools/p02/p02-new-time-baseline-selftest.ps1, PowerShell 7.6.6, CWD=G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION. Owner stdout SHA-256=F242304EC8090BFCFDA6530895D3CF111C15D86FCAA595CB9539FB75A50298F9; Owner run-record SHA-256=C179678CC1C767DB05ED76577D10FEF7EF9C7C6F706FB307A1E38015089FA9E5. Codex stdout SHA-256=92CA9348946B74089224D83133A3759E7FFB3A626A95C37149B1F1B90B6F7F04; stderr SHA-256=E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855 (empty). Codex SUMMARY collectorSha256=BF9F69CFB291C6E7609A861821FC458C32C7A3C7AD93898953E3AD2DB26D567A, matching the delivery source file SHA-256.
5. Both summaries state liveCollectorExecuted=false, liveQueriesExecuted=false, gitChildExecuted=false, historicalInputAccessed=false. Seven skips are enumerated in the run output and excluded from PASS. Temp fixture inventory SHA-256=F19F51566C48F374CCD0D38EA06972A5B6C1F13EE4E01486FF3C2BCA9440514F; all listed fixture files are preserved.
6. Review scope remains bounded: no unrestricted audit, no finding outside current blockers/AC/safety is opened. DSH AC4 Review and Codex AC5 integration have not yet run.

## AC state after Codex VERIFY

- AC1: PASS — producer shape normalized on both paths; consumer/pointer compatibility retained.
- AC2: PASS — eight pure regression assertions added; original assertions not reduced.
- AC3: PASS — PowerShell parser/selftest exit=0, 220/0/7 in Owner and Codex runs.
- AC4: NOT_RUN — independent DSH bounded Review pending.
- AC5: NOT_RUN — DSH approval and Codex integration pending.
- AC6: PASS — no collector, RunId, X6, post-run Review, Build/Cargo, product AC1–AC7, or Sandbox was run.

This VERIFY is deterministic evidence only. It does not replace DSH Review or integrate source changes.