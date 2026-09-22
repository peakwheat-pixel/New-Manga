# T1.2.1 R3 Blocker Repair — Non-author Review

Date: 2026-09-22  
Reviewer: Codex  
Author: ZCode  
Review base: `d11d927`  
R3 implementation: `d978d6f`  
R3 Handoff: `7376bce`  
R1 implementation/Handoff: `c54f360` / `ace633a`  
Branch: `agent/zcode/T1.2.1-settings-ui-viewmodel`  
Worktree: `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`

## Verdict

**CHANGES_REQUESTED — R3 REVIEW BLOCKED.**

R3 closes the previously demonstrated happy path for one translation profile:
the SQLite `pipeline_defaults` row can be loaded, projected onto the fixed
translation registry slot, and its named network profile reaches a recording
transport. However, independent edge probes find unresolved production
contract failures in aliasing, proxy policy semantics, disabled profiles,
missing network profiles, and proxy credential construction. These are
acceptance-level blockers; no integration worktree was promoted and T2.1.1
was not started.

## Scope and commit review

The author worktree was clean at `7376bce954e700c43a4fed5dbdc43b71580c3fcf`.
`d978d6f` is the implementation commit; `7376bce` is the Handoff-only commit.

`git diff --stat ace633a..d978d6f` is exactly:

```text
src/bootstrap/app.py                               |   3 +
src/infrastructure/providers/registry.py           |  12 +-
src/infrastructure/providers/runtime.py            | 148 +++++++++-
src/ui/viewmodels/settings/viewmodel.py            | 136 +++++++++-
tests/providers/test_provider_binding_projection.py | 301 +++++++++++++++++++++
tests/ui_shell/test_settings_viewmodel.py          | 120 +++++++-
6 files changed, 710 insertions(+), 10 deletions(-)
```

No QML, `src/ports/**`, SQLite schema/migrations, Roadmap, STATUS, or
unrelated agent file is present in the R3 implementation diff. The requested
bootstrap seam is limited to passing `provider_bindings`; the additional
runtime/registry scope is the explicitly authorized B-001/B-002 seam.

## Architecture review

### Accepted aspects

- Projection is performed at runtime assembly rather than hard-coded in QML.
- The input settings mapping is copied rather than mutated.
- Unknown user profile ids do not create registry entries and remain
  fail-closed on the tested path.
- The happy path preserves the user profile id in the persisted binding while
  resolving against a fixed provider slot.
- The new tests cover string/mapping bindings, Sakura/vision slot selection,
  network profile construction, transport hand-off, and mirror immutability.

### BLOCKING R3-B001 — one profile id cannot alias multiple capability slots

`ProviderRegistry.binding_aliases` is a single `profile_id -> registry_id`
mapping. `_apply_profile_bindings()` overwrites that value when the same user
profile is bound to more than one step. `ProviderProfile.capabilities` allows
multi-capability profiles, and the Settings UI exposes the same profile list
for each capability; no current contract forbids one profile being bound to
both translation and OCR.

Fresh edge probe:

```text
bindings = {'translate': 'shared', 'ocr': 'shared'}
MULTI_BINDING translation= ProviderNotConfigured: provider 'openai-vision-ocr' does not declare capability 'translation'
MULTI_BINDING ocr= resolved
```

The projection copied the profile into both fixed slots, but the single alias
selected the last slot. A valid multi-capability profile therefore resolves to
the wrong provider for at least one bound capability.

### BLOCKING R3-B002 — proxy policy is not preserved or applied

The ViewModel mirror omits `proxy_policy`, and `_network_profile_for()` selects
`network_profile_id` without consulting the existing
`ProviderNetworkResolver` contract:

- `direct` must ignore any named network profile;
- `profile` must use the named profile and fail when it is missing;
- `inherit` must use the effective `network.profile_id` setting, or direct
  only when no effective setting exists.

Fresh edge probes:

```text
proxy_policy=direct, network_profile_id=proxy
DIRECT_POLICY mode= socks5

proxy_policy=profile, network_profile_id=missing
MISSING_NETWORK mode= None
```

The first result proves a configured direct policy is ignored. The second
silently falls back to direct instead of raising the existing typed settings
error. The global `network.profile_id` setting is not read by the new runtime
projection either. This is a behavioral and safety regression, not a visual
or future-enhancement issue.

### BLOCKING R3-B003 — proxy credential store is absent from production transport

`src/bootstrap/app.py` constructs `StdlibTransport()` without a
`credential_store`, while the same bootstrap path constructs a separate
Windows credential resolver for provider API credentials. `StdlibTransport`
requires its own credential store to resolve a network profile's
`credential_ref`; otherwise an authenticated proxy reaches
`MissingCredentialError`.

The R3 recording transport test proves that a `NetworkProfile` object reaches
the transport, but it does not prove that the real production transport can
resolve the persisted proxy password. The production construction seam is
therefore still incomplete for the credential-bearing proxy case.

### BLOCKING R3-B004 — disabled fixed-slot profile remains resolvable

The new fail-closed test uses an arbitrary disabled profile id. A disabled
profile whose id already equals a fixed registry slot takes the `target ==
profile_id` path, and registry registration does not apply the profile's
`enabled` flag. Fresh probe:

```text
fixed profile id: openai-compatible-translation
enabled: False
DISABLED_FIXED resolved=True
```

This violates the R3 design statement that disabled profiles remain
unprojected and resolution stays unavailable. It also makes the result depend
on whether the user chose a fixed-looking id.

### BLOCKING R3-B005 — capability declaration is not checked at binding time

`SettingsViewModel.saveBinding()` checks only that the profile exists. It does
not require the requested capability to be in `ProviderProfile.capabilities`.
The QML binding model is not filtered by capability. A profile declared for a
different capability can therefore be projected into a remote slot and used
for the wrong pipeline step. The registry descriptor check cannot recover the
user's profile declaration after projection.

## Verification review

All commands below were run from the R3 author worktree with PowerShell and:

```text
G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe
PYTHONPATH=src
```

| Check | Fresh result | Exit |
|---|---|---:|
| `pytest tests/ui_shell tests/network tests/providers -q -rs -p no:cacheprovider` | `410 collected = 403 passed + 6 skipped + 1 failed`; failure is the expected torch registry-readiness assertion; six skips are OpenSSL-unavailable TLS tests | 1 |
| `pytest tests -q -rs -p no:cacheprovider` | `1124 collected = 1117 passed + 6 skipped + 1 failed`, 1 warning; same expected torch registry-readiness failure | 1 |
| `python -m compileall -q src tests` | passed | 0 |
| six `python -m bootstrap.app --smoke-test --data-root <fresh-temp-dir>` runs | `6/6` exit 0 | 0 |
| `git diff --check -- src tests doc verification` | clean | 0 |
| production SQLite-row → `_load_pipeline_settings`/`_load_pipeline_defaults` → `build_provider_runtime` probe | resolved fixed translation slot; recording transport received `corp-proxy` SOCKS5; no secret in mirror | 0 |
| independent edge probe | reproduced B-001 and B-002/B-004 failures above | 0 |

The Handoff reports `409 passed, 1 failed` and `1123 passed, 1 failed` with no
skips in the implementation venv. The exact venv and PowerShell invocation
used here produced six OpenSSL skips in both runs. The total collected count
still matches the R3 claim (`410` focused and `1124` full), so this is an
environment/evidence split, not a new product failure; it must nevertheless be
recorded as `403 passed + 6 skipped`, not silently counted as passed.

The full-suite warning is the existing MOBI/imghdr deprecation warning. No
T1.2.1 test failed apart from the known environment assertion.

## Production-path probe result

The happy-path probe is valid but narrower than the acceptance gate. It used a
fresh migrated SQLite database, inserted the same `providers` mirror shape and
`translate -> my-openai-profile` binding, then loaded the row through the two
production bootstrap readers before calling `build_provider_runtime`. It
reported:

```text
LOADED_SECTIONS= ['providers']
LOADED_BINDINGS= {'translate': 'my-openai-profile'}
RESOLVED_PROVIDER= openai-compatible-translation
TRANSPORT_NETWORK= corp-proxy socks5 socks5://gateway.internal:1080
SECRET_IN_MIRROR= False
PRODUCTION_PROBE_EXIT=0
```

This proves B-003's happy path and the basic B-001/B-002 projection path, but
does not override the edge failures or prove an authenticated real
`StdlibTransport` route.

## Findings disposition

| Finding | Disposition |
|---|---|
| R3-B001 multi-capability alias collision | **MERGE required before approval** |
| R3-B002 proxy policy / missing-network semantics | **MERGE required before approval** |
| R3-B003 production proxy credential store | **MERGE required before approval** |
| R3-B004 disabled fixed-slot profile | **MERGE required before approval** |
| R3-B005 capability-to-binding validation | **MERGE required before approval** |
| R3 focused/full skip-count discrepancy | **IMPORTANT — correct evidence** |
| R1 QML context-property uniform hardening | **NON_BLOCKING — DEFER** |
| JSON → SQLite migration | **NON_BLOCKING — DEFER to T3.1.1** |

## Gate decision

`T1.2.1 = REVIEW_BLOCKED / IMPLEMENTED_NOT_VERIFIED`.

No R3 product commit is integrated into `master`. The author must produce a
new delivery after the blocking findings are resolved, with focused tests for
policy semantics, multi-capability bindings, disabled fixed slots, proxy
credential resolution, and a fresh production-path probe. Codex then performs
another non-author review before any integration window.
