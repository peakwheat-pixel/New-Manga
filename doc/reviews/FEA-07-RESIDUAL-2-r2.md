# FEA-07-RESIDUAL-2 Review r2（独立上下文 fresh subagent）

| 项 | 值 |
|---|---|
| 被审 head | `bacf6c307`（r1 返修） |
| 结论 | **changes_requested**（P0=0 / **P1=1** / P2=1 / P3=7） |

## r1 修复复核
P2-003/P3-001/P3-010/P3-008/P2-004 全部 PASS（构造即注册 + 未注册 target typed `UnknownWindow`；旧 owner `Retained/CanEdit=false`；`EnsureWritable` 绑身份+实时 owner；C-13 注释收敛；定标 JSON 真实且算术正确）。独立变异（删构造注册）3 RED → 复原 MATCH → 复绿 71/0/0。

## P1（真实问题）
新增 `uiThreadSchedulingGapMs ≤ 400 ms` 断言在 **full-suite/负载**下不稳定：全量 **1777/1/102**（gap 513.55）；隔离复跑 3/4 次失败（437.34 / 471.81）。1000 ms p95 门槛本身通过。定标 249.44 不能代表负载条件 → 建议移入专用性能门禁或重定标。

## P2/P3
P2-002 Canonical Evidence 4 条 commit 归因错误；P3 注释旧数、定标脚本样本选择、JSON `passed` 只含 p95、措辞「纯加法」、`WindowRole.Main` 猜测、pytest 证据缺、`EnsureWritable` DraftId 边界。
