# ZCode functional delivery report — `df637df`

Task: T2.2.1
Author: ZCode
Codex evidence supplement: 2026-09-22
Base: `16810c55c28ada960420d8053f47f29b1f71b8f0`
Delivery: `df637df1f9d6e8468bc73d6ff585bbf55e8e9a64`
Worktree: `G:/CODEX/New Manga.worktrees/T2.2.1-zcode`

## Change set

The delivery adds two functional regression tests only:

- `tests/ui_shell/test_bookshelf_viewmodel.py`: selecting another book
  refreshes the chapter model before the reader handoff and passes the second
  book/chapter context through the existing navigation slot.
- `tests/workbench/test_command_error_surface.py`: clearing a held command
  error removes the message without changing the existing pending run
  projection.

No production ViewModel, QML, bootstrap, contract, Schema, dependency, or
other product file changed in `16810c5..df637df`.

## Independent verification

| Scenario | Shell / interpreter | Command | Result |
|---|---|---|---|
| Functional focused suite | PowerShell; `G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe` | `PYTHONPATH=src PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/ui_shell/test_bookshelf_viewmodel.py tests/workbench/test_command_error_surface.py tests/reading_export -q -p no:cacheprovider -rs` | `139 passed, 0 skipped, 0 failed, exit 0` |
| Compile | Same PowerShell/interpreter | `python -m compileall -q src tests` | exit 0 |
| Bootstrap smoke | Same PowerShell/interpreter; fresh isolated temp data root | `python -m bootstrap.app --smoke-test --data-root <fresh-temp-dir>` | exit 0 |
| Diff check | PowerShell / Git | `git diff --check 16810c5 df637df` | clean, exit 0 |

The agent also reported a full-suite result of `1206 passed + 6 skipped + 1
known environment failure`, but the required shell/venv header, exit code, and
per-skip reasons were not delivered in an artefact. Codex therefore records
that full-suite claim as **NOT_RUN/UNVERIFIED**, not PASS. The full suite is a
required Qoder/Codex integration gate.

## Handoff concerns

The author report was not produced before the agent returned. This Codex
supplement records the fixed diff and independently rerun evidence; a complete
author Handoff is still required after the QML implementation and before
T2.2.1 review/integration approval.
