# V11R-F0-1 · r5 窄验证（仅核 r4 遗留 3 项 P2）

**验证者**：reviewer（独立、只读，未参与实现；本次写操作仅本文件）。
**Pin**：`6a5c8eaa8e404e39e7c73a6631f796b70a632686`（I4 代码 head `6af12665b`，docs 提交在其后）；增量 `git diff ed2d991e4..6a5c8eaa8`。
**证据**：`verification/V11R-F0-1-I4/{README.md, commands.json, logs/i4-1,i4-2,i4-3, pytest-full.log}`。
**纪律**：只核这 3 项，不重审历史；未重跑 pytest/build（以 pin 内日志为准，未核项注明）；未改任何代码/证据。

**增量范围核实**（`git diff --name-only`，12 文件）：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md`（v1.4→v1.5，补 I4 验证要求）、`src/application/editing/service.py`、`src/bootstrap/core_service.py`、3 个测试文件、`verification/V11R-F0-1-I4/*`。无范围外代码改动。

---

## 1. 并发 create 的独立真实 SQLite 连接 + rows 零写 — **CLOSED**

**依据**：`ThreadRoutedConnection._current()`（`src/infrastructure/sqlite/connection.py:149-178`）按 `threading.local()` + registry 为每个线程懒创建**真实 `sqlite3.Connection`**；`tests/core/test_region_create_cap.py` 的 `test_concurrent_creates_at_the_cap_boundary_cannot_overshoot` 在两个 create 线程内各记录 `id(core.conn._current())`，断言 `len==2`、两条 id **互异**、且**不等于主线程连接 id**；barrier 挂在被 monkeypatch 的 `_commit_batch_or_raise` 上（`create_region` 先做 service 层预检、`_commit_batch_or_raise` 在 `:625` 才进入批事务），即「双方都过预检、任一事务未开始」的真交错；结果断言 `created==1`、`RegionLimitExceeded==1`、live count==limit、`regions`/`region_revisions` 总行数各 **+1**（只有胜者写）、无孤儿；wire 满页用例 `test_wire_create_at_cap_is_invalid_request_and_writes_nothing` 断言拒绝前后两表总行数**均不变**。日志 `logs/i4-1-create-cap-interleaving.log` = 4 passed、`EXIT_CODE=0`。

---

## 2. `restore_revision_with_number` 提交前顶点上限（513 拒 / 512 允许）— **CLOSED**

**依据**：`src/application/editing/service.py` 的 diff 在 `staged.restore_from_snapshot(...)` 之后、构造 `RegionRevision` 与提交**之前**调用 `assert_geometry_within_limits(staged.geometry)`（`:1386-1390` 区段）；该 helper 以 `points = len(polygon) if polygon else 4` 与 `points > MAX_GEOMETRY_POINTS` 判定，`MAX_GEOMETRY_POINTS = 512`（`region_canvas.py:41`）→ **513 拒绝、512 允许**，超限抛 typed `RegionLimitExceeded`。测试 `test_restore_rejects_oversized_history_snapshot_geometry` 插入 513 顶点历史 revision 后断言 `RegionLimitExceeded`，且 `current_revision_id`、`geometry.bbox/polygon`、`region_revisions` 计数**全部不变**（零写）；wire 用例断言 `INVALID_REQUEST`/`validation` 且 revision 数/几何不变。`512 允许` 由同一 helper 的严格 `>` 语义保证，并有 `tests/core/test_region_service_limits.py:154-160`（`test_at_the_bound_is_allowed`）以**恰好 512 顶点**创建并断言存回 512 顶点佐证（restore 与 create 共用该 helper）。日志 `logs/i4-2-restore-geometry-limit.log` = 2 passed、`EXIT_CODE=0`。
（P3 备注：无「restore 路径恰好 512 顶点成功」的专项用例；语义由共享 helper + 同值边界用例覆盖，不阻塞。）

---

## 3. restore 的 `TARGET_NOT_FOUND → RegionNotFound` 映射与 wire 安全短语 — **CLOSED**

**依据**：`service.py` diff 在提交结果分支中显式新增 `RegionCommitStatus.TARGET_NOT_FOUND → raise RegionNotFound(result.detail or region_id)`（位于 `APPLIED` 检查之前、`RuntimeError` 之前，`RegionRevisionChanged` 之后）；wire handler `restore_region_revision` 的 `except RegionNotFound → raise RegionLookupError(region_id)`（`core_service.py:2276-2277`）把 typed not-found 收敛到既有冻结行；dispatch 的 `except RegionLookupError`（`:5146-5161`）返回 `code=E_TARGET_NOT_FOUND`、`category="not_found"`、`message=error.message`——`RegionLookupError.__init__(region_id, message="region not found")` 只持 opaque id + **固定短语**，不携带原始异常文本/路径（类注释明确 §8 安全要求）。测试 `test_restore_after_concurrent_soft_delete_is_typed_not_found_zero_write`（commit 门处用**独立临时 sqlite3 连接**软删目标）断言 service 抛 `RegionNotFound`、revision 数不变、仅旁路 delete 生效；wire 用例断言 `code=="TARGET_NOT_FOUND"`、`category=="not_found"`、revision 数不变。日志 `logs/i4-3-restore-liveness.log` = 2 passed、`EXIT_CODE=0`。
（P3 备注：wire 测试断言 code/category，未单独断言 message 文案；固定短语由 `RegionLookupError` 默认值保证，代码层面无原始文本上网。）

---

## 证据与门禁（只读核对，未重跑）

- `logs/pytest-full.log`：`2727 passed, 10 skipped, 2 warnings in 236.91s`，末尾 `EXIT_CODE=0`（I3 为 2723，+4 与 I4 新增 restore 两文件各 2 例一致）。日志末尾的 `PrimaryNavigationRail.qml/ReaderView.qml TypeError` 是**旧 UI 运行噪音**（pytest 汇总行之后的 Qt 输出，非测试失败）。
- `logs/i4-1/2/3`：4 + 2 + 2 passed，均 `EXIT_CODE=0`。
- `commands.json`：reviewed_head=`ed2d991e4`、i4_head=`6af12665b`、契约 v1.5、逐项 commit `d858f44d7`/`f3ecc19de`/`6af12665b` 与 diff 对得上。
- 契约 diff 仅 v1.4→v1.5 头部与 §8 I4 验证要求 + 变更记录一行，未改既有冻结语义。

---

## 结论

| # | 项目 | 结果 |
|---|---|---|
| 1 | 并发 create 独立真实连接 + rows 零写 | **CLOSED** |
| 2 | restore 顶点上限（513 拒零写 / 512 允许） | **CLOSED** |
| 3 | restore `TARGET_NOT_FOUND→RegionNotFound` + wire 安全短语 | **CLOSED** |

**F0-1 可否合入 main：可。**
