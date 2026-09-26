"""Bring-up run log for M2-RC1 (raw commands, exit codes, owner-side defects).

Host: Windows 11 (NT 10.0.26200), Python 3.14.6 (.venv absent -- system
python used for pytest), rustc/cargo 1.98.1, node v24.15.0, WebView2 Runtime
153.0.4234.48, tauri 2.11.x per Cargo.lock.

1. pytest (35 cases)
   python -m pytest tests/m2_resource_channel -q            exit 0 (35 passed)
   Bring-up defects found and fixed (all in new probe code):
   a. service.issue accepted drive-qualified rel paths -> added `X:` check
   b. service.resolve raised NameError on expiry (missing E_EXPIRED import)
   c. handle_resolver lacked the pre-open reparse walk (CreateFileW traverses
      junctions) -> early REF_REPARSE_POINT layer added; handle containment
      remains the authoritative check
   d. concurrency test used bare write_bytes (sharing violation instead of
      the intended rewrite) -> switched to the M2-S2 pre-held write handle
      (share_write availability-first mode) and rewrote the NOT-yet-read
      block (flipping already-read bytes cannot change the stream digest)
   e. expiry tests used clock injection instead of poking internals

2. cargo test (9 cases) -- first run requires generating Cargo.lock, then
   `cargo test --locked` is reproducible
   cargo generate-lockfile                                   exit 0
   cargo test --locked                                       exit 0 (9 passed)
   Bring-up defects found and fixed:
   a. tauri Manager trait import, borrow restructuring in the grant cache
   b. mock IDs did not follow the m2id.v1.<43-char> convention -> URL segment
      mapping unified (build_url strips the prefix; handler rebuilds it)
   c. identity test overwrote the file in place (NTFS keeps the file index)
      -> unlink+write (M2-S2 relink method) so FILE_IDENTITY_CHANGED fires
   d. Win32 test helper leaked the handle (mem::forget) which blocked later
      writes -> closing capture_facts_for_tests helper

3. npm test (8 vitest cases) + npm run build
   npm test --prefix apps/desktop/frontend -- --run          exit 0 (8 passed)
   npm run build --prefix apps/desktop/frontend              exit 0
   Bring-up defect: bare `fetch` stored as a method default loses `window`
   -> "Illegal invocation"; wrapped in an arrow.

4. end-to-end matrix (real Python Core sidecar + Tauri host + WebView2 page)
   python verification/M2-RC1/run_e2e.py                     exit 0 (10/10 PASS)
   second run                                                exit 0, identical
   Bring-up defects found and fixed:
   a. the embedded page URL has no query string -> probe mode switched from
      `?probe=1` to host-provided probe_config (M2RC1_PROBE_OUT presence)
   b. withGlobalTauri required for window.__TAURI__ (no npm-bound invoke)
   c. `into_issued` resolved the grant for the presentation size, which
      renewed the sliding TTL before any consumption -> issue response now
      carries size; TTL expiry (E-05) verified after the fix
   d. E-05 ttlOverride was dropped by host_bridge -> ttl_seconds passthrough
   e. a gitignore path mistake committed target/ artifacts -> commit amended
      (git rm -r --cached) before delivery; .gitignore corrected

5. NOT_RUN / UNVERIFIED ledger
   - S1-B6 cold-cache P95: no safe cache-clearing method on this host; the
     hot-cache P95 (~1 ms) is measured and the 1 s cold target stays a target
   - S1-B3 (DACL/integrity level), S1-B8 (MSIX/AppContainer packaging):
     NOT_RUN; no product-level security or packaging readiness is claimed
   - S1-B5: restart semantics (old IDs never re-bound) verified in pytest;
     key lifecycle / cross-restart table persistence NOT_RUN
   - model weights channel: out of scope (T7), not implemented
   - product pytest suite beyond tests/m2_resource_channel: untouched by this
     Task (no product regression scope); full-suite run belongs to integration
"""
