# DIAG-READING-EXPORT-001 集成核验记录（Integrator=Codex 代行）

- 日期：2026-09-28（Asia/Shanghai）
- Owner：DeepSeek Harness；非作者 Reviewer：Codex（本会话代行）；Integrator：Codex（本会话代行）
- 固定 base：`83de13dfe0521125715c2e26da75b96a63103938`（main）
- Owner 交付 head：`8b36e98e8ce11bb54be5d6dfe8921cf64390aa4e`；Owner 分支 tip（含 Handoff）：`77c661b0e32c8f6f5a9a2e4006a267624f622e2e`
- 非作者 Review：[doc/reviews/DIAG-READING-EXPORT-001-77c661b0.md](../../../doc/reviews/DIAG-READING-EXPORT-001-77c661b0.md) `decision=approved`（review commit `c90b8b27`）
- **Integration merge：`e0a0e784498fc339a4d666dd931cc67cfb65bbdb`**（parents `c90b8b27` + `77c661b0`；Owner 提交历史未改写，Owner 分支/worktree 保留）

## 集成方式

1. 集成 worktree `G:/CODEX/New Manga.worktrees/DIAG-READING-EXPORT-001-integration`，分支 `codex/DIAG-READING-EXPORT-001-integration`，起点 main=`72215b8f`。
2. 提交 Review（`c90b8b27`）→ `git merge --no-ff 77c661b0`。唯一冲突 `doc/tasks/DIAG-READING-EXPORT-001.md`（主线释放版 vs Owner claim/交付版），按用户指示以 **Owner 已交付版为底**（`git checkout --theirs`），随后由 Integrator 写入 `done` 与 `integration_commit`。
3. 治理提交（本记录所在提交）：Task 置 `done` + AC 勾选 + 集成记录；报告 §4.1 R-001 措辞修正；STATUS/REBASELINE_PLAN/ROADMAP/00_INDEX/tasks README 同步；FIX-A/FIX-B 登记（`proposed`）。

## 集成核验（对象级；按 Integrator 指示不重跑诊断矩阵）

| # | 检查 | 命令/方式 | 结果 |
|---|---|---|---|
| N1 | 范围 | `git diff --name-status 83de13df..77c661b0` → 24 路径，全部在 Task 允许清单（doc/tasks、doc/research、doc/handoffs、verification/DIAG-READING-EXPORT-001/**）；禁改路径（`src/**`、`tests/**`、`packaging/**`、`src-tauri/**`、`requirements*`、`pyproject`、`doc/contracts/**`）grep 零命中；无 D/R（未删除或改写既有证据） | PASS |
| N2 | 卫生 | `git diff --check 83de13df..77c661b0` | exit 0，PASS |
| N3 | 历史 | `git merge-base 83de13df 77c661b0` = `83de13df`（Owner 分支直接生长于固定 base）；claim `064ff980` 仅改 Task 文件且相对释放版 `ceab572b` 仅 `status: ready→in_progress` 一行；治理释放 commit `ceab572b` 未混入 Owner 分支 | PASS |
| N4 | 证据交叉核对 | matrix.tsv 15 条 ↔ run-01..15.log 逐条（命令/次数/环境头/结果/EXIT/UTC 时间戳）；run-01 的 11 个 skip 逐条披露于 `run-01.log:389-399`（6 OpenSSL、2 docTR、1 numpy、2 torch），未计为通过；结论全文维持 `NOT_REPRODUCED` | PASS |
| N5 | 源码核对 | 报告引用行号（export `viewmodel.py:291/344/379-394`、tests `:33-48/163/274-275`、reader `viewmodel.py:42/69-72/104-105/110-112/441-451`、`test_bootstrap.py:604-611`、`closeReader` 唯一调用 `test_viewmodels.py:163`）逐一与 `git show 83de13df:…` 相符；`git diff 0275290 83de13df -- src/ui/viewmodels/export/viewmodel.py` 为空（`_finish` 顺序逐字节相同，非发布顺序回归） | PASS |
| N6 | 探针合规 | 两脚本全文通读：无产品/测试文件编辑、无 monkeypatch（探针 1 仅探针内子类打时间戳；探针 2 仅公开 API + `sys.excepthook` 进程内捕获）、tempfile 写入、无新依赖；探针日志与报告引用数据一致（隔离 0/400、忙碌 26/200、26/26 一次泵到达；`ProgrammingError` 栈帧逐帧相同、失败后心跳仍 active）。探针恰 2 个，未超上限 | PASS |
| N7 | 合并后状态 | merge 后 `doc/tasks/DIAG-READING-EXPORT-001.md` 以 Owner 版为底 + Integrator 治理增量（done/AC/集成记录）；报告 §4.1 措辞修正（R-001）落地 | DONE |
| N8 | 结论口径 | Task、报告、STATUS、Roadmap 均维持 `NOT_REPRODUCED`；未出现"已修复/已解决"表述 | PASS |

## Findings 处置（来自 Review）

- R-001（P2，报告 §4.1 "全仓……正是放大条件" 与 §5 U3 未决矛盾）：**fixed at integration**——该句已改为"候选放大条件"并显式引用 U3；不改写 Owner git 历史，修正发生在集成层并在此登记。
- R-002（P3，探针 1 r1/r2 中间日志被同文件名重跑覆盖）：**accepted**——报告 §0 已如实披露修订史；矩阵 15 次证据完整。
- U1（哪个用例留下活心跳）/ U2（store 类型归属）：维持**未决**，归属 FIX-B 验证范围；收口探针超出本 Task ≤2 上限，未授权。
- U3（症状 A 真实触发条件）：维持**未决**；FIX-A 的验证 Gate 应含忙碌主线程判别探针。
- U4（两症状独立）：采信，作为 FIX-A/FIX-B 独立立案依据。

## 后续

- 修复实现不在本 Task 范围：[DIAG-READING-EXPORT-001-FIX-A](../../../doc/tasks/DIAG-READING-EXPORT-001-FIX-A.md)、[DIAG-READING-EXPORT-001-FIX-B](../../../doc/tasks/DIAG-READING-EXPORT-001-FIX-B.md) 均 `proposed / NOT_RELEASED`。
- 诊断结论在修复落地前不构成任何"已解决"声明；11 个环境 skip 对全仓"全绿"口径的折扣继续有效。
