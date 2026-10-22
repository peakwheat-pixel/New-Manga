# ZCode Dispatch：P02PRE-R1H-R6-EXEC-A6

## Assignment

Task: doc/tasks/P02PRE-R1H-R6-EXEC-A6.md
Owner: ZCode
Reviewer: DeepSeek Harness (non-author, independent static Review)
Integrator/Adjudicator: Codex /root
Repository: G:\CODEX\New Manga
Base HEAD: 343895fb5f0329c0c07a7104ec321b698f967607
Working tree: C:\Users\49745\.codex\worktrees\p02pre-r1h-attempt6-zcode\New Manga
Branch: agent/zcode/P02PRE-R1H-R6-EXEC-A6

## Work

Read the attached current AGENTS, REBASELINE_PLAN, STATUS, collaboration protocol, P02 parent Task, A6 Task, A5/A4 source artifacts, A5 Review/adjudications, checkpoint, and the actual Owner Handoff. The root has original-author uncommitted data; these attachments are read-only references. The A6 worktree intentionally starts at the frozen base and does not contain root dirty files. Do not copy those files into the worktree.

Implement the A6 Task with the smallest change that fully addresses every accepted A5 adjudication finding. Write only these three paths in the working tree:

- verification/P02/p02pre-r1h-round6-integrator-attempt6-20261012.ps1
- verification/P02/p02pre-r1h-round6-integration-protocol-attempt6-20261012.md
- verification/P02/p02pre-r1h-round6-attempt6-exec-handoff-20261012.md

Treat every A4/A5 source, Task, manifest, adjudication, checkpoint, and Owner Handoff attachment as immutable input. In particular, bind the actual Owner Handoff bytes from the attached file; preserve separate source Parser/in-memory evidence and executor runtime selfcheck/engine states; include an immutable review-contract snapshot and pinned checkpoint; record observed/expected SDDL or NOT_VERIFIED; retain .tmp.driveupload as NOT_VERIFIED; distinguish pre-write output absence, Codex disposition, and process exit; and never claim unobserved post-fail-stop state is unchanged.

You may run only a PowerShell 7.6.6 Parser-only syntax check on the new executor. Do not dot-source or invoke any executor, selfcheck, capture, OS/API, child-process test, registry/profile/ACL operation, Build/Cargo, or AC1–AC7. Do not access .tmp.driveupload. Do not write tests or evidence files outside the three-path allowlist. Do not change Task, Plan, STATUS, index, checkpoint, or review inputs. Do not merge or write to the main worktree.

Return a fixed delivery HEAD and Handoff, exact changed-path list, commit(s), Parser command/environment/result, git diff --check result, every AC outcome, and any blocker. If the requested edit permission is denied, stop and report; do not switch to a broader permission mode.
