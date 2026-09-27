# M2-C1 ZCode Owner Delivery — DSH independent Review r3: scope, binding, blob identity

Reviewer: DeepSeek Harness (non-author). reviewed_head: `b2377288680569dbee4e2299fd7dfae4de067c54`.
Fixed base: `7478f72fe6f9872cae29f4fa12888b5e1f2380f1`.
Owner Delivery: `7de1cd27e22037d4b76b235c9f11399b0cea9463`.
Shell: PowerShell 7 (`pwsh`), git 2.52.0.windows.1 (see 00-review-environment.md).

## 1. Diff scope base..delivery (raw, exit 0)

```text
$ git diff --name-status 7478f72fe6f9872cae29f4fa12888b5e1f2380f1..7de1cd27e22037d4b76b235c9f11399b0cea9463
A	doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
A	verification/M2-C1/zcode-owner/00-environment.md
A	verification/M2-C1/zcode-owner/01-source-trace-owner-base.md
A	verification/M2-C1/zcode-owner/02-decision-log.md
A	verification/M2-C1/zcode-owner/03-blob-equivalence.md
A	verification/M2-C1/zcode-owner/04-git-scope-check.md
A	verification/M2-C1/zcode-owner/05-drift-and-links.md
```

## 2. Diff scope base..reviewed_head (raw, exit 0)

```text
$ git diff --name-status 7478f72fe6f9872cae29f4fa12888b5e1f2380f1..b2377288680569dbee4e2299fd7dfae4de067c54
A	doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
A	doc/handoffs/M2-C1-zcode-7de1cd2.md
A	verification/M2-C1/zcode-owner/00-environment.md
A	verification/M2-C1/zcode-owner/01-source-trace-owner-base.md
A	verification/M2-C1/zcode-owner/02-decision-log.md
A	verification/M2-C1/zcode-owner/03-blob-equivalence.md
A	verification/M2-C1/zcode-owner/04-git-scope-check.md
A	verification/M2-C1/zcode-owner/05-drift-and-links.md
```

8 paths, all `A` (added). Count re-verified: `(git diff --name-status <range>).Count` = 8.

## 3. reviewed_head vs delivery (Handoff-only delta, raw, exit 0)

```text
$ git diff --name-status 7de1cd27e22037d4b76b235c9f11399b0cea9463..b2377288680569dbee4e2299fd7dfae4de067c54
A	doc/handoffs/M2-C1-zcode-7de1cd2.md
```

The Handoff is the only path added on top of the Delivery, exactly as the Handoff
claims (§10 of the Handoff says the review head should be the Handoff commit/tip).

## 4. Delivery is an ancestor of reviewed_head

```text
$ git merge-base --is-ancestor 7de1cd27e22037d4b76b235c9f11399b0cea9463 b2377288680569dbee4e2299fd7dfae4de067c54
exit 0
```

The reviewed_head therefore contains 100 % of the Delivery plus the Handoff.

## 5. Forbidden-path probe over base..reviewed_head

```text
$ git diff --name-only 7478f72..b237728 -- src/** tests/** packaging/** src-tauri/** \
    *.qml *.jsx *.tsx *.ts *.rs pyproject.toml requirements*.txt uv.lock package.json \
    doc/STATUS.md doc/REBASELINE_PLAN.md doc/00_INDEX.md doc/tasks/** doc/tasks/README.md
(empty output; exit 0)
```

No product code, test, packaging, Rust/Tauri/React/QML, dependency, Schema,
bootstrap, Domain Contract, Task/Plan/Status/Index or historical Review/evidence path
is touched by the reviewed range.

## 6. Whitespace / conflict-marker check

```text
$ git diff --check 7478f72fe6f9872cae29f4fa12888b5e1f2380f1 b2377288680569dbee4e2299fd7dfae4de067c54
(no output)
exit 0

$ git diff --check 7478f72..b237728 -- doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
(no output)
exit 0
```

## 7. Contract blob identity (Case A core evidence)

```text
$ git rev-parse b2377288680569dbee4e2299fd7dfae4de067c54:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3

$ git rev-parse 7478f72fe6f9872cae29f4fa12888b5e1f2380f1:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
fatal: path 'doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md' exists on disk, but not in '7478f72...'
(exit 128 -> the Contract is new at the fixed base, consistent with an `A` diff entry)

$ git rev-parse HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3

$ git rev-parse :doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md      # index
4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3
```

Blob-level byte identity with the adopted draft head:

```text
$ $h = git cat-file blob 4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3 | git hash-object --stdin
$ $h
4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3

$ git show HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md   -> 25122 bytes
$ git show ac38dede84ff22290c9b9d579c1372c8184a7bd5:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md -> 25122 bytes
identical = True
lines = 276 (matches the adopted draft's 276 lines)
```

SHA-256 of the blob content (LF-canonical) and of the raw worktree file:

```text
blob content  sha256 = c04b5af59c1c36ecaf862c9b63e8e410219966ea3d1e526e711ea19904b6f0d8
worktree file sha256 = ae68c0e1cd18b075bdc7947c3ad5f10406bc57dd9cfc72219f6cad5130198785
worktree bytes = 25398, CRLF = 276, core.autocrlf = true
```

The worktree-file SHA-256 differs **only** because this clone checks the file out with
CRLF while the repository stores LF. Git-canonical identity is unaffected: blob OID,
index OID and `git show` bytes are all identical on both sides. See finding F-003 in the
review report and 05-blobcommand-discrimination.log.

## 8. Dependency ancestry re-run at the fixed base

```text
$ for d in 100abfbb51e2d59d0b0dccbb0cb6aa15ba9f6e02 \
           cff1e0a8658f57a2e9caf774a9de0961e8f65da3 \
           7e2da6b8eb55e437d36fa3fa11cbf3e976a834c9 \
           5803bd7b9e80ba780e7a7f12078b00b9178e6f86 \
           5242f64882d2189e177fff19a75ad16630693566 ; do
    git merge-base --is-ancestor $d 7478f72fe6f9872cae29f4fa12888b5e1f2380f1 ; echo "$d -> $?"
  done
100abfbb51e2 -> 0     (M2-D1)
cff1e0a8658f -> 0     (M2-I1)
7e2da6b8eb55 -> 0     (M2-I2)
5803bd7b9e80 -> 0     (M2-R1)
5242f64882d2 -> 0     (M2-UI1)
```

All five declared dependencies are ancestors of the fixed base, independently
reproducing the Owner's `00-environment.md` and the Scheduler registration record.

## 9. Task-file reachability from the reviewed tree

```text
$ git ls-tree -r --name-only b2377288680569dbee4e2299fd7dfae4de067c54 -- doc/tasks | Select-String M2
(no match: doc/tasks/M2-C1.md is NOT in the reviewed tree)

$ git cat-file -e b2377288680569dbee4e2299fd7dfae4de067c54:doc/tasks/M2-C1.md   -> exit 128
$ git cat-file -e ac38dede84ff22290c9b9d579c1372c8184a7bd5:doc/tasks/M2-C1.md   -> exit 0
$ git cat-file -e origin/master:doc/tasks/M2-C1.md                              -> exit 0
```

The M2-C1 Task authorisation file is a Codex governance artefact held on mainline, not
part of the Owner branch. The Owner tree therefore cannot self-prove its own allowed
paths. This is expected for this branch topology and is covered in finding F-002.
