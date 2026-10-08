# P03 Codex Integration Checkpoint

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`in_review`；ExecutionState=`FINAL_REVIEW_CHECKPOINT_PENDING`。

## 当前恢复点（优先于下方历史阶段记录）

- Repository=`G:/CODEX/New Manga`；integration worktree=`G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`；branch=`codex/P03-integration-4c04459`；common-dir=`G:/CODEX/New Manga/.git`。
- Task base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；Owner delivery=`85482c5b001d452953c3ed797ce3c4ed64cae4e3`；pre-review candidate=`2d114480e04528c3340247d41fe463c4c72c1b72`。旧 DSH R2 对 `4c04459…` 的 approved 不覆盖修复/新 Gate；需对本 checkpoint 产生的新固定 head 再正式 DSH Review。
- 当前有 Task/RESUME/manifest 修改与三个 Task-local untracked trace；这些是本次受控 P03 checkpoint，不属于用户或其他 Agent 文件。Root `main` 的用户/历史 Agent dirty/raw、Antigravity Owner worktree 三个 untracked helper 与 DSH raw 均保持保护。
- 40 项定向测试、16 项 Snapshot oracle、frontend/Sidecar/Tauri NSIS builds 及新 installer packaged Gate 28/28 PASS 均已完成。Installer SHA=`2de124f387bfaf1d0d01b1b0279ad319cd453850d223efa9620b0103ce88a814`。细节见 P03 Task 与下方历史验证阶段。
- 两份只读 normalization verifier 对 candidate `2d114480…` 均 EXIT=0；trace 在 `build-logs/09-existing-normalization-readonly.log` 与 `10-gate-normalization-readonly.log`。固定范围检查 `31abde9…2d114480` 为 114 paths、zero out-of-scope，`git diff --check` 空输出/EXIT=0，trace=`build-logs/11-fixed-head-diff-check.log`。
- **立即下一步：**仅 stage Task、RESUME、manifest 与这三份日志；跑 `git diff --cached --check` 后提交；读出新 commit 作为 fixed DSH review head。再对该精确 head 运行 scope check、`git diff --check` 和两份只读 normalization verifier，将真实输出/EXIT 纳入正式 DSH prompt/证据；然后派发 DSH 非作者 Review，并让独立 Codex Reviewer 对同一 base/head 更新报告。修复所有需要阻塞集成的问题并重新固定/Review；通过后完成 Codex 集成 Gate 与 P03 治理收口。
- 用户新增指示：P03 当前任务完成并把下一次自动推进提示词保存后，关闭计算机；无需等全路线图完成再关机。下次启动应先读当前 Live Git、STATUS 与本 RESUME，再接着已释放 Task 自动推进。
- 以下 `## 修订验证进展` 起为按时间记录的历史阶段，不再作为当前待办清单。

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
