# FEA-06-RESIDUAL-3 Canonical Evidence（Fluent 4 格 + Tab/a11y，0 pin）

> **结论先行**：`FEA-06-RESIDUAL-2` 的 BLOCKED 表 **6 格**在本卡处理 —— **4 格关闭**（格1 批量矩阵/吸顶 + RunProjectionBar、格2 Reader 双页/webtoon、格4 书架自洽聚合、格5 Console 9 行）、**Tab 遍历 + a11y 属性/UIA 树**补齐；**格 3（RegionBox「查看对照」）re-home `FEA-06-RESIDUAL-4`**（需 C-07 additive，违反 0 pin）；**原生 a11y 行为/200% DPI/原生截图 NA**（原生交互未执行，保留 NOT_RUN）。
> 关键事实：Core `page_order` **1-based**（R3-001 修复）；C061 重试返回子 Run 于 `run_id`（R3-R3-001 修复）；像素不作 AC（9 图仅签署证据）。

| 项 | 值 |
|---|---|
| task | `FEA-06-RESIDUAL-3`（卡面；scope review `FEA-06-RESIDUAL-3-scope-r1.md`） |
| Owner | `fea06-residual3-impl`（DSH Agent Teams） |
| Review | r1 changes_requested（P1×2）→ r2 changes_requested（P1×1）→ r3 changes_requested（P1×1）→ **r4 approved（P0=0/P1=0/P2=0/P3=5）** |
| base | `9429fc210` |
| 实现/返修提交 | `a2b51c79d` → `fc6712e94` → `5cabc1ebd` → **`ddc29ecb3`**（integration/delivery） |
| 契约 | 零变更（0 pin；18 pins PASS） |

## 门禁（Lead 一手，head `ddc29ecb3`）
build 0/0；全量 .NET **1731 passed / 0 failed / 98 skipped**；pytest **3390/10**；pins **18/18**；check PASS(3w)；API EXIT 0；diff 24 文件 ⊆ allowed_paths；禁止面（src/、doc/、Services/、V2、DesignSystem）零 diff；FEA-09 已恢复。

## 关闭/未关闭矩阵（BLOCKED 表逐格）
| 格 | 结果 |
|---|---|
| 1 BatchMatrix 七状态/吸顶、RunProjectionBar | **关闭**（AC-1） |
| 2 ReaderPage 双页第二图/滚动 | **关闭**（AC-3；两页连续口径，L-R3-1 全章长滚动 re-home） |
| 3 RegionBox 冲突态「查看对照」 | **未关闭 → re-home `FEA-06-RESIDUAL-4`**（C-07 additive） |
| 4 书架满态统计 | **关闭（改口径）**：既有投影自洽聚合（AC-4） |
| 5 Console 投影/9 行 | **关闭**（AC-2） |
| 6 完整 Tab 遍历 / 原生 a11y / 200% DPI / 原生截图 | Tab 遍历+a11y 属性**关闭**（AC-5）；原生 a11y/DPI/截图 **NA（NOT_RUN）** |

> **done 不覆盖 BLOCKED 表**：格 3 与原生项仍未做；本卡 done 仅覆盖上述 4 格 + Tab/a11y。

## 不构成什么
不构成「FEA-06-RESIDUAL-2 全部关闭 / UI L1–L10 关闭 / 完全实现」；不构成可发布（`Technical Gate=NOT_SATISFIED` 不变）；原生项 `NOT_RUN`。
