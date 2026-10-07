---
task_id: M2-DERIVED-GC-2-DESIGN
author: Codex
recipient: DeepSeek Harness / Codex Integrator
base_commit: ab4b7c110a7c828f20d2d0787bd71144336d2e44
delivery_head: 73e70536b9c5c3525607311892a44ec055805902
status: awaiting_independent_recheck
---

# r3 Handoff

设计 worktree/branch 未变。DSH r2@3a684675 changes_requested（1P2 R2-01），原报告原字节保留；修订delivery=73e70536，本Handoff与design-check-r3.log随后metadata commit入库，实际复审使用包含它们的固定HEAD。

只读bootstrap定位hint→关闭→取租约→业务连接重读绑定/identity→才初始化/服务；缺失/失配拒绝，loader/acceptance不需改文件。mark独立零busy连接、startup ping超时child/worker清理seam、WebView不透传退役位、已有测试入口名单均明确，详见review-disposition.md r2段。文档检查绑定73e70536 EXIT=0；src/apps/tests/Schema/依赖零改动，产品/native/回收NOT_RUN。

AC1-AC3取证与设计已给；AC4实际后继恢复点待设计集成后准备；AC5待r3批准与Codex集成，不提前done。下一步DSH限定复核R2-01及新增段；通过后Codexmerge/检查/回填done，准备proposed M2-DERIVED-GC-2给ZCode，G1-G7不减，不启动实现。完整next-task-instruction.md在集成后创建，actualbase/branch/worktree不得猜。
