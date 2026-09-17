---
kind: window-authorization-brief
recipient: ZCode
from: Codex（Lead/Integrator）
window_t0: 2026-09-17（授权提交进入 master 的实际时刻，23:12:28）
window_t1: 2026-09-18 08:50（Asia/Shanghai）
status: active
---

# ZCode 全权窗口指令包（2026-09-17 → 2026-09-18 08:50）

> 权威条款在 [STATUS](../STATUS.md)「**ZCode 全权窗口授权（2026-09-17）【生效中】**」；本文件是**可直接执行的作业指令**。两者冲突时以 STATUS 为准。

## 0. 一句话

从 T0 起，**你是唯一主线写入与集成责任人**；Codex 与 DeepSeek Harness 已暂停主线写入。按下方队列串行推进，每个切片走完"实施 →（子 agent）Review → 修订 → 集成 → Task/STATUS 收口"。

## 1. 时间门（硬）

| 门 | 时刻 | 规则 |
|---|---|---|
| T0 | 23:12:28（已生效） | 开始实施 |
| **W3 启动门** | **04:50** | [TASK-033](TASK-033.md)（W2）**未集成**则**跳过 W3（TASK-020）**，时间并入 W2 收口与 W4 |
| **停止启动新切片** | **08:20** | 之后只做在飞切片的收口 |
| **T1** | **08:50** | 停止实施与集成；在飞切片冻结在当前状态；授权失效 |

## 2. 权限

**自动批准（无需请示）**：窗口名单内 Task 的实施 / 测试 / 取证 / 提交（`agent/zcode/*` 分支）/ 按 §6.6 串行集成 master / 开子 agent 做 Review / 建 own branch-worktree。

**必须登记 `BLOCKED` 并等待用户**：产品需求与范围变更；D08 验收标准或发布 Gate 放宽；**Schema/migration 变更**；**依赖变更（仅 TASK-023 的 `pypdfium2` 一项已获批准，且须按该 Task 的留证要求执行）**；`git push` / 配置远端 / 对外发送内容；解冻**名单之外**的 Task；触碰**他人 worktree/分支/未提交内容**（含 `TASK-020/023/033/034/035/036-deepseek` 与更早的 `agent/*`）。

## 3. Review 定性（本窗口的核心例外）

- 你开的**子 agent** 做 Review：用 [Review 模板](../templates/REVIEW.md)、固定 base_commit 与 reviewed_head、**实际跑测试**并在报告里 passed/skipped 分列、报告入库 `doc/reviews/`。
- 结论**只能** `approved_subagent` 或 `changes_requested`，**不得写 `approved`**。窗口内**不得**宣称"独立 Review 通过"。
- 期满后 Codex + DSH 会**强制补外部 post-hoc 复审**，可能推翻或重开你标记的 `done`——所以**如实登记**比"好看"重要。

## 4. 队列（用户批准的裁剪）

| # | 切片 | 类型 | 关键点 |
|---|---|---|---|
| **W1** | [TASK-037](TASK-037.md) flaky 修复 + TASK-036 R-01 | **保底，先做** | 用它先把窗口流水线跑通。根因已定性（`contentY` 被 `StopAtBounds` 夹回 → 无变化信号 → 节流保存未启动）；修法见 Task AC ①；**须给修复前后各 ≥10 次对照**；**只允许 `tests/reading_export/**` + 文档，不得改生产 `src/`** |
| **W2** | [TASK-033](TASK-033.md) 完整链收口 | **保底，唯一旗舰** | 三 handler 归 `infrastructure/providers/handlers.py` 并经 `bootstrap/app.py` 注入；`color`/`term_extract` 无外部调用 + 能力缺失 **fail-closed**；**`render` 必须同时补生产装配**（`RenderService` 目前只在测试里被构造），复用既有 `infrastructure/rendering/**` 适配器；**「单一写者」P0 约束**（`translated` 指针不得双写，须测试证据）；**AC-RFULL-001 只更新为 BLOCKED（装配面已打通、真实能力仍缺），严禁记 PASS** |
| **W3** | [TASK-020](TASK-020.md) Webtoon 分块处理与阅读 | **条件**（04:50 门） | 白名单已按实际结构收紧（草案里的 `src/infrastructure/imaging/webtoon/**`、`ViewerCanvas.qml`、`tests/webtoon/**` 都不存在）；用 `tests/reading_export/**` 放用例；坐标往返/Tile 边界/滚动恢复等 AC 见 Task |
| **W4** | 文档状态同步 + 窗口报告 | **兜底，必做** | 更新 `doc/00_INDEX.md`、`doc/12_ROADMAP.md` 的「当前状态」段（自 TASK-032 起未更新）+ 产出窗口报告（见 §7） |
| 插队 | [TASK-023](TASK-023.md) PDF/MOBI 导入 | 按该 Task「插队规则」 | 用户已批准新增 `pypdfium2`；注意它会**改变共享 venv** → 仅此一项、安装前后各跑全仓、更新 readiness 断言 |
| — | **不做** | — | TASK-021 / 022 / 025 / 026 / 027（链式依赖与发布 Gate，保持冻结） |

## 5. 证据纪律（会被复查，别省）

1. 每条命令记 **退出码 + passed/skipped 分列**；失败一律加 `-rf` **记录用例名**（本环境全仓串跑非 100% 稳定，见 STATUS flaky 节）。
2. 回归声明须 **全仓 ≥5 次逐次记录**；命中 flaky **如实登记**，不得记通过、不得归因本切片。
3. **不得**把 `BLOCKED`/`NOT_RUN`（真实端点/模型类）改记为通过；不得放宽/删除断言；**不得新增 `skip`/`xfail`**。
4. 每收口一个切片立刻更新：STATUS 台账行 + Task 文件（AC 勾选与集成记录）+ 证据路径，**保证 master 随时可交接**。
5. 判别力：新测试要对**修前代码**失败（把新测试放到 base 导出树上跑一次，记入证据）。

## 6. 环境与命令

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$py = "G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe"
& $py -m pytest -q -p no:cacheprovider -rs -rf          # 全仓
```

- 当前基线：master `e96b3eb`，全仓 **737 passed / 6 skipped**（6 条 skip 均为既有 `tests/network` 的 `openssl unavailable`）。
- worktree 已由 Codex 建好（见各 Task 顶部元数据），**不要**在 `G:/CODEX/New Manga` 主工作区直接改文件。

## 7. 收尾（T1 前必须留下）

在 `verification/ZCODE-WINDOW-2026-09-17/` 或 `doc/handoffs/` 产出**窗口报告**，至少包含：

1. 每个队列项的最终状态（`done` / `in_review` / `frozen`）+ 对应 `integration_commit` / Review 报告路径；
2. **未完成项与冻结原因**（含在飞切片的当前状态与下一步）；
3. 全部集成的 `approved_subagent` 清单（供 Codex/DSH 排 post-hoc 复审）；
4. 本轮**环境变化**（如曾安装 `pypdfium2`）与基线变化（全仓 passed/skipped 前后对照）；
5. 遗留风险与建议。

**T1（08:50）后不得再实施或集成**；未完成切片冻结在当前状态即可，Codex 会在 08:50 接手做失效登记与临时条款移除。
