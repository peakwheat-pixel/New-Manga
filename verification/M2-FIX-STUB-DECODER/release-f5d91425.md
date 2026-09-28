# M2-FIX-STUB-DECODER Release Evidence — release base `f5d91425`

- 日期:2026-09-29 01:2x Asia/Shanghai(编排会话,Goal G2 持续推进)
- 释放裁决:Codex(代行,ZCode 会话,用户授权 2026-09-28);依据=已登记候选(M2-AC2 集成遗留)+GOAL G2 优先级(三个 FIX 候选中范围最小、无契约/schema 冲击者先走;M2-FIX-EXPORT-LINEAGE 与 M2-FIX-LISTBOOKS-PAGECOUNT-UNKNOWN 涉及 schema migration/IPC 破坏性变更,留后续冻结)。**代理裁决,用户可撤销。**
- Task:[M2-FIX-STUB-DECODER](../../doc/tasks/M2-FIX-STUB-DECODER.md) core_service stub decoder signature fix
- kind=fix(产品代码最小修复):base=`f5d91425`(M2-AC4 收口 commit)
- branch=`agent/zcode/M2-FIX-STUB-DECODER`;worktree=`G:/CODEX/New Manga.worktrees/M2-FIX-STUB-DECODER-zcode`(从 release commit 检出)
- Owner=ZCode(子 agent 代行实现);非作者 Reviewer=DeepSeek Harness;Integrator=Codex(另一子 agent,保持 Owner≠Integrator)
- 缺陷锚点(起草复核):`src/bootstrap/core_service.py:51-54`(`format=` 多余 + `mime_type` 缺失)、`src/application/importing/images/ports.py:11-16`(真实契约)
- 硬前置承诺:未来 core_service 扩 ImportPages 类命令前本修复必须已集成
