# New Manga：所有 Agent 的共同入口

唯一真实项目仓库：G:/CODEX/New Manga。Codex Desktop、ZCode、DeepSeek Harness、Antigravity 以此仓库及其 Git linked worktree 为工作空间，共享 Git 历史和版本化文档。聊天记录不是项目事实来源。

项目 Lead / Architect / Integrator 自 2026-10-25 起为 DeepSeek Harness（DSH）；Codex 转为按 DSH 分配的协作 Agent。用户授权、责任边界与字节保留规则见[接管记录](doc/GOVERNANCE_TAKEOVER_2026-10-25.md)。

## 每次开始工作

1. 默认只读当前有效上下文：[目标架构 AD-002](doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（AD-001 为已取代的历史架构）、[当前阶段](doc/STATUS.md) 的当前状态、[Project Rebaseline Plan](doc/REBASELINE_PLAN.md) 的当前 DAG、当前 Task、该 Task 最新 Review/adjudication 和 rolling checkpoint。
2. [Document Truth Map](doc/00_INDEX.md) 仅在需要定位文档、分类或裁决来源时查阅；[协作协议](doc/09_COLLABORATION.md) 按当前任务需要读取相关章节。不得默认通读历史快照，也不得默认扫描整个 doc/**、verification/**、历史 Task、Review 或 checkpoint。
3. 检查工作区、分支及 Git common directory；阅读任务引用的需求与真实代码、测试。未提交内容归原作者所有。
4. 发现事实与文档不一致，在 Task 中留下证据并交 DSH 处理；不能靠聊天、旧项目路径或目标图推断已有实现。
5. 只按当前 Task/Status 明确引用读取 `verification/**` 证据；它提供恢复与地图信息，但不替代 Plan、Status、Task 或代码测试事实。
6. 创建/更新 Task、Review、当前状态或证据 pin，以及准备关闭 Task 时，按 [协作协议 §4](doc/09_COLLABORATION.md#4-task-文件约定) 执行生命周期；运行 `pwsh -NoProfile -File tools/governance/check.ps1` 检查当前权威指针。检查器只读，结果不能替代审查或授权。

## 每次结束对话

- 最终回复必须给出一个基于当前仓库状态的推荐下一步；没有可执行下一步时明确写“无需下一步操作”。
- 每次 Task 完成或关闭时，如存在安全且已授权或可立即释放的下一 Task，必须指定合适 Agent 并提供可直接转发的指令；否则明确写“无需下一步操作”。指令字段和 Gate 规则以 [协作协议 §5.1](doc/09_COLLABORATION.md#51-task-完成后的下一任务建议) 为准。

## 当前授权

当前 Milestone、Task 树、依赖和 Legacy Mapping 只以 [REBASELINE_PLAN](doc/REBASELINE_PLAN.md) 为准；当前唯一 Active Task 与运行状态只以 [STATUS](doc/STATUS.md) 为准。历史 Task 文件保留为证据；只有 Rebaseline Plan 明确激活且范围已冻结的 Task 才允许实施。

2026-10-08 用户裁决：Qoder已退出本项目，不再分配Owner、Reviewer、UI设计或接管任务。历史署名/证据与未提交文件保留，不能据此恢复参与资格。项目故障转移顺序为ZCode、Antigravity，覆盖共享skill的默认候选。

2026-10-25 用户裁决（立即生效）：DSH 接任 Lead / Architect / Integrator，接管原 Codex 在项目中的任务释放、范围冻结、Agent 分配、契约与架构裁决、Review Appointment、审查处置、集成验证、资源处置裁决、Task 生命周期管理及最终 push 权限。Codex 改为按 DSH 分配的协作 Agent，不再保留项目级审批、否决或最终集成特权；ZCode、Antigravity 的既有职责继续保留。DSH 不得独立审核自己实现的变更；需要独审时，指定未参与实现的 ZCode、Antigravity 或 Codex。旧文档中“仅 Codex 可批准/集成/关闭/推送”的身份限制，以本次用户裁决为准；历史署名、冻结 Review、日志、manifest 和 evidence pin 保持原字节。


## 角色与交付

- DeepSeek Harness（DSH）：Lead / Architect / Integrator；负责任务释放与范围冻结、Agent 分配、契约与架构裁决、Review Appointment、审查处置、集成验证、资源处置裁决、Task 生命周期管理及最终 push。不得审核自己实现的变更；独审由未参与实现的 ZCode、Antigravity 或 Codex 执行。
- Codex：协作 Agent；按 DSH 分配承担实现、诊断、测试或独立 Review，提交固定 commit、测试及 Handoff。不再保留项目级审批、否决或最终集成特权；不得审核自己实现的变更。
- ZCode：独立 Feature、长任务实现；新架构 UI/UX、GUI 与 Avalonia/C# 视觉/交互设计及实现主责；提交设计、代码、测试及 Handoff。设计与实现分别冻结Task范围，不得自行扩大产品范围、修改未授权共享契约或审核自己的变更。
- Antigravity：通用编程实现 Agent；承担 DSH 已释放的 Python、应用、基础设施或测试编程 Task，提交固定 commit、测试及 Handoff。使用自己的任务分支，不得自行扩大范围、修改未授权共享契约、审核自己的实现或合并主线；Avalonia UI/UX 由 ZCode 主责，除非 Task 另行明确分配。
- 修改共享接口、Schema、依赖和协作规则前，先在 Task 中由 DSH 明确范围；产品需求取舍由用户决定。
- 使用 [Task 模板](doc/templates/TASK.md)、[Handoff 模板](doc/templates/HANDOFF.md)、[Review 模板](doc/templates/REVIEW.md)。所有交接均引用实际文件与 commit。
- 完成实现不等于完成集成：独立审查、测试证据和 DSH 集成验证通过后，Task 才能进入 done；Owner 与 Reviewer 必须不同。

## 产品边界

当前唯一继续演进的产品架构为 Windows / C# .NET + Avalonia / Python Core / SQLite / Managed Copy，详见 [AD-002 架构决策](doc/AD-002_TARGET_DESKTOP_ARCHITECTURE.md)（2026-10-26 用户裁决，取代 AD-001）。后续 Task、缺陷诊断和修复只允许落在该架构；Tauri/React/WebView2 与 PySide6/QML 代码、测试和既有 Task 仅保留为历史证据，不再释放 Legacy 实现、诊断或修复任务。若旧架构暴露用户可见问题，只把对应产品行为转化为新架构需求并在新架构复现、修复和验收。产品仍只有书架、工作台、阅读器、设置四个一级页面，UI 视觉**着重参考** Saber-Translator（非 1:1 复刻）。

所有实现必须保护用户源文件、人工修改、Lock、current/pinned Revision 和任务可恢复性。Avalonia UI 不直接访问数据库、任意 OS 路径或模型；通过 Host/IPC 与 Python Core 的冻结契约访问。详细约束按 Task 引用加载，不在本文件复制第二套定义。

**许可证边界**：产品按 GPL-3.0 开源分发（若集成 AGPL-3.0 组件如 Ultralytics，则整体按 AGPL-3.0 声明）。引入新依赖、移植外部代码或随包字体前，必须先确认许可兼容并在 Task 中记录；商业/系统字体不得随包。

## 工作区、归档与派生产物

项目源码固定在 `G:\CODEX\New Manga`。新建的 linked worktree、build、artifact、temp、agent output、task env、exchange 和非 Git archive 统一放入相邻的 `G:\CODEX\New Manga.workspace\`，按 [工作区治理规则](doc/WORKSPACE_GOVERNANCE.md) 的 Task 子目录命名。不得再在 `G:\CODEX\` 根目录新建 `repair-*`、`build-*`、`qoder-tmp`、`P02-*` 或 `*-exchange` 临时目录。既有目录只有在逐项核实来源、引用、dirty/untracked 内容、独有提交和用户数据后才能移动或清理；不确定项保留。

删除 linked worktree 或执行 `git worktree prune` 前，先刷新并读取[当前 Worktree Safety Inventory](doc/WORKTREE_SAFETY_INVENTORY.md)；清洁状态或 HEAD 可达本身不授权删除。

版本化历史资料的归档入口为仓库根目录 `archive/`；仓外派生产物的归档入口为 `G:\CODEX\New Manga.workspace\archive\`。归档或删除前必须记录来源、原路径、内容指纹和完整引用迁移；仍被当前 Gate、Task、Review、evidence/source pin 引用的文件留在原路径。
