# Integration record — M2-IPC1 Production Core Lifecycle + Read-only Library Vertical Slice

- **Merge:** `04c1394a7aee6c16e8b841f4fd2e4f3550198686` (parents `5e218bfa` + Owner tip `5556fc8e7a184da25af0f082a3d53f0bd84c56dc`); strategy `ort`, no conflicts; 21 paths (+2315/−13).
- **Fixed base:** `a54bb8c92faefa90f4077e7ac2bb000f6b6712fd`; release commit `4792faa0`; Owner branch `agent/antigravity/M2-IPC1-production-core-library` preserved at tip; worktree `G:/CODEX/New Manga.worktrees/M2-IPC1-agy` preserved.
- **Integrator:** Codex role executed by ZCode session acting as Codex (user full authorization 2026-09-28).

## Head ledger

| Head | Meaning |
|---|---|
| `a54bb8c9` | fixed base (code freeze point) |
| `4792faa0` | release commit (Task file + frozen seam; code-identical to base) |
| `fdff10f3` → `12978bb2` → `c221cf81` → `a2f8d6b8` | Owner delivery: Python core_service + e2e tests / Rust library_bridge + command surface / React library module / docs+evidence |
| `5556fc8e` | **Owner tip (rework)**: R1–R7 from DSH r1 `changes_requested` |
| `04c1394a` | integration merge |
| `c0fe679a` / `ca11159f` / `66416eb6` | integrator ruling commits (see Dispositions) |

## Verification (independent replays; all EXIT recorded)

- Owner (at `a2f8d6b8`): pytest 7 / cargo 30 / vitest 28, diff-check 0.
- Integrator (at `a2f8d6b8`, pre-review): same four commands independently re-run — identical results.
- Owner rework (at `5556fc8e`): pytest **9** / cargo **32** / vitest **29**, diff-check 0; integrator independently re-ran — identical.
- Integrator (at integration head after rulings): pytest **9 passed** EXIT=0; cargo **32 passed** EXIT=0 (pin tests updated for option B); vitest **29 passed** EXIT=0; `git diff --check a54bb8c9..HEAD` EXIT=0.
- **M2-RC2 E2E runner** (at `ca11159f`): `GATE PASS: all phases green` EXIT=0 — `interactive-production-surface` accepts the 5-command production announce; `probe-allowlist-announcement` accepts the frozen 7-command probe surface.
- **M2-AC1 E2E runner** (at `66416eb6`): `GATE PASS`, all scenarios PASS (dual-sample restart, Reader/Export pixel digests identical) EXIT=0.

## Review chain

- DSH r1 (at `a2f8d6b8`): [`changes_requested`](../../../doc/reviews/M2-IPC1-a2f8d6b8-dsh-r1.md) — 2×P1, 5×P2, 8×P3.
- DSH r2 recheck (at `5556fc8e`): [`approved_with_conditions`](../../../doc/reviews/M2-IPC1-5556fc8e-dsh-r2.md) — R1/R3/R4/R5/R6/R7 verified, R2 partially, 0×P0/P1, 2×P2, 5×P3. Handoff delivery-head anchoring (r2 P3-1) is disposed by this record and the Task frontmatter (`delivery_head=5556fc8e`); the Owner handoff file is preserved verbatim (M2-C2 precedent).

## Integrator rulings & dispositions (commits `c0fe679a`, `ca11159f`, `66416eb6`)

1. **DSH r1 P1-2 / r2 P2-1 (cross-Task surface growth) — ruled option B.** The production surface intentionally grows to 5 commands, but the frozen RC2/AC1 test-mode surfaces keep their historical shapes: `command_allowlist` now filters the `IPC1_PRODUCTION_ONLY_COMMANDS` (`core_ping`, `library_list_books`) out of probe/ac1 announcements, so announce ≡ registration in every mode (production 5, probe 7, ac1 6); pin tests assert both directions; the `None → CORE_UNAVAILABLE` guards are kept with a defensive-only comment. Runner expectations: RC2 `PRODUCTION_EXPECTED`=5 (grows, production-mode announce), `PROBE_EXPECTED`=7 (frozen, pinned explicitly); AC1 `EXPECTED_AC1_ALLOWLIST`=6 (frozen). Owner never touched `verification/M2-RC2/**` or `verification/M2-AC1/**` (verified by git).
2. **DSH r2 P2-2 (data-root isolation):** `verification/M2-RC2/run_e2e.py` runtime env now sets `NEWMANGA_DATA_ROOT` to the lab root, so the production-phase `bootstrap.core_service` sidecar cannot fall back to the real `%LOCALAPPDATA%\New Manga` user data root (no migrations/`recover_running_runs` against real user data).
3. **Owner delivery defect fixed by the integrator (`66416eb6`):** unused `React` imports in `LibraryPanel.tsx` / `LibraryPanel.test.tsx` broke the strict `tsc` build — a surface the Owner's verification commands did not cover (vitest skips tsc); first exposed when the AC1 e2e runner's `BLD-frontend` phase returned exit 2. Two-line fix, no behavior change; vitest 29 still green.
4. **DSH r2 P3-2..P3-5:** recorded as follow-ups (R4 test discrimination shape, R6 DOM-shim assertion strength, `LIST_BOOKS_FAILED` retryable semantics vs Contract §8, non-hermetic Rust e2e test) — not blocking; candidates for the next UI/test-hygiene slice.

## Seam compliance (frozen at release, DSH-verified)

stdio JSON-lines sidecar (`bootstrap.core_service`); envelope per Contract §3 with `PROTOCOL_VERSION_UNSUPPORTED` / `UNKNOWN_COMMAND` and result/error mutual exclusion; exactly three commands (`core.ping`, `ListBooks`, `core.shutdown`); spawn only in production mode; EOF/non-zero exit → `CORE_UNAVAILABLE`; 5s shutdown timeout→kill (`wait_timeout_or_kill`); no auto-supervision; BookSummary carries no OS paths; announce ≡ registration in all three modes.

## What this closes

The first **production** React → Tauri invoke → Rust → stdio sidecar → Python Core → SQLite read path is live: the desktop WebView can now list the real library (`ListBooks`) with an explicit empty/unavailable state. Write commands, event channels and automatic supervision remain future slices per the frozen seam.
