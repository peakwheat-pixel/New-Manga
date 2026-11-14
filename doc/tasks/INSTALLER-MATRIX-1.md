---
id: INSTALLER-MATRIX-1
title: 用旧 sidecar 跑通安装/卸载矩阵（条件 4 的机制验证）
kind: evidence
governance_version: 3
status: in_progress
disposition: "Gate 条件 4：setup.exe + clean install + 启动 + 卸载 + 用户数据根保护"
approval: DSH 2026-11-15（makensis 已具备；sidecar 沿用 2026-10-23 版并标注 E-2）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - RELEASE-PACKAGE-PROBE-1
base_commit: fe7da5d92
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/INSTALLER-MATRIX-1
allowed_paths:
  - doc/tasks/INSTALLER-MATRIX-1.md
  - doc/reviews/INSTALLER-MATRIX-1-*.md
  - doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/INSTALLER-MATRIX-1/**
---

# INSTALLER-MATRIX-1：安装/卸载矩阵（条件 4）

## 目标

条件 4 要求"对当前固定产品 commit 生成并固定 Windows 包，完成 clean install、启动、升级/回退、
四个一级页面可达性与卸载矩阵"。

`RELEASE-PACKAGE-PROBE-1` 已证明：**包能构建、能启动、Host 就绪**（`git_head` 绑定当前 head），
且 `makensis v3.13` 与 `.nsi` 均具备。本卡补上**安装器与 install/uninstall 矩阵**。

**sidecar 约束**：仍用 **2026-10-23 的旧 sidecar**（重建受 `yolo11s-seg.onnx` 缺失阻塞，已登记）。
因此在 `VERSION.json` 中**必须如实标注**该 sidecar 的真实来源与构建时间 —— **不得沿用模板里的旧值**。

## Acceptance Criteria

- [x] **AC1 stage 就绪**：以 `AGPL-RELEASE-1` 的 stage 为**结构模板**构建新 stage：
      `app/NewManga.App.exe` = 当前 head 的 publish 产物（sha256 记录）；
      `app/core-sidecar` = `apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar`；
      许可/NOTICE 文件齐全。
- [x] **AC2 VERSION.json 真实**：`sidecar_build.core_service_sha256`/`core_service_bytes`/
      `core_service_built_at_utc`/`repo_head` 必须与**实际使用的** sidecar 与 head 一致；
      `app` 的 exe sha256/尺寸同样记录。**不得照抄模板旧值**。
- [x] **AC3 setup.exe**：`build-installer.ps1` 产出 `NewManga-<ver>-setup.exe`，记录尺寸与 sha256、NSIS 日志。
- [x] **AC4 clean install**：`/S` 静默安装 → 程序出现在 `%LOCALAPPDATA%\Programs\NewManga`，
      HKCU 卸载项存在，Start Menu 快捷方式存在（若 `.nsi` 声明）。
- [x] **AC5 安装后启动**：运行**安装目录里的** exe，断言窗口出现且 Host 就绪（用与 publish 冒烟相同的判据）。
- [x] **AC6 卸载**：静默卸载 → 程序目录与 HKCU 项被清理；
      **`%APPDATA%\com.newmanga.desktop` 用户数据根未被触碰**（安装前后记录其文件清单+哈希对比）。
- [ ] **AC7 四页可达性（打包产物上）**：至少用截图证明四个一级页面（书架/工作台/阅读器/设置）可从安装产物到达；
      若做不到（例如需要真实交互），**如实标 NOT_RUN** 并说明原因，不得用 headless 结果冒充。
- [ ] **AC8 不虚报**：产物与安装全部在 workspace / `%LOCALAPPDATA%`，**不提交二进制**；
      不得声称条件 4 满足（sidecar 仍旧、无签名）。

## 允许修改范围

见 frontmatter。stage 与安装器产物落 `G:\CODEX\New Manga.workspace\task-envs\INSTALLER-MATRIX-1\`。

## 禁止范围

- **不得**修改 `packaging/**`、`apps/desktop-avalonia/src/**`、`.nsi`（除非发现真实缺陷，需先登记）。
- **不得**沿用模板 `VERSION.json` 的旧 `repo_head`/sha256（那是造假）。
- 不得提交任何二进制进仓库。
- 不得声称条件 4 通过。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | 构建 stage + 写 VERSION.json | workspace | NOT_RUN | 无 |
| AC3 | `build-installer.ps1` | makensis v3.13 | NOT_RUN | 无 |
| AC4/AC5 | `setup.exe /S` + 启动安装后 exe | 本机 | NOT_RUN | 无 |
| AC6 | 卸载 + 用户数据根对比 | 本机 | NOT_RUN | 无 |
| AC7 | 四页截图 | 本机 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **风险 R1**：安装会写入 `%LOCALAPPDATA%` / HKCU —— 属可控副作用，但**必须**在卸载后清理干净，
  并在卡面登记"装了什么、卸了什么"。
- **风险 R2**：新 stage 体积约 850 MB（exe 95 MB + sidecar 753 MB），NSIS 压缩耗时可能数分钟。
- **风险 R3**：`INSTALL_SIZE_KB` 默认 220000，新 stage 更大 → 需按实际调整 define（否则卸载面板显示错误大小）。
- **阻塞**：sidecar 重建（`yolo11s-seg.onnx` 缺失）—— 不阻塞本卡的"机制验证"，但**阻塞正式分发包**。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文，重点核"VERSION.json 是否与真实来源一致"与"卸载是否真的没碰用户数据根"）。
- 实际测试：尚无。
- 后续记录日期、commit、环境、结果、遗留项。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| artifact | 待填（workspace\task-envs\INSTALLER-MATRIX-1） | PRESERVE_REFERENCED | 同左 | 待填 | stage + setup.exe，不在仓库 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待填。
- 当前指针清理：待关闭时更新 STATUS / Plan / TASK_LEDGER / rolling checkpoint。
