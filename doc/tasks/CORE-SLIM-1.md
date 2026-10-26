---
id: CORE-SLIM-1
title: Core 瘦身：移除 PySide6 + entry exe 去重 + 体积预算（≤700MB 运行时/≤2GB 包）
kind: implementation
governance_version: 3
status: done
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: antigravity
owner: null
reviewer: dsh
depends_on: [CORE-TILE-EMIT-1]
base_commit: 7a9d474d8
branch: task/CORE-SLIM-1
worktree: G:/CODEX/New Manga.workspace/worktrees/CORE-SLIM-1
integration_commit: c5aade851
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
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
  - doc/handoffs/**
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

- [x] **AC1 <<MET>>
- [x] **AC2 <<MET>>
- [x] **AC3 体积达标：Core 运行时（不含模型）**≤700MB**；允许在**冻结闭包**中 excludes 未使用的传递依赖（cv2/scipy/h5py/shapely 等），**前提是**解码/OCR/检测/修复/导入/PDF 全能力 smoke 全绿且可复跑；若仍 >700MB 则 AC3 记 `PARTIAL`（附实测值与缺口原因），不得改预算口径或伪造。产出 `verification/CORE-SLIM-1/size-report.md`（before/after 表 + 每项 exclude 的能力证据）。→ **PARTIAL**：实测 **970.1 MiB**（改前 1067.3，−97.2）；未做 excludes——build venv 实测 `cv2/scipy/h5py/shapely` 是 ML 栈**导入期硬依赖**（排除即删能力），且强排后仅 ~788 MiB 仍不达标；缺口 270.1 MiB 由能力必需的 torch/cv2/scipy/onnxruntime 构成（`size-report.md` §4）。 <<PARTIAL: 970.1 MiB（目标 ≤700MB）；缺口 270.1 MiB 全为能力必需 ML 栈（torch 365/cv2 112/scipy 70/onnx 63 MiB），cv2/scipy 为导入期硬依赖，强排仅 ~788 MiB 且删能力，故不做 excludes>>
- [x] **AC4 <<MET>>
- [x] **AC5 <<MET>>

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
| E-AC1-DECODE | AC1 | `verification/CORE-SLIM-1/ac1/COMPARISON.md` | `95c2c28bb` | `3cbc559e62d050328d83652d7a022f7ed8ca3e35853ddf6b5995858f9297b8e8` | CANONICAL |
| E-AC2-BUNDLE | AC2 | `verification/CORE-SLIM-1/ac2/bundle-after.json` | `95c2c28bb` | `0d2305407b7a18a9a228abcaa7d6cc61a6325f8cd04fdb6434f8606c6e0a77fe` | CANONICAL |
| E-AC2-SMOKE | AC2/AC3 能力 | `verification/CORE-SLIM-1/ac2/capability-smoke.json` | `95c2c28bb` | `16ad92a89cbee2d816e192406f5a5ae844321b78faf6e5b18d850fb881102c88` | CANONICAL |
| E-AC3-SIZE | AC3 | `verification/CORE-SLIM-1/size-report.md` | `95c2c28bb` | `bac34850c543f2b7bf0421bce7957e802bc78a49311ece4435581e301674bb15` | CANONICAL |
| E-AC4-PYTEST | AC4 | `verification/CORE-SLIM-1/ac4/pytest-after.log` | `95c2c28bb` | `3581abf13134a4065d31deab1f2ae27576cb46ce7981f9a9e9cb34f290294719` | CANONICAL |
| E-AC4-DOTNET | AC4 | `verification/CORE-SLIM-1/ac4/scripts-test-after.log` | `95c2c28bb` | `5d988bc8842fb0412475100b105c8f857a6047741204a6459c45a253a0f05569` | CANONICAL |

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
## Review（DSH 集成复核，2026-10-27）— PASS（AC3 接受 PARTIAL）

- 单命令：scripts/test.ps1 → **102/102 passed / 0 skipped**（对重建无标签 sidecar 副本）。
- pytest：**3F/2710P/9S**，失败集合 = 基线 3 项、**0 新增**、+19 用例；基线更新为 3F/2710P/9S。
- AC1（口径=打包闭包零 Qt）：闭包 Qt 命中 **0**；Pillow 解码矩阵 11/12（差异=AVIF 能力增益）、像素 16/16、PDF 2/2 逐像素相等；legacy QML 与旧测试原位冻结未动（符合 S5-C 口径）。
- AC2：5 entry exe **199.6 → 1.9 MiB**，
oarchive=True 共享 8767 个 .pyc，entry 名/argv/stdio 协议不变（能力 smoke 7/7）。
- **AC3 裁决**：接受 PARTIAL——Core 运行时 **1067.3 → 970.1 MiB（−97.2）**；未做 excludes 的理由成立（cv2/scipy 为检测链导入期硬依赖，排除=删能力；强排仅 ~788 MiB）。**不改 700MB 口径、不伪造达成**；缺口归 ML 栈，交由 CORE-SLIM-2（依赖 INFER-BASELINE-EP-1 的 ONNX 化结论）处置。
- 遗留：build venv 仍装 PySide6（pin 已删，干净重建自然消失）；主检出 release 侧车仍是旧 Qt 版，发布前需按新 spec 重建（S5-D 打包脚本应内置重建步骤）。
- 集成：c5aade851；未 push。
