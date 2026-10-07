---
task_id: M2-DERIVED-GC-2-DESIGN
author: Codex
recipient: DeepSeek Harness / Codex Integrator
base_commit: ab4b7c110a7c828f20d2d0787bd71144336d2e44
delivery_head: af09c00d6dea1beef50d4bb7c6c2ada74670073c
status: awaiting_independent_recheck
---

# r4 Handoff

r3@8557a3d4 changes_requested（1P2首次隔离库覆盖）；本次delivery=af09c00d。本Handoff/design-check-r4.log在随后metadata commit入库，复审采用其实际HEAD。工作区/分支同前。

设计§2.3/5/6/7冻结已有store窄初始化函数、trusted loader新fixture flag、首次initialize→seed→probe/ac1/AcceptanceBridge链；点名8个生产模块、main/library/core Rust seam、8个现成测试文件、两个packaged runner及两个dev verification driver（只fixture接线，历史报告/日志/发布流程不改）。Core负责G7受控产品迁移登记；新fixture登记不启GC、不回填来源、不删用户文件。A1-A4精度和所有URI/超时终止Drop策略已明确。

文档检查af09c00d EXIT=0；产品src/apps/tests/packaging/依赖及历史driver实际diff为零。native/回收/产品测试NOT_RUN。本Task未done、后继未创建/启动。请DSH仅新固定head上复核R3-01及上述新增段，真实结论原字节入库。通过后Codexmerge/检查/回填done，准备proposed M2-DERIVED-GC-2实际base/branch/worktree/allowed_paths和完整指令二，Owner=ZCode、Reviewer=DSH、Integrator=Codex，G1-G7不减。
