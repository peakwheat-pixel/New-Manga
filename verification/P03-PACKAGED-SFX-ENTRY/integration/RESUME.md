# P03 Codex Integration Checkpoint

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`in_review`；ExecutionState=`R3_CONDITIONS_CLOSED_R4_REVIEW_PREP`。

## 当前恢复点（优先于下方历史阶段记录）

- Repository=`G:/CODEX/New Manga`；root `main` 与 integration worktree source head=`423ea5f196e6276f007bd3f96e381fa893985eb9`；branch=`codex/P03-integration-4c04459`；common-dir=`G:/CODEX/New Manga/.git`。root原24项用户/Agent dirty与raw文件快进前后均保留。
- Task base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；Owner delivery=`85482c5b001d452953c3ed797ce3c4ed64cae4e3`；Owner=Antigravity；Reviewer=DeepSeek Harness；Integrator=Codex。
- DSH R3已对`423ea5f1…` approved，session=`session-4401e9bb-28cb-42a1-8447-608b7fc80b8e`；报告/raw及SHA、exit、环境限制见`integration/dsh-review-r3.md`与manifest。DSH自身shell/Git/test/Gate=`NOT_RUN`；web可见性未核验。
- DSH条件R3-01/02已处置：固定集成commit `423ea5f1…` 上40项定向测试`40 passed`、同一installer SHA=`2de124f3…`的packaged Gate`28/28 PASS`，均EXIT=0，日志19/20；122 paths、零越界、diff-check EXIT=0、两份normalization 6/6，日志17/18。11项Gate raw output逐字节归档于`raw-finalhead-gate-output.zip`并有manifest SHA索引；本地隔离实验目录`run-2de124f3-finalhead-423ea-py314`与TEMP=`C:\Users\49745\AppData\Local\Temp\codex-p03-gate-423ea-py314`均保留不清理。
- R3-03：`packaging/release-gate/run_release_gate.py`和旧`main.rs`注释均超出P03范围；风险登记为P20后续Gate任务，无P03代码修订。
- DSH R3 report SHA256=`90892d5ed121533ed83768dbd21c7b539d1dae6dcd630c1a55d3e7dcdd65f041`；raw JSONL SHA256=`BE9B8D4DB40FEBB01CA93894328281915FBCF34F03DED6D0D8A2CCB078CDE509`。其approved不覆盖处置后新commit；必须重新固定head做DSH R4及Codex非作者复审。

## 下一条直接指令

核对HEAD与dirty路径后，提交本checkpoint涉及的P03文件/证据；再对该新候选跑fixed-range scope、`git diff --check`和两份只读normalization verifier，记录真实输出与EXIT。创建DSH R4 prompt并用真实`dsh --profile headless --json`在此worktree dispatch、收回JSONL/stderr/exit与最终Review，mount该session到精确worktree；让已有Codex独立Reviewer检查同一base/head。解决阻断后更新P03 Task、Plan、Status、依赖图、README与RESUME至done，再复核P01依赖、创建并释放P01、保存下次自动推进提示词，最后按本轮用户指示关闭计算机。

- 保护root Qoder `.qoder-credits/**`、历史dispatch、P08 DSH raw、主checkout已有P03 DSH R2原始文件及Antigravity Owner worktree三个untracked helper；不stage/修改/stash/清理。
- 不改`src/**`、`apps/**`、Schema、contracts、依赖、build spec/script；K07与ONNX外部输入只读；任何安装/APPDATA/WebView数据只在Gate隔离TEMP lab中操作。

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
