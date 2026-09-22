# T1.2.1 R5 Non-author Review — `e5716ac`

## Decision

**REVIEW APPROVED — B-003 CLOSED FOR INTEGRATION.**

The R5 implementation is within the authorized bootstrap seam, its new
assembly tests are discriminating, the fail-closed comparison test passes,
and the independent production probe proves the real credential path. The
delivery is now eligible for Codex integration and final mainline
verification. It is not yet `VERIFIED_COMPLETE` until that integration
verification finishes.

## Fixed inputs and worktree

| Field | Value |
|---|---|
| Task | T1.2.1 Settings UI & ViewModel — R5 B-003 repair |
| Author | ZCode |
| Reviewer / Integrator | Codex, non-author |
| R5 base | `39dbbf7` |
| Implementation commit | `e5716ac` |
| Handoff / evidence commit | `e025c9a` |
| Branch | `agent/zcode/T1.2.1-settings-ui-viewmodel` |
| Worktree | `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel` |
| Final author HEAD | `e025c9a04b8fcd9043985836f6c609312dc25ba5` |
| Author worktree | clean |

The implementation commit contains the production and test changes. The
Handoff commit adds §10 and the redacted author probe. Author history was not
rewritten.

## Scope audit

`git diff 39dbbf7..e5716ac --stat` contains only:

```text
src/bootstrap/app.py
tests/core/test_transport_credential_assembly.py
```

The complete R5 delivery (`39dbbf7..e025c9a`) contains only the two paths
above plus:

```text
doc/handoffs/T1.2.1-zcode-handoff.md
verification/T1.2.1/author-r5-credential-store-probe.md
```

No ports, SQLite schema, dependencies, QML, Roadmap, STATUS, or unrelated
agent files were changed by the author delivery. The diff is whitespace-clean.

## Standards

No documented repository standard is violated. The change keeps the existing
application-to-infrastructure assembly direction, reuses the existing
`WindowsCredentialStore` and `StdlibTransport(credential_store=...)` seams,
and adds no parallel abstraction or dependency.

The only observability addition is the existing-style `AppServices.transport`
field, used by assembly tests to inspect the object actually built by
production assembly. It does not create a second transport path.

## Spec and implementation review

### `_credential_store()` fallback

`src/bootstrap/app.py` defines one best-effort construction point. Import or
constructor failures caught by `except Exception` return `None`; startup does
not fail merely because the optional Windows vault cannot be opened. The
existing typed failure behavior remains: providers report missing credential
readiness and transport raises `MissingCredentialError` for an authenticated
proxy without a credential source. No silent direct fallback is introduced.

### Shared instance at production assembly

`assemble_services()` constructs one local `credential_store` and passes the
same object to:

```text
StdlibTransport(credential_store=credential_store)
_credential_resolver(credential_store)
SettingsViewModel(credential_store=credential_store)
```

The transport and provider resolver therefore cannot silently diverge to
separate vault instances.

### Handoff §10.2③ scope decision

**Confirmed in scope.** Removing the SettingsViewModel-local vault
construction and using the already-created assembly instance is part of the
same authorized production assembly seam. It is in `src/bootstrap/app.py`,
removes a second failure policy that only caught `ImportError`, and is needed
to make the required “any vault construction failure → None” behavior true
for the whole production assembly. No rollback is required.

### Tests and discriminating evidence

The four new assembly tests cover:

1. real assembled transport owns a `WindowsCredentialStore`;
2. constructor failure returns `None` and assembly still succeeds;
3. import failure returns `None`;
4. resolver uses the same store and resolves a real vault roundtrip.

The existing `test_missing_proxy_credential_is_config_error_not_network`
continues to prove that no credential does not become a network request or a
silent direct connection.

## Independent production probe

Fresh reviewer probe reproduced the required chain:

```text
assemble_services ×2
→ real WindowsCredentialStore with random credential_ref
→ SQLite pipeline_defaults settings/binding row
→ second production assembly
→ registry.resolve("translation", PROFILE_ID)
→ provider.client.complete()
→ ControlledProxyServer(mode="forward")
→ LocalTargetServer
```

Fresh output:

```text
ASSEMBLY_1_TRANSPORT_STORE=WindowsCredentialStore
ASSEMBLY_2_TRANSPORT_STORE=WindowsCredentialStore
REGISTRY_RESOLVE=translation:r5-probe-profile->openai-compatible-translation
PROXY_FORWARD_AUTH_HEADERS_MATCH=True
PROXY_AUTH_FAILURES=0
TARGET_REQUESTS=1
SECRET_EXPOSED_IN_OUTPUT=False
R5_PRODUCTION_PROBE=PASS
VAULT_CLEANUP=True
R5_PROBE_EXIT=0
```

The exact expected Basic header was asserted in-process and the random vault
credential was deleted in `finally`. The local target intentionally returns a
non-chat JSON response; the expected provider-output error occurs after the
authenticated proxy forwarding and does not invalidate the transport proof.

## Fresh verification

All Python runs used:

```text
G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe
PYTHONPATH=src
```

| Check | Shell / result | Exit |
|---|---|---:|
| R5 assembly + fail-closed focused | PowerShell: 5 passed | 0 |
| R5 focused integration set | PowerShell: 90 passed, 0 skipped | 0 |
| Full suite | Git Bash: 1139 passed, 1 known environment failure, 0 skipped, 1 warning | 1 |
| Full suite | PowerShell: 1133 passed, 6 OpenSSL skips, 1 known environment failure, 1 warning | 1 |
| Compile | PowerShell `python -m compileall -q src tests` | 0 |
| Bootstrap smoke | PowerShell, six fresh data roots: 6/6 passed | 0 |
| Diff check | `git diff --check 39dbbf7..e5716ac -- src tests doc verification` | 0 |
| Production credential probe | PowerShell, fresh local servers and Windows vault | 0 |

The only full-suite failure in both shells is
`tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment`,
because this implementation venv contains `torch`. The six PowerShell skips
are the existing `shutil.which("openssl")`-guarded TLS cases; Git Bash finds
Git's OpenSSL and executes them. These are recorded as environment evidence,
not represented as an all-green suite.

## Findings

### BLOCKING

None for R5. B-003 is closed by the production probe and fresh assembly
verification.

### IMPORTANT

None. The shell-dependent skip count and known torch assertion are existing
environment conditions and were not caused by this delivery.

### NON_BLOCKING

None introduced by R5.

## Gate

```text
R5 scope: PASS
B-003 production credential-store injection: PASS
Shared vault instance: PASS
Fail-closed missing credential behavior: PASS
Fresh focused tests: PASS
Full suite: known environment failure only
compileall: PASS
bootstrap smoke: PASS
diff check: PASS
Codex integration: AUTHORIZED / NEXT STEP
T1.2.1: READY_FOR_INTEGRATION_VERIFICATION
T2.1.1: NOT_STARTED
```

Evidence source: [author probe](author-r5-credential-store-probe.md).

## Next task

Codex now performs the serial T1.2.1 integration in an isolated integration
worktree, reruns the final gate, and only then updates `STATUS` and the Task
to `done`/`VERIFIED_COMPLETE`. ZCode must not merge master. T2.1.1 remains
unreleased until the integration gate closes.
