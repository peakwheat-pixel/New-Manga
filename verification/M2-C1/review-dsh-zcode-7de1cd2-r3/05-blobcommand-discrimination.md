# M2-C1 ZCode Owner Delivery — DSH independent Review r3: blob-command discrimination

Reviewer: DeepSeek Harness (non-author). Probe: `probe-crlf-hashobject.py`, raw output
`01-blob-command-discrimination.log` (Python 3.14.6, PowerShell 7, git 2.52.0.windows.1).

## Why this probe exists

`verification/M2-C1/zcode-owner/03-blob-equivalence.md` publishes four reproduction
commands and states that the Owner file's SHA-256 equals the adopted blob's SHA-256
(`c04b5af59c1c36ecaf862c9b63e8e410219966ea3d1e526e711ea19904b6f0d8`). This Review tested,
in this checkout, whether each published command reproduces the published value.

## Verbatim probe output

```text
cwd = C:\Users\49745\.codex\worktrees\M2-C1-dsh-review-7de1cd2-r3
core.autocrlf = true

[1] git hash-object <worktree-path>        -> 4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3
[2] git hash-object --no-filters <path>    -> 1b5466eab3836a50a3a59628ad7da2e629f320ce
[3] git hash-object --path=<path> <path>   -> 4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3
[4] git rev-parse HEAD:<path>              -> 4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3
[5] git rev-parse :<path> (index)          -> 4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3

worktree bytes = 25398  CRLF = 276
LF-normalized bytes = 25122
sha1(LF-normalized) via git hash-object --stdin -> 4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3

python hashlib.sha256(raw worktree bytes)  -> ae68c0e1cd18b075bdc7947c3ad5f10406bc57dd9cfc72219f6cad5130198785
python hashlib.sha256(LF-normalized bytes) -> c04b5af59c1c36ecaf862c9b63e8e410219966ea3d1e526e711ea19904b6f0d8

git check-attr -a -> (none)
.gitattributes exists -> False

Owner-claimed blob SHA-1  = 4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3
Owner-claimed SHA-256     = c04b5af59c1c36ecaf862c9b63e8e410219966ea3d1e526e711ea19904b6f0d8
```

## Reading

| Owner-published command | Reproduces the published value here? |
|---|---|
| `git rev-parse ac38dede…:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | YES -> `4b503a17…` |
| `git hash-object doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` | YES -> `4b503a17…` (git applies the CRLF->LF filter because `core.autocrlf=true`) |
| `git cat-file blob 4b503a17… \| python -c "…sha256(sys.stdin.buffer.read())…"` | YES -> `c04b5af5…` |
| `python -c "…sha256(open('doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md','rb').read())…"` | **NO** -> `ae68c0e1…`, because this expression reads raw worktree bytes (CRLF in this clone) and applies no filter |

For contrast, `git hash-object --no-filters` on the same worktree file yields
`1b5466ea…`, confirming that the file as stored on this filesystem is not byte-identical
to the LF blob; the git-canonical identity is nonetheless exact (blob OID, index OID and
`git show` bytes all equal `4b503a17…` / 25122 bytes on both sides).

## Conclusion

Case A byte identity is TRUE and is proven by the blob-OID evidence and by the
`git show` byte comparison. One of the four published commands, however, cannot produce
the published value on a CRLF checkout and would mislead an independent replicator into
suspecting a content difference that does not exist. This is recorded as finding F-003
(P2, non-blocking, documentation reproducibility).
