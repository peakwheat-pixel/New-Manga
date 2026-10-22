# P22 R9 Handoff-only 修订任务

请在已存在的 P22 Owner worktree 中，基于固定 R8 提交完成一次最小 Handoff 文本修订。此任务由 Codex 授权，范围仅限下列单个文件和一个标题行。

## 固定依据

- P22 Task 快照：`G:\CODEX\New Manga\doc\tasks\P22.md`，SHA-256=`3883A3093ABBF4866D9057882331503C1A17F075608C80614C327448AD7367BE`。
- Codex R8 Review adjudication：`G:\CODEX\New Manga\verification\P22\codex-p22-r8-review-adjudication.md`，SHA-256=`8C40E942AA788D665A9E6F4A2A3565B97C611D07E0C5D3ACE658904CA102F5AD`。
- Owner worktree：`G:\CODEX\New Manga.worktrees\P22-roundtrip-serialization-antigravity`。
- branch：`agent/antigravity/P22-roundtrip-serialization`。
- 必须从 R8 HEAD=`a99d092fbf0fe71079f17d6510ad697c547a3fa2`（tree=`417ae9572399e584dce8f237ab9622db3a57bc2d`）继续；不得从 R7 或更早基线开始，以免丢失 R8 已完成的证据根澄清。
- R8 Handoff=`verification/P22/antigravity-owner-p22.handoff.md`，当前 SHA-256=`248D267C1407C894A62BA4C52F19584C6CA0EFEA9DECC8B26DB17AC7C49DD9BA`。

## 唯一写入范围与修改

只修改 `verification/P22/antigravity-owner-p22.handoff.md` 第 252 行的标题。将：

`- Owner Worktree 相对文档：`

改成能无歧义固定其根目录的标题，明确写出：

`G:\CODEX\New Manga.worktrees\P22-roundtrip-serialization-antigravity`

并说明下方相对路径均以该 Owner worktree 根解析。保留下方清单及全部其他 Handoff 内容不变；不要改代码、测试、Task、主仓证据、Gate 或其他文件。

## 交付

- 固定一个以 R8 为 parent 的新 commit；报告 commit、tree、parent、Handoff SHA 和 `R8..HEAD` changed path。
- 对目标单文件执行 `git diff --check R8..HEAD` 并报告退出码。
- 报告 worktree tracked/untracked 状态，不清理、覆盖、移动或删除任何既有 untracked 文件。
- 不运行 Cargo、build、测试、Tauri、sidecar、产品 runtime、Sandbox、OS measurement、Windows API、profile/ACL/registry 操作。
- 不宣称 P22 完成、集成批准或任何 Gate PASS；Cargo/runtime/AC2 继续 `BLOCKED / NOT_RUN`，P02 Hard Build Barrier 继续 `EFFECTIVE`。
