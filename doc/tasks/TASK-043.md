---
id: TASK-043
title: TASK-023 修订尾项（F-1 PDF 红蓝通道互换 P1 + F-3 失败余页 + F-9 依赖导入位置）
kind: bugfix
status: in_progress
approval: approved_by_user
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-023]
base_commit: 1c171dcdeafc1cbffe6111d503dd0cd598e22dea
branch: agent/deepseek/TASK-043-import-fixes
worktree: G:/CODEX/New Manga.worktrees/TASK-043-deepseek
integration_commit: null
---

# TASK-043：TASK-023 修订尾项（F-1 / F-3 / F-9）

**READY（2026-09-18，Codex 依外部复审裁定开立）**：Owner=`DeepSeek Harness`（**非缺陷作者**）、Reviewer=`Codex`（**非作者**）、base=`1c171dc`。开工前置 `in_progress`。

来源：`doc/reviews/POSTHOC-WINDOW-DSH-2026-09-18.md` 的 **F-1(P1) / F-3(P2) / F-9(P3)** + `doc/code-review-5f3c115-zcode-window-7-integrations.json`。**Codex 已独立复现 F-1**（见 AC ①）。

## AC ①（F-1，P1，核心）：PDF 光栅化红蓝通道互换

- 缺陷：`src/infrastructure/importing.py:165-174` 把 pdfium 的 `BGR` 缓冲（`mode=BGR`、`stride == width*3`）包成 `QImage.Format_RGB888`（该格式期望 R,G,B）→**每页 PDF 红蓝互换**，错误像素被写入 Managed Copy 并计入 `source_hash`。
- **Codex 独立复现（2026-09-18）**：纯红 PDF（`1 0 0 rg`）经生产 `PdfiumDocumentRaster(scale=2.0)` 渲染后，解码中心像素 **RGBA = (0,0,255,255)**；pdfium 侧 `mode=BGR`、`stride=600=w*3`、原始中心字节 `(0,0,255)`（B,G,R）。
- 修法：BGR 分支改用 **`QImage.Format_BGR888`**（Qt ≥ 5.14；**本环境 PySide6 6.11.2 已确认存在该枚举**）。若 `BGRA` 分支在本环境不可达，须在 Handoff **写明其字节序正确性的依据**（不得只改一条分支而无交代）。
- **必测（用户指定）**：新增"**纯红 PDF → 像素为红**"回归——走生产光栅器渲染已知纯色 PDF，解码落盘 PNG 并断言中心像素为红（±容差）；**不得**只断言尺寸（本缺陷正是在"只核尺寸"下漏掉的）。
- **验收惯例（写入 Handoff，供后续 Task 引用）**：光栅化适配器**必须有像素级断言**。

## AC ②（F-3，P2）：文档导入失败/取消时的余页状态

- 缺陷：`src/application/importing/documents/service.py:142-147/162-166/191` 在某页失败时 `break`，其余页**既非 failed 也非 pending**（只有取消路径才写 pending）；且 **0 页文档被报为 `skipped_duplicates`**（误导性结果）。
- 修法：失败与取消**都**把 `page_no+1..page_count` 追加为 `pending`；**0 页文档**用独立 typed 结果/错误（如 `INVALID_DOCUMENT`）表达，不得混入 `skipped_duplicates`。
- 补回归：中途失败 → 余页 pending；取消 → 余页 pending；空文档 → typed 错误。

## AC ③（F-9，P3）：缺依赖不得抛裸 `ImportError`

- 缺陷：`src/infrastructure/importing.py:126` 的 `import pypdfium2` 在 `try` **之外** → 缺依赖时抛裸 `ImportError`，与同文件 `:114-117` 承诺的 typed 错误不符。
- 修法：移入 `try` 并包成 typed `DocumentDecodeError`（与既有错误类型体系一致）；补"依赖不可用"用例（monkeypatch/子进程模拟导入失败均可）。

## AC ④（回归与证据）

- **F-1 新增像素断言、F-3 新增余页用例**均对**修前代码**失败（把新测试放 base `1c171dc` 的 `src` 上跑并留证 = 判别力）。
- `tests/import_formats`、`tests/library`、`tests/providers` 与全仓 **passed 不减少**；全仓 **≥5 次**逐次记录（**同一 shell + 同一 venv**：PowerShell + `TASK-012-py312`），**passed/skipped 分列并给出 skip 原因**（6 条应为既有 `tests/network` `openssl unavailable`）。
- 不得新增 `skip`/`xfail`；不得放宽既有断言。

## AC ⑤

交付 Handoff、取证（含修前/修后像素证据），经**非作者** Review（四轴 + passed/skipped 分列）与 Codex 集成后才能 done；并在 STATUS 记录 F-1/F-3/F-9 关闭。

## 允许修改范围

- `src/infrastructure/importing.py`
- `src/application/importing/documents/**`
- `tests/import_formats/**`、`tests/library/**`
- `doc/tasks/TASK-043.md`、`doc/handoffs/TASK-043-*.md`、`verification/TASK-043/**`、`doc/STATUS.md`（仅登记关闭）

## 禁止范围

- 不得改 Schema/migration、依赖清单、seam 本体、`AGENTS.md`、其他 Task。
- **不得以"已登记"为由跳过 F-1**；不得只改分支而不动断言；不得把缺陷记成"已知/暂不处理"。
- 不处理 MOBI（[TASK-041](TASK-041.md) 已释放）、超大 webtoon（[TASK-042](TASK-042.md) 已释放）。

## 依赖、风险与阻塞

硬依赖：TASK-023（`done`）。风险：`Format_BGR888` 与 `Format_RGB888` 在**字节序**上的差异须在测试里以**已知颜色**证明（不得只靠断言"格式名正确"）。

## 交付与运行记录

- Handoff：[TASK-043-d8e9406](../handoffs/TASK-043-d8e9406.md)（delivery_head=`d8e9406`）。Review：尚无（待 Codex 按 §6 执行**非作者** Review）。
- 实际执行/测试（`TASK-012-py312`，Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1，`PYTHONDONTWRITEBYTECODE=1`，全部 `-p no:cacheprovider`）：
  - 证据总表：[verification/TASK-043/README.md](../../verification/TASK-043/README.md)；修前/修后像素：[pixels-pre-fix.txt](../../verification/TASK-043/pixels-pre-fix.txt) / [pixels-post-fix.txt](../../verification/TASK-043/pixels-post-fix.txt)（两棵树的 `PYTHONPATH` 选择，日志首行打印实际加载的 `src` 树）；BGRA 依据：[bgra-basis.txt](../../verification/TASK-043/bgra-basis.txt)；恒等重构：[pdf-builder-identity.txt](../../verification/TASK-043/pdf-builder-identity.txt)；全仓逐次：[full-suite-runs.log](../../verification/TASK-043/full-suite-runs.log)；基线：[baseline-master-c5aa664.txt](../../verification/TASK-043/baseline-master-c5aa664.txt)；skip 原因：[skip-reasons.txt](../../verification/TASK-043/skip-reasons.txt)。
  - 定向：`tests/import_formats tests/library tests/providers` → **225 passed / 0 skipped**（16 / 40 / 169）；`tests/import_formats tests/library` → 56 passed。
  - 全仓：**802 passed / 6 skipped ×5 次**（逐次 exit 0）；独立基线 master `c5aa664` → **792 passed / 6 skipped** ⇒ +10 = 恰好新增 10 例；6 条 skip 全部为既有 `tests/network` `openssl unavailable`（`test_connection_tester.py:106`、`test_transport_tls.py:39/47/62/69/83`）。
  - 判别力：新测试放到 base `c5aa664` 的 `src` 上 → **8 failed / 8 passed**（`-rf` 逐条 node id + 树溯源）。修前也通过的两项（F-1 `[green]` 在 R↔B 互换下恒等；生产 0 页 PDF 本就 typed 拒绝）已声明为守卫、不计入判别力。
  - 边界：改动恰为 `src/infrastructure/importing.py`、`src/application/importing/documents/service.py`、`src/application/importing/documents/ports.py`、`tests/import_formats/test_document_import.py`、`verification/TASK-043/**`，**越界 0**；`git diff --check` 退出码 0；**未新增 skip/xfail**；既有断言零删除（`tests/` 的删除行仅为 `minimal_pdf` 尾部搬入 `_assemble_pdf`，字节恒等已证）。
- **待 Reviewer 裁定**：① F-3 的 `cancelled` 语义收紧（原 `bool(pending)` → 真实取消）；② 失败余页复用 `pending_after_cancel` 字段名（该端口文件 `application/importing/images/ports.py` 不在本 Task 白名单，未改名）；③ F-9 新报告码 `MISSING_DEPENDENCY` 与 `except (ImportError, OSError)` 的宽度；④ **修复前已导入的 PDF 页不会自动修复**（Managed Copy 内仍是互换像素，且其 `source_hash` 与修复后不一致 → 重新导入不会去重）是否另开切片。
- **最近状态（当前，唯一）**：2026-09-18 **`in_progress`（实现已交付，待非作者 Review）**——F-1 / F-3 / F-9 已实现并取证，delivery head `d8e9406`，fixed base `1c171dc`（开工先 `git merge master` → `c5aa664`，fast-forward 无冲突）。**未 push；未改 Schema/migration、依赖清单、pipeline seam、路由判定/SFX、`AGENTS.md`、其他 Task；`doc/STATUS.md` 未改**（按 AC ⑤，F-1/F-3/F-9 的关闭登记发生在 Review 与集成之后，作者阶段不预写）。本 Task **尚未 done**、三项缺陷**尚未"关闭"**。
- 历史状态（2026-09-18）：由 Codex 依 DSH 外部复审 `doc/reviews/POSTHOC-WINDOW-DSH-2026-09-18.md` 的 F-1/F-3/F-9 开立为 `ready`（Owner=`DeepSeek Harness`、Reviewer=`Codex`、base=`1c171dc`）；本次开工置 `in_progress`。

