# DSH r5 exact-head Review dispatch

- Agent/role: DeepSeek Harness；非作者独立 Reviewer。
- CLI: `dsh 0.2.0-rc.2 --profile headless --json -`；dispatch skill=`C:/Users/49745/.agents/skills/dsh-dispatch/SKILL.md`。
- Base=`fb0a7668d948ae68f15fd59aaffd6aedf6663c99`；candidate=`1c7efb172b8e9d766e38f84cf3728a90bb5953d0`；tree=`f50f9716a87ffe7a6272370a92b0eeb862e75079`；parent=base。
- Reviewer checkout=`C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r5`，detached exact candidate，审查前后 clean。
- Prompt=`verification/P02/dsh-review-process-isolation-r5.prompt.md`；命令=`dsh --profile headless --json -`。
- Session=`session-e94ff6f7-0701-4dc2-955d-018c373ebe79`；CLI exit=0；stderr bytes=0。
- Raw JSONL 位于 checkout 外 `C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/dsh-review-logs/dsh-review-process-isolation-r5.stdout.jsonl`；bytes=`269485`；SHA-256=`f9b4a9ad2f270fe1774e3892b12b627bed708f79b344ef9bf2c94b4c775b19f9`；含 thinking events，未入库。
- Last reported usage event: inputTokens=`3455`，outputTokens=`6631`，cacheReadTokens=`113664`，totalTokens=`123750`（按 CLI 字段原样记录，不跨 event 相加）。
- Decision=`APPROVED_WITH_CONDITIONS`（仅设计）；P0/P1/P2/P3=`0/0/0/2`。N-01..N-03 closed；N-04、N-05 为两项新 P3 条件，待纯文档修订与复审。
