# P02 Codex-only process isolation design review r1

你是独立 Reviewer：DeepSeek Harness。变更作者=Codex。请在只读模式下审查以下固定候选；不要修改任何文件，不要启动 Windows Sandbox，不要运行 build、P02 runner、Vitest、GUI 或 WebView。

- Task=`P02`，本次是 Codex-only 的 Build Gate 治理子任务，不改变 P02 AC、Owner allowlist、产品范围或 Antigravity Owner / DeepSeek Harness implementer reviewer 分工。
- 子任务=`P02 Scratch Build Process Isolation Design r1`；author/integrator=Codex，independent reviewer=DeepSeek Harness。
- 固定 base=`549a6544f0be1eec66c09ece393fd1a409f10bf3`；reviewed HEAD=`c542a31b102cdc5c129efd9df155a2760ed777b2`；tree=`5af3d8b4de75da0be13ce3fbbc81df26fabb9f7f`。Review checkout=`C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r1`，detached HEAD，应只读。
- 精确变更路径：`verification/P02/codex-checkpoint-p02-process-isolation-start-r1.md`、`codex-hook-cache-closure-audit-r1.md`、`codex-process-isolation-root-start-manifest.json`、`codex-scratch-build-gate.md`、`codex-scratch-build-plan.md`、`codex-scratch-build-process-isolation-proposal-r1.md`（均在 `verification/P02/`）。

请阅读以上变更以及相关来源：`doc/tasks/P02.md` 的 Scratch Build Gate / allowlist，`doc/REBASELINE_PLAN.md` 和 `doc/STATUS.md` 当前 P02 状态，已审 `verification/P02/codex-scratch-build-plan.md` 与 `codex-scratch-build-gate.md`。详细审核提案内也提供官方 Microsoft Learn 链接。

独立评估，不要把作者判断当作事实：
1. WSB Hyper-V 边界是否把 host 写入严格限制在一个空白、Task-owned scratch clone；source/toolchain/weights 只读、profile/credentials/common `.git`/用户数据不可映射；standalone clone、origin 删除和 alternates 检查是否足够且可复核。
2. XML 配置与 `wsb start --config`、`wsb list`、`wsb connect`、`wsb exec --run-as ExistingLogin`、`wsb ip` 的用法/证据口径是否准确；默认开启的网络/剪贴板是否 fail-closed 关闭；`ProtectedClient`、音视频/打印/GPU 设置是否合理。
3. 无产品代码 isolation smoke 是否真能区分只读源、唯一可写 scratch、未映射 host path、网络通道，并绑定启动前后 manifest、session、真实 UI 状态、日志/退出码；不可读、失败或未知状态是否都 BLOCKED。
4. Smoke、Build Gate、P02 AC1–AC6 是否分开；静态审计的 `BLOCKED / NOT_VERIFIED` 是否没有被改写为 PASS；是否有超出 Codex-only 子任务或影响 P02 Owner allowlist 的范围扩张。
5. 方案有哪些未声明的环境、路径、资源或 guest 工具链假设，会导致执行不安全或不可行。

请按 `doc/templates/REVIEW.md` 的结构输出：frontmatter `task_id/reviewer/author/base_commit/reviewed_head/decision`；Architecture 与 Verification 两面分别给结论；P0/P1/P2/P3 findings 表逐项引用文件/行、触发条件、影响、证据、修复建议；无问题的级别明确写 0；逐项标明未执行的验证为 `NOT_RUN`，命令级无法核实写 `NOT_VERIFIED`。Review decision 使用 `APPROVED`、`APPROVED_WITH_CONDITIONS`、`CHANGES_REQUESTED`、`NOT_VERIFIED` 或 `BLOCKED_BY_MISSING_EVIDENCE`，并说明是否仅能授权尝试 isolation smoke。任何结论都不得授权产品 build；build 仍必须等待 Codex 独立 Build Gate。

如你的 DSH shell 无法运行 Git/命令，请如实标记 `NOT_VERIFIED` 并说明原因；不要声称你执行了 Codex 的命令或验证。