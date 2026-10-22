# Codex pure-selftest run record

| Field | Value |
|---|---|
| Task | P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION |
| Command | `pwsh -NoProfile -File tools/p02/p02-new-time-baseline-selftest.ps1` |
| Branch / HEAD at start | `agent/zcode/P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` / `c8434a8e74d5dd211cfad673f9fd46f9d4d73e0f` |
| CWD | `G:\CODEX\New Manga.workspace\worktrees\P02-NEW-TIME-BASELINE-AC3-HELPER-OUTPUT-RESOLUTION` |
| PowerShell | `7.6.6` / `Core` / `FullLanguage` |
| Started UTC / finished UTC | `10/13/2026 21:09:45` / `10/13/2026 21:09:47` |
| Exit | `0` |
| Assertions | `220 PASS / 0 FAIL / 7 SKIP` |
| Collector SHA-256 | `BF9F69CFB291C6E7609A861821FC458C32C7A3C7AD93898953E3AD2DB26D567A` |
| Selftest SHA-256 | `26C5F50EC3C7CD447A7BC116B1038AE57777FCDA38E3B95E74232A2ACAF2F73F` |
| stdout SHA-256 | `92CA9348946B74089224D83133A3759E7FFB3A626A95C37149B1F1B90B6F7F04` |
| stderr SHA-256 | `E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855` (empty) |
| Fixture inventory SHA-256 | `F19F51566C48F374CCD0D38EA06972A5B6C1F13EE4E01486FF3C2BCA9440514F` |

Seven skips remain separately enumerated in the stdout and are not counted as PASS: live-collector-run, live-git-child, live-whoami-child, live-registry-acl-profile-getter, executor-dynamic-process-enumeration, x6-post-run-review-build-cargo-ac-sandbox, historical-input-access.

The SUMMARY-JSON records liveQueriesExecuted=false, liveCollectorExecuted=false, gitChildExecuted=false, historicalInputAccessed=false. All fixture files are preserved; inventory and per-file hashes are in `selftest-fixture-inventory-r1.json`.