---
id: INSTALLER-MATRIX-1
title: 用旧 sidecar 跑通安装/卸载矩阵（条件 4 的机制验证）
kind: evidence
governance_version: 3
status: closed_with_limitations
disposition: "Gate 条件 4：setup.exe + clean install + 启动 + 卸载 + 用户数据根保护。AC1–AC6 已有实测证据（见 verification/INSTALLER-MATRIX-1/README.md）；AC7 四页可达性仍 NOT_RUN。"
approval: DSH 2026-11-15（makensis 已具备；sidecar 沿用 2026-10-23 版并标注 E-2）
suggested_owner: DSH
owner: DSH
reviewer: reviewer-inst（DSH 子 agent，独立上下文，未参与实现；2026-11-17 收口复核）
depends_on:
  - RELEASE-PACKAGE-PROBE-1
base_commit: fe7da5d92
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: 998e04ae4
canonical_evidence_status: complete
resource_closeout_status: complete
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

> ## ★ 状态澄清（2026-11-15，DSH）—— 含我自己的两次失误
>
> **本卡的表在很长时间里全部写着 `NOT_RUN`，但实物证据显示 AC1–AC6 其实已经跑过。**
> 依据：`verification/INSTALLER-MATRIX-1/README.md`（**r1 REJECT 后重做版**，所有数字为重做后实测值）。
>
> | AC | 真实结果（来自证据 README） |
> |---|---|
> | AC1 stage | ✅ **848.15 MB / 1037 files** |
> | AC2 `VERSION.json` | ✅ `repo_head` 用 exe 内嵌 `ProductVersion` 自证 |
> | AC3 `setup.exe` | ✅ `NewManga-0.1.1-setup.exe` **621.9 MB**，sha256 `0c041599…58f06`，`makensis v3.13` |
> | AC4 clean install | ✅ `/S` exit 0；848 MB；HKCU `New Manga 0.1.1`；Start Menu 两个快捷方式 |
> | AC5 安装后启动 | ✅ exit 0；`ProductVersion = 0.1.1+71cecb95a…`；`core_service ready` + `host_bridge ready` + `self-check Passed` |
> | AC6 卸载 | ✅ `/S` exit 0；程序目录/HKCU/StartMenu 全清理；**用户数据根清单 SHA-256 前后完全一致** `6ae4d6da…46d9b2`（532 文件） |
> | **AC7 四页可达性** | ❌ **NOT_RUN**（未在打包产物上逐页导航；**未用 headless 证据冒充**） |
> | AC8 不虚报 | ✅ 产物全在 workspace；仓库仅文本 |
>
> **⇒ 真实状态：AC1–AC6 已通过，AC7 未做。所以本卡是 `in_progress`，不是 `done`。**
>
> ### ★ 我在同一轮里的两次失误（原样登记）
> 1. **第一次**：我看到本卡表格全是 `NOT_RUN`，就把 `status: done` 直接改成 `in_progress`，
>    并写下"七项 AC 一项都没有实测记录，却被标成 done"——**这是错的**。
>    我没有查 `verification/INSTALLER-MATRIX-1/` 的实物证据就下了结论。
> 2. **第二次**：发现实物证据后，我才知道 AC1–AC6 真做过。
>    **正确做法本应是先读证据、再改状态。**
>
> **⇒ 结论没变（`in_progress` 是对的，因为 AC7 未做），但我的理由是错的，过程是错的。**
> **这正是本项目反复出现的模式：先下结论，后查证据。**


## 目标

条件 4 要求"对当前固定产品 commit 生成并固定 Windows 包，完成 clean install、启动、升级/回退、
四个一级页面可达性与卸载矩阵"。

`RELEASE-PACKAGE-PROBE-1` 已证明：**包能构建、能启动、Host 就绪**（`git_head` 绑定当前 head），
且 `makensis v3.13` 与 `.nsi` 均具备。本卡补上**安装器与 install/uninstall 矩阵**。

**sidecar 约束**：仍用 **2026-10-23 的旧 sidecar**（重建受 `yolo11s-seg.onnx` 缺失阻塞，已登记）。
因此在 `VERSION.json` 中**必须如实标注**该 sidecar 的真实来源与构建时间 —— **不得沿用模板里的旧值**。

## Acceptance Criteria

- [x] **AC1 stage 就绪**：以 `AGPL-RELEASE-1` 的 stage 为**结构模板**构建新 stage： <<MET>>
      `app/NewManga.App.exe` = 当前 head 的 publish 产物（sha256 记录）；
      `app/core-sidecar` = `apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar`；
      许可/NOTICE 文件齐全。
- [x] **AC2 VERSION.json 真实**：`sidecar_build.core_service_sha256`/`core_service_bytes`/ <<MET>>
      `core_service_built_at_utc`/`repo_head` 必须与**实际使用的** sidecar 与 head 一致；
      `app` 的 exe sha256/尺寸同样记录。**不得照抄模板旧值**。
- [x] **AC3 setup.exe**：`build-installer.ps1` 产出 `NewManga-<ver>-setup.exe`，记录尺寸与 sha256、NSIS 日志。 <<MET>>
- [x] **AC4 clean install**：`/S` 静默安装 → 程序出现在 `%LOCALAPPDATA%\Programs\NewManga`， <<MET>>
      HKCU 卸载项存在，Start Menu 快捷方式存在（若 `.nsi` 声明）。
- [x] **AC5 安装后启动**：运行**安装目录里的** exe，断言窗口出现且 Host 就绪（用与 publish 冒烟相同的判据）。 <<MET>>
- [x] **AC6 卸载**：静默卸载 → 程序目录与 HKCU 项被清理； <<MET>>
      **`%APPDATA%\com.newmanga.desktop` 用户数据根未被触碰**（安装前后记录其文件清单+哈希对比）。
- [ ] **AC7 四页可达性（打包产物上）**：至少用截图证明四个一级页面（书架/工作台/阅读器/设置）可从安装产物到达； <<PARTIAL: 未在打包产物上逐页导航（NOT_RUN）；不以 headless 结果冒充；见 §限制 L-IM-2>>
      若做不到（例如需要真实交互），**如实标 NOT_RUN** 并说明原因，不得用 headless 结果冒充。
- [x] **AC8 不虚报**：产物与安装全部在 workspace / `%LOCALAPPDATA%`，**不提交二进制**； <<MET>>
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
| EV-IM-01 | AC1–AC6 / 证据 | verification/INSTALLER-MATRIX-1/build-info.republished.json | 998e04ae4 | 6dac2fcc0df77ac546ccdd8fc8b3b4acf3a58d0ecc98a825edad23555b045ac5 | CANONICAL | BLOB |
| EV-IM-02 | AC1–AC6 / 证据 | verification/INSTALLER-MATRIX-1/host.log.republished-run | 998e04ae4 | 277829807d0533fcd77b4570d90e0aea092e9944a80264105e410781937ad30b | SOURCE_PIN | BLOB |
| EV-IM-03 | AC1–AC6 / 证据 | verification/INSTALLER-MATRIX-1/publish-head/build-singlefile.log | 998e04ae4 | ab0e416da6a80b117ee3ac68433d0fa26452fcd487217034a4af08e02c454f68 | SOURCE_PIN | BLOB |
| EV-IM-04 | AC1–AC6 / 证据 | verification/INSTALLER-MATRIX-1/publish-head/manifest-singlefile.json | 998e04ae4 | 90b8897aeec19c6fe79edb19aefaebc90a6b5c56138469262591db357d898116 | SOURCE_PIN | BLOB |
| EV-IM-05 | AC1–AC6 / 证据 | verification/INSTALLER-MATRIX-1/publish-head/manifest-summary.json | 998e04ae4 | 2de165cc16675a633382c009535b160ae3aa9f27824a60d95b2f2712877088ef | SOURCE_PIN | BLOB |
| EV-IM-06 | AC1–AC6 / 证据 | verification/INSTALLER-MATRIX-1/publish-head/published-singlefile.png | 998e04ae4 | 149f79fca4832de8fa6c5422694de7278fdb248319f0aae637762f1a50bedb22 | SOURCE_PIN | BLOB |
| EV-IM-07 | AC1–AC6 / 证据 | verification/INSTALLER-MATRIX-1/publish-head/smoke-singlefile.json | 998e04ae4 | 8cd0ab1f78d94661a92152600af2d41ee6a95510db9d8950ffbafbebfadea636 | SOURCE_PIN | BLOB |
| EV-IM-08 | AC1–AC6 / 证据 | verification/INSTALLER-MATRIX-1/publish-manifest.republished.json | 998e04ae4 | 90b8897aeec19c6fe79edb19aefaebc90a6b5c56138469262591db357d898116 | SOURCE_PIN | BLOB |
| EV-IM-09 | AC1–AC6 / 证据 | verification/INSTALLER-MATRIX-1/README.md | 998e04ae4 | f80bdcd4ef837ec3c7815594b5531b97af8dd05286a479cb0678945923ef27ef | CANONICAL | BLOB |
| EV-IM-10 | AC1–AC6 / 证据 | verification/INSTALLER-MATRIX-1/startup.log.republished-run | 998e04ae4 | d391ca4e76bebb0c260c32c60311491262cbd3fafcf653d9f9d89b10cdc4d5e3 | SOURCE_PIN | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| artifact | G:/CODEX/New Manga.workspace/task-envs/INSTALLER-MATRIX-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/INSTALLER-MATRIX-1 | G:/CODEX/New Manga.workspace/task-envs/INSTALLER-MATRIX-1/RESOURCE-MANIFEST.json | 7 目录 / 1,068 文件 / 2,194,905,712 B（stage + setup.exe + smoke + out 系列）；manifest sha256 `c94feccb…`；产物全部在 workspace，未入仓；实测存在，未清理 |

## Closeout Record（2026-11-17，DSH 执行 Codex Q3 裁定）

- canonical_evidence_status：`complete`（10 行 BLOB，基准 `998e04ae4`）；resource_closeout_status：`complete`。
- 删除、迁移、归档数量/字节数：**0**（全部产物原地位于 workspace）。
- **收口依据**：`doc/reviews/CODEX-RULING-CORE-ENV2-FEA11-GATE-2026-11-17.md` Q3（条件 4 段）。本卡是**旧 sidecar 条件下的机制验证**卡，
  AC1–AC6 已有实物证据（stage 848.15 MB / 1037 files；setup.exe 621.9 MB sha256 `0c041599…`；clean install / 启动 / 卸载全 exit 0；
  用户数据根 532 文件清单 SHA-256 前后一致 `6ae4d6da…`）；**AC7 四页可达性仍 `NOT_RUN`**。
- **限制清单**：
  1. **L-IM-1｜旧 sidecar**：本卡全程使用 2026-10-23 的旧 sidecar（E-2 时代），不代表当前 sidecar 的行为。
  2. **L-IM-2｜AC7 NOT_RUN**：未在打包产物上逐页导航四个一级页面；Gate 映射 Review 另称「安装产物四页 5/5」，**两者证据不一致，未对齐**（可能不是同一安装包/head），不得据此把本卡 AC7 改成 MET。
  3. **L-IM-3｜无签名**：产物**没有 Authenticode 签名**，条件 4 的签名要求未满足。
  4. **L-IM-4｜跨版本升级/回退未证明**：此前「回退」只改版本标签，完整跨版本矩阵未做。
  5. **L-IM-5｜不宣称条件 4 通过**：本卡只是机制验证；完整签名 + 真实安装矩阵另立 `RELEASE-GATE4-SIGNED-MATRIX-1`（proposed）。
- **边界**：`Technical Gate=NOT_SATISFIED` 不变；不得据此宣称条件 4 满足。

## 2026-11-17 复核登记（reviewer-inst，ACCEPTED_WITH_FINDINGS，P0=0 / P1=2 / P2=4）

报告：`doc/reviews/INSTALLER-MATRIX-1-CLOSEOUT-REVIEW-2026-11-17.md`。两条 P1 已由 DSH 独立复核实证，作为**追加限制**登记；**不改 AC7**、不重跑矩阵、不宣称条件 4。

- **L-IM-6｜包内 `package-manifest.json` 与包不同步（P1）**：`stage/NewManga-0.1.1-win-x64/package-manifest.json`（381,448 B）仍写
  `version: 0.1.0`、`variant: base`、`models_bundled: false`，而同一 stage 目录名为 `0.1.1`、且含 3 个 ONNX 权重共 **632,552,582 B**（DSH 实测）。
  该 manifest 随安装包落盘 ⇒ 用户看到的版本/内容描述与实物不一致。**未修**（`packaging/**` 在本卡禁止范围内），需另立打包修复项。
- **L-IM-7｜许可证声明与实物不一致（P1）**：包为 `variant=base` / `GPL-3.0-or-later`，却内置 632,552,582 B 权重；
  随包 `NOTICE.md` / `LICENSE_AUDIT.md` 仍写「base 不含权重、models=AGPL」，且 rtdetr/OCR 权重上游许可「待核实」。
  **未修**（属许可裁决 + 打包变更），需 DSH/用户就随包权重许可作出书面决定后才能改。

复核同时确认：**AC7 仍为 `[ ]` + `<<PARTIAL: …NOT_RUN…>>`**（未被改成 MET）；AC1–AC6 数字与证据一致；资源 manifest sha256 `c94feccb…` 一致。

## 2026-11-17 追加登记：加严后的发布护栏会**拒绝**本卡 stage

`INSTALLER-METADATA-CONSISTENCY-1` 给 `tools/ci/verify-package-manifest.ps1` 增加了 `package-manifest.json` 交叉校验后，
对本卡使用的 stage（`...\INSTALLER-MATRIX-1\stage\NewManga-0.1.1-win-x64`）实测 **FAILED with 5 problem(s) / EXIT=1**：

1. `package-manifest.json` 版本 `0.1.0` ≠ `VERSION.json` 的 `0.1.1`；
2. `models_bundled: false` ≠ 实物 3 个 onnx；
3. `models_bytes: 0` ≠ 实物 632,552,582 B；
4. manifest 列 1,968 个文件，stage 实有 1,036（排除 manifest 自身）；
5. manifest 列出 1,041 个 stage 里**不存在**的条目（含 `app/core-sidecar/python/*`）。

**这意味着**：该 stage **不是 `package.ps1` 的干净输出** —— `package-manifest.json` 的 mtime 是 **2026-10-28**（stage 其余为 11-15），
根 `VERSION.json` 与 `app/VERSION.json` **哈希不同**（脚本本应逐字节复制），且 manifest 描述的是另一套含 `python/*` 的布局。

- 本卡的 **AC1–AC6 结论不变**（安装/启动/卸载矩阵当时实测通过，资源和数据一致性证据有效），
  但「包内元数据描述与实际一致」这一属性**不成立**，其 `L-IM-1..7` 之外再补一条：
- **L-IM-8｜stage 元数据不自洽**：该 stage 的 `package-manifest.json` 与 `VERSION.json`/实物不一致（见上面 5 条），
  加严后的护栏会拒绝它；**不覆盖**该 stage（历史证据字节保留），修复与复现见 `INSTALLER-METADATA-CONSISTENCY-1`。
- **不改变**：条件 4 仍归 `RELEASE-GATE4-SIGNED-MATRIX-1`（proposed）；不宣称签名或 Gate 通过。

## 2026-11-17 追加登记（二）：ZCode 裁定 —— 许可声明非法、本卡 stage 不是条件 4 证据

裁定书：`doc/reviews/ZCODE-RULING-INSTALLER-LICENSE-2026-11-17.md`（ZCode，全文逐字落盘，DSH 全文采纳）。

- **L-IM-9｜许可声明与实物不相容（P0 发布阻塞）**：`variant=base` + `license=GPL-3.0-or-later` 却内置 **632,552,582 B** 权重；
  按裁定书 R1–R4 落在 **R4**（权重台账三项均「待核实」）⇒ **该声明非法**，合法出口只有「保守声明 AGPL-3.0」或「移除权重回归 base」。
  处置卡：`LICENSE-VARIANT-DECLARATION-1`（`blocked`，等用户选向）。
- **L-IM-10｜本卡 stage 不是条件 4 证据**：裁定 Q3 = **No** —— 条件 4 要求证据绑定安装包 hash，而 Q1/Q2 的修复必然重打包；
  旧矩阵对最终包无证据效力。⇒ 条件 4 的等待项从「缺证书」扩展为「**先产出合规新包 → 再签名 → 再跑矩阵**」。
- 本卡 **AC1–AC6 的矩阵观察仍然有效**（安装/启动/卸载/数据保护在当时的字节上确实通过），但**不能**作为发布证据；
  与 L-IM-8（元数据不自洽）合并看：该 stage **不可发布、不可作 Gate 证据**，由加严后的护栏负责拒绝（实测 8 条 FAIL）。
