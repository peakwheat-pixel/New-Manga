---
id: TASK-045
title: TASK-020/038 修订尾项（F-4 tile 落盘几何 + F-5 翻页旧图 + F-8 Slot result + F-11 坐标口径 + F-13/F-14 注释口径）
kind: bugfix
status: ready
approval: approved_by_user
suggested_owner: DeepSeek Harness
owner: DeepSeek Harness
reviewer: Codex
depends_on: [TASK-020, TASK-038]
base_commit: 1c171dcdeafc1cbffe6111d503dd0cd598e22dea
branch: agent/deepseek/TASK-045-webtoon-display-fixes
worktree: G:/CODEX/New Manga.worktrees/TASK-045-deepseek
integration_commit: null
---

# TASK-045：TASK-020/038 修订尾项（F-4 / F-5 / F-8 / F-11 / F-13 / F-14）

**READY（2026-09-18，Codex 依外部复审裁定开立）**：Owner=`DeepSeek Harness`（**非缺陷作者**）、Reviewer=`Codex`（**非作者**）、base=`1c171dc`。开工前置 `in_progress`。

## AC ①（F-4，P2）：tile 落盘几何与声明不符

- 缺陷：`webtoon_tiles.py:99-108/234-262` + `ReaderView.qml:245-254` —— 落盘 PNG 是**含 overlap 的解码窗**（实测 400×832 vs 声明 800、400×3064 vs 3000），而模块注释称 "displayed band stays [content_top, content_bottom)"、"dedup by construction"；Delegate 又用 `PreserveAspectFit` 在声明盒内缩放 → 非首块被 letterbox 且顶部重复上一带。
- 修法（**二选一，但必须让"代码、注释、断言"三者一致**）：①落盘前裁到 `[content_top, content_bottom)`（overlap 仅作**解码上下文**）；或②改声明口径为"落盘含 overlap"+ 相应修正显示与注释。
- 必测：**落盘尺寸 == 声明高度** 的几何断言（或按所选口径的等价断言）。

## AC ②（F-5，P2）：分块模式翻页显示旧图

- 缺陷：`viewmodel.py:112/128/246/252/258` 的 `_rebuild_tiles()` 只挂在 `openChapter`/`setMode`，**翻页槽不重建**；且工具栏"上/下一页"未按 `vertical` 门控（键盘翻页已门控）→ 分块模式"显示旧页像素、进度记新页"。
- 修法：换页槽末尾重建瓦片；分块模式下禁用/门控工具栏翻页（与键盘一致）。
- 证据：**首选可机器验证的断言**（换页后瓦片集合对应新页）；**若只能靠实机 GUI 观察，必须在 Handoff 明确声明该局限**（外部复审已登记"未做真机截图确认"），不得以"码面推导"冒充已验证。

## AC ③（F-8，P3）：`@Slot` 缺 `result=` 致 QML 得 `undefined`

- `src/ui/viewmodels/bookshelf/viewmodel.py:370-371`：`@Slot(str, list)` 未声明 `result=` → 元对象 `returnType=void`；同文件 `:285/:311/:349` 先例均带 `result=`。
- 修法：补 `result="QVariantMap"`（与先例一致）并接线验证。

## AC ④（F-11，P3）：`requestTiles` 的坐标口径

- `ReaderView.qml:231-235` 传入的是**显示像素** `contentY`，而网格按**页像素**解释；`pagePixelWidth/Height` 已暴露却无人使用 → 视宽≠页宽时请求带偏移（空白带）。
- 修法：调用处换算，或给 `requestTiles` 增加 scale 参数；二选一并在注释/断言中固定口径。

## AC ⑤（F-13 / F-14，P3）：注释与实现一致

- **F-13**：`webtoon_tiles.py:14-18/186-188` 称 `setClipRect` 使峰值内存≈一个 tile —— 与本仓库自身测试结论（"`setClipRect` 不改变该行为，handler 先分配整图再裁剪"）冲突。改为："**整图解码是根因**，`setClipRect` 无效"（与 [TASK-042](TASK-042.md) 的立项前提一致）。
- **F-14**：`webtoon_tiles.py:189/289-295` 称 key 含 "source hash"，实际为**路径+大小+几何**、无语义内容哈希 → 同尺寸原地改写会命中陈旧瓦片。修注释或补内容哈希；与已登记的 TASK-020 R-004 合并处置。

## AC ⑥（回归与证据）

- 新增/更新的断言对**修前代码**失败（留判别力证据）。
- `tests/reading_export`、`tests/core`、`tests/ui_shell`、`tests/workbench` 与全仓 **passed 不减少**；全仓 **≥5 次**逐次记录（同一 shell + 同一 venv），**passed/skipped 分列 + skip 原因**。
- 不得新增 `skip`/`xfail`；不得放宽既有断言（尤其 TASK-020 已交付的几何/带宽断言与 TASK-037 的滚动断言）。

## AC ⑦

交付 Handoff、取证，经**非作者** Review 与 Codex 集成后才能 done；并在 STATUS 记录 F-4/F-5/F-8/F-11/F-13/F-14 关闭。

## 允许修改范围

- `src/infrastructure/imaging/**`
- `src/ui/viewmodels/reader/**`、`src/ui/viewmodels/bookshelf/**`
- `src/ui/qml/reader/ReaderView.qml`
- `tests/reading_export/**`、`tests/core/**`
- `doc/tasks/TASK-045.md`、`doc/handoffs/TASK-045-*.md`、`verification/TASK-045/**`、`doc/STATUS.md`（仅登记关闭）

## 禁止范围

- 不得改 Schema/migration、依赖清单、seam 本体、`AGENTS.md`、其他 Task；不得改 `src/ui/qml/` 中除 `reader/ReaderView.qml` 之外的文件。
- 不得以"视觉问题无法自动断言"为由跳过 F-4/F-5 —— 必须先尝试机器可验证的断言，确不可行则显式声明局限。
- 不得与 [TASK-042](TASK-042.md)（超大页带状解码）混做：本 Task 只修**显示几何/翻页/接线口径**。

## 依赖、风险与阻塞

硬依赖：TASK-020、TASK-038（均 `done`）。风险：F-4 的修法会改变落盘尺寸 → 须同步核对 tile 缓存 key 与已登记断言，避免"改了落盘但缓存仍按旧几何命中"。

## 交付与运行记录

- Handoff：[TASK-045-1171bc5](../handoffs/TASK-045-1171bc5.md)（delivery_head=`1171bc5`，实现两提交 `602cca8` + `1171bc5`）。Review：尚无（待 Codex 按 §6 执行**非作者** Review）。
- 实际执行/测试（`TASK-012-py312`，Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1，`PYTHONDONTWRITEBYTECODE=1`，全部 `-p no:cacheprovider`）：
  - 证据总表：[verification/TASK-045/README.md](../../verification/TASK-045/README.md)；AC ⑨ 内存构成：[memory-and-fixture-probe.txt](../../verification/TASK-045/memory-and-fixture-probe.txt)；AC ⑩ rewind 成本：[rewind-cost-probe.txt](../../verification/TASK-045/rewind-cost-probe.txt)；F-13/F-14 注释核查：[comment-drift-check.txt](../../verification/TASK-045/comment-drift-check.txt)；全仓逐次：[full-suite-runs.log](../../verification/TASK-045/full-suite-runs.log)；基线：[baseline-master-6ea3dd3.txt](../../verification/TASK-045/baseline-master-6ea3dd3.txt)。
  - 定向：`tests/reading_export tests/core` = **130 passed / 0 skipped**；QML 契约 10 passed。
  - 全仓：**827 passed / 6 skipped ×5 次**（另 run 6 给出逐条 skip 原因），逐次 exit 0；独立基线 master `6ea3dd3` = **813 passed / 6 skipped** ⇒ +14 = 恰好新增 14 例；逐目录 reading_export 106/93、core 24/23、ui_shell 46/46、workbench 51/51，AC ⑥ 聚合 227/213；6 条 skip 全为既有 `tests/network` `openssl unavailable`。
  - 判别力（**两棵树**：`git archive 6ea3dd3 src pytest.ini` + 本 worktree 最终 `tests/`）：**10 failed / 120 passed**，逐条原因见 [pre-fix-failure-summary.txt](../../verification/TASK-045/pre-fix-failure-summary.txt)；3 例守卫（per-tile rewind 计量、内存构成、真实编码器超大页）修前亦通过，已声明不计入判别力。
  - 边界：作者自有改动 23 文件、+1919/−38，**0 文件删除、越界 0**；`src/ui/qml/` 仅改 `reader/ReaderView.qml`；未改 Schema/migration、依赖清单、seam、`AGENTS.md`、其他 Task；`git diff --check` 退出码 0；未新增 skip/xfail、未放宽既有断言。
- **新发现（先于本 Task 存在，已在本 Task 内修复并留证）**：`ReaderView.qml` 的瓦片 `Repeater` 使用未限定名 `model.tiles`，而 `model` 在该作用域解析为 **Repeater 自身的 `model` 属性** ⇒ delegate 从未创建，同时整图 `<Image>` 因 `tilesActive` 为真被隐藏 ⇒ **分块（webtoon tiled）视图自 TASK-020 起渲染空白**（而非 F-5 描述的"旧图"）。修复为 `rv.model.tiles`；隔离证据 [pre-fix-delegate-diagnosis.txt](../../verification/TASK-045/pre-fix-delegate-diagnosis.txt)。归属与是否需要更正 TASK-020/038 的 Review 结论请 Reviewer 裁定。
- **AC ⑩ 的前提被实测推翻（请 Reviewer 裁定）**：`visible_tiles` 升序只保证"不向后跳"；生产 `overlap=64` 使**每个非首块的窗口起点落在游标之前**，故每块各 rewind 一次并从 row 0 重扫（400×20000 全页扫掠 24 次 rewind；1600×8000 Qt 编码页单块 4.53s → 两块 14.24s）。TASK-042 Handoff 的"全页只需一次顺序扫描"仅在 `overlap=0` 成立。本 Task 按 AC 只做**文档化 + 实测**；解码策略与生产 `overlap`（`src/bootstrap/app.py:547`，不在白名单）未动。
- **AC ⑨ 口径修正**：实测构成为**常驻压缩源 + 2×最大 IDAT 块 + O(带)**（单块编码时块项主导，400×10000 实测额外 24.1MB ≈ 23× 带宽；1000 行分块时 5.7MB），修正 R-02 的"≈3–4× 带宽"表述。
- **F-8 如实说明**：契约（`result="QVariantMap"`）与元对象断言已补，接线由 `tests/core/test_bootstrap.py` 既有断言继续覆盖；但当前 QML 侧只有 `importFilesFromUrls` 有调用方，`importDocumentsFromUrls` 尚无 QML 入口——本修复保证一旦接线即得 dict 而非 `undefined`。
- **最近状态（当前，唯一）**：2026-09-18 **`in_progress`（实现已交付，待非作者 Review）**——F-4/F-5/F-8/F-11/F-13/F-14 与 TASK-042 的 R-01～R-04 已实现并取证，delivery head `1171bc5`，fixed base `1c171dc`（开工先 `git merge master` → `6ea3dd3`）。**集成注意**：master 其后已推进到 `fe59360`（TASK-041 复审），集成前需再 merge 一次。**未 push；`doc/STATUS.md` 未改**（按 AC ⑦，关闭登记在 Review/集成之后）。本 Task **尚未 done**、各项**尚未"关闭"**。
- 历史状态（2026-09-18）：由 Codex 依 DSH 外部复审的 F-4/F-5/F-8/F-11/F-13/F-14 开立为 `ready`（base=`1c171dc`），随后并入 TASK-042 复审的 R-01～R-04（AC ⑧～⑪）；本次开工置 `in_progress`。

## 追加范围（2026-09-18，由 TASK-042 Review 的 findings 并入）

TASK-042 复审产生 4 项 P3（均不影响其批准），因同属 webtoon/imaging 血缘且本 Task 白名单已覆盖 `src/infrastructure/imaging/**` 与 `tests/reading_export/**`，**并入本 Task 一并收口**：

- [ ] **AC ⑧（= R-01）typed 化损坏载荷**：`streaming_png.py::_pump` 把 `decompress()` 的 `zlib.error` 包成 typed `StreamingPngError`（如 `INVALID_PNG`/`CORRUPT_DATA`）。现状：`zlib.error` 的 MRO 为 `(zlib.error, Exception)`，**逃出** `viewmodel.py:309/351` 的 `except (OSError, ValueError)`，损坏源文件不再走优雅回退；**失败本身仍是 fail-closed（Adler-32 拦截，不产出错误像素）**。补"容器合法但载荷损坏"用例（TASK-042 的变体矩阵未覆盖此格）。
- [ ] **AC ⑨（= R-02）内存声明精确化**：把 `streaming_png.py` / `webtoon_tiles.py` 的"peak = one decode window / never more than one scanline pair plus the band"改为**实测构成**——"压缩源常驻（`__init__` 的 `read_bytes()`）+ O(带宽)（实测 ≈3–4× 带）"；并说明将来要 O(带) 总量需改为流式读源。
- [ ] **AC ⑩（= R-03）rewind 成本文档化**：在 `ensure_viewport`/`_decode` 写明"`visible_tiles` 升序 ⇒ **每次调用最多一次 rewind**、最坏为以目标带末端为界的一次重扫"，并记入实测（Reviewer 实测：扫 20000 行 0.39 s；回跳 row 12000 0.156 s；回跳 row 0 0.219 s）；如需再加"最近 N 带缓存"。
- [ ] **AC ⑪（= R-04）补"真实编码器 × 超大"覆盖**：新增一个**中尺寸 Qt 编码**夹具（建议 `1600×20000` ≈128 MB rgb32，**低于 Qt 的 ~300 MB 失效门**）走带状读 + 与 Qt 解码的像素一致性，补上"超大页夹具由测试自写 stdlib 写入器（filter 0）生成"留下的覆盖缺口。

→ 对应 TASK-042 Review 的 R-01/R-02/R-03/R-04（[doc/reviews/TASK-042-fc6c649.md](../reviews/TASK-042-fc6c649.md)）。
