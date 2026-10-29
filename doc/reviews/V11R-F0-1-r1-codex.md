# 结论：FAIL

审查固定在 `ba59a6c0d..f971ece0785fb3fd32431b1b5f6c51daebc0541e`。三个 P1 问题分别涉及复合写非原子、并发冲突不保证整批零写，以及 merge 后显式翻译锁丢失；**当前不可合入 main**。下列行号均对应 `f971ece` 的 Git 对象。

## 逐项结论

| 审查项 | 结论 |
|---|---|
| 数据安全 | 软删除保留源历史，单 revision commit seam 正确；create/merge/split 的多步写入可能留下部分状态。 |
| 乐观锁 | 调用前已过期会返回 `INPUT_REVISION_CHANGED`；并发写入时，多 region 命令不能保证整批零写，delete/pin 也有检查与写入间隙。 |
| 锁语义 | `set_region_lock` 会生成 revision 并同步双投影；merge 可丢失显式 `translation_locked`，split 只复制文本级锁。 |
| 协议 | 十条命令的名称、Region 域、Core 同名路由和 `minor=3` 一致；冻结的 66 命令快照未改。Host 发帧前校验不完整。 |
| 错误边界 | `INVALID_REQUEST`、`INPUT_REVISION_CHANGED`、`TARGET_NOT_FOUND`、`UNKNOWN` 映射一致；错误响应使用安全短语，没有发现路径或异常原文泄漏。 |
| 测试 | Python 测试使用生产 Core 装配、临时 SQLite 和 JSON-lines dispatch，并断言实际状态；但没有覆盖并发交错和中途失败。 |
| 权限与文件 | create 校验 page 存在，merge/reorder 校验 page 归属；写命令不访问源文件或 Managed Copy 路径。单 region 命令按 `region_id` 定位，项目没有定义逐书 ACL。 |

## 问题清单

1. **[P1]** [service.py:385–390、663–673、708–715](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py>)；[regions.py:117–133、149–155、201–275](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py>) — create/merge/split 不是一个原子操作。`add_region()` 先独立提交；revision seam 随后单独提交；merge 再逐个软删源，split 逐个提交 part 后才软删源。**复现**：在 create 的 revision seam 失败时，region 行已留下但没有首 revision/current pointer；merge 的软删中途失败会同时留下 merged region 和仍 live 的源；split 的第二个 part 失败会留下 live 源和已创建的 part。建议把实体插入、revision/current pointer 更新及源软删纳入同一个 `BEGIN IMMEDIATE` 事务。

2. **[P1]** [service.py:320–343、608–673、722–759](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py>)；[core_service.py:1078–1101](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/bootstrap/core_service.py>) — `expected_revisions` 只在写前检查；run scheduler 在独立线程运行。merge/split 后续没有在事务内重新核对源 revision；reorder 则每个 region 各自提交。**复现**：reorder 两个 region 时，第一条 revision 提交后，pipeline 更新第二个 region；第二条 seam 返回冲突，但第一条已经写入，调用方收到 conflict 却留下部分排序。merge/split 则可能基于旧快照继续成功并软删已被更新的源。建议在一个批次事务中重新核对所有输入 revision，并将整批写入或整批回滚。

3. **[P1]** [service.py:639–661、675–715](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py>)；[entities.py:239–245](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/domain/regions/entities.py>)；[tasks/service.py:527–531](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/tasks/service.py>) — merge 不继承“仅显式设置”的翻译锁。新 `Region` 默认两处锁都为 false；merge 只有在 `manual_edited` 为真时才复制文本级锁，而且仍没设置 region 级投影。**复现**：对 `manual_edited=false` 的源 region 调 `set_region_lock(translation_locked=true)`，再 merge；新 region 成为未锁定状态，后续 translation step 会被调度并可覆盖合并后的 machine translation。split 则只把锁复制到 `part.text`，region 级锁仍为 false，pipeline 会启动翻译；最终写入保护可挡住覆盖，但会产生多余候选。建议 merge/split 都继承有效锁，并一致写入 region 与 text 两个投影；增加显式锁场景测试。

4. **[P2]** [service.py:311–318、400–414、1048–1052](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/application/editing/service.py>)；[regions.py:183–195](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/src/infrastructure/sqlite/regions.py>) — delete/pin 的 `expected_revision` 只在独立读检查中验证，随后分别写 `deleted_at` 或 `is_pinned`，没有与 current pointer 在同一事务内二次校验。pipeline 写入可在两步之间改变 current revision，旧请求仍会成功。建议在同一 `BEGIN IMMEDIATE` 事务中校验 current pointer 并执行软删或 pin 更新。

5. **[P2]** [HostCommandDispatcher.cs:579–619、893–905](<G:/CODEX/New Manga.workspace/worktrees/V11R-F0-REGION-WRITE/apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs>) — Host 校验了点数、坐标类型和有限值，但没拒绝超出 `[0,1]` 的坐标；通用 `WriteOptionalInt64` 也接受 `expected_revision=0`、`reading_order=-1` 等领域非法值。这些值会先发到 Core，再由 Core 返回 `INVALID_REQUEST`，没有满足发帧前 fail-closed。建议按命令校验归一化范围和正整数，并补对应 C# 边界用例。

## 已核实正确

- delete、merge、split 对源 region 使用软删，源 revision/history/current/pinned 行没有硬删；pin 只更新 `is_pinned`，不新增 revision 或移动 current pointer。
- 单 region revision 写的 `commit_region_revision` 在 `BEGIN IMMEDIATE` 内重读 current，冲突时 rollback；geometry、manual translation、confirm、lock 写经此 seam。
- 十条命令已注册到 Region 域，Core 命令同名、minor 为 3；66 条冻结快照没有出现在变更文件清单中。
- typed error 使用固定安全文本；`UNKNOWN` 不回传原始异常，not-found 消息也不回显 ID 或路径。
- Python 测试直接使用 `assemble_production_core(tmp_path / "data")` 和 SQLite，并断言 revision、删除状态与 pin 行为；存档日志记录 targeted pytest 38 通过、CoreClient 测试 53 通过、build 0 warning/0 error。**本次未重跑测试**，只读了代码和存档日志。
- `GAP-2` 在 `f971ece` 中诚实标记为 OPEN：没有页面初载文本读取通道，并明确要求 UI 不得伪造文本。空字符串写入会清空人工稿，因此 UI 不能把“读不到”表示成“已读取的空稿”。

## UNVERIFIED 与建议验证

- **UI 空文本风险**：本次提交不含 UI 变更，无法验证未来 Studio 页面是否会把缺失文本当空值保存。页面接入时应以已有非空人工稿验证：未读取文本时不能发送清空写入，读取到真正空稿时才允许清空。
- **并发与故障路径**：现有测试证明调用前已过期会零写，但没有测试写入期间 revision 改变或提交中途失败。修复后应在临时 SQLite 上用同步 barrier 和故障注入验证冲突零写、批次全回滚、以及不会留下无 current revision 的 region 行。
- **page/book 作用域**：merge/reorder 会校验目标 page 的 live region 集合；单 region 写命令只带 `region_id`。项目未定义按书授权的 ACL；若 UI 页面上下文需要承担作用域检查，应在 Host/UI 集成中验证错页 ID 会被拒绝。
- 当前工作树在审查过程中出现未提交的 F0-2 读面改动（含 `RegionTextProjection.cs`、`test_region_text_read_command.py` 和 F0-2 证据）。它们不属于 `f971ece`，本报告已按 Git 对象排除且未触碰。

## 是否可合入 main

**否。** 阻断项是问题 1–3；问题 4–5 也应在集成前处理。Task 卡在被审提交中仍为 `blocked`，`delivery_head` 为空，因此这份审查结论不等于 Task 已获批准。建议下一步由 DSH/实现方修复并增加失败注入、并发和锁继承测试，发布新的固定 HEAD 后再做独立复审；F0-2 读面改动应另行固定并审查。