---
id: RELEASE-GATE4-SIGNED-MATRIX-1
title: Gate 条件 4 —— Authenticode 签名 + 真实 Windows 安装矩阵
kind: infra
governance_version: 3
status: proposed
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

- [ ] **AC1 环境与凭据冻结**：记录真实 Windows 环境（版本/构建/快照 ID）、安装包 hash、签名证书身份（Subject/Thumbprint/颁发者）与时间戳服务器；凭据不可得时**停止并如实登记**，不得用自签名冒充发布签名。
- [ ] **AC2 签名可验证**：对 `setup.exe` 与 `NewManga.App.exe` 执行 Authenticode 签名，`Get-AuthenticodeSignature` 结果为 `Valid`，记录证书链、时间戳与验证输出；未签名/无效一律记 `NOT_RUN` 或失败。
- [ ] **AC3 clean install**：在干净环境执行静默安装，记录 exit code、安装后文件清单与哈希、HKCU 卸载项、Start Menu 快捷方式。
- [ ] **AC4 四页可达（打包产物）**：从**安装后的 exe** 依次到达书架 / 工作台 / 阅读器 / 设置，用截图或可核验的 UI 自动化证据证明；不得用 headless 渲染冒充真实窗口（Codex Q3 条件 3 同理）。
- [ ] **AC5 跨版本升级与回退**：安装上一版本 → 覆盖安装当前版本 → 回退到上一版本，逐步记录版本号、文件哈希与用户数据根清单；**只改版本标签的“回退”不算**。
- [ ] **AC6 卸载与用户数据保护**：静默卸载后程序目录/HKCU/StartMenu 清理，`%APPDATA%\com.newmanga.desktop` 文件清单+哈希前后一致。
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
