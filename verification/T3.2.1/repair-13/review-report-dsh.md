# T3.2.1-REPAIR-13 独立 Review 报告（DeepSeek Harness，非作者）

- Reviewer：DeepSeek Harness（DSH）；作者/交付方：ZCode。Reviewer 未参与本切片任何实现。
- Base：`8738c41d7215920935e6fa067d3740e69280cdc6`
- Delivery（代码）：`aed009405fd523c52fa45e604afe40f01cef3d45`
- 证据提交（Handoff/增量验证/截图）：`66a13f8`（本分支 HEAD）
- 分支 / worktree：`agent/zcode/T3.2.1-repair-13` @ `G:/CODEX/New Manga.worktrees/T3.2.1-zcode-repair-13`
- 日期：2026-09-25（Asia/Shanghai）
- Review 环境：Windows 10.0.26200 x64；venv `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3，pytest 9.1.1，PySide6 6.11.2）

> 范围口径说明：任务给定的 scope 是 `git diff 8738c41 aed0094`。但 `aed0094` Handoff、
> `local-verification.md` 的 F-13-2/F-13-4 增量章节、build7/build8 证据、GUI stderr、
> 导出完成截图均位于其后一个提交 `66a13f8`（Handoff front-matter 亦自述"本 Handoff 提交为
> evidence commit，跟在 aed0094 之后"）。因此代码范围按 `8738c41..aed0094` 审计，
> 文档/证据面按 `8738c41..66a13f8` 审计，两者已在下列各节分别标注。

---

## 1. 独立复跑（Reviewer 自测）

| 项 | 命令 | 结果 |
|---|---|---|
| 套件复跑 | `pytest tests/ui_shell tests/reading_export/test_qml_contract.py -q -p no:cacheprovider -rs` | **162 passed in 7.66s，EXITCODE=0**（与 Handoff 声明一致） |
| 范围 whitespace（约定口径） | `git diff --check 8738c41 aed0094 -- src tests` | **exit 0** |
| 范围 whitespace（全路径） | `git diff --check 8738c41 aed0094` | exit 2，3 份 pytest 捕获日志有 trailing whitespace（见 F-3） |

复跑时 stderr 仅出现既有 teardown 期噪音（`AppShell` / `PrimaryNavigationRail` /
`Bookshelf*` / `ReaderView.qml:204` 的 null 绑定 TypeError），与 base 基线行为一致，
不属本切片引入。162 = 155（base 基线）+ 5（`test_repair13_import_entry.py`）+
2（`test_repair13_export_window_open.py`），可加性核对一致。

本次复跑输出写入系统临时目录；审查期间除本报告外未在仓库留下改动（曾临时写入并已删除
一个日志文件；`git status` 仅有派发器自身的两个未跟踪文件 `dsh-review-prompt-4.txt` /
`dsh-review-run-4.log`）。

---

## 2. Scope 审计（逐路径对授权）

`git diff --name-only 8738c41 aed0094` 全部路径归并如下（证据提交 `66a13f8` 另加 13 个
`verification/**` 与 `doc/handoffs/T3.2.1-REPAIR-13-aed0094.md`）：

| 路径 | 授权来源 | 判定 |
|---|---|---|
| `src/ui/qml/bookshelf/BookDetailPanel.qml` | 初版授权：Bookshelf 导入接线（AC1） | 合规 |
| `src/ui/qml/bookshelf/BookshelfView.qml` | 初版授权：导入接线 + 提示/启停（AC1） | 合规 |
| `src/ui/qml/bookshelf/BookshelfToolbar.qml` | 初版授权：导入按钮启停 + hint（AC1/AC3） | 合规 |
| `src/ui/qml/Main.qml` | 初版授权：四页面按钮可读性（AC3，`palette.buttonText`） | 合规 |
| `src/ui/qml/common/ChapterPicker.qml` | 追加授权：两对话框文字对比（R-13-1） | 合规 |
| `src/ui/qml/windows/ExportWindow.qml` | 追加授权：文字对比；本段 F-13-4 一行 `id` | 合规（范围裁认见 §5） |
| `src/ui/qml/reader/ReaderView.qml` | 本段授权：F-13-2 一行 `open()`→`show()` | 合规 |
| `tests/ui_shell/test_repair13_import_entry.py` | 初版授权回归守卫（5 例） | 合规 |
| `tests/ui_shell/test_repair13_export_window_open.py` | 本段授权回归守卫（2 例） | 合规 |
| `verification/T3.2.1/repair-13/**` | 证据 | 合规 |
| `doc/handoffs/T3.2.1-REPAIR-13-*.md`（3 份） | Handoff 模板交付物 | 合规 |

越权类别逐项核查（`git diff --name-only 8738c41 aed0094 -- <path>`）：

- Python 业务逻辑：**零改动**（改动的 `*.py` 仅 `tests/ui_shell/*` 两个测试与
  `verification/T3.2.1/repair-13/probe_ui_states.py` 证据脚本）。
- export service：**零改动**；`packaging/**`：**零改动**；依赖清单：**零改动**；
  Schema：**零改动**；`src/bootstrap/**`：**零改动**。
- Theme tokens：`src/ui/qml/theme/Tokens.qml` **未改**；改动只是把既有 token `inkInv`
  绑定到 `palette.buttonText`/`palette.text`，未改任何 token 值。

**结论：未发现越权变更。**

---

## 3. 证据审计（判别力与真实性）

### 3.1 两个新增测试确实加载真实 QML

- `test_repair13_import_entry.py`：`HOST_QML` 通过 `QQmlComponent.setData(..., SRC_QML.parent / "_TestHost.qml")`
  实例化 `src/ui/qml/bookshelf/BookshelfView.qml`，注入**真实** `BookshelfViewModel` +
  `LibraryService(InMemoryLibraryRepository)`，并以 `QTest.mouseClick` 点击真实章节行。
  `StubImporter` 是导入端口（外部依赖）的测试替身，**不是被测代码的桩**。
- `test_repair13_export_window_open.py`：同样机制加载**真实** `ReaderView.qml`；
  `StubReaderViewModel`/`StubExportController` 仅替代 bootstrap 经 context property
  发布的 viewmodel（`src/bootstrap/app.py` 同契约），被测的 Reader/Export **QML** 为
  仓库真实文件。两份 RED 日志中报错路径均指向
  `file:///.../src/ui/qml/reader/ReaderView.qml:62` 与
  `.../src/ui/qml/windows/ExportWindow.qml:205`，反证测试未加载桩 QML。

### 3.2 RED 日志判别性成立

| 日志 | 关键内容 | 判定 |
|---|---|---|
| `f13-2-pre-repair-red.log` | `ReferenceError: open is not defined`（ReaderView.qml:62），断言失败 | 判别（修复前必红） |
| `f13-4-pre-repair-red.log` | `ReferenceError: exportOutputPath is not defined`（ExportWindow.qml:205），`start_calls=0` | 判别（修复前必红） |
| `discriminating-pre-repair.log` | 导入接线 5 例：**4 failed / 1 passed**，含 `BookshelfView.qml:23 TypeError` 三连 | 判别（唯一通过者是不依赖 QML handler 的 viewmodel 直调例） |

F-13-2 的 RED 日志在 `9d6e3b8` 内、F-13-4 的在 `aed0094` 内，均已入库。
缺陷确系先存：base 版本 `ReaderView.qml` 的 `Component.onCompleted: open()` 与
`ExportWindow.qml` 仅 `objectName: "exportOutputPath"` 而无 `id`（`onClicked` 引用该名字
的行在两段 diff 中均为未改动的上下文），与 `aed0094` Handoff 描述一致。

### 3.3 证据交叉核对

- `build8-f13-4-delivery.raw.log` 记录 `Git Delivery Head: aed009405…`，
  末尾 `Build Completed Successfully`、manifest 5437 条；`build8-f13-4-delivery-exe.sha256`
  = `8b2343dd…`，与 `local-verification.md` 声明一致。build7 同理（`9d6e3b8` /
  `11545a0d…`）。
- `gui2-stderr.log`：**无 ReferenceError**；其中的 null TypeError 行号（如
  `BookshelfView.qml:66/82`）与补丁后行号一致，佐证运行的是补丁后 QML；`gui2-stdout.log`
  为空与 CLI 启动方式相符。
- 截图独立查看：`09-export-window.png`（840×720）为深字浅底、按钮文字清晰可辨；
  `10-export-window-export-complete.png` 显示「导出完成：
  `G:\CODEX\repair13-export-verify\out\export-two-pages.zip`」、内容 `Original`、
  Stale `继续导出现有版本`、范围「当前章节 2 页（阅读顺序）」，与 Handoff 叙事一致。
- 探针 `probe-ui-states.stdout.log` 的 fixture hash（`6d6e58b0…`/`30c0f080…`）与
  `fixtures.sha256`（`97fbf856…`/`3294fd29…`）不同属正常：探针在临时 data root
  **自生成**两张 PNG（`probe_ui_states.py:207-213`），后者是 Sandbox exchange 的固定
  fixture；不构成矛盾。
- 历史探针的 `[PASS] AC4 export window opened` 只断言 `exportWindow` 对象存在
  （`probe_ui_states.py:350` `is not None`），并直接驱动 Python controller 导出，
  **不判别窗口可见性**——所以它能通过而 F-13-2 同时存在。该盲区已由本段新增守卫消除，
  且 `local-verification.md` 已如实自我披露，不构成隐瞒；但该探针未同步加严（F-4）。

---

## 4. AC 判定

| AC | Handoff 判定 | Reviewer 判定 | 理由 |
|---|---|---|---|
| R13-AC1 | PASS | **同意 PASS** | 提示随选择状态切换、导入按钮启停，有 4 个判别例 + 探针 `[PASS]` 行 + 本机 GUI 记录支撑；本机复跑 GREEN。 |
| R13-AC2 | PASS | **同意 PASS（证据强度分级）** | 原生对话框真实弹出、双 fixture 导入、Managed Copy 2 文件、DB 2 行、源 hash 不变：探针有自动断言；「Managed Copy 逐字节 == 源」仅见本机人工记录（探针只断言源 hash 不变与副本数量）。结论成立，但该项自动覆盖度低于其余子项。 |
| R13-AC3 | PASS | **同意 PASS** | 四页面 + 两对话框色值/对比度（4.72–18.7:1）在探针 stdout 有逐控件采样；本段 build8 导出窗口截图（10）独立查看可辨；token 值未改。 |
| R13-AC4 | PASS（本段解除 BLOCKED） | **同意 PASS** | F-13-2/F-13-4 各有修复前 RED（ReferenceError 原文）与修复后 GREEN（窗口 `isVisible()`、`setOutputPath` 收到键入路径、`start_calls==1`）；`10-export-window-export-complete.png` 显示两页 ZIP 导出完成；ZIP/EXE hash 有记录。 |
| R13-AC5 | 本机验证替代完成（用户裁决） | **同意"按用户裁决完成"，但限定口径** | 用户 2026-09-25 裁决取消 Sandbox、以本机验证代替，Handoff 与 `local-verification.md` 已声明本机为含 Python/venv 的开发机、覆盖范围与"干净 Windows"不同。该 PASS 只在本裁决口径下成立，**不得**用于关闭父 Gate 的干净环境验证项；Sandbox 三次失败与恢复材料（`sandbox-attempts.md`、`.wsb`、fixture）保留完整。 |
| R13-AC6 | 待独立 Review | **本次 Review 即为该项**（范围清单核对一致） | 变更路径清单与实际 diff 完全一致，无越权类别；AC6 的正式结论以 Codex 采信本报告为准。 |

---

## 5. F-13-4 范围裁认

**裁定：ACCEPT（并入本切片），附登记条件。**

理由：

1. **同文件、已授权**：`ExportWindow.qml` 已在上段追加授权中开放（文字对比修复），
   本次改动仅新增一行 `id: exportOutputPath`，未引入新文件、新接口。
2. **同一缺陷类别、同一链路**：与 F-13-2 同为先存 QML 名称解析缺陷，都在用户本段
   授权的目标（"完成本机 GUI 两页导出验证"）的关键路径上；不修则 AC4 无法产出
   （`exportRunButton.onClicked` 首行抛 `ReferenceError`，`startExport()` 永不执行）。
3. **低风险、可回退、有守卫**：QML 单行；`revert aed0094` 即回到"F-13-2 已修、
   导出按钮仍被 F-13-4 阻断"；新增判别守卫覆盖该行。
4. **如实登记**：作者在 Handoff 中以"范围声明"明示该修复超出上段字面授权并交 Review/
   Codex 裁认，提供 revert 路径，未见隐瞒。

**条件（不阻塞代码本身）**：Codex 在 `doc/tasks/T3.2.1-REPAIR-13.md` / `doc/STATUS.md`
补登记时必须把 F-13-2 与 F-13-4 **一并**记为本次授权范围（见 F-2），以维持授权链可审计。

**程序性提醒**：本段之所以可直接实施 F-13-4，是因为它是既定目标不可绕过的阻断点，
而非"顺手多修"。后续若再出现同类"顺带"缺陷，仍应遵循 c0aba79 段的先例（F-13-2 当时
未获授权即停手上报），除非该缺陷同样直接阻断已授权目标的交付。

---

## 6. Findings（按严重度）

| ID | 严重度 | 位置 | 问题 | 建议 |
|---|---|---|---|---|
| F-1 | P3（证据卫生） | `verification/T3.2.1/repair-13/screenshots/10-export-window-export-complete.png` | 文件扩展名声明 PNG，实际字节为 **JPEG**（`FF D8 FF E0 … JFIF`），导致严格按签名读取的工具拒读（本 Reviewer 的图片工具即报格式不符）。 | 在 evidence-only 提交中改名为 `.jpg`（或转码为真 PNG）；同步更新 `aed0094` Handoff 与 `local-verification.md` 中的链接文字。 |
| F-2 | P3（治理/可审计） | `doc/tasks/`、`doc/STATUS.md` | **不存在** `doc/tasks/T3.2.1-REPAIR-13.md`；`STATUS.md` 未登记 REPAIR-13（仍写 "current bounded slice is REPAIR-10"）。故 Handoff 所称"初版授权（STATUS 原 Task 范围）"无法从仓库独立核验，授权目前只存在于用户指令与本切片 Handoff 中。属 Handoff"Codex 同步清单"第 1 项（Codex-owned），**非作者违规**。 | Codex 集成前补齐 Task/STATUS 登记：Owner 改派、初版/追加/本段三段授权、base/delivery、AC4 PASS、F-13-4 并入。 |
| F-3 | P3（证据卫生） | `discriminating-pre-repair.log`、`f13-2-pre-repair-red.log`、`f13-4-pre-repair-red.log` | `git diff --check 8738c41 aed0094` **exit 2**（trailing whitespace，来自 pytest 捕获输出的缩进行）。`-- src tests` 范围内 exit 0，故产品/测试代码无 whitespace 问题。仓库有清理先例：`188d72a "docs(verification): remove repair-9 log whitespace"`。 | 在 evidence-only 提交中清理这三份日志的行尾空白；或在集成时接受并记录（不影响代码）。 |
| F-4 | P3（证据强度） | `probe_ui_states.py:350`、`09-export-window.png` 生成路径 | 探针的 `AC4 export window opened` 仅断言 `exportWindow` 对象 `is not None`，不校验 `visible`，且导出经 Python controller 直调而非点击按钮；该日志中该 PASS 在 F-13-2 存在时同样会通过。新 pytest 守卫已覆盖，但探针自身未同步加严，若后续有人以探针 stdout 作为 AC4 证据会再次误判。 | 给探针补 `export_window.isVisible()` 断言与真实按钮驱动（可作为后续 evidence 清理项）。 |
| F-5 | P3（可复现性） | 外部产物 `G:\repair13-build8-out\NewManga\NewManga.exe`、`G:\repair13-export-verify\out\export-two-pages.zip` | 两处外部产物当前**已不在磁盘**（`Test-Path` 均为 False），Reviewer 无法复核 `8b2343dd…` / `1bcdad21…` 与 ZIP 条目级字节一致；只能核对仓库内记录的 hash 与 `build8` 原始构建日志（Delivery Head=aed0094）。 | 后续把 ZIP 本身或"条目名 + 每页 SHA-256"清单入库，使"两页 ZIP 字节级与源一致"可被独立复核。 |
| F-6 | P4（测试保真度） | `tests/ui_shell/test_repair13_export_window_open.py` | 两个用例以 `QMetaMethod.invoke` 直接触发 `clicked()`，未走真实鼠标事件，也未断言按钮 `enabled` 门；若按钮因状态绑定被禁用，QML handler 守卫仍会通过。"按钮确实可点"由本机 GUI 证据承担。 | 可接受；若后续要加严，用 `QTest.mouseClick` 并断言 `isEnabled()`。同类：导入测试的 `_click_chapter_row` 依赖 `childItems()` + `className` 前缀，略脆。 |
| F-7 | P4（信息） | `local-verification.md` / `c0aba79` Handoff | F-13-2 初次登记位置笔误为 `ExportWindow.qml:62`，实为 `ReaderView.qml:62`（实例化处）；`local-verification.md` 已更正并注明。 | 无需动作。 |
| F-8 | P4（范围遗留） | — | F-13-3（重启后书架列表空）、章节行页数文本不刷新、R-13-2/3/4（原生样式观感不统一等）仍未修，已如实移交 Codex。 | 不在本切片；建议 Codex 排期，勿随本切片合并而遗忘。 |

未发现 P0/P1/P2 级问题。

---

## 7. 结论

- Scope：无越权变更；禁止类别（Python 业务逻辑、export service、packaging、依赖、
  Schema、bootstrap、theme token 值）零触碰。
- 判别证据：两份 RED 日志证明守卫在修复前必红；测试加载真实 QML 并驱动真实控件。
- 独立复跑：`162 passed, exit 0`（Reviewer 自测）。
- AC1–AC4 同意 PASS；AC5 同意"按用户裁决以本机验证替代完成"并限定不关闭父 Gate 的
  干净环境项；AC6 由本报告完成范围核对部分。
- F-13-4：**ACCEPT 并入本切片**，条件为 Codex 在 Task/STATUS 中一并登记 F-13-2/F-13-4。

条件 C1（登记）：Codex 补 `doc/tasks/T3.2.1-REPAIR-13.md` 与 `doc/STATUS.md`，含三段授权
与 F-13-4 并入。条件 C2（证据）：后续 evidence-only 提交修正 F-1 的扩展名并清理 F-3 的
日志行尾空白（或在集成时接受并记录）。C1/C2 均不改变代码正确性与范围结论。

**Overall: APPROVE_WITH_CONDITIONS**

（本报告不改变仓库任何其它文件；分支在 Codex 采信本报告并完成集成前仍禁止合并 `master`。）
