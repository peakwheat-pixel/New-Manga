# M2-FIX-EXPORT-LINEAGE Release Evidence — release base `8b0d9040`

- 日期:2026-09-29 02:1x Asia/Shanghai(编排会话,Goal G2 持续推进)
- 释放裁决:Codex(代行,ZCode 会话,用户授权 2026-09-28);依据=M2-AC4 F-1 缺陷(刚闭环验收的 FAIL 证据,修复价值最高)+GOAL G2 优先级。**代理裁决,用户可撤销。**
- 释放时冻结(代理裁决,用户可撤销):
  - **方案 A**(scope_snapshot_json 加 included_stale/missing ids 键),不动 schema.py;发现必须动 schema 即停,不得擅自升级方案 B
  - **per-page revision 拆出本 Task**(未来独立候选,登记留 planning)
  - **P3-7 并发 write 不同期修**(只评估留痕)
- Task:[M2-FIX-EXPORT-LINEAGE](../../doc/tasks/M2-FIX-EXPORT-LINEAGE.md);base=`8b0d9040`(M2-FIX-STUB-DECODER 收口 commit)
- branch=`agent/zcode/M2-FIX-EXPORT-LINEAGE`;worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-EXPORT-LINEAGE-zcode`(从 release commit 检出)
- Owner=ZCode(子 agent 代行实现);非作者 Reviewer=DeepSeek Harness;Integrator=Codex(另一子 agent,保持 Owner≠Integrator)
- 核心验收=移除 F-1 xfail 转 PASS(33 passed+1 xfailed 预期)+legacy 前向兼容断言;M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN 保持 proposed
