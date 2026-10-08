P01 read-only execution preflight. This session was launched with working directory G:\CODEX\New Manga, the canonical repository workspace. The exact reviewed candidate is in the linked worktree G:\CODEX\New Manga.worktrees\P01-metadata-audit-codex at commit 06f52f5a644079afeb57abb38f0ac674c02531c8, tree d868ecf40b4724227b74686e666f6005428e7b88, with base 826bea12a132c5af2ac0cd1244d00e9170093c71.

Do not modify any files, Git index, branches, worktrees, DSH settings, or repository state. Do not run a formal review in this preflight. Report only command, working directory/path, exact result, and exit code.

From the current workspace, test whether the exact linked worktree path is accessible to this DSH process. Run:
1) Get-Location and Test-Path for the exact linked worktree.
2) cmd /c dir for the exact linked worktree root.
3) git -C "G:\CODEX\New Manga.worktrees\P01-metadata-audit-codex" rev-parse HEAD; expected exact C7 SHA above.
4) git -C the same path show -s --format=%T HEAD; expected exact tree SHA above.
5) git -C the same path status --porcelain=v1 --no-optional-locks; expected empty.
6) git -C the same path merge-base --is-ancestor 826bea12a132c5af2ac0cd1244d00e9170093c71 06f52f5a644079afeb57abb38f0ac674c02531c8.
7) git -C the same path diff --check 826bea12a132c5af2ac0cd1244d00e9170093c71..06f52f5a644079afeb57abb38f0ac674c02531c8.
8) Run the exact validator by absolute path: python -B -X utf8 "G:\CODEX\New Manga.worktrees\P01-metadata-audit-codex\verification\PROJECT-ROADMAP-20261008\verify_plan.py". State whether the script path used was the P01 linked worktree and give its exit code.

If the target path is denied/missing, classify its commands as NOT_RUN or FAIL as appropriate and do not substitute the canonical main checkout. If all checks work, report that this proves read-only execution access only; it does not approve the P01 Review. Keep the final answer concise and do not include private chain-of-thought.