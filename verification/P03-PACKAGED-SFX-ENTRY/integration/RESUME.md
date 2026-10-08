# P03 Codex Integration Checkpoint

时间：2026-10-09（Asia/Shanghai）；Task=`P03`；TaskStatus=`in_review`；ExecutionState=`CHECKPOINTED`。

## 固定状态

- Repository=`G:/CODEX/New Manga`；integration worktree=`G:/CODEX/New Manga.worktrees/P03-review-prep-85482c5b`；branch=`codex/P03-integration-4c04459`；start HEAD=`4c04459bc6b8bf9ef6cba596829ac47f37bc02af`；common-dir=`G:/CODEX/New Manga/.git`。
- Task base=`31abde9bf4b73aea2851931dcd48faa0f750b318`；Owner delivery=`85482c5b001d452953c3ed797ce3c4ed64cae4e3`；formal DSH review head=`4c04459bc6b8bf9ef6cba596829ac47f37bc02af`；DSH decision=`approved`, 0 unresolved P0/P1, 3 open P2 and 3 P3 including 2 deferred.
- Root `main` remains `0a31bbc52447b87a3f04145df62a5ad19baa4b44`, with user/previous-agent uncommitted files. The Antigravity Owner worktree remains at `85482c5b...` with its three untracked dispatch/follow-up files. Both are protected and untouched.

## Completed

- Rechecked Plan, Index, Status, Collaboration Protocol, P08 RESUME, P03 Task/Handoff/RESUME, current root and linked worktrees.
- Reviewed DSH formal R2 raw output and independent Codex review. DSH approved the fixed R2 head; Codex identified C-001 bad relative Handoff link.
- Verified `evaluate_sfx_probe_success` has one production caller passing `install_dir`; several negative tests omit it, but none currently supplies otherwise-valid payload. DSH R-003 is a real fail-open for future callers.

## Open findings / next work

1. Correct P03 AC3 and input table to final installer SHA-256 `5a14c0a98008442bf4e3b70ec1fcc17373e33313cbadf69414fd9584a25a2fa0` (579,528,233 bytes), labeling `d21e89b6...` as the superseded initial revision-2 installer.
2. Make `evaluate_sfx_probe_success` fail closed when `install_dir` is omitted; add a focused test using valid probe payload and omitted `install_dir`.
3. Fix Handoff token count 6,704→6,702 and RESUME link to `../../doc/handoffs/...`.
4. Build a fresh installer from a clean fixed source commit, rerun the focused packaging tests, snapshot oracle, and full packaged Gate; record exact command/shell/versions/exit/hash evidence.
5. Capture `git diff --check` with command, shell, output and EXIT against a fixed head; independently rerun normalization verifier and scope checks.
6. Freeze the corrected delivery head, request a new formal DSH Review (Reviewer remains non-author), disposition R-004/R-006 and any new findings, then complete Codex integration Gate and update Task/Plan/Status/index/roadmap/graph/resume.

## Blockers / risks

- No unresolved product decision currently blocks this integration.
- Code change to the acceptance runner requires fresh packaged verification because it changes the predicate used for acceptance.
- DSH was unable to execute shell/Python in its sandbox during R2; Codex must provide host-side validation evidence. DSH Web visibility remains unverified.

## Resume safety

No Owner worktree, main-worktree dirty file, historical raw artifact, build input, user data, or reviewer workspace has been changed. Current integration worktree was clean at fixed approved head before this checkpoint was created.

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
