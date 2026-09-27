# M2-C1 ZCode Owner Verification — 02 Owner Decision Log

Owner: ZCode. Date: 2026-09-26.

## D-O1 — Owner disposition selection

- **Decision: `OWNER_ADOPTED_WITHOUT_SEMANTIC_CHANGE` (Case A).**
- Adopted source head: `ac38dede84ff22290c9b9d579c1372c8184a7bd5` (Qoder R3
  `reviewed_head`, draft final content head).
- The Owner Contract file
  `doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md` is reproduced byte-for-byte from
  that head. Git blob SHA-1 `4b503a170ff8ff6e995e5e5d70e3a053f9cc62c3` and
  SHA-256 `c04b5af59c1c36ecaf862c9b63e8e410219966ea3d1e526e711ea19904b6f0d8`
  are identical to the draft blob (reproduced in `03-blob-equivalence.md`).

Basis:

1. The draft Contract's semantics were independently full-reviewed by Qoder R3
   (`APPROVED_ARCHITECTURE_DRAFT`, R-001…R-008 all closed, no new finding).
   ZCode re-read the R3 report and all R-001…R-008 dispositions; none of the
   rechecked contract points (wire DTO proposal labeling, AD-001 citations,
   Run lifecycle semantics, credential honesty, half-up+clamp wording, M2-S1
   link removal, `list_revisions` port attribution) requires change.
2. ZCode independently re-validated the AS-IS evidence chain at the Owner base
   `7478f72…`: every Contract-cited source/document file is blob-identical
   between the draft AS-IS baseline `eec1aa4…` and `7478f72…`
   (`01-source-trace-owner-base.md` section A), and ZCode's own spot checks of
   enumerations, line numbers, field counts and zero-hit probes all match
   (section B).
3. The only product-tree delta between the two baselines
   (`src/bootstrap/app.py` frozen-resource resolution; new
   `tests/packaging/**` files) touches no Contract claim
   (`05-drift-and-links.md`).
4. Changing the Contract's baseline-hash references or its
   `../../verification/M2-C1/source-trace.md` link would alter the AS-IS
   evidence anchor of §1 — a semantic-anchor change — for zero semantic gain,
   and would force a full re-review where an equivalence re-validation
   suffices. The Task authorizes revision only when evidence requires it; it
   does not.

## D-O2 — Known non-semantic limitation, recorded not fixed

- The Contract's §1 relative link `../../verification/M2-C1/source-trace.md`
  resolves inside the draft head tree (`ac38dede…`) but has no target inside
  the Owner branch tree, because the allowed Owner paths do not include
  creating files under `verification/M2-C1/` outside `zcode-owner/**`, and
  Case A requires the Contract blob to stay identical. The target content
  remains readable from the fixed historical object via
  `git show ac38dede…:verification/M2-C1/source-trace.md`. The Owner provides
  an equivalent Owner-base-anchored trace in
  `01-source-trace-owner-base.md`. This is a link-scope limitation of the
  adoption path, not a semantic defect; it does not alter any normative
  clause.

## D-O3 — Re-read confirmations of historical dispositions

- Codex draft Delivery = `ARCHITECTURE_DRAFT / PRE_OWNER_BASELINE`; Qoder R3 =
  `APPROVED_ARCHITECTURE_DRAFT`. Neither is treated by ZCode as a final dual
  Review or an Integration Gate approval.
- R-001…R-008 were each re-read from the R3 report with their evidence; their
  historical closure is accepted as input, and their contract points were
  re-verified at the Owner base rather than skipped (see
  `01-source-trace-owner-base.md`).
- R3's three non-blocking notes are acknowledged: (1) the removed ACL-diagnosis
  link in the draft Task is a Codex governance-navigation matter outside Owner
  paths; (2) the `source-trace.md:28` section-number citation format is part of
  the frozen draft evidence and not adopted into an Owner file; (3) the
  `531647e` Task-wording residue is outside the reviewed head and outside Owner
  paths. None requires Owner action.

## D-O4 — Deferred / undecided items preserved

- Page-level `blocked` UI meaning/glyph/behavior: untouched, remains
  `DEFERRED / USER_DECISION_REQUIRED` (Contract §11); Run-level mapping not
  applied; no user-visible behavior chosen by ZCode.
- React UI Owner: not decided by this Task.
- Large-media transport and import path capability: untouched, remains
  `DEFERRED` to an independent Spike; no capacity/channel selection made.
- M2-S1: remains `NOT_RELEASED`; not started, not scheduled.
- Product pytest / GUI / IPC runtime: `NOT_RUN` (document-only scope).
