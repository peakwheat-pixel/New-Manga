# C05 页可见性谓词 · 冻结记录

**契约**：`doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md`
**冻结时间**：2026-11-01（v1.0）/ 2026-11-03（v1.1）/ 2026-11-04（v1.2）
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[用户裁决记录 2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md) + [冻结矩阵](../plan/FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C05_PAGE_VISIBILITY_DRAFT.md` |
| 冻结版本 | **v1.2**（2026-11-04 UNFREEZE 重冻；v1.1/v1.0 历史） |
| sha256（v1.2 冻结后最终字节，verify_pins 口径） | `f6e6f3cb1fe19b253688f14ddf55f106b8bb89d3d3ab946a185cc12c34dc4714` |
| git hash-object（v1.2 blob id） | `32d039c0e8d10063076ecded1b333a4f4a512ab6` |
| blob 内容 sha256（LF 原始字节） | `f6e6f3cb1fe19b253688f14ddf55f106b8bb89d3d3ab946a185cc12c34dc4714` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核 | r3 approved（FEA-GOV-6-c05-c06-r3） |
| 复核后到冻结的改动 | 仅状态行 |
| 处置 | 无需补复核 |

| **v1.1 复核（2026-11-03）** | r7 approved（`doc/reviews/FEA-09-PREREQ-1-r7.md`） |
| **v1.1 复核字节** | `13ff436af7bfbdc2a65181153a2b6140902e4aff1a8665a28e1c9c5b60167a39`（工作树 SHA-256，草案 v1.1） |
| **v1.1 冻结字节** | `a234346fb0eec2304c598024740bd0c26eea18117dde6dae5b49410192d58e82`（仅状态行由 UNFREEZE 草案改为 FROZEN v1.1；条款字节=复核字节） |
| **v1.0 pin（历史，保留）** | `b34db88768790a982c00d6b78a9649c24047e15d2ba86e3c0bf6a5a293ec8d25` |
**为什么必须有这一节**：冻结条件①是「独立复核通过」，若冻结字节 ≠ 复核字节，该条件在证据上不覆盖被冻内容。本节的目的是把差异显式化，而不是掩盖它。

## 2. 冻结条件逐条核验

| # | C-05 §7 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过（上下文独立） | ✅ | r1→r2→r3 [approved](../reviews/FEA-GOV-6-c05-c06-r3.md)（P0×0 / P1×0 / P2×4） |
| 2 | `VISIBLE_TYPES` 与 `active_runs` 语义经 C-01b/ADJ-001 确认 | ✅ | C-01b **已冻结**（[冻结记录](FEA-CONTRACT-FROZEN-C01b.md)）：`ACTIVE_STATES` 与 `core_assembly.py:171-181` 一致、`VISIBLE_TYPES` 与 `artifact_type` CHECK 一致 |
| 3 | `check.ps1` PASS | ✅ | 冻结时 PASS（3 persistent warnings） |

## 3. 依赖与后果

- **上游**：C-01b 已冻结（SC-30/31/33 的 ADJ-001 依赖已注明）。
- **下游**：C-08（Run 快照）冻结条件①要求 C-05 已冻结 → **本记录使 C-08 第 5 步解锁**。
- **实现**：C-05 是谓词定义，无独立实现 Task；由使用它的导出（FEA-14-EXPORT）与删除预览（C-04b）承载。

## 4. 不构成什么

- **不构成**实现授权（实现须按 C-11 选候选 → 建 Task → 独立 Review）。
- **不构成**远端 push 授权。

## 1A. pin 修正记录（2026-11-01，**保留原值**）

| 项 | 值 |
|---|---|
| 原 pin（**错误口径**） | `e48707cf8aa8805b99375db267849269338266631d9a6169512c9e343f926e53` |
| 修正后 pin（最终字节） | `b34db88768790a982c00d6b78a9649c24047e15d2ba86e3c0bf6a5a293ec8d25` |
| 差异范围 | **仅状态行** DRAFT→FROZEN，条款字节未动 |

**为什么保留原值**：pin 是证据，不能静默替换。原值可独立复现（还原本次冻结动作后重算即得），因此证明冻结前的确切字节；修正后的值才是后续校验基准。

**冻结字节 = 复核字节？** 见 §1B。

**纪律（自本记录起）**：
1. pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；
2. 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；
3. 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径；
4. **冻结提交本身不得含条款编辑**——最后处置必须在冻结**之前**的独立提交完成并经复核。


**为什么保留原值**：pin 是证据，不能静默替换。原值证明「条款内容与冻结前一致」（状态行是元数据，条款字节未动）；修正后的值才是后续校验的基准。

**纪律（自本记录起）**：① pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；② 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；③ 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径。
## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin、条件核验、依赖与后果 | DSH |
| 2026-11-01 | pin 修正：原 pin 指向冻结前草案（状态行改动前），改为最终字节 `b34db88768790a982c00d6b78a9649c24047e15d2ba86e3c0bf6a5a293ec8d25`；新增 §1A 修正记录与纪律（见上） | DSH |

| 2026-11-03 | **UNFREEZE v1.1 重冻**：referenced 页可见性分支 + 三谓词拆分（[载体](../reviews/CONTRACT-UNFREEZE-2026-11-03.md)）；r7 approved；新 pin `a234346fb0eec2304c598024740bd0c26eea18117dde6dae5b49410192d58e82`；保留 v1.0 pin 于 §1A/§1B | DSH；FEA-09-PREREQ-1 |
## 6. v1.2 UNFREEZE 重冻（2026-11-04）

| 项 | 值 |
|---|---|
| 载体 | `doc/reviews/CONTRACT-UNFREEZE-2026-11-04.md` |
| 语义修订提交（复核字节） | `ed570681b57e1343cb8c477f5dd7d23200a2dab4` |
| 已提交字节独立复核 | ZCode `sess_1517188b…`（P1→补正）→ `ed570681b` 补正提交 `a9276fbae…` → ZCode `sess_f155bf21…` **approved P0/P1/P2=0** |
| 复核字节 sha256 | `284ce9552e4d569e67bc885386c316b5c40c971e2eb33b578abfeec5429357e7` |
| 冻结字节 sha256 | `f6e6f3cb1fe19b253688f14ddf55f106b8bb89d3d3ab946a185cc12c34dc4714`（**仅状态行**差异） |
| 历史 pin（保留） | v1.1 `a234346fb0ee…`；v1.0 `b34db8876879…` |
| 修订内容 | `V_managed=V_artifact∨V_copy_original`、witness 独立、V/R 分离、反例 1–8、参考投影 |
