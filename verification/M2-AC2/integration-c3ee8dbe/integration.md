# M2-AC2 Integration Record — c3ee8dbe → merge 9d3c1db5

- Integrator: Codex（本会话由 ZCode 代行，用户 2026-09-28 全权授权；Owner=ZCode 为另一会话，Owner≠Integrator 保持）
- Integration merge: `9d3c1db5ffafd9ff2c7cd8aeb4f209c1e5c1df0c`（parents `1320b5fb` + `c3ee8dbebc860f67abd668301dc81ab78d917bac`；no-ff）
- Reviewer: DeepSeek Harness（非作者）r2 = `approved_with_conditions`（[报告](../../doc/reviews/M2-AC2-375cf43b-dsh-r2.md)，C1-C3 Owner 已闭）
- 日期: 2026-09-28（Asia/Shanghai）

## ① 残余 not_verified 三项的 git 核对（DSH r2 §not_verified）

1. **HEAD 核实**：`agent/zcode/M2-AC2-data-integrity` tip = `c3ee8dbe`（`git worktree list` / `git log` 实证）。`8d72f91f`（r1 代码返修）为 commit 对象但已被 amend 取代、不在 tip 祖先链（`git merge-base --is-ancestor` 失败），与 Handoff HEAD ledger（a3e3fb22 → 8d72f91f → 8db6d150 代码/证据层 → workspace tip c3ee8dbe）口径一致。
2. **范围核对**：`git diff --name-status 375cf43b..c3ee8dbe` 仅 4 文件——`doc/handoffs/M2-AC2-owner-delivery.md`、`doc/tasks/M2-AC2.md`、`tests/m2_acceptance/test_data_integrity.py`、`verification/M2-AC2/verification-results.md`，全部落在 Task 允许路径。逐 commit（b76cc4ce 初始 / 375cf43b 返修 / c3ee8dbe C3 关闭）name-status 同样全在允许路径。全 range `61f9db9b..c3ee8dbe` 中的治理文件（00_INDEX/REBASELINE_PLAN/STATUS/tasks README/release evidence）全部来自 main 上的 release commit `01af7732`（Codex 治理侧），非 Owner 交付；Owner delta（`01af7732..c3ee8dbe`）恰为上述 4 允许路径。禁改路径（`src/**`、`apps/**`、`doc/contracts/**`）零命中。
3. **C3 断言存在性**：`tests/m2_acceptance/test_data_integrity.py:343`（`assert decisions`）与 `:536`（`assert planned.tasks[0].units`）在 tip 上实证存在。

## ② 集成方复跑（Owner worktree `G:/CODEX/New Manga.worktrees/M2-AC2-zcode`，tip c3ee8dbe）

| 命令 | 结果 | EXIT |
|---|---|---|
| `pytest tests/m2_acceptance/test_data_integrity.py -v` | **11 passed** | 0 |
| `pytest tests/m2_acceptance -q` | **15 passed**（M2-AC1 4 + 本模块 11） | 0 |
| `git diff --check 61f9db9b..c3ee8dbe` | （无输出） | 0 |

shell=Git Bash (win32)；interpreter=`G:\CODEX\New Manga.task-envs\TASK-012-py312\Scripts\python.exe`（Python 3.12.3, pytest 9.1.1）。

## ③ Review 条件处置核对

- **C1**（verification-results 自洽）：已闭——`:3` delivery head=`8db6d150`、`:7` cmd1 为 `-v` 且 `:15-25` 为 `-v` 逐条格式、cmd3 写真实 hash、补 tip 说明行。核对通过。
- **C2**（Handoff/Task 数字同步）：Task `delivery_head` 已在 main 侧 `1320b5fb` 更新为 `c3ee8dbe` 并附 review 字段；Handoff 交付物行/AC6 行已为 11 场景/11 passed/15 passed。**残留**：Handoff"验证命令"段第 1/2 条仍写 `10 passed / 14 passed`（C1-C3 关闭 commit 未触及该两行）——由集成方在集成 head 修正为实测 11/15 并标注，见 commit `9d3c1db5` 之后的收口 commit。
- **C3**（非空守卫）：已闭（见①.3），复跑 11/15 passed 证实无回归。
- **C4**（P3-1..P3-6 清洁项）：按 Review 裁决登记为后续清洁项，不阻断集成。

## ④ 集成 merge 与集成 head 复跑

- merge 冲突：唯一 `doc/tasks/M2-AC2.md`（main `1320b5fb` 的终态字段 vs Owner `delivered` 版）；按用户裁决惯例取 **Owner 交付版**（保留 AC 勾选与 AC3 双层锁语义澄清），终态字段（done/integration_merge/INTEGRATED）由收口 commit 叠加，避免 merge hash 自指。
- 集成 head `9d3c1db5` 复跑：`pytest tests/m2_acceptance/test_data_integrity.py -q` → **11 passed EXIT=0**；`pytest tests/m2_acceptance -q` → **15 passed EXIT=0**；`git diff --check 61f9db9b..9d3c1db5` → **EXIT=0**。
- 树一致性：`git diff --stat c3ee8dbe 9d3c1db5 -- tests/ src/ apps/` 为空 → 集成树产品路径与 Owner 树逐字节一致。
- Owner branch/worktree 保留于 tip `c3ee8dbe`（未 advance、未改写）。

## ⑤ 遗留登记（不阻断 done）

- C4 P3-1..P3-6（死 import、`test:499` 字面 revision 1、局部重复 import、AC5 场景实现 helper、`chr(92)` 冗余 replace、`core.editing._repo` 私有读面无注释）→ 后续测试清洁项。
- Handoff §实现过程中的语义发现 ②：`core_service._PassthroughImageDecoder` stub decoder 签名缺陷（传 `format=` 而 `DecodedImage` 无该字段）——未来 core_service 扩 ImportPages 命令前必须替换该 stub。
- Qt provider 读面 typed `ProviderInputError` 分支 NOT_RUN（需 Qt/WebView2 E2E）→ 后续 E2E slice 输入。
- M2 Acceptance Backlog 其余行（Provider fail-closed、Reader lineage+Library page-count、Package/clean-start、Real docTR、M2 Release Gate）仍未登记。
