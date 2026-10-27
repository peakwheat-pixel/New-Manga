# TRANSLATE-PROVIDER-1 Handoff（翻译 provider 最小可用接线）

- Task: `doc/tasks/TRANSLATE-PROVIDER-1.md`（team task-37）
- Branch: `task/TRANSLATE-PROVIDER-1`；Worktree: `G:/CODEX/New Manga.workspace/worktrees/TRANSLATE-PROVIDER-1`
- Base: `97de0fa99`（卡面）；实际分支基于 `ae7fe3334`（卡面允许 HEAD）
- Delivery head: `f96f245f4b5f435275767a6b00d7721debd64ea3`（实现+证据提交；Canonical Evidence 的 sha256 pin 指向该树）
- 未 push；未改协议/Host 契约/旧壳；未改 `packaging/**`（RELEASE-REPACK-1 的领域）。

## 1. 交付摘要

| AC | 结论 | 证据 |
|---|---|---|
| AC1 provider 盘点/判定 | **MET** | `provider-inventory.json`：现有 2 个 translate slot（openai-compatible-translation / sakura-local）均不能开箱离线（`not_configured`）；新增 `identity-translation`（`identity-experimental`，零 requirements）并注册，`ready` |
| AC2 绑定与装配 | **MET** | `src/infrastructure/providers/translation_identity.py`（新增）+ `runtime.py` 注册；两条绑定路径均实测（StartRun override / 持久化默认绑定）；无绑定仍 typed `PROVIDER_NOT_CONFIGURED`；新增单测 12 例 |
| AC3 8 页 Run | **MET（同构建全链路待重打包）** | 源码直跑（生产 assembly 同路径）`identity` 与 `default-binding` 两变体：translate 3/3 页 completed（22/22 Region units）→ segment/mask_refine/inpaint/**render 22/22 completed**，整 run `completed`；页 4–8 completed(0 region)。RELEASE-REPACK-1 新 exe（sha `9fcb9e87…`）上 8 页 Run 为同构建见证：detect/ocr/color/term completed、translate typed 缺口（见 §3） |
| AC4 回归 | **MET** | pytest 本树 **4F/2763P/9S** vs 同树纯净 base `ae7fe3334` **4F/2752P/9S**（失败集合逐条相同，含环境性 `test_sandbox_job_kills_grandchildren`；+11 全为本批新增用例，0 新增失败）；test.ps1 **177/177**；vitest **60/567** |
| AC5 门禁 | **MET** | `check.ps1 -TaskPath` 见 §5；sha256 pin + 本 Handoff + Record Decision（REPORT §6） |

## 2. 代码改动

| 文件 | 改动 |
|---|---|
| `src/infrastructure/providers/translation_identity.py`（新增） | `IdentityTranslationProvider`：输入=输出；每条结果 provenance 标 `identity-experimental` / `identity-passthrough` / `options.experimental=identity-placeholder`；空输入 typed `ProviderInputError`；文档明示 experimental 占位与替换路径 |
| `src/infrastructure/providers/runtime.py` | translation 段注册 `identity-translation` slot（无 requirements/gate、离线 ready，note 标 EXPERIMENTAL）；导出常量 |
| `tests/providers/test_translation_identity.py`（新增） | 9 例：语义/provenance/空输入、registry 注册与 ready、四种绑定形状解析、无绑定/未知/禁用/能力不匹配 typed 拒绝 |
| `tests/providers/test_handlers_pipeline.py` | +2：identity 绑定的 translate step 落库（machine==OCR 源）+ 无绑定 typed 失败且数据不变；fixture registry 注册同一生产 provider |
| `tests/core/test_pipeline_defaults_service.py` | +1：默认绑定持久化 → Run 快照 → `chain_from_binding`；override 优先且不回写默认 |

## 3. AC3 结果（详见 `verification/TRANSLATE-PROVIDER-1/REPORT.md` §3 / `run-summary.json`）

| 变体 | run 终态 | translate | 下游 |
|---|---|---|---|
| `identity`（StartRun override） | **completed**（82.1s） | 3/3 页、22/22 units completed | render 22/22 completed |
| `default-binding`（持久化默认绑定） | **completed**（82.4s） | 3/3 页、22/22 units completed | render 22/22 completed |
| `no-binding`（对照） | completed_with_failures | 3 页 typed `PROVIDER_NOT_CONFIGURED`（数据不变） | 未规划下游 |

逐页：1–3 页（E04P02/E04P03/E04P06）9/6/7 个 Region 全部走通到 render；4–8 页（E20P01–P05）detect 0 region → 任务 completed（`empty_detection`）。

**RELEASE-REPACK-1 新 exe 见证**（`evidence/new-sidecar-run.json`，真实 spawn/wire）：
- exe sha `9fcb9e8750ff7a52bc7ab5467f261ca689114a059874f9223054022ac41331dd`（新）对照旧 frozen `2b36bfeb…`（`sidecar-provenance.json`）。
- 8 页 Run `completed_with_failures`（9.35s）：页 1–3 detect/ocr/color/term_extract 全 completed，**translate typed `PROVIDER_NOT_CONFIGURED`**（该 exe 构建于本 provider 之前）；页 4–8 completed。
- 结论：新 exe 上唯一 translate 缺口是 provider 未注入；源码直跑已证明注入后 translate→render 全通。**下一次 RELEASE-REPACK 重打包即同构建全链路**（工具已就绪：`tools/run_new_sidecar_probe.py --with-translate-binding`）。

**环境瞬态（如实）**：`default-binding` 首跑页 8 detect 一次 `PROVIDER_FAILED: [Errno 22]`，同参数重跑 8/8 全 completed；判为连续 heavy run 的 Windows/ORT 瞬态，最终证据采用重跑绿色结果。

## 4. 关键决策（Record Decision 摘要；完整见 REPORT §6）

1. **语义/质量**：identity = 输入输出完全相同的 **EXPERIMENTAL 占位**，不含任何翻译能力；落库/导出可识别（provider_id/type/model/options）。**不得作为产品翻译质量宣发**。
2. **只显式生效**：无条件注册但绝不隐式选择；无绑定仍是 typed `PROVIDER_NOT_CONFIGURED`（对照变体实测）。
3. **替换路径零代码**：改绑定到 `openai-compatible-translation` / `sakura-local` / 用户 profile 即可；绑定是 Run 冻结快照。
4. **未放宽校验**：provider 输入校验、registry fail-closed、错误分类均未改动；未新增协议/设置面。
5. **不改 packaging**：identity 进入 exe 由 RELEASE-REPACK-1 下一次重打包完成（本卡只读消费其现有构建并记录缺口）。

## 5. 门禁

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/TRANSLATE-PROVIDER-1.md` → PASS（见 Task 卡收口记录）。
- Canonical Evidence：64-hex sha256 pin、commit 列留空；Resource Manifest 指向 task-env。
- 未 push、未 gc/prune。

## 6. 遗留

1. 同构建全链路（新 exe 内含 identity）待 RELEASE-REPACK-1 下一次重建后复验；本卡已给出可直接跑的探针。
2. 真实翻译质量（OpenAI-compatible / Sakura 配置与验收）不在本卡。
3. 页 1–3 translated artifact 的视觉/排版验收属 UI/渲染线。
4. heavy-run 瞬态 `[Errno 22]` 需另开诊断（非本卡 provider 逻辑）。
5. 需独立 Review（Owner 不得自审；reviewer=`dsh`）。
