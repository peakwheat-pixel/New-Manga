# M2-C1 ZCode Owner Delivery — DSH independent Review r3: Git position & object preflight

Reviewer: DeepSeek Harness (non-author). Task: M2-C1.
Session: session-5a2d596e-5db0-4651-b180-e45c1a8abedc
Shell: PowerShell 7 (`pwsh`) on Windows; repository Git linked worktree.
Date: 2026-09-26 (Asia/Shanghai).

## 1. Initial working position (recorded before any write)

Commands executed verbatim and their raw output:

```text
$ git rev-parse --show-toplevel
C:/Users/49745/.codex/worktrees/M2-C1-dsh-review-7de1cd2-r3

$ git branch --show-current
review/deepseek/M2-C1-zcode-7de1cd2-r3

$ git rev-parse HEAD
b2377288680569dbee4e2299fd7dfae4de067c54

$ git rev-parse --path-format=absolute --git-dir
C:/Users/49745/.codex/worktrees/M2-C1-dsh-review-7de1cd2-r3/.git

$ git rev-parse --path-format=absolute --git-common-dir
C:/Users/49745/.codex/worktrees/M2-C1-dsh-review-7de1cd2-r3/.git

$ git status --short
(no output; exit 0)
```

| Required value | Observed | Verdict |
|---|---|---|
| root = `C:\Users\49745\.codex\worktrees\M2-C1-dsh-review-7de1cd2-r3` | `C:/Users/49745/.codex/worktrees/M2-C1-dsh-review-7de1cd2-r3` | PASS |
| branch = `review/deepseek/M2-C1-zcode-7de1cd2-r3` | match | PASS |
| HEAD = `b2377288680569dbee4e2299fd7dfae4de067c54` | match | PASS |
| git-dir is this clone's own `C:` `.git` | `<root>/.git` | PASS |
| common-dir is the same independent clone `.git` | `<root>/.git` | PASS |
| initial status clean | 0 lines | PASS |

The checkout is an independent clone: `--git-dir` and `--git-common-dir` both point at
`<root>/.git`, not at `G:/CODEX/New Manga/.git`. This differs from the Owner/Qoder
worktrees (which share the main repository common dir) and is recorded as an
environment fact, not a deviation.

## 2. Object type of the four fixed review objects

```text
$ git cat-file -t 7de1cd27e22037d4b76b235c9f11399b0cea9463   -> commit
$ git cat-file -t b2377288680569dbee4e2299fd7dfae4de067c54   -> commit
$ git cat-file -t 4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3   -> blob
$ git cat-file -t 0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5   -> commit
```

All four objects resolve in this clone's object database. `git log --oneline -3` at HEAD:

```text
b237728 docs(m2-c1): add ZCode owner handoff for 7de1cd2
7de1cd2 docs(m2-c1): owner delivery - adopt typed IPC contract (Case A, no semantic change)
7478f72 docs(T3.2.1): close legacy gate as superseded by M2
```

## 3. Git identity used for this Review commit

```text
$ git config --show-origin --get-all user.name
file:C:/Users/49745/.gitconfig   peakwheat-pixel
$ git config --show-origin --get-all user.email
file:C:/Users/49745/.gitconfig   peak.wheat@gmail.com
$ git config --global --get user.name   -> peakwheat-pixel
$ git config --global --get user.email  -> peak.wheat@gmail.com

$ Get-ChildItem env: | where DSH_*
DSH_HOME        = C:\Users\49745\.dsh
DSH_PROFILE     = headless
DSH_PROFILE_DIR = C:\Users\49745\.dsh\profiles\headless
DSH_SESSION_ID  = session-5a2d596e-5db0-4651-b180-e45c1a8abedc
DSH_SHELL       = 1
GIT_PAGER       = cat
```

No DSH-specific Git identity (`user.name`/`user.email`) exists in config or environment;
the machine-global identity is the one every agent on this host commits with. It is
therefore the only real Git identity available to this DSH session and is used verbatim.
This is recorded as an environment fact; it does not change any Review conclusion.

## 4. Final position before the Review commit

```text
$ git status --porcelain=v1 --untracked-files=all
?? verification/M2-C1/review-dsh-zcode-7de1cd2-r3/...
```

Only the authorised Review evidence directory is untracked. No Owner delivery,
Handoff, Task, Contract, `src/**`, `tests/**`, Schema, dependency, governance
navigation, Qoder Review or other path was modified.

## 5. Prior-round material check

```text
$ git ls-tree -r --name-only HEAD -- doc/reviews verification/M2-C1 | Select-String dsh
(no match)

$ Test-Path doc/reviews/M2-C1-zcode-7de1cd2-dsh-r2.md   -> False
$ Test-Path verification/M2-C1/review-dsh-zcode-7de1cd2-r2  -> False
```

No prior-round DSH report exists in this checkout's tree or worktree. The r2 dirty
report was neither imported nor used as a conclusion source; every finding, evidence
item and decision below was re-established in this checkout.
