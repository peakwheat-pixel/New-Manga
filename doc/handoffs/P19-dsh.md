---
task_id: P19
author: dsh (executor/verifier; epoch 6)
recipient: Codex (独立非作者复核) / Coordinator
base_commit: 6f128dfe2
delivery_head: f00fbeab4
status: in_review
---

# Handoff：P19 四页安全 E2E（D 变体验收）

## 交付结果

**已按用户裁决执行端到端验收**（用户 2026-10-17："授权，选D+"）。D+ 的 **CDP 通道**在本构建不可用（Tauri 覆盖 `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS`，实测所有 `msedgewebview2.exe` 无 `remote-debugging-port`、无端口监听），故按 **D 变体**执行：**真实 WebView2 窗口 + UIA 语义断言 + 交互驱动**（仍为真实渲染路径，非替身）。**CDP 不可用已双处如实登记**（[dplus-status-r3.md](../../verification/P19/dplus-status-r3.md) 与 [d-acceptance-r1.md](../../verification/P19/d-acceptance-r1.md)）。

## 过程中修复的真实缺陷（本 Task 的直接产出）

| 缺陷 | 处置 | 结果 |
|---|---|---|
| **启动即崩 exit 101**（`catalog` 存在而命名空间锁/binding 缺失 → 自举跳过初始化 → 裸 `FileNotFoundError`） | 释放 **P19-BOOT-1**：从 catalog 权威身份恢复绑定 + 类型化失败 + 锁写入截断；Coordinator A/B 复现"崩溃→正常启动"，Core **515 passed** | **done**（`c6d2e9a30`） |
| **打包 sidecar 早于修复**（产品仍崩） | 重建 bundle（`build_sidecar.ps1 -Force`，HEAD=c6d2e9a3，65.6MB/11:15）+ `cargo build` 刷新资源（hash `41932CED…` 一致） | 已修复并复核 |

## AC 状态

- **AC1**：用户裁决 ✓（D+）；CDP 不可用 → **降级 D 并如实声明**（PASS，含限制）
- **AC2 四页可达 + 主流程**：**PASS**——书架 21 / 工作台 101 / 阅读器 36 / 设置 64 个具名 UIA 元素；并驱动 `⚙️ 设置 → 新建 Profile` 弹出**契约 §3.1 对应表单**（`provider_id`/`display_name`/`capabilities`：OCR·Translation·Inpaint·Detection）
- **AC3 安全边界**：**PASS（UI 层）**——UI 无 path/secret/凭据/原始响应文本；设置页明文"凭据只经专用一次性通道配置，永不回显明文"；**内存/边界级**由 P15-HOST-2 六类反例测试覆盖（互补，不互相替代）
- **AC4 未交付缺口禁用**：**PASS**——设置 **9 分区标「未开放」**；工作台两处诚实说明（页序 wire 未冻结；低清缩略图未接入）
- **AC5 可复现与如实**：**PASS**——命令/步骤/UIA 转储/截图入库；**CDP 不可用**与**未提交表单**均如实声明
- **AC6 交付**：见下

## 证据清单（`verification/P19/`）

`boot-defect-r1.md`（缺陷 #1 报告）、`boot-defect-stderr-run{1,2,3}.log`、`stale-bundle-r2.md` + `app-stale-bundle-stderr.log`（缺陷 #2）、`dplus-status-r3.md`（CDP 不可用与诊断面误判更正）、**`d-acceptance-r1.md`（四页 UIA 断言 + 交互流程）**、`app-window-bookshelf.png`。

## 未关闭项与限制（如实）

1. **CDP/DOM 级断言不可用** → 本验收为 **UIA 语义级**。
2. **未提交表单**（未构造真实写入，避免污染用户 AppData）。
3. **未执行**"导入真实文件 → Run → 导出"与阅读器实际翻页（需用户数据/长耗时）。

## 接收方式

请 **Codex** 以**非作者**身份独立复核：① 证据是否足以支撑 AC2/AC4 的 PASS；② CDP 不可用的降级是否被如实声明、是否影响 AC1 判定；③ 上述三条限制是否应在关闭前补齐或作为 `closed_with_limitations` 条件；④ 是否需要为 P20 增加"sidecar 重建"发布 Gate。**Reviewer 不执行 merge。**