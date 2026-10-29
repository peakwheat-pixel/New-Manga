---
id: AD002-FOLLOWUPS-1
title: AD-002 重构遗留项集中登记（NS 批次/签名/进度保存/多章/精度）
kind: planning
governance_version: 3
status: closed_with_limitations
approval: user_authorized_2026-10-27_followups
suggested_owner: dsh
owner: dsh-lead
reviewer: region-workbench-owner
depends_on: []
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/AD002-FOLLOWUPS-1
allowed_paths:
  - doc/tasks/AD002-FOLLOWUPS-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
---

# AD002-FOLLOWUPS-1：重构后遗留项集中登记

AD-002 重构（S0–S5 + 后端瘦身 + 推理基线 + 发布件）已完成，真机 5 项全部 PASS。本文集中登记**未包含在重构范围**的遗留项，供用户决定优先级后逐个释放。

## 遗留清单（按类型）

### A. 功能补全（产品内不可用/受限）
1. **50 条 NOT_SUPPORTED 命令分批接线**（S2 范围裁决）：settings/plugins/backup/cleanup → region/reader 写 → Run/Export。
2. **阅读进度保存**（`SaveReadingProgress` 未接线）。
3. **多章选择器**（当前固定第一本书第一章）。
4. **全局快捷键 F11**（当前入口为按钮/双击）。
5. `devices/manager.py` 改 **ORT EP 探测**（打包后设置页 GPU 状态显示不可用，不影响推理）。

### B. 发布形态
6. **代码签名 + NSIS/MSIX**（当前 zip + `install.ps1`）。
7. **AGPL 声明落地**（yolo11s-seg=AGPL-3.0；`NOTICE` 已预留，发行页需同步）。

### C. 质量/研究
8. **绝对精度 vs 人工 GT**（检测/OCR；无对齐标注，INFER-BASELINE/CORE-SLIM-2 均 NOT_RUN）。
9. CUDA 可选包构建（当前主包仅 DirectML）。
10. 50 NS 中 Run/Export 链路端到端验证。

### D. 历史与治理
11. **旧壳彻底归档**（当前原位冻结；移动需授权 + 引用迁移清单）。
12. Win10 真机验证（Mica/DPI；本机不可得）。
13. 真实用户数据升级演练（旧 Tauri 版 → 新壳，dry-run 已有，真实数据未跑）。

## AC（本卡为登记表，释放子任务后关闭）

- [x] **AC1 清单登记**：以上 13 项 + 追加 7 项全部登记；截至 2026-10-29 全部已释放，其中 18 项完成、2 项受外部条件限制。<<MET>>
- [x] **AC2 释放规则**：按 S2/S3/S4/S5 批次与独立 Task 释放（S2/S4 命令批次、阅读进度、章节选择、F11、导入导出、region 工作台、PDF 导出等）。<<MET>>

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|
| release-0.1.1-verify | AC1/AC2 | verification/RELEASE-REPACK-6/verify.json | 93cfb1bce | 39b0c6a11ac747e12fc35e7074c89d000f6f0cb6d1a1b03d92e89da2c6b5d3e5 | CANONICAL |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| register | doc/tasks/AD002-FOLLOWUPS-1.md | NOT_APPLICABLE | — | — | 登记表，无派生资源；证据在各子 Task 的 evidence_dir |

## Closeout Record

- Closed：2026-10-29 as **closed_with_limitations**（清单已作为登记表完成使命；18/20 项已释放并完成，2 项受外部条件限制）。
- 已完成项（对应 Task）：#1 命令接线（Host 57 条命令全部映射，源码注释 "no NOT_SUPPORTED command left"）、#2 READING-PROGRESS-1（done `bafe73709`）、
  #3 CHAPTER-SELECTOR-1（done）、#4 F11-HOTKEY-1（done）、#6 NSIS-INSTALLER-1 + SIGNPATH-OSS-SIGNING-1（done；签名待批）、#7 AGPL-RELEASE-1（done）、
  #9 CUDA-PACKAGE-DECISION-1（done，defer）、#11 LEGACY-SHELL-ARCHIVE-1（closed_with_limitations）、#13 REAL-USER-UPGRADE-1（done）、
  #14 REAL-TRANSLATE-PROVIDER-1（done，AC3 额度 BLOCKED）、#15 RELEASE-REPACK-6（done，0.1.1 含修复）、#16 SCHEDULER-THREAD-DIAG-1（done）、
  #17 PDF-EXPORT-1/PDF-EXPORT-UI-1（done）、#19 REGION-WORKBENCH-1（done，含 region 写 UI）、#20 IMPORT-EXPORT-UI-1（done）、
  #18 list_region_revisions（REGION-WORKBENCH-1 内完成）。
- 未完成项（外部条件）：
  - #8 绝对精度 vs 人工 GT：无对齐人工标注数据（INFER-BASELINE/CORE-SLIM-2 均 NOT_RUN），需用户提供标注集。
  - #12 Win10 真机验证：本机不可得。
  - #5 devices/manager ORT EP 探测：已由 VERSION.json 构建期 probe 覆盖（设置页设备信息来自构建元数据）；如需运行期探测可另开小 Task。
- canonical_evidence_status：`complete`（本卡为登记表，证据在各子 Task）。
- resource_closeout_status：`complete`（无派生资源）。
- 删除、迁移、归档数量/字节数：无。
- 当前指针清理：STATUS/PLAN/LEDGER 已更新。


## 追加登记（2026-10-27，A/B 批次后）

### E. Run/Export 链闭环
14. **翻译 provider slice**：`translate` 步骤 typed `PROVIDER_NOT_CONFIGURED`（CORE-PIPELINE-FIX-1 后 Run 止于此）→ 接入翻译 provider 才能到 render/Export。
15. **sidecar 重打包**：Core 修复（color analyzer/空检测语义）只在源码，冻结 `core_service.exe`（`2b36bfeb…`）未重打包；发布前需重打包 base + models 包并复跑 `verify_inproc.py`。
16. **调度线程异常诊断**：`python -m bootstrap.core_service` 调度线程内 detect StepRun 卡 `running`、下游 regionless ocr 报 `INVALID_INPUT`（进程内正常，3 份证据）——疑 `ThreadRoutedConnection`/`write_in_current_transaction` 事务路径，建议单开诊断 Task。
17. **Export 真跑**：需 14 + translated 产物 + grant（grant 已由 GRANT-ISSUER-1 完成）。

### F. 命令面收尾
18. `list_region_revisions`（读）仍 NS，路由探针 ok:true，可直接接线。
19. region 写 UI 入口 + 只读门（S5）。
20. App 侧导入/导出 UI（文件/文件夹选择器 → 已接的 4 条 Host 命令）。
