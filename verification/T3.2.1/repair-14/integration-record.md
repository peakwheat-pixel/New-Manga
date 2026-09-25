# T3.2.1-REPAIR-14 Integration Record

## Result

**Integration result: `PASS_WITH_ACCEPTED_DEVIATION`.** The reviewed Bookshelf hydration slice is integrated at `296131b57a4c3660949ecbdfb6003c6201023dab`. The post-integration targeted suite passed. Parent T3.2.1 remains `OPEN`; parent AC3 remains `BLOCKED`.

## Fixed points

| Item | Verified value |
|---|---|
| Mainline before integration | `master` at `75fa4d796807e52c7e72752bbaeedbeb63064f37` |
| Task fixed base | `4ab6f58c06cb0691413e2630cb48a145c18c383a` |
| Delivery | `43b24eefaa1d517f51c7fd8dba7c658a58415d89` |
| Reviewed Handoff tip | `2f0d26645a5e3597977859f0624d72f561d38ba1` |
| Independent Review report commit | `f616175e24229c4fbcffb0145e10764e0c7f93df`, parent=`2f0d26645a5e3597977859f0624d72f561d38ba1` |
| Review decision / anchors | `decision: approved`; report base, reviewed delivery, and reviewed head match the objects above |
| Codex integration worktree | `G:/CODEX/New Manga.worktrees/T3.2.1-codex-repair-14-integration`, branch `codex/T3.2.1-repair-14-integration`, common dir `G:/CODEX/New Manga/.git` |
| Product/evidence integration commit | `296131b57a4c3660949ecbdfb6003c6201023dab` |

The author branch and DeepSeek review branch were not merged. The integration commit contains one product file, two test files, the 13 delivery evidence files, the reviewed final Handoff, the unchanged Round 2 report and its two run logs, and three Codex verification logs. The superseded Round 1 Handoff was not imported. The Review report and final Handoff were copied without edits.

## Post-integration verification

| Check | Result | Evidence |
|---|---|---|
| `tests/ui_shell tests/reading_export/test_qml_contract.py tests/core/test_bootstrap.py` | **184 passed in 12.52s; exit 0**; Windows PowerShell 7.6.6, Python 3.12.3 from `G:/CODEX/New Manga.task-envs/T3.2.1-packaging-py312/Scripts/python.exe`, run against integration commit `296131b` | [integration-suite.log](integration-suite.log) |
| `git diff --check 75fa4d796807e52c7e72752bbaeedbeb63064f37` | **exit 0** | [integration-diff-check.log](integration-diff-check.log) |
| Protected-path diff from the same mainline base | **exit 0**, no differences in `src/domain`, `src/application`, `src/ports`, `packaging`, or dependency manifests; changed-path inventory contains no Schema or migration path | [integration-protected-path-check.log](integration-protected-path-check.log) |

No Schema, packaging implementation, dependencies, parent Gate files, or REPAIR-13 history were changed. Review report: [review-report-dsh-r2.md](review-report-dsh-r2.md). Its independent GUI rerun and test output are retained beside it.

## Review finding dispositions

### R14-008 — accepted verification setup deviation

The AC4 log and probe show that Session 1 launched the fixed EXE on an empty data root and exited; after that, `assemble_services` / `LibraryService` created one Book and Chapter in the same isolated SQLite data root; Session 2 launched the fixed EXE and displayed the persisted book. DeepSeek Harness independently reran the probe with two real OS processes and verified the restart hydration result.

Codex accepts this setup deviation for the narrow defect under test: the changed behavior is initial Bookshelf hydration from persisted library data, and the second packaged GUI process exercised that path with a production-service-created record. GUI-native book creation during Session 1 was **not run** and is **not claimed as PASS**. No follow-up implementation Task is released for that unrelated creation flow. The parent release gate remains responsible for any broader product acceptance.

### R14-010 — counts corrected in this record

The source diff has 17 paths from fixed base to delivery (`3 M + 14 A`), including the Round 1 Handoff; it has 18 paths from fixed base to the reviewed Handoff tip, which adds the Round 2 Handoff. The prior Handoff's `13` / `17` counts are retained as reviewed historical text and are not silently edited. The Codex integration delta from mainline has 23 paths, including the selected product/tests/evidence plus the final Handoff, Review artefacts, and integration logs.

### Other Round 2 notes

- R14-009 (the fixed EXE cannot be rebuilt from a repository packaging recipe in this slice) is deferred to the parent T3.2.1 packaging/release Gate; no packaging implementation was added.
- R14-011's dispatch typo is superseded by the verified full reviewed-head SHA recorded above.
- R14-012's output-overwriting probe was not rerun by Codex; the independent Reviewer had already rerun it and restored the reviewed worktree. Codex reran the requested pytest suite only.

## Parent Gate invariant

T3.2.1 Full Release Gate remains `OPEN`; parent AC3 remains `BLOCKED`. REPAIR-14 integration does not establish parent release readiness or alter any REPAIR-13 result.
