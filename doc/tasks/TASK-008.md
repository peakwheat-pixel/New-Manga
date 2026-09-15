---
id: TASK-008
title: 实现 Region 编辑、Revision 与人工保护
kind: implementation
status: in_review
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-007]
base_commit: f129ae96900fb567288f91a78d55c0ff4ecafe6d
branch: agent/zcode/TASK-008-region-editing
worktree: G:/CODEX/New Manga.worktrees/TASK-008-zcode
integration_commit: null
---

# TASK-008：实现 Region 编辑、Revision 与人工保护

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §6～11/15；D06 §29/87～90；D08 AC-REGION/TRANS/REV/AUTO。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-REGION-001、AC-REGION-002、AC-REGION-003、AC-REGION-004、AC-OCR-002、AC-TRANS-001、AC-TRANS-002、AC-REV-003、AC-REV-004。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 实现统一Region几何、类型、阅读顺序及新建/删除/合并/拆分，按原图坐标保存并重启恢复。（统一 Region 模型 BBox+Polygon；六类型；合并=覆盖 BBox+拼接+最强保护继承、拆分=调用方几何+保护继承、源软删；模拟重启恢复测试通过）
- [x] 保存/确认四级文本与样式时产生正确Revision，人工编辑自动translation_locked；明确保存或获批autosave在切换前flush。（四级文本+edited_confirmed 确认语义（D03 §8.3）；人工保存自动置 manual_edited+translation_locked；EditingSession dirty 跟踪与 flush/discard）
- [x] 通过已冻结的原子写入契约检查输入Revision与Lock；恢复历史保留可追踪记录并按契约处理Pin/失效。（Optimistic Write Guard 重读 current 与锁（D06 §90），冲突返回 INPUT_REVISION_CHANGED/LOCK_CHANGED 且 current 不动（Candidate 落库属 TASK-011）；恢复=新 Revision+溯源（AC-REV-004）；Pin 标志（AC-REV-003，清理执行属 TASK-021））
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。（Handoff 已交付 [TASK-008-1f373ac](../handoffs/TASK-008-1f373ac.md)；待 DeepSeek Review + Codex 集成）

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/domain/regions/**
- src/application/editing/**
- tests/editing/**
- doc/tasks/TASK-008.md
- doc/handoffs/TASK-008-*.md
- verification/TASK-008/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/editing；几何往返、reading_order、合并拆分、人工文本保存后重启。
- 重OCR保留人工final、后台10→人工12覆盖拒绝、空字符串/未确认文本的final解析、Dirty切换。
- 以上已执行（2026-09-15，owner ZCode，head `1f373ac`）：`python -m pytest tests/editing` 退出码 0（17 passed）；`PYTHONPATH=src python -m pytest tests` 退出码 0（79 passed）。几何往返、reading_order、合并拆分、人工文本保存后重启、重OCR保留人工final、后台 stale 覆盖拒绝（10→12）、空字符串/未确认文本的final解析、Dirty 切换 flush 均已覆盖。命令、环境、退出码与证据见 [verification/TASK-008/author-verification.md](../../verification/TASK-008/author-verification.md)。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-007](TASK-007.md)。依赖必须已经集成 done 才可开始。

不自行定义review_state/Pin存储；以TASK-002冻结的约束为准。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：[TASK-008-1f373ac](../handoffs/TASK-008-1f373ac.md)（delivery_head=`1f373ac2240fb5fc6304e447b7d0fd873310aef1`）。
- Review：尚无；等待 DeepSeek Harness 独立 Review，报告将写入 `doc/reviews/TASK-008-*.md`（Owner 不写该路径）。
- 实际执行/实验/测试：[verification/TASK-008/author-verification.md](../../verification/TASK-008/author-verification.md)（命令、退出码、环境、NOT_RUN/N-A 清单）。
- 最近状态：2026-09-15 ZCode 完成实现并交付：domain/regions（统一 Region 模型+RegionRevision 快照+final 确认语义）+ application/editing（RegionEditingService：几何保存/合并拆分/reading_order/受守卫机器写入/恢复/Pin/EditingSession flush）+ 17 项 editing 测试全过、全量 79 passed。开发中一次 tests/library 同名模块改名已自查回退（最终 diff 零触碰）。reviewed_head=`1f373ac`，状态 in_progress → in_review；未合并 master。
- 最近状态：2026-09-15 Codex 派单开始执行（base=`f129ae9`，含 TASK-007 集成收口；分支/worktree 如上，Owner ZCode、Reviewer DeepSeek Harness）。基线核验通过：HEAD=base、工作区干净、common dir 正确。流转补记：派单时本文件仍为 `proposed/pending_user_review`，按派单口径填入并直接置 `in_progress`（同 TASK-006/007 先例）。切片边界声明：允许路径不含 infrastructure/ports——Region 持久化契约消费侧定义于 `src/application/editing/ports.py`，测试以契约 fake 驱动（含模拟重启）；SQLite RegionRepository 落地与 schema 扩展需 Codex 协调 TASK-006 边界后另行授权；StepResultCandidate 落库属 TASK-011，本切片冲突以结果对象表达。
