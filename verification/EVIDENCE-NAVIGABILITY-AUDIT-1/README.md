# EVIDENCE-NAVIGABILITY-AUDIT-1：证据索引**真的可被第三人导航**（模拟复核）

基线 `df387347d`。

## 1. 方法

不重新论证，**只做一件事**：假装自己是第一次接触本项目的 Reviewer，
**只拿 `doc/reviews/EVIDENCE-INDEX-2026-11-15.md`**，按它写的路径去打开证据，看能不能找到对应内容。

## 2. 抽检结果（4/4 命中）

| # | 索引里的主张 | 索引给的路径 | 我实际打开看到的 | 命中 |
|---|---|---|---|---|
| 1 | §1：`L-AI1-6` 有**能变红的反向断言** | `tests/storage/test_prompt_templates.py:221` | `assert not hasattr(SqlitePromptTemplateStore, "reassign_references"), (`<br>`"dead N-01 helper is back; P23 must keep using delete_with_reassign"` | ✅ |
| 2 | §4.2：`GATE4-PAGES-UPGRADE-1` 当时把 reader 标 `NOT_REACHABLE` | `verification/GATE4-PAGES-UPGRADE-1/README.md` | `L18` 含 `NOT_REACHABLE` | ✅ |
| 3 | §7.2：全量测试 955/0/11/966 | `verification/READER-OVERLAY-HEADLESS-PNG-1/render-info.md` | `L24` `已通过! - 失败: 0，通过: 955，已跳过: 11，总计: 966`；`L29-32` 与基线 954/965 的对照表 | ✅ |
| 4 | §7.3：`L-R1-1-VISUAL-EVIDENCE-1` 存在 | `verification/L-R1-1-VISUAL-EVIDENCE-1/` | 目录与 `README.md` 存在，内含四项控件的图证描述 | ✅ |

## 3. 这说明什么

**证据索引不是"文档里声称有证据"，而是"指向的具体位置确实有那个内容"。**

**⇒ 第三人可以从索引出发，独立复核每一条主张，不需要信任我的叙述。**

## 4. 它不说明什么（诚实）

- 只抽了 4 条（索引里有 30+ 条），**没有全量复核**；
- 抽的 4 条都是"文件存在 / 某行有某字符串"这类**低成本可验**项；
- **没有抽"结论是否正确"**（例如"条件 3 是否真的接近满足"）——
  那需要重新论证，不是导航测试能证明的。

## 5. 建议给后来者

**若要验证本项目的结论，建议顺序**：

1. 先跑四件套（`check` / `pins` / `inventory` / `dotnet test`）—— 30 秒，能确认"现在"的状态；
2. 再从 `EVIDENCE-INDEX-2026-11-15.md` 挑 2–3 条**你关心的**主张，按路径打开；
3. **不要只读 `FINAL-HANDOFF`** —— 它是汇总，不是证据。
