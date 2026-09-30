---
task_id: M2-FIX-REGISTRY-READINESS-ENV
author: ZCode
recipient: Codex（转 DeepSeek Harness 非作者 Review）
base_commit: 46f079e8
delivery_head: 3e4c3b44
status: delivered
---

# Handoff：M2-FIX-REGISTRY-READINESS-ENV（test_registry_readiness 环境断言条件化）

## 交付结果

- **变更路径**（fix commit `3e4c3b44`）：仅
  `tests/providers/test_registry_readiness.py`——
  `test_no_model_runtime_is_installed_in_this_environment` 环境条件化（方案 a）。
  **零 conftest 改动**；`src/**`、`packaging/**`、`requirements*`、其他测试语义
  零触碰。
- **修复语义**：`torch` 在位（T1.1.1+ 主 venv 标志）→ `pytest.skip` 显式理由
  （引 T1.1.1 用户批准 requirements：`torch==2.14.0`；M2-PROD-DETECT-1：
  `transformers==5.17.0`+`safetensors`；闭包级保证由
  `packaging/m2ac5/core_sidecar.spec` `_assert_ml_closure` 构建期断言接管，
  M2-PROD-DETECT-2）。**原断言循环逐字未动**——无 torch 环境走修复前完全
  相同的判别路径（`diffusers`/`paddleocr`/`manga_ocr` 至今未获批，仍断言缺位）。
- **原始意图判定**（详见 Task「原始意图判定」小节）：该测试是 TASK-019 释放
  时登记缺口第 3 条「本环境无 torch/diffusers/numpy（已实测）」的测试化固化，
  守护 BLOCKED 分类的环境前提；T1.1.1 起合法依赖变化推翻前提 → 恒红（历轮
  「既有环境性失败」）。
- **commit 链**（branch `agent/zcode/M2-FIX-REGISTRY-ENV`，worktree
  `G:/CODEX/New Manga.worktrees/M2-REGISTRY-ENV-zcode`）：
  - `66ec6a6d` claim：status ready→in_progress + 意图判定结论登记 Task；
  - `3e4c3b44` fix（delivery head）；
  - 本 Handoff + Task 回填为第三提交（claim→fix→handoff，真实历史）。

## 验证证据

| AC/场景 | 实际命令/步骤 | 环境与被测 commit | 结果 | 日志/产物 |
|---|---|---|---|---|
| base 对照（修复前恒红） | `PYTHONPATH=src <venv>/Scripts/python.exe -m pytest tests/providers/test_registry_readiness.py -v`（fix 前，同 base 同 venv） | 主 venv `G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312` / `46f079e8` 工作区 | **1 failed, 7 passed**（`AssertionError: torch unexpectedly present`，torch 实际在位） | 本行命令在 fix 前可复现 |
| AC1 修复后单文件 | 同命令（fix 后，加 `-rs`） | 主 venv / `3e4c3b44` | **7 passed, 1 skipped** EXIT=0，skip 理由全文显式（引 T1.1.1 + DETECT-2 闭包断言） | `-rs` 输出 |
| AC1 无 torch 判别力（低成本模拟） | 受控 stub `importlib.util.find_spec` 直接驱动测试函数：(1) 全模块缺位；(2) 无 torch 但 `paddleocr` 漂移出现 | 主 venv python / `3e4c3b44` | (1) 断言循环逐字执行 → PASS（无 skip 无 fail）；(2) → `AssertionError`（TASK-019 原报警消息）。双路径均符合设计 | 探针脚本为临时文件，跑后已删；逻辑可由 diff 复核（skip 分支唯一触发条件 `find_spec("torch") is not None`） |
| AC2 providers 全套 | `PYTHONPATH=src <venv>/python -m pytest tests/providers -q` | 主 venv / `3e4c3b44` | **289 passed + 1 skipped**，EXIT=0 | — |
| AC2 m2_acceptance | `PYTHONPATH=src <venv>/python -m pytest tests/m2_acceptance -q` | 同上 | **35 passed**，EXIT=0 | — |
| AC2 core | `PYTHONPATH=src <venv>/python -m pytest tests/core -q`（stderr 有既有 QML 噪声，与断言无关） | 同上 | **77 passed**，EXIT=0 | — |
| AC2 合计口径 | 三套件相加 | 同上 | **401 passed + 1 skipped，0 failed**（设计决策预估「402 passed 0 failed」以实跑为准修正：本测试 failed→skipped，不产生 passed） | 本表三行 |
| AC3 纪律 | `git diff --check 46f079e8..HEAD`、`git diff --name-only 46f079e8..HEAD`、`git status --porcelain` | 本 worktree | PASS（见自检三项） | — |

未运行项：无 BLOCKED/NOT_RUN。说明：三套件修复前全套计数未重复实测（仅单文件
base 对照）——修复前全套=288 passed + 1 failed 可由「修复后 289+1 skip、唯一
变化即该测试」严格推出，未伪造实测。

## 接收方式

- 分支 `agent/zcode/M2-FIX-REGISTRY-ENV` @ worktree
  `G:/CODEX/New Manga.worktrees/M2-REGISTRY-ENV-zcode`，base `46f079e8`，
  delivery head `3e4c3b44`（+ 本文档提交）。
- 复现命令：见上表（venv=`G:/CODEX/New Manga.task-envs/T1.1.1-impl-py312`，
  `PYTHONPATH=src`，worktree 根目录运行）。
- 接收者检查建议：读 Task 意图判定小节与 fix diff；确认 skip 理由文本与
  `packaging/m2ac5/core_sidecar.spec` `_assert_ml_closure` 引用准确；抽跑
  AC1/AC2 两行命令。

## 下一任务建议（必填）

- Task ID / 标题：M2-FIX-REGISTRY-READINESS-ENV 的 DSH 非作者 Review（本
  Task 内闭环）；
- 推荐 Agent / Reviewer：DeepSeek Harness（非作者，符合 Task frontmatter）；
- 推荐原因与前置依赖：实现已交付，按「完成实现≠完成集成」需独立审查；
  无外部依赖；
- Recovery point：仓库 `G:/CODEX/New Manga`，worktree
  `G:/CODEX/New Manga.worktrees/M2-REGISTRY-ENV-zcode`，branch
  `agent/zcode/M2-FIX-REGISTRY-ENV`，base `46f079e8` / head `3e4c3b44`+
  handoff commit；
- 允许修改路径：Review 意见落 Review 文档 + 本 Task；若需改码，回本 worktree
  本 branch（fix 链）；
- 禁止范围与新增授权条件：不得改 `src/**`、`packaging/**`、`requirements*`、
  其他测试；把 skip 改为无条件删除（方案 b 类语义）须新授权；
- 交付物：REVIEW 文档（模板 `doc/templates/REVIEW.md`）；
- 验证命令、环境与完成 Gate：上表 AC1/AC2 命令 + `git diff --check
  46f079e8..HEAD` EXIT=0 + 变更范围仅 `tests/providers/
  test_registry_readiness.py` + Task + Handoff；
- 可直接转发给 Agent 的指令：「对 M2-FIX-REGISTRY-READINESS-ENV 做非作者
  Review：读 doc/tasks/M2-FIX-REGISTRY-READINESS-ENV.md（含意图判定小节）与
  doc/handoffs/M2-FIX-REGISTRY-READINESS-ENV-3e4c3b44.md，复核
  tests/providers/test_registry_readiness.py 的条件化修复（重点：原始意图
  判定是否成立、skip 理由文本事实准确性、无 torch 环境验证力保留、三套件
  计数口径），产出 REVIEW 文档；禁止修改实现与共享契约。」

## 风险与遗留

- **口径同步**：STATUS/后续 Task 测试表的「+1 既有环境性失败」条目随本 Task
  终结；integrator 验收后建议在 STATUS 注记新口径「providers 289+1 skipped」
  （Task AC2 已含该请求）。
- 无 torch 环境的行为未在真实裸环境实测（本机可用 Python 均带 ML 栈），以
  受控 stub 模拟替代（AC1 允许「低成本模拟」）；若未来出现真实无 torch CI，
  该测试将自动恢复原判别路径，无需再改。
- skip 触发信号是单一 `torch` 探测：理论上存在「无 torch 但 numpy 在位」的
  环境会走断言并报 numpy——这是保留的漂移报警（numpy 亦属 TASK-019 断言
  面），非缺陷。
- 关联：TASK-019（意图来源）、M2-PROD-DETECT-1（历轮登记遗留、遗留
  slice③）、M2-PROD-DETECT-2（构建期闭包断言现状）、GOAL.md T3。
