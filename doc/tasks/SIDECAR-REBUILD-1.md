---
id: SIDECAR-REBUILD-1
title: 重建 sidecar 使命令面追上当前 head（解除 E-2）
kind: infra
governance_version: 3
status: in_progress
disposition: "E-2 根因消解；条件 3 的 100 个 skip 与条件 4 的 sidecar 均依赖此项"
approval: DSH 2026-11-15（.workspace 内构建，不动产品代码）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - RELEASE-PACKAGE-PROBE-1
base_commit: 6ad457c62
branch: main
worktree: G:/CODEX/New Manga
integration_commit: null
delivery_head: null
canonical_evidence_status: pending
resource_closeout_status: pending
evidence_dir: verification/SIDECAR-REBUILD-1
allowed_paths:
  - doc/tasks/SIDECAR-REBUILD-1.md
  - doc/reviews/SIDECAR-REBUILD-1-*.md
  - doc/reviews/MAINT-1-EXISTING-FINDINGS-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/SIDECAR-REBUILD-1/**
---

# SIDECAR-REBUILD-1：重建 sidecar 解除 E-2

## 来源与目标

E-2：仓库 sidecar 构建于 **2026-10-23**，早于多条现行命令（如 `ReorderChapters`，`83e45cfe5` 2026-11-10）。
这使得 `Host.Tests` 74 / `CoreClient.Tests` 26 / `App.Tests` 7 个需要 sidecar 的测试长期 SKIP。

`RELEASE-PACKAGE-PROBE-1` 的 r1 复核**推翻**了我"PyPI 不可达"的旧结论：`pypi.org` 直连可下载
`pyinstaller 6.22.3`。我已复现确认，并进一步验证 `requirements-build.txt` 的全部钉死版本在该源均存在，
且 `torch 2.14.0` 有 **cp314** wheel（本机 Python 3.14.6 可用）。

**一个可观察交付结果**：重建出一个新 sidecar，其 `core.ping` capabilities **包含**当前 registry 的命令
（至少包含 `ReorderChapters` 相关能力与 FEA-12 delete/trash 系列）；用它重跑三项目测试，skip 数**实测下降**。

## Acceptance Criteria

- [x] **AC1 构建环境**：在 `.workspace/task-envs/m2ac5-build` 建 venv 并安装 `requirements-build.txt`
      的全部钉死版本（源用 `-i https://pypi.org/simple`）；记录每个包的**实际安装版本**。
- [x] **AC2 构建成功**：跑 `packaging/m2ac5/build_sidecar.ps1` 产出 `core_service.exe`/`host_bridge.exe` 等；
      记录产物尺寸、sha256、构建时间与构建日志。失败则原样贴出失败原因。
- [x] **AC3 命令面核对（判别核心）**：新旧 sidecar 各跑一次 `core.ping`，**贴出 capabilities 差异**；
      必须证明新 sidecar 包含旧 sidecar 缺失的命令（尤其 `ReorderChapters` 所在命令与 FEA-12 delete/trash）。
      若没有差异，本卡**不得**声称 E-2 已解除。
- [x] **AC4 skip 下降实测**（下降已达成：skip 100→44；**但暴露 13 个失败，见 §5**）：设 `NEWMANGA_CORECLIENT_SIDECAR_DIR=<新 sidecar>` 重跑三项目全量，
      记录 pass/skip 变化，与基线（App 950/0/11、Host 321/0/74、CoreClient 186/0/26）逐项对比。
      **skip 减少必须是新 sidecar 导致**，不得通过改测试 gate 或跳过实现来达成。
- [ ] **AC5 不回归**：无夹具模式下三项目仍 0 failed；不得新增 skip/xfail、不得放宽断言。
- [ ] **AC6 零产品代码改动**：`git diff` 不触及 `src/**`、`apps/**`（构建脚本如确需调整，须单独说明并留痕）。

## 允许修改范围

见 frontmatter。构建产物落 `G:\CODEX\New Manga.workspace\task-envs\SIDECAR-REBUILD-1\`。

## 禁止范围

- 不得修改 `requirements-build.txt` 的钉死版本（除非某版本在该源确实不存在，此时停下来登记）。
- 不得把二进制产物提交进仓库。
- 不得为了让 skip 下降而修改测试的 gate 判定。
- 不得声称条件 3/4 已满足。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | venv + `pip install -r requirements-build.txt -i https://pypi.org/simple` | 网络可达 pypi.org | **63 包全部成功**（含 torch 2.14.0 cp314、pyinstaller 6.22.3） | `pip-freeze.txt`、README §1 |
| AC2 | `pwsh packaging/m2ac5/build_sidecar.ps1 -PythonExe <venv> -Force` | 上一步成功 | **PyInstaller Build complete**（753 MB、5 exe、3 ONNX、closure assertion PASS）；**最后复制 SFX 权重一步失败并 exit 1** | README §2 |
| AC3 | 新 sidecar 的 capabilities 核对 | 新 bundle | **确证**：capabilities 含 `library.delete.preview/1`、`library.trash.read/1`、`library.trash.write/1`（旧 sidecar 无） | README §3 |
| AC4 | 设夹具跑三项目全量 | 新 sidecar | CoreClient **208/4/0**（基线 186/0/26）、Host **342/9/44**（基线 321/0/74）⇒ skip **-56**、pass **+43**、**新增 13 failed** | README §4/§5 |
| AC5 | 无夹具三项目 | — | **未变**：App 950/0/11、Host 321/0/74、CoreClient 186/0/26（0 failed） | `four-pieces.log` |
| AC6 | `git status` / `git check-ignore` | — | 零产品代码改动；新 bundle 在 `apps/.../build/` 已被 `.gitignore:22` 忽略 | 同上 |

## 依赖、风险与阻塞

- **风险 R1**：torch 2.14.0 wheel 约 2 GB+，下载与安装耗时较长（可能 10–20 分钟）；用后台 job。
- **风险 R2**：PyInstaller 打包 ML 栈可能在 `torch` 动态库上出问题（历史 spec 有 `ML_HIDDENIMPORTS`）。
- **风险 R3**：新 sidecar 的 capabilities 可能仍不含某些命令（若 Core 侧本来就未实现），此时必须如实登记，
  区分"sidecar 过期"与"Core 未实现"。
- **风险 R4**：磁盘/时间。G: 余量 1216 GB，不是瓶颈。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无（须独立上下文，重点核 capabilities 差异与 skip 下降的因果关系）。
- 实际测试：尚无。
- 后续记录日期、commit、环境、结果、遗留项。
### 未关闭项（本卡**不得**收口为 done）

- **13 个失败未归因完成**：CoreClient 4 个性质清楚（"Frozen Core" 前提过期，但**不得**删除 ——
  它们守 `CORE_CAPABILITY_MISSING` fail-closed 语义，需改为显式模拟旧 capabilities）；
  Host 9 个**归因未做**，其中 `ListChapters_MatchesReaderProjection` 失败为
  `Assert.NotEmpty() Failure: Collection was empty`，属**数据/夹具层面**差异（schema v14），
  **不能**归为前提过期。
- **SFX 权重缺失**：`yolo11s-seg.onnx` 全工作区不存在，是训练产物 ⇒ 需求用户提供（goal blocked 判据）。
  只影响 `sfx_detect_probe`，不影响 `core_service`。
- **未做**：App.Tests 的 7 个 sidecar 测试、用新 sidecar 重跑 publish 冒烟（条件 4 下一步）。

### 自登记：本卡推翻的旧结论

我在此前多轮中反复以"PyPI 不可达"为由把 E-2 与条件 4 判为不可解。**这是错的**：
`-i https://pypi.org/simple` 可装全套 ML 栈（含 2 GB 级 torch），本卡已实证。
`RELEASE-PACKAGE-PROBE-1` 的 r1 复核最先指出，我当时只验证了单包；本卡验证了**完整 requirements**。

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| artifact | 待填（workspace\task-envs\SIDECAR-REBUILD-1） | PRESERVE_REFERENCED | 同左 | 待填 | 新 sidecar，供后续卡使用 |

## Closeout Record

- Closeout date / DSH：待关闭时填写。
- canonical_evidence_status：`pending`。
- resource_closeout_status：`pending`。
- 删除、迁移、归档数量/字节数：待关闭时填写；无操作填写 0。
- 未关闭项及保留原因：待填。
- 当前指针清理：待关闭时更新 STATUS / Plan / TASK_LEDGER / rolling checkpoint。
