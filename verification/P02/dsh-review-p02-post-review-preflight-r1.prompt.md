请对本地仓库当前 HEAD=d92c405304cb88712cb8777d8ec59618f4806df7（tree=e49a8842f351edebaaacda60e1a6727aabf9996f）执行只读、独立的 P02 证据与文档 Review。该提交父提交 D20=915566a96b7cdd1b294952127b7b7e2550ba117a；main/base=D19=1d5845e2b185179d7b683e5279f6520fc0882d97。当前目录是 detached reviewer worktree，HEAD 必须保持不变。

请检查 candidate 相对 main/base 的实际 diff、doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/00_INDEX.md、doc/tasks/P02.md、verification/P02/codex-checkpoint-p02-post-review-preflight-blocked-r1.md、post-review-preflight 的 JSON/log/exit、route/diffcheck r2 artifacts。Review 范围为 P02 状态与 fresh preflight evidence，禁止修改任何文件、提交或切换 HEAD。不要访问或读取 main root 的其他脏文件；不要读取 manifest 列出的无关用户文件。不要执行 HostFolder recheck、host inventory、Windows Feature 查询、wsb start、guest command、build、Cargo/Tauri、Vitest、GUI 或产品测试。允许只读 git/show/diff、读取候选报告与验证其内部一致性。

重点判断：
1. 实际路径变更是否全部处于本次冻结的 doc/00_INDEX.md、doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/tasks/P02.md、verification/P02/** 范围；是否意外改产品源码/接口/依赖。
2. D16 exact SHA 是否正确为 999e6adfc229698344c0cbf9bfb6d636fe73fb7c，D16 tree、R5 DSH review 与 integration statements 是否一致。
3. fresh evidence 是否支持 R2 11/11 PASS、filesystem 12/12 roots / 20/20 hashes / 14/14 registered sizes / 3/3 EOL pins / 3/3 hardlinks；是否把未注册 size 说成已核验。
4. Host/WSB 报告是否准确将 10/11 作为通过、唯一 Windows Sandbox Feature query 标为 UNKNOWN（非提权 EXIT=1 / COMException），并正确 fail-closed：未执行 wsb start、build 或产品验收；Hard Build Barrier 仍 EFFECTIVE。方案 Review、Smoke admission、Build Gate、产品验收不可混为一谈。
5. root protection 报告是否精确陈述 203/203 对照及 0 overlap；报告与主线基线、当前保护约束是否一致。不要读取被保护用户文件。
6. route-r2 是否确实记录 fixed D20 HEAD 的 verify_plan.py 7/7 PASS；diffcheck-r2 是否对应 D20 HEAD 的 commit whitespace check EXIT=0。检查 checkpoint 和当前状态文字无陈旧或相互矛盾状态。
7. Reports 是否意外泄漏用户名/SID、完整应用路径、无关应用窗口标题或其他不必要隐私。

输出简体中文，格式：
- Verdict: APPROVED 或 CHANGES_REQUESTED
- 审查 HEAD/base
- 检查矩阵（PASS/FAIL/NOT_RUN）
- Findings（每项 severity、路径/行号、问题与最小修复；无问题写“无”）
- 是否允许将此 evidence/docs candidate fast-forward 集成到 main。
只有在所有关键项均有充分证据且无 P0/P1/P2 finding 时才能 APPROVED。不要声称未运行的操作 PASS。
