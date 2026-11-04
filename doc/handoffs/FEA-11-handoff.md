# FEA-11 Handoff（DSH 接手阶段 → Phase C 交接）

状态：**in_progress**（未完成；不得 closeout/Review）。Owner：ZCode 启动 → DSH 接手（Codex/ZCode 额度耗尽期间）；Reviewer 待 Appointment（全新上下文）。

## 恢复点

- 仓库：`G:/CODEX/New Manga`（main）；HEAD 与 WIP 链：`40cc6508`（ZCode 中断快照）→ `0ca363cd` → `ec40c51e`（Phase A 收尾）→ `29749af2` → `f912b41` → `3ab6c8ef` → `64db448d`（v8 迁移测试）→ 本提交（AC-MATRIX/Handoff）。
- Task：`doc/tasks/FEA-11.md`（in_progress；10 AC；逐文件写域；条件项）。
- 契约：`doc/plan/FEA-C17_SOURCE_SYNC_DRAFT.md`（v1.0 FROZEN）+ 冻结记录；pins 18/18。
- 进度：`G:/CODEX/New Manga.workspace/FEA-10/agent-output/DSH-PROGRESS-2026-11-04.md`。

## 已完成

### Phase A（`ec40c51e`）
v8 迁移（schema.py `default_migrations()` 追加 `v8__source_sync` 四表）；`src/application/sources/`（scanner/matcher/planner/service/runtime/model/ports/errors）；`src/infrastructure/sqlite/source_sync.py`；`core_service.py` 命令 dispatch 与 capability；`core_assembly.py` 装配。
修复 9 处：scanner 1 元 tuple version_id、matcher 逐侧重复检测、missing/defer 校验、planner target 键、授权先于 location、current-location 更新顺序、operation 先于 publications（FK）、CAS 页顺序、locator 回退不复用已配对 entry、CAS 物理 page 行（非 V(p,t) 视图）。

### Phase B（`29749af2`…`64db448d`）
- `tests/fea11/test_source_scan.py`（8）：scan/diff/plan/stale 零写。
- `test_source_sync.py`（4）：apply 幂等/tombstone/ACK 开门/replay 拒绝/cancel。
- `test_source_relink.py`（4）：relink 保续/拒绝内容变/repoint 需 resync 确认/成功发布。
- `test_source_operation.py`（4）：durable 恢复/伪造摘要拒绝/未知操作。
- `test_source_lineage.py`（2）：captured_v7/legacy_unverified 冻结。
- `test_v8_migration.py`（4）：全起点迁移/旧数据守恒/旧端拒写/约束守卫。
- 实跑：`pytest tests/fea11` **26 passed**；`tests/core + tests/storage + tests/fea11` **1046 passed**；check PASS；pins 18/18。

### 证据
`verification/FEA-11/AC-MATRIX.md`（逐 AC 状态与缺口）；测试输出可直接复跑（命令见 AC-MATRIX）。

## 未完成（Phase C 清单）

1. **Host/C#**：`apps/desktop-avalonia/src/NewManga.Host/Sources/SourceOperationCoordinator.cs`（Host durable journal/授权/ACK/恢复；DPAPI/锁/原子替换复用 C-15 §5）、`SourceReadCoordinator.cs` 命令映射、`HostRuntime.cs` 路由/写 Gate、`NewManga.CoreClient/Commands/HostCommandRegistry.cs`、`CoreServiceClient.cs`、`Wire/CoreProtocol.cs`（按 C-17 命令面；不扩冻结面）。
2. **真实 IPC**：`Fea11SourceIpcTests.cs`（Host→Core→DB→resolve→实际字节；源守恒；fail-closed）；`SourceOperationTests.cs`（崩溃点矩阵/ACK/恢复/撤销）；`SourceRegistryTests.cs`/`HostRuntimeIntegrationTests.cs` 回归。
3. **resolve 版本选择**：C-17 §7.2 `page-rendition-v2-*` 选择函数 + `core_service.py` 窄接缝；同步后生产 resolve/issue 读新图断言；旧资源键不可变。
4. **迁移/回归**：真实 v7→v8 升级（Host 侧装配）、主套件/providers、全量 .NET（build 0/0、test 不减少）、check/pins、范围 0 域外、FEA-09/10 tracked 证据零 diff。
5. AC-MATRIX 完成态、`verification/FEA-11/logs/**` 证据、Task 卡 AC 标记如实（未验证不得 MET）、status → in_review。

## 门禁（当前已跑）

- `pytest tests/fea11` 26 passed；`tests/core+storage+fea11` 1046 passed；`check.ps1` PASS；`verify_pins.ps1` 18/18；工作树 clean；未 push；冻结契约/组合根/FEA-08-10 证据零改动。

## 交接指令

见 `G:/CODEX/New Manga.workspace/FEA-11/codex-impl-continue.md`（Phase C 部分）与 Appointment `doc/reviews/FEA-11-appointment.md`。写域外文件（render_preview.py/regions.py/drafts.py 等）先报 DSH；不 commit/push。

## 资源

- 隔离根：`G:/CODEX/New Manga.workspace/FEA-11/`（fixtures/TEMP/TMP/诊断日志/phaseA-diag/phaseB-diag）。
- 证据：`verification/FEA-11/AC-MATRIX.md`（+ 后续 logs/）。
