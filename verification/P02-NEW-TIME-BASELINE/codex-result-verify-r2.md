# Codex Result Verification r2

- Deterministic result verification: PASS.
- RunId: baseline-20261014T0915CST-p02-admission-r2
- Result disposition: COLLECTED_NEW_TIME_EVIDENCE
- Collector: 64 lines (1 meta, 62 observations, 1 closed); 57/57 checks PASS; exit 0; stderr empty.
- Result SHA-256: CAAC6AFDE8D479CABCD839E2B74FDD86A1ECD8B59E5E8C88100A552382A9458E, 161783 bytes.
- Freeze Manifest SHA-256: 8662DEC583D2FD865532A414F0BEDE63B7F02872AB3C9232553C3B01E239006D.
- All 17 frozen input pins revalidated after collection; worktree HEAD remained at the frozen delivery commit.
- At verification time, the exact Git porcelain-v2 status bytes matched the collector's captured bytes. This verifies no status drift through that point; it does not claim the worktree was clean.
- ZCode's final JSON response disclosed one earlier internal launcher attempt using pwsh -Command - from stdin that did not execute the launcher script; ZCode says it used a probe to confirm this and then ran with -EncodedCommand. The actual probe command/output was not separately supplied. This is recorded as a pre-collector orchestration failure, not a collector run; the successful collector ran once and consumed the RunId.
- AC3 remains pending DSH result Review and Codex adjudication. AC5 is pending; X6 and later gates remain blocked.
- This new-time result does not backfill, replace, or close historical H1/P2-1 evidence.