# P04 Proposal Amendment Checkpoint

- Timestamp: 2026-10-09 17:41:50 UTC (2026-10-10 01:41:50 Asia/Shanghai)
- Agent / Task ID: Codex / P04
- TaskStatus / ExecutionState: proposed / CHECKPOINTED
- Branch / Worktree: `codex/P04-scope-freeze` / `G:/CODEX/New Manga.worktrees/P04-scope-freeze`
- Base / last reviewed HEAD / current HEAD: `88579622d85ff6d0dfd509c6f21931bd91d0881b` / `018023e8129ee9e34f441e39b30ab0c22786eccc` / `018023e8129ee9e34f441e39b30ab0c22786eccc`
- Root main: `main@88579622d85ff6d0dfd509c6f21931bd91d0881b`; the 203 pre-existing modified/untracked root paths are preserved and outside this branch's changes.
- Working Tree: modified `doc/00_INDEX.md`, `doc/REBASELINE_PLAN.md`, `doc/STATUS.md`, `doc/tasks/P04.md`, `verification/P04/proposal-checkpoint-20261010.md`; new `verification/P04/proposal-review-checkpoint-018023e8.md`, DSH prompt/output/exit/session records. No files staged.

## Completed Steps

- DSH proposal review at fixed head `018023e8129ee9e34f441e39b30ab0c22786eccc` returned `changes requested` (P0/P1/P2/P3=`0/1/3/6`); full report and dispatch prompt are preserved under `verification/P04/`.
- Confirmed `build.rs` requires the gitignored `target/core-sidecar/core-sidecar` directory before Tauri build; it is absent in this worktree. P02 scratch-build plan forbids unverified root ignored output as an input.
- Updated P04 Task draft to record the missing bundle provenance gate, exact `--bin m2rc1-desktop` commands, literal AC1 assertion, `#[cfg(test)]` boundary, diagnostic evidence location and blocked/follow-up state if a mismatch is reproduced.
- Updated Plan/STATUS/Index to keep P04 proposed and machine-visible as blocked by P02 Build Gate plus a Codex-provisioned isolated checkout and provenance-bound sidecar bundle.

## Test / Review State

- P04 Cargo/Tauri tests: `BLOCKED / NOT_RUN`; no build, test, Feature query/enable, scratch clone or Sandbox operation was performed.
- The P04 proposal review is static only and does not pass the implementation or product gates.
- Initial proposal route validation and direct link checks passed; rerun route, link and diff checks on this amendment before committing.

## Next Exact Step

- Run the route validator, `git diff --check`, and changed-document link check; stage only P04 proposal docs plus the DSH final prompt/output/exit/session records (never the stderr trace); commit the amended candidate, then ask DSH to re-review the new exact head.
- Do not release P04 or run Cargo until P02's isolation policy and the provenance-bound sidecar bundle prerequisite are satisfied.

- Previous review checkpoint: [P04 DSH changes-requested checkpoint](proposal-review-checkpoint-018023e8.md).
