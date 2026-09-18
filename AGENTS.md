# New Manga：所有 Agent 的共同入口

唯一真实项目仓库：G:/CODEX/New Manga。Codex Desktop、ZCode、DeepSeek Harness 以此仓库及其 Git linked worktree 为工作空间，共享 Git 历史和版本化文档。聊天记录不是项目事实来源。

## 每次开始工作

1. 阅读 [文档索引与 Source of Truth](doc/00_INDEX.md) 和 [当前阶段](doc/STATUS.md)。
2. 阅读 [协作协议](doc/09_COLLABORATION.md)，核对自己的 Task、依赖、授权状态、基线 commit 和允许修改路径。
3. 检查工作区、分支及 Git common directory；阅读任务引用的需求与真实代码、测试。未提交内容归原作者所有。
4. 发现事实与文档不一致，在 Task 中留下证据并交 Codex 处理；不能靠聊天、旧项目路径或目标图推断已有实现。

## 每次结束对话

- 最终回复必须给出一个基于当前仓库状态的推荐下一步；没有可执行下一步时明确写“无需下一步操作”。
- 下一步需要其他 Agent 执行时，同时提供可直接转发的指令，至少写明实际工作路径、Task、固定 base/head、允许与禁止范围、交付物和验证要求。

## 当前授权

当前阶段、已释放 Task 与冻结范围只以 [STATUS](doc/STATUS.md) 和对应 Task 文件为准，本入口不复制易过期的状态。Agent 只能执行已批准且依赖满足的 Task；接管、Review 或单个 Task 获批不等于其他开发自动获批。


## 角色与交付

- Codex：Lead / Architect / Integrator；负责契约、任务分配、冲突决策及集成。
- ZCode：独立 Feature、长任务实现；提交代码、测试及 Handoff。
- DeepSeek Harness：技术实验、OCR / Translation / Inpainting 研究、测试、Bug 分析及独立 Review。不得审核自己实现的变更。
- 修改共享接口、Schema、依赖和协作规则前，先在 Task 中由 Codex 明确范围；产品需求取舍由用户决定。
- 使用 [Task 模板](doc/templates/TASK.md)、[Handoff 模板](doc/templates/HANDOFF.md)、[Review 模板](doc/templates/REVIEW.md)。所有交接均引用实际文件与 commit。
- 完成实现不等于完成集成：独立审查、测试证据和 Codex 集成验证通过后，Task 才能进入 done。

## 产品边界

目标为 Windows / Python / PySide6 QML / SQLite / Managed Copy；只有书架、工作台、阅读器、设置四个一级页面。具体规则分别以 01～08 文档的职责为准，见索引。目标能力不代表已实现能力。

所有实现必须保护用户源文件、人工修改、Lock、current/pinned Revision 和任务可恢复性。QML 不直接访问数据库、文件或模型。详细约束按 Task 引用加载，不在本文件复制第二套定义。
