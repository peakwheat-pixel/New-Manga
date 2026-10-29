# V11R-F0-1 I4 有界返修证据（独立审查 r4 关闭项）

- 审查轮次：r4 结论——P1（单 revision 目标存活）**CLOSED**、P3 **CLOSED**；仅剩 2×P2 关闭项
  （页上限并发测试的独立连接 + rows 零写断言；restore 绕过顶点上限）与 1 个新 P2
  （restore 未映射 seam `TARGET_NOT_FOUND`）。Lead 指示本轮后不再开第 5 轮全量复审，由独立验证只核这 3 条。
- 审查报告：`doc/reviews/V11R-F0-1-r4-codex.md`（独立通道，Lead 归档；本分支可见 r1）
- 上一轮固定点：`ed2d991e4d7f5ba578deedadb9cf1be49bbe90bd`（r4 审查 pin）
- 本分支：`v11r/region-write`
  - F0-1 `f971ece07` / F0-2 `089cdb761` / I1 `c861fcba5` / I2 `1a457111c` / I3 `ed2d991e4`
  - **I4 修复 HEAD：`6af12665b336961546315b2ab8863fbde8fb2297`**（docs 提交在其后；最终 HEAD 见 Handoff）
- Owner：core-writer（未自审）；契约：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md` **v1.5**

## 1. 逐项处置表（问题 → 修法 → 新增/修改测试 → commit）

| # | 审查问题 | 修法 | 测试（三条日志见 §2） | Commit |
|---|---|---|---|---|
| P2-A | 页上限并发测试未用独立连接（`test_region_create_cap.py:145`）：两个线程共用 `core.editing`/SQLite 连接，不满足「独立连接真实交错」；wire 断言缺 rows 总数不变 | 两个 create 线程显式记录 `ThreadRoutedConnection` 的**每线程真实 sqlite3 连接** id，断言两条连接互异且都不是主线程连接（路由即独立连接）；barrier 仍在双方预检后、任一事务前；断言只有胜者写入：`regions`/`region_revisions` 总行数各 +1、live count=limit、无孤儿；wire 满页用例补 `regions`/`region_revisions` 总数前后不变 | `logs/i4-1-create-cap-interleaving.log`：4 passed（含 `test_concurrent_creates_at_the_cap_boundary_cannot_overshoot`、`test_wire_create_at_cap_is_invalid_request_and_writes_nothing`） | `d858f44d7` |
| P2-B | `restore_revision_with_number` 绕过顶点上限（`service.py:1395`）：restore 直接把历史 snapshot 送 revision seam | `restore_revision_with_number` 在 `restore_from_snapshot` 后、建 revision/提交前调用 `assert_geometry_within_limits(staged.geometry)`；超限 typed `RegionLimitExceeded`，零写；wire `restore_region_revision` 映射为 `INVALID_REQUEST`/validation（固定短语） | `logs/i4-2-restore-geometry-limit.log`：2 passed（构造 513 顶点历史 revision → service 拒绝且 revision/current/几何不变；wire 拒绝且总数不变） | `f3ecc19de` |
| P2（新） | `restore_revision_with_number` 未把 seam `TARGET_NOT_FOUND` 映射为 typed not-found：只转 revision/lock conflict，其余非成功 → `RuntimeError`（wire UNKNOWN） | 提交结果显式加 `TARGET_NOT_FOUND → RegionNotFound`（detail=region id）；wire handler 既有 `RegionNotFound → RegionLookupError` 映射为 `TARGET_NOT_FOUND`/not_found 固定短语，零写 | `logs/i4-3-restore-liveness.log`：2 passed（barrier 在 `BEGIN IMMEDIATE` 前，独立连接软删目标 → service typed not-found 零写；wire restore 返回 `TARGET_NOT_FOUND`/not_found） | `6af12665b` |

## 2. 三条测试日志（Lead 指定）

| 日志 | 命令 | 结果 |
|---|---|---|
| `logs/i4-1-create-cap-interleaving.log` | `python -m pytest -v tests/core/test_region_create_cap.py` | **4 passed**（满页顺序 / 直接 seam 权威 / **独立连接并发** / wire 满页零写） |
| `logs/i4-2-restore-geometry-limit.log` | `python -m pytest -v tests/core/test_region_restore_limits.py` | **2 passed**（513 顶点历史 snapshot 被 service 拒绝；wire `INVALID_REQUEST` 零写） |
| `logs/i4-3-restore-liveness.log` | `python -m pytest -v tests/core/test_region_restore_liveness.py` | **2 passed**（并发软删后 restore typed not-found 零写；wire `TARGET_NOT_FOUND`） |

每个日志末尾均有 `EXIT_CODE=0` 行。

## 3. Gate（实测）

| # | 命令（工作目录） | Exit | 结果摘要 | 日志 |
|---|---|---|---:|---|
| G1 | `python -m pytest -q`（仓库根） | 0 | **2727 passed, 10 skipped, 2 warnings in 236.91s**（I3 后 2723；+4 I4 用例；0 failed） | `logs/pytest-full.log` |
| G2 | 三条逐项测试（见 §2） | 0 | 4 + 2 + 2 passed | §2 三个日志 |
| G3 | `dotnet build NewManga.sln -warnaserror`（`apps/desktop-avalonia`） | 0 | **0 警告 / 0 错误**（本轮无 C# 生产代码改动） | — |

skip 均为既有环境性 skip，与本返修无关。

## 4. 复核点（只核这 3 条）

1. **P2-A**：并发用例内 `thread_connection_ids` 断言两条真实连接互异且不等于主线程连接；
   `regions`/`region_revisions` 总数各 +1（只有胜者写入）；wire 用例拒绝前后总数不变。
2. **P2-B**：`restore_revision_with_number` 在 seam 前调用 `assert_geometry_within_limits`；
   513 顶点历史 revision 的 service/wire 均被拒，current pointer / 几何 / revision 数不变。
3. **P2（新）**：`TARGET_NOT_FOUND → RegionNotFound` 显式分支；并发软删窗口后 restore 零写且
   wire 返回 `TARGET_NOT_FOUND`/not_found（不再是 UNKNOWN）。
4. 契约 §8 已补 I4 验证要求（v1.5）；GAP/ACL 诚实性未变。

## 5. 复审入口（独立验证）

```powershell
git log --oneline ed2d991e4..HEAD          # I4 三个修复/测试 commit + docs
git diff ed2d991e4..HEAD -- src apps/desktop-avalonia/src/NewManga.CoreClient
python -m pytest -v tests/core/test_region_create_cap.py
python -m pytest -v tests/core/test_region_restore_limits.py
python -m pytest -v tests/core/test_region_restore_liveness.py
python -m pytest -q
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
```

复审结论请按 `doc/templates/REVIEW.md`；Owner 无 push 权限，最终由 Lead 集成。
