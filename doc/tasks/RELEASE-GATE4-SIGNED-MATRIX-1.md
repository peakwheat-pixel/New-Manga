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
| AC3 | **MET** | 先卸载旧安装（ExitCode 0，程序目录/卸载项清空、数据根不变）→ 静默安装 **ExitCode 0**（35.1 s）；程序目录 **1,040 文件 / 827,026,762 B**；安装后 `app\NewManga.App.exe` 37,344,576 B / sha256 `c2bf9265…` 与 stage **逐字节相同**；HKCU 卸载项（New Manga / 0.1.1 / UninstallString / InstallLocation）齐全。**Start Menu 证据补正（reviewer-g4 P1-02）**：原日志写「0 项」是采集脚本过滤串漏了空格（实际目录名 `New Manga`）；正确证据在 `ac5-upgrade-rollback-real.log`——`New Manga.lnk` 2,304 B + `卸载 New Manga.lnk` 1,279 B，且 `ac6-uninstall.log` 证明卸载后目录被清理 |
| AC4 | **MET** | 从**安装后的 exe** 四页全部到达并实拍：资料柜（作品卡+页列表）→ 工位（页面预览 1200×1660、`01/08`）→ 控制台（9 分区）→ 阅读器（F11 沉浸）；三次空格切换均由 UI Automation `Invoke()` 按钮完成，返回名 `工位空间`/`控制台空间`/`资料柜空间`、阅读按钮 `阅读` |
| AC5 | **MET（真实跨版本，已按 reviewer-g4 P1-01 重做）** | 用**真实历史 0.1.0 包**（`task-envs/GATE4-PAGES-UPGRADE-1/out-0.1.0`，652,164,075 B / `1d573ab4…`）：装 0.1.0（app exe **99,554,850 B / `a3ec2133…`**，程序目录 1,038 文件 / 889,400,438 B）→ **覆盖安装 0.1.1**（app exe **37,344,576 B / `c2bf9265…`**，1,040 文件 / 827,026,762 B）→ **卸载后重装 0.1.0**（app exe 回到 `a3ec2133…`，与首次**完全相同**）；五次安装/卸载全部 **ExitCode=0**；数据根五步全程 **530 文件 / 684,197,540 B**。app 二进制**确实不同**（99.5 MB 旧构建 vs 37.3 MB 单文件构建），不是只改版本号 |
| AC6 | **MET** | 静默卸载 **ExitCode 0**（0.6 s）；程序目录/HKCU/Start Menu **全部清理**；数据根 **530 文件 / 684,197,540 B**，逐文件 sha256 比对：**丢失 0 / 新增 0 / 变化 0** |
| AC7 | 待复核 | 下面「边界」段自陈；`Technical Gate` 与条件 4 的关闭结论**不在本轮宣布** |

**边界（AC7 自陈）**：
- 全部产物在 `G:\CODEX\New Manga.workspace\`；仓库内只提交**截图（JPG）与文本日志**，未提交安装包二进制。
- 本轮**不宣布**条件 4 通过，也不动 `Technical Gate`；须先由独立上下文复核者核过这些证据。
- 条件 5（质量基线）与本卡无关，未被本轮影响。
- 测试机现状：**已卸载**（AC6 需要），机器上没有残留安装；如需使用请重新运行 setup.exe。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| EV-G4-01 | AC1 环境与包冻结 + AC2 未签名披露 | verification/RELEASE-GATE4-SIGNED-MATRIX-1/ac1-environment-and-package.log | 12bb456fa | 473f06b1fef0c4a04388fe339334015a56059ff66ca1bac5178cc6823286c773 | CANONICAL | BLOB |
| EV-G4-02 | AC3 干净安装（ExitCode 0 / 1,040 文件 / exe 逐字节同 stage） | verification/RELEASE-GATE4-SIGNED-MATRIX-1/ac3-clean-install.log | 12bb456fa | 7c72e5762f34c90febf51752d243803a7a3aee4989a4ceab9bb65f0e7d63b9fc | CANONICAL | BLOB |
| EV-G4-03 | AC4 四页可达说明 | verification/RELEASE-GATE4-SIGNED-MATRIX-1/ac4-four-pages.log | 12bb456fa | 6af1db0f1076d035ba49115360e21cf18b327dfadbb8340a8e6f5690663f1494 | CANONICAL | BLOB |
| EV-G4-04 | AC4 资料柜实拍 | verification/RELEASE-GATE4-SIGNED-MATRIX-1/ac4-page1-bookshelf.jpg | 12bb456fa | c1a44f3f31ec2aca8003ebf68f3f454a5513054f48ba03b0d971a24036f62660 | CANONICAL | BLOB |
| EV-G4-05 | AC4 工位实拍 | verification/RELEASE-GATE4-SIGNED-MATRIX-1/ac4-page2-workbench.jpg | 12bb456fa | 8df06f62f00d98ea3b9fe1f2ca44556080fd647f4ef8385623a13620f63cd3b5 | CANONICAL | BLOB |
| EV-G4-06 | AC4 控制台实拍 | verification/RELEASE-GATE4-SIGNED-MATRIX-1/ac4-page3-settings.jpg | 12bb456fa | 10761638af40fb86b12edaf2e4a2f90002e1a8acb2825053cdd01a5f855a4b9f | CANONICAL | BLOB |
| EV-G4-07 | AC4 阅读器实拍 | verification/RELEASE-GATE4-SIGNED-MATRIX-1/ac4-page4-reader.jpg | 12bb456fa | 0de8c1d72d724f8a537d1ee93bc8bf013a40e58a25d69896486c25ffb945814d | CANONICAL | BLOB |
| EV-G4-08 | AC5 升级与真回退 | verification/RELEASE-GATE4-SIGNED-MATRIX-1/ac5-upgrade-rollback.log | 12bb456fa | cc9f781fd13995aa024e25ab984bbf3bffe75f9161d9cd60b5b48030d6bb2828 | CANONICAL | BLOB |
| EV-G4-09 | AC6 卸载与数据根零变化 | verification/RELEASE-GATE4-SIGNED-MATRIX-1/ac6-uninstall.log | 12bb456fa | a2896e78931ef4c87b109c3217dc95b9e830d160aa69239c93408a781414fc41 | CANONICAL | BLOB |
| EV-G4-10 | AC6 卸载前数据根逐文件清单（530 文件） | verification/RELEASE-GATE4-SIGNED-MATRIX-1/ac6-dataroot-before.json | 12bb456fa | 5cdd21212aef93a26c29aa935d3559e32002fa1bbb7504e70ded4898883e3ac4 | CANONICAL | BLOB |

## 2026-11-18 复核处置与 limitation（reviewer-g4，P0=0 / P1=2 / P2=7）

报告：`doc/reviews/RELEASE-GATE4-MATRIX-REVIEW-2026-11-18.md`。

- **P1-01（已修，重做 AC5）**：原 AC5 用的「0.1.0」是同日同源重构包，其 app 仍自报 `FileVersion 0.1.1.0`、`ProductVersion 0.1.1+292f2e77…` ⇒ 只验证了**安装器级**回退。
  已改用**真实历史 0.1.0 包**（`1d573ab4…`，app exe 99,554,850 B / `a3ec2133…`）重跑，app 二进制与当前 0.1.1（37,344,576 B / `c2bf9265…`）**确实不同**，回退后 exe 与首次 0.1.0 一致。
- **P1-02（已修，补正证据）**：AC3 日志的 `Start Menu 项: 0` 是采集脚本过滤串漏空格所致；正确证据（两个 `.lnk` + 字节 + sha256）见 `ac5-upgrade-rollback-real.log`，AC3 日志已**追加**更正说明（原字节保留）。
- **P2 处置**：P2-01（AC6 未写明卸载的是 0.1.0）/P2-02（JSON 是 AC1 安装前基线而非卸载前清单）——见下方 limitation；P2-03（测试要求表 NOT_RUN）如实保留；P2-04（截图无版本号）已在本段说明：**截图证明的是"页面可达"，不承担版本标识职责**，版本由注册表与 exe 指纹证明。

### Limitations（关闭条件 4 时必须一并登记）

1. **单机、非全新 VM、无快照**：全部在本机（HOME-MY，Win11 10.0.26300）执行；没有干净 VM/快照，"干净"是**先卸载到 0 文件**达成的，不是镜像级干净。
2. **用户数据根是既有真实数据**（530 文件 / 684,197,540 B），不是新建空库；因此验证的是"卸载/升级**不动**既有数据"，未验证"空数据根首次安装"。
3. **AC5 只覆盖 0.1.0 ↔ 0.1.1 两版**，未覆盖更早版本或跨多个大版本的升级链；历史 0.1.0 包属旧构建（base 变体），升级到 models 变体后文件数 1,040 与干净安装一致，但**未逐一比对每个文件来源**。
4. **未签名**（用户裁决不需要）；SmartScreen 提示未在截图中复现。
5. **AC4 用隔离数据根副本**，未在真实用户数据根下走四页。
