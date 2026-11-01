# C04b 删除协议字段与码表 · 冻结记录

**契约**：`doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md`
**冻结时间**：2026-11-01
**冻结人**：DSH（Lead / Architect / Integrator）
**授权**：[Gate 阻塞口径裁定 v2](GATE-CLOSURE-RULING-2026-11-01.md)（[复核 approved](../reviews/GATE-CLOSURE-RULING-r2.md)）+ [冻结矩阵](FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 1. 冻结字节

| 项 | 值 |
|---|---|
| 文件 | `doc/plan/FEA-C04b_DELETE_PROTOCOL_DRAFT.md` |
| sha256 | `694ce5bc8c8bcb21f45858e57a110d3b5c02ec48f487980d9119a122cd419947` |

**冻结语义**：条款字节自本记录起不得改动；修订须走 UNFREEZE 载体（`doc/reviews/CONTRACT-UNFREEZE-<DATE>.md`）+ 重新独立复核 + 重新冻结。

## 2. 冻结条件逐条核验

| # | C-04b §5 条件 | 状态 | 证据 |
|---|---|---|---|
| 1 | 独立复核通过 | ✅ | r1（5 P1）→ r2（1 P1）→ r3 [approved](../reviews/FEA-GOV-5-c04b-r3.md)；Gate 口径修订后 [再次确认](../reviews/GATE-CLOSURE-RULING-r2.md) |
| 2 | C-01b 已冻结（语义先行） | ✅ | [FEA-CONTRACT-FROZEN-C01b](FEA-CONTRACT-FROZEN-C01b.md) |
| 3 | `G-DELETE-CONTRACT` **不阻塞本单** | ✅ | [裁定 v2](GATE-CLOSURE-RULING-2026-11-01.md) R-1′：Gate 保持 OPEN；本单只承载 D07 |
| 4 | DSH 批准协议 minor `2.11` | ✅ | 裁定 R-3（新增 1 命令 + 2 码；兼容性**依赖旧端 fail-closed**，不依赖旧端接受新码） |
| 5 | M2-C1 扩展**方案**已冻结在 §2.4 | ✅ | §2.4 列 4 个扩展点；**字节修订**是释放前置（见 §4） |
| 6 | `check.ps1` PASS | ✅ | PASS（3 persistent warnings） |

## 3. 依赖与后果

- **上游**：C-01b 已冻结（SC-30/31/33 的协议层落地）。
- **下游**：C-09（删除/备份/迁移）仍 blocked —— 其条件②「两 Gate 关闭」**不满足**（Gate 保持 OPEN）。
- **释放实现前必须完成**（裁定 R-2′）：M2-C1 §5.11.3 表 + 两个 ErrorView 的**字节修订**由**独立 Task**（**不得并入任何删除实现 Task**）完成并复核，复核须含**负向对照**：未扩 M2-C1 时新码必须被 host 投影拒绝。
- **本裁定不新增运行时保证**：`PermanentlyDeleteBookErrorView` 与两新码在 `apps/**`+`src/**` 0 命中，host 投影未接线——"新码不能用"是**契约纪律**，靠该独立 Task 的 AC 与 Review 落实。

## 4. 不构成什么

- **不构成**实现授权。**不构成** Gate 关闭（`G-DELETE-CONTRACT` / `G-CONTRACT` 均**保持 OPEN**）。
- **不构成**远端 push 授权。

## 4A. 已知限制（冻结后发现）

- **L-1**（来自 [FEA-C13-r2](../reviews/FEA-C13-r2.md)，2026-11-01）：book 级聚合 digest 对「**计数不变而分布变**」（A 区加锁 + B 区解锁）不敏感；**region 级指针**不进 book 级 `currentRevisionId`。这是 `inventory_digest` 的粒度局限，**本契约冻结时已知**。C-13 的 `protectionDigest` 是**编辑层**的逐 Region 摘要，不替代本契约的 book 级 digest，也不接入删除 preflight。若删除线实现需要逐 Region 检测，须走本契约的 **UNFREEZE** + 协议扩展。

## 5. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：冻结字节 pin、条件核验、依赖与后果 | DSH |
