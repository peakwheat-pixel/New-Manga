---
id: TASK-019
title: 集成已验证的检测/OCR/翻译/修复 Provider
kind: implementation
status: in_review
approval: approved_by_user
suggested_owner: ZCode
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-011, TASK-014, TASK-016, TASK-017, TASK-018, TASK-024]
base_commit: 36242fb00f9f432ec66cc3c33afc167578d0f341
branch: agent/deepseek/TASK-019-provider-integration
worktree: G:/CODEX/New Manga.worktrees/TASK-019-deepseek
integration_commit: null
---

# TASK-019：集成已验证的检测/OCR/翻译/修复 Provider

**READY（2026-09-17 用户批准释放；同日按用户指示改派 Owner）**：六个硬依赖 **全部已集成 `done`**（TASK-011 `369e95f`、TASK-014 `a9432971`、TASK-016 `9bf85f5`、TASK-017 `d36f724`、TASK-018 `5a9f5c8`、TASK-024 `61c33e2`）。Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**——Owner 为 DSH 时原 Reviewer DSH 会构成同体审查，故一并更换）；base=`36242fb`、branch/worktree 见顶部元数据（首次按 `agent/zcode/...` 命名创建的**无提交** worktree/分支已移除，不作为工作区）。Owner 开始实施前，在本任务分支把 `status` 改为 `in_progress`。

**释放时登记的输入缺口（不得默认通过，必须在交付中显式分列）**：

1. **真实 OpenAI-compatible 端点未配置**：TASK-017 的真实 Provider 协议/成本/时延为 `NOT_RUN`（付费端点未提供，且任何 Task 都不得自行配置付费 Provider）。因此依赖真实端点才能成立的 AC（兼容 Vision 的端到端行为、成本/时延）必须按 `BLOCKED`/`NOT_RUN` 交付，**不得**用 mock 或本机回环结果冒充。
2. **本机未运行 Sakura 服务**：AC-EXT-SAKURA-001 的真实服务验证为 `NOT_RUN`；本 Task 需交付**可测的健康/就绪探测实现**（探测范围遵守 U-6：只做健康探测与就绪状态，不做显存/负载等深度指标），并把"真实服务验证"如实标为 `NOT_RUN`，同时明确探测端点与判定原因的契约。
3. **本环境无 `torch`/`diffusers`/`numpy`**（已实测），GPU 存在（RTX 5070 Ti, 16303 MiB）但无运行时依赖：依赖模型权重的本地 OCR/修复质量类 AC 必须按 `BLOCKED` 交付，并在交付物中给出**解锁条件**（依赖获批 + 权重获取路径 + 可复现实测）。

**上游已可引用的实验结果**（本 Task 直接消费，不必重做）：TASK-016 的 OCR/检测候选与许可调研；TASK-017 的 RegionID 契约分类器与 retry/fallback 口径（R-001/R-002/R-003 已吸收）；TASK-018 的 Mask/修复路线实测与 fail-closed 门控结论。**这些实验结论不自动成为产品需求**，取舍按本 Task 的 AC 与用户裁决。
当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D01 §5；D02 §6/11；D06 §6～23/51～57/80～85；D08 AC-OCR/INPAINT/FALLBACK/GPU/MODEL。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-OCR-001、AC-OCR-004、AC-INPAINT-001、AC-INPAINT-002、AC-INPAINT-003、AC-INPAINT-004、AC-RFULL-001、AC-RFULL-002、AC-RFULL-003、AC-RFULL-004、AC-RFULL-005、AC-FALLBACK-001、AC-FALLBACK-002、AC-GPU-001、AC-GPU-002、AC-GPU-003、AC-OPTIONAL-002、AC-MODEL-001、AC-MODEL-002。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 按已批准实验报告实现明确选定能力，覆盖本地OCR、韩文OCR、兼容Vision、Translation以及Simple Fill/漫画修复和彩色路线；不可用候选明确禁用，未获批范围不能称完成。
      → **部分达成、已分列**：能力端口与适配器（manga-ocr / PaddleOCR Korean / OpenAI-compatible Vision / 远程与本地 Sakura 翻译 / Simple Fill+Edge Bleed 基线 / 彩色路线策略）全部交付；**真实 OCR、韩文 OCR、真实彩色修复的质量类判定为 `BLOCKED`**（无依赖/权重/端点），未获批范围（学习型修复路线）未称完成。逐条见 [AC 状态分列](../verification/TASK-019/ac-status.md)。
- [x] 通过统一网络/设备/文件边界接入Pipeline，严格输出映射、显式fallback、Mask/模型/options/provenance与单Region写回限制。
      → `tests/providers/test_handlers_pipeline.py`（真实 SQLite + 真实 seam）与 `tests/providers/test_retry_fallback.py`；`color`/`term_extract`/`render` 三步的 handler 不在本 Task 允许路径，完整链见 AC-RFULL-001 的 `BLOCKED` 登记。
- [x] 模型延迟加载、下载进度/取消/Hash、Ready判定、OOM隔离、GPU重任务默认单并发；CPU fallback仅在Provider声明支持时执行。
      → `tests/providers/test_model_lifecycle.py`、`test_devices.py`；**真实权重下载与真实 GPU OOM 复现为 `BLOCKED`/`NOT_RUN`**（无来源、无运行时）。
- [x] D08 §78 的 AC-EXT-SAKURA-001：Sakura Profile 连接测试给出健康/就绪状态与原因，探测范围遵守 U-6；真实服务验证与实现证据必须实测，当前 D13 结果 NOT_RUN。SAKURA-002/003 仍为草案，不自动纳入本任务。
      → 探测实现 **PASS**（5 种结果与原因码；仅请求 `/models`（必要时 `/health`），无显存/负载字段）；**真实服务验证 `NOT_RUN`**：本机无 Sakura 实例，已用真实 `StdlibTransport` 执行一次真实探测（`unreachable` / `connection refused`）。SAKURA-002/003 未实现。
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。
      → Handoff：[TASK-019-726baf5](../handoffs/TASK-019-726baf5.md)；取证：[verification/TASK-019/](../verification/TASK-019/author-verification.md)。**Review 与集成尚未执行**，本 Task 不自行标记 `approved`/`done`。

## 允许修改范围

以下为相对仓库根目录的允许路径。**Codex 已按 base `36242fb` 的实际结构核对并收紧**（2026-09-17）：`src/ports/` 现有 `network`/`providers`/`rendering`/`repositories`；`src/infrastructure/` 现有 `credentials`/`filesystem`/`network`/`pipeline`/`rendering`/`sqlite`/`transport`；`src/application/translation/` 现有 `color`/`context`/`knowledge`/`pipeline`。下列当前不存在的目录属**本 Task 新建**，不是既有实现。

- src/ports/detection/**、src/ports/ocr/**、src/ports/translation/**、src/ports/inpaint/**（新建能力端口）
- src/ports/providers/**（既有 profile/capability 模型：**只允许扩展 capability 常量与新增可选字段**，不得改变既有字段语义或破坏既有测试）
- src/infrastructure/providers/**、src/infrastructure/devices/**（新建适配器、设备与模型生命周期）
- src/application/translation/inpaint/**（新建修复 Step）
- src/bootstrap/app.py（**唯一允许改动的既有装配点**：`build_production_pipeline(conn)` 目前不传 `handlers`，本 Task 在此注入真实 handler。`src/infrastructure/pipeline/**` 与 `src/application/translation/pipeline/**` 已支持注入，**不在允许范围**）
- tests/providers/**
- doc/tasks/TASK-019.md、doc/handoffs/TASK-019-*.md、verification/TASK-019/**

超出以上范围（依赖清单、Schema、pipeline seam 本体、其他 Task、`AGENTS.md`）先由 Codex 在本 Task 明确范围变更，不得自行扩展。

## 禁止范围

禁止范围：

- 不得修改未列出的其他 Task、`AGENTS.md`、生产数据或用户源文件。
- **不得变更依赖清单（`requirements*.txt`/`pyproject.toml`）与 Schema/migration**：新增任何第三方依赖或数据库变更必须先取得用户批准并在本 Task 记录范围变更；未获批准时相关能力按 `BLOCKED` 交付。
- 不得把 mock、回环 HTTP 或确定性替身的结果当作真实模型/真实端点证据（TASK-016/017/018 已确立的诚实性要求）。
- 不得为了让测试变绿而放宽既有测试、删除既有断言或新增 skip 掩盖失败。
- 不得改动画布外的共享接口与装配（含 pipeline seam 本体）；需要时先由 Codex 在本 Task 明确范围变更。

## 测试要求

- **主要套件**：`python -m pytest tests/providers`（本 Task 新建）。每项能力至少覆盖 contract（成功 / 失败 / 畸形输入）与**缺依赖时的 fail-closed 行为**（缺依赖不得让 Core 崩溃或静默降级）。
- **回归（强制）**：改动 `src/ports/providers/**` 或 `src/bootstrap/app.py` 后，必须复跑相关既有套件（至少 `tests/pipeline`、`tests/core`、`tests/storage`）与全仓 `python -m pytest`，并在记录中**分列 passed/skipped 与 skip 原因**；不得用新测试替换或放宽既有断言。
- 真实端点/真实模型可用时另跑端到端：比较目标/非目标 Region、原图 Hash、人工锁与新建 Revision；记录实际设备、模型版本与权重 Hash。
- 缺依赖、缺端点或缺权重时：相关 AC 标 `BLOCKED`/`NOT_RUN` 并给出解锁条件；**不得**以 mock 结果代替真实证据。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果与证据路径。

## 依赖、风险与阻塞

硬依赖：[TASK-011](TASK-011.md)（`369e95f`）、[TASK-014](TASK-014.md)（`a9432971`）、[TASK-016](TASK-016.md)（`9bf85f5`）、[TASK-017](TASK-017.md)（`d36f724`）、[TASK-018](TASK-018.md)（`5a9f5c8`）、[TASK-024](TASK-024.md)（`61c33e2`）——**均已集成 `done`**（2026-09-17 释放前核对）。

**已登记阻塞（不得默认通过）**：

1. **真实 OpenAI-compatible 端点未配置** → 依赖真实端点成立的 AC（兼容 Vision 端到端、成本/时延）标 `BLOCKED`；解锁条件 = 用户提供端点，或用户明确取消该路线。
2. **本机未运行 Sakura** → AC-EXT-SAKURA-001 的**真实服务验证** `NOT_RUN`；健康/就绪探测实现仍必须交付并可测，范围遵守 U-6。
3. **本环境无 `torch`/`diffusers`/`numpy`** 且依赖清单变更需用户批准 → 模型质量/性能类 AC `BLOCKED`；解锁条件 = 依赖获批 + 权重获取路径 + 可复现实测。

若必需模型/端点不可用，阻止相关 AC 完成并由用户决定范围；**不能只交 Mock 冒充真实集成**。需要新增依赖、改动 Schema 或超出允许范围时，登记具体 blocker 交 Codex 处理，不得自行扩展。

## 交付与运行记录

- Handoff：[TASK-019-726baf5](../handoffs/TASK-019-726baf5.md)（delivery_head=`726baf5`）。
- Review：尚无（待 Codex 非作者独立 Review）。
- 实际执行/实验/测试：
  - 取证总表：[verification/TASK-019/author-verification.md](../verification/TASK-019/author-verification.md)；AC 分列：[ac-status.md](../verification/TASK-019/ac-status.md)；环境：[environment.json](../verification/TASK-019/environment.json)；就绪报告：[readiness-report.json](../verification/TASK-019/readiness-report.json)；真实 Sakura 探测：[sakura-probe-attempt.json](../verification/TASK-019/sakura-probe-attempt.json)；日志：[pytest-providers.log](../verification/TASK-019/pytest-providers.log)、[pytest-regression.log](../verification/TASK-019/pytest-regression.log)、[pytest-full.log](../verification/TASK-019/pytest-full.log)；路径核对：[changed-paths.txt](../verification/TASK-019/changed-paths.txt)。
  - 命令与结果（本机 `G:/CODEX/New Manga.task-envs/TASK-012-py312`，Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1，`PYTHONDONTWRITEBYTECODE=1`，退出码全部 0）：基线 `python -m pytest -q -p no:cacheprovider` = **530 passed / 6 skipped**；`python -m pytest tests/providers` = **110 passed / 0 skipped**；`python -m pytest tests/pipeline tests/core tests/storage` = **78 passed / 0 skipped**；全仓 = **640 passed / 6 skipped**（+110 全部为本 Task 新增；6 条 skip 均在既有 `tests/network`，原因 `openssl unavailable`）。`git diff --check 36242fb..726baf5` 退出码 0；`git diff --name-only c9eb65a..HEAD` 46 条**全部在允许路径内**，禁止路径命中 0。
  - 真实探测（非 mock）：生产 `SakuraProbe` + `StdlibTransport` 对 `http://127.0.0.1:8080/v1` 发起真实连接 → `reason_code=unreachable`、`connection refused`、仅 1 个请求（各证明探测可用与 U-6 范围）。
  - **BLOCKED/NOT_RUN 如实分列**：真实 OCR/韩文 OCR/真实彩色修复质量、真实翻译质量与成本/时延、真实权重下载、`color`/`term_extract`/`render` 接线（AC-RFULL-001 完整链）为 `BLOCKED`；真实 Sakura 服务验证、真实端点端到端为 `NOT_RUN`。**未以 mock/替身冒充模型质量或真实端点**。
- **最近状态（当前，唯一）**：2026-09-17 实现完成并置 **`in_review`**，交 Codex 非作者独立 Review（集成由 Codex 执行）。分支 `agent/deepseek/TASK-019-provider-integration`、worktree `G:/CODEX/New Manga.worktrees/TASK-019-deepseek`、fixed base `36242fb`、delivery head `726baf5`（`07d78d3` 开工文档、`8effbeb` 实现主体、`5fdd80a` 写入守卫与一致性、`3176520` 取证文档、`726baf5` 页面级修复累积与端到端用例）。**未 push、未合并 master**。范围判定登记：新增 `src/ports/providers/errors.py`（共享错误/就绪分类）属允许 glob 内的**新增模块**，`src/ports/providers/profiles.py` 仅新增 `CAPABILITY_DETECTION` 常量、未改既有字段语义；如 Reviewer 判定越界请退回并指定落点（Handoff 风险 R-6）。同批登记待 Codex 裁决项：AC-RFULL-001 的 `color`/`term_extract`/`render` handler 归属与允许路径（R-2）、彩色/复杂场景拒绝单色基线的产品取舍（R-3）、**页面级 Mask artifact 与 Region 单元的一对多关系**（R-8：当前 Mask 指针最终只指向最后一个 Region 的精修 mask，历史 revision 保留；按 Region 查看 mask 需数据模型裁决）、以及 **R-5 疑似跨 Task 缺陷**（普通新建 Region 默认 `sfx_policy='skip'` 导致 planner 对 `translate/segment/mask_refine/inpaint/render` 一律 `SKIP_POLICY`，`src/ui/**` 无写入路径；证据见取证 §5）。
- 历史状态（2026-09-17 释放前）：窗口条款登记 `blocked`；U-6 已批准 Sakura 监控范围；AC-EXT-SAKURA-001 已正式编号并追踪为 `NOT_RUN`；TASK-018 已 `ready` 但未完成；TASK-017 真实 Provider 协议/成本/时延 `NOT_RUN`（付费端点未配置）；本机 Sakura 未运行。
