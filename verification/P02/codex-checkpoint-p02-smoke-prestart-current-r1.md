# Checkpoint: P02 current prestart checklist

- Timestamp / Agent / Task: 2026-10-10 06:56 +08:00 / Codex / P02.
- TaskStatus / ExecutionState: in_progress / ACTIVE.
- Boundary: PRESTART_CHECKLIST_PASS / INDEPENDENT_REVIEW_PENDING / NO_SANDBOX_START.
- Owner / non-author Reviewer / Integrator: Codex / DeepSeek Harness / Codex.
- Branch / worktree: codex/P02-process-isolation / C:\Users\49745\.codex\worktrees\p02-process-isolation-plan\New Manga.
- Start/base HEAD / tree: 4183e7f7cf366c27aa8ad8a0bc7300af48783470 / 6cc9c13a1da760bb60a4cbc369e7b8d90128b4da; main 与 candidate 在本切片开始时同一 HEAD。候选共用 Git common dir=G:\CODEX\New Manga\.git。
- Working tree: 主 checkout main 有 203 项既存 dirty/untracked（4 tracked、199 untracked），冻结 manifest digest=3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2；candidate 在 checkpoint 创建时共 129 个 status 路径：4 个 tracked modified、125 个 untracked、staged=0、added=0、deleted=0（含本 checkpoint 文件）。本提交只选择本切片显式列出的文件；不覆盖、清理、暂存或改动主 checkout 的既存内容。
- Scope / allowed paths: 仅 doc/00_INDEX.md、doc/REBASELINE_PLAN.md、doc/STATUS.md、doc/tasks/P02.md 与 verification/P02/** 中本切片证据；不改产品源码、依赖、共享接口/Schema，不写 HostFolder，不启动 Sandbox，不运行 Build/产品测试。

## 已完成步骤与证据

1. R2 HostFolder compare/recheck 在 candidate 固定 HEAD=4183e7f7cf366c27aa8ad8a0bc7300af48783470 / tree=6cc9c13a1da760bb60a4cbc369e7b8d90128b4da 完成：11/11 mappings PASS、mismatch=0、EXIT=0；artifact validator PASS。共 204,419 records、50,356 full hashes、33 samples、138,947 content-not-computed。命令和日志 Hash 见 [HostFolder recheck delivery checkpoint](codex-checkpoint-p02-smoke-prestart-hostfolder-recheck-delivery-r1.md)；原 stdout 保留在 r9f-current-prestart-host-recheck-r2.stdout.log，未在 checkpoint 展开固定 HostFolder 路径。
2. Clone 后 filesystem/input/source 检查通过：12/12 mapped roots present、root-level reparse=0、20/20 input hashes、14/14 registered sizes；3 个 source blob 与 clone CRLF EOL pins匹配；clone HEAD=7ce3c40cd308e7093929bd5f53abc4f8a6c4ef7a、private Git common dir、无 remotes/alternates、clean porcelain。见 r9f-current-prestart-filesystem-r2.json。
3. Git object hardlink 检查 3/3 link_count=1、failures=0；见 r9f-current-prestart-hardlinks-r1.json 及配套 .exit。
4. Host/WSB/toolchain 与资源阈值检查通过；Windows Sandbox feature InstallState=1，wsb --version / wsb list --raw EXIT=0，当前环境列表为空。进程为 PowerShell 7.6.6、interactive、非 elevated；资源阈值全通过。见 r9f-current-host-prestart-r3.json、r9f-current-token-integrity-r1.json 及配套 exit files。
5. @oai/sky read-only inventory：app_count=40、window_count=4、Windows Sandbox app/window count=0；不持久化其它应用名称或窗口标题。见 r9f-current-sky-enumeration-r2.json。
6. Synthetic output-capability probe 在 scratch clone 的 canary 目录执行独占写入、读回和删除，三步 PASS，目录恢复为空；未访问产品源文件或 HostFolder。见 r9f-current-prestart-output-capability-r1.json。
7. Root protection 在 fast-forward 前复核为 203/203 MATCH，missing/extra/mismatch/staged=0，digest 与冻结基线一致；candidate touched paths 与 root dirty paths overlap=0。见 r9f-host-recheck-root-manifest-pre-ff-r2.json。
8. Route validator 在本切片 commit 前于固定 HEAD 执行 7/7 PASS、EXIT=0；见 r9f-host-recheck-route-validator-r1.stdout.log 与 .exit。Delivery commit 后仍需精确复跑 route validator 与 git diff HEAD^ HEAD --check。

## 历史值、未完成 Gate 与风险

- 2026-10-10 04:11 的 Stage-1 16/16 发生在固定 clone 创建之前，明确属于历史观测；本 checkpoint 不将它记作当前 PASS。当前使用 clone 后 filesystem/source/integrity 报告。
- P02 R9F exact-head Review=APPROVED 并已集成；本轮新文档/证据的 DSH exact-head Review=PENDING。
- Smoke admission=ADMITTED，仅一次；wsb start=NOT_RUN，Smoke=NOT_RUN；完整产品 preflight 尚未结束，AC1–AC7=BLOCKED / NOT_RUN。
- Build Gate=BLOCKED；build=NOT_AUTHORIZED / NOT_RUN；hook/cache closure=BLOCKED / NOT_VERIFIED；Hard Build Barrier=EFFECTIVE。不得因本次 HostFolder/prestart 检查通过而解除。
- Known portability observation: candidate pinned XML 为 canonical LF（2609 bytes）；主 checkout core.autocrlf=true 可能落盘 CRLF。Smoke 继续从 candidate canonical-LF worktree 验证，不改变 checker 或 Git 属性。

## 下一准确动作

1. 对本切片明确文件建立 delivery commit，随后按提交后的 exact HEAD/tree 复跑 route validator 与 diff-check，并将 exact-head Review prompt 固定到该候选。
2. 从隔离的 C: detached review worktree 派发 DSH 只读 Review；禁止 DSH 启动 Sandbox、运行 Build/产品测试、扫描或哈希 HostFolder 内容。记录 stdout、EXIT 与 session ID；不得把 NOT_RUN/BLOCKED 改写为 PASS。
3. 只有 Review 批准后，立即重新读取 WSB 环境列表、@oai/sky app/window inventory、r3 XML canonical bytes/hash、clone/source/EOL pins、root protection 与宿主身份/资源。任一项 UNKNOWN/FAIL 则记录 Blocker，禁止启动。
4. 若上述即时复核全部 PASS，最多尝试一次 wsb start --config <same canonical LF formatted XML string>；成功后先绑定唯一 Sandbox window 并保存 screenshot，再执行任何 guest command。若 start/binding/capture 失败，停止已有 session（如有）并保留现场，绝不重试。

- Tests already run: 本 checkpoint 列示的只读验证与 synthetic scratch output probe；产品 Build、Vitest、GUI、guest commands 均未运行。
- Tests remaining: exact-head docs Review；Review 后即时 prestart 复核；至多一次 Smoke attempt 及其隔离证据；独立 Review 与 integration gate。
- Blockers / decisions: Review pending；Hard Build Barrier 与 hook/cache blocker 持续有效；不涉及产品范围裁决。
- Evidence / confidence / resume safety: 证据以 linked worktree 内的 JSON、stdout、EXIT 与 source files 为准；candidate/main 起始 HEAD 一致且 root dirty manifest 未与候选路径重叠。RESUME_SAFE，恢复时先核验 exact HEAD、branch、worktree 与 manifest digest。
