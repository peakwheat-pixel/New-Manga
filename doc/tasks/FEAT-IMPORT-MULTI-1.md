---
id: FEAT-IMPORT-MULTI-1
title: 页面导入支持多选与文件夹导入（用户要求：一次多张 / Ctrl+A 全选 / 直接导文件夹）
kind: feature
governance_version: 2
status: ready
approval: user_requirement_20261017_multi_select_and_folder_import
suggested_owner: Codex
owner: null
reviewer: null
depends_on: [FEAT-CREATE-4]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/FEAT-IMPORT-MULTI-1
---

# FEAT-IMPORT-MULTI-1：多选 + 文件夹导入

## 来源（用户 2026-10-17 明确要求）
> "我要的是一次能选择很多张，甚至可以 alt+a 进行全选然后导入。尤其需要直接导入文件夹。现在的状态是一次只能选一张。"

**代码层核实**：
- `apps/desktop/src-tauri/src/main.rs:873` 使用 **`blocking_pick_file()`（单选）** → 与"一次只能选一张"一致 → **缺口确认**
- `main.rs:895` 使用 `blocking_pick_folder()`；Core 有 `handle_import_pages`，host 有 `library_import_file`/`library_import_folder` → **文件夹导入能力已存在**，需按用户期望完善语义与入口

## Acceptance Criteria
- [ ] **AC1 多选文件**：`📄 选择图片 / PDF 文件` 必须允许**多选**（改为 `blocking_pick_files()` 或等价），一次选择**多张**后**逐张导入**并汇总结果；单次操作的**总页数增量 = 所选文件数**（重复内容按既有 `duplicate_policy` 处理并如实回报跳过数）。
- [ ] **AC2 全选可用**：系统对话框内 **`Ctrl+A`（或 `Alt+A`）全选**后确认，能导入文件夹内**全部**图片（不得因逐个 `invoke` 导致超时/部分失败；需汇总成功/失败/跳过）。
- [ ] **AC3 直接导入文件夹**：`📁 选择图片文件夹` 选中**一个文件夹**即**递归/按既有规则**导入其中全部图片（超出子目录规则由 Task 明确）；结果汇总同上。
- [ ] **AC4 结果可见**：导入完成后界面必须显示**成功数 / 跳过数（重复）/ 失败数及原因**（脱敏，遵守 §5.10 与封闭错误投影）。
- [ ] **AC5 安全与契约**：不得让前端直接读文件系统或任意路径；必须经既有 host 命令与 Core；不得回显绝对路径/Secret；**不得**下调既有校验。
- [ ] **AC6 测试**：前端（多选映射、汇总渲染、失败脱敏）+ host 侧（多文件/文件夹解析与逐项调用）；既有 **前端 278 / Rust source 107 / packaged 12 / Core 535** 基线**不得回归**。
- [ ] **AC7 真实 GUI 复验（必做）**：重建产品（`npm run build` → `build_sidecar.ps1 -Force` → `cargo build`，**校验 bundle==resource hash 一致**）+ 隔离 `NEWMANGA_DATA_ROOT`（**不改用户数据**）→ 实测：多选 2 张 → 页数 +2；文件夹导入 → 页数 = 文件夹内图片数。留 UIA/窗口证据与退出码。
- [ ] **AC8**：commit + **Handoff（必须）** + Canonical Evidence（`status: in_review`；BL-15/17/19/16/18）。

## 允许 / 禁止
- 允许：`apps/desktop/src-tauri/**`、`apps/desktop/frontend/**`、`src/**`（若 Core 需配合批量语义，**先上报**）、本 Task、Handoff、`verification/FEAT-IMPORT-MULTI-1/**`。
- 禁止：改契约（wire 若需新增字段 → **停下上报**）；Schema/迁移/依赖；改 STATUS/PLAN；碰用户 19 项 dirty；**不得**用"循环调用单文件导入"掩盖超时/失败（AC1/AC2 要求汇总与如实回报）。

## 依赖、风险与阻塞
- 前置：FEAT-CREATE-4（done）。**被阻塞方**：P19 的 AC2 主流程（多页场景与翻页验证）。
- 风险：逐个 `invoke` 造成长时间阻塞 → 需明确进度/汇总与失败隔离。

## 交付与运行记录
- 2026-10-17 Coordinator 释放（dsh, epoch 6），依据用户明确要求。