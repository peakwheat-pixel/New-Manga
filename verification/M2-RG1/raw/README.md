# verification/M2-RG1/raw/ — evidence index

All logs carry a shell/interpreter header + fixed `HEAD=<hash>` + per-command
`EXIT=` unless noted. Gate summary JSON: `rg1-gate.json` (verdict PASS,
25/25 scenarios, v2 — r1-rework runner). The pre-rework run is archived
verbatim as `rg1-gate-run1.json` (23/23) for the DSH r1 audit trail.

| File | Content |
|---|---|
| `rg1-build-sidecar.log` | AC1: `powershell -File packaging/m2ac5/build_sidecar.ps1` @ HEAD=33280f5e (fresh worktree order per M2-AC5 prerequisite), EXIT=0 |
| `rg1-frontend-npm-install.log` / `rg1-frontend-build.log` | AC1: frontend deps + `npm run build` (dist = 2 files), EXIT=0 |
| `rg1-tauri-build-run1.log` | AC1: pre-fix `npx --yes @tauri-apps/cli@2 build`, EXIT=0 (installer sha256 `def5b92b…`, build1 process evidence) |
| `rg1-tauri-build-run2-fix.log` | AC2: post-fix rebuild, EXIT=0 — **gate-anchored installer sha256 `d222073b…`** |
| `rg1-sidecar-manifest-gen.log` / `rg1-sidecar-manifest-build1.txt` | AC1: full-tree sha256 manifest of the sidecar onedir (161 files, M2-AC5 runA format) |
| `rg1-environment-record.log` / `rg1-os-detail.log` | AC1/AC5: toolchain versions (rustc/cargo/node/npm/tauri-cli/pyinstaller/PySide6/venvs) + OS snapshot (Win11 Pro 26200.9457 x64, Ryzen 9 7950X3D, `TotalPhysicalMemory` 33981165568 B = 33.98 GB) |
| `rg1-console-policy-fix.diff` / `rg1-console-policy-fix-stat.log` | AC2: the bounded-fix diff (main.rs + 3 bridges + spec comment) exactly as committed at 29c71024 |
| `rg1-gate-run.log` | full transcript of `run_release_gate.py` — the v2 (r1-rework) PASS run only. The first-run `AC1_BRIDGE_MISCONFIGURED` FAIL transcript does NOT exist anywhere: the rerun overwrote the stdout redirect before anything was archived (grep over `verification/M2-RG1/**` has zero MISCONFIGURED hits) — text disclosure only, nothing fabricated (DSH r1 P1-1) |
| `rg1-gate.json` | machine-readable gate summary, v2 (r1-rework runner: dual window classes, RG1-CW0 positive control, registry snapshot, DC1a/DC1b seed, pid-scan details, timings) |
| `rg1-gate-run1.json` | archived verbatim copy of the pre-rework (r1-audited) gate summary: 23/23 PASS, timings app 46.0/48.2/157.1, core 239.1/240.5/240.9, ac1 266.5/268.2/280.1 ms — comparison only, not a criterion |
| `rg1-localappdata-newmanga-forensics.log` | P2-3: `%LOCALAPPDATA%\New Manga` forensics after the run1 default-data-root probe — no new persistent files, no content writes (library.db 303104 B and managed tree mtime stay 2026-09-26; only the dir-node mtime 12:50:09 matches the run1 window = transient SQLite WAL/shm artifact) |
| `rg1-warn-warn-core_sidecar.txt` | AC4: the merged PyInstaller warn file copied from the build tree (PyInstaller 6 emits one per spec, covering all four entries) |
| `rg1-baseline-pytest-m2-acceptance.log` | AC6: pytest tests/m2_acceptance — 35 passed, EXIT=0 |
| `rg1-baseline-cargo-test.log` | AC6 (pre-rework): cargo test --bin m2rc1-desktop — 38 passed, 1 ignored, EXIT=0 |
| `rg1-baseline-cargo-test-r2.log` | AC6 (r1 rework): cargo rerun after the P3-1 comment-only Rust edits — 38 passed, 0 failed, 1 ignored, EXIT=0 |
| `rg1-baseline-vitest-run.log` | AC6: npx vitest run — 31 passed (5 files), EXIT=0 |
| `rg1-m2ac5-cleanstart-gate.json` | AC4: M2-AC5 clean-start runner verdict on THIS installer — v2 rerun PASS, 25/25 (installer sha256 d222073b… bound) |
| `rg1-m2ac5-cleanstart-runner.log` | AC4: transcript of the M2-AC5 clean-start run (runs "run → move → git restore" flow disclosure at top) |
| `rg1-m2ac5-cleanstart-probe-stdout.log` / `-ac1-run1/run2-stdout.log` / `-production-stdout.log` / `rg1-m2ac5-r1-library-probe.log` | AC4: per-phase stdout captures copied from `verification/M2-AC5/raw/` (runner writes that path hardcoded, P3-9(b); M2-AC5 dir git-restored after the move) |
| `rg1-scope-audit.log` | AC6: mid-delivery scope audit (name-status / diff --check / status --porcelain); flagged 3 evidence logs with trailing whitespace |
| `rg1-final-scope-audit.log` | AC6: final scope audit at the r1-rework bookkeeping content head — name-status all within allowed paths, diff --check EXIT=0 (audited by DSH r1 at this state) |
| `rg1-final-scope-audit-r2.log` | AC6: final scope audit r2 at the r1-rework final tip (post DSH-r1 rework) — name-status / diff --check / status --porcelain |

## Notes

- Zero-touch (DSH r1 P2-3, rewritten; corrected r2 P1-1(N)): rests on TWO
  mechanisms — (1) every spawn pins `APPDATA` into the lab; (2) the Rust host
  derives the data roots via `packaged_user_root()`
  (`main.rs:315-319,366-367`) and passes them explicitly
  (`main.rs:446-452`; `library_bridge.rs:149-151`), while core_service's
  fallback root is `%LOCALAPPDATA%\New Manga` (`core_assembly.py:562-568`).
  `NEWMANGA_DATA_ROOT` is pinned explicitly only inside the
  core/ac1/seed/DC1b/DC3 probes (run_release_gate.py :409/:445/:658/:702/:802)
  — the app rounds (timed_app_cold_start, :472-481) do NOT pin it; their
  zero-touch rests on the APPDATA pin plus the host-side derivation and
  explicit pass-down. The
  host's real `%APPDATA%\com.newmanga.m2rc1.desktop` is never written or
  deleted (P2-4); the runner never deletes anything outside the lab / install
  dirs it creates under the system temp dir.
- r2 P3-2(N): the runner docstring was corrected ("four PyInstaller warn
  files" -> "the one merged warn-<spec>.txt"; the RG1-Z1 reference rewritten
  as the APPDATA per-process pin wording) — docstring-only text fix, the
  executable logic is ZERO-DIFFERENT from the version that produced the v2
  rg1-gate.json (no gate rerun needed per DSH r2).
- r2 P3-4(N): `rg1-localappdata-newmanga-forensics.log` and
  `rg1-final-scope-audit-r2.log` each received one `HEAD=<hash>` discipline
  line inserted at the top (original content untouched) — backfilled after
  DSH r2 flagged the missing header discipline; the recorded hashes are the
  repo HEADs at capture/audit time respectively.
- Authoritative line-ending / trailing-whitespace normalization list (DSH r1
  P3-3 — exactly 10 files, whitespace-only changes, content preserved
  character-for-character otherwise):
  + batch 1 (trailing whitespace, committed at `a1100d75`, cleaned at
    `b38a646c` — provable from git history): `rg1-console-policy-fix.diff`,
    `rg1-gate-run.log`, `rg1-os-detail.log`;
  + batch 2 (CRLF -> LF before the first commit; re-verified after the v2
    rerun overwrote the same names): `rg1-m2ac5-cleanstart-ac1-run1-stdout.log`,
    `rg1-m2ac5-cleanstart-ac1-run2-stdout.log`,
    `rg1-m2ac5-cleanstart-gate.json`, `rg1-m2ac5-cleanstart-probe-stdout.log`,
    `rg1-m2ac5-cleanstart-production-stdout.log`,
    `rg1-m2ac5-cleanstart-runner.log`, `rg1-m2ac5-r1-library-probe.log`.
  Correction: the first version of this note also listed `rg1-scope-audit.log`
  (giving 11) — git history proves that file was committed clean and never
  modified, so the authoritative count is 10; the earlier "3 files" figure in
  verification-results.md counted batch 1 only.
