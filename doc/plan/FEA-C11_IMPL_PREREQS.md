# 实现线强制前置（L-1 / L-2 / L-5）· 用户 U-09 落实登记

状态：**登记文档（非契约、不冻结、不 pin）**。依据用户 2026-11-01 追加裁决 **U-09**（[ADJ-2026-11-01-FEA-DECISIONS](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)「追加裁决」）：**保留 L-1…L-9，不作整体豁免；四表 DDL、M2-C1 修订、整库恢复独占锁分别进入对应实现 Task 的明确前置与 AC。**

**来源（精确指向，供审计核对）**：
- 保留项清单与 L-1/L-2/L-5 原文：`doc/plan/GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md` **§3**（`:38`–`:48`，不是 §4）；
- L-1（四表 DDL 承载方式与时点）：`doc/plan/GATE-CONTRACT-CLOSURE-2026-11-01.md` §3.3 + `doc/plan/FEA-CONTRACT-FROZEN-C14.md` §5（L-1）；
- L-2（M2-C1 字节修订）：`doc/plan/FEA-CONTRACT-FROZEN-C09.md` §5（L-2）+ `doc/plan/FEA-CONTRACT-FROZEN-C08.md`（块②协议注册）；
- L-5（整库恢复独占锁）：C-09 冻结记录 §3（SC-17 独占维护锁）+ 裁定 §3（`:40`）；
- 候选 Task 与 write_scopes 口径：`doc/design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md` §15.6（`:912-940`）。
- 注意：C-09 冻结记录的 **L-1 是「K-5 外部记账残留」**（对应裁定保留项 L-3，非四表 DDL）；四表 DDL 的 L-1 由 **C-14** 冻结记录 §5 承载——两者编号相同但主体不同，引用时须写明承载文件（本条即 P2-001 的更正）。

## 0. 禁则（不得由本文档推导出任何豁免）

- 本文档**不构成**对 L-1…L-9 的豁免、**不构成**实现 Task 释放；`G-DELETE-IMPL` 仍 **OPEN**，候选 Task 须按 C-11 选候选并**经用户确认**后才可建卡/释放。
- 本文档**不修改**任何冻结契约字节（14 份 pin 不变），**不写入**已冻结的 C-11 草案正文。
- 前置未满足时，对应候选 Task **不得进入 `in_progress`**；若已建卡则必须停在 `proposed`/`blocked`。
- L-1/L-2 涉及的 schema 与 wire 字节修订本身属"新增/修改共享契约"，须走 `CONTRACT-UNFREEZE-*` 或新建契约，**不得在实现 Task 内顺手改**。

## 1. 逐项登记

| 保留项 | 内容（裁定原文摘要） | 归属候选实现 Task（方案 §15.6 口径） | 实现前必须完成的前置 | 必须写入候选 Task 的 AC | 证据计划（等级/位置） |
|---|---|---|---|---|---|
| **L-1** | **四张表**（`source_entries` / `page_bindings` / `source_sync_plans` / `source_operations`）的 **DDL 未冻结** → 保留为 Source 线生产实现前置；承载方式与时点见 G-CONTRACT 裁定 §3.3 | `FEA-03`（`src/application`/`src/domain`/`src/infrastructure/sqlite`）、`FEA-02-CORE`（ApplicationCore）、`FEA-13`（SQLite/bootstrap）、`FEA-11`（sources/resource_channel） | 四表 DDL 以**独立字节修订/契约冻结**取得 pin（`CONTRACT-UNFREEZE-*` 或新 DDL 契约）；在此之前不得实施依赖该 schema 的写入路径 | schema pin + 迁移测试同批：四表**列级断言**（全列/NULL/默认值）+ 回滚路径；旧库只读核验 | L2 迁移测试 + schema pin；`verification/<Task-ID>/` |
| **L-2** | **M2-C1 字节修订**，含四项：① `PrepareRun`/`AcceptRun` + 3 个 `RUN_*` 码；② `§8 Proposed（未观察）` 小节；③ `allowedRunErrorCodes` 白名单（**C-08 块②**）；④ `TRASH_*` 3 码（**C-09 SC-B06**） | `FEA-12-CORE`（maintenance/删除）、`FEA-10`（Run 管道）、`FEA-13`（备份/恢复引用） | **M2-C1 独立字节修订 Task 完成**（wire 2.12 落地，块①/块②分别 commit + 分别复核）；未完成前 host 侧只可降级 | ① 三码入 wire 2.12 且 `PrepareRun`/`AcceptRun` 使用；② §8 Proposed 小节存在且与 observed 表分离；③ host 投影 `allowedRunErrorCodes` 白名单**负向对照**（未知码降级 `category=unknown`、不重写 `code`）；④ `TRASH_*` 3 码入 SC-B06 协议注册 | L2 单测 + 负向对照；`verification/<Task-ID>/` |
| **L-5** | **整库恢复按迁移处理**：实现时必须持 **SC-17 独占维护锁**——停所有写者/Run/lease → staging → 校验 → **commit marker 后才切换** | `FEA-13`（备份/恢复）、`FEA-12-CORE`（维护窗口互斥） | 恢复期间的独占锁语义在实现前以 AC 固定；不得以「先实现后补锁」方式进入 | ①停写者期间写操作 **fail-closed**（拒绝而非静默降级）；②**staging 完成后校验通过才允许 commit marker**；③**marker 前崩溃**：原库仍可读、无半迁移状态；**marker 后崩溃**：可续/可回退且状态可判定；④恢复完成后写操作恢复 | L2/L3 恢复演练（含崩溃注入于 marker 前后两点）；`verification/<Task-ID>/` |

## 2. 与其它保留项的关系

- L-3 / L-4 / L-6…L-9 维持裁定 §3 与各冻结记录原文状态，**本文件不重复定义、也不改变其约束力**（含 C-09 的 L-1「K-5 外部记账残留」= 裁定 L-3、L-3「实现路径未核」等编号差异，引用时以承载文件为准）。
- 本登记与 `doc/plan/FEA-C11_TASK_TABLE_ALIGNMENT_DRAFT.md`（已冻结的候选表补列契约）**互补**：C-11 管"表列口径"，本文档管"实现前强制前置与 AC"。

## 3. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：按用户 U-09 登记 L-1/L-2/L-5 的归属候选、强制前置与必须 AC；声明不豁免、不释放实现 | DSH |
| 2026-11-01 | 处置 FEA-C11-PREREQ-r1 的 P2-001/002/003：来源改为精确指向（裁定 §3 + G-CONTRACT §3.3 + C-14 §5 L-1 + C-09 §5 L-2）；L-2 补全四项；L-5 AC 补 4 步序列与崩溃注入两点 | DSH |
