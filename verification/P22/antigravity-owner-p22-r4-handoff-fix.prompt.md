你是 P22 的 Antigravity Owner。请按本次复审结果完成一次范围冻结的 Handoff 文档修订，并提交新的固定 commit。

## 固定对象与写入权限
- 仓库/worktree：`G:\CODEX\New Manga.worktrees\P22-roundtrip-serialization-antigravity`
- 当前 HEAD / R3：`3038fe03ba57b42cf5039402b333fbf4b8efbc05`
- parent：`92093792ba0bc653f9423dda2486d558226caf86`
- 唯一允许修改的文件：`verification/P22/antigravity-owner-p22.handoff.md`
- 唯一交付：修订 Handoff + 一个新 commit + 简洁 Handoff，列出新 HEAD、tree、parent、变更路径与实际检查。
- 保留所有既有 untracked / modified 文件；不要 reset、clean、stash、覆盖或删除它们。不要修改 Task、Plan、代码、其他证据或任何共享契约。

## 独立 Review 输入
DSH 对 R3 Handoff 的独立内容 Review 是 `CHANGES_REQUESTED`，P0/P1/P2/P3=`0/0/1/3`，四项均 open。报告：`verification/P22/dsh-p22-review-r3.stdout.md`。DSH 未运行 shell/Git/hash，故 `object_binding=NOT_VERIFIED`，其内容 Review 不代表对象/commit 验证。

请按以下要求逐项修订：
1. **P2-1，区分两种 diff 范围**：在 §3 和 §6 分别记录累计 `base(faea1a2c)..R2` 为 3 条路径，其中 `verification/P04/deterministic_concurrent_sidecar.py` 属 R1 引入；R2 自身增量 `parent(R1=680e3830)..R2` 为 2 条路径：`apps/desktop/src-tauri/src/library_bridge.rs` 与本 Handoff。不要称累计 3 条为“R2 实际变更”。同步 §6 与给 Codex 的 forwardable instruction，要求核对两种范围。
2. **P3-1，限定 diff-check 声明**：准确说明 Antigravity 本轮获授权且实际执行的是哪一个 `git diff --check` 范围；不得据此声称 base..R2 或 parent..R2 的检查通过。若无原始命令输出留存，明确标出“未保留原始输出”，不要补造输出。Codex 独立核验留在 Codex adjudication，不要冒称 Owner 运行。
3. **P3-2，修正状态时态**：把“R3 文档修订已完成收口”改为“本轮文档交付已提交，待独立 Review 和 Codex adjudication”；不要暗示当前新修订已审或已集成。
4. **P3-3，披露 R2 Review 限制**：准确记载 R2 两轮 DSH Review 均 `object_binding=NOT_VERIFIED`，初次 R2 Review CLI exit=`1`、后续 follow-up exit=`0`；内容结论与对象验证分开表述。

## 保持的状态与限制
- 只修 Handoff 证据措辞，不改运行时代码，不扩大产品范围。
- P22 的 Cargo/Rust/Tauri/sidecar/runtime AC2 仍为 `BLOCKED / NOT_RUN`，直到 P02 Build Gate=`PASS` 且 Hard Build Barrier 正式解除，并满足 scratch provenance 条件。
- 不运行 Cargo/Rust/Tauri/build、sidecar、产品测试；不访问 Windows Sandbox。
- 不声称 P22 已集成或 AC2 已通过。

完成后提交新 commit。请只报告真实执行的文件修改、commit/tree/parent/changed paths 和检查结果；不要自审或宣称独立 Review 已通过。
