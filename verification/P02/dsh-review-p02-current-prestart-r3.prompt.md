# DSH 独立 Review：P02 current prestart R3

角色：独立、只读 Reviewer；你没有编写本轮修复。当前 detached review worktree 的 HEAD 是本次 review target。先完整报告 `git rev-parse HEAD` 和 `git rev-parse 'HEAD^{tree}'`，并确认 expected base=`4183e7f7cf366c27aa8ad8a0bc7300af48783470`。若 HEAD/tree 无法确定、差异含非预期路径，或无法读取必要的已提交材料，停止并返回 `BLOCKED`。

先阅读 `AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02.md`，以及 `verification/P02/codex-checkpoint-p02-smoke-prestart-r2-review.md`、`verification/P02/codex-checkpoint-p02-smoke-prestart-r2-followup-delivery.md`、`verification/P02/dsh-review-p02-current-prestart-r2.response.md`。审查从 expected base 到当前 exact HEAD 的完整 diff 与相关已提交证据。

## 必查修复

1. `P02-PRESTART-R2-01`（P3）/原 R1-03：`doc/STATUS.md` current evidence 与前次 r6 history 之间现在是否存在独立段落空行，且历史内容、状态值未被改写或合并。
2. R2 非阻断观察：`doc/REBASELINE_PLAN.md` 是否将 2026-10-08 审计计数明确标为历史输入快照；当前 P01–P21 状态文字是否与表格和 `doc/STATUS.md` 一致（P05=`done`、P02=`in_progress / ACTIVE`、16 项 proposed）。
3. R1-02 后续绑定观察：`codex-checkpoint-p02-smoke-prestart-review-dispatch-r2.md` 是否明确说明 R3 日志绑定 D4 `a5557be49e1c2abd993814ddcc01a71ef1aa09cd` / tree `4e8157cd703393bcd3b42173fd44a77d30b21d16`，并且这些日志不声称验证 D5 或当前 package HEAD。
4. 重新确认 R1-01/R1-02 closure、完整差异路径仅为 `doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md` 与 `verification/P02/**`；P02 为唯一 active Task；旧 04:11 Stage-1 观察仍标为历史；Smoke/Build/AC/Hard Build Barrier 没有无证据 PASS；唯一一次 Smoke 限制及 Review 后即时重测要求仍明确。

在 detached worktree 自行执行并报告退出码：

- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`
- `git diff 4183e7f7cf366c27aa8ad8a0bc7300af48783470 HEAD --check`
- `git diff HEAD^ HEAD --check`
- 检查上述 base-to-HEAD 完整差异的路径范围。

不可修改任何文件；不可访问、扫描、列举或哈希 HostFolder 内容。不可运行 `wsb start`、任何 Sandbox/guest command、Build、GUI 或产品测试。不可读取任何 DSH `*.stderr.txt` 文件。没有证据的项目需标为 `NOT_RUN`、`BLOCKED` 或 `UNKNOWN`，不得推断为 `PASS`。不得扩大产品范围。

## 输出

- Decision：`APPROVED`、`CHANGES_REQUESTED` 或 `BLOCKED`。
- 完整 exact HEAD/tree、expected base、必跑命令退出码。
- P0/P1/P2/P3 finding counts 与 open count。
- 每个 finding 的 ID、severity、文件与行号、触发/影响、最小修复；若无 findings，写 `0/0/0/0`、`open=0`。
- Review coverage 与 `NOT_RUN` / `BLOCKED` / `UNKNOWN` 项。
- 明确确认没有运行 Sandbox、HostFolder scan/hash、Build、GUI 或产品测试。
