# TASK-019 AC 状态分列（PASS / BLOCKED / NOT_RUN）

- Task：TASK-019「集成已验证的检测/OCR/翻译/修复 Provider」
- Owner：DeepSeek Harness（**作者**）／ Reviewer：Codex（**非作者**，集成由 Codex 执行）
- 固定 base：`36242fb`（代码基线）／交付 head：`5fdd80a`
- 环境：Windows 11 `10.0.26200`／Python 3.12.3（`G:/CODEX/New Manga.task-envs/TASK-012-py312`）／PySide6 6.11.2／pytest 9.1.1
- 环境实测：`torch`/`diffusers`/`numpy`/`paddleocr`/`paddle`/`manga_ocr`/`onnxruntime`/`openai`/`PIL`/`transformers` **全部不存在**；GPU 为 RTX 5070 Ti 16303 MiB（见 [`environment.json`](environment.json)）
- 证据总表：[`author-verification.md`](author-verification.md)

**判定口径**：`PASS` = 本环境有真实可复现证据；`BLOCKED` = 缺依赖/缺端点/缺实现，且**未**用 mock 或替身冒充真实模型或真实端点；`NOT_RUN` = 需外部条件（服务/端点/权重）尚未具备，本轮未运行。替身 Provider 只用于证明**集成语义**（写作用域、守卫、路由、错误码），**不作为模型质量或真实端点证据**。

## 1. 逐条 AC

| AC | 级别 | 判定 | 证据 / 原因 |
|---|---|---|---|
| AC-OCR-001 单 Region OCR | P0 | **PASS（集成语义）** | `tests/providers/test_handlers_pipeline.py::test_ocr_region_writes_only_the_target_region`：真实 SQLite + 真实 seam，目标 Region `ocr_text` 更新、新 RegionRevision 落库、pointer 前移、`pipeline_stage_states.ocr=completed`；同页 A/C 的 text/pointer/stage 完全未变。**真实 OCR 模型质量另列为 BLOCKED** |
| AC-OCR-001 真实识别质量（模型权重） | P0 | **BLOCKED** | 无 `manga_ocr`/`paddleocr`/`torch`；无权重与 hash。解锁：依赖获批 + 权重路径 + 可复现实测 |
| AC-OCR-004 韩漫 OCR | P1 | **BLOCKED（实现与路由已交付）** | `PaddleKoreanOcrProvider`（识别+检测、韩文/英文）+ 注册表项 `paddleocr-korean` 已交付并单测（引擎注入替身）；本机 `paddleocr`/`paddle` 缺失 → `missing_dependency`。解锁：安装依赖 + 韩文权重 + hash 留档 |
| AC-OCR-004 艺术字 fallback 仅在已配置规则下执行 | P1 | **PASS** | `chain_from_binding` 只读取 binding 中的显式 `fallback`；`test_chain_without_configured_fallback_never_tries_another_provider`、`test_fallback_is_not_burned_on_non_retryable_failures`；Vision fallback 需在 binding 显式配置 + 端点已配置才 Ready |
| AC-INPAINT-001 Mask 持久化 | P0 | **PASS** | `segment` 写入 raw Mask revision、`mask_refine` 写入 refined revision（`artifact_revisions` + Managed Storage 真实文件）；`test_reinpaint_chain_persists_masks_and_clean_revisions` 重新读回并逐位解码（`decode_mask_payload`），`final_covers_raw=true`，`current_revision_id` 指向 refined revision |
| AC-INPAINT-002 新 Clean 不覆盖旧版本 | P0 | **PASS** | 第二次 `REINPAINT_REGION` 生成 revision 2，revision 1 行与文件保留；`new_revision_required=True`；`ArtifactStepWriter` 发布路径为内容新 revision（不可覆盖）。页面级命令另有累积证据：`test_page_scope_reinpaint_expands_to_regions_and_accumulates_clean`（同页 3 个 Region → 3 个 Clean revision，`source_artifact_revision_id` 依次串联、互不覆盖） |
| AC-INPAINT-003 Router provenance | P1 | **PASS** | Clean revision 的 `provenance_json` 记录 provider/model/options/`router_reason`/`fallback_chain`/`device`/`mask_params`（`test_reinpaint_chain_persists_masks_and_clean_revisions`）；`InpaintStepResult.provenance` 另记 `used_fallback` 与 `upstream_revision_id` |
| AC-INPAINT-004 Webtoon Color Route（可配置选择 + 可追踪） | P1 | **PASS（选择与追踪）** | `RoutePolicy.color_route` + `acceptable_routes()`：彩色/高复杂度场景只接受彩色路线，决策与候选及拒绝理由全部进 provenance（`test_router_selects_and_traces_the_colored_webtoon_route`、`test_inpaint.py` 路由组） |
| AC-INPAINT-004 真实彩色修复执行 | P1 | **BLOCKED** | BrushNet/PowerPaint 与 FLUX Fill 无实现（`implements=False`，R-007 门控）；缺 `torch`/`diffusers`/`numpy` 与权重。解锁：依赖获批 + 权重 + 显存实测 |
| AC-RFULL-001 完整链 | P0 | **BLOCKED（部分链路已打通）** | 实测：`REINPAINT_REGION` 的 `segment → mask_refine → inpaint` 全链通过；页面级 `REINPAINT_ALL` 展开为 Region 单元后 3 个 Region 全链通过且 Clean 累积（`test_page_scope_reinpaint_expands_to_regions_and_accumulates_clean`）；`RETRANSLATE_REGION` 的 `translate` 提交成功，`render` 在**规划阶段**即 `BLOCKED(missing_clean_artifact)`，无 StepRun。`color`/`term_extract`/`render` 的 handler **不在本 Task 允许路径**（`src/infrastructure/providers/**` 只覆盖 detection/OCR/translation/inpaint），故完整链不可在本 Task 内收口。解锁：Codex 明确 Render/Color/TermExtract handler 的归属与允许路径（见 Handoff 风险 R-2） |
| AC-RFULL-002 只写目标 Region | P0 | **PASS** | `test_ocr_region_writes_only_the_target_region`（A/C 的 text、current pointer、stage 全未变）+ `test_ocr_keeps_manual_translation_and_reports_the_hint`；写作用域由 `StepResult.output_target_ids` + 单 Region revision 保证 |
| AC-RFULL-003 Page / Region Lock 阻止 | P0 | **PASS（既有 planner + 本 Task 防御）** | 既有 `tests/pipeline/test_pipeline.py` 覆盖 `skip_lock`（回归运行通过）；本 Task 在写入侧新增同级守卫：`RegionStepWriter` 在 `BEGIN IMMEDIATE` 内比对期望 revision、拒绝 `region_locked`（`test_locked_region_refuses_ocr_and_translation_writes`） |
| AC-RFULL-004 专项 Lock 临时覆盖 | P0 | **PASS（既有 planner 行为，未回归）** | `tests/pipeline/test_pipeline.py`（`allow_lock_override` → 全 `run`，原锁值不变）在本次回归中通过；本 Task 未改 planner，也未新增覆盖语义 |
| AC-RFULL-005 人工结果保护点 | P0 | **PASS（既有保护 + 本 Task 提示）** | `test_ocr_keeps_manual_translation_and_reports_the_hint`：`edited_translation`/`final_translation`/`translation_locked` 保留，`retranslate_hint=true`；`test_locked_region_is_skipped_and_never_translated` 证明翻译锁 Region 不被机器结果覆盖 |
| AC-FALLBACK-001 无配置不跨 Provider | P0 | **PASS** | `run_chain` 在无显式 fallback 时**只**调用 primary（`test_chain_without_configured_fallback_never_tries_another_provider`）；缺 binding → 步骤失败为 `PROVIDER_NOT_CONFIGURED`（`test_missing_provider_binding_fails_closed`） |
| AC-FALLBACK-002 显式 fallback | P1 | **PASS** | `test_explicit_fallback_records_both_attempts`：provenance 记录 primary（失败）与 secondary（成功）两次尝试；非可重试错误不会消耗 fallback |
| AC-GPU-001 GPU OOM 不崩主程序 | P0 | **PASS（OOM 隔离与类型化）** | `DeviceManager.run_guarded` 将 OOM 类异常转为 `OUT_OF_MEMORY`、释放并发槽并允许卸载模型（`test_oom_is_typed_and_does_not_escape`、`test_oom_marker_detection`）；**真实 GPU OOM 复现为 NOT_RUN**（无运行时依赖） |
| AC-GPU-002 GPU Heavy 默认单并发 | P1 | **PASS** | `HeavyJobGate` 默认容量 1；双线程实测 `max_observed=1`、`serialised_count>=1`（`test_heavy_gate_serialises_to_one_slot_by_default`）；`ProviderDescriptor.heavy_gate_capacity` 仅在显式允许并发时为 2 |
| AC-GPU-003 CPU Fallback 可追踪 | P1 | **PASS** | `DeviceManager.plan()` 仅在 Provider 声明 `supports_cpu_fallback` 时回落，并产出 `device_fallback_reason`/`device_fell_back`（`test_cpu_fallback_only_when_the_provider_declares_it`）；否则抛 `DEVICE_UNAVAILABLE`（不伪造 GPU 执行） |
| AC-OPTIONAL-001 缺重型模型仍可启动 | P0 | **PASS** | `tests/providers/test_bootstrap_providers.py::test_production_stack_starts_without_heavy_runtimes`：真实 `assemble_services` 在本机（无 torch/numpy/OCR 运行时）构建成功并产出 readiness 报告 |
| AC-OPTIONAL-002 Provider 状态 | P1 | **PASS** | readiness 六态（ready/missing_dependency/not_configured/disabled/not_ready/unknown）；实测 `manga-ocr`/`paddleocr-korean` = `missing_dependency`、`openai-vision-ocr`/`openai-compatible-translation` = `not_configured`、四条学习型修复路线 = `not_ready(PROVIDER_NOT_IMPLEMENTED)`、两条 dependency-free 路线 = `ready`（[`readiness-report.json`](readiness-report.json)） |
| AC-MODEL-001 下载进度 | P1 | **PASS（生命周期）/ BLOCKED（真实权重下载）** | 进度回调、取消、失败可重试、下载后 hash 校验均有单测（`test_model_lifecycle.py`）；**真实权重下载 BLOCKED**：无 `source_url`、无权重来源与体积基准 |
| AC-MODEL-002 不完整模型不 Ready | P0 | **PASS** | 尺寸不符（中断）或 SHA-256 不匹配一律 `incomplete`，`is_ready/gate/load` 全部拒绝（`test_incomplete_download_never_becomes_ready`、`test_hash_mismatch_is_reported_as_incomplete`、`test_size_mismatch_marks_an_interrupted_download`） |
| AC-EXT-SAKURA-001 健康/就绪探测 | P2 | **PASS（探测实现）** | `SakuraProbe` 覆盖 ready / not_ready（服务在但无模型）/ invalid_response / unreachable / not_configured 五种结果与原因码；**U-6 范围可证**：只请求 `/models`（必要时 `/health`），报告字段集合固定且无任何显存/负载/吞吐字段（`test_probe_only_reads_health_and_readiness_endpoints`） |
| AC-EXT-SAKURA-001 真实服务验证 | P2 | **NOT_RUN** | 本机无 Sakura 实例。已用真实 `StdlibTransport` 对 `http://127.0.0.1:8080/v1` 执行一次真实探测：`reason_code=unreachable`、`detail=connection refused`、仅发出 1 个请求（[`sakura-probe-attempt.json`](sakura-probe-attempt.json)）。解锁：本机启动 Sakura 后重跑连接测试 |

## 2. 已登记阻塞项（释放时登记的输入缺口）——逐项如实分列

| 登记项 | 本轮判定 | 证据 / 说明 |
|---|---|---|
| 真实 OpenAI-compatible 端点未配置 | **NOT_RUN（依赖真实端点的行为）/ BLOCKED（成本、时延）** | 端点与模型未配置（未自行配置付费端点）；客户端、Vision OCR、远程翻译的协议行为经**注入 fake transport** 验证 HTTP 状态映射与 RegionID 校验，**该证据不作为真实端点证据**。解锁：用户提供端点，或明确取消该路线 |
| 本机未运行 Sakura | **NOT_RUN** | 见 AC-EXT-SAKURA-001 第二行：探测实现 PASS、真实服务验证 NOT_RUN |
| 无 `torch`/`diffusers`/`numpy`（依赖清单变更需用户批准） | **BLOCKED** | 环境实测全部缺失；本地 OCR（manga-ocr/PaddleOCR Korean）与四条学习型修复路线的**质量/性能**全部未产出数字。解锁条件：①用户批准依赖变更；②权重获取路径与 SHA-256；③可复现的 GPU/CPU 实测 |
| 完整链 `color`/`term_extract`/`render` handler 不在允许路径（**本轮新登记**） | **BLOCKED** | 见 AC-RFULL-001 行与 Handoff 风险 R-2；需 Codex 明确归属/范围，不得由本 Task 自行扩展 |

## 3. 未以任何形式冒充的部分（诚实边界）

- 未用 mock/替身结果声称任何 **OCR 识别质量、翻译质量、修复质量、成本或时延**；
- 未把「dependency-free 基线（simple-fill / edge-bleed）」表述为学习型模型；route table 明确区分 `implemented` 与 `not_implemented`（TASK-018 R-007）；
- 未把「配置齐备（Ready）」表述为「服务可达」：Sakura 与远程端点的可达性由连接测试报告；
- 未修改依赖清单、Schema、pipeline seam 本体、`AGENTS.md` 或其他 Task（允许路径核对见 [`changed-paths.txt`](changed-paths.txt)）。
