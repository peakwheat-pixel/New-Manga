# H1/H2 applicability matrix R1

Review scope: whether any H2 new-time observation can be the original H1 v2 source for the 15 generic evidence references.
Inputs: review-inputs-r1.json, H1 v2 result, H1 DSH Review/adjudication, H2 runtime result, DSH R3 Review and Codex adjudication.
Decision for all rows: NO. H2 observations are later measurements from a separate RunId and collector. No exact same-time, same-operation, item-level mapping exists in the frozen inputs.

| # | H1 check ID / v2 line | H1 evidence label | Closest H2 observation | Codex applicability decision |
|---:|---|---|---|---|
| 1 | tools / 172 | collection A | tools-pwsh, tools-git-version | NO. H2 is a separate next-day collection; the H1 collection-A item-level capture is still absent. |
| 2 | a-identity / 180 | collection A | identity-windows, whoami-all | NO. whoami-all produced a byte-identical stdout hash, but it is a second measurement on 2026-10-13 and cannot be the H1 2026-10-12 source; it also does not establish every H1 identity subclaim. |
| 3 | b-registry-wer-localdumps / 188 | collection A | wer-localdumps-readonly | NO. The later H2 observation is a different collection operation/input and does not resolve H1's generic pointer. |
| 4 | b-profile-moniker / 196 | collection A | profile-moniker-packages-probe | NO. H2 is later; its probe is not H1's v2 pre-run source. |
| 5 | c-temp-paths / 204 | collection A | temp-tmp-env, path-probe observations | NO. H2 used its own frozen path set at a later time. |
| 6 | e-root-refs / 244 | collection B | refs-root observations | NO. The root refs are later observations; H1's collection-B source remains unpinned. |
| 7 | e-owner-refs / 252 | collection B | refs-candidate observations | NO. Candidate naming is not evidence of identical H1 owner input or time. |
| 8 | e-agy-refs / 260 | collection B | refs-a6 observations | NO. A6 refs are a later snapshot, not H1's original source. |
| 9 | e-root-status / 268 | collection B | status-root | NO new H1 source. Existing H1 status span evidence remains as previously adjudicated; H2 status is a later snapshot and H1's exact argv limitation remains. |
| 10 | e-owner-status / 276 | collection B | status-candidate | NO. Later status output does not map to the H1 owner status observation. |
| 11 | e-agy-status / 284 | collection B | status-a6 | NO new H1 source. Existing H1 partial status-span evidence remains unchanged; H2 A6 status is a later snapshot. |
| 12 | e-root-index-hash / 292 | collection B | root-index-hash-before/after | NO. H2 before/after checks establish stability only within the H2 window, not H1 provenance. |
| 13 | f-protected-file-pin / 300 | collection B | protected-selfcheck-before/after | NO. A later hash of the same file is not the source for H1's frozen pin. |
| 14 | h-targets-initial / 324 | v2 precheck | H2 target-1..7 absent/parent/check-ignore observations | NO. H1 checked its own four v2 targets; H2 checked its own seven targets on a different date. |
| 15 | h-targets-final-prewrite / 348 | write script guard | H2 output-path-chain-volume/CreateNew observations | NO. H1's last pre-write guard is tied to the H1 write script and its missing pinned harness material; H2 used a different launcher/guard sequence. |

## Shared adjudication facts

- H1 v2 completed 2026-10-12T11:04:51Z, with its write window recorded as 2026-10-12T10:50:18Z–11:04:51Z. H2 completed 2026-10-13T10:39:08Z; it is a separate RunId and collector.
- The identical whoami stdout hash is a value match, not a provenance link to H1's missing collection-A source.
- H1's two previously accepted status spans are not withdrawn or enlarged by H2. The remaining H1 P2-1 evidence-provenance conclusion is unchanged.
- H2's own 15 provenance pointers are a different set from H1's 15 generic evidence references.
- The frozen inputs contain no deterministic map from an H2 observation to an H1 v2 check at the same time and operation.

## Result

H2 contributes zero admissible original sources for the 15 H1 v2 references. Preserve H1 v2 as PRE_RUN_PASS (23 PASS / 1 NOT_VERIFIED), preserve its DSH Review as CHANGES_REQUESTED and P2-1 as OPEN. X6 remains BLOCKED and unreleased.
