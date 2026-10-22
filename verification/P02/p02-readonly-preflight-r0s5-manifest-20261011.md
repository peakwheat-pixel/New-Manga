# P02PRE-R0S5 Frozen Read-only Manifest

## 1. Authorization and immutable state

This is the user's newly issued 2026-10-11 authorization for the separate P02PRE-R0S5 controlled read-only task. It does not extend the earlier registry-risk waiver, is not a Gate PASS, and does not release the Build Barrier.

- `private_registry_absence=UNPROVABLE`
- Technical Gate=`NOT_SATISFIED`
- Owner Risk Acceptance=`APPROVED`
- Gate Disposition=`WAIVED_BY_OWNER`
- Build Authorization=`AUTHORIZED_WITH_EXCEPTION`
- Required exact statement: `technical condition unmet; user explicitly accepted residual risk`
- Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`; build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`

## 2. Source-of-truth pins

- R6 source: `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md` (fixed current project file; use only its exact allowlisted objects and current fields).
- Prior read-only task: `doc/tasks/P02PRE-R0S4.md`; manifest `verification/P02/p02-readonly-preflight-r0s4-manifest-20261011.md`; adjudication `verification/P02/codex-p02pre-r0s4-adjudication-20261011.md`; checkpoint `verification/P02/codex-checkpoint-p02pre-r0s4-20261011.md`.
- Historical limited evidence: `verification/P02/p02-readonly-preflight-r0-evidence-20261011.md`; it applies only to the exact objects and capture time recorded there.
- R0 evidence §`固定文件 hash 前/后对照` records 13 hash observations: 12 named project documents plus `.git/index`; it is a limited historical hash collection, not a complete protected-file inventory. The historical capture used PowerShell `Get-FileHash` (R0 evidence §`实际执行调用与结果`, L18–L29; r6 also records `Get-FileHash` at L229), so it does not prove the current runner or method safe. Current hashes remain uncollected.
- Current R0S4 independent Review Round 2=`verification/P02/dsh-p02pre-r0s4-review-r2-20261011.md`, `30529 bytes / SHA-256 E8AB99FE1F340E13AA7C4A044F5580DDE554A840230EB420E3E34730A516AAF3`; its Codex adjudication=`verification/P02/codex-p02pre-r0s4-adjudication-20261011.md`, `8669 bytes / SHA-256 DDE130CE4E33612AAC3B21113E20FAF52A1599B85D358CECD0CC66DACA6380FC`. These explicitly leave the current runner `NOT_SAFE_FOR_R0`.
- Live execution target remains only the current host process identity and exact r6-listed paths/keys. No guessed or derived path is authorized by this manifest.

## 3. Exact read-only candidate inventory

| Candidate | Exact scope | Required method boundary | Initial disposition |
|---|---|---|---|
| Current execution identity | Compare actual values with r6 §`固定身份、Profile 与 API 参数`: expected user `HOME-MY\49745`, user SID `S-1-5-21-2196946971-914346751-4210154634-1001`; require non-elevated execution and no thread impersonation | Same process; capture user/SID/token/elevation/impersonation fields only; no `whoami`, P/Invoke, helper process or token mutation | `NOT_SAFE_FOR_R0` until exact runner and getter are reviewed; current condition=`UNPROVABLE` |
| Profile/target path | Only exact path explicitly present in r6 | Existence + basic metadata only; no guessed SID path; no profile API | `UNPROVABLE` if r6 has no exact safe path; otherwise getter remains `NOT_SAFE_FOR_R0` pending review |
| Path ACL | Exactly the 12 input roots, 13 scratch output leaves, and three canary leaves enumerated below (28 objects total); no protected/deny-scope host path or profile path | Read security descriptor only; no effective-access test, ACL mutation, owner/label query beyond r6 | `NOT_SAFE_FOR_R0` pending runner/method review; current descriptors=`UNPROVABLE` |
| TEMP/cache/scratch resolution | Exact environment variables and 12 input roots, 13 output leaves, three canary leaves enumerated by r6 | Read values/metadata only; no host config, credentials, content, recursion or writes | `NOT_SAFE_FOR_R0` pending runner/method review |
| Historical R0 hash collection | The exact 13 entries in R0 evidence §`固定文件 hash 前/后对照`: 12 named documents plus `.git/index` | Historical PowerShell `Get-FileHash` only; do not label this collection the full R6 `protected-invariants` inventory | Historical collection=`PASS_WITH_EVIDENCE`; current hash query=`NOT_SAFE_FOR_R0`; full R6 protected-invariants set remains unproven |
| WER/T0 candidate state | Only the exact LocalDumps key/views and three directory candidates explicitly listed in r6 | No registry value/subkey enumeration; no dump/content reads; no broader view/path | `NOT_SAFE_FOR_R0` pending exact getter and runner review; effective WER/T0 remains unproven |
| Other getter/query | Only a method explicitly in r6 with prior independent evidence that it has no side effects | No new API, executable, provider, module, child process or path | `NOT_SAFE_FOR_R0` unless the exact method and runner are individually cleared |

### Exact ACL object set

The only ACL descriptor candidates are:

1. **12 r6 read-only input roots** (`r6` §`允许读取路径`): `C:\Users\49745\AppData\Local\Programs\Python\Python312`; `G:\CODEX\New Manga.task-envs\m2ac5-build`; `G:\CODEX\New Manga.task-envs\M2-DOCTR-QUAL-C4\weights\ogkalu-comic-text-and-bubble-detector`; `G:\CODEX\New Manga.task-envs\M2-SFX-DETECT\weights-v2b`; `E:\Program Files\nodejs`; `C:\Users\49745\.rustup\toolchains\stable-x86_64-pc-windows-msvc`; `C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools`; `C:\Program Files (x86)\Microsoft Visual Studio\Installer`; `C:\Program Files (x86)\Windows Kits\10`; `C:\Program Files\Git\cmd`; `C:\Program Files\Git\mingw64`; `G:\CODEX\P02-scratch-build-source`.
2. **13 exact scratch output leaves** (`r6` §`Scratch 写入、ACL 与输入/输出`), each relative to `G:\CODEX\P02-scratch-build-source`: `apps/desktop/frontend/node_modules/`; `apps/desktop/frontend/dist/`; `apps/desktop/src-tauri/target/core-sidecar/`; `apps/desktop/src-tauri/target/pyinstaller-work/`; `apps/desktop/src-tauri/gen/schemas/`; `apps/desktop/src-tauri/permissions/autogenerated/`; `verification/P02/cargo-target/`; `npm-cache/`; `cargo-home/`; `tmp/appdata/`; `tmp/home/`; `python-cache/`; `pyinstaller-config/`.
3. **Three exact canary leaves** (`r6` §`Scratch 写入、ACL 与输入/输出`): root=`G:\CODEX\P02-scratch-build-source`; relative leaves=`verification/P02/tmp/smoke-readonly-probe/`, `verification/P02/tmp/lpac-write-control/`, and `verification/P02/tmp/lpac-write-deny-control/`. The r6 section's scratch root governs these relative leaves; they are not under `G:\CODEX\New Manga`.

No ACL query is authorized for `G:\CODEX\New Manga`, linked worktree roots, other clones, host-wide caches, credentials, manga/library inputs, databases, Locks, current/pinned Revisions, model paths, unlisted system/profile paths or the unknown AppContainer profile folder. These remain protected/deny scope.

The historical hash collection's 12 named documents are `AGENTS.md`; `doc/REBASELINE_PLAN.md`; `doc/00_INDEX.md`; `doc/STATUS.md`; `doc/09_COLLABORATION.md`; `doc/tasks/P02.md`; `doc/tasks/P02PRE-R0.md`; `verification/P02/codex-checkpoint-p02-readonly-preflight-r0-20261011.md`; `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-20261011.md`; `verification/P02/p02-owner-risk-waiver-execution-manifest-r6-review-20261011.md`; `verification/P02/codex-p02-owner-risk-waiver-manifest-r6-adjudication-20261011.md`; and `verification/P02/codex-p02-unwaived-gate-feasibility-20261011.md`. The 13th entry is `.git/index`. This fixed historical collection does not substitute for the dynamic R6 protected-invariants inventory.

### Getter/method eligibility

No current-host getter/query in the r6 manifest has yet been independently cleared for repeat execution in this R0 task. Existing `DeriveAppContainerSidFromAppContainerName` evidence is historical only; it neither proves profile existence nor authorizes repeating its P/Invoke/Add-Type route here. `GetAppContainerFolderPath` remains blocked by M7; `GetAppContainerRegistryLocation` remains blocked by M8; the R0S2 LocalDumps open candidate remains `NOT_SAFE_FOR_R0`. Plain names such as `Get-Acl` or `Test-Path` are not themselves evidence that the current runner/provider chain is side-effect-free.

## 4. Runner gate

Before any P02PRE host query, evidence must bind the actual current tool instance to its executable/version and complete launch argument vector; establish startup/profile/module/provider, cache/history, wrapper, temp/log behavior; and enumerate all possible children. `shell=PowerShell` or `login=false` alone is insufficient. Explicitly launching a `-NoProfile` child does not establish the safety of its parent launcher.

The previous independent Review of R0S4 records the current `exec_command`/PowerShell launch chain as not proven side-effect-free. This manifest does not override that finding. Until new exact evidence and non-author review plus Codex adjudication exist, **no P02PRE host/OS/registry/WER/profile/token/ACL/path/environment/hash query is permitted under this manifest**. Static document classification may continue.

## 5. Protected and prohibited targets

- No write/delete/rename/ACL change/profile creation or deletion/registry mutation anywhere.
- No permission canary write, including to a protected path.
- No access to manga/library inputs, databases, Lock, current/pinned Revision, credentials, model files, dumps, or any unlisted host path.
- No Windows feature or Windows Sandbox query/change; no build/Cargo/AC1–AC7; no privilege elevation, service/driver/ETW/network/compile/JIT.
- Evidence output may be written only to the exact new `verification/P02/*r0s5*` artifacts listed by `doc/tasks/P02PRE-R0S5.md` and the named governance summaries. No other output/cache/log path is authorized.

## 6. Stop conditions and status semantics

Stop before querying if runner, getter, target identity/path, child boundary, or evidence destination differs from this manifest. Stop immediately on unknown child, out-of-scope path, identity mismatch, unexpected write or evidence/hash anomaly. Do not clean up or retry.

`PASS_WITH_EVIDENCE` is limited to evidence actually captured for the pinned object/time. `FAILED` requires an executed check that failed. `UNPROVABLE` means the condition has no applicable proof. `REQUIRES_ACTIVE_TEST` identifies a condition that inherently needs the separately authorized dynamic validation. `NOT_SAFE_FOR_R0` identifies a candidate that must not be run during this read-only task.
