# FEA-07-RESIDUAL-2 Review r1（独立上下文 fresh subagent）

| 项 | 值 |
|---|---|
| 被审 head | `9ec6b196b`（feat `85207730e` + docs） |
| 结论 | **approved**（P0=0 / P1=0 / **P2=4** / P3=12） |

## 判定
AC-R4a-1（AC2 窗口层 owner，含冻结解释）**MET**；AC-R4a-2（生命周期）**MET**；AC-R4a-3（AC6 指标/规模）**MET**；AC-R4a-4（证据/治理）**MET**（pytest 未跑，后补）。变异 3 组（owner 恒 Grant / 窗口插 Start-Dispose / UI 心跳延迟）均 RED → sha256 MATCH 复原 → 复绿。

## P2
P2-001 扩域行数口径（+26/−5 净 +21，非「≤25 纯加法」）；P2-002 生产组合根未注入共享 registry、`RegisterSecondary` 零调用 → 跨窗仅测试可见（→ L-R4a-1）；P2-003 转移目标未注册默认 Main（**真实顺序缺陷**）；P2-004 UI gap 400ms 定标原始数据未入证据。

## P3（摘要）
旧 owner Retained/CanEdit、3 轮同进程、n=10 p95=max、规模 residual 无 ID、pytest 未跑、allowed_paths 待落盘、Host 零写入为测试替身、C-13 注释压缩复述、跨 Session 措辞、`EnsureWritable` 未绑身份、主窗 token 变化、AC5 NA 行政性重复。
