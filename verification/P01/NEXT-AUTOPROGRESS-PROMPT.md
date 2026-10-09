请从 `G:/CODEX/New Manga` 自动推进已授权的项目路线图，默认使用简体中文；持续到全部已授权工作完成，或遇到必须由我决定的产品问题/外部不可逆操作。聊天内容只作意图背景，项目事实以当前仓库的文档、Git 和实际验证为准。

## 恢复步骤

1. 阅读仓库 `AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、当前 Task 与其 `verification/<Task>/RESUME.md`。
2. 核对 root 与对应 worktree 的 branch、HEAD、dirty/staged、登记状态和 common-dir。若与恢复点不符，先记录漂移并按协作规则保护人工/Agent改动；不得 reset、clean、覆盖、stage 或 stash 未授权内容。
3. 本恢复点的详细证据与可执行步骤见 [P01 RESUME](RESUME.md)。此处不假设 P01 当前是 pending、done 或其他状态；按 Live Git 和权威 STATUS 选择对应下一步，已完成的审计不得重复。
4. 每项 Task 都要满足验收条件、真实测试证据、不同于 Owner 的独立 Review 与 Codex Integration Gate 后，才可记为 `done`；更新 Task、Plan、Status、依赖图与恢复点，再从权威路线图释放满足条件的下一 Task 并继续。
5. 按项目规则使用合适 Agent/Skill 并跟踪真实交付。Qoder 已退出，绝不分配；Owner 不得审核自己的实现。共享接口、Schema、依赖或协作规则仅按已冻结 Task 修改。不得伪造交付、测试、Review、PASS 或 DONE。
6. 不因已确认决策、常规实现细节或任务分配再次询问我；遇到真正未决产品取舍时，继续独立工作并一次性列明问题与影响，暂停依赖该决定的工作。
7. 保护用户文件、人工修改、Lock、current/pinned Revision、密钥及其他 Agent 的未提交内容。不 push、不发布、不部署、不删除、不影响项目外部状态，除非用户另行明确授权。
8. 只有在 P01 按本轮指示完成并且续跑提示已安全保存后，才执行本轮授权的关机。此关机授权仅限本轮 P01 收口；重启后的自动推进不得据此在后续 Task 完成时再次关机。

## 当前恢复信息

- Task 与精确步骤：`verification/P01/RESUME.md`。
- P01 worktree：`G:/CODEX/New Manga.worktrees/P01-metadata-audit-codex`；分支：`agent/codex/P01-metadata-audit`；base：`826bea12a132c5af2ac0cd1244d00e9170093c71`。
- P01 checkpoint 可能随本轮继续推进；每次恢复以 `git rev-parse HEAD`、`git status --short --branch` 与 RESUME 最新检查点为准，不依赖此提示词中的历史 SHA。
- root `main` 既有 dirty/untracked 是用户与其他 Agent 的内容，当前检查清单见 `verification/P01/ac1-root-status.log`；未经明确授权，不要改动、暂存、stash 或清理。

开始后直接执行可安全进行的下一步，不要只返回计划或要求我再次说“下一步”。
