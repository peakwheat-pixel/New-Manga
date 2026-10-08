# P03 Codex Integration Checkpoint

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`in_review`；ExecutionState=`R5_APPROVED_CODEX_INTEGRATION_PENDING`。

## 当前恢复点

- Repository=`G:/CODEX/New Manga`；integration worktree=`G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`；branch=`codex/P03-integration-4c04459`；common-dir=`G:/CODEX/New Manga/.git`。恢复时核对 live `main` 与 worktree HEAD/status。
- Task base=`31abde9bf4b73aea2851931dcd48faa0f750b318`; Owner=Antigravity; Reviewer=DeepSeek Harness; Integrator=Codex. Existing integration commit=`d717c049a41544a6d592943a0b0fe1b76a41a050`.
- DSH R5 session=`session-089283e0-246f-44e3-9c2f-14dea850e4e2`; reviewed head=`7677e9c324da2fde618e7cd6fdba2363abeb1f1b`; decision=`approved`; unresolved P0/P1/P2=0/0/0, P3=1, P4=4. Report/prompt/raw/exit and hashes are recorded in Task/manifest; session mounted to this worktree. DSH own shell/Git/tests/Gate=`NOT_RUN` because of Win32 5; web/Desktop visibility=`unverified`. Codex non-author review of the same head found no new P0–P3.
- Logs 28/29 version exact-head scope and both read-only normalization results; log 30 compares every one of the 11 members of `raw-finalhead-d717-gate-output.zip` byte-for-byte against the retained directory, EXIT=0. Manifest records hashes.
- Exact tested source remains `d717c049`: snapshot 16 cases PASS, targeted suite 40 passed / 0 skipped, same-installer packaged Gate 28/28 PASS; all EXIT=0. No runner/test blob changes after that source commit.
- Preserve root checkout's 24 existing dirty/untracked entries and both untracked retained raw Gate folders. P03 remains `in_review` pending Codex AC5 integration.

## 下一条直接指令

Recheck Git and the authority docs, verify the manifest/review/evidence hashes, and finish Codex AC5 integration. The DSH and Codex approvals apply to base `31abde9b…` / reviewed head `7677e9c3…`; do not describe a later commit as DSH-reviewed. Because runtime/test blobs match tested source `d717c049`, use range/evidence/integration checks instead of rerunning the installer. Fast-forward only after the gate passes, then set P03 `done` and release P01 after rechecking authoritative Plan dependencies.

## 保护边界

Keep the root's 24 dirty entries, retained raw Gate folders, Owner worktree, user data, locks, current/pinned revisions, K07/ONNX inputs and Qoder evidence untouched. No push, external message, deployment or deletion.
## 修订验证进展

- 2026-10-09，固定代码修订提交 `db2c1e9390b0b8601877c366d4a43699b1d12ee5`：R-003 现在要求有效 weights path 必须可证明位于非空 install_dir 下；省略 install_dir 时返回 FAIL。同步修正 AC3/input table hash、R-005 token 数与 C-001 相对链接。
- 定向命令：`C:\Python314\python.exe -m pytest -v tests/packaging/test_packaged_fifth_sfx_entry.py tests/packaging/test_runner_output_dir_required.py`；PowerShell 7.6.6；Python 3.14.6；40 passed，0 skipped，EXIT=0。日志：`build-logs/01-targeted-tests.log`。
- Snapshot 命令：`C:\Python314\python.exe verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py`；16 actual-predicate cases PASS，EXIT=0。日志：`build-logs/02-snapshot-check.log`。
- 两项验证均只触及隔离测试临时目录和本 checkpoint 的新日志；运行前代码文件已提交干净，新增日志目录是命令输出。
- 下一步：提交本节与日志后，在 clean source commit 上对 K07 与 v2b weights 只读复算 hash，记录 Node/Rust/Python/NSIS 工具版本；随后运行 frontend、sidecar、NSIS fresh build，并将 build source HEAD / installer SHA 写入新 manifest 后再运行 packaged Gate。

## Fresh package preflight

- Preflight ran from clean checkout HEAD `14ed25be0670ae5dc1286cc0a9cff0d5b7492409`; branch `codex/P03-integration-4c04459`; PowerShell 7.6.6.
- External read-only K07 page hash/size matched: `28dab503aca3c903111488c03e857b430d309421a4a54bab335a63bbe7b9cec4`, 1,020,887 bytes. v2b SFX weights matched: `944e811410933ad6ff8d32446fcc9eef90fb463794e1874ce83035e83acd418d`, 40,824,255 bytes. Neither file was copied or modified.
- Toolchain preflight EXIT=0: Node `v24.15.0`, npm `12.0.1`, rustc `1.98.1`, cargo `1.98.1`, build Python `3.12.3`, PyInstaller `6.22.3`, NSIS `v3.11` at `C:/Users/49745/AppData/Local/tauri/NSIS/makensis.exe`. Full trace: `build-logs/00-input-preflight.log`.
- No product/user `%APPDATA%` data was read or written during preflight. Next: commit preflight trace/checkpoint, then run frontend `npm ci --no-audit --no-fund` and `npm run build` from this isolated worktree, retaining exact command output and exit codes.

## Frontend dependency install

- `npm ci --no-audit --no-fund` completed from `apps/desktop/frontend` at the clean pre-command source HEAD recorded in `build-logs/03-frontend-npm-ci.log`; PowerShell 7.6.6; EXIT=0; 140 packages installed.
- npm 12 reported one warning: the configured `allowScripts` policy blocked `esbuild@0.21.5` postinstall. No script was manually approved; continue with the planned frontend build and capture the actual result.
- `node_modules` is gitignored and was left in the isolated integration worktree. Next exact step: run `npm run build` in `apps/desktop/frontend`, record shell/HEAD/status/output/EXIT, then checkpoint.

## Frontend production build

- `npm run build` completed from `apps/desktop/frontend` at source HEAD `19f5348ff8ad88c4d5baaefc6fa1ab65968210e0`, with a clean working tree before command start; PowerShell 7.6.6; TypeScript and Vite production build passed; EXIT=0. Log: `build-logs/04-frontend-npm-build.log`.
- Vite transformed 50 modules and emitted `dist/index.html` plus the frontend JS bundle. `dist/` and `node_modules/` are ignored build output; no user source or runtime data was touched.
- Next: commit this phase's log/checkpoint; then run the frozen Sidecar build from the clean isolated target tree.

## Sidecar fresh build

- Command `powershell.exe -NoProfile -ExecutionPolicy Bypass -File packaging/m2ac5/build_sidecar.ps1 -Force` ran from the clean integration worktree at source HEAD `a7161ca316052d14aefd24b920b146afd1969017`; Windows PowerShell 5.1 child process; Python 3.12.3 / PyInstaller 6.22.3; EXIT=0. Full log: `build-logs/05-sidecar-build.log`.
- Build script reports five required executables present in the frozen bundle, closure assertions passed, zero shadowing ICU binaries, and pinned manga/SFX model copying succeeded. Independent output check confirms all five executables and SFX weight size/hash `40,824,255` / `944e8114...` match.
- PyInstaller produced optional-module warnings for tensorboard/TorchVision/SciPy and Torch deprecations; build completed and all project closure/pin assertions passed. No package/spec/dependency change was made.
- `apps/desktop/src-tauri/target/**` remains gitignored build output. Next: commit this log/checkpoint, then run `npx --yes @tauri-apps/cli@2 build` from `apps/desktop/src-tauri` on a clean checkout.
