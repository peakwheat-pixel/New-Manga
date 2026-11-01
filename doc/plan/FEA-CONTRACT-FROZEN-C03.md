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
| sha256（冻结后最终字节） | `b77e7968a00b4c35c7b3cd03efe92f1999a3b9c6dec4a22ff5c504c8211608be` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核 | v5 approved（FEA-GOV-12-review） |
| 复核后到冻结的改动 | v6 四处内容修订（行号/U-05c 案 C/命名映射/等价性限定）+ 状态行 |
| 处置 | **已补复核**（[FEA-CONTRACT-BYTES-r1](../reviews/FEA-CONTRACT-BYTES-r1.md)：差异方向在复核建议内、无越界新增） |

**为什么必须有这一节**：冻结条件①是「独立复核通过」，若冻结字节 ≠ 复核字节，该条件在证据上不覆盖被冻内容。本节的目的是把差异显式化，而不是掩盖它。

## 2. 冻结条件逐条核验（5/5）

| # | C-03 §4 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过（上下文独立） | ✅ | r1（2 P1）→ r2 [approved](../reviews/FEA-GOV-4-c03-r2.md)；Codex 意见后的 v5 修正确认：[FEA-GOV-12](../reviews/FEA-GOV-12-review.md) pproved（P0×0 / P1×0 / P2×5） |
| 2 | 用户裁决 U-05a / U-05b | ✅ | U-05a=**纳入**（三态三类）、U-05b=**保留**（转只读） |
| 3 | C-02 已冻结（本单在 C-02 之上） | ✅ | [FEA-CONTRACT-FROZEN-C02](FEA-CONTRACT-FROZEN-C02.md)（2026-11-01） |
| 4 | 用户裁决 U-05c（v5 新增） | ✅ | **A 用户显式优先**（uto 跟随 / ull 覆盖 / 
educe 强制） |
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

## 1A. pin 修正记录（2026-11-01，**保留原值**）

| 项 | 值 |
|---|---|
| 原 pin（**错误口径**） | `85a75d367bf977a65434d419e20d8a110728eb6b33e30c73a32381f3ee917ecb` |
| 修正后 pin（最终字节） | `c188cf947cda971103a1ea17e1312ab6ce7ed27f0f734b975c6073a33ac1612e` |
| 差异范围 | 冻结提交内**同时含 v6 四处内容修订**：方案行号 `:866`→`:874`（补 `:1041`）、U-05c 补第三案 C、方案术语命名映射新段、迁移等价性限定新段（均为 FEA-GOV-12 r3 的 P2 建议转写） |

**冻结后措辞限定**（2026-11-01，提交 `a111b0873`）：按 [FEA-CONTRACT-BYTES-r1](../reviews/FEA-CONTRACT-BYTES-r1.md) 的 P2-1（方案三类 page-transition/overlay/hover 中**无 overlay 专类**），对「浮层 → decorative」加收窄限定（不新增语义）；pin 已随之更新。

**冻结字节 = 复核字节？** 见 §1B。

**纪律（自本记录起）**：
1. pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；
2. 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；
3. 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径；
4. **冻结提交本身不得含条款编辑**——最后处置必须在冻结**之前**的独立提交完成并经复核。



**为什么保留原值**：pin 是证据，不能静默替换。原值证明「条款内容与冻结前一致」（状态行是元数据，条款字节未动）；修正后的值才是后续校验的基准。

**纪律（自本记录起）**：① pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；② 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；③ 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径。
## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin（v6）、条件 5/5、迁移映射表、实现铁律、已知限制 L-1 | DSH |
| 2026-11-01 | pin 修正：原 pin 指向冻结前草案（状态行改动前），改为最终字节 `c188cf947cda971103a1ea17e1312ab6ce7ed27f0f734b975c6073a33ac1612e`；新增 §1A 修正记录与纪律（见上） | DSH |
