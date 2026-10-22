# H2-RUN runtime verification R1

Task: P02PRE-R1H-H2-RUN  
RunId: h2-20261013-de77a42fccca4193925767ba4e414970  
Verification time UTC: 2026-10-13T10:39Z  
Collector source commit: 1924fbb4fbff6044205e4f8b52adb6aaff879e2a  
Base commit: 343895fb5f0329c0c07a7104ec321b698f967607

## Result

The pinned collector was invoked exactly once after the Task entered in_progress. The process and collector both completed with OS/collector exit code 0. The result disposition is COLLECTED_NEW_TIME_EVIDENCE.

Raw NDJSON: G:/CODEX/New Manga.workspace/agent-output/codex/P02PRE-R1H-H2-COLLECTOR/run-h2-20261013-de77a42fccca4193925767ba4e414970.json  
Bytes: 788029  
SHA-256: 32cd72b710857bb0f19eb92d2c01f2ff6aa13778f10836965c8619ebbf5a2179

The file has 80 parseable NDJSON records: 1 meta, 78 observation, and 1 terminal closed record. All 78 observations have unique IDs, nonempty start/finish timestamps and output fields, and state OK. They consist of 54 in-process-getter and 24 helper-process observations.

The terminal record contains 55 checks: 55 PASS, 0 FAIL, 0 NOT_VERIFIED, and 0 NOT_RUN checks; it has no blocked reasons. Codex independently traversed every observedPointer as a JSON Pointer against the terminal record's observations graph: 55/55 resolved, 0 malformed, 0 unresolved. The machine-readable assertion summary is [runtime-verification-r1.json](runtime-verification-r1.json), SHA-256 30845dd99832d4a774dd5104633bd5de3f9c436231e1981702426125e5189566.

Launcher capture metadata matches the raw stdout, stderr, exit marker, and collector output by bytes and SHA-256. Collector stdout is 29,817 bytes (SHA-256 8a6d80eadd27af3ebc6198edabda79c76ef849a392e44302ff0b4d5b24ea3814); stderr is empty (SHA-256 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855); the exit marker is 0 plus CRLF (SHA-256 13bf7b3039c63bf5a50491fa3cfd8eb4e699d1ba1436315aef9cbe5711530354). The launch interval was 2026-10-13T10:39:06.7990757Z through 2026-10-13T10:39:08.7561361Z.

## Frozen-state verification

After collection, root HEAD and refs/heads/main both remained 343895fb5f0329c0c07a7104ec321b698f967607; .git/index remained 973,207 bytes with SHA-256 c5ca88842173a8fe4b9c6b6b675528347eecbdc73f85600aba06f11e3a692b68. The approved source worktree remained clean at 1924fbb4fbff6044205e4f8b52adb6aaff879e2a. Collector and selftest source hashes remained 69dbe8ffd57a4e182f6f79817d2351d519724f69188f2ea7840da187714edc61 and e7ad2b19508d8aae0943e4b42e6830d6fc16bec53b757b62d745c017645ad96c. The collector's root/candidate/A6 ref, protected-file, and before/after root-index checks all recorded PASS.

## Scope and disposition

This is evidence from the new collection time only. It does not replace H1 v2 evidence, close historical P2-1, satisfy X6 S0, or release X6. Dynamic process closure remains REQUIRES_ACTIVE_TEST / NOT_RUN; Build/Cargo and AC1–AC7 remain unrun. These limits match the frozen Task scope.

The three one-shot launcher failures were all pre-Process.Start, individually preserved in the Task run directory, and did not invoke the collector. The final pinned launcher was then invoked once; no retry occurred.