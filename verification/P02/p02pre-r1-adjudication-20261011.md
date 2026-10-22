# P02PRE-R1 Codex Adjudication — pre-run release

Date=`2026-10-11 14:48 Asia/Shanghai`; Owner/Author/Integrator/Adjudicator=`Codex /root`; independent Reviewer=`DeepSeek Harness`, session=`session-a98bffe4-310e-4726-8125-830ca5d0f02c`.

## Decision

`PRE_RUN_REVIEW_ACCEPTED; RELEASED_FOR_ONE_READ_ONLY_CAPTURE`.

This adjudication releases only the single capture explicitly defined by the frozen R1 manifest. It does not classify any host condition as passed and does not change any P02 technical Gate or Build authorization.

## Review evidence and disposition

- Round 1=`CHANGES_REQUESTED` (`0/2/6/3`); Round 2=`CHANGES_REQUESTED` (`0/0/3/2`); Round 3=`CHANGES_REQUESTED` (`0/0/1/2`). Round 3 confirmed all 16 prior findings closed; its three new findings were corrected and reviewed in Round 4.
- Round 4 full Review=`CHANGES_REQUESTED` (`0/0/0/1`), report=`verification/P02/dsh-p02pre-r1-review-r4-20261011.md` (18,995 bytes; SHA-256 `DD099DCDCA59E1C7EBBB5B9A938C2F50BF31A9F5B39872B738874CF4DEB7ED98`). It closed all 19 prior findings; P3-DOC-1 was the only remaining finding.
- Follow-up #1=`CHANGES_REQUESTED` (`0/0/0/1`), report=`verification/P02/dsh-p02pre-r1-review-r4-followup-20261011.md` (15,629 bytes; SHA-256 `BFED4454E5F338C59CC2E942D96A48634F67B54DCCED33CECE14C63DFACEA9B9`). It closed P3-DOC-1 and raised P3-PIN-1 based on a mis-transcribed SHA character.
- Follow-up #2=`APPROVED` (`0/0/0/0`), report=`verification/P02/dsh-p02pre-r1-review-r4-followup-2-20261011.md` (6,572 bytes; SHA-256 `BFEA7516C815F4236A6A7421214720D809164785FD55B8AF1EC22D7F8D576D8E`). The Reviewer closed P3-PIN-1 as their own transcription error after visually confirming the same `97400A9E…84AB` string in the parser JSON, prompts and Task. The Reviewer did not independently recompute hashes because DSH sandbox preparation failed with Win32 5.
- After Codex found two stale manifest status sentences during live-file review, they were updated without changing the script or query/write scope. Follow-up #3 reviewed the final manifest bytes and returned `APPROVED`, P0/P1/P2/P3=`0/0/0/0`; report=`verification/P02/dsh-p02pre-r1-review-r4-followup-3-20261011.md` (`9,399 bytes / SHA-256 86445E85D5CA73C4549C58BCB31E92017CC59619AFFE18A4C53BDF310D52EB0A`); raw stdout=`verification/P02/dsh-p02pre-r1-review-r4-followup-3-20261011.stdout.jsonl` (`45,496 bytes / SHA-256 BC6A5BC8EFD83C150CD05B2C1EDCA70E0F89BD713EFD010FAB59DEDB178D68F2`); stderr empty; exit=`0`. The Reviewer recorded three non-blocking observations: finding groups are compressed in manifest line 9 (detailed in Task), line 13 does not restate “R4 + focused follow-up” (line 9 states this), and Review timestamps were not audited. No open finding remains.

DSH Review #3 was a narrow, read-only content review. It did not execute commands or recompute hashes. Its conclusion is review evidence only, not an OS result or Gate PASS.

## Codex pin and scope verification

Local SHA-256 methods `.NET SHA256.ComputeHash(ReadAllBytes)`, PowerShell `Get-FileHash`, and `certutil -hashfile` agree for the final manifest and unchanged script:

| File | Bytes | .NET | `Get-FileHash` | `certutil` |
|---|---:|---|---|---|
| `verification/P02/p02pre-r1-manifest-20261011.md` | 12615 | `A5510774B47C17EB29C5BF5D73FE7B755C72E2726FC5280E7EF11A91A23C67A7` | same | same |
| `verification/P02/p02pre-r1-capture.ps1` | 38729 | `97400A9EF16E47242DA3C4E53C8265F16BA9A70853B26D3905748B9CA69884AB` | same | same |

The hash-bound parser evidence=`verification/P02/p02pre-r1-windows-powershell-parse-r4-20261011.json` (`2,086 bytes / SHA-256 `1AE3462C5EB16E85B47A03E90CBC53DA33F5EAD74BFCFB1992BADC5F6A805841`) records 38,729 input bytes with the same script SHA in child, parent recheck and embedded stdout; parse result=`PARSE_OK`, process exit=`0`, `captureScriptInvoked=false`.

The final manifest change is limited to status/procedure wording in lines 9 and 13. DSH follow-up #3 confirmed these sentences match the completed Review sequence and retain the pre-run Codex adjudication requirement. The command, CWD, user/SID and Git target checks, getter allowlist, protected paths, child-process allowlist, single `FileMode.CreateNew` evidence path, error/stop behavior and classification rules remain those in the manifest. No capture has been invoked as of this decision.

## Exact one-time invocation released

After a fresh preflight confirms the evidence target is absent and the manifest/script pins still match the values above, invoke exactly once from `G:\CODEX\New Manga`:

```text
C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -File verification/P02/p02pre-r1-capture.ps1
```

The script itself checks the expected user `HOME-MY\49745`, SID `S-1-5-21-2196946971-914346751-4210154634-1001`, main repo HEAD/tree and scratch HEAD/tree before expanding to the frozen getters. It must stop on any mismatch, query/hash/ACL error, incomplete evidence or write error; preserve any partial evidence; never retry, clean up, or expand the allowlist. Its only output is the unique `verification/P02/p02pre-r1-evidence-20261011.json`, created with `CreateNew`.

## Gate disposition

Preserve exactly: `private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`.

Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; product Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`. The authorized R1 invocation is only pre-run evidence capture; it does not satisfy other security requirements or pass a Gate. After capture, classify the actual result, obtain any required independent evidence review, and record a separate Codex post-run adjudication before releasing the next Task.

## Post-run Codex adjudication — partial evidence (2026-10-11)

### Decision

`PARTIAL_EVIDENCE_ACCEPTED; P02PRE-R1_CLOSED_WITH_LIMITATIONS; RELEASE_P02PRE-R1F_PLANNING`.

This accepts the saved stop event as truthful evidence and closes the one-shot R1 capture path with limitations. It does **not** satisfy the R1 host-baseline objective, release R2 execution, or pass any P02 Gate. The successor is a new, independently scoped capture task; the old manifest, script and evidence remain immutable.

### Run and independent review

The exact frozen R1 command ran once from `G:\CODEX\New Manga`; PowerShell process exit=`1`. Evidence=`verification/P02/p02pre-r1-evidence-20261011.json`, `2588454 bytes / SHA-256 8A1A056600F6A1B5C2E7980E4CCAE2B3DB085B1EF7EC7DC5CC7FD35A4A068B9C`. Its `stopReason=MAIN_REPOSITORY_BASELINE_OR_HASH_FAILED`; the main Git target/HEAD/tree/branch and expected user/SID matched. Protected inventory stopped at `.codex/skills/ask-matt`; 662 regular-file hashes had been collected. Read-only metadata/index checks identify this path as a tracked symbolic link (`mode 120000`, `Directory, ReparsePoint`, unchanged path status); no link target was resolved or read. Scratch, later path/ACL, TEMP/cache, WER and later registry queries were not reached. R1 did not call profile creation/deletion, mutate ACL/registry, write a canary, build/Cargo, or run AC1–AC7.

Non-author DSH review=`changes_requested` (`P0/P1/P2/P3=0/1/1/2`); report=`verification/P02/dsh-p02pre-r1-evidence-review-20261011.md` (`103356 bytes / SHA-256 3B949CF20160BFFC0122A489C632D00C7CF84540571305567B4A23D5DF701736`); prompt=`verification/P02/dsh-p02pre-r1-evidence-review-20261011.prompt.md` (`3610 bytes / SHA-256 2CA8E9F50CAAC994391FDFC036F593657A7F0AAF707E8E5EF8D0769874F2AC42`); raw stdout=`103356 bytes / SHA-256 685D388657C87FB65771E0AE2179968105E32114AE27AEDF4A096A92EE292CB6`; stderr=`0 bytes`; exit=`0`. DSH reviewed JSON text but could not independently recalculate hashes because its sandbox failed with Win32 5; it ran no commands and edited no project files.

### Finding disposition

- `F-01 P1`: accepted. The frozen fail-stop worked, but it deterministically prevented the complete baseline when the Git inventory included a tracked reparse object. Do not rerun the original script or extend its one-time evidence. Successor policy: for an exact Git-index entry with mode `120000` whose leaf is a live reparse point, record only mode and non-target metadata as `SKIPPED_SYMLINK_NOT_FOLLOWED`; never open, hash, resolve or follow the target. Any untracked/unknown reparse, mode mismatch, parent reparse, or other unsupported non-regular object still stops the new capture. This leaves link-target content explicitly unproven.
- `F-02 P2`: accepted. The new result will include `candidateCount`, `processedCount`, `regularFileHashCount`, `skippedSymlinkCount`, `omittedCount`, and `firstBlockingPath`; the old partial's count remains 662 and is not backfilled.
- `F-03 P3`: accepted. The new parser will explicitly remove and count the terminal NUL split artifact; it will not treat it as a candidate path.
- `F-04 P3`: accepted. Captured child-command records will serialize as one named object each, with an assert preventing placeholder-array records. The new parser/capture artifact will be independently reviewed.

These repairs belong in a new Task/manifest/script and a new `CreateNew` output path. Do not amend the old R1 script or JSON. DSH findings are not marked independently verified as fixed until the R1F Review confirms the frozen bytes.

### Five-state result and remaining Gate

| 项 | Codex 分类 | 执行证据 |
|---|---|---|
| host identity 与 main Git target | `PASS_WITH_EVIDENCE` | user/SID、HEAD/tree/branch、status bytes/hash 已写入 JSON |
| main regular-file protected inventory | `FAILED`（采集未闭合） | 662 hashes 后在 tracked reparse path 按冻结停止条件结束；不是 Build/AC 测试失败 |
| `.git/index` pre-state | `PASS_WITH_EVIDENCE` | R1 T0 前记录 hash；未到达 post-state，不能推断稳定 |
| scratch root、输入/output/canary ACL、TEMP/cache、WER 与 registry getters | `UNPROVABLE`；运行状态 `NOT_RUN` | 脚本在访问这些对象前停止 |
| profile API/store 与 LPAC 子进程/写入闭包 | `REQUIRES_ACTIVE_TEST` | R1 未执行动态验证 |
| R1 未触发的 Build/Cargo 与 AC1–AC7 | `NOT_RUN` | 本次没有运行 |
| `private_registry_absence` | `UNPROVABLE` | 保留用户已批准的精确风险裁决，不改成 PASS |

本次为当前有效 checkpoint 之后的新增变化：R1 唯一 capture 已执行并以 safe-stop 结束；独立证据 Review 已完成但提出 4 项 findings；Codex 已裁决并释放 R1F 的 planning/implementation。新的 blocker 是完整 baseline 遇到 tracked symlink；它由新 no-follow contract 处理，不需要用户决定。旧 checkpoint 未包含 capture 结果，因此不存在先验可比较的执行证据。

### Gate 保留

`private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`; Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`; Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; `technical condition unmet; user explicitly accepted residual risk`.

Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; Build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`. Neither this evidence review nor its adjudication is a Gate pass.