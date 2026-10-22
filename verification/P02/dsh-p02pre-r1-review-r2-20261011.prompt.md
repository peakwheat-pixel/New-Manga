# DeepSeek Harness Review Task: P02PRE-R1 Round 2

请作为 P02PRE-R1 的非作者独立 Reviewer，对下列确切字节只做只读复审。不要编辑任何文件；不要运行 capture script、PowerShell query、Git query、OS/API/registry/WER/token/ACL/path/environment/hash 命令；不要 build/Cargo/AC；不要更改 Gate 或 Task 状态。可读取项目文档用于核对，但只评论，不做执行。

## Review target pins

- Repo=`G:/CODEX/New Manga`；branch=`main`；HEAD=`cddff58469b56e181019a8ddfeade80684bc7eb9`；tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`。
- Task `doc/tasks/P02PRE-R1.md`: `9028 bytes / SHA-256 6E901052AADA0242CA65EFD98E1283F789762322EEAA6956303F2CEBDA15C4C8`。
- Manifest `verification/P02/p02pre-r1-manifest-20261011.md`: `11206 bytes / SHA-256 594690BF104A657064A82C96B1E4FB3421AA37E24701799C429D0F6C55E13212`。
- Script `verification/P02/p02pre-r1-capture.ps1`: `35725 bytes / SHA-256 CAC5F08C10555F7A68C047CFA6D33287671581CB56CF9BDDE5D98243D0BA1A0D`。
- Windows PowerShell parser evidence: version `5.1.26100.9549`; parse stdout=`POWERSHELL_VERSION=5.1.26100.9549` + `PARSE_OK`, stderr empty, exit `0`. This parsed with `ScriptBlock::Create` and did not invoke the script.
- Source contract: `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`.

## User authorization and preserved Gate state

The user authorizes the P02 one-time continuous scope, including host getters, dynamic isolation, P02PRE, Build/Cargo, AC1–AC7, fixes, review, retest and integration; the user accepted residual risk for runner/source-contract and host getter absolute-no-side-effect preproof. R0 is over and static runner/source research must not be repeated. This does not convert unknown facts into PASS.

Preserve exactly: `private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`. P02PRE-R1 is only a readonly host capture. Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`. Do not query/install/enable/start Windows Sandbox.

## Round 1 result and required adjudication

Round 1 Review was `CHANGES_REQUESTED`, P0/P1/P2/P3=`0/2/6/3`. The report is `verification/P02/dsh-p02pre-r1-review-20261011.md`. Codex accepted all 11 findings; the revised code/manifest now claims to address them as follows. Independently check the actual pinned files; do not trust this summary.

1. P1 evidence over 64 MiB: produce a bounded `PARTIAL_EVIDENCE` to the same one `CREATE_NEW` output, retaining explicit stop reason, classification, repo state, status SHA/byte count/NUL count, bounded inventory records and omitted counts; if still over limit, preserve a minimal partial summary. No retry/cleanup.
2. P1 raw Git status bytes: `BaseStream.CopyToAsync` captures raw stdout bytes; SHA-256/Base64/length/NUL count derive from those bytes. Human-readable Git stdout uses replacement UTF-8 only; inventory parsing is strict UTF-8.
3. P2 home: record `HOMEDRIVE+HOMEPATH`, normalize and compare with host `USERPROFILE`; future LPAC `scratch	mphome` is explicitly not applied in R1. Even host-home consistency `PASS_WITH_EVIDENCE` must not make `tempCache` PASS.
4. P2 query/ACL stop: top-level per-class query error counts and fail-stop on getter errors, ACL endpoint changes or incomplete hash; record which WER scope is deliberately not enumerated and label access/child/write closure unprovable because R1 has no OS monitor.
5. P2 reparse: each root and every ancestor component, including drive root and `.git` metadata paths, is checked component by component and stops on reparse/query error.
6. P2/P2 hive/view: readable enum name plus numeric value.
7. P2 Git metadata: explicitly aggregate `.git/HEAD/index/config` states and compare index pre/post hash.
8. P3 serialization: preserve `stopReason` and attempt bounded/minimal evidence outside `finally`; no rethrow that silently masks an existing stop.
9. P3 WER last-write: explicitly emit `NOT_AVAILABLE_BY_GETTER`.
10. P3 NUL counts: field is `nulSegmentCountApprox` and defines one terminator per record under `--no-renames`.
11. The report had 11 total findings; the above bullets group the precise requested fixes. Please cross-reference every P1/P2/P3 finding in Round 1 and explicitly mark each `CLOSED`, `PARTIALLY_CLOSED`, or `OPEN` with evidence line references. If any finding needs more nuance than this grouped list, state it.

## Independent scope review

Read the full pinned Task, manifest and script. Compare every query path, registry hive/view/value, environment variable, child executable/argument, write, hash target, stop path, and partial serialization branch against R6 and Task. Confirm Windows PowerShell 5.1 compatibility beyond parser syntax if possible. Check for new false PASS semantics: effective access, TEMP/cache/scratch mapping, actual WER policy, absent-object ACL, profile/private-registry store, transient ACL writes and child/path access closure must remain unknown unless actually proved. Ensure no expansion into unlisted paths, writes, profile API, ACL/registry mutation, canary, build/Cargo, AC, Sandbox, or user file content.

State exactly what you reviewed and could not review. The round-1 Reviewer could not independently hash the files because their sandbox ACL setup failed (Win32 5); if your environment has the same limit, report it without claiming hash verification. Static review/parser evidence does not prove the host state or any runtime condition.

Return a Chinese report with exactly one result from `APPROVED`, `CHANGES_REQUESTED`, `NOT_VERIFIED`, `BLOCKED_BY_MISSING_EVIDENCE`; counts P0/P1/P2/P3; findings with precise file/line, trigger, impact and concrete fix; disposition of each Round 1 finding; scope coverage/limits; and whether the exact pinned readonly capture may be released for one invocation. `APPROVED` is a review decision only and does not pass any Gate.