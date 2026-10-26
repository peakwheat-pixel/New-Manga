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
  - packaging/**
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

- [x] **AC1 PySide6 移除（口径=打包 Core 闭包零 PySide6）**：`src/` 中 4 个 Core 文件（`infrastructure/importing.py`、`bootstrap/{core_assembly,core_service,acceptance_bridge}.py`）的去 Qt 化；`requirements.txt` 移除 PySide6/shiboken6；spec 打包闭包不加载 Qt；PDF/TIFF/WebP/多帧 GIF 解码回归通过。legacy QML 源与约 45 个旧测试**原位冻结、不打包、不改**（与 S5-C 冻结口径一致），AC1 记 MET + Record Decision。→ **MET**：闭包实测 0 Qt；解码矩阵 11/12（唯一差异=AVIF 能力增益）、像素产物 16/16、PDF 2/2 逐像素相等（`verification/CORE-SLIM-1/ac1/COMPARISON.md`）。
- [x] **AC2 exe 去重**：打包脚本产出的 entry 数量与体积优化（记录 before/after 体积表）；sidecar 启动与协议不变。→ **MET**：5 个 exe 合计 199.6 → **1.9 MiB**（每 entry ~0.38 MiB）；机制=`noarchive=True` 共享 `_internal/*.pyc`（8767 个），entry 名/argv/stdio 协议未变（能力 smoke 7/7 PASS）。
- [ ] **AC3 体积达标**：Core 运行时（不含模型）**≤700MB**；允许在**冻结闭包**中 excludes 未使用的传递依赖（cv2/scipy/h5py/shapely 等），**前提是**解码/OCR/检测/修复/导入/PDF 全能力 smoke 全绿且可复跑；若仍 >700MB 则 AC3 记 `PARTIAL`（附实测值与缺口原因），不得改预算口径或伪造。产出 `verification/CORE-SLIM-1/size-report.md`（before/after 表 + 每项 exclude 的能力证据）。→ **PARTIAL**：实测 **970.1 MiB**（改前 1067.3，−97.2）；未做 excludes——build venv 实测 `cv2/scipy/h5py/shapely` 是 ML 栈**导入期硬依赖**（排除即删能力），且强排后仅 ~788 MiB 仍不达标；缺口 270.1 MiB 由能力必需的 torch/cv2/scipy/onnxruntime 构成（`size-report.md` §4）。
- [x] **AC4 回归**：pytest 无新增失败（基线 3F/2691P/9S）；`scripts/test.ps1` 全绿；渲染/导入关键样例像素级不变（或差异有解释）。→ **MET**：pytest `3F/2710P/9S`（失败集合=基线 3 项，0 新增；新增 19 个 AC1 用例）；`test.ps1` **102/102 passed, 0 skipped**；像素等价见 AC1 证据。
- [x] **AC5 门禁**：`check.ps1 -TaskPath` PASS；证据 64-hex pin；Handoff + Record Decision（解码器替代方案、打包策略）。→ **MET**：`doc/handoffs/CORE-SLIM-1-handoff.md`（含 Record Decision §5）；pin 见下。

## 允许修改范围

`src/**`、`tests/**`、`requirements.txt`、旧壳打包配置（仅删除 PySide6 相关，不重构旧壳）、本卡、STATUS/PLAN/LEDGER、`verification/CORE-SLIM-1/**`、workspace。

## 禁止范围

不改协议/命令语义、不改 Host 契约、不 push、不 gc/prune、不删除任何既有解码能力（必须等价替代）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | PDF/TIFF/WebP/GIF 解码回归 | Pillow/pypdfium2 | **PASS**：解码矩阵 11/12（AVIF=增益）、像素产物 16/16、PDF 2/2 | `verification/CORE-SLIM-1/ac1/COMPARISON.md` |
| AC2 | 打包前后体积表 + 启停 smoke | 无标签副本 | **PASS**：exe 199.6→1.9 MiB；能力 smoke 7/7 | `verification/CORE-SLIM-1/size-report.md`、`ac2/capability-smoke.json` |
| AC3/AC4 | 体积报告 + pytest + scripts/test.ps1 | 全量 | **AC3 PARTIAL**（970.1 MiB）；**AC4 PASS**（pytest 3F/2710P/9S 无新增；test.ps1 102/102） | `verification/CORE-SLIM-1/size-report.md`、`ac4/pytest-after.log`、`ac4/scripts-test-after.log` |

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

