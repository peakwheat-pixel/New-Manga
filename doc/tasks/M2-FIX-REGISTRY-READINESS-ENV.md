---
id: M2-FIX-REGISTRY-READINESS-ENV
title: "test_registry_readiness 环境断言条件化（遗留 slice③；Goal T3，自治执行 2026-10-01）"
kind: fix
status: in_review
approval: user_autonomous_mode_2026-10-01
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness（非作者）
integrator: 编排会话代行 Codex（用户全权授权+自治授权）
depends_on: []
base_commit: 095e314dad490781ec5d8c1b5b88d53ae0b5d39c
branch: agent/zcode/M2-FIX-REGISTRY-ENV
worktree: G:/CODEX/New Manga.worktrees/M2-REGISTRY-ENV-zcode
---

# M2-FIX-REGISTRY-READINESS-ENV：环境断言条件化

## 来源与目标

- 来源：M2-PROD-DETECT-1 起登记的既有环境性失败——`tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment` 断言当前 venv **无** torch/numpy（TASK-019 时代的环境证据），但 T1.1.1 起 主 venv 自带 torch，恒失败（base 同败，历轮 Task 如实登记为「既有」）。遗留 slice③（GOAL.md T3）。
- 目标：让该测试在新事实下恢复判别力且不再恒红。

## 设计决策（代理裁决）

1. 先读测试原文与 TASK-019/M2-AC3 语境，判定原始意图（大概率=「sidecar 闭包/registry readiness 假设无 ML runtime」的防护）。
2. 修复采**环境条件化**：ML runtime 在位时 `pytest.skip` 显式原因（「dev venv intentionally carries the ML stack since T1.1.1; closure-level assertion is enforced by packaging/m2ac5 warn/closure evidence (M2-PROD-DETECT-2)」），无 ML 环境保留原断言验证力；若读后发现断言意图已被 DETECT-2 的构建期闭包断言完全取代，也可改写断言语义（二选一，Owner 判断后在 Task 登记理由）。
3. pytest 三套件恢复全绿口径：**402 passed 0 failed**（401+本测试转 skip/pass——以实跑为准，如实记录计数变化并同步 STATUS 口径注记）。

## AC

- [x] AC1 修复：条件化/改写 + 测试在新 venv PASS 或 skip（显式理由）+ 在无 torch 环境的判别力论证（如可低成本模拟）—— 方案 a 落地（`tests/providers/test_registry_readiness.py`，fix commit 见 Handoff）：`torch` 在位（T1.1.1+ 主 venv 标志）→ `pytest.skip` 显式理由（引 T1.1.1 用户批准 requirements 事实 + `packaging/m2ac5/core_sidecar.spec` `_assert_ml_closure` 构建期闭包断言接管，M2-PROD-DETECT-2）；断言循环逐字未动。主 venv 实跑：`7 passed, 1 skipped` EXIT=0，skip 理由全文可见（`-rs`）。判别力低成本模拟（受控 stub `find_spec` 直接驱动测试函数，主 venv python）：[1] 全模块缺位（无 torch 环境等价）→ 断言循环逐字执行 PASS（无 skip 无 fail）；[2] 无 torch 但 `paddleocr` 漂移出现 → `AssertionError`（TASK-019 原报警消息）。双路径均符合设计。
- [x] AC2 回归：pytest 三套件全绿（无 failed）；基数变化如实登记—— 主 venv `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`（PYTHONPATH=src）：`tests/providers` **289 passed + 1 skipped**、`tests/m2_acceptance` **35 passed**、`tests/core` **77 passed**——三套件合计 **401 passed + 1 skipped，0 failed**（设计决策预估的「402 passed 0 failed」以实跑为准修正为「401 passed + 1 skipped + 0 failed」；本测试由 failed 转 skipped，不产生 passed）。**口径终结说明**：历轮 Task 测试表登记的「tests/providers +1 既有环境性失败（`test_no_model_runtime_is_installed_in_this_environment`）」自本 Task 交付起终结——后续 Task 测试表不再出现该项；providers 基数口径为「289 passed + 1 skipped（env-conditioned，理由见本 Task）」。
- [x] AC3 纪律：diff --check；仅 tests/**（如需 conftest 最小适配）+ Task/Handoff—— 变更仅 `tests/providers/test_registry_readiness.py` + 本 Task + Handoff，**零 conftest 改动**；`src/**`、`packaging/**`、`requirements*` 零触碰；base 对照留痕：修复前同 venv 同文件 `1 failed, 7 passed`（`AssertionError: torch unexpectedly present`，fix commit 前实测）。

## 允许/禁止

允许：`tests/providers/test_registry_readiness.py`、相关 conftest、Task/Handoff。禁止：src/**、packaging/**、其他测试语义。

## 原始意图判定（claim 时登记，Owner=ZCode）

1. **测试原文**：`tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment`（190-196 行）——对 `("torch", "diffusers", "numpy", "paddleocr", "manga_ocr")` 逐个 `assert importlib.util.find_spec(module) is None`，失败消息自述「the BLOCKED classification in doc/tasks/TASK-019.md assumes it is absent」。
2. **语境**：TASK-019 释放时登记缺口第 3 条「本环境无 `torch`/`diffusers`/`numpy`（已实测）……依赖模型权重的本地 OCR/修复质量类 AC 必须按 `BLOCKED` 交付」（`doc/tasks/TASK-019.md`）。该测试即这条**环境证据的测试化固化**：守护「BLOCKED 分类的环境前提=当前 venv 无 ML runtime」。它不是 registry/闭包语义防护（那些由同文件 `test_real_environment_reports_optional_providers_as_not_ready` 等测试与装配 fail-closed 承担，且在主 venv 本就 PASS）。
3. **前提失效原因**：T1.1.1 起用户批准 `requirements.txt` 携带 `torch==2.14.0`（M2-PROD-DETECT-1 追加 `transformers==5.17.0`+`safetensors`）；主 venv（`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`）torch 在位是合法产品事实，TASK-019 前提被合法依赖变化推翻——测试恒红（历轮如实登记「既有环境性失败」，base 同败已复现）。
4. **防护去向**：无-ML/闭包级部署保证已由构建期断言接管——`packaging/m2ac5/core_sidecar.spec` 的 `_assert_ml_closure`（ML_HIDDENIMPORTS 三 pin，DSH r1 R3）+ 分 entry warn-archive 证据（M2-PROD-DETECT-2 GATE 25/25）。
5. **裁决：方案 a（环境条件化）**——`torch` 在位（T1.1.1+ 主 venv 标志）→ `pytest.skip` 显式理由（引 T1.1.1 事实 + DETECT-2 构建期闭包断言）；无 torch 环境走与修复前**逐字相同**的断言循环（验证力原样保留）。不选方案 b（改写断言语义）：会连「无 ML 环境漂移报警」的判别力一并删除，且不可逆；方案 a 成本低、两类环境行为明确。注意 `diffusers`/`paddleocr`/`manga_ocr` 至今仍未获批（不在 requirements），无 torch 环境下原断言对它们继续有效。
