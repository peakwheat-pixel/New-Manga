# T1.2.1 Settings UI & ViewModel — Non-author Review

Date: 2026-09-22  
Reviewer: Codex  
Author: ZCode  
Review base: `d11d927`  
Reviewed delivery: `c54f360`  
Author handoff commit: `ace633a`  
Author branch: `agent/zcode/T1.2.1-settings-ui-viewmodel`  
Author worktree: `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`

## Verdict

**CHANGES_REQUESTED — NOT APPROVED FOR INTEGRATION.**

The delivery is clean and its implementation diff stays within the requested
product paths, but the production path is not yet closed. There are three
blocking findings: provider profile data is not fully resolvable by the
production registry, network/proxy settings are not passed to the runtime
transport, and the original delivery did not mirror provider profile writes to
the pipeline settings read by bootstrap. A minimal mirror fix was made only in
the isolated Codex candidate and is not merged to `master`; the two runtime
contract blockers remain.

## Delivery and scope checks

The author worktree was clean and its final handoff HEAD was `ace633a`; the
requested delivery commit `c54f360` is the implementation commit immediately
below it. `git diff --stat d11d927..c54f360` reported 8 files and 1566 added,
3 removed lines:

```text
src/bootstrap/app.py
src/infrastructure/settings/__init__.py
src/infrastructure/settings/json_profile_stores.py
src/ui/qml/settings/SettingsView.qml
src/ui/viewmodels/settings/__init__.py
src/ui/viewmodels/settings/viewmodel.py
tests/network/test_settings_profile_persistence.py
tests/ui_shell/test_settings_viewmodel.py
```

No SQLite schema, `src/ports/**`, QML shell, Roadmap, STATUS, or other agent
dirty file was changed by the author delivery. The author handoff itself is
the separate `ace633a` documentation commit.

## Review axes

### Standards / architecture

- QML uses the `settingsViewModel` context property and does not directly open
  databases, files, or models.
- Persistence is behind settings stores/services; secrets are represented by
  credential references and are resolved through the credential store.
- Bootstrap constructs `SettingsViewModel` and exposes it to QML.
- The QML context-property race defense (null guards, imperative signal
  connections, and initial refresh) is acceptable for this page. Six fresh
  bootstrap smoke runs produced no matching QML error text. Uniform adoption
  across the existing four pages is deferred to a later QML-hardening review;
  it is not silently treated as a T1.2.1 integration requirement.

### Specification / production behavior

#### BLOCKING B-001 — provider profile is not a resolvable production binding

The Settings UI permits arbitrary `provider_profile_id` values and writes a
binding using that value. The production registry, however, registers fixed
provider IDs in `src/infrastructure/providers/runtime.py`, while
`ProviderRegistry.resolve_binding()` resolves the binding as a registry ID.

Fresh production-path probe in the Codex candidate:

```text
profile id: openai-translation
binding: translation -> openai-translation
result: ProviderUnavailable: no provider registered as 'openai-translation'
exit: 1
```

The same probe showed that the saved profile was present in the pipeline
settings after reassembly, but it did not become a registered provider. This
is a real production-path failure, not a unit-test injection issue. It cannot
be closed by changing only the SettingsViewModel; the provider profile-to-
adapter/registry seam must be explicitly resolved in the approved integration
scope or the task contract must be narrowed and re-approved.

#### BLOCKING B-002 — network/proxy settings do not reach the transport

`saveNetworkProfile()` persists the profile to the JSON network store, but the
production runtime assembly reads only the pipeline settings map. The runtime
`_openai_config()` creates `OpenAiCompatibleConfig` without its
`network_profile`; `OpenAiCompatibleClient` therefore uses the direct default
profile. The UI's `network_profile_id` and `proxy_policy` are not included in
the runtime profile shape either.

Result: endpoint/model settings can be present while the configured proxy,
TLS policy, bypass list, or proxy credential is ignored by actual provider
transport. This violates the stated acceptance that proxy settings feed the
pipeline. Do not close this by changing the acceptance wording; add the
minimal approved runtime seam or return the task for scope authorization.

#### BLOCKING B-003 — original provider save path did not feed bootstrap settings

At `c54f360`, `saveProviderProfile()` updated only the JSON provider profile
store. Bootstrap builds `provider_runtime` from `_load_pipeline_settings(conn)`
before constructing the SettingsViewModel, so a restart/production assembly
could not see the provider saved by the Settings UI.

Codex added a focused red/green check in an isolated candidate:

```text
before fix: KeyError: 'providers'        exit 1
after fix:  1 passed                     exit 0
```

The candidate fix is committed as `0b4e434` on
`agent/codex/T1.2.1-integration`, but is not merged to `master`. It is a
partial repair only; B-001 and B-002 remain open.

## Important findings

### IMPORTANT I-001 — focused evidence count is misstated

The handoff says “166 passed” for the focused settings/network run. A fresh
run on the author worktree collected the same 166 tests as **160 passed and 6
skipped**, exit 0. All six skips are existing OpenSSL-unavailable network/TLS
cases. The count must be corrected in the final evidence; this is not itself a
product failure.

### NON_BLOCKING / deferred D-001 — four-page context-property hardening

The SettingsView defense is sufficient for this slice. Applying the same
pattern to all four existing pages is a candidate backlog item, not a reason
to expand this task.

### NON_BLOCKING / deferred D-002 — JSON to SQLite migration

The handoff correctly defers migration of profile stores to T3.1.1. No schema
change is requested or made here.

### NON_BLOCKING D-003 — QML exposes credential reference metadata

The ViewModel exposes `credential_ref` alongside `credential_set`. The
credential secret is not exposed and the tests verify the secret is absent;
the reference is metadata rather than the secret. Keep the public UI contract
documented consistently in a later hardening pass.

## Verification evidence

Author worktree focused rerun:

```text
pytest tests/ui_shell tests/network -q -p no:cacheprovider
160 passed, 6 skipped in 8.43s
exit 0
```

The handoff's full-suite claim was also independently checked against the
fresh Codex candidate after the partial B-003 repair:

```text
pytest tests -q -rs -p no:cacheprovider
1094 passed, 6 skipped, 1 failed, 1 warning
exit 1
```

The sole failure is the known environment assertion
`tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment`
because this implementation environment contains torch. No T1.2.1 test
failed. The six skips are OpenSSL-unavailable TLS cases; the warning is the
existing MOBI/imghdr deprecation warning.

Additional fresh candidate evidence:

| Check | Result | Exit |
|---|---:|---:|
| `pytest tests/ui_shell tests/network -q -rs -p no:cacheprovider` | 161 passed, 6 skipped | 0 |
| `python -m compileall -q src tests` | passed | 0 |
| `python -m bootstrap.app --smoke-test --data-root <fresh-temp-dir>` | passed | 0 |
| source-protection subset (`tests/library/test_import_images.py` and `tests/workbench/test_region_create_persistence.py`) | 15 passed | 0 |
| `git diff --check -- src tests doc verification` | passed | 0 |
| six repeated QML/bootstrap smoke launches | 6/6 clean; no matching QML error text | 0 |

## Findings disposition

| Finding | Disposition |
|---|---|
| B-001 provider profile registry resolution | **MERGE required before approval** |
| B-002 network/proxy runtime application | **MERGE required before approval** |
| B-003 provider profile to pipeline settings | **PARTIAL MERGE in candidate; final verification required** |
| I-001 focused count correction | **MERGE evidence correction** |
| D-001 four-page QML hardening | **DEFER / Candidate Backlog** |
| D-002 JSON→SQLite | **DEFER to T3.1.1** |
| D-003 credential-ref metadata contract | **DEFER** |

## Decision

T1.2.1 remains **REVIEW_BLOCKED / IMPLEMENTED_NOT_VERIFIED**. No product code
from the candidate has been merged to `master`; ZCode must not merge or start
T2.1.1. Re-review is required after the two production-path blockers are
resolved with focused tests and fresh bootstrap/runtime evidence.
