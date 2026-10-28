---
id: AGPL-RELEASE-1
title: AGPL-3.0 声明落地（models 包含 Ultralytics 权重）+ 重打包验证
kind: implementation
governance_version: 3
status: in_review
approval: user_authorized_2026-10-27_followups
suggested_owner: release-compliance-owner
owner: region-workbench-owner
reviewer: dsh
depends_on: []
base_commit: d8aadc0deb9bcd696953a75ce6b65a7bab54b5e5
branch: task/AGPL-RELEASE-1
worktree: G:/CODEX/New Manga.workspace/worktrees/AGPL-RELEASE-1
integration_commit: null
delivery_head: 35fd83c3ab28e0f3293238bd17543c5cec2f8e91
canonical_evidence_status: complete
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

- [x] **AC1 权重与许可事实表**：列出 models 包内全部随包权重（路径/字节/sha256）与逐项许可证结论；`yolo11s-seg` 的 AGPL-3.0 结论须有一手来源记录（Ultralytics 官方许可页或发行包内 LICENSE 文本，记录 URL/版本/抓取日期或本地路径）；RT-DETR / MangaOCR 权重保留原核实状态并注明「不作为本卡阻断」。证据：`verification/AGPL-RELEASE-1/weights-licenses.json` + REPORT 表。 <<MET>>
- [x] **AC2 声明修正**：`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、`apps/desktop-avalonia/docs/LICENSE_AUDIT.md` 三处修正——明确「**models 发行包含 Ultralytics YOLO11s-seg（AGPL-3.0），该发行包整体按 AGPL-3.0 分发；base 发行包不含模型权重，按 GPL-3.0-or-later 分发**」；删除/改写「模型权重不随包」等与事实矛盾的表述；`LICENSE_AUDIT.md` 按 variant 给出两套正确结论。证据：三文件 diff + 包内副本 hash。 <<MET>>
- [x] **AC3 AGPL 全文随包**：新增仓库根 `LICENSE-AGPL-3.0.txt`（GNU AGPL-3.0 官方全文，记录来源 URL 与 sha256）；`package.ps1` 将其加入随包复制与逐字节校验（与 LICENSE/NOTICE/THIRD_PARTY 同一机制），models 与 base 两变体均随包（base 含 AGPL 文本不改变其 GPL 声明，仅说明可选组件许可）。证据：AGPL 文本 sha256、package.ps1 diff、包内文件 hash。 <<MET>>
- [x] **AC4 重打包验证**：重打 base + models 两包（REPACK-6 口径，输出到 `task-envs/AGPL-RELEASE-1/out/`），验证：包内 `NOTICE.md`/`THIRD_PARTY_LICENSES.md`/`LICENSE_AUDIT.md`/`LICENSE-AGPL-3.0.txt` 与仓库根逐字节一致（base 与 models 各 4 项 SHA-256）；`package-manifest.json`/`VERSION.json` 记录 variant 与许可声明；包体大小与 REPACK-5 相当（无异常膨胀/缺失）；记录 base/models zip 字节数与 sha256。若重打包因环境阻塞，必须给出可复现命令与失败原始输出并标 `BLOCKED`，不得伪造。证据：`out/`、`package-check.json`、publish 日志。 <<MET>>
- [x] **AC5 回归与门禁**：`extract-command-surface.py --check` PASS（66 命令）；`apps/desktop-avalonia/scripts/test.ps1` 全绿（零产品代码改动时可用当前基线 249/249 说明 + 至少一次隔离 evidence 复跑）；`check.ps1 -TaskPath` PASS；64-hex sha256 evidence pin；Handoff。证据：logs/summary/pin 表。 <<MET>>

## 允许修改范围

`NOTICE.md`、`THIRD_PARTY_LICENSES.md`、新增 `LICENSE-AGPL-3.0.txt`、`apps/desktop-avalonia/docs/LICENSE_AUDIT.md`、`apps/desktop-avalonia/scripts/package.ps1`（仅新增复制与校验，不改既有打包逻辑）、本卡、STATUS/PLAN/LEDGER、`verification/AGPL-RELEASE-1/**`、自己的 Handoff、worktree 与 task-env。

## 禁止范围

不改产品源码/Core/旧壳、不改冻结契约、不改 `LICENSE`（GPL-3.0 全文原样保留）、不删除他人证据、不 push、不 gc/prune、不覆盖发布包原件（重打包写自己的 task-env）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 枚举 models 包权重 + 许可来源核对 | REPACK-5 models 包（只读） | **PASS**：10 文件（4 权重+6 配置）字节/sha256 全量；yolo11s-seg ONNX metadata_props 一手证明 AGPL-3.0，Ultralytics 许可页/仓库 LICENSE/GNU 全文交叉核实 | `verification/AGPL-RELEASE-1/weights-licenses.json` |
| AC2/AC3 | 三文件修正 + 新增 AGPL 文本 + package.ps1 校验 | 仓库 | **PASS**：NOTICE/THIRD_PARTY/LICENSE_AUDIT 按变体修正；`LICENSE-AGPL-3.0.txt` 34,523B sha256 `0d96a4ff…`；package.ps1 4 许可文件逐字节校验 | 三文件 diff + `package-check.json` |
| AC4 | `package.ps1`（base）与 `-WithModels` 各一次 | sidecar=REPACK-5 out 的 `app/core-sidecar`（只读） | **PASS**：base zip 103,492,048B sha `722fc62b…`；models zip 725,499,708B sha `480d0632…`；包内 5 许可文件 zip 流+staging 双验逐字节一致；各 +0.11MB/+1 file | `out/`、`package-check.json`、`packages/*`、`logs/package-*.log` |
| AC5 | `extract-command-surface.py --check`、`scripts/test.ps1`、`check.ps1 -TaskPath` | 仓库 | `--check` **PASS（66）**；`test.ps1` 隔离复跑 **PASS 258/258 passed, 0 skipped**（61/60/137）；`check.ps1 -TaskPath` **PASS** | `logs/extract-command-surface.log`、`logs/test-ps1-console.log`、`test/summary.json`、`check-governance.json` |

## Record Decisions（交付记录）

1. **变体级许可结论**：models 包随包 `detector/yolo11s-seg.onnx`（Ultralytics YOLO11s-seg，AGPL-3.0）→ models 整体 **AGPL-3.0**；base 包在 sidecar 复制时排除 `models/`（`package.ps1` 既有 `/XD` 逻辑）→ **GPL-3.0-or-later**。两变体都随包 `LICENSE-AGPL-3.0.txt`（base 作可选组件许可说明，不改变其 GPL 声明），以满足 AGPL「许可证副本随分发」并避免变体间文件面分裂。
2. **AGPL 全文取证**：`https://www.gnu.org/licenses/agpl-3.0.txt` 官方文本（34,523 B，sha256 `0d96a4ff…`）；Ultralytics 仓库 LICENSE 抓取结果与之**逐字节一致**（同一 sha），说明其许可文本即 GNU AGPL-3.0 原文。AGPL 文件未加任何增补/修改。
3. **yolo11s-seg 归属用文件自证**：不依赖文件名推断——ONNX `metadata_props` 明确 `author=Ultralytics`、`license=AGPL-3.0 License (https://ultralytics.com/license)`、`version=8.4.172`、`task=segment`；另用 Ultralytics 官方许可页与仓库 LICENSE 交叉核实。
4. **package.ps1 最小改动**：只在许可文件组加第 4 个文件（复制+SHA-256 逐字节校验，缺失即 throw），并在 `VERSION.json` 增加 `license`/`license_files`/`bundled_weights_license` 元数据；既有发布流程（dotnet publish、robocopy、manifest、zip、预算 Gate）不改。base 的 AGPL 文本随包不引入变体差异风险。
5. **重打包输入复用 REPACK-5（只读）**：`-SidecarDir` 指向 `task-envs/RELEASE-REPACK-5/out/NewManga-0.1.0-win-x64-models/app/core-sidecar`，输出只写 `task-envs/AGPL-RELEASE-1/out`；未覆盖 REPACK-5 out。包体增量 +0.11MB/+1 文件（许可文件+文本增量），权重字节与 REPACK-5 完全一致（yolo11s-seg sha `944e8114…18d`）。
6. **AC5 测试口径**：本卡零产品代码改动，仍按要求做一次隔离 evidence 复跑：`test.ps1` 258/258（61/60/137）0 skipped，与当前 main 基线一致；命令面 66 命令零漂移。
7. **RT-DETR / MangaOCR 保留 [待核实]**：文件无内嵌许可元数据、上游模型卡未在本次抓取；按 AC1 记「不阻断本卡」，在 `THIRD_PARTY_LICENSES.md` §3 与 `weights-licenses.json` 显式标注，供下一次发行 Gate 补齐。

## 交付与运行记录

- Handoff：[AGPL-RELEASE-1-handoff.md](../handoffs/AGPL-RELEASE-1-handoff.md)
- Review：尚未（reviewer=`dsh`；Owner 与 Reviewer 不同）。
- 实现提交：`80fe5cde23b1ead55fd3a2b961a15124fc7b031a`（许可声明修正 + AGPL 全文 + package.ps1 校验 + 版本元数据）。
- 证据提交 / delivery_head：`35fd83c3ab28e0f3293238bd17543c5cec2f8e91`（`verification/AGPL-RELEASE-1/**`，含 REPORT/pins 引用目标）。
- Task 卡 + Handoff：紧随 delivery head 的文档提交（本卡所在提交）（紧随 delivery head 的文档提交）。
- 实际测试：见「测试要求」表与证据索引。

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
| delivery-report | 交付报告 | verification/AGPL-RELEASE-1/REPORT.md | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | c7309d2b25ba24c927b383dc4c6986f0c4ce47569c21b6eb11d5a84f5c7c7e44 | CANONICAL |
| ac5-command-surface | AC5 | verification/AGPL-RELEASE-1/logs/extract-command-surface.log | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | 564676d393ad475f6924d84dce57281e51ba6ae22d4f7984379030a8e05dfda1 | CANONICAL |
| ac4-package-base-log | AC4 | verification/AGPL-RELEASE-1/logs/package-base.log | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | fb37599292366e08c0304f51c888f054d0ef96504db8d78f5c71598308d3ca5e | CANONICAL |
| ac4-package-models-log | AC4 | verification/AGPL-RELEASE-1/logs/package-models.log | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | f7486eb9c182f1df8520f54fbd5a21d7ac0f727ab4d6dab93b4dbc5e39f6719a | CANONICAL |
| ac4-publish-base-log | AC4 | verification/AGPL-RELEASE-1/logs/publish-base.log | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | 2735630f773b8933a90e86ef72ce7c95fd3d6b23f5519687c2db9b6bf5be68e9 | CANONICAL |
| ac4-publish-models-log | AC4 | verification/AGPL-RELEASE-1/logs/publish-models.log | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | 0b82aec706da188fd9b3cd8cd584d7704260b52e2f996bd20d26c39797ce9f60 | CANONICAL |
| ac5-test-console | AC5 | verification/AGPL-RELEASE-1/logs/test-ps1-console.log | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | cccb564b402bd75ca83e56b056ab35b4215875cab9b40019989c450d788c4943 | CANONICAL |
| ac4-package-check | AC4 | verification/AGPL-RELEASE-1/package-check.json | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | 68f1323e8e0a12cc3342c19534bad972ea6e2c073a411af7ce3b4d129f9bc196 | CANONICAL |
| ac4-version-base | AC2/AC4 | verification/AGPL-RELEASE-1/packages/VERSION-base.json | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | b67919458f0e5a41b6141bc311e73582f3dbb27aebb1c79022ea3513b3d2fb32 | CANONICAL |
| ac4-version-models | AC2/AC4 | verification/AGPL-RELEASE-1/packages/VERSION-models.json | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | b6e45942d8cb83137e740612e4f56462599e139868e00d4315ab0da67e999e04 | CANONICAL |
| ac4-summary-base | AC4 | verification/AGPL-RELEASE-1/packages/package-summary-base.json | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | 2aa9aeefae4d0413df22392c0d62f2fb9228912f629dd2e21a5419f3c46fa752 | CANONICAL |
| ac4-summary-models | AC4 | verification/AGPL-RELEASE-1/packages/package-summary-models.json | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | 4523620b65eb4d96e765b9ec570221304f32804edb92cd921c0a4a2dfce8f539 | CANONICAL |
| ac5-test-summary | AC5 | verification/AGPL-RELEASE-1/test/summary.json | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | cca4a2a804aa72722e2eeeae82e34492736551d09295543515a649d858fa3a53 | CANONICAL |
| ac1-weights-licenses | AC1 | verification/AGPL-RELEASE-1/weights-licenses.json | 35fd83c3ab28e0f3293238bd17543c5cec2f8e91 | 99bb7bb2695d27b42bdc0746dee5b9e836b3a4d647d985f562e1594e8546e171 | CANONICAL |
| ac5-governance-check | AC5 | verification/AGPL-RELEASE-1/check-governance.json | - | f020d1f577cfd4e117d99ee4a75e687945b94c8eea4b1b2ea6519d028b278b17 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| worktree | G:/CODEX/New Manga.workspace/worktrees/AGPL-RELEASE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/worktrees/AGPL-RELEASE-1 | verification/AGPL-RELEASE-1/weights-licenses.json | 交付 head 与 repo_head 记录于该 JSON 的 run_meta；未 push；按 Worktree Safety Inventory 复核后由 DSH 处置 |
| task-env | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1 | verification/AGPL-RELEASE-1/package-check.json | 含 out/（两变体 stage+zip）、evidence-test/、evidence-raw/、logs/；重打包输出只写此处；引用检查见 package-check.json |
| package-input | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-5/out | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/RELEASE-REPACK-5/out | verification/AGPL-RELEASE-1/weights-licenses.json | 只读作为 sidecar/基线；REPACK-5 zip 与 summary 未被覆盖（输入 core_service sha `bde2d866…`，zip 字节记录于 weights-licenses.json） |
| artifact | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64.zip | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64.zip | 722fc62b53a4488dff8e3043b419a720cb59c3e4c790a9c8d19511efb627e8ef | 重打包 base 变体 zip（103,492,048 B），SHA-256 实测；证据见 package-check.json |
| artifact | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64-models.zip | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/AGPL-RELEASE-1/out/NewManga-0.1.0-win-x64-models.zip | 480d06323ce482214955582dc86696bfdd8023e9227100941fd6b8873b237f67 | 重打包 models 变体 zip（725,499,708 B），SHA-256 实测；证据见 package-check.json |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`complete`（15 项 64-hex evidence pin；`check-governance.json` 含 `check.ps1 -TaskPath` PASS 记录）。
- resource_closeout_status：`pending`（由 DSH 在集成窗口按本 Manifest 逐项处置）。
- 删除、迁移、归档数量/字节数：本 Task 未删除/迁移/归档；task-env（两变体 stage+zip ~1.7GB）与 worktree 保留至 Review/集成。
- 未关闭项及保留原因：REPACK-5 out 只读保留（被本卡证据引用）；AGPL 义务的发行页「对应源码」链接属发布流程，交 DSH/发布项处理。
- 当前指针清理：STATUS/PLAN/LEDGER 由 DSH 统一更新（Owner 未改这三份文件）。
