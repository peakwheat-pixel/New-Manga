---
id: M2-FIX-REGISTRY-READINESS-ENV
title: "test_registry_readiness 环境断言条件化（遗留 slice③；Goal T3，自治执行 2026-10-01）"
kind: fix
status: ready
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

- [ ] AC1 修复：条件化/改写 + 测试在新 venv PASS 或 skip（显式理由）+ 在无 torch 环境的判别力论证（如可低成本模拟）
- [ ] AC2 回归：pytest 三套件全绿（无 failed）；基数变化如实登记
- [ ] AC3 纪律：diff --check；仅 tests/**（如需 conftest 最小适配）+ Task/Handoff

## 允许/禁止

允许：`tests/providers/test_registry_readiness.py`、相关 conftest、Task/Handoff。禁止：src/**、packaging/**、其他测试语义。
