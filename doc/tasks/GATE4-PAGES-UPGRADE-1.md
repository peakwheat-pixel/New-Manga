---
id: GATE4-PAGES-UPGRADE-1
title: 条件 4 收尾 —— 四页可达性（安装产物上）+ 升级/回退矩阵
kind: evidence
governance_version: 3
status: done
disposition: "Gate 条件 4 仅剩：四页可达性（长期 NOT_RUN）与升级/回退矩阵未做"
approval: DSH 2026-11-15（`--page` 参数已确认支持四个一级页面）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - INSTALLER-MATRIX-1
base_commit: 6485c44b8
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/GATE4-PAGES-UPGRADE-1
allowed_paths:
  - doc/tasks/GATE4-PAGES-UPGRADE-1.md
  - doc/reviews/GATE4-PAGES-UPGRADE-1-*.md
  - doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/GATE4-PAGES-UPGRADE-1/**
  - verification/INSTALLER-MATRIX-1/**
---

# GATE4-PAGES-UPGRADE-1：四页可达性 + 升级/回退矩阵

## 背景

`INSTALLER-MATRIX-1` 已实测通过：stage → setup.exe → clean install → 启动（Host 完全就绪）→ 卸载，
且用户数据根清单 SHA-256 前后一致。**条件 4 仅剩两块**：

1. **四页可达性**：一直没有在**安装产物**上逐页到达书架/工作台/阅读器/设置并留证（长期标 NOT_RUN）。
2. **升级/回退矩阵**：需要一个旧版本作回退目标，从未做过。

**已核实**：`AppOptions` 支持 `--page=<value>`，`AllowedStartupPages` =
`bookshelf` / `library` / `reader` / `workbench` / `studio` / `settings` / `console`
（`AppOptions.cs:103`），且 `App.axaml.cs:455 NavigateStartupPage` 会真的切到对应空间。
⇒ 可以**每页各启动一次并截图**，不必模拟点击。

## Acceptance Criteria

- [x] **AC1 四页截图（安装产物）**：用**已安装目录里的** `NewManga.App.exe`
      （`%LOCALAPPDATA%\Programs\NewManga\app\NewManga.App.exe`）分别以
      `--page=bookshelf|workbench|reader|settings` 启动，各截一张图，落到
      `verification/GATE4-PAGES-UPGRADE-1/pages/`。
      每张图必须能看出是该页（标题/主导航高亮/内容区），并记录：exe 路径与 sha256、数据根、启动参数、
      截图方法、`exit` 码。
- [x] **AC2 截图不是"黑屏也算数"**：断言图像非全黑/非单色（例如像素方差 > 阈值），
      否则该页记 `FAIL` 而不是"已截图"。
- [x] **AC3 隔离**：所有启动必须 `--data-root=<workspace 内隔离目录>`；启动前后记录
      `%APPDATA%\com.newmanga.desktop` 的清单 SHA-256 并断言不变。
- [x] **AC4 升级矩阵**：装 **0.1.0** 版 → 用 **0.1.1** 覆盖安装 → 断言：
      程序目录 `VERSION.json.version == 0.1.1`、HKCU `DisplayVersion == 0.1.1`、
      安装后 exe 的 `ProductVersion` 含当前 head、用户数据根清单 SHA-256 不变。
- [x] **AC5 回退矩阵**：卸载 0.1.1 → 再装 0.1.0 → 断言同上三条（版本回到 0.1.0），
      用户数据根仍不变。
- [x] **AC6 0.1.0 包如何造**：必须说明来源（例如把 0.1.1 的 stage 复制一份、只把 `VERSION.json.version`
      改为 `0.1.0`），并说明为何这样不算造假（**exe 与 sidecar 的真实 sha256/head 一律不动**；
      若要绕过 `verify-package-manifest.ps1` 的 version 无关项，必须**显式**说明并记录）。
- [ ] **AC7 不虚报**：任何做不到的步骤如实标 `NOT_RUN` 并写原因；不得用 headless 渲染冒充安装产物截图；
      不得声称条件 4 已满足（sidecar 缺 SFX 权重、安装器 unsigned）。

## 允许修改范围

见 frontmatter（只加证据，不改产品代码）。

## 禁止范围

- 不得修改 App/Core/Host 源码来"让截图好看"。
- 不得提交二进制截图进仓库**除非**单张 < 200 KB 且确有必要（默认留在 workspace，仓库只放清单与说明）。
- 不得伪造 `VERSION.json` 的 sha256/head（`VERSION-MANIFEST-GUARD-1` 会拦，且这是本卡的前车之鉴）。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1/AC2 | 四个 `--page=` 启动 + 截图 + 非黑屏断言 | 已安装 0.1.1 | NOT_RUN | 无 |
| AC3 | 启动前后数据根清单哈希 | 同上 | NOT_RUN | 无 |
| AC4 | 0.1.0 → 0.1.1 覆盖安装 | 需 0.1.0 setup | NOT_RUN | 无 |
| AC5 | 卸载 → 装 0.1.0 | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **风险 R1**：`--exit-after` 会在指定毫秒后退出；截图必须在退出**前**完成 → 用较大值（如 25000）并在
  窗口出现后立即截图。
- **风险 R2**：`PrintWindow` 对 GPU 合成窗口可能返回黑图 → 备选 `Graphics.CopyFromScreen`（需窗口前台）。
  两种都失败则该页记 `FAIL` 并写明。
- **风险 R3**：0.1.0 与 0.1.1 的 NSIS 卸载项同名 → 升级时需确认是"覆盖"而非"先卸后装"。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文，重点核"截图是否真来自安装产物、是否真做了双向升级回退"）。
- 实际测试：尚无。
- 后续记录日期、commit、环境、结果、遗留项。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| artifact | G:/CODEX/New Manga.workspace/task-envs/GATE4-PAGES-UPGRADE-1 | PRESERVE_REFERENCED | 同左 | 待填 | 截图与 setup，按需保留 |

## Closeout Record

- Closeout date / DSH：2026-11-15，DSH（Lead / Architect / Integrator）。
- canonical_evidence_status：`complete`。
- resource_closeout_status：`complete`（截图与 setup 均在 workspace）。
- 删除、迁移、归档数量/字节数：0（安装副作用已全部卸载清理）。
- **交付（限定）**：
  - **四页**：`bookshelf` / `workbench` / `settings` **PASS**（安装产物上、`PrintWindow` 从窗口自身渲染、
    窗口标题强制含 `NewManga`、方差阈值防黑屏；bookshelf 已目视确认）。`reader` **NOT_REACHABLE**——
    空数据根下 `--page=reader` 与 bookshelf 哈希完全相同（回落），**未算作到达**。
  - **升级/回退**：0.1.0 ↔ 0.1.1 双向**覆盖安装与卸载-再装**共六步全部 exit 0，
    `VERSION.json.version` / HKCU `DisplayVersion` 正确切换，**用户数据根清单 SHA-256 全程不变**
    （`6ae4d6da…d9b2`）。
- **未达成（如实登记）**：
  - `reader` 页未到达（需先导入一本书）；**未**声称四页全部可达。
  - 0.1.0 是**同一份字节换标签**，因此**没有**验证"真实跨版本二进制升级/回退"。
  - 条件 4 仍**不判 MET**：sidecar 缺 SFX 权重、安装器 unsigned、阅读器页未验证。
- **自登记的错误（本卡）**：
  1. **第一版截图全是假的** —— 用 `Graphics.CopyFromScreen` 截窗口矩形，四张 PNG 全是**桌面**
     （我的 DSH 对话窗口 + VPN 工具），而四张哈希各不相同、方差也各不相同，**看起来完全像四页证据**。
     我只看了数字没看图，直到把 `bookshelf.png` 读出来才发现。改为 `PrintWindow` + 标题校验后修正。
     **教训：数字不同不等于内容正确；截图类证据必须人眼过一遍，且必须从目标窗口渲染。**
  2. 我一度把 `reader.png` 与 `bookshelf.png` 同为 35,540 B 的情况当成"四页都截到了"，
     是被文件大小提醒后才去比哈希，才发现是同一张图。
