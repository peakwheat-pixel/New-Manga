你是 New Manga 项目 P04 的 Owner Antigravity。请从当前 linked worktree 完成 P04 的测试代码实现，并在任务允许范围内提交固定 commit 与 Handoff。

仓库：G:\CODEX\New Manga
当前 worktree：G:\CODEX\New Manga.worktrees\P04-prod-command-concurrency-antigravity
当前 branch：agent/antigravity/P04-prod-command-concurrency
Task Contract：当前 worktree 中 doc/tasks/P04.md。请先读取此 Task 与 AGENTS.md、协作协议中适用于 Owner 的部分，并核对当前 HEAD 和工作区。
Task base：8a0685c9bf5aec7e7cc51f466f3fec7b176c35de。当前 branch 已包含随后 fast-forward 的治理文档提交与 Codex start checkpoint；保留这些提交，不要 reset/rebase/checkout 到其他分支。

本轮范围：
1. AC1：加入字面精确断言：
assert_eq!(PAGE_NAV_PRODUCTION_ONLY_COMMANDS, &["list_chapters", "list_chapter_pages"]);
同时验证该组仅位于 production surface，不出现在 probe 或 M2-AC1 surface。期望值必须字面固定，不能从被测常量推导。
2. AC2：实现同一 StdioLibraryChannel 实例上的确定性并发 round_trip 测试，至少两个可区分请求与响应。同步必须可复现，不用 sleeps 或概率性压力循环；记录当前协议字段只作为边界诊断，不改变合同语义。按 Task Contract 判断 sidecar/test seam 的最小实现。
3. 只触碰 apps/desktop/src-tauri/src/main.rs 测试代码、apps/desktop/src-tauri/src/library_bridge.rs 的 cfg(test) 范围、verification/P04/** 和 P04 Handoff。不得修改生产逻辑、接口、schema、依赖、其他 Task 或共享 Plan/Status/Index。

重要 Gate：P02 Build Gate 仍为 BLOCKED，build=NOT_AUTHORIZED / NOT_RUN，Hard Build Barrier=EFFECTIVE；用户要求屏障解除前必须有真实隔离证据。本机验收等效口径不证明 VM 隔离。当前 P04 仅授权静态测试代码实现；严禁运行 cargo、Tauri、sidecar build、Rust 测试、GUI 或产品验收。不要声称任何 AC 已通过。若某项实现依赖未获准的 P02 sidecar 环境，就只提交可安全完成的测试代码与清晰的 NOT_RUN/BLOCKED 说明。

返回前：
- 只在当前 branch/worktree 工作，保留已有 Codex checkpoint 与探测 artifacts。
- 确认 git status 和改动只落在允许路径；提交实现形成固定 commit。
- 写入 verification/P04/antigravity-owner-implementation-r1.handoff.md，说明 commit、变更路径、AC1/AC2实现、未运行项和下一 Gate。
- 不更新 P04 shared status docs；Codex 会在独立 Review 与后续集成阶段负责。

任务交付不等于完成；等待 DeepSeek Harness 非作者 Review。