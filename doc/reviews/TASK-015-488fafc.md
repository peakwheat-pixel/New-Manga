---
task_id: TASK-015
reviewer: ZCode 子 agent（窗口授权 2026-09-16）
author: ZCode
base_commit: 1000ac82743b75df8b4b385bc7096a015e13f107
reviewed_head: 488fafc
decision: changes_requested
---

# Review：TASK-015

## 审查背景与授权说明

本次审查按用户 2026-09-16 全权窗口授权条款执行：由与实现同体（ZCode）的独立子 agent
完成代码审查，结论只能登记为 `approved_subagent` 或 `changes_requested`，不得写
`approved`。该结论是窗口期内的同体审查结果，**不等同于跨 Agent 独立批准**；窗口期满后
仍需外部 post-hoc 复审，Task 进入 done 仍以协作协议要求的独立 Review 与 Codex 集成验证
为准。

关于审查对象：STATUS 窗口章节曾引用第一轮交付 `fac2ffe`，该实现已被 `488fafc`
全量重写取代（`git log 1000ac8..488fafc` 可见 fac2ffe→6917b0b→488fafc 的演进，
Handoff `TASK-015-488fafc.md` frontmatter 亦声明 supersedes）。本轮审查以
`1000ac8..488fafc` 的生产 diff 为准，未采信 fac2ffe 轮任何描述。

## 范围与依据

**实际读过的需求文档（均为 worktree 内当前版本）**

- `doc/tasks/TASK-015.md`（AC、白名单、禁止范围、测试要求）
- `doc/03_DATA_MODEL.md` §29 ReadingProgress（行 1793 起）、§31 ExportHistory（行 1858 起）
- `doc/04_USER_FLOW.md` §33~37（行 1353~1480）
- `doc/05_UI_MAPPING.md` §37~42（行 1300~1428）、§51 Export Window（行 1672~1710）
- `doc/06_TRANSLATION_PIPELINE.md` §96~97（行 2806~2859）
- `doc/08_ACCEPTANCE_CRITERIA.md` AC-LIB-004（行 423）、AC-EXPORT-001~003（行 2054~2093）、AC-READ-001~005（行 2099~2126）

**实际读过的交付物与 diff**

- 完整 diff `git diff 1000ac8..488fafc`（22 files，+4062/−25）：`src/application/reading/{__init__,ports,service}.py`、`src/application/export/{__init__,ports,service,pdf_qt}.py`、`src/ui/viewmodels/reader/viewmodel.py`、`src/ui/viewmodels/export/viewmodel.py`、`src/ui/qml/reader/ReaderView.qml`、`src/ui/qml/windows/ExportWindow.qml`、`tests/reading_export/`（conftest、helpers、test_reading、test_export、test_viewmodels、test_qml_contract）、`doc/tasks/TASK-015.md`、handoff/verification 文档。
- 交付文档：`doc/handoffs/TASK-015-488fafc.md`、`verification/TASK-015/author-verification.md`。
- 工作区 HEAD 为 `ed382d6`（= 488fafc + 纯文档提交），生产代码与 reviewed_head 一致，测试直接在该 HEAD 运行。

**核对过的交叉项**

- 白名单符合性：diff 中每个路径逐一对照 TASK-015.md 允许修改范围——全部在白名单内（`doc/handoffs/TASK-015-*.md` 模式覆盖 fac2ffe 轮文件），未触碰 Schema/migration、`src/bootstrap/app.py`、依赖清单、AGENTS、AppShell、BookDetailPanel 或其他 Task。
- 架构边界：application/reading 与 application/export 仅 import 标准库 + `domain.books.entities` + 本包 ports；无 infrastructure/ui import；PySide6 在生产代码中仅出现于 `pdf_qt.compose()` 函数体内（延迟导入），`application.export.__init__` 不引用 pdf_qt，无 Qt 解释器导入该包不触发 Qt。ui 层两个 viewmodel 仅 import PySide6 + application 层，无 infrastructure。QML 两个文件为纯状态渲染 + slot 调用，无业务规则。
- 抽查实现↔测试真实对应：os.replace 末步提交与 temp 清理（`service.py:246-281` ↔ test_cancel/test_failure/test_disk_error 三例）；stale 默认拦截在 `_resolve_target` 之前 raise（`service.py:203-205` ↔ `test_translated_export_with_stale_pages_is_refused_by_default` 断言无产物）；覆盖三策略（`_resolve_target` ↔ 三例测试断言旧文件字节级保留/auto_rename 命名）。

**未审到的部分**

- 未做人工 GUI 冒烟（`--smoke-test` 未运行）；QML 行为依赖契约测试（PySide6 真加载 + QTest 键事件）。
- PDF 外部阅读器像素级验收 NOT_RUN（沿用作者登记，环境无阅读器/QtPdf）。
- 生产装配接线、SQLite 迁移、BookDetailPanel 摘要接线、Reader Nav 章节数据源不在本 diff，按作者登记转 Codex 裁量，本轮未验证。
- Webtoon 完整按宽滚动验收归 TASK-020，本轮只审数据链路与纵向 Flickable 骨架。

## Findings

| ID | 级别 | 文件/行 | 触发与影响 | 复现证据 | 建议 | 处理状态/修订 commit |
|---|---|---|---|---|---|---|
| R-001 | P1 | src/ui/qml/reader/ReaderView.qml:105-118 | RTL 章节下翻页按钮文字与动作绑定矛盾：`readerPreviousPage`（onClicked=previousPage、enabled=canGoPrevious）在 RTL 时文字为"下一页 ◀"；`readerNextPage` 文字"▶ 下一页"。结果 RTL 章节屏幕同时出现两个"下一页"按钮，左侧那枚点击后实际倒退，与键盘 Left=前进（已测试正确）方向相反，直接误导 AC-READ-003 的 UI 交互 | 静态代码证据（行 108/110/114/116）；契约测试只覆盖键盘序（test_reader_rtl_ltr_key_order）与 readerNextPage 点击，未覆盖 readerPreviousPage 的文字/动作组合 | RTL 时两按钮文字互换（readerPreviousPage 应显示"上一页 ▶"类文案），或改为不随 direction 变换文字；补一条 RTL 按钮点击契约测试 | open |
| R-002 | P1 | src/ui/viewmodels/export/viewmodel.py:312-335 | `repeatExport` 的 worker `_work` 只有 `except ExportCancelledError`/`except ExportError`，缺 `except OSError`（startExport 的 `_work` 行 278 有）。repeat 途中任何 I/O 错误（磁盘满、目标目录不可写/被替换为文件、权限）从线程逃逸：`running` 永久停留 True、exportFinished/exportFailed 均不发射、状态卡在"正在按相同设置导出…"，之后所有导出/再导出请求被 `if self._running: return` 拒绝，导出功能静默失效直至重启 | 已实际复现（环境 A）：首导成功后将输出目录替换为同名普通文件，`repeatExport` 抛 `FileExistsError [WinError 183]`（service 层已记 failed 到 history），worker 线程崩溃，实测 `running=True`、两信号计数 0、`statusMessage='正在按相同设置导出…'`，复现脚本输出 `BUG CONFIRMED` | 给 repeatExport 的 `_work` 补 `except OSError as error: self._fail(f"导出写入失败：{error}")`，与 startExport 对齐；补一条 repeat OSError 用例 | open |
| R-003 | P2 | src/ui/qml/reader/ReaderView.qml:206-211 | Webtoon 滚动恢复时序风险：`Component.onCompleted: contentY = active ? model.scrollOffsetY : 0` 执行时图片（`asynchronous: true`）尚未解码，`contentHeight`（paintedHeight）为 0，contentY 会被 Flickable 钳制到 0，"恢复"大概率落空。保存路径（500ms 节流）已验证，恢复路径无测试 | 代码证据；test_reader_webtoon_swaps_in_vertical_viewer 只验证手动设 contentY 后保存，未验证重开恢复；测试自身注释也承认需先等 contentHeight>0 | 图片 onStatusChanged=Ready 后再设 contentY；集成/TASK-020 时补恢复路径验证 | open（可与 TASK-020 合并处理） |
| R-004 | P2 | tests/reading_export/test_export.py:351 | `test_disk_error_on_final_write_keeps_target` 的无残留断言写错模式：target 为 `out.zip`，temp 实际前缀为 `.out.zip.`，断言 `glob(".out.txt*")` 恒为空 → 该"temp 已清理"断言恒真，未实际校验（target 保留断言仍有效；取消用例行 305 的 `.cancelled.zip*` 模式正确，temp 清理逻辑另有真实覆盖） | 静态对照：`_new_temp` 生成 `.{target.name}.<rand>.tmp` | 模式改为 `".out.zip*"` | open |
| R-005 | P2 | src/application/export/service.py:425-461 | `_record` docstring 称历史持久化 best-effort、"never masks the export outcome"，但实现为：仅 FAILED 状态吞掉历史写失败，COMPLETED/SKIPPED/CANCELLED 下历史写失败会 re-raise。COMPLETED 场景目标文件已被 os.replace 更新，调用方（UI 显示"导出写入失败"）会误判导出失败，实际新文件已落盘且旧文件被覆盖。低概率（磁盘满时小 JSON 历史写失败而大文件写成功）、fail-loud 方向保守，但与文档表述及 UI 呈现语义不一致 | 代码对照 docstring 行 434 与 except 分支行 458-461 | 统一语义：或全部 best-effort（记日志/状态提示"历史未记录"），或修正 docstring 并让 UI 区分"产物成功但历史失败" | open |
| R-006 | P2 | doc/handoffs/TASK-015-488fafc.md、doc/tasks/TASK-015.md | 文档表述与提交时序出入：Handoff 称旧 handoff"在本提交中删除"，但 `doc/handoffs/TASK-015-fac2ffe.md` 在 488fafc 树中仍存在（`git ls-tree 488fafc -- doc/handoffs/` 可见，且是审查 diff 的 +36 行组成），实际删除发生在 ed382d6。当前 HEAD 已删除，无实质影响，但"仅审查 1000ac8..488fafc"的 diff 因此含一个与正文描述相反的文件新增 | `git ls-tree 488fafc -- doc/handoffs/`；`git diff 488fafc..ed382d6 --stat` | 无需改生产代码；后续交付说明避免以 head commit 指代后续文档提交的变更 | open（记录性） |

观察项（不计入 findings 处置）：

- 作者诚实登记的 NOT_RUN/NOT_IN_SCOPE 项（PDF 像素级验收、真实磁盘满/权限注入、生产装配接线、Reader Nav 数据源、SQLite 迁移）经核属实，均确属白名单外或环境受限，转 Codex 集成裁量，不作为本轮阻塞，但集成前不可视为已验证。
- `test_qml_contract.py:26-27` 重复 `from application.export import ExportPage`（无害冗余）。
- `service.py` 的 `_scope_snapshot` 等函数体内局部 `import json`：风格选择，无功能影响。
- `save_scroll_offset` 的 viewmodel 槽只暴露 offset_y（offset_x 由 service 支持但 UI 未接）：与 D03 §29"Webtoon 重点保存 last_page_id + scroll_offset_y"一致，可接受。

## 验证

| 场景 | 命令或手工步骤 | 环境/commit | 结果 | 证据 |
|---|---|---|---|---|
| 专项测试（完整 Qt） | `PYTHONPATH=src "G:/CODEX/New Manga.task-envs/TASK-014-py312/Scripts/python.exe" -m pytest tests/reading_export -q`（CWD=worktree） | Python 3.12.3 + PySide6 6.11.2 / HEAD ed382d6（生产代码=488fafc） | PASS（63 passed, 0 skipped，2.37s） | 本轮实际运行输出 |
| 全仓回归（完整 Qt） | 同解释器 `-m pytest tests -q` | 同上 | PASS（535 passed, 0 skipped，22.56s；含 tests/core/test_architecture.py 守卫通过） | 本轮实际运行输出 |
| 专项 skip 分列（无 Qt） | `PYTHONPATH=src python -m pytest tests/reading_export -q -rs` | Python 3.14.6，`find_spec('PySide6') is None` / 同 HEAD | PASS（42 passed, 3 skipped；skip 逐条：test_qml_contract.py:21、test_viewmodels.py:21、test_export.py:421，原因均为 "PySide6 not installed"） | `-rs` 输出与 author-verification B1 记录逐字一致 |
| repeatExport OSError 缺口 | 复现脚本（首导成功→输出目录替换为同名文件→repeatExport，泵事件后检查 running/信号计数） | 环境 A / 同 HEAD | **复现成立（BUG CONFIRMED）**：OSError 逃逸 worker、running=True、exportFinished/exportFailed 计 0 | 脚本输出含 threading traceback（viewmodel.py:324→service.py:343→_new_temp mkdir FileExistsError） |
| 架构边界 | grep 全部新增模块 import；确认 PySide6 仅在 pdf_qt.compose 体内；tests/core/test_architecture.py 在全仓回归中通过 | 同 HEAD | PASS | 本报告"范围与依据-核对过的交叉项" |
| 白名单符合性 | diff 路径清单逐一对照 TASK-015.md 允许修改范围 | 1000ac8..488fafc | PASS（无越界路径） | git diff --stat |
| AC-EXPORT-003 stale 拦截（顺带实证） | 复现脚本首导阶段：translated 模式、页面无译图、默认 abort | 环境 A / 同 HEAD | PASS：StaleExportError 文案含"缺少译图的页/重新渲染/继续导出现有版本"，未产出文件 | 复现脚本第一次运行即被拦截（"first export never finished: 导出失败：部分页面不是最新渲染结果…"） |
| PDF 外部阅读器像素级验收 | — | — | NOT_RUN | 沿用作者登记；环境无阅读器/QtPdf，本轮为结构级回读覆盖 |
| 人工 GUI 冒烟 | — | — | NOT_RUN | QML 行为以 8 例 PySide6 契约测试（真加载+QTest 键事件）代替 |

## 三轴结论

**Spec（需求符合性）**：主体符合。D03 §29/§31 字段逐列落地且行结构与未来 SQLite 列一一对应；D04 §33~36 双模式独立进度/时长、resume/restart 有测试；D04 §37/D03 §31 五格式、顺序、命名、覆盖三策略、history 全字段、repeat、打开所在文件夹均有实现与测试；D06 §97 stale 不静默在 reader（横幅提示）、export（默认拒绝 StaleExportError + VM 警告文案 + QML banner 测试）两侧落地；AC-LIB-004 交付数据层（UI 接线按登记转集成）。**不符合项**：R-001（AC-READ-003 的 RTL 工具栏交互文案错误）；**保留风险**：R-003（AC-READ-005 恢复路径时序，部分验收本就转 TASK-020）。因此 Spec 轴判定为"修复 R-001 后可达标"。

**Architecture（架构符合性）**：符合。分层 import 干净（application→domain/标准库；ui→PySide6/application；无 infrastructure）；PySide6 延迟导入真实隔离（`application.export` 包导入链不触 pdf_qt，无 Qt 解释器 42 passed 实证）；QML 无业务逻辑；全部变更在白名单内，未触碰冻结面（Schema/bootstrap/依赖/AGENTS）；JSON 文档存储为 Schema 冻结期的登记性替换，端口收窄了后续 SQLite 适配的影响面。守卫测试随全仓回归通过。

**Verification（验证充分性）**：充分且有超出作者记录的独立证伪。三条计划命令全部复算通过且与 author-verification 数字逐项一致（63/535/42+3，skip 原因逐条吻合）；关键 durability 声明（os.replace、取消/失败保护、覆盖三策略、stale 拦截）经代码级抽查与测试断言对应确认；同时独立复现出一个作者未发现的 P1（R-002）。缺口：R-001/R-003 所在交互路径无测试、PDF 像素级与真实磁盘故障 NOT_RUN（已登记）。

## 结论与复审

**decision = changes_requested。**

理由：发现 2 项未解决 P1——R-002（repeatExport 无 OSError 兜底，I/O 故障下导出 UI 永久卡死且无提示，已实证复现）与 R-001（RTL 章节工具栏两个"下一页"按钮语义矛盾，误导 AC-READ-003 的直接交互）。两项修复量都很小（一行 except、一处文案对调+补测），不影响本轮交付的整体设计质量：服务层、数据模型映射、stale 语义、durability 契约与测试密度均达到集成标准，P2 项（R-003~R-006）可随修或明确 disposition。

可集成性判断：**当前固定 head 488fafc 不建议交 Codex 集成**；建议作者在本 worktree 修复 R-001/R-002（建议顺带 R-004 一行测试修正）后生成新 head，由本轮 reviewer 做增量复审（复核两个 P1 的 diff 与新测试），无新增 P0/P1 后改登记 `approved_subagent`，再交 Codex 按协议集成并行使装配接线/SQLite 迁移的范围变更裁量。

性质与剩余风险：本结论是用户窗口授权下的同体（ZCode 子 agent）审查，不等同跨 Agent 独立批准；窗口期满后需外部 post-hoc 复审，Task 的 done 仍取决于独立 Review 与 Codex 集成验证。剩余风险：① 生产装配、SQLite 迁移、BookDetailPanel 接线未验证，集成期可能出现接线级缺陷；② Webtoon 恢复路径（R-003）与完整按宽滚动归 TASK-020，届时需复核；③ PDF 像素级验收与真实磁盘满/权限注入仍 NOT_RUN；④ 阅读时长心跳机制（5s 粒度）在进程挂起/睡眠场景的准确性未验证。
