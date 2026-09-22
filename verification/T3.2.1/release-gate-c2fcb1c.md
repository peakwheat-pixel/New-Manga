# T3.2.1 Release Gate — Windows Packaging and Clean-Machine Release

Date: 2026-09-22 (Asia/Shanghai)
Decision: **PASS TO START**
Task: [T3.2.1](../../doc/tasks/T3.2.1.md)
Owner: Antigravity (implementation; worktree not yet created)
Independent reviewer: DeepSeek Harness
Integrator: Codex
Base: `c2fcb1ce575099f6e74f69c711f423040a545951` (`master`)
Implementation branch: `agent/antigravity/T3.2.1-windows-packaging` (to be created)
Implementation worktree: `G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-packaging` (to be created)

## Gate conclusion

The scope is independently bounded and ready to start. This Gate releases only
the packaging engineering, artifact inspection, Windows clean-machine smoke,
data-safety probes, performance evidence, Handoff and independent Review work.
It does not claim that a production package exists or that a clean Windows
workflow has passed. The clean-machine result remains a hard release condition.

## Preconditions checked

- T3.1.1 is `VERIFIED_COMPLETE`; its product code is integrated at `0c70e44`,
  with independent DeepSeek Harness approval and Codex integration evidence.
- The current mainline baseline is `c2fcb1c`; the main worktree has only the
  pre-existing user dirty/untracked paths listed in `doc/STATUS.md`. They are
  preserved and excluded from this Gate and any future packaging build input.
- `src/bootstrap/app.py` is the production entry point. It loads
  `src/ui/qml/Main.qml` through `QML_PATH` and stores user data under
  `%LOCALAPPDATA%/New Manga` unless `--data-root` is explicitly supplied.
- `requirements.txt` contains the Core runtime dependencies; `requirements-dev.txt`
  contains `pyinstaller==6.22.3` and `pyinstaller-hooks-contrib==2026.7`.
- No production `packaging/**`, PyInstaller `.spec`, or package build script is
  present at the Gate baseline.
- TASK-004 proved only a minimal Qt/QML onedir experiment. Its E12 clean Windows
  result is explicitly `BLOCKED`, so that evidence cannot satisfy T3.2.1 AC3,
  AC4 or AC6.

## Frozen scope

In scope:

- a reproducible PyInstaller onedir build for the real `bootstrap.app` entry;
- frozen resource/QML/Qt DLL closure and package manifest/hash inspection;
- Core-only startup and optional dependency diagnostics;
- user-data path, Unicode path, read-only program directory and clean shutdown
  behavior;
- clean Windows main workflow and restart persistence using authorized fixtures;
- source-file, Managed Copy, Lock, Revision, SQLite and Secret safety probes;
- startup performance measurement, support-matrix reporting, Handoff, independent
  Review and Codex integration evidence.

Out of scope:

- installer, updater, code signing, remote CI, upload, push or public release;
- UI redesign, new pages, provider/pipeline semantic changes or model quality;
- SQLite migration/schema changes and user-data migration beyond the existing
  production behavior;
- deleting old artifacts, changing other Task branches or cleaning the main
  worktree.

## Required invariants

1. The onedir artifact starts without Python, venv, source checkout or developer
   PATH; the program directory can be treated as read-only.
2. The real `Main.qml`, four top-level routes, Qt platform plugins and QML
   imports are present and load from the frozen artifact.
3. Core/UI startup does not require torch, large OCR, inpainting or translation
   model downloads; missing optional capability is typed/diagnosable.
4. User data is written outside the artifact, under the intended Windows data
   root; Unicode paths and explicit `--data-root` remain valid.
5. The clean-machine workflow does not mutate source files, lose SQLite rows,
   overwrite manual content, break Lock/current/pinned Revision invariants or
   leak secrets into logs/artifacts.
6. The process exits cleanly, releases SQLite file handles and leaves no
   residual product process.
7. A package is not `READY` when clean Windows, P0/P1, data safety, benchmark,
   or independent Review evidence is missing; no undocumented waiver is allowed.

## Required evidence before integration

- fixed build commit, app/Schema version, Python/Qt/PySide6/PyInstaller versions,
  dependency snapshot, exact build command and SHA-256 artifact manifest;
- PyInstaller spec/build output and package inspection proving no source/venv/
  user-data leakage and complete Qt/QML assets;
- local package start and no-developer-PATH run, with stdout/stderr and exit code;
- real clean Windows 11 x64 package smoke; Windows 10 x64 result separately marked
  PASS, FAIL or NOT_RUN/BLOCKED;
- main workflow plus restart persistence and source/data/Secret safety evidence;
- at least five cold-start samples with P50/P95 and hardware/OS details;
- applicable repository tests, compileall, package smoke and `git diff --check`;
- Antigravity Handoff bound to the fixed delivery head;
- DeepSeek Harness independent Review bound to the same base/head;
- Codex integration evidence after `approved` Review. No automatic release action.

## Gate audit trail

Read-only audit commands used before this Gate:

```text
PowerShell, repo: G:\CODEX\New Manga
git rev-parse HEAD                         => c2fcb1ce575099f6e74f69c711f423040a545951
git branch --show-current                   => master
git status --short --branch                 => pre-existing user dirty/untracked paths only; preserved
rg "PySide6|PyInstaller" requirements*.txt => Core + PyInstaller dev pins present
rg "QML_PATH|--data-root|default_data_root" src/bootstrap/app.py
                                           => real entry/QML/data-root seams present
Test-Path packaging                         => False
Get-ChildItem -Filter *.spec                => no production spec found
```

These are As-Is observations, not implementation or release results. All
T3.2.1 implementation checks remain `NOT_RUN` until a delivery head exists.

## Gate ownership and release rule

Codex may create the isolated Antigravity worktree from the recorded base and
release implementation within the frozen paths. Antigravity must deliver a
fixed head, tests, package evidence and Handoff. DeepSeek Harness must review
that head from an independent context and cannot review its own changes. Codex
must not integrate before `approved`. T3.2.1 cannot become `VERIFIED_COMPLETE`
or `READY` for release while the clean Windows or P0/P1/data-safety evidence is
missing.
