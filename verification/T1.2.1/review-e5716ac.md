# T1.2.1 R5 Non-author Review — `e5716ac`

## Decision

**REVIEW APPROVED — B-003 CLOSED; integration verified.**

The R5 implementation is within the authorized bootstrap seam, its new
assembly tests are discriminating, the fail-closed comparison test passes,
and the independent production probe proves the real credential path. The
delivery was integrated by Codex at `9a14310` and independently verified at
`e92c414`. This report records the fixed-head non-author review and the fresh
reviewer checks below; later mainline commits do not change the reviewed R5
code.

## Fixed inputs and worktree

| Field | Value |
|---|---|
| Task | T1.2.1 Settings UI & ViewModel — R5 B-003 repair |
| Author | ZCode |
| Reviewer / Integrator | Codex, non-author |
| R5 base | `39dbbf7` |
| Implementation commit | `e5716ac` |
| Handoff / evidence commits | `e025c9a` + `b8a8841` (§10.6 authorization supplement) |
| Branch | `agent/zcode/T1.2.1-settings-ui-viewmodel` |
| Worktree | `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel` |
| Final author HEAD | `b8a8841449135320337c9bc9736f85b695d8ab2a` |
| Author worktree | clean |

The implementation commit contains the production and test changes. The
Handoff commit adds §10 and the redacted author probe; `b8a8841` adds only the
user authorization supplement in §10.6. Author history was not rewritten.

## Scope audit

`git diff 39dbbf7..e5716ac --stat` contains only:

```text
src/bootstrap/app.py
tests/core/test_transport_credential_assembly.py
```

The complete R5 delivery (`39dbbf7..b8a8841`) contains only the two paths
above plus:

```text
doc/handoffs/T1.2.1-zcode-handoff.md
verification/T1.2.1/author-r5-credential-store-probe.md
```

The final diff also contains the Handoff-only §10.6 authorization supplement;
it does not alter production code or tests.

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

### Handoff §10.6 authorization confirmation

The author branch final head `b8a8841` records the user's explicit
authorization for the single allowed path drift: deleting the independent
SettingsViewModel vault construction and making transport, provider resolver,
and SettingsViewModel consume the assembly-local store. The implementation is
confined to `src/bootstrap/app.py`; no further scope expansion is inferred.

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

Independent reviewer rerun on the current integrated mainline used PowerShell
and the same Python 3.12 venv:

```text
python -m pytest tests/core/test_transport_credential_assembly.py tests/network/test_transport_local.py tests/providers/test_provider_binding_projection.py tests/ui_shell/test_settings_viewmodel.py tests/core/test_bootstrap.py tests/network/test_settings_profile_persistence.py -q -rs -p no:cacheprovider
95 passed, 0 skipped, exit 0
```

The reviewer also reran the production-chain probe with a temporary script:

```text
COMPLETE_EXCEPTION=ProviderInvalidOutput
ASSEMBLY_X2=PASS
REGISTRY_RESOLVE=PASS
PROXY_FORWARD_AUTH_HEADERS_MATCH=True
PROXY_AUTH_FAILURES=0
TARGET_REQUESTS=1
SECRET_EXPOSED_IN_OUTPUT=False
R5_REVIEW_PROBE=PASS
VAULT_CLEANUP=True
PROBE_EXIT=0
```

`ProviderInvalidOutput` is expected response-format noise after the local
target returned HTTP 200; the authenticated forward and exact Basic header
assertions are the decisive transport evidence.

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
Codex integration: VERIFIED at `9a14310`; evidence `e92c414`
T1.2.1: VERIFIED_COMPLETE
T2.1.1: NOT_STARTED at the R5 review point; current STATUS later records it
as VERIFIED_COMPLETE at `5da1cf6`
```

Evidence source: [author probe](author-r5-credential-store-probe.md).

## Next task

- **Task**: `T2.2.1 Reader & Workbench Polish`; first obtain its own Codex
  Release Gate. Dependency `T2.1.1` is now integrated.
- **Agent**: ZCode for the implementation; Codex as non-author reviewer and
  integrator. Qoder remains responsible for QML/UI/UX decisions.
- **Recovery point**: `G:\CODEX\New Manga`, `master`, current head
  `24c8005`; implementation branch/worktree is **待 Codex 创建**.
- **Scope**: only the paths released by `doc/tasks/T2.2.1.md`; no shared
  contract, Schema, dependency, or unrelated QML changes without a new Task
  authorization.
- **Deliverables**: implementation, focused tests, Handoff, Review and
  `verification/T2.2.1/**` evidence.
- **Verification**: record shell, interpreter, full counts, skips and exit
  codes; run the Task-focused suite, compile, smoke and non-author review
  before marking `done`.

Forwardable instruction:

> Codex: first create/release the T2.2.1 Release Gate from `master` at
> `24c8005`; do not start implementation before its dependencies and allowed
> paths are frozen. After release, assign ZCode to the isolated implementation
> worktree, require focused tests/Handoff/verification with shell, venv,
> counts, skips and exit codes, then perform non-author review and serial
> integration. Do not modify T1.2.1 history or merge from ZCode.
