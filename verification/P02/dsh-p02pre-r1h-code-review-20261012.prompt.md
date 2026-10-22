# P02PRE-R1H Frozen Candidate Independent Review

Role: non-author code/security Reviewer. Owner=Antigravity; root Codex is Integrator/Adjudicator. Review exact branch=`agent/antigravity/P02PRE-R1H`, base=`946938bd0696dfddd01f87d61fe6723c63ecdc86`, reviewed HEAD=`256e3ea622cba7a658020ddcf015b18894d88b38` in the current project worktree.

## Read-only allowlist

Read only these seven frozen files, each exactly once if practical:

1. `G:\CODEX\New Manga\doc\tasks\P02PRE-R1H.md`
2. `G:\CODEX\New Manga\verification\P02\p02pre-r1h-manifest-20261012.md`
3. `G:\CODEX\New Manga\verification\P02\p02pre-r1g-manifest-20261011.md`
4. `verification/P02/p02pre-r1h-capture.ps1`
5. `verification/P02/p02pre-r1h-selfcheck.ps1`
6. `verification/P02/p02pre-r1h-handoff-20261012.md`
7. `verification/P02/p02pre-r1g-capture.ps1` (compare only relevant inventory decision, launcher and output contract)

## Review scope

Independently determine whether the new branch is narrow, fail-closed and consistent with Task/manifest. In particular:

- For Git stage/index mode=`120000` and an ordinary non-directory non-reparse leaf, is path-only skipping justified by prior frozen checks? Does it avoid every content read/hash, target resolution/follow, ACL query and child enumeration for that leaf? Does code record the representation and skip before all later operations?
- Do genuine reparse symlinks remain no-follow; do wrong mode, wrong stage, regular-mode reparse, directory/device/unknown objects and repository refs/index/status drift stop?
- Can a mismatch or an unclean repository reach the new skip? Could the new logic mask unrelated working-tree/user-file changes or broaden inventory exclusions?
- Are phase/status/error fields accurate and bounded? Do outputs use distinct R1H names and `CreateNew` without overwriting R1G outputs? Are child executable/argv/path/API/write allowlists unchanged?
- Does the self-check exercise both symlink forms, regular files and illegal combinations, and assert control flow before hash/ACL/enumeration? Is it itself isolated from capture and host APIs?
- Identify any product/security risk in Task or manifest, including an unsafe blanket skip. R1G technical limitations stay explicit.

## Strict limitations

This is content-only Review. Do not run commands, PowerShell, Git, tests, parser, self-check, capture, getters, hashes, glob/grep/search, directory enumeration, or other tools. Do not write files. Do not inspect any path other than the seven allowlisted files, especially never access `.tmp.driveupload`. Do not claim any runtime, gate, write-closure or AC PASS. The requested hash check is performed by root Codex, not Reviewer.

## Response

Return a concise Markdown report with verdict=`APPROVED` / `CHANGES_REQUESTED` / `BLOCKED`, P0-P3 counts, exact findings with file/line and triggering condition, Task/manifest fidelity, what was/was not independently checked, and minimum safe next step. If anything cannot be established from the frozen content, say `NOT_VERIFIED`.