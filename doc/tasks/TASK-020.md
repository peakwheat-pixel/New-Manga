---
id: TASK-020
title: 实现 Webtoon 分块处理与阅读
kind: implementation
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: ZCode（窗口内子 agent，结论仅 approved_subagent）
depends_on: [TASK-013, TASK-015, TASK-019]
base_commit: e96b3eb880bdfcfca182aa1350d9ff56798556c1
branch: agent/zcode/TASK-020-webtoon-chunked-reading
worktree: G:/CODEX/New Manga.worktrees/TASK-020-zcode
integration_commit: b73820048d6251e8d0da42c67427ab1f7fd7ac49
---

# TASK-020：实现 Webtoon 分块处理与阅读

**READY（2026-09-17 ZCode 全权窗口 W3——条件执行）**：用户批准解冻（依赖 TASK-013/015/019 均已 `done`）。Owner=`ZCode`、Reviewer=窗口内子 agent（结论仅 `approved_subagent`）、`base=e96b3eb`、branch/worktree 见顶部元数据。开工前把 `status` 改为 `in_progress`。

**启动门（窗口规则）**：本 Task **只在 W2（[TASK-033](TASK-033.md)）已于 `04:50` 前完成集成时才启动**；否则跳过本 Task，把时间留给 W2 收口与 W4。若启动，须在 `08:20` 前完成集成，否则冻结回 `proposed` 并在窗口报告中说明。

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §5；D05 §20/40；D06 §17/67～70；D07 §14～17；D08 AC-WEBTOON/CAP。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-WEBTOON-001、AC-WEBTOON-002、AC-WEBTOON-003、AC-WEBTOON-004、AC-WEBTOON-005。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 一张超长图保持一Page，Tile仅为可重建Cache；按模型约束处理并回映到原图坐标。（几何/缓存/回映/去重全交付并有测试；超大页像素解码 BLOCKED——Qt PNG handler ≳300MB rgb32 硬限制，见 Handoff，未记 PASS）
- [x] 长图按宽适配、按需解码、限制预取/内存，阅读位置重启恢复；Region/Mask/Render一致。（Qt 可读范围内实测：视口+有界预取材料化、跨会话恢复；Region 为页面级真值不随 tile 变化，清缓存不动真值有测试）
- [x] 验证Tile边界重叠Region去重与拼接，非目标范围不变，清缓存不会破坏业务真值。（内容带按构造互斥且并集=全页；跨 tile Region 回映去重测试；TASK-037 既有契约测试原样通过=非目标范围不变）
- [x] 交付 Handoff=[doc/handoffs/TASK-020-7833604.md](../handoffs/TASK-020-7833604.md)；Review=[doc/reviews/TASK-020-7833604.md](../reviews/TASK-020-7833604.md)（首轮 `changes_requested` `baffcc4`：R-001 P1 修订收口 `b337f71`、R-004 表述收口、R-002/003/005 deferred、R-006 P3 open 不阻断；复审 `40f20e7`=**approved_subagent**，四轴均 executed）；集成=`b738200`（merge，parents `5832894`+`40f20e7`），集成后复验全仓 **764 passed / 0 skipped**、exit 0。

## 允许修改范围

**已由 Codex 按实际结构收紧（2026-09-17，窗口授权）**：原草案中的 `src/infrastructure/imaging/webtoon/**`、`src/ui/qml/workbench/ViewerCanvas.qml`、`tests/webtoon/**` **当前均不存在**，已替换为下列**实测存在**的路径。"不得扩展到整个 `src/tests`"仍然有效。

- `src/application/reading/**`（存在）
- `src/ui/viewmodels/reader/**`（存在）
- `src/ui/qml/reader/**`（存在）
- `src/ui/qml/workbench/ViewerPanel.qml`（存在；画布相关改动只能用此文件，**不得**改其他 workbench QML）
- `src/infrastructure/imaging/**`（**新建**：Tile / Cache 光栅实现归属处；不得引入越界依赖）
- `tests/reading_export/**`（存在；本 Task 的阅读器/QML 契约用例归此目录）
- `doc/tasks/TASK-020.md`、`doc/handoffs/TASK-020-*.md`、`verification/TASK-020/**`

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/webtoon；坐标往返、Tile边界、单Page数、滚动恢复和两模式阅读。
- 按授权fixture验证约1600x200000px，记录峰值内存/耗时，不将建议预算宣称实测。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-013](TASK-013.md)、[TASK-015](TASK-015.md)、[TASK-019](TASK-019.md)。依赖必须已经集成 done 才可开始。

允许修改既有Viewer/Reader，必须先集成依赖并避免与TASK-013/015并行写同文件。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
- **最近状态（当前，唯一）**：2026-09-18 01:1x 由 ZCode 在窗口内开工（W3，status→`in_progress`；启动门达标：W2 TASK-033 已于 04:50 前集成 `4d0f932`）；分支按窗口规则 `git merge master` 快进至 `5832894`（Task 元数据 base=e96b3eb 之上为窗口授权与 W1/W2 集成提交，写集合与本 Task 不相交）。实施开始：TileGrid 几何 + LRU TileCache + QImageReader 按需 clip 解码 + tile 缓存文件 + ViewModel/QML 接线。
- **最近状态（当前，唯一）**：实现 head=`7833604`（开工 `7a540f6`）：`src/infrastructure/imaging/webtoon_tiles.py` 新建（TileGrid/TileCache/TiledPageRasterizer）+ ViewModel opt-in `tile_factory` 接线 + QML webtoon viewer tiled 分支（旧路径不变，TASK-037 契约测试原样过）+ `test_webtoon_tiles.py` 10 例全过；套件回归 82 passed/0 skipped。**BLOCKED 如实登记**：1600x200000 fixture 像素解码在当前依赖下不可行（Qt PNG handler ≳300MB rgb32 硬限制、clip 无效、19GB 空闲内存排除 OOM），几何层 PASS、表征断言+解锁条件入库；未记 PASS。遗留：bootstrap 生产装配点（白名单外）。首轮 Review `changes_requested`（R-001 P1）已修订收口（`b337f71`），复审 `40f20e7`=**approved_subagent**；集成 `b738200`，集成后复验全仓 764 passed/0 skipped exit 0。**TASK-020 已收口 `done`；期满后须 Codex + DSH 外部 post-hoc 复审（可推翻）。**遗留：bootstrap 注入 `tile_factory`（生产装配点，白名单外）、超大页像素解码 BLOCKED（Qt PNG handler 限制，解锁条件入库）、R-002/003/005 deferred、R-006 P3 open。
