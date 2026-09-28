# Handoff — M2-AC4 Reader Export Lineage + Library Page-count/Unknown Semantics Acceptance

- Owner: ZCode（子 agent 代行实现，用户授权 2026-09-28）
- Task: `doc/tasks/M2-AC4.md`（`ready → in_review / M2_AC4_READER_LINEAGE_LIBRARY_PAGECOUNT_RELEASED`；纯验收，产品代码零改动）
- Base / release: `a5529181` / `252705bf`
- Branch / worktree: `agent/zcode/M2-AC4-reader-lineage-library-pagecount` / `G:/CODEX/New Manga.worktrees/M2-AC4-zcode`
- Head ledger: claim=`5f9f54ab` → 实现（测试+证据）=`130dd7db` → evidence/handoff=本文件所在 commit（交付 tip；`git rev-parse HEAD` 即是，commit message 注明同一 hash；`delivery_head` frontmatter 按 Task 约定保持 null，由 Integrator 在 merge 后回填）
- Status: delivered（等 DeepSeek Harness 非作者 Review；Integrator=另一会话代行 Codex，保持 Owner≠Integrator）

## 交付物

| 文件 | 说明 |
|---|---|
| `tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py` | 新增验收模块，**11 场景**覆盖 AC1–AC5（AC1×2、AC2×3、AC3×2、AC4×3、AC5×1）；production 装配 + 真实 SQLite/文件系统，零 mock 数据层 |
| `verification/M2-AC4/verification-results.md` | 主证据：两级命令日志摘要、场景→AC 判定表、AC 判定、缺陷清单（F-1/F-2）、范围自检、NOT_RUN 单列 |
| `verification/M2-AC4/discrimination-mutations.md` | 红判别力记录（MU1/MU2 均红 + 还原零残留），含 Reviewer 可独立复放的精确命令 |
| `verification/M2-AC4/raw/probe_export_semantics.py` + `raw/probe-output.log` | 写测试前的语义探针（production 通道一次性复演），其输出固化了 F-1/F-2 的直接证据 |
| `verification/M2-AC4/raw/final-new-suite.log` / `final-regression.log` | 新套件 `-v`（9 passed, 2 xfailed, EXIT=0）与回归 `tests/m2_acceptance -q`（32 passed, 2 xfailed, EXIT=0），头部含 shell/解释器/固定 HEAD/时间戳 |
| `verification/M2-AC4/raw/mutation-MU1-run.log` / `mutation-MU2-run.log` | 变异运行原始输出（红判别） |
| `verification/M2-AC4/raw/git-diff-check-owner-tip.log` | `git diff --check` 卫生追踪（两次实测 EXIT=2 与修复轨迹、工作树预演 EXIT=0；最终 tip 复跑按协议归 Integrator） |
| `doc/tasks/M2-AC4.md` | AC 判定回填、测试矩阵 executed、`status: in_review` / `dispatch_state: DELIVERED_FOR_REVIEW` |

## AC 判定表（全部实测，细节见 verification-results.md）

| AC | 判定 | 要点 |
|---|---|---|
| AC1 导出 lineage 与输出对账 | **FAIL（部分）→ F-1** | (b) zip 条目名/字节=页 scope、text payload=页文本（Region 同源）、file_hash=输出 SHA-256 全 PASS；(c) export_id 唯一、history 最近优先 PASS；(a) history() 字段覆盖 `included_stale_page_ids` **实测缺失**（`_record`/`_scope_snapshot` 不含该字段） |
| AC2 stale 防线 fail-closed | **PASS**（附 F-1 引用） | (a) 默认 ABORT 抛 `StaleExportError`（stale/missing ids 如实、可区分），零输出文件、零 temp、**零 history 记录**；(b) CONTINUE 成功：输出=旧译文字节（非 current），missing 页 fallback 原图字节，`ExportResult.included_stale/missing_page_ids` 如实；history 持久留痕缺口即 F-1 |
| AC3 失败/取消 durability | **PASS**（2 场景） | 中途 provider 失败 / 页间取消：既有目标文件字节逐位原样、源与 Managed 文件指纹（size/mtime_ns/sha256）不变、零 temp 残留、history 记 failed/cancelled 且 detail 非空（含 "OSError" 类型名/取消文案） |
| AC4 Library page-count/unknown | **FAIL（部分）→ F-2** | (a) 有页书 page_count == 章页合计 == production 谓词 SQLite COUNT == Reader 侧（reader_catalog 长度 + `ReadingService.page_count`）全一致；(c) 受控破坏页行后不崩溃、计数如实、其他字段不伪造；(b) 无章/无页书呈现 `page_count=0`（int，无 unknown 通道）= Task 预期验收张力，记 FAIL |
| AC5 源文件零风险 + 证据纪律 | **PASS** | 混合轮（成功/ABORT/CONTINUE/失败/取消）后用户源文件+Managed Copy+译文 revision 指纹全部不变；32 passed 回归 EXIT=0；命令日志带头带 EXIT；`git diff --check` 轨迹见 raw（最终 tip 复跑归 Integrator） |

## 验证命令（worktree 根目录，$py=TASK-012-py312，均带 `PYTHONIOENCODING=utf-8`）

1. `$py -m pytest tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py -v` → **9 passed, 2 xfailed**，EXIT=0
2. `$py -m pytest tests/m2_acceptance -q` → **32 passed, 2 xfailed**（既有 23 全绿 + 新增 9 passed + 2 xfailed，零回归），EXIT=0
3. `git diff --check a5529181..<delivery-tip>` → Owner 阶段：f615d5da/130dd7db 两次 EXIT=2（pytest 日志尾随空白，修复轨迹见 `raw/git-diff-check-owner-tip.log`），工作树预演 EXIT=0；**最终 tip 由 Integrator 复跑为准**

环境：Windows x64 · Git Bash · Python 3.12.3 · pytest 9.1.1；0 skipped；两个 xfailed 均为 `strict=True` 的缺陷证据（修复落地会 XPASS 报错提醒移除标记）。

## 装配说明（Owner 的 production 通道选择，如实记录）

1. **装配函数**：`bootstrap.core_assembly.assemble_core_services`——production sidecar（`bootstrap/core_service.py::assemble_production_core`）调用的同一装配函数（M2-AC2/AC3 先例）。headless adapter（decoder/style analyzer）经 I1-AC4 required-adapter injection 注入：sidecar 自带的 `_PassthroughImageDecoder` 向 `DecodedImage` 传不存在的 `format=` 参数（M2-AC2 已记录的缺陷），本套件与先例一致地注入自己的 headless decoder，语义路径与 production 相同。`mock_local_providers` 未使用（本 Task 不跑 pipeline）。
2. **ExportService production 可达性**：`assemble_core_services` 内部组装 `export_service = ExportService(SqliteExportHistoryStore(conn))`（`core_assembly.py:853`），历史落 SQLite `export_history` 表——**无需任何桥接**，直接 `core.export_service` 使用（Task 风险条目「若 production 装配未组装 ExportService」不成立，装配说明如实记录为已组装）。
3. **ListBooks production 入口**：直接调用 production RPC 命令处理函数 `CoreServiceServer(core).handle_list_books({})`（`core_service.py:145`，即 production `ListBooks` 命令的同一处理函数，MU2 变异点所在）；未起 stdio sidecar 进程（传输层归 M2-IPC1，进程级往返 NOT_RUN 单列）。
4. **stale 页构造（与 Reader 同口径）**：TRANSLATED 修订经 production 写路径 `SqliteArtifactRepository.commit_revision`（RenderService/pipeline 同一仓库）落两个 revision（R1→R2）；reader 快照在 R1 为 current 时经 `core.reader_catalog.list_pages` 取得（= 打开中的 Reader/Workbench 持有的页视图），新渲染 R2 落地后，`ExportPage` 的 `translated_revision_id` 用快照值 R1、`current_translated_revision_id` 经同一 `SqlitePageArtifactLocator` 实时解析为 R2——与 `ReaderPage.translated_stale` 同一判定（D06 §97）。
5. **页文本**：经 production `SqliteRegionRepository.add_region` 写入、`list_regions(...).text.final_translation` 读回（Reader/Workbench 文本同源），填入 `ExportPage.text`（reader catalog 的 text 字段按设计为空，translated-export 文本是独立 seam——`core_assembly.py` `_ManagedReaderCatalog` docstring）。

## 实现过程中的语义发现（供 Reviewer 重点核对）

1. **F-1（AC1(a) FAIL）**：export history 行（SQLite `export_history`，经 `SqliteExportHistoryStore`）**不含** `included_stale_page_ids`/`included_missing_page_ids`；`scope_snapshot_json` 仅记录 `stale_policy` 字符串。CONTINUE 放行了哪些 stale 页在持久 lineage 中不可追溯（内存 `ExportResult` 字段正确——`export()` 返回值如实）。探针 + xfail 场景双重证据。修复建议方向：`_record` 落行时并入 `result.included_stale_page_ids/included_missing_page_ids`（scope_snapshot 或独立列，属 schema/契约变更，留给修复 Task）。
2. **F-2（AC4(b) FAIL，Task 预期张力）**：`core_service.py:160` `page_counts.get(book.book_id, 0)`——无章书与有章无页书都呈现 `page_count=0`（int），`BookSummaryDto` 无 unknown 标志，违反「缺失数据不得伪造成看似真实的数字」。探针输出原句：`Probe Empty Book page_count: 0`。修复建议方向：DTO 增加 `page_count_known`/可选 null 语义（IPC 契约变更，留给修复 Task）。
3. **ABORT 是真·零痕迹**：`StaleExportError` 在 `created_at`/`_record` 之前抛出（`service.py:216-220`），被拒绝的导出连 failed 记录都不留——本套件将其断言为承诺语义（「零 completed 记录」实测为零*任何*记录）。Reviewer 若认为被拒导出也应留痕，属 D03 §31 语义澄清，超出本 Task。
4. **history 排序精度**：`utc_now()` 毫秒精度（`domain/books/entities.py:15`），同一毫秒内的两次导出顺序依赖 SQLite `ORDER BY created_at DESC` 的稳定行为；AC1 顺序断言以 20ms 间隔保证可分。真实 UI 间隔远大于此，未列为缺陷。
5. **取消时机**：`cancel` poll 点=导出开始、archive 每条目前、写盘终检前（`service.py:224/255/397`）；套件用「条目 1 写入后、条目 2 前」的真实中途取消。
6. **Task 锚点核对**：`service.py:216/152/81-95/127/159-170/248-301`、`core_service.py:115/150/160/167`、`reading/service.py:199`（`page_count = len(self.pages)`）与实际语义全部相符，无需 AC 措辞修订。

## NOT_RUN / BLOCKED

- **React/WebView2 UI 呈现面**（Library 页数徽标、导出对话框 stale 提示）：NOT_RUN——headless 不可达（M2-AC2/AC3 先例同因）；Core 层持久状态断言为准。
- **sidecar 进程级 IPC 往返**：NOT_RUN——本 Task 承诺为 Core 层语义，传输层由 M2-IPC1 覆盖；ListBooks 语义经 production handler 直调。
- **PDF/CBZ/single_image 格式**：不在 AC1「≥2 格式」承诺内（已覆盖 zip+text），不列缺陷。
- FAIL/BLOCKED 产品缺陷：无 BLOCKED；FAIL 证据 = F-1、F-2（见上，均以 xfail(strict) 场景 + 探针固化）。

## 风险 / 遗留

- 两个 xfail 标记需随修复 Task 关闭：F-1/F-2 修复落地后 XPASS 会使套件红，由确认修复的 Review 移除标记。
- 开发期失败日志（run1/MU1/MU2）做过 whitespace-only 清理以满足 `git diff --check`（轨迹见 `raw/git-diff-check-owner-tip.log`），内容逐字保留；Reviewer 可按 mutation 文档独立复放全部红点。
- 既有三个验收套件零触碰（回归 32 passed 实证）；`src/**`/`apps/**`/`doc/contracts/**` 零改动（`git status --porcelain src/` 全程为空）。

## 启动 / 复现方式

```bash
cd "G:/CODEX/New Manga.worktrees/M2-AC4-zcode"
git checkout agent/zcode/M2-AC4-reader-lineage-library-pagecount   # tip = delivery head
export PYTHONIOENCODING=utf-8
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance/test_reader_export_lineage_library_pagecount.py -v
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" -m pytest tests/m2_acceptance -q
# 探针（可选）：
"G:/CODEX/New Manga.task-envs/TASK-012-py312/Scripts/python.exe" verification/M2-AC4/raw/probe_export_semantics.py
```

## 下一接收者

DeepSeek Harness（非作者 Review）。Review 输入：本 Handoff、`doc/tasks/M2-AC4.md` AC 表、`verification/M2-AC4/**`、Owner 分支 tip。重点核对：F-1/F-2 判定与 xfail 证据是否成立、AC2(b) 的 PASS-with-F-1-reference 归属、stale 快照构造语义（装配说明 §4）。Review 通过后由 Integrator（另一会话代行 Codex）集成：复跑验证命令（含对最终 tip 的 `git diff --check a5529181..<tip>`）、核对 allowed paths（`tests/m2_acceptance/` 新增文件、`doc/tasks/M2-AC4.md`、`verification/M2-AC4/**`、`doc/handoffs/M2-AC4-*.md`；禁改 `src/**`、`apps/**`、`doc/contracts/**`、既有验收套件行为）、merge、回填 `delivery_head`/`integration_merge` 并置 done；F-1/F-2 转后续修复 Task（需 Codex 定义契约/schema 变更范围）。
