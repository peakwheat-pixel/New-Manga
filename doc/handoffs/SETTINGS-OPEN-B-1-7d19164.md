---
task_id: SETTINGS-OPEN-B-1
author: dsh (Lead, epoch 10)
recipient: Codex / 下一批次 Owner
base_commit: da3b781d8971dcc36bd7bfd1165fa1a2f4519ea5
delivery_head: 3ec334f77405de08be2f276b10522a12ce3503cb
status: in_review
---

# Handoff — SETTINGS-OPEN-B-1（批次 B-1：模型/GPU + 任务/并发）

## 1. 交付摘要

按 [SETTINGS 分区 Schema 设计](../design/SETTINGS_SECTION_SCHEMAS.md) §4.1–§4.2，开放设置页 **模型/GPU** 与 **任务/并发** 两个分类：

- **写入校验**：[settings_sections.py](../../src/bootstrap/settings_sections.py) 新增 `model_gpu`（`device_preference: auto|cpu|gpu`、`allow_cpu_fallback: bool`）与 `tasks`（`retry_max_attempts: int 1–3`、`retry_backoff_seconds: float 0.1–30`）两节白名单；未知键/非法值 `INVALID_REQUEST` 且不落库。
- **模型/GPU 消费点**：Run 快照 `model_gpu` → `handlers._invoke_provider` → `heavy_runner` → `ProviderRuntime.heavy_runner` → `DeviceManager.run_guarded`。`auto`（默认）保持历史行为（不调用 `plan`）；`cpu`/`gpu` 显式偏好经 `DeviceManager.plan` 校验，GPU 不可用且 `allow_cpu_fallback=false` 或 Provider 不支持回退 → typed `DeviceUnavailable`（D06 §82 的"用户开关 AND Provider 声明"）。
- **任务/并发消费点**：`_retry_policy_for_run(run)` 按 Run 快照 `tasks` 构造 `RetryPolicy`；未设置节时返回装配期 `deps.retry_policy` 同一对象（逐位等价）；`retry_codes` / `retry_after_provider` 保留。
- **前端**：`ModelGpuSettingsPanel`、`TasksSettingsPanel`（真实下拉/开关/数字输入 + 保存 + 错误投影 + 生效说明）；分类矩阵 8 开 4 关；`task_concurrency` 只显示"任务串行执行（并发数不开放）"。
- **契约**：M2-C1 §5.3 与 P15 §7 的增量修订注记追加 B-1 两节；设计 §4.1–§4.2 冻结。

## 2. 验证

| 命令 | 结果 |
|---|---|
| `python -m pytest tests/core tests/providers -q --ignore=tests/providers/test_detection_manga_real.py` | 1212 passed / 3 skipped / exit 0（Lead 独立重跑一致） |
| `python -m pytest tests -q`（全量） | 2544 passed / 3 failed（3 个均为既有环境/基线失败，见 core-report §5.4） |
| `npm --prefix apps/desktop/frontend test` | 39 files / 387 tests passed |
| `tsc --noEmit` | exit 0 |
| 新测试 | +108 pytest（60 settings / 38 handlers+runtime / 10 devices）、+20 vitest |

原始证据：[core-report.md](../../verification/SETTINGS-OPEN-B-1/core-report.md)、[ui-report.md](../../verification/SETTINGS-OPEN-B-1/ui-report.md)、`core-pytest-*.txt`、`frontend-*.txt`。

## 3. 未执行 / 遗留

1. **GUI 烟测 NOT_RUN**：需真实 Tauri + Python Core 集成环境（设置页两分区保存 + 重启复查）。集成阶段执行。
2. **真实 GPU 端到端 NOT_RUN**：本机无 GPU/torch；偏好分支用 `tests/providers/env_sim.py::gpu_state` 模拟覆盖，属 typed 单测证据。
3. **任务文本笔误**：验收命令中的 `tests/infrastructure` 不存在；设备测试在 `tests/providers/test_devices.py`（已记录）。
4. **未开放项（明确不做假控件）**：GPU 并发策略（单槽 gate 不变量）、模型下载/路径管理、设备状态只读展示（需新增 Tauri wire）、并发数（调度器强制串行）。
5. **契约一致性**：批次 A/B-1 的白名单扩展均通过 M2-C1 §5.3 / P15 §7 的增量注记记录，未改 wire 形状。

## 4. 独立 Review r1 与返修

- Review r1（`reviewer-settings-a`，commit `7d19164`）：**changes_requested**。报告 `verification/SETTINGS-OPEN-B-1/review-b1.md`。
  - **B1（blocker）**：`_invoke_provider` 从 provider **实例**读取 `requires_gpu`/`supports_cpu_fallback`，而真实 provider 不在实例上重复声明（声明在 `ProviderDescriptor`）→ `allow_cpu_fallback` 对生产 provider 永远为 False，CPU 回退不可达。**已修**：新增 `ProviderRegistry.descriptor(provider_id, *, capability=None)` 只读查询（capability 别名感知），handlers 改读 descriptor、缺失才回退实例属性；新增"descriptor True / 实例无属性 → 真实 DeviceManager 回退执行"回归与 OCR 端到端回退测试。
  - **M1（major）**：`DeviceManager.run_guarded` 调用 `plan` 后丢弃返回值。**裁决**：设备偏好是"校验/回退策略"而非强制设备（provider API 无 device 参数）；UI 文案与设计 §4.1 已同步（cpu=跳过 GPU 校验；gpu=校验可用性并按回退策略执行或拒绝；不强制 Provider 内部设备）。
  - **m1（minor）**：`_retry_policy_for_run` 对非 Mapping 快照应视为空节——`_section` 加 guard + 4 个参数化测试。
  - **M2/M3（治理）**：证据/pins/Handoff 已固定；B-2 批次在独立 Task 记录，其 WIP 未进入 B-1 交付 commit（可用 `git archive 3ec334f` 复核干净树）。
- 修复 commit：`3ec334f`；证据刷新：`2fdcd5d`、`e9c3b5f`。修复后 `pytest tests/core tests/providers --ignore=tests/providers/test_detection_manga_real.py` → **1251 passed / 3 skipped**（Lead 独立重跑 + core-report §8 原始日志）。
- 待复审（review-b1 的 B1/m1 闭环确认）。

## 5. 推荐下一步

批次 B-2：缓存/Revision 的清理操作面（`GetCleanupPreview` / `RunCleanup` / `RetryPendingCleanups`，接 `application/maintenance/cleanup.py`，需 Core + Tauri 命令与 UI）。再之后批次 C：回收站、备份/恢复、Plugin/Hooks（需新增 wire 与产品取舍）。指令见 Lead 最终回复。
