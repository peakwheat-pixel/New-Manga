# Gate 关闭口径裁定（G-DELETE-CONTRACT / G-CONTRACT）

状态：**DSH 架构裁定 / 待独立复核**
裁定人：DSH（Lead / Architect / Integrator）
日期：2026-11-01
依据：[FEA-00 方案 r4 §15.12](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md)（`:764-771`）、[ADJ-001 §9](../contracts/ADJ-001_PERMANENT_DELETE_AND_PROTECTION.md)、[AD-003 §5](../AD-003_REFERENCED_SOURCE_ARCHITECTURE.md)、[冻结矩阵](FEA-CONTRACT_FREEZE_MATRIX.md)

---

## 1. 问题

`G-DELETE-CONTRACT` 与 `G-CONTRACT` 的关闭条件**与被它们守门的契约构成循环**：

| Gate | 定义（原文） | 守门的契约 | 契约的冻结条件 |
|---|---|---|---|
| `G-DELETE-CONTRACT` | 「协议字段/码表/**D04-D07** 冻结」（ADJ-001 §9） | **C-04b**（删除协议字段/码表） | ③ `G-DELETE-CONTRACT` 关闭 |
| `G-CONTRACT` | 「**D05** Source/grant/资源契约冻结」（AD-003 §5） | **C-06**（SourceAccessRegistry + source-read grant） | ③ `G-CONTRACT` 关闭 |

按字面执行会死锁：Gate 要契约冻结才关，契约要 Gate 关闭才冻。

## 2. 事实核查

`D01`–`D08` **不是独立文档**，而是 [FEA-00 §15.12](../design/FLUENT_FRONTEND_ARCHITECTURE_PROPOSAL.md) `:764-771` 的**变更包分组编号**，每个对应一组契约：

| 变更包 | 覆盖面 | 对应契约（现代载体） |
|---|---|---|
| D01 架构补充决策 | AD-002/AD-003/AGENTS | **C-01b**（已冻结） |
| D02 前端可替换契约 | V11R 修订 | **C-02**（已冻结） |
| D03 应用端口/错误/capability | IHostController/Registry/Dispatcher | **C-07**（已冻结） |
| D04 草稿/保护/结果 | Region 契约、edit token/journal | C-08 部分 + 未起草的 draft 契约 |
| **D05 Source/grant/资源** | 导入/资源控制面、Host issuer | **C-06** |
| D06 Run 快照 | IRunController/PreparedRun | **C-08** |
| **D07 删除/备份/迁移** | `M2-C1 §5.11`、ADJ-001 | **C-04b**（方案 `:516` 明写「协议字段与错误码仍待 D07 冻结（**C-04b**）」） |
| D08 现有任务协调 | STATUS/PLAN 等 | 治理文档（非契约） |

**结论**：Gate 的「D04-D07 冻结」「D05 冻结」= 「对应变更包的契约已冻结」。Gate 不是契约的**前置**，而是契约冻结状态的**投影**。

## 3. 裁定

### R-1 Gate 与契约的关闭是同一事件

冻结 C-04b 时**同步**关闭 `G-DELETE-CONTRACT`；冻结 C-06 时**同步**关闭 `G-CONTRACT`。冻结记录的「冻结后果」节承担 Gate 状态更新，不再需要单独的 Gate 关闭前置。

**理由**：Gate 的作用是防止「未冻结就实现」。契约冻结 = 防线的达成，二者是同一时点。

### R-2 C-04b 的 M2-C1 扩展降级为「实现前置」

C-04b 原冻结条件⑤「M2-C1 §5.11.3 + §5.11.5 的扩展已由独立 Task 完成并复核」**改为**：

> ⑤ **M2-C1 扩展方案已冻结在 C-04b §2.4**（4 个扩展点 + 2 个新码）；**协议字节修订**由紧接的实现 Task 完成，且**在修订完成与复核通过前，新码一律不得启用**（C-04b §2.4 已规定 fail-closed）。

**理由**（三层）：
1. **契约层与协议层分离**：C-04b 冻结的是「要加什么字段/码」（结构性声明），M2-C1 §5.11 是「字节级协议」。冻结契约不等于协议已改。
2. **现行语义继续有效**：ADJ-001 §10 明写「在 D04/D07 契约冻结并实施前，`M2-C1 §5.11` 现行语义继续按原字节生效」——契约冻结（D07）与实施（M2-C1 改字节）本就是两件事。
3. **安全不降级**：C-04b §2.4 已规定新码未注册前 host 投影会拒绝、§3 规定 `PROTOCOL_VERSION_UNSUPPORTED` fail-closed——不存在「未扩展却生效」的窗口。

### R-3 wire 版本批准

C-06 条件④「wire 版本由 DSH 批准（v1.1 minor 增量）」——**批准**。理由：`source-read` 是新 grant 类型，不改既有 `ImportPages` 语义（C-06 §2.2 已规定不复用），minor 递增符合 ADJ-001 §6.1 末句口径。

C-04b 条件④「DSH 批准 `2.11` minor」——**批准**。理由：新增 `PreviewPermanentDeleteBooks` 命令 + 2 个错误码，无既有字段语义变更。

## 4. 影响

| 项 | 变化 |
|---|---|
| C-04b | 条件⑤降级 → **可冻结**（其余 5 条已满足） |
| C-06 | 条件③按 R-1 同步关闭 → **可冻结**（其余 4 条已满足） |
| C-08 | 条件「C-05/C-04b 冻结」→ C-04b 冻结后满足；「协议注册独立 Task」同样按 R-2 降级为实现前置 |
| C-09 | 条件「两 Gate 关闭」→ C-04b/C-06 冻结后满足 |
| ADJ-001 §9 / AD-003 §5 | Gate 状态更新为 CLOSED（附本裁定引用） |

## 5. 风险与回退

| 风险 | 缓解 |
|---|---|
| Gate 关闭早于协议字节，若长期不实现则 Gate 状态与实际能力不符 | C-04b/C-06 的**冻结记录**必须标注「能力未实现（`NOT_RUN`）」；STATUS 的下一候选不含依赖新码的 Task |
| M2-C1 扩展被无限推迟 | 扩展 Task 作为 C-04b 的**紧接动作**写入冻结记录；释放实现前必须完成 |
| 本裁定本身降低安全 | 不降级任何 fail-closed 条款；新码在未注册前被 host 投影拒绝（M2-C1 §5.11.5 封闭联合） |
| 与 ADJ-001/AD-003 的原文冲突 | 只更新 Gate **状态值**，不改语义条款；裁定引用原文作为依据，不改其字节 |

**回退条件**：若独立复核认为 R-1/R-2 降低安全，或 ADJ-001/AD-003 的语义条款被证明依赖「Gate 必须先关」→ 撤销本裁定，改为「先建 M2-C1 扩展 Task → 完成 → 再冻 C-04b」的严格路径。

## 6. 变更记录

| 日期 | 变更 | 记录 |
|---|---|---|
| 2026-11-01 | 建立：问题（循环依赖）、事实核查（D01–D08 是变更包）、三条裁定（R-1 同步关闭 / R-2 降级 / R-3 版本批准）、影响、风险与回退 | DSH |
