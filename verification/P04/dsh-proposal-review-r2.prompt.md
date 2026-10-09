请在当前已存在的 DSH 会话中，对 P04 提案修订做第二轮只读审查。

固定候选：branch codex/P04-scope-freeze，reviewed head af67d5019fa3fb83ed2c1765dd2548cdba743a80，base 88579622d85ff6d0dfd509c6f21931bd91d0881b。该 head 已由 Codex 提交并通过路线 validator。
请读取当前 doc/tasks/P04.md、doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/00_INDEX.md、verification/P04/proposal-amendment-checkpoint-20261010.md、verification/P04/proposal-review-checkpoint-018023e8.md，以及第一轮报告 verification/P04/dsh-proposal-review.stdout.md；必要时读 build.rs、P02 scratch build plan 和 STATUS 证据。

逐项确认第一轮 finding 是否关闭：P1-1 sidecar bundle/source provenance + build gate；P2-1 AC1 字面精确断言；P2-2 AC2 FAIL/blocked/follow-up 修复流程无循环；P2-3 checkpoint 与恢复指针；P3-1 M2-AC1 术语；P3-2 protocol 旁录证据及 PROPOSAL 限制；P3-3 stderr/availability 临时工件是否未签入；P3-4 显式 `--bin m2rc1-desktop`；P3-5 `#[cfg(test)]` 限定；P3-6 机器可读 `blocked_by`。

审查 Task 是否仍保持 proposed，依赖与允许修改范围是否准确，Plan/STATUS/Index/Checkpoint 是否一致，sidecar 与 `CARGO_TARGET_DIR` 是否只在 P02 批准隔离环境使用，以及 P04 是否仍被正确阻止释放。

请不要修改文件，不要运行 Cargo/Tauri build/test、Sandbox、Windows Sandbox Feature 查询/启用、scratch clone 或创建/派发 Task。只做固定 head 的静态审查。

返回中文 Markdown：verdict（approve / changes requested / blocked）；逐条 finding（若有，severity、路径行号、影响、最小修改）；给出 unresolved P0/P1/P2/P3 数量。全清时写 `unresolved P0/P1/P2/P3 = 0/0/0/0`，并注明这仅批准 proposed Task 契约，不是 P04 实现 Review、Build Gate 或产品验收。