# AC3 — Evidence pin basis and migration candidates

Snapshot: `main` at `948d73e0629869e560df9a2b2d8a357cec67027f`. This is analysis only. No policy is approved by this document, and no implementation is performed.

## Observed facts

1. The inventory contains 5,350 rows: 5,332 Canonical Evidence rows in 584 tracked Task cards and 18 frozen contract records. At this snapshot, 3,451 rows match only the current worktree hash, 327 only the recorded commit blob, 999 both, and 160 neither. The remaining 573 are explicitly unpinned or cannot be compared because the path/commit is unavailable or unresolved. These are row counts, not unique files or active-task counts.
2. The 4,733 unique repository paths in those rows include 4,639 files present in the current worktree. Of unique present paths, 442 have binary bytes, 172 mixed EOL, and 2,807 CRLF. These counts cover files referenced by the pin rows only; they are not counts of every file in `verification/**`.
3. Git reports `core.autocrlf=true` from the system config `C:/Program Files/Git/etc/gitconfig`; the inventory snapshot records no tracked worktree or index changes. Most pinned paths have no explicit EOL attribute. `.gitattributes` has targeted rules for selected handoffs, tools, Task paths, and evidence directories, not one universal rule for all verification evidence.
4. `tools/governance/check.ps1` r194 first hashes current worktree bytes, then accepts a recorded commit blob hash when the commit contains the path. This is the current compatibility behavior. `tools/governance/verify_pins.ps1` checks the 18 frozen contract hashes against current worktree bytes; it remains `18/18` at this snapshot.
5. Existing precedents have distinct scopes. FEA-08 records blob/LF SHA-256 for text evidence and explicitly keeps PNG/GIF/ZIP/PDF fixtures byte-exact. P19 and GOV-EOL rules pin selected text evidence to LF. `GOV-EOL-PIN-1` added bounded rules for named evidence paths and Task files; it did not establish that every historical pin shares one basis.
6. FEA-15-ACCEPT-1 r1/r2 and the older r27 figures describe their own historical populations. The current 5,350-row inventory was measured directly and is not inferred from 27/30 or 187/300.
7. The four-sample matrix shows both reproducible and non-reproducible outcomes across the three checked worktrees. Blob-only text matches the LF checkout; worktree-only JSON matches the CRLF checkout; a mixed-EOL source file's original bytes match neither fresh checkout; the PNG hash is unchanged. All checkouts are the same HEAD.
8. The inventory's Task/frozen source text comes from the committed snapshot via `git cat-file`; worktree hashes and EOL observations come from the actual `main` worktree. That worktree had only the current Task's known documentation/evidence edits, which are listed in the machine snapshot. This keeps the row universe bound to HEAD while preserving the measured worktree bytes.

## Inferences, with boundaries

- Switching future pins to blob/LF could improve checkout portability for text files, but 3,451 current rows are worktree-only at this snapshot. This is a candidate triage population, not a migration worklist: rows include historical Tasks, and some references are unresolved or stale.
- The 160 `INCONSISTENT` rows cannot be explained by EOL alone from this inventory. They need per-row source/task classification before anyone changes their recorded value.
- A broad `text eol=lf` rule over all evidence paths would be unsafe without binary exclusions and path-level analysis. The pin-linked sample already contains 442 unique binary files and 172 unique mixed-EOL files. A narrowly scoped extension/path policy could affect a different set; its exact impact was not simulated here.
- `git add --renormalize` could change index blobs for paths covered by a future attribute rule. The resulting source/evidence hashes would need to be measured against a fixed pre-change matrix. No dry run was attempted because no candidate rule was authorized in this Task.

## Candidate options for a later adjudication

1. **Keep dual-basis compatibility for legacy entries; declare the basis for new entries.** Preserve r194 for existing Task pins while a Task template or authoring guide states whether a new pin is blob-based or worktree-based. A separate governance change would be needed if the checker begins requiring that declaration.
2. **Use blob/LF for new textual evidence, with explicit binary handling.** This follows the FEA-08 precedent. It would require narrowly scoped attributes or a deterministic capture rule for text and `-text`/byte-preserving treatment for binary fixtures. Do not infer a global pattern from FEA-08.
3. **Migrate selected historical pins.** Only after each row's Task status, source commit/path, current references, and intended basis are known; use a separate released Task with before/after matrices and independent Review. The 3,451 worktree-only rows are an upper-bound candidate population from this snapshot, not automatic edits.
4. **Retain worktree basis for named artifacts.** If selected for a specific use case, require a reproducible checkout contract and explicit attributes/configuration. The mixed-EOL sample shows that merely recording current worktree bytes does not guarantee a fresh checkout can reproduce them.

No option is selected. The immediate safe state is to preserve every existing pin and keep the checker semantics unchanged until an authorized follow-up decision chooses a bounded population and policy.

## Unknowns and counterevidence

- The causes of the 160 mismatches, 68 unresolved commits, 47 unavailable external paths, 3 missing paths, and 2 composite path rows have not been individually adjudicated. The 293 unpinned rows have no digest to compare.
- Linux checkout behavior was not measured in this Task. The Windows `core.autocrlf=false` clone is a local configuration comparison, not a Linux result.
- The exact affected set for any new `.gitattributes` rule or index renormalization is unknown until the rule and path patterns are separately frozen and dry-run in an isolated clone.
- Counterevidence to a claim that the current gate is broken: the 18 frozen pins pass `verify_pins.ps1`; the current checker accepts both recorded blob and worktree hashes; several scoped LF precedents already work. These facts do not resolve historical inconsistent rows.

## Stop gates before any implementation

1. Freeze the exact affected file and pin universe; classify unresolved and external rows or explicitly exclude them with reasons.
2. Specify candidate EOL attributes, text/binary exceptions, and the checker result semantics before editing any attribute or verifier.
3. In a separate isolated clone, compute a before/after matrix for representative and boundary cases, including binary and mixed-EOL samples. Keep `git add --renormalize` and generated blob changes out of the main checkout until the matrix is reviewed.
4. If the observations disagree with the assumed basis, discard the assumption and stop. Do not convert an observed mismatch into a rewrite list.
5. Require an independently reviewed follow-up Task and a ZCode adjudication before changing `.gitattributes`, checker semantics, any frozen contract, historical evidence, or pin values.
