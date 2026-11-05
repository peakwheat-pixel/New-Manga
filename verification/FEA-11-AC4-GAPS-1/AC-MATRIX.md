# FEA-11-AC4-GAPS-1 · AC 证据矩阵

> 交付：`tests/fea11/test_source_sync.py`（+18 用例）、`tests/fea11/test_source_sync_storage.py`（+1 用例）。
> 基线：`base_commit 51e139eff`（main head `d8049fe6e`）。**test-only**：无 `src/**`、契约、schema 变更。

## 判别性装置（G11 共同比较集）

| 装置 | 位置 | 说明 |
|---|---|---|
| `_full_snapshot(conn)` | `tests/fea11/test_source_sync.py` | 卡内冻结口径 4 的 **16 表** `SELECT * ORDER BY 1` → `{table: [tuple]}`；`_assert_snapshot_equal` 失败时打印逐表行数/首行差 |
| `_routed_file_stack(path)` | 同上 | 生产 `ThreadRoutedConnection` facade（每线程独立真实连接）+ 隔离文件 DB；AC1-a/b「同实例两线程」用它（`:memory:` 单连接跨线程共享同一事务状态，`connection.py` TASK-060 Q-001 明确非安全） |
| `_file_db_stack(path)` | 同上 | 两独立 `SourceSyncStore`/`SourceReadGrantRegistry`/`build_source_sync_stack` 指向同一文件 DB（AC1-c） |
| `_materialize_target_version` | 同上 | 预写目标 `source_versions`/`source_entries`，使两栈都短路 `_ensure_target_version` 并到达 `BEGIN IMMEDIATE`（live-scan cache 是每栈隔离的；L1 seam 防御装置） |
| `_seed_three_regions` | 同上 | rg1/rg2/rg3 current=r1/r2/r3 + rg3 历史 `r3old`（AC3） |
| `_seed_pipeline_run` | 同上 | `pipeline_runs`/`pipeline_run_targets`（+ task/step/candidate）用于 G9 draft/Run 漂移 |
| `_seed_book_and_chapter` / `_add_project_reference` | 同上 | b1 与共享源 s1 的既有/新增项目引用（G5/G10） |

## AC1 并发 apply（C-17 §6.2「两个并发 apply」）

| 子项 | 测试 | 断言要点 | 结果 |
|---|---|---|---|
| AC1-a same operation | `test_concurrent_same_operation_returns_the_original_receipt_once` | 两线程都返回；`accepted=true`、`state=core-committed`、同 `operation_id`/`request_digest`；`source_operations` 对 plan 恰 1 行；`page_bindings` 只增一代（p1=2 / p2=1 / 总 3）；`source_binding_publications` 恰 1 套；plan `applied` 且 `applied_at` 非空 | PASS |
| AC1-b different operation | `test_concurrent_different_operations_leave_one_commit_and_one_refusal` | 恰 1 成功；失败方 typed ∈ {`SOURCE_OPERATION_CONFLICT`,`SOURCE_PLAN_STALE`} 且**非** `sqlite3.Error`；恰一次提交（1 receipt / 1 publication / 3 bindings）；失败前快照 = 失败后快照（确定性复探） | PASS |
| AC1-c 两独立 stack/两连接 | `test_two_connection_stacks_commit_exactly_once_on_one_file_db` | `tmp_path` 文件 DB + FK/WAL/busy_timeout=5000；两 registry 以相同 `registry_id/generation/identity` 注册等价 grant（断言 payload 授权基线相等）；恰一次提交（1 op / 各页 2 代 / 恰 2 publication）；失败方 typed ∈ {`SOURCE_PLAN_STALE(cause=applied)`,`SOURCE_OPERATION_CONFLICT`}；**无 `database is locked`**；零写复探通过 | PASS |
| AC1-d 跨实例 same-op replay | 不写断言（卡内 Out） | 见卡 Out：replay 检查在 `BEGIN` 之前；生产串行路径已满足 C-17 §6.2 | N/A（Out） |

## AC2 DB 失败注入

| 子项 | 测试 | 断言要点 | 结果 |
|---|---|---|---|
| AC2-a 事务中途失败 | `test_mid_transaction_storage_failure_rolls_back_the_whole_batch` | `BEFORE INSERT ON page_bindings WHEN NEW.page_id='p2'` `RAISE(ABORT)`；apply 抛真实 `sqlite3.Error`（非 typed 业务拒绝）；16 表快照与失败前完全相等；plan 仍 `confirmed`/`applied_at IS NULL`；0 operation、0 publication、p1 仍 1 行；移除 trigger 后新 `operation_id` 重试成功 | PASS |
| AC2-b 最后一步失败 | `test_final_step_storage_failure_rolls_back_the_whole_batch` | `BEFORE UPDATE ON source_operations WHEN OLD.state='host-authorized'`（命中 `commit_operation`，`source_sync.py:186-207`）；整批回滚（16 表相等，含 operation 行本身）；plan 仍 confirmed；重试成功 | PASS |
| AC2-c wire 级 typed | `test_storage_failure_is_a_typed_wire_error_with_zero_business_writes`（新文件） | 真实 `assemble_production_core` + host-control `ResyncSource` dispatch；envelope `code=SOURCE_SYNC_STORAGE_FAILED`、`category=internal`、`retryable=true`、`result=None`；`injected`/`RAISE` 不出现在响应 JSON；16 表零写；同 trigger 下直接 service 调用抛原始 `sqlite3.IntegrityError`（证明失败点在 `BEGIN IMMEDIATE` 与 `COMMIT` 之间，**不是** post-commit `_bind_operation_grant`，L3）；移除 trigger 后 wire 重试成功 | PASS |

## AC3 第三区域 BaseRevisionId（双分支）

| 子项 | 测试 | 断言要点 | 结果 |
|---|---|---|---|
| AC3-a plan 自带过期 revision | `test_third_region_stale_migrate_revision_aborts_the_whole_batch` | 3 region current r1/r2/r3 + rg3 历史 `r3old`；decision=bind、`migrate_revision_ids=[r1,r2,r3old]`；期望 `STALE_BASE_REVISION`（非 `INVALID_REQUEST`）；前两项迁移 + 新 binding + lineage 全部回滚：16 表相等、regions=3、region_revisions=4、lineage=0、rg3 current 仍 `r3` | PASS |
| AC3-b 现实漂移 | `test_third_region_live_drift_is_plan_stale_manual` | confirm 后为 rg3 插入 `r3new`（rev_no 3）并改 `current_revision_id`；期望 `SOURCE_PLAN_STALE(cause='manual')`；断言**不是** `STALE_BASE_REVISION`（manual/protection digest 覆盖 current，不会走到迁移分支）；16 表零写；plan 仍 confirmed | PASS |
| AC3-c 口径登记 | 卡内 §AC3-c | AC3-a 是非 conforming Host 的防御 seam（L2）；plan-time 校验 Out | 已登记 |

## AC4 漂移矩阵 + 全表零写（G4–G11）

共同断言：每次拒绝 `_full_snapshot` 前后逐行相等；无未包装 `sqlite3.*`；错误码/`details.cause` 精确匹配；plan 状态不被提前提交。

| 子项 | 测试 | 装置（plan confirm 之后） | 期望 typed | 结果 |
|---|---|---|---|---|
| G4 源物理漂移 | `test_drift_source_bytes_refuses_file_identity_changed` | 同路径覆盖 zip 字节 | `FILE_IDENTITY_CHANGED`（strict lease） | PASS |
| G4b 版本行漂移 | `test_drift_source_version_row_is_plan_stale_source` | 篡改 `source_versions.content_digest` | `SOURCE_PLAN_STALE(cause=source)` | PASS |
| G5 引用集合漂移 | `test_drift_reference_set_is_plan_stale_binding` | 新增 b2/c2/p3 共享源引用 | `SOURCE_PLAN_STALE(cause=binding)` | PASS |
| G6 决定/plan 失效 | `test_drift_decision_is_plan_stale_decision` | `planner.invalidate(reason='decision')` | `SOURCE_PLAN_STALE(cause=decision)`；plan 仍 `stale`/`stale_reason=decision` | PASS |
| G7 授权 generation 漂移 | `test_drift_authorization_generation_is_plan_stale_authorization` | 用 generation=2 的 grant/授权（baseline=1，identity 相同） | `SOURCE_PLAN_STALE(cause=authorization)` | PASS |
| G8 授权失联 | `test_drift_authorization_eof_is_grant_revoked` | `registry.revoke_all_for_session()` | `SOURCE_GRANT_REVOKED` | PASS |
| G9 人工 revision | `test_drift_manual_revision_is_plan_stale_manual` | 改 p2 rg1 `text_json`（p2 是**最后一个** base） | `SOURCE_PLAN_STALE(cause=manual)` | PASS |
| G9 保护位 | `test_drift_protection_is_plan_stale_manual` | 改 p2 rg1 `region_locked` | `SOURCE_PLAN_STALE(cause=manual)` | PASS |
| G9 draft | `test_drift_draft_is_plan_stale_manual` | 插入未 resolve 的 `step_result_candidates` | `SOURCE_PLAN_STALE(cause=manual)` | PASS |
| G9 Run | `test_drift_run_is_plan_stale_manual` | 插入 `pipeline_runs`/`pipeline_run_targets` | `SOURCE_PLAN_STALE(cause=manual)` | PASS |
| G10 多项目末项 | `test_multi_project_final_item_drift_leaves_both_projects_untouched` | b1+b2 共享 s1，scope=all，漂移**最后一个 base**（b2/p3 的 `sort_order`） | `SOURCE_PLAN_STALE(cause=binding)`；两项目零写（16 表相等，各页仍 1 行 binding） | PASS |
| G11 比较集 | `_full_snapshot` / `_assert_snapshot_equal` | 所有拒绝型用例共用 | 16 表逐行相等 | PASS |

## AC5 证据、范围与门禁

| 要求 | 结果 |
|---|---|
| `pytest tests/fea11 -q -p no:cacheprovider` | 88 passed（基线 69） |
| `pytest tests -q -p no:warnings --tb=no` | **3183 passed / 10 skipped**（释放日基线 3164/10，+19 passed，skip 不增） |
| 新增测试计数 | 19（`test_source_sync.py` +18、`test_source_sync_storage.py` +1），全部实跑 |
| `check.ps1 -TaskPath doc/tasks/FEA-11-AC4-GAPS-1.md` | PASS（见 `logs/gates.log`） |
| `check.ps1`（默认） | PASS（见 `logs/gates.log`） |
| `verify_pins.ps1` | 18/18 PASS（见 `logs/gates.log`） |
| 0 域外 diff | `git diff --name-only 51e139eff..HEAD -- src/ doc/plan doc/contracts apps` 为空（`logs/scope-diff.log`） |
| 无新依赖 / 无 schema/migration 改动 | 是（0 域外 diff；无依赖文件改动） |
| 隔离根 | `G:/CODEX/New Manga.workspace/FEA-11-AC4-GAPS-1/`（probes/logs；未复用/未复写 FEA-11 tracked 证据） |
| 独立上下文 Review + 负向探针 | **待 Reviewer**（本卡不自行宣告 MET；见 `logs/mutation-probes.log` 的实现者自检，非权威） |
| AC11-4 判定 | 由 Lead/Review 判定；本卡不自行宣告 MET |
| `.NET` 口径 | **NOT_RUN**（0 C# 文件变更、纯 Python 测试；不得写 PASS）见 `logs/dotnet-not-run.md` |
