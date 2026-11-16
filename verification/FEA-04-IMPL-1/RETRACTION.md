# FEA-04-IMPL-1 撤销记录（2026-11-16，DSH）

## 结论
本卡**撤销**，从未开展任何实现工作。全部 8 条 AC 记 `NOT_APPLICABLE`。

## 撤销原因：建卡前提是错的
我（DSH）建本卡时依据 `doc/tasks/FEA-04.md` 卡面上「AC1–AC8 一律标 `blocked: 实现未开始`」，
推断「实现还没开始，需要一张实现卡」。**我没有先核实实现是否已交付** —— 流程错误。

## 同日核实结果：FEA-04 的实现早已交付并通过独立复核

| 项 | 位置 |
|---|---|
| 代码 | `apps/desktop-avalonia/src/NewManga.App/Shell/V2/Frontends/CurrentFrontend.cs`(12493 B)、`CurrentSessionMemento.cs`(4112 B)、`apps/desktop-avalonia/src/NewManga.App/Views/V2/Route/CurrentRouteAdapter.cs`(1642 B) |
| 测试 | `apps/desktop-avalonia/tests/NewManga.App.Tests/FEA04CurrentAdapterTests.cs`(16804 B，17 项) |
| 证据 | `verification/FEA-04/`：baseline-comparison.md、preflight-blocker-matrix.md、lifecycle-assertions.md、sln-test-results.md、build-test-raw.log、git-diff-check.log、governance-check.log、verify-pins.log |
| 复核 | `doc/reviews/FEA-04-r3.md` = **approved（P0=0 / P1=0，reviewed_head `af9625e7e`）**；r3 `:105` 明写「AC1–AC7 在 head 均有实测/证据支撑（本席位独立复跑 931/0/60、0 failed）」 |

⇒ `FEA-04` 的 AC1–AC8 **已逐条依据既有证据闭合**（含两处诚实登记：基线 commit 由
`91be6c134` 替换为 `68c72ba57`（前者 build 被 NuGet 路径问题 BLOCKED）、AC8 点名 `r1` 但 `r1` 实为
`changes_requested` 而由 `r3` approved 满足）。

## 教训
**卡面的 `blocked: 实现未开始` 不等于「实现不存在」。**
处理任何 blocked AC 前，先核 **代码 / 测试 / 证据 / 复核** 四者是否已存在，再决定是「补证据」还是「立新卡」。
这与 R11 在 `M2-SFX` AC4 上踩的是同一类错（blocked 理由会过期）。
