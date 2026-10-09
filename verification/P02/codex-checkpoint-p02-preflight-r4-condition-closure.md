# P02 R9 Review Condition Closure checkpoint

- Started: 2026-10-10 (Asia/Shanghai). State: `R10_CONDITION_REPAIR / AWAITING_EXACT_HEAD_REVIEW`.
- Parent Task=P02 remains `in_progress / ACTIVE`; this Codex-only isolation subtask is Owner=Codex, non-author Reviewer=DeepSeek Harness, Integrator=Codex.
- Reviewed r9 candidate: HEAD=`083d2b47f7051c2dedd0d9ae4346ae1affab6c1b`, tree=`27a8051b95df3c2cf40be90737d09b324592a78e`, base=`ceffb7479cb1f79bd3b620afdaf6e9eaa0ae6d50`.
- DSH final decision: `APPROVED_WITH_CONDITIONS`; blocking P0/P1/P2=`0/0/0`; six nonblocking P3 findings and one note. Exact report is preserved in the DSH review response attachment after this candidate is reviewed.

## Finding disposition

| Finding | Disposition in r10 |
|---|---|
| C-01: empty expected size with `size_match=true` | Six unregistered size values now use JSON `null`; counts distinguish 20 SHA-256 checks, 14 registered size checks, and six not registered. |
| C-02: exact write paths not named in checkpoint | The original r9 five-path set and the exact seven-path r10 candidate set are listed in the start checkpoint and scope extension. |
| C-03: `mapping_domain=null` | All 12 JSON roots now match classifications from the frozen HostFolder TSV. |
| C-04: authorization anchor missing | The r10 extension points to the r7 authorization-basis section and P02 Task checkpoint. |
| C-05: admission checklist omitted shell/session conditions | The separate Smoke admission checkpoint specifies non-elevated interactive shell, fresh empty `wsb list --raw`, and post-start UI/screenshot binding to the returned session. |
| C-06: shared documents still show `UNKNOWN / BLOCKED` | This is explicitly recorded as a temporary pre-review lag; shared current-status segments may be updated only after exact-head Review passes. |

## Exact candidate path set

1. `verification/P02/codex-scratch-build-process-isolation-scope-delta-r1.md`
2. `verification/P02/codex-scratch-build-preflight-r2.md`
3. `verification/P02/codex-scratch-build-preflight-observations-r2.json`
4. `verification/P02/codex-checkpoint-p02-preflight-r4-start.md`
5. `verification/P02/codex-preflight-r4-validation.md`
6. `verification/P02/codex-checkpoint-p02-preflight-r4-condition-closure.md`
7. `verification/P02/codex-checkpoint-p02-smoke-admission-r1.md`

- These paths are the complete r10 documentation/evidence candidate; exact path validation and root protected-manifest containment are required before freeze.
- Root shared status documents still say Feature=`UNKNOWN` and preflight=`BLOCKED / INCOMPLETE`; this is intentional until the r10 Review passes. It does not change the measured r9 observation `InstallState=1` or the r9 `PRESTART_STAGE_1_PASS` evidence.
- Smoke admission=`NOT_ADMITTED`; clone=`NOT_CREATED`; Sandbox/Smoke=`NOT_RUN`; Build Gate=`BLOCKED`; build=`NOT_AUTHORIZED / NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`; Hard Build Barrier remains effective.
- Pre-freeze validation passed at 2026-10-10 03:08 +08:00: route validator EXIT=0; focused Markdown links 6 local links with 0 new missing; root manifest 203/203 with zero mismatches, staged entries, or candidate-path overlap; JSON pin/domain consistency passed; `git diff --check` EXIT=0. The exact outputs and scope are in [R10 validation](codex-preflight-r4-validation.md).

- Next exact step: stage only the seven listed candidate paths, rerun staged diff/path validation, freeze one commit, and dispatch DeepSeek Harness to review its exact HEAD/tree. If any check fails or is unknown, do not admit Smoke; preserve the evidence and record the blocker.
