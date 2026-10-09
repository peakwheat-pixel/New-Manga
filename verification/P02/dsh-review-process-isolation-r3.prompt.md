# DSH exact-head design review: P02 process isolation r3

You are the independent, non-author reviewer for the Codex-only P02 process-isolation design update. Work read-only in this exact detached checkout.

- Base: `3555213a748a7b407400589e1490a387353dec16` (r2; DSH approved design-only with 10 P3 conditions).
- Candidate: `92361e3578eedb93d7cf6c4c5a4db06652d31fe9` (r3; parent must be the base above).
- Review the complete base-to-candidate diff, especially `doc/tasks/P02.md`'s Codex-only boundary and all `verification/P02/codex-*process-isolation*`, `codex-p02-wsb-smoke-config-r3.xml`, `codex-scratch-build-*`, and r2 review disposition/evidence files.
- The project architecture and scope are frozen. Do not propose product-scope expansion or changes to P02 Owner allowlist/ACs.

Review whether the r2 findings F-01 through F-10 are correctly closed, explicitly deferred, or still open. In particular verify: build-only guest Git/MSVC/SDK inputs remain separate from Smoke; the WSB configuration fails closed when networking restrictions are ignored; unknown memory ceilings stay deferred and do not authorize >4096 MiB; resource thresholds are measurable; dirty clone handling preserves data; the read-only canary writes only into disposable task scratch; the manifest recipe is reproducible and describes its hashing limits; canonical hash corrections match the exact reviewed commit; and raw JSONL with potential thinking events stays out of Git with sufficient audit references.

Check all scope boundaries and gate semantics against the repo documents: formal r3 review can approve design only. It does not authorize Windows Feature changes, elevation, Sandbox startup/connect/exec, Smoke, product builds/tests, or AC1-AC6 PASS. P02 Hard Build Barrier must remain. Distinguish Scheme/Plan Review, Smoke admission, Build Gate, and product acceptance. Identify any mismatch between prose, XML, scripts/commands, hashes, allowlists, and checkpoint state.

Do not execute commands that alter Windows features, launch or connect to Windows Sandbox, build, run product tests, edit files, or modify Git. Static/read-only inspection only. Do not infer runtime success from a plan.

Return a formal review in Chinese with:
1. Exact base, candidate, tree, checkout cleanliness and scope inspected.
2. Decision: `APPROVED`, `APPROVED_WITH_CONDITIONS`, `CHANGES_REQUESTED`, or `BLOCKED`; explain what that decision authorizes (design review only).
3. P0/P1/P2/P3 counts and a numbered finding list with severity, exact file/line evidence, user/project impact, and required action. Map r2 F-01..F-10 one by one, stating closed/deferred/open and evidence.
4. Explicit gate state: WSB feature, Smoke, Build Gate/build, AC1-AC6, Hard Build Barrier. Use `UNKNOWN`, `NOT_RUN`, or `BLOCKED` where evidence is absent; never mark runtime gates PASS based on static design.
5. Reviewer limitations, commands attempted/results, and whether any finding blocks the next read-only preflight.
