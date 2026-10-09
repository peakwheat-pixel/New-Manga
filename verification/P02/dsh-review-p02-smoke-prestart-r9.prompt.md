角色：P02 的独立非作者 Reviewer（DeepSeek Harness）。本轮作者为 Codex；请独立判断，不预设通过。

任务：审查 P02 R9 Smoke pre-start evidence correction，确认 R8 的 P2-A、P2-B、P3-C、P3-D、P3-E、P3-F 是否充分处置，并检查本轮新增问题。
Review base=`6be3dfdb1911a358ac779e1398437b0411bf2cfa`
固定 Delivery HEAD=`8b91c8bf032fce3db50bd5a89d5122bf461f0cb2`
固定 Delivery tree=`586902273c98399c4737a8f801f0ddfff11408d8`
branch=`codex/P02-process-isolation`；worktree=`C:\Users\49745\.codex\worktrees\p02-process-isolation-plan\New Manga`。

先验证 `git rev-parse HEAD` 与 `git rev-parse 'HEAD^{tree}'` 精确匹配；只对固定 commit 作结论。请从 `git diff base..HEAD` 与 `git show HEAD:path` 阅读已提交内容。当前 worktree 有前几轮保留的 untracked DSH/验证日志；不要把任何 untracked 文件当作候选交付内容，也不要读取 DSH stderr。

R8 finding 的预期修复：
- P2-A：修正 errata、delivery checkpoint、P02 Task 中指向未提交 R3/R4 日志的引用，改为当时已提交证据。
- P2-B：修正 R1 标记描述，准确区分 README 的 `NOT_GATE_EVIDENCE` 与脚本头部的 `INVALID_PARTIAL_HISTORY`。
- P3-C：在 INDEX 恢复 gate 状态摘要。
- P3-D：明确 Stage-1 12-root inventory 只检查 root existence/root-level reparse；R2 Smoke manifest 的 11 个映射才递归，6 个 toolchain mappings 为 metadata-only。
- P3-E：manifest checker 改用 context manager 关闭被读取文件。
- P3-F：synthetic self-test 增加 hash/count/status/issues mismatch 并确认 fail closed。

范围：仅 documentation / verification。重点检查 `doc/00_INDEX.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P02.md`、R2 delivery checkpoint、R2 errata、manifest checker 与 self-test，以及已提交的 R8/R9 报告、checkpoint 和验证日志。

安全边界：只读，不修改任何文件；禁止执行 `recheck` 或 scanner；禁止读取、枚举、扫描或哈希任何实际 HostFolder 内容；禁止启动 WSB/Sandbox、guest command、Build、runner/Vitest/GUI/WebView 或产品测试。允许执行 artifact-only `python -B -X utf8 verification/P02/codex-smoke-prestart-manifest-check.py validate`，以及 `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`（若环境可用）；准确区分实际执行与静态检查。如果命令因环境限制失败，标为 `NOT_VERIFIED`，不得推断通过。

最终报告（简洁中文）：`decision: APPROVED | CHANGES_REQUESTED | NOT_VERIFIED | BLOCKED_BY_MISSING_EVIDENCE`；确认 HEAD/tree；P0/P1/P2/P3 counts；每个 finding 的稳定 ID、级别、精确路径/行号、影响、最小修复；列出实际运行与未运行项。没有发现时写 `findings: none`，并保留尚未验证的宿主/运行时限制。不得把 `NOT_RUN`、`BLOCKED` 或 `UNKNOWN` 写成 PASS。
