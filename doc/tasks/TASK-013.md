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
- `Page` 实体带 `width`/`height` 且 `__post_init__` 保证为正（`src/domain/pages/entities.py:26-27,41-42`）；`VM._load_pages`（:179-186）已遍历这些对象，只是未把宽高放进 row dict。
- `create_region`（`src/application/editing/service.py:247`）的 `origin` **默认即 `RegionOrigin.USER`**，`reading_order=None` 自动取 max+1，内部为「first revision + pointer 一次原子提交」⇒ AC「落 `regions` + `region_revisions` 两表」由 service 保证、**本 Task 不需新增实现**，但仍必须给出真落库证据（见测试策略），二者不矛盾。
- 几何为**整数且带构造期校验**：`BBox.__post_init__` 对 `width/height<=0` 抛 `ValueError`；`RegionGeometry.__post_init__` 对 polygon `<3` 点抛 `ValueError`。⇒ 退化输入必须在写入前拦截，否则异常会冒进 QML。

## 范围（含两处超出计划 :104 字面的增加，均由 Owner 明确要求）

1. 矩形与多边形**两种输入都做**（忠于 :104）。
2. overlay **同时绘制本页已有 Region 的框**并高亮当前选中项。超出 :104 字面（其只写 "input"），理由：不显示已有框即盲画，气泡会叠在一起。
3. 本片含**最小删除入口**（Delete 键或 Inspector 删除动作）。超出 :104 字面，理由：绘制即时落库 + 已有框可见 ⇒ 不补删除就是「看得见删不掉」的不自洽切片。

Reviewer 判 Scope/spec 时**以本节为准**，不以 `REBASELINE_PLAN.md` :104 字面为准；:104 的 AC（:108）仍为规格来源。

## 架构与接缝

唯一真正的分层问题是「视口坐标 ↔ 页面整数像素」换算放在哪。视口尺寸只有 QML 知道，而已有框的回显也必须由 QML 计算内容矩形，若 Python 再反演一次同一段 letterbox 算术就会有两份会漂移的实现。**接缝取归一化坐标 0..1**：QML 独占 item↔归一化（视图关注点），VM 独占归一化↔页面像素（模型关注点），两侧各只有一份换算。

- **新增 `src/ui/viewmodels/workbench/region_canvas.py`**：不 import PySide6 的纯函数模块。`normalized_to_page_geometry(points, page_w, page_h) -> RegionGeometry` 返回**真的 domain 值对象**（页面整数像素的 `BBox` + `polygon`），内含取整、clamp、退化判定。理由：`RegionEditingService.create_region` 要的是 `RegionGeometry`，`RegionRevision` 走 `staged.snapshot_state()` 序列化，喂 dict 会当场炸；而架构守卫 `tests/core/test_architecture.py:15` 的 `UI_FORBIDDEN` **只禁 `infrastructure`**，`domain` 在 UI 层是允许的（VM 现在就已 `from domain.tasks.models import …`），故 import `domain.regions.entities` 不破坏守卫、也贴合既有实践。模块仍是纯 Python，全部换算与校验可无 Qt 单测。
- **改 `viewmodel.py`**：`_load_pages` row 补 `width`/`height`；新增两个 int Property `viewerPageWidth`/`viewerPageHeight`（读 `_pages[_viewer_page_id]`，由既有 `viewerChanged` 通知）；`__init__` 补 `region_creator=None`、`region_deleter=None` 两个鸭子注入；`get_inspector_regions`（:504-517，当前**不含几何**）返回补 `"geometry"`；新增三槽，全部复刻 `saveInspector` 的「未绑定 → typed error，绝不抛到 QML」范式：
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

VM 侧（唯一知道页面像素处）：`v = round(n*size)` 后 clamp 到 `[0, size]`（右/下边取 exclusive，故全宽拖拽恰好得 `x=0, w=page_w`）；`bbox` 由点集 min/max 导出。

一组带数字的基准（同时作为测试断言）：页面 `800×1200`、pane `600×600` ⇒ `scale=0.5`、`disp=400×600`、`offset=(100,0)`；item `(150,100)→(350,400)` ⇒ 归一化 `(0.125,0.1667)-(0.625,0.6667)` ⇒ 页面像素 `bbox=[100,200,400,600]`、`polygon=[(100,200),(500,200),(500,800),(100,800)]`。回显走同一常数的逆运算。

## 错误处理与边界

1. writer 未绑定（即 Codex 那行未落时的可见化）→ `_record_command_error("no region creator bound", stage="editor")`，走既有 `commandError`/`commandErrorText` 面；不抛、不静默。
2. 无当前页 → typed error `no page selected`。
3. 退化输入（零面积、polygon `<3` 点）→ **写入前**拦截并给 typed error，依据见上节 `__post_init__` 会抛 `ValueError`。
4. 落在 letterbox 灰带的起笔/加点**直接拒绝**（clamp 前 `n` 超出 0..1），不 clamp 成贴边假框；VM 侧仍保留 clamp 作纵深防御，因为槽是公开契约、测试会直接喂归一化值。
5. 绘制中途切页/起 run/关窗 → overlay 丢在制点集，不落库不报错（尚无副作用）。
6. **dirty 守卫分岔**：`_navigate` 在 Inspector dirty 时会弹保存确认；无条件选中新框会触发该弹窗，而绕过 `_navigate` 直接切选中又会丢掉用户刚敲进 Inspector 的未保存译文。取舍：无 dirty → 选中新框（满足 AC「更新 Inspector」的直观读法）；有 dirty → 仅 `inspectorChanged.emit()` 刷新列表、不抢选中。两分支均可测。
7. 删除为软删，`list_regions`（:279-280）本就过滤 `deleted` ⇒ 删后 overlay 自动不再绘制，无需新增广播；若删的正是选中项则清 `_inspector_region_id`。
8. **run 期间绘制不加禁止**：`tests/workbench/test_gui_write_during_run.py` 已把「run 执行期间 GUI 写入必须存活」定为契约，restore latch 只拒 worker start 且 restore 至今未接生产（见 R-012 记录）。本片不引入新限制，也不重复添加同类测试。

## 测试策略

- 新增 `tests/workbench/test_region_canvas.py`（无 Qt）：上节 800×1200/600×600 的确切整数；全宽边界；越界 clamp；零面积；`<3` 点；矩形→4 点顺序。
- 改 `tests/workbench/test_workbench_viewmodel.py`：creator 收到的是页面像素 int geometry；未绑定 → typed error 且不抛；无页 → typed error；**退化输入 → creator 未被调用**（关键判别，证明校验发生在写之前）；dirty 不抢选中 / 非 dirty 抢选中；`deleteRegion` 未绑定 → typed error。
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
