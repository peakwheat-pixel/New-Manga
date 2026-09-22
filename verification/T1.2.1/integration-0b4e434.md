# T1.2.1 Settings UI & ViewModel — Codex Integration Evidence

Date: 2026-09-22  
Integrator: Codex  
Author: ZCode  
Master before review: `d11d927a46c9d2350b0e8e8161abb8ff21acba79`  
Candidate branch: `agent/codex/T1.2.1-integration`  
Candidate worktree: `C:\Users\49745\.codex\worktrees\t121-codex-integration\New Manga`  
Candidate merge commit: `3097656a350abed32172c9f95c17772bbd8d6abf`  
Candidate partial-fix commit: `0b4e4342e94576a23a20d2861a045d42ab911005`  
Master after review: unchanged at `d11d927a46c9d2350b0e8e8161abb8ff21acba79`

## Integration decision

**BLOCKED — no merge to master.**

The candidate preserves the author's commits and contains only a minimal
provider-profile-to-pipeline mirror repair plus its focused regression test.
The candidate is intentionally not promoted because the production provider
registry cannot resolve the UI-created profile ID and configured network/proxy
profiles are not applied to the provider transport. These are acceptance-level
failures, not cosmetic follow-ups.

## Fresh verification

| Command / check | Result | Exit |
|---|---|---:|
| `pytest tests/ui_shell tests/network -q -rs -p no:cacheprovider` | 161 passed, 6 skipped; skips are OpenSSL-unavailable TLS cases | 0 |
| `pytest tests -q -rs -p no:cacheprovider` | 1094 passed, 6 skipped, 1 failed, 1 warning; only failure is the expected torch-installed registry-readiness environment assertion | 1 |
| `python -m compileall -q src tests` | passed | 0 |
| `python -m bootstrap.app --smoke-test --data-root <fresh-temp-dir>` | passed | 0 |
| source protection subset: `tests/library/test_import_images.py tests/workbench/test_region_create_persistence.py` | 15 passed | 0 |
| `git diff --check -- src tests doc verification` | passed | 0 |
| six repeated real bootstrap/QML smoke launches | 6/6 exit 0; no matching QML error text | 0 |

The full suite is not reported as green: the single failure is the existing
environment-specific `test_no_model_runtime_is_installed_in_this_environment`
assertion, and the six skips are OpenSSL-unavailable tests. The full-suite
failure is not the reason this integration is blocked; B-001 and B-002 are.

## Production-path probes

The candidate's mirror repair produced the expected persisted runtime shape
after save/reassembly:

```text
settings.providers.profiles.openai-translation =
  base_url=https://api.example.com/v1
  model=gpt-test
  credential_ref=None
  enabled=True
  options={}
```

The next real registry step failed:

```text
ProviderUnavailable: no provider registered as 'openai-translation'
exit 1
```

The runtime's `_openai_config()` also leaves `network_profile` unset, so the
client selects its direct default instead of the saved proxy profile. This
requires a bounded follow-up implementation/review before integration.

## Safety

- Main dirty files were preserved and not staged.
- No `git reset --hard` or `git clean -fd` was used.
- No SQLite schema, ports, QML shell, Roadmap, or unrelated agent files were
  changed by the candidate repair.
- Source-protection tests remained green.

## Gate result

`T1.2.1 = REVIEW_BLOCKED`; it is not `INTEGRATED` or
`VERIFIED_COMPLETE`. T2.1.1 is not started.
