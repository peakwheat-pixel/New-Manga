# Antigravity implementation instruction

You are the Owner of `M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD` in the linked worktree below. Read the committed Task before editing; it is the frozen contract.

- Repository: `G:/CODEX/New Manga`
- Worktree: `G:/CODEX/New Manga.worktrees/RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-antigravity`
- Branch: `agent/antigravity/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD`
- Implementation base: `e9b66455356c56e0fe6720d658b46bdbdbeb53b5`
- Actual release/start HEAD: `d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10`
- Common directory: `G:/CODEX/New Manga/.git`
- Reviewer: DeepSeek Harness (must not author the implementation)
- Integrator: Codex
- Task: `doc/tasks/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD.md`

Start by verifying branch, HEAD, common directory, and clean status. Then update the Task to `in_progress` on your branch and implement only its frozen allowed paths.

R-001 concerns these current defaults: `verification/M2-RC2/run_e2e.py` writes to `verification/M2-RC2/raw/` when `--output-dir` is omitted; `packaging/m2ac5/run_clean_start_e2e.py` similarly writes to `verification/M2-AC5/raw/`. Make `--output-dir` required in both existing argparse parsers, update current usage text and `packaging/m2ac5/README.md` to show a fresh isolated output directory, and add `tests/packaging/test_runner_output_dir_required.py`. The regression test must prove omission exits with argparse code 2 before runner work or file writes, and that explicit output-dir parses; stop execution immediately after parsing so no Gate/build/install starts.

Run and record at minimum:

```powershell
python -m pytest -q tests/packaging/test_runner_output_dir_required.py
git diff --check
git diff --name-only d12ebc7a0bbd5617e7a376e00f45c9ee114c8c10...HEAD
```

Also compare the tracked file set/content under `verification/M2-RC2/raw/` and `verification/M2-AC5/raw/` before and after the regression test. Do not invoke either runner in a way that writes to those directories. Do not run the full Dev/Packaged Gate, builds, or installers; this is a CLI safety slice, not product Gate evidence. Record shell, Python path/version, each command's EXIT, summary, and evidence paths; do not call planned checks PASS.

Commit implementation and tests, update the Task to `in_review`, and deliver the fixed commit plus `doc/handoffs/M2-RUNNER-HISTORICAL-RAW-OUTPUT-GUARD-<short-head>.md`. Stop after handoff for independent DSH review; do not integrate or broaden scope. If an allowed-path change is needed, pause and ask Codex to refreeze the Task first.
