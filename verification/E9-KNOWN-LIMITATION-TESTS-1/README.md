# E9-KNOWN-LIMITATION-TESTS-1：按 ZCode 裁决改造测试口径

基线 `aa20202b7`。执行 ZCode 裁决（`doc/reviews/E9-PRODUCT-ADJUDICATION-zcode-2026-11-15.md`）的待办：
把 `Fea11Residual4AIpcTests.ProductionDispatcherFullSyncChain_NewKeyOldDigestConserved` 的
"ACK 成功"期望，改为**断言 typed 拒绝**，并标记 `KNOWN-LIMITATION-E9`。

## 1. 改了哪段

| 步骤 | 改前 | 改后 |
|---|---|---|
| (5) ACK | 期望 `acknowledged` | **断言 `SourceAccessException` 且 Code == `SOURCE_PLAN_UNAVAILABLE`** |
| (5a) 新增 | —— | **journal 仍 `core-committed`**（拒绝不损坏状态） |
| (5b) 新增 | —— | **重复 ACK 幂等**：同码拒绝 + 状态不动 |
| (6) 页面 | 期望解析到 v2 key 并读到蓝色像素 | **断言仍不可读**（`SOURCE_ACCESS_DENIED`，与步骤 (4) 一致） |
| (7) 旧摘要 | `superseded` + 断言 catalog 含已服务 rendition | **`superseded`**（保留）+ **`Assert.Empty(renditions)`**（没有服务过任何 rendition） |

**保留未动**：(1) 前置状态、(2) scan + wire 级 DTO 断言、(3) plan/preview/confirm/apply + wire 级字段断言、
(4) pending gate、(8) 源文件未变、(9) 撤销 registry fail-closed。

## 2. 为什么这不属于"放宽断言"

ZCode 裁决明确：旧 `acknowledged` 期望**从未可达** —— 修复前该步骤同样失败，
只是错误码被兜底成 `SOURCE_ENTRY_MISSING`（误导）。

**本改造实际是收紧 + 扩容**：
- 从"期望成功"→"**精确拒绝码**"（更严格的声明）；
- **新增 3 条断言**（状态无损、幂等、catalog 空），覆盖面**比原来更宽**；
- **未删除**任何 scan/plan/apply 段的 wire 级断言。

## 3. 我自己在改造中犯的两个错（已登记在测试注释）

1. **异常类型猜错**：先写成 `Assert.ThrowsAsync<CoreOperationException>`，实测抛的是
   `SourceAccessException`（Host 侧）。**改正**。
2. **supersede 时机猜错**：先写成"没发布所以旧 binding 仍 `healthy`"，实测是 **`superseded`**
   —— **supersede 发生在 core-commit（apply）阶段，不是 ACK 阶段**。**改正**，并把这条实测结论写进注释。

**两处都是"猜而没有先测"**，与之前几次同类错误同源。

## 4. 结果

| 口径 | 改前 | 改后 |
|---|---|---|
| 带 opt-in 三类（Fea11Source/Residual4A/Scan） | 12 passed / 1 failed | **13 / 0 / 0 / 13** |
| 无夹具 Host.Tests 全量 | 325 / 0 / 74 / 399 | **325 / 0 / 74 / 399** |

## 5. 必须说清的边界

**这没有修好 E-9。** E-9 仍是**能力限制**：
- 非 folder 来源的 **sync 完成链（ACK/恢复）不可用**；
- 现在失败是 **typed 且可解释**（`SOURCE_PLAN_UNAVAILABLE`），而不是误导性的文件系统错误；
- **解锁路径** = mint-time DPAPI 路径映射（ZCode 登记的后续 Task 候选），**本卡未做**。

**"13/0" 是测试口径与产品能力声明对齐后的结果，不是"恢复功能可用"。**

## 6. 未做

- 未落 C-17/FEA-11 的"已知限制"正式小节（ZCode 要求的最小产品动作是**文档**，需另起或并入文档卡）。
- 未实现 mint-time 路径映射。
- 未跑 App/CoreClient 全量（本次只改 Host 测试文件）。
