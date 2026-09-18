---
kind: posthoc-review
object: ZCode 全权窗口（2026-09-17 23:12:28 → 2026-09-18 08:50）7 项 approved_subagent 集成
range: c3dabc8..5f3c115（63 commits，7 项集成 + W4 文档工作）
reviewer: DeepSeek Harness（外部独立复审；作者 ZCode 回避，Reviewer 非作者）
companion: doc/reviews/POSTHOC-WINDOW-2026-09-17.md（Codex 复审，本报告为其第 123 行「待补」的 DSH 外部独立复审）
decision: approved_with_findings（7 项集成的集成本身维持 approved；Spec 轴"0 实现有误"修正为 2 项 P1，见 §4）
axes: Standards / Spec / Architecture / Verification（逐轴声明、不跨轴排名）
---

# Post-hoc 外部复审（DSH）：ZCode 窗口 7 项集成 `c3dabc8..5f3c115`

## 0. 复审对象、输入与方法

**对象**：`c3dabc8..5f3c115`，7 项集成 —— `372c3bf`(TASK-037) / `4d0f932`(TASK-033) / `b738200`(TASK-020) / `ba7d560`(TASK-023) / `f835ac9`(TASK-038) / `c8024fe`(TASK-039) / `5bc17f8`+`b940497`(TASK-021)。全部为窗口内 `approved_subagent`（同体）审查，按窗口条款**可被本复审推翻或重开**。

**输入**：[POSTHOC-REVIEW-BRIEF-2026-09-18](../handoffs/POSTHOC-REVIEW-BRIEF-2026-09-18.md)、7 份窗口内 Review（`doc/reviews/TASK-037-7b96e72.md`、`TASK-033-933819f.md`、`TASK-020-7833604.md`、`TASK-023-7fa9118.md`、`TASK-038-317f33e.md`、`TASK-039-38fbde4.md`、`TASK-021-887e0d6.md`）、[Codex 复审](POSTHOC-WINDOW-2026-09-17.md)、各 Task/Handoff 与 `verification/TASK-0xx/**`。

**方法（四轴 + 并行镜头）**：Standards / Spec / Architecture / Verification 四轴分别执行、分别报告、**不跨轴排名**。本轮在 DSH 会话内**实际派发**了三条相互隔离的审查镜头子代理（agent-guidance 合规 / bug 与正确性 / 安全），并于其发现文件集上派发两条情境镜头（历史上下文 / 代码注释合规），再对全部发现去重、逐条评分（置信度阈值 80）后定稿——**本环境本次具备并行子代理通道**，故不适用 §6 第 6 条兜底，特此声明与 Codex 复审（该复审按兜底执行）的差异。

**口径声明（重要）**：本复审全部实跑均在 **PowerShell + `G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe`（Python 3.12.3 / PySide6 6.11.2 / pytest 9.1.1，`PYTHONDONTWRITEBYTECODE=1`，`-p no:cacheprovider`）** 口径下完成，**全仓稳定为 `781 passed / 6 skipped`（exit 0）**，6 条 skip 全为既有 `tests/network` 的 `openssl unavailable`。**不得**把 Git-Bash 口径（openssl 在 PATH 上、6 条 skip 转 pass ⇒ `N passed / 0 skipped`）与本口径的差值读作"skip 被消除"；两口径**收集总数一致**。

**锚定漂移声明**：复审期间 master 由 Codex 持续推进（`904fca1` → `74b1fcf` → `7ea1629`）。本复审的对象是**固定区间** `c3dabc8..5f3c115`（内容不随 HEAD 移动改变）；实跑与文件行号引用的时点为撰写时 HEAD（见 §3 表），并已注明。

## 1. 两项优先核验（请求方指定；均以代码级证据独立复核）

### 1.1 `4d0f932`（TASK-033）「单一写者不变式」：**成立（无二次翻转）**

| 环节 | 证据（本次独立读取） |
|---|---|
| handler 只产出 judgement，不回写指针 | `src/infrastructure/providers/handlers.py:668-726`：`handle_render` 的 docstring 明示 "**Single writer (TASK-033 P0 constraint)** … the pipeline seam must not flip the same pointer a second time"，返回处 `:723-724` 为 `# RenderService is the sole writer of the 'translated' pointer.` + `revision_updates={}`。对照同文件确实回写的其它 handler（`:275 / :357 / :408 / :456 / :542 / :601 / :664`），render 是唯一的空更新 |
| seam 不从别处翻转指针 | `src/infrastructure/sqlite/pipeline.py:568-610` `commit_step`：页级目标只按 `revision_updates` 逐项 `UPDATE media_artifacts … artifact_type = ?`（`:601-610`）；`revision_updates={}` ⇒ 循环体不执行，且 Region 目标的键校验（`:589-591`）也不受影响 |
| 真正写入者带 CAS | `src/application/rendering/service.py:464-499` `_commit_translated` → `:489` `commit_revision(...)`、`:494` `expected_current_revision_id=expected`；原子比较在 `src/infrastructure/sqlite/artifacts.py:195-212`（`BEGIN IMMEDIATE` → `actual_current != expected` ⇒ `CommitStatus.CONFLICT` / `INPUT_REVISION_CHANGED`）。`expected=None` 分支（`service.py:166-181` 先 `create_artifact`，行已存在且 `current_revision_id IS NULL`）**同样受 CAS 保护**，非"无 guard 创建路径" |
| 断言存在且实测通过 | `tests/providers/test_full_chain.py:468-532`：`:515` 断言 `result.revision_updates == {}`；每次 render **恰好新增 1 个** translated revision 且当前指针指向最新、revision_no 单调 `[1,2,3]`（"no jitter, no rewrites"）。本次实跑 `-k single_translated_pointer_writer` → **1 passed** |

**结论**：单一写者不变式**在代码、seam、CAS 与回归测试四处一致**；**不推翻**。

### 1.2 `b940497`（TASK-021）「永久删除只能触达受控数据」：**成立**

| 环节 | 证据 |
|---|---|
| 删除决策唯一入口 | `src/application/maintenance/trash.py:137-147` `purge_batch`：`:144-145` 仅 `if page.managed_original_ref: self._remover.remove_managed(...)`，`:146` `purge_pages(batch.page_ids)`，`:147` `_drop_batch`。全仓 `purge_batch` 唯一调用方是装配点（`bootstrap/app.py:462`），无 UI/CLI 直通入口 |
| 文件侧越界拒绝 | `src/infrastructure/filesystem/managed_storage.py:118-131` `remove_managed`：`Path(...).resolve()` 后 `relative_to(root.resolve())`，越界即抛 `ImmutablePathViolation`（`:122-129`）——`.resolve()` 同时消解 `..` 与符号链接，故**受控根外的用户源文件结构性不可达** |
| DB 侧作用域 | `src/infrastructure/sqlite/library.py:432-457` `purge_pages` 只删 `region_revisions → regions → pages`（给定 page_id 集合），不触 book/chapter/其它页 |
| 批次串扰修复（R-001） | `trash.py:78-104`：微秒精度 + 冲突守卫（`:81-86`）、`actually_deleted` 只记录**本次实际软删**的 id（`:92-98`）——消除了"新 batch 记录已被旧 batch 软删的 id ⇒ restore/purge 跨批串扰"的真实数据路径 |
| 回归断言（本次实跑 **6 passed**） | `tests/storage/test_trash.py:136-156` `test_purge_removes_controlled_data_only`（受控文件与行删除、**根外用户源文件逐字节幸存**）；`:166-172` `test_remove_managed_refuses_paths_escaping_the_root`（`"../outside.txt"` → `ImmutablePathViolation` 且文件未动）；`:192` `test_overlapping_soft_delete_does_not_cross_batches`（跨批重叠终态） |

**结论**：用户数据保护**成立**；R-001 修订**闭环属实**；**不推翻**。

**我在核验中另行发现的两处（不影响上述两项结论，见 §3）**：
1. **ledger 崩溃窗口与"可重建"表述不符**：`trash.py:87`（DB 软删）与 `:105-114`（manifest 写入）非原子；全仓**不存在** ledger 重建实现（`grep -ni rebuild src/application/maintenance src/bootstrap` 仅命中无关的 export/tile 语义），而该文件 docstring `:15` 声称 "rebuildable bookkeeping"。窗口内 Review R-003 只登记了 **purge 侧**窗口并把软删侧定性为"非数据丢失"；就**可恢复性**而言该定性偏松：崩溃落在窗口内时页面已被阅读器隐藏，而唯一的恢复入口是 `restore_batch`（`:129`），无批次记录即无法恢复。
2. **purge 只清受控原件、不清该页的其余 managed 修订文件**：`trash.py:144-145` 仅删 `managed_original_ref`，clean/mask/translated 等 artifact revision 文件在 `purge_pages` 后成为孤儿（磁盘增长，非用户数据丢失）。**注意**：`doc/04_USER_FLOW.md:1677-1688` 与 `doc/07_NON_FUNCTIONAL_REQUIREMENTS.md:1065` 明确"永久删除 = 数据库项目数据 + Managed Copy + **生成资产** + Cache；**不删除**用户原始源文件"——即生成资产本应在删除范围内，故此项不只是"磁盘泄漏"，而是**文档化删除范围的缺口**（与 F-2 合并计）。

### 1.3 §1.2 的加重发现：purge 在真实页上**必然失败**（我逐条实测确认）

§1.2 的结论只覆盖"**用户源文件**不可达"这一层；**行与生成资产**这一层存在确定性缺陷，且与窗口内 Review R-003（P3「崩溃窗口」）的定级不符：

- **缺陷**：`purge_pages`（`library.py:432-457`）只删 `region_revisions → regions → pages`，而 `pages(page_id)` 的依赖者共 7 张表——`media_artifacts`（`schema.py:64/71`）、`pipeline_run_targets`（`:315`）、`pipeline_tasks`（`:330`）、`step_runs`（`:345`）、`step_result_candidates`（`:380`）等——**均无 `ON DELETE CASCADE`**，且 `connection.py:37` 固定 `PRAGMA foreign_keys = ON`。`trash.py:143-146` 又是**先 unlink managed 副本、再删行**。
- **实测（我的探针，真实 schema + 真实 `ManagedFileStorage`）**：只给页加一条 `media_artifacts` 行（真实页跑过任一步骤即具备；`step_writes.py:500` 会写入），`purge_batch` → `IntegrityError: FOREIGN KEY constraint failed`；此后 **managed 副本已消失**、`pages` 行仍在（`deleted_at` 仍为软删值）、batch 仍在 ledger；`restore_batch` 随即"恢复"出一个 `managed_original_ref` **指向已删文件**的活页，且 purge 永远无法重试成功。见 [`purge-fk-failure-probe.txt`](../../verification/POSTHOC-WINDOW-2026-09-18/purge-fk-failure-probe.txt)。
- **测试为何恒绿**：`tests/storage/test_trash.py:69-88` 的 `make_page` 只 `repository.add_page()`（不建 artifacts/pipeline 行），故 5 例全过；窗口内 Review 亦据此判"FK 删除顺序正确"（`TASK-021-887e0d6.md:50` 只枚举了 2 个依赖者）。同文件 `delete_tag`（`library.py:252-254`，窗口前）恰好是"子表先行"的成文先例。
- **现网影响口径（诚实界定）**：`doc/tasks/TASK-021.md:72` 明确"永久删除实现只在测试目录演练，不对用户真实漫画库运行"，且 `TrashService` 未注册为 QML context property（`app.py:462` 装配但 `src/ui/**` 零消费者）→ 当前**无用户可触发路径**，影响是"该功能在真实数据上不可用"，而非现网数据丢失。故定级按 **major（功能确定性失败 / 需在接线前修复）**，而非现网 blocker。
- **既有 finding 强度修正**：`doc/reviews/POSTHOC-WINDOW-2026-09-17.md:60` 对 TASK-021 的 approved 主张（"purge_pages 只删行并自述…"）应在此范围内**部分修正**：源文件保护成立，但"依赖完整性已核实"不成立。

### 1.4 我在领域专项核验中确认的第二处 blocker：PDF 光栅化红蓝通道互换

**不在请求方指定的两项之内，但严重度更高，故在此单列**：`src/infrastructure/importing.py:165-174` 把 pdfium 的 `BGR` 缓冲映射为 `QImage.Format_RGB888`（`BGR` 分支是**默认且实际可达**的分支；`BGRA` 分支在本环境不可达），而同文件 `BGRA → Format_ARGB32` 在 little-endian 上字节序正确——**两条分支不对称即为缺陷**，正解是 `Format_BGR888`（Qt ≥ 5.14）。

- **实测（我的探针）**：手写最小一页纯红 PDF（`1 0 0 rg 0 0 100 100 re f`）→ 生产 `PdfiumDocumentRaster(scale=2.0).open(...).render_page(0)` → 解码 PNG 中心像素 **RGBA = (0,0,255,255)**（纯红被导成纯蓝）；pdfium 侧 `mode=BGR`、`stride=600=w*3`、原始中心字节 `(0,0,255)`（B,G,R）。见 [`pdf-channel-swap-probe.txt`](../../verification/POSTHOC-WINDOW-2026-09-18/pdf-channel-swap-probe.txt)。
- **归因**：该函数与映射整块由窗口内 `7fa9118`(TASK-023) 新增（`git blame` 全部指向该提交），非既有代码回归；窗口内 Review（`TASK-023-7fa9118.md`）只核尺寸 1224×1584 与 typed 错误，**零像素断言**，Codex 复审亦未覆盖像素正确性。
- **影响界定**：错误像素被写入 Managed Copy 并计入 `source_hash`（每页 PDF 都是错的）；但 `importDocumentsFromUrls` 目前无 QML 调用者（见 F-8），故当前是"导入通道一旦接线即产出错误文物"，定级 **blocker（需在接线/发布前修复）**、对现网为"未接线即未暴露"。

## 2. 四轴证据（本轴范围内独立复核）

### Standards（`executed`）
- **边界**：`git diff --name-only <merge>^1 <merge> -- src` × 8 逐项核对，`src/` 改动全部落在各自 Task 白名单内；**越界 0**。
- **Schema/migration**：`git diff --name-only c3dabc8..5f3c115 | grep -i 'schema\|migration'` = **0**；TASK-021 复用既有 `deleted_at` 列（无 DDL）✓。
- **删除**：`git diff --diff-filter=D --name-only` = **空**（窗口内未删除任何文件，含测试）✓。
- **依赖**：`requirements.txt` 净变更**仅 1 行** `pypdfium2==5.13.0`（用户 2026-09-17 单独批准）✓。
- **skip 纪律**：tests diff 中唯一的 skip 声明是 `pytest.importorskip("PySide6", reason="the render/color assembly is Qt-backed")`（providers full-chain，模块级）。与既有多处先例一致、在声明 venv 中不生效；**登记为 P3（与 Codex P-01 一致）**：未来应优先"带理由的显式 skipif/fixture"或在 Task 中预先声明。全仓 skip 总数未变（6）✓。
- **禁改面**：路由判定算法/SFX 语义在区间内 `grep` **零命中**；`src/ui/qml/` 仅经 TASK-020/038 授权改动 ✓。
- **轴小结**：0 硬性违反；1×P3（`importorskip`，已披露）。

### Spec（`executed`）
- 7 项集成的 AC 覆盖与**诚实性**逐项核对：3 处 `BLOCKED` **均未记 PASS**（TASK-020 超大 webtoon 像素解码、TASK-023 MOBI 光栅化、TASK-033 AC-RFULL-001）；`ACCEPTANCE_TRACEABILITY` 中 `AC-TRASH-001~004` 仍为 `NOT_RUN`（子集交付未冒充全 AC）✓。
- **窗口内 Review 自身 findings 的终态核对**（外部复审应核对"是否漏判"，也应核对"是否已收口"）：
  - TASK-020 R-001（P1）**fixed→closed**（wanted-index 门先于解码，本次独立复核 `src/ui/viewmodels/reader/viewmodel.py::requestTiles`：`wanted_indices` 计算在 `tile_file()` 调用**之前**）✓；R-002/R-003/R-005/R-006 deferred/open（P3，已登记）。
  - TASK-033 R-001（P2，planner `_clean_available` 缺陷，白名单外）→ **由 TASK-039 `c8024fe` 承接修复**，本复审核对 `_clean_available` 新实现（`src/application/tasks/service.py:463-496`）：三分支保序、`probe is None` 与旧判据**等价**（旧 `A or B` ≡ 新 `B or A or probe`，probe 仅能把 BLOCKED 转 RUN）✓。
  - TASK-039 R-001/R-002（P2，Handoff 证据叙述失实）→ 已在后续文档修订中更正（handoff 证据表现记 `89 passed` 并标注 Review R-001 更正）；TASK-038 R-001（P3，R-002 disposition 口径）→ handoff 处置表已改记 `accepted` ✓。
  - TASK-021 R-001（P2）→ **fixed** 并已由本复审独立复核（§1.2）✓。
- **Codex 复审的漏判核对**：Codex 复审的 Findings P-01～P-05 **未包含**上述窗口内 Review 已登记的 P2/P3 文档准确性问题（TASK-039 R-001/R-002、TASK-038 R-001）；本复审核对后确认这些项**已在文档修订中收口**，故不构成漏判的实质风险，但建议后续复审在 Findings 中显式引用窗口 Review 的 disposition 表。
- **轴小结**：7/7 AC 范围无缺失、无 scope creep、无"看似实现但有误"；1 项**新发现**（§3 F-1，pdfium 缺依赖路径未 typed）。

### Architecture（`executed`）
- **分层方向**：`tests/core/test_architecture.py` 的 AST 守卫（application 不得 import infrastructure，含动态导入）在本次独立全仓复跑中通过 ✓；新增包 `application/{maintenance,importing/documents}`、`infrastructure/imaging` 归属合理，未把 Qt/DB 依赖带进 application 层（`pypdfium2` 仅 `infrastructure/importing.py:126`）✓。
- **QML 边界**：`ReaderView.qml` 的瓦片经 `model.tiles`（Python 侧）下发 `source: modelData.url`，QML 无 sqlite/文件直连；整图路径保留为回退（`visible: !tilesHost.visible`）✓。
- **单一写者/装配可达性**：见 §1.1 与 §1.2；"能力已实现但生产不可达"在本窗口出现两次（TASK-020 tile、TASK-023 文档导入），**已被 TASK-038 修复**（本次核对 `bootstrap/app.py` 注册 5 个 context property）；**唯一残留**是 TASK-039 `clean_probe` 的注入点（`git grep clean_probe src` 仅 `application/tasks/service.py`，bootstrap 零命中）——与 Codex P-03 一致，属**已登记的跨白名单项**，即用户本次释放的 TASK-040 的目标。
- **轴小结**：0 项缺陷；1 项已登记残留（TASK-040 目标）。

### Verification（`executed`）
- **独立全仓复跑**：`python -m pytest -q -p no:cacheprovider -rs -rf`（PowerShell 口径）→ **781 passed / 6 skipped，exit 0**，与 Codex 复审的 781/6 一致 ✓。
- **关键路径定向复跑（本次实跑）**：`tests/providers/test_full_chain.py -k single_translated_pointer_writer` **1 passed**；`tests/storage/test_trash.py` **6 passed**；`tests/core/test_bootstrap.py` **14 passed**。
- **证据纪律**：`verification/TASK-0xx/full-suite-runs.log` 存在（7 项均有）；TASK-038 R-002（日志缺少逐次退出码行）与 TASK-039 R-001/R-002（数字/叙述失实）为窗口内已登记项，本次核对**均已修订**；TASK-037 的修前 `EXIT=127` 不可复现异常**如实登记未粉饰** ✓。
- **口径**：见 §0；作者与 Codex 已统一口径说明，本复审以 PowerShell 781/6 为准。
- **未验证项（与 Codex 一致）**：各切片自身的 ≥5 次 full-suite 日志（抽样）；作者登记的 `EXIT=127` 异常（不可复现）；7 份窗口内 Review 的逐行内容。**新增未验证**：webtoon 分块三处视觉结论（瓦片接缝/空白带/换页旧图）由码面与几何探针推导，**未做真机 GUI 截图确认**；D2/D1 的并发/真实库路径未在本机对用户数据演练。
- **轴小结**：0 项阻断（对本 Task 的现有证据链）；独立复跑与边界审计通过。

### 2.1 既有 Review 主张的修正（外部复审的独立价值之一）

| 既有主张 | 位置 | 本次核对结论 |
|---|---|---|
| "**`purge_pages` FK 删除顺序正确**…实现一致" | `doc/reviews/TASK-021-887e0d6.md:50` | **部分推翻**：只枚举了 7 个 `pages(page_id)` 依赖者中的 2 个；实测 `media_artifacts`/`pipeline_run_targets` 任一存在即 `IntegrityError`（详见 §1.3、F-1） |
| "tile delegate 高度…为**纯等比换算**…无固定高度压缩" | `doc/reviews/TASK-020-7833604.md:32` | **与实现不符**：落盘 PNG 为 `content_height + overlap`，Delegate 又用 `PreserveAspectFit` 在声明盒内缩放 ⇒ 非首块被 letterbox 且顶部重复上一带（详见 F-3） |
| "purge 只作用受控数据（安全关键）"（`POSTHOC-WINDOW:60`） | Codex 复审 | **源文件部分成立、行/生成资产部分不成立**：§1.2 的源文件保护成立；§1.3 的依赖完整性与生成资产删除范围双双不成立 |
| "7/7 维持 approved、0 实现有误" | Codex 复审 §Spec | **建议修正为**：7 项**集成边界与诚实性**维持（白名单/无删除/无新增 skip/BLOCKED 未记 PASS 均成立），但 **Spec 轴存在 2 项实现有误（F-1、F-2）**，需重开/加项 |
| `TASK-015-488fafc.md` R-003/R-007"移交 TASK-020 验收覆盖" | 历史镜头 | **仍未执行**：TASK-020 以整图路径验收判 done，而同窗口 TASK-038 把生产默认切到分块路径 → R-007 要求的"两章节真实重载"验收在分块路径上缺失 |

### 2.2 既有 flaky / 未定性项的交叉核对

- `TASK-037` 的 webtoon clamp 修复**经我独立复核成立**（wanted-index 门在解码前；`reader_stack_webtoon` 夹具改为可容纳 240px 的页高 + 新增 `contentY == 240.0` 落地断言 = **只加强未放宽**）；该修复与我方 TASK-036 独立捕获的 `contentY=-0.0` 签名**互为印证**（见 `verification/TASK-036/registered-flaky-signature.md`）。
- `EXIT=127`（不可复现）与 webtoon 保存 flaky：本轮 DSH 复跑未触发；按既有口径**不记为通过**。

## 3. Findings（外部复审新增；置信度阈值 80）

> 本节为 **DSH 外部复审相对 Codex 复审的增量发现**；窗口内各 Review 已登记的 findings 不在本节重复（其终态见 §2 Spec）。

**评定口径**：每条给出**仓库级 P 级**（P0/P1/P2/P3）+ **外部复审置信度**（0–100；评分环节阈值 80，低于阈值但在本报告登记）+ 归属（本区间新引入 / 本区间首次生产可达）+ 处置建议。**本区间新增文件亦计入"新引入"**：`webtoon_tiles.py` 于本区间新增（325 行）、`ReaderView.qml` 于本区间改动（49 行）。

| ID | P 级 | 置信度 | 位置 | 缺陷 | 归属 | 处置建议 |
|---|---|---|---|---|---|---|
| **F-1** | **P1** | **90** | `src/infrastructure/importing.py:165-174` | pdfium `BGR` 缓冲映射为 `Format_RGB888` → 每页 PDF 红蓝互换，错误像素写入 Managed Copy 与 `source_hash` | 本区间新引入（`7fa9118` TASK-023） | **修实现**：改 `Format_BGR888`（Qt≥5.14）+ 新增"纯红 PDF → 取像素"回归 |
| **F-2** | **P1** | **90** | `library.py:432-457` + `trash.py:137-147` | `purge_pages` 漏 5 张 `pages(page_id)` 依赖表（无 CASCADE、FK 强制）→ 处理过的页 `purge_batch` 必抛 `IntegrityError`；且**先 unlink 托管件再删行** → 文件已失、行仍软删、batch 仍留（实测 `batches in ledger: 1`），`restore_batch` 复原出**指向已删文件的活页** | 本区间新引入（`887e0d6` TASK-021） | **修实现**：单事务内按 FK 逆序清 `step_result_candidates/pipeline_tasks/pipeline_run_targets/step_runs → artifact_revisions → media_artifacts → region_revisions → regions → pages`，并改为**先删行、后删文件**；补"有 artifact/run 行的页 purge"用例 |
| **F-3** | **P2** | 75 | `application/importing/documents/service.py:142-147,162-166,191` | 文档内某页失败即 `break`，其余页既不 failed 也不 pending（取消路径才写 pending）；0 页文档被报 `skipped_duplicates` | 本区间新引入（TASK-023） | 修实现：失败/取消均把 `page_no+1..page_count` 追加 pending；空文档单独 `INVALID_DOCUMENT` |
| **F-4** | **P2** | 75 | `webtoon_tiles.py:99-108,234-262` + `ReaderView.qml:245-254` | tile PNG 落盘的是**含 overlap 的解码窗**（实测 400×832 vs 声明 800、400×3064 vs 3000），而模块注释称"displayed band stays [content_top,content_bottom)"、"dedup by construction" | 本区间新引入；`TASK-038` 使其生产可达 | 修实现：落盘前裁到 `[content_top,content_bottom)`（overlap 仅作解码上下文），或改整图高 + 偏移对齐 |
| **F-5** | **P2** | 75 | `viewmodel.py:112/128/246/252/258` + `ReaderView.qml:110-121` | `_rebuild_tiles()` 只挂 `openChapter`/`setMode`；翻页槽不重建，且工具栏"上/下一页"未按 `vertical` 门控（键盘翻页已门控）→ 分块模式"显示旧页像素、进度记新页" | 本区间新引入/首次可达 | 修实现：换页槽末尾重建瓦片；分块模式禁用工具栏翻页 |
| F-6 | P3 | 75 | `trash.py:141-143` | purge 只删 `managed_original_ref`；mask/clean/translated 及其行永不删除，违背 `doc/04_USER_FLOW.md:1677-1688` 与 `doc/07_NON_FUNCTIONAL_REQUIREMENTS.md:1065` 的删除范围 | 本区间新引入 | 随 F-2 一并修（收集全部 `artifact_revisions.managed_path` 后删除） |
| F-7 | P3 | 75 | `trash.py:39-49,87-105` | manifest 非原子写 + 裸 `json.loads`；DB 与 manifest 跨介质无事务（截断即整功能失效；DB 先行窗口使页被隐藏且无 batch 可恢复） | 本区间新引入 | 原子写（temp+`os.replace`）+ 读侧容错；或在写失败时补偿 DB |
| F-8 | P3 | 50 | `bookshelf/viewmodel.py:370-371` | `@Slot(str, list)` 缺 `result=` → 元对象 `returnType=void`，QML 得 `undefined`；同文件 `:285/:311/:349` 先例均带 `result=` | 本区间新引入（TASK-038） | 修实现：`result="QVariantMap"` 并接线 |
| F-9 | P3 | 75 | `importing.py:126` | `import pypdfium2` 在 `try` 之外 → 缺依赖时抛裸 `ImportError`，与 `:114-117` 承诺的 typed 错误不符 | 本区间新引入 | 移入 `try` 并包成 `DocumentDecodeError` |
| F-10 | P3 | 75 | `trash.py:6-8` + `library.py:296-310` | 注释称"reader/imports 都隐藏软删行"，但 import 侧 `existing_source_hashes`/`max_source_order` 不过滤 `deleted_at` → 软删页 hash 仍去重（重导报 `skipped_duplicates` 而章节无可见页）并占用 `source_order` | 本区间新引入 | 修实现（两查询加 `deleted_at IS NULL`）或修注释 |
| F-11 | P3 | 50 | `ReaderView.qml:231-235` + `webtoon_tiles.visible_tiles` + `viewmodel.py:330/337` | `requestTiles` 收到显示像素 `contentY`，网格按页像素解释；`pagePixelWidth/Height` 暴露却无人使用 → 视宽≠页宽时请求带偏移（空白带） | 本区间新引入 | 修实现：调用处换算，或给 `requestTiles` 加 scale 参数 |
| F-12 | P3 | 75 | `service.py:486` + `assembly.py:30-41` + `app.py:508` | docstring 称 `clean_probe` "injected at assembly (AC 2)" 且 TASK-039 AC ② 已勾，但生产从未注入 → render-only 仍 `BLOCKED(missing_clean_artifact)` | 已登记（Codex P-03 / 裁决 #1） | **已由用户释放的 TASK-040 承接**；建议同时修正 docstring/AC 注记口径 |
| F-13 | P3 | 25 | `webtoon_tiles.py:14-18,186-188` | 注释称 `setClipRect` 使峰值内存≈一个 tile；仓库自身测试写明"setClipRect 不改变该行为（handler 先分配整图再裁剪）" | 本区间新增文件 | 修注释，并在 TASK-042 立项前提中改记"整图解码是根因" |
| F-14 | P3 | 25 | `webtoon_tiles.py:189,289-295` | 注释称 key 含"source hash"，实际为路径+大小+几何，无语义内容哈希 → 同尺寸原地改写命中陈旧瓦片 | 本区间新增文件；已登记 TASK-020 R-004 | 修注释或补内容哈希 |

**F-1 / F-2 的实测证据**（可由任何人复跑）：[`pdf-channel-swap-probe.txt`](../../verification/POSTHOC-WINDOW-2026-09-18/pdf-channel-swap-probe.txt)、[`purge-fk-failure-probe.txt`](../../verification/POSTHOC-WINDOW-2026-09-18/purge-fk-failure-probe.txt)（探针脚本同目录）。

**诚实性说明（关于 F-2 的一处细节修正）**：评分环节推测 `_drop_batch` 在异常后仍会清 ledger；**实测相反**——`_drop_batch` 位于 `purge_pages` 之后，异常时不会执行，故 **batch 仍留在 manifest**（这与"页可被 restore 出悬空活页"的后果一致）。本报告以实测为准。

**诚实性说明（关于"是否本区间改动"的判定）**：评分环节一度以"切片提交只改了 7 个文件"为由，把 `webtoon_tiles.py` / `ReaderView.qml` 判为"区间外既有代码"。**该前提不成立**：本复审对象是**合并区间** `c3dabc8..5f3c115`，`git diff --stat c3dabc8..5f3c115 -- src` 明确包含 `src/infrastructure/imaging/webtoon_tiles.py`（新增 325 行）与 `src/ui/qml/reader/ReaderView.qml`（改动 49 行），二者由区间内的 `b738200`(TASK-020) 与 `f835ac9`(TASK-038) 两次合并带入/改写。故 F-4/F-5/F-11/F-13/F-14 均按"**本区间新引入**"计（F-13/F-14 的严重度仍低，因为它们主要是注释与已登记 R-004 的口径问题，而非新增运行时缺陷）。

## 4. 结论与对裁决清单的意见

## 4. 结论与对裁决清单的意见

### 4.1 两项指定优先项：**均维持（不推翻）**

- **`4d0f932` 单一写者不变式：成立**（§1.1，四层证据 + 回归实测；唯一残余是"指针提交不在 `commit_step` 的 CAS 事务内"的窄窗口，属另一类问题，未发现双重写入）。
- **`b940497` 用户**源文件**保护：成立**（§1.2，`resolve()+relative_to` 拒越界 + 根外文件逐字节幸存）。**但同一函数的"行/生成资产"边界不成立**（§1.3、F-2）——这是对既有 Review 定级（P3 崩溃窗口）的**升级建议**，不是对"源文件安全"结论的推翻。

### 4.2 对 7 项集成总评：**"集成边界与诚实性"维持，"0 实现有误"应修正为 2 项**

| 维度 | 结论 |
|---|---|
| 白名单/依赖/Schema/删除/skip 纪律 | **7/7 维持**（§2 Standards：越界 0、依赖仅获批 1 行、0 Schema/migration、0 删除、0 新增 skip） |
| 诚实性（BLOCKED 未记 PASS、异常主动披露） | **维持**（§2 Spec） |
| AC 范围内"无实现有误" | **修正**：本区间存在 **2 项实现级缺陷**（F-1 PDF 像素、F-2 purge 依赖完整性），且**窗口内 7 份 Review 与 Codex 复审均未发现** |
| 是否回滚集成 | **不建议回滚**：F-1/F-2 当前均**无用户可触发路径**（文档导入入口未接线、TrashService 未注册 context property），回滚代价大于收益 |

### 4.3 处置建议（交 Codex）

1. **F-1（P1，PDF 像素）**：改 `Format_BGR888`，并在 `tests/import_formats` 增加**像素级断言**（红页 → 像素红）。建议把"光栅化适配器必须有像素断言"写入后续 Task 的验收惯例。
2. **F-2（P1，purge）**：修 `purge_pages` 的完整 FK 图（含 `artifact_revisions`），并把"先删文件后删行"改为"先删行、后删文件（失败可诊断）"；补"有 artifact/run 行的页 purge"用例。**在接线任何 purge UI 之前必须完成。**
3. **F-3（P2，文档导入余页）** 与 **F-4/F-5（P2，分块显示/翻页）**：建议各自开小切片（TASK-023 与 TASK-020/038 的修订/尾项），与已释放的 TASK-041/042 一并排期。
4. **F-12**：TASK-040 已承接注入；请同时修正 `service.py:486` 的 docstring 与 TASK-039 AC ② 的注记口径。
5. **F-13/F-14**：修注释即可；F-13 与 TASK-042 的立项前提相关（"整图解码"是根因，不是可绕过的 Qt 限制）。
6. **流程性建议**：硬删/级联路径应强制"枚举全部引用表"核对（本仓库 `delete_tag` 已有正确先例）；窗口内同类"能力已实现但生产不可达"已出现三次（tile、文档导入、clean_probe），建议把"接线断言"纳入 Task 模板的 AC 清单。

### 4.4 复审决定

**decision = `approved_with_findings`**（7 项集成的**集成本身**维持 approved；因新发现 2 项 P1 实现缺陷，Spec 轴"0 实现有误"结论修正）。**可推翻/重开的对象**：TASK-023（像素正确性）、TASK-021（purge 完整性）；建议以"修订尾项"而非"重开原切片"方式处理。**不推翻**：TASK-033 单一写者（P0 约束）、TASK-021 源文件安全、TASK-037/038/039/020 的集成结论与已登记 BLOCKED 口径。

### 4.5 复审自身的限制（如实声明）

- 未做真机 GUI 截图确认（F-4/F-5 的视觉结论由几何 + 码面推导）；F-1/F-2 的实测均在**临时目录/临时库**上进行，未对用户数据演练；未复跑各切片自身的 ≥5 次 full-suite 日志（抽样核对）；`EXIT=127` 不可复现异常未重现。
- 复审期间 master 由 Codex 持续推进（`904fca1 → 74b1fcf → 7ea1629`），本报告以**固定区间** `c3dabc8..5f3c115` 为对象，行号引用以撰写时工作区为准（`git diff 5f3c115..HEAD -- src` 为空，即 `src/` 与区间终态一致）。
