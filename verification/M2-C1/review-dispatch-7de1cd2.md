# M2-C1 Dual Review Dispatch Evidence

Date: 2026-09-26 (Asia/Shanghai)

## Fixed Owner binding

| Field | Verified value |
|---|---|
| Owner branch | `agent/zcode/M2-C1-typed-ipc-contract` |
| Owner worktree | `G:/CODEX/New Manga.worktrees/M2-C1-zcode-typed-ipc-contract` |
| Fixed base | `7478f72fe6f9872cae29f4fa12888b5e1f2380f1` |
| Owner Delivery | `7de1cd27e22037d4b76b235c9f11399b0cea9463` |
| Handoff / final reviewed_head | `b2377288680569dbee4e2299fd7dfae4de067c54` |
| Disposition | `OWNER_ADOPTED_WITHOUT_SEMANTIC_CHANGE` |
| Adopted source head | `ac38dede84ff22290c9b9d579c1372c8184a7bd5` |

Commands run in PowerShell:

```powershell
git -C "G:\CODEX\New Manga.worktrees\M2-C1-zcode-typed-ipc-contract" rev-parse --show-toplevel
git -C "G:\CODEX\New Manga.worktrees\M2-C1-zcode-typed-ipc-contract" branch --show-current
git -C "G:\CODEX\New Manga.worktrees\M2-C1-zcode-typed-ipc-contract" rev-parse HEAD
git -C "G:\CODEX\New Manga.worktrees\M2-C1-zcode-typed-ipc-contract" rev-parse --git-common-dir
git -C "G:\CODEX\New Manga.worktrees\M2-C1-zcode-typed-ipc-contract" status --short
```

Observed root, branch, head, and common dir match the table; status was clean. `base` is an ancestor of Delivery and reviewed_head; Delivery is an ancestor of Handoff/final reviewed_head (each `git merge-base --is-ancestor` exit 0). The Owner delta `base..delivery` contains exactly seven additions: the Contract and six files under `verification/M2-C1/zcode-owner/**`. The delta `base..b237728` adds those paths plus only `doc/handoffs/M2-C1-zcode-7de1cd2.md`. Both path sets are within the Owner Task scope.

`git diff --check 7478f72fe6f9872cae29f4fa12888b5e1f2380f1 b2377288680569dbee4e2299fd7dfae4de067c54` returned no output, exit 0. At the Owner reviewed head:

```text
git rev-parse b2377288680569dbee4e2299fd7dfae4de067c54:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3
```

This exactly matches adopted source blob `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`.

D1/I1/I2/R1/UI1 commits each passed `git merge-base --is-ancestor <dependency> 7478f72...` with exit 0. Product pytest, GUI, and IPC runtime remain `NOT_RUN` as required by the document-only Task.

## Reviewer worktrees and authorization

Both branches were absent and target directories did not exist before creation. Codex created each as a distinct linked worktree from the same fixed `reviewed_head=b2377288680569dbee4e2299fd7dfae4de067c54`:

| Reviewer | Branch | Worktree | Initial HEAD | Common dir | Initial status |
|---|---|---|---|---|---|
| DeepSeek Harness | `review/deepseek/M2-C1-zcode-7de1cd2` | `G:/CODEX/New Manga.worktrees/M2-C1-dsh-review-7de1cd2` | `b2377288680569dbee4e2299fd7dfae4de067c54` | `G:/CODEX/New Manga/.git` | clean |
| Qoder | `review/qoder/M2-C1-zcode-7de1cd2` | `G:/CODEX/New Manga.worktrees/M2-C1-qoder-review-7de1cd2` | `b2377288680569dbee4e2299fd7dfae4de067c54` | `G:/CODEX/New Manga/.git` | clean |

The checkouts are separate directories and branches; neither shares a writable worktree with the Owner or the other Reviewer. Task authorization is registered in `doc/tasks/M2-C1.md`:

- DSH report: `doc/reviews/M2-C1-zcode-7de1cd2-dsh.md`; evidence: `verification/M2-C1/review-dsh-zcode-7de1cd2/**`.
- Qoder report: `doc/reviews/M2-C1-zcode-7de1cd2-qoder.md`; evidence: `verification/M2-C1/review-qoder-zcode-7de1cd2/**`.

## Dispatch channels and status

- `dsh --version` returned `0.1.7-rc.2`; `dsh --profile headless --dump-config` exited 0 and confirmed the headless profile is available.
- Qoder CLI is installed at `C:/Users/49745/.qoder-cn/bin/qoderclicn/qoderclicn.exe`; `--help` exited 0. Qoder desktop process is present. No `qoder` command/MCP tool is registered; the installed Qoder CLI is the available dispatch route.
- Dispatch status: `RUNNING`.

- DeepSeek Harness: `dsh headless <authorized review prompt>` was started from the DSH worktree; Codex terminal exec session `72166` returned initial task acceptance/reconnaissance and remains the active process handle. This is a shell session handle, not a claimed DSH Review commit/session ID.
- Qoder: installed Qoder CLI was started with `--cwd` set to the Qoder Review worktree, `--permission-mode accept_edits`, and the authorized Review prompt; Codex terminal exec session `15760` is the active process handle. The CLI had not emitted output at the initial dispatch poll. This is a shell session handle, not a claimed Qoder Review commit/session ID.

After completion, record each agent session identity if returned, independent decision, Review commit, exact commands/exit codes, and post-review worktree checks. A started CLI process is not itself a Review or an approval.

## Review constraints

- DSH must perform a fresh, full independent technical Review of the fixed ZCode head.
- Qoder may perform Case A equivalence re-validation only after independently checking the fixed Owner head, Contract blob identity, Delivery/Handoff/evidence and the previously reviewed semantic contract. Any semantic delta requires a full Review.
- Both Reviewers must write/commit only their own authorized report/evidence and independently issue a decision bound to the same `b237728…` head. Neither may edit Owner artifacts or task governance.
- The Owner Handoff records a known relative-link limitation: Contract §1's `../../verification/M2-C1/source-trace.md` has no target in the Owner tree because the equivalent trace is under `verification/M2-C1/zcode-owner/**`. Reviewers must independently assess and disposition the effect; they must not repair it in the Owner tree.
- No product pytest, GUI, IPC runtime, Integration Gate, product integration, or M2-S1 work is authorized here.
