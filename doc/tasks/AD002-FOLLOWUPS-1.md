---
id: AD002-FOLLOWUPS-1
title: AD-002 重构遗留项集中登记（NS 批次/签名/进度保存/多章/精度）
kind: planning
governance_version: 3
status: proposed
approval: user_authorized_2026-10-27_followups
suggested_owner: dsh
owner: null
reviewer: null
depends_on: []
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
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

- [ ] **AC1 清单登记**：以上 13 项全部登记并可被用户按优先级选择。
- [ ] **AC2 释放规则**：每批 ≤3 项，按 S2/S3/S4 校验口径（单命令 + 真机/证据 + 治理）释放为独立 Task。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| — | — | — | — | — | 登记表，无派生资源 |

## Closeout Record

- Closeout date / DSH：全部遗留项已释放或用户明确放弃后关闭。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：无。
- 未关闭项及保留原因：即本清单。
- 当前指针清理：关闭时更新 STATUS/PLAN/LEDGER。
