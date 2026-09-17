---
task_id: TASK-019
reviewer: Codex
author: DeepSeek Harness
base_commit: 36242fb00f9f432ec66cc3c33afc167578d0f341
reviewed_head: 726baf5
metadata_head: 6c981c2
kind: post-hoc addendum（补充审查轴）
decision: findings_open（不改变 3755af9 的既有集成结论）
---

# 附录：TASK-019 的 Standards / Spec 双轴补充审查（post-hoc）

**性质**：本文件是主 Review（[`doc/reviews/TASK-019-726baf5.md`](TASK-019-726baf5.md)）**之后的补充审查**。主 Review 按仓库 `doc/09_COLLABORATION.md §6` + `doc/templates/REVIEW.md` 走了 Spec/Architecture/Verification 三轴，**没有覆盖独立的 Standards 轴**；本附录按 `code-review` 技能的两轴口径补跑，并把结果归档。**它不改变 `integration_commit=3755af9` 的集成事实**，但登记的 S-1 是已合并代码上的真实缺陷。

固定对象：fixed point `c9eb65a`（= 作者实施起点，当时 master）→ `6c981c2`（分支 head）= 8 commits、**56 files、`+10354/−15`**。

## Standards

**依据的 standards sources**：`doc/02_TECHNICAL_ARCHITECTURE_.md`（§架构方向、§16 推荐源码边界）、`doc/09_COLLABORATION.md`（白名单/边界纪律）、`AGENTS.md`；仓库**无** `CODING_STANDARDS.md`/`CONTRIBUTING.md`，故同时适用 Fowler smell baseline（判断项，repo 标准优先）。无 formatter/linter 配置，无可"交给工具"的项。

| ID | 类型 | 位置 | 内容与依据 | 修法 |
|---|---|---|---|---|
| **S-1** | **记录在案标准的违反** | `src/application/translation/inpaint/step.py:23,29` | 反向依赖 `infrastructure.providers.inpaint_router` / `inpaint_routes`。`doc/02_TECHNICAL_ARCHITECTURE_.md` §架构方向："依赖方向必须保持 `QML / UI → Application → Domain / Ports → Infrastructure Adapters`"且"禁止反向依赖"。全仓扫描 `src/application/**`：**本文件是唯一**反向导入 infrastructure 的应用层模块（无既有先例可援引） | 把路由/决策**策略**下沉到 `src/application/translation/inpaint/`（本 Task 允许路径内），infrastructure 只保留适配器实现；或让 handler 经 port 注入决策结果 |
| S-2 | 判断项（同根因） | `src/infrastructure/providers/inpaint_router.py`、`inpaint_routes.py` | D06 §21 的路由**策略**（`RouterFeatures`/`RoutePolicy`/`acceptable_routes()`/route 选择）与**适配器**（simple-fill/edge-bleed 实现）住在同一目录 → `Feature Envy`/`Divergent Change` 读法 | 与 S-1 同修：策略入 application，适配器留 infrastructure |
| S-3 | 判断项（可接受） | `src/infrastructure/providers/handlers.py` | 直接 import 具体错误类 `application.translation.pipeline.executor.StepExecutionError`；方向允许，但适配器耦合到应用层具体类型 | 保持现状（seam 已冻结）；如后续引入 port 级错误类型再收敛 |

**Baseline smell 检查（未发现问题）**：无重复实现（`_utc_now` 仅一处；10 个新基础设施模块除适配器对称外无同形逻辑）；无死错误类（21 个错误码全部有引用）；无 `TODO/FIXME/XXX`；未见为 spec 之外需求添加的抽象（`heavy_gate_capacity` 同时被策略与测试使用）；ports/application 未 import PySide6/sqlite3。

**Standards 轴小结**：1 条记录在案标准的硬性违反（S-1）+ 1 条同根因判断项（S-2）+ 1 条可接受耦合（S-3）。

## Spec

**spec sources**：`doc/tasks/TASK-019.md`（5 条 AC + 释放时登记的输入缺口）、`doc/08_ACCEPTANCE_CRITERIA.md`（AC-OCR/INPAINT/RFULL/FALLBACK/GPU/OPTIONAL/MODEL、§78 AC-EXT-SAKURA-001）、U-6 裁决（Sakura 探测范围）。

| 类别 | 结果 |
|---|---|
| 缺失/部分 | `color`/`term_extract`/`render` handler 未实现 → **AC-RFULL-001 完整链 `BLOCKED`**（不在本 Task 允许路径内，主 Review 已裁定不扩范围）；真实模型质量与成本/时延 `BLOCKED`；AC-EXT-SAKURA-001 真实服务验证 `NOT_RUN`（探测实现 PASS；代码核对确认 U-6 合规：仅健康/就绪，无 VRAM/负载/吞吐字段，SAKURA-002/003 未实现） |
| 未要求却做了（scope creep） | 未发现实质越界。唯一需登记的是**任务文件自身的 AC 覆盖缺口**：标题与实现都含"检测（detection）"，但 TASK-019 的"主责任编号 AC"列表中没有 detection 对应的 D08 条目 → 建议补登记或确认 detection 无独立 AC |
| 看似实现但有误 | 除已登记 F-1（默认 `sfx_policy='skip'` + planner 不看 `region_type` → 真实默认下整链被 `SKIP_POLICY` 跳过，本 Reviewer 已独立坐实）外无新增；AC-TRANS 类契约（missing/duplicate/extra、非字符串 id、429 可重试）在 `src/ports/translation/protocol.py` 与 `tests/providers/test_translation_protocol.py` 中确有覆盖，与 TASK-017 口径一致 |

**Spec 轴小结**：无新增错误实现；缺口为已登记的三项 `BLOCKED`/`NOT_RUN` 加 1 条任务文件 AC 覆盖口径缺口。

## 与主 Review 的关系

- 主 Review 的 Spec/Verification 结论**不受本附录影响**（本附录的 Spec 轴与其一致）。
- **S-1/S-2 是主 Review 未覆盖的轴**，因此属于"事后发现"：`integration_commit=3755af9` 不撤销，修复按尾项切片走"实现 → 非作者 Review → 集成"。
- 两轴**分别报告、不合并、不跨轴排名**。
