# P02 AppContainer contract r7 / Phase A manifest r3 · Codex adjudication

**日期：**2026-10-10（Asia/Shanghai）  
**Live repo：**`G:\CODEX\New Manga`，`main@cddff58469b56e181019a8ddfeade80684bc7eb9` / tree=`c25d051a4b9a0bd9773b50170e100f575ea19f2b`  
**裁决者：**Codex（Integrator / Gate owner）；独立内容 Reviewer=DeepSeek Harness。

## 固定对象与 Review 证据

| 对象 | SHA-256 | 字节 |
|---|---|---:|
| P02 Task（派发时） | `AC200DA1D9565BD612420C0518752D4CCCDFB32FA62C85CDD01449BDCE81FF72` | 94063 |
| Contract r7 | `7FBFFE6583511CBF5348539D1D8A2C4174000D93950FD54DBCDFBBC5B6C90ADF` | 32969 |
| Phase A manifest r3 | `AC45329A58BFFA3AF6984E02207E1AF4AD54E46644DFEEC25B50869E26C4BC43` | 6339 |
| DSH r7 prompt | `45B74CA24BBCB415D38601C6F415B71C9404E0007C709FDBABE5DA2A6887E1A8` | 3813 |
| DSH r7 report | `C1FADDC2D366286F14473DB68AE72D20FCF946E15DE50E4AFA3E2752998EF705` | 24532 |
| DSH r7 exit file | `5FECEB66FFC86F38D952786C6D696C79C2DBC239DD4E91B46729D73A27FB57E9` | 1 |
| Prior r6 adjudication | `103CBD5FBBDDBFF478F823355932A44AD1D0F02897746D328DBECE4BAA983759` | 5095 |
| Prior r6 DSH report | `D8821DF6D93AE47FA650C88FFB90516027F0310BAED6874ABB6210E7A49CAC96` | 26109 |

Codex independently recomputed these SHA-256 values from the listed files. DSH r7 CLI exit=`0`; DSH session=`session-cda214ab-a0e5-4908-8795-b571f5294c6e`; mount succeeded. DSH's formal `object_binding=NOT_VERIFIED` remains its own limitation; this table records Codex's separate byte checks.

## DSH r7 Review disposition

DSH content decision=`APPROVED`; P0/P1/P2/P3=`0/0/0/5`. DSH-R6A-01..12 are all `CLOSED` in the actual r7/r3 text. The “24 environment variables” count in the r6 report was wrong: r2 enumerates 23; r3 retains the same 23 in order, explicitly calls the set complete, and leaves all other mappings `NOT_RUN / Phase B`. No variable was added to reach 24.

The five new findings are non-blocking P3s. Codex dispositions:

| Finding | Disposition | Reason |
|---|---|---|
| P3-01 candidate manifest still says “冻结日期” | **Defer to next candidate** | Its state explicitly says `CANDIDATE / NOT_RUN / NOT_AUTHORIZED_FOR_EXECUTION`; changing the pinned manifest is unnecessary for the current document adjudication. |
| P3-02 manifest omits repetition of all 10 Gate tokens | **Defer** | Contract §1.2 and Task carry the authoritative tokens; manifest retains the operative restrictions and no contradictory status. |
| P3-03 `%LOCALAPPDATA%` controller reference | **Defer** | Phase A is controller-only and no profile API may run, so there is no second profile-local interpretation; the next measurement manifest must freeze exact resolution. |
| P3-04 contract §1.2 summarizes OS/token fields generically | **Defer** | Contract explicitly delegates the exact controller-only read set to manifest r3; r3 enumerates the fields. |
| P3-05 exclusion-manifest filename omitted | **Defer to Phase B** | Phase A performs no protected-file digest; the future Phase B manifest must freeze its own path and exact objects. |

These deferrals do not change an authorization, path, field, or Gate. No r7/r3 bytes were changed, so their pins remain valid.

## Codex execution-readiness finding

**EA-01 — Exact read procedure and bootstrap order are not frozen; Phase A r3 execution remains blocked.** This is a Codex execution-readiness finding, not a DSH content finding and not a test failure.

Manifest r3 names fields and path objects but does not specify enough method detail to ensure an exact, controller-only, no-write measurement:

- Token fields require a pinned read mechanism and failure handling (`GetTokenInformation` requires `TOKEN_QUERY`; the five named information classes and output parsing are not specified in r3).
- File IDs, reparse state, owner/DACL and mandatory labels require a pinned handle/open strategy and exact information classes. r3 does not specify how to avoid following reparse points or how to distinguish unavailable fields from a confirmed result.
- The 23-variable list omits `ProgramData`, while WER paths include `%ProgramData%`. r3 prohibits unlisted environment reads but does not pin a permitted path resolver.
- T0 is required before any Phase A read, yet two WER directory paths must be resolved before their T0 metadata can be sampled. The resolution step and its place inside the T0 bootstrap are not defined.
- r3 says PowerShell/.NET only and no child process, but does not pin an implementation mechanism or establish that compilation/measurement cannot create a child process or write a file.

Microsoft documents `GetTokenInformation` and `TOKEN_QUERY` semantics, `Environment.GetFolderPath` special-folder mappings, `GetSecurityInfo`, and that PowerShell 7 `Add-Type` creates an in-memory assembly by default. These references establish API semantics, not that a particular r3 implementation is exact or that local OS state has been read: [GetTokenInformation](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-gettokeninformation), [token access rights](https://learn.microsoft.com/en-us/windows/win32/secauthz/access-rights-for-access-token-objects), [Environment.SpecialFolder](https://learn.microsoft.com/en-us/dotnet/api/system.environment.specialfolder?view=net-6.0), [GetSecurityInfo](https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo), [PowerShell Add-Type](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.utility/add-type?view=powershell-7.6).

**Resolution:** do not execute manifest r3. Keep `OS isolation preflight=NOT_RUN`. Freeze a new Phase A manifest and a minimal measurement procedure/source with exact path-resolution order, read-only API calls, handle flags/access masks, output fields, error mapping, and a no-child/no-file-write boundary. Get a new non-author Review and Codex byte/object check before any measurement. Do not widen the 23-variable set; either resolve the WER path using an explicitly permitted system-folder API inside the T0 bootstrap or mark it `UNKNOWN / BLOCKED` if equivalence cannot be confirmed without an unlisted read. This finding does not authorize profile creation, ACL/registry changes, writes, probes, build, or Sandbox access.

## Current Gate and next action

No operating-system measurement was run in this adjudication. Current state remains:

`private_registry_absence=UNPROVABLE / BLOCKED`; `profile=NOT_CREATED`; `ACL/registry=NOT_MODIFIED`; `scratch ACL/label mutation=AUTHORIZATION_PATH_DEFINED / NOT_APPROVED`; `OS isolation preflight=NOT_RUN`; `hook/cache/child-process closure=BLOCKED / NOT_VERIFIED`; `Build Gate=BLOCKED`; `build=NOT_AUTHORIZED / NOT_RUN`; `Hard Build Barrier=EFFECTIVE`; `AC1–AC7=BLOCKED / NOT_RUN`.

**Next:** update P02 Task, Plan, STATUS, Index, and rolling checkpoint with the r7 review/adjudication and EA-01; then prepare a narrowly scoped Phase A method candidate for independent review. Do not start P02 build or Cargo work.
