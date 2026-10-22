---
id: SETTINGS-OPEN-A-1
title: 设置分区开放批次 A：OCR / 翻译参数+上下文 / 图片修复 / 排版样式
kind: implementation
governance_version: 2
status: in_progress
approval: user_ruling_20261022_open_all_settings_partitions
suggested_owner: dsh
owner: dsh
reviewer: reviewer-settings-a
depends_on: [P15, P15-C1]
base_commit: 1fa2c3c58413b6bce972bd20fb044438d538d3d6
branch: main
worktree: null
integration_commit: null
delivery_head: 87ae85a678880bff840ac77b53f2700e586ad95c
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/SETTINGS-OPEN-A-1
allowed_paths:
  - doc/design/SETTINGS_SECTION_SCHEMAS.md
  - doc/tasks/SETTINGS-OPEN-A-1.md
  - doc/STATUS.md
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
- [ ] **AC2 排版默认样式接入（返修中）**：`RenderService.style_defaults` 从持久化 `typeset` 节派生（缺省 `None` 时行为不变）；Pipeline `render` 步与手动整页重渲染（`handle_rerender_page`）两条路径都使用新默认值，Region 已持久化样式仍按 D03 §11.4 覆盖默认值。字体选择不在本批白名单（设计 §3.4 注），`font_family` 保持代码默认。**r1 Review 发现 B1：`_merge_defaults` 优先级使 7/11 键不生效，返修 r2 中修复并要求 tests/rendering 级回归。**
- [x] **AC3 前端分区开放**：`SETTINGS_CATEGORIES` 中 ocr/inpaint/typeset 改为 open，翻译分类内的"翻译参数 / 上下文策略"由 disabled 占位替换为可编辑面板；四个面板具备保存、错误展示、"对之后的任务生效"说明；无 mock 值，显示持久化值或明确"未设置"。返修 r2 移除 `fill_color` 假控件、收窄 `text_align`、加跨字段校验、`saveSection` 收窄为 union。
- [x] **AC4 测试**：pytest 覆盖四节合法/非法/未知键/默认投影；Vitest 覆盖四个面板与 SettingsPage 分类可点；全部通过且不弱化既有测试。返修 r2 追加 AC2 合并语义回归（`tests/rendering`）。
- [ ] **AC5 证据与交付**：固定 commit；evidence_dir 记录测试原始输出与关键截图；Handoff；独立 Review 由非实现者执行后记录结论；未跑项标 NOT_RUN。**r1 Review=`changes_requested`（B1/B2/M1/M2/M3/M4 等），返修 r2 后需复审。**

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
| AC1 | `python -m pytest tests/core -k settings -q` | 本地 Python 环境 | PASS（r1：239 passed；r2 待重跑） | core-report.md |
| AC2 | `python -m pytest tests/core tests/pipeline tests/rendering -q` | 同上 | r1 819 passed；**B1 回归 r2 待补** | core-report.md + review-r1.md |
| AC3/AC4 | `npm --prefix apps/desktop/frontend test`（仓库跟踪 npm 通道；pnpm 需环境产物，不作为主命令） | node_modules 已装 | PASS（r1：37 files/364 tests） | ui-report.md + raw logs |
| 烟测 | 启动 dev preview，保存并重启复查（inpaint.background_complexity=medium） | 构建可用 | PASS（保存后 SQLite 落库；重启后回显） | gui-smoke.md + screenshots |
| 独立 Review r1 | 只读审查 `87ae85a` + 独立跑测试 | — | **changes_requested**（B1/B2 blocker；M1–M5） | review-r1.md |
| 独立 Review r2 | 返修后复审 | — | 待执行 | 待填 |

## 依赖、风险与阻塞

- depends_on P15/P15-C1（already done）：设置 wire 与 P15 前端基线。
- 风险一：`style_defaults` 若只读启动时快照，保存后不生效——实现为可调用 provider。
- 风险二：前端分类 open 后，若有测试断言"未开放"需同步更新而非删除（保留翻译上下文占位外的其他禁用断言）。
- 阻塞：无。

## 交付与运行记录

- 2026-10-22：dsh 释放并登记；实现由 dsh Lead 组织（Core 与前端分属不同 writer），独立 Review 另行指派。
- Handoff / Review / 实际测试：待填。

## Canonical Evidence

| evidence_id | AC/Gate | path | commit | sha256 | class |
|---|---|---|---|---|---|
| pending | pending | pending | pending | pending | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference check |
|---|---|---|---|---|---|
| NOT_APPLICABLE | — | — | — | — | 本 Task 不产生 worktree/artifact |

## Closeout Record

- Closeout date / Codex：待关闭。
- canonical_evidence_status：pending；resource_closeout_status：pending。
- 删除、迁移、归档数量/字节数：0。
- 未关闭项：独立 Review 与烟测待完成。
- 当前指针清理：STATUS 已登记本 Task。
