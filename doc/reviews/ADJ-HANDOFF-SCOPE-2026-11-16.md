# 裁决：历史卡补写 Handoff / Review 的 allowed_paths 边界（DSH，2026-11-16）

- adjudicator: DSH（Lead / Architect / Integrator，2026-10-25 用户裁决授予 Task 生命周期与范围裁决权）
- date: 2026-11-16
- subject: `status ∈ {done, closed_with_limitations}` 的历史卡，补写 Handoff / Review 时可否超出原 `allowed_paths`
- base_commit: 3b17a2c42

## 问题

`B1` 批次（33 条待处置 AC 中的 `DOC` 8 条）里，有三条卡在同一个约束上：

| 卡 | AC | 剩余缺口 | 位置 |
|---|---|---|---|
| `RELEASE-PACKAGE-1` | AC6 | Handoff 文件不存在 | `doc/handoffs/RELEASE-PACKAGE-1-handoff.md` |
| `MICA-FIX-1` | AC5 | Handoff 缺「取色方法」 | `doc/handoffs/MICA-FIX-1-handoff.md` |
| `FEA-07-AC5-NATIVE-1` | AC-N5 | 缺独立 Review | `doc/reviews/` |

而这三张卡的 `allowed_paths` **都不含** `doc/handoffs/**` 或 `doc/reviews/**`。

## 既有规定（不是空白，是本裁决的依据）

`09_COLLABORATION.md`：

- **§4.1（L56）**：「并行只用于……超出 `allowed_paths` 时**暂停越界部分，在 Task 提出范围变更**。」
- **§5（L262-264）**：「交付文件：`doc/handoffs/TASK-xxx-<short-head>.md`，使用 Handoff 模板。」
- **§4（L73）**：「`in_progress` → `in_review`：交付 head 固定，AC 结果、**Handoff** 和 canonical evidence 就绪后请求独立 Review。」

⇒ **Handoff 是规定的交付物**，不是可选项；而 `allowed_paths` 是按**实现范围**写的元数据，
历史卡在冻结时往往没有把「事后补交接文档」的位置纳入。

`check.ps1` **不校验 `allowed_paths`**（grep 无命中）—— 说明这是**流程约束**而非机械门禁。

## 裁决

**历史卡（`status ∈ {done, closed_with_limitations}`）在补写交付文档时，可按以下口径扩范围：**

1. **允许**在 `doc/handoffs/<卡名>-handoff.md` 与 `doc/reviews/<卡名>-*.md` 写入，
   视为该卡**生命周期内的合理补写**，不视为范围扩大；
2. 前提：该卡确实缺这些交付物（如 AC 判据要求 Handoff / Review），且补写内容**只描述既有事实**，
   不得借机修改产品代码、契约或 Gate；
3. **不允许**借本裁决修改该卡 `allowed_paths` 已声明的**产品代码范围**
   （`apps/**`、`scripts/**`、Python `src/**` 等）；
4. 每次扩范围必须在该卡的 **Closeout 或 AC progress 注释中留痕**（说明扩了哪些路径、为什么）。

## 理由

1. **§5 把 Handoff 定为交付物** —— 不补等于交付不完整，而 `allowed_paths` 的冻结早于此需求；
2. **`check.ps1` 不校验它** —— 说明它不是安全边界，而是**协调手段**（防并发误写他人文件）；
   历史卡已 `done`、无并发写者，协调风险为零；
3. **不扩范围会导致"永远无法关闭"** —— 三条 B1 都因此卡住，这不是治理意图；
4. 保留硬边界（**不得改产品代码**），所以本裁决不会成为越权工具。

## 生效范围

仅适用于 **`status ∈ {done, closed_with_limitations}` 且缺交付文档**的历史卡。
**不适用于**在途卡（`proposed` / `ready` / `in_progress` / `in_review`）——
那些卡的范围冻结仍然有效，扩范围需走正常的范围变更流程。

## 本次适用

依本裁决，以下扩范围获准并将在卡面留痕：

| 卡 | 扩入路径 |
|---|---|
| `RELEASE-PACKAGE-1` | `doc/handoffs/RELEASE-PACKAGE-1-handoff.md` |
| `MICA-FIX-1` | `doc/handoffs/MICA-FIX-1-handoff.md` |
| `FEA-07-AC5-NATIVE-1` | `doc/reviews/FEA-07-AC5-NATIVE-1-*.md`（若后续需要独立 Review） |
