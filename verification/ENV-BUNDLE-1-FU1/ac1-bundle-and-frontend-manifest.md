# AC1 artifact pin

Build source worktree: `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1`, HEAD at build: `3bf2604dc9e8ef6be47bd80897e4df05cae077b3`.

## Frozen sidecar

- Build command: `powershell -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force`
- Build environment: existing `G:/CODEX/New Manga.task-envs/m2ac5-build`, Python `3.12.3`, PyInstaller `6.22.3`; no `-SkipWeights`.
- Bundle: `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1/apps/desktop/src-tauri/target/core-sidecar/core-sidecar`
- Bundle size: `1,287,287,472` bytes across `5,563` files.
- Tested executable: `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1/apps/desktop/src-tauri/target/core-sidecar/core-sidecar/core_service.exe`
- Executable size: `68,717,156` bytes; SHA-256: `896bd56286b25bc8539028d52f3ef991cfbcbda24f93ae6c6d75758a7dbfd842`.
- Protocol: `new-manga.core` 2.3, confirmed by direct frozen `core.ping` and clean `core.shutdown`, exit code `0`; see [`ac1-core-service-smoke.log`](ac1-core-service-smoke.log).
- Full build log and exit: [`ac1-build-sidecar.log`](ac1-build-sidecar.log), `EXIT_CODE=0`. It reports all five entry points built, frozen closure and ICU checks passed, and manga/SFX weights SHA-256 verified.

## Frontend

- Commands: `npm ci --no-audit --no-fund`; `npm run build`.
- Environment: Node `v24.15.0`, npm `12.0.1`.
- `package-lock.json` SHA-256 before and after: `520be4900b855e235b8347f8a179b3cffe4a520069a51464151fc880b05f0295` (unchanged).
- Dist: `G:/CODEX/New Manga.workspace/worktrees/ENV-BUNDLE-1-FU1/apps/desktop/frontend/dist`, `2` files / `201,081` bytes.
- Dist manifest SHA-256 (UTF-8 of sorted relative-path, byte-count, file-SHA-256 records joined with platform newline): `d56249d8a1afc8edd88309a7fb4ad9b4add39ec9c68151dca7850c9012898ea7`.

```text
assets\index-B18Ljq2O.js  200805  8a4e4252291e98e3408bd06da06a52ee31d799feee8d79043bc0026a94575995
index.html                276     a05b375c3e34ece03e72196b2177e17903aee01edc10d043f89b0d242051e4f3
```

`npm ci` and `npm run build` raw logs and exit codes: [`ac1-npm-ci.log`](ac1-npm-ci.log), [`ac1-frontend-build.log`](ac1-frontend-build.log); both `EXIT_CODE=0`.
