# P19-UI-FIX-3 Blocker Checkpoint r1

- **Timestamp:** 2026-10-17 19:44:46 Asia/Shanghai
- **Agent / Task:** Codex / P19-UI-FIX-3
- **TaskStatus / ExecutionState:** `blocked` (previous status `ready`) / `CHECKPOINTED`
- **Branch / Worktree:** `codex/P19-UI-FIX-3` / `G:/CODEX/New Manga.workspace/worktrees/P19-UI-FIX-3`
- **Start commit / current HEAD:** `9e152b6312e75be5e7381b6a6be021aa7e6a9060` / `9e152b6312e75be5e7381b6a6be021aa7e6a9060`
- **Working tree:** Started clean. This checkpoint and the Task status/evidence update are the only changes; no production code was edited.

## Completed steps

- Read the Rebaseline Plan, document index, STATUS, collaboration protocol, P19-UI-FIX-3 Task, and the required P19 verification records.
- Confirmed the linked worktree, branch, common Git directory, base HEAD, and clean starting tree.
- Checked the contract, exhaustive production host command allowlist, and Core dispatcher for a frozen create-work/create-chapter command.

## Blocker and evidence

- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md:139` lists `CreateBook` in the §5 proposal catalog; line 141 says `CreateChapter` remains PROPOSAL; line 158 freezes only the read-only `list_chapters` projection.
- `apps/desktop/src-tauri/src/main.rs:71` registers `library_list_books`; line 110 registers `list_chapters`. The production command list has no create-work or create-chapter command.
- `src/bootstrap/core_service.py:3080-3086` dispatches only `list_chapters` / `list_chapter_pages` in the navigation handler; no create handler exists there.
- The Legacy Qt methods in `src/ui/viewmodels/bookshelf/viewmodel.py:287,313` do not provide the required React/Tauri host→Core path and are outside the allowed implementation paths.
- Pre-fix GUI evidence is recorded in `verification/P19/create-work-and-import-r6.md`: `+ 新建作品` was `IsEnabled=False`, and UIA Invoke threw. No post-fix GUI evidence exists because implementation stopped at the hard gate.

## Tests and AC status

- **Tests already run:** None. No frontend test, `npm run build`, sidecar build, or Cargo build was run after the gate check.
- **Tests remaining:** New empty-shelf create test; frontend regression suite (274 baseline); `npm run build`; sidecar build; `cargo build` and bundle/resource hash comparison; isolated-root real GUI/UIA flow.
- **AC1–AC3:** BLOCKED by missing frozen CreateBook/CreateChapter command and host/Core implementation.
- **AC4–AC6:** NOT_RUN / BLOCKED; there is no implementation to test, package, revalidate in GUI, or hand off.

## Resume point

- **Next exact step:** Coordinator releases a contract task for CreateBook/CreateChapter and a host/Core implementation task with explicit allowed paths. After that work is integrated, re-scope and resume P19-UI-FIX-3.
- **Resume safety:** `RESUME_SAFE`; HEAD is unchanged, and no source, user data, package, or test output was modified. The only working-tree changes are this checkpoint and the P19-UI-FIX-3 blocker record.
- **Confidence:** High that the hard gate is hit: the current contract proposal status and production command surfaces provide no frozen create wire.
