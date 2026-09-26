# M2-C1 ZCode Owner Delivery — DSH independent Review r3: Qoder Reviewer B cross-check

Reviewer of this document: DeepSeek Harness (Reviewer A, non-author). Subject: the formal
Qoder Reviewer B review at commit `0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5`
(Decision = `APPROVED`).

This is an independent reading of the Qoder original, not an endorsement borrowed from it.
Qoder's decision carries no weight in this Review's own conclusion.

## 1. Locating the artefact

`doc/reviews/M2-C1-zcode-7de1cd2-qoder.md` does **not** exist at reviewed_head
`b237728…`. It exists only at `0d73983…`, the tip of
`refs/remotes/origin/review/qoder/M2-C1-zcode-7de1cd2`. It was read with
`git show 0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5:doc/reviews/M2-C1-zcode-7de1cd2-qoder.md`
and is therefore **outside the reviewed tree**. The Qoder review has not been merged into
the Owner line and must not be treated as part of the artefact under review.

## 2. Its own scope and bindings

```text
commit   0d73983a5e1f37f104c76d8bd4c70c6f98fa36f5
message  review(m2-c1): Qoder independent review at b237728
diff scope (0d73983^..0d73983):
  A doc/reviews/M2-C1-zcode-7de1cd2-qoder.md
  A verification/M2-C1/review-qoder-zcode-7de1cd2/00-review-environment.log
  A verification/M2-C1/review-qoder-zcode-7de1cd2/01-blob-equivalence.log
  A verification/M2-C1/review-qoder-zcode-7de1cd2/02-diff-scope.log
  A verification/M2-C1/review-qoder-zcode-7de1cd2/03-ancestry.log
  A verification/M2-C1/review-qoder-zcode-7de1cd2/04-r001-r008-verification.log
  A verification/M2-C1/review-qoder-zcode-7de1cd2/05-link-limitation.log
  A verification/M2-C1/review-qoder-zcode-7de1cd2/06-notrun-register.log
git show --check 0d73983 -> no output, exit 0
```

Frontmatter binds `base_commit=7478f72…`, `delivery_commit=7de1cd2…`,
`handoff_commit=reviewed_head=b237728…`, `case: A`, `decision: approved`. All eight
evidence files named in the report exist at the Qoder commit (verified by
`git ls-tree -r`). The Qoder commit touches only its own two authorised paths.

Recorded honesty points in the Qoder original:

- `session: 31a451ce-… (UNVERIFIED - reported by user, not independently provable by Reviewer)`.
- `web_visibility: not-applicable`.
- An explicit environment deviation: the prescribed commands were written for PowerShell but
  executed under Git Bash, with the assertion that exit-code semantics are unchanged.
- An explicit "未覆盖" section listing pytest/GUI/IPC runtime as NOT_RUN and stating that the
  four dependency Tasks were confirmed by ancestry only.

## 3. Independent reconciliation of its load-bearing claims

| Qoder claim | This Review's independent result | Agree? |
|---|---|---|
| Contract blob = `4b503a17…` | reproduced (`git rev-parse HEAD:`, index, re-hash of `git cat-file blob`) | YES |
| Contract = 276 lines | reproduced (LF-canonical newline count = 276 on both sides) | YES |
| Diff scope = 8 `A` paths, all allowed | reproduced; forbidden-path probe empty | YES |
| `git diff --check` exit 0 | reproduced | YES |
| Five dependency commits are ancestors of `7478f72…` | reproduced, all exit 0 | YES |
| R-004 lifecycle semantics match `service.py:829-884` | reproduced line by line, including the `abandon` branch not setting `interruption_disposition` and `restart` setting `"restarted"` | YES |
| R-008 `list_revisions` on the port, zero service definitions | reproduced (`ports.py:30`; service count 0; delegation at service `:131`) | YES |
| R-001 `TaskProjection` = 23 fields | reproduced by independent dataclass walk | YES |
| R-005 `CredentialRef` zero hits in `src/` | reproduced (`git grep -c` exit 1) | YES |
| R-006 half-up then clamp in pixel space | reproduced (`region_canvas.py:40-41`) | YES |
| R-003 AD-001 line citations | reproduced (`:15`, `:19-24`, `:28`, `:35`) | YES |
| R-002 AD-001 large-binary line | reproduced (`:33`) | YES |
| §1 relative link has no target in the Owner tree; non-blocking, "not merit finding" | Confirmed the fact (exit 128 at reviewed_head, exit 0 at `ac38dede…`). **Disagreement on disposition**: this Review records it as a P3 auditability finding (F-001) rather than as no finding at all, and additionally records two further non-resolving references (F-002) that the Qoder report did not catalogue. The blocking verdict (non-blocking, no Owner rework) is reached independently and coincides. | partial |
| 54 new relative links all resolve in the R3 draft | not re-run for the draft tree (out of this Review's scope; the claim concerns `ac38dede…`, not reviewed_head) | not checked (NOT_RUN) |
| Product pytest / GUI / IPC runtime NOT_RUN | same — this Review also ran none | YES |

## 4. Divergences worth recording

1. **Link finding granularity.** Qoder evaluated only the Contract §1 link and concluded it
   "does not merit a finding". This Review's automated sweep over all eight reviewed paths
   found 49 repository references, of which nine do not resolve in the reviewed tree
   (one Markdown hyperlink plus eight prose/table path mentions, of which one is the Owner's
   own "this filename does not exist" note). The blocking outcome is the same; the
   coverage is broader. See `03-link-adjudication.md`.
2. **Blob command reproducibility.** The Qoder evidence set repeats the Owner's four
   commands, including the raw-worktree-file SHA-256. In this checkout that command yields
   `ae68c0e1…`, not `c04b5af5…` (finding F-003). The Qoder report's conclusion (blob
   identity holds) is unaffected and independently true, but the published command is not
   reproduclible as written on a CRLF checkout.
3. **Own-task provenance.** The Qoder report cites "Task 指令" as a source of its path
   authorisation, but the M2-C1 Task file is not present in the reviewed tree (finding
   F-002). This Review verified the authorisation from `origin/master` instead.

## 5. Effect on this Review's decision

None. The Qoder decision is neither inherited nor required. This Review's
`APPROVED` decision rests on its own reproductions listed above and on the three
non-blocking findings it records.
