# REPAIR-13 本机验证记录（替代 Sandbox 验证——用户裁决 2026-09-25）

用户裁决（2026-09-25，Asia/Shanghai）：**取消 Windows Sandbox 验证，以本机验证代替**；
相关文档与任务按本裁决修订。本文件是 R13-AC5 的替代验证记录。Sandbox 的三次启动
尝试与失败详情保留在 [`sandbox-attempts.md`](sandbox-attempts.md) 作为历史证据。

## 固定对象

- 被测包：delivery `c0aba799168d10ab20c63efa7d8c4ff0a44ed6cd` 构建
  （`packaging/build.ps1 -OutputDir G:/CODEX/repair13-build-out`，exit 0），
  `NewManga.exe` SHA-256 =
  `18eac441cdedac9d51d9e3396e21c129d589183b106d4a688d14c73aceaf464d`
  （[`build6-final-delivery-exe.sha256`](build6-final-delivery-exe.sha256)、
  manifest 5437 条 [`build6-final-delivery-artifact-manifest.sha256`](build6-final-delivery-artifact-manifest.sha256)）。
- 本机环境：Windows 10.0.26200 x64（开发机，**含 Python/venv/开发 PATH——
  覆盖范围与原 AC3"干净 Windows"不同**，如实声明；干净环境验证按用户裁决以本机验证替代，
  后续是否补跑由 Codex/用户决定）。
- 数据根隔离：`--data-root G:\CODEX\repair13-local-verify\data`（不触碰真实用户数据）。
- fixture：`G:\CODEX\repair13-sandbox-exchange\fixture-page-{a,b}.png`，
  SHA-256 `97fbf856…` / `3294fd29…`（[`fixtures.sha256`](fixtures.sha256)）。
- 驱动方式：真实鼠标/键盘（computer-use），无源码注入、无测试桩。

## 流程与结果（打包 EXE 真实 GUI）

| 步骤 | 操作与观察 | 结果 |
|---|---|---|
| 启动 | `NewManga.exe --data-root …` 无其它参数；窗口出现，pid 47980 | PASS |
| AC3 空态 | 工具栏"导入"禁用 + 提示"先新建作品并选择章节，再导入页面"可见；全部按钮文字可辨（无障碍树确认 `button 导入 (pressable disabled)`） | PASS |
| 空标题防拒 | 对话框空标题点 OK → `ValueError: title must be a non-empty string`（域校验拒绝，数据安全） | PASS（正确拒绝） |
| 建书 | 对话框键入"本机验证作品"→ OK → 网格出现书卡 | PASS |
| 选书 | 点击书卡 → 详情面板显示；提示切换为"已选作品还未选择章节：…"（状态反馈正确） | PASS |
| 建章 | 键入"第一章"→ 新建章节 → 列表出现"第一章 分页·从右到左·0 页" | PASS |
| 选章 | 点击章节行 → 行高亮、提示消失、**导入按钮启用**、"进入翻译/进入阅读"启用 | PASS（R13-AC1） |
| AC2 导入 | 点导入 → **原生"打开"对话框真实弹出**（图片过滤器生效）；文件名框键入两个带引号路径多选 → 打开 → Managed Copy 出现 2 个 PNG | PASS |
| Managed Copy 逐字节校验 | 副本 SHA-256 `97fbf856…` / `3294fd29…` == fixture 源 hash | PASS |
| DB 落库 | `pages` 表该章节恰 2 行 | PASS |
| Workbench | "进入翻译" → 页列表显示 `1 fixture-page-a.png`、`2 fixture-page-b.png`；点击页 1 → 高亮选中、查看器渲染红色原图、Inspector 出现区域提示 | PASS |
| AC4 Reader | "进入阅读"（经 ChapterPicker，其按钮/下拉已可辨）→ 红色页渲染、"1 / 2 页 · 50%"、导出…启用 | PASS（按钮与阅读） |
| AC4 导出窗口 | 点击"导出…" → **窗口未出现**；stderr：`ReaderView.qml:62: ReferenceError: open is not defined` | **FAIL → F-13-2（见下）** |
| 退出 | 点关闭 ×2（两次会话）→ 每次进程均退出，无残留 | PASS |

## 新发现（超本切片授权，交 Codex 裁决）

- **F-13-2（P1，阻断 AC4 真实 UI 路径）**：`src/ui/qml/windows/ExportWindow.qml:62`
  `Component.onCompleted: open()` —— `ExportWindow` 根是 **Window**（非 Popup），Window
  没有 `open()`，QML 抛 `ReferenceError: open is not defined`，窗口从未 `show()`。点击
  Reader 的"导出…"时 `openExporter()` 成功返回 controller，但窗口静默不出现。此前源码
  探针的"AC4 export window opened"只断言了实例存在 + 直接驱动 controller 导出（绕过窗口
  可见性），未暴露该缺陷；Build 3 因章节无法导入从未走到这里（manual-observations：
  "导出实现尚未被有效测试"）。**该缺陷先于本切片存在**（delivery 2f18e78 与 base 8738c41
  同样如此）。最小修复：`open()` → `show()`（或改用 `Window.visible` 绑定），一行，位于
  本切片已授权过的文件内；按用户本轮"只可修改按钮文字对比问题"的限定未改，交 Codex
  裁决新范围。
- **F-13-3（P2）**：重启后书架列表为空（DB `books` 表有书、清空持久化搜索文本后仍空），
  `bookListModel` 未随启动恢复。本切片未触碰列表加载逻辑（base 8738c41 行为相同——
  上次会话同样路径未验证过重启，无法给出更早基线），交 Codex 排查。
- **信息**：章节行的页数文本在导入后仍显示"0 页"（DB 已 2 页），章节列表 model 未在
  导入后刷新页数列；Python viewmodel 侧通知，超本切片范围，随 F-13-3 一并交 Codex。

## 结论

- 本机验证支持：R13-AC1、R13-AC2（含文件选择器真实打开与双 fixture 导入闭环）、
  R13-AC3（四页面+对话框按钮可辨，包内行为与源码探针一致）、R13-AC4 的按钮启用与
  阅读链路、正常退出。
- R13-AC4 的**导出窗口打开**被先存缺陷 F-13-2 阻断 → **AC4 = BLOCKED（F-13-2）**，
  如实记录，不改判父 Gate。
- R13-AC5 = 本机验证替代完成（用户裁决）；干净 Windows 环境覆盖差异已声明。

## 产物

- `G:\CODEX\repair13-local-verify\`：`local-verify.log`、`gui-stderr.log`、`gui-stdout.log`、
  `data\`（library.db + managed/ 副本，hash 见上文）。
- 主工作区与本分支的仓库内证据：本文件与 [`build6-*`](build6-final-delivery-exe.sha256)。

---

# F-13-2 / F-13-4 修复验证（delivery 9d6e3b8 + aed0094，2026-09-25）

用户授权按 Handoff 中的 F-13-2 裁决实施微切片修复；验证过程中发现并修复了
同性质的 F-13-4（见下）。两个缺陷均为**先于本切片存在**的 QML 一行修复，
均在 `openExporter` 真实 UI 导出路径上。

## 修复内容与判别证据

| 缺陷 | 位置 | 修复 | 判别证据（修复前 RED / 修复后 GREEN） |
|---|---|---|---|
| F-13-2（P1） | `ReaderView.qml:62`（Handoff 初登记为 ExportWindow.qml:62，实为实例化处） | `open()` → `show()`（Window 无 `open()`） | [`f13-2-pre-repair-red.log`](f13-2-pre-repair-red.log)：守卫测试捕获 `ReaderView.qml:62: ReferenceError: open is not defined`，窗口 `visible=false`；修复后 PASS |
| F-13-4（P1） | `ExportWindow.qml:116/205` | 输出路径 TextField 补 `id: exportOutputPath`（onClicked 引用了只有 objectName 的名字，handler 首行抛错，`startExport()` 永不执行） | [`f13-4-pre-repair-red.log`](f13-4-pre-repair-red.log)：守卫捕获 `ExportWindow.qml:205: ReferenceError: exportOutputPath is not defined`、`start_calls=0`；修复后 PASS |

回归守卫：[`tests/ui_shell/test_repair13_export_window_open.py`](../../../tests/ui_shell/test_repair13_export_window_open.py)
（加载真实 ReaderView + stub readerViewModel，驱动真实窗口按钮）。
测试口径：`pytest tests/ui_shell tests/reading_export/test_qml_contract.py` →
**162 passed，exit 0**（venv `TASK-012-py312`）。

## 固定包

| 构建 | Delivery | EXE SHA-256 | 证据 |
|---|---|---|---|
| build7（中间，仅验证到 F-13-2 修复、发现 F-13-4） | `9d6e3b881e6566c17e161686f7ab1fb2a39828e3` | `11545a0d57ad29fdb4c390a83619f48e03cef627bfddf70c8a5ae4d08a8184db` | [`build7-f13-2-delivery-exe.sha256`](build7-f13-2-delivery-exe.sha256)、raw log 入库 |
| **build8（最终）** | **`aed009405fd523c52fa45e604afe40f01cef3d45`** | `8b2343ddb295e5b69699851bc10701311ed285ce3b52b911593538e87a7bc6e1` | [`build8-f13-4-delivery-exe.sha256`](build8-f13-4-delivery-exe.sha256)、[`manifest 5437 条`](build8-f13-4-delivery-artifact-manifest.sha256) |

## build8 本机 GUI 全流程（真实鼠标/键盘，--data-root 隔离）

`G:\CODEX\repair13-export-verify\data2`（全新隔离数据根，不触碰真实用户数据）。
pid 38740，全程 stderr 采集 [`gui2-stderr.log`](gui2-stderr.log)。

| 步骤 | 操作与观察 | 结果 |
|---|---|---|
| 启动 | `NewManga.exe --data-root …`；窗口出现，空态"导入"禁用 + 提示可见 | PASS |
| 建书/建章/选章 | "导出验证作品B"/"第一章"；提示随选择状态正确切换、导入按钮随之启停 | PASS（R13-AC1 保持） |
| AC2 导入 | 原生"打开"对话框（图片过滤器）键入双 fixture 路径 → DB `pages` 2 行，hash `97fbf856…`/`3294fd29…` 与源一致 | PASS |
| **AC4 导出窗口（F-13-2）** | 点击"导出…"→ **"导出成果"窗口真实出现**（build6 同操作静默无窗口）；范围"当前章节 2 页（阅读顺序）" | **PASS（BLOCKED 解除）** |
| **AC4 导出执行（F-13-4）** | 内容切 Original、Stale 切"继续导出现有版本"（banner 同步）、输出路径改验证目录 → 点"导出"→ 状态"**导出完成**：G:\CODEX\repair13-export-verify\out\export-two-pages.zip"；"再次导出（相同设置）"启用（history 有记录） | **PASS** |
| **ZIP 校验** | [`export-two-pages-zip.sha256`](export-two-pages-zip.sha256)：`1bcdad21…`；2 条目 `0001_fixture-page-a.png`/`0002_fixture-page-b.png`，字节级 hash 与 fixture 完全一致 | **PASS（两页 ZIP 达成）** |
| AC3 按钮可读性 | 导出窗口全部按钮（导出/取消导出/打开所在文件夹/再次导出/关闭）深底浅字清晰可辨（截图 [`screenshots/10-export-window-export-complete.jpg`](screenshots/10-export-window-export-complete.jpg)；F-1 更正：文件为 JPEG 字节，扩展名由 .png 更正为 .jpg） | PASS |
| 退出 | 关闭导出窗口 + 主窗口 → 进程退出、无残留；stderr 无 ReferenceError（仅退出阶段既有 ViewModel 置空噪音） | PASS |

## 结论（增量）

- **R13-AC4 = PASS**（此前 BLOCKED F-13-2）：真实 UI 全路径（窗口打开 → Original +
  继续导出 → 输出路径 → 导出完成）生成两页 ZIP，字节级与源一致。
- F-13-2、F-13-4 均已修复并有判别性回归守卫；`openExporter` 链路的其余部分
  未触碰（Python/export service/打包实现零改动）。
- F-13-3（重启后书架列表空）与章节行页数文本不刷新仍未修，维持交 Codex。
- 干净 Windows 覆盖差异声明同上节（本机为开发机环境）。

## 产物（增量）

- `G:\CODEX\repair13-export-verify\`：`gui2-stdout.log`、`gui2-stderr.log`、
  `out\export-two-pages.zip`、`data2\`（隔离数据根）。
- 仓库内：上述守卫测试、两份 RED 日志、build7/build8 证据文件、本文件。
