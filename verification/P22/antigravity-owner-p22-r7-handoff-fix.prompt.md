请在既有 P22 Owner worktree 和原 Antigravity 会话中完成 R7 Handoff-only 文档修订。只修改并提交 `verification/P22/antigravity-owner-p22.handoff.md` 一个文件。不要修改 `doc/tasks/P22.md`、代码、测试、其他 evidence 或共享文档；不得运行 Cargo/build/Rust/Tauri/sidecar/runtime/产品测试。不要执行 `git add -A`，提交时只暂存 Handoff 单文件。

## 固定输入

- Worktree：`G:\CODEX\New Manga.worktrees\P22-roundtrip-serialization-antigravity`
- Branch：`agent/antigravity/P22-roundtrip-serialization`
- 本轮基于 R6 HEAD：`a61e2979d7808d1efaa15283a7e17bac038b7748`，tree=`23aa3cfa01c14dcb17ec8d0166d28f96a126fcc7`。
- R6 Handoff SHA-256=`768DFE728D7D8D8426F986D0AE97A4F9FFB9A6DA7590905690F3A3B5DB482461`。
- Live Task 的本轮输入快照 SHA-256=`CC6015D290A6BEE72BF7257C96DE86C7882AED4E82F16B03504FE0CD4A56529B`；权威 R6 DSH finding adjudication=`verification/P22/codex-p22-r6-review-adjudication.md`，SHA-256=`3C5480B926A795FA9C5683B0C3A9329F46D56FAC73E05376CE27559F5A7F9245`。
- DSH R6 report=`verification/P22/dsh-p22-review-r6.stdout.md`，SHA-256=`5B234E4E81C8F0CD26B0DCB3828F051F9608A2252B1FB8271F1A2DED23EA0FE8`；content=`APPROVED_WITH_CONDITIONS`（P0/P1/P2/P3=`0/0/0/2`），`object_binding=NOT_VERIFIED`。

## 必须修复的两项非阻断 finding

1. **R6-1 P3**：Handoff §1 的 R5 Review 历史（当前约 `:55`）只写有三项建议。请明确补入 DSH R5 正式内容结论=`APPROVED_WITH_CONDITIONS`（P0/P1/P2/P3=`0/0/0/4`）、报告路径 `verification/P22/dsh-p22-review-r5.stdout.md` 与 SHA-256=`BB2241825A0A2AD306D5DC9887DBA2E5BAA07C8607A577BDF787B86DF199EF68`。说明 P3-1..3 属 Handoff 修订项；P3-4 是 live Task 时点问题，Codex 已在 `doc/tasks/P22.md:79` 收口。Handoff 参考资料清单（当前约 `:218`）补入 R5 report 与 `verification/P22/codex-p22-r5-review-adjudication.md`。
2. **R6-2 P3**：Codex 已核实 `verification/P22/antigravity-owner-p22-r3-handoff-fix.stdout.md` 在 Owner worktree 存在且为 untracked（`git ls-files --error-unmatch` exit 1，`git status --short` 显示 `??`）。请将该精确相对路径加入 Handoff 的“未暂存保护文件（原样保留，绝不纳入提交）”清单。不要使用覆盖范围更大的 glob。

在 Handoff 简短记录 DSH R6 Review=`APPROVED_WITH_CONDITIONS`（P0/P1/P2/P3=`0/0/0/2`）、object binding=`NOT_VERIFIED`，并说明上述两项是非阻断文档 finding、本轮逐项修订、等待 DSH R7/Codex adjudication。保持既有已闭合 R3/R4/R5 finding 内容和 Gate 声明，不扩大声明。

## 交付要求

- 修订完成后只对目标单文件运行 `git diff --check -- verification/P22/antigravity-owner-p22.handoff.md` 并记录真实 exit。
- 基于指定 R6 HEAD 创建一个新固定 commit；报告新 HEAD/tree/parent、唯一 changed path、Handoff SHA-256、准确的 diff-check exit、tracked/untracked 状态与未运行的测试。
- 不要把修订自述当作 Review 结论；新 head 将由 Codex 核验，再交 DSH 独立 Review。