# Library Module Documentation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create an architecture-focused `library.md` that documents the current library application module, its UI consumers, persistence adapter, dependencies, data flows, and verification evidence.

**Architecture:** Trace the library boundary from QML-facing bookshelf models/ViewModel through `LibraryService` and repository ports to the SQLite adapter, then show adjacent import, navigation, reader, workbench, and bootstrap relationships without duplicating their module documentation. Mark implementation facts and known gaps separately.

**Tech Stack:** Markdown, Mermaid, Python/PySide6/QML, SQLite, pytest.

**Spec:** User request in the current conversation; repository rules in `AGENTS.md`, `doc/REBASELINE_PLAN.md`, `doc/00_INDEX.md`, `doc/STATUS.md`, and `doc/09_COLLABORATION.md`.

## Global Constraints

- Treat `doc/REBASELINE_PLAN.md` as the sole sequencing source and `doc/STATUS.md` as the live state checkpoint.
- Document the current implementation, not planned capability; label gaps and blocked paths explicitly.
- Preserve layer direction `QML/UI → Application → Domain/Ports → Infrastructure`.
- Link to companion module documentation instead of duplicating its internal design.
- Write only the requested documentation area and preserve unrelated dirty files.

## Review Focus

- Library service versus repository responsibilities: diagrams and tables must not imply SQL in the application layer.
- Soft-delete and source-file safety: deletion/import flows must preserve the managed-copy boundary.
- UI projection versus domain truth: list-model roles and ViewModel state must be identified as projections.
- Adjacent workflow hand-offs: library context must flow to navigation, reading, workbench, and importing without inventing a second state store.
- Evidence accuracy: links, source paths, test commands, and baseline status must match files present in the current checkout.

### Task 1: Analyze the library slice and existing documentation

**Files:**
- Read: `src/application/library/errors.py`
- Read: `src/application/library/ports.py`
- Read: `src/application/library/service.py`
- Read: `src/infrastructure/sqlite/library.py`
- Read: `src/ui/models/library/models.py`
- Read: `src/ui/viewmodels/bookshelf/viewmodel.py`
- Read: `src/ui/viewmodels/navigation/viewmodel.py`
- Read: `src/bootstrap/app.py`
- Read: focused library/UI tests and companion `wiki/codewiki/*.md` files

**Interfaces:**
- Consumes: current source code, tests, project docs, and existing wiki conventions.
- Produces: verified component responsibilities, dependency edges, data-flow facts, and safe cross-document links.

- [x] **Step 1: Inspect the project baseline and dirty-worktree ownership.**
- [x] **Step 2: Trace library callers, adapters, UI projections, and tests.**
- [x] **Step 3: Compare existing wiki documents for structure and link conventions.**

### Task 2: Write the module documentation

**Files:**
- Create: `wiki/codewiki/library.md`

**Interfaces:**
- Consumes: Task 1's verified code and repository facts.
- Produces: a standalone architecture document with Mermaid architecture, dependency, component, data-flow, and process-flow diagrams; module API tables; persistence/safety boundaries; failure behavior; current gaps; verification; and maintenance guidance.

- [x] **Step 1: Add a brief introduction and module boundary.**
- [x] **Step 2: Add architecture and dependency diagrams with source-linked component tables.**
- [x] **Step 3: Add library CRUD, import, navigation, and persistence data-flow/process diagrams.**
- [x] **Step 4: Link to companion docs and project source-of-truth documents instead of duplicating their details.**
- [x] **Step 5: Separate current behavior from roadmap gaps and record verification commands.**

### Task 3: Validate the documentation artifact

**Files:**
- Read: `wiki/codewiki/library.md`

**Interfaces:**
- Consumes: the generated Markdown document and repository file layout.
- Produces: a link-valid, source-grounded documentation artifact with no unrelated file changes.

- [x] **Step 1: Check the document exists and has the required sections/diagrams.**
- [x] **Step 2: Resolve every relative source/document link against the repository.**
- [x] **Step 3: Review the diff and confirm unrelated dirty files remain untouched.**
