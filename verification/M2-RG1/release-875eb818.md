# M2-RG1 Release Evidence — M2 Release Gate（Windows 本机口径）

- **Release commit（治理）**：本文件所在 commit（见 STATUS release checkpoint 记录实际 hash）
- **base_commit**：`875eb818abc74a498c84026016dd1a1c72e0ad50`（main @ M2-AC5 收口）
- **Task**：[doc/tasks/M2-RG1.md](../../doc/tasks/M2-RG1.md)（`ready / M2_RG1_RELEASE_GATE_RELEASED`）
- **Owner**：ZCode（子 agent 代行）；**非作者 Reviewer**：DeepSeek Harness；**Integrator**：编排会话代行 Codex（Owner≠Integrator 保持）
- **branch**：`agent/zcode/M2-RG1-release-gate`；**worktree**：`G:/CODEX/New Manga.worktrees/M2-RG1-zcode`（release 时创建）
- **depends_on**：[M2-AC5](../M2-AC5/integration-0541b86b/integration.md) `done`（integration=`9db08dc7`）

## 1. 用户裁决存档（授权锚点）

> **用户（2026-09-29，原话）**："把本机视为干净widows环境。若本机通过，则视为pass"

裁决解释（本会话作为 Lead 的落字口径，用户可审查）：解除 M2 Release Gate 的"真干净机覆盖"前置——**本机（Windows 11 x64，build 26200，开发工具链在场）视为干净 Windows 环境的验证基座**；干净性由 M2-AC5 已交付的净化手段保证（净化 PATH、`APPDATA=<lab>` 隔离、安装目录 hash 零变化）；**本机全项通过 ⇒ Release Gate PASS**。Windows 10/其他 build 不在本轮覆盖，如实 NOT_RUN 披露（AC5）。

## 2. 裁量与释放依据

Backlog 第 6 行四项（cold start、Windows matrix、console policy、packaged dependencies）的可测对象已由 M2-AC5 就位；用户裁决补齐最后一项前置（干净机口径）。**形态=实现+验收混合**（同 M2-AC5 先例），因释放侦察实证 console policy 现状 FAIL：

| 现状证据（2026-09-29 实测） | 结论 |
|---|---|
| `target/release/m2rc1-desktop.exe` PE OptionalHeader Subsystem=**3 (CONSOLE)**（python 解析 e_lfanew→+68 实测；magic=0x20b） | 安装态双击弹应用自身控制台窗口 |
| main.rs 全文无 `windows_subsystem` 属性（grep 零命中） | release 构建未声明 GUI 子系统 |
| 全仓 grep `creation_flags|CREATE_NO_WINDOW` 零命中；`core_sidecar.spec:91` `console=True` | production 派生 `host_bridge.exe`/`core_service.exe`（ac1 加 `acceptance_bridge.exe`）各弹控制台 |

故预授权 AC2 有界修复（`windows_subsystem` 属性 + 三 bridge Command 段 `creation_flags(CREATE_NO_WINDOW)`；spec `console=True` 禁改——stdio 管道协议依赖）。修复范围冻结于 Task AC2；`src/**` Python 零改动硬边界不变。

## 3. Backlog 四项 → M2-RG1 AC 映射

| Backlog 冻结项 | AC | 裁决口径 |
|---|---|---|
| cold start（metrics） | AC3 | 只测录（app 窗口/core ready/ac1 handshake，≥3 采样）；阈值属用户产品裁决，不在本 Gate 设定 |
| target Windows support matrix | AC5 | 本机（Win11 x64 build 26200）=已验证基座；Win10/其他 NOT_RUN 披露；扩展登记候选 |
| GUI console policy | AC2 | packaged 正常运行零可见控制台（主窗口除外）；现状 FAIL → 有界修复后复测 |
| packaged dependency closure | AC4 | 安装态四入口 stdio 闭环 + PyInstaller warn 审查 + M2-AC5 25 场景回归 |

## 4. 冻结字段与两级允许路径

见 [Task 文件](../../doc/tasks/M2-RG1.md) frontmatter 与"允许修改范围"节。要点：无条件=`packaging/release-gate/**` 新增、`verification/M2-RG1/**`、Task/Handoff；条件（AC2 修复激活）=main.rs 顶部属性 + core_bridge/ac1_bridge/library_bridge Command 段 creation_flags + spec 注释；禁止=`src/**`、`requirements.txt`、contracts、frontend、`run_clean_start_e2e.py`、`verification/M2-AC5/**`（回归搬运后 restore）、`tauri.conf.json`。

## 5. 释放检查单（协议 §3.2）

- [x] 依赖 M2-AC5 `done` @9db08dc7
- [x] 用户裁决在案（§1）+ 释放侦察实证（§2）
- [x] Owner/Reviewer/Integrator 指定，Owner≠Integrator
- [x] base/branch/worktree 冻结；允许路径两级具体化
- [x] AC 机器可验证；无阈值虚设；NOT_RUN 口径预声明
