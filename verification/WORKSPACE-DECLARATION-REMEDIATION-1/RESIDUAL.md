# RESIDUAL — remaining real-repository audit errors (after remediation)

Source: `audit-after.json` (same command/snapshot as `audit-before.json`). **15 errors remain; none is silent.**

| # | code | file | tracked | owner | locator | why the parser cannot fix it | suggested ruling |
|---:|---|---|---|---|---|---|---|
| 1 | TABLE_ROW_ARITY | `doc/tasks/GOV-DEBT-CLEANUP-2.md` | tracked | historical Task GOV-DEBT-CLEANUP-2 |  | genuinely malformed resource table (7 vs 6 columns); AC5 keeps it fatal | Codex ruling: fix the historical table (not done: history is frozen) |
| 2 | DECL_RELATIVE_AMBIGUOUS | `doc/tasks/P19.md` | tracked | historical Task P19 | line 5 | relative path could mean repo or workspace root | User ruling: pin repo-relative or workspace-relative intent |
| 3 | DECL_ENV | `doc/tasks/P19.md` | tracked | historical Task P19 | line 6 | value contains %ENV% or ${ENV}; expansion target is not provable | User ruling: expand the env token in this historical Task, or confirm ignore |
| 4 | DECL_ENV | `doc/tasks/P19.md` | tracked | historical Task P19 | line 7 | value contains %ENV% or ${ENV}; expansion target is not provable | User ruling: expand the env token in this historical Task, or confirm ignore |
| 5 | DECL_GENERALIZED | `doc/tasks/SEC-FIX-PATH-ECHO-1.md` | tracked | historical Task SEC-FIX-PATH-ECHO-1 | line 5 | declaration intentionally names the workspace root / a managed-area root; AC1 policy role, not parse precision | Codex ruling: narrow to a concrete resource, or record a blanket protection policy |
| 6 | DECL_GENERALIZED | `doc/tasks/WORKSPACE-CONSOLIDATION-1.md` | tracked | historical Task WORKSPACE-CONSOLIDATION-1 | line 10 | declaration intentionally names the workspace root / a managed-area root; AC1 policy role, not parse precision | Codex ruling: narrow to a concrete resource, or record a blanket protection policy |
| 7 | DECL_GENERALIZED | `doc/tasks/WORKSPACE-CONSOLIDATION-1.md` | tracked | historical Task WORKSPACE-CONSOLIDATION-1 | line 11 | declaration intentionally names the workspace root / a managed-area root; AC1 policy role, not parse precision | Codex ruling: narrow to a concrete resource, or record a blanket protection policy |
| 8 | DECL_GENERALIZED | `doc/tasks/WORKSPACE-CONSOLIDATION-1.md` | tracked | historical Task WORKSPACE-CONSOLIDATION-1 | line 12 | declaration intentionally names the workspace root / a managed-area root; AC1 policy role, not parse precision | Codex ruling: narrow to a concrete resource, or record a blanket protection policy |
| 9 | DECL_GENERALIZED | `doc/tasks/WORKSPACE-CONSOLIDATION-1.md` | tracked | historical Task WORKSPACE-CONSOLIDATION-1 | line 14 | declaration intentionally names the workspace root / a managed-area root; AC1 policy role, not parse precision | Codex ruling: narrow to a concrete resource, or record a blanket protection policy |
| 10 | DECL_GENERALIZED | `doc/tasks/WORKSPACE-CONSOLIDATION-1.md` | tracked | historical Task WORKSPACE-CONSOLIDATION-1 | line 15 | declaration intentionally names the workspace root / a managed-area root; AC1 policy role, not parse precision | Codex ruling: narrow to a concrete resource, or record a blanket protection policy |
| 11 | JSON_PARSE | `verification/P02-NEW-TIME-BASELINE/run-baseline-20261014T0430CST-ac3fix.json` | untracked | evidence P02-NEW-TIME-BASELINE |  | unparsable JSON contains declaration tokens; cannot prove protection is complete | Codex ruling: replace with a single valid JSON document or declare it non-declaration |
| 12 | JSON_PARSE | `verification/P02-NEW-TIME-BASELINE/run-baseline-20261014T0915CST-p02-admission-r2.json` | tracked | evidence P02-NEW-TIME-BASELINE |  | unparsable JSON contains declaration tokens; cannot prove protection is complete | Codex ruling: replace with a single valid JSON document or declare it non-declaration |
| 13 | DECL_DESTINATION_UNRESOLVED | `verification/P19-UI-FIX-1/resource-manifest.json` | tracked | evidence P19-UI-FIX-1 | $.resources[1].destination_path | path-like destination prose; F-03 keeps it an integrity error | Codex ruling: treat as prose or fix the value |
| 14 | DECL_ENV | `verification/P19-UI-FIX-1/resource-manifest.json` | tracked | evidence P19-UI-FIX-1 | $.resources[2].disposition | value contains %ENV% or ${ENV}; expansion target is not provable | User ruling: expand the env token in this historical Task, or confirm ignore |
| 15 | DECL_ENV | `verification/P19-UI-FIX-1/resource-manifest.json` | tracked | evidence P19-UI-FIX-1 | $.resources[3].disposition | value contains %ENV% or ${ENV}; expansion target is not provable | User ruling: expand the env token in this historical Task, or confirm ignore |

## Grouping

- `DECL_DESTINATION_UNRESOLVED`: 1
- `DECL_ENV`: 4
- `DECL_GENERALIZED`: 6
- `DECL_RELATIVE_AMBIGUOUS`: 1
- `JSON_PARSE`: 2
- `TABLE_ROW_ARITY`: 1

## Why 15 rather than <=10

`DECL_GENERALIZED` (6) and `DECL_ENV` (4) are the policy-gated declarations the Task explicitly keeps for Codex/user ruling; `DECL_RELATIVE_AMBIGUOUS` (1), `TABLE_ROW_ARITY` (1), `JSON_PARSE` (2) and the destination-prose error (1) are genuine gaps. Reaching <=10 would require weakening fail-closed semantics (forbidden) or editing 107 historical files (forbidden).

## Not done / not claimed

- No historical Task/evidence/untracked file was edited to lower the count.
- No real apply/delete/move/GC/prune was executed.
