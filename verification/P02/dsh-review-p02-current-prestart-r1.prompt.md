# DSH independent review: P02 current prestart delivery

Role: independent, read-only Reviewer. You did not author this delivery. Review the exact current commit at the top of this detached checkout; first report the full output of git rev-parse HEAD and git rev-parse HEAD^{tree}. Expected base is 4183e7f7cf366c27aa8ad8a0bc7300af48783470. Stop and report BLOCKED if the checkout head/tree cannot be determined or the diff is not the intended P02 documentation/evidence slice.

Read the repository instructions and source of truth: AGENTS.md, doc/REBASELINE_PLAN.md, doc/STATUS.md, doc/00_INDEX.md, doc/09_COLLABORATION.md, doc/tasks/P02.md, and verification/P02/codex-checkpoint-p02-smoke-prestart-current-r1.md. Review the complete diff from the expected base through HEAD, including the route-validator and diff-check evidence committed in this review package.

Review whether the records are accurate and internally consistent; links resolve; old 04:11 Stage-1 16/16 is clearly historical and not treated as current; HostFolder recheck counts and evidence agree; clone/source/EOL/hardlink/output-capability and current Sky/WSB statements are supported by the saved artifacts; and no status says Smoke, product acceptance, Build Gate, or Hard Build Barrier passed without evidence. Confirm the one-attempt limit and the required post-review immediate checks remain explicit.

Do not modify files. Do not access, scan, list, or hash HostFolder contents. Do not run wsb start, any Sandbox/guest command, Build, GUI, or product tests. This review is limited to the submitted governance/checkpoint/evidence slice and exact-head diff. Do not expand scope or propose product decisions.

Return:
- Decision: APPROVED, CHANGES_REQUESTED, or BLOCKED.
- Exact HEAD and tree; expected base; command exit codes for your read-only diff/scope checks.
- P0/P1/P2/P3 finding counts and open count.
- Each finding with ID, severity, file and line, trigger/impact, and minimal correction. If none, say 0/0/0/0 and open=0.
- Review coverage and anything NOT_RUN/BLOCKED/UNKNOWN.
- Explicit confirmation that no Sandbox, HostFolder scan/hash, Build, GUI, or product test was run.
