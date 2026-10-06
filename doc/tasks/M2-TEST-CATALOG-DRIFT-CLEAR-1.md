---
id: M2-TEST-CATALOG-DRIFT-CLEAR-1
title: test_catalog 断言漂移清算（exact snapshot 反模式修复）
kind: test-debt
status: in_progress
approval: user_2026-10-07_autonomous_mode_continuation
suggested_owner: Codex Executor
owner: Codex Executor
reviewer: Antigravity（非作者，快速独立 Review）
integrator: Codex
depends_on: [M2-SFX-E2E-MATERIAL, M2-TA2C, M2-SFX-ANNOTATE-R2, M2-SFX-ANNOTATE-R3]
base_commit: 8bf57ba2
branch: main（单文件测试修复，直落 main）
worktree: G:/CODEX/New Manga
integration_commit: null
---

# M2-TEST-CATALOG-DRIFT-CLEAR-1

## 来源与目标

`tests/m2_test_assets/test_catalog.py::test_manifest_has_unique_cases_and_exact_taxonomy` 自 2026-10-01 起长期失败（每轮 Gate 以 BASELINE_FAILURE 单列定性，累计 15+ 轮）。本轮清算：manifest 从 97 涨到 122 是**三次合法授权素材 Task 的 append-only 追加**，测试的 exact-total snapshot 断言过时；同时 49-53 行的 fail-closed NOT_RUN 断言缺少 M2-SFX-E2E-MATERIAL 合法执行留态的例外。

## 漂移事实（已核实）

| 漂移 | commit | 授权 Task | 内容 |
|---|---|---|---|
| 97→100 | `40a8ceec` | M2-SFX-E2E-MATERIAL | 追加 BJ13/14/15（densho810 vol03 SFX-rich 池，commit message 明记 "cases.json 97->100 append-only"） |
| 100→110 | `9b9916af` | SFX-ANNOTATE-R2 | 追加 BJ16-BJ25（chiqui7 密度 top-10 选页） |
| 110→122 | `579af8a5` | SFX-ANNOTATE-R3 | 追加 BJ26-BJ37（44 页候选池选 12） |

三向核对：122 = 100+10+12，`len == len(unique)`=122（无重复），BJ16-37 结构抽查（levels=[regression,full]、READY、stages 齐全）通过。

**BJ13/14/15 pipeline_status 非全 NOT_RUN 的授权出处**：`40a8ceec`（BJ13 sfx=PASS＝SFX translate e2e 真跑；BJ14/15 其余九阶段 PASS＝E2E 留态），与 ta3a 五 case 的字面快照同一性质。

## 范围（冻结）

- 仅改 `tests/m2_test_assets/test_catalog.py`：①删除 exact-total pin（`==97`），改为唯一性不变量 + `>=100` 冻结下界 + 漂移史注释；②NOT_RUN fail-closed 例外集并入 BJ13/14/15 并附真实状态字面快照（与 ta3a 同型）。
- manifest `cases.json` **零改动**（追加-only 原则与既有授权事实不动）。
- 其他测试文件、src、契约零改动。

## 验收 Gate

1. `pytest tests/m2_test_assets -q` 全绿。
2. pytest 全量：**1859+1sk+2 failed**（唯一减少=本失败；ui_shell 两例属 M2-UI-SHELL-ENV 另行核实，不在本 Task）。
3. 非作者 Review 通过（Antigravity）。

## 完成定义

AC 全过 + Review 通过 + STATUS Planned next 更新。
