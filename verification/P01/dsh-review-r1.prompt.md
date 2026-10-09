请作为 P01 的非作者独立 Reviewer，执行正式只读 Review。不要修改任何文件，不要自行集成。仓库工作目录是当前 P01 worktree。

固定依据：Task=`P01`，base=`826bea12a132c5af2ac0cd1244d00e9170093c71`，必须只评审 reviewed_head=`6f24006c21281df485375674d20a1d3b7b48ca63`。确认 `git rev-parse HEAD` 与该 SHA 完全相同，branch 为 `agent/codex/P01-metadata-audit`，且没有检出其他head。审查差量为 `base..reviewed_head`；不得把其他未提交/外部文件算入候选。

先读 `AGENTS.md`、`doc/09_COLLABORATION.md`、`doc/REBASELINE_PLAN.md`、`doc/STATUS.md`、`doc/tasks/P01.md`、`doc/handoffs/P01-9b124936.md`、`verification/P01/RESUME.md`、`verification/P01/metadata-audit.md`、`verification/P01/ac7-preflight.log`、`verification/P01/ac7-candidate-check.log`、`verification/PROJECT-ROADMAP-20261008/verify_plan.py`。再读取 base 与 candidate 的 Git diff 和全部受影响文件。

按 P01 AC1–AC7 独立核对：
1. AC1：branch/base/worktree/recovery事实与root已有24项dirty保护记录是否一致；不得声称检查过未实际查看的内容。
2. AC2：GC2 `integration_commit` 仅在实际merge、祖先、Task/Handoff/Review链证据充分时修正；来源Task其他字段与状态无额外变化。
3. AC3：DETECT3旧值对象无效，候选实际merge、祖先、Handoff与集成证据相符；来源Task其他字段与状态无额外变化。
4. AC4：ANNOTATE-R2证据不足是否准确标为 `NOT_VERIFIED`，没有把Owner报告、摘要或别轮Review冒充独立载体，也没有推断Review从未发生。
5. AC5：SYNTH重复integration字段修正是否有Git集成证据；`status: in_review`、Review缺失和人工登录要求是否原样保留，Plan/Task冲突有无准确记录。
6. AC6：是否保留R2 challenge空集/T2是否释放的用户裁决，是否未代用户决定或冒充SYNTH人工冒烟通过。
7. AC7：Handoff是否包含可追溯实际delivery、允许路径、AC、证据和剩余Gate；Task/Plan/Status/导航/派生路线/校验器状态是否一致；fixed candidate paths是否都在P01 allowed paths；路线验证器辅助改动是否严格限Task scope note；有无产品代码、测试、Schema、依赖、用户数据或其他越界改动。注意DSH通道probe不是正式Review。

请执行或明确标记未能执行的验证：
- `git diff --name-only 826bea12a132c5af2ac0cd1244d00e9170093c71..6f24006c21281df485375674d20a1d3b7b48ca63`
- `git diff --check 826bea12a132c5af2ac0cd1244d00e9170093c71..6f24006c21281df485375674d20a1d3b7b48ca63`
- `python -B -X utf8 verification/PROJECT-ROADMAP-20261008/verify_plan.py`

输出一个简体中文Review报告，包含：reviewer、author、base_commit、reviewed_head、decision（`approved` / `changes_requested` / `blocked`）、Architecture结论、Verification表（实际命令/环境/exit或NOT_RUN）、按P0/P1/P2/P3列出的具体finding（没有时明确写“未发现问题”）、可否交Codex Integration Gate及限制。只报告实测事实；遇到关键证据无法确认时不要批准。产品pytest/cargo/vitest/GUI/build是否运行要以实际结果为准，不能把NOT_RUN写成PASS。