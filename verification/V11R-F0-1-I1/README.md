# V11R-F0-1 I1 有界返修证据（独立审查 r1 FAIL 处置）

- 审查报告：`doc/reviews/V11R-F0-1-r1-codex.md`（独立通道，结论 FAIL：3×P1 + 2×P2；不在本分支内，由 main 持有）
- 审查固定点：`ba59a6c0d..f971ece07`（F0-1 delivery head）
- 本分支：`v11r/region-write`
  - F0-1 HEAD：`f971ece0785fb3fd32431b1b5f6c51daebc0541e`
  - F0-2 HEAD（独立提交，另行审查）：`089cdb761f7d015688cd273d40a9c9fae668c154`
  - **I1 HEAD：见 Handoff / 本证据提交后的 `git log --oneline -6`**（I1 提交均在 F0-2 HEAD 之上，未混入 F0-2）
- Owner：core-writer（**未自审**；复审走独立通道，未通过前不合入 main）
- 契约：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md` **v1.2**（§1.4 事务内重核对、§2 逐命令、§3 不变量、§8 验证要求、§9 变更记录）

## 0. 处置原则

- 每个问题独立 commit（`fix(V11R-F0-1): ...`），SHA 见 §1 表；
- 修复复用既有原子 commit seam 扩展（`commit_region_batch`，单 `BEGIN IMMEDIATE`），不新增第二写路径；
- 失败注入与并发模拟均在**真实生产 SQLite assembly**（`tmp_path`）上执行，测试只通过公开 JSON-lines 命令或
  committer/use case 断言，不 mock 事务语义；
- 未降低 GAP 诚实性：GAP-1「本任务新增」标注保留；GAP-2 在 F0-1 中仍按原始事实记录、F0-2 标 CLOSED；
  GAP-3 的「既有 manual save 未改」显式保留。

## 1. 逐项处置表（问题 → 修法 → 新增测试 → 证据）

| # | 审查问题 | 修法 | 新增测试（真实 SQLite） | Commit |
|---|---|---|---|---|
| P1-1 | create/merge/split 复合写非原子：可留下无 current revision 的孤儿 region、merged 与 live 源共存、live 源+半套 part | 新增 `RegionRevisionCommitter.commit_region_batch`：新 region 行+首 revision+current 指针、更新 region 的新 revision+指针、源软删、pin 旗标**全部在一个 `BEGIN IMMEDIATE`**；create/merge/split 改走 `_commit_batch_or_raise` | `tests/core/test_region_atomicity.py`：注入 `_insert_revision` / `_soft_delete_row` 失败，断言 region 行 0、源保持 live、无孤儿行（`current_revision_id` 必须可解析且每 region 至少 1 条 revision）；成功路径同样断言不变量 | `a3aed053a` |
| P1-2 | 多 region 乐观锁仅写前检查：reorder 可部分写入；merge/split 可基于旧快照软删已更新的源 | 多 region 批处理在**事务内**先重读并比较全部 expected current 指针，再执行任何写；任一过期整批回滚、零写。reorder 的未变更 region 也纳入 expected 检查 | `tests/core/test_region_batch_locking.py`：三个 region 中第二个 expected 过期 → 无 region 移动、无 revision 追加；模拟 pipeline 在预检与提交之间推进 current（直接 `commit_region_batch`）→ `INPUT_REVISION_CHANGED` 且 revision 数不变 | `f7afca5f7` |
| P1-3 | merge/split 丢失显式翻译锁：merge 仅 `manual_edited` 时复制文本锁、不写 region 级；split 仅复制文本级 | `effective_region_locks()`：源 region 级 OR 文本级锁任一为真即视为有效锁；`_apply_effective_locks()` 一致写入新 region 的两个投影；merge/split 均继承 | `tests/core/test_region_lock_inheritance.py`：`manual_edited=false` 的源显式 `set_region_lock(translation_locked=true)` 后 merge/split，断言两个投影均为 true；region/inpaint 锁继承；`apply_machine_translation` 返回 `lock_changed` 且不覆盖合并文本；wire 级 `list_page_region_texts` 复核 | `6dfc0cd51` |
| P2-4 | delete/pin 的 expected 检查与写入不在同一事务 | delete 的 current 比较+`deleted_at`、pin 的 current 比较+`is_pinned` 走同一 `commit_region_batch` 事务；pin 目标 revision 存在性为 append-only 历史下的无竞态前置校验；移除遗留的 read-then-write helper | `tests/core/test_region_transactional_guards.py`：模拟并发推进 current 后，delete 返回冲突且 `deleted_at IS NULL`；pin 返回冲突且 `is_pinned=0` | `cead08188` |
| P2-5 | Host 发帧前 fail-closed 不完整：坐标越界、`expected_revision=0`、`reading_order=-1` 被放行 | `HostCommandDispatcher`：几何坐标必须在 `[0,1]`；`expected_revision`/`reading_order` 用 `WriteOptionalPositiveInt64`（present ⇒ >0）；`revision_no` 用 `RequirePositiveInt64`；`expected_revisions` 值必须 >0 | `RegionWriteCommandTests` 新增 13 条边界用例（负/越界坐标、reading_order 0/-1、多命令 expected_revision 0、expected_revisions 0、revision_no 0/-3），断言发帧前 `INVALID_ARGUMENTS` | `ea568b09b` |

## 2. Gate（全部实测，日志在本目录 `logs/`）

环境：Windows 10.0.26100；Python 3.14.6；dotnet SDK 10.0.401（目标 net9.0）；pytest 9.1.1。

| # | 命令（工作目录） | Exit | 结果摘要 | 日志 |
|---|---|---|---:|---|
| G1 | `python -m pytest -q`（仓库根） | 0 | **2684 passed, 10 skipped, 2 warnings in 225.22s**（F0-2 后 2672；+12 I1 用例；0 failed） | `logs/pytest-full.log` |
| G2 | `python -m pytest -q tests/core/test_region_atomicity.py tests/core/test_region_batch_locking.py tests/core/test_region_transactional_guards.py tests/core/test_region_lock_inheritance.py tests/core/test_region_write_commands.py tests/core/test_region_text_read_command.py tests/editing/test_region_write_guards.py` | 0 | **61 passed**（12 I1 + 11 F0-2 读面 + 31 F0-1 wire + 7 F0-1 guard） | `logs/pytest-region-i1.log` |
| G3 | `dotnet build NewManga.sln -warnaserror`（`apps/desktop-avalonia`） | 0 | **0 警告 / 0 错误** | `logs/dotnet-build.log` |
| G4 | `dotnet test NewManga.sln --no-build` | 0 | 全绿：App 137/137、Host 39 passed+21 skipped、CoreClient **111 passed**+22 skipped；0 failed | `logs/dotnet-test.log` |
| G5 | `dotnet test NewManga.sln --no-build --filter "RegionWriteCommandTests|CommandParityContractTests"` | 0 | **77 passed / 0 failed**（F0-2 后 64；+13 P2-5 边界用例） | `logs/dotnet-test-region-i1.log` |

skip 均为既有环境性 skip（缺 AC11 sidecar / S4 region fixture），与本返修无关；无失败用例。

机器可读：`dotnet-evidence/commands/v11r-region-write-registration.json`、
`dotnet-evidence/commands/parity-contract.json`、`commands.json`（本目录）。

## 3. 数据安全复核点（复审建议逐项核对）

> **可勾选复审清单**：`REVIEW_CHECKLIST.md`（每条含断言点 / 文件:行 / 期望结果 / 可复跑测试，
> 供 Reviewer 与 L4 直接复用）。**消费指南**：`CONSUMER_GUIDE.md`（合并后 Studio Page 如何调用
> C067–C077、何时带 `expected_revision`、失败如何处理，ui-studio 使用）。

1. **无孤儿**：`SELECT COUNT(*) FROM regions r LEFT JOIN region_revisions rev ON
   rev.region_revision_id=r.current_revision_id WHERE r.current_revision_id IS NULL OR
   rev.region_revision_id IS NULL` 在失败注入后必须为 0（`_assert_no_orphan_regions`）。
2. **整批零写**：冲突/失败后不得出现任何新 revision、任何 region 移动/软删、任何 pin 变化；
   I1 用例直接断言相关行数/指针/`deleted_at`/`is_pinned`。
3. **锁继承**：显式锁经 merge/split 后两个投影均为 true，且 `apply_machine_translation` 走
   `lock_changed`（不覆盖文本）。
4. **current/pinned/历史**：未新增删除或 upsert 历史路径；pin 仍只翻 `is_pinned`；软删仍只写
   `deleted_at`。
5. **协议**：冻结 66 快照未编辑；C067–C077 仍 minor=3、零 protocol bump。
6. **Host 边界**：领域非法值（坐标越界/非正整数）在发帧前 `INVALID_ARGUMENTS`。
7. **page/book 作用域**：契约 §3.1 已写明——单 region 命令按 id 定位；项目未定义按书 ACL，
   本任务不新增假授权；跨书 id 授权由 Host 未来 ACL 承担；UI 只传自己已加载的 id。

## 4. 复审入口

```powershell
git log --oneline f971ece07..HEAD          # F0-2 一个提交 + I1 五个 fix 提交 + 本证据提交
git diff f971ece07..HEAD -- src/ apps/desktop-avalonia/src/NewManga.CoreClient
python -m pytest -q
python -m pytest -q tests/core/test_region_atomicity.py tests/core/test_region_batch_locking.py tests/core/test_region_transactional_guards.py tests/core/test_region_lock_inheritance.py
cd apps/desktop-avalonia
dotnet build NewManga.sln -warnaserror
dotnet test NewManga.sln --no-build
```

复审结论请按 `doc/templates/REVIEW.md`，明确 P1/P2 是否关闭、是否放行 DSH 集成；
Owner 无 push 权限，最终由 Lead 集成。
