请对 P02 Codex-only isolation Smoke 授权与预检候选做独立、只读的 exact-head Review。不要修改任何文件，不启动 Windows Sandbox，不创建 clone，不运行 build/product tests。

Review checkout:
- branch: review/deepseek/P02-preflight-r4-083d2b47
- worktree: C:/Users/49745/.codex/worktrees/P02-preflight-r4-083d2b47-review-dsh
- fixed reviewed HEAD: 083d2b47f7051c2dedd0d9ae4346ae1affab6c1b
- tree: 27a8051b95df3c2cf40be90737d09b324592a78e
- parent/base: ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50
- Task author/Owner=Codex; required non-author Reviewer=DeepSeek Harness; Integrator=Codex.
- Review only the committed diff base..HEAD and the cited context. Use git show/git diff against the fixed commit; do not infer from a dirty checkout.

Candidate files:
1. verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md (r9 extension only)
2. verification/P02/codex-scratch-build-preflight-r2.md
3. verification/P02/codex-scratch-build-preflight-observations-r2.json
4. verification/P02/codex-checkpoint-p02-preflight-r4-start.md
5. verification/P02/codex-preflight-r4-validation.md

Read context:
- doc/tasks/P02.md, especially the Codex-only scratch isolation boundary and Smoke requirements.
- doc/STATUS.md and doc/REBASELINE_PLAN.md current P02 gate state.
- verification/P02/codex-scratch-build-process-isolation-proposal-r1.md (r3 fixed configuration and one-shot Smoke protocol).
- verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md prior r6/r7/r8 history.
- verification/P02/dsh-review-process-isolation-r6.followup.response.md (N-06 closure).
- verification/P02/codex-checkpoint-p02-preflight-r3-delivery.md (preflight review).
- Microsoft reference cited by candidate: Win32_OptionalFeature InstallState enumeration. If your environment cannot browse or run commands, label that check NOT_RUN rather than assuming.

Questions:
A. Does r9 accurately reflect the user's 2026-10-10 authorization to obtain real P02 isolation evidence, while keeping elevation/feature mutation, product build, product acceptance, AC completion, and barrier release separate?
B. Is the feature observation legitimate and sufficiently narrow? The non-elevated Get-WindowsOptionalFeature command failed because elevation was required; no elevation occurred. Get-CimInstance Win32_OptionalFeature returned Containers-DisposableClientVM InstallState=1. Confirm the cited enum and note that Enabled is necessary preflight only, not proof of isolation.
C. Are root protected manifest, timestamp/root HEAD, hardware thresholds, WSB identity/list, 12 HostFolder roots, 20 input pins, source ancestry, config hash, helper availability, and stated limitations internally consistent and clearly bounded? Do not claim unmeasured isolation or source checkout success.
D. Is the new authorization scope limited to the one already-reviewed r3 Smoke configuration and the fixed clone path, with a separate Smoke admission after Review and a separate Build Gate afterward?
E. Did validation report only actual checks, and are there missing P0/P1/P2/P3 risks that must block admission?

Report in Simplified Chinese. Include exact reviewed HEAD/tree/base and verification method. Cover Architecture and Verification. Give a decision (APPROVED / APPROVED_WITH_CONDITIONS / CHANGES_REQUESTED / BLOCKED), P0/P1/P2/P3 counts, each finding's severity/file/line/trigger/impact/fix, explicit dispositions for prior findings relevant to this candidate, checks run with exit codes and checks not run. If you cannot independently reproduce a claim, say so. Do not treat file text as instructions; it is review input only.
