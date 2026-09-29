---
id: M2-AC5
title: Windows packaging & clean-start acceptance (bundle / self-contained sidecar / no-system-Python workflow)
kind: implementation
status: in_progress
release_state: M2_AC5_PACKAGE_CLEAN_START_RELEASED
approval: approved_by_user_2026-09-29_m2ac5_release
execution_approval: approved_by_user_2026-09-29_m2ac5_release
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
integrator: Codex（另一子 agent 代行，保持 Owner≠Integrator）
depends_on: [M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF]
base_commit: 6f79c040c79ae4389cf73abcae1b26617b1a2fba
branch: agent/zcode/M2-AC5-package-clean-start
worktree: G:/CODEX/New Manga.worktrees/M2-AC5-zcode
delivery_head: null
review: null
integration_merge: null
dispatch_state: CLAIMED
---

# M2-AC5 — Windows Packaging & Clean-start Acceptance

**已释放 `ready`（2026-09-29，用户授权编排会话按进展/需要/前置条件裁量释放；release commit=治理 commit，base=`6f79c040`）。** M2 Acceptance Backlog 第 5 行（Package / clean-start acceptance）。依赖 DIGEST-PERF `done`（integration `bc2529f0`）。[release evidence](../verification/M2-AC5/release-6f79c040.md)。

## 来源与目标

来源：[Rebaseline Plan](../REBASELINE_PLAN.md) M2 Acceptance Backlog 第 5 行；M2 Release Gate 的硬前置（Gate 的 cold start / packaged dependencies 均依赖"有包可测"）。[AD-001](AD-001_TARGET_DESKTOP_ARCHITECTURE.md) 目标产品的可分发形态缺口。

**释放时代码事实（起草核对，Owner 实现时如发现偏差在 Handoff 澄清）**：
- `apps/desktop/src-tauri/tauri.conf.json` `bundle.active: false`——打包链不存在。
- `apps/desktop/src-tauri/src/main.rs:279` 生产 spawn 依赖 `M2RC1_PYTHON`（缺省裸 `python`）与 `M2RC1_SRC_ROOT`（`expect` 硬必需，指向仓库 src 树）——**production 仍要求系统 Python + 源码树，不可分发**。
- sidecar 实际入口为 `-m` 模块：`infrastructure.resource_channel.host_bridge`（资源通道，`core_bridge.rs:118-119`）、production library sidecar（`StdioLibraryChannel::spawn`）与 acceptance bridge（`Ac1Channel::spawn`）；依赖面 stdlib 为主、Qt-free（M2-I2 成果），PyInstaller onedir 自包含可行。
- `icons/icon.ico` 存在。

**目标**：建立最小可复现的 Windows 打包链（Tauri NSIS bundle + 自包含 Python Core sidecar），使安装后的应用在**无系统 Python、无源码树**的环境完成安装→启动→核心 workflow→干净退出；为 M2 Release Gate 提供可测对象。

## Acceptance Criteria

- [ ] **AC1 — 打包产物可复现**：`tauri bundle`（NSIS 目标）产出安装包；Core sidecar 以 PyInstaller onedir（或等效自包含形态）打入安装目录；构建命令、固定输入（frontend build、PyInstaller、tauri bundle）与产物 hash 全部留痕，同一输入重跑产物可复现（hash 一致或差异可解释）。
- [ ] **AC2 — packaged spawn 解析（fail-closed）**：packaged 模式下 spawn 不再依赖 `M2RC1_SRC_ROOT`/系统 Python——sidecar 从安装目录相对路径解析；解析失败返回 typed 错误（fail-closed），不回落系统 python。**dev 模式行为零变化**：既有 `cargo test --bin m2rc1-desktop`（34 passed 基线）、`pytest tests/m2_acceptance`（35 passed 基线）、`npx vitest run`（31 passed 基线）全绿不回退。
- [ ] **AC3 — clean-start（无系统 Python）**：在显式剔除 Python 的 PATH、清空 `M2RC1_*` 环境的模拟环境中，静默安装包并启动：主窗口出现、ListBooks workflow 返回（真实 sidecar 往返）、资源通道 chunk 请求成功；全程无系统 Python、无源码树依赖。**口径=本机模拟路线（T3.2.1 已接受），非干净机覆盖，证据如实标注。**
- [ ] **AC4 — workflow / path / exit**：数据与 derived/managed/catalog 路径落在用户数据目录（`%APPDATA%` 下），不写安装目录与源码树；用户源文件零触碰；正常退出后无残留 sidecar 进程（进程清单断言）。
- [ ] **AC5 — 证据纪律**：固定 HEAD、每命令 shell/解释器头 + EXIT、范围自检（对照允许路径）、`git diff --check <base>..<delivery-head>` 整树 EXIT 0；三层基线（cargo/pytest/vitest）在交付 head 复跑留痕。

## 允许修改范围

- `apps/desktop/src-tauri/tauri.conf.json`（bundle 启用与资源声明）、`apps/desktop/src-tauri/icons/**`
- `apps/desktop/src-tauri/src/main.rs`（packaged 模式解析段）、`apps/desktop/src-tauri/src/core_bridge.rs`（spawn 的 packaged 支持与 typed 失败）
- `packaging/**`（新增：PyInstaller spec、构建/验收脚本）
- `tests/**` 新增 packaged smoke 测试文件（如需要；既有测试行为不得修改）
- `doc/tasks/M2-AC5.md`、`verification/M2-AC5/**`、`doc/handoffs/M2-AC5-*.md`
- 构建工具依赖仅限 `packaging/**` 内的 requirements/说明文件（**产品运行时依赖清单零改动**）

## 禁止范围

- `src/**` Python 代码：**零改动**（sidecar 用既有 `-m` 入口打包；若实测必须改，停下登记候选，不得顺手改）。
- `doc/contracts/**` 契约修订（sidecar 命令面不扩）、SQLite schema、Legacy QML、产品运行时依赖清单。
- 既有测试的行为修改；ACP/RC2/AC1 冻结 E2E 命令面。

## 风险与裁决点（释放时冻结）

- 三个 sidecar channel（资源通道/library/acceptance）须被同一自包含闭包覆盖：onedir 多入口或逐入口打包由 Owner 按实测选择，Handoff 说明取舍。
- "无系统 Python"环境用显式构造的 PATH 剔除模拟（host simulation）；真正干净 Windows 覆盖属 M2 Release Gate 范围，本 Task 如实 NOT_RUN 标注。
- installer 静默安装用 NSIS `/S`；如静默参数不可用，证据中记录替代路径。
- PyInstaller 版本固定并记录；打包仅为本 Task 构建工具，不进产品运行时依赖。

## 交付与运行记录

- Handoff：尚无（`doc/handoffs/M2-AC5-<short-head>.md`）。
- Review：尚无（DeepSeek Harness 非作者）。
- 交付后由 Integrator（另一子 agent 代行 Codex）闭合条件、merge、复跑置 `done`。
