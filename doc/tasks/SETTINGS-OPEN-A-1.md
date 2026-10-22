---
id: SETTINGS-OPEN-A-1
title: 设置分区开放批次 A：OCR / 翻译参数+上下文 / 图片修复 / 排版样式
kind: implementation
governance_version: 2
status: done
approval: user_ruling_20261022_open_all_settings_partitions
suggested_owner: dsh
owner: dsh
reviewer: reviewer-settings-a
depends_on: [P15, P15-C1]
base_commit: 1fa2c3c58413b6bce972bd20fb044438d538d3d6
branch: main
worktree: null
integration_commit: 6a303a9d2c66f6ffbfee2aec6ebde359312a6b33
delivery_head: 6a303a9d2c66f6ffbfee2aec6ebde359312a6b33
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/SETTINGS-OPEN-A-1
allowed_paths:
  - doc/design/SETTINGS_SECTION_SCHEMAS.md
  - doc/tasks/SETTINGS-OPEN-A-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - doc/handoffs/SETTINGS-OPEN-A-1-*.md
  - doc/contracts/M2-C1_TYPED_IPC_CONTRACT.md
  - doc/contracts/P15_SETTINGS_IPC_CONTRACT.md
  - verification/SETTINGS-OPEN-A-1/**
  - apps/desktop/frontend/src/settings/**
  - src/bootstrap/core_service.py
  - src/bootstrap/settings_commands.py
  - src/bootstrap/settings_sections.py
  - src/application/settings/**
  - src/application/rendering/service.py
  - src/infrastructure/providers/handlers.py
  - src/infrastructure/sqlite/pipeline.py
  - src/bootstrap/core_assembly.py
  - tests/core/**
  - tests/application/**
  - tests/pipeline/**
  - tests/rendering/**
---

# SETTINGS-OPEN-A-1：设置分区开放批次 A

## 来源与目标

用户 2026-10-22 裁决：设置页全部 9 个禁用分区开放（当前仅 Provider / 网络代理 / 翻译 SFX 可用）。设计依据：[SETTINGS 分区 Schema 设计](../design/SETTINGS_SECTION_SCHEMAS.md) 批次 A。

交付一个可观察结果：在真实应用中，设置页 **OCR、翻译（参数/上下文）、图片修复、排版样式** 四个分区可编辑并保存；保存的设置对之后启动的 PipelineRun 生效；非法值被 Core 拒绝且不落库。

## Acceptance Criteria

- [x] **AC1 Core 写入校验**：`settings.update_section` 对 `ocr` / `translate` / `inpaint` / `typeset` 四节按白名单校验（键集与值域见设计 §3.1–§3.4）；未知键、非法枚举、越界数值返回 `INVALID_REQUEST`，且不写入任何值。未知 section 保持既有透传（兼容）。返修 r2 追加：`typeset` 跨字段约束（`auto_font_size=false` 时 `manual_font_size` 必填）与 `text_align` 收窄为 `left|center`。
- [x] **AC2 排版默认样式接入**：`RenderService.style_defaults` 从持久化 `typeset` 节派生（缺省 `None` 时行为不变）；Pipeline `render` 步与手动整页重渲染（`handle_rerender_page`）两条路径都使用新默认值，Region 已持久化样式仍按 D03 §11.4 覆盖默认值。字体选择不在本批白名单（设计 §3.4 注），`font_family` 保持代码默认。**r1 Review 发现 B1（合并优先级）→ r2 已修复：`_merge_defaults` 改用 RAW domain `TextStyle` 判断持久化，`tests/rendering/test_typeset_defaults_merge.py` 旧实现 3 failed / 修复后 4 passed。**
- [x] **AC3 前端分区开放**：`SETTINGS_CATEGORIES` 中 ocr/inpaint/typeset 改为 open，翻译分类内的"翻译参数 / 上下文策略"由 disabled 占位替换为可编辑面板；四个面板具备保存、错误展示、"对之后的任务生效"说明；无 mock 值，显示持久化值或明确"未设置"。r2 移除 `fill_color` 假控件、收窄 `text_align`、加跨字段校验、`saveSection` 收窄为 union。
- [x] **AC4 测试**：pytest 覆盖四节合法/非法/未知键/默认投影；Vitest 覆盖四个面板与 SettingsPage 分类可点；全部通过且不弱化既有测试。r2 追加 AC2 合并语义回归（`tests/rendering`）。最终：pytest 832 passed（core+pipeline+rendering）、vitest 367 passed、tsc exit 0。
- [x] **AC5 证据与交付**：固定 commit `6a303a9`（base `1fa2c3c5`；集成目标）；evidence_dir 记录测试原始输出与关键截图（含逐分区保存与重启复查）；Handoff；独立 Review r1=`changes_requested` → r2=`approved`（`review-r2.md`）；未跑项标 NOT_RUN。

## 允许修改范围

- 上列 `allowed_paths`；共享接口仅限设置白名单与 `style_defaults` 装配，不改变既有冻结语义（Provider/Network/凭据/SFX 面不动）。
- 本 Task、Handoff、`verification/SETTINGS-OPEN-A-1/**`。

## 禁止范围

- 不改 Schema/migration、不新增依赖、不改 Provider/Network/凭据 wire 语义、不引入设置内的 Secret/任意路径。
- 不开放批次 B/C 分区（模型/GPU、任务/并发、缓存、回收站、备份、Plugin），不发明无消费点的键。
- 不删用户源文件、不 push/merge/rebase。

## 测试要求

| 场景/AC | 计划命令 | 前提 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `python -m pytest tests/core -k settings -q` | 本地 Python 环境 | PASS（r2：248 passed） | core-report.md |
| AC2 | `python -m pytest tests/core tests/pipeline tests/rendering -q` | 同上 | PASS（r2：832 passed；B1 回归旧实现 3 failed / 修复后 4 passed） | core-report.md + core-r2-b1-old-impl-failure.txt |
| AC3/AC4 | `npm --prefix apps/desktop/frontend test`（仓库跟踪 npm 通道；pnpm 需环境产物，不作为主命令） | node_modules 已装 | PASS（r2：37 files / 367 tests；tsc exit 0） | ui-report.md + raw logs |
| 烟测（逐分区） | dev preview：inpaint/OCR/typeset 各保存一次 + 重启复查 | 构建可用 | PASS（保存后 SQLite 落库；重启后各面板回显持久化值；DB 见 gui-smoke.md） | gui-smoke.md + screenshots/01..10 |
| 独立 Review r1 | 只读审查 `87ae85a` + 独立跑测试 | — | **changes_requested**（B1/B2 blocker；M1–M5） | review-r1.md |
| 独立 Review r2 | 只读审查 `6a303a9` + 独立跑测试 | — | **approved**（无 blocker/major 残留；3 项非代码收口已处理） | review-r2.md |

## 依赖、风险与阻塞

- depends_on P15/P15-C1（already done）：设置 wire 与 P15 前端基线。
- 风险一：`style_defaults` 若只读启动时快照，保存后不生效——实现为可调用 provider。
- 风险二：前端分类 open 后，若有测试断言"未开放"需同步更新而非删除（保留翻译上下文占位外的其他禁用断言）。
- 阻塞：无。

## 交付与运行记录

- 2026-10-22：dsh 释放并登记；实现由 dsh Lead 组织（Core 与前端分属两个独立 writer），独立 Review 由非实现者 `reviewer-settings-a` 执行。
- 2026-10-22：r1 实现 commit `87ae85a`；独立 Review r1 `changes_requested`（B1/B2 blocker + M1–M5），报告 `verification/SETTINGS-OPEN-A-1/review-r1.md`。
- 2026-10-22：r2 返修 commit `6a303a9`（B1 合并语义重写、B2 移除 fill_color、M1 跨字段、M2 值域收窄、M3 契约增量注记、M4 base 更正、m1/m2/m3/m5/m6 + 治理指针）；独立 Review r2 `approved`（`review-r2.md`）。最终测试：pytest 832 passed、vitest 367 passed、tsc exit 0；GUI 逐分区保存 + 重启复查 PASS。
- Handoff：[doc/handoffs/SETTINGS-OPEN-A-1-87ae85a.md](../handoffs/SETTINGS-OPEN-A-1-87ae85a.md)（r1 实现；r2 记录见 §风险与遗留）。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| EV-A-IMPL | AC1/AC2/AC3/AC4/AC5 | 仓库 commit（实现+测试） | `6a303a9d2c66f6ffbfee2aec6ebde359312a6b33` | 见 git | CANONICAL |
| EV-A-REVIEW-R1 | AC5 | `verification/SETTINGS-OPEN-A-1/review-r1.md` | `6a303a9` | 见 git | CANONICAL |
| EV-A-REVIEW-R2 | AC5 | `verification/SETTINGS-OPEN-A-1/review-r2.md` | `6a303a9`（将在证据提交中固定） | 见 git | CANONICAL |
| EV-A-REPORTS | AC1–AC4 | `verification/SETTINGS-OPEN-A-1/core-report.md`、`ui-report.md`、`gui-smoke.md`、`*.txt` | `6a303a9` | 见 git | CANONICAL |
| EV-A-SCREENS | AC3/AC5 | `verification/SETTINGS-OPEN-A-1/screenshots/01..10` | `6a303a9` | 见 git | CANONICAL |
| EV-A-B1-OLD | AC2 | `verification/SETTINGS-OPEN-A-1/core-r2-b1-old-impl-failure.txt` | `6a303a9` | 见 git | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference check |
|---|---|---|---|---|---|
| NOT_APPLICABLE | — | — | — | — | 本 Task 不产生 worktree/artifact；dev-preview 隔离数据根仅本机验证用，不在仓库内 |

## Closeout Record

- Closeout date / Codex：2026-10-22 / dsh（Coordinator，epoch 10；用户直接授权）。
- canonical_evidence_status：complete；resource_closeout_status：complete。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项：无（m6 的"翻译参数 GUI 保存"未单独做，已说明由 pytest + 同一 client 覆盖；typeset 渲染效果由渲染级回归覆盖）。
- 当前指针清理：STATUS / REBASELINE_PLAN / TASK_LEDGER 已更新；Handoff 已提交；旧 checkpoint 不恢复。
