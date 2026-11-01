# FEA-04 preflight blocker 矩阵

preflight 只读取 Current session memento、DraftBuffer 与 Run intent 的本地状态；实现中没有调用 IHostController/Core，也没有切换执行入口。每个 blocker 产生 Code、Source、Detail；任一 blocker 存在时 Allowed=false。

| 冻结 Code | Source | 派生谓词 | 用例 | 当前验证状态 |
|---|---|---|---|---|
| PENDING_REGION_TYPE | S1 | DraftBuffer 中含 regionType patch 且 Status != Flushed | Preflight_reports_each_frozen_blocker_without_host_side_effects；Preflight_derives_all_five_blockers_from_current_state；Region_type_draft_has_a_stable_draft_id_and_flushes_without_host_calls | 已新增；未执行（build restore 阻断） |
| PENDING_CONFIRMATION | S2 | CurrentStudioMemento.HasPendingConfirmation | 同上两项 preflight 用例 | 已新增；未执行 |
| UNFLUSHED_RUN_KEY | S3 | CurrentRunIntentCoordinator.PendingKey 非空 | 同上两项 preflight 用例；Run_start_retry_reuses_the_same_key_after_ack_loss | 已新增；未执行 |
| UNMAPPED_READER_ANCHOR | S4 | Reader memento 有 PageId/SemanticAnchor 且 AnchorMapped=false | 同上两项 preflight 用例；Reader_keeps_old_anchor_when_new_projection_cannot_map_its_page_id | 已新增；未执行 |
| UNMAPPED_SHELL_STATE | S6 | Shell.HasUnmappedState，或 Appearance draft dirty 且 IsMapped=false | 同上两项 preflight 用例 | 已新增；未执行 |

Clear path 用例 Console_selection_and_filters_are_rebuildable_session_state_not_preflight_blockers 覆盖 Allowed=true，并比较调用前后的 Host 计数；未执行。实现没有在 Allowed=true 时创建 Run。

## Host/Core 副作用计数

新增测试 Capture 记录 FakeHostController.StartCalls、StartRequests、RefreshCalls、ReaderLoadCount、RunSnapshotRequests、TaskProjectionRequests、StartRunRequests、SetRegionTypeCalls 和 LifecycleLog。阻断和允许用例都比较调用前后状态。以上断言当前均为未执行状态，不能作为 PASS 报告。

## 当前限制

Q-20 五个 blocker 及其 Source 由冻结卡规定。当前报告确认源码中的映射和测试设计覆盖；独立编译、测试结果与实现 Review 尚待环境恢复及 DSH 指派。
