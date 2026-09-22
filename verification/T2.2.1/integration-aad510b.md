# T2.2.1 Codex Integration Evidence

## Fixed integration state

- Repository: `G:/CODEX/New Manga`
- Branch: `master`
- Product integration head: `fe9fca0` (`d8d5c33` ZCode functional tests,
  `99b5f0e` QML implementation, and `fe9fca0` Escape/run-state tests)
- Governance/evidence state at capture: `aad510b`; later governance commits
  update the authoritative Task/STATUS/Plan pointers only.
- Qoder delivery reviewed: `08465739ae92d7175a77d00053abe598bb150bae`
- Review: `verification/T2.2.1/review-0846573.md`, review artifact commit
  `125fff7`
- ZCode non-author review: `verification/T2.2.1/review-df637df.md`
- Release Gate base: `16810c5`

The author history was preserved through serial cherry-picks; no author
branch merged `master`, and no history was rewritten. The pre-existing dirty
main-worktree paths were preserved and were not staged or overwritten.

## Fresh post-integration verification

Shell: PowerShell. Interpreter:
`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe`.
`PYTHONPATH=src`; `PYTHONDONTWRITEBYTECODE=1` for pytest; `QT_QPA_PLATFORM`
unset; pytest cache provider disabled.

| Command | Result | Exit |
|---|---|---:|
| `python -m pytest tests/ui_shell tests/workbench/test_qml_workbench.py tests/reading_export -q -p no:cacheprovider -rs` | 278 passed, 0 failed, 0 skipped; `SHELL=PowerShell`, `PYTHON=G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312/Scripts/python.exe` | 0 |
| `python -m compileall -q src tests` | clean; same shell/interpreter | 0 |
| `python -m bootstrap.app --smoke-test --data-root G:/CODEX/New Manga.task-envs/T2.2.1-integration-smoke-20260922` | clean bootstrap smoke; fresh data root; same shell/interpreter | 0 |
| `python -m pytest tests -q -p no:cacheprovider -rs` | 1209 passed, 6 skipped, 1 known environment failure, 1 warning; same shell/interpreter | 1 |
| `git diff --check` | clean after governance artifact whitespace fix | 0 |

Full-suite skips, one per line: `tests/network/test_connection_tester.py:106`
and `tests/network/test_transport_tls.py:39`, `47`, `62`, `69`, `83` — each
`openssl unavailable`. The single failure is the existing
`tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment`
probe because `torch` is installed in this venv. It is not a T2.2.1 failure;
the exit 1 is intentionally retained rather than hidden.

## Acceptance and safety result

Reader and Workbench picker selection, Escape dismissal, no-context safety,
command-error clearing with unchanged run state, webtoon canvas ground, and
the ZCode ViewModel seam all have executable evidence. No bootstrap, storage,
provider/runtime, dependency, schema, or top-level page change was added.

T2.2.1 is eligible for `VERIFIED_COMPLETE` with the known environment probe
recorded as an external verification limitation. The next release gate is
T3.1.1; it is not started by this integration.
