---
id: TASK-007
title: 实现书架领域与本地图片导入
kind: implementation
status: in_review
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-006]
base_commit: 6b123fe55f2e6373335b044fc5e5f169b5d108e0
branch: agent/zcode/TASK-007-library-import
worktree: G:/CODEX/New Manga.worktrees/TASK-007-zcode
integration_commit: null
---

# TASK-007：实现书架领域与本地图片导入

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D03 §3～5/30；D04 §4～10；D07 §37～39；D08 AC-LIB/CH/IMPORT/PAGE。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-LIB-001、AC-LIB-002、AC-LIB-003、AC-CH-001、AC-CH-002、AC-CH-003、AC-CH-004、AC-IMPORT-001、AC-IMPORT-002、AC-IMPORT-003、AC-IMPORT-004、AC-IMPORT-005、AC-PAGE-001。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 支持 Book/Chapter CRUD、paged/webtoon、阅读方向、标签/收藏/归档分离、章节/页序与原始导入顺序。（领域不变量：webtoon=vertical、paged=rtl/ltr；收藏/归档为系统标志与 Tag 隔离；chapter_number 承载 10.5/番外；source_order 冻结与 sort_order 重排分离；无 Volume）
- [x] 图片/文件夹导入执行 Managed Copy、decode验证、hash去重与排序；取消/损坏/复制失败不留可处理坏Page。（逐文件 hash→decode→Managed Copy→提交的顺序保证；copy 失败/取消/截断 PNG（真实 QImage 解码）均零坏 Page；skip 与 import_as_new 去重策略；文件夹自然排序）
- [x] 应用用例通过已批准Repository契约工作；不写QML、不新增Volume。（契约消费侧定义于 `src/application/library/ports.py` 与 importing `ports.py`（允许路径不含 src/ports，SQLite 落地待 Codex 协调 TASK-006 边界）；用例零 QML/零 PySide6/sqlite3 导入）
- [ ] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。（Handoff 已交付 [TASK-007-6ea4dd9](../handoffs/TASK-007-6ea4dd9.md)；待 DeepSeek Review + Codex 集成）

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/domain/books/**
- src/domain/pages/**
- src/application/library/**
- src/application/importing/images/**
- tests/library/**
- doc/tasks/TASK-007.md
- doc/handoffs/TASK-007-*.md
- verification/TASK-007/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/library；CRUD重启持久化、Tag删除不删Book、混合章节、重复/损坏/透明图。
- 中文/日文/韩文/emoji路径与源文件前后Hash一致；导入中断可恢复。
- 以上已执行（2026-09-15，owner ZCode，head `6ea4dd9`）：`python -m pytest tests/library -v` 退出码 0（25 passed）；`PYTHONPATH=src python -m pytest tests` 退出码 0（62 passed，含 TASK-005 守卫与 TASK-006 storage）。CRUD 模拟重启持久化、Tag 删除不删 Book、混合章节、重复/损坏/透明图、中日韩/emoji/空格/括号路径与源文件 Hash 前后一致、导入取消/中断保护均已覆盖。命令、环境、退出码与证据见 [verification/TASK-007/author-verification.md](../../verification/TASK-007/author-verification.md)。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-006](TASK-006.md)。依赖必须已经集成 done 才可开始。

PDF/MOBI/网页导入属于 TASK-023；Schema新增需Codex协调 TASK-006边界。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：[TASK-007-6ea4dd9](../handoffs/TASK-007-6ea4dd9.md)（delivery_head=`6ea4dd9241c0a24f60964b570cb768bb48dfa0f3`）。
- Review：尚无；等待 DeepSeek Harness 独立 Review，报告将写入 `doc/reviews/TASK-007-*.md`（Owner 不写该路径）。
- 实际执行/实验/测试：[verification/TASK-007/author-verification.md](../../verification/TASK-007/author-verification.md)（命令、退出码、环境、NOT_RUN/N-A 清单）。
- 最近状态：2026-09-15 ZCode 完成实现并交付：domain（Book/Chapter/Tag/Page 实体与不变量）+ application（LibraryService CRUD/标签/收藏归档；ImportImagesUseCase 去重→decode→Managed Copy→提交与取消保护）+ 25 项 library 测试全过、全量 62 passed。Repository 契约消费侧定义（见切片边界声明），SQLite 落地待协调。reviewed_head=`6ea4dd9`，状态 in_progress → in_review；未合并 master。
- 最近状态：2026-09-15 Codex 派单开始执行（base=`6b123fe`，分支/worktree 如上，Owner ZCode、Reviewer DeepSeek Harness）。基线核验通过：HEAD=`6b123fe`（=派单 base，含 TASK-006 集成与收口），工作区干净，common dir 正确。流转补记：派单时本文件仍为 `proposed/pending_user_review`，按派单口径填入 owner/approval/base/branch/worktree 并直接置 `in_progress`（与 TASK-006 派单先例一致，ready 未单独落盘）。切片边界声明：本 Task 允许路径不含 infrastructure/ports，因此 Repository 契约在 `src/application/library/ports.py`（消费侧 Protocol）定义，持久化由契约实现注入；SQLite BookRepository 落地与 schema 扩展需 Codex 协调 TASK-006 边界后另行授权（本 Task 测试以契约 fake 验证用例行为，含模拟重启重载）。
