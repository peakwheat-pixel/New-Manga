---
kind: posthoc-review
object: ZCode 全权窗口（2026-09-17 23:12:28 → 2026-09-18 08:50）两轮全部交付
range: c3dabc8..5f3c115（63 commits，7 项 approved_subagent 集成 + W4 文档工作）
reviewer: Codex（Lead；作者 ZCode 已回避）
external_second_reviewer: DeepSeek Harness（待补，见「结论」）
decision: approved（7/7 维持，无推翻）
errata: 见文末「勘误（2026-09-18）」——Spec 轴由"0 实现有误"修正为 **2 项 P1 实现缺陷（F-1/F-2）**，由 DSH 外部复审发现并经我独立复现
---

# Post-hoc 复审：ZCode 窗口（2026-09-17 → 2026-09-18 08:50）

**性质**：窗口条款要求的**外部 post-hoc 复审**（窗口内 Review 均为 `approved_subagent` 同体审查，**可被本复审推翻或重开**）。作者 ZCode 已在 [POSTHOC-REVIEW-BRIEF-2026-09-18](../handoffs/POSTHOC-REVIEW-BRIEF-2026-09-18.md) 中自述回避。

**执行口径**：四轴 = **Standards** + **Spec** + **Architecture** + **Verification**，逐轴声明、分别报告、**不跨轴排名**。双轴隔离按已固化环境结论走 §6 第 6 条**兜底**（本环境无并行子代理通道），并在此声明该偏差。

## 范围与依据（含覆盖度声明）

- 被审范围：`git diff c3dabc8..5f3c115` —— **63 commits、7 项集成**（`372c3bf` TASK-037、`4d0f932` TASK-033、`b738200` TASK-020、`ba7d560` TASK-023、`f835ac9` TASK-038、`c8024fe` TASK-039、`5bc17f8`+`b940497` TASK-021）+ W4 文档同步（`00_INDEX`/`12_ROADMAP`/窗口报告 v1–v3）。
- 复审输入：7 份窗口内 Review 报告（`doc/reviews/TASK-0xx-*.md`）、各 Task Handoff、`verification/TASK-0xx/**`（含 full-suite 日志）、窗口报告 v1–v3、作者自述的诚实边界。
- **覆盖度（诚实声明）**：我做了①**逐切片边界与证据完整性的机械核对**（全量）②**独立重跑全仓**③**对 5 处最高风险主张做代码级深挖**（下表标注）。我**未**逐行通读全部 63 个 commit 与全部 7 份窗口内 Review 的每一行；未复跑每个切片各自的 ≥5 次 full-suite 日志（抽样）；未复现作者登记的 EXIT=127 异常（不可复现）。**未覆盖项以「未验证」标注，不视为已核。**

## Standards

轴状态：**`executed`**。

**① 逐切片边界（全量核对，`git diff --name-only <merge>^1 <merge>`）**：7 个切片的 `src/` 改动**全部落在各自 Task 白名单内**，无越界文件：

| 集成 | `src/` 改动 | 判定 |
|---|---|---|
| `372c3bf` TASK-037 | （仅 `tests/reading_export/**`） | ✓ 白名单为 tests+docs |
| `4d0f932` TASK-033 | `application/rendering/service.py`、`application/translation/knowledge/term_extraction.py`、`bootstrap/app.py`、`infrastructure/providers/handlers.py` | ✓ 全在白名单 |
| `b738200` TASK-020 | `infrastructure/imaging/**`（新建，已授权）、`ui/qml/reader/ReaderView.qml`、`ui/viewmodels/reader/viewmodel.py` | ✓ |
| `ba7d560` TASK-023 | `requirements.txt`、`application/importing/documents/**`、`infrastructure/importing.py` | ✓（依赖为用户批准的 `pypdfium2`） |
| `f835ac9` TASK-038 | `bootstrap/app.py`、`infrastructure/imaging/webtoon_tiles.py`、`ui/viewmodels/{bookshelf,reader}/viewmodel.py` | ✓ |
| `c8024fe` TASK-039 | `application/tasks/service.py` | ✓ 恰为白名单 |
| `5bc17f8`+`b940497` TASK-021 | `application/maintenance/**`（新建，已授权）、`bootstrap/app.py`、`infrastructure/filesystem/managed_storage.py`、`infrastructure/sqlite/library.py` | ✓ |

**② 依赖与 Schema**：`requirements.txt` 净变更**仅 1 行** `pypdfium2==5.13.0`（用户 2026-09-17 单独批准）；**`schema`/`migration` 文件 0 命中**（TASK-021 的软删除复用了已存在的 `deleted_at` 列，作者有 schema 前置核对记录）✓。

**③ 无删除**：`git diff --diff-filter=D --name-only c3dabc8..5f3c115` **为空** —— 窗口内**没有删除任何文件**（含测试）✓。

**④ skip 纪律**：全仓 skip 数**未变**（仍 6 条、全部为既有 `tests/network` 的 `openssl unavailable`）。窗口内新增的 skip 机制**仅 1 处**：`pytest.importorskip("PySide6", ...)`（模块级，providers 的 full-chain 用例）。判定：**P3，接受并登记** —— 该写法与仓库既有先例一致（`tests/reading_export/test_viewmodels.py:22`）、作者已在窗口报告显式披露、且在**声明 venv** 中不产生 skip（PySide6 已装）。**但**它确实是一种 skip 声明，未来切片应优先用带理由的显式 fixture/skipif，或在 Task 中预先声明。

**⑤ 诚实性**：三处 `BLOCKED` **均未记 PASS**（TASK-020 超大 webtoon 像素解码、TASK-023 MOBI、TASK-033 AC-RFULL-001）；`tests/reading_export/test_qml_contract.py:231` 把 TASK-038 带来的**前提变化**明确标注为"等价更新、非放宽"；作者主动登记一处**不可复现的 EXIT=127** 异常。**无硬性违反记录在案标准。**

**本轴小结**：0 项硬性违反；1 项 P3（`importorskip`，已披露且无实际影响）。本轴最严重项 = 该 P3。

## Spec

轴状态：**`executed`**。逐切片核对 AC 与交付真实性；**深挖项**以 ★ 标注（代码级）。

| 集成 | 窗口内判定 | 本复审判定 | 依据（含深挖） |
|---|---|---|---|
| `372c3bf` TASK-037 flaky + R-01 | approved_subagent（2×P3） | **approved** | ★ 读 `fix` 侧改动：滚动前置条件改为"内容足够再设值"、诊断改数值兜底，**未放宽断言/未加 skip**；R-01 的 `TypeError` 掩蔽路径已消除 |
| `4d0f932` TASK-033 完整链 | approved_subagent | **approved** | ★ **单一写者 P0 核实**：`handle_render` 返回 `revision_updates={}`，并注明"seam 不得二次翻转同一指针"，实际提交由 `RenderService` 的 CAS 承担；AC-RFULL-001 保持 `BLOCKED`；R-001（planner `_clean_available`）标记为"白名单外移交"，**处置正确**（后由 TASK-039 承接） |
| `b738200` TASK-020 webtoon 分块 | **首轮 changes_requested** → 修订 → approved_subagent | **approved** | ★ 修订侧存在"wanted-index 门"（解码前先判带宽），并有"tile 3 未被物化 / 缓存目录恰为带宽"的回归；oversize 解码登记 `BLOCKED` 未记 PASS |
| `ba7d560` TASK-023 PDF 导入 | approved_subagent（4×P3） | **approved** | 依赖 diff 恰为获批 1 行；MOBI 走 typed `UNSUPPORTED_FORMAT` **不伪造**；Managed Copy 纪律复用 |
| `f835ac9` TASK-038 生产装配 | approved_subagent | **approved** | ★ **核实到 5 个 context property**：`navigation`/`bookshelf`/`workbench`/`reader`/`export_viewmodel`(`bootstrap/app.py:685-691`)；装配契约测试补于 `tests/core/test_bootstrap.py:402/420`；`:231` 的用例做**前提等价更新**而非删除 |
| `c8024fe` TASK-039 planner Clean 可用性 | approved_subagent | **approved** | ★ 根因（看 stage 而非 artifact）与修法一致；`clean_probe` 为**可选参数**，未注入时行为与修前**逐字节等价**（作者留了 AC③ 对照矩阵）；**生产注入未实现**（白名单外）→ 见裁决 #1 |
| `5bc17f8`+`b940497` TASK-021 trash 子集 | approved_subagent + R-001 修订 | **approved** | ★ **用户数据保护核实（安全关键）**：`purge_batch` 只删 `managed_original_ref`（受控副本）再删 DB 行；`purge_pages` 只删行并自述"用户源文件在 managed root 之外、此处永不寻址"；R-001 修订使 batch **只记录实际软删除的 id**，并加固同毫秒 `deleted_at` |

**① 缺失/部分完成**：无（各切片 AC 范围内的要求均达成）。**② scope creep**：无（越界文件 0）。**③ 看似实现但有误**：未发现。

**本轴小结**：**7/7 维持 `approved`，无推翻、无重开**；0 缺失 / 0 scope creep / 0 实现有误。本轴最严重项 = 无（唯一"部分落地"是 TASK-039 的生产注入，属已登记的跨白名单项，见裁决 #1）。

## Architecture

轴状态：**`executed`**。

- **分层守卫仍然成立**：全仓含 `tests/core/test_architecture.py` 的 AST 守卫（application 不得 import infrastructure），本次全仓复跑**通过** → 窗口未引入方向倒置。
- **单一写者不变式**（我在 TASK-033 释放时立的 P0 约束）：**成立** —— render handler 不重复翻转 `translated` 指针，提交权留在 `RenderService` 的 CAS。
- **产品边界（QML 不得直连 DB/文件）**：★ 核对 `ReaderView.qml` 改动 —— 瓦片经 `model.tiles`（Python 侧属性）下发 `source: modelData.url`，QML 侧无 sqlite/文件访问；**整图路径保留为回退**（`visible: !tilesHost.visible`），未注入工厂时行为不变。
- **装配可达性**：窗口内出现两次"能力已实现但生产不可达"（TASK-020 tile、TASK-023 文档导入），根因是 `assemble_engine` 从未注册 reader/export —— **已被 TASK-038 修复**。剩余的同类残留是 TASK-039 的 `clean_probe` 注入点。
- 新增包 `src/application/maintenance/**`、`src/application/importing/documents/**`、`src/infrastructure/imaging/**` 归属合理，未把 Qt/DB 依赖带进 application 层。

**本轴小结**：0 项缺陷；1 项**已登记的跨白名单残留**（TASK-039 注入点，见裁决 #1）。本轴最严重项 = 该残留。

## Verification

轴状态：**`executed`**。

| 场景 | 方法 | 结果 |
|---|---|---|
| **独立全仓复跑** | PowerShell + `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`，`-q -p no:cacheprovider -rs` | **PASS 781 passed / 6 skipped**（exit 0）；6 条 skip 全为既有 `tests/network` `openssl unavailable` |
| 删除/依赖/Schema 审计 | `git diff --diff-filter=D`、`requirements.txt` diff、`schema|migration` 路径扫描 | **PASS** 无删除、依赖仅 +`pypdfium2==5.13.0`、Schema 0 命中 |
| 逐切片边界 | `git diff --name-only <merge>^1 <merge>` × 8 | **PASS** 全在白名单内 |
| 5 处高风险深挖 | 读代码 + 探针（单一写者、tile 带宽门、5 个 context property、purge 只碰受控数据、probe 未注入等价） | **PASS** 主张与实现一致 |
| 未验证项 | 各切片自身的 ≥5 次 full-suite 日志（抽样）；EXIT=127 异常（不可复现）；7 份窗口内 Review 的逐行内容 | **未验证（如实标注）** |

**口径勘误（P3，已处置）**：窗口第一轮报告把 `737/6 PS` 与 `764/0 GB` 并排当作基线增量（后者为 Git-Bash 继承 PATH 下 openssl 可用、6 条 network skip 转为通过），**易被误读为"skip 被消除"**。经我核对：**总收集数一致、无屏蔽、无删除**；作者已在第二轮指令包与本复审 brief 中统一口径。**本复审以 PowerShell 口径 781/6 为准。**

**四轴结论（逐轴声明，不跨轴排名）**

- **Standards：`executed`** —— 0 硬性违反；1×P3（`importorskip` 已披露）。本轴最严重项 = 该 P3。
- **Spec：`executed`** —— 7/7 维持 `approved`；0 缺失 / 0 scope creep / 0 实现有误。本轴最严重项 = 无。
- **Architecture：`executed`** —— 单一写者、分层守卫、QML 边界均成立；1 项已登记的跨白名单残留。本轴最严重项 = 该残留。
- **Verification：`executed`** —— 独立全仓 781/6、边界与依赖审计通过、5 处高风险深挖通过；1×P3 口径勘误；3 项未验证已标注。本轴最严重项 = 口径勘误（P3）。

**P0/P1：0 项。**

## Findings

| ID | 级别 | 内容 | 处置 |
|---|---|---|---|
| P-01 | P3 | 新增模块级 `pytest.importorskip("PySide6")`（providers full-chain 用例）：属 skip 声明；在声明 venv 中不生效（PySide6 已装），与既有先例一致 | **accepted + 登记**：未来优先"带理由的显式 skipif/fixture"，或在 Task 中预先声明 |
| P-02 | P3 | 第一轮报告基线口径混用（PS `737/6` vs GB `764/0`） | **fixed（口径已在第二轮统一，本报告以 781/6 为准）** |
| P-03 | P3 | TASK-039 `clean_probe` 的生产注入未实现（白名单外）→ 生产 render-only 命令仍走既有 `BLOCKED` 行为（**不比修前差**） | **deferred → 新小切片**（见裁决 #1） |
| P-04 | P3 | 修前对照中 1 次全仓 96% 处 `EXIT=127`（无 summary、复跑未再现） | **open（不可复现，如实登记）**：与 flaky 分开跟踪 |
| P-05 | P3 | TASK-021 三个子集（备份/恢复、缓存/版本/模型清理、日志/诊断包）冻结未做 | **deferred → 排期**（见裁决 #3） |

## 复审裁决（三项，作者在 brief 中请求）

1. **TASK-039 生产注入点** → **批准开一个 scope 明确的小切片**：`src/bootstrap/app.py` 注入 `clean_probe`（一行接线）+ 装配断言 + 回归；**必须走正常流程**（非 ZCode 作者 Review）。**不必急修**：未注入前生产行为与修前**逐字节等价**（不倒退），故按队列排期即可。
2. **TASK-021 R-001（P2）** → **认可窗口内修订收口**（`0fe634f`，复审 `79ec0d2`，复现 + 终态 7/7）。我另行核对 `trash.py` 的 R-001 修法（batch 只记录**实际**软删除的 id + 同毫秒 `deleted_at` 加固）**成立**，**不推翻、不重开**。
3. **排期** → 建议顺序：**① TASK-039 注入切片**（小、闭合一个已登记缺陷）→ **② TASK-021 的备份/恢复子集**（数据安全相关、优先级高于清理/日志）→ **③ TASK-021 缓存/清理与日志/诊断子集** → **④ 两项依赖裁决落地后**再排 MOBI 与超大 webtoon 流式解码。

## 结论

**窗口内 7 项 `approved_subagent` 集成全部维持为 `approved`（post-hoc）——无推翻、无重开、无降级。** 窗口交付**真实、边界合规、失败与能力缺口均如实登记**（3 处 `BLOCKED` 未记 PASS、1 处不可复现异常主动披露），并且把最大的既有缺口（reader/export 从未装配）**发现并修复**。窗口规则中"同体审查"的代价由本复审吸收。

**剩余风险**：P-03（TASK-039 注入点，不倒退）、P-05（TASK-021 三个子集未做）、两项**用户待裁决依赖**（MOBI 解析、超大 webtoon 流式解码）、P-04（不可复现异常）。

**待补**：本复审由 Codex 执行；按窗口条款，**DeepSeek Harness 的外部独立复审仍应补做**（尤其 `4d0f932` 单一写者与 `b940497` 用户数据保护两处），结论记入审核记录。

---

## 勘误（2026-09-18，DSH 外部复审之后）

DSH 已完成外部独立复审：[POSTHOC-WINDOW-DSH-2026-09-18](POSTHOC-WINDOW-DSH-2026-09-18.md)。**本文 Spec 轴「0 缺失 / 0 scope creep / 0 实现有误」的第三项被修正为 2 项 P1 实现缺陷**；两项均经**我独立复现确认**（非仅采信报告）：

1. **F-1（P1）PDF 红蓝通道互换** —— `src/infrastructure/importing.py:165-174` 把 pdfium 的 `BGR` 缓冲包成 `Format_RGB888`。**我的复现**：纯红 PDF 经生产 `PdfiumDocumentRaster(scale=2.0)` 渲染 → 解码中心像素 **RGBA=(0,0,255,255)**（红变蓝）；pdfium 侧 `mode=BGR`、`stride=600=w*3`、原始中心字节 `(0,0,255)`。**我漏判的原因**：只核了尺寸与 typed 错误，**没有任何像素断言**。
2. **F-2（P1）purge 的 FK 图不完整 + 先删文件后删行** —— `library.py:432-457` 只处理 `region_revisions → regions → pages`，漏掉 5 张引用 `pages` 的表（全部 `NO ACTION`）。**我的复现**：`purge_batch` → `IntegrityError: FOREIGN KEY constraint failed`；随后 `managed file after: False`（文件已消失）、`page row after: 1`、`batches in ledger: 1`、`restore_batch` → **活页指向缺失文件**。**我漏判的原因**：只读了 `purge_pages` 的代码与其 docstring 自述，**没有枚举 `PRAGMA foreign_key_list`**，且当时"5 处高风险深挖"全部以读码为主，未做**行为级验证**。

**口径修正**：本文 Spec 轴结论 → **「0 缺失 / 0 scope creep / 2 项实现有误（F-1、F-2）」**。**维持不变的部分**：7 项集成的**边界合规**（白名单 0 越界）、**诚实性**（3 处 `BLOCKED` 未记 PASS、异常主动披露）、**P0 单一写者约束**（DSH 亦独立复核成立）、无删除/依赖仅获批 1 行/0 Schema/0 新增有效 skip。

**对本文两处具体主张的修正**：①文内对 TASK-021 的 approved 主张（"purge 只删行并自述…"）**在"行依赖完整性 / 生成资产删除范围"范围内不成立**（源文件保护部分仍成立）；②文内 TASK-020 相关结论**未覆盖 tile 落盘几何与声明不符**（F-4）。两处均已在其对应 Review 文件中追加勘误。

**F-3～F-14 的归属裁定（Codex）**

| Findings | 归属切片 | 依据 |
|---|---|---|
| **F-1(P1)** + F-3(P2) + F-9(P3) | [TASK-043](../tasks/TASK-043.md)（TASK-023 修订尾项） | 同在文档导入血缘 |
| **F-2(P1)** + F-6/F-7/F-10(P3) | [TASK-044](../tasks/TASK-044.md)（TASK-021 修订尾项） | 同在 trash/purge 血缘；**接线任何 purge UI 前必须完成** |
| F-4/F-5(P2) + F-8/F-11/F-13/F-14(P3) | [TASK-045](../tasks/TASK-045.md)（TASK-020/038 修订尾项） | 同在 webtoon 分块/显示与装配血缘 |
| F-12(P3) | **并入 TASK-040**（`clean_probe` 注入，**仍未释放**，待用户决定） | 其口径修正与注入同一切片最自然 |

**流程性采纳**（来自 DSH §4.3 的建议）：①"光栅化/图像适配器必须有**像素级断言**"；②"硬删/级联路径必须**枚举全部引用表**"；③"**接线断言**（能力已实现但生产不可达）应纳入 Task 模板 AC 清单"——本窗口已三次出现同类问题（tile、文档导入、clean_probe），值得写进模板。
