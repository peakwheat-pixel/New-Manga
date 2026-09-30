---
id: M2-FIX-REGISTRY-READINESS-ENV
title: "test_registry_readiness 环境断言条件化（遗留 slice③；Goal T3，自治执行 2026-10-01）"
kind: fix
status: done
integration_commit: 52b07438
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
2. 修复采**环境条件化**：ML runtime 在位时 `pytest.skip` 显式原因（「dev venv intentionally carries the ML stack since T1.1.1; closure-level assertion is enforced by packaging/m2ac5 warn/closure evidence (M2-PROD-DETECT-2)」（注：该事前表述的方向性已由意图判定第 4 条取代——TASK-019 证据系作废非转移，r2 P4-2 注记）），无 ML 环境保留原断言验证力；若读后发现断言意图已被 DETECT-2 的构建期闭包断言完全取代，也可改写断言语义（二选一，Owner 判断后在 Task 登记理由）。
3. pytest 三套件恢复全绿口径：**402 passed 0 failed**（401+本测试转 skip/pass——以实跑为准，如实记录计数变化并同步 STATUS 口径注记）。

## AC

- [x] AC1 修复：条件化/改写 + 测试在新 venv PASS 或 skip（显式理由）+ 在无 torch 环境的判别力论证（如可低成本模拟）—— 方案 a 落地（`tests/providers/test_registry_readiness.py`，fix commit 见 Handoff）：`torch` 在位（T1.1.1+ 主 venv 标志）→ `pytest.skip` 显式理由；断言循环逐字未动。主 venv 实跑：`7 passed, 1 skipped` EXIT=0，skip 理由全文可见（`-rs`）。判别力论证（DSH r1 R-B5 后**固化为可复跑参数化测试** `test_environment_assertion_discrimination_probe`，stub `find_spec` 驱动真实测试函数，同文件随套件执行）：[1] 全模块缺位（无 torch 环境等价）→ 断言循环逐字执行 PASS（无 skip 无 fail）；[2] 无 torch 但 `paddleocr` 漂移出现 → `AssertionError`（TASK-019 原报警消息）。双路径均符合设计。
- [x] AC2 回归：pytest 三套件全绿（无 failed）；基数变化如实登记—— 主 venv `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`（PYTHONPATH=src）：fix 时点 `tests/providers` **289 passed + 1 skipped**、`tests/m2_acceptance` **35 passed**、`tests/core` **77 passed**——三套件合计 **401 passed + 1 skipped，0 failed**（设计决策预估的「402 passed 0 failed」以实跑为准修正为「401 passed + 1 skipped + 0 failed」；本测试由 failed 转 skipped，不产生 passed）。**DSH r1 返修后**（R-B5 判别力探针固化为 2 个参数化用例）：providers **291 passed + 1 skipped**、m2_acceptance 35、core 77，合计 **403 passed + 1 skipped，0 failed**（+2 即探针用例，如实登记）。**口径终结说明**：历轮 Task 测试表登记的「tests/providers +1 既有环境性失败（`test_no_model_runtime_is_installed_in_this_environment`）」自本 Task 交付起终结——后续 Task 测试表不再出现该项；修复前基线以仓库既有实测为准（providers 289 passed + 1 failed、三套件 401 + 1 failed，`verification/M2-PROD-DETECT-2/release-notes.md:67`），providers 新口径「291 passed + 1 skipped（含 2 判别力探针用例）」。
- [x] AC3 纪律：diff --check；仅 tests/**（如需 conftest 最小适配）+ Task/Handoff—— 变更仅 `tests/providers/test_registry_readiness.py` + 本 Task + Handoff，**零 conftest 改动**；`src/**`、`packaging/**`、`requirements*` 零触碰；base 对照留痕：修复前同 venv 同文件 `1 failed, 7 passed`（`AssertionError: torch unexpectedly present`，fix commit 前实测）。

## 允许/禁止

允许：`tests/providers/test_registry_readiness.py`、相关 conftest、Task/Handoff。禁止：src/**、packaging/**、其他测试语义。

## 原始意图判定（claim 时登记，Owner=ZCode）

1. **测试原文**：`tests/providers/test_registry_readiness.py::test_no_model_runtime_is_installed_in_this_environment`（190-196 行）——对 `("torch", "diffusers", "numpy", "paddleocr", "manga_ocr")` 逐个 `assert importlib.util.find_spec(module) is None`，失败消息自述「the BLOCKED classification in doc/tasks/TASK-019.md assumes it is absent」。
2. **语境**：TASK-019 释放时登记缺口第 3 条「本环境无 `torch`/`diffusers`/`numpy`（已实测）……依赖模型权重的本地 OCR/修复质量类 AC 必须按 `BLOCKED` 交付」（`doc/tasks/TASK-019.md`）。该测试即这条**环境证据的测试化固化**：守护「BLOCKED 分类的环境前提=当前 venv 无 ML runtime」。它不是 registry/闭包语义防护（那些由同文件 `test_real_environment_reports_optional_providers_as_not_ready` 等测试与装配 fail-closed 承担，且在主 venv 本就 PASS）。
3. **前提失效原因**：T1.1.1 起用户批准 `requirements.txt` 携带 `torch==2.14.0`（M2-PROD-DETECT-1 追加 `transformers==5.17.0`+`safetensors`）；主 venv（`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`）torch 在位是合法产品事实，TASK-019 前提被合法依赖变化推翻——测试恒红（历轮如实登记「既有环境性失败」，base 同败已复现）。
4. **前提作废后的关系澄清（DSH r1 R-B2 口径）**：TASK-019 的环境证据随前提失效而**作废**，不存在「被构建期断言接管/替代」——发布侧 ML 闭包**完整性**由 `packaging/m2ac5/core_sidecar.spec` 的 `_assert_ml_closure`（ML_HIDDENIMPORTS 三 pin + 分 entry warn-archive 证据，M2-PROD-DETECT-2 GATE 25/25）**独立**保证，且方向相反（它断言 ML **在**发布闭包内，本测试断言开发环境**无** ML runtime），两者勿混同。
5. **裁决：方案 a（环境条件化）**——`torch` 在位（T1.1.1+ 主 venv 标志）→ `pytest.skip` 显式理由（引 T1.1.1 事实 + DETECT-2 构建期闭包断言）；无 torch 环境走与修复前**逐字相同**的断言循环（验证力原样保留）。不选方案 b（改写断言语义）：会连「无 ML 环境漂移报警」的判别力一并删除，且不可逆；方案 a 成本低、两类环境行为明确。注意 `diffusers`/`paddleocr`/`manga_ocr` 至今仍未获批（不在 requirements），无 torch 环境下原断言对它们继续有效。

## DSH r1 返修处置（2026-10-01，approved_with_conditions → 全 findings 闭合）

- **R-B1[P3] 已闭**：Handoff「未运行项」段的修复前基线改为直引仓库既有实测——providers **289 passed + 1 failed**、三套件 **401 + 1 failed**（`verification/M2-PROD-DETECT-2/release-notes.md:67`），删除「288+1 可推出」的错误推导句。
- **R-B2[P3] 已闭**：skip 理由与 docstring 改写为「TASK-019 环境证据**作废**（INVALIDATED，非被替代转移）；发布侧 ML 闭包完整性由 `core_sidecar.spec` `_assert_ml_closure` 构建期断言**独立**保证（方向相反，勿混同）」；本 Task 意图小节第 4 条同口径修正。
- **R-B3[P4] 已闭**：skip 门只取 torch 的意图写入 skip 语句旁注释 + docstring Known limitations。
- **R-B4[P4] 已闭**：`find_spec` 存在性 vs 可导入性盲区（半装 torch 同样触发 skip）登记 docstring Known limitations；与原断言循环同探针，属逐字继承非新回归。
- **R-B5[P4] 已闭**：判别力模拟固化为同文件参数化测试 `test_environment_assertion_discrimination_probe`（2 用例，stub `find_spec` 驱动真实测试函数，任何机器可复跑）。
- **修后复跑**：单文件 `-rs` **9 passed, 1 skipped** EXIT=0；三套件 providers **291 passed + 1 skipped** / m2_acceptance **35 passed** / core **77 passed**——合计 **403 passed + 1 skipped，0 failed**（+2 即探针用例）。

## 集成记录（2026-10-01，acting Codex）

DSH r1 approved_with_conditions → review-fix 全闭 → DSH r2 approved → 集成修正（P4 残留）→ merge `52b07438`。集成方复跑：main 三套件 **403 passed + 1 skipped, 0 failed**（EXIT=0，skip 理由逐字符合更正口径）——**历轮「+1 既有环境性失败」口径自此终结**，新基线=providers 291+1 skipped/35/77。详见 [integration.md](../../verification/M2-FIX-REGISTRY-READINESS-ENV/integration.md)。Owner branch/worktree 保留于 `75c72dfa`。
