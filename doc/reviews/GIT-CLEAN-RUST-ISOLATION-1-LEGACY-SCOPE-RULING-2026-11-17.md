---
task_id: GIT-CLEAN-RUST-ISOLATION-1
kind: external-ruling
authority: Codex（外部裁定；只读，未修改任何文件）
invited_by: DSH（Lead / Architect / Integrator）
issued_at: 2026-11-17T17:00+08:00
subject: AD-002 退役 Tauri/Rust 线后，本卡 AC3 与 R2-F01..F05 的处置
decision: Q1=(A) WONT_FIX_LEGACY / 不强制新架构容量卡
adopted_by: DSH
---

# GIT-CLEAN-RUST-ISOLATION-1 —— Legacy 范围裁定（Codex）

> 本文件是 Codex 的书面裁定原文（只读产出；Codex 当时无法写盘，由 DSH 逐字保存）。
> 下方「DSH 采纳」段是本项目 Lead 的采纳记录，不修改裁定正文。

## 裁定

Q1 结论：**(A) 不需要在本卡内实现 AC3，也不强制另立新架构容量卡；本卡可按 `closed_with_limitations` 收口，AC3 原样保持 `<<BLOCKED>>`。**

AGENTS 将 Tauri/Rust 代码、测试和既有 Task 定为历史证据，并限定后续工作落在 Avalonia/C# + Python Core 架构；AD-002 也明确由 C# Host 取代 Tauri/Rust Host（`AGENTS.md:54`；`doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md:24,30`）。R2-F01 明确记载「当前没有生产缺陷证据」，所以目前证明的是旧 Rust 测试未触及 `32` 容量边界，而不是新架构已复现的用户可见问题（`verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md:16`）。因此，无须把这个测试缺口强制转成新架构 Task；若之后在新架构复现了用户可见问题，再由 DSH 按 Plan 另行冻结需求和范围（`AGENTS.md:54`）。

## Q2 逐条 disposition

以下是**本次裁定对本卡的分类**；`verification/**` 中原有 finding 的 `open` 状态及证据保持原样。

| ID | 级别 | 处置 | 理由 | 若转移则最小范围 |
|---|---|---|---|---|
| R2-F01 | P1 | `WONT_FIX_LEGACY` | `peak0/32` 及 accepted/refused 所有权路径未验证，但这是 Rust registry 的容量测试缺口；现有审查未证明生产缺陷。保留 AC3 `BLOCKED`，不在旧实现上补测。 | 不转移。 |
| R2-F02 | P2 | `WONT_FIX_LEGACY` | write timeout 错误码/消息及 writer/reader unfinished 的硬断言属于旧测试面的验证缺口；没有新架构复现证据。 | 不转移。 |
| R2-F03 | P2 | `WONT_FIX_LEGACY` | guard 异常清理、未完成 worker 收尾和 holder `Arc` 生命周期与旧 Rust 实现绑定；缺陷仍按原记录保留，未证明新架构存在对应故障。 | 不转移。 |
| R2-F04 | P2 | `WONT_FIX_LEGACY` | `threads_spawned/joined` 账本与 child-lock tasklist 退出断言是旧测试编排及回收核验缺口。 | 不转移。 |
| R2-F05 | P2 | `WONT_FIX_LEGACY` | owner 槽读超时 panic 与 owner mismatch fallback 是旧 Rust registry/测试隔离路径的断言缺口。 | 不转移。 |

R2-F01 至 F05 的原始内容分别见 `verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md:16-20`；该文件还说明 R2-F01 没有生产缺陷证据（`:16`）。若后续在新架构发现对应的用户可见行为，应另立卡，仅验证该行为在实际 Host/Python Core 路径上的边界处理与资源归属，不继承 Rust 的 `MAX=32` 或扩大为无界压力目标。

## Q3 收口限制清单与 reviewer 处置

收口记录应逐项保留以下限制，不能改写既有 AC 或 verification 证据：

1. AC1 保持原样 `<<PARTIAL: ...R006异常清理及R2-F02..05仍待补>>`；不得将遗留项写成已修复（`doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:34`）。
2. AC3 保持原样 `<<BLOCKED: ...peak0未达32，容量接受/拒绝路径未验证>>`；不得声称已达到饱和或已验证 accepted/refused 所有权（同文件 `:36`）。
3. AC2 的 `MET` 仅适用于固定 head `1829a38` 的两次默认并发结果 `153 passed / 0 failed / 6 ignored / 12 filtered`，不得外推为任意生产负载或新架构容量结论（同文件 `:35`；`verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md:22`）。
4. AC4 的 `MET` 只表示交付绑定及审查流程已执行；审查结论仍为 `blocked`，不能据此声称技术验收或集成通过（同文件 `:37`、`:181`；`verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md:22`）。
5. R2-F01 至 F05 在原 r2 `DISPOSITION.md` 中仍为 `open`；本次 `WONT_FIX_LEGACY` 是收口分类，不表示 finding 已修复或原始记录已关闭（`verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md:16-22`）。
6. fault 回收检查只记录 peak 检查前通过的部分；`remaining=0` 是打印值，peak 失败后续断言未执行，不能宣称整个故障场景通过（同文件 `:22`）。
7. 收口不得改变生产预算 `MAX=32`，也不得据此修改生产实现、契约、Schema 或依赖；原卡已明确生产 registry 与 MAX 不变（`doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:41,48`）。

**Reviewer 处置：**建议在本次收口 Review 前将卡面 `reviewer` 更新为 `Codex`，由未参与该实现/返修的独立 Codex 上下文审查。Appointment 和 Review 报告须记录 `reviewer_kind=agent`、审查者身份及实际会话/来源；若改派独立子 agent，则记录 `reviewer_kind=subagent` 及其会话或子任务 ID（`AGENTS.md:31-32`；`doc/09_COLLABORATION.md:335-337`）。现行规则要求上下文独立，不要求 Owner 与 Reviewer 必须是不同 Agent；因此 `ZCode` 身份本身不构成绝对禁止，但产出该实现的同一会话/实例不得自审。旧卡面关于 Owner 与 Reviewer 必须不同的说法应按后来的上下文独立裁决理解，不应据此恢复过时的角色限制（`doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:193-196`；`AGENTS.md:31-32`）。

## 依据

- `AGENTS.md:31-32`：上下文独立 Review 的现行规则及来源记录要求。
- `AGENTS.md:54`：新架构边界、Legacy 处理规则及用户可见问题的转化条件。
- `doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md:24,30`：C# Host 取代 Tauri/Rust Host，并明确移除旧技术栈。
- `doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:6-10`：Task 状态、Owner 与 Reviewer 字段。
- `doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:34-37`：AC1–AC4 当前标记及限定。
- `doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:41,48`：生产实现和 `MAX` 不变、容量边界的原验收要求。
- `doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:179-181`：最新 r2 blocked 结论与 AC4 的程序性含义。
- `doc/tasks/GIT-CLEAN-RUST-ISOLATION-1.md:185-196`：Owner/Reviewer 历史改派记录及过时角色冲突说明。
- `verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md:16-22`：R2-F01..F05 原始 finding、`open` 状态、AC 限定及未执行断言。
- `verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md:26-29`：无生产缺陷证据、旧测试切片尚未释放及不修改本卡 AC 的记录。
- `doc/09_COLLABORATION.md:79,81,87`：`closed_with_limitations` 的条件、状态权威和 Review/adjudication 指针规则。
- `doc/REBASELINE_PLAN.md:60-61`：当前无 READY 节点；此 Task 列为表外节点。
- `doc/STATUS.md:7`：当前 Active Task 指针不指向本卡。

## 边界声明

本裁定不构成产品发布验收，不改变任何 Gate 结论，也不改写 `verification/**` 中的历史记录。是否登记收口以及何时更新权威状态仍由 DSH 按协作协议办理。

**推荐下一步：**由 DSH 在可变 Task 卡面追加本裁定及限制清单，Appointment 一名上下文独立的 Codex Reviewer 完成收口 Review，再按协作协议更新权威状态；当前没有依据要求释放新的架构容量实现 Task。

---

## DSH 采纳（2026-11-17，Lead）

**采纳结论**：全部采纳。理由与执行动作如下。

1. **Q1=(A)**：`GIT-CLEAN-RUST-ISOLATION-1` 的 AC3 实现面属 AD-002 已退役的 Tauri/Rust 线（`AGENTS.md` 产品边界：Tauri/React 仅保留为历史证据，不再释放 Legacy 实现/诊断/修复任务）。故**不在旧实现上补测**，本卡按 `closed_with_limitations` 收口，**AC1 保持 `<<PARTIAL>>`、AC3 保持 `<<BLOCKED>>` 原字节**。
2. **Q2**：R2-F01…F05 全部登记为 **`WONT_FIX_LEGACY`**（收口分类，不表示 finding 已修复；`verification/GIT-CLEAN-RUST-ISOLATION-1/r2/DISPOSITION.md` 原 `open` 状态与证据字节保持原样）。**不另立**新架构容量卡；若将来新架构复现对应**用户可见**问题，再按 `AGENTS.md` 另立卡并只验证该行为。
3. **Q3**：Codex 的 7 条限制逐条写入卡面 `## Closeout Record` 的 limitation 段；`reviewer` 由 `ZCode`（与 Owner 同 Agent，存在自审风险）改派为**上下文独立的子 agent**，并在卡面记录来源。
4. **不改写**：AC 标记、`verification/**` 历史证据、生产 `MAX=32` 与实现、契约/Schema/依赖，一律不动。
5. **边界**：本裁定与收口**不构成产品发布验收**，不改变任何 Gate 结论，不改变父候选/源 main。
