# FEA-15 集成验收计划（准备版）

- 编制：DSH（Lead / Integrator）
- 日期：2026-11-09；依据：FEA-00 §S5（`:654`）、FEA-13/15 前置证据
- 状态：**准备版**（FEA-14 六切片未全部完成前不构成正式验收）

## 1. 验收范围（方案 §S5）

| # | 验收项 | 判别 | 当前状态 |
|---|---|---|---|
| A1 | 隔离干净构建 | 全新 worktree / 无 bin,obj 下 Release 构建 0 错误 0 警告 | ✅ 已验（`FEA-15-PREREQ-3`，worktree @ `afbc7e411`） |
| A2 | 安装 | 真实安装包安装 + 启动 + 四页面可达 | ⛔ 待正式验收（需安装包与真实 UI 会话） |
| A3 | 双 UI 回归 | legacy `MainWindow.Show()` 与 Fluent shell 两套入口冒烟 + 关键路径测试 | ◐ 部分：App.Tests **838/0/11**、Host **305/0/72**、V2 沉浸阅读器 3/3；真实 UI 会话待正式验收 |
| A4 | 升级与回退报告 | 旧库升级（FEA-13 迁移/备份/恢复证据）+ 回退（pre_restore）可执行 | ◐ 部分：FEA-13 五片证据（backup/2、覆盖、DatabaseId、merge restore、调度）；真实用户库升级待正式验收 |
| A5 | 全量测试基线 | pytest + .NET 全绿 | ✅ 已验（pytest 3446/0/10；.NET 1804/0/107；`FEA-15-PREREQ-2`） |
| A6 | 契约与 pin | 18 pins 全绿、无 UNFREEZE 未决 | ✅ `verify_pins` 18/18 |
| A7 | FEA-14 领域能力 | 六切片（LIB/READ/EDIT/AI/FONT/SET）按各自冻结 Task 验收 | ⛔ 未开始（每切片需单独冻结；见 §3） |
| A8 | 已知 limitation 登记 | 逐项列明并指向后续卡 | ◐ 「源授权元数据未入包」→ `FEA-13-SRC-6`（ZCode 裁决 2026-11-09：同机恢复有效、跨机须重授权） |

## 2. 本次可验收子集（不依赖 FEA-14）

A1（干净构建）、A5（全量基线）、A6（契约/pin）已具备证据；A3/A4 具备「测试层」证据，真实 UI/安装层留待正式验收。

## 3. 待冻结的 FEA-14 切片（DSH 拟定的优先顺序）

| 顺序 | 切片 | 理由 | 主要风险 |
|---|---|---|---|
| 1 | `FEA-14-SET`（Host 能力：托盘/退出协调/启动页/语言/通知/更新/诊断预览） | 不涉 DDL/契约字节；可与 ZCode UI 分 Task | 托盘/语言需产品取舍（交 ZCode/用户裁决） |
| 2 | `FEA-14-FONT`（漫画字体库） | 独立资产库；但需存储位置与 DDL/元数据决定 | 字体许可、库位置 |
| 3 | `FEA-14-LIB`（ContentItem 兼容 DTO） | 数据模型改动 | 需 C-01b/C-15 兼容性裁决 |
| 4 | `FEA-14-READ`（阅读器） | UI 为主 | ZCode 主导 |
| 5 | `FEA-14-EDIT` / `FEA-14-AI` | 大切片、依赖 provider/编辑栈 | 产品取舍与安全 |

## 4. 正式验收前置（清单）

1. FEA-14 六切片按各自 Task 完成并 done（或明确 out_of_scope 裁决）。
2. 真实安装包（`dotnet publish` 产物）安装与卸载验证。
3. 双 UI 真实会话冒烟（legacy MainWindow + Fluent shell 四页面）。
4. 真实旧库升级 + pre_restore 回退演练（隔离用户数据副本）。
5. 独立验证 Agent 复核（上下文独立），报告入 `doc/reviews/`。

## 5. 不构成什么

- 不构成正式验收通过；不构成 FEA-14 的释放授权；
- 不改任何契约字节/18 pins。
