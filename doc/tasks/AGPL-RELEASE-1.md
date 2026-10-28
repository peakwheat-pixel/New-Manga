---
id: AGPL-RELEASE-1
title: AGPL-3.0 声明落地（models 包含 Ultralytics 权重）+ 重打包验证
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-27_followups
suggested_owner: release-compliance-owner
owner: null
reviewer: dsh
depends_on: []
base_commit: d8aadc0deb9bcd696953a75ce6b65a7bab54b5e5
branch: task/AGPL-RELEASE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/AGPL-RELEASE-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/AGPL-RELEASE-1
allowed_paths:
  - doc/tasks/AGPL-RELEASE-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - NOTICE.md
  - THIRD_PARTY_LICENSES.md
  - LICENSE-AGPL-3.0.txt
  - apps/desktop-avalonia/docs/LICENSE_AUDIT.md
  - apps/desktop-avalonia/scripts/package.ps1
  - verification/AGPL-RELEASE-1/**
  - G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/**
  - G:/CODEX/New Manga.workspace/worktrees/AGPL-RELEASE-1/**
---

# AGPL-RELEASE-1：AGPL-3.0 声明落地（models 包含 Ultralytics 权重）

## 来源与目标

- 登记来源：[AD002-FOLLOWUPS-1](AD002-FOLLOWUPS-1.md) 遗留 #7「AGPL 声明落地（yolo11s-seg=AGPL-3.0；NOTICE 已预留，发行页需同步）」。
- 2026-10-28 DSH 复核发现的事实缺口（HEAD `d8aadc0de`）：
  - RELEASE-REPACK-5 的 **models 包含权重**（`app/core-sidecar/models/…`）：`detector/yolo11s-seg.onnx`（40,824,255 B，sha256 `944e8114…18d`，Ultralytics YOLO11s-seg = **AGPL-3.0**）、`detector/rtdetr-v2-fixed.onnx`、`ocr/manga-ocr-onnx/{encoder,decoder}_model.onnx`。
  - 但包内 `LICENSE_AUDIT.md`（源自 `apps/desktop-avalonia/docs/LICENSE_AUDIT.md`）写着「AGPL 结论：仓库当前依赖清单未包含 AGPL 运行时组件」「**模型权重不随包**」——对 models 变体**与事实矛盾**。
  - 仓库根 `NOTICE.md` 只有条件句「若发行包集成了 AGPL-3.0 组件…则该发行包整体按 AGPL-3.0 分发」，未对已发布的 models 包作出明确声明；`THIRD_PARTY_LICENSES.md` 仍列 yolo11s-seg 为「若进主安装包 → 整体须 AGPL-3.0 声明」的待决状态。
  - 随包只有 GPL-3.0 全文（`LICENSE`），**没有 AGPL-3.0 全文**；AGPL 要求随分发提供许可证副本。
- 目标：models 发行包明确按 **AGPL-3.0** 声明并随包携带 AGPL-3.0 全文；base 包（不含权重）保持 GPL-3.0 声明；重打包 base + models 使声明真正落地，包内文本与仓库根逐字节一致且 hash 可核。

## Acceptance Criteria

- [ ] **AC1 权重与许可事实表**：列出 models 包内全部随包权重（路径/字节/sha256）与逐项许可证结论；`yolo11s-seg` 的 AGPL-3.0 结论须有一手来源记录（Ultralytics 官方许可页或发行包内 LICENSE 文本，记录 URL/版本/抓取日期或本地路径）；RT-DETR / MangaOCR 权重保留原核实状态并注明「不作为本卡阻断」。证据：`verification/AGPL-RELEASE-1/weights-licenses.json` + REPORT 表。
- [ ] **AC2 声明修正**：`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`apps/desktop-avalonia/docs/LICENSE_AUDIT.md` 三处修正——明确「**models 发行包含 Ultralytics YOLO11s-seg（AGPL-3.0），该发行包整体按 AGPL-3.0 分发；base 发行包不含模型权重，按 GPL-3.0-or-later 分发**」；删除/改写「模型权重不随包」等与事实矛盾的表述；`LICENSE_AUDIT.md` 按 variant 给出两套正确结论。证据：三文件 diff + 包内副本 hash。
- [ ] **AC3 AGPL 全文随包**：新增仓库根 `LICENSE-AGPL-3.0.txt`（GNU AGPL-3.0 官方全文，记录来源 URL 与 sha256）；`package.ps1` 将其加入随包复制与逐字节校验（与 LICENSE/NOTICE/THIRD_PARTY 同一机制），models 与 base 两变体均随包（base 含 AGPL 文本不改变其 GPL 声明，仅说明可选组件许可）。证据：AGPL 文本 sha256、package.ps1 diff、包内文件 hash。
- [ ] **AC4 重打包验证**：重打 base + models 两包（REPACK-6 口径，输出到 `task-envs/AGPL-RELEASE-1/out/`），验证：包内 `NOTICE.md`/`THIRD_PARTY_LICENSES.md`/`LICENSE_AUDIT.md`/`LICENSE-AGPL-3.0.txt` 与仓库根逐字节一致（base 与 models 各 4 项 SHA-256）；`package-manifest.json`/`VERSION.json` 记录 variant 与许可声明；包体大小与 REPACK-5 相当（无异常膨胀/缺失）；记录 base/models zip 字节数与 sha256。若重打包因环境阻塞，必须给出可复现命令与失败原始输出并标 `BLOCKED`，不得伪造。证据：`out/`、`package-check.json`、publish 日志。
- [ ] **AC5 回归与门禁**：`extract-command-surface.py --check` PASS（66 命令）；`apps/desktop-avalonia/scripts/test.ps1` 全绿（零产品代码改动时可用当前基线 249/249 说明 + 至少一次隔离 evidence 复跑）；`check.ps1 -TaskPath` PASS；64-hex sha256 evidence pin；Handoff。证据：logs/summary/pin 表。

## 允许修改范围

`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、新增 `LICENSE-AGPL-3.0.txt`、`apps/desktop-avalonia/docs/LICENSE_AUDIT.md`、`apps/desktop-avalonia/scripts/package.ps1`（仅新增复制与校验，不改既有打包逻辑）、本卡、STATUS/PLAN/LEDGER、`verification/AGPL-RELEASE-1/**`、自己的 Handoff、worktree 与 task-env。

## 禁止范围

不改产品源码/Core/旧壳、不改冻结契约、不改 `LICENSE`（GPL-3.0 全文原样保留）、不删除他人证据、不 push、不 gc/prune、不覆盖发布包原件（重打包写自己的 task-env）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 枚举 models 包权重 + 许可来源核对 | REPACK-5 models 包（只读） | NOT_RUN | planned |
| AC2/AC3 | 三文件修正 + 新增 AGPL 文本 + package.ps1 校验 | 仓库 | NOT_RUN | planned |
| AC4 | `apps/desktop-avalonia/scripts/package.ps1 -WithModels` 与不带 `-WithModels` 各一次 | sidecar（REPACK-5 out 的 `app/core-sidecar` 或等价构建） | NOT_RUN | planned |
| AC5 | `extract-command-surface.py --check`、`scripts/test.ps1`、`check.ps1 -TaskPath` | 仓库 | NOT_RUN | planned |

## 依赖、风险与阻塞

- 硬依赖：无（RELEASE-REPACK-5 已产出包，可只读为输入）。
- 风险：①重打包耗时（base ~100MB / models ~725MB zip）；②`package.ps1` 的 `-SidecarDir` 需指向含 models 的完整 sidecar（可用 REPACK-5 out 的 `app/core-sidecar`）；③AGPL 全文获取需一次网络抓取（GNU 官方）；不可得时用 Ultralytics 包内 LICENSE 文本替代并在证据中记录。
- 与 REGION-WORKBENCH-1 无文件面重叠（本卡限许可/打包文件，不含 `src/**`）。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/AGPL-RELEASE-1 | PRESERVE_REFERENCED | 原路径 | branch `task/AGPL-RELEASE-1` @ `d8aadc0de` | 交付后按 Worktree Safety Inventory 复核 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1 | PRESERVE_REFERENCED | 原路径 | 待交付时登记 | 重打包输出只写此处 |
| package-input | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-5/out | PRESERVE_REFERENCED（只读） | 原路径 | REPACK-5 package-summary | 只读作为 sidecar/基线，不覆盖 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：交付时更新 STATUS/PLAN/LEDGER。
