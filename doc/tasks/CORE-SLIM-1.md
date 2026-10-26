---
id: CORE-SLIM-1
title: Core 瘦身：移除 PySide6 + entry exe 去重 + 体积预算（≤700MB 运行时/≤2GB 包）
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [CORE-TILE-EMIT-1]
base_commit: 7a9d474d8
branch: task/CORE-SLIM-1
worktree: G:/CODEX/New Manga.workspace/worktrees/CORE-SLIM-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/CORE-SLIM-1
allowed_paths:
  - doc/tasks/CORE-SLIM-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - src/**
  - tests/**
  - requirements.txt
  - apps/desktop/src-tauri/tauri.conf.json
  - verification/CORE-SLIM-1/**
  - G:/CODEX/New Manga.workspace/task-envs/CORE-SLIM-1/**
  - G:/CODEX/New Manga.workspace/worktrees/CORE-SLIM-1/**
---

# CORE-SLIM-1：Core 瘦身

## 目标（AD-002 §3.5 预算规则）

1. **移除 Core 内 PySide6**：`infrastructure/rendering`/`importing` 中 `QtImageDecoder` 改用 Pillow/pypdfium2，覆盖 PDF/TIFF/WebP/多帧 GIF 回归；依赖清单移除 PySide6/shiboken6。
2. **entry exe 去重**：当前 3 个 ~68MB entry exe（core_service/acceptance_bridge/sfx_detect_probe）存在运行时重复；改为共享 `_internal` 或合并入口，目标 Core 运行时 **≤700MB（不含模型）**。
3. **预算口径**：主安装包（含基础模型）≤2GB；CUDA 可选包独立且 ≤8GB。
4. **回归**：pytest 相对基线无新增失败；`apps/desktop-avalonia/scripts/test.ps1` 全绿；中文路径/figure 渲染样例不变。

## Acceptance Criteria

- [ ] **AC1 PySide6 移除**：源码无 PySide6 import；`requirements.txt` 移除；PDF/TIFF/WebP/动画 GIF 解码回归通过（含多帧）。
- [ ] **AC2 exe 去重**：打包脚本产出的 entry 数量与体积优化（记录 before/after 体积表）；sidecar 启动与协议不变。
- [ ] **AC3 体积达标**：Core 运行时（不含模型）≤700MB；产出体积报告 `verification/CORE-SLIM-1/size-report.md`。
- [ ] **AC4 回归**：pytest 无新增失败（基线 3F/2691P/9S）；`scripts/test.ps1` 全绿；渲染/导入关键样例像素级不变（或差异有解释）。
- [ ] **AC5 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff + Record Decision（解码器替代方案、打包策略）。

## 允许修改范围

`src/**`、`tests/**`、`requirements.txt`、旧壳打包配置（仅删除 PySide6 相关，不重构旧壳）、本卡、STATUS/PLAN/LEDGER、`verification/CORE-SLIM-1/**`、workspace。

## 禁止范围

不改协议/命令语义、不改 Host 契约、不 push、不 gc/prune、不删除任何既有解码能力（必须等价替代）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | PDF/TIFF/WebP/GIF 解码回归 | Pillow/pypdfium2 | NOT_RUN | 待填 |
| AC2 | 打包前后体积表 + 启停 smoke | 无标签副本 | NOT_RUN | 待填 |
| AC3/AC4 | 体积报告 + pytest + scripts/test.ps1 | 全量 | NOT_RUN | 待填 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/CORE-SLIM-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/CORE-SLIM-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
