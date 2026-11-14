---
id: RELEASE-PACKAGE-PROBE-1
title: 条件 4 打包可行性只读探测（依赖清单 + 可执行边界）
kind: evidence
governance_version: 3
status: done
disposition: "Gate 条件 4（当前 commit 的 Windows 包）；Gate 里唯一尚未被探测过的方向"
approval: DSH 2026-11-15（只读探测 + 允许在 workspace 产出派生物）
suggested_owner: DSH
owner: DSH
reviewer: null
depends_on:
  - MAINT-1-RELEASE-MONITOR
base_commit: 5dda04437
branch: main
worktree: G:/CODEX/New Manga
integration_commit: 4557bd03bd7a92765a873d1b30d481010269083e
delivery_head: 4557bd03b
canonical_evidence_status: complete
resource_closeout_status: complete
evidence_dir: verification/RELEASE-PACKAGE-PROBE-1
allowed_paths:
  - doc/tasks/RELEASE-PACKAGE-PROBE-1.md
  - doc/reviews/RELEASE-PACKAGE-PROBE-1-*.md
  - doc/reviews/MAINT-1-GATE-CONDITION-4-PROBE-2026-11-15.md
  - doc/reviews/MAINT-1-RELEASE-GATE-ASSESSMENT-2026-11-14.md
  - doc/REBASELINE_PLAN.md
  - doc/STATUS.md
  - doc/TASK_LEDGER.md
  - doc/checkpoints/GOAL-PROGRESS-2026-11-02.md
  - verification/RELEASE-PACKAGE-PROBE-1/**
---

# RELEASE-PACKAGE-PROBE-1：条件 4 打包可行性只读探测

## 来源与目标

Gate 条件 4 = "对当前固定产品 commit 生成并固定 Windows 包，完成 clean install、启动、升级/回退、
四个一级页面可达性与卸载矩阵"。评估一直记作"未完成，需重新打包 sidecar + 安装器签名"，但**从未探测过：
本环境到底能走到哪一步、卡在哪个具体依赖**。

本卡只做**探测**：逐条核实打包链的前置依赖，能做的部分尝试真做（产物只落 workspace），
不能做的写清"缺什么、给了就能走到哪一步"。

**一个可观察交付结果**：`doc/reviews/MAINT-1-GATE-CONDITION-4-PROBE-2026-11-15.md`，含
①依赖逐项 FREE / NEED_ACQUIRE / MISSING；②实际尝试的结果（成功则记录产物 path+size+sha256+smoke 结论）；
③"若提供 X 则可继续到 Y 步"的链条；④明确的 NOT_RUN 清单。

## Acceptance Criteria

- [x] **AC1 依赖清单**：至少覆盖 .NET SDK / 目标 runtime pack、sidecar 包（`core_service.exe`）、
      权重文件、代码签名证书、打包脚本本身、长路径与磁盘空间；每项标 FREE / NEED_ACQUIRE / MISSING
      并给**命令级证据**（不是"看起来有"）。
- [x] **AC2 真实尝试**：至少跑一次 `tools/ci/publish-release.ps1`（singlefile）到**可判定**的程度；
      成功则记录 exe path + 字节数 + sha256 + `manifest-singlefile.json` + smoke 结果（window/host ready/exit 0）；
      失败则原样贴出失败输出与退出码。
- [x] **AC3 绑定当前 commit**：产物 manifest 的 git HEAD 必须等于被探测的 head；不等则明确标注不可用作条件 4 证据。
- [x] **AC4 sidecar 版本诚实性**：明确记录所用 sidecar 的构建时间与它早于哪些命令（E-2），
      并说明"包能启动"**不等于**"命令面完整"。
- [x] **AC5 后续链条**：给出 clean install / 启动 / 升级回退 / 四页 / 卸载 六步里，哪些能在本环境做、
      哪些需要什么才可做。
- [x] **AC6 不虚报**：不得声称条件 4 已满足或包"可发布"；产物只落 workspace，不进仓库。

## 允许修改范围

见 frontmatter。产物落 `G:\CODEX\New Manga.workspace\artifacts\publish\`（脚本默认），证据文本落
`verification/RELEASE-PACKAGE-PROBE-1/`。

## 禁止范围

- **不得**修改 `src/**`、`apps/**`、打包脚本（探测不改代码）。
- **不得**把二进制产物提交进仓库。
- **不得**执行签名（无证书）、不得上传/发布到任何远端。
- **不得**因探测失败而把条件 4 写成"部分完成"—— 只有真实产物才算推进。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC1 | `dotnet --list-sdks`、检查 sidecar/权重/`makensis`/证书/长路径/磁盘 | 本机 | **全部逐项判定**（FREE 6 项、MISSING 2 项：PyInstaller、签名证书；签名经 `.nsi` 判定为非阻塞） | `doc/reviews/MAINT-1-GATE-CONDITION-4-PROBE-2026-11-15.md` §2 |
| AC2 | `pwsh tools/ci/publish-release.ps1 -Mode singlefile -SidecarDir … -EvidenceDir …` | .NET 9/10 + 旧 sidecar | **PASS**：`result=PASS exit=0 elapsed=7.7s artifact=94.94 MB`；smoke `pass=True exit=0 exit_kind=natural host_ready=True` | `verification/RELEASE-PACKAGE-PROBE-1/{manifest-singlefile,smoke-singlefile}.json`、`published-singlefile.png` |
| AC3 | 读 manifest 的 `git_head` | 产物 | **`5dda04437d68baf304b4364a3a73f9dfa217d943` = 被探测 head** ✅ | 同上 |
| AC4 | 记录 sidecar 构建时间与 E-2 影响 | — | 已写明：sidecar 为 **2026-10-23**，早于 `ReorderChapters`（`83e45cfe5`）等；`host_ready` 只证明 Core 能起、桥能连，**不证明 111 条命令可用**；且包**不自包含** sidecar | 探测文档 §4.1/§4.2 |
| AC5 | 六步链条逐项判定 | — | 已给出：build/冒烟 ✅、setup.exe 工具具备 🟡、install/启动/升级回退/四页/卸载 ✅ 可做（待 stage）、sidecar 重建 ❌、签名 ⚪ 非必需 | 探测文档 §5 |
| AC6 | 检查产物位置与措辞 | 仓库/workspace | 产物全部在 `G:\CODEX\New Manga.workspace\artifacts\publish\`，**未进仓库**；**未**声称条件 4 满足或可发布 | 同上 §6 |

## 依赖、风险与阻塞

- **风险 R1**：publish 可能长时间运行（自包含单文件 + 裁剪分析）。用后台 job 跑，避免阻塞。
- **风险 R2**：smoke 需要真实窗口；若本会话无交互桌面，`IsWindowVisible` 会失败 —— 这本身是有效结论
  （"本环境不能做真窗口冒烟"），但要与"包构建失败"区分开。
- **风险 R3**：旧 sidecar 可能让 smoke 的 host-ready 判定失败（E-2），需明确区分"包有问题"与"sidecar 过期"。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际测试：尚无。
- 后续记录日期、commit、环境、结果、遗留项。
### r1 复核处置（REJECT → 返修）

复核报告：`doc/reviews/RELEASE-PACKAGE-PROBE-1-review-r1.md`（审查者 `review-gate4-probe`，未参与实现）。

| finding | 严重度 | 处置 |
|---|---|---|
| **P1 "PyPI 不可达"为假**：默认 index（清华镜像）缺包，但 `pip download pyinstaller -i https://pypi.org/simple` **成功**（`pyinstaller-6.22.3`，正是钉死版本） | **P1** | **已修**：文档 §1 第 4 行、§2 表、§5 表、Gate §16 全部改写。**撤回"条件 4 只剩一项阻塞"的收窄结论**。这是我的判断错误：把"某个 index 失败"当成"包不可得"，未换源验证。 |
| **P2 截图不是四页导航** | P2 | **已修**：§4.3 改为"顶部是**空间切换**（资料柜/工位/控制台，见 `AppShellViewModel.cs:58-63`）+ Breadcrumb，不是四页导航"；§1/§16 措辞同步，消除与 §4.3 的矛盾。 |
| **P2 7.7s 是热缓存增量构建** | P2 | **已修**：新增 §7.2 —— 只证明"本机可构建"，不证明 clean-room；建议补 `--no-incremental` 或 `verify-clean-clone.ps1`。 |
| **P2 无失效检测** | P2 | **已修**：新增 §7.3 staleness 声明（sidecar 重建成功 / publish 脚本变更 / head 变化 / PyInstaller 可用性变化均会使结论过时，无自动报警）。 |
| **P2 Canonical Evidence 为空** | P2 | 已在收口时补 6 条 BLOB pin。 |
| 已核实为真的部分（保留） | — | manifest `git_head` 与 `git rev-parse` 一致；sha256 复算一致；输出目录无 sidecar；`--sidecar-dir` 为外部注入；`git ls-files` 仅 6 个文本/PNG；`host_ready` 来自 `HostRuntime.cs:1229`（`core.ping` 之后写出，非脚本自证）；`makensis /VERSION` = v3.13。 |

## Canonical Evidence

| evidence_id | AC/Gate | path（仓库相对路径或绝对路径） | commit | sha256 | class (`CANONICAL` / `SOURCE_PIN`) | sha256_basis |
|---|---|---|---|---|---|---|
| EV-RPP-01 | AC1/AC2/AC3/AC4/AC5 主交付 | doc/reviews/MAINT-1-GATE-CONDITION-4-PROBE-2026-11-15.md | 4557bd03b | 044475b58123629b56984d3a4ab02f411706cfb3296f1c9b5bd7b2415d18c13c | CANONICAL | BLOB |
| EV-RPP-02 | AC3 绑定当前 commit | verification/RELEASE-PACKAGE-PROBE-1/manifest-singlefile.json | 4557bd03b | 7eeb56702e5ff6aa3c7a50fe6d16e0d75ec3eceb8da11efee146b5d6162e6cd2 | CANONICAL | BLOB |
| EV-RPP-03 | AC2 冒烟结果 | verification/RELEASE-PACKAGE-PROBE-1/smoke-singlefile.json | 4557bd03b | dbdac2a743f2ad706fec55e98bd3c599557304399d460024d8e8f56b55c00e01 | CANONICAL | BLOB |
| EV-RPP-04 | AC2 窗口视觉证据 | verification/RELEASE-PACKAGE-PROBE-1/published-singlefile.png | 4557bd03b | 149f79fca4832de8fa6c5422694de7278fdb248319f0aae637762f1a50bedb22 | CANONICAL | BLOB |
| EV-RPP-05 | AC1/AC6 门禁 | verification/RELEASE-PACKAGE-PROBE-1/four-pieces.log | 4557bd03b | e0190eb059b06af3b9d8d9226208093ea49f2049d5d5c9b0b44519faf9f76a0a | CANONICAL | BLOB |
| EV-RPP-06 | 独立复核 r1（REJECT，纠正了 P1） | doc/reviews/RELEASE-PACKAGE-PROBE-1-review-r1.md | 4557bd03b | 45372a95dfc0ca616cece09e932226eca677e6bbbad5a6f06a1ff917555d09e7 | CANONICAL | BLOB |
## Resource Manifest

| resource_type | source_path | disposition | destination_path | sha256/manifest | reference/process check and result |
|---|---|---|---|---|---|
| artifact | 待填（workspace\artifacts\publish） | PRESERVE_REFERENCED | 同左 | 待填 | 本卡产物，不在仓库 |

## Closeout Record

- Closeout date / DSH：2026-11-15，DSH（Lead / Architect / Integrator）。
- canonical_evidence_status：`complete`（6 条 BLOB pin，commit `4557bd03bd7a92765a873d1b30d481010269083e`）。
- resource_closeout_status：`complete`。产物保留在 `G:\CODEX\New Manga.workspace\artifacts\publish\`
  （`NewManga.App.exe` 99,554,850 B + manifest + smoke + 截图），**未进仓库**；pip 探针缓存
  `G:\CODEX\New Manga.workspace\task-envs\RELEASE-PACKAGE-PROBE-1\pip-probe\pyinstaller-6.22.3-py3-none-win_amd64.whl`
  保留为证据（证明 PyInstaller 可得）。
- 删除、迁移、归档数量/字节数：0。
- **交付结论**：条件 4 **首次真实推进** —— 产出绑定 `5dda04437` 的包（`git_head` 一致、sha256 可复算），
  启动冒烟 `window_found/host_ready/exit 0/natural` 全通过。但**条件 4 仍 NOT MET**：install / 升级回退 /
  四页（打包产物上）/ 卸载矩阵**均未执行**，sidecar 仍是 2026-10-23 的旧版。
- **最重要的发现（推翻了我自己的旧结论）**：PyInstaller **可以**从 `pypi.org` 直连获得（`6.22.3`），
  这意味着 **E-2 可解**、`Host.Tests` 74 / `CoreClient.Tests` 26 / `App.Tests` 7 的 skip 面**可能可跑**。
  这是下一张卡的入口。
- 未关闭项及保留原因：见文档 §4 三条诚实边界与 §7.3 staleness。
- **本卡自身的错误登记（不淡化）**：
  1. **错判"PyPI 不可达"**（只试了默认镜像就下结论），并据此得出"条件 4 只剩一项阻塞"的错误收窄；
     r1 复核用 `-i https://pypi.org/simple` 实测推翻，我已复现确认；
  2. 把截图里的"资料柜/工位/控制台"空间切换写成"四页导航"，且与文档 §4.3 自相矛盾；
  3. 未在首版登记 staleness 与 evidence pin（r1 P2）。
