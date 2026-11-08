# FEA-07-RESIDUAL-3 Review r1（独立上下文 fresh subagent）

| 项 | 值 |
|---|---|
| 被审 head | `c3e3d37b9` |
| 结论 | **approved**（P0=0 / P1=0 / **P2=3** / P3=5），**附条件**：P2-01（真实 `%APPDATA%` 写入）须在关账前测试侧隔离，DSH 已升为 P1 处理 |

## 判定
AC-R4b-1（AC1 A03 真库/ACK）**MET**（真实 Python Core + 真实 `library.db`、50 往返=100 切换、保护列 0/11 diff、ACK 重放同 run）；AC-R4b-2（AC3 跨进程）**MET**（park/kill/recover 三进程、心跳冻结证真死、`RolledBack`/上一已提交/二次恢复零变化）；AC-R4b-3（AC4）**MET**（sink + 4 组真实进程 + 9 类矩阵）；AC-R4b-4 回填 **MET**（关账待 DSH）。变异 3 组 RED→MATCH→复绿。

## P2/P3
P2-01 真实 AppData 写入（→ 升 P1）；P2-02「旧结果仅 candidate」证据弱（候选表不存在）；P2-03 暂停期「最新状态」只改 appearance；P3-01 卡面 `sfx_locked` 笔误、P3-02 backfill 数字、P3-03 `Trace.AutoFlush`、P3-04 未过 HostRuntime、P3-05 `testhostGone` 措辞。
