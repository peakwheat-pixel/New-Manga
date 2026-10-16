---
task_id: P12-C1
title: 导入侧 IPC 契约修订
reviewer: dsh（项目权威 Reviewer，`.orchestrator/tasks/P12-C1-role.json`；role_exclusion 已排除 owner=codex）
owner: codex
base_commit: 5837e079a4ea0c08da93c0d64c8eed8770c961a0
declared_delivery_head: 919ca24731f5aaf50f1b46e8fe61c214b94c4b71
reviewed_head: e325e007231beb866d3bd2656bc081e9424acc15
review_worktree: G:/CODEX/New Manga.workspace/worktrees/P12-C1-IMPORT-IPC
date: 2026-10-16
mode: 只读审查 + 独立 Git/契约 diff 复核；未修改被审分支或主仓任何文件
object_binding: VERIFIED
severity: 冻结契约增量修订（rev 2.1 → 2.2；major 不变）
decision: approved
---

# P12-C1 独立 Review（R1）—— IPC 契约 rev 2.2（导入侧）

## 0. 复核结果（未采信自述）

| 项 | 方式 | 结果 |
|---|---|---|
| 变更范围 | `git diff --name-only 5837e079..HEAD` | **5 个路径，全部在授权范围** |
| **产品实现零改动** | 过滤 `^(src\|apps\|packaging)/` | **空** ✅ |
| **P11 契约完好** | 过滤 `P11_LONG_TASK` | **空** ✅ |
| **既有冻结 wire 完好** | 读契约确认 rev 2.0（Run）与 rev 2.1（Reader/Export）条目仍在，且 rev 2.2 头部明示"P13 Run wire、P16 Reader/Export wire 与 §10.3 `ExportTargetRef` 本文零语义变化" | ✅ |
| worktree / 主仓 | `git status` | worktree **clean**；主仓 **19 项 dirty 未变** |

## 1. 契约修订的逐项审查

| 关注点 | 审查结论 |
|---|---|
| **`ImportSourceRef` 定义**（AC1） | §10.4 冻结为 `{grant_id: OpaqueId, host_signature: string}`：**不透明、受限、可过期的读授权引用，不是路径或 URI**；**不得携带原始 bytes、Base64、绝对/相对路径或任何可解码出路径的字段**；仅在可信 Tauri host→Python Core 通道注入 ✅ |
| **与写引用同源（关键设计）** | 契约明示与 §10.3 `ExportTargetRef` 及 §10.1/§10.2 同源：**均由 Tauri host 授权、opaque、受限、过期、由 Core 解析并拒绝伪造/越 scope 引用**；**差异只有能力方向与生命周期**（`ImportSourceRef` 为 Core 控制的只读输入，可按 §10.1 T6 滑动续期并按来源撤销）——**未发明第二套授权**，与 P16-C1 的裁决要求一致 ✅ |
| **与 P09 语义对齐**（AC2） | 覆盖 P09 已交付行为：来源保护、Managed Copy、真实 `width/height`、重复/中断/Unicode；`sources` 必须非空且**所有引用与授权在首次读取之前验证**；命令级拒绝 `INVALID_REQUEST` / `TARGET_NOT_FOUND`，引用拒绝使用 §10.4 的稳定 `REF_*` code ✅ |
| **`ImportReport`**（AC3） | 可表达源文件 hash 与各 Page hash、真实 `width/height`、页序、重复判定、成功/跳过/拒绝/pending、错误类别与副作用边界 ✅ |
| **`ImportProgressChanged`**（AC4） | **明确保持 `UNKNOWN / PROPOSAL`**，理由：无持久导入 operation/snapshot wire 时，单独冻结事件**无法提供状态真值** ✅ **这是一个克制且正确的判断**——没有为了"看起来完整"而硬凑一个无真值支撑的事件 |
| **授权边界**（AC5） | §12 明确授权**导入侧** Python IPC Runtime，且限定冻结 allowlist；排除 React、Tauri/Rust、QML/Legacy、Schema/migration、依赖 ✅ |
| **版本策略** | rev **2.2** / envelope **major 2 · minor 2**；因**只新增冻结命令、不改既有冻结 wire**，**major 不变**（符合 §3.2）；并如实声明**不代表 Runtime 或产品验收已通过** ✅ |
| **诚实边界** | Owner 明确未把 **P09 项目级永久删除验收**记为通过（仍 `BLOCKED`），也未声称 `ImportPages` 已可用 ✅ |

## 2. Findings

| id | 级别 | 内容 | 处置 |
|---|---|---|---|
| **F1** | **P3（流程，同类第 8 次）** | `delivery_head` 申报 `919ca247`（契约冻结提交），实际 HEAD=`e325e007`（证据 pin 提交） | closeout 冻结实际 HEAD；BL-7 再次确认 |
| **F2** | P2（下游影响） | `ImportProgressChanged` 保持非冻结 → **P12/P17 的导入进度只能靠轮询/快照**，不存在"重要事件立即推送" | 需在释放 P12 时明确：进度刷新走查询面；若 UI 需要事件，须另立契约增量 |
| **F3** | P2（实现缺口） | 本 Task **只冻结契约**；Runtime 未实现，故 P18 实测的 **`ImportPages=UNKNOWN_COMMAND` 仍然存在**，直到实现 Task 完成 | 契约已就绪 → 建议下一步释放**导入侧实现 Task**（复用 P16-C1 → P16 模式），使端到端链路真正打通 |
| **F4** | P3（继承限制） | P09 的**项目级永久删除**验收仍 `BLOCKED`（Owner 未记为通过） | 与 `AC-IMPORT-002` 关联；保持登记，不随本契约消失 |
| F5 | P4 | `coverage-matrix` 标 D08 七条导入 AC 为 `WIRE_COVERED` | 措辞准确（"由 wire 承载"≠"验收通过"）；建议后续实现 Task 用真实运行替换该判定 |

**无 P0/P1 finding。**

## 3. 条件

- **C1**：Coordinator 集成时冻结实际被审 head `e325e007231beb866d3bd2656bc081e9424acc15`。
- **C2**：**下一步应释放导入侧实现 Task**（F3），否则 `ImportPages` 在运行时仍返回 `UNKNOWN_COMMAND`，P12 与 P19 仍无法端到端。
- **C3**：释放 P12 时须把 F2（进度只能轮询/快照）写入其范围说明。
- 契约内容本身无需返修。

## 4. 能力边界

- 本 Review 覆盖契约文本、范围合规、与 P09 语义对齐及版本策略；本 Task 无代码，**未运行任何 runtime 测试**。
- 所有 Git / 契约结论均由 Reviewer 在 live 环境实际执行。
- Reviewer 未修改被审分支、主仓或任何证据文件；未 push。
