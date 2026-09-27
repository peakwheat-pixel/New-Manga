---
task_id: M2-I1
reviewer: DeepSeek Harness
author: ZCode
decision: approved
base_commit: 6a68fdeb92d8a1c7903166a8076d6260bf8fa79a
review_baseline: 0275290c3cc64e92dc53157b7d35028447d4d54f
reconcile_base_commit: 7e2da6b8eb55e437d36fa3fa11cbf3e976a834c9
prior_review: 0766952684b733de263797ab6495930a9ff36cf4 (Codex approved)
product_delivery: 09ad43a03c324eb52def326a6b7a49cb3da03efa
handoff_head: 8dab0abbc667e09054616d4f0b0f5a76b1a04d9e
branch: agent/zcode/M2-I1-core-assembly-seam
worktree: G:/CODEX/New Manga.worktrees/M2-I1-zcode
integration_commit: null
---

# M2-I1 R3 reconcile — DeepSeek Harness 非作者 Review（2026-09-25）

## 范围与依据

审查对象：作者 ZCode 把已审 R2 交付（`0766952`，Codex Review `approved`）以 `--no-ff` 合并 `master@0275290`（含 M2-I2 集成基线 `7e2da6b`）后产生的新固定交付 `09ad43a`，以及 Handoff 提交 `8dab0ab`。Reviewer 非作者，未参与该实现。

依据：[M2-I1 Task](../../doc/tasks/M2-I1.md) I1-AC1～AC8 与允许/禁止范围、[R2 Review](M2-I1-0766952.md)、[R1 Review](M2-I1-a89447f.md)、[协作协议](../09_COLLABORATION.md)、[AGENTS.md](../../AGENTS.md)。

**merge 事实核查（本 Review 独立复算）**

| 项 | 命令 | 结果 |
|---|---|---|
| merge 结构 | `git log -1 --format=%P 09ad43a` | 双父：`cb45902`（作者分支 R2 Handoff head）+ `0275290`（review baseline，`--no-ff`），非 fast-forward |
| 作者历史保留 | `git merge-base --is-ancestor <c> 09ad43a` | `b8741eb` / `a89447f` / `0766952` / `cb45902` / `0275290` 全部 exit 0；四个 commit hash 与 Task/Handoff 记录逐字一致（无 rebase/改写） |
| 无产品改写 | `git diff cb45902 09ad43a -- src/bootstrap tests/core/test_bootstrap.py tests/core/test_core_assembly.py` | 空 = 作者 I1 产品文件与 R2 交付逐字节相同；blob hash `app.py=8278ca4`、`core_assembly.py=8d4a04d` 在 `0766952`/`cb45902`/`09ad43a` 三点一致 |
| 主线侧未被改写 | `git diff 0275290 09ad43a -- src/application src/ui tests/workbench tests/core/test_architecture.py` | 空 = I2 产品代码保持主线版 |
| 冲突解决 | 唯一冲突 `doc/tasks/M2-I1.md` | 取 Codex 主线版（该文件不在 `0275290..09ad43a` delta 中，等于主线版）；R3 Owner 记录写在 `8dab0ab` 的文档提交 |
| delta 无删除 | `git diff --name-status --diff-filter=D 0275290 09ad43a` | 空 |
| 交付范围 | `git diff --name-only 0275290 09ad43a` | 21 路径，全部落在 Task 授权列表（`src/bootstrap/**`、两份 core 测试、`doc/handoffs/M2-I1-*.md`、`verification/M2-I1/**`） |
| 作者分支自身范围 | `git diff --name-only 6a68fde cb45902 -- src tests` | 仅 `src/bootstrap/{app.py,core_assembly.py}` + `tests/core/{test_bootstrap.py,test_core_assembly.py}`，未触碰 I2 独占路径 |
| Handoff head | `git diff --stat 09ad43a 8dab0ab` | 仅 3 个 doc/verification 文件；`git diff 09ad43a 8dab0ab -- src tests` 为空 |

**视角**：Standards `executed`（范围/证据纪律/授权路径）；Spec `executed`（逐条 AC 对照）；Architecture 与 Verification 见下。

## Standards（可选视角）

依据 [AGENTS.md](../../AGENTS.md)、[协作协议](../09_COLLABORATION.md)、Task 授权范围。无硬性违规：作者累积 delta 严格限于授权路径，主线共享文档（`doc/STATUS.md`、`doc/REBASELINE_PLAN.md` 等）零修改，未越权改写他人 Task/I2 产品代码。Fowler baseline 无实质命中（R3 未引入新代码，产品代码与 R2 交付逐字节相同）。

## Spec（可选视角）

I1-AC1～AC8 逐条对照见「验证」。范围外行为（scope creep）为零：delta 无 React/Tauri/IPC/打包/依赖/QML 产物（`NO_REACT_TAURI_IPC_MATCHES`，21 路径无匹配）；未新增或替换 adapter 实现。AC3 的真实人工 GUI 交互由作者如实标注 `NOT_RUN`，未冒充 PASS。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态 |
|---|---|---|---|---|---|---|
| P3-001 | P3（文档，非阻断） | `verification/M2-I1/12-r3-reconcile-verification.log:80` | 结论句 `the delivery delta is EMPTY product-code` 与同日志 `:58-63` 自己列出的 `src/bootstrap/{app.py,core_assembly.py}`、`tests/core/{test_bootstrap.py,test_core_assembly.py}` 矛盾。R3 delta 相对 `0275290` **包含** I1 产品代码；准确语义是"delta 等于已审作者交付、不含任何未审产品改写"。误读会让人以为 I1 产品代码尚未进入该 head | 同文件 `:57-63` 路径清单 vs `:80` 结论 | 集成登记时改为准确表述（"delta = 已审 I1 交付，无新增产品改写"） | open |
| P3-002 | P3（文档，非阻断） | `verification/M2-I1/README.md`（证据索引表） | 索引未登记 R3 证据 `12-r3-reconcile-verification.log` 与 R3 段落，而 Handoff 已引用该文件；索引与 handoff 引用不完整 | `git diff 09ad43a 8dab0ab` 未包含 README；README 表格止于 R2 段 | Codex 集成登记时补齐 R3 行 | open |
| P3-003 | P3（流程，非阻断） | `doc/tasks/M2-I1.md` front matter | 固定交付 `09ad43a` 上该文件取主线版：`status: approved`、`reviewer: Codex`、`reconcile_status: pending`。本轮实际为 R3 新 head 复审且 Reviewer 为 DeepSeek Harness；authors 在 `8dab0ab` 已把 status 改回 `in_review`（方向保守、正确，且该文件在 Owner 授权路径内） | `git show 09ad43a:doc/tasks/M2-I1.md` vs `git diff 09ad43a 8dab0ab -- doc/tasks/M2-I1.md` | 集成登记时统一 `status` / `reviewer` / `reconcile_status` / `integration_commit` | open |
| P3-004 | P3（范围外既有问题，非阻断） | `tests/reading_export/test_viewmodels.py::test_start_export_completes_and_updates_history` | 隔离基线副本（master `0275290`）全仓第 1 次运行出现 1 次失败：`exportFinished` 未触发 + teardown 期 `settleReadingTime` 后台线程写已关闭的连接（`sqlite3.ProgrammingError: Cannot operate on a closed database`）。基线全仓第 2 次、交付树全仓 2 次、两树该文件各 3 次独立运行全部通过 → 既有跨测试竞态 flaky，**与 I1 交付无关**（I1 不触碰该路径） | `baseline-full-suite-0275290.log`（1 failed, 1228 passed）、`baseline-full-suite-run2.log`（1229 passed）、`delivery-repeat-*.log` / `baseline-repeat-*.log`（15 passed ×3/树） | 另开诊断 Task 交 Codex 评估（属于 master 既有残留，不由 I1 承担） | open |

在 I1 交付自身的记录范围内，未发现 P0/P1/P2 问题。

## 验证

环境：Windows；`G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（3.12.3 + PySide6 6.11.2）与 `C:/Python314/python.exe`（3.14.6，无 PySide6）；`PYTHONDONTWRITEBYTECODE=1`；`QT_QPA_PLATFORM` 不设；作者 worktree 干净（`git status` 空），HEAD=`8dab0ab`，其 `src/`+`tests/` 与 `09ad43a` 逐字节相同（见上表）。原始日志见 [verification/M2-I1/review-09ad43a/](../../verification/M2-I1/review-09ad43a/)。

| 场景 | 命令 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| Task 套件（Required） | `pytest -q tests/core/test_bootstrap.py tests/core/test_core_assembly.py tests/ui_shell tests/providers tests/pipeline` | py312+Qt，`09ad43a` 树 | **468 passed, 5 skipped, exit 0**（复跑两次一致） | [task-suite.log](../../verification/M2-I1/review-09ad43a/task-suite.log)、[exit](../../verification/M2-I1/review-09ad43a/task-suite.exit.txt) |
| skip 归因（AC7） | 同上加 `-rs` | 同上 | 5 skip 逐条：docTR×2、numpy×1、torch×2（环境未安装），与 R1/R2/base 同集 | [task-suite-skip-reasons.log](../../verification/M2-I1/review-09ad43a/task-suite-skip-reasons.log) |
| 架构守卫（Required） | `pytest -q tests/core/test_architecture.py` | py312+Qt | **16 passed, exit 0** | [architecture.log](../../verification/M2-I1/review-09ad43a/architecture.log) |
| 无 Qt 探针（Required，S-01 判别） | `pytest -q -rs tests/core/test_core_assembly.py` | `C:/Python314/python.exe`（无 PySide6） | **7 passed, 1 skipped, exit 0**；唯一 skip=`:239` 函数内 `importorskip("PySide6")`（真实 Qt adapter 注入断言），其余 7 项纯 Core 探针实际执行 | [qtfree-py314.log](../../verification/M2-I1/review-09ad43a/qtfree-py314.log) |
| Core 三层审计（Required，AC2） | `git grep -n -E 'PySide6\|src\.ui\|from ui\|import ui' 0275290 -- src/domain src/ports src/application` 与交付树同模式 | 两树 | 均 **7 行命中且逐行一致**（domain/ports 纯度注释 4 + `pdf_qt.py` docstring/惰性导入 3）→ **零新增**；I2 新增 `src/application/{tasks/projection,editing/region_canvas}.py` 零命中 | [rg-core-three-layers.log](../../verification/M2-I1/review-09ad43a/rg-core-three-layers.log) |
| 空白检查（Required） | `git diff --check 0275290 09ad43a` | 主仓库 | **exit 0** | 本报告「merge 事实核查」 |
| AC4 静态/运行期 | AST 走查 + `git grep` Qt adapter 构造点 | `09ad43a` 树 | `core_assembly.py` 模块级零 PySide6/`ui` 导入，五个 adapter 经 keyword-only 必填参数注入，无 `QtImageDecoder/QtFontCatalog/QtTextLayoutEngine/QtImageCompositor/PixelSourceStyleAnalyzer` 构造；Qt 侧构造在 `bootstrap/app.py:151-160` | [task-suite.log](../../verification/M2-I1/review-09ad43a/task-suite.log)（含 `test_core_assembly.py` 全部断言） |
| AC3/AC5 异常清理（P-01 回归） | `test_assemble_services_closes_connection_when_qt_assembly_fails` 等 | py312+Qt | PASS（`app.py:162-171` `try/except: core.conn.close(); raise` 覆盖 Qt 接线段；成功路径不提前关闭），装配副作用顺序与旧版一致 | [task-suite.log](../../verification/M2-I1/review-09ad43a/task-suite.log) |
| I1×I2 组合全仓回归（额外，判别性对照） | `pytest -q -rs tests` | 交付树 `09ad43a` ×2 与基线 `0275290` 的 `git archive` 隔离副本 ×2；py312+Qt；openssl 在 PATH | 交付：**1238 passed, 5 skipped, exit 0**（两次一致）；基线：run1 **1 failed(flaky), 1228 passed, 5 skipped**、run2 **1229 passed, 5 skipped, exit 0**。差值 **1238−1229=9** 恰为 I1 相对主线新增的测试数（`test_core_assembly.py` 8 + P-01 回归 1）→ 无隐藏行为变化，无跨模块回归 | [full-suite.log](../../verification/M2-I1/review-09ad43a/full-suite.log)、[run2](../../verification/M2-I1/review-09ad43a/delivery-full-suite-run2.log)、[baseline run1](../../verification/M2-I1/review-09ad43a/baseline-full-suite-0275290.log)、[baseline run2](../../verification/M2-I1/review-09ad43a/baseline-full-suite-run2.log) |
| flaky 定位（P3-004） | `pytest -q tests/reading_export/test_viewmodels.py` ×3/树 | 两树 | 基线 15 passed ×3、交付 15 passed ×3 → 上述失败为跨测试竞态 flaky，非 I1 引入 | [baseline-repeat-*.log](../../verification/M2-I1/review-09ad43a/baseline-repeat-1.log)、[delivery-repeat-*.log](../../verification/M2-I1/review-09ad43a/delivery-repeat-1.log) |
| AC8 零 React/Tauri | `git diff --name-only 0275290 09ad43a` 过滤 `package.json\|tsconfig\|src-tauri\|Cargo\|.tsx\|.ts\|tauri\|ipc` | 21 路径 | `NO_REACT_TAURI_IPC_MATCHES` | 本报告「范围与依据」 |
| 真实人工 GUI 交互 | — | — | **NOT_RUN**（无交互会话；作者 Handoff 与本 Reviewer 均如实标注，不冒充 PASS） | Handoff「未跑项」 |
| 全量入口 smoke/screenshot 探针 | 未由本 Reviewer 重跑 | — | **NOT_RUN**（作者本轮亦未声称重跑；产品代码与 R2 逐字节相同，R2 证据仍有效） | — |

## 结论与复审

**决定：`approved`。** 理由：merge 以 `--no-ff` 保留作者历史（四个已审 commit hash 未改写），未做任何产品改写（I1 产品文件与 R2 `approved` 交付逐字节相同，I2 主线产品代码未被覆盖，唯一冲突 `doc/tasks/M2-I1.md` 取主线版且不在 delta 中）；`0275290..09ad43a` 的 21 条路径全部属于已审 I1 作者交付与 Task 授权范围，零删除、零 React/Tauri/IPC；Required 验证（468/5/0、16 passed、无 Qt 7/1/0、rg 零新增、`git diff --check` exit 0）全部独立复现，并额外以两树全仓对照确认增量恰为 I1 新增测试。

无 P0/P1/P2；四条 P3 均为文档/流程/范围外既有问题，不阻断本交付。真实人工 GUI 交互 `NOT_RUN` 已如实记录。

**集成门（不放宽）**：本 Review 仅批准固定 head `09ad43a` 进入集成流程；**未 approved 不得集成**的约束在本轮已满足，但 **approved ≠ integrated ≠ done**。Codex 集成到主线后须以届时主线为基线做集成后验证（全仓 + diff 范围 + 架构守卫），并在 [Task](../../doc/tasks/M2-I1.md) 登记 `integration_commit`、统一 `status/reviewer/reconcile_status`、补齐 `verification/M2-I1/README.md` 的 R3 索引（P3-002/P3-003）；集成后验证完成前不得标 `done`。P3-001 与 P3-004 分别交集成登记与独立诊断 Task 处理，不回退本决定。复审若出现新固定 head，须重新提交非作者 Review，不沿用本结论。
