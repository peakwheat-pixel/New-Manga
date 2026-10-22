# Codex Post-Integration Pure Selftest Run Record r1

Task：`P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION`
Owner：Codex；parent branch=`agent/zcode/P02-NEW-TIME-BASELINE`；integration commit=`50c60755a59a714729b8371b07acce9ff535a3c1`；tree=`55fbd3ff5bf6580e80c300c0e064bf894372a297`

## Command and environment

- Command：`pwsh -NoProfile -File tools/p02/p02-new-time-baseline-selftest.ps1 -Stamp 20261014-054650-integration-50c60755`
- Working directory：`G:/CODEX/New Manga.workspace/worktrees/P02-NEW-TIME-BASELINE`
- PowerShell=`7.6.6 Core / FullLanguage`; executable=`C:/Program Files/PowerShell/7/pwsh.exe`。
- Start/end UTC：`2026-10-13T21:45:09.2756321Z` / `2026-10-13T21:45:10.7935236Z`。
- Fixture directory：`G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-BASELINE/20261014-054650-integration-50c60755-pure-selftest/`；`3` files / `105` bytes; file list/size/hash=`post-integration-selftest-fixture-inventory-r1.json`。

## Result

- Exit=`0`; assertions=`220 PASS / 0 FAIL / 7 SKIP`; stderr empty. All seven named skips and reasons are in the full stdout.
- Collector/live query, Git child, whoami child, history input, X6, post-run Review, Build/Cargo, product AC1–AC7, and Windows Sandbox were not run. No collector RunId was created or reused.
- Full stdout/stderr/exit are pinned in `post-integration-selftest-r1.stdout.log`, `post-integration-selftest-r1.stderr.log`, and `post-integration-selftest-r1.exit.txt`; raw copies are preserved in the Task `agent-output` directory.