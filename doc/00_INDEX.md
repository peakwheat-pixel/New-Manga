# Document Truth Map / 项目文档权威地图

更新：2026-10-25（DSH 接任 Lead / Architect / Integrator；角色迁移与字节保留见[接管记录](GOVERNANCE_TAKEOVER_2026-10-25.md)）。当前目标架构固定为 Windows + React + TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy。本文是文档导航和冲突裁决表，不替代下列权威来源。

## 权威来源与冲突裁决

| 事实类型 | 唯一权威来源 | 解释 |
|---|---|---|
| 当前目标架构与技术边界 | [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md)；后续用户明确裁决优先 | 目标是 React/TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy。PySide6/QML 仅为旧生产基线/迁移参考。 |
| 项目规则与 Agent 权限 | [AGENTS.md](../AGENTS.md) | 当前角色、安全边界、默认上下文和工作区规则。 |
| Milestone、Task DAG、依赖和释放状态 | [REBASELINE_PLAN](REBASELINE_PLAN.md) | 历史 Task 文件、聊天记录和旧计划快照不能激活 Task。 |
| 唯一活动 Task 与运行状态 | [STATUS](STATUS.md) | 仅此处声明当前 Active Task、Gate、阻塞和恢复指针。 |
| Task 范围与冻结契约 | Plan 指定的当前 Task、该 Task 明确引用的契约 | 已完成或历史 Task 不构成当前授权。 |
| Review 结论 | 当前 Task 最新 Review 及 DSH adjudication | adjudication 记录 finding 的接受/拒绝及限制。 |
| 当前恢复点 | STATUS 指定的 rolling checkpoint | 只为恢复当前 Task，不替代 Task、Review 或原始证据。 |
| 技术事实/验证结果 | 当前 Task 指定的原始 evidence/source pin | 证据说明其实际测得内容；不自行授予授权或改写 Review/adjudication。 |

冲突时，先按事实类型选择权威来源。历史文档的旧技术路线、Task 状态和 Gate 不得覆盖当前来源；不得把要求文档、旧图或验证结果解释为实现授权。

## 当前文档地图

| 文档 | 分类 | 当前可依赖内容 |
|---|---|---|
| [AGENTS.md](../AGENTS.md) | CURRENT / GOVERNANCE | Agent 项目入口、角色、安全和最小读取规则。 |
| [接管记录](GOVERNANCE_TAKEOVER_2026-10-25.md) | CURRENT / GOVERNANCE | 2026-10-25 用户裁决：Codex 的 Lead / Architect / Integrator 权限移交 DSH；历史署名与证据字节保留。 |
| [Push 记录](PUSH_RECORD_2026-10-25.md) | CURRENT / DELIVERY RECORD | 干净源码快照推送到 `origin/codex/clean-source-snapshot` 的授权、审查、命令、远端 SHA 核验与未关闭项。 |
| [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) | CURRENT / ARCHITECTURE | 唯一目标架构及边界。 |
| [REBASELINE_PLAN](REBASELINE_PLAN.md) | CURRENT / PLAN | 当前 DAG 和 Task 释放/阻塞关系。 |
| [STATUS](STATUS.md) | CURRENT / STATUS | 当前唯一 Active Task、Gate 状态和恢复指针。 |
| [09 协作协议](09_COLLABORATION.md) | CURRENT / PROCESS | 协作、Review、handoff 和 Task 关闭流程；按需读取。 |
| [Workspace Governance](WORKSPACE_GOVERNANCE.md) | CURRENT / GOVERNANCE | 分类、归档、证据保护及派生产物规则。 |
| [Governance checker](../tools/governance/check.ps1) | CURRENT / AUTOMATION | 只读检查当前指针、相对引用、目标架构标记、STATUS/PLAN 预算及受治理 Task 的 canonical evidence/closeout 字段。 |
| [Worktree Safety Inventory](WORKTREE_SAFETY_INVENTORY.md) | CURRENT / OPERATIONAL | 删除 worktree 或 prune 前必须刷新并读取。 |
| [Task templates](templates/TASK.md)、[Review template](templates/REVIEW.md)、[Handoff template](templates/HANDOFF.md) | CURRENT / TEMPLATE | 仅在创建对应交付时读取。 |
| [TASK-002 minimum contract](contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md) | TASK-SCOPED / SEMANTIC CONTRACT | G06–G13 semantics only when a current Task cites it; subordinate to AD-001 and not authority for QML/React UI architecture. |
| Plan 指向的当前 Task、最新 Review/adjudication、checkpoint 和证据 | CURRENT / TASK-SCOPED | 只读当前 Task 明确引用的版本；其他内容均按需检索。 |
| [01 功能架构](01_FUNCTIONAL_ARCHITECTURE.md)、[03 数据模型](03_DATA_MODEL.md)、[04 用户流程](04_USER_FLOW.md) | REQUIREMENT REFERENCE | 产品行为/概念数据意图；不授予实现权限。03 的正式字段与写入契约以当前 Task 冻结契约为准。 |
| [06 Translation Pipeline](06_TRANSLATION_PIPELINE.md) | REQUIREMENT + LEGACY MAPPING | 业务流程与安全语义可作需求参考；Qt/QML 接线是历史映射。 |
| [07 非功能需求](07_NON_FUNCTIONAL_REQUIREMENTS.md)、[08 验收标准](08_ACCEPTANCE_CRITERIA.md) | MIXED / REQUIREMENT | 产品级要求保留；旧 Qt/QML/PyInstaller 实现与 Gate 不可继承到新架构。 |
| [02 技术架构](02_TECHNICAL_ARCHITECTURE_.md)、[05 UI 映射](05_UI_MAPPING.md)、[11 架构地图](11_ARCHITECTURE_MAPS.md) | LEGACY / HISTORICAL | PySide6/QML 旧生产基线与当时架构映射；不得作为目标架构或新 Task 实施说明。 |
| [10 接管状态](10_CURRENT_STATE_AND_GAPS.md)、[12 Roadmap](12_ROADMAP.md)、[13 验收追踪](13_ACCEPTANCE_TRACEABILITY.md)、[14 接管验证](14_TAKEOVER_VERIFICATION.md) | HISTORICAL | 带时间点的历史事实、编号与验证结果；不参与当前 DAG、状态或新架构验收。 |
| [2026-10-12 计划/状态/索引快照](../archive/history/2026-10-12/README.md) | ARCHIVE | 被当前导航替代的完整历史快照，仅审计/恢复时读取。 |

## 架构状态裁决

| 状态 | 定义 | 当前记录 |
|---|---|---|
| 旧生产基线 | 曾实际采用的历史生产架构 | Python + PySide6/QML + SQLite；仅作为 Legacy Production Baseline / Migration Reference。 |
| 迁移中间态 | 特定迁移 Task 中的阶段性实现状态 | 不构成另一个产品目标；仅由当前 Task 明确范围描述，不得推翻目标架构或默认释放 QML 工作。 |
| 用户最终目标 | 当前唯一继续演进的产品架构 | Windows + React + TypeScript + Tauri/Rust + Python Core + SQLite + Managed Copy。 |

因此，2026-09-25 注册快照中的 QML 保留/parity 计划、旧 M2 释放列表和 Qoder 分工均不代表当前决定；详情仅在 [AD-001 pre-Rebaseline snapshot](../archive/history/2026-10-13/document-rebaseline/source/doc/AD-001_TARGET_DESKTOP_ARCHITECTURE.md) 中作为原始历史文本保留。该归档副本不是权威来源。

## Agent 默认最小读取集

1. AGENTS.md
2. AD-001
3. STATUS 当前状态段
4. REBASELINE_PLAN 当前 DAG
5. Plan 指定的当前 Task
6. 该 Task 最新 Review/adjudication
7. STATUS 指定的 rolling checkpoint

本索引只在需要定位文档或判断分类时读取。不得默认扫描全部 doc、Task、Review、verification、checkpoint 或 archive；历史材料只有在当前 Task 明确需要时按需读取。仓库根目录没有 README.md；本文件承担文档入口与真相地图。
