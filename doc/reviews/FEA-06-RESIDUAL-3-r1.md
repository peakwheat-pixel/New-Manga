# FEA-06-RESIDUAL-3 Review r1（独立上下文 fresh subagent）

| 项 | 值 |
|---|---|
| 审查者 | 独立子代理（未参与实现）；DSH 落盘 |
| 被审 head | `a2b51c79d`（实现提交） |
| 结论 | **changes_requested**（P0=0 / **P1=2** / P2=5 / P3=6） |

## P1
- **R3-001**：矩阵/页面条页码对 Core **1-based** `page_order` 多加 1（`FluentRunProjection.cs:143` + `WorkbenchPageView.cs:568`）；测试用 0-based `index` 掩盖。
- **R3-002**：webtoon 末页/单页章节/第二页失败时 `_bitmapSecondary` 未清，`_webtoonImageSecondary` 仍显示上一页残留（`ReaderPageView.cs:416-435`）。

## P2/P3 摘要
R3-003 webtoon「连续页」仅两页口径；R3-004 A4 对 `ReaderPage ControlType=None` 测试内静默豁免；R3-005 A1 断言方向为 visited⊆F(P) 未全覆盖；R3-006 closeout 未做；R3-007 `_runId` 不清空无法 re-run；R3-008/009/011/012/013 测试质量/证据依赖 `.git` 等。

## 判别性
M1–M5 变异全部 RED 后复原；确认三处既有断言为**改写而非删除**。
