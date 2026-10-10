# P02 Review response SHA-256 EOL-basis errata R1

- Timestamp / Agent / Task: 2026-10-10 07:46 +08:00 / Codex / P02.
- Scope: correct the hash basis in R2/R3 Review metadata and preserve both the original DSH worktree byte digest and the committed Git blob digest. Review response contents and Review outcomes are unchanged.

## Cause and corrected values

The DSH worktree preserved response text with mixed line endings. The project candidate uses `core.autocrlf=true`; Git committed canonical UTF-8 LF blobs, while a Windows checkout uses CRLF. The earlier `response_sha256` values came from pre-commit DSH worktree bytes, so they could not be reproduced from the committed reports.

| Review | Original DSH worktree bytes | Original SHA-256 | Committed Git blob bytes | Canonical SHA-256 now recorded |
|---|---:|---|---:|---|
| R2 | 12049 bytes, 83 LF + 1 CRLF | `D5C7A65322C14CA1C1EB1992E78CE6B00617AA5067724C0C423CCCD0982ABC86` | 12048 bytes, UTF-8 LF | `9869F229DADD4A173C74B737321270AEF504C5266B2AA2A100CF999B41696612` |
| R3 | 8600 bytes, 54 LF + 1 CRLF | `9D508F71381B16E7638869766D83B4556004C400BE0BDD5DF9993BA834C5468D` | 8599 bytes, UTF-8 LF | `A07E7DE8DA8C2F1466763EDC037227C39E7E2C5900E616122B19CC3FB5D1A565` |
| R4 | canonicalized to UTF-8 LF before recording | n/a | canonical UTF-8 LF | `A2F962B6494579C162F1D0FD36EE8985819108860967E189A3EA25B3BD04B3B4` |

`response_sha256` in the R2/R3 session JSON and the current Task/checkpoints now means SHA-256 of the committed Git blob bytes. The original DSH worktree digest is retained under the distinct `original_dsh_worktree_response_sha256` metadata field, with its EOL and byte-count basis. R4's session metadata states `canonical UTF-8 LF bytes` as its hash basis.

## Historical log interpretation

`r9f-current-prestart-scope-assertions-r4.stdout.log` and `r9f-current-prestart-scope-assertions-r5.stdout.log` remain unchanged as run records. Their R2 and R3 response SHA labels respectively refer to the copied DSH worktree bytes before the later Git normalization; neither is the committed response blob digest. The canonical committed report hashes are the R2/R3 values in the table above. The earlier R1 report digest is unchanged because it already matched its committed blob.

To reproduce a canonical value, hash the bytes returned by `git cat-file blob <commit>:verification/P02/<response-file>`; do not hash a CRLF working-tree checkout and call it a Git blob hash.
