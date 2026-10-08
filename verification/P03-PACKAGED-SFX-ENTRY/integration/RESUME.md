# P03 Codex Integration Checkpoint

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`in_review`；ExecutionState=`R4_DISPOSITIONS_RECORDED_R5_CANDIDATE_PENDING`。

## 当前恢复点

- Repository=`G:/CODEX/New Manga`；integration worktree=`G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`；branch=`codex/P03-integration-4c04459`；Git common directory=`G:/CODEX/New Manga/.git`。恢复时核对 `main` 与 worktree live HEAD；root 原有24项用户/Qoder/Agent dirty 与 raw evidence 必须保持原样。
- Task base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；Owner delivery=`85482c5b001d452953c3ed797ce3c4ed64cae4e3`；Owner=Antigravity；Reviewer=DeepSeek Harness；Integrator=Codex。Integration commit=`d717c049a41544a6d592943a0b0fe1b76a41a050`，main 已有该 fast-forward，原因与时间顺序记录在 R4 报告及 Task。
- DSH R4=session=`session-d27e8ea9-f983-4c1c-9258-a76cdaba0ac0`；base=`31abde9b…`；reviewed_head=`d717c049…`；decision=`approved`，未解决P0/P1=0/0。报告 SHA=`3a389c2385f5fb7956636b3e94911875f80bc677a4c8673d4f8ec2c294fa755d`；raw JSONL SHA=`39737ec10538469b8d8fa063b10d3e33f6be998b5fd7c61af0a69cd5d33ff8d3`；R4 report/prompt/raw/stderr/exit 已保存。会话已挂载；DSH 自身 shell/Git/test/Gate=`NOT_RUN`，Web/Desktop 可见性未核验。
- R4-01..06 与 Codex C-004/C-005 的修订/证据见 P03 Task 与 manifest；R4-07 明确 deferred cosmetic。Exact `d717c049` evidence：snapshot 16 actual-predicate cases PASS（log 23）；targeted suite 40 passed / 0 skipped（log 24）；同 installer SHA=`2de124f387bfaf1d0d01b1b0279ad319cd453850d223efa9620b0103ce88a814` 的 packaged Gate 28/28 PASS（log 25）；installer 579,537,342 bytes；Gate output 11项逐字节验证归档于 `raw-finalhead-d717-gate-output.zip`。
- Trace 21：base..`d717c049` 共132 paths、zero out-of-scope、diff-check EXIT=0；trace 22 两个只读 normalization verifier 各6/6 PASS。 R4 finding处置候选 `051c086879e52058be80a83bd0b01c3ce080b67e` 的base..HEAD复核为144 paths、zero out-of-scope、diff-check EXIT=0，两个normalization verifier各6/6 PASS；新增日志为26/27， manifest记录SHA。R5固定head须取恢复时worktree live HEAD。
- AC4 语义已澄清：CS-Z2 是 lab 内4个合成 fixture；CS-Z4 证明 host `%APPDATA%` 的4个文件未变化。Gate 未访问用户漫画源目录。R-004 保留 ONNX 未独立重哈希；R3-03 仍留给 P20，不修改范围外文件。
- 当前 Resume 补有 [P03 r3 Handoff](../../../doc/handoffs/P03-PACKAGED-SFX-ENTRY-140a6686-r3.md)。

## 下一条直接指令

先重核 branch/HEAD/status，保留全部其他 Agent dirty/untracked 内容。固定待审候选的 base=`31abde9b…` 与 `git rev-parse HEAD`，检查整个 base..HEAD 路径仅在 Task allowed_paths；对 exact HEAD 运行 `git diff --check`、`verify_normalization.py` 与 `normalize_gate_logs.py --verify-only` 并保存完整日志。然后对该 HEAD 派发真实 DSH R5、挂载会话，并由 Codex 非作者 Reviewer 独立检查同一 exact range。新 finding 修复后重跑受影响 Gate 并重新 Review。双 Review 和集成 Gate 通过后关闭 P03，复核 Plan P01 依赖并建立 released Task；把 P01 当前可核验内容限定在 Git 事实与 Review 载体，缺失报告记 `NOT_VERIFIED`，产品选择留给用户。

保护根工作区既有 dirty、P08/旧DSH raw、Qoder文件、Owner worktree、K07/ONNX、用户源文件、数据库/Lock/Revision；禁止 push、外发、部署或删除。当前会话收到的关机授权仅在 P03 收口及恢复资料保存后执行。

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
