# H2-RUN frozen preflight R1

Freeze time UTC: 2026-10-13T10:13:50Z
Task: P02PRE-R1H-H2-RUN
State: ready / CODEX_H2_RUN_READY_FROZEN
Collector invocation has not occurred. The unique output target was absent when Attempt 2 ran; the one-shot launcher rechecks absence immediately before starting.

## Exact source and review gate

- Collector delivery commit: a4766131ba7962583a846117e123fb3376ca37de.
- Isolated integration commit: 1924fbb4fbff6044205e4f8b52adb6aaff879e2a, based on 343895fb5f0329c0c07a7104ec321b698f967607.
- Collector source SHA-256: 69dbe8ffd57a4e182f6f79817d2351d519724f69188f2ea7840da187714edc61.
- Pure selftest source SHA-256: e7ad2b19508d8aae0943e4b42e6830d6fc16bec53b757b62d745c017645ad96c.
- DSH R7 exact-head source Review: APPROVED_STATIC_CONTENT, 0 P0–P3 findings; report SHA-256 b3ff51a9fd499a1eb0067846cc8b83f03e5759f23cfe1468d9f547325f9be233.
- Codex post-review verification: 20/20 inputs match; SHA-256 e5a7057f0f9e5caea48cad48941333285b598a7b10f1340c30efba51fc5b1a3d.
- Codex adjudication: APPROVED; SHA-256 c0d5236f6937ac518d8d862975a050ca86a62b980ed58a4c39ae6081e27150ce.
- Isolated integration verification: Parser 0 errors; pure selftest 200 PASS / 0 FAIL / 6 SKIP; report SHA-256 13939aea005629c591974fa07befd08c34e9f716eee19bd85eea04a6789c1a7d. Collector and selftest source hashes match the reviewed pins.

## Live preflight

Attempt 2 returned PASS_READY_GATE with 43/43 checks passing. Its source pin set has 11/11 entries matching expected bytes and SHA-256; all 4 R7 review/integration artifacts match their pins. The exact JSON and helper outputs are retained under:

G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/preflight2-h2-20261013-de77a42fccca4193925767ba4e414970

- preflight.json: 156261 bytes; SHA-256 1333b1e74e4a5a90752c744c151b812410a4ba2d22a842678991f8b104add929.
- freeze-preflight.ps1: 21274 bytes; SHA-256 38f50803b16169746243e5673ac9bcb8a55fb10d7d2d24bb8418a7d08e46b223.
- preflight stdout: 527 bytes; SHA-256 649e4d66f61e16ed7f0bc7207e7148c4de8e78baf6f790e7581be7eb40dc060a. stderr: 0 bytes.
- Root branch/ref and HEAD are main / 343895fb5f0329c0c07a7104ec321b698f967607; tree e12bd627c307d4bf3c851dc09d0b82f97c86ec63; .git/index SHA-256 C5CA88842173A8FE4B9C6B6B675528347EECBDC73F85600ABA06F11E3A692B68 (973207 bytes).
- At Attempt 2, root working-tree status was captured as raw bytes only: 91772 bytes, 1315 NUL delimiters, SHA-256 aaaaf307a4fb0835a76526cdd80f911a65a7a214adc6fb722b5b91b79de20e85. Later scoped Task/STATUS/Plan/checkpoint edits intentionally changed the root status; no pre-existing listed path was enumerated, staged, changed, or cleaned. The live collector will record the current status. Root HEAD/ref/index remain the frozen invariants.
- Candidate ref/head: refs/heads/agent/codex/P02PRE-R1H / c1cc26811ea0c7e0690b49e6b8f2edbf4c55987d; status empty.
- A6 ref/head: refs/heads/agent/antigravity/P02PRE-R1H-R6-EXEC-A6 / 343895fb5f0329c0c07a7104ec321b698f967607; the frozen expected status is exactly 3 untracked records / 220 bytes, SHA-256 3f422059515c896b0633087f3e6a052e18f4de8c556e38e5cdd5ccc06b6de083.
- PowerShell 7.6.6 Core FullLanguage, fixed executable/home and non-admin identity checks passed. Output parent chain is ordinary with no reparse points; G: is ready NTFS. Seven fixed executor targets were absent and unignored. Protected selfcheck security descriptor and source/worktree identity checks passed.
- Exact run ID: h2-20261013-de77a42fccca4193925767ba4e414970.
- Exact target: G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-COLLECTOR/run-h2-20261013-de77a42fccca4193925767ba4e414970.json. It was absent when checked. No collector output has been created.
- Collector excludes .tmp.driveupload from every probe; Git status argv uses the explicit exclusion pathspec. No access to that path occurred in preflight.

Attempt 1 is separately preserved at G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/preflight-h2-20261013-de77a42fccca4193925767ba4e414970. Its wrapper failed before completing a record due to serialization; it did not call the collector or create the target. Attempt 2 corrected the wrapper capture and argv serialization without changing the collector or its inputs.

The saved one-shot launcher is G:\CODEX\New Manga.workspace\agent-output\codex\P02PRE-R1H-H2-RUN\run-h2-20261013-de77a42fccca4193925767ba4e414970\launch-once.ps1 (SHA-256 c9a5b77d3585cc4613c2dafa18d6251e185b025b0ddfef0397bbdc135b1d179d); its PS7.6.6 Parser/assert selfcheck passed 12/12 with 0 skips. The launcher uses ProcessStartInfo.ArgumentList, UseShellExecute=false, and binary BaseStream capture for both pipes.

## Pre-launch attempt history

Attempt 1 stopped before starting a process because a CRLF frontmatter line did not match the wrapper guard. Evidence: G:\CODEX\New Manga.workspace\agent-output\codex\P02PRE-R1H-H2-RUN\run-h2-20261013-de77a42fccca4193925767ba4e414970\launcher-precheck-failure-001.md (SHA-256 89585d9ad42c71be71efe7c68197bd7b3ae7f5a4b3207790b47059befe41d55b). The output target remains absent, no one-shot lock exists, and no collector stdout/stderr/exit capture was created. The wrapper and assert check were corrected before the sole collector invocation.

Additionally, the launcher selfcheck failed because its updated SHA was hidden by malformed Task pin rows; report: G:\CODEX\New Manga.workspace\agent-output\codex\P02PRE-R1H-H2-RUN\run-h2-20261013-de77a42fccca4193925767ba4e414970\launcher-selfcheck-failure-001.md (SHA-256 b0fff9cd23ef7e35b6438f7fb91cf5236f2a2882c055bc59446b6837173b0ef9). Canonical pins were rebuilt directly before the successful recheck.

Attempt 2 stopped before Process.Start because the H2-RUN frontmatter also used CRLF and the wrapper used an end-anchored multiline regex. Evidence: G:\CODEX\New Manga.workspace\agent-output\codex\P02PRE-R1H-H2-RUN\run-h2-20261013-de77a42fccca4193925767ba4e414970\launcher-precheck-failure-002.md (SHA-256 92ddc876d66fe864da6f244a30cc255bbf57314f49a7c8094ac67e0cbd96bea3). No lock or collector output was created. The wrapper now compares exact Get-Content lines and the selfcheck asserts both Task states.

Attempt 3 stopped before Process.Start because Get-Volume on this host has no IsReady property. Evidence: G:\CODEX\New Manga.workspace\agent-output\codex\P02PRE-R1H-H2-RUN\run-h2-20261013-de77a42fccca4193925767ba4e414970\launcher-precheck-failure-003.md (SHA-256 8d55327e92211f4e5b897481409307d1489b18f3ce5e0f85544622fcec52e7f1). Direct read-only volume metadata was NTFS / OperationalStatus=OK / HealthStatus=Healthy. The launcher now checks those supported fields and the selfcheck covers them.

## One-shot invocation

After this Task is transitioned to in_progress, launch exactly once with CWD G:/CODEX/New Manga and direct ProcessStartInfo (UseShellExecute=false, ArgumentList; no shell parsing):

C:\Program Files\PowerShell\7\pwsh.exe
-NoLogo -NoProfile -NonInteractive -File
G:\CODEX\New Manga.workspace\worktrees\P02PRE-R1H-H2-COLLECTOR-INTEGRATION\tools\p02\h1-raw-pre-run.ps1
-RunId h2-20261013-de77a42fccca4193925767ba4e414970

Capture raw stdout, stderr, OS exit and launch metadata under G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-RUN/run-h2-20261013-de77a42fccca4193925767ba4e414970. Recheck target absence and frozen source/root pins immediately before starting. If the process exits nonzero or produces a partial result, preserve it and do not retry this RunId.