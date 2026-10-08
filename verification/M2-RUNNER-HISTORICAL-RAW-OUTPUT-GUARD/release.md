# M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD Release

- Date: 2026-10-08 (Asia/Shanghai)
- User authorization: R-001 follow-up assigned to Antigravity; DeepSeek Harness is the independent Reviewer; Codex is Integrator.
- Task: `doc/tasks/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD.md`
- Dependency: `M2-RUNNER-SNAPSHOT-DEBT done@73588624`
- Implementation base: `e9b66455356c56e0fe6720d658b46bdbdbeb53b5`
- Release commit / Owner start HEAD: `d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10`
- Owner branch: `agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD`
- Owner worktree: `G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity`
- Git common directory: `G:/CODEX/New Manga/.git`
- Worktree verification: branch and HEAD matched the allocation; `git status --short --branch` was clean at release/start HEAD; common directory matched the unique repository.
- CLI availability: `agy --version` returned `1.3.1`; availability probe returned exit `0`, JSON `status=SUCCESS`, response `收到`.
- Product tests: `NOT_RUN` at release; the availability probe is not product verification.
- Main checkout note: Qoder-owned `.qoder-credits/report.json` and `.qoder-credits/通路探测__8602db50.canvas.tsx` remain untouched and outside the Owner worktree.

## Allowed implementation paths

- `packaging/m2ac5/run_clean_start_e2e.py`
- `packaging/m2ac5/README.md`
- `verification/M2-RC2/run_e2e.py`
- `tests/packaging/test_runner_output_dir_required.py`
- `doc/tasks/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD.md`
- `doc/handoffs/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-<short-head>.md`
- `verification/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD/**`

Codex alone updates the Plan, Status, and task navigation metadata. Do not expand the Owner's code/test paths.

## Release Gate

Task is `ready`; no Owner implementation had started when this record was written. The task requires `--output-dir` on both runner CLIs, a safe current README example, a parser-only regression test that stops before runner side effects, and a before/after check proving both historical tracked raw directories were unchanged. Full Dev/Packaged product Gates are outside this Task and remain `NOT_RUN` unless separately authorized.
