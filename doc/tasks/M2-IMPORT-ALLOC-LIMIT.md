---
id: M2-IMPORT-ALLOC-LIMIT
title: "大图导入 QImageReader allocation limit 可配置化（建议 B：Qt 256MB 默认上限拒绝 webtoon 导入）"
kind: feature
status: ready
approval: user_ruling_2026-10-01_all_four
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: [M2-TA3-B2]
base_commit: 8e0de8d0
branch: agent/zcode/M2-IMPORT-ALLOC-LIMIT
worktree: G:/CODEX/New Manga.worktrees/M2-IMPORT-ALLOC-LIMIT-zcode
---

# M2-IMPORT-ALLOC-LIMIT：大图导入 allocation limit 修复

## 背景（M2-TA3-B2 F2）

TA3-B2 实证：K07（690×131289，≈345.6MiB 解码）K09/K10（≈264.5/265.0MiB）被 Qt `QImageReader` **内建默认 256MB allocation limit** 拒绝导入（`src/infrastructure/importing.py:45-59` 是唯一 QImageReader 使用点，无 allocation limit 设置点）；F1 五例 <256MiB 且 import OK——尺寸边界自洽。webtoon 长条漫是产品目标域，256MB 默认上限直接阻断。

## 交付（AC）

1. **AC1 修复**：导入路径显式设置 allocation limit——方案自选并留痕（如 `QImageReader.setAllocationLimit(N)`，Qt 6.5+ API；N 取安全值如 2047 或从 settings 读取，须论证选择的理由与内存上界风险）；同时评估 degraded/失败路径的 typed 错误信息改善（r1 R4：当前 per-file detail 为空串，应携带 reader 级错误原文）。
2. **AC2 测试**：先红后绿——现有 256MB 上限下超大尺寸图（伪造大尺寸头，不造真大文件）导入 FAIL 的测试；修复后同图导入 PASS（或 typed 可诊断）；setAllocationLimit 调用断言。
3. **AC3 真图验证**：K07 真实文件（`test_assets/comic_golden_suite/韩漫_KO/01_webtoon_..."` 路径见 TA3-B2 case-selection/qual-K07.json）经生产 import 通道跑通，尺寸/宽高登记。
4. **AC4 文档**：memory 上界选择论证（为何该值安全）、Task/Handoff 登记；F2 的「推断」口径可升级为一级证据（复跑 K09 原始错误归档，若顺带）。

## 允许修改面 / 禁改面

允许：`src/infrastructure/importing.py`、`tests/`（import 相关）、`experiments/M2-IMPORT-ALLOC-LIMIT/**`（真图验证脚本）、`verification/M2-IMPORT-ALLOC-LIMIT/**`、Task/Handoff。
禁改：`src/ports/**`、其他 infrastructure 文件、`src/bootstrap/**`、`doc/contracts/**`、`packaging/**`、`apps/**`、`doc/STATUS.md`。

## 纪律

- fail-closed 语义不放宽（超上限仍 typed 失败，只是上限更合理+错误可诊断）；内存上界必须有论证（不能简单 setAllocationLimit(0) 无限放行，除非论证 Qt 内存管理可控并登记风险）。
- 基线不回退：main 509+1skipped 0 failed。
