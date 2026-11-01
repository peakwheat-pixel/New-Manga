# Gate 关闭裁定 · `G-DELETE-CONTRACT`

状态：**ACTIVE / DSH 裁定**
裁定人：DSH（Lead / Architect / Integrator）
日期：2026-11-01
依据：[D04–D07 完整覆盖检查](D04-D07-COVERAGE-CHECK-2026-11-01.md)（**r3 `approved`**，[FEA-D04D07-COVERAGE-r3](../reviews/FEA-D04D07-COVERAGE-r3.md)）+ 用户 2026-11-01 裁决「补齐并复核最终字节、重新冻结后，再做一次 D04–D07 完整覆盖检查并决定关闭 Gate」

---

## 1. 裁定

| Gate | 定义（原文） | 原状态 | **裁定后** |
|---|---|---|---|
| **`G-DELETE-CONTRACT`** | 「协议字段/码表/**D04-D07** 冻结」（[ADJ-001 §9](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md)） | OPEN | **✅ CLOSED（2026-11-01）** |

**两条 Gate 的最终状态**：

| Gate | 状态 |
|---|---|
| `G-CONTRACT`（D05） | **CLOSED**（2026-11-01，[前一份裁定](GATE-CONTRACT-CLOSURE-2026-11-01.md)） |
| `G-DELETE-CONTRACT`（D04–D07） | **CLOSED**（本裁定） |

## 2. 关闭依据：D04–D07 四包条款级承载全部完成

| 包 | 声明范围 | 承载契约 | 独立复核 |
|---|---|---|---|
| **D04** 草稿/保护/结果 | 6 项（方案 `:767`） | C-13 SC-D01…D12 | 6/6 ✅ |
| **D05** Source/grant/资源 | 5 项 | C-06 + C-14 + C-01b | 5/5 ✅ |
| **D06** Run 快照 | 6 项（FEA-01 `:57`） | **C-08 v7**（SC-R06…R09 补齐四项） | 6/6 ✅ |
| **D07** 删除/备份/迁移 | 7 项（FEA-01 `:58`）+ 方案 `:770` 的 2 项 | **C-09 v5** + C-01b + C-04b | 前 6 项 ✅ / **行 7 ⚠ 部分**（见 L-5） |

**13 份契约全部冻结**，`verify_pins.ps1` **13/13 PASS**。

## 3. 明文保留项（**必须与裁定一同生效**）

复核特别强调：**L-5 若不在裁定里明文保留，Gate 关闭就会在「整库恢复锁」上留下未记账的口子**。

| # | 保留项 | 处置 |
|---|---|---|
| **L-5** | **整库恢复（C-09 SC-B02/SC-B09）未明文要求持 C-01b SC-17 的独占维护锁**；方案 `:530` 有要求，契约未落实 | **本裁定认定**：整库恢复**按迁移处理**，实现时**必须持 SC-17 的独占维护锁**（停所有写者/Run/lease、staging、校验、commit marker 后才切换）。**该认定是实现前置约束**，不改变已冻结契约的字节；若后续要写入 C-09，走 UNFREEZE |
| L-1 | 四张表（`source_entries`/`page_bindings`/`source_sync_plans`/`source_operations`）的 **DDL 未冻结** | 保留为 Source 线**生产实现前置**；承载方式与时点见 [G-CONTRACT 裁定](GATE-CONTRACT-CLOSURE-2026-11-01.md) §3.3 |
| L-2 | **M2-C1 字节修订未做**：`PrepareRun`/`AcceptRun` + 3 码、`§8 Proposed（未观察）` 小节、`allowedRunErrorCodes` 白名单（C-08 块②）；`TRASH_*` 3 码（C-09 SC-B06） | 作为**实现前置 Task**；未扩时 host 投影层须降级为 `category=unknown`（负向对照已写入 C-08/C-09） |
| L-3 | **旧口径残留**：C-13 `:203`、C-04b/C-08/C-13 冻结记录、GATE-CLOSURE-RULING `:63`/`:111`、ADJ-001 `:128` 等仍写旧「D07 缺多项且与 C-09 循环」 | 由**本次 Errata**（§4）统一更正；冻结契约正文不改 |
| L-4 | **C-04b 的 pending operation 披露字段未加入** | C-14 SC-S08 需求声明；属 C-04b UNFREEZE（实现前置） |
| L-6 | C-14 的 L-3：`scope.entry` ↔ `EntryId` 对齐规则待 C-06 侧/协议实现确认 | 实现前置 |
| L-7 | C-13 L-1 / C-04b L-1：`protectionDigest` 是编辑层摘要、不接入删除 preflight；book 级聚合对「计数不变而分布变」不敏感 | 影响**实现层检测精度**，不改条款承载 |
| L-8 | C-08 L-1/L-2：wire 编码与防抖值为实现前置（含 `RUN_*` 3 码 + §8 Proposed） | 实现前置 |
| L-9 | C-09 L-3：`settings/` 包内相对路径 vs 磁盘路径以 C-03 为准，未做实现级复核 | 实现前置 |

## 4. Errata（旧口径统一更正）

以下文件里的**过期表述**在本裁定生效后按此更正（只改状态描述，不动冻结字节）：

| 文件 | 过期表述 | 更正为 |
|---|---|---|
| `ADJ-001 §9 :128` | 「OPEN（D06 缺 4 项 / D07 缺多项且与 C-09 循环）」 | **CLOSED（2026-11-01）**，见本裁定 |
| `FEA-CONTRACT_FREEZE_MATRIX.md` | D06/D07 的陈旧阻塞列 | 指向本裁定 |
| `FEA-CONTRACT-FROZEN-C04b.md` / `-C08.md` / `-C13.md` | 旧「D07 缺多项」口径 | 以本裁定为准 |
| `GATE-CLOSURE-RULING-2026-11-01.md :63/:111` | 同上 | 以本裁定为准 |
| `FEA-C13_DRAFT_PROTECTION_DRAFT.md :203` | 同上 | 以本裁定为准 |

## 5. 关闭意味着什么 / 不意味着什么

**意味着**：
- D04/D05/D06/D07 的**契约语义**已全部有冻结承载；
- 删除线的**契约级**前置已完成，`G-DELETE-IMPL`（Core 实现 + 故障回归）可以按 Task 计划评估释放。

**不意味着**：
- ❌ **不构成 `G-DELETE-IMPL` 的关闭或自动释放**——实现仍需按 C-11 选候选 → 建 Task → 独立 Review。
- ❌ **不构成 DDL 已冻结**（L-1）。
- ❌ **不构成 M2-C1 字节修订已完成**（L-2）。
- ❌ **不构成整库恢复可以不加锁**（L-5 的认定必须实现）。
- ❌ **不构成远端 push 授权**。

## 6. 后续

| 项 | 说明 |
|---|---|
| C-09 | 已于 2026-11-01 冻结（解环后）；本裁定不改变其字节 |
| C-10 交互契约 | U-03 已裁（B），可起草；**不受本裁定阻塞** |
| 实现 Task | 须按 C-11 选候选、建 Task、独立 Review；本裁定只解除**契约级**阻塞 |

## 7. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：`G-DELETE-CONTRACT` CLOSED、D04–D07 四包覆盖依据、9 条保留项（**L-5 明文认定**）、Errata、边界声明 | DSH |
