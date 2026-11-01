# 真实生产 assembly 执行记录

- 唯一入口：src/bootstrap/core_assembly.py:assemble_core_services。
- 每个用例使用独立临时 data root，调用 assemble_core_services；返回对象中的真实 RegionStepWriter / ArtifactStepWriter 由生产 ProductionHandlers 持有；pipeline 由 src/infrastructure/pipeline/assembly.py:build_production_pipeline 组装。
- 真实执行链：PipelineService → ProductionStepExecutor → 生产 handler → prepare writer → SqliteTargetCatalog.commit_step → SQLite store。测试通过 mock local providers 产生 OCR/segment 输入；未替换 executor、catalog、pipeline。
- test_v7 在生产连接上设置 SQLite trace callback，并在独立 mode=ro + query_only=ON 连接中观察提交边界。
- test_v9 在生产 ManagedStorage 上追踪 publish 发生时事务仍打开、候选已 resolved，并检查数据库语句次序。
- V1–V9（V5、V6 各含两个参数/路径）共 **11 passed**；另有 R-ART-4 storage=None fail-closed 用例 **1 passed**，AC4 静态 prepare 写域边界 **2 passed**。V1–V9 过滤日志中的 1 deselected 就是单独运行的 storage=None 用例，不是未执行项。
- 原始证据：production-assembly-v1-v9.log、prepare-boundary-checks.log；汇总：v1-v9-summary.md。
