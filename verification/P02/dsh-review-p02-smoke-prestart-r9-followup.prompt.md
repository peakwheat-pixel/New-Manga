角色：P02 的独立非作者 Reviewer（DeepSeek Harness）。本轮作者为 Codex；请独立判断，不预设通过。

任务：对 P02 R9 follow-up 文档证据修复进行 exact-head Review，验证 R9 Review 的 P3-1 和 P3-2 已关闭，并检查是否有新问题。
Review base=`8b91c8bf032fce3db50bd5a89d5122bf461f0cb2`
固定 Delivery HEAD=`5fe19efbedf6d46407c92fa7b73897e6794863e2`
固定 Delivery tree=`68dfa537a7cb6da99a7e954b6c5f734dd334488d`
branch=`codex/P02-process-isolation`；worktree=`C:\Users\49745\.codex\worktrees\p02-process-isolation-plan\New Manga`。

先核实 `git rev-parse HEAD` 与 `git rev-parse 'HEAD^{tree}'` 精确匹配；结论只针对该固定 commit。使用 `git diff base..HEAD`、`git show HEAD:path` 阅读已提交内容。当前 worktree 含历史 untracked 日志与本 prompt/checkpoint；不得把任何 untracked 文件当作候选交付内容，也不要读取 DSH stderr。

预期修复：
1. `verification/P02/codex-checkpoint-p02-smoke-prestart-r8-candidate.md` 保留 R8 hash=`4d374260f81ff5868da11a577823b31bb576f6eb8e67414d79235d5f14c679ff`，并明确它对应 R8 fixed Delivery HEAD `6be3dfdb1911a358ac779e1398437b0411bf2cfa` 的 checker snapshot；R9 新 checker SHA=`1bcbc836b07ba76627816a63206e1dde846201872f6df32d265684abb3020af8` 应与 R9 artifact validator R6 / self-test R5 evidence 一致绑定。确认旧 hash 可由相应 Git object 重现，避免把历史数值误写成当前值。
2. `verification/P02/codex-smoke-prestart-manifest-r2-errata.md` 与 `codex-checkpoint-p02-smoke-prestart-r2-delivery.md` 的 current/latest citation 统一指向 artifact validation R6 与 self-test R5，并说明 R5/R4 是 R8 时点的早期证据。
3. Task、Plan、Status、Index 与 follow-up checkpoint 中 R9 review decision、当前状态和 product Gates 自洽；不得把 `NOT_RUN`、`BLOCKED` 或 `UNKNOWN` 写为 PASS。

安全边界：只读，不修改任何文件；禁止执行 `recheck` 或 scanner；禁止读取、枚举、扫描或哈希任何实际 HostFolder 内容；禁止启动 WSB/Sandbox、guest command、Build、runner/Vitest/GUI/WebView 或产品测试。可在环境允许时运行 artifact-only `python -B -X utf8 verification/P02/codex-smoke-prestart-manifest-check.py validate`、synthetic self-test、`python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`；只将实际运行并检查 exit 的命令写为已运行。

最终报告（简洁中文）：`decision: APPROVED | CHANGES_REQUESTED | NOT_VERIFIED | BLOCKED_BY_MISSING_EVIDENCE`；确认 HEAD/tree；P0/P1/P2/P3 counts；每个 finding 的稳定 ID、级别、精确路径/行号、影响、最小修复；列出实际运行与未运行项。无发现写 `findings: none`，保留未验证的宿主/运行时限制。
