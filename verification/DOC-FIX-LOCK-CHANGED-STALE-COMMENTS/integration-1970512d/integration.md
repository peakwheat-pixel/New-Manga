# Integration record — DOC-FIX-LOCK-CHANGED-STALE-COMMENTS

- integrated: `done` @ merge `1970512d`（parents `4ed3c044` + `8ab9045b`，--no-ff 无冲突，16 文件全允许路径）+ 集成修正 commit（本记录所在提交）
- integration date: 2026-09-30 (Asia/Shanghai)
- integrator: 代行 Codex（ZCode，用户全权授权）；Owner=ZCode（交付链）；Reviewer=DeepSeek Harness（非作者，r1+r2）
- reviewed_head: **`8b00d199`**（r1 报告归档 commit；DSH r2 独立读取 refs 发现派发口径「928b881d」实为其直接父之后的新提交——`git show --stat 8b00d199` 确认仅新增 r1 报告 1 文件 120 行，纯文档导入，见 [integrator-replay.log](../raw/integrator-replay.log)）；Owner 终 tip=`8ab9045b`（r2 报告归档）
- 性质：两处注释/docstring 文本修正，零指令流变化；依赖 [DIAG-M2-LOCK-CHANGED-REPRO-002](../../../doc/tasks/DIAG-M2-LOCK-CHANGED-REPRO-002.md)（`done` @`1faf6c1b`）结论。

## 交付链（Owner branch `agent/zcode/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS`）

`74022cdc`(claim) → `65f0facb`(实现+AC1-AC4 证据) → `1dd30dc7`(Handoff) → `768a0933`(whitespace 规范化=r1 被审 tip) → `928b881d`(r2 返修：P2-1 provenance-note/措辞限定 + P2-2 探针入库/指令流口径 + P3-1/2/3/6) → `8b00d199`(r1 报告归档=reviewed_head) → `8ab9045b`(r2 报告归档=Owner 终 tip)。

## Review 轨迹（Reviewer=DSH 非作者，均纯静态）

- r1：[approved_with_conditions](../../doc/reviews/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-768a0933-dsh-r1.md)（0×P0/P1、2×P2、6×P3、4×P4；原字节 SHA256=`939e77c5…`）
- r2：[approved](../../doc/reviews/DOC-FIX-LOCK-CHANGED-STALE-COMMENTS-8b00d199-dsh-r2.md)（**准予集成**；P2-1/P2-2 均 closed，P3-1/2/3/6 closed，新增 N-1～N-3×P3 + 8×P4 全部非阻塞；原字节 SHA256 记录于归档 commit）

## 集成复算（r2 §四-1，全部达成）

| 项 | 结果 | 证据 |
|---|---|---|
| N-1：`git show --stat 8b00d199` | 仅 r1 报告 1 文件（120 行），纯文档导入 | [integrator-replay.log](../raw/integrator-replay.log) |
| sha256 复算（**LF blob 基准统一**，N-3 闭合） | 改前 `f1b5976d…`/`b2d7b86e…` 与 provenance-note 锚点一致 ✓；改后 blob=`8493bbe5…`/`a5def2b1…`——**Owner note 原记的 `30d55acd…`/`3e4b1fd1…` 为 CRLF 工作区字节（autocrlf checkout），与本 Task worktree 的 LF blob 不同基准**（N-3 实锤，更正见集成修正 commit 与 note 内追加段） | 同上 |
| 字节码探针 tip 级重跑（临时 worktree @`8ab9045b`） | 52 objects ALL-EQUAL（37+15）、`instruction stream unchanged`、EXIT=0 | 同上 |

## 集成记录登记（DSH r2 §四-5 一次性收口）

1. **L-7 ④（r1 P3-4）**：`experiments/M2-TA3-A/run_smoke.py:303` 注释「# Known planner gap: region-less backfill chain (M2-AC1 handoff).」为同类第三处过时表述（L-7 原登记仅 ①②③）；`:305` 的证据键字面量 `"defect:known-planner-gap-lock-changed"` 是证据键**不得改名**。处置：维持不改、引用 DIAG-002 结论；随未来触碰该文件的 Task 顺手更新注释（不动字面量）。
2. **P3-5**：`run_smoke.py:273` 本 Task 新注释中「page-level chain」措辞沿用自旧注释，M2-TA3-A r1 P2-2 曾判「整页链」易高估 Run1 覆盖面——低危登记，随未来触碰补「region-level steps act on primary region only（Run2 covers the rest）」限定或改中性描述。
3. **行号换算注（r1 P4-1）**：本 Task 两文件各净 +2 行，DIAG-002 Task/Handoff/Review 中引用的 `acceptance_bridge.py:338-340`、`run_smoke.py:489-491`、`:464` 等行号自此整体 +2；历史文档不改写。
4. **N-5 解读注**：`ac4-scope-proof-r2.log:10` 的 `(empty = clean)` 为模板残留措辞，紧跟 4 行 `??` 输出——语义应为「若为空即干净」；当时 4 个 `??` 即本轮返修新增的 4 个证据文件，随后已提交。
5. **P4-2（登记）**：`acceptance_bridge.py:336-337`「fail-closed safety net for the region-less case」理由句的现在时性偏软（M2-P1 后 regionless 链已可完成），未来触碰时清理。
6. **M2-TA3-A provenance 口径（P2-1 落地）**：`verification/M2-TA3-A/raw/00-provenance.txt` 的 sha256 manifest 在 main/tip 上对 run_smoke.py 一行 FAILED 属**本 Task 注释演进的预期结果**（15/15 → 14/15）；字节级 15/15 仅在其交付 worktree 成立；行为等价由本 Task AC1 diff + 52 对象 co_code 全等支撑，dc2b9aca 历史标识不变。M2-TA3-A.md 正文不改写，以本记录为准。

## 集成修正 commit 内容（标注集成方修正）

N-3 更正（provenance-note 追加 blob 基准段）、reviewed_head/delivery_head/提交链终值回填、P3-7「内嵌脚本」句清理、证据链接升级 r2 资产、N-4「指令流（co_code）零变化」口径统一（STATUS:14/Task:25；release 证据与初版 log 历史捕获不改写）、P4-3 DIAG-002 frontmatter 重复键清理、P4-4 tasks/README:7 回填、N-6 探针盲区清单补 `co_freevars`/`co_cellvars`。

## 遗留

- 无阻塞遗留。L-7 ④/⑤、P4-2 均为登记类；真 docTR 相关推断限定不受本 Task 影响。
