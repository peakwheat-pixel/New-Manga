---
id: SETTINGS-OPEN-B-1
title: 设置分区开放批次 B-1：模型/GPU + 任务/并发
kind: implementation
governance_version: 2
status: in_review
approval: user_ruling_20261022_open_all_settings_partitions
suggested_owner: dsh
owner: dsh
reviewer: reviewer-settings-a
depends_on: [SETTINGS-OPEN-A-1]
base_commit: da3b781d8971dcc36bd7bfd1165fa1a2f4519ea5
branch: main
worktree: null
integration_commit: b521ad27149f59c251f0e281b56d329e72a7ba78
delivery_head: b521ad27149f59c251f0e281b56d329e72a7ba78
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/SETTINGS-OPEN-B-1
allowed_paths:
  - doc/design/SETTINGS_SECTION_SCHEMAS.md
  - doc/tasks/SETTINGS-OPEN-B-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
  - doc/contracts/P15_SETTINGS_IPC_CONTRACT.md
  - doc/handoffs/SETTINGS-OPEN-B-1-*.md
  - verification/SETTINGS-OPEN-B-1/**
  - apps/desktop/frontend/src/settings/**
  - src/bootstrap/settings_sections.py
  - src/infrastructure/devices/manager.py
  - src/infrastructure/providers/runtime.py
  - src/infrastructure/providers/handlers.py
  - tests/core/**
  - tests/providers/**
---

# SETTINGS-OPEN-B-1：模型/GPU + 任务/并发

## 来源与目标

用户 2026-10-22 裁决开放全部设置分区；批次 A（OCR/翻译/修复/排版）已 done（`6a303a9`）。本 Task 实现批次 B-1：设计 [SETTINGS 分区 Schema](../design/SETTINGS_SECTION_SCHEMAS.md) §4.1–§4.2。

交付结果：设置页 **模型/GPU** 与 **任务/并发** 两个分类可编辑并保存；`model_gpu.device_preference` / `allow_cpu_fallback` 对之后启动的 Run 生效；`tasks.retry_max_attempts` / `retry_backoff_seconds` 对之后启动的 Run 生效；并发数不提供假控件，UI 显示"任务串行执行"只读说明。

## Acceptance Criteria

- [x] **AC1 Core 写入校验**：`settings.update_section` 对 `model_gpu`（`device_preference ∈ auto|cpu|gpu`、`allow_cpu_fallback: bool`）与 `tasks`（`retry_max_attempts` int 1–3、`retry_backoff_seconds` float 0.1–30）白名单校验；未知键/非法值 `INVALID_REQUEST` 且不落库（60 个新测试 + 既有 pass-through 列表根因适配）。
- [x] **AC2 模型/GPU 消费点**：Run 执行时的 `heavy_runner` 路径读取 Run 快照的 `model_gpu` 节；`auto` 保持历史行为（不调用 `plan`，monkeypatch 断言）；`cpu`/`gpu` 显式偏好经 `DeviceManager.plan` 校验，GPU 不可用且 `allow_cpu_fallback=false`（或 Provider 不支持回退）时抛 typed `DeviceUnavailable`；回退语义与 D06 §82 一致（用户开关与 Provider `supports_cpu_fallback` 相与）。
- [x] **AC3 任务/并发消费点**：Run 执行时按 Run 快照的 `tasks` 节构造 `RetryPolicy`（`max_attempts`、`backoff_seconds`），未设置时返回装配期 `deps.retry_policy` **同一对象**（逐位等价）；`retry_codes`/`retry_after_provider` 保留。
- [x] **AC4 前端两面板**：`model_gpu` / `task_concurrency` 分类 open，渲染真实面板（下拉/开关/数字输入 + 保存 + 错误投影 + "对之后启动的任务生效"）；`task_concurrency` 面板显示串行执行只读说明；其余 4 个分区（cache_revision/recycle_bin/backup_restore/plugins）保持禁用断言（39 files / 387 tests）。
- [x] **AC5 测试与证据**：pytest（校验 + 两个消费点）与 vitest（两面板/分类矩阵）全绿；tsc 无错误；GUI 烟测（两分区保存 + 重启复查）；独立 Review 由非实现者执行；未跑项标 NOT_RUN。

## 允许修改范围

上列 allowed_paths。不动 Provider/Network/凭据/SFX 语义、不改 Schema/migration、不加依赖。

## 禁止范围

- 不开放并发数、GPU 并发策略、模型下载/路径管理、设备状态 wire（另立 Task）。
- 不删用户源文件、不 push/merge/rebase。

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `python -m pytest tests/core -k settings -q` | 本地 Python | PASS（60 个新校验测试 + 既有 settings 测试全绿） | core-report.md §5.2 |
| AC2/AC3 | `python -m pytest tests/core tests/providers -q --ignore=tests/providers/test_detection_manga_real.py` | 同上 | PASS（clean commit `b521ad27`：**1253 passed / 3 skipped**，exit 0；在 `git archive` 快照重录、排除 B-2 WIP） | core-pytest-clean-acceptance-raw.txt |
| AC4 | `npm --prefix apps/desktop/frontend test` | node_modules | PASS（39 files / 387 tests；tsc exit 0） | ui-report.md + raw logs |
| 烟测 | dev preview 两分区保存 + 重启复查 | 构建可用 | NOT_RUN（需集成阶段真实 Tauri + Core） | — |
| 全量回归 | `python -m pytest tests -q` | 同上 | clean：**2585 passed / 3 failed / 9 skipped**（3 个既有失败：2 环境 + 1 旧 PySide6；与 B-1 无关） | core-pytest-clean-full-raw.txt |

## 依赖、风险与阻塞

- 依赖 SETTINGS-OPEN-A-1（done）：白名单/面板模式与 `SettingsClient` 泛化 API。
- 风险一：把 `auto` 偏好也接入 `plan` 会改变历史行为 → 仅显式偏好时校验，`auto` 直通。
- 风险二：`tasks` 重试策略改为 per-run 后，既有 `DEFAULT_RETRY_POLICY` 行为必须保持；测试覆盖未设置时等值。
- 风险三：`model_gpu` 在空库/无 Provider 时无法端到端验证 GPU 分支 → typed 单测 + NOT_RUN 说明。

## 交付与运行记录

- 2026-10-22：dsh 释放并登记；Core 由 `core-settings-b1`、前端由 `ui-settings-b1` 两个独立 writer 并行实现；Lead 独立复核 diff、重跑测试并组织集成。
- 2026-10-22：交付 commit `7d19164`（dsh 集成）；独立 Review 由 `reviewer-settings-a`（非实现者）执行，结论落 `verification/SETTINGS-OPEN-B-1/review-b1.md`（r1 `changes_requested`：B1 descriptor 来源 + m1；返修后复审）。B-2 批次在同一工作区并行时未进入本 Task 的交付 commit（`7d19164` 树干净可用 `git archive` 复核）；B-2 独立 Task 记录。
- Lead 独立验证：`pytest tests/core tests/providers --ignore=tests/providers/test_detection_manga_real.py -q` → 1212 passed / 3 skipped；`npm --prefix apps/desktop/frontend test` → 39 files / 387 tests；`tsc --noEmit` exit 0。
- 任务文本笔误：验收命令中的 `tests/infrastructure` 不存在；设备测试在 `tests/providers/test_devices.py`（已由 core-report §4.1 记录）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|EV-B1-CORE-PYTEST-B1-TARGETED-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-pytest-b1-targeted-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|7ece5a5af1dc57a180ec3d53935d88af53a6ab7be52c41089a9d59d101e8daaf|CANONICAL|
|EV-B1-CORE-PYTEST-BASELINE-BEFORE-CHANGE-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-pytest-baseline-before-change-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|53b5bd584f6259eed3c6f00477427214b2bb9870c6de7e12ce0ceb32f9214e7f|CANONICAL|
|EV-B1-CORE-PYTEST-CLEAN-ACCEPTANCE-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-pytest-clean-acceptance-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|c23133874a051a04379e69d1f4ea4ca55a42539e1bbb88b0965c169d43bf2820|CANONICAL|
|EV-B1-CORE-PYTEST-CLEAN-FULL-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-pytest-clean-full-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|1abd43d7a2a4b80c0dc0f16a41d21ad35fdf77692fab64caa9dd68c47ea8a794|CANONICAL|
|EV-B1-CORE-PYTEST-CORE-PROVIDERS-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-pytest-core-providers-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|586670063529bb51546f7fb629d5b321c1f9f83579a9375b1b3fc0448822d6c9|CANONICAL|
|EV-B1-CORE-PYTEST-FULL-SUITE-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-pytest-full-suite-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|888168799a0a95e24b633480156933c587d9028eb20216b871eb76ab4908789e|CANONICAL|
|EV-B1-CORE-PYTEST-GREEN-NO-ENV-MODULE-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-pytest-green-no-env-module-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|0c1610e9068c4e3b8cb76dd66da635df1e9dfe4d71334a8b44d45b467537fc38|CANONICAL|
|EV-B1-CORE-PYTEST-R1-ACCEPTANCE-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-pytest-r1-acceptance-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|bf62dac9b848932088f90eab1da73d4fa9c9a74ab2d46dedfad1b44ba1c7668d|CANONICAL|
|EV-B1-CORE-PYTEST-R1-CORE-PROVIDERS-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-pytest-r1-core-providers-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|7ce53322ff901b675184259cae803de2dd9cf87c12b28b3ba0209712db031d14|CANONICAL|
|EV-B1-CORE-PYTEST-R1-FULL-SUITE-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-pytest-r1-full-suite-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|dc8fc5f6c994556ba90b883dc6429bb8bcfb235674b182bf6b788887ea2125c6|CANONICAL|
|EV-B1-CORE-PYTEST-R1-TARGETED-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-pytest-r1-targeted-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|926facbf05db501e5a3cba775dab023a48b340dc709303e8e29ee762a4867bd5|CANONICAL|
|EV-B1-CORE-PYTEST-REQUIRED-COMMAND-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-pytest-required-command-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|d83c0ca6fe0aa432ab199f6f30dbff612282036f35f5737981d0616017b49ee1|CANONICAL|
|EV-B1-CORE-REPORT|AC1-AC5|verification/SETTINGS-OPEN-B-1/core-report.md|b521ad27149f59c251f0e281b56d329e72a7ba78|59eaec12f7fdf2afa8f04ce5187f8356452c1be7f834368154bce3da3a7cadfe|CANONICAL|
|EV-B1-FRONTEND-NPM-TEST-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/frontend-npm-test-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|3926d8ee9acbe02dc8dd5ea32dcee3ab00234744cbb9f631a057e476605dcf1b|CANONICAL|
|EV-B1-FRONTEND-TARGETED-TEST-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/frontend-targeted-test-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|64f300ea328c3baf40b4cb66fa039edaeb9e2d222e41e7e103ee96c7d084913b|CANONICAL|
|EV-B1-FRONTEND-TSC-RAW|AC1-AC5|verification/SETTINGS-OPEN-B-1/frontend-tsc-raw.txt|b521ad27149f59c251f0e281b56d329e72a7ba78|17cba47483e4bf23854c951231fee6eabbf067af4795ddc738375692c233ed12|CANONICAL|
|EV-B1-REVIEW-B1|AC1-AC5|verification/SETTINGS-OPEN-B-1/review-b1.md|b521ad27149f59c251f0e281b56d329e72a7ba78|34e7654414be2f55ab2e2e887ea4294c604452843bb8e132b2651e443bdd5be4|CANONICAL|
|EV-B1-REVIEW-B2|AC1-AC5|verification/SETTINGS-OPEN-B-1/review-b2.md|b521ad27149f59c251f0e281b56d329e72a7ba78|adb260d6b1ea84e2c8de93f0690e64df7b348b9417c08cda9fbfb277a562f5cd|CANONICAL|
|EV-B1-UI-REPORT|AC1-AC5|verification/SETTINGS-OPEN-B-1/ui-report.md|b521ad27149f59c251f0e281b56d329e72a7ba78|518644f33ae4c642a479f60a38785a2d22d31d36bd4a9953a687996306ff6752|CANONICAL|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference check |
|---|---|---|---|---|---|
| NOT_APPLICABLE | — | NOT_APPLICABLE | — | — | 本 Task 不产生持久资源 |

## Closeout Record

- Closeout：待关闭。
- canonical_evidence_status：pending；resource_closeout_status：pending。
- 删除/迁移/归档：0。
- 当前指针清理：STATUS/REBASELINE/LEDGER 已登记本 Task。
