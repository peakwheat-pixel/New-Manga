# CORE-PIPELINE-FIX-1 交付报告（Core 语义小改：color analyzer + 空检测语义）

- Task: `doc/tasks/CORE-PIPELINE-FIX-1.md`（base `ce181ce0b`；本 Task 开工时 HEAD `146377373`）
- Owner: `baseline-scout`（DSH 委派）
- 证据目录: `verification/CORE-PIPELINE-FIX-1/`
- 结论: **AC1–AC5 全部达成**；遗留两件事（frozen sidecar 未重打包 / stdio 调度路径异常观察），见 §7。

---

## 1. AC1 — color analyzer 可用（不再 `PROVIDER_FAILED`）

### 改动
| 文件 | 改动 |
| --- | --- |
| `src/bootstrap/core_service.py` | 删除 `_StubStyleAnalyzer`（只有 `analyze_pixel_styles`，与 `SourceStyleAnalyzer.analyze` 契约不符）；`assemble_production_core()` 改为注入 `SourceStyleService(PillowSourceStyleAnalyzer())`（Qt-free 的已验证实现，`src/infrastructure/rendering/pillow_source_style.py`）。 |
| `src/infrastructure/providers/handlers.py` | `handle_color` 把 analyzer 抛出的非 `ProviderError` 异常包装为 typed `ProviderError`（code `PROVIDER_FAILED`，detail `source style analysis failed: ...`），保证失败仍是 typed，而不是裸 `AttributeError`/`ValueError`。 |

根因（诊断已完成于 `RUN-OCR-DIAG-1`）：`SourceStyleService.extract` 调 `self._analyzer.analyze(original_png, box)`，而 stub 没有 `analyze` → 每个 color 单元 `AttributeError` → executor 压平成 `PROVIDER_FAILED`。

### 证据
- 装配层：`tests/core/test_core_color_assembly.py` 断言生产装配注入的是 `PillowSourceStyleAnalyzer`，且该 pair 对真实 PNG 的 `extract(...)` 返回 `SourceStyle`。
- 处理器层：`tests/providers/test_color_handler.py`（3 例）——真实 analyzer 产出 `source_style`；无 analyzer → `PROVIDER_NOT_CONFIGURED`；analyzer 抛错 → `PROVIDER_FAILED` + `source style analysis failed`。
- 真实数据（同构建，见 §3）：pages 1–3 的 `color` 步骤 **3/3 `completed`**。

---

## 2. AC2 — 空检测语义（0 候选不再整页失败，且可观测）

### 语义
- 默认 `detect.empty_detection_policy = "complete"`：检测 0 候选 → detect 步骤 **completed（0 region）**，不下游造 Region；页面任务照常收尾。适用于封面/跨页/纯插画等无文字页。
- 可配 `"fail"`：保留原契约（typed `INVALID_INPUT: detector returned no candidates ...`）。
- 非法取值：回退默认 `complete` 并在 stderr 说明（不静默改变语义）。
- **可观测性**（用户要求 0 候选不得静默成功）：
  - `step_runs.output_json.detection` 增加 `candidate_count: 0` / `empty_detection: true` / `empty_detection_policy: "complete"`；
  - stderr 行 `[core.detect] page '...' produced 0 candidates; empty_detection_policy=complete -> step completed with 0 regions`；
  - 该页不产生 OCR/color 等步骤（0 region 无可执行目标）。
- **未放宽输入校验**：detect 帧校验、OCR 输入校验均未改动；错误输入仍按原语义报错。

### 改动
| 文件 | 改动 |
| --- | --- |
| `src/infrastructure/providers/handlers.py` | 新增 `EMPTY_DETECTION_POLICY_*` 常量、`_empty_detection_policy()`（读 `run.settings_snapshot["detect"]["empty_detection_policy"]`，不新增设置面）、`_log_empty_detection()`；`handle_detect` 0 候选分支按策略返回 completed(0 region)（含 provenance 标记）或抛 `ProviderInputError`。 |
| `src/application/tasks/service.py` | `_backfill_detected_regions`：detect 结果 `region_ids` 为空且 `detection.empty_detection` 为真时，`_cancel_remaining(run, task, unit)` 退役任务中仍为 `RUN` 的预规划 regionless 单元（否则它们会以 `step 'ocr' requires a Region target` 失败，整页仍报错）。 |

### 证据（单测/回归）
- `tests/providers/test_detect_handler.py`：默认策略 completed(0 region) + 输出标记；`policy=fail` → `INVALID_INPUT`/`COMPLETED_WITH_FAILURES`；非法策略回退 complete。
- `tests/pipeline/test_regionless_rebinding.py`：N3（page scope 0 候选 → 整 run `completed`，仅 `detect` 一条 step_run，OCR 未跑）、N3b（`policy=fail` 保留旧契约）、F3（回填边界：0 候选 → 任务 completed、无 region、无 fan-out）。
- 真实数据负向对照：`run-ac3-policy-fail.json` —— `policy=fail` 时 4–8 页 detect 全部 `failed INVALID_INPUT`（1–3 页仍跑到 color/term_extract）。

---

## 3. AC3 — 同构建复验（models 包 + 8 页整书 Run）

### 构建说明（必须如实记录）
- 被复验的 models 包：`G:\CODEX\New Manga.workspace\task-envs\FINAL-VALIDATION-1\out\NewManga-0.1.0-win-x64-models\app\core-sidecar`，其 frozen `core_service.exe` sha256 = `2b36bfebcf09ea118537a0bc77a6c7c9a47c8845d7a853bc60d56ed004ec519b`，**未改动**（PyInstaller 冻结二进制无法原地打补丁；重打包属发布步骤，本 Task 不做）。
- 复验方式：**同一 models 目录 + 同一私有数据根（BOOK-FIXTURE 副本）+ 同一请求序列**，用修复后的源码 Core（`assemble_production_core` + `PipelineService.execute_run`，即调度器 `run_pending_once` 实际调用的同一路径）在进程内执行。脚本 `tools/verify_inproc.py`（含环境变量、overrides、逐页/整书两种 scope）。
- 命令: `translate_untranslated`，book scope，`overrides.provider_bindings = {"ocr": "manga-ocr"}`（Host 侧绑定修复属 `RUN-BINDING-FIX-1`；不注入则该 run 仍停在 OCR `PROVIDER_NOT_CONFIGURED`，与诊断一致）。

### 整书结果（`run-ac3-default.json`）
- run 终态 `completed_with_failures`，总耗时 **4107 ms**；step 统计：`detect` 8/8 `completed`、`ocr` 3/3 `completed`、**`color` 3/3 `completed`**、`term_extract` 3/3 `completed`、`translate` 3 `failed`（typed `PROVIDER_NOT_CONFIGURED: no provider binding configured for step 'translate'`）。
- 页 1–3：检测到 13/6/7 个 region，OCR→color→term_extract 全通过，止于 `translate` 的 typed 缺口（未到 `segment/mask_refine/inpaint/render`，如实记录）。
- **页 4–8：`detect completed`（0 region）→ 页面任务 `completed`**（修复前为整页 `INVALID_INPUT` 失败）。

### 逐页状态与耗时（逐页隔离运行，`runs-per-page.json`）
| 页 | 文件 | 状态 | 耗时(ms) | 步骤结果 |
| --- | --- | --- | --- | --- |
| 1 | E04P02 | failed（仅 translate） | 3750.8 | detect/ocr/color/term_extract completed；translate `PROVIDER_NOT_CONFIGURED` |
| 2 | E04P03 | failed（仅 translate） | 2665.0 | 同上 |
| 3 | E04P06 | failed（仅 translate） | 2453.5 | 同上 |
| 4 | E20P01 | **completed** | 1626.2 | 仅 detect completed（0 region，`empty_detection=true`） |
| 5 | E20P02 | **completed** | 1595.4 | 同上 |
| 6 | E20P03 | **completed** | 1587.5 | 同上 |
| 7 | E20P04 | **completed** | 1731.4 | 同上 |
| 8 | E20P05 | **completed** | 1661.8 | 同上 |

负向对照 `policy=fail`（`run-ac3-policy-fail.json`）：页 4–8 `detect failed INVALID_INPUT`（旧契约保持可用），页 1–3 仍到 color/term_extract。

---

## 4. AC4 — 单测/回归

| 项目 | 基线 | 本次 | 结论 |
| --- | --- | --- | --- |
| `python -m pytest tests -q` | 3F / 2739P / 9S | **3F / 2753P / 9S**（+14 新增用例） | 失败集合逐一相同（`test_detection_manga_real`×2、`test_workbench_viewmodel`×1，均为既有环境性失败），**0 新增失败** |
| `apps/desktop-avalonia/scripts/test.ps1`（App/Host） | 161/161 | **162/162 passed** | 全绿（+1 为其它 Task 新增） |
| `apps/desktop/frontend` vitest | 60 文件 / 567 用例 | **60 文件 / 567 用例 passed** | 不变 |

日志：`pytest-full.log`、`dotnet-test.log`、`dotnet-summary.json`、`vitest.log`。

---

## 5. AC5 — 门禁

- `pwsh -NoProfile -File tools/governance/check.ps1 -TaskPath doc/tasks/CORE-PIPELINE-FIX-1.md`：PASS（见 Handoff 收口记录）。
- Canonical Evidence 采用 64-hex sha256 pin、commit 列留空；Resource Manifest 指向 `verification/CORE-PIPELINE-FIX-1/resource-manifest.json`。
- 未 push、未 `gc/prune`；未改协议/Host 契约/旧壳。

---

## 6. Record Decision：Core 语义变更

- **变更**：① color 步骤的生产装配由 stub 换成 `PillowSourceStyleAnalyzer`，并把 analyzer 失败收敛为 typed `PROVIDER_FAILED`；② detect 0 候选默认按 completed(0 region) 处理，并把过期 regionless 下游单元退役；`empty_detection_policy="fail"` 保留旧行为。
- **理由**：修复前所有 Run 在 color 必败（`AttributeError`），且无文字页（4–8 页）会整页 `INVALID_INPUT`，这两个语义共同阻断 Run 链路到达 translate/render；用户已授权 A+B 小改。
- **影响面**：仅 Core `src/**` 的两个语义点（`core_service` 装配点、`handlers.handle_detect/handle_color`、`PipelineService._backfill_detected_regions`）＋测试；协议、Host 契约、旧壳、设置面均未改。wire 输出新增的是 step output 里的可观测字段（向后兼容，旧消费者忽略即可）。
- **回退开关**：`detect.empty_detection_policy="fail"` 一键回到检测 0 候选即失败的旧语义；color 侧如需回退，可用 `source_styles=None` 恢复 `PROVIDER_NOT_CONFIGURED`（fail-closed），不涉及数据迁移。

---

## 7. 遗留与风险

1. **frozen models 包未重打包**：AC3 的实际执行体是修复后的源码 Core（同一 assembly/同一执行路径），`core_service.exe` 仍是旧二进制。发布前需要用 PyInstaller 重新打包并复跑本报告 §3 的 8 页脚本。
2. **stdio/调度线程路径异常（独立问题，未修复）**：用 `python -m bootstrap.core_service` 起进程、经 `StartRun` 由调度线程执行同一 8 页 Run 时，可复现 `detect` StepRun 停留在 `running`、下游 regionless `ocr` 以 `INVALID_INPUT: step 'ocr' requires a Region target` 失败（4–8 页仍整页失败）；同一份代码在进程内直接 `PipelineService.execute_run` 正常。已排除并发轮询干扰（`--sleep-poll` 复现）与本次语义改动在该路径的差异（`run_pending_once` 调用的也是 `execute_run`）。证据：`run-stdio-scheduler-anomaly*.json`（3 份）。该现象与 `CORE-PIPELINE-FIX-1` 两个语义点无关性尚未最终定位，建议单开诊断 Task（含 scheduler 线程 + `ThreadRoutedConnection`/`write_in_current_transaction` 事务路径）。
3. **translate 之后仍未验证**：本 Task 不引入翻译 provider，Run 止于 `translate` 的 typed `PROVIDER_NOT_CONFIGURED`；`segment/mask_refine/inpaint/render` 未到达，符合"未到 render 如实记录"。
