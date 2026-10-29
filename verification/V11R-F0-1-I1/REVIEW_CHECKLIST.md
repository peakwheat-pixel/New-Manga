# V11R-F0-1 I1 复审可勾选清单（Reviewer / L4 复用）

- 被审代码固定点：`c861fcba5aa3dd70fb8444cc14c6dc6ea607b395`（I1 HEAD；F0-2 为 `089cdb761`，F0-1 为 `f971ece07`）
- 契约：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md` v1.2
- 审查报告 r1：`doc/reviews/V11R-F0-1-r1-codex.md`（main）
- 用法：逐条勾选；每条含「断言点 / 文件:行 / 期望结果 / 可复跑测试」。行号对应上述固定点；若上游合并导致偏移，
  以代码符号名（函数/记录名）为准。
- 停止条件：A1–A12 全部勾选 + B1–B5 SQL 不变量通过 + C1–C4 通过 + D1–D5 exit 0，方可判 PASS；
  任一条不满足 → 记录 FAIL 条目（文件:行 + 复现命令 + 实际结果）。

## A. 逐项问题关闭（P1/P2）

### A1–A3 P1-1 复合写全有或全无

- [ ] **A1** `commit_region_batch` 在同一事务内先校验所有 expected、再执行全部写；异常/冲突 rollback。
  文件：`src/infrastructure/sqlite/regions.py:283`（`commit_region_batch`）；`src/application/editing/ports.py:81`（protocol）。
  期望：函数体内只有一个 `BEGIN IMMEDIATE`（行 283 起），expectations 循环在任何 `_insert_region_row/_insert_revision/_soft_delete_row` 之前；`except` 分支 `conn.rollback()` 并返回 `DB_FAILED`。
  测试：`tests/core/test_region_atomicity.py:155/176/201`。
- [ ] **A2** create 失败不留下无 current revision 的孤儿 region 行。
  文件：`src/application/editing/service.py:519`（`create_region`）；`regions.py:412`（`_insert_region_row`）。
  期望：注入 `_insert_revision` 异常后 service 抛 `RuntimeError`，`regions` 表该 page 行数 = 0；每 region 行 `current_revision_id` 均可关联到 `region_revisions`。
  测试：`test_region_atomicity.py:155`（注入点 112/78 辅助断言 `_assert_no_orphan_regions`）。
- [ ] **A3** merge/split 失败不留下「merged/live 源共存」或「live 源 + 半套 part」。
  文件：`service.py:853`（merge）、`service.py:933`（split）；`regions.py:431`（`_soft_delete_row`）。
  期望：merge 注入源软删异常 → 两个源仍 live、merged 不存在；split 第二次 `_insert_revision` 注入异常 → 源仍 live、part 行数 0。
  测试：`test_region_atomicity.py:176`、`:201`。

### A4–A5 P1-2 多 region 乐观锁整批零写

- [ ] **A4** reorder 用整批 batch：变更 region 的 update + 未变更 region 的 expected check 都进同一事务。
  文件：`service.py:994`（`reorder_regions`）；`regions.py:283`（batch 中 `updated_regions`/`expected_current_checks`）。
  期望：请求内存在任一过期 expected → `RegionRevisionChanged`，无 region 移动、无新 revision。
  测试：`tests/core/test_region_batch_locking.py:154`。
- [ ] **A5** 事务内重读（防 TOCTOU）：预检之后、提交之前 current 指针被并发推进 → batch 返回 `INPUT_REVISION_CHANGED` 且零写。
  文件：`regions.py:283` 的 expectations 段落（先 `SELECT current_revision_id ...` 再写）。
  期望：直接 `commit_region_batch(updated_regions=[...])`（expected 为旧 id）返回 `RegionCommitStatus.INPUT_REVISION_CHANGED`；revision 总数不变。
  测试：`test_region_batch_locking.py:194`（真实第二 revision + 指针推进于 `_advance_current_revision`，见 `test_region_atomicity.py:112` 同构 helper）。

### A6–A8 P1-3 锁继承

- [ ] **A6** merge 继承有效锁并写双投影（region 列 + text_json），显式锁不因 merge 丢失。
  文件：`service.py:97`（`effective_region_locks`）、`service.py:115`（`_apply_effective_locks`）、`service.py:853`（merge 调用点）。
  期望：源显式 `set_region_lock(translation_locked=True)`（manual_edited=False）→ merge 后 `stored.translation_locked is True` 且 `stored.text.translation_locked is True`。
  测试：`tests/core/test_region_lock_inheritance.py:154`。
- [ ] **A7** split 每个 part 继承有效锁并写双投影。
  文件：`service.py:933`（split 调用点）。
  期望：source 显式锁 → 两个 part 的两个投影均 True。
  测试：`test_region_lock_inheritance.py:182`。
- [ ] **A8** 锁继承后机器翻译不覆盖文本（走 lock/candidate 通道）。
  文件：`service.py:97` 采用「region OR text」判定；`service.py` `apply_machine_translation` 的 `translation_locked` early return（既有）。
  期望：`apply_machine_translation(merged_id, ...)` 返回 `outcome.status.value == "lock_changed"`，`machine_translation` 仍为空。
  测试：`test_region_lock_inheritance.py:154`（含 region/inpaint 继承在 `:203`；wire 复核在 `:233`）。

### A9–A10 P2-4 delete/pin 同事务

- [ ] **A9** delete 的 current 比较与 `deleted_at` 写入同一 batch 事务；过期零写。
  文件：`service.py:557`（`delete_region`）；`regions.py:283`（`soft_delete_region_ids`）。
  期望：并发推进 current 后 `commit_region_batch(soft_delete_region_ids=[(rid, stale_id)])` → `INPUT_REVISION_CHANGED` 且 `deleted_at IS NULL`。
  测试：`tests/core/test_region_transactional_guards.py:153`。
- [ ] **A10** pin 的 current 比较与 `is_pinned` 更新同一 batch 事务；目标 revision 存在性为 append-only 下的无竞态前置校验。
  文件：`service.py:1316`（`set_revision_pinned`）；`regions.py:283`（`revision_pins`）。
  期望：并发推进 current 后返回 `INPUT_REVISION_CHANGED` 且目标行 `is_pinned=0`；未知 revision_no → `TARGET_NOT_FOUND`（wire）。
  测试：`test_region_transactional_guards.py:169`；`tests/core/test_region_write_commands.py:822`。

### A11–A12 P2-5 Host 发帧前域校验

- [ ] **A11** 归一化坐标越界在 Host 侧被拒（不依赖 Core 拒绝）。
  文件：`apps/desktop-avalonia/src/NewManga.CoreClient/Commands/HostCommandDispatcher.cs:628`（`WritePointArray` 的 `[0,1]` 检查，约行 655–670）。
  期望：`create_region`/`save_region_geometry`/`split_region` 传 `-0.1` 或 `1.2` → `HostCommandInvalidArgumentsException`（code `INVALID_ARGUMENTS`），无 Core 帧。
  测试：`RegionWriteCommandTests.Dispatcher_RejectsInvalidArguments_WithTypedCode` 新增边界行。
- [ ] **A12** `expected_revision`/`reading_order`/`revision_no`/`expected_revisions` 值必须为正整数。
  文件：`HostCommandDispatcher.cs:761`（`RequirePositiveInt64`）、`:990`（`WriteOptionalPositiveInt64`）、`:686`（`WriteOptionalRevisionsMap`）。
  期望：0 或负数 → `INVALID_ARGUMENTS`；合法值 payload 与契约 §2 完全一致。
  测试：同上 theory + `Dispatcher_WritesExactlyTheCoreValidatedPayload`。

## B. SQL 不变量（可直接在临时 assembly 上执行；期望值）

- [ ] **B1** 无孤儿：`SELECT COUNT(*) FROM regions r LEFT JOIN region_revisions rev ON rev.region_revision_id=r.current_revision_id WHERE r.current_revision_id IS NULL OR rev.region_revision_id IS NULL` → **0**（任何失败注入/正常操作后都成立）。
- [ ] **B2** 每 region 至少 1 revision：`SELECT COUNT(*) FROM regions r WHERE NOT EXISTS (SELECT 1 FROM region_revisions rev WHERE rev.region_id=r.region_id)` → **0**。
- [ ] **B3** 零写：冲突后目标 region 的 `COUNT(*) FROM region_revisions` 不增加、`reading_order` 不变、`deleted_at`/`is_pinned` 不变（见 A4/A9/A10 测试断言）。
- [ ] **B4** 历史不可变：本分支不存在 `UPDATE/DELETE region_revisions` 的写入（除 `is_pinned` 单列，属既有 pin 语义）；`git diff f971ece07..HEAD -- src/infrastructure/sqlite/regions.py` 只应出现批量 seam 与行写 helper。
- [ ] **B5** 双投影一致（锁）：显式锁路径（set_region_lock / merge/split 继承）后 `regions.translation_locked` 与 `text_json.translation_locked` 同为真/同为假；既有 `save_manual_translation` 只写文本级的行为保持不变（GAP-3，见 C4）。

## C. 协议/契约/安全

- [ ] **C1** 命令面与 minor：C067–C077 全部 `minor=3`；`PROTOCOL_MINOR` 仍为 3（零 bump）。
  文件：`core_service.py:451`（`_REGION_WRITE_COMMANDS`）、`:4952`（读命令归入 Region 读分支）；`HostCommandRegistry.cs:279/299/310`（三集合）；测试 `test_region_write_commands.py:911`、`test_region_text_read_command.py:382`。
- [ ] **C2** 冻结 66 快照未编辑；追加集恰为 10 写 + 1 读。
  命令：`git diff ba59a6c0d..HEAD -- verification/HOST-COMMAND-MIGRATION-1` → 空；`CommandParityContractTests` 派生式断言（`V11RAdditiveCommandNames`）。
- [ ] **C3** 错误边界：INVALID_REQUEST(validation) / INPUT_REVISION_CHANGED(conflict) / TARGET_NOT_FOUND(not_found) / UNKNOWN(internal)；消息不含路径/异常原文/未请求文本。
  文件：`core_service.py:5050`（`_REGION_WRITE_COMMANDS` 分支的 error 映射）；测试各 `assert_error`。
- [ ] **C4** GAP 诚实性：GAP-1「set_locks 为 V11R-F0-1 新增」标注仍在；GAP-2 在 F0-1 记录原始事实、F0-2 单独 CLOSED；GAP-3「既有 manual save 只写文本级、未改」显式保留。
  文件：`doc/contracts/V11R_REGION_WRITE_CONTRACT.md` §6；`verification/V11R-F0-1/GAPS.md`。

## D. 可复跑 Gate（期望全部 exit 0）

- [ ] **D1** `cd <worktree> && python -m pytest -q` → `2684 passed, 10 skipped`（skip 为既有环境性）。
- [ ] **D2** `python -m pytest -q tests/core/test_region_atomicity.py tests/core/test_region_batch_locking.py tests/core/test_region_transactional_guards.py tests/core/test_region_lock_inheritance.py tests/core/test_region_write_commands.py tests/core/test_region_text_read_command.py tests/editing/test_region_write_guards.py` → **61 passed**。
- [ ] **D3** `cd apps/desktop-avalonia && dotnet build NewManga.sln -warnaserror` → 0 warning / 0 error。
- [ ] **D4** `dotnet test NewManga.sln --no-build` → 0 failed（CoreClient 111 passed；App 137；Host 39+21 skip）。
- [ ] **D5** `dotnet test NewManga.sln --no-build --filter "RegionWriteCommandTests|CommandParityContractTests"` → **77 passed**。
- [ ] **D6** 证据与固定点一致：`verification/V11R-F0-1-I1/commands.json` 的 commit SHA 与 `git log --oneline f971ece07..HEAD` 一致；日志中的 `EXIT_CODE=0` 行存在。

## E. 明确不在本次范围（不得据此判 FAIL，除非被伪装成已实现）

- [ ] **E1** UI 空文本风险：本分支无 UI 改动；Studio Page 接入时不得把「读取失败」当「空稿」写回（见 `CONSUMER_GUIDE.md`）。
- [ ] **E2** page/book ACL：项目未定义按书授权；本次不加假 ACL；跨书 id 由 Host 未来 ACL 承担（契约 §3「安全边界」）。
- [ ] **E3** 既有 `save_manual_translation` 双投影不一致（GAP-3）保持现状，未在本分支修改。
- [ ] **E4** `IHostController` 便捷方法不在本任务（core-bridge 写域）；UI 通过 `HostRuntime.Commands` 消费。

## F. 审查结论记录位

```
Reviewer:            ____________        Date: ____________
PASS / PASS_WITH_ISSUES / FAIL: ________
未关闭条目（文件:行 + 复现 + 实际）：
  - 
是否放行 DSH 集成到 main： 是 / 否
```
