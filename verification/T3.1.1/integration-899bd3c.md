# T3.1.1 Codex Integration Evidence

Date: 2026-09-22 (Asia/Shanghai)

## Fixed inputs and integration chain

| Item | Value |
|---|---|
| Base | `e771179beaa92b7c592a1986a32ffbf1b6302566` |
| Delivery | `899bd3c99752ce435da25e41166bafa1c2963abc` |
| Author branch/worktree | `agent/antigravity/T3.1.1-storage-sqlite` / `G:/CODEX/New Manga.worktrees/T3.1.1-antigravity-storage-sqlite` |
| Handoff | `81c319705afd2be2abc168414310164acdce9d90` |
| Independent Review | `4e1eb3ab829eea438437e6289418c20393950dcb`, DeepSeek Harness, `approved` |
| Product merge | `0c70e44` (`master`) |
| Review-evidence merge | `cbed31b` |
| Handoff merge | `0ed71a8` |

Codex merged the reviewed delivery only after the independent Review reported
`approved`. The product merge is a `--no-ff` merge of the fixed delivery head;
Review and Handoff were then merged as separate evidence-only commits. Existing
main-worktree user dirty/untracked paths were preserved and were not staged.

## Integration gate

Shell: PowerShell. Venv: `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`,
Python 3.12.3. Environment: `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=src;.`.

| Gate | Command | Result | Evidence |
|---|---|---:|---|
| Focused | `python -m pytest tests/reading_export tests/storage -q -p no:cacheprovider` | `220 passed`, exit 0 | [integration-focused.log](integration-focused.log) |
| Core | `python -m pytest tests/core -q -p no:cacheprovider` | `49 passed`, exit 0 | [integration-core.log](integration-core.log) |
| Compile | `python -m compileall -q src tests` | exit 0 | [integration-compileall.log](integration-compileall.log) |
| Smoke | `python -m bootstrap.app --smoke-test --data-root <isolated temp root>` | exit 0 | [integration-smoke.log](integration-smoke.log) |
| Diff check | `git diff --check` | exit 0 | command result; no whitespace errors |

The full test suite was not repeated in this integration window. The delivery
and independent Review records retain their prior full-suite result and known
torch-environment limitation.

## Review finding disposition

- **R-001 / accepted design choice:** v4 tables intentionally have no foreign
  keys or cascade delete. The delivery report's phrase claiming foreign-key
  linkage/cascade is corrected by this Task record; no product code change was
  needed.
- **R-002 / deferred P2:** duplicate `progress_id` in malformed or manually
  edited legacy JSON can still surface raw `sqlite3.IntegrityError`. The import
  transaction rolls back and leaves the legacy file unchanged, and the normal
  UUID writer does not produce duplicates. A future hardening task must
  prevalidate uniqueness and raise a typed `LegacyInvalidRecordError` with file
  and entry context; no new delivery head was created for this integration.
- **R-003 / evidence wording corrected:** the delivery Probe 3 only checks that
  JSON files remain present. The independent Review's call-level monitor covered
  14 filesystem mutation APIs and recorded zero calls; that is the authoritative
  integration evidence for the no-mutation claim.
- **R-004/R-005/R-006:** retained as non-blocking P2 follow-ups in the Task; they
  are not regressions introduced by this delivery.

## Scope and outcome

The integrated product diff is limited to the reviewed SQLite v4 persistence,
legacy import, bootstrap wiring, tests, and their evidence. No QML/UI, Provider,
Pipeline, source-file, Managed Copy, Lock, current/pinned Revision, or dependency
scope was added. Result: **T3.1.1 = VERIFIED_COMPLETE**.
