# C02 V11R 条款级修订单 · 冻结记录

**契约**：`doc/plan/FEA-C02_V11R_AMENDMENT_DRAFT.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[用户裁决记录 2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md) + [冻结矩阵](../plan/FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C02_V11R_AMENDMENT_DRAFT.md` |
| sha256（冻结后最终字节） | `bb365ca891a7d48960da4a593d2f3f5e3785727a63fc4f5a2016732b06b1565a` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 2. 冻结条件逐条核验

| # | C-02 §6 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核确认与 V11R 合同、FEA 方案 r4 一致、无新增语义 | ✅ | r1（4 P1：项目授权/双 id/§6.3 拆分/圆角组）→ r2 [approved](../reviews/FEA-GOV-4-c02-r2.md)（P0×0 / P1×0 / P2×3） |
| 2 | 用户裁决 **U-04**（V-05 两行 per-scheme 例外） | ✅ | [ADJ-2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)：**批准**（per-scheme + 令牌强制） |
| 3 | `check.ps1` PASS | ✅ | 冻结时 PASS（3 persistent warnings） |

## 3. 依赖与后果

- **上游**：C-01b 已冻结（V-07 的 ThemeKind 冻结面与其一致）。
- **下游**：**C-03 冻结条件③要求 C-02 先冻结 → 本记录使 C-03 解锁**；Fluent 实现 Task 释放须再满足 C-11 建卡 + 独立 Review。
- **实现注意**：V-05 判据④ —— 禁止提高全局 `ThemeCorners.MaxRadius`；Fluent 圆角走独立键组 + 限定校验路径。

## 4. 已知限制（冻结后发现）

- **L-1**（来自 [FEA-GOV-12](../reviews/FEA-GOV-12-review.md) P2-5，2026-11-01）：V-05 判据④只禁「提高全局 `ThemeCorners.MaxRadius`」，未指定 Fluent 的「限定校验路径」落点——`ThemeValidator.ValidateCorner` 对所有 corner 键套共享上限，`Nm.Corner.Fluent.*` 的 4/6/8 需要独立路径。**不得为此 UNFREEZE C-02**；由 FEA-05 实现 Task 在 `ThemeValidator` 内加限定路径（不改全局上限）解决。

## 5. 不构成什么

- **不构成**实现授权（实现须按 C-11 选候选 → 建 Task → 独立 Review）。
- **不构成**远端 push 授权。

## 1A. pin 修正记录（2026-11-01，**保留原值**）

| 项 | 值 |
|---|---|
| 原 pin（**错误口径**） | `ecae0c8dfb3de5319dc8508e903ea704c0029cc65460f8e569731aa2b376b8f2` |
| 修正后 pin（最终字节） | `bb365ca891a7d48960da4a593d2f3f5e3785727a63fc4f5a2016732b06b1565a` |
| 差异原因 | 冻结动作本身把状态行从 `DRAFT` 改为 `FROZEN`，而原 pin 在**该改动之前**计算 → pin 指向冻结前的草案字节，未覆盖最终文件 |

**为什么保留原值**：pin 是证据，不能静默替换。原值证明「条款内容与冻结前一致」（状态行是元数据，条款字节未动）；修正后的值才是后续校验的基准。

**纪律（自本记录起）**：① pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；② 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；③ 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径。
## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin、条件核验、依赖与后果 | DSH |
| 2026-11-01 | 补 §4 已知限制 L-1（冻结后发现，来自 FEA-GOV-12 P2-5） | DSH |
| 2026-11-01 | pin 修正：原 pin 指向冻结前草案（状态行改动前），改为最终字节 `bb365ca891a7d48960da4a593d2f3f5e3785727a63fc4f5a2016732b06b1565a`；新增 §1A 修正记录与纪律（见上） | DSH |
