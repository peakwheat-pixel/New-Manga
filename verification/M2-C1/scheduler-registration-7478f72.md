# M2-C1 Scheduler Registration / Owner Baseline Verification

Date: 2026-09-26 (Asia/Shanghai)

## Authority and scope

Codex performed Scheduler/Release Controller registration only. No ZCode Owner implementation, independent Review, or M2-C1 Integration Gate was started in this operation. No product file, test, Schema, dependency, bootstrap, QML, React, Tauri, or runtime file was changed.

## Actual master and worktree checks

Commands were run in PowerShell against the linked master worktree:

```powershell
git -C "G:\CODEX\New Manga.worktrees\M2-UI1-integration-final-83a" rev-parse --show-toplevel
git -C "G:\CODEX\New Manga.worktrees\M2-UI1-integration-final-83a" branch --show-current
git -C "G:\CODEX\New Manga.worktrees\M2-UI1-integration-final-83a" rev-parse HEAD
git -C "G:\CODEX\New Manga.worktrees\M2-UI1-integration-final-83a" rev-parse --git-common-dir
git -C "G:\CODEX\New Manga.worktrees\M2-UI1-integration-final-83a" status --short
```

Observed before Scheduler edits:

- toplevel: `G:/CODEX/New Manga.worktrees/M2-UI1-integration-final-83a`
- branch: `master`
- HEAD / Owner fixed base: `7478f72fe6f9872cae29f4fa12888b5e1f2380f1`
- common dir: `G:/CODEX/New Manga/.git`
- master worktree status: clean
- Git: `2.52.0.windows.1`; Python: `3.14.6`; shell: PowerShell.

The repository's primary worktree `G:/CODEX/New Manga` is on `codex/preserve-preexisting-main-worktree-20260925`, has 44 pre-existing status entries classified `PRE_EXISTING_WORKTREE_CHANGE / OWNERSHIP_UNVERIFIED`, and was not edited, cleaned, stashed, reset, or used for this registration.

## Dependency ancestry

At fixed Owner base `7478f72fe6f9872cae29f4fa12888b5e1f2380f1`, `git merge-base --is-ancestor <dependency> <base>` returned exit code 0 for each:

| Dependency | Integrated commit | Exit |
|---|---|---:|
| M2-D1 | `100abfb` | 0 |
| M2-I1 | `cff1e0a8658f57a2e9caf774a9de0961e8f65da3` | 0 |
| M2-I2 | `7e2da6b8eb55e437d36fa3fa11cbf3e976a834c9` | 0 |
| M2-R1 | `5803bd7` | 0 |
| M2-UI1 | `5242f64` | 0 |

## Historical draft disposition / non-ancestry

The following commit references resolve in the shared object database but `git merge-base --is-ancestor <ref> 7478f72...` returned exit code 1 for each. Therefore they remain preserved draft/review history outside current master:

| Object | Role | Ancestor of base? |
|---|---|---:|
| `4d665238cc43ae9a54d70a117f2e58ba596cf1f5` | Codex draft Delivery | No (exit 1) |
| `4ee7b3e5caa17bfe24591ab288c5215e344bd85f` | Codex draft Handoff | No (exit 1) |
| `ac38dede84ff22290c9b9d579c1372c8184a7bd5` | Qoder R3 reviewed head / draft head | No (exit 1) |
| `1950a23619ae489ecc88209593eac75546d61105` | Qoder R3 Review commit | No (exit 1) |
| `86013b34da52e106ad55afc035792e9340c5aee8` | Codex pre-integration/governance commit | No (exit 1) |

Disposition registered in `doc/tasks/M2-C1.md`:

- Codex Delivery: `ARCHITECTURE_DRAFT / PRE_OWNER_BASELINE`.
- Qoder R3: `APPROVED_ARCHITECTURE_DRAFT`.
- R-001…R-008 remain historically closed by Qoder R3; this is not the final M2-C1 dual Review or an Integration Gate approval.

The source Contract blob at `ac38dede…:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` resolves to Git blob `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` for future Case A equivalence checks.

## Current master tree and task worktrees

Before Scheduler registration, `HEAD` did not contain these paths:

- `doc/tasks/M2-C1.md`
- `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`
- `doc/handoffs/M2-C1-4d66523.md`

The following two linked worktrees were created clean from fixed base `7478f72…`:

| Role | Worktree | Branch | HEAD | common dir | Initial status |
|---|---|---|---|---|---|
| Codex Scheduler registration | `G:/CODEX/New Manga.worktrees/M2-C1-zcode-registration` | `agent/codex/M2-C1-zcode-owner-registration` | `7478f72fe6f9872cae29f4fa12888b5e1f2380f1` | `G:/CODEX/New Manga/.git` | clean |
| ZCode Owner | `G:/CODEX/New Manga.worktrees/M2-C1-zcode-typed-ipc-contract` | `agent/zcode/M2-C1-typed-ipc-contract` | `7478f72fe6f9872cae29f4fa12888b5e1f2380f1` | `G:/CODEX/New Manga/.git` | clean |

The ZCode prompt must keep this Owner base fixed. The Task/governance registration is Codex-maintained on mainline after the fixed product base; ZCode reads it as an external authorization record and does not cherry-pick it into the Owner branch or edit Scheduler paths.

## State after registration

- `M2-C1` status: `ready`, Owner=`ZCode`, Reviewer A=`DeepSeek Harness`, Reviewer B=`Qoder`, Integrator=`Codex`.
- Prompt generation is complete; no prompt has been dispatched.
- No product implementation, Reviewer worktree, Review, Integration Gate, or integration was started.
- M2-S1 remains `NOT_RELEASED`.
