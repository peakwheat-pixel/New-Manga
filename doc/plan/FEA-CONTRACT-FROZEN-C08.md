# C08 Run 快照 · 冻结记录

**契约**：`doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[Gate 阻塞口径裁定 v7](GATE-CLOSURE-RULING-2026-11-01.md)（R-4 + [r8 复核](../reviews/GATE-CLOSURE-RULING-r8.md) pproved）+ [冻结矩阵](FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C08_RUN_SNAPSHOT_DRAFT.md` |
| 版本 | **v5 起冻 / v6 正文 / v7（r11 P2）**；r12 终检后按 `453f993c…` 重冻 |
| sha256（冻结后最终字节） | `453f993c1a16eab9db783f5b3a24710ac6e24b9a290a2b05bcba45f463fa8517` |

## 1B. 冻结字节 vs 复核字节

| 项 | 值 |
|---|---|
| 最后一次独立复核 | **r12 `approved`**（[FEA-C08-r12](../reviews/FEA-C08-r12.md)）：4 项终检全部到位，结论「AC7 可签」 |
| 复核后到冻结的改动 | 前置（b）`:1119` 例外 + 变更记录 + 状态行 |
| 处置 | **已补复核**（[FEA-CONTRACT-BYTES-r1](../reviews/FEA-CONTRACT-BYTES-r1.md)）；D06 四项经 r9（2 P1 → v6）→ r10/r11（记录同步）→ **r12 `approved`**；pin 定稿 `453f993c1a16eab9…` |

**为什么必须有这一节**：冻结条件①是「独立复核通过」，若冻结字节 ≠ 复核字节，该条件在证据上不覆盖被冻内容。本节的目的是把差异显式化，而不是掩盖它。

## 2. 冻结条件逐条核验（5/5）

| # | C-08 §5 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过 | ✅ | r1（3 P1）→ r2 [approved](../reviews/FEA-GOV-7-r2.md)；R-4 处置后 [r8 复核](../reviews/GATE-CLOSURE-RULING-r8.md) pproved |
| 2 | C-01b 已冻结（顺序） | ✅ | [FEA-CONTRACT-FROZEN-C01b](FEA-CONTRACT-FROZEN-C01b.md) |
| 3 | 前置（a）C-05 与 C-04b 已冻结 | ✅ | [C05](FEA-CONTRACT-FROZEN-C05.md)、[C04b](FEA-CONTRACT-FROZEN-C04b.md) |
| 4 | 前置（b）协议注册（**R-4 降级为释放前置**） | ✅ | 方案已冻结在 §3；M2-C1 字节修订由独立 Task 在释放 Run 实现前完成 + 负向对照（host 白名单降级） |
| 5 | `check.ps1` PASS | ✅ | PASS（3 persistent warnings） |

## 3. 协议注册（块②，释放前置）

| 项 | 内容 |
|---|---|
| M2-C1 §5.5 | 命令表追加 PrepareRun/AcceptRun 两行 |
| 3 个新码 | RUN_STALE_PREVIEW(conflict/false) / RUN_PREVIEW_EXPIRED(conflict/false) / RUN_SNAPSHOT_INCOMPLETE(unavailable/true) |
| §8 | 新增「Proposed（未观察）」小节 3 行 + :1119 retryable 证据规则例外 + :1122 taxonomy 例外 |
| **host 投影层** | 新增 `allowedRunErrorCodes` 白名单：未注册码 → `category=unknown` + 安全短消息、**不重写 `code`**、不作 UI 分支依据 |
| wire 版本 | **minor 2.12**（DSH 批准） |
| 与 C-04b 共用 Task | **块②**（块①= C-04b 删除章节增量）；两段独立提交、AC 分包、上限 5 提交 |

**负向对照**：未扩 M2-C1 时，3 个新码必须被 host 投影**降级为 category=unknown**（不是拒绝——删除线有封闭 ErrorView，Run 线没有）。

## 4. 依赖与后果

- **上游**：C-01b、C-05、C-04b 均已冻结。
- **D06 覆盖状态（2026-11-01，v5 更新）**：本契约现覆盖 D06 六项声明**全部**——①preview 与发送同源 SC-R01 ②不可变内容 pin SC-R02 ③控制 pending 状态 SC-R06 ④真实完成口径 SC-R07 ⑤retry 快照来源 SC-R08 ⑥断线 receipt SC-R09。D06 条件**以 AC8 的完整覆盖检查为准**。
- **Gate 仍不自动关闭**：D06 已由本契约覆盖；`G-DELETE-CONTRACT` 的关闭须经 AC8 完整覆盖检查 + AC9 裁定（C-09 已解环并冻结，不再构成阻塞）。
- **实现**：FEA-03/FEA-13（Run 快照相关）释放需前置（b）完成 + C-11 建卡 + 独立 Review。

## 5. 已知限制

- **L-1**：preparedDigest 的 canonical JSON 定义已冻结，但**逐字段 wire 编码**留给块② Task。
- **L-2**：防抖/过期（≤10 分钟）为建议值，待实现实测。

## 6. 不构成什么

- 不构成实现授权；不构成 Gate 关闭；不构成远端 push 授权。

## 1A. pin 修正记录（2026-11-01，**保留原值**）

| 项 | 值 |
|---|---|
| 原 pin（**错误口径**） | `5864a098109212b8db9060253196738dcae2aff6bc646ab296a521677b6120e6` |
| 修正后 pin（最终字节） | `37586fb2bfd2a2725d2851ca4db6f12533679eea18f22358f9ae144441bc78a9` |
| 差异范围 | 冻结提交内**同时含前置（b）的 `:1119` retryable 证据规则例外 + 变更记录改写**（来源＝裁定 r7/r8 的复核建议） |

**为什么保留原值**：pin 是证据，不能静默替换。原值可独立复现（还原本次冻结动作后重算即得），因此证明冻结前的确切字节；修正后的值才是后续校验基准。

**冻结后补充（2026-11-01，FEA-D06-GAP）**：按 [CONTRACT-UNFREEZE-C08-2026-11-01](../reviews/CONTRACT-UNFREEZE-C08-2026-11-01.md) 新增 SC-R06…SC-R09 四项（D06 声明范围的剩余四项：控制 pending 状态 / 真实完成口径 / retry 快照来源 / 断线 receipt）。这是**冻结后的条款新增**，走 UNFREEZE 载体而非仅重算 pin；pin 已更新为 `453f993c…`（历史值 `2e7a5f2b…`/`b509271c…`）。

**冻结字节 = 复核字节？** 见 §1B。

**纪律（自本记录起）**：
1. pin **必须在冻结动作全部完成后**计算（含状态行、U-03 等元数据改动）；
2. 冻结后任何字节改动（含状态行）都必须**重算 pin 或走 UNFREEZE**；
3. 建议同时记录 worktree sha256 与 `git cat-file blob`（LF）sha256 双口径；
4. **冻结提交本身不得含条款编辑**——最后处置必须在冻结**之前**的独立提交完成并经复核。

## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 冻结后补充（FEA-D06-GAP）：新增 SC-R06…SC-R09 四项，走 UNFREEZE 载体；pin 更新 | DSH |
| 2026-11-01 | 建立：冻结字节 pin（v4）、条件 5/5、协议注册块②、依赖与后果、2 条已知限制 | DSH |
| 2026-11-01 | pin 修正：原 pin 指向冻结前草案（状态行改动前），改为最终字节 `37586fb2bfd2a2725d2851ca4db6f12533679eea18f22358f9ae144441bc78a9`；新增 §1A 修正记录与纪律（见上） | DSH |

## 8. Errata 注记（2026-11-01 追加；**原文保留**）

按 [关闭裁定 §4](GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md) 的 Errata 表（L-3）：**经全文核对，本记录原本就不含「D07 缺多项」表述**（除本节外全文 0 命中），因此无需更正原文；裁定 §4 括注所称「以其 §5 历史段落为准」在本记录中**指向落空**——§5 只有 L-1（preparedDigest 逐字段 wire 编码）与 L-2（防抖/过期建议值）两条实现限制，§7 变更记录亦无 D07 表述。该括注的不精确**按用户指令不在 Errata 中改裁定正文**，仅在此留痕。本次只追加确认，不改原文：

- §4（`:55`）「Gate 仍不自动关闭…须经 AC8 完整覆盖检查 + AC9 裁定」**已履行**：AC8（`FEA-D04D07-COVERAGE-r3` `approved`）与 AC9（`GATE-DELETE-CONTRACT-CLOSURE-r3` `approved`）均完成，两 Gate 于 2026-11-01 **CLOSED**。
- §6（`:65`）「不构成 Gate 关闭」为**冻结时**状态描述；现行两 Gate 均 **CLOSED**（[关闭裁定](GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md)）。
- C-08 草案字节未改（pin `453f993c…`，`verify_pins.ps1` 13/13）。
