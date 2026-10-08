# Antigravity Owner 补充交付：P03 revision-2 可追溯性修订

这是同一项已授权 P03 Task 的交付修订。先核对 Owner worktree、common-dir、branch、HEAD 和状态；预期 worktree=`G:/CODEX/New Manga.worktrees/P03-packaged-sfx-entry-antigravity`，branch=`agent/antigravity/P03-packaged-sfx-entry`，HEAD=`d4c17ddb4ed2b5961102018d7d31a383bdaebab3`，common-dir=`G:/CODEX/New Manga/.git`。如果偏离，请记录实际状态后停止修改。保留现有两个未跟踪 `verification/P03-PACKAGED-SFX-ENTRY/antigravity-dispatch.*`，不得 stage、覆盖或删除。

Codex 对 `31abde9bf4b73aea2851931dcd48faa0f750b318..d4c17ddb4ed2b5961102018d7d31a383bdaebab3` 做了只读初审：未发现代码阻断项；发现日志可追溯性问题，故 Task 临时退回 `changes_requested`。正式 DSH Review 尚未开始，不要自行审查、集成或置为 `done`。

## 唯一补充目标
原始 revision-2 证据不得覆盖。新增独立复验日志，补齐每条记录的 PowerShell 版本、working directory、完整命令、stdout/stderr、实际 EXIT；不要伪造已经缺失的原始控制台输出。

1. 重跑定向测试：
`python -m pytest -v tests/packaging/test_packaged_fifth_sfx_entry.py tests/packaging/test_runner_output_dir_required.py`
预期 40 passed。
2. 重跑 snapshot oracle：
`python verification/M2-RUNNER-SNAPSHOT-DEBT/check_snapshots.py`
预期 16 actual-predicate cases PASS。
3. 对当前 NSIS build source `29024a21939917c6d8eb15f1a2bb9ff46cd5bf23` 做一次可复现的 Tauri build 记录。先验证可用的 Tauri CLI verbose 参数，再运行 NSIS build 并将真实完整 stdout/stderr/EXIT 捕获到新文件；保留原 `06-tauri-nsis-build.log`。记录新产物实际路径、字节数和 SHA-256。如果 SHA 变化，更新 revision-2 manifest，并以新 hash 在唯一的新 run 目录重跑 Gate；如果 SHA 不变，也重跑 Gate 以留下完整命令行与参数记录。绝不把 NOT_RUN 写 PASS。
4. 对当前完整 delivery 范围运行并归档：
   - `git diff --name-only ece8765461ce19f7493ce636ff7d69ae6a3e1c4b..d4c17ddb4ed2b5961102018d7d31a383bdaebab3`
   - `git diff --check 31abde9bf4b73aea2851931dcd48faa0f750b318..d4c17ddb4ed2b5961102018d7d31a383bdaebab3`
   记录 PowerShell 环境、完整命令、原始输出和 EXIT。
5. 全新运行 Gate 时要在 log 首部写出完整命令，含 `--installer`、唯一 `--output-dir`、`--sfx-real-page`，保存完整 stdout/stderr/EXIT。原 Gate 与 28/28 结果不改写。
6. 核对 build manifest 的 tool versions、npm/esbuild warning、6 条 Rust warning 与 fresh installer SHA；按事实写入新 Handoff，不得把沉默/未捕获的输出描述为完整输出。

## 文件范围与收尾
只写 `verification/P03-PACKAGED-SFX-ENTRY/**`、`doc/tasks/P03.md` 和一个新的 Handoff `doc/handoffs/P03-PACKAGED-SFX-ENTRY-<new-delivery-head8>-r2.md`。不得改代码或其他产品路径；旧 Gate、首轮原始证据、旧 Handoff、历史 dispatch raw 全部保留。更新 RESUME 记录本轮 changes_requested→in_review、实测证据、固定 build source、installer SHA 和新的 delivery head。必须只 stage 允许的明确文件，避免添加未跟踪 dispatch raw。提交新的 delivery checkpoint 后，Task 可恢复 `in_review` 并由 DeepSeek Harness 正式复审。

如遇构建输入/工具无法复现，记录真实阻塞与 NOT_RUN，不得伪造 PASS。不要 push、部署或清理任何其他工作区。
