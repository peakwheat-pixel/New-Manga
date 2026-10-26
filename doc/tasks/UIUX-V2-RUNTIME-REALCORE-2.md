---
id: UIUX-V2-RUNTIME-REALCORE-2
title: 补齐真机端到端未覆盖路径（原生导入 / Core 掉线 / 编码守卫）+ 视觉窄窗与高 DPI
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_autonomous
suggested_owner: codex
owner: codex
reviewer: dsh
depends_on: [UIUX-V2-RUNTIME-REALCORE-1]
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/UIUX-V2-RUNTIME-REALCORE-2
allowed_paths:
  - doc/tasks/UIUX-V2-RUNTIME-REALCORE-2.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - verification/UIUX-V2-RUNTIME-REALCORE-2/**
  - apps/desktop/frontend/e2e/uiux-v2/**
---

# UIUX-V2-RUNTIME-REALCORE-2：补齐真机端到端未覆盖路径

## 来源

[UIUX-V2-RUNTIME-REALCORE-1](UIUX-V2-RUNTIME-REALCORE-1.md) 已用脚本化 CDP 验收把「真实 Tauri 生产窗 + 真实 Python Core」跑通 7/7，并修掉 P0 中文编码与 P1 死按钮。该 Task 显式保留了三处 **PARTIAL** 与两条 ZCode 复核的 P3 未覆盖项。本 Task 只做这些缺口——不重做已通过的部分。

## 目标（一条一条可验收）

- **G1（对应 AC3）**：自动化覆盖"从本地图片导入页图"这条路径。难点是原生文件选择器：需要一种**不依赖人点系统对话框**的方式（例如 Core 侧已有的 import 命令直调 + UI 侧导入对话框的状态机断言，二者结合；或对 `input[type=file]` 用 CDP `DOM.setFileInputFiles`）。
- **G2（对应 AC4）**：受控故障注入——杀掉 sidecar Core 进程，断言四页状态条进入真实错误态（显示错误码，不是空白或假成功），并验证重启后恢复。
- **G3（对应 AC5 剩余）**：高 DPI（如 150%/200% 缩放）与窄窗口（如 900×700）下的布局与亚克力预算表现，用计算样式断言而非人眼。
- **G4（ZCode R-P3-3）**：`core_bridge.rs` / `ac1_bridge.rs` 的请求序列化仍用原样 `to_string()`，当前载荷恰好全 ASCII 但**没有守卫**。二选一：统一走 `ascii_json_line`，或加一条断言守卫（载荷含非 ASCII 即失败/即崩溃可见）。必须留下明确选择理由。
- **G5（ZCode R-P3-2）**：`Shelf.test.tsx` 的 aria-expanded 守卫只覆盖 `false` 分支；补 `commandOpen=true` 的覆盖。

## 允许修改范围

- `apps/desktop/frontend/e2e/uiux-v2/**`（扩展场景）
- `verification/UIUX-V2-RUNTIME-REALCORE-2/**`（证据）
- 若 G4 选择统一序列化：`apps/desktop/src-tauri/src/core_bridge.rs`、`ac1_bridge.rs`（仅该函数与测试）
- 若 G5 需要：`apps/desktop/frontend/src/pages/Shelf.test.tsx`

**不允许**：改产品视觉/交互设计、改 IPC 契约形状、动 `tauri.conf.json`、触碰用户真实数据根。

## 约束（来自 REALCORE-1 的教训，必须继承）

1. 所有运行使用隔离数据根（`NEWMANGA_DATA_ROOT`/`APPDATA`/`LOCALAPPDATA`/`TEMP`/`WEBVIEW2_USER_DATA_FOLDER` 全指 workspace），启动前断言干净；**不得读写 `%LOCALAPPDATA%\New Manga`**。
2. 页面已加载时**不要 `Page.reload`**（会打断 Tauri IPC 桥，REALCORE-1 实测 hang）。
3. WebView2 的真实鼠标事件必须带 `buttons`，否则 Chromium 当 hover 处理。
4. 需要 CDP 时用 `tauri.acceptance.conf.json` 构建验收 exe，**不得**把调试端口带进发布构建。
5. 失败轮次保留 `report.json`，过程文件（logs/shots）移 workspace，不混进 canonical 证据集。
6. 任何"实测"结论都必须有可复查留痕（REALCORE-1 的 R-P2-1 教训）；不得用"我跑过了"代替证据。

## 验收方式

- 沿用 `node e2e/uiux-v2/run.mjs` 的断言风格：每个新场景独立 `record()`，exit code 反映全绿/失败。
- 新增场景建议编号 S8（导入）、S9（Core 掉线/恢复）、S10（窄窗+高 DPI）。
- 证据落 `verification/UIUX-V2-RUNTIME-REALCORE-2/`，README 记录命令、SHA、复现步骤。
- 完成后必须由**未参与实现**的 Agent 独立复核（DSH 实现则 ZCode 复核，反之亦然）。

## 明确不在本 Task

- push（维持未执行裁决）。
- 任何视觉重设计或设计系统变更。
- 引擎/导入/渲染管线的新功能。
