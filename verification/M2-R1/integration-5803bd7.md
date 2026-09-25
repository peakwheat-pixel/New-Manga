# M2-R1 Codex integration record

## Fixed points

- Authorized base: `6a68fdeb92d8a1c7903166a8076d6260bf8fa79a`
- Owner start: `5d989bab6c5c8a24a5112303f95c2b8eea356bdc`
- Reviewed delivery head: `5e2800b93da1d3516449f8765a06828822a7e9b1`
- Final author handoff/backfill head: `052f99cb861adfb1602bd34b4cac86d4567d6b97`
- Approved non-author Review: `doc/reviews/M2-R1-5e2800b.md` at `79b1a77477cc325211483ffe5c38199b752402a7`
- Codex integration merge: `5803bd7b9e80ba780e7a7f12078b00b9178e6f86` (parents: review-record commit `79b1a77477cc325211483ffe5c38199b752402a7`, author handoff head `052f99cb861adfb1602bd34b4cac86d4567d6b97`)

## Integration verification

The approved Review was bound to `reviewed_head=5e2800b`; the appended `052f99c` commit only adds the round-2 Handoff, rewrites the `09` verification log and backfills delivery metadata. Codex independently rechecked the final appended state before integration.

| Check | Result |
|---|---|
| Stale initial-count phrase | **PASS** — the reviewed author set had 15 text files including the new Handoff and `09` log, with 0 matches; the added integration record was also scanned, so all 16 current M2-R1 text files have 0 matches |
| Artifacts | **PASS** — 20 formal runs (9+5+6), 21 `probe.json` files including one excluded smoke, 45 PNGs; all JSON records exit 0 with empty `errors` |
| Original evidence since first delivery `87afdd2` | **PASS** — no changes under `verification/M2-R1/raw/` |
| Whitespace | **PASS** — `git diff --check` from `owner-start` through both `5e2800b` and `052f99c` exits 0 |
| Authorized/forbidden paths | **PASS** — 84 changed paths in the author range are within M2-R1's authorized documentation/evidence scope; no `src/**`, `tests/**`, `requirements*`, packaging/Schema, or `verification/T3.2.1/**` changes |

No product tests were run as part of this research/documentation integration; their state remains `NOT_RUN`. No production code, product tests, dependency manifests, packaging, Schema, or T3.2.1 evidence was integrated.

## Registered result and limits

M2D1-22 is registered as `MEASURED_WITH_LIMITATIONS`: the tested production adapter components ran on `windows`, `offscreen`, and `minimal` with Windows 11 `10.0.26200` and PySide6/Qt `6.11.2`. The evidence supports only those tested combinations. QML/`QQuickWindow` behavior remains `UNVERIFIED`; production `main()` modes and end-to-end document rendering remain `NOT_RUN`. The integration grants no implementation or migration authorization and does not change I1/I2/UI1 or T3.2.1 state.
