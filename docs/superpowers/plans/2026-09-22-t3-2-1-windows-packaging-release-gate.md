# T3.2.1 Windows Packaging and Clean-Machine Release Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and verify a reproducible Windows x64 PyInstaller onedir package for the real application entry, then prove the core workflow on a clean Windows machine without data or source-file damage.

**Architecture:** Keep packaging in `packaging/` and make the spec explicitly collect the real `src/ui/qml` tree and Qt plugins. Keep user data outside the package under `%LOCALAPPDATA%/New Manga`; change `src/bootstrap/**` only if a frozen-resource seam is required. Use a manifest/hash script and external clean-machine runbook so artifact inspection and runtime behavior are independently reproducible.

**Tech Stack:** Python 3.12.x, PySide6_Essentials 6.11.2, shiboken6 6.11.2, PyInstaller 6.22.3, pyinstaller-hooks-contrib 2026.7, pytest, PowerShell, Windows 11 x64 primary / Windows 10 x64 best effort.

**Spec:** [T3.2.1 Task](../../doc/tasks/T3.2.1.md), [D07 non-functional requirements](../../doc/07_NON_FUNCTIONAL_REQUIREMENTS.md) §81–§85/§104/§106/§111, [D08 acceptance criteria](../../doc/08_ACCEPTANCE_CRITERIA.md) AC-PKG-001–003, AC-SMOKE and §72–§76.

## Global Constraints

- PyInstaller onedir is the priority release shape.
- The package must be verified in a clean Windows environment; a developer-machine run is not sufficient.
- Core startup must not require all PyTorch, Inpaint, OCR or Translation model dependencies.
- The default user data root is `%LOCALAPPDATA%/New Manga`; the package directory is not a writable data store.
- Existing user source files, Managed Copy, Lock, current/pinned Revision, SQLite data and manual content must remain safe.
- No installer, updater, signing, upload, push, CI release, schema migration or UI redesign is authorized by this Task.

## Review Focus

- Frozen `QML_PATH` and relative resource resolution must load the real four-page shell from the onedir artifact, not the source checkout.
- Qt platform plugins and QML imports must be complete on a machine without the development venv or developer PATH.
- Optional dependency absence must degrade the affected Provider without preventing Core/UI startup.
- Program-directory read-only behavior and Unicode/user-data paths must not redirect writes into the artifact or corrupt SQLite.
- Clean shutdown and restart must release process/file locks and preserve data; a successful first launch alone is insufficient.

---

### Task 1: Freeze the packaging contract

**Files:**
- Create: `packaging/new_manga.spec`
- Create: `packaging/build.ps1`
- Create: `packaging/manifest.py`
- Test: `tests/packaging/test_packaging_contract.py`
- Modify: `doc/tasks/T3.2.1.md`

**Interfaces:**
- Consumes: `src/bootstrap/app.py:main`, `src/ui/qml/Main.qml`, `requirements.txt`, `requirements-dev.txt`.
- Produces: a named onedir entry executable, a deterministic artifact directory, and a SHA-256 manifest.

- [ ] **Step 1: Write the failing contract tests**

  Create `tests/packaging/test_packaging_contract.py` with the smallest
  source-level contract:

  ```python
  from pathlib import Path

  ROOT = Path(__file__).resolve().parents[2]


  def test_spec_owns_real_entry_and_qml_tree():
      spec = (ROOT / "packaging" / "new_manga.spec").read_text(encoding="utf-8")
      assert "src/bootstrap/app.py" in spec
      assert "src/ui/qml" in spec
      assert "tests" not in spec
      assert ".pytest_cache" not in spec


  def test_build_script_requires_explicit_output_directory():
      script = (ROOT / "packaging" / "build.ps1").read_text(encoding="utf-8")
      assert "OutputDir" in script
      assert "manifest" in script.lower()
  ```

  These assertions intentionally fail at the Gate baseline because the
  production spec and build script do not yet exist.

- [ ] **Step 2: Run the contract tests**

  Run from `G:\CODEX\New Manga`:

  ```powershell
  $env:PYTHONPATH = 'src;.'
  & 'G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe' -m pytest tests/packaging/test_packaging_contract.py -q
  ```

  Expected: FAIL because no production spec or build script exists at the Gate baseline.

- [ ] **Step 3: Add the minimal spec/build/manifest seam**

  The spec must use the real bootstrap entry and explicitly collect QML and Qt
  assets. `build.ps1` must accept a fixed output path, invoke the pinned
  interpreter's `PyInstaller`, remove only its own output directory, and emit
  the exact command, dependency snapshot and manifest path. `manifest.py` must
  hash files in stable relative-path order and never traverse the data root.

- [ ] **Step 4: Run the contract tests again**

  Re-run the command in Step 2. Expected: PASS, with no generated artifact
  checked into the repository.

- [ ] **Step 5: Commit the packaging contract**

  ```powershell
  git add packaging tests/packaging doc/tasks/T3.2.1.md
  git commit -m "build(T3.2.1): define reproducible Windows package"
  ```

### Task 2: Build and inspect the artifact

**Files:**
- Modify: `packaging/new_manga.spec`
- Modify: `packaging/build.ps1`
- Modify: `packaging/manifest.py` if inspection exposes a deterministic gap
- Create: `verification/T3.2.1/build.log`
- Create: `verification/T3.2.1/artifact-manifest.sha256`
- Create: `verification/T3.2.1/artifact-inspection.log`

**Interfaces:**
- Consumes: the fixed delivery commit and the packaging venv outside the repository.
- Produces: a complete onedir artifact and reproducible inspection evidence.

- [ ] **Step 1: Create the isolated packaging venv outside the repo**

  Use `G:\CODEX\New Manga.task-envs\T3.2.1-packaging-py312`; install the exact
  requirements from `requirements-dev.txt`, and record `python --version`,
  `pip freeze`, and `pip check` in `verification/T3.2.1/build.log`.

- [ ] **Step 2: Build from the fixed head**

  Run `packaging/build.ps1` with an output directory under `%TEMP%`, with
  `PYTHONPATH=src`, and record the exit code, commit, spec path and artifact path.

- [ ] **Step 3: Inspect the artifact**

  Verify the executable, `_internal`/Qt files, `qwindows` plugin, QML modules,
  four page files and manifest. Assert no `src`, `tests`, `.git`, venv or user
  data root appears in the artifact. Record the exact file count and SHA-256.

- [ ] **Step 4: Rebuild once and compare manifests**

  Build into a second isolated temp directory with the same fixed input. Compare
  the normalized manifests and record any expected PyInstaller timestamp/path
  normalization; unexplained content differences are FAIL, not waived.

- [ ] **Step 5: Commit only reproducible packaging evidence**

  Commit the spec/scripts and evidence headers/logs; keep the binary artifact
  outside the repository unless a later explicit release decision authorizes it.

### Task 3: Verify local frozen runtime and safety

**Files:**
- Create: `tests/packaging/test_frozen_runtime_contract.py`
- Create: `verification/T3.2.1/local-smoke.log`
- Create: `verification/T3.2.1/path-safety.log`
- Modify: `src/bootstrap/**` only if the frozen resource path requires it

**Interfaces:**
- Consumes: the onedir artifact from Task 2 and an isolated data root.
- Produces: local runtime evidence; it does not replace clean-machine evidence.

- [ ] **Step 1: Pin frozen-path and data-root tests**

  Test the real entry with an explicit temp `--data-root`, verify SQLite is
  created outside the artifact, and verify an existing source fixture hash is
  unchanged. Add a process-exit assertion that the executable is gone and the
  SQLite file can be reopened after normal shutdown.

- [ ] **Step 2: Run local smoke in normal and system-only PATH modes**

  Start the packaged executable once normally and once with PATH limited to
  `%SystemRoot%\system32;%SystemRoot%`. Capture stdout/stderr, exit code,
  process list and data-root tree for both runs.

- [ ] **Step 3: Run no-heavy-model startup**

  Use an environment that has Core dependencies but no torch/large model files.
  Confirm startup reaches the shell and missing optional capability is diagnosed
  without a process crash.

- [ ] **Step 4: Commit local runtime evidence**

  Keep the local result separate from the clean-machine result and record any
  limitation as `BLOCKED` or `NOT_RUN`, never as PASS by inference.

### Task 4: Execute the clean Windows release workflow

**Files:**
- Create: `verification/T3.2.1/clean-windows-runbook.md`
- Create: `verification/T3.2.1/clean-windows-smoke.log`
- Create: `verification/T3.2.1/clean-windows-safety.log`
- Create: `verification/T3.2.1/benchmark-report.md`

**Interfaces:**
- Consumes: the fixed artifact and authorized test fixtures.
- Produces: the evidence required for AC3, AC6, AC7, AC8 and AC9.

- [ ] **Step 1: Record the test machine before installing**

  Record Windows edition/build/architecture, CPU/RAM, user privilege, clean
  state, installed Python absence, PATH, test date, artifact hash and install
  directory. Do not use the developer checkout as the clean machine.

- [ ] **Step 2: Run the complete smoke flow**

  Execute: extract/install → launch → default bookshelf → create Book → create
  Chapter → import an authorized image fixture → Workbench → Mock/Local Pipeline
  → save → Reader → export → close → relaunch → verify persisted state.
  Record every step, expected/actual result and exit code.

- [ ] **Step 3: Run safety probes**

  Hash the source fixture before/after, inspect SQLite rows and managed files,
  verify Lock/current/pinned Revision invariants, scan logs and package contents
  for credential values, and confirm no product process or file lock remains.

- [ ] **Step 4: Measure startup**

  Perform at least five cold starts on the recorded machine, exclude model
  download and first-time user restore, and report P50/P95. If the machine or
  measurement is unavailable, record BLOCKED/NOT_RUN and do not claim READY.

- [ ] **Step 5: Commit the external-run evidence**

  Commit logs and reports without copying user data, secrets or the binary into
  the repository.

### Task 5: Handoff, independent Review, and Codex integration

**Files:**
- Create: `doc/handoffs/T3.2.1-<delivery-head>.md`
- Create: `verification/T3.2.1/review-<delivery-head>.md`
- Create: `verification/T3.2.1/integration-<delivery-head>.md`
- Modify: `doc/STATUS.md`, `doc/REBASELINE_PLAN.md`, `doc/00_INDEX.md`, `doc/tasks/README.md`

- [ ] **Step 1: Prepare Handoff bound to one delivery head**

  Include allowed paths, exact base/head, package hash, all commands, shell/venv,
  PASS/FAIL/BLOCKED/NOT_RUN status, clean-machine identity and known limits.

- [ ] **Step 2: Obtain DeepSeek Harness Review**

  Review the fixed head from an independent worktree. The Review must inspect
  spec/resource closure, no-source/user-data leakage, optional dependency
  behavior, clean shutdown, safety probes, performance evidence and allowed paths.
  Any P0/P1 or missing clean-machine proof blocks approval.

- [ ] **Step 3: Integrate only after `approved`**

  Codex merges the fixed delivery with `--no-ff`, reruns applicable tests and
  `git diff --check`, then writes integration evidence. No upload, push, installer
  publication or release tag is created by this Task.

- [ ] **Step 4: Close the Task only if the Gate is satisfied**

  Set `done / VERIFIED_COMPLETE` only when the package, clean Windows smoke,
  P0/P1/data-safety evidence, independent Review and Codex integration all pass.
  Otherwise retain `ready`, `BLOCKED` or `NOT_READY` with the exact missing gate.
