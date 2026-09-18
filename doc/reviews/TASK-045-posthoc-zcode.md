# Post-hoc 复审：TASK-045（独立第二意见，ZCode）

```yaml
task: TASK-045（TASK-020/038 尾项 F-4/F-5/F-8/F-11/F-13/F-14 + TASK-042 R-01～R-04）
reviewer: ZCode（非作者；作者=DeepSeek Harness；本切片原 Reviewer=Codex，亦非本人）
commissioned_by: doc/handoffs/POSTHOC-REVIEW-BRIEF-TASK-045.md（master 16f7d75）
worktree: G:\CODEX\New Manga.worktrees\TASK-045-posthoc-zcode（分支 agent/zcode/TASK-045-posthoc）
reviewed_state: cb93d66（收口）；评审期间工作区 fast-forward 至 16f7d75（纯文档提交，
  cb93d66..16f7d75 的 src/tests diff 为空），被审代码面不变
base: 1c171dc（Task 固定 base；实际 merge base = 6ea3dd3）
first_review: doc/reviews/TASK-045-1171bc5.md（changes_requested，R-001 P1）
revision_review: doc/reviews/TASK-045-a165aa3.md（approved）
integration: e2a8f01；close: cb93d66
decision: uphold_with_findings
date: 2026-09-18
```

**decision = `uphold_with_findings`** —— 两轮 Review 的结论（首轮 `changes_requested` → 修订 → `approved`）**全部维持**，7 个靶点无一推翻；另登记 **3 项 P3 观察项**（均有测试锁定或无用户可达路径，**不要求返工**，供后续切片参考）。无 P1/P2、无可复现反例，故不构成 `overturn`；findings 非空，故不写裸 `uphold`。

执行口径：用户 `[$code-review]` 调用（交接包固定 7 靶点）。四轴 = Standards / Spec / Architecture / Verification，逐轴执行、分别报告、**不跨轴排名**。技能第 4 步要求 Standards/Spec 由**并行 sub-agent** 隔离运行；本复审由同一 Reviewer 单遍执行，**偏差在此声明**（与 [TASK-045-1171bc5.md:19](TASK-045-1171bc5.md) 的先例一致；本切片被审面小、靶点由交接包固定，隔离收益有限）。技能第 1 步（issue tracker）不适用：仓库无 tracker，按协议 §6.2 顺序取 Task AC 与两份已入档 Review。

边界遵守：**只读**——本工作区 `src/**`、`tests/**`、Schema、依赖、`AGENTS.md`、其他 Task 全程零改动（`git status` 仅 `verification/TASK-045/posthoc-zcode/` 未跟踪 + 本报告）；未改任何已入档 Review 结论正文；未与 TASK-042/TASK-046 的带状解码/overlap 改动混做；未 push。

## 范围与依据

- 被审对象（交接包固定）：首轮 diff `6ea3dd3..1171bc5`（实现 `602cca8` + `1171bc5`），修订 diff `1171bc5..a165aa3`（实现 `a165aa3`，文档 `a99f10a`）。两份 Review 分列的作者自有生产面：`webtoon_tiles.py`、`streaming_png.py`、`reader/viewmodel.py`、`bookshelf/viewmodel.py`、`ReaderView.qml`。
- 实际读过的调用链：`ReaderView.qml`（Repeater/delegate/`tileScale()`/`onContentYChanged`/`restoreSavedOffset`）→ `ReaderViewModel`（7 个页/模式入口 → `_rebuild_tiles` → `_serve_viewport` → `ensure_viewport` → `tile_file` → `_decode` → `grid.decode_rect` + `StreamingPngReader.read_band` → `TileCache`/磁盘瓦片）。
- 证据来源分列见下文各靶点与「Verification 轴」；作者/原 Reviewer 证据入口 = `verification/TASK-045/{README.md, review-1171bc5/, review-a165aa3/}`。

## 七个靶点的复审结果

### 靶点 1（优先）：F-4 逐行等价在多过滤器页上的重验 —— **成立，判别力成立**

**空白确认**：作者的 F-4 锁定用例 `test_materialised_tiles_carry_exactly_the_declared_band` 与原 Reviewer 探针使用的页均为**手写 filter-0** PNG（每行单色）；作者在 `602cca8` 补的 AC⑪（`test_qt_encoded_oversized_page_bands_match_qt_pixels`）覆盖了**真实编码器 × 分带读取**，但「**落盘 tile 文件 × 多过滤器**」这一交叉点在修复时无直接覆盖。

**独立复跑**（`verification/TASK-045/posthoc-zcode/f4_multifilter_probe.py`，本 Reviewer 编写）：

- **A 段**：Qt/libpng 真实编码页 800×4000 RGB，内容分四带（横向渐变/纵向重复/平滑混合/确定性噪声）逼出混合过滤器；从编码文件恢复的逐行 filter 直方图 = **{None: 308, Sub: 215, Up: 2067, Average: 239, Paeth: 1171}——五种过滤器全部出现**。经生产 `TiledPageRasterizer`（tile_height=1500, overlap=64，覆盖首/中/末 tile）：每个 tile 文件高 == 声明 `content_height`；Qt 参照解码下逐行逐像素 == 页对应行；全部 tile 拼接 == 整页（4000 行，无重复无缺失）。→ `f4-multifilter-probe-current.log`（exit 0）。
- **B 段**：手工逐行指定过滤器（0,1,2,3,4 循环，每种恰好 90 行）× 四种通道布局（RGB/RGBA/Gray/Gray+Alpha），tile_height=90、overlap=13 加密 tile 边界：文件高/像素/拼接断言全过。→ 同日志。
- **C 段（行为记录）**：`read_band(past EOF)` → typed `OUT_OF_RANGE`；跨页尾请求静默钳制到 EOF（见 P3-3）。
- **判别力**：同一探针在修前树 `6ea3dd3`（临时 detached worktree，已删）上 **exit 1**：tile 1 文件高 1564（=1500+overlap）、tile 2 高 1064、拼接 4128 行（=4000+2×64 重复行）——正是 F-4 修复消灭的症状。→ `f4-multifilter-probe-pre-f4-6ea3dd3.log`。
- **R-004 无误报**（靶点 6 一部分）：A/B 两段全 tile 解码零 `OSError` 短读硬失败误触发。

**复用**：作者判别力矩阵 `pre-fix-tests.txt`（10 failed @ 6ea3dd3 归档树，含 `tile 1: file height 864 != declared 800`），与本探针的失败形态互相印证。

### 靶点 2：触发面不变式 —— **成立**

**独立复跑（代码级穷举）**：`reader/viewmodel.py` 中改变"当前页来源"的全部入口 —— `openChapter` / `continueReading` / `restartFromBeginning` / `setMode` / `nextPage`（F-5）/ `previousPage` / `jumpToPage` —— **7 个无一例外**在状态变更后调用 `_rebuild_tiles()`，后者统一负责换 rasterizer、重建行、并经 `_serve_viewport` 物化记忆视口（R-001）。`_viewport_for_new_page` 的钳制（`span` 保持、`top ∈ [0, page_height−span]`）在短页上不产生空窗。

**R-101（(0,0) 双重语义）复核**：`visible_tiles(0, 0, prefetch=1)` 依赖 `(viewport_bottom − 1)` 的 floor-division 负数语义（`(−1)//4000 = −1` 被 `max(first, …)` 拉回 0）得到「tile 0 + 1 预取」——**行为正确且非空窗**，但该正确性是隐式的（见 P3-1）。锁定测试：`test_request_tiles_converts_display_pixels_to_page_pixels`（记录首项 `(0,0)`）与 `test_opening_a_tiled_chapter_serves_the_first_band_by_itself`（锁定 `[0,1]`），本复审定向复跑通过。

**复用**：原 Reviewer 修订探针复跑（`review-a165aa3/reviewer-probe-on-revision.txt`：B1 打开 → 2 个 page-1 瓦片、B3 翻页 → 2 个 page-2 瓦片且与 page-1 不相交）——未重跑其探针脚本，以本复审 QML 面审计与作者测试复跑覆盖同一命题。

### 靶点 3：断言强度 —— **5 处全部为加强或等价替换，无放宽**

**独立复跑（`git diff 1171bc5..a165aa3 -- tests/` 逐行审计）**：

1. `test_tiled_reader_serves_viewport_tiles`：`all(not url)` → `恰好 [0,1] 有 url`（精确集合，且隐含 2/3 无 url）——**加强**。
2. `test_next_page_rebuilds_the_tiles_for_the_new_page`：删去「翻页后全空」中间态断言，代之以 `served == [0,1]` + 与首页文件 **disjoint** + 文件真实存在——**等价替换且更强**（旧断言锁的是 R-001 修前行为，修后不再成立）。
3. `test_jump_to_page_rebuilds_the_tiles_too`：`all(url=="")` → `served 非空 + disjoint`——**加强**。
4. `test_request_tiles_converts_display_pixels_to_page_pixels`：新增 `(0,0)` bootstrap 首项——**加强**（同时锁定 R-101 语义）。
5. 新用例 ×4（VM 2 + QML 2）：QML 两例**从不调用 `requestTiles`**（docstring 自证）；"因错误原因通过"排查——`served_tile_sources` 在 host 为 None 时返回空 → pump 超时失败（不会假通过）；翻页用例的 `disjoint(first_page_sources)` 在 Repeater 同步重建下是确定性判定（若 pump 命中旧 delegate，disjoint 立即失败），无 flaky 假通过通道。
6. **判别力**（复用 + 印证）：作者 `revision-pre-fix-tests.txt` 与原 Reviewer `discriminating-revision-tests-vs-1171bc5.txt`（8 failed @ 1171bc5）独立留证，本复审未重跑树间矩阵（修前树已由靶点 1 探针判别力覆盖）。
7. **3s 等待预算**：R-001 的服务在 `openChapter`/`nextPage` slot 内同步完成，QML 侧仅剩 delegate 创建的 1–2 跳事件循环，正常路径 ≪100ms；3s ≈ 30× 余量，且复审轮已记录 5s 版本曾遇 access violation、3s 加固后未复现——预算合理。

### 靶点 4：QML 面 —— **成立**

**独立复跑（`ReaderView.qml` 全文审计）**：

- Repeater `model: tilesHost.visible && rv.model ? rv.model.tiles : []`——两处限定名齐全（靶点 5 探针验证语义）；delegate `height = modelData.height × tilesHost.width / modelData.pageWidth` 与 `tileScale() = tilesHost.width / model.pagePixelWidth` 为**同一比值**（F-11 自洽），且 tile 文件宽高比 == 盒子宽高比（F-4 的直接 UI 后果），`fillMode: PreserveAspectFit` 无 letterbox。
- `tileScale()` 对 0 值防退化（`!pagePixelWidth || host.width<=0 → 1.0`）；`requestTiles` 内 `float(scale) or 1.0` 同；`onContentYChanged` 以 `tilesHost.visible`（= `active && model.tilesActive`）作门，`model` 判空隐式成立。
- `restoreSavedOffset` 设置 `contentY` → 经 `onContentYChanged` 自动触发 `requestTiles`，与 VM 侧 R-001 的先行服务形成幂等双保险（文件已存在时 `tile_file` 快速返回）。
- `contentHeight` 取 `tilesHost.childrenRect.height`（delegate 高度不依赖异步加载，恢复偏移不被 clamp 回 0）；`clearTileCache` 在生产 QML **无调用点**（见 P3-2）。
- 未发现其他未限定名/遮蔽残留。

### 靶点 5：Repeater 历史勘误核实 —— **成立（独立复现）**

**独立复跑（git 历史 + 语义探针）**：

- 源码逐版本比对：`7833604`（TASK-020 集成）与 `602cca8` 的 Repeater 均为 `model: visible ? model.tiles : []`（两处未限定）；`1171bc5` 改为 `visible && rv.model ? rv.model.tiles : []`（`model` 已限定、`visible` 仍遮蔽）；`a165aa3` 才两处齐全——与两份 Review 的叙事一致。
- 最小 QML 语义探针（`verification/TASK-045/posthoc-zcode/qml_shadow_probe.py`，本 Reviewer 编写）：同一树并排三种拼写 → **legacy 0 个 delegate / partial（1171bc5 拼写）2 个 / fixed（a165aa3 拼写）2 个**，exit 0 → `qml-shadow-probe.log`。即「TASK-020 拼写下 `model.tiles` 为 undefined、delegate 从未创建」在本 Qt 构建上复现；`visible` 遮蔽的实际后果是守卫空转（而非 0 delegate），与 a165aa3 注释口径一致。

**结论**：原 Reviewer 第 107 行的历史表述更正（TASK-020「tiled 分支已交付」过强、TASK-038 仅「装配可达」）**有据**；已按其承诺以 STATUS/复审尾注登记、未改正文——本复审无需追加勘误。

### 靶点 6：清理与缓存遗留 —— **成立，登记 1 项观察**

- **`clearTileCache()`（R-102）**：代码级核对——清 LRU + `glob("tile-*.png")` 跨代删盘 + 行 URL 清空 + `tilesChanged`；只碰可重建像素，业务真值（progress/regions/render revisions）不在 VM/rasterizer 内。**遗留用户可见后果**：清 URL 后 `contentY` 不变 ⇒ 不自发重发 `requestTiles` ⇒ 视口空白直到滚动/翻页；当前生产 QML 无调用点，无用户可达路径 → **P3-2**。
- **`_TILE_CACHE_FORMAT` 升版（R-005）**：注释如实声明「升版遗留上一代孤儿文件，`clear()` 或人工清目录回收」；`clear()` 的 glob 确实跨代（`tile-*.png` 前缀匹配）——文档化处置成立。
- **`_decode` 短读硬失败（R-004）**：真实 Qt 编码页上零误报（靶点 1 探针 A 段全 tile 通过）；修前树对照（6ea3dd3 无此校验）的失败形态由判别力日志呈现。

### 靶点 7：streaming_png 的 AC⑧/AC⑨ 与 `_pump` —— **成立**

- **AC⑧（复跑锁定测试 + 代码审计）**：`test_corrupt_idat_payload_fails_typed` 真实注入 `zlib.error`（确定性 LCG 改写 IDAT 载荷）→ `CORRUPT_DATA`，并断言 `StreamingPngError` 是 `ValueError` 子类（调用方 `except (OSError, ValueError)` 可见）——本复审定向复跑通过。代码审计：`_pump` 包装点唯一且完备（`zlib.error` 是 decompress 调用的唯一异常源）；`produced == 0` 返回 False → 上层 TRUNCATED 判定，无吞错路径。
- **第二次 `read_band`（rewind 后）的逃逸形态**：若 rescan 再遇损坏，`StreamingPngError` 未包装 `OSError` 直接逃出 `_decode`，但仍是 `ValueError` → `_serve_viewport` 的 `except (OSError, ValueError)` 与 `_rebuild_tiles` 的同型守卫兜住 → 整图降级路径不变（fail-closed 保持，仅异常类型不同）。不构成缺陷。
- **AC⑨（复用测量 + 复跑锁定测试）**：`test_band_read_peak_composition`（单 IDAT / 分块 IDAT 两参数）以 tracemalloc 实测「常驻源 + 2×最大 IDAT + O(带)」，定向复跑通过；原始探针测量（`memory-and-fixture-probe.txt`：单块 24.1MB ≈ 23× 带、分块 5.7MB）未重测，**复用**。模块 docstring 的构成声明与实现一致（本复审逐行核对）。
- **AC⑩ rewind 成本**：`test_ensure_viewport_rewind_accounting_is_per_tile` 定向复跑通过；原始计时（`rewind-cost-probe.txt`）与 O(块数²) 口径**复用**（解码面收口归 TASK-046，本切片不做）。

## 四轴

| 轴 | 状态 | 小结 |
|---|---|---|
| Standards | **executed** | 只读边界保持（工作区 `src/tests` 零改动、未改已入档 Review 正文、未 push）；证据口径统一（PowerShell + `TASK-012-py312` venv、`PYTHONDONTWRITEBYTECODE=1`、`-p no:cacheprovider`、退出码与 passed/skipped 分列）；断言纪律无违例（靶点 3：5 处更新全为加强/等价替换，0 新增 skip/xfail）；本报告自身证据可复跑（3 份探针脚本随证据入库）。 |
| Spec | **executed** | 7 AC 逐条复核：F-4（独立探针 + 判别力，成立）、F-5/R-001（触发面穷举 + 测试复跑，成立）、F-8（`bookshelf/viewmodel.py` 三个 `@Slot(..., result="QVariantMap")` 在位 + 元对象断言测试在全仓复跑中通过，成立）、F-11（QML/delegate/VM 三处同一比值，成立）、F-13（`setClipRect` 在 `src/infrastructure/imaging/**` 0 命中 + docstring 为整图根因口径，独立 grep 核对，成立）、F-14（`_cache_key` 内容寻址 + `v2` 升版 + 同尺寸改写用例复跑，成立）、TASK-042 R-01～R-04（AC⑧/⑨/⑩ 与短读校验，成立）。AC⑥（超大页门）属 TASK-042 既有交付，本切片未回归其原始场景，依两份 Review 的 PASS 维持。 |
| Architecture | **executed** | 「tile = 可重建像素缓存」契约无破口：清缓存/升版/重建均不触碰业务真值；页/模式变更的重建收敛于 `_rebuild_tiles` 单点（7 入口穷举）；坐标口径（显示像素 vs 页像素）只有 `requestTiles` 一个换算点且与 QML 比值自洽；streaming reader 单向游标 + typed error 边界完整（`_pump` 无吞错；rewind 后逃逸仍被 ValueError 守卫兜住）；(0,0) 视口语义行为正确但隐式（P3-1）。分层不越界：QML 不触库，imaging 层无 Qt 依赖。 |
| Verification | **executed** | 独立复跑：3 份探针（多过滤器 F-4 / QML 遮蔽 / 行为记录）+ 判别力对照 @6ea3dd3 + 定向 45/45 + 全仓 ×3 + network 直接证据。复用：AC⑨/⑩ 原始测量、作者与原 Reviewer 的修前判别力矩阵、comment_drift_check 输出。全仓口径 848/0（交接包期望 842/6 的差 = 6 条 `tests/network` openssl 依赖用例在本 shell 转正；`network-tests-in-this-shell.log` 直接证据 97 passed；总数自洽，非 skip 消除——与既有 P-02/R-006 口径勘误同型）。真机 GUI 屏幕级像素仍未验证（作者如实声明，本复审同样未做，维持原 Report 的该未验证项）。 |

## Findings（全部 P3，不要求返工）

| # | 级别 | 观察 | 依据与影响 |
|---|---|---|---|
| P3-1 | P3 | `TileGrid.visible_tiles` 对 `(0,0)` 视口的「页头 + prefetch」正确性依赖 `(viewport_bottom − 1)` 在负数上的 floor-division 语义（`(−1)//4000 = −1` 被 `max(first, …)` 拉回 0），无显式 `bottom <= top` 分支 | 行为已被两处测试锁定（`(0,0)` 首项记录 + `[0,1]` 服务断言），无用户可见缺陷；建议后续若重构 `visible_tiles` 时显式化空视口语义，避免隐式依赖随重构丢失 |
| P3-2 | P3 | `ReaderViewModel.clearTileCache()` 清空行 URL 后 `contentY` 不变 ⇒ `onContentYChanged` 不会自发重发 `requestTiles`，视口内瓦片保持空白直到下一次滚动/翻页/模式变更 | 生产 QML 当前**无**该 slot 调用点（仅测试调用），无用户可达路径；若未来接入 QML（如「清理缓存」入口），须同时触发一次 `requestTiles` 或在 VM 内重发记忆视口 |
| P3-3 | P3 | `StreamingPngReader.read_band` 对跨页尾请求**静默钳制**（`band_height` 收窄到 EOF），typed `OUT_OF_RANGE` 仅拦完全越界——与模块整体的 fail-closed 风格不完全一致 | 生产 `_decode` 由 R-004 显式相等校验自检兜底（探针 C 段实测钳制行为并记录）；仅 API 层设计观察，无当前缺陷 |

## 独立复跑 vs 复用证据（分列声明）

**本复审独立复跑/新造**：

1. `f4_multifilter_probe.py`（A/B/C 三段）在被审树 `16f7d75`：`f4-multifilter-probe-current.log`（exit 0）
2. 同探针对修前树 `6ea3dd3` 的判别力：`f4-multifilter-probe-pre-f4-6ea3dd3.log`（exit 1，tile 高 1564/1064、拼接 4128 行）
3. `qml_shadow_probe.py`：`qml-shadow-probe.log`（legacy=0 / partial=2 / fixed=2，exit 0）
4. Repeater 源码逐版本比对（`7833604`/`6ea3dd3`/`602cca8`/`1171bc5`/`a165aa3`）与 `git diff 1171bc5..a165aa3 -- tests/` 断言审计（本报告靶点 3/5 全文）
5. 定向复跑 `tests/reading_export/{test_streaming_png,test_webtoon_tiles,test_qml_contract}.py`：45 passed / 0 skipped，exit 0（`targeted-reading-export.log`）
6. 全仓 ×3：848 passed / 0 skipped，exit 0 ×3（`full-suite-run{1,2,3}.log`；口径声明见 Verification 轴）
7. `tests/network` 直接运行：97 passed / 0 skipped（`network-tests-in-this-shell.log`，openssl 转正证据）
8. 代码级审计：`viewmodel.py` 触发面穷举、`visible_tiles(0,0)` 语义、`_pump` 包装完备性、QML 全文、`clearTileCache` 调用点普查、F-8 `result=` 与 F-13 `setClipRect` grep

**复用（未重跑，引用作者/原 Reviewer 证据）**：

1. AC⑨ 内存构成原始测量（`memory-and-fixture-probe.txt`）与 AC⑩ rewind 原始计时（`rewind-cost-probe.txt`）——锁定它们的测试已由第 5 项复跑
2. 作者修前判别力矩阵（`pre-fix-tests.txt` 10 failed、`revision-pre-fix-tests.txt`）与原 Reviewer 修订判别力（`discriminating-revision-tests-vs-1171bc5.txt` 8 failed）
3. `comment_drift_check.py` 输出（`comment-drift-check.txt`）——其守卫对象（setClipRect=0、docstring 根因、`_cache_key` 内容寻址）已由第 8 项独立 grep/读码核对
4. 原 Reviewer 修订探针输出（`review-a165aa3/reviewer-probe-on-revision.txt`）——其 B1/B3 命题已由第 5 项的 QML 用例与第 1 项探针覆盖

## 结论

**维持（uphold）**：TASK-045 的两轮 Review 结论、`e2a8f01` 集成与 `cb93d66` 收口全部维持；F-4/F-5/F-8/F-11/F-13/F-14 与 TASK-042 R-01～R-04 的关闭登记**不变**。**附带 3 项 P3 观察**（P3-1 隐式视口语义、P3-2 clearTileCache 后不自发重请求、P3-3 read_band 静默钳制），均不构成返工要求；P3-1/P3-2 可由未来触碰相应文件的切片顺手显式化，P3-3 仅登记。推翻检验：无——所有关键命题要么独立复现成功，要么判别力反例在修前树如约失败。

后续建议（不阻塞）：① P3-2 在「缓存清理」类 Task 立项时并入验收清单；② TASK-046（decode-rewind-cost）落地时可一并把 `visible_tiles` 的空视口语义显式化（P3-1）。
