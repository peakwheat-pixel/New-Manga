---
task_id: HOST-ISSUER-1-C1
title: host→Core grant 注册通道契约
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/HOST-ISSUER-1-C1-role.json`；role_exclusion 已排除 owner=codex）
owner: codex
base_commit: 6a5051dcafa549f200730a4f9824d83d187f07a2
declared_delivery_head: af6fa705de54489ce32811cdc8dd3be51a1fd999
reviewed_head: 13cc2bb5440b9d4bfb9e01266b9045079de84e65
review_worktree: G:/CODEX/New Manga.workspace/worktrees/HOST-ISSUER-1-C1
date: 2026-10-16
mode: 只读审查 + 独立 Git/契约 diff 复核；未修改被审分支或主仓任何文件
object_binding: VERIFIED
severity: 冻结契约增量修订（rev 2.2 → 2.3；major 不变）—— 补上 §11 遗留的 `auth/permission handshake`
decision: approved
---

# HOST-ISSUER-1-C1 独立 Review（R1）—— IPC 契约 rev 2.3（HostControl）

## 0. 复核结果（未采信自述）

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only 6a5051dc..HEAD` | **6 个路径，全部在授权范围** |
| **产品代码零改动** | 过滤 `^(src\|apps\|packaging\|tests)/` | **空** ✅ |
| **P11 契约完好** | 过滤 `P11_LONG_TASK` | **空** ✅ |
| **既有冻结 wire 完好** | 读 revision history 与 verb 计数 | rev **2.0/2.1/2.2/2.3 四条全在**；`idempotency_key` 12 处、`GetReaderProjection` 9、`StartExport` 7、`ImportPages` 12、`RetryFailedTargets` 16、`ResumeBlockedRun` 10、`ReadingProgressChanged` 5 —— **全部存在** ✅ |
| worktree / 主仓 | `git status` | worktree **clean**；主仓 **19 项 dirty 未变** |

## 1. 契约修订的逐项审查

| 关注点 | 审查结论 |
|---|---|
| **host-only 边界的表达**（AC1，本 Review 核心） | §5.7 把授权控制面做成**独立 `HostControl` envelope**，并明确声明它**"不属于 §3 普通 application `Request<T>` command catalog，也不是 Tauri command"**；唯一通道是 Tauri host **直接 spawn 并持有**的 `bootstrap.core_service` 子进程 stdio。**架构上正确**：不是"在普通命令上加权限位"，而是**从路由层面隔离** ✅ |
| **非 host 调用的拒绝** | §5.7 规定：普通 JSON-RPC 尝试调用 host-only 操作 → **`HOST_ONLY_REQUIRED`**（validation）；credential 缺失/错误或 session 已关闭 → **`HOST_SESSION_INVALID`**（conflict）；`core_session_id` 不符 → **`CORE_SESSION_MISMATCH`**（conflict）。三者均明确"**拒绝；不调用 seam**" ✅ |
| **session 绑定与失效**（AC2） | Core 每进程生成新 `core_session_id`；host 在向 WebView 暴露普通 Core 操作**之前**只能内部调用一次 `OpenHostSession`；host 生成并保管 credential。grant 绑定**当前 Core 实例 + host session**；关闭/轮换 host session 撤销其 grants；Core 重启丢弃进程内 registry；撤销**立即**影响后续引用校验 ✅ |
| **与 §10.3/§10.4 一致**（AC3） | 契约明示**现有 ref 字段、签名输入与 `REF_*` 语义没有改变**；注册只是把 grant 放进 registry，不改变 ref 的形态与校验面 ✅ |
| **错误面与零副作用**（AC4） | 错误表逐类给出稳定码，且每类均要求"拒绝；不调用 seam"；配合既有 Core 侧"拒绝不产生库/文件写入"的断言，语义闭合 ✅ |
| **§12 授权边界**（AC5） | 只授权后续实现所需的 **Core handler 最小改动**（`src/bootstrap/core_service.py`、`tests/core/**`）；明确未授权 React/WebView、**面向 WebView 的 Tauri 命令**、Schema/migration、依赖或其他产品行为 ✅ |
| **版本策略** | rev **2.3** / protocol **2.3**；因**只新增独立 control 面、不改既有 application command catalog**，**major 不变**（符合 §3.2 minor widening）；并声明既有 ref wire 与操作语义未破坏 ✅ |
| **诚实边界** | Owner 明确声明"契约覆盖完整**不代表** runtime 已实现或验证"；并如实记载 grant 上限、多来源同时注册等策略**本次未裁定** ✅ |

## 2. 对 HOST-ISSUER-1 阻塞的处置复核

- HOST-ISSUER-1 的阻塞是**真实架构缺口**：`_register_*`/`_revoke_*` 为 in-process 私有方法、无 dispatcher 路由、
  registry 为 per-instance 内存态、`core_bridge` sidecar 不持有 registry、WebView 暴露会破坏受信边界。
- 本契约给出的解法**正面回应**了全部五点：独立 envelope + direct-child stdio + session 凭证 + 三拒绝码 + 普通路由不承认这些命令。
- **复核结论：解法定向正确，未回避任何一项事实**。

## 3. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P3（流程，同类第 10 次）** | `delivery_head` 申报 `af6fa705`（契约冻结提交），实际 HEAD=`13cc2bb5`（证据提交） | closeout 冻结实际 HEAD；BL-7 再次确认 |
| **F2** | P3（未裁定项） | **grant 上限、是否允许多来源同时注册**等策略未在本契约裁定（Owner 已声明） | 若 P12/P17 的实现需要这些策略，须以**契约增量**处理；不得由实现方自行决定 |
| **F3** | **P2（恢复前置）** | 本契约冻结后，**HOST-ISSUER-1 仍不能立即恢复**：除本通道外还受阻于 **BL-11（`cargo build`/`cargo test` exit 101：`core-sidecar` bundle 与打包/前端前置缺失）** | 恢复 HOST-ISSUER-1 前须先处理 BL-11（`packaging/m2ac5/build_sidecar.ps1` 入口）；建议登记为独立环境 Task 或先行修复 |
| F4 | P3（验证边界） | 本 Task 为契约设计，**无 runtime 测试**；契约覆盖 ≠ 实现验证 | 实现验证留给恢复后的 HOST-ISSUER-1 |
| F5 | P4 | 沿用了 P16/P12-C1 的"同源"表述并要求 ref 不变 | 一致，无异议 |

**无 P0/P1 finding。**

## 4. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `13cc2bb5440b9d4bfb9e01266b9045079de84e65`。
- **C2**：**恢复 HOST-ISSUER-1 前必须先解 BL-11**（构建前置），否则其 AC8 仍会 exit 101；建议把 BL-11 作为独立环境 Task 优先处置。
- **C3**：HOST-ISSUER-1 恢复时须把新版 main（含本契约 rev 2.3）并入其分支 `fa270d85`，并以其 AC1–AC7 重跑。
- **C4**：F2 的策略项（grant 上限/多来源）若被需要，须另立契约增量，实现方不得自行决定。
- 契约内容本身无需返修。

## 5. 能力边界

- 本 Review 覆盖契约文本、范围合规、既有冻结 wire 的完整性、host-only 边界的架构正确性与版本策略；**未运行任何构建或 runtime 测试**。
- 所有 Git / 契约结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
