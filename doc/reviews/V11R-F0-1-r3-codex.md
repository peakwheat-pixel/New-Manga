# 结论：FAIL

固定 pin 与 `HEAD` 均为 `1a457111cd2cb68321947b5359a2ad235f13fe2e`，工作树干净。**本轮未运行测试**；G1/G3/G5 只核对了存档日志，日志对应代码提交 `6c5a9f8c3`，之后到 pin 的提交仅改契约与证据文件。

r2 报告 `doc/reviews/V11R-F0-1-r2-codex.md` 不在此 pin 的文件树或可见 Git 历史中。以下按题面列出的五项和 [I2 README](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/verification/V11R-F0-1-I2/README.md:1>) 核对；无法校验原报告的完整措辞。

## r2 五项关闭情况

| 项目 | 状态 | 核对依据 |
|---|---|---|
| P1-A 目标存活 | **CLOSED（批量写 seam）** | 事务内重读 `deleted_at` 与 current pointer，条件软删并要求 `rowcount == 1`；已删目标映射为 `TARGET_NOT_FOUND`。见 [regions.py:309](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py:309>)、[regions.py:378](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py:378>)、[service.py:427](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py:427>)。单 revision 写入仍有存活检查缺口，列为新问题。 |
| P1-B 真实交错测试 | **CLOSED** | barrier 在服务预检后、提交 seam 前；侧写线程用独立 SQLite 连接，并提交真实 current 推进或软删。双 merge 用例让两个调用都越过预检，再断言一成一败和零重复结果；线程连接由 `ThreadRoutedConnection` 按线程路由。见 [test_region_concurrency.py:92](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/tests/core/test_region_concurrency.py:92>)、[test_region_concurrency.py:107](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/tests/core/test_region_concurrency.py:107>)、[test_region_concurrency.py:379](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/tests/core/test_region_concurrency.py:379>)、[connection.py:149](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/connection.py:149>)。未见测试在预检前串行化。 |
| P2-C DTO 缺字段严格失败 | **CLOSED** | 缺 `geometry`、`page_size` 会失败；显式 `null` 仍合法。见 [RegionTextProjection.cs:103](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RegionTextProjection.cs:103>)、[RegionTextProjection.cs:241](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/apps/desktop-avalonia/src/NewManga.CoreClient/Commands/RegionTextProjection.cs:241>)、[RegionWriteCommandTests.cs:517](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/apps/desktop-avalonia/tests/NewManga.CoreClient.Tests/Commands/RegionWriteCommandTests.cs:517>)。 |
| P2-D DB_FAILED 独立且 wire 安全 | **CLOSED** | `DB_FAILED` 不再落入 conflict；存档用例核对 wire 为 `UNKNOWN/internal`、固定文案且不泄漏 SQLite 错误。见 [service.py:134](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py:134>)、[test_region_db_failure.py:117](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/tests/core/test_region_db_failure.py:117>)。 |
| P2-E 输入上限双侧一致且零写 | **PARTIAL** | Core 与 C# 上限同为 500/64/64/512，wire 超限在写前拒绝；但直接调用 service 的几何写入没有顶点数上限，且创建页上限是事务外预检，可并发越界。见 [region_canvas.py:38](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/region_canvas.py:38>)、[HostCommandDispatcher.cs:33](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs:33>)。 |

## 新问题

- **[P1] 单 revision 写入可在目标软删后仍提交。** `_require_region` 只在提交前检查存活；事务内的 `commit_region_revision` 只读 current pointer 和锁，未读 `deleted_at`，随后按 `region_id` 更新。若保存几何、译文或锁的调用先通过预检，另一连接随后删除/合并该 Region，旧调用仍可能插入新 revision 并返回成功；该 revision 留在软删目标上，不出现在 live 列表。见 [service.py:362](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py:362>)、[regions.py:205](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py:205>)、[regions.py:254](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py:254>)。应在此 seam 内检查存活并返回 typed `TARGET_NOT_FOUND`，增加独立连接交错测试。
- **[P2] 500 个 live Region 上限有并发越界窗口。** service 和 Core 都在事务外数 live rows；两个调用者在已有 499 个时都可能通过预检，随后各自成功插入，达到 501。批事务没有重查页数；这也会使“全页 reorder”超过 500 项而被拒绝。见 [service.py:552](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py:552>)、[core_service.py:2484](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/bootstrap/core_service.py:2484>)、[regions.py:307](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py:307>)。
- **[P2] 非 wire service 调用绕过顶点上限。** `save_geometry` 接受任意 `RegionGeometry`，`split_region` 只限制 part 数；`MAX_GEOMETRY_POINTS` 只在 Core 请求解析器与 Host dispatcher 检查。见 [service.py:855](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py:855>)、[service.py:979](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py:979>)、[core_service.py:2378](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/bootstrap/core_service.py:2378>)。这与 I2 README 所述“service 非 wire 调用同值拒绝”不符。

## 已核实正确

批量事务的软删保留 Region 行和 revision 历史，revision 写入仍追加新行；merge/split 的有效锁继承到两个投影，现有测试覆盖显式翻译锁。未见 Managed Copy 源文件访问或改写回归。C# 对 `geometry`、`page_size` 的缺失与显式 null 区分正确。

C077 已声明为真实命令 `list_page_region_texts`。总命令契约保留 `PENDING(V11R-F0-2)`，并说明须合入 main、由 DSH 签发后才冻结；本分支尚未集成，因此这个状态是诚实的，不是占位命令。

## UNVERIFIED

- 最大 reorder（500 项）和最大 split（64×512 点）的持锁时长未验证。5 秒 `busy_timeout` 是锁等待上限，不是事务执行时限；现有锁测试只验证短锁等待。建议在最大输入下测持锁时间，并让独立 writer 同时竞争。
- I2 日志可核对为 7 个并发用例通过及 build/test 通过，但本轮未重跑。

## 关闭判断

- **F0-1：不可 closed。** 新的 P1 单 revision 存活缺口，以及 P2-E 的两个上限缺口未解决。
- **F0-2：代码子范围可通过；Task lifecycle 暂不可正式 closed。** P2-C 已关闭，但当前它依赖的 F0-1 仍 blocked，`STATUS.md` 仍列 F0-2 进行中，pin 中也没有独立 F0-2 Task 卡。
- **整支：不可合入 main。** F0-1 尚有未关闭问题，且 F0-1 Task 卡仍为 `blocked`。

下一步建议：修复单 revision 的事务内存活检查、把页数上限移入原子写路径、在 service 层补顶点上限，并为这三条缺口增加并发/边界用例；完成后固定新 pin 再做独立复审。

## Standards

未发现违反仓库明确规范的情况。发现一项 **[P3，判断性 smell]**：`RegionTextProjection.cs` 第 203 与 280 行的 `RequireInt` 实现重复，可考虑复用 helper。

## Spec

本轮 Spec 发现 3 项：最高为 **P1**，另有两项 **P2**；r2 五项中四项关闭、一项部分关闭。C077 的 `PENDING` 状态符合尚未合并/签发的流程定义。

Standards 轴有 1 项 P3 判断性 smell；Spec 轴有 3 项，最严重为 P1。