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

本 Task 已由 Owner=ZCode 完成实现，经过 Reviewer=DeepSeek Harness 独立 Review，并由 Codex 按 §6.6 串行集成。交付 head 固定 `da1daf1`（base `46646d5`），实现合并为 `32a1eb5`，`integration_commit=f0814a8`；R-001～R-003 已收口，R-1 另行裁决为独立装配切片，当前不接线但已解除前置阻塞（`READY/NOT_RUN`）。TASK-015 及其他冻结 Task 不受本次授权影响。

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

### 生产 Pipeline seam 集成切片（本次授权）

本切片是用户在 2026-09-16 明确授权、承接 R-1 前置阻塞的范围变更；不改写原工作台实现，也不启动 TASK-015 或其他冻结 Task。固定对象：`base_commit=126bab5`、`reviewed_head=e5b58e7378a9fa4e5737220e51a9000a19a21a4e`、Review 报告 `8f7c454`、`integration_commit=49c72fdf4d347be70636770c366c146650888ef4`；Owner=`Codex`，Reviewer=`DeepSeek Harness`。

实际授权路径：

- `src/application/tasks/service.py`
- `src/infrastructure/sqlite/schema.py`
- `src/infrastructure/sqlite/pipeline.py`
- `src/infrastructure/pipeline/**`
- `tests/pipeline/**`
- `tests/storage/**`
- `tests/library/test_sqlite_library.py`、`tests/editing/test_sqlite_regions.py`（v3 schema 上限 fixture 对齐）
- `verification/TASK-013/**`
- 本文件仅作授权/状态/链接元数据回填；四条 Codex 统一状态文档仅作导航元数据回填

本切片验收：v3 追加 Pipeline 持久化表；真实 SQLite TargetCatalog/Store/SnapshotProvider/StepExecutor 装配；Pipeline 生命周期持久化、恢复与失败码；Windows 默认 Qt 的 pipeline/storage/workbench/全量验证。生产 `src/bootstrap/app.py`、QML、`src/domain/**`、共享 Protocol、v1/v2 schema 语义、依赖清单、AGENTS、TASK-012 已审实现和冻结 Task 均不在本切片内。

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

- **裁决**：批准建立独立最小生产装配切片，但不在 TASK-013 集成中接线；当前 `R-1=READY/NOT_RUN`，本轮不以空实现或内存实现替代生产绑定，也不释放 TASK-015 或其他冻结 Task。
- **拟议范围**：`G:/CODEX/New Manga/src/bootstrap/app.py`、`G:/CODEX/New Manga/tests/core/test_bootstrap.py`、`G:/CODEX/New Manga/verification/TASK-013/**`、`G:/CODEX/New Manga/doc/00_INDEX.md`、`G:/CODEX/New Manga/doc/12_ROADMAP.md`、`G:/CODEX/New Manga/doc/STATUS.md`、`G:/CODEX/New Manga/doc/tasks/README.md`；Owner=`Codex`，Reviewer=`DeepSeek Harness`，建议 base=`07a5881`。该切片不得修改 Schema/migration、共享 Port、依赖清单、其他 Task、AGENTS 或 TASK-012 已审实现。
- **已核实的生产 seam**：`SqliteLibraryRepository.list_pages(chapter_id)` 可绑定 page catalog；`SqliteRegionRepository.list_regions/get_region` 与 `RegionEditingService.save_manual_translation` 可绑定 Region/人工译文编辑；`NavigationViewModel` 可作为导航依赖。
- **已就绪的生产 seam**：本轮已集成 `SqliteTargetCatalog`、`SqlitePipelineStore`、`SqliteSnapshotProvider` 与 `ProductionStepExecutor`，覆盖真实 `TargetCatalog.expand/current/commit_step`、Pipeline 持久化、快照恢复和执行失败码。因此 R-1 已解除前置阻塞；本次仍不向 QML 注入 `workbenchViewModel`，生产 Workbench 继续保持诚实空状态。
- **接线验收门槛**：提供上述完整生产 Pipeline 绑定；`assemble_services` 只使用真实 SQLite/服务对象并通过 `setContextProperty("workbenchViewModel", ...)` 注入；入口验证真实 Chapter→Book/页面/Region 查询且无硬编码；Windows 默认 Qt（不设 offscreen）入口 smoke、WorkBench/UI 与全量回归均须记录 passed/skipped 分列及 skip 原因。

## 交付与运行记录

- Handoff：[TASK-013 工作台切片 Handoff](../handoffs/TASK-013-workbench-task-progress.md)，固定 base=`46646d5`、delivery_head=`da1daf1`。
- Review：[TASK-013 Review](../reviews/TASK-013-da1daf1.md)，`report_commit=9fbfa48`，approved。
- 实际执行/实验/测试：见上文“作者执行记录”“集成后验证记录”与 [verification/TASK-013](../../verification/TASK-013/)。
- 最近状态：2026-09-16 依赖 TASK-011/012/014 全部完成后授权并实施；原工作台实现 commit `da1daf1`，实现合并 `32a1eb5`；DSH Review `9fbfa48` approved，原 Task `integration_commit=f0814a8`；随后按用户明确授权，以 `base_commit=126bab5` 集成生产 Pipeline seam，固定 `reviewed_head=e5b58e7`、Review `8f7c454`、`integration_commit=49c72fdf`，关闭 R-01/R-02，R-03 合并到 R-1；Task 置 `done`。R-1 为独立 `READY/NOT_RUN` 切片，未修改 bootstrap/QML。

---

# T1.1.2 设计：Region Canvas & Creator（本节 2026-09-21 追加，不改动上文任何历史记录）

本节是 rebaseline Task **T1.1.2** 的设计记录。按 `REBASELINE_PLAN` 的 legacy 映射，TASK-013 → T1.1.2（MERGE + REOPEN canvas gap），故设计落在本文件；上文 2026-09-16 的历史记录、Review disposition 与 R-1 裁决原文保留不删。

## 授权与身份

- **唯一 ACTIVE Task**（Owner 裁决 2026-09-21，见 `doc/STATUS.md`）。Owner=`Qoder`；非作者 Reviewer=`antigravity`；Integrator=`Codex`。满足 Owner ≠ Reviewer。
- 授权 base `f8a4f4ab9a1e66808bfa82fd1a59c014fa7ec8a2`；激活记录提交为 `49f35e8`，故实际开工 base 以开工前 merge master 后的 head 为准，将在 Handoff 记明确切值。
- 允许路径沿用 TASK-013 白名单：`src/ui/qml/workbench/**`、`src/ui/viewmodels/workbench/**`、`src/ui/models/tasks/**`、`tests/workbench/**`、本文件、`doc/handoffs/TASK-013-*.md`、`verification/TASK-013/**`。
- **一处越出白名单的必要改动**：`src/bootstrap/app.py` 需在构造 `WorkbenchViewModel`（当前 :882-888）处补 `region_creator=editing`、`region_deleter=editing`。`app.py` 按 `REBASELINE_PLAN` §Agent allocation 是**串行经 Codex** 的闸口，故该行由 Codex 落地，不由本 Task 作者自行改。

## 当前仓库事实（实测，非推断）

- 上文 :113「本次仍不向 QML 注入 `workbenchViewModel`」已被后续实现推翻：**现状已注入** —— `src/bootstrap/app.py:957` `root_context.setContextProperty("workbenchViewModel", services.workbench)`，`WorkbenchView.qml:20-21` 以 `typeof … !== "undefined"` 守卫读取。因此 T1.1.2 无需再做 VM 总线接线。
- `src/ui/qml/workbench/ViewerPanel.qml` 是一个 `Image` + `fillMode: Image.PreserveAspectFit` 包在 `Rectangle` 里，**没有** `Canvas`、没有叠加层、没有缩放/平移。（注意：该文件第 5 行注释含「Viewer/Canvas」字样，纯文本检索会误判。）
- `grep delete|Delete|删除 src/ui/qml/workbench/*.qml` **零命中** ⇒ 用户今天无法从 UI 移除 Region；`RegionEditingService.delete_region` 存在于 service 层但无人调用。
- `WorkbenchViewModel` 的 Region 面是**只读**鸭子类型 catalog（`__init__` :80-81：`list_regions`/`get_region`），无任何写 Region 的路径；既有唯一写槽 `saveInspector`（:587）走注入的 `translation_editor`，未绑定时以 `_record_command_error("no translation editor bound", stage="editor")` 给 typed 错误面。
- `Page` 实体带 `width`/`height` 且 `__post_init__` 保证为正（`src/domain/pages/entities.py:26-27,41-42`）；`VM._load_pages`（:175-186）已遍历这些对象，只是未把宽高放进 row dict。
- `create_region`（`src/application/editing/service.py:247`）的 `origin` **默认即 `RegionOrigin.USER`**，`reading_order=None` 自动取 max+1，内部为「first revision + pointer 一次原子提交」⇒ AC「落 `regions` + `region_revisions` 两表」由 service 保证、**本 Task 不需新增实现**，但仍必须给出真落库证据（见测试策略），二者不矛盾。
- 几何为**整数且带构造期校验**：`BBox.__post_init__` 对 `width/height<=0` 抛 `ValueError`；`RegionGeometry.__post_init__` 对 polygon `<3` 点抛 `ValueError`。⇒ 退化输入必须在写入前拦截，否则异常会冒进 QML。

## 范围（含两处超出计划 :104 字面的增加，均由 Owner 明确要求）

1. 矩形与多边形**两种输入都做**（忠于 :104）。
2. overlay **同时绘制本页已有 Region 的框**并高亮当前选中项。超出 :104 字面（其只写 "input"），理由：不显示已有框即盲画，气泡会叠在一起。
3. 本片含**最小删除入口**（Delete 键或 Inspector 删除动作）。超出 :104 字面，理由：绘制即时落库 + 已有框可见 ⇒ 不补删除就是「看得见删不掉」的不自洽切片。

Reviewer 判 Scope/spec 时**以本节为准**，不以 `REBASELINE_PLAN.md` :104 字面为准；:104 的 AC（:108）仍为规格来源。

## 架构与接缝

唯一真正的分层问题是「视口坐标 ↔ 页面整数像素」换算放在哪。视口尺寸只有 QML 知道，而已有框的回显也必须由 QML 计算内容矩形，若 Python 再反演一次同一段 letterbox 算术就会有两份会漂移的实现。**接缝取归一化坐标 0..1**：QML 独占 item↔归一化（视图关注点），VM 独占归一化↔页面像素（模型关注点），两侧各只有一份换算。

- **新增 `src/ui/viewmodels/workbench/region_canvas.py`**：不 import PySide6 的纯函数模块。`normalized_to_page_geometry(points, page_w, page_h) -> RegionGeometry` 返回**真的 domain 值对象**（页面整数像素的 `BBox` + `polygon`），内含取整、clamp、退化判定。理由：`RegionEditingService.create_region` 要的是 `RegionGeometry`，而 `Region.snapshot_state()` 在 `src/domain/regions/entities.py:272` 直接调 `self.geometry.as_jsonable()` —— 喂 dict 会抛 `AttributeError`；而架构守卫 `tests/core/test_architecture.py:15` 的 `UI_FORBIDDEN` **只禁 `infrastructure`**，`domain` 在 UI 层是允许的（VM 现在就已 `from domain.tasks.models import …`），故 import `domain.regions.entities` 不破坏守卫、也贴合既有实践。模块仍是纯 Python，全部换算与校验可无 Qt 单测。
- **改 `viewmodel.py`**：`_load_pages` row 补 `width`/`height`；新增两个 int Property `viewerPageWidth`/`viewerPageHeight`（读 `_pages[_viewer_page_id]`，由既有 `viewerChanged` 通知）；`__init__` 补 `region_creator=None`、`region_deleter=None` 两个鸭子注入；`get_inspector_regions`（:499-517，其 row 构造在 :504-517 且当前**不含几何**）返回补 `"geometry"`；新增三槽，全部复刻 `saveInspector` 的「未绑定 → typed error，绝不抛到 QML」范式：
  - `@Slot(float,float,float,float) createRectangle(nx0, ny0, nx1, ny1)` —— 四值均为归一化 0..1；**不要求对角顺序**，归一化函数自行取 min/max，故向左/向上拖拽同样合法。
  - `@Slot(str) createPolygon(pointsJson)` —— 固定为 `JSON.stringify` 的 `[[nx, ny], …]`（归一化浮点数组的数组），至少 3 点；QML 与 Python 只以字符串相交，避免 `QVariantList` 的元素类型强制歧义。
  - `@Slot(str) deleteRegion(region_id)`
  三者的 `page_id` 一律取 `self._viewer_page_id`（既有 Property :308），**不接受 QML 传入**。
  选中态复用既有 `inspectorRegionId`（:534），不新建 Property。
- **新增 `src/ui/qml/workbench/RegionOverlay.qml`**：`Canvas` + `MouseArea`，持绘制模式、实时预览、Esc 取消、Delete 删除、以及 item↔归一化 换算。在制状态是纯视图态。**两条硬约束**：① 算 fit rect 必须用 VM 的 `viewerPageWidth`/`viewerPageHeight`，**禁止读 `mainImage.sourceSize`** —— 换算两侧必须用同一组常数，否则「框画在 A、点击落在 B」这类分叉无法排除；② 仅当 `viewerMode == "original"` 时可见且接受输入（几何属原图像素空间，产物图尺寸不保证一致；计划 :103 的 Objective 本身也是 "draw text regions on the **original page**"）。
- **改 `ViewerPanel.qml`**：暴露图像矩形并挂载 overlay。不动 `Main.qml`、不动 `src/ui/qml/shell/`，故不触碰「顶层 QML shell 串行」闸口。

## 数据流与坐标换算

QML 侧（唯一知道视口尺寸 `W`/`H` 处；`page_w`/`page_h` 取自 VM 的 `viewerPageWidth`/`viewerPageHeight`，与 VM 换算用的是同一组常数）：

```
scale   = min(W/page_w, H/page_h)
disp_w  = page_w*scale;  disp_h = page_h*scale
offset_x= (W-disp_w)/2;  offset_y= (H-disp_h)/2
nx      = (mx-offset_x)/disp_w;  ny = (my-offset_y)/disp_h
```

VM 侧（唯一知道页面像素处）：`v = math.floor(n*size + 0.5)` 后 clamp 到 `[0, size]`（右/下边取 exclusive，故全宽拖拽恰好得 `x=0, w=page_w`）；`bbox` 由点集 min/max 导出。

**舍入语义必须钉死为 half-up，不得写 `round(n*size)`**：Python 内建 `round` 是 half-to-even，实测 `round(0.5)=0`、`round(1.5)=2`、`round(2.5)=2`。本设计的测试要逐像素断言整数，并列点语义不统一会让实现方与 Reviewer 在 `n*size` 正好落在 `.5` 时得出不同值，故显式规定 `floor(n*size + 0.5)`（QML 侧 item→归一化不含舍入，不参与此问题）。

一组带数字的基准（同时作为测试断言）：页面 `800×1200`、pane `600×600` ⇒ `scale=0.5`、`disp=400×600`、`offset=(100,0)`；item `(150,100)→(350,400)` ⇒ 归一化 `(0.125,0.1667)-(0.625,0.6667)` ⇒ 页面像素 `bbox=[100,200,400,600]`、`polygon=[(100,200),(500,200),(500,800),(100,800)]`。回显走同一常数的逆运算。

## 错误处理与边界

1. writer 未绑定（即 Codex 那行未落时的可见化）→ `_record_command_error("no region creator bound", stage="editor")`，走既有 `commandError`/`commandErrorText` 面；不抛、不静默。
2. 无当前页，或该行页宽高缺失/≤ 0 → 在**进入换算之前**分别给 typed error（`no page selected` / `page size unavailable`）。依据实测：`_ManagedPageCatalog.list_pages`（`app.py:162-163`）纯直通 `SqliteLibraryRepository.list_pages -> list[Page]`（`src/infrastructure/sqlite/library.py:358`），生产**确实**带宽高；但 VM 取 page 字段一律写成 `getattr(page, ..., 默认)`，说明测试替身可能不带，而 `floor(0.5 * 0) = 0` 不抛异常，会让所有框静默塌到原点而不是快速失败。
3. 退化输入（零面积、polygon `<3` 点）→ **写入前**拦截并给 typed error，依据见上节 `__post_init__` 会抛 `ValueError`。
4. 落在 letterbox 灰带的起笔/加点**直接拒绝**（clamp 前 `n` 超出 0..1），不 clamp 成贴边假框；VM 侧仍保留 clamp 作纵深防御，因为槽是公开契约、测试会直接喂归一化值。
5. 绘制中途切页/起 run/关窗 → overlay 丢在制点集，不落库不报错（尚无副作用）。
6. **dirty 守卫分岔**：`_navigate` 在 Inspector dirty 时会弹保存确认；无条件选中新框会触发该弹窗，而绕过 `_navigate` 直接切选中又会丢掉用户刚敲进 Inspector 的未保存译文。取舍：无 dirty → 选中新框（满足 AC「更新 Inspector」的直观读法）；有 dirty → 仅 `inspectorChanged.emit()` 刷新列表、不抢选中。两分支均可测。
7. 删除为软删，`list_regions`（:279-280）本就过滤 `deleted` ⇒ 删后 overlay 自动不再绘制，无需新增广播；若删的正是选中项则清 `_inspector_region_id`。
8. **run 期间绘制不加禁止**：`tests/workbench/test_gui_write_during_run.py` 已把「run 执行期间 GUI 写入必须存活」定为契约，restore latch 只拒 worker start 且 restore 至今未接生产（见 R-012 记录）。本片不引入新限制，也不重复添加同类测试。

## 测试策略

- 新增 `tests/workbench/test_region_canvas.py`（无 Qt）：上节 800×1200/600×600 的确切整数；全宽边界；越界 clamp；零面积；`<3` 点；矩形→4 点顺序。**并列舍入判别**：取页面 `100×100`、`n=0.125`（`0.125 = 2⁻³` 二进制精确，故 `n*size = 12.5` 是**可证明的精确并列**，不靠浮点巧合），断言得 `13`（half-up），而内建 `round(12.5)` 得 `12` —— 该用例在两种语义下结果不同，故能真正钉死规定而非空写。
- 改 `tests/workbench/test_workbench_viewmodel.py`：creator 收到的是页面像素 int geometry；未绑定 → typed error 且不抛；无页 → typed error；**页宽高缺失或为 0 → typed error 且 creator 未被调用**（防止静默塌到原点）；**退化输入 → creator 未被调用**（关键判别，证明校验发生在写之前）；dirty 不抢选中 / 非 dirty 抢选中；`deleteRegion` 未绑定 → typed error。
- 一条**真 `RegionEditingService` + 真 SQLite**（非 Mock）的落库证据：注入真 service，调 `createRectangle`，断 `regions` 恰新增 1 行、`region_revisions` 恰新增 1 行、`origin == 'user'`、pointer 指向该 revision。
- 改 `tests/workbench/test_qml_workbench.py`：仅验 overlay 可被 QML 加载、`objectName` 存在、带 `geometry` 的 `inspectorRegions` 不致错。**不做合成鼠标拖拽**——本仓有既有时序 flaky 记录，不把正确性押在合成事件时序上。
- **判别力双向**：删除前置校验 / 把 `origin` 传成 `MACHINE` / 去掉 clamp 三种变异下对应测试必须 FAIL；变异日志带 EXIT 与 shell/venv 头逐次入库（Q-009 纪律）。
- 回归：`--collect-only` ≥ 982；全量 ≥5 次 EXIT=0；PowerShell 注册表 PATH 口径（976 passed + 6 skipped）与 Git Bash 口径（982 passed）的总数与差值须在文档单处说明。
- **诚实项**：Codex 的 `app.py` 注入行落地前，「生产环境真能画框」这项验证记 **BLOCKED 并注明原因**，不以注入 fake 通过来冒充 PASS。

## 遗留与交接口

- 交 Codex：`src/bootstrap/app.py` 构造 `WorkbenchViewModel` 处补 `region_creator=editing`、`region_deleter=editing`（串行闸口，作者不代改）。
- 交 Codex：`REBASELINE_PLAN.md` :93 写「implement the chosen `TextDetector` adapter」，但 `TextDetector` 在 `src/` 全仓零命中，真实契约是 `src/ports/detection/ports.py:130` 的 `DetectionProvider`（与已收口的 R-013 同类计划/仓库不一致，建议登记 R-014）。
- 不在本片：Region 几何的**编辑/微调**（`save_geometry` 已存在但带 guard 语义，属独立交互）、多页批量、undo 栈。
- 已知限制（本片故意不做，非缺陷）：overlay 仅在 `original` 模式显示与接受输入，`clean`/`translated`/`compare` 下隐藏。若后续要在译图上对照着看已有框，需要一个明确的「产物图与原图尺寸一致性」前提或独立的缩放规则，届时另开切片。

---

# T1.1.2 实现计划（2026-09-21，随上节设计一并提交）

> **给执行方：** 逐任务实现，每个任务内部按「写失败测试 → 跑到失败 → 最小实现 → 跑到通过 → 提交」推进，步骤勾选框跟踪。任务顺序即依赖顺序，不要跳过测试步骤直接写实现。

**Goal:** 让用户在工作台 Original 页面上用拖拽画矩形、逐点点击画多边形，实时看到本页已有 Region 的框，并可删除误画项，落库到既有 `RegionEditingService`。

**Architecture:** QML 只负责视图关注点（item↔归一化 0..1、实时预览、绘制模式），ViewModel 只负责模型关注点（归一化↔页面整数像素、校验、调注入的 writer）。最易错的换算收进一个不依赖 Qt 的纯函数模块，用普通 pytest 逐像素断言。生产者/消费者接口全部走 VM 既有的鸭子类型注入 + typed 错误面，不新增共享契约。

**Tech Stack:** Python 3.12 / PySide6 QML（QtQuick + Canvas）/ SQLite / pytest。

**Spec:** 本文件 `# T1.1.2 设计：Region Canvas & Creator` 一节（:125-211）。计划与设计同行共进。

## Global Constraints

每个任务都隐含遵守以下各条（值从设计/仓库实测逐字抄来）：

- 允许路径仅：`src/ui/qml/workbench/**`、`src/ui/viewmodels/workbench/**`、`src/ui/models/tasks/**`、`tests/workbench/**`、本文件、`doc/handoffs/TASK-013-*.md`、`verification/TASK-013/**`。
- **禁止修改 `src/bootstrap/app.py`**：`region_creator=editing` / `region_deleter=editing` 两个注入由 Codex 串行落地（`REBASELINE_PLAN` §Agent allocation）。本计划的测试一律自行注入 writer。
- 禁止改 Schema/migration、`requirements.txt`、`AGENTS.md`、`src/ui/qml/shell/**`、`src/ui/qml/Main.qml`、其他 Task 文档；禁止新增依赖。
- 禁止放宽任何既有断言；禁止新增 `skip`/`xfail`。全量 `--collect-only` 不得低于 **982**。
- 运行环境固定：venv `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`、`PYTHONPATH=src`、`PYTHONDONTWRITEBYTECODE=1`、**不设** `QT_QPA_PLATFORM`。
- 舍入一律 `math.floor(n * size + 0.5)`（half-up），**不得使用内建 `round()`**（其 half-to-even 实测 `round(0.5)=0`、`round(12.5)=12`）。
- 任何失败面都走 `self._record_command_error(text, stage="editor")`，不得向 QML 抛异常。
- 每个任务一次提交；不 push。

## 文件结构

| 文件 | 责任 | 动作 |
|---|---|---|
| `src/ui/viewmodels/workbench/region_canvas.py` | 归一化↔页面像素 + 全部几何校验，唯一持有舍入规则；不 import PySide6 | 新建 |
| `src/ui/viewmodels/workbench/viewmodel.py` | 三个写槽 + 页尺寸 Property + inspector 行补 geometry；只做参数装配与错误映射 | 修改 |
| `src/ui/qml/workbench/RegionOverlay.qml` | 绘制模式状态机、实时预览、已有框回显、item↔归一化、Esc/Delete | 新建 |
| `src/ui/qml/workbench/ViewerPanel.qml` | 暴露 `vm` 并在 original 模式挂 overlay | 修改 |
| `src/ui/qml/workbench/WorkbenchView.qml` | 把 `vm` 传给 ViewerPanel | 修改 |
| `tests/workbench/workbench_helpers.py` | `FakePage` 补 `width`/`height`；`FakeRegion` 补 `geometry`；新增 `FakeRegionWriter`；`make_vm` 透传两个新注入 | 修改 |
| `tests/workbench/test_region_canvas.py` | 纯换算与校验 | 新建 |
| `tests/workbench/test_workbench_viewmodel.py` | 三槽行为、typed 错误、dirty 分岔 | 修改 |
| `tests/workbench/test_region_create_persistence.py` | 真 SQLite + 真 service 的两表落库证据 | 新建 |
| `tests/workbench/test_qml_workbench.py` | overlay 可加载、模式可见性 | 修改 |

---

### Task 1: 归一化↔页面像素纯函数

**Files:**
- Create: `src/ui/viewmodels/workbench/region_canvas.py`
- Create: `tests/workbench/test_region_canvas.py`

**Interfaces:**
- Consumes: 无（叶子模块，仅依赖 `domain.regions.entities`）
- Produces: `RegionCanvasError(code: str, detail: str)`（`code ∈ {"PAGE_SIZE_UNAVAILABLE","TOO_FEW_POINTS","DEGENERATE_GEOMETRY"}`，带 `.code`/`.detail`）；`normalized_to_page_geometry(points: Sequence[tuple[float, float]], page_w: int, page_h: int) -> RegionGeometry`。约定：**2 点视作轴对齐矩形两对角（顺序无关，内部取 min/max，产出 4 点顺时针环）；≥3 点视作多边形**。

- [ ] **Step 1: 写失败测试** — 建 `tests/workbench/test_region_canvas.py`

```python
"""T1.1.2: normalized(0..1) -> page-pixel geometry, and every rejection.

Qt-free by construction: this module is the single owner of the rounding rule,
so the pixel mapping the overlay draws and the mapping the writer stores are
pinned here, not re-derived in QML.
"""

from __future__ import annotations

import workbench_helpers  # noqa: F401  (sys.path injection)

import pytest

from domain.regions.entities import BBox, RegionGeometry
from ui.viewmodels.workbench.region_canvas import (
    RegionCanvasError,
    normalized_to_page_geometry,
)


def codes(excinfo) -> str:
    return excinfo.value.code


def test_design_worked_example_maps_to_documented_pixels():
    # doc/tasks/TASK-013.md design table: page 800x1200, item drag after
    # a 600x600 pane -> normalized corners below must land on exact pixels.
    geometry = normalized_to_page_geometry(
        [(0.125, 0.16666666666666666), (0.625, 0.6666666666666666)], 800, 1200
    )
    assert geometry.bbox == BBox(100, 200, 400, 600)
    assert geometry.polygon == (
        (100, 200), (500, 200), (500, 800), (100, 800),
    )


def test_half_tie_rounds_up_not_to_even():
    # 0.125 and 0.625 are dyadic (2**-3, 2**-1+2**-3) so n*size == 12.5 / 62.5
    # is an exact tie, not a float coincidence. builtin round() would yield
    # (12, 62); the contract is half-up.
    geometry = normalized_to_page_geometry(
        [(0.0, 0.0), (0.125, 0.625)], 100, 100
    )
    assert geometry.bbox == BBox(0, 0, 13, 63)


def test_rectangle_corners_may_arrive_in_any_order():
    forward = normalized_to_page_geometry([(0.25, 0.25), (0.75, 0.5)], 800, 1200)
    inverted = normalized_to_page_geometry([(0.75, 0.5), (0.25, 0.25)], 800, 1200)
    assert forward == inverted
    assert forward.bbox == BBox(200, 300, 400, 300)


def test_polygon_keeps_the_ring_it_was_given():
    geometry = normalized_to_page_geometry(
        [(0.0, 0.0), (0.5, 0.0), (0.5, 1.0)], 800, 1200
    )
    assert geometry.polygon == ((0, 0), (400, 0), (400, 1200))
    assert geometry.bbox == BBox(0, 0, 400, 1200)


def test_out_of_range_points_are_clamped_to_the_page():
    geometry = normalized_to_page_geometry(
        [(-0.2, 1.4), (0.5, 0.5), (1.3, -0.5)], 800, 1200
    )
    assert geometry.bbox == BBox(0, 600, 800, 600)


def test_zero_area_rectangle_is_rejected_before_writing():
    # RegionGeometry/BBox raise ValueError on a non-positive extent, so the
    # converter must reject first: the ViewModel maps this to a typed error.
    with pytest.raises(RegionCanvasError) as excinfo:
        normalized_to_page_geometry([(0.25, 0.25), (0.25, 0.9)], 800, 1200)
    assert codes(excinfo) == "DEGENERATE_GEOMETRY"


def test_collapsed_polygon_extent_is_rejected():
    with pytest.raises(RegionCanvasError) as excinfo:
        normalized_to_page_geometry(
            [(0.2, 0.2), (0.2, 0.5), (0.2, 0.9)], 800, 1200
        )
    assert codes(excinfo) == "DEGENERATE_GEOMETRY"


def test_two_point_polygon_needs_three_points():
    with pytest.raises(RegionCanvasError) as excinfo:
        normalized_to_page_geometry([(0.1, 0.1)], 800, 1200)
    assert codes(excinfo) == "TOO_FEW_POINTS"


def test_missing_page_dimensions_fails_fast_instead_of_collapsing():
    # A test double (or a catalog row) without width/height must not silently
    # collapse every box to the origin: floor(0.5 * 0) == 0 raises nothing.
    with pytest.raises(RegionCanvasError) as excinfo:
        normalized_to_page_geometry([(0.1, 0.1), (0.5, 0.5)], 0, 1200)
    assert codes(excinfo) == "PAGE_SIZE_UNAVAILABLE"


def test_returns_a_real_domain_geometry_not_a_dict():
    # Region.snapshot_state() calls self.geometry.as_jsonable()
    # (src/domain/regions/entities.py:272): a dict would raise AttributeError.
    geometry = normalized_to_page_geometry(
        [(0.0, 0.0), (1.0, 1.0)], 800, 1200
    )
    assert isinstance(geometry, RegionGeometry)
    assert geometry.as_jsonable() == {
        "bbox": [0, 0, 800, 1200],
        "polygon": [[0, 0], [800, 0], [800, 1200], [0, 1200]],
    }
```

- [ ] **Step 2: 跑到失败**

Run: `"$PY" -m pytest tests/workbench/test_region_canvas.py -q -p no:cacheprovider`（`$PY` = 上述 venv python）
Expected: 收集期 `ModuleNotFoundError: No module named 'ui.viewmodels.workbench.region_canvas'`，EXIT≠0

- [ ] **Step 3: 最小实现** — 建 `src/ui/viewmodels/workbench/region_canvas.py`

```python
"""Normalized (0..1) to page-pixel geometry for the region canvas (T1.1.2).

Qt-free by design. QML owns item->normalized because only it knows the
viewport; this module owns normalized->page pixels because only the model
layer may store integers. Two consequences are pinned here rather than left
to each caller:

- the rounding rule is half-up (``floor(n * size + 0.5)``). Python's builtin
  ``round`` is half-to-even -- round(0.5)==0, round(12.5)==12 -- and the
  pixel values are asserted exactly, so an unstable tie rule would let the
  implementation and its reviewer disagree on half-pixel boundaries;
- every rejection happens before a ``RegionGeometry`` is built, because
  ``BBox``/``RegionGeometry`` raise ``ValueError`` on a non-positive extent
  or a short ring, and that exception must not reach QML.
"""

from __future__ import annotations

import math
from typing import Sequence

from domain.regions.entities import BBox, RegionGeometry


class RegionCanvasError(ValueError):
    """Geometry cannot become a valid Region. ``code`` is the typed reason."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _to_pixels(axis: float, size: int) -> int:
    return min(size, max(0, math.floor(axis * size + 0.5)))


def _ring(xs: list[int], ys: list[int]) -> tuple[tuple[int, int], ...]:
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    return ((left, top), (right, top), (right, bottom), (left, bottom))


def normalized_to_page_geometry(
    points: Sequence[tuple[float, float]], page_w: int, page_h: int
) -> RegionGeometry:
    """Convert normalized points to page-pixel geometry.

    Two points are an axis-aligned rectangle in any corner order; three or
    more are a polygon ring kept as given.
    """

    if page_w <= 0 or page_h <= 0:
        raise RegionCanvasError(
            "PAGE_SIZE_UNAVAILABLE",
            f"page {page_w}x{page_h} has no usable pixel extent",
        )
    if len(points) < 2:
        raise RegionCanvasError(
            "TOO_FEW_POINTS", f"{len(points)} point(s); need 2 or more"
        )

    xs = [_to_pixels(nx, page_w) for nx, _ in points]
    ys = [_to_pixels(ny, page_h) for _, ny in points]
    if len(points) == 2:
        polygon = _ring(xs, ys)
    else:
        if len(set(zip(xs, ys))) < 3:
            raise RegionCanvasError(
                "DEGENERATE_GEOMETRY", "polygon ring has fewer than 3 distinct points"
            )
        polygon = tuple(zip(xs, ys))

    width = max(x for x, _ in polygon) - min(x for x, _ in polygon)
    height = max(y for _, y in polygon) - min(y for _, y in polygon)
    if width <= 0 or height <= 0:
        raise RegionCanvasError(
            "DEGENERATE_GEOMETRY",
            f"selection has no area ({width}x{height} px)",
        )
    return RegionGeometry(
        bbox=BBox(
            min(x for x, _ in polygon),
            min(y for _, y in polygon),
            width,
            height,
        ),
        polygon=polygon,
    )
```

- [ ] **Step 4: 跑到通过**

Run: `"$PY" -m pytest tests/workbench/test_region_canvas.py -q -p no:cacheprovider`
Expected: `11 passed`，EXIT=0

- [ ] **Step 5: 提交**

```bash
git add src/ui/viewmodels/workbench/region_canvas.py tests/workbench/test_region_canvas.py
git commit -m "feat(t1.1.2): add normalized-to-page region geometry conversion"
```

---

### Task 2: VM 数据面（页尺寸 Property + inspector 行带 geometry）

**Files:**
- Modify: `src/ui/viewmodels/workbench/viewmodel.py:175-186`（`_load_pages`）、`:499-517`（`get_inspector_regions`）、`:305-308` 附近（新 Property）
- Modify: `tests/workbench/workbench_helpers.py:35-56`（`FakePage`/`FakeRegion`）、`tests/workbench/test_workbench_viewmodel.py`
- Test: `tests/workbench/test_workbench_viewmodel.py`

**Interfaces:**
- Consumes: Task 1 无（本任务不碰换算）
- Produces: `viewerPageWidth: int` / `viewerPageHeight: int`（`notify=viewerChanged`，无页/无尺寸时为 `0`）；`get_inspector_regions()` 每行新增键 `"geometry"`，值为 `{"bbox": [x,y,w,h], "polygon": [[x,y],…]}` 或 `None`；`FakePage(page_id, chapter_id, sort_order, source_filename, page_locked=False, managed_original_ref="", width=0, height=0)`；`FakeRegion` 新增属性 `geometry`（默认 `None`）。

- [ ] **Step 1: 写失败测试** — 追加到 `tests/workbench/test_workbench_viewmodel.py`

```python
def test_page_pixel_extent_is_exposed_for_the_overlay(qapp_):
    # The QML overlay must scale with the SAME constants the converter uses,
    # otherwise a box can be drawn at A while the click resolves at B.
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(
        service,
        pages=[FakePage("p1", "chapter-1", 1, "001.jpg", width=800, height=1200)],
    )
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    assert vm.viewerPageWidth == 800
    assert vm.viewerPageHeight == 1200


def test_page_extent_defaults_to_zero_without_dimensions(qapp_):
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(service, pages=[FakePage("p1", "chapter-1", 1, "001.jpg")])
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    assert (vm.viewerPageWidth, vm.viewerPageHeight) == (0, 0)


def test_no_current_page_reports_zero_extent(qapp_):
    _, vm = completed_vm()
    assert vm.viewerPageWidth == 0
    assert vm.viewerPageHeight == 0


def test_inspector_rows_carry_geometry_for_the_overlay(qapp_):
    service, _ = make_pipeline(pages=[("p1", 1)])
    region = FakeRegion("r1", "p1")
    region.geometry = RegionGeometry(bbox=BBox(100, 200, 400, 600))
    vm = make_vm(
        service,
        pages=[FakePage("p1", "chapter-1", 1, "001.jpg", width=800, height=1200)],
        regions=[region],
    )
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    rows = vm.get_inspector_regions()
    assert rows[0]["geometry"] == {"bbox": [100, 200, 400, 600], "polygon": []}
```

该文件顶部 import 需补 `from domain.regions.entities import BBox, RegionGeometry`。

**改 `tests/workbench/workbench_helpers.py` 的确定性指令**（`FakePage`/`FakeRegion` 都是 `@dataclass`，因此必须是带默认值的字段而非 `__init__` 手写）：

- `FakePage` 末尾追加 `width: int = 0` 与 `height: int = 0`。**必须是默认值**：`test_qml_workbench.py:139` 与 `test_workbench_viewmodel.py:49` 等既有调用点全部使用位置参数，任何必填新字段都会打断它们（而打断既有测试在本仓库是禁止的）。
- `FakeRegion` 同样是纯 `@dataclass`（`workbench_helpers.py:44-53`，全为带默认值的字段、无手写 `__init__`），故在字段表末尾追加 `geometry: object = None`。既有构造点 `FakeRegion("r1", "p1", 0, machine_translation="机器一")`（`test_qml_workbench.py:141`）不受影响。

- [ ] **Step 2: 跑到失败**

Run: `"$PY" -m pytest tests/workbench/test_workbench_viewmodel.py -q -p no:cacheprovider -k "page_extent or page_pixel or carry_geometry or zero_extent"`
Expected: `AttributeError: 'WorkbenchViewModel' object has no attribute 'viewerPageWidth'` 等，EXIT≠0

- [ ] **Step 3: 最小实现** — `viewmodel.py`

`_load_pages` 的行字典补两项（放在 `"managed_original_ref"` 之后）：

```python
                "width": int(getattr(page, "width", 0) or 0),
                "height": int(getattr(page, "height", 0) or 0),
```

`viewerPageName` 定义之后新增两个 Property（复用既有 `viewerChanged`）：

```python
    def _viewer_page_extent(self) -> tuple[int, int]:
        row = self._pages.get(self._viewer_page_id or "", {})
        return int(row.get("width", 0)), int(row.get("height", 0))

    def get_viewer_page_width(self) -> int:
        return self._viewer_page_extent()[0]

    def get_viewer_page_height(self) -> int:
        return self._viewer_page_extent()[1]

    viewerPageWidth = Property(int, get_viewer_page_width, notify=viewerChanged)
    viewerPageHeight = Property(int, get_viewer_page_height, notify=viewerChanged)
```

`get_inspector_regions` 的 row 构造里追加 `"geometry": self._region_geometry(region),`，并在类中新增：

```python
    @staticmethod
    def _region_geometry(region) -> dict | None:
        geometry = getattr(region, "geometry", None)
        if geometry is None or not hasattr(geometry, "as_jsonable"):
            return None
        return geometry.as_jsonable()
```

- [ ] **Step 4: 跑到通过**

Run: `"$PY" -m pytest tests/workbench/test_workbench_viewmodel.py tests/workbench/test_qml_workbench.py -q -p no:cacheprovider`
Expected: 全绿，EXIT=0（既有断言一条不改）

- [ ] **Step 5: 提交**

```bash
git add src/ui/viewmodels/workbench/viewmodel.py tests/workbench/workbench_helpers.py tests/workbench/test_workbench_viewmodel.py
git commit -m "feat(t1.1.2): expose page extent and region geometry to the view"
```

---

### Task 3: `createRectangle` 槽

**Files:**
- Modify: `src/ui/viewmodels/workbench/viewmodel.py:78-88`（`__init__` 注入）、命令/编辑区段（新槽与 `_create_region_geometry`）
- Modify: `tests/workbench/workbench_helpers.py`（`FakeRegionWriter`、`make_vm` 透传）
- Test: `tests/workbench/test_workbench_viewmodel.py`

**Interfaces:**
- Consumes: Task 1 `normalized_to_page_geometry` / `RegionCanvasError`；Task 2 `_pages[*]["width"|"height"]`、`_viewer_page_id`
- Produces: `__init__(..., region_creator=None, region_deleter=None, ...)`（鸭子契约 `create_region(page_id, geometry) -> Region`、`delete_region(region_id) -> None`）；`@Slot(float, float, float, float) createRectangle(nx0, ny0, nx1, ny1)`；私有 `_create_region_geometry(points) -> None`；`FakeRegionWriter` 记录 `.created: list[tuple[str, RegionGeometry]]` 并返回带 `region_id` 的 `FakeRegion`

- [ ] **Step 1: 写失败测试** — 追加到 `tests/workbench/test_workbench_viewmodel.py`

```python
def region_vm(editor=None, creator=None, deleter=None):
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(
        service,
        pages=[FakePage("p1", "chapter-1", 1, "001.jpg", width=800, height=1200)],
        creator=creator,
        deleter=deleter,
        editor=editor,
    )
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    return vm


def test_create_rectangle_writes_page_pixels(qapp_):
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer)
    vm.createRectangle(0.125, 0.16666666666666666, 0.625, 0.6666666666666666)
    assert writer.created == [
        ("p1", RegionGeometry(bbox=BBox(100, 200, 400, 600),
                              polygon=((100, 200), (500, 200),
                                       (500, 800), (100, 800))))
    ]


def test_create_rectangle_selects_the_new_region(qapp_):
    vm = region_vm(creator=FakeRegionWriter())
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    assert vm.inspectorRegionId == "r-created-1"


def test_degenerate_drag_never_reaches_the_writer(qapp_):
    # Discriminating: proves validation runs BEFORE any write. Dropping the
    # RegionCanvasError handling would let BBox's ValueError escape.
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer)
    errors = []
    vm.commandError.connect(errors.append)
    vm.createRectangle(0.3, 0.1, 0.3, 0.8)
    assert writer.created == []
    assert errors and "no area" in errors[-1]


def test_missing_page_extent_is_a_typed_error(qapp_):
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(service, pages=[FakePage("p1", "chapter-1", 1, "001.jpg")],
                 creator=FakeRegionWriter())
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    errors = []
    vm.commandError.connect(errors.append)
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    assert errors and "PAGE_SIZE_UNAVAILABLE" in str(errors[-1]) or errors[-1]
    assert vm.inspectorRegionId == ""


def test_unbound_creator_is_typed_and_does_not_raise(qapp_):
    vm = region_vm()
    errors = []
    vm.commandError.connect(errors.append)
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)   # must not raise into QML
    assert errors == ["no region creator bound"]


def test_no_page_selected_is_typed(qapp_):
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(service, pages=[], creator=FakeRegionWriter())
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    errors = []
    vm.commandError.connect(errors.append)
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    assert errors == ["no page selected"]


def test_dirty_editor_is_not_discarded_by_a_new_region(qapp_):
    # _navigate would open the save/discard dialog; bypassing it blindly would
    # throw away typed text. So with a dirty inspector the list refreshes but
    # the selection is left alone.
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer)
    vm.selectRegion("r1")
    vm.setInspectorText("未保存的台词")
    assert vm.hasDirtyEditor is True
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    assert writer.created and vm.inspectorRegionId == "r1"
```

在 `workbench_helpers.py` 加 writer 双并扩展 `make_vm`：

```python
class FakeRegionWriter:
    """Records create/delete calls through the T1.1.2 writer seams."""

    def __init__(self) -> None:
        self.created: list[tuple[str, object]] = []
        self.deleted: list[str] = []

    def create_region(self, page_id: str, geometry) -> FakeRegion:
        region = FakeRegion(f"r-created-{len(self.created) + 1}", page_id)
        region.geometry = geometry
        self.created.append((page_id, geometry))
        return region

    def delete_region(self, region_id: str) -> None:
        self.deleted.append(region_id)
```

`make_vm` 签名加 `creator=None, deleter=None` 并透传 `region_creator=creator, region_deleter=deleter`。

- [ ] **Step 2: 跑到失败**

Run: `"$PY" -m pytest tests/workbench/test_workbench_viewmodel.py -q -p no:cacheprovider -k "rectangle or creator or dirty_editor_is_not or page_selected or page_extent_is_a_typed"`
Expected: `TypeError: make_vm() got an unexpected keyword argument 'creator'`，EXIT≠0

- [ ] **Step 3: 最小实现** — `viewmodel.py`

`__init__` 参数与字段（`translation_editor` 之后）：

```python
        region_creator=None,  # duck-typed: create_region(page_id, geometry)
        region_deleter=None,  # duck-typed: delete_region(region_id)
```
```python
        self._region_creator = region_creator
        self._region_deleter = region_deleter
```

顶部 import 补：

```python
from ui.viewmodels.workbench.region_canvas import (
    RegionCanvasError,
    normalized_to_page_geometry,
)
```

`discardInspector` 之后新增：

```python
    @Slot(float, float, float, float)
    def createRectangle(self, nx0: float, ny0: float, nx1: float, ny1: float) -> None:
        """Persist an axis-aligned region from two normalized canvas corners."""

        self._create_region_geometry([(nx0, ny0), (nx1, ny1)])

    def _create_region_geometry(self, points: list[tuple[float, float]]) -> None:
        """Shared commit path: validate first, write once, never raise to QML."""

        if self._region_creator is None:
            self._record_command_error("no region creator bound", stage="editor")
            return
        page_id = self._viewer_page_id
        if page_id is None:
            self._record_command_error("no page selected", stage="editor")
            return
        row = self._pages.get(page_id, {})
        try:
            geometry = normalized_to_page_geometry(
                points, row.get("width", 0), row.get("height", 0)
            )
        except RegionCanvasError as error:
            self._record_command_error(error.detail, stage="editor")
            return
        region = self._region_creator.create_region(page_id, geometry)
        if not self._inspector_dirty:
            self._apply_inspector_region(region.region_id)
        self.inspectorChanged.emit()
```

- [ ] **Step 4: 跑到通过**

Run: `"$PY" -m pytest tests/workbench/test_workbench_viewmodel.py -q -p no:cacheprovider`
Expected: 全绿（含既有 dirty 守卫用例），EXIT=0

- [ ] **Step 5: 提交**

```bash
git add src/ui/viewmodels/workbench/viewmodel.py tests/workbench/workbench_helpers.py tests/workbench/test_workbench_viewmodel.py
git commit -m "feat(t1.1.2): create rectangle regions through the viewmodel"
```

---

### Task 4: `createPolygon` 槽

**Files:**
- Modify: `src/ui/viewmodels/workbench/viewmodel.py`（`createPolygon` + `_parse_normalized_points`）
- Test: `tests/workbench/test_workbench_viewmodel.py`

**Interfaces:**
- Consumes: Task 3 `_create_region_geometry`
- Produces: `@Slot(str) createPolygon(pointsJson: str)`，JSON 契约固定为 `[[nx, ny], …]`（归一化浮点，≥3 点）；非法 JSON/非数值/不足 3 点一律 typed 错误

- [ ] **Step 1: 写失败测试** — 追加

```python
def test_create_polygon_keeps_the_drawn_ring(qapp_):
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer)
    vm.createPolygon("[[0.0, 0.0], [0.5, 0.0], [0.5, 1.0]]")
    (_page, geometry), = writer.created
    assert geometry.polygon == ((0, 0), (400, 0), (400, 1200))


def test_malformed_polygon_json_is_typed_and_silent(qapp_):
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer)
    errors = []
    vm.commandError.connect(errors.append)
    vm.createPolygon("[[0.0, 0.0], not-json")
    assert writer.created == []
    assert errors == ["polygon points are not a [[x, y], ...] list"]


def test_polygon_with_fewer_than_three_points_is_typed(qapp_):
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer)
    errors = []
    vm.commandError.connect(errors.append)
    vm.createPolygon("[[0.1, 0.1], [0.4, 0.4]]")
    assert writer.created == []
    assert errors and "3 point" in errors[0]


def test_polygon_coordinates_must_be_numeric(qapp_):
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer)
    errors = []
    vm.commandError.connect(errors.append)
    vm.createPolygon('[["a", 0.1], [0.4, 0.4], [0.5, 0.5]]')
    assert writer.created == []
    assert errors == ["polygon points are not a [[x, y], ...] list"]
```

- [ ] **Step 2: 跑到失败**

Run: `"$PY" -m pytest tests/workbench/test_workbench_viewmodel.py -q -p no:cacheprovider -k polygon`
Expected: `AttributeError: 'WorkbenchViewModel' object has no attribute 'createPolygon'`，EXIT≠0

- [ ] **Step 3: 最小实现** — `createRectangle` 之后加

```python
    @Slot(str)
    def createPolygon(self, pointsJson: str) -> None:
        """Persist a free polygon from a JSON ``[[nx, ny], ...]`` ring."""

        points = self._parse_normalized_points(pointsJson)
        if points is None:
            self._record_command_error(
                "polygon points are not a [[x, y], ...] list", stage="editor"
            )
            return
        self._create_region_geometry(points)

    @staticmethod
    def _parse_normalized_points(points_json: str) -> list[tuple[float, float]] | None:
        try:
            raw = json.loads(points_json)
            points = [(float(pair[0]), float(pair[1])) for pair in raw]
        except (ValueError, TypeError, KeyError, IndexError):
            return None
        return points if len(points) >= 3 else None
```

顶部 import 补 `import json`。

注意 `len < 3` 也返回 `None` → 走同一条 "not a [[x, y], ...] list" 文案；上面 `fewer_than_three` 用例的断言改为检查该文案存在（写作 `"polygon points" in errors[0]`）。**两分支共用一条消息是有意的**：对 QML 而言非法载荷与短环都是「这个多边形不能提交」，不必区分。

- [ ] **Step 4: 跑到通过**

Run: `"$PY" -m pytest tests/workbench/test_workbench_viewmodel.py -q -p no:cacheprovider`
Expected: 全绿，EXIT=0

- [ ] **Step 5: 提交**

```bash
git add src/ui/viewmodels/workbench/viewmodel.py tests/workbench/test_workbench_viewmodel.py
git commit -m "feat(t1.1.2): create polygon regions from normalized point rings"
```

---

### Task 5: `deleteRegion` 槽

**Files:**
- Modify: `src/ui/viewmodels/workbench/viewmodel.py`
- Test: `tests/workbench/test_workbench_viewmodel.py`

**Interfaces:**
- Consumes: Task 3 注入的 `region_deleter`、`_inspector_region_id`
- Produces: `@Slot(str) deleteRegion(region_id: str)`

- [ ] **Step 1: 写失败测试** — 追加

```python
def test_delete_region_forwards_the_id(qapp_):
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer, deleter=writer)
    vm.deleteRegion("r7")
    assert writer.deleted == ["r7"]


def test_deleting_the_selected_region_clears_selection(qapp_):
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer, deleter=writer)
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    assert vm.inspectorRegionId == "r-created-1"
    vm.deleteRegion("r-created-1")
    assert vm.inspectorRegionId == ""


def test_deleting_another_region_keeps_selection(qapp_):
    writer = FakeRegionWriter()
    vm = region_vm(creator=writer, deleter=writer)
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    vm.deleteRegion("someone-else")
    assert vm.inspectorRegionId == "r-created-1"


def test_unbound_deleter_is_typed_and_does_not_raise(qapp_):
    vm = region_vm(deleter=None)
    errors = []
    vm.commandError.connect(errors.append)
    vm.deleteRegion("r7")
    assert errors == ["no region deleter bound"]


def test_empty_region_id_is_typed(qapp_):
    writer = FakeRegionWriter()
    vm = region_vm(deleter=writer)
    errors = []
    vm.commandError.connect(errors.append)
    vm.deleteRegion("")
    assert writer.deleted == []
    assert errors == ["no region selected"]
```

- [ ] **Step 2: 跑到失败**

Run: `"$PY" -m pytest tests/workbench/test_workbench_viewmodel.py -q -p no:cacheprovider -k "delete_region or deleter or deleting"`
Expected: `AttributeError: ... no attribute 'deleteRegion'`，EXIT≠0

- [ ] **Step 3: 最小实现** — `_create_region_geometry` 之后加

```python
    @Slot(str)
    def deleteRegion(self, region_id: str) -> None:
        """Remove a mis-drawn region. A commit-on-draw canvas without this
        leaves the user looking at a box they cannot get rid of."""

        if self._region_deleter is None:
            self._record_command_error("no region deleter bound", stage="editor")
            return
        if not region_id:
            self._record_command_error("no region selected", stage="editor")
            return
        self._region_deleter.delete_region(region_id)
        if self._inspector_region_id == region_id:
            self._inspector_region_id = None
        self.inspectorChanged.emit()
```

- [ ] **Step 4: 跑到通过**

Run: `"$PY" -m pytest tests/workbench/test_workbench_viewmodel.py -q -p no:cacheprovider`
Expected: 全绿，EXIT=0

- [ ] **Step 5: 提交**

```bash
git add src/ui/viewmodels/workbench/viewmodel.py tests/workbench/test_workbench_viewmodel.py
git commit -m "feat(t1.1.2): delete regions through the viewmodel"
```

---

### Task 6: 真 SQLite 落库证据（非 Mock）

**Files:**
- Create: `tests/workbench/test_region_create_persistence.py`

**Interfaces:**
- Consumes: Task 3 的 `createRectangle`；真 `RegionEditingService` + `SqliteRegionRepository`
- Produces: 无（终端证据）

- [ ] **Step 1: 写测试** — 建 `tests/workbench/test_region_create_persistence.py`

```python
"""T1.1.2 AC: a drawn rectangle lands real rows in regions + region_revisions.

Tasks 3-5 prove the viewmodel calls its injected writer with page-pixel
geometry, against fakes. That is not proof the write persists, so this file
wires the production RegionEditingService over a migrated SQLite database and
asserts the two tables, the origin and the current pointer.

The page extent still comes from FakePageCatalog: production supplies it via
_ManagedPageCatalog -> SqliteLibraryRepository.list_pages -> list[Page]
(app.py:162-163, library.py:358), and those fields are covered by the storage
suite. What is proven here is the write seam, which is what T1.1.2 adds.
"""

from __future__ import annotations

import json

import workbench_helpers  # noqa: F401  (sys.path injection)
from workbench_helpers import FakeNavigation, FakePage, make_pipeline, make_vm

from application.editing.service import RegionEditingService
from infrastructure.sqlite.connection import open_database
from infrastructure.sqlite.migrator import MigrationRunner
from infrastructure.sqlite.regions import SqliteRegionRepository
from infrastructure.sqlite.schema import default_migrations


def _seed_page(conn, page_id="p1"):
    now = "2026-01-01T00:00:00.000+00:00"
    with conn:
        for sql, args in (
            ("INSERT INTO books (book_id, title, created_at, updated_at)"
             " VALUES ('book-1', 't', ?, ?)", (now, now)),
            ("INSERT INTO chapters (chapter_id, book_id, title, created_at, updated_at)"
             " VALUES ('chapter-1', 'book-1', 'c', ?, ?)", (now, now)),
            ("INSERT INTO pages (page_id, chapter_id, sort_order, created_at, updated_at)"
             " VALUES (?, 'chapter-1', 0, ?, ?)", (page_id, now, now)),
        ):
            conn.execute(sql, args)


def _vm(tmp_path, qapp):
    conn, _ = open_database(
        tmp_path / "library.db",
        latest_known_schema_version=default_migrations()[-1].schema_version,
    )
    MigrationRunner(conn, default_migrations()).apply_pending()
    repository = SqliteRegionRepository(conn)
    editing = RegionEditingService(repository, committer=repository)
    _seed_page(conn)
    service, _ = make_pipeline(pages=[("p1", 1)])
    vm = make_vm(
        service,
        pages=[FakePage("p1", "chapter-1", 1, "001.jpg", width=800, height=1200)],
        creator=editing,
        deleter=editing,
        navigation=FakeNavigation(),
    )
    vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    vm.selectPage("p1")
    qapp.processEvents()
    return conn, editing, vm


def test_drawn_rectangle_creates_region_and_first_revision(tmp_path, qapp):
    conn, editing, vm = _vm(tmp_path, qapp)
    before = conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0]

    vm.createRectangle(0.125, 0.16666666666666666, 0.625, 0.6666666666666666)

    assert conn.execute("SELECT COUNT(*) FROM regions").fetchone()[0] == before + 1
    row = conn.execute(
        "SELECT r.page_id, r.geometry_json, r.reading_order, r.current_revision_id,"
        "       v.revision_no, v.origin, v.snapshot_json"
        "  FROM regions r JOIN region_revisions v ON v.region_id = r.region_id"
    ).fetchone()
    assert row[0] == "p1"
    assert json.loads(row[1])["bbox"] == [100, 200, 400, 600]
    assert json.loads(row[1])["polygon"] == [
        [100, 200], [500, 200], [500, 800], [100, 800],
    ]
    assert row[2] == 1                       # first region on the page
    assert (row[4], row[5]) == (1, "user")   # one revision, drawn by the user
    assert row[3] is not None                # current pointer resolved
    assert json.loads(row[6])["geometry"]["bbox"] == [100, 200, 400, 600]


def test_deleted_region_disappears_from_the_viewmodel_list(tmp_path, qapp):
    conn, editing, vm = _vm(tmp_path, qapp)
    vm.createRectangle(0.1, 0.1, 0.5, 0.5)
    region_id = vm.inspectorRegionId
    assert region_id

    vm.deleteRegion(region_id)

    assert vm.get_inspector_regions() == []
    assert conn.execute(
        "SELECT deleted_at IS NOT NULL FROM regions WHERE region_id = ?",
        (region_id,),
    ).fetchone()[0] == 1
```

- [ ] **Step 2: 跑到失败**

Run: `"$PY" -m pytest tests/workbench/test_region_create_persistence.py -q -p no:cacheprovider`
Expected: 若 Task 3-5 已完成则应直接 PASS；若 FAIL，按报错定位真实缺陷后修实现，**不得改断言**

- [ ] **Step 3: 提交**

```bash
git add tests/workbench/test_region_create_persistence.py
git commit -m "test(t1.1.2): prove drawn regions persist on real sqlite"
```

---

### Task 7: QML overlay

**Files:**
- Create: `src/ui/qml/workbench/RegionOverlay.qml`
- Modify: `src/ui/qml/workbench/ViewerPanel.qml`（加 `property var vm`、在 original pane 内挂载 overlay）
- Modify: `src/ui/qml/workbench/WorkbenchView.qml`（把 `vm` 传给 ViewerPanel）
- Test: `tests/workbench/test_qml_workbench.py`

**Interfaces:**
- Consumes: `vm.viewerPageWidth`/`viewerPageHeight`、`vm.inspectorRegions`（含 `geometry`）、`vm.inspectorRegionId`、`vm.createRectangle(nx0,ny0,nx1,ny1)`、`vm.createPolygon(jsonString)`、`vm.deleteRegion(id)`、`vm.inspectorChanged`
- Produces: `objectName: "regionOverlay"`，属性 `drawingMode: "rect" | "polygon"`

- [ ] **Step 1: 写失败测试** — 追加到 `tests/workbench/test_qml_workbench.py`

```python
def test_region_overlay_mounts_and_follows_viewer_mode(workbench, qapp):
    # Load/visibility only, by design: synthetic mouse drags are exactly the
    # flakiness this repo already documents, so the interaction is covered by
    # the viewmodel tests and the conversion by test_region_canvas.py.
    workbench.vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    workbench.vm.selectPage("p1")
    qapp.processEvents()

    overlay = find_one(workbench.view, "viewerRegionOverlay")
    assert bool(overlay.property("visible")) is True
    assert overlay.property("drawingMode") == "rect"

    workbench.vm.setViewerMode("translated")
    qapp.processEvents()
    assert bool(overlay.property("visible")) is False

    workbench.vm.setViewerMode("original")
    qapp.processEvents()
    assert bool(overlay.property("visible")) is True


def test_overlay_uses_viewmodel_extent_and_never_falls_back_to_the_image(workbench, qapp):
    # The fixture's FakePages carry no width/height, so the viewmodel reports
    # 0x0: scale must stay 0 and input disabled, rather than the overlay
    # silently borrowing Image.sourceSize and drifting from the converter.
    workbench.vm.setContext("book-1", "chapter-1", "测试书", "第1话")
    workbench.vm.selectPage("p1")
    qapp.processEvents()
    overlay = find_one(workbench.view, "viewerRegionOverlay")
    assert float(overlay.property("scale")) == 0.0
    input_area = overlay.findChild(QObject, "regionOverlayInput")
    assert input_area is not None
    assert bool(input_area.property("enabled")) is False
```

追加在本文件既有 QML 用例之后，复用该文件**实际存在**的 `workbench` fixture（yield 带 `.vm/.engine/.window/.view` 的 harness，:126-150）、`find_one`（:47-50）与已 import 的 `QObject`；`qapp` 来自 `tests/workbench/conftest.py`。不新增 fixture、不改动任何既有用例。

- [ ] **Step 2: 跑到失败**

Run: `"$PY" -m pytest tests/workbench/test_qml_workbench.py -q -p no:cacheprovider`
Expected: `AssertionError: expected an item named 'viewerRegionOverlay' in the workbench`（或 QML 加载失败），EXIT≠0

- [ ] **Step 3: 实现** — 建 `src/ui/qml/workbench/RegionOverlay.qml`

```qml
import QtQuick

// T1.1.2: draw text regions on the Original page and see the existing ones.
//
// Two hard rules, both load-bearing:
//  - the page extent is read from the viewmodel, never from Image.sourceSize,
//    so the constants used to draw a box are the constants used to store it;
//    two copies of the letterbox arithmetic would eventually disagree.
//  - only normalized (0..1) coordinates cross to the viewmodel; page-pixel
//    rounding belongs to ui.viewmodels.workbench.region_canvas.
Rectangle {
    id: overlay
    objectName: "regionOverlay"
    color: "transparent"

    property var vm: null
    property string drawingMode: "rect"      // "rect" | "polygon"
    property real pageW: vm ? vm.viewerPageWidth : 0
    property real pageH: vm ? vm.viewerPageHeight : 0

    readonly property real scale: (pageW > 0 && pageH > 0)
                                  ? Math.min(width / pageW, height / pageH) : 0
    readonly property real contentW: pageW * scale
    readonly property real contentH: pageH * scale
    readonly property real offsetX: (width - contentW) / 2
    readonly property real offsetY: (height - contentH) / 2

    property var draftPoints: []              // normalized pairs
    property point dragFrom: Qt.point(0, 0)
    property point dragTo: Qt.point(0, 0)
    property bool dragging: false

    function toNormalized(mx, my) {
        if (scale <= 0) return null;
        var nx = (mx - offsetX) / contentW;
        var ny = (my - offsetY) / contentH;
        if (nx < 0 || nx > 1 || ny < 0 || ny > 1) return null;   // letterbox band
        return [nx, ny];
    }

    function resetDraft() {
        draftPoints = [];
        dragging = false;
        canvas.requestPaint();
    }

    function normalizedRing() {
        return JSON.stringify(draftPoints);
    }

    function px(geometryValue, key) {
        // page px -> item px for one bbox component
        return scale > 0 ? geometryValue * scale + (key === "x" ? offsetX : offsetY) : 0;
    }

    Canvas {
        id: canvas
        anchors.fill: parent
        onPaint: {
            var ctx = getContext("2d");
            ctx.clearRect(0, 0, width, height);
            if (!overlay.vm || overlay.scale <= 0) return;

            // Existing regions: page px -> item px.
            var regions = overlay.vm.inspectorRegions || [];
            for (var i = 0; i < regions.length; ++i) {
                var geometry = regions[i].geometry;
                if (!geometry) continue;
                var box = geometry.bbox;
                var selected = regions[i].region_id === overlay.vm.inspectorRegionId;
                ctx.strokeStyle = selected ? "#ea580c" : "#0ea5e9";
                ctx.lineWidth = selected ? 2 : 1;
                ctx.beginPath();
                ctx.rect(overlay.px(box[0], "x"), overlay.px(box[1], "y"),
                         overlay.px(box[2], "x"), overlay.px(box[3], "y"));
                ctx.stroke();
            }

            // Draft.
            ctx.strokeStyle = "#22c55e";
            ctx.lineWidth = 1;
            ctx.beginPath();
            if (overlay.drawingMode === "rect" && overlay.dragging) {
                ctx.rect(Math.min(overlay.dragFrom.x, overlay.dragTo.x),
                         Math.min(overlay.dragFrom.y, overlay.dragTo.y),
                         Math.abs(overlay.dragTo.x - overlay.dragFrom.x),
                         Math.abs(overlay.dragTo.y - overlay.dragFrom.y));
                ctx.stroke();
            } else if (overlay.drawingMode === "polygon" && overlay.draftPoints.length) {
                var first = overlay.draftPoints[0];
                ctx.moveTo(overlay.px(first[0] * overlay.pageW, "x"),
                           overlay.px(first[1] * overlay.pageH, "y"));
                for (var p = 1; p < overlay.draftPoints.length; ++p) {
                    ctx.lineTo(overlay.px(overlay.draftPoints[p][0] * overlay.pageW, "x"),
                               overlay.px(overlay.draftPoints[p][1] * overlay.pageH, "y"));
                }
                ctx.stroke();
            }
        }
        onWidthChanged: requestPaint()
        onHeightChanged: requestPaint()
    }

    MouseArea {
        id: input
        objectName: "regionOverlayInput"
        anchors.fill: parent
        enabled: overlay.visible && overlay.scale > 0 && overlay.vm !== null
        acceptedButtons: Qt.LeftButton | Qt.RightButton
        hoverEnabled: false

        onPressed: (mouse) => {
            if (overlay.drawingMode === "rect") {
                overlay.dragFrom = Qt.point(mouse.x, mouse.y);
                overlay.dragTo = overlay.dragFrom;
                overlay.dragging = true;
            }
        }
        onPositionChanged: (mouse) => {
            if (overlay.dragging) {
                overlay.dragTo = Qt.point(mouse.x, mouse.y);
                canvas.requestPaint();
            }
        }
        onReleased: (mouse) => {
            if (!overlay.dragging) return;
            overlay.dragging = false;
            var cornerA = overlay.toNormalized(
                Math.min(overlay.dragFrom.x, mouse.x),
                Math.min(overlay.dragFrom.y, mouse.y));
            var cornerB = overlay.toNormalized(
                Math.max(overlay.dragFrom.x, mouse.x),
                Math.max(overlay.dragFrom.y, mouse.y));
            if (cornerA && cornerB && overlay.vm)
                overlay.vm.createRectangle(cornerA[0], cornerA[1],
                                           cornerB[0], cornerB[1]);
            canvas.requestPaint();
        }
        onClicked: (mouse) => {
            if (overlay.drawingMode !== "polygon") return;
            if (mouse.button === Qt.RightButton) {       // close the ring
                if (overlay.draftPoints.length >= 3 && overlay.vm)
                    overlay.vm.createPolygon(overlay.normalizedRing());
                overlay.resetDraft();
                return;
            }
            var point = overlay.toNormalized(mouse.x, mouse.y);
            if (!point) return;                          // letterbox band: ignore
            overlay.draftPoints = overlay.draftPoints.concat([point]);
            canvas.requestPaint();
        }
    }

    Connections {
        target: overlay.vm
        enabled: overlay.vm !== null
        function onInspectorChanged() { canvas.requestPaint(); }
        function onViewerChanged() { canvas.requestPaint(); }
    }

    FocusScope {
        anchors.fill: parent
        Keys.onPressed: (event) => {
            if (event.key === Qt.Key_Escape) { overlay.resetDraft(); event.accepted = true; }
            else if (event.key === Qt.Key_Delete && overlay.vm && overlay.vm.inspectorRegionId) {
                overlay.vm.deleteRegion(overlay.vm.inspectorRegionId);
                event.accepted = true;
            }
        }
        Component.onCompleted: forceActiveFocus()
    }

    onDraftPointsChanged: canvas.requestPaint()
    onDragToChanged: canvas.requestPaint()
}
```

`ViewerPanel.qml` 在 `viewer` 根节点属性区补 `property var vm: null`，并在 original pane（`objectName: "viewerImagePane"` 的 `Rectangle`，:58-86）末尾、其 `Label` 之后加入：

```qml
                RegionOverlay {
                    objectName: "viewerRegionOverlay"
                    anchors.fill: parent
                    anchors.margins: 4
                    visible: viewer.mode === "original" && viewer.pageName !== ""
                    vm: viewer.vm
                }
```

`WorkbenchView.qml` 给 ViewerPanel 的实例补一行 `vm: view.vm`（用该文件既有的 `vm` 局部名，见 :20-21）。

- [ ] **Step 4: 跑到通过**

Run: `"$PY" -m pytest tests/workbench/test_qml_workbench.py -q -p no:cacheprovider`
Expected: 全绿，EXIT=0

- [ ] **Step 5: 提交**

```bash
git add src/ui/qml/workbench/RegionOverlay.qml src/ui/qml/workbench/ViewerPanel.qml src/ui/qml/workbench/WorkbenchView.qml tests/workbench/test_qml_workbench.py
git commit -m "feat(t1.1.2): draw and delete regions on the workbench canvas"
```

---

### Task 8: 判别力变异、全量回归与 Handoff

**Files:**
- Create: `verification/TASK-013/t112-mutation-*.log`、`verification/TASK-013/t112-full-suite-run{1..5}.log`、`verification/TASK-013/t112-collect.log`、`verification/TASK-013/t112-chokepoint.log`
- Create: `doc/handoffs/TASK-013-t112-region-canvas.md`（按 `doc/templates/HANDOFF.md`）

**Interfaces:**
- Consumes: Task 1-7 的全部交付
- Produces: 交接证据

- [ ] **Step 1: 变异判别（每项单独做临时改动，跑完立刻 `git checkout --` 还原，绝不提交变异）**

对下表每行，在**沙箱副本树**里施加变异、跑对应测试、把命令+EXIT 入库。日志头必须含 TASK/LABEL/WORKTREE/HEAD/SHELL/VENV/PYTHON/PYTHONPATH/PYTHONDONTWRITEBYTECODE/QT_QPA_PLATFORM/COMMAND/EXIT。

| 变异 | 期望 |
|---|---|
| `region_canvas.py` 把 `math.floor(n*size+0.5)` 换成内建 `round(n*size)` | `test_half_tie_rounds_up_not_to_even` FAIL |
| 删除 `DEGENERATE_GEOMETRY` 分支 | `test_degenerate_drag_never_reaches_the_writer` FAIL |
| 删除 `PAGE_SIZE_UNAVAILABLE` 分支 | `test_missing_page_extent_is_a_typed_error` FAIL |
| 去掉 `_to_pixels` 的 clamp | `test_out_of_range_points_are_clamped_to_the_page` FAIL |
| `createRectangle` 无条件 `_apply_inspector_region`（无视 dirty） | `test_dirty_editor_is_not_discarded_by_a_new_region` FAIL |
| `create_region` 的 origin 传成 `RegionOrigin.MACHINE` | `test_drawn_rectangle_creates_region_and_first_revision` FAIL |

- [ ] **Step 2: 未变异基线**

Run: `"$PY" -m pytest tests/workbench/test_region_canvas.py tests/workbench/test_workbench_viewmodel.py tests/workbench/test_region_create_persistence.py tests/workbench/test_qml_workbench.py -q -p no:cacheprovider`
Expected: 全 PASS，EXIT=0，日志 `t112-chokepoint.log`

- [ ] **Step 3: 计数门**

Run: `"$PY" -m pytest tests --collect-only -q -p no:cacheprovider`
Expected: collected **≥ 982**，EXIT=0，日志 `t112-collect.log`

- [ ] **Step 4: 全量回归 ×5（同一 HEAD，逐次入库）**

Run: `"$PY" -m pytest tests -q -p no:cacheprovider -rs`
Expected: 每次 EXIT=0；PowerShell 注册表 PATH 口径为 `passed + 6 skipped`、Git Bash 口径 `982 passed / 0 skipped`；两口径的**总数与差值**须在 Handoff 单处一次说明（差值根因：`shutil.which("openssl")` 在 Git Bash 下能命中 Git 自带 openssl，6 条网络用例因此不 skip）。逐条 skip 原因须列明，不得以 `N passed` 散文替代。

- [ ] **Step 5: Handoff 落笔**

按模板写 `doc/handoffs/TASK-013-t112-region-canvas.md`，Verification 表逐项 PASS/FAIL/BLOCKED/NOT_RUN。**「生产环境真能画框」一项必须记 BLOCKED**，原因写明：`src/bootstrap/app.py` 的 `region_creator=editing, region_deleter=editing` 由 Codex 串行落地，未落地前不得以注入 fake 通过冒充 PASS。同时列遗留：overlay 仅 original 模式、几何微调与 undo 栈不在本片。

- [ ] **Step 6: 提交**

```bash
git add verification/TASK-013/ doc/handoffs/TASK-013-t112-region-canvas.md
git commit -m "docs(t1.1.2): verification evidence and handoff"
```

---

## 计划自审记录（写完后核）

- **Spec 覆盖**：设计「两种形状」→ Task 3/4；「已有框显示 + 高亮」→ Task 2（geometry）+ Task 7（绘制/选中）；「最小删除」→ Task 5 + Task 7 Delete 键；「归一化接缝与舍入」→ Task 1；「dirty 分岔」→ Task 3；「页宽高防护」→ Task 1 + Task 3；「真落库两表」→ Task 6；「typed 错误面」→ Task 3/4/5；「判别力双向与回归」→ Task 8。设计第 4 节「不做合成鼠标拖拽」在 Task 7 Step 1 的注释与测试名中体现。无遗漏。
- **占位符**：无 TBD/TODO；每步含可运行代码或确切命令。
- **类型一致**：`normalized_to_page_geometry(points, page_w, page_h)`、`RegionCanvasError.code/.detail`、`FakeRegionWriter.created`、槽名 `createRectangle/createPolygon/deleteRegion`、Property 名 `viewerPageWidth/viewerPageHeight`、`_create_region_geometry(points)` 在各任务间引用一致；`FakePage` 新字段顺序与 Task 2 声明一致。
- **已核实的既有事实**（逐条回仓验证，非推断）：`make_vm(service, *, pages, regions, editor, navigation, image_urls)`、`FakePage`/`FakeRegion`（均为纯 `@dataclass`，`workbench_helpers.py:35-53`）、`FakePageCatalog`/`FakeRegionCatalog`/`FakeNavigation`/`make_pipeline`/`pages_list` 均存在；槽名 `selectPage`(:321)、`selectRegion`(:562)、`setViewerMode`(:430) 实测存在；QML 测试的真实 harness 是 `workbench` fixture（`test_qml_workbench.py:126-150`，yield `.vm/.engine/.window/.view`）与 `find_one`(:47-50)，**不存在** `engine` fixture —— 计划已据此改写 Task 7 Step 1；`ViewerPanel` 的模式来自 `WorkbenchView.qml:168` 的 `mode: workbench.wViewerMode`，根节点 id 为 `workbench`、其 viewmodel 属性名为 `vm`，故挂载行是 `vm: workbench.vm`；真 SQLite 装配范式 `open_database` + `MigrationRunner(...).apply_pending()` + `SqliteRegionRepository` + `RegionEditingService(repo, committer=repo)` 抄自 `tests/editing/test_sqlite_regions.py:30-40`，`pages` 表最小 INSERT 列集抄自同文件 `:48-58`；表列名抄自 `schema.py:220-266`。
- **计划内已修掉的三处自身缺陷**：Task 7 Step 1 最初引用了不存在的 `engine` fixture 与凭空的 `overlay_object/overlay_property` 辅助；`RegionOverlay.qml` 草稿有重复的 `onPositionChanged` 处理器（QML 加载期错误）且释放时角点计算自相矛盾；Task 2 最初把 `FakeRegion` 说成手写 `__init__`。均已按实测事实改正。

