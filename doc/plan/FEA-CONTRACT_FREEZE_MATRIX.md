# FEA 契约冻结准备总表（冻结矩阵）

状态：**DRAFT / 待复核**
日期：2026-11-01
作者：DSH（Lead / Architect / Integrator）
依据：[FEA-01 契约清单](FEA-01_CONTRACT_DRAFT.md)、各草案的「冻结条件」节、[FEA-CONTRACT_FREEZE_PACKAGE](FEA-CONTRACT_FREEZE_PACKAGE.md)

**用途**：把 **11 份已起草契约 + C-10（未起草）共 12 行**的冻结依赖链收成一张可执行表——每份差什么、按什么顺序、卡在哪个 Gate。**不是**冻结令。

---

## 1. 总表

| # | 契约 | 状态 | 冻结条件（差什么） | 依赖（先冻谁） | 阻塞项 |
|---|---|---|---|---|---|
| 1 | **C-01b** 存储契约 | `approved` r5 | ①独立复核 ✅（r5 approved）②AD-003 `G-REVIEW` 收口 ✅（SATISFIED）+ ADJ-001 依赖注明（`G-DELETE-CONTRACT` OPEN）③用户确认 AD-002 责任表/哨兵口径（**`R`**）④`check.ps1` PASS | 无（语义基座） | ③（用户 `R`） |
| 2 | **C-02** V11R 修订 | `approved` r2 | ①**U-04** 用户裁决 | 无（与 C-01b 独立） | U-04 |
| 3 | **C-03** 外观持久化 | `approved` r2 | ①**U-05a/U-05b** ②C-02 先冻结 | C-02 | U-05a/b |
| 4 | **C-04b** 删除协议 | `approved` r3 | ①C-01b 冻结 ②`G-DELETE-CONTRACT` 关闭 ③D04/D07（码表裁决，ADJ-001 §6.3）④DSH 批准 2.11 ⑤M2-C1 扩展独立 Task | C-01b | 5 项全未满足 |
| 5 | **C-05** 页可见性 | `approved` r3 | ①`VISIBLE_TYPES`/`active_runs` 经 C-01b/ADJ-001 确认（C-01b 冻结后即可） | C-01b（口径确认） | 无硬阻塞 |
| 6 | **C-06** 授权面 | `approved` r3 | ①C-01b 冻结 ②`G-CONTRACT` 关闭 ③wire v1.1 DSH 批准 | C-01b | `G-CONTRACT: OPEN` |
| 7 | **C-07** API inventory | 已生成（54 成员） | ①独立复核 | 无 | 未复核 |
| 8 | **C-08** Run 快照 | `approved` r2 | ①C-05/C-04b 冻结 ②C-01b 冻结 ③协议注册独立 Task | C-05/C-04b | 协议注册未建 |
| 9 | **C-09** 删除/备份/迁移 | `approved` r2 | ①C-01b 冻结 ②`G-DELETE-CONTRACT` + `G-CONTRACT` 关闭 | C-01b | 两 Gate |
| 10 | **C-11** 候选表口径 | `approved` r3 | ①C-01b 或 C-02 至少其一冻结 | C-01b/C-02 | 无 |
| 11 | **C-12** 检查器边界 | `approved` r2 | ①独立复核 ✅ ②检查器现有断言与 §2 表一致（可机械核对）③`check.ps1` PASS | 无 | 无硬阻塞 |
| — | **C-10** 交互契约 | **部分**（追溯矩阵/draft owner/快捷键成立；其余待起草） | 待 **U-03** | 方案 §12.1 F-10/F-18/F-39/R7-07 | U-03 |

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
第 5 步：C-06 冻结（G-CONTRACT 关闭后） / C-04b 冻结（G-DELETE-CONTRACT 关闭 + D04/D07 + 2.11 + M2-C1 扩展后）
   ↓
第 6 步：C-08 冻结（C-05/C-04b 都冻 + 协议注册）
   ↓
第 7 步：C-09 冻结（两 Gate 关闭）
   ↓
第 8 步：C-07 复核（无依赖，可随时插队）
```

## 3. 卡的 Gate 清单

| Gate | 影响 | 关闭条件 |
|---|---|---|
| `G-DELETE-CONTRACT` | C-01b/C-04b/C-09 | ADJ-001 的 PD 语义冻结（**D04–D07** 裁决，ADJ-001 §9 `:128`） |
| `G-CONTRACT` | C-06/C-09 | AD-003 存储契约冻结 |
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
- 本文档：**11 份已起草 + 1 未起草（12 行）**的依赖矩阵（更细，逐份）；
- 两者不冲突：PACKAGE 是「怎么冻」，本文档是「谁先谁后」。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：11 行总表、8 步顺序、5 个 Gate、5 条验证动作 | DSH |
