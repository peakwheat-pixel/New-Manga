---
id: TASK-033
title: 完整链收口：Color / Term Extract / Render handler 与渲染侧生产装配
kind: implementation
status: ready
approval: approved_by_user
suggested_owner: ZCode
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-010, TASK-014, TASK-019, TASK-034]
base_commit: 81ffd8314309324aeb7ed510f8f5a5ef73d509a7
branch: agent/deepseek/TASK-033-full-chain-handlers
worktree: G:/CODEX/New Manga.worktrees/TASK-033-deepseek
integration_commit: null
---

# TASK-033：完整链收口（Color / Term Extract / Render handler 与渲染侧生产装配）

**READY（2026-09-17 用户批准释放）**：Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**）、base=`81ffd83`（释放时 master HEAD）、branch/worktree 见顶部元数据（已创建并同步到本次释放提交）。Owner 开始实施前，在本任务分支把 `status` 改为 `in_progress`。

**Owner 指派说明**：`suggested_owner` 原为 ZCode，本次指派给 **DeepSeek Harness**——ZCode 的窗口授权已于 2026-09-17 撤销、当前不在线；同批次 TASK-032/034/035/036 亦由 DSH 承接、Codex 非作者 Review。**若用户希望等 ZCode 回归后改派，可在开工前提出**。

**本 Task 是 AC-RFULL-001 的收口切片**：D08 §AC-RFULL-001 [P0] 要求完整链 `OCR → Color → Term Extract → Translate → Segment → Mask Refine → Inpaint → Render → Save`。

## 释放前核对（Codex 实测，非作者自述；master `81ffd83`）

| 缺口 | 实测现状 |
|---|---|
| **`color` handler 缺失** | `ProductionHandlers._handlers`（`src/infrastructure/providers/handlers.py:146-157`）只注册 `ocr`/`translate`/`segment`/`mask_refine`/`inpaint`；执行期走 `src/infrastructure/pipeline/executor.py:29-32` → `StepExecutionError("PROVIDER_UNAVAILABLE", "no production handler for step='color' …")` |
| **`term_extract` handler 缺失** | 同上（同型 `PROVIDER_UNAVAILABLE`）；`src/application/tasks/service.py:84` 的 `_FULL_TRANSLATION` **确实规划**该步 |
| **`render` handler 缺失** | 同上；**且**上游 Clean 缺失时规划阶段即 `BLOCKED(missing_clean_artifact)`、无 StepRun（TASK-019 `verification/TASK-019/ac-status.md:25` 实测） |
| **更根本：渲染侧生产装配完全缺失** | `RenderService` **只在测试中被构造**（`rg "RenderService(" src/` = **0 命中**；唯一命中在 `tests/rendering/test_rerender.py:108`）。`src/bootstrap/app.py` 无 `RenderService`/`FontCatalog`/`Compositor`/`LayoutEngine` 装配（`rg` 0 命中）→ **仅补 handler 不足以打通 render**，必须同时补生产装配 |
| 渲染侧**适配器齐备**（故无需改渲染侧实现） | `QtTextLayoutEngine`（`infrastructure/rendering/qt_layout.py:43`）、`QtImageCompositor`（`qt_compositor.py:39`）、`QtFontCatalog`（`font_catalog.py:26`）、`PixelSourceStyleAnalyzer`（`pixel_source_style.py:51`）、`SqlitePageArtifactLocator`（`locator.py`）均已存在 |
| `color` 的依赖**已存在** | `SourceStyleService`（`application/translation/color/service.py:23`，`extract(...)`）+ 端口 `SourceStyleAnalyzer`（`ports/rendering/ports.py:133`）+ 实现 `PixelSourceStyleAnalyzer` |
| `term_extract` 的服务本体**可能不存在** | `application/translation/knowledge/` 目前只有 `tm.py`（TM 范围/状态/条目 + `TranslationMemoryStore` 协议）。**若无术语抽取服务，则需在本 Task 内新建**（`knowledge/**` 在允许路径内） |
| `translated` 指针的写者 | `ArtifactType.TRANSLATED` 已定义（`ports/repositories/artifacts.py:25`）；`RenderService` **自身**以 compare-and-set 提交 `translated`（`application/rendering/service.py::_commit_translated`）→ 见下文「单一写者」要求 |

## 归属裁决（回答 TASK-019 的 R-2「Render/Color/TermExtract handler 的归属与允许路径」）

1. **三个 handler 归 `src/infrastructure/providers/handlers.py`**（该文件已是 pipeline seam 的 handler 归属地），由 `src/bootstrap/app.py:313` 的 `build_production_handlers(...)` 构建并经 `:324` 注入 pipeline。**不得**改 seam 本体（`src/infrastructure/pipeline/**`）或执行器（`src/application/translation/pipeline/**`）。
2. **`color` / `term_extract` 是"无外部调用"的应用内步骤**：不得发起网络请求、不得依赖重型模型；能力缺失时 **fail-closed**（不静默降级为单色基线、不伪造术语结果）。
3. **`render` 调用应用层 `RenderService`**：生产装配补齐渲染侧依赖（复用既有 `infrastructure/rendering/**` 实现），使 render 步骤在 Clean 齐备时可执行。
4. **渲染侧范围裁定**：`src/ports/rendering/**`、`src/infrastructure/rendering/**` **本次不预先开放**——因适配器已齐备，本 Task 只需**装配**而非修改实现。**若确有修改必要**（例如新增端口方法），先在 Task 中记录**具体文件 + 理由 + 是否改变既有签名/行为**，由 Codex 裁决后再动；**任何改变 TASK-014 已交付行为**的改动必须先获批。

## 「单一写者」要求（P0 级架构约束，必须显式解决）

`RenderService` 会自行 compare-and-set 提交 `translated` 指针，而 pipeline seam 也按 `StepResult.revision_updates` 翻转指针——两者都可能写同一指针。**本 Task 必须**：

- 在 Task 中**明确记录谁是 `translated` 指针的唯一写者**（并说明理由）；
- 用测试证明**不出现双写或指针抖动**（例如断言一次 render 后指针恰好前进一次、`render` 的 `StepResult` 不重复翻转同一指针）；
- 若无法在不改 seam 的前提下保证单一写者，**停下并交 Codex 裁决**，不得自行修改 seam。

## Acceptance Criteria

- [ ] **AC ①（`color`）**：新增 handler，产出并记录 color/route 判定与 provenance；无外部调用/无模型依赖时 **fail-closed**（不得静默降级）；写回遵守单 Region 写作用域与 Lock。
- [ ] **AC ②（`term_extract`）**：新增 handler，产出 term/TM 候选并记录 provenance；**不修改正式术语库或 TM 数据、不发出网络请求**；能力缺失时 fail-closed。
- [ ] **AC ③（`render`）**：新增 handler；上游（Clean 等）齐备时**规划不再** `BLOCKED(missing_clean_artifact)` 且步骤可执行；写回遵守单 Region 写作用域、Lock 与 current/pinned Revision 保护；**缺上游时仍 fail-closed 且原因入 provenance**（不得放宽既有规划守卫）。并满足上文「单一写者」要求。
- [ ] **AC ④（渲染侧生产装配）**：`src/bootstrap/app.py` 组装 render 所需适配器（**复用** `infrastructure/rendering/**` 既有实现，不新增实现、不改其签名/行为），使 `assemble_services` 在**无重型依赖**时仍可构建（沿用 AC-OPTIONAL-001 口径），并给出 readiness 证据。
- [ ] **AC ⑤（完整链用例）**：以**真实 SQLite + 真实 seam + 替身 provider**（沿用 `tests/providers` 既有替身范式）跑通 9 步，断言：目标 Region 被写入；**同页其他 Region 的 text / pointer / stage 全不变**（AC-RFULL-002）；人工译文与 Lock 保留（AC-RFULL-005）；并**逐步**给出每步 `status`。
- [ ] **AC ⑥（AC-RFULL-001 口径更新，不得记 PASS）**：更新 `verification/TASK-019/ac-status.md` 中 AC-RFULL-001 的口径为「**BLOCKED（handler 与生产装配面已打通；真实 OCR/翻译/修复能力仍缺）**」，并逐项列出仍 `BLOCKED`/`NOT_RUN` 的项与**解锁条件**。**严禁**把 AC-RFULL-001 记为通过。
- [ ] **AC ⑦（回归与分列）**：`tests/providers`、`tests/pipeline`、`tests/core`、`tests/storage`、`tests/rendering` 与全仓套件 **passed 不减少**；全仓串跑**至少 5 次**逐次记录 passed/skipped 与退出码。
- [ ] **AC ⑧** 交付 Handoff、实际测试/审阅记录与未完成项，经**非作者** Review（协作协议 §6 四轴）与 Codex 集成验证后才能 done。

## 允许修改范围

- `src/infrastructure/providers/**`（新增 handler 与接线）
- `src/bootstrap/app.py`（注入 handler、装配渲染侧依赖）
- `src/application/translation/color/**`、`src/application/translation/knowledge/**`、`src/application/translation/context/**`（仅在确需小幅适配/新建术语抽取服务时；须在 Handoff 说明理由）
- `src/application/rendering/**`（仅在确需小幅适配时；须在 Handoff 说明理由）
- `tests/providers/**`、`tests/pipeline/**`
- `doc/tasks/TASK-033.md`、`doc/handoffs/TASK-033-*.md`、`verification/TASK-033/**`、`verification/TASK-019/ac-status.md`（仅 AC ⑥ 的口径更新）
- **需先申请**：`src/ports/rendering/**`、`src/infrastructure/rendering/**`（见「归属裁决」第 4 条）

## 禁止范围

- 不得修改依赖清单、Schema/migration、**pipeline seam 本体**（`src/infrastructure/pipeline/**`、`src/application/translation/pipeline/**`）、路由判定算法、`AGENTS.md`、生产数据、其他 Task。
- 不得把 TASK-019 / TASK-034 已登记的 `BLOCKED`/`NOT_RUN` 项改记为通过（AC-RFULL-001 的完整通过仍需真实模型/端点证据）。
- 不得放宽既有测试或新增 `skip`/`xfail` 掩盖失败；不得伪造 provider 结果或静默降级（AC-FALLBACK-001 / AC-OPTIONAL-002 口径）。
- 不得顺手处理 **R-06**（`tests/reading_export` webtoon flaky）与 TASK-034 的 R-03（常量跨层归属）；不得释放 TASK-020～TASK-023、TASK-025～TASK-027。
- 不 push。

## 测试要求

- 主套件：`python -m pytest tests/providers tests/pipeline -q -p no:cacheprovider -rs`（含完整链用例与三个 fail-closed 用例）。
- 回归：`python -m pytest tests/core tests/storage tests/rendering -q -p no:cacheprovider -rs`；全仓 `python -m pytest -q -p no:cacheprovider -rs` **至少 5 次**并逐次记录。
- AC ④ 须给出"无重型依赖下 `assemble_services` 可构建"的证据（对象可从 `tests/providers/test_bootstrap_providers.py` 的既有范式扩展）。
- AC ③ 须给出「单一写者」与「缺上游仍 fail-closed」两类证据。
- 真实模型/端点可用时另跑端到端并记录设备、模型版本与权重 Hash；不可用时标 `BLOCKED`/`NOT_RUN` 并给出解锁条件。
- 分列 passed/skipped 与 skip 原因；记录 commit、OS/依赖、命令、退出码与证据路径。

## 依赖、风险与阻塞

硬依赖：[TASK-010](TASK-010.md)（Context/TM）、[TASK-014](TASK-014.md)（渲染切片）、[TASK-019](TASK-019.md)（provider 集成层）、[TASK-034](TASK-034.md)（`RoutePolicy` 单一入口）——均已集成 `done`。

阻塞：**已解除**——2026-09-17 用户批准释放。

风险：
- **渲染侧生产装配从未存在**（本 Task 的首要发现之一）：装配可能牵出 TASK-030 装配契约或 TASK-015 阅读/导出路径的既有假设；若发现需要改动 seam 或渲染侧实现，**必须先回抛裁决**（见「归属裁决」第 1/4 条）。
- **双写风险**：见上文「单一写者」要求；这是本 Task 最可能出现的架构缺陷。
- **真实能力仍缺**：本环境无 `torch`/`diffusers`/`numpy`、无真实端点 → 真实 OCR/翻译/修复类 AC 保持 `BLOCKED`/`NOT_RUN`，**不因本 Task 而改变**。
- 全仓串跑非 100% 稳定（STATUS「已知 flaky 测试」）；若复现失败请用 `-rf` 记录用例名并按同一口径登记。

## 交付与运行记录

- Handoff：尚无。Review：尚无。实际执行/测试：尚无（`ready`，实施未开始）。
- **最近状态（当前，唯一）**：2026-09-17 由用户批准释放；Codex 登记 `status=ready`、`approval=approved_by_user`、Owner=`DeepSeek Harness`、Reviewer=`Codex`（**非作者**）、base=`81ffd83`（释放时 master HEAD）、branch=`agent/deepseek/TASK-033-full-chain-handlers`、worktree=`G:/CODEX/New Manga.worktrees/TASK-033-deepseek`，并完成上表「释放前核对」（含**关键新发现**：渲染侧生产装配完全缺失、`RenderService` 仅测试构造）与「归属裁决」「单一写者」两项约束的固化。**实施尚未开始。**
- 历史状态（2026-09-17）：由 Codex 依 TASK-019 R-2/F-2 创建为 `proposed`（`approval=pending_user_review`）；同日获用户批准释放。
