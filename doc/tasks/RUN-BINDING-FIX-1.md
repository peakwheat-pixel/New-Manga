---
id: RUN-BINDING-FIX-1
title: Host 侧 StartRun 携带 provider bindings（零 Core 改动）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-27_run_fix_a_b
suggested_owner: saber-ui-spec
owner: saber-ui-spec
reviewer: dsh
depends_on: []
base_commit: 146377373
branch: task/RUN-BINDING-FIX-1
worktree: G:/CODEX/New Manga.workspace/worktrees/RUN-BINDING-FIX-1
integration_commit: 692347b58
delivery_head: 33ddc2804c0ba018b7c0d83df85226e7cc851a09
canonical_evidence_status: complete
resource_closeout_status: pending
evidence_dir: verification/RUN-BINDING-FIX-1
allowed_paths:
  - doc/tasks/RUN-BINDING-FIX-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/RUN-BINDING-FIX-1/**
  - G:/CODEX/New Manga.workspace/task-envs/RUN-BINDING-FIX-1/**
  - G:/CODEX/New Manga.workspace/worktrees/RUN-BINDING-FIX-1/**
---

# RUN-BINDING-FIX-1：Host 侧 StartRun 携带 provider bindings（零 Core 改动）

> 交付状态：**ready-for-integration**（实现 `33ddc2804` + 证据 + Handoff 已完成；待 DSH 复核/集成；Owner 不自审）。
> 说明：卡面 base 为 `b993e68bb`；按 DSH 指令分支从当前 HEAD **`146377373`** 创建，避免过旧 base。

## 背景

RUN-OCR-DIAG-1 实证：OCR `PROVIDER_NOT_CONFIGURED` 根因是 Core `pipeline_defaults.provider_bindings_json='{}'`，`_chain()` 取不到 `ocr` 绑定。**只加 `overrides.provider_bindings={"ocr":"manga-ocr"}` → OCR 步骤 completed**（13/13 region 有文本），零 Core 改动。

## Acceptance Criteria

- [x] **AC1 接线**：Host 侧 StartRun 调用携带 `overrides.provider_bindings`（默认 `{"ocr":"manga-ocr"}`，允许配置/关闭覆盖；不覆盖用户显式传入的 overrides）。→ **MET**：`HostCommandDispatcher.library_start_run` 经 `WriteStartRunOverrides` 恒注入默认；`NEWMANGA_RUN_PROVIDER_BINDINGS` 可配置/关闭；显式 `overrides.provider_bindings` 原样优先、其余 overrides 保留；非对象边界 `INVALID_ARGUMENTS`（0 Core 帧）。证据：`commands/run-binding-wire.json`、`commands/run-binding-overrides.json`。
- [x] **AC2 同构建复验**：在 models 包构建 `2b36bfeb…4ec519b` 上整书 8 页复跑，断言 `ocr` step 不再出现 `PROVIDER_NOT_CONFIGURED`；允许仍停在 color/translate 且错误类型可判定。→ **MET**：8 targets；`provider_binding_snapshot_json={"ocr":"manga-ocr"}`；`step_runs` **ocr 3/3 completed、0 条 `PROVIDER_NOT_CONFIGURED`**；链停在 **color**（3 条 `PROVIDER_FAILED`）；run 终态 `completed_with_failures`（**未写成整链通**）。同构建对照（关闭注入）ocr 3/3 `PROVIDER_NOT_CONFIGURED`。证据：`commands/run-binding-models.json`、`commands/run-binding-baseline.json`、`run-binding-db-check.json`。
- [x] **AC3 语义测试**：有/无 override 两态单测；参数边界与覆盖优先级；unknown provider 返回 typed 错误。→ **MET**：4 个策略单测 + 5 个 frozen-sidecar 契约/边界测试 + 2 个 models 真跑；unknown provider (`no-such-provider`) → typed `PROVIDER_UNAVAILABLE`。证据：`test/results-coreclient.trx`、`commands/run-binding-unknown-provider.json`、`run-binding-db-check.json`。
- [x] **AC4 回归**：`scripts/test.ps1` 全绿；vitest 60/567；pytest 相对基线（3F/2746P/9S）无新增失败。→ **MET**：test.ps1 **172/172, 0 skipped**（coreclient 55 / host 42 / app 75）；vitest **60 files / 567 tests**；pytest **3F/2746P/9S**。证据：`test/summary.json`、`test/dotnet-test-Debug.log`、`test/vitest.log`、`test/pytest.log`。
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；64-hex pin；Handoff + Record Decision（默认绑定/覆盖策略）。→ **MET**：`pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/RUN-BINDING-FIX-1.md` PASS；13 条 Canonical Evidence pin；`doc/handoffs/RUN-BINDING-FIX-1-handoff.md`。

## Record Decision（摘要，完整版在 Handoff / REPORT）

| 项 | 决定 |
|---|---|
| 默认绑定 | `{"ocr":"manga-ocr"}`（冻结 Core 唯一注册 OCR provider） |
| 注入位置 | Host `HostCommandDispatcher` 的 `library_start_run`（零 Core 改动）；策略类 `RunBindingDefaults` |
| 覆盖优先级 | 用户显式 `overrides.provider_bindings` 对象完全优先（不合并/不覆盖）；`null` 视为未提供；其余 overrides 保留 |
| 配置/关闭 | `NEWMANGA_RUN_PROVIDER_BINDINGS`：JSON 对象替换；空/`off`/`none`/`disabled`/`0` 关闭 |
| 非法配置 | 非对象/非字符串 id/非法 JSON → `InvalidOperationException`（明显失败，不静默降级） |
| 边界 | `overrides`、`overrides.provider_bindings` 非对象 → `INVALID_ARGUMENTS`，Before-any-Core-frame |
| 不改变范围 | color `PROVIDER_FAILED`、detect 0 候选 `INVALID_INPUT` 属 B/CORE-PIPELINE-FIX-1；本卡不声称整链通 |

## 实现摘要（全部 `apps/desktop-avalonia/**`）

- `Commands/RunBindingDefaults.cs`（新）——默认/自定义/关闭/非法配置解析。
- `Commands/HostCommandDispatcher.cs`——`library_start_run` 改 `WriteStartRunOverrides`：注入、优先级、其余 overrides 保留、参数边界。
- `tests/.../Commands/RunBindingFixTests.cs`（新，11 项）——策略单测、frozen-sidecar 契约/边界、models 构建 A/B 真跑与 unknown provider typed。
- `scripts/test.ps1`——models 包存在时导出 `NEWMANGA_MODELS_SIDECAR_DIR`（缺失则真跑测试自动 Skip 并说明原因）。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| RB-TEST-SUMMARY | AC4 | verification/RUN-BINDING-FIX-1/test/summary.json | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | caee504a60f09237f96205378e999786770e07c3c66007c9d08f85a4e617d415 | CANONICAL |
| RB-TEST-LOG | AC4 | verification/RUN-BINDING-FIX-1/test/dotnet-test-Debug.log | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | 950e4ff5635699fa4fe50b1a57817462e333fd257faf5404dbda56bf887d705d | CANONICAL |
| RB-VITEST | AC4 | verification/RUN-BINDING-FIX-1/test/vitest.log | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | 2e85c79dea329b2ac87459f483d7dea984909eab394922070d33eb520b11afd4 | CANONICAL |
| RB-PYTEST | AC4 | verification/RUN-BINDING-FIX-1/test/pytest.log | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | c6f8f8883463f6fc0dd7b2763760065ddccf0e4f0ee292b19a5e06ffe1e62517 | CANONICAL |
| RB-TEST-PS1-LOG | AC4 | verification/RUN-BINDING-FIX-1/test/test.ps1-final.log | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | d866ec847cdf68d2ea1801e9c49ffdd6dffec07c1fc45762355863b13be23b39 | CANONICAL |
| RB-WIRE | AC1/AC3 | verification/RUN-BINDING-FIX-1/commands/run-binding-wire.json | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | dc992f082370628283d58f11ee10515184755e8c9049390bb181ee2a44422ab4 | CANONICAL |
| RB-OVERRIDES | AC1/AC3 | verification/RUN-BINDING-FIX-1/commands/run-binding-overrides.json | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | 0946cce96c6f8bb636246e4f1e097d72c20c90e8a08096c506d631412e85c710 | CANONICAL |
| RB-MODELS-RUN | AC2 | verification/RUN-BINDING-FIX-1/commands/run-binding-models.json | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | 36730edca9b1314ea55b287f8ae126f0c0a74b5b2e0e6e61ef0168de7ddbc6aa | CANONICAL |
| RB-BASELINE-RUN | AC2/AC3 | verification/RUN-BINDING-FIX-1/commands/run-binding-baseline.json | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | 330a4a150b893deb7768a44347582c9e35751d6d361f06d25a6c943ed18e3828 | CANONICAL |
| RB-UNKNOWN-PROVIDER | AC3 | verification/RUN-BINDING-FIX-1/commands/run-binding-unknown-provider.json | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | c9b5becc8e6db089274cd49046ed9956afe392d8930423f4ceaea7891d71b1ae | CANONICAL |
| RB-DB-CHECK | AC2/AC3 | verification/RUN-BINDING-FIX-1/run-binding-db-check.json | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | 9748af8b645a74bc9b4b1804d94095f97a0e7e5a6b9fdf56ae0d4872794563cf | CANONICAL |
| RB-REPORT | AC5 | verification/RUN-BINDING-FIX-1/REPORT.md | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | 4e6cb90f81042500160308b27141b948315ac5f10f8154ee9d7e124b9fc22b22 | CANONICAL |
| RB-DB-CHECK-SOURCE | AC2/AC3 | verification/RUN-BINDING-FIX-1/tools/check_run_binding.py | 33ddc2804c0ba018b7c0d83df85226e7cc851a09 | 772a19c44e19e67afab65b0aab55f924f1e948e81647065a90e393f15331117f | SOURCE_PIN |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/RUN-BINDING-FIX-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RUN-BINDING-FIX-1 | `evidence/`（commands/test/logs；含 Host 路径 run 的 library.db 副本，约 6.5 MB）；不含构建产物 | 2026-10-27 收口时存在；`run-binding-db-check.json` 的 `db_sha256` 即来自这些副本；未移动/未删除；关闭时由 DSH 复核 |
| models-package sidecar | G:/CODEX/New Manga.workspace/task-envs/FINAL-VALIDATION-1/out/NewManga-0.1.0-win-x64-models/app/core-sidecar | READ_ONLY_REFERENCED | — | core_service.exe sha256 `2b36bfebcf09ea118537a0bc77a6c7c9a47c8845d7a853bc60d56ed004ec519b` | 已引用（只读运行，未复制/未修改）；sha256 与 RUN-OCR-DIAG-1 记录一致 |
| BOOK-FIXTURE | G:/CODEX/New Manga.workspace/task-envs/BOOK-FIXTURE-1/isolated-data | READ_ONLY_REFERENCED | — | book `14340ddad0ed472fbe687fe12340c5d8`，8 页 | 测试复制到私有临时根运行，原件未修改 |

## Closeout Record

- Closeout date / DSH：待关闭时填写（owner 交付 `33ddc2804`，待 DSH 集成验证与独立 Review）。
- canonical_evidence_status：`complete`（13 条 pin：12 CANONICAL + 1 SOURCE_PIN，指向 delivery_head）。
- resource_closeout_status：`pending`（task-env 保留引用含 run 数据库副本；models 包与 fixture 只读引用）。
- 删除、迁移、归档数量/字节数：0（本任务未删除任何文件；真实 run 只在临时数据根创建并运行）。
- 未关闭项及保留原因：color `PROVIDER_FAILED`、detect 0 候选 `INVALID_INPUT` 属 CORE-PIPELINE-FIX-1（B）范围；Export/Retry 等其它 run 入口未注入 bindings；若需 UI 开关应为后续 UI Task；需独立 Review。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
## Review（DSH 集成复核，2026-10-27）— PASS

- 合并冲突仅 scripts/test.ps1（S4 fixture 种子 vs models sidecar 环境）→ 保留双方两块，无冲突标记；DSH 复跑 	est.ps1 **173/173**。
- 接线：HostCommandDispatcher.library_start_run → WriteStartRunOverrides/RunBindingDefaults；默认注入 {"ocr":"manga-ocr"}；用户显式优先；NEWMANGA_RUN_PROVIDER_BINDINGS 可配置/关闭；非对象 → INVALID_ARGUMENTS 且 0 Core 帧。
- 同构建 8 页 A/B：注入后 ocr **3/3 completed、0 条 PROVIDER_NOT_CONFIGURED**；关闭注入 → 3/3 PROVIDER_NOT_CONFIGURED；链停 color（属 CORE 修复、冻结 exe 未重打包）；**未写成整链通**。
- 集成：692347b58。
