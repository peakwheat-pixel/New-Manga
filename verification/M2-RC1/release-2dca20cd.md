# M2-RC1 Release Record

- **Decision:** User explicitly authorized Codex on 2026-09-27 to register and separately release the M2 large-media resource-channel runtime Task.
- **Task:** [M2-RC1 — Contract-Aligned Large-Media Resource Channel Runtime](../../doc/tasks/M2-RC1.md)
- **Release state:** `ready / LARGE_MEDIA_RESOURCE_CHANNEL_RUNTIME_RELEASED`
- **Owner / Reviewer / Integrator:** ZCode / DeepSeek Harness (non-author) / Codex
- **Dependencies:** M2-C1, M2-S1, M2-S2, M2-C2 and M2-S3 are all `done` at this release.
- **Fixed base:** `2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1`
- **Registration/release commit:** `fb87414af906348666ffd7d001a276e86c4cd5bc`; the Owner worktree starts from the fixed base above.
- **Owner branch:** `agent/zcode/M2-RC1-large-media-resource-channel-runtime`
- **Owner worktree:** `G:/CODEX/New Manga.worktrees/M2-RC1-zcode`
- **Contract baseline:** `fc35913801297ee1876ea395f9c5041a16226f20` (M2-C1 1.1)

## Authorized scope

Implement the bounded Core → Tauri host → React/WebView large-media resource-channel slice in the new app paths listed in the Task. The frontend reference is only a `http://m2res.localhost/m2id/<opaque-id>` URL; the Core↔host control DTO and bridge are internal to this Task and must be documented. Resource bytes stay out of ordinary JSON/Base64 IPC. Only synthetic `derived-cache` fixtures are authorized for tests. Contract 1.1 T1–T7 and §10.2 semantics are acceptance constraints.

Allowed and forbidden paths, runtime behavior, acceptance criteria, and test obligations are frozen in `doc/tasks/M2-RC1.md`. Shared Contract changes, Legacy QML changes, model weights, Schema/migrations, root dependencies, packaging, and product release are excluded. Product-level security remains unclaimed until S1-B3 and S1-B8 are separately verified; S1-B6 cold-cache results must be reported honestly.

## Recovery and Owner start instructions

The release commit is newer than the fixed implementation base. Create the Owner branch/worktree at exactly `2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1` and keep it clean until the Task file is copied from the release commit. Then copy only `doc/tasks/M2-RC1.md` from the recorded release commit, change its Task status from `ready` to `in_progress`, and commit that claim before implementation. Do not merge the release commit into the Owner branch; this preserves the fixed base and isolates governance registration from implementation history.

Required initial checks: `git rev-parse --show-toplevel`, `git rev-parse --path-format=absolute --git-common-dir`, `git branch --show-current`, `git status --short --branch`, `git worktree list --porcelain`, `git rev-parse HEAD`, and `git rev-parse HEAD:doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md`. Record shell/venv and exact results under `verification/M2-RC1/`.

Owner worktree was created by Codex at the fixed base and verified clean before handoff: HEAD=`2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1`, branch=`agent/zcode/M2-RC1-large-media-resource-channel-runtime`, Contract blob=`fc35913801297ee1876ea395f9c5041a16226f20`, common dir=`G:/CODEX/New Manga/.git`, status clean. The Owner worktree intentionally does not contain the release-only Task file yet; ZCode must copy that single file from release commit `fb87414af906348666ffd7d001a276e86c4cd5bc` and commit the `ready` → `in_progress` claim before implementation.
