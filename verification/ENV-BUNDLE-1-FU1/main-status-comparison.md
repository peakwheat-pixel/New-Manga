# AC6 main-worktree comparison

Main root: `G:/CODEX/New Manga`. Initial snapshot was captured before AC4; final snapshot was captured at `2026-10-16T17:38:02+08:00`. The two AC4 destinations are gitignored (`apps/desktop/.gitignore` rules for `src-tauri/target/` and `frontend/dist/`).

| Observation | Before AC4 | Final snapshot |
|---|---|---|
| Main HEAD | `4dcd5a9499f17d1b189f3b67f3a3ac59509b2337` | `a79bc1035955ec13a2d42b15da256314a1704029` |
| `git status --porcelain --untracked-files=no` entries | 19 original user-owned paths | Same 19 original paths |
| Status bytes SHA-256 | `a72d1076a20534021c50709972e760a66b7b65d220248284e518eb8f891d460a` | same |
| `git diff --binary` | 250,300 bytes; SHA-256 `fde78be03b5e5be8a01d10050703c2b2e587756b8d77a39be6bce05d1e7bfe35` | same |

HEAD advanced concurrently through UI-DESIGN-1 documentation/review/closeout commits while this task ran. `git diff --name-status 4dcd5a9499f17d1b189f3b67f3a3ac59509b2337 a79bc1035955ec13a2d42b15da256314a1704029 -- src apps/desktop packaging` is empty. A transient extra dirty UI-DESIGN-1 review file appeared during the run, was left untouched, and was no longer dirty in the final snapshot. Final full status is the original 19 entries. The captured status and diff fingerprints are in [`main-status-before.txt`](main-status-before.txt), [`main-status-after.txt`](main-status-after.txt), [`main-diff-fingerprint-before.txt`](main-diff-fingerprint-before.txt), and [`main-diff-fingerprint-after.txt`](main-diff-fingerprint-after.txt).

The AC6 protection check passes: all original 19 status and diff fingerprints match byte-for-byte. The observed HEAD movement was concurrent and changed no `src`, `apps/desktop`, or `packaging` paths; this task only refreshed the two authorized ignored artifact trees.
