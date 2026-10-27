---
id: RELEASE-REPACK-2
title: 第二次 sidecar 重打包（identity provider + 缓存竞态修复）与 8 页全链复验
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: core-admin-rca
owner: null
reviewer: dsh
depends_on: []
base_commit: 2980608e0
branch: task/RELEASE-REPACK-2
worktree: G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-2
integration_commit: 090371703
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-REPACK-2
allowed_paths:
  - doc/tasks/RELEASE-REPACK-2.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - packaging/**
  - apps/desktop-avalonia/scripts/**
  - apps/desktop-avalonia/docs/**
  - verification/RELEASE-REPACK-2/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-2/**
  - G:/CODEX/New Manga.workspace/worktrees/RELEASE-REPACK-2/**
---

# RELEASE-REPACK-2：第二次 sidecar 重打包与 8 页全链复验

## 背景

`TRANSLATE-PROVIDER-1`（identity-experimental provider）与 `RUN-STORE-CACHE-RACE-FIX-1`（缓存竞态）已合入 main，但 sidecar 仍是第一次重打包的构建（不含 identity provider）。需第二次重打包，并在**同一新构建**上验证 8 页全链到 render，再推进 Export。

## Acceptance Criteria

- [x] **AC1 重打包**：用当前 `src/` 重打 base+models sidecar；记录新旧 sha256/大小；torch-free 闭包断言。→ **MET**：新 base `091a201da8a044c1830e7cb8d541b012cf458c8c5b7d392624de913fa93bf45a` / 新 models `c55319306e3022f325c1879deaa96a476dc105b206fa7135c6ae312a2a5c027b`（均 399,492B；bundle 195,375,520 / 868,862,035B）；对照 RELEASE-REPACK-1 `ed499bd7…` / `9fcb9e87…` 与原始冻结 `2b36bfeb…`；构建日志含 torch-free（858 pure modules）、0 shadowing ICU、python runtime 随包。
- [x] **AC2 同构建 8 页全链**：新 models 构建 + BOOK-FIXTURE 私有副本 + identity 绑定（`pipeline_defaults` 或 StartRun override）：translate 3/3 completed、segment/inpaint/render 22/22 completed、页 4–8 completed(0)；**0 条 PROVIDER_NOT_CONFIGURED**；给每步耗时。→ **MET**：StartRun override `provider_bindings={ocr:manga-ocr, translate:identity-translation}`；run **terminal=completed** 86.43s；step_runs detect 8、ocr/color/term_extract 各 26、translate/segment/mask_refine/inpaint/render 各 **22**，全部 completed；**0 PNC**；页 4–8 task completed（0 region）；每步耗时 detect 4.40s/ocr 5.58s/color 5.25s/term_extract 1.35s/translate 1.16s/segment 8.54s/mask_refine 15.99s/inpaint 29.76s/render 13.85s；证据 `full-chain-run.json`、`tools/run_full_chain_probe.py`。
- [x] **AC3 projection-fresh 并发复验**：新构建上跑 `verification/RUN-STORE-CACHE-RACE-FIX-1/tools/repro_scheduler.py`（或等价），断言 0 卡 running、0 regionless INVALID_INPUT。→ **MET**：① 同构建 wire 探针并发 `GetTaskProjection` **658 次@100ms** → `stuck_running=0`、`regionless_invalid_input=0`、PNC=0；② 源码拓扑 `repro_scheduler.py scheduler projection-fresh` **PASS**（`{"verdict":"PASS","stuck_running":0,"regionless_invalid_input":0}`）；证据 `full-chain-run.json`、`ac3-repro.log`、`ac3/*.json`。
- [x] **AC4 发布件与文档**：重打 base/models zip（`task-envs/RELEASE-REPACK-2/out`）、install-verify/install-smoke（幂等、console 0、许可证一致）、更新 `VERSION.json.sidecar_build`；**补 `apps/desktop-avalonia/docs/UPGRADE.md` 安装说明**（本次 allowed_paths 已含）。→ **MET**：base zip 102,981,645B / models zip 724,989,976B；install-verify 安装×2/卸载×2 幂等、license byte-identical；install-smoke **console_window_count=0**、exit 0、sidecar 随包（1955/1965 files，字节与 bundle 一致）；`VERSION.json.sidecar_build` 实测 base `091a201d…` / models `c5531930…`、repo_head=`0f4b836a5`；**UPGRADE.md 已补「构建识别（RELEASE-REPACK-2 起）」章节**（sidecar_build 字段、新旧 sha、identity experimental 声明、覆盖升级说明）；`packaging/m2ac5/README.md` §2.1 同步。
- [x] **AC5 门禁**：`scripts/test.ps1` 全绿（≥177）；pytest 相对基线 4F/2760P/9S 无新增；`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。→ **MET**：test.ps1 **177/177 passed**；pytest 实测 **3F/2772P/9S**（基线失败集合子集 + 新增测试全过，0 新增失败）；check.ps1 PASS；pin 见下表；`doc/handoffs/RELEASE-REPACK-2-handoff.md`。

## 允许修改范围

`packaging/**`、`apps/desktop-avalonia/scripts/**`、`apps/desktop-avalonia/docs/**`、本卡、STATUS/PLAN/LEDGER、`verification/RELEASE-REPACK-2/**`、workspace。

## 禁止范围

不改 Core 语义/Host 契约/旧壳、不 push、不 gc/prune；不得复用旧 exe 冒充新构建；不得伪造全链结果。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| E-RR2-REPORT | AC1–AC5 | `verification/RELEASE-REPACK-2/REPORT.md` | `fd6f819ca` | `563d5a13549996d5351ce33381e349e6594e91c127f71663aea66ee1022d087e` | CANONICAL |
| E-RR2-HASHES | AC1 | `verification/RELEASE-REPACK-2/sidecar-hashes.json` | `fd6f819ca` | `03ba3cb9b69abcfd13f01e28db0b0b73b72932fa7053432852bc2cb06d8e2c39` | CANONICAL |
| E-RR2-FULLCHAIN | AC2 | `verification/RELEASE-REPACK-2/full-chain-run.json` | `fd6f819ca` | `fd68db0dd75bf40121e25ec7da7bab99872b5d98803cdcfbcf464eb4fa8a4deb` | CANONICAL |
| E-RR2-PROBE-LOG | AC2 | `verification/RELEASE-REPACK-2/full-chain-probe.log` | `fd6f819ca` | `9394c0c416e21c9ad33f8e54d00343abeeb00ec6dcb9d9982a9609d07cec55ee` | CANONICAL |
| E-RR2-PROBE-SRC | AC2 | `verification/RELEASE-REPACK-2/tools/run_full_chain_probe.py` | `fd6f819ca` | `d8f151d69ba4dd340f5897f60b51f360399b6e20c6147c60d25b4f4fbe33759c` | CANONICAL |
| E-RR2-AC3-REPRO | AC3 | `verification/RELEASE-REPACK-2/ac3-repro.log` | `fd6f819ca` | `4be4478c1701114e013c0d87ebc61451801a990619de10363db14c3f50b8ed7c` | CANONICAL |
| E-RR2-AC3-RAW | AC3 | `verification/RELEASE-REPACK-2/ac3/repro-scheduler-projection-fresh-1793104924.json` | `fd6f819ca` | `326af76b395dadc94b8f3b8f8702109305c334c6a1a03f4e16172ea5bfa38df3` | CANONICAL |
| E-RR2-ZIPS | AC4 | `verification/RELEASE-REPACK-2/packages/zip-hashes.json` | `fd6f819ca` | `ff0e24f7e2e9240986d80b5811606a0dfff3d4eb20586dda9292744924882521` | CANONICAL |
| E-RR2-VERSION | AC4 | `verification/RELEASE-REPACK-2/packages/VERSION-models.json` | `fd6f819ca` | `101230f3f748b769883fc22a872883d6daf45d56b4375e33474130c3dcfc6e3f` | CANONICAL |
| E-RR2-VERIFY | AC4 | `verification/RELEASE-REPACK-2/smoke/install-verify-models.json` | `fd6f819ca` | `6d5461846882b044af7d6b3d8449911f48d0f01da7e16c198ff973d23f0db559` | CANONICAL |
| E-RR2-SMOKE | AC4 | `verification/RELEASE-REPACK-2/smoke/install-smoke-models.json` | `fd6f819ca` | `0c72985a097e23b9626c21af65f10b240eeb52330ffc84265e301d9d2806846f` | CANONICAL |
| E-RR2-BUILD-BASE | AC1 | `verification/RELEASE-REPACK-2/build-base.log` | `fd6f819ca` | `85b3ed3d353b76e5e9ac8965828280903e64e59d3e911428f632f56aa147ae1f` | CANONICAL |
| E-RR2-BUILD-MODELS | AC1 | `verification/RELEASE-REPACK-2/build-models.log` | `fd6f819ca` | `c3cd89f40c641748cb86d8ef480c056881ed67d72dec29ca61453fb5d03c7fc0` | CANONICAL |
| E-RR2-DOTNET | AC5 | `verification/RELEASE-REPACK-2/dotnet-all.log` | `fd6f819ca` | `dd95c4dde87d3a4633145c73e1edba8599471da894dd39bc7ac5e00e43450f3f` | CANONICAL |
| E-RR2-PYTEST | AC5 | `verification/RELEASE-REPACK-2/pytest.log` | `fd6f819ca` | `ef8bfdead6aab3061eca72a5339667298bc6fd1ebdf69673b3ee48024801cb7f` | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-2 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-2 | `sidecar-base/`、`sidecar-models/`、`out/`（base/models zip+解压目录）、`ac3-repro/`、`data-roots/` | 证据已复制到 `verification/RELEASE-REPACK-2/`；`out/` 为本 Task 发布件保留；关闭时按裁决保留/清理 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS

- AC1：REPACK-1 base d499bd7…/models 9fcb9e87… → 新 base  91a201d… / models c5531930…（均 399,492B；bundle 195,375,520 / 868,862,035B）；torch-free 858 modules、0 shadowing ICU。
- AC2 同构建 8 页全链（identity 绑定，真实 wire）：run **terminal=completed 86.43s**；step_runs translate/segment/mask_refine/inpaint/**render 各 22/22** completed；**0 条 PROVIDER_NOT_CONFIGURED**；页 4–8 completed(0)。每步耗时：detect 4.40 / ocr 5.58 / color 5.25 / term 1.35 / translate 1.16 / segment 8.54 / mask 15.99 / inpaint 29.76 / render 13.85s。
- AC3 并发：同构建 wire 并发 GetTaskProjection **658 次@100ms** → stuck_running=0、regionless=0、PNC=0；epro_scheduler.py PASS。
- AC4：base zip 102,981,645B / models 724,989,976B；install×2/卸载×2 幂等、license 一致、console=0、exit 0、sidecar 随包；VERSION.json.sidecar_build 两包实测正确；**UPGRADE.md 已补「构建识别」**（含 identity experimental 声明/覆盖升级），packaging README §2.1 同步。
- AC5：DSH 复跑 test.ps1 **182/182**（首跑 1 例 coreclient 偶发，复跑全绿）；pytest 3F/2772P/9S（0 新增确定性失败）；check.ps1 PASS；15 条 pin；Handoff。
- 遗留：identity 为 EXPERIMENTAL 占位（非真实翻译能力，UPGRADE 已声明）；旧包未动。
- 集成：090371703。
