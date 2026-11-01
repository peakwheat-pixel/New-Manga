# FEA-03 手工 Smoke 与边界记录

所有临时 SQLite/journal/进程探针数据均放在系统临时目录，不接触用户 library 或源文件。以下属于补充手工 smoke，不能替代 pytest、dotnet test 或 D4 production assembly 验收。

## Draft / Journal

直接调用 Draft 与 DraftJournal：断言 Draft JSON 恰有 11 字段、DraftSequence 0 起并在两次 patch 后为 2、journal roundtrip 保留 PageBindingVersion=7、sequence 1 和 2 的 receipt 分别可读。

结果：{"draft_fields":11,"sequence":"0->2","journal_roundtrip":"PASS","multi_sequence_receipts":"PASS"}

edit-open active 登记也在真实 SQLite 组件 smoke 中断言通过。

## 崩溃与单写者进程探针

可复跑命令：python verification/FEA-03/crash_probes.py。脚本使用 tests/infrastructure/draft_journal_crash_worker.py 对临时目录启动真实子进程。每个阶段预先写旧 journal：

| 阶段 | 注入点 / 子进程退出码 | 重启后内容 | 临时文件 |
|---|---|---|---|
| CRASH-A | temp 写入前，70 | old | 清理后无 *.tmp |
| CRASH-B | temp fsync 后、replace 前，71 | old | 清理后无 *.tmp |
| CRASH-C | replace 返回后、目录 fsync 前，72 | new | 清理后无 *.tmp |
| LOCK | 第二进程返回 73；释放锁后再启动返回 0 | 第二写者 fail-closed，释放后可启动 | PASS |

结果：四个探针均断言通过。CRASH-A/B/C 是进程级 kill；Task 所要求的单元级异常注入 pytest 未运行。

## SQLite component-level apply

可复跑命令：python verification/FEA-03/component_sqlite_smoke.py。以真实 sqlite3 数据库、MigrationRunner、SqliteRegionRepository、RegionEditingService、DraftJournal 和 DraftProtectionService 组装；不是 fake/in-memory repository，也不是 assemble_production_core 对象图。脚本还验证 edit-open active 登记、跨 Session 冲突、former owner 只读及冲突 candidate 阻止 apply。

结果：
- edit-open 后 journal status=active；
- prepare 仅生成 candidate，current_revision_id 不变；
- apply 后 receipt replay 返回相同 revisionIds，revision 数量未重复增加；
- 三个 Region 的批次中第三个 base stale，返回 STALE_BASE_REVISION，前两个 Region 的 current pointer 与 revision count 均不变。

脚本最终输出：{"apply_and_receipt_replay":"PASS","edit_open_and_candidate_only":"PASS","receipt_failure_intent_recovery":"PASS","session_conflict_and_owner_gate":"PASS","three_region_stale_atomic_rollback":"PASS"}

## Intent 崩溃恢复

在真实 SQLite 组件 apply 成功提交 DB 后，注入 receipt 写失败，断言 apply 以 DRAFT_JOURNAL_UNWRITABLE fail-closed；关闭并重启 SQLite 与 DraftJournal 后，commitIntent 通过 current revision id 和 revision content digest 检查补写 receipt；同 token 重放返回相同 revisionId，revision count 保持 2。

输出：{"integration":"SQLite + DraftJournal component restart","receipt_write_crash":"injected after DB commit","intent_recovery":"PASS","replay_same_revision":"PASS","revision_count":"2 (no duplicate)"}

此证据只覆盖 receipt 写失败→intent 恢复分支，不覆盖 receipt-present、current mismatch、每个 Region 不全匹配的所有分支。

## owner conflict

真实 SQLite 组件级 smoke 验证 Session 1 的 text patch 与 Session 2 冲突时双方进入 conflicted；新 Session 的 candidate apply 被拒绝 DRAFT_CANDIDATE_INVALID。

输出：{"cross_session_text_conflict":"PASS","conflicted_candidate_apply_blocked":"PASS"}

## BRIDGE 防抖测量

直接编译并执行临时 C# harness，使用 DraftBuffer 默认 400ms debounce。方法：12 次串行 ApplyPatchAsync；每次从调用开始计时至注入 flush seam；以样本升序，nearest-rank 索引 ceil(n*p)-1 计算 p50/p95。

输出：Debounce measurement: n=12, p50=405.3ms, p95=407.6ms.

该测量通过真实 DraftBuffer 生产源，不是 dotnet test；机器负载与单机样本限制了外推范围。