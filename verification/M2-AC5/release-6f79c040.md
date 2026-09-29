# M2-AC5 Release Evidence — release-6f79c040

- Release commit: 本次治理 commit（即 `doc/tasks/M2-AC5.md` 首次登记 commit，父 commit = `6f79c040c79ae4389cf73abcae1b26617b1a2fba`；实际 hash 见 `git log --grep "release M2-AC5"` 与 STATUS release checkpoint）
- Fixed base: `6f79c040c79ae4389cf73abcae1b26617b1a2fba`（release 时 main HEAD；DIGEST-PERF 收口 commit，cargo 34/pytest 35/vitest 31 全绿态）
- Approval: 用户 2026-09-29 指令"按进展和需要以及前置条件释放所需的任务"（编排会话裁量释放，裁量依据见 §3）
- Branch / worktree: `agent/zcode/M2-AC5-package-clean-start` / `G:/CODEX/New Manga.worktrees/M2-AC5-zcode`（从 release commit 检出，创建时干净）
- Roles: Owner=ZCode（子 agent 代行实现）/ 非作者 Reviewer=DeepSeek Harness / Integrator=另一子 agent 代行 Codex（Owner≠Integrator 保持）
- Depends_on: M2-FIX-RESOURCE-CHANNEL-DIGEST-PERF（done @ `bc2529f0`）

## 1. 登记内容（Task 冻结摘要）

- **形态：实现+验收混合**（backlog 第 5 行"Package / clean-start acceptance"）。释放时打包链整体缺失（`bundle.active: false`；production spawn 硬依赖 `M2RC1_SRC_ROOT`+系统 Python）——纯验收必然 BLOCKED，故本 Task 授权最小打包实现 + clean-start 验收。
- **AC1-AC5**：打包产物可复现（NSIS + PyInstaller onedir sidecar，输入/产物 hash 留痕）；packaged spawn fail-closed 且 dev 行为零变化（cargo 34/pytest 35/vitest 31 基线不回退）；无系统 Python clean-start（本机模拟路线，如实标注）；路径落 userData/无残留进程/源文件零风险；证据纪律。
- **允许路径**：tauri.conf.json、main.rs packaged 解析段、core_bridge.rs spawn 支持、icons、`packaging/**` 新增、tests 新增 smoke、Task/verification/handoff。**`src/**` Python 零改动**；产品运行时依赖清单零改动。
- **风险与裁决点**：三 channel 同一闭包由 Owner 按实测选择；clean-start 为 host simulation 口径；NSIS `/S` 静默安装。

## 2. 释放时核验

- main HEAD = `6f79c040`（DIGEST-PERF 收口）；治理文档 clean（除 pre-existing `verification/M2-RC2/raw/*` 5 文件，与本 Task 无关）。
- 无 `in_progress`/`ready` Task 争用；worktree/分支名未占用。
- Release commit 仅含 Task/evidence/治理文档，**零代码**。
- 代码事实锚点：`tauri.conf.json` bundle.active=false；`main.rs:279` `M2RC1_PYTHON`/裸 `python` fallback + `M2RC1_SRC_ROOT` expect 硬必需；sidecar 入口 `-m infrastructure.resource_channel.host_bridge`（`core_bridge.rs:118-119`）等；`icons/icon.ico` 存在；依赖面 stdlib 为主 Qt-free。

## 3. 裁量依据（用户授权"按进展/需要/前置条件释放"）

| 候选 | 裁量 | 依据 |
|---|---|---|
| **Package/clean-start（本 Task）** | **释放** | 前置全满足（DIGEST-PERF done、资源通道语义冻结）；是 M2 Release Gate 硬前置；缺口已实证（打包链缺失）；工作方向单一明确 |
| Real docTR qualification | **不释放（BLOCKED 待用户资源）** | 需受控权重、环境与质量阈值——须用户供给，释放权在用户（协议 §5.1） |
| M2 Release Gate | **不释放（前置未满足）** | cold start/packaged dependencies 依赖本 Task 产物；Windows 10 matrix 等后续 |
| 散落 P3 修复候选（stub 家族/term_extract book_id/P3-5 SetFilePointer 等） | **不释放** | 无产品紧迫性；修复价值排序低于验收线闭合；留待用户裁决 |

## 4. 释放指令存档（用户原文）

> 按进展和需要以及前置条件释放所需的任务
