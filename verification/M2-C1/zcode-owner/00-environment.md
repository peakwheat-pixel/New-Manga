# M2-C1 ZCode Owner Verification — 00 Environment & Dependency Ancestry

Owner: ZCode. Task: M2-C1 (Typed IPC Contract — ZCode Owner Baseline).
Fixed base: `7478f72fe6f9872cae29f4fa12888b5e1f2380f1`.
All commands re-run by ZCode at Owner start of work (2026-09-26), Git Bash on Windows.

## Worktree binding

| Check | Command | Observed | Result |
|---|---|---|---|
| Worktree root | `git rev-parse --show-toplevel` | `G:/CODEX/New Manga.worktrees/M2-C1-zcode-typed-ipc-contract` | PASS |
| Branch | `git branch --show-current` | `agent/zcode/M2-C1-typed-ipc-contract` | PASS |
| HEAD | `git rev-parse HEAD` | `7478f72fe6f9872cae29f4fa12888b5e1f2380f1` (= fixed base) | PASS |
| Common dir | `git rev-parse --git-common-dir` | `G:/CODEX/New Manga/.git` (shared history with main repo) | PASS |
| Status | `git status --porcelain=v1` | 0 lines before any Owner edit; no unknown content found; nothing cleaned/stashed/reset | PASS |

## Dependency ancestry at fixed base

`git merge-base --is-ancestor <dependency> 7478f72fe6f9872cae29f4fa12888b5e1f2380f1`, re-run by Owner:

| Dependency | Integrated commit | Exit code |
|---|---|---:|
| M2-D1 | `100abfb` (full: `100abfbb51e2d59d0b0dccbb0cb6aa15ba9f6e02` per draft Task) | 0 |
| M2-I1 | `cff1e0a8658f57a2e9caf774a9de0961e8f65da3` | 0 |
| M2-I2 | `7e2da6b8eb55e437d36fa3fa11cbf3e976a834c9` | 0 |
| M2-R1 | `5803bd7` | 0 |
| M2-UI1 | `5242f64` | 0 |

All five dependencies are ancestors of the fixed base. This reproduces the Scheduler
registration result in `verification/M2-C1/scheduler-registration-7478f72.md` (on master).

## Historical draft objects

| Object | `git cat-file -t` | Ancestor of base? |
|---|---|---|
| `4d665238cc43ae9a54d70a117f2e58ba596cf1f5` (Codex draft Delivery) | commit | No (exit 1) |
| `4ee7b3e5caa17bfe24591ab288c5215e344bd85f` (Codex draft Handoff) | commit | No (exit 1) |
| `ac38dede84ff22290c9b9d579c1372c8184a7bd5` (draft head / Qoder R3 reviewed head) | commit | No (exit 1) |
| `1950a23619ae489ecc88209593eac75546d61105` (Qoder R3 Review commit) | commit | No (exit 1) |
| `86013b34da52e106ad55afc035792e9340c5aee8` (Codex pre-integration/governance) | commit | not checked for ancestry (read-only source of draft Task) |

All draft objects resolve in the shared object database and were read via `git show`
only. No draft object was merged, cherry-picked, or rebased into the Owner branch.

## Environment

- Git: 2.52.0.windows.1 (per `git --version` family used throughout verification).
- Shell: Git Bash on Windows (commands below are semantically identical to the
  PowerShell-form prescriptions in the Task; exit code semantics unchanged — same
  deviation class as recorded by the Qoder R3 session, see its report).
- Python: 3.14.x (used only for SHA-256 hashing of one blob and link parsing; no
  product code executed).

## Known instruction/evidence naming note

The dispatching prompt cites `verification/M2-C1/review-r3-4d66523/03-finding-recheck.md`
as an example R3 evidence file. That exact filename does not exist in commit
`1950a236…`. The third file in that evidence set is `03-delivery-scope.log`; the
per-finding recheck material lives in `05-r008-source-ownership.log`,
`06-r001-r006-regression.log`, and `07-coverage-notrun-decision.log`. All were read;
no evidence was missing, only the example filename differs. Recorded here as a
documentation note, not a drift blocker.
