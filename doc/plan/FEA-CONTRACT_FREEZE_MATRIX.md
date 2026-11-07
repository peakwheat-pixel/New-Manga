# FEA 契约冻结准备总表（冻结矩阵）

状态：**ACTIVE**（**18 个冻结对象**：17 份既有 + C-17 v1.1；C-05 v1.2/C-15 v1.5/C-16 v1.7/C-06 v1.3 于 2026-11-04/2026-11-07/2026-11-07/2026-11-07 UNFREEZE 重冻；C-16 v1.3 新增 §2.4；v1.4 增容器多成员 entry 语义；v1.5 增 `source.reattest/1` + §2.5 条件写 + `roots_available`；v1.6 增 §2.4 mid-run 重复调用语义；v1.7 澄清 §2.4「无 publication 行」口径（legacy open / 新同步链缺行 fail-closed））
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md)、各草案的「冻结条件」节、[FEA-CONTRACT_FREEZE_PACKAGE](FEA-CONTRACT_FREEZE_PACKAGE.md)

**用途**：把 **14 份已冻结契约（含 C-09 v5、C-14、C-10 v5）** 的冻结依赖链收成一张可执行表——每份差什么、按什么顺序、卡在哪个 Gate。**不是**冻结令。

> **当前进度（2026-11-01）**：用户 6 项裁决 + 追加裁决 U-06…U-12 已落盘（[ADJ-2026-11-01](../reviews/ADJ-2026-11-01-FEA-DECISIONS.md)）；**已冻结 15 份**（14 份子契约 + FEA-01 清单）：C-01b / C-02 / C-03 / C-04b / C-05 / C-06 / C-07 / C-08 / C-11 / C-12 / C-13（D04）/ **C-14（D05）** / **C-09（D07，v5）** / **C-10（交互，v5，`T=4 DIP`）**。**Gate 判定见下方 `:12` 的最终块**（两 Gate 均已 CLOSED，2026-11-01）。契约线 + FEA-01 清单**已全部冻结**（门禁链 4/4，FEA-01 pin `0370c189…`）；实现线首候选 `FEA-02-CORE` 待范围冻结复核（`G-DELETE-IMPL` OPEN）。
>
> **Gate 判定（最终，2026-11-01）**：`G-CONTRACT` **✅ CLOSED**（[裁定](GATE-CONTRACT-CLOSURE-2026-11-01.md)）；`G-DELETE-CONTRACT` **✅ CLOSED**（[裁定](GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md)，D04–D07 全覆盖，`approved` r3）。**保留项 L-1…L-9**（尤其 L-5 整库恢复锁认定）与 **Errata** 见该裁定。
---

## 1. 总表

| # | 契约 | 状态 | 冻结条件（差什么） | 依赖（先冻谁） | 阻塞项 |
|---|---|---|---|---|---|
| 1 | **C-01b** 存储契约 | **`FROZEN`** 2026-11-01 | ①独立复核 ✅（r5 approved）②AD-003 `G-REVIEW` 收口 ✅（SATISFIED）+ ADJ-001 依赖注明（`G-DELETE-CONTRACT` OPEN）③用户确认 AD-002 责任表/哨兵口径（**`R`**）④`check.ps1` PASS | 无（语义基座） | ③（用户 `R`） |
| 2 | **C-02** V11R 修订 | **`FROZEN`** 2026-11-01 | ①**U-04** 用户裁决 | 无（与 C-01b 独立） | U-04 |
| 3 | **C-03** 外观持久化 | **`FROZEN`** 2026-11-01 | ①**U-05a/U-05b** ②C-02 先冻结 | C-02 | U-05a/b |
| 4 | **C-04b** 删除协议 | **`FROZEN`** 2026-11-01 | ①独立复核 ✅ ②C-01b 冻结 ✅ ③`G-DELETE-CONTRACT` **不阻塞**（裁定 R-1′）④DSH 批准 2.11 ✅ ⑤M2-C1 扩展为释放前置（R-2′） | C-01b | 5 项全未满足 |
| 5 | **C-05** 页可见性 | **`FROZEN v1.2`** 2026-11-04（v1.2 UNFREEZE 重冻；v1.1 2026-11-03、v1.0 2026-11-01） | ①`VISIBLE_TYPES`/`active_runs` 经 C-01b/ADJ-001 确认（C-01b 冻结后即可） | C-01b（口径确认） | 无硬阻塞 |
| 6 | **C-06** 授权面 v1.3（mid-run 重复建立） | **`FROZEN v1.3`** 2026-11-07（UNFREEZE 重冻；v1.0 2026-11-01 / v1.1 2026-11-03 / v1.2 2026-11-06） | ①v1.3 独立 byte-level 复核 **r6 approved**（P0=0/P1=0/P2=0/P3=1 非阻断；载体 CONTRACT-UNFREEZE-2026-11-07-C06-C16-RUN-RENEWAL）②C-01b 冻结 ✅ ③`G-CONTRACT` **不阻塞**（裁定 R-1′）④C-16 v1.6 同批 ⑤18/18 | C-01b/C-16 v1.6 | `G-CONTRACT: OPEN` |
| 7 | **C-07** API inventory | **`FROZEN`** 2026-11-01 | ①独立复核 ✅ ②生成脚本入库（`tools/generate_api_inventory.py`）③`--check` OK | 无 | 无硬阻塞 |
| 8 | ~~C-08 Run 快照~~ | ~~`approved` r2~~（**已被 #12 FROZEN 取代**） | — | — | — |
| 9 | **C-09** 删除/备份/迁移 | **`FROZEN`** 2026-11-01 | ①C-01b/C-04b/C-06/C-08/C-14 冻结 ②`G-CONTRACT` 关闭 ✅（**不再要求 `G-DELETE-CONTRACT`**——解环，见 [D07 解环](../tasks/FEA-D07-UNBLOCK.md)） | C-01b | 无（Gate 不阻塞） |
| 10 | **C-11** 候选表口径 | **`FROZEN`** 2026-11-01 | ①C-01b 或 C-02 至少其一冻结 | C-01b/C-02 | 无 |
| 11 | **C-12** 检查器边界 | **`FROZEN`** 2026-11-01 | ①独立复核 ✅ ②检查器现有断言与 §2 表一致（可机械核对）③`check.ps1` PASS | 无 | 无硬阻塞 |
| 13 | **C-13** 草稿与保护（D04） | **`FROZEN`** 2026-11-01 | ①独立复核 ✅ ②U-03=B 裁决 ③C-01b 冻结 | C-01b | 无（Gate 不阻塞） |
| 12 | **C-08** Run 快照 | **`FROZEN`** 2026-11-01 | ①独立复核 ✅ ②C-01b/C-05/C-04b 冻结 ③协议注册为释放前置（R-4） | C-05/C-04b | 无（Gate 不阻塞） |
| 14 | **C-14** Source 重定位/同步/容器页/缓存（D05） | **`FROZEN`** 2026-11-01 | ①独立复核 ✅（r1 5 P1 → r2 approved）②C-01b/C-06/C-04b/C-08 冻结 ③用户 2026-11-01 裁决（新建 C-14 承载 D05 剩余范围） | C-01b/C-06 | 无（Gate 不阻塞） |
| — | **C-10** 交互契约 | **`FROZEN`** 2026-11-01 | ①用户裁定 `T=4 DIP` ✅（U-06）②独立复核 ✅（r4 的 P1×2 已修，R4b 确认冻结字节）③[冻结记录](FEA-CONTRACT-FROZEN-C10.md) + pin `ec8fd862…` | FEA-01 C-10 依赖列（F-10/F-18/F-39/R7-07；F-ID 见方案 §15.8 台账 `:972/980/1001`） | 无（Gate 不阻塞；实现线未释放） |


| 15 | **C-15** Source 存储契约（DDL/迁移/完整性-可见性/Registry/跨存储次序/根级不可用拆分） | **`FROZEN v1.5`** 2026-11-07（UNFREEZE 重冻；v1.0 2026-11-03 / v1.1 2026-11-04） | ①v1.5 独立 byte-level 复核 approved（载体 CONTRACT-UNFREEZE-2026-11-07-C15）②C-16/C-17 零改动 ③18/18 ④PASS | C-01b/C-05 v1.1/C-06 v1.1/C-14 | 无（读取韧性实现归 FEA-11-L-S1-REGISTRY-RESILIENCE-1） |
| 16 | **C-16** Source 读取/导入 wire v1.7（四维 scope/撤销/密码引用/fresh-grant resolve/异步 receipt/Run 授权建立命令/容器多成员 entry/re-attest 条件写/roots 可用性投影/mid-run 重复调用/publication 无行口径） | **`FROZEN v1.7`** 2026-11-07（UNFREEZE 重冻；v1.0/v1.1/v1.3/v1.4/v1.5/v1.6 历史） | ①v1.6 独立 byte-level 复核 **r6 approved**（P0=0/P1=0/P2=0/P3=1 非阻断；载体 CONTRACT-UNFREEZE-2026-11-07-C06-C16-RUN-RENEWAL）②v1.7 独立 byte-level 复核 **r1 approved**（P0=0/P1=0/P2=0/P3=7 非阻断；载体 CONTRACT-UNFREEZE-2026-11-07-C16-L-R11；报告 FEA-11-L-R11-GATE-UNIFY-PREREQ-1-r1）③C-17/C-06/C-15/C-07/M2-C1 零改动 ④18/18 ⑤PASS | C-06 v1.3/C-15 v1.5/C-17 v1.1 | 无（L-R11 实现归 FEA-11-L-R11-GATE-UNIFY-1） |

| — | **C-17** Source 同步契约（v1.1） | **`FROZEN v1.1`**（2026-11-06 UNFREEZE 重冻；v1.0 2026-11-04） | ①契约最终字节独立 Review ②DSH 冻结记录/三指纹/pin 18 ③M2-C1 增量或无增量决定 | C-14/C-15/C-16（语义基座） | 无（实现释放归 FEA-11-SCAN-2） |

## 2. 可执行顺序（推荐）

```
第 0 步（用户裁决，阻塞 1/2/3）：R + U-04 + U-05a + U-05b
   ↓
第 1 步：C-01b 冻结（语义基座；需 ADJ-001 的依赖注明）
   ↓
第 2 步（可并行）：C-05 冻结（只差 VISIBLE_TYPES 确认） / C-12 冻结（无阻塞）
   ↓
第 3 步：C-02 冻结（U-04 已裁）
   ↓
第 4 步（可并行）：C-03 冻结（跟 C-02） / C-11 冻结（C-01b 已冻）
   ↓
第 5 步：C-06 冻结 / C-04b 冻结（**历史步骤**：两 Gate 已于 2026-11-01 CLOSED）
   ↓
第 6 步：C-08 冻结（C-05/C-04b 都冻 + 协议注册）
   ↓
第 7 步：C-09 冻结（上游契约全冻 + 独立复核；**解环后不再等 Gate 关闭**）
   ↓
第 8 步：C-07 复核（无依赖，可随时插队）
```

## 3. 卡的 Gate 清单

| Gate | 影响 | 关闭条件 |
|---|---|---|
| `G-DELETE-CONTRACT` | C-01b/C-04b/C-09 | ADJ-001 的 PD 语义冻结（**D04–D07** 裁决，ADJ-001 §9 `:128`）；**已 CLOSED 2026-11-01**（[裁定](GATE-DELETE-CONTRACT-CLOSURE-2026-11-01.md)） |
| `G-CONTRACT` | C-06/C-09 | AD-003 存储契约冻结；**已 CLOSED 2026-11-01** |
| `G-SAFETY` | FEA-00a（实现） | SAFETY 线收尾 + F20 修复（当前 `NOT_RUN`） |
| U-03 / U-04 / U-05a / U-05b | C-10 / C-02 / C-03 | 用户裁决 |
| AD-002 口径 `R` | C-01b（以及 AD-002 正文是否改字节） | 用户裁决 |

## 4. 每步的验证动作（冻结时执行）

1. 草案 `approved` 且无 P0/P1 未解决；
2. 冻结条件逐条勾选；
3. 冻结后：在 `doc/plan/FEA-CONTRACT-FROZEN-<ID>.md` 记录冻结时间 + 字节 pin + 条件清单；
4. `check.ps1` PASS；
5. 冻结后不得再改草案正文（UNFREEZE 载体见 FREEZE_PACKAGE）。

## 5. 与其他文档的关系

- [FEA-CONTRACT_FREEZE_PACKAGE](FEA-CONTRACT_FREEZE_PACKAGE.md)：四阶段执行序列（更粗，含 UNFREEZE 与回退表）；
- 本文档：**11 份已起草 + C-10（部分起草）共 12 行**的依赖矩阵（更细，逐份）；
- 两者不冲突：PACKAGE 是「怎么冻」，本文档是「谁先谁后」。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：11 行总表、8 步顺序、5 个 Gate、5 条验证动作 | DSH |
