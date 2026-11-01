# V1–V9 真实生产 assembly 结果

执行证据：production-assembly-v1-v9.log（PowerShell 7.6.8，EXIT=0，11 passed）；完整回归记录见 final-pytest-log.txt。新增测试全部经 assemble_core_services 构建真实 providers/writers，再经 build_production_pipeline 取得真实 PipelineService、SQLite catalog/store 与 ProductionStepExecutor。仅使用 R-SEAM-3 允许的 mock local providers；无 fake executor、InMemory catalog 或测试专用 pipeline。

| 验证 | 用例 | 结果 | 核验点 |
|---|---|---:|---|
| V1 | test_v1_revision_conflict_abandons_prepare_and_preserves_both_rows | PASS | revision 冲突后 region live 三值不变；prepared 行 abandoned 且同一步 pending 诊断行仍可区分。 |
| V2 | test_v2_lock_conflict_abandons_prepare_without_live_mutation | PASS | lock 冲突无 live mutation，prepared 行 abandoned。 |
| V3 | test_v3_stale_run_snapshot_rolls_back_live_region_writes | PASS | 注入 STALE_RUN_SNAPSHOT 后 live 写 rollback，候选 abandoned，service 返回 stale。 |
| V4 | test_v4_artifact_commit_failure_compensates_published_file | PASS | publish 后延迟 FK 失败触发事务 rollback、managed 文件补偿及候选 abandoned，无 artifact revision/孤儿文件。 |
| V5 | test_v5_pause_and_cancel_abandon_after_seam_rollback（pause、stop 两参数） | PASS（2 项） | BEGIN 后读取持久控制标志；rollback 后独立事务 abandoned；Run/Step 状态映射为 paused/interrupted 与 cancelled/cancelled。 |
| V6 | test_v6_restart_sweep_abandons_prepared_candidate_and_counts_it；test_v6_artifact_restart_removes_unreferenced_final_file | PASS（2 项） | 重启后 prepared→abandoned 并计数；残留 temp 与已 publish、无 revision 引用的文件清理。 |
| V7 | test_v7_region_commit_has_one_observable_transaction | PASS | trace 断言 revision→live text/pointer→resolved→单次 COMMIT；独立只读连接在 COMMIT 时仍读到旧值，提交后读到新值。 |
| V8 | test_v8_concurrent_same_region_has_one_winner_and_one_abandoned_candidate | PASS | 并发两候选只有一个 committed，另一个 abandoned；revision 行不交叉污染。 |
| V9 | test_v9_artifact_failure_is_invisible_and_success_publishes_consistently | PASS | 失败零推进且无孤儿；成功时断言 BEGIN→artifact 行→revision→CAS 指针→stage→resolved→publish→COMMIT，并校验 sha256/size/指针/文件一致。 |

V7 提供 AC3 要求的 trace 与独立连接双证据。V9 小型本地 fixture 的单用例为 0.40 秒（v9-artifact-timing.log；包含 assembly 与图片构建，不代表大文件锁时延基准）。R-ART-4 的 storage=None 用例通过真实 assembly 单独执行，见 storage-none-check.log；V1–V9 过滤运行中 1 项被显式 deselect，即该 R-ART-4 用例，随后已单独执行并通过。
