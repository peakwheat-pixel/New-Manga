# DSH 独立 Review：P02 current prestart R4

角色：独立、只读 Reviewer；你没有编写本轮修复。当前 detached review worktree HEAD 是本次 review target。先报告完整 `git rev-parse HEAD` 与 `git rev-parse 'HEAD^{tree}'`，确认 expected base=`4183e7f7cf366c27aa8ad8a0bc7300af48783470`。如果无法固定 HEAD/tree 或完整差异不是允许的 P02 文档/证据范围，停止并返回 `BLOCKED`。

先阅读 `AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/00_INDEX.md`、`doc/09_COLLABORATION.md`、`doc/tasks/P02.md`、`verification/P02/codex-checkpoint-p02-smoke-prestart-r3-review.md`、`verification/P02/codex-checkpoint-p02-smoke-prestart-r3-followup-delivery.md` 与 `verification/P02/dsh-review-p02-current-prestart-r3.response.md`。审查从 expected base 到当前 exact HEAD 的完整 diff。

## 必查 R3-01 修复

1. `P02-PRESTART-R3-01`：在 `codex-checkpoint-p02-smoke-prestart-r2-followup-delivery.md`、`doc/tasks/P02.md`、`codex-checkpoint-p02-smoke-prestart-review-dispatch-r3.md` 中，D6 的 66 路径计数是否明确只绑定 D6，不会被理解为后续 review package 的范围。
2. 核对三次计数的绑定证据：D6=`3a16570b306081d1f3c52a90f80fe80406a40c98` / tree=`65a5f62fcd2542c6e8efb0c1e75fb263764162bd` / 66 paths；D7 R3 package=`322526fcde650ea9dcfde4a14f828afeb8808ead` / tree=`0298f62f29bd0c6c4a737255a7f857adb168b9af` / 80 paths；D8=`5bdda66889dc4a5b2ad20b1500fbf6487c774ed0` / tree=`1dbf74dd54bdc7a29c825d82e1df33f9cec98626` / 84 paths。D6 `r4.*` logs must bind to D6; D8 `r5.*` logs must bind to D8; neither log set can substitute for the current package's scope check.
3. Independently measure the current package's full base-to-HEAD path count and out-of-scope count; confirm all three historical counts are accurately labeled.

Also recheck R2-01 closure (blank line between current STATUS and r6 history), dated/current Plan wording and P05 status alignment, R1-01/R1-02 closure, allowed paths (`doc/00_INDEX.md`, `doc/REBASELINE_PLAN.md`, `doc/STATUS.md`, `doc/tasks/P02.md`, `verification/P02/**`), P02 as the only active Task, historical treatment of the old 04:11 measurement, one-attempt Smoke limit and Review-after immediate-check rule. No Smoke, Build, AC, or Hard Build Barrier success may be claimed without evidence.

In the detached worktree, independently execute and report exit codes:

- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`
- `git diff 4183e7f7cf366c27aa8ad8a0bc7300af48783470 HEAD --check`
- `git diff HEAD^ HEAD --check`
- complete `git diff --name-only 4183e7f7cf366c27aa8ad8a0bc7300af48783470 HEAD` scope review.

Do not modify files. Do not access, scan, list, or hash HostFolder contents. Do not run `wsb start`, Sandbox/guest commands, Build, GUI, or product tests. Do not read any DSH `*.stderr.txt` file. Mark unsupported evidence `NOT_RUN`, `BLOCKED`, or `UNKNOWN`, never `PASS`.

## Report format

- Decision: `APPROVED`, `CHANGES_REQUESTED`, or `BLOCKED`.
- Exact HEAD/tree, expected base, command exit codes, full diff path count and out-of-scope count.
- P0/P1/P2/P3 counts and open count; each finding with ID, severity, file/line, impact and minimal fix. If none, state `0/0/0/0`, `open=0`.
- Review coverage and `NOT_RUN` / `BLOCKED` / `UNKNOWN` items.
- Explicitly confirm no Sandbox, HostFolder scan/hash, Build, GUI or product tests were run.
