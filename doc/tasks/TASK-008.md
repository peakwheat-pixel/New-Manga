---
id: TASK-008
title: 实现 Region 编辑、Revision 与人工保护
kind: implementation
status: done
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-007]
base_commit: f129ae96900fb567288f91a78d55c0ff4ecafe6d
branch: agent/zcode/TASK-008-region-editing
worktree: G:/CODEX/New Manga.worktrees/TASK-008-zcode
integration_commit: 06ba2e7322e5f565feda1808094e9edd282b3c0b
---

# TASK-008：实现 Region 编辑、Revision 与人工保护

本 Task 已完成并集成。Owner=ZCode，Reviewer=DeepSeek Harness；当前阶段见 [STATUS](../STATUS.md)，共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §6～11/15；D06 §29/87～90；D08 AC-REGION/TRANS/REV/AUTO。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-REGION-001、AC-REGION-002、AC-REGION-003、AC-REGION-004、AC-OCR-002、AC-TRANS-001、AC-TRANS-002、AC-REV-003、AC-REV-004。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 实现统一Region几何、类型、阅读顺序及新建/删除/合并/拆分，按原图坐标保存并重启恢复。（统一 Region 模型 BBox+Polygon；六类型；合并=覆盖 BBox+拼接+最强保护继承、拆分=调用方几何+保护继承、源软删；模拟重启恢复测试通过）
- [x] 保存/确认四级文本与样式时产生正确Revision，人工编辑自动translation_locked；明确保存或获批autosave在切换前flush。（四级文本+edited_confirmed 确认语义（D03 §8.3）；人工保存自动置 manual_edited+translation_locked；EditingSession dirty 跟踪与 flush/discard）
- [x] 通过已冻结的原子写入契约检查输入Revision与Lock；恢复历史保留可追踪记录并按契约处理Pin/失效。（Optimistic Write Guard 重读 current 与锁（D06 §90），冲突返回 INPUT_REVISION_CHANGED/LOCK_CHANGED 且 current 不动（Candidate 落库属 TASK-011）；恢复=新 Revision+溯源（AC-REV-004）；Pin 标志（AC-REV-003，清理执行属 TASK-021））
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。（Handoff、DeepSeek approved Review 与 Codex 集成验证均已归档）

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
- Review：[TASK-008-1f373ac](../reviews/TASK-008-1f373ac.md)（report_commit=`f9e59770e7617744178b0f56fc10af558a416298`，reviewed_head=`1f373ac2240fb5fc6304e447b7d0fd873310aef1`，decision=`approved`）。
- 实际执行/实验/测试：[verification/TASK-008/author-verification.md](../../verification/TASK-008/author-verification.md)；Codex 集成验证见 [integration-06ba2e7.md](../../verification/TASK-008/integration-06ba2e7.md)。
- 最近状态：2026-09-15 Codex 已按协作协议 §6 串行集成实现与 approved Review，`integration_commit=06ba2e7322e5f565feda1808094e9edd282b3c0b`，TASK-008=`done`。
- 派单记录：2026-09-15 基线=`f129ae9`，Owner=ZCode，Reviewer=DeepSeek Harness；SQLite Region/Revision 持久化与 StepResultCandidate 落库仍属后续授权范围。

## Codex 集成验证与 Finding 处置

- 固定范围：`base_commit=f129ae96900fb567288f91a78d55c0ff4ecafe6d`、`reviewed_head=1f373ac2240fb5fc6304e447b7d0fd873310aef1`、`integration_commit=06ba2e7322e5f565feda1808094e9edd282b3c0b`。
- Codex 先以 `--no-ff` 合并 ZCode 分支，产生实现集成提交 `604ca6d`；再以 `--no-ff` 合并 DeepSeek Review 分支，产生 `06ba2e7`。两次来源提交均保留。
- Review 报告：[TASK-008-1f373ac.md](../reviews/TASK-008-1f373ac.md)，report_commit=`f9e5977`，与 `reviewed_head=1f373ac` 一致；集成复验见 [integration-06ba2e7.md](../../verification/TASK-008/integration-06ba2e7.md)。
- **R-201 noted / deferred**：合并后 `edited_confirmed` 不自动继承；当前行为不阻塞本切片，后续产品语义裁决时明确确认态继承规则。
- **R-202 noted / deferred**：拆分后的 `reading_order` 可能与既有 Region 重叠；后续编辑器切片考虑归一化，不阻塞本切片。
