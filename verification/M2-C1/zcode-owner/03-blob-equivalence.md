# M2-C1 ZCode Owner Verification — 03 Case A Blob Equivalence

Owner: ZCode. Case: A — `OWNER_ADOPTED_WITHOUT_SEMANTIC_CHANGE`.

## Compared objects

- Adopted draft source head: `ac38dede84ff22290c9b9d579c1372c8184a7bd5`
- Adopted draft Contract blob: `git rev-parse ac38dede…:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`
  → `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` (also the value recorded by the
  Scheduler registration evidence)
- Owner file: `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` on the Owner branch,
  created by `git show ac38dede…:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md > <file>`
  (byte-for-byte redirection; no editor normalization applied)

## Reproduction commands (Git Bash, from the Owner worktree)

```bash
git rev-parse ac38dede84ff22290c9b9d579c1372c8184a7bd5:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
git hash-object doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
git cat-file blob 4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3 | python -c "import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())"
python -c "import hashlib; print(hashlib.sha256(open('doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md','rb').read()).hexdigest())"
```

## Observed values (2026-09-26, ZCode run)

| Quantity | Adopted draft | Owner file | Equal? |
|---|---|---|---|
| Git blob SHA-1 | `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` | `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` | YES |
| Content SHA-256 | `c04b5af59c1c36ecaf862c9b63e8e410219966ea3d1e526e711ea19904b6f0d8` | `c04b5af59c1c36ecaf862c9b63e8e410219966ea3d1e526e711ea19904b6f0d8` | YES |
| Line count | 276 | 276 | YES |

The Git blob OID is exact-content identity evidence: the Owner Contract is the
same object as the Qoder-R3-reviewed draft Contract, so semantic equivalence
holds by construction, and the final Contract reviewed by both Reviewers must
carry blob `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` (verify with
`git rev-parse <final-head>:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`).

## Non-semantic delta inventory relative to the adopted draft head

The Owner delivery intentionally does **not** reproduce the draft's
governance/navigation files, because they belong to Codex's governance faces
and are outside the Owner's allowed paths:

| Draft-head path (`ac38dede…`) | Present in Owner delivery? | Reason |
|---|---|---|
| `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | YES — identical blob | Owner adoption object (Case A) |
| `doc/tasks/M2-C1.md` (draft version) | NO | Task file is Codex-Scheduler-maintained on mainline; current authoritative version lives on master, not in the Owner branch |
| `doc/handoffs/M2-C1-4d66523.md` (draft Handoff) | NO | Historical draft handoff stays frozen in history; the Owner adds a separate template Handoff |
| `doc/00_INDEX.md`, `doc/REBASELINE_PLAN.md`, `doc/STATUS.md`, `doc/tasks/README.md` (draft navigation edits) | NO | Governance navigation belongs to Codex; Owner must not modify Plan/Status/Index/Task files |
| `verification/M2-C1/review-remediation-r3.md`, `verification/M2-C1/reviewer-prompt-r3.md` | NO | Draft evidence and reviewer prompt stay untouched in history |
| `verification/M2-C1/source-trace.md` (draft) | NO — outside `zcode-owner/**` allowed paths | Equivalent Owner-base trace provided at `verification/M2-C1/zcode-owner/01-source-trace-owner-base.md` |

None of these absences changes a Contract clause; they are scope-boundary
differences only. The single product-document file of this Task — the Contract
— is byte-identical to the reviewed draft.
