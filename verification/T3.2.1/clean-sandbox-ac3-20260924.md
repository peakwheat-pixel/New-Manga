# T3.2.1 Clean Windows Sandbox AC3 Attempt

Date: 2026-09-24 (Asia/Shanghai)

Agent: Codex

Host repository: `G:/CODEX/New Manga`, `master` at
`15e67507022fdfb40664d72e24aa7bb1e1cc865c`.

Candidate source tree: `37d5488ebf8e33f897e802b4147cbd5fb1ad8e04`
(`agent/antigravity/T3.2.1-repair-7`; not integrated).

Latest production packaging code in that tree:
`7d687f51567d4f947fee9b3f6eff4bc95e2b6413`.

Sandbox: Windows 11 Enterprise x64, version `10.0.26100`, build `26100`;
account `WDAGUtilityAccount`.

This records a failed clean-environment startup and a controlled diagnosis. It is
not an AC3 pass, a product fix, or permission to integrate the candidate branch.

## Baseline package attempt

The build transcript identifies source tree `37d5488`, Windows 11 Pro x64 build
26200, Python `3.12.3`, PyInstaller `6.22.3`, and build environment
`T3.2.1-packaging-py312`. The package executable SHA-256 was
`F276CD9C8D25BBB407B7E4337889CCAF994DF5E81C10556ACE567918FCC366A4`.
The generated `artifact-manifest.sha256` is included alongside the build log.

The package was copied into the Sandbox and its executable hash matched. No
`python`, `py`, or `git` command was available there. Running
`NewManga.exe --smoke-test --data-root C:\NewMangaTestData` exited `1`; no
database was created. Stderr reports `ImportError: DLL load failed while
importing QtCore` at frozen `app.py:36`.

The Sandbox environment is usable for isolated Windows testing, but this first
attempt disproves AC3 startup for this artifact. The full GUI workflow remains
not run.

## Dependency diagnosis

`Qt6Core.dll` (Qt `6.11.2.0`) imports 20 named symbols from `icuuc.dll`. The
packaged `_internal/icuuc.dll` is version `78.3.0.0`, SHA-256
`93CC29031627A72A12C79328F441359CF0570F8E7341D9C4F4555F34D49BB779`. It is
byte-identical to the `icuuc.dll` available under the host Codex Poppler runtime
directory on `PATH`. That DLL exports none of the 20 symbols imported by
`Qt6Core.dll`. The static comparison and paths are recorded in
[`icu-import-check.log`](clean-sandbox-ac3-20260924/icu-import-check.log).

The host and Sandbox `C:\Windows\System32\icuuc.dll` is version `72.1.0.4`,
SHA-256 `59D134DDC15AE0594F0A328979F8201662FC82634DDB7C537B156E7CF871F5EB`;
its export table contains all 20 names imported by this `Qt6Core.dll`. The
build log does not record PyInstaller's resolved source path for `icuuc.dll`,
so the exact resolver decision is not directly logged. The package/source hash
match, host `PATH` candidate, import/export comparison, and controlled
substitution below jointly identify an incompatible bundled ICU as the
startup cause.

As a diagnostic only, the Sandbox copy of the package was temporarily given
that Sandbox's own System32 `icuuc.dll` in place of the bundled file. With no
PATH additions and no other package change, the smoke process exited `0` and
created `C:\NewMangaIcuProbeData\library.db`. Its stderr still contains QML
warnings and null-view-model errors; it does not establish an interactive GUI
workflow. The original package ICU was restored inside the Sandbox copy and
verified at its original SHA-256; the backup no longer exists. The host build
artifact was not modified.

## Gate disposition and next action

- AC3 startup checkpoint: **FAIL** for this fixed artifact; full GUI workflow:
  **NOT_RUN**. AC3 remains a release blocker.
- AC4 Qt runtime closure: **FAIL** for this artifact because `QtCore` cannot
  import with the bundled ICU. AC5 remains **NOT_RUN**. AC6/AC7 remain
  **PARTIAL / NOT_RUN**. R-014–R-016 remain open.
- Antigravity, as packaging implementation Owner, must fix deterministic Qt/ICU
  dependency selection within the already released T3.2.1 packaging scope.
  The correction must not rely on this diagnostic file replacement. Add a
  build-time closure check that confirms imported symbols resolve to the
  selected dependency, then build and test an unchanged package in the
  Sandbox. Confirm the supported Windows matrix before deciding whether ICU is
  bundled or intentionally supplied by Windows.
- DeepSeek Harness must independently review the fixed delivery. This
  documentation and the earlier REPAIR-8 approval do not approve product
  integration. Do not merge `agent/antigravity/T3.2.1-repair-7` or any derived
  delivery into `master` before Codex closes the full T3.2.1 Release Gate.

## Raw evidence

- [`build.log`](clean-sandbox-ac3-20260924/build.log)
- [`artifact-manifest.sha256`](clean-sandbox-ac3-20260924/artifact-manifest.sha256)
- [`sandbox-baseline.log`](clean-sandbox-ac3-20260924/sandbox-baseline.log)
- [`sandbox-baseline.stderr.log`](clean-sandbox-ac3-20260924/sandbox-baseline.stderr.log)
- [`sandbox-icu-substitution.log`](clean-sandbox-ac3-20260924/sandbox-icu-substitution.log)
- [`sandbox-icu-substitution.stderr.log`](clean-sandbox-ac3-20260924/sandbox-icu-substitution.stderr.log)
- [`sandbox-restore.log`](clean-sandbox-ac3-20260924/sandbox-restore.log)
- [`loadlibrary-qt6core.log`](clean-sandbox-ac3-20260924/loadlibrary-qt6core.log)
- [`loadlibrary-pyside.log`](clean-sandbox-ac3-20260924/loadlibrary-pyside.log)
- [`loadlibrary-shiboken.log`](clean-sandbox-ac3-20260924/loadlibrary-shiboken.log)
