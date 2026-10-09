# P02 非提权宿主 Preflight R2 exact-head Review

你是 DeepSeek Harness，本轮担任 P02 Codex-only scratch-build isolation follow-up 的独立非作者 Reviewer。只读审查，不修改、暂存、提交或删除任何文件，不运行 Windows Feature 查询/更改、提权、Sandbox、clone、Smoke、Build、产品 runner、测试、GUI 或 WebView。

## 固定对象

- Repository: G:/CODEX/New Manga
- Reviewer worktree / cwd: C:/Users/49745/.codex/worktrees/p02-process-isolation-plan/New Manga
- Review target HEAD: 7d8951c28cd954d7e325cd53e7991f3bec87d971
- Review target tree: 1340c5282e32361c117f0aeacb670d412fe568c9
- Target parent: b14c7d2750cc53f0ae4edae6f3f5435398edccc9
- Fixed content repair commit: 80cf56514e7b079fc18c71730558edd6913f80f3
- R2 scope-freeze commit: cd3e86d6f072888270d0179627fe4c39cce4829c
- Task base and live main at dispatch: 6855c113e6a44320d9555777900cfb78a218d383
- Author/Integrator: Codex. Independent Reviewer: DeepSeek Harness. Parent Task P02 remains in_progress / ACTIVE.

First verify your checkout HEAD/tree/parent and cleanliness against these fixed values. Review the diff from 6855c113e6a44320d9555777900cfb78a218d383, the r7 scope extension, the R1 report and this R2 delivery/validation evidence. Focus on the exact changed paths; do not scan unrelated history or product code unless a finding requires it.

## R1 decision and repair scope

Your R1 exact-head decision on 561f4105171b99910d739698380787f35203d3f2 was APPROVED_WITH_CONDITIONS, P0/P1/P2/P3=0/0/1/5. P2-01 required an auditable authorization basis for Codex's four current-status document edits. P3-01..P3-05 concerned predicted source pin wording, machine-readable host measurements/provenance, the 14-path count, frozen manifest HEAD semantics, and HostFolder mapping-domain/count semantics.

The R2 scope was frozen in verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md § r7 before the repair commit. It cites the user's persistent PROJECT_ORCHESTRATION_AUTHORIZATION and AGENTS.md Codex coordination/integration role, narrows permitted status-document edits to their current segments and P02's latest Codex-only Gate record, and preserves product scope, P02 AC, owner allowlist, and all blocked/not-run boundaries.

## Review questions

1. Does the r7 authorization record close P2-01 sufficiently for this exact repair, given the user authorization is recorded as an external task instruction and the repository role boundary in AGENTS.md?
2. Are P3-01..P3-05 addressed accurately and consistently across the report, TSV, JSON, delivery checkpoint, P02 current record, Plan, Status and Index?
   - Source commit pins must remain MATCH_PREDICTED / CHECKOUT_NOT_RUN, never imply an actual checkout PASS.
   - The observation JSON should identify non-elevation, exact CIM classes/properties and units, current-user AppX identity, executable size/version/hash and capture time; summary values should match it. Distinguish R1 and R2 time-sensitive readings.
   - The original preflight delivery candidate was 14 paths: 4 current-status document segments plus 10 verification files including its delivery checkpoint.
   - The manifest head 549a6544f0be1eec66c09ece393fd1a409f10bf3 is its frozen creation HEAD, while its 203 entries match live main at 6855c113e6a44320d9555777900cfb78a218d383.
   - The 12 HostFolder roots should resolve as 1 scratch RW + 9 Smoke RO + 2 Build-only RO; the r3 Smoke XML has 11 mappings because it includes a clone-local canary RO alias. Do not conflate roots and mappings.
3. Independently inspect the 26-path candidate diff against the frozen scope. Report any unauthorized path, product/contract/test change, or root dirty-path collision. The delivery record reports 203/203 root-manifest match, zero staged root entries, and zero overlap.
4. Check for false PASS, inconsistent timestamps/values, misleading state, unresolved Review conditions, or evidence claims stronger than the commands support.
5. Confirm the project route validator/diff/link/path evidence is recorded honestly. Do not claim product tests, Smoke, Build, Feature status, or AC acceptance were run.

## Required output

Return a formal concise report with:
- decision: APPROVED, APPROVED_WITH_CONDITIONS, CHANGES_REQUESTED, NOT_VERIFIED, or BLOCKED_BY_MISSING_EVIDENCE;
- exact reviewed HEAD/tree/base and whether the worktree was clean;
- P0/P1/P2/P3 counts;
- each finding's ID, severity, evidence path/line, impact, and required repair/closure;
- an explicit decision on R1 P2-01 and each P3-01..P3-05;
- whether this doc/evidence repair may be integrated.

This review only covers the documentation/evidence repair. Even if approved, Windows Sandbox Feature remains UNKNOWN; full preflight stays BLOCKED / INCOMPLETE; Smoke remains NOT_ADMITTED / NOT_AUTHORIZED / NOT_RUN; Build Gate remains BLOCKED; build remains NOT_AUTHORIZED / NOT_RUN; P02 AC1–AC7 remain BLOCKED / NOT_RUN; the Hard Build Barrier remains effective.