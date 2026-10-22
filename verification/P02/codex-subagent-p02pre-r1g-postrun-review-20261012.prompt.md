# P02PRE-R1G capture post-run independent Review

Review role: non-author Reviewer. Implementation Owner: Antigravity. Integrator/Adjudicator: Codex /root. Reviewed candidate branch HEAD=`946938bd0696dfddd01f87d61fe6723c63ecdc86`; main HEAD at capture=`cddff58469b56e181019a8ddfeade80684bc7eb9`.

Return findings to Codex; do not write repository files. Review exact evidence content only. Do not execute code or commands, calculate hashes, query Git or OS state, enumerate directories, or access `.tmp.driveupload`. Do not infer that an unobserved side effect did not occur.

## Exact review inputs

1. `doc/tasks/P02PRE-R1G.md`
2. `verification/P02/p02pre-r1g-manifest-20261011.md`
3. `verification/P02/p02pre-r1g-capture.ps1`
4. `verification/P02/p02pre-r1g-runner-evidence-20261011.json`
5. `verification/P02/p02pre-r1g-evidence-20261011.json` (large JSON; inspect only required top-level and main/scratch/command fields; never return embedded base64 or full status payload)
6. `verification/P02/p02pre-r1g-capture-20261011.stdout.log`
7. `verification/P02/p02pre-r1g-capture-20261011.stderr.log`
8. `verification/P02/p02pre-r1g-capture-20261011.exit`
9. `verification/P02/codex-subagent-p02pre-r1g-review-followup3-20261012.md`
10. `verification/P02/p02pre-r1g-review-followup3-adjudication-20261012.md`
11. `verification/P02/codex-checkpoint-p02pre-r1g-20261012.md`
12. `doc/templates/REVIEW.md`
13. This prompt.

Codex froze the capture outputs as follows: runner evidence=`33238 / 690BFB6072272D69B953B6CC01038402167230F676E64C11EC7447582945FE08`; child evidence=`9025567 / E3601767D19D70C19AF8168548A2B7D9894D4414532232F9493331966A7838EE`; stdout=`0 / E3B0C44298FC1C149AFBF4C8996FB92427AE41E4649B934CA495991B7852B855`; stderr=`398 / 91C80EFC3E6BB2E443DEDAADE3C54E39BE090B603591B2CACBBD713085D762D7`; exit marker=`3 / F1B2F662800122BED0FF255693DF89C4487FBDCF453D3524A42D4EC20C3D9C04`. The exact source pin was `81991 / 3C7D85AB3E20C023873197FE391B8F22DFB319038F43B7C554DC4F38927AADDF`. These are Codex-provided pins, not a request to recalculate hashes.

## Review questions

- Does the runner evidence agree with the child evidence, stderr, and exit marker on the executable, ordered argv, CWD, PIDs, exit, source pre/post pin, and captured stdout/stderr hashes?
- Which child commands actually ran before the stop? Do the evidence records fit the frozen Git plus `whoami.exe /all` allowlist? Identify any missing evidence. Do not claim OS-wide process closure if the files cannot prove it.
- Does the child record `identity=PASS_WITH_EVIDENCE`, `mainRepository=CAPTURED`, and `scratchRepository=PROTECTED_HASH_FAILED`, with stop category `INVENTORY_OR_QUERY_STOP`, reason `SCRATCH_BASELINE_OR_HASH_FAILED`, and no later environment/path/WER/protectedHashes/ACL phase?
- Is the reported scratch stop at `.codex/skills/ask-matt` consistent with Git mode `120000`, file attributes `Archive`, and the code's fail-closed rule for a Git symlink that is not represented as a filesystem reparse point? Was its target content hashed or followed according to the evidence?
- Does the parent record all 96 pre-run protected hashes unchanged post-run, the capture source unchanged, and the five declared outputs as the only newly created artifacts? State the boundary of that evidence and any side effects not independently observable.
- Give a disposition for the actual R1G capture result. Distinguish a fail-closed precondition stop from a product AC failure. Do not treat the owner risk waiver as a technical PASS, and do not release Build Gate/Hard Build Barrier.
- Recommend the smallest safe next task that can resolve this platform-specific symlink representation condition without rerunning or overwriting the consumed R1G one-shot outputs. State any remaining unknowns.

Return a concise report using the repository Review template headings where practical: verdict, evidence checked, findings with severity, stage/result classification, process/write-closure limits, Gate disposition, and exact recommended next Task/Owner/acceptance criteria. No code changes or test execution.

