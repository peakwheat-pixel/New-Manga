# AC2（R-003）：证据措辞修正

日期：2026-11-01。Owner：DSH。基线：`main@5b888cd70`。

## 问题（SAFETY-8 Review R-003）

`verification/REALUSE-DATA-SAFETY-7/ac2-eol-pin.md` 在交付提交 `60056d353`（01:54:27）中写入：

> SAFETY-7 与 SAFETY-8 的独立 Review 均按此方式复核并全部一致（SAFETY-6 12/12、SAFETY-7 10/10）。

当时 SAFETY-8 的独立 Review 尚未开始（`captured_at` 02:08:02）——属于"证据文档写未发生的事实"，
与 F-001 同类。结论本身现已被 SAFETY-8 Review 证实（12/12 与 10/10 一致），但写入时机不对。

## 修复

改为只记录**已发生**的审查结论，并显式声明回填规则：

```markdown
SAFETY-7 的独立 Review 已按此方式复核并全部一致（SAFETY-6 12/12、SAFETY-7 10/10，见
`doc/reviews/REALUSE-DATA-SAFETY-7-review.md`）；SAFETY-8 的独立 Review 也已按同一方式复核
（12/12 一致、变化恰为 5 条，见 `doc/reviews/REALUSE-DATA-SAFETY-8-review.md`）。
本段只记录**已发生**的审查结论；任何新 Review 的结论须在其报告落盘后再回填。
```

两处引用均指向已成文、可核对的 Review 报告（`REALUSE-DATA-SAFETY-7-review.md` 于 `2a0528851`
入库、`REALUSE-DATA-SAFETY-8-review.md` 于 `5bea0ce4b` 入库），不再有对未来的断言。

## 验收

- 文中不再出现"某 Review 已复核"而该 Review 尚未成文的表述；
- 引用路径真实存在且 commit 可查。
