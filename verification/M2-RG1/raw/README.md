# verification/M2-RG1/raw/ — evidence index

All logs carry a shell/interpreter header + fixed `HEAD=<hash>` + per-command
`EXIT=` unless noted. Gate summary JSON: `rg1-gate.json` (verdict PASS, 23/23).

| File | Content |
|---|---|
| `rg1-build-sidecar.log` | AC1: `powershell -File packaging/m2ac5/build_sidecar.ps1` @ HEAD=33280f5e (fresh worktree order per M2-AC5 prerequisite), EXIT=0 |
| `rg1-frontend-npm-install.log` / `rg1-frontend-build.log` | AC1: frontend deps + `npm run build` (dist = 2 files), EXIT=0 |
| `rg1-tauri-build-run1.log` | AC1: pre-fix `npx --yes @tauri-apps/cli@2 build`, EXIT=0 (installer sha256 `def5b92b…`, build1 process evidence) |
| `rg1-tauri-build-run2-fix.log` | AC2: post-fix rebuild, EXIT=0 — **gate-anchored installer sha256 `d222073b…`** |
| `rg1-sidecar-manifest-gen.log` / `rg1-sidecar-manifest-build1.txt` | AC1: full-tree sha256 manifest of the sidecar onedir (161 files, M2-AC5 runA format) |
| `rg1-environment-record.log` / `rg1-os-detail.log` | AC1/AC5: toolchain versions (rustc/cargo/node/npm/tauri-cli/pyinstaller/PySide6/venvs) + OS snapshot (Win11 Pro 26200.9457 x64, Ryzen 9 7950X3D, 32 GB) |
| `rg1-console-policy-fix.diff` / `rg1-console-policy-fix-stat.log` | AC2: the bounded-fix diff (main.rs + 3 bridges + spec comment) exactly as committed at 29c71024 |
| `rg1-gate-run.log` | full transcript of `run_release_gate.py` (first run: AC1_BRIDGE_MISCONFIGURED FAIL honestly recorded, probe env corrected, rerun PASS) |
| `rg1-gate.json` | machine-readable gate summary (installer sha256, per-scenario verdicts, timings, environment snapshot) |
| `rg1-warn-warn-core_sidecar.txt` | AC4: the merged PyInstaller warn file copied from the build tree (PyInstaller 6 emits one per spec, covering all four entries) |
| `rg1-baseline-pytest-m2-acceptance.log` | AC6: pytest tests/m2_acceptance — 35 passed, EXIT=0 |
| `rg1-baseline-cargo-test.log` | AC6: cargo test --bin m2rc1-desktop — 38 passed, 1 ignored, EXIT=0 |
| `rg1-baseline-vitest-run.log` | AC6: npx vitest run — 31 passed (5 files), EXIT=0 |
| `rg1-m2ac5-cleanstart-gate.json` | AC4: M2-AC5 clean-start runner verdict on THIS installer — PASS, 25/25 (installer sha256 d222073b… bound) |
| `rg1-m2ac5-cleanstart-runner.log` | AC4: transcript of the M2-AC5 clean-start run (runs "run → move → git restore" flow disclosure at top) |
| `rg1-m2ac5-cleanstart-probe-stdout.log` / `-ac1-run1/run2-stdout.log` / `-production-stdout.log` / `rg1-m2ac5-r1-library-probe.log` | AC4: per-phase stdout captures copied from `verification/M2-AC5/raw/` (runner writes that path hardcoded, P3-9(b); M2-AC5 dir git-restored after the move) |
| `rg1-scope-audit.log` | AC6: mid-delivery scope audit (name-status / diff --check / status --porcelain); flagged 3 evidence logs with trailing whitespace |
| `rg1-final-scope-audit.log` | AC6: final scope audit at the bookkeeping commit content head — name-status all within allowed paths, diff --check EXIT=0 |

## Notes

- Line-ending / trailing-whitespace normalization: the moved `rg1-m2ac5-*`
  runner artifacts (CRLF) plus `rg1-console-policy-fix.diff`,
  `rg1-gate-run.log`, `rg1-os-detail.log`, `rg1-scope-audit.log` had CR and
  line-end whitespace stripped after first commit (content preserved
  character-for-character otherwise) so `git diff --check` over the delivery
  range returns EXIT=0.
- The gate runner never deletes anything outside the lab / install dirs it
  creates under the system temp dir; the host's real
  `%APPDATA%\com.newmanga.m2rc1.desktop` is never written or deleted (P2-4).
