# 下一阶段 Task 范围（D06 缺口 / D07 解环）

状态：**SCOPE DEFINED / 待激活**
定义人：DSH
日期：2026-11-01
依据：[GATE-CONTRACT-CLOSURE-2026-11-01](GATE-CONTRACT-CLOSURE-2026-11-01.md) §6、[FEA-GATE-READINESS-review](../reviews/FEA-GATE-READINESS-review.md) P1-1/P1-2

---

## FEA-D06-GAP

**目标**：补齐 D06（Run 快照）四项未覆盖的声明范围，使 `G-DELETE-CONTRACT` 的 D06 条件可判定。

**背景**：C-08 只覆盖 D06 六项中的 2 项（preview 与发送同源、不可变内容 pin）+ 候选/配置/完整性。以下 4 项**无任何冻结契约承载**：

| # | 缺失项 | 现状 | 可能承载方式 |
|---|---|---|---|
| 1 | **控制 pending 状态** | C-08 无条款；M2-C1 §5.5（**已冻结**）有 `ControlRun` + 状态迁移表 `:212`–`:216` | **写映射即可**：C-08 引用 M2-C1 §5.5 并声明「控制期间的 pending 语义由该冻结面承载」+ 补 Run 侧不变量（如「pending 期间不得重复提交」） |
| 2 | **真实完成口径** | 12 份契约 + M2-C1 **0 命中** | **须新写**：定义「什么算真完成」（事件 ≠ 状态真值；须以 Core 持久状态为准；`Completed` 与 `CompletedWithFailures` 的区别；失败页的处理） |
| 3 | **retry 是否复用 source run 快照** | 只有「更新快照=新 Run（`source_run_id`）」 | **须明确回答**：retry 复用与否；若不复用，旧快照何时可回收 |
| 4 | **断线 receipt** | **0 命中**（C-01b SC-34 的 receipt 是删除 operation，与 Run 断线无关）；M2-C1 §7.2 是 Proposed | **须新写**：断线后如何判定「这次请求到底生效没有」；receipt 的字段与生命周期 |

**范围**：
- 允许写：`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`（需 UNFREEZE 载体，因为 C-08 已冻结）、`doc/reviews/CONTRACT-UNFREEZE-C08-<DATE>.md`、`doc/tasks/FEA-D06-GAP.md`、STATUS/PLAN/LEDGER
- 禁止：改代码、改 M2-C1 字节（那属块② 独立 Task）

**验收**：
- AC1 四项各有条款或明确的「由 X 冻结面承载」映射，且映射可核（给行号）
- AC2 经独立复核 `approved`
- AC3 C-08 冻结记录的 D06 覆盖声明更新为准确状态
- AC4 `check.ps1` + `verify_pins.ps1` PASS

**风险**：C-08 已冻结，补条款须走 UNFREEZE；若第 2、4 项需要新协议字段，则须同时评估是否扩 M2-C1（与块② 合并或独立）。

---

## FEA-D07-UNBLOCK

**目标**：解除 `G-DELETE-CONTRACT` 的 D07 缺口与 C-09↔Gate 循环。

**背景**：D07 的多项未冻内容全在 C-09 草案里，而 C-09 的条件③要求「两 Gate 关闭」→ 死锁。

**三个候选方案**（复核给出，择一并在留痕中写明理由）：

| 方案 | 做法 | 代价 | 风险 |
|---|---|---|---|
| **① 改 C-09 条件③** | 改为「`G-CONTRACT` 关闭 + `G-DELETE-CONTRACT` 的 D04/D05/D06 部分关闭」这类**可满足形式**，先冻 C-09 | 需说明「D07 自身的备份/迁移面由 C-09 承载」的先后关系 | 循环定义被打破，但 C-09 冻在 Gate 前会削弱 Gate 的守门作用 |
| **② 拆独立小契约** | 把 `backup/2`、旧包 legacy adapter、自动备份调度归属、`catalog` 归属拆成独立小契约（如 C-15）先冻 | 多一份契约 + 一轮复核 | 最干净：Gate 的 D07 条件由多个小契约共同满足；但 C-09 自身仍要补这些条款，可能重复 |
| **③ 重定义 Gate 边界** | 在 Gate 定义中明确「D07 的备份/迁移面由 C-09 承载，Gate 关闭以 C-09 回归为后置」并据此改 ADJ-001 §9 + 矩阵 | 改的是 Gate 定义本身（影响面最大） | 需用户确认；否则等于自我放宽 |

**推荐**：**②**——拆独立小契约最符合「不自我放宽」的原则，且 `backup/2`/旧包 adapter 本来就是可独立成文的格式契约。

**范围**：
- 允许写：`doc/plan/FEA-C15_*.md`（或所选载体）、`doc/tasks/FEA-D07-UNBLOCK.md`、ADJ-001 §9（仅 Gate 状态行）、矩阵、STATUS/PLAN/LEDGER
- 禁止：改已冻结契约字节（除非走 UNFREEZE）

**验收**：
- AC1 循环被显式打破，且留痕写明「为什么这个改法不是自我放宽」
- AC2 `G-DELETE-CONTRACT` 的 D07 条件可判定（满足 / 仍需 X）
- AC3 C-09 的可冻性重新评估并记录
- AC4 独立复核 `approved`

---

## 依赖与顺序

1. **FEA-D06-GAP** 与 **FEA-D07-UNBLOCK** 可并行（不同文件）
2. 两者都完成 + 复核通过后，才评估 `G-DELETE-CONTRACT` 是否关闭
3. C-09 冻结在两者之后

## 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：D06 四项缺口表 + 承载可行性、D07 三个解环方案 + 推荐、范围与验收、依赖顺序 | DSH |
