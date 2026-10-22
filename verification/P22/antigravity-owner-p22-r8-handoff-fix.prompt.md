请在原 Antigravity 会话 59764b45-3139-42b3-98e7-3ae79f3746b4 继续处理 P22 R8 Handoff 文档修订。

## 固定任务与状态

- Codex P22 Task 快照：G:\CODEX\New Manga\doc\tasks\P22.md，SHA-256=5391FE776ECDBA99918B4C0441CC6EBEBB5609028E08298D4A19024F145F2E09。以它为任务范围和状态指令；该 Task 由 Codex 管理，严禁修改。
- Owner workspace：G:\CODEX\New Manga.worktrees\P22-roundtrip-serialization-antigravity；branch=agent/antigravity/P22-roundtrip-serialization。
- 只读起点：R7 HEAD=bcbe8632beea067047630c0bc94e6901ced72eda，tree=058cf0fed3cde0a1a77293ad404d46b4c6b331d5；待修文件 verification/P22/antigravity-owner-p22.handoff.md，SHA-256=D1D0C3F9A683A80426DE4C5111722F617E5CDEC7F57FD40F3732F8DA4AC31ECC。
- 非作者 DSH R7 内容 Review=APPROVED_WITH_CONDITIONS（P0/P1/P2/P3=0/0/0/1）；R7-1 是非阻断 P3：R5/R6 report/adjudication 的路径被写成 verification/P22/...，但这些四个文件实际在主仓 G:\CODEX\New Manga\verification\P22，而 R7 Handoff 声明的 workspace 是 Owner worktree。DSH 正式 object_binding=NOT_VERIFIED。Codex adjudication 在主仓 verification/P22/codex-p22-r7-review-adjudication.md。

## 唯一写入范围与交付

只修改 Owner worktree 内的 verification/P22/antigravity-owner-p22.handoff.md。明确区分：

1. Owner 工作区是 G:\CODEX\New Manga.worktrees\P22-roundtrip-serialization-antigravity。
2. R5/R6 DSH reports 与 Codex adjudications 保存在主仓 G:\CODEX\New Manga\verification\P22，不在 Owner worktree。把这四个来源路径改成显式主仓绝对路径，或在其前加清晰的主仓 evidence-root 声明，确保转发者不会在 Owner worktree 中寻找。
3. 保留所有已有 report/adjudication 文件名、SHA、Review 结论、Gate 内容与范围；不改其他链接根，除非它们也被确认引用上述主仓文件。

完成后基于当前 HEAD 提交一个 R8 文档 commit。验收：该 commit 的唯一 changed path 是上述 Handoff；`git diff --check R7..R8` exit=0；既有 untracked 文件不变；Handoff 中可直接区分两个根。记录 R8 commit/tree/parent、修改文件 SHA、diff 路径与 diff-check 结果，并给出简短 Handoff。

不要修改代码、测试、Task、Plan、STATUS、合同、Gate 或其他文件；不运行测试、Cargo、build、Tauri、sidecar、Sandbox 或产品 runtime。不要声称 AC2 runtime 或 P22 集成通过。P02 Build Gate 仍 BLOCKED，Hard Build Barrier 仍 EFFECTIVE，P22 Cargo/runtime=`BLOCKED / NOT_RUN`。如工作区不匹配固定起点、发现未提交 tracked 变更或无法安全完成，停止并只报告证据。
