---
id: MANUAL-VERIFY-1
title: 真机人工核验（AD-002 重构收尾的唯一人工环节）
kind: verification
governance_version: 3
status: in_progress
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: user
owner: user
reviewer: dsh
depends_on: [FINAL-VALIDATION-1]
base_commit: 0ab42cd15
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/MANUAL-VERIFY-1
allowed_paths:
  - doc/tasks/MANUAL-VERIFY-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/MANUAL-VERIFY-1/**
---

# MANUAL-VERIFY-1：真机人工核验

## 背景

AD-002 S0–S5 与后端瘦身/推理基线/发布件已全部完成（`FINAL-VALIDATION-1` done：base zip 97.75MB + models zip 690.94MB、安装 smoke PASS）。剩余唯一环节是**必须在真机上用人眼/人工输入确认的 5 项**，Agent 无法诚实验证。

## Acceptance Criteria（用户执行，DSH 记录）

- [ ] **AC1 Mica**：Win11 上窗口材质为 Mica（非纯色），截图或人眼确认。
- [ ] **AC2 DPR2 400%**：在 200% 缩放显示器上，阅读器 400% 等效像素锐利（无插值模糊）。
- [ ] **AC3 进程工作集**：webtoon 长条滚动时进程工作集峰值 ≤1.5GB。
- [ ] **AC4 微软拼音**：输入 20 个中文字符无丢字、候选窗位置正确。
- [ ] **AC5 沉浸阅读**：沉浸模式 Esc 退出、H 隐藏 UI 行为正常。
- [ ] **AC6 记录**：结果（PASS/FAIL + 截图路径）回填本卡 Review 段；FAIL 项开修复 Task。

## 执行方式

使用发布候选包（`task-envs/FINAL-VALIDATION-1/out/NewManga-0.1.0-win-x64.zip` + `-models.zip`），按 `apps/desktop-avalonia/docs/MANUAL_VERIFY.md` 逐项执行；结果贴回本卡。

## 后续（非本卡范围，需用户批准后释放）

50 条 NOT_SUPPORTED 命令分批接线（settings/plugins/backup/region/reader/Run/Export）、代码签名 + NSIS/MSIX、`devices/manager.py` 改 ORT EP 探测、绝对精度 vs 人工 GT。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Closeout Record

- Closeout date / DSH：待用户回填后关闭。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：关闭时更新 STATUS/PLAN/LEDGER。
