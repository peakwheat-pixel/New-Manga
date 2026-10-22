# P02PRE-R1G：处理 DeepSeek Harness Review findings

你是 P02PRE-R1G 原实现 Owner Antigravity。只在既有 worktree `C:\Users\49745\.codex\worktrees\p02pre-r1g\New Manga`、branch `agent/antigravity/P02PRE-R1G`、当前 delivery HEAD `9ec34a8847f625331c729306fd303bd5df09ab92` 继续修复你自己的实现。你不是 Reviewer；Codex 后续会独立 adjudicate，并安排新的非作者 Review。

只可写这三个已分配文件：
1. `verification/P02/p02pre-r1g-capture.ps1`
2. `verification/P02/p02pre-r1g-author-selfcheck-20261011.json`
3. `verification/P02/p02pre-r1g-antigravity-handoff-20261011.md`

修复依据：`G:\CODEX\New Manga\verification\P02\dsh-p02pre-r1g-review-20261011.stdout.md` 中最终 Review 报告的 R-001 至 R-008。逐项处理如下：

- R-001：将证据序列化失败、证据大小部分输出、证据写入失败与普通 inventory/query stop 机读地区分，保留底层 stopReason/细节；对无法写入 evidence JSON 的情况，明确只能由 stderr/runner evidence 证明，不要声称该类别已写入 JSON。
- R-002：Handoff 不得把 Codex-owned AC1 或未执行 self-check 的 AC3 写成 PASS。把 AC1–AC7 的 owner / 状态如实区分为作者已交付、Codex 待裁决、NOT_RUN、NOT_VERIFIED；特别是 parse/self-check 目前仍 NOT_RUN。
- R-003：若 protected hash 有任何失败，必须在发起 ACL stability re-query 前 fail-stop，同时仍保留现有安全的部分 evidence 序列化路径。为 ACL endpoint stability/re-query 加入真实 phase 状态（初始 NOT_REACHED；开始后 IN_PROGRESS；完整且无异常时 COMPLETED；发现漂移、query error 或 unverifiable 并以其停止时 FAILED），并确保 stop phase 不会报告为 COMPLETED。异常/失败后的 phase 字段须准确。
- R-005：Handoff front matter 的 `delivery_head` 应指当前包含交接文件的 delivery commit（本轮新提交完成后填写实际最终 HEAD），并把 implementation commit 作为单独字段保留。
- R-006：修正 Handoff 对 engine attestation 的描述：代码比较 executable path/version/edition/language mode 和 cmdlet availability；`psHome`、cmdlet source/version 是记录项，除非你确实增加了精确比较与相应测试，否则不要声称会断言它们。不要扩大本次工作到运行期预检。
- R-008：self-check `executionAttestation` 不得说完全未调用 child process，因为 Handoff 已记录只读 Git/Python 工具；措辞限定为未调用 capture/parser/host getter/profile/registry/ACL API/Build/Cargo/AC，并与本轮实际操作保持一致。

不要求你改 R-004 或 R-007：这是 Codex-owned 的 manifest/Task/pre-run pin 对齐，Codex 会单独处理。不要修改其他路径、manifest、Task、Plan/STATUS、主仓文件或 R1F 原件。

顺序与安全：
1. 先静态阅读 frozen review 的原文及相关行，再作最小修改。
2. 不运行候选 parser、自检、engine preflight、capture、host getter、任何 registry/ACL/profile API、Build/Cargo/AC；不调用 Windows Sandbox；不读取/查询 `.tmp.driveupload`。
3. 不要碰本机主仓中其他 dirty/untracked 文件，不 reset/clean/stash/覆盖/删除。
4. 完成后在本 worktree 以单独 commit 保存三文件变更，保留原实现 commit 历史；不合并主线。
5. 交付说明逐项列 R-001/R-002/R-003/R-005/R-006/R-008 的修改、R-004/R-007 留给 Codex、准确列出本轮命令和未运行项、提交 SHA 与三文件 bytes/SHA-256。不要自审或宣称 Review/Gate PASS。