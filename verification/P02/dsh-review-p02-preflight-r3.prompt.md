# P02 非提权宿主 Preflight R3 exact-head Review

你是 DeepSeek Harness，本轮担任 P02 Codex-only scratch-build isolation follow-up 的独立非作者 Reviewer。只读审查，不修改、暂存、提交、删除任何文件。禁止 Windows Feature 查询/变更、提权、`wsb`、Sandbox、clone、Smoke、Build、产品 runner/test、GUI 或 WebView。

## 固定审查对象

- Repository: `G:/CODEX/New Manga`
- Reviewer checkout / cwd: `C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga`
- Exact target HEAD=`c36435aec5042143b816c01aa6da2ff3e80ba154`
- Exact target tree=`cba4d7f25bf8d68827b41449d0cfbde62539fd7f`
- Target parent=`9a96b5ae0695f56da9f19bfaf0771adda7999ea7`
- Task base / live main=`6855c113e6a44320d9555777900cfb78a218d383`
- R3 repair content commit=`6f47d4812e269a7c4c6192f302842b902e5f5ae4`
- R3 start checkpoint=`ed0fb8a28484e547da953cf2b68ec32d21a320b8`
- R2 exact-head reviewed candidate=`7d8951c28cd954d7e325cd53e7991f3bec87d971`
- Owner/author=Codex; independent Reviewer=DeepSeek Harness; Integrator=Codex. Parent Task P02 remains `in_progress / ACTIVE`.

First verify your own checkout HEAD/tree/parent and cleanliness exactly. Review `6855c113..c36435ae` and the frozen scope/evidence listed below. Do not infer from earlier review summaries; check the files and changed paths.

## Prior decisions and repair scope

R1 DSH Review on `561f4105171b99910d739698380787f35203d3f2`: `APPROVED_WITH_CONDITIONS`, P0/P1/P2/P3=`0/0/1/5`. R2 exact-head Review on `7d8951c28cd954d7e325cd53e7991f3bec87d971`: `APPROVED`, P0/P1/P2/P3=`0/0/0/3`; R1 P2-01/P3-01..P3-05 were explicitly closed. Full record: `verification/P02/dsh-review-p02-preflight-r2.response.md`.

R2 findings N-01..N-03 were nonblocking documentation/evidence issues. The narrow repair was frozen in scope-delta r8 before implementation (see `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md` § r8):
- N-01: distinguish original R1 frozen scope ∪ r7 from r7 alone; list the six unchanged inherited R1 files; anchor `24 paths` at `80cf5651` and `26 paths` at reviewed `7d8951c2`.
- N-02: record exact-head `7d8951c2` validator/link/diff replay and final candidate validation.
- N-03: preserve the original scope-freeze time but label the later completion sentence as a retrospective delivery-time note.

## Review questions

1. Are N-01, N-02 and N-03 fully and accurately closed in the validation record, R2/R3 checkpoints, start checkpoint, delivery checkpoint, scope-delta, P02 current record, Plan, Status and Index?
2. Independently verify the six carry-forward paths and the scoped path counts. R1 freeze lists the original preflight evidence paths at `codex-checkpoint-p02-preflight-scope-frozen.md:6`; r7 is in scope-delta; r8 freezes this R3 repair. Check the diff against the union and report any path outside it.
3. Review all 35 base-relative changed paths at this exact HEAD. Confirm the change is documentation/evidence only: no product source, test, contract, IPC, Schema, dependency, user data, Owner allowlist, AC, or dependency-state edits.
4. Independently replay route validator, `git diff --check`, focused Markdown link comparison, exact HEAD/tree/parent, root protected manifest, and candidate/root path intersection. The author recorded at `9a96b5ae`: route EXIT=0 (196 nodes), diff check EXIT=0, 19 Markdown files / 772 relative targets / 10 already missing in base / 0 new missing, root 203/203 with zero overlap. The current exact target adds the R3 delivery checkpoint; report fresh exact-target values.
5. Check timestamps, links, counts, status accuracy, and claims. No `PASS` may imply Windows Feature/Smoke/Build/AC success. Confirm product tests, Smoke, Build, Feature query, Sandbox and GUI were not run.
6. Explicitly state whether N-01..N-03 are closed and whether this documentation/evidence repair may be integrated.

## Required output

Return a concise formal report with decision (`APPROVED`, `APPROVED_WITH_CONDITIONS`, `CHANGES_REQUESTED`, `NOT_VERIFIED`, or `BLOCKED_BY_MISSING_EVIDENCE`), exact reviewed HEAD/tree/base and checkout cleanliness, P0/P1/P2/P3 counts, each finding ID/severity/path/line/impact/required closure, explicit N-01/N-02/N-03 dispositions, and integration recommendation.

This review only covers documentation/evidence. Preserve these gate states: Windows Sandbox Feature=`UNKNOWN`; full preflight=`BLOCKED / INCOMPLETE`; Smoke admission=`NOT_ADMITTED`; Smoke=`NOT_AUTHORIZED / NOT_RUN`; Build Gate=`BLOCKED`; build=`NOT_AUTHORIZED / NOT_RUN`; P02 AC1–AC7=`BLOCKED / NOT_RUN`; Hard Build Barrier remains effective. Do not run the prohibited operations above.