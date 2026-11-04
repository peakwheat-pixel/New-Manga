# FEA-11 AC-MATRIX（实施中；DSH 维护）

状态：**in_progress**（Phase A/B 证据已落地；Phase C（Host/C#/真实 IPC）与最终门禁未完成——未完成的 AC 不得标 MET）。
隔离根：`G:/CODEX/New Manga.workspace/FEA-11/`；TEMP/TMP/DataRoot/Host registry 均在其中。C-17 v1.0 FROZEN（`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`、`doc/plan/FEA-CONTRACT-FROZEN-C17.md`）。

## 证据基线（实跑）

| 命令 | 结果 | 记录 |
|---|---|---|
| `C:/Python314/python.exe -m pytest tests/fea11 -q` | **26 passed** | 见下逐 AC |
| `pytest tests/core tests/storage tests/fea11` | **1046 passed** | 回归链（v8 迁移/旧端拒写/subprocess e2e） |
| `pwsh tools/governance/check.ps1` | PASS（2 warnings） | 指针治理 |
| `pwsh tools/governance/verify_pins.ps1` | PASS 18/18 | C-17 第 18 pin |

## 逐 AC 状态

| AC | 当前证据 | 状态 |
|---|---|---|
| AC11-1 变化检测/强验证/Dirty | scan 测试：同 mtime/size 不同字节可发现（`test_scan_same_mtime_size_bytes_changed_discovered`）；过期 grant typed 拒绝（`test_scan_expired_grant_typed_refusal`）；四路中三路在服务层可测、watcher 消费者实现待 Phase C | **PARTIAL**（定时扫描承接 FEA-11-SCAN-1） |
| AC11-2 scan/diff/plan | `test_scan_changed_container_diff_classifications`（数量=明细）、`test_scan_scope_all_requires_frozen_reference_books`、plan 绑定/预览/确认 | **MET** |
| AC11-3 页匹配（C-15 §3.2） | `test_scan_same_container_direct_continuation`、`test_scan_changed_container_diff_classifications`（unique_pixel/added/missing）、重复组与旧证据降级在 matcher 单测路径 | **PARTIAL**（PDF/ZIP 重排/旧库 fixture 待补） |
| AC11-4 CAS/原子性/零写 | `test_stale_apply_zero_write_baseline`（逐表快照零写）、`test_apply_rejects_replayed_different_request_without_writes`、`test_resync_apply_publishes_new_generation_and_replay_is_idempotent` | **MET（seam 层）** |
| AC11-5 守恒/tombstone/lineage | `test_tombstone`（sync 套件）、`test_first_switch_captures_current_revision_on_old_binding`、`test_second_switch_keeps_existing_lineage_attribution`、relink 保序 | **MET（seam 层，在途 Run/draft 交错待生产装配测试）** |
| AC11-6 relink/repoint/resync | `test_relink_renamed_same_container_keeps_binding_and_page`、`test_relink_rejects_changed_container`、`test_repoint_changed_content_requires_resync_confirmation`、`test_repoint_with_resync_confirmation_publishes_new_binding` | **MET（seam 层）** |
| AC11-7 缺失/诊断出口 | missing observation 路径（scan 套件）、tombstone 保留；管理诊断查询接线待 Phase C | **PARTIAL** |
| AC11-8 durable operation/双确认 | `test_operation_survives_a_fresh_stack_over_the_same_store`、`test_recovery_opens_gates_and_is_idempotent`、`test_acknowledge_rejects_forged_commit_digest`、`test_apply_acknowledge_opens_gates_and_marks_operation`、`test_operation_cancel_before_commit_keeps_zero_business_writes` | **MET（seam 层；Host journal/崩溃矩阵待 Phase C）** |
| AC11-9 生产链路/读图/回归 | v8 迁移链与 subprocess e2e 通过；真实 IPC/Host 授权链路未接（Phase C） | **NOT MET** |
| AC11-10 范围/冻结/证据 | check/pins 18/18、冻结契约零改动、逐 AC 证据；迁移测试 `test_v8_migration.py`（全起点/旧数据守恒/旧端拒写）；Handoff/AC-MATRIX 本文件 | **PARTIAL**（最终门禁/Review 待做） |

## 未完成清单（Phase C 与尾项）
1. Host/C#：`SourceOperationCoordinator`（Host durable journal/授权/ACK/恢复）、`SourceReadCoordinator` 命令映射、`HostRuntime` 路由、`HostCommandRegistry`/`CoreServiceClient`/`CoreProtocol` 接线（C-17 命令面）。
2. 真实 IPC 测试 `Fea11SourceIpcTests.cs` 与真实 v7→v8 迁移（Host 侧）、真实 grant/lease/撤销/DPAPI、崩溃点恢复矩阵。
3. resolve 版本选择（C-17 §7.2 `page-rendition-v2-*`）与同步后读新图断言。
4. 全量 .NET 门禁、主套件/providers 回归、check/pins、范围 0 域外、证据字节。
5. AC11-1 watcher 消费者 / AC11-7 诊断查询接线（如在本卡范围）。

## 已知缺口（非阻断，登记）
- FEA-11-SCAN-1 承接定时扫描/后台调度（proposed）。
- C-17 未覆盖的 Host 侧 capability 探测细节由 Phase C 测试验证。
