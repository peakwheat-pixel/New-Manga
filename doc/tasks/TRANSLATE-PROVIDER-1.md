---
id: TRANSLATE-PROVIDER-1
title: 翻译 provider 最小可用接线
kind: implementation
governance_version: 3
status: in_review
approval: user_authorized_2026-10-27_goal_auto_except_recommended
suggested_owner: route-research
owner: route-research
reviewer: dsh
depends_on: []
base_commit: 97de0fa99
branch: task/TRANSLATE-PROVIDER-1
worktree: G:/CODEX/New Manga.workspace/worktrees/TRANSLATE-PROVIDER-1
integration_commit: null
delivery_head: f96f245f4b5f435275767a6b00d7721debd64ea3
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/TRANSLATE-PROVIDER-1
allowed_paths:
  - doc/tasks/TRANSLATE-PROVIDER-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - verification/TRANSLATE-PROVIDER-1/**
  - G:/CODEX/New Manga.workspace/task-envs/TRANSLATE-PROVIDER-1/**
  - G:/CODEX/New Manga.workspace/worktrees/TRANSLATE-PROVIDER-1/**
---

# TRANSLATE-PROVIDER-1：翻译 provider 最小可用接线（让 Run 过 translate）

## 背景

CORE-PIPELINE-FIX-1 后 Run 链停在 `translate`：typed `PROVIDER_NOT_CONFIGURED`（无 provider binding）。需要最小可用翻译 provider 让流水线可继续到 render（不追求翻译质量，但必须真实产出、可观测、可替换）。

分支基于 `ae7fe3334`（卡面允许 HEAD），已实测 8 页 Run 到达 render；identity 为 **EXPERIMENTAL 占位**，不是成品翻译（Record Decision / Handoff）。Handoff：`doc/handoffs/TRANSLATE-PROVIDER-1-handoff.md`。

## Acceptance Criteria

- [x] **AC1 清单**：列出 Core 现有 translate provider（`openai-compatible-translation`、`sakura-local`）与注册/解析方式，判定**均不能开箱离线**（requirements=endpoint/credential 或需本机 Sakura 服务，状态 `not_configured`）；新增最小 `identity-translation`（`identity-experimental`，零 requirements）并注册，状态 `ready`。证据：`verification/TRANSLATE-PROVIDER-1/provider-inventory.json`。<<MET>>
- [x] **AC2 绑定与装配**：StartRun override（`overrides.provider_bindings`）与持久化默认绑定（`PipelineDefaultsService.save_provider_binding` → `pipeline_defaults` → Run 冻结快照）两条路径均实测生效；无绑定/未知/禁用/能力不匹配仍为既有 typed provider 错误，未放宽输入校验。证据：`run-summary.json` 两变体 + `evidence/inproc-*.json`；单测 11 例。<<MET>>
- [x] **AC3 同构建复验**：源码直跑（生产 assembly 同一路径，真实 models）8 页 Run：`identity` 与 `default-binding` 两变体 translate **3/3 页 completed（22/22 Region units）**、页 4–8 保持 completed(0 region)，**全链路推进到 render（22/22 completed）**，run `completed`。RELEASE-REPACK-1 新 exe（sha `9fcb9e87…`，构建早于本 provider）实测：页 1–3 detect/ocr/color/term completed、translate typed 缺口，页 4–8 completed——同构建“含 identity”全链路待下次重打包（工具已就绪）。证据：`evidence/new-sidecar-run.json`、`sidecar-provenance.json`。<<MET>>
- [x] **AC4 单测/回归**：provider/绑定单测 **11 例全绿**；pytest 本树 **4F/2763P/9S** vs 同树纯净 base `ae7fe3334` **4F/2752P/9S**（失败集合逐条相同，**0 新增失败**；含环境性 `test_plugin_sandbox_job_kills_grandchildren`，已在 base 复现）；`scripts/test.ps1` **177/177 passed**；vitest **60 文件/567 用例**。证据：`pytest.log`、`pytest-baseline-base.log`、`dotnet/summary.json`、`vitest.log`。<<MET>>
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；14 条 64-hex sha256 pin；Handoff + Record Decision（provider 语义/质量声明/替换路径，见 REPORT §6）。<<MET>>

## Record Decision（摘要；完整见 `verification/TRANSLATE-PROVIDER-1/REPORT.md` §6）

1. **语义**：`identity-translation` 严格输入=输出（OCR 源文本原样写为 machine translation），**不做翻译**、不联网、零依赖。
2. **质量声明**：**EXPERIMENTAL 占位**，仅用于推进/验证流水线；不得作为产品翻译质量宣发。落库/导出可识别：`provider_id=identity-translation`、`provider_type=identity-experimental`、`model=identity-passthrough`、`options.experimental=identity-placeholder`。
3. **只显式生效**：无条件注册、绝不隐式选择；无绑定时仍 typed `PROVIDER_NOT_CONFIGURED`。
4. **替换路径零代码**：绑定改为 `openai-compatible-translation` / `sakura-local` / 用户 profile 即可（Run 冻结快照）。
5. **未改协议/Host 契约/旧壳/packaging**：identity 进入 exe 由 RELEASE-REPACK-1 下次重打包完成。

## 实际测试记录

| 套件 | 命令 | 结果 |
|---|---|---|
| provider/绑定单测 | `python -m pytest tests/providers/test_translation_identity.py tests/providers/test_handlers_pipeline.py tests/core/test_pipeline_defaults_service.py -q` | **全部通过**（新增 11 例） |
| 全量 Python | `python -m pytest -q` | **4F/2763P/9S**（同树纯净 base 4F/2752P/9S：失败集合相同、0 新增） |
| 全量 .NET | `apps/desktop-avalonia/scripts/test.ps1 -EvidenceDirectory <private>` | **PASS 177/177，0 skipped** |
| 前端 | `apps/desktop/frontend`：`npx vitest run` | **60 files / 567 tests passed** |
| 真实 8 页 Run | `python verification/TRANSLATE-PROVIDER-1/tools/verify_inproc.py {identity,default-binding,no-binding}` | identity/default-binding：**completed**，translate 3/3 页 → render 22/22；no-binding：typed `PROVIDER_NOT_CONFIGURED` |
| 新 exe 见证 | `python verification/TRANSLATE-PROVIDER-1/tools/run_new_sidecar_probe.py` | 8 页：5 completed / 3 failed（页 1–3 仅 translate typed 缺口） |

## 允许修改范围

`src/**`（providers/registry/装配与测试）、本卡、STATUS/PLAN/LEDGER、`verification/TRANSLATE-PROVIDER-1/**`、workspace。

## 禁止范围

不改协议/Host 契约/旧壳、不 push、不 gc/prune；不得把 machine/identity 翻译当成品宣发（必须在 Handoff 明确「experimental/占位」）；不得放宽输入校验。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| T1 | AC1 | verification/TRANSLATE-PROVIDER-1/provider-inventory.json | - | be352cfce840707f6cd36920107b1dc26f1616b75adbd658492bf0277e40f841 | CANONICAL |
| T2 | AC3 | verification/TRANSLATE-PROVIDER-1/run-summary.json | - | bb84de05dd4816fd3cf6045f32c90f693dd18ac6cd86f3169343bccd6bc3cf7b | CANONICAL |
| T3 | AC3 | verification/TRANSLATE-PROVIDER-1/sidecar-provenance.json | - | 144437d02632e39f46b1e8de0ecc82bceddff268123479b72b922b9174e65952 | CANONICAL |
| T4 | AC2/AC3 | verification/TRANSLATE-PROVIDER-1/evidence/inproc-identity.json | - | a090af70c136541b0567d659bae50c9c3023fb0b0dc9275c46b0f470946ef455 | CANONICAL |
| T5 | AC2/AC3 | verification/TRANSLATE-PROVIDER-1/evidence/inproc-default-binding.json | - | a822167601624b17b172fafeda6ff2616e4f56c11cbc48b4a7ca010dbbd0c2c7 | CANONICAL |
| T6 | AC2 | verification/TRANSLATE-PROVIDER-1/evidence/inproc-no-binding.json | - | 82c7824adfbc787f89619bc0543d9d327d93dbc82cca5e7a271ba58f7bc7a05a | CANONICAL |
| T7 | AC3 | verification/TRANSLATE-PROVIDER-1/evidence/new-sidecar-run.json | - | 16dbc6342183307b4f345f22e6f84a2792ef8e7207c913195ec13a2131b8321f | CANONICAL |
| T8 | AC3 | verification/TRANSLATE-PROVIDER-1/evidence/exe-core.stderr.log | - | cd4299f089b3a13511b8942a2a500e6a123226ef82ee58cc3e48f7bcbdfb5b5d | CANONICAL |
| T9 | AC4 | verification/TRANSLATE-PROVIDER-1/pytest.log | - | b42fc815feccb83a0870158945b47780b28d1c7f34deadc740937d70b034557f | CANONICAL |
| T10 | AC4 | verification/TRANSLATE-PROVIDER-1/pytest-baseline-base.log | - | f5977abf025c4ae9e346824f78af2053a279c57cac5a9471eca39e10b390648b | CANONICAL |
| T11 | AC4 | verification/TRANSLATE-PROVIDER-1/dotnet/summary.json | - | 19c94028f11420e29df50ea30a896a341e5d3c4a968cf00c1fd4a86f63319050 | CANONICAL |
| T12 | AC4 | verification/TRANSLATE-PROVIDER-1/dotnet/test-ps1.log | - | 9795723abbef4d3833d491244d6afcec89c80961fcf4cbd09d1cdf3ea8b565d1 | CANONICAL |
| T13 | AC4 | verification/TRANSLATE-PROVIDER-1/vitest.log | - | c2972b7edfed0d7bf83b200b9e93659a9d8e3fd30a271e0e277f77a789a300d9 | CANONICAL |
| T14 | AC1–AC5 | verification/TRANSLATE-PROVIDER-1/REPORT.md | - | fbebf5238295671602d446dec534b7b5f82ed91731aa05bfef0df7936238aba4 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/TRANSLATE-PROVIDER-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/TRANSLATE-PROVIDER-1 | 见 `evidence/*.json` 与各日志 | 交付时保留：inproc-* 运行证据、new-sidecar-run、dotnet 私有证据、日志；`baseline-worktree`（纯净 base 对照）交付后清理并记录。关闭时复核引用。 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-1 | PRESERVE_REFERENCED | 原路径 | `sidecar-models/core-sidecar/core_service.exe` sha `9fcb9e87…` | 本卡只读消费其现有构建做同构建见证，不宣称其验收；归属 RELEASE-REPACK-1。 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1 | PRESERVE_REFERENCED | 原路径 | frozen models sidecar sha `2b36bfeb…` | 仅作旧 frozen 对照与 models 权重来源（只读）。 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`complete`（14 条 sha256 pin）。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写（本卡交付后清理 `baseline-worktree` 与 inproc 数据根，见 Handoff）。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
