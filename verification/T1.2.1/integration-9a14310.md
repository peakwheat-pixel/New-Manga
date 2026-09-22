# T1.2.1 Integration Verification — code HEAD `9a14310`

## Integration decision

Codex integrated the approved ZCode T1.2.1 delivery in an isolated worktree.
The merge preserves the complete author branch as the second parent of the
integration merge commit; author history was not rewritten. The product code
is ready for mainline fast-forward integration. The known full-suite failure
is an existing environment assertion and is not a T1.2.1 failure.

| Field | Value |
|---|---|
| Mainline base | `ade5814` |
| Author branch | `agent/zcode/T1.2.1-settings-ui-viewmodel` |
| Author delivery | `e025c9a`; authorization supplement `b8a8841` |
| Integration branch | `agent/codex/T1.2.1-r5-integration` |
| Integration worktree | `G:\CODEX\New Manga.worktrees\T1.2.1-r5-integration` |
| Code integration HEAD | `9a14310` |
| Integration method | merge preserving author branch as second parent |

## Scope and history

The final product diff from the mainline base contains the complete T1.2.1
implementation: provider settings stores/ViewModel, Settings QML, provider
binding projection/runtime fixes, bootstrap assembly, focused tests, and the
author Handoff/probe evidence. No ports, SQLite schema, dependencies, or
unrelated agent files were added by the T1.2.1 delivery. The R5 code change
itself remains limited to `src/bootstrap/app.py` and the assembly test.

The merge was required because master had not yet integrated the earlier
c54/R3/R4 T1.2.1 implementation commits. A partial R5-only cherry-pick would
have omitted those prerequisites; the final tree includes them and retains
the ZCode commit chain as the merge's second parent.

The later `b8a8841` commit is Handoff-only: it records the user's explicit
§10.6 authorization for the already-reviewed assembly seam. It adds no
production or test code; Codex preserved it on mainline as commit `24c8005`.

## Final integration verification

Python interpreter:

```text
G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe
PYTHONPATH=src
```

| Check | Shell / result | Exit |
|---|---|---:|
| T1.2.1 focused integration set | PowerShell: 122 passed, 0 skipped | 0 |
| Full suite | Git Bash: 1139 passed, 1 known torch readiness failure, 0 skipped, 1 warning | 1 |
| Full suite | PowerShell: 1133 passed, 6 OpenSSL skips, 1 known torch readiness failure, 1 warning | 1 |
| Compile | PowerShell `python -m compileall -q src tests` | 0 |
| Bootstrap smoke | PowerShell, six fresh data roots: 6/6 passed | 0 |
| Integration diff check | `git diff --check master..HEAD -- src tests doc verification` | 0 |
| Source protection | Full suite source/managed-copy protection tests included and passed | PASS |

The only failure is
`tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment`:
the selected implementation venv contains `torch`. PowerShell's six skips
are the existing OpenSSL-gated TLS cases. These are recorded as environment
evidence, not claimed as an all-green suite.

## Production credential path probe

Fresh probe on integration code HEAD:

```text
FINAL_ASSEMBLY_X2=PASS
FINAL_SQLITE_BINDING_AND_RESOLVE=PASS
FINAL_PROXY_AUTH_HEADER_MATCH=True
FINAL_PROXY_AUTH_FAILURES=0
FINAL_SECRET_EXPOSED=False
FINAL_TARGET_REQUESTS=1
FINAL_PROBE=PASS
FINAL_VAULT_CLEANUP=True
FINAL_PROBE_EXIT=0
```

The probe used two real `assemble_services` calls, a random Windows
Credential Manager reference, a persisted `pipeline_defaults` row, production
registry resolution, the provider client, a local controlled forward proxy,
and a local target. The exact `Proxy-Authorization` header was asserted; the
secret was absent from SQLite/output and was deleted in `finally`.

## Gate

```text
R5 B-003: VERIFIED
Production bootstrap path: VERIFIED
Shared credential-store instance: VERIFIED
Fail-closed missing credential path: VERIFIED
Focused tests: PASS
Full suite: PASS for product scope; known environment assertion documented
compileall: PASS
bootstrap smoke: PASS
diff check: PASS
BLOCKING findings: 0
```

This evidence authorizes Codex to fast-forward master to the integration
branch and then update `STATUS` and the Task record. T2.1.1 remains gated
until that mainline bookkeeping is complete.
