# M2-C1 ZCode Owner Verification — 05 Drift Check & Link Policy

Owner: ZCode. Fixed base: `7478f72fe6f9872cae29f4fa12888b5e1f2380f1`.

## A. Product-tree drift between draft AS-IS baseline and Owner base

Full changed-path list between `eec1aa49d07119f0aa66ff461ebbb55e4595e624` and
`7478f72fe6f9872cae29f4fa12888b5e1f2380f1` under `src/` and `tests/`
(`git diff --name-status eec1aa4… 7478f72… -- src/ tests/`):

| Status | Path | Contract impact |
|---|---|---|
| M | `src/bootstrap/app.py` | None on any Contract claim. Diff inspected by ZCode: the only change replaces a static `QML_PATH = Path(__file__)…` with a `_resolve_resource_root()` helper that switches between source tree and PyInstaller `_MEIPASS` root in frozen mode. The module remains the Qt/QML application entry (the role statement the draft trace cites); it adds no IPC, transport, DB-write, or projection behavior. |
| A | `tests/packaging/conftest.py` | None. New packaging tests (T3.2.1 line of work); not referenced by the Contract. |
| A | `tests/packaging/test_frozen_runtime_contract.py` | None; not referenced by the Contract. |
| A | `tests/packaging/test_packaging_contract.py` | None; not referenced by the Contract. |
| A | `tests/packaging/test_qt_closure.py` | None; not referenced by the Contract. |

`git diff --name-status eec1aa4… 7478f72… -- src/application src/domain src/ui`
→ empty, exit 0. **No drift touches any Contract AS-IS claim.**
`DRIFT_DETECTED` is therefore not raised.

## B. Relative-link policy for the Owner delivery

Owner-added/modified Markdown in this delivery:

1. `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` — byte-identical to the adopted
   draft (Case A). Its internal relative link `../../verification/M2-C1/source-trace.md`
   resolves within the adopted draft head tree but has no target in the Owner
   branch tree (the draft evidence file is not reproduced; allowed paths limit
   Owner verification to `verification/M2-C1/zcode-owner/**`). Treatment per
   decision D-O2: recorded as a known, explained non-semantic limitation; the
   target remains readable from the frozen historical object
   `ac38dede…`; an equivalent Owner-base trace exists at
   `verification/M2-C1/zcode-owner/01-source-trace-owner-base.md`. All other
   links in the Contract are `doc/**`-internal (`../AD-001_TARGET_DESKTOP_ARCHITECTURE.md`)
   and resolve at the Owner base.
2. `verification/M2-C1/zcode-owner/*.md` — cross-reference only files inside
   this `zcode-owner/` directory; no external relative links.
3. `doc/handoffs/M2-C1-zcode-<delivery-short>.md` (separate Handoff commit) —
   links only to paths that exist at its own commit.

No new link to `M2-S1` is introduced anywhere (R-007 policy preserved).

## C. Checks planned in the Handoff (commit-bound)

The commands `git diff --name-status 7478f72… <delivery>` and
`git diff --check 7478f72… <delivery>` require the fixed delivery commit and
are recorded with their raw output in the Owner Handoff after the Owner
Delivery commit exists (staged-tree equivalents are recorded in
`04-git-scope-check.md` before committing).
