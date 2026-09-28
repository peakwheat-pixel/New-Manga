# M2-AC4 Release Evidence — release base `a5529181`

- 日期:2026-09-28 23:5x Asia/Shanghai(编排会话,Goal G2)
- 释放裁决:Codex(代行,ZCode 会话,用户授权 2026-09-28);依据 REBASELINE_PLAN M2 Acceptance Backlog 第 4 行 + GOAL G2 优先级(M2-AC3 done 后主链下一项)。**代理裁决,用户可撤销。**
- Task:[M2-AC4](../../doc/tasks/M2-AC4.md) Reader Export Lineage + Library Page-count/Unknown Semantics Acceptance
- kind=acceptance,纯验收产品代码零改动;base=`a5529181`(释放 commit 父,= M2-AC3 收口 commit)
- branch=`agent/zcode/M2-AC4-reader-lineage-library-pagecount`;worktree=`G:/CODEX/New Manga.worktrees/M2-AC4-zcode`(从 release commit 检出)
- Owner=ZCode(子 agent 代行实现);非作者 Reviewer=DeepSeek Harness;Integrator=Codex(另一子 agent,保持 Owner≠Integrator)
- 释放时 main HEAD:`a5529181`;分叉基线干净(Owner worktree 创建后核验)
- AC 锚点起草核对:`export/service.py:216/152/88-95/159-170/248-290/297-301`、`core_service.py:115/150/160/167`、`reading/service.py:199`(详见 Task 文件锚点节)
- 预期评审关注:AC4 对 `page_counts.get(book_id, 0)` 默认值的 unknown 语义张力(PASS/FAIL 均为合法交付)

## 前置核验(释放时点)

- M2-AC3 done @`cac37485`(DSH r1 approved_with_conditions,C1-C5 关闭,复跑 23 passed EXIT=0)
- 收口 commit=`a5529181`;工作区除历史遗留未提交改动(frontend/permissions/M2-RC2,归原作者)外干净
