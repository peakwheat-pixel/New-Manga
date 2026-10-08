# P03 Codex Integration Checkpoint

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`done`；ExecutionState=`CODEX_INTEGRATION_GATE_PASS`。

## 当前恢复点

- Root `main` 已集成 `552464238a69ad2cea63cff18abe98f412dbae87`；P03=`done`，`integration_commit=552464238a69ad2cea63cff18abe98f412dbae87`。当前没有Active Task；P01为Plan中的下一候选，待在live main上正式释放。
- DSH R5只批准 `31abde9b..7677e9c3`；DSH R6只批准 `31abde9b..f09100d5`。两轮均approved且未解决P0/P1/P2=0；Codex非作者复核未发现新P0–P3。DSH自身shell/Git/tests/Gate仍`NOT_RUN`（Win32 5），Web/Desktop visibility=`unverified`。
- Codex integration Gate：base..552共162 paths、零越界、`git diff --check` EXIT=0；d717..552产品/runner/test/build路径零差量。Gate报告见[`codex-integration-gate.md`](codex-integration-gate.md)。Manifest的55组artifact SHA/size已在本worktree 552下55/55逐字节匹配；main的`core.autocrlf=true`只导致工作树换行编码差异，未覆盖源artifact。R5 prompt精确5463 bytes及manifest hash仍保存在本worktree。
- Snapshot 16 actual-predicate cases、targeted tests 40/40（0 skipped）与packaged Gate 28/28 PASS均绑定source `d717c049a41544a6d592943a0b0fe1b76a41a050`及installer SHA `2de124f387bfaf1d0d01b1b0279ad319cd453850d223efa9620b0103ce88a814`。d717 structured JSON保存在`raw-finalhead-d717-gate-output.zip`内的`cleanstart-gate.json`；log 30核对归档11项逐字节一致。
- 根checkout原有24项用户/Qoder/Agent dirty和untracked仍须保留；不stage、不stash、不覆盖、不清理。

## 下一条直接指令

先核对live `main`、Plan、Status和P01恢复点。按已经审核的P01范围建立Codex worktree并正式释放：Owner=Codex、Reviewer=DeepSeek Harness。核实GC2/DETECT3 Git对象与交付证据；缺失的ANNOTATE-R2/SYNTH独立Review载体必须记为`NOT_VERIFIED`。完成后派发DSH固定head Review，再由Codex完成集成Gate、更新Task/Plan/Status/依赖图与恢复点。

## 保护边界

Keep the root's 24 dirty entries, retained raw Gate folders, Owner worktree, user data, locks, current/pinned revisions, K07/ONNX inputs and Qoder evidence untouched. No push, external message, deployment or deletion.
> 以下各节记录已完成的历史阶段证据；其中当时写的“下一步”是阶段日志，不覆盖本文件顶部的当前恢复点与下一条直接指令。

## 历史执行记录：修订验证进展

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
