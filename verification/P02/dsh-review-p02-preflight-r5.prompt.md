请对 P02 Codex-only isolation 子任务做独立、只读、exact-head Review。Reviewer=DeepSeek Harness；Owner/author=Codex；Integrator=Codex。

固定审查对象：
- HEAD: 844aec282416111310d9a9efcac5bc9e0c6eb451
- tree: 79ec85adc5aabcd3e93d6a7d08bb8986fdfed16b
- base: 92dc7361194f1db8fdf7aff3a15a3d234ae56678
- Review checkout: C:/Users/49745/.codex/worktrees/P02-preflight-r5-844aec28-review-dsh
- review branch: review/deepseek/P02-preflight-r5-844aec28

请从这个 checkout 直接读取并核对：
1. doc/STATUS.md、doc/REBASELINE_PLAN.md、doc/00_INDEX.md、doc/tasks/P02.md 的当前 P02 段落；
2. verification/P02/codex-scratch-build-preflight-r3.md、codex-scratch-build-preflight-observations-r3.json、codex-preflight-r5-validation.md、codex-checkpoint-p02-preflight-r5-start.md；
3. R10 DSH response、erratum、condition-review checkpoint，以及 frozen HostFolder/input TSV、R3 Sandbox config 和 root-start manifest；
4. base 到 HEAD 的完整差量、exact path set、用户 root-protection/hash evidence。

Review 问题：
- R10 APPROVED 与 erratum 是否准确闭合 R9 C-01..C-06、纠正报告计数并撤回 O-3；R5 current authorization traceability 与 O-1/O-2 闭合是否有证据。
- observations R3 是否准确对应 frozen TSV，20/20 input SHA-256、14/14 registered sizes、6 null size comparisons、12/12 HostFolder root rows、source/EOL pins、r3 XML bytes/hash/mapping count、CIM/WSB values、RAM/disk thresholds、root manifest live match 与 zero candidate overlap。
- 记录中的聚合器纠正是否透明且不改变实测值；是否把 InstallState=1 或 Stage-1 PASS 越界表述成隔离、Smoke PASS、Build PASS 或产品验收。
- 23-path candidate 是否严格限定在四个已授权当前状态文档段和 verification/P02/**，没有改变 AC、Owner allowlist、依赖图、产品代码/测试、共享契约或 Task 状态。
- 每个当前状态和恢复指针是否相互一致；P02 仍 ACTIVE，完整 preflight BLOCKED / INCOMPLETE，Smoke NOT_ADMITTED，Build Gate BLOCKED，build NOT_AUTHORIZED / NOT_RUN，AC1–AC7 BLOCKED / NOT_RUN，Hard Build Barrier 有效。

Review 限制：
- 只读固定 HEAD，不改文件，不切换到其他 commit，不运行 Sandbox、Smoke、build、runner、Vitest、GUI 或产品测试。
- 若命令/检查无法执行，明确写 NOT_RUN/UNKNOWN，不推断 PASS。
- 不要把此 Review 当作 Smoke admission；只判断 R5 候选是否可由 Codex 进入单独的 admission Gate。

请返回正式结构化报告：reviewed HEAD/tree/base、decision、P0/P1/P2/P3 数量与 finding IDs、逐项证据位置（文件和行号）、精确 next action，以及是否存在阻止 Codex 记录独立 Smoke admission 的 finding。请独立判断，不因 Codex 的验证记录而默认通过。