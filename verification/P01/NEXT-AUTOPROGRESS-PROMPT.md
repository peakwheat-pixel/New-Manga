请从 `G:/CODEX/New Manga` 自动推进项目路线图，默认使用简体中文；持续到所有已授权工作完成，或遇到必须由我决定的产品问题/外部不可逆操作。项目文档、Live Git与实际验证是事实来源，聊天记录仅提供意图背景。不要只给计划；对安全且已授权的工作直接执行并持续保存恢复点。

## 恢复入口与Reality Check

1. 阅读根目录 `AGENTS.md`、`doc/REBASELINE_PLAN.md`、`doc/00_INDEX.md`、`doc/STATUS.md`、`doc/09_COLLABORATION.md`、当前Task和对应 `verification/<Task>/RESUME.md`。再检查root与相关worktree的branch、HEAD、staged/unstaged/untracked、common-dir；核对恢复点中每个hash和状态。
2. P01历史交付、正式Review、Gate、fast-forward前后root manifest及本轮关机记录见 [P01 RESUME](RESUME.md)。若Live main显示P01=`done`，不要重做P01；若尚未`done`，按该RESUME最新一步继续，不能依据本提示的旧hash推测已集成。
3. 保护root工作区中已有用户/人工/其他Agent修改、Qoder历史文件、Lock、current/pinned Revision、密钥与所有未提交数据。不得 reset、clean、覆盖、stage或stash未授权内容；如Git快进因冲突或受保护数据漂移而拒绝，保留现场并记录证据。

## 自动推进规则

4. 从权威Plan选择依赖已满足的最早候选。P02「真UI行为、300ms刷新与对比度验证」仍需先由Codex基于Live main和真实React/Tauri入口冻结只读harness范围、实际WebView能力、逐项验收、允许/禁止路径及退出判据；创建正式Task与RESUME、更新Plan/Status并登记Owner和非作者Reviewer后，才可释放。P02当前建议Owner=ZCode，Reviewer=DeepSeek Harness；正式释放时重新核对Reviewer通路，若DSH确实不可用，按项目故障转移规则改用Antigravity并记下证据。不得分配Qoder。
5. 每项工作均核对AC、逐条测试/`NOT_RUN`与skip、独立Review、Codex Integration Gate和集成后验证；更新Task、Plan、Status、依赖图、Handoff、RESUME与下一自动推进提示。Task完成后直接选择并释放安全可执行的下一项，不因单个Task完成而停下来等待我。
6. 产品实现严格限定到当前Windows / React + TypeScript / Tauri / Python Core / SQLite / Managed Copy架构；UI任务先验证现有真实行为，不以JSDOM/mock冒充WebView。共享接口、Schema、依赖或协作规则须先登记范围；产品取舍未决时继续独立工作并一次性列明问题及影响，暂停仅依赖该决定的工作。
7. 依据仓库规则使用适用Skill与真实Agent通路；Owner和Reviewer必须不同。保存实际commit、测试输出/exit、Review载体、session和fingerprint；不得伪造派发、交付、Review、PASS或DONE。
8. 未经新的明确授权，不push、发布、部署、删除生产/用户数据，也不执行其他影响项目外部状态的操作。此前“P01完成后关机”是仅适用于上一会话的一次性要求，不能继承为本次或后续任务的关机授权；除非我再次明确要求，否则保持计算机运行。

恢复后直接执行可安全开展的下一步，不要要求我再次说“下一步”。
