# C03 外观持久化与字段迁移 · 冻结记录

**契约**：`doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[用户裁决记录 2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)（U-05a=纳入 / U-05b=保留 / U-05c=A 用户优先）

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C03_PRESENTATION_SETTINGS_DRAFT.md` |
| 版本 | **v6** |
| sha256 | `85a75d367bf977a65434d419e20d8a110728eb6b33e30c73a32381f3ee917ecb` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 2. 冻结条件逐条核验（5/5）

| # | C-03 §4 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过（上下文独立） | ✅ | r1（2 P1）→ r2 [approved](../reviews/FEA-GOV-4-c03-r2.md)；Codex 意见后的 v5 修正确认：[FEA-GOV-12](../reviews/FEA-GOV-12-review.md) pproved（P0×0 / P1×0 / P2×5） |
| 2 | 用户裁决 U-05a / U-05b | ✅ | U-05a=**纳入**（三态三类）、U-05b=**保留**（转只读） |
| 3 | C-02 已冻结（本单在 C-02 之上） | ✅ | [FEA-CONTRACT-FROZEN-C02](FEA-CONTRACT-FROZEN-C02.md)（2026-11-01） |
| 4 | 用户裁决 U-05c（v5 新增） | ✅ | **A 用户显式优先**（uto 跟随 / ull 覆盖 / educe 强制） |
| 5 | `check.ps1` PASS | ✅ | 冻结时 PASS（3 persistent warnings） |

## 3. 迁移映射（冻结口径）

| 旧 `ReducedMotion` | 新 `motion.mode` | 备注 |
|---|---|---|
| `true` | `reduce` + 三类全禁 | 等价旧 `Motion.Reduced.axaml`（全时长 0 + `Enabled=False`） |
| `false` | **`full`** | 等价旧 `SetReducedMotion(false)`（移除覆盖层）；**不是 `auto`**（Codex 意见 ③ 修正） |
| （新选项） | `auto` | 仅由用户显式选择 / 新安装默认产生，不从旧布尔推导 |

## 4. 依赖与后果

- **上游**：C-02 已冻结（材质/圆角/动效的视觉例外由 C-02 V-05 定义）。
- **下游**：FEA-05（ThemeEngine 实现）/ FEA-04b（外观面板）释放条件：本单冻结 + C-11 建卡 + 独立 Review。
- **实现铁律**（两条，来自 Codex 意见核验）：
  1. **顺序铁律**：旧文件转只读必须在保存路径完全接管之后（否则 `TrySave` 异常被 `ThemeService.cs:654` 吞掉 → 界面已应用但设置没保存）。
  2. **迁移按持久化值域等价**：排除 overlay 加载失败的瞬时行为。

## 5. 已知限制

- **L-1**（冻结后发现，登记于 C-02）：C-02 V-05 判据④只禁「提高全局 `ThemeCorners.MaxRadius`」，未指定 Fluent 的「限定校验路径」落点（`ThemeValidator.ValidateCorner` 对所有 corner 键套共享上限）。需在 FEA-05 实现 Task 中细化，或走 C-02 的 UNFREEZE。

## 6. 不构成什么

- **不构成**实现授权（实现须按 C-11 选候选 → 建 Task → 独立 Review）。
- **不构成**远端 push 授权。

## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin（v6）、条件 5/5、迁移映射表、实现铁律、已知限制 L-1 | DSH |
