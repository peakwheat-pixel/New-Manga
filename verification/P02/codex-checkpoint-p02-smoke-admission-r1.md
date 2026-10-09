# P02 Sandbox Isolation Smoke admission checkpoint

- State: `NOT_ADMITTED`; this checkpoint does not itself start a clone, Sandbox, or Smoke.
- Parent Task=P02 remains `in_progress / ACTIVE`; Owner=Codex for the Codex-only isolation subtask; non-author Reviewer=DeepSeek Harness; Integrator=Codex.
- The r9 candidate's DSH decision was `APPROVED_WITH_CONDITIONS`; all six P3 dispositions are included in the r10 candidate and require exact-head follow-up Review before this checkpoint can advance.
- Smoke admission can become `ADMITTED` only through a separate Codex gate decision after the exact-head Review passes and a current non-elevated stage-1 preflight passes. It authorizes one attempt using the already-reviewed r3 config/hash at the fixed clone path only.

## Admission and pre-start checklist

### Required before recording `Smoke admission=ADMITTED`

- [ ] DSH exact-head follow-up Review approves the frozen r10 condition-closure candidate; all six P3 dispositions are accepted; no unresolved P0/P1/P2 remains.
- [ ] Repeat the non-elevated read-only CIM feature query and record a known state; do not elevate or change the feature.
- [ ] Re-measure volatile RAM, free disk, CPU/firmware virtualization, WSB identity/version/list, HostFolder roots and registered pins; use the fixed thresholds and record exact command output/time.
- [ ] Recheck the protected root manifest and root worktree state; record the exact live root HEAD and verify zero candidate-path overlap.
- [ ] Confirm the reviewed r3 config canonical bytes/hash remain `2609 / 9af445134c6c6d3cec900b6d5c903a3c7fe19a104e0eab10f7c0886280de664d`.

### Required after admission, before any `wsb start`

- [ ] Create only `G:\CODEX\P02-scratch-build-source` from the fixed source commit with the prescribed `--no-hardlinks` clone procedure; verify detached checkout, private common Git directory, empty remotes, no alternates, clean status, exact source pins and one link per object.
- [ ] Create and compare the full recursive pre-start manifests for every mapped HostFolder; enumerate reparse points and verify the approved root set and scratch-only output boundary.
- [ ] Run from a live, interactive, non-elevated host PowerShell process; record shell path/version, PID, and non-elevated token status in the pre-start evidence.
- [ ] Immediately before start, run `wsb list --raw`, verify it is empty, and bind that output/time to the exact Smoke attempt.
- [ ] Verify the r3 XML hash and mapping set again. Any failed or unknown check means do not run `wsb start`; preserve the clone and evidence without cleanup.

### Required during and after the one Smoke attempt

- [ ] Bind the started Sandbox's returned session/environment identity to the visible Sandbox UI window; save a target screenshot inside the fixed scratch clone and record the session ID, window identity, and screenshot hash together.
- [ ] Run only the approved read-only/write/unmapped/network probes; preserve expected fail-closed results and do not access user data.
- [ ] Stop the same bound session, then compare protected root/input/clone manifests. On any unexpected change or missing evidence, mark the Smoke `BLOCKED / NOT_VERIFIED`, preserve all state, and do not infer a pass.

## Independent gates

- Smoke admission and Smoke result do not pass the Build Gate. Build Gate=`BLOCKED`; product build=`NOT_AUTHORIZED / NOT_RUN`; P02 AC1–AC7=`BLOCKED / NOT_RUN`; product acceptance=`NOT_RUN`; Hard Build Barrier remains effective until its own required evidence and Codex Gate are satisfied.
- No clone, Sandbox, Smoke, build, Vitest, runner, GUI, or product test has run as of this checkpoint.

## Recovery

Start from this checkpoint, reverify the reviewed HEAD, current root HEAD/manifest and worktree status, and current volatile preflight. Do not repeat the already-approved design review or claim Smoke admission until every required precondition is supported by current evidence.
