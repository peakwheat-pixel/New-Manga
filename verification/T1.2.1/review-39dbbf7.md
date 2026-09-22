# T1.2.1 R4 Non-author Review — `39dbbf7`

## Decision

**R4 implementation review: APPROVED for the resolved R3 edge seams.**

**T1.2.1 integration gate: BLOCKED pending B-003.** The delivery does not
modify `src/bootstrap/app.py`; production still constructs
`StdlibTransport()` without a credential store. Therefore this review does
not authorize product integration, `VERIFIED_COMPLETE`, or T2.1.1.

The B-003 seam is **AUTHORIZED for the next delivery** with the bounded
decision in §6 below.

## Review identity and recovery point

| Field | Value |
|---|---|
| Task | T1.2.1 Settings UI & ViewModel |
| Author | ZCode |
| Reviewer/integrator | Codex, non-author |
| Review base | `d978d6f` implementation / `7376bce` Handoff |
| R4 implementation | `39dbbf7` |
| R4 Handoff | `a527b85` |
| Branch | `agent/zcode/T1.2.1-settings-ui-viewmodel` |
| Worktree | `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel` |
| Author worktree | clean; HEAD `a527b858aa37a97b125b8ff2f16dd6de99e4d615` |

The Handoff commit is documentation-only and records the R4 delivery and
verification claims. The implementation commit is `39dbbf7`; it is the head
reviewed against the R3 implementation. Neither commit has been merged to
master.

## Scope audit

`git diff 7376bce..39dbbf7 --stat` contains exactly these six paths:

```text
src/infrastructure/providers/registry.py
src/infrastructure/providers/runtime.py
src/ui/qml/settings/SettingsView.qml
src/ui/viewmodels/settings/viewmodel.py
tests/providers/test_provider_binding_projection.py
tests/ui_shell/test_settings_viewmodel.py
```

`src/bootstrap/app.py` is unchanged by R4. No ports, SQLite schema,
dependencies, Roadmap, STATUS, or unrelated agent files are in the
implementation diff. `git diff --check -- src tests doc verification` is clean.

The single `SettingsView.qml` capability-model filter is accepted as a
scope reconciliation under the current R4 user instruction. Other QML paths
remain forbidden. It is not a toolbar or visual redesign.

## Architecture and acceptance review

### R4-B001 — multi-capability aliasing: resolved

`registry.py` uses a two-dimensional alias keyed by `(profile_id,
capability)`, so one profile can project independently into translation and
OCR fixed slots. The independent probe recorded:

```text
DUAL_TRANSLATE=openai-compatible-translation
DUAL_OCR=openai-vision-ocr
```

This is a real runtime result, not a test-name inference.

### R4-B002 — network policy and fail-closed behavior: resolved

`runtime.py` preserves `direct`, `profile`, and `inherit` semantics and gates
an incomplete network selection before provider construction. The probe
recorded:

```text
DIRECT_NETWORK=None
PROFILE_MISSING=ProviderUnavailable ... missing network profile 'vanished'
INHERIT_NETWORK=corp-proxy
```

There is no silent direct fallback for a missing named profile.

### R4-B004 — disabled fixed slot and enabled binding precedence: resolved

The probe recorded:

```text
DISABLED_FIXED=ProviderDisabled PROVIDER_DISABLED: provider is disabled by the user
ENABLED_OVERRIDE=openai-compatible-translation
```

The R4 boundary is accepted: a declared enabled binding may project into a
stale disabled fixed-slot record; the binding is the newer, explicit user
selection. A disabled binding still fails closed.

### R4-B005 — capability declaration enforcement: resolved

The ViewModel rejects undeclared capability bindings and the runtime checks
the projected profile declaration rather than trusting QML. `SettingsView.qml`
filters the visible model by the declared capability. The focused UI/provider
tests and six bootstrap smoke loads passed without QML load errors.

### R3-B003 — production credential-store assembly: unresolved, BLOCKING

`src/bootstrap/app.py:639-643` still passes:

```python
transport=StdlibTransport(),
credential_resolver=_credential_resolver(),
```

The existing `StdlibTransport` seam accepts `credential_store`, and the
fresh authenticated-proxy adapter subset passed 28 tests. That does not prove
the production path. With the current bootstrap construction, a persisted
proxy `credential_ref` cannot be resolved by the transport credential path.

This is an acceptance-level production wiring gap, not an optional cleanup.

## Findings

### BLOCKING

**B-003 — production transport credential store is not injected.**

- Location: `src/bootstrap/app.py:639-643`.
- Trigger: start the real bootstrap with a persisted proxy profile containing
  a `credential_ref`, then allow the assembled transport to resolve the proxy.
- Observed: `StdlibTransport()` receives no credential store.
- Impact: authenticated proxy settings cannot complete through the real
  production assembly path; the T1.2.1 credential/pipeline acceptance
  criterion remains unverified.
- Disposition: **APPROVED FOR NEXT DELIVERY**, not waived. See §6.

### IMPORTANT

**I-001 — verification counts differ by shell environment, as expected.**

Git Bash sees `openssl` and reports zero TLS skips; PowerShell does not and
reports six skips guarded by `shutil.which("openssl")`. Both runs are real and
are recorded below. This is not a product finding.

### NON_BLOCKING

**N-001 — no synthetic QML mouse interaction harness was added.** The existing
bootstrap smoke loads the QML path and the ViewModel/provider tests exercise
the binding logic. The filter has not been represented as a headless click
session. No current project harness makes that a reliable acceptance gate;
keep it as a later UI-harness candidate, not a reason to expand T1.2.1.

## B-003 authorization decision

The proposed seam in Handoff §9.3 is **approved with minimum scope**:

```text
src/bootstrap/app.py only:
  StdlibTransport(credential_store=_credential_store())
```

`_credential_store()` may use the existing Windows credential-store adapter
and return `None` on unavailable optional platform support, preserving
best-effort startup behavior. The next delivery must also add:

1. one assembly-level test proving the production bootstrap passes the store
   into the transport;
2. one local authenticated-proxy probe with a controlled redacted credential;
3. evidence that missing credentials remain typed failure and that secret
   values do not enter logs, mirrors, or verification artifacts.

No ports, schema, dependencies, QML redesign, or new credential abstraction
is authorized. The author remains prohibited from merging master.

## Fresh verification

Interpreter for all Python runs:
`G:\CODEX\New Manga.task-envs\T1.1.1-impl-py312\Scripts\python.exe`.
`PYTHONPATH=src` was set. The full/focused suites intentionally include the
existing registry-readiness environment assertion; its failure is not a R4
failure.

| Check | Shell / command family | Result | Exit |
|---|---|---:|---:|
| Focused provider/UI/network suite | Git Bash; `tests/ui_shell tests/network tests/providers -q -rs` | 422 collected = 421 passed + 1 known environment failure; 0 skipped | 1 |
| Full suite | Git Bash; `pytest tests -q -rs -p no:cacheprovider` | 1136 collected = 1135 passed + 1 known environment failure; 0 skipped; 1 warning | 1 |
| Focused provider/UI/network suite | PowerShell; same suite | 422 collected = 415 passed + 6 OpenSSL skips + 1 known environment failure | 1 |
| Full suite | PowerShell; `pytest tests -q -rs -p no:cacheprovider` | 1136 collected = 1129 passed + 6 OpenSSL skips + 1 known environment failure; 1 warning | 1 |
| Compile | PowerShell; `python -m compileall -q src tests` | PASS | 0 |
| Bootstrap smoke | PowerShell; six fresh `python -m bootstrap.app --smoke-test --data-root <fresh-temp-dir>` runs | 6/6 PASS | 0 |
| Diff check | PowerShell; `git diff --check -- src tests doc verification` | PASS | 0 |
| Authenticated proxy adapter subset | PowerShell; `tests/network/test_transport_local.py tests/network/test_review_revision.py` | 28 passed | 0 |
| R4 runtime edge probe | PowerShell; independent production-runtime probe | PASS; exit recorded in [probe log](r4-probe-39dbbf7.log) | 0 |

The one expected failure in both suites is
`tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment`:
the selected implementation venv contains torch. It is an environment
assertion, not an R4 regression. The six PowerShell skips are the existing
OpenSSL-gated TLS cases. No result is represented as all-green.

## Gate result

| Gate | Result |
|---|---|
| R4 scope audit | PASS, with the explicitly reconciled single QML path |
| R4 B001/B002/B004/B005 | PASS |
| B003 production assembly | BLOCKING / not implemented |
| Non-author review | R4 code seams approved; task integration blocked |
| Product integration | NOT RUN; correctly withheld |
| T1.2.1 final status | `REVIEW_BLOCKED_B003_PENDING` |
| T2.1.1 | NOT STARTED |

## Deferred findings disposition

| Finding | Disposition |
|---|---|
| B-003 credential-store bootstrap seam | MERGE in next T1.2.1 delivery; not deferred |
| Shell-dependent OpenSSL skip count | DEFER as environment evidence; no product change |
| Synthetic QML mouse harness | DEFER / candidate backlog |
| Zoom/pan or visual toolbar redesign | REJECT for this Task; no such acceptance requirement |

## Next task recommendation

Keep the same Task open for a narrow B-003 follow-up. Assign **ZCode** to
implement only the authorized bootstrap seam and evidence; assign **Codex** as
non-author Reviewer/Integrator. Base the delivery on implementation
`39dbbf7` (Handoff context `a527b85`). Do not start T2.1.1 until the new
delivery passes independent review and final integration verification.

### Directly forwardable instruction

> Task: T1.2.1 B-003 production credential-store repair. Author: ZCode.
> Base: `39dbbf7`; branch/worktree unchanged at
> `agent/zcode/T1.2.1-settings-ui-viewmodel` /
> `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`.
> Modify only `src/bootstrap/app.py`, the minimum approved assembly-level
> tests, `verification/T1.2.1/**`, and the T1.2.1 Handoff. Inject the existing
> credential store into production `StdlibTransport`; keep best-effort None
> fallback and typed missing-credential failure. Add an assembly test and a
> local authenticated-proxy probe with redacted evidence. Do not modify ports,
> schema, dependencies, QML, Roadmap, STATUS, or unrelated files. Do not merge
> master, use `git reset --hard`, or use `git clean -fd`. Return a clean
> delivery HEAD and wait for Codex non-author review.
