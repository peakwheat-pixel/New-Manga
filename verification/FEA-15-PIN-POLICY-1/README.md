# FEA-15-PIN-POLICY-1 evidence

## Initial execution snapshot

- Captured: 2026-11-11T15:02:38+08:00
- Branch: main
- HEAD: d0fa710ea74a0b48a5fabaa002009170cd4665c3
- Worktree: clean before adding this checkpoint and README.
- Task owner/status: Codex / in_progress.
- Base commit: 4efc592d12c25b8be33502f53c9270ad0597adfd.

## Evidence and AC state at initial capture

- The ZCode release decision is in doc/reviews/FEA-15-PIN-POLICY-1-zcode-release-adjudication-2026-11-11.md.
- release-gates-0730335.log records default governance check, current and prior TaskPath checks, 18 pins, and API inventory at generation HEAD 0730335f835306a19d283f06dbc0164134a9e04e. All five commands exited 0. This is release evidence, not the final delivery gate.
- AC1 inventory refresh and policy ruling: NOT_RUN.
- AC2 implementation impact-surface plan: NOT_RUN.
- AC3 final delivery gates, Handoff, independent Review and ZCode adjudication: NOT_RUN.

## Final delivery measurement and current state

- Delivery measurement HEAD: `e9f7bb1b48c885cb329848d2d3591e145ff3d229`.
- Final inventory: [`pin-inventory.json`](pin-inventory.json), 5,376 rows (585 Task cards, 5,358 Task pins, 18 frozen records), SHA-256 `e38b7d2279177ea701fc7e7e10afa7f8ef3bbe4414cecbb81529a2c8feecef56`; run log [`pin-inventory-run.log`](pin-inventory-run.log), `EXIT=0`.
- Baseline delta: [`pin-inventory-delta.json`](pin-inventory-delta.json), `5,350 → 5,376`, `+26 / -0 / changed 0`; the additions are 24 rows from `FEA-15-PIN-EOL-GOV-1` and 2 release rows from this Task. Basis change is `WORKTREE +16`, `MIXED +10`; the six exception classes remain 573. Delta run log records `EXIT=0`.
- Modeled r194 matrix: [`pin-r194-baseline-matrix.json`](pin-r194-baseline-matrix.json), `4,803` match the worktree-or-blob predicate and `573` are nonpass observations. It is explicitly a model from inventory booleans, not a per-row `check.ps1` execution.
- Final governance log [`delivery-gates-e9f7bb1.log`](delivery-gates-e9f7bb1.log): default/current TaskPath/prior TaskPath all PASS (3 warnings each, EXIT 0); `verify_pins.ps1` 18/18 EXIT 0; API 1/79/6=86 EXIT 0.
- Inventory limitation: the legacy parser does not capture the current Task's parenthesized `class (CANONICAL / SOURCE_PIN)` header, so its two release rows have blank `class` values; historical `class_counts` are not a reliable semantic taxonomy. Row identity, SHA, basis and delta counts are unaffected. This remains documented; the frozen source parser was not modified.
- AC1 is PARTIAL pending ZCode's ruling adjudication. AC2's impact plan is drafted, pending independent Review/ZCode adjudication. AC3 delivery gates are recorded and Handoff is committed at `fd8a60b57a16b0076ed4e14586463f4a1cf19e57`; Canonical Evidence pinbackfill, fresh-context Review and final adjudication remain pending.
- Preliminary inventory/delta/matrix at `da4a60baafba18281f156330b9ed1646045edb6d` are retained as process snapshots and are superseded by the final delivery measurement above.

## Proposed ruling and impact plan

- Drafts: [`pin-basis-ruling.md`](pin-basis-ruling.md) recommends exact commit-blob bytes for new repository evidence, legacy r194 compatibility, and transfer of R-001 to a separately released basis-enforcement Task. This is a proposal pending ZCode Review/adjudication.
- [`pin-basis-impact-plan.md`](pin-basis-impact-plan.md) captures the preliminary 5,376-row affected universe, the modeled `r194` predicate split (4,803 match / 573 nonpass observations), four binary/text/EOL boundary samples, a frozen-clone dry-run plan, rollback conditions, and a successor Task outline. No checker run was performed per inventory row; no clone/dry-run was performed.
- Preliminary matrix extract is [`pin-r194-preliminary-matrix-da4a60b.json`](pin-r194-preliminary-matrix-da4a60b.json); its command and `EXIT=0` are recorded in [`pin-r194-preliminary-matrix-run-da4a60b.log`](pin-r194-preliminary-matrix-run-da4a60b.log). The delivery-head matrix will be regenerated later.
- Current AC state: AC1 `PARTIAL` pending final delivery snapshot and ZCode ruling; AC2 `PARTIAL` pending final measurement and independent adjudication of the impact plan; AC3 `PARTIAL` pending delivery gates, Handoff, independent Review, and ZCode adjudication.

## Limits retained

- The baseline inventory at 948d73e0629869e560df9a2b2d8a357cec67027f has 5,350 rows. The mutually exclusive basis split is WORKTREE=3,451, BLOB=327, MIXED=999, other=573. The 573 other rows include INCONSISTENT=160, UNPINNED=293, UNRESOLVED_COMMIT=68, EXTERNAL_UNAVAILABLE=47, MISSING=3 and COMPOSITE_PATH=2.
- Product pytest/.NET, Linux fresh clone, renormalize simulation, pin migration and checker semantic changes remain NOT_RUN or out of scope. No NOT_RUN item is represented as PASS.
- No external checkout, task-env, dataset, model, installer, temp, agent-output or exchange was created; no resource was removed, migrated or archived; no push occurred.

## Next step

Complete independent review/adjudication of the proposal, then generate the final inventory and delta at the fixed delivery measurement HEAD. Keep policy decisions and implementation proposals separate from observed data.
