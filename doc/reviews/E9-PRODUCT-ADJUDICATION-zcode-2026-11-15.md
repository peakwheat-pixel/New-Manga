---
task: E9-PRODUCT-ADJUDICATION
adjudicator: zcode (external, delegated by DSH 2026-11-15)
scope: E-9 修复方向（扩 Core vs 接受为能力限制）与测试口径
date: 2026-11-15
adjudication_base: main@5c8ca712f
verdict: B（接受为能力限制）；登记第三方案（mint-time 路径映射）为后续解锁候选；A 任何时点都不采
---

# ZCode 裁决：E-9 的产品取舍与测试口径

## 裁决

**B —— 接受为能力限制**；登记**第三方案**（Host 侧 mint-time 路径持久映射）为后续解锁候选；
**A（扩 Core）任何时点都不采**。

**理由**：
1. **sync 完成链尚未产品化**（UI 无 `source_resync` 入口），今日接受限制**对用户零影响**；
2. **A 实为让 Core 开始持久化路径**，跨权威漂移**不可逆**；
3. E-9 现为 typed 拒绝且**数据无损**（apply 已 `core-committed`）。

## 事实核实清单（ZCode 读源码确认，HEAD `5c8ca712f`）

1. `SourceOperationCoordinator.cs:294-297` 非 folder → `SOURCE_PLAN_UNAVAILABLE`；
   **`:22-23` journal closed shape 冻结、禁绝对路径（C-17 §5.2）**。
2. **六入口无路径属实**：`Begin:97` / `Authorize:138` / `MarkCommitted:164` /
   `ApplyAsync` payload（`:199-265`）/ `registryAuthorizations`（`:258-263`）/ `Mint:273`。
3. **★ 影响面大于 DSH 的表述**（"仅崩溃恢复"是**低估**）：
   **`AcknowledgeAsync:468` 与 `RecoverAsync:581` 均走同一 fresh re-mint** ——
   zip/cbz/pdf/image 实际是 **sync 完成链（含正常 ACK）整体不可用**；
   ACK 失败 → gate 停 pending（`source_sync.py:150`）→ 新 binding 不可读。
4. **★ A 的成本被 DSH 低估**：Core `source_locations` **刻意只存物理 facts**
   （`volume_serial`/`file_id`/`size_bytes`，**无路径列**）；A 不是"暴露已有列"，
   而是 **Core 新接收并持久化 Host 授权材料** → **路径双权威（Host registry vs Core 副本）必漂移**。
   故**不采**，也**无需**在 scan target 与 materialization 间选择。
5. **第三方案存在但比设想的长**：`Begin` 加参受 closed shape 约束；`ApplyAsync` 上游 payload 与
   scan-target 驱动的调度链**均不持有路径**。真正最小形态是 **mint 时持久化**——
   `IssueLockedAsync` 手中有真路径，写 **Host 侧 DPAPI 映射**（`registry_id` → `container_path`），
   恢复时取候选路径、**身份仍经 `IssueAsync` 全量物理 facts 验证**（路径失效 = typed 失败，fail-closed 保留）。
   不动 wire／Python／apply payload，但**系新增持久授权材料，需契约小节 + 安全审查**，中等工作量 ——
   列为**后续 Task 候选**。
6. **该测试 opt-in**（`NEWMANGA_FEA11_IPC=1`，基线 12/1）：**"zip ACK 成功"从未达成**
   （fix 前为 `UnauthorizedAccessException` → `SOURCE_ENTRY_MISSING` 误导兜底，同样失败）。

## 最小产品动作（B）：**仅文档**

在 C-17 / FEA-11 已知限制与 E-9 finding 按**真实口径**落盘：
"**非 folder 来源 sync 完成（ACK/恢复）暂不可用，typed 拒绝 `SOURCE_PLAN_UNAVAILABLE`；
解锁路径 = mint-time 路径映射**"。

**不做导入 UI 提示** —— sync UI 入口尚不存在，**无载体**，待 sync 入口 Task 时一并处理。

## 测试口径

改为**断言 typed 拒绝**，**不 skip**（保留 scan/plan/apply 段的 wire 级回归覆盖）。三断言：
1. 精确码 `SOURCE_PLAN_UNAVAILABLE`；
2. journal 状态保持 `core-committed` **无损**；
3. 重复 ACK **幂等同拒**。

**是否降低产品约束**：**形式收紧、实质是能力边界重新声明** —— 旧成功期望**从未可达**，
**不属放宽断言**；但它是**产品约束改判**，须由 DSH 在 finding 文档**显式留痕**
（含解锁条件与测试名标记 `KNOWN-LIMITATION-E9`），**禁止静默改绿**。

## 保留给用户判断

1. 近期若要上**非 folder 来源（zip/cbz/pdf）的书架重同步**，B 即**挡路项**，应提前释放路径映射 Task；
2. 接受 B 的安全前提是**数据无损边界** —— 只挡"读门打开"，**无业务数据损坏**。

## DSH 采纳记录

**采纳**。执行项：
- 测试改为断言 typed 拒绝（三条），测试名/注释标记 `KNOWN-LIMITATION-E9`；
- E-9 finding 更新为真实口径（"sync 完成链整体不可用"，非"仅崩溃恢复"）；
- 登记第三方案为后续 Task 候选（mint-time DPAPI 路径映射）。
