---
id: UI-SHELL-THEME-1
title: S3 主窗 + 主题中心 + 书架（Saber 参考）+ 设置骨架
kind: implementation
governance_version: 3
status: ready
approval: user_authorized_2026-10-26_ad002_autonomy
suggested_owner: zcode
owner: null
reviewer: dsh
depends_on: [HOST-CORECLIENT-1]
base_commit: 5a11fa7d9
branch: task/UI-SHELL-THEME-1
worktree: G:/CODEX/New Manga.workspace/worktrees/UI-SHELL-THEME-1
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/UI-SHELL-THEME-1
allowed_paths:
  - doc/tasks/UI-SHELL-THEME-1.md
  - doc/STATUS.md
  - doc/REBASELINE_PLAN.md
  - doc/TASK_LEDGER.md
  - apps/desktop-avalonia/**
  - verification/UI-SHELL-THEME-1/**
  - G:/CODEX/New Manga.workspace/task-envs/UI-SHELL-THEME-1/**
  - G:/CODEX/New Manga.workspace/worktrees/UI-SHELL-THEME-1/**
---

# UI-SHELL-THEME-1：S3 主窗 + 主题中心 + 书架 + 设置骨架

## 来源与目标

AD-002 §3/§4、`ui-spec/SABER_UI_SPEC.md` + `tokens-saber-purple.json`（已交付）、ADR-0001（布局/共存）、S1/S2 已完成。目标：新壳具备可用的四页骨架，主题中心可运行时热切换，书架按 Saber **参考规格**（非 1:1）实现，并为 S4 工作台/阅读器留出插槽。

## Acceptance Criteria

- [ ] **AC1 主窗与导航**：沉浸式标题栏（Win11 Mica / Win10 回退不透明）、四页导航壳（书架/工作台/阅读器/设置）、单实例、启动不阻塞（不等待 Core 完成首帧）、无控制台。
- [ ] **AC2 主题中心**：ThemePack = `manifest.json + tokens.json + controlthemes.xaml + materials.json + motion.json + icons/`；内置 ≥6 套（含 Saber Purple 默认 + light/dark）；**3 套热切 P95 ≤100ms**、不重启、截图差分无色残留、reduced-motion 归零。
- [ ] **AC3 书架页**（Saber 参考）：紫渐变顶栏、1400 居中、标题+三动作、白卡搜索+标签 chip、封面 3:4 书卡网格（列数在 VM 计算，Avalonia 无 auto-fill）、hover「查看详情」、详情/新建入口、空态/无结果态。
- [ ] **AC4 设置骨架**：分区导航 + 已接线 settings 命令的展示/编辑；S2 的 50 条 NS 中「书架/设置所需」子集逐批接线（列出清单与完成数）。
- [ ] **AC5 质量门禁**：`scripts/test.ps1` 全绿（含 UI headless 测试）；旧壳 `npx vitest run` 仍 60/60 文件 567/567；换肤/导航/书卡交互有测试；无控制台；键盘焦点可达；`check.ps1 -TaskPath` PASS；证据 pin 64-hex。
- [ ] **AC6 交接**：Handoff `doc/handoffs/UI-SHELL-THEME-1-handoff.md`；Record Decision（主题服务设计、NS 接线批次、字体策略=仅系统栈）。

## 允许修改范围

`apps/desktop-avalonia/**`、本卡、STATUS/PLAN/LEDGER 指针、`verification/UI-SHELL-THEME-1/**`、workspace。只读：`ui-spec/**`、`doc/AD-002*`、`doc/design/ADR-*`、`doc/design/EXECUTION_DIRECTIVE_AD002_V2.md`。

## 禁止范围

不改旧壳 `apps/desktop/**`、不改 Python Core、不改 AD/ADR、不 push、不 1:1 复刻 Saber 截图、不随包商业/系统字体（仅系统字体栈）、不 gc/prune。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 启动计时 + Mica 取色 + 无控制台检查 | Win11 26300 | NOT_RUN | 待填 |
| AC2 | 3 套主题 × 30 次切换计时 + 截图差分 | 同上 | NOT_RUN | 待填 |
| AC3/AC4 | headless UI 测试 + 真 sidecar 数据 | sidecar 无标签副本 | NOT_RUN | 待填 |
| AC5 | `scripts/test.ps1` + vitest 基线 + check.ps1 | 全量 | NOT_RUN | 待填 |

## 依赖、风险与阻塞

- 依赖：HOST-CORECLIENT-1（done）；S2 的 NS 清单（Handoff 已列）。
- 风险 1：主题热切与 Mica 合成冲突（spike 已验证可行，需回归）；风险 2：书卡网格列数计算与 DPI；风险 3：NS 命令接线遗漏导致页面空态误判。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) |
|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| task-env | G:/CODEX/New Manga.workspace/task-envs/UI-SHELL-THEME-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/UI-SHELL-THEME-1 | 待填 | 待关闭时核 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写。
- 未关闭项及保留原因：待关闭时填写。
- 当前指针清理：释放时已更新 STATUS/PLAN/LEDGER。
