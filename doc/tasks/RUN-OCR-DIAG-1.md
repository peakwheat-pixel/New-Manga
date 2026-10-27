---
id: RUN-OCR-DIAG-1
title: Run 链 OCR PROVIDER_NOT_CONFIGURED / detect INVALID_INPUT 诊断（只诊断）
kind: research
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_run_ocr_diag
suggested_owner: baseline-scout
owner: null
reviewer: dsh
depends_on: []
base_commit: 9f58b4c1d
branch: task/RUN-OCR-DIAG-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RUN-OCR-DIAG-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RUN-OCR-DIAG-1
allowed_paths:
  - doc/tasks/RUN-OCR-DIAG-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/RUN-OCR-DIAG-1/**
  - G:/CODEX/New Manga.workspace/task-envs/RUN-OCR-DIAG-1/**
  - G:/CODEX/New Manga.workspace/worktrees/RUN-OCR-DIAG-1/**
---

# RUN-OCR-DIAG-1：Run 链 OCR/detect 失败诊断（只诊断，不改 Core）

## 背景

RUN-EXPORT-E2E-1 用 models 包跑 Run 链，观察：
- 页 1–3：detect 真实完成（ONNX），**OCR 步骤 typed `PROVIDER_NOT_CONFIGURED`**
- 页 4–8：detect `INVALID_INPUT`
- run 3.1s（热）/6.5s（冷）终态 `completed_with_failures`，未到 translate/render

证据：`verification/RUN-EXPORT-E2E-1/probe-models.json`、`REPORT.md`。

## Acceptance Criteria

- [x] **AC1 最小复现**：用冻结 sidecar + models 包对**单页**复现 OCR `PROVIDER_NOT_CONFIGURED`，给出请求帧/配置/环境（EP、模型路径、provider 配置）。
- [x] **AC2 根因**：判定是 (a) 模型包缺 OCR 模型/配置 (b) EP/provider 配置错误 (c) Core 侧翻译/OCR provider 未注册 (d) 输入不符合预期；每类给出可判定证据。
- [x] **AC3 detect INVALID_INPUT**：页 4–8 的 `INVALID_INPUT` 根因（图尺寸/格式/固定 640 约束/空页），给出输入特征与判定。
- [x] **AC4 建议**：产出修复建议列表（按最小改动排序）+ 预计影响面（哪些 Task 会变绿），不改 Core 语义、不改产品源码。
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff。

## 允许修改范围

`verification/RUN-OCR-DIAG-1/**`、本卡、STATUS/PLAN/LEDGER、workspace。**只读**产品源码/Core/models。

## 禁止范围

不改 Python Core 语义、不改产品源码/协议/Host 契约/旧壳、不 push、不 gc/prune、不伪造复现；跑不通就如实记录卡点。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| EV-AC1-PROBE | AC1 | verification/RUN-OCR-DIAG-1/probe-models-book.json |  | d8edc2086e921b4e423f31d606851b19e410f3ebc202ec0eca66610a3e1dc4d5 | CANONICAL |
| EV-AC1-BIND | AC1/AC2 | verification/RUN-OCR-DIAG-1/probe-binding-override.json |  | 7c40badcdd789c003297bb5b7fe6302d6f56048240e1745169fd5ae8a974da57 | CANONICAL |
| EV-AC2-DIAG | AC2/AC3 | verification/RUN-OCR-DIAG-1/diagnosis.json |  | d43bf8cf7073909a1e9d332b404c8989488dfdaeda7f50cf65236a0ff8d10f4d | CANONICAL |
| EV-AC3-DETECT | AC3 | verification/RUN-OCR-DIAG-1/detect-per-page.json |  | 5a09ec4c1e60b7da729a45d539a2a20fc6ee3243da94fc4ff97ac5232107be45 | CANONICAL |
| EV-AC3-FEATURES | AC3 | verification/RUN-OCR-DIAG-1/page-features.json |  | 26659b0dc013778934ca5c22cbb9bbf34954c8657f86f8476592c783d562473c | CANONICAL |
| EV-AC1-LOG1 | AC1 | verification/RUN-OCR-DIAG-1/core-models-book.log |  | bf00ec945670059dfc54e8f613be5f6b7eb7ea30fb3825bbaac7a6174df3c3a6 | SOURCE_PIN |
| EV-AC2-LOG2 | AC2 | verification/RUN-OCR-DIAG-1/core-binding-override.log |  | bf8d6ada3b83757abd59e282aa0105d454f42e5d0def050b6b2e598404a67d0d | SOURCE_PIN |
| EV-AC4-REPORT | AC4/AC5 | verification/RUN-OCR-DIAG-1/REPORT.md |  | 2675e30ca1bac63c2501fa49a257001901a342137351755980432560b1e799f3 | CANONICAL |
| EV-RES-MANIFEST | AC5 | verification/RUN-OCR-DIAG-1/resource-manifest.json |  | 1aa5a9b2dc8be1ade7befc1b3a2b15b287b80d07a061f511f065dd27ec6e4172 | SOURCE_PIN |
| EV-T-RUNDIAG | AC1/AC4 | verification/RUN-OCR-DIAG-1/tools/run_diag.py |  | 00285d4f63b0537477752b6bcb0303940cf23ce4611f88e39c2a086cb4c061c4 | CANONICAL |
| EV-T-DETECT | AC3 | verification/RUN-OCR-DIAG-1/tools/detect_probe.py |  | be4960135f3723a1615b928540f649bdd8aca4474c4480b0399e82e7e568c017 | CANONICAL |
| EV-T-FEATURES | AC3 | verification/RUN-OCR-DIAG-1/tools/page_features.py |  | db4e9d43317b5f8cbb90cd9d904b1d52ca6ab60f4dc2c744c2d2344c06309ab7 | CANONICAL |
| EV-T-SUMMARY | AC1 | verification/RUN-OCR-DIAG-1/tools/summarize.py |  | 983d5b005f921ca5137d21ee32068a818a05ab27c26d789f0e0df20efbc337e1 | CANONICAL |

说明：只诊断任务，未提交代码；证据用 64-hex SHA-256 pin（commit 列留空）。

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RUN-OCR-DIAG-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RUN-OCR-DIAG-1 | verification/RUN-OCR-DIAG-1/resource-manifest.json | 已核：诊断全程只读 models 包 sidecar 与 models/（未复制、未修改）；数据根为 BOOK-FIXTURE 私有副本，原件与真实 %APPDATA% 零触碰；仓库内无二进制/权重，只有 JSON/MD 证据 |

## 交付与运行记录

- Handoff：`verification/RUN-OCR-DIAG-1/REPORT.md` + `diagnosis.json`（机器可读）+ 4 个可重跑脚本（`tools/`）。
- 诊断对象：models 包冻结 sidecar `core_service.exe` `sha256=2b36bfeb…4ec519b`（与 AC11 副本 `e0a1eff8…` 不同构建，结论只对 models 包成立）。
- **AC1 复现**：整书 8 页与单页均稳定复现；`step_runs.error_detail` 给出机制级证据。
- **AC2 OCR 根因**：`PROVIDER_NOT_CONFIGURED` = **Core step provider binding 未配置**
  （`pipeline_defaults.provider_bindings_json='{}'`；`handlers.py:1068-1074 _chain()` 取不到 `ocr` 键）。
  排除：①模型缺失/损坏（权重 sha256 与 provider pin 逐字节一致）；②EP 配置（detect 已用 DML 跑通，错误早于 EP）；
  ③输入不符（错误早于输入，绑定后同一输入成功）。因果实证：只加 `overrides.provider_bindings={"ocr":"manga-ocr"}`
  → **OCR completed**（13/13 region 有 text；provider=manga-ocr/local-manga-ocr-onnx/cpu），随后撞上第 2 个缺陷
  `color` 步骤 `_StubStyleAnalyzer` 缺 `analyze`（`core_service.py:654/715` ↔ `application/translation/color/service.py:30`）。
- **AC3 detect INVALID_INPUT**：页 4–8 检测器**正常返回 0 候选**（8 页 `core.detect` = 13/6/7/0/0/0/0/0，无错误码），
  页 4 目视确认为无文字全彩插画；Core 把"0 候选"映射成 `INVALID_INPUT`（`handlers.py:296`）→ 应改为 completed(0 region)/skipped。
- **AC4 建议 5 条**（按最小改动）：①Host 侧 StartRun 带 `overrides.provider_bindings`（零 Core 改动，已实证）；
  ②全新安装种默认本地绑定（需契约裁决）；③补 `color` analyzer（现成 PillowSourceStyleAnalyzer 可用）；
  ④空检测语义改为完成/跳过（需裁决）；⑤Export 闭环（host-control grant + translated 产物）。
- 未改：Python Core 语义、产品源码、协议、Host 契约、旧壳；未 push/gc/prune；未伪造复现。
- NOT_RUN：translate/inpaint/render 全链（需远端翻译 provider，且 color 先失败）；其它 step 缺绑定的根因（机制同源未逐一实证）；
  OCR 文本质量；页 5–8 逐页目视（仅统计特征 + 0 候选推断）。
- 仓库状态提示：诊断期间 main 被 reset 到 `9f58b4c1d`，本卡在释放提交 `98423eec0` 中、工作树已缺失，已从该提交恢复为工作树文件（未提交、卡面内容未改），AC/证据/交付段为本任务追加；同时按释放提交的同一意图恢复了 `doc/REBASELINE_PLAN.md` 的 DAG 行与 READY 节点、并用 `tools/governance/task_ledger.py --write` 重建 `doc/TASK_LEDGER.md`（脚本生成，未改任何 Task 状态）。`doc/STATUS.md` 未动（当前指向他人正在执行的 GRANT-ISSUER-1）。

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
