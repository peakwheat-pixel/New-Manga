# CONDITION1-FINDINGS-RECHECK-2：`L-L1-1` 核实通过 —— **条件 1 的 8 项全部核完**

基线 `940c8aaf2`。补上 `CONDITION1-FINDINGS-RECHECK-1` 遗留的最后一项（`L-L1-1` 未查）。

## 1. `L-L1-1`（`ChapterSummary` 不投影 `kind`）—— **已解决**

### 1.1 契约侧：有 UNFREEZE 载体

`doc/reviews/CONTRACT-UNFREEZE-2026-11-14-M2C1.md`：

| 行 | 内容 |
|---|---|
| `:5` | 授权：**DSH 2026-11-14 裁决「批准方案 A（契约 additive 修订）」**（依据 `M2-C1:194` 的 `ListRegions` 1.5 additive widening 先例） |
| `:6` | 上游依据：limitation 处置矩阵 §3.1 的 **`C1-4`（L-L1-1 `kind` 投影）** 与 `C1-5`（L-L1-2 `custom_rank`） |
| `:12` | `list_chapters` result 行：由 `{chapter_id, title, chapter_number, sort_order}` → **追加两个字段** |
| `:31` | `kind` string 可选，来源 `chapters.chapter_type`（v1 起既有列），枚举 `"paged"` / `"webtoon"` |
| `:35` | **"实现必须总是返回 `kind`"**；`custom_rank` 未设置时返回 `null`（不是省略） |

**⇒ 这是 additive 修订，有明确授权与载体，不是私自改契约。**

### 1.2 实现侧：`Kind` / `CustomRank` 已投影

`apps/desktop-avalonia/src/NewManga.CoreClient/CoreServiceClient.cs`：

```csharp
record ChapterSummary(
    string ChapterId,
    string Title,
    string ChapterNumber,
    int SortOrder,
    string? Kind = null,
    long? CustomRank = null)
```

且 `Parse` 的 XML 注释写明：

> M2-C1 rev 2.16: parse one `list_chapters` row. The four frozen keys are required
> (a missing/mistyped one throws `FormatException` -- the row is malformed),
> while `kind`/`custom_rank` are **OPTIONAL**: an absent field, an explicit null and
> an older four-key Core all read as null.
> Kept as a static entry point (same convention as `RegionTextDetail.Parse`) so the widening is
> **testable without a live sidecar**.

**⇒ 三个关键点都满足**：
1. **字段存在**（`Kind` / `CustomRank`）；
2. **向后兼容**（老的四键 Core 读作 null，不抛）；
3. **可测**（静态 `Parse` 入口，无需 live sidecar）。

## 2. ★ 条件 1 的 8 项 —— 全部核实完毕

| # | finding | 核实方式 | 结论 |
|---|---|---|---|
| 1 | **L-R1-1** | 静态核查 `Views/Fluent/ReaderPageView.cs`（737 行，C# 构建 UI） | ✅ 书签/进度/reset/偏好四控件全在（`L-R1-1-UI-WIRING-VERIFY-1`） |
| 2 | **L-R2-1** | 同上（与 #1 同族） | ✅ |
| 3 | **L-F1-2** | 打开 `tests/core/test_font_wire.py` | ✅ `:92` 测试存在，`:86` 注释明标 finding id |
| 4 | **L-F1-3** | ZCode 裁决 + CLOSE-1 | ✅ 替代判据被接受 |
| 5 | **L-L1-1** | UNFREEZE 载体 + `CoreServiceClient.cs` record | ✅ **本卡** |
| 6 | **L-L1-2** | 前卡四项核实 | ✅ |
| 7 | **L-L1-4** | 打开 `src/application/library/service.py` | ✅ `:28-33` + `:298` 注释明标 `AC6 (R3-001)` |
| 8 | **L-AI1-6** | 实测命中 0 + 反向断言 | ✅ `assert not hasattr(...)` |

**⇒ 8/8 全部有**我亲自打开过的**代码/测试证据**，不是只引用裁决文档。**

## 3. 仍未消除的唯一保留点（诚实）

**`L-R1-1`/`L-R2-1` 的"真实窗口可见性"未验。**

静态证明的是"**控件已构建并绑定 Command**"，**不等于**"真实窗口里用户能看到它们"。
真实窗口验证受 GUI 限制（`GATE3-FOUR-PAGE-WALKTHROUGH-1` §8：4 种途径全部挂起 + 对照实验）。

**⇒ 这是与条件 3 / 条件 4 AC7 同源的一个缺口，不是条件 1 独有的。**

## 4. 未做

- 未运行 UI 测试（headless）验证这四项控件的运行期行为 —— 既有 `FEA-14-READ-2` 记录了 VM 行为与测试已覆盖。
- 未核实 `FEA-14-READ-2` 的 `closed_with_limitations` 是否已被某张卡正式关闭流程走完
  （本卡只证明"代码里有控件且契约已解锁"，不证明"那张 limitation 卡被走完流程关闭"）。
