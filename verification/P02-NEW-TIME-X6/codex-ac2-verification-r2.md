# P02-NEW-TIME-X6 X6-AC2 Codex verification r2

## Frozen source and environment

- Reviewed source head=`839e0089c971e9be984cd9e99a56ea0152ec1391`; Task-only evidence head when run=`a1536968ca063edc33ce033cd937de0f33dbb08e`. No executor or selftest source change occurred after the DSH r3 review.
- Executor disk SHA-256=`43EE7BE2EEF449CC85C7FDDEECAF22BA689E60479CCD37D82137F4F405DDB9D4`; selftest disk SHA-256=`9E1138499BCA22F54B13BC2A9D88B4730BDC8CDCB810D9BA28EC66599213FBC1`.
- Shell=`C:\Program Files\PowerShell\7\pwsh.exe`; PowerShell=`7.6.6`, edition=`Core`, language mode=`FullLanguage`; OS=`Microsoft Windows 10.0.26300`; every invocation used `-NoProfile`.

## Results

| Check | Result | Raw evidence |
|---|---|---|
| Parser: executor and selftest | PASS; both `PARSER_ZERO_ERRORS`; exit=0; stderr=0 B | `G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6/codex-ac2-parser-selftest-r2/parser-stdout.txt`, SHA-256=`E3A4691A98DA9AAB7EC25A3130FC3EA46FBB4FF176477F563AC10C8B71A1C3D9` |
| Pure-memory selftest | PASS; 272 assertions passed, 0 failed, 7 individually recorded SKIP; exit=0; stderr=0 B | `.../selftest-stdout.txt`, SHA-256=`1E169224436BF046471033445A65E72AFA18AD257BF08A664A8803B1EB66EB20` |

Selftest summary records `liveQueriesExecuted=false`, `liveCollectorExecuted=false`, `gitChildExecuted=false`, and `historicalInputAccessed=false`. The seven SKIP names and reasons are in raw stdout: `live-x6-executor-run`, `live-git-child`, `live-whoami-child`, `live-registry-acl-profile-getter`, `executor-dynamic-process-enumeration`, `x6-post-run-review-build-cargo-ac-sandbox`, and `historical-input-access`.

Fixture root=`G:/CODEX/New Manga.workspace/temp/P02-NEW-TIME-X6/codex-ac2-r2-20261014-124643-pure-selftest/`; preserved files: `collision.bin` 5 B / SHA-256=`74F81FE167D99B4CB41D6D0CCDA82278CAEE9F3E2F25D5E5A3936FF3DCEC60D0`, `exclusive.bin` 1 B / SHA-256=`559AEAD08264D5795D3909718CDD05ABD49572E84FE55590EEF31A88A08FDFFD`, `partial-run.json` 93 B / SHA-256=`695D4BF696D7988C3A4561810A004BFE29B84083700C52FED34987194302A45D`. No fixture from attempt 1 was reused or modified.

Complete command, stdout, stderr, exit, environment, and fixture inventory remain in `G:/CODEX/New Manga.workspace/agent-output/codex/P02-NEW-TIME-X6/codex-ac2-parser-selftest-r2/`.

## Gate disposition

X6-AC2=`PASS`. This establishes only parser/selftest readiness. No freeze manifest was created, no final pre-run was run, and the X6 executor was not invoked. X6-AC4 remains NOT_RUN; downstream post-run Review, Build/Cargo, and product AC1–AC7 remain blocked. Old H1/P2-1 findings and historical missing-source records were not accessed or changed.
