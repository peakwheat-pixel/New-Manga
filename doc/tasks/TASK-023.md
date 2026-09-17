---
id: TASK-023
title: 实现 PDF/MOBI 导入路线
kind: implementation
status: done
approval: approved_by_user
suggested_owner: ZCode
owner: ZCode
reviewer: ZCode（窗口内子 agent，结论仅 approved_subagent）
depends_on: [TASK-007, TASK-009, TASK-012, TASK-024]
base_commit: e96b3eb880bdfcfca182aa1350d9ff56798556c1
branch: agent/zcode/TASK-023-pdf-mobi-import
worktree: G:/CODEX/New Manga.worktrees/TASK-023-zcode
integration_commit: ba7d560f346bb1af8a6e71474e23904bc066cf81
---

# TASK-023：实现 PDF/MOBI 导入路线

**READY（2026-09-17 ZCode 全权窗口——插队项）**：用户批准解冻，并**同时批准本 Task 新增 `pypdfium2` 依赖**（原唯一阻塞项）。Owner=`ZCode`、Reviewer=窗口内子 agent（结论仅 `approved_subagent`）、`base=e96b3eb`、branch/worktree 见顶部元数据。

**插队规则**：本 Task 为窗口内**插队/优先替补项**——当且仅当出现下列情形才启动：(a) 用户在窗口内指示优先；(b) W1+W2（及已启动的 W3）于 `06:30` 前全部集成完成、余量 ≥2h；(c) 出现必须优先处理的新任务。**不满足则本窗口不动它**（窗口报告登记为"依赖已解除、待排期"）。

**依赖变更注意事项（必须留证）**：向共享测试 venv 安装 `pypdfium2` 会**改变其他 Agent 的运行环境**。因此：①只允许新增该一项依赖，不得顺带升级/新增其他项；②必须在安装**前后各跑一次全仓**并记录对照；③若既有测试断言 pypdfium2 缺失或 readiness 为 `missing_dependency`，须在本 Task 内一并更新并说明理由（**不得**用放宽断言绕过）。

本 Task 仅为规划，尚未授权、认领或实施。当前阶段见 [STATUS](../STATUS.md)；共用流程见 [协作协议](../09_COLLABORATION.md)。

## 来源与目标

D01 §2；D02 §8；D04 §8；D05 §52；G17。网页导入已按 U-1 取消；本任务规划仅覆盖 PDF/MOBI。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：本任务为设计/实验/基础工作，验收以下专属条件；关联产品 AC 不因本任务完成就自动 PASS。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 依据用户批准的格式支持范围实现PDF/MOBI解析，复用Managed Copy/Page用例。（PDF：pypdfium2 光栅化＋`ImportDocumentsUseCase` 复用 images 的 Managed Copy/去重/排序纪律；**MOBI 光栅化 BLOCKED**——无批准解析依赖，非 PDF 载荷 typed `UNSUPPORTED_FORMAT` 可诊断，未自行发明解析器，未记 PASS）
- [x] 保留排序/来源/重复策略，畸形/加密/不支持输入可诊断，取消和失败不破坏已导入数据。（页级 hash 去重＋order 顺延；INVALID_DOCUMENT/ENCRYPTED/UNSUPPORTED_FORMAT/COPY_FAILED 分列；取消保留已提交页并报告剩余；先导数据在后续失败时原样——均有测试）
- [x] 交付 Handoff=[doc/handoffs/TASK-023-7fa9118.md](../handoffs/TASK-023-7fa9118.md)；Review=[doc/reviews/TASK-023-7fa9118.md](../reviews/TASK-023-7fa9118.md)（**approved_subagent**，报告 commit `c87f21c`，四轴均 executed；R-001～R-004 全 P3 不阻断）；集成=`ba7d560`（merge，parents `cca8b09`+`c87f21c`），集成后复验全仓 **770 passed / 0 skipped**、exit 0。

## 允许修改范围

**已由 Codex 按实际结构收紧（2026-09-17，窗口授权）**：原草案中的 `src/application/importing/documents/**`、`src/infrastructure/importers/**`、`tests/import_formats/**` **当前均不存在**，已替换为下列实测结构。

- `src/application/importing/**`（存在，现为 `importing/images/**`；文档导入用例可在此新增子包）
- `src/infrastructure/importing.py`（存在的模块；如确需拆包须在 Handoff 说明理由）
- `pyproject.toml` / `requirements*.txt`（**仅允许新增 `pypdfium2`**，用户 2026-09-17 批准）
- `tests/library/**`（存在）与**新建** `tests/import_formats/**`
- `doc/tasks/TASK-023.md`、`doc/handoffs/TASK-023-*.md`、`verification/TASK-023/**`

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/import_formats；自制多页PDF/MOBI、损坏/不支持输入、顺序和源Hash。
- 以上均为计划，当前结果全部 NOT_RUN；命令中的测试目录需本 Task 实际建立后才能运行。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

## 依赖、风险与阻塞

硬依赖：[TASK-007](TASK-007.md)、[TASK-009](TASK-009.md)、[TASK-012](TASK-012.md)、[TASK-024](TASK-024.md)。依赖必须已经集成 done 才可开始。

缺少格式契约不得自行发明行为；所有测试素材应有明确使用许可。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 交付与运行记录

- Handoff：尚无。
- Review：尚无。
- 实际执行/实验/测试：尚无。
- 最近状态：2026-09-13 接管规划创建；proposed，pending_user_review。
- **最近状态（当前，唯一）**：2026-09-18 02:3x 由 ZCode 在窗口内开工（插队规则(b) 达标：W1+W2+W3 已于 06:30 前全部集成、余量 ≥2h）；分支按窗口规则 `git merge master` 快进至 `cca8b09`（base=e96b3eb 之上为窗口授权与 W1-W3 集成提交，写集合不相交）。MOBI 契约边界：pypdfium2 仅覆盖 PDF（U-2 范围），MOBI 解析无批准依赖 → 实现为**可诊断不支持路径**并登记 BLOCKED，不自行发明解析行为。
- **最近状态（当前，唯一）**：实现 head=`7fa9118`（开工 `d117467`）：requirements 加 `pypdfium2==5.13.0`（唯一批准项；安装前后全仓各 **764 passed/0 skipped exit 0** 留证；readiness 断言零命中无需更新）＋`application/importing/documents/` 新子包＋`PdfiumDocumentRaster`＋`tests/import_formats/` 6 例全过（library 回归 46 passed）。MOBI BLOCKED 如实登记。遗留：bootstrap 生产装配点（白名单外）。Review `c87f21c`=**approved_subagent**（R-001～R-004 全 P3 不阻断：死变量/测试 double 低保真/ENCRYPTED 真实映射未验证（作者已如实标注）/中途失败页不进 pending）；集成 `ba7d560`，集成后复验全仓 770 passed/0 skipped exit 0。**TASK-023 已收口 `done`；期满后须 Codex + DSH 外部 post-hoc 复审（可推翻）。**遗留：bootstrap 生产装配点（白名单外）、MOBI 光栅化 BLOCKED（解锁=批准 MOBI 解析依赖）、R-004 语义完善。
