# M2-S1 research release — 2026-09-26

- Authorization: user explicitly directed DeepSeek Harness to perform the M2-S1 research at a Codex-fixed base in a dedicated workspace, submit candidate tradeoffs, raw experiment logs, report and Handoff, and mark each item `PASS`, `BLOCKED` or `NOT_RUN` without product or shared Contract changes.
- Dependency: M2-C1 is `done`; its fixed Contract blob at the research base is `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`.
- Research base: `85a2aa7fd07a2dca843bf5cea3ec34070b63bdbc` (`master` before release governance edits).
- Owner: DeepSeek Harness. Reviewer: Codex (non-author). Branch: `agent/deepseek/M2-S1-resource-channel-spike`.
- Owner workspace: `C:/Users/49745/.codex/worktrees/M2-S1-dsh-resource-channel`, created with `git clone --no-local --branch master --single-branch G:/CODEX/New Manga` and then `git switch -c agent/deepseek/M2-S1-resource-channel-spike`.
- Verification before dispatch: `git rev-parse --show-toplevel` resolved to the above C: path; `git rev-parse --git-dir` and `--git-common-dir` both returned `.git` inside that clone; `git rev-parse HEAD` returned the fixed base; branch matched; `git status --short` was empty; `.git/objects/info/alternates` absent. A temporary file under `verification/M2-S1/` was successfully staged and unstaged, then removed; status returned clean. No product test or research experiment was run by Codex.
- Owner allowed paths: `doc/tasks/M2-S1.md`, `doc/research/M2-S1_RESOURCE_CHANNEL_SPIKE.md`, one new `doc/handoffs/M2-S1-*.md`, and `verification/M2-S1/**`. Owner must preserve this release record and the earlier scope registration record.
- Excluded: `src/**`, `tests/**`, dependencies, Schema, shared Contract, AD-001, governance navigation, and unrelated Task/Review files. Reviewer report path is `doc/reviews/M2-S1-<reviewed-head>.md` and belongs to Codex.
- Gate at release: `ready / RESEARCH_RELEASED`; Owner research, non-author Review and integration remain pending. IPC runtime and product implementation stay unreleased.

The Owner branch remains at the fixed base. The release governance commit can be read at `origin/master` after a fetch; it is not merged into the Owner branch so the research diff retains its fixed base.
