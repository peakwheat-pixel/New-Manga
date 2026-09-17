---
task_id: TASK-039
author: ZCode（窗口第二轮 W6 Owner；Reviewer=ZCode 子 agent）
recipient: Codex（T1 后 post-hoc 复审）
base_commit: 047164e（分支起点 202dd21 = round2 指令提交；开工提交 6533c39 快进至 W5 收口后 HEAD）
delivery_head: 38fbde4
status: delivered（待窗口内子 agent Review；结论仅 approved_subagent/changes_requested）
---

# Handoff：TASK-039（修复 planner `_clean_available` 继承缺陷）

## 交付结果

**实现 head `38fbde4`**（分支 `agent/zcode/TASK-039-clean-availability`）。3 文件，+303/−4：`src/application/tasks/service.py`（修复本体）、`tests/pipeline/test_clean_availability.py`（新建 8 例）、`verification/TASK-039/discriminability-pre-fix.log`（判别力取证）。

## AC ① 根因（证据行级）

`src/application/tasks/service.py` 原 `_clean_available`（修前 `:459-470`）：

```python
return stages.get("clean", StageState.NOT_STARTED).is_valid or previous.get("inpaint") is PlanDecision.RUN
```

- 判据一 `stages["clean"]`：**没有任何步骤写入名为 `clean` 的 stage**——`inpaint` handler 的 `next_stage_states` 是 `{"inpaint": COMPLETED}`（`src/infrastructure/providers/handlers.py::handle_inpaint`），Clean **artifact 指针**由 handler 内 CAS 提交（`_commit_artifacts` → `adopt_current`，不走 `revision_updates` 也不写 stage）。因此对真实数据该判据**恒为 false**。
- 判据二 `previous["inpaint"] is RUN` 只覆盖**同 run 内**先跑 inpaint 的场景。
- 后果：`RERENDER_REGION/SINGLE` 等 render-only 命令**跨 run** 恒 `BLOCKED(missing_clean_artifact)`，即使当前 Clean revision 真实存在。
- 隐蔽原因：既有单测夹具**手写了 `clean` stage**（`tests/pipeline/test_pipeline.py::catalog_with_pages` 的 r1），测试环境判据被人为满足。

## AC ② 修复

`PipelineService.__init__` 新增**可选** `clean_probe: Callable[[str], bool] | None = None`（page_id → 当前 Clean artifact 是否存在）；`_clean_available(page_id, stages, previous)` 保留两个历史判据（同 run inpaint RUN；有效 `clean` stage——未来若有写入者仍被尊重）并**叠加** probe。语义保证：`probe=None`（所有既有构造）→ 判定逐字节等于修前；probe 只能把"本会 BLOCKED"翻成 RUN（当且仅当 artifact 真实存在），**从不**阻塞旧判据允许的东西（守卫未放宽）。实际命令枚举与覆盖：`RERENDER_REGION`（region scope，矩阵含）、`RERENDER_SINGLE`（page scope，矩阵含）、`RERENDER_ALL/SELECTED`（同族展开，page 命令语义与 SINGLE 相同判据路径）。

**生产注入点在白名单外（如实登记）**：probe 的生产装配（bootstrap 处 `pipeline.clean_probe = lambda page_id: ArtifactStepWriter(conn, storage).artifact_for(page_id, "clean") is not None`）需改 `src/bootstrap/app.py`——本 Task 白名单不含 bootstrap，**移交后续装配切片**（与 TASK-020 `tile_factory`、TASK-023 `ImportDocumentsUseCase` 同一先例口径）。未注入前生产 render-only 命令保持既有 BLOCKED 行为（不比修前差）。

## AC ③ 对照矩阵（tests/pipeline/test_clean_availability.py，region r4=有 OCR、**无** clean stage 的真实形态）

| 命令（scope） | probe=missing | probe=present | 判定 |
|---|---|---|---|
| `retranslate_region`（region） | translate run + render **BLOCKED(missing_clean_artifact)** | translate run + render **run** | render 单元按真实 artifact 翻转——修复意图内 |
| `reinpaint_region`（region） | segment/mask_refine/inpaint 全 run | **逐项不变** | 无 render 单元，结构性不受影响 |
| `rerender_region`（region） | render BLOCKED | render run | AC ② 主目标 |
| `rerender_single`（page） | render BLOCKED | render run | 同上（page scope 分支） |
| `retranslate_region_full`（region，同 run 含 inpaint） | render **run**（同 run inpaint RUN 分支先短路） | render run | 继承分支保持首位 |
| `REOCR_*` | 结构性无 render 单元 | 同左 | 不适用 |

## AC ④ 判别力 + 回归

- **判别力**（[discriminability-pre-fix.log](../../verification/TASK-039/discriminability-pre-fix.log)）：新测试放修前 src（stash `service.py` 至 base `047164e`）→ **exit 1、7 failed / 1 passed**——唯一通过项是"probe=missing 时 BLOCKED 保持"守卫测试（该行为修前即正确，属预期）。
- **回归**：`tests/pipeline`+`tests/core` 81 passed（probe=None 下全部既有 planner 测试逐字节保持）；全仓 ×5 见下表；`tests/providers` 未触碰（TASK-038 契约在 W5 集成口径内）。

## 验证证据（同一 shell + 同一 venv）

**口径**：与 W5 完全相同——`powershell.exe -NoProfile -Command`（Git Bash 会话启动，PATH 继承含 openssl）+ `TASK-012-py312` venv；全仓 N passed / 0 skipped 口径。

| 场景 | 命令 | commit | 结果 |
|---|---|---|---|
| 本切片 | `pytest tests/pipeline/test_clean_availability.py -q -p no:cacheprovider -rf` | `38fbde4` | **8 passed / 0 skipped**、exit 0 |
| pipeline+core 回归 | `pytest tests/pipeline tests/core -q -p no:cacheprovider -rf` | `38fbde4` | **81 passed / 0 skipped**、exit 0 |
| 全仓 ×5 | `-q -rs -rf` 逐次 | `38fbde4` | **每次 780 passed / 0 skipped、exit 0**（[full-suite-runs.log](../../verification/TASK-039/full-suite-runs.log)） |

## AC ⑤ 与遗留

- Review 待窗口内子 agent；集成后在 STATUS/TASK-033 Handoff 登记"R-001 已由 TASK-039 关闭"。
- **遗留**：生产 probe 注入点（bootstrap，白名单外）——移交后续装配切片，与 TASK-020/023 同口径。
- 未 push；未改路由判定算法/SFX 门控/Schema/依赖/seam 本体/AGENTS/其他 Task；无新增 skip/xfail；无既有断言改动。
