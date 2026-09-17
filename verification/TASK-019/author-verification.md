# TASK-019 作者取证：`5fdd80a`（Provider 集成）

- Task：TASK-019「集成已验证的检测/OCR/翻译/修复 Provider」
- Owner／作者：DeepSeek Harness ／ Reviewer：Codex（**非作者**，最终集成由 Codex 执行）
- 固定 base：`36242fb00f9f432ec66cc3c33afc167578d0f341`（代码基线）
- 分支 / 工作区：`agent/deepseek/TASK-019-provider-integration` ／ `G:/CODEX/New Manga.worktrees/TASK-019-deepseek`
- 交付 head：`5fdd80a`（实现提交 `8effbeb` + 守卫/一致性提交 `5fdd80a`；`07d78d3` 为开工的 `in_progress` 文档提交）
- AC 逐条判定：[`ac-status.md`](ac-status.md)

## 1. 交付范围（相对代码基线 `36242fb`）

| 路径 | 内容 |
|---|---|
| `src/ports/detection/ports.py` | 检测能力端口：候选多边形 + Tile→page 坐标映射（缺 origin 即失败）+ provenance |
| `src/ports/ocr/ports.py` | OCR 能力端口：Region crop 请求、结果 + 置信度、`needs_detection` 声明、prepare-only 写入契约（含期望 revision 守卫） |
| `src/ports/translation/ports.py`、`protocol.py` | 翻译能力端口；**TASK-017 分类器生产化**（吸收 R-001/R-002/R-003） |
| `src/ports/inpaint/ports.py` | 修复能力端口：`ImageFrame`/`BooleanMask`/`MaskRecord`、route 常量、非目标保护语义 |
| `src/ports/providers/errors.py`（新增）、`profiles.py`（+`CAPABILITY_DETECTION`） | 统一 provider 错误/就绪分类（D06 §56/§92）与能力常量扩展 |
| `src/infrastructure/devices/manager.py` | 设备探测（无 torch 即 `unavailable`）、GPU-heavy 单并发闸门、CPU fallback 声明策略、OOM 隔离 |
| `src/infrastructure/providers/dependencies.py` | 模块/权重/端点/凭据探测（TASK-018 R-002 风格），不安装、不假设 |
| `src/infrastructure/providers/registry.py` | Provider 描述符与六态就绪；解析失败一律 fail-closed |
| `src/infrastructure/providers/retry.py` / `fallback.py` | 有界重试（D06 §56）+ 重试不得改变 payload（§57）；**仅显式配置**的 fallback 链与双重尝试 provenance |
| `src/infrastructure/providers/openai_client.py` | OpenAI-compatible JSON 客户端（走既有 Transport）：HTTP 状态全映射、凭据/图片、错误不泄漏 secret |
| `src/infrastructure/providers/ocr_local.py` / `ocr_vision.py` | manga-ocr（recognition-only）、PaddleOCR Korean、Vision OCR（RegionID 不外泄、信封严格校验） |
| `src/infrastructure/providers/translation_openai.py` | 远程 OpenAI-compatible 与本地 Sakura 翻译（同一适配器，RegionID 协议校验） |
| `src/infrastructure/providers/inpaint_routes.py` / `inpaint_router.py` | **显式** route 表（implemented / not_implemented，R-007）、dependency-free Simple Fill 基线、非目标保护校验；Router 决策 + 彩色路线策略（AC-INPAINT-004） |
| `src/infrastructure/providers/sakura_probe.py` | Sakura 健康/就绪探测（U-6：只做健康与就绪） |
| `src/infrastructure/providers/models.py` | 模型生命周期：进度/取消/重试、尺寸+SHA-256 门控、懒加载、OOM 卸载 |
| `src/infrastructure/providers/step_writes.py` | seam 兼容的 **prepare-only** 写入：Region revision + `text_json`（不动 pointer）、artifact revision + 发布（不动 pointer）、region 级 artifact 的 CAS 指针收编 |
| `src/infrastructure/providers/handlers.py` | `ocr`/`translate`/`segment`/`mask_refine`/`inpaint` 生产 handler，保留 provider 错误码穿越 seam |
| `src/infrastructure/providers/runtime.py` | 注册表装配（本地/远程/学习型）与 settings 契约 |
| `src/application/translation/inpaint/mask.py` / `step.py` | Mask 几何/细化（不变量：final covers raw）与 Inpaint Step 编排（路由阻断、fallback 链、非目标保护、新 revision） |
| `src/bootstrap/app.py` | **注入真实 handler 与 provider runtime**（`build_production_pipeline(conn, handlers=...)`），并提供 Managed Copy 像素/裁剪与 Region 几何来源 |
| `tests/providers/**`（新增 12 文件） | 109 例：端口契约、就绪/缺依赖 fail-closed、retry/fallback、RegionID 协议、远程适配器、Sakura 探测、设备/OOM、模型生命周期、修复路由、seam 集成 |

`git diff --check 36242fb..5fdd80a` → **退出码 0**（无输出）。允许路径：`git diff --name-only c9eb65a..HEAD` 共 46 条，**0 条越界**（未触碰依赖清单、Schema/migration、`src/infrastructure/pipeline/**`、`src/application/translation/pipeline/**`、`AGENTS.md`、其他 Task 或生产数据）。

## 2. 关键设计决策（交付时需 Reviewer 重点看）

### 2.1 写作用域：handler 只准备内容，pointer 仍归 seam

`ProductionStepExecutor` → `PipelineService.commit_step_result` → `SqliteTargetCatalog.commit_step` 是唯一的目标指针写入点。为保持该 seam 的乐观守卫（D06 §90）仍权威，本 Task **不**在 handler 内移动 pipeline 可见的指针：

- **Region 文本**：`RegionStepWriter` 在 `BEGIN IMMEDIATE` 内插入新 `region_revisions` 行并更新 `regions.text_json`，**不**改 `current_revision_id`；`StepResult.revision_updates={"region": <new>}` 由 seam 收编。
- **页面 artifact（page 目标）**：`ArtifactStepWriter` 发布不可变文件 + 插入 `artifact_revisions` 行，**不**改 artifact pointer；`StepResult.revision_updates={"mask"/"clean": <new>}` 由 seam 收编。
- **Region 目标的 artifact（`REINPAINT_REGION` 等）**：seam 对 region 目标只接受 `{"region": …}`，无法表达页面 artifact 指针，因此由 `ArtifactStepWriter.adopt_current()` 以**同样的 CAS 语义**完成指针收编，`StepResult` 不带 revision 更新。
- 两侧都在写前用**期望当前 revision** 校验（`expected_current_revision_id`）：region 侧在事务内比对，artifact 侧在发布前比对；不匹配即 `LOCK_CHANGED`，**不产生任何写入**。
- 残留窗口（已知、已登记）：prepare 与 seam 收编之间存在极小的并发窗口。若该窗口内发生并发写，region 文本已在事务外提交、seam 会把该步骤记为 candidate 而不收编指针。本 Task 无法在不改 seam 的前提下完全消除；见 §5 风险 R-1。

### 2.2 fail-closed 与诚实分类

- 未实现的修复路线：`RouteRecord(state="not_implemented", provider_id=…)`，`route_gate()` **先判可实现性再判依赖**；Router 只输出被策略接受且 runnable 的路线，否则 BLOCKED 并给出逐候选理由。
- 彩色/高复杂度场景**不接受**单色基线（`acceptable_routes()`）：宁可 BLOCKED 也不静默降级（AC-INPAINT-004 的可追踪性由此成立）。
- provider 错误码穿越 seam：handler 捕获 `ProviderError` 并抛 `StepExecutionError(error_code, …)`，因此 StepRun 保留 `PROVIDER_NOT_CONFIGURED`/`PROVIDER_NOT_IMPLEMENTED`/`LOCK_CHANGED` 等可诊断码，而不是被压平成 `PROVIDER_FAILED`。
- Sakura/远程端点的「Ready」只表示**配置齐备**；可达性由连接测试（`SakuraProbe`）报告，不把配置事实表述为服务事实。

## 3. 验证证据（逐命令、退出码、passed/skipped）

环境：Windows 11 `10.0.26200`；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1）；`$env:PYTHONDONTWRITEBYTECODE='1'`；未设置 `QT_QPA_PLATFORM`。原始日志见同目录 `pytest-*.log`。

| # | 命令（原样） | 退出码 | passed | skipped | 结果 |
|---|---|---:|---:|---:|---|
| 0 | `python -m pytest -q -p no:cacheprovider`（**基线** `c9eb65a`，改动前） | 0 | **530** | **6** | 改动前全仓基线 |
| 1 | `python -m pytest tests/providers -q -p no:cacheprovider -rs` | **0** | **109** | **0** | 本 Task 新建套件全绿（`pytest-providers.log`） |
| 2 | `python -m pytest tests/pipeline tests/core tests/storage -q -p no:cacheprovider -rs` | **0** | **78** | **0** | 强制回归：seam/bootstrap/storage 未回归（`pytest-regression.log`） |
| 3 | `python -m pytest -q -p no:cacheprovider -rs` | **0** | **639** | **6** | 全仓（基线 530 → 639，+109 均为本 Task 新增）（`pytest-full.log`） |
| 4 | `git diff --check 36242fb..5fdd80a` | **0** | — | — | 无输出（无空白错误） |
| 5 | 允许路径核对 `git diff --name-only c9eb65a..HEAD` | — | — | — | 46/46 在允许范围内；禁止路径命中 **0**（`changed-paths.txt`） |
| 6 | readiness 报告导出（真实装配） | **0** | — | — | `readiness-report.json`（六态与 `not_implemented` 分类） |
| 7 | 真实 Sakura 探测（`StdlibTransport`，`127.0.0.1:8080`） | **0** | — | — | `sakura-probe-attempt.json`：`unreachable` / `connection refused` / 仅 1 个请求 |

**skip 明细（命令 0 与 3 相同，6 条全部来自既有 `tests/network`，与本 Task 无关）**：

| 位置 | skip 原因 |
|---|---|
| `tests/network/test_connection_tester.py:106` | `openssl unavailable` |
| `tests/network/test_transport_tls.py:39` | `openssl unavailable` |
| `tests/network/test_transport_tls.py:47` | `openssl unavailable` |
| `tests/network/test_transport_tls.py:62` | `openssl unavailable` |
| `tests/network/test_transport_tls.py:69` | `openssl unavailable` |
| `tests/network/test_transport_tls.py:83` | `openssl unavailable` |

本 Task 新增套件 **0 skipped**（无网络、无模型、无 Qt 依赖；唯一使用 PySide6 的 `test_bootstrap_providers.py` 走真实 `assemble_services`，环境已安装 PySide6）。

**环境实测**（`environment.json`）：`torch`/`diffusers`/`numpy`/`paddleocr`/`paddle`/`manga_ocr`/`onnxruntime`/`openai`/`PIL`/`transformers` 全部 `false`；GPU `NVIDIA GeForce RTX 5070 Ti, 16303 MiB, driver 616.92`（有 GPU ≠ 有可用运行时）。

**真实探测（非 mock）**：命令 7 使用生产 `SakuraProbe` + `StdlibTransport` 对默认本地端点发起真实 TCP 连接，得到 `connection refused`，`reason_code=unreachable`，请求列表仅 `/v1/models` —— 既证明探测可用，也证明 U-6 范围（不采集显存/负载）与「真实 Sakura 服务验证 NOT_RUN」的事实。

## 4. 未运行 / 未产出（诚实清单）

| 项 | 状态 | 原因 |
|---|---|---|
| 真实 OCR 识别质量（含韩漫、艺术字、长图） | **BLOCKED** | 无 `manga_ocr`/`paddleocr`/权重；未产出任何准确率数字 |
| 真实翻译质量（远程端点或本地 Sakura） | **BLOCKED / NOT_RUN** | 端点未配置（禁止自行配置付费端点）；本机无 Sakura |
| 真实修复质量（Manga LaMa / AOT-GAN / BrushNet / FLUX） | **BLOCKED** | 无实现、无依赖、无权重；未新增任何质量/耗时/显存数字 |
| 成本、时延、吞吐 | **BLOCKED** | 同上；未用 mock 时延冒充 |
| 真实 GPU OOM 复现 | **NOT_RUN** | 无 GPU 运行时；OOM 隔离以异常类型化单测证明 |
| 真实权重下载与进度 | **BLOCKED** | 未配置 `source_url`；下载器为真实 Transport 实现但无来源 |
| `color`/`term_extract`/`render` 步骤接线（完整链） | **BLOCKED** | handler 不在本 Task 允许路径；需 Codex 明确归属（风险 R-2） |
| AC-EXT-SAKURA-001 真实服务验证 | **NOT_RUN** | 本机无 Sakura 实例 |

## 5. 风险与遗留

| ID | 风险 | 处置建议 |
|---|---|---|
| R-1 | prepare-only 写入与 seam 收编之间存在极小并发窗口（§2.1）；窗口内并发写会让 region 文本已提交而指针未收编（步骤记 candidate） | 已用写前期望 revision 校验把窗口压到最小。若要彻底消除，需要 seam 支持「内容 + 指针同事务」的提交入口——属 `src/infrastructure/pipeline/**`，超出本 Task 允许路径，交 Codex 裁决 |
| R-2 | 完整链（AC-RFULL-001）缺 `color`/`term_extract`/`render` handler，且 `render` 在规划阶段即 `missing_clean_artifact` | 请 Codex 明确这三步 handler 的归属 Task 与允许路径；在补齐前 AC-RFULL-001 保持 BLOCKED |
| R-3 | 修复路线的「彩色/复杂场景不接受单色基线」是本 Task 的 fail-closed 裁决，D06 §21 只给了策略示例 | 若产品希望降级到基线，需要用户裁决并在设置中显式允许；当前实现不会静默降级 |
| R-4 | TASK-017 报告 §4.1 提醒：除 401/403/429 外的其余 4xx 被显式归为不可重试请求侧错误；生产是否需要区分 408 等边缘状态 | 本 Task 沿用该口径并单测锁定；如需细原子集，应在网络栈单独裁决，不要直接照搬 |
| R-5 | **疑似跨 Task 缺陷（非本 Task 引入，未修改）**：普通新建 Region 的 `sfx_policy` 默认 `'skip'`，而 `PipelineService._decide_step` 对 `skip/manual` 一律跳过 `translate`/`segment`/`mask_refine`/`inpaint`/`render`（不限 `region_type='sfx'`），因此**真实使用中普通对白 Region 的翻译/修复步骤会持续 `SKIP_POLICY`** | 证据：`src/infrastructure/sqlite/schema.py:229`（`DEFAULT 'skip'`）、`src/application/editing/service.py:254`（`create_region(sfx_policy=SfxPolicy.SKIP)`）、`src/domain/regions/entities.py:230`（域默认 SKIP）、`src/application/tasks/service.py:353-361`（skip/manual → SKIP_POLICY）、`src/infrastructure/sqlite/pipeline.py:709`（从 DB 列读取）与同一文件 `:103`／`src/domain/tasks/models.py:182`（快照默认却是 `"translate"`，两处口径不一致）；`src/ui/**` 中无任何 `sfx_policy` 写入路径（grep 0 命中），`tests/pipeline/test_pipeline.py:47` 的辅助函数默认写 `"translate"`。本 Task 未改动该行为（不在允许路径），集成夹具显式置 `sfx_policy='translate'`。**请 Codex 核对是否为既有设计意图**；若确认为缺陷，其影响面（P0 级：翻译链在真实使用中不执行）超出本 Task 范围 |
| R-6 | 本 Task 新建 `src/ports/providers/errors.py`（共享错误/就绪分类）属 `src/ports/providers/**` 内的**新增模块**，而非既有字段扩展 | 任务文本允许该 glob 但限定「仅扩展 capability/可选字段」；此处按「新增文件不改变既有语义、不破坏既有测试」处理（`profiles.py` 仅加常量）。如判定越界，请退回并指定共享错误分类的落点 |

## 6. 边界与合规

- 仅修改允许路径；**未修改**依赖清单（`requirements*.txt`/`pyproject.toml`）、Schema/migration、pipeline seam 本体、`AGENTS.md`、其他 Task、生产数据或用户源文件。
- 未 `push`、未合并 `master`；未自行配置任何付费端点；未安装任何第三方依赖。
- Secret 未进入代码、测试、日志或报告：客户端仅从凭据 vault 解析；单测断言错误信息不含响应体与密钥（`test_http_status_mapping_is_total`、`test_client_attaches_credential_and_image_without_leaking_secret`）。
