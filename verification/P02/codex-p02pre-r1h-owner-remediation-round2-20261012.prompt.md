P02PRE-R1H Owner remediation follow-up: R1H-005 / R1H-006

Owner: /root/p02_r1h_codex_owner. You authored the prior candidate. Do not Review your work. Integrator is /root; Reviewer will be a separate agent after your delivery.

Frozen task and source:
- Repository: G:\CODEX\New Manga
- Frozen Task: doc/tasks/P02PRE-R1H.md
- Task SHA-256: F028AB523DB3D909BC85CFE5FBCD30B242C68E07691F5FD3EE099460DA87F5AB
- Prior review report: verification/P02/codex-subagent-p02pre-r1h-static-review-remediation-20261012.md
- Root adjudication: verification/P02/p02pre-r1h-remediation-review-adjudication-20261012.md
- Pin reconciliation addendum: verification/P02/codex-subagent-p02pre-r1h-static-review-remediation-pin-addendum-20261012.md
- Owner worktree: C:\Users\49745\.codex\worktrees\p02pre-r1h-codex
- Branch: agent/codex/P02PRE-R1H
- Prior delivery HEAD: 4a02811d6edf9ab423d299a36c51f103e62dd5f3
- Frozen Task base for complete candidate review: 946938bd0696dfddd01f87d61fe6723c63ecdc86

Adjudicated findings:
1. R1H-005 / P2: selfcheck currently rejects every InvokeMemberExpressionAst in Get-LinkTypeEvidence and Set-RepositoryStop. The actual candidate has the pure in-memory calls [string]::IsNullOrEmpty and [Math]::Max, so static structure predicts that the existing candidate will be rejected by its own AST check. Do not characterize this as an executed test failure. Make the smallest exact AST allowlist for the known safe receiver/method/argument shapes while rejecting unrelated/dynamic/external calls. Add a legal helper positive case and injected external-call negative cases.
2. R1H-006 / P2: current AST inspection does not constrain all statements in the real candidate component loop before/after the skip nor the gap through outer continue. A Get-Acl -LiteralPath $full inserted after the loop body and before continue can escape current checks. Current copied pure-function negative cases do not prove candidate control-flow regressions are rejected. Bind analysis to the real AST and direct blocks; cover skip pre/post operations, state, break/continue, and add in-memory source/AST mutations proving that injected hash/ACL/enumeration/target reads, state changes, or removal/bypass of break/continue are rejected.
3. Prior findings R1H-001/002/003 were adjudicated FIXED_BY_FAIL_STOP_STATIC / FIXED_STATIC / FIXED_STATIC. Preserve these behaviors. In particular, do not invent frozen main/scratch status/index hashes or replace unavailable frozen values with live reads; missing baseline must continue to stop as UNPROVABLE before repository queries/inventory.

Allowed code writes: only the existing Task's three candidate files:
- verification/P02/p02pre-r1h-capture.ps1
- verification/P02/p02pre-r1h-selfcheck.ps1
- verification/P02/p02pre-r1h-handoff-20261012.md
Prefer the smallest fix in selfcheck; update handoff only if its status/limitations need to reflect the correction. No changes to Task, manifest, Plan/STATUS/index, prior reports/adjudication/pins, R1G evidence, or other paths. No new dependency or product scope.

Checks and delivery:
- You may run only git diff --check before independent Review.
- Do not run PowerShell parser, self-check, preflight, capture, getters, any API, tests, Build/Cargo, AC1–AC7, OS dynamic validation, or Sandbox.
- Commit the bounded candidate changes on the same branch, then report exact new HEAD/tree, parent/base, changed paths/stat, controlled status, diff-check exit, per-file byte/hash pins, commands run, and any limitations. Do not integrate or claim Review/Gate/AC PASS.
- The next non-author Reviewer will inspect the complete diff from frozen Task base 946938bd0696dfddd01f87d61fe6723c63ecdc86 to your new HEAD. If a finding cannot be closed safely within scope, preserve fail-stop and report it.