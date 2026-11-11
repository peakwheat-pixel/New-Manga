# FEA-15-PIN-EOL-GOV-1 evidence

## Snapshot and scope

- Snapshot branch: `main`
- Snapshot HEAD: `948d73e0629869e560df9a2b2d8a357cec67027f`
- Inventory generation: `2026-11-11 12:58:14 +08:00`; command, HEAD, and `EXIT=0` are in [`pin-inventory-run.log`](pin-inventory-run.log).
- The inventory reads the committed Task cards, frozen records, and pin map from `HEAD` using `git cat-file`; it hashes referenced files from the actual `main` worktree. At capture, the worktree had only the current Task's documented card/status/plan/ledger/evidence edits; all are listed in `pin-inventory.json`. No unrelated user changes were present. The current Task's later Canonical Evidence pinbackfill was not yet committed at this snapshot and is therefore not counted as a versioned pin row.
- The Task workspace was confirmed absent before creation. Both `core.autocrlf=true/false` isolated checkouts are at this snapshot and clean. A third preserved snapshot clone at `c6f34d93a09cba0afa3046697badd5bdb433a207` contains an earlier clean-checkout comparison and its generated files. That observation is supplemental only; the AC1 inventory and final AC2 matrix below use the exact `948d73e…` snapshot. Checkout creation/refresh commands are in [`snapshot-clone-setup.log`](snapshot-clone-setup.log) and [`checkout-refresh.log`](checkout-refresh.log); final resource states are in [`resource-manifest.json`](resource-manifest.json).
- Effective `core.autocrlf=true` came only from `file:C:/Program Files/Git/etc/gitconfig`. See the environment block in [`pin-inventory.json`](pin-inventory.json).
- On earlier tool/evidence snapshots, default and TaskPath governance checks passed with 3 warnings each, `verify_pins.ps1` passed 18/18, and the API inventory check passed at 1/79/6=86. Those commands, HEADs, outputs, and exit codes are in [`gate-baseline.log`](gate-baseline.log) and [`gate-post-evidence.log`](gate-post-evidence.log); the final post-correction gate run is recorded separately.

## AC1 inventory

[`pin_inventory.py`](pin_inventory.py) parses all tracked `doc/tasks/**/*.md` Canonical Evidence tables and the 18 `doc/plan/FEA-CONTRACT-FROZEN-*.md` records mapped by `tools/governance/verify_pins.ps1`. For each row it stores the source, ID, path, pin, commit, current worktree SHA-256, referenced blob SHA-256 when available, basis classification, current EOL profile, `git ls-files --eol` values, and attribute state in [`pin-inventory.json`](pin-inventory.json).

The snapshot contains 584 tracked Task cards, 5,332 Canonical Evidence rows, 18 frozen contract records, and 5,350 rows total. The 18 frozen record IDs and source paths all match the `verify_pins.ps1` map. Of those 18, 16 match both current worktree and HEAD blob bytes; C04b and C17 match worktree bytes only. `verify_pins.ps1` still checks those 18 worktree hashes. `doc/tasks/README.md` is the Task index, not a Task card, and is excluded from the card count.

| Basis | Rows | Meaning |
|---|---:|---|
| `BLOB` | 327 | Pin matches only the blob at its recorded commit. |
| `WORKTREE` | 3,451 | Pin matches only the current worktree bytes. |
| `MIXED` | 999 | Pin matches both; the bytes do not distinguish the intended basis. |
| `INCONSISTENT` | 160 | Pin matches neither the recorded blob nor current worktree bytes. This is an observation requiring classification, not a corruption verdict. |
| `UNPINNED` | 293 | No valid SHA-256 is recorded. |
| `UNRESOLVED_COMMIT` | 68 | No usable commit is recorded for blob comparison. |
| `EXTERNAL_UNAVAILABLE` | 47 | External path is not available in this local workspace. |
| `MISSING` | 3 | Path is absent from both its recorded commit and current worktree. |
| `COMPOSITE_PATH` | 2 | One row lists multiple paths, so a single path-to-blob comparison cannot be inferred. |

The table includes rows without a valid pin so their missing state is visible; they are not counted as successful hashes. No historical ratio was used to infer this snapshot. The 573 rows outside the three match categories comprise the 160 compared mismatches plus the five explicitly unpinned/unresolved/path categories above. Basis definitions are encoded in the generator; the full row data is authoritative for these counts.

EOL profiles count pin rows: 3,100 CRLF, 1,288 LF, 198 mixed-EOL, 452 binary, 167 without line endings, and 145 whose current file is unavailable. There are 4,733 unique repository paths among the rows, 4,639 currently present. Their unique-file EOL counts and attribute states are in the JSON summary. Empty `git check-attr` results are represented as `UNSPECIFIED`; external paths are `NOT_APPLICABLE_EXTERNAL`.

## AC2 checkout matrix

[`checkout_matrix.py`](checkout_matrix.py) compares the main worktree and two isolated checkouts at the same snapshot HEAD. The checkouts use local `core.autocrlf=true` and `false`. Four samples cover a blob-only pin, worktree-only pin, mixed-EOL text file, and binary PNG. [`checkout-matrix-run.log`](checkout-matrix-run.log) records the command, time, HEAD, summary, and `EXIT=0`; [`checkout-matrix.json`](checkout-matrix.json) records all 12 observations, each checkout HEAD, EOL output, hash results, and individual Git command exit codes. [`checkout-samples.json`](checkout-samples.json) records the selected sample rows.

| Sample | Main / isolated `true` | Isolated `false` | Interpretation |
|---|---|---|---|
| BLOB — `AGPL-RELEASE-1`, `verification/AGPL-RELEASE-1/REPORT.md` | `FAIL`, CRLF worktree hash differs from pin | `PASS`, LF worktree hash equals pin | Blob basis is reproducible in the LF checkout. |
| WORKTREE — `AD002-FOLLOWUPS-1`, `verification/RELEASE-REPACK-6/verify.json` | `PASS`, CRLF worktree hash equals pin | `FAIL`, LF worktree hash equals blob instead | Worktree basis depends on checkout EOL behavior. |
| MIXED_EOL — `FEA-06-PREREQ-1`, `apps/desktop-avalonia/src/NewManga.Appearance/AppearanceJson.cs` | `PASS`, original mixed bytes equal pin | `FAIL` in both fresh checkouts: `true` yields CRLF and `false` yields LF | The original mixed bytes are not reproduced by either fresh checkout. |
| BINARY — `CHAPTER-SELECTOR-1`, `verification/CHAPTER-SELECTOR-1/screens/01-bookshelf-two-books.png` | `PASS` | `PASS` | The SHA-256 is identical across all three worktrees. |

`pin_result` means the checkout's worktree SHA-256 equals the recorded pin. The separate `head_blob_result` is `PASS` for all 12 observations. These are measurement outcomes, not authorization to change pin rules.

The first Windows checkout attempt reported `Filename too long` for 20 long-path files per clone even though Git returned exit 0. The two autocrlf clones showed 20 missing tracked paths and were not treated as successful. In the clones only, `core.longpaths=true` followed by `git restore --source=HEAD --worktree -- .` restored them to clean status; each recovery command exited 0. [`checkout-setup.log`](checkout-setup.log) and [`checkout-recovery.log`](checkout-recovery.log) preserve this. The two matrix clones were advanced to `948d73e…` and remain clean with their respective `core.autocrlf` values. The extra `c6f34d9…` snapshot clone is preserved with its exploratory inventory and matrix; its older HEAD is not used for the AC1 count or final matrix. No source worktree files were changed.

## AC3 analysis and limits

Candidate strategy analysis is in [`candidate-policy-analysis.md`](candidate-policy-analysis.md). It separates observed facts, inferences, unknowns, candidate policies, and stop gates. No final pin policy is selected here.

Not run: Linux fresh clone, global or path-wide `git add --renormalize` simulation, product test suites, and any mutation of `.gitattributes`, checker semantics, frozen contracts, historical evidence, or pins. They are outside this read-only Task scope. Parser-development attempts are retained under `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-15-PIN-EOL-GOV-1/`; only the final successful runs above are canonical evidence.
