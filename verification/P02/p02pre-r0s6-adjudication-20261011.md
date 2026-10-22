# P02PRE-R0S6 Codex Adjudication

## Decision

**Accepted with limits; Task=`blocked / NOT_SAFE_FOR_R0`.** DeepSeek Harness R2 is accepted as an independent static-document Review (`APPROVED`, P0/P1/P2/P3=`0/0/0/0`). The R1 findings (`0/0/4/6`) are closed by the recorded revisions. Review approval establishes only the adequacy of the reviewed Task/manifest text; it does not prove runner safety, provide host evidence, pass a technical Gate, or release the Build Barrier.

No current getter can safely execute under the frozen manifest because the invocation runner and its side-effect/process boundary are unproven. The correct R0S6 result is to run no host query and retain the methods as `NOT_SAFE_FOR_R0`; do not convert the absence of an execution into `FAILED` or `PASS`.

## Five-state adjudication

| State | Adjudicated items |
|---|---|
| `PASS_WITH_EVIDENCE` | Historical R0 evidence only, for its pinned objects and capture window. It does not establish current identity, paths, ACLs, or hashes. |
| `FAILED` | None; no R0S6 host checks ran after the manifest freeze. |
| `UNPROVABLE` | Current identity/token; profile/target-path metadata; ACL/effective permissions; TEMP/cache/scratch resolution; protected-file hashes; WER/T0; `private_registry_absence`. |
| `REQUIRES_ACTIVE_TEST` | LPAC/canary behavior, complete child/broker/write closure, and stop/cleanup behavior. These need a separately authorized stage. |
| `NOT_SAFE_FOR_R0` | The current launcher/wrapper and all dependent identity, path, ACL, environment, hash, Git, and WER/T0 getter methods. Invocation effects and child-process closure are not proven. |

The pre-freeze scratch metadata observation is excluded as current R0S6 evidence. It is recorded for auditability only. The R1 report/stderr/exit pre-write state remains `NOT_VERIFIED`; possible overwrite of prior contents remains `UNKNOWN`; no restoration or no-loss claim is made.

## Unchanged risk and gates

- `private_registry_absence=UNPROVABLE`; Technical Gate=`NOT_SATISFIED`.
- Owner Risk Acceptance=`APPROVED`; Gate Disposition=`WAIVED_BY_OWNER`.
- Build Authorization=`AUTHORIZED_WITH_EXCEPTION`; exact residual-risk text: `technical condition unmet; user explicitly accepted residual risk`.
- P02PRE=`BLOCKED`; Build Gate=`BLOCKED`; Hard Build Barrier=`EFFECTIVE`.
- profile=`NOT_CREATED`; ACL/registry=`NOT_MODIFIED`; build/Cargo=`NOT_RUN`; AC1–AC7=`BLOCKED / NOT_RUN`.

The owner exception waives only the requirement to prove absence of private registry storage before creation. R0S6 adds no waiver and does not authorize profile creation, registry/ACL writes, active tests, build, Cargo, AC1–AC7, or Windows Sandbox operations.

## Next authorized boundary

No host-query task is READY under the present authorization. A new user decision is required before a follow-on static runner/source-contract audit or any active test. If that decision is given, freeze exact scope and evidence paths, obtain non-author review, and adjudicate before considering any getter. Until then, preserve the effective Hard Build Barrier.
