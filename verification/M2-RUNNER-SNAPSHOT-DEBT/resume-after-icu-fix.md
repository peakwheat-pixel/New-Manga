# M2-RUNNER-SNAPSHOT-DEBT：ICU blocker 解除与恢复点

Recorded: 2026-10-08 (Asia/Shanghai)

## 前置阻塞解除

原 blocker=`packaged_ac1_QtGui_DLL_import_failure`。它由单独释放、非作者 DSH r2 批准并经 Codex 集成的 `M2-PACKAGED-AC1-ICU-ISOLATION-FIX` 解除：

- ICU integration commit=`65ba30144048a0b8daae22205c01f8049b44b8a7`
- reviewed/fresh-tested source head=`4499217d7b2249da16d5dbf27a3219a43876aac7`
- Owner fresh packaged Gate=`26/26 PASS`，AC1 `acceptance_bridge` 成功；installer SHA256=`f2a4e2e7e92f083739bb92d2055539ea859461991b43559c3fe1f759b2c195ae`
- 证据：`verification/M2-PACKAGED-AC1-ICU-ISOLATION-FIX/REPORT.md`、`build-fingerprint.json`、`raw/packaged/cleanstart-gate.json`、`integration-validation.log`

以上仅证明前置 ICU 修复；不代替 Runner Debt 在其组合代码 head 上 fresh build/AC4。

## Runner Owner 恢复点

- Task=`M2-RUNNER-SNAPSHOT-DEBT`；Owner=Codex；Reviewer=DeepSeek Harness（非作者）；Integrator=Codex
- 原 Task base=`968c8f34601b72667831f1fd15bb20cd2c8f3cb7`
- branch=`codex/M2-RUNNER-SNAPSHOT-DEBT`
- worktree=`G:/CODEX/New Manga.worktrees/RUNNER-SNAPSHOT-DEBT-codex`
- common-dir=`G:/CODEX/New Manga/.git`
- owner tip before sync=`15cd788f10e83f6a1a215e71538bfa175b435785`
- synchronized main=`cd09c4d9d39685979d06cc4930d12e4719caccd4`
- clean dependency merge / resume code head=`bc337fcbef676d4d75befae03e6ea3f5d406e076` (parents: owner tip + synchronized main)
- Task-specific product delta relative to synchronized main: `packaging/m2ac5/run_clean_start_e2e.py`, `verification/M2-RC2/run_e2e.py`; no `src/**`, `apps/**`, or `tests/**` delta.

`bc337fcb` worktree was clean after merge and used the integrated ICU packaging code. The prior DSH r3 approval is bounded to runner implementation at `2af6b71a`; AC4 remains NOT_RUN for the combined source. Fresh sidecar/NSIS build, Dev Gate and complete Packaged Gate must bind to a new fixed source head and installer hash. Preserve prior FAIL evidence; do not modify production, wire/schema, dependencies, packaging build/spec/install flow, or expand beyond Task `allowed_paths`.
