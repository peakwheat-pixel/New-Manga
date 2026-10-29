# V11R-F0-1 I2 有界返修证据（独立审查 r2 FAIL 处置）

- 审查报告：`doc/reviews/V11R-F0-1-r2-codex.md`（独立通道；结论 FAIL：2×P1 + 3×P2；由 Lead 归档到 main）
  - 上一轮 r1 报告：`doc/reviews/V11R-F0-1-r1-codex.md`（本分支已 `git merge main` 带入，复审可见）
- Reviewer 固定点：`c861fcba5`（I1 HEAD；r2 覆盖 F0-2 + I1 全部 5 项关闭核对 + 新问题扫描）
- 本分支：`v11r/region-write`
  - F0-1 HEAD：`f971ece0785fb3fd32431b1b5f6c51daebc0541e`
  - F0-2 HEAD（独立提交，另审）：`089cdb761f7d015688cd273d40a9c9fae668c154`
  - I1 HEAD：`c861fcba5aa3dd70fb8444cc14c6dc6ea607b395`
  - merge main（获取 r1 报告/项目治理文档）：`c180fa4ac`
  - **I2 修复 HEAD：`6c5a9f8c3186efe51319032f067fd21e0957fc9e`**（I2 提交链见 §1；docs 提交在最后）
- Owner：core-writer（**未自审**；复审走独立通道，未通过前不合入 main）
- 契约：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md` **v1.3**

## 0. 处置原则

- P1/P2 每项独立 commit；P2-C 明确标为 **F0-2 修复项**（`fix(V11R-F0-2): ...`），不混入 F0-1 语义；
- 「目标存活」与「真实交错」都在**真实生产 SQLite assembly** + **独立 sqlite3 连接 + `threading.Barrier`** 上验证，
  不使用 mock 事务、不在预检阶段伪造冲突；
- 未降低 GAP 诚实性：GAP-1「本任务新增」、GAP-2（F0-1 原始记录 / F0-2 单独 CLOSED）、GAP-3 双投影与
  「既有 manual save 未改」均保留；page/book ACL 仍按契约 §3.1 不做假授权；
- 合并 main 后顺带修复 A-3 契约的 C077 占位（A-3 契约测试要求注册表命令全部被声明），单独 commit 标明集成性质。

## 1. 逐项处置表（问题 → 修法 → 新增测试 → 证据/commit）

| # | 审查问题 | 修法 | 新增测试（真实 SQLite） | Commit |
|---|---|---|---|---|
| P1-A | 批事务只比较 `current_revision_id`，不重核对目标仍 live：两个调用者都在首次提交前通过 `_require_region` 时，第二个 merge/split 会再生成一套结果；delete/pin 也可写已软删目标 | `commit_region_batch` 第 1 步对**每个既有目标**（merge/split 源、reorder 全部、delete、pin、expected checks）重读 `deleted_at IS NULL`；软删改**条件 UPDATE**（`deleted_at IS NULL` 且给 expected 时 `current_revision_id = expected`）并强制 `rowcount==1`；pin UPDATE 带 live 条件；任一目标已删 ⇒ 整批 rollback + `RegionCommitStatus.TARGET_NOT_FOUND` → 服务层 typed `RegionNotFound`（wire `TARGET_NOT_FOUND` 安全短语） | `tests/core/test_region_target_liveness.py`（8 用例）：已软删源再 merge/split、已删目标再 delete/pin、真实第二连接在预检与提交间软删（直接 seam + 完整 merge 路径 barrier）、wire 重复 merge/delete/pin typed TARGET_NOT_FOUND 且零写 | `8a43a0224` |
| P1-B | 「并发测试」没有真实交错：只在服务预检阶段用假 revision 触发冲突，或直接调 committer；没有第二连接/barrier | 新增真实交错测试基建：在 `_commit_batch_or_raise` 内装 `threading.Barrier`（预检已过、事务未开），由**独立 sqlite3 连接**在该窗口推进 current 或软删，然后才进 `BEGIN IMMEDIATE` | `tests/core/test_region_concurrency.py`（7 用例）：单源 current 推进→conflict 零写；reorder 两 region 在同一侧事务同时过期→整批零写；split 源并发软删→TARGET_NOT_FOUND 零写；delete/pin guard vs 推进→零写；**两个真实 merge 调用者**都过预检、仅一个提交；2 线程×5 并发写无孤儿；日志 `logs/pytest-concurrency-verbose.log` | `e229da632` |
| P2-C（**F0-2 修复项**） | DTO 静默把缺失必需字段解析为 null：`ParseGeometry` 把缺失 `geometry` 与显式 null 等同；`RegionPageTextProjection` 把缺失 `page_size` 当 null | 先要求属性**存在**（`TryGetProperty` 失败即 `FormatException`），再允许值为 null；`geometry`/`page_size` 缺失属性严格失败，显式 null（未知页/无 extent）仍合法 | `RegionWriteCommandTests.RegionTextProjection_RejectsMissingRequiredFields`（缺失 geometry / 缺失 page_size / 显式 null 合法） | `1798d2e00` |
| P2-D | `DB_FAILED` 被 `_guard_status_of` 映射成 `INPUT_REVISION_CHANGED`：数据库 busy/IO 故障在 wire 变成 conflict（“刷新后重试”） | `GuardStatus` 新增 `DB_FAILED`；`_guard_status_of` 把 `RegionCommitStatus.DB_FAILED` 映射到它，不再落入 conflict；既有 wire 消费方对非 APPLIED 非 conflict 抛 RuntimeError → `UNKNOWN`/internal/固定短语 `Region write failed`（无 SQLite 文本/路径） | `tests/core/test_region_db_failure.py`（4 用例）：service outcome 是 `GuardStatus.DB_FAILED`（非 conflict）且零写；wire `save_region_geometry` 返回 UNKNOWN/internal 固定文案；create 失败无孤儿；set_region_type 保持 internal | `23f707a1b` |
| P2-E | split `parts` 与 reorder 全页列表无上限：单 `BEGIN IMMEDIATE` 逐项写 revision + busy timeout 5s → 极大输入长写锁、其他写者 BUSY | 契约冻死并双侧强制上限：`MAX_REGIONS_PER_PAGE=500`（create/reorder）、`MAX_REGION_IDS_PER_BATCH=64`（merge）、`MAX_SPLIT_PARTS=64`、`MAX_GEOMETRY_POINTS=512`；Core 在任何持久化前 `INVALID_REQUEST`，service 对非 wire 调用同值 `ValueError`，C# Host 发帧前 `INVALID_ARGUMENTS` | `tests/core/test_region_limits.py`（6 用例）：split/merge/reorder/geometry 超限均零写拒绝；页上限 wire+service；短时独立写锁下正常写等待（bounded busy timeout）成功；`RegionWriteCommandTests.Dispatcher_RejectsOversizedBatches_BeforeAnyFrame` | `6c5a9f8c3` |
| 集成 | 合并 main 后 A-3 `CommandContractV11RTests` 要求注册表每条命令都被 A-3 契约声明，C077 仍是占位文本 | 把 C077 行改为真实命令名 `list_page_region_texts`（Region/core/minor 3，`PENDING(V11R-F0-2)`），节标题/说明同步 C067–C077；不改任何生产代码 | `CommandContractV11RTests` 全绿（聚焦 dotnet 85 passed） | `5f4d1884c` |

## 2. 真实交错测试怎么做的（P1-B 复核要点）

- 测试在 `RegionEditingService._commit_batch_or_raise` 上安装 barrier（monkeypatch，测试结束还原）：
  - **预检已通过**（`_require_region` / `_expected_current_ids` 都已执行），
  - 事务**尚未** `BEGIN IMMEDIATE`，
  - 主线程 `barrier.wait()` 后由工作线程用**独立 sqlite3 连接**（`sqlite3.connect(db_path)`，非 Core facade）
    在一个事务里推进 current 指针（插真实 revision + 移指针）或软删目标，`commit()` 后第二次 `barrier.wait()`，
  - 主线程随后进入真实 `BEGIN IMMEDIATE` 批次 —— 事务内重读发现变化 → conflict/TARGET_NOT_FOUND，整批回滚。
- 覆盖场景见 §1 P1-B；日志 `logs/pytest-concurrency-verbose.log`（7 PASSED，逐用例名）。
- 「两个调用者」用例让两个线程**都真实调用** `merge_regions` 并在 barrier 相遇，断言恰好一个成功、一个
  `TARGET_NOT_FOUND`，页面只有一套合并结果、源各 1 条 revision、无孤儿。

## 3. Gate（全部实测，日志在本目录 `logs/`）

环境：Windows 10.0.26100；Python 3.14.6；dotnet SDK 10.0.401（target net9.0）；pytest 9.1.1。

| # | 命令（工作目录） | Exit | 结果摘要 | 日志 |
|---|---|---|---:|---|
| G1 | `python -m pytest -q`（仓库根） | 0 | **2709 passed, 10 skipped, 2 warnings in 247.57s**（I1 后 2684；+25 I2 用例；0 failed） | `logs/pytest-full.log` |
| G2 | `python -m pytest -q <I2 + F0 相关 11 文件>` | 0 | **86 passed**（8 存活 + 7 并发 + 4 DB 失败 + 6 上限 + 既有 61） | `logs/pytest-region-i2.log` |
| G3 | `python -m pytest -v tests/core/test_region_concurrency.py` | 0 | **7 passed**（真实交错逐用例，见 §2） | `logs/pytest-concurrency-verbose.log` |
| G4 | `dotnet build NewManga.sln -warnaserror`（`apps/desktop-avalonia`） | 0 | **0 警告 / 0 错误** | `logs/dotnet-build.log` |
| G5 | `dotnet test NewManga.sln --no-build` | 0 | 全绿：ThemeEngine 189、Host 42+24skip、DesignSystem 67、CoreClient **119 passed**+22skip、App 232+6skip；0 failed | `logs/dotnet-test.log` |
| G6 | `dotnet test NewManga.sln --no-build --filter "RegionWriteCommandTests｜CommandParityContractTests｜CommandContractV11RTests"` | 0 | **85 passed / 0 failed**（含 P2-C/P2-E 用例 + A-3 契约对齐） | `logs/dotnet-test-region-i2.log` |

**诚实记录一次环境性失败**：首次 G5 运行时测试主机进程崩溃（`活动的测试运行已中止`，dotnet exit 1；
各项目已打印的通过摘要正常，App.Tests 只发现 166 用例而非 238）。原始日志保留在
`logs/dotnet-test-run1-hostcrash.log`。未改任何代码，立即复跑两次均 exit 0（238/238 App.Tests），
判定为测试主机环境 flake，不是本分支行为；复审可复跑 G5 验证。

skip 均为既有环境性 skip（缺 sidecar fixtur / QML 宿主等），与本返修无关。

## 4. 数据安全复核点（复审建议逐项核对）

1. **软删目标零写**：已软删 region 再 `merge_regions`/`split_region`/`delete_region`/`pin_revision` ⇒
   `TARGET_NOT_FOUND`；`deleted_at` 不被重写、无新 revision、无 part/merged 行（`test_region_target_liveness.py`）。
2. **事务内 live 重读**：`commit_region_batch` 第 1 步 `SELECT current_revision_id, deleted_at` 覆盖全部既有目标；
   软删条件 UPDATE 检查 `rowcount==1`；pin UPDATE 带 `EXISTS (... deleted_at IS NULL)`。
3. **真实并发零写**：第二连接在预检与提交间推进 current / 软删 ⇒ 冲突/not_found 且 revision/顺序/软删/pin 全不变
   （`test_region_concurrency.py`，日志 G3）。
4. **DB 故障语义**：`GuardStatus.DB_FAILED` 独立；wire UNKNOWN/internal 固定短语；不得被当 conflict。
5. **输入上限**：四类上限在 Core/Host 双侧同值；超限零写；正常写可在短时并发写锁下等待成功。
6. **历史/锁/协议**：未新增删除或 upsert 历史路径；锁双投影与 GAP-3 保持；C067–C077 minor=3；冻结 66 快照未编辑。
7. **F0-2 修复隔离**：P2-C 单独 commit（`fix(V11R-F0-2)`），不动 F0-1 写语义；F0-2 HEAD 仍可单独审/合并。

## 5. 复审入口

```powershell
git log --oneline f971ece07..HEAD     # F0-2 1 个 + I1 5 个 + merge main + A-3 集成 + I2 5 个 + docs
git diff c861fcba5..HEAD -- src apps/desktop-avalonia/src/NewManga.CoreClient
python -m pytest -q
python -m pytest -v tests/core/test_region_concurrency.py
python -m pytest -q tests/core/test_region_target_liveness.py tests/core/test_region_db_failure.py tests/core/test_region_limits.py
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln --no-build
dotnet test NewManga.sln --no-build --filter "RegionWriteCommandTests|CommandParityContractTests|CommandContractV11RTests"
```

复审结论请按 `doc/templates/REVIEW.md`；Owner 无 push 权限，最终由 Lead 集成。
