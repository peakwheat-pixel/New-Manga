# T2.2.1 Reader & Workbench Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the existing Reader and Workbench context-entry paths reachable and understandable without adding a page, backend store, or new command paradigm.

**Architecture:** Reuse the already published `bookshelfViewModel` and `navigationViewModel` context properties. A shared QML picker may read the existing book/chapter list models and call the existing navigation slots; it must not construct a database, file store, or new application service. Keep command-error production in `WorkbenchViewModel`; this Task only makes the existing error surface accessible, token-consistent, and dismissible.

**Tech Stack:** PySide6/QML, existing ViewModels and Qt Quick Controls, pytest/QML harnesses.

**Spec:** `doc/REBASELINE_PLAN.md` order 5, `doc/05_UI_MAPPING.md` §§15–20, §§37–42, §54, `doc/contracts/UI_UX_GUI_DESIGN.md` §6C and §7.2, and the deferred findings in `verification/T2.1.1/review-bc49ef9.md`.

## Global Constraints

- Preserve the four top-level pages: Bookshelf, Workbench, Reader, Settings.
- QML may consume ViewModel context properties, but must not access databases, files, providers, or construct models/services.
- Use the existing `src/ui/qml/theme/Tokens.qml` source for colors, spacing, sizes, radii, and status semantics; do not introduce a parallel palette or literal design system.
- Reuse `bookshelfViewModel.bookListModel`, `bookshelfViewModel.chapterListModel`, `bookshelfViewModel.selectBook`, `bookshelfViewModel.enterTranslation`, `bookshelfViewModel.enterReading`, and the existing navigation slots unless a concrete failing test proves a minimal seam is missing.
- Do not implement E command-palette behavior, C glass, D top navigation, Region six-state rendering, theme persistence, storage migration, or packaging in this Task.
- Protect source files, Managed Copy, databases, current/pinned revisions, locks, and existing agents' dirty files/worktrees.
- Every recorded test result must include shell, interpreter/venv, counts, skip reasons, and exit code; discriminating mutation evidence must be an artefact.

## Review Focus

- Picker selection must not silently operate on a stale book/chapter model after the user changes the book; test the model refresh and selected chapter handoff.
- Empty states must remain honest when no ViewModel/context exists; test disabled/hidden actions and standalone QML loading.
- Dismissal must clear the held command error and hide the surface without changing run state; test a visible error, dismissal, and a mutation that would break the assertion.
- Webtoon and paged viewers must use the same canvas ground while preserving width-fit, natural-height, and scroll-offset behavior; test the production QML source, not only a fixture.
- Keyboard/focus and modal dismissal must not create a second page or bypass existing dirty/error confirmation paths.

### Task 1: Freeze functional seams and red tests

**Files:**
- Modify only the smallest existing ViewModel/test files proven necessary by the tests; default expected production write set is empty because the existing navigation and bookshelf slots already cover the required handoff.
- Test: `tests/ui_shell/**`, `tests/workbench/**`, `tests/reading_export/**` as needed for non-QML seam and regression coverage.
- Evidence: `verification/T2.2.1/**`.

**Interfaces:**
- Consumes the existing `BookshelfViewModel`, `NavigationViewModel`, `ReaderViewModel`, and `WorkbenchViewModel` slots/properties.
- Produces explicit test expectations for Task 2. No new shared interface, bootstrap registration, Schema, or dependency is authorized by this plan.

- [ ] **Step 1: Record the fixed base and inspect existing seams.** Confirm the current master base, dirty-file inventory, the existing QML object names, and the real bootstrap context properties before writing a test.
- [ ] **Step 2: Add only discriminating functional tests.** Pin selection refresh, navigation handoff, honest empty state, and command-error clear semantics using the existing test helpers. If all seams are already covered, record the result and do not add duplicate tests.
- [ ] **Step 3: Run the new focused tests.** Use the repository's Python 3.12 venv with `PYTHONPATH=src`, record the red/green result and exit code, and keep the mutation/fixture output under `verification/T2.2.1/`.
- [ ] **Step 4: Commit the smallest functional/test change.** The commit must not include QML visual implementation or governance files.

### Task 2: Implement Reader and Workbench QML polish

**Files:**
- Create or modify only `src/ui/qml/common/**`, `src/ui/qml/reader/**`, and `src/ui/qml/workbench/**` for the shared picker, Reader chapter action, Workbench empty-state action, command-error surface, and webtoon canvas ground.
- Test: `tests/ui_shell/**`, `tests/workbench/test_qml_*.py`, and `tests/reading_export/test_qml_contract.py` for the corresponding QML behavior.
- Evidence/Handoff: `verification/T2.2.1/**`, `doc/handoffs/T2.2.1-*.md`.

**Interfaces:**
- Consumes the Task 1 expectations and existing context properties; no new Python bootstrap contract.
- Produces an object-name-addressable, keyboard-usable picker and command-error surface while preserving existing four-page navigation and workbench object names.

- [ ] **Step 1: Implement the shared picker with existing models.** It must distinguish book selection from chapter selection, refresh chapter rows after book selection, expose an empty state, support Escape/close, and call only existing slots on accept.
- [ ] **Step 2: Enable Reader and Workbench entry points.** `readerPickChapter` opens the picker and enters the selected chapter; `workbenchPickContext` opens the same picker and enters the Workbench context. No-context standalone loads remain honest and must not dereference absent ViewModels.
- [ ] **Step 3: Polish the command-error surface.** Preserve `commandErrorText` and `clearCommandError`; use F tokens, accessible labels/object names, a visible held-error state, and a dismiss action. Do not change run/error generation semantics.
- [ ] **Step 4: Fix the webtoon canvas ground.** The production `Flickable` must use the same `Tokens.bgCanvas` ground as the paged viewer without changing tile geometry, width-fit, natural height, or scroll persistence.
- [ ] **Step 5: Add mutation-backed QML tests.** Cover opening/closing, selection handoff, no-context state, command-error dismissal, and webtoon ground. Include a mutation that fails when the guard is weakened.
- [ ] **Step 6: Run focused tests and compile checks, then commit.** Record exact shell/venv/counts/skips/exit code and create the fixed delivery Handoff; do not merge `master`.

### Task 3: Non-author review and Codex integration

**Files:** Codex-only governance and integration evidence under `doc/tasks/T2.2.1.md`, `doc/STATUS.md`, `doc/REBASELINE_PLAN.md`, and `verification/T2.2.1/**`.

- [ ] **Step 1: Review the fixed implementation head against this plan, the Task AC, the full affected call chain, Architecture, and Verification.** Use a generated diff package and record all findings.
- [ ] **Step 2: Resolve P0/P1 findings through the implementer and scoped re-review.** Do not fix author findings directly in the controller session.
- [ ] **Step 3: Integrate serially on `master` only after review approval.** Preserve source history, rerun affected focused tests, compileall, bootstrap smoke, full suite, and diff checks.
- [ ] **Step 4: Update Task/STATUS/Plan/evidence and mark `VERIFIED_COMPLETE` only when AC, independent review, integration, and post-integration verification all pass.**

## Completion Gate

T2.2.1 is complete only when the picker, Workbench empty-state entry, dismissible command-error surface, and webtoon canvas consistency each have executable evidence; no P0/P1 finding remains; author Handoff and verification artefacts are committed; Codex integration and post-integration tests are recorded with exit codes; and all unrun or environment-blocked checks remain explicitly labelled.
