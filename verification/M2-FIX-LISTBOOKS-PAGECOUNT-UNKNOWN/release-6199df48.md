# M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN Release Evidence — release base `6199df48`

- 日期:2026-09-29 02:3x Asia/Shanghai(编排会话,Goal G2 持续推进)
- 释放裁决:Codex(代行,ZCode 会话,用户授权 2026-09-28);依据=M2-AC4 F-2 缺陷(最后一个 xfail,修复后 m2_acceptance 全绿)+GOAL G2。**代理裁决,用户可撤销。**
- 释放时冻结(代理裁决,用户可撤销):
  - **None 通道**:Python `int | None` / Rust `Option<u32>` / TS `number | null`;无合格页书(SQL 无行)→None;**SQL 数出的 0 不改 None**(硬约束,单测锁定 0/null 可区分)
  - **契约修订授权**:ListBooks DTO widened 属本 Task 目的,命令面清单不变;契约文档最小修订+修订记录
  - 三层验证义务:pytest / cargo / vitest-tsc 各自留痕
- Task:[M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN](../../doc/tasks/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN.md);base=`6199df48`(EXPORT-LINEAGE 收口 commit)
- branch=`agent/zcode/M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN`;worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-LISTBOOKS-zcode`(从 release commit 检出)
- Owner=ZCode(子 agent 代行实现);非作者 Reviewer=DeepSeek Harness;Integrator=Codex(另一子 agent,保持 Owner≠Integrator)
- 核心验收=F-2 xfail 移除转 PASS(先红留痕;预期回归 35 passed 0 xfailed)+known-0 通道单测+契约/副本同步
