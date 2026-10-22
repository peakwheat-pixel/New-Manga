# DeepSeek Harness Review Task: P02PRE-R1

请作为本 Task 的非作者独立 Reviewer，只做只读审查；不要修改文件，不要运行 capture script、PowerShell query、Git query、OS/API/registry/WER/token/ACL/path/environment/hash 命令，不要 build/Cargo/AC，不要改 Gate 或 Task 状态。

## Review target pins

- Repo=`G:/CODEX/New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Task `doc/tasks/P02PRE-R1.md`: `6050 bytes / SHA-256 1D8B0639A7B24D3331F2172BC6FADD78A1AEC20B7BF41B89DCE487E70EE6C64A`。
- Manifest `verification/P02/p02pre-r1-manifest-20261011.md`: `9085 bytes / SHA-256 36BDD2BE4129DA5F5392AE6F2C1523A47020DDABCBAE5567300B5DF468E86921`。
- Script `verification/P02/p02pre-r1-capture.ps1`: `19113 bytes / SHA-256 01D70CD7A049231AE187379F5D5B1963E9775C078AC437D9FDF65BB7F7EB646A`。
- Source constraints: `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`.
- Governance context: `doc/REBASELINE_PLAN.md`, `doc/STATUS.md`, `doc/09_COLLABORATION.md`, `doc/tasks/P02.md`.

## User authorization context

The latest user decision authorizes the existing P02 one-time continuous scope, accepts the remaining absolute-no-side-effect preproof risk for runner/source-contract and host getters, ends R0, and permits host dynamic validation, P02PRE, Build/Cargo, AC1–AC7, fixes, Review, retest and integration. It does not convert unknown facts into PASS. Preserve `private_registry_absence=UNPROVABLE`, Technical Gate=`NOT_SATISFIED`, Owner Risk Acceptance=`APPROVED`, Gate Disposition=`WAIVED_BY_OWNER`, Build Authorization=`AUTHORIZED_WITH_EXCEPTION`, and `technical condition unmet; user explicitly accepted residual risk`. Product Build Gate and Hard Build Barrier stay blocked until evidence and Codex adjudication. Do not query/install/enable/start Windows Sandbox.

## Review scope

Independently read the complete pinned Task, manifest and script, and only the referenced r6/governance material needed to check exact paths, API and query scope, evidence behavior, process behavior, protection of user data and compatibility with Windows PowerShell 5.1/.NET Framework. Check the script against every frozen query and file-write constraint. Identify any path or process outside the allowlist; overwrite/truncation, partial evidence or reparse behavior; bad Git argument/path handling; exception/reporting errors; incorrect classification; or mismatch between the Task, manifest and code. Confirm whether this precise host-only preflight can be safely reviewed and, if approved, released for one invocation.

Do not rely on the author’s summary. Report an exact result from `APPROVED`, `CHANGES_REQUESTED`, `NOT_VERIFIED`, `BLOCKED_BY_MISSING_EVIDENCE`; give P0/P1/P2/P3 counts and findings with file/line, trigger, impact and concrete fix. State review coverage and anything not checked. Static review is not evidence that the script ran or that any OS condition passed. Return the review in Chinese.
