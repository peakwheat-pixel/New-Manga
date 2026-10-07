---
task_id: M2-DERIVED-GC-2-DESIGN
author: Codex
recipient: DeepSeek Harness / Codex Integrator
base_commit: ab4b7c110a7c828f20d2d0787bd71144336d2e44
delivery_head: be779967fc3baab3a174b7ba3a4c47eed6e0fc2f
status: awaiting_independent_recheck
---

# 修订设计 Handoff

原设计 delivery=8dd88c56，其 Handoff 到4a930c61入库；首轮DSH固定4a930c61 approve_with_conditions。修订delivery=be779967，当前Handoff/验证日志在后续metadata commit入库；Review必须使用包含本Handoff的实际新HEAD，不把delivery声称包含后写文件。

工作区 G:/CODEX/New Manga.worktrees/DERIVED-GC-2-DESIGN，branch=codex/m2-derived-gc-2-design。实际修改仍只有设计/正式Task/原报告导入/verification；不改 src/apps/tests、任何生产Schema/wire/依赖/用户文件。

修订点与C1-C5/F06-F07逐项对应见 verification/M2-DERIVED-GC-2-DESIGN/review-disposition.md；包含derived删除域租约+catalog单行namespace、全部现有store入口保护、源路径精确绑定、复用native helper、人工修改保留、core.ping启动deadline。退役复用旧revoke请求内部位，SQLite零busy等待/零重试、异常非致命；不增第二同步RPC。设计不承诺磁盘有界或在线回收。

AC1-AC3设计取证/矩阵/生命周期已给出；AC4实际后继恢复点将在设计集成后创建并填写proposed Task，未启动；AC5文档检查EXIT=0，DSH r2/集成尚待执行。design-check-r2.log绑定be779967执行后的修订树；运行/native/产品测试NOT_RUN，无产品PASS口径。

下一接收者=DSH：仅新固定head上复核C1-C5与新增安全补强，返回真实Architecture/Verification及逐项disposition。通过后Codex串行merge并文档检查，回填done与integration_commit，创建proposed M2-DERIVED-GC-2实际worktree/base/allowed_paths和指令二。Owner=ZCode、Reviewer=DSH、Integrator=Codex；G1-G7保持，G7不足则禁用两个sweep/BLOCKED。后继完整转发指令在 verification/M2-DERIVED-GC-2-DESIGN/next-task-instruction.md（待集成后创建），本Handoff不授权开工。
