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

未运行项：无 BLOCKED/NOT_RUN。基线口径（R-B1 修正）：修复前全套计数取仓库
**既有实测记录**而非自行推导——providers **289 passed + 1 failed**、三套件
合计 **401 passed + 1 failed**（`verification/M2-PROD-DETECT-2/release-notes.md:67`）；
290 个测试项在修复前后数量不变，唯一变化是该项 failed→skipped（skip 不减
passed），故修复后 providers 289+1 skipped 自洽。

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

- Task ID / 标题：M2-FIX-REGISTRY-READINESS-ENV 集成（r1 全部 findings 已
  闭合，见上文「DSH r1 处置」小节）；可选：DSH r2 快速抽查（非阻塞）；
- 推荐 Agent / Reviewer：编排会话代行 Codex（集成）；可选抽查=DeepSeek
  Harness（非作者）；
- 推荐原因与前置依赖：r1 verdict=approved_with_conditions，两项 P3
  （R-B1/R-B2）与三项 P4（R-B3~R-B5）均已闭合并复跑（三套件 403 passed +
  1 skipped，0 failed）；r1 清单第 6 项 STATUS 新口径注记由集成方在集成时
  落地（本 Task 无 STATUS 路径）；无其他前置依赖；
- Recovery point：仓库 `G:/CODEX/New Manga`，worktree
  `G:/CODEX/New Manga.worktrees/M2-REGISTRY-ENV-zcode`，branch
  `agent/zcode/M2-FIX-REGISTRY-ENV`，base `46f079e8` / head=`3e4c3b44` fix +
  handoff commit + r1 返修 fix + 本文档提交（真实链见 `git log`）；
- 允许修改路径（集成方）：合并入 master + STATUS 口径注记（「providers 291
  passed + 1 skipped」+ 历轮「+1 既有环境性失败」条目终结）；
- 禁止范围与新增授权条件：不得改 `src/**`、`packaging/**`、`requirements*`、
  其他测试；把 skip 改为无条件删除（方案 b 类语义）须新授权；
- 交付物（集成方）：merge commit + STATUS 注记；
- 验证命令、环境与完成 Gate：`PYTHONPATH=src <主venv>/python -m pytest
  tests/providers tests/m2_acceptance tests/core -q -rs`（预期 403 passed +
  1 skipped 0 failed）+ `git diff --check 46f079e8..HEAD` EXIT=0 + 变更范围
  仅 `tests/providers/test_registry_readiness.py` + Task + Handoff；
- 可直接转发给 Agent 的指令：「对 M2-FIX-REGISTRY-READINESS-ENV 做集成前
  复验：读 doc/handoffs/M2-FIX-REGISTRY-READINESS-ENV-3e4c3b44.md 的『DSH
  r1 处置』小节，抽跑其复跑命令（三套件 -rs）确认 403 passed + 1 skipped
  0 failed 与新 skip 理由文本，然后按协作协议集成；集成时在 STATUS 注记
  新测试口径并删除历轮『+1 既有环境性失败』条目。禁止修改测试语义。」

## DSH r1 处置（review：G:/CODEX/New Manga.task-envs/M2-WEIGHTS-SOP/dsh-review-r1.md，verdict=approved_with_conditions）

r1 全部 findings 闭合（2×P3 + 3×P4，均为文档/注释/测试级，行为零变化），
返修 commit 为本 Handoff 之前的 `fix(M2-FIX-REGISTRY-READINESS-ENV): DSH r1
处置` 提交。逐条：

| Finding | 处置 |
|---|---|
| R-B1[P3] 修复前基线数字错误（288+1 推导） | 「未运行项」段已改为直引仓库既有实测：providers **289 passed + 1 failed**、三套件 **401 + 1 failed**（`verification/M2-PROD-DETECT-2/release-notes.md:67`）；删除自行推导句 |
| R-B2[P3] 「闭包断言接管」方向性不成立 | skip 理由与 docstring 改写：TASK-019 环境证据被 T1.1.1 合法依赖变化**作废**（INVALIDATED，非被替代转移）；发布侧 ML 闭包**完整性**由 `core_sidecar.spec` `_assert_ml_closure` 构建期断言**独立**保证，且方向相反（断言 ML 在闭包内 vs 本测试断言环境无 ML），docstring 明确「勿混同」 |
| R-B3[P4] skip 门只取 torch 未说明意图 | skip 语句旁一行注释 + docstring Known limitations：无 torch 环境五模块逐字断言（numpy-only 环境仍按漂移 FAIL）；ML venv 下未获批 provider 的缺位事实由 registry 探针测试覆盖——窄门是有意为之非 flaky |
| R-B4[P4] `find_spec` 存在性 vs 可导入性 | docstring Known limitations 登记：半装 torch（目录在但 import 坏）同样触发 skip；与原断言循环同探针，属逐字继承的已知盲区非本条件化引入的回归 |
| R-B5[P4] 判别力模拟不可复跑 | 固化为同文件参数化测试 `test_environment_assertion_discrimination_probe`（2 用例：torch-free 裸环境 → 逐字断言 PASS；torch-free + paddleocr 漂移 → 原 TASK-019 `AssertionError`），stub `find_spec` 驱动真实测试函数，任何机器（含 ML venv）可复跑 |

**r1 修后复跑**（主 venv `T1.1.1-impl-py312`，PYTHONPATH=src，`3e4c3b44`+
返修 commit）：单文件 `-rs` **9 passed, 1 skipped** EXIT=0（7 原有 + 2 探针
用例；新 skip 理由全文可见）；三套件 **providers 291 passed + 1 skipped /
m2_acceptance 35 passed / core 77 passed**——合计 **403 passed + 1 skipped，
0 failed**（计数变化 = +2 来自固化的判别力探针参数化用例，如实登记）。

## 风险与遗留

- **口径同步**：STATUS/后续 Task 测试表的「+1 既有环境性失败」条目随本 Task
  终结；integrator 验收后建议在 STATUS 注记新口径「providers 291 passed +
  1 skipped（289 基数 + 2 判别力探针用例；env-conditioned skip 1，理由见
  本 Task）」。
- 真实裸环境（完全无 ML 栈的 Python）仍未实测，但 R-B5 已把判别力模拟固化
  为可复跑参数化测试（stub `find_spec`，任何机器可跑）；若未来出现真实无
  torch CI，真实测试将自动恢复原判别路径，无需再改。
- skip 触发信号是单一 `torch` 探测：理论上存在「无 torch 但 numpy 在位」的
  环境会走断言并报 numpy——这是保留的漂移报警（numpy 亦属 TASK-019 断言
  面），非缺陷。
- 关联：TASK-019（意图来源）、M2-PROD-DETECT-1（历轮登记遗留、遗留
  slice③）、M2-PROD-DETECT-2（构建期闭包断言现状）、GOAL.md T3。
