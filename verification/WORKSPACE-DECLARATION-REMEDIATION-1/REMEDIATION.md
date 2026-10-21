# REMEDIATION — real-repository declaration audit

Task: WORKSPACE-DECLARATION-REMEDIATION-1

## Same command / same snapshot

`same_snapshot`: **True** (git HEAD `f0f19596fa9df6b561626b27f1c086b095552be7`; `git ls-files -z -- doc/tasks verification` sha256 `6eaeb3923c7f299f3b3bfa37cd60a6c2b86c4976e2d8bac8daf39a2e379210d3`, 7416 tracked + 1504 untracked scan files, content manifest sha256 `3187c41a66d1853cf247ba1a4570fdb77713c2747a2cce27f700d3baf8aad5ab`).

Before tool: `5a4a1a1cfaeb37698c1d22bd2c9d80149beb48bf4adf075027f7177eb5ded8a7`

After tool: `1a5b70ef91f015532ca85afd62c471cd60210f6353a6b151c3c259baa9b2b5ba`

```
BEFORE: C:\Python314\python.exe -B G:\CODEX\New Manga.workspace\worktrees\WORKSPACE-CLEANUP-TOOL-HARDENING-1\tools\governance\clean_workspace.py --repo G:\CODEX\New Manga --workspace-root G:\CODEX\New Manga.workspace --audit-declarations --out G:\CODEX\New Manga.workspace\worktrees\WORKSPACE-DECLARATION-REMEDIATION-1\verification\WORKSPACE-DECLARATION-REMEDIATION-1\evidence\audit-before-run
AFTER:  C:\Python314\python.exe -B G:\CODEX\New Manga.workspace\worktrees\WORKSPACE-DECLARATION-REMEDIATION-1\tools\governance\clean_workspace.py --repo G:\CODEX\New Manga --workspace-root G:\CODEX\New Manga.workspace --audit-declarations --out G:\CODEX\New Manga.workspace\worktrees\WORKSPACE-DECLARATION-REMEDIATION-1\verification\WORKSPACE-DECLARATION-REMEDIATION-1\evidence\audit-after-run
```

Both runs: cwd `G:\CODEX\New Manga.workspace\worktrees\WORKSPACE-DECLARATION-REMEDIATION-1\verification\WORKSPACE-DECLARATION-REMEDIATION-1`, `PARENT_SHELL=pwsh`, `SHELL=False` (subprocess list argv), exit `2` (read-only; 0 deletions).

| metric | before | after |
|---|---:|---:|
| declarations | 1858 | 1858 |
| protected roots | 1264 | 1264 |
| errors | 163 | 76 |
| warnings | 54 | 236 |
| exit code | 2 | 2 |

Enumeration vs parsing (AC2 wording fix): `tracked_declaration_files`/`untracked_declaration_files` are *enumerated paths* (7416 + 1504); only 2275 `.md` + 1153 `.json` were actually parsed in the after audit.

## Errors by code (before -> after)

| code | before | after |
|---|---:|---:|
| DECL_BARE_NAME | 57 | 0 |
| DECL_DESTINATION_GENERALIZED | 0 | 6 |
| DECL_DESTINATION_UNRESOLVED | 7 | 1 |
| DECL_ENV | 4 | 4 |
| DECL_GENERALIZED | 6 | 6 |
| DECL_RELATIVE_AMBIGUOUS | 1 | 1 |
| DECL_RELATIVE_UNRESOLVED | 6 | 6 |
| DECL_UNKNOWN_DISPOSITION | 9 | 2 |
| FILE_UNREADABLE | 3 | 3 |
| JSON_PARSE | 69 | 2 |
| TABLE_ROW_ARITY | 1 | 1 |
| TABLE_SCHEMA_INCOMPLETE | 0 | 44 |

## Before-audit triage categories

| category | errors |
|---|---:|
| after: DECL_DESTINATION_GENERALIZED | 6 |
| after: DECL_DESTINATION_UNRESOLVED | 1 |
| after: DECL_ENV | 4 |
| after: DECL_GENERALIZED | 6 |
| after: DECL_RELATIVE_AMBIGUOUS | 1 |
| after: DECL_RELATIVE_UNRESOLVED | 6 |
| after: DECL_SOURCE_NOT_A_PATH | 62 |
| after: DECL_UNKNOWN_DISPOSITION | 2 |
| after: JSON_NON_DECLARATION | 67 |
| after: JSON_PARSE | 2 |
| after: TABLE_ROW_ARITY | 1 |
| r2: no matching residual | 5 |

Every one of the 163 before-audit errors is listed in `TRIAGE.md` (code / file / tracked / owner / locator / category / decision); nothing was dropped silently.

## After-audit warnings

| warning | count |
|---|---:|
| DECL_ALIAS_REAL_TARGET | 19 |
| DECL_DESTINATION_PROSE | 35 |
| DECL_EVIDENCE_NOT_A_PATH | 10 |
| DECL_SOURCE_NOT_A_PATH | 54 |
| FILE_ENCODING_LEGACY | 3 |
| JSON_NON_DECLARATION | 67 |
| TABLE_NOT_CANONICAL_EVIDENCE | 47 |
| TABLE_NOT_RESOURCE_MANIFEST | 1 |

## Safety invariants (AC7)

- Existing 80 tests: PASS (`tests.log`, exit 0).
- New AC2–AC5 fixtures: PASS (`tests.log`).
- Incident replay through both tools: 15/15 REJECT, 0 deleted, 18/18 sources covered (`incident-replay-*.json`).
- Real-repository audit still exits 2 (fail-closed); no real file was deleted/moved/archived.
- Protected identities: before 1264 -> after 1264 (`evidence/protection-delta.json`; every dropped or changed declaration is explained there).

## Fixes

1. AC2: BOM-tolerant JSON loading; unparsable JSON is fatal unless its exact path+sha256 is in the explicit `non-declaration-json-exceptions.json` (67 reviewed logs). Renamed `*.stdout.json` declarations stay fatal. JSON_PARSE 69 -> 2.
2. AC3/F-01: only explicit placeholders and pure prose are skipped; ANY path-like value is parsed and unresolved path-like values are fatal (spaces/CJK paths included). DECL_BARE_NAME 57 -> 0, DECL_RELATIVE_UNRESOLVED 6 -> 6.
3. AC4/F-05: strict GB18030 fallback only for CJK text; NUL/control-heavy or non-CJK binary payloads are `FILE_UNREADABLE`. FILE_UNREADABLE 3 -> 3.
4. AC5/F-04: Resource Manifest / Canonical Evidence tables that claim identity columns but lack a required one are `TABLE_SCHEMA_INCOMPLETE` integrity errors; only tables with no identity columns are narrative warnings. TABLE_SCHEMA_INCOMPLETE -> 44, TABLE_ROW_ARITY -> 1.
5. F-03: path-like generalized destinations are fatal again (`DECL_DESTINATION_GENERALIZED` -> 6).
6. Residual: 76 errors remain (see `RESIDUAL.md`): {'TABLE_SCHEMA_INCOMPLETE': 44, 'TABLE_ROW_ARITY': 1, 'DECL_RELATIVE_UNRESOLVED': 6, 'DECL_RELATIVE_AMBIGUOUS': 1, 'DECL_ENV': 4, 'DECL_GENERALIZED': 6, 'DECL_DESTINATION_GENERALIZED': 6, 'DECL_UNKNOWN_DISPOSITION': 2, 'JSON_PARSE': 2, 'FILE_UNREADABLE': 3, 'DECL_DESTINATION_UNRESOLVED': 1}. The <=10 target is **not** met because review r2 restored fail-closed rules (F-01/F-03/F-04) and kept 67 explicit byte-bound exemptions; lowering the count would require weakening fail-closed semantics or editing frozen history, both forbidden by the Task.
