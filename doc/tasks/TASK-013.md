---
id: TASK-013
title: 实现工作台与任务进度交互
kind: implementation
status: done
approval: approved
suggested_owner: ZCode
owner: ZCode
reviewer: DeepSeek Harness
depends_on: [TASK-011, TASK-012, TASK-014]
base_commit: 46646d58b3f645fa30fe7e10fae050218f9c55bb
branch: agent/zcode/TASK-013-workbench-task-progress
worktree: G:/CODEX/New Manga.worktrees/TASK-013-zcode
delivery_head: da1daf1
reviewed_head: da1daf11e65fdc80f20450bec1f5e87234b826c7
implementation_merge: 32a1eb5
integration_commit: f0814a8
review_report_commit: 9fbfa48
---

# TASK-013：实现工作台与任务进度交互

本 Task 已由 Owner=ZCode 完成实现，经过 Reviewer=DeepSeek Harness 独立 Review，并由 Codex 按 §6.6 串行集成。交付 head 固定 `da1daf1`（base `46646d5`），实现合并为 `32a1eb5`，`integration_commit=f0814a8`；R-001～R-003 已收口，R-1 另行裁决为独立装配切片，当前不接线。TASK-015 及其他冻结 Task 不受本次授权影响。

## 来源与目标

D05 §15～36/55/61～65；D06 §74～79/102～103；D08 AC-PAGE/PROGRESS/NFR-UI/ERRUI。D 编号对应 [文档索引](../00_INDEX.md)；依赖交付物是后续输入，当前并不存在。

主责任编号 AC：AC-PAGE-002、AC-PAGE-003、AC-PROGRESS-001、AC-PROGRESS-002、AC-PROGRESS-003、AC-PROGRESS-004、AC-PROGRESS-005、AC-PROGRESS-006、AC-PROGRESS-007、AC-NFR-UI-001、AC-NFR-UI-002。完整映射见 [验收追踪](../13_ACCEPTANCE_TRACEABILITY.md)。

## Acceptance Criteria

- [x] 固定PageList/Viewer/Inspector/底部TaskProgress同时可用，支持当前章节多选与命令入口、Region编辑和三种图/Compare。（实现 commit `da1daf1`；Clean/Translated 产物占位与几何画布编辑的范围边界见 Handoff）
- [x] PageList与TaskProgress使用同一投影；Viewer当前页与Pipeline焦点分开；失败/完成/跳过统计定位正确。（`src/ui/models/tasks/projection.py` 单一投影；与 `get_task_progress` 口径一致性有专项测试）
- [x] 暂停/停止/继续与状态按钮匹配；频繁百分比更新节流、关键事件及时响应；Dirty导航不丢编辑。（D06 §103 按钮矩阵 9 状态测试；250 ms 节流；暂停乐观反馈 ≤200 ms 断言；dirty 三键确认对话框）
- [x] 交付 Handoff、实际测试/审阅记录和未完成项，经非作者独立 Review 与 Codex 集成验证后才能 done。（Review=`9fbfa48` approved；集成=`f0814a8`；集成后验证见 [integration-f0814a8.md](../../verification/TASK-013/integration-f0814a8.md)）

## 允许修改范围

以下为相对仓库根目录的允许路径；源码路径均为拟议边界，不表示当前文件存在。ready 前由 Codex与已冻结实际结构核对并收紧；不能自行扩展到整个 src/tests。

- src/ui/qml/workbench/**
- src/ui/viewmodels/workbench/**
- src/ui/models/tasks/**
- tests/workbench/**
- doc/tasks/TASK-013.md
- doc/handoffs/TASK-013-*.md
- verification/TASK-013/**

## 禁止范围

不得修改未列出的其他 Task、AGENTS、生产数据或用户源文件。实验任务不写生产 src；Review 任务不顺手修生产代码。共享接口、Schema、依赖或装配超出白名单时，先由 Codex在本 Task 明确范围变更。

## 测试要求

- 计划：python -m pytest tests/workbench；选择切换、按钮enable、失败筛选、collapse、38成功2失败、模态覆盖确认。
- Mock长任务中操作UI不冻结；暂停反馈按获批AC阈值实测。
- 实际记录包含 commit、OS/依赖/设备、准确命令、退出码、结果和证据路径；模型/视觉/性能结果不由Mock代替。

### 作者执行记录（executed，2026-09-16）

- 环境：Windows 10.0.26200 x64；Python 3.12.3；PySide6 6.11.2；解释器 `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`；默认 Windows Qt 平台，未设置 offscreen。
- 命令：`python -m pytest tests/workbench` → **50 passed, 0 skipped**，退出码 0。无 skip 项，无逐项 skip 原因需要登记。
- 命令：`python -m pytest`（全量回归，testpaths=tests）→ **465 passed, 0 skipped**，退出码 0；含 TASK-012 已审 `tests/ui_shell` 套件与架构守卫，无回归。
- 证据：[windows-pytest-workbench.txt](../../verification/TASK-013/windows-pytest-workbench.txt)、[windows-pytest-full-suite.txt](../../verification/TASK-013/windows-pytest-full-suite.txt)。
- AC-NFR-UI-001 为 Mock 证据：worker 线程执行 + GUI 心跳存活测试；真实 AI 负载下的性能结论不在本 Task 范围（D07 目标值需 Benchmark）。

## 依赖、风险与阻塞

硬依赖：[TASK-011](TASK-011.md)、[TASK-012](TASK-012.md)、[TASK-014](TASK-014.md)。依赖必须已经集成 done 才可开始。

单Region重全翻译只给专项锁任务级确认；Page/Region Lock仍阻止。

如本 Task 需要获批契约或用户范围决定而输入仍未就绪，登记具体 blocker 并保持未释放。建议 Owner 不是已经分派；Codex释放时指定实际 owner 与非作者 reviewer。

## 集成后验证记录（Codex，2026-09-16）

- 被测主线包含实现合并 `32a1eb5`、Review 报告合并 `f0814a8` 及本次 R-001/R-003 修正；`integration_commit` 由 Codex 填写为 `f0814a8`。
- 环境：Windows 11 `10.0.26200` AMD64；Python 3.12.3；PySide6 6.11.2；解释器 `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`；默认 Windows Qt，未设置 `QT_QPA_PLATFORM=offscreen`。
- `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests/workbench -v` → **51 passed, 0 skipped**，退出码 0。
- `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe -m pytest tests -q -rs` → **460 passed, 6 skipped**，退出码 0。6 个 skip 均因 `openssl unavailable`：`tests/network/test_connection_tester.py:106`、`tests/network/test_transport_tls.py:39/47/62/69/83`。
- `git diff --check` → PASS（无空白错误）。

## Review finding disposition

- **R-001 closed**：移除 `QThread.terminate()`；shutdown 超时不强杀正在执行的 worker，并对非暂停 run 请求取消。代码明确标注：接入持久化 `PipelineStore` 前必须改为有确认的安全边界 shutdown 协议；暂停 run 不被误标为取消，专项测试已回归通过。
- **R-002 closed**：按协作协议 §3.6，`doc/00_INDEX.md`、`doc/12_ROADMAP.md`、`doc/STATUS.md`、`doc/tasks/README.md` 的状态、Task 导航和链接由 Codex 统一回填；未借元数据权限修改需求、契约、AGENTS 或实现范围。
- **R-003 closed**：页步进的索引计算与边界收窄下沉至 `WorkbenchViewModel.stepPage(int)`；QML `stepPage` 仅转发 toolbar 动作；新增 ViewModel 边界测试。

## R-1 接线范围裁决

- **裁决**：批准建立独立最小生产装配切片，但不在 TASK-013 集成中接线；当前 `R-1=BLOCKED/NOT_RUN`，不以空实现或内存实现替代生产绑定，也不释放 TASK-015 或其他冻结 Task。
- **拟议范围**：`G:/CODEX/New Manga/src/bootstrap/app.py`、`G:/CODEX/New Manga/tests/core/test_bootstrap.py`、`G:/CODEX/New Manga/verification/TASK-013/**`、`G:/CODEX/New Manga/doc/00_INDEX.md`、`G:/CODEX/New Manga/doc/12_ROADMAP.md`、`G:/CODEX/New Manga/doc/STATUS.md`、`G:/CODEX/New Manga/doc/tasks/README.md`；Owner=`Codex`，Reviewer=`DeepSeek Harness`，建议 base=`07a5881`。该切片不得修改 Schema/migration、共享 Port、依赖清单、其他 Task、AGENTS 或 TASK-012 已审实现。
- **已核实的生产 seam**：`SqliteLibraryRepository.list_pages(chapter_id)` 可绑定 page catalog；`SqliteRegionRepository.list_regions/get_region` 与 `RegionEditingService.save_manual_translation` 可绑定 Region/人工译文编辑；`NavigationViewModel` 可作为导航依赖。
- **未就绪的生产 seam**：当前 `PipelineService` 仅发现 `InMemoryTargetCatalog`、`InMemoryPipelineStore`、`InMemorySnapshotProvider` 与 `DeterministicStepExecutor`；尚无生产 `TargetCatalog.expand/current/commit_step`、PipelineStore、SnapshotProvider 和真实 StepExecutor 的完整装配。因此本次不向 QML 注入 `workbenchViewModel`，生产 Workbench 继续保持诚实空状态。
- **接线验收门槛**：提供上述完整生产 Pipeline 绑定；`assemble_services` 只使用真实 SQLite/服务对象并通过 `setContextProperty("workbenchViewModel", ...)` 注入；入口验证真实 Chapter→Book/页面/Region 查询且无硬编码；Windows 默认 Qt（不设 offscreen）入口 smoke、WorkBench/UI 与全量回归均须记录 passed/skipped 分列及 skip 原因。

## 交付与运行记录

- Handoff：[TASK-013 工作台切片 Handoff](../handoffs/TASK-013-workbench-task-progress.md)，固定 base=`46646d5`、delivery_head=`da1daf1`。
- Review：[TASK-013 Review](../reviews/TASK-013-da1daf1.md)，`report_commit=9fbfa48`，approved。
- 实际执行/实验/测试：见上文“作者执行记录”“集成后验证记录”与 [verification/TASK-013](../../verification/TASK-013/)。
- 最近状态：2026-09-16 依赖 TASK-011/012/014 全部完成后授权并实施；实现 commit `da1daf1`，实现合并 `32a1eb5`；DSH Review `9fbfa48` approved；Codex 保留实现与 Review merge，填写 `integration_commit=f0814a8`，完成集成后 `51 passed, 0 skipped` / `460 passed, 6 skipped` 验证；Task 置 `done`。R-1 保持独立切片 BLOCKED/NOT_RUN。
