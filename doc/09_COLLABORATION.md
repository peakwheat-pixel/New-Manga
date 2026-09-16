# Codex / ZCode / DeepSeek Harness 协作协议

本协议将用户本次协作安排固化为可共享文件。当前只准备接管资料，所有未来实施仍受 [STATUS](STATUS.md) 的冻结约束。

## 1. 角色与权限

| Agent | 主责 | 交付物 | 集成权限 |
|---|---|---|---|
| Codex Desktop | Lead / Architect / Integrator；盘点、契约、拆任务、协调依赖、处理冲突 | 基线文档、Task、集成验证与决策记录 | 唯一主线写入和合并责任人 |
| ZCode | 独立 Feature、长任务 | 固定 commit、代码与必要测试、Handoff | 自己的任务分支；不得自行合并主线 |
| DeepSeek Harness | 技术实验、OCR/Translation/Inpainting 研究、测试、Bug 分析、独立 Code Review | 可复现实验、测试证据、诊断/Review 报告 | 自己的实验或测试分支；不得自行改生产实现以“证明”Review |
| 用户 | 产品取舍、阶段审核、重大范围变化 | 由 Codex 记录的审核决定 | 决定接管及后续阶段范围 |

Owner 与 Reviewer 必须不同。DeepSeek 自己的测试/实验由 Codex 或 ZCode 独立审查；Codex 的实现优先由 DeepSeek 审查。工具不可用时记录 reviewer_unavailable，等待可用 Reviewer；不得虚构独立批准。

研究结论不自动成为产品需求。诊断任务只读分析与复现；修复需要有允许修改生产代码的 Task。Reviewer 默认只写 Review 报告。

## 2. Git：一个仓库、多个 linked worktree

实际主工作区 G:/CODEX/New Manga；当前分支 master。保留现有名字，未要求改为 main。无 remote，当前不设计 PR/push 为必需流程。

批准接管后先由 Codex 创建可复现的初始基线 commit，再开放任务分支。未提交的当前接管文件不能充当可跨 worktree 同步的基线。第一次提交的 author 使用实际 Git 身份，不能冒用其他 Agent 的签名。

并行模式：Codex 使用主工作区；ZCode 和 DeepSeek 使用同仓库的 linked worktree。每个 worktree 独立 checkout/index，Git common directory 相同。另建同名仓库、复制源码目录当真值、在任务 worktree 再执行 git init 均不符合此约定。

开始时记录以下检查结果：

~~~powershell
git rev-parse --show-toplevel
git rev-parse --path-format=absolute --git-common-dir
git branch --show-current
git status --short --branch
git worktree list --porcelain
git rev-parse HEAD
~~~

linked worktree 的 toplevel 可以不同，但 common directory 必须指向本项目 .git。初始仓库 HEAD 不存在时，由 Codex先完成基线提交；其他 Agent 不自行绕过。

分支约定：agent/codex/TASK-xxx-slug、agent/zcode/TASK-xxx-slug、agent/deepseek/TASK-xxx-slug。一个 Task 一个 Owner，一个分支；实际路径由 Codex 分配并填进 Task，不能复制模板中的示例命令直接执行。

同一物理 checkout 同时只允许一个写入者；无法使用 worktree 时串行交接。read-only Review 也固定被审查 commit，不对正在写的 checkout 运行会改文件的命令。

## 3. 任务释放、并行和共享文件

1. Codex 将用户批准的范围落入 STATUS。
2. Task 依赖全部 done，接口和允许路径具体化，填 owner、base_commit、branch/worktree 后才能从 proposed 变 ready。
3. Codex 串行登记认领，然后 Owner 在任务分支将 ready 改 in_progress；所有 Agent 以已集成 Task 记录为准。两个 Agent 不能仅靠各自编辑副本宣称同时认领成功。
4. 并行只用于无未完成依赖且写集合互不重叠的 Task。共用 Schema、ports、启动配置、依赖清单、AGENTS、Task 总索引由 Codex协调；超出 allowed_paths 时暂停越界部分，在 Task 提出范围变更。
5. Task 文档由 Owner 更新；总索引由 Codex更新。工作日志、阻塞、测试结果及时写进任务文件，长任务不能只留在聊天。
6. 为统一授权口径，所有 Task 的默认元数据维护范围包括由 Codex 负责的 `doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/STATUS.md`、`doc/tasks/README.md`；仅可回填状态、Task 导航和链接，不得借此修改需求、契约或代码范围。Task 的 `allowed_paths` 仍决定 Owner 可写范围。
7. 每个 Agent 的测试数据根目录、临时目录、数据库、模型缓存及输出分别隔离。共享 Git 仓库不等于共享可写 app.db 或用户漫画库。

禁止覆盖他人未提交修改、未经协调切换他人分支、自动 stash 他人内容、强制 push 或清理他人 worktree。冲突由 Codex结合两侧需求处理，禁止整文件盲选 ours/theirs。

## 4. Task 文件约定

任务文件：doc/tasks/TASK-xxx.md；复制 [模板](templates/TASK.md)。

必须包含：ID、kind、status、suggested_owner、实际 owner、reviewer、depends_on、approval、base_commit、branch、worktree、需求来源、结果目标、Acceptance Criteria、allowed_paths、禁止范围、测试计划、产物与交接链接、已知阻塞。

状态：proposed → ready → in_progress → in_review → approved → done。

- proposed：规划，不允许实施。
- ready：阶段已获准、依赖已集成、Owner 和范围确定。
- in_progress：正在实施。
- blocked：记录 blocker、恢复条件与前一个状态；不是完成。
- in_review：交付 head 固定、测试和 Handoff 齐全。
- changes_requested：Reviewer 要求修订，修订后回到 in_review。
- approved：独立审查通过，等待 Codex 集成。
- done：Codex 已集成，记录 integration_commit 并完成集成后验证。

Task 的开发状态与产品 PipelineRun 状态是两套不同概念，不能混入应用 Schema。

测试项必须注明 planned / executed、命令、环境、结果、证据；结果中的 `passed` 与 `skipped` 必须分列（如 `290 passed, 6 skipped`），并为每个 skip 记录原因。测试命令尚无实现时写“计划命令”，不能假装可立即运行。Acceptance Criteria 的逐项满足需实际证据，不能仅引用 D08 标题。

## 5. Handoff

交付文件：doc/handoffs/TASK-xxx-<short-head>.md，使用 [Handoff 模板](templates/HANDOFF.md)。

至少记录：基线 commit、交付 commit、提交列表、变更路径、做了什么、AC 对照、实际测试命令和结果、未跑项、风险/遗留问题、启动或复现方式、下一接收者。实验额外记录数据来源/许可、数据 Hash、模型版本/权重 Hash、硬件、参数、耗时/质量测量和结论适用范围。

验证证据提交到本仓库对应 `verification/` 路径并由 Handoff 引用；Agent 会话、仓库外临时路径或未提交的本机状态不能作为唯一证据。安装或构建日志支撑交付结论时一并入库；Secret 只记录脱敏结果。

Handoff 在交付 head 之后以文档提交追加，引用之前的实现 head；避免要求文件包含自己的 commit hash。修订生产内容必须生成新的 handoff/head，并重新审查。

## 6. 独立 Review 与集成

使用 [Review 模板](templates/REVIEW.md)。Review 必须固定 base_commit 与 reviewed_head；分支随后变化不延用旧批准。

1. Reviewer 在独立工作区读完整 diff、受影响调用链、需求和测试，不只看作者摘要。
2. Spec 轴：AC、写回范围、命令语义、数据保护、失败/暂停/恢复、UI 行为是否符合来源。
3. Architecture 轴：分层、共享契约、依赖、安全、持久化、可选 AI 依赖边界。
4. Verification 轴：运行相关检查；逐项写 PASS/FAIL/BLOCKED/NOT_RUN。没有运行环境时不能批准未核实的关键路径。
5. Findings 写明严重级别、文件/行、触发条件、影响、复现和建议。记录 findings_disposition；P0/P1 未解决不能批准。无发现也记录审查覆盖和未覆盖风险。
6. Codex 核对 Review 与当前 head，检查 Task 路径范围及依赖基线，串行集成。默认保留来源分支的 merge 提交；必要时 cherry-pick 需记录 old→new commit 对应关系。
7. 基线变化或合并冲突影响行为时，重新跑受影响测试并触发复审。即使无冲突，仍执行该切片的集成检查。
8. 集成后更新 Task、STATUS、派生图及验收证据；测试结果只能适用于记录的 commit。分支/worktree 不自动删除，先确认无未交付内容。

仅元数据归档提交无需重跑产品测试；生产代码/契约/测试变化不能用此规则免检。Git hooks 和远端保护当前都不存在，本协议是人工/Agent 协作约束，不是已安装的强制机制。

## 7. 发布与阶段审核

接管通过、契约冻结、切片通过、最终发布是不同 Gate。Mock Pipeline 通过只能证明编排和保存链路，不能证明 OCR/翻译/修复质量。

发布按 D08 执行：P0/P1 和干净 Windows 验证等要求不因 Roadmap 分阶段而降低。范围删减、阈值豁免先形成用户可审查的文档决定，不能把未完成标成 N/A。当前未授权提交远端、创建外部项目或向其他人发送消息。
