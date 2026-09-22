# New Manga：所有 Agent 的共同入口

唯一真实项目仓库：G:/CODEX/New Manga。Codex Desktop、ZCode、DeepSeek Harness、Qoder、Antigravity 以此仓库及其 Git linked worktree 为工作空间，共享 Git 历史和版本化文档。聊天记录不是项目事实来源。

## 每次开始工作

1. 阅读 [Project Rebaseline Plan（唯一规划事实源）](doc/REBASELINE_PLAN.md)、[文档索引](doc/00_INDEX.md) 和 [当前阶段](doc/STATUS.md)。
2. 阅读 [协作协议](doc/09_COLLABORATION.md)，核对自己的 Task、依赖、授权状态、基线 commit 和允许修改路径。
3. 检查工作区、分支及 Git common directory；阅读任务引用的需求与真实代码、测试。未提交内容归原作者所有。
4. 发现事实与文档不一致，在 Task 中留下证据并交 Codex 处理；不能靠聊天、旧项目路径或目标图推断已有实现。
5. 若 `STATUS` 指向当前审计或 checkpoint，先阅读对应的 `verification/**` 证据；它提供恢复与地图信息，但不替代 Plan、Status、Task 或代码测试事实。

## 每次结束对话

- 最终回复必须给出一个基于当前仓库状态的推荐下一步；没有可执行下一步时明确写“无需下一步操作”。
- 每次 Task 完成或关闭时，必须给出下一 Task；同时指定合适的 Agent，并提供可直接转发的指令。指令字段和 Gate 规则以 [协作协议 §5.1](doc/09_COLLABORATION.md#51-task-完成后的下一任务建议) 为准。

## 当前授权

当前 Milestone、Task 树、依赖和 Legacy Mapping 只以 [REBASELINE_PLAN](doc/REBASELINE_PLAN.md) 为准；当前唯一 Active Task 与运行状态只以 [STATUS](doc/STATUS.md) 为准。历史 Task 文件保留为证据；只有 Rebaseline Plan 明确激活且范围已冻结的 Task 才允许实施。


## 角色与交付

- Codex：Lead / Architect / Integrator；负责契约、任务分配、冲突决策及集成。
- ZCode：独立 Feature、长任务实现；提交代码、测试及 Handoff。
- Qoder：UI/UX、GUI 与 QML 视觉/交互设计责任方；同时承担独立 Feature、长任务实现（与 ZCode 同面），提交代码、测试及 Handoff；也可作为**非作者** Reviewer。设计交付不能替代已释放 Task；不得自行扩大产品范围、修改共享契约或审核自己实现的变更。
- DeepSeek Harness：技术实验、OCR / Translation / Inpainting 研究、测试、Bug 分析及独立 Review。不得审核自己实现的变更。
- Antigravity：通用编程实现 Agent；承担 Codex 已释放的 Python、应用、基础设施或测试编程 Task，提交固定 commit、测试及 Handoff。使用自己的任务分支，不得自行扩大范围、修改未授权共享契约、审核自己的实现或合并 master；QML/UI/UX 任务仍由 Qoder 主责，除非 Task 另行明确分配。
- 修改共享接口、Schema、依赖和协作规则前，先在 Task 中由 Codex 明确范围；产品需求取舍由用户决定。
- 使用 [Task 模板](doc/templates/TASK.md)、[Handoff 模板](doc/templates/HANDOFF.md)、[Review 模板](doc/templates/REVIEW.md)。所有交接均引用实际文件与 commit。
- 完成实现不等于完成集成：独立审查、测试证据和 Codex 集成验证通过后，Task 才能进入 done。

## 产品边界

目标为 Windows / Python / PySide6 QML / SQLite / Managed Copy；只有书架、工作台、阅读器、设置四个一级页面。具体规则分别以 01～08 文档的职责为准，见索引。目标能力不代表已实现能力。

所有实现必须保护用户源文件、人工修改、Lock、current/pinned Revision 和任务可恢复性。QML 不直接访问数据库、文件或模型。详细约束按 Task 引用加载，不在本文件复制第二套定义。
