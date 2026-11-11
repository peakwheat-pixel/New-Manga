# FEA-15-PIN-EOL-GOV-1 evidence

## Snapshot and scope

- Snapshot branch: `main`
- Snapshot HEAD: `1c8d0abb92645779eb40c1a4fd46d156b02f5339`
- Inventory generation: `2026-11-11 12:38:01 +08:00`; command, HEAD, and `EXIT=0` are in [`pin-inventory-run.log`](pin-inventory-run.log).
- The measured tracked worktree and index were clean. `git status --porcelain` showed only this Task's untracked evidence directory. The inventory reads tracked Task cards and frozen records at the snapshot HEAD; it does not scan untracked Task drafts.
- The Task workspace was confirmed absent before creation. Both isolated checkouts are under `G:/CODEX/New Manga.workspace/FEA-15-PIN-EOL-GOV-1/`; after the inventory tooling commit they were advanced to this snapshot and verified clean. The fetch/checkout/restore commands and exit codes are in [`checkout-refresh.log`](checkout-refresh.log).
- Effective `core.autocrlf=true` came only from `file:C:/Program Files/Git/etc/gitconfig`. See the environment block in [`pin-inventory.json`](pin-inventory.json).
- On this snapshot, the default and TaskPath governance checks passed with 3 warnings each, `verify_pins.ps1` passed 18/18, and the API inventory check passed at 1/79/6=86. Exact commands, HEAD, output, and exit codes are in [`gate-baseline.log`](gate-baseline.log).

## AC1 inventory

[`pin_inventory.py`](pin_inventory.py) parses all tracked `doc/tasks/**/*.md` Canonical Evidence tables and the 18 `doc/plan/FEA-CONTRACT-FROZEN-*.md` records mapped by `tools/governance/verify_pins.ps1`. For each row it stores the source, ID, path, pin, commit, current worktree SHA-256, referenced blob SHA-256 when available, basis classification, current EOL profile, `git ls-files --eol` values, and attribute state in [`pin-inventory.json`](pin-inventory.json).

The snapshot contains 585 tracked Task cards, 5,332 Canonical Evidence rows, 18 frozen contract records, and 5,350 rows total. The 18 frozen record IDs and source paths all match the `verify_pins.ps1` map. Of those 18, 16 match both current worktree and HEAD blob bytes; C04b and C17 match worktree bytes only. `verify_pins.ps1` still checks those 18 worktree hashes.

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

The first Windows checkout attempt reported `Filename too long` for 20 long-path files per clone even though Git returned exit 0. Both checkouts showed 20 missing tracked paths and were not treated as successful. In the clones only, `core.longpaths=true` followed by `git restore --source=HEAD --worktree -- .` restored both to clean status; each recovery command exited 0. [`checkout-setup.log`](checkout-setup.log) and [`checkout-recovery.log`](checkout-recovery.log) preserve this. The checkout workspace was then advanced from the earlier `c3b1068…` observation to the tooling snapshot with `git fetch`, detached checkout, and a second restore; both remained clean and retained their `core.autocrlf` values. The earlier snapshot logs and JSON are retained in the external Task agent-output directory. No source worktree files were changed.

## AC3 analysis and limits

Candidate strategy analysis is in [`candidate-policy-analysis.md`](candidate-policy-analysis.md). It separates observed facts, inferences, unknowns, candidate policies, and stop gates. No final pin policy is selected here.

Not run: Linux fresh clone, global or path-wide `git add --renormalize` simulation, product test suites, and any mutation of `.gitattributes`, checker semantics, frozen contracts, historical evidence, or pins. They are outside this read-only Task scope. Parser-development attempts are retained under `G:/CODEX/New Manga.workspace/agent-output/codex/FEA-15-PIN-EOL-GOV-1/`; only the final successful runs above are canonical evidence.
