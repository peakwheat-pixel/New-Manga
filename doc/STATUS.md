# Current Development Status

Planning source of truth: [Project Rebaseline Plan](REBASELINE_PLAN.md)

Execution checkpoint: 2026-09-28 (Asia/Shanghai)

> **DIAG FIX-A release checkpoint（2026-09-28 00:2x；用户全夜自主推进指令授权，代行 Codex 释放）:** [DIAG-READING-EXPORT-001-FIX-A](tasks/DIAG-READING-EXPORT-001-FIX-A.md)（导出终态等待/投递语义修复，症状 A）released `ready`。Owner=ZCode（本会话亲自实现），非作者 Reviewer=DeepSeek Harness，Integrator=代行 Codex（集成记录标注"代行 Codex"待追认）；fixed base=`32ef1dd60cd82ac3a5fa18dfc5f834ec8639164a`（释放时 main HEAD）；branch=`agent/zcode/DIAG-READING-EXPORT-001-FIX-A-terminal-wait-semantics`；worktree=`G:/CODEX/New Manga.worktrees/DIAG-FIX-A-zcode`。Allowed paths：`tests/reading_export/test_viewmodels.py`、`verification/DIAG-READING-EXPORT-001-FIX-A/**`、本 Task 文件、`doc/handoffs/DIAG-READING-EXPORT-001-FIX-A-*.md`；`src/ui/viewmodels/export/viewmodel.py` 仅在测试侧方案不足时按 Task AC 评估（默认不动）。FIX-B 保持 `proposed / NOT_RELEASED` 串行释放。
> **DIAG FIX-A integration checkpoint（2026-09-28 01:3x；代行 Codex 集成，待追认）:** [DIAG-READING-EXPORT-001-FIX-A](tasks/DIAG-READING-EXPORT-001-FIX-A.md) is `done`。双轮 DSH 非作者 Review：R1 `changes_requested`（1×P2 snapshots 排队消费暴露面 + 5×P3；[r1](reviews/DIAG-READING-EXPORT-001-FIX-A-dsh-r1.md)）→ R2 修订（6 处谓词、探针严格判定 completed/exit-code、定向日志）→ R2 [复核](reviews/DIAG-READING-EXPORT-001-FIX-A-dsh-r2.md) `approved` @`6fe7bd86`（6/6 处置通过、无新增 P0-P2、5×P4 观察 deferred）。两轮报告逐字节导入（SHA256 于 review-dsh-import）。R1 交付=`77a78b25`、R2 交付=`db5ee918`、Owner tip=`6fe7bd86`；集成 merge=`a8b94df1f1ee091a9cca894c421e9ffc3ad30614`（parents `0b30d3d9`+`6fe7bd86`；唯一 Task 冲突取 Owner 交付版）。判别证据：旧谓词忙碌主线程 R1 324/400、R2 27/200 miss（先红）→ 新谓词 0 miss + completed 全满（后绿）→ 故障注入 3/3、2/2 正确检出（判别力保留）。集成核验：8 Owner 路径全授权、禁改零命中、`diff --check` exit 0、集成 head 全仓复跑 **1316 passed, 5 skipped, EXIT=0**（6 OpenSSL 差值=shell PATH，已解释）；记录：[integration-a8b94df1](../verification/DIAG-READING-EXPORT-001-FIX-A/integration-a8b94df1/integration.md)。修复为测试等待语义，产品排队投递行为未变；诊断 U3 仍未决。
> **DIAG FIX-B release checkpoint（2026-09-28 01:3x；用户全夜自主推进指令授权，代行 Codex 串行释放）:** [DIAG-READING-EXPORT-001-FIX-B](tasks/DIAG-READING-EXPORT-001-FIX-B.md)（Reader 心跳生命周期，症状 B）released `ready`。Owner=ZCode，非作者 Reviewer=DeepSeek Harness，Integrator=代行 Codex；fixed base=`a8b94df1f1ee091a9cca894c421e9ffc3ad30614`（FIX-A 集成 merge，治理 commit 之前）；branch=`agent/zcode/DIAG-READING-EXPORT-001-FIX-B-reader-heartbeat-lifecycle`；worktree=`G:/CODEX/New Manga.worktrees/DIAG-FIX-B-zcode`。Allowed/forbidden paths 以 Task 文件为准。

> **Current M2 checkpoint:** M2-RC1 大媒体资源 runtime is integrated and `done` at merge `3a246840`; [M2-RC2](tasks/M2-RC2.md) is integrated and `done` at Codex merge `88f972fe`. No M2 successor is released. The separate Legacy reliability diagnosis [DIAG-READING-EXPORT-001](tasks/DIAG-READING-EXPORT-001.md) is integrated and `done` at Codex merge `e0a0e784`; symptom-A repair [FIX-A](tasks/DIAG-READING-EXPORT-001-FIX-A.md) is `done` at integration `a8b94df1` (test-wait semantics; DSH r2 approved); symptom-B repair [FIX-B](tasks/DIAG-READING-EXPORT-001-FIX-B.md) is `ready` (serial release). The historical flaky is closed at the test-observation level; product queued-delivery behaviour is unchanged and diagnosis U3 stays open. S1-B3/B6/B8 remain `NOT_RUN`, S1-B5 remains `UNVERIFIED`; product-level security/packaging claims remain gated.

> **DIAG-READING-EXPORT-001 integration checkpoint（2026-09-28；Codex 额度恢复前由 ZCode 会话代行 Codex Lead/Reviewer/Integrator，用户指派）:** [DIAG-READING-EXPORT-001](tasks/DIAG-READING-EXPORT-001.md) is `done`. Owner=DeepSeek Harness delivered `8b36e98e` / Owner tip `77c661b0` (fixed base `83de13dfe0521125715c2e26da75b96a63103938`); the proxy Codex non-author [Review](reviews/DIAG-READING-EXPORT-001-77c661b0.md) `approved` is committed at `c90b8b27` (0×P0/P1; R-001 P2 = report §4.1 overstated "full-suite event load" as the confirmed amplifier while §5 U3 stays open — wording corrected at integration, U3 preserved; R-002 P3 accepted); integration merge=`e0a0e784498fc339a4d666dd931cc67cfb65bbdb` (parents `c90b8b27` + `77c661b0`; Owner history unrewritten; sole conflict on `doc/tasks/DIAG-READING-EXPORT-001.md` resolved to the Owner-delivered version per the user-directed rule). Diagnosis result: **15/15 fixed matrix `NOT_REPRODUCED`** (0 failures, all exit 0; run-01's 11 environment skips — 6 OpenSSL/2 docTR/1 numpy/2 torch — disclosed individually, not counted as passes) with **both historical mechanisms located and reproduced by exactly the two allowed read-only probes**: symptom A = terminal-signal queued delivery vs `running`-flag polling (isolated 0/400, busy-main-thread 26/200, 26/26 delivered by one more `processEvents`); symptom B = leaked reader heartbeat writing a closed SQLite store (deterministic; stack frames identical to historical stderr; heartbeat stays active after failure). `NOT_REPRODUCED` ≠ fixed. Integration verification (object-level; matrix rerun not required by the Integrator): 24 paths all authorized, zero forbidden paths, `git diff --check` exit 0, `_finish` order byte-identical between `0275290` and base, claim = one-line status flip, evidence cross-checked line by line — record: [integration-e0a0e784](../verification/DIAG-READING-EXPORT-001/integration-e0a0e784/integration.md). U1–U3 remain open (owned by the FIX tasks), U4 (independent defects) adopted. Follow-ups registered `proposed / NOT_RELEASED`, not started: [DIAG-READING-EXPORT-001-FIX-A](tasks/DIAG-READING-EXPORT-001-FIX-A.md) (export terminal wait/signal-delivery semantics; suggested Owner=ZCode, Reviewer=DeepSeek Harness) and [DIAG-READING-EXPORT-001-FIX-B](tasks/DIAG-READING-EXPORT-001-FIX-B.md) (reader heartbeat lifecycle; same roles); both freeze base/branch/worktree only at a future §5.1 release.

> **M2-RC1 release checkpoint（2026-09-27；用户明确授权）:** [M2-RC1](tasks/M2-RC1.md) Contract-Aligned Large-Media Resource Channel Runtime is registered and released `ready / LARGE_MEDIA_RESOURCE_CHANNEL_RUNTIME_RELEASED`. Owner=ZCode, non-author Reviewer=DeepSeek Harness, Integrator=Codex; release commit=`fb87414af906348666ffd7d001a276e86c4cd5bc`; fixed base=`2dca20cd971e3c2ae1a3ab8134ac0acdf98c45f1`; branch=`agent/zcode/M2-RC1-large-media-resource-channel-runtime`; worktree=`G:/CODEX/New Manga.worktrees/M2-RC1-zcode`. Contract 1.1 blob=`fc35913801297ee1876ea395f9c5041a16226f20`. Release evidence: [release-2dca20cd](../verification/M2-RC1/release-2dca20cd.md). Only the new app/resource-channel paths are authorized; shared Contract, Legacy QML, Schema, root dependencies, packaging and release are excluded.
> **M2-RC1 integration checkpoint（2026-09-27）:** [M2-RC1](tasks/M2-RC1.md) is `done`; merge=`3a24684007fd5a5e855f324077ad996841300f27` (parents `cb6e6d51` + Owner evidence tip `ce3c3771`). Round-4 DSH Review approved reviewed head `2f6a31cd67e983e789c02cb4e33c194f0e012f23`; report `doc/reviews/M2-RC1-FIX3-2f6a31cd.md`. Codex reran pytest 43, Cargo 12, Vitest 8, E2E 10/10 twice, all exit 0; command transcript: [codex-command-transcript.log](../verification/M2-RC1/integration-2f6a31cd/codex-command-transcript.log). Contract blob=`fc35913801297ee1876ea395f9c5041a16226f20`; 62 reviewed paths plus DSH evidence import; Owner branch remains at `ce3c3771`. M2-RC1 deferred F-03/F-05 to [M2-RC2](tasks/M2-RC2.md), now done at Codex merge `88f972fe`. S1-B3/B5/B6/B8 remain open boundaries.

> **M2-RC2 integration checkpoint（2026-09-27）:** [M2-RC2](tasks/M2-RC2.md) is `done`; Codex merge=`88f972fed921c7d7a010bef38a734de2601d9ca5` (parents `6a68fdeb` + ZCode docs head `dc8e5c95`; validation head `eac5cb3e` remains in its ancestry). Fixed Task base=`22a2c2bf9a70d8c3b81edcdbe0e1ef146db556e5`; Owner branch/worktree is preserved at `agent/zcode/M2-RC2-resource-channel-hardening` / `C:/Users/49745/.codex/worktrees/m2-rc2-zcode/New Manga`. DSH FIX review approved; both DSH reports and 54 review artifacts were imported byte-for-byte, with SHA256 in [import manifest](../verification/M2-RC2/review-dsh-import-sha256.txt). R3-01 wording was corrected in the matrix. Codex reran pytest 66, Cargo 20, Vitest 15, E2E GATE 10/10 with probe 13/13, and the TTL probe; all `EXIT=0`. Full transcripts: [integration evidence](../verification/M2-RC2/integration-88f972fe/integration.md). Contract 1.1 blob=`fc35913801297ee1876ea395f9c5041a16226f20` is unchanged; S1-B3/B6/B8 remain `NOT_RUN`, S1-B5 remains `UNVERIFIED`; no product-level security, installation, or packaging-readiness claim is made.

> **DIAG-READING-EXPORT-001 release checkpoint（2026-09-27）:** The separate read-only diagnostic is registered and released `ready / READ_ONLY_DIAGNOSTIC_RELEASED`; this is not an M2 successor. Owner=DeepSeek Harness, non-author Reviewer=Codex, Integrator=Codex; `depends_on=[]`; fixed base=`83de13dfe0521125715c2e26da75b96a63103938` (`main`); branch=`agent/deepseek/DIAG-READING-EXPORT-001-reading-export-flaky-diagnosis`; worktree=`C:/Users/49745/.codex/worktrees/diag-reading-export-001/New Manga`. Scope is limited to the Task, a diagnosis report, handoff and `verification/DIAG-READING-EXPORT-001/**`; no code/tests/dependencies/contracts may change. Owner must first claim the Task and pass the PySide6 environment Gate, then run the fixed maximum 15-run matrix. The forwardable dispatch is in the release record; no active DeepSeek Harness connector/thread is available in this Codex session, so dispatch is pending and no claim or diagnostic run has started. [Release record](../verification/DIAG-READING-EXPORT-001/release-83de13df.md).

> **M2-S1 §7 threshold ruling + M2-S2 release（2026-09-26; user-authorized proxy governance）:** With Codex quota exhausted, the user directed this session to act as Codex proxy: the 7 product thresholds in [M2-S1 report §7](../doc/research/M2-S1_RESOURCE_CHANNEL_SPIKE.md) are ruled in [product-thresholds-ruling-67c3d56.md](../verification/M2-S1/product-thresholds-ruling-67c3d56.md) (T1 256 MiB max page/tile; T2 ≥32 refs/≥16 subscribers; T3 200 ms hot/1 s cold first-frame target; T4 no-Base64-materialization + bounded buffers; T5 layered trust — WebView never sees OS paths, mapped-ID confidentiality chosen; T6 300 s sliding TTL + immediate revision-bound revocation; T7 model weights on an independent channel). The ruling is user-reviewable and revocable per item; it does not modify the M2-S1 report or any Contract. [M2-S2](tasks/M2-S2.md) — Resource Channel Security Verification Spike (S1-B11 TOCTOU open-then-verify-from-handle + S1-B12 mapped-ID confidentiality) is registered and released `ready / SECURITY_VERIFICATION_RELEASED`: Owner=ZCode, Reviewer=Antigravity (non-author), base `67c3d56e`, branch `agent/zcode/M2-S2-resource-channel-security`, worktree `G:/CODEX/New Manga.worktrees/M2-S2-zcode`, release evidence [release-67c3d56.md](../verification/M2-S2/release-67c3d56.md).

> **M2-S2 integration checkpoint（2026-09-26）:** [M2-S2](tasks/M2-S2.md) is `done`. Owner ZCode delivery `d502aa5af88159a78ad1b39030f8780cca4021f7` / Handoff head `fbdf1bc237a2c34db7546e76990f3aad29dfae8d`; Antigravity non-author [Review](reviews/M2-S2-fbdf1bc2.md) commit `ea11d109` `decision=approved` (6/6 AC PASS, 24/24 probe scenarios re-run consistently in the Reviewer's own worktree, P0/P1=0, one deferred P2 R-001 GBK-console encoding finding with documented workaround). Codex integration merge `bf1d12309bee19cccf665fb2d5bb5c9d4dee7e66` (parents `7671f0c1` + `ea11d109`; Owner chain and Review preserved unrewritten; single add/add conflict on `doc/tasks/M2-S2.md` resolved to the Owner version per the M2-S1 pattern). [Post-integration verification](../verification/M2-S2/integration-bf1d1230.md): 32 changed paths all inside authorized/governance scope, zero product-code changes (`src/**`/`tests/**`/`packaging/**`/`src-tauri/**` untouched), `git diff --check` exit 0, 6 Markdown files / 9 local links / 0 broken. Prototype level closes the S1-B11/S1-B12 verification gap; product-grade guarantees remain `UNVERIFIED/NOT_RUN` (report §7: 11 NOT_RUN + 3 UNVERIFIED incl. S1-B3 DACL and S1-B8 packaged-sandbox re-run). No product security guarantee is claimed; large-media runtime stays unreleased.

> **M2-C2 release checkpoint（2026-09-26; user-approved next-step）:** The user approved the recommended next Task: [M2-C2](tasks/M2-C2.md) — Typed IPC Contract Revision (Resource Channel Thresholds and Security Conclusions) is registered and released `ready / CONTRACT_REVISION_RELEASED`. It revises [M2-C1 Typed IPC Contract](contracts/M2-C1_TYPED_IPC_CONTRACT.md) in place (`1.0`→`1.1`): §10 gains the ruled T1–T7 thresholds plus the validated security semantics (open-then-verify-from-handle resolution per S1-B11, Core-side opaque mapped-ID confidentiality per T5.4/S1-B12, typed error-code minimal set, model-weights independent channel); §11 large-media DEFERRED row is partially discharged (runtime form stays deferred). Owner=ZCode (reassigned from Codex at the user's option: Codex quota exhausted; original M2-C1 Contract owner was also ZCode), Reviewer=DeepSeek Harness (non-author), Integrator=Codex. Base `3f468e6e`, branch `agent/zcode/M2-C2-typed-ipc-contract-revision`, worktree `G:/CODEX/New Manga.worktrees/M2-C2-zcode` (created at release, clean), release evidence [release-3f468e6e.md](../verification/M2-C2/release-3f468e6e.md). The revision must not weaken existing §10 protections, must not claim implementation, and does not authorize runtime work.

> **M2-C2 integration checkpoint（2026-09-26）:** [M2-C2](tasks/M2-C2.md) is `done`. Owner ZCode delivery `67f814ffa7528da91335ef28deec3cb18f8ebf75` / Handoff+reviewed_head `c18f273ad5a7768c6ae1726610da1ac27aa958d3`; DeepSeek Harness non-author [Review](reviews/M2-C2-c18f273a.md) `decision=approved`, `no_blocking_findings` (0×P0/P1/P2; 4×P3 advisory F-01..F-04 wording/label precision, deferred). The DSH review was produced headless inside the Owner worktree with git commands sandbox-blocked, so the report arrived as untracked files: the integrator imported report + dispatch record byte-for-byte at `0bbe78f3` (SHA-256 recorded in the integration evidence) without advancing the Owner branch. The three DSH-recommended pre-integration commands were run by the integrator: scope 7 authorized paths, `diff --check` exit 0, contract blob `fc35913801297ee1876ea395f9c5041a16226f20` at delivery/reviewed/integrated heads. Codex integration merge `d574ec1ec42bade5da98ec955d02284d1451f04a` (parents `0bbe78f3` + `c18f273a`); the single add/add conflict on `doc/tasks/M2-C2.md` was resolved per the user-directed rule "master as base + Owner backfill" with a blob-identity check (`f0e8bec3`). [Post-integration verification](../verification/M2-C2/integration-d574ec1e.md): 15 paths all authorized/governance, zero product-code changes, `diff --check` exit 0, 8 files / 30 links / 0 broken, integrated contract blob still `fc359138`. Contract `1.1` now carries T1–T7 and the security semantics as design requirements (product-grade guarantees stay UNVERIFIED where sourced); runtime remains unreleased.
> **M2-S3 original release checkpoint（2026-09-26; superseded by reassignment below）:** [M2-S3](tasks/M2-S3.md) Tauri Asset Protocol Feasibility Probe was initially released `ready / TAURI_ASSET_PROTOCOL_PROBE_RELEASED`, base `90c3e45962733799d43e3aefacf4fea99f662a2c`; original Owner=DeepSeek Harness, non-author Reviewer=ZCode, branch `agent/deepseek/M2-S3-tauri-asset-protocol-probe`, worktree `G:/CODEX/New Manga.worktrees/M2-S3-deepseek`. It is research-only; no product code or Contract change is authorized. Original release evidence: [release-90c3e459](../verification/M2-S3/release-90c3e459.md).

> **M2-S3 reassignment checkpoint（2026-09-26; user-directed; superseded by integration below）:** Owner changed to ZCode, non-author Reviewer to DeepSeek Harness. At reassignment, the Owner branch/worktree `agent/zcode/M2-S3-tauri-asset-protocol-probe` / `G:/CODEX/New Manga.worktrees/M2-S3-zcode` was clean at the fixed base `90c3e45962733799d43e3aefacf4fea99f662a2c`. The former DeepSeek Harness branch/worktree remains preserved and clean at the same base, authorization revoked; it is not cleaned or deleted. [Reassignment evidence](../verification/M2-S3/reassignment-9b2d40c2.md).

> **M2-S3 integration checkpoint（2026-09-26）:** [M2-S3](tasks/M2-S3.md) is `done`. ZCode Owner tip=`bcef79e775bf4a5b4a4eceb4c3e63ac630aa6de9`; DeepSeek Harness non-author Review `approved` only at `233d0901e1de817a8357be7047346de7d8c49f23` (0×P0/P1, 5×P2, 5×P3). Codex separately reviewed the later `233d0901..bcef79e7` delta and reran the real Tauri/WebView2 probe twice plus one symlink-specific run (each exit 0, 16/16 PASS). Integration merge=`6799c73a75c16252602ac85f4454a5ac1b45b8d2`, parents `a006acb9`+`bcef79e7`; sole Task add/add conflict resolved as master base + Owner backfill. [Integration verification](../verification/M2-S3/integration-bcef79e7/integration.md): 27 authorized source paths, no forbidden product paths, both source and integrated `diff --check` exit 0. S1-B1 is PASS only for a single host, Rust simulated map, one-shot body and unpackaged probe; true streaming, revision binding, sliding TTL, S1-B3/B5/B6/B8 and product runtime remain NOT_RUN/UNVERIFIED. At this 2026-09-26 checkpoint the runtime had not yet been released; this was superseded by the M2-RC1 release below. M2-C2 F-01..F-04 remain deferred because M2-RC1 does not edit the Contract.

> **Historical T3.2.1 transfer checkpoint (2026-09-26; superseded by the Legacy Closure Audit above):** At the user's direction, ZCode owns continuation of the open Release Gate; Codex retains integration responsibility. **The independent full-scope Review of `78aba7c` was executed by Qoder (non-author, Codex assignment) — earlier "DeepSeek Harness" attributions for this round are corrected (R-014); DeepSeek Harness remains the reviewer of record for the historical packaging rounds.** Sandbox use is prohibited; the user accepts a complete local host simulation as the test route, without calling it clean-machine coverage. **Review verdict on `78aba7c`: `changes_requested`** ([report](reviews/T3.2.1-78aba7c.md) @ `agent/qoder/T3.2.1-review-78aba7c` `4422f79`) — the fixed package itself was independently re-verified (all key hashes recomputed, full-package verifier EXIT=0, packaging tests 12 passed, zero product defects in Gate scope); the blockers were evidence archiving and AC wording only. **The remediation is delivered**: R-001/R-009 raw+reviewer logs committed into `verification/.../host-simulation/artifact-run-logs/` and `review-78aba7c/`; R-002 app version corrected to `0.1.0` (`src/bootstrap/core_assembly.py:90`); R-003 **AC6 = PARTIAL** (11/12 steps PASS, pipeline step = fail-closed diagnostic; converting to PASS needs an explicit user/Codex ruling); R-004 all host-simulation ACs annotated「本机模拟路线；非干净机覆盖」and **Codex is asked to confirm whether the user's ruling extends to AC6/AC8**; R-005 exit-code wording fixed; R-006/007/008/012/013 addressed; R-010/R-011 spun off as `proposed` child Tasks [T3.2.1-REPAIR-15](tasks/T3.2.1-REPAIR-15-reader-export-lineage.md) and [T3.2.1-REPAIR-16](tasks/T3.2.1-REPAIR-16-bookshelf-page-count.md) (Owner suggestion Qoder). Remaining open risks after remediation: clean Windows (no Python) start unproven; Windows 10 x64 matrix `NOT_RUN`; real docTR-weight success path `NOT_RUN`; `console=True` in the release package; ICU resolved from host System32. Fixed input unchanged: `08f9bd85137965df922db524bc92917af513bd24`, manifest `073b84f5…9608`, exe `3aac341a…74b2`; no rebuild. See [checkpoint](../verification/T3.2.1/clean-release-gate-20260926/checkpoint.md) (ZCode Continuation Run Record + 返修记录) and the [delivery Handoff](handoffs/T3.2.1-zcode-delivery-20260926.md). No integration/merge/push before the reviewer signs off on the new head.

> **Historical Codex integration checkpoint (2026-09-26; T3.2.1 open-gate disposition superseded by the closure audit above):** Delivery b18fa0e70ec4356a207fd7d941cdcf0cb2f1c285 + Qoder review branch b66788a813b04c0305226331c54327e178093664 are integrated at merge 6519125406161924b0021e021e79fea07cf673fc. Qoder's appended re-review is approved for use as integration input only. Fixed build input 08f9bd85137965df922db524bc92917af513bd24 was not rebuilt. AC3=PASS（本机模拟路线；非干净机覆盖）with completely Python-absent clean Windows startup NOT_RUN; AC6/AC8=PARTIAL (clean-Windows scope not waived); AC9=PARTIAL (warm-cache repeat only); AC10=PASS after Codex integration validation. Full Release Gate remains OPEN; no push, upload, installer or signing is authorized.


| Field | Current value |
|---|---|
| Historical T3.2.1 child-slice integration | REPAIR-14 was the latest child-slice integration at `296131b57a4c3660949ecbdfb6003c6201023dab`; 184 focused tests passed. The parent integration `6519125` and this child record remain historical evidence, not current blockers. |
| T3.1.1 Release Gate base | `e771179`; delivery `899bd3c`; independent Review `4e1eb3a` approved |
| Branch | `master` |
| Mainline base checked before this audit/control baseline | `ade58140ac37d972385be416b4cc3ee7d81073b3`; T1.2.1 integrated at `9a14310`, evidence at `e92c414`. |
| Current milestone | M2 Desktop Architecture Migration first wave `FIRST_WAVE_RELEASED / BOUNDED_IMPLEMENTATION` is complete; T3.2.1 Legacy track is `CLOSED_WITH_LIMITATIONS / SUPERSEDED_BY_M2`. |
| Stage | **Stage B — Controlled Execution** |
| Current product checkpoint | T1.1.1, T1.1.2, T1.2.1, T2.1.1, T2.2.1 and T3.1.1 are verified complete. M2 first-wave M2-I1/I2/R1/UI1 are integrated. T3.2.1 is closed with limitations; AC6/AC8/AC9 remain PARTIAL and the listed clean-machine/Windows 10/real-weight/cold-start items remain NOT_RUN. |
| Current Active Task | [DIAG-READING-EXPORT-001-FIX-B](tasks/DIAG-READING-EXPORT-001-FIX-B.md) is `ready` (serial release 2026-09-28 01:3x): Owner=ZCode, non-author Reviewer=DeepSeek Harness, base=`a8b94df1f1ee091a9cca894c421e9ffc3ad30614`, branch/worktree=`agent/zcode/DIAG-READING-EXPORT-001-FIX-B-reader-heartbeat-lifecycle` / `G:/CODEX/New Manga.worktrees/DIAG-FIX-B-zcode`. [FIX-A](tasks/DIAG-READING-EXPORT-001-FIX-A.md) is `done` (integration `a8b94df1`, DSH r2 approved). DIAG-READING-EXPORT-001 is `done` (integration `e0a0e784`); M2-RC1/M2-RC2 `done`; no M2 successor released. |
| M2 first-wave release | M2-D1, M2-I1/I2/R1/UI1, M2-C1, M2-S1, M2-S2, M2-C2, M2-S3, M2-RC1 and the separate M2-RC2 F-03/F-05 slice are integrated. |
| Most recent Owner/reviewer | DIAG-READING-EXPORT-001: Owner=DeepSeek Harness (`77c661b0`); independent non-author Review=Codex proxy (`approved` at `77c661b0`, commit `c90b8b27`); Integrator=Codex proxy (`e0a0e784`). Owner branch/worktree remains preserved at `agent/deepseek/DIAG-READING-EXPORT-001-reading-export-flaky-diagnosis` / `C:/Users/49745/.codex/worktrees/diag-reading-export-001/New Manga`. |
| M2-RC1 Owner branch/worktree | `agent/zcode/M2-RC1-large-media-resource-channel-runtime` at tip `ce3c3771d15c60b743b1e1da936edc445676b305`; verification left worktree clean and the integrator did not advance the branch. Worktree=`G:/CODEX/New Manga.worktrees/M2-RC1-zcode`. Master integration worktree=`G:/CODEX/New Manga.worktrees/M2-UI1-integration-final-83a`; the pre-existing dirty user main worktree remains untouched. |
| T3.2.1 historical Review references | REPAIR-8 Review `2585efd69009cd7620c6b020e67df90c7d49b0f1` approved delivery `3cdfdee126e8aab6b7930e49460a753abc69dad0` / tip `37d5488ebf8e33f897e802b4147cbd5fb1ad8e04` for documentation only. REPAIR-9 Review `85f8c59d0a012c1edc4e466187b5b42515297d74` returned `changes_requested`; REPAIR-10 Review `ddc21a2f3cf5521675e95d6e2a8f8f50b1c065fb` approved packaging-test path independence only; REPAIR-11 Review `4f2f8a07e5b8119834cdc4cfd0fd0aa5c62ac4cc` returned `changes_requested`; REPAIR-12 Review `a6564862649b00fd91fa4e4ea8a2f64205eb71b7` approved its evidence slice only. Qoder Review `b66788a813b04c0305226331c54327e178093664` approved only as an integration input, not release. |
| T3.2.1 integration evidence | At head `6519125`, focused packaging/bootstrap tests: 34 passed; artifact verifier 7/7 checks true; compileall exit 0. These are historical Legacy checks and do not imply clean-machine or real-weight coverage. Logs: `verification/T3.2.1/integration-6519125/`. |
| T3.2.1 smoke evidence | Fixed input `08f9bd85137965df922db524bc92917af513bd24`; local host simulation covered Book/Chapter/Page, Reader export and restart recovery. Pipeline returned `completed_with_failures / PROVIDER_NOT_CONFIGURED`, supporting AC5 diagnostics only; it is not successful AC6 output. AC3 remains PASS（本机模拟路线；非干净机覆盖）; no-Python clean Windows `NOT_RUN`; AC6/AC8 `PARTIAL`. |
| T3.2.1 compile evidence | No rebuild. Fixed Build 2 was hash-verified against its manifest and exe hash; integrated-head `compileall -q src/bootstrap packaging` exited 0. Full record: `verification/T3.2.1/integration-6519125/integration-evidence.md`. |
| Current blockers | S1-B3/B5/B6/B8 and product-grade security/IPC/packaging remain verification boundaries; no product-level security or package-readiness claim is authorized. The released diagnostic must stop as `blocked` if its supported PySide6 environment cannot be established; no code implementation is authorized by it. |
| Full Gate closure audit | Current disposition and AC/Finding matrix: [legacy-closure-audit-20260926.md](../verification/T3.2.1/legacy-closure-audit-20260926.md). Prior Codex closeout `b800d11`, integration `6519125`, fixed-package checkpoint and ZCode Handoffs remain historical evidence; none is rewritten. |
| AC3 environment route | User prohibits Sandbox and accepts complete local host simulation for AC3. At this historical checkpoint AC3=PASS（本机模拟路线；非干净机覆盖）; fully Python-absent clean Windows coverage=NOT_RUN. Sandbox artifacts are historical and must not be launched. Windows 10 x64=NOT_RUN. |
| F-003 disposition | REPAIR-11 Delivery `9622395` corrected the four wording instances; Review `4f2f8a0` independently marked R11-AC4 PASS. The REPAIR-11 slice overall remains `changes_requested` for F-11-1/F-11-2; no historical Review/log is to be rewritten. |
| G7-002 source ruling | Codex fixed the REPAIR-7 count source to `verification/T3.2.1/repair-5/reference-check.log` blob `fdddfc19225c66ca32a85a3ebe5b5e1cc3fe1dfe` at revision `297c3dd7d0c977eb22eedefd0ba1ae03d29b64cd` (identical at REPAIR-7 base `14f587c`). The `e54a7b6` blob `09b5f2d20a592694031ff40e3c02d7dc8e48d6aa` is historical 40/39 evidence, not the 41/40/27/19 derivation source. Both stay read-only. |
| REPAIR-8 allowed paths | Antigravity may change only `doc/tasks/T3.2.1-REPAIR-5.md`, `doc/tasks/T3.2.1-REPAIR-6.md`, `doc/handoffs/T3.2.1-REPAIR-6-f6dc383.md`, its new REPAIR-8 Handoff, and `verification/T3.2.1/repair-8/**`. Codex alone maintains this STATUS and the REPAIR-8 Task. Product code, tests, dependencies, Schema, original reference log, REPAIR-7 Handoffs and Reviewer reports are excluded. |
| REPAIR-9 allowed paths | `packaging/**`, `tests/packaging/**`, `verification/T3.2.1/repair-9/**`, and one new REPAIR-9 Handoff. Codex alone maintains this STATUS and the Task file. `src/**`, dependencies, Schema, REPAIR-7/8 artifacts and existing Review reports are excluded unless Codex separately expands scope. |
| REPAIR-10 allowed paths | Antigravity may change only `tests/packaging/**` for F-3(b), add evidence under `verification/T3.2.1/repair-9/**`, and add one new REPAIR-10 Handoff. Task/STATUS/Plan/index registration is Codex-owned; `src/**`, `packaging/**`, dependencies, Schema, REPAIR-7/8 artifacts, any Review report and the original `repair-5/reference-check.log` are prohibited. Base=`eeb095ea94cdf0d477bcb09ab7c761883b06f833`. |
| REPAIR-11 allowed paths | Antigravity may change `verification/T3.2.1/repair-11/**`, only the four F-003 wording instances in `doc/tasks/T3.2.1-REPAIR-6.md` / `doc/handoffs/T3.2.1-REPAIR-6-f6dc383.md`, and one new REPAIR-11 Handoff. Codex alone owns Task/STATUS/Plan/index registration. Base=`188d72a9d144b8cab16f77757abc46318ac8e5e6`; O-1 is already present and REPAIR-10 F-3(b) is approved. Product code, tests, packaging, dependencies, Schema, old evidence and all Review reports are excluded. |
| REPAIR-12 outcome | Base=`962239521afbfec72025ab01941f89e08116ffc4`; Delivery=`a2f6695bb289518db656f4d266910dccaa171207`; Handoff/tip=`8738c41d7215920935e6fa067d3740e69280cdc6`; independent Review=`a6564862649b00fd91fa4e4ea8a2f64205eb71b7` `approved` for the evidence slice only. O-12-2 is handled in the Codex closeout record; no Owner branch is merged. |
| REPAIR-13 registration | ZCode / DeepSeek Harness; `done`; fixed base=`8738c41d7215920935e6fa067d3740e69280cdc6`, product delivery=`aed009405fd523c52fa45e604afe40f01cef3d45`, final Handoff/evidence head=`13ae23f65e963cf1d5aea19634572627e5e709db`, independent Review report=`ccd26a4b4ef19a33ad91841602535614705213bd` (`APPROVE_WITH_CONDITIONS`, C1/C2 satisfied); integration=`6fe7455d0927ae0b4328b77f117893d373797d92`. Parent Gate status unchanged. |
| REPAIR-14 integration | [T3.2.1-REPAIR-14](tasks/T3.2.1-REPAIR-14.md); Owner=Antigravity; `done`; base=`4ab6f58c06cb0691413e2630cb48a145c18c383a`; delivery=`43b24eefaa1d517f51c7fd8dba7c658a58415d89`; Handoff tip=`2f0d26645a5e3597977859f0624d72f561d38ba1`; DeepSeek Harness Review=`f616175e24229c4fbcffb0145e10764e0c7f93df` (`approved`); integration=`296131b57a4c3660949ecbdfb6003c6201023dab`. R14-008 GUI-native create substep=`NOT_RUN` (accepted fixture deviation); R14-010 counts corrected in integration record. Parent Gate OPEN at this integration checkpoint; AC3 was BLOCKED then, a historical status superseded by the current checkpoint above. Evidence: [integration record](../verification/T3.2.1/repair-14/integration-record.md), [Review](../verification/T3.2.1/repair-14/review-report-dsh-r2.md). |
| Pre-reconciliation dirty main-worktree files | Preserve `experiments/TASK-017/README.md`, the uncommitted `.codewiki/`, `.codex/`, `.dsh/`, `.gemini/`, `.qoder-credits/`, `.qoder/`, `.tmp.driveupload/`, `.workbuddy/`, `.zcode/`, `docs/superpowers/plans/`, `material/`, `wiki/codewiki/temp/`, and all other pre-existing dirty paths. No cleanup or overwrite was performed. |
| Worktrees | All prior worktrees remain preserved. REPAIR-13 ZCode worktree remains at `13ae23f`; its three untracked DSH prompt/run/report files were preserved. The author branch was not merged wholesale; the fixed REPAIR-13 task delta was applied to `master`. No worktree was deleted or pruned. |
| Evidence | [REPAIR-13 Task](tasks/T3.2.1-REPAIR-13.md); [independent Review](../verification/T3.2.1/repair-13/review-report-dsh.md); [C2 diff-check supplement](../verification/T3.2.1/repair-13/diff-check-full-post-c2.md); [Codex integration record](../verification/T3.2.1/repair-13/integration-6fe7455.md); parent [T3.2.1 Release Gate](../verification/T3.2.1/release-gate-c2fcb1c.md). |

## Parallel architecture governance registration

`GOV-001` is `done`: Codex integrated its documentation registration at merge `969f7a5e535b6d98b163bab9fb6ac2f6e8512088` from fixed base `1e8cb1157c987945316351728f725073b8b109f9`; DeepSeek Harness independently [approved](reviews/GOV-001-2e8f4bf.md) it at `bbf24e73b0d5b40f23f90ce851e47c7cf681ab2a`. [AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) records the user-accepted target. M2 first wave and M2-C1 are complete; T3.2.1 remains `closed_with_limitations / SUPERSEDED_BY_M2`. The preexisting dirty main worktree remains untouched.

## Verified completed capability

SQLite v2 core persistence, managed copy, image/PDF/picture-MOBI import,
Webtoon tiled reading, scheduler/executor, rendering/export, connection
ownership, diagnostics wiring, four top-level routes, backup/restore service
tests and restore admission/latch tests are present and covered by the fresh
isolated suite. This is implementation evidence, not a claim of real-provider
quality or release readiness.

T1.1.2 manual rectangle/polygon creation, canonical page-coordinate conversion,
real SQLite persistence, revision creation, deletion, Inspector cleanup,
source-file protection, production bootstrap wiring and fresh integration
verification are now complete.

## Open gaps

1. T3.2.1 is `closed_with_limitations / SUPERSEDED_BY_M2`; its incomplete Legacy ACs retain their original states and are not M2 blockers. Cross-architecture acceptance requirements are registered in the Rebaseline Plan and closure audit; future release-only items remain deferred.

## Stage B execution gate

T1.1.2, T1.1.1, T1.2.1 and T2.1.1 are integrated and verified. Preserve all
dirty files and worktrees. `TASK-013` remains the historical task; completed
T1.1.2 and the completed T2.1.1 state belong to the Current Roadmap.

## T2.1.1 Release Gate checkpoint

Codex created the formal [T2.1.1 Task](tasks/T2.1.1.md) and the isolated
Qoder worktree `G:/CODEX/New Manga.worktrees/T2.1.1-design-f-qml` from
`7f341355968f69fc3db7b6824d73ec7d56c182be`. The selected token delivery was
fixed to `pragma Singleton` + `qmldir`. Qoder delivered, Codex completed
non-author review, repaired the one blocking status-badge defect, and
integrated the task at product code commit `5da1cf6`.

## T2.1.1 Non-author Review / Integration checkpoint

Codex reviewed Qoder delivery `bc49ef9` with evidence/Handoff head `ddb2044`.
The authorized QML/test/verification scope was respected; `Main.qml` palette
binding, `AppShell.qml` rail token, and presentation-only `SettingsView.qml`
changes were accepted as in-scope. The light-mode dark-canvas consequence was
handled with the F `.vfloat`-style `CanvasCaption`; the webtoon canvas ground
remains an IMPORTANT deferred finding.

One BLOCKING finding was found in `NavBadge.qml`: `st-run` was used as a solid
background with `on-accent` text (2.54:1 in dark mode), violating the F status
badge contract. A focused test was first red, the minimum fix was committed
as `5da1cf6`, and the test became green. Qoder history is preserved in merge
commit `e34e19c`.

Fresh integration evidence: focused QML/workbench/reader-export `382 passed`,
full suite `1178 passed, 11 skipped, 0 failed, 1 warning`, compileall exit 0,
bootstrap smoke exit 0, and diff-check clean. Environment skips are documented
in [integration evidence](../verification/T2.1.1/integration-5da1cf6.md).
Review: [review-bc49ef9](../verification/T2.1.1/review-bc49ef9.md).
Result: **T2.1.1 = VERIFIED_COMPLETE**. Its successor now has its own
Release Gate.

## T2.2.1 Release Gate / completion checkpoint

Codex created the formal [T2.2.1 Task](tasks/T2.2.1.md), implementation plan,
and [Release Gate](../verification/T2.2.1/release-gate-ef1a9b8.md) at base
`16810c5`. ZCode delivered the functional seam at `df637df`; Qoder delivered
the QML/UI head `0846573` in
`G:/CODEX/New Manga.worktrees/T2.2.1-qoder`. Codex approved the non-author
review and integrated the serial chain at product code head `fe9fca0`.

The frozen scope is: Reader chapter picker, Workbench empty-state picker,
dismissible command-error presentation, and webtoon `Tokens.bgCanvas`
consistency. Region six-state rendering, command palette, storage, bootstrap,
Schema, provider/runtime, and dependency changes are excluded.

Focused integration verification is `278 passed`, exit 0. Compile and smoke
are exit 0. Full-suite verification is `1209 passed`, six explicit OpenSSL
skips, one known torch-environment failure, exit 1; this limitation is
recorded in [integration evidence](../verification/T2.2.1/integration-aad510b.md)
and is not hidden as PASS. Result: **T2.2.1 = VERIFIED_COMPLETE**.

## T3.1.1 independent Release Gate and integration checkpoint

Codex created the formal [T3.1.1 Task](tasks/T3.1.1.md), implementation plan,
and [independent Release Gate](../verification/T3.1.1/release-gate-e771179.md)
at governance base `e771179`. Antigravity delivered `899bd3c`; DeepSeek Harness
independently reviewed it in a separate worktree and approved it at `4e1eb3a`.
Codex then integrated the product delivery at `0c70e44`, merged the Review and
Handoff evidence, and reran the focused/core/compileall/smoke gates.

Integration evidence is [integration-899bd3c](../verification/T3.1.1/integration-899bd3c.md):
focused `220 passed`, core `49 passed`, compileall exit 0, smoke exit 0, and
`git diff --check` exit 0. R-001/R-003 wording is corrected by explicit Task
disposition; R-002 remains a documented non-blocking P2 defer.

Result: **T3.1.1 = VERIFIED_COMPLETE**. T3.2.1 now has its own Release Gate;
implementation has not started.

## T3.2.1 Windows Packaging Release Gate / delivery Review checkpoint

Codex established the formal [T3.2.1 Task](tasks/T3.2.1.md) and
[Release Gate](../verification/T3.2.1/release-gate-c2fcb1c.md) from the verified
T3.1.1 baseline `c2fcb1c`. REPAIR-2 delivered product head
`7d687f51567d4f947fee9b3f6eff4bc95e2b6413` and evidence/Handoff head
`ffff7c688df07165c6e801c0c9572e9c4910cb9e`. DeepSeek Harness independently
reviewed it at commit `4613338815406be0fdf2240cb1e5715a619f61f7` and returned
`CHANGES_REQUESTED`: R-008 still passes after its production branch is removed,
and AC7's Handoff `PASS` conflicts with the Task's `PARTIAL / NOT_RUN`. The
delivery remains isolated; `master` has no T3.2.1 product integration.

### T3.2.1-REPAIR-3 review result

[T3.2.1-REPAIR-3](tasks/T3.2.1-REPAIR-3.md) delivered product head
`d79d7dd251cd5f10434ea40c54e15e8bae42d374` and evidence/Handoff head
`c04497e157bb76dabdc70aedabd07ba3496d45e4`. DeepSeek Harness reviewed the
fixed delivery and returned `CHANGES_REQUESTED` at
`54f2627196969309d5c3942caf19ccec6c6ab7b5` for R-017–R-021. R-008's test
discrimination passed independent mutation; AC3 remains `NOT_RUN`, AC6/AC7
remain `PARTIAL / NOT_RUN`, and R-014–R-016 remain open.

### T3.2.1-REPAIR-4 release record

[T3.2.1-REPAIR-4](tasks/T3.2.1-REPAIR-4.md) is `ready` and released to
Antigravity. Delivery head is `f39ddc0fcaeb8c8271d73376f82b3ec9f15c0fd9`;
Handoff commit is `f2581a44d1198639ad00fd386e1fbe1dc61c1f7a`. DeepSeek Harness
reviewed it at `dc199f607c407adce40d303cb182b28f9a76a1db` and returned
`CHANGES_REQUESTED` for F-001: `doc/tasks/T3.2.1.md:153` points to a nonexistent
REPAIR-4 Handoff filename.

REPAIR-4 remains `changes_requested`; its review report and the author delivery
stay on their isolated branches. REPAIR-5 is `ready` on branch
`agent/antigravity/T3.2.1-repair-5`, worktree
`G:/CODEX/New Manga.worktrees/T3.2.1-antigravity-repair-5`, based on the valid
REPAIR-4 author tip `0e0905f8041743175239183d9c4ab7eabb78cb90`. Its scope is
F-001 plus relative-link and commit-object reachability self-checks for
`doc/tasks/T3.2.1*.md`. AC3 and AC5 remain `NOT_RUN`; AC6 and AC7 remain
`PARTIAL / NOT_RUN`; R-014–R-016 remain open. No source, test, packaging,
dependency, Schema or product behavior changes are authorized. The new fixed
head requires fresh independent DeepSeek Harness review; Codex must still
complete the full T3.2.1 Release Gate before any product integration.

The hard final boundary is D07/D08: a real Windows x64 machine without Python,
venv, source checkout or developer PATH must complete the package workflow,
restart with data intact, preserve source/data safety, and leave no residual
process. TASK-004's minimal onedir experiment remains supporting evidence only;
its clean-machine E12 is `BLOCKED` and cannot satisfy T3.2.1.

The frozen boundary is: additive v4 migration, SQLite adapters for the existing
progress/history ports, one-time non-destructive legacy JSON import, bootstrap
injection, and migration/data-loss evidence. TASK-028 Library/Page/Region work,
v1–v3 migration edits, backup UI, Pipeline/Provider/QML and packaging remain out
of T3.1.1 scope. T3.2.1 packaging is released only within its own Gate.

## T1.1.1 preparation Release Gate

Codex reviewed the fixed evaluation `base=1fa5f89` → `head=ed607b7` from
`G:\CODEX\New Manga.worktrees\T1.1.1-detector-evaluation`.

- Result: **CONDITIONAL_PASS — implementation scope may be prepared; production
  implementation is not started.**
- Selection: docTR local detection (`fast_base` default proposal); CTD is
  **NO-GO** under the current GPL-3.0 and unverified weight-license chain.
- Verification: the evaluation harness was independently rerun with the
  recorded Python 3.12 environment: `22/22 checks`, exit `0`; the result was
  written outside the repository. Evaluation evidence remains at
  `verification/T1.1.1/`.
- Formal Task: [T1.1.1 Production Text Detector](tasks/T1.1.1.md).
- Release conditions: adapter and merge-policy tests, pinned local weights with
  typed missing-weight failure, harness promotion plus real-page quality pass,
  license/compliance re-check, and explicit CPU/GPU torch packaging choice.
- Historical checkpoint state: Task was `proposed`; no owner/branch/worktree or
  production implementation had been released at that preparation review.
  The current implementation/review state is recorded below.

## T1.1.1 implementation Review checkpoint

Codex independently reviewed ZCode delivery
`4a1ed6ca2778301da983f9f9159210a2fcca6985` against base
`1fa5f893649ec3c9f13f0823aca838548d863393` in
`G:\CODEX\New Manga.worktrees\T1.1.1-production-text-detector`.

- Owner: ZCode; non-author Reviewer/Integrator: Codex.
- Result: **CHANGES_REQUESTED — NOT APPROVED FOR INTEGRATION**.
- Blocking findings: R-001 horizontal merge tolerance is not used; R-002 block
  padding is not clipped to page bounds; R-003 torch is not pinned and CPU/GPU
  environments use different torch minor versions; R-004 compliance re-check
  is not present as reproducible verification evidence.
- Important follow-ups: default weight-fetch destination does not match the
  production default path; merge-policy tests do not cover the critical
  threshold/boundary mutations.
- Fresh evidence: focused CPU `41 passed` and GPU `41 passed`; compileall,
  bootstrap smoke and diff check exit 0. Full-suite failures reproduce in the
  fixed `1fa5f89` control and are recorded as baseline evidence, not as a
  T1.1.1 regression.
- Review report: [T1.1.1 review 4a1ed6c](../verification/T1.1.1/review-4a1ed6c.md).
- Integration: none; master product code remains at the prior integrated
  T1.1.2 state. ZCode must deliver a new head and wait for re-review.

## T1.1.1 R2 Review checkpoint

Codex reviewed ZCode R2 delivery `2f116a2` against base `4a1ed6ca` in
`G:\CODEX\New Manga.worktrees\T1.1.1-production-text-detector`.

- R2 code commit: `2f116a2`; follow-up evidence/Handoff commit:
  `4a631355316e959e9a9704f1ead2eaed39cbf7a3`.
- Result: **APPROVED FOR CODEX INTEGRATION WINDOW**; all six historical
  blockers are fixed and fresh CPU/GPU focused suites are `46 passed` each.
- Fresh full-suite evidence is recorded in
  [review-2f116a2](../verification/T1.1.1/review-2f116a2.md): implementation
  environment `1069 passed, 6 skipped, 2 failed`; baseline environment
  `1043 passed, 11 skipped, 1 failed`. The only product failure is the
  pre-existing export signal race; the other implementation-environment
  failure is the expected model-runtime readiness assertion.
- IMPORTANT deferred findings: correct the stale author pass/skip split in the
  R2 evidence, and assign the export race to a separate export/reading repair
  window. Neither is a T1.1.1 R2 code blocker.
- Integration: none yet; master remains at the prior T1.1.2 product state.
  ZCode must not merge. Codex owns the next serial integration gate.

## T1.1.1 Integration Gate checkpoint

The scope reconciliation was authorized by the user. The isolated candidate
merge at `f56f441` preserves all ZCode commits and includes the required
`src/bootstrap/app.py` detector injection and supporting `tests/**` files.
Fresh focused CPU tests (`46 passed`), bootstrap detection-to-SQLite probe,
bootstrap smoke, compileall, real-material detection, source protection, and
diff check passed. The full suite recorded `1077 collected = 1070 passed + 6
skipped + 1 known environment failure`, exit 1; the failure is the expected
`test_registry_readiness` assertion because this detector venv contains torch.
The historical export signal race remains a separate deferred issue and was
not part of this diff. Full evidence:
[T1.1.1 Codex integration evidence](../verification/T1.1.1/integration-f56f441.md).

## T1.2.1 Non-author Review / Integration Gate checkpoint

Codex reviewed ZCode delivery `c54f360` against base `d11d927` in
`G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`; the author
handoff is `ace633a`.

- Result: **REVIEW_BLOCKED — NOT APPROVED FOR INTEGRATION**.
- Scope: the implementation diff stays within the authorized settings,
  ViewModel, SettingsView.qml, bootstrap and two test paths. The author
  worktree was clean.
- Blocking findings: the UI-created provider profile ID is not resolvable by
  the production registry, and saved network/proxy settings are not applied
  to the provider transport. A minimal provider-to-pipeline mirror repair was
  tested and committed only in isolated Codex candidate `0b4e434`; it was not
  merged to master.
- Fresh evidence: focused candidate tests `161 passed, 6 skipped`, exit 0;
  compileall, bootstrap smoke, source-protection subset, and diff check exit
  0. Full suite `1094 passed, 6 skipped, 1 failed, 1 warning`, exit 1; the
  only failure is the known torch-installed registry-readiness environment
  assertion.
- Evidence: [T1.2.1 review](../verification/T1.2.1/review-c54f360.md) and
  [Codex integration evidence](../verification/T1.2.1/integration-0b4e434.md).
- Status: `T1.2.1 = REVIEW_BLOCKED / IMPLEMENTED_NOT_VERIFIED`. Do not start
  T2.1.1. ZCode must resolve B-001/B-002 and wait for re-review.

## T1.2.1 R3 Non-author Review checkpoint

Codex reviewed the ZCode R3 implementation `d978d6f` against `ace633a` and
the R3 Handoff `7376bce` in
`G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`.

- Result: **CHANGES_REQUESTED — R3 REVIEW_BLOCKED**.
- Scope: `git diff ace633a..d978d6f --stat` contains exactly the six
  authorized R3 paths; QML, `src/ports/**`, SQLite schema, Roadmap and STATUS
  are untouched by the R3 implementation.
- The single-profile happy path is independently reproduced through the
  migrated SQLite row, `_load_pipeline_settings`/
  `_load_pipeline_defaults`, `build_provider_runtime`, fixed registry-slot
  resolution and a recording transport.
- Remaining blocking findings: one profile id cannot alias multiple capability
  slots; `proxy_policy` semantics and missing-network fail-closed behavior are
  not preserved; production `StdlibTransport` lacks the credential store for
  proxy credentials; disabled fixed-slot profiles still resolve; and binding
  does not validate the profile capability declaration.
- Fresh R3 verification in the stated implementation venv: focused
  `410 collected = 403 passed + 6 skipped + 1 failed`, exit 1; full
  `1124 collected = 1117 passed + 6 skipped + 1 failed`, one warning, exit 1;
  compileall, six smoke runs and diff-check exit 0. The single failure is the
  known torch registry-readiness environment assertion; the six skips are
  OpenSSL-unavailable TLS cases.
- Evidence: [R3 review](../verification/T1.2.1/review-d978d6f.md) and
  [R3 edge probes](../verification/T1.2.1/r3-edge-probes-d978d6f.log).
- Status remains `T1.2.1 = REVIEW_BLOCKED / IMPLEMENTED_NOT_VERIFIED`. No R3
  product commit is integrated; do not start T2.1.1.

## T1.2.1 R4 revision Release Gate

Codex has frozen the [formal Task](tasks/T1.2.1.md) after the
[R3 review](../verification/T1.2.1/review-d978d6f.md). This records the next
authorized revision, not a claim that implementation has resumed or passed.

- **Owner / reviewer**: ZCode / Codex (non-author). Original base
  `d11d927a46c9d2350b0e8e8161abb8ff21acba79`; reviewed R3 implementation
  `d978d6f17f52b5b02ce7c2efa434e491e7cc878c`; current author Handoff HEAD
  `7376bce954e700c43a4fed5dbdc43b71580c3fcf`.
- **Recovery**: `agent/zcode/T1.2.1-settings-ui-viewmodel` at
  `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`, clean when this
  Gate was recorded. Recheck branch, HEAD, dirty state and Git common dir
  before author work; stop on divergence.
- **Allowed**: only the source, test, Task, Handoff and verification paths in
  [T1.2.1 §允许修改范围](tasks/T1.2.1.md#允许修改范围). The current R4
  reconciliation permits only the single `SettingsView.qml` capability filter;
  other QML remains forbidden. `0b4e434` remains an isolated unmerged
  candidate, not the repair base.
- **Exit**: R4 implementation `39dbbf7` and Handoff `a527b85` were reviewed by
  Codex. B-003 follow-up delivery `e5716ac` / Handoff `e025c9a` is now
  independently approved; product integration and final verification are the
  current Codex-only next step.

## T1.2.1 R5 non-author review checkpoint (historical; superseded by integration)

Codex reviewed ZCode R5 implementation `e5716ac` against `39dbbf7` and Handoff
`e025c9a` in `G:\CODEX\New Manga.worktrees\T1.2.1-settings-ui-viewmodel`.
The author worktree is clean at `e025c9a`.

- Result: **REVIEW APPROVED — B-003 CLOSED; READY FOR INTEGRATION VERIFICATION**.
- R5 implementation scope is limited to `src/bootstrap/app.py` and
  `tests/core/test_transport_credential_assembly.py`; Handoff and redacted
  probe are the only accompanying evidence paths.
- `_credential_store()` catches construction/import failures and returns
  `None`; production `assemble_services` constructs one store and shares it
  with transport, provider resolver and SettingsViewModel. The Handoff
  §10.2③ cleanup is confirmed in scope because it removes a duplicate vault
  construction inside the same authorized assembly file.
- Fresh Git Bash full: `1139 passed, 1 known torch environment failure, 0
  skipped, 1 warning`, exit 1. Fresh PowerShell full: `1133 passed, 6
  OpenSSL skips, 1 known failure, 1 warning`, exit 1. Assembly/fail-closed
  focused: `5 passed`, exit 0; broader R5 focused set: `90 passed`, exit 0.
- Compileall exit 0; six bootstrap smoke runs passed; diff-check exit 0.
  Fresh production probe passed: two real assemblies, SQLite binding,
  registry resolution, provider client request, exact proxy Basic header,
  zero auth failures, secret absent from output, and vault cleanup true.
- Evidence: [R5 review](../verification/T1.2.1/review-e5716ac.md).
- Status: `T1.2.1 = READY_FOR_INTEGRATION_VERIFICATION`; Codex may now
  integrate serially. Do not start T2.1.1 before final integration evidence.

## T1.2.1 R4 non-author review checkpoint (historical)

Codex reviewed ZCode implementation `39dbbf7` against the R3 implementation
baseline `d978d6f` and Handoff `a527b85` against `7376bce` in the author
worktree. The author worktree is clean at `a527b85`.

- Result: **R4 EDGE REVIEW APPROVED; INTEGRATION BLOCKED — B-003**.
- The implementation diff contains exactly six paths: registry, runtime,
  Settings ViewModel, the explicitly reconciled `SettingsView.qml` filter,
  and two focused test files. `src/bootstrap/app.py` is unchanged.
- R4-B001 multi-capability aliasing, B002 network policy/fail-closed behavior,
  B004 disabled-slot behavior, and B005 capability validation were reproduced
  by independent runtime probe. Evidence: [R4 review](../verification/T1.2.1/review-39dbbf7.md)
  and [R4 probe](../verification/T1.2.1/r4-probe-39dbbf7.log).
- B-003 remains BLOCKING: production line 642 still constructs
  `StdlibTransport()` without `credential_store`. The existing authenticated
  proxy adapter subset passes, but that is not production bootstrap evidence.
- B-003 is **authorized for the next delivery only**: use the existing
  credential-store seam with best-effort `None` fallback, add an assembly-level
  test and a local redacted authenticated-proxy probe. No ports, schema,
  dependencies or QML redesign are authorized.
- Fresh author-worktree evidence: Git Bash focused `421 passed + 1 known
  torch readiness failure`, full `1135 passed + 1 known failure`; PowerShell
  focused `415 passed + 6 OpenSSL skips + 1 known failure`, full `1129 passed
  + 6 skips + 1 known failure`; compileall exit 0, six smoke runs 6/6, and
  diff-check exit 0. The known failure and environment skips are not reported
  as all-green.
- Status: `T1.2.1 = REVIEW_BLOCKED_B003_PENDING / NOT INTEGRATED`. Do not
  start T2.1.1. Next executor: ZCode for the bounded repair; Codex remains
  non-author Reviewer/Integrator.

## Current Project Control Dashboard

Detailed evidence and maps are in [PROJECT-AUDIT-2026-09-22](../verification/PROJECT-AUDIT-2026-09-22.md).

| Field | Current value |
|---|---|
| TaskStatus | T3.2.1=`closed_with_limitations / SUPERSEDED_BY_M2`; M2-C1=`done`; M2-S1 research=`done`. |
| ExecutionState | M2-S1 Owner original commits, Handoffs, initial `changes_requested` Review and final `APPROVED` Review preserved in shared history; merge=`4103493`; [integration evidence](../verification/M2-S1/integration-4103493.md). Product tests=`NOT_RUN` by Task scope. |
| Current Executor | None for a released Task. Codex retains scheduler/product Gate responsibility; DeepSeek Harness Owner research is complete. |
| YOU ARE HERE | M2 first wave integrated -> M2-C1 done/Gate PASSED -> M2-S1 research done -> product threshold/security decisions pending. |
| Dependency Blocking Chain | Future large-media runtime needs a separately released Task, user decisions on the 7 thresholds in M2-S1 report §7, and validation of S1-B1–B12 (especially TOCTOU and reference path confidentiality). |
| `Safe Parallel` | RepoWiki/derived knowledge refresh; isolated research-only work |
| Conditional | No REPAIR-13 evidence follow-up remains. The C2 record's pre-cleanup count differs from Codex's fixed-range recount (12 vs 13); all reported whitespace is removed and post-C2 full diff-check is exit 0. |
| Do Not Start Yet | IPC runtime/product implementation remain NOT_RELEASED. M2-S1 research completion does not authorize product code, dependency, Schema or shared Contract change. |
| Safe To Resume | All original G:/C: Review, Owner and Qoder worktrees and their uncommitted audit evidence remain preserved. M2-C1 integration can be audited from fixed commits and Gate record. |
| Latest audit checkpoint | [M2-S1 integration verification](../verification/M2-S1/integration-4103493.md) at merge `4103493`; [release](../verification/M2-S1/release-85a2aa7.md), [scope registration](../verification/M2-S1/scheduler-registration-0c2e202.md), both Reviews and M2-C1 [Gate verification](../verification/M2-C1/integration-gate-readiness-96666bf.md) remain preserved. |

### Historical position map (superseded by the current checkpoint above)

```text
T1.1.2 VERIFIED_COMPLETE
        ↓
T1.1.1 VERIFIED_COMPLETE @ f56f441
        ↓
T1.2.1 VERIFIED_COMPLETE @ 9a14310 / e92c414
        ↓
T2.1.1 VERIFIED_COMPLETE @ 5da1cf6
        ↓
T2.2.1 VERIFIED_COMPLETE @ fe9fca0
        ↓
T3.1.1 VERIFIED_COMPLETE @ 0c70e44
        ↓
T3.2.1 implementation authorization (PASS TO START) @ c2fcb1c
        ↓
T3.2.1 isolated repairs; full Release Gate OPEN (parent AC3 BLOCKED; REPAIR-13 done at integration `6fe7455`)
        ↓
REPAIR-13 task delta integrated at `6fe7455` (C1/C2 conditions satisfied; parent Gate still open)
        ↓
  → REPAIR-14 done @ integration `296131b` (delivery `43b24ee`, Handoff `2f0d266`, Review `f616175e` approved; R14-008/010 disposition recorded; parent Gate OPEN / AC3 BLOCKED)
```

### Historical parallel execution matrix (as of the REPAIR-14 checkpoint)

| Work item | Readiness | Class | Conflict |
|---|---|---|---|
| T1.2.1 | complete | closed | provider runtime, VM, Settings QML, bootstrap integrated |
| T2.1.1 | complete | `CLOSED` | four-page QML/theme; F token contract; T1.2.1 UI contracts |
| T3.1.1 | complete | closed | SQLite v4 progress/export persistence integrated and independently approved |
| T3.2.1-REPAIR-8 | approved | documentation slice only | DSH report `2585efd`; no product/Gate approval |
| T3.2.1-REPAIR-9 | changes_requested | review findings open | DSH report `85f8c59`; Codex O-1 whitespace correction is isolated at `188d72a`; F-2/F-4/O-3 remain |
| T3.2.1-REPAIR-10 | approved | packaging tests only | DSH report `ddc21a2`; 12 passed without external `PYTHONPATH`; full Gate remains open |
| T3.2.1-REPAIR-13 | done | QML import/readability, dialog contrast, F-13-2 + F-13-4 and local two-page export | ZCode owner; DeepSeek Harness independent reviewer; delivery `aed0094`, evidence head `13ae23f`, Review conditions satisfied; Codex integration=`6fe7455`; parent Gate remains open |
| T3.2.1-REPAIR-14 | done | F-13-3: restore persisted bookshelf entries after process restart | Antigravity; delivery=`43b24ee`; Round 2 Review=`f616175e` approved; integration=`296131b`; R14-008 deviation and R14-010 counts are recorded; parent Gate remains open |
| T3.2.1 full Release Gate | in_progress | Codex closeout | AC10 integration closure=PASS at 6519125; parent Gate remains OPEN. AC3=PASS（本机模拟路线；非干净机覆盖）; fully Python-absent clean Windows start=NOT_RUN. AC6/AC8/AC9 are PARTIAL; Windows 10 and real-weight success paths remain NOT_RUN. |
| RepoWiki | ready | safe parallel derived write | `wiki/repowiki/**` only |
| CodeWiki | conditional | derived write, freshness caveat | `wiki/codewiki/**`; not Task truth |

## T1.2.1 integration completion checkpoint

Codex fast-forwarded master to integration evidence commit `e92c414`, whose
code integration merge is `9a14310`. The author chain from `c54f360` through
`e025c9a` is preserved as the merge's second parent. The final integration
tree is clean; the pre-existing main-worktree dirty files remain untouched.

- R5 Review: [review-e5716ac](../verification/T1.2.1/review-e5716ac.md),
  BLOCKING findings = 0.
- Final integration evidence: [integration-9a14310](../verification/T1.2.1/integration-9a14310.md).
- Final product probe: two production assemblies, persisted SQLite binding,
  registry/provider resolution, exact authenticated proxy header, zero auth
  failures, no secret exposure, and vault cleanup all passed.
- Final focused suite: 122 passed, exit 0. Full suite: Git Bash 1139 passed,
  1 known torch environment failure, 0 skipped; PowerShell 1133 passed, 6
  OpenSSL skips, 1 known failure; both exit 1 only for the documented
  environment assertion. Compileall, six smoke runs, and diff-check passed.
- Result: `T1.2.1 = VERIFIED_COMPLETE`. T2.1.1 subsequently passed its own
  Release Gate and is recorded in the completion checkpoint above.

## Recovery instruction

```powershell
Set-Location 'G:\CODEX\New Manga'
git status --short --branch
git rev-parse HEAD
Get-Content doc\STATUS.md
Get-Content doc\REBASELINE_PLAN.md
git log -8 --oneline --decorate
```

If the worktree is dirty, preserve the listed files and identify their owner
before any edit. Resume from the latest committed checkpoint, not chat memory.

Worker recovery check:

```powershell
Set-Location 'G:\CODEX\New Manga.worktrees\T1.1.2-qoder'
git status --short --branch
git rev-parse HEAD
```
