# AC5 回归证据：9 个失败是 pre-existing，不是本修复引入的

**产出**: 2026-10-20 · **对应**: `PDF-STREAM-FIX-1` AC5
**问题**：全量跑 `pytest tests` 得到 `9 failed, 2294 passed, 9 skipped`。
**必须回答**：这 9 个是我的改动造成的吗？

## 一、方法

**不是「看失败信息像不像我碰过的代码」——那是猜。**

**做法**：把工作区完全还原到**修复前的基线 commit** `d58748dee`，
**在其上跑同样的 9 个测试文件**。

```
git stash push -u -m "pdf-fix-wip"
git checkout d58748dee
python -m pytest <the 9 failing test files> -q
```

## 二、结果

```
9 failed, 146 passed, 1 skipped in 32.03s
```

**基线上一模一样失败 9 个。**

| 失败测试 | 基线 | 修复后 |
|---|---|---|
| `test_bootstrap_providers.py::test_production_stack_starts_without_heavy_runtimes` | **FAILED** | **FAILED** |
| `test_detection_manga_real.py::test_real_detection_returns_block_candidates` | **FAILED** | **FAILED** |
| `test_detection_manga_real.py::test_real_blank_page_yields_zero_candidates` | **FAILED** | **FAILED** |
| `test_devices.py::test_gpu_is_unavailable_without_a_runtime_but_reported_not_invented` | **FAILED** | **FAILED** |
| `test_devices.py::test_cpu_fallback_only_when_the_provider_declares_it` | **FAILED** | **FAILED** |
| `test_registry_readiness.py::test_real_environment_reports_optional_providers_as_not_ready` | **FAILED** | **FAILED** |
| `test_projection.py::test_pending_run_all_waiting_and_pause_stop_enabled` | **FAILED** | **FAILED** |
| `test_projection.py::test_button_matrix_all_statuses` | **FAILED** | **FAILED** |
| `test_workbench_viewmodel.py::test_pause_shows_optimistic_feedback_immediately` | **FAILED** | **FAILED** |

**9 / 9 在基线上同样失败。**

## 三、所以这 9 个是什么

### 6 个是 provider / 运行时环境问题

**典型失败信息**：

```
ports.providers.errors.ProviderError: PROVIDER_FAILED: manga detector engine
failed to load from G:\CODEX\New Manga.task-envs\M2-DOCTR-QUAL-C4\weights\
ogkalu-comic-text-and-bubble-detector:
AttributeError('module transformers has no attribute RTDetrV2ForObjectDetection')
```

**根因**：**安装的 `transformers` 版本没有 `RTDetrV2ForObjectDetection`。**

**这是环境问题，与 PDF 导出无关。**

**同类的还有 `test_devices.py`（GPU 可用性）与 `test_registry_readiness.py`（provider 就绪）。**

### 3 个是 workbench 的时序/投影测试

`test_projection.py`（2 个）与 `test_workbench_viewmodel.py`（1 个）。

**从名字看涉及 `pause` 的乐观反馈与时序。**

**本轮未深究根因**——**它们的目的是证明「与我的改动无关」，而这一点已经由基线对照证明了。**

## 四、这对本 Task 的含义

**本 Task 的改动只碰 `src/infrastructure/export/qt_free.py` 的一行。**

**而 9 个失败中没有一个在 `tests/export/` 或 `tests/security/`。**

**基线对照证明这 9 个与本次改动无关。**

**所以：本 Task 没有引入回归。**

## 五、但必须诚实记录三件事

### 5.1 全量套件不是绿的

**`9 failed, 2294 passed, 9 skipped`。**

**即使这 9 个是 pre-existing，全量也不是绿的。**

**所以不能写「全量测试通过」。**

### 5.2 这 9 个失败是项目的一个真实状态问题

**`transformers` 版本不匹配意味着 `paddleocr` / 漫画检测链路在本机不可用。**

**这与 r34 的记录一致**（`paddleocr` 在 Python 3.14 上 KO）。

**它应该被某个 Task 处理，但不在本 Task 范围。**

### 5.3 我没有修它们，也没有假装它们不存在

**本文件的作用就是让「9 failed」这个数字有一个可核对的解释，
而不是被下一个读者当成「本次改动引入的」。**

## 六、命令可复算

```
git checkout d58748dee
python -m pytest tests/providers/test_bootstrap_providers.py \
  tests/providers/test_detection_manga_real.py \
  tests/providers/test_devices.py \
  tests/providers/test_registry_readiness.py \
  tests/workbench -q
# -> 9 failed, 146 passed, 1 skipped
```

```
git checkout agent/dsh/PDF-STREAM-FIX-1
python -m pytest tests -q
# -> 9 failed, 2294 passed, 9 skipped
```

**两次的失败集合完全相同。**

## 七、明确未做

- **未修这 9 个失败**（不在本 Task 范围）
- **未深究 3 个 workbench 失败的根因**
- **未把这条环境问题立成 Task**（可能需要，但应由 Codex 裁定归属）
