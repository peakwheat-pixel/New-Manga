# TASK-013：生产 Pipeline seam 设计记录

状态：APPROVED FOR IMPLEMENTATION（用户已授权）  
基线：`126bab54e03849d2684921a5d7fb211f7ad7c23b`  
Owner：Codex  
Reviewer：DeepSeek Harness（实现 head 固定后独立 Review）

## 范围

本切片只完成生产 Pipeline seam，不进行 R-1 入口装配。生产默认必须显式使用 SQLite 与生产执行器；测试仍可继续使用 TASK-011 的 InMemory/Deterministic double。

## 最小设计

1. 在 v2 之后追加 v3 migration，保存 Run/Target/Task/Step/Ref/Candidate、Page/Region stage state 及 Pipeline 默认快照配置。v1/v2 SQL 不改。
2. 新增 `SqliteTargetCatalog`：从真实 Book→Chapter→Page→Region 查询稳定叶子目标；以同一 SQLite 事务重读 Revision/Lock，提交 stage/current 更新。
3. 新增 `SqlitePipelineStore`：对 `PipelineRun` 做可恢复 round-trip，并将可查询的子对象同步到对应表。
4. 新增 `SqliteSnapshotProvider`：读取当前默认设置、Provider binding、Constraint snapshot ref、Context policy；只写脱敏快照，Run 自己保存冻结值。
5. 新增 `ProductionStepExecutor`：通过显式 handler registry 调用真实 provider seam；缺少 handler 返回 `PROVIDER_UNAVAILABLE`，不得生成 Deterministic 假结果。
6. 在 `PipelineService` 的状态边界调用现有 `PipelineStore.put`，确保 SQLite store 能看到 create/plan/step/control/recovery 的每个安全持久化点。
7. 提供生产 assembly helper，显式构造上述四个 adapter；`src/bootstrap/app.py` 不在本切片，留给后续 R-1。

## 非目标

- 不修改 `src/domain/**`、共享 Protocol、既有 v1/v2 语义、Schema/migration 之外的依赖、QML、bootstrap 或 R-1。
- 不实现 OCR/翻译/Inpaint 等尚未存在的 provider；没有 handler 时必须可观察地阻塞/失败。
- 不释放 TASK-015、TASK-030 或其他冻结 Task；不 push、不合并其他分支。

## 验收门槛

- v3 只追加表；v2 边界测试仍能证明 Pipeline 表不属于 v2。
- 真实 SQLite Book→Chapter→Page→Region 可 expand、current、Revision/Lock guard commit。
- Run 重启后可从 SQLite round-trip；`running` Run 可被 recovery 识别为 `interrupted`。
- 快照冻结可复现，数据库中不出现 Secret 字段值。
- 生产执行器无默认假输出；未知/未注册 provider 使用稳定错误码。
- Windows 默认 Qt（不设 offscreen）记录 `tests/pipeline`、`tests/storage`、`tests/workbench` 与全量测试，passed/skipped 分列并逐项写 skip 原因。
- Review 通过后才由 Codex 串行集成；集成完成后才能启动 R-1。
