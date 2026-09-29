---
id: M2-RG1
title: M2 Release Gate（Windows 本机口径）：cold start metrics / Windows matrix / console policy / packaged dependency closure
kind: acceptance
status: in_progress
release_state: M2_RG1_RELEASE_GATE_RELEASED
approval: approved_by_user_2026-09-29_local_machine_ruling
execution_approval: approved_by_user_2026-09-29_local_machine_ruling
suggested_owner: ZCode
owner: ZCode
claimed_by: ZCode
claimed_at: 2026-09-29
reviewer: DeepSeek Harness
integrator: Codex（编排会话代行，保持 Owner≠Integrator）
depends_on: [M2-AC5]
base_commit: 875eb818abc74a498c84026016dd1a1c72e0ad50
branch: agent/zcode/M2-RG1-release-gate
worktree: G:/CODEX/New Manga.worktrees/M2-RG1-zcode
delivery_head: null
review: null
integration_commit: null
dispatch_state: CLAIMED
---

# M2-RG1 — M2 Release Gate（Windows 本机口径）

## 来源与目标

来源：[Rebaseline Plan](../REBASELINE_PLAN.md) M2 Acceptance Backlog 第 6 行（"M2 Release Gate | backlog"）与 Acceptance Backlog 表行 "Cold-start metrics, target Windows support matrix, GUI console policy and packaged dependency closure | DEFERRED | Decide and verify in a future M2 Release Gate/D08; do not inherit the Legacy results."

**用户裁决（2026-09-29，存档原文）**："把本机视为干净widows环境。若本机通过，则视为pass"——据此解除"真干净机覆盖"前置：本机（Windows 11 x64，build 26200）即为验证基座；本机全项通过 ⇒ 本 Release Gate PASS。该裁决按 D08"范围删减、阈值豁免先形成用户可审查的文档决定"的要求以此 Task 文件与 release evidence 固化。

**目标**：对 [M2-AC5](M2-AC5.md) 交付的分发形态（NSIS installer + onedir 四入口自包含 sidecar）执行 Release Gate 四项：**cold start metrics、Windows support matrix、GUI console policy、packaged dependency closure**——每项做出**可审查的裁决（decision）**并给出**机器可验证证据**。可测对象已由 M2-AC5 就位；本 Task 是 M2 新架构首个正式发布验收 Gate（Legacy T3.2.1 PyInstaller Gate 已按 REBASELINE 撤销，不继承其结果）。

**形态：实现+验收混合（同 M2-AC5 先例）**。console policy 现状已在释放侦察中实证 FAIL（见 AC2 证据），故预授权有界修复；修复仅为达成 Gate 裁决所必需的最小改动。

## Acceptance Criteria

### AC1 构建锚定（可复现发布候选）

- [ ] Owner worktree 从 `base_commit` 干净构建：先 `packaging/m2ac5/build_sidecar.ps1`（fresh-checkout 约束），后 Tauri NSIS bundle；构建日志带 shell 头 + 固定 HEAD + EXIT 入库。
- [ ] 记录并锚定：installer sha256、sidecar 全清单 hash（沿用 M2-AC5 的清单格式）、工具链版本（pyinstaller/PySide6/tauri CLI/rustc/NSIS）；本机 OS 版本快照（Windows 11 x64 build 26200）。
- [ ] 后续所有 gate 运行绑定该 installer sha256（gate.json 记录），被测物与 release candidate 一一对应。

### AC2 GUI console policy —— 裁决 + 验证（现状 FAIL，授权有界修复）

**裁决（frozen）**：packaged 产品正常运行（静默安装 → 冷启动 → 核心 workflow → 干净退出）期间，除应用主窗口外**零可见控制台窗口**。

**现状实证（释放侦察，2026-09-29）**：
- `target/release/m2rc1-desktop.exe` PE OptionalHeader Subsystem=**3（CONSOLE）**（python 解析 e_lfanew→Subsystem 字段实测）；main.rs 无 `windows_subsystem` 属性——安装态双击即弹应用自身控制台。
- 全仓 `grep creation_flags|CREATE_NO_WINDOW` 零命中；`packaging/m2ac5/core_sidecar.spec:91` `console=True`——production 分派（main.rs:410-462）派生 `host_bridge.exe`+`core_service.exe`（ac1 模式再加 `acceptance_bridge.exe`）时各自弹控制台。

- [ ] 机器可验证判据（gate runner 实现）：① installed `m2rc1-desktop.exe` PE Subsystem=2（GUI）；② 运行期 EnumWindows 观测：类名 `ConsoleWindowClass` 且窗口标题或属主进程涉及 `m2rc1-desktop`/四 frozen 入口 exe 的顶层可见窗口数=0（app 运行中与退出后各采样）；③ dev 模式行为零变化（cfg_attr 仅 release 生效）。
- [ ] **授权的有界修复**（仅此，不得扩大）：
  - `apps/desktop/src-tauri/src/main.rs` 顶部加 `#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]`；
  - `core_bridge.rs` / `ac1_bridge.rs` / `library_bridge.rs` 的 **Command 构建段**加 `creation_flags(CREATE_NO_WINDOW=0x08000000)`（`#[cfg(windows)]` 门控）；不改协议、不改参数语义、不改其他任何逻辑；
  - **`packaging/m2ac5/core_sidecar.spec` 的 `console=True` 参数值禁改**（stdio JSON 协议依赖管道；PyInstaller windowed 模式会改变 stdout 语义）——如注释需同步可改注释。
- [ ] 修复后重建 → 重装 → 复测 AC2 三判据全过；若修复引入回归（三层基线跌破）停下登记，不得用放宽断言换绿。

### AC3 Cold start metrics —— 测录（无阈值）

**裁决（frozen）**：本 Gate **只测录、不设阈值**——冷启动阈值属用户产品裁决，Backlog 行仅要求 "cold-start metrics"。

- [ ] 安装态（净化 PATH + `APPDATA=<lab>`）测量并落 gate.json + raw 日志，每项 ≥3 次采样（报 min/median/max）：
  - ① app 冷启动：`CreateProcess(installed exe)` → 首个可见顶层窗口（EnumWindows by pid, IsWindowVisible）耗时 ms；
  - ② core ready：安装态 `core_service.exe` stdio probe spawn → `ready` 应答耗时 ms；
  - ③ ac1 handshake：安装态 `acceptance_bridge.exe` spawn → ready 耗时 ms。
- [ ] 环境快照（PATH 净化条目数、APPDATA lab 路径、采样轮次）随数值入库；NOT_RUN 项（如有）如实标注原因。

### AC4 Packaged dependency closure —— 安装态闭环

- [ ] 安装态**四入口** stdio 往返全部成功：`core_service.exe`（core.ping ready + ListBooks envelope）、`host_bridge.exe`（资源通道握手）、`acceptance_bridge.exe`（ac1 handshake）、`catalog_loader.exe`（lab 数据根真实 seed + SQLite 读回）。
- [ ] PyInstaller warn 文件（4 入口，`build_sidecar.ps1` 产物）入库并逐类审查：缺 load-time-critical 模块=FAIL；仅条件导入/可选模块=逐条披露。
- [ ] 复用 M2-AC5 clean-start runner（25 场景）作为回归基线并在本 installer 上全 PASS；其证据按 **"运行 → 搬运（改名 `rg1-m2ac5-*` 入 `verification/M2-RG1/raw/`）→ `git restore verification/M2-AC5/`"** 处理——M2-AC5 raw 在本 Task worktree 中**不得提交**（runner 写死 `verification/M2-AC5/raw/` 绝对路径，属 M2-AC5 P3-9(b) 已知行为，披露即可）。

### AC5 Windows support matrix —— 裁决 + 记录

**裁决（frozen）**：当前支持矩阵声明 = **"Windows 11 x64（本机 build 26200）已验证（本 Gate）；Windows 10 及其他 build 未验证（NOT_RUN，如实披露）"**。矩阵扩展（Win10 物理/虚拟机覆盖）登记为后续候选，不阻断本 Gate。

- [ ] 本机环境快照入库：OS 名称/版本/build、架构、CPU/内存摘要。
- [ ] Windows 10 / 其他版本 NOT_RUN 在 Task、Handoff、verification-results 三处如实标注（不得写成 N/A 或 PASS）。

### AC6 证据纪律与范围

- [ ] 所有 raw 日志带 shell/解释器头 + 固定 HEAD + 每命令 EXIT；gate 汇总 JSON 机器可读。
- [ ] `git diff --name-status <base>..<delivery_head>` 对照两级允许路径（日志入库）；`git diff --check <base>..<delivery_head>` EXIT=0。
- [ ] 三层基线不回退：`cargo test --bin m2rc1-desktop`（≥38 passed + 1 ignored）/ `pytest tests/m2_acceptance -q`（≥35）/ `npx vitest run`（≥31）全 EXIT=0；触碰 Rust spawn 段后 cargo 必须全绿。
- [ ] NSIS 卸载测试 NOT_RUN 如实披露（不在 Backlog 四项范围）；**`src/**` Python 零改动**（发现缺陷只记 FAIL/候选）。

## 允许修改范围

**无条件允许**：
- `packaging/release-gate/**`（新增：gate runner 脚本 + README）
- `verification/M2-RG1/**`
- `doc/tasks/M2-RG1.md`、`doc/handoffs/M2-RG1-*.md`

**条件允许（仅当 AC2 现状 FAIL——释放侦察已实证成立，随 release 激活）**：
- `apps/desktop/src-tauri/src/main.rs`（仅顶部 `windows_subsystem` 属性）
- `apps/desktop/src-tauri/src/core_bridge.rs`、`apps/desktop/src-tauri/src/ac1_bridge.rs`、`apps/desktop/src-tauri/src/library_bridge.rs`（**仅** Command 构建段 `creation_flags`；AC2 冻结的修复形态）
- `packaging/m2ac5/core_sidecar.spec`（仅注释同步；`console=True` 参数值禁改）

**禁止**：`src/**`（Python）、`requirements.txt`、`doc/contracts/**`、`apps/desktop/frontend/**`、`packaging/m2ac5/run_clean_start_e2e.py`（M2-AC5 回归参照不得改）、`verification/M2-AC5/**`（不得提交）、`tauri.conf.json`（若证明必需，停下登记）、其他任何共享契约。

## 禁止范围

非目标：安装包 bit-for-bit 可复现（沿用 M2-AC5 候选登记）、NSIS 卸载链路、自动更新、代码签名、多语言/本地化、性能阈值设定（AC3 只测录）、Windows 10 实机覆盖（AC5 候选）。用户源文件、人工修改、Lock、current/pinned Revision 保护语义不在本 Task 触碰面。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | build_sidecar.ps1 + `npx tauri build`（worktree 内） | fresh worktree @ base | 计划中 | verification/M2-RG1/raw/ |
| AC2 | gate runner：PE subsystem 解析 + EnumWindows 运行期观测 | 安装态 | 计划中 | gate.json + raw |
| AC3 | gate runner：三类冷启动计时 ≥3 采样 | 安装态 + 净化 PATH | 计划中 | gate.json + raw |
| AC4 | 四入口 stdio 往返 + warn 审查 + M2-AC5 25 场景回归 | 安装态 + lab 根 | 计划中 | gate.json + raw |
| AC6 | 三层基线 + diff --check + name-status | worktree @ delivery head | 计划中 | raw |

## 产物与交接链接

- Handoff：`doc/handoffs/M2-RG1-<short-head>.md`（交付后回填）
- Release evidence：`verification/M2-RG1/release-875eb818.md`
- Review 报告：`doc/reviews/M2-RG1-<head>-dsh-r1.md`（交付后回填）

## 已知阻塞

无。前置 M2-AC5 已 done；真干净机前置经用户裁决（2026-09-29）以本机口径解除。
