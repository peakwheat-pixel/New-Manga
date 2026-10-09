# DSH 独立 Review：P02 current prestart R2

角色：独立、只读 Reviewer；你没有编写本轮修复。当前 detached review worktree 的 HEAD 就是本次 review target。首先报告完整 `git rev-parse HEAD` 与 `git rev-parse 'HEAD^{tree}'`，并确认预期 base=`4183e7f7cf366c27aa8ad8a0bc7300af48783470`。若 HEAD/tree 无法确定、相对 base 的差异含非预期范围，或无法访问必要的已提交材料，停止并报告 `BLOCKED`。

先阅读仓库指令与事实源：`AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02.md`、`verification/P02/codex-checkpoint-p02-smoke-prestart-current-r1.md`、`verification/P02/codex-checkpoint-p02-smoke-prestart-r1-review.md`、`verification/P02/codex-checkpoint-p02-smoke-prestart-r2-repair-delivery.md`。审查从预期 base 到当前 exact HEAD 的完整 diff 及支撑证据，不只看本轮 commit 或摘要。

## 必须逐项复核 R1 finding closure

1. `P02-PRESTART-R1-01`（P2）：HostFolder delivery checkpoint 是否引用真实且已提交的 R2 stdout、精确 SHA-256、完成时间、空 stderr 与 exit=0；文件内容/记录的结果是否一致。
2. `P02-PRESTART-R1-02`（P3）：文档是否明确区分原 route/diff logs 的 D1 delivery 绑定、DSH 在 D2 review package 的独立复跑，以及后续日志各自的 exact HEAD；不得将旧日志说成当前 review HEAD 的验证。
3. `P02-PRESTART-R1-03`（P3）：`doc/STATUS.md` current 与 history 的段落分隔是否修复且旧 04:11 Stage-1 16/16 明确只是 clone 前历史观察。

另外检查：完整差异的路径都在允许范围 `doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md`、`verification/P02/**`；相关链接可解析；HostFolder、clone/source/EOL/hardlink/output-capability、阈值和 Sky/WSB 状态有已保存证据支持；P02 仍是唯一 active Task；没有把 Smoke、产品验收、Build Gate 或 Hard Build Barrier 写成通过；仅一次 Smoke 尝试限制与 Review 后立即重测要求仍清楚。

在此 detached worktree 中自行执行并报告结果：

- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`
- `git diff 4183e7f7cf366c27aa8ad8a0bc7300af48783470 HEAD --check`
- `git diff HEAD^ HEAD --check`
- 检查 `git diff --name-only 4183e7f7cf366c27aa8ad8a0bc7300af48783470 HEAD` 的完整路径范围。

不可修改任何文件；不可访问、扫描、列举或哈希 HostFolder 内容。不可运行 `wsb start`、任何 Sandbox/guest command、Build、GUI 或产品测试。不可读取仓库中任何 DSH `*.stderr.txt` 文件。若某项证据缺失或不确定，准确标为 `NOT_RUN`、`BLOCKED` 或 `UNKNOWN`，不能推断为 `PASS`。不得扩展到产品决策。

## 报告格式

- Decision：`APPROVED`、`CHANGES_REQUESTED` 或 `BLOCKED`。
- exact HEAD、tree、expected base，以及上述命令退出码。
- P0/P1/P2/P3 finding counts 与 open count。
- 每项 finding 的 ID、severity、文件与行号、触发条件/影响、最小修复；无 findings 时写 `0/0/0/0`、`open=0`。
- Review coverage、任何 `NOT_RUN` / `BLOCKED` / `UNKNOWN` 项。
- 明确确认未运行 Sandbox、HostFolder scan/hash、Build、GUI 或产品测试。
