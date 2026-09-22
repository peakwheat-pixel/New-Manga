# T2.1.1 Codex Integration Evidence

## Fixed integration state

- Repository: `G:/CODEX/New Manga`
- Integration worktree: `G:/CODEX/New Manga.worktrees/T2.1.1-integration`
- Integration branch: `agent/codex/T2.1.1-integration`
- Product base: `7f34135`
- Qoder delivery chain: `agent/qoder/T2.1.1-design-f-qml` through `ddb2044`
- Merge commit preserving the Qoder history: `e34e19c`
- Codex review fix: `5da1cf6`
- Review: [review-bc49ef9](review-bc49ef9.md)

The Qoder commits were merged with `--no-ff`; no author history was rewritten.
The Codex fix is limited to the F status badge surface and its focused guard.

## Fresh verification

Shell: PowerShell; interpreter:
`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`;
`PYTHONPATH=src`; `QT_QPA_PLATFORM` unset; cache provider disabled.

| Command | Result | Exit |
|---|---|---:|
| `python -m pytest tests/ui_shell tests/workbench tests/reading_export -q -p no:cacheprovider -rs` | 382 passed, 0 failed | 0 |
| `python -m pytest tests -q -p no:cacheprovider -rs` | 1178 passed, 11 skipped, 0 failed, 1 warning | 0 |
| `python -m compileall -q src tests` | completed cleanly | 0 |
| `python -m bootstrap.app --smoke-test --data-root <fresh-temp-dir>` | SQLite/database smoke completed; `library.db` present | 0 |
| `git diff --check -- src tests doc verification` | no output | 0 |

The same final product tree was rechecked on `master` after the fast-forward:
full suite `1178 passed, 11 skipped, 0 failed, 1 warning`, exit 0;
`compileall` exit 0; bootstrap smoke exit 0; and source-protection tests
`tests/storage/test_managed_storage.py tests/editing/test_text_protection.py`
reported `19 passed`, exit 0.

Full-suite skips are environment facts: 2 docTR tests, 6 OpenSSL tests, 1
numpy test, and 2 torch tests. The author’s dependency-equipped evidence
recorded 1183 passed / 5 skipped; this environment cannot reproduce that exact
split and no skip is reported as a product pass.

## Scope and safety

The integrated diff contains QML, QML tests, verification evidence, and the
author Handoff, plus the single Codex badge fix/test. It contains no bootstrap,
ports, SQLite schema/migration, provider/runtime, dependency, or Python
production changes. No user source or Managed Copy file was touched. The
main worktree’s pre-existing dirty paths were not used or overwritten.

## Gate result

Fresh integration evidence is green for the available environment. The
integration candidate was fast-forwarded to `master`; the final governance
commit is the current repository HEAD after this evidence was recorded.
The reader webtoon canvas consistency and human GUI/DPI inspection remain
deferred findings, not hidden PASS claims.
