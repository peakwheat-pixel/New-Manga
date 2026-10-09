# Checkpoint：P02 process isolation r6 start，N-04/N-05 修订范围已冻结

- 时间：2026-10-09 15:31 UTC（2026-10-09 23:31 Asia/Shanghai）。状态边界：R6_SCOPE_FROZEN / IMPLEMENTATION_STARTED。
- Parent Task=P02 Hard Build Barrier（唯一 Active Task）；Codex-only process-isolation 子任务。Owner/author=Codex，非作者 Reviewer=DeepSeek Harness，Integrator=Codex；PROJECT_ORCHESTRATION_AUTHORIZATION 持续有效。
- Base=`1c7efb172b8e9d766e38f84cf3728a90bb5953d0`，tree=`f50f9716a87ffe7a6272370a92b0eeb862e75079`，branch=`codex/P02-process-isolation`，author worktree=`C:\Users\49745\.codex\worktrees\p02-process-isolation-plan\New Manga`，common Git directory=`G:/CODEX/New Manga/.git`。r5 DSH exact-head result=`APPROVED_WITH_CONDITIONS`（P0/P1/P2/P3=0/0/0/2）。
- 当前 author workspace 有 8 条未提交 R5 Review artifacts/checkpoints；r5 candidate commit 本身未变更。DSH reviewer checkout=`C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r5`，detached at exact candidate，clean。
- 冻结 R6 允许路径与变更：
  1. `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md`：仅修改 r5 extension 中 N-04 所指的 :66 许可语句，使其明确授权 :52 的一行就地扩写且不改其他行；仅移除 N-05 所指文件末尾字面 `` `n `` 并补一个 UTF-8 LF；随后追加本 R6 extension，记录上述精确范围与附件许可。
  2. `verification/P02/**`：新增 r5 DSH dispatch/response/session/mount 等正式审查附件、r5-review checkpoint、r6 start/delivery/review checkpoints、r6 validation，以及 DSH r6 prompt/dispatch/response/exit/session/mount/stderr 附件。`dsh-review-process-isolation-r5.prompt.md` 已存在于 r5 commit。
- 不允许改 `doc/tasks/P02.md`、Build plan、host inventory、STATUS、REBASELINE_PLAN、P02 Owner allowlist、产品实现/测试、Schema/IPC/依赖、r3 WSB XML/canonical hash、root/其他作者 dirty files 或用户数据。
- 验收：N-04 的许可措辞准确覆盖单行 :52 就地变更；N-05 末尾不含字面 `` `n `` 且文件以 LF 结束；其余授权段落字节语义不变；r3 XML 保持 2609 bytes / SHA-256=`9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`；`git diff --check` 和路线 validator 通过；固定候选并由 DSH exact-head 非作者复审。
- Gate 保持：Feature=`UNKNOWN`；Smoke admission=`NOT_ADMITTED`；Smoke=`NOT_AUTHORIZED / NOT_RUN`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；P02 AC1–AC7=`BLOCKED / NOT_RUN`；Hard Build Barrier 有效。
- 下一条准确动作：按冻结范围仅修订 scope delta 的一行许可和文件尾字节/换行，追加 R6 extension；将 r5 Review response/dispatch/checkpoints 一并纳入本次候选审查证据；验证后固定提交并派发 DSH exact-head R6 review。
