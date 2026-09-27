# DIAG-READING-EXPORT-001-FIX-C 集成核验记录（Integrator=代行 Codex，2026-09-28）

- Owner：ZCode；非作者 Reviewer：DeepSeek Harness（六轮）；Integrator：代行 Codex（ZCode 会话，待真 Codex 追认）
- 固定 base：`0e34c5c3c0a753be3e9f310daa0e413959f4ca5d`（FIX-B 集成治理 commit）
- Owner 交付链：claim `b1f4cedf` → R1 `de0bf175` → R2 `e9f61f5b` → R3 `132aa5e1` → R4 `46c7ff5a` → R5 `5d541bee`（doc）→ R6 `0e0e699e`（doc，tip）
- Review 六轮：[r1](../../../../doc/reviews/DIAG-READING-EXPORT-001-FIX-C-dsh-r1.md) `approved`（F-1..F-6 六×Minor）→ [r2](../../../../doc/reviews/DIAG-READING-EXPORT-001-FIX-C-dsh-r2.md) `changes_requested`（N-1 P2 + N-2..N-5 P3 + N-6 P4）→ [r3](../../../../doc/reviews/DIAG-READING-EXPORT-001-FIX-C-dsh-r3.md) `changes_requested`（T-1 P3 + T-2..T-4）→ [r4](../../../../doc/reviews/DIAG-READING-EXPORT-001-FIX-C-dsh-r4.md) `changes_requested`（H-1..H-3 纯文档）→ [r5](../../../../doc/reviews/DIAG-READING-EXPORT-001-FIX-C-dsh-r5.md) `changes_requested`（H-3 尾项 AC4 指针）→ [r6](../../../../doc/reviews/DIAG-READING-EXPORT-001-FIX-C-dsh-r6.md) `approved` @`0e0e699e`。逐字节导入，SHA256：[sha256.txt](../review-dsh-import/sha256.txt)
- **Integration merge：`0f2e9e31a666eddb4c9b8e17fb5401567c7e3924`**（parents `601371f5`（Review 归档）+ `0e0e699e`；Owner 历史未改写；唯一冲突 `doc/tasks/DIAG-READING-EXPORT-001-FIX-C.md` 按先例取 Owner 交付版，治理写入 `done`）

## 集成核验

| # | 检查 | 方式 | 结果 |
|---|---|---|---|
| N1 | 历史 | `git merge-base 7144e4fa 0e0e699e` = `0e34c5c3`（Owner 分支直接生长于固定 base） | PASS |
| N2 | 范围 | `git diff --name-status 0e34c5c3..0e0e699e` = 15 路径，产品代码仅 `src/bootstrap/app.py`（Task allowed 首项）；`src/application/**`、`src/infrastructure/**`、`src/ui/**`（含 QML）、`requirements*`、`doc/contracts/**` 零命中 | PASS |
| N3 | 卫生 | `git diff --check 0e34c5c3..0e0e699e` 非日志文件零问题（原始 pytest 日志含运行时行尾空白，按 Q-009 原始字节保留） | PASS |
| N4 | Review 六轮闭环 | N-1（P2 离园时长计入）以 bootstrap 层重置守卫修复 + 600s 判别测试（容忍式断言，DSH T-1 要求）；N-2 幂等守卫 + open 计数断言；N-3/N-4/N-5 收口；R4/R5 纯文档指针收口；R6 `approved` | PASS |
| N5 | 集成 head 全仓复跑 | `python -m pytest -q -p no:cacheprovider -rs tests` @ 集成 head：**1318 passed, 5 skipped, 1 warning**，[integration-full-suite.log](../integration-full-suite.log) | EXIT=0，PASS |
| N6 | 口径一致性 | 1318+5 与 Owner R4 全仓一致（+1 = FIX-C 接线测试，FIX-B 基线 1317+5）；5 skip = 2 docTR + 1 numpy + 2 torch；6 OpenSSL = 本 shell PATH 实跑通过 | PASS |
| N7 | 结论口径 | 零 QML 改动（纯 Python bootstrap 接线）；F-1/AC1 裁决记录于 Task 集成记录；无产品级过度声明 | PASS |

## F-1/AC1 裁决（代行 Codex，待真 Codex 追认）

采信 DSH R1 F-1 建议：Task AC1 原文"断言 `services.reader.hasChapter is False`"为 **AC 文本缺陷**（与 FIX-B
冻结的 `closeReader` 语义——flush + 停心跳、不清 `hasChapter`——直接矛盾），非实现缺陷。AC1 有效契约修订为
"离开读者页触发 `closeReader`：**心跳停止 + 进度 flush**（`hasChapter` 按 `ReadingService.close()` 既有
语义保留）"；实现与测试按修订契约核验通过。Task 文件已按裁决修订 AC1 并标注。

## 结论

[DIAG-READING-EXPORT-001-FIX-C](../../../tasks/DIAG-READING-EXPORT-001-FIX-C.md) 置 `done`，
integration_commit=`0f2e9e31a666eddb4c9b8e17fb5401567c7e3924`。**诊断家族终态**：DIAG-READING-EXPORT-001
（诊断）+ FIX-A（症状 A）+ FIX-B（症状 B 生命周期）+ FIX-C（生产接线）全部 `done`；历史
`reading_export` flaky 的两个机制（终态信号排队投递竞态、读者心跳写已关闭 SQLite）均已修复落地；
唯一未决知识项 = 诊断 U3（真实全仓触发条件）。DSH 各轮的 P3/P4 观察（N-6 公开 pause/resume 面、
T-4 口径注释等）已披露于各 Handoff，随后续触碰相应文件的 Task 顺带处理。
