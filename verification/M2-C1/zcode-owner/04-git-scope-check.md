# M2-C1 ZCode Owner Verification — 04 Git Scope & Whitespace Check

Owner: ZCode. Fixed base: `7478f72fe6f9872cae29f4fa12888b5e1f2380f1`.

## A. Staged-tree check before the Owner Delivery commit

Because the verification files are part of the delivery commit itself, the
prescribed base..delivery checks are recorded here in their staged
(`--cached`) form, which is byte-equivalent to the commit-tree diff at the
moment of commit. The post-commit re-check against the fixed delivery hash is
recorded in the Owner Handoff.

`git diff --name-status 7478f72fe6f9872cae29f4fa12888b5e1f2380f1 --cached`
(raw, exit 0):

```text
A	doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
A	verification/M2-C1/zcode-owner/00-environment.md
A	verification/M2-C1/zcode-owner/01-source-trace-owner-base.md
A	verification/M2-C1/zcode-owner/02-decision-log.md
A	verification/M2-C1/zcode-owner/03-blob-equivalence.md
A	verification/M2-C1/zcode-owner/05-drift-and-links.md
```

`git diff --check 7478f72fe6f9872cae29f4fa12888b5e1f2380f1 --cached`
→ no output, exit 0 (no trailing whitespace / conflict markers).

## B. Allowed-path verification, item by item

| Path | Allowed by Task? |
|---|---|
| `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | YES — the one authoritative Owner Contract |
| `verification/M2-C1/zcode-owner/00-environment.md` | YES — `verification/M2-C1/zcode-owner/**` |
| `verification/M2-C1/zcode-owner/01-source-trace-owner-base.md` | YES |
| `verification/M2-C1/zcode-owner/02-decision-log.md` | YES |
| `verification/M2-C1/zcode-owner/03-blob-equivalence.md` | YES |
| `verification/M2-C1/zcode-owner/05-drift-and-links.md` | YES |

Forbidden-path probes over the staged diff: no `src/**`, `tests/**`,
`packaging/**`, `src-tauri/**`, QML/React/TypeScript files, Schema/migration,
dependency/lock files, bootstrap, Domain Contract, Task/Plan/Status/Index,
historical Review/evidence files. The staged path list above is exhaustive and
contains only the six allowed paths.

## C. Environment note

`git add` printed `LF will be replaced by CRLF` warnings for the new files
(`core.autocrlf` on Windows). Repository-stored blobs use LF; the staged
Contract blob is `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3`, identical to the
adopted draft blob, so normalization does not affect Case A identity. Working-copy
line endings are irrelevant to the stored objects.

## D. NOT_RUN register

| Item | Status | Reason |
|---|---|---|
| Product pytest | NOT_RUN | Document-only Task; adding/running product tests is out of scope |
| GUI / QML runtime checks | NOT_RUN | No UI change; no UI run authorized |
| IPC Runtime / serialization / version handshake tests | NOT_RUN | No runtime exists; implementing/starting one is forbidden (M2-S1 NOT_RELEASED) |
| Large-media channel capacity tests | NOT_RUN | Deferred to independent Spike |
