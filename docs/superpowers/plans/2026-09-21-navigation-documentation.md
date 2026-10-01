# Navigation Module Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create an architecture-focused `navigation.md` that documents the current application navigation state holder, its QML bridge, bootstrap wiring, sibling-module hand-offs, data flows, and verification evidence.

**Architecture:** Trace the boundary from `NavigationService`'s process-local four-route state through `NavigationViewModel` to the QML shell. Show Bookshelf and Workbench as command producers, bootstrap as the validated context synchronizer for Reader, Workbench, and standalone Export, and link to existing UI module documents instead of duplicating their internals.

**Tech Stack:** Markdown, Mermaid, Python, PySide6, QML, pytest.

**Spec:** User request in the current conversation; repository rules in `AGENTS.md`, `doc/REBASELINE_PLAN.md`, `doc/00_INDEX.md`, `doc/STATUS.md`, and `doc/09_COLLABORATION.md`.

## Global Constraints

- Treat `doc/REBASELINE_PLAN.md` as the sole sequencing source and `doc/STATUS.md` as the live state checkpoint.
- Document the current implementation, not planned capability; label gaps explicitly.
- Preserve the layer direction `QML/UI → Application → Domain/Ports → Infrastructure`.
- Link to companion module documentation instead of copying its internal design.
- Preserve unrelated dirty/generated files and write only the requested documentation artifacts.

## Review Focus

- Four-route invariant: the document must distinguish route validation from page-specific content.
- Context ownership: navigation carries IDs and optional reader resume data but does not load or validate domain objects.
- Persistence boundary: navigation is process-local and must not be described as database-backed.
- Bootstrap hand-offs: Reader, Workbench, and standalone Export consumers must be connected to the correct signals.
- Evidence accuracy: source links, test paths, and verification commands must match the checkout.

### Task 1: Analyze the navigation slice

**Files:**
- Read: `src/application/navigation/service.py`
- Read: `src/ui/viewmodels/navigation/viewmodel.py`
- Read: `src/bootstrap/app.py`
- Read: `src/ui/viewmodels/bookshelf/viewmodel.py`
- Read: `src/ui/viewmodels/workbench/viewmodel.py`
- Read: `src/ui/qml/shell/AppShell.qml`
- Read: `src/ui/qml/shell/PrimaryNavigationRail.qml`
- Read: focused navigation tests and companion `wiki/codewiki/*.md` files

**Interfaces:**
- Consumes: current source code, tests, project docs, and existing wiki conventions.
- Produces: verified route/state contracts, dependency edges, hand-off behavior, and source-grounded links.

- [x] **Step 1: Inspect the baseline and dirty-worktree ownership.**
- [x] **Step 2: Trace service callers, Qt properties/signals, bootstrap consumers, and QML bindings.**
- [x] **Step 3: Compare existing module documents and verify relative-link conventions.**

### Task 2: Write the module documentation

**Files:**
- Create: `wiki/codewiki/navigation.md`

**Interfaces:**
- Consumes: Task 1's verified code and repository facts.
- Produces: a standalone architecture document with introduction, scope, Mermaid architecture/dependency/component/data-flow/process diagrams, API tables, failure behavior, verification, and companion links.

- [x] **Step 1: Add the application-layer boundary and current-state summary.**
- [x] **Step 2: Add architecture, dependency, and component diagrams with source-linked tables.**
- [x] **Step 3: Add route/state invariants and Reader/Workbench hand-off process flows.**
- [x] **Step 4: Link to UI, library, reader, workbench, export, and project source-of-truth documents.**
- [x] **Step 5: Record safety boundaries, limitations, and focused verification commands.**

### Task 3: Validate the documentation artifact

**Files:**
- Read: `wiki/codewiki/navigation.md`

**Interfaces:**
- Consumes: the generated Markdown document and repository file layout.
- Produces: a link-valid, source-grounded documentation artifact with no unrelated file changes.

- [x] **Step 1: Check required sections and Mermaid diagrams are present.**
- [x] **Step 2: Resolve every relative source/document link against the repository.**
- [x] **Step 3: Review the diff and confirm unrelated dirty files remain untouched.**
