---
id: SIDECAR-REBUILD-1
title: 重建 sidecar 使命令面追上当前 head（解除 E-2）
kind: infra
governance_version: 3
status: closed_with_limitations
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
delivery_head: ce0cc85c1
canonical_evidence_status: complete
resource_closeout_status: complete
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

- [x] **AC1 构建环境**：在 `.workspace/task-envs/m2ac5-build` 建 venv 并安装 `requirements-build.txt` <<MET>>
      的全部钉死版本（源用 `-i https://pypi.org/simple`）；记录每个包的**实际安装版本**。
- [x] **AC2 构建成功**：跑 `packaging/m2ac5/build_sidecar.ps1` 产出 `core_service.exe`/`host_bridge.exe` 等； <<MET>>
      记录产物尺寸、sha256、构建时间与构建日志。失败则原样贴出失败原因。
- [x] **AC3 命令面核对（判别核心）**：新旧 sidecar 各跑一次 `core.ping`，**贴出 capabilities 差异**； <<MET>>
      必须证明新 sidecar 包含旧 sidecar 缺失的命令（尤其 `ReorderChapters` 所在命令与 FEA-12 delete/trash）。
      若没有差异，本卡**不得**声称 E-2 已解除。
- [x] **AC4 skip 下降实测**（下降已达成：skip 100→44；**但暴露 13 个失败，见 §5**）：设 `NEWMANGA_CORECLIENT_SIDECAR_DIR=<新 sidecar>` 重跑三项目全量， <<MET>>
      记录 pass/skip 变化，与基线（App 950/0/11、Host 321/0/74、CoreClient 186/0/26）逐项对比。
      **skip 减少必须是新 sidecar 导致**，不得通过改测试 gate 或跳过实现来达成。
- [x] **AC5 不回归**：无夹具模式下三项目仍 0 failed（2026-11-17 实测 Host 334/0/74/408、CoreClient 227/0/31/258、App 962/0/11/973 ⇒ **1523 passed / 0 failed / 116 skipped / 1639 total**，三项目 EXIT 均 0）；未新增 skip/xfail、未放宽断言。 <<MET>>
- [x] **AC6 零产品代码改动**：逐提交核对本卡 6 个提交（`83f452607`/`92349bc4e`/`acb8a89b2`/`0b458eeba`/`18bc51bc9`/`f1a2e8805`）——**均无 `src/**` 或 `apps/**` 改动**；新 bundle 位于 `.gitignore:22` 忽略的 `apps/desktop-avalonia/build/`，未提交进仓库。 <<MET>>

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
| EV-SR-01 | AC1 构建环境 | verification/SIDECAR-REBUILD-1/pip-freeze.txt | ce0cc85c1 | 2b89ef4935c6a432b4618a9a4b1d731abfbfbc8c4faf7c2a5dab9af75bd8df59 | CANONICAL | BLOB |
| EV-SR-02 | AC2/AC3/AC4 主证据（构建、capabilities 差异、skip 下降、13 失败） | verification/SIDECAR-REBUILD-1/README.md | ce0cc85c1 | 34fce28ee73959c023992fff4887afa511fbd48de9c3c5f96dc5ebd6b056d7ee | CANONICAL | BLOB |
| EV-SR-03 | AC5 四件套（当时口径） | verification/SIDECAR-REBUILD-1/four-pieces.log | ce0cc85c1 | ad4369ec58c9fc3a28d20e809f21371d7685132ef0db0ce04ecf019d1721f598 | CANONICAL | BLOB |
| EV-SR-04 | AC5 无夹具复测（2026-11-17） | verification/SIDECAR-REBUILD-1/ac5-no-fixture-2026-11-17.log | ce0cc85c1 | 76781ecd5a3f6dc403a75eec17ed16ad6376b0f6520e41f53d867a193f5b9039 | CANONICAL | BLOB |
| EV-SR-05 | source/probe | verification/SIDECAR-REBUILD-1/probe_args.py | ce0cc85c1 | 3e96befdb95de81139bf7611f7f8fc6b536bb101c3bcd811f304bfcfe0c7fd1b | SOURCE_PIN | BLOB |
| EV-SR-06 | source/probe | verification/SIDECAR-REBUILD-1/probe_core.py | ce0cc85c1 | 014ec5d39630e93aa6ab9fd74384b9f6b3dc6da9ce7978f033463e50ad81d1f2 | SOURCE_PIN | BLOB |
| EV-SR-07 | source/probe | verification/SIDECAR-REBUILD-1/probe_env.py | ce0cc85c1 | 6dc9b3064d71e1c76945e2ec05899874ef5dc6b5cff324e606745e028974d7c4 | SOURCE_PIN | BLOB |
| EV-SR-08 | source/probe | verification/SIDECAR-REBUILD-1/probe_fixture.py | ce0cc85c1 | db869682eccead1d41ec76ffcc29e1f8c89b416157893aeafbe8f9efc5c07136 | SOURCE_PIN | BLOB |
| EV-SR-09 | source/wire | verification/SIDECAR-REBUILD-1/wire_analyze.py | ce0cc85c1 | 76dc509b830f3739f030a4fb17fe534636c02f1528604474105e7ed4e2f5c63b | SOURCE_PIN | BLOB |
| EV-SR-10 | source/wire | verification/SIDECAR-REBUILD-1/wire_chap.py | ce0cc85c1 | 161a49b448944d703fe9523c87a31219b48578baf6d9ea3a344509a62868a90e | SOURCE_PIN | BLOB |
| EV-SR-11 | source/wire | verification/SIDECAR-REBUILD-1/wire_fail.py | ce0cc85c1 | 885a07c842836acde5942e352ed86c1441253a199ee96e44ba42af94e3e91e49 | SOURCE_PIN | BLOB |
| EV-SR-12 | source/wire | verification/SIDECAR-REBUILD-1/wire_resp.py | ce0cc85c1 | 77605d4c121c63304cfcddcb5a6f35710de6548fbbefc0a4d9f63e198874d4a7 | SOURCE_PIN | BLOB |
| EV-SR-13 | source/wire | verification/SIDECAR-REBUILD-1/wire_timeline.py | ce0cc85c1 | 2bb4bc1e9b232cbfa1ab7296baa865614167ed5744d31e9f5f9870d714c037f4 | SOURCE_PIN | BLOB |
| EV-SR-14 | source/raw-log | verification/SIDECAR-REBUILD-1/core_service.stderr.reader-chapters-concurrent.log | ce0cc85c1 | 46f881c44c178087483ec0915ef814d38d6e551e3871d0eb1f217d75091882c2 | SOURCE_PIN | BLOB |
| EV-SR-15 | source/raw-log | verification/SIDECAR-REBUILD-1/core_service.stderr.reader-chapters-list.log | ce0cc85c1 | f238611bb63ac0539e36b74e0d387b1f30eedf8e413394553cf2786303faf606 | SOURCE_PIN | BLOB |

## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| artifact | G:/CODEX/New Manga.workspace/task-envs/SIDECAR-REBUILD-1 | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/SIDECAR-REBUILD-1 | G:/CODEX/New Manga.workspace/task-envs/SIDECAR-REBUILD-1/RESOURCE-MANIFEST.json | 证据/探针目录 170 文件 / 55,837,093 B；manifest sha256 54096522…；实测存在，未清理 |
| artifact | G:/CODEX/New Manga.workspace/task-envs/m2ac5-build | PRESERVE_REFERENCED | G:/CODEX/New Manga.workspace/task-envs/m2ac5-build | G:/CODEX/New Manga.workspace/task-envs/SIDECAR-REBUILD-1/RESOURCE-MANIFEST.json | 构建 venv（63 包，含 torch 2.14.0 cp314、pyinstaller 6.22.3）40,334 文件 / 1,310,861,487 B；实测存在 |
| artifact | apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar | PRESERVE_REFERENCED | apps/desktop-avalonia/build/sidecar/core-sidecar/core-sidecar | G:/CODEX/New Manga.workspace/task-envs/SIDECAR-REBUILD-1/RESOURCE-MANIFEST.json | 新 sidecar bundle（schema v14，build-manifest git_head f7d273d9、pyinstaller 6.22.3）；被 .gitignore:22 忽略，未提交进仓库；实测存在 |

## Closeout Record（2026-11-17，DSH）

- canonical_evidence_status：`complete`（15 行，BLOB 基准 `ce0cc85c1`）。
- resource_closeout_status：`complete`（3 行 `PRESERVE_REFERENCED`；`RESOURCE-MANIFEST.json` 40,504 文件 / 1,366,698,580 B，sha256 `54096522b0a16c52b783ad64cc0e44bdff2625db6df6661da22de39c54202170`）。
- 删除、迁移、归档数量/字节数：**0**。
- **实测（2026-11-17 复测）**：AC1–AC4 见 `README.md`；AC5 无夹具三项目 **1523 passed / 0 failed / 116 skipped / 1639**（Host 334/0/74/408、CoreClient 227/0/31/258、App 962/0/11/973，均 EXIT=0）；AC6 本卡 6 个提交零产品代码改动。
- **为何是 `closed_with_limitations` 而不是 `done`**（卡面既有约束 + 实测）：
  1. **13 个失败未归因完成**（用新 sidecar 的夹具模式）：CoreClient 4 个性质清楚（"Frozen Core" 前提过期，保留 fail-closed 语义，需改为显式模拟旧 capabilities）；Host 9 个已由第七轮诊断定位根因 = **`request_id` 错配，后台 source 扫描抢走阅读器响应（P1，产品侧）**，本卡范围不含修复。
  2. **SFX 权重缺失**：`yolo11s-seg.onnx` 全工作区不存在（训练产物），只影响 `sfx_detect_probe`，不影响 `core_service`。
  3. **未做**：App.Tests 的 7 个 sidecar 测试、用新 sidecar 重跑 publish 冒烟（条件 4 下一步）。
- **边界**：本卡**不宣称条件 3/4 已满足**；AC4 的 skip 下降（100→44）与新 sidecar 的因果关系已由 AC3 的 capabilities 差异证明，但 13 个失败必须在后续卡（或 MAINT-1 的 E-6 归因）里处置。
- 当前指针：STATUS / `REBASELINE_PLAN` / `TASK_LEDGER` 已随收口更新；恢复点为本卡 + `verification/SIDECAR-REBUILD-1/README.md`。
