# 实现线强制前置（L-1 / L-2 / L-5）· 用户 U-09 落实登记

状态：**登记文档（非契约、不冻结）**。依据用户 2026-11-01 追加裁决 **U-09**（[ADJ-2026-11-01-FEA-DECISIONS](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)「追加裁决」）：**保留 L-1…L-9，不作整体豁免；四表 DDL、M2-C1 修订、整库恢复独占锁分别进入对应实现 Task 的明确前置与 AC。**

来源：`GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md` §4 保留项（L-1…L-9）；C-09 冻结记录 §5（L-1/L-2）；C-13/C-08 冻结记录（引用不动）。

## 0. 禁则（不得由本文档推导出任何豁免）

- 本文档**不构成**对 L-1…L-9 的豁免、**不构成**实现 Task 释放；`G-DELETE-IMPL` 仍 **OPEN**，候选 Task 须按 C-11 选候选并**经用户确认**后才可建卡/释放。
- 本文档**不修改**任何冻结契约字节（14 份 pin 不变）。
- 前置未满足时，对应候选 Task **不得进入 `in_progress`**；若已建卡则必须停在 `proposed`/`blocked`。

## 1. 逐项登记

| 保留项 | 内容（裁定原文摘要） | 归属候选实现 Task（方案 §15.6 口径） | 实现前必须完成的前置 | 必须写入候选 Task 的 AC | 证据计划（等级/位置） |
|---|---|---|---|---|---|
| **L-1** | 四表 DDL 未冻结；生产实现前置 | `FEA-03`（`src/application`/`src/domain`/`src/infrastructure/sqlite`）、`FEA-02-CORE`（ApplicationCore）、`FEA-13`（SQLite/bootstrap） | 四表 DDL 以**独立字节修订/契约冻结**取得 pin（`CONTRACT-UNFREEZE-*` 或新 DDL 契约）；在此之前不得实施依赖该 schema 的写入路径 | schema pin + 迁移测试同批：列级断言（全列/NULL/默认值）+ 回滚路径；旧库只读核验 | L2 迁移测试 + schema pin；`verification/<Task-ID>/` |
| **L-2** | M2-C1 字节修订：`TRASH_*` 3 码与 Run 错误码白名单（C-09 SC-B06） | `FEA-12-CORE`（maintenance/删除）、`FEA-10`（Run 管道）、`FEA-13`（备份/恢复引用） | **M2-C1 独立字节修订 Task 完成**（wire 2.12 落地）；未完成前 host 侧只可降级为 `category=unknown` | 3 码入 wire 2.12 + host 投影白名单**负向对照**（未知码降级且不重写 `code`）；Run 线 `allowedRunErrorCodes` 白名单生效 | L2 单测 + 负向对照；`verification/<Task-ID>/` |
| **L-5** | 整库恢复独占锁（C-09 §3 明文认定） | `FEA-13`（备份/恢复）、`FEA-12-CORE`（维护窗口互斥） | 恢复期间的独占锁语义在实现前以 AC 固定；不得以「先实现后补锁」方式进入 | 恢复期间写操作 **fail-closed**（拒绝而非静默降级）；恢复完成后恢复可写；崩溃后锁状态可判定 | L2/L3 恢复演练（含崩溃注入）；`verification/<Task-ID>/` |

## 2. 与其它保留项的关系

- L-3 / L-4 / L-6…L-9 维持 C-09 冻结记录与 Gate 关闭裁定的原文状态，**本文件不重复定义、也不改变其约束力**。
- 四表 DDL（L-1）与 M2-C1（L-2）的字节修订本身属于「新增/修改共享契约」，须走 UNFREEZE 或新建契约流程，不得在实现 Task 内顺手改。
- 本登记与 `doc/plan/FEA-C11_TASK_TABLE_ALIGNMENT_DRAFT.md`（已冻结的候选表补列契约）**互补**：C-11 管"表列口径"，本文档管"实现前强制前置与 AC"。

## 3. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：按用户 U-09 登记 L-1/L-2/L-5 的归属候选、强制前置与必须 AC；声明不豁免、不释放实现 | DSH |
