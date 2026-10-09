# P02 Scratch Isolation Preflight — R6 Incremental Exact-Head Review

You are DeepSeek Harness acting as the independent non-author Reviewer. Perform a read-only exact-head review of the P02 Codex-only scratch isolation preflight findings repair. The authorized orchestration directs this review; no user confirmation is needed.

## Fixed delivery

- Repository: `G:/CODEX/New Manga` (shared Git history).
- Reviewed HEAD: `c85a041c514f3c0dd1c355a2d09f064dbc64e749`.
- Reviewed tree: `b67e3e02186a8009c46da0dba819003b04acfec1`.
- Parent/base: `844aec282416111310d9a9efcac5bc9e0c6eb451`.
- Owner branch: `codex/P02-process-isolation`.
- Review only the delta from the base and the cited evidence needed to judge it. Do not edit files or change commits.

## Review contract

1. Confirm the checkout is exactly the reviewed HEAD/tree, is clean, and the delta stays within the four authorized current-status documents plus `verification/P02/**`. Confirm no product source, tests, dependencies, shared contracts, task AC, owner allowlist, or dependency graph changed.
2. Resolve P2 F-01 by recomputing the hash and size of the committed canonical-LF observations blob and checking the cited report/validation values. Confirm none of the captured measurement values was altered by serialization.
3. Review disposition table entries F-02 through F-11 in `verification/P02/codex-preflight-r5-review-disposition.md` against the exact R5 response and current evidence. Judge the explicit limits for F-04 (frozen input TSV ambiguity), F-10 (targeted erratum/process-output record), and F-11 (immutable dispatched prompt whitespace) rather than treating them as automatically closed.
4. Check the updated report and four current P02 status segments for accuracy, links to authorization/recovery evidence, honest timestamps and byte bases, and unchanged gate state.
5. Verify the current records still say Stage-1=`PRESTART_STAGE_1_PASS`, complete preflight=`BLOCKED / INCOMPLETE`, Smoke=`NOT_ADMITTED`, Build Gate=`BLOCKED`, build=`NOT_AUTHORIZED / NOT_RUN`, AC1–AC7=`BLOCKED / NOT_RUN`, Hard Build Barrier=`EFFECTIVE`.
6. Do not create or start a clone/Sandbox, do not invoke `wsb`, and do not run build, runner, Vitest, GUI, WebView, or product tests. Live host checks are not part of this review and must remain NOT_RUN.

## Prior review context

- Formal prior response: `verification/P02/dsh-review-p02-preflight-r5.response.md` (reviewed `844aec28`, `APPROVED_WITH_CONDITIONS`, P0/P1/P2/P3=`0/0/1/10`).
- This delivery is a new fixed commit on top of that reviewed candidate. Reassess each finding based on the current tree; do not assume the author's disposition is correct.
- Evidence values and Gate state are authoritative only as recorded in committed artifacts. Do not inspect raw process stderr/stdout as model reasoning or formal Review evidence.

## Required return

Save one formal Markdown response under `verification/P02/` and state:

- exact reviewed HEAD, tree, parent, branch, and checkout status;
- decision from `APPROVED`, `CHANGES_REQUESTED`, `NOT_VERIFIED`, `BLOCKED_BY_MISSING_EVIDENCE`;
- P0/P1/P2/P3 counts and each finding ID with disposition/evidence;
- whether F-01 is closed, whether every P3 is explicitly dispositioned, and whether this Review permits Codex to consider a separate Smoke admission checkpoint;
- exact next action and any required narrow repair;
- explicit NOT_RUN list for Sandbox/clone/Smoke/build/product tests.

Do not report hidden reasoning. Keep the review evidence-focused, concise, and limited to this fixed delta.
