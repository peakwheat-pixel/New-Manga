# FEA-15-PIN-POLICY-1 evidence

## Current execution snapshot

- Captured: 2026-11-11T15:02:38+08:00
- Branch: main
- HEAD: d0fa710ea74a0b48a5fabaa002009170cd4665c3
- Worktree: clean before adding this checkpoint and README.
- Task owner/status: Codex / in_progress.
- Base commit: 4efc592d12c25b8be33502f53c9270ad0597adfd.

## Evidence and current AC state

- The ZCode release decision is in doc/reviews/FEA-15-PIN-POLICY-1-zcode-release-adjudication-2026-11-11.md.
- release-gates-0730335.log records default governance check, current and prior TaskPath checks, 18 pins, and API inventory at generation HEAD 0730335f835306a19d283f06dbc0164134a9e04e. All five commands exited 0. This is release evidence, not the final delivery gate.
- AC1 inventory refresh and policy ruling: NOT_RUN.
- AC2 implementation impact-surface plan: NOT_RUN.
- AC3 final delivery gates, Handoff, independent Review and ZCode adjudication: NOT_RUN.

## Limits retained

- The baseline inventory at 948d73e0629869e560df9a2b2d8a357cec67027f has 5,350 rows. The mutually exclusive basis split is WORKTREE=3,451, BLOB=327, MIXED=999, other=573. The 573 other rows include INCONSISTENT=160, UNPINNED=293, UNRESOLVED_COMMIT=68, EXTERNAL_UNAVAILABLE=47, MISSING=3 and COMPOSITE_PATH=2.
- Product pytest/.NET, Linux fresh clone, renormalize simulation, pin migration and checker semantic changes remain NOT_RUN or out of scope. No NOT_RUN item is represented as PASS.
- No external checkout, task-env, dataset, model, installer, temp, agent-output or exchange was created; no resource was removed, migrated or archived; no push occurred.

## Next step

After committing this snapshot, refresh the pin inventory at the resulting fixed HEAD and compare it against the baseline. Keep policy decisions and implementation proposals separate from observed data.
