## 审查结论：`FAIL`

审查固定在 `c861fcba5aa3dd70fb8444cc14c6dc6ea607b395`。审查期间共享 worktree 的分支指针前移到了 `66c3b936`；我没有查看新 HEAD 的代码，下面的判断已用 `git show c861...:<path>` 复核。没有修改文件或 Git 状态，也没有重跑测试。

上一轮报告 `doc/reviews/V11R-F0-1-r1-codex.md` **不在这个固定 pin 的 Git tree 中**；以下逐项核对依据是你列出的五项问题、I1 README、契约和固定 pin 的代码与测试。

## 上一轮 5 项关闭状态

| 问题 | 状态 | 依据 |
|---|---|---|
| P1-1 create/merge/split 复合写原子性 | **CLOSED** | `commit_region_batch` 用单个 `BEGIN IMMEDIATE` 完成插入、revision/current 指针和源软删，异常时 rollback。[regions.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py:283>) 失败注入覆盖了 create 首 revision、merge 写入后软删失败、split 后续 part 失败，并检查零写及无孤儿。[test_region_atomicity.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/tests/core/test_region_atomicity.py:155>) |
| P1-2 多 region 乐观锁整批零写 | **PARTIAL** | 实现确实在事务内检查 expected current，并将 reorder 变更整批提交。[regions.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py:307>) 但检查没有覆盖“目标仍为 live”；并发删除不改变 current 指针，merge/split 仍可能基于已软删源再次提交，详见下方 P1。测试也没有真实交错。 |
| P1-3 merge/split 继承显式翻译锁 | **CLOSED** | merge/split 计算有效锁，并同步写入 region 与 text 两个投影。[service.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py:97>) 测试检查双投影和机器翻译锁保护路径。[test_region_lock_inheritance.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/tests/core/test_region_lock_inheritance.py:154>) |
| P2-4 delete/pin 检查与写入同事务 | **PARTIAL** | current 指针比较和软删/pin 写入已放入同一事务。[service.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py:572>) 但 live 状态仍只在事务外检查；软删更新没有 `deleted_at IS NULL` 条件。[regions.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py:431>) |
| P2-5 Host 发帧前 fail-closed | **CLOSED** | 新写命令检查归一化坐标 `[0,1]` 和正整数 revision/reading_order。[HostCommandDispatcher.cs](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs:628>) 边界测试覆盖越界坐标和非正整数。[RegionWriteCommandTests.cs](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/RegionWriteCommandTests.cs:270>) |

## 新问题

1. **[P1] 批事务未重核对目标仍为 live，可能重复 merge/split。**  
   [regions.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py:322>) 只读取并比较 `current_revision_id`；软删只按 `region_id` 更新，未检查 `deleted_at`。[regions.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py:377>) 若两个内部调用者都在首次提交前通过 `_require_region`，首个 merge/split 软删源之后，第二个批次仍会看到相同 current 指针并通过校验，可能再创建一组结果。delete/pin 也可能在目标已经软删后成功写入。当前 stdio 主循环逐行同步处理请求，因此普通单管道客户端不容易触发；但批事务的服务层并未保证调用者串行，这仍是数据完整性缺口。建议在事务中检查所有既有目标的 `deleted_at IS NULL`，软删使用条件更新并检查 `rowcount`，目标已删除时整批 rollback 并返回 `TARGET_NOT_FOUND`。

2. **[P1] 所谓并发回归测试没有真实交错，也没有覆盖事务内的多项冲突。**  
   `test_reorder_with_a_stale_second_expectation` 在服务预检阶段就用 revision `99` 触发冲突；事务重核对测试只改动一个 region，且先推进指针、再直接调用 committer。[test_region_batch_locking.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/tests/core/test_region_batch_locking.py:154>) [test_region_batch_locking.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/tests/core/test_region_batch_locking.py:194>) delete/pin 测试也直接调用 committer，先推进指针后再检查，没有 barrier 或第二连接。[test_region_transactional_guards.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/tests/core/test_region_transactional_guards.py:153>) 因此它们证明了“已过期指针在批次入口被拒绝”，但没有证明检查与写之间被同一事务隔离，也不会捕获上面的 `deleted_at` 缺口。建议用独立 SQLite 连接和同步 barrier，在服务预检后推进状态，再断言 revision、顺序、软删、pin 均为零写。

3. **[P2] C# DTO 将缺失的必需字段静默解析为 null。**  
   `ParseGeometry` 将 `geometry` 缺失和显式 `null` 等同处理；`RegionPageTextProjection.Parse` 也把缺失的 `page_size` 当作 null。[RegionTextProjection.cs](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RegionTextProjection.cs:103>) [RegionTextProjection.cs](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RegionTextProjection.cs:227>) 契约要求缺字段严格失败。[V11R_REGION_WRITE_CONTRACT.md](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/doc/contracts/V11R_REGION_WRITE_CONTRACT.md:381>) 现有“malformed geometry”用例实际传入的是空 `regions` 数组，没有验证缺字段。[RegionWriteCommandTests.cs](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/RegionWriteCommandTests.cs:461>) 建议先强制要求属性存在，再允许其值为 null；补测缺失 `geometry` 与 `page_size`。

4. **[P2] 几何保存的数据库错误会被映射成乐观锁冲突。**  
   SQLite seam 会把 busy/数据库错误返回为 `DB_FAILED`。[regions.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py:198>) 但 `_guard_status_of` 对除 `LOCK_CHANGED` 外的状态一律映射为 `INPUT_REVISION_CHANGED`；`save_region_geometry` 因而会把数据库故障报告为冲突，而不是 `UNKNOWN`。[service.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py:129>) [core_service.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/bootstrap/core_service.py:2543>) 建议保留 `DB_FAILED` 的独立错误路径，让 wire 层返回固定安全的内部错误。

5. **[P2] batch 输入无数量上限，锁持有时间随输入增长。**  
   split 的 `parts` 和 reorder 的全页 region 列表均没有最大数量限制；批事务在一个 `BEGIN IMMEDIATE` 内逐项写 revision。[core_service.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/bootstrap/core_service.py:2627>) [regions.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py:307>) 数据库 busy timeout 为 5 秒。[connection.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/connection.py:57>) 没发现嵌套 `BEGIN IMMEDIATE` 或明显死锁路径；风险是极大输入下的长写锁和其他写者 `SQLITE_BUSY`。建议定义并执行 region/part/vertex 上限，并用并发写入做压力验证。

## 已核实正确

- create、merge、split、reorder、delete、pin 的写入都进入同一个 batch seam；rollback 路径清晰，没有在 seam 内再次调用会开启事务的 repository 写方法。
- 失败注入是在生产 SQLite assembly 上通过 `_insert_revision` / `_soft_delete_row` 注入异常；create、merge、split 的断言确实检查了数据库状态，不只是检查返回值。[test_region_atomicity.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/tests/core/test_region_atomicity.py:155>)
- merge/split 锁继承会把有效翻译锁写入两个投影；机器翻译测试检查了锁定后不覆盖文本。
- C077 的 Core 实现是真实页级投影：文本不补占位，过滤 id 会拒绝未知/跨页/软删 region，空页和未知 page 返回空数组；测试逐字段对照真实 revision 与 SQLite 状态。[core_service.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/bootstrap/core_service.py:2174>) [test_region_text_read_command.py](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/tests/core/test_region_text_read_command.py:137>)
- pin 操作只更新 `is_pinned`，delete 只写 `deleted_at`；这两个命令本身没有删除或改写 revision 历史。显式 page/book purge 是单独的既有删除路径，不属于这两个命令的 append-only 保证。

## UNVERIFIED 与关闭/合入决定

- 我没有重跑 pytest 或 dotnet；固定 pin 的证据 README 记录了全绿日志，但这不是本轮独立执行结果。尤其没有真实并发 barrier 测试或 `SQLITE_BUSY` 压力测试。
- 固定 pin 中找不到上一轮 Review 文件；逐项状态按你提供的问题摘要与代码核对。固定 pin 中也没有 `doc/tasks/V11R-F0-2.md`，且 `STATUS.md` 只登记 F0-1；因此 GAP-2 的功能可以说已补齐，但 F0-2 的正式 Task 生命周期尚不能据此关闭。[STATUS.md](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/doc/STATUS.md:6>) F0-1 Task 仍是 `blocked`、`delivery_head` 为空、证据状态 pending。[V11R-F0-1.md](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/doc/tasks/V11R-F0-1.md:6>)
- **是否可合入 main：否。F0-1 是否可 closed：否。F0-2 是否可 closed：否**；其中 GAP-2 功能状态可标为 `CLOSED`，但 DTO 严格解析问题和 Task 登记缺口仍需收口。

如果之后分开集成，建议顺序是 **F0-1（含 I1 修复及新增并发修复）先，F0-2 后**。当前提交历史把 F0-2 `089cdb761` 放在 I1 修复之前；拆成两个合并 commit 需要 DSH 重整 cherry-pick/rebase，并对共享的 service、dispatcher 和契约重新验证。下一步建议 DSH 先将 F0-1 保持 blocked，安排实现方修复 P1 并补真实交错测试，再进行独立复审。