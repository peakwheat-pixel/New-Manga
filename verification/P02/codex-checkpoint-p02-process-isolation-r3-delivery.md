# Checkpoint：P02 process isolation r3 delivery 固定，等待 DSH exact-head Review

- 时间：2026-10-09 14:44:56 UTC（2026-10-09 22:44:56 Asia/Shanghai）。状态边界：R3_DELIVERED / REVIEW_DISPATCH_PENDING。
- Task=P02 Hard Build Barrier 的 Codex-only process-isolation 子任务；Owner/author=Codex，非作者 Reviewer=DeepSeek Harness，Integrator=Codex。P02 产品范围、AC、Owner allowlist、行为基线未改。
- 固定候选 branch=`codex/P02-process-isolation`，delivery HEAD=`92361e3578eedb93d7cf6c4c5a4db06652d31fe9`，tree=`919e10809390a7fa6c4cf7133ae36ac600a9b517`，parent/base=`3555213a748a7b407400589e1490a387353dec16`。`git show` 已复核 commit/tree/parent/subject；delivery commit 为 `docs(P02): revise process isolation smoke gate r3`。相对 r2 为 18 个路径，全在 `doc/tasks/P02.md` Codex-only boundary 与 `verification/P02/**`；无 Owner production allowlist 或 AC 差量。
- 作者 checkout=`C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga`。commit 固定时 worktree/index clean；当前新增的 DSH prompt 与本 checkpoint 是 review evidence 的 untracked 文件，不改候选 commit。基线分支与作者 checkout共用 `G:/CODEX/New Manga/.git`。
- 独立 DSH review checkout=`C:/Users/49745/.codex/worktrees/P02-process-isolation-review-dsh-r3`，detached exact HEAD=`92361e3578eedb93d7cf6c4c5a4db06652d31fe9`，worktree clean。作者 branch 与 review checkout 的差异被隔离。
- root=`G:/CODEX/New Manga`，仍为 `main@549a6544f0be1eec66c09ece393fd1a409f10bf3`。保护 manifest `verification/P02/codex-process-isolation-root-start-manifest.json` 与 live root 逐路径状态/文件大小/SHA-256 比对 `203/203 MATCH`，missing/extra/mismatch=0；canonical entries=36,985 UTF-8 bytes，SHA-256=`3a54fa978bf228bfae366a4c4de35b90e4fab609447d3370ed81370299da10e2`；状态统计=`4 × " M" + 199 × "??"`，staged=0。相对候选 18 个路径与 root dirty/untracked paths 交集=0；root 现场未写入。
- 已存在验证复核：路线/依赖校验 EXIT=0（196 unique nodes，无周期，P02状态/路线匹配）；`git diff --check` EXIT=0；r3 XML结构自检 EXIT=0（11 mappings，1 RW/10 RO，hash=`9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`，无 `LogonCommand`）；r2 canonical hash erratum 8/8 精确匹配。完整记录=`verification/P02/codex-process-isolation-r3-validation.md`。以上是文档/配置静态验证，不是产品或 Sandbox 运行证据。
- DSH r2 对 `3555213a...` 的方案 Review=`APPROVED`（0/0/0/10）；r3 针对固定 HEAD 的正式复审尚未执行。自包含 prompt=`verification/P02/dsh-review-process-isolation-r3.prompt.md`。
- 当前门状态：Windows Optional Feature=`UNKNOWN`；Smoke=`NOT_AUTHORIZED / NOT_RUN`；Build Gate=`BLOCKED`；build=`NOT_AUTHORIZED / NOT_RUN`；P02 AC1–AC6=`BLOCKED`；Hard Build Barrier 有效。尚未查询/更改 Windows Feature、提权、启动/连接 Sandbox，也未运行 build、产品 tests、runner、GUI 或 WebView。
- 下一条准确动作：按 `dsh-dispatch` skill 在上述 clean exact-head review checkout 执行 `dsh --profile headless --json -`，保存原始 JSONL 到 checkout 外，解析并归档 final response/exit/stderr/session/mount；随后依据 DSH 决定修订或进入集成评估。Review 通过仅表示方案设计审批，不授权 Smoke 或 Build。


## R3 delivery reconciliation after exact-head Review（R3-05 / C5）

- 本 checkpoint 于 r3 commit `92361e3578eedb93d7cf6c4c5a4db06652d31fe9` 交付后建立；该 commit parent=`3555213a748a7b407400589e1490a387353dec16`，tree=`919e10809390a7fa6c4cf7133ae36ac600a9b517`。其 `git diff --name-only <parent>..<delivery>` 精确为以下 18 条：
  1. `doc/tasks/P02.md`
  2. `verification/P02/codex-checkpoint-p02-process-isolation-r2-candidate.md`
  3. `verification/P02/codex-checkpoint-p02-process-isolation-r2-delivery.md`
  4. `verification/P02/codex-checkpoint-p02-process-isolation-r2-review.md`
  5. `verification/P02/codex-checkpoint-p02-process-isolation-r3-start.md`
  6. `verification/P02/codex-p02-wsb-smoke-config-r3.xml`
  7. `verification/P02/codex-process-isolation-r3-validation.md`
  8. `verification/P02/codex-scratch-build-gate.md`
  9. `verification/P02/codex-scratch-build-input-host-inventory-r2-build-addendum.md`
  10. `verification/P02/codex-scratch-build-plan.md`
  11. `verification/P02/codex-scratch-build-process-isolation-proposal-r1.md`
  12. `verification/P02/dsh-review-process-isolation-r2.dispatch.md`
  13. `verification/P02/dsh-review-process-isolation-r2.exit.txt`
  14. `verification/P02/dsh-review-process-isolation-r2.mount.txt`
  15. `verification/P02/dsh-review-process-isolation-r2.prompt.md`
  16. `verification/P02/dsh-review-process-isolation-r2.response.md`
  17. `verification/P02/dsh-review-process-isolation-r2.session.txt`
  18. `verification/P02/dsh-review-process-isolation-r2.stderr.txt`
- Scope basis: `codex-scratch-build-process-isolation-scope-delta-r1.md` § “r3/r4 scope extension”. It freezes the only cross-folder edit to the `Codex-only scratch-build output boundary` paragraph in `doc/tasks/P02.md`, plus this subtask's named artifacts under `verification/P02/**`; it excludes P02 Owner allowlist/AC, product code, shared contracts, root status/plan, root 203 dirty paths, other worktrees and user data.
- R3 config identity unchanged: `verification/P02/codex-p02-wsb-smoke-config-r3.xml`, canonical UTF-8/LF bytes=2609, SHA-256=`9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d` (11 mappings, 1 RW / 10 RO, no `LogonCommand`).
- DSH exact-head R3 Review completed with `APPROVED_WITH_CONDITIONS`, P0/P1/P2/P3=`0/0/2/4`; report/dispatch/session/mount/exit/stderr are linked in this evidence set. This outcome is design-only and is recorded in the separate `codex-checkpoint-p02-process-isolation-r3-review.md`; it does not authorize Smoke or Build.
- This reconciliation was added during r4 repair to make the delivered r3 artifact auditable; it does not alter the fixed r3 commit or claim that this file was present inside that commit.
