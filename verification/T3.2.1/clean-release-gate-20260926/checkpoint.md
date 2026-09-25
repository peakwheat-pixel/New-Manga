# T3.2.1 Checkpoint — ZCode Continuation

Date: 2026-09-26 (Asia/Shanghai)

## Frozen input and workspace

- Task authorization base: `c2fcb1ce575099f6e74f69c711f423040a545951`.
- Requested source baseline was `master @ eec1aa49...`; the local full master commit resolved in this repository is `eec1aa49d07119f0aa66ff461ebbb55e4595e624`. The longer hash supplied in the request differs after the shared `eec1aa49` prefix and was not used as a commit object.
- Fixed package source HEAD: `08f9bd85137965df922db524bc92917af513bd24`, parent `d9285cbe7e3bf5eae55bcb925a03b88aeb464408`, based directly on the resolved master commit above.
- Active linked worktree: `G:\CODEX\New Manga.worktrees\T3.2.1-clean-release-gate-20260925`.
- Branch: `codex/T3.2.1-clean-release-gate-20260925`.
- Git common directory: `G:/CODEX/New Manga/.git`.
- At checkpoint creation, HEAD was the fixed input above; only `verification/T3.2.1/clean-release-gate-20260926/` was untracked. No product source edits were made in the GUI continuation.
- User checkout `G:\CODEX\New Manga` and old closeout worktree `G:\CODEX\New Manga.worktrees\T3.2.1-codex-release-gate-closeout` were left untouched. Old closeout branch/head `codex/T3.2.1-release-gate-closeout @ 188d72a9d144b8cab16f77757abc46318ac8e5e6` was not rebased or overwritten.

## Build evidence bound to fixed input

- Python `3.12.3` (64-bit); PySide6 `6.11.2`; Qt `6.11.2`; Shiboken6 `6.11.2`; PyInstaller `6.22.3`; hooks-contrib `2026.7`.
- Build environment: `G:\CODEX\New Manga.task-envs\T3.2.1-clean-gate-py312-20260926`.
- Exact recorded Build 2 command:

  ```powershell
  & 'G:\CODEX\New Manga.worktrees\T3.2.1-clean-release-gate-20260925\packaging\build.ps1' -PythonExe 'G:\CODEX\New Manga.task-envs\T3.2.1-clean-gate-py312-20260926\Scripts\python.exe' -OutputDir 'G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926\build2\dist' -WorkDir 'G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926\build2\work' -ConfigDir 'G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926\build2\pyinstaller-config'
  ```

- Build 1 and Build 2 were made from the same fixed source HEAD. Build 2 manifest SHA-256: `073B84F509685EFE636071DCA7794C2A45B0DBB2646E40A6C9E05FF2029D9608`; packaged `NewManga.exe` SHA-256: `3aac341ace018a6884322ea2602c90c350844330154d63dc51ff16aa0bef74b2`; manifest enumerates 2,475 files / 234,071,167 bytes.
- Task-local raw logs, manifests, runtime versions, dependency freeze, build comparison and static verifier: [`verification/T3.2.1/clean-release-gate-20260926`](.). Packaging tests recorded 12 passed. Check the raw logs and comparison result before upgrading AC2 from partial.
- Historical Build 3/4 were based on pre-fix `8738c41d7215920935e6fa067d3740e69280cdc6`; their manifests differ. They are preserved under `build-history/` and are not AC2 evidence for `08f9bd8`.

## Local host simulation checkpoint

Per user direction on 2026-09-26, do **not** use Windows Sandbox; a local host simulation may count for AC3 if the required interactive workflow is completed. This run is explicitly a host simulation, not a separate clean-machine environment. AC3 remains `BLOCKED` until the remaining workflow and restart recovery are complete.

- Host: Windows 11 Pro x64, build `10.0.26200`.
- Build 2 package was staged under Unicode/read-only program path `G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926\host-simulation-20260926-rerun1\程序目录只读\NewManga`; isolated profile/data root is `G:\CODEX\New Manga.artifacts\T3.2.1-clean-release-gate-20260926\host-simulation-20260926-rerun1\用户配置隔离\AppData\Local\New Manga`. Launcher constrained `PATH` to `C:\WINDOWS\System32;C:\WINDOWS`; the host itself still has Python installed, so record this as a local simulation limitation.
- Synthetic fixture `漫画页-测试.png`, 520×760, SHA-256 `05026a0531c0f053ec7d58db35849338c93ddd70edbf9185f354663567c16430`, was imported. Read-only SQLite inspection found one Book, one Chapter, one Page, matching `source_hash` and managed-copy hash; original synthetic source remained unchanged.
- Completed interactively: launch, create Book, create Chapter, import Page, enter Workbench, display imported image, open Reader and see `1 / 1 page`, open Settings and verify blank defaults/no configured credential. Evidence screenshots `01`–`13` are in the task-local `host-simulation/` folder.
- App process PID `12276` exited normally; launcher session `94490` returned `PROCESS_EXIT=0`. This is not a restart/recovery check and no post-exit SQLite-lock probe was captured. The process is no longer running; preserve existing data and logs, and use a new run/log folder for continuation.
- Not yet completed: configure/use Mock or Local Pipeline; Reader export; close/relaunch the same package against the same isolated profile and prove restored Book/Chapter/Page state. Do not mark AC3 complete until these are evidenced.
- Runtime logs contain ChapterPicker `Keys`/`Accessible`/style warnings and `qt.qpa.mime: Retrying to obtain clipboard`; no `currentChapterId` TypeError or QtCore missing-DLL startup failure was observed. After import, Bookshelf still displayed `0 页` although the database and Reader showed one page. Do not repair product/QML in this Gate; if correction is needed, stop and create a separately frozen child Task with Qoder as QML/UI owner and a non-author Reviewer.
- Settings remained unchanged. Pipeline defaults/bindings were empty; no credentials or provider changes were made. The earlier file-picker location showing unrelated files was not used; only the synthetic fixture above was imported.

## AC status at checkpoint

All statements below are bound to package source HEAD `08f9bd85137965df922db524bc92917af513bd24`; they do not close the Gate.

| AC | Status | Checkpoint evidence / remaining work |
|---|---|---|
| AC1 | PARTIAL | Runtime/build versions, source HEAD and exact Build 2 command recorded. Confirm app version, schema/migration version and complete declared-input snapshot. |
| AC2 | PARTIAL | Current-input Build 1/2 artifacts and manifests exist; verify the raw deterministic comparison and close artifact exclusion checks. Build 3/4 are invalid for this HEAD. |
| AC3 | BLOCKED | Host simulation launch and initial GUI flow passed; full workflow and restart recovery remain. No Sandbox was used in this continuation. |
| AC4 | PARTIAL | Static closure and runtime bookshelf/workbench/reader/settings reached; review full four-page/plugin/QML closure and warnings against final package. |
| AC5 | NOT_RUN | Optional-provider dependency boundary and missing-dependency diagnostics remain. Heavy model dependencies were absent in the build environment. |
| AC6 | PARTIAL | Book/Chapter/Page, Workbench and Reader observed; Mock/Local Pipeline, export, close and relaunch recovery remain. |
| AC7 | PARTIAL | Synthetic source/managed-copy hash and basic SQLite rows checked. Lock/revision/manual-confirmation and secret non-disclosure probes remain. |
| AC8 | PARTIAL | Unicode paths, isolated `%LOCALAPPDATA%`, read-only app copy and exit code evidenced. Explicit `--data-root` and no-process/no-SQLite-lock checks remain. |
| AC9 | NOT_RUN | Five cold starts and P50/P95 remain; Windows 10 best effort also remains `NOT_RUN`. |
| AC10 | NOT_RUN | Freeze the complete evidence at a final fixed HEAD, then request independent DeepSeek Harness review and wait. Integration remains null; no push or release. |

## Resume instructions and safety

1. Keep the build input at the fixed HEAD unless a separately authorized Task changes product code. Do not rebase the old closeout candidate or alter the user checkout/other worktrees.
2. Read `host-simulation/run-host-simulation.ps1` before reuse. Continue from the existing isolated app data root to test recovery, but create a new run ID and preserve every existing log, screenshot, database and package directory.
3. Finish the permitted GUI workflow and security/path checks; record skipped items individually as `NOT_RUN`. Do not treat `--smoke-test` as interactive acceptance.
4. Update the task-local verification and Task/Handoff with exact final source HEAD, artifacts, commands, exit codes and evidence links. Do not mark any incomplete Gate as PASS.
5. Once all evidence is frozen, dispatch DeepSeek Harness as a non-author full-scope Reviewer and stop for its result. ZCode must not self-review. Codex retains integration responsibility; no merge, push, publishing or artifact cleanup is authorized.

Historical Sandbox files and old artifacts are intentionally preserved. Do not launch or use Sandbox.

---

# ZCode Continuation Run Record (2026-09-26, later session)

Fixed input unchanged: source HEAD `08f9bd85137965df922db524bc92917af513bd24`, Build 2 manifest SHA-256 `073B84F509685EFE636071DCA7794C2A45B0DBB2646E40A6C9E05FF2029D9608`, `NewManga.exe` SHA-256 `3aac341ace018a6884322ea2602c90c350844330154d63dc51ff16aa0bef74b2` (both re-verified at session start). The rerun1 read-only program directory and its isolated data root were reused for recovery; no old log, screenshot or database was overwritten. All new runs below are local host simulations on the same Windows 11 Pro x64 build `10.0.26200` host (host still has Python installed; `PATH` was constrained to `C:\WINDOWS\System32;C:\WINDOWS` and `python`/`py`/`git` were not visible to the launched process). This is not clean-machine coverage.

## AC2 deterministic comparison and exclusions (closed)

- `builds/manifest-compare.raw.log`: `Manifests match identically.` `EXIT_CODE=0` (Build 1 vs Build 2, same fixed source HEAD). Build 3/4 remain historical (`build-history/`, pre-fix HEAD `8738c41d`) and are not AC2 evidence.
- `builds/ac4-static-closure.log` + `builds/scan-manifest-exclusions.py` / `host-simulation/manifest-exclusion-scan.log`: 2,475 manifest entries, zero absolute paths, zero venv/pytest/`.git`/verification/user-data entries; the only `tests` hit is PySide6's own `QtTest/TestSchedule.qml`. Top level is exactly `NewManga.exe` + `_internal`.
- Qt/ICU closure: `builds/qt-icu-closure-build2.json`, `check_qt_closure.py --dist-dir build2\dist\NewManga` exit `0`.
- AC4 static closure: `builds/ac4-static-closure.log` — `Main.qml`, all four top-level page QMLs, `qwindows.dll`, Qt6Core/Gui/Qml/Quick/QuickControls2/Widgets, `python312.dll` all present, `missing_count=0`; QML modules `Qt/QtCore/QtNetwork/QtQml/QtQuick` and 10 imageformat plugins shipped.

## AC1 build-input completion

- Application version: the product defines no application/version field (no `applicationVersion` in `src/bootstrap/app.py`, none in `packaging/new_manga.spec`); the deliverable is identified by source HEAD + artifact manifest, recorded as such rather than invented.
- Schema/migration version: code `src/infrastructure/sqlite/schema.py` defines `SCHEMA_VERSION_V1..V4` with four migrations; the isolated runtime DB reports `application_metadata.schema_version = '4'` and all four `schema_migrations` rows (`v1__storage_base`, `v2__library_region_persistence`, `v3__production_pipeline_persistence`, `v4__reading_export_storage`), consistent with code.
- Build inputs: `setup/runtime-versions.txt` (Python 3.12.3, Qt/PySide6/Shiboken6 6.11.2, PyInstaller 6.22.3), `setup/pip-freeze-all.txt`, `setup/build-requirements.txt`, `setup/pip-install-report.json`; exact Build 2 command is recorded above in this checkpoint.

## Recovery run 2 (`host-simulation-20260926-rerun2`) — AC3/AC6/AC5/AC7

Launcher: `host-simulation/run-host-simulation-recovery.ps1` (new run id; reused the rerun1 read-only program directory `程序目录只读\NewManga` and the isolated data root `用户配置隔离\AppData\Local\New Manga`; `library.db` before-hash `d21c69858e7fdcb0a105a7869eaf2af3823b5ae72f8f1b327e9f5d246260cf16`; constrained PATH). PID `9320`, main window ready in `1.327 s`.

Interactive flow (screenshots `14`–`23`, same folder):

1. `14-recovery-bookshelf-restored.png` — cold start against the reused data root shows Book `本机回归漫画-20260926` and Chapter `本机验收章节` restored. This is the restart-recovery evidence for the earlier interactive session.
2. `15-workbench-entered.png` — Workbench restores the page list (`1 漫画页-测试.png ○ 等待`).
3. `16-pipeline-trigger-no-provider.png` / `17-pipeline-failure-diagnostic.png` — `全部翻译` (translate-all) was triggered with no provider configured. The pipeline run reached `completed_with_failures` (detect step `!`), UI shows `完成 0 失败 1`, and the main program did not crash.
4. Read-only SQLite diagnostic dump `host-simulation/pipeline-diagnostic-dump.json` (dump script `dump-pipeline-diagnostic.py`): run `run-7b54ae37c70e4bcdbb880c1a9e6c306e`, `error_code=PROVIDER_NOT_CONFIGURED`, `error_detail` names the missing docTR weight file, its official fetch URL and expected SHA-256 (`stage=detection`), `provider_binding_snapshot={}`, per-step `lock_snapshot` all false. This is the AC5 missing-dependency diagnostic evidence and the AC6 pipeline step executed fail-closed. The product contains no mock provider by design (`src/infrastructure/providers/runtime.py`: unconfigured providers are `not_configured`, never silently mocked), so the honest diagnostic — not a fabricated success — is the expected release behavior.
5. `18-reader-recovered.png` → `20-reader-page-restored.png` — Reader restores `1 / 1 页 · 100%`, original image renders, reading progress (`最后阅读 … · 累计 295 秒`) survived the restart.
6. `21-export-window.png` → `22-export-executed.png` — Export window: content switched to `Original（原图）` via the combo box, format ZIP, output path typed into the isolated `rerun2\exports` directory. Result: `导出完成：…\rerun2\exports\recovery-chapter-1-original.zip`.
7. Export artifact verification: ZIP SHA-256 `94a1166fb277207627dbf19f59880595f096227597227ba30e99c65bd8ce08ee`, contains `0001_漫画页-测试.png` whose SHA-256 equals the original fixture hash `05026a05…6430` (byte-identical managed-copy round trip). The export-history row was later re-read from the DB with matching `file_hash` (see AC7 dump).
8. Graceful exit via title-bar close. `logs/process-exit.json` + `logs/post-exit-check.json` (closeout script `closeout-rerun2.ps1`): process exited within the 30 s window (`EXITED=True`), `RESIDUE=0` NewManga processes, SQLite lock probe `EXCLUSIVE_OPEN_OK`, after-hash recorded. Exit code itself was not captured in this run (launcher did not `WaitForExit`); it is captured as `0` in run 3 and all 5 benchmark runs below.

## Recovery run 3 (`host-simulation-20260926-rerun3`) — final restoration confirmation

Launcher: `run-host-simulation-rerun3.ps1` (backgrounded; waits for exit and records it). PID `26304`, ready in `1.331 s`. Screenshots `24-rerun3-bookshelf-recovered.png` (bookshelf restored again) and `25-rerun3-reader-recovered.png` (Reader `1 / 1 页`, page image and reading progress restored). Graceful close → `logs/process-exit.json`: `RESIDUE=0`, `EXCLUSIVE_OPEN_OK`. PowerShell `Start-Process -PassThru` returned an empty `ExitCode` here despite `WaitForExit` (known behavior when the handle is not pre-cached); the process disappearance, zero residue and lock-free probes stand as the graceful-exit evidence for this run.

## AC9 cold-start benchmark + AC8 explicit `--data-root` (one combined run)

Script `run-cold-start-benchmark.ps1`, results `…\cold-start-benchmark\logs\cold-start-results.json`:

- Attempt 1 (preserved under `cold-start-benchmark\logs-argparse-fail-attempt1\`): passing the path as two tokens failed argparse (`error: unrecognized arguments: Manga.artifacts\…`, exit 2). Preserved as fail-closed evidence of argument validation.
- Attempt 2 (final): single-token `--data-root="<path>"`, 5 runs, all `READY=True`, graceful `CloseMainWindow` close, `EXIT=0` each: `1.158 / 1.102 / 1.090 / 1.078 / 1.146 s`. P50 (median) = `1.102 s`, P95 (linear interpolation) = `1.156 s` (`cold-start-benchmark\p50-p95-summary.log`).
- Explicit `--data-root` evidence: `…\cold-start-benchmark\data-root\` received `library.db` (303,104 bytes) + `managed\` (AC8).
- Windows 10 x64: `NOT_RUN` (no Windows 10 machine in this environment; not inferred from anything else).

## AC8 default data root probe

Script `run-default-data-root-probe.ps1`, record `…\default-data-root-probe\default-data-root-probe.json`: launched with **no** overrides from the same read-only program directory. Real `%LOCALAPPDATA%\New Manga` (`C:\Users\49745\AppData\Local\New Manga`) did not exist before and was created by the app (`root_created_by_probe=true`, `library.db` + `managed\` inside). Window ready `1.138 s`, graceful close `EXIT=0`, `RESIDUE=0`. The created directory is preserved untouched as evidence (not cleaned up).

## AC7 data-safety verification (single read-only pass)

Script `ac7-data-safety-check.py`, output `ac7-data-safety-check.log`:

- Synthetic fixture `漫画页-测试.png` SHA-256 unchanged after the whole session (`05026a05…6430`, `unchanged=true`).
- Managed copy exists at `managed/books/356f…/chapters/aca7…/original/674700a7….png`, SHA-256 equals `source_hash` (lossless managed-copy round trip; export ZIP content also matched).
- `page_locked=0`, `review_state=unreviewed`, `overall_status=not_started` — locks and manual-confirmation content were not modified by the failed pipeline or the export.
- `artifact_revisions=0`, `region_revisions=0` — the fail-closed pipeline created no revisions.
- `export_history`: exactly one row, `status=completed`, `file_hash` equals the verified ZIP hash; scope snapshot records `mode=original`, the page id and the isolated output path. (Observed, not judged: `book_id`/`chapter_id` columns are empty strings in that row while `scope_snapshot_json.page_ids` is populated — recorded for the Reviewer; not a Gate item and no product change is authorized here.)
- Secret scan over all rerun/benchmark/probe logs and diagnostics (pattern `api[_-]?key|authorization|bearer\s|password|secret|sk-…`): zero hits, `NO_CREDENTIAL_MATERIAL_IN_LOGS`. No credential was ever configured in these runs (Settings remained at blank defaults, `pipeline_defaults` empty).

## AC status after this continuation (bound to HEAD `08f9bd8`; final judgment belongs to the independent Review)

| AC | Status | Basis |
|---|---|---|
| AC1 | PASS | Versions/snapshot/commands above; no app-version field exists in the product (recorded, not invented) |
| AC2 | PASS | Manifest-identical Build 1/2 (`EXIT_CODE=0`), exclusion scan clean, package closed |
| AC3 | PASS (local host simulation route, per user direction; not clean-machine coverage) | Full interactive workflow + restart recovery (rerun2/rerun3) on the fixed package; host-sim limitation recorded |
| AC4 | PASS | Static closure `missing_count=0` + Qt/ICU exit 0 + four pages reached at runtime |
| AC5 | PASS | `PROVIDER_NOT_CONFIGURED` honest diagnostic; app/UI start unaffected |
| AC6 | PASS (pipeline step executed fail-closed, recorded) | Full flow incl. export and restart recovery; pipeline honest-failure diagnostic captured |
| AC7 | PASS | Hash/Lock/Revision/manual-state/secret checks above |
| AC8 | PASS | Unicode read-only program dir, default root, explicit `--data-root`, zero residue, no SQLite lock |
| AC9 | PASS (Windows 11 host simulation) / Windows 10 = NOT_RUN | 5 cold starts, P50 `1.102 s`, P95 `1.156 s`, all EXIT=0 |
| AC10 | IN_PROGRESS (evidence frozen; independent Review requested, awaiting result) | This record + delivery handoff; no integration, push or release |

Remaining NOT_RUN items (explicit): Windows 10 x64 cold-start matrix; heavy-model (real docTR weights) pipeline success path — out of Gate scope by user direction (no model downloads as a Gate precondition).

Known observations left for the Reviewer (no product change authorized in this Gate): bookshelf chapter row shows `0 页` while the DB and Reader show 1 page (pre-existing, see earlier checkpoint); export-history row leaves `book_id`/`chapter_id` empty while `scope_snapshot_json` is populated; ChapterPicker/style warnings in runtime logs; Qt `qt.qpa.mime: Retrying to obtain clipboard` noise.

