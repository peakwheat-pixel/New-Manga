# P03 Codex Integration Checkpoint

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`in_review`；ExecutionState=`C002_TEST_FIX_CHECKPOINT_PENDING`。

## 当前恢复点（优先于下方历史阶段记录）

- Repository=`G:/CODEX/New Manga`；integration worktree=`G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`；branch=`codex/P03-integration-4c04459`；common-dir=`G:/CODEX/New Manga/.git`。
- Task base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；Owner delivery=`85482c5b001d452953c3ed797ce3c4ed64cae4e3`；last committed candidate=`fb5782c51eab0d5dc3267770c9a0a7df8f343175`。独立 Codex Review 对该 head 发现 C-002 P2：success-negative 参数化用例省略 `install_dir`，因此 fail-closed 前置条件遮蔽了被测负例；旧 DSH R2 对 `4c04459…` 的 approved 不覆盖当前候选。
- 当前变更是 C-002 的 test-only 修复：建立实际 `install_dir` 与内部 weights path，每个负例先断言未修改基线会通过，再应用目标坏条件。对应 40/40 测试通过，`build-logs/14-targeted-regression-tests.log`。Task 文档已登记 C-002/C-003，需随此 checkpoint 一并提交。
- Root `main` 用户/历史 Agent dirty/raw、Antigravity Owner worktree 三个 untracked helper 与 DSH raw 均保持保护；Integration worktree 当前有 C-002 测试、Task 修改，以及 `build-logs/12–14` 和一份未派发的 R3 prompt 草稿。
- Fresh installer SHA=`2de124f387bfaf1d0d01b1b0279ad319cd453850d223efa9620b0103ce88a814`；前序 frontend/Sidecar/Tauri NSIS build、同 installer packaged Gate 28/28 PASS、16 项 Snapshot 与原始/规范化日志验证均已完成，见 P03 Task 与下方历史阶段。
- 上一固定 head `fb5782c5…` 的 scope/diff trace=`build-logs/12`（117 paths、zero out-of-scope、`git diff --check` EXIT=0）；normalization trace=`build-logs/13`（两份 verifier EXIT=0）。这两项发生在 C-002 测试修改之前，提交后必须对新 head 重跑并更新 trace/prompt。
- **立即下一步：**已更新 manifest、两份 RESUME 和 Task；仅 stage P03 Task/test/evidence/checkpoint paths，跑 `git diff --cached --check` 后提交。取得新 HEAD 后重跑 `base..HEAD` scope + diff-check 和两份 normalization verifier；再触发正式 DSH Review 与 Codex 独立复审，二者都使用同一精确 head。Review findings 要先处理并重审；approved 且 Codex 集成 Gate 通过后才收口 P03。
- 用户指示：P03 当前任务完成、下一次自动推进 prompt 保存后关闭计算机；下次先核对 Live Git、STATUS 与此 RESUME，再自动进入路线图推进。
- 以下 `## 修订验证进展` 起为按时间记录的历史阶段，非当前待办清单。

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
