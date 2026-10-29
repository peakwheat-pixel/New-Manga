# V11R-F0-1 I3 有界返修证据（独立审查 r3 FAIL 处置）

- 审查报告：`doc/reviews/V11R-F0-1-r3-codex.md`（独立通道；结论 FAIL：r2 五项中 4 项 CLOSED，剩 1 个新 P1 + 2 个 P2 + 1 个可选 P3；由 Lead 归档）
  - r1：`doc/reviews/V11R-F0-1-r1-codex.md`（本分支经 `git merge main` 可见）；r2：Lead 归档于 main/审查通道
- 上一轮固定点：`1a457111cd2cb68321947b5359a2ad235f13fe2e`（r3 审查 pin）
- 本分支：`v11r/region-write`
  - F0-1 HEAD：`f971ece0785fb3fd32431b1b5f6c51daebc0541e`
  - F0-2 HEAD（独立提交）：`089cdb761f7d015688cd273d40a9c9fae668c154`
  - I1 HEAD：`c861fcba5aa3dd70fb8444cc14c6dc6ea607b395`
  - I2 HEAD：`1a457111cd2cb68321947b5359a2ad235f13fe2e`
  - **I3 修复 HEAD：`c0ea0df4fd8c21f85db145f56d28f8f27606c0d6`**（docs 提交在其后；最终 HEAD 见 Handoff）
- Owner：core-writer（**未自审**；复审走独立通道，未通过前不合入 main）
- 契约：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md` **v1.4**

## 0. 处置原则

- 每项独立 commit；P3 为可选清理，单独 `refactor` 提交且行为不变；
- P1 用**独立 sqlite3 连接 + barrier**（预检后、`BEGIN IMMEDIATE` 前）制造真实软删交错；
- P2-A 的并发测试用 barrier 让两个 create 都在预检后（同见 N-1）再进事务，验证事务内上限是唯一权威；
- P2-B 直接在 application service 层构造超限几何（不经过 wire/Host），断言持久化前拒绝；
- 未降低 GAP/ACL 诚实性（GAP-1/2/3、契约 §3.1 均保持）。

## 1. 逐项处置表（问题 → 修法 → 新增测试 → commit）

| # | 审查问题 | 修法 | 新增测试（真实 SQLite） | Commit |
|---|---|---|---|---|
| P1 | 单 revision 写入可在目标软删后仍提交：`commit_region_revision` 事务内只读 current/锁，未读 `deleted_at`；save_geometry/save_manual_translation/confirm/set_region_locks 预检通过后、另一连接删除/合并该 region，旧调用仍插 revision 并返回成功 | 单 revision seam 在 `BEGIN IMMEDIATE` 内同时重读 `deleted_at`；缺失/已删 ⇒ rollback + `TARGET_NOT_FOUND`（detail=region_id）。服务层 `_commit` / `_commit_user_or_raise` 映射为 typed `RegionNotFound`（wire `TARGET_NOT_FOUND` 安全短语，零写）；in-memory committer 同语义 | `tests/core/test_region_single_write_liveness.py`（5）：barrier 装在 `BEGIN IMMEDIATE` 前，独立 sqlite3 连接软删目标；save_geometry / save_manual_translation / confirm_final / set_locks 全部 typed not-found 且零写（revision 数、几何/文本/锁状态不变）；wire `save_region_geometry` 返回 `TARGET_NOT_FOUND` | `d6bfee1f3` |
| P2-A | 500 live region 上限有并发越界窗口：两个调用者都在事务外数到 499 → 501 | `commit_region_batch` 新增 `page_region_limit=(page_id, limit)`：在**同一事务内**重查 page live region 数，`count >= limit` ⇒ 整批回滚 + `REGION_LIMIT_EXCEEDED`（service → `RegionLimitExceeded` → wire `INVALID_REQUEST`/validation）。`create_region` 的预检查降级为快速失败，事务内计数是权威 | `tests/core/test_region_create_cap.py`（4）：满页顺序拒绝零写；直接 seam 证明预检通过后事务内上限仍拒绝；**并发测试**（limit=2、起始 1 个、两 create 在 barrier 同过预检）恰好 1 成功 + 1 限流拒绝、页内永不超过上限、无孤儿；wire 满页 `INVALID_REQUEST` | `e0f9597e4` |
| P2-B | service 层 `save_geometry`/`split_region` 绕过顶点上限：`MAX_GEOMETRY_POINTS` 只在 wire/Host 检查 | 新增 `service.assert_geometry_within_limits`（polygon 顶点数；bbox-only 记为 4），在持久化前覆盖 create_region / save_geometry / split 每个 part / merge 派生多边形（两个合法源合并后超限也拒绝），抛 typed `RegionLimitExceeded` | `tests/core/test_region_service_limits.py`（5）：四条路径直接 service 调用超限均持久化前拒绝且零写（无 region/revision、源保持 live）；恰好 512 顶点仍允许 | `00ab2dcf7` |
| P3（可选） | `RegionTextProjection.cs` 两份重复 `RequireInt` | 合并为一份 `internal static RegionTextDetail.RequireInt`，`RegionPageTextProjection.Parse` 复用；行为与异常文案不变 | `RegionWriteCommandTests` 74 passed（DTO 解析/缺失字段用例全绿），build 0W/0E | `c0ea0df4f` |

## 2. 真实交错 / 边界测试日志

- **P1 单 revision 交错**：`logs/pytest-i3-interleaving-verbose.log`（9 PASSED）：
  `test_save_geometry_after_concurrent_delete_is_target_not_found`、
  `test_save_manual_translation_...`、`test_confirm_final_...`、`test_set_locks_...`、
  `test_wire_save_region_geometry_...`、以及 P2-A 的满页/直接 seam/并发/ wire 四例。
- 交错做法：barrier 装在 `commit_region_revision` 真实 `BEGIN IMMEDIATE` 之前（服务预检已过、事务未开）；
  工作线程用**独立 sqlite3 连接**在窗口内软删目标并 commit；主线程随后进事务 → 事务内重读发现
  `deleted_at` → rollback + TARGET_NOT_FOUND。断言只通过 fresh query / Core facade 读取。
- **P2-A 并发上限**：同一 barrier 机制，两个 create 线程都在预检后到达，事务内计数裁决；
  日志逐用例 PASSED 见上。

## 3. Gate（全部实测，日志在本目录 `logs/`）

环境：Windows 10.0.26100；Python 3.14.6；dotnet SDK 10.0.401（target net9.0）；pytest 9.1.1。

| # | 命令（工作目录） | Exit | 结果摘要 | 日志 |
|---|---|---|---:|---|
| G1 | `python -m pytest -q`（仓库根） | 0 | **2723 passed, 10 skipped, 2 warnings in 234.03s**（I2 后 2709；+14 I3 用例；0 failed） | `logs/pytest-full.log` |
| G2 | `python -m pytest -q <I3 + 既有 Region 相关 14 文件>` | 0 | **100 passed** | `logs/pytest-region-i3.log` |
| G3 | `python -m pytest -v tests/core/test_region_single_write_liveness.py tests/core/test_region_create_cap.py` | 0 | **9 passed**（逐用例名见 §2） | `logs/pytest-i3-interleaving-verbose.log` |
| G4 | `dotnet build NewManga.sln -warnaserror`（`apps/desktop-avalonia`） | 0 | **0 警告 / 0 错误** | `logs/dotnet-build.log` |
| G5 | `dotnet test NewManga.sln --no-build` | 0 | 全绿：ThemeEngine 189、Host 42+24skip、DesignSystem 67、CoreClient 119+22skip、App 232+6skip；0 failed | `logs/dotnet-test.log` |
| G6 | `dotnet test NewManga.sln --no-build --filter "RegionWriteCommandTests｜CommandParityContractTests｜CommandContractV11RTests"` | 0 | **85 passed / 0 failed** | `logs/dotnet-test-region-i3.log` |

skip 均为既有环境性 skip，与本返修无关；本轮 G4/G5 一次通过，无测试主机崩溃。

## 4. 数据安全复核点（复审建议逐项核对）

1. **单 revision 目标存活**：`commit_region_revision` 事务内 `SELECT current_revision_id, deleted_at, <locks>`；
   `deleted_at` 非空或行缺失 ⇒ rollback + TARGET_NOT_FOUND，无新 revision/指针/状态写入。
2. **四类单写路径**：save_geometry / save_manual_translation / confirm_final / set_region_lock 在并发软删窗口
   后均 typed not-found 且零写（`test_region_single_write_liveness.py`，G3）。
3. **页上限原子性**：`page_region_limit` 在 batch 事务内重查 live count；并发测试恰好 1 成功 + 1 拒绝，
   页内不超过 limit（`test_region_create_cap.py`）。
4. **service 顶点上限**：create/save/split part/merge 派生多边形均在持久化前拒绝；恰好上限允许。
5. **回归面**：I2 的软删目标批量校验、真实交错并发、DB_FAILED、wire/Host 上限测试全部仍绿（G2）。
6. **协议/历史/锁**：C067–C077 minor=3；冻结 66 快照未编辑；无历史删除/upsert 新路径；GAP-3 双投影未改。
7. **P3 隔离**：仅 helper 去重，无行为差异（G6/DTO 用例）。

## 5. 复审入口

```powershell
git log --oneline f971ece07..HEAD     # F0-2 + I1 5 + merge main + A-3 + I2 5 + docs + I3 4 + docs
git diff 1a457111c..HEAD -- src apps/desktop-avalonia/src/NewManga.CoreClient
python -m pytest -q
python -m pytest -v tests/core/test_region_single_write_liveness.py tests/core/test_region_create_cap.py
python -m pytest -q tests/core/test_region_service_limits.py
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln --no-build
dotnet test NewManga.sln --no-build --filter "RegionWriteCommandTests|CommandParityContractTests|CommandContractV11RTests"
```

复审结论请按 `doc/templates/REVIEW.md`；Owner 无 push 权限，最终由 Lead 集成。
