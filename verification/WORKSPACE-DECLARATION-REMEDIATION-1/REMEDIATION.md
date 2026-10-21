# REMEDIATION — real-repository declaration audit

Task: WORKSPACE-DECLARATION-REMEDIATION-1

## Same command / same snapshot

```
C:/Python314/python.exe -B tools/governance/clean_workspace.py --repo G:/CODEX/New Manga --workspace-root G:/CODEX/New Manga.workspace --audit-declarations --out <dir>
```

| metric | before | after |
|---|---:|---:|
| declarations | 1858 | 1855 |
| protected roots | 1264 | 1262 |
| errors | 163 | 15 |
| warnings | 54 | 239 |
| exit code | 2 | 2 |

Enumeration vs parsing (AC2 wording fix): `tracked_declaration_files`/`untracked_declaration_files` are *enumerated paths* (7416 + 1504); only 2275 `.md` + 1153 `.json` were actually parsed in the after audit.

## Errors by code (before -> after)

| code | before | after |
|---|---:|---:|
| DECL_BARE_NAME | 57 | 0 |
| DECL_DESTINATION_UNRESOLVED | 7 | 1 |
| DECL_ENV | 4 | 4 |
| DECL_GENERALIZED | 6 | 6 |
| DECL_RELATIVE_AMBIGUOUS | 1 | 1 |
| DECL_RELATIVE_UNRESOLVED | 6 | 0 |
| DECL_UNKNOWN_DISPOSITION | 9 | 0 |
| FILE_UNREADABLE | 3 | 0 |
| JSON_PARSE | 69 | 2 |
| TABLE_ROW_ARITY | 1 | 1 |

## Before-audit triage categories

| category | errors |
|---|---:|
| AC3 non-path source | 63 |
| AC3/AC5 destination | 7 |
| AC3/AC5 narrative row | 9 |
| AC4 legacy encoding | 3 |
| BOM/format tolerance | 58 |
| JSON declaration classification | 11 |
| genuinely malformed resource table | 1 |
| policy gap (ambiguous relative path) | 1 |
| policy gap (environment token) | 4 |
| policy gap (over-broad declaration) | 6 |

Every one of the 163 before-audit errors is listed in `TRIAGE.md` (code / file / tracked / owner / locator / category / decision); nothing was dropped silently.

## After-audit warnings

| warning | count |
|---|---:|
| DECL_ALIAS_REAL_TARGET | 19 |
| DECL_DESTINATION_GENERALIZED | 6 |
| DECL_DESTINATION_PROSE | 35 |
| DECL_EVIDENCE_NOT_A_PATH | 10 |
| DECL_SOURCE_NOT_A_PATH | 65 |
| FILE_ENCODING_LEGACY | 3 |
| JSON_NON_DECLARATION | 9 |
| TABLE_NOT_CANONICAL_EVIDENCE | 91 |
| TABLE_NOT_RESOURCE_MANIFEST | 1 |

## Safety invariants (AC7)

- Existing 80 tests: PASS (`tests.log`, exit 0).
- New AC2–AC5 fixtures: PASS (`tests.log`).
- Incident replay through both tools: 15/15 REJECT, 0 deleted, 18/18 sources covered (`incident-replay-*.json`).
- Real-repository audit still exits 2 (fail-closed); no real file was deleted/moved/archived.
- Protected identities: before 1264 -> after 1262. The three declarations the old parser registered but the new parser does not are prose strings wrongly normalised as protected identities; none exists as a single path (see `evidence/protection-delta.json`).

## Fixes

1. AC2: BOM-tolerant JSON loading; unparsable tracked/token/manifest-named JSON stays fatal, untracked instrumentation JSON becomes `JSON_NON_DECLARATION` warning. JSON_PARSE 69 -> 2.
2. AC3: descriptive source values (`NOT_APPLICABLE`, `none yet`, Chinese prose, `见 G:/...`) are warnings and do not register protection; bare identifiers and real path-like `PRESERVE_*` failures stay fatal. DECL_BARE_NAME 57 -> 0.
3. AC4: strict GB18030 fallback with `FILE_ENCODING_LEGACY`; FILE_UNREADABLE 3 -> 0.
4. AC5: Resource Manifest / Canonical Evidence tables need the exact English schema; narrative tables are warnings. DECL_UNKNOWN_DISPOSITION 9 -> 0, TABLE_ROW_ARITY stays 1 (genuinely malformed).
5. Residual: 15 errors remain (see `RESIDUAL.md`): {'TABLE_ROW_ARITY': 1, 'DECL_RELATIVE_AMBIGUOUS': 1, 'DECL_ENV': 4, 'DECL_GENERALIZED': 6, 'JSON_PARSE': 2, 'DECL_DESTINATION_UNRESOLVED': 1}. The <=10 goal is **not** met: 10 of the 15 are the explicitly policy-gated generalized/env declarations and 5 are genuine non-policy residuals; reaching <=10 would require either weakening fail-closed semantics or editing frozen history, both forbidden by the Task.

