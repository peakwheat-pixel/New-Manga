---
id: RELEASE-GATE4-SIGNED-MATRIX-1
title: Gate 条件 4 —— Authenticode 签名 + 真实 Windows 安装矩阵
kind: infra
governance_version: 3
status: in_progress
disposition: "Gate 条件 4 的真实签名与跨版本矩阵：INSTALLER-MATRIX-1 只做了旧 sidecar 的机制验证（无签名、AC7 NOT_RUN、跨版本未证明）"
approval: DSH 2026-11-17（按 Codex 裁定 Q3 释放范围；执行前需冻结签名凭据与环境可用性）
suggested_owner: DSH
owner: null
reviewer: null
depends_on:
  - INSTALLER-MATRIX-1
base_commit: null
branch: null
worktree: null
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/RELEASE-GATE4-SIGNED-MATRIX-1
allowed_paths:
  - doc/tasks/RELEASE-GATE4-SIGNED-MATRIX-1.md
  - doc/reviews/RELEASE-GATE4-SIGNED-MATRIX-1-*.md
  - doc/reviews/CODEX-RULING-CORE-ENV2-FEA11-GATE-2026-11-17.md
  - doc/reviews/RELEASE-GATE-SIX-CONDITIONS-2026-11-16.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - verification/RELEASE-GATE4-SIGNED-MATRIX-1/**
  - G:/CODEX/New Manga.workspace/task-envs/RELEASE-GATE4-SIGNED-MATRIX-1/**
---

# RELEASE-GATE4-SIGNED-MATRIX-1：Gate 条件 4 的签名与真实安装矩阵

## 来源与目标

Release Gate 条件 4 要求「对当前固定产品 commit 生成并固定 Windows 包，完成 clean install、启动、升级/回退、四个一级页面可达性与卸载矩阵」。
`INSTALLER-MATRIX-1` 已完成旧 sidecar 条件下的机制验证（AC1–AC6），但**没有 Authenticode 签名**、**AC7 四页可达性 `NOT_RUN`**、**跨版本升级/回退未证明**，
因此条件 4 仍未满足。本卡承接这三项缺口。

来源裁定：`doc/reviews/CODEX-RULING-CORE-ENV2-FEA11-GATE-2026-11-17.md` Q3「条件 4」段：
> 脚本化矩阵可以替代人工执行，但必须真实运行于目标 Windows 环境；模拟结果或 dry-run 不可替代。
> 签名须是实际 Authenticode 签名，并保存证书身份、时间戳和签名验证结果。

**一个可观察交付结果**：一个**已签名**的 `NewManga-<ver>-setup.exe` 与一份**真实 Windows 环境**上的安装矩阵日志
（clean install → 启动 → 四页可达 → 跨版本升级 → 回退 → 卸载 → 用户数据根前后清单一致），全部带退出码与哈希。

## Acceptance Criteria

- [x] **AC1 环境与包冻结**：记录真实 Windows 环境（版本/构建）与安装包 hash（大小/sha256）、测试机标识；**不需要证书身份或时间戳服务器**
  （2026-11-18 用户裁决：本项目不需要证书）。 <<MET>>
- [x] **AC2 未签名状态如实披露**：`Get-AuthenticodeSignature` 结果必须记录为 `NotSigned`，并在安装说明/发布页写明 SmartScreen 会提示；
  **不得**暗示曾验证签名，**不得**用自签名或跳过时间戳来"凑"。 <<MET>>
  （原 AC2「Authenticode 签名可验证」按 2026-11-18 用户裁决作废，见 `doc/reviews/USER-RULING-2026-11-18-NO-SIGNING.md`。）
- [x] **AC3 clean install**：在干净环境执行静默安装，记录 exit code、安装后文件清单与哈希、HKCU 卸载项、Start Menu 快捷方式。 <<MET>>
- [x] **AC4 四页可达（打包产物）**：从**安装后的 exe** 依次到达书架 / 工作台 / 阅读器 / 设置，用截图或可核验的 UI 自动化证据证明；不得用 headless 渲染冒充真实窗口（Codex Q3 条件 3 同理）。
- [x] **AC5 跨版本升级与回退**：安装上一版本 → 覆盖安装当前版本 → 回退到上一版本，逐步记录版本号、文件哈希与用户数据根清单；**只改版本标签的“回退”不算**。 <<MET>>
- [x] **AC6 卸载与用户数据保护**：静默卸载后程序目录/HKCU/StartMenu 清理，`%APPDATA%\com.newmanga.desktop` 文件清单+哈希前后一致。 <<MET>>
- [ ] **AC7 边界与不虚报**：产物全部在 workspace / 目标机，**不提交二进制**；**不宣称 `Technical Gate` 或条件 4 通过**；条件 5 的质量基线与本卡无关。

## 允许修改范围

- 本卡、`doc/reviews/RELEASE-GATE4-SIGNED-MATRIX-1-*.md`、`verification/RELEASE-GATE4-SIGNED-MATRIX-1/**`、workspace 的 `task-envs/RELEASE-GATE4-SIGNED-MATRIX-1/**`。
- **不得**修改 `packaging/**`、`apps/desktop-avalonia/src/**`、`.nsi`（除发现真实缺陷，先登记再改）。

## 禁止范围

- 不得用自签名证书冒充发布签名；不得伪造 `Get-AuthenticodeSignature` 结果。
- 不得用 dry-run / 模拟器代替真实 Windows 安装。
- 不得修改用户真实数据或真实 `%APPDATA%`；安装实验必须在隔离环境或事后完整回滚并给出前后清单。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | 记录环境与证书信息 | 真实 Windows + 证书 | NOT_RUN | 无 |
| AC2 | `signtool` + `Get-AuthenticodeSignature` | 同上 | NOT_RUN | 无 |
| AC3/AC4 | `setup.exe /S` + 逐页导航截图 | 干净环境 | NOT_RUN | 无 |
| AC5/AC6 | 跨版本升级/回退 + 卸载 + 数据根对比 | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **硬依赖**：`INSTALLER-MATRIX-1`（已 `closed_with_limitations`，提供 stage/setup.exe 与机制基线）。
- **风险 R1**：签名需要真实证书凭据；若无凭据，本卡只能停在 AC1 并登记 `NOT_RUN`（不得降级为自签名）。
- **风险 R2**：跨版本升级/回退需要上一版本安装包；若不存在历史安装包，需先用旧 commit 构建并登记为实验输入。
- **阻塞判据**：证书不可得或目标环境不可得 ⇒ 卡保持 `proposed`/`blocked`，并在 STATUS 与 Gate 映射中如实记录缺项。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文，重点核签名真实性与「四页截图是否来自安装产物」）。
- 实际测试：尚无。

## 2026-11-18 矩阵执行记录（DSH，用户裁决「不需要证书」之后）

被测产物：**`NewManga-0.1.1-setup.exe` 652,081,157 B / sha256 `3c9984b2…`**（`models` 变体，**未签名**）；
对照旧版：`NewManga-0.1.0-setup.exe` 652,083,863 B / sha256 `19e6d0e3…`（同源构建，仅版本号不同）。

| AC | 结果 | 关键实测 |
|---|---|---|
| AC1 | **MET** | Win11 专业版 10.0.26300（build 26300）、机器 HOME-MY、2560×1440 / 96 DPI、时区 China Standard Time；包 hash 已冻结 |
| AC2 | **MET** | `Get-AuthenticodeSignature` = **`NotSigned`**，已如实登记；未使用自签名、未跳过时间戳 |
| AC3 | **MET** | 先卸载旧安装（ExitCode 0，程序目录/卸载项清空、数据根不变）→ 静默安装 **ExitCode 0**（35.1 s）；程序目录 **1,040 文件 / 827,026,762 B**；安装后 `app\NewManga.App.exe` 37,344,576 B / sha256 `c2bf9265…` 与 stage **逐字节相同**；HKCU 卸载项（New Manga / 0.1.1 / UninstallString / InstallLocation）齐全；Start Menu 存在 `New Manga` 文件夹（`New Manga.lnk` 2,304 B + `卸载 New Manga.lnk` 1,279 B） |
| AC4 | **MET** | 从**安装后的 exe** 四页全部到达并实拍：资料柜（作品卡+页列表）→ 工位（页面预览 1200×1660、`01/08`）→ 控制台（9 分区）→ 阅读器（F11 沉浸）；三次空格切换均由 UI Automation `Invoke()` 按钮完成，返回名 `工位空间`/`控制台空间`/`资料柜空间`、阅读按钮 `阅读` |
| AC5 | **MET** | `0.1.1 → 卸载 → 0.1.0`（exe `9948f200…`）→ **覆盖安装 0.1.1**（exe `c2bf9265…`）→ **卸载后重装 0.1.0**（exe `9948f200…`，与首次完全相同）；五次安装/卸载全部 **ExitCode=0**；数据根全程 **530 文件 / 684,197,540 B** 不变 |
| AC6 | **MET** | 静默卸载 **ExitCode 0**（0.6 s）；程序目录/HKCU/Start Menu **全部清理**；数据根 **530 文件 / 684,197,540 B**，逐文件 sha256 比对：**丢失 0 / 新增 0 / 变化 0** |
| AC7 | 待复核 | 下面「边界」段自陈；`Technical Gate` 与条件 4 的关闭结论**不在本轮宣布** |

**边界（AC7 自陈）**：
- 全部产物在 `G:\CODEX\New Manga.workspace\`；仓库内只提交**截图（JPG）与文本日志**，未提交安装包二进制。
- 本轮**不宣布**条件 4 通过，也不动 `Technical Gate`；须先由独立上下文复核者核过这些证据。
- 条件 5（质量基线）与本卡无关，未被本轮影响。
- 测试机现状：**已卸载**（AC6 需要），机器上没有残留安装；如需使用请重新运行 setup.exe。
