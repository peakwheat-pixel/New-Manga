# FEA-15-PIN-POLICY-1 evidence

## Initial execution snapshot

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

## Latest progress — preliminary AC1 comparison

- Execution HEAD: `1d48d9b13698e9b4d7e2549b26fc7795b957cb65`.
- A preliminary inventory was generated at `da4a60baafba18281f156330b9ed1646045edb6d`; it is preserved as [`pin-inventory-preliminary-da4a60b.json`](pin-inventory-preliminary-da4a60b.json), with its run record in [`pin-inventory-preliminary-run-da4a60b.log`](pin-inventory-preliminary-run-da4a60b.log). It is not the delivery-head inventory.
- The preliminary delta against baseline `948d73e0629869e560df9a2b2d8a357cec67027f` is machine-readable in [`pin-inventory-preliminary-delta-da4a60b.json`](pin-inventory-preliminary-delta-da4a60b.json); command summary and EXIT are in [`pin-inventory-preliminary-delta-run-da4a60b.log`](pin-inventory-preliminary-delta-run-da4a60b.log).
- Observed rows: `5,350 → 5,376`; `26 added`, `0 removed`, `0 changed`. The additions are 24 rows in `FEA-15-PIN-EOL-GOV-1` and 2 release rows in this Task. Basis deltas are `WORKTREE +16`, `MIXED +10`; exception-class rows remain 573. These are generator classifications, not validity or damage findings.
- AC1 remains partial until the full snapshot and delta are regenerated at the delivery measurement HEAD, the policy ruling is completed, and ZCode adjudicates it. AC2 remains NOT_RUN. AC3 remains partial: release and intermediate gates passed, while delivery-head evidence, Handoff, independent Review, and final adjudication remain pending.

## Limits retained

- The baseline inventory at 948d73e0629869e560df9a2b2d8a357cec67027f has 5,350 rows. The mutually exclusive basis split is WORKTREE=3,451, BLOB=327, MIXED=999, other=573. The 573 other rows include INCONSISTENT=160, UNPINNED=293, UNRESOLVED_COMMIT=68, EXTERNAL_UNAVAILABLE=47, MISSING=3 and COMPOSITE_PATH=2.
- Product pytest/.NET, Linux fresh clone, renormalize simulation, pin migration and checker semantic changes remain NOT_RUN or out of scope. No NOT_RUN item is represented as PASS.
- No external checkout, task-env, dataset, model, installer, temp, agent-output or exchange was created; no resource was removed, migrated or archived; no push occurred.

## Next step

Complete the proposed policy ruling and implementation impact plan, then generate the final inventory and delta at the fixed delivery measurement HEAD. Keep policy decisions and implementation proposals separate from observed data.
