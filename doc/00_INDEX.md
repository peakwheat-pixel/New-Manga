# 项目文档索引与 Source of Truth

状态：TASK-001～TASK-014、TASK-028 设计、TASK-029 统一 SQLite 持久化实现、TASK-030 入口装配与 TASK-031 生产 ImageDecoder/Managed Copy 适配器已完成并集成；TASK-013 生产 Pipeline seam 已按 `integration_commit=49c72fdf` 集成，R-1 已按 `integration_commit=734d5b3` 完成生产 Workbench 装配并验证；TASK-016 已按 `integration_commit=9bf85f5` 完成集成；TASK-015 已按窗口条款收口 `done`（integration=`fa72cee`，Review=`approved_subagent`）；TASK-024 已按窗口条款收口 `done`（仅设计，integration=`61c33e2`，扩展边界设计见 [TASK-024 契约](contracts/extensions.md)，待用户批准 U-1~U-6），TASK-017 已按窗口条款收口 `done`（integration=`c0cf3a1`，实验报告见 [doc/research/TASK-017.md](research/TASK-017.md)），窗口三项目标（TASK-015/024/017）全部完成，其余 TASK-018～TASK-027 继续冻结。仓库现状见 [STATUS](STATUS.md)。2026-09-16 23:30 ～ 09-17 08:30（Asia/Shanghai）的 ZCode 全权窗口已经用户指示于 2026-09-17 归还撤销（窗口目标 TASK-015/024/017 均已收口 `done`，交付留待外部 post-hoc 复审）；条款存档见 [STATUS](STATUS.md)「ZCode 全权窗口授权」。所有路径均相对本文档；保留现有 doc 目录及 02 文件名末尾的下划线。

## 原始目标文档（已完整检查）

| 证据编号 | 文档 | 权威职责 | 当前性质 |
|---|---|---|---|
| D01 | [01 功能架构](01_FUNCTIONAL_ARCHITECTURE.md) | 产品能力范围、入口、扩展能力 | To-Be；§5 的旧代码引用不能证明本仓库实现 |
| D02 | [02 技术架构](02_TECHNICAL_ARCHITECTURE_.md) | 分层、技术选型、依赖边界、运行拓扑 | To-Be；TASK-005 仅实证最小 Python/PySide6 Core 入口与当前包边界 |
| D03 | [03 数据模型](03_DATA_MODEL.md) | 实体、字段、数据不变量、持久化归属 | To-Be；G06～G13 的最小实现契约由 TASK-002 冻结；TASK-006 已有 v1 SQLite 基础，统一 v2 设计见 TASK-028 |
| D04 | [04 用户流程](04_USER_FLOW.md) | 操作意图、用户流程、对象范围 | To-Be |
| D05 | [05 UI 映射](05_UI_MAPPING.md) | Screen、Panel、Window、动作与 ViewModel 映射 | To-Be；内含线框示意，非实际 QML |
| D06 | [06 Pipeline](06_TRANSLATION_PIPELINE.md) | 命令语义、DAG、Lock、失效、重试与进度协议 | To-Be；G06～G13 的最小执行契约由 TASK-002 冻结 |
| D07 | [07 非功能需求](07_NON_FUNCTIONAL_REQUIREMENTS.md) | 性能、容量、可靠性、安全、Windows 与打包 | 目标数值，未经 Benchmark 验证 |
| D08 | [08 验收标准](08_ACCEPTANCE_CRITERIA.md) | 验收预期、证据要求与发布 Gate | 验收规格，不是测试实现或 PASS 报告 |

TASK-001 已将 D03～D08“基于”列表里的历史长文件名改为上表实际文件；这只恢复当前项目导航，不证明与未提供的历史版本逐字一致。原始引用保存在基线 `496b4ed`。

## 接管与执行文档

| 文件 | 用途 / 何时阅读 |
|---|---|
| [AGENTS.md](../AGENTS.md) | 三 Agent 每次进入项目必读入口 |
| [STATUS](STATUS.md) | 当前授权、开发阶段、用户审核记录 |
| [09 协作协议](09_COLLABORATION.md) | 角色、Git、Task/Handoff/Review 生命周期 |
| [10 当前状态与 Gap Analysis](10_CURRENT_STATE_AND_GAPS.md) | 本次盘点、证据指纹、代码与目标差距、审核清单 |
| [11 架构与交互地图](11_ARCHITECTURE_MAPS.md) | 11 类接管基线视图；目标设计仍不得冒充 TASK-005 最小骨架的实际能力 |
| [12 Roadmap](12_ROADMAP.md) | 阶段 Gate、依赖和范围取舍 |
| [13 验收追踪](13_ACCEPTANCE_TRACEABILITY.md) | D08 条目到计划 Task 的映射；不代表已验收 |
| [14 接管验证](14_TAKEOVER_VERIFICATION.md) | 本次文档自检结果、复现命令与验证边界 |
| [接管自检脚本](verify_takeover.ps1) | 仅适用于初始接管快照；TASK-001 已修改文档与授权，其 Hash/冻结断言不再适用于当前工作区 |
| [TASK-001 检查](../verification/TASK-001/verify.ps1) | 验证文档引用、状态枚举、AC 编号/优先级及修改范围 |
| [TASK-002 最小契约](contracts/TASK-002_MINIMUM_DATA_EXECUTION_CONTRACT.md) | G06～G13、R-011 的冻结语义；后续 Schema/Pipeline/UI/测试共同输入 |
| [TASK-028 统一 SQLite 设计](contracts/TASK-028_UNIFIED_SQLITE_PERSISTENCE_DESIGN.md) | TASK-006/007/008 的 SQLite 收敛设计；实现由 TASK-029 承接 |
| [TASK-029 统一 SQLite 实现](tasks/TASK-029.md) | 按 TASK-028 实现 v2 migration、Library/Page/Region adapter 与原子 Revision seam；已集成 |
| [任务目录](tasks/README.md) | 30 个 Task 索引；单个文件是任务状态真值 |
| [Task 模板](templates/TASK.md) | 新任务创建 |
| [Handoff 模板](templates/HANDOFF.md) | 实现 / 实验交付、故障中断交接 |
| [Review 模板](templates/REVIEW.md) | 按固定 commit 独立审查和复审 |

handoffs、reviews、verification 已包含固定提交的真实交付；目录或文件名本身仍不等于审查/验证通过。

## Source of Truth 按问题区分

| 要回答的问题 | 事实来源 | 不能替代它的材料 |
|---|---|---|
| 当前实际做到了什么 | 当前项目 commit 的源代码、迁移、配置与同 commit 测试证据；工作区变化单独说明 | To-Be 图、旧项目能力表、Agent 自述 |
| 产品应该做什么 | D01/D04/D05；冲突提交用户决策并在相关权威文档修订 | 实现中的偶然行为、测试中的猜测 |
| 架构及数据怎么约束 | D02/D03/D06 按职责管理；已冻结缺口以对应 `doc/contracts/` 文件解释 | 任意 Agent 的私有笔记 |
| 什么算达标 | D07/D08 与可复现 verification 记录 | 仅有测试文件或“本地通过”口头描述 |
| 谁在做什么、可改哪里 | STATUS 的阶段授权 + 单个 Task 文件 | 看板截图、聊天中的认领 |
| 交付了什么 | Handoff 中固定 commit、文件与测试结果 | 分支名称本身、作者概述 |
| Review 是否完成 | 独立 Review 报告绑定的 base/head + Codex 集成验证 | 作者自查或对旧 head 的批准 |

不存在“代码永远胜过需求”或“编号越大越权威”的规则。代码回答实际行为，文档回答目标，两者差异记录为 Gap。D08 明确要求冲突先修订设计，不能用测试替代设计决策（D08 L15）。

冲突处理：记录双方文件/章节/行号 → 在 Gap/Task 标明影响 → Codex提出可审查修改 → 产品范围变化由用户决定 → 在权威文档修订并同步受影响图和 AC。当前发现的问题尚未自动裁决。

## 文档维护规则

- 新事实标明 As-Is（代码/测试）、To-Be（目标）、Proposal（本次建议）或 Unknown（无证据）。
- 原始 01～08 已保存在初始基线；后续仅按已授权 Task 修订。接管报告的 SHA256 是修订前指纹，不是当前文件必须保持的值。
- 架构图与矩阵是派生视图；出现实现后补充 source/test 路径与 commit，才能标为代码生成。
- 代码、测试和文档同一 Task 一起交付。涉及未分配的共享文档，先交 Codex协调写权限。
- 同一个结论只维护一个权威位置，其余位置使用链接；STATUS 管阶段，Task 管进度，Review 管审查结论。
