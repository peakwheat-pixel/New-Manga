---
id: TASK-046
title: 解码面 rewind 成本收敛（overlap 语义收口，落地 TASK-042 AC ⑩ 的实测结论）
kind: performance
status: in_progress
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-042, TASK-045]
base_commit: fc8f1d95dd465bf021f8d61414778f98a4f46f17
branch: agent/zcode/TASK-046-decode-rewind-cost
worktree: G:/CODEX/New Manga.worktrees/TASK-046-zcode
integration_commit: null
---

# TASK-046：解码面 rewind 成本收敛（overlap 语义收口）

**READY（2026-09-18，用户批准"下一步"后由 Codex 开立并释放）**：Owner=`ZCode`、Reviewer=`DeepSeek Harness`（**非作者**）、base=`fc8f1d9`（释放时 master HEAD）。

> **✅ 开工门已解除（2026-09-18）**：TASK-045 已集成（`e2a8f01`），写集合冲突消除 ⇒ **可置 `in_progress`**（开工先 `git merge master`，现为 `e2a8f01`）。原记录：本 Task 的写集合与 [TASK-045](TASK-045.md) **重叠**（`src/infrastructure/imaging/webtoon_tiles.py`、`tests/core/test_bootstrap.py`、`tests/reading_export/**`）。**TASK-045 必须已集成**（当前 `in_review`、首轮 Review 判 `changes_requested`，R-001 P1 待修）方可把本 Task 置 `in_progress`；开工前先 `git merge master`。此门由 Codex 在 TASK-045 集成时解除（协议 §3.4：并行只用于写集合互不重叠的 Task）。

## 来源与目标

来源＝**TASK-042 Review 的 R-03（AC ⑩）** 在 [TASK-045](TASK-045.md) 中被实测推翻的结论，以及 [TASK-045 复审](../reviews/TASK-045-1171bc5.md) 中对 AC ⑩ 的裁定（"接受文档化 + 更正 TASK-042 措辞"，并**建议另开解码面切片**）。

**实测事实（TASK-045 留证 + Reviewer 复跑，`verification/TASK-045/rewind_cost_probe.py`）**：

- 生产装配传 `overlap=64`（`src/bootstrap/app.py:553`），`TileGrid`/`TiledPageRasterizer` 默认亦为 64；
- `visible_tiles` 升序只保证"不向后跳"；由于每块解码窗起点 = 上一块的 `content_bottom - overlap`（**落在游标之前**），**每个非首块都会 rewind 一次并从 row 0 重扫**⇒ 全页扫掠为 **O(块数²)**：
  - `400×20000`（tile 800）：25 块全页扫掠 = **24 次 rewind**；
  - `1600×8000` Qt 编码：单块 4.406s、同调用两块 **13.281s**（多付 ≈**8.9s** 纯重扫；作者留证 4.53→14.24s，多付 ≈9.7s）；
- 因此 TASK-042 Handoff 的"全页只需一次顺序扫描"**仅在 `overlap=0` 时成立**；
- **TASK-045 F-4 之后，overlap 对输出已无贡献**：落盘瓦片已被裁到 `[content_top, content_bottom)`，overlap 只作为"解码上下文"存在于被丢弃的行里。

**目标（可观察结果）**：把上述二次折叠消掉——**一次全页扫掠的 rewind 次数不再随块数线性增长**，并在同一测量口径下给出前后对照；同时保持像素输出逐字节不变。

## Acceptance Criteria

- [ ] **AC ①（根因与不变量，先证后用）**：写清 overlap 在 F-4 之后**还剩什么职责**（是否被任何解码正确性依赖：PNG 行过滤只依赖"上一重建行"，而流式读取本就是顺序重建），并给出**可复现证明**：把解码窗 overlap 去掉/改变后，瓦片像素与 `overlap=64` **逐字节相同**（对图案页与随机页各一次；断言"瓦片行拼接 == 整页行"仍成立）。若结论是"overlap 仍必需"，必须给出反例与最小必要值，**不得凭码面推导**。
- [ ] **AC ②（成本对照，主 AC）**：同一 shell + 同一 venv，同一页尺寸与同一测量脚本，修复前 vs 修复后**逐次**记录（≥3 次）：
  - `rewind` 次数：全页扫掠的 rewind 数**不再 = 块数 − 1**（目标 ≤1/次调用，单块调用为 0）；
  - 墙钟：`1600×8000` Qt 编码页"单块 → 两块同调用"的**额外**耗时应落在噪声级（对照 ≈8.9–9.7s）；`400×20000` 全页扫掠耗时同步下降；
  - 与 `verification/TASK-045/rewind-cost-probe.txt`、[author-probes-rerun.txt](../verification/TASK-045/review-1171bc5/author-probes-rerun.txt) 的基线数字逐项对照。
- [ ] **AC ③（像素语义不变）**：`tests/reading_export/**` 既有几何/带宽/缓存键/逐行断言**逐条不变**（不得放宽）：瓦片文件高度 == 声明 `content_height`、每块行 == 该页对应行、拼接 == 整页；全屏/视口请求返回的文件集合语义不变。
- [ ] **AC ④（缓存语义显式声明）**：缓存键含 `overlap`（`webtoon_tiles.py:335`）⇒ 改 overlap 会使既有磁盘瓦片**失效重建**。须在 Handoff 声明这一点及其影响（可重建像素缓存、不触业务数据），并确认 `_TILE_CACHE_FORMAT` 是否需要随之升版。
- [ ] **AC ⑤（判别力与对照）**：新增/更新的断言对**修前代码**失败（或给出等价对照矩阵并说明为何不适用）；如实标注哪些用例只是"钉住既有行为"、不计入判别力。
- [ ] **AC ⑥（不回归）**：`tests/reading_export`、`tests/core` 与全仓 **passed 不减少**；全仓 ≥5 次逐次记录（同一 shell + 同一 venv、退出码 + passed/skipped 分列 + skip 原因）；**不得新增 `skip`/`xfail`、不得放宽/删除既有断言**。
- [ ] **AC ⑦（可观测性收口）**：`webtoon_tiles.py` 的 `ensure_viewport`/`_decode` 与 `TASK-042` Handoff 里"一次顺序扫描"的措辞必须与最终实现**一致**（代码/注释/断言三者一致）；`doc/STATUS.md` 由 Codex 在集成时登记 AC ⑩ 的最终口径。

## 允许修改范围

- `src/bootstrap/app.py`（装配处的 overlap 取值）
- `src/infrastructure/imaging/**`（解码窗与 rewind 语义；`TileGrid`/`TiledPageRasterizer`/`StreamingPngReader`）
- `tests/reading_export/**`、`tests/core/**`
- `doc/tasks/TASK-046.md`、`doc/handoffs/TASK-046-*.md`、`verification/TASK-046/**`
- `doc/STATUS.md`（仅登记状态/关闭关系）

## 禁止范围

- 不得改 Schema/migration、依赖清单、pipeline seam 本体、`AGENTS.md`、其他 Task；**不得改 `src/ui/**`**（若确证必须改 QML，先停下交 Codex 登记范围变更）。
- 不得改变页面像素语义、页序、Managed Copy 纪律；不得把"重扫"换成"整页解码"（那会退回 TASK-020 的 BLOCKED 面）。
- 不得放宽/删除既有断言，不得新增 `skip`/`xfail`；不得与 TASK-045 并发改同一文件；不 push。

## 测试要求

| 场景/AC | 计划命令或手工步骤 | 前提/环境 | 实际结果 | 证据 |
|---|---|---|---|---|
| AC ① 像素等价 | planned：图案页 + 随机页，overlap 变更前后瓦片逐字节比对 | python 3.12 + `TASK-012-py312` venv | NOT_RUN | 无 |
| AC ② rewind 成本 | planned：`python verification/TASK-046/rewind_cost_probe.py`（基线脚本可从 TASK-045 复制） | 同上，同页尺寸 | NOT_RUN | 无 |
| AC ③ 像素语义 | planned：`pytest tests/reading_export -q -rs -rf` | 同上 | NOT_RUN | 无 |
| AC ⑥ 全仓回归 | planned：`pytest -q -rs`（≥5 次） | 同上 | NOT_RUN | 无 |
| AC ⑤ 判别力 | planned：新断言 + 修前 `src`/装配（对照矩阵） | 同上 | NOT_RUN | 无 |

## 依赖、风险与阻塞

- **硬依赖**：TASK-042（流式带状读取，已集成 `ce7b4f9`）、TASK-045（F-4 裁剪使 overlap 对输出失去贡献；**已集成 `e2a8f01`** ⇒ 开工门已解除）。
- **写集合冲突**：与 TASK-045 在 `webtoon_tiles.py` / `tests/core/test_bootstrap.py` / `tests/reading_export/**` 重叠 ⇒ **已随 TASK-045 集成（`e2a8f01`）解除**。
- **契约风险**：`TileGrid(overlap=...)` 是公开构造参数，`TiledPageRasterizer` 默认值亦为 64；改默认值会影响所有构造点（含测试）——需在 AC ④ 中说明影响面。
- **性能风险**：`overlap=0` 若被证明对解码正确性无影响，则"复用上一窗尾部"是等价更强的方案；若二者有差异，以实测为准并记录取舍。
- **未验证面**：真实超大商业 webtoon 页（授权素材）不可得，测量仍以合成/Qt 编码页为准。

## 交付与运行记录

- Handoff：尚无。Review：尚无（待 `DeepSeek Harness` 按 §6 执行**非作者** Review）。实际测试：尚无（`ready`；开工门已解除，可开工）。
- **最近状态（当前，唯一）**：2026-09-19 ZCode 开工（`git merge master` 至 `ec5b4d1` 后置 `in_progress`）。`base=fc8f1d9`。实施进行中。
