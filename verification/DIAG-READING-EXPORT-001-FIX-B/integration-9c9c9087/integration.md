# DIAG-READING-EXPORT-001-FIX-B 集成核验记录（Integrator=代行 Codex，2026-09-28）

- Owner：ZCode；非作者 Reviewer：DeepSeek Harness（三轮）；Integrator：代行 Codex（ZCode 会话，待真 Codex 追认）
- 固定 base：`a8b94df1f1ee091a9cca894c421e9ffc3ad30614`（FIX-A 集成 merge；串行释放）
- Owner 交付链：claim `6e37f05d` → R1 `3ce82240`/`528ba4d4` → R2 `2a1078b6` → R3 docs `f93ea667`（tip）
- Review 三轮：[r1](../../../../doc/reviews/DIAG-READING-EXPORT-001-FIX-B-dsh-r1.md) `changes_requested`（R-01/R-02 2×P2 + R-03..R-06 4×P3）→ [r2](../../../../doc/reviews/DIAG-READING-EXPORT-001-FIX-B-dsh-r2.md) 复核"代码与测试面通过"，剩 N-01..N-05 文档缺口 → [r3](../../../../doc/reviews/DIAG-READING-EXPORT-001-FIX-B-dsh-r3.md) `approved` @`f93ea667`（另 2×P3 advisory 不影响批准）。逐字节导入，SHA256：[sha256.txt](../review-dsh-import/sha256.txt)
- **Integration merge：`9c9c9087b8f2a6e51fa670ab99486d4a11edff49`**（parents `dbae0240`（Review 归档）+ `f93ea667`；Owner 历史未改写；唯一冲突 `doc/tasks/DIAG-READING-EXPORT-001-FIX-B.md` 按先例取 Owner 交付版，治理写入 `done`）

## 集成核验

| # | 检查 | 方式 | 结果 |
|---|---|---|---|
| N1 | 历史 | `git merge-base 8e57e4df f93ea667` = `a8b94df1`（Owner 分支直接生长于固定 base） | PASS |
| N2 | 范围 | `git diff --name-status a8b94df1..f93ea667` = 12 路径（6A+6M），全在 Task allowed 清单；`src/bootstrap/**`、`src/application/**`、`src/infrastructure/**`、`src/ui/qml/**`、`requirements*`、`doc/contracts/**` 零命中（DSH r1 的内容级核验与本记录的 git 级核验双重确认零越权） | PASS |
| N3 | 卫生 | `git diff --check a8b94df1..f93ea667` | exit 0，PASS |
| N4 | Review 三轮闭环 | R-01（生产终结点 AC1 口径）以披露式升级处置并被 r2 接受；R-02 teardown 补 ：162 + webtoon_tiles 不收口理由成立；R-03..R-06 与 N-01..N-05 全部收口；r3 `approved` | PASS |
| N5 | 集成 head 全仓复跑 | `python -m pytest -q -p no:cacheprovider -rs tests` @ 集成 head：**1317 passed, 5 skipped, 1 warning, 69.10s**，[integration-full-suite.log](../integration-full-suite.log)；全日志无 `Cannot operate on a closed database` | EXIT=0，PASS |
| N6 | 口径一致性 | 1317+5 与 Owner R2 全仓一致（+1 = FIX-B 新回归测试，FIX-A 基线 1316+5）；5 skip = 2 docTR + 1 numpy + 2 torch；6 OpenSSL = 本 shell PATH 实跑通过 | PASS |
| N7 | 结论口径 | 泄漏探针 7/7 PASS（真实 2 心跳周期 0 异常、心跳自停、错误可诊断）；AC1 生产接线缺口如实披露并转裁决；无"产品级已修复"的过度声明 | PASS |

## AC1 范围缺口裁决（代行 Codex，待真 Codex 追认）

- 本 Task 修复目标（症状 B 的异常噪音、重复写、测试泄漏面）全部达成；`closeReader()` 终结点在 API/测试面成立。
- 生产 QML/bootstrap 的终结点接线为零（Task 禁止范围）；生产路径行为 = 存储消失后"报错一次（类型化记录）→ 心跳自停"。
- **裁决**：FIX-B 判 `done`；生产接线登记为独立 `proposed` 候选 Task（建议名 `DIAG-READING-EXPORT-001-FIX-C`：生产装配/QML 离开读者页接线 `closeReader`/`aboutToQuit`；Owner/Reviewer/范围待真 Codex 释放时冻结），不在本 Task 内实现。
- r3 附带的 2×P3 advisory（不影响批准）：见 [r3 报告](../../../../doc/reviews/DIAG-READING-EXPORT-001-FIX-B-dsh-r3.md)尾部，随 FIX-C 候选一并考虑。

## 结论

[DIAG-READING-EXPORT-001-FIX-B](../../../tasks/DIAG-READING-EXPORT-001-FIX-B.md) 置 `done`，integration_commit=`9c9c9087b8f2a6e51fa670ab99486d4a11edff49`。诊断家族收口：DIAG（诊断）+ FIX-A（症状 A）+ FIX-B（症状 B）均 `done`；诊断 U3（真实全仓触发条件）作为唯一未决知识项保留；无已释放 Task 遗留。
